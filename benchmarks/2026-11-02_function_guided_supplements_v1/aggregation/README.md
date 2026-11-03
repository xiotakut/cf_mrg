# 聚合配套：功能收益保留

复用[已公开六臂冻结结果](../../2026-10-29_cf_moa_post_aggregation_full_v1/README.md)，零新推理/评分。主表保留R1–R5、Avg-R及ALL，类别多标签，Avg-R与ALL不同。

[六臂主表](system_main_table_pct.csv)、[相对B收益变化](gain_retention.csv)、[保持/应变配对](pair_behavior.csv)、[来源hash](receipt.json)。M5 Gen保持双正确4453/6838接近B4460/6838，但应变193/1780低于B360/1780；RulePrompt应变360/1780。该分析验证聚合是否保留已有功能收益，不能替代功能分工的受控对照。

## 收益保留率的两个定义

`gain_retention.csv`的ALL单元归一加权修复保留率为：

`sum(w × I[C0错、B对、聚合对]) / sum(w × I[C0错、B对])`

RulePrompt的M4/M5分别为88.5078%／98.9107%；权重w是在对应类别/单元内对非reference映射归一，因此不是简单逐条计数比例。

总体净增益比则为`(Acc(RulePrompt)−Acc(C0))/(Acc(B)−Acc(C0))`，分别93.5184%／93.6994%。这两个量不互换，也不统称无定义的retention。

## 真实保存的展示案例

[3个QA全文及保存输出](illustrative_saved_examples.jsonl)：支持v03617、候选v00011、保持v09066。每例保留record/request/judgment ID、题目/参考、C0、功能候选及Gen/RulePrompt输出，并记录事后选例规则。它们用于说明机制，不是盲审错误频率样本，也不是E5确认数据。
