#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
source "$TASK_ROOT/code/env.sh"
export CUDA_VISIBLE_DEVICES=2
RUN_PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_llama.py" M0 --smoke --batch-size 4 --gpu-memory .55 > "$TASK_ROOT/m0_native_smoke.log" 2>&1
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_llama.py" M0 --batch-size 16 --gpu-memory .55 > "$TASK_ROOT/m0_full.log" 2>&1
export JAVA_HOME=/home/data3/txy/.cache/jdk/temurin21
export PATH="$JAVA_HOME/bin:$PATH"
export HF_HOME=/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.cache/huggingface
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_medrag.py" M5 --smoke --batch-size 4 --gpu-memory .55 > "$TASK_ROOT/m5_smoke.log" 2>&1
"$RUN_PYTHON" -u "$TASK_ROOT/code/run_medrag.py" M5 --batch-size 16 --gpu-memory .55 > "$TASK_ROOT/m5_full.log" 2>&1
