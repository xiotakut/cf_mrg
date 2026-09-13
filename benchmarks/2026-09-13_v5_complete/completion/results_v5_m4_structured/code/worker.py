"""Persistent vLLM per GPU; disjoint formal chunks with atomic batch outputs."""
import fcntl
import json
import os
import sys
import time
from prepare_v5 import OUT, read, write, dump


def claim(gpu):
    with (OUT / 'queue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        jobs = [json.loads(p.read_text()) for p in sorted((OUT / 'jobs').glob('*.json'))]
        owned = [j for j in jobs if j['state'] == 'running' and j['gpu'] == gpu]
        assert len(owned) <= 1
        queued = [j for j in jobs if j['state'] == 'queued']
        job = next(iter(owned or queued), None)
        if job:
            job.update(state='running', gpu=gpu, worker_pid=os.getpid())
            job.setdefault('started_at', time.time())
            dump(OUT / 'jobs' / (job['name'] + '.json'), job)
        return job


def main(gpu):
    assert gpu in ('1', '2', '3') and os.environ['CUDA_VISIBLE_DEVICES'] == gpu
    with (OUT / f'gpu{gpu}.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        job = claim(gpu)
        if job is None:
            return
        config = json.loads((OUT / 'config.json').read_text())
        sys.path.insert(0, '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')
        from vllm import LLM, SamplingParams
        from vllm.sampling_params import GuidedDecodingParams
        try:
            model = LLM(model=config['base']['model_path'], dtype='bfloat16',
                        max_model_len=config['max_model_len'], seed=config['seed'],
                        **{k: config[k] for k in ('gpu_memory_utilization', 'max_num_seqs',
                           'max_num_batched_tokens', 'enable_prefix_caching',
                           'enable_chunked_prefill', 'guided_decoding_backend')})
            tok = model.get_tokenizer()
            dump(OUT / 'logs' / f'gpu{gpu}_ready.json', dict(time=time.time(), pid=os.getpid(), config=config))
            while job is not None:
                name = job['name']
                folder = OUT / 'runs' / name
                folder.mkdir(exist_ok=True)
                inputs = read(OUT / 'inputs' / (name + '.jsonl'))
                results = read(folder / 'predictions.jsonl')
                done = {r['item_id'] for r in results}
                assert len(done) == len(results) and done <= {r['item']['item_id'] for r in inputs}
                pending = [r for r in inputs if r['item']['item_id'] not in done]
                pending.sort(key=lambda r: len(r['messages'][-1]['content']))
                if pending:
                    prompts = [tok.apply_chat_template(r['messages'], tokenize=False,
                               add_generation_prompt=True) for r in pending]
                    lengths = [len(tok.encode(p, add_special_tokens=False)) for p in prompts]
                    assert max(lengths) + 2048 <= config['max_model_len']
                    params = [SamplingParams(temperature=.7, top_p=1., top_k=-1,
                              max_tokens=2048, seed=42, guided_decoding=GuidedDecodingParams(
                              json=r['schema'], backend='xgrammar')) for r in pending]
                    started = time.time()
                    outputs = model.generate(prompts, params, use_tqdm=False)
                    elapsed = time.time() - started
                    for r, output in zip(pending, outputs):
                        answer = output.outputs[0]
                        results.append(dict(item_id=r['item']['item_id'], method='medrag_llama31',
                            method_id='M4', implementation='structured_fix_20260913',
                            raw_response=answer.text, prompt_tokens=len(output.prompt_token_ids),
                            completion_tokens=len(answer.token_ids), finish_reason=answer.finish_reason,
                            sampling=dict(temperature=.7, top_p=1., top_k=-1, max_tokens=2048, seed=42),
                            batch_wall_seconds=elapsed, batch_size=len(pending), time=time.time(),
                            context_truncated_tokens=r['context_truncated_tokens']))
                    write(folder / 'predictions.jsonl', results)
                assert len(results) == job['n'] and len({r['item_id'] for r in results}) == job['n']
                job.update(state='done', finished_at=time.time(), predictions=len(results))
                dump(OUT / 'jobs' / (name + '.json'), job)
                print(json.dumps(job), flush=True)
                job = claim(gpu)
        except Exception as e:
            if job is not None:
                job.update(state='error', error=f'{type(e).__name__}: {e}', error_at=time.time())
                dump(OUT / 'jobs' / (job['name'] + '.json'), job)
            raise
    import finish
    finish.main()


if __name__ == '__main__':
    main(sys.argv[1])
