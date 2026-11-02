"""Score durable full-panel outputs with the unchanged native scorer and denominators."""
import argparse
from collections import Counter, defaultdict
import gzip
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import time
import zlib

ROOT = Path(__file__).parent
WORK = Path('/home/data3/txy')
FULL = WORK / 'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/full_v5'
sys.path.insert(0, str(WORK)); sys.path.insert(0, str(ROOT))
from cf_moa.contracts import digest
from run_full import dump, now, read_record, sha

spec = importlib.util.spec_from_file_location('frozen_full_v5_summary', FULL / 'analyze_full.py')
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
ARMS = ['original_C0', 'strong_B', 'gen', 'select', 'rule_prompt', 'strict']
old.ARMS = ARMS


def compressed_rows(path, values):
    path = Path(path); tmp = path.with_suffix(path.suffix+'.tmp')
    with gzip.open(tmp, 'wt', compresslevel=3) as stream:
        for row in values:
            stream.write(json.dumps(row, ensure_ascii=False)+'\n')
    tmp.replace(path)


def main(method):
    started = time.monotonic(); name = method.lower(); run = ROOT / 'runs' / name
    terminal=json.loads((run / 'terminal.json').read_text())
    assert terminal['status'] == 'complete'
    assert json.loads((run / ('attempt_'+terminal['attempt']) / 'cleanup.json').read_text())['status'] == 'complete'
    inference_launch=run/('attempt_'+terminal['attempt'])/'launch.json'
    launch=json.loads(inference_launch.read_text())
    out = ROOT / 'analysis' / name; out.mkdir(parents=True, exist_ok=True)
    if (out / 'receipt.json').exists() and json.loads((out / 'receipt.json').read_text())['status'] == 'complete':
        print('Already complete:', method); return
    prep = json.loads((ROOT / 'preparation.json').read_text())
    for path, expected in prep['source_code_sha256'].items():
        assert sha(path) == expected
    for path, expected in json.loads((ROOT / 'runtime_sources.json').read_text()).items():
        assert sha(path) == expected
    assert sha(ROOT / 'protected_B.sqlite3') == prep['protected_sha256']
    items = {r['request_id']:r for r in old.rows(FULL / 'offline/items.jsonl')}
    evaluations = list(old.rows(FULL / 'offline/evaluations.jsonl'))
    pairs = list(old.rows(FULL / 'offline/pairs.jsonl'))
    assert len(items) == 13905 and len(evaluations) == 15616
    assert len({e['unit_id'] for e in evaluations if e['role']!='reference'}) == 6104
    sample_db = sqlite3.connect((ROOT / 'samples.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
    pools = {rid:pool_hash for rid,pool_hash in sample_db.execute('SELECT rid,pool_hash FROM samples WHERE method=?',(method,))}; sample_db.close()
    db = sqlite3.connect((ROOT / 'protected_B.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
    baseline = {rid:json.loads(zlib.decompress(payload)) for rid,payload in db.execute('SELECT rid,payload FROM baseline WHERE method=?',(method,))}; db.close()
    assert set(baseline) == set(items)
    ledger = sqlite3.connect((run / 'ledger.sqlite3').as_uri()+'?mode=ro',uri=True)
    records = list(ledger.execute('SELECT rid,mode,status,origin,artifact,artifact_sha,request_hash,pool_hash FROM tasks'))
    ledger.close(); assert len(records) == 41715 and all(row[2]=='complete' for row in records)
    native = {'strong_B':{rid:b['native_answer'] for rid,b in baseline.items()}}
    native.update({a:{} for a in ARMS[2:]})
    process = []; costs = defaultdict(Counter); error_counts = Counter(); rule_stats = Counter()
    for rid,mode,status,origin,path,file_sha,request_hash,pool_hash in records:
        assert sha(path) == file_sha
        row = read_record(path)
        if origin=='new':
            assert row['config_hash']==launch['config_hash']
        assert row['request_hash'] == request_hash and row['pool_hash'] == pool_hash == pools[rid]
        assert row['method'] == method and row['request_id'] == rid and row['mode'] == mode
        for arm,result in row['results'].items():
            assert result['pool_hash'] == pool_hash and result['native_hash'] == digest(result['native_answer'])
            native[arm][rid] = result['native_answer']
        usage = row['usage']; cost = costs[origin+':'+mode]; cost['requests'] += 1
        for key in ('input_tokens','output_tokens','elapsed_seconds'):
            cost[key] += usage[key]
        error_counts[mode] += bool(row['results'][mode]['aggregator_error'])
        if mode=='rule_prompt':
            strict = row['results']['strict']; prompt = row['results']['rule_prompt']
            assert digest(strict['native_answer']) == digest(baseline[rid]['native_answer'])
            assert strict['capability_predicate'] == baseline[rid]['predicate']
            assert strict['aggregator_raw'] == prompt['aggregator_raw']
            rule_stats['strict_complete_native_equal'] += 1; rule_stats['strict_route_equal'] += 1
            rule_stats['rule_prompt_id_compliant'] += prompt['proposed_candidate_id'] == strict['selected_candidate_id']
            rule_stats['rule_prompt_full_rule_compliant'] += prompt['rule_compliant'] is True
            rule_stats['strict_id_corrections'] += strict['selection_corrected']
            rule_stats['rule_prompt_native_differs_from_B'] += prompt['native_hash'] != strict['native_hash']
            process.append(dict(request_id=rid, proposed_id=prompt['proposed_candidate_id'],
                expected_id=strict['selected_candidate_id'], full_rule_compliant=prompt['rule_compliant'],
                id_corrected=strict['selection_corrected'], strict_native_equal=True, strict_route_equal=True,
                aggregation_error=prompt['aggregator_error']))
    assert all(set(values)==set(items) for values in native.values())
    cache_path = out / 'native_score_cache.sqlite3'
    if not cache_path.exists():
        source = sqlite3.connect((FULL/'analysis'/name/'native_score_cache.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
        target = sqlite3.connect(cache_path); source.backup(target); target.close(); source.close()
    cache = old.ScoreCache(cache_path)
    original = {r['record_id']:r for r in old.rows(FULL / 'offline' / (name+'_C0_native_scored.jsonl'))}
    all_scored=[]; all_unique=[]; all_units=[]; all_pairs=[]; reports=[]
    for arm in ARMS:
        scored={}
        for e in evaluations:
            rid=e['request_id']; row=dict(method=method,arm=arm,request_id=rid,record_id=e['record_id'],analysis_status='scored')
            if arm=='original_C0':
                row.update(old.scientific_score(original[e['record_id']]),score_provenance=dict(kind='unchanged_formal_C0_score'))
            else:
                value,proof=cache.obtain(method,items[rid],e,native[arm][rid],grade=arm!='strong_B')
                assert value is not None, 'Saved B score missing; do not silently regrade old B'
                row.update(value,score_provenance=proof,native_answer_ref=digest(native[arm][rid]))
            scored[e['record_id']]=row
        report,unique,units,pair_rows=old.summarize(method,arm,scored,evaluations,pairs,items)
        assert report['status']=='complete' and report['scored_native_mappings']==15616
        reports.append(report);all_scored.extend(scored.values());all_unique.extend(unique);all_units.extend(units);all_pairs.extend(pair_rows)
    effects,atoms,families=old.comparisons(all_unique,all_units,all_pairs)
    old_reports={r['arm']:r for r in json.loads((FULL/'analysis'/name/'quality_summary.json').read_text())['reports'] if r['method']==method}
    for arm in ('original_C0','strong_B'):
        current=next(r for r in reports if r['arm']==arm);saved=old_reports[arm]
        assert current['correct_inputs']==saved['correct_inputs']
        assert current['unavailable_inputs']==saved['unavailable_inputs']
        assert current['pairs']==saved['pairs']
        assert current['native_categories']==saved['native_categories']
    base=next(r for r in reports if r['arm']=='strong_B');strict=next(r for r in reports if r['arm']=='strict')
    for key in ('correct_inputs','unavailable_inputs','native_categories','pairs','auxiliary'):
        assert base[key]==strict[key]
    b={r['request_id']:r for r in all_unique if r['arm']=='strong_B'}
    damage={arm:dict(harmed=sum(b[r['request_id']]['correct'] is True and r['correct'] is not True for r in all_unique if r['arm']==arm),
        repaired=sum(b[r['request_id']]['correct'] is not True and r['correct'] is True for r in all_unique if r['arm']==arm)) for arm in ARMS[2:]}
    assert damage['strict']==dict(harmed=0,repaired=0)
    for filename,data in [('native_scored',all_scored),('per_input_status',all_unique),('native_units',all_units),
        ('pairs',all_pairs),('paired_atoms',atoms),('family_effects',families),('process',process)]:
        compressed_rows(out/(filename+'.jsonl.gz'),data)
    dump(out/'quality_summary.json',dict(status='complete',method=method,reports=reports,comparisons=effects,
        damage=damage,process=rule_stats,aggregator_errors=error_counts,costs=costs,
        independent=False,frozen_experts=True,denominator_policy='13905 inputs; 15616 mappings; 6104 non-reference ALL units; every failure retained'))
    receipt=dict(status='complete',method=method,timestamp=now(),new_model_calls=0,new_cpu_native_scores=cache.new_calls,
        score_cache_hits=dict(cache.reuse),scorer_sources=cache.lock,summary_source=dict(path=str(FULL/'analyze_full.py'),sha256=sha(FULL/'analyze_full.py')),
        elapsed_seconds=time.monotonic()-started,new_expert_calls=0,strict_equivalence=rule_stats['strict_complete_native_equal'],script_sha256=sha(Path(__file__)))
    receipt['inference_launch']=dict(path=str(inference_launch),sha256=sha(inference_launch),config_hash=launch['config_hash'],runtime_sha256=launch['runtime_sha256'])
    cache.db.execute('PRAGMA wal_checkpoint(TRUNCATE)');cache.db.close()
    dump(out/'receipt.json',receipt);print(json.dumps(receipt),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--method',choices=['M4','M5'],required=True)
    main(parser.parse_args().method)
