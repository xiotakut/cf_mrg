#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
for method in M0 M2 M4 M5; do
  while ! test -f "$TASK_ROOT/$method/complete.json"; do sleep 30; done
done
RUN_PYTHON=/home/data3/txy/MedRGAG/.venv/bin/python
"$RUN_PYTHON" "$TASK_ROOT/code/check_v5.py" > "$TASK_ROOT/final_preparation_check.log" 2>&1
"$RUN_PYTHON" "$TASK_ROOT/code/analyze_v5.py" > "$TASK_ROOT/final_analysis.log" 2>&1
"$RUN_PYTHON" "$TASK_ROOT/code/audit_results.py" > "$TASK_ROOT/final_artifact_audit.log" 2>&1
"$RUN_PYTHON" "$TASK_ROOT/code/report_results.py" > "$TASK_ROOT/final_report.log" 2>&1
date -Is > "$TASK_ROOT/analysis_finished_at.txt"
