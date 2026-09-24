"""Fixed all-covered-rule mechanism views; isolated offline native scoring."""
from collections import Counter,defaultdict
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import time

from cf_moa.contracts import Budget,InputPacket,digest
from cf_moa.controller.rule_operation_ablation import run
from cf_moa.evaluation.native_scoring import load_native_scorer,score_proposal,source_lock
from cf_moa.evaluation.score_run import unit_summaries
from cf_moa.tools.adopted import sha256

ROOT=Path('/home/data3/txy');HERE=Path(__file__).resolve().parent;FULL=HERE.parent/'full_v5'
def read(p):
 with Path(p).open() as stream:return [json.loads(l) for l in stream if l.strip()]
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def write(p,rows):Path(p).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
KEYS='correct prediction semantic_prediction semantic_gold invalid_reason invalid format_invalid unmapped_diagnosis ambiguous raw_exact uncertainty option_f1 tp fp fn predicted_set_size gold_set_size'.split()
START=time.monotonic();scorer=load_native_scorer();api,canonical=scorer
items={r['request_id']:r for r in read(FULL/'offline/items.jsonl')}
evaluations={r['request_id']:r for r in read(FULL/'offline/evaluations.jsonl') if r['request_id'] in items}
provenance={(r['model'],r['request_id']):r for r in read(FULL/'offline/provenance.jsonl')}
sources=[ROOT/'Documents/Codex/2026-09-16/r1_head_experiments/rules/scored.jsonl',ROOT/'Documents/Codex/2026-09-14/new-chat/r2_question_scope_analysis/positive_facts_scored.jsonl',ROOT/'Documents/Codex/2026-09-24/cf_moa_candidate_verify_20260924/recovery_gpu23/analysis/complete_results/native_scored.jsonl']
oldlookup=defaultdict(list)
for path in sources:
 for line,row in enumerate(read(path),1):
  if row.get('method') in ('M4','M5') and 'record_id' in row:
   oldlookup[row['method'],row['record_id']].append((row,dict(path=str(path),line=line)))
# Scores use exactly the existing native parser projection. No reason text or
# fields absent from the unchanged native scorer can change a multi-item grade.
newcache={r['cache_key']:r for r in read(HERE/'new_native_scores.jsonl')} if (HERE/'new_native_scores.jsonl').exists() else {}
newcalls=0;reusecounts=Counter();scored=[];outputs=[];unique=[];source_bindings={str(p):sha256(p) for p in sources}

def grade(method,item,evaluation,native,*,base_unchanged=False):
 global newcalls
 answer=native.get('answer_choice') if isinstance(native,dict) else native
 cache_key=digest(dict(item=item,evaluation=evaluation,answer=answer,native_available=native is not None))
 if cache_key in newcache:
  reusecounts['new_analysis_cache']+=1
  return deepcopy(newcache[cache_key]['score']),dict(mode='reused_new_analysis_cache',cache_key=cache_key)
 if native is not None:
  pred,error,raw=api.parse(json.dumps(dict(answer=answer),ensure_ascii=False),item,canonical)
  pred=json.loads(json.dumps(pred));semantic_gold=sorted(api.norm(item['options'][k]) for k in evaluation['gold'])
  for old,proof in oldlookup[method,evaluation['record_id']]:
   if any(k in old and old[k]!=evaluation[k] for k in ('gold','task','target','role','item_id')):continue
   if old.get('prediction')!=pred or old.get('invalid_reason')!=error or old.get('raw_exact')!=(raw==evaluation['gold']):continue
   if old.get('semantic_gold')!=semantic_gold or old.get('correct') is None:continue
   result={k:deepcopy(old.get(k)) for k in KEYS};result.update(applicability='supported',native_available=True,method_score='scored',semantic_result='native_answer_available')
   reusecounts['existing_native_score_parser_equivalent']+=1
   return result,dict(mode='existing_native_score_parser_equivalent',**proof,native_parser_only_executed=True,scorer_not_executed=True)
 else:
  for old,proof in oldlookup[method,evaluation['record_id']]:
   if old.get('native_available') is False and old.get('correct') is None:
    result={k:deepcopy(old.get(k)) for k in KEYS};result.update(applicability='failed',native_available=False,method_score='not_scored',semantic_result='unavailable')
    reusecounts['existing_unavailable_score']+=1
    return result,dict(mode='existing_unavailable_score',**proof)
 result=score_proposal(item,evaluation,dict(native_proposal=native,applicability='supported' if native is not None else 'failed'),scorer=scorer)
 entry=dict(cache_key=cache_key,method=method,request_id=evaluation['request_id'],record_id=evaluation['record_id'],native_proposal=native,score=result,reason='new changed assembly answer' if not base_unchanged else 'new unavailable B native interface; previous illegal object retained separately')
 if base_unchanged and native is not None:raise AssertionError('Baseline native response must have an existing score: '+evaluation['request_id'])
 newcache[cache_key]=entry;newcalls+=1
 with (HERE/'new_native_scores.jsonl').open('a') as stream:stream.write(json.dumps(entry,ensure_ascii=False)+'\n')
 return deepcopy(result),dict(mode='new_original_native_score',cache_key=cache_key,reason=entry['reason'])

for method in ('M4','M5'):
 basepath=FULL/'cache'/(method.lower()+'_bases.jsonl');source_bindings[str(basepath)]=sha256(basepath)
 bases={r['request_id']:r for r in read(basepath) if r['result']['operations']['roles']==['A1','A2']}
 assert len(bases)==123
 packets={}
 with (FULL/'inference'/(method.lower()+'.jsonl')).open() as stream:
  for line in stream:
   data=json.loads(line)
   if data['request_id'] in bases:
    data['budget']=Budget(**data['budget']);p=InputPacket(**data);packets[p.request_id]=p
 for rid,p in packets.items():
  row=bases[rid];base=row['result'];assert base['input_hash']==p.input_hash
  original=base.get('trace',{}).get('legacy_result');proof=deepcopy(row['source_proof'])
  if original is None:
   source=proof['component_source'];sourcepath=Path(source['path']);source_bindings[str(sourcepath)]=sha256(sourcepath)
   origin=read(sourcepath)[source['physical_line']-1];assert digest(origin)==source['row_digest'];original=origin['proposal']['trace']['legacy_result']
  initial_digest=digest(original);item=items[rid];evaluation=evaluations[rid]
  assert evaluation['role']!='reference' and item['answer_format']=='multi'
  original_native=base['native_answer'];baseline_score,baseline_proof=grade(method,item,evaluation,original_native,base_unchanged=True)
  scored.append(dict(method=method,arm='strong_B',request_id=rid,record_id=evaluation['record_id'],score_provenance=baseline_proof,**baseline_score))
  unique.append(dict(method=method,arm='strong_B',request_id=rid,unit_id=evaluation['unit_id'],correct=baseline_score['correct'],invalid=baseline_score['invalid'],native_available=original_native is not None))
  for disabled in ('add','remove'):
   view=run(p.native_input,p.baseline_answer,original,disabled=disabled);assert digest(original)==initial_digest
   changed=view['answer']!=original['answer'];native=deepcopy(original_native)
   if changed:
    native=dict(step_by_step_thinking='Offline mechanism ablation of one saved shared rule execution. Facts and original support records are unchanged. The '+disabled+' operation is disabled only in a separate assembly view; this deterministic statement is not model reasoning.',answer_choice=deepcopy(view['answer']))
   score,score_proof=(deepcopy(baseline_score),dict(mode='unchanged_complete_B_score',baseline_score_provenance=baseline_proof)) if not changed else grade(method,item,evaluation,native)
   arm='disable_'+disabled
   outputs.append(dict(method=method,arm=arm,request_id=rid,input_hash=p.input_hash,native_answer=native,native_valid=native is not None,original_native_answer=original_native,original_candidate_native_answer=base.get('candidate_native_answer'),same_original_result_digest=initial_digest,shared_execution_source=proof,view=view,answer_changed=changed,new_model_requests=0))
   scored.append(dict(method=method,arm=arm,request_id=rid,record_id=evaluation['record_id'],score_provenance=score_proof,**score))
   unique.append(dict(method=method,arm=arm,request_id=rid,unit_id=evaluation['unit_id'],family_ids=provenance[method,rid]['family_ids'],applicable=view['applicable'],answer_changed=changed,correct=score['correct'],invalid=score['invalid'],native_available=native is not None,baseline_correct=baseline_score['correct'],repair=baseline_score['correct'] is False and score['correct'] is True,harm=baseline_score['correct'] is True and score['correct'] is False,unavailable_to_correct=baseline_score['correct'] is None and score['correct'] is True))
summary=[]
for method in ('M4','M5'):
 for arm in ('strong_B','disable_add','disable_remove'):
  rs=[r for r in unique if r['method']==method and r['arm']==arm];ss=[r for r in scored if r['method']==method and r['arm']==arm];es=[evaluations[r['request_id']] for r in rs];units=unit_summaries(ss,es)
  summary.append(dict(method=method,arm=arm,inputs=len(rs),correct=sum(r['correct'] is True for r in rs),incorrect=sum(r['correct'] is False for r in rs),unavailable=sum(r['correct'] is None for r in rs),applicable=sum(r.get('applicable',False) for r in rs) if arm!='strong_B' else None,changed=sum(r.get('answer_changed',False) for r in rs),repair=sum(r.get('repair',False) for r in rs),harm=sum(r.get('harm',False) for r in rs),unavailable_to_correct=sum(r.get('unavailable_to_correct',False) for r in rs),native_units=units))
write(HERE/'proposals.jsonl',outputs);write(HERE/'native_scored.jsonl',scored);write(HERE/'per_input_status.jsonl',unique);dump(HERE/'summary.json',summary)
assert all(sha256(path)==value for path,value in source_bindings.items())
dump(HERE/'receipt.json',dict(status='complete',methods=['M4','M5'],inputs_per_method=123,complete_native_nonreference_units_per_method=123,operation_views=492,new_model_calls=0,new_fact_extractions=0,new_old_head_executions=0,new_native_grader_calls=newcalls,reused_scores=dict(reusecounts),source_bindings=source_bindings,scorer_sources=source_lock(),scorer_identity_unchanged=True,elapsed_seconds=time.monotonic()-START,scope='all 123 rule-covered inputs; not the full 13905-input system score; all nonapplicable and unavailable retained',mechanism='two operation projections of one existing shared support engine, not two independent models',score_reuse='same current evaluation and original native-parser outputs/error/raw_exact/semantic_gold; explanations are not grader inputs for multi format',invalid_originals='corrected cache unavailable interfaces retained, original invalid object stays in candidate_native_answer'))
print(json.dumps(dict(status='complete',new_native_grader_calls=newcalls,summary=[{k:v for k,v in r.items() if k!='native_units'} for r in summary]),ensure_ascii=False))
