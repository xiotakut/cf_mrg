**2026-09-25 · RCV收口计划执行中：[第16章进展报告](2026-09-25_cf_moa_rcv_completion_in_progress/docs/research/cf_moa_experiment_report.md#rcv-completion-in-progress) · [五张开发主表](2026-09-25_cf_moa_rcv_completion_in_progress/data/tables/five_tables.md) · [代码、配置与trace/成本索引](2026-09-25_cf_moa_rcv_completion_in_progress/README.md)。cached/live接线、配对统计、C5及规则操作消融已完成；完整v5正在GPU1/M4、GPU2/M5并行，冻结后确认尚未开始。旧默认B不变；这是进度快照，不是最终效果交付。**

**2026-09-24 · 候选验证新计划已完整执行：[完整报告第15章](2026-09-24_cf_moa_candidate_verification/docs/research/cf_moa_experiment_report.md#candidate-verification-execution) · [运行过程与代码/配置/逐题trace/成本交付](2026-09-24_cf_moa_candidate_verification/RUN_AND_DELIVERY.md)。GPU2/3完成780次真实取分；带理由臂历史121正确88/87、自然52正确35/28（旧B87/82、35/26），有开发选择增益但原生/配对仍有退步，暂不默认采用。公开完整结果、运行时源码、3460逐题状态和780调用元数据；完整病例/SQL留私有。此次发布0新模型/评分，旧版本保持。**

**2026-09-24 · v4诊断补充：[给规划模型的阅读入口](2026-09-24_cf_moa_v4_diagnosis/README.md) · [真实调用链与选择分解](2026-09-24_cf_moa_v4_diagnosis/DIAGNOSTIC_REPORT.md)。公开采用F及被调用源码、运行配置/diff、95组合/285 seed记录的元数据；0新生成，默认B保持。完整原始样本仍为私有附件。**

**2026-09-24 · 版本4：[CF-MoA最简复用完整报告第14章](2026-09-24_cf_moa_minimal_v4/docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4) · [运行过程与交付索引](2026-09-24_cf_moa_minimal_v4/RUN_AND_DELIVERY.md)。等价旧B五操作包装完成；231次新增调用，历史121小幅增益、自然52三seed双骨干均退步，F普通重答未采用。公开有限源码/配置、99项原始索引与公开映射、逐题状态和调用元数据；原完整trace留本地。此次发布0新模型/评分，前3版保留。**

# Benchmark 结果归档

**2026-09-23 · 版本3：[CF-MoA完整进展与四轮效果优先实验](2026-09-23_cf_moa_effect_first_v3/docs/research/cf_moa_experiment_report.md) · [状态、成本与核验材料](2026-09-23_cf_moa_effect_first_v3/README.md)。保留原全过程，补全四轮2203次新调用及失败/修复；第四轮主臂18/34、15/34，低于B的23/34、19/34，仍未采用、未开启独立评估。GPU0/1自有占位已释放，2/3保留。本次仅发布文档与已保存元数据，0新推理/评分。**

**历史版本2：[CF-MoA修订后执行报告](2026-09-23_cf_moa_incremental_v2/docs/research/cf_moa_experiment_report.md#incremental-revision-v2) · [状态、失败与成本](2026-09-23_cf_moa_incremental_v2/README.md)。B接口及A2兼容完成，A1_delta/A3均未采用，独立评估未完成。**

**09:41历史版：[2026-09-23 CF-MoA Router＋五专家完整过程报告](2026-09-23_cf_moa_process/docs/research/cf_moa_experiment_report.md) · [开发结果、错误、成本与核验材料](2026-09-23_cf_moa_process/README.md)。当前聚合不采用，共同冻结与独立评估尚未完成。**

**2026-09-20：[R1–R5实验全过程报告](2026-09-16_support_update_method/docs/research/support_update_experiment_report.md) · [方法论证稿与配套记录](2026-09-16_support_update_method/README.md)。**

**2026-09-13 归档：[2026-09-13 v5 五方法完整结果（M4 修复版）](2026-09-13_v5_complete/completion/v5_benchmark_latest/README.md) · [近期全部工作及文档](2026-09-13_v5_complete/README.md)。**

本目录统一保存本项目 benchmark 的结果与数据构建流程说明。每次运行或流程记录使用独立的日期子目录，保留历史版本。

| 完成日期 | 运行 | 方法 | 范围 | 完成率 |
|---|---|---|---|---|
| 2026-09-23 版本3 | [CF-MoA完整进展与四轮效果优先开发](2026-09-23_cf_moa_effect_first_v3/README.md) | 原全过程＋A1/A3/A5后续及目标条件绑定 | 四轮2203新调用；2546保存状态行、92质量组；失败、成本和剩余缺口 | 四轮完成未采用；GPU0/1自有占位释放；本次0新推理/评分 |
| 2026-09-23 版本2 | [CF-MoA新计划执行](2026-09-23_cf_moa_incremental_v2/README.md) | 新B接口、A1_delta、A3受控编辑 | 36条旧变化归因；A1两骨干3题；A3各8题/三臂；254调用实际成本 | 本轮结束，两新机制未采用；0本次发布新模型/评分 |
| 2026-09-23 | [CF-MoA完整过程报告](2026-09-23_cf_moa_process/docs/research/cf_moa_experiment_report.md) | Router＋五专家、旧F及核心控制 | 全流程状态、错误/修复、负结果、成本；两骨干各121开发输入 | 文档发布；聚合不采用、独立评估未完成；0本次新模型 |
| 2026-09-20 | [R1–R5实验全过程报告](2026-09-16_support_update_method/docs/research/support_update_experiment_report.md) | 增补R4与未完成R5，原78阶段保留 | 共148阶段；含失败、过早停止纠正、平台中断及保存 | 文档发布；0新模型调用 |
| 2026-09-18 | [R1–R3实验全过程报告](2026-09-16_support_update_method/docs/research/support_update_experiment_report.md) | R2→R3→R1的实际研究过程与交叉审计 | 78阶段的观察、候选、失败恢复、优化、验证及交付 | 文档发布；0 新模型调用 |
| 2026-09-16 | [支持更新与候选重决策论证稿](2026-09-16_support_update_method/README.md) | 七方法基线与 R1/R2/R3 开发头，附机制和新来源对照 | 完整原因—方法—证据链及相关记录 | 文档发布；0 新模型调用 |
| 2026-09-13 | [v5 全量结果及近期工作归档](2026-09-13_v5_complete/README.md) | M0/M2/M3/M4 修复版/M5；附 M6/M7 试验与暂停记录 | 五方法各 13,905 输入、15,616 映射、6,104 单元 | 五方法全量完成；M6 52 条、M7 1,646 条暂停 |
| 2026-09-07 | [MedRGAG-Llama 五入口完整测试](2026-09-07_medrgag_llama_base_full_test/README.md) | M2：medrgag_llama_base | 五入口全部发布测试记录，另含预定 MedEinst 四选项辅助 | 25,280/25,280 唯一输入 |
| 2026-09-07 | [Llama 三方法完整对照](2026-09-07_llama_full_test_three_methods/README.md) | M0 Direct / M1 retrieval-only / M2 MedRGAG-Llama | 相同五入口完整测试及冻结辅助；补齐 M0/M1，保留 M2 | 各 25,280/25,280；共 75,840 条预测 |
| 2026-09-08 | [医学 CF 五标签分类与来源审核](2026-09-08_medical_cf_five_labels/README.md) | R1–R5 分类、来源核验、旧预测离线重分组 | 完整收集标注 55,991 条；分析集 28,243 个单元；修正 172 个具体判断 | 文本 21,695 个有标签、4,051 个暂不定类；另有 2,497 个缺图多模态记录 |
| 2026-09-10，09-13 补充 | [R1–R5 工作过程与调整记录（论文参考）](2026-09-10_r1_r5_process_history/README.md) | 收集、抽样、分类、资格、704 条 AMQA 调整及 172 项审核修正实例 | 衔接 55,991 条归档、v2/v3、完整 v4 和随机 v5；区分讨论、确认与实施 | 文档及证据索引已更新；09-13 本次无数据或模型改动 |
| 2026-09-10 | [R1–R5 分类指南与补分类范围](2026-09-10_r1_r5_full_coverage_plan/README.md) | 原五类定义、具体判定规则、已审正例与纠错反例、子目标及资格处理 | 供其他本地对话接手；保留 v3，补 24,436 个抽样遗漏候选并审查已有 R5 暂缓范围 | 指南已同步完成状态；[补分类交付](2026-09-10_r1_r5_full_classification/README.md)，新版评测未运行 |
| 2026-09-10 | [R1–R5 v4 分类与资格整理](2026-09-10_r1_r5_full_classification/README.md) | 原规则分类、旧 R5 复用、独立目标资格 | 24,436 遗漏单元、18,238 旧 R5、3,615 RESOURCE 目标；全母库55,991有去向 | 待处理0；38,123单元至少一个目标可测；未运行新版评测 |
| 2026-09-10 | [v4与排除七来源方案：图表及采用原因](2026-09-10_r1_r5_v4_scope_comparison/README.md) | 两方案逐类、逐来源数量及未采用理由 | 当前11来源38,123单元；预览排除7来源后剩4来源7,611单元 | 报告完成；预览未修改v4 |
| 2026-09-10 | [R1–R5 v5：随机抽样与探索记录](2026-09-10_r1_r5_v5/README.md) | R1–R4完整保留；R5八来源各随机450 | 6,104去重单元、13,000具体判断；完整v4保留 | 种子/候选/选中ID可重放；后续五方法 v5 全测已完成（见最新入口） |
| 2026-09-13 | [R1–R5论文工作与调整总记录](2026-09-13_r1_r5_paper_work_record/README.md) | 版本形成、16项调整、验证证据及Methods草稿 | 本线程v3→v4→v5；后续运行单列交接 | 文档归档，未修改数据或重跑实验 |
| 2026-09-13 | [v3基线与分类指南：工作及调整记录](2026-09-13_r1_r5_v3_methods_record/README.md) | M2复用/补跑、M3接口/长证据/投票终态、M1身份、来源追溯和指南修订 | 逐项调整前后、原因、证据及论文表述；链接独立构建与后续方法记录 | 文档归档；本次未改分类、预测或运行代码 |

实验归档包含相应结果说明、预测、指标、图表、配置、命令和验收记录；流程说明归档记录版本演变及决策依据，其完整运行制品状态在文中注明。后续内容放入新的子目录，并在此表追加索引。

原始 benchmark 文本、权重、检索库、凭据及大型推理正文缓存留在服务器；来源、版本和恢复说明随每次结果保留。已有实验工作目录继续用于执行和断点恢复。
