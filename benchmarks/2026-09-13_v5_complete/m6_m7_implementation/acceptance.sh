#!/usr/bin/env bash
# Fixed development acceptance only; this script never runs the formal manifest.
set -euo pipefail
cd "$(dirname "$0")"
BASELINE_PY=/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python
export CUDA_VISIBLE_DEVICES=1,2

bash run.sh imedrag --config configs/imedrag_runtime_v4.json \
  --inputs data/dev_inputs.jsonl --run-dir runs/imedrag_dev_accepted --workers 4 \
  >> reports/imedrag_dev_accepted.log 2>&1

bash run.sh tcrag --config configs/tcrag_runtime_v4.json \
  --inputs data/dev_inputs.jsonl --run-dir runs/tcrag_dev --verify-backend --workers 4 \
  >> reports/tcrag_dev.log 2>&1
for DEV_RUN in runs/imedrag_dev_accepted runs/tcrag_dev; do
  "$BASELINE_PY" code/report.py --inputs data/dev_inputs.jsonl --run-dir "$DEV_RUN"
  "$BASELINE_PY" code/score.py --split dev --run-dir "$DEV_RUN"
done
"$BASELINE_PY" code/cost.py --run-dirs runs/imedrag_dev_accepted runs/tcrag_dev \
  > reports/formal_cost_estimate.log
"$BASELINE_PY" -c 'import json; from pathlib import Path; Path("reports/acceptance_execution_complete.json").write_text(json.dumps({"development_runs_complete":True,"formal_started":False,"blind_runs_started":False,"calibration_started":False})+"\n")'
