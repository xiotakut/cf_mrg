# 聚合配套：功能收益保留

复用[已公开六臂冻结结果](../../2026-10-29_cf_moa_post_aggregation_full_v1/README.md)，零新推理/评分。主表保留R1–R5、Avg-R及ALL，类别多标签，Avg-R与ALL不同。

[六臂主表](system_main_table_pct.csv)、[相对B收益变化](gain_retention.csv)、[保持/应变配对](pair_behavior.csv)、[来源hash](receipt.json)。M5 Gen保持双正确4453/6838接近B4460/6838，但应变193/1780低于B360/1780；RulePrompt应变360/1780。该分析验证聚合是否保留已有功能收益，不能替代功能分工的受控对照。
