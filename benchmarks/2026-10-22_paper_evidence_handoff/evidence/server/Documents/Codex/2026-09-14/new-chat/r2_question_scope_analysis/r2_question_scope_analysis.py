"""Paired rule-scope analysis reusing exactly the previous seven-method facts."""
import os
import sys
from datetime import datetime
import json
from r2_support_pilot import HERE,PACK,read,write,dump
from r2_program_head import assemble
from r2_evidence_first_head import renal_question,execute_scoped


def run():
    os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison';sys.path.insert(0,str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    out=HERE/'r2_question_scope_analysis';out.mkdir(exist_ok=True)
    source=read(HERE/'r2_program_all_methods/scored.jsonl')
    base={(r['method'],r['item_id']):r for r in source if r['policy']=='baseline'}
    items={r['item']['item_id']:r['item'] for r in read(HERE/'r2_task_scoped_qwen/inputs.jsonl') if r['scope']=='native'}
    facts={model:{r['item_id']:r for r in read(HERE/('r2_task_scoped_'+model)/'extractions.jsonl') if r['scope']=='native'} for model in ['qwen','llama']}
    rows=[];changes=[]
    for r in source:
        if r['policy']!='documented':continue
        method=r['method'];iid=r['item_id'];item=items[iid];b=base[method,iid];ex=facts[r['fact_model']].get(iid)
        result=r;trace=None;answer=None
        if ex and renal_question(item):
            trace=execute_scoped(item,ex['action'],ex['facts']);answer=assemble(item,None if b['invalid'] else b['prediction'],trace)
            result=score(dict(raw_response=json.dumps(dict(answer=answer))),r,item,{}) if answer is not None else b
        row={**r,**result,'policy':'question_scope','repaired':result['correct'] and not b['correct'],'harmed':b['correct'] and not result['correct']}
        rows.append(row)
        pred=list(row['prediction']) if isinstance(row['prediction'],tuple) else row['prediction']
        if pred!=r['prediction']:changes.append(dict(method=method,item_id=iid,old_prediction=r['prediction'],new_prediction=pred,
            old_correct=r['correct'],new_correct=row['correct'],gold=r['gold'],trace=trace))
    assert len(rows)==7*79
    summary=[]
    for method in sorted({r['method'] for r in rows}):
        for group in ['all','none','remaining','M14']:
            rs=[]
            for r in rows:
                item=items[r['item_id']];multi=item['answer_format']=='multi';none=multi and any(item['options'][k]=='None of the above' for k in r['gold'])
                if r['method']==method and {'all':True,'none':none,'remaining':multi and not none,'M14':not multi}[group]:rs.append(r)
            summary.append(dict(method=method,group=group,n=len(rs),correct=sum(r['correct'] for r in rs),invalid=sum(r['invalid'] for r in rs),repairs=sum(r['repaired'] for r in rs),harms=sum(r['harmed'] for r in rs)))
    write(out/'scored.jsonl',rows);write(out/'changes.jsonl',changes)
    dump(out/'summary.json',dict(status='complete',created_at=datetime.now().astimezone().isoformat(),new_model_calls=0,
        scope='same79 exposed R2, same previous extracted facts and initial answers',renal_question_count=sum(renal_question(i) for i in items.values()),results=summary,
        note='All-rules reference is r2_program_all_methods documented policy. Only explicitly renal-function final questions use renal rules; missing rule remains UNKNOWN. No change to patient facts, source rules, initial answers or gold.'))
    (out/'r2_question_scope_analysis.py').write_text((HERE/'r2_question_scope_analysis.py').read_text())
    print(json.dumps(dict(results=[r for r in summary if r['group']=='all'],changes=changes),indent=2))


if __name__=='__main__':run()
