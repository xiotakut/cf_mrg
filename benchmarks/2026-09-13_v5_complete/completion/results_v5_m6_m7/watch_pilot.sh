#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
while [[ ! -f logs/pilot_m6_gpu1.exit || ! -f logs/pilot_m6_gpu2.exit || ! -f logs/pilot_m7_gpu3.exit ]]; do
  python3 status.py > logs/status.tmp
  mv logs/status.tmp logs/status.json
  sleep 30
done
python3 status.py > logs/status.json
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python finish_pilot.py > logs/finish_pilot.log 2>&1
