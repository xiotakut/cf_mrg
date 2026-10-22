"""Continuous single-GPU generation; exact configured full-vocabulary entropy."""
import queue
import threading
import time
from concurrent.futures import Future


class EntropyCapture:
    def __init__(self, temperature):
        self.temperature = temperature
        self.values = []
        self.positions = []

    def __call__(self, past_tokens, logits):
        from backend import entropy_from_scores
        # V0 invokes this before its sampler's temperature division. Our pinned
        # configs have no penalties, top-k/p truncation, masks or min-tokens.
        # Observe the same post-temperature distribution without modifying it.
        self.values.append(entropy_from_scores(logits.float() / self.temperature).detach())
        self.positions.append(len(past_tokens))
        return logits


class VLLMBackend:
    def __init__(self, config):
        self.config = config
        self.queue = queue.Queue()
        self.ready = Future()
        self.failure = None
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        self.ready.result()

    def generate(self, messages, max_tokens, seed, entropy=False, batch_group=None, sampling=None):
        if self.failure:
            raise RuntimeError('vLLM engine failed') from self.failure
        futures = []
        for index, message in enumerate(messages):
            future = Future()
            self.queue.put((message, max_tokens, (seed + index) % (2**31), entropy, sampling or {}, future))
            futures.append(future)
        return [future.result() for future in futures]

    def close(self):
        self.queue.put(None)
        self.thread.join()

    def _worker(self):
        active = {}
        engine = None
        restore_sampler = None
        try:
            import copy
            import vllm
            from vllm import EngineArgs, LLMEngine, SamplingParams
            from vllm.sampling_params import RequestOutputKind
            c = self.config
            assert c['temperature'] > 0 and c['top_p'] == 1.0 and c['top_k'] == 0
            if c['method'] == 'tcrag':
                from vllm.model_executor.layers.sampler import Sampler
                restore_sampler = Sampler.forward

                def fp32_sampler(sampler, logits, sampling_metadata):
                    # V0 otherwise builds its temperature tensor in logits'
                    # BF16 dtype (.7 becomes .69921875). The pinned HF entropy
                    # convention applies temperature to FP32 scores.
                    return restore_sampler(sampler, logits.float(), sampling_metadata)

                Sampler.forward = fp32_sampler
            engine = LLMEngine.from_engine_args(EngineArgs(
                model=c['model_path'], dtype='bfloat16', max_model_len=c['max_length'],
                gpu_memory_utilization=c['gpu_memory_utilization'],
                max_num_seqs=c['max_num_seqs'], max_num_batched_tokens=16384,
                enable_prefix_caching=True, enable_chunked_prefill=True, seed=c['seed'],
                rope_scaling=c.get('rope_scaling')))
            tokenizer = engine.get_tokenizer_group().tokenizer
            # Context assembly runs in input threads, separate from engine tokenization.
            separate = copy.deepcopy(tokenizer)
            lock = threading.Lock()

            class Tokenizer:
                def encode(self, *args, **kwargs):
                    with lock:
                        return separate.encode(*args, **kwargs)

                def decode(self, *args, **kwargs):
                    with lock:
                        return separate.decode(*args, **kwargs)

            self.tokenizer = Tokenizer()
            self.identity = {k:c[k] for k in ('model_id','model_path','weight_id','tokenizer_id')}
            self.identity.update(dtype='bfloat16', engine='vllm', version=vllm.__version__,
                score_dtype='float32', entropy_supported=True, engine_generation='V0',
                sampling_temperature_dtype='float32' if c['method']=='tcrag' else 'vllm_default',
                cost_convention='scheduler step wall time divided among submitted unfinished requests')
            self.ready.set_result(None)
            counter = 0
            while True:
                incoming = [self.queue.get()] if not active else []
                while True:
                    try:
                        incoming.append(self.queue.get_nowait())
                    except queue.Empty:
                        break
                for request in incoming:
                    if request is None:
                        assert not active
                        return
                    message, limit, seed, entropy, sampling, future = request
                    try:
                        prompt = tokenizer.apply_chat_template(message, tokenize=False,
                            add_generation_prompt=True, **c['chat_template_kwargs'])
                        ids = tokenizer.encode(prompt, add_special_tokens=False)
                        if len(ids) + limit > c['max_length']:
                            raise ValueError(f'context_overflow: {len(ids)} + {limit}')
                        rid = f'request_{counter}'
                        counter += 1
                        capture = EntropyCapture(c['temperature']) if entropy else None
                        params = SamplingParams(temperature=sampling.get('temperature', c['temperature']),
                            frequency_penalty=sampling.get('frequency_penalty', 0.0), top_p=c['top_p'],
                            top_k=-1 if c['top_k']==0 else c['top_k'], max_tokens=limit,
                            seed=seed, output_kind=RequestOutputKind.FINAL_ONLY,
                            logits_processors=[capture] if capture else None)
                        engine.add_request(rid, {'prompt_token_ids':ids}, params)
                        active[rid] = dict(future=future, prompt=prompt, ids=ids,
                            started=time.monotonic(), charged_seconds=0., capture=capture)
                    except Exception as error:
                        future.set_exception(error)
                if not active:
                    continue
                started = time.monotonic()
                outputs = engine.step()
                elapsed = time.monotonic() - started
                for state in active.values():
                    state['charged_seconds'] += elapsed / len(active)
                for output in outputs:
                    if not output.finished:
                        continue
                    state = active[output.request_id]
                    answer = output.outputs[0]
                    ids = list(answer.token_ids)
                    useful = [i for i,t in enumerate(ids) if t not in tokenizer.all_special_ids]
                    entropies = None
                    if state['capture'] is not None:
                        import torch
                        values = state['capture'].values
                        positions = state['capture'].positions
                        assert positions == list(range(len(values))), positions
                        # V0 async output processing can sample one step ahead
                        # before observing EOS/length completion. Only emitted
                        # token positions belong to the method's entropy span.
                        assert len(ids) <= len(values) <= len(ids)+1, (len(values),len(ids))
                        values = torch.stack(values[:len(ids)]).cpu().tolist()
                        entropies = [values[i] for i in useful]
                    state['future'].set_result(dict(text=answer.text, prompt=state['prompt'],
                        prompt_token_ids=state['ids'], token_ids=ids, useful_positions=useful,
                        tokens=[tokenizer.decode([ids[i]]) for i in useful], entropies=entropies,
                        prompt_tokens=len(state['ids']), completion_tokens=len(ids),
                        finish_reason=answer.finish_reason, model=self.identity,
                        batch_seconds=state['charged_seconds'], batch_size=1,
                        request_wall_seconds=time.monotonic()-state['started'],
                        score_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32' if entropies is not None else None,
                        scoring_forward_calls=0))
                    del active[output.request_id]
        except BaseException as error:
            self.failure = error
            if not self.ready.done():
                self.ready.set_exception(error)
            for state in active.values():
                state['future'].set_exception(error)
            while not self.queue.empty():
                request = self.queue.get_nowait()
                if request:
                    request[-1].set_exception(error)
        finally:
            if engine is not None and hasattr(engine, 'engine_core'):
                engine.engine_core.shutdown()
            if restore_sampler is not None:
                Sampler.forward = restore_sampler
