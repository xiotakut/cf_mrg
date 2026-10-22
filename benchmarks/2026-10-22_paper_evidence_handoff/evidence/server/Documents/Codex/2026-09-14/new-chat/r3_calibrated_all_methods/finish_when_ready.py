"""Run the two pending CPU analyses after the existing GPU queues finish."""
import json
from pathlib import Path
import subprocess
import sys
import time

out = Path(__file__).resolve().parent
for gpu in (1, 3):
    path = out/f'runtime_gpu{gpu}.json'
    while (status := json.loads(path.read_text()))['status'] == 'running':
        time.sleep(15)
    assert status['status'] == 'complete', status
for name, command in (
    ('analysis', [sys.executable, '-u', str(out.parent/'r3_calibrated_all_methods.py'), 'analyze']),
    ('complete_head_replay', [sys.executable, '-u', str(out/'replay_complete_head.py')]),
):
    with (out/f'{name}.log').open('x') as log:
        subprocess.run(command, cwd=out.parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(name, 'complete', flush=True)
