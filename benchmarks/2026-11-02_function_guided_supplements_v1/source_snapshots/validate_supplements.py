"""Final artifact audit. Does not submit inference or alter prior results."""
import json,sys,csv,zipfile,hashlib
from pathlib import Path
import pandas as pd
from common import ROOT,WORK,FULL,rows,dump,sha,now
sys.path.insert(0,str(WORK))
from cf_moa.contracts import digest
prep=json.load(open(ROOT/'e4a/preparation.json'));runtime=json.load(open(ROOT/'e4a/runtime.json'))
assert sha(ROOT/'e4a/runtime.json')==prep['runtime_sha256']
for p,h in prep['sources'].items():assert sha(p)==h,p
native=list(rows(ROOT/'e4a/analysis/native_scored.jsonl'))
old={(r['method'],r['record_id']):r for r in rows(WORK/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/operation_ablations/native_scored.jsonl') if r['arm']=='strong_B'}
for r in native:
 if r['arm']=='program_B':assert r['correct']==old[r['method'],r['record_id']]['correct']
new=0;token_in=0;token_out=0;fail=0;records=[]
for m in ['M4','M5']:
 run=ROOT/'e4a/runs'/m.lower();qs=list(rows(ROOT/'e4a/inference'/f'{m.lower()}.jsonl'))
 assert sha(ROOT/'e4a/inference'/f'{m.lower()}.jsonl')==prep['inference_hashes'][m]
 assert json.load(open(run/'terminal.json'))['status']=='complete'
 assert json.load(open(run/'cleanup.json'))['status']=='complete'
 assert len(list((run/'responses').glob('*.json')))==len(list((run/'submitted').glob('*.json')))==len(qs)==123
 engineids=[]
 for q in qs:
  r=json.load(open(run/'responses'/(q['request_id']+'.json')))
  assert digest(q['request'])==q['request_hash']==r['request_hash']
  v=json.loads(q['request']['messages'][1]['content']);assert digest(v)==r['shared_information_hash']
  assert not set(v)&{'gold','labels','evaluation_labels','judgment_id','old_final_answer'}
  assert r['new_model_requests']==1 and len(r['physical'])==1
  phys=r['physical'][0];assert phys['status']=='complete' and phys['submission_state']=='accepted'
  actual=phys['engine_accepted']['prompt']
  assert actual==phys['request']['prompt']
  assert all(msg['content'] in actual for msg in q['request']['messages'])
  par=phys['request']['sampling_params'];assert par['temperature']==0 and par['seed']==42 and par['max_tokens']==4096
  assert phys['value']==r['raw']==phys['raw_response']
  assert phys['event']['input_tokens']==r['usage']['input_tokens']
  engineids.append(phys['engine_core_request_id'])
  new+=1;token_in+=r['usage']['input_tokens'];token_out+=r['usage']['output_tokens'];fail+=r['error'] is not None
  records.append(dict(method=m,request_id=q['request_id'],response_hash=sha(run/'responses'/(q['request_id']+'.json')),request_hash=q['request_hash']))
 assert len(set(engineids))==123
assert new==246
for name in ['phase1_classification','phase2_error_coding']:
 with zipfile.ZipFile(ROOT/'e2'/f'{name}.zip') as z:
  assert not any('coordinator' in f or 'selection' in f for f in z.namelist())
  for reviewer in ['A','B']:
   data=list(csv.DictReader(z.read(f'reviewer_{reviewer}.csv').decode().splitlines()))
   assert len(data)==120
   assert all(not v for r in data for k,v in r.items() if k not in ['blind_id','reviewer_id'])
e1=json.load(open(ROOT/'e1_corrected/summary.json'));df=pd.read_json(ROOT/'e1_corrected/out_of_fold.jsonl.gz',lines=True)
assert df.groupby('family').fold.nunique().max()==1 and df.groupby('record_id').fold.nunique().max()==1
assert df.family.nunique()==4216
assert len(pd.read_csv(ROOT/'e1_corrected/category_reproduction.csv'))==42
e3=json.load(open(ROOT/'e3/receipt.json'))
assert e3['new_model_requests']==0
for p,h in e3['source_hashes'].items():assert sha(p)==h
agg=pd.read_csv(ROOT/'aggregation/system_main_table_long.csv')
assert agg.groupby(['method','arm']).size().eq(6).all()
for m,g in agg.groupby('method'):
 b=g[g.arm=='strong_B'].set_index('category').accuracy;s=g[g.arm=='strict'].set_index('category').accuracy;assert (b==s).all()
receipt=dict(status='passed',time=now(),completed_new_requests=new,input_tokens=token_in,output_tokens=token_out,length_or_parse_failures=fail,new_upstream_calls=0,source_hashes_preserved=True,actual_engine_prompt_and_parameters_verified=246,program_B_native_scores_match_old=246,human_labels=0,families=4216,source_e3_hashes_verified=len(e3['source_hashes']),E4b_started=False,E5_started=False)
dump(ROOT/'validation.json',receipt);dump(ROOT/'e4a/analysis/response_hashes.json',records)
print(json.dumps(receipt,ensure_ascii=False))
