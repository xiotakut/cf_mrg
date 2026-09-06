#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
RESULTS=${CF_SCREENING_OUTPUT:-results_cf_screening}
export PYTHONPATH="$PWD/$RESULTS/runtime${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
case "${1:-}" in
  prepare)
    if [[ ! -f "$RESULTS"/screening_items.jsonl ]]; then
      "$PYTHON" scripts/prepare_cf_baseline_screening.py "${@:2}"
    fi
    "$PYTHON" scripts/run_cf_baseline_screening.py preflight
    ;;
  run)
    mkdir -p "$RESULTS"/cache
    date -Is >> "$RESULTS"/cache/batch_wall_times.txt
    CUDA_VISIBLE_DEVICES=1 "$PYTHON" -u scripts/run_cf_baseline_screening.py retrieval --shard-index 2 > "$RESULTS"/retrieval.log 2>&1 &
    RETRIEVAL_PID=$!
    CUDA_VISIBLE_DEVICES=0 "$PYTHON" -u scripts/run_cf_baseline_screening.py run --shard-index 0 --shard-count 2 --batch-size 32 --chunk-size 32 --gpu-memory .50 > "$RESULTS"/run_0.log 2>&1 &
    WORKER_ZERO_PID=$!
    CUDA_VISIBLE_DEVICES=2 "$PYTHON" -u scripts/run_cf_baseline_screening.py run --shard-index 1 --shard-count 2 --batch-size 32 --chunk-size 32 --gpu-memory .50 > "$RESULTS"/run_1.log 2>&1 &
    WORKER_ONE_PID=$!
    STATUS=0
    wait "$WORKER_ZERO_PID" || STATUS=1
    wait "$WORKER_ONE_PID" || STATUS=1
    wait "$RETRIEVAL_PID" || STATUS=1
    date -Is >> "$RESULTS"/cache/batch_wall_times.txt
    if [[ "$STATUS" -eq 0 ]]; then
      CUDA_VISIBLE_DEVICES=2 "$PYTHON" -u scripts/run_cf_baseline_screening.py repeat --batch-size 32 --chunk-size 20 --gpu-memory .50 > "$RESULTS"/repeat_independent.log 2>&1 || STATUS=1
    fi
    exit "$STATUS"
    ;;
  analyze)
    "$PYTHON" scripts/analyze_cf_baseline_screening.py "${@:2}"
    ;;
  *) echo 'Usage: bash scripts/cf_baseline_screening.sh prepare|run|analyze [--partial]' >&2; exit 2;;
esac
