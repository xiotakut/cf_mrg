# 完整文档目录

2026-09-13 发布；56 份来源文档，连同本目录的总览与发布说明。当前状态以[最新完整结果](completion/v5_benchmark_latest/README.md)为准。

## 全量修复、最新结果与 M6/M7 运行

- [新 M4：v5 全量结构约束修复重测](<completion/results_v5_m4_structured/README.md>) — `completion/results_v5_m4_structured/README.md`
- [新 M4 v5 全量结果](<completion/results_v5_m4_structured/RESULTS.md>) — `completion/results_v5_m4_structured/RESULTS.md`
- [v5 M6 / M7 正式输入小批量试跑（2026-09-13）](<completion/results_v5_m6_m7/README.md>) — `completion/results_v5_m6_m7/README.md`
- [v5 M6/M7 小批量结果](<completion/results_v5_m6_m7/RESULTS.md>) — `completion/results_v5_m6_m7/RESULTS.md`
- [M0–M7 输出有效率核对（2026-09-13）](<completion/results_v5_m6_m7/VALIDITY_COMPARISON.md>) — `completion/results_v5_m6_m7/VALIDITY_COMPARISON.md`
- [v5 M6 / M7 全量测试](<completion/results_v5_m6_m7/formal/README.md>) — `completion/results_v5_m6_m7/formal/README.md`
- [v5 M6/M7 活动全量：按阶段与长度合批](<completion/results_v5_m6_m7/formal_balanced/README.md>) — `completion/results_v5_m6_m7/formal_balanced/README.md`
- [v5 M6/M7 全量运行：提高并发后的接续](<completion/results_v5_m6_m7/formal_fast/README.md>) — `completion/results_v5_m6_m7/formal_fast/README.md`
- [v5 benchmark：M0 / M2 / M3 / 新 M4 / M5 完整对照](<completion/v5_benchmark_latest/README.md>) — `completion/v5_benchmark_latest/README.md`

## 正式评测、性能、修复试验与诊断

- [v5 评测实施、调整与复现记录（M0–M5 正式评测及 M4/M6 格式修复试验）](<execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>) — `execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`
- [M6 最终格式整理修复试验（2026-09-13）](<execution/m6_formatter_pilot/README.md>) — `execution/m6_formatter_pilot/README.md`
- [M7 暂停结果有效率诊断（2026-09-13）](<execution/m7_validity_audit/README.md>) — `execution/m7_validity_audit/README.md`
- [V5 R1–R5：M0 / M2 / M4 / M5 完整评测运行](<execution/results_v5_m0_m2_m4_m5/README.md>) — `execution/results_v5_m0_m2_m4_m5/README.md`
- [V5 R1–R5：M0 / M2 / M4 / M5 完整结果](<execution/results_v5_m0_m2_m4_m5/RESULTS.md>) — `execution/results_v5_m0_m2_m4_m5/RESULTS.md`
- [V5 已完成方法：M0 / M2 / M5](<execution/results_v5_m0_m2_m4_m5/completed_m0_m2_m5/RESULTS.md>) — `execution/results_v5_m0_m2_m4_m5/completed_m0_m2_m5/RESULTS.md`
- [当前 M4 输出格式修复试验](<execution/results_v5_m0_m2_m4_m5/m4_format_pilot/README.md>) — `execution/results_v5_m0_m2_m4_m5/m4_format_pilot/README.md`
- [M4 提示词 + JSON Schema 试跑结果](<execution/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/README.md>) — `execution/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/README.md`
- [旧 M4 同题有效率对照：准备记录](<execution/results_v5_m0_m2_m4_m5/old_m4_pilot/README.md>) — `execution/results_v5_m0_m2_m4_m5/old_m4_pilot/README.md`
- [运行监督记录](<execution/results_v5_m0_m2_m4_m5/supervision.md>) — `execution/results_v5_m0_m2_m4_m5/supervision.md`
- [M3 v5 continuation](<execution/results_v5_m3/README.md>) — `execution/results_v5_m3/README.md`
- [M3 v5 final results](<execution/results_v5_m3/RESULTS.md>) — `execution/results_v5_m3/RESULTS.md`
- [M3 performance investigation](<execution/results_v5_m3/performance_notes.md>) — `execution/results_v5_m3/performance_notes.md`
- [v5 M0/M2/M3/M4/M5 分类表现与优化优先级](<execution/v5_category_priority/README.md>) — `execution/v5_category_priority/README.md`

## M4/M5 安装与实现

- [MedRAG：M4（Llama 3.1）与 M5（Qwen3）](<m4_m5_implementation/BASELINES.md>) — `m4_m5_implementation/BASELINES.md`
- [M4 / M5 MedRAG 安装、调整与论文实施记录](<m4_m5_implementation/M4_M5_INSTALLATION_REPORT.md>) — `m4_m5_implementation/M4_M5_INSTALLATION_REPORT.md`
- [MedRAG Toolkit](<m4_m5_implementation/README.md>) — `m4_m5_implementation/README.md`

## M6/M7 方法复现与兼容性

- [M6 i-MedRAG 与 M7 TC-RAG：实现、调整及论文写作记录](<m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md>) — `m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md`
- [M6 i-MedRAG / M7 TC-RAG 比较方法接入](<m6_m7_implementation/README.md>) — `m6_m7_implementation/README.md`
- [M6 i-MedRAG / M7 TC-RAG 接入验收](<m6_m7_implementation/acceptance_report.md>) — `m6_m7_implementation/acceptance_report.md`
- [冻结输入与评分接口](<m6_m7_implementation/evidence_protocol.md>) — `m6_m7_implementation/evidence_protocol.md`
- [M6 i-MedRAG / M7 TC-RAG 方法忠实性记录](<m6_m7_implementation/method_fidelity.md>) — `m6_m7_implementation/method_fidelity.md`

## 数据构建、来源资格与方案记录

- [R1–R5 benchmark v4：分类与资格交付入口](<construction/benchmark_r1_r5_v4_20260910/DELIVERY.md>) — `construction/benchmark_r1_r5_v4_20260910/DELIVERY.md`
- [R1–R5 benchmark v4](<construction/benchmark_r1_r5_v4_20260910/README.md>) — `construction/benchmark_r1_r5_v4_20260910/README.md`
- [完成要求差距审查](<construction/benchmark_r1_r5_v4_20260910/completion_gap_review.md>) — `construction/benchmark_r1_r5_v4_20260910/completion_gap_review.md`
- [已审 R5 资格恢复说明](<construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M11/README.md>) — `construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M11/README.md`
- [已审 R5 资格恢复说明](<construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M12/README.md>) — `construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M12/README.md`
- [M14 旧 R5 资格恢复记录](<construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M14/README.md>) — `construction/benchmark_r1_r5_v4_20260910/deferred_r5/sources/M14/README.md`
- [图表统计口径](<construction/benchmark_r1_r5_v4_20260910/figures/README.md>) — `construction/benchmark_r1_r5_v4_20260910/figures/README.md`
- [M17 旧目标资格补充：实际无变化控制](<construction/benchmark_r1_r5_v4_20260910/legacy_target_qualification_overrides_report.md>) — `construction/benchmark_r1_r5_v4_20260910/legacy_target_qualification_overrides_report.md`
- [R1–R5 benchmark：当前 v4 与排除七来源方案对比](<construction/benchmark_r1_r5_v4_20260910/reports/two_scenarios/README.md>) — `construction/benchmark_r1_r5_v4_20260910/reports/two_scenarios/README.md`
- [全来源流程清单](<construction/benchmark_r1_r5_v4_20260910/source_scope_inventory.md>) — `construction/benchmark_r1_r5_v4_20260910/source_scope_inventory.md`
- [MedEinst 抽样遗漏项补分类](<construction/benchmark_r1_r5_v4_20260910/sources/M01/README.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M01/README.md`
- [最终评分资格 sidecar](<construction/benchmark_r1_r5_v4_20260910/sources/M01/evaluation_eligibility_README.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M01/evaluation_eligibility_README.md`
- [CPV-MedQA 抽样遗漏补分类](<construction/benchmark_r1_r5_v4_20260910/sources/M10/README.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M10/README.md`
- [最终评分资格 sidecar](<construction/benchmark_r1_r5_v4_20260910/sources/M10/evaluation_eligibility_README.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M10/evaluation_eligibility_README.md`
- [M14 roots 600–1067 实际复核](<construction/benchmark_r1_r5_v4_20260910/sources/M14/tail_review_method.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M14/tail_review_method.md`
- [BioRAB M23 新 context 语义补审](<construction/benchmark_r1_r5_v4_20260910/sources/M23/cpv_semantic_review_report.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M23/cpv_semantic_review_report.md`
- [最终评分资格 sidecar](<construction/benchmark_r1_r5_v4_20260910/sources/M23/evaluation_eligibility_README.md>) — `construction/benchmark_r1_r5_v4_20260910/sources/M23/evaluation_eligibility_README.md`
- [从完整 v4 到随机评测子集 v5：探索与决策记录](<construction/benchmark_r1_r5_v5_20260910/EXPLORATION_HISTORY.md>) — `construction/benchmark_r1_r5_v5_20260910/EXPLORATION_HISTORY.md`
- [R1–R5 benchmark v5：八来源各450个随机R5单元](<construction/benchmark_r1_r5_v5_20260910/README.md>) — `construction/benchmark_r1_r5_v5_20260910/README.md`
- [医学 R1–R5 benchmark 工作与调整总记录：v3 → v4 → v5](<construction/paper_work_record_20260913/README.md>) — `construction/paper_work_record_20260913/README.md`
- [r1_r5_benchmark_sources_20260910.md](<construction/r1_r5_benchmark_sources_20260910.md>) — `construction/r1_r5_benchmark_sources_20260910.md`

## 跨工作区索引与历史指南

- [MedRGAG Llama 3.1 复现历史与会话交接](<workspace_reference/LLAMA31_REPRODUCTION_HISTORY.md>) — `workspace_reference/LLAMA31_REPRODUCTION_HISTORY.md`
- [MedRGAG Workspace Guide](<workspace_reference/MEDRGAG_WORKSPACE_GUIDE.md>) — `workspace_reference/MEDRGAG_WORKSPACE_GUIDE.md`
- [医学 R1–R5 分类指南：原有规则、示例与后续补分类](<workspace_reference/R1_R5_CLASSIFICATION_GUIDE.md>) — `workspace_reference/R1_R5_CLASSIFICATION_GUIDE.md`
- [R1–R5 v3 基线与分类指南：工作及调整记录](<workspace_reference/R1_R5_V3_BASELINES_WORK_RECORD.md>) — `workspace_reference/R1_R5_V3_BASELINES_WORK_RECORD.md`
