# 原生评测协议与结果解释

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。当前v5每方法有13,905个唯一模型输入、15,616条原生评分映射，对应6,104唯一单元和13,000选中判断。ALL按唯一单元等权，不是五类百分比均值。失败/无效保留分母；格式、原生有效率与准确率分别报告。

工作区总入口（本地来源：`/home/data3/txy/docs/README.md`） · 记录归属与迁移证据（本地来源：`/home/data3/txy/docs/workspace.md#documentation-migration-20260914`）

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [2. 数据、复用与评分口径](#record-0088)
- [2.1 冻结范围](#record-0089)
- [2.2 精确复用](#record-0090)
- [2.3 评分与失败处理](#record-0091)
- [5. 数据、输入权限和评分如何接入](#record-0187)
- [5.1 继承既有正式范围](#record-0188)
- [5.2 固定开发包](#record-0189)
- [5.3 可见信息和证据干预](#record-0190)
- [5.4 评分和分母](#record-0191)
- [5. 次要开销与应避免的误判](#record-0219)
- [evidence_protocol.md](#record-0386)

<a id="record-0088"></a>

## 2. 数据、复用与评分口径

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`），原文第46行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 2. 数据、复用与评分口径

<a id="record-0089"></a>

## 2.1 冻结范围

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`），原文第48行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 2.1 冻结范围

使用 `benchmark_r1_r5_v5_20260910` 的 `evaluation_labels` 确定评测成员；保留 v3/v4/v5 原件。范围为 6,104 个唯一比较单元、13,000 个选中判断、13,905 个去重模型输入（包括参考端）和每方法 15,616 条原生评分映射。

R1–R5 类别可重叠：R1=2,866、R2=79、R3=733、R4=13、R5=3,600。类别数量不能直接相加作为总样本量。参考题用于原有配对评测，不是训练集或调参验证集。

模型输入仅含题目、原生选项、完整给定证据、输出格式及预算等可见字段。金标、分类理由、目标判断和评分映射不进入生成。M14 恢复原生选项；M17 按独立合格的 VISIT/MANAGE/RESOURCE 子项加载，不把父单元资格自动传给子项。详见材料化验证（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5/preparation_validation.json`）。

MedRGB 沿用本地六档污染比例 `p_sig=100/80/60/40/20/0`；100 是参考端。各比例独立抽取材料，不能按数组位置假定污染文档与原件一一配对。28 个单元的 77 个上下文包含原有空文档槽位：保留输入，缺失文档不纳入检测评分；纠正文本保留但未进行额外语义判分。

<a id="record-0090"></a>

## 2.2 精确复用

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`），原文第58行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 2.2 精确复用

比较实际可见输入字段，包括问题、**选项顺序**、固定证据、原生格式和输出预算，并保存来源路径、原 item_id 等溯源信息。不是仅按题号或问题字符串复用。

M3 原 v3 结果共有 4,872 个输入，只有 3,690 个与 v5 精确匹配；其余输入进入 10,215 条续测清单。复用审计（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m3/reuse_audit.json`）验证可见输入、solver/query 模板和方法配置一致。已完成但答案无效或投票平局的旧记录也保留，不挑选性重跑。

最终预测同时包含历史复用和本次生成。因此，完整结果不能描述为“五方法各自从零重跑一次”；单独统计本次推理成本时也不能把复用记录当成本次调用。

<a id="record-0091"></a>

## 2.3 评分与失败处理

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`），原文第66行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

##### 2.3 评分与失败处理

主表先计算一个比较单元在该类别下的非参考原生任务平均正确性，再对单元等权平均。ALL 在 6,104 个唯一单元上计算，不是 R1–R5 五个百分比的简单平均。另存来源等权均值、全部任务通过率、逐来源/任务、R5 一致性与两端同时正确等指标。

诊断使用已有归一化精确匹配，不添加医学同义词裁判。R4 是 13 个作者预期答案的一致率。原生任务准确率不等同于对每条分类理由做医学语义验证。无效输出、平局和协议失败保留并按原有规则计错，不用金标修复。

M3 新生成结果最终状态：9,926 `complete`、186 `invalid_answer`、88 `vote_tie`、15 `runtime_invalid`。后三类是已产生结果的模型输出结局，不是缺失题目。`runtime_invalid` 包括 query 达到固定输出预算仍没有 `</think>`；不通过不断重试寻找有效答案。传输/执行错误与这些原生输出结局分开处理，技术恢复复用已保存阶段。

<a id="record-0187"></a>

## 5. 数据、输入权限和评分如何接入

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第165行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

#### 5. 数据、输入权限和评分如何接入

<a id="record-0188"></a>

## 5.1 继承既有正式范围

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第167行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 5.1 继承既有正式范围

| 数量类型 | 冻结数量 | 含义 |
|---|---:|---|
| 比较单元unit | 6104 | 既有v5去重入选单元 |
| 入选具体判断target | 13000 | 已确认evaluation_labels下的判断 |
| 唯一推理输入input | 13905 / 方法 | 共享完整输入可复用推理后的实际计划分母 |
| 原生评分记录 | 15616 / 方法 | 原题/变体和原生任务展开后的评分映射 |
| target→input映射行 | 34753 | 展开关系数量，不是新增判断或模型调用 |

沿用既有候选母库、抽样概率、入选原因和种子，不重选v4/v5或R5。类别用 `evaluation_labels`；不把原始 `labels` 中未入选R5的语义标签计回R5。原记录和完整物化输入均保留内容哈希，见 input_manifest.jsonl（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_manifest.jsonl`）、source_target_input_mapping.jsonl（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/source_target_input_mapping.jsonl`）、input_lock.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/input_lock.json`）。

<a id="record-0189"></a>

## 5.2 固定开发包

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第179行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 5.2 固定开发包

开发包24条：BigBio MedQA validation前12条，加本地MedEinst train中排除全部正式病例组/完整输入后的前12条。MedQA源固定revision为 `484a6c066fe8e75c83edea0c88b5169316714fcd`；只把原选项key/value列表转换为保持顺序的字典。MedEinst候选第3行 `case_100034` 因重叠排除，没有删除正式输入。

来源及逐条映射见 dev_source_acquisition.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_source_acquisition.json`）、dev_provenance.jsonl（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_provenance.jsonl`）、dev_overlap_audit.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/data/dev_overlap_audit.json`）。24条与13905条正式输入的规范化题干精确重叠为0，见 dev_question_overlap.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/dev_question_overlap.json`）；未声称排除全部语义近重复。真实开发覆盖选择题和开放诊断，其余格式及证据干预使用隔离回放测试。

<a id="record-0190"></a>

## 5.3 可见信息和证据干预

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第185行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 5.3 可见信息和证据干预

推理白名单为 `question/options/fixed_evidence/answer_format`；ID只做记录。gold、evaluation_labels、分类解释、配对另一侧答案及评分映射不进入模型或检索查询。原题和变体独立推理，既有选项顺序保留。

协议固定为 `v5_full_medcorp_plus_required_evidence_20260911`。原题自带证据保留，TC不能回退原题；仅追加检索片段按排名裁剪到30000 tokens，原题、必需证据及i-MedRAG历史不裁剪，完整prompt超窗明确失败。M22继承v5六档固定受扰动材料及额外MedCorp检索，M20也保留规定证据及既定额外检索权限。M22应称“固定受扰动证据＋外部动态检索”项目协议，不能与MedRGB原生静态证据结果混称。

<a id="record-0191"></a>

## 5.4 评分和分母

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第191行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 5.4 评分和分母

复用既有v5评分：选择题精确key，多选集合exact/F1，关系标签归一化exact，诊断使用既定canonical映射；M22主问和错误文档检测分别报告，R4为作者预期答案一致率。诊断canonical规则不是原来源的LLM语义评分，未用当前gold补充同义词。快照见 scoring_snapshot/sources.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/reports/scoring_snapshot/sources.json`）。

计划输入满足 `N_planned = N_ok + N_invalid + N_failed + N_pending`。无效/失败保留完整分母，运行有效率、评分映射有效率和准确率分别计算。沿用v5既定单元内/单元间聚合，类别可重叠；原题、变体、应保持/应改变及配对共同正确率分别报告。置信区间按病例组重采样，跨来源可精确识别的共享原题连接为依赖组。详细来源契约见 [evidence_protocol.md](protocol.md#record-0386)。

<a id="record-0219"></a>

## 5. 次要开销与应避免的误判

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/PAPER_REPRODUCTION_RECORD.md`），原文第422行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

##### 5. 次要开销与应避免的误判

- M4每卡模型全程常驻；M6/M7每个128题分片由subprocess启动新的模型和检索器，结束后销毁。不过完整M7分片记录的generate调用区间已占墙钟约99%，因此启动、审计及批次间空闲不是当前小时级瓶颈。这里的generate区间也包含CPU同步，99%不能解释成GPU算力利用率99%。
- M7完整32路分片检索recorded seconds中位1.45–2.41秒，而单次LLM请求在引擎外等待的中位数121–150秒；主要排队在生成器。M6检索中位约10–11秒，也值得优化，但两片已保存的生成区间各约65分钟，不能只归因于检索慢。检索时间可能含锁等待/历史缓存元数据，不是独立检索kernel的纯耗时。
- M4启用了prefix cache；M6/M7的use_cache只用于一次generate内，没有跨请求KV复用。多轮共享前缀存在复用机会，但命中率需测量，不能假设整个历史每次可复用。[vLLM0.8.5官方文档](https://docs.vllm.ai/en/v0.8.5/features/automatic_prefix_caching.html)说明APC只省共享前缀的prefill，不直接加速decode。
- M4的87.2GiB包含预留KV缓存，HF显存按当前静态批次变化。显存使用率不是实际吞吐指标；硬凑满显存没有收益保证。

<a id="record-0386"></a>

## evidence_protocol.md

来源：Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/evidence_protocol.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc/evidence_protocol.md`），原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc`。

### 冻结输入与评分接口

本协议对应比较方法 **M6 = i-MedRAG（`imedrag`）**、**M7 = TC-RAG（`tcrag`）**，编号由用户2026-09-13指定。下文M01、M02等为数据来源编号。

冻结范围来自服务器 `results_v5_m0_m2_m4_m5` 的已完成版本：6104 单元、13000 判断、13905 独立输入、15616 原生评分记录。`data/input_lock.json` 锁定具体来源文件，`source_target_input_mapping.jsonl` 的34753行是 target→input 展开映射，不是新的判断或 LLM 请求。采样种子、候选母库、抽样概率和入选理由继续引用 v5 的 sampling_protocol / membership 文件，不重采样。

#### 可见信息

推理只读取 `question/options/fixed_evidence/answer_format` 白名单，`item_id` 仅用于记录，不进入 prompt。原生选项按已物化字典顺序保留。原题/变体独立初始化；gold、分类、成对答案、分类解释及任务评分映射仅离线可见。

| 来源 ID | 实际答案结构 | 必需信息及检索权限 |
|---|---|---|
| M01 | 开放诊断 | 原叙述，MedCorp 动态检索 |
| M02 | 原生多选集合 | 病例、问题、原生选项；MedCorp 动态检索 |
| M06 | 原生 yes/no | 原题；作者预期答案只用于离线一致率 |
| M10 / M11 / M12 / M14 | 原生选择题 | 物化题干与选项；原题和变体独立；MedCorp 动态检索 |
| M17 | 原生 yes/no 分目标 | 临床材料与该次 VISIT / MANAGE / RESOURCE 问题；MedCorp 动态检索 |
| M20 | 关系标签 | 完整给定证据随题保留，各轮原题上下文和最终回答均可见；追加 MedCorp 动态检索 |
| M22 | 主问选择 + 错误文档检测 | 原样保留 v5 六档比例全部 D 编号文档（含原始空槽）；追加 MedCorp 动态检索 |
| M23 | positive/negative | 原题和给定 instruction 原样保留；追加 MedCorp 动态检索 |

协议名称固定为 **v5_full_medcorp_plus_required_evidence_20260911**。它继承现有 v5 M4/M5 的额外检索权限；M22 是“六档固定证据 + 外部动态检索”的项目协议，**不能称 MedRGB 原生静态证据评测**。M20 同样需按此额外检索权限解释。原题和变体检索权限完全相同；已有扰动证据永久保留在原问题，不被干净检索覆盖、裁掉或提前修正。TC-RAG 可回退/总结动态检索记忆，不能移除原题。i-MedRAG 最终原题含其自带证据，额外信息仅来自成功追问 QA 历史。

目前不另起“原生证据内检索”主结果。若将来测试禁止外部检索的来源协议，应新配置并同时重跑对应比较方法。各来源结果带此协议名称；不能与不同访问权限的旧结果混合。

#### 预算、错误、评分与成本

只裁剪追加检索片段，依排名依次消耗30000模型token预算，记录逐文档的全文哈希、进入上下文的文本和裁剪数；原题、必需证据、i-MedRAG QA历史不裁剪。每阶段实际完整 prompt + generation 上限超窗时返回 `context_overflow` 失败。QA1024、query1024、parse1024、TC action2048、final2048、format2048；这是项目阶段预算，不是论文共同默认。根 seed42，内部请求 seed 为根seed加完整请求哈希前8位再模2^31；实际值逐请求记录。

最多2次传输重试（1/2秒退避）；每次i-MedRAG追问提取最多1次同模型纯JSON格式修复。最终输出最多1次确定性的字典字面量→JSON转换，保留值及原始响应，两个方法共用，不改评分器或增加模型调用。模型/OOM/算法失败不当传输重试。解析失败、无命中、检索失败、截断、预算用尽分别记录。TC预算耗尽保留真实栈顶，但未通过状态接受的 Thought/Observation 不当合法结论评分。终止后没有新生成兜底。

沿用当前 v5 评分器：选择题精确 key；多选集合 exact 与 F1；关系标签归一化 exact；诊断使用既有 canonical_labels 精确映射（不是原来源的 LLM 语义评分）；M22 主问准确率与错误文档检测分开，空文档按既有排除规则列出，纠正文案无额外 LLM 评分。R4 是作者预期答案一致率。失败/无效占全计划分母并记错。完成率、运行有效率、评分映射有效率分别报告。

类别只使用 evaluation_labels，沿用 v5“先平均单元下非参考记录，再平均单元”的已确认规则。类别可重叠，不相加作为总体。原题/变体分别报告；配对共同正确率按该保持/该改变拆分。置信区间按原始病例组重采样；跨来源完全相同原题与选项的组连接为一个依赖组，未能识别的语义近重复不声称已排除。

生成批次、逻辑 LLM 请求（各序列）、检索请求、额外打分前向、token、延迟分别统计。正常满额 i-MedRAG为22个逻辑请求、12次检索；同轮QA可共享物理生成批次，每条QA独立缓存和恢复，物理批次数按实际batch ID去重统计。TC为至多8个动作生成，无额外状态打分前向。执行配置v4的32000 padded-token合批上限只影响并发形状；单个合法长请求完整执行。

#### 开发与正式测试隔离

24个固定开发输入：BigBio MedQA validation的前12条；本地 MedEinst train 文件中排除全部正式病例组/完整输入后的前12条。来源路径和原始记录哈希逐条保留；排除记录见 dev_overlap_audit.json。训练文件名并不证明无重叠，实际检查已执行。

用户最新指令收紧本轮至方法复现和必要开发验证。仅运行上述24条训练/开发输入。早先准备的15条正式输入盲检查清单未执行，模型没有接触该清单；不以此改提示或阈值。TC-RAG保持上游默认sigma=1.2。其他原生格式和证据干预接口由隔离的固定响应单元测试验证，不能称已经完成全部来源的真实模型验收。

#### 历史可比性

TC-RAG按用户2026-09-12指令用Qwen3-8B非thinking，对照M5的backbone/语料；i-MedRAG用Llama-3.1-8B，对照M4。TC原始医学论文Qwen1.5-32B及医学预训练并未安装。两新方法间不能把差异归因于算法而忽略backbone。现有M0/M2大量64-token最终预算、vLLM引擎及旧预测复用限制保留原义；它们与本包不构成严格共同预算/引擎下的主因果对照。未改写任何历史预测。
