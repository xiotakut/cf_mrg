"""Run M4 on shared GPU 0; yield only our process group on external activity."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
GPU = 'GPU-14389c08-56d0-3988-fa42-24b42fbd723f'
PAUSED = {1202819, 1202820}


def state(pid):
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0]


def allowed(pid, group, process_group=os.getpgid, process_state=state):
    if group is not None and process_group(pid) == group:
        return True
    return pid in PAUSED and process_state(pid) in ('T', 't')


def check(group=None, min_free_gib=25):
    raw = subprocess.check_output([
        'nvidia-smi', '--query-compute-apps=gpu_uuid,pid',
        '--format=csv,noheader,nounits'], text=True, timeout=5)
    for line in raw.splitlines():
        gpu, pid = (v.strip() for v in line.split(','))
        if gpu != GPU:
            continue
        try:
            if not allowed(int(pid), group):
                return f'external GPU process active: {pid}'
        except (FileNotFoundError, ProcessLookupError):
            continue
    free = int(subprocess.check_output([
        'nvidia-smi', '-i', GPU, '--query-gpu=memory.free',
        '--format=csv,noheader,nounits'], text=True, timeout=5).strip())
    if free < min_free_gib * 1024:
        return f'free GPU memory below {min_free_gib} GiB: {free} MiB'
    # Also detect a resumed incumbent before its next GPU call appears.
    for pid in PAUSED:
        try:
            if state(pid) not in ('T', 't'):
                return f'incumbent resumed: {pid}'
        except FileNotFoundError:
            pass
    return None


def report(**values):
    values['time'] = time.time()
    print(json.dumps(values), flush=True)
    (ROOT/'M4/gpu0_guard.json').write_text(json.dumps(values, indent=2))


def stop_group(group):
    try:
        os.killpg(group, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(40):
        time.sleep(.2)
        try:
            os.killpg(group, 0)
        except ProcessLookupError:
            return
    try:
        os.killpg(group, signal.SIGKILL)
    except ProcessLookupError:
        pass


def main():
    if '--check-only' in sys.argv:
        assert allowed(9, 77, lambda p: 77, lambda p: 'R')
        assert allowed(1202819, 77, lambda p: 8, lambda p: 'T')
        assert not allowed(1202819, 77, lambda p: 8, lambda p: 'R')
        assert not allowed(123, 77, lambda p: 8, lambda p: 'T')
        reason = check()
        print(json.dumps({'guard_checks_passed': True, 'conflict': reason}))
        return 1 if reason else 0
    (ROOT/'M4').mkdir(exist_ok=True)
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    for phase, extra in [('smoke', ['--smoke', '--batch-size', '4']),
                         ('full', ['--batch-size', '16'])]:
        reason = check()
        if reason:
            report(status='yielded', reason=reason)
            return 2
        with (ROOT/f'm4_gpu0_{phase}.log').open('a') as log:
            child = subprocess.Popen([
                sys.executable, '-u', str(ROOT/'code/run_medrag.py'), 'M4',
                '--gpu-memory', '.50', *extra], stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True)
            report(status='running', phase=phase, pid=child.pid, gpu=GPU)
            try:
                while child.poll() is None:
                    reason = check(child.pid)
                    if reason:
                        report(status='yielded', phase=phase, reason=reason)
                        return 2
                    time.sleep(2)
                if child.returncode:
                    report(status='failed', phase=phase, exit_code=child.returncode)
                    return child.returncode
            finally:
                stop_group(child.pid)
                child.wait()
    report(status='complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
