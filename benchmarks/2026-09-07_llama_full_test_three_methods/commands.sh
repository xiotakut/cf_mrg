#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../cf_medrgag_validation_pack"
PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
"$PYTHON" scripts/prepare_cf_reader_completion.py
export CF_SCREENING_OUTPUT=results_cf_full_comparison
bash scripts/cf_baseline_screening.sh readers
bash scripts/cf_baseline_screening.sh analyze
# Executed detached: tmux -L cf-readers, session full-controls, GPU0/2.
# Same batch/chunk64, BF16, gpu-memory .75 and frozen per-item/stage seeds.
"$PYTHON" results_cf_full_comparison/artifact_audit.py
