"""Verify complete fixed-run evidence and original source integrity, no inference."""
import json,sys,collections
from copy import deepcopy
from dataclasses import replace
from common import ROOT,WORK,rows,sha,dump,now
sys.path.insert(0,str(WORK))
from cf_moa.contracts import digest,InputPacket,Budget
from cf_moa.evaluation.c0_native import parse_native
receipts={};physical_total=0;identities=[]
for path,h in json.load((ROOT/'e5/implementation_freeze.json').open())['files'].items():
 assert sha(path)==h,path
def actual(p):
 assert p['status']=='complete' and p['submission_state']=='accepted'
 assert all(p['expected_engine_request'][k]==p['engine_accepted'][k] for k in p['expected_engine_request'])
 assert p['event']['input_tokens']==len(p['engine_prompt_token_ids'])
 assert p['engine_accepted']['sampling_params']['truncate_prompt_tokens'] is None
for experiment in ['e4b','e5']:
 out=ROOT/experiment;prep=json.load((out/'preparation.json').open())
 for path,h in prep['sources'].items():assert sha(path)==h,path
 assert sha(out/'runtime.json')==prep['runtime_sha256']
 assert json.load((out/'analysis/receipt.json').open())['status']=='complete'
 n=0
 for m in ['M4','M5']:
  ip=out/'inference'/f'{m.lower()}.jsonl';assert sha(ip)==prep['inference_hashes'][m]
  run=out/'runs'/m.lower();term=json.load((run/'terminal.json').open())
  assert term['status']=='complete' and json.load((run/'cleanup.json').open())['status']=='complete'
  inputs=list(rows(ip))
  if experiment=='e4b':
   assert term['completed']==len(inputs)==160
   assert {p.stem for p in (run/'submitted').glob('*.json')}=={r['request_id'] for r in inputs}=={p.stem for p in (run/'responses').glob('*.json')}
   for r in inputs:
    z=json.load((run/'responses'/(r['request_id']+'.json')).open());assert z['request_hash']==r['request_hash']==digest(r['request']);actual(z['physical']);n+=1
  else:
   assert term['completed']==len(inputs)==112
   assert {p.stem for p in (run/'results').glob('*.json')}=={i['packet']['request_id'] for i in inputs}
   submitted={p.stem for p in (run/'submitted').glob('*.json')};saved={p.stem for p in (run/'calls').glob('*.json')};assert submitted==saved
   used=[];complete_B_equal=0;choice_B_equal=0
   for i in inputs:
    rid=i['packet']['request_id'];z=json.load((run/'results'/(rid+'.json')).open());assert z['frozen_packet_hash']==digest(i);used+=z['physical_call_keys']
    first=json.load((run/'calls'/(rid+'_00.json')).open())
    assert first['phase']=='C0' and first['value']==z['C0']['raw_response']
    assert parse_native(first['value'],m)==z['arms']['C0']
    values=deepcopy(i['packet']);values['budget']=Budget(**values['budget']);p=InputPacket(**values)
    native=z['arms']['C0'];initial=native.get('answer_choice') if isinstance(native,dict) else native
    p=replace(p,baseline_answer=initial,baseline_response=first['value'])
    assert p.input_hash==z['input_hash']==z['pool']['input_hash']
    assert z['arms']['B']==z['F']['native_proposal']==z['pool']['proposals']['A5']['native_answer']
    assert z['arms']['C0']==z['pool']['c0_native']
    a=z['aggregations']['RulePrompt'];selected=a['selected_candidate_id']
    expected=z['pool']['c0_native'] if selected=='C0' else z['pool']['proposals'][selected]['native_answer'] if selected else None
    assert z['arms']['RulePrompt']==a['native_answer']==expected
    complete_B_equal+=z['arms']['RulePrompt']==z['arms']['B']
    choice_B_equal+=z['arms']['RulePrompt'].get('answer_choice')==z['arms']['B'].get('answer_choice')
    assert z['pool']['capabilities']['F_eligible'] and not any(z['pool']['capabilities'][k] for k in ['diagnosis','rule_eligible','complete_model_capability'])
   assert set(used)==saved and len(used)==len(set(used))==term['physical_calls']
   identities.append(dict(method=m,inputs=112,RulePrompt_complete_native_equal_B=complete_B_equal,RulePrompt_answer_choice_equal_B=choice_B_equal))
   for key in saved:
    c=json.load((run/'calls'/(key+'.json')).open());assert c['request_hash']==digest(c['request']);actual(c['physical']);n+=1
    if c['phase']=='C0':
     accepted=c['physical']['engine_accepted']['sampling_params'];assert accepted['temperature']==.7 and accepted['max_tokens']==2048
     assert (accepted['guided_decoding'] is None)==(m=='M5')
 assert json.load((out/'supervisor/terminal.json').open())['status']=='complete'
 receipts[experiment]=dict(status='passed',physical_calls=n,original_sources=len(prep['sources']),models_closed=2)
 physical_total+=n
dump(ROOT/'extension_validation.json',dict(status='passed',time=now(),experiments=receipts,new_physical_calls=physical_total,new_retrieval=0,human_labels=0,source_immutability=True,actual_engine_acceptance_checked=True,no_unknown_submissions=True,no_prompt_truncation=True,selected_complete_native_response_preserved=True,identity_with_B=identities))
print(json.dumps(receipts))
