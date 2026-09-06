#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
export PYTHONPATH="$PWD/results_cf_screening/runtime${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
case "${1:-}" in
  prepare)
    if [[ ! -f results_cf_screening/screening_items.jsonl ]]; then
      "$PYTHON" scripts/prepare_cf_baseline_screening.py
    fi
    "$PYTHON" scripts/run_cf_baseline_screening.py preflight
    ;;
  run)
    mkdir -p results_cf_screening/cache
    date -Is >> results_cf_screening/cache/batch_wall_times.txt
    CUDA_VISIBLE_DEVICES=1 "$PYTHON" -u scripts/run_cf_baseline_screening.py retrieval --shard-index 2 > results_cf_screening/retrieval.log 2>&1 &
    RETRIEVAL_PID=$!
    CUDA_VISIBLE_DEVICES=0 "$PYTHON" -u scripts/run_cf_baseline_screening.py run --shard-index 0 --shard-count 2 --batch-size 32 --chunk-size 32 --gpu-memory .45 > results_cf_screening/run_0.log 2>&1 &
    WORKER_ZERO_PID=$!
    CUDA_VISIBLE_DEVICES=2 "$PYTHON" -u scripts/run_cf_baseline_screening.py run --shard-index 1 --shard-count 2 --batch-size 32 --chunk-size 32 --gpu-memory .45 > results_cf_screening/run_1.log 2>&1 &
    WORKER_ONE_PID=$!
    STATUS=0
    wait "$WORKER_ZERO_PID" || STATUS=1
    wait "$WORKER_ONE_PID" || STATUS=1
    wait "$RETRIEVAL_PID" || STATUS=1
    date -Is >> results_cf_screening/cache/batch_wall_times.txt
    exit "$STATUS"
    ;;
  analyze)
    "$PYTHON" scripts/analyze_cf_baseline_screening.py "${@:2}"
    ;;
  *) echo 'Usage: bash scripts/cf_baseline_screening.sh prepare|run|analyze [--partial]' >&2; exit 2;;
esac
