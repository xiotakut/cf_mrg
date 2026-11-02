"""Independent, read-only final artifact audit. No model or scorer imports."""
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import sqlite3
import time
import traceback
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ARMS = ('original_C0', 'strong_B', 'gen', 'select', 'rule_prompt', 'strict')
MODES = ('gen', 'select', 'rule_prompt')


def now():
    return datetime.now().astimezone().isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, allow_nan=False,
        separators=(',', ':')).encode()).hexdigest()


def rows(path):
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            yield json.loads(line)


def save(name, value):
    path = HERE / name
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def main():
    start = time.monotonic()
    save('started.json', {'timestamp': now(), 'mode': 'read_only_artifacts_no_rescoring'})
    final = read(ROOT / 'final_summary.json')
    final_sha = sha(ROOT / 'final_summary.json')
    assert final['status'] == 'complete'
    prep = read(ROOT / 'preparation.json')
    source_checks = {}
    for filename in ('runtime_sources.json', 'elastic/sources.json'):
        sources = read(ROOT / filename)
        for path, checksum in sources.items():
            assert sha(path) == checksum, path
        source_checks[filename] = len(sources)
    for path, checksum in prep['source_code_sha256'].items():
        assert sha(path) == checksum, path
    assert sha(ROOT / 'samples.sqlite3') == prep['samples_sha256']
    assert sha(ROOT / 'protected_B.sqlite3') == prep['protected_sha256']
    samples = sqlite3.connect((ROOT / 'samples.sqlite3').as_uri() + '?mode=ro', uri=True)
    baselines = sqlite3.connect((ROOT / 'protected_B.sqlite3').as_uri() + '?mode=ro', uri=True)
    queue = sqlite3.connect((ROOT / 'elastic/queue.sqlite3').as_uri() + '?mode=ro', uri=True)
    assert queue.execute('select method,status,count(*) from inputs group by method,status order by method').fetchall() == [
        ('M4', 'complete', 13905), ('M5', 'complete', 13905)]
    queue.close()
    output = {'methods': {}, 'frozen_source_checks': source_checks}
    total_new = Counter()
    earliest = []
    latest = []
    for method in ('M4', 'M5'):
        print(now(), 'checking', method, flush=True)
        result = final['methods'][method]
        assert result == read(ROOT / 'analysis' / method.lower() / 'quality_summary.json')
        receipt = read(ROOT / 'analysis' / method.lower() / 'receipt.json')
        assert receipt == final['scoring_receipts'][method] and receipt['status'] == 'complete'
        for binding in receipt['scorer_sources'] + [receipt['summary_source'], receipt['parallel_handover']]:
            assert sha(binding['path']) == binding['sha256']
        native = {rid: json.loads(zlib.decompress(blob)) for rid, blob in baselines.execute(
            'select rid,payload from baseline where method=?', (method,))}
        assert len(native) == 13905
        ledger = sqlite3.connect((ROOT / 'runs' / method.lower() / 'ledger.sqlite3').as_uri() + '?mode=ro', uri=True)
        ledger.row_factory = sqlite3.Row
        records = ledger.execute('select * from tasks order by rid,mode').fetchall()
        assert len(records) == 41715
        assert Counter(r['mode'] for r in records) == {m: 13905 for m in MODES}
        assert all(r['status'] == 'complete' for r in records)
        current_records = {(r['rid'], r['mode']): dict(r) for r in records}
        backup = sqlite3.connect((ROOT / 'elastic/handover' / (method.lower() + '_ledger.sqlite3')).as_uri() + '?mode=ro', uri=True)
        backup.row_factory = sqlite3.Row
        old_rows = {(r['rid'], r['mode']): dict(r) for r in backup.execute('select * from tasks')}
        backup.close()
        preserved = list(rows(ROOT / 'elastic/handover' / (method.lower() + '_preserved.jsonl.gz')))
        assert len(preserved) == len(old_rows) == final['parallel_handover']['preserved_requests'][method]
        for old in preserved:
            key = (old['rid'], old['mode'])
            assert current_records[key] == old_rows[key]
            assert current_records[key]['artifact'] == old['path']
            assert current_records[key]['artifact_sha'] == old['sha256']
        earliest.append(min(r['submitted_at'] for r in records if r['submitted_at']))
        latest.append(max(r['completed_at'] for r in records))
        cache_rid = None
        costs = defaultdict(Counter)
        process = Counter()
        errors = Counter()
        modes_per_input = defaultdict(set)
        origin_counts = Counter()
        worker_counts = Counter()
        launch_cache = {}
        for index, record in enumerate(records):
            rid, mode, origin = record['rid'], record['mode'], record['origin']
            modes_per_input[rid].add(mode)
            if cache_rid != rid:
                poolhash, blob = samples.execute('select pool_hash,payload from samples where method=? and rid=?',
                                                (method, rid)).fetchone()
                sample = json.loads(zlib.decompress(blob))
                assert set(sample['pool']['proposals']) == {'A1', 'A2', 'A3', 'A4', 'A5'}
                assert {e['role'] for e in sample['pool']['events'] if e['event'] == 'proposer_finished'} == {'A1', 'A2', 'A3', 'A4', 'A5'}
                assert sample['pool']['new_expert_model_calls'] == 0
                cache_rid = rid
            raw = Path(record['artifact']).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == record['artifact_sha']
            row = json.loads(gzip.decompress(raw))
            assert (row['method'], row['request_id'], row['mode'], row['origin']) == (method, rid, mode, origin)
            assert row['pool_hash'] == record['pool_hash'] == poolhash
            assert row['request_hash'] == record['request_hash'] == sample['request_hashes'][mode]
            assert row['usage'] == json.loads(record['usage'])
            origin_counts[origin] += 1
            for arm, answer in row['results'].items():
                assert answer['pool_hash'] == poolhash
                assert answer['native_hash'] == digest(answer['native_answer'])
            if origin == 'new':
                physical = row['physical']
                assert len(physical) == 1 and physical[0]['status'] == 'complete'
                request = physical[0]['request']
                sampling = request['sampling_params']
                assert sampling['temperature'] == 0 and sampling['seed'] == 42
                assert sampling['max_tokens'] == (2048 if mode == 'gen' else 256)
                assert sampling['truncate_prompt_tokens'] is None
                engine = request['engine_kwargs']
                assert (engine['max_model_len'], engine['max_num_seqs'], engine['num_gpu_blocks_override']) == (65536, 1, 4096)
                if 'parallel_worker' in row:
                    worker = row['parallel_worker']
                    if worker not in launch_cache:
                        path = ROOT / 'elastic/workers' / worker / 'launch.json'
                        launch_cache[worker] = (read(path), sha(path))
                    launch, checksum = launch_cache[worker]
                    assert row['worker_launch_sha256'] == checksum
                    assert row['config_hash'] == launch['config_hash']
                    assert engine['gpu_memory_utilization'] == .95
                    worker_counts[worker] += 1
            elif origin == 'pilot':
                ref = row['source_ref']
                assert sha(ref['path']) == ref['sha256']
                assert sha(ref['results_path']) == ref['results_sha256']
                assert read(ref['results_path'])['results'] == row['results']
            else:
                assert origin == 'capacity_unavailable'
                assert row['new_model_calls'] == 0 and row['physical'] == []
            cost = costs[origin + ':' + mode]
            cost['requests'] += 1
            for key in ('input_tokens', 'output_tokens', 'elapsed_seconds'):
                cost[key] += row['usage'][key]
            errors[mode] += bool(row['results'][mode]['aggregator_error'])
            if mode == 'rule_prompt':
                strict = row['results']['strict']
                prompt = row['results']['rule_prompt']
                assert digest(strict['native_answer']) == digest(native[rid]['native_answer'])
                assert strict['capability_predicate'] == native[rid]['predicate']
                assert strict['aggregator_raw'] == prompt['aggregator_raw']
                process['strict_complete_native_equal'] += 1
                process['strict_route_equal'] += 1
                process['rule_prompt_id_compliant'] += prompt['proposed_candidate_id'] == strict['selected_candidate_id']
                process['rule_prompt_full_rule_compliant'] += prompt['rule_compliant'] is True
                process['strict_id_corrections'] += strict['selection_corrected']
                process['rule_prompt_native_differs_from_B'] += prompt['native_hash'] != strict['native_hash']
            if (index + 1) % 10000 == 0:
                print(now(), method, 'response hashes verified', index + 1, flush=True)
        assert set(modes_per_input) == set(native)
        assert all(modes == set(MODES) for modes in modes_per_input.values())
        assert dict(process) == result['process']
        assert dict(errors) == result['aggregator_errors']
        for key, actual in costs.items():
            for field, value in actual.items():
                assert math.isclose(value, result['costs'][key][field], rel_tol=1e-12, abs_tol=1e-5)
                if key.startswith('new:'):
                    total_new[field] += value
        reports = {r['arm']: r for r in result['reports']}
        assert set(reports) == set(ARMS)
        grouped = {arm: {} for arm in ARMS}
        for row in rows(ROOT / 'analysis' / method.lower() / 'per_input_status.jsonl.gz'):
            bucket = grouped[row['arm']]
            assert row['request_id'] not in bucket
            assert row['analysis_status'] == 'scored'
            bucket[row['request_id']] = row
        damage = {}
        for arm, values in grouped.items():
            report = reports[arm]
            assert set(values) == set(native)
            assert sum(r['correct'] is True for r in values.values()) == report['correct_inputs']
            assert sum(bool(r['unavailable']) for r in values.values()) == report['unavailable_inputs']
            assert sum(r['native_mapping_count'] for r in values.values()) == 15616
            if arm not in ('original_C0', 'strong_B'):
                damage[arm] = dict(
                    harmed=sum(grouped['strong_B'][rid]['correct'] is True and r['correct'] is not True for rid, r in values.items()),
                    repaired=sum(grouped['strong_B'][rid]['correct'] is not True and r['correct'] is True for rid, r in values.items()))
        assert damage == result['damage']
        unit_groups = defaultdict(dict)
        for row in rows(ROOT / 'analysis' / method.lower() / 'native_units.jsonl.gz'):
            bucket = unit_groups[(row['arm'], row['category'])]
            assert row['unit_id'] not in bucket and row['complete'] is True
            bucket[row['unit_id']] = row['score']
        for arm, report in reports.items():
            for category in report['native_categories']:
                values = unit_groups[(arm, category['category'])]
                assert len(values) == category['units'] == category['completed_units']
                assert math.isclose(math.fsum(values.values()) / len(values), category['mean_native_unit_score'], abs_tol=1e-12)
            assert len(unit_groups[(arm, 'ALL')]) == 6104
        for category in ('ALL', 'R1', 'R2', 'R3', 'R4', 'R5'):
            assert unit_groups[('strong_B', category)] == unit_groups[('strict', category)]
        pairs = defaultdict(dict)
        for row in rows(ROOT / 'analysis' / method.lower() / 'pairs.jsonl.gz'):
            bucket = pairs[(row['arm'], row['relation'])]
            assert row['pair_id'] not in bucket and row['complete'] is True
            bucket[row['pair_id']] = row['both_correct']
        for arm, report in reports.items():
            for pair in report['pairs']:
                values = pairs[(arm, pair['relation'])]
                assert len(values) == pair['pairs'] == pair['completed_pairs']
                assert sum(values.values()) == pair['both_correct']
        scored_counts = Counter()
        baseline_scores = {}
        strict_scores = {}
        for row in rows(ROOT / 'analysis' / method.lower() / 'native_scored.jsonl.gz'):
            assert row['analysis_status'] == 'scored'
            scored_counts[row['arm']] += 1
            if row['arm'] in ('strong_B', 'strict'):
                target = baseline_scores if row['arm'] == 'strong_B' else strict_scores
                assert row['record_id'] not in target
                target[row['record_id']] = {k: v for k, v in row.items() if k not in ('arm', 'score_provenance')}
        assert scored_counts == {arm: 15616 for arm in ARMS}
        assert baseline_scores == strict_scores
        old = read(Path(prep['historical_full_root']) / 'analysis' / method.lower() / 'quality_summary.json')
        for arm in ('original_C0', 'strong_B'):
            saved = next(r for r in old['reports'] if r['method'] == method and r['arm'] == arm)
            for key in ('correct_inputs', 'unavailable_inputs', 'native_categories', 'pairs'):
                assert reports[arm][key] == saved[key]
        output['methods'][method] = {
            'artifact_hashes_verified': len(records), 'inputs': len(native),
            'pre_handover_complete_rows_and_hashes_preserved': len(preserved),
            'origin_counts': dict(origin_counts), 'process': dict(process), 'aggregator_errors': dict(errors),
            'native_mapping_rows_verified': dict(scored_counts), 'category_means_verified': len(unit_groups),
            'strict_unit_and_mapping_scores_equal_B': True, 'damage': damage,
            'new_requests_by_parallel_worker': dict(worker_counts),
            'ALL': {arm: next(c['mean_native_unit_score'] for c in reports[arm]['native_categories'] if c['category'] == 'ALL') for arm in ARMS}}
        ledger.close()
    samples.close()
    baselines.close()
    for key, value in total_new.items():
        assert math.isclose(value, final['new_physical_cost'][key], rel_tol=1e-12, abs_tol=1e-5)
    assert total_new['requests'] == 82928
    assert sum(m['origin_counts']['pilot'] for m in output['methods'].values()) == 144
    assert sum(m['origin_counts']['capacity_unavailable'] for m in output['methods'].values()) == 358
    terminal = read(ROOT / 'elastic/terminal.json')
    assert terminal['status'] == 'complete' and terminal['exit_code'] == 0
    worker_receipts = {}
    for worker, waited in final['parallel_workers'].items():
        folder = ROOT / 'elastic/workers' / worker
        assert waited == read(folder / 'wait.json') and waited['exit_code'] == 0
        assert read(folder / 'terminal.json')['status'] == read(folder / 'cleanup.json')['status'] == 'complete'
        pid = waited['identity']['pid']
        proc = Path('/proc') / str(pid) / 'stat'
        same_alive = proc.exists() and proc.read_text().rsplit(')', 1)[1].split()[19] == waited['identity']['start_ticks']
        assert not same_alive
        worker_receipts[worker] = {'exit_code': 0, 'original_process_absent': True, 'gpu': waited['gpu']}
    assert sha(ROOT / 'final_summary.json') == final_sha
    output.update(status='passed', timestamp=now(), elapsed_seconds=time.monotonic()-start,
        final_summary_sha256=final_sha, new_physical_cost_recomputed=dict(total_new),
        first_request_at=min(earliest), last_request_at=max(latest), workers=worker_receipts,
        wall_seconds_first_request_to_closeout=(datetime.fromisoformat(final['timestamp'])-datetime.fromisoformat(min(earliest))).total_seconds(),
        data4_free_bytes=shutil.disk_usage(ROOT).free, new_model_calls_by_verification=0, native_rescoring_calls=0)
    save('validation.json', output)
    print(json.dumps({'status': 'passed', 'elapsed_seconds': output['elapsed_seconds'], 'artifacts': 83430,
                      'strict_native_equal': 27810, 'category_means': 72}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        save('failure.json', {'timestamp': now(), 'traceback': traceback.format_exc()})
        raise
