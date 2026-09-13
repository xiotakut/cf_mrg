"""Materialize the frozen v5 selection using the existing native input builder."""
import json, gzip, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
OUT=Path(__file__).resolve().parents[1]
PACK=Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
V5=Path('/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v5_20260910')
V4=V5.parent/'benchmark_r1_r5_v4_20260910'
LEGACY=PACK/'results_r1_r5_m0_m1_20260908'
def read(p):
    if not p.exists(): return []
    op=gzip.open if p.suffix=='.gz' else open
    with op(p,'rt') as f:return [json.loads(l) for l in f if l.strip()]
def write(p,rs):
    with p.open('w') as f:
        for r in rs:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def dump(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
def task(t):
    if '在家' in t:return 'MANAGE'
    if '到诊所' in t:return 'VISIT'
    return 'RESOURCE'
def main():
    assert not (OUT/'plan.json').exists()
    selected=read(V5/'selected_targets.jsonl.gz');targets=defaultdict(list)
    for r in selected: targets[r['unit_id']].append(r)
    units=read(OUT/'source_units.jsonl')
    for u in units:
        ts=targets[u['unit_id']]
        u['labels']=sorted({x for t in ts for x in t['evaluation_labels']})
        u['judgments']=[dict(t,labels=t['evaluation_labels'],scoring_eligible=True,
                            target_id=task(t['target']) if u['resource_id']=='M17' else t.get('target_id')) for t in ts]
        u['review_state']='reviewed';u['review_resolution']='classified';u['missing_image_input']=False
    # Seed with all earlier native inputs so unchanged inputs retain IDs and seeds.
    pool={}
    for p in [PACK/'results_cf_full_comparison/screening_items.jsonl',LEGACY/'items.jsonl',PACK/'results_r1_r4_m0_m1_20260908/items.jsonl']:
        for r in read(p):
            if r['item_id'] in pool:assert pool[r['item_id']]==r
            pool[r['item_id']]=r
    old_evals=defaultdict(list)
    for e in read(LEGACY/'evaluation.jsonl'):old_evals[e['unit_id']].append(e)
    recovery={r['original_question']:r for r in read(V4/'sources/M14/exact_question_recovery.jsonl')}
    src=(LEGACY/'code/prepare_benchmark.py').read_text()
    src=src.replace("units = read(COLLECTION / '分析子集.jsonl')",'units = selected_units')
    src=src.replace("assert len(units) == 28243",'assert len(units) == 6104')
    src=src.replace('import pyarrow.parquet as pq','')
    a=src.index('    medqa = defaultdict(list)');b=src.index('    m22roots = {}',a)
    src=src[:a]+src[b:]
    src=src.replace("old_items = {r['item_id']: r for r in read(OLD / 'screening_items.jsonl')}", 'old_items = prior_pool')
    src=src.replace('next_id = 100000','next_id = 200000')
    a=src.index('                matches = medqa.get(q1, [])');b=src.index('            else:\n                q1, q2',a)
    src=src[:a]+'''                match = recovered[q1]; opts=match['options']; gold=match['gold']
                recoveries.append(dict(unit_id=u['unit_id'], **match))
'''+src[b:]
    # Qualification is already frozen per target; do not reclassify with regexes.
    src=src.replace('def image_reason(text):','def unused_image_reason(text):')
    src=src.replace('    items, labels, coverage, recoveries = {}, [], [], []','    items, labels, coverage, recoveries = {}, [], [], []')
    # Preserve the exact earlier MedRGB context materialization where it exists.
    needle="        elif rid == 'M22':\n            root = m22roots"
    replacement="""        elif rid == 'M22' and u['unit_id'] in prior_evaluations:
            for e in prior_evaluations[u['unit_id']]:
                items[e['item_id']]=prior_pool[e['item_id']]
                labels.append(dict(e, labels=u['labels'], scoring_eligible=True, scoring_exclusion=None))
        elif rid == 'M22':
            root = m22roots"""
    assert needle in src;src=src.replace(needle,replacement)
    # Only selected native MedPerturb targets, including independently qualified RESOURCE.
    src=src.replace("                        gold = r['gold_standard_' + target.lower()].strip().lower()", "                        if target not in {j['target_id'] for j in u['judgments']}: continue\n                        gold = r['gold_standard_' + target.lower()].strip().lower()")
    ns={'__name__':'v5_native_builder','selected_units':units,'prior_pool':pool,'prior_evaluations':old_evals,'recovered':recovery,'image_reason':lambda text:None}
    exec(compile(src,str(OUT/'code/native_builder.py'),'exec'),ns)
    ns['OUT']=OUT
    (OUT/'code/native_builder.py').write_text(src)
    ns['prepare']()
    items=read(OUT/'items.jsonl'); evaluation=read(OUT/'evaluation.jsonl')
    for e in evaluation:
        ts=targets[e['unit_id']]
        if e['resource_id']=='M17':ts=[t for t in ts if task(t['target'])==e['task']]
        if e['resource_id']=='M22' and e['role']!='reference':
            present={d['native_id'] for d in e['document_map'].values() if d['is_cf']}
            ts=[t for t in ts if t['judgment_id'].rsplit(':',1)[-1] in present]
        e['judgment_ids']=[t['judgment_id'] for t in ts]
        e['evaluation_labels']=sorted({l for t in ts for l in t['evaluation_labels']})
        e['labels']=e['evaluation_labels']
        assert e['scoring_eligible'] and e['gold'] is not None
    assert {e['unit_id'] for e in evaluation}==set(targets)
    assert {j for e in evaluation for j in e['judgment_ids']}=={t['judgment_id'] for t in selected}
    write(OUT/'evaluation.jsonl',evaluation);write(OUT/'units.jsonl',read(V5/'units.jsonl'))
    visible=['question','options','fixed_evidence','answer_format']
    needed={r['item_id']:r for r in items};cached={}
    paths=[PACK/'results_cf_full_comparison/predictions.jsonl',PACK/'results_r1_r4_m0_m1_20260908/predictions.jsonl',PACK/'results_r1_r5_v3_m2_20260909/m2_predictions.jsonl',LEGACY/'cache/reused.jsonl',*sorted((LEGACY/'cache').glob('worker-*/predictions.jsonl'))]
    for p in paths:
        for r in read(p):
            iid=r['item_id'];m=r['method']
            if iid not in needed or m not in ['direct_llama','medrgag_llama_base']:continue
            assert all(needed[iid][k]==pool[iid][k] for k in visible)
            assert list(needed[iid]['options'].items())==list(pool[iid]['options'].items())
            assert needed[iid].get('max_tokens',64)==pool[iid].get('max_tokens',64)
            key=(iid,m)
            if key in cached:assert cached[key]['raw_response']==r['raw_response']
            else:cached[key]=dict(r,reused_from=str(p))
    write(OUT/'cache/reused.jsonl',cached.values())
    for m,name in [('M0','direct_llama'),('M2','medrgag_llama_base')]:
        write(OUT/f'pending_{m}.jsonl',[r for r in items if (r['item_id'],name) not in cached])
    counts=Counter(r['method'] for r in cached.values())
    plan=dict(status='prepared',methods=['M0','M2','M4','M5'],benchmark=str(V5),units=len(units),selected_judgments=len(selected),unique_inputs=len(items),evaluation_records_per_method=len(evaluation),reused_predictions=dict(counts),pending={m:len(items)-counts[name] for m,name in [('M0','direct_llama'),('M2','medrgag_llama_base'),('M4','medrag_llama31'),('M5','medrag_qwen3')]},answer_formats=dict(Counter(r['answer_format'] for r in items)),per_source=dict(Counter(e['resource_id'] for e in evaluation)),supplemental_runs=[])
    dump(OUT/'plan.json',plan);print(json.dumps(plan,indent=2))
if __name__=='__main__':main()
