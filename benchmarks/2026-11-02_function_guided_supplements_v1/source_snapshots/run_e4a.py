"""Finite frozen terminal control, no upstream model calls and no automatic retries."""
import argparse, json, sys, os, time, traceback, fcntl
from dataclasses import replace
from copy import deepcopy
from pathlib import Path
from common import ROOT,WORK,DEP,rows,dump,sha,now
sys.path[:0]=[str(DEP),str(WORK)]
from cf_moa.contracts import digest
from cf_moa.tools import vllm_backend
vllm_backend.EXTRA_SITE=str(DEP)
from cf_moa.tools.native_backend import NativeBackend,profile

OUT=ROOT/'e4a'
def backend():
    p=profile(args.method,'readout');c=deepcopy(p.config);rt=json.loads((OUT/'runtime.json').read_text())
    c.update(gpu_memory_utilization=rt['gpu_memory_utilization'],max_model_len=rt['context'],max_num_seqs=1,max_num_batched_tokens=4096,batch_size=1)
    c['model_kwargs']['num_gpu_blocks_override']=rt['blocks']
    return NativeBackend(replace(p,config=c,source=dict(old_readout=p.source,experiment='same_information_terminal_execution_v1')),load_model=False)

def main():
    prep=json.loads((OUT/'preparation.json').read_text());rt=json.loads((OUT/'runtime.json').read_text())
    assert sha(OUT/'runtime.json')==prep['runtime_sha256']
    for p,h in prep['sources'].items(): assert sha(p)==h,p
    ip=OUT/'inference'/f'{args.method.lower()}.jsonl';assert sha(ip)==prep['inference_hashes'][args.method]
    data=list(rows(ip));b=backend();started=time.monotonic();run=OUT/('preflight' if args.preflight else 'runs')/args.method.lower();run.mkdir(parents=True,exist_ok=True)
    lock=(run/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    completed=[]
    try:
        if args.preflight:
            sizes=[]
            for r in data:
                assert digest(r['request'])==r['request_hash'];n=b.count_tokens(r['request']);b.preflight(r['request']);sizes.append(n)
            dump(run/'receipt.json',dict(status='passed',method=args.method,requests=len(data),min_input_tokens=min(sizes),max_input_tokens=max(sizes),max_output_tokens=rt['max_tokens'],engine=b.adopted.engine_kwargs(),input_sha256=sha(ip),elapsed_seconds=time.monotonic()-started,new_model_requests=0))
            print(args.method,'preflight passed',max(sizes),flush=True);return
        prior=json.loads((OUT/'preflight'/args.method.lower()/'receipt.json').read_text());assert prior['status']=='passed' and prior['input_sha256']==sha(ip)
        dump(run/'launch.json',dict(time=now(),pid=os.getpid(),method=args.method,config=b.adopted.config,runtime_sha256=sha(OUT/'runtime.json')))
        b.start();dump(run/'engine_ready.json',dict(time=now(),initialization_seconds=b.initialization_seconds))
        for r in data:
            path=run/'responses'/(r['request_id']+'.json');pending=run/'submitted'/(r['request_id']+'.json')
            if path.exists():
                saved=json.loads(path.read_text());assert saved['request_hash']==r['request_hash'];completed.append(saved);continue
            if pending.exists():raise RuntimeError('Unknown prior submission; no retry: '+r['request_id'])
            if (OUT/'STOP').exists():raise RuntimeError('Operator stop before next request')
            dump(pending,dict(time=now(),request_hash=r['request_hash']))
            result=b(r['request']);usage=result.events[0];error=None;native=None
            try:
                import jsonschema
                parsed=json.loads(result.value);jsonschema.validate(parsed,r['request']['schema'])
                native=parsed['native_answer']
                if usage.get('finish_reason')=='length':error='output_truncated';native=None
            except (ValueError,jsonschema.ValidationError) as exc:error=type(exc).__name__+': '+str(exc)
            record=dict(method=args.method,request_id=r['request_id'],request_hash=r['request_hash'],shared_information_hash=r['shared_information_hash'],raw=result.value,native_answer=native,error=error,usage=usage,physical=deepcopy(b.physical_calls),new_model_requests=1,time=now())
            dump(path,record);completed.append(record);b.physical_calls.clear()
            dump(run/'progress.json',dict(method=args.method,status='running',completed=len(completed),planned=123,unavailable=sum(x['native_answer'] is None for x in completed),errors=sum(x['error'] is not None for x in completed),input_tokens=sum(x['usage']['input_tokens'] for x in completed),output_tokens=sum(x['usage']['output_tokens'] for x in completed),time=now()))
            print(args.method,len(completed),r['request_id'],'ok' if error is None else error,flush=True)
        dump(run/'terminal.json',dict(status='complete',method=args.method,completed=len(completed),planned=123,elapsed_seconds=time.monotonic()-started,time=now()))
    except Exception:
        dump(run/'failure.json',dict(time=now(),traceback=traceback.format_exc(),completed=len(completed)));raise
    finally:
        if b.llm is not None:
            b.llm.llm_engine.engine_core.shutdown()
            dump(run/'cleanup.json',dict(status='complete',time=now(),action='native_engine_core_shutdown'))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--method',choices=['M4','M5'],required=True);parser.add_argument('--preflight',action='store_true');args=parser.parse_args();main()
