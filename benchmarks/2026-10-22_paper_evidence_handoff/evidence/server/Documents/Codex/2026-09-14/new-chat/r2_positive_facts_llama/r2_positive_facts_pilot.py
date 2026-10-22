"""Only regenerate requests changed by the positive-field representation."""
import argparse
from collections import Counter
from datetime import datetime
import json
import os
import sys
from r2_support_pilot import HERE,PACK,read,write,dump
from r2_task_scoped_head import build_request as previous_request
from r2_positive_facts import build_request,clean_extraction,check
from r2_action_scope import execute_scoped
from r2_program_head import eligible,assemble
from r2_interface_pilot import run


def prepare(model):
    out=HERE/('r2_positive_facts_'+model);out.mkdir(exist_ok=True);assert not (out/'config.json').exists();check()
    original=HERE/('r2_task_scoped_'+model);scope=HERE/('r2_scope_holdout_'+model)
    inputs=[dict(r,scope='native' if r['scope']=='native' else 'rule_probe') for r in read(original/'inputs.jsonl')]
    inputs.extend(dict(item=r['item'],scope='scope_probe') for r in read(scope/'inputs.jsonl'))
    old={r['item_id']:r for r in read(original/'raw_predictions.jsonl') if r['review']=='facts'}
    old.update({r['item_id']:r for r in read(scope/'raw_predictions.jsonl') if r['review']=='previous'})
    jobs=[];reuse=[]
    for d in inputs:
        item=d['item']
        if d['scope']=='native' and not eligible(item):continue
        req=build_request(item)
        if req==previous_request(item):reuse.append(dict(old[item['item_id']],scope=d['scope'],provenance='previous_short_prompt_exact_reuse'))
        else:jobs.append(dict(item_id=item['item_id'],review='positive_facts',**req))
    write(out/'inputs.jsonl',inputs);write(out/'requests.jsonl',jobs);write(out/'reused_predictions.jsonl',reuse)
    write(out/'evaluation.jsonl',[r for r in read(original/'evaluation.jsonl') if r['item_id'] in {d['item']['item_id'] for d in inputs}]+read(scope/'evaluation.jsonl'))
    cfg=json.loads((scope/'recovery_memory/config.json').read_text());cfg['gpu_memory_utilization']=.75;dump(out/'config.json',cfg)
    dump(out/'plan.json',dict(status='prepared',created_at=datetime.now().astimezone().isoformat(),model=model,new_calls=len(jobs),exact_reused_calls=len(reuse),physical_gpu=3,
        changed_by_scope=dict(Counter(d['scope'] for d in inputs if d['item']['item_id'] in {r['item_id'] for r in jobs})),note='Only two negative Boolean extraction fields are renamed positively and complemented back for the same71 rules. UNKNOWN stays UNKNOWN. Same original weights/short prompt/evidence order/temperature0/2048 budget. Native79, already exposed96 rule probes and48 scope probes; no new independent dataset. Regenerate only changed requests, reuse exact unchanged requests. Default standalone API unchanged pending results.'))
    assert len(jobs)+len(reuse)==199
    for name in ['r2_positive_facts.py','r2_positive_facts_pilot.py','r2_task_scoped_head.py','r2_action_scope.py','r2_program_head.py','r2_guideline_rules.py','r2_interface_pilot.py','r2_indexed_head.py']:(out/name).write_text((HERE/name).read_text())
    print(json.dumps(json.loads((out/'plan.json').read_text()),indent=2))


def score_results(model):
    out=HERE/('r2_positive_facts_'+model);os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison';sys.path.insert(0,str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    inputs={r['item']['item_id']:r for r in read(out/'inputs.jsonl')}
    raw=read(out/'gpu3/predictions.jsonl');reused=read(out/'reused_predictions.jsonl');lookup={r['item_id']:r for r in raw+reused};assert len(lookup)==len(raw)+len(reused)==199
    base={r['item_id']:r for r in read(HERE/'r2_program_all_methods/scored.jsonl') if r['policy']=='baseline' and r['method']==('M5' if model=='qwen' else 'M4')}
    proofs={r['item_id']:r for r in read(HERE/'r2_rule_holdout/proofs.jsonl')+read(HERE/'r2_scope_holdout/proofs.jsonl')};rows=[];extractions=[]
    for e in read(out/'evaluation.jsonl'):
        iid=e['item_id'];d=inputs[iid];item=d['item'];old=base.get(iid);result=old;answer=trace=None;error=None
        if iid in lookup:
            try:
                action,facts,errors=clean_extraction(item,json.loads(lookup[iid]['raw_response']))
                mismatch={k:dict(expected=v,prediction=facts[k]) for k,v in proofs.get(iid,{}).get('current',{}).items() if k in facts and facts[k]!=v}
                extractions.append(dict(item_id=iid,scope=d['scope'],action=action,facts=facts,evidence_errors=errors,oracle_mismatches=mismatch))
                trace=execute_scoped(item,action,facts);answer=assemble(item,None if old is None or old['invalid'] else old['prediction'],trace)
            except (ValueError,KeyError,TypeError) as exc:error=f'{type(exc).__name__}: {exc}';extractions.append(dict(item_id=iid,scope=d['scope'],error=error))
            if answer is not None:result=score(dict(raw_response=json.dumps(dict(answer=answer))),e,item,{})
        if result is None:result=score(dict(raw_response=''),e,item,{})
        rows.append({**e,**result,'scope':d['scope'],'options_trace':trace,'extraction_error':error})
    summary=[]
    for scope in ['native','rule_probe','scope_probe']:
        for group in ['all','none','remaining','M14']:
            rs=[]
            for r in rows:
                item=inputs[r['item_id']]['item'];multi=item['answer_format']=='multi';none=multi and any(item['options'][k]=='None of the above' for k in r['gold'])
                if r['scope']==scope and {'all':True,'none':none,'remaining':multi and not none,'M14':not multi}[group]:rs.append(r)
            if rs:summary.append(dict(scope=scope,group=group,n=len(rs),correct=sum(r['correct'] for r in rs),invalid=sum(r['invalid'] for r in rs)))
    costs=dict(calls=len(raw),input_tokens=sum(r['prompt_tokens'] for r in raw),output_tokens=sum(r['completion_tokens'] for r in raw),length_stops=sum(r['finish_reason']=='length' for r in raw))
    diag=[dict(scope=scope,parse_errors=sum('error' in r for r in rs),evidence_rejections=sum(len(r.get('evidence_errors',[])) for r in rs),mismatch_fields=dict(Counter(k for r in rs for k in r.get('oracle_mismatches',{})))) for scope in ['native','rule_probe','scope_probe'] for rs in [[r for r in extractions if r['scope']==scope]]]
    write(out/'raw_predictions.jsonl',raw);write(out/'scored.jsonl',rows);write(out/'extractions.jsonl',extractions)
    runtime=json.loads((out/'gpu3/runtime.json').read_text());assert runtime['status']=='complete'
    dump(out/'summary.json',dict(status='complete',results=summary,costs=costs,reused_calls=len(reused),diagnostics=diag,runtime=runtime));print(json.dumps(dict(results=summary,diagnostics=diag),indent=2))


def analyze():
    """Own-backbone attachment after both runs; all seven initial methods."""
    os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison';sys.path.insert(0,str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    from r2_program_all_methods import MODEL
    from r2_decision_policy import choose
    items={r['item']['item_id']:r['item'] for r in read(HERE/'r2_positive_facts_qwen/inputs.jsonl') if r['scope']=='native'}
    facts={m:{r['item_id']:r for r in read(HERE/('r2_positive_facts_'+m)/'extractions.jsonl') if r['scope']=='native'} for m in ['qwen','llama']}
    old={(r['method'],r['item_id']):r for r in read(HERE/'r2_question_scope_analysis/scored.jsonl')}
    bases=[r for r in read(HERE/'r2_program_all_methods/scored.jsonl') if r['policy']=='baseline'];rows=[];changes=[]
    for b in bases:
        method=b['method'];iid=b['item_id'];item=items[iid];ex=facts[MODEL[method]].get(iid);trace=execute_scoped(item,ex['action'],ex['facts']) if ex and 'facts' in ex else None
        for policy in ['inherit_unknown','support_only']:
            result=b
            if trace is not None:
                answer=choose(item,None if b['invalid'] else b['prediction'],trace,policy)
                if answer is not None:result=score(dict(raw_response=json.dumps(dict(answer=answer))),b,item,{})
            row={**b,**result,'policy':policy,'repaired':result['correct'] and not b['correct'],'harmed':b['correct'] and not result['correct']};rows.append(row)
            pred=list(result['prediction']) if isinstance(result['prediction'],tuple) else result['prediction'];ref=old[method,iid]
            if policy=='inherit_unknown' and pred!=ref['prediction']:changes.append(dict(method=method,item_id=iid,old_prediction=ref['prediction'],new_prediction=pred,old_correct=ref['correct'],new_correct=result['correct']))
    summary=[]
    for method in sorted(MODEL):
        for policy in ['inherit_unknown','support_only']:
            for group in ['all','none','remaining','M14']:
                rs=[]
                for r in rows:
                    item=items[r['item_id']];multi=item['answer_format']=='multi';none=multi and any(item['options'][k]=='None of the above' for k in r['gold'])
                    if r['method']==method and r['policy']==policy and {'all':True,'none':none,'remaining':multi and not none,'M14':not multi}[group]:rs.append(r)
                summary.append(dict(method=method,policy=policy,group=group,n=len(rs),correct=sum(r['correct'] for r in rs),invalid=sum(r['invalid'] for r in rs),repairs=sum(r['repaired'] for r in rs),harms=sum(r['harmed'] for r in rs)))
    out=HERE/'r2_question_scope_analysis';write(out/'positive_facts_scored.jsonl',rows)
    write(out/'positive_facts_changes.jsonl',changes)
    dump(out/'positive_facts_summary.json',dict(status='complete',new_model_calls=0,results=summary,changed_predictions=len(changes),note='Same original seven-method answers, finite rules and scope; positive-field factual outputs from each own backbone. inherit_unknown and support_only shown as fixed policies; no per-method best-of selection. Native development79 only.'))
    costs=[]
    for model in ['qwen','llama']:
        root=HERE/('r2_positive_facts_'+model);r=json.loads((root/'summary.json').read_text());assert r['status']=='complete'
        costs.append(dict(model=model,**r['costs'],reused_calls=r['reused_calls'],worker_seconds=r['runtime']['elapsed_seconds'],initialization_seconds=r['runtime']['initialization_seconds']))
    costreport=dict(status='complete',runs=costs,calls=sum(r['calls'] for r in costs),input_tokens=sum(r['input_tokens'] for r in costs),output_tokens=sum(r['output_tokens'] for r in costs),length_stops=sum(r['length_stops'] for r in costs),note='New142=54 native +24 old-rule-probe +64 exposed-scope-probe. Reused256 exact old requests; no extra generation for seven-method comparison.')
    deployment=[]
    for model in ['qwen','llama']:
        root=HERE/('r2_positive_facts_'+model);rs=[r for r in read(root/'raw_predictions.jsonl')+read(root/'reused_predictions.jsonl') if r['item_id'] in items]
        assert len(rs)==55
        deployment.append(dict(model=model,native_inputs=79,added_calls=55,input_tokens=sum(r['prompt_tokens'] for r in rs),output_tokens=sum(r['completion_tokens'] for r in rs)))
    costreport['selected_head_native']=deployment
    prior=json.loads((HERE/'r2_method_analysis/evidence_scope_series_costs.json').read_text())
    costreport['combined_with_evidence_scope']=dict(calls=prior['calls']+costreport['calls'],input_tokens=prior['input_tokens']+costreport['input_tokens'],output_tokens=prior['output_tokens']+costreport['output_tokens'],length_stops=prior['length_stops']+costreport['length_stops'],successful_worker_seconds=prior['successful_worker_seconds']+sum(r['worker_seconds'] for r in costs),failed_initializations=5,note='796 evidence/scope plus142 positive-field calls; existing outputs counted once. Successful worker time excludes five recorded failed initializations.')
    dump(HERE/'r2_method_analysis/positive_facts_costs.json',costreport)
    print(json.dumps(dict(results=[r for r in summary if r['group']=='all'],changes=changes),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','score','analyze']);p.add_argument('--model',choices=['qwen','llama']);a=p.parse_args()
    if a.action!='analyze' and a.model is None:p.error('--model is required for prepare/run/score')
    if a.action=='analyze':analyze()
    elif a.action=='prepare':prepare(a.model)
    elif a.action=='run':run(3,HERE/('r2_positive_facts_'+a.model))
    else:score_results(a.model)
