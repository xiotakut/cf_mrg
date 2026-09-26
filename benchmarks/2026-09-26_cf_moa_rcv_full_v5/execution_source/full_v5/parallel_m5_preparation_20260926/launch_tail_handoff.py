"""One explicit three-card handoff; no retry, scientific edits or general queue."""
import json
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime

W = Path('/home/data3/txy')
PY = W/'MedRGAG/.venv/bin/python'
FULL = W/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/full_v5'
OLD = FULL/'readout_parallel_m5_20260926'
NEW = FULL/'readout_tail_gpu123_20260926'
LAUNCHER = Path(__file__).with_name('launch_shard.py')
HOLDERS = {
    2: (3823439, 3853788, OLD/'gpu2_recovery1/restored_holders/gpu2'),
    1: (3861584, 3861589, OLD/'gpu1/restored_holders/gpu1'),
    3: (3863369, 3863374, OLD/'gpu3/restored_holders/gpu3'),
}


def now():
    return datetime.now().astimezone().isoformat()


def save(name, value):
    path = NEW/name
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(path)


def identity(pid, state):
    p = Path('/proc')/str(pid)
    uid = p.stat().st_uid
    command = (p/'cmdline').read_bytes().replace(b'\0', b' ').decode()
    stat = (p/'stat').read_text().rsplit(')', 1)[1].split()
    if uid != os.getuid() or '/.local/bin/gpu_watch.py' not in command or str(state) not in command:
        raise ValueError('Owned reservation identity changed: '+str(pid))
    return dict(pid=pid, uid=uid, command=command, start_ticks=stat[19])


def ended(pid):
    p = Path('/proc')/str(pid)/'stat'
    try:
        return p.read_text().rsplit(')', 1)[1].split()[0] == 'Z'
    except FileNotFoundError:
        return True


def restore_waiter(gpu):
    state = NEW/f'gpu{gpu}/handoff_capacity_wait'
    state.mkdir()
    command = [str(PY), '-u', str(W/'.local/bin/gpu_watch.py'), '--state-dir', str(state),
        '--only-gpu', str(gpu), '--min-free-gib', '50', '--gib', '60', '--hold-hours', '0',
        '--wait-hours', '0', '--interval', '5', '--log-interval', '300', '--max-cards', '1',
        '--torch-python', str(PY)]
    with (state/'watch.log').open('x') as log:
        p = subprocess.Popen(command, cwd=W, stdin=subprocess.DEVNULL, stdout=log,
            stderr=subprocess.STDOUT, start_new_session=True)
    return dict(pid=p.pid, state=str(state), command=command)


def main():
    import sys
    sys.path.insert(0, str(W))
    from cf_moa.evaluation.run_moa_rcv import load_plan, selected_profile
    from partial_prefix_transfer import sha, DB06
    if sha(W/'cf_moa/evaluation/run_moa_rcv_batched.py') != DB06:
        raise ValueError('Original scheduler changed')
    if sha(LAUNCHER) != 'e99f59747c13c5dcd44dc1cd3eb382b9f622a8030dc9a40d9c5f1dbc04b2bb95':
        raise ValueError('Original launcher changed')
    if sha(W/'.local/bin/gpu_watch.py') != 'a6ef2550000a72d3fa558b48f0e665d4861a29204d0a8898ef97ef1105913ec0':
        raise ValueError('Original reservation script changed')
    receipt = json.loads((NEW/'transfer_receipt.json').read_text())
    if receipt['status'] != 'resource_shards_prepared_not_launched' or not receipt['source_SQL_unchanged']:
        raise ValueError('Transfer not ready')
    if (NEW/'handoff_intent.json').exists():
        raise ValueError('This explicit handoff was already attempted; do not retry')
    entries = []
    for gpu, (watch, holder, state) in HOLDERS.items():
        shard = next(s for s in receipt['shards'] if s['gpu'] == gpu)
        plan = Path(shard['plan'])
        if sha(plan) != shard['plan_sha256'] or (Path(shard['output'])/'launch.json').exists():
            raise ValueError('Changed or already launched shard')
        parsed, selected, packets, pools, bases, tasks = load_plan(plan, 'M5')
        if parsed['allowed_gpus'] != [gpu] or len(tasks) != shard['tasks']:
            raise ValueError('Actual loader task/GPU identity differs')
        entries.append(dict(gpu=gpu, processes=[identity(watch, state), identity(holder, state)],
            state=str(state), plan=str(plan), tasks=len(tasks), output=shard['output']))
    intent = dict(at=now(), entries=entries, source_receipt_sha256=sha(NEW/'transfer_receipt.json'),
        configuration_hash=selected_profile('M5', 'readout').config_hash,
        launcher_sha256=sha(LAUNCHER), automatic_retry=False, general_autoqueue_enabled=False)
    with (NEW/'handoff_intent.json').open('x') as stream:
        json.dump(intent, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    results = []
    for entry in entries:
        gpu = entry['gpu']; state = Path(entry['state'])
        for expected in entry['processes']:
            if identity(expected['pid'], state) != expected:
                raise ValueError('Reservation process identity changed before STOP')
        (state/'STOP').write_text('User explicitly authorizes fixed M5 tail on GPU1/2/3.\n')
        started = time.monotonic()
        while not all(ended(p['pid']) for p in entry['processes']):
            if time.monotonic()-started > 30:
                raise RuntimeError('Owned holder did not finish; no model launched on GPU '+str(gpu))
            time.sleep(.2)
        free = int(subprocess.check_output(['nvidia-smi', '-i', str(gpu),
            '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).strip())
        result = dict(gpu=gpu, at=now(), free_MiB=free, model_launches=0)
        if free < 61440:
            result.update(status='capacity_not_ready', reservation=restore_waiter(gpu))
        else:
            command = [str(PY), '-u', str(LAUNCHER), '--transfer',
                str(NEW/'transfer_receipt.json'), '--gpu', str(gpu)]
            with (NEW/f'gpu{gpu}/supervisor.stdout.log').open('x') as log:
                p = subprocess.Popen(command, cwd=W, stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            result.update(status='supervisor_submitted_not_yet_inference', pid=p.pid,
                command=command, model_launches=1)
        results.append(result)
        save('handoff_result.json', dict(at=now(), entries=results, external_process_actions=0))
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
