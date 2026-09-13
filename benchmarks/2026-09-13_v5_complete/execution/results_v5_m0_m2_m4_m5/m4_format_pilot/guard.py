"""Run only the isolated pilot under the established shared-GPU protection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from run_m4_gpu0_guard import check, stop_group

out = ROOT / ('m4_format_structured_pilot' if '--structured' in sys.argv else 'm4_format_pilot')
out.mkdir(exist_ok=True)
reason = check()
if reason:
    raise SystemExit(reason)
env = dict(os.environ, CUDA_VISIBLE_DEVICES='0', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1')
with (out / 'inference.log').open('a') as log:
    child = subprocess.Popen([sys.executable, '-u', str(ROOT / 'code/m4_format_pilot.py'), *sys.argv[1:]], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    reason = None
    try:
        while child.poll() is None:
            reason = check(child.pid)
            if reason:
                break
            time.sleep(2)
    finally:
        stop_group(child.pid)
        child.wait()
    (out / 'guard_result.json').write_text(json.dumps(dict(exit_code=child.returncode, yield_reason=reason, time=time.time()), indent=2))
