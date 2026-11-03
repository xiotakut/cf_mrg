# 功能分类与 CF-MoA：已完成补充实验

更新：2026-11-03，交付修正版v2。E0、最终修正后的 E1、E3、E4a、E4b、E5 及聚合配套分析已完成并发布；[E2-lite 审计](e2/README.md)已在此前发布，原人工审核包仍保留且人工标注为 0。

本包把跨任务功能诊断、受控操作、指令条件化和聚合保留分别检验。结果包含负结果与骨干差异，不支持“所有功能代理普遍优于统一处理”。

| 实验 | 范围与主要结果 | 结果入口 | 新模型请求 |
|---|---|---|---:|
| E0 文献覆盖 | 8 项工作；区分任务内分类与跨任务功能分类 | [覆盖矩阵](e0/coverage_matrix.csv) · [说明](e0/README.md) | 0 |
| E1 功能异质性 | 7 配置、6,104 单元、4,216 保守家族；加入功能信息后 OOF Brier 0.177945 → 0.176789 | [汇总](e1_corrected/summary.json) · [同来源/格式](e1_corrected/supported_within_source_contrasts.csv) · [图](e1_corrected/functional_diagnostics.pdf) | 0 |
| E2-lite 证据审计 | 120 目标、600 关系判断；模型辅助质量诊断，非专家验证 | [报告](e2/E2_LITE_AUDIT_REPORT.md) · [逐项结果](e2/e2_lite_model_audit.csv) | 对话中分 12 批，未另发 API 请求 |
| E3 既有操作消融 | 支持增删、680 诊断单元、288 给定模型条件及保持控制；不同面板分开报告 | [说明](e3/README.md) · [操作图](e3/operation_controls.pdf) · [覆盖图](e3/functional_coverage.pdf) | 0 |
| E4a 同信息执行 | 各 123 输入；程序/统一 LLM 正确数 M4 **69/50**、M5 **71/71** | [结果](e4a/analysis/overall.csv) · [说明](e4a/README.md) · [图](e4a/analysis/terminal_execution_comparison.pdf) | 246 |
| E4b 指令条件化 | 各 80 输入；统一/条件化正确数 M4 **27/28**、M5 **41/40**，无一致增益 | [结果](e4b/analysis/overall.csv) · [区间](e4b/analysis/paired.csv) · [说明](e4b/README.md) | 320 |
| E5 冻结后小面板 | **仅 R5**，32 家族、每骨干 112 端点；RulePrompt−C0 +4.79/+4.38pp，区间均跨 0 | [主表](e5/analysis/primary_unit_mean.csv) · [区间](e5/analysis/unit_contrasts.csv) · [说明](e5/README.md) | 1,479 |
| 聚合配套 | 复用已有完整六臂结果，按功能/配对分析收益保留 | [主表](aggregation/system_main_table_pct.csv) · [收益保留](aggregation/gain_retention.csv) · [配对](aggregation/pair_behavior.csv) | 0 |

M4/M5 指项目中 Llama/Qwen 两套配置。E4a/E4b/E5 共 **2,045 次实际请求**，输入 8,710,487、输出 520,453 tokens；其中 1,981 次生成和 64 次单 token NLI 取分。没有重跑上游检索或全量基线。本次上传另新增模型请求 0。E2 对话审计的推理消耗没有可用 token 账本，不能算成零计算。

## 阅读与复核

**[下载v2完整包：包含E2全部审计与原材料](completed_supplementary_experiments_v2.zip)** · [ZIP校验值](DOWNLOADS.json) · [本次交付修正清单](DELIVERY_NOTES.md)

[v1原包（保持原字节，不含E2）](completed_supplementary_experiments.zip)继续保留；v2不改变实验评分或原审计判断。

1. 先读各实验说明，确认样本、分母、复用/新运行身份和适用范围。
2. 查看 CSV、PDF/PNG 和逐项保存分数；无效/不可用输出始终保留在分母。
3. 按[离线复核说明](REPRODUCE.md)运行`python3 verify_saved_results.py`及`python3 verify_delivery.py`；E1重拟合用`reproduce_e1_fixed_folds.py`。均不需要GPU或模型下载。
4. [SHA-256清单](MANIFEST.json)覆盖v2交付文件；[原发布来源](provenance.json)和[补交来源](delivery_provenance.json)记录复制/投影。E2保留自身清单，同时纳入v2总清单与完整ZIP。

本包提供完整分析表、逐项评分投影、家族划分、请求与实际接受参数的摘要、原执行脚本快照。除E2既有审核材料及明确标出的聚合/E4a展示案例外，全量病例、请求正文、自由文本回答和运行日志仍留在原运行证据中；本包不是可脱离来源数据与模型权重直接重跑的独立推理发行版。`native_scored.jsonl`只移除`native_answer`，所有评分字段/行均保留，不重新评分。提示模板在`source_snapshots/prepare_*.py`及`run_*.py`中。

## 结论边界与修订

- E1 使用已暴露 v5；小幅预测增量不是因果“纯功能难度”。仅采用 `e1_corrected/` 的 4,216 家族版本；早期划分快照放在 `history/`。
- E4a 是冻结事实/规则/状态/作用域下的终端执行对照，不是完整 generalist MoA 对照。M5 总分相同也不等于逐题等价。
- E4b 只改变合法能力信息的指令强调；两臂证据、资源、接口和单次额度相同。没有取得跨骨干一致收益。
- E5 只确认有限 R5 范围。32 家族等权、64 非 reference 判断、112 全端点和64保持配对是不同分母；不混用。BioNLI 文章级独立性仍未确认。
- E5 RulePrompt 与 B **224/224 最终判断相同，完整响应仅 209/224 相同**。选择后完整复制与相对 B 的字典相同是不同检查。
- E5 原始 66 次 `finish_reason=length` 包含 64 次预定单 token 取分；真正生成额度停止仅 2 次。连同 E4a 7 次，共 9 次。见 [停止原因分解](e5/analysis/stop_reason_breakdown.csv)。
- E4b离线R5标签参与current_decision候选池筛选；标签不进入模型提示。上版“仅作事后分析”已更正，不改变冻结实验。
- E2 不是独立临床专家标注，不报告人类一致性或分类准确率，不自动修改主表。

## 历史与来源

[完整后置聚合结果](../2026-10-29_cf_moa_post_aggregation_full_v1/README.md)提供聚合配套的上游冻结结果。[本包运行/修订摘要](history/README.md)保留失败和纠正身份。`validation/`中的收据为当时冻结快照，其中“E4b/E5尚未启动”“人工审查延期”等旧状态以本页及各实验当前说明为准。
