"""Same-weight HF generation with full-vocabulary, post-processor entropy."""
import json
import os
import threading
import time
from pathlib import Path


def entropy_from_scores(scores):
    import torch
    p = torch.softmax(scores.float(), dim=-1)
    return -(p * torch.log(p + 1e-10)).sum(dim=-1)


class HFBackend:
    def __init__(self, config):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.config = config
        if config.get('allocator'):
            assert os.environ.get('PYTORCH_CUDA_ALLOC_CONF') == config['allocator']
        self.lock = threading.Lock()
        self.tokenizer = AutoTokenizer.from_pretrained(config['model_path'], local_files_only=True)
        self.tokenizer.padding_side = 'left'
        self.tokenizer.pad_token = self.tokenizer.eos_token
        kwargs = dict(torch_dtype=torch.bfloat16, local_files_only=True, attn_implementation='sdpa')
        device_map = config.get('device_map', 'auto')
        if config.get('max_memory'):
            kwargs['max_memory'] = {int(k) if k.isdigit() else k: v for k, v in config['max_memory'].items()}
        if config.get('rope_scaling'):
            kwargs['rope_scaling'] = config['rope_scaling']
        self.model = AutoModelForCausalLM.from_pretrained(config['model_path'], device_map=device_map, **kwargs).eval()
        self.identity = dict(model_id=config['model_id'], model_path=config['model_path'],
                             weight_id=config['weight_id'], tokenizer_id=config['tokenizer_id'],
                             dtype='bfloat16', score_dtype='float32', engine='transformers',
                             version=__import__('transformers').__version__,
                             allocator_config=os.environ.get('PYTORCH_CUDA_ALLOC_CONF'),
                             device_map={k: str(v) for k, v in getattr(self.model, 'hf_device_map', {}).items()})

    def prompts(self, messages):
        return [self.tokenizer.apply_chat_template(m, tokenize=False, add_generation_prompt=True,
                                                  **self.config['chat_template_kwargs']) for m in messages]

    def generate(self, messages, max_tokens, seed, entropy=False, reference=False, sampling_groups=None):
        """One deterministic cached batch. Per-row outputs count as LLM requests."""
        import torch
        from transformers import LogitsProcessor
        prompts = self.prompts(messages)
        inputs = self.tokenizer(prompts, padding=True, add_special_tokens=False, return_token_type_ids=False, return_tensors='pt')
        lengths = inputs.attention_mask.sum(1).tolist()
        if max(lengths) + max_tokens > self.config['max_length']:
            raise ValueError(f'context_overflow: {max(lengths)} + {max_tokens} > {self.config["max_length"]}')
        entropies = []
        groups = sampling_groups or [(len(messages), seed)]
        assert sum(n for n, _ in groups) == len(messages)

        class Capture(LogitsProcessor):
            def __call__(self, input_ids, scores):
                entropies.append(entropy_from_scores(scores).detach().cpu().tolist())
                return scores

        with self.lock, torch.inference_mode():
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            inputs = inputs.to(self.model.get_input_embeddings().weight.device)
            width = inputs.input_ids.shape[1]
            original = self.model._get_logits_processor

            def processors(*args, **kwargs):
                # Append AFTER HF's sampling warpers, unlike logits_processor=.
                result = original(*args, **kwargs)
                if entropy:
                    result.append(Capture())
                return result

            self.model._get_logits_processor = processors
            original_sample = torch.multinomial
            generators = {}

            def sample(probabilities, num_samples, replacement=False, *, generator=None, out=None):
                # Each original request keeps its own RNG stream when requests
                # share a tensor batch. Its QA rows retain their original shape.
                if probabilities.ndim != 2 or probabilities.shape[0] != len(messages) or generator is not None or out is not None:
                    return original_sample(probabilities, num_samples, replacement, generator=generator, out=out)
                draws, offset = [], 0
                for j, (count, group_seed) in enumerate(groups):
                    key = j, str(probabilities.device)
                    if key not in generators:
                        generators[key] = torch.Generator(device=probabilities.device).manual_seed(group_seed)
                    draws.append(original_sample(probabilities[offset:offset + count], num_samples, replacement, generator=generators[key]))
                    offset += count
                return torch.cat(draws, dim=0)

            torch.multinomial = sample
            started = time.monotonic()
            try:
                outputs = self.model.generate(**inputs, max_new_tokens=max_tokens,
                    do_sample=self.config['temperature'] > 0,
                    temperature=self.config['temperature'] if self.config['temperature'] > 0 else None,
                    top_p=self.config['top_p'], top_k=self.config['top_k'],
                    repetition_penalty=1.0, num_beams=1, use_cache=True,
                    eos_token_id=self.model.generation_config.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                    return_dict_in_generate=True, output_scores=reference)
            finally:
                self.model._get_logits_processor = original
                torch.multinomial = original_sample
            elapsed = time.monotonic() - started
            sequences = outputs.sequences[:, width:].tolist()
            reference_entropies = [entropy_from_scores(s).cpu().tolist() for s in outputs.scores] if reference else None
        eos = self.model.generation_config.eos_token_id
        eos = set(eos if isinstance(eos, list) else [eos])
        results = []
        for i, ids in enumerate(sequences):
            end = next((j + 1 for j, x in enumerate(ids) if x in eos), len(ids))
            ids = ids[:end]
            useful = [j for j, x in enumerate(ids) if x not in self.tokenizer.all_special_ids]
            result = dict(text=self.tokenizer.decode(ids, skip_special_tokens=True),
                          prompt=prompts[i], prompt_token_ids=inputs.input_ids[i][inputs.attention_mask[i].bool()].tolist(),
                          token_ids=ids, useful_positions=useful,
                          tokens=[self.tokenizer.decode([ids[j]]) for j in useful],
                          entropies=[entropies[j][i] for j in useful] if entropy else None,
                          prompt_tokens=lengths[i], completion_tokens=len(ids),
                          finish_reason='stop' if ids and ids[-1] in eos else 'length',
                          batch_seconds=elapsed, batch_size=len(messages), model=self.identity,
                          score_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32',
                          scoring_forward_calls=0)
            if reference:
                result['reference_entropies'] = [reference_entropies[j][i] for j in useful]
            results.append(result)
        return results


class BatchingBackend:
    """Batch independent synchronous stage requests; histories stay per item."""
    def __init__(self, engine, max_batch_tokens=32000):
        import copy
        import queue
        self.engine, self.queue = engine, queue.Queue()
        self.max_batch_tokens = max_batch_tokens
        self.identity = engine.identity
        separate_tokenizer = copy.deepcopy(engine.tokenizer)
        tokenizer_lock = threading.Lock()

        class LockedTokenizer:
            def encode(self, *args, **kwargs):
                with tokenizer_lock:
                    return separate_tokenizer.encode(*args, **kwargs)

            def decode(self, *args, **kwargs):
                with tokenizer_lock:
                    return separate_tokenizer.decode(*args, **kwargs)

        self.tokenizer = LockedTokenizer()
        threading.Thread(target=self._worker, daemon=True).start()

    def generate(self, messages, max_tokens, seed, entropy=False):
        from concurrent.futures import Future
        # Independent per-sequence RNG permits splitting a large three-query QA
        # request without dropping documents or changing its output order.
        futures = []
        for index, message in enumerate(messages):
            future = Future()
            self.queue.put(dict(messages=[message], max_tokens=max_tokens,
                                seed=(seed + index) % (2 ** 31), entropy=entropy, future=future))
            futures.append(future)
        return [future.result()[0] for future in futures]

    def _worker(self):
        import queue
        import uuid
        pending = []
        while True:
            first = pending.pop(0) if pending else self.queue.get()
            batch = [first]
            time.sleep(.05)
            while True:
                try:
                    pending.append(self.queue.get_nowait())
                except queue.Empty:
                    break
            count = len(first['messages'])
            prompt_max = max(len(self.engine.tokenizer.encode(p, add_special_tokens=False)) for p in self.engine.prompts(first['messages']))
            for request in pending[:]:
                if (request['max_tokens'], request['entropy']) != (first['max_tokens'], first['entropy']):
                    continue
                n = len(request['messages'])
                length = max(len(self.engine.tokenizer.encode(p, add_special_tokens=False)) for p in self.engine.prompts(request['messages']))
                if (max(length, prompt_max) + first['max_tokens']) * (count + n) > self.max_batch_tokens:
                    continue
                count += n
                prompt_max = max(prompt_max, length)
                batch.append(request)
                pending.remove(request)
            try:
                results = self.engine.generate([m for r in batch for m in r['messages']], first['max_tokens'], first['seed'],
                    entropy=first['entropy'], sampling_groups=[(len(r['messages']), r['seed']) for r in batch])
                offset, batch_id = 0, uuid.uuid4().hex
                for r in batch:
                    size = len(r['messages'])
                    outputs = results[offset:offset + size]
                    for output in outputs:
                        output.update(engine_batch_id=batch_id, engine_batch_size=count,
                                      engine_batch_seconds=output['batch_seconds'])
                        # Allocate shared backend time once across original calls.
                        output['batch_seconds'] *= size / count
                        output['batch_size'] = size
                    r['future'].set_result(outputs)
                    offset += size
            except Exception as e:
                for r in batch:
                    r['future'].set_exception(e)


class Retriever:
    def __init__(self, config):
        import sys
        from common import MEDRAG
        sys.path.insert(0, str(MEDRAG))
        from src.baselines import make_retriever
        self.config, self.lock = config, threading.Lock()
        self.engine = make_retriever(config, Path(config['corpus_path']), Path(config['reranker_path']))

    def retrieve(self, query):
        with self.lock:
            docs, scores = self.engine.retrieve(query, k=self.config['k'], rrf_k=self.config['rrf_k'])
        return dict(documents=docs, scores=scores)
