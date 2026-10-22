"""Same-backbone frozen fact reuse across seven original methods, R2 only."""
import json
import os
import sys
from datetime import datetime
from r2_support_pilot import HERE, PACK, read, write, dump
from r2_program_head import execute, assemble

MODEL={'M0':'llama','M2':'llama','M3':'qwen','M4':'llama','M5':'qwen','M6':'llama','M7':'qwen'}


def run():
    out=HERE/'r2_program_all_methods';out.mkdir(exist_ok=True)
    os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison';sys.path.insert(0,str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    evaluations=read(HERE/'r2_task_scoped_qwen/evaluation.jsonl')
    evaluations=[e for e in evaluations if e['item_id'].startswith('s')]
    assert len(evaluations)==79 and all('R2' in e['evaluation_labels'] for e in evaluations)
    items={r['item']['item_id']:r['item'] for r in read(HERE/'r2_task_scoped_qwen/inputs.jsonl') if r['scope']=='native'}
    baseline={(r['method'],r['item_id']):r for r in read(HERE/'r2_method_analysis/frozen_scores.jsonl')}
    extractions={}; diagonal={}
    for model in ['qwen','llama']:
        source=HERE/('r2_task_scoped_'+model)
        assert json.loads((source/'summary.json').read_text())['status']=='complete'
        extractions[model]={r['item_id']:r for r in read(source/'extractions.jsonl') if r['scope']=='native'}
        assert len(extractions[model])==55
        diagonal[model]={(r['item_id'],r['method']):r for r in read(source/'scored.jsonl') if r['scope']=='native'}
    rows=[];traces=[];parity=0
    for method,model in MODEL.items():
        for e in evaluations:
            iid=e['item_id'];item=items[iid];base=baseline[method,iid]
            if not base['invalid']:
                check=score(dict(raw_response=json.dumps(dict(answer=base['prediction']))),e,item,{})
                assert check['correct']==base['correct'] and check['invalid']==base['invalid'],(method,iid)
            rows.append(dict(base,policy='baseline',fact_model=model))
            for policy in ['documented','strict']:
                result=base;answer=None;trace=None;extraction=extractions[model].get(iid)
                if extraction and 'facts' in extraction:
                    trace=execute(item,extraction['action'],extraction['facts'],policy)
                    answer=assemble(item,None if base['invalid'] else base['prediction'],trace)
                    if answer is not None:result=score(dict(raw_response=json.dumps(dict(answer=answer))),e,item,{})
                row={**e,**result,'method':method,'policy':policy,'fact_model':model,
                     'route':'program' if extraction else 'original','repaired':result['correct'] and not base['correct'],
                     'harmed':base['correct'] and not result['correct']}
                if method in ['M4','M5']:
                    ref=diagonal[model][iid,'scoped_program' if policy=='documented' else 'scoped_strict']
                    prediction=list(row['prediction']) if isinstance(row['prediction'],tuple) else row['prediction']
                    assert prediction==ref['prediction'] and all(row[k]==ref[k] for k in ['correct','invalid']),(method,iid,policy)
                    parity+=1
                rows.append(row);traces.append(dict(item_id=iid,method=method,policy=policy,fact_model=model,answer=answer,options=trace))
    summary=[]
    for method in MODEL:
        for policy in ['baseline','documented','strict']:
            for group in ['all','none','remaining','M14']:
                rs=[]
                for r in rows:
                    item=items[r['item_id']];multi=item['answer_format']=='multi'
                    none=multi and any(item['options'][k]=='None of the above' for k in r['gold'])
                    if r['method']==method and r['policy']==policy and {'all':True,'none':none,'remaining':multi and not none,'M14':not multi}[group]:rs.append(r)
                summary.append(dict(method=method,policy=policy,group=group,n=len(rs),correct=sum(r['correct'] for r in rs),
                                    invalid=sum(r['invalid'] for r in rs),repairs=sum(r.get('repaired',False) for r in rs),harms=sum(r.get('harmed',False) for r in rs)))
    dump(out/'summary.json',dict(status='complete',created_at=datetime.now().astimezone().isoformat(),new_model_calls=0,
         scope='79 exposed native R2 cases',fact_models=MODEL,diagonal_record_parity=parity,results=summary,
         note='Fixed same-backbone task-scoped facts reused. Original24 uncovered answers stay unchanged for every method. This is offline attachment; only M4/M5 fact extractors were newly run. No other92 cases or R5 evaluated.'))
    write(out/'scored.jsonl',rows);write(out/'traces.jsonl',traces)
    (out/'r2_program_all_methods.py').write_text((HERE/'r2_program_all_methods.py').read_text())
    print(json.dumps([r for r in summary if r['group']=='all'],indent=2))


if __name__=='__main__':run()
