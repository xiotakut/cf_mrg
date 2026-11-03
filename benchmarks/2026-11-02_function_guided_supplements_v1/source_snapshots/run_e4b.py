"""Durable batched execution of the fixed E4b paired instruction control."""
import argparse,json,sys,os,time,traceback,fcntl
from dataclasses import replace
from copy import deepcopy
from common import ROOT,WORK,DEP,rows,dump,sha,now
sys.path[:0]=[str(DEP),str(WORK)]
from cf_moa.tools import vllm_backend
vllm_backend.EXTRA_SITE=str(DEP)
from cf_moa.tools.native_backend import NativeBackend,profile
from cf_moa.contracts import digest
import jsonschema

def main(a):
 out=ROOT/'e4b';prep=json.load((out/'preparation.json').open());rt=json.load((out/'runtime.json').open())
 for path,h in prep['sources'].items():assert sha(path)==h,path
 ip=out/'inference'/f'{a.method.lower()}.jsonl';assert sha(ip)==prep['inference_hashes'][a.method]
 assert sha(out/'runtime.json')==prep['runtime_sha256']
 data=list(rows(ip));p=profile(a.method,'readout');cfg=deepcopy(p.config)
 cfg.update(gpu_memory_utilization=rt['gpu_memory_utilization'],max_model_len=rt['context'],max_num_seqs=rt['max_num_seqs'],max_num_batched_tokens=rt['max_num_batched_tokens'],batch_size=rt['batch_size'])
 cfg['model_kwargs']['num_gpu_blocks_override']=rt['blocks']
 b=NativeBackend(replace(p,config=cfg),load_model=False)
 run=out/('preflight' if a.preflight else 'runs')/a.method.lower();run.mkdir(parents=True,exist_ok=True)
 lock=(run/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 completed=[];start=time.monotonic()
 try:
  sizes=[]
  for r in data:
   assert digest(r['request'])==r['request_hash'];b.preflight(r['request']);sizes.append(b.count_tokens(r['request']))
  dump(run/'preflight.json',dict(status='passed',requests=len(data),max_input_tokens=max(sizes),new_model_requests=0,input_sha256=sha(ip),config=cfg))
  if a.preflight:return
  dump(run/'launch.json',dict(time=now(),pid=os.getpid(),method=a.method,config=cfg,gpu=os.environ.get('CUDA_VISIBLE_DEVICES')))
  pending=[]
  for r in data:
   f=run/'responses'/(r['request_id']+'.json')
   if f.exists():
    z=json.load(f.open());assert z['request_hash']==r['request_hash'];completed.append(z)
   else:
    assert not (run/'submitted'/(r['request_id']+'.json')).exists(),'Unknown prior submission: '+r['request_id']
    pending.append(r)
  b.start();dump(run/'engine_ready.json',dict(time=now(),initialization_seconds=b.initialization_seconds))
  for offset in range(0,len(pending),rt['batch_size']):
   if (out/'STOP').exists():raise RuntimeError('Operator stop before batch')
   batch=pending[offset:offset+rt['batch_size']]
   for r in batch:dump(run/'submitted'/(r['request_id']+'.json'),dict(time=now(),request_hash=r['request_hash']))
   result=b.generate_batch([r['request'] for r in batch]);physical=deepcopy(b.physical_calls);b.physical_calls.clear()
   assert len(physical)==len(batch)
   for r,z,ph in zip(batch,result,physical):
    native=None;error=None;usage=z.events[0]
    try:
     v=json.loads(z.value);jsonschema.validate(v,r['request']['schema']);native=v['native_answer']
     if usage['finish_reason']=='length':error='output_truncated';native=None
    except (ValueError,jsonschema.ValidationError) as exc:error=type(exc).__name__+': '+str(exc)
    saved=dict(method=a.method,request_id=r['request_id'],input_id=r['input_id'],arm=r['arm'],request_hash=r['request_hash'],shared_information_hash=r['shared_information_hash'],raw=z.value,native_answer=native,error=error,usage=usage,physical=ph,time=now())
    dump(run/'responses'/(r['request_id']+'.json'),saved);completed.append(saved)
   dump(run/'progress.json',dict(status='running',method=a.method,completed=len(completed),planned=160,errors=sum(r['error'] is not None for r in completed),input_tokens=sum(r['usage']['input_tokens'] for r in completed),output_tokens=sum(r['usage']['output_tokens'] for r in completed),time=now()))
   print(a.method,len(completed),'of 160',flush=True)
  dump(run/'terminal.json',dict(status='complete',completed=len(completed),elapsed_seconds=time.monotonic()-start,time=now()))
 except Exception:
  dump(run/'failure.json',dict(time=now(),traceback=traceback.format_exc(),completed=len(completed),physical=b.physical_calls));raise
 finally:
  if b.llm is not None:b.llm.llm_engine.engine_core.shutdown();dump(run/'cleanup.json',dict(status='complete',time=now()))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--method',choices=['M4','M5'],required=True);p.add_argument('--preflight',action='store_true');main(p.parse_args())
