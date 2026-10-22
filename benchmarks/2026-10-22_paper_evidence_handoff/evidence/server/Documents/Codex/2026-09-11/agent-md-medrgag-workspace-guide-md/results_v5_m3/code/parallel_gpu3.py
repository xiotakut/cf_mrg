"""Move three original disjoint M3 shards onto newly released GPU3."""
import json, os, signal, subprocess, sys, time, urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
MOVED={1:1631152,2:1631154,5:1631161}
GPU='GPU-b8407209-7d9e-2c18-d39f-f5f8a3eeb1e4'
raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],text=True)
assert GPU not in raw, 'GPU3 is no longer empty'
plan=json.loads((OUT/'plan.json').read_text())
ids=[x for shard in plan['shards'] for x in shard]
assert len(ids)==len(set(ids))==plan['pending']
for shard,pid in MOVED.items():
    p=Path(f'/proc/{pid}');args=(p/'cmdline').read_bytes().decode().split('\0')
    assert p.stat().st_uid==os.getuid() and 'code/run_m3.py' in args and args[args.index('--shard')+1]==str(shard)
if '--check-only' in sys.argv:
    print('GPU3 empty; worker ownership and unchanged disjoint shards verified.')
    sys.exit(0)
command=[sys.executable,'-m','vllm.entrypoints.openai.api_server',
    '--model','/home/data3/txy/models/Qwen3-8B','--served-model-name','qwen3-8b',
    '--host','127.0.0.1','--port','8013','--dtype','bfloat16',
    '--max-model-len','131072','--max-num-seqs','32','--gpu-memory-utilization','.75',
    '--seed','223','--enable-prefix-caching','--rope-scaling',
    '{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}']
with (OUT/'services/qwen_3.log').open('a') as log:
    server=subprocess.Popen(command,env=dict(os.environ,CUDA_VISIBLE_DEVICES='3'),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(OUT/'services/qwen_3.pid').write_text(str(server.pid)+'\n')
print(json.dumps(dict(status='loading',server_pid=server.pid,time=time.time())),flush=True)
for _ in range(450):
    assert server.poll() is None, f'GPU3 server exited {server.returncode}'
    try:
        with urllib.request.urlopen('http://127.0.0.1:8013/health',timeout=1) as r:
            if r.status==200:break
    except Exception:pass
    time.sleep(2)
else:
    server.terminate()
    raise TimeoutError('GPU3 service startup')
for pid in MOVED.values():os.kill(pid,signal.SIGTERM)
for pid in MOVED.values():
    while Path(f'/proc/{pid}').exists():time.sleep(.1)
workers={}
for shard in MOVED:
    with (OUT/f'run_{shard}_gpu3_resume.log').open('a') as log:
        workers[shard]=subprocess.Popen([sys.executable,'-u',str(OUT/'code/run_m3.py'),
            '--shard',str(shard),'--shards','8','--endpoint','http://127.0.0.1:8013/v1'],
            cwd=OUT,stdout=log,stderr=subprocess.STDOUT)
record=dict(status='running',server_pid=server.pid,workers={s:p.pid for s,p in workers.items()},
    time=time.time(),completed_before=sum(1 for p in (OUT/'cache/items').glob('*/result.json')),
    coverage='Original eight disjoint ID lists unchanged; GPU0 coordinator retains finalization')
(OUT/'gpu3_handoff.json').write_text(json.dumps(record)+'\n')
print(json.dumps(record),flush=True)
for shard,p in workers.items():
    code=p.wait()
    if code:raise RuntimeError(f'GPU3 shard {shard} exited {code}')
print(json.dumps(dict(status='workers_complete',time=time.time())),flush=True)
# Existing GPU0 coordinator audits all IDs, then finish.py releases this server.
server.wait()
