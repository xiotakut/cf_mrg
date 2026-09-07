# 完整测试集：Direct / retrieval-only / MedRGAG-Llama 对照结果

**完成并验收。M0、M1、M2 各 25,280/25,280 个唯一输入，合计 75,840 条预测、82,131 条方法×评价记录。** 2026-09-07 19:29:22 CST 推理结束，19:31:50 离线分析结束。本次按用户要求补齐此前中止的 M0/M1，保留各 5,832 条旧预测，新增各 19,448 条。M2 和全部上游阶段逐字节复用。

## 完整发布范围

| 入口 / 协议 | 完成源题组或行级单元 | 评价记录 / 方法 | 唯一输入 / 方法 | 完成率 |
|---|---:|---:|---:|---:|
| MedEinst 官方 test，原生诊断 | 5,383 | 10,766 | 10,755 | 100% |
| MedPIC，原生多选 | 467 | 467 | 467 | 100% |
| CPV-MedQA，真实原题及全部变体 | 1,202 | 13,512 | 11,427 | 100% |
| Cultural-Cues，全部发布源题及变体 | 150 | 1,500 | 1,499 | 100% |
| MedCounterFact，原题及全部发布替换 | 203 | 1,012 | 1,012 | 100% |
| MedEinst，预定四选项辅助 | 60 | 120 | 120 | 100% |

五个入口原生协议均覆盖实际完整发布范围。四选项是冻结的 60 对辅助敏感性协议。CPV 包含 1,202 个真实原题和 12,310 个变体；Cultural 的 1,273 条 MedQA 原题文件是映射池，发布增强评估集为 150 组。此次沿用相同 revision、样本列表、opaque IDs、taxonomy、来源映射和历史曝光标记，没有重新抽样。来源及字段核对见 [acquisition.md](acquisition.md)、[data_checks.md](data_checks.md)。

## 同一模型和调用合同

本地 Llama-3.1-8B-Instruct，BF16、原 tokenizer/chat template，reader temperature=0、max_tokens=64、相同逐输入/阶段 seed；上下文容量 98,304。M0 使用完整合法任务输入；M1 使用同一输入加 M2 的首次 source-balanced BM25/MedCPT top-5 文档。MedCounterFact 必需题内证据和全部原生选项在两者中完整保留。

M2 继承已完成的基础链：两库各 BM25 32 候选 → MedCPT top 5 → KGCC 摘要 5 次及缺失知识探索 1 次 → 补充生成 5 次 → 原始 KADS 1 次 → 最终 MedCPT/reader。模型、采样预算、候选和文档数未改变。新增 `readers` 入口在 M0/M1 后返回，既有全部 M2 阶段与检索缓存无变化；无 Profile、CFShift scorer、CFMoE、sidecar、judge、训练或新方法调用。实际函数和参数见 [baseline_contract.md](baseline_contract.md)、[config.json](config.json)。这是 local all-Llama reproduction，与论文混合模型配置有别。

## 主结果与方法差异

下表为源题组内平均后跨源题平均。差异单位为百分点，95% CI 来自 2,000 次源题组 cluster bootstrap；完整分数区间、micro 分数和分母见 [benchmark_metrics.csv](benchmark_metrics.csv)。

| 原生入口 / 指标 | M0 Direct | M1 retrieval-only | M2 MedRGAG | M2−M0（pp；95% CI） |
|---|---:|---:|---:|---:|
| MedEinst / canonical match | 10.93% | 7.75% | 8.26% | -2.68 [-3.21, -2.07] |
| MedPIC / exact-set | 35.97% | 36.83% | 30.84% | -5.14 [-8.99, -1.50] |
| CPV-MedQA / accuracy | 61.59% | 63.78% | 67.09% | +5.50 [3.60, 7.34] |
| Cultural-Cues / accuracy | 62.53% | 61.53% | 66.13% | +3.60 [-0.60, 7.80] |
| MedCounterFact / EA | 66.31% | 61.87% | 66.50% | +0.20 [-1.97, 2.56] |

CPV 上 M2 高于 M0 和 M1；MedPIC 上 M2 低于二者。MedEinst 的规范化匹配中 M2 低于 M0，与 M1 的差异区间包含 0。Cultural 上 M2−M0 为 +3.60 pp，但区间包含 0；M2−M1 的区间下界为 0 附近。MedCounterFact 上 M2 与 M0 接近，M1 比 M0 低 4.43 pp（CI [−7.19,−2.07]），M2 比 M1 高 4.63 pp（CI [2.17,7.19]）。这些是各原生指标上的描述性比较，不合并成总体 CF accuracy。

MedPIC option F1 micro / macro：M0 49.53% / 46.73%，M1 51.26% / 47.59%，M2 49.96% / 46.77%。平均预测集合大小为 1.139 / 1.214 / 1.486，真实集合大小 1.343。exact-set 与 F1 的差异提示预测集合内容及大小都影响结果。GF/CF 和官方 operation 切片见 [category_metrics.csv](category_metrics.csv)；GF−CF 为非配对 composition gap。

## 原题到变体的变化

正 drop 表示原题分数高于变体；多变体先在源题组内平均。括号均为未作多重校正的 95% CI（pp）。

| 原生入口 | Pairs / groups | M0 drop | M1 drop | M2 drop | M2 drop−M0 drop |
|---|---:|---:|---:|---:|---:|
| MedEinst | 5383 / 5383 | +5.59 [4.38, 6.80] | +1.60 [0.58, 2.66] | +1.80 [0.74, 2.86] | -3.79 [-4.87, -2.69] |
| CPV-MedQA | 12310 / 1202 | +0.07 [-0.54, 0.68] | +0.58 [-0.38, 1.56] | +0.33 [-1.34, 2.08] | +0.26 [-1.49, 2.06] |
| Cultural-Cues | 1350 / 150 | +2.37 [-0.81, 5.41] | -0.22 [-4.07, 3.78] | -0.15 [-5.56, 5.11] | -2.52 [-8.37, 3.19] |
| MedCounterFact | 809 / 203 | +1.48 [-1.35, 4.43] | +3.94 [-0.25, 8.13] | +0.62 [-3.33, 4.68] | -0.86 [-4.43, 2.46] |

MedEinst 的 M2 drop 小于 Direct，但 M2 的总体 canonical 分数也更低，不能只凭较小 drop 宣称诊断更可靠。其余入口 M2 的整体 drop 及相对 Direct 的 amplification 区间均包含 0；这不证明等价。M1 的 amplification、各条件四格及分母完整保存在 [amplification.csv](amplification.csv)、[paired_effects.csv](paired_effects.csv)。

本次恢复三方法比较，预定 native Holm 检验族从旧 M2-only 报告的 29 项扩大为 87 项。MedEinst 的 M0/M1/M2 原始 McNemar p 分别约 1.11e−18 / .00308 / .000988，Holm 后约 9.69e−17 / .2616 / .08494。M2 原始预测、drop、CI 和未校正 p 均与旧报告相同，校正后 p 的变化来自比较族扩大。多变体整体不套用把每个变体视为独立源题的 McNemar 检验。

Cultural 相对 Original、跨文化平均的 Id / Context / Id+Context drop：M0 为 +2.00 / +1.56 / +3.56 pp；M1 为 −0.22 / −0.44 / 0.00 pp；M2 为 +0.89 / −2.44 / +1.11 pp。各自源题组区间均包含 0；完整条件及区间在 paired_effects.csv。

## 错误结构与输出合同

MedEinst 原生的旧答案持续 BTR：M0 622/739=84.17%，M1 219/460=47.61%，M2 199/493=40.37%。正确原题及正确变体的 pair accuracy 分别为 4/5,383、4/5,383、19/5,383。invalid 不自动计旧答案持续；未映射和歧义也不被挑选成碰巧等于 gold 的答案。

CPV 中，原题正确后变体出错的 raw-pair conditional failure 为 M0 131/7,590=1.73%，M1 353/7,925=4.45%，M2 1,005/8,310=12.09%；Cultural 为 7.22% / 8.45% / 15.49%。各方法“原题正确”集合不同；这些条件比例须与源题组分数及 amplification 同看。正确修正/保持、语义 flip、changed-but-wrong、stable-but-wrong 在 [transitions.csv](transitions.csv) 分开保存。

M2 相对 Direct 既修正错误，也引入新错误。下表 H 是模型答题错误变化，非临床伤害标注。

| 原生入口 | R：M0 错/M2 对 | H：M0 对/M2 错 | H / 全部记录 | H / M0 正确 |
|---|---:|---:|---:|---:|
| MedEinst | 328 | 616 | 5.72% | 52.34% |
| MedPIC | 29 | 53 | 11.35% | 31.55% |
| CPV-MedQA | 1714 | 957 | 7.08% | 11.50% |
| Cultural-Cues | 172 | 118 | 7.87% | 12.58% |
| MedCounterFact | 38 | 36 | 3.56% | 5.37% |

| 原生入口 | M0 格式/歧义 invalid | M1 格式/歧义 invalid | M2 格式/歧义 invalid |
|---|---:|---:|---:|
| MedEinst | 11 | 7 | 68 |
| MedPIC | 10 | 1 | 4 |
| CPV-MedQA | 17 | 0 | 6 |
| Cultural-Cues | 9 | 3 | 1 |
| MedCounterFact | 0 | 0 | 0 |

MedEinst 未映射诊断另列：M0 6,416/10,766（59.60%），M1 8,572/10,766（79.62%），M2 7,749/10,766（71.98%）；raw-exact 为 7.54% / 4.96% / 5.49%。未映射 JSON 诊断与 malformed output 不同，在冻结 canonical 协议中计错。MedCounterFact uncertainty 为合法输出：M0/M1/M2 分别 5/31/15 条；higher/lower/no-difference 分布完整保存在 metrics.json。

冻结 60 对 MedEinst 辅助中，四选项分数 M0/M1/M2 为 46.67% / 43.33% / 55.00%；相同病例的 native 分数为 11.67% / 5.00% / 7.50%。各方法 reference 与 variant 的四选项−native 区间均高于 0（见 [sensitivities.json](sensitivities.json)）。该协议差异很大，辅助题的选择和选项构造限制了外推，不能用四选项替代全 test 的原生诊断结论。

## 类型、来源与局限

MedEinst 是临床更新；MedPIC 是患者信息/指南推理的行级任务；CPV 和 Cultural 是答案应保持的身份/文化变换；MedCounterFact 是假设证据世界。三域跨独立临床来源 taxonomy 均为 **NOT_IDENTIFIABLE**。临床更新与假设证据域存在秩不足；身份/文化域仅在同源 MedQA 构造内部可估计描述性关系。CPV/Cultural 有 142 个跨资源源题映射，不能把它们当独立临床来源复现。来源映射、矩阵秩和探索模型在 source_overlap.json、taxonomy_identifiability.json、explanatory_models.json。

MedEinst 主分数是冻结标签规范化匹配，不是作者官方语义诊断评分；高未映射率及原生/四选项差异限制医学解释。MedPIC 缺可验证官方 pair map；Cultural 未发布 Neutral；MedCounterFact 的 147/43/66 三个源题各缺一个发布变体类别。完整发布集中的这些缺项不计为模型失败。MedCounterFact EA 不代表临床安全，也不与诊断 accuracy 平均。

预定曝光、质量标记、去除重叠源题、MedEinst 去除 11 个相同输入而 gold 冲突病例的敏感性全部保留；没有据结果删题或增加医学别名。固定 20 输入的 M2 独立 seed 复测沿用旧结果：19 个双有效输出中语义 flip 7/19，raw 变化 10/20；其早期样本不能代表全 test 的随机性，也未用于集成或分数校正。

## 本次成本、验收和交付

补跑时间为 2026-09-07 18:44:08—19:29:22 CST，makespan **2,714 秒（45 分 14 秒）**；离线分析再用 148 秒。使用 GPU0/2 的 H20、vLLM 0.8.5、BF16、batch/chunk 64、GPU memory .75。较快分片先正常退出，另一分片继续完成；推理没有重启，没有降候选数、文档数、token 上限或精度。Luna max 负责只读监督，主代理核对心跳、处理初期监控刷新问题并独立验收。

新增 **38,896 次 LLM 请求**，logical prompt tokens **33,914,033**、completion tokens **339,142**。M0/M1 各复用 5,832 条旧答案，M2 全部 25,280 输入及其 328,640 次主干 LLM 阶段记录复用。新增 M0 有 2 次到达原 token 上限，M1 为 0；保留原始输出并按同一规则评分，format repair=0，网络重试=0，pending/transport failure=0。

含旧缓存的三方法主运行共 379,200 次记录调用、481,617,579 prompt tokens、77,700,293 completion tokens；再计旧复测及作废尝试，共 379,730 次、483,767,326 prompt tokens、77,827,615 completion tokens。旧 M2 扩展批次的 15 小时 32 分钟及历史未返回 token 限制保存在 [prior_run_efficiency.json](prior_run_efficiency.json)，不计入本次 45 分钟。精确可见输入去重 2,097 条，逻辑上避免三方法主干 31,455 次请求。logical tokens 包含缓存前缀，不等于物理重算 tokens。

[reader_completion_efficiency.csv](reader_completion_efficiency.csv) 单列这次两个 reader 的调用、tokens、阶段时间和截断；[efficiency.csv](efficiency.csv) 包含所有已记录历史阶段。阶段时间并行重叠，不能相加作为 makespan。当前 reader 进程的 cache-hit 计数另存 [execution_provenance.json](execution_provenance.json)；metrics.json 还保留历史 worker-2 的 runtime，不把其旧 M2 命中计数误作本次新调用。接口未返回可用 queue time。

4 项合同/覆盖/指标测试通过；全量阶段 key/seed/config/budget、完整 durable prompt 引用、旧 reader 字节前缀和全部非 reader 缓存字节一致性审计通过。M2 导出预测、主指标和 paired 指标与旧结果完全相同。所有表的四格、drop、gain、OCP、source-macro 和 amplification 恒等式通过。见 [artifact_audit.json](artifact_audit.json)、[validation.json](validation.json)。

10 张实际数据图均有 SVG/PNG，见 [figures/](figures/)；流程图源码见 [flow.mmd](flow.mmd)。从仓库根目录执行 `bash cf_medrgag_validation_pack/results_cf_full_comparison/commands.sh` 即可依次 prepare/readers/analyze/audit，完整缓存下会跳过已完成推理。数据和模型资产要求与旧完整运行相同。原始 benchmark 文本、模型/检索库、凭据及大型正文缓存留在服务器，下载器、IDs、原生预测和派生结果按既有归档约定提供。

本次推理代码基于 commit `79a9454`，M2 来源结果 commit `638f1e3ad116ffdad609e74bb5a9f019a196911e`；本报告和脚本随最终结果提交，GitHub 独立快照列在仓库 `benchmarks/` 索引，保留旧 M2-only 快照。

## 研究判断

本轮支持“不同入口的表现及变化模式不同”的描述性结论；不支持统一退化或统一提升，也不能验证跨独立来源 taxonomy。一个后续值得检验的机制是原始 KADS 输出/解析造成的空证据，是否与 M2−M1 的错误换答相关。已有 2,561/25,280（10.13%）空选择及文档来源记录提供线索；当前只有 proxy/association，没有开展新的 parser、gate、judge 或因果实验。
