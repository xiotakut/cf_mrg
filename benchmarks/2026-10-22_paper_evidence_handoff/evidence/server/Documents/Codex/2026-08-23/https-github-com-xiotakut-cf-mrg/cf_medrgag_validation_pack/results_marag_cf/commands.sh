#!/usr/bin/env bash
# Executed-command record, not a one-click driver. The three long-lived services
# were run in separate terminals; adapt this record before rerunning inference.
set -e

PROJECT=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg
MARAG=/home/data3/txy/MA-RAG
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
QWEN=/home/data3/txy/models/Qwen3-8B
LLAMA=/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
OUT="$PROJECT/cf_medrgag_validation_pack/results_marag_cf"
DATA="$PROJECT/cf_medrgag_validation_pack/results_cfmoe/cache/marag_cf/datasets"
SC="$OUT/cache/fresh_sidecar"
COND="$PROJECT/cf_medrgag_validation_pack/private_data/deltarank_sources/release_conditions.json"
EVID="$PROJECT/cf_medrgag_validation_pack/private_data/deltarank_sources/release_evidences.json"
export TMPDIR=/home/data3/txy/.cache/marag_tmp
export PYTHONPATH=/home/data3/txy/.cache/marag_pydeps
export API_KEY=dummy
export RETRIEVER_HOST=http://127.0.0.1:8993

# External revisions used:
#   cf_mrg start: 212866da104889534097bf92a2ee9f83cbb201b3
#   MA-RAG:       423f031cc0ffca679a047c885be999b9604100a9
# The two small upstream compatibility/resume patches are recorded beside this file.
# On a clean checkout they were each applied once with:
# git -C "$MARAG" apply "$OUT/marag_logging.patch"
# git -C "$MARAG" apply "$OUT/marag_retriever_compat.patch"

# Services used during inference (Qwen on GPUs 1/2, MedCPT retrieval on GPU 3).
CUDA_VISIBLE_DEVICES=1 /home/data3/txy/MedRGAG/.venv/bin/vllm serve "$QWEN" \
  --port 8011 --served-model-name qwen3-8b --dtype bfloat16 --max-model-len 32768 \
  --max-num-seqs 16 --gpu-memory-utilization .82 --seed 223 --enable-prefix-caching
CUDA_VISIBLE_DEVICES=2 /home/data3/txy/MedRGAG/.venv/bin/vllm serve "$QWEN" \
  --port 8012 --served-model-name qwen3-8b --dtype bfloat16 --max-model-len 32768 \
  --max-num-seqs 16 --gpu-memory-utilization .82 --seed 223 --enable-prefix-caching
CUDA_VISIBLE_DEVICES=3 "$PYTHON" "$PROJECT/cf_medrgag_validation_pack/scripts/run_marag_retriever.py" \
  --marag-repo "$MARAG" --retriever BM25 --reranker MedCPT-Cross-Encoder \
  --corpus-name MedCorp3 --cuda 0 --port 8993

# The operational upstream check used 100 MedQA items, N=4, T=2.
"$PYTHON" "$PROJECT/cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py" \
  original-check --source "$MARAG/datasets/MedQA.json" --items 100
cd "$MARAG"
ORIGINAL_RANGES=("0 24" "25 49" "50 74" "75 99")
for shard in 0 1 2 3; do
  range=(${ORIGINAL_RANGES[$shard]})
  "$PYTHON" ma_rag_entropy.py --dataset-path "$DATA/original_medqa_check.json" \
    --model-name qwen3-8b --base-url http://127.0.0.1:8012/v1 \
    --exp "original_check_medcorp3_n4t2_shard${shard}" --num-workers 4 --num-round 2 \
    --start-id "${range[0]}" --end-id "${range[1]}"
done

# Freeze 400 development and 150 calibration pairs, then fit the portable adapter.
# Fresh-test was deliberately zero while prompts, entropy temperature, and L2 were selected.
"$PYTHON" "$PROJECT/cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py" \
  prepare --dev 400 --calibration 150 --fresh-test 0
cd "$PROJECT/cf_medrgag_validation_pack"
"$PYTHON" scripts/run_marag_cf.py smoke --pairs "$OUT/dev.jsonl" \
  --experts results_cfmoe/expert_scores.jsonl \
  --marag-rounds results_cfmoe/cache/marag_cf/marag_rounds.pilot_base.jsonl \
  --limit 20
# Separate 100-development/50-calibration N=4,T=2 pilot runs checked the
# interface and selected the native threshold/ranking settings reported below.

# MA-RAG N=8,T=4 was run for control, trap, and pair_prompt in four disjoint
# record-ID shards. Shards 0/1 used port 8011; shards 2/3 used port 8012.
run_official_split() {
  split=$1; shift
  ranges=("$@")
  cd "$MARAG"
  for member in control trap pair_prompt; do
    for shard in 0 1 2 3; do
      range=(${ranges[$shard]})
      port=$((8011 + shard / 2))
      "$PYTHON" ma_rag_entropy.py --dataset-path "$DATA/${split}_${member}.json" \
        --model-name qwen3-8b --base-url "http://127.0.0.1:${port}/v1" \
        --exp "formal_n8t4_${member}_s${shard}" --num-workers 8 --num-round 4 \
        --start-id "${range[0]}" --end-id "${range[1]}"
    done
  done
}
run_official_split dev "0 299" "300 599" "600 899" "900 1199"
run_official_split calibration "0 113" "114 227" "228 338" "339 449"

# Parse the formal development/calibration base runs and fit once. Development
# fit the entropy temperature and linear weights; calibration selected the L2 variant.
cd "$PROJECT/cf_medrgag_validation_pack"
FORMAL_ARGS=()
for split in dev calibration; do
  for member in control trap pair_prompt; do
    for shard in 0 1 2 3; do
      FORMAL_ARGS+=(--run "marag_int:${split}:${member}:8:$MARAG/runs/ma-rag/${split}_${member}/qwen3-8b/exp_formal_n8t4_${member}_s${shard}")
    done
  done
done
"$PYTHON" scripts/parse_marag_outputs.py --mapping "$OUT/marag_dataset_map.jsonl" \
  --candidates 8 "${FORMAL_ARGS[@]}" \
  --output results_cfmoe/cache/marag_cf/marag_rounds.formal_base.jsonl
"$PYTHON" scripts/run_marag_cf.py fit --pairs "$OUT/dev.jsonl" \
  --pairs "$OUT/calibration.jsonl" --experts results_cfmoe/expert_scores.jsonl \
  --marag-rounds results_cfmoe/cache/marag_cf/marag_rounds.formal_base.jsonl \
  --output "$OUT/fusion_config.json" --dev-limit 400 --calibration-limit 150

# Selected native dev/cal diagnostics. All four variants used frozen t=1,
# beta_profile=0, beta_cpg=1. Each output-dir is its actual split/variant/shard
# run root; baseline-run is the official run root, not its evaluations child.
run_native_split() {
  split=$1; shift
  ranges=("$@")
  for variant in cf_trigger_only delta_query_only cf_history_ranking full_cf_marag_native; do
    for shard in 0 1 2 3; do
      range=(${ranges[$shard]})
      port=$((8011 + shard / 2))
      "$PYTHON" scripts/run_cf_marag_native.py --marag-repo "$MARAG" \
        --dataset-path "$DATA/${split}_trap.json" --mapping "$OUT/marag_dataset_map.jsonl" \
        --pairs "$OUT/${split}.jsonl" --experts results_cfmoe/expert_scores.jsonl \
        --split "$split" --variant "$variant" --model-name qwen3-8b \
        --base-url "http://127.0.0.1:${port}/v1" \
        --output-dir "$MARAG/runs/cf-marag-native/formal_selected/${split}/${variant}/s${shard}" \
        --baseline-run "$MARAG/runs/ma-rag/${split}_trap/qwen3-8b/exp_formal_n8t4_trap_s${shard}" \
        --num-workers 8 --num-round 4 --profile-threshold 1 \
        --beta-profile 0 --beta-cpg 1 --start-id "${range[0]}" --end-id "${range[1]}"
    done
  done
}
run_native_split dev "0 299" "300 599" "600 899" "900 1199"
run_native_split calibration "0 113" "114 227" "228 338" "339 449"

# Parse and evaluate the completed native dev/cal diagnostics.
NATIVE_ARGS=("${FORMAL_ARGS[@]}")
for split in dev calibration; do
  for variant in cf_trigger_only delta_query_only cf_history_ranking full_cf_marag_native; do
    for shard in 0 1 2 3; do
      NATIVE_ARGS+=(--run "${variant}:${split}:trap:8:$MARAG/runs/cf-marag-native/formal_selected/${split}/${variant}/s${shard}")
    done
  done
done
"$PYTHON" scripts/parse_marag_outputs.py --mapping "$OUT/marag_dataset_map.jsonl" \
  --candidates 8 "${NATIVE_ARGS[@]}" \
  --output results_cfmoe/cache/marag_cf/marag_rounds.formal_native.jsonl
"$PYTHON" scripts/run_marag_cf.py predict --pairs "$OUT/dev.jsonl" \
  --pairs "$OUT/calibration.jsonl" --experts results_cfmoe/expert_scores.jsonl \
  --marag-rounds results_cfmoe/cache/marag_cf/marag_rounds.formal_native.jsonl \
  --config "$OUT/fusion_config.json" \
  --output results_cfmoe/cache/marag_cf/predictions.formal_native.jsonl
"$PYTHON" scripts/evaluate_marag_cf.py --pairs "$OUT/dev.jsonl" \
  --pairs "$OUT/calibration.jsonl" \
  --predictions results_cfmoe/cache/marag_cf/predictions.formal_native.jsonl \
  --experts results_cfmoe/expert_scores.jsonl \
  --marag-rounds results_cfmoe/cache/marag_cf/marag_rounds.formal_native.jsonl \
  --output-dir results_cfmoe/cache/marag_cf/formal_native_evaluation

# Select the untouched seed-223 fresh set only after the configuration was frozen.
"$PYTHON" "$PROJECT/cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py" \
  prepare --dev 400 --calibration 150 --fresh-test 500

# The fresh control/trap/pair runs used the same four-shard layout.
run_official_split fresh_test "0 374" "375 749" "750 1124" "1125 1499"

# Shared Llama/MedRGAG sidecar, run once on GPU 0 for both base frameworks.
cd "$PROJECT/cf_medrgag_validation_pack"
CUDA_VISIBLE_DEVICES=0 "$PYTHON" scripts/run_cfshift.py baseline \
  --data "$OUT/fresh_test.jsonl" --output-dir "$SC/baseline" --model "$LLAMA" \
  --shard-index 0 --shard-count 1 --gpu-memory-utilization .55
CUDA_VISIBLE_DEVICES=0 "$PYTHON" scripts/run_cfshift.py score \
  --data "$OUT/fresh_test.jsonl" --baseline "$SC/baseline/shard-000-of-001/baseline.jsonl" \
  --output-dir "$SC/option_score" --model "$LLAMA" --shard-index 0 --shard-count 1 \
  --gpu-memory-utilization .55
CUDA_VISIBLE_DEVICES=0 "$PYTHON" scripts/run_cfshift.py match \
  --data "$OUT/fresh_test.jsonl" --evidences "$EVID" \
  --output "$SC/delta_evidence_matches.jsonl" --device cuda:0
CUDA_VISIBLE_DEVICES=0 "$PYTHON" scripts/run_cfmoe.py documents \
  --data "$OUT/fresh_test.jsonl" --cache-root "$SC/baseline" \
  --output "$SC/document_scores.jsonl" --device cuda:0 --batch-size 64
CUDA_VISIBLE_DEVICES=0 "$PYTHON" scripts/run_cfmoe.py score-experts \
  --data "$OUT/fresh_test.jsonl" \
  --base-scores "$SC/option_score/shard-000-of-001/option_scores.jsonl" \
  --document-scores "$SC/document_scores.jsonl" --output "$SC/raw_experts.jsonl" \
  --model "$LLAMA" --shard-index 0 --shard-count 1 --gpu-memory-utilization .55
"$PYTHON" scripts/run_cfmoe.py assemble --data "$OUT/fresh_test.jsonl" \
  --baseline "$SC/baseline/shard-000-of-001/baseline.jsonl" \
  --base-scores "$SC/option_score/shard-000-of-001/option_scores.jsonl" \
  --matches "$SC/delta_evidence_matches.jsonl" --document-scores "$SC/document_scores.jsonl" \
  --raw-experts "$SC/raw_experts.jsonl" --conditions "$COND" --evidences "$EVID" \
  --output "$SC/cf_expert_scores.fresh.jsonl"

# Parse the 12 completed MA-RAG shard directories.
RUN_ARGS=()
for member in control trap pair_prompt; do
  for shard in 0 1 2 3; do
    RUN_ARGS+=(--run "marag_int:fresh_test:${member}:8:$MARAG/runs/ma-rag/fresh_test_${member}/qwen3-8b/exp_formal_n8t4_${member}_s${shard}")
  done
done
"$PYTHON" scripts/parse_marag_outputs.py \
  --mapping "$OUT/marag_dataset_map.jsonl" --candidates 8 "${RUN_ARGS[@]}" \
  --output "$OUT/cache/marag_rounds.fresh_core.jsonl"

# Frozen prediction and first/only fresh evaluation.
"$PYTHON" scripts/run_marag_cf.py predict --pairs "$OUT/fresh_test.jsonl" \
  --experts "$SC/cf_expert_scores.fresh.jsonl" \
  --marag-rounds "$OUT/cache/marag_rounds.fresh_core.jsonl" \
  --config "$OUT/fusion_config.json" --output "$OUT/predictions.jsonl"
"$PYTHON" scripts/evaluate_marag_cf.py --pairs "$OUT/fresh_test.jsonl" \
  --predictions "$OUT/predictions.jsonl" --experts "$SC/cf_expert_scores.fresh.jsonl" \
  --marag-rounds "$OUT/cache/marag_rounds.fresh_core.jsonl" --output-dir "$OUT"

# Assemble the three required public score artifacts from the frozen formal and
# fresh caches. The original expert file is ordered dev(800), calibration(200),
# fresh(1000), so these exact sed ranges select the formal 400/150 prefixes.
cat results_cfmoe/cache/marag_cf/marag_rounds.formal_base.jsonl \
  "$OUT/cache/marag_rounds.fresh_core.jsonl" > "$OUT/marag_rounds.jsonl"
sed -n '1,400p;801,950p' results_cfmoe/expert_scores.jsonl > "$OUT/cf_expert_scores.jsonl"
cat "$SC/cf_expert_scores.fresh.jsonl" >> "$OUT/cf_expert_scores.jsonl"
"$PYTHON" scripts/run_marag_cf.py export-scores \
  --marag-rounds "$OUT/marag_rounds.jsonl" --config "$OUT/fusion_config.json" \
  --output "$OUT/marag_option_scores.jsonl"
cp results_cfmoe/cache/marag_cf/formal_native_evaluation/metrics.json \
  "$OUT/native_dev_cal_metrics.json"

# Final checks.
cd "$PROJECT"
"$PYTHON" -m unittest discover -s cf_medrgag_validation_pack/tests -p 'test_marag_cf.py' -v
"$PYTHON" -m py_compile cf_medrgag_validation_pack/scripts/evaluate_marag_cf.py \
  cf_medrgag_validation_pack/scripts/parse_marag_outputs.py \
  cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py \
  cf_medrgag_validation_pack/scripts/run_cf_marag_native.py \
  cf_medrgag_validation_pack/scripts/run_marag_cf.py \
  cf_medrgag_validation_pack/scripts/run_marag_retriever.py
git diff --check

# User-approved core-only scope: fresh native MA-RAG, direct-Qwen N=1/T=1, and
# three-seed robustness were intentionally not run.
