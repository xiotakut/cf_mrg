"""Run MedGENIE with the existing receipts, v5 inputs and native scoring interface."""
import argparse
import fcntl
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')
from common import ROOT, atomic, file_hash, read, visible
from medgenie import UPSTREAM, medgenie
from run import METHODS, audit, run_item


def resolve(config_path, inputs, run_dir, workers):
    run_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(config_path.read_text())
    files = [ROOT / 'code' / name for name in ('run_medgenie.py', 'medgenie.py', 'medgenie_backend.py', 'run.py', 'runtime.py', 'common.py')]
    files += list((UPSTREAM / 'context_generation/prompt').glob('pmc-llama*.txt'))
    files += [UPSTREAM / 'icl_reader/templates/templates_llama3/Meta-Llama-3-8B-Instruct/medqa/medqa4opt.txt']
    config.update(run_id=run_dir.name, input_path=str(inputs.resolve()),
                  inputs_hash=file_hash(inputs), workers=workers,
                  physical_gpu_selection=os.environ.get('CUDA_VISIBLE_DEVICES'),
                  code_hashes={str(p.relative_to(ROOT)): file_hash(p) for p in files})
    resolved = run_dir / 'resolved_config.json'
    if resolved.exists():
        assert json.loads(resolved.read_text()) == config, 'Configuration changed; use a new run directory.'
    else:
        atomic(resolved, config)
        for path in files:
            target = run_dir / 'code_snapshot' / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/medgenie.json')
    parser.add_argument('--workers', type=int, default=12)
    args = parser.parse_args()
    items = read(args.inputs)
    assert items and len(items) == len({i['item_id'] for i in items})
    for item in items:
        assert set(item) <= {'item_id', 'question', 'options', 'fixed_evidence', 'answer_format', 'max_tokens'}
        visible(item)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    with (args.run_dir / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = resolve(args.config, args.inputs, args.run_dir, args.workers)
        pending = [i for i in items if not (args.run_dir / 'items' / i['item_id'] / 'result.json').exists()]
        if not pending:
            print(json.dumps(audit(args.run_dir, items)))
            return
        from medgenie_backend import VLLMBackend
        started = time.time()
        backend = VLLMBackend(config)
        atomic(args.run_dir / 'actual_backend.json', backend.identity)
        inference_started = time.time()
        METHODS['medgenie'] = medgenie
        try:
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                jobs = [pool.submit(run_item, item, args.run_dir, config, backend, None) for item in pending]
                for job in as_completed(jobs):
                    result = job.result()
                    print(json.dumps(dict(item_id=result['item_id'], **audit(args.run_dir, items))), flush=True)
            atomic(args.run_dir / 'complete.json', dict(**audit(args.run_dir, items),
                   seconds=time.time() - inference_started, total_seconds=time.time() - started))
        finally:
            backend.close()


if __name__ == '__main__':
    main()
