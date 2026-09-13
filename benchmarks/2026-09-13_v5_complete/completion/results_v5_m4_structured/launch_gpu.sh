#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export CUDA_VISIBLE_DEVICES="$1"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1
exec /home/data3/txy/MedRGAG/.venv/bin/python -u code/worker.py "$1" >> "logs/gpu$1.log" 2>&1
