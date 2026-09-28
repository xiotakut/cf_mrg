# CF-MoA完整v5透明收尾（2026-09-28）

**本阶段零新增推理收尾已完成；冻结后新家族确认与独立F复本未执行并延后。** 默认采用B保持，C3为显式研究扩展。原d857934结果、全部六臂与完整分母不覆盖、不按输赢筛选。

- [完整结果与三组主要对比](full_results.md)
- [五张完整表：全量、全部来源/类别/格式、理由与旧核消融、配对区间、成本/覆盖](five_tables.md)
- [完整过程报告第16.13节](docs/research/cf_moa_experiment_report.md#transparent-closeout-20260928)
- [阶段状态](final_status.json) · [归属成本](attributed_costs.md) · [范围与限制](scope_and_limitations.md) · [交付索引](public_delivery_index.json)

两骨干每臂13905输入、15616评分映射、6104非参考ALL单位保持。11来源、5格式、全部R类及36个5000次/seed240924家族区间齐全；区间仅描述已暴露开发数据，未校正选择偏差。

原生ALL C3−B：M4 −1.8108pp [−2.5287,−1.0819]；M5 +0.9273pp [0.3039,1.5562]。B−C0的收益来自已有采用组件，不是RCV新增贡献。C3相对无理由版本的正点差不等于稳定超过B。

每方法费用按共同B/旧head/F一次＋自身增量归属，未将162979多臂物理请求除以六。历史上游与部分旧模型秒保持unknown。空data_issues.jsonl表示本次有限既有证据未确立当前可更正缺陷，不意味着全数据无误。

所有本轮模型/原生grader/缓存写入/GPU进程操作为0。完整患者文本、原始模型请求响应、SQL及costs/projection内gold派生诊断留私有；公开逐输入费用/覆盖166860行无gold/原文，来源索引保留。

代码与实际配置仍为[原d857934冻结快照](https://github.com/xiotakut/cf_mrg/blob/d85793470cf75af57217f3fdc73093f494d9f003/benchmarks/2026-09-26_cf_moa_rcv_full_v5/README.md)、[解析规格](https://github.com/xiotakut/cf_mrg/blob/d85793470cf75af57217f3fdc73093f494d9f003/benchmarks/2026-09-26_cf_moa_rcv_full_v5/method_spec.resolved.json)，不是新的算法版本。本包仅增加离线统计/费用收尾代码与产物。

复现纯统计（在合法本地结果目录运行，OUT使用新目录）：

```bash
python statistics/scripts/summarize_existing_results.py --root EXISTING_DATA_FULL_V5 --out NEW_OUT --draws 5000 --seed 240924
```

成本脚本使用已有私有SQL和本地来源路径，见costs/sources.json与原始目录索引；公开包不包含SQL，不能仅凭公共元数据重建所有真实messages。主方法与原生分数没有重新生成。
