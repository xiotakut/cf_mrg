"""Link saved operation controls to functions; no new inference or native rescoring."""
import json,csv,sqlite3,zlib,itertools
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
import pandas as pd
from common import ROOT,WORK,FULL,rows,dump,sha,now
OUT=ROOT/'e3';OUT.mkdir(exist_ok=True)
P2=WORK/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/operation_ablations'
P3=WORK/'Documents/Codex/2026-09-14/new-chat/r3_calibrated_all_methods'
P4=WORK/'Documents/Codex/2026-09-17/r4_structural_head/physiology_head/v2/heldout'
P5=WORK/'Documents/Codex/2026-09-18/r5_head/delivery'
sources={}
def read(p):
 sources[str(p)]=sha(p)
 return json.loads(p.read_text())
evals={r['record_id']:r for r in rows(FULL/'offline/evaluations.jsonl')}
controls=read(P2/'summary.json')
raw=pd.DataFrame(list(rows(P2/'native_scored.jsonl')));sources[str(P2/'native_scored.jsonl')]=sha(P2/'native_scored.jsonl')
support=[]
for r in controls:
 x=raw[(raw.method==r['method'])&(raw.arm==r['arm'])]
 assert len(x)==123 and sum(x.correct==True)==r['correct']
 support.append({k:v for k,v in r.items() if k!='native_units'})
pd.DataFrame(support).to_csv(OUT/'support_operation_controls.csv',index=False)
scat=[]
for r in controls:
 for cat in ['ALL','R1','R2','R3','R4','R5']:
  x=raw[(raw.method==r['method'])&(raw.arm==r['arm'])]
  if cat!='ALL':x=x[x.record_id.map(lambda k:cat in evals[k]['evaluation_labels'])]
  if len(x):scat.append(dict(method=r['method'],arm=r['arm'],category=cat,inputs=len(x),correct=sum(x.correct==True),unavailable=sum(x.correct.isna()),accuracy=sum(x.correct==True)/len(x)))
pd.DataFrame(scat).to_csv(OUT/'support_controls_by_function.csv',index=False)
r3=read(P3/'summary.json');d3=pd.DataFrame(list(rows(P3/'scored.jsonl')));sources[str(P3/'scored.jsonl')]=sha(P3/'scored.jsonl')
a3=[]
for r in r3['results']:
 if r['scope']!='all680':continue
 x=d3[(d3.method==r['method'])&(d3.variant==r['variant'])]
 assert len(x)==680 and sum(x.correct==True)==r['correct']
 a3.append({k:r[k] for k in ['method','variant','n','correct','invalid','macro_recall']})
pd.DataFrame(a3).to_csv(OUT/'candidate_controls_680.csv',index=False)
r4=read(P4/'summary.json');d4=pd.DataFrame(list(rows(P4/'scored.jsonl')));sources[str(P4/'scored.jsonl')]=sha(P4/'scored.jsonl')
a4=[];paired=[]
for r in r4['results']:
 x=d4[(d4.method==r['method'])&(d4.arm==r['arm'])]
 assert len(x)==288 and sum(x.correct==True)==r['correct']
 a4.append({k:r[k] for k in ['method','arm','n','correct','invalid','joint_numeric_correct','all_outputs_correct','routes']})
for method in ['M4','M5']:
 p=d4[d4.method==method]
 for metric in ['correct','joint_numeric_correct']:
  table=p.pivot(index=['item_id','profile'],columns='arm',values=metric).astype(float)
  for control in ['full','patch_no_do']:
   if control not in table:continue
   delta=table['patch']-table[control];g=delta.groupby(level='profile').mean().to_numpy()
   rng=np.random.default_rng(20261102);ci=np.quantile(g[rng.integers(len(g),size=(2000,len(g)))].mean(1),[.025,.975])
   paired.append(dict(method=method,metric=metric,control=control,n=288,profiles=len(g),delta=delta.mean(),repair=int((delta>0).sum()),harm=int((delta<0).sum()),ci95_low=ci[0],ci95_high=ci[1]))
pd.DataFrame(a4).to_csv(OUT/'consequence_controls_288.csv',index=False);pd.DataFrame(paired).to_csv(OUT/'consequence_profile_intervals.csv',index=False)
r5=read(P5/'summary.json')
a5=[]
for r in r5['comparisons']:
 if r['source']!='all':continue
 if (r['stage']=='all' and r['control'] in ['original','maj5','single_mean']) or (r['stage']=='nli_validation' and r['control']=='native_single'):
  a5.append(dict(method=r['method'],stage=r['stage'],cohort=r['cohort'],control=r['control'],units=r['head']['units'],mappings=r['shared_mappings'],control_both_pct=r['baseline']['both_pct'],head_both_pct=r['head']['both_pct'],difference_pp=r['head']['both_pct']-r['baseline']['both_pct'],repairs=r.get('repairs'),harms=r.get('harms')))
pd.DataFrame(a5).to_csv(OUT/'invariance_matched_controls.csv',index=False)
# Frozen complete pool: role applicability / reuse / fallback are metadata, not independent new model calls.
db=Path('/home/data4/txy/codex_runs/2026-10-27/cf_moa_post_aggregation_full_v1/samples.sqlite3')
conn=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True);counts=Counter();catcounts=Counter();n=Counter()
labels=defaultdict(set)
for e in evals.values():
 if e['role']!='reference':labels[e['request_id']].update(e['evaluation_labels'])
for method,rid,blob in conn.execute('select method,rid,payload from samples order by method,ordinal'):
 pool=json.loads(zlib.decompress(blob))['pool'];n[method]+=1
 for role,p in pool['proposals'].items():
  key=(method,role,p['tool_applicable'],p['execution_mode'],p['execution_status'],p['native_answer'] is not None,p['shared_origin'])
  counts[key]+=1
  for cat in labels[rid]:catcounts[(cat,)+key]+=1
 if sum(n.values())%5000==0:print('coverage',sum(n.values()),flush=True)
assert n=={'M4':13905,'M5':13905}
cols=['method','role','tool_applicable','execution_mode','execution_status','native_available','shared_origin']
pd.DataFrame([dict(zip(cols,k),inputs=v) for k,v in counts.items()]).to_csv(OUT/'role_coverage_all_inputs.csv',index=False)
pd.DataFrame([dict(zip(['category']+cols,k),inputs=v) for k,v in catcounts.items()]).to_csv(OUT/'role_coverage_by_function_nonreference.csv',index=False)
sources[str(db)]=sha(db)
dump(OUT/'receipt.json',dict(status='complete',time=now(),source_hashes=sources,new_model_requests=0,new_native_scores=0,new_simulations=0,full_input_counts=dict(n),controls='saved scores; deterministic recombination of statistics',limits=['Historical component panels retain their versions and denominators.','Same frozen pool role records are not five independent model generations.','A1/A2 share one execution; unavailable and unsupported are distinct.','A4 clinical activation is zero; given-model profile panel is separate.']))
print('E3 complete',flush=True)
