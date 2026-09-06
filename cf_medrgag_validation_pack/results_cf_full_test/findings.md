# MedRGAG-Llama 基础版：五入口完整测试结果

状态：**完成并通过验收**。2026-09-07 05:16:18 CST 推理完成，05:17:09 首次完整分析完成。本轮最终要求只有 M2；共完成 25,280/25,280 个唯一输入，对应 27,377 条评价记录。旧 M0/M1 各 5,832 条仅作为历史辅助记录保留，不构成全测试集对照。

## 数据范围和完成率

| 入口 / 协议 | 完成源题组 / 计划 | 全部评价记录 | 唯一输入 | 完成率 |
|---|---:|---:|---:|---:|
| MedEinst 官方 test，原生诊断 | 5,383/5,383 | 10,766 | 10,755 | 100% |
| MedPIC，原生多选 | 467/467 行级单元 | 467 | 467 | 100% |
| CPV-MedQA，全部变体及真实原题 | 1,202/1,202 | 13,512 | 11,427 | 100% |
| Cultural-Cues，全部原题及发布变体 | 150/150 | 1,500 | 1,499 | 100% |
| MedCounterFact，原题及全部发布替换 | 203/203 | 1,012 | 1,012 | 100% |
| MedEinst 冻结四选项辅助敏感性 | 60/60 | 120 | 120 | 100% |

五个入口的原生数据均为完整发布范围；最后一行是预定辅助协议，不是第二个 MedEinst benchmark，也不是全 test 的四选项转换。CPV 包含 12,310 个变体和 1,202 个真实原题。Cultural 附带的 1,273 条 MedQA 原题文件用于来源映射，作者实际发布的增强评估集是 150 组。数据 revision、下载路径、字段检查见 [acquisition.md](acquisition.md)、[data_checks.md](data_checks.md)；推理输入与标签保持分离。

## 实际基础调用链

采用本地 `medrgag_llama_base`，不是 exact published SOTA reproduction。复用 `run_cfshift.py::run_baseline` 所指向的 `run_gate_b.py::run_m2` 基础实现及 MedRGAG prompt/retrieval helpers，由 `scripts/run_cf_baseline_screening.py` 调度：

Textbooks/Wikipedia 各 BM25 32 候选 → MedCPT 排序取初始 5 文档 → 5 次 KGCC 摘要 → 3 个缺失知识点 → 5 次补充文档生成 → 原始 KADS 从 10 候选选最多 5 个 → MedCPT 最终排序 → 原始任务适配 JSON reader。

Llama checkpoint/tokenizer：`/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`，BF16，原 chat template。MedCPT：本地 `ncbi-MedCPT-Cross-Encoder`，FP32、pair max_length 512。Llama 上下文容量 98,304；摘要/探索/生成/KADS/reader 上限分别为 64/1,024/256/2,048/64 tokens。生成 T=1.2、top_p=.9、top_k=50、presence_penalty=1；其余阶段 T=0。完整参数与各实际函数在 [baseline_contract.md](baseline_contract.md)。与论文混合模型配置的差别是全部生成/reader 均用本地 Llama，并为开放诊断、多选、证据比较作最小 I/O 适配；没有声称远端 checkpoint revision 已核实。

MedCounterFact 顶层问题和完整 article_summaries 在各必要阶段保留，不由 KADS 删除。原题/变体独立推理，输入不含 gold、配对正文、role、taxonomy。没有启动 Profile/DDX、CFShift scorer、CFMoE/sidecar、Qwen、反事实生成方法、gate/adapter、judge、训练或全选项似然评分。缓存记录只包含基础摘要、探索、生成、选择、reader 和检索/排序阶段；M2 的 13 次 LLM 调用预算逐输入验收通过。

## M2 原生结果

分数按源题组先平均；micro 分数另列。区间为 2,000 次源题组 cluster bootstrap。

| 数据集 | 源题平均分数 | 95% CI | Micro 分数 | 正确评价记录 / N |
|---|---:|---|---:|---:|
| MedEinst canonical match | 8.26% | [7.76%, 8.75%] | 8.26% | 889/10,766 |
| MedPIC exact-set | 30.84% | [26.77%, 34.90%] | 30.84% | 144/467 |
| CPV-MedQA accuracy | 67.09% | [64.89%, 69.35%] | 67.20% | 9,080/13,512 |
| Cultural-Cues accuracy | 66.13% | [60.60%, 71.80%] | 66.13% | 992/1,500 |
| MedCounterFact evidence agreement | 66.50% | [60.59%, 72.12%] | 66.50% | 673/1,012 |

MedEinst raw-exact 为 5.49%，canonical match 为 8.26%。7,749/10,766（71.98%）条诊断未映射到冻结官方标签清单，另有 68 条歧义诊断。未映射不等于 JSON 格式错误，也不能据此断言全部为医学语义错误；此处是确定性规范化匹配 screening，不是作者官方语义 evaluator。未按结果增加同义词或调用 judge。

MedPIC option F1：micro 49.96%，macro 46.77%；平均预测集合大小 1.486，真实集合大小 1.343。GF 为 104/284（36.62%），CF 为 40/183（21.86%），差 14.76 pp，CI [6.63,22.90] pp。这是 **unpaired_composition_gap**，没有恢复或编造官方配对。

MedCounterFact 输出分布：higher 317、lower 376、no difference 304、uncertainty 15；uncertainty 为合法输出，单独计数。EA 不与临床 accuracy 平均，也不解释为临床安全性。

## 配对变化和错误结构

正 drop 表示原题分数高于变体。多变体先源题内平均，避免变体多的题权重更大。

| 原生数据集 | 配对数 / 源题组 | 原题分数 → 变体分数（源题平均） | Drop | 95% CI |
|---|---:|---|---:|---|
| MedEinst | 5,383/5,383 | 9.16% → 7.36% | +1.80 pp | [0.74,2.86] pp |
| CPV | 12,310/1,202 | 67.39% → 67.06% | +0.33 pp | [-1.34,2.08] pp |
| Cultural | 1,350/150 | 66.00% → 66.15% | -0.15 pp | [-5.56,5.11] pp |
| MedCounterFact EA | 809/203 | 67.00% → 66.38% | +0.62 pp | [-3.33,4.68] pp |

MedEinst 规范化匹配下降的 McNemar p=.000988，预定 native 比较族 Holm 修正后 p=.02864。其余三个整体配对效应区间包含 0；这不证明完全相同或等价，也不支持“所有 benchmark 都下降”。MedPIC 的非配对差不能与上述 drop 混用。M0/M1 未完成全量，按用户最新要求不报告跨方法 amplification 或归因于检索的额外效应。

MedEinst 四格 n11/n10/n01/n00 = 19/474/377/4,513；pair accuracy 19/5,383=0.35%。原题正确的 493 对中，变体正确 19 对，仍输出旧 gold 的 199 对，BTR=199/493=40.37%。这区分了正确换诊断、旧答案持续和其他错误，不能把全部 474 个变体错误都叫作不更新。CPV、Cultural、MedCounterFact 的 raw pair conditional failure 分别为 1,005/8,310=12.09%、138/891=15.49%、57/542=10.52%；完整变化/稳定错误与 invalid 分开保存在 [transitions.csv](transitions.csv)。

Cultural 跨文化汇总中，相对 Original 的 Id、Context、Id+Context drop 分别为 +0.89、-2.44、+1.11 pp，各自区间均包含 0；不存在可用 Neutral 条件。文化与官方操作切片在 [category_metrics.csv](category_metrics.csv)、[paired_effects.csv](paired_effects.csv)。

## 格式和预定敏感性

冻结 60 对四选项辅助结果为 66/120=55.00%，control/trap 为 50.00%/60.00%，drop=-10.00 pp，CI [-28.37,8.33] pp。同一 60 对的原生结果仅 7/60 和 2/60；四选项减原生的差分别为 +38.33 pp（CI [26.67,51.67]）和 +56.67 pp（CI [45.00,68.33]）。这种巨大协议差异限制了 MedEinst 的解释；不能用派生选项结果替代完整原生 test 结论。

MedEinst 历史曝光 3,849 组，历史未匹配到叙述的 1,534 组。两组 canonical 分数为 8.37%/7.99%，配对 drop 分别 +2.13 pp（CI [.91,3.43]）和 +.98 pp（CI [-1.04,2.93]）。未称后者严格 pristine。排除发布集中 11 个“输入完全相同而 gold 不同”的病例后，5,372 组 drop 为 +1.79 pp（CI [.69,2.83]），主分析仍保留全部官方行。

去除 CPV/Cultural 的 142 个跨资源共享来源映射后，CPV 保留 1,060 组、drop +.06 pp（CI [-1.80,1.95]）；Cultural 仅余 8 组，区间很宽，不能作独立来源复现证据。CPV 事前质量标记阴性且组完整的 920 组 drop +.69 pp（CI [-1.35,2.77]）。这些敏感性按预定规则全部报告，不挑选最好结果。

固定 20 个输入的独立 seed 辅助复测完成；19 个双有效输出中语义 flip 7/19，raw response 变化 10/20。该样本继承自早期 screening，不是全 test 的新随机样本，不选最佳 seed、不集成、不从主分数中扣除随机变化。

## 类型可识别性与结论边界

MedEinst 属于临床更新；MedPIC 为 guideline-following/临床患者信息改变任务，但缺正式 pair map。CPV/Cultural 属于答案应保持的身份/文化变换；MedCounterFact 属于假设证据世界。这三类评价语义不合并成总体 CF accuracy。

完整 coverage 表已冻结并保留。临床更新与假设证据世界的设计矩阵秩不足；身份/文化域在 MedQA 构造内部满秩，但 CPV 和 Cultural 同源，无法验证独立临床来源的类型规律。三域跨独立来源 taxonomy 均为 **NOT_IDENTIFIABLE**。没有删除 dataset 控制、靠正则化强造系数或因掉点重新分组；没有适用的独立跨源 ±5 pp 等价证据，leave-one-source 不可用。细节见 [taxonomy_identifiability.json](taxonomy_identifiability.json)、[explanatory_models.json](explanatory_models.json)。

本轮对“各数据来源的变化模式不同”提供部分描述性支持；不支持“所有数据集显著退化”，不能从当前结果证明 taxonomy、检索因果失败或临床危害。低 MedEinst canonical 分数尤其受开放输出映射协议限制。

## 成本、监控和验收

完整扩展批次从 2026-09-06 13:44:17 到 2026-09-07 05:16:18，makespan **55,921 秒（15 小时 32 分 01 秒）**，包含并发、受控重启和异常停机，不是 stage wall-time 之和。此前已完成的抽样批次约 4 小时 32 分钟，其 3,774 个完全相同输入/阶段被复用。本轮新增 21,506 个唯一输入；该 15.53 小时是已有缓存的扩展实测，不是从零无缓存的完整重跑耗时。

M2 主干共 328,640 次 LLM 调用；加保留的 M0/M1 11,664 次，共 340,304 次。再计固定复测及已作废 smoke/复测尝试 530 次，总记录 **340,834 次**，logical prompt tokens **449,853,293**，completion tokens **77,488,473**。扩展新增 283,694 次记录调用、350,655,816 prompt tokens、65,839,313 completion tokens。完全相同可见输入去重 2,097 条，按 M2 每题 13 次避免 27,261 次调用；没有跨反事实语义近似复用。

主推理使用 GPU0/2 的 NVIDIA H20（各约 97,871 MiB），检索预取曾使用 GPU1，vLLM 0.8.5，最终 batch/chunk64、GPU memory allocation .75；未停止其他用户进程。候选数/文档数/解码预算未为加速减少。后段把已完成奇数分片之外的 1,061 个输入按现有参数分成 531/530 两组，集合验收互斥且无遗漏。

KADS select 的已记录并发阶段批次时间累计约 55,308 秒，是主要 LLM 时间来源；生成约 27,794 秒，摘要约 21,288 秒，探索约 18,313 秒。它们包含已复用历史工作，不能相加充当本轮 makespan。原始预算到达 token 上限的次数：summary 58,136/126,400，generate 93,488/126,400，explore 73/25,280，select 1,273/25,280，M2 reader 1/25,280。未因此延长或缩短预算。prefix-cache 的 logical token 数不等于物理重算 tokens；本地 vLLM 接口没有返回可用 queue-time 指标。runtime cache-hit 计数仅覆盖各 worker 最新进程记录，历史精确复用另列。

20:31 左右旧任务进程曾退出，Luna 在 21:02 报告，主代理直到用户 21:30 询问才接手，存在监控响应延迟；没有错误地把这段时间记成有效推理。原因未证实，无 Python traceback，内核日志不可读。21:31 从已校验缓存恢复到独立 tmux，此后主代理持续检查 Luna 心跳并处理尾部分配，直到完整结束。受控容量/调度重启及该异常退出期间未返回的 tokens 不可测，已记录 totals 不含它们；不把估计上限当实际成本。原记录见 capacity_restart.json、throughput_restart.json、unexpected_exit_restart.json、tail_rebalance.json。

最后所有 source groups/输入完成，pending transport=0，网络重试=0，format repair=0。原生评价记录中格式/歧义 invalid：MedEinst 68、CPV 6、Cultural 1、MedPIC 4、MedCounterFact 0；MedEinst 未映射 7,749 另列。3 个合同/数据/指标测试通过；全量阶段 key、5/1/5/1/1 调用数、seed/config/token limits、文档缓存一致性、所有 gzip prompt 引用、全表配对恒等式通过。25,349 条检索记录中含 69 条重复缓存记录，重复的排序文档 ID/正文一致；LLM 阶段无重复 key。见 [artifact_audit.json](artifact_audit.json)、[validation.json](validation.json)。

原始 KADS/parser 最终选文档数：0/1/2/3/4/5 对应 2,561/10/28/37/130/22,514 个输入；10.13% 为空选择，仍执行全部 M2 阶段，没有事后填文档。一个后续值得检验的机制是：原始 KADS 输出/解析失配造成的空证据，是否与同源题的错误换答相关。本轮保存的是 association/proxy，不能证明因果；没有实施新 parser、gate 或方法。

## 可用性和交付

没有访问受限而跳过的核心入口。Cultural 的 Neutral 未发布；MedPIC 没有可验证官方 pair map；MedCounterFact 的 147/43/66 三个原题各缺一个发布变体类别，这些未发布记录不计模型失败。MedEinst/MedPIC/CPV 许可信息与另外两库未明确许可的情况见 acquisition；原始文本、模型权重、检索库与凭据不提交 Git。

[summary.md](summary.md) 是自动生成摘要；[benchmark_metrics.csv](benchmark_metrics.csv)、[paired_effects.csv](paired_effects.csv)、[statistics.json](statistics.json)、[efficiency.csv](efficiency.csv) 为机器可读结果。9 张实际数据图均导出 SVG/PNG，见 figures/；流程图保留 [flow.mmd](flow.mmd)，没有下载大型渲染环境。全部准备/运行/分析及审计命令在 [commands.sh](commands.sh)，阶段正文通过本地可恢复缓存引用保存。

开始代码 HEAD：`1e01b3a33c378041c64a76cce70ed381e4280d35`；全量扩展起点 `bc31166fcbca514138ae5db38ab4a73a4b2f3312`；完成时执行代码 checkpoint `8630dfc`，其后只修正 M2 计划计数元数据、补充验收和报告。最终交付 commit 由本目录 Git 历史及最终回复记录；未推送远端，用户原有未提交修改保留。
