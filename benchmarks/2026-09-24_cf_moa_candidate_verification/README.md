# CF-MoA：候选验证新计划的完整执行与交付

2026-09-24。用户授权的新计划A–H已执行完成；固定GPU2/M5、GPU3/M4于当日14:03完成真实推理及全分母分析。这里发布已保存结果与源码，不重新运行模型、原生评分或旧head。

**建议给规划/审阅模型先读这两份：**

1. [完整报告第15章：新计划、失败修复、真实效果与限制](docs/research/cf_moa_experiment_report.md#candidate-verification-execution)。前14章原有研究过程保留。
2. [本轮运作过程、代码/配置/逐题trace/成本交付索引](RUN_AND_DELIVERY.md)。

|完整开发面板|旧B正确|candidate_only|candidate_with_rationales|
|---|---:|---:|---:|
|历史121 / M4|87/121|87/121|88/121|
|历史121 / M5|82/121|83/121|87/121|
|自然52 / M4|35/52|33/52|35/52|
|自然52 / M5|26/52|27/52|28/52|

带理由臂有真实开发选择增益，候选池含正确键时的选择从38/71升为46/71；但自然M5原生单元均分49.26%→48.15%，自然保持配对双正确两骨干均少1对。无理由臂未形成合计输入净收益。两者暂不进入默认路径，`adopted_B_five_operations_v1`与`f_disagreement_reanswer=false`保持。这些是已暴露开发结果，不是独立泛化成绩，也不是五个新LLM专家的协作成功。

新增780次物理取分、5,504,408输入token、780输出token，0新运行错误；176验证输出＋14 NLI原F直返。无旧F重生成，无早停补样，无新普通重答。先前32次初始化失败及8次失败回退单列保留，不能用成功恢复将其抹去。历史M5原B不可用1题仍留完整分母。

[数据说明](data/README.md) · [全部对照/分层质量](data/quality_summary.json) · [真实成本](data/cost_summary.json) · [原116项交付索引的公开映射](data/public_delivery_index.json) · [实际源码入口](SOURCE_ENTRY.md) · [持续记录快照](docs/research/cf_moa.md#candidate-verify-results-20260924)

公开逐题/调用文件是白名单**元数据投影**，不是完整私有模型trace。原病例、允许检索材料、messages、完整响应、gold与SQL仍在服务器，路径和哈希可追溯；不从公开元数据推断完整医学因果审计。源代码内固定方法提示公开，实际病例填充内容不公开。此包依赖已发布旧调用链及服务器环境/数据/权重，不称为独立可运行软件。

前一阶段：[v4真实调用链与95组诊断](../2026-09-24_cf_moa_v4_diagnosis/README.md)；[最简旧head复用实验](../2026-09-24_cf_moa_minimal_v4/README.md)。这些历史包及仓库已有计划保持原字节。本轮来源计划见[原始指令](plan/CF_MoA_V4_Source_Diagnosis_and_Coding_Instructions.md)、[下载来源收据](plan/download_receipt.json)与[运行冻结计划](plan/runtime_plan.json)。

公开一致性检查：`python3 check_publication.py`。它只读取本包，核对字节、分母、计数与已保存费用；不会访问私有样本或重新评分，不能替代独立重现实验。
