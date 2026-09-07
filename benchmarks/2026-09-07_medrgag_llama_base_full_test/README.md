# MedRGAG-Llama：五入口完整测试（2026-09-07）

**已完成并验收：25,280/25,280 个唯一输入，覆盖 27,377 条评价记录。** 本目录是这次完整运行的独立结果归档，原始实验目录为 [`cf_medrgag_validation_pack/results_cf_full_test`](../../cf_medrgag_validation_pack/results_cf_full_test)。

- [完整中文报告](findings.md) · [自动生成摘要](summary.md)
- [数据规模与覆盖](benchmark_summary.csv) · [模型和调用链](baseline_contract.md) · [数据来源及版本](acquisition.md)
- [逐题 M2 预测](predictions.jsonl) · [主指标](benchmark_metrics.csv) · [配对效应及区间](paired_effects.csv) · [统计检验](statistics.json)
- [分类指标](category_metrics.csv) · [转换记录](transitions.csv) · [敏感性分析](sensitivities.json) · [类型可识别性](taxonomy_identifiability.json)
- [效率和调用成本](efficiency.csv) · [完整指标 JSON](metrics.json) · [压缩阶段记录](stages.jsonl.gz)
- [图表（SVG/PNG）](figures/) · [实际流程图源码](flow.mmd) · [验收记录](validation.json) · [阶段完整性审计](artifact_audit.json)

## 范围与主要结果

模型为本地 Llama-3.1-8B-Instruct BF16，完整 KGCC、补充生成、原始 KADS 和 reader。按最新任务范围，只要求 M2 完整测试；已完成的 M0/M1 各 5,832 条留在 `auxiliary_predictions.jsonl`，不作为全量对照。

| Benchmark / 协议 | 源题组或行级单元 | 评价记录 | M2 源题平均分数 |
|---|---:|---:|---:|
| MedEinst，原生诊断 | 5,383 | 10,766 | canonical match 8.26% |
| MedPIC，原生多选 | 467 | 467 | exact-set 30.84% |
| CPV-MedQA，原题及全部变体 | 1,202 | 13,512 | accuracy 67.09% |
| Cultural-Cues，原题及发布变体 | 150 | 1,500 | accuracy 66.13% |
| MedCounterFact，原题及发布替换 | 203 | 1,012 | evidence agreement 66.50% |
| MedEinst，冻结四选项辅助 | 60 | 120 | accuracy 55.00% |

五个入口的原生评估均覆盖实际完整发布范围。MedEinst 的四选项只用于预定 60 对敏感性检查，不是第二个 benchmark。MedEinst 71.98% 的开放诊断未映射到冻结标签清单，分数不能解释为官方语义诊断准确率。MedPIC 缺可验证官方 pair map；Cultural 未发布 Neutral；MedCounterFact 有三个源题各缺一个发布变体类别，均已如实记录。

MedEinst 原生规范化匹配的 paired drop 为 +1.80 pp，95% CI [0.74,2.86]；其余可配对入口整体差异区间包含 0。跨独立来源 taxonomy 为 NOT_IDENTIFIABLE。各原生分数不合并为总体 CF accuracy，EA 不代表临床安全性。

## 运行、成本与复用

推理于 **2026-09-07 05:16:18 CST** 完成，扩展 makespan 为 **15 小时 32 分 01 秒**，包括中断与恢复，并复用了 3,774 个完全相同的旧输入。M2 主干调用记录为 328,640 次；包含历史辅助和复测后的记录总数为 340,834 次，logical prompt tokens 449,853,293、completion tokens 77,488,473。未返回的中断调用 tokens 无法测量，未混入记录总量。

执行代码在 [`cf_medrgag_validation_pack/scripts`](../../cf_medrgag_validation_pack/scripts)，实际 prepare/run/analyze 命令记录在 [commands.sh](commands.sh)。运行和原始正文审计需要服务器上的 checkpoint、语料、原始输入及缓存；本归档不重复这些资产。阶段记录中的 `cache/...` 引用相对于原始实验工作目录解析。快照中的运行/审计脚本保留当时执行路径，不会在浏览结果时触发重新推理。

## 归档来源

本次结果来源 commit：[`638f1e3ad116ffdad609e74bb5a9f019a196911e`](https://github.com/xiotakut/cf_mrg/commit/638f1e3ad116ffdad609e74bb5a9f019a196911e)。原结果目录的 73 个 Git 记录文件原样复制到此目录，另加本 README；原始结果、模型输出、统计和图表均未重新计算或修改。原报告中的“未推送”描述的是生成报告时的状态；本目录是随后建立的 GitHub 发布归档。

后续 benchmark 使用 `benchmarks/` 下新的日期目录，并更新[总索引](../README.md)。
