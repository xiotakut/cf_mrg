# R1–R5 benchmark v4

正式版本名为 **v4**，本地目录为 `benchmark_r1_r5_v4_20260910`。分类与资格已完成；模型运行接口兼容性尚未验证。

本轮分类及资格整理已完成。完整范围、限制和文件入口见 [DELIVERY.md](<DELIVERY.md>)。

| 范围 | 已处理 | 具备评分资格的单元/目标 |
|---|---:|---:|
| 抽样遗漏比较单元 | 24,436 | 18,023 个单元 |
| 旧 R5 比较单元（既有目标） | 18,238 | 16,972 个单元 |
| M17 新增 RESOURCE 目标 | 3,615 | 3,529 个目标 |

RESOURCE 位于已有单元上，不与前两行相加。全母库 55,991 个单元均已交代去向，最终 38,123 个单元至少有一个可测目标。必要缺失多模态输入、无法固定评分和构造问题均留有具体理由；没有再次抽样或按数量删减 R5。

旧 R5 原标签、理由、证据和原始记录保留。10 个新查明的实际无变化控制采用单独资格覆盖文件，旧原件不改；其中9个从可测集合移除，另1个原已禁用。v3 保留，本轮未运行新的 M0–M3 评测。

- [完整标注与统计入口](<DELIVERY.md>)
- [来源及获取缺口](<source_scope_inventory.md>)
- [表格与图](<figures/README.md>)
- [最后10个资格修正的证据](<legacy_target_qualification_overrides_report.md>)

`inputs/` 和 `deferred_r5/inputs/` 为固定候选。原ID和来源定位保留，恢复时不重建候选或重复标注。各来源实际分类见 `sources/*/annotations.jsonl`，旧标注复用及资格见 `deferred_r5/sources/*/annotations.jsonl`；最终下游应读取 `exports/all_reviewed_target_annotations.jsonl.gz` 的逐目标资格。

版本清单：[v4_manifest.json](<v4_manifest.json>)。分类统计：v4_category_summary.csv（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/exports/v4_category_summary.csv`）。

[当前v4与排除七来源方案：完整图表及采用原因](<reports/two_scenarios/README.md>)。此报告不修改v4范围。

后续已按用户确认另建 [v5随机评测选择](<../benchmark_r1_r5_v5_20260910/README.md>)：R5八来源各450，完整v4数据保留。
