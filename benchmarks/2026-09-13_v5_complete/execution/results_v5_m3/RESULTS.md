# M3 v5 final results

[最新M0/M2/M3/新M4/M5 v5完整对照](<../../completion/v5_benchmark_latest/README.md>)（2026-09-13）。

Completed inference: 2026-09-12 23:43:45 Asia/Shanghai. Scoring completed 23:43:58.

Exact coverage audit passed: 13,905 predictions = 3,690 exact-input reused + 10,215 new. Missing: 0. Duplicates: 0. Scoring: 15,616 mapped records across 6,104 units and 13,000 selected judgments.

| Category | Units | Unit-mean native accuracy (%) |
|---|---:|---:|
| R1 | 2866 | 26.73 |
| R2 | 79 | 34.18 |
| R3 | 733 | 8.59 |
| R4 | 13 | 38.46 |
| R5 | 3600 | 73.37 |
| ALL | 6104 | 51.61 |

Category membership overlaps. ALL is the mean over the 6,104 unique units, not the mean of the five category scores. Native invalid answers, vote ties and query-budget failures remain in the denominator.

New-result statuses: 9,926 complete; 186 invalid_answer; 88 vote_tie; 15 runtime_invalid. These are model-output outcomes, not missing tasks. No execution failure records remain.

Artifacts: [CSV](<category_scores.csv>), [plot](<v5_selected_methods.png>), [coverage audit](<artifact_audit.json>), [scoring validation](<validation.json>), all predictions（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/m3_predictions.jsonl`）, [performance notes](<performance_notes.md>).

GPU0 automatic yield triggered when dpc PID1889151 appeared; our shards resumed on GPU1/2 from saved stages. All our model and retriever GPU processes are now released. GPU1/2/3 each show only 4 MiB residual usage. GPU0 retains dpc processes, untouched.

The validated vectorized entropy parser changed only response processing; frozen model prompts, decoding and intrinsic MA-RAG method settings remained unchanged. Client handoffs preserve saved results/stages; unsaved in-flight stages may be regenerated. See README for runtime history.
