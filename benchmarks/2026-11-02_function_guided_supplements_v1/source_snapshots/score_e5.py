"""Native offline evaluation: 32 fixed families, 112 endpoints per backbone."""
import json,sys,collections
import numpy as np
import pandas as pd
from common import ROOT,WORK,rows,write,dump,sha,now
sys.path.insert(0,str(WORK))
from cf_moa.evaluation.native_scoring import load_native_scorer,score_proposal,source_lock
from cf_moa.contracts import digest
out=ROOT/'e5/analysis';out.mkdir(exist_ok=True)
evals={e['request_id']:e for e in rows(ROOT/'e5/offline/evaluations.jsonl')}
assert len(evals)==112
scorer=load_native_scorer();records=[];pairs=[];costs=[];finished=[]
for m in ['M4','M5']:
 run=ROOT/'e5/runs'/m.lower()
 if not (run/'terminal.json').exists():continue
 terminal=json.load((run/'terminal.json').open());assert terminal['status']=='complete' and terminal['completed']==112
 data=list(rows(ROOT/'e5/inference'/f'{m.lower()}.jsonl'));local=[]
 for item in data:
  rid=item['packet']['request_id'];z=json.load((run/'results'/(rid+'.json')).open())
  assert z['frozen_packet_hash']==digest(item)
  e=evals[rid]
  for arm,native in z['arms'].items():
   score=score_proposal(item['packet']['native_input'],e,dict(native_proposal=native,applicability='applicable' if native is not None else 'failed'),scorer=scorer)
   entry=dict(method=m,arm=arm,request_id=rid,unit_id=e['unit_id'],family=e['group_id'],source=e['unit_id'].split(':')[0],task=e['task'],role=e['role'],labels=e['labels'],native_answer=native,score=score,success=score['correct'] is True,native_available=score['native_available'])
   records.append(entry);local.append(entry)
 for arm in ['C0','B','Gen','RulePrompt']:
  rs=[r for r in local if r['arm']==arm];groups=collections.defaultdict(list)
  for r in rs:groups[r['unit_id']].append(r)
  assert len(groups)==32
  for unit,entries in groups.items():
   refs=[r for r in entries if r['role']=='reference'];vs=[r for r in entries if r['role']!='reference']
   for variant in vs:
    reference=[r for r in refs if r['task']==variant['task']] if variant['source']!='M22' else refs
    assert len(reference)==1;reference=reference[0]
    assert reference['score']['semantic_gold']==variant['score']['semantic_gold'],'This panel must contain only native keep-answer pairs'
    valid=reference['native_available'] and variant['native_available'] and not reference['score']['invalid'] and not variant['score']['invalid']
    pairs.append(dict(method=m,arm=arm,unit_id=unit,family=variant['family'],source=variant['source'],reference=reference['request_id'],variant=variant['request_id'],task=variant['task'],both_correct=reference['success'] and variant['success'],both_valid=valid,same_semantic_answer=valid and reference['score']['semantic_prediction']==variant['score']['semantic_prediction']))
 for path in (run/'calls').glob('*.json'):
  c=json.load(path.open());u=c['usage'];assert c['request_hash']==digest(c['request'])
  costs.append(dict(method=m,key=c['key'],request_id=c['request_id'],phase=c['phase'],kind=c['request']['kind'],input_tokens=u['input_tokens'],output_tokens=u['output_tokens'],elapsed_seconds=u['elapsed_seconds'],length_stop=u.get('finish_reason')=='length',missing_code=c['request'].get('allowed_codes') is not None and len(c['request']['allowed_codes'])<len(c['request']['codes'])))
 assert len([c for c in costs if c['method']==m])==terminal['physical_calls']
 finished.append(m)
assert finished,'No complete backbone'
d=pd.DataFrame(records);d.to_json(out/'native_scored.jsonl',orient='records',lines=True,force_ascii=False)
unit=d[d.role!='reference'].groupby(['method','arm','unit_id','family','source']).agg(accuracy=('success','mean'),judgments=('success','size'),unavailable=('native_available',lambda x:int((~x).sum()))).reset_index()
unit.to_csv(out/'unit_scores.csv',index=False)
primary=unit.groupby(['method','arm']).agg(units=('unit_id','size'),accuracy=('accuracy','mean'),nonreference_judgments=('judgments','sum'),unavailable=('unavailable','sum')).reset_index();primary.to_csv(out/'primary_unit_mean.csv',index=False)
unit.groupby(['method','arm','source']).agg(units=('unit_id','size'),accuracy=('accuracy','mean'),judgments=('judgments','sum')).reset_index().to_csv(out/'by_source.csv',index=False)
for name,g in [('all_endpoints',d),('nonreference_judgments',d[d.role!='reference'])]:
 q=g.groupby(['method','arm']).agg(n=('success','size'),correct=('success','sum'),available=('native_available','sum')).reset_index();q['accuracy']=q.correct/q.n;q.to_csv(out/(name+'.csv'),index=False)
pairdf=pd.DataFrame(pairs);pairdf.to_csv(out/'paired_behavior.csv',index=False)
pairdf.groupby(['method','arm']).agg(pairs=('both_correct','size'),both_correct=('both_correct','sum'),both_valid=('both_valid','sum'),same_semantic_answer=('same_semantic_answer','sum')).reset_index().to_csv(out/'pair_summary.csv',index=False)
contrasts=[]
for m,g in unit.groupby('method'):
 pivot=g.pivot(index=['unit_id','family'],columns='arm',values='accuracy')
 assert len(pivot)==32 and len(set(pivot.index.get_level_values('family')))==32
 for a,b in [('B','C0'),('Gen','C0'),('RulePrompt','C0'),('Gen','B'),('RulePrompt','B')]:
  v=(pivot[a]-pivot[b]).to_numpy();rng=np.random.default_rng(20261102);boot=v[rng.integers(32,size=(4000,32))].mean(1);lo,hi=np.quantile(boot,[.025,.975])
  contrasts.append(dict(method=m,comparison=a+'-'+b,units=32,delta=float(v.mean()),ci95_low=float(lo),ci95_high=float(hi),units_improved=int((v>0).sum()),units_harmed=int((v<0).sum())))
pd.DataFrame(contrasts).to_csv(out/'unit_contrasts.csv',index=False)
harms=[]
for m,g in d.groupby('method'):
 pivot=g.pivot(index='request_id',columns='arm',values='success')
 for a,b in [('B','C0'),('Gen','B'),('RulePrompt','B')]:
  harms.append(dict(method=m,comparison=a+'-'+b,endpoints=len(pivot),repair=int((pivot[a]&~pivot[b]).sum()),harm=int((~pivot[a]&pivot[b]).sum())))
pd.DataFrame(harms).to_csv(out/'endpoint_repairs_harms.csv',index=False)
doc=[]
for r in records:
 if 'document_detection' in r['score']:doc.append(dict(method=r['method'],arm=r['arm'],request_id=r['request_id'],unit_id=r['unit_id'],role=r['role'],**r['score']['document_detection']))
pd.DataFrame(doc).to_csv(out/'document_detection.csv',index=False)
pd.DataFrame(doc).groupby(['method','arm']).agg(inputs=('request_id','size'),exact=('exact','sum'),valid=('valid','sum'),tp=('tp','sum'),fp=('fp','sum'),fn=('fn','sum')).reset_index().to_csv(out/'document_summary.csv',index=False)
pd.DataFrame(costs).to_csv(out/'physical_calls.csv',index=False)
costdf=pd.DataFrame(costs);costdf.groupby(['method','phase']).agg(requests=('key','size'),input_tokens=('input_tokens','sum'),output_tokens=('output_tokens','sum'),length_stops=('length_stop','sum'),missing_code_calls=('missing_code','sum')).reset_index().to_csv(out/'physical_costs.csv',index=False)
attributed=[]
for (m,arm),g in d.groupby(['method','arm']):
 phases={'C0':['C0'],'B':['C0','F'],'Gen':['C0','F','Gen'],'RulePrompt':['C0','F','RulePrompt']}[arm]
 x=costdf[(costdf.method==m)&costdf.phase.isin(phases)]
 attributed.append(dict(method=m,arm=arm,logical_requests=len(x),input_tokens=int(x.input_tokens.sum()),output_tokens=int(x.output_tokens.sum()),new_retrieval=0,shared_base_and_F=True))
pd.DataFrame(attributed).to_csv(out/'attributed_costs.csv',index=False)
dump(out/'receipt.json',dict(status='complete' if len(finished)==2 else 'partial',time=now(),methods=finished,physical_calls=len(costs),scoring_source_lock=source_lock(),primary='32 unit means of non-reference judgments, then equal mean; 64 judgments and 112 endpoints reported separately',pair_protocol='64 unchanged-gold semantic pairs; shared reference for five M22 evidence levels; no new change-response controls',interval='4000 paired family bootstrap draws; 32 distinct families equal unit weight',limits=['Only R5; not confirmation of A1–A4 or all functional roles.','Previously collected/qualified but not previously executed selected family panel within bounded audit.','NLI exact-premise disjointness is not article-level independence.','Small source quotas; no broad clinical generalization or statistical equivalence claim.','One frozen run per backbone, invalid outputs remain in denominators.','F generated once and reused in both aggregation arms; actual shared cost counted once.','Document identification is auxiliary; correction semantics not scored.']))
print(primary.to_string(index=False));print(pd.read_csv(out/'pair_summary.csv').to_string(index=False))
