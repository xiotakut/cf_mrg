#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
while [[ ! -f m6_upstream_fix/runs/pilot_m6_fixed_gpu1/execution_report.json || ! -f m6_upstream_fix/runs/pilot_m6_fixed_gpu2/execution_report.json ]]; do
  for gpu in 1 2; do
    file="m6_upstream_fix/logs/pilot_m6_fixed_gpu$gpu.exit"
    if [[ -f "$file" && "$(cat "$file")" != 0 ]]; then exit 1; fi
  done
  sleep 30
done
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python finalize_fixed.py > logs/finalize_fixed.log 2>&1
