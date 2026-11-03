"""Finite new-family confirmation with unchanged C0/F/Gen/RulePrompt policies.

Replay the saved call frontier to batch independent inputs. A submitted call
without a durable response is never automatically resubmitted.
"""
import argparse,json,sys,time,os,fcntl,traceback
from copy import deepcopy
from dataclasses import replace
from common import ROOT,WORK,DEP,rows,dump,sha,now
sys.path[:0]=[str(DEP),str(WORK)]
from cf_moa.contracts import InputPacket,Budget,ModelResult,digest
from cf_moa.tools import vllm_backend
vllm_backend.EXTRA_SITE=str(DEP)
from cf_moa.tools.vllm_backend import sampling_snapshot
from cf_moa.tools.native_backend import NativeBackend,profile
from cf_moa.tools.adapters import ModelSession
from cf_moa.evaluation import c0_native
from cf_moa.agents import a5_robust_readout,post_proposers
from cf_moa.controller import post_selective

class CapacityError(ValueError):pass

class ConfirmationBackend(NativeBackend):
 def __init__(self,selected,method):
  super().__init__(selected,load_model=False);self.c0=c0_native.profile(method)
 def prepare(self,request):
  if 'model_config' not in request:
   try:return super().prepare(request)
   except ValueError as error:
    if 'exceeds selected capacity' in str(error):raise CapacityError(str(error)) from error
    raise
  assert request==self.c0.request(request['messages'],request['schema']),'Original C0 policy changed'
  prompt=self.tokenizer.apply_chat_template(request['messages'],tokenize=False,add_generation_prompt=True,**self.c0.config.get('chat_template_kwargs',{}))
  if len(self.tokenizer.encode(prompt))+request['max_tokens']>self.adopted.config['max_model_len']:
   raise CapacityError('Complete C0 input exceeds runtime capacity; no truncation')
  params=self.SamplingParams(**{k:request[k] for k in ('seed','temperature','top_p','top_k','max_tokens')},guided_decoding=self.Guided(json=request['schema'],backend='xgrammar') if self.c0.config['guided_json'] else None)
  return dict(engine_kwargs=self.adopted.engine_kwargs(),prompt=prompt,sampling_params=sampling_snapshot(params),use_tqdm=False),params

class NeedCallback(Exception):
 def __init__(self,task):self.task=task

class Frontier:
 def __init__(self,run,rid,engine):
  self.run,self.rid,self.engine=run,rid,engine;self.index=0;self.phase='C0';self.used=[]
 def count_tokens(self,request):
  h=digest(request)
  if h not in self.engine.token_cache:self.engine.token_cache[h]=self.engine.count_tokens(request)
  return self.engine.token_cache[h]
 def __call__(self,request):
  index=self.index;self.index+=1;key=f'{self.rid}_{index:02d}'
  path=self.run/'calls'/(key+'.json');h=digest(request)
  if path.exists():
   saved=json.load(path.open());assert saved['request_hash']==h,(key,'request changed across frontier')
   self.used.append(key)
   event=dict(saved['usage'],mode='replay')
   return ModelResult(saved['value'],[event])
  if (self.run/'submitted'/(key+'.json')).exists():raise RuntimeError('Unknown prior submission, no retry: '+key)
  raise NeedCallback(dict(key=key,request_id=self.rid,index=index,phase=self.phase,request=request,request_hash=h))

def packet(data):
 values=deepcopy(data['packet']);values['budget']=Budget(**values['budget']);return InputPacket(**values)

def pipeline(data,backend,method):
 p=packet(data);backend.phase='C0';s=ModelSession(p,backend)
 assert c0_native.request(p,method)==data['c0_request']
 c0=c0_native.run(p,s,method)
 n=c0['native_answer'];initial=n.get('answer_choice') if isinstance(n,dict) else n
 p=replace(p,baseline_answer=initial,baseline_response=c0['raw_response'])
 backend.phase='F';s=ModelSession(p,backend)
 f=a5_robust_readout.run_legacy(p,s)
 component=dict(input_hash=p.input_hash,method=method,role='A5',request_id=p.request_id,native_answer=f.native_proposal,native_hash=digest(f.native_proposal),status='complete' if f.native_proposal is not None else 'unavailable',trace=f.trace,source_ref=dict(kind='current_run_F',request_id=p.request_id,native_hash=digest(f.native_proposal)))
 pool=post_proposers.collect_cached(p,method=method,c0_native=n,components={'A5':component})
 answers={'C0':n,'B':f.native_proposal};aggregation={}
 for mode,name in [('gen','Gen'),('rule_prompt','RulePrompt')]:
  backend.phase=name;s=ModelSession(p,backend);req=post_selective.request(p,pool,mode=mode)
  try:
   raw=s.invoke(req,stage=name)
   # As in the existing aggregator, any length stop is unavailable even if a prefix parses.
   length=any(c.get('event',{}).get('finish_reason')=='length' for c in s.calls)
   result=post_selective.resolve(p,pool,raw=raw,mode=mode,aggregation_error='output_truncated' if length else None)
  except CapacityError as error:
   result=post_selective.resolve(p,pool,raw='',mode=mode,aggregation_error=str(error))
  answers[name]=result['native_answer'];aggregation[name]=result
 return dict(method=method,request_id=p.request_id,input_hash=p.input_hash,arms=answers,
    C0=c0,F=f.to_dict(),pool=pool,aggregations=aggregation,
    computation='C0 and F generated once in this run; same completed pool reused by both aggregators; frontier replay is scheduling, not extra inference.',time=now())

def placeholder(schema):
 if schema is None:return None
 if 'enum' in schema:return schema['enum'][0]
 if 'anyOf' in schema:return placeholder(schema['anyOf'][0])
 typ=schema.get('type')
 if typ=='object':return {k:placeholder(v) for k,v in schema.get('properties',{}).items()}
 if typ=='array':return [placeholder(schema['items']) for _ in range(schema.get('minItems',0))]
 if typ=='string':return 'CPU-only placeholder'
 if typ in ('number','integer'):return schema.get('minimum',0)
 if typ=='boolean':return False
 return None

class DryFrontier:
 def __init__(self,engine,data):self.engine=engine;self.data=data;self.phase='C0';self.count=0;self.max_tokens=0
 def count_tokens(self,request):return self.engine.count_tokens(request)
 def __call__(self,request):
  self.engine.preflight(request);tokens=self.count_tokens(request);self.max_tokens=max(self.max_tokens,tokens);self.count+=1
  if request['kind']=='score':value={code:float(-i) for i,code in enumerate(request['allowed_codes'])}
  elif 'model_config' in request:value=json.dumps(placeholder(self.data['packet']['answer_schema']))
  elif request.get('schema') is None:value='CPU-only intermediate analysis placeholder.'
  else:value=json.dumps(placeholder(request['schema']))
  return ModelResult(value,[dict(mode='replay',model='CPU-synthetic-no-inference',config_hash='cpu',input_tokens=tokens,output_tokens=0,elapsed_seconds=0,finish_reason='stop')])

def main(a):
 out=ROOT/'e5';prep=json.load((out/'preparation.json').open());rt=json.load((out/'runtime.json').open())
 for path,h in prep['sources'].items():assert sha(path)==h,path
 ip=out/'inference'/f'{a.method.lower()}.jsonl';assert sha(ip)==prep['inference_hashes'][a.method]
 assert sha(out/'runtime.json')==prep['runtime_sha256']
 data=list(rows(ip));p=profile(a.method,'readout');cfg=deepcopy(p.config)
 cfg.update(gpu_memory_utilization=rt['gpu_memory_utilization'],max_model_len=rt['context'],max_num_seqs=rt['max_num_seqs'],max_num_batched_tokens=rt['max_num_batched_tokens'],batch_size=rt['batch_size'])
 cfg['model_kwargs']['num_gpu_blocks_override']=rt['blocks']
 b=ConfirmationBackend(replace(p,config=cfg),a.method);b.token_cache={}
 run=out/('preflight' if a.preflight else 'runs')/a.method.lower();run.mkdir(parents=True,exist_ok=True)
 lock=(run/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 start=time.monotonic();done=set()
 try:
  if a.preflight:
   checks=[]
   for item in data:
    dry=DryFrontier(b,item);result=pipeline(item,dry,a.method)
    assert set(result['arms'])=={'C0','B','Gen','RulePrompt'}
    checks.append(dict(request_id=item['packet']['request_id'],synthetic_callbacks=dry.count,max_input_tokens=dry.max_tokens))
   dump(run/'receipt.json',dict(status='passed',time=now(),checks=checks,new_model_requests=0,synthetic_only=True,input_sha256=sha(ip),config=cfg));print(a.method,'CPU preflight passed',len(checks),flush=True);return
  pre=json.load((out/'preflight'/a.method.lower()/'receipt.json').open());assert pre['status']=='passed' and pre['input_sha256']==sha(ip)
  dump(run/'launch.json',dict(time=now(),pid=os.getpid(),method=a.method,config=cfg,input_sha256=sha(ip),gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),script_sha256=sha(__file__)))
  for item in data:
   rid=item['packet']['request_id'];f=run/'results'/(rid+'.json')
   if f.exists():
    saved=json.load(f.open());assert saved['frozen_packet_hash']==digest(item);done.add(rid)
  b.start();dump(run/'engine_ready.json',dict(time=now(),initialization_seconds=b.initialization_seconds))
  while len(done)<len(data):
   if (out/'STOP').exists():raise RuntimeError('Operator stop before next batch')
   tasks=[]
   for item in data:
    rid=item['packet']['request_id']
    if rid in done:continue
    front=Frontier(run,rid,b)
    try:
     result=pipeline(item,front,a.method)
     result.update(frozen_packet_hash=digest(item),physical_call_keys=front.used)
     dump(run/'results'/(rid+'.json'),result);done.add(rid)
    except NeedCallback as needed:tasks.append(needed.task)
    if len(tasks)>=rt['batch_size']:break
   if tasks:
    for task in tasks:
     b.preflight(task['request'])
     dump(run/'submitted'/(task['key']+'.json'),dict(time=now(),request_hash=task['request_hash'],phase=task['phase']))
    results=b.generate_batch([task['request'] for task in tasks]);physical=deepcopy(b.physical_calls);b.physical_calls.clear()
    assert len(physical)==len(tasks)
    for task,result,actual in zip(tasks,results,physical):
     dump(run/'calls'/(task['key']+'.json'),dict(**task,value=result.value,usage=result.events[0],physical=actual,time=now()))
   calls=list((run/'calls').glob('*.json'))
   dump(run/'progress.json',dict(status='running',method=a.method,complete_inputs=len(done),planned_inputs=112,physical_calls=len(calls),time=now()))
   print(a.method,'inputs',len(done),'of112; calls',len(calls),flush=True)
  costs=[json.load(p.open()) for p in (run/'calls').glob('*.json')]
  dump(run/'terminal.json',dict(status='complete',time=now(),completed=len(done),physical_calls=len(costs),input_tokens=sum(x['usage']['input_tokens'] for x in costs),output_tokens=sum(x['usage']['output_tokens'] for x in costs),elapsed_seconds=time.monotonic()-start))
 except Exception:
  dump(run/'failure.json',dict(time=now(),traceback=traceback.format_exc(),completed=len(done),physical=b.physical_calls));raise
 finally:
  if b.llm is not None:b.llm.llm_engine.engine_core.shutdown();dump(run/'cleanup.json',dict(status='complete',time=now()))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--method',choices=['M4','M5'],required=True);p.add_argument('--preflight',action='store_true');main(p.parse_args())
