"""Borrow GPU0 with the existing guard; hand three disjoint shards back on yield."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

OUT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guard', OUT.parent/'results_v5_m0_m2_m4_m5/code/run_m4_gpu0_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
MOVED = {0: 1631150, 3: 1631156, 4: 1631158}


def report(**data):
    data['time'] = time.time()
    text = json.dumps(data)
    print(text, flush=True)
    (OUT/'gpu0_parallel_status.json').write_text(text+'\n')
    with (OUT/'gpu0_parallel_events.jsonl').open('a') as f:
        f.write(text+'\n')


def launch(shard, endpoint):
    with (OUT/f'run_{shard}_gpu0_resume.log').open('a') as log:
        return subprocess.Popen([sys.executable, '-u', str(OUT/'code/run_m3.py'),
            '--shard', str(shard), '--shards', '8', '--endpoint', endpoint],
            cwd=OUT, stdout=log, stderr=subprocess.STDOUT)


def main():
    plan = json.loads((OUT/'plan.json').read_text())
    ids = [iid for shard in plan['shards'] for iid in shard]
    pending = [json.loads(line)['item_id'] for line in (OUT/'pending_M3.jsonl').open()]
    assert len(ids) == len(set(ids)) == len(pending) and set(ids) == set(pending)
    reason = guard.check(min_free_gib=4)
    assert reason is None, reason
    for shard, pid in ({} if '--resume' in sys.argv else MOVED).items():
        proc = Path(f'/proc/{pid}')
        args = (proc/'cmdline').read_bytes().decode().split('\0')
        assert proc.stat().st_uid == os.getuid()
        assert 'code/run_m3.py' in args and args[args.index('--shard')+1] == str(shard)
    if '--check-only' in sys.argv:
        print('Exact disjoint coverage, original worker ownership and GPU0 guard passed.')
        return
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='0')
    command = [sys.executable, '-m', 'vllm.entrypoints.openai.api_server',
        '--model', '/home/data3/txy/models/Qwen3-8B', '--served-model-name', 'qwen3-8b',
        '--host', '127.0.0.1', '--port', '8010', '--dtype', 'bfloat16',
        '--max-model-len', '131072', '--max-num-seqs', '32', '--gpu-memory-utilization', '.9378',
        '--seed', '223', '--enable-prefix-caching', '--rope-scaling',
        '{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}']
    with (OUT/'services/qwen_0.log').open('a') as log:
        server = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                  start_new_session=True)
    (OUT/'services/qwen_0.pid').write_text(str(server.pid)+'\n')
    workers = {}
    borrowed = True
    try:
        report(status='loading', server_pid=server.pid)
        deadline = time.monotonic()+900
        while True:
            reason = guard.check(server.pid, min_free_gib=4)
            if reason or server.poll() is not None:
                raise RuntimeError(reason or f'GPU0 service exited {server.returncode}')
            try:
                with urllib.request.urlopen('http://127.0.0.1:8010/health', timeout=1) as r:
                    if r.status == 200:
                        break
            except Exception:
                pass
            if time.monotonic() > deadline:
                raise TimeoutError('GPU0 model startup')
            time.sleep(2)
        # Stop only these verified clients. The two existing model services,
        # retriever and other five shards remain running throughout handoff.
        for shard, pid in ({} if '--resume' in sys.argv else MOVED).items():
            os.kill(pid, signal.SIGTERM)
        for pid in ([] if '--resume' in sys.argv else MOVED.values()):
            while Path(f'/proc/{pid}').exists():
                time.sleep(.1)
        baseline = {iid for iid in pending if (OUT/'cache/items'/iid/'result.json').exists()}
        (OUT/('gpu0_memory_upgrade_81gib.json' if '--resume' in sys.argv else 'gpu0_handoff.json')).write_text(json.dumps(dict(
            time=time.time(), moved_shards=list(MOVED), completed_before=sorted(baseline),
            coverage='original 8 disjoint shards unchanged', memory_fraction=.9378, min_free_gib=4,
            old_controller='intentional client exits; this coordinator now finalizes'))+'\n')
        workers = {s: launch(s, 'http://127.0.0.1:8010/v1') for s in MOVED}
        report(status='running', server_pid=server.pid, workers={s:p.pid for s,p in workers.items()})
        while True:
            if borrowed:
                reason = guard.check(server.pid, min_free_gib=4)
                if reason or server.poll() is not None:
                    reason = reason or f'GPU0 service exited {server.returncode}'
                    # Free our GPU group first. Never signal incumbent PIDs.
                    guard.stop_group(server.pid)
                    server.wait()
                    for p in workers.values():
                        if p.poll() is None:
                            p.terminate()
                    for p in workers.values():
                        p.wait()
                    for s in workers:
                        failure = OUT/f'run_{s}_failure.json'
                        if failure.exists():
                            failure.replace(OUT/f'run_{s}_gpu0_yield_error.json')
                    workers = {s:launch(s, f'http://127.0.0.1:{8011+s%2}/v1') for s in MOVED}
                    borrowed = False
                    report(status='fallback', reason=reason, workers={s:p.pid for s,p in workers.items()})
            for shard, p in workers.items():
                if p.poll() not in (None, 0):
                    raise RuntimeError(f'Resumed shard {shard} exited {p.returncode}')
            failures = list(OUT.glob('run_*_failure.json'))
            if failures:
                raise RuntimeError(f'Worker failure files: {failures}')
            if all((OUT/'cache/items'/iid/'result.json').exists() for iid in pending):
                assert all((OUT/'cache/items'/iid/'result.json').exists() for iid in baseline)
                break
            time.sleep(2)
        for p in workers.values():
            assert p.wait() == 0
        guard.stop_group(server.pid)
        server.wait()
        (OUT/'finished_at.txt').write_text(time.strftime('%Y-%m-%dT%H:%M:%S%z')+'\n')
        with (OUT/'finish.log').open('a') as log:
            subprocess.run([sys.executable, str(OUT/'code/finish.py')], stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        report(status='complete')
    finally:
        guard.stop_group(server.pid)
        server.wait()


if __name__ == '__main__':
    main()
