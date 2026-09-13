# R1–R5 benchmark v4：分类与资格交付入口

正式版本名为 **v4**，本地目录为 `benchmark_r1_r5_v4_20260910`。分类与资格已完成；模型运行接口兼容性尚未验证。

本轮采用原 R1–R5 分类指南及修正后的旧判断。旧 v3 保留，分类工作未使用历史模型预测，也未启动新的 M0–M3 测试。全部既定补分类与资格处置已完成，待处理为 0。

## 范围和已完成部分

- 24,436 个抽样遗漏比较单元全部完成分类或有明确理由的处置。
- 18,238 个已有 R5 比较单元直接复用原分类、理由和证据，完成原生输入与评分资格恢复；不重复标注。
- 对母库 55,991 个比较单元逐 ID 交代去向，覆盖 15 个已取得来源。另 11 个来源的获取缺口单列，不计入已审分母。
- 原 1,127 个部分定类父单元的 2,078 个无标签子目标保留具体既有裁决。它们已有证据不足、范围不符或源无效的处置，不能统称未读。
- 另恢复 20 个旧 CPV 比较单元的资格：原修正记录已明确图外文字足以完成所问目标，原分类直接保留。

**MedPerturb RESOURCE 的 3,615 个独立目标已补判完成**：3,539 个可归类、65 个依据不足、1 个源无效、10 个实际无变化控制；3,529 个具备评分资格。它们属于已有比较单元，不新增单元数，也不从 VISIT/MANAGE 继承标签。

最终两批增补中，新遗漏可纳入 18,023 个单元，旧 R5 的既有目标可恢复 16,972 个单元。最后发现的 10 个无变化控制中，9 个此前有资格，1 个此前已排除，因此旧 R5 可恢复数从 16,981 调整为 16,972；旧语义原件保留，资格修正见 `legacy_target_qualification_overrides.jsonl`。新增 RESOURCE 独立恢复了另 3 个单元的目标资格。

全母库最终共有 **38,123 个单元至少有一个合格目标、77,781 个合格具体判断**；全部已审具体判断为 109,599。此数包含旧 v3 及其他旧已审目标，不是本轮新题数。

## 文件入口

| 内容 | 文件 |
|---|---|
| 新遗漏分类及依据 | `sources/{M01,M10,M14,M23}/annotations.jsonl` |
| 新来源资格 | M01/M10/M23 的 `evaluation_eligibility.jsonl`；M14 的 `annotations.jsonl` |
| 旧 R5 恢复结果 | `deferred_r5/sources/*/annotations.jsonl` |
| 旧语义保留全量校验 | `deferred_r5/restoration_preservation_audit.json` |
| 两批增补逐单元覆盖 | `exports/expansion_unit_coverage.csv` |
| 两批增补逐目标分类、依据与资格 | `exports/expansion_target_annotations.jsonl.gz` |
| 两批增补不能评分的具体目标及理由 | `exports/expansion_excluded_targets.jsonl.gz` |
| 全母库逐单元去向 | `exports/archive_unit_coverage.csv` |
| 已审全目标统一记录（含新增 RESOURCE） | `exports/all_reviewed_target_annotations.jsonl.gz` |
| 全目标最终统计及待处理数 | `exports/all_target_summary.json` |
| 全来源及获取缺口 | `source_scope_inventory.csv`、`source_scope_inventory.md` |
| 既有部分定类目标去向 | `existing_partial_target_dispositions.jsonl` |
| 相对旧冻结记录的变化 | `exports/changes_relative_to_frozen_review.csv` |
| 全来源语义类别统计 | `exports/archive_source_category_counts.csv` |
| 表图及口径 | `figures/README.md` |
| RESOURCE 完整补判与空待处理清单 | `sources/M17_resource/annotations.jsonl`、`pending.jsonl`、`progress.json` |

## 解释与使用限制

分类成立、评分可执行和原参考已独立核实是不同结论。保留完整语义多标签；父单元标签取子判断并集，不能把互斥展示类别覆盖回语义。父单元可纳入只表示至少一个具体目标合格，不能自动给其他子目标计分。

缺图按原生目标的实际依赖判断。若关键图片没有文字替代，则禁用对应目标；仅引用图片、但所需发现或关系已在文本中完整提供，不按关键词整题排除。RESOURCE 已独立核对自己的视觉依赖，其中 63 个目标需要缺失图像，均禁止评分。

原生四选项和二元任务使用已有固定答案接口。MedEinst 保持开放诊断输入，沿用本地既有归一化精确匹配，明确它不涵盖医学同义表达的语义判分，不声称复现作者全部评价协议。需要人工长答评价的目标不临时换用模型裁判。MedCF 所需知识编辑步骤没有执行，普通文本问答不能替代其原生编辑评测。

所有正式排除均依据任务、内容、构造或评分条件；没有重新随机抽样，也没有按数量限制 R5。未取得的来源属于获取缺口，不伪装成科学排除。

比较单元、具体判断、来源原题 ID、独立输入和评分映射分别统计。当前 CSV 的 `annotated_source_root_ids` 只是来源 ID 去重，不是独立患者人数。尚未生成新评测运行包，因此没有把判断数冒充独立输入数或实际评分映射数。

## 复算

`summarize_classification.py` 复算新遗漏分类覆盖；`export_expansion.py` 合并两批增补及逐目标资格；`export_archive_coverage.py` 连接全母库、旧修正集、v3 和新增资格，导出去向与变化表。各来源脚本保存实际审阅依据与原件定位。RESOURCE 的 `merge_resource.py` 校验五个互不重叠的固定分段，合并时核对了全部目标的原生 YES/NO 参考接口及明确资格。

旧母库、旧修正集和 v3 不由这些脚本覆盖。后续评测必须按具体目标读取资格，并保留本文件所述协议限制。

最终覆盖与保留检查见 `completion_audit.json`；分类结果可供本地后续对话继续组装评测包。

GitHub 说明、聚合统计和图表：[全量补分类交付](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-10_r1_r5_full_classification)。完整原文和逐目标标注保留本地。

版本清单：[v4_manifest.json](<v4_manifest.json>)。分类统计：v4_category_summary.csv（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/exports/v4_category_summary.csv`）。

## v4 当前分类

按完整语义多标签统计，类别可重叠；合格单元去重总数为38,123。

| 类别 | 有标签单元 | 有合格目标的单元 | 合格具体判断 |
|---|---:|---:|---:|
| R1 | 2967 | 2866 | 4155 |
| R2 | 90 | 79 | 79 |
| R3 | 795 | 733 | 733 |
| R4 | 139 | 13 | 13 |
| R5 | 40003 | 35872 | 74268 |

v4 当前分类（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/figures/v4_category_distribution.png`）

[当前v4与排除七来源方案：完整图表及采用原因](<reports/two_scenarios/README.md>)。此报告不修改v4范围。

后续已按用户确认另建 [v5随机评测选择](<../benchmark_r1_r5_v5_20260910/README.md>)：R5八来源各450，完整v4数据保留。

面向论文写作及接手的[工作与具体调整总记录](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-13_r1_r5_paper_work_record/README.md)，汇总v3→v4→v5过程、修改台账、验证边界及后续交接。
