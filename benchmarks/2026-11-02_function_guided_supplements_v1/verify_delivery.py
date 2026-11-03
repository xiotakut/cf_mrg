"""Stdlib-only replay of the additionally delivered E3/E5 evidence."""
import argparse, ast, collections, csv, gzip, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def rows(name):
    p=ROOT/name;opener=gzip.open if p.suffix=='.gz' else open
    with opener(p,'rt',encoding='utf-8') as f:
        return list(csv.DictReader(f)) if '.csv' in p.name else [json.loads(l) for l in f if l.strip()]
def near(a,b):assert math.isclose(float(a),float(b),abs_tol=1e-8,rel_tol=0),(a,b)
def groups(data,keys):
    result=collections.defaultdict(list)
    for row in data:result[tuple(row[k] for k in keys)].append(row)
    return result
def truth(x):return x is True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--with-intervals',action='store_true',help='Also reproduce E3 profile bootstrap intervals; requires numpy.')
    args=parser.parse_args()
    checked=collections.Counter()
    support=rows('e3/replay_inputs/support_scores.jsonl.gz')
    grouped=groups(support,['method','arm'])
    views={(r['method'],r['arm'],r['request_id']):r for r in rows('e3/replay_inputs/support_views.jsonl.gz')}
    baseline={(r['method'],r['request_id']):r for r in support if r['arm']=='strong_B'}
    for row in rows('e3/support_operation_controls.csv'):
        data=grouped[row['method'],row['arm']]
        assert len(data)==int(row['inputs'])==123
        assert sum(r['correct'] is True for r in data)==int(row['correct'])
        assert sum(r['correct'] is False for r in data)==int(row['incorrect'])
        assert sum(r['correct'] is None for r in data)==int(row['unavailable'])
        if row['arm']!='strong_B':
            current=[views[r['method'],r['arm'],r['request_id']] for r in data]
            assert sum(x['applicable'] for x in current)==int(float(row['applicable']))
            assert sum(x['answer_changed'] for x in current)==int(row['changed'])
        repair=sum(truth(r['correct']) and not truth(baseline[r['method'],r['request_id']]['correct']) for r in data)
        harm=sum(not truth(r['correct']) and truth(baseline[r['method'],r['request_id']]['correct']) for r in data)
        assert repair==int(row['repair']) and harm==int(row['harm'])
        checked['support_main']+=1
    for row in rows('e3/support_controls_by_function.csv'):
        data=[r for r in grouped[row['method'],row['arm']] if row['category']=='ALL' or row['category'] in r['evaluation_labels']]
        assert len(data)==int(row['inputs'])
        assert sum(r['correct'] is True for r in data)==int(row['correct'])
        near(sum(truth(r['correct']) for r in data)/len(data),row['accuracy'])
        checked['support_function']+=1

    candidate=groups(rows('e3/replay_inputs/candidate_scores.jsonl.gz'),['method','variant'])
    for row in rows('e3/candidate_controls_680.csv'):
        data=candidate[row['method'],row['variant']]
        assert len(data)==int(row['n'])==680
        assert sum(truth(r['correct']) for r in data)==int(row['correct'])
        assert sum(truth(r['invalid']) for r in data)==int(row['invalid'])
        classes=groups(data,['gold'])
        recall=sum(sum(truth(r['correct']) for r in g)/len(g) for g in classes.values())/len(classes)
        near(recall,row['macro_recall']);checked['candidate']+=1

    consequence=groups(rows('e3/replay_inputs/consequence_scores.jsonl.gz'),['method','arm'])
    for row in rows('e3/consequence_controls_288.csv'):
        data=consequence[row['method'],row['arm']]
        assert len(data)==int(row['n'])==288
        for k in ['correct','invalid','joint_numeric_correct','all_outputs_correct']:
            assert sum(truth(r[k]) for r in data)==int(row[k]),(k,row)
        assert dict(collections.Counter(r['route'] for r in data))==ast.literal_eval(row['routes'])
        checked['consequence']+=1
    for row in rows('e3/consequence_profile_intervals.csv'):
        left={(r['item_id'],r['profile']):r for r in consequence[row['method'],'patch']}
        right={(r['item_id'],r['profile']):r for r in consequence[row['method'],row['control']]}
        assert left.keys()==right.keys()
        deltas={key:int(left[key][row['metric']])-int(right[key][row['metric']]) for key in left}
        near(sum(deltas.values())/len(deltas),row['delta'])
        assert sum(v>0 for v in deltas.values())==int(row['repair'])
        assert sum(v<0 for v in deltas.values())==int(row['harm'])
        profile=collections.defaultdict(list)
        for (_,name),value in deltas.items():profile[name].append(value)
        assert len(profile)==int(row['profiles'])==24
        if args.with_intervals:
            import numpy as np
            v=np.array([sum(profile[k])/len(profile[k]) for k in sorted(profile)])
            rng=np.random.default_rng(20261102)
            lo,hi=np.quantile(v[rng.integers(len(v),size=(2000,len(v)))].mean(1),[.025,.975])
            near(lo,row['ci95_low']);near(hi,row['ci95_high'])
        checked['consequence_paired_intervals' if args.with_intervals else 'consequence_paired_points']+=1

    invariance=rows('e3/replay_inputs/invariance_scores.jsonl.gz')
    def both_summary(data):
        task=lambda r:'robustness' if r['task'].startswith('robustness_') else r['task']
        refs={(r['unit_id'],task(r)):r for r in data if r['role']=='reference'}
        nonref=groups([r for r in data if r['role']!='reference'],['unit_id'])
        values=[sum(truth(refs[r['unit_id'],task(r)]['correct']) and truth(r['correct']) for r in g)/len(g) for g in nonref.values()]
        return len(nonref),100*sum(values)/len(values)
    for row in rows('e3/invariance_matched_controls.csv'):
        subset=[r for r in invariance if r['method']==row['method'] and
            ((row['stage']=='all' and 'R5' in r['evaluation_labels']) or
             (row['stage']!='all' and r['stage']==row['stage'] and r['cohort']==row['cohort']))]
        arms=groups(subset,['arm'])
        names=['draw'+str(i) for i in range(5)] if row['control']=='single_mean' else [row['control']]
        controlsets=[arms[name,] for name in names]
        ids={r['record_id'] for r in controlsets[0]}
        head=[r for r in arms['combined_head',] if r['record_id'] in ids]
        assert len(head)==int(row['mappings'])
        n,h=both_summary(head);assert n==int(row['units'])
        b=sum(both_summary(data)[1] for data in controlsets)/len(controlsets)
        near(h,row['head_both_pct']);near(b,row['control_both_pct']);near(h-b,row['difference_pp'])
        if row['repairs']:
            hmap={r['record_id']:truth(r['correct']) for r in head}
            assert sum(hmap[r['record_id']] and not truth(r['correct']) for r in controlsets[0])==int(float(row['repairs']))
            assert sum(not hmap[r['record_id']] and truth(r['correct']) for r in controlsets[0])==int(float(row['harms']))
        checked['invariance']+=1

    coverage=rows('e3/replay_inputs/role_coverage.jsonl.gz')
    assert len(coverage)==27810
    assert len({(x['method'],x['request_id']) for x in coverage})==27810
    fields=['method','role','tool_applicable','execution_mode','execution_status','native_available','shared_origin']
    counts=collections.Counter();categorical=collections.Counter()
    for x in coverage:
        for role,v in x['roles'].items():
            item=dict(v,method=x['method'],role=role)
            key=tuple(str(item[k]) for k in fields);counts[key]+=1
            for label in x['evaluation_labels']:categorical[(label,)+key]+=1
    for name,count,keys in [('role_coverage_all_inputs',counts,fields),
                            ('role_coverage_by_function_nonreference',categorical,['category']+fields)]:
        saved={tuple(row[k] for k in keys):int(row['inputs']) for row in rows('e3/'+name+'.csv')}
        assert dict(count)==saved,name
        checked[name]=len(saved)

    candidates=rows('e5/exposure/candidate_fingerprints.jsonl.gz')
    qs=collections.defaultdict(set);ps=collections.defaultdict(set)
    for x in candidates:
        qs[x['question_sha256']].add(x['unit_id'])
        if x['premise_sha256']:ps[x['premise_sha256']].add(x['unit_id'])
    assert len({x['unit_id'] for x in candidates})==128
    scan=rows('e5/exposure/exposure_scan.jsonl')
    fingerprints=rows('e5/exposure/scanned_fingerprints.jsonl.gz')
    assert len(scan)==len(fingerprints)==111
    excluded=set();prepared=set()
    for i,(saved,current) in enumerate(zip(scan,fingerprints)):
        assert current['scan_index']==i and current['path']==saved['path']
        assert current['source_sha256']==saved['sha256']
        if saved.get('status')=='unsupported_json_container':continue
        overlap=set()
        for q in current['question_sha256']:overlap.update(qs.get(q,set()))
        for p in current['premise_sha256']:overlap.update(ps.get(p,set()))
        assert sorted(overlap)==saved['overlap_units']
        assert current['input_rows']==saved['input_rows']
        if current['exposure_kind']=='other_working_input_exclusion':excluded.update(overlap)
        else:prepared.update(overlap)
    selected={x['unit_id'] for x in rows('e5/offline/families.jsonl')}
    assert len(selected)==32 and not excluded&selected
    checked['E5_scan_records']=len(scan)

    e2=json.loads((ROOT/'e2/MANIFEST.json').read_text())
    for name,info in e2['files'].items():
        p=ROOT/'e2'/name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==info['sha256']
        assert p.stat().st_size==info['bytes']
    audit=rows('e2/e2_lite_audit_results.jsonl');assert len(audit)==120
    assert len(rows('aggregation/illustrative_saved_examples.jsonl'))==3
    print(json.dumps(dict(status='passed',table_rows_checked=dict(checked),E2_targets=len(audit),
        E5_excluded_units=len(excluded),E5_preparation_only_overlap_units=len(prepared),
        E5_selected_overlap_units=len(excluded&selected),new_model_requests=0,new_native_scores=0,
        scope='Replay saved metrics, role coverage and bounded fingerprint matches; no clinical reference adjudication.'),
        ensure_ascii=False,indent=2))

if __name__=='__main__':main()
