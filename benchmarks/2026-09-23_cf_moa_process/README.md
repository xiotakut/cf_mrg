# CF-MoA完整执行过程与阶段结果

发布于2026-09-23，实验状态截至当日09:41。**原型已有完整开发结果，当前聚合候选未采用；同工具完整控制、共同冻结和独立评估尚未完成。**

从[完整过程报告](docs/research/cf_moa_experiment_report.md)开始阅读。报告覆盖计划阶段、实际采用入口、A4配置恢复、A1-v1至v2各修订、A5负结果和旧F、A2/A3控制、离线互补、Router/聚合各次失败与修复、完整结果、真实费用、CPU/GPU调度问题及当前阻断。

| 完整开发结果，每骨干121输入 | M4正确 | M5正确 |
|---|---:|---:|
| 强旧head | 87 | 82 |
| 固定三次采样公共上限对照 | 84 | 74 |
| 实验A1池top-1 | 72 | 57 |
| 含A1稀疏聚合 | 79 | 74 |

同池top-1仍保留16/44个不可用；聚合改善可用性不能全部称为错误修复。固定三次采样只有相同公共上限，并非严格相同实际计算费用。原生等单元指标、配对分母、修复/误伤及证据使用见报告，不能用本表代替全部结论。

## 文件导航

- [完整过程报告](docs/research/cf_moa_experiment_report.md)：面向读者的连贯回顾，包含当前完成表与全部主要失败链。
- [持续主记录快照](docs/research/cf_moa.md)：原阶段正文，保留当时的准备、暂停、错误和后续恢复。
- [原核心执行计划](plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)：原文逐字保留。
- [完整比较摘要](data/comparison_summary.json)、[成本](data/cost_summary.json)、[证据使用](data/evidence_use_summary.json)。
- [242题精简状态](data/per_input_status.csv)：仅不透明题号及已保存的正确/错误/不可用状态，不含题面、答案或模型原文。
- [未采用决定](data/non_adoption_decision.json)、[开发交付索引](data/development_delivery_index.json)。
- [来源与哈希](SOURCE_MANIFEST.json)、[未上传本地制品索引](LOCAL_ARTIFACT_REFERENCES.csv)。

## 复核

从仓库根目录执行：

```bash
python3 benchmarks/2026-09-23_cf_moa_process/check_publication.py
```

该检查只核对发布文件哈希、既有评分状态的计数/转移、费用与Markdown链接，不读取gold、不调用模型、不重新执行原生评分。原始输入、完整请求/响应、SQLite、模型权重和大型缓存留在服务器；JSON内的绝对路径是原证据位置，不是在线下载地址。发布副本把未收录Markdown链接明确标为本地制品。

本次是文档发布，新增模型调用0。正式v5、原生评分器和全部历史结果不变；此前R1–R5单head过程报告仍保留在[原发布包](../2026-09-16_support_update_method/README.md)。
