# MedRGAG Workspace Guide

> 发布状态（2026-09-13）：[最新五方法结果](../completion/v5_benchmark_latest/README.md)已全量完成，M4 采用修复版；M6/M7 均暂停。下文过程状态与执行命令按其原记录时间理解。

Updated: 2026-09-13 (Asia/Shanghai)

This is the MedRGAG orientation and historical handoff document. Use it to
locate the relevant source, interface, result, and handoff without
rediscovering the workspace or rerunning an experiment.
Inspect additional files only when the user's requested change actually
touches them.

For paper methods and a dated record of completed work and concrete changes,
read the consolidated work log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/工作过程与调整记录_论文参考.md`）
([GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md)),
expanded on 2026-09-13. It distinguishes collection, semantic labels,
qualification, sampling and model runs; documents the 704-unit AMQA review
overlay and 172-judgment audit corrections; and connects the 09-08 archive to
v2/v3/v4/v5 without mixing their counts. This update only consolidated existing
artifacts and documentation. Follow each run pack's final report for model
completion; a dated dataset README can predate its subsequent completed run.

## 1. Current result and source-of-truth order

**当前v5五方法完整结果：[M0/M2/M3/新M4/M5最新总表](<../completion/v5_benchmark_latest/README.md>)**（2026-09-13）。各13,905输入/15,616评分映射，6,104单元。M4使用全量结构约束修复版，其余方法沿用已完成结果；ALL依次48.10/48.81/51.61/48.20/47.35%。分类图、错误分解、有效率及完整精度CSV均已同步。下方早期Active条目为历史运行记录；当前这五方法全部完成，M6/M7暂停。

For paper provenance on the v3 baselines and classification-guide revisions, read
[R1_R5_V3_BASELINES_WORK_RECORD.md](<R1_R5_V3_BASELINES_WORK_RECORD.md>). It records
M2 reuse/new computation, M3 task/context/runtime adaptations, method identity,
before/after changes, evidence, and paper wording. The separate v3→v4→v5
construction record remains the source for full classification and sampling work.
The new record also points to the completed v5 M0/M2/M3/M4/M5 result packages as
of September 13; older running-status entries retain their historical dates.

Path aliases used below:

```text
CF_REPO=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg
CF_PACK=$CF_REPO/cf_medrgag_validation_pack
CF_FULL=$CF_PACK/results_cf_full_comparison
CF_R14=$CF_PACK/results_r1_r4_m0_m1_20260908
CF_BENCH_V2=$CF_PACK/benchmark_r1_r5_text_auto_cpv_v2_20260909
CF_V2_RESULTS=$CF_PACK/results_r1_r5_v2_m0_m1_20260909
CF_BENCH_V3=$CF_PACK/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909
CF_BENCH_V5=/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v5_20260910
CF_CLASSIFIED_FULL=/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910
CF_V3_M2=$CF_PACK/results_r1_r5_v3_m2_20260909
CF_V3_M3=$CF_PACK/results_r1_r5_v3_m3_20260909
CF_M2_FULL=$CF_PACK/results_cf_full_test
CF_BENCHMARKS=$CF_REPO/benchmarks
CF_ADAPTER=$CF_PACK/results_marag_cf
CF_ITERATIVE=/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc
MARAG=/home/data3/txy/MA-RAG
WM_ARCHIVE=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill
V4=$WM_ARCHIVE/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4
```

`CF_BENCH_V3` is the current user-approved R1–R5 test subset with mutually
exclusive categories and reused M0/M1 results. The complete M2 evaluation and
three-method comparison are separately in `CF_V3_M2`; the complete M3 MA-RAG
evaluation and latest four-method comparison are in `CF_V3_M3`. `CF_BENCH_V2` is the preserved
overlapping-category version. `CF_R14` is the preceding classified R1–R4 M0/M1 result. `CF_FULL` is the completed
full-release M0/M1/M2 comparison. `CF_ADAPTER` names the historical
MA-RAG/adapter result and is not the latest baseline entry.

There are three distinct research layers. Do not collapse their claims:

1. `/home/data3/txy/MedRGAG` is the completed local all-Llama MedRGAG
   reproduction/proxy and its five ordinary medical-QA datasets.
2. `$WM_ARCHIVE` contains the completed 2026-08-23 action-aware/world-model
   proxy experiment. It was negative and is stopped.
3. `$CF_REPO` contains the later counterfactual work. Its current evaluation
   dataset is **v3, the 3,105-unit exclusive R1–R5 benchmark**, with complete
   M0/M1 results under `$CF_BENCH_V3/results`, complete M2 under `$CF_V3_M2`,
   and complete M3 plus the latest four-method comparison under `$CF_V3_M3`.
   It derives from the
   **2026-09-08 medical CF five-label collection, audit and GitHub release**.
   The last new-input M0/M1 inference was the R1–R4 run completed 2026-09-08;
   v2 added the CPV-MedQA R5 slice using existing predictions, and v3 changed
   only category allocation. The formerly deferred R5 sources now have completed classification/qualification
   restoration under `$CF_CLASSIFIED_FULL`, with existing outputs preserved. v3 is available locally and has not been
   published to the dated GitHub archive.
   The complete independent-input M0/M1/M2 full-release comparison remains
   available separately. The earlier pair-aware CF-Residual
   Adapter and MA-RAG studies are historical.

### M6 i-MedRAG / M7 TC-RAG implementation and development record (2026-09-13)

The user assigned **M6 = i-MedRAG (`imedrag`)** and **M7 = TC-RAG (`tcrag`)**
on 2026-09-13 for the current R1–R5 comparison and paper. Commands, configs,
predictions and run directories retain the descriptive execution IDs. Historical
MedRGAG ablation and Gate D labels keep their original experiment-local meanings.
The two additional methods' server run pack is
`$CF_ITERATIVE`, registered through `$CF_PACK/scripts/run_iterative_baselines.py`.
Start with the [paper implementation and adjustment record](<../m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md>)
for completed work, source versions, every development run, before/after fixes,
cache provenance, cumulative compute, Methods drafts and remaining limitations.
Append subsequent changes and their evidence there, as requested by the user.
The [README](<../m6_m7_implementation/README.md>)
contains the verified commands; [method fidelity](<../m6_m7_implementation/method_fidelity.md>)
records paper/code differences; [acceptance report](<../m6_m7_implementation/acceptance_report.md>)
records the measured status.

Final execution configs are `configs/imedrag_runtime_v4.json` and
`configs/tcrag_runtime_v4.json`. i-MedRAG uses Llama-3.1-8B-Instruct with four
query rounds and three requested queries per round, independent retrieval/QA,
ordered cross-round QA history and the upstream final formatting call.
TC-RAG uses the user-specified Qwen3-8B with thinking disabled, full-distribution
generation entropy, a real memory stack, Backtrack and paper-aligned Summary
replacement; max_loop=8, topK=4, sigma=1.2 (earliest acceptance on generation 5).
Both reuse full MedCorp, BM25 top32 per corpus and MedCPT reranking top8.
The same-weight Transformers backend supplies entropy; it differs from the
existing vLLM baseline engine. The two new methods also have different backbones,
so their comparison is not an algorithm-only controlled comparison.

Nineteen automated tests passed. Each method completed all 24 fixed development
inputs (12 MedQA validation and 12 nonoverlapping MedEinst training inputs):
i-MedRAG has 19 valid / 5 invalid, TC-RAG 9 valid / 15 invalid, with zero failed,
pending, unknown or duplicate terminal records. Final runs are
`runs/imedrag_dev_accepted` and `runs/tcrag_dev`. The i-MedRAG final directory
replays 521 real model and 279 retrieval receipts after a deterministic
single-quoted dictionary-to-JSON syntax fix; its 1.6-second replay is not model
throughput. Earlier pilots, failures, formatter changes and code snapshots remain
available. Use the original cold run and saved fresh requests for cost accounting.

Output-format and open-diagnosis canonical-scoring compatibility remain unresolved.
Other source structures, long inputs and evidence interventions have not all had
real-model validation; complete formal cost remains unestimated. Formal inference,
formal-input blind checks and TC threshold calibration were not started. The
earlier blind-input and calibration plan files are retained as unexecuted history.
No new CF method or adapter was added. M20/MedCounterFact, M22/MedRGB and M23/BioRAB
are existing dataset IDs, not additional methods.

The inherited V5 scope remains 6,104 units, 13,000 selected judgments, 13,905
unique inference inputs per method, 15,616 native scoring records and 34,753
target-to-input mapping rows, using `evaluation_labels`. M22 retains the existing
fixed perturbed evidence plus external retrieval protocol; this is not native
MedRGB static-evidence evaluation. This documentation update launched no models
and changed no benchmark selection, predictions or scoring.

### R1–R5 paper work and adjustment record (2026-09-13)

For the construction thread's concrete before/after changes, read
[the paper work record](<../construction/paper_work_record_20260913/README.md>) ([GitHub](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-13_r1_r5_paper_work_record/README.md)).
It covers v3 M2/M3 handling and method identities, full v4 classification and
qualification, semantic preservation, 16 specific adjustments, rejected scope
previews, v5 random sampling, proof boundaries, and a Methods draft. Later
M0/M2/M4/M5 runs belong to their separate run directory: on 2026-09-13 its
`validation.json` reports complete coverage of 13,905 inputs per method with
zero missing/duplicate predictions. The September 10 v5 construction files'
`runtime_compatibility=not_verified` is a dated construction-stage statement.
No model was run or dataset selection changed to create this record.

### Latest selection: v5, eight random R5 strata (2026-09-10)

The user approved 450 randomly sampled R5 comparison units per source, totaling
3,600, while preserving complete v4 and every eligible R1–R4 target. The resulting
v5 selection has 6,104 unique units and 13,000 eligible judgments across 11 sources.
R1–R5 evaluation memberships: 2,866 / 79 / 733 / 13 / 3,600 (overlapping).

Start with [v5 README](<../construction/benchmark_r1_r5_v5_20260910/README.md>),
[sampling protocol](<../construction/benchmark_r1_r5_v5_20260910/sampling_protocol.json>),
[full exploration history](<../construction/benchmark_r1_r5_v5_20260910/EXPLORATION_HISTORY.md>), and
[verification](<../construction/benchmark_r1_r5_v5_20260910/verification.json>). The [GitHub v5 archive](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_v5/README.md)
includes candidate IDs, selected IDs and a standalone replay script.

The protocol seed was generated once before selection. Within each source, sorted
eligible unit IDs were sampled without replacement using Python `random.sample`;
v3 membership and model predictions played no role. All eight draws replay exactly.

Read `selected_targets.jsonl.gz` and **`evaluation_labels`** when loading v5.
`labels` preserves original semantics, including R5 memberships that were not sampled
but coexist with retained R1 targets. Never use semantic R5 alone to rebuild the
v5 evaluation subset. `v3_v4_v5_membership.csv` contains all v4 eligible units and
membership flags; v5 includes 2,116 v3 units and 3,988 units outside v3. Prediction
reuse still requires exact input/task/method compatibility. The V5 native input pack is now materialized and validated. The requested M0/M2/M4/M5 run started on 2026-09-11; use the active-run entry below before launching any inference.

### Active V5 M0/M2/M4/M5 evaluation (started 2026-09-11)

Run pack: [README](<../execution/results_v5_m0_m2_m4_m5/README.md>).
This is a running experiment, not a completed result. Frozen V5/v4/v3 files and previous results are preserved.
The pack contains 13,905 independent inputs and 15,616 native evaluation mappings per method, covering all 6,104 selected units and 13,000 selected judgments using `evaluation_labels`.
M0 reuses 8,877 predictions and adds 5,028; M2 reuses 6,687 and adds 7,218; M4/M5 each require 13,905. Smoke outputs are included and must not be rerun.

M0 and M2 full inference are active under tmux socket `v5-benchmark`; queues `m0-m5` and `m2-m4` continue to M5/M4 after their preceding method. M4 no longer waits for RRF indexes after the user-requested configuration change on 2026-09-11. Queue `finalize` runs complete scoring and stage audits only after all four method completion markers exist.
Read the pack's `M*/progress.json`, `M*/complete.json`, `*_full.log`, `validation.json`, and `analysis_finished_at.txt` for current state. Partial scores are not final comparisons. Resume these queues/caches rather than preparing a duplicate run.

For this V5 evaluation, the user requested M4 to match M5 except for Llama: both use full-MedCorp BM25 top-32/source, MedCPT reranking top-8, temperature 0.7, output 2048, context clipping 30000 tokens, vLLM BF16 and identical native task adapters. Active configs are in the V5 result directory `configs/`, overriding the standalone historical M4 RRF config. Both have 131072 total context; Qwen uses YaRN factor 4, Llama uses its native context. Existing RRF indexing jobs remain untouched but are no longer a benchmark dependency. Full-M4 and M5 inference smoke validation remains pending at this entry's creation.
M0/M2 use the existing native Llama prompts and M2 stages; new MedRGB final answers use the existing robustness protocol with a 2,048-token output budget. The six local MedRGB context ratios and missing-document scoring limits are documented in the pack.

GPU1/2 are shared with the user's existing index preparation. GPU0 belongs to dpc and GPU3 to wwj; their jobs are untouched. M2 uses batch64 and a .75 GPU-memory fraction after startup capacity measurement. Luna max provides read-only supervision. The user explicitly requested leaving normal running processes uninterrupted; no further planned stop/reallocation of healthy jobs.

### Latest full-coverage classification delivery (2026-09-10)

Classification and qualification are complete; v3 remains the latest completed M0–M3 evaluation. Start with the [new delivery](<../construction/benchmark_r1_r5_v4_20260910/DELIVERY.md>) for the expanded data, and the v3 section below for existing model results.

The 24,436 sampling omissions and 18,238 previously deferred R5 units are fully accounted for. Existing R5 labels, reasons and evidence were reused. RESOURCE adds 3,615 judgments on existing units, with 3,529 eligible targets. The complete 55,991-unit archive now has 38,123 units with at least one eligible target and 77,781 eligible judgments. These are not distinct inference-input counts; a new evaluation run pack has not been materialized.

| Read | Entry |
|---|---|
| Classification definitions and examples | [Classification guide](<R1_R5_CLASSIFICATION_GUIDE.md>) |
| Full delivery and limitations | [DELIVERY.md](<../construction/benchmark_r1_r5_v4_20260910/DELIVERY.md>) |
| Final target annotations and eligibility | all_reviewed_target_annotations.jsonl.gz（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/exports/all_reviewed_target_annotations.jsonl.gz`） |
| All archived unit dispositions | archive_unit_coverage.csv（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/exports/archive_unit_coverage.csv`） |
| Source scope and exclusion reasons | [source_scope_inventory.md](<../construction/benchmark_r1_r5_v4_20260910/source_scope_inventory.md>) |
| Figures and tables | [figures/README.md](<../construction/benchmark_r1_r5_v4_20260910/figures/README.md>) |
| Verified coverage and preservation | [completion_audit.json](<../construction/benchmark_r1_r5_v4_20260910/completion_audit.json>) |
| GitHub report | [Published classification delivery](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-10_r1_r5_full_classification/README.md) |

Use each target's `evaluation_eligible`; a qualified parent does not qualify every child. Ten newly identified unchanged controls are excluded by a separate qualification override, preserving historical semantic records. Required missing multimodal input is excluded. New classification does not overwrite v3 or its results.

### Complete v3 R1–R5 M3 MA-RAG evaluation (2026-09-10)

The user requested the local MA-RAG as M3, without the project's added modules.
The full **4,872-input / 3,105-unit v3** run completed under `$CF_V3_M3`:
**2026-09-09 17:32:33 to 2026-09-10 08:43:00 Asia/Shanghai**, **54,627 s
(15.17 h)**. All eight 609-input shards exited 0. Native scoring and the full
candidate/stage audit completed, and report generation finished at 08:44:22.
The conversation interruption did not stop the background run. The primary
agent confirmed completion on resuming at 09:38; no recovery inference was
needed. This run is complete; do not launch a duplicate.

Read `$CF_V3_M3/README.md`, `category_scores.csv`, `validation.json`, and
`artifact_audit.json`; download `$CF_V3_M3.zip`. M3 contributes **4,872
predictions and 6,030 scored mappings**. Combined M0–M3 files contain **19,488
predictions and 24,120 scored records**, with zero missing or duplicate records.
The frozen v3 inputs/mappings and previous M0/M1/M2 results remain unchanged.

| Category | Units | M0 | M1 | M2 | M3 |
|---|---:|---:|---:|---:|---:|
| R1 | 1,601 | 45.22% | 41.29% | 44.41% | 43.85% |
| R2 | 77 | 9.09% | 9.09% | 7.79% | 32.47% |
| R3 | 324 | 18.83% | 28.40% | 23.46% | 14.20% |
| R4 | 13 | 38.46% | 38.46% | 53.85% | 38.46% |
| R5 | 1,090 | 66.51% | 69.82% | 70.28% | 79.82% |
| Total | 3,105 | 49.02% | 49.15% | 50.43% | 53.08% |

M3 scores **1,648/3,105**, **+2.64 percentage points** over M2. R2 and R5
increase while R1/R3/R4 decrease. R5 answer invariance is **90.28%**
(984/1,090), and both-answers-correct is **75.69%** (825/1,090). Read
`r5_pair_summary.csv`; these are separate from R5 variant accuracy.
The main chart is `r1_r5_four_methods.png` (PDF/SVG available).

The baseline is upstream MA-RAG intrinsic, local Qwen3-8B BF16, N=8/T=4,
MedCorp3 BM25/MedCPT, original solver/query decoding and entropy/history/voting.
Only native v3 answer formats and full fixed evidence are adapted at the task
interface. No native CF variant, adapter, Profile, CFShift, CFMoE, Qwen sidecar,
WM, training or judge is called. Qwen is M3's own backbone, not an added sidecar.
Official Qwen YaRN factor 4 extends context to 131,072; actual solver/query
prompts plus output budgets were checked without evidence truncation.
This preserves the existing local N8/T4 and MedCorp3 configuration, rather
than reproducing the original paper's table settings. M3's backbone, corpus,
and call budget differ from M0–M2; score differences cannot be attributed to
the MA-RAG algorithm alone. R4 remains agreement with 13 author-expected answers.

The audit covers **10,360 solver requests / 82,880 candidates** and **5,493
query generations**: 79,533,427 API prompt tokens, 432,965,800 logical prompt
tokens, and 43,100,841 completion tokens. Final input statuses are **4,812
complete, 51 vote ties, 4 invalid answers, and 5 runtime-invalid query outputs**;
the latter 60 inputs retain null answers and count as incorrect. Native score
invalidity also includes diagnosis labels not accepted by the original exact
scorer, so it is a different count. No transport/backend worker failures occurred.

Six real-input smoke cases all passed, including the longest mandatory
evidence; maximum observed full-stage prompt was 80,156 tokens. They are
reused in the full run; the full-run wall time excludes this earlier smoke
phase and service preparation. Four additional long official inputs completed an
early concurrent KV check at 17:48:21 and are also reused; all four passed
without preemption, abort, timeout or context overflow. Qwen endpoints
8011/8012 used GPU 1/2, max-num-seqs 32 and memory .75; eight clients ran
disjoint frozen-input shards. The original MedCorp3 retriever on port 8993
shared GPU 1. The run released its own services after inference; other users'
services were untouched.

The completed run used tmux socket `r1r5-m3` and `code/run_full.sh`.
`cache/items/<item_id>/` contains stage prompts, candidates, retrieval and final
votes. `run_exit.json` records exit 0, and `analysis_finished_at.txt` records
report completion. `code/analyze_m3.py` rebuilds the results offline.
Luna max provided read-only supervision, with periodic primary-agent checks;
its final independent acceptance passed with zero differences across all
6,030 recomputed M3 scores and the R5 pair results. Read `supervision.md`
for the final acceptance record.

### Complete v3 R1–R5 M2 evaluation (2026-09-09)

The user requested the full local all-Llama MedRGAG baseline without added
modules. All **4,872/4,872 independent inputs** now have M2 predictions,
covering **6,030 evaluation mappings and 3,105 exclusive-category units**.
Read `$CF_V3_M2/README.md`, `category_scores.csv`, `validation.json`, and
`artifact_audit.json`; download `$CF_V3_M2.zip`. The frozen v3 dataset and its
original M0/M1 files remain unchanged. The separate result directory includes
all **14,616 three-method predictions and 18,090 scored records**.

M0/M1/M2 unit pass rates are:

| Category | Units | M0 | M1 | M2 |
|---|---:|---:|---:|---:|
| R1 | 1,601 | 45.22% | 41.29% | 44.41% |
| R2 | 77 | 9.09% | 9.09% | 7.79% |
| R3 | 324 | 18.83% | 28.40% | 23.46% |
| R4 | 13 | 38.46% | 38.46% | 53.85% |
| R5 | 1,090 | 66.51% | 69.82% | 70.28% |
| Total | 3,105 | 49.02% | 49.15% | 50.43% |

M2 scores **1,566/3,105**, +1.42/+1.29 percentage points over M0/M1.
These are descriptive differences. R5 answer invariance is **78.81%**
(859/1,090), versus M0/M1 97.16%/91.83%; M2 both-answers-correct is **62.02%**
(676/1,090). R5 accuracy and invariance remain separate metrics. R4 is still
agreement with 13 author-expected HIV ART answers, not clinically validated gold.

Exactly **4,720 complete M2 results** were reused from `$CF_M2_FULL` after
matching IDs, question text, ordered options, fixed evidence, answer format,
configuration and input/stage seeds. The other **152 inputs** (FairMedQA,
DiversityMedQA and HIV ART scenarios) completed **1,976 new Llama calls**:
760 summaries, 152 explorations, 760 generations, 152 original KADS selections,
and 152 final answers. Their initial top-5 documents were reused from matching
M1 retrieval queries; final MedCPT reranking ran normally. No M0/M1 inference,
format repair, LLM judge, sidecar, adapter, Qwen or supplemental repeat ran.

The unchanged local baseline uses Llama-3.1-8B-Instruct BF16, 98,304 context,
the original KGCC/generation/KADS path, and reader T=0/max_tokens=64. GPU 1/2,
batch/chunk 64, gpu_memory .75; **2026-09-09 16:54:30–16:58:21 CST**, **231 s**.
New logical prompt/completion tokens: **2,062,136 / 487,180**. Both workers exited
0 and released their GPUs. Luna max provided read-only supervision, with the
primary agent checking progress and full coverage.

`$CF_V3_M2/items.jsonl`, `evaluation.jsonl`, and `units.jsonl` are exact v3
copies. `m2_predictions.jsonl` / `m2_scored.jsonl` contain M2 only;
`predictions.jsonl` / `scored.jsonl` also include preserved M0/M1. Aggregate
`role != 'reference'` using current `labels`. `screening_items.jsonl` contains
only the 152 supplemental inference inputs; it is not the full benchmark.
`code/run_m2.sh` records the actual inference command; `code/analyze_m2.py`
rebuilds the report offline. `stages.jsonl.gz` indexes every selected input's
complete original/current stage artifacts by `source_run` and `artifact`.

### Current R1–R5 benchmark v3: exclusive categories (2026-09-09)

The user requested assigning all overlaps to the smaller existing category.
Each unit is assigned to the smallest category among its v2 active labels,
using the fixed pre-assignment category sizes (R1 1,929; R2 77; R3 327;
R4 13; R5 1,090). Assignment does not use model scores.
The 324 R1/R3 units go to R3, the 1 R1/R2 unit goes to R2, and the 3
R1/R2/R3 units also go to R2. This resolves 328 overlapping units and removes
331 duplicate memberships, without removing any units.

Read `$CF_BENCH_V3/README.md`; download `$CF_BENCH_V3.zip`. Active
R1/R2/R3/R4/R5 counts are now **1,601/77/324/13/1,090**, summing directly to
**3,105** with zero overlapping units. Inputs, gold, predictions, original
classification provenance, and per-record correctness remain unchanged.
The package still has 4,872 inputs, 6,030 evaluation mappings per method,
9,744 M0/M1 predictions, and 12,060 method score records. No new inference,
LLM judge, or M2 calls were made. All earlier versions remain preserved.

`labels` in units/evaluation/scored files contains exactly one active category.
`previous_labels` preserves v2 active labels; `original_labels` in units and
`original_unit_labels` in evaluation/scores preserve the original semantic
classification. `classification_provenance.jsonl` remains a full copy of the
original records. `reassigned_units.csv` lists all 328 assignment changes.
Exclusivity applies to `unit_id`; source cases and reference inputs can still
be shared by different units.

Current M0/M1 pass rates for R1/R2/R3/R4/R5 are **45.22/41.29%, 9.09/9.09%,
18.83/28.40%, 38.46/38.46%, 66.51/69.82%**. The total remains
**1,522/3,105 (49.02%) versus 1,526/3,105 (49.15%)**. Read
`results/category_scores.csv` and `results/r1_r5_total.png` (PDF/SVG available)
inside the v3 package. R4/R5 scope and supplementary pair results remain as in
v2. Category-score changes result only from reassignment of existing units.

#### Load the current benchmark in a new conversation

The real instruction filename is `/home/data3/txy/AGENTS.md` (plural); it
points here. For R1–R5 tasks, read the v3 README（本地制品：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909/README.md`）
and its `manifest.json`. This is the current local package. The following
command is self-contained and reads existing files with system Python;
no model environment, inference, regeneration, or network access is needed.

```bash
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path

benchmark = Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909')
results = benchmark.parent / 'results_r1_r5_v3_m3_20260909'
def read(name, base=benchmark):
    with (base / name).open() as stream:
        return [json.loads(line) for line in stream]

manifest = json.loads((benchmark / 'manifest.json').read_text())
assert manifest['version'] == 'v3_20260909_exclusive_text_auto_cpv'
units = read('units.jsonl')
items = {r['item_id']: r for r in read('items.jsonl')}
evaluation = read('evaluation.jsonl')
prediction_rows = read('predictions.jsonl', results)
predictions = {(r['item_id'], r['method']): r for r in prediction_rows}
scored = read('scored.jsonl', results)
methods = {'direct_llama', 'retrieval_only_llama', 'medrgag_llama_base', 'marag_intrinsic_qwen3_8b'}
counts = Counter(r['labels'][0] for r in units)
assert all(len(r['labels']) == 1 for r in units)
assert counts == dict(R1=1601, R2=77, R3=324, R4=13, R5=1090)
assert len(units) == len({r['unit_id'] for r in units}) == 3105
assert len(items) == 4872 and len(evaluation) == 6030
assert len(prediction_rows) == len(predictions) == 19488
assert len(scored) == len({(r['record_id'], r['method']) for r in scored}) == 24120
assert set(predictions) == {(i, m) for i in items for m in methods}
assert all(e['item_id'] in items for e in evaluation)
r5_units = {r['unit_id'] for r in units if r['labels'] == ['R5']}
r5_evaluation = [e for e in evaluation if e['unit_id'] in r5_units]
r5_input_ids = {e['item_id'] for e in r5_evaluation}  # Includes reference inputs.
assert len(r5_units) == 1090 and len(r5_input_ids) == 1762
print(dict(category_counts=dict(counts), units=len(units), inputs=len(items),
           method_predictions=len(predictions), method_scores=len(scored)))
PY
```

Use `units.labels` / `evaluation.labels` / `scored.labels` for current
categories. `previous_labels`, `original_labels`, `original_unit_labels`, and
`classification_provenance.jsonl` provide history, not v3 membership.
Filter units first, then retain **all** their evaluation records to include
references. Join inputs by `item_id`, predictions by `(item_id, method)`, and
scores by `(record_id, method)`. Prediction method names are `direct_llama`,
`retrieval_only_llama`, `medrgag_llama_base`, and `marag_intrinsic_qwen3_8b`;
score method names are `M0`, `M1`, `M2`, and `M3`. The frozen benchmark manifest
still describes its original M0/M1 export; the separate M3 result directory
holds the latest combined comparison. Raw output is `raw_response`; a normalized
`answer` field is absent in some saved predictions. For M3, `raw_response` is
the final native vote serialized for scoring; actual LLM outputs are in its
`cache/items` stage records.
Aggregate only `role != 'reference'` for the 3,105-unit category/total table.
`$CF_V3_M3/category_scores.csv` already provides those four-method results. Model inputs
are the question/options/fixed evidence in `items.jsonl`; gold and classification
reasoning are evaluation metadata.

**Runtime boundary:** v3 is an exported dataset/results package. The historical
thread scripts `prepare_benchmark.py`, `run_benchmark.py`, and
`analyze_benchmark.py` default to `results_r1_r5_m0_m1_20260908`, not v3.
`run_benchmark.py` additionally requires a frozen `plan.json`, preflight lengths,
and a worker/cache layout absent from v3. Setting `R_BENCHMARK_OUTPUT` to v3
alone does not make it a runnable directory. `CF_FULL/commands.sh` targets the
25,280-input full-release experiment. Use the read-only command above for
loading/status/analysis. For requested new inference, create a separate run
directory from the selected v3 inputs and mappings with the chosen runner's
required plan/cache configuration, then score against the v3 evaluation.
`export_benchmark_v3.py` regenerates and writes the export; it is not a loader.

### Preceding R1–R5 benchmark v2 (exported 2026-09-09)

The user approved retaining the prior automatic-only R1–R4 subset and adding
only the eligible CPV-MedQA R5 slice, while preserving all old versions.
Read `$CF_BENCH_V2/README.md`; download `$CF_BENCH_V2.zip`.
The export contains **3,105 comparison units, 8 sources, 4,872 unique inputs,
6,030 evaluation mappings per method**, and all **9,744 saved M0/M1 predictions
and 12,060 fixed-rule scored records**. No new inference, LLM judge, or M2 calls
were made. Prior datasets, results, and archives were not modified.

Active R1/R2/R3/R4/R5 counts are **1,929/77/327/13/1,090**, with overlapping
categories and 3,105 units after deduplication. R5 is CPV-MedQA only: 672 source
cases and 1,762 unique inputs, including 62 reference inputs shared with R1–R4.
This includes every eligible CPV R5 unit in the frozen cohort without further
sampling; it is not the entire original CPV public dataset.

Use `units.jsonl` / `units.csv` and their `labels` for this version's categories;
join `items.jsonl` to `evaluation.jsonl` by `item_id` for questions and gold.
`classification_provenance.jsonl` retains the original 3,105 reviewed records.
Original classifications are also recorded as `original_labels` in units and
`original_unit_labels` in evaluation and score rows. In particular, the original
MedCounterFact R1/R5 units participate only in R1 in this version; their original
classifications remain intact. `category_summary.csv` and `source_summary.csv`
describe the test composition; `results/category_scores.csv` contains the reused
fixed-rule results. R4 remains 13 HIV ART scenarios; R5 covers one source's
patient-attribute variants. Read `manifest.json` and `validation.json` for counts
and export checks. No publication to an external service was requested.

### Preceding v2 R4/R5 evaluation and combined R1–R5 results (2026-09-09)

The user requested M0/M1 evaluation of the new R4/R5 scope combined with the
previous R1–R3 results. Read `$CF_V2_RESULTS/README.md` and
`$CF_V2_RESULTS/category_scores.csv`; figures are `r1_r5_total.png`, `.pdf`,
and `.svg`. Download `$CF_V2_RESULTS.zip` for the report, figures, combined
scored records, and per-unit tables. The frozen v2 benchmark remains unchanged.

All 3,550 M0/M1 predictions for the 1,775 R4/R5 unique inputs were already
complete. The existing native scorer was rerun on raw responses for 4,386
method evaluation records, including references. Every rescored field matches
the previous result. The 7,674 R1–R3 method evaluation records remain intact.
No new model inference, LLM judge, or M2 calls were needed.

Unit-weighted M0/M1 pass rates for R1/R2/R3/R4/R5 are respectively
**40.75/39.09%, 9.09/9.09%, 18.96/28.44%, 38.46/38.46%, 66.51/69.82%**.
The deduplicated total is **1,522/3,105 (49.02%) versus 1,526/3,105 (49.15%)**.
R4 is agreement with author-expected answers, not a clinically validated gold
accuracy claim. R5 is CPV choice accuracy; a separate paired table reports
answer invariance **1,059/1,090 (97.16%) versus 1,001/1,090 (91.83%)**, and
both answers correct **719/1,090 (65.96%) versus 724/1,090 (66.42%)**.
See `r5_pair_summary.csv` and `r5_pair_scores.csv`; consistency can include two
wrong answers and is not substituted into the category accuracy table.

### Preceding R1–R4 automatic-only subset (exported 2026-09-09)

This preceding benchmark scope excludes all judgment-scored free-response
units: M05 LabTest (30) and M16 EquityMedQA (125). The 9 LabTest NA questions
were a prior AI-review choice and are included in the 30 removed units, with
no additional subtraction. The 86 image-dependent R4 units remain excluded.
Read `$CF_R14/automatic_only/README.md`; the full export is
`$CF_R14/r1_r4_automatic_only.zip`. It contains **2,015 comparison units,
8 sources, 3,172 unique inputs, 6,344 saved M0/M1 predictions**, 3,850 evaluation
mappings per method, and 7,700 fixed-rule scored method records. No inference
or LLM judge calls were made for this export. All original data are preserved.

R1/R2/R3/R4 counts are **1,929/77/327/13** (overlapping labels). Unit-weighted
non-reference M0/M1 pass rates are **40.75/39.09%, 9.09/9.09%,
18.96/28.44%, 38.46/38.46%**; the deduplicated total is **39.55/37.97%**.
R4 now contains only 13 HIV ART scenarios (5 correct per method), scored
against author-expected answers. Prior AI-inclusive category tables are
historical and do not describe this subset. See `units.csv`, `source_summary.csv`,
`category_summary.csv` and `validation.json` within the subset directory.

### Classified R1–R4 M0/M1 result (completed 2026-09-08)

The user first requested the new R1–R5 benchmark, then excluded multimodal
questions and deferred further R5 execution while preserving existing R5
outputs. The final scope is all previously included records carrying R1–R4:
**2,170 comparison units, 3,296 unique inputs, 6,592/6,592 M0/M1 predictions**.
There are no missing or duplicate predictions and **no M2 calls**. Counts by
overlapping label are R1/R2/R3/R4 = **2,030/88/389/53**; 86 image-dependent R4
units remain excluded. Reused predictions number 6,192; the reduced run made
400 additional calls with unchanged inputs, model, retrieval and sampling.

The run produces 8,260 method evaluation records: 7,700 use native automatic
scoring. The other 560 LabTest/EquityMedQA records have now completed **AI rubric
review**, authorized by the user, with GPT-6 primary judgments and Luna max
supervision. These deduplicate to 60 LabTest and 188 EquityMedQA answers; an
additional 250 same-method counterfactual pair assessments are complete. This
is not a clinical-expert replication. LabTest has 9 NA conclusions per method
(21 adjudicable each); all 30 reasoning scores per method are retained. M0/M1
adjudicable correctness is 100.00%/95.24%; reasoning mean is 4.23/4.40 (1 best,
5 worst). Equity independent bias is 46.81%/40.43%; pair bias is 72.80%/60.80%.
Read `$CF_R14/rubric_scoring/report.md`, `protocol.md`, and `validation.json` for
judgments, original-rubric boundaries and local operationalization. Original
predictions and automatic eligibility/scores remain unchanged. Native metrics
remain source/task-specific. The user-requested **R1–R4 category overview** is
in `$CF_R14/category_summary/report.md`, with CSV and PNG/PDF/SVG exports.
It adds an explicitly project-defined, unit-weighted pass rate: native automatic
correctness, LabTest conclusion correctness, or Equity pair no-bias, according
to each unit's task. It is not an original-paper common accuracy metric.
M0/M1 rates for R1/R2/R3/R4 are **39.80/39.31%, 9.09/7.95%,
21.34/28.79%, 72.73/70.45%**. Deduplicated overall: **39.43/38.59%**,
denominator 2,161 per method after 9 shared NA exclusions. R4 denominator is
44 of 53 included units. Reasoning quality and independent-answer bias remain
separate, and original native metrics are also tabulated by R category.

Read `findings.md`（本地制品：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/findings.md`）,
`source_label_metrics.csv`（本地制品：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/source_label_metrics.csv`）
and `validation.json`（本地制品：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/validation.json`）.
The original full-scope directory `$CF_PACK/results_r1_r5_m0_m1_20260908/`
retains **30,844 R5-associated method predictions**, including historical reuse
and overlap with R1–R4. Its refreshed metrics are explicitly partial, and its
original 29,270 newly generated cache rows are unchanged. This local run has
not been published to GitHub. Luna max provided read-only supervision.

### Current full-release baseline comparison (completed 2026-09-07)

M0 Direct, M1 retrieval-only and M2 MedRGAG-Llama each completed **25,280/25,280
unique inputs (100%)**, covering 27,377 evaluation records per method and
75,840 unique method predictions. The user replaced the initial sampled plan
with the entire released test sets. M2 finished first; the previously stopped
M0/M1 were then completed with the same frozen inputs and configuration.

| Native benchmark / metric | Source groups or row units | Records per method | M0 | M1 | M2 |
|---|---:|---:|---:|---:|---:|
| MedEinst / canonical match | 5,383 | 10,766 | 10.93% | 7.75% | 8.26% |
| MedPIC / exact-set | 467 | 467 | 35.97% | 36.83% | 30.84% |
| CPV-MedQA / accuracy | 1,202 | 13,512 | 61.59% | 63.78% | 67.09% |
| Cultural-Cues / accuracy | 150 | 1,500 | 62.53% | 61.53% | 66.13% |
| MedCounterFact / evidence agreement | 203 | 1,012 | 66.31% | 61.87% | 66.50% |

Scores are source-group means. An additional frozen MedEinst 60-pair four-way
sensitivity contributes 120 records; M0/M1/M2 score 46.67% / 43.33% / 55.00%.
It is not a second benchmark or a substitute for native diagnosis. Exactly
identical visible inputs are inferred once; 2,097 duplicate label records
remain in evaluation.

The model is local Llama-3.1-8B-Instruct BF16, with the original tokenizer/chat
template, reader T=0/max_tokens=64, context capacity 98,304, and unchanged
per-input/stage seeds. M1 uses M2's initial source-balanced BM25/MedCPT top-5.
M2 retains retrieval/reranking, KGCC summaries and missing-knowledge exploration,
five complementary generations, original KADS, final reranking and reader.
All native options and mandatory item evidence are retained. No Profile,
CFShift scorer, CFMoE, MA-RAG/Qwen sidecar, judge, training or new method was
called. This is the local all-Llama reproduction, not an exact published
mixed-model SOTA reproduction.

M0/M1 each reuse 5,832 old predictions and add 19,448: **38,896 new calls**,
33,914,033 logical prompt tokens and 339,142 completion tokens. Completion
ran on H20 GPUs 0/2, vLLM 0.8.5, batch/chunk 64, for **45 min 14 sec**
(2026-09-07 18:44:08–19:29:22 CST); offline analysis finished at 19:31:50.
All M2 answers and upstream stage files stayed byte-identical. The earlier
M2 full-expansion batch's 15 h 32 min 01 sec is a separate historical cost.
Luna max performed read-only monitoring and the primary agent supervised and
accepted the run. Four contract/data/metric tests and full stage/cache/metric
audits passed; no pending predictions or transport failures remain.

The effects are mixed: M2 improves CPV versus Direct, loses on MedPIC and
MedEinst canonical matching, while Cultural and MedCounterFact M2−M0 intervals
contain zero. MedEinst M0/M1/M2 paired drops are +5.59 / +1.60 / +1.80 pp;
other overall paired-drop intervals contain zero. Cross-independent-source
taxonomy is NOT_IDENTIFIABLE. MedEinst has high unmapped-diagnosis rates;
CPV/Cultural share MedQA sources; MedPIC lacks a verified official pair map;
Cultural lacks released Neutral inputs; three MedCounterFact source groups
each lack one released variant category. Invalids remain scored under the
frozen protocol, and EA does not establish clinical safety. The native Holm
family expands from 29 M2-only tests to 87 three-method tests; M2 unadjusted
results remain identical, but its MedEinst adjusted p becomes .08494.

Read the [complete report](<../../../cf_medrgag_validation_pack/results_cf_full_comparison/findings.md>)
and `$CF_FULL/metrics.json`, `baseline_contract.md`, `acquisition.md`,
`execution_provenance.json`, `validation.json`, and `artifact_audit.json`.
Result commit: `3a6b5ab17505e5ed3cc506389282042d0ef15440`.
Published archive commit: `d92232428a0dd716bef9c55b5328262a4ca35c7b`, verified
on `origin/main` after pushing. The [GitHub full comparison archive](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-07_llama_full_test_three_methods)
contains 72 tracked result files plus its README. Published benchmark archives
use separate dated directories under `$CF_BENCHMARKS`, indexed by its README;
the current v3 package remains local under `$CF_BENCH_V3`.
The old M2-only full archive is preserved.

Implementation: `$CF_PACK/scripts/run_cf_baseline_screening.py` (including
`readers` mode), `prepare_cf_reader_completion.py`, and
`analyze_cf_baseline_screening.py`. The prepare/readers/analyze/audit command,
from `$CF_REPO`, is:

```bash
bash cf_medrgag_validation_pack/results_cf_full_comparison/commands.sh
```

Use existing artifacts for result/status questions. Raw inputs, separate gold
labels and durable prompt/document caches remain locally under `$CF_FULL`;
raw benchmark text, weights and the retrieval corpus were not uploaded.
`$CF_PACK/results_cf_screening` is the older sampled experiment, not full-test
coverage. The historical sections below retain earlier protocols and open
questions; this subsection records the latest completed scope.

### R1–R5 classification guide and completed expansion (2026-09-10)

For a new local conversation continuing classification, read
[R1_R5_CLASSIFICATION_GUIDE.md](<R1_R5_CLASSIFICATION_GUIDE.md>) first. It contains
the user's original five definitions, concrete decision rules, reviewed positive
examples and corrected counterexamples with original IDs, target-level annotation
and eligibility handling, and the local source files. The matching
[GitHub guide](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_full_coverage_plan/README.md)
is the published copy.

Keep v3 and all completed results. The completed classification covers eligible content
in the 15 acquired sources, including 24,436 candidates omitted by the old sampling
and renewed eligibility review of 18,238 already-classified R5 candidates deferred
by the old scope limit. The old 2,500 sampling rule and R5 size/source cap are
historical; they do not govern the next version. Evidence-based exclusions still
apply. The classification and qualification work is complete; read `$CF_CLASSIFIED_FULL/DELIVERY.md` and the latest-delivery section above. New model evaluation has not started.

### Source collection and five-label annotation archive (2026-09-08)

The source annotation collection, from which the current v3 subset derives, is
[`medical_cf_collection/README.md`](<../../2026-09-08_medical_cf_five_labels/README.md>),
indexed under `$CF_BENCHMARKS/2026-09-08_medical_cf_five_labels/`.
Published to [the independent GitHub folder](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-08_medical_cf_five_labels)
on `origin/main` at `cfe8246e4c759abf914867d2c92e1e016f007c84`.
The public archive contains 55,991 annotation records, the 28,243-unit reviewed
analysis set, 80,910 target annotations, audit/correction receipts and offline
prediction regrouping; native `original_records` and raw model responses stay
on the server. Necessary evidence quotations and official download locators
are retained. Its 9 gzip files and all exported ID/field correspondences passed
`scripts/verify_github_results.py`; this is package consistency, not a new
medical semantic audit. Text R5 is 20,318/25,746 (78.92%); AMQA, MedRGB and
MedPerturb supply 56.40% of text R5. See the archived R5 composition report.
The publication receipt（本地制品：`/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/reports/github_publication.json`）
records the verified remote commit and scope; the
[package validation](<../../2026-09-08_medical_cf_five_labels/reports/github_package_validation.json>)
records the 79-file release checks. The
[counting and R5 explanation](<../../2026-09-08_medical_cf_five_labels/reports/统计口径与R5分布.md>)
defines comparison units, source roots and missing-image metadata, and explains
why source-size sampling has not balanced the five labels.
It uses the user's medical-only five labels: R1 新增支持, R2 撤销支持,
R3 重新比较, R4 推导后果, R5 保持判断, at the question/comparison or
specific subjudgment level. Labels may overlap; uncertain records remain.

Independent audit on 2026-09-08 is now in
[`audit_20260908/README.md`](<../../2026-09-08_medical_cf_five_labels/audit_20260908/README.md>).
All 26 candidate sources and 2 cited medical controls have primary sources;
all 55,991 collected and 28,243 selected records reproduce independently
downloaded official originals. The initial 187-judgment audit found 92
confirmed classification problems. Follow-up corrections now update 172
judgments in 130 units, including same-rule siblings; 11 original references
are explicitly excluded from scoring. Native questions, gold and frozen
IDs are unchanged. See `audit_20260908/corrections/README.md` for current
results. `scripts/finalize_review.py` reapplies the three stable correction
files; `scripts/audit_collection.py` checks provenance and independent
post-correction review. The initial audit remains historical evidence.

The user clarified quantity: collect all acquired target subsets below 1,000,
and reduce very large sources around 5,000–10,000. The adopted implementation
also keeps 1,000–4,999 in full and takes 2,500 comparison units from pools of
5,000 or more; these defaults do not equalize sources or functional labels.
Keep complete raw files and normalized data.
The earlier 358-unit pilot was too small and is archived under `pilot_358/`.
It is no longer the current collection scope.

All 26 resources have acquisition records; 15 contribute collected data
(14 text sources and one missing-image multimodal source), while the specified
CF inputs of 11 candidates remain unacquired. The complete normalized archive
has 55,991 records: 53,494 text comparison records (including 97 flagged
non-CF/no-op records) and 2,497 MedMKEB edit metadata records with missing
images. The analysis subset has 25,746 text comparisons plus those 2,497
multimodal metadata records kept separately. The frozen 28,243 IDs and their
order now all have first-pass review decisions. Of the 25,746 text units,
21,695 have at least one classified target; 4,051 have reviewed reasons for
no label (2,129 insufficient evidence, 1,901 source problems, 21 outside the
five relations). Of the labelled text units, 1,127 still have unresolved
child targets. Text R1/R2/R3/R4/R5 counts are 2,030/88/389/53/20,318 and overlap.
The 2,497 missing-image metadata groups remain separate; all have partial
child coverage. Nonselected 27,748 archive rows retain preliminary status.
`review_method` distinguishes semantic item review, semantic group review,
and structural verification; all retain `clinical_review=false`. Current
child decisions are in `judgments`; old `target_annotations` and rule fields
are archived in `pre_review_annotation`. No expert agreement study was run.

All 25,280 old unique inputs and all 75,840 M0/M1/M2 predictions are
accounted for in `reports/旧库全部输入索引.jsonl`. The complete collection
links 17,949 comparisons to old predictions (7,341 in the analysis subset).
All 82,131 original evaluation-record/method rows were regrouped offline
using the original native parser and gold; zero new model calls or changed
inputs. References, GF, no-ops and historical sensitivity inputs remain
explicitly identified. The earlier full-test metrics remain authoritative.

Reuse the five original raw caches rather than downloading again. Newly
acquired fixed data include LabTest, HIV, MedPerturb, AMQA, DiversityMedQA,
EquityMedQA, MedRGB, BioRAB, MedCF and MedMKEB metadata. MedRGB is counted as
3,680 question groups preserving 36,800 document slots; MedCF retains all
splits but analysis uses all 798 actual test edits plus four unchanged test
records as references. Source roots, repeated variants and patients differ.
MamaBench access, CLIR official CF pairs, ECG MCo, and other documented
fixed-data gaps remain unresolved; GenMedicalEval's one public example is
separate and does not imply acquisition of its declared 12,000 entries.

Read `分析子集_逐题标注.csv`, `分析子集.jsonl`, `全部比较单元.jsonl`,
`医学CF资源清单.md`, `分类与抽样说明.md`, and `reports/` in the package.
Re-export the frozen annotations sequentially with `scripts/finalize_review.py`,
`scripts/reclassify_full_predictions.py` (the existing MedRGAG venv), and
`scripts/verify_full_collection.py`. The preliminary assembler is guarded
against overwriting reviewed data. `parts/*/build_full.py` expands cached
releases. Read `reports/分类审阅报告.md`, `分析子集_具体判断.csv`, and
`分析子集_未能定类.csv` for current decisions and limitations. Old pilot
scripts and pilot review reports are historical only. Complete-scope saved
prediction grouping includes preliminary nonselected annotations; use
analysis_subset for this reviewed cohort, retaining native task metrics.

### Historical adapter result (2026-09-05)

The earlier frozen 500-pair result was:

- MA-RAG intrinsic: 39.2%; MA-RAG + CF adapter: 80.0%, a +40.8 point
  difference with paired-bootstrap 95% CI +36.6 to +45.4;
- MedRGAG-style: 40.8%; MedRGAG + the same adapter: 82.4%, a +41.6 point
  difference with 95% CI +37.0 to +46.2;
- Profile-only: 79.4%; adapter without MA-RAG: 81.8%; consequently the result
  supports cross-interface transfer but **not** beneficial synergy with
  MA-RAG's own scores;
- the successful method is a pair-aware counterfactual sidecar, not a clinical
  world model, clinical safety system, official open-diagnosis result, or
  improvement on MA-RAG's original benchmark suite.

The result implementation was committed to `xiotakut/cf_mrg` at
`53aaff676439066f8d0b6478404c91e7ece3528f`. A later evidence handoff was
committed at `1e01b3a33c378041c64a76cce70ed381e4280d35`. Use the result commit
for code/result provenance and the handoff commit for the expanded data-lineage
and runtime audit.

The older completed 2026-08-23 WM-proxy study remains important historical
evidence. Its final prompt- and token-matched comparison was:

- blind direct ranking: 64/85 strict correct;
- WM-planner ranking: 64/85 strict correct;
- one improvement, one regression, 83 unchanged;
- delta 0.0 percentage points, bootstrap 95% CI -3.5 to +3.5, exact McNemar
  p=1.0;
- all temporary reviewer roles were distinct Luna Max agents, so artifacts
  remain `human_validated=false` and `grounding=parametric_no_nice`.

That decision is complete: those artifacts do not identify incremental value
from transition cards or a world-model planner over direct ranking. Stop the
world-model claim; retain only an exploratory
`action-aware/direct-ranking` signal. Do not rerun anything merely to learn
this conclusion.

Use these sources in this order:

| Question | Authoritative source |
|---|---|
| Where is the latest random evaluation selection? | `$CF_BENCH_V5/README.md`, `selected_targets.jsonl.gz`; use `evaluation_labels`, not semantic `labels` |
| Where is the expanded full-coverage classification? | `$CF_CLASSIFIED_FULL/DELIVERY.md`, `exports/all_reviewed_target_annotations.jsonl.gz`; target-level eligibility |
| What is the evaluated v3 benchmark and category allocation? | `$CF_BENCH_V3/README.md`, `manifest.json`, `units.jsonl`; use current `labels` |
| How do I load current questions, gold and saved results? | Section 1, “Load the current benchmark in a new conversation”; `$CF_BENCH_V3/items.jsonl`, `evaluation.jsonl`, `results/` |
| What are the current R1–R5 M0/M1 results? | `$CF_BENCH_V3/results/category_scores.csv`, `scored.jsonl`, `r1_r5_total.png` |
| What was the separate full-release comparison and claim boundary? | `$CF_FULL/findings.md`, `summary.md`, `metrics.json` |
| Where are benchmark publications? | `$CF_BENCHMARKS/README.md`; 2026-09-08 annotation archive and 2026-09-07 full comparison are published; v3 is local |
| Which data, exposure and source overlap were used in the full-release comparison? | `$CF_FULL/acquisition.md`, `data_checks.md`, `sample_plan.json`, `taxonomy.jsonl`, `source_overlap.json` |
| What was the historical adapter result? | `$CF_ADAPTER/summary.md`, `metrics.json`, `bootstrap.json` |
| What produced the current full comparison, and how was it accepted? | `$CF_FULL/commands.sh`, `baseline_contract.md`, `config.json`, `execution_provenance.json`, `validation.json`, `artifact_audit.json` |
| What did the historical adapter handoff add about reuse, cost and missing controls? | `$CF_REPO/chatgpt_handoff_2026-09-05/README.md` |
| Where is the full-release baseline implementation? | `$CF_PACK/scripts/run_cf_baseline_screening.py`; section 1 describes the v3 runtime boundary; section 11 describes the historical adapter |
| What was each earlier CF experiment? | Its own `results_*` directory and `summary.md`; see section 9 |
| What is the external MA-RAG revision and patch boundary? | `$CF_ADAPTER/commands.sh`, `marag_logging.patch`, and `marag_retriever_compat.patch` |
| What was planned? | `$WM_ARCHIVE/medrgag_wm_validation_pack/PROJECT_PLAN.md` |
| What was actually run and concluded? | `$WM_ARCHIVE/medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md`, especially sections 15–18 |
| What is the final numerical result? | `$V4/p4_matched_rank_greedy_reader_summary.json` |
| What is the frozen v15 boundary consumed by the WM study? | The same v4 directory's `p2_v15_item_results.jsonl`, `p2_v15_baseline_results.json`, and `p4_proxy_all85_input.jsonl` |
| How did the full all-Llama v15 baseline run? | `MedRGAG/REPRODUCE_ALL_LLAMA.md`, the completed runtime state, and the v15 `metrics.json` described below |
| What was transferred to GitHub? | `$WM_ARCHIVE/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/README.md` and `FILE_INDEX.md` |

The files named `ARCHIVED_*IMPLEMENTATION_CONTRACT.md` preserve old proposed
study contracts. They are research history, not active coding-agent
instructions. Their stages and gates must not restart stopped work.

## 2. Data flow

```text
paper + upstream MedRGAG
          |
          v
/home/data3/txy/MedRGAG
completed five-dataset all-Llama v15 baseline
          |
          | frozen selected documents and item results
          v
archived WM workspace/private_data/.../stage-b-real-20260823-seed13-37-v4
          |
          | 85-item input -> state/cards/rankings -> reader outputs
          v
matched direct-ranking vs WM-planner result and stop decision
          |
          v
mrg-handoff-upload -> https://github.com/xiotakut/mrg

current full-release baseline path:

MedEinst + MedPIC + CPV + Cultural + MedCounterFact
   -> independent native inputs -> Direct / initial retrieval-only / full MedRGAG
   -> complete three-method comparison -> cf_mrg/benchmarks/<dated-run>/

historical pair-aware CF path:

MedEinst control/trap pairs + DDXPlus profiles
          |
          +-> DeltaRev -> DeltaRank -> CFShift -> CF-KADS-MoE -> RiskRoute
          |                      (iterative MedRGAG-side experiments)
          |
          +-> frozen Profile/CPG sidecar ---------------------+
          |                                                   |
          +-> MedRGAG-style four-option base scores ----------+-> linear
          |                                                   |   option fusion
          +-> external MA-RAG Qwen3-8B candidate pools -------+
                                                              |
                                                              v
                                      frozen 500-pair MedEinst later test
                                      + legacy-exposure caveat
                                      + transfer / no-synergy conclusion
```

## 3. Top-level directory map

| Path | What it is | Main interface |
|---|---|---|
| `$CF_ITERATIVE` | **M6 = i-MedRAG** (`imedrag`), **M7 = TC-RAG** (`tcrag`), registered in the existing CF pack; 19 tests and 24 real development inputs per method completed, with output/scoring and coverage limitations still recorded. Preserves all pilots and source snapshots; no formal full run. | [Paper implementation and adjustment record](<../m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md>), `README.md`, `method_fidelity.md`, `acceptance_report.md`, `configs/*runtime_v4.json` |
| `/home/data3/txy/MedRGAG` | Upstream `ll0ruc/MedRGAG` checkout plus the local all-Llama reproduction, corpora, indexes, v15 runner, logs, and outputs. | `REPRODUCE_ALL_LLAMA.md`, `run_medrgag_all_llama.sh`, completed v15 `metrics.json` |
| `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag` | Standalone `gzxiong/MedRAG` installation: **M4 = MedRAG-Llama-3.1-8B** (`medrag_llama31`), **M5 = MedRAG-Qwen3-8B** (`medrag_qwen3`). Original M4 RRF-4 passed Textbooks smoke; Wikipedia MedCPT completed, Contriever/SPECTER stopped with partial files retained. Subsequent V5 uses matching full-MedCorp BM25/MedCPT settings for M4/M5 and completed 13,905 inputs each; use the V5 run configs for those results. The report now maintains the action history, before/after changes, evidence and paper methods drafts (updated 2026-09-13); append subsequent M4/M5 work there as requested by the user. | [Installation and paper implementation record](<../m4_m5_implementation/M4_M5_INSTALLATION_REPORT.md>), `BASELINES.md`, historical `configs/m4.json` / `configs/m5.json` |
| `$CF_REPO` | Git repository `https://github.com/xiotakut/cf_mrg`; later CF experiments, integration scripts, compact public results, and handoffs. | `$CF_FULL/findings.md`, `$CF_BENCHMARKS/README.md`, `$CF_PACK/README.md` |
| `$MARAG` | External official MA-RAG checkout at upstream commit `423f031cc0ffca679a047c885be999b9604100a9`; not vendored into `cf_mrg`. | upstream `ma_rag_entropy.py` plus the two recorded patches in `$CF_ADAPTER` |
| `/home/data3/txy/Documents` | User documents; its `Codex/2026-08-23/...ponytail-skill` child is the archived WM experiment workspace. | See section 5 |
| `/home/data3/txy/models` | Local model weights. These are runtime inputs, not source code. | Pass a local path through `P4_MODEL` or the MedRGAG runner's model argument |
| `$CF_REPO/chatgpt_handoff_2026-09-05` | Historical adapter evidence handoff, including the dataset reuse audit and timing decomposition. | `README.md` |
| `/home/data3/txy/Li - 2026 - From Retrieval to Generation Unifying External and Parametric Knowledge for Medical Question Answer.pdf` | The research paper being reproduced/extended. | Read-only research source |
| `/home/data3/txy/.codex` | Codex application state, installed skills, plugins, and thread metadata. Ponytail is installed under `.codex/skills/ponytail`. | Managed by Codex; not a project source tree |
| `/home/data3/txy/.local` | User-installed binaries and libraries; GitHub CLI is `.local/bin/gh`. | Runtime/tooling only |
| `/home/data3/txy/.cache` | Hugging Face, Python, and application caches. | Reusable cache; not authoritative output |
| `/home/data3/txy/.config`, `.copilot`, `.dotnet`, `.modelscope`, `.nv`, `.vscode-server` | Per-user tool/runtime configuration. | Not MedRGAG source |
| `/home/data3/txy/.ssh` | SSH configuration and credentials. | Outside project scope unless explicitly requested |
| shell dotfiles such as `.bashrc`, `.profile`, `.gitconfig` | User shell and Git configuration. | Environment configuration, not experiment evidence |

## 4. Full all-Llama MedRGAG baseline

### Purpose and status

`/home/data3/txy/MedRGAG` is the full local baseline implementation. Its
tracked upstream commit is
`0057853df65dcaa46d2934a28f8d5025fc3de623`; the local reproduction code and
reports are currently untracked additions, so never use `git clean`, reset,
or checkout to remove them.

The completed v15 run is:

```text
/home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/
  all-llama31-8b-released-code-intent/
  role-stable-v15-guided-sentence-labels/
  all-llama-five-dataset-lenient-v1/
```

It completed all eight stages over 7,663 questions with exit code 0:

```text
retrieval -> summary -> explore -> generate -> select -> rerank -> reader -> evaluate
```

The run root contains `manifest.lock.json`, per-dataset `artifacts/`, and
`metrics.json`. The metrics report strict macro accuracy 69.9034% and author
macro accuracy 70.0297%; this is explicitly
`experimental_not_table1=true`, not an exact paper Table 1 reproduction.

`MedRGAG/LLAMA31_REPRODUCTION_HISTORY.md` is a 2026-08-17 historical
conversation/checkpoint document. Its bottom-line “not started” text predates
the completed run above. Use it for implementation history only; runtime state
and `metrics.json` override it for current status.

### Command interface

Read-only status:

```bash
cd /home/data3/txy/MedRGAG
./run_medrgag_all_llama.sh status \
  --run-id all-llama-five-dataset-lenient-v1
```

The shell interface is:

```text
run_medrgag_all_llama.sh [start|status|attach]
  --run-id ID
  [--datasets medqa medmcqa mmlu pubmedqa bioasq]
  [--limit N]
  [--retrieval-source-run PATH]
  [--from-stage STAGE] [--to-stage STAGE]
  [--dry-run]
```

`status` reads the state file; `attach` tails the log; `start` or the
default foreground mode executes stages and is expensive. The stage-level
Python interface is:

```text
.venv/bin/python reproduce_medrgag_all_llama.py
  --run-id ID
  --stage {retrieval,summary,explore,generate,select,rerank,reader,evaluate}
  ...
```

Do not overwrite the completed v15 run. New execution requires a new run ID
unless explicitly resuming the same unchanged run after a technical failure.

### Main implementation files

| File | Function |
|---|---|
| `run_medrgag_all_llama.sh` | Eight-process orchestration, status/log files, stage range, background start |
| `reproduce_medrgag_all_llama.py` | Stage CLI and all-Llama five-dataset pipeline |
| `src/medrgag_local_aux.py` | Local Llama auxiliary roles |
| `src/medrgag_logic.py` | Prompt formatting, selection parsing, reader rendering, answer parsing |
| `src/medrgag_retrieval.py` | BM25 corpus retrieval and MedCPT reranking |
| `src/medrgag_artifacts.py` | Per-stage records, manifests, completion markers, resume behavior |
| `REPRODUCE_ALL_LLAMA.md` | Current runner semantics and commands |
| `ALL_LLAMA_V15_AUDIT.md` | v15 prompt/output quality audit |

## 5. Archived WM experiment workspace

The archived experiment workspace is:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-dietrichgebert-ponytail-skill/
```

The long directory name reflects the original Ponytail installation task; it
now also contains the MedRGAG WM work. This directory itself is not a Git
repository.

| Child | Role and authority |
|---|---|
| `medrgag_wm_validation_pack/` | Authoritative plan, prompts, schemas, reusable Python modules, P4 runner, and the renamed protocol/results record |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/` | Canonical 22 MB v4 experiment inputs, proxy review artifacts, predictions, scored results, and summaries |
| `mrg-handoff-upload/` | Clean clone of `https://github.com/xiotakut/mrg`; the handoff was pushed at commit `c86ec675a3948af430a099c7c5a14abdffe236d5` |
| `medrgag_validation_pack/` | Early three-file minimal scaffold; not the authoritative WM plan or result |
| top-level `src/`, `scripts/`, `tests/` | Empty/legacy shells; the archived implementation is inside `medrgag_wm_validation_pack/` |
| `medrgag_wm_validation_pack.zip` | Small early snapshot; not the current experiment record |

Important path rule: the source P4 runner sets `WORKSPACE` to the parent of
`medrgag_wm_validation_pack`, so its canonical `RUN` is the sibling
`private_data/.../stage-b-real-20260823-seed13-37-v4`, not the nearly empty
`medrgag_wm_validation_pack/private_data`.

### Pack components

| Part | Function/interface |
|---|---|
| `PROJECT_PLAN.md` | User-selected experimental plan and decision logic |
| `ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md` | Archived coding-agent contract for the proposed full implementation; not active instructions |
| `WM_VALIDATION_PROTOCOL_AND_RESULTS.md` | Sections 1–14 protocol; sections 15–18 actual proxy experiments and final decision |
| `configs/` | Formal M0–M10 experiment matrix and proposed no-go criteria; not required to interpret the completed P4 result |
| `prompts/` | Files 01–17: slice classification, state/action extraction, retrieval, transition, planning, reader, judging, counterfactual, and P4 context |
| `schemas/` | JSON Schemas for action labels, clinical state, transition cards, judgments, and final answers |
| `src/data/` | Item loading, slice construction, and matched-control helpers |
| `src/medrgag_adapter/` | Answer-free baseline adapter, external v15 binding, single-GPU and local-Llama adapters |
| `src/wm/` | State/action construction, query planning, evidence retrieval, transition-card generation, rollout selection, and routing |
| `src/controls/` | Action decomposition, equal-reasoning, extra-retrieval, and shuffled-transition controls |
| `src/evaluation/` | Accuracy, paired statistics, fidelity, counterfactual, faithfulness, and cost helpers |
| `src/experiment_runner.py` | M0–M10 registry and `dispatch_variant` / `dispatch_all` shared-reader API |
| `scripts/` | CLI preparation, binding, execution, aggregation, status, and P4 historical runners |
| `tests/` | Unit/integration checks for the proposed reusable pack; they are not the source of the completed P4 numerical result |

### Core Python interfaces

```text
construct_state(Item, action_label) -> clinical_state dict
construct_actions(state) -> list[{candidate_id, text, ...}]
transition_with_provider(...) -> (transition_card | None, metadata)
select_rollout(item_id, decision_mode, cards, allow_unsupported=False) -> planner dict
dispatch_variant(MethodSpec, VariantContext, reader, seed=13) -> prediction dict
paired_bootstrap(a, b, samples=10000, seed=13) -> paired statistics
exact_mcnemar(a, b) -> discordant counts and exact p-value
```

`select_rollout(..., allow_unsupported=True)` is the interface used for the
parametric Luna cards. It is not NICE grounding.

### P4 runner interface

`medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py` is a historical
fixed-path runner. It refuses to overwrite existing output files.

| Environment setting | Condition |
|---|---|
| none | 20-item M0/M1/PX pilot |
| `P4_ALL85=1` | 85-item M0/M1/PX |
| `P4_ADJUDICATED=1` | 20-item Luna-adjudicated PA |
| `P4_ALL85_ADJUDICATED=1` | 85-item PA |
| `P4_ALL85_ABLATIONS=1` | M2/M4/M5/M6/MR ablations |
| `P4_ALL85_DIRECT_RANK=1` | direct Luna ranking reader |
| `P4_ALL85_MATCHED_RANK=1` | matched direct/planner ranking |
| matched rank plus `P4_MATCHED_GREEDY=1` | accepted temperature-0, single-call deduplicated comparison |
| an all-85 mode plus `P4_CPU_PREFLIGHT=1` | input/prompt validation without GPU inference |
| `P4_MODEL=/absolute/model/path` | override the local reader model |

Existing files already occupy every completed mode's output path. Treat this
runner as provenance unless the user explicitly requests a new run design.

### JSONL interfaces

All identities are the pair `(dataset, item_id)`.

| Artifact | Required top-level fields and meaning |
|---|---|
| `p4_proxy_all85_input.jsonl` | `dataset,item_id,question,options,action_label,medrgag_documents`; answer-free frozen reader input |
| `p2_v15_item_results.jsonl` | frozen 1,000-item v15 predictions, gold, correctness, tier and task labels |
| `p4_luna_adjudicated_all85_cards.jsonl` | `state,parametric_transition_cards,planner,adjudication,proxy_review` plus identity/provenance |
| `*_reader_predictions.jsonl` | raw response, parsed predictions, condition, sampling and token metadata; no scored correctness |
| `*_reader_results.jsonl` | prediction rows joined with gold and correctness |
| `*_reader_summary.json` | aggregated condition metrics and paired comparisons |

The state object exposes
`initial_state,candidate_actions,candidate_outcomes,fixed_action,transition_target,decision_mode,clinical_goal,facts_not_to_assume`.
A transition card exposes
`candidate_id,action,preconditions,next_state,applicability,coverage,goal_alignment,uncertainty_reasons,unsupported_claims,rollout_valid,compact_rollout`.
The planner exposes
`preferred_candidate_id,candidate_scores,decision_mode,decision_rationale,abstain,abstention_reason,grounding`.

## 6. GitHub handoff

Local clone:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload
```

Remote: `https://github.com/xiotakut/mrg`, branch `main`.

The handoff entry is
`handoff/medrgag-wm-2026-08-23/README.md`; `FILE_INDEX.md` describes all
104 handoff files, and `CONVERSATION_HISTORY.md` contains only user/assistant
visible conversation. The handoff is a transfer copy, while the sibling
workspace paths in section 5 are the canonical local archive. Its copied results
record is `medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md`.

## 7. Model inputs

| Path | Use |
|---|---|
| `models/LLM-Research-Meta-Llama-3.1-8B-Instruct` | Complete local reader/generator checkpoint used by the v15 and P4 runs |
| `models/NousResearch-Meta-Llama-3.1-8B-Instruct` | Alternate downloaded Llama repository; do not silently substitute it for the recorded checkpoint |
| `models/Qwen3-8B` | Backbone used by the external MA-RAG intrinsic runs |
| `models/ncbi-MedCPT-Cross-Encoder` | Local MedCPT reranker |

Models are large runtime dependencies and should not be copied into Git
handoffs.

## 8. Fast start for a new conversation

1. Read this file.
2. Run `git status --short` in the source tree you will touch. Several project
   trees coexist, and another agent's uncommitted work must be preserved.
3. Decide whether the request concerns the v15 baseline, archived WM study,
   later CF experiments, MA-RAG integration, i-MedRAG/TC-RAG reproduction, or a
   GitHub handoff. For i-MedRAG/TC-RAG, use `$CF_ITERATIVE/PAPER_REPRODUCTION_RECORD.md`
   and the implementation/development entry in section 1; it records actual
   changes and paper-writing evidence without requiring new inference.
4. For the latest expanded classification, read `$CF_CLASSIFIED_FULL/DELIVERY.md` and
   `exports/all_reviewed_target_annotations.jsonl.gz`. For completed v3 evaluation results, read `$CF_BENCH_V3/README.md`,
   `manifest.json`, `units.jsonl` and `results/category_scores.csv`. Use the
   tested read-only loading example in section 1. For a request specifically
   about the full-release comparison, use `$CF_FULL`; the 2026-09-05 handoff
   and `$CF_ADAPTER` describe historical adapter work.
5. For result questions, inspect the existing JSON/CSV output; do not launch a
   model. For weight, threshold, category, or subgroup analysis, reuse saved
   per-item scores and predictions offline.
6. For current baseline code, trace the entry and contract in section 1.
   Section 11 describes historical adapter interfaces.
   Keep upstream MA-RAG external and keep baseline and native-variant outputs
   under distinct method names/directories.
7. Run a new experiment only when the user explicitly requests one. State the
   full cumulative work, remaining ETA, and whether it is core or supplemental
   before starting a multi-hour block.
8. Use a new output/run identity unless explicitly resuming the same frozen run
   after a technical failure. Never overwrite canonical results.

The old shorter rule still applies to the archived WM branch:

1. Decide whether the request concerns the v15 baseline, the WM experiment,
   or the historical `mrg` GitHub handoff.
2. Read only the corresponding authoritative document from section 1.
3. For result questions, inspect the existing summary JSON; do not launch a
   model.
4. For code changes, trace the relevant public interface listed above and
   preserve the canonical v4 artifacts.
5. Run a new experiment only when the user explicitly asks for one; use a new
   output/run identity rather than overwriting recorded results.

## 9. Later counterfactual project chronology

The Git repository for the later work is:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-xiotakut-cf-mrg
remote: https://github.com/xiotakut/cf_mrg
branch: main
```

The experiments were iterative. Development sets and cached model outputs were
deliberately reused, so successive commits are not independent replications.

| Commit | Experiment | Data and purpose | Result |
|---|---|---|---|
| `b714735` | revised gold-free transition/WM test | 303 held-out items across MedPIC, CLIR, MedEinst, MedCounterFact | Negative: full transition 20.8%, below the local MedRGAG proxy at 31.7% |
| `f2652d0` | DeltaRev-MedRGAG | 40 development + 160 test MedEinst pairs | No useful repair; hard fail-closed behavior; no WM support |
| `c5b20e2` | DeltaRank-MedRGAG | 300 development + 300 test pairs | Four-way base 45.33%; residual +1.0 point, 5 repairs and 2 harms |
| `9768abe` | CFShift-MedRGAG | 800 development + 200 calibration + 500 fresh pairs | Profile signal strong; pure shift added only 0.2 point and its CI crossed zero |
| `1b95f9b` | CF-KADS-MoE | reused 800/200 + 1,000 fresh pairs | Profile 77.7%; learned fusion 78.5%, a nonsignificant +0.8 point; MedPIC transfer negative |
| `212866d` | RiskRoute-CF | reused 800/200 + another 1,000-pair test | Router 73.3% versus Profile 74.3%; no risk/accuracy Pareto improvement |
| `53aaff6` | CF-Residual Adapter for MA-RAG | 400 development + 150 calibration + 500 later test pairs | Large base-to-adapter gains on both interfaces; no MA-RAG synergy |
| `1e01b3a` | evidence handoff | no inference | Added the dataset-lineage, fairness, timing, asset, and missing-control audit |
| `638f1e3`, archive `6a174dc` | full-release M2 baseline | 25,280 unique inputs, five entries plus frozen sensitivity | Complete M2; native protocols, no sidecar; M0/M1 then partial |
| `79a9454`, result `3a6b5ab`, archive `d922324` | full M0/M1/M2 comparison | Same 25,280 inputs per method; 38,896 missing reader calls added | 100% all methods; M2 unchanged; heterogeneous effects, taxonomy not identifiable |

The historical adapter trajectory through 2026-09-05 was:

```text
old transition/world-model route: stopped after negative evidence
        |
        v
control-to-trap option-score change + disease profile: consistently strong
        |
        v
CPG and small forced-choice score fusion: portable sidecar
        |
        v
MedRGAG-style and MA-RAG interface evaluation on one MedEinst MCQ protocol
```

Do not describe this trajectory as five-dataset success. Its positive
evidence is concentrated on MedEinst. MedPIC transfer was negative, while
ReMedQA served as a static/invariance control.

## 10. Counterfactual datasets, actual use, and split lineage

Three different “five dataset” phrases occur in this workspace:

- the all-Llama MedRGAG baseline's five ordinary medical-QA datasets are
  MedQA, MedMCQA, MMLU, PubMedQA, and BioASQ;
- the historical CF plan had five **roles**: MedPIC, CLIR, MedEinst,
  MedCounterFact, and one invariant-control role containing ReMedQA plus
  CPV/MedEqualQA;
- the 2026-09-07 full baseline comparison uses MedEinst, MedPIC, CPV-MedQA,
  Cultural-Cues and MedCounterFact, with complete counts in section 1.

The Gate-A table and subsections below describe historical subsets, not the
current full-test coverage. Sections 11–16 retain the historical adapter and
MA-RAG implementation, results, cost and open-question record.

Gate A actually froze six named sources because ReMedQA and CPV were prepared
separately. MedEqualQA was discussed but not run.

| Source | Pinned revision | Raw rows observed | Prepared subset |
|---|---|---:|---:|
| MedPIC | `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983` | 467 | 467 rows |
| CLIR | `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` | 3,000 in the pinned snapshot | 500 rows, t6–t10 with 100 each; only t6/t8 had usable observations |
| MedEinst | `354f4b527e764a8f2bebea8f71be55e0a6966402` | 10,766 | 500 pairs / 1,000 rows; upstream total 5,383 pairs |
| MedCounterFact | `f35b98063b51a63e677829b6d173029d98dd3b1e` | 1,012 | 200 pairs / 400 rows |
| ReMedQA | `3abb4b47a5859c7b46c0a1872a58c82e2e3029e3` | 5,036 | 300 IDs / 1,200 rows |
| CPV | `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5` | 12,310 | 300 case IDs / 3,010 rows |

The exact source report is `$CF_PACK/GATE_A_RESULTS.md`. Raw public-source and
private clinical caches are intentionally ignored by Git.

### 10.1 Model-inference coverage beyond MedEinst

The balanced Gate-B pilot passed only 60 items through inference:

```text
MedPIC 10, CLIR 10, MedEinst 20, MedCounterFact 16, ReMedQA 2, CPV 2
```

The revised gold-free heldout run used 78 MedPIC, 79 CLIR, 72 MedEinst, and
74 MedCounterFact items. The later CF-MoE secondary checks used all 467 MedPIC
rows and 400 ReMedQA variant rows. None produced a broad positive
cross-dataset CF conclusion.

### 10.2 MedEinst split reuse

One modern MedEinst JSONL row is one `(control, trap)` pair. MA-RAG turns that
pair into three separate records: control, trap, and pair prompt.

| Experiment | Development | Calibration | Later test |
|---|---:|---:|---:|
| DeltaRev | 40 | — | 160 |
| DeltaRank | 300 | — | 300 |
| CFShift | 800 | 200 | 500 |
| CF-KADS-MoE | same 800 | same 200 | 1,000 |
| RiskRoute | same asset family | same asset family | 1,000 |
| MA-RAG CF-Residual | first 400 of the reused 800 | first 150 of the reused 200 | 500 |

All DeltaRank development IDs are inside the later 800-row development set.
CFShift and CF-MoE development/calibration files are identical. RiskRoute
learned from the same feature family. These are valid iterative-development
assets, not independent confirmations.

The five later test files for DeltaRank, CFShift, CF-MoE, RiskRoute, and
MA-RAG are pairwise disjoint by `source_case_id`, totaling 3,300 IDs. The old
DeltaRev test was omitted from the later exclusion code, however: 115 of its
160 IDs were later reused, including seven in the MA-RAG 500-pair test. The
MA-RAG test also contains exact pair `case_180796` from earlier CFShift/CF-MoE
calibration. There are nine conservatively exposed rows in total when all old
DeltaRev rows plus that prior-calibration duplicate are removed.

An offline sensitivity on the remaining 491 rows, without refitting or model
reruns, gives:

| Method | Original 500 | Conservative 491 |
|---|---:|---:|
| MA-RAG | 39.2% | 39.51% |
| MA-RAG + adapter | 80.0% | 79.84% |
| Profile-only | 79.4% | 79.02% |
| Adapter without MA-RAG | 81.8% | 81.87% |
| MedRGAG-style | 40.8% | 40.53% |
| MedRGAG + adapter | 82.4% | 82.48% |

The 491-row adapter-minus-base differences remain large: +40.33 points for
MA-RAG, 95% CI +35.64 to +44.81, and +41.96 points for MedRGAG, 95% CI
+37.27 to +46.84. This sensitivity is audit evidence only and did not replace
the canonical 500-row results.

The broad “zero overlap with every earlier use” wording in older summaries is
therefore not literally correct. The detailed audit in
`$CF_REPO/chatgpt_handoff_2026-09-05/README.md` supersedes it.

## 11. Implemented CF-Residual Adapter functionality

The current integration added six focused scripts and one test module. It did
not vendor MA-RAG or alter the existing MedRGAG/CF formulas.

The implementation boundary was deliberately small: reuse the existing
Profile/CPG sidecar unchanged, add normal forced-choice fusion, and isolate any
MA-RAG-native behavior under separate names. The task explicitly excluded new
world models, transition cards, NICE/atomic-rule systems, the old 27-method
matrix, large MoE routers, hard preserve/revise gates, hash registries, generic
retry frameworks, and multiple timestamped result trees.

| File | Implemented behavior |
|---|---|
| `$CF_PACK/scripts/prepare_marag_medeinst.py` | Reuses the existing MedEinst loader and deterministic four-option construction; emits control, trap, and pair-prompt MA-RAG records plus one shared mapping; selects dev/cal/test while excluding configured later-test/current-train IDs |
| `$CF_PACK/scripts/parse_marag_outputs.py` | Reads completed MA-RAG rounds, preserves candidate text and entropy, computes vote counts, consensus, cost fields, and official strict-majority output; exact ties are explicit invalids rather than gold-resolved answers |
| `$CF_PACK/scripts/run_marag_cf.py` | Implements `smoke`, `fit`, `predict`, and `export-scores`; builds smoothed vote and entropy-weighted distributions, z-normalized option features, linear fusion, uniform controls, no-base ablations, and shuffle controls |
| `$CF_PACK/scripts/evaluate_marag_cf.py` | Computes accuracy, paired correctness, BTR, old-answer persistence, correct flips, repairs, harms, conditional harm, preservation, false consensus, efficiency, and 1,000-sample paired bootstrap |
| `$CF_PACK/scripts/run_cf_marag_native.py` | Contains separate native variants: pure residual trigger, delta-aware query, CF history ranking, and their full combination; never overwrites official baseline outputs |
| `$CF_PACK/scripts/run_marag_retriever.py` | Starts the upstream retriever once and avoids upstream script-mode double initialization/JNI option duplication |
| `$CF_PACK/tests/test_marag_cf.py` | Checks mappings, tie handling, no-gold inference, scorable continuous ties, invalid exclusions, trigger semantics, costs, and score export |

### 11.1 Four-option and sidecar contract

Each pair has exactly the same A–D mapping for every base/method:

```text
trap diagnosis
control diagnosis
two deterministic DDXPlus-profile-overlap hard negatives
```

The trap-only MA-RAG baseline sees only the trap case. The pair-prompt baseline
sees control, trap, and structured changed findings. The Profile/CPG sidecar is
also pair-aware and uses a separate Llama-3.1-8B scoring path.

Ignoring an option-independent constant, `profile_no_document` is:

```text
2 * direct_trap_option_score
- direct_control_option_score
+ 2 * standardized_delta_profile_alignment
```

The profile term rewards added findings aligned with a diagnosis and penalizes
removed findings. It uses DDXPlus profiles and no MA-RAG retrieved documents.

CPG reuses the counterfactual edit/probability-gap idea from
`FAIRHealth/clinical-counterfactual-reasoning` at
`265d1aea88f705063bb7ff2d686547d373da7e09`. This implementation applies up to
two deterministic remove/revert/negate edits and scores exact option-sequence
likelihood changes. It does not claim to invent CPG or reproduce the full
multi-agent method.

### 11.2 Portable methods

`run_marag_cf.py predict` produces these main methods from one frozen score
cache:

```text
marag_int_control
marag_int_trap
marag_int_pair_prompt
profile_only
cpg_core
marag_profile_uniform
marag_profile_cpg_uniform
marag_cf_learned
marag_cf_without_marag
marag_cf_shuffled_delta
marag_cf_shuffled_profile
marag_cf_shuffled_cpg
medrgag_baseline
medrgag_profile_uniform
medrgag_profile_cpg_uniform
medrgag_cf_learned
medrgag_cf_without_medrgag
```

For MA-RAG, per-option learned feature groups are:

```text
vote_score(a) = log((count(a) + 0.5) / (N + 2.0))
candidate_weight(i) = exp(-mean_entropy(i) / temperature)
entropy_score(a) = log(normalized sum of weights predicting a)
```

Each expert's four scores are z-normalized within the question before fusion.
The official majority prediction remains unchanged; continuous vote scores are
adapter inputs only.

The learned feature groups are:

```text
normalized vote score
normalized entropy-weighted vote score
normalized Profile score
normalized CPG score
vote x consensus strength
entropy vote x rounds used
Profile x MA/Profile top-1 agreement
Profile x Profile margin
CPG x availability
```

Development fits the scalar entropy temperature and linear coefficients.
Calibration selects L2 from `{0, 0.01, 0.1, 1}`. The frozen selection is
entropy temperature `0.05000032401354733` and L2 `0` for the main MA and
Med variants. Fresh inference does not refit.

This is ordinary forced-choice score fusion, not a preserve/revise gate. Every
runtime-valid item receives four scores and selects their argmax. There is no
default preserve behavior or silent baseline fallback.

### 11.3 Invalid and tie semantics

- Official MA-RAG uses strict majority behavior. A 4–4 or other top-count tie
  is `status=invalid`, with candidates and vote counts retained for diagnosis.
- A complete tie with all eight valid candidates, finite entropy, finite
  four-option scores, and vote total eight is still a valid continuous-score
  input to the forced-choice adapter. It is not converted into an official
  baseline prediction.
- Parse failures, incomplete pools, and runtime failures remain invalid for
  both baseline and adapter. They are never replaced with gold or a base
  prediction.
- Profile/CPG disagreement uses three states. An unavailable score is excluded
  from its disagreement denominator rather than treated as agreement.
- Efficiency summaries include only rows with all required finite cost fields
  and state their denominator/excluded count.
- `full_cf_marag_native_plus_adapter` uses full native as its own repair/harm
  reference; comparisons against original MA-RAG remain separate bootstrap
  contrasts.

### 11.4 Native MA-RAG variants

The official baseline code path was kept separate. Native behavior lives only
in `run_cf_marag_native.py` and separately named output roots.

- `cf_trigger_only`: after validating and reusing the complete official
  baseline history, append exactly one ordinary official-query round only when
  the final pool is unanimous, Profile disagrees above the frozen threshold,
  and round budget remains. It does not expose delta/challenger text.
- `delta_query_only`: retains normal candidate-conflict information and adds at
  most two changed-finding/challenger queries while keeping at most four total
  queries and eight documents.
- `cf_history_ranking`: adds normalized Profile/CPG scores for a candidate's
  predicted option to original `-mean_token_entropy` quality.
- `full_cf_marag_native`: combines the selected trigger, query, and ranking
  mechanisms.

Gold is never passed to the native inference judger or ranking feature path.
Baseline reuse requires source metadata and a complete first-round candidate
pool. Pilot grid selection froze Profile threshold 1.0, beta-Profile 0, and
beta-CPG 1.0.

## 12. MA-RAG environment and execution contract

The external checkout is `/home/data3/txy/MA-RAG` at upstream commit
`423f031cc0ffca679a047c885be999b9604100a9`. The two intentional upstream
runtime changes are stored as reproducible patches in `$CF_ADAPTER`:

- `marag_logging.patch`: preserves detailed per-round candidate and cost logs;
- `marag_retriever_compat.patch`: supports the locally available corpus/index
  layout and MedCorp3 naming.

The checkout also had an untracked local corpus symlink. Do not clean or reset
it without inspecting the exact targets. Do not copy the checkout into
`cf_mrg`.

### 12.1 Actual main configuration

```text
MA-RAG variant: intrinsic
backbone: local Qwen3-8B
candidate pool N: 8
maximum rounds T: 4
solver thinking: disabled
solver temperature: 0.7
solver max new tokens: 2048
query-generator thinking: enabled
query temperature: 0
query max new tokens: 8192
retrieval: BM25 + MedCPT-Cross-Encoder
corpus: MedCorp3 = PubMed + textbooks + Wikipedia
```

The checked-out MA-RAG script defaults to `T=8`; the experiment explicitly
used `T=4` as the user-approved cost-effective setting. It is not an exact
full-table reproduction. The extrinsic evaluator was not run because its
official checkpoint was unavailable.

The local StatPearls archive was truncated/corrupt: `gzip -t` failed and
`tar -tzf` stopped after 48 members. It was therefore excluded and the corpus
is correctly called **MedCorp3**, never full MedCorp. Do not silently claim
otherwise.

The 100-item original MedQA operational check used N=4/T=2 and returned 72.0%
accuracy. It verified candidate generation, retrieval, round logging, stopping,
and strict-majority evaluation; it is not a paper-table reproduction. A
textbooks-only 76% diagnostic was also observed but is not the official main
check.

### 12.2 Service layout used

```text
GPU 0: Llama sidecar during fresh scoring
GPU 1: Qwen3-8B OpenAI-compatible service on port 8011
GPU 2: Qwen3-8B OpenAI-compatible service on port 8012
GPU 3: MedCorp3 BM25/MedCPT retriever on port 8993
```

Qwen service settings were bfloat16, max model length 32,768, max 16 sequences,
GPU memory utilization 0.82, seed 223, and prefix caching enabled. Four
disjoint data shards ran concurrently, two client runners per Qwen endpoint,
with eight client workers each. The Llama sidecar used GPU utilization 0.55.

The base environment eventually contained Transformers 5.16.1, which was
incompatible with vLLM 0.8.5 for this Llama checkpoint. The successful sidecar
run prepended `/home/data3/txy/.cache/marag_pydeps`, which pins Transformers
4.51.3. Reuse the exact command record instead of rediscovering this failure.

All task Qwen/retriever services were stopped after the final push. Ports
8011, 8012, and 8993 had no listeners at handoff. Other users' GPU processes
were deliberately left untouched.

## 13. Pilot, formal selection, and final results

### 13.1 N=4/T=2 pilot

The pilot used 100 development and 50 calibration pairs.

| Method | Development | Calibration |
|---|---:|---:|
| MA-RAG trap | 58% | 42% |
| MA-RAG pair prompt | 77% | 70% |
| Profile-only | 78% | 74% |
| MA learned adapter | 83% | 78% |
| Adapter without MA | 78% | 78% |
| MedRGAG-style base | 51% | 40% |
| Med learned adapter | 81% | 80% |

Wrong-unanimous stops were 32/100 on development and 21/50 on calibration.
The pilot proved that the interface worked and false consensus existed. It did
not establish synergy: the calibration adapter tied the no-MA ablation.

Pure-trigger thresholds 0, 0.5, and 1.0 produced no pilot repairs or harms.
Threshold 1.0 was frozen because it made the fewest unnecessary extra rounds at
the same accuracy. The nine history-ranking beta pairs selected beta-Profile 0
and beta-CPG 1 on development; calibration moved from 42% base to 46%.

Do not reuse the earliest native pilot directories blindly. One old “trigger”
run included delta-query behavior and was reclassified as
`cf_trigger_plus_delta_query`; an early 100-item full-native directory mixed two
query semantics across its first 82 and last 18 items and is marked
`legacy_mixed`. It was excluded from selection. The frozen pilot record is
`$CF_PACK/results_cfmoe/cache/marag_cf/native_selection.pilot.json`; the
consistent formal-native merged rounds and predictions in the same cache are
the usable native artifacts.

### 13.2 Formal development/calibration, N=8/T=4

Official MA-RAG results before opening the later test:

| Member/method | Development 400 | Calibration 150 |
|---|---:|---:|
| control | 54.75% | 53.33% |
| trap | 53.75% | 48.67% |
| pair prompt | 73.75% | 67.33% |
| Profile-only | 78.50% | 81.33% |
| MA learned adapter | 79.50% | 81.33% |
| adapter without MA | 78.50% | 81.33% |
| MedRGAG-style base | 48.00% | 44.00% |
| Med learned adapter | 78.75% | 81.33% |

The formal native diagnostics were supplementary:

| Native variant | Development | Calibration | Interpretation |
|---|---:|---:|---|
| pure trigger | 53.75% | 48.67% | exactly base; no false-consensus repairs |
| delta query | 57.50% | 50.00% | +3.75 and +1.33 points |
| history ranking | 55.75% | 48.00% | +2.0 then -0.67; unstable |
| full native | 54.00% | 50.00% | +0.25 and +1.33; small |

Fresh native variants were deliberately not run after the user narrowed the
scope to the core portable adapter.

### 13.3 Frozen 500-pair result

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| MA-RAG trap | 39.2% | 17.6% | 66.76% | — | — | 8 |
| MA-RAG pair prompt | 50.2% | 30.2% | 49.00% | 86 | 31 | 3 |
| Profile-only | 79.4% | 42.8% | 12.19% | 226 | 25 | 0 |
| MA-RAG + learned adapter | 80.0% | 52.6% | 13.18% | 210 | 6 | 1 |
| Adapter without MA-RAG | 81.8% | 55.0% | 8.31% | 229 | 16 | 1 |
| MedRGAG-style base | 40.8% | 17.6% | 60.54% | — | — | 0 |
| MedRGAG + learned adapter | 82.4% | 47.0% | 10.88% | 220 | 12 | 0 |
| Adapter without MedRGAG | 81.8% | 46.8% | 10.88% | 217 | 12 | 0 |

Required paired-bootstrap contrasts:

- MA adapter minus MA base: +40.8 points, 95% CI +36.6 to +45.4;
- Med adapter minus Med base: +41.6, CI +37.0 to +46.2;
- MA adapter minus pair prompt: +29.8, CI +25.2 to +34.6;
- MA adapter minus Profile: +0.6, CI -2.4 to +3.8;
- MA adapter minus adapter-without-MA: -1.8, CI -4.2 to +0.4.

Shuffle controls reduced MA adapter accuracy to 50.0% for shuffled delta,
42.4% for shuffled profile, and 73.0% for shuffled CPG. The corresponding
real-minus-shuffle differences were +30.0, +37.6, and +7.0 points, all with
confidence intervals above zero.

MA-RAG stopped with a unanimous final pool on 459/500 items and a wrong
unanimous pool on 273/500. The post-hoc adapter corrected 190/273. This supports
the existence of a false-consensus blind spot, but not the native trigger: the
trigger itself did not repair it in development/calibration.

Fresh MA trap had eight invalid outputs: seven exact vote ties and one runtime
failure. The adapter numerically resolved five tied distributions correctly
but left the runtime failure invalid. The improvement remains large when all
ties are removed. CPG had finite four-way scores on 484/500 fresh pairs and was
explicitly not applicable on 16; no score was fabricated for those rows.

### 13.4 Static compatibility

- The prior RiskRoute path returned exactly the stored MedRGAG prediction on
  400 ReMedQA static rows: 71.0% accuracy, ReAcc 53.0%, ReCon 60.0%.
- The MA-RAG static check is a deterministic bypass of the stored 100-item
  MedQA base prediction, with 100/100 prediction equality and 72.0% accuracy.

These checks establish applicability isolation, not learned safety.

### 13.5 Claim boundary

Supported:

> The same pair-aware counterfactual sidecar substantially improves two
> different medical-RAG base interfaces under one controlled four-option
> MedEinst protocol.

Not supported:

- genuine MA-RAG synergy, because removing MA-RAG is numerically better;
- broad cross-dataset transfer;
- official open-diagnosis MedEinst or original MA-RAG benchmark SOTA;
- an exact paper configuration for the local all-Llama MedRGAG proxy;
- clinical deployment or safety;
- a clinical world model.

## 14. Runtime, failures, recovery, and cost

The server inventory observed on 2026-09-05 was:

```text
4 x NVIDIA H20, 97,871 MiB each
NVIDIA driver 570.133.20
Intel Xeon Platinum 8469C, 48 physical cores / 96 threads
491 GiB RAM, no swap
Linux 5.15.0-144-generic
vLLM 0.8.5, PyTorch 2.6.0
```

The visible end-to-end window ran from 2026-09-02 16:44:31 to the final result
commit on 2026-09-03 19:24:48, about 26 h 40 m. Reboot downtime was not logged
separately.

| Phase | Elapsed wall time | Work |
|---|---:|---|
| environment, MedQA check, smoke, pilot, grids | about 5 h visible | 450 official pilot item-runs plus native/grid work |
| formal base dev/cal | 6 h 37 m | 1,650 MA-RAG item-runs |
| parse/fit/freeze | minutes | entropy temperature, linear weights, L2 |
| formal native dev/cal | 8 h 12 m | four variants x 550 pairs = 2,200 method/item runs |
| fresh Qwen control/trap/pair | 5 h 32 m | 1,500 MA-RAG item-runs |
| fresh Llama sidecar | 4 h 38 m 52 s | concurrent with fresh Qwen, so not added again to elapsed wall time |
| evaluation/report/tests/push | about 38 m | metrics, bootstrap, documentation, verification |

Formal plus fresh unchanged MA-RAG alone generated:

```text
3,150 item-runs
45,872 candidate answers
10,332 retrieval queries
19,710 retained/retrieved documents
20,531,300 generated tokens
45.99 summed per-item wall hours, compressed by parallelism to about 12.1 h
```

One MA-RAG item is therefore not one model call: it starts with eight solver
candidates and can add query generation, retrieval/reranking, and another eight
candidates on every additional round.

The 500-pair sidecar took 4 h 38 m 52 s and recorded 3,312,304 generation-stage
completion tokens; exact option-likelihood passes are additional and were not
counted by that field. Approximate stages were 1 h 43 m for retrieval and the
MedRGAG baseline path, 47 m for option likelihood, 7 m for matching/document
scores, 2 h 1 m for raw CPG/expert scores, and 22 s for assembly.

The largest avoidable delay was running the 8 h 12 m native block before the
fresh portable result. Future order should be:

```text
smoke/pilot -> portable dev/cal fit -> portable fresh core -> optional native
```

### 14.1 Restart and failure history worth preserving

- A server reboot interrupted calibration pair-prompt and one native-full
  question. Partial directories were moved under
  `/home/data3/txy/.cache/marag_interrupted/`; completed metadata-backed items
  were reused rather than rerun.
- Baseline reuse now requires source metadata and the expected candidate pool.
  A bug that called `.exists()` on a missing later round was fixed so validation
  occurs only when that round exists.
- The Llama sidecar initially failed at model startup because the wrong
  Transformers version was imported. It resumed the existing retrieval cache
  with the pinned 4.51.3 compatibility path.
- Fresh trap question 34 entered an upstream unbounded retry because a thinking
  response lacked `</think>`. Only that child was stopped; its partial directory
  was archived and an explicit runtime-invalid metadata record was written.
  The question was never replaced with a fallback prediction.
- Upstream aggregate accuracy could not consume an invalid sentinel with no
  round file; the project parser can. Use the project parser for canonical
  metrics.
- Wrapper shells originally queued direct-Qwen runs after pair prompts. When the
  user selected core-only scope, those queues were removed; pair-prompt shards
  were resumed without starting direct inference.

These failures added some overhead but were not the main cause of the one-day
runtime. The experimental matrix and millions of generated tokens were.

## 15. Canonical artifacts and local-only caches

The historical adapter output directory `$CF_ADAPTER` contains:

```text
dev.jsonl                         400 pairs
calibration.jsonl                 150 pairs
fresh_test.jsonl                  500 pairs
marag_dataset_map.jsonl         1,050 pair mappings
marag_rounds.jsonl              3,150 member rows
marag_option_scores.jsonl       3,150 score rows
cf_expert_scores.jsonl          1,050 expert rows
fusion_config.json              frozen fit/configuration
predictions.jsonl                 500 fresh prediction rows
metrics.json / metrics.csv      main metrics
bootstrap.json                  paired comparisons
false_consensus.csv             consensus analysis
efficiency.csv                  completed-row cost analysis
native_dev_cal_metrics.json     non-confirmatory native diagnostics
static_compatibility.json       bypass checks
summary.md                      narrative result
commands.sh                     exact execution record
```

`marag_option_scores.jsonl` has 3,147 scorable rows: 3,121 official-valid plus
26 complete vote ties. Three rows are non-scorable because of parse/entropy or
runtime failures and retain null vectors plus their raw error.

Expensive local assets were not uploaded:

| Asset | Approximate size |
|---|---:|
| `$CF_ADAPTER/cache/` | 92 MiB |
| `$CF_PACK/results_cfmoe/cache/` | 865 MiB |
| external MA-RAG base raw runs | 1.7 GiB |
| external MA-RAG native raw runs | 1.1 GiB |
| Qwen3-8B weights | about 16 GiB |
| Llama-3.1-8B weights | about 15 GiB |

The raw caches are useful for resuming the exact same input/configuration and
for offline analysis. They are not the source of truth for published metrics;
the compact committed files above are.

At result handoff, the focused MA-RAG suite passed 13/13, the full repository
suite passed 155/155, six integration scripts compiled, `commands.sh` passed
`bash -n`, JSON/score-vector contracts passed, and `git diff --check` passed.
Those counts describe commit `53aaff6`; rerun only checks relevant to a later
code change.

## 16. Historical adapter open questions (2026-09-05)

This section is the older adapter record. Current results and limits are in
section 1. The new baseline report proposes one possible follow-up: whether
original KADS empty selection is associated with M2−M1 errors. This follow-up
has not been implemented or evaluated.

The following requested experiments were intentionally left undone after the
user chose core-only scope:

- fresh native MA-RAG trigger/query/ranking variants;
- direct-Qwen N=1/T=1 on fresh;
- three-seed robustness on a 200-pair subset;
- MA-RAG extrinsic evaluator;
- a same-extra-Llama, similar-token, non-counterfactual ensemble control.

The most important scientific gaps are:

1. **Extra-model attribution.** Pair prompt shows that merely seeing both cases
   is insufficient, and shuffled delta/profile/CPG controls support the sidecar
   signals, but no equal-budget non-CF Llama ensemble has been tested.
2. **Cross-dataset scope.** Positive evidence is still one constructed
   MedEinst MCQ protocol. The older multi-dataset and MedPIC results were
   negative or too small.
3. **Task taxonomy.** There is no frozen, clinically reviewed sample-level
   labeling of negation, temporal change, numeric change, risk-factor edits,
   irrelevant attributes, and evidence corruption.
4. **Retrieval versus evidence use.** There is no clinically verified
   sufficient-evidence oracle or document-level factuality/applicability audit.
5. **Configuration fidelity.** MA-RAG used T=4 and MedCorp3, not the full default
   T=8/full corpus; MedRGAG is an all-Llama proxy rather than a confirmed exact
   mixed-model paper configuration.
6. **Data lineage.** Any future fresh set must exclude every earlier dev,
   calibration, test, and derived variant by underlying source case, including
   DeltaRev and older calibration tails.
7. **Budget.** No numeric wall-time, GPU-hour, or money cap has been provided.
   Ask for one before launching another multi-hour matrix.

The historical recommendation was to verify sources, define sample-level
categories and regroup saved predictions before considering another model run.
The current five-label collection, source audit, classification corrections
and offline regrouping were completed and published on 2026-09-08 as described
in section 1. The earlier small taxonomy is superseded by that frozen cohort;
remaining data-access and expert-validation gaps are listed there. This update
does not start a new model experiment or choose a repair mechanism.

Do not automatically multiply every dataset by every base and native variant.
Classifying saved predictions is offline; changing only a threshold, weight, or
grouping is offline. New inference is required only when prompts, visible
fields, retrieval, documents, model behavior, or the dataset actually change.

## 17. Takeover checklist for another agent

Current CF state checked on 2026-09-08: remote `main` contains the published
medical CF classification archive at `cfe8246`. It was committed and pushed
from the isolated worktree
`/home/data3/txy/Documents/Codex/2026-09-08/medical_cf_publish`, branch
`publish/medical-cf-five-labels-20260908`. The original `$CF_REPO` local `main`
remains at `d922324`, with its unrelated documentation migration changes
preserved. These are different checkouts of the same repository. Full
M0/M1/M2 model results remain complete in `$CF_FULL`; the later release only
adds collection, classification, audit and offline analysis results.

Historical workspace snapshot from 2026-09-06:

- `cf_mrg` local and remote `main` were both at `1e01b3a`, with a pre-existing
  documentation migration in progress: the old pack `AGENTS.md` was deleted,
  `ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md` was untracked, and the
  two handoff documents had matching link updates. These changes were not made
  or staged by this guide update; preserve and inspect them.
- MA-RAG still had the two expected modified runtime files
  (`ma_rag_entropy.py`, `microservice/RetrievalSystem.py`) and the local
  untracked `corpus` link.
- MedRGAG still had the local reproduction scripts, reports, tests, and runtime
  logs as untracked additions. They are the implementation described in
  section 4, not disposable clutter.
- This guide lives at `/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md`, outside the
  three Git repositories. Updating it does not stage or commit project files.

That status is a dated snapshot, not a reason to assume the trees remain
unchanged. Always inspect them again.

1. Read `/home/data3/txy/AGENTS.md`, then this file.
2. Run `git status --short` in `$CF_REPO`, `/home/data3/txy/MedRGAG`, and
   `$MARAG` before editing. Preserve all unrelated user/agent changes.
3. For expanded classification, read `$CF_CLASSIFIED_FULL/DELIVERY.md`; for
   completed v3 benchmark and M0/M1 results, read
   `$CF_BENCH_V3/README.md`, `manifest.json`, `units.jsonl`, and `results/`;
   follow the read-only loading example in section 1. The medical CF collection
   README, correction/R5 reports and publication receipt describe the source
   annotation archive. `$CF_FULL` describes a separate full-release comparison;
   the 2026-09-05 handoff is historical.
4. Treat archived world-model contracts as history. Do not resume their stages
   or make a world-model claim.
5. Prefer the selected benchmark's existing predictions and score files for analysis.
   The current v3 package is local and untracked. Do not start
   Qwen, Llama, or the retriever to answer a result/status question.
6. If an inference run is explicitly requested, state the total planned
   item-runs, candidate budget, estimated wall time, GPU allocation, and which
   supplemental blocks are opt-in before starting.
7. `$CF_FULL/commands.sh` records prepare/readers/analyze/audit for the full
   comparison. Read its existing artifacts for status questions. Historical
   MA-RAG commands under `$CF_ADAPTER` describe a separate experiment.
8. Keep official MA-RAG baseline behavior and outputs separate from native CF
   variants. Never use gold in a prompt/query/ranking feature, resolve a tie
   with gold, or replace an invalid output with a baseline prediction.
9. Preserve the chosen run's frozen output/parser policy. The full comparison
   used zero format repairs; malformed outputs count wrong and unmapped
   diagnoses are reported separately. Never repair with gold.
10. Before committing, run only checks that could detect a failure introduced
    by the change. Documentation-only changes need link/path checks and diff
    checks, not a multi-hour model run.

Useful read-only commands:

```bash
CF_REPO=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg
CF_PACK="$CF_REPO/cf_medrgag_validation_pack"
CF_FULL="$CF_PACK/results_cf_full_comparison"

cd "$CF_REPO"
git status --short
git log --oneline -10

wc -l "$CF_FULL/predictions.jsonl"
jq '{status, required_methods, planned_unique_inputs, completed_unique_method_predictions, completion_rate}' "$CF_FULL/metrics.json"
cat "$CF_FULL/validation.json"

/home/data3/txy/MedRGAG/.venv/bin/python -m unittest discover \
  -s "$CF_PACK/tests" -v
```

The last test command is appropriate after relevant code changes. It is not a
prerequisite for reading existing results.

## Active M3 v5 continuation (2026-09-11 23:38 Asia/Shanghai)

Run directory:
`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3`.
This continues M3 on the same 13,905 v5 inputs used by completed M0/M2/M4/M5.
3,690 exact-input M3 v3 results are reused; 10,215 are new. Native-format and
longest-input smoke checks passed. Eight disjoint workers run on GPUs 1/2,
with Qwen endpoints 8011/8012 and MedCorp3 retrieval port 8993. tmux socket:
`v5-m3`, sessions `services` and `evaluation`. Do not launch a duplicate run.
`code/status.py` records progress and GPU snapshots in `supervision.jsonl`.
`code/run_all.sh` automatically audits full coverage, releases this run's
services, and scores via `code/finish.py` once all shards finish successfully.
Check current files/processes rather than treating this timestamp as live status.

User requests five-minute monitoring and checking whether GPU3 becomes free.
GPU0 and GPU3 contain other users' processes; 0% utilization does not make them
free. Do not stop those processes. Current eight M3 workers retain upstream
entropy processing; the validated vectorized equivalent in source applies only
to subsequent launches/resumes, without interrupting active workers.

### M3 GPU0 parallel update (2026-09-12 12:53 Asia/Shanghai)

User authorized protected GPU0 borrowing after dpc's active job exited. M3 now
uses GPU0/1/2. See the active `results_v5_m3/README.md` GPU0 section: original
shards 0/3/4 moved to endpoint 8010 with 0.60 GPU memory; other five workers
continue. The `v5-m3` tmux `gpu0-parallel` session owns finalization and automatic
fallback to GPU1/2 if the existing 2-second GPU0 guard yields. Do not treat the
three intentional original client exit codes as failed benchmark items, or
restart overlapping shards. Never signal dpc's paused PIDs 1202819/1202820.

M3 update 2026-09-12 12:59: user explicitly authorized GPU0 model allocation of
approximately 75 GiB and lowered only its free-memory exit threshold to 10 GiB.
Other GPU0 yield triggers unchanged; allocation fraction now 0.875 for this
installed vLLM's profiling behavior. Restarted only GPU0 service/three clients.
Report all GPU0–3 usage and M3 cumulative/new/remaining counts every five minutes.

M3 update 2026-09-12 15:29: user explicitly authorized another 6 GiB for GPU0,
lowering its free-memory exit threshold to **4 GiB**. Memory fraction now
0.9378 (about 81 GiB model allocation). Same protected GPU0-only restart,
same three shards and stage caches; GPU1/2 and dpc processes left untouched.

M3 update 2026-09-12 17:59: GPU3 became fully free and joined under the user's
standing parallel-all-available-GPUs instruction. Current shards: GPU0=0/3/4,
GPU1=6, GPU2=7, GPU3=1/2/5 (port 8013, memory .75). See `gpu3_handoff.json`,
tmux `v5-m3` session `gpu3-parallel`. GPU0 coordinator retains finalization;
finish.py includes our GPU3 service cleanup. Other workspace's iMedRAG dev
process on GPU1/2 is unrelated and must remain untouched.

M3 update 2026-09-12 19:18: GPU0 automatic guard yielded after dpc PID 1889151
appeared. Our GPU0 model released; original shards 0/4 now on GPU1, shard3 on
GPU2. Current M3 placement GPU1=0/4/6, GPU2=3/7, GPU3=1/2/5. GPU0 coordinator
is still alive in fallback mode, preserving finalization. No dpc signals sent.

M3 update 2026-09-12 20:55: completed shards1/3/7; shard6 handed to existing
GPU2 service after its queue finished. Active GPU1=0/4, GPU2=6, GPU3=2/5.
Tmux `shard6-gpu2`; GPU0 fallback coordinator still finalizes all results.

### M3 v5 completed (2026-09-12 23:48 Asia/Shanghai)

`results_v5_m3/RESULTS.md` is the final M3 v5 summary. Full 13,905 predictions
(3,690 reused + 10,215 new), 15,616 mapped scored records, 6,104 units; zero
missing or duplicate predictions. Unit-mean native accuracy R1 26.73%, R2 34.18%,
R3 8.59%, R4 38.46%, R5 73.37%, ALL 51.61%. Categories overlap.
Inference finished 23:43:45; scoring 23:43:58. All our model/retriever GPU
processes released, including retriever PID1627382 which required cleanup after
SIGTERM. GPU1/2/3 each show 4 MiB residual usage. GPU0 retains untouched dpc
PIDs1202819/1202820/1889151. No M3 tasks remain active; do not restart queues.

### v5 实施与复现总记录（2026-09-13）

[五方法评测实施、调整与复现记录](<../execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)：供论文和后续交接使用，包含配置差异、优化证据、GPU 调度、五方法结果总表、文件索引与复现步骤。仅补充文档，未重启已完成任务。

### v5 M6/M7 正式输入小批量试跑与上游兼容性修复（2026-09-13）

用户新授权先试跑原始M6/M7，使用GPU1/2/3。新包：[results_v5_m6_m7/README.md](<../completion/results_v5_m6_m7/README.md>)。每方法12条（11来源各一条中位长度输入＋全库最长输入），全量27,810方法输入尚未启动。保留前次源码与输出，使用独立副本；没有CF/WM/adapter附加模块。

M7原12条1有效/11无效；补回锁定上游的无动作关键词输出→Final Answer提议处理后9有效/3无效/0运行失败，原sigma1.2与步数条件不变。复用60次LLM请求，新增10次；全部轨迹审计和原生诊断评分已完成。M7已释放GPU3。M6原第一个6条分片已完成，862秒、25.06输入/小时；第二分片长输入仍运行。M6独立修复取消上游没有的查询逐字匹配门槛，并允许解析失败轮次跳过后返回合法最终答案，14项方法测试通过；修复分片自动接续，只复用依赖未变化请求。M7修复亦14项方法测试通过。后续进展以制品为准，勿把本段时间点当作实时状态。

进度：在新包执行 `python3 status.py`。tmux socket `v5-m6-m7`；原始小批量、M6修复接续及自动汇总已安排。完成后生成 `RESULTS.md`、`fixed_pilot_summary.json`、`diagnostics/M6/`、`diagnostics/M7/`；未出现结果文件表示汇总尚未完成，先查日志和进程，不重复启动。方法修复与前后证据同时追加至原 `PAPER_REPRODUCTION_RECORD.md`。

M6/M7小批量后续完成：新包 `RESULTS.md` 和 `fixed_pilot_summary.json` 已生成。修复后M6 11/12有效，M7 9/12有效，均0运行失败；M6新增40次LLM请求、复用222次，M7新增10次、复用60次。全部诊断评分及轨迹审计完成，试跑进程已退出；没有启动全量。M0–M5既有输出有效率核对见新包 `VALIDITY_COMPARISON.md`，采用独立输入去重口径，M1仅有v3结果。

### v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

用户明确授权使用三张卡运行全量。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal/README.md](<../completion/results_v5_m6_m7/formal/README.md>)。每方法13,905独立输入，其中12条修复试跑结果原样复用、13,893条新运行，覆盖6,104单元和13,000入选判断。每方法109个128输入分片（末片不足128）；GPU1/2优先M6，GPU3优先M7，优先方法队列领完后自动领取另一方法。GPU0不动。使用已验证的M6/M7上游兼容性修复，无CF/WM/adapter附加模块，权重、提示、轮数、阈值、检索与阶段预算保持试跑配置。合并方法15项测试及1项调度测试通过。

三个模型已进入真实推理，M7产生首条新有效终态，初始GPU1/2/3利用率约97–98%。tmux socket `v5-m6-m7-full`，会话gpu1/gpu2/gpu3/monitor。在formal目录执行 `python3 status.py`；`logs/supervision.jsonl`每五分钟记录GPU及进度。各分片完成后审计，最后一片触发完整汇总和原生评分，完成标记为formal/complete.json，最终报告为formal/RESULTS.md。健康进程勿重复启动或中断。

耗时估计纠正：先前4–7天偏乐观；按已完成两个M6分片和M7试跑吞吐分配三卡，直接投影约11天。该试跑非代表性且含最长输入，不是完工承诺，后续以全量滚动吞吐更新。

### v5 M6/M7 提高并发后接续（2026-09-13 06:37）

用户要求提高正式测试的显存利用与吞吐。活动运行改为 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_fast/README.md](<../completion/results_v5_m6_m7/formal_fast/README.md>)，tmux socket `v5-m6-m7-fast`，GPU1/2=M6每卡32线程/128000合批token，GPU3=M7每卡16线程/96000合批token。原 `formal/`三队列已停止，记录和缓存保留，勿重启。方法、权重、提示、预算、阈值及评分不变，执行参数单独覆盖以保留原请求缓存键/随机种子。

相同32条正式请求微基准：M6批量4→32 token吞吐83.47→96.69/s；M7批量4→16为37.81→44.65/s，增到32下降至40.18/s，因此选择不同并发。微基准使用128生成token，不直接当作完整方法加速比。方法与队列16项测试通过。接续已复用旧正式请求并无模型重放完整终态，一致性检查通过。SIGTERM后0.33秒内产生的4个M6人工关闭异常已保存原制品、明确记录并重排同输入，未按答案正确性筛选。新进度06:37 M6=44/13905，M7=70/13905，均无真实运行失败，显存约38.55/43.23/36.64 GiB。

在formal_fast执行 `python3 status.py`。监控与自动审计/全量评分继续，新结果最终写入formal_fast/RESULTS.md。每五分钟向用户报告两方法累计、新计算、剩余及GPU0–3显存/利用率。

### v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

当前活动目录 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/README.md](<../completion/results_v5_m6_m7/formal_balanced/README.md>)，tmux socket `v5-m6-m7-balanced`。单纯提高批量在正式混合长度请求上造成大量补齐与长尾等待，实际M6约37–44、M7约10 token/s，不能称全量提速。相同28请求分组微基准40.31→33.16秒、88.91→108.08 token/s；有效输入补齐量减少31%。因此按原生答案类型、生成阶段、token长度2倍区间合批，并把等待池提高至M6每卡64、M7每卡32，token上限保持128000/96000。模型、方法预算和阈值不变；batch_group不进入prompt、缓存键或随机种子。17项测试通过。

接续无模型/检索重放原M6 32条、M7 68条正式终态，输出和状态一致；加上各12条试跑后进度M6=44、M7=80。原成功阶段收据全部保留复用，未完成响应重算。本次先冻结调度器再终止模型，没有产生新的关闭异常。formal与formal_fast为历史目录，勿重启；源结果、先前4条人工关闭异常和递归成本链完整保留。五分钟报告、自动审计和全量评分继续在formal_balanced执行。

### v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

用户明确要求暂停 M6，继续 M7。当前活动包 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced` 未迁移。M6全部109分片标记paused，累计52/13905（40新＋12复用），41有效/11无效/0失败；预测与阶段缓存保留，操作记录m6_pause.json，不自动恢复。GPU1/2原M6已释放并领取M7分片002/003；GPU3原M7分片001未中断。M7三卡均32并发、96000合批token，其余方法/生成/检索设置不变。GPU0未动。tmux仍v5-m6-m7-balanced。

调整独立完成汇总：M7所有分片完成并审计后，自动写results/tcrag/complete.json、原生评分和RESULTS.md，不等待M6；根complete.json仍只用于两方法均完成。暂停队列不被领取和独立评分幂等性等3项针对性测试通过。五分钟进度与GPU0–3报告继续。

### M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）

用户询问更大批次/显存是否有帮助及每五分钟新增偏少的原因。读取formal_balanced三张卡最近20分钟的真实请求：平均实际batch2.68/3.13/2.95，完整题平均约6次LLM调用，decode有效位置约42.6%–59.1%，排队中位数122–216秒，检索中位数0.59–1.30秒。长输出拖住整批：6条输出223/7/2048/107/10/169 tokens用了273.6秒。几乎没有批次碰到96000 token上限，因此仅增显存上限不是当前主要改进。

将execution.json中M7 workers32→64，保留96000合批token、原阶段/答案格式/长度分组、完整2048生成预算、模型和熵语义。只在下一分片启动时生效，当前分片不中断。实际配置由各run/batching.json记录。此时M7=362/13905，0运行失败；M6继续暂停52条。证据formal_balanced/logs/m7_throughput_diagnosis.json，变更记录m7_workers64_change.json。64等待池不是实际batch64，完整正式吞吐改善尚未验证。

### 当前 M4 格式修复独立试跑（2026-09-13 09:17）

[试验记录](<../execution/results_v5_m0_m2_m4_m5/m4_format_pilot/README.md>)：100条同题、固定历史检索证据，原格式有效65/100；加强提示92/100；再加xgrammar JSON Schema为98/100（1截断、1含糊诊断），原生有效53→76→84。新增200条试验预测独立保存，原正式输出不变。GPU0试跑模型已释放，M6/M7未操作。尚未启动全量重测；同一试验样本已用于方案选择，不能当独立确认集。

### M6 formatter修复试验（2026-09-13 09:44完成）

[实施、验证及候选补丁](<../execution/m6_formatter_pilot/README.md>)。固定40条正式完成输出，两种仅重跑formatter的生成版均39/40协议有效，但出现实质改选，未采用。确定性兼容解析40/40有效，追加12条不重叠原试跑12/12有效；合计协议41/52→52/52，原生35/52→43/52。答案值在仅去除显式诊断包装后保持，既有errors不改写，无LLM补答或新增同义词。推荐转换代码和仅针对M6的集成补丁已准备，未写入活动方法代码或正式预测；M6保持既有暂停，未操作GPU1–3的M7。试验新增80次formatter请求，GPU0已释放自身模型。样本非全库代表性，也不声称100%普遍保证。

### M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）

formal_balanced的tcrag_004完成128输入并审计通过，64路等待池耗时97.87分钟，15.01有效token/s，decode有效位置36.5%；前三个完整32路分片001/002/003分别79.33/90.97/68.39分钟，18.37–21.08 token/s，45.2%–52.0%有效位置。分片是不同随机输入，输入token量也不同，因此不是成对因果测试；但尚无完整方法提速证据，扩大等待池未消除长输出拖住整批。

据此将后续execution.json的M7 workers恢复32，96000 token上限及全部方法参数不变。当前005/006/007保留64运行至完成，避免丢失未返回生成。M6保持暂停。制品：formal_balanced/logs/m7_completed_chunk_throughput.json、m7_workers32_restore.json。10:33累计M7 780/13905，0运行失败。

### 64路观察完成，三卡恢复32路（2026-09-13 11:58）

四个64路正式分片004–007均已完成并审计，耗时97.87/102.92/127.36/88.72分钟，中位100.40分钟，合并73.69输入/GPU小时；此前三个32路完整分片001–003耗时79.33/90.97/68.39分钟，中位79.33分钟，合并96.53输入/GPU小时。64路的有效生成吞吐14.90–17.04 token/s，32路18.37–21.08 token/s。输入是不同随机分片，保留非成对观察限制，不宣称严格因果比；四片均未支持增加并发的实际收益。已完成全部64路分片，GPU1/2/3当前分片009/008/010均按32路、96000合批token继续，未中断任何分片。M7累计1148/13905、0运行失败；M6仍暂停52条。

完整制品更新于formal_balanced/logs/m7_completed_chunk_throughput.json，包含逐片请求数、生成/输入tokens、实际批量、有效decode比例及耗时，供后续论文与效率分析引用。

### M4/M6修复实施文档汇总（2026-09-13）

[统一实施与复现记录](<../execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)已补齐阅读入口及第13节：逐文件修改、280条新增试验输出与52条离线转换的区别、指标分母、无需模型的复核命令、论文措辞和未部署范围。详细证据仍在各试验README及JSON中；本次只整理文档，没有修改预测或运行配置。

### 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

用户明确要求保存M7并让GPU1/2/3全力运行刚更新的M4，额外监督有效率。M7已13:45暂停，1646/13905（1634新＋12复用），1026有效/620无效/0失败、11完整分片；已核对单题terminal数量与独立保存点一致。保存点：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/；原阶段缓存保留，m7_pause.json记录暂停。M6仍52条暂停，不自动恢复两方法。

新活动包：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md。全新生成13905条，复用原M4完整历史检索消息，加入已试验的明确输出契约与逐题JSON Schema/xgrammar。代码和修改后的全量输入独立保存，旧M4不覆盖。Llama3.1-8B、BF16、温度0.7、top_p1、seed42、2048输出及131072上下文不变。每卡vLLM常驻实例、.90显存、128并行序列、16384 prefill token、prefix cache/chunked prefill，109个锁保护动态分片。tmux v5-m4-structured；GPU0未动。

队列与有效率监控2项针对性检查通过；监控复现已有100题98格式有效/84原生有效/99Schema有效/1截断。监控分别报告格式/原生/Schema有效率、截断和题型原因，并单列100条方案选择输入之外的有效率；全部无效保留分母。原v5的3个共享输入存在不同gold映射，最终评分保留全部映射；去重有效率与gold无关。全量完成后自动合并并调用原生分析器，生成scores/、validity.json、complete.json、RESULTS.md。五分钟报告继续针对新M4。

### v5五方法分类对比与优化排查（2026-09-13）

[图表与分析](<../execution/v5_category_priority/README.md>)。M0/M2/M3/M4/M5原正式结果的类别均值从低到高R3 18.14、R2 19.75、R1 27.64、R4 41.54、R5 61.60；排除M4排序不变。错误分解发现R3/R1诊断未映射占比较高，R2主要为有效但错误。R3全部属于R1，R2仅79单元且75来自MedPIC。提供PNG/PDF/SVG、CSV、脚本及验证收据，仅离线分析，未改变任何运行或预测。

### 新M4结构约束修复全量完成（2026-09-13 15:04）

[最终结果](<../completion/results_v5_m4_structured/RESULTS.md>)：13,905唯一输入全部新生成，109/109分片完成，15,616原生评分映射、6,104单元、13,000入选判断完整，缺失/重复/运行失败均为0。GPU1/2/3生成墙钟含加载71.86分钟，完成后自动释放；GPU0未动。

同一13,905输入，格式有效率61.41%→99.09%，原生有效率43.92%→79.42%；严格Schema有效99.46%，原生监控与完整评分器去重一致。单元平均准确率原M4→修复M4：R1 21.53→27.84、R2 6.33→29.11、R3 14.32→30.42、R4 23.08→53.85、R5 39.63→65.28、ALL 29.76→48.20（%）。所有无效保留分母。原生无效2,861：未映射诊断2,735、诊断歧义50、原生解析malformed_json 76；严格JSON无效75，长度截断73，口径分别记录。诊断原生有效率仍仅21.32%。

方案选择100输入之外的13,805输入格式/原生有效率99.11%/79.39%；全库并非独立泛化确认。明确输出契约＋JSON Schema约束改变生成协议，不声称token等价；M5未同步修改，因此新M4/M5不再是仅骨干不同的对照。旧M4原结果独立保留。比较、完整评分及有效率见结果包，五分钟GPU与进度记录见logs/supervision.jsonl。M7保存点仍1,646条（1,634新＋12复用），M6仍52条，均保持暂停。

### 最新v5五方法文档与图表同步（2026-09-13）

[统一benchmark文档](<../completion/v5_benchmark_latest/README.md>)已合并M0/M2/M3/新M4/M5全量结果。只将M4切换为13,905条结构约束修复版，其他方法预测/评分不变。补齐格式/原生有效率、最新分类主图及错误分解PNG/PDF/SVG、完整精度CSV和复现脚本。五方法输入集合一致（各13,905输入、15,616映射），25个方法×类别得分与分解一致，各分解行合计100。ALL为48.10/48.81/51.61/48.20/47.35%；五方法分类均值从低到高R3 21.36、R2 24.30、R1 28.90、R4 47.69、R5 66.73。

旧五方法报告及旧M4图表保留为历史版本并添加新入口；工作区指南、AGENTS、方法结果和实施记录同步。新M4/M5输出协议不同，不能沿用仅骨干不同的描述；旧M4配对统计不适用于新M4。此次只读评分、离线构图，无新增模型请求。M6/M7保持暂停。
