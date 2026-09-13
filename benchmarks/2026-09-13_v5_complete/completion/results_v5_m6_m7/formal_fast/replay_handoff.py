"""Copy committed receipts and replay completed inputs without model inference."""
import json
import os
import shutil
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'formal'
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, read
from run import audit, resolve, run_item
from transformers import AutoTokenizer


class CacheOnly:
    def __init__(self, model_path):
        self.tokenizer = self
        self.inner = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.lock = threading.Lock()

    def encode(self, *args, **kwargs):
        with self.lock:
            return self.inner.encode(*args, **kwargs)

    def decode(self, *args, **kwargs):
        with self.lock:
            return self.inner.decode(*args, **kwargs)

    def generate(self, *args, **kwargs):
        raise AssertionError('Handoff replay must not generate model responses')

    def retrieve(self, *args, **kwargs):
        raise AssertionError('Handoff replay must not issue retrieval')


def main():
    summaries, backends = [], {}
    for old_run in sorted((SOURCE / 'runs').iterdir()):
        job = json.loads((SOURCE / 'jobs' / (old_run.name + '.json')).read_text())
        run = ROOT / 'runs' / old_run.name
        assert not run.exists()
        records = [json.loads(p.read_text()) for p in old_run.glob('items/*/result.json')]
        copied, keys, interrupted = [], set(), []
        for path in old_run.glob('items/*/requests/*.json'):
            target = run / path.relative_to(old_run)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            item_id, key = path.parts[-3], path.stem
            copied.append(dict(item_id=item_id, request_key=key, source_path=str(path)))
            keys.add((item_id, key))
        for path in old_run.glob('items/*/attempts/*/*.json'):
            attempt = json.loads(path.read_text())
            if attempt['status'] != 'ok':
                interrupted.append(dict(path=str(path), status=attempt['status'], started=attempt['started']))
                continue
            target = run / path.relative_to(old_run)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            item_id, key = path.parts[-4], path.parts[-2]
            if (item_id, key) not in keys:
                copied.append(dict(item_id=item_id, request_key=key, source_path=str(path)))
                keys.add((item_id, key))
        atomic(run / 'cache_provenance.json', dict(source_run=str(old_run), copied_requests=copied,
               selection='Every committed request and terminal input, without correctness filtering.',
               change='Execution batching only; canonical request config and stage seeds unchanged.',
               fresh_compute='Only requests without committed responses and subsequently new stages.',
               uncommitted_attempts_retained_at_source=interrupted))
        os.environ['CUDA_VISIBLE_DEVICES'] = job['gpu']
        config = resolve(ROOT / 'configs' / f"{job['method']}_single_gpu.json", job['input_path'], run)
        if job['method'] not in backends:
            backends[job['method']] = CacheOnly(config['model_path'])
        backend = backends[job['method']]
        inputs = {r['item_id']: r for r in read(job['input_path'])}
        for old in records:
            new = run_item(inputs[old['item_id']], run, config, backend, backend)
            assert all(new.get(key) == old.get(key) for key in
                       ('raw_response', 'status', 'termination', 'issues', 'answer_error',
                        'steps', 'rounds', 'executed_queries', 'backtracks', 'summaries'))
        coverage = audit(run, list(inputs.values()))
        # Retain ownership so the newly frozen execution settings recover on the
        # same physical GPU. Source queues remain an untouched historical scope.
        next_job = json.loads((ROOT / 'jobs' / (old_run.name + '.json')).read_text())
        next_job.update(state='running', gpu=job['gpu'], source_run=str(old_run))
        atomic(ROOT / 'jobs' / (old_run.name + '.json'), next_job)
        summaries.append(dict(run=old_run.name, completed_replayed=len(records),
                              copied_requests=len(copied), unresolved_attempts=len(interrupted), coverage=coverage))
    atomic(ROOT / 'handoff_validation.json', dict(status='passed',
           completed_predictions_identical=True, new_model_or_retrieval_calls=0, runs=summaries))
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
