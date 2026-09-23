# CF-MoA进度报告 · 版本2

实验状态截至 **2026-09-23 14:25（UTC+8）**。这是修订计划后的过程报告和精简核验材料，不是正式v5变更或冻结后的独立评估。

**新B接口和A2原parser缓存兼容完成；A1_delta与A3编辑均未取得增量采用资格。旧A2/A3/A4/F和全部负结果保留。** 新A5、完整同工具控制、独立范围资格、共同冻结和独立质量评估仍未完成。

- [完整过程报告：先读版本2新增第11章](docs/research/cf_moa_experiment_report.md#incremental-revision-v2)
- [持续主记录快照](docs/research/cf_moa.md#incremental-revision-execution-20260923)
- [修订后的核心执行计划](plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)
- [上一版09:41报告与原121题比较](../2026-09-23_cf_moa_process/README.md)：原目录保留不变，前十章的历史暂停状态以新第11章为后续进展。

| 本轮事项 | 结果 |
|---|---|
| B确定性封装 | 242条答案值保持，241条接口合法；旧M5 d00050枚举失败保留 |
| 既有修复/误伤归因 | 36条变化；26误伤中24条正确候选已送达，23条自报采纳；不据此断言医学因果 |
| A1_delta | 两骨干各3题，6/6诊断不可用、0次实际裁决；完整B回退不计专家成功 |
| A3受控开发 | 两骨干各8题×3臂，48条臂结果、45次真实final；包括3条无合格编辑回退 |
| 实际新成本 | 254次调用，924870输入/18483输出token，447.297453累计模型墙钟秒 |

## A3固定面板结果

| 方案 | M4正确/8 | M5正确/8 | M4覆盖4个非参考单元均分 | M5覆盖4个非参考单元均分 |
|---|---:|---:|---:|---:|
| 新B接口 | 3 | 4 | 50% | 50% |
| 同readout共享前缀 | 3 | 4 | 50% | 50% |
| 关键局部编辑 | 4 | 3 | 75% | 25% |
| 随机合格位置编辑 | 3 | 3 | 50% | 25% |
| 原题重复评分 | 4 | 4 | 75% | 50% |

M4关键编辑和原题重评分只修复同一题；M5关键编辑误伤1题。两骨干预定增量门均未通过，保留负结果、继续旧目录核。随机合格位置不代表已知无关位置；边际变化不是临床因果效应。该8题开发面板不能替换历史121输入/157映射/74单元主表，也不是独立成绩。

## 可核对材料

| 内容 | 文件 |
|---|---|
| B值保持及旧失败 | [B接口摘要](data/baseline_interface_summary.json) |
| A2历史parser恢复，尚非live完整控制 | [A2摘要](data/a2_parser_summary.json) |
| 36条旧变化的来源/范围归因 | [归因摘要](data/trace_attribution_summary.json) |
| A1资格失败和可选诊断回退 | [A1摘要](data/a1_delta_summary.json)、[24臂状态](data/a1_arm_status.csv) |
| A3原生指标、修复/误伤、编辑资格及未采用 | [A3汇总](data/a3_development_summary.json)、[80行输入×方案状态](data/a3_input_status.csv) |
| 实际新物理成本、历史B另账 | [成本摘要](data/cost_summary.json) |
| 未完成范围、暴露未知 | [就绪摘要](data/readiness_summary.json) |
| 工程修复和原本地制品索引 | [生命周期收据](evidence/lifecycle_fix_receipt.json)、[交付索引](evidence/development_delivery_index.json) |
| 本次已有小收据计数核验 | [56项来源审计](evidence/source_audit.json) |
| 来源SHA与导出字段规则 | [文件来源清单](SOURCE_MANIFEST.json)、[数据转换清单](DATA_EXPORT_MANIFEST.json) |
| 未随包上传的服务器引用 | [本地制品索引](LOCAL_ARTIFACT_REFERENCES.csv) |

逐输入CSV无答案值、gold、患者、证据原文或完整模型响应。A1未进行质量评分，`method_score=not_scored`，不能把空correct解释为答错。A3保留48实验臂及32个B/共享前缀控制行；实验臂logical费用包含共享前缀，**不能跨臂相加**。真实新成本只按物理请求统计，已完成smoke只计一次，历史B另列而非免费。墙钟秒不等于独占GPU秒或能耗。

来源清单记录原文件及公开副本SHA；数据是显式字段筛选，链接指向对应摘要时不意味着完整原收据已上传。Markdown只转换链接并添加快照说明，核心计划的源SHA仍为`2e86d0a6cb7302ca671cd68bfbe3f738396dea85b1cfbf8b8a225759d1414935`，公开副本因链接转换哈希不同。生命周期收据记14:02时的无模型修复状态，稍后真实退出验收见版本2正文；历史状态不覆盖新结果。 `plan/execution_plan.json`原样保留计划沿革，部分步骤内的future/no_model_calls文字描述计划更新当时；当前执行状态以其顶层status、round_delivery及报告第11章为准，不把旧步骤文案当作尚未运行。

## 无模型文档核验

在仓库根运行：

```bash
python3 benchmarks/2026-09-23_cf_moa_incremental_v2/check_publication.py
```

只检查发布文件哈希、已保存状态/计数/费用和Markdown链接；不加载模型、不重新执行原生评分、不访问原始或独立gold。单元均分引用已保存报告，此公开包没有原生标签和完整单元账本，不能独立重算医学正确性。另可运行上一版核验脚本确认旧快照保持。

源码、完整配置、SQL、模型请求与逐题原trace仍在服务器，由交付索引提供路径与哈希。本包不是可独立重新推理的完整运行环境。发布行为不自动恢复任何旧失败批次，不改变正式v5、采用基线或原生评分器。
