#!/usr/bin/env bash
set -euo pipefail
cd /home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack
export CF_SCREENING_OUTPUT=results_cf_full_test
bash scripts/cf_baseline_screening.sh prepare --tier full-test
bash scripts/cf_baseline_screening.sh run
bash scripts/cf_baseline_screening.sh analyze
# Current batch began 2026-09-06 13:44:17 CST with .45 on GPU0/2.
# GPU0 initialization needed more KV capacity and produced no LLM requests.
# One bounded restart used --gpu-memory .50; GPU2 .45 remained running.
# Future wrapper replays use .75 on both GPUs. Candidate counts and decoding do not change.
# Prior task-local runtime and exact stage artifacts are copied/reused by prepare.

# Controlled capacity restart: both task-owned workers resumed with --gpu-memory .75;
# exact preceding logs and interruption accounting are in capacity_restart.json.

# Current run/analyze automatically read method_scope.json: required methods = [M2].
# Current scheduling: batch/chunk64, frozen visible-length order, gpu_memory .75.

# 2026-09-07 tail recovery: after all old odd-index tasks completed, the
# remaining even-index tasks were repartitioned with the existing CLI:
# GPU0: run --shard-index 0 --shard-count 4 --batch-size 64 --chunk-size 64 --gpu-memory .75
# GPU2: run --shard-index 2 --shard-count 4 --batch-size 64 --chunk-size 64 --gpu-memory .75
# Local executed wrapper: cache/tail_rebalance/run.sh; proof: tail_rebalance.json.
# The standard run command above remains the full-data prepare/resume entry.

# Final full-artifact verification (after run completes):
/home/data3/txy/MedRGAG/.venv/bin/python results_cf_full_test/artifact_audit.py
