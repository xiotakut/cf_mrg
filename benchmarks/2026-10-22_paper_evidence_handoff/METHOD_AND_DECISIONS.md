> 轻量阅读副本：下文“本包”、原路径和历史核查状态按完整交接包的范围理解。本轻量目录真正交付哪些文件，以根目录 `EVIDENCE_INDEX.csv` 和 `SELECTION_AND_VALIDATION.json` 为准；缺少的层不能视为已经取得。

# 方法事实与研究决策

核查日期：2026-10-22。这里区分实际代码/请求所支持的事实、保存记录中的选择理由、仍未核实的历史。原始路径是溯源标识；用 `FILE_MANIFEST.csv` 的 `package_path/encoding` 读取交付文件，不能把原路径当作接手 agent 已有的文件。所有研究文档在本包中仍是主张及决策线索，不是完整性或医学正确性的独立担保。

## 1. 方法身份与真实路由

**最终默认为 B（C1），C3 是研究扩展。** `cf_moa_minimal_revision_20260923/decision.json` 保存 `adopted_B_five_operations_v1`；RCV 的 `closeout_20260928/method_identity.final.json` 和 `final_status.json` 明确保持 B、C3 不默认采用。双骨干全量 C3−B 的 ALL 分别为 −1.8108、+0.9273 个百分点，方向不同。不能把 B−C0 的约10.09/12.01点归给新增候选验证模块。[逐项核查与原路径](audit/cfmoa/findings.md)

**B 是按当前输入能力稀疏选择已采用组件，不是五个独立模型同时讨论。** `cf_moa/controller/strong_legacy.py`、`minimal_operations.py` 显示目录诊断、规则执行、给定模型执行、F读出及透传的能力判断；不以离线 R 标签作为路由输入。A1/A2共享规则执行与组装，A3使用目录比较，A4要求可执行模型和状态，A5包装已采用F。全量保存路由每骨干：目录3,560、规则123、F 10,178、透传44，A4为0。全量 R4 标签成绩因此不等于 A4 被调用的临床验证。[实际路由字段及核查](audit/route_counts.json)；[组件说明](audit/cfmoa/findings.md)

C2在旧F普通投票的同一合法候选池上做二元核验，C3加入已有理由，C4扩展旧池并多三次普通重答，C5联合选择同候选及理由。C2/C3各次A/B先softmax归一，再平均互换编码后映射的TRUE概率排序，返回已有完整响应；分数没有临床概率校准。NLI路径仍用旧F。实际消息、schema、seed、温度见原 `model_calls`，不得以当前模板代替已发出的提示。六臂定义与实现绑定（完整归档路径：`audit/cfmoa/tables.json`；本轻量目录未交付）

## 2. 七系统及参数解释

七配置是 M0、M2、M3、M4、M5、MedGENIE M6、M7，共六方法家族。历史M1为初始检索对照；历史i-MedRAG M6保留原身份，不能改名成MedGENIE。M4使用修复的结构输出、M5保留原协议，检索语料及预算亦有差异，不能将其差值全部解释为纯骨干或纯算法效果。[完整配置与版本核查](audit/baselines/findings.md)

- M2保存的all-Llama配置为初始5文档、3知识点、5生成文档、10个KADS候选、最终5文档。
- M3为Qwen3-8B，8候选、至多4轮；solver温度0.7/2048 token、关闭thinking；query温度0/8192 token、开启thinking。MedCorp3、BM25总32、MedCPT取2；最高投票平局无效。M3合并预测的 `raw_response` 是投票序列化，真实模型原文另在请求缓存，包内导出按实际 `source_run` 取证。
- M4结构修复保留旧检索证据，生成2048、温度0.7、seed42，加入可见输入的JSON Schema；旧M4及两次100题试跑分别保留。
- M6为本地Llama generator/reader适配，3个选项相关＋2个自由背景（无选项时5个自由）；生成温度0.9、frequency penalty1.95、512 token，reader贪心/2048。不是原论文PMC-LLaMA数值复现。
- M7为Qwen3-8B，关闭thinking，8步/topK4/sigma1.2，以FP32全词表熵及typed控制运行。选择typed参考了同384输入开发结果，不能写成独立测试后确认其所有组件的因果贡献。

M0/M2/M3/M4/M5的实际运行完整代码版本未核实。M6/M7各109分片的生成代码/config/input hash可绑定，但评分器运行时版本未充分绑定。CF-MoA有20项主要源/评分源哈希绑定；A4有冻结副本和运行后未变收据；头部研究另有284项保存哈希找到当前或历史副本。所有这些都是局部范围，未扩写成模型权重、依赖闭包和语料整体完全锁定。基线版本（完整归档路径：`audit/baselines/runtime_versions.json`；本轻量目录未交付）；CF版本（完整归档路径：`audit/cfmoa/version_checks.json`；本轻量目录未交付）；头部版本（完整归档路径：`audit/heads/recorded_hash_checks.json`；本轻量目录未交付）

## 3. R1–R3、操作消融与A4

R1/R2/R3表分别有2866/79/733成员，联合只有2941唯一单位。R2及规则分支复用两套骨干事实，再组合七系统各自原答案；不能把共享事实计作七次生成。R3目录为49名称，评分器为46归一键；六种排列及校正的增量必须与单次目录分开报告。R3新增五系统实际请求18,714，另486复用，不把缓存回调当新推理。[ID交集、调用检查与代码路径](audit/heads/findings.md)

123输入支持操作消融复用相同事实和执行状态，将add或remove状态投影为UNKNOWN；并非重新训练或重新抽取事实。双骨干完整/禁add/禁remove正确数为69/43/53及71/48/60，所有无效输出留分母。[保存分数重汇总](audit/cfmoa/operation_reaggregation.json)

A4保留集为24个模拟profile×4情景×3时间点＝288题；typed patch二元、联合数值和完整输出指标两骨干都288/288，full联合数值正确数270/222，普通重答的联合数值正确数0/0，禁do为67/67。它要求给定模型、参数、完整初态和事实动作表，数值容差1 mg/dL，支持的是受限执行能力。不是288个患者，不是临床干预效应验证。开发6 profile与保留24 profile有实际冻结、后续请求、原响应和评分证据；准备文件的旧 `prepared_not_run` 状态不能覆盖后来的真实完成记录。[A4核查](audit/heads/findings.md)

## 4. 评分、分母、复用与费用

v5固定6104单位/13000选中判断；每系统13905唯一输入、15616原生评分映射。主均值排除6818条reference映射，将8798条非reference映射先在单位内平均，再对单位等权；类别可重叠。ALL不是五类均值，也不是13905输入准确率。保持/响应对分母6838/1780，要求两端均对。输入格式分解包含reference，因此与ALL不同。[协议核查](audit/baselines/coverage_and_reaggregation.json)；CF连接检查（完整归档路径：`audit/cfmoa/join_checks.json`；本轻量目录未交付）

本次只使用保存的correct/invalid等结果，不重新解析答案或运行评分器；无效、不可用、投票平局仍保留原分母。诊断归一与原生评分有医学语义和参考粒度限制，本次数值一致不证明评分或标签医学正确。

M0为5028新输出＋8877复用；M2为7218＋6687；M3为10215＋3690。M6/M7终态13,905不等于模型调用数。CF-MoA全量跨臂物理请求162,979与各方法继承成本是不同账本，不能相加或除以六。C0共同上游费用未知；每骨干2503个旧head输入模型耗时缺失，不能将已知小计写成完整端到端成本/速度。39/36物理请求与终态行差额、M5失败callback与回放保留原对账。[费用检查](audit/cfmoa/cost_reaggregation.json)

## 5. 已保存的研究选择与负结果

采用原因只引用历史decision或明确记录，不从最终分数反推动机。具体证据路径均在相应审计报告和RUN_REGISTRY；没有明确依据的条目仍写“未找到依据”。

| 决策/路径 | 实际证据及应保留的解释 |
|---|---|
| i-MedRAG被MedGENIE替代 | 旧正式链仅52/13905；其dev_v2有请求但缺终态，vLLM128试跑全部failed后有恢复；不抹去旧身份与失败。见基线审计。 |
| TC-RAG typed采用 | 同384输入typed与recovery-only试跑均存在；早期GPU2初始化OOM后实际在GPU0恢复。选择参考开发结果。 |
| R3候选与控制 | 单次目录解释了大量改善；校正并非跨系统稳定增量。病例记忆、关系/NLI、反向似然等实际试验保留，不能改名并入最终A3。 |
| R5研究未完成 | 最终旧F与后续监督/实体视图研发不同。entity-view880前向、0生成且未采用；最后五头仅计划，与前面的真实训练失败分开。 |
| 早期CF-MoA全聚合放弃 | 两骨干121组的79/74低于B87/82；A1/A5及单agent控制多次部分完成/失败，真实status和输出均保留。 |
| 最简版本B保持 | 231新请求及自然52三seed结果未稳定支持普通F重答；不按最好seed选写。 |
| 四轮effect-first未采用 | cycle1–4均有输出与decision；末轮34输入18/15低于B23/19，截断及旧B不可用保留。 |
| C3仍是扩展 | 两骨干全量方向相反；最终method identity文件显式保持B。 |

[基线全过程发现](audit/baselines/findings.md) · [头部及A4/R5发现](audit/heads/findings.md) · [CF-MoA全过程发现](audit/cfmoa/findings.md)。更早DeltaRev/DeltaRank/CFShift/CF-KADS-MoE/RiskRoute/MA-RAG迁移单独登记为历史范围，原始预测已读取计数；不拿其配对结果直接与v5比较。[历史制品计数](audit/history/artifact_row_checks.json)

## 6. 开发暴露和独立性

完整v5、历史121、自然52及多轮参数/格式试跑已参与开发或方法选择。冻结数据身份、缓存接口回放通过与重新汇总不能把这些范围变成未触碰测试。

A4保留profile、ASCENT47、CUPCase三批18条及部分旧F冻结后检查确有执行；它们各有来源、资格、模拟机制、后续暴露限制，不能代替最终CF-MoA共同冻结后的独立临床确认。R1后续refinement在看过验证结果后继续，属于再次开发。CUPCase校正两骨干15/16、未校正16/17，不能称已证实稳定泛化改善。[逐项范围检查](audit/heads/findings.md)

最终CF-MoA新的family确认、独立F候选池复本、历史自然52 M5 C0四缺项补齐，均有显式未执行/延后状态。confirmation内准备脚本、draft、输入、CPU测试仅证明准备工作，不能写成真实确认运行。[检查范围、显式状态与原文件](audit/cfmoa/findings.md)
