#!/usr/bin/env bash
# Commands used from cf_medrgag_validation_pack/. Expensive two-GPU stages use only GPUs 0 and 1.
set -euo pipefail

PY=/home/data3/txy/MedRGAG/.venv/bin/python
MODEL=/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
OUT=results_cfmoe
COND=private_data/deltarank_sources/release_conditions.json
EVID=private_data/deltarank_sources/release_evidences.json
PACK_DIR=$PWD

$PY scripts/run_cfmoe.py prepare --output-dir "$OUT" --fresh-pairs 1000 --seed 13
$PY scripts/run_cfmoe.py existing-fusion --output "$OUT/exploratory_existing_fusion.json"

# One 20-case smoke before any formal expert run.
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_cfmoe.py documents \
  --data "$OUT/dev.jsonl" --cache-root results_cfshift/cache/formal_baseline \
  --output "$OUT/smoke_document_scores.jsonl" --device cuda:0 --limit 20
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_cfmoe.py score-experts \
  --data "$OUT/dev.jsonl" --base-scores results_cfshift/option_scores.jsonl \
  --document-scores "$OUT/smoke_document_scores.jsonl" \
  --output "$OUT/smoke_expert_scores.jsonl" --model "$MODEL" --limit 20
$PY scripts/run_cfmoe.py assemble --data "$OUT/dev.jsonl" \
  --baseline results_cfshift/cache/baseline.jsonl \
  --base-scores results_cfshift/option_scores.jsonl \
  --matches results_cfshift/delta_evidence_matches.jsonl \
  --document-scores "$OUT/smoke_document_scores.jsonl" \
  --raw-experts "$OUT/smoke_expert_scores.jsonl" --conditions "$COND" --evidences "$EVID" \
  --output "$OUT/smoke_assembled_experts.jsonl" --limit 20

# Development/calibration document and raw-expert scores (fusion is frozen here).
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py documents \
    --data "$OUT/dev.jsonl" "$OUT/calibration.jsonl" \
    --cache-root results_cfshift/cache/formal_baseline \
    --output "$OUT/cache/documents/shard-$i.jsonl" \
    --device cuda:0 --shard-index "$i" --shard-count 2 --batch-size 64 &
done
wait
$PY scripts/run_cfmoe.py merge-exact \
  --data "$OUT/dev.jsonl" "$OUT/calibration.jsonl" \
  --inputs "$OUT/cache/documents/shard-0.jsonl" "$OUT/cache/documents/shard-1.jsonl" \
  --output "$OUT/cache/document_scores.train.jsonl"
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py score-experts \
    --data "$OUT/dev.jsonl" "$OUT/calibration.jsonl" \
    --base-scores results_cfshift/option_scores.jsonl \
    --document-scores "$OUT/cache/document_scores.train.jsonl" \
    --output "$OUT/cache/raw_experts_train/shard-$i.jsonl" --model "$MODEL" \
    --shard-index "$i" --shard-count 2 --gpu-memory-utilization .55 &
done
wait
$PY scripts/run_cfmoe.py merge-exact \
  --data "$OUT/dev.jsonl" "$OUT/calibration.jsonl" \
  --inputs "$OUT/cache/raw_experts_train/shard-0.jsonl" "$OUT/cache/raw_experts_train/shard-1.jsonl" \
  --output "$OUT/cache/raw_experts.train.jsonl"
$PY scripts/run_cfmoe.py assemble \
  --data "$OUT/dev.jsonl" "$OUT/calibration.jsonl" \
  --baseline results_cfshift/cache/baseline.jsonl \
  --base-scores results_cfshift/option_scores.jsonl \
  --matches results_cfshift/delta_evidence_matches.jsonl \
  --document-scores "$OUT/cache/document_scores.train.jsonl" \
  --raw-experts "$OUT/cache/raw_experts.train.jsonl" \
  --conditions "$COND" --evidences "$EVID" \
  --output "$OUT/cache/expert_scores.train.jsonl"
$PY scripts/run_cfmoe.py calibrate \
  --expert-scores "$OUT/cache/expert_scores.train.jsonl" --output "$OUT/fusion_weights.json"

# Fresh 1000: these commands were run only after the preceding weights were frozen.
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py baseline \
    --data "$OUT/fresh_test.jsonl" --output-dir "$OUT/cache/fresh_baseline" \
    --model "$MODEL" --shard-index "$i" --shard-count 2 --gpu-memory-utilization .55 &
done
wait
$PY scripts/run_cfshift.py merge \
  --inputs "$OUT/cache/fresh_baseline"/shard-*/baseline.jsonl \
  --output "$OUT/cache/baseline.fresh.jsonl"
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py score \
    --data "$OUT/fresh_test.jsonl" --baseline "$OUT/cache/baseline.fresh.jsonl" \
    --output-dir "$OUT/cache/fresh_scores" --model "$MODEL" \
    --shard-index "$i" --shard-count 2 --gpu-memory-utilization .55 &
done
wait
$PY scripts/run_cfshift.py merge \
  --inputs "$OUT/cache/fresh_scores"/shard-*/option_scores.jsonl \
  --output "$OUT/cache/option_scores.fresh.jsonl"
CUDA_VISIBLE_DEVICES=0 $PY scripts/run_cfshift.py match \
  --data "$OUT/fresh_test.jsonl" --evidences "$EVID" \
  --output "$OUT/cache/matches.fresh.jsonl" --device cuda:0
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py documents \
    --data "$OUT/fresh_test.jsonl" --cache-root "$OUT/cache/fresh_baseline" \
    --output "$OUT/cache/documents_fresh/shard-$i.jsonl" \
    --device cuda:0 --shard-index "$i" --shard-count 2 --batch-size 64 &
done
wait
$PY scripts/run_cfmoe.py merge-exact \
  --data "$OUT/fresh_test.jsonl" \
  --inputs "$OUT/cache/documents_fresh/shard-0.jsonl" "$OUT/cache/documents_fresh/shard-1.jsonl" \
  --output "$OUT/cache/document_scores.fresh.jsonl"
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py score-experts \
    --data "$OUT/fresh_test.jsonl" \
    --base-scores "$OUT/cache/option_scores.fresh.jsonl" \
    --document-scores "$OUT/cache/document_scores.fresh.jsonl" \
    --output "$OUT/cache/raw_experts_fresh/shard-$i.jsonl" --model "$MODEL" \
    --shard-index "$i" --shard-count 2 --gpu-memory-utilization .55 &
done
wait

# Exact-ID merges prevent older observed test rows from entering the final artifacts.
DATA=("$OUT/dev.jsonl" "$OUT/calibration.jsonl" "$OUT/fresh_test.jsonl")
$PY scripts/run_cfmoe.py merge-exact --data "${DATA[@]}" \
  --inputs results_cfshift/cache/baseline.jsonl "$OUT/cache/baseline.fresh.jsonl" \
  --output "$OUT/cache/baseline.full.jsonl"
$PY scripts/run_cfmoe.py merge-exact --data "${DATA[@]}" \
  --inputs results_cfshift/option_scores.jsonl "$OUT/cache/option_scores.fresh.jsonl" \
  --output "$OUT/cache/option_scores.full.jsonl"
$PY scripts/run_cfmoe.py merge-exact --data "${DATA[@]}" \
  --inputs results_cfshift/delta_evidence_matches.jsonl "$OUT/cache/matches.fresh.jsonl" \
  --output "$OUT/cache/matches.full.jsonl"
$PY scripts/run_cfmoe.py merge-exact --data "${DATA[@]}" \
  --inputs "$OUT/cache/document_scores.train.jsonl" "$OUT/cache/document_scores.fresh.jsonl" \
  --output "$OUT/cache/document_scores.full.jsonl"
$PY scripts/run_cfmoe.py merge-exact --data "${DATA[@]}" \
  --inputs "$OUT/cache/raw_experts.train.jsonl" "$OUT/cache/raw_experts_fresh/shard-0.jsonl" \
           "$OUT/cache/raw_experts_fresh/shard-1.jsonl" \
  --output "$OUT/cache/raw_experts.full.jsonl"
$PY scripts/run_cfmoe.py assemble --data "${DATA[@]}" \
  --baseline "$OUT/cache/baseline.full.jsonl" --base-scores "$OUT/cache/option_scores.full.jsonl" \
  --matches "$OUT/cache/matches.full.jsonl" --document-scores "$OUT/cache/document_scores.full.jsonl" \
  --raw-experts "$OUT/cache/raw_experts.full.jsonl" --conditions "$COND" --evidences "$EVID" \
  --output "$OUT/expert_scores.jsonl"
$PY scripts/run_cfmoe.py evaluate --expert-scores "$OUT/expert_scores.jsonl" \
  --fusion "$OUT/fusion_weights.json" --document-scores "$OUT/cache/document_scores.full.jsonl" \
  --output-dir "$OUT"
$PY scripts/run_cfmoe.py compact-documents \
  --input "$OUT/cache/document_scores.full.jsonl" --output "$OUT/document_scores.jsonl"

# MedPIC: all 467 public rows; official release has no pair map, so evaluation is row-level.
MEDPIC=private_data/gate-a-public-20260823-seed13-v3/raw/medpic/9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983/00-questions.json
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py medpic-run --data "$MEDPIC" \
    --output-dir "$OUT/cache/medpic/shard-$i" --model "$MODEL" \
    --shard-index "$i" --shard-count 2 --gpu-memory-utilization .55 &
done
wait
$PY scripts/run_cfmoe.py merge-keyed \
  --inputs "$OUT/cache/medpic/shard-0/medpic_scores.jsonl" "$OUT/cache/medpic/shard-1/medpic_scores.jsonl" \
  --output "$OUT/cache/medpic_scores.jsonl" --key instance_id
$PY scripts/run_cfmoe.py medpic-evaluate --scores "$OUT/cache/medpic_scores.jsonl"

# ReMedQA: fixed seed-13 subset, 100 source IDs x four official variants.
REMEDQA=private_data/gate-a-public-20260823-seed13-v2/raw/remedqa/3abb4b47a5859c7b46c0a1872a58c82e2e3029e3
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py remedqa-run --source-dir "$REMEDQA" \
    --output-dir "$OUT/cache/remedqa/shard-$i" --model "$MODEL" \
    --shard-index "$i" --shard-count 2 --limit-ids 100 --gpu-memory-utilization .55 &
done
wait
$PY scripts/run_cfmoe.py merge-keyed \
  --inputs "$OUT/cache/remedqa/shard-0/remedqa_scores.jsonl" "$OUT/cache/remedqa/shard-1/remedqa_scores.jsonl" \
  --output "$OUT/cache/remedqa_scores.jsonl" --key item_id
$PY scripts/run_cfmoe.py remedqa-evaluate --scores "$OUT/cache/remedqa_scores.jsonl"

# Non-blocking official-code CPG discussion pilot, after the core matrix; excluded from fusion.
$PY scripts/run_cfmoe.py specialist-prepare \
  --data "$OUT/dev.jsonl" --output "$OUT/cache/cpg_specialist_input.json" --limit 5
CPG_TMP=$(mktemp -d)
git clone -q https://github.com/FAIRHealth/clinical-counterfactual-reasoning.git "$CPG_TMP/repo"
git -C "$CPG_TMP/repo" checkout -q 265d1aea88f705063bb7ff2d686547d373da7e09
git -C "$CPG_TMP/repo" apply --unidiff-zero "$PACK_DIR/$OUT/cpg_official_compat.patch"
CUDA_VISIBLE_DEVICES=0 $PY -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" --port 8006 --gpu-memory-utilization .55 --max-model-len 32768 \
  --enforce-eager --generation-config vllm > "$OUT/cache/cpg_server.log" 2>&1 &
CPG_SERVER_PID=$!
trap 'kill "$CPG_SERVER_PID" 2>/dev/null || true' EXIT
(
  cd "$CPG_TMP/repo"
  VLLM_MODEL="$MODEL" VLLM_BASE_URL=http://127.0.0.1:8006/v1 \
  MAX_NEW_TOKENS=1024 TEMPERATURE=0 "$PY" run.py \
    --input "$PACK_DIR/$OUT/cache/cpg_specialist_input.json" \
    --output "$PACK_DIR/$OUT/cache/cpg_specialist_raw.json" \
    --backend vllm --max-rounds 1 --num-candidates 1 --retries 1 --wait-ready-timeout 60
)
kill "$CPG_SERVER_PID"
wait "$CPG_SERVER_PID" || true
trap - EXIT
$PY scripts/run_cfmoe.py specialist-evaluate \
  --data "$OUT/dev.jsonl" --raw "$OUT/cache/cpg_specialist_raw.json" \
  --output "$OUT/cpg_specialist_pilot.json"

$PY -m unittest discover -s tests -p 'test_*.py' -q
