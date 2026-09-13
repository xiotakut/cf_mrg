#!/usr/bin/env bash
set -euo pipefail
MEDRAG_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$MEDRAG_ROOT"
export HF_HOME="$MEDRAG_ROOT/.cache/huggingface"
export TMPDIR="$MEDRAG_ROOT/.cache/tmp"
export OMP_NUM_THREADS=8
export TOKENIZERS_PARALLELISM=false
MEDRAG_GPU_A="${MEDRAG_GPU_A:-1}"
MEDRAG_GPU_B="${MEDRAG_GPU_B:-2}"
MEDRAG_PIDS=()
for MEDRAG_ENCODER in contriever specter medcpt; do
    MEDRAG_GPU="$MEDRAG_GPU_A"
    if [[ "$MEDRAG_ENCODER" == medcpt ]]; then MEDRAG_GPU="$MEDRAG_GPU_B"; fi
    CUDA_VISIBLE_DEVICES="$MEDRAG_GPU" .venv/bin/python -u prepare_rrf4.py --encoder "$MEDRAG_ENCODER" \
        > ".cache/prepare-$MEDRAG_ENCODER.log" 2>&1 &
    MEDRAG_PIDS+=("$!")
    printf '%s pid=%s gpu=%s\n' "$MEDRAG_ENCODER" "$!" "$MEDRAG_GPU"
done
MEDRAG_STATUS=0
for MEDRAG_PID in "${MEDRAG_PIDS[@]}"; do
    wait "$MEDRAG_PID" || MEDRAG_STATUS=1
done
if [[ "$MEDRAG_STATUS" != 0 ]]; then
    printf 'Index preparation failed; inspect .cache/prepare-*.log\n'
    exit 1
fi
./run_baseline.sh --variant m4 --check > .cache/check-llama31.json
MEDRAG_RUN="runs/smoke_m4_full_$(date +%Y%m%d_%H%M%S).jsonl"
CUDA_VISIBLE_DEVICES="$MEDRAG_GPU_A" ./run_baseline.sh --variant m4 \
    --input examples/retrieval_smoke.jsonl --output "$MEDRAG_RUN" > .cache/smoke-llama31-full.log 2>&1
printf 'Completed: %s\n' "$MEDRAG_RUN" > .cache/rrf4-complete.txt
cat .cache/rrf4-complete.txt
