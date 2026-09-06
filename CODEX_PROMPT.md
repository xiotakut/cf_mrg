# Codex 执行 Prompt：Medical RAG Counterfactual Baseline Screening

你是 coding agent。研究方案已经在同目录 `RESEARCH_PLAN.md` 中确定；先读该方案，再执行本文件。**本轮只实现和运行 baseline screening，不开发、训练或评价新的反事实增强方法。**

## 1. 任务目标与研究边界

仓库：`https://github.com/xiotakut/cf_mrg`。

目标是用同一套本地 all-Llama MedRGAG 基础实现，比较以下五个现有数据入口：

- MedEinst；
- MedPIC-Bench；
- CPV-MedQA；
- Cultural-Cues 医学 QA 反事实集；
- MedCounterFact。

以原题/变体独立推理为前提，分析 accuracy、配对变化、应该更新/应该保持的错误、类型与来源的混杂，以及相对于 Direct 和 retrieval-only RAG 的差异。

不要假定每个 benchmark 必然下降。不要为显示 taxonomy 有效而重新分组。不要从错误结果挑选题目。不要扩展为所有候选 benchmark × 所有方法的大矩阵。

规划助手没有成功读取当前 GitHub HEAD；最近上传的证据快照是 `53aaff676439066f8d0b6478404c91e7ece3528f`。**这不是命令你 checkout 此提交。** 在当前本地分支中检查真实状态，复用正确修复过的实现。

## 2. 当前研究中已排除的方向

本轮不得执行或为之初始化额外模型：

```text
Profile / DDXPlus profile scoring
CFShift / preference-shift scorer
CPG / counterfactual edit generation
CF-KADS / delta-aware retrieval
ECR-lite / expert fusion
RiskRoute / residual adapter / preserve-revise gate
MA-RAG / Qwen sidecar
NICE / transition cards / world model / teacher oracle
full option-sequence likelihood scoring / permutation ensemble
```

旧代码和旧结果不要删除。只在本轮调用链中排除它们。

不要因为历史 Profile 方法达到高准确率，就误把其路径当作 baseline。不要运行 `run_cfmoe.py` 或完整 sidecar 后仅在最后去掉融合项；那仍然消耗了不需要的计算。

## 3. 先定位真实基线，而不是猜函数

阅读当前根 README、包内 README、AGENTS 的适用范围、最新报告和实际配置。历史 AGENTS 可能描述 WM 阶段，不能据此扩展本轮任务。

至少检查以下已有线索是否存在、现在指向什么：

```text
cf_medrgag_validation_pack/scripts/run_deltarank.py
cf_medrgag_validation_pack/scripts/run_cfshift.py
cf_medrgag_validation_pack/scripts/run_cfmoe.py
cf_medrgag_validation_pack/results_marag_cf/commands.sh
cf_medrgag_validation_pack/results_marag_cf/summary.md
```

搜索 `medrgag_proxy`、`medrgag_mcq_proxy`、M2、KGCC、KADS、reader、retrieval 等实际符号，找到基础流水线的最短可复用入口。上述文件是定位线索，不保证当前函数签名。

在 `baseline_contract.md` 里写一张实际调用表：

```text
stage -> actual file/function -> model -> decoding/config -> input/output
```

记录当前 commit、checkpoint/tokenizer 路径或 revision、精度、chat template、语料及索引、BM25/MedCPT、各阶段候选与文档数量、温度/top_p/token limits、最终文档数。

方法结构必须是：

```text
source-balanced initial retrieval
→ reranking / initial evidence
→ KGCC summarization and missing-knowledge exploration
→ complementary document generation
→ original KADS selection
→ original final reader
```

原论文官方实现只作核对来源：

```text
https://github.com/ll0ruc/MedRGAG
https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py
https://github.com/ll0ruc/MedRGAG/blob/master/src/medrgag.py
```

**不要盲目用官方混合模型参数覆盖当前 all-Llama 基线。** 先确立当前本地可运行、没有后加模块的配置；记录与论文差异。正式名称使用 `medrgag_llama_base` / local reproduction，不使用 exact published SOTA reproduction。

不要在未保留用户未提交修改的情况下 reset、checkout、清理文件或删除缓存。结束时提交本轮代码/报告到当前工作分支；除非已有明确发布约定，不自行推送 main。

## 4. 三个固定方法

### M0：`direct_llama`

同一 Llama checkpoint，仅输入当前题目的合法任务信息。包含患者情境、全部原生选项，以及数据集自带的必需证据。

### M1：`retrieval_only_llama`

复用 M2 对该输入的首次标准检索/重排结果与同一 reader。没有 KGCC、生成补充文档、KADS。

### M2：`medrgag_llama_base`

完整基础主干。不能通过关闭 KGCC/KADS、减少固定文档/候选数量或改变 decoder 来节省时间。

三者共享任务输入合同、原生答案空间与解析。M1 的上下文数使用基线的原始检索 reader 配置；记录与 M2 最终上下文的差异。

**同一原题只算一次，之后可以被多个配对比较复用。** M1/M0 不重复运行完整检索生成链。

## 5. 轻量工程原则

不要创建新的 gate 框架、几十种配置版本、hash 注册表、审批系统、通用工作流引擎或大型 schema 层。

需要保留的最小实验正确性措施：

- 推理可见输入与评价标签明确分离；
- 保存 raw response、invalid 原因、模型配置与 source IDs；
- 一个小型合同测试；
- 一个固定性能测试；
- 断点续跑；
- 基本指标恒等式测试。

这些是实验有效性要求，不是 fail-closed 推理策略。

系统性格式问题在 smoke 时修复；正式结果中 malformed response 计 invalid/wrong，不猜答案、不映射为 PRESERVE、不复用另一方法答案。允许最多一次仅用于格式恢复的固定 repair，须保留初次输出、repair 输出、调用成本和原始失败率；所有对应方法使用相同规则。不得利用 gold repair。

普通网络/服务重试有明确上限；不得保留无限等待 `</think>` 或无限 JSON 重试。

## 6. 建议最小代码与产物结构

沿用现有项目组织。若缺少统一入口，可新增：

```text
scripts/run_cf_baseline_screening.py
scripts/analyze_cf_baseline_screening.py
configs/cf_baseline_screening.yaml
results_cf_screening/
  baseline_contract.md
  acquisition.md
  benchmark_summary.csv
  screening_items.jsonl
  evaluation_labels.jsonl
  taxonomy.jsonl
  predictions.jsonl
  stages.jsonl
  metrics.json
  benchmark_metrics.csv
  paired_effects.csv
  category_metrics.csv
  transitions.csv
  efficiency.csv
  taxonomy_identifiability.json
  statistics.json
  data_checks.md
  summary.md
  commands.sh
  figures/
```

大段文档可放可恢复的本地压缩缓存，`stages.jsonl` 保存对应引用和必要摘要；不要只保留不可访问的临时路径。受限文本、模型权重、凭据和整个检索库不提交 Git。公共输入是否可再分发按原许可处理，不确定时只提交下载器、IDs 和派生指标。

## 7. 数据下载 allowlist 与实际资源

优先使用项目已有合法本地缓存，并核对 revision。缺失再下载以下官方来源。

### 7.1 MedEinst

```text
https://huggingface.co/datasets/zhui711/MedEinst
```

主要字段已核实：

```text
case_id, case_type, age, sex, narrative, ground_truth
```

按 `(dataset revision, split, case_id)` 分组，control/trap 组成完整 pair。不能用裸 case_id 跨 split 判断重复，因为历史发生过 namespace collision；再比较规范化完整叙述以确认相同病例。

主样本：300 个完整官方 test pairs，固定 seed 20260906。优先在历史未使用的合格池中抽取，但 screening 并不要求所有题全新；若不足，按事先顺序补入已用题并标 `previously_exposed=true`。**任何不足/补入都在看此次输出前完成并记录。**

遍历可找到的历史 test/dev/calibration 与早期 DeltaRev 资产，只为记录 exposure；不要只排除最后两个文件然后宣称 pristine。

采用原生独立诊断：每次只有一个 narrative。不能把 control/trap role、配对文本、gold、delta、疾病画像提供给任一方法。

开放诊断输出合同需明确请求一个诊断，而非填空模板里的字面 `concise diagnosis`。不要直接调用含空 options 的 MCQ prompt。对 KGCC 中明确引用 options 的措辞做最小任务格式适配，保存全文；核心阶段、知识来源、采样预算不变。

使用官方 canonical label 清单及来源可核实的同义表达做确定性规范化。允许大小写/空白/标点标准化，不能根据 test 对错增加别名，不能自动把 `chronic bronchitis` 与 `Bronchitis` 视为医学等价。多个矛盾诊断无明确最终答案时为 ambiguous/invalid，而非选择碰巧等于 gold 的一个。

保存 raw-exact、canonical-match、unmapped/ambiguous 率。没有可用官方语义 evaluator 时，明确写为规范化匹配 screening，不冒称原论文官方语义评分。不要调用新的大型 judge 作为主评估依赖。

#### 四选项辅助敏感性

主结论不使用 gold-centered MCQ 代替原生诊断。仅对预定 60 对做既有四选项协议的辅助检查：优先选择 300 对里已有冻结选项的病例；不足时从已有冻结 MCQ 资产选额外病例，并为这些病例保存相应 native 结果。标明是附加样本。

可以复用现成选项/旧构造工具，但不得运行 Profile scorer 或为了该辅助项建立新疾病画像。缺少可验证构造资产时，报告该辅助项 unavailable，不用不明选项凑数。

每对 control/trap 共享相同选项语义和固定排列。gold 只在离线 MCQ 构造和评价中使用，不能给推理标注哪项正确。输出 `protocol=derived_four_way`，不计作第二个 benchmark。原生/四选项结果单列。

### 7.2 MedPIC-Bench

```text
https://huggingface.co/datasets/TIM0927/MedPIC-Bench
```

全量 467 行是预期发布规模；若当前 revision 不同，记录实际差异，不强行截取到 467。

已核实字段包括：

```text
instance_id, patient_vignette, question, options, answer
benchmark_task_family, taxonomy_reasoning_operation
taxonomy_patient_info_type, taxonomy_clinical_department
```

推理必须组合 patient_vignette+question+全部 options。`answer` 是集合时保留真正多选合同；不能默认单选，不能改成未经校准的逐项 Yes/No scorer。

评价 exact-set、option F1、预测集合大小、GF/CF 和官方 operation slices。忽略 `answer` 的顺序，但不忽略内容。

对 None/All-of-the-above 保留官方选项含义；语义跨题比较需要先映射选项文本。不要用 A/B/C 字母的变化代表规则变化。

只有官方显式 pair map 或有文档说明的确定映射才做 paired analysis。数字相邻、ID 类似或高文本相似都不足以恢复官方 89 对。没有映射，GF−CF 差必须标记 `unpaired_composition_gap`。

### 7.3 CPV-MedQA

```text
https://github.com/kenza-ily/diagnose_treat_bias_llm
https://huggingface.co/datasets/kenza-ily/medqa-cpv
```

已核实字段包括：

```text
case_id, case_text, question, option_a..option_d, answer_idx,
answer, gender, ethnicity
```

实际字段大小写/复数以文件为准。

按原始病例组抽 60 组，保留全组正式变体。**先查 `case_text` 与 `question` 的关系**：不得把已包含完整问题的 perturbed case_text 与原始完整 question 直接拼接，造成两个不同患者并存。只在字段确实分离时补终问句。

原题必须从官方原始字段或 MedQA source ID/确切文本恢复；不能用 White/Male 当 reference。无法恢复则该组仍可报告组内 invariance，但不得编造 reference-drop。

记录 no-op 编辑、病例是否适合患者属性变换、是否有明显冲突。规则在模型输出前冻结。除无法构成任务的记录外保留原发布集主分析，另报告事前质量标记的敏感性分析；不要事后删除 baseline 失败样本。

HF 的 `train` 名称不代表本研究训练集；只按来源和作者用途使用，不在这轮训练模型。

### 7.4 Cultural-Cues 医学 CF 集

官方仓库拼写为：

```text
https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs
Data/final_augment_test_questions.json
Data/test.jsonl
```

论文中某些链接有拼写错误；不要因此下载另一个不相关项目。

预期 150 原题 × (1 Original + 1 Neutral + 3 cultures × 3 edit types)=1,650 输入。读取实际 JSON 结构与原题映射，确认 Neutral 在文件中是否已经提供。**不要把发布的 Llama/GPT 最终答案文件当测试 gold 或缓存复用。**

对三类操作采用作者定义：Id、Context、Id+Context；Neutral 单独作为编辑/长度对照。不重新在线调用模型生成 augmentation。

如果原始发布缺少某条件，记录缺失并仅对真实存在且配对有效的条件分析；不得声称已完整复现 1,650 条。数据入口已确认，但规划阶段没有完整解析该 JSON，必须在 acquisition report 中给出实际记录数。

全部原生选项保留，包含超过四项的题。完整 150 source groups 全部跑，不在看到掉点后再选文化或变体。

### 7.5 MedCounterFact

```text
https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence
MedCounterFact_original_data.jsonl
MedCounterFact_replaced_data.jsonl
DataFormat.md
```

主要字段：

```text
index, question, article_summaries, metadata.id,
metadata.answer, metadata.MainCategory, metadata.SubCategory,
metadata.item, metadata.original_review
```

以 metadata.id 对齐 original 和所有 replaced records。抽 80 个原始问题，保留各自发布的替换。优先保证四 MainCategory 可覆盖；不要用结果筛选四类。缺失不是模型错误，记录不完整组合。

只将顶层 question + article_summaries 以及原生任务格式交给模型。**metadata.question、treatment A/B 可能仍是 original 内容，不得回填到替换实例。** metadata.answer 和类别/替换词标签仅供评价和分组。

题内 evidence 在 M0/M1/M2 都是必需输入，不能被 KADS 丢弃。M2 保留原来的外部检索与 KGCC，这恰好可以观察参数/外证干扰；不要为了理想结果临时关闭或加入“必须无条件遵循反事实”修正器。

输出比较关系 higher/lower/no difference 或明确 uncertainty；别把自由生成失配、拒绝和语义不确定合并成一个标签。EA、uncertainty、输出分布单独报告；只有真实 gold 可评分现实合理性/安全维度。

不把 EA 与诊断 accuracy 平均，不默认高 EA 等于临床安全。

## 8. 默认不执行的扩展

MamaBench、LabTest、CLIR、AMQA、MedEqualQA、MediEval、ECG、GenMedicalEval、CLadder、CounterBench、MedRGB、BioRAB 都不是自动任务。

可记录是否已有合法可用资产，但不能因为核心缺一项就自行替换并仍称五项完成。没有授权时不自动同意条款、申请访问或把权限缺失变成模型错误。默认完成其余已就绪集合并报告缺项。

MamaBench 是后续独立诊断来源的首选；当前任务只在明确配置 `include_mamabench=true` 且合法数据与协议已齐备时追加，不挤占核心批次。默认 false。

## 9. 数据准备与五条真实样本自检

每个核心 benchmark 自动选取固定五个 source units，生成 `data_checks.md`：

```text
source id / revision
模型实际看到的完整输入字段名
必要的内容节选（不发布受限文本）
reference/variant 映射来源
gold 类型与输出空间
任务约定与操作标签依据
潜在歧义
```

这不是新的人类审批 gate。目的是让你在大跑前检查：患者 vignette 是否丢失、原题是否重复粘贴、gold 是否混入、选项是否被截断、两种患者是否同时出现。

`screening_items.jsonl` 存推理所需最少字段及无语义暗示的 item_id；`evaluation_labels.jsonl` 另存 gold、source/group/role/type 等。

不要通过一个混有 gold/配对正文的大对象传给各推理函数后依赖 prompt “不要看”。在构造 solver 输入时明确筛选字段。

保存原始文本，不为了更好分类自行改写病例或修复临床矛盾。必要格式修复如编码/空格可以做，但必须可追溯。

## 10. Taxonomy 标注：先于模型表现

使用 RESEARCH_PLAN 的三轴定义。

### 任务约定

```text
clinical_update
answer_invariance
hypothetical_evidence_world
```

### 操作标签（允许多个）

```text
presence_polarity
measurement_threshold
temporal_history
clinical_evidence_substitution
identity_attribute
contextual_addition
hypothetical_entity_replacement
mixed_or_unresolved
```

### 独立字段

```text
clinical_target
expected_answer_relation
edit_scope
answer_format
original_source_family
construction_family
native_or_derived
pair_mapping_status
annotation_source
annotation_confidence
```

优先直接使用官方字段及确定性 diff/规则。对 MedEinst 中不易归类的复合编辑，宁可 mixed_or_unresolved，不用一个新大模型强贴标签。必要的小规模自动语义标注可以复用本地 Llama、固定 prompt、独立保存，但不得看预测或文档；不能声称经过医学人工验证。

不存在正式 pair 时，不发明 reference delta。MedPIC 的官方 operation 标签可用于行级分类，答案改变关系仍可能 unknown。

expected_answer_relation 可由评价侧的 canonical gold 计算，但绝不送入任何 baseline。跨排列比较答案语义/label ID，不比较字母。`not mentioned` 不是 `absent`。

在首次分析模型结果前保存 taxonomy 和 sample list，后续不能根据掉点重命名类别。发现明确标注实现 bug 时可以更正，并记录改动范围与更正前后敏感性，而不是无痕改变。

## 11. 单病例推理与任务格式

所有 reference/variant 独立请求；无聊天状态、上一答案、对照病例、gold delta 或类型标签。

M0/M1/M2 在一个 benchmark 内共享 reader 合同。对于原生多选、开放诊断、证据比较，允许最小 I/O 适配；记录实际 prompt，不改核心推理结构和知识检索政策。

不要加入“你正在解反事实问题，请修改答案”的新指令。这会把 baseline 变成 CF prompt 方法。

保留当前主干 reader 的回答方式；不要主动作多排列平均、投票或全选项 logprob 评分。仅记录系统自然产出的分数；不要为日志额外触发 sidecar。

保持原配置信息完整；若长输入超过上下文预算，报告 overflow 并使用预先冻结的任务兼容政策，不能静默裁去关键患者状态。先在数据预检中定位，不在看到结果后选择性丢题。

## 12. 成本预算与执行方式

目标：单个约 24 小时执行批次交付多个 benchmark 的可信结果，而非一天为一个 benchmark 运行所有历史实验。

### 固定完整 screening 档

```text
MedEinst: 300 pairs native
MedEinst: 60 pairs derived-four-way sensitivity (existing assets when available)
MedPIC: full released set (~467)
MedCounterFact: 80 source groups + all available declared variants
CPV-MedQA: 60 source groups + all declared variants + authentic reference
Cultural-Cues: 150 complete source groups (~1650 inputs)
M0/M1/M2 for all primary inputs
```

### 唯一预定紧缩档

仅在正式输出尚未被检查、当前服务器实测表明完整档不可能满足批次预算时使用：

```text
MedEinst: 200 pairs
MedCounterFact: 60 source groups
CPV: 40 source groups
MedPIC/Cultural-Cues: unchanged full small sets
```

其他方法、参数和变体覆盖不变。使用紧缩档必须在报告和 summary 表注明，不能叫全量各集。若仍超预算，给出预计任务数与缺口，运行各 benchmark 的预定完整 source-group 前缀，并如实标 partial；不能保证性宣称已全部完成。

### 有效的工程优化

- 使用常驻 Llama 服务/引擎，避免每个小分片反复加载权重。
- 跨独立病例批处理同一阶段；让病例 A 检索时病例 B 生成。
- 将 MedCPT 重排合并为微批，不改变顺序、分数或截断语义。
- 在可用 GPU 上测试单副本与有限独立副本调度；不要终止不属于本任务的进程。
- 预填充缓存与精确输入缓存；保持相同原题只计算一次。
- 同一知识库/模型/模板/参数/输入/选项/上游证据一致才能复用该阶段。语义相近不等于相同，尤其否定和数值变化。
- 批处理次序变化不应使随机种子取决于“这是 control 还是 trap”；给每个输入稳定、角色无关的预定 RNG 设置。

仅测试少量吞吐配置；不要把性能调优本身变成一天的网格。当前 vLLM 0.8.5 接口以实际安装为准，不为单个参数贸然升级所有依赖。

以下优化禁止：减生成候选/文档数、关闭 KGCC、换量化后沿用同名、截短推理、只算易题、按答案正确性动态跳过、把失败改成别的方法答案。

### 必须输出的效率数据

```text
unique input tasks / source groups / pairs / total LLM requests
per-stage prompt & completion tokens
per-stage wall time; pipeline makespan (not sum of overlapping times)
cache hit counts; cold vs reused workload
queue time / tokens-per-second / active batch stats where available
retries, invalids, truncations
completed vs planned groups for each benchmark
GPU allocation and versions
```

不要将历史 sidecar 的 1h43 阶段当成本轮精确吞吐，也不要使用 MA-RAG 的26小时进行本轮估时。

## 13. Smoke 与最低正确性检查

从开发或明确标记的合同样本里，每个核心 benchmark 选 5 个输入，包含原题/变体、MedPIC 多选和 MedCounterFact 必需证据。试跑三个方法，并人工式地由 agent 查看实际 raw prompts/responses。

检查：

1. gold/配对正文/类别提示没有进入 baseline；
2. 原生选项和必需患者信息没有丢失；
3. M2 确实执行 KGCC/KADS，其他专家没有被调用；
4. 标签映射和多选集合解析正确；
5. 同一原题缓存没有被错用于反事实输入；
6. option permutation 只影响映射，不把 letter 当 diagnosis；
7. 同时记录模型错误和 parse/transport 错误。

系统性错误先修，不跑几百题后才发现输出都复制占位符。不要因此新增大规模 schema/gate。

用若干完整 source groups 的真实长度记录性能，然后在打开正式正确率前冻结完整/紧缩档。smoke 样本明确标记，不冒充 untouched test。

另外预定 20 个真实输入，完整流水线用第二个独立 seed 复测一次并绕过答案缓存，只估计随机性；不选最佳 seed，不将重复结果集成为主预测。

## 14. 评价实现与公式

### 基本表

每种方法、benchmark、原生协议、原题/变体、官方子类分别保存：N、source groups、正确数、invalid、accuracy 或对应原生分数。

完成的合法请求若输出非法计错并保留 invalid。没有执行的请求是 pending/failed transport，不作为“模型答错”补入，必须显示完成率。主要配对效应用预定并完整运行的 source groups；缺失原因和数量另列。

### 配对四格

对可验证 reference–variant pairs：

```text
n11 = reference correct & variant correct
n10 = reference correct & variant wrong
n01 = reference wrong & variant correct
n00 = reference wrong & variant wrong
N = n11+n10+n01+n00

A_ref = (n11+n10)/N
A_var = (n11+n01)/N
drop = A_ref-A_var = (n10-n01)/N
pair_accuracy = n11/N
conditional_success = n11/(n11+n10)
conditional_failure = n10/(n11+n10)
```

根据 gold relation 分别称 correct revision / correct preservation / harmful flip，不能混为一个指标。分母为0输出 null/NA。

对于 gold 不同且 reference 正确的 pair，统计 `variant_prediction == reference_gold`，得到 old-answer persistence/BTR。invalid 不自动当 old-answer persistence，但影响 variant accuracy。

语义 flip、changed-but-wrong、stable-but-wrong 单独保存。多变体先每个源题/条件平均再跨源题平均；raw micro 作为补充。

### 方法间比较（不要和输入变化混用）

```text
R = M0 wrong & M2 correct
H = M0 correct & M2 wrong
introduced_error_rate = H / all_items
conditional_harm_rate = H / M0_correct
OCP = 1 - conditional_harm_rate
net_gain = (R-H)/N = accuracy_M2 - accuracy_M0
```

不使用混淆过的统一 harm_rate 名称。写微型测试校验恒等式。

### 三方法差中之差

相同 paired subset：

```text
amplification_M2 = drop_M2 - drop_M0
amplification_M1 = drop_M1 - drop_M0
```

正值提示比直接作答更敏感，不自动证明检索错误、幻觉或临床危害。

### 专用指标

- MedEinst：raw/canonical accuracy、pair accuracy、BTR与分母、正确换诊断率；native/derived 分表。
- MedPIC：exact-set、micro/macro option F1、预测/真实集合大小、GF/CF、官方 operation；无 map 不做 paired metrics。
- CPV：按性别/族群操作与来源分组，no-op 和原题恢复状态明确；不是所有变化都解释成同一种医学效应。
- Cultural：Original、Neutral、Id、Context、Id+Context；按文化及跨文化源题平均，分别相对 Original 与 Neutral。
- MedCounterFact：EA、uncertainty、输出分布、按 MainCategory；不要统一成 clinical accuracy。

## 15. taxonomy 检验：必须允许结果为不可识别

先输出 benchmark×operation×answer_relation×source_family×format 的计数表。

只有在一个操作至少跨两个合适 benchmark/来源、且有必要组内变异时，才计算可解释的跨集类型比较。两份 MedQA 衍生集只叫同源构造重复，不叫独立临床来源。

模型分析在语义和评价方式相容的子域内进行。比较：

```text
base explanatory model:
  dataset/source + format + reference length + edit length

augmented model:
  above + operation tags + available task interactions
```

不把参考题一次预测的对错简单当作无噪声题目难度。控制原题差异优先用原题内对照；独立难度估计不足时报告。

拟合前检查设计矩阵秩、完全共线、有效样本和类别覆盖。type 与 dataset 绑定时，输出：

```text
status: NOT_IDENTIFIABLE
reason: operation is confounded with benchmark/source/format
```

不要通过正则化、随意删掉 dataset 控制或强行随机效应来“做出”类别显著性。

同类相似仅作预设 ±5pp 的探索性等价检验；不能用 p>0.05 证明相同。区间过宽报告 inconclusive。

留一 benchmark/source 分析只在同类标签和评价语义能跨训练/测试保持时执行。否则报告 unavailable，而非全库硬拟合。

来源不足导致无法验证整个 taxonomy 时，这是研究结论之一，不是代码失败。

## 16. 统计与稳健性

- 2,000 次 source-group cluster bootstrap，整组变体重采样。
- 原始 MedQA 题在 CPV/Cultural 重复出现时，建立跨资源来源映射。不能仅按 numeric ID 认为相同；使用官方 source mapping 或保留题意/选项的规范化匹配，近似匹配只标 suspected。
- 主要配对比较用 McNemar 与 Holm 修正；提前限定主比较，不对所有事后切片挑显著结果。
- 非配对 MedPIC GF/CF 仅报告原生组差与适当区间，不伪装成 paired test。
- 报告 MedEinst native/derived、质量标记、已曝光/未曝光、去除重叠源题等预先规定的敏感性；不据此挑最好表。
- 20 输入重复实验估计随机 flip；不将其结果隐含扣除变成“校正准确率”。

## 17. 不依赖额外 judge 的机制线索

利用保存的 stage artifacts 离线统计：

```text
reference/variant retrieval overlap
selected retrieved/generated document counts
keyword/concept coverage proxies for actual edited spans
stage response length / truncation
prediction changes with M0/M1/M2
```

关键词覆盖、相似度与引用存在不等于 evidence correctness/entailment。文档相同也不等于 retrieval failure。报告用 “proxy/association”，不要写已证明 causal failure。

不得为了自动写漂亮机制故事，再调用全库医疗 judge、生成几十条 transition claim 或构造 oracle。

## 18. 图表与流程图

只根据实际完成数据绘制，使用 matplotlib，导出 SVG 和 PNG，给出生成命令。不得填入占位准确率。

有数据时生成：

1. 可配对任务的 drop + CI；W 与非配对结果单独图；
2. reference→variant 四格/条件失败谱及分母；
3. 类型×benchmark 覆盖和误差谱，缺失为 NA；
4. Cultural 的 Original/Neutral 对照下 Id/Context/组合比较；
5. M0/M1/M2 的变化敏感性差异；
6. 成本/吞吐表与必要曲线。

实际流程图使用 Mermaid 源码和可用的本地渲染工具；至少保留可读 `.mmd`，不为渲染下载大型新环境。图中包括真实运行的三方法与数据协议支路，未运行扩展用明确未执行标记或不画。

若关键数据缺失，不生成虚假的全局排行榜、雷达图或总体 CF accuracy。

## 19. 最终报告必须回答

1. 实际采用哪个本地基线调用链？与论文有哪些区别？
2. 哪些后来模块确实没有调用？如何由调用/成本记录确认？
3. 五个入口实际下载、合法使用、准备、计划、完成了多少 source groups / inputs？
4. 哪些属于窄临床 CF，哪些是反事实变换和假设证据世界？
5. M2 在哪些任务下降，哪些不下降，区间和分母是什么？
6. Direct 与 retrieval-only 是否也有同样变化？M2 额外效应是多少？
7. 是不更新、错误更新、稳定错误，还是格式/输入问题？
8. 同一操作是否跨 benchmark 复现？是否仅同源 MedQA？
9. 哪些 taxonomy 系数不可识别，不能从首轮得出哪些结论？
10. 原生/派生输出格式是否显著影响对 MedEinst 的解释？
11. 实际运行成本是否符合批次目标？主要瓶颈和缓存贡献是什么？
12. 后续最值得检验的一个机制是什么？只提出后续建议，不在此轮自动实施。

结论允许：支持 / 部分支持 / 不支持 / 不可识别。不要把“所有程序运行完”写成“科研假设成立”。

## 20. 完成顺序

```text
读取历史与当前代码
→ 确认 baseline contract 与资源
→ 下载/读取五入口并检查五个真实样本
→ 冻结 taxonomy、来源映射和候选 sampling list
→ 小合同测试及代表性吞吐测试
→ 在看正式效果前确定完整/紧缩档
→ 固定 M0/M1/M2 独立推理并保存 stages
→ 离线指标与统计
→ 数据支持的图表及实际流程图
→ 总结局限、完成率、成本和下一研究决定
```

不要停在只写代码；在当前服务器执行已确定且资源允许的 screening。若因为真实资产/权限/预算不能完成全部，优先保留已完成的真实结果，明确剩余，不扩大权限、不编造记录、不悄悄降低模型定义。

## 21. 最终交付与验收

交付工作代码、单条 prepare/run/analyze 命令、上述结果文件、README 更新、必要测试和 Git diff。记录当前/最终 commit；不要声称已 push 除非确实执行成功。

最终回复简要列出：

```text
实际 benchmark/protocol/样本和完成率
模型与基础配置
M0/M1/M2 主结果
paired drops 与分类可识别性
invalid / 数据缺失 / 访问限制
耗时、token、调用数与缓存复用
主要结论以及不能支持的结论
文件位置与 commit
```

最重要的是：**这轮交付一个能解释 cross-benchmark degradation pattern 的可信基础实验，而不是再次拼接一个复杂的新方法。**
