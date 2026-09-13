"""One GPU consumes disjoint frozen chunks, then helps the other method."""
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic


def claim(gpu):
    preferred = 'tcrag' if gpu == '3' else 'imedrag'
    with (ROOT / 'queue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        states = [json.loads(p.read_text()) for p in sorted((ROOT / 'jobs').glob('*.json'))]
        # An interrupted process resumes on its recorded GPU with the same config.
        owned = [r for r in states if r['state'] == 'running' and r['gpu'] == gpu]
        assert len(owned) <= 1
        pending = sorted((r for r in states if r['state'] == 'queued'),
                         key=lambda r: (r['method'] != preferred, r['name']))
        job = next(iter(owned or pending), None)
        if job:
            job.update(state='running', gpu=gpu, worker_pid=os.getpid())
            job.setdefault('started_at', datetime.now().astimezone().isoformat())
            atomic(ROOT / 'jobs' / (job['name'] + '.json'), job)
        return job


def main(gpu):
    assert gpu in ('1', '2', '3')
    with (ROOT / f'gpu{gpu}.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            job = claim(gpu)
            if job is None:
                subprocess.run([sys.executable, str(ROOT / 'finish.py')], check=True)
                return
            name, method = job['name'], job['method']
            execution = json.loads((ROOT / 'execution.json').read_text())[method]
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu)
            command = ['bash', str(ROOT / 'run.sh'), method, '--config',
                       str(ROOT / 'configs' / f'{method}_single_gpu.json'),
                       '--inputs', job['input_path'], '--run-dir', str(ROOT / 'runs' / name),
                       '--workers', str(execution['workers']), '--max-batch-tokens', str(execution['max_batch_tokens'])]
            with (ROOT / 'logs' / f'{name}.log').open('a') as log:
                result = subprocess.run(command, env=env, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            job.update(inference_exit_code=result.returncode)
            if result.returncode == 0:
                with (ROOT / 'logs' / f'{name}.report.log').open('a') as log:
                    result = subprocess.run([sys.executable, str(ROOT / 'code/report.py'),
                        '--run-dir', str(ROOT / 'runs' / name), '--inputs', job['input_path']],
                        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                job['report_exit_code'] = result.returncode
            job.update(state='done' if result.returncode == 0 else 'error',
                       finished_at=datetime.now().astimezone().isoformat())
            atomic(ROOT / 'jobs' / f'{name}.json', job)
            print(json.dumps(job), flush=True)
            if result.returncode:
                raise SystemExit(result.returncode)


if __name__ == '__main__':
    main(sys.argv[1])
