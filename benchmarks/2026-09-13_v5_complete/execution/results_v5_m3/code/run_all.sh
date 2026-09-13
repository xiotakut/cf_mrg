#!/usr/bin/env bash
set -euo pipefail
cd /home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
export PYTHONPATH=/home/data3/txy/.cache/marag_pydeps
export TMPDIR=/home/data3/txy/.cache/marag_tmp
export JAVA_HOME=/home/data3/txy/.local/medrgag-jdk-21
export API_KEY=dummy RETRIEVER_HOST=http://127.0.0.1:8993
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONHASHSEED=223
"$PYTHON" -u - <<'PY'
import json,time,urllib.request
from pathlib import Path
assert json.loads(Path('plan.json').read_text())['status']=='frozen'
for port,path in [(8011,'/health'),(8012,'/health'),(8993,'/openapi.json')]:
    deadline=time.monotonic()+1800
    while True:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=3) as r:assert r.status==200
            break
        except Exception:
            if time.monotonic()>deadline:raise
            time.sleep(3)
    print('Ready:',port,flush=True)
PY
date -Is > started_at.txt
# Native format and longest-input probes become normal cached results.
"$PYTHON" -u code/run_m3.py --smoke --shard 0 --shards 2 > smoke_0.log 2>&1 &
A=$!
"$PYTHON" -u code/run_m3.py --smoke --shard 1 --shards 2 > smoke_1.log 2>&1 &
B=$!
wait "$A"
wait "$B"
"$PYTHON" -u code/audit_smoke.py > smoke_audit.log 2>&1
PIDS=()
for SHARD in 0 1 2 3 4 5 6 7; do
  (
    set +e
    "$PYTHON" -u code/run_m3.py --shard "$SHARD" --shards 8 > "run_$SHARD.log" 2>&1
    STATUS=$?
    printf '{"exit_code": %s}\n' "$STATUS" > "run_${SHARD}_exit.json"
    exit "$STATUS"
  ) &
  PIDS+=("$!")
done
printf '%s\n' "${PIDS[@]}" > worker_shell_pids.txt
STATUS=0
for PID in "${PIDS[@]}"; do wait "$PID" || STATUS=1; done
printf '{"exit_code": %s}\n' "$STATUS" > run_exit.json
if [[ "$STATUS" -ne 0 ]]; then exit "$STATUS"; fi
date -Is > finished_at.txt
"$PYTHON" -u code/finish.py > finish.log 2>&1
