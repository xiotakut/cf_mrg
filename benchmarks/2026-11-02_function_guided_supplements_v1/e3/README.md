# E3：已有操作消融与覆盖联结

这是保存结果的离线重汇总，零新增模型请求/评分/模拟；来源 SHA 见[收据](receipt.json)。

- [支持增删](support_operation_controls.csv)：123 输入，M4 完整/禁 add/禁 remove 为69/43/53，M5为71/48/60；同一事实与路径上比较。
- [候选目录](candidate_controls_680.csv)：680 诊断单元，七配置平均原系统20.97%→单次目录45.44%；额外排列/校正单列。
- [后果执行](consequence_controls_288.csv)：24 profile、288 条件的给定模型面板，与临床 v5 分开。临床A4激活为0。
- [保持对照](invariance_matched_controls.csv)：保留普通共识与任务适配的原结果、保持/相关变化边界；不推为通用不变性已解决。
- [操作图](operation_controls.pdf)与[覆盖图](functional_coverage.pdf)同时区分执行、共享、回退与不适用。

这些面板的分母、评价协议和证据层不同，不合并为一个总分，也不把历史组件成绩当成当前完整 CF-MoA 成绩。
