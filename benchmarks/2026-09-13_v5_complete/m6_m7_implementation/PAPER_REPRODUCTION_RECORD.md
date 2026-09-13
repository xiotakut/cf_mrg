# M6 i-MedRAG 与 M7 TC-RAG：实现、调整及论文写作记录

> 发布状态（2026-09-13）：[最新五方法结果](../completion/v5_benchmark_latest/README.md)已全量完成，M4 采用修复版；M6/M7 均暂停。下文过程状态与执行命令按其原记录时间理解。

更新日期：2026-09-13（Asia/Shanghai）。本文根据已保存的源码快照、配置、请求收据、运行日志和离线报告整理本轮实际工作，供论文 Methods、Implementation Details、实验记录和局限性部分使用。后续修改继续追加日期、改动原因及对应制品，不覆盖本次记录。

**编号约定（用户2026-09-13指定）：M6 = i-MedRAG（`imedrag`），M7 = TC-RAG（`tcrag`）。** 本轮R1–R5比较和后续论文使用这两个编号；代码、配置及历史制品继续使用括号中的执行标识。旧MedRGAG消融及Gate D实验中的同名编号保留其历史实验含义。

**当前结论：两种方法已接入现有项目，通过19项自动测试，并分别完成24条固定开发输入的真实模型运行及轨迹审计。i-MedRAG有19条有效、5条无效；TC-RAG有9条有效、15条无效。输出格式和开放诊断评分兼容性仍有问题，尚未完成全部来源的真实验收及正式评测。**

新增方法只有 `imedrag`、`tcrag`。M20＝MedCounterFact、M22＝MedRGB、M23＝BioRAB是项目原有的**数据来源编号**，出现在输入适配和评分记录中，不是新增方法。没有新增 CF 方法、CF adapter、专项 verifier 或更强的辅助模型。用户所述论文的7个医疗QA benchmark属于来源论文设置；本次继续使用服务器已确认的 R1–R5 v5，没有重新选择 benchmark。

## 1. 实际完成的工作及代码位置

服务器运行包位于本文件所在目录；项目入口为 run_iterative_baselines.py（本地制品：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/run_iterative_baselines.py`）。入口用 `runpy` 调用本运行包，支持 `CF_ITERATIVE_BASELINES` 指定部署位置。沿用已有 dated-run-pack 组织方式。

| 工作 | 实际实现 / 复用内容 | 证据入口 |
|---|---|---|
| 来源固定 | 阅读原论文及官方实现，记录版本、SHA、许可证和论文/代码差异 | [method_fidelity.md](<method_fidelity.md>)、[source_resolution.json](<reports/source_resolution.json>)、`upstream/` |
| i-MedRAG | 4轮追问、逐问检索和回答、跨轮QA历史、最终分析与格式化；安全解析和确定顺序 | [methods.py](<code/methods.py>)：`imedrag`、`parse_queries`、`final_json` |
| TC-RAG | 独立活动栈、真实工具、Backtrack、Summary替换、状态监控、接受及步数终止 | [methods.py](<code/methods.py>)：`tcrag`、`parse_action`、`state_signal` |
| 同权重生成和熵 | 增加 Transformers 后端，生成时计算完整分布熵；请求合批和独立随机数流 | [backend.py](<code/backend.py>)：`HFBackend`、`BatchingBackend`、`entropy_from_scores` |
| 检索接入 | `Retriever` 调用已有 MedRAG `src.baselines.make_retriever`；复用完整MedCorp、BM25及MedCPT | [backend.py](<code/backend.py>)、[resources.json](<configs/resources.json>) |
| 输入和资源冻结 | 接入已有v5物化输入，保留source→unit→target→input展开映射；固定开发包、模型、索引和环境身份 | [prepare.py](<code/prepare.py>)、[check.py](<code/check.py>)、[input_lock.json](<data/input_lock.json>) |
| 请求与恢复 | 保存完整prompt、原始响应、finish_reason、真实检索材料、尝试和终态；原子写入、请求级恢复和配置漂移拒绝 | [runtime.py](<code/runtime.py>)、[run.py](<code/run.py>) |
| 评分、审计和成本 | 接入已有原生评分器；离线重算历史、栈和熵；分别统计逻辑请求、新增计算、缓存及正式成本 | [score.py](<code/score.py>)、[report.py](<code/report.py>)、[cost.py](<code/cost.py>) |
| 执行入口和验证 | 环境准备、开发运行、恢复、离线评分及验收命令；19项隔离回放测试 | [run.sh](<run.sh>)、[acceptance.sh](<acceptance.sh>)、[tests/](<tests>)、[README.md](<README.md>) |

已有模型权重、MedRAG环境、语料、索引和重排序器直接复用；本轮没有训练模型或重新建设完整知识库。实际生成使用既有 MedRAG 基线环境：Python 3.10.12、torch 2.6.0、Transformers 4.51.3、accelerate 1.10.1、pyserini 1.0.0、Java 21；数据准备复用另一个已有环境。完整版本和路径见 [environment.json](<configs/environment.json>)、[requirements.lock.txt](<configs/requirements.lock.txt>)。

## 2. 固定来源与最终配置

### 2.1 方法依据

| 方法 | 原论文版本 | 官方仓库固定提交 | 许可证记录 |
|---|---|---|---|
| i-MedRAG | [2408.00727v3](https://arxiv.org/html/2408.00727v3)，2024-10-11，§3.2–3.3、Algorithm 1 | [gzxiong/MedRAG](https://github.com/gzxiong/MedRAG/tree/7599a728a28789fd601728c08d313b1148051f41)，`7599a728a28789fd601728c08d313b1148051f41` | NCBI US Government Work公有领域声明；GitHub API为NOASSERTION，不写成MIT |
| TC-RAG | [2408.09199v3](https://arxiv.org/html/2408.09199v3)，2026-09-03，§5、Appendix 8.6 Algorithm 1 | [Artessay/TC-RAG](https://github.com/Artessay/TC-RAG/tree/dd8f32f90832eeb452680cfdb02ca604988648d0)，`dd8f32f90832eeb452680cfdb02ca604988648d0` | checkout没有LICENSE、API为null；参考源码独立适配，不替上游声明授权 |

i-MedRAG论文中的作者仓库用户名与定位链接不同；本次API实际解析为 `gzxiong/MedRAG`，原始和resolved URL均已记录。引用代码时使用上表固定SHA。逐组件上游函数和本地函数对应关系以 [method_fidelity.md](<method_fidelity.md>) 为准。

### 2.2 最终执行参数及来源

最终配置为 [imedrag_runtime_v4.json](<configs/imedrag_runtime_v4.json>)、[tcrag_runtime_v4.json](<configs/tcrag_runtime_v4.json>)，`method_version=iterative-v4`。部分后续语法修复仍沿用这个版本字符串，因此论文制品身份还应引用各run的 `resolved_config.json`、`code_snapshot/` 和其中的源码哈希，不能只写“v4”。

| 条件 | 最终值 | 来源 / 说明 |
|---|---|---|
| i-MedRAG backbone | `meta-llama/Llama-3.1-8B-Instruct` | 当前项目M4设置；追问、解析、QA和最终格式化使用同一模型 |
| TC-RAG backbone | `Qwen/Qwen3-8B`，`enable_thinking=false` | 用户明确指定；Adaptive RAG baseline，状态也来自该模型 |
| i-MedRAG轮数 | `n_rounds=4`、每轮请求 `n_queries=3` | 官方函数/README默认；实际数由模型及解析结果决定 |
| TC-RAG控制 | `max_loop=8`、`topK=4`、`sigma=1.2`、初值100000 | 固定官方执行器；topK不是检索条数；最早第5次动作生成接受 |
| 模型精度/引擎 | BF16、Transformers、SDPA | 本地同权重执行后端；权重与tokenizer身份见 [resources.json](<configs/resources.json>) |
| 采样 | temperature=0.7、top_p=1、top_k=0、repetition_penalty=1、num_beams=1、seed=42 | 当前v5生成设置及后端固定参数；请求种子独立记录 |
| 模型窗口 | 131072 tokens；Qwen YaRN factor=4、original=32768 | 沿用当前M4/M5上下文配置 |
| 知识库和检索 | 完整MedCorp四库；BM25每库32，k1=0.9、b=0.4；MedCPT-Cross-Encoder重排top8 | 复用当前v5统一检索设置及已有索引；配置遗留 `rrf_k=100` 不参与本BM25＋MedCPT路径 |
| 追加证据预算 | 30000模型tokens | 当前v5追加检索上下文预算；原题及必需证据保留 |
| 阶段生成预算 | query/parse/QA各1024；final/format/TC action各2048 | 本项目分阶段工程配置，不写成两论文共同默认 |
| 请求重试 | 最多2次传输重试，退避1/2秒 | 本项目规则；OOM不当作传输重试 |
| 格式处理 | 查询提取最多1次同模型纯格式修复；最终最多1次确定性字面量转JSON | 本项目接口修复，完整记录原始输出与额外调用 |
| 并发和显存 | 4个输入工作线程，合批上限32000 padded tokens，`expandable_segments:True` | 真实共享GPU下的OOM修复；单个合法长请求仍完整执行 |
| 设备分层 | 实测用物理GPU1/2；Llama层12/20，Qwen层14/22 | 按共享显存余量分配；不是量化或更换小模型 |

TC论文附录另有 `uct=20 / cppl=10`、temperature=0.6、500 tokens等设置；本实现选择已核对的代码默认阈值和本项目统一生成配置，并在差异表披露，没有混用成所谓“论文原配置”。

## 3. 对方法具体做了什么调整

### 3.1 i-MedRAG

真实执行顺序为：原题Q及成功QA历史H → 本轮追问生成 → 同模型提取追问 → 每个追问独立检索和作答 → 按查询序号写入H → 下一轮 → 基于Q与H生成最终分析 → 同模型格式化。最后的追加上下文是QA历史；各轮动态检索正文不会直接合并给最终reader。任务本来自带的合法固定证据仍属于原题。

| 调整 | 原行为 / 问题 | 最终处理及影响 |
|---|---|---|
| 安全查询解析 | 官方依赖特定空格正则和 `eval()` | 保留上游LLM提取调用，用JSONDecoder读明确JSON；保存提取prompt、原始输出、状态和成本 |
| 限定格式修复边界 | 提取模型可能重写、截取、合并或补造查询 | 逐条定位原查询段、完整边界及原顺序；拒绝语义重写/拆合；无效轮次有记录，成功QA才进入H |
| 支持实际Markdown形式 | 实测出现加粗、编号标题、`### Query 1`、`### 1.`、`1. ##`及关键词括注 | 仅处理这些语法包装和无意义空白；保留问题正文，保护1.5等小数和-3等负数；没有凑足3条查询 |
| 每条QA独立恢复 | 早期同轮 `call_many` 以一个批请求收据保存，不利于局部恢复 | 每条QA独立future/请求收据；后端可合批，写回仍按原查询序号；轮间保持依赖 |
| 固定终止 | 上游除4轮外还允许3次自由循环，可能继续追问 | 本项目固定4轮后一次最终分析及一次格式化；这是明确的终止适配 |
| 最终格式提示 | 初版通用格式提示；中间尝试明确flat JSON和小写选项，随后恢复官方形式 | 最终保留 `Output the answer in JSON: {'answer': your_answer (...)}`；只按原生选项/多选/关系/诊断/错误文档字段适配 |
| 单引号字典兼容 | 模型模仿官方提示中的单引号字典，严格JSON接口拒绝 | `final_json` 用标准库 `ast.literal_eval` 读取完整字典后 `json.dumps`；拒绝重复字段、非字面量及值变化；不改大小写、诊断内容或增加LLM调用 |
| 失败与分母 | 仅最终输出合法不足以证明追问流程完成 | 有未解决追问问题仍记invalid；检索/QA请求失败记failed；不使用其他方法或Direct补答案 |

标准恰好3条有效追问/轮时，4轮共12条QA，加上4次生成追问、4次提取、1次最终分析和1次格式化，共 **22次LLM请求、12次检索**。这不是实际请求数的硬上限；实际查询数、格式修复和传输重试分别统计。

### 3.2 TC-RAG

| 组件 / 调整 | 实际控制流 | 与论文或上游的关系 |
|---|---|---|
| 栈及隔离 | 每题初始化不可删除的原题、状态100000和动作计数；Thought/Plan/真实工具材料进入活动栈 | 保留stack-based memory；并发输入、原题和变体不共享活动状态 |
| 工具 | 模型提出DOC_RAG查询，程序调用统一检索器并注入实际Observation | 统一MedCorp工具迁移；没有复制上游web/KG/NER异构工具系统 |
| 伪Observation | 原始模型响应完整保存，但模型生成的Observation及其后续内容在动作解析前截断 | 工具结果来自实际调用，不能把模型自行编出的Observation当检索证据 |
| Backtrack | 弹出栈顶，恢复下面栈项的状态；被移除内容及回退反馈仅留审计 | 按论文恢复记忆/状态；修复上游跨题state_value_list未清空及反馈重新入栈的问题 |
| Plan / Summary | 增加独立动作；Summary用模型总结**替换栈顶旧内容**，原题不能被移除 | 论文§5.1和算法包含这些操作，上游主执行器没有独立Summary分支；明确标为论文对齐补丁 |
| Summary状态快照 | 替换Thought后恢复下面栈项状态，再存Summary快照 | 本项目保持活动记忆/状态一致的记录约定；论文Summary伪代码未明确写出这项恢复，不能称原文规定 |
| 普通Thought | 保存真实熵，普通Thought不终止循环 | 沿用官方执行器；没有采用论文while伪代码中的低熵Thought钳制到sigma操作 |
| 过早结论 | 零基step<4时转Thought；若有Thought前缀，保留该前缀 | 修复早期适配丢弃前缀的问题，对齐固定执行器；达到topK后沿用上游Final Answer片段处理 |
| 接受结论 | 仅当零基step≥4且当前Final状态严格小于1.2时接受 | 最早第5次生成；topK=4不代表每次检索4篇；不是口头置信度判断 |
| 最大步数 | 第8步后没有合格结论则保留真实栈顶，记invalid / budget_exhausted | 不追加Direct或将Observation提升为最终答案 |
| 原生输出接口 | 英文动作说明及统一原生答案空间；熵接受后才调用共用 `final_json` 纯语法转换 | 任务接口适配；预算耗尽输出不经转换伪装成合格结论 |

状态数值不作为额外提示写给模型；模型下一轮看到的是当前活动记忆。回退和总结移除的文本可以在审计文件恢复，但不混回活动prompt。

### 3.3 熵口径和后端调整

选择官方默认cuct路径。对生成处理器和采样变换之后、抽样之前的**完整词表scores**转FP32：

```text
p_t = softmax(scores_t.float())
h_t = -sum_v p_t(v) * ln(p_t(v) + 1e-10)
state = sum_{t in selected_positions} h_t
```

这是自然对数的逐token分布熵之和。排除已生成特殊token的位置，不把特殊token从词表分布删除后重归一化。保存生成token、逐token熵、选定位置、起点、匹配状态和聚合结果，不导出巨大的完整词表张量。

位置选择保留固定上游的实际规则：先过滤特殊ID，扫描 `range(len(tokens)-3)`；首次精确 `Thought` 后偏移2，或首次 `Final` 后下一token精确为 `Answer` 时偏移3；匹配失败从0开始。没有strip token前导空格，` Answer`可能不匹配。这是上游字符串/边界口径，不能写成“精确提取最终答案语义正文”。

原依赖torch 2.4.0 / Transformers 4.44.0升级为既有环境的2.6.0 / 4.51.3，以支持Qwen3；核对了原生成器保存的是处理器及warper之后的scores。生成时收集器不改变scores，移除了cuct控制流不使用的attention、其他指标及完整logits导出。主路径没有额外评分前向，没有top-k截断熵、单token NLL、口头自信度或更小评分模型。

同后端 `generate(output_scores=True)` 参考对照覆盖实际Llama和Qwen：token序列一致、熵最大绝对误差0、阈值判断一致。证据见 [Llama参考](<runs/imedrag_dev_v4/backend_reference.json>)、[Qwen参考](<runs/tcrag_dev/backend_reference.json>)。每次后端对照额外计2个真实请求；这是所测同引擎序列的结果，不是跨硬件逐bit等价声明。

## 4. 实际试跑、修复和复验顺序

以下目录及失败制品均保留。目录后缀是操作顺序标记，不能代替其resolved配置和源码快照。v1/v2/v3的配置仍写 `iterative-v1`；v4及之后写 `iterative-v4`。

| 顺序 / run目录（均在 `runs/`） | 当时完成情况 | 对应处理 | 新增有输出LLM请求，不含参考对照 |
|---|---|---|---:|
| `imedrag_dev_v1` | 未完成，保存1条终态 | 收紧查询完整边界；从逐输入串行改为输入并发及后端合批 | 29 |
| `imedrag_dev_v2` | 未完成，无完整输入终态；另有startup OOM日志 | 支持实际Markdown语法；将请求随机种子/缓存身份与运行目录分离 | 20 |
| `imedrag_dev_v3` | 未完成，保存1条failed终态及OOM尝试 | 真实共享显存不足，调整层分配、合批上限和分配器 | 59 |
| `imedrag_dev_v4` | 首次24条完整终态：7 ok / 17 invalid / 0 failed | 使用显存修复、单QA收据和有序回填；成为完整真实生成时间来源 | 509 |
| `imedrag_dev` | 24条：11 ok / 13 invalid | 扩展实际查询语法包装；试改flat JSON最终提示；只重算受影响依赖及格式化 | 60 |
| `imedrag_dev_final` | 24条：2 ok / 22 invalid | 恢复官方最终格式化提示；所有24条重新执行格式化 | 24 |
| `imedrag_dev_accepted` | 24条：19 ok / 5 invalid | 用同一规则重放全部真实收据；只加完整字典字面量→JSON语法转换 | 0 |
| `tcrag_dev` | 24条：9 ok / 15 invalid | 最终源码下的一次完整真实开发运行；sigma固定1.2 | 144 |

`accepted`是目录名，不表示所有验收项通过。上表是不同工程版本的开发记录，不能当作受控算法消融或独立测试集成绩。

### 4.1 并发、随机数和显存修复的具体变化

v1→v2新增4输入工作线程和 `BatchingBackend`，初始上限60000 padded tokens。各阶段随机数流独立，避免不同输入因合批共用一个抽样流。v2→v3使请求身份和种子不再受 `run_id`、`code_hashes`、`inputs_hash`、`input_path`、`physical_gpu_selection` 等运行位置元数据影响；模型、tokenizer、完整prompt、证据、角色、生成参数和方法语义配置仍参与身份。run级完整配置和源码仍锁定，改变后拒绝续写同一run。

v3→v4把合批上限60000改为32000，启用可扩展显存分配器，Llama由16/16层调整为12/20，Qwen采用14/22层；每条QA独立收据并按序写回，拆分大批次时继续使用各序列自己的随机数流。单个合法长输入不会按合批上限截短。后续又在加载模型前增加worker数漂移拒绝检查。

这些修改解决实际OOM、调度及恢复问题，未减少4轮追问、8步上限、检索条数、输入范围或阶段输出预算。小模型固定响应/采样测试检查单独与合批token序列一致；BF16在不同硬件和张量形状下仍可能产生数值差异。

### 4.2 i-MedRAG缓存复验链

1. `imedrag_dev_v4` → `imedrag_dev`：复制716份未受影响的请求收据，排除所有最终格式化；查询语法修复涉及 `dev_medqa_009` 第3轮、`dev_medeinst_003` 第1轮、`dev_medeinst_006` 第3轮、`dev_medeinst_009` 第1轮（均为零基编号），重算受影响QA及依赖历史之后的阶段。新增60个LLM请求、24次检索。
2. `imedrag_dev` → `imedrag_dev_final`：复制776份收据；只新增24次最终格式化调用，恢复官方提示及原生答案类型说明。
3. `imedrag_dev_final` → `imedrag_dev_accepted`：复制全部800份真实收据，即521个模型请求及279个检索请求；统一重放24条，19条产生 `answer_syntax_repair` 事件，新增模型/检索调用均为0。

每层 [cache_provenance.json](<runs/imedrag_dev_accepted/cache_provenance.json>) 指向来源和复用规则；辅助脚本为 [replay_format_prefix.py](<reports/replay_format_prefix.py>)。早先734份收据的准备方案在追加两项实际语法问题后作废，当时尚未开始该复验的推理，保留于 [prefix_preparation_before_syntax_followup.json](<reports/prefix_preparation_before_syntax_followup.json>)。最终按716份方案执行。没有按答案正确与否挑选输入或复用结果。

### 4.3 曾准备但未执行的工作

早期准备过15条正式输入盲检查清单和一个有限TC阈值计划（1.2、5、10、20）。用户要求专注两方法复现后，撤下额外队列并保留历史文件；未启动盲测、校准或整套正式推理。依据为 [scope_correction.json](<reports/scope_correction.json>)、[unused_tcrag_calibration_plan.json](<reports/unused_tcrag_calibration_plan.json>)、[acceptance_execution_complete.json](<reports/acceptance_execution_complete.json>)。`data/blind*.jsonl`及暴露说明是未执行准备记录，不是新增实验结果。

## 5. 数据、输入权限和评分如何接入

### 5.1 继承既有正式范围

| 数量类型 | 冻结数量 | 含义 |
|---|---:|---|
| 比较单元unit | 6104 | 既有v5去重入选单元 |
| 入选具体判断target | 13000 | 已确认evaluation_labels下的判断 |
| 唯一推理输入input | 13905 / 方法 | 共享完整输入可复用推理后的实际计划分母 |
| 原生评分记录 | 15616 / 方法 | 原题/变体和原生任务展开后的评分映射 |
| target→input映射行 | 34753 | 展开关系数量，不是新增判断或模型调用 |

沿用既有候选母库、抽样概率、入选原因和种子，不重选v4/v5或R5。类别用 `evaluation_labels`；不把原始 `labels` 中未入选R5的语义标签计回R5。原记录和完整物化输入均保留内容哈希，见 input_manifest.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_manifest.jsonl`）、source_target_input_mapping.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/source_target_input_mapping.jsonl`）、[input_lock.json](<data/input_lock.json>)。

### 5.2 固定开发包

开发包24条：BigBio MedQA validation前12条，加本地MedEinst train中排除全部正式病例组/完整输入后的前12条。MedQA源固定revision为 `484a6c066fe8e75c83edea0c88b5169316714fcd`；只把原选项key/value列表转换为保持顺序的字典。MedEinst候选第3行 `case_100034` 因重叠排除，没有删除正式输入。

来源及逐条映射见 [dev_source_acquisition.json](<data/dev_source_acquisition.json>)、dev_provenance.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl`）、[dev_overlap_audit.json](<data/dev_overlap_audit.json>)。24条与13905条正式输入的规范化题干精确重叠为0，见 [dev_question_overlap.json](<reports/dev_question_overlap.json>)；未声称排除全部语义近重复。真实开发覆盖选择题和开放诊断，其余格式及证据干预使用隔离回放测试。

### 5.3 可见信息和证据干预

推理白名单为 `question/options/fixed_evidence/answer_format`；ID只做记录。gold、evaluation_labels、分类解释、配对另一侧答案及评分映射不进入模型或检索查询。原题和变体独立推理，既有选项顺序保留。

协议固定为 `v5_full_medcorp_plus_required_evidence_20260911`。原题自带证据保留，TC不能回退原题；仅追加检索片段按排名裁剪到30000 tokens，原题、必需证据及i-MedRAG历史不裁剪，完整prompt超窗明确失败。M22继承v5六档固定受扰动材料及额外MedCorp检索，M20也保留规定证据及既定额外检索权限。M22应称“固定受扰动证据＋外部动态检索”项目协议，不能与MedRGB原生静态证据结果混称。

### 5.4 评分和分母

复用既有v5评分：选择题精确key，多选集合exact/F1，关系标签归一化exact，诊断使用既定canonical映射；M22主问和错误文档检测分别报告，R4为作者预期答案一致率。诊断canonical规则不是原来源的LLM语义评分，未用当前gold补充同义词。快照见 [scoring_snapshot/sources.json](<reports/scoring_snapshot/sources.json>)。

计划输入满足 `N_planned = N_ok + N_invalid + N_failed + N_pending`。无效/失败保留完整分母，运行有效率、评分映射有效率和准确率分别计算。沿用v5既定单元内/单元间聚合，类别可重叠；原题、变体、应保持/应改变及配对共同正确率分别报告。置信区间按病例组重采样，跨来源可精确识别的共享原题连接为依赖组。详细来源契约见 [evidence_protocol.md](<evidence_protocol.md>)。

## 6. 验证证据和最终真实开发结果

### 6.1 自动测试与轨迹审计

tests_final_syntax.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/tests_final_syntax.log`）记录19项自动测试通过：i-MedRAG跨轮QA历史、查询语法和并发顺序；TC工具/回退/总结/过早结论/合格结论/耗尽；FP32熵公式与特殊token位置；样本隔离、gold哨兵、证据差异和缓存；请求与终态恢复、配置漂移拒绝；原生格式、失败分母和复用成本。固定响应均隔离在tests，未进入真实benchmark。

真实审计核对i-MedRAG的521次模型身份、96轮前后历史、279次QA及24次最终历史；TC核对144次prompt/活动栈、97次熵重算、44次接受边界、3次Summary移除/状态恢复及3次耗尽。结果见 [i-MedRAG执行审计](<runs/imedrag_dev_accepted/execution_report.json>)、[TC-RAG执行审计](<runs/tcrag_dev/execution_report.json>)。

### 6.2 最终终态及方法运行量

| 指标 | M6 i-MedRAG | M7 TC-RAG |
|---|---:|---:|
| 计划 / 终态 | 24 / 24 | 24 / 24 |
| ok / invalid / failed / pending | 19 / 5 / 0 / 0 | 9 / 15 / 0 / 0 |
| 运行有效率 | 79.17% | 37.50% |
| 未知ID / 正式重复 | 0 / 0 | 0 / 0 |
| 实际轮次 / 动作数 | 每题4轮，共96轮 | 平均6步，范围3–8，中位6 |
| 逻辑LLM请求 | 521 | 144 |
| 输入 / 生成tokens | 1093381 / 169363 | 354715 / 18918 |
| 检索请求 | 279 | 40（34后端、6同查询缓存） |
| 自然Summary / Backtrack | 不适用 | 3 / 0 |
| 输出截断 / 传输重试 / 无命中 | 均0 | 均0 |
| 预算耗尽 | 0 | 3，12.5% |

i-MedRAG实际279条查询均逐条检索和作答，单题6–15条，不保证每轮恰好3条。5条invalid中，3条涉及追问提取问题、3条涉及最终格式问题，交集1条。TC的15条invalid包括12条动作解析失败（9条缺动作标签、3条空Thought）和3条预算耗尽。真实模型未自然触发Backtrack，其行为由固定响应测试核对，未为增加动作率强迫回退。

TC的44次Final Answer提议中，17次因步数过早拒绝、18次因熵拒绝、9次接受。97次状态值中位数22.38、p95=60.04、范围0.0121–109.88。阈值始终为1.2，没有根据这些开发结果重新选阈值。

### 6.3 按来源的完整分母评分

| 来源 / split | 方法 | 运行有效 / 计划 | 当前既定评分器正确 / 计划 |
|---|---|---:|---:|
| MedQA validation | i-MedRAG | 11 / 12 | 11 / 12 |
| MedEinst train | i-MedRAG | 8 / 12 | 0 / 12 |
| MedQA validation | TC-RAG | 3 / 12 | 2 / 12 |
| MedEinst train | TC-RAG | 6 / 12 | 0 / 12 |

i-MedRAG的8条运行有效诊断中，6条嵌套结构字符串被旧解析器拒绝、1条未映射、1条歧义；TC的6条运行有效诊断均未进入既定canonical映射。这里的0/12不等于医学语义准确率为0。两个阶段的有效性及错误保留在 [i-MedRAG评分](<runs/imedrag_dev_accepted/scores/summary.json>)、[TC-RAG评分](<runs/tcrag_dev/scores/summary.json>)，未基于gold改词或修改映射。

## 7. 已发生的计算成本及正式成本估算

### 7.1 开发累计新增计算

[formal_cost_estimate.json](<reports/formal_cost_estimate.json>)分别保存失败pilot、缓存来源运行、最终新增计算及参考对照。成本脚本曾只匹配 `superseded.json` 而漏掉v1/v2的 `superseded_development_pilot.json`；已改为识别 `superseded*.json` 并重算。这是成本清单修复，不影响预测或评分。

按这些互不重复的新增计算组汇总：**845个有输出的实际LLM请求＋10个后端参考请求＝855个请求**；输入tokens为1929371＋394＝1929765，生成tokens为231389＋206＝231595。406份新增检索收据含同查询缓存，不能写成406次访问检索后端。中断后没有输出的生成，其未知token不作猜测；这些数字是已保存收据能证明的累计量，不是包括所有启动失败开销的精确资源账单。

最终两方法24条制品的逻辑请求数为521＋144＝665，不等于开发累计855个真实请求。i-MedRAG最终目录复用800份收据后耗时1.60秒，不能当作模型推理速度。

| 实测时间 / 调度指标 | i-MedRAG完整真实来源运行 `imedrag_dev_v4` | TC-RAG `tcrag_dev` |
|---|---:|---:|
| 24条wall time | 11914秒，3.31小时 | 2792秒，46.53分钟 |
| 共享GPU输入吞吐 | 7.25输入/小时 | 30.95输入/小时 |
| 单题延迟p50 / p95 | 1875 / 2401秒 | 476 / 787秒 |
| 合批行数中位 / 最大 | 4 / 10 | 3 / 4 |

i-MedRAG后续接口复验另用约1057秒和241秒，产生60＋24次新模型调用；纯语法重放不增加生成。最终i制品中的物理batch ID来自不同来源阶段，不宜当作一次冷运行的批处理测量。TC的144个逻辑请求对应49个物理生成批次。吞吐均包含无效及提前解析失败的输入，不表示相同有效输出质量下的效率。

### 7.2 正式规模及尚不能估出的部分

每方法正式计划13905个唯一输入。i-MedRAG标准恰好12条QA且无重试的情景为305910个LLM请求、166860次检索；TC最多111240个动作请求，所有输入最早第5步接受的情景为69525个。重试另计，不能把13000个判断直接当调用数。

| 方法 | ≤1024必需输入tokens层：正式 / 已测开发 | 该层条件投影 | 1024–8192层未测数量 | >8192层未测数量 |
|---|---:|---:|---:|---:|
| i-MedRAG | 10508 / 24 | 约1398小时 | 3040 | 357 |
| TC-RAG | 10466 / 24 | 约338小时 | 3072 | 367 |

输入长度用各自tokenizer计算，故分层数量不同。投影使用最终逻辑请求成本和原始完整运行的wall/engine比例，不再次除以并发数；仅代表当时共享GPU及短开发输入的执行尝试。未测长度层缺少真实吞吐，因此两个方法完整正式时长仍为 `null`。不把已覆盖层当整套预算，不据此宣称TC-RAG更快。

## 8. 可用于论文的表述及局限性

### 8.1 Methods草稿

> 我们在既有医疗问答评测框架中适配i-MedRAG（M6）与TC-RAG（M7）。i-MedRAG使用Llama-3.1-8B-Instruct，执行4轮追问，每轮请求3个查询；每个有效查询独立检索并生成答案，随后按原查询顺序写入历史，最终由原问题及QA历史生成答案。TC-RAG使用关闭thinking的Qwen3-8B，通过活动记忆栈、工具检索、回退和总结替换维护推理上下文，并以完整生成分布的逐token熵之和监控状态；沿用官方执行器的8步上限、topK=4及sigma=1.2。两个方法复用完整MedCorp及BM25每库32条候选、MedCPT重排top8的检索配置。所有角色在各自方法内使用同一backbone，输入权限、原生答案空间与评分规则沿用冻结v5协议。

### 8.2 实现验证草稿

> 我们通过固定响应测试核对跨轮QA依赖、活动记忆回退与总结、熵计算、终止边界、输入隔离及断点恢复，并在24条固定训练/开发输入上分别执行真实模型验证。19项自动测试通过，两个模型的生成时熵与同后端output_scores参考一致。i-MedRAG与TC-RAG分别获得19/24和9/24运行有效输出；其余输入及失败原因保留在完整计划分母中。开发结果用于报告实现行为、接口兼容性和实际成本，正式v5全量比较尚未执行。

### 8.3 当前证据的局限

1. **适配实现的边界**：名称应为“统一实验框架下的适配实现”。i-MedRAG固定4轮后终止、TC工具集合迁移及Summary补齐均已披露；不能声称直接复现两篇原论文的表格分数或原样运行完整上游系统。
2. **对照配置差异**：i-MedRAG与TC-RAG使用不同backbone，不能把两者差异全部归因于算法；与既有M4/M5比较也须披露Transformers/vLLM及阶段预算差异。旧M0/M2的64-token预测不是完全受控的共同预算对照。
3. **开发与测试区别**：24条开发输入在工程修复中反复使用，不是独立测试集；各版解析/提示/随机数/调度变更交织，不能把版本得分差写成受控消融。
4. **兼容问题仍在**：i-MedRAG有5条invalid，TC有15条invalid，开放诊断还存在解析及canonical映射问题；不能把终态齐全称为全部验收通过，也不能把canonical未命中直接解释为语义答错。
5. **覆盖和协议**：真实开发只覆盖两类来源和短输入；其余格式、长输入及证据干预尚无完整真实覆盖。M22使用项目的固定受扰动证据＋额外检索协议，不等价于原生静态证据任务。v5是已确认预算抽样范围，不是全部来源原始全量。
6. **数值及成本外推**：熵对照只证明已测同后端序列一致；不同硬件、引擎及BF16批次形状可能改变分布。实测共享GPU吞吐包含invalid，未测长度层不能可靠外推，因此尚无完整正式预算。

## 9. 制品导航及记录维护

| 论文写作所需信息 | 制品 |
|---|---|
| 固定出处、组件对应、非等价修改 | [method_fidelity.md](<method_fidelity.md>) |
| 最终状态、错误及实测结果 | [acceptance_report.md](<acceptance_report.md>) |
| 原生输入/证据/评分权限 | [evidence_protocol.md](<evidence_protocol.md>) |
| 最终配置、模型和环境 | [configs/](<configs>)、各run的 `resolved_config.json` 与 `code_snapshot/` |
| 正式映射、开发来源及隔离审计 | [data/input_lock.json](<data/input_lock.json>)、data/dev_provenance.jsonl（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl`）、[reports/dev_question_overlap.json](<reports/dev_question_overlap.json>) |
| 逐题最终预测 | i-MedRAG predictions（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/imedrag_dev_accepted/predictions.jsonl`）、TC-RAG predictions（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/runs/tcrag_dev/predictions.jsonl`） |
| 完整prompt/输出/检索/活动栈 | `runs/<run>/items/<input>/{requests,attempts,events}`；输入、配置和文档身份随记录保存 |
| 历史修复和新增成本 | [runs/](<runs>)、各run的缓存来源和源码快照、[formal_cost_estimate.json](<reports/formal_cost_estimate.json>) |
| 已验证命令 | [README.md](<README.md>)、acceptance_final_commands.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/acceptance_final_commands.log`） |
| 总工作区功能入口 | [MEDRGAG_WORKSPACE_GUIDE.md](<../workspace_reference/MEDRGAG_WORKSPACE_GUIDE.md>)，由 /home/data3/txy/AGENTS.md（本地制品：`/home/data3/txy/AGENTS.md`） 链接 |

README中的准备、检查、19项测试、开发运行、终态恢复和离线评分命令已有本机执行证据；正式全量命令已接入入口，尚未执行全量GPU验证。模型权重、受限制原始材料、凭据及巨型轨迹不随代码发布，服务器保留可恢复路径和身份记录。

2026-09-13本次更新为文档整理：新增本文并更新README及AGENTS.md链接的工作区功能记录。数值来自已有制品和源码快照；没有在本次文档更新中运行模型、改变方法配置、修改评分或新增实验。

2026-09-13后续命名调整：按用户指令将i-MedRAG命名为M6、TC-RAG命名为M7，同步README、方法忠实性、验收、输入协议及工作区功能记录。该调整仅确定论文/比较编号；原执行标识、配置、源码、预测、缓存与运行目录保持原有身份。

## 2026-09-13 v5 M6/M7 正式输入诊断试跑启动

用户新授权先运行部分v5输入，检查原始M6/M7的兼容性与效率，可用GPU1/2/3。运行包：[results_v5_m6_m7](<../completion/results_v5_m6_m7/README.md>)。每方法12条：11来源各取可见字符长度中位输入，另加M20全库最长输入；选择未读取gold或模型预测。M6在GPU1/2各运行6条，M7在GPU3运行12条。只将两卡分层部署改为单卡完整模型副本，其余方法、阈值、阶段预算和原生评分沿用runtime_v4；没有增加CF/WM/adapter模块。源码复制至新包，旧结果和旧源码不变。单卡三个进程均通过真实模型熵参考核对（最大误差0），已进入正式输入推理。全量27,810方法输入评测尚未启动；试跑并不代表完整正式结果。实时状态及后续结果以新包制品为准。

### 本次试跑发现的上游行为遗漏（2026-09-13）

M7原12条试跑为1有效/11无效/0失败，404.71秒；9条无动作标签输出在本地直接失败。锁定上游 `model/TCRAG.py::process_no_regular_output` 实际会将无关键词输出加上Final Answer标签，再经过原步数/熵判断。独立 `results_v5_m6_m7/tc_upstream_fix` 补回此处理，保持原始生成token熵、sigma1.2和topK4，保留适配的Plan/Summary及DOC_RAG查询参数，不照搬会破坏参数的query全局替换。14项方法测试通过；复用77份旧请求收据，新增10次LLM请求后，同12条为9有效/3无效/0失败。新增运行50.19秒不可称冷吞吐。70次模型身份/活动栈、57次熵重算、33次接受边界检查通过，原生诊断评分19条映射已完成。

M6锁定上游 `src/medrag.py::i_medrag_answer` 直接使用抽取列表，查询解析异常时跳过该轮；旧适配的逐字匹配门槛及任一解析问题使整题invalid并非上游行为。独立 `results_v5_m6_m7/m6_upstream_fix` 恢复这两项行为，保留JSON类型检查和运行失败记录，14项方法测试通过。当前原始M6试跑继续运行，修复分片已排队接续。只复用首个查询列表改变之前的请求，之后QA和依赖重算；全量尚未启动。完成状态以新包 `RESULTS.md`、`fixed_pilot_summary.json` 和各run制品为准。

### v5 M6/M7 全量已启动（2026-09-13 05:46 Asia/Shanghai）

用户明确授权使用三张卡运行全量。运行包：[/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal/README.md](<../completion/results_v5_m6_m7/formal/README.md>)。每方法13,905独立输入，其中12条修复试跑结果原样复用、13,893条新运行，覆盖6,104单元和13,000入选判断。每方法109个128输入分片（末片不足128）；GPU1/2优先M6，GPU3优先M7，优先方法队列领完后自动领取另一方法。GPU0不动。使用已验证的M6/M7上游兼容性修复，无CF/WM/adapter附加模块，权重、提示、轮数、阈值、检索与阶段预算保持试跑配置。合并方法15项测试及1项调度测试通过。

三个模型已进入真实推理，M7产生首条新有效终态，初始GPU1/2/3利用率约97–98%。tmux socket `v5-m6-m7-full`，会话gpu1/gpu2/gpu3/monitor。在formal目录执行 `python3 status.py`；`logs/supervision.jsonl`每五分钟记录GPU及进度。各分片完成后审计，最后一片触发完整汇总和原生评分，完成标记为formal/complete.json，最终报告为formal/RESULTS.md。健康进程勿重复启动或中断。

耗时估计纠正：先前4–7天偏乐观；按已完成两个M6分片和M7试跑吞吐分配三卡，直接投影约11天。该试跑非代表性且含最长输入，不是完工承诺，后续以全量滚动吞吐更新。

### v5 M6/M7 提高并发后接续（2026-09-13 06:37）

用户要求提高正式测试的显存利用与吞吐。活动运行改为 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_fast/README.md](<../completion/results_v5_m6_m7/formal_fast/README.md>)，tmux socket `v5-m6-m7-fast`，GPU1/2=M6每卡32线程/128000合批token，GPU3=M7每卡16线程/96000合批token。原 `formal/`三队列已停止，记录和缓存保留，勿重启。方法、权重、提示、预算、阈值及评分不变，执行参数单独覆盖以保留原请求缓存键/随机种子。

相同32条正式请求微基准：M6批量4→32 token吞吐83.47→96.69/s；M7批量4→16为37.81→44.65/s，增到32下降至40.18/s，因此选择不同并发。微基准使用128生成token，不直接当作完整方法加速比。方法与队列16项测试通过。接续已复用旧正式请求并无模型重放完整终态，一致性检查通过。SIGTERM后0.33秒内产生的4个M6人工关闭异常已保存原制品、明确记录并重排同输入，未按答案正确性筛选。新进度06:37 M6=44/13905，M7=70/13905，均无真实运行失败，显存约38.55/43.23/36.64 GiB。

在formal_fast执行 `python3 status.py`。监控与自动审计/全量评分继续，新结果最终写入formal_fast/RESULTS.md。每五分钟向用户报告两方法累计、新计算、剩余及GPU0–3显存/利用率。

### v5 M6/M7 活动目录再次更新：按阶段/长度合批（2026-09-13 06:57）

当前活动目录 [/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/README.md](<../completion/results_v5_m6_m7/formal_balanced/README.md>)，tmux socket `v5-m6-m7-balanced`。单纯提高批量在正式混合长度请求上造成大量补齐与长尾等待，实际M6约37–44、M7约10 token/s，不能称全量提速。相同28请求分组微基准40.31→33.16秒、88.91→108.08 token/s；有效输入补齐量减少31%。因此按原生答案类型、生成阶段、token长度2倍区间合批，并把等待池提高至M6每卡64、M7每卡32，token上限保持128000/96000。模型、方法预算和阈值不变；batch_group不进入prompt、缓存键或随机种子。17项测试通过。

接续无模型/检索重放原M6 32条、M7 68条正式终态，输出和状态一致；加上各12条试跑后进度M6=44、M7=80。原成功阶段收据全部保留复用，未完成响应重算。本次先冻结调度器再终止模型，没有产生新的关闭异常。formal与formal_fast为历史目录，勿重启；源结果、先前4条人工关闭异常和递归成本链完整保留。五分钟报告、自动审计和全量评分继续在formal_balanced执行。

### v5 M6 暂停、三卡运行 M7（2026-09-13 08:03）

用户明确要求暂停 M6，继续 M7。当前活动包 `/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced` 未迁移。M6全部109分片标记paused，累计52/13905（40新＋12复用），41有效/11无效/0失败；预测与阶段缓存保留，操作记录m6_pause.json，不自动恢复。GPU1/2原M6已释放并领取M7分片002/003；GPU3原M7分片001未中断。M7三卡均32并发、96000合批token，其余方法/生成/检索设置不变。GPU0未动。tmux仍v5-m6-m7-balanced。

调整独立完成汇总：M7所有分片完成并审计后，自动写results/tcrag/complete.json、原生评分和RESULTS.md，不等待M6；根complete.json仍只用于两方法均完成。暂停队列不被领取和独立评分幂等性等3项针对性测试通过。五分钟进度与GPU0–3报告继续。

### M7 正式吞吐诊断与后续等待池调整（2026-09-13 08:46）

用户询问更大批次/显存是否有帮助及每五分钟新增偏少的原因。读取formal_balanced三张卡最近20分钟的真实请求：平均实际batch2.68/3.13/2.95，完整题平均约6次LLM调用，decode有效位置约42.6%–59.1%，排队中位数122–216秒，检索中位数0.59–1.30秒。长输出拖住整批：6条输出223/7/2048/107/10/169 tokens用了273.6秒。几乎没有批次碰到96000 token上限，因此仅增显存上限不是当前主要改进。

将execution.json中M7 workers32→64，保留96000合批token、原阶段/答案格式/长度分组、完整2048生成预算、模型和熵语义。只在下一分片启动时生效，当前分片不中断。实际配置由各run/batching.json记录。此时M7=362/13905，0运行失败；M6继续暂停52条。证据formal_balanced/logs/m7_throughput_diagnosis.json，变更记录m7_workers64_change.json。64等待池不是实际batch64，完整正式吞吐改善尚未验证。

### M7 首个64路正式分片完成，后续恢复32路（2026-09-13 10:34）

formal_balanced的tcrag_004完成128输入并审计通过，64路等待池耗时97.87分钟，15.01有效token/s，decode有效位置36.5%；前三个完整32路分片001/002/003分别79.33/90.97/68.39分钟，18.37–21.08 token/s，45.2%–52.0%有效位置。分片是不同随机输入，输入token量也不同，因此不是成对因果测试；但尚无完整方法提速证据，扩大等待池未消除长输出拖住整批。

据此将后续execution.json的M7 workers恢复32，96000 token上限及全部方法参数不变。当前005/006/007保留64运行至完成，避免丢失未返回生成。M6保持暂停。制品：formal_balanced/logs/m7_completed_chunk_throughput.json、m7_workers32_restore.json。10:33累计M7 780/13905，0运行失败。

### 64路观察完成，三卡恢复32路（2026-09-13 11:58）

四个64路正式分片004–007均已完成并审计，耗时97.87/102.92/127.36/88.72分钟，中位100.40分钟，合并73.69输入/GPU小时；此前三个32路完整分片001–003耗时79.33/90.97/68.39分钟，中位79.33分钟，合并96.53输入/GPU小时。64路的有效生成吞吐14.90–17.04 token/s，32路18.37–21.08 token/s。输入是不同随机分片，保留非成对观察限制，不宣称严格因果比；四片均未支持增加并发的实际收益。已完成全部64路分片，GPU1/2/3当前分片009/008/010均按32路、96000合批token继续，未中断任何分片。M7累计1148/13905、0运行失败；M6仍暂停52条。

完整制品更新于formal_balanced/logs/m7_completed_chunk_throughput.json，包含逐片请求数、生成/输入tokens、实际批量、有效decode比例及耗时，供后续论文与效率分析引用。
