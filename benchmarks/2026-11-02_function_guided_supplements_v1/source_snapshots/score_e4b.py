"""Offline native scoring for the frozen 80-input instruction comparison."""
import json,sys,collections
import numpy as np
import pandas as pd
from common import ROOT,WORK,FULL,rows,write,dump,sha,now
sys.path.insert(0,str(WORK))
from cf_moa.evaluation.native_scoring import load_native_scorer,score_proposal,source_lock
from cf_moa.contracts import digest
out=ROOT/'e4b/analysis';out.mkdir(exist_ok=True)
selection={r['request_id']:r for r in rows(ROOT/'e4b/offline/selection.jsonl')}
evals=collections.defaultdict(list)
for e in rows(FULL/'offline/evaluations.jsonl'):
 if e['request_id'] in selection and e['role']!='reference':evals[e['request_id']].append(e)
assert len(evals)==80 and all(len(es)==1 for es in evals.values())
assert len({r['families'][0] for r in selection.values()})==80
scorer=load_native_scorer();records=[];costs=[];paired=[];finished=[]
def contrast(d,method,scope):
 p=d.pivot(index='input_id',columns='arm',values='success').astype(float)
 v=(p.conditioned-p.uniform).to_numpy();rng=np.random.default_rng(20261102)
 ci=np.quantile(v[rng.integers(len(v),size=(4000,len(v)))].mean(1),[.025,.975])
 return dict(method=method,scope=scope,n=len(v),conditioned_minus_uniform=float(v.mean()),ci95_low=float(ci[0]),ci95_high=float(ci[1]),conditioned_only=int((v>0).sum()),uniform_only=int((v<0).sum()))
for m in ['M4','M5']:
 run=ROOT/'e4b/runs'/m.lower()
 if not (run/'terminal.json').exists():continue
 terminal=json.load((run/'terminal.json').open());assert terminal['status']=='complete' and terminal['completed']==160
 requests=list(rows(ROOT/'e4b/inference'/f'{m.lower()}.jsonl'));shared={};responses=[];local=[]
 for r in requests:
  z=json.load((run/'responses'/(r['request_id']+'.json')).open());responses.append(z)
  assert z['request_hash']==r['request_hash']==digest(r['request']) and z['shared_information_hash']==r['shared_information_hash']
  visible=json.loads(r['request']['messages'][1]['content']);iid=r['input_id']
  if iid in shared:assert shared[iid]==visible
  else:shared[iid]=visible
  e=evals[iid][0];sel=selection[iid];n=z['native_answer']
  score=score_proposal(visible['current_native_input'],e,dict(native_proposal=n,applicability='applicable' if n is not None else 'failed'),scorer=scorer)
  entry=dict(method=m,arm=r['arm'],input_id=iid,request_id=r['request_id'],family=sel['families'][0],operation=sel['operation'],source=sel['source'],record_id=e['record_id'],labels=e['evaluation_labels'],native_answer=n,score=score,success=score['correct'] is True,native_available=score['native_available'])
  records.append(entry);local.append(entry)
 d=pd.DataFrame(local);paired.append(contrast(d,m,'ALL_80_inputs'))
 for op,g in d.groupby('operation'):paired.append(contrast(g,m,op))
 costs.append(dict(method=m,requests=len(responses),input_tokens=sum(z['usage']['input_tokens'] for z in responses),output_tokens=sum(z['usage']['output_tokens'] for z in responses),length_stops=sum(z['usage'].get('finish_reason')=='length' for z in responses),invalid_json_or_schema=sum(z['error'] is not None for z in responses),elapsed_seconds=terminal['elapsed_seconds'],upstream_calls=0))
 finished.append(m)
d=pd.DataFrame(records)
if len(d):
 for name,keys in [('overall',['method','arm']),('by_operation',['method','arm','operation']),('by_source',['method','arm','source'])]:
  q=d.groupby(keys).agg(n=('success','size'),correct=('success','sum'),available=('native_available','sum')).reset_index();q['accuracy']=q.correct/q.n;q['unavailable']=q.n-q.available;q.to_csv(out/(name+'.csv'),index=False)
 categories=[]
 for (m,a),g in d.groupby(['method','arm']):
  for c in ['R1','R2','R3','R4','R5']:
   x=g[g.labels.map(lambda labels:c in labels)]
   if len(x):categories.append(dict(method=m,arm=a,category=c,n=len(x),correct=int(x.success.sum()),accuracy=float(x.success.mean())))
 pd.DataFrame(categories).to_csv(out/'by_function.csv',index=False)
write(out/'native_scored.jsonl',records);pd.DataFrame(paired).to_csv(out/'paired.csv',index=False);pd.DataFrame(costs).to_csv(out/'costs.csv',index=False)
dump(out/'receipt.json',dict(status='complete' if len(finished)==2 else 'partial',time=now(),methods=finished,physical_calls=sum(r['requests'] for r in costs),scoring_source_lock=source_lock(),denominator='80 inputs from 80 different conservative families, one non-reference native evaluation per input; not full-v5 ALL',limits=['Exposed v5 diagnostic; not full CF-MoA or independent confirmation.','Both arms have identical resources, input, initial answer, schema and one-call budget.','Only capability-based focus instruction differs; no true offline function labels supplied.','Paired intervals condition on this fixed panel; operation intervals exploratory.','Invalid answers retained in denominator.']))
print(pd.read_csv(out/'overall.csv').to_string(index=False));print(pd.DataFrame(paired).to_string(index=False))
