"""Stdlib-only verification of published saved results; no inference or clinical rescoring."""
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((ROOT / name).read_text())


def read_rows(name):
    p = ROOT / name
    opener = gzip.open if p.suffix == '.gz' else open
    with opener(p, 'rt', encoding='utf-8') as f:
        if '.csv' in p.name:
            return list(csv.DictReader(f))
        return [json.loads(line) for line in f if line.strip()]


def close(a, b, tol=1e-8):
    assert math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol), (a, b)


def boolean(x):
    assert x in ('True', 'False', True, False), x
    return x is True or x == 'True'


def grouped(rows, keys):
    out = defaultdict(list)
    for row in rows:
        out[tuple(row[k] for k in keys)].append(row)
    return out


def success(r):
    return r['score']['correct'] is True


def main():
    manifest = read_json('MANIFEST.json')
    for entry in manifest['files']:
        p = ROOT / entry['path']
        assert p.is_file(), p
        assert p.stat().st_size == entry['bytes'], p
        assert hashlib.sha256(p.read_bytes()).hexdigest() == entry['sha256'], p

    summary = read_json('e1_corrected/summary.json')
    oof = read_rows('e1_corrected/out_of_fold.jsonl.gz')
    assert len(oof) == 8798 * 7
    families = defaultdict(set)
    ids = set()
    for r in oof:
        key = r['method'], r['record_id']
        assert key not in ids
        ids.add(key)
        families[r['family']].add(r['fold'])
    assert len(families) == 4216 and all(len(x) == 1 for x in families.values())
    assert {r['fold'] for r in oof} == {0, 1, 2, 3, 4}
    weights = sum(r['weight'] for r in oof)
    briers = {}
    for model in ['base', 'functional']:
        score = sum(r['weight'] * (r[model+'_probability'] - (1-r['correct']))**2 for r in oof) / weights
        close(score, summary['metrics'][model]['brier'])
        briers[model] = score
    close(briers['base'] - briers['functional'], summary['brier_improvement'])
    unit_groups = grouped(read_rows('e1_corrected/unit_scores.csv.gz'), ['category', 'method'])
    for row in read_rows('e1_corrected/category_reproduction.csv'):
        g = unit_groups[row['category'], row['method']]
        assert len(g) == int(row['units'])
        close(sum(float(r['score']) for r in g)/len(g), row['score'])

    scored = {}
    for experiment, size, arms in [('e4a',123,2), ('e4b',80,2), ('e5',112,4)]:
        data = read_rows(experiment+'/analysis/native_scored.jsonl')
        assert len(data) == size * arms * 2
        assert all('native_answer' not in r for r in data)
        groups = grouped(data, ['method', 'arm'])
        assert len(groups) == arms * 2
        for g in groups.values():
            assert len(g) == size
            assert len({r['request_id'] for r in g}) == size
        scored[experiment] = data
        if experiment == 'e5':
            continue
        for row in read_rows(experiment+'/analysis/overall.csv'):
            g = groups[row['method'], row['arm']]
            ncorrect = sum(success(r) for r in g)
            nunavailable = sum(not r['native_available'] for r in g)
            assert ncorrect == int(row['correct'])
            assert nunavailable == int(row['unavailable'])
            assert len(g) == int(row['n'])
            close(ncorrect/len(g), row['accuracy'])

    for method in ['M4', 'M5']:
        by_request = grouped([r for r in scored['e4a'] if r['method']==method], ['request_id'])
        win = loss = 0
        for g in by_request.values():
            x = {r['arm']: success(r) for r in g}
            win += x['program_B'] and not x['uniform_LLM']
            loss += x['uniform_LLM'] and not x['program_B']
        saved = read_json('e4a/analysis/'+method.lower()+'_paired.json')
        assert win == saved['program_correct_LLM_incorrect']
        assert loss == saved['LLM_correct_program_incorrect']
        close((win-loss)/123, saved['program_minus_LLM'])

    for row in read_rows('e4b/analysis/paired.csv'):
        data = [r for r in scored['e4b'] if r['method']==row['method'] and
                (row['scope']=='ALL_80_inputs' or r['operation']==row['scope'])]
        by_input = grouped(data, ['input_id'])
        win = loss = 0
        for g in by_input.values():
            x = {r['arm']: success(r) for r in g}
            win += x['conditioned'] and not x['uniform']
            loss += x['uniform'] and not x['conditioned']
        assert len(by_input) == int(row['n'])
        assert win == int(row['conditioned_only']) and loss == int(row['uniform_only'])
        close((win-loss)/len(by_input), row['conditioned_minus_uniform'])

    e5 = scored['e5']
    units = grouped([r for r in e5 if r['role']!='reference'], ['method','arm','unit_id'])
    calculated_units = {}
    for key, g in units.items():
        calculated_units[key] = sum(success(r) for r in g)/len(g)
    for row in read_rows('e5/analysis/unit_scores.csv'):
        close(calculated_units[row['method'],row['arm'],row['unit_id']], row['accuracy'])
    for row in read_rows('e5/analysis/primary_unit_mean.csv'):
        g = [v for k,v in calculated_units.items() if k[:2]==(row['method'],row['arm'])]
        assert len(g) == int(row['units']) == 32
        close(sum(g)/32, row['accuracy'])
    for name in ['all_endpoints','nonreference_judgments']:
        subset = e5 if name=='all_endpoints' else [r for r in e5 if r['role']!='reference']
        groups = grouped(subset, ['method','arm'])
        for row in read_rows('e5/analysis/'+name+'.csv'):
            g = groups[row['method'],row['arm']]
            assert len(g)==int(row['n'])
            assert sum(success(r) for r in g)==int(row['correct'])
            assert sum(r['native_available'] for r in g)==int(row['available'])
    endpoint = {(r['method'],r['arm'],r['request_id']):r for r in e5}
    pairs = read_rows('e5/analysis/paired_behavior.csv')
    assert len(pairs) == 64*4*2
    for row in pairs:
        a = endpoint[row['method'],row['arm'],row['reference']]
        b = endpoint[row['method'],row['arm'],row['variant']]
        assert a['score']['semantic_gold'] == b['score']['semantic_gold']
        assert boolean(row['both_correct']) == (success(a) and success(b))
    groups = grouped(pairs, ['method','arm'])
    for row in read_rows('e5/analysis/pair_summary.csv'):
        g = groups[row['method'],row['arm']]
        assert len(g)==int(row['pairs'])==64
        for k in ['both_correct','both_valid','same_semantic_answer']:
            assert sum(boolean(x[k]) for x in g)==int(row[k])

    calls = []
    cost = {}
    for experiment, expected in [('e4a',246), ('e4b',320), ('e5',1479)]:
        ledger = read_rows(experiment+'/call_ledger.jsonl')
        assert len(ledger)==expected
        assert len({(r['method'],r['key']) for r in ledger})==expected
        for row in ledger:
            assert row['accepted'] is True
            assert row['expected_prompt_sha256']==row['accepted_prompt_sha256']
            assert len(row['source_sha256']) == 64
        cost[experiment] = dict(requests=len(ledger), input_tokens=sum(r['usage']['input_tokens'] for r in ledger),
                                output_tokens=sum(r['usage']['output_tokens'] for r in ledger))
        calls.extend(ledger)
    assert len(calls)==2045
    assert sum(r['usage']['input_tokens'] for r in calls)==8710487
    assert sum(r['usage']['output_tokens'] for r in calls)==520453
    scoring = [r for r in calls if r['sampling_params']['max_tokens']==1]
    assert len(scoring)==64
    assert all(r['experiment']=='e5' and r['usage']['output_tokens']==1 for r in scoring)
    generation_stops = [r for r in calls if r['usage']['finish_reason']=='length' and r['sampling_params']['max_tokens']!=1]
    assert Counter(r['experiment'] for r in generation_stops)=={'e4a':7,'e5':2}
    print(json.dumps(dict(status='passed',manifest_files=len(manifest['files']),E1_families=len(families),
                         E1_brier=briers,scored_rows={k:len(v) for k,v in scored.items()},calls=cost,
                         total_calls=len(calls),normal_one_token_stops=64,generation_budget_stops=9,
                         scope='Saved-score aggregation and integrity; not native clinical rescoring or model rerun.'),
                     ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
