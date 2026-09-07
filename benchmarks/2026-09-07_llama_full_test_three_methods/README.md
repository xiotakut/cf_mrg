# 完整测试集：Llama 三方法对照（2026-09-07）

**M0 Direct、M1 retrieval-only、M2 MedRGAG-Llama 各 25,280/25,280 个唯一输入，完成率 100%。** 本次补齐此前中止的 M0/M1；各保留 5,832 条旧预测、新增 19,448 条，M2 及所有上游阶段完全沿用已验收结果。

- [完整中文报告](findings.md) · [自动统计摘要](summary.md)
- [全部逐题预测](predictions.jsonl) · [主指标](benchmark_metrics.csv) · [配对效应](paired_effects.csv) · [方法间比较](method_comparisons.csv) · [变化敏感性差异](amplification.csv)
- [来源与规模](benchmark_summary.csv) · [数据获取与版本](acquisition.md) · [基线合同](baseline_contract.md) · [配置](config.json)
- [三方法图表 SVG/PNG](figures/) · [类型可识别性](taxonomy_identifiability.json) · [统计检验](statistics.json) · [敏感性](sensitivities.json)
- [本次新增成本](reader_completion_efficiency.csv) · [执行来源与监控](execution_provenance.json) · [全部阶段成本](efficiency.csv) · [压缩阶段记录](stages.jsonl.gz)
- [验收](validation.json) · [完整阶段审计](artifact_audit.json) · [prepare/run/analyze 命令](commands.sh) · [流程图](flow.mmd)

## 完整原生测试结果

同一本地 Llama-3.1-8B-Instruct BF16，reader T=0、max_tokens=64，保持原提示、原生选项、必需证据与逐输入/阶段 seeds。分数为源题组平均，详细区间见报告。

| Benchmark / 指标 | 评价记录 / 方法 | M0 | M1 | M2 |
|---|---:|---:|---:|---:|
| MedEinst / canonical match | 10,766 | 10.93% | 7.75% | 8.26% |
| MedPIC / exact-set | 467 | 35.97% | 36.83% | 30.84% |
| CPV-MedQA / accuracy | 13,512 | 61.59% | 63.78% | 67.09% |
| Cultural-Cues / accuracy | 1,500 | 62.53% | 61.53% | 66.13% |
| MedCounterFact / evidence agreement | 1,012 | 66.31% | 61.87% | 66.50% |

另有冻结的 MedEinst 60 对四选项辅助：120 条记录，M0/M1/M2 为 46.67% / 43.33% / 55.00%。它不是第二个 benchmark。全部共 27,377 条评价记录、25,280 个去重可见输入，每个方法完整覆盖；三方法合计 75,840 条唯一预测。

M2 在 CPV 上高于 Direct，在 MedEinst canonical 匹配及 MedPIC 上低于 Direct；Cultural 与 MedCounterFact 的 M2−M0 区间包含 0。MedEinst 的 M0/M1/M2 paired drop 分别为 +5.59/+1.60/+1.80 pp，M2 相对 Direct 的 drop 小 3.79 pp，但总体 canonical 分数也更低。其余可配对入口的整体 drop 区间包含 0。

MedEinst 高未映射率限制语义诊断解释；EA 不代表临床安全。MedPIC 缺可验证官方 pair map；Cultural 未发布 Neutral；MedCounterFact 有三个源题各缺一个发布变体类别。跨独立来源 taxonomy 为 NOT_IDENTIFIABLE。三方法使 native Holm 族从旧报告 29 项扩大为 87 项，M2 未校正结果保持原样；详见报告。

## 成本与复用

本次推理 **45 分 14 秒**，新增 **38,896 次** LLM 请求，prompt tokens **33,914,033**、completion tokens **339,142**；没有新增 M2、检索、KGCC 或 KADS 调用。全部三方法主运行含历史缓存共 379,200 次调用。当前成本与旧 M2 工作负载分列，避免将历史成本算作本次耗时。

4 项合同/覆盖/指标测试及全量阶段、字节保留、指标恒等式审计通过。Luna max 只读监督，主代理定期核验并完成验收。已完成的 malformed/invalid 输出均保留并按冻结协议计分；无 pending 或 transport failure。

## 归档来源与使用

原实验目录为 [cf_medrgag_validation_pack/results_cf_full_comparison](../../cf_medrgag_validation_pack/results_cf_full_comparison)。本目录从结果 commit [3a6b5ab](https://github.com/xiotakut/cf_mrg/commit/3a6b5ab17505e5ed3cc506389282042d0ef15440) 原样复制其 72 个 Git 记录文件，另加本 README。旧 [M2-only 完整快照](../2026-09-07_medrgag_llama_base_full_test/README.md) 保持不变。

从仓库根目录执行：

```bash
bash cf_medrgag_validation_pack/results_cf_full_comparison/commands.sh
```

此命令依次准备独立缓存、补齐 readers、分析并审计；需要服务器已有的完整源数据、模型和检索缓存。原始 benchmark 正文、模型权重、检索库、凭据及大型正文缓存留在服务器。阶段记录内的 `cache/...` 引用相对于上述原实验目录解析；快照中的审计脚本需在原实验目录执行，统一 commands.sh 已使用该路径。

后续运行继续在 [benchmarks/](../README.md) 新建独立日期目录。
