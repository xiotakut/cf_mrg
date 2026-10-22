import json
import subprocess
import time
from prepare_v5 import OUT, dump
from status import status

while True:
    snapshot = status()
    gpu = subprocess.run(['nvidia-smi', '--query-gpu=index,memory.used,memory.total,utilization.gpu',
                          '--format=csv,noheader'], capture_output=True, text=True)
    snapshot['gpu_snapshot'] = gpu.stdout
    dump(OUT / 'logs/status.json', snapshot)
    with (OUT / 'logs/supervision.jsonl').open('a') as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + '\n')
    if (OUT / 'complete.json').exists():
        break
    time.sleep(300)
