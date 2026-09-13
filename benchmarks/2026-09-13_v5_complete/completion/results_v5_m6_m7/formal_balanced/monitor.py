"""Persist five-minute progress and GPU snapshots for the long benchmark run."""
import json
import subprocess
import time
from pathlib import Path
from status import status

ROOT = Path(__file__).resolve().parent


while True:
    snapshot = status()
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=index,memory.used,utilization.gpu',
                          '--format=csv,noheader'], capture_output=True, text=True)
    snapshot['gpu_snapshot'] = gpu.stdout
    snapshot['gpu_query_exit_code'] = gpu.returncode
    (ROOT / 'logs/status.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    with (ROOT / 'logs/supervision.jsonl').open('a') as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + '\n')
    if (ROOT / 'complete.json').exists() or any(
            m['jobs'].get('error', 0) for m in snapshot['methods'].values()):
        break
    time.sleep(300)
