"""Replay the independent API against the frozen seven-method scoped analysis."""
import json
import os
import sys
from r2_support_pilot import HERE,PACK,read,dump
from r2_program_all_methods import MODEL
from r2_condition_head import optimize


def run():
    os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison';sys.path.insert(0,str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    refs=[r for r in read(HERE/'r2_question_scope_analysis/positive_facts_scored.jsonl') if r['policy']=='inherit_unknown']
    base={(r['method'],r['item_id']):r for r in read(HERE/'r2_program_all_methods/scored.jsonl') if r['policy']=='baseline'}
    items={r['item']['item_id']:r['item'] for r in read(HERE/'r2_task_scoped_qwen/inputs.jsonl') if r['scope']=='native'}
    raw={};requests={}
    for model in ['qwen','llama']:
        source=HERE/('r2_task_scoped_'+model)
        raw[model]={r['item_id']:r for r in read(source/'raw_predictions.jsonl') if r['review']=='facts'}
        requests[model]={r['item_id']:r for r in read(source/'requests.jsonl') if r['review']=='facts'}
        positive=HERE/('r2_positive_facts_'+model)
        raw[model].update({r['item_id']:r for r in read(positive/'raw_predictions.jsonl')})
        requests[model].update({r['item_id']:r for r in read(positive/'requests.jsonl')})
    calls=[];receipts=[]
    for ref in refs:
        method=ref['method'];iid=ref['item_id'];model=MODEL[method];b=base[method,iid];item=items[iid]
        def replay(messages,schema):
            expected=requests[model][iid]
            assert messages==expected['messages'] and schema==expected['schema'],(method,iid,'request drift')
            calls.append((method,iid));return raw[model][iid]['raw_response']
        result=optimize(item,None if b['invalid'] else b['prediction'],replay)
        scored=score(dict(raw_response=json.dumps(dict(answer=result['answer']))),ref,item,{}) if result['applied'] else b
        pred=list(scored['prediction']) if isinstance(scored['prediction'],tuple) else scored['prediction']
        assert pred==ref['prediction'] and scored['correct']==ref['correct'] and scored['invalid']==ref['invalid'],(method,iid)
        receipts.append(dict(method=method,item_id=iid,applied=result['applied'],reason=result['reason'],matched=True))
    assert len(receipts)==553 and len(calls)==7*55 and len(set(calls))==len(calls)
    dump(HERE/'r2_question_scope_analysis/positive_interface_validation.json',dict(status='passed',records=553,request_replays=385,
         new_model_calls=0,scope='all seven methods x79 R2, including 24 uncovered per method',receipts=receipts,
         note='The positive-field API requests match the actual new or unchanged previously generated original-model requests exactly; captured raw fact responses replay the generation callback. Predictions, correctness and invalid state match the separate scoped analysis.'))
    print('PASS553 native records;385 exact original-model request replays, no new inference.')


if __name__=='__main__':run()
