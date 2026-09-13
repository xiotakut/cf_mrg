#!/usr/bin/env bash
set -euo pipefail
cd /home/data3/txy/MA-RAG
OUT=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
export PYTHONPATH=/home/data3/txy/.cache/marag_pydeps
export TMPDIR=/home/data3/txy/.cache/marag_tmp
export JAVA_HOME=/home/data3/txy/.local/medrgag-jdk-21
export PATH="$JAVA_HOME/bin:$PATH"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
for GPU in 1 2; do
  CUDA_VISIBLE_DEVICES="$GPU" "$PYTHON" -m vllm.entrypoints.openai.api_server \
    --model /home/data3/txy/models/Qwen3-8B --served-model-name qwen3-8b \
    --host 127.0.0.1 --port "$((8010 + GPU))" --dtype bfloat16 \
    --max-model-len 131072 --max-num-seqs 32 --gpu-memory-utilization .75 \
    --seed 223 --enable-prefix-caching \
    --rope-scaling '{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}' \
    > "$OUT/services/qwen_$GPU.log" 2>&1 &
  printf '%s\n' "$!" > "$OUT/services/qwen_$GPU.pid"
done
CUDA_VISIBLE_DEVICES=1 "$PYTHON" \
  /home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/run_marag_retriever.py \
  --marag-repo /home/data3/txy/MA-RAG --retriever BM25 --reranker MedCPT-Cross-Encoder \
  --corpus-name MedCorp3 --cuda 0 --port 8993 > "$OUT/services/retriever.log" 2>&1 &
printf '%s\n' "$!" > "$OUT/services/retriever.pid"
wait
