# M4 提示词 + JSON Schema 试跑结果

完整设置、结果与局限见[试验主记录](<../m4_format_pilot/README.md>)。100题全部完成，严格JSON对象99/100，原生格式有效98/100，原生有效84/100。剩余格式无效为1条2048-token截断和1条含糊诊断，未进行结果修补。

- [对照计数](<comparison.json>)
- 逐题评分（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/scored.jsonl`）
- 原始输出（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/predictions.jsonl`）
- [有效配置](<config.json>)
- 完整修改后输入（本地制品：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/m4_format_structured_pilot/inputs.jsonl`）
- [结构验证](<schema_validation.json>)
- [GPU0保护退出记录](<guard_result.json>)

本目录为独立试验，不替代原正式M4结果。
