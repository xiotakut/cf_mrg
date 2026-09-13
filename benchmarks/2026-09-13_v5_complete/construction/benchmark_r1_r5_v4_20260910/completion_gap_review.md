> 此文件为中途缺口审阅快照。其 RESOURCE 缺口现已完成，最终状态及检查见 `DELIVERY.md` 和 `completion_audit.json`。

# 完成要求差距审查

审查日期：2026-09-10。依据 `/home/data3/txy/R1_R5_CLASSIFICATION_GUIDE.md` §8–11。只读核对现有产物，没有重分类或运行评测；本文是审查时点快照，主代理仍在合并。

**结论：两大候选批次的完成不等于指南全范围完成。** 新遗漏 24,436 已全部处置，旧 R5 18,238 已有各来源结果；仍需完成下列逐目标与全来源覆盖交代。已有明确裁决直接复用，不应要求重标全部旧记录。

## 1. 必须建立旧部分定类目标的去向表

从母库 `分析子集_逐题标注.csv` 筛选父 labels 非空、unclassified_target_count>0、resource_id!=M25，可精确复算指南的 1,127 个父单元。连接 `分析子集_具体判断.csv` 后共有 2,078 个无标签目标：

| 来源 | 父单元 | 无标签子目标 | 本轮覆盖情况 |
|---|---:|---:|---|
| M01 | 38 | 38 | 不在本轮新遗漏或旧 R5 清单 |
| M16 | 66 | 66 | 不在两大候选清单 |
| M17 | 22 | 22 | 在旧 R5 中，VISIT/MANAGE 分目标资格已有输出 |
| M20 | 20 | 20 | 不在两大候选清单 |
| M22 | 184 | 203 | 在旧 R5 中，203 无标签判断已有 evaluation_eligible=false |
| M24 | 797 | 1,729 | 在旧 R5 中，原编辑协议未执行，逐判断禁用已有输出 |
| 合计 | 1,127 | 2,078 | 其中 124 父单元尚未被两大范围清单覆盖 |

这些无标签目标历史上已有实质处置：outside_five_labels 1,594、insufficient_evidence 464、invalid_source 20，**不能统称为未读，也无需全部重新分类**。必要待办是导出每个 judgment_id 的原裁决、是否拟纳入、资格、禁用理由、新证据修订（如有）及父标签并集。拟纳入且仍缺关系的目标才补判；不纳入者复用已有具体正式理由。特别补齐 M01/M16/M20 的 124 父单元去向，不能只因不在新候选表中省略。

证据：母库两个上述 CSV；`deferred_r5/sources/M22/annotations.jsonl`、`M24/annotations.jsonl`、`M17/annotations.jsonl`。M17 的 22 个空标签 judgment 本体缺 evaluation_eligible，资格另放 target_eligibility；最终扁平表应以该映射明确传播，避免父单元 eligible 使 MANAGE 等无标签目标误入。

## 2. MedPerturb RESOURCE 仍是必要待办

`deferred_r5/sources/M17/annotations.jsonl` 的 `auxiliary_task_dispositions.RESOURCE` 当前写：“原生字段保留；旧修正记录没有该目标的R1–R5裁决，未从VISIT/MANAGE推断或纳入。”这正确避免继承标签，但“旧记录没标”只说明待处理，**不是 §9–11 允许的正式排除依据**。指南 §8 明示 RESOURCE 独立判断，§10 明示已有 yes/no 固定 gold 不应误判必须人工。

必要待办：固定 RESOURCE 实际候选/原生目标清单，复用已读上下文和已有关系但单独核对目标；给每个拟纳入目标分类与资格。若实质不满足定义、缺必要前提或源构造无效，写具体理由；若尚未处理则保留 pending，不得将整包 RESOURCE 默默从范围删掉。不要求重做 VISIT/MANAGE。

## 3. 全 15 已取得来源必须有最终覆盖总账

`candidate_manifest.json.archive_counts` 列了 15 来源和 55,991 母库单元，但现有顶层 `candidate_coverage.csv` 仅 24,436 新遗漏；`source_category_counts.csv` 仅 4 行；`formal_exclusion_reasons.csv` 也仅这 4 来源。旧 R5 7 来源与新遗漏合并后仍只涉及 9 个来源，M02、M05、M06、M16、M20、M25 需要在最终交付表显式出现。

必要待办：全母库按 ID 连接旧修正结果、新遗漏与资格恢复结果，逐源交代纳入、正式排除、已有未定类、必要待处理、原生 split 不属于当前评测和无变化参照。复用 M05/M16 的原生人工评分限制、M25 缺图、既有 11 个参考评分禁用；不能把整来源删掉以掩盖混合目标。MedCounterFact 已在 v3 的 703 个 R1/R5 重叠单元恢复语义不计新增；旧 v3 3,105 也需进入新版来源去向并保留历史版本。正式排除宜落到具体目标。

保留母库差额口径：55,991=28,243 已审+24,436 新遗漏+83 M01 无变化+14 M17 无变化+3,215 M24 train/valid。原发布范围还包括 CPV 的 2,085、Diversity 的 84 等无变化参照；它们未必在 55,991 表内，需单列出处，不混作新候选。

证据：`candidate_manifest.json`、`deferred_r5/manifest.json`；母库 `医学CF资源清单.md`、`reports/analysis_selection.json`、`reports/发布范围与原始来源.md`、`audit_20260908/corrections/修改明细.csv`。

## 4. 另 11 个来源的获取缺口仍须列明

最终表应单列 M03 MamaBench、M04 肿瘤CF、M07 CLIR、M08 ECG-Expert-QA、M09 GenMedicalEval、M13 MedEqualQA、M15 CLIMB、M18 DeVisE、M19 MedFuzz、M21 MediEval、M26 COLLECT。沿用历史具体获取缺口和官方定位即可；此审查不要求重新下载或申请权限。状态是“目标输入未取得”，不能写成科学范围被排除或混入已审分母。

证据：母库 `reports/发布范围与原始来源.md` 最后 11 项表，及 `医学CF资源清单.md` 对应各项 acquisition.json 定位。

## 5. 最终交付需要补齐的汇总层

在上述目标去向确定后，输出全来源覆盖清单、逐目标分类与资格、正式排除与未定类理由、新旧变化表、来源/类别统计和图。比较单元、判断目标、原题根、独立输入、评分映射分别计数；父标签保持语义并集，展示互斥类别另生成。不得把 pending 改名为排除来形成全完成宣称。

当前 `progress_summary.json` 的 scope 仅新遗漏，completion_claim=false 是准确状态；顶层 README 也主要描述新遗漏及旧 R5 工作。最终应改写交付范围而非只把完成开关置 true。无需启动 M0–M3 测试来满足本次分类整理交付。

母库根路径：`/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection/`。本文其他相对路径均相对本 RUN。
