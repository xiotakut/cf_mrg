"""Sequential full-panel aggregation with durable requests and no duplicate retries."""
import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from datetime import datetime
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import time
import traceback
import zlib

ROOT = Path(__file__).parent
WORK = Path('/home/data3/txy')
DEP = Path('/home/data4/txy/codex_runs/2026-10-23/cf_moa_publication_gpu/environment/dependencies')
sys.path.insert(0, str(WORK))
from cf_moa.contracts import InputPacket, Budget, digest
from cf_moa.controller.post_selective import request, resolve
from cf_moa.agents.post_proposers import validate_pool


def now():
    return datetime.now().astimezone().isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)


def write_record(path, record):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', compresslevel=3, mtime=0) as zipped:
            zipped.write(json.dumps(record, ensure_ascii=False, separators=(',', ':')).encode())
        stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)
    return sha(path)


def read_record(path):
    with gzip.open(path, 'rt') as stream:
        return json.load(stream)


def packet(sample):
    value = deepcopy(sample['packet']); value['budget'] = Budget(**value['budget'])
    return InputPacket(**value)


def sample_rows(method):
    db = sqlite3.connect((ROOT / 'samples.sqlite3').as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        for rid, ordinal, payload in db.execute('SELECT rid,ordinal,payload FROM samples WHERE method=? ORDER BY ordinal', (method,)):
            yield rid, ordinal, json.loads(zlib.decompress(payload))
    finally:
        db.close()


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS tasks (rid TEXT, mode TEXT, request_hash TEXT, pool_hash TEXT, status TEXT, origin TEXT, artifact TEXT, artifact_sha TEXT, usage TEXT, submitted_at TEXT, completed_at TEXT, PRIMARY KEY(rid,mode))')

    def complete(self, rid, mode, request_hash, pool_hash, artifact):
        row = self.db.execute('SELECT status,request_hash,pool_hash,artifact,artifact_sha FROM tasks WHERE rid=? AND mode=?', (rid, mode)).fetchone()
        if row is not None:
            assert (row[1], row[2]) == (request_hash, pool_hash), 'Changed pending/completed request'
            if row[0] == 'complete':
                assert Path(row[3]).exists() and sha(Path(row[3])) == row[4]
                return True
        if artifact.exists():
            value = read_record(artifact)
            assert value['status'] == 'complete' and value['request_hash'] == request_hash and value['pool_hash'] == pool_hash
            assert value['request_id'] == rid and value['mode'] == mode
            self.commit(value, artifact, sha(artifact))
            return True
        if row is not None:
            raise RuntimeError('Unresolved submitted request; refusing automatic replay: ' + rid + ':' + mode)
        return False

    def begin(self, rid, mode, request_hash, pool_hash):
        self.db.execute('INSERT INTO tasks (rid,mode,request_hash,pool_hash,status,origin,submitted_at) VALUES (?,?,?,?,?,?,?)',
            (rid, mode, request_hash, pool_hash, 'submitted', 'new', now()))
        self.db.commit()

    def commit(self, record, path, file_sha):
        self.db.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(rid,mode) DO UPDATE SET status=excluded.status,origin=excluded.origin,artifact=excluded.artifact,artifact_sha=excluded.artifact_sha,usage=excluded.usage,completed_at=excluded.completed_at',
            (record['request_id'], record['mode'], record['request_hash'], record['pool_hash'], 'complete', record['origin'], str(path), file_sha,
             json.dumps(record['usage']), record.get('submitted_at'), now()))
        self.db.commit()

    def progress(self):
        counters = Counter(); usage = Counter()
        for status, origin, payload in self.db.execute('SELECT status,origin,usage FROM tasks'):
            counters[status] += 1; counters[origin] += status == 'complete'
            if payload and origin == 'new':
                for key, value in json.loads(payload).items():
                    if key in ('input_tokens', 'output_tokens', 'elapsed_seconds'):
                        usage[key] += value
        return dict(counts=counters, new_usage=usage)

    def close(self):
        self.db.execute('PRAGMA wal_checkpoint(TRUNCATE)'); self.db.close()


def backend_for(method, *, preflight=False):
    sys.path.insert(0, str(DEP))
    from cf_moa.tools import vllm_backend
    vllm_backend.EXTRA_SITE = str(DEP)
    from cf_moa.tools.native_backend import NativeBackend, profile
    adopted = profile(method, 'readout'); config = deepcopy(adopted.config)
    cfg = dict(context=131072, gpu_memory_utilization=0.40 if method == 'M4' else 0.45)
    if not preflight:
        cfg = json.loads((ROOT / 'runtime.json').read_text())['methods'][method]
    config.update(gpu_memory_utilization=cfg['gpu_memory_utilization'], max_model_len=cfg['context'],
        max_num_seqs=1, max_num_batched_tokens=4096, batch_size=1)
    config['model_kwargs']['num_gpu_blocks_override'] = cfg['context'] // 16
    adopted = replace(adopted, config=config, source=dict(source_readout=adopted.source, full_post_aggregation=True, expert_profile_changed=False))
    return NativeBackend(adopted, load_model=False)


def preflight(method):
    backend = backend_for(method, preflight=True)
    destination = ROOT / 'preflight' / method.lower(); destination.mkdir(parents=True, exist_ok=False)
    db = sqlite3.connect(destination / 'requests.sqlite3')
    db.execute('CREATE TABLE requests (rid TEXT, mode TEXT, request_hash TEXT, input_tokens INTEGER, max_tokens INTEGER, status TEXT, error TEXT, PRIMARY KEY(rid,mode))')
    failures = []; counts = Counter(); started = time.monotonic(); max_input = 0; required_capacity = 0; schemas = set()
    for rid, ordinal, sample in sample_rows(method):
        p = packet(sample); validate_pool(p, sample['pool'])
        for mode, expected_hash in sample['request_hashes'].items():
            req = request(p, sample['pool'], mode=mode)
            assert digest(req) == expected_hash
            try:
                count = backend.count_tokens(req)
                schema_hash = digest(req['schema'])
                if schema_hash not in schemas:
                    backend.preflight(req); schemas.add(schema_hash)
                error = None; status = 'passed'
            except Exception as exc:
                count = None; status = 'failed'; error = type(exc).__name__ + ': ' + str(exc)
                failures.append(dict(request_id=rid, mode=mode, error=error))
            db.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?)', (rid, mode, expected_hash, count, req['max_tokens'], status, error))
            counts[status] += 1
            if count is not None:
                max_input = max(max_input, count); required_capacity = max(required_capacity, count + req['max_tokens'])
        if ordinal % 250 == 0:
            db.commit(); dump(destination / 'progress.json', dict(method=method, inputs=ordinal + 1, counts=counts, max_input_tokens=max_input, elapsed_seconds=time.monotonic()-started))
    db.commit(); db.close()
    result = dict(status='passed' if not failures else 'failed', method=method, requests=sum(counts.values()), counts=counts,
        max_input_tokens=max_input, required_capacity=required_capacity, failures=failures,
        elapsed_seconds=time.monotonic()-started, new_model_calls=0)
    dump(destination / 'terminal.json', result)
    if failures:
        raise RuntimeError('Complete-input preflight failed; no model submitted')


def live(method, attempt):
    run = ROOT / 'runs' / method.lower(); run.mkdir(parents=True, exist_ok=True)
    lock = (run / 'worker.lock').open('w'); fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    history = run / ('attempt_' + attempt); history.mkdir(exist_ok=False)
    prep = json.loads((ROOT / 'preparation.json').read_text())
    for path, expected in prep['source_code_sha256'].items():
        assert sha(path) == expected, path
    for path, expected in json.loads((ROOT / 'runtime_sources.json').read_text()).items():
        assert sha(path) == expected, path
    assert sha(ROOT / 'samples.sqlite3') == prep['samples_sha256']
    capacity_plan = json.loads((ROOT / 'capacity_plan.json').read_text())
    assert capacity_plan['status'] == 'complete'
    capacity_failures = capacity_plan['methods'][method]['capacity_failures']
    backend = None; ledger = Ledger(run / 'ledger.sqlite3'); started = time.monotonic(); last_report = 0
    pilot = Path(prep['pilot_root']); pilot_name = json.loads((pilot / 'run_map.json').read_text())[method]
    pilot_launch = json.loads((pilot / 'runs' / pilot_name / 'launch.json').read_text())
    pilot_samples = {r['request_id']: r for r in json.loads((pilot / 'inference' / (method.lower() + '.json')).read_text())}
    try:
        backend = backend_for(method)
        actual_config=deepcopy(backend.adopted.config);old_config=deepcopy(pilot_launch['config'])
        actual_memory=actual_config.pop('gpu_memory_utilization');old_memory=old_config.pop('gpu_memory_utilization')
        assert actual_config == old_config, 'Only a declared memory-budget change can reuse pilot requests'
        dump(history / 'launch.json', dict(timestamp=now(), pid=os.getpid(), method=method, attempt=attempt,
            config=backend.adopted.config, config_hash=backend.adopted.config_hash,
            runtime_sha256=sha(ROOT / 'runtime.json'), cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES')))
        for rid, ordinal, sample in sample_rows(method):
            p = packet(sample); pool = sample['pool']; validate_pool(p, pool)
            for mode, expected_hash in sample['request_hashes'].items():
                artifact = run / 'requests' / f'{ordinal // 250:03d}' / (rid + '_' + mode + '.json.gz')
                if ledger.complete(rid, mode, expected_hash, pool['pool_hash'], artifact):
                    continue
                if (ROOT / 'STOP').exists() or shutil.disk_usage(ROOT).free < 100 * 1024**3:
                    raise RuntimeError('Stopped before submission by resource/operator guard')
                req = request(p, pool, mode=mode); assert digest(req) == expected_hash
                if rid + ':' + mode in capacity_failures:
                    measured = capacity_failures[rid + ':' + mode]
                    error = 'context_capacity_exceeded: ' + str(measured['required_capacity']) + ' > 65536; no truncation or model submission'
                    results = {mode: resolve(p, pool, raw='', mode=mode, aggregation_error=error)}
                    if mode == 'rule_prompt':
                        results['strict'] = resolve(p, pool, raw='', mode=mode, strict=True, aggregation_error=error)
                    record = dict(status='complete', method=method, request_id=rid, mode=mode,
                        origin='capacity_unavailable', request_hash=expected_hash, pool_hash=pool['pool_hash'],
                        results=results, usage=dict(input_tokens=0, output_tokens=0, elapsed_seconds=0),
                        capacity_evidence=measured, new_model_calls=0, physical=[])
                elif rid in pilot_samples:
                    original = pilot / 'runs' / pilot_name / (rid + '_' + mode)
                    old = json.loads((original / 'results.json').read_text()); response = json.loads((original / 'model_response.json').read_text())
                    assert digest(pilot_samples[rid]['requests'][mode]) == expected_hash == response['request_hash']
                    assert pilot_samples[rid]['pool']['pool_hash'] == pool['pool_hash']
                    physical,_=backend.prepare(req);old_physical=deepcopy(response['physical'][0]['request'])
                    physical['engine_kwargs'].pop('gpu_memory_utilization');old_physical['engine_kwargs'].pop('gpu_memory_utilization')
                    assert digest(physical)==digest(old_physical), 'Pilot model-facing request differs beyond memory quota'
                    record = dict(status='complete', method=method, request_id=rid, mode=mode, origin='pilot',
                        request_hash=expected_hash, pool_hash=pool['pool_hash'], results=old['results'], usage=old['usage'],
                        source_ref=dict(path=str(original / 'model_response.json'), sha256=sha(original / 'model_response.json'),
                            results_path=str(original / 'results.json'), results_sha256=sha(original / 'results.json'),
                            physical_request_equal_excluding_memory_quota=True,
                            original_memory_quota=old_memory,current_memory_quota=actual_memory))
                else:
                    if backend.llm is None:
                        backend.start(); dump(history / 'engine_started.json', dict(timestamp=now(), initialization_seconds=backend.initialization_seconds))
                    ledger.begin(rid, mode, expected_hash, pool['pool_hash'])
                    try:
                        value = backend(req); usage = value.events[0]
                        error = 'output_truncated' if usage.get('finish_reason') == 'length' else None
                        results = {mode: resolve(p, pool, raw=value.value, mode=mode, aggregation_error=error)}
                        if mode == 'rule_prompt':
                            results['strict'] = resolve(p, pool, raw=value.value, mode=mode, strict=True, aggregation_error=error)
                        record = dict(status='complete', method=method, request_id=rid, mode=mode, origin='new',
                            request_hash=expected_hash, pool_hash=pool['pool_hash'], config_hash=backend.adopted.config_hash,
                            results=results, usage=usage, raw=value.value, physical=backend.physical_calls,
                            five_proposers_finished=[e for e in pool['events'] if e['event']=='proposer_finished'])
                    except Exception:
                        write_record(history / (rid + '_' + mode + '_failure.json.gz'), dict(
                            request_id=rid, mode=mode, request_hash=expected_hash, pool_hash=pool['pool_hash'],
                            traceback=traceback.format_exc(), physical=backend.physical_calls))
                        raise
                file_sha = write_record(artifact, record)
                ledger.commit(record, artifact, file_sha)
                backend.physical_calls.clear()
                if time.monotonic() - last_report > 60:
                    progress = dict(method=method, timestamp=now(), latest_request=rid + ':' + mode,
                        planned_requests=41715, attempt_wall_seconds=time.monotonic()-started, **ledger.progress())
                    dump(run / 'progress.json', progress); print(json.dumps(progress), flush=True); last_report = time.monotonic()
        progress = ledger.progress(); assert progress['counts']['complete'] == 41715
        dump(run / 'terminal.json', dict(status='complete', timestamp=now(), method=method, attempt=attempt,
            attempt_wall_seconds=time.monotonic()-started, **progress))
        dump(history / 'terminal.json', dict(status='complete', timestamp=now()))
    except BaseException:
        dump(history / 'failure.json', dict(status='failed', timestamp=now(), traceback=traceback.format_exc(), **ledger.progress()))
        raise
    finally:
        if backend is not None and backend.llm is not None:
            cleanup = time.monotonic(); backend.llm.llm_engine.engine_core.shutdown(); backend.llm = None
            dump(history / 'cleanup.json', dict(status='complete', seconds=time.monotonic()-cleanup, timestamp=now()))
        ledger.close(); lock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method', choices=['M4', 'M5'], required=True)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--attempt', default='1')
    args = parser.parse_args()
    if args.preflight:
        preflight(args.method)
    else:
        live(args.method, args.attempt)
