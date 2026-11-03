"""Reuse post-aggregation scores for gain retention and examples; no models."""
import json,sqlite3,zlib,gzip
from pathlib import Path
from collections import defaultdict
import pandas as pd
from common import ROOT,FULL,rows,dump,write,sha,now
OUT=ROOT/'aggregation';OUT.mkdir(exist_ok=True)
OLD=Path('/home/data4/txy/codex_runs/2026-10-27/cf_moa_post_aggregation_full_v1')
evals={e['record_id']:e for e in rows(FULL/'offline/evaluations.jsonl')}
tables=[];gains=[];pairs=[];sources={};examples=[]
db=sqlite3.connect('file:'+str(OLD/'samples.sqlite3')+'?mode=ro',uri=True)
for m in ['M4','M5']:
 path=OLD/'analysis'/m.lower()/'native_scored.jsonl.gz';data=list(rows(path));sources[str(path)]=sha(path)
 df=pd.DataFrame([dict(r,unit_id=evals[r['record_id']]['unit_id'],labels=evals[r['record_id']]['evaluation_labels']) for r in data if evals[r['record_id']]['role']!='reference'])
 df['success']=df.correct.eq(True);pivot=df.pivot(index='record_id',columns='arm',values='success').astype(int)
 for category in ['ALL','R1','R2','R3','R4','R5']:
  x=df if category=='ALL' else df[df.labels.map(lambda ls:category in ls)]
  for arm,g in x.groupby('arm'):
   units=g.groupby('unit_id').success.mean()
   tables.append(dict(method=m,arm=arm,category=category,units=len(units),accuracy=float(units.mean())))
  meta=x[x.arm=='strong_B'][['record_id','unit_id']].set_index('record_id')
  weight=1/meta.groupby('unit_id').unit_id.transform('size')
  p=pivot.loc[meta.index];b_gain=(p.strong_B==1)&(p.original_C0==0)
  for arm in ['gen','select','rule_prompt','strict']:
   retention=b_gain&(p[arm]==1);harm=(p.strong_B==1)&(p[arm]==0);repair=(p.strong_B==0)&(p[arm]==1)
   gains.append(dict(method=m,arm=arm,category=category,mappings=len(p),C0_wrong_B_right_mappings=int(b_gain.sum()),retained_gain_mappings=int(retention.sum()),harm_vs_B_mappings=int(harm.sum()),repair_vs_B_mappings=int(repair.sum()),unit_weighted_gain_mass=float(weight[b_gain].sum()),unit_weighted_retained_mass=float(weight[retention].sum()),unit_weighted_retention_rate=float(weight[retention].sum()/weight[b_gain].sum()) if weight[b_gain].sum() else None))
 ppath=OLD/'analysis'/m.lower()/'pairs.jsonl.gz';sources[str(ppath)]=sha(ppath)
 pp=pd.DataFrame(list(rows(ppath)))
 for (arm,relation),g in pp.groupby(['arm','relation']):pairs.append(dict(method=m,arm=arm,relation=relation,pairs=len(g),both_correct=int(g.both_correct.eq(True).sum()),complete=int(g.complete.eq(True).sum())))
 # Illustrative saved-output selection, not independent error coding.
 if m=='M4':
  wanted=[('support','R2'),('candidate','R3'),('invariance','R5')]
  taken=set()
  for name,cat in wanted:
   ids=sorted(rid for rid in pivot.index if cat in evals[rid]['evaluation_labels'] and pivot.loc[rid,'strong_B']==1 and pivot.loc[rid,'original_C0']==0 and pivot.loc[rid,'rule_prompt']==1)
   chosen=None
   for rid in ids:
    e=evals[rid]
    if e['request_id'] in taken:continue
    row=db.execute('select ordinal,payload from samples where method=? and rid=?',(m,e['request_id'])).fetchone()
    sample=json.loads(zlib.decompress(row[1]));role='A2' if name=='support' else 'A3' if name=='candidate' else 'A5'
    if sample['pool']['proposals'][role]['tool_applicable']:chosen=(rid,e,row[0],sample,role);break
   if chosen:
    rid,e,ordinal,sample,role=chosen;taken.add(e['request_id']);answers={}
    for arm in ['gen','rule_prompt']:
     p=OLD/'runs'/m.lower()/'requests'/f'{ordinal//250:03d}'/(e['request_id']+'_'+arm+'.json.gz')
     rr=next(rows(p));answers[arm]=rr['results'][arm]['native_answer']
    examples.append(dict(kind=name,method=m,record_id=rid,request_id=e['request_id'],judgment_ids=e['judgment_ids'],labels=e['evaluation_labels'],native_input=sample['packet']['native_input'],gold=e['gold'],C0=sample['packet']['baseline_response'],functional_role=role,functional_candidate=sample['pool']['proposals'][role],aggregation_outputs=answers,selection='first lexicographic eligible C0-wrong/B-right/RulePrompt-right record in the functional category; illustrative only'))
pd.DataFrame(tables).to_csv(OUT/'system_main_table_long.csv',index=False)
pd.DataFrame(gains).to_csv(OUT/'gain_retention.csv',index=False)
pd.DataFrame(pairs).to_csv(OUT/'pair_behavior.csv',index=False)
write(OUT/'illustrative_saved_examples.jsonl',examples)
dump(OUT/'receipt.json',dict(status='complete',time=now(),source_hashes=sources,new_model_calls=0,new_native_scores=0,examples=len(examples),gain_denominator='native nonreference mappings; category-unit-normalized weights supplied separately',limitations=['Paired behavior is a different axis from functional labels.','Example selection is retrospective and cannot substitute independent blind E2 error coding.','Role candidate summaries are provenance-tagged execution summaries, not raw independent medical reasoning.']))
print('aggregation support complete',len(examples))
