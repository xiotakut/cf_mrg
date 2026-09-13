#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
gpu="$1"
source_name="pilot_m6_gpu$gpu"
run_name="pilot_m6_fixed_gpu$gpu"
while [[ ! -f "../logs/$source_name.exit" ]]; do sleep 20; done
python3 prepare_reuse.py "../runs/$source_name" "runs/$run_name" > "logs/$run_name.reuse.log"
set +e
CUDA_VISIBLE_DEVICES="$gpu" bash run.sh imedrag --config configs/imedrag_single_gpu.json --inputs "data/pilot_m6_gpu$gpu.jsonl" --run-dir "runs/$run_name" --workers 4 > "logs/$run_name.log" 2>&1
result=$?
printf '%s\n' "$result" > "logs/$run_name.exit"
set -e
[[ "$result" == 0 ]]
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python code/report.py --run-dir "runs/$run_name" --inputs "data/pilot_m6_gpu$gpu.jsonl" > "logs/$run_name.report.log" 2>&1
