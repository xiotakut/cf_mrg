# V5 R1–R5：M0 / M2 / M4 / M5 完整评测运行

**最新五方法总表（2026-09-13，新M4全量修复版）：[M0/M2/M3/新M4/M5 v5 benchmark](<../../completion/v5_benchmark_latest/README.md>)。本页原M4数值及图表保留为历史版本；当前比较请使用新总表。**

2026-09-11 启动，四方法完整评测及审计已完成。结果见 [RESULTS.md](<RESULTS.md>)。冻结数据来源为 `benchmark_r1_r5_v5_20260910`，使用 `evaluation_labels`；保留 v3/v4/v5 原件及既有模型结果。

| 范围 | 数量 |
|---|---:|
| 比较单元 | 6,104 |
| 选中具体判断 | 13,000 |
| 去重独立输入（含参考端） | 13,905 |
| 每方法原生评分映射 | 15,616 |
| 最终四方法预测目标 | 55,620 |

| 方法 | 已有预测复用 | 新增完整方法运行 |
|---|---:|---:|
| M0 Direct Llama-3.1-8B | 8,877 | 5,028 |
| M2 本地全 Llama MedRGAG | 6,687 | 7,218 |
| M4 MedRAG-Llama-3.1-8B | 0 | 13,905 |
| M5 MedRAG-Qwen3-8B | 0 | 13,905 |

M2 每个新输入有 5 次摘要、1 次探索、5 次候选生成、1 次选择、1 次最终回答，共 93,834 次新阶段调用和 36,090 个生成候选。没有额外消融、训练或模型裁判。冒烟样本来自正式输入，完成后直接复用。

## 数据与方法协议

- 原题、原生选项/金标、完整给定证据和评分接口保持。M14 按已审阅的原题精确匹配恢复原生选项；M17 逐项加载独立合格的 VISIT/MANAGE/RESOURCE，不继承父单元资格。
- 输入仅包含 `item_id/question/options/fixed_evidence/answer_format/max_tokens`。分类理由、金标、目标判断和评分映射均不进入模型。
- 旧预测复用核对实际可见字段、选项顺序、原生输出预算，并保留旧 item_id、解码 seed 与来源路径。`cache/reused.jsonl` 与两个 `pending_*.jsonl` 互斥。
- M0/M2 使用原本的提示、Llama BF16 和解码设置。M2 保留完整 KGCC/KADS、五候选及最终 reranking；给定证据始终可见，不受生成文档选择影响。新增 MedRGB 最终回答使用原有 robustness JSON 协议和 2,048 token 预算，其余最终回答为 64 token。
- M4：按用户 2026-09-11 最新指令，与 M5 使用同一 MedCorp/BM25/MedCPT 单轮设置，仅回答模型为 Llama-3.1-8B。四库每库 top-32，重排 top-8，temperature 0.7；不再依赖 RRF 稠密索引。当前配置在 `configs/m4.json`、`configs/m5.json`；旧配置记录在 `m4_configuration_change.json`。
- M5：完整 MedCorp 四语料，每库 BM25 top-32，MedCPT 重排 top-8，temperature 0.7，Qwen 非 thinking。
- M4/M5 保留上游单轮、question-only 检索及 CoT/JSON 模板；原生任务扩展允许多选集合、开放诊断、关系标签和 robustness 错误文档列表。最终字段为 `answer_choice`，只做明确字段映射后使用同一原生评分器，不修复格式错误。
- M4/M5 使用本机已有 vLLM 0.8.5 批量推理，BF16，seed 42，top_p 1，输出上限 2,048。既有安装冒烟使用 Transformers；不同引擎不保证逐 token 相同。依赖复用 MedRAG 的 Transformers 4.51.3 环境，不修改上游安装文件。
- M5 完整必需证据超过 32K（Qwen 最长原生输入 69,721 token）。沿用本地 M3 的 YaRN factor 4 / original context 32,768，最大上下文 131,072。M4 最大上下文 131,072；M0/M2 为 98,304。M4/M5 追加检索片段均最多 30,000 个各自模型 token，必需证据不裁剪；完整阶段溢出时报错。

## MedRGB

沿用已存在的本地六档污染比例协议：p_sig=100/80/60/40/20/0，每个单元 6 个输入，100 为参考，其他为变体；已有具体材料化输入精确复用。新单元沿用原构建器的固定种子和冻结单元次序。各比例独立抽取信号与污染文档，不能把信号数组位置当作 DOC_n 的原件配对。

R5 目标绑定原主问；文档级选中判断仅映射到实际含该文档的变体比例，参考映射到该单元全部选中判断。28 个单元共 77 个材料化上下文含原始空文档槽位；保留原始输入，缺失文档不进入检测评分。见 `medrgb_mapping_note.json`。原主问均有原生选项/答案可评分；文档纠正文本保留，不用模型临时判定其语义正确性。

## 评分

主表按比较单元等权：先平均该类别下单元的非参考原生任务正确性，再对单元取均值。另报全部任务通过率、来源等权均值、逐来源/任务结果、R5 答案一致性及两端同时正确。各类别可重叠，ALL 对 6,104 单元只计一次。分类判断用于确定评测成员与类别；原生准确率不等同于对分类理由逐条进行语义验证。

诊断沿用已有归一化精确匹配；无效输出算错，不用金标消除歧义或改答案。R4 仍为 13 个作者预期答案的一致率。`--partial` 结果只用于运行状态，不作为最终比较；完整评分命令强制所有预测和类别分母齐备。

## 运行与文件入口

GPU0 为 dpc 任务，GPU3 为 wwj 服务；未使用或终止。GPU1/2 与用户自己的索引准备任务共用，M0/M4/M5 reader 初始显存份额 0.55；M2 经启动实测改为 0.75、batch64，KV 容量 290,208 token。若其他卡自然空闲可重新调度。

- tmux socket `v5-benchmark`，队列 `m0-m5` 与 `m2-m4`。
- `code/run_m0_then_m5.sh`：GPU2 M0 → M5。
- `code/run_m2_then_m4.sh`：GPU1 M2 → M4（不等待 RRF 索引）。
- `M*/progress.json`、`*_full.log`：当前吞吐和阶段进度。
- `plan.json`：初始复用和新增规模；`preflight.json`：完整原生输入长度。
- `preparation_validation.json`：全部判断、映射、输入去重及复用分离检查。
- `code/check_v5.py`：可重复的数据与评分接口检查。
- `code/analyze_v5.py`：原生评分和总表；默认要求完整，`--partial` 仅作进度快照。
- `cache/reused.jsonl`、`M*/predictions.jsonl`、`M*/prompts.jsonl.gz`：复用来源、新输出与原始提示。
- `m2_runtime/cache/main/worker-0`：M2 全部阶段、检索和选择缓存。

Luna max 子代理承担只读运行监督，主代理定期检查和处理故障。子代理 API 没有独立 fast 开关，当前可用服务档位为 priority。

旧 RRF Textbooks 检查文件仅为历史安装验证，不是当前 M4 的验证。本评测不依赖旧 RRF 稠密索引。MedCPT 构建已完成；Contriever、SPECTER 及其启动脚本已停止，避免继续占用资源。已有生成索引文件尚未删除。

运行时已补齐 PubMed 的 1,166 个分片行偏移文件（约 182 MiB），复用现有 `CorpusDocumentResolver` 生成器与 MedRAG 的按偏移读取路径，避免每条命中都读取整个 JSONL 分片。M5 无需重启即可使用；同一问题的 32 条正文前后完全一致，验证见 `pubmed_offset_validation.json`。检索策略、文档内容、顺序及评分协议不变。

M4/M5 shared retrieval acceleration verified: both use code/run_medrag.py and the same MedRAG corpus directory, including all 1166 PubMed line-offset files. M4 automatically inherits the validated document-read acceleration at startup. Retrieval and generation settings match; full-run batch size 16 and GPU memory fraction 0.55 match. Model-specific tokenizer/chat-template and Qwen context-extension settings remain model-specific. No evaluation process restarted.

M4 moved to shared GPU 0 by user authorization. Guard code/run_m4_gpu0_guard.py checks every 2 seconds and terminates only its own M4 process group if an incumbent resumes, another GPU process appears, or free VRAM drops below 25 GiB. vLLM fraction 0.50 (0.45 could not fit 131072-token KV cache); generation settings unchanged. Six smoke inputs completed and validated; full run started. run_medrag.py serializes M4 with flock and skips completed smoke/full runs, so the original GPU 1 queue remains a fallback without duplicate inference. M2/M5 and other users processes remain untouched. Logs: m4_gpu0_smoke.log, m4_gpu0_full.log, m4_gpu0_guard.log. Root monitoring remains every five minutes.

M4 parallel continuation authorized by user, with no omitted items. Stopped the old GPU 0 runner only after batch 5824 committed; 5830 results including six smoke retained and prompt coverage verified. Remaining 8075 inputs split by whole 16-item batches into disjoint worker-0 (4043) and worker-1 (4032) manifests under M4/parallel/. Worker 0 uses GPU 0 with the existing 2-second external-process/memory guard; worker 1 uses free GPU 1. Both retain batch 16, vLLM memory fraction .50, model/prompts/sampling. The coordinator code/run_m4_parallel.py holds M4/run.lock and merges only after exact prediction and prompt coverage, with zero duplicate IDs. It backs up pre-merge artifacts under M4/before_parallel/. Old blocked queue process 1590743 retired to prevent duplicate startup. Status source is M4/parallel_status.json and each worker progress.json; root M4/progress.json remains the pre-split snapshot until final merge. Aggregate M4 completed = 5830 + completed worker outputs; denominator 13905 (includes smoke). M5 uninterrupted. Both workers produced first 16 results, validated against disjoint manifests.

M0/M2/M5 complete comparison is available in [completed_m0_m2_m5/RESULTS.md](<completed_m0_m2_m5/RESULTS.md>). All three methods have full coverage; M4 remains running. Reproduce: `.venv/bin/python code/analyze_v5.py --methods M0 M2 M5 --output-dir completed_m0_m2_m5`, then `code/report_completed_methods.py`, using the shared MedRGAG Python environment.

M4 expanded to GPUs 0/1/2 by user authorization. Previous workers stopped after each committed 1616 results. Consolidated and verified 9062 unique predictions and matching prompts; old two-GPU artifacts retained in M4/parallel_two_gpu, and pre-consolidation base files retained in M4/before_parallel_*. Remaining 4843 items divided by whole 16-item batches: [1616,1616,1611], disjoint exact coverage. New workers all produced output; no generation settings changed. Coordinator supports all three workers; GPU 0 retains external-process/memory guard. Aggregate count is 9062 + three worker counts, denominator13905. GPU 3 remains untouched.

最终状态：四方法推理、分片合并、全量覆盖检查及评分审计全部完成，见 [RESULTS.md](<RESULTS.md>)。全部评测进程已退出，GPU 1/2 已释放；GPU 0/3 的其他用户进程未操作。M4 的完整分片记录及切换历史保留在 M4/parallel* 与 supervision.md。

## 实施与复现总记录（2026-09-13）

[五方法评测实施、调整与复现记录](<../EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)汇总实际配置变更、工程加速验证、资源调度时间线、最终结果及论文表述边界；历史日志中的中间状态以该记录及最终审计为准。

## 本轮格式修复的统一交接

[实施总记录](<../EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>)第10–13节汇总M4/M6诊断、候选方案、逐文件调整、复核命令和论文表述；明确区分正式结果、独立试验及尚未应用的补丁。
