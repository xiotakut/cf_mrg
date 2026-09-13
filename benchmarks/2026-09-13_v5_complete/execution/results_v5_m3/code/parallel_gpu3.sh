#!/usr/bin/env bash
set -euo pipefail
cd /home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3
export PYTHONPATH=/home/data3/txy/.cache/marag_pydeps
export TMPDIR=/home/data3/txy/.cache/marag_tmp
export JAVA_HOME=/home/data3/txy/.local/medrgag-jdk-21
export API_KEY=dummy RETRIEVER_HOST=http://127.0.0.1:8993
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONHASHSEED=223
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
exec /home/data3/txy/MedRGAG/.venv/bin/python -u code/parallel_gpu3.py "$@" >> gpu3_parallel.log 2>&1
