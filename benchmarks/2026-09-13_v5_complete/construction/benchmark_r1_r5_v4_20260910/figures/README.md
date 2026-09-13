# 图表统计口径

运行：`/home/data3/txy/MedRGAG/.venv/bin/python figures/make_classification_figures.py`（工作目录为本次 RUN）。使用既有 Matplotlib，不安装依赖。

图1读取 `progress_summary.json`：以比较单元为分母，classified / insufficient_evidence / invalid_source / outside_five_labels 为互斥处置；completed 指完成处置，并非全部分入 R1–R5。required_image 是独立资格维度，不能加进四项处置。R标签可多选，CSV保留各标签原计数。该汇总 completion_claim=false 原样记入manifest，图表不作整个项目完成或评分已完成的主张。

图2从 `exports/expansion_unit_coverage.csv` 读取旧目标最终资格（包含10个实际无变化控制的禁用）；原语义保留依据为 `deferred_r5/restoration_preservation_audit.json`。恢复资格=eligible；已核验但未恢复=completed−eligible；待核验=pending。未恢复原因未在该聚合审计逐项提供，因此不从本图虚构原因分解。全部来源 semantic_fields_preserved=true，仅复用既有分类后核资格。

两批统计范围分开：新抽样遗漏与旧R5暂缓不是同一分母。计数不是独立患者数、医学专家验收数或模型准确率。PNG与PDF内容一致；CSV为UTF-8 BOM。图2不含新增RESOURCE目标；所有图表均为分类/资格统计。

## 新遗漏分类处置

| 来源 | 候选 | 可归类 | 依据不足 | 源无效 | 五类外 | 缺图（独立） |
|---|---:|---:|---:|---:|---:|---:|
| M01 MedEinst | 2800 | 937 | 1403 | 460 | 0 | 0 |
| M10 CPV-MedQA | 7725 | 3585 | 334 | 3806 | 0 | 254 |
| M14 DiversityMedQA | 3796 | 3498 | 177 | 111 | 10 | 256 |
| M23 BioRAB | 10115 | 10108 | 7 | 0 | 0 | 0 |

## 旧R5资格恢复

| 来源 | 旧单元 | 恢复资格 | 未恢复 | 待核验 |
|---|---:|---:|---:|---:|
| M11 Counterfactual Cultural Cues | 1107 | 1098 | 9 | 0 |
| M12 FairMedQA/AMQA | 4164 | 4149 | 15 | 0 |
| M14 DiversityMedQA | 2376 | 2239 | 137 | 0 |
| M17 MedPerturb | 3615 | 3567 | 48 | 0 |
| M22 MedRGB | 3680 | 3423 | 257 | 0 |
| M23 BioRAB | 2499 | 2496 | 3 | 0 |
| M24 MedCF | 797 | 0 | 797 | 0 |

## v4 总分类

PNG（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/figures/v4_category_distribution.png`） · PDF（本地制品：`/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v4_20260910/figures/v4_category_distribution.pdf`）。按全部目标汇总父单元语义多标签并集，每类别内按unit_id去重；资格只取该类别存在合格目标的单元。
