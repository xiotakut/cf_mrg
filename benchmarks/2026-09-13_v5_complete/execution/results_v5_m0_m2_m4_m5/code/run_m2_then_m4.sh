#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
source "$TASK_ROOT/code/env.sh"
export CUDA_VISIBLE_DEVICES=1
RUN_PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
SMOKE_PID=$($RUN_PYTHON -c 'import json,sys;print(json.load(open(sys.argv[1]))["pid"])' "$TASK_ROOT/M2/started.json")
while kill -0 "$SMOKE_PID" 2>/dev/null; do sleep 15; done
test -f "$TASK_ROOT/M2/smoke_complete.json"
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_llama.py" M2 --batch-size 64 --gpu-memory .75 > "$TASK_ROOT/m2_full.log" 2>&1
MEDRAG_ROOT=/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag
export JAVA_HOME=/home/data3/txy/.cache/jdk/temurin21
export PATH="$JAVA_HOME/bin:$PATH"
export HF_HOME="$MEDRAG_ROOT/.cache/huggingface"
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_medrag.py" M4 --smoke --batch-size 4 --gpu-memory .55 > "$TASK_ROOT/m4_smoke.log" 2>&1
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_medrag.py" M4 --batch-size 16 --gpu-memory .55 > "$TASK_ROOT/m4_full.log" 2>&1
