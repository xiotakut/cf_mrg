"""Strict native scoring, category membership, equal-unit and equal-source summaries."""
import argparse,csv,json,os,sys
from pathlib import Path
from itertools import combinations
from collections import Counter,defaultdict
from statistics import mean
from prepare_v5 import OUT,PACK,read,write,dump
os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison'
sys.path.insert(0,str(PACK/'scripts'))
from analyze_cf_baseline_screening import score,norm
METHODS=dict(M3='marag_intrinsic_qwen3_8b')
RESULTS=OUT
def objects(raw,key):
    decoder=json.JSONDecoder();values=[];pos=0
    while pos<len(raw):
        start=raw.find('{',pos)
        if start<0:break
        try:
            value,size=decoder.raw_decode(raw[start:]);pos=start+size
            if isinstance(value,dict) and key in value:values.append(value)
        except json.JSONDecodeError:pos=start+1
    if not values or any(x[key]!=values[0][key] for x in values[1:]):return None
    return values[0]
def table(name,rows):
    if not rows:return
    with (RESULTS/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def main():
    global METHODS,RESULTS
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');p.add_argument('--methods',nargs='+',choices=list(METHODS),default=list(METHODS));p.add_argument('--output-dir',type=Path,default=OUT);a=p.parse_args()
    METHODS={m:METHODS[m] for m in a.methods};RESULTS=a.output_dir;RESULTS.mkdir(parents=True,exist_ok=True)
    items={r['item_id']:r for r in read(OUT/'items.jsonl')};evaluations=read(OUT/'evaluation.jsonl');preds={}
    for path in [OUT/'cache/reused.jsonl',*[OUT/m/'predictions.jsonl' for m in METHODS]]:
        for r in read(path):
            key=r['item_id'],r['method'];assert key not in preds,('duplicate',key)
            assert key[0] in items and key[1] in METHODS.values();preds[key]=r
    missing={m:sum((iid,name) not in preds for iid in items) for m,name in METHODS.items()}
    if not a.partial:assert not any(missing.values()),missing
    canonical={norm(s):s for s in json.loads((PACK/'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    scored=[];detection=[]
    for e in evaluations:
        item=items[e['item_id']]
        for m,name in METHODS.items():
            raw=preds.get((e['item_id'],name))
            if raw is None:continue
            key='answer_choice' if m in ['M4','M5'] else 'answer'
            obj=objects(raw['raw_response'],key)
            if m in ['M4','M5'] or item['answer_format'].startswith('robustness'):
                native=dict(raw,raw_response=json.dumps({'answer':obj[key]}) if obj else '')
            else:native=raw
            native_item=dict(item,answer_format='single') if item['answer_format']=='robustness_single' else item
            result=score(native,e,native_item,canonical)
            scored.append(dict(e,method=m,answer_format=item['answer_format'],**result))
            if item['answer_format']=='robustness_single':
                errors=obj.get('errors') if obj else None
                valid=isinstance(errors,list) and all(isinstance(x,dict) and isinstance(x.get('document_id'),str) and isinstance(x.get('correction'),str) for x in errors)
                guessed=[x['document_id'] for x in errors] if valid else []
                valid=valid and len(guessed)==len(set(guessed)) and set(guessed)<=set(e['document_map'])
                excluded=set(e['incomplete_document_ids'])
                gold=set(e['error_document_ids'])-excluded;guess=set(guessed)-excluded if valid else set()
                detection.append(dict(record_id=e['record_id'],unit_id=e['unit_id'],method=m,p_sig=e['p_sig'],valid=valid,exact=valid and guess==gold,tp=len(guess&gold),fp=len(guess-gold),fn=len(gold-guess),correction_semantic_score=None))
    write(RESULTS/'predictions.jsonl',preds.values());write(RESULTS/'scored.jsonl',scored);write(RESULTS/'document_detection.jsonl',detection)
    buckets=defaultdict(list)
    for r in scored:
        if r['role']=='reference':continue
        for category in ['ALL',*r['evaluation_labels']]:buckets[r['unit_id'],category,r['method']].append(r)
    # A unit contributes its mean native task score, regardless of task/ratio count.
    units=[]
    for (uid,cat,m),rs in sorted(buckets.items()):
        units.append(dict(unit_id=uid,resource_id=rs[0]['resource_id'],group_id=rs[0]['group_id'],category=cat,method=m,native_records=len(rs),score=mean(int(r['correct']) for r in rs),all_tasks_pass=all(r['correct'] for r in rs),invalid_records=sum(r['invalid'] for r in rs)))
    table('unit_scores.csv',units)
    summary=[]
    for cat in ['R1','R2','R3','R4','R5','ALL']:
        row=dict(category=cat)
        for m in METHODS:
            rs=[r for r in units if r['category']==cat and r['method']==m];by_source=defaultdict(list)
            for r in rs:by_source[r['resource_id']].append(r['score'])
            row.update({m+'_units':len(rs),m+'_pct':100*mean(r['score'] for r in rs) if rs else None,m+'_all_tasks_pass_pct':100*mean(r['all_tasks_pass'] for r in rs) if rs else None,m+'_source_macro_pct':100*mean(mean(v) for v in by_source.values()) if rs else None})
        summary.append(row)
    table('category_scores.csv',summary)
    sources=[]
    for rid in sorted({r['resource_id'] for r in scored}):
        for m in METHODS:
            rs=[r for r in units if r['resource_id']==rid and r['method']==m and r['category']=='ALL']
            if rs:sources.append(dict(resource_id=rid,method=m,units=len(rs),pct=100*mean(r['score'] for r in rs),all_tasks_pass_pct=100*mean(r['all_tasks_pass'] for r in rs)))
    table('source_scores.csv',sources)
    tasks=[]
    task_buckets=defaultdict(list)
    for r in scored:task_buckets[r['resource_id'],r['task'],r['role'],r['method']].append(r)
    for (rid,task,role,m),rs in sorted(task_buckets.items()):
        tasks.append(dict(resource_id=rid,task=task,role=role,method=m,records=len(rs),correct=sum(r['correct'] for r in rs),accuracy=mean(int(r['correct']) for r in rs),invalid=sum(r['invalid'] for r in rs)))
    table('source_task_scores.csv',tasks)

    refs={(r['unit_id'],'robustness' if r['task'].startswith('robustness_') else r['task'],r['method']):r for r in scored if r['role']=='reference'}
    pairs=[]
    for r in scored:
        if r['role']=='reference' or 'R5' not in r['evaluation_labels']:continue
        ref=refs.get((r['unit_id'],'robustness' if r['task'].startswith('robustness_') else r['task'],r['method']))
        if ref is None:continue
        pairs.append(dict(unit_id=r['unit_id'],resource_id=r['resource_id'],group_id=r['group_id'],method=r['method'],task=r['task'],reference_correct=ref['correct'],variant_correct=r['correct'],both_correct=ref['correct'] and r['correct'],answer_invariant=not ref['invalid'] and not r['invalid'] and ref['semantic_prediction']==r['semantic_prediction']))
    write(RESULTS/'r5_pairs.jsonl',pairs)
    pair_summary=[]
    for m in METHODS:
        grouped=defaultdict(list)
        for r in pairs:
            if r['method']==m:grouped[r['unit_id']].append(r)
        if grouped:pair_summary.append(dict(method=m,units=len(grouped),answer_invariant_pct=100*mean(mean(int(r['answer_invariant']) for r in rs) for rs in grouped.values()),both_correct_pct=100*mean(mean(int(r['both_correct']) for r in rs) for rs in grouped.values())))
    table('r5_pair_summary.csv',pair_summary)
    validation=dict(status='partial' if any(missing.values()) else 'complete',unique_inputs=len(items),units=6104,selected_judgments=13000,evaluation_records_per_method=len(evaluations),missing_predictions=missing,predictions=len(preds),scored_records=len(scored),duplicate_predictions=0)
    dump(RESULTS/'validation.json',validation);print(json.dumps(validation,indent=2))
    if not a.partial:
        import numpy as np
        paired={(r['unit_id'],r['category'],r['method']):r for r in units}
        contrasts=[]
        for category in ['R1','R2','R3','R4','R5','ALL']:
            for baseline,method in combinations(METHODS,2):
                groups=defaultdict(list)
                for r in units:
                    if r['category']==category and r['method']==method:
                        groups[r['group_id']].append(r['score']-paired[r['unit_id'],category,baseline]['score'])
                sums=np.array([sum(v) for v in groups.values()]);counts=np.array([len(v) for v in groups.values()]);rng=np.random.default_rng(20260911)
                boot=[]
                for _ in range(2000):
                    sample=rng.integers(0,len(sums),len(sums));boot.append(sums[sample].sum()/counts[sample].sum())
                lo,hi=np.quantile(boot,[.025,.975])
                contrasts.append(dict(category=category,baseline=baseline,method=method,source_groups=len(groups),unit_count=int(counts.sum()),difference_pp=100*sums.sum()/counts.sum(),ci_low_pp=100*lo,ci_high_pp=100*hi,bootstrap='source-root cluster resampling, 2000, seed 20260911'))
        table('paired_method_comparisons.csv',contrasts)
        assert len(scored)==len(evaluations)*len(METHODS)
        expected=[2866,79,733,13,3600,6104]
        for row,n in zip(summary,expected):
            for m in METHODS:assert row[m+'_units']==n
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(11,5));width=.19
        for j,m in enumerate(METHODS):ax.bar([i+(j-(len(METHODS)-1)/2)*width for i in range(6)],[r[m+'_pct'] for r in summary],width,label=m)
        ax.set(xticks=range(6),xticklabels=[r['category'] for r in summary],ylabel='Unit-mean native accuracy (%)',ylim=(0,100),title='V5 R1–R5 · 6,104 units · overlapping categories');ax.legend();fig.tight_layout()
        stem='v5_four_methods' if len(METHODS)==4 else 'v5_selected_methods'
        for ext in ['png','pdf','svg']:fig.savefig(RESULTS/f'{stem}.{ext}',dpi=180)
if __name__=='__main__':main()
