# R1–R3：从失败机制到支持更新方法

发布快照：2026-09-16。主稿串联类别表现、错误原因、失败尝试、改进依据、方法设计和实验结果。

**[阅读全文：医学反事实问答中的支持更新与候选重决策](docs/research/support_update_method.md)**

## 阅读入口

- [R1 研究与后续验证](docs/research/optimization.md)
- [R2 支持重算：运行、调整与失败记录](docs/research/r2_support_head.md)
- [R3 候选比较：运行、调整与失败记录](docs/research/r3_candidate_comparison.md)
- [R1–R5 分类定义](docs/data/classification.md)、[输入与评分协议](docs/evaluation/protocol.md)
- [截至 09-16 的七方法正式 v5 结果](docs/evaluation/v5.md#current-seven-methods)
- [会话与文档阅读范围](evidence/reading_scope.md)、[阅读清单](evidence/reading_manifest.json)

## 快照范围

保留主稿、三个研究主记录、分类与评测依据，以及主稿直接引用的小型分析和运行说明。原始研究事实不作改写；主稿公式采用 GitHub 支持的数学分隔符。发布副本将已收录文档链接转换为仓库相对路径，未收录目标改为服务器来源文字，统一列于[本地制品索引](LOCAL_ARTIFACT_REFERENCES.csv)。逐文件来源见[SOURCE_MANIFEST.csv](SOURCE_MANIFEST.csv)。

本文中的 head 成绩属于已暴露开发范围；正式 v5 基线、受控机制证据与新来源验证分别报告。历史章节按当时状态理解，最新研究结论见主稿和各记录顶部。本次发布没有新增模型实验。

原始会话 JSONL、完整患者/模型轨迹、模型权重和大型缓存保留在本地。此目录是 09-16 的发布快照，后续持续研究记录仍在服务器 `/home/data3/txy/docs/` 维护。
