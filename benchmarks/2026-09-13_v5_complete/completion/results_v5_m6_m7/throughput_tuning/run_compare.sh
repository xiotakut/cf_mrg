#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
gpu="$1"
method="$2"
model_pid="$3"
trap 'kill -CONT "$model_pid"' EXIT
kill -STOP "$model_pid"
export CUDA_VISIBLE_DEVICES="$gpu" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
set +e
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python bench_compare.py "$method" > "$method.compare.log" 2>&1
result=$?
printf '%s\n' "$result" > "$method.compare.exit"
exit "$result"
