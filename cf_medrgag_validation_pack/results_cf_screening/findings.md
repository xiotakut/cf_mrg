# 五入口 baseline screening：结果解读与验收

**Scope clarification: completed sampled screening only, not the entire test sets. Full-release expansion is tracked in [results_cf_full_test](../results_cf_full_test/findings.md).**

本轮完整档已完成。结果支持“不同来源/任务格式下表现不同”，不支持“MedRGAG 普遍放大反事实敏感性”；独立跨来源 taxonomy 效应不可识别。以下结论限定于本地 all-Llama reproduction、冻结样本和当前解析合同，不能推广为论文原模型的精确复现或临床安全评价。

## 实际完成范围

| 入口/协议 | source groups | 输入记录 | 完成率 | M0 | M1 | M2 |
|---|---:|---:|---:|---:|---:|---:|
| MedEinst 原生主样本 | 300 对 | 600 | 100% | 10.83% | 9.00% | 7.67% |
| MedPIC 原生多选 | 467 | 467 | 100% | 35.97% | 36.83% | 30.84% |
| CPV 原生单选 | 60 | 665 | 100% | 57.58% | 59.85% | 55.30% |
| Cultural 原生单选 | 150 | 1500 | 100% | 62.53% | 61.53% | 66.13% |
| MedCounterFact 证据关系 | 80 | 400 | 100% | 67.25% | 63.75% | 66.75% |
| MedEinst 冻结四选项辅助 | 60 对 | 120 | 100% | 46.67% | 43.33% | 55.00% |

表中按源题先平均；CPV 的 micro 分数另为 57.14%/59.40%/54.89%。MedEinst 是 canonical-match screening；MedPIC 是 exact-set；MedCounterFact 是 EA，不能与诊断 accuracy 平均，也不代表临床安全。四选项辅助另补 59 对的原生结果（118 输入），与主样本重合的 1 对只运行一次。总共 3,870 条评价记录、3,774 个唯一可见输入、11,322 个方法预测。

五入口均取得作者公开数据并固定 revision；全部采样在正式效果检查前冻结，没有采用紧缩档。Cultural 的真实发布是 150×10=1,500 条，没有 Neutral，不能宣称完成 1,650 条设计。MedPIC 无可核验官方 pair map，未构造所谓 89 对。CPV 使用作者原始 question 恢复 reference，变体使用完整 case_text，未把两个患者问题拼接。MedCounterFact 80 组均有四种替换，保留四 MainCategory 和全部题内证据。原始公开文本只留本地；Cultural/MedCounterFact 未发现明确仓库再分发许可，不提交原文。

MedEinst 扫描 163 份历史资产，找到 3,550 个官方 test 病例的完整叙述匹配；主样本为 299 个未匹配病例和 1 个已曝光病例，不能称 pristine。CPV/Cultural 有 6 个完整原题文本匹配、原生选项集合不同的来源重叠组，已做保守聚类和去重叠敏感性。数据规模、revision、五条 source-unit 自检及已知歧义见 acquisition.md、data_checks.md、benchmark_summary.csv。

## 真实基线及执行证据

复用 `run_cfshift.py::run_baseline` 所指向的 `run_gate_b.py::run_m2` 基础主干符号及外部 MedRGAG prompt/parser；没有运行 CFShift 本身。Llama-3.1-8B-Instruct BF16、同 checkpoint/tokenizer、vLLM 0.8.5；全部辅助 LLM 阶段均用 Llama。Textbooks/Wikipedia 各 BM25 32 候选，经 FP32 MedCPT 取 5 文档；5 个 KGCC 摘要→3 个知识点→5 个补充文档→原 KADS 从 10 候选选最多 5 个→MedCPT→原本地 JSON reader。

KGCC/reader 为温度 0；补充生成温度 1.2、top_p 0.9、top_k 50；摘要/知识探索/生成/KADS/reader 上限为 64/1024/256/2048/64 token。为完整保留最长题内证据，容量由历史 32K 扩为 65,536；实际最长 prompt 51,307 token，无输入裁剪或 overflow。开放诊断、多选、证据比较只做任务 I/O 适配。与官方混合模型、早期 v15 约束标签输出不同，正式命名 `medrgag_llama_base`，完整调用表和 prompt 见 baseline_contract.md 及本地持久化缓存。

56,610 个主 LLM 请求严格对应每输入 15 次：3 reader、5 summary、1 explore、5 generate、1 select。各输入都执行了 KGCC/KADS；无额外专家或 judge 调用。31 条并发预取重叠检索结果完全一致，成本保留。其他用户的 GPU 进程未终止。

## 下降、稳定与方法差异

| M2 原题→变体 | 配对数/源组 | drop，95% source-cluster CI |
|---|---:|---|
| MedEinst 原生 | 300/300 | +6.67 pp [2.67, 10.67] |
| CPV | 605/60 | −2.17 pp [−10.67, 5.83] |
| Cultural | 1350/150 | −0.15 pp [−5.56, 5.11] |
| MedCounterFact EA | 320/80 | −0.62 pp [−7.19, 5.94] |

MedEinst 的 M0 drop 为 6.33 pp，M2−M0 drop amplification 仅 +0.33 pp [−3.67, 4.34]。另外三个配对入口的 M2 amplification 也都跨零。因此，没有证据证明 M2 比 Direct 更普遍地放大编辑敏感性；区间跨零也不能证明等价。跨来源 ±5pp 等价检验因缺乏相容来源覆盖 unavailable。

方法整体得分差异与原题→变体变化是不同问题。MedPIC M2−M0 为 −5.14 pp [−8.99, −1.50]，M2−M1 为 −6.00 pp [−10.06, −2.14]；M2 相对 Direct 修复 29 题、引入 53 错，条件伤害率 53/168=31.55%。MedEinst 原生 M2−M0 为 −3.17 pp [−5.33, −1.00]。CPV、Cultural、MedCounterFact 的 M2−M0 区间均跨零，Cultural 点估计为 +3.60 pp。MedPIC 三方法均有 GF 高于 CF 的未配对构成差：16.92/17.43/14.76 pp；没有 pair map，不能称原题被编辑后下降。

MedEinst M2 四格为 n11/n10/n01/n00=1/32/12/255；reference 正确仅 33/300，variant 正确 13/300。旧答案坚持为 15/33=45.45%，不能把其余错误都叫“不更新”。大量低分及 floor effect 与规范化合同共同限制解释。Cultural M2 有 138 个正确→错误和 140 个错误→正确，整体均值接近不变掩盖了双向变化。CPV 相应为 49/62，MedCounterFact 为 22/24。完整 correct revision/preservation、semantic flip、changed/stable wrong 和 invalid 记录见 transitions.csv。

## 输出合同、格式敏感性与阶段限制

MedEinst 主样本 M0/M1/M2 未映射诊断为 323/462/432，占 53.83%/77.00%/72.00%；M2 另有 3 个歧义诊断。未映射不等于医学语义错误，未增加结果驱动的别名，也未调用医学 judge。其余原生格式非法数：CPV 0/0/0，Cultural 9/3/1，MedPIC 10/1/4，MedCounterFact 0/0/0。MedCounterFact uncertainty 为 0/7/1，单列于拒绝及格式非法。

相同冻结 60 对内，四选项相对原生的 M2 reference/variant 增益为 +38.33/+56.67 pp，95% CI 分别 [25.00,51.67]/[45.00,68.33]。辅助四选项 M2 drop 为 −10 pp [−30,10]，不能替代 300 对原生结论；其选项构造和辅助样本来源都影响难度。

原 KADS/parser 的最终文档数分布为：5 篇 3375，4 篇 33，3 篇 10，2 篇 7，1 篇 5，0 篇 344。零篇占 9.12%；抽查包含生成了选档叙述但不符合原解析标记的响应。它们是必须披露的本地基线阶段格式失败，不能把其结果解释成理想 KADS 的纯检索效应。没有事后修改解析器、补文档、换答案或重跑挑种子。所有请求仍完成知识生成和最终 reader；MedCounterFact 题内证据始终保留。

原预算下 summary/generate/select 达 token 上限分别为 8877/18870、14152/18870、219/3774；最终 M0/M1/M2 为 9/0/1。保留这些自然截断，不缩短预算以加速。20 条固定独立随机流复测中，19 个有效语义比较有 7 次变化，原始输出变化 10/20；样本很小，只估计本实现随机性，不扣除噪声或择优。原 master+1 复测存在跨槽位种子重叠，已透明保留并另计成本，最终独立复测使用固定流偏移，详见 rng_repeat_correction.json。

## Taxonomy 与可支持的范围

MedEinst 的临床信息更新及 MedPIC 临床规则条件题最接近窄临床 CF；CPV/Cultural 是患者身份/情境变换下的答案保持任务；MedCounterFact 是假设证据世界。三者评价语义不能混合。MedEinst 复合编辑保守标为 mixed_or_unresolved，没有为制造掉点重分组。

clinical_update 与 evidence-world 设计矩阵秩不足；answer_invariance 在两个 MedQA 构造内满秩，但只有一个原始来源家族。identity 虽跨 CPV/Cultural，仍只是同源构造重复。所有独立跨来源 taxonomy 结论为 NOT_IDENTIFIABLE。保留同源描述性回归、组内比较及 2,000 次 cluster bootstrap；没有以正则化、删除 source 控制或把 reference 正误当无噪声难度来强行识别。MedPIC 静态 GF 行标签的规则修正及敏感性完整保留，不改样本或预测。

## 成本与下一步

正式批次 2026-09-06 08:56:18–13:28:14 CST，共 16,316 秒（4 小时 31 分 56 秒），GPU0/GPU2 两副本，GPU1 预取耗时 4,592.89 秒。复测利用释放后的 GPU2 与最后一个主分片短暂重叠，13:32:32 完成；从正式启动到全部推理结束 4 小时 36 分 14 秒。前置 smoke/兼容性准备独立记录于 performance_test.json，不冒充正式批次吞吐。

主任务 56,610 请求、97,047,730 prompt token、11,521,838 completion token。含两次复测及废弃 smoke 的实际总计 57,140 请求、99,197,477 prompt token、11,649,160 completion token。精确去重 96 输入节省 1,440 次主 LLM 调用；复用审核后的 25 条 smoke 全阶段，历史答案缓存使用为零。prompt token 是逻辑计数，含前缀缓存，不能当作实际重算 prefill 数。vLLM V1 前缀缓存/分块预填充默认开启，但未暴露本次 prefix hit/queue 统计，留 NA。没有 transport 失败或格式 repair。最大耗时阶段为 KADS；完整 stage wall sum 与重叠批次 makespan 分开报告。

唯一建议的后续机制检验：原 KADS 输出与解析格式失配导致的证据丢失，是否解释同一题上的 M2−M1 变化。当前 344 个空选档及双向预测变化足以提出这个问题，尚不能证明因果；本轮不实施解析修复实验、新方法或额外 judge。

代码、统计、SVG/PNG 图和 Mermaid 源码均已落盘。复现入口为 `bash scripts/cf_baseline_screening.sh prepare|run|analyze`（分别执行）。工作从当前本地 HEAD `1e01b3a` 开始，首个代码/协议提交 `a3881eb` 在正式启动之后的 09:03:04 创建；最终提交号由 Git 历史及交付回复记录。没有推送，用户原有未提交修改保持原状。
