# 历史：早期R1–R5评测、v2与v3

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。保存R5暂停转R1–R4、早期rubric、automatic-only、v2离线重算与v3 M0–M3结果。v3为3,105单元互斥展示类别；旧rubric不作为当前原生评分默认协议。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [Current R1–R5 benchmark v3: exclusive categories (2026-09-09)](#record-0014)
- [Preceding R1–R5 benchmark v2 (exported 2026-09-09)](#record-0015)
- [Preceding v2 R4/R5 evaluation and combined R1–R5 results (2026-09-09)](#record-0016)
- [Preceding R1–R4 automatic-only subset (exported 2026-09-09)](#record-0017)
- [Classified R1–R4 M0/M1 result (completed 2026-09-08)](#record-0018)
- [R1_R5_V3_BASELINES_WORK_RECORD.md](#record-0233)
- [1. 查找入口](#record-0234)
- [2. 已完成工作的时间记录](#record-0235)
- [3. M0–M3 的准确身份及实现调整](#record-0236)
- [4. v3 结果和图表处理](#record-0240)
- [9. 可用于论文的表述草稿与边界](#record-0247)
- [数据构建与标注](#record-0248)
- [v5 评测选择](#record-0249)
- [v3 历史基线实验](#record-0250)
- [10. 证据文件和提交索引](#record-0251)
- [11. 本次文档交付及后续维护](#record-0252)
- [README.md](#record-0302)
- [baseline_contract.md](#record-0303)
- [README.md](#record-0304)
- [README.md](#record-0305)
- [baseline_contract.md](#record-0306)
- [report.md](#record-0307)
- [supervision.md](#record-0308)
- [tables.md](#record-0309)
- [findings.md](#record-0310)
- [protocol.md](#record-0311)
- [report.md](#record-0312)
- [supervision.md](#record-0313)
- [README.md](#record-0314)
- [rubric_protocol.md](#record-0412)

<a id="record-0014"></a>

## Current R1–R5 benchmark v3: exclusive categories (2026-09-09)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第540行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Current R1–R5 benchmark v3: exclusive categories (2026-09-09)

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

###### Load the current benchmark in a new conversation

The real instruction filename is `/home/data3/txy/AGENTS.md` (plural); it
points here. For R1–R5 tasks, read the [v3 README](/home/data3/txy/docs/data/construction.md#record-0316)
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

<a id="record-0015"></a>

## Preceding R1–R5 benchmark v2 (exported 2026-09-09)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第650行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Preceding R1–R5 benchmark v2 (exported 2026-09-09)

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

<a id="record-0016"></a>

## Preceding v2 R4/R5 evaluation and combined R1–R5 results (2026-09-09)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第678行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Preceding v2 R4/R5 evaluation and combined R1–R5 results (2026-09-09)

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

<a id="record-0017"></a>

## Preceding R1–R4 automatic-only subset (exported 2026-09-09)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第702行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Preceding R1–R4 automatic-only subset (exported 2026-09-09)

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

<a id="record-0018"></a>

## Classified R1–R4 M0/M1 result (completed 2026-09-08)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第722行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Classified R1–R4 M0/M1 result (completed 2026-09-08)

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

Read [`findings.md`](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0310),
[`source_label_metrics.csv`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/source_label_metrics.csv)
and [`validation.json`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/validation.json).
The original full-scope directory `$CF_PACK/results_r1_r5_m0_m1_20260908/`
retains **30,844 R5-associated method predictions**, including historical reuse
and overlap with R1–R4. Its refreshed metrics are explicitly partial, and its
original 29,270 newly generated cache rows are unchanged. This local run has
not been published to GitHub. Luna max provided read-only supervision.

<a id="record-0233"></a>

## R1_R5_V3_BASELINES_WORK_RECORD.md

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

### R1–R5 v3 基线与分类指南：工作及调整记录

整理日期：2026-09-13，Asia/Shanghai。本地入口：`/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md`。

本文供论文方法、实现细节、数据构建和实验局限性写作，以及其他本地对话接手时引用。重点记录本对话可直接追溯的 v3 M2/M3 测试、方法身份澄清、来源与抽样追溯、流程文档及分类指南调整；早期分类和后续 v4/v5 工作按已有交付文件补记。**具体操作归属和执行细节以对应运行记录、提交及交付文件为准，不能把本次文档整理当作重新完成了全部实验。**

记录采用“触发要求 → 原状态 → 实际调整 → 原因 → 结果与证据”的口径。讨论过但未采用的方案、已执行的修改、历史状态和当前结果分别标明。历史文件中“尚未运行”等措辞按其记录日期理解，09-13 已完成的后续运行见第 8 节。

本记录侧重 v3 基线实施和分类指南修改。完整 v3→v4→v5 构建、后续分类及选择操作已有[独立构建工作记录](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-13_r1_r5_paper_work_record/README.md)；本文第 7–8 节作为版本衔接摘要引用，不取代该记录。

<a id="record-0234"></a>

## 1. 查找入口

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第11行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 1. 查找入口

| 要回答的问题 | 优先读哪里 |
|---|---|
| 怎样按原标准判断 R1–R5？ | [分类指南](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_full_coverage_plan/README.md)；本地 `R1_R5_CLASSIFICATION_GUIDE.md`，含原定义和带 ID 的审核实例 |
| 原母库怎样形成 v3？ | [完整历史流程](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md)，保留 09-08 至 09-10 的决策和数量 |
| 本对话具体做过什么、调整了什么？ | 本文第 2–6 节 |
| 全量扩充 v4 怎样完成、哪些内容排除？ | [v4 交付](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_full_classification/README.md)、[逐来源范围表](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_v4_scope_comparison/README.md)及本文第 7 节 |
| v3→v4→v5 的完整构建动作及调整清单？ | [构建工作与调整总记录](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-13_r1_r5_paper_work_record/README.md) |
| 为什么后来又有 v5 抽样？ | [v5 探索与授权记录](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_v5/EXPLORATION_HISTORY.md)、[抽样协议和结果](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_v5/README.md) |
| 论文怎样准确描述方法与版本？ | 本文第 3、8、9 节；具体参数引用实际运行目录 |
| 后续修改记在哪里？ | 本文第 11 节；M4/M5、M6/M7 的专门实施记录见第 10 节 |

<a id="record-0235"></a>

## 2. 已完成工作的时间记录

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第24行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 2. 已完成工作的时间记录

以下时间均为北京时间。文档提交时间仅表示发布时点，不能当作整项工作的开始或结束时间。

| 时间 / 阶段 | 触发要求与原状态 | 实际完成工作 | 结果与证据 |
|---|---|---|---|
| 09-08，既有基础 | 用户提出医学专用五类功能分类；早期审阅范围后来扩大 | 收集 15 个来源、归档 55,991 个单元，冻结审阅 28,243 个；审计后修正 172 个具体判断 | [分类归档](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-08_medical_cf_five_labels/README.md)、[修正记录](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-08_medical_cf_five_labels/audit_20260908/corrections/README.md)；这是后续工作的数据基础 |
| 09-09，v2/v3 形成 | 已有 R1–R4 自动评分范围；用户当时确认 R5 仅取 CPV，并要求类别互斥 | v2 合并为 3,105 个单元；v3 按调整前固定类别规模，将重合单元分到其已有标签中数量较少的一类 | [历史流程](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md)阶段 9–10；只是成员/展示口径重组，M0/M1 复用已有预测 |
| 09-09 16:54:30–16:58:21 | 用户要求当前 v3 完整测试 M2，全 Llama MedRGAG，不加入项目额外模块 | 完成 4,872 个输入覆盖：复用 4,720 条相同输入和条件的完整流程结果，补跑 152 条；离线评分并生成三方法表图 | `V3_M2/README.md`、`validation.json`、`artifact_audit.json`；新增 1,976 次阶段调用 |
| 09-09 17:32:33–09-10 08:43:00 | 用户要求查找本地 MA-RAG，作为 M3 使用原方法测试 | 接入本地 intrinsic MA-RAG；完成同一 v3 的全部 4,872 个输入、6,030 条评分映射和四方法图表 | `V3_M3/README.md`、`plan.json`、`validation.json`；8 个分片退出正常 |
| 09-10，对话中断后的进度核对 | 用户认为可能中断，要求查看并恢复 | 读取后台运行和完成记录；确认后台推理没有随对话中断停止，恢复会话时已完成 | `V3_M3/run_exit.json`、`analysis_finished_at.txt`；无需重新启动推理 |
| 09-10，图表及职责反馈 | 用户指出一次仅调出图表却耗时约 14 分钟，并质疑非监督工作调用监督代理 | 明确后续结果展示直接读取已有 CSV/图；运行监督与主代理的资料读取、分析及分类裁决分开 | [历史流程](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md)阶段 11；此处约 14 分钟为用户反馈，不是模型推理耗时测量 |
| 09-10，M0/M1 身份追溯 | 用户追问方法来源、M1 是否就是 MedRAG 论文方法或论文消融 | 对照本地实现、先前运行和历史说明，明确 M0 为直接回答、M1 为本项目初始检索对照 | 第 3 节；不将 M1 标为独立 MedRAG 论文方法或某项官方消融的精确复现 |
| 09-10，来源与 2,500 抽样追溯 | 用户要求每类来源、缺失范围及抽样理由可解释 | 形成逐来源说明和 CSV，区分获取缺口、分类不足、评分限制、旧规模限制和真实作者划分；核实 2,500 的决定来源 | 本地 `r1_r5_benchmark_sources_20260910.md`、`r1_r5_source_scope_20260910.csv`；第 5 节 |
| 09-10 12:16，流程归档 | 用户要求全过程、理由及处理写成说明并上传 GitHub | 发布 13 阶段流程、来源数量、v3 演变、M0–M3 方法及结果边界 | [提交 19e8ecb](https://github.com/xiotakut/cf_mrg/commit/19e8ecb)、[历史流程](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-10_r1_r5_process_history/README.md) |
| 09-10 14:51，补分类计划 | 用户要求保留 v3、补足抽样遗漏，并允许有证据的正式排除 | 核算 24,436 个抽样遗漏候选、18,238 个已有 R5 暂缓候选；写出来源、任务资格和覆盖计划 | [提交 b26dc8d](https://github.com/xiotakut/cf_mrg/commit/b26dc8d)；当时交付为计划，没有在该步骤启动分类或实验 |
| 09-10 15:17，计划改为分类指南 | 用户明确文件主要用于其他本地对话，核心应是原规则和示例，删除推荐运行配置 | 找回用户原方案，补齐五类判定条件、正例/反例、多目标和评分边界；核对 13 个实例的当前标签；建立共享入口 | [提交 636994b](https://github.com/xiotakut/cf_mrg/commit/636994b)；本地指南及 `AGENTS.md` / `MEDRGAG_WORKSPACE_GUIDE.md` 路由 |
| 09-10 17:19–22:14，后续交付补记 | 后续分类、方案比较及 v5 选择已有独立记录 | v4 完整交付并正式命名；整来源删除仅做预览；随后按用户确认另建 v5 | 第 7 节；提交 c0375be、83222bd、a1a8e70、ecda328，执行细节见各交付 |
| 09-13，本次记录 | 用户要求所有做过的工作和具体调整方便论文及其他对话引用 | 对照已有文件与提交整理本文，补充新旧差异、证据目录、论文表述和后续记录入口；核实后续 v5 完成状态 | 本文及本次提交；本轮只更新文档与入口 |

<a id="record-0236"></a>

## 3. M0–M3 的准确身份及实现调整

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第44行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 3. M0–M3 的准确身份及实现调整

<a id="record-0240"></a>

## 4. v3 结果和图表处理

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第85行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 4. v3 结果和图表处理

v3 使用互斥展示类别，3,105 个单元的计数可相加。下表为已完成 v3 原生任务结果，不用于替代 v4/v5 的结果。

| 类别 | 单元 | M0 | M1 | M2 | M3 |
|---|---:|---:|---:|---:|---:|
| R1 | 1,601 | 45.22% | 41.29% | 44.41% | 43.85% |
| R2 | 77 | 9.09% | 9.09% | 7.79% | 32.47% |
| R3 | 324 | 18.83% | 28.40% | 23.46% | 14.20% |
| R4 | 13 | 38.46% | 38.46% | 53.85% | 38.46% |
| R5 | 1,090 | 66.51% | 69.82% | 70.28% | 79.82% |
| ALL | 3,105 | 49.02% | 49.15% | 50.43% | 53.08% |

产物为 `V3_M2/category_scores.csv` / `r1_r5_three_methods.{png,pdf,svg}` 与 `V3_M3/category_scores.csv` / `r1_r5_four_methods.{png,pdf,svg}`，另有来源表、逐单元评分、R4 逐题表及 R5 配对表。图表基于保存的评分文件生成。

R5 的变体准确率、答案一致率、两端均正确率分别报告。例如 M3 在 v3 R5 的答案一致率为 90.28%，两端均正确率为 75.69%，二者不是同一指标。R4 仅 13 个 HIV ART 作者预期答案场景，结果是预期答案一致性，不能表述成已临床验证的后果预测准确率。

图表调阅反馈带来的工作方式调整：已有结果展示直接读取对应文件；只有实际发现输入、评分或版本问题时才追加相关核对。Luna max 的授权范围是运行监督，资料追溯、一般分析和分类裁决由主代理负责。此前图表提取时增加了不必要的重复核验，不能将其当成之后展示结果的前置要求。

<a id="record-0247"></a>

## 9. 可用于论文的表述草稿与边界

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第191行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 9. 可用于论文的表述草稿与边界

<a id="record-0248"></a>

## 数据构建与标注

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第193行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 数据构建与标注

> 我们从已取得的 15 个医学反事实相关来源构建了包含 55,991 个归档比较单元的母库。以具体判断为单位，依据新增支持、撤销支持、重新比较、推导后果和保持判断五种功能关系进行标注，保留原题、来源版本、比较轴及判断依据。早期审阅存在按来源规模抽取 2,500 个单元的实施性限制；随后在独立 v4 中补齐该抽样遗漏并重新核定原暂缓内容的资格。经逐目标处置，38,123 个比较单元至少含一个合格目标，共有 77,781 个合格具体判断。需要人工语义评分、缺少必要输入或参考、源构造无效及原实验协议不适用等内容按具体原因单列。

<a id="record-0249"></a>

## v5 评测选择

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第197行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 评测选择

> 我们保留完整 v4，并为后续评测另建 v5。所有合格 R1–R4 目标完整保留；R5 在八个来源内分别对合格比较单元进行不放回随机抽样，每来源 450 个，共 3,600 个。该配额用于提供相近的来源比较预算，并非由统计功效优化得到。候选清单、一次生成并保存的随机种子及选中 ID 均可重放。v5 共含 6,104 个去重比较单元和 13,000 个选中判断；原语义标签和评测选择标签分开存储。

<a id="record-0250"></a>

## v3 历史基线实验

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第201行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v3 历史基线实验

> 在 v3 的 3,105 个互斥比较单元上，我们比较了直接回答、本项目初始检索对照、全 Llama MedRGAG 和本地 MA-RAG。完整覆盖为每方法 4,872 个独立输入及 6,030 条原生评分映射。M2 复用 4,720 条条件一致的历史完整流程结果，并计算 152 个新增输入；M3 对全部输入产生本轮结果。MA-RAG 保留其 intrinsic 迭代、查询与投票逻辑，适配原生题型及完整长证据上下文。该比较的骨干、检索语料和调用预算不完全一致，因此结果描述本地方法配置的整体表现。

正式投稿前，按实际主实验版本选择对应段落，并引用其最终文件。关键限制集中说明如下：

- 分类是真实执行的代理标注及复核，审阅方式有逐项、分组与结构核验之分；`clinical_review=false` 不得写成临床专家一致性验收。
- 来源可追溯、功能标签有依据、原参考有效和原生评分可执行是不同证据。原生答案准确率不等于逐条推理理由已得到语义验证。
- 开放诊断沿用本地归一化精确匹配，不能把其分数解释成已覆盖全部医学同义表达的诊断判分。
- R4 的可评分部分仅有 13 个 HIV ART 作者预期答案场景；类别范围很小，参考未经过独立临床金标准验证。
- 多标签统计、子目标展开、重复参照和同源变体分别计数；比较单元不是独立患者，推理调用次数也不是题目数。
- 配额、规模限制和协议适配如实报告。2,500 与 450 的制定阶段和理由不同；固定种子只支持复现，不自动证明代表性或统计最优。
- 跨骨干、跨检索库及不同预算的结果不能只归因于算法；M1 不能标为官方 MedRAG，M2/M3 不能直接声称复现了对应论文全部表格设置。
- 版本结果保持分离。早期被排除的 AI rubric 评分、旧适配器/WM 结果以及开发集试跑，不混入本次正式范围。

<a id="record-0251"></a>

## 10. 证据文件和提交索引

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第216行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 10. 证据文件和提交索引

本地路径别名仅用于定位文件，不是运行建议：

```text
WORK=/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md
PACK=/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack
COLLECTION=/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection
V3_M2=$PACK/results_r1_r5_v3_m2_20260909
V3_M3=$PACK/results_r1_r5_v3_m3_20260909
V5_FOUR=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5
V5_M3=/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3
```

| 内容 | 本地证据 |
|---|---|
| 母库、原始题目与已审记录 | `COLLECTION/全部比较单元.jsonl`、`分析子集.jsonl`、`分析子集_具体判断.csv` |
| 分类修正 | `COLLECTION/audit_20260908/corrections/修改明细.csv`、`clinical.jsonl`、`amqa.jsonl`、`gold.jsonl` |
| 来源追溯报告 | `WORK/r1_r5_benchmark_sources_20260910.md`、`r1_r5_source_scope_20260910.csv` |
| v3 当前成员、原分类及 M0/M1 | `PACK/benchmark_r1_r5_text_auto_cpv_v3_exclusive_20260909/` 的 `units.jsonl`、`classification_provenance.jsonl`、`results/` |
| v3 M2/M3 配置、结果、阶段与完整性 | `V3_M2` / `V3_M3` 的 `README.md`、`config.json`、`plan.json`、`validation.json`、`artifact_audit.json`、`category_scores.csv`、`supervision.md` |
| v3 M2 复用与补跑 | `V3_M2/stages.jsonl.gz`、`m2_predictions.jsonl`、`code/run_m2.sh`、`code/analyze_m2.py` |
| v3 M3 原始迭代记录 | `V3_M3/cache/items/`、`code/run_full.sh`、`code/analyze_m3.py`、`run_exit.json`、`analysis_finished_at.txt` |
| v4 完整分类及资格 | `WORK/benchmark_r1_r5_v4_20260910/DELIVERY.md`、`exports/all_reviewed_target_annotations.jsonl.gz`、`exports/archive_unit_coverage.csv`、`completion_audit.json` |
| v4 具体资格调整 | 同目录 `legacy_target_qualification_overrides.jsonl`、`existing_partial_target_dispositions.jsonl`、`sources/M17_resource/annotations.jsonl` |
| v5 探索、抽样与成员关系 | `WORK/benchmark_r1_r5_v5_20260910/EXPLORATION_HISTORY.md`、`sampling_protocol.json`、`selected_r5_unit_ids.json`、`v3_v4_v5_membership.csv`、`verification.json` |
| 后续 v5 M0/M2/M4/M5 正式结果 | `V5_FOUR/RESULTS.md`、`README.md`、`validation.json`、`artifact_audit.json`、`category_scores.csv`、`paired_method_comparisons.csv` |
| 后续 v5 M3 正式结果与执行变化 | `V5_M3/RESULTS.md`、`README.md`、`performance_notes.md`、`validation.json`、`artifact_audit.json` |
| M4/M5 专门实施记录 | `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/M4_M5_INSTALLATION_REPORT.md` |
| M6/M7 专门实施记录 | `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md` |
| v3→v4→v5 专门构建记录 | `WORK/paper_work_record_20260913/README.md` |

主要公开版本：

| 提交（日期均为 09-10，另注明者除外） | 实际变更 |
|---|---|
| [cfe8246](https://github.com/xiotakut/cf_mrg/commit/cfe8246)（09-08） | 收集、分类、来源审核、修正及旧预测离线重分组归档 |
| [19e8ecb](https://github.com/xiotakut/cf_mrg/commit/19e8ecb) | 完整流程、来源流失、v3 方法和结果说明 |
| [b26dc8d](https://github.com/xiotakut/cf_mrg/commit/b26dc8d) | 全量补分类计划初版 |
| [636994b](https://github.com/xiotakut/cf_mrg/commit/636994b) | 计划改写为具体分类指南，去除推荐运行配置 |
| [c0375be](https://github.com/xiotakut/cf_mrg/commit/c0375be) | 完成分类交付及入口更新 |
| [83222bd](https://github.com/xiotakut/cf_mrg/commit/83222bd) | 正式命名 v4、类别统计及图 |
| [a1a8e70](https://github.com/xiotakut/cf_mrg/commit/a1a8e70) | v4 与七来源排除预览、数量和采用理由 |
| [ecda328](https://github.com/xiotakut/cf_mrg/commit/ecda328) | 冻结 v5 随机子集、种子、候选/选中 ID 及探索历史 |

完整原题、大型阶段缓存和完整运行制品按原记录保留本地；公开仓库包含对应文档及其已明确发布的统计、清单和图表。本文的证据入口不等于这些大型文件全部已公开。

<a id="record-0252"></a>

## 11. 本次文档交付及后续维护

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第263行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 11. 本次文档交付及后续维护

09-13 本次实际修改：新增本文及共享本地副本；在 GitHub benchmark 索引、`AGENTS.md`、`MEDRGAG_WORKSPACE_GUIDE.md` 和分类指南增加记录入口；为较早的“尚未运行”说明增加有日期的后续结果入口。分类规则、原始数据、预测和运行代码不因本次文档整理而改变。

本文检查的是记录引用：提交是否存在、关键文件是否能定位、版本数量是否与交付/结果摘要一致、本地与公开文档副本是否一致。没有为编写本文重新推理、重新分类、重抽样或重跑全量实验检查。

后续与本线相关的工作继续追加有日期的记录，至少包括：**用户要求或触发问题、修改前后、调整理由、生效版本和文件、实际验证结果、仍未完成内容、提交/产物位置**。实质改变数据范围、标签、输入、评分、方法配置或结果时，保留前版并明确对应关系；仅文档修订则明确写成文档修订。

跨方法工作优先更新其专门实施记录，再在本文追加关联入口。分类指南继续以规则和实例为主，工作历史和实现参数保留在本记录或对应方法文档中。

<a id="record-0302"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908`。

### R1–R5 文本 benchmark：M0 / M1

2026-09-08 按用户指示暂缓全量 R5；已有缓存完整保留。R1–R4 续跑结果见 [独立目录](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0304)。使用已冻结并审阅的分析集，排除多模态/缺图题。方法、输入、评分与适用范围见 [baseline_contract.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0303)。

原全量冻结计划（已暂缓）：24,195 个比较单元，60,282 个独立输入，每种方法 75,806 条原任务评测记录。复用 22,284 条预测，新增 98,280 次调用。M2 不运行。MedCF 的 798 个单元需要知识编辑，单列为不适用；3,250 个单元因多模态或缺图排除。

比较单元与模型调用不是同一计数：20,338 个纳入单元有 R1–R5 标签，3,857 个尚未定类，仅保留原任务结果。原题/变体及原任务子问题展开后，按模型可见输入全局去重，再各运行 M0、M1；重叠 R 标签不增加调用。MedRGB 的 3,636 个单元各展开为六档本地固定文档条件，共 21,816 个独立输入；MedPerturb 的 3,277 个单元展开原题/变体与 MANAGE、VISIT、RESOURCE 后，去重为 14,049 个独立输入。新增调用数为 `60,282 × 2 − 22,284 = 98,280`，并不表示有 98,280 道 benchmark 题。

- [plan.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/plan.json)：冻结范围及来源计数。
- [coverage.jsonl](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/coverage.jsonl)：每个冻结比较单元的执行或排除原因。
- [preparation_validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/preparation_validation.json)：输入隔离、旧预测复用和完整性检查。
- [execution_provenance.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/execution_provenance.json)：模型、进程、GPU与监督记录。
- [baseline_contract.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0303)：逐来源任务处理和指标边界。
- [medqa_recovery.jsonl](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/medqa_recovery.jsonl)：DiversityMedQA 的原选项/答案精确回补。
- [metrics.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/metrics.json)：最近一次离线分析状态；运行中可能仍是 smoke/partial。

运行日志为 run_0.log、run_1.log；实时进度为 cache/worker-0/runtime.json 和 cache/worker-1/runtime.json。全量任务已在批次保存后退出，当前 metrics.json 为截至切换时缓存的 partial 分析；该目录不表示 R5 已全部完成。此前 smoke_complete.json 仅代表短批次完成。

代码在本目录 code/ 留有快照，实际执行脚本位于 `/home/data3/txy/Documents/Codex/2026-09-08/agent-md-medrgag-workspace-guide-md/`。执行记录见 code/commands.sh；tmux socket 为 r1r5，此前 session 为 text-completion，现已退出；R1–R4 续跑也已完成。

最终指标分来源、原任务、原始 split、R1–R5 标签与参考/变体报告。未定类题纳入原任务覆盖，不补猜标签。开放问答与文档纠正的语义评分需要后续按原 rubric 评定，不用自动准确率替代。

文本排除规则已修正：恢复 180 个纯文本单元，原 59,875 个输入内容和 ID 不变。新增 407 个输入已纳入当时 text-completion 会话使用的完整清单；随后按用户要求收缩至 R1–R4。见 text_coverage_revision/receipt.json。

<a id="record-0303"></a>

## baseline_contract.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/baseline_contract.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908/baseline_contract.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_m0_m1_20260908`。

### Frozen R1–R5 text benchmark: M0/M1

2026-09-08. User requests full testing of the newly reviewed R1–R5 benchmark, only M0 and M1, and excludes multimodal inputs. This run uses every applicable text unit in the frozen 28,243-unit reviewed cohort, including unclassified units. No new sampling, annotation changes, M2 inference, training, sidecar or automatic judge is used.

#### Methods and execution

M0: Llama-3.1-8B-Instruct with the independent native question, full options and mandatory task evidence. M1: the identical input plus the existing source-balanced textbook/Wikipedia BM25 32/source, MedCPT cross-encoder top-5. Mandatory task evidence remains visible in both methods. Retrieval sees only the question and full options; no answer, functional label, review rationale or pollution mask is supplied.

Model: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`; BF16; original tokenizer/chat template; vLLM 0.8.5; context 98,304; temperature 0; top_p 1; original per-item/stage seed formula with base seed 20260906. Existing native answer-only tasks retain 64 output tokens and the original prompt/parser. Newly added open answers use 512 tokens. MedRGB answer-plus-error/correction JSON uses 2,048 tokens. Each method makes one generation per unique input; no repairs, retries based on answer quality, repeated seeds or candidates. Invalid outputs remain invalid.

The all-Llama M0/M1 definitions are retained; new source task serialization is documented below. This is not an exact reproduction of the original papers' model/prompt settings.

GPU 0 and 1, two workers, batches of 32. Installed vLLM V1 counts other processes' allocations in its memory-profile peak. Its 0.78 parameter therefore bounds the profiled total card budget, leaving roughly 20 GB headroom; it does not allocate 78% in addition to other users' jobs. An initial 0.42 startup could not allocate KV cache and generated zero predictions. That startup and the superseded preparation are retained under `preflight_initial/`.

`plan.json` freezes all item and coverage counts. Identical visible inputs are inferred once across sources. Compatible old M0/M1 inputs retain their original IDs, prompts, seeds and cached responses; both new and reused predictions retain provenance. No M2 artifacts are copied into this run.

#### Native task handling

- M01/M02/M10/M11/M20: preserve original independent inputs, gold, diagnosis canonicalization, multi-select exact-set, MCQ accuracy or evidence agreement. Reuse exact compatible predictions. The classification unit's reference and variant are separate inputs.
- M12 AMQA: original and the released fixed adversarial question; original options and answer key. No attack generation or historical model answers.
- M14 DiversityMedQA: restore options and gold only through exact original-question matching to pinned BigBio MedQA English 4-option source files. `medqa_recovery.jsonl` records each recovery, independently of frozen annotations. Preserve the author's test/train provenance; the frozen collection includes both and is not a newly held-out test.
- M17 MedPerturb: keep all three original MANAGE/VISIT/RESOURCE questions separately with each released clinical context and gold. Use an explicit yes/no JSON answer, without the paper's extra model-based binary extractor. Functional tags are joined to their corresponding child target; RESOURCE has no inherited VISIT/MANAGE tags.
- M23 BioRAB: independent original instruction (including retrieved demonstrations) and target context for both clean and corrupted records. Retain native positive/negative labels. The row's response/category and other paired row are absent from input. References explicitly marked ineligible stay out of scoring.
- M06 HIV: yes/no agreement with the author's generated expected answer, explicitly not clinical gold validation.
- M05 LabTest: original CF question, no invented patient identity linkage to adjacent questions. Historical model Response/Reasoning and historical ratings are not gold. Save new responses for independent expert scoring.
- M16 EquityMedQA: generate both independent questions. Original ideal-answer-difference ratings do not score these new answers. Save responses for the native human fairness rubric; no invented accuracy.
- M24 MedCF: native efficacy/generality/locality requires actual knowledge editing, absent from M0/M1. Record all 798 as not applicable; no ordinary-QA substitution or contextual editing proxy is included by default.
- M25 and other explicit image-dependent inputs: excluded with the matched missing-visual reference in `coverage.jsonl`. Imaging findings fully described in text are not excluded merely because imaging is mentioned.

#### MedRGB robustness materialization

All selected text question groups and their released CF document slots are retained. Test signal proportions 0/20/40/60/80/100. These six contexts are a **local, frozen materialization of the released document pools**, not author-released masks or an exact replay of the paper. Correct documents and erroneous documents are sampled independently from the same question's released signal/CF pools using seed 20260908 plus the frozen cohort position, and shuffled. No `DOC_n → signal_documents[n]` mapping is invented: the release does not provide that mapping. This preserves the clean/error count without claiming matched individual document replacements. All ten CF slots appear at p_sig=0. Four release rows have only nine signal slots; if such a row is included, its p_sig=100 context retains the available nine, without duplication or fabrication.

The visible supplied document IDs are D0…D9, with no clean/error markers. The main question, options and document text are visible. Original answers, `new_answer`, masks, sub-answer gold and long-answer rubrics remain separate. M1's external top-5 is additional evidence, not part of the supplied-document error mask. `document_map` and `p_sig` are evaluation-only metadata.

Main answer correctness, document error detection and correction content remain separate. Score error IDs against the released corruption mask, excluding missing/empty document slots and retaining invalid outputs. Save correction text without claiming unperformed semantic assessment. MedLFQA long answers retain must_have/nice_to_have rubrics for later human evaluation; MCQ scores do not stand in for long-answer or correction quality.

#### Reporting

Report coverage, source × native task × reference/variant, overlapping R1–R5 tags, and M1−M0 contrasts. Unclassified units remain in native-task totals but never acquire a guessed functional tag. Use paired source-root bootstrap intervals (2,000 draws); preserve derivative MedQA source-family and original split metadata. Do not pool heterogeneous tasks into one accuracy. Parent native-task accuracy does not establish correctness of each annotated subjudgment.

A full inference completion receipt means every planned M0/M1 response exists. It does not mean missing images, inapplicable editing tasks, expert rubrics or explicitly unreliable references have been resolved. Open-ended and document-correction semantic scoring stays explicitly pending.

##### Coverage review receipt

The first image filter incorrectly treated bare “shown below” introducing fully transcribed laboratory tables as an image dependency. The corrected filter restores 180 text units and adds 407 unique inputs. Every previously frozen input and its ID/seed remains identical; added inputs receive fresh IDs. See `text_coverage_revision/receipt.json`. A queued `text-completion` session completes these after the initial workers.

MedRGB complete-document and incomplete-CF-document conditions are separate metric strata. Nominal p_sig is not presented as a verified effective pollution percentage when a source slot is missing. MedRGB all-signal comparisons are saved as local context contrasts separately from native official-pair correctness.

##### Execution-only retrieval optimization

A 16-query check found that 8-thread CPU BM25 returned exactly the same 64 candidates, scores, contents and ordering as serial execution (7.00 s versus 1.40 s). The run resumed at saved M1 batch boundaries with CPU BM25 parallelized. Per-query MedCPT forward batches, precision and ordering remain unchanged. Prior predictions are retained; `checkpointed_restart.json` records the saved counters and only the benchmark-owned terminated process trees. The queued continuation incorporates the restored text inputs.

<a id="record-0304"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908`。

### R1–R4 文本 benchmark：M0 / M1

当前排除全部需人工评审任务后的 benchmark 见 [固定规则自动评分子集](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0305)：2,015 个比较单元，R1/R2/R3/R4 为 1,929/77/327/13。LabTest（含原 AI 初评的 9 个 NA）和 EquityMedQA 整体排除，视觉多模态继续排除。[下载子集](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/r1_r4_automatic_only.zip)。下文保留此前完整文本运行的记录。

按用户最新指示，仅补齐 R1–R4；重叠标签题保留，R5 专属与未定类任务暂缓。原题/变体、输入、证据、金标与 item_id 均未改变。原标签保存在 original_labels，当前统计 labels 仅含 R1–R4。

已全部完成推理，结果见 [findings.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0310)。计划：2,170 个可测试比较单元、3,296 个独立输入，M0/M1 共 6,592 条预测。已复用 6,192 条，本次补齐 400 次调用。M2 为 0。

完整结果见 [findings.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0310)；精确范围见 plan.json、coverage.jsonl、evaluation.jsonl，范围切换及 R5 保留记录见 scope_change.json。baseline_contract.md 来自原全量运行；其中涉及当前清单之外来源的规则不表示继续运行那些题目。

R5 已有输出保留在 ../results_r1_r5_m0_m1_20260908/cache/，原完整输入和评测映射也保留于该目录。当前没有继续生成 R5 专属输入。

按 R1–R4 分类的完整总表与图见 [category_summary/report.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0307)，含自动评分和 AI rubric 汇总，以及原指标分项。全部图表见 [figures/tables.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0309)，含 PNG、PDF、SVG 和 CSV；[下载完整图表包](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/r1_r4_charts_and_tables.zip)。

<a id="record-0305"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only`。

### R1–R4：文本、固定规则自动评分子集

按用户最新要求，整体排除 LabTest（M05，30 单元）和 EquityMedQA（M16，125 题对）。此前 AI 初评标为 NA 的 9 道 LabTest 已包含在这 30 道中，不额外删除。视觉多模态题继续排除。

范围：原 R1–R4 共 2,256 个比较单元 → 排除 86 个图像依赖单元 → 2,170 个文本单元 → 排除 155 个需人工评审单元 → **2,015 个比较单元、8 个来源**。

#### 分类及结果

| 分类 | 原有文本单元 | 排除人工评分 | 保留 | M0 | M1 | 差值（pp） |
|---|---:|---:|---:|---:|---:|---:|
| R1 新增支持 | 2,030 | 101 | 1,929 | 40.75% | 39.09% | -1.66 |
| R2 撤销支持 | 88 | 11 | 77 | 9.09% | 9.09% | +0.00 |
| R3 重新比较 | 389 | 62 | 327 | 18.96% | 28.44% | +9.48 |
| R4 推导后果 | 53 | 40 | 13 | 38.46% | 38.46% | +0.00 |
| 去重合计 | 2,170 | 155 | 2,015 | 39.55% | 37.97% | -1.59 |

M0 为直接回答，M1 为检索增强。分数为非参照比较单元按现有规则判正确的比例，每单元等权；标签允许重叠，合计按 unit_id 去重。原输入、金标、预测、解析和自动判分均保持原样，包括既定规则下的无效输出计错。

#### 来源分布

| 来源 | 去重单元 | R1 | R2 | R3 | R4 |
|---|---:|---:|---:|---:|---:|
| MedEinst | 843 | 843 | 0 | 274 | 0 |
| MedPIC-Bench | 167 | 96 | 75 | 10 | 0 |
| HIV ART causal scenarios | 13 | 0 | 0 | 0 | 13 |
| CPV-MedQA | 1 | 1 | 0 | 0 | 0 |
| Counterfactual Cultural Cues | 67 | 67 | 0 | 0 | 0 |
| FairMedQA/AMQA | 134 | 134 | 0 | 43 | 0 |
| DiversityMedQA | 2 | 0 | 2 | 0 | 0 |
| MedCounterFact | 788 | 788 | 0 | 0 | 0 |

各来源仍使用各自的原任务指标，包括诊断标签匹配、答案集合完全匹配、选项准确率、作者预期答案一致率和证据关系一致率。原题以文字作答但能按固定规则判分的任务仍保留。

R4 仅剩 HIV ART 13 个场景，两方法均为 5/13；范围已收窄到单一来源。原 R4 的 53 个文本单元减去 LabTest 30 和 EquityMedQA 10，剩余 13，与此前 AI 初评的 NA 判定无关。

#### 可复用文件

- [比较单元清单](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/units.csv)：2,015 行，包含 R 标签、来源、输入 ID、评分指标。
- [原题及固定证据](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/items.jsonl)：3,172 个独立输入，包含保留任务所需的参考题。
- [评测映射与金标](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/evaluation.jsonl)：3,850 条，供每个方法使用。
- [已完成的 M0/M1 预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/predictions.jsonl)：6,344 条，保留原方法名 direct_llama／retrieval_only_llama，对应 M0／M1。
- [固定规则评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/scored.jsonl)：7,700 条方法评测记录，包含参考题；分类得分仅统计非参照单元。
- [分类总表](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/category_summary.csv)、[来源分布](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/source_summary.csv)、[排除清单](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/excluded_units.csv)、[覆盖记录](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/coverage.jsonl)、[检查结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/automatic_only/validation.json)。

此目录是原结果的筛选导出，未新增模型调用。原始完整结果及 AI 初评保留在上一级，当前子集不使用 AI 初评分。下载 [完整子集压缩包](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/r1_r4_automatic_only.zip)。

<a id="record-0306"></a>

## baseline_contract.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/baseline_contract.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/baseline_contract.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908`。

正文与[已合入记录](#record-0303)相同，统一在该处维护。

<a id="record-0307"></a>

## report.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/report.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/report.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary`。

### R1–R4 分类总表与图

历史版本：本页为包含 AI 初评分的跨任务汇总。当前排除全部需人工评审任务后的分类总表见 [自动评分子集](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0305)，R4 保留 13 个 HIV ART 场景。

M0 为直接回答，M1 为检索增强。包含本次 R1–R4 全部已完成的非多模态结果，以及已完成的 AI rubric 评分。

项目汇总通过率 = 通过的比较单元数 / 可计分的比较单元数。每个单元等权：自动任务按原定规则答对、LabTest 结论被评为正确、EquityMedQA 题对被评为无偏见分别记 1，否则记 0。它是为分类总览新增的跨任务汇总指标，不是原论文共同定义的准确率；无偏见不等同于医学回答正确。未修改任何模型输出或原始评分。

| 分类 | 纳入单元 | 计分分母 | M0 通过率（通过数） | M1 通过率（通过数） | M1−M0 |
|---|---:|---:|---:|---:|---:|
| R1 新增支持 | 2,030 | 2,030 | 39.80%（808） | 39.31%（798） | -0.49 pp |
| R2 撤销支持 | 88 | 88 | 9.09%（8） | 7.95%（7） | -1.14 pp |
| R3 重新比较 | 389 | 389 | 21.34%（83） | 28.79%（112） | +7.46 pp |
| R4 推导后果 | 53 | 44 | 72.73%（32） | 70.45%（31） | -2.27 pp |
| R1–R4 去重合计 | 2,170 | 2,161 | 39.43%（852） | 38.59%（834） | -0.83 pp |

![R1–R4 分类总览](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.png)

R4 纳入 53 个单元，其中 LabTest 每方法 9 个结论无法判定，按 NA 排除，故计分分母为 44。两方法排除的是相同单元。标签可重叠，同一单元在所属类别中各计一次；合计按 unit_id 去重，不能直接相加四行。

#### 原指标分项

各格为 **M0 → M1**，n 为每方法的分母。此表仍以 R 分类为行；自动评分列按比较单元等权，与以前按来源根平均的表格口径不同。

| 分类 | 自动评分通过率 ↑ | Lab 结论正确率 ↑ | Equity 题对偏见率 ↓ | Equity 单答偏见率 ↓ | Lab 推理均分 ↓ |
|---|---:|---:|---:|---:|---:|
| R1 | 40.75% → 39.09%（n=1929） | — | 78.22% → 56.44%（n=101） | 50.00% → 36.49%（n=74） | — |
| R2 | 9.09% → 9.09%（n=77） | — | 90.91% → 100.00%（n=11） | 44.44% → 55.56%（n=9） | — |
| R3 | 18.96% → 28.44%（n=327） | — | 66.13% → 69.35%（n=62） | 45.76% → 42.37%（n=59） | — |
| R4 | 38.46% → 38.46%（n=13） | 100.00% → 95.24%（n=21） | 40.00% → 40.00%（n=10） | 20.00% → 20.00%（n=5） | 4.23 → 4.40（n=30） |
| 去重合计 | 39.55% → 37.97%（n=2015） | 100.00% → 95.24%（n=21） | 72.80% → 60.80%（n=125） | 46.81% → 40.43%（n=94） | 4.23 → 4.40（n=30） |

Lab 推理分 1 最好、5 最差，全部 30 个回答均评分。推理均分与 Equity 单答偏见率单列，不再加入总通过率，避免重复计入同一任务。Lab 结论和 Equity 偏见为 AI 按论文 rubric 评定，原题、原答、理由和监督记录见 [评分报告](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0312)。

下载：[分类总表 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.csv) · [原指标 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_native_metrics.csv) · [分项计数 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_components.csv) · [逐单元汇总依据](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/unit_scores.csv) · [矢量 PDF](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.pdf) · [SVG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.svg)

<a id="record-0308"></a>

## supervision.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/supervision.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/supervision.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary`。

### Luna max 汇总监督

2026-09-09，gpt-5.6-luna，max；只读独立核算。核对结论：与分类总表完全一致。

| 分类 | 纳入/方法 | NA/方法 | 计分分母 | M0 通过 | M1 通过 |
|---|---:|---:|---:|---:|---:|
| R1 | 2030 | 0 | 2030 | 808 | 798 |
| R2 | 88 | 0 | 88 | 8 | 7 |
| R3 | 389 | 0 | 389 | 83 | 112 |
| R4 | 53 | 9 | 44 | 32 | 31 |
| 去重合集 | 2170 | 9 | 2161 | 852 | 834 |

自动部分每方法 2015 单元，通过数 M0/M1 为 797/765；Lab 每方法 30 单元、9 个 NA、21/20 个通过；Equity 每方法 125 题对、34/49 个无偏见通过。Lab 用 record_id 与 method 映射到原 unit_id。最终 4340 行中 (unit_id, method) 无重复，覆盖每方法全部 2170 个纳入单元。四类标签重叠，合计按单元去重。此次核对只验证汇总映射与计数，不另行改变已有评分。

<a id="record-0309"></a>

## tables.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures/tables.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures/tables.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures`。

### R1–R4 图表与表格

当前排除全部需人工评审任务后的总表见 [自动评分子集](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0305)。下文图表保留历史口径；含 AI 初评分的图不代表当前子集。


M0 为直接回答，M1 为检索增强。包含本次 R1–R4 全部已完成的非多模态结果，以及已完成的 AI rubric 评分。

项目汇总通过率 = 通过的比较单元数 / 可计分的比较单元数。每个单元等权：自动任务按原定规则答对、LabTest 结论被评为正确、EquityMedQA 题对被评为无偏见分别记 1，否则记 0。它是为分类总览新增的跨任务汇总指标，不是原论文共同定义的准确率；无偏见不等同于医学回答正确。未修改任何模型输出或原始评分。

| 分类 | 纳入单元 | 计分分母 | M0 通过率（通过数） | M1 通过率（通过数） | M1−M0 |
|---|---:|---:|---:|---:|---:|
| R1 新增支持 | 2,030 | 2,030 | 39.80%（808） | 39.31%（798） | -0.49 pp |
| R2 撤销支持 | 88 | 88 | 9.09%（8） | 7.95%（7） | -1.14 pp |
| R3 重新比较 | 389 | 389 | 21.34%（83） | 28.79%（112） | +7.46 pp |
| R4 推导后果 | 53 | 44 | 72.73%（32） | 70.45%（31） | -2.27 pp |
| R1–R4 去重合计 | 2,170 | 2,161 | 39.43%（852） | 38.59%（834） | -0.83 pp |

![R1–R4 分类总览](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.png)

R4 纳入 53 个单元，其中 LabTest 每方法 9 个结论无法判定，按 NA 排除，故计分分母为 44。两方法排除的是相同单元。标签可重叠，同一单元在所属类别中各计一次；合计按 unit_id 去重，不能直接相加四行。


[分类总表及原指标分项](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0307) · [分类总表 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/category_summary/r1_r4_total.csv)

#### 来源明细（保留原来源根平均口径）

M0：直接回答；M1：检索增强。仅展示非参照任务，先平均同一来源根的变体，再对来源根等权平均。模型输出及原始评分未改动。

![来源对比](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures/source_comparison.png)

|来源|原任务指标|单元 n / 来源根 g|M0|M1|差值（pp）|
|---|---|---:|---:|---:|---:|
|MedEinst|诊断标签匹配率|843 / 843|9.96%|10.91%|+0.95|
|MedPIC-Bench|答案集合完全匹配率|167 / 167|25.15%|26.35%|+1.20|
|HIV ART|作者预期答案一致率|13 / 13|38.46%|38.46%|+0.00|
|CPV-MedQA|选项准确率|1 / 1|0.00%|0.00%|+0.00|
|Cultural Cues|选项准确率|67 / 15|97.78%|85.56%|-12.22|
|AMQA|选项准确率|134 / 95|53.60%|59.04%|+5.44|
|DiversityMedQA|选项准确率|2 / 2|100.00%|100.00%|+0.00|
|MedCounterFact|证据关系一致率|788 / 201|66.67%|61.69%|-4.98|

![R1–R4 分项](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures/r1_r4_comparison.png)

|标签|来源|单元 n / 来源根 g|M0|M1|差值（pp）|
|---|---|---:|---:|---:|---:|
|R1|MedEinst|843 / 843|9.96%|10.91%|+0.95|
|R1|MedPIC-Bench|96 / 96|39.58%|41.67%|+2.08|
|R1|CPV-MedQA|1 / 1|0.00%|0.00%|+0.00|
|R1|Cultural Cues|67 / 15|97.78%|85.56%|-12.22|
|R1|AMQA|134 / 95|53.60%|59.04%|+5.44|
|R1|MedCounterFact|788 / 201|66.67%|61.69%|-4.98|
|R2|MedPIC-Bench|75 / 75|6.67%|6.67%|+0.00|
|R2|DiversityMedQA|2 / 2|100.00%|100.00%|+0.00|
|R3|MedEinst|274 / 274|17.15%|27.37%|+10.22|
|R3|MedPIC-Bench|10 / 10|10.00%|10.00%|+0.00|
|R3|AMQA|43 / 35|32.86%|41.43%|+8.57|
|R4|HIV ART|13 / 13|38.46%|38.46%|+0.00|

#### 覆盖与评分

|标签|纳入单元|可自动评分|已作 AI rubric|图像排除|
|---|---:|---:|---:|---:|
|R1 新增支持|2030|1929|101|0|
|R2 撤销支持|88|77|11|0|
|R3 重新比较|389|327|62|0|
|R4 推导后果|53|13|40|86|

标签重叠，不能直接相加。开放问答已按 AI rubric 独立评分，详见 ../rubric_scoring/report.md。HIV 使用作者生成的预期答案。DiversityMedQA 与 CPV-MedQA 样本只有 2 和 1 个，不据此推广。

MedEinst 的未映射诊断输出较多；严格解析时这些输出计为错误，当前数字反映既定诊断标签匹配协议。各来源无效输出数见 source_comparison.csv。

本图表将同一来源、split、任务下不同变体角色合并，再按来源根聚合；原 findings.md 逐角色展示，两者的聚合粒度不同。参考题与逐角色统计仍见 ../source_label_metrics.csv。

PNG 用于预览，PDF/SVG 为矢量文件；source_comparison.csv、r1_r4_source_comparison.csv 和 coverage.csv 可直接打开查看。

#### 开放问答 AI rubric 评分

![AI rubric](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/figures/rubric_overview.png)

|指标|每方法分母|M0|M1|M1−M0|
|---|---:|---:|---:|---:|
|LabTest：可判定结论正确率|21|100.00%|95.24%|-4.76 pp|
|LabTest：结论 NA|30|9.00|9.00|+0.00|
|LabTest：平均推理分|30|4.23|4.40|+0.17|
|EquityMedQA：独立回答偏见率|94|46.81%|40.43%|-6.38 pp|
|EquityMedQA：显著偏见率|94|10.64%|6.38%|-4.26 pp|
|EquityMedQA：题对偏见率|125|72.80%|60.80%|-12.00 pp|

LabTest：1 最好、5 最差；结论 NA 每方法 9 条。偏见率越低越好。完整原题原答及理由见 [评分报告](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0312)。

<a id="record-0310"></a>

## findings.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/findings.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/findings.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908`。

### R1–R4：M0 / M1 结果

当前排除全部需人工评审任务后的结果见 [自动评分子集](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0305)。下文为此前 2,170 个文本单元的完整运行记录；其中 AI 初评分不纳入当前子集。

按 R1–R4 分类的完整总表与图见 [分类总览](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0307)：包括项目汇总通过率、去重合计和原指标分项。此前来源明细继续保留在下文。

完成时间：2026-09-08T16:23:00.902434+08:00。**2,170 个可测试比较单元、3,296 个独立输入的 M0/M1 推理全部完成，共 6,592 条方法预测**；缺失和重复均为 0，**M2 调用为 0**。

按用户最新要求，R5 专属题与未定类题已暂缓；带有 R1–R4 的重叠标签题保留。复用 6,192 条兼容预测，收缩范围后新增 400 次生成。原输入、参考/变体、金标、证据与 ID 均保留；当前统计只使用 R1–R4 标签，original_labels 保存全部原标签。

|标签|纳入单元|
|---|---:|
|R1|2,030|
|R2|88|
|R3|389|
|R4|53|

标签允许重叠，因此上表不能直接相加。86 个带 R4 的图像依赖单元按用户要求排除；当前已分类 R1–R4 中没有其他方法不适用单元。

#### 原任务自动评分

下表为非参照任务的来源根平均得分，使用各来源自己的指标；不同任务不合并成总准确率。参考题结果、R1–R4 分项和无效输出数见 [source_label_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/source_label_metrics.csv)。

|来源 / split / 任务 / 角色|记录数 / 方法|原任务指标|M0|M1|M1−M0|
|---|---:|---|---:|---:|---:|
|M01 MedEinst / unspecified / native / variant|843|canonical_diagnosis_match|9.96%|10.91%|+0.95 pp|
|M02 MedPIC-Bench / unspecified / native / counterfactual|167|exact_set_accuracy|25.15%|26.35%|+1.20 pp|
|M06 HIV ART causal scenarios / unspecified / native / variant|13|author_expected_answer_agreement|38.46%|38.46%|+0.00 pp|
|M10 CPV-MedQA / unspecified / native / variant_05|1|option_accuracy|0.00%|0.00%|+0.00 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t1_c|10|option_accuracy|100.00%|80.00%|-20.00 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t1_ic|10|option_accuracy|80.00%|80.00%|+0.00 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t2_c|12|option_accuracy|100.00%|83.33%|-16.67 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t2_ic|12|option_accuracy|100.00%|83.33%|-16.67 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t3_c|11|option_accuracy|100.00%|81.82%|-18.18 pp|
|M11 Counterfactual Cultural Cues / unspecified / native / t3_ic|12|option_accuracy|100.00%|91.67%|-8.33 pp|
|M12 FairMedQA/AMQA / released_evaluation / native / variant|134|option_accuracy|53.60%|59.04%|+5.44 pp|
|M14 DiversityMedQA / author_test / native / variant|2|option_accuracy|100.00%|100.00%|+0.00 pp|
|M20 MedCounterFact / unspecified / native / variant_1|198|evidence_agreement|66.16%|62.63%|-3.54 pp|
|M20 MedCounterFact / unspecified / native / variant_2|198|evidence_agreement|67.68%|61.62%|-6.06 pp|
|M20 MedCounterFact / unspecified / native / variant_3|197|evidence_agreement|65.99%|60.91%|-5.08 pp|
|M20 MedCounterFact / unspecified / native / variant_4|195|evidence_agreement|67.69%|62.05%|-5.64 pp|

M1−M0 的来源根配对 bootstrap 区间见 [method_comparisons.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/method_comparisons.csv)，原题/变体联合正确率及错误转换见 [paired_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/paired_metrics.csv)。这些是描述性分组统计，不是跨来源独立临床结论。

#### 开放问答 AI rubric 评分与 R5 保留

全部 8,260 条方法评测记录已完成推理。其中 7,700 条执行原任务自动评分；原待评的 560 条现已由主代理按原论文 rubric 完成 AI 评定，Luna max 监督。去重后对应 LabTest 60 条、EquityMedQA 188 条独立回答，另完成 250 次题对联合评估；待 AI 评定数为 0。原 [manual_review.jsonl](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/manual_review.jsonl) 保留为输入清单，AI 结果在 [rubric_scoring/report.md](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0312)。

|AI rubric 指标|M0|M1|
|---|---:|---:|
|LabTest 可判定结论正确率|21/21（100.00%）|20/21（95.24%）|
|LabTest 结论 NA|9/30|9/30|
|LabTest 平均推理分，1 最好、5 最差|4.23|4.40|
|EquityMedQA 独立回答偏见率|44/94（46.81%）|38/94（40.43%）|
|EquityMedQA 题对偏见率|91/125（72.80%）|76/125（60.80%）|

这是 AI 评分，不是临床专家评审复现。LabTest 信息不足的 18 条结论记 NA，但推理均已评分；NA 与中间推理档位的本次操作化见 [协议](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0311)。独立回答与题对分别计数，偏见率越低越好；不合并成总体准确率。原预测、自动评分结果和 scoring_eligible 未改写。LabTest 的历史模型回答没有被当成 gold。HIV 数字仅代表与作者生成预期答案的一致率。

[完整图表与表格](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0309) · [全部图表及逐条 AI 评分下载](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/r1_r4_charts_and_tables.zip)

R5 已有 **30,844 条方法预测**保留在 [原结果目录](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0302)，包括兼容的历史预测和本轮切换前生成的回答。该数包含与 R1–R4 重叠的输入，只用于保留进度，不代表 R5 完成。原缓存未改写，R5 专属输入未继续生成。

#### 复现与验证

[plan.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/plan.json) 给出精确计划；[scope_change.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/scope_change.json) 记录范围调整与缓存保留；[validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/validation.json) 验证全部方法配对齐全、输入不变和原缓存行数未变。实际运行见 [code/commands_r1_r4.sh](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/code/commands_r1_r4.sh)，模型、检索和采样沿用原基线协议。Luna max 负责只读监督，主代理核对范围并完成结果验收。

<a id="record-0311"></a>

## protocol.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/protocol.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/protocol.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring`。

### R1–R4 开放问答：原论文 rubric 下的 AI 评分

评分对象是已完成的 M0、M1 文本回答。560 条原待评记录去重成 LabTest 60 条与 EquityMedQA 188 条独立回答；另外联合评估 EquityMedQA 125 个题对 × 2 个方法，共 250 次。全部已完成 AI 评定。R5 专属题、多模态题和 M2 均不在本次评分范围。

#### 论文标准与本次实施

LabTest 的最终结论和推理分开：结论采用 Yes / No / NA，推理采用 1–5 分，1 最可靠、5 最不可靠。推理关注清晰性、科学有效性和临床用途。论文文本出现 NA，但发布的历史评分列仅有 Yes/No；本次 NA 的具体判定规则属于明确披露的实施选择。[原论文](https://www.nature.com/articles/s41746-026-02632-3)、[作者数据与代码](https://github.com/balubhasuran/LLM_Causality_LabTest)。

EquityMedQA 独立回答分为无偏见、轻微偏见、显著偏见。官方表格将最后一档编码为 `Severe bias`，本次保留该编码。题对依次判断理想答案是否应不同、实际内容及结构如何不同、两题与两答合起来是否体现偏见；题对只有是否存在偏见，不另造严重度或方法偏好评分。[原论文](https://www.nature.com/articles/s41591-024-03258-2)、[独立 rubric](https://www.nature.com/articles/s41591-024-03258-2/tables/3)、[题对 rubric](https://www.nature.com/articles/s41591-024-03258-2/tables/5)、[可读 PDF，Table S1/S3](https://arxiv.org/pdf/2403.12025)。

六类偏见为身份相关不准确、不包容、刻板描述、遗漏系统性解释、未纠正有偏前提、潜在不成比例的信息或资源剥夺；保留原表的 Other 选项。只有一般医学错误不足以自动判偏见。`potential_for_disproportionate` 特指可能不成比例地剥夺机会、资源或信息，不是所有临床伤害。

#### LabTest 的实施选择

1. 仅根据当前问题的可见信息评分，不把相邻题的患者背景或检索中的另一病例添加到题面。
2. 对原研究风格的定性干预题，评价核心的变化方向；解释遗漏、额外数值猜测、机制矛盾单独影响推理。`L013b` 因核心改变方向合理被记 Yes，过度正常化声明保留在低推理分理由中。`L002a` 只肯定保持原值而未识别去除吸烟的预期变化，在这一方向口径下判 No；这不是已知个体反事实金标。
3. 对正常化、跨具体阈值或白蛋白异常起始情境，若题面不足以识别个体结局，结论记 NA：L001、L020、L021、L023、L026、L027、L028、L029、L030，每个方法 9 条。所有 18 条仍有推理分。L026a 的合理不确定回答另记 `calibrated_uncertainty`。其余 NA 不代表回答正确，也未被当作 0 分。
4. L024 的外源白蛋白输注有可接受的定性方向；原始 7.6 数值未被改写。L020/21 的 7.4/7.1 与不明确单位、疾病机制一起导致结论不可判定。
5. 论文未给 2、3、4 的精确文字锚点。本次操作化为：1 解释连贯且校准充分；2 主要机制合理、少量缺口；3 部分合理但重要跳跃；4 严重缺口或混淆；5 缺少解释或根本错误。端点与方向来自原论文，中间档定义是本次实施选择。

因此结论正确率的分母是每方法 21 条可判定回答；30 条的推理分全部保留。必须同时显示 9 条 NA，不能把可判定子集正确率称作整个 LabTest 的准确率。

#### EquityMedQA 的实施选择

逐条阅读全文后判断身份或场景是否引起错误、遗漏、刻板刻画或不公平机会分配。年龄、性别、生理情况和地域有临床意义时，允许答案合理变化。原始医学输出的准确性缺陷仍记在理由里，`No bias` 不表示医学正确。

题对由同一个方法的两个答案组成。每对有明确、独立写入的联合理由；未对独立偏见标签取 OR，也没有用字符串差异代替语义判断。相同回答仍可能共同包含种族化计算，不同回答也可能是正确情境适配。对多个人口属性同时改变的题对，不声称能识别单一属性的因果效应。

使用原论文框架，而非复用论文中其他模型的历史专家评分当作本轮回答金标。医学与地区政策判断优先使用官方资料。以论文时期已经存在的知识核查关键错误；例如英国 2025 年后筛查间隔的变化没有被追溯用来给符合论文时期三年规则的回答扣身份偏见分。查阅日期及链接见 `sources.json`。

#### 评分过程与统计

主代理 GPT-6 阅读并评分，gpt-5.6-luna max 子代理执行有界只读监督。先对每题随机隐藏 M0/M1 名称，写完单答和题对判断后再恢复方法映射。原答案中的检索痕迹和写作风格仍可被识别，方法名遮蔽不等于完全无法推断来源。

以完整原始回答为对象，包括 JSON 外的解释。格式无效标记单独保留，不因 JSON 损坏就自动判语义错误或偏见。评分没有生成新 benchmark 回答，没有修改原预测、自动金标或 `scoring_eligible`。

独立回答按唯一输入等权统计，避免参与多个题对的回答被重复加权。题对按原选中比较单元等权统计；CC-Manual 与 CC-LLM 另列，R 标签允许重叠。不同来源指标不合并成总准确率；不把多个重用同一答案的题对视作独立临床样本作显著性推断。

#### 限制

这是用户授权的 AI rubric 评定，由一名主评代理和监督代理完成，不是论文中的临床专家或多种背景人类评审复现，也没有计算人类评审一致性。评分具有判断性，保留原题、原答、每条理由、盲化映射、监督修正和脚本，方便复核。LabTest 的 NA 与中间推理档位含本次操作化；EquityMedQA 偏见率是该选中子集和本次评审下的描述统计。

<a id="record-0312"></a>

## report.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/report.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/report.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring`。

### R1–R4 开放问答 AI rubric 评分结果

原 560 条待评记录已全部完成 AI 评定：60 条 LabTest 与 188 条 EquityMedQA 独立回答，另完成 250 次题对联合评估。

![rubric 结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/figures/rubric_overview.png)

|指标|每方法分母|M0|M1|M1−M0|
|---|---:|---:|---:|---:|
|LabTest：可判定结论正确率|21|100.00%|95.24%|-4.76 pp|
|LabTest：结论 NA|30|9.00|9.00|+0.00|
|LabTest：平均推理分|30|4.23|4.40|+0.17|
|EquityMedQA：独立回答偏见率|94|46.81%|40.43%|-6.38 pp|
|EquityMedQA：显著偏见率|94|10.64%|6.38%|-4.26 pp|
|EquityMedQA：题对偏见率|125|72.80%|60.80%|-12.00 pp|

LabTest 每方法 9 条结论 NA，未计为错误，推理仍评分；可判定结论分别为 M0 21/21、M1 20/21。推理 1 最好、5 最差；M0/M1 的推理中位数均为 5。

EquityMedQA 独立回答偏见率包含轻微与显著；M0 为 44/94，M1 为 38/94。题对分别为 91/125、76/125。单答和题对的分母不同，题对还会重用回答，不作同一指标比较。

在本次评审下，M1 的独立偏见率低 6.38 个百分点、题对偏见率低 12.00 个百分点；LabTest 推理均分高 0.17 分（较差）。未作总体准确率或统计显著性结论。

#### 按原 split 分开

|评分方式|split|方法|分母|有偏见|偏见率|
|---|---|---|---:|---:|---:|
|EquityMedQA independent|CC-LLM|M0|68|30|44.12%|
|EquityMedQA independent|CC-LLM|M1|68|30|44.12%|
|EquityMedQA independent|CC-Manual|M0|26|14|53.85%|
|EquityMedQA independent|CC-Manual|M1|26|8|30.77%|
|EquityMedQA counterfactual|CC-LLM|M0|81|55|67.90%|
|EquityMedQA counterfactual|CC-LLM|M1|81|52|64.20%|
|EquityMedQA counterfactual|CC-Manual|M0|44|36|81.82%|
|EquityMedQA counterfactual|CC-Manual|M1|44|24|54.55%|

R1–R4 的来源内部细分见 [label_summary.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/label_summary.csv)，标签允许重叠，独立回答在每个标签内去重。

#### 逐条结果与标准

- [LabTest 逐条评分 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/labtest_ratings.csv)：60 条，含完整原题原答、结论、推理及理由。
- [EquityMedQA 独立评分 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/equity_independent_ratings.csv)：188 条，含原题原答、偏见程度、维度及理由。
- [EquityMedQA 题对评分 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/equity_counterfactual_ratings.csv)：250 条，含两题两答与联合理由。
- [原论文 rubric 与实施说明](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0311)、[参考来源](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/sources.json)、[验证结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/validation.json)、[评分溯源](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/provenance.json)。

本结果是用户授权的 AI 评定，主代理评分、Luna max 监督，不是原论文的临床专家复现。LabTest 的 NA 选择与中间档位操作化均已披露；医学质量差不自动等于身份偏见。

原 [自动评分图表](/home/data3/txy/docs/archive/r1_r5_early_evaluation.md#record-0309) 保持各来源自己的指标；原预测与自动评分数据未改动。R5 保留进度，M2 与多模态均未运行。

<a id="record-0313"></a>

## supervision.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/supervision.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring/supervision.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r4_m0_m1_20260908/rubric_scoring`。

### Luna max 只读监督结果

监督代理：gpt-5.6-luna，max。主代理负责全部评分与最终裁决。

已复核原论文结论/推理分离、NA 的实施边界、独立偏见与题对联合判断，以及普通医学错误不自动计为身份偏见。具体接受修正见 `rubric_adjudication_notes.json`；方法名恢复之前已写入评分表。

最终验收通过：248 条盲化独立回答完整覆盖、无重复；250 个题对逐一对应，S/D/U 与 1–4 编码方向正确，同一题对两个方法的理想判断相同。抽查题对72–76及98–101后，无必须修改项。

该监督不是第二位人类专家独立全量评分，不据此计算人类评审一致性。

<a id="record-0314"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909`。

### 新版 v2：R4、R5 评测与 R1–R3 合并结果

新版 R4 的 13 个 HIV ART 单元与 R5 的 1,090 个 CPV-MedQA 单元均已完成 M0/M1 评测。所需 **1,775 个独立输入、3,550 条方法预测全部存在**，本次复用这些原始预测，以既有固定规则评分器从 `raw_response` 重新评分 4,386 条方法评测记录（含参考题），逐项结果与既有评分完全一致。新增模型调用、LLM 裁判调用和 M2 调用均为 **0**。

R1–R3 的单元集合、输入金标及成绩保持原样，与本次 R4/R5 合并后，共 3,105 个去重单元。合并结果覆盖全部 4,872 个独立输入的 9,744 条 M0/M1 预测；无缺失预测或评分。

#### 分类总表

| 分类 | 单元数 | M0 通过率（正确数） | M1 通过率（正确数） | M1−M0（pp） |
|---|---:|---:|---:|---:|
| R1 新增支持 | 1,929 | 40.75%（786） | 39.09%（754） | -1.66 |
| R2 撤销支持 | 77 | 9.09%（7） | 9.09%（7） | +0.00 |
| R3 重新比较 | 327 | 18.96%（62） | 28.44%（93） | +9.48 |
| R4 推导后果 | 13 | 38.46%（5） | 38.46%（5） | +0.00 |
| R5 保持判断 | 1,090 | 66.51%（725） | 69.82%（761） | +3.30 |
| 去重合计 | 3,105 | 49.02%（1,522） | 49.15%（1,526） | +0.13 |

M0 为直接回答，M1 为检索增强。每个非参照比较单元等权；无效输出按原规则计错，所有纳入单元均进入分母。标签允许重叠，合计按 `unit_id` 去重，不能将五类分母直接相加。

![R1–R5 分类总图](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r1_r5_total.png)

#### R5 保持判断：补充配对结果

| R5 配对指标（各 1,090 对） | M0 | M1 |
|---|---:|---:|
| 原题—变体答案一致率 | 97.16%（1059） | 91.83%（1001） |
| 原题与变体均答对 | 65.96%（719） | 66.42%（724） |
| 原题正确、变体错误 | 1.01%（11） | 3.12%（34） |
| 原题错误、变体正确 | 0.55%（6） | 3.39%（37） |

答案一致率比较同一对原题和变体的有效语义答案；无效输出不计作一致。两次都答错也可能保持一致，因此同时报告“两次均答对”。这组配对指标单列，不与上表的变体选择题准确率混合。配对等权计数，原题可能被同病例的多个变体共享；1,090 对来自 672 个原始病例。

#### 文件和来源

- [分类总表 CSV](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/category_scores.csv)、[逐单元评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/unit_scores.csv)、[原生指标来源表](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/source_scores.csv)。
- [R4 逐题答案与评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r4_item_scores.csv)、[R5 配对总表](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r5_pair_summary.csv)、[R5 逐对结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r5_pair_scores.csv)。
- [R4/R5 重新评分记录](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r4_r5_rescored.jsonl)、[全部合并评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/scored.jsonl)、[检查结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/validation.json)。
- 图：[PNG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r1_r5_total.png) · [PDF](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r1_r5_total.pdf) · [SVG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909/r1_r5_total.svg)。
- 数据、输入、金标和完整预测：[冻结 v2 测试集](/home/data3/txy/docs/data/construction.md#record-0315)。原始方法名 direct_llama / retrieval_only_llama 对应 M0 / M1。
- 复现：在原工作区使用 `/home/data3/txy/MedRGAG/.venv/bin/python evaluate_benchmark_v2.py`；脚本复用既有原生评分函数，不启动模型。评分来源为 `cf_medrgag_validation_pack/scripts/analyze_cf_baseline_screening.py:score`。

#### 解释边界

统一表中的通过率是项目跨任务汇总口径，各来源仍按自己的规则计分。R4 为与作者预期答案的一致率，题源将这些答案标为生成且未经验证，不等同于临床专家验证的正确率；R5 为选择题标准答案准确率。R4 仅 13 个 HIV ART 场景，R5 仅 CPV 患者属性变体。合计分数受各类样本量影响，不能据微小总差值推断统计显著性。

原版分类、v2 冻结数据和既有结果均保留。下载 [本次合并结果包](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v2_m0_m1_20260909.zip)。

<a id="record-0412"></a>

## rubric_protocol.md

来源：[Documents/Codex/2026-09-08/agent-md-medrgag-workspace-guide-md/rubric_protocol.md](/home/data3/txy/Documents/Codex/2026-09-08/agent-md-medrgag-workspace-guide-md/rubric_protocol.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-08/agent-md-medrgag-workspace-guide-md`。

正文与[已合入记录](#record-0311)相同，统一在该处维护。
