# 近期工作、实现调整与 v5 完整结果归档

发布快照：2026-09-13。汇集 09-09 至 09-13 的数据构建、方法实施、正式评测、性能排查、输出修复和论文分析记录；更早工作通过现有归档和工作区指南连接。以落盘报告、配置、完成标记及验证收据为依据。

**当前结果入口：[M0 / M2 / M3 / 新 M4 / M5 完整对照](completion/v5_benchmark_latest/README.md)。** 五方法均完整覆盖 13,905 输入；M4 已完成结构约束修复全测，旧 M4 保留为历史。M6 52 条、M7 1,646 条均暂停，未恢复。

[完整文档目录](DOCUMENTS.md) · [逐文件来源](SOURCE_MANIFEST.csv) · [本地大型制品索引](LOCAL_ARTIFACT_REFERENCES.csv) · [发布验证](publication_validation.json)

## 工作时间线与具体调整

| 阶段 | 实际工作与调整 | 结果 / 证据 |
|---|---|---|
| 数据构建 | 保留 v3；完整 v4 分类及资格整理；v5 保留全部合格 R1–R4，R5 八来源各随机 450；evaluation_labels 与原 labels 分开 | [构建总记录](construction/paper_work_record_20260913/README.md)、[既有公开 v5](../2026-09-10_r1_r5_v5/README.md) |
| v3 基线与接口 | 追溯 M0/M1 身份；M2 兼容复用与补测；M3 原生接口、长证据与投票终态调整 | [v3 方法记录](workspace_reference/R1_R5_V3_BASELINES_WORK_RECORD.md) |
| M4/M5 安装与配置 | 安装 MedRAG、本地骨干与依赖；M4 从原 RRF-4 配置改为与 M5 对齐的 BM25＋MedCPT crossencoder / MedCorp，记录语料、top-k、温度、上下文差异 | [安装记录](m4_m5_implementation/M4_M5_INSTALLATION_REPORT.md)、[实施总记录 §3](execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md) |
| 原 v5 四方法 | M0/M2 精确复用并补测，M4/M5 全测；保留原生题型、必要证据与冻结评分 | [完整结果及覆盖审计](execution/results_v5_m0_m2_m4_m5/RESULTS.md) |
| M4/M5 输入读取加速 | 为 1,166 个 PubMed 分片补齐行偏移；32 文本读取 4.3263 秒→0.001511 秒，内容一致，历史样本 prompt/token ID 一致 | [工程证据 §4.1](execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md) |
| M2 性能分析 | 批量 64、显存比例 .75；保留每题完整 13 阶段调用；记录阶段耗时，未削减候选或方法步骤 | [阶段剖析](execution/results_v5_m0_m2_m4_m5/m2_stage_timing_profile.json) |
| M3 续测与等价优化 | 复用 3,690，补跑 10,215；熵计算向量化，保留候选、查询、种子和投票语义，微基准及响应一致性检查 | [最终结果](execution/results_v5_m3/RESULTS.md)、[性能记录](execution/results_v5_m3/performance_notes.md) |
| GPU 调度与监督 | 不重叠输入分片、阶段缓存续跑；GPU0 保护性借用、显存变更与自动退出；GPU3 加入，动态移交已授权任务 | [完整时间线 §5](execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)、[M3 五分钟记录](execution/results_v5_m3/supervision.jsonl) |
| M4 有效率排查 | 核对同骨干 M0/M2；检查输入修改与历史配置；旧 RRF 试跑因索引不齐未执行；发现 JSON 控制字符、选项键＋文本等失败 | [总记录 §10](execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md)、[旧配置预检](execution/results_v5_m0_m2_m4_m5/old_m4_pilot/README.md) |
| M4 100 题修复试验 | 固定题与历史检索证据；原版→提示→提示＋Schema：格式 65→92→98，原生 53→76→84；新增 200 预测 | [试验记录](execution/results_v5_m0_m2_m4_m5/m4_format_pilot/README.md) |
| M6/M7 复现接入 | 锁定上游与环境，补齐 M7 无动作输出作为 Final Answer 提议的上游处理；M6 去除非上游逐字查询门槛等；原生试跑与轨迹审计 | [完整论文复现记录](m6_m7_implementation/PAPER_REPRODUCTION_RECORD.md)、[方法忠实度](m6_m7_implementation/method_fidelity.md) |
| M6/M7 批处理尝试 | HF 并发调整；按阶段、答案类型和长度分组；完整预算不变；64 路观察未支持提速，后续恢复 32 | [历史运行](completion/results_v5_m6_m7/formal_balanced/README.md)、[完成分片吞吐](completion/results_v5_m6_m7/formal_balanced/logs/m7_completed_chunk_throughput.json) |
| M6 formatter 修复 | 两种生成式 formatter 各跑 40 条，出现改选而未采用；确定性显式字典兼容转换 52 条，协议 41→52 有效，原生 35→43，保留答案值 | [试验、验证与未部署补丁](execution/m6_formatter_pilot/README.md) |
| M7 保存与诊断 | 暂停 1,646 条：1,026 有效、620 无效、0 运行失败；无效分为 294 已接受答案协议问题、272 预算耗尽、54 动作解析失败；未强行接受被门槛拒绝的答案 | [审计](execution/m7_validity_audit/README.md)、[保存点](completion/results_v5_m6_m7/formal_balanced/checkpoints/m7_paused_20260913_1345/summary.json) |
| 修复 M4 全测 | 13,905 条全部新生成，复用历史证据；109 分片三卡 vLLM，71.86 分钟含加载；输出契约＋xgrammar，格式 99.09%，原生 79.42%，ALL 48.20% | [最终报告](completion/results_v5_m4_structured/RESULTS.md)、[完成标记](completion/results_v5_m4_structured/complete.json) |
| 分类与论文分析 | 保留原 M4 图，生成新 M4 五方法表图、错误分解与有效率；区分实现纠错、工程优化和未证实的研究候选 | [最新分析](completion/v5_benchmark_latest/README.md)、[原 M4 历史分析](execution/v5_category_priority/README.md)、[贡献讨论 §15](execution/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md) |

## 论文使用时的版本与指标

- 当前主要结果采用修复版 M4，原 M4 用于修复前后对照。两版逐题预测独立保留；方案选择试验也单独保存。
- 格式有效率、原生有效率、严格 JSON/Schema 有效率和原生正确率不同。最新有效率按 13,905 个唯一输入统计；历史一些核查按 15,616 条评分映射统计，不能混用分母。
- M6 推荐的是确定性显式输出解析；生成式 formatter 虽提高格式成功率，却改变部分已有答案，未采用。52 条非代表性样本不足以保证全库 100% 有效。
- M7 的协议问题、预算结束与熵/步数门槛拒绝不同；没有把未接受候选强制变成有效结果。
- 行偏移、熵向量化属于工程优化；微基准不是端到端加速比。M6/M7 提高并发的失败观察也保留。
- 修复基线后再讨论新优化方法。约束解码已有先例，当前工作没有确立新的算法贡献；v5 已用于问题发现，后续机制研究需要独立验证。

## 制品与复现边界

本目录包含完整叙述文档、图表 PNG/PDF/SVG、CSV 汇总和单元分数、配置、实现代码及补丁、诊断和完成收据、部分资源监督记录。原始文档只调整阅读入口、本地链接和当前状态提示；历史的“运行中”“未执行”均指对应时间点。

[来源清单](SOURCE_MANIFEST.csv)逐一映射发布文件与服务器源文件；其中 source_bytes 是源文件大小，Markdown 因链接适配可能不同。不能点击下载的本地制品保留原路径，并列入[本地引用表](LOCAL_ARTIFACT_REFERENCES.csv)。工作区指南是历史参考快照，不是发布仓库的运行指令。

原始 benchmark 正文、全部逐题响应及中间请求、权重、密集索引、环境目录和大型缓存未重复上传。原始题型和来源依赖仍按既有数据发布记录获取。候选修复代码作为快照保存，不代表已经部署；已有执行脚本含服务器路径、端口和历史进程操作，应按环境与当前任务重建，不能直接用于恢复旧进程。

在本仓库无需模型即可运行：

```bash
python3 benchmarks/2026-09-13_v5_complete/check_publication.py
```

它核对本次发布的文档链接、来源文件清单、五方法分类 CSV 与单元分数/错误分解、有效率分母及 M4 完成收据。原 build_report.py 保留实际绘图来源链，需要原始评分制品与已记录 Python 环境；本次发布不重新生成模型输出，也不重做显著性检验。

## GitHub 同步记录

本次从 GitHub main 的 c71581f 建立独立工作区；保留原首页为 README_HISTORY.md，更新根 README 与 benchmarks 导航，加入本目录及发布验证脚本。没有修改冻结标签、原生评分器、正式预测或当前进程。Git 提交记录提供此次发布的变更边界。
