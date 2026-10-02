# TC-RAG（M7）

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。完整第二版TC-RAG已完成13,905个全新v5输入及15,616评分映射。协议有效97.43%、格式97.25%、原生78.45%、ALL准确率49.43%；保留早期暂停结果、控制流程修复、typed版和仅异常恢复版的消融，不能混写成同一版本。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）](#record-0068)
- [M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）](#record-0069)
- [M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）](#record-0072)
- [64路观察完成，三卡恢复32路（2026-09-13 11:58）](#record-0073)
- [保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）](#record-0075)
- [M7 第二版修复从头试跑完成（2026-09-13 21:05）](#record-0082)
- [M7 最新仅异常恢复版同384题试跑（2026-09-13，启动）](#record-0083)
- [14. M7 暂停结果有效率核查（2026-09-13）](#record-0136)
- [与其他方法的控制流程失败对照](#record-0137)
- [18. M7 输出有效率修复方案与离线验证（2026-09-13）](#record-0147)
- [18.1 问题分层与上游核对](#record-0148)
- [18.2 已实现的确定性候选方案](#record-0149)
- [18.3 全部暂停样本回放结果](#record-0150)
- [18.4 剩余问题的具体解决路线](#record-0151)
- [19. M7 控制流程实际修正与真实续跑（2026-09-13）](#record-0152)
- [19.1 原因与具体修改](#record-0153)
- [19.2 冻结样本、缓存与真实执行](#record-0154)
- [19.3 结果与回答变化](#record-0155)
- [19.4 验证、制品与复现](#record-0156)
- [20. M7 第二版修复从头试跑（2026-09-13 21:05，完成）](#record-0157)
- [原论文有效率口径核查与 TC-RAG 异常恢复依据补充（2026-09-13）](#record-0158)
- [20.1 完整运行与有效率](#record-0159)
- [20.2 审计、成本与证据](#record-0160)
- [20.3 结论与运行交接](#record-0161)
- [21. M7 仅异常恢复的同题消融（2026-09-13，完成）](#record-0162)
- [21.1 具体调整与边界](#record-0163)
- [21.2 同题结果与成本](#record-0164)
- [21.3 结论与证据](#record-0165)
- [22. M7 最新仅异常恢复版同384题试跑（2026-09-13 21:37，完成）](#record-0166)
- [22.1 GPU2启动显存冲突与调度调整（进行中）](#record-0167)
- [22.2 用户指定GPU0承接待跑128题（启动）](#record-0168)
- [22.3 完整同题结果及负结果说明](#record-0169)
- [22.4 轨迹、采样、成本与证据](#record-0170)
- [23. 完整第二版设为 M7 当前主要方法（2026-09-13）](#record-0171)
- [24. M7 完整第二版 v5 全量运行（2026-09-13 21:59，已启动）](#record-0172)
- [24.1 全量完成与最终结果](#record-0173)
- [3.2 TC-RAG](#record-0181)
- [3.3 熵口径和后端调整](#record-0182)
- [2026-09-13 v5 M6/M7 正式输入诊断试跑启动](#record-0204)
- [v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）](#record-0206)
- [v5 M6/M7 提高并发后接续（2026-09-13 06:37）](#record-0207)
- [v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）](#record-0208)
- [M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）](#record-0210)
- [M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）](#record-0211)
- [64路观察完成，三卡恢复32路（2026-09-13 11:58）](#record-0212)
- [11. M6/M7 vLLM 优化、失败重试与完整流程验证](#record-0221)
- [M7 有效率口径核对（2026-09-13，优化后追问）](#record-0227)
- [M7 TC-RAG真实运行](#record-0383)
- [README.md](#record-0400)
- [README.md](#record-0401)
- [README.md](#record-0402)
- [RESULTS.md](#record-0403)

<a id="record-0068"></a>

## v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2204行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

用户明确要求暂停 M6，继续 M7。当前活动包 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced` 未迁移。M6全部109分片标记paused，累计52/13905（40新＋12复用），41有效/11无效/0失败；预测与阶段缓存保留，操作记录m6_pause.json，不自动恢复。GPU1/2原M6已释放并领取M7分片002/003；GPU3原M7分片001未中断。M7三卡均32并发、96000合批token，其余方法/生成/检索设置不变。GPU0未动。tmux仍v5-m6-m7-balanced。

调整独立完成汇总：M7所有分片完成并审计后，自动写results/tcrag/complete.json、原生评分和RESULTS.md，不等待M6；根complete.json仍只用于两方法均完成。暂停队列不被领取和独立评分幂等性等3项针对性测试通过。五分钟进度与GPU0–3报告继续。

<a id="record-0069"></a>

## M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2210行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）

用户询问更大批次/显存是否有帮助及每五分钟新增偏少的原因。读取formal_balanced三张卡最近20分钟的真实请求：平均实际batch2.68/3.13/2.95，完整题平均约6次LLM调用，decode有效位置约42.6%–59.1%，排队中位数122–216秒，检索中位数0.59–1.30秒。长输出拖住整批：6条输出223/7/2048/107/10/169 tokens用了273.6秒。几乎没有批次碰到96000 token上限，因此仅增显存上限不是当前主要改进。

将execution.json中M7 workers32→64，保留96000合批token、原阶段/答案格式/长度分组、完整2048生成预算、模型和熵语义。只在下一分片启动时生效，当前分片不中断。实际配置由各run/batching.json记录。此时M7=362/13905，0运行失败；M6继续暂停52条。证据formal_balanced/logs/m7_throughput_diagnosis.json，变更记录m7_workers64_change.json。64等待池不是实际batch64，完整正式吞吐改善尚未验证。

<a id="record-0072"></a>

## M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2224行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）

formal_balanced的tcrag_004完成128输入并审计通过，64路等待池耗时97.87分钟，15.01有效token/s，decode有效位置36.5%；前三个完整32路分片001/002/003分别79.33/90.97/68.39分钟，18.37–21.08 token/s，45.2%–52.0%有效位置。分片是不同随机输入，输入token量也不同，因此不是成对因果测试；但尚无完整方法提速证据，扩大等待池未消除长输出拖住整批。

据此将后续execution.json的M7 workers恢复32，96000 token上限及全部方法参数不变。当前005/006/007保留64运行至完成，避免丢失未返回生成。M6保持暂停。制品：formal_balanced/logs/m7_completed_chunk_throughput.json、m7_workers32_restore.json。10:33累计M7 780/13905，0运行失败。

<a id="record-0073"></a>

## 64路观察完成，三卡恢复32路（2026-09-13 11:58）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2230行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 64路观察完成，三卡恢复32路（2026-09-13 11:58）

四个64路正式分片004–007均已完成并审计，耗时97.87/102.92/127.36/88.72分钟，中位100.40分钟，合并73.69输入/GPU小时；此前三个32路完整分片001–003耗时79.33/90.97/68.39分钟，中位79.33分钟，合并96.53输入/GPU小时。64路的有效生成吞吐14.90–17.04 token/s，32路18.37–21.08 token/s。输入是不同随机分片，保留非成对观察限制，不宣称严格因果比；四片均未支持增加并发的实际收益。已完成全部64路分片，GPU1/2/3当前分片009/008/010均按32路、96000合批token继续，未中断任何分片。M7累计1148/13905、0运行失败；M6仍暂停52条。

完整制品更新于formal_balanced/logs/m7_completed_chunk_throughput.json，包含逐片请求数、生成/输入tokens、实际批量、有效decode比例及耗时，供后续论文与效率分析引用。

<a id="record-0075"></a>

## 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2240行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 保存M7，三卡全量运行新M4结构约束修复（2026-09-13 13:52）

用户明确要求保存M7并让GPU1/2/3全力运行刚更新的M4，额外监督有效率。M7已13:45暂停，1646/13905（1634新＋12复用），1026有效/620无效/0失败、11完整分片；已核对单题terminal数量与独立保存点一致。保存点：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/；原阶段缓存保留，m7_pause.json记录暂停。M6仍52条暂停，不自动恢复两方法。

新活动包：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/README.md。全新生成13905条，复用原M4完整历史检索消息，加入已试验的明确输出契约与逐题JSON Schema/xgrammar。代码和修改后的全量输入独立保存，旧M4不覆盖。Llama3.1-8B、BF16、温度0.7、top_p1、seed42、2048输出及131072上下文不变。每卡vLLM常驻实例、.90显存、128并行序列、16384 prefill token、prefix cache/chunked prefill，109个锁保护动态分片。tmux v5-m4-structured；GPU0未动。

队列与有效率监控2项针对性检查通过；监控复现已有100题98格式有效/84原生有效/99Schema有效/1截断。监控分别报告格式/原生/Schema有效率、截断和题型原因，并单列100条方案选择输入之外的有效率；全部无效保留分母。原v5的3个共享输入存在不同gold映射，最终评分保留全部映射；去重有效率与gold无关。全量完成后自动合并并调用原生分析器，生成scores/、validity.json、complete.json、RESULTS.md。五分钟报告继续针对新M4。

<a id="record-0082"></a>

## M7 第二版修复从头试跑完成（2026-09-13 21:05）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2286行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M7 第二版修复从头试跑完成（2026-09-13 21:05）

用户授权后，GPU1/2/3各128题，共384个新选v5输入，从第0步全新生成，检索新缓存；排除原1646终态、修复开发与优化输入。使用最终typed控制修复和已验证vLLM后端，64线程/卡、70%显存。主记录及后续结果见[实施记录第20节](/home/data3/txy/docs/baselines/tcrag.md#record-0157)。运行包results_v5_m6_m7/m7_repaired_fresh；tmux m7-repaired-fresh；旧M6/M7全量队列仍暂停，GPU0未操作。

上述384题试跑全部完成：格式95.31%、原生75.52%、0运行失败；全部2459次生成均从头计算，三卡含初始化墙钟约7分9秒。具体原因、成本、复核与限制以[主记录第20节](/home/data3/txy/docs/baselines/tcrag.md#record-0157)为准。本次进程已退出，GPU2随后被其他用户使用；原全量队列仍暂停。

<a id="record-0083"></a>

## M7 最新仅异常恢复版同384题试跑（2026-09-13，启动）

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第2292行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### M7 最新仅异常恢复版同384题试跑（2026-09-13，启动）

用户指定更新版，采用candidate_recovery_only.py，GPU1/2/3各128题全新推理，沿用第20节同题分片作对照。详见[主记录第22节](/home/data3/txy/docs/baselines/tcrag.md#record-0166)；运行包/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh，tmux m7-recovery-only-fresh。旧M6/M7全量队列仍暂停，GPU0不动。

本轮启动更新：GPU2初始化时与其他用户训练显存冲突，未产生任务LLM结果。用户随后明确指定GPU0，待跑128题已改由GPU0执行；当前本次占用GPU0/1/3，保留所有其他用户进程。旧GPU2启动失败与新runs/gpu2_retry分开保存，实际物理卡以resolved_config为准。详见主记录第22.1–22.2节。

最新仅异常恢复版384题试跑已完成（21:37）：格式70.05%、原生52.60%、0单题运行失败；另保留GPU2初始化冲突1次，按用户授权GPU0接续成功。与同题完整typed版95.31%/75.52%相比，有效率较低，预算耗尽99题。主事实、成本和运行交接见[第22节](/home/data3/txy/docs/baselines/tcrag.md#record-0166)。本次GPU0/1/3进程退出，其他任务及旧全量队列保持。


2026-09-13 最新全量运行：用户指定完整第二版M7（typed-control-v2）重新生成全部13,905个v5输入，GPU0/1/3，五分钟监督与完整原生评分。运行包/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full；状态及后续结果见[主记录第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)。历史旧队列仍暂停。


2026-09-14 最新完成：M7完整第二版13,905输入全量新生成、15,616原生评分映射和109分片轨迹审计均完成；协议97.43%、格式97.25%、原生有效78.45%、ALL准确率49.43%，0运行失败，GPU0/1/3本轮模型进程退出。结果与六方法图：[完整报告](/home/data3/txy/docs/baselines/tcrag.md#record-0403)；方法/成本/失败记录统一见[主记录第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)。M6及旧M7队列继续暂停。


2026-09-14 08:53：按用户要求试跑新版M6 MedGENIE（v2及多选序列化修复），此前M7相同384题全部重新生成，GPU0/1/3，GPU2其他训练保留。运行包[m6_medgenie_fresh](/home/data3/txy/docs/baselines/medgenie.md#record-0396)，方法与试跑主记录见[PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/docs/baselines/medgenie.md#record-0231)。旧i-MedRAG暂停保存点不恢复，M7全量已完成。


2026-09-14 09:00完成：新版M6 MedGENIE同题384试跑全部新生成，协议96.61%、格式95.31%、原生74.74%，0失败/重试/复用，含启动5分19秒，GPU0/1/3本轮模型已退出。412评分映射与2304生成轨迹审计通过；诊断原生有效21/105。仅为输入子集试跑，未加入全量方法图表。主记录和证据：[MedGENIE试跑](/home/data3/txy/docs/baselines/medgenie.md#record-0231)、[结果](/home/data3/txy/docs/baselines/medgenie.md#record-0397)。


2026-09-14 09:04最新全量：用户授权新版M6 MedGENIE v2全量13905输入全新生成，GPU0/1/3，每卡常驻32题目线程，109动态分片，五分钟表格监督；GPU2训练保留。主记录：[MedGENIE全量](/home/data3/txy/docs/baselines/medgenie.md#record-0232)，[运行包](/home/data3/txy/docs/baselines/medgenie.md#record-0398)。384试跑和旧i-MedRAG制品独立保留。


2026-09-14 11:48最新完成：新版M6 MedGENIE v2全量13,905输入和15,616原生评分映射完成；全部新生成，0运行失败/重试/阶段复用，109分片、83,430次真实生成轨迹检查通过。协议97.45%、格式96.49%、原生有效77.32%，ALL原生准确率48.02%。推理含初始化2小时41分46秒，GPU0/1/3本轮模型已正常退出。方法和成本主事实见[主记录](/home/data3/txy/docs/baselines/medgenie.md#record-0232)，[最终报告与七方法图](/home/data3/txy/docs/baselines/medgenie.md#record-0399)。旧i-MedRAG保持历史暂停，完整第二版M7结果保留。

<a id="record-0136"></a>

## 14. M7 暂停结果有效率核查（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第592行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 14. M7 暂停结果有效率核查（2026-09-13）

只读冻结暂停时的全部1,646个唯一终态，包括12条复用试跑；与用户提供的1,026有效、620无效、0运行失败一致。协议有效率62.33%。[完整计数](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/summary.json)与[原始终态快照](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/snapshot.jsonl)保留，未修改运行、解析或评分。

| 无效原因 | 数量 |
|---|---:|
| 已被状态监控器接受，但选项键不合法 | 278 |
| 已接受，但errors字段无效 | 13 |
| 已接受，但答案对象缺失或冲突 | 2 |
| 已接受，但文档ID不符合协议 | 1 |
| 8步预算耗尽，未返回被接受的最终答案 | 272 |
| 动作解析失败（empty_thought） | 54 |

294条属于已接受最终答案的输出协议失败，占620条无效的47.42%。278条选项键问题都以合法键开头；其中207条是“键＋与题目完全相同的选项正文”，71条是键后附其他字符/正文（例如no.），不能直接假设这71条语义全部一致。例s103363返回 `{"answer":"A. Sorbitol dehydrogenase"}`。

272条预算耗尽逐题回查tc_action轨迹：122条没有任何final proposal；104条最后一次final proposal被entropy_threshold拒绝；46条最后一次proposal发生太早、被minimum_steps拒绝，之后未完成接受。该分类依据最后一次final proposal，不等同于断言某单一原因独立导致整场失败。当前实现max_loop=8，接受条件为step>=topK（topK=4，step从0开始）且state<sigma（sigma=1.2）；不得将未接受栈顶直接转换成成功最终答案。

54条动作解析失败均记录empty_thought。可见实例只输出 `Action Input: {"query": "..."}` 而没有对应Action/Thought标签；这里的错误名不能理解成模型“没有思考”，需要按原工具调用协议进一步核查兼容性，不能凭空补动作。

结论：M7的低协议有效率同时包含输出适配损失和控制流程未正常收敛。M6的确定性JSON/字面量兼容不能一键解决这两类；对已接受终态可研究保留答案的格式适配，动作解析需独立验证，放宽sigma、减少最小步数、增加max_loop或强行接受答案均是方法/预算变更，应单独记录。当前没有实施修复、重跑或计算修复后的正式有效率，也没有重算原生评分；协议有效不等于答对。

<a id="record-0137"></a>

## 与其他方法的控制流程失败对照

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第613行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 与其他方法的控制流程失败对照

进一步只读核对了M3新增预测及M6暂停终态。M0/M1/M4/M5的最终回答为单轮生成，M2为固定阶段流水线，均没有当前TC-RAG的动作栈、minimum_steps与sigma终止门控；这不表示它们没有JSON/选项/截断错误。

M3属于最接近的多轮情形：新增10,215条中9,926 complete、186 invalid_answer、88 vote_tie、15 runtime_invalid；15条均为查询生成在固定输出预算内缺少 `</think>`。M3到最后一轮按唯一最高票回答，不要求所有候选一致，也没有M7那种最终答案必须低于sigma的接受门槛。这里只统计新增部分，不将其比例与M7早期1,646条直接作公平排名。

M6当前暂停52条，41 ok、11 invalid，全部到达final_formatted；11无效是10答案对象提取失败和1答案类型错误。查询轮次还记录2次missing_or_conflicting_output、1次missing_queries_section（是事件数，不一定对应3个唯一输入）；当前实现跳过失败查询轮次后仍尝试最终回答。M6的4轮上限本身不会像M7那样把未过熵门槛的最终提议标为预算耗尽。

因此共有的问题包括格式损失、查询解析和token预算；M7特有的当前问题是动作协议/状态栈与熵及最小步数门控共同导致的无效终态。跨方法比较需要区分“总能返回文本”和“按自身协议有效完成”，不能仅凭终态比例认定某种推理方法更好。

后续已完成的接受后输出适配及1,026→1,281协议有效离线回放集中见[第18节](/home/data3/txy/docs/baselines/tcrag.md#record-0147)。它仍为未部署候选，原预测和暂停队列保持。

随后控制流程修正已真实试跑，见[第19节](/home/data3/txy/docs/baselines/tcrag.md#record-0152)的样本、结果和答案变化；本节原始诊断计数保留。

<a id="record-0147"></a>

## 18. M7 输出有效率修复方案与离线验证（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第723行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 18. M7 输出有效率修复方案与离线验证（2026-09-13）

<a id="record-0148"></a>

## 18.1 问题分层与上游核对

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第725行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 18.1 问题分层与上游核对

沿用已冻结的 1,646 条 M7 暂停终态，未选择性抽取错误或重跑。原 1,026 有效、620 无效、0 运行失败。294 条无效已通过 TC 的最终答案接受门槛，属于输出协议损失；另 272 条预算耗尽、54 条动作解析失败，不能靠最终答案格式化全部解决。

核对[锁定版本 TC-RAG 官方执行器](https://raw.githubusercontent.com/Artessay/TC-RAG/dd8f32f90832eeb452680cfdb02ca604988648d0/model/TCRAG.py)：保留 max_loop=8、topK=4、sigma=1.2，Final Answer 同时满足步数与熵条件才接受。官方部分异常工具输出会通过 plugin-not-found 等路径继续循环，而本地 parse_action 抛错立即返回 action_parse_failed；这是一项需要分离验证的失败恢复适配差异，不意味着可以凭空补出缺失 Action 或保证修复全部 54 条。

不能直接把 M4 的 xgrammar 施加于 M7 动作生成后仍声称接受语义不变：TC 使用经过生成处理器的分布熵，约束采样可能减少分布熵并改变 sigma 门槛是否通过。若以后研究约束生成，应另行定义和记录熵计算分布及阈值对照，不能把因此更容易通过门槛当作模型更确定。

<a id="record-0149"></a>

## 18.2 已实现的确定性候选方案

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第733行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 18.2 已实现的确定性候选方案

新增 `m7_validity_audit/normalize_accepted.py`，仅接收模型原响应、终态和可见原生选项；不读取 gold。只有 termination=accepted 且原 status=invalid 的 single/robustness_single 才可能转换，其他结果原样返回。

- 严格 JSON 的 answer 恰为“原生选项键＋`. `＋完全相同的选项正文”时，改为原生键；要求正文与该键对应的原选项完全一致。
- answer 恰为“原生键＋单个句号”时去除该句号，如 `no.`→`no`；不截取带其他解释的前缀，`yes. ED` 仍无效。
- 普通 single 的原响应恰为一个合法原生键时，包装为 answer JSON 对象；robustness_single 不使用此规则，因为它还要求 errors。
- 不补 errors、不改文档编号、不猜诊断、不选择冲突答案、不执行额外 LLM；拒绝重复 JSON 字段。原本有效输出保持原文本。

候选部署位置只在 tcrag 已接受最终答案之后，不改生成消息、熵信号、阈值、状态栈、检索及预算。`methods.integration.patch` 给出这一局部接入和审计事件；应用时还需将 normalize_accepted.py 复制到运行包 code/，使用新的运行版本。当前没有应用到活动方法，也没有覆盖原始终态。

<a id="record-0150"></a>

## 18.3 全部暂停样本回放结果

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第744行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 18.3 全部暂停样本回放结果

| 指标 | 原始 | 确定性候选 |
|---|---:|---:|
| 唯一终态数量 | 1,646 | 1,646 |
| 协议有效 | 1,026 | 1,281 |
| 协议有效率 | 62.33% | 77.83% |
| 无效 | 620 | 365 |
| 本轮新增 LLM 请求 | 0 | 0 |

共执行 260 次表示转换：完整键＋正文 206、键＋句号 52、裸键包装 2；其中 255 条新增有效，另外 5 条仍因其他必需字段无效而失败。原排查的 207 条完整键＋正文包含本候选严格整段 JSON 解析未接受的格式，因此不能把 207 全计为已修复。

剩余 365 条：budget_exhausted 272、action_parse_failed 54、invalid_errors 17、invalid_option_key 20、invalid_document_ids 2。errors/文档ID计数比初始排查增加，是修复选项表示后暴露了后续字段错误，原验证顺序此前首先报选项错误；不是删除或新增了这些字段。

`check_repair.py` 对全量 1,646 条回放，验证输入集合、原有效文本完全保持、所有未接受终态完全保持、变更后的键与原显式选项身份一致、其他 JSON 字段保持，并运行冲突、重复键、矛盾正文、预算失败及缺失 errors 的针对性检查。修复候选逐题保存为 `repaired_candidate.jsonl`，计数为 `repair_comparison.json`，原 snapshot.jsonl 不变。

```bash
python3 m7_validity_audit/check_repair.py
```

这里报告的是该暂停样本的协议有效率，不是原生正确率，也不是全库确认；本轮没有重算正确率。样本已用于规则开发，不能称独立验证集。表示转换保持所选选项的身份，不声称 JSON 字符串逐字不变。

<a id="record-0151"></a>

## 18.4 剩余问题的具体解决路线

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第766行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 18.4 剩余问题的具体解决路线

1. 优先将已验证的接受后转换作为独立适配版本，并保留旧结果；后续比较需报告新增有效与真实答对的区别。
2. 对 54 条动作解析失败，在独立试验中评估“记录协议错误并允许在剩余原 8 步内重新输出合法动作”；没有明确工具名时不执行检索，不将失败直接视作有效。此方案需要新的生成，当前未实施或测量收益。
3. 在新试验中加强 Final Answer 的逐题原生格式契约，明确只输出键、必须提供 errors 及可见 D 编号；不让 formatter 重新选择医学答案。提示改变会影响后续轨迹，不能离线套用旧请求来声称新运行等价。
4. 对 272 条预算耗尽，分别检查无 final proposal、熵拒绝、过早提议后未收敛；延长轮数、放宽 sigma、改变熵归一化或强制末轮接受都是新的方法/预算变体，需要独立报告。仅对已接受终态做后处理的理论上限为 1,320/1,646≈80.19%，因为另外 326 条从未被接受。

本轮未恢复 M7/M6、未加载模型或操作 GPU。以上代码与补丁属于已验证的离线候选，完整控制流程修复和全量收益尚未验证。继续在本文记录后续实施，不新建替代总记录。

第18节候选制品：[计数](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/repair_comparison.json)、[转换代码](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/normalize_accepted.py)、[验证脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/check_repair.py)、[接入补丁](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/methods.integration.patch)。

<a id="record-0152"></a>

## 19. M7 控制流程实际修正与真实续跑（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第779行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 19. M7 控制流程实际修正与真实续跑（2026-09-13）

<a id="record-0153"></a>

## 19.1 原因与具体修改

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第781行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 19.1 原因与具体修改

上一节的接受后表示转换只能改善协议损失，仍留下 272 条预算耗尽及 54 条解析失败。用户要求继续修正，因此本轮在独立 `m7_validity_audit/control_pilot/` 中实现并真实验证控制流程适配。原 formal_balanced 源码、1,646 条终态和阶段收据保持不变，M7/M6 原全量队列继续暂停。

| 位置 | 原行为 | 第一版实际调整 |
|---|---|---|
| parse_action 异常 | 立即返回 action_parse_failed，剩余轮次不用 | 记录原错误、不执行未知工具，给下一轮明确合法动作格式反馈，在原剩余预算内继续 |
| Final Answer 太早 | 转为 Thought，模型看不到明确拒绝原因 | 下轮告知提议过早，请继续思考或检索；仍由 step>=4 决定最早接受时间 |
| Final Answer 熵不通过 | 转为 Thought，模型可能重复长 Thought＋答案 | 下轮告知未通过监控，要求检查证据、解决不确定性后再给简洁最终答案；不把熵数值写进提示、不放宽阈值 |
| 无最终提议而预算将尽 | 模型不知道执行器剩余生成轮数 | 第 7、8 次生成前告知剩余 2、1 轮，准备好时提出答案；没有强制返回或增加轮数 |
| 最终输出格式 | 无适时的完整契约提醒 | 上述反馈中提示 Final Answer 后只放所需 JSON、不带 Thought 前缀，保留上一节的确定性接受后转换 |

第一版文件为 `candidate_methods.py`。`candidate_typed.py` 为第二版，额外调整：

1. 反馈按 answer_format 使用原 answer_contract，诊断要求诊断字符串，multi 要求数组，relation 要求原关系值；避免第一版通用“只输出选项键”与无选项题型冲突。
2. 答案已过熵门槛但 valid_answer 仍失败时，若尚有原预算，则记录 tc_invalid_output_continued，将该提议留作 Thought 并反馈具体格式错误，要求保留已选答案、纠正表示或按证据补齐所需 errors。若已到第 8 次生成则照常保留无效，不额外调用模型。

两版都保留 Qwen3-8B、BF16、HF Transformers 4.51.3、temperature=.7、top_p=1、top_k=0、2048 action 输出上限、131072 上下文、max_loop=8、topK=4、sigma=1.2、原始未加约束的全词表熵和原 token 选段规则。没有使用 xgrammar、降低阈值、增加原每题最大轮数或强制接受末轮答案。全局 seed=42 与原按请求派生随机种子的规则保留；消息变更会改变请求键及其派生种子，不能宣称逐请求随机数与旧提示完全相同。

这些变更会改变提示、后续推理轨迹和回答。简洁最终输出也会改变熵求和所覆盖的生成长度；虽然计算公式与门槛未改，仍不能称停止行为等价或完全复现上游提示。属于显式记录的控制/输出协议适配，不作为已证明的新推理算法。

<a id="record-0154"></a>

## 19.2 冻结样本、缓存与真实执行

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第802行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 19.2 冻结样本、缓存与真实执行

- 开发试验20题，seed20260913：8动作解析失败、4无最终提议、2最后因熵拒绝、2最后因步数拒绝、4原本有效。按失败分层，不能用20题有效率估计整体。
- 随后从其余暂停终态中随机选100题，seed20260914，抽取不按正确性或状态挑选，和前20题无重叠。第一版复验后，第二版在同一100题上复核；第二版已利用第一版发现的问题，因此不是独立确认集。整个暂停队列此前也已用于问题诊断，不是外部泛化集。
- 每批生成前，用原 methods.py 和逐题精确匹配请求缓存回放基线；20题及100题各分片原文本/状态/termination均一致，基线回放零新增模型请求。候选从头执行控制逻辑，只复用 spec 完全相同的历史请求；提示或上下文变化的请求真实重算。
- 第二版额外复用第一版中完全匹配的收据。派生缓存写入独立候选目录，原收据不改写；检索沿用既有共享查询缓存。
- 20题使用GPU1；100题划分34/33/33到GPU1/2/3，8个输入线程/卡、64000合批token，按原阶段/类型/长度分组的HF批处理。GPU0保留其他用户占用，未操作。当前20题及两版100题均已结束，GPU1–3已释放。
- 实际新增LLM请求：开发20题38次，第一版100题187次，第二版100题64次，合计289次。共保存220个候选终态，涉及120个不同输入；不得把重复试验当作220个独立病例。

<a id="record-0155"></a>

## 19.3 结果与回答变化

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第811行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 19.3 结果与回答变化

| 样本 / 版本 | 原协议有效 | 修正后协议有效 | 说明 |
|---|---:|---:|---|
| 20题失败分层开发 / 第一版 | 4/20 | 20/20 | 16个原控制失败恢复；4个原有效答案值不变 |
| 随机100题 / 第一版 | 61/100 | 98/100 | 12预算耗尽、3动作解析失败全部恢复；2格式失败保留 |
| 同一100题 / 第二版 | 61/100 | 99/100 | 进一步修复1个缺失errors；剩1个非法选项键 |

100题原无效分组为24已接受但格式无效、12预算耗尽、3动作解析失败。第二版对应有效数23/24、12/12、3/3；原先61有效仍61有效。剩余 s201019 到第8次生成仍输出 `yes. ED` 而非原生合法键 yes/no，保留 invalid_option_key，没有截断字符串猜选项或按结果补分。

按原评分器对这100题全部105条映射（含reference）评分：原生有效49→87→88，原生正确33→69→70（原版→第一版→第二版）。这是试验的映射计数，不是完整v5单元等权准确率，也不与其他方法全量分数直接排名。gold仅在生成后用于该离线分析，不参与提示或修复。

原本协议有效的61题涉及63条映射，原生正确数两版均保持33、原生有效数均保持49；这不表示每一题答案保持。第一版有3个答案值变化；第二版也有3个：s024893 lower→uncertainty，s145243 yes→no，s011811 Mucormycosis→Tuberculosis (TB)。其他字段（如纠错文本）也可能重新生成，因此只能说该子集汇总正确数未下降，不能声称逐题无损或语义等价。

<a id="record-0156"></a>

## 19.4 验证、制品与复现

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第825行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 19.4 验证、制品与复现

`test_control.py` / `test_typed.py` 覆盖解析失败恢复、不凭空执行工具、过早提议不接受、高熵提议不接受、8步上限、诊断类型提示、缺失errors纠正及末步失败保留。真实事件逐项核对：20题36次、第一版100题233次、第二版100题240次Final Answer门控，accepted均严格等于step>=4且原熵和<1.2；state与保存的逐token熵求和一致。

证据位于 `m7_validity_audit/control_pilot/`：

[第二版100题报告](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/typed100/comparison.json) · [第一版100题](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/validation100/comparison.json) · [20题试验](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/comparison.json) · [固定样本ID](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/selection_manifest.json) · [最终代码](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/candidate_typed.py) · [接入差异](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/control_v2.integration.patch)

- `comparison.json`：20题对照；`validation100/comparison.json`与`typed100/comparison.json`：两版100题结果、原有效答案变化和门控核对。
- `selection_manifest.json`：固定输入ID、题型与分层；完整原生输入、原响应和来源在本地selection.json。
- `candidate_methods.py`、`candidate_typed.py`、`normalize_accepted.py`和`control_v2.integration.patch`：实际执行代码及相对原方法的最终接入差异。
- `run_pilot.py`、`run_validation.py`、`run_typed.py`及对应sh：本轮准确执行流程，含原缓存回放和独立输出目录。
- 各分片`baseline_replay.json`、`backend.json`、`complete.json`、candidate逐题events/requests/result.json及`supervision.jsonl`：运行和复核收据。

仅离线复核（不启动模型）：

```bash
python3 m7_validity_audit/control_pilot/test_typed.py
/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python m7_validity_audit/control_pilot/report.py typed
```

第二条需要本地逐题候选、冻结评分映射与canonical标签。不要把本地复核命令当成公开仓库已包含全部原始题目。接入正式运行应使用新版本目录、保留原结果，并复制normalize_accepted.py及应用最终补丁；本轮未将99%写成13,905题全量结论，也未恢复M7/M6原队列。

<a id="record-0157"></a>

## 20. M7 第二版修复从头试跑（2026-09-13 21:05，完成）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第851行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 20. M7 第二版修复从头试跑（2026-09-13 21:05，完成）

用户确认M7有效率修复后，要求从头试跑。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh)。采用第19节最终 candidate_typed.py 与 normalize_accepted.py 原文件，接入已验证的vLLM0.8.5 V0连续调度/FP32全词表熵后端。控制/类型修复定向检查全部通过，未修改候选方法本身；审计器增加反馈消息、接受后规范化及预算内继续执行的事件核对。

固定seed20260916，从v5可见原生输入随机抽384题，排除原M7保存点全部1646题、修复开发输入及先前优化输入（合计排除1735个ID）。与修复/优化样本均0重叠；题型为single188、diagnosis105、robustness_single65、relation20、multi6。冻结输入及计划见inputs/all_384.jsonl与plan.json；不按答案/结果选择。属于新的384题验证，仍在已使用过的v5内，不是外部泛化集。

GPU1/2/3各128题、64输入线程，70%显存预留、128最大序列、16384每步prefill token。模型Qwen3-8B、BF16、完整2048生成token、131072上下文、8步预算、topK4、sigma1.2保持；修复本身改变反馈消息及后续轨迹，不能声称与旧方法停止行为等价。新方法版本 iterative-v4-tc-typed-control-v2-vllm，按现有请求配置派生种子；不承诺与历史逐请求seed/输出相同。

三个全新run目录从第0步生成，未复制任何历史LLM收据；检索使用本运行包新的空缓存目录，仅允许本次试跑内部相同查询命中。原M6/M7保存点及全量队列保持暂停，GPU0不操作。tmux socket m7-repaired-fresh，启动命令为 bash launch.sh <GPU> m7_vllm --inputs inputs/gpu<GPU>.jsonl --run-dir runs/gpu<GPU> --workers 64。日志在logs/gpu*.log，结果和评分将在reports/中补充，完成后续写本节。

<a id="record-0158"></a>

## 原论文有效率口径核查与 TC-RAG 异常恢复依据补充（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第861行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 原论文有效率口径核查与 TC-RAG 异常恢复依据补充（2026-09-13）

本次核对以下版本的正文、实验指标与附录，未找到与本地协议有效率、原生有效率或严格JSON/Schema有效率口径相同的单独数值报告；这不是断言作者输出全为有效，也不意味着论文使用本地严格JSON/诊断映射协议。

| 本地方法 | 原论文及位置 | 报告内容与相关说明 |
|---|---|---|
| M0/M1 | 本项目直接回答/检索对照 | 不是各自独立原论文方法；本地有效率属于本项目诊断统计 |
| M2 MedRGAG | [2510.18297v1](https://arxiv.org/html/2510.18297v1)，§4与附录D | 主要指标为accuracy；附录有要求JSON的回答模板，但未见解析成功率或本地原生有效率的独立数值 |
| M3 Multi-Round Agentic RAG | [2603.03292v1](https://arxiv.org/html/2603.03292v1)，§4.1及附录 | 主要报告七个医学基准accuracy，另有成本及候选排序分析；未见同口径无效终态比例。勿与同名Multi-Agent Retrieval-Augmented Generation论文混淆 |
| M4/M5 MedRAG | [ACL Findings 2024.372](https://aclanthology.org/2024.findings-acl.372/)，主表与限制 | 报告MIRAGE选择题准确率；并非本地多题型v5以及修复M4的生成协议，未见单独JSON/Schema有效率 |
| M6 i-MedRAG | [2408.00727v3](https://arxiv.org/html/2408.00727v3)，实验结果 | 主要报告MedQA/MMLU-Med等准确率，未见formatter成功率或本地原生有效率的独立统计 |
| M7 TC-RAG | [2408.09199v3](https://arxiv.org/html/2408.09199v3)，§6.1、§8.7.5、§8.9 | 选择题使用EM，开放QA使用BLEU/ROUGE等，扩展任务有EM/F1；§8.9明确讨论格式错误与解析重试，但没有报告本地定义的有效率百分比 |

**补充并纠正此前依据遗漏：** TC-RAG的[§8.9](https://arxiv.org/html/2408.09199v3)明确写出两类异常处理：先用正则/模板等方式提取可用组件，仍解析失败则通过循环与异常捕获让模型重新生成，直到可解析或达到预定上限。此前本地parse_action失败立即结束整题，未完整体现论文说明的恢复机制；第19节补齐失败后恢复有直接论文依据，应该优先定位为复现/适配缺口修复。该段没有给出足以与本地实现逐项对齐的重试次数及预算细分，因此不能断言我们的具体反馈提示、原8步内扣预算规则、临近末轮提示和格式纠错实现逐项等同作者实现，也不能据此声称100%有效保证。

TC-RAG附录的有限时间收敛讨论依赖动作有效性与状态下降等假设，不等于实测有限8步内全部完成。EM/accuracy未单列失败原因也不能反推出作者的JSON成功率；开放QA的BLEU/ROUGE更不要求进入我们使用的冻结诊断canonical映射。因此论文里的高准确率或收敛结论均不能直接证明本地原生有效率应为100%。

本项目可把这些比例作为跨题型适配的补充诊断指标，明确分母与失败定义；引用原论文accuracy/EM作为原实验结果时，不改称“原生有效率”。本次为文献核查及现有记录补充，无新增推理、无运行代码修改。

<a id="record-0159"></a>

## 20.1 完整运行与有效率

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第880行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 20.1 完整运行与有效率

384/384唯一输入完成，缺失/重复/未知ID/运行失败均0；各卡128题均从第0步运行，无任何阶段收据复用。GPU1/2/3推理墙钟391.92/333.33/344.85秒，含模型及检索初始化428.92/370.41/381.84秒；三卡从配置落盘20:58:04到最后终态21:05:13约7分9秒，不含选样及代码准备。按各卡实际运行时长求和归一化，推理吞吐1291.85题/GPU小时，含初始化1170.37题/GPU小时；不把其他卡完成后的空闲计作仍在推理。

| 原生题型 | 输入数 | 协议/格式有效 | 原生有效 |
|---|---:|---:|---:|
| diagnosis | 105 | 104 | 28 |
| multi | 6 | 6 | 6 |
| relation | 20 | 20 | 20 |
| robustness_single | 65 | 64 | 64 |
| single | 188 | 172 | 172 |
| **合计** | **384** | **366（95.31%）** | **290（75.52%）** |

协议与v5格式有效在本次样本上均为366条，原生评分进一步有76条诊断未映射。没有计算或宣称完整v5单元等权准确率。18条协议无效：16条invalid_option_key、1条missing_or_conflicting_answer、1条budget_exhausted，全部已执行到第8步，未额外生成或按结果补分。16条选项错误的键空间分布为{'A/B/C': 1, 'yes/no': 14, 'A/B/C/D': 1}；实际仍可见“yes. ED”、原键A/B/C却输出“maybe”等，保留原输出，未在本轮扩大转换规则。

<a id="record-0160"></a>

## 20.2 审计、成本与证据

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第895行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 20.2 审计、成本与证据

新生成2,459次、9,570,503输入tokens、272,567输出tokens，平均每题6.40次调用；8次生成长度截断保留。检索756次中676次调用后端，80次仅复用本次试跑建立的新检索缓存。LLM/历史阶段复用0，运行重试0、失败请求0、额外scoring forward0。

完整轨迹核对通过：2,459次模型/token与实际消息、1,900次全词表熵状态重算、758次接受边界、525次协议反馈、39次接受后确定性规范化、28次预算内格式纠正继续、22次记忆移除/状态恢复、1次预算耗尽不冒充答案。新方法文件与第19节candidate_typed.py、normalize_accepted.py逐字节一致；定向控制与转换检查在启动前通过。集成审计器仅适配新反馈与继续事件，没有更改评分规则或候选方法。

- [最终结果与成本](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/final_results.json)
- [错误明细与审计计数](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/failure_breakdown.json)
- [384条新预测](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/predictions.jsonl)、[逐题有效率](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/native_validity_rows.jsonl)、[18条协议无效](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/protocol_invalid_rows.jsonl)
- [最终审计日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/final_audit.log)、[启动前检查](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/prelaunch_checks.json)、[监督记录](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/supervision.jsonl)
- [试跑包与运行命令](/home/data3/txy/docs/baselines/tcrag.md#record-0400)；离线复核在包内执行 `/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/bin/python code/monitor_fresh.py --final`。各runs/gpu*/中保存冻结配置、启动源码快照、完整事件及请求。

<a id="record-0161"></a>

## 20.3 结论与运行交接

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第907行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 20.3 结论与运行交接

修复版在384题全新生成中达到95.31%格式有效，没有复现开发100题的99%；不同样本、引擎、派生种子与历史缓存条件不相同，不能把差值当作单一因素的因果影响。这里原生有效分母是384唯一输入，前次100题原生计数的分母为105评分映射，也不能直接混比。此轮验证可复核修复版运行稳定性和有效率，但不是13,905题全量结论。未追加修复、未更改预算、未启动全量。

本次模型进程已全部退出。GPU2原试跑21:04:14完成，其他用户dcy的训练进程2139748于21:05:12使用GPU2（当次观察约36GiB）；未操作该进程，后续调度须重新检查可用卡。GPU0原其他用户任务保持不动。M6和旧M7全量队列/保存点仍暂停保留。

<a id="record-0162"></a>

## 21. M7 仅异常恢复的同题消融（2026-09-13，完成）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第914行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 21. M7 仅异常恢复的同题消融（2026-09-13，完成）

用户授权尝试加入异常恢复并观察变化。本轮从原始 formal_balanced/code/methods.py 构建 candidate_recovery_only.py，单独测试该机制；未替换正式运行版本，未恢复 M6/M7 全量队列。沿用第19节固定100条开发输入，不是独立测试集或完整v5结论。

<a id="record-0163"></a>

## 21.1 具体调整与边界

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第918行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 21.1 具体调整与边界

动作解析失败后，将实际解析错误及合法动作格式反馈给下一轮，明确没有执行工具；已满足原始接受门槛但最终输出校验失败时，在尚有轮数的前提下反馈题型契约和允许的选项键，要求保留所选答案并纠正格式，再继续生成。所有恢复均消耗原有最多8步预算，最后一步仍无效则保留无效终态。

未加入熵拒绝反馈、最低步数拒绝反馈、剩余轮数提醒或确定性答案字符串转换。模型、原系统提示、topK=4、sigma=1.2、全词表熵计算与接受条件不变；反馈改变实际输入，后续输出不保证等价。种子仍按原请求派生规则生成。TC-RAG §8.9 对解析恢复有依据，但论文未给出足以逐项对齐的重试预算；本轮是有明确边界的复现/适配实验，不应称为原创机制或完全等同作者实现。

<a id="record-0164"></a>

## 21.2 同题结果与成本

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第924行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 21.2 同题结果与成本

| 版本 | 协议有效 /100输入 | 原生有效 /105评分映射 | 原生正确 /105评分映射 | 逻辑模型调用 | 平均调用/输入 | 输出tokens | 检索调用 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 原始 | 61 | 49 | 33 | 607 | 6.07 | 81,025 | 188 |
| 仅异常恢复（本轮） | 77 | 68 | 51 | 641 | 6.41 | 81,974 | 191 |
| 第19节完整第二版修复 | 99 | 88 | 70 | 603 | 6.03 | 77,354 | 196 |

105为包括附加映射的评分记录数，不是105条唯一输入；此表不是v5单元等权准确率。逻辑调用包含历史阶段复用。本轮实际新增34次模型请求，复用795份历史模型/检索收据；生成不读取正确答案。GPU1、3各处理50题，进程记录约66.34/30.58秒，包含加载/回放等，不能作为无缓存完整推理的吞吐指标。

原先61条有效题的原始回答、状态及终止原因全部不变，均无需新模型调用。24条原先已接受但格式无效的题修复16条，余8条为invalid_option_key。原先12条budget_exhausted保持原始输出及终态不变。原先3条action_parse_failed均继续到budget_exhausted：解析失败标签消失不代表得到了有效答案。最终23条无效为15条预算耗尽、8条选项键错误。

定向测试覆盖解析后恢复、没有虚构工具执行、没有拒绝/预算反馈、8步上限及最后一步格式失败。262次最终答案提议的实际接受边界均符合 step>=4 且 entropy_sum<1.2，保存的熵和重算一致。测试与离线评分复核通过。

<a id="record-0165"></a>

## 21.3 结论与证据

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第938行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 21.3 结论与证据

异常恢复使同题协议有效率提高16个百分点，原生正确记录增加18，平均增加0.34次模型调用，值得保留为复现/适配修复。但它没有解决本样本的预算耗尽问题；完整修复的99%还包含其他反馈与确定性表示转换，不能全部归因于异常恢复。完整修复在第20节独立384输入上为95.31%协议有效，开发集99%不能当作泛化或全量保证。

- [独立候选实现](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/candidate_recovery_only.py)、[相对原实现补丁](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/recovery_only.patch)
- [运行入口](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/run_recovery.py)、[启动脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/run_recovery.sh)、[边界测试](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/test_recovery_only.py)、[评分与复核脚本](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/compare_recovery.py)
- [分层结果及审计](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/recovery100/comparison.json)、[三版本成本比较](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/m7_validity_audit/control_pilot/recovery100/three_way_comparison.json)

完整逐题输出、事件与请求收据保存在本地 recovery100/gpu1 和 gpu3 下；公开归档只发布代码、汇总和运行收据，不公开原始题目/答案缓存。两个实验进程均已正常退出。完成后GPU快照：GPU0为9863/97871 MiB、利用率0%；GPU1/2/3均0/97871 MiB、利用率0%。未操作其他用户进程；本机该次查询只返回GPU0–3，无GPU4状态可报告。

<a id="record-0166"></a>

## 22. M7 最新仅异常恢复版同384题试跑（2026-09-13 21:37，完成）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第950行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 22. M7 最新仅异常恢复版同384题试跑（2026-09-13 21:37，完成）

用户要求用再次更新的修复版试运行。定位到21:15更新、已在第21节记录的candidate_recovery_only.py。直接复制该候选文件，不包含完整typed版的熵/最小步数拒绝反馈、剩余预算提醒及确定性答案转换。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh)。

使用第20节同一384题、相同三份128题分配，从第0步重新生成；不按前次结果选题，也不复制任何旧阶段收据。检索使用独立的新空缓存目录。vLLM0.8.5 V0及已验证FP32全词表熵后端保持，Qwen3-8B、BF16、温度0.7、top_p1、2048生成预算、131072上下文、8步、topK4、sigma1.2不变；每卡64输入线程、70%显存、128最大序列、16384每步prefill tokens。GPU1/2/3启动前均空闲，GPU0原其他用户占用不动。

新版本iterative-v4-tc-recovery-only-vllm及新检索路径进入实际收据/缓存身份；仅在派生采样种子时映射回第20节的版本和缓存路径，使相同消息/阶段保持前次seed（不读取旧缓存）。三个真实已保存阶段的seed一致、缓存身份不同的检查通过。不同提示仍派生不同seed；连续调度下不承诺逐token一致，也不能称完全隔离数值影响。异常恢复、原拒绝提示不变、八步边界的候选检查通过，日志reports/prelaunch_checks.log。

审计器沿用前次工具，仅切换为本版tc_exception_feedback/Output error消息并移除不适用的确定性转换审计；预算内继续事件、熵状态、接受边界照常核对。启动命令：bash launch.sh <GPU> m7_vllm --inputs inputs/gpu<GPU>.jsonl --run-dir runs/gpu<GPU> --workers 64；tmux socket m7-recovery-only-fresh。每卡保存启动源码快照、配置、完整原响应和事件；日志logs/gpu*.log。旧试验及M6/M7原全量队列保持不变，结束后补充完整结果。

<a id="record-0167"></a>

## 22.1 GPU2启动显存冲突与调度调整（进行中）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第960行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 22.1 GPU2启动显存冲突与调度调整（进行中）

初次检查GPU1/2/3空闲，但21:27启动GPU2时，其他用户进程2146449已占约35.97GiB。本次进程2147228在vLLM KV cache初始化分配1.38GiB时OOM（当时本进程已占58.38GiB、剩余722.56MiB），尚无输入终态或LLM请求。保留runs/gpu2、logs/gpu2.log及[失败记录](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/gpu2_launch_failure.json)，不覆盖为成功。GPU1/3健康继续。GPU2原定同128题将写入新runs/gpu2_retry，等本次GPU1或3先完成后接续，仍用原方法/输入/预算。其他用户任务不操作，最后区分这次启动失败与完整输入执行失败。

<a id="record-0168"></a>

## 22.2 用户指定GPU0承接待跑128题（启动）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第964行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 22.2 用户指定GPU0承接待跑128题（启动）

用户在运行中明确指示“在gpu0运行”，授权GPU0承担原GPU2分片。启动前GPU0总97,871MiB、已占10,198MiB、利用率0%；保留原进程1202819/1202820及2146449，未停止其他任务。新命令：bash launch.sh 0 m7_vllm --inputs inputs/gpu2.jsonl --run-dir runs/gpu2_retry --workers 64，仍为70%显存预留及原方法预算。记录[GPU0接续启动](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/gpu0_retry_launch.json)，日志logs/gpu0_retry.log；实际GPU写入resolved_config，不把文件名gpu2误作物理GPU。GPU1/3继续原128题，GPU2其他用户训练保留。

<a id="record-0169"></a>

## 22.3 完整同题结果及负结果说明

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第968行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 22.3 完整同题结果及负结果说明

384题全部完成，输入与第20节相同，缺失/重复/未知ID/单题运行失败均0。最后一个分片按用户指令在GPU0运行，物理GPU1/0/3分别完成128题。每个分片完整推理369.21/357.61/336.99秒，含初始化404.27/390.70/371.77秒。按各卡成功运行时长求和归一化，推理吞吐1299.49题/GPU小时、含初始化1184.84题/GPU小时；GPU0与其他进程共用，并且有分片接续，不能把该数值视为与前次独占GPU2严格可比的纯速度实验。

整次从首个成功run配置落盘到最后终态约645.92秒，包含GPU2冲突处理及改卡等待；失败初始化另耗约23.00秒，未产生任何任务LLM请求，但初始化仍消耗计算资源。失败日志和原runs/gpu2保留，未混入成功吞吐。

| 同384题版本 | 协议/格式有效 | 原生有效 | 预算耗尽 |
|---|---:|---:|---:|
| 第20节完整typed第二版 | 366（95.31%） | 290（75.52%） | 1 |
| 最新仅异常恢复版 | 269（70.05%） | 202（52.60%） | 99 |

本次协议无效115题：99预算耗尽、15非法选项键、1个errors字段不合规；另有67条诊断未映射导致原生无效。预算耗尽的最后一轮动作分布为{'plan': 27, 'final answer:entropy_threshold': 34, 'tool': 23, 'summary': 1, 'thought': 8, 'parse_failed': 4, 'backtrack': 2}，这是最后一步的分类，不表示之前从未提出过答案。协议有效净减少97题（-25.26个百分点）：107条原有效变无效、10条原无效变有效；原生有效净减少88题（-22.92个百分点）：104条原有效变无效、16条原无效变有效。

仅异常恢复不包含完整typed版的熵/最小步数拒绝反馈、剩余轮数提醒及确定性转换，不能把它当成在完整修复基础上额外增强的版本。结果支持：本批输入上，仅靠异常恢复未保留完整修复的有效率收益，直接损失主要表现为预算耗尽；不把几项反馈的独立因果贡献混为已经分别验证。此轮没有修改新候选、扩预算、放宽门槛或丢弃无效题。

<a id="record-0170"></a>

## 22.4 轨迹、采样、成本与证据

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第983行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 22.4 轨迹、采样、成本与证据

全部2605次模型/token身份与实际消息检查、2012次全词表熵状态重算、748次接受边界、99次预算耗尽不冒充答案、34次记忆移除/状态恢复、48次预算内输出纠正继续、51次异常反馈审计通过。启动前候选边界及种子匹配检查通过。相同输入/阶段且消息完全一致的753对实际请求均保持与第20节相同seed，其中383对token序列相同；其余存在连续批处理数值/生成差异，因此不声称逐token等价。

本次2605次任务生成全部新计算，10,458,615输入tokens、295,319输出tokens，检索772次；旧阶段复用0、失败请求0、运行重试0、额外scoring forward0，3次生成长度截断保留。新空检索缓存仅允许本轮内部复用，实际命中及后端调用逐卡见最终报告。相同输入的两轮生成总计均独立保留。

- [最终结果与逐卡成本](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/final_results.json)、[同384题对照/转移/种子检查](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/paired_comparison.json)
- [完整预测](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/predictions.jsonl)、[逐题原生有效率](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/native_validity_rows.jsonl)、[执行/资源交接](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/execution_handoff.json)
- [最终轨迹审计日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/final_audit.log)、[同题对照日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/comparison_audit.log)、[监督日志](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/supervision.jsonl)
- [GPU2失败启动](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/gpu2_launch_failure.json)、[用户授权GPU0接续](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/gpu0_retry_launch.json)、[运行包与复核入口](/home/data3/txy/docs/baselines/tcrag.md#record-0401)

离线复核：在运行包使用既有HF虚拟环境Python依次运行code/monitor_fresh.py --final和code/compare_384.py，无新增模型调用。GPU0/1/3本次模型进程均已退出；最终快照GPU0恢复原10,198MiB占用，GPU1/3各约4MiB，GPU2仍为其他用户训练约36,857MiB。其他用户进程未停止，原M6/M7全量队列与保存点保持暂停。

<a id="record-0171"></a>

## 23. 完整第二版设为 M7 当前主要方法（2026-09-13）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第997行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 23. 完整第二版设为 M7 当前主要方法（2026-09-13）

用户明确指定完整第二版为当前主要方法。当前 M7 指第19/20节的 typed-control-v2：同时保留动作解析恢复、预算内最终格式纠正、熵/最低步数拒绝反馈、剩余预算提醒、按题型反馈及确定性已接受答案表示转换。Qwen3-8B、关闭thinking、max_loop=8、topK=4、sigma=1.2及原熵接受规则保持不变。定位为“TC-RAG复现修复＋本项目额外优化”；原始版和仅异常恢复版留作对照，不再按文件更新时间选择主方法。

实际当前入口：results_v5_m6_m7/m7_current -> m7_repaired_fresh（相对符号链接）。默认使用该目录的 code/methods.py、code/normalize_accepted.py 和 configs/tcrag_vllm.json，版本 iterative-v4-tc-typed-control-v2-vllm；其 launch.sh 的 m7_vllm 模式调用已验证vLLM运行入口，m7模式保留HF对照。后续新评测显式指定新输入清单及独立 --run-dir，不能向既有384题试跑目录追加，也不能将旧版1646条终态混作第二版全量结果。

切换前按字节核对部署方法与 candidate_typed.py、normalize_accepted.py 完全一致；当前链接解析及配置版本核对通过。此次仅设定主方法及文档入口，新增推理0、未启动/恢复任何队列、未改写历史代码配置或结果。

采用依据：开发100输入99/100协议有效；同384输入独立生成中，完整第二版366/384（95.31%）协议有效、290/384（75.52%）原生有效；仅异常恢复版269/384（70.05%）和202/384（52.60%）。同题试验存在批处理数值及后续提示差异，组合收益不等于各组件独立贡献已经验证。当前无第二版13,905题全量结果。具体试跑证据见第20、22节。

<a id="record-0172"></a>

## 24. M7 完整第二版 v5 全量运行（2026-09-13 21:59，已启动）

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第1010行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 24. M7 完整第二版 v5 全量运行（2026-09-13 21:59，已启动）

用户选择开发集99/100协议有效的完整第二版，对全部v5重新推理，沿用每五分钟进度、有效率、失败和GPU0–3报告。使用第23节当前主要方法，方法源码与candidate_typed.py、normalize_accepted.py逐字节一致；99%是开发100题结果，不当作全量承诺。此前384题全新生成格式95.31%、原生75.52%。

本次13,905独立输入，保留15,616原生评分映射、6,104选中单元、13,000选中判定。输入仅含ID及可见问题/选项/证据/答案格式，按seed20260917洗牌为109份，每份128题（最后81）。不复用旧预测或阶段请求；新空检索缓存允许本次内部查询复用。派生seed时仅把检索目录映射回第20节的路径，实际收据与缓存身份使用新路径，保持相同提示的历史种子。输入包含已有开发/试跑输入，不能将全库称为从未使用的独立测试集；最终另列开发/试跑之外的有效率。

GPU0已获用户前序授权；GPU2当前其他用户训练占36,857MiB，因此使用GPU0/1/3，保留所有其他进程。Qwen3-8B、BF16、vLLM0.8.5 V0、FP32采样/全词表熵、温度0.7、2048输出、131072上下文、8步、topK4、sigma1.2均沿用第二版。每卡64输入线程、70%显存、128最大序列、16384实际prefill预算。复用M4的文件锁动态分片领取模式，每卡一个常驻模型/检索器，单题沿用已验证run_item，逐题落盘、分片内审计。未加入CF/WM或约束解码；第23节所述额外控制优化属于本方法。

运行包：/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full。启动命令bash launch_gpu.sh 0/1/3；tmux socket m7-typed-v5-full。logs/gpu*.log、jobs/、runs/保存实际进度，reports/status.json和supervision.jsonl每五分钟记录累计/本次新增/复用/剩余、协议/格式/原生有效率、无效原因、运行失败和GPU0–3显存/利用率。code/monitor.py --watch在全覆盖后自动运行原生评分及逐分片轨迹审计，输出RESULTS.md、reports/final_results.json及scores/。旧1646题保存点与两轮384题试跑独立保留。

准备期间首次数据读取使用str.splitlines误拆题目内Unicode行分隔符而报JSON解析错误；改用既有JSONL逐文件行读取方式成功，无推理发生、未改变题目。

21:59启动GPU0/1/3及独立监控窗口；方法边界、确定性规范化、13,905输入覆盖/109分片领取及三个实际阶段seed匹配检查通过，证据reports/prelaunch_checks.log。启动前GPU状态与时间reports/launch.json。

22:03三卡已完成初始化并进入连续批处理，GPU0/1/3快照利用率均100%，运行请求约64/卡。最终评分补充与旧五方法相同的ALL去重单元聚合，并自动生成六方法分组柱状图（旧方法颜色保持，M7棕色）；完整13,905/15,616/6,104/13,000分母与类别单元数自动核对。补充开发/旧运行/优化/384试跑外输入有效率，作为描述性分层。code/full_report.py在监控完成后运行，图与比较表留在本包reports/，不覆盖旧五方法报告。仅重载CPU监控进程，无中断三卡推理。

22:06首个完整分片chunk_001（GPU1）审计通过：128新输入、120协议有效、8无效、0失败，推理326.74秒；848次新生成、640次熵重算、235次接受边界、172次反馈、15次确定性表示转换、6次预算内继续及1次预算耗尽均核对通过，旧LLM复用0。证据runs/chunk_001/execution_report.json与reports/first_chunk_audit.log。

22:30阶段记录：1,777/13,905新输入（12.78%），协议97.92%、格式97.81%、原生77.72%，0单题失败/重试/旧生成复用。协议无效37，另有2个多义诊断在原生格式检查判无效，357个诊断未映射；因此协议有效与格式有效须分开报告。完成12分片，三卡继续，GPU0/1/3占用约85.8/75.6/75.8GiB。五分钟原始状态持续写入reports/supervision.jsonl。

22:51在最终汇总执行前发现并修正一处离线断言：13,000是selected_targets中的合格具体判断数，不能当作原生非参考映射数；15,616评分映射实际包含6,818参考、8,798非参考。改为分别核对selected_targets.jsonl.gz的13,000行及原生映射数，并保留6,104唯一单元的ALL聚合。数据核对通过，未改变任何推理输入、方法、输出或评分规则，也未中断三卡。

23:00一小时进度：3,453/13,905（24.83%）全部新生成、26完整分片；协议97.71%、格式97.54%、原生77.47%，0单题失败/重试/旧阶段复用，22预算耗尽、38生成长度截断。22,184次生成、88,098,328输入tokens、2,426,436输出tokens。GPU0/1/3健康继续，原队列仍暂停；实时状态reports/status.json，进程与自动完成入口reports/execution_handoff.json。

2026-09-14 00:00两小时进度：6,776/13,905（48.73%）全部新生成、52完整分片；协议97.55%、格式97.33%、原生78.73%，0单题失败/重试/旧阶段复用。43预算耗尽、81生成长度截断。43,537次生成、175,283,697输入tokens、4,763,087输出tokens。GPU0/1/3继续运行，最新交接已更新。

00:01最终作图依赖检查发现HF评分环境和系统Python均无matplotlib；既有MedRGAG vLLM环境具备matplotlib3.10.9/numpy1.26.4，中文字体文件存在。最终流程改为HF Python运行monitor.py --watch（原生评分/轨迹审计），随后使用/home/data3/txy/MedRGAG/.venv/bin/python运行code/full_report.py（比较表/图/最终文档）。仅重启CPU监控窗口，日志追加，三卡模型进程未改动；无依赖安装或推理变化。此前尚未执行最终作图，缺失依赖在完成前处理。

2026-09-14 01:00三小时进度：10,045/13,905（72.24%）全部新生成、78完整分片；协议97.38%、格式97.16%、原生78.39%，0单题失败/重试/旧阶段复用。69预算耗尽、139生成长度截断。64,517次生成、263,486,075输入tokens、7,079,246输出tokens；三卡模型持续常驻，GPU0/1/3仍健康。实时状态与交接已更新。

<a id="record-0173"></a>

## 24.1 全量完成与最终结果

来源：[Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md](/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)，原文第1041行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 24.1 全量完成与最终结果

2026-09-14 02:10：M7完整第二版全量13,905/13,905完成，协议97.43%、格式97.25%、原生78.45%，运行失败0；原生15,616映射、6,104唯一单元、13,000选中判定及全部轨迹审计通过。全部预测来自本次推理，旧预测复用0；运行内阶段复用0。推理总墙钟246.09分钟，分片执行归一化吞吐1138.08题/GPU小时。GPU0共享条件及初始化开销见机器可读timing。

| 类别 | 单元数 | 原生准确率 |
|---|---:|---:|
| R1 | 2866 | 31.44% |
| R2 | 79 | 29.11% |
| R3 | 733 | 28.92% |
| R4 | 13 | 30.77% |
| R5 | 3600 | 66.17% |
| ALL | 6104 | 49.43% |

记录中的旧终态、修复开发、优化及384试跑之外，11786题格式有效97.25%、原生有效78.48%；仅为已有记录的排除分层。全部无效/失败保留分母。最终结果及六方法图表：[RESULTS.md](/home/data3/txy/docs/baselines/tcrag.md#record-0403)，完整成本/轨迹检查：[final_results.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/final_results.json)，逐条、来源、R1–R5/ALL及配对评分：[scores](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/scores)，分层：[exposure_strata.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/exposure_strata.json)。旧试验、M6暂停状态及其他用户任务保留。

最终核对：89,341次模型/token身份及实际提示、68,522次熵状态重算、27,493次接受门槛、18,895次反馈、1,592次确定性表示转换、607次预算内输出纠正继续、1,199次记忆移除/恢复及86次预算耗尽审计全部通过。所有输入实际模型调用数等于5–8个执行步数；旧阶段复用0。总365,634,771输入tokens、9,756,641输出tokens；27,578检索请求，其中22,971实际后端调用、4,607本轮新缓存命中；173次长度截断保留，0请求失败/重试、0额外scoring forward。具体协议无效357=254非法选项键+86预算耗尽+4答案缺失/冲突+6关系不合规+3多选集合+2errors格式+2文档ID不合规；另26多义诊断造成格式无效、2,613诊断未映射造成原生无效。完整明细protocol_invalid_reasons.json和final_results.json。

六方法柱状图已目视核对：Y轴从0开始、旧五方法颜色保持、M7棕色、图中数值与完整评分表一致，PNG/PDF/SVG均生成。相关总览和五方法报告顶部入口已更新，旧五方法制品保留。已确认本次三个worker PID全部退出，最终GPU快照及执行交接见reports/execution_handoff.json；GPU0与GPU2的其他用户进程未操作。


2026-09-14补充：用户指定新版M6 MedGENIE v2完成全量13905新输入、15616原生映射；格式96.49%、原生77.32%、ALL48.02%、0失败。方法、全量运行、成本、验证和图表统一见[M6主记录](/home/data3/txy/docs/baselines/medgenie.md#record-0232)及[七方法最终结果](/home/data3/txy/docs/baselines/medgenie.md#record-0399)。此前完整第二版M7分数保持不变。

<a id="record-0181"></a>

## 3.2 TC-RAG

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第92行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 3.2 TC-RAG

| 组件 / 调整 | 实际控制流 | 与论文或上游的关系 |
|---|---|---|
| 栈及隔离 | 每题初始化不可删除的原题、状态100000和动作计数；Thought/Plan/真实工具材料进入活动栈 | 保留stack-based memory；并发输入、原题和变体不共享活动状态 |
| 工具 | 模型提出DOC_RAG查询，程序调用统一检索器并注入实际Observation | 统一MedCorp工具迁移；没有复制上游web/KG/NER异构工具系统 |
| 伪Observation | 原始模型响应完整保存，但模型生成的Observation及其后续内容在动作解析前截断 | 工具结果来自实际调用，不能把模型自行编出的Observation当检索证据 |
| Backtrack | 弹出栈顶，恢复下面栈项的状态；被移除内容及回退反馈仅留审计 | 按论文恢复记忆/状态；修复上游跨题state_value_list未清空及反馈重新入栈的问题 |
| Plan / Summary | 增加独立动作；Summary用模型总结**替换栈顶旧内容**，原题不能被移除 | 论文§5.1和算法包含这些操作，上游主执行器没有独立Summary分支；明确标为论文对齐补丁 |
| Summary状态快照 | 替换Thought后恢复下面栈项状态，再存Summary快照 | 本项目保持活动记忆/状态一致的记录约定；论文Summary伪代码未明确写出这项恢复，不能称原文规定 |
| 普通Thought | 保存真实熵，普通Thought不终止循环 | 沿用官方执行器；没有采用论文while伪代码中的低熵Thought钳制到sigma操作 |
| 过早结论 | 零基step<4时转Thought；若有Thought前缀，保留该前缀 | 修复早期适配丢弃前缀的问题，对齐固定执行器；达到topK后沿用上游Final Answer片段处理 |
| 接受结论 | 仅当零基step≥4且当前Final状态严格小于1.2时接受 | 最早第5次生成；topK=4不代表每次检索4篇；不是口头置信度判断 |
| 最大步数 | 第8步后没有合格结论则保留真实栈顶，记invalid / budget_exhausted | 不追加Direct或将Observation提升为最终答案 |
| 原生输出接口 | 英文动作说明及统一原生答案空间；熵接受后才调用共用 `final_json` 纯语法转换 | 任务接口适配；预算耗尽输出不经转换伪装成合格结论 |

状态数值不作为额外提示写给模型；模型下一轮看到的是当前活动记忆。回退和总结移除的文本可以在审计文件恢复，但不混回活动prompt。

<a id="record-0182"></a>

## 3.3 熵口径和后端调整

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第110行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 3.3 熵口径和后端调整

选择官方默认cuct路径。对生成处理器和采样变换之后、抽样之前的**完整词表scores**转FP32：

```text
p_t = softmax(scores_t.float())
h_t = -sum_v p_t(v) * ln(p_t(v) + 1e-10)
state = sum_{t in selected_positions} h_t
```

这是自然对数的逐token分布熵之和。排除已生成特殊token的位置，不把特殊token从词表分布删除后重归一化。保存生成token、逐token熵、选定位置、起点、匹配状态和聚合结果，不导出巨大的完整词表张量。

位置选择保留固定上游的实际规则：先过滤特殊ID，扫描 `range(len(tokens)-3)`；首次精确 `Thought` 后偏移2，或首次 `Final` 后下一token精确为 `Answer` 时偏移3；匹配失败从0开始。没有strip token前导空格，` Answer`可能不匹配。这是上游字符串/边界口径，不能写成“精确提取最终答案语义正文”。

原依赖torch 2.4.0 / Transformers 4.44.0升级为既有环境的2.6.0 / 4.51.3，以支持Qwen3；核对了原生成器保存的是处理器及warper之后的scores。生成时收集器不改变scores，移除了cuct控制流不使用的attention、其他指标及完整logits导出。主路径没有额外评分前向，没有top-k截断熵、单token NLL、口头自信度或更小评分模型。

同后端 `generate(output_scores=True)` 参考对照覆盖实际Llama和Qwen：token序列一致、熵最大绝对误差0、阈值判断一致。证据见 [Llama参考](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_v4/backend_reference.json)、[Qwen参考](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/backend_reference.json)。每次后端对照额外计2个真实请求；这是所测同引擎序列的结果，不是跨硬件逐bit等价声明。

<a id="record-0204"></a>

## 2026-09-13 v5 M6/M7 正式输入诊断试跑启动

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第306行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 2026-09-13 v5 M6/M7 正式输入诊断试跑启动

用户新授权先运行部分v5输入，检查原始M6/M7的兼容性与效率，可用GPU1/2/3。运行包：[results_v5_m6_m7](/home/data3/txy/docs/evaluation/v5.md#record-0404)。每方法12条：11来源各取可见字符长度中位输入，另加M20全库最长输入；选择未读取gold或模型预测。M6在GPU1/2各运行6条，M7在GPU3运行12条。只将两卡分层部署改为单卡完整模型副本，其余方法、阈值、阶段预算和原生评分沿用runtime_v4；没有增加CF/WM/adapter模块。源码复制至新包，旧结果和旧源码不变。单卡三个进程均通过真实模型熵参考核对（最大误差0），已进入正式输入推理。全量27,810方法输入评测尚未启动；试跑并不代表完整正式结果。实时状态及后续结果以新包制品为准。

<a id="record-0206"></a>

## v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第316行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

用户明确授权使用三张卡运行全量。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0407)。每方法13,905独立输入，其中12条修复试跑结果原样复用、13,893条新运行，覆盖6,104单元和13,000入选判断。每方法109个128输入分片（末片不足128）；GPU1/2优先M6，GPU3优先M7，优先方法队列领完后自动领取另一方法。GPU0不动。使用已验证的M6/M7上游兼容性修复，无CF/WM/adapter附加模块，权重、提示、轮数、阈值、检索与阶段预算保持试跑配置。合并方法15项测试及1项调度测试通过。

三个模型已进入真实推理，M7产生首条新有效终态，初始GPU1/2/3利用率约97–98%。tmux socket `v5-m6-m7-full`，会话gpu1/gpu2/gpu3/monitor。在formal目录执行 `python3 status.py`；`logs/supervision.jsonl`每五分钟记录GPU及进度。各分片完成后审计，最后一片触发完整汇总和原生评分，完成标记为formal/complete.json，最终报告为formal/RESULTS.md。健康进程勿重复启动或中断。

耗时估计纠正：先前4–7天偏乐观；按已完成两个M6分片和M7试跑吞吐分配三卡，直接投影约11天。该试跑非代表性且含最长输入，不是完工承诺，后续以全量滚动吞吐更新。

<a id="record-0207"></a>

## v5 M6/M7 提高并发后接续（2026-09-13 06:37）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第324行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### v5 M6/M7 提高并发后接续（2026-09-13 06:37）

用户要求提高正式测试的显存利用与吞吐。活动运行改为 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_fast/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0408)，tmux socket `v5-m6-m7-fast`，GPU1/2=M6每卡32线程/128000合批token，GPU3=M7每卡16线程/96000合批token。原 `formal/`三队列已停止，记录和缓存保留，勿重启。方法、权重、提示、预算、阈值及评分不变，执行参数单独覆盖以保留原请求缓存键/随机种子。

相同32条正式请求微基准：M6批量4→32 token吞吐83.47→96.69/s；M7批量4→16为37.81→44.65/s，增到32下降至40.18/s，因此选择不同并发。微基准使用128生成token，不直接当作完整方法加速比。方法与队列16项测试通过。接续已复用旧正式请求并无模型重放完整终态，一致性检查通过。SIGTERM后0.33秒内产生的4个M6人工关闭异常已保存原制品、明确记录并重排同输入，未按答案正确性筛选。新进度06:37 M6=44/13905，M7=70/13905，均无真实运行失败，显存约38.55/43.23/36.64 GiB。

在formal_fast执行 `python3 status.py`。监控与自动审计/全量评分继续，新结果最终写入formal_fast/RESULTS.md。每五分钟向用户报告两方法累计、新计算、剩余及GPU0–3显存/利用率。

<a id="record-0208"></a>

## v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第332行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

当前活动目录 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/README.md](/home/data3/txy/docs/evaluation/v5.md#record-0409)，tmux socket `v5-m6-m7-balanced`。单纯提高批量在正式混合长度请求上造成大量补齐与长尾等待，实际M6约37–44、M7约10 token/s，不能称全量提速。相同28请求分组微基准40.31→33.16秒、88.91→108.08 token/s；有效输入补齐量减少31%。因此按原生答案类型、生成阶段、token长度2倍区间合批，并把等待池提高至M6每卡64、M7每卡32，token上限保持128000/96000。模型、方法预算和阈值不变；batch_group不进入prompt、缓存键或随机种子。17项测试通过。

接续无模型/检索重放原M6 32条、M7 68条正式终态，输出和状态一致；加上各12条试跑后进度M6=44、M7=80。原成功阶段收据全部保留复用，未完成响应重算。本次先冻结调度器再终止模型，没有产生新的关闭异常。formal与formal_fast为历史目录，勿重启；源结果、先前4条人工关闭异常和递归成本链完整保留。五分钟报告、自动审计和全量评分继续在formal_balanced执行。

<a id="record-0210"></a>

## M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第344行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

正文与[已合入记录](#record-0069)相同，统一在该处维护。

<a id="record-0211"></a>

## M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第350行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

正文与[已合入记录](#record-0072)相同，统一在该处维护。

<a id="record-0212"></a>

## 64路观察完成，三卡恢复32路（2026-09-13 11:58）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第356行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

正文与[已合入记录](#record-0073)相同，统一在该处维护。

<a id="record-0221"></a>

## 11. M6/M7 vLLM 优化、失败重试与完整流程验证

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第442行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 11. M6/M7 vLLM 优化、失败重试与完整流程验证

2026-09-13 20:00（Asia/Shanghai）完成。M7 同32题完整方法墙钟提速 **15.58倍**；M6/M7 均完成128题规模验证。最终收据见 [full_method_results.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/full_method_results.json)。GPU1/2/3已释放。

本包承接[吞吐诊断](/home/data3/txy/docs/workspace.md#record-0213)，在独立目录优化既有 iMedRAG / TC-RAG 执行。原 `formal_balanced` 的 M6 52 条、M7 1,646 条保存点和暂停队列不变。使用 GPU1/2/3，GPU0 未操作。这里是预选输入的完整方法验证，不是全量 13,905 题结果。

<a id="record-0227"></a>

## M7 有效率口径核对（2026-09-13，优化后追问）

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md)，原文第514行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### M7 有效率口径核对（2026-09-13，优化后追问）

用户询问为何有效率低。将原暂停点1,646条使用与优化试验相同的冻结v5原生评分入口离线重算：协议1,026/1,646=62.33%，原生776/1,646=47.14%；新128题协议81/128=63.28%，原生54/128=42.19%。过去简写的“有效”主要指协议有效，不能与现在原生有效直接比较。新旧不是同一批输入，不能把原生相差4.96个百分点归因于vLLM；已有同32题对照原生14/32→19/32，也不支持“加速必然降低有效率”。

新128题的74条原生无效可完整拆为：27条诊断未映射、25条八步预算耗尽、20条被接受但选项键不符合协议、2条动作解析失败。20条选项错误中9条普通单选、11条robustness_single；实际例子包括要求E却输出“E. Obstruction of the cystic duct”，也包括“None of the options provided”，不能将全部20条都当作可无歧义格式修复。36条诊断仅6条原生有效；旧411条诊断也仅90条有效，诊断映射困难是既有问题。

证据：[按题型与原因拆分的重算结果](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/optimization_vllm/reports/m7_validity_comparison.json)。本次只读预测、离线核对，没有改写答案、放宽阈值或启动模型。

2026-09-13 后续：M7第二版控制/输出修复已在新384题上从头验证，记录统一维护于[实施记录第20节](/home/data3/txy/docs/baselines/tcrag.md#record-0157)。旧优化试验保留历史口径。


2026-09-13 21:59：用户指定完整第二版M7全量v5，GPU0/1/3已启动13,905输入新生成；方法、调度、监督和最终结果统一续写[评测主记录第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)。旧M6/M7队列继续暂停。

2026-09-14完成：完整第二版M7全量13,905新输入及15,616原生评分映射全部完成，109分片轨迹审计通过；最终结果、成本与无效原因仍统一在[主记录第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)，比较图表见[完整结果](/home/data3/txy/docs/baselines/tcrag.md#record-0403)。本轮GPU0/1/3进程已退出，旧M6/M7队列继续暂停。

<a id="record-0383"></a>

## M7 TC-RAG真实运行

来源：[Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/acceptance_report.md)，原文第45行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### M7 TC-RAG真实运行

运行目录[runs/tcrag_dev](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev)。24/24终态：9有效、15无效、0失败、0待运行、0未知ID、0重复；有效率37.50%。12条动作解析失败（9条缺动作标签、3条空Thought），3条达到8步上限。实际动作数平均6步、中位6步、范围3–8步；40次真实检索、3次自然Summary替换、0次自然Backtrack。Backtrack完整行为已由固定响应测试验证，未强制模型额外触发动作。

44次Final Answer提议中，17次因步数过早拒绝，18次因熵阈值拒绝，9次接受。全部97次状态计算的熵和中位数22.38、p95=60.04、范围0.0121–109.88；逐次值、选定token位置、栈前后和阈值均可重算。sigma固定1.2，没有校准。审计通过144次实际prompt/活动栈检查、97次熵重算、44次接受边界、3次Summary移除及状态恢复、3次耗尽不提升为答案检查。见[执行审计](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/execution_report.json)、[逐题终态](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/predictions.jsonl)。

MedQA 12条中3有效、6条动作解析失败、3条耗尽；MedEinst 12条中6有效、6条动作解析失败。按完整来源分母的旧评分器：MedQA为2/12，MedEinst canonical为0/12；后者6条运行有效答案全部未进入既定canonical映射，不等同于语义答错。完整[离线结果](/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/scores/summary.json)保留这些区别，未修改gold、映射、阈值或提示来提高分数。

实际144次模型请求、354715输入token、18918生成token；40次检索中34次访问后端、6次同查询缓存命中。输出截断、无命中和传输重试为0；预算耗尽率12.5%。全程2792秒（46.53分钟），吞吐30.95输入/小时，单题延迟p50=476秒、p95=787秒；合批行数中位3、最大4。这里的吞吐包含失败解析及早停输入，不是保证得到有效答案的吞吐，也不用于宣称TC-RAG一定更快。熵参考对照的2个请求另计。

<a id="record-0400"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh`。

### M7 修复版全新384题试跑

主记录：[实施、启动和最终结果](/home/data3/txy/docs/baselines/tcrag.md#record-0157)。

inputs/all_384.jsonl与plan.json固定样本；configs/tcrag_vllm.json固定运行配置；code/methods.py为已验证的第二版修复原文件。GPU1–3各128题，64线程/卡。所有LLM与首次检索从头计算。

复现：在本目录执行 bash launch.sh 1 m7_vllm --inputs inputs/gpu1.jsonl --run-dir runs/NEW_GPU1 --workers 64，其他卡同理；使用新输出目录。各run保存code_snapshot、配置、原始响应和轨迹，logs/保存完整日志。

试跑已完成，主文档第20节保存最终结论；机器可读结果见[final_results.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_repaired_fresh/reports/final_results.json)。离线复核运行上述HF虚拟环境的Python执行 `code/monitor_fresh.py --final`。

<a id="record-0401"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh`。

### M7 最新仅异常恢复版试跑

主记录：[第22节：版本、运行与结果](/home/data3/txy/docs/baselines/tcrag.md#record-0166)。与前次完整typed版使用同384题，从第0步重新生成；所有旧输出保留。

运行命令：`bash launch.sh 1 m7_vllm --inputs inputs/gpu1.jsonl --run-dir runs/NEW_GPU1 --workers 64`，其余卡同理。

状态：使用既有HF虚拟环境Python执行 `code/monitor_fresh.py`；全部完成后 `code/monitor_fresh.py --final` 做轨迹与原生有效率审计。配置、输入、预测、日志分别位于configs/、inputs/、runs/、logs/。

试跑已完成。最终汇总见[final_results.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/final_results.json)，同384题对照见[paired_comparison.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_recovery_only_fresh/reports/paired_comparison.json)。原GPU2启动失败保留在runs/gpu2；同分片已按用户指令在GPU0完成，成功结果为runs/gpu2_retry。

<a id="record-0402"></a>

## README.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/README.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full`。

### M7 typed-control-v2 full v5

主记录：[第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)。

从本目录运行 `bash launch_gpu.sh <0|1|3>`。监督与自动完成：既有HF环境Python执行 `code/monitor.py --watch`。

全部13,905输入重新生成；冻结配置configs/tcrag_vllm.json，任务jobs/，逐题输出/请求/轨迹runs/，五分钟状态reports/status.json。最终RESULTS.md和scores/。

最终作图/汇总使用 `/home/data3/txy/MedRGAG/.venv/bin/python code/full_report.py`；评分与轨迹审计仍使用HF环境。两个步骤已在tmux监控窗口串联。

<a id="record-0403"></a>

## RESULTS.md

来源：[Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/RESULTS.md](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full`。

### M7 完整第二版 v5 全量结果

2026-09-14 02:06推理完成，02:11完成评分与109分片轨迹审计。推理总墙钟 **4小时6分5秒**（含初始化），0单题运行失败、0旧预测/阶段复用。

全部13,905输入新生成；协议、格式及原生有效率分母均为独立输入，完整评分保留15,616条原生映射。

| 有效率 | 比例 |
|---|---:|
| 协议有效率 | 13548/13905 = 97.43% |
| 格式有效率 | 13522/13905 = 97.25% |
| 原生有效率 | 10909/13905 = 78.45% |

| 类别 | 单元数 | 单元平均准确率 |
|---|---:|---:|
| ALL | 6104 | 49.43% |
| R1 | 2866 | 31.44% |
| R2 | 79 | 29.11% |
| R3 | 733 | 28.92% |
| R4 | 13 | 30.77% |
| R5 | 3600 | 66.17% |

配置、成本、轨迹审计及无效原因见 reports/final_results.json；原生逐条与来源、配对评分见 scores/。

![方法分组柱状图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/v5_grouped_methods.png)

六方法比较见 reports/category_comparison.csv；开发/试跑以外的有效率见 reports/exposure_strata.json。

导出：[PDF柱状图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/v5_grouped_methods.pdf) / [SVG柱状图](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/v5_grouped_methods.svg)。R4仅13个单元。开发100题的99%是开发结果，本次全量格式有效率为97.25%。

持续主记录：[第24节](/home/data3/txy/docs/baselines/tcrag.md#record-0172)。配置：[tcrag_vllm.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/configs/tcrag_vllm.json)；具体无效原因及步数：[protocol_invalid_reasons.json](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/reports/protocol_invalid_reasons.json)；全量来源/类别/配对评分：[评分汇总](/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m7_typed_v5_full/scores/summary.json)。
