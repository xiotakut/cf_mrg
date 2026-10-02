# MA-RAG原生基线（M3）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。当前M3为Qwen3-8B的MA-RAG intrinsic，N=8/T=4；保留分歧驱动查询、检索、熵、历史、停止与投票。v5已完成13,905输入，其中复用3,690、新生成10,215。带CF sidecar的早期实验另归Adapter历史。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [Complete v3 R1–R5 M3 MA-RAG evaluation (2026-09-10)](#record-0012)
- [Active M3 v5 continuation (2026-09-11 23:38 Asia/Shanghai)](#record-0060)
- [M3 GPU0 parallel update (2026-09-12 12:53 Asia/Shanghai)](#record-0061)
- [M3 v5 completed (2026-09-12 23:48 Asia/Shanghai)](#record-0062)
- [3.4 M3 保留的完整 intrinsic 流程](#record-0096)
- [4.3 M3：输入准备与一次性检索服务加载](#record-0100)
- [4.4 M3：逐 token 熵计算向量化](#record-0101)
- [5.3 M3 事件时间线](#record-0106)
- [3.3 M3：原生任务接口、长上下文与运行终态](#record-0239)
- [README.md](#record-0319)
- [supervision.md](#record-0320)
- [README.md](#record-0389)
- [RESULTS.md](#record-0390)

<a id="record-0012"></a>

## Complete v3 R1–R5 M3 MA-RAG evaluation (2026-09-10)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第416行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Complete v3 R1–R5 M3 MA-RAG evaluation (2026-09-10)

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

<a id="record-0060"></a>

## Active M3 v5 continuation (2026-09-11 23:38 Asia/Shanghai)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2100行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### Active M3 v5 continuation (2026-09-11 23:38 Asia/Shanghai)

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

<a id="record-0061"></a>

## M3 GPU0 parallel update (2026-09-12 12:53 Asia/Shanghai)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2120行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M3 GPU0 parallel update (2026-09-12 12:53 Asia/Shanghai)

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

<a id="record-0062"></a>

## M3 v5 completed (2026-09-12 23:48 Asia/Shanghai)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2157行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M3 v5 completed (2026-09-12 23:48 Asia/Shanghai)

`results_v5_m3/RESULTS.md` is the final M3 v5 summary. Full 13,905 predictions
(3,690 reused + 10,215 new), 15,616 mapped scored records, 6,104 units; zero
missing or duplicate predictions. Unit-mean native accuracy R1 26.73%, R2 34.18%,
R3 8.59%, R4 38.46%, R5 73.37%, ALL 51.61%. Categories overlap.
Inference finished 23:43:45; scoring 23:43:58. All our model/retriever GPU
processes released, including retriever PID1627382 which required cleanup after
SIGTERM. GPU1/2/3 each show 4 MiB residual usage. GPU0 retains untouched dpc
PIDs1202819/1202820/1889151. No M3 tasks remain active; do not restart queues.

<a id="record-0096"></a>

## 3.4 M3 保留的完整 intrinsic 流程

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第107行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 3.4 M3 保留的完整 intrinsic 流程

依据[冻结配置](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/config.json)及[运行实现](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/run_m3.py)：

| 项目 | 本次 M3 |
|---|---|
| 上游代码 | MA-RAG，commit `423f031cc0ffca679a047c885be999b9604100a9` |
| 模型 / 精度 | 本地 Qwen3-8B / BF16 |
| solver | 8 候选；temperature 0.7；最多 2,048 token；thinking=false |
| query | temperature 0；最多 8,192 token；thinking=true |
| 轮次 | 最多 4 轮，解析答案一致时提前停止 |
| 不确定性 | top-20 logprobs 对应的 token 熵；历史按平均熵降序排列 |
| 查询与检索 | 分歧生成 1–4 查询；各查询 BM25 total_k=32、MedCPT top_k=2；文档按 ID 去重 |
| 语料 | MedCorp3：PubMed、Textbooks、Wikipedia；不同于 M4/M5 四库 |
| 答案决策 | 最终候选唯一最高票；最高票平局无效 |
| 诊断归一化 | 大小写、空白和标点，不使用金标或同义词表消歧 |
| 上下文 | 131,072；YaRN factor=4、original=32,768；每阶段检查完整输入预算 |
| 服务 | server seed=223；max-num-seqs=32；prefix caching；客户端 PYTHONHASHSEED=223 |

没有减少候选数、轮次、query 预算或历史来提速，没有换成 extrinsic verifier，也没有增加训练、适配器或裁判。提前停止保留已有解析规则，包括候选均解析为无效答案的情况，未在运行中改写以抬高分数。

M3 对 v5 `robustness_single` 新增必要的任务 I/O 适配：要求指出 D 编号错误文档及纠正文本；保留 `<answer>选项</answer>` 做原有答案投票，并要求后附 `errors` JSON。文档纠正取最终获胜答案的**第一个候选**，不对纠正做额外投票、也不根据金标补写。原始候选保存在 gzip 阶段缓存中；评分序列化的 `raw_response` 不是模型直接输出的全部文本。该适配应披露为 benchmark 格式适配，不能描述成所有任务提示均与上游逐字相同。

<a id="record-0100"></a>

## 4.3 M3：输入准备与一次性检索服务加载

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第159行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 4.3 M3：输入准备与一次性检索服务加载

M3 的 `cache=True` 检索服务一次性加载约 57 GiB 的 `id2text.json`，运行观察约 8 分钟启动、展开后约 96 GiB RAM；之后命中文本是字典查找。启动慢与每题提示准备慢是两类成本。没有把正在运行的检索服务替换成偏移读取实现，也未修改其 0.5 秒批处理等待或重排方式。

在新生成阶段写入 `.timing.json`，拆分 preparation、API request、response processing、cache write；检索 JSON 记录其服务往返时间。API request 包括模型生成、传输及客户端处理开销，不是纯 GPU kernel 时间。早期记录的准备步骤约 5–14 ms（tokenizer 首次加载后）、响应处理约 0.33–1.33 秒、缓存写入约 1–48 ms、检索约 2.30–3.97 秒，见[性能调查记录](/home/data3/txy/docs/baselines/marag.md#record-0100)。

原性能笔记（2026-09-11）补充：当时已有prefix caching、八客户端分片、冲突查询并行检索和全票一致提前终止；八分片工作时GPU利用率曾达到100%/90%，生成仍是主要成本。`.timing.json` 的缓存写入包括gzip输出，检索往返包括服务合批等待。最初仅完成合成微测，随后通过真实响应验证，实际启用时间见下一节；未采用的offset loader只作为降低启动/RAM成本的候选。

<a id="record-0101"></a>

## 4.4 M3：逐 token 熵计算向量化

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第167行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 4.4 M3：逐 token 熵计算向量化

上游对每个输出 token 单独调用 SciPy entropy；本地改为对 top-logprob 矩阵执行 `entropy(np.exp(top), axis=1)`，对非规则长度输入保留兼容的逐行路径。代码：[response_processing.py](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/response_processing.py)。

| 测试 | 原实现 | 向量化 | 等价性 |
|---|---:|---:|---|
| 合成 8,192×20 矩阵 | 1.212420 秒 | 0.007853 秒 | 本样本 bit-exact，最大差 0 |
| 8 个非 thinking 候选，共 674 token | 0.110958 秒 | 0.005029 秒 | 全部解析字段完全一致 |
| 1 个 thinking 响应，共 256 token | 0.070735 秒 | 0.002451 秒 | 全部解析字段完全一致 |

证据：[微基准](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/entropy_microbenchmark.json)、[真实响应等价验证](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/response_processing_validation.json)、[可运行验证脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/code/check_response_processing.py)。验证用的附加请求不是正式题目预测。

**实际生效范围**：修改 import 时，8 个初始 worker 已加载旧函数，所以没有立即生效。9 月 12 日 12:53 重启的分片 0/3/4 首先使用优化版；17:59 迁到 GPU3 的 1/2/5 使用优化版；20:55 迁移的 6 使用优化版；未重启的分片 7 一直保留旧函数。各分片已有阶段继续复用，因此本次记录混合了两种处理实现，不能宣称全部 10,215 个新输入都使用了优化版。两种实现的测试支持处理字段等价，但没有进行全体原始响应的双实现逐项比对。

本优化不修改提示或采样。它减少的是 CPU 响应处理开销；没有严格端到端加速实验，不能把微基准倍数当作 M3 整体加速比。

<a id="record-0106"></a>

## 5.3 M3 事件时间线

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第205行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 5.3 M3 事件时间线

以下为 JSON 事件时间，部分历史 README 标题写的是开始操作的分钟，可能早于实际交接完成时间。

| 时间（2026-09-12，除首行） | 操作 / 实际安排 |
|---|---|
| 09-11 23:30:33 | 控制器启动时间记录；随后完成正式清单内的冒烟并启动 8 分片，GPU1/2 各 4 客户端 |
| 12:53:01 | GPU0 服务健康后迁入分片 0/3/4；GPU1=2/6，GPU2=1/5/7 |
| 13:00:15 | GPU0 扩容交接完成：份额 .875，空闲退出阈值 10 GiB |
| 15:30:56 | GPU0 再扩容：份额 .9378，退出阈值 4 GiB |
| 17:59:03 | GPU3 原占用自然退出后，分片 1/2/5 迁到 GPU3；GPU1=6，GPU2=7 |
| 19:13:39 | GPU0 检测新 dpc 进程，自动释放我们的模型；0/4 回到 GPU1，3 回到 GPU2 |
| 20:55:33 | 分片 3/7 完成后，分片 6 从 GPU1 迁到现有 GPU2 服务；GPU1=0/4，GPU3=2/5 |
| 22:32:39 | GPU2 分片全部完成，只释放我们闲置的 8012 模型服务 |
| 23:07:18 | GPU3 分片全部完成，只释放我们闲置的 8013 模型服务 |
| 23:43:45–23:43:58 | 全部推理完成；全 ID 审计、合并与评分完成 |
| 23:48:04 | 检索服务收到 SIGTERM 后仍残留，核对归属后仅终止本次检索 PID，释放最后显存 |

事件依据：[GPU0 事件流](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_parallel_events.jsonl)、[首次交接](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_handoff.json)、[75 GiB 交接](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_memory_upgrade.json)、[再次扩容](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu0_memory_upgrade_81gib.json)、[GPU3 交接](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu3_handoff.json)、[分片 6 交接](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu2_shard6_handoff.json)、[GPU2 释放](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu2_released.json)、[GPU3 释放](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/gpu3_released.json)、[检索服务清理](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/retriever_cleanup.json)。

<a id="record-0239"></a>

## 3.3 M3：原生任务接口、长上下文与运行终态

来源：[R1_R5_V3_BASELINES_WORK_RECORD.md](/home/data3/txy/R1_R5_V3_BASELINES_WORK_RECORD.md)，原文第69行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 3.3 M3：原生任务接口、长上下文与运行终态

| 原入口 / 原状态 | 本次实际调整 | 保留的边界与证据 |
|---|---|---|
| 上游入口主要面向大写单选答案 | 在本次运行接口支持真实选项键、多选、yes/no、开放诊断及证据关系答案 | 保留原生题型和评分；不是统一改造为新的选择题任务 |
| 本地方法有原有迭代、熵、历史及投票逻辑 | 沿用 N=8/T=4、top-20 token entropy、分歧驱动查询、全体同答停止及唯一最高票规则 | 不添加项目 CF 变体、adapter、训练或额外 judge；已有 checkout 及 MedCorp3 接口补丁来源见运行记录 |
| 一些 v3 原题有长固定证据，随后还要加多轮历史 | 固定证据每轮完整传入；使用 Qwen YaRN factor 4，将上下文上限设为 131,072，检查实际 prompt 与输出预算 | 未截断固定证据；此项是本地长上下文适配，须在实现细节披露 |
| 开放诊断字符串需要投票和原生评分衔接 | 投票只规范化大小写、空白/标点；最终最高票答案序列化后交原生评分器 | 未向推理加入医学同义词映射、canonical 标签或 gold；原始 LLM 响应在逐轮缓存 |
| thinking 结束标记缺失可能导致原路径无休止重试 | 保存原响应并标为 `runtime_invalid`，按冻结规则保留空答案计错 | 不生成替代答案；与网络/后端执行故障分开 |
| 最高票并列或输出无效 | 保留 `vote_tie` / `invalid_answer` / `runtime_invalid` 终态和原始记录 | 不用 gold 打破平票，不删掉失败题分母 |
| 对话出现中断 | 查看后台完成标记及分片结果，确认工作已结束 | 本次没有因为会话中断重复启动完整实验 |

M3 的 4,872 条结果均来自本轮新推理，含先行试跑。运行产生 82,880 个 solver 候选、5,493 个 query 输出；输入终态为 4,812 complete、51 vote_tie、4 invalid_answer、5 runtime_invalid。全部 6,030 条评分映射保留，覆盖无缺失或重复。

这些属于运行接口和执行行为的实际记录，不是对后续分类会话的推荐配置。M3 与 M0–M2 的骨干、语料和调用预算不同；方法间差值不能全部归因于算法本身。

<a id="record-0319"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909`。

### R1–R5 v3：M3 MA-RAG 完整测试

M3 覆盖全部 4,872 个独立输入、6,030 条评分映射及 3,105 个互斥单元。M0/M1/M2 原始结果保留，统一使用 v3 当前 labels 和既有原生评分规则。

| 分类 | 单元数 | M0 | M1 | M2 | M3 | M3−M2 |
|---|---:|---:|---:|---:|---:|---:|
| R1 新增支持 | 1,601 | 45.22% | 41.29% | 44.41% | 43.85%（702） | -0.56 pp |
| R2 撤销支持 | 77 | 9.09% | 9.09% | 7.79% | 32.47%（25） | +24.68 pp |
| R3 重新比较 | 324 | 18.83% | 28.40% | 23.46% | 14.20%（46） | -9.26 pp |
| R4 推导后果 | 13 | 38.46% | 38.46% | 53.85% | 38.46%（5） | -15.38 pp |
| R5 保持判断 | 1,090 | 66.51% | 69.82% | 70.28% | 79.82%（870） | +9.54 pp |
| ALL 合计 | 3,105 | 49.02% | 49.15% | 50.43% | 53.08%（1,648） | +2.64 pp |

全量阶段：2026-09-09 17:32:33 至 2026-09-10 08:43:00（Asia/Shanghai），墙钟 15.17 小时；此阶段复用 6 个先前试跑结果，时长不含服务准备及试跑。

R5 配对指标（1,090 对，672 个原始病例）：

| 方法 | R5 答案保持率 | R5 两次均答对 |
|---|---:|---:|
| M0 | 97.16%（1059/1,090） | 65.96%（719/1,090） |
| M1 | 91.83%（1001/1,090） | 66.42%（724/1,090） |
| M2 | 78.81%（859/1,090） | 62.02%（676/1,090） |
| M3 | 90.28%（984/1,090） | 75.69%（825/1,090） |

输入结束状态：4,812 个 complete、51 个 vote_tie、4 个 invalid_answer、5 个 runtime_invalid。后三类保留空答案并计错。原生评分还会将未映射诊断标签计为无效，因此评分表的 invalid 与这些运行状态不是同一计数。

实际生成 82,880 个 solver 候选及 5,493 个 query 输出；逻辑 prompt / completion token 为 432,965,800 / 43,100,841。



![四方法对比图](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r1_r5_four_methods.png)

#### M3 方法与运行

M3 是本地 MA-RAG intrinsic，Qwen3-8B BF16、每轮 8 个候选、最多 4 轮；solver temperature=.7、max_tokens=2048、关闭 thinking；query temperature=0、max_tokens=8192、启用 thinking。保留原 top-20 token entropy、原历史答案排序、基于分歧的查询生成、MedCorp3 BM25/MedCPT 检索、全体同答提前停止及最终唯一最高票规则。最高票并列或最高票答案无效均计错，不用金标打破平票。

没有调用 Profile、CFShift、CFMoE、CF-KADS、WM、MA-RAG native CF 变体、残差融合、训练或额外裁判。本次沿用本地已有的日志记录和 MedCorp3 语料接口补丁，未再修改 MA-RAG checkout。

原入口只支持大写单选，因此本次仅作必要任务接口适配：保留真实选项键，支持多选、yes/no、开放诊断及证据关系答案；固定证据在每轮完整传入。诊断投票仅规范化大小写和空白/标点，不加入医学同义词或 canonical 标签；金标仅在离线评分阶段加载。每个最终 raw_response 字段是最高票答案供原生评分器读取的 JSON 序列化；真实 LLM 输出在 cache/items 的逐轮记录中。

为容纳最长约 6.96 万 token 原题及多轮历史，统一使用 Qwen 官方 YaRN factor=4、original_max_position_embeddings=32768、max_model_len=131072；每次实际 solver/query prompt 加输出预算均检查，未截断固定证据。原上游缺少 thinking 结束标记时可能无限重试；本次保存原输出并计为 runtime-invalid，不替换答案。网络/后端故障保留阶段并停止对应 worker，由主代理处理。

#### 数据与结果文件

- [分类成绩](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/category_scores.csv)、[来源原生指标](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/source_scores.csv)、[逐单元评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/unit_scores.csv)。
- [M3 预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/m3_predictions.jsonl)、[M3 评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/m3_scored.jsonl)、[四方法预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/predictions.jsonl)、[四方法评分](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/scored.jsonl)。
- [R4 逐题结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r4_item_scores.csv)、[R5 配对汇总](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r5_pair_summary.csv)、[R5 逐对结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r5_pair_scores.csv)。
- [冻结计划](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/plan.json)、[配置](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/config.json)、[阶段审计](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/artifact_audit.json)、[完整性检查](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/validation.json)、[结构化结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/metrics.json)。
- 图表：[PNG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r1_r5_four_methods.png) · [PDF](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r1_r5_four_methods.pdf) · [SVG](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/r1_r5_four_methods.svg)。
- 原始输入/映射/单元分别在 items.jsonl、evaluation.jsonl、units.jsonl。code/run_full.sh 是运行入口，code/analyze_m3.py 离线重算投票及评分。阶段记录及完整候选输出保留本服务器 cache/items；结果压缩包不重复打包大缓存。

#### 解释边界

M3 与 M0/M1/M2 的模型骨干、检索库和调用预算不同，分数差不能单独归因于 MA-RAG 算法。这里沿用已有本地 N8/T4、MedCorp3 设置，并进行原生题型和长上下文扩展，不是原论文表格配置复现；静态 YaRN 也可能影响短输入。每个非参照单元等权，无效输出按原任务规则计错。R4 仅 13 个未经临床验证的作者预期答案场景；R5 仅 CPV-MedQA，准确率和配对答案一致率分开报告。百分点差为描述性比较。

M2 本次复用了 4,720 条历史预测；M3 的 4,872 条预测均来自本轮新推理，包含先行试跑。两次运行墙钟对应的新增工作量不同。

<a id="record-0320"></a>

## supervision.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/supervision.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909/supervision.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909`。

### M3 supervision record

The user requested a Luna max subagent for supervision, with periodic checks
by the primary agent. The same `m2_supervisor` agent supervised this M3 run
using `gpt-5.6-luna` with reasoning effort `max`.

#### Before the full run

Luna independently reviewed the upstream intrinsic MA-RAG loop, native task
interface adaptations, preserved fixed evidence, decoding settings and six
completed smoke inputs. The review passed. The full run started on
2026-09-09 at 17:32:33 Asia/Shanghai.

#### Long-input concurrency check

Four formal inputs (`s025188`, `s025185`, `s025187`, `s025186`) were evaluated
early on endpoint 8012 using the same frozen method and saved for full-run
reuse. All completed by 17:48:21, using respectively 2, 2, 2 and 3 rounds.
Maximum actual stage prompts were 75,851 / 79,068 / 77,153 / 77,925 tokens.

Luna independently checked complete stage records, eight responses per solver
round, entropy values and context capacity. No non-200 request, preemption,
OOM, timeout, abort or traceback was found. The primary agent also read the
four final records and both services' preemption/abort counters, which were 0.

In about seven minutes of ordinary work after the long-input check, Luna
observed average running sequence counts of 14.8 / 12.3, no queued sequences,
and GPU utilization of about 93–100%. The existing four clients per endpoint
were retained. Candidate count N=8 and round limit T=4 remain unchanged.

#### Full-run supervision

Luna performed periodic read-only checks of shard progress, stage/HTTP activity,
worker exits and the Qwen/retriever services while the primary agent checked
the accumulating final records. Its last pre-interruption snapshot, at
2026-09-10 07:25:04 Asia/Shanghai, recorded 4,813/4,872 outputs, five normally
completed shards, three active shards and no transport/backend failure.
Long stages were assessed using actual stage/HTTP activity, not a fixed
five-minute per-input timeout. No inference settings changed during the run.

At 18:36:16, Luna checked the first invalid final vote, `s013991`, without
consulting gold. The final eight raw answer tags were `X, X, X, X, A, X, X, A`
for an A–D single-choice input. The native parser correctly produced six invalid
sentinels and two A votes. The invalid sentinel therefore won; the saved null
answer is retained and scores as incorrect. No prompt change or rerun was made.

Luna also checked the first final tie, `s001066`: the final raw multi-select
candidates split four votes for B,D and four for D. The null answer correctly
preserves the upstream rule for tied highest counts.

At 22:07:44, Luna checked the first `runtime_invalid`, `s006631`. Its query
ended with `finish_reason=length` after all 8,192 output tokens, without a
closing thinking tag. The original query output, log probabilities, entropy
values and preceding eight solver candidates were preserved. The frozen
error policy records a null answer before retrieval; no answer substitution,
extra generation or prompt change was made. All eight full-run workers
continued, with no transport/backend failure recorded at that snapshot.

#### Completion and recovery check

The conversation interruption did not interrupt the background tmux run.
At the user's recovery request, the primary agent checked status at
2026-09-10 09:38:28 Asia/Shanghai. All 4,872 inputs had final records, all
eight shards had completed 609 inputs and exited 0, and `run_exit.json`
recorded exit 0. Inference finished at **08:43:00**; automatic native scoring
and raw-candidate auditing passed, with report generation finished at
**08:44:22**. Full-run wall time was 54,627 seconds (15.17 hours), excluding
service preparation and the preceding six-input smoke run.

There are 4,812 complete outputs, 51 highest-vote ties, four invalid final
answers and five runtime-invalid query outputs. All 60 null outputs remain
in the results and count as incorrect. The audit recomputed votes from every
raw candidate pool, confirmed N=8 and T<=4, checked actual stage context
capacity, and confirmed preservation of the original MA-RAG source snapshots.
It recorded 82,880 solver candidates and 5,493 query generations, with no
additional-module or judge calls.

The primary agent confirmed that all three tracked service parents had exited;
the run's tmux server was also gone. No recovery inference or regeneration was
needed. The four-method plot was visually inspected, and the updated workspace
guide's read-only loading example ran successfully against the final files:
3,105 exclusive units, 4,872 inputs, 19,488 method predictions and 24,120 scores.

#### Final independent acceptance — passed, 2026-09-10

Luna max independently recomputed all **6,030 M3 evaluation records** from
the saved raw responses with the existing native scorer. There were **zero
field differences** from `m3_scored.jsonl`. Correct counts for R1–R5 were
**702 / 25 / 46 / 5 / 870**, giving **1,648/3,105 (53.075684%)** overall;
these match `category_scores.csv`. Native invalid unit scores total 714,
including 602 unmapped diagnosis labels.

Independent R5 pairing reproduced all 1,090 pairs and 672 roots: reference
correct 854, variant correct 870, unchanged 984, both correct 825,
correct-to-wrong 29 and wrong-to-correct 45. Both the pair rows and M3 summary
had zero differences. Previous M0–M2 scored records were fully preserved.

The candidate review confirmed eight responses per round, final vote counts,
statuses, answers and serialized outputs against the exports. All five
runtime-invalid final query outputs had `finish_reason=length`, 8,192 output
tokens and no closing thinking tag; they remain incorrect under the frozen
policy. The 24,120 combined score rows have no missing or duplicate records.
The PNG/PDF/SVG data agree with the independent aggregates; the primary agent
also inspected the rendered PNG.

All eight workers completed 609 inputs and exited 0. Luna confirmed that no
M3 worker, Qwen 8011/8012 service or retriever process/listener remained.
Other tasks' services were left untouched. No substantive issue was found,
and no inference was rerun during recovery or acceptance. The primary agent
accepted the outputs and refreshed the result archive with this final record.

<a id="record-0389"></a>

## README.md

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/README.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3`。

### M3 v5 continuation

Continues the existing MA-RAG intrinsic Qwen3-8B baseline: N=8, T=4,
MedCorp3 BM25 + MedCPT, solver temperature 0.7 / 2048 tokens / thinking off,
query temperature 0 / 8192 tokens / thinking on, top-20 entropy history.

13,905 total inputs; 3,690 exact-input results reused from the completed v3 M3
run; 10,215 pending inputs. Completed invalid/vote-tie answers are retained.
Eight disjoint client shards alternate between GPUs 1 and 2, four per service.
Each service supports 32 sequences and reserves 75% GPU memory. GPU 1 also
hosts the existing MedCorp3 retrieval service. Other users' GPU 0/3 processes
are not touched. Recheck GPU availability during supervision.

`plan.json` freezes all shard memberships. `cache/reused.jsonl` records original
source IDs and paths. `cache/items/` preserves each new stage and native outputs.
For v5 robustness inputs, prompts request D-numbered factual-error corrections;
answer voting remains unchanged, with errors preserved from the first final
candidate carrying the winning answer. No gold labels enter inference.

`code/run_all.sh` waits for services, validates smoke and longest inputs, runs
all shards, then executes coverage audit and native v5 scoring. Smoke outputs
are reused. `code/finish.py` releases only this run's verified service PIDs.
Services and controller run in tmux socket `v5-m3`.

Generation stage timings separate input preparation, API request (generation
plus transport), response processing, and cache writes. Retrieval stages record
wall time. These support performance analysis without changing prompts or
sampling. Existing prefix caching and parallel query retrieval are retained.

##### GPU0 protected parallel continuation — 2026-09-12 12:53

User authorized borrowing GPU0 while dpc remains paused, using the previous
M4 automatic yield rules. `code/parallel_gpu0.py` imports that existing guard:
check every 2 seconds; yield on resumed incumbent, another GPU process, or less
than 25 GiB free. Only our new service process group is terminated on yield;
its three clients resume from their saved stages on GPU1/2. No signal is sent
to dpc's processes.

GPU0 serves the same Qwen model and frozen generation settings at port 8010,
with 0.60 GPU memory allocation. Original shards 0, 3, 4 were handed to this
endpoint; the other five workers, GPU1/2 model services, and retriever continued.
The original eight disjoint ID lists are unchanged. Three original client
processes were terminated only after GPU0 health passed; completed results and
stage caches are reused, while an unsaved in-flight stage may be regenerated.
The resumed clients now also load the previously validated vectorized entropy
parser; the other five still use their already-loaded original parser.

`tmux -L v5-m3` session `gpu0-parallel` runs the new coordinator. It takes over
finalization because the original controller records the intentional client
exits as nonzero. It checks full pending-ID coverage before invoking the same
`finish.py` audit/scorer and releasing our services. See `gpu0_handoff.json`,
`gpu0_parallel_events.jsonl`, `gpu0_parallel_status.json`, and
`run_{0,3,4}_gpu0_resume.log`. No benchmark inputs or method settings changed.

###### GPU0 memory update — 2026-09-12 12:59

User explicitly requested approximately 75 GiB for our GPU0 model and authorized
lowering its free-memory yield threshold to **10 GiB**. Incumbent-resume and
new-external-process checks remain unchanged. This supersedes the 0.60 / 25 GiB
settings above. GPU0 uses memory fraction 0.875: this installed vLLM counts the
incumbent allocation during profiling, so 0.75 would not give our process 75 GiB.
Only GPU0's own service and three clients were restarted, via
`parallel_gpu0.sh --resume`; GPU1/2 and the other five clients continued.
`gpu0_guard_validation.json` verifies the changed threshold while the shared
M4 guard's default remains 25 GiB. `gpu0_memory_upgrade.json` records coverage
at the second handoff. Five-minute updates now include all four GPUs, cumulative
M3 progress, remaining inputs, and newly completed inputs since the last report.

###### GPU0 additional 6 GiB — 2026-09-12 15:29

User explicitly approved lowering free-memory yield to **4 GiB** and adding
approximately 6 GiB to our GPU0 process. Allocation fraction is now 0.9378,
targeting about 81 GiB for our model while retaining the dpc-resume and
new-external-process yield triggers. Only our GPU0 coordinator, service, and
three clients were restarted; all other workers/services continued. Exact
original shard IDs and existing caches are reused. See
`gpu0_guard_validation_4gib.json`, `gpu0_pre_upgrade_81gib_status.json`, and
`gpu0_memory_upgrade_81gib.json`. This supersedes the previous 10 GiB threshold.

##### GPU3 joins — 2026-09-12 17:59

GPU3's other-user vLLM exited. Following the user's standing instruction to use
available GPUs in parallel, `code/parallel_gpu3.py` launched the same frozen
Qwen server on 8013 (memory fraction .75), then handed original shards 1/2/5
to it after health passed. Only these three original clients restarted; all
model services and other shards continued. Exact original eight shard lists
remain unchanged. Current placement: GPU0=0/3/4, GPU1=6, GPU2=7, GPU3=1/2/5.
The resumed GPU3 clients load the validated vectorized entropy parser; only
original shards 6/7 still have the older parser in memory.

Tmux socket `v5-m3`, session `gpu3-parallel`; see `gpu3_handoff.json` and
`run_{1,2,5}_gpu3_resume.log`. GPU0 coordinator still owns final coverage audit
and scoring. `finish.py` now also releases only our verified port-8013 service.
GPU1/2 also host another workspace's iMedRAG dev task; do not signal it.

##### GPU0 guard yielded — 2026-09-12 19:13–19:18

The guard detected dpc's new active GPU0 PID 1889151 and automatically stopped
only our GPU0 model group. Shards 0/4 resumed on 8011, shard 3 on 8012, with
saved stages retained. No dpc processes were signalled. Current placement:
GPU1=0/4/6, GPU2=3/7, GPU3=1/2/5. GPU0 coordinator remains alive in `fallback`
state and still owns finalization. Do not restart its original handoff script
or reclaim GPU0 while the external job exists. Events and new worker PIDs are
in `gpu0_parallel_status.json` and `gpu0_parallel_events.jsonl`.

##### Remaining-tail balance — 2026-09-12 20:55

Shards 1/3/7 completed. The original shard6 client was handed from GPU1 to the
already-running GPU2 endpoint8012, reusing its saved stages and exact ID list.
Only that client restarted; all model services and other active shards continued.
Tmux session `shard6-gpu2`, script `code/resume_6_gpu2.sh`, record
`gpu2_shard6_handoff.json`. Active placement: GPU1=0/4, GPU2=6, GPU3=2/5.
GPU0 coordinator in fallback mode still owns full-coverage finalization.
All original controller clients have now exited; its intentional nonzero exit
is expected and is not the active completion controller.

##### Completed — 2026-09-12 23:48

See [RESULTS.md](/home/data3/txy/docs/baselines/marag.md#record-0390). All 13,905 predictions and 15,616 scoring records validated, zero missing/duplicates. All our model and retriever GPU allocations released. No M3 work remains running.

#### 实施与复现总记录（2026-09-13）

[五方法评测实施、调整与复现记录](/home/data3/txy/docs/evaluation/v5.md#record-0084)汇总实际配置变更、工程加速验证、资源调度时间线、最终结果及论文表述边界；历史日志中的中间状态以该记录及最终审计为准。

<a id="record-0390"></a>

## RESULTS.md

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/RESULTS.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3`。

### M3 v5 final results

[最新M0/M2/M3/新M4/M5 v5完整对照](/home/data3/txy/docs/evaluation/v5.md#record-0410)（2026-09-13）。

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

Artifacts: [CSV](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/category_scores.csv), [plot](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/v5_selected_methods.png), [coverage audit](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/artifact_audit.json), [scoring validation](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/validation.json), [all predictions](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/m3_predictions.jsonl), [performance notes](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/performance_notes.md).

GPU0 automatic yield triggered when dpc PID1889151 appeared; our shards resumed on GPU1/2 from saved stages. All our model and retriever GPU processes are now released. GPU1/2/3 each show only 4 MiB residual usage. GPU0 retains dpc processes, untouched.

The validated vectorized entropy parser changed only response processing; frozen model prompts, decoding and intrinsic MA-RAG method settings remained unchanged. Client handoffs preserve saved results/stages; unsaved in-flight stages may be regenerated. See README for runtime history.
