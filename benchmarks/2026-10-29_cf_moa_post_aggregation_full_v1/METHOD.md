# 本次实际执行的方法

第一阶段为每个输入建立 A1–A5 五个提议记录，复用已冻结的完整专家响应与操作证据。
A1/A2 共享同一次规则执行的完整组装答案；A2 为规范选择槽。工具不适用的角色携带明确标记的 C0 fallback。
五个角色记录完成后才进入后置聚合；五个记录不代表五次新的模型生成。

| 实验臂 | 聚合行为 |
|---|---|
| Gen | 模型综合生成完整原生答案 JSON |
| Select | 无任务优先级的候选 ID 选择，完整复制候选 |
| RulePrompt | prompt 中给出旧能力优先级，模型自主选 ID，完整复制候选 |
| Strict | 复用 RulePrompt 原始模型响应，按同一旧策略校验/纠正，然后完整复制候选 |

固定优先级为：diagnosis→A3；否则旧规则适用→A2（A1/A2完整联合结果）；否则完整给定模型可执行→A4；否则 single/robustness_single/relation 且 original_context 非字符串→A5；否则 C0。
RulePrompt 也计算期望选择以记录遵循率，但不会用它覆盖模型选择。Strict 才强制使用期望选择；解析/容量失败也保留原能力选择及完整候选，不隐藏原专家不可用状态。
原生答案对象与聚合解释分开保存；不只复制答案字母，不让聚合模型重写所选候选。

五提议、聚合请求、解析与最终提交实现分别见 `source/post_proposers.py`、`source/post_selective.py` 和 `source/strong_legacy.py`。
源码是实际运行时的研究快照，文件内保留试跑版本名和原机依赖；本目录不是自包含的 GPU 推理安装包，也不将旧源码的 pilot 名称误解为只运行小试。全量范围由冻结输入与最终收据确定。
`source/analyze_full.py` 与 `source/original_full_audit.py` 是原评分/验收来源；它们需要本地私有运行材料。公开可运行的离线结果核对入口为 `scripts/verify_results.py`。

运行中出现过零提交的 socket 路径、显存 profiling 和 setup 绑定失败，后续修复后继续；监督器统计文件竞争也曾导致收尾监督退出并被接管。请求边界交接保留 42,492 份已有结果、未知请求为 0；未重提已提交请求。
原被接管进程 OS wait 退出码未知，保留原停止保护异常；四个新增并行 worker 的 wait 退出码均为 0。原故障及恢复证据仍在完整本地运行包，不能把最终成功改写成从未失败。

公开逐单位、输入、配对和过程 gzip 逐字复制原产物。逐映射数值文件通过白名单投影去掉 prediction/semantic_gold/semantic_prediction、文档检测明细、缓存来源与答案引用；source_manifest.json 记录来源 SHA、字段清单和转换方法。指标、样本及失败分母不变。
