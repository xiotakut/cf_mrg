"""Native scoring of frozen terminal controls; model workers never import this file."""
import json,sys,collections
from pathlib import Path
import numpy as np
import pandas as pd
from common import ROOT,WORK,FULL,rows,dump,write,sha,now
sys.path.insert(0,str(WORK))
from cf_moa.evaluation.native_scoring import load_native_scorer,score_proposal,source_lock
OUT=ROOT/'e4a/analysis';OUT.mkdir(exist_ok=True)
bas={(r['method'],r['request_id']):r for r in rows(ROOT/'e4a/offline/baselines.jsonl')}
evals=collections.defaultdict(list)
for e in rows(FULL/'offline/evaluations.jsonl'):
 if e['role']!='reference':evals[e['request_id']].append(e)
families=json.load(open(ROOT/'e1_corrected/family_mapping.json'))['record_to_family']
scorer=load_native_scorer();records=[];checks=[];summaries=[];costs=[];subsets=[];finished=[]
def answer(n):
 return n.get('answer_choice') if isinstance(n,dict) else None
for m in ['M4','M5']:
 run=ROOT/'e4a/runs'/m.lower()
 if not (run/'terminal.json').exists():continue
 terminal=json.load(open(run/'terminal.json'));assert terminal['status']=='complete' and terminal['completed']==123
 requests=list(rows(ROOT/'e4a/inference'/f'{m.lower()}.jsonl'));local=[];responses=[]
 for r in requests:
  raw=json.load(open(run/'responses'/(r['request_id']+'.json')));responses.append(raw)
  assert raw['request_hash']==r['request_hash'] and raw['shared_information_hash']==r['shared_information_hash']
  assert len(raw['physical'])==1 and raw['new_model_requests']==1
  visible=json.loads(r['request']['messages'][1]['content']);old=bas[m,r['request_id']]
  assert len(evals[r['request_id']])==1
  e=evals[r['request_id']][0];family=families[e['record_id']]
  for arm,native in [('program_B',old['native_answer']),('uniform_LLM',raw['native_answer'])]:
   score=score_proposal(visible['current_input'],e,dict(native_proposal=native,applicability='applicable' if native is not None else 'failed'),scorer=scorer)
   entry=dict(method=m,arm=arm,request_id=r['request_id'],record_id=e['record_id'],family=family,unit_id=e['unit_id'],labels=e['evaluation_labels'],native_answer=native,correct=score['correct'],native_available=score['native_available'],score=score,upstream_applied=visible['upstream_applied'])
   records.append(entry);local.append(entry)
   pred=answer(native);available=isinstance(pred,list)
   initial=visible['initial_answer'];none=visible['none_option_key'];options=visible['current_input']['options']
   iv=isinstance(initial,list) and bool(initial) and all(k in options for k in initial) and not(none in initial and len(initial)>1)
   if visible['upstream_applied']:
    for k,v in (visible['saved_support_states'] or {}).items():
     state=v['state']
     checks.append(dict(method=m,arm=arm,request_id=r['request_id'],family=family,option=k,metric='include_established' if state=='MET' else 'exclude_contradicted' if state=='CONTRADICTED' else 'preserve_unknown',eligible=state!='UNKNOWN' or iv,passed=available and ((k in pred) if state=='MET' else (k not in pred) if state=='CONTRADICTED' else ((k in pred)==(k in initial)) if iv else False)))
     if state=='MET' and iv and k not in initial:checks.append(dict(method=m,arm=arm,request_id=r['request_id'],family=family,option=k,metric='activation_missing_from_initial',eligible=True,passed=available and k in pred))
     if state=='CONTRADICTED' and iv and k in initial:checks.append(dict(method=m,arm=arm,request_id=r['request_id'],family=family,option=k,metric='retraction_of_initial',eligible=True,passed=available and k not in pred))
     states=[x.get('state') for x in v.get('paths',[])]
     if state=='MET' and 'MET' in states and 'CONTRADICTED' in states:checks.append(dict(method=m,arm=arm,request_id=r['request_id'],family=family,option=k,metric='remaining_independent_support',eligible=True,passed=available and k in pred))
 d=pd.DataFrame(local);d['success']=d.correct.eq(True)
 for arm,g in d.groupby('arm'):
  summaries.append(dict(method=m,arm=arm,n=len(g),correct=int(g.success.sum()),unavailable=int((~g.native_available).sum()),accuracy=float(g.success.mean())))
  for cat in ['R1','R2','R3','R4','R5']:
   x=g[g.labels.map(lambda ls:cat in ls)]
   if len(x):subsets.append(dict(method=m,arm=arm,category=cat,n=len(x),correct=int(x.success.sum()),unavailable=int((~x.native_available).sum()),accuracy=float(x.success.mean())))
 pivot=d.pivot(index=['request_id','family'],columns='arm',values='success').astype(int)
 delta=pivot.program_B-pivot.uniform_LLM;g=delta.groupby(level='family').agg(['sum','count']).to_numpy();rng=np.random.default_rng(20261102);s=g[rng.integers(len(g),size=(2000,len(g)))].sum(1);ci=np.quantile(s[:,0]/s[:,1],[.025,.975])
 native_agree=0;available_agree=0;both_available=0;both_unavailable=0
 for r in requests:
  b=bas[m,r['request_id']]['native_answer'];l=json.load(open(run/'responses'/(r['request_id']+'.json')))['native_answer']
  if b is None and l is None:both_unavailable+=1
  elif b is not None and l is not None:
   both_available+=1;available_agree+=set(answer(b))==set(answer(l))
  native_agree+=(b is None and l is None) or (b is not None and l is not None and set(answer(b))==set(answer(l)))
 dump(OUT/f'{m.lower()}_paired.json',dict(method=m,n=123,families=len(g),program_minus_LLM=float(delta.mean()),ci95=[float(x) for x in ci],program_correct_LLM_incorrect=int((delta>0).sum()),LLM_correct_program_incorrect=int((delta<0).sum()),same_answer_or_both_unavailable=native_agree,both_available=both_available,agree_when_both_available=available_agree,both_unavailable=both_unavailable,bootstrap_draws=2000))
 costs.append(dict(method=m,requests=len(responses),input_tokens=sum(r['usage']['input_tokens'] for r in responses),output_tokens=sum(r['usage']['output_tokens'] for r in responses),length_stops=sum(r['usage'].get('finish_reason')=='length' for r in responses),invalid_json_or_schema=sum(r['error'] is not None for r in responses),elapsed_seconds=terminal['elapsed_seconds'],new_upstream_calls=0))
 finished.append(m)
write(OUT/'native_scored.jsonl',records);pd.DataFrame(summaries).to_csv(OUT/'overall.csv',index=False);pd.DataFrame(subsets).to_csv(OUT/'by_function.csv',index=False);pd.DataFrame(costs).to_csv(OUT/'costs.csv',index=False)
if checks:
 x=pd.DataFrame(checks);x.to_csv(OUT/'option_requirements.csv',index=False)
 x=x[x.eligible].groupby(['method','arm','metric']).agg(option_requirements=('passed','size'),inputs=('request_id','nunique'),passed=('passed','sum')).reset_index()
 x['rate']=x.passed/x.option_requirements;x.to_csv(OUT/'operation_requirements.csv',index=False)
dump(OUT/'receipt.json',dict(time=now(),status='complete' if len(finished)==2 else 'partial',completed_methods=finished,planned_requests=246,actual_completed_requests=sum(r['requests'] for r in costs),new_upstream_calls=0,scoring_source_lock=source_lock(),limits=['Same frozen support states; terminal execution/readout control only.','Requirement success is relative to shared saved states, not independent clinical truth.','No automatic retries; length/parse failures and unavailable outputs remain in denominator.','Intervals use scenario-family clustering and are conditional on this exposed panel.']))
print(json.dumps(summaries));print(json.dumps(costs))
