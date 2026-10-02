# 全Llama MedRGAG（M2）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。M2保留初始检索→KGCC→缺失知识探索与生成→KADS→最终重排和reader，所有LLM角色用Llama。已完成v3和v5；v5包含6,687条复用和7,218条新增预测。早期Table 1与v15复现详见复现归档。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [Complete v3 R1–R5 M2 evaluation (2026-09-09)](#record-0013)
- [4. Full all-Llama MedRGAG baseline](#record-0025)
- [Purpose and status](#record-0026)
- [Command interface](#record-0027)
- [Main implementation files](#record-0028)
- [3.1 M0 / M2](#record-0093)
- [4.2 M2：阶段剖析，未削减完整方法](#record-0099)
- [3.2 M2：完成覆盖、复用与新增计算](#record-0238)
- [REPRODUCE_ALL_LLAMA.md](#record-0261)
- [README.md](#record-0317)
- [supervision.md](#record-0318)

<a id="record-0013"></a>

## Complete v3 R1–R5 M2 evaluation (2026-09-09)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第488行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Complete v3 R1–R5 M2 evaluation (2026-09-09)

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

<a id="record-0025"></a>

## 4. Full all-Llama MedRGAG baseline

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1091行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 4. Full all-Llama MedRGAG baseline

<a id="record-0026"></a>

## Purpose and status

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1093行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Purpose and status

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

<a id="record-0027"></a>

## Command interface

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1126行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Command interface

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

<a id="record-0028"></a>

## Main implementation files

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1162行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Main implementation files

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

<a id="record-0093"></a>

## 3.1 M0 / M2

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第76行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 3.1 M0 / M2

保留既有 Llama BF16、提示和解码设置。M2 保留完整 KGCC/KADS、五候选与最终 reranking；固定证据一直可见。每个新输入包含 5 次摘要、1 次探索、5 次候选生成、1 次选择、1 次最终回答，共 13 次生成阶段；7,218 个新输入对应 93,834 次新阶段调用。检索与 reranking 另外审计，不能再次当作 LLM 生成调用相加。

M2 的新增 robustness 最终回答使用既有 JSON 格式和 2,048 token 预算，其余最终回答为 64 token。运行容量采用显存份额 0.75、batch 64；这是本地运行配置，不是新增方法模块。M0/M2 最大上下文设置为 98,304。精确阶段数和 token 统计见[阶段审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/artifact_audit.json)，复现应读取其原始运行配置而非从本文推断未列出的采样参数。

<a id="record-0099"></a>

## 4.2 M2：阶段剖析，未削减完整方法

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第151行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 4.2 M2：阶段剖析，未削减完整方法

对三个 batch64 实测：总耗时约 262.52 / 268.65 / 271.39 秒，检索约 62–67 秒、选择约 79 秒、摘要约 38–40 秒、探索约 28 秒、候选生成约 38–39 秒，最终回答约 12–13 秒，reranking 约 1.8–1.9 秒。详见[原始剖析](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m2_stage_timing_profile.json)。

主要成本来自方法内部阶段，未发现可直接照搬 PubMed 缺失偏移的同类大瓶颈。没有为提速删摘要、候选、选择或最终回答。这里记录的是已观察到的瓶颈，而非已完成一个新的 M2 算法优化。

<a id="record-0238"></a>

## 3.2 M2：完成覆盖、复用与新增计算

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第57行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 3.2 M2：完成覆盖、复用与新增计算

| 原状态 / 需求 | 实际调整 | 原因及影响 |
|---|---|---|
| 既有 M2 结果已覆盖大量相同任务，但当前 v3 还包含新输入 | 按 ID、题目、选项及顺序、固定证据、答案格式和运行条件连接结果；复用 4,720，补跑 152 | 覆盖完整 v3，同时避免把相同输入重复推理；“完整测试”不等于 4,872 条全都重新计算 |
| 用户要求全部 LLM 角色用 Llama | 沿用相同 Llama 权重执行摘要、探索、知识生成、KADS 和最终回答；MedCPT 继续承担原有检索/重排职责 | “全 Llama”指 LLM 角色；不等于删除原方法的专用检索器 |
| 测试原 MedRGAG，不加入项目新增模块 | 保留原 KGCC/KADS 等方法步骤；本轮 Profile、CFShift、CFMoE、WM、残差适配器及额外裁判调用为 0 | 原方法组成与本项目新增模块分别核对，避免把原方法本身的组件误删 |
| 新输入需要各阶段可追溯 | 每个新输入执行 13 次 Llama 调用，保留检索、重排、阶段 prompt 和结果索引 | 152×13＝1,976 次新增调用；生成 760 个知识候选，完整覆盖审计通过 |
| 需要和 M0/M1 比较 | 读取冻结 v3 旧结果，按原生评分规则生成类别、来源及 R4/R5 辅助表和图 | 这一报告步骤是离线汇总，不是再次执行三种方法 |

运行细节以 `V3_M2/config.json` 为准。该次新增计算使用 Llama-3.1-8B-Instruct BF16、98,304 上下文容量；初始 BM25 每源 32 候选，MedCPT 取 top-5，之后执行原方法增强流程。新增计算墙钟为 231 秒；复用历史计算的成本单列，不能与 M3 全部新生成的墙钟直接比较方法速度。

<a id="record-0261"></a>

## REPRODUCE_ALL_LLAMA.md

来源：[MedRGAG/REPRODUCE_ALL_LLAMA.md](/home/data3/txy/MedRGAG/REPRODUCE_ALL_LLAMA.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/MedRGAG`。

### 全 Llama-3.1-8B MedRGAG 测试指南

本入口把 summarizer、explorer、generator、integrator/selector 和 reader 五个 LLM
角色都指向同一个本地 Llama-3.1-8B-Instruct checkpoint。它不会构造 OpenAI client，
也不需要或使用 `.env` 中的 OpenAI API key。

这不是论文 Table 1 或 Figure 3(b) 的原样复现：

- Table 1 的 Llama 行是 Llama generator + Llama reader + GPT-4o-mini auxiliaries，覆盖五个数据集；
- Figure 3(b) 的 Llama auxiliary 消融固定 Qwen2.5-7B reader，只报告三个数据集；
- 本实验把五个角色全部替换为同一 Llama checkpoint，是论文没有报告的新交叉组合。

阶段入口为
[reproduce_medrgag_all_llama.py](/home/data3/txy/MedRGAG/reproduce_medrgag_all_llama.py)，
无人值守编排入口为
[run_medrgag_all_llama.sh](/home/data3/txy/MedRGAG/run_medrgag_all_llama.sh)，本地辅助后端为
[src/medrgag_local_aux.py](/home/data3/txy/MedRGAG/src/medrgag_local_aux.py)。

#### 当前科研执行语义

当前采用“科研宽容、工程完整性严格”的语义。模型输出质量差是实验数据，不是停止整个
实验的理由：

- summary、explore 和 select 仍执行原有格式、截断、重复、范围和解析检查；
- 完成推理但未通过这些检查的记录仍以 `status=ok` 落盘，表示调用完成且已有确定的下游
  payload；质量单独记录为 `model_output_valid=false`、`validation_status=invalid`、
  `parse_warnings`/`quality_warnings`，同时保留 `InvalidModelOutput` error sidecar；
- explore 缺失的编号位置使用字符串 `None` 补齐，以便 generator 继续；
- select 重复、少于五个或空选择都保留诊断。空选择传入空的 MedCPT 输入，reader 随后执行
  question-only 推理；
- evaluate 报告每个数据集的 `summary_model_output_invalid`、
  `explore_model_output_invalid`、`select_model_output_invalid`、截断和解析警告等质量计数。

以下问题仍然是致命错误并以非零退出码停止无人值守脚本：vLLM/MedCPT/CUDA 或其他后端
异常、无法构造任何确定下游 payload 的 Python/parser 异常、缺失或损坏的上游 artifact、
profile/input/source/hash 不一致。编排脚本不会用 `|| true` 隐藏这些技术失败。

旧的全量质量安全闸已经删除。现在不带 `--limit` 可以直接运行全部五个数据集，
`--allow-unvalidated-full-run` 也已经从 CLI 删除，不应再传。允许执行不等于认可结果：所有
全量报告仍必须标明 `experimental_not_table1=true`，并完整报告 invalid、截断、fallback 和
人工审核限制。

#### v15 profile 与解释边界

当前默认 profile 是 `role-stable-v15-guided-sentence-labels`：

| 角色 | temperature | top_p | top_k | frequency penalty | max tokens | seed |
|---|---:|---:|---:|---:|---:|---|
| summary | 0.0 | 1.0 | -1 | 0.1 | 64 | 按请求派生 |
| explore | 0.0 | 1.0 | -1 | 0.0 | 1024 | 按请求派生 |
| select | 0.0 | 1.0 | -1 | 0.0 | 2048 | 按请求派生 |
| generator | 1.2 | 0.9 | 50 | 0.0 | 256 | 未设置（发布代码行为） |
| reader | 0.1 | 1.0 | -1 | 0.0 | 512 | 42 |

summary 会把每篇 retrieval 文档确定性切成 `[S0]`、`[S1]` 等原句，通过动态 xgrammar
正则限制模型只能选择真实标签或 `NONE`，再由程序逐字回填原句。xgrammar 固定为
`0.1.18`。这保证机械 grounding，但不保证所选证据具有语义相关性。

MedQA 前 10 题曾反复用于 v4–v15 prompt 调试，不是 held-out。人工审核的 50 个摘要/
证据选择中，acceptable=30、suboptimal=13、blocking=7，详见
[ALL_LLAMA_V15_AUDIT.md](/home/data3/txy/docs/archive/medrgag_reproduction.md#record-0260)。这些发现现在是
必须报告的质量诊断，而不是禁止科研运行的门；它们也意味着全量结果不能被描述为论文
Table 1 的可比复现或可靠效果估计。

论文没有披露 Figure 3(b) 本地 auxiliary 的 checkpoint revision、chat template、完整
sampling、max tokens、seed、dtype、batch 或错误处理。v15 的低温、输出上限、派生 seed、
本地 chat template、结构约束和 fallback 都是明确披露的工程干预，不是“只换模型”的
因果消融。generator 仍无 seed，因此整条流水线不保证逐位确定性。

#### 冻结的历史运行

`all-llama-five-dataset-full-v1` 是旧严格语义下的完整尝试：

- retrieval：7,663/7,663；summary：38,315/38,315；explore：7,663/7,663；
  generate：38,315/38,315；
- select 实际完成了 7,663 次推理，其中 7,596 条旧状态为 `ok`、67 条旧状态为 `invalid`；
- 旧安全门因此在 select 末尾退出，rerank、reader、evaluate 未运行，没有 metrics；
- 67 条是模型真实输出，但把它们标成不可消费并让阶段退出是旧工程化语义，不是公开代码
  本身的要求。

为实现当前科研宽容语义，runner/backend 及空输入处理源码已经改变；manifest 会锁定这些
源码 SHA。因而该旧 run 与 `all-llama-smoke1-v19` 等早期 smoke 都已经冻结为历史证据，
**不能用当前源码和同一 run-id 续跑**。不要改写旧 manifest 或旧 records。下一次正式运行
必须使用新的 run-id，例如 `all-llama-five-dataset-lenient-v1`。

早期 `all-llama-smoke1-v19` 的 15/15 records、7/7 complete 和 0 errors 仍可证明旧字节下
一题链路曾完整工作，但它不再是“当前源码可续跑断点”。

#### 无人值守全流程

脚本按以下固定顺序调用八个独立进程：

```text
retrieval -> summary -> explore -> generate -> select -> rerank -> reader -> evaluate
```

每个阶段退出后模型进程会释放资源。脚本自动传 `--retry-pending-local`；同一源码、配置、
profile 和 run-id 下重新启动时，已有有效 artifact 会被校验并跳过，中断留下的 pending 会
被归档后重算。脚本使用 `flock` 防止同一 run-id 并发执行，并把状态和追加日志写到：

```text
runtime_logs/all-llama-<run-id>.state
runtime_logs/all-llama-<run-id>.log
```

先做零副作用 dry-run。它只打印命令，不创建日志、锁或 artifact：

```bash
cd /home/data3/txy/MedRGAG

./run_medrgag_all_llama.sh \
  --run-id all-llama-five-dataset-lenient-v1 \
  --retrieval-source-run \
  /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1 \
  --dry-run
```

后台启动完整五数据集流程：

```bash
./run_medrgag_all_llama.sh start \
  --run-id all-llama-five-dataset-lenient-v1 \
  --retrieval-source-run \
  /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1
```

查看一次状态及最后 20 行日志：

```bash
./run_medrgag_all_llama.sh status \
  --run-id all-llama-five-dataset-lenient-v1
```

持续跟随日志：

```bash
./run_medrgag_all_llama.sh attach \
  --run-id all-llama-five-dataset-lenient-v1
```

`attach` 只是 `tail -f`；按 `Ctrl+C` 只停止日志查看，不会停止后台 pipeline。也可以省略
`start` 子命令以前台运行。此前聊天中的周期性监督从未驱动模型或阶段切换；旧 run 本身已
在 tmux 中通过 shell 循环自动执行。聊天轮询只消耗了用于读取和转述状态的 token，新脚本
不需要任何 assistant 常驻监督。

可用 `--from-stage` 和 `--to-stage` 指定包含端点的阶段范围。例如只打印 generate 到 reader：

```bash
./run_medrgag_all_llama.sh \
  --run-id all-llama-five-dataset-lenient-v1 \
  --from-stage generate --to-stage reader --dry-run
```

若技术故障导致停止，应先修复故障，再用同一 run-id 和相同参数重启；必要时用
`--from-stage` 从故障阶段开始。若源码、profile、batch、数据范围或其他 manifest 内容改变，
必须使用新 run-id，不能把不兼容产物混在一个 run 中。

#### 有界 smoke

MedQA 前 10 题可用同一脚本运行；必须使用独立 run-id：

```bash
./run_medrgag_all_llama.sh start \
  --run-id all-llama-medqa10-lenient-v1 \
  --datasets medqa --limit 10 \
  --retrieval-source-run \
  /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/released-code-intent/table1-full-v1
```

一个 smoke 或正式 run 至少应审计：所有 `finish_reason`、invalid/error 数和 completion token
分布；summary 的 source rendering 与人工相关性；explore 的 2/3 点分支和 fallback；selector
的 exact-five、unique、in-range、空选择及解析警告；reader strict parse rate；生成文档的医学
事实、幻觉和答案泄漏。

五数据集全量为 7,663 题，每题 13 个 Llama 输出：5 summary + 1 explore + 5 generator +
1 select + 1 reader，共 99,619 个本地输出。OpenAI 请求和 API 费用为 0，代价转为 GPU 时间。

#### 验证

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m py_compile \
  reproduce_medrgag_all_llama.py \
  src/medrgag_local_aux.py src/medrgag_local_prompts.py
.venv/bin/python -m pip check
```

当前为 35/35 测试通过。覆盖全本地 mock E2E、科研宽容 invalid、空模型 completion、技术
失败仍致命、空选择到 question-only reader、缺失 knowledge 位置补齐、无人值守脚本 dry-run
零副作用与阶段范围、八阶段真实 shell 编排及非零退出停止、OpenAI 零构造、resume、donor、
动态 xgrammar、source rendering、MedMCQA 两点分支以及 profile/source/artifact 哈希。

<a id="record-0317"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909`。

### R1–R5 v3：M2 全 Llama MedRGAG 完整测试

全部 **4,872/4,872 个独立输入**完成 M2，覆盖 **3,105 个互斥单元、6,030 条评分映射**（含参考题），无缺失或重复预测。采用 v3 当前 `labels`；分类为 R1/R2/R3/R4/R5 = 1,601/77/324/13/1,090。

本次复用 4,720 个相同 ID、题目、选项及其顺序、固定证据和答案格式的既有 M2 完整流程结果，并补跑 152 个新输入。复用与补跑使用相同模型、提示构建函数、解码参数及逐输入/阶段/槽位种子。M0/M1 来自冻结 v3 原始预测和评分。

#### 分类结果

| 分类 | 单元数 | M0 | M1 | M2 | M2−M0 | M2−M1 |
|---|---:|---:|---:|---:|---:|---:|
| R1 新增支持 | 1,601 | 45.22% | 41.29% | 44.41%（711） | -0.81 pp | +3.12 pp |
| R2 撤销支持 | 77 | 9.09% | 9.09% | 7.79%（6） | -1.30 pp | -1.30 pp |
| R3 重新比较 | 324 | 18.83% | 28.40% | 23.46%（76） | +4.63 pp | -4.94 pp |
| R4 推导后果 | 13 | 38.46% | 38.46% | 53.85%（7） | +15.38 pp | +15.38 pp |
| R5 保持判断 | 1,090 | 66.51% | 69.82% | 70.28%（766） | +3.76 pp | +0.46 pp |
| ALL 合计 | 3,105 | 49.02% | 49.15% | 50.43%（1,566） | +1.42 pp | +1.29 pp |

每个非参照单元等权，无效输出计错。M2−M0/M1 为通过率百分点差；本表为描述性对照。

![三方法分类结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r1_r5_three_methods.png)

#### R5 配对结果

| R5 配对指标（各 1,090 对） | M0 | M1 | M2 |
|---|---:|---:|---:|
| 答案一致 | 97.16%（1059） | 91.83%（1001） | 78.81%（859） |
| 两题均正确 | 65.96%（719） | 66.42%（724） | 62.02%（676） |
| 正确变错误 | 1.01%（11） | 3.12%（34） | 7.80%（85） |
| 错误变正确 | 0.55%（6） | 3.39%（37） | 8.26%（90） |

1,090 对来自 672 个 CPV-MedQA 病例；参考输入可以复用。答案一致也可能是两题都答错，因此单列“两题均正确”，不替代上表的变体准确率。

#### 配置、运行与复用

M2 使用 Llama-3.1-8B-Instruct BF16，上下文容量 98,304。流程是 BM25（textbooks/wikipedia 每源 32 候选）→ MedCPT 初始 top-5 → 5 次 KGCC 摘要 → 1 次缺失知识探索 → 5 路知识生成 → 原始 KADS → MedCPT 最终重排 → Llama 阅读器。所有 LLM 角色使用相同 Llama；MedCPT 保留原基线检索重排职责。Profile、CFShift、CFMoE、MA-RAG、Qwen、WM、适配器及额外评分模块调用均为 0。

阅读器 T=0/max_tokens=64；摘要 64、探索 1,024、生成每路 256、KADS 2,048 token；生成 T=1.2/top_p=.9/top_k=50/presence_penalty=1。每个新输入执行 13 次 Llama 调用，共 **1,976 次**，产生 760 个生成文档候选。初始检索复用同输入 M1 已保存的 5 篇文档。无格式修复、无模型裁判，超长输入按原运行器报错而不截断。

GPU 1/2，batch/chunk=64，gpu_memory=.75，主种子 20260906。实际补跑：2026-09-09T16:54:30+08:00 至 2026-09-09T16:58:21+08:00，墙钟 **3.85 分钟**。新增逻辑 prompt token **2,062,136**，completion token **487,180**。费用表中的复用 token 是既有推理记录，不计入本次新增成本。

用户指定的 Luna max 子代理负责只读运行监督，主代理核查进度及最终完整性。历史 M2 全流程审计见 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/artifact_audit.json`。本次全量阶段索引覆盖每个输入的全部 13 个 LLM 槽位及检索/重排记录；新增 1,976 条完整 prompt 引用均通过检查。两工作进程退出码均为 0。

#### 文件与复现

- [分类总表](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/category_scores.csv)、[来源原生指标](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/source_scores.csv)、[逐单元结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/unit_scores.csv)。
- [M2 原始预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/m2_predictions.jsonl)、[M2 完整评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/m2_scored.jsonl)、[三方法预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/predictions.jsonl)、[三方法评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/scored.jsonl)。
- [R4 逐题结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r4_item_scores.csv)、[R5 配对汇总](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r5_pair_summary.csv)、[R5 逐对结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r5_pair_scores.csv)。
- [Luna max 独立复核](/home/data3/txy/docs/baselines/medrgag.md#record-0318)、[完整性检查](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/validation.json)、[阶段审计](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/artifact_audit.json)、[冻结计划](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/plan.json)、[精确配置](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/config.json)、[结构化结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/metrics.json)。
- 图表：[PNG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r1_r5_three_methods.png) · [PDF](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r1_r5_three_methods.pdf) · [SVG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/r1_r5_three_methods.svg)。
- `items.jsonl` / `evaluation.jsonl` / `units.jsonl` 是冻结 v3 的原样副本。运行器的 `screening_items.jsonl` 仅含 152 个补跑输入；`evaluation_labels.jsonl` 仅用于调度，不含金标。
- `code/run_m2.sh` 执行已有运行器，仅补跑 M2；`code/analyze_m2.py` 复用已有原生评分器离线重建本报告。`stages.jsonl.gz` 用 `source_run` + `artifact` / `prompt_ref` 定位原始阶段与 prompt。大缓存保留在本服务器，不随轻量结果压缩包重复打包。

#### 结果适用范围

这是本地全 Llama MedRGAG 复现配置。跨来源总通过率为项目汇总口径：诊断 canonical match、多选 exact-set、单选准确率及证据一致率按原任务分别评分。R4 仅 13 个 HIV ART 场景，金标为未经临床验证的作者预期答案；R5 仅 CPV-MedQA 患者属性变体。诊断不在冻结 canonical 标签表中时按既有规则计错，数量另列在分类与来源表。描述性百分点差不代表统计显著性。

<a id="record-0318"></a>

## supervision.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/supervision.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/supervision.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909`。

### Luna max 只读监督与独立复核

监督代理：`/root/m2_supervisor`，模型 `gpt-5.6-luna`，reasoning effort `max`。

监督结论：**通过，无实质发现**。本记录由主代理依据监督代理返回的终态复核结论保存。

- 运行时间 2026-09-09 16:54:30–16:58:21（Asia/Shanghai），231 秒；GPU 1/2，两工作进程退出码均为 0。
- 新增 1,976 个 LLM 阶段记录；加上检索、重排共 2,280 条阶段记录。阶段槽位无缺失、无重复，每次初始检索 5 篇文档。
- M2 4,872/4,872 个预测、6,030/6,030 条评分；复用 4,720 个输入与补跑 152 个输入无交集。
- 无新增 M0/M1 调用，未发现 failure、Traceback 或 OOM。
- 独立使用既有原生 `score()` 从 M2 `raw_response` 重算；统一 JSON tuple/array 表示后，6,030 条评分字段差异为 0。
- 当前 R1–R5 正确数为 711/6/76/7/766；总计 1,566/3,105 = 50.4348%。
- 152 条复用初始检索均通过与历史 M1 缓存的 query/document 一致性核查。

主代理另行完成全量阶段覆盖、采样参数与种子、1,976 条新增 prompt 引用、当前分类汇总、原 M0/M1 结果保持、图表与结果包检查。见 [阶段审计](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/artifact_audit.json) 和 [完整性检查](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m2_20260909/validation.json)。
