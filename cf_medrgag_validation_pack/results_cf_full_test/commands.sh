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
