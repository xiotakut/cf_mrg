"""Persistent validated M7 engines; reuse the M4 locked chunk queue pattern."""
import fcntl
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')
from common import ROOT, atomic, read
from run import resolve, run_item, audit


def claim(gpu):
    with (ROOT / 'queue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        jobs = [json.loads(p.read_text()) for p in sorted((ROOT / 'jobs').glob('*.json'))]
        owned = [j for j in jobs if j['state'] == 'running' and j['gpu'] == gpu]
        assert len(owned) <= 1
        job = next(iter(owned or [j for j in jobs if j['state'] == 'queued']), None)
        if job:
            job.update(state='running', gpu=gpu, worker_pid=os.getpid())
            job.setdefault('started_at', time.time())
            atomic(ROOT / 'jobs' / (job['name'] + '.json'), job)
        return job


def main(gpu):
    assert gpu in ('0', '1', '3') and os.environ['CUDA_VISIBLE_DEVICES'] == gpu
    with (ROOT / f'gpu{gpu}.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        job = claim(gpu)
        if job is None:
            return
        started = time.time()
        try:
            from vllm_backend import VLLMBackend
            from backend import Retriever
            config = json.loads((ROOT / 'configs/tcrag_vllm.json').read_text())
            backend = VLLMBackend(config)
            retriever = Retriever(config['retrieval'])
            atomic(ROOT / 'logs' / f'gpu{gpu}_ready.json', dict(time=time.time(), started=started, pid=os.getpid(), backend=backend.identity))
            while job is not None:
                root = ROOT / 'runs' / job['name']
                inputs = ROOT / 'inputs' / (job['name'] + '.jsonl')
                cfg = resolve(ROOT / 'configs/tcrag_vllm.json', inputs, root)
                atomic(root / 'actual_backend.json', backend.identity)
                atomic(root / 'batching.json', dict(workers=64, max_batch_tokens=32000, actual_max_num_batched_tokens=16384, persistent_engine=True))
                items = read(inputs)
                tick = time.time()
                with ThreadPoolExecutor(max_workers=64) as pool:
                    futures = [pool.submit(run_item, item, root, cfg, backend, retriever) for item in items]
                    for future in as_completed(futures):
                        result = future.result()
                        status = audit(root, items)
                        print(json.dumps(dict(chunk=job['name'], item_id=result['item_id'], termination=result['termination'], **status)), flush=True)
                atomic(root / 'complete.json', dict(**status, seconds=time.time()-tick))
                job.update(state='done', finished_at=time.time(), predictions=len(items))
                atomic(ROOT / 'jobs' / (job['name'] + '.json'), job)
                job = claim(gpu)
            backend.close()
            atomic(ROOT / 'logs' / f'gpu{gpu}_complete.json', dict(time=time.time(), seconds=time.time()-started))
        except Exception as e:
            if job is not None:
                job.update(state='error', error=f'{type(e).__name__}: {e}', error_at=time.time())
                atomic(ROOT / 'jobs' / (job['name'] + '.json'), job)
            raise


if __name__ == '__main__':
    main(sys.argv[1])
