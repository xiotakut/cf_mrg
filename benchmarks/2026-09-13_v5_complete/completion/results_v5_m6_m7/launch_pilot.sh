#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export CUDA_VISIBLE_DEVICES="$1"
method="$2"
inputs="$3"
run_name="$4"
set +e
bash run.sh "$method" --config "configs/${method}_single_gpu.json" --inputs "$inputs" --run-dir "runs/$run_name" --workers 4 --verify-backend >"logs/$run_name.log" 2>&1
result=$?
printf '%s\n' "$result" >"logs/$run_name.exit"
exit "$result"
