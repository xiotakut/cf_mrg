#!/usr/bin/env bash
set -euo pipefail
PY=/home/data3/txy/MedRGAG/.venv/bin/python
MODEL=/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
OUT=results_riskroute
CACHE=results_cfmoe/cache/riskroute
TMPDIR=/home/data3/txy/.cache/riskroute_tmp
mkdir -p "$TMPDIR"
export TMPDIR

$PY scripts/run_riskroute.py smoke
$PY scripts/run_riskroute.py fit
# router_models.json is frozen before the next command reads official unseen test rows.
$PY scripts/run_riskroute.py prepare-test

pids=()
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py baseline --data "$OUT/new_test.jsonl"     --output-dir "$CACHE/baseline" --model "$MODEL" --shard-index "$i" --shard-count 2     --gpu-memory-utilization .55 &
  pids+=("$!")
done
CUDA_VISIBLE_DEVICES=2 $PY scripts/run_cfshift.py match --data "$OUT/new_test.jsonl"   --evidences private_data/deltarank_sources/release_evidences.json   --output "$CACHE/matches.test.jsonl" --device cuda:0 &
pids+=("$!")
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfshift.py merge --inputs "$CACHE"/baseline/shard-*/baseline.jsonl   --output "$CACHE/baseline.test.jsonl"

CUDA_VISIBLE_DEVICES=2 $PY scripts/run_cfmoe.py documents --data "$OUT/new_test.jsonl"   --cache-root "$CACHE/baseline" --output "$CACHE/document_scores.test.jsonl" --device cuda:0

# Runtime note: an isolated initial 2-shard debug run wrote 120 rows under cache/riskroute/option
# and was intentionally stopped after documents completed. It is not an input to this merge.
pids=()
for i in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py score --data "$OUT/new_test.jsonl"     --baseline "$CACHE/baseline.test.jsonl" --output-dir "$CACHE/option3" --model "$MODEL"     --shard-index "$i" --shard-count 3 --gpu-memory-utilization .55 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfshift.py merge --inputs "$CACHE"/option3/shard-*/option_scores.jsonl   --output "$CACHE/option_scores.test.jsonl"

pids=()
for i in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py score-experts --data "$OUT/new_test.jsonl"     --base-scores "$CACHE/option_scores.test.jsonl" --document-scores "$CACHE/document_scores.test.jsonl"     --output "$CACHE/raw_experts/shard-$i.jsonl" --model "$MODEL"     --shard-index "$i" --shard-count 3 --gpu-memory-utilization .55 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfmoe.py merge-exact --data "$OUT/new_test.jsonl"   --inputs "$CACHE/raw_experts/shard-0.jsonl" "$CACHE/raw_experts/shard-1.jsonl" "$CACHE/raw_experts/shard-2.jsonl"   --output "$CACHE/raw_experts.test.jsonl"
$PY scripts/run_cfmoe.py assemble --data "$OUT/new_test.jsonl"   --baseline "$CACHE/baseline.test.jsonl" --base-scores "$CACHE/option_scores.test.jsonl"   --matches "$CACHE/matches.test.jsonl" --document-scores "$CACHE/document_scores.test.jsonl"   --raw-experts "$CACHE/raw_experts.test.jsonl"   --conditions private_data/deltarank_sources/release_conditions.json   --evidences private_data/deltarank_sources/release_evidences.json   --output "$CACHE/expert_scores.test.jsonl"
$PY scripts/evaluate_riskroute.py
$PY -m unittest tests.test_riskroute -v
$PY -m py_compile scripts/run_riskroute.py scripts/evaluate_riskroute.py tests/test_riskroute.py
git diff --check
