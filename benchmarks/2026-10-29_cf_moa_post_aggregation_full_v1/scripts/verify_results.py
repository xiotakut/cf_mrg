"""Verify exported scores and manifests using only Python's standard library.

No clinical text, gold labels, model, native scorer, or original workspace required.
Complete-response equality is an original-audit claim, not rerun by this script.
"""
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('original_C0','strong_B','gen','select','rule_prompt','strict')


def read(rel):
    return json.loads((ROOT/rel).read_text())


def rows(rel):
    with gzip.open(ROOT/rel,'rt') as f:
        for line in f:
            yield json.loads(line)


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


def equal_number(a,b):
    assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)


def main():
    final=read('final_summary.json')
    audit=read('verification/original_validation.json')
    assert final['status']=='complete' and audit['status']=='passed'
    assert sha(ROOT/'final_summary.json')==audit['final_summary_sha256']
    manifest={}
    for line in (ROOT/'CHECKSUMS.sha256').read_text().splitlines():
        expected,rel=line.split('  ',1)
        assert rel not in manifest
        assert sha(ROOT/rel)==expected,rel
        manifest[rel]=expected
    actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert actual==set(manifest)|{'CHECKSUMS.sha256'}
    for entry in read('source_manifest.json')['entries']:
        if entry['transform']=='byte-identical copy':
            assert sha(ROOT/entry['published'])==entry['source_sha256']
    verified={}
    for method,result in final['methods'].items():
        prefix='analysis/'+method.lower()+'/'
        reports={r['arm']:r for r in result['reports']}
        assert tuple(reports)==ARMS
        groups=defaultdict(list)
        unit_maps={a:{} for a in ARMS}
        for row in rows(prefix+'native_units.jsonl.gz'):
            arm=row['arm']; key=(row['category'],row['unit_id'])
            assert key not in unit_maps[arm] and row['method']==method and row['complete']
            unit_maps[arm][key]=row['score']
            groups[(arm,row['category'])].append(row['score'])
        for arm,report in reports.items():
            for c in report['native_categories']:
                values=groups[(arm,c['category'])]
                assert len(values)==c['units']==c['completed_units']
                equal_number(math.fsum(values)/len(values),c['mean_native_unit_score'])
            assert len(groups[(arm,'ALL')])==6104
            assert report['scored_native_mappings']==15616
        assert unit_maps['strict']==unit_maps['strong_B']
        statuses={a:{} for a in ARMS}
        for row in rows(prefix+'per_input_status.jsonl.gz'):
            assert row['method']==method and row['analysis_status']=='scored'
            target=statuses[row['arm']]
            assert row['request_id'] not in target
            target[row['request_id']]=row
        for arm,values in statuses.items():
            report=reports[arm]
            assert len(values)==13905
            assert sum(bool(r['correct']) for r in values.values())==report['correct_inputs']
            assert sum(bool(r['unavailable']) for r in values.values())==report['unavailable_inputs']
            if arm in result['damage']:
                base=statuses['strong_B']
                harms=sum(bool(base[k]['correct']) and not bool(r['correct']) for k,r in values.items())
                repairs=sum(not bool(base[k]['correct']) and bool(r['correct']) for k,r in values.items())
                assert dict(harmed=harms,repaired=repairs)==result['damage'][arm]
        pair_groups=defaultdict(list)
        pair_ids=set()
        for row in rows(prefix+'pairs.jsonl.gz'):
            assert row['complete'] and row['method']==method
            key=(row['arm'],row['pair_id'])
            assert key not in pair_ids
            pair_ids.add(key)
            pair_groups[(row['arm'],row['relation'])].append(row['both_correct'])
        for arm,report in reports.items():
            for pair in report['pairs']:
                values=pair_groups[(arm,pair['relation'])]
                assert len(values)==pair['pairs']==({'maintain':6838,'respond':1780}[pair['relation']])
                assert sum(values)==pair['both_correct']
                equal_number(sum(values)/len(values),pair['full_both_correct_rate'])
        mappings={a:{} for a in ARMS}
        for row in rows(prefix+'native_mapping_scores.jsonl.gz'):
            assert row['method']==method and row['analysis_status']=='scored'
            arm=row['arm'];key=row['record_id']
            assert key not in mappings[arm]
            mappings[arm][key]={k:v for k,v in row.items() if k not in ('method','arm')}
        assert all(len(v)==15616 for v in mappings.values())
        assert mappings['strict']==mappings['strong_B']
        proc=list(rows(prefix+'process.jsonl.gz'))
        assert len(proc)==len({r['request_id'] for r in proc})==13905
        stats=result['process']
        checks={'strict_complete_native_equal':sum(r['strict_native_equal'] for r in proc),
                'strict_route_equal':sum(r['strict_route_equal'] for r in proc),
                'rule_prompt_id_compliant':sum(r['proposed_id']==r['expected_id'] for r in proc),
                'rule_prompt_full_rule_compliant':sum(bool(r['full_rule_compliant']) for r in proc),
                'strict_id_corrections':sum(r['id_corrected'] for r in proc)}
        assert all(stats[k]==v for k,v in checks.items())
        assert sum(bool(r['aggregation_error']) for r in proc)==result['aggregator_errors']['rule_prompt']
        verified[method]=dict(inputs_per_arm=13905,native_mappings_per_arm=15616,
            ALL_units_per_arm=6104,category_means=36,pair_metric_rows=12,
            strict_saved_mapping_and_unit_scores_equal=True,damage=result['damage'])
    for filename,expected_count in [('categories',72),('pairs',24),('overall',12)]:
        with (ROOT/f'tables/{filename}.csv').open(newline='') as f:
            values=list(csv.DictReader(f))
        assert len(values)==expected_count
        for row in values:
            report=next(r for r in final['methods'][row['method']]['reports'] if r['arm']==row['arm'])
            if filename=='categories':
                c=next(c for c in report['native_categories'] if c['category']==row['category'])
                equal_number(float(row['score']),c['mean_native_unit_score'])
                assert int(row['units'])==c['units']
            elif filename=='overall':
                equal_number(float(row['ALL']),report['native_categories'][0]['mean_native_unit_score'])
                assert int(row['correct_inputs'])==report['correct_inputs']
            else:
                p=next(p for p in report['pairs'] if p['relation']==row['relation'])
                assert int(row['both_correct'])==p['both_correct']
                equal_number(float(row['rate']),p['full_both_correct_rate'])
    costs=Counter()
    for result in final['methods'].values():
        for origin,cost in result['costs'].items():
            if origin.startswith('new:'):
                costs.update(cost)
    for key,value in final['new_physical_cost'].items():
        assert math.isclose(costs[key],value,rel_tol=1e-12,abs_tol=1e-9)
    print(json.dumps(dict(status='passed',methods=verified,verified_file_hashes=len(manifest),
        new_physical_requests=costs['requests'],new_model_calls_by_this_check=0,native_rescoring_calls=0,
        full_response_equality='Referenced from original audit; complete responses are not included in this package'),
        ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
