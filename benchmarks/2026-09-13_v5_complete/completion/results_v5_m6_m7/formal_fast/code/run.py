"""Registered imedrag/tcrag runner over the existing native items interface."""
import argparse
import fcntl
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from pathlib import Path
from common import ROOT, atomic, digest, file_hash, read, visible
from methods import METHODS
from runtime import Session, RequestFailure


def resolve(config_path, inputs, run_dir):
    config = json.loads(Path(config_path).read_text())
    config['code_hashes'] = {p.name: file_hash(p) for p in sorted((ROOT / 'code').glob('*.py')) if p.name in ('run.py', 'methods.py', 'runtime.py', 'backend.py', 'common.py')}
    config['inputs_hash'] = file_hash(inputs)
    config['physical_gpu_selection'] = os.environ.get('CUDA_VISIBLE_DEVICES')
    config['input_path'] = str(Path(inputs).resolve())
    config['run_id'] = Path(run_dir).name
    path = Path(run_dir) / 'resolved_config.json'
    if path.exists():
        if json.loads(path.read_text()) != config:
            raise ValueError('run_configuration_changed: use a new run directory')
    else:
        atomic(path, config)
    return config


def run_item(item, root, config, backend, retriever):
    path = root / 'items' / item['item_id']
    terminal = path / 'result.json'
    if terminal.exists():
        result = json.loads(terminal.read_text())
        if result['input_hash'] != digest(visible(item)) or result['config_hash'] != digest(config):
            raise ValueError('terminal_identity_mismatch')
        return result
    session = Session(path, config, backend, retriever)
    started = time.time()
    try:
        result = METHODS[config['method']](item, session)
    except RequestFailure as e:
        result = dict(status='failed', termination='request_failed', error=str(e), raw_response='')
    except ValueError as e:
        result = dict(status='failed', termination='protocol_failed', error=str(e), raw_response='')
    result.update(item_id=item['item_id'], inference_input_id=item['item_id'], method=config['method'],
                  run_id=config['run_id'], input_hash=digest(visible(item)), config_hash=digest(config), seed=config['seed'],
                  seconds=time.time() - started, costs=session.costs(), trace_path=str(path / 'events'),
                  requests_path=str(path / 'requests'), reused_stage_requests=session.reused)
    atomic(terminal, result)
    return result


def audit(root, planned):
    ids = {i['item_id'] for i in planned}
    results = [json.loads(p.read_text()) for p in sorted((root / 'items').glob('*/result.json'))]
    assert not {r['item_id'] for r in results} - ids
    assert len(results) == len({r['item_id'] for r in results})
    counts = Counter(r['status'] for r in results)
    status = dict(N_planned=len(ids), N_ok=counts['ok'], N_invalid=counts['invalid'],
                  N_failed=counts['failed'], N_pending=len(ids) - len(results),
                  unknown_ids=0, duplicates=0)
    assert status['N_planned'] == sum(status[k] for k in ('N_ok', 'N_invalid', 'N_failed', 'N_pending'))
    atomic(root / 'predictions.jsonl', results, lines=True)
    atomic(root / 'progress.json', status)
    return status


def main():
    p = argparse.ArgumentParser()
    p.add_argument('method', choices=METHODS)
    p.add_argument('--config', type=Path)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--audit-only', action='store_true')
    p.add_argument('--verify-backend', action='store_true')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--max-batch-tokens', type=int)
    args = p.parse_args()
    args.run_dir.mkdir(parents=True, exist_ok=True)
    items = read(args.inputs)
    assert len(items) == len({i['item_id'] for i in items})
    # The entry point rejects accidentally passing the offline gold/mapping file.
    for item in items:
        assert set(item) <= {'item_id', 'max_tokens', 'question', 'options', 'fixed_evidence', 'answer_format'}
        visible(item)
    if args.audit_only:
        print(json.dumps(audit(args.run_dir, items)))
        return
    config = resolve(args.config or ROOT / 'configs' / (args.method + '.json'), args.inputs, args.run_dir)
    assert config['method'] == args.method
    batch_tokens = args.max_batch_tokens or config.get('max_batch_tokens', 32000)
    with (args.run_dir / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        batching_path = args.run_dir / 'batching.json'
        if batching_path.exists():
            previous = json.loads(batching_path.read_text())
            if previous['workers'] != args.workers or previous['max_batch_tokens'] != batch_tokens:
                raise ValueError('run_workers_changed: use the frozen execution settings or a new run directory')
        pending = [i for i in items if not (args.run_dir / 'items' / i['item_id'] / 'result.json').exists()]
        if not pending:
            print(json.dumps(audit(args.run_dir, items)))
            return
        from backend import HFBackend, Retriever, BatchingBackend
        backend = HFBackend(config)
        if args.verify_backend and not (args.run_dir / 'backend_reference.json').exists():
            probe = [[dict(role='user', content='Write a short sentence about organizing research notes.')]]
            reference = backend.generate(probe, 32, 1729, entropy=True, reference=True)[0]
            ordinary = backend.generate(probe, 32, 1729, entropy=False)[0]
            errors = [abs(a - b) for a, b in zip(reference['entropies'], reference['reference_entropies'])]
            assert reference['token_ids'] == ordinary['token_ids']
            assert reference['prompt_token_ids'] == ordinary['prompt_token_ids']
            assert errors and max(errors) <= 1e-5
            atomic(args.run_dir / 'backend_reference.json', dict(status='passed', max_abs_error=max(errors),
                   generation_tokens_identical=True, reference=reference, ordinary=ordinary,
                   threshold_decision_identical=(sum(reference['entropies']) < config['sigma']) == (sum(reference['reference_entropies']) < config['sigma']),
                   overhead_llm_requests=2, overhead_scoring_forward_calls=0,
                   note='Same model/engine/dtype; collector observes post-processor full scores without modifying generation.'))
        retriever = Retriever(config['retrieval'])
        atomic(args.run_dir / 'actual_backend.json', backend.identity)
        backend = BatchingBackend(backend, batch_tokens)
        atomic(args.run_dir / 'batching.json', dict(workers=args.workers, max_batch_tokens=batch_tokens,
               rng='Independent RNG per sequence (stage seed + row index); oversized QA groups split without dropping inputs.'))
        started = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {pool.submit(run_item, item, args.run_dir, config, backend, retriever): item for item in pending}
            for job in as_completed(jobs):
                result = job.result()
                status = audit(args.run_dir, items)
                print(json.dumps(dict(item_id=result['item_id'], termination=result['termination'],
                                      elapsed=time.time() - started, **status)), flush=True)
        atomic(args.run_dir / 'complete.json', dict(**status, seconds=time.time() - started))


if __name__ == '__main__':
    main()
