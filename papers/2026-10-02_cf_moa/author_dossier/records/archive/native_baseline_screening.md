# 历史：原生来源筛选与完整基线比较

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。保存进入R1–R5之前的来源筛选、M2全量以及M0/M1/M2完整比较。阶段间样本、旧结果复用和原生任务协议保持区分；历史研究计划不作为当前实验指令。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [Current full-release baseline comparison (completed 2026-09-07)](#record-0019)
- [RESEARCH_PLAN.md](#record-0280)
- [RESEARCH_PLAN.md](#record-0281)
- [acquisition.md](#record-0282)
- [baseline_contract.md](#record-0283)
- [data_checks.md](#record-0284)
- [findings.md](#record-0285)
- [smoke_review.md](#record-0286)
- [summary.md](#record-0287)
- [RESEARCH_PLAN.md](#record-0288)
- [acquisition.md](#record-0289)
- [baseline_contract.md](#record-0290)
- [data_checks.md](#record-0291)
- [findings.md](#record-0292)
- [smoke_review.md](#record-0293)
- [summary.md](#record-0294)
- [RESEARCH_PLAN.md](#record-0295)
- [acquisition.md](#record-0296)
- [baseline_contract.md](#record-0297)
- [data_checks.md](#record-0298)
- [findings.md](#record-0299)
- [smoke_review.md](#record-0300)
- [summary.md](#record-0301)

<a id="record-0019"></a>

## Current full-release baseline comparison (completed 2026-09-07)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第765行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Current full-release baseline comparison (completed 2026-09-07)

M0 Direct, M1 retrieval-only and M2 MedRGAG-Llama each completed **25,280/25,280
unique inputs (100%)**, covering 27,377 evaluation records per method and
75,840 unique method predictions. The user replaced the initial sampled plan
with the entire released test sets. M2 finished first; the previously stopped
M0/M1 were then completed with the same frozen inputs and configuration.

| Native benchmark / metric | Source groups or row units | Records per method | M0 | M1 | M2 |
|---|---:|---:|---:|---:|---:|
| MedEinst / canonical match | 5,383 | 10,766 | 10.93% | 7.75% | 8.26% |
| MedPIC / exact-set | 467 | 467 | 35.97% | 36.83% | 30.84% |
| CPV-MedQA / accuracy | 1,202 | 13,512 | 61.59% | 63.78% | 67.09% |
| Cultural-Cues / accuracy | 150 | 1,500 | 62.53% | 61.53% | 66.13% |
| MedCounterFact / evidence agreement | 203 | 1,012 | 66.31% | 61.87% | 66.50% |

Scores are source-group means. An additional frozen MedEinst 60-pair four-way
sensitivity contributes 120 records; M0/M1/M2 score 46.67% / 43.33% / 55.00%.
It is not a second benchmark or a substitute for native diagnosis. Exactly
identical visible inputs are inferred once; 2,097 duplicate label records
remain in evaluation.

The model is local Llama-3.1-8B-Instruct BF16, with the original tokenizer/chat
template, reader T=0/max_tokens=64, context capacity 98,304, and unchanged
per-input/stage seeds. M1 uses M2's initial source-balanced BM25/MedCPT top-5.
M2 retains retrieval/reranking, KGCC summaries and missing-knowledge exploration,
five complementary generations, original KADS, final reranking and reader.
All native options and mandatory item evidence are retained. No Profile,
CFShift scorer, CFMoE, MA-RAG/Qwen sidecar, judge, training or new method was
called. This is the local all-Llama reproduction, not an exact published
mixed-model SOTA reproduction.

M0/M1 each reuse 5,832 old predictions and add 19,448: **38,896 new calls**,
33,914,033 logical prompt tokens and 339,142 completion tokens. Completion
ran on H20 GPUs 0/2, vLLM 0.8.5, batch/chunk 64, for **45 min 14 sec**
(2026-09-07 18:44:08–19:29:22 CST); offline analysis finished at 19:31:50.
All M2 answers and upstream stage files stayed byte-identical. The earlier
M2 full-expansion batch's 15 h 32 min 01 sec is a separate historical cost.
Luna max performed read-only monitoring and the primary agent supervised and
accepted the run. Four contract/data/metric tests and full stage/cache/metric
audits passed; no pending predictions or transport failures remain.

The effects are mixed: M2 improves CPV versus Direct, loses on MedPIC and
MedEinst canonical matching, while Cultural and MedCounterFact M2−M0 intervals
contain zero. MedEinst M0/M1/M2 paired drops are +5.59 / +1.60 / +1.80 pp;
other overall paired-drop intervals contain zero. Cross-independent-source
taxonomy is NOT_IDENTIFIABLE. MedEinst has high unmapped-diagnosis rates;
CPV/Cultural share MedQA sources; MedPIC lacks a verified official pair map;
Cultural lacks released Neutral inputs; three MedCounterFact source groups
each lack one released variant category. Invalids remain scored under the
frozen protocol, and EA does not establish clinical safety. The native Holm
family expands from 29 M2-only tests to 87 three-method tests; M2 unadjusted
results remain identical, but its MedEinst adjusted p becomes .08494.

Read the [complete report](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0299)
and `$CF_FULL/metrics.json`, `baseline_contract.md`, `acquisition.md`,
`execution_provenance.json`, `validation.json`, and `artifact_audit.json`.
Result commit: `3a6b5ab17505e5ed3cc506389282042d0ef15440`.
Published archive commit: `d92232428a0dd716bef9c55b5328262a4ca35c7b`, verified
on `origin/main` after pushing. The [GitHub full comparison archive](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-07_llama_full_test_three_methods)
contains 72 tracked result files plus its README. Published benchmark archives
use separate dated directories under `$CF_BENCHMARKS`, indexed by its README;
the current v3 package remains local under `$CF_BENCH_V3`.
The old M2-only full archive is preserved.

Implementation: `$CF_PACK/scripts/run_cf_baseline_screening.py` (including
`readers` mode), `prepare_cf_reader_completion.py`, and
`analyze_cf_baseline_screening.py`. The prepare/readers/analyze/audit command,
from `$CF_REPO`, is:

```bash
bash cf_medrgag_validation_pack/results_cf_full_comparison/commands.sh
```

Use existing artifacts for result/status questions. Raw inputs, separate gold
labels and durable prompt/document caches remain locally under `$CF_FULL`;
raw benchmark text, weights and the retrieval corpus were not uploaded.
`$CF_PACK/results_cf_screening` is the older sampled experiment, not full-test
coverage. The historical sections below retain earlier protocols and open
questions; this subsection records the latest completed scope.

<a id="record-0280"></a>

## RESEARCH_PLAN.md

来源：[RESEARCH_PLAN.md](/home/data3/txy/RESEARCH_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

### Medical RAG 的反事实基线筛查：研究判断与首轮实验设计

**日期：2026-09-06；用途：研究方案，不是已经完成的实验报告。**  
**本轮目标：在不加载现有反事实增强模块的情况下，研究同一医学 RAG 主干在不同受控变化任务中的表现与错误模式。**

#### 0. 最终建议

建议开展一轮 **分层、多 benchmark、单病例独立作答的 baseline screening**。不再以“证明旧方法有效”为前提，也不把“至少五个 benchmark”当作能自动解决统计混杂的条件。

首轮固定五个评测入口：

1. **MedEinst**：临床证据变化后的诊断更新。
2. **MedPIC-Bench**：患者条件变化后的用药规则适用性。
3. **CPV 的 MedQA 子集**：原作者定义的非决定性人口属性变换。
4. **Cultural-Cues 医学 QA 反事实集**：身份、情境及组合变化，包含中性编辑对照。
5. **MedCounterFact**：提供的假设证据与现实知识冲突；独立成表。

这不是“五个严格临床状态反事实数据集”：前两项是本轮窄定义的临床 CF；第三、四项是医学任务上的反事实不变性变换；第五项是假设证据世界。后三项扩展的是研究行为边界，不为前两项补造独立临床因果证据。

统一主 baseline 是 **现有本地 all-Llama MedRGAG 主干**，不是 Profile、CFShift、CPG、CF-KADS、RiskRoute、fusion 或 MA-RAG。增加同一 Llama 的 **Direct** 和共享首次检索的 **retrieval-only RAG** 两个轻量对照，否则无法知道下降是基础模型的困难还是 RAG 的额外敏感性。

taxonomy 采用“**任务约定 + 实际变化操作 + 独立描述标签**”，不是将症状变化、诊断变化、minimal CF 放进一个平级列表。首轮可验证部分类型的可解释性，不能预先承诺证明完整分类。

#### 1. 证据基础、已核对内容与没有核对到的内容

##### 1.1 本轮资料来源

- **[H1]** 用户上传 `2026-8-23 1-32-45-Medrgag__.md`：研究讨论、旧计划、实验汇报和方向调整。
- **[H2]** 用户上传 `README.md`：2026-09-05 的 evidence handoff，记载截至 `53aaff676439066f8d0b6478404c91e7ece3528f` 的数据、结果、实现边界、硬件和运行日志。
- **[H3]** 用户上传 `literature_and_benchmarks.md` 及上一轮严格筛选报告：作为候选检索起点，不将里面的早期判断自动视为验证事实。
- **[S01–S25]** 本轮查阅的原论文、官方数据卡、作者仓库和官方文档，见文末。

##### 1.2 当前 GitHub 状态的明确限制

本次尝试了用户仓库页面、原始文件和已知提交入口，但没有成功取得 `cf_mrg` 当前 HEAD 或当前代码正文。**不能声称已经审计最新分支的具体函数。** 本次能够直接核对的是上传材料里的项目快照，以及原始 MedRGAG 官方实现。

因此，“选择现有 M2 / all-Llama 基线调用链”是有历史证据支持的具体建议；“该链在当前 checkout 的具体函数与配置文件是什么”需要 Codex 首先从本地仓库定位。不要为填补这个缺口虚构函数名，也不要直接回滚整个仓库到旧提交。[H1–H2; S01–S03]

这不阻止研究设计，但限制了本文件对当前代码的保证范围。

#### 2. 对研究状态的理解：哪些是主线，哪些已经不是

| 阶段 | 已有证据 | 对本轮的意义 |
|---|---|---|
| 静态 action slice / world-model 计划 | 未得到稳定的 action-specific deficit；强排序对照可解释一些增益 | 不再以 WM 缺失作为已经证明的病因 |
| 303 条多集 transition 实验 | full transition 20.8%，proxy 31.7%；grounding 与输出合同问题并存 | 不能复用这张异质总体表来证明 CF 分类 |
| DeltaRev | 候选、规则抽取与过度保守 gate 造成近乎不动作 | 不重新搭建 fail-closed 规则流水线 |
| DeltaRank / CFShift | MCQ 接口修复；Profile/delta 信号明显，纯 shift 较弱 | 原生任务、构造选项和增强信号必须分开 |
| CF-KADS / expert fusion | MedEinst 的 Profile 很强；fusion 未稳定胜出；MedPIC 为负 | 不能宣称跨 benchmark 已成功 |
| RiskRoute | 主结果未超过 Profile；没有安全 Pareto 改善的证据 | 不把“安全路由成功”当既定结论 |
| MA-RAG residual adapter | 同一 pair-aware sidecar 可接两个接口；去除 MA-RAG 分数反而更强 | 是接口迁移证据，不是两套基础系统提供协同的证明 |

以上均来自历史材料，不是本轮新实验。[H1–H2]

现有高分集中于 **DDXPlus 相关、四选项、pair-aware 的 MedEinst 协议**。其结果不能等同于原生开放诊断成绩，更不能用来判断其他 CF 类别。历史 test 曝光也不完全独立；筛查可以复用旧预测，但需标注曝光与协议，不再把已看过的题命名为 fresh。[H2]

**本轮研究身份：评估与诊断，不是方法开发；行为鲁棒性研究，不是临床安全保证或形式化个体因果识别。**

#### 3. 研究问题需要怎样修正

原问题“不同 CF 类型是不是下降不同”值得检验，但存在三处逻辑风险。

##### 3.1 不是所有 CF 都要求改答案

临床判别证据变化可能要求更新诊断；不决定答案的身份信息变化应该保持答案；假设证据中的实体替换可能要求保持证据比较关系，但不能因此声称现实临床建议也正确。[S04–S13]

因此应研究 **对任务要求的选择性敏感性**：该改时是否正确更新，不该改时是否保持，给定假设证据时是否按任务语义处理。

##### 3.2 同类下降接近，不是分类成立的必要条件

两个属于同一类的 benchmark 可能因为文本长度、基础难度、输出形式和构造方式不同而下降不同。两个不同类也可能偶然有相同平均下降。

更可证伪的主假设是：

> 在有可比较的任务、来源和配对结构时，预先定义的变化类型，能否解释并预测一部分错误模式，而且这种解释不能完全归结为 dataset 名称或输出格式？

##### 3.3 五个名称不等于五个独立来源

CPV-MedQA 与 Cultural-Cues 都源于 MedQA。MedEinst 与 DDXPlus 有数据血缘关系。多个变体也不是多个独立患者。来源关系需要显式登记并在统计中聚类，不能把几千变体当几千独立观察。[S04, S08–S11]

最重要的可识别性规则是：**一个类别只出现在一个 benchmark 时，类别效应与 benchmark 效应不可分离。增加该 benchmark 的样本数量不会自动解决这个问题。**

#### 4. Benchmark 搜集与选择

##### 4.1 纳入标准

一个资源进入本轮必须满足：医学文本任务；有明确的受控替换、编辑或假设；能确定该任务期望的回答行为；有公开任务记录与可用标签或官方评价定义；能在不伪造患者事实、配对、选项或答案的情况下接入。

“严格临床 CF”在本文件中特指：**遵循现实医学规则，改变患者相关条件，考察临床判断如何随之变化**。这是一项操作性范围选择，不宣称这是所有领域唯一合法的 counterfactual 定义，也不声称文本编辑已识别出个体因果效应。

文献搜索同时覆盖 clinical/medical counterfactual benchmark、minimal/contrastive clinical pairs、patient-information intervention、demographic/cultural counterfactual、hypothetical medical evidence、causal laboratory reasoning 及相关官方代码。对原清单中的边界候选回查任务与资产。

本轮完成了候选与关键原始资源核验；**没有完成所有数据库的全量导出和全引文追踪，不声称绝对穷尽全部文献。** 可核查性比无依据的“全覆盖”更重要。

##### 4.2 首轮确定集合

| 资源 | 原生任务 / 原始规模 | 访问核验 | 纳入理由 | 必须保留的边界 |
|---|---|---|---|---|
| **MedEinst** | control/trap 诊断病例；论文及数据卡报告 5,383 test pairs、49 疾病 | 官方 HF 有实际记录、pair 字段、gold 与评价说明 | 最直接的诊断证据更新；项目已有资产 | 原生开放诊断；四选项是本项目派生协议；DDXPlus 同源；实际下载数量以指定 revision 为准 |
| **MedPIC-Bench** | 467 行用药安全多选；284 GF、183 CF | 官方 HF 可见题干、患者情境、答案集合和 taxonomy 字段 | 将反事实从诊断扩展到规则适用性 | 不能把 467 行称为 467 对；未取得官方映射前，GF–CF 是非配对组差 |
| **CPV-MedQA** | 人口属性变体；项目及公开 HF 为 12,310 行快照 | 官方仓库及 HF 实际字段可见 | 检验原作者规定的答案不变行为；可复用项目数据 | MedQA 衍生；年龄/性别不能普遍视为医学无关；需检查原题恢复、无操作与冲突文本 |
| **Cultural-Cues 医学 CF 集** | 150 MedQA 原题；总计 1,650 输入，含原题、中性、三文化×三操作 | 作者仓库已定位具体输入 JSON 与原题文件；本轮没有下载解析整库 | 有同一原题下 Id / Context / Id+Context / Neutral 的交叉对照 | 与 CPV 同源；不是第五个独立临床来源；不要使用发布的旧模型输出代替新实验 |
| **MedCounterFact** | 医疗证据比较；203 原始问题及四类替换，实际行数按发布文件计算 | 官方 original/replaced JSONL 及 DataFormat 可见 | 测试外部参数知识与给定假设证据的冲突 | 单列证据世界轨；EA 不是现实治疗安全准确率；原始与替换记录用 metadata.id 对齐 |

来源：MedEinst [S04–S05]；MedPIC [S06–S07]；CPV [S08–S09]；Cultural-Cues [S10–S11]；MedCounterFact [S12–S13]。

**数量结论：**可以提出五个有合理用途、存在公开资产入口的医学领域 CF 评测入口；不能据此声称本次找到了五个已完整下载、严格临床状态 CF、且互相独立的数据集。目前本轮明确、可直接推进的窄临床主集合仍是两项。

##### 4.3 优先扩展、暂不运行与排除

| 候选 | 决定 | 理由 |
|---|---|---|
| **MamaBench** | 最优先扩展；本轮默认不自动运行 | 217 对妇幼诊断病例，可提供重要独立诊断来源；官方 HF 需要授权。已有合法访问时可追加，不绕过权限。[S14] |
| **临床检验因果推理 / LabTest** | 暂不进首轮 | 99 是全部关联/干预/CF 问题规模，不是 99 CF pairs；还需确认 CF 子集及可复用于新模型的 reference；对既有回答的人工评级不是新模型 gold。[S15] |
| **CLIR 受控编辑子集** | 指定子集候选，整库排除 | 论文的 CF 编辑限于可确定重算标签的理解/推理任务，排除了预测/决策任务；项目缺少完整编辑资产。[S16; H2] |
| **FairMedQA / AMQA** | 对抗性 stress extension，首轮不跑 | 真实记录含大段对抗描述，有时增加治疗机制等提示，不是仅人口属性替换；801 原题不能作为干净身份不变性对照直接与 CPV 合并。[S17] |
| **MedEqualQA** | 候选，当前数据就绪度不足 | 论文相关，但本轮看到的官方仓库只有 LICENSE；不同 CSC 消融不能自动继承相同正确性标签。[S18] |
| **MediEval** | 受权限和任务协议约束的扩展 | 四象限患者上下文/知识推理有价值，但需核验 MIMIC/UMLS 访问及正式评价，不混成 MCQ drop。[S19] |
| **ECG-Expert-QA、GenMedicalEval 的 CF 部分** | 保留文献，不进当前主集合 | 尚未核实可用纯文本 CF 记录和标签语义；不能仅根据栏目名纳入。[S20] |
| **肿瘤 CSS 反事实** | 暂缓 | 长上下文、访问和编辑有效性问题；论文自身报告某类较高不一致性。[S21] |
| **MedRGB / BioRAB 证据污染** | 相邻鲁棒性扩展，本轮不跑 | 错误文档抵抗与遵从假设世界不具有相同正确行为；不能为凑 CF 数量合并 |
| **ReMedQA** | 非 CF 的接口/格式控制 | 格式扰动不等于临床反事实；可用少量历史数据验证 baseline 合同，不计入五项 |
| **CLadder rung-3 / CounterBench** | 一般因果扩展，本轮不跑 | 可测试形式 CF，但医学语料不一定有帮助；加入主表会引入领域与任务双重混杂。[S22] |

#### 5. Taxonomy：最终采用什么，以及怎样修订

##### 5.1 第一层：任务约定，决定怎样解释分数

| 组别 | 受控变化 | 要求模型做什么 | 首轮数据 |
|---|---|---|---|
| **C：临床条件更新** | 症状、检查、病史、患者条件等 | 按新病例重算诊断或规则适用性；是否换答案以实际标签为准 | MedEinst、MedPIC |
| **I：答案不变性** | 经原任务定义为非决定性的信息 | 不让这些变化引入错误更新 | CPV、Cultural-Cues |
| **W：假设证据世界** | 题目和证据中的干预实体被替换 | 按原任务区分证据结论、认知冲突与现实合理性 | MedCounterFact |

这层是评估协议分层，不是“所有 CF 的普适理论分类”。W 不与 C/I 合成一个总准确率或总下降排行榜。

##### 5.2 第二层：实际变化操作，允许跨 benchmark 复用

| 操作标签 | 判定内容 | 不允许的偷换 |
|---|---|---|
| `presence_polarity` | 同一临床概念的有/无、肯定/明确否定 | “没有提到”不等于“明确没有” |
| `measurement_threshold` | 数值、分级或阈值两侧条件改变 | 不凭结果推定一定触发规则 |
| `temporal_history` | 发病顺序、持续时间、既往治疗或检查状态改变 | 普通未来预测不自动成为 CF |
| `clinical_evidence_substitution` | 一项症状/检查证据被另一项替换 | 不能因文本相近就声称只改一个临床变量 |
| `identity_attribute` | 身份、代词、族群等变化 | 在 C 组可为临床相关因素，在 I 组才按任务约定不变 |
| `contextual_addition` | 增加情境线索；Cultural-Cues 有官方 Id/Context/组合 | 涉及实质新病史时不能继续称纯身份替换 |
| `hypothetical_entity_replacement` | 给定证据的实体替换 | 不等同于患者接受真实干预后的结局 |
| `mixed_or_unresolved` | 多种变化并存，或无法可靠判定 | 不为了表格完整强分到单一类 |

标签优先使用作者的明确元数据；病例差异提取和必要的自动判别只服务离线标注，不输入 baseline。一个样本可有多个标签；单标签可比分析与 mixed 组分别报告。

##### 5.3 第三层：描述标签，不当作平级类别

- **临床目标**：diagnosis、medication eligibility/safety、evidence comparison。
- **答案关系**：`change / invariant / relation_transport / unknown`；来自官方配对与语义标签，不把答案字母是否变化作为依据。
- **变化幅度**：single-concept / linked-multiple / broad / unresolved。文本长度差是另外的数值特征。
- **来源与协议**：原始题库、构造方式、输出类型、原生/派生版本、配对可靠性。

诊断发生变化是目标结果；minimal 是幅度；temporal 是操作；它们不能并列成互斥类别。

##### 5.4 设计修订与剩余风险

| 被检验的设计 | 主要问题 | 本方案的修订 |
|---|---|---|
| 按数据集名称或医学专科分组 | 不能证明 CF 类型的作用 | 使用跨集可复用操作标签，另存任务/专科 |
| 用一张互斥长列表涵盖所有概念 | 输入、输出、幅度混杂；许多样本同时落多类 | 任务约定、操作、目标/幅度分轴 |
| 按 accuracy drop 聚类后命名类型 | 分类与验证循环论证 | 先按文本及官方结构标注，冻结后再看输出 |
| 直接拟合 dataset+type 的回归 | type 与 dataset 完全共线时系数不可识别 | 先检查交叉覆盖与设计矩阵；不可识别就报告，不强行估计 |
| 以“不显著不同”说明同类相似 | 低功效也会得不显著 | 预先定义等价范围，做等价性/区间分析；否则只说未能区分 |

剩余风险仍然存在：严格临床 benchmark 少；有些类别只有一个来源；自动标签可能误判；参考标签本身可有噪声。它们不再阻止**筛查**，但阻止首轮直接宣称“普适 taxonomy 已证实”。优先补 MamaBench，是为了增加独立诊断来源，不是为了把数字变成六。

#### 6. 首轮明确的样本和运行范围

本轮是 exploration/screening，不以 sampled benchmark 冒充全量结果。原则：按原始病例/问题抽取，保留该单元所有预先规定的变体；不按模型错题或掉点幅度取样。

| 资源 | 首轮规模 | 预计独立输入数 | 用途 |
|---|---:|---:|---|
| MedEinst | 300 个完整 test pairs；支持时从未用部分固定抽样 | 600 | 原生单病例诊断主筛查 |
| MedEinst 四选项敏感性 | 优先在上述 300 中选已有冻结选项的 60 对；不足则用额外已曝光病例，单独记数 | 120 个额外输入 | 仅区分输出形式影响；不计作另一个 benchmark |
| MedPIC | 完整 467 行 | 467 | 完整 GF/CF 组比较；配对另核实 |
| MedCounterFact | 80 原始问题及每题已发布替换；不足则全部合格原始问题 | 约 400，按实际展开核算 | evidence-world 独立表 |
| CPV-MedQA | 60 个原始病例组，全部规定变体及可恢复原题 | 约 660–960，实际核算 | 身份变化不变性 screening |
| Cultural-Cues | 完整 150 个原题组 | 1,650，含原题与 Neutral | 身份/情境/组合的组内主比较 |

预计约 3,900–4,300 次 M2 输入任务（含可能的额外原生格式对照）；这不是模型调用次数，因为 M2 含多个阶段。完全相同的原题输入可复用，所以实际可能更少。另留少量重复输入噪声对照和非计分 smoke；**具体预算要用当前服务器实测每类吞吐，不使用 MA-RAG 的旧速度外推本轮。**

首轮不自动执行：全量 MedEinst、CPV 全量、多轮 MA-RAG、所有 optional benchmark、全部方法消融、多个模型或三种子全量。负结果不会触发自动扩展或改 prompt。

若预检显示范围超过一个 24 小时运行批次，可在看 screening 正确率前，按预先声明的紧缩档统一减为 MedEinst 200 对、CPV 40 组、MedCounterFact 60 原题，仍保留完整小 benchmark；报告必须称为紧缩 screening，而不是默默少跑。不得根据中途表现调整样本。

#### 7. Baseline 选择与公平性

##### 7.1 使用哪个版本

从当前 checkout 中定位最近仍然保留的 **all-Llama 原始检索→KGCC→KADS→reader 的基线路径**，以历史 `medrgag_proxy / medrgag_mcq_proxy / M2` 为线索。复用当前可工作的实现，停用后加专家；不要通过回滚恢复旧的 parser、指标和 gold 隔离错误。[H1–H2]

正式名称建议：

> **MedRGAG-Llama local reproduction，原生任务合同适配版。**

不能称为“原论文精确 SOTA 复现”，因为原论文部分辅助模块使用 GPT-4o-mini，而这里采用本地 Llama。[S01–S03]

##### 7.2 必须保留 / 必须关闭

| 必须保留 | 本轮关闭 |
|---|---|
| 同一 Llama-3.1-8B-Instruct checkpoint/tokenizer/精度 | MA-RAG、Qwen sidecar |
| 已有 source-balanced retrieval、BM25、MedCPT | DDXPlus Profile expert、CPG、自生成 CF edits |
| KGCC 的摘要、知识缺口探索、补充生成 | CFShift、CF-KADS、ECR-lite、delta query |
| 原始 KADS 选择与最终 reader | Fusion、RiskRoute、residual gate、verifier/corrector |
| 当前固定候选数、文档数、温度和生成长度配置 | 额外全选项似然、多排列集成、投票 |
| 原生题目必须提供的患者信息、题内证据 | NICE、transition cards、oracle、旧 WM 路径 |

官方实现可作为结构核对：多源检索、生成补充文档、联合选择、最终作答。但官方参数和当前本地实现的差异需要记录，不要一边筛查一边偷偷切换配置。[S02–S03]

##### 7.3 为什么需要两个便宜的额外对照

- **M0 Direct**：同一 Llama，只看该题要求的输入。MedCounterFact 的题内证据不是“外部增强”，必须保留。
- **M1 Retrieval-only**：同一初始检索和重排结果、同一 reader；不执行 KGCC/KADS。
- **M2 MedRGAG-base**：完整基础主干。

M1 复用 M2 初始检索，不重新检索另一套语料。这两个对照只是额外 reader 调用，不是两套完整的大型框架。

##### 7.4 原生任务与 MCQ 方法的不可回避冲突

无法同时做到“原生开放诊断完全不改”和“原来只接受 MCQ 的 reader 合同一个字不改”。合理方案是保留方法内部流程，允许**最小任务输入/输出适配**，并公开说明。[S03–S07]

- MedEinst 主筛查：只给当前病例，要求一个明确诊断；不能发送会被复制的 `concise diagnosis` 占位模板。主评分为冻结 canonical/来源支持 alias 的确定性规范化匹配，同时保留 raw exact 和无法归一化的比例。不能随意把不同临床亚型并为同一答案。没有可靠官方语义 evaluator 时，不冒充官方开放诊断分数。
- 四选项 60 对是输出空间敏感性，不是用较高 MCQ 分数替代原生结果；其选项构造受 gold 和 DDXPlus 血缘影响，明确标记 derived，不与原论文 SOTA 比。
- MedPIC：真正的多选集合生成与 exact-set；不要用四个独立 Yes/No 概率阈值替代原 reader。
- CPV/Cultural：保留原始所有选项与顺序；不强行截为四个。
- MedCounterFact：保留被替换的 question+article_summaries；输出比较关系/明确不确定。不要把原始 metadata 的 treatment 或 canonical question 回填到替换题。

整个 M0/M1/M2 在同一任务内使用相同的输入、答案空间、格式约定与确定性解析。

#### 8. 推理协议：让比较真的只反映输入变化

每个原始/反事实输入 **独立作答**，无共享会话记忆，无上个答案，无另一病例，无 gold delta，无类别提示。pair 只在离线分析时合并。

因此“revision”在本轮指两次独立预测对病例变化的正确响应，不表示模型在一个多轮对话中明确撤回旧答案。不要偷换成记忆或信念更新实验。

必需的题内观察/证据不能被 KADS 当作可选外文档丢掉。长输入采用预先冻结的统一上下文预算；记录截断位置和是否损失任务事实。对超预算题报告不兼容或单列，不能默认“保留前半段”后把缺信息造成的失败当 reasoning 缺陷。

同一 prompt 的重复输入可能产生随机差异。额外固定 20 个输入，各执行一次不同预定 seed 的完整复测，不走预测缓存；用于估计采样噪声。它不是三种子全量实验，也不用于挑最优 seed。

#### 9. 核心指标：统一可比部分，保留不可比部分

##### 9.1 真正配对的正确性变化

对 source unit i 的 reference 与 variant，定义正确性 C0_i、C1_i∈{0,1}。统计：

- n11：两次均正确；n10：原来正确、变体错误；
- n01：原来错误、变体正确；n00：两次均错误。

**Drop = A_reference − A_variant = (n10 − n01)/N。** 正值表示下降，所有表统一这个符号。

同时报告四格，避免“没有平均下降”掩盖大量互相抵消的错误变化。

##### 9.2 答案应变化的对

- Variant accuracy。
- Both-correct pair accuracy = n11/N。
- Conditional correct revision = n11/(n11+n10)，限定语义 gold 确实不同的 pairs。
- Old-answer persistence：原题答对且变体输出旧 gold 的数量 / 原题答对的数量；与 MedEinst 官方 BTR 对齐，并报告分母。
- Changed-but-wrong：变体确实换答案但没有换对，不当成功。

##### 9.3 答案应保持的对

- Correct preservation = n11/(n11+n10)。
- Harmful flip = n10/(n11+n10)。
- Semantic flip = 预测语义发生变化的比例。
- Stable-but-wrong：两次同样错误，不能当作良好稳健性。

同一公式因任务约定不同而对应不同临床含义；不是给全库一个含糊的“consistency”。零分母报告 NA，不填 0%。

##### 9.4 多变体数据

先在每个源题内按预定义变体/类别平均，再对源题平均；同时提供原始逐条件分数。原题只需推理一次，但统计仍保留不同对照关系。不要让变体多的患者在总体统计里获得更多隐含权重。

CPV 原题若无法可靠恢复，只做组内不变性，reference drop 标为不可用，不用 White/Male 替代“正常患者”。

##### 9.5 无可靠配对的数据

MedPIC 报 exact-set、micro/macro option F1、集合大小、GF/CF 与官方 operation slices。GF−CF 可以展示，但名称为 **非配对构成差**，不能混进配对 drop 总体估计。只有取得官方验证映射后才计算 pair metrics。

##### 9.6 MedCounterFact

EA/evidence-conditioned relation accuracy、输出不确定率、输出分布，按四类替换分开。安全/荒谬性识别仅在有合法标签或独立可靠评估时评分，否则保留定性输出而不自造 gold。**EA 高不代表临床安全高；EA 下降不必然等于临床能力下降。**

##### 9.7 MedRGAG 是否额外放大变化敏感性

对于同一配对单元：

**Amplification = Drop_M2 − Drop_M0。**

再比较 M1。若三者都下降，首先是共同任务困难；若 M2 的额外下降稳定更大，才提示完整检索–生成–选择流程的附加敏感性。它仍不能单独确定是 KGCC hallucination 还是 KADS 的责任。

M2 相对 M0 的 wrong→correct 与 correct→wrong 另记为方法间 repairs/harms，不能与 reference→variant 的变化四格混用。检查 `(R−H)/N = Acc_M2−Acc_M0`。

#### 10. 如何验证 taxonomy，而不是事后画漂亮图

##### 10.1 五个研究问题的证据要求

| 研究问题 | 首轮可以怎样回答 | 不能做什么 |
|---|---|---|
| M2 是否普遍下降？ | 各可配对 benchmark 的 drop 与区间；分 C/I/W 报告 | 把 MedPIC 非配对差和 MCF EA 合成一条“普遍下降” |
| benchmark 之间是否不同？ | 按任务/原生协议分别比较效应与失败谱 | 用原始 accuracy 排名直接解释 CF 难度 |
| 同类跨集是否相似？ | 在共同操作、任务和足够来源覆盖下比较；CPV/Cultural 为同源构造复制 | 将单一 benchmark 内成千上万变体当跨来源重复 |
| 不同类型是否系统不同？ | 优先同一原题的交叉对照，如 Cultural 的 Id、Context、组合、中性 | 让 dataset 与 type 完全绑定后宣称独立类型效应 |
| taxonomy 是否有意义？ | 类型是否增加超出来源/格式的解释、是否在留出来源上保留方向 | 将无显著差异解释成“证实同类相同” |

##### 10.2 统计实施

- 主要效应做 2,000 次 source-cluster bootstrap；原题全部变体一起重采样。跨 CPV/Cultural 的同源题尽可能统一源题键。
- 两条件成对正确性可用 McNemar；预先限定主要比较，提供 Holm 校正。多标签探索其余结果标记 exploratory。
- 同类“足够相似”预设 ±5 个百分点作探索性等价范围，报告两单侧检验或等价 90% CI；区间太宽就是证据不足，不是相同。
- 可比子域内比较仅有 dataset/source/format/长度的模型与加入 operation 的模型；先检查 design matrix、实际变异与类别覆盖。
- 若 type 完全嵌套在 dataset，输出 `NOT_IDENTIFIABLE`。正则化、随机效应和增加样本不能凭空产生缺失的交叉对照。
- 留一 benchmark/source 验证仅用于训练与测试均有相应类别、且评价语义一致的子域；不适用时报告原因。
- 300 对的配对估计通常不足以确认几百分点的等价；例如 discordant probability≈0.3 时，零附近 drop 的近似 95% 半宽约 6.2pp。这是设计示例，不是预计效果。

本轮最强的 taxonomy 检验机会是 **同一 Cultural-Cues 原题的操作交叉**。严格临床 C 组的“跨来源诊断更新规律”还需要 MamaBench 或另一个可用独立来源。

#### 11. 要记录什么，才能解释错误

保存原始响应、解析答案、各阶段原始文档/生成文档/最终选择、查询、模型和 prompt 配置、输入/输出 token、阶段时间、无效与截断状态。不得只存最后 accuracy。

低成本分析可以计算：reference/variant 文档重叠、新增信息关键词覆盖、检索分数变化、生成文档比例、错误转移。它们只是机制线索。

**相同检索文档不必然失败**：同一篇鉴别诊断文档可能同时覆盖两种情况。仅凭相似度或 LLM 自评不能声称“正确证据缺失”或“生成内容不真实”。若后续需要因果归因，再单独做固定证据、充分证据或模块干预实验，不在首轮自动展开。

#### 12. 运行成本怎样控制，而不偷偷改 baseline

允许的优化：移除本轮不需要的专家调用；常驻 Llama 服务；跨病例批处理；重排微批；检索与其他病例生成重叠；相同原题精确复用；重复评估离线计算；在显存允许时测试独立服务副本。

不允许的“加速”：删除 KGCC/KADS；减少基线规定文档/生成候选/轮次；换小模型或量化后仍使用同一基线名；缩短生成上限截掉推理；只对已知难题调用模块；跳过慢题；语义缓存把仅差否定词的病例合并；把选项似然/多排列集成当作原 reader。

vLLM 的 prefix caching 主要减少重复前缀 prefill，不能省掉实际生成 token；并发上限与 token batch 应由吞吐、排队和 KV 抢占一起判断，而不是看 GPU 利用率。[S24–S25]

历史 4h39 是 full sidecar，里面基线相关阶段约 1h43，但该阶段还包含 M0/M2 与输入展开，**不能直接推断一个原生 benchmark 的准确用时**。[H2]

将 24 小时作为执行批次预算而不是保证。先用代表性输入实测各类型成本，列出 M2 任务数、LLM 调用数、预期 token 和余量。若超过预算，在看到正式结果前采用事先声明的紧缩档。执行中保留完整未完成清单，不能把运行不完整伪装成全量。

#### 13. 图表由研究问题决定

此时不生成结果图。执行完成后，仅生成数据支持的以下图表：

1. **配对 drop + 95% CI 图**：只放可配对、同语义的指标；MedPIC 和 MedCounterFact 独立 panel/file，不做误导的共同排序。
2. **四格错误转移 / correct revision 与 harmful flip 图**：回答“不会更新”还是“乱更新”，同时显示分母。
3. **类别×benchmark 覆盖及失败谱图**：空单元标 NA，不补 0；显示哪些分类结论有交叉证据。
4. **Cultural Id/Context/组合相对 Original 与 Neutral 的对比图**：这是有明确组内因子设计的类型检验。
5. **M0/M1/M2 敏感性差异图**与 **吞吐/成本表**：分别定位 RAG 附加效应和效率。
6. **实际执行流程图**：标清数据协议分流、三个方法、独立推理与离线配对。未执行的 optional 支路不画成完成状态。

不需要雷达图、强行全库总分或没有来源的临床危害图。若某图缺少数据，报告为何不生成。

#### 14. 研究推进与结果判读

| 阶段 | 交付 | 继续条件的含义 |
|---|---|---|
| 资料与当前代码核对 | 来源/配置差异、数据可用性与调用链 | 只排除无效接口，不因没掉点停止 |
| taxonomy 与样本冻结 | 标签规则、交叉覆盖、来源关系、采样清单 | 不看模型结果分组 |
| 小规模合同与性能测试 | 每集真实样本、各方法输入输出、token/吞吐 | 系统性格式错先修；不搞极端 fail-closed |
| 首轮 screening | 五入口的三方法预测、阶段记录、完整性计数 | 固定计划执行；负结果完整保留 |
| 离线分析 | 指标、CI、可识别性、图表与失败模式 | 决定后续收窄范围而非自动加模块 |
| 后续研究设计 | 选择一个可重复、可修复机制；确定独立确认集 | 本轮不实现新方法 |

结果没有下降，是对原始假设有信息的结果；不同 benchmark 下降不同但类型不能解释，也有研究价值。只有当类型与错误模式的联系跨来源复现，才能逐步升级 taxonomy 主张。若只在同一个 MedQA 衍生家族中成立，应明确写成同源构造下的结果。

#### 15. 相关方法在本轮的角色

ECR-Agent、EA-RAG、CF-RAG、CPG、CoRFu 仍是后续优化的最近邻候选，但不进入首轮推理矩阵。现在就把它们全接回去，会把“基础失效是什么”与“哪个插件涨点”重新混为一谈。

分类是实验组织与可检验假设，不必硬包装成独立理论贡献。首轮完成后才能决定：做临床更新方法、研究无关变化敏感性，还是聚焦证据世界冲突。这不是提前放弃方法，而是避免重复过去“先搭复杂模块，后发现任务与指标没对齐”的路径。[H1–H2]

#### 16. 来源索引

以下是本方案使用的关键原始来源，而非“全部论文已穷尽”的声明。访问核验日期为 2026-09-06；文件下载后的 revision 和行数由执行报告补记。

- **S01** MedRGAG paper: https://arxiv.org/html/2510.18297v1
- **S02** MedRGAG official main: https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py
- **S03** MedRGAG official implementation: https://github.com/ll0ruc/MedRGAG/blob/master/src/medrgag.py
- **S04** MedEinst paper: https://aclanthology.org/2026.acl-long.1847/ ; https://arxiv.org/html/2601.06636v1
- **S05** MedEinst data and BTR definition: https://huggingface.co/datasets/zhui711/MedEinst
- **S06** MedPIC paper: https://arxiv.org/html/2608.03028v1
- **S07** MedPIC data: https://huggingface.co/datasets/TIM0927/MedPIC-Bench
- **S08** CPV paper: https://aclanthology.org/2025.naacl-long.114/ ; code: https://github.com/kenza-ily/diagnose_treat_bias_llm
- **S09** CPV-MedQA data: https://huggingface.co/datasets/kenza-ily/medqa-cpv
- **S10** Cultural-Cues paper: https://arxiv.org/html/2601.20102v1
- **S11** Cultural-Cues official repo: https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs ; inputs: `Data/final_augment_test_questions.json`, `Data/test.jsonl`
- **S12** MedCounterFact paper: https://arxiv.org/html/2601.11886v1
- **S13** MedCounterFact official data: https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence ; field specification: https://raw.githubusercontent.com/KaijieMo-kj/Counterfactual-Medical-Evidence/main/DataFormat.md
- **S14** MamaBench: https://arxiv.org/html/2607.14385v2 ; gated data: https://huggingface.co/datasets/HelpMum-Personal/MamaBench/tree/main
- **S15** Laboratory causal reasoning: https://www.nature.com/articles/s41746-026-02632-3 ; https://github.com/balubhasuran/LLM_Causality_LabTest
- **S16** CLIR: https://arxiv.org/html/2607.09880v1 ; https://huggingface.co/datasets/winall/CLIR-Bench
- **S17** FairMedQA / AMQA: https://arxiv.org/html/2505.19562v2 ; https://github.com/XY-Showing/AMQA ; actual records: https://huggingface.co/datasets/Showing-KCL/AMQA
- **S18** MedEqualQA: https://aclanthology.org/2025.sciprodllm-1.4/ ; https://github.com/rajarshi51382/MEDEQUALQA
- **S19** MediEval: https://aclanthology.org/2026.acl-long.734/
- **S20** ECG-Expert-QA: https://arxiv.org/html/2502.17475v2 ; GenMedicalEval: https://github.com/MediaBrain-SJTU/GenMedicalEval
- **S21** Oncology counterfactual sensitivity: https://arxiv.org/html/2605.30590v1
- **S22** CLadder: https://github.com/causalNLP/cladder
- **S23** Behavioral testing / contrast sets: https://aclanthology.org/2020.acl-main.442/ ; https://aclanthology.org/2020.findings-emnlp.117/
- **S24** vLLM 0.8.5 performance: https://docs.vllm.ai/en/v0.8.5/performance/optimization.html
- **S25** vLLM prefix caching: https://docs.vllm.ai/en/v0.8.5/features/automatic_prefix_caching.html

**没有执行的事情：**本轮没有修改用户服务器，没有跑任何新 LLM benchmark，没有重新拟合模型，也没有生成带假结果的图。详细执行规范见同目录 `CODEX_PROMPT.md`。

<a id="record-0281"></a>

## RESEARCH_PLAN.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/RESEARCH_PLAN.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/RESEARCH_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### Medical RAG 的反事实基线筛查：研究判断与首轮实验设计

**日期：2026-09-06；用途：研究方案，不是已经完成的实验报告。**
**本轮目标：在不加载现有反事实增强模块的情况下，研究同一医学 RAG 主干在不同受控变化任务中的表现与错误模式。**

#### 0. 最终建议

建议开展一轮 **分层、多 benchmark、单病例独立作答的 baseline screening**。不再以“证明旧方法有效”为前提，也不把“至少五个 benchmark”当作能自动解决统计混杂的条件。

首轮固定五个评测入口：

1. **MedEinst**：临床证据变化后的诊断更新。
2. **MedPIC-Bench**：患者条件变化后的用药规则适用性。
3. **CPV 的 MedQA 子集**：原作者定义的非决定性人口属性变换。
4. **Cultural-Cues 医学 QA 反事实集**：身份、情境及组合变化，包含中性编辑对照。
5. **MedCounterFact**：提供的假设证据与现实知识冲突；独立成表。

这不是“五个严格临床状态反事实数据集”：前两项是本轮窄定义的临床 CF；第三、四项是医学任务上的反事实不变性变换；第五项是假设证据世界。后三项扩展的是研究行为边界，不为前两项补造独立临床因果证据。

统一主 baseline 是 **现有本地 all-Llama MedRGAG 主干**，不是 Profile、CFShift、CPG、CF-KADS、RiskRoute、fusion 或 MA-RAG。增加同一 Llama 的 **Direct** 和共享首次检索的 **retrieval-only RAG** 两个轻量对照，否则无法知道下降是基础模型的困难还是 RAG 的额外敏感性。

taxonomy 采用“**任务约定 + 实际变化操作 + 独立描述标签**”，不是将症状变化、诊断变化、minimal CF 放进一个平级列表。首轮可验证部分类型的可解释性，不能预先承诺证明完整分类。

#### 1. 证据基础、已核对内容与没有核对到的内容

##### 1.1 本轮资料来源

- **[H1]** 用户上传 `2026-8-23 1-32-45-Medrgag__.md`：研究讨论、旧计划、实验汇报和方向调整。
- **[H2]** 用户上传 `README.md`：2026-09-05 的 evidence handoff，记载截至 `53aaff676439066f8d0b6478404c91e7ece3528f` 的数据、结果、实现边界、硬件和运行日志。
- **[H3]** 用户上传 `literature_and_benchmarks.md` 及上一轮严格筛选报告：作为候选检索起点，不将里面的早期判断自动视为验证事实。
- **[S01–S25]** 本轮查阅的原论文、官方数据卡、作者仓库和官方文档，见文末。

##### 1.2 当前 GitHub 状态的明确限制

本次尝试了用户仓库页面、原始文件和已知提交入口，但没有成功取得 `cf_mrg` 当前 HEAD 或当前代码正文。**不能声称已经审计最新分支的具体函数。** 本次能够直接核对的是上传材料里的项目快照，以及原始 MedRGAG 官方实现。

因此，“选择现有 M2 / all-Llama 基线调用链”是有历史证据支持的具体建议；“该链在当前 checkout 的具体函数与配置文件是什么”需要 Codex 首先从本地仓库定位。不要为填补这个缺口虚构函数名，也不要直接回滚整个仓库到旧提交。[H1–H2; S01–S03]

这不阻止研究设计，但限制了本文件对当前代码的保证范围。

#### 2. 对研究状态的理解：哪些是主线，哪些已经不是

| 阶段 | 已有证据 | 对本轮的意义 |
|---|---|---|
| 静态 action slice / world-model 计划 | 未得到稳定的 action-specific deficit；强排序对照可解释一些增益 | 不再以 WM 缺失作为已经证明的病因 |
| 303 条多集 transition 实验 | full transition 20.8%，proxy 31.7%；grounding 与输出合同问题并存 | 不能复用这张异质总体表来证明 CF 分类 |
| DeltaRev | 候选、规则抽取与过度保守 gate 造成近乎不动作 | 不重新搭建 fail-closed 规则流水线 |
| DeltaRank / CFShift | MCQ 接口修复；Profile/delta 信号明显，纯 shift 较弱 | 原生任务、构造选项和增强信号必须分开 |
| CF-KADS / expert fusion | MedEinst 的 Profile 很强；fusion 未稳定胜出；MedPIC 为负 | 不能宣称跨 benchmark 已成功 |
| RiskRoute | 主结果未超过 Profile；没有安全 Pareto 改善的证据 | 不把“安全路由成功”当既定结论 |
| MA-RAG residual adapter | 同一 pair-aware sidecar 可接两个接口；去除 MA-RAG 分数反而更强 | 是接口迁移证据，不是两套基础系统提供协同的证明 |

以上均来自历史材料，不是本轮新实验。[H1–H2]

现有高分集中于 **DDXPlus 相关、四选项、pair-aware 的 MedEinst 协议**。其结果不能等同于原生开放诊断成绩，更不能用来判断其他 CF 类别。历史 test 曝光也不完全独立；筛查可以复用旧预测，但需标注曝光与协议，不再把已看过的题命名为 fresh。[H2]

**本轮研究身份：评估与诊断，不是方法开发；行为鲁棒性研究，不是临床安全保证或形式化个体因果识别。**

#### 3. 研究问题需要怎样修正

原问题“不同 CF 类型是不是下降不同”值得检验，但存在三处逻辑风险。

##### 3.1 不是所有 CF 都要求改答案

临床判别证据变化可能要求更新诊断；不决定答案的身份信息变化应该保持答案；假设证据中的实体替换可能要求保持证据比较关系，但不能因此声称现实临床建议也正确。[S04–S13]

因此应研究 **对任务要求的选择性敏感性**：该改时是否正确更新，不该改时是否保持，给定假设证据时是否按任务语义处理。

##### 3.2 同类下降接近，不是分类成立的必要条件

两个属于同一类的 benchmark 可能因为文本长度、基础难度、输出形式和构造方式不同而下降不同。两个不同类也可能偶然有相同平均下降。

更可证伪的主假设是：

> 在有可比较的任务、来源和配对结构时，预先定义的变化类型，能否解释并预测一部分错误模式，而且这种解释不能完全归结为 dataset 名称或输出格式？

##### 3.3 五个名称不等于五个独立来源

CPV-MedQA 与 Cultural-Cues 都源于 MedQA。MedEinst 与 DDXPlus 有数据血缘关系。多个变体也不是多个独立患者。来源关系需要显式登记并在统计中聚类，不能把几千变体当几千独立观察。[S04, S08–S11]

最重要的可识别性规则是：**一个类别只出现在一个 benchmark 时，类别效应与 benchmark 效应不可分离。增加该 benchmark 的样本数量不会自动解决这个问题。**

#### 4. Benchmark 搜集与选择

##### 4.1 纳入标准

一个资源进入本轮必须满足：医学文本任务；有明确的受控替换、编辑或假设；能确定该任务期望的回答行为；有公开任务记录与可用标签或官方评价定义；能在不伪造患者事实、配对、选项或答案的情况下接入。

“严格临床 CF”在本文件中特指：**遵循现实医学规则，改变患者相关条件，考察临床判断如何随之变化**。这是一项操作性范围选择，不宣称这是所有领域唯一合法的 counterfactual 定义，也不声称文本编辑已识别出个体因果效应。

文献搜索同时覆盖 clinical/medical counterfactual benchmark、minimal/contrastive clinical pairs、patient-information intervention、demographic/cultural counterfactual、hypothetical medical evidence、causal laboratory reasoning 及相关官方代码。对原清单中的边界候选回查任务与资产。

本轮完成了候选与关键原始资源核验；**没有完成所有数据库的全量导出和全引文追踪，不声称绝对穷尽全部文献。** 可核查性比无依据的“全覆盖”更重要。

##### 4.2 首轮确定集合

| 资源 | 原生任务 / 原始规模 | 访问核验 | 纳入理由 | 必须保留的边界 |
|---|---|---|---|---|
| **MedEinst** | control/trap 诊断病例；论文及数据卡报告 5,383 test pairs、49 疾病 | 官方 HF 有实际记录、pair 字段、gold 与评价说明 | 最直接的诊断证据更新；项目已有资产 | 原生开放诊断；四选项是本项目派生协议；DDXPlus 同源；实际下载数量以指定 revision 为准 |
| **MedPIC-Bench** | 467 行用药安全多选；284 GF、183 CF | 官方 HF 可见题干、患者情境、答案集合和 taxonomy 字段 | 将反事实从诊断扩展到规则适用性 | 不能把 467 行称为 467 对；未取得官方映射前，GF–CF 是非配对组差 |
| **CPV-MedQA** | 人口属性变体；项目及公开 HF 为 12,310 行快照 | 官方仓库及 HF 实际字段可见 | 检验原作者规定的答案不变行为；可复用项目数据 | MedQA 衍生；年龄/性别不能普遍视为医学无关；需检查原题恢复、无操作与冲突文本 |
| **Cultural-Cues 医学 CF 集** | 150 MedQA 原题；总计 1,650 输入，含原题、中性、三文化×三操作 | 作者仓库已定位具体输入 JSON 与原题文件；本轮没有下载解析整库 | 有同一原题下 Id / Context / Id+Context / Neutral 的交叉对照 | 与 CPV 同源；不是第五个独立临床来源；不要使用发布的旧模型输出代替新实验 |
| **MedCounterFact** | 医疗证据比较；203 原始问题及四类替换，实际行数按发布文件计算 | 官方 original/replaced JSONL 及 DataFormat 可见 | 测试外部参数知识与给定假设证据的冲突 | 单列证据世界轨；EA 不是现实治疗安全准确率；原始与替换记录用 metadata.id 对齐 |

来源：MedEinst [S04–S05]；MedPIC [S06–S07]；CPV [S08–S09]；Cultural-Cues [S10–S11]；MedCounterFact [S12–S13]。

**数量结论：**可以提出五个有合理用途、存在公开资产入口的医学领域 CF 评测入口；不能据此声称本次找到了五个已完整下载、严格临床状态 CF、且互相独立的数据集。目前本轮明确、可直接推进的窄临床主集合仍是两项。

##### 4.3 优先扩展、暂不运行与排除

| 候选 | 决定 | 理由 |
|---|---|---|
| **MamaBench** | 最优先扩展；本轮默认不自动运行 | 217 对妇幼诊断病例，可提供重要独立诊断来源；官方 HF 需要授权。已有合法访问时可追加，不绕过权限。[S14] |
| **临床检验因果推理 / LabTest** | 暂不进首轮 | 99 是全部关联/干预/CF 问题规模，不是 99 CF pairs；还需确认 CF 子集及可复用于新模型的 reference；对既有回答的人工评级不是新模型 gold。[S15] |
| **CLIR 受控编辑子集** | 指定子集候选，整库排除 | 论文的 CF 编辑限于可确定重算标签的理解/推理任务，排除了预测/决策任务；项目缺少完整编辑资产。[S16; H2] |
| **FairMedQA / AMQA** | 对抗性 stress extension，首轮不跑 | 真实记录含大段对抗描述，有时增加治疗机制等提示，不是仅人口属性替换；801 原题不能作为干净身份不变性对照直接与 CPV 合并。[S17] |
| **MedEqualQA** | 候选，当前数据就绪度不足 | 论文相关，但本轮看到的官方仓库只有 LICENSE；不同 CSC 消融不能自动继承相同正确性标签。[S18] |
| **MediEval** | 受权限和任务协议约束的扩展 | 四象限患者上下文/知识推理有价值，但需核验 MIMIC/UMLS 访问及正式评价，不混成 MCQ drop。[S19] |
| **ECG-Expert-QA、GenMedicalEval 的 CF 部分** | 保留文献，不进当前主集合 | 尚未核实可用纯文本 CF 记录和标签语义；不能仅根据栏目名纳入。[S20] |
| **肿瘤 CSS 反事实** | 暂缓 | 长上下文、访问和编辑有效性问题；论文自身报告某类较高不一致性。[S21] |
| **MedRGB / BioRAB 证据污染** | 相邻鲁棒性扩展，本轮不跑 | 错误文档抵抗与遵从假设世界不具有相同正确行为；不能为凑 CF 数量合并 |
| **ReMedQA** | 非 CF 的接口/格式控制 | 格式扰动不等于临床反事实；可用少量历史数据验证 baseline 合同，不计入五项 |
| **CLadder rung-3 / CounterBench** | 一般因果扩展，本轮不跑 | 可测试形式 CF，但医学语料不一定有帮助；加入主表会引入领域与任务双重混杂。[S22] |

#### 5. Taxonomy：最终采用什么，以及怎样修订

##### 5.1 第一层：任务约定，决定怎样解释分数

| 组别 | 受控变化 | 要求模型做什么 | 首轮数据 |
|---|---|---|---|
| **C：临床条件更新** | 症状、检查、病史、患者条件等 | 按新病例重算诊断或规则适用性；是否换答案以实际标签为准 | MedEinst、MedPIC |
| **I：答案不变性** | 经原任务定义为非决定性的信息 | 不让这些变化引入错误更新 | CPV、Cultural-Cues |
| **W：假设证据世界** | 题目和证据中的干预实体被替换 | 按原任务区分证据结论、认知冲突与现实合理性 | MedCounterFact |

这层是评估协议分层，不是“所有 CF 的普适理论分类”。W 不与 C/I 合成一个总准确率或总下降排行榜。

##### 5.2 第二层：实际变化操作，允许跨 benchmark 复用

| 操作标签 | 判定内容 | 不允许的偷换 |
|---|---|---|
| `presence_polarity` | 同一临床概念的有/无、肯定/明确否定 | “没有提到”不等于“明确没有” |
| `measurement_threshold` | 数值、分级或阈值两侧条件改变 | 不凭结果推定一定触发规则 |
| `temporal_history` | 发病顺序、持续时间、既往治疗或检查状态改变 | 普通未来预测不自动成为 CF |
| `clinical_evidence_substitution` | 一项症状/检查证据被另一项替换 | 不能因文本相近就声称只改一个临床变量 |
| `identity_attribute` | 身份、代词、族群等变化 | 在 C 组可为临床相关因素，在 I 组才按任务约定不变 |
| `contextual_addition` | 增加情境线索；Cultural-Cues 有官方 Id/Context/组合 | 涉及实质新病史时不能继续称纯身份替换 |
| `hypothetical_entity_replacement` | 给定证据的实体替换 | 不等同于患者接受真实干预后的结局 |
| `mixed_or_unresolved` | 多种变化并存，或无法可靠判定 | 不为了表格完整强分到单一类 |

标签优先使用作者的明确元数据；病例差异提取和必要的自动判别只服务离线标注，不输入 baseline。一个样本可有多个标签；单标签可比分析与 mixed 组分别报告。

##### 5.3 第三层：描述标签，不当作平级类别

- **临床目标**：diagnosis、medication eligibility/safety、evidence comparison。
- **答案关系**：`change / invariant / relation_transport / unknown`；来自官方配对与语义标签，不把答案字母是否变化作为依据。
- **变化幅度**：single-concept / linked-multiple / broad / unresolved。文本长度差是另外的数值特征。
- **来源与协议**：原始题库、构造方式、输出类型、原生/派生版本、配对可靠性。

诊断发生变化是目标结果；minimal 是幅度；temporal 是操作；它们不能并列成互斥类别。

##### 5.4 设计修订与剩余风险

| 被检验的设计 | 主要问题 | 本方案的修订 |
|---|---|---|
| 按数据集名称或医学专科分组 | 不能证明 CF 类型的作用 | 使用跨集可复用操作标签，另存任务/专科 |
| 用一张互斥长列表涵盖所有概念 | 输入、输出、幅度混杂；许多样本同时落多类 | 任务约定、操作、目标/幅度分轴 |
| 按 accuracy drop 聚类后命名类型 | 分类与验证循环论证 | 先按文本及官方结构标注，冻结后再看输出 |
| 直接拟合 dataset+type 的回归 | type 与 dataset 完全共线时系数不可识别 | 先检查交叉覆盖与设计矩阵；不可识别就报告，不强行估计 |
| 以“不显著不同”说明同类相似 | 低功效也会得不显著 | 预先定义等价范围，做等价性/区间分析；否则只说未能区分 |

剩余风险仍然存在：严格临床 benchmark 少；有些类别只有一个来源；自动标签可能误判；参考标签本身可有噪声。它们不再阻止**筛查**，但阻止首轮直接宣称“普适 taxonomy 已证实”。优先补 MamaBench，是为了增加独立诊断来源，不是为了把数字变成六。

#### 6. 首轮明确的样本和运行范围

本轮是 exploration/screening，不以 sampled benchmark 冒充全量结果。原则：按原始病例/问题抽取，保留该单元所有预先规定的变体；不按模型错题或掉点幅度取样。

| 资源 | 首轮规模 | 预计独立输入数 | 用途 |
|---|---:|---:|---|
| MedEinst | 300 个完整 test pairs；支持时从未用部分固定抽样 | 600 | 原生单病例诊断主筛查 |
| MedEinst 四选项敏感性 | 优先在上述 300 中选已有冻结选项的 60 对；不足则用额外已曝光病例，单独记数 | 120 个额外输入 | 仅区分输出形式影响；不计作另一个 benchmark |
| MedPIC | 完整 467 行 | 467 | 完整 GF/CF 组比较；配对另核实 |
| MedCounterFact | 80 原始问题及每题已发布替换；不足则全部合格原始问题 | 约 400，按实际展开核算 | evidence-world 独立表 |
| CPV-MedQA | 60 个原始病例组，全部规定变体及可恢复原题 | 约 660–960，实际核算 | 身份变化不变性 screening |
| Cultural-Cues | 完整 150 个原题组 | 1,650，含原题与 Neutral | 身份/情境/组合的组内主比较 |

预计约 3,900–4,300 次 M2 输入任务（含可能的额外原生格式对照）；这不是模型调用次数，因为 M2 含多个阶段。完全相同的原题输入可复用，所以实际可能更少。另留少量重复输入噪声对照和非计分 smoke；**具体预算要用当前服务器实测每类吞吐，不使用 MA-RAG 的旧速度外推本轮。**

首轮不自动执行：全量 MedEinst、CPV 全量、多轮 MA-RAG、所有 optional benchmark、全部方法消融、多个模型或三种子全量。负结果不会触发自动扩展或改 prompt。

若预检显示范围超过一个 24 小时运行批次，可在看 screening 正确率前，按预先声明的紧缩档统一减为 MedEinst 200 对、CPV 40 组、MedCounterFact 60 原题，仍保留完整小 benchmark；报告必须称为紧缩 screening，而不是默默少跑。不得根据中途表现调整样本。

#### 7. Baseline 选择与公平性

##### 7.1 使用哪个版本

从当前 checkout 中定位最近仍然保留的 **all-Llama 原始检索→KGCC→KADS→reader 的基线路径**，以历史 `medrgag_proxy / medrgag_mcq_proxy / M2` 为线索。复用当前可工作的实现，停用后加专家；不要通过回滚恢复旧的 parser、指标和 gold 隔离错误。[H1–H2]

正式名称建议：

> **MedRGAG-Llama local reproduction，原生任务合同适配版。**

不能称为“原论文精确 SOTA 复现”，因为原论文部分辅助模块使用 GPT-4o-mini，而这里采用本地 Llama。[S01–S03]

##### 7.2 必须保留 / 必须关闭

| 必须保留 | 本轮关闭 |
|---|---|
| 同一 Llama-3.1-8B-Instruct checkpoint/tokenizer/精度 | MA-RAG、Qwen sidecar |
| 已有 source-balanced retrieval、BM25、MedCPT | DDXPlus Profile expert、CPG、自生成 CF edits |
| KGCC 的摘要、知识缺口探索、补充生成 | CFShift、CF-KADS、ECR-lite、delta query |
| 原始 KADS 选择与最终 reader | Fusion、RiskRoute、residual gate、verifier/corrector |
| 当前固定候选数、文档数、温度和生成长度配置 | 额外全选项似然、多排列集成、投票 |
| 原生题目必须提供的患者信息、题内证据 | NICE、transition cards、oracle、旧 WM 路径 |

官方实现可作为结构核对：多源检索、生成补充文档、联合选择、最终作答。但官方参数和当前本地实现的差异需要记录，不要一边筛查一边偷偷切换配置。[S02–S03]

##### 7.3 为什么需要两个便宜的额外对照

- **M0 Direct**：同一 Llama，只看该题要求的输入。MedCounterFact 的题内证据不是“外部增强”，必须保留。
- **M1 Retrieval-only**：同一初始检索和重排结果、同一 reader；不执行 KGCC/KADS。
- **M2 MedRGAG-base**：完整基础主干。

M1 复用 M2 初始检索，不重新检索另一套语料。这两个对照只是额外 reader 调用，不是两套完整的大型框架。

##### 7.4 原生任务与 MCQ 方法的不可回避冲突

无法同时做到“原生开放诊断完全不改”和“原来只接受 MCQ 的 reader 合同一个字不改”。合理方案是保留方法内部流程，允许**最小任务输入/输出适配**，并公开说明。[S03–S07]

- MedEinst 主筛查：只给当前病例，要求一个明确诊断；不能发送会被复制的 `concise diagnosis` 占位模板。主评分为冻结 canonical/来源支持 alias 的确定性规范化匹配，同时保留 raw exact 和无法归一化的比例。不能随意把不同临床亚型并为同一答案。没有可靠官方语义 evaluator 时，不冒充官方开放诊断分数。
- 四选项 60 对是输出空间敏感性，不是用较高 MCQ 分数替代原生结果；其选项构造受 gold 和 DDXPlus 血缘影响，明确标记 derived，不与原论文 SOTA 比。
- MedPIC：真正的多选集合生成与 exact-set；不要用四个独立 Yes/No 概率阈值替代原 reader。
- CPV/Cultural：保留原始所有选项与顺序；不强行截为四个。
- MedCounterFact：保留被替换的 question+article_summaries；输出比较关系/明确不确定。不要把原始 metadata 的 treatment 或 canonical question 回填到替换题。

整个 M0/M1/M2 在同一任务内使用相同的输入、答案空间、格式约定与确定性解析。

#### 8. 推理协议：让比较真的只反映输入变化

每个原始/反事实输入 **独立作答**，无共享会话记忆，无上个答案，无另一病例，无 gold delta，无类别提示。pair 只在离线分析时合并。

因此“revision”在本轮指两次独立预测对病例变化的正确响应，不表示模型在一个多轮对话中明确撤回旧答案。不要偷换成记忆或信念更新实验。

必需的题内观察/证据不能被 KADS 当作可选外文档丢掉。长输入采用预先冻结的统一上下文预算；记录截断位置和是否损失任务事实。对超预算题报告不兼容或单列，不能默认“保留前半段”后把缺信息造成的失败当 reasoning 缺陷。

同一 prompt 的重复输入可能产生随机差异。额外固定 20 个输入，各执行一次不同预定 seed 的完整复测，不走预测缓存；用于估计采样噪声。它不是三种子全量实验，也不用于挑最优 seed。

#### 9. 核心指标：统一可比部分，保留不可比部分

##### 9.1 真正配对的正确性变化

对 source unit i 的 reference 与 variant，定义正确性 C0_i、C1_i∈{0,1}。统计：

- n11：两次均正确；n10：原来正确、变体错误；
- n01：原来错误、变体正确；n00：两次均错误。

**Drop = A_reference − A_variant = (n10 − n01)/N。** 正值表示下降，所有表统一这个符号。

同时报告四格，避免“没有平均下降”掩盖大量互相抵消的错误变化。

##### 9.2 答案应变化的对

- Variant accuracy。
- Both-correct pair accuracy = n11/N。
- Conditional correct revision = n11/(n11+n10)，限定语义 gold 确实不同的 pairs。
- Old-answer persistence：原题答对且变体输出旧 gold 的数量 / 原题答对的数量；与 MedEinst 官方 BTR 对齐，并报告分母。
- Changed-but-wrong：变体确实换答案但没有换对，不当成功。

##### 9.3 答案应保持的对

- Correct preservation = n11/(n11+n10)。
- Harmful flip = n10/(n11+n10)。
- Semantic flip = 预测语义发生变化的比例。
- Stable-but-wrong：两次同样错误，不能当作良好稳健性。

同一公式因任务约定不同而对应不同临床含义；不是给全库一个含糊的“consistency”。零分母报告 NA，不填 0%。

##### 9.4 多变体数据

先在每个源题内按预定义变体/类别平均，再对源题平均；同时提供原始逐条件分数。原题只需推理一次，但统计仍保留不同对照关系。不要让变体多的患者在总体统计里获得更多隐含权重。

CPV 原题若无法可靠恢复，只做组内不变性，reference drop 标为不可用，不用 White/Male 替代“正常患者”。

##### 9.5 无可靠配对的数据

MedPIC 报 exact-set、micro/macro option F1、集合大小、GF/CF 与官方 operation slices。GF−CF 可以展示，但名称为 **非配对构成差**，不能混进配对 drop 总体估计。只有取得官方验证映射后才计算 pair metrics。

##### 9.6 MedCounterFact

EA/evidence-conditioned relation accuracy、输出不确定率、输出分布，按四类替换分开。安全/荒谬性识别仅在有合法标签或独立可靠评估时评分，否则保留定性输出而不自造 gold。**EA 高不代表临床安全高；EA 下降不必然等于临床能力下降。**

##### 9.7 MedRGAG 是否额外放大变化敏感性

对于同一配对单元：

**Amplification = Drop_M2 − Drop_M0。**

再比较 M1。若三者都下降，首先是共同任务困难；若 M2 的额外下降稳定更大，才提示完整检索–生成–选择流程的附加敏感性。它仍不能单独确定是 KGCC hallucination 还是 KADS 的责任。

M2 相对 M0 的 wrong→correct 与 correct→wrong 另记为方法间 repairs/harms，不能与 reference→variant 的变化四格混用。检查 `(R−H)/N = Acc_M2−Acc_M0`。

#### 10. 如何验证 taxonomy，而不是事后画漂亮图

##### 10.1 五个研究问题的证据要求

| 研究问题 | 首轮可以怎样回答 | 不能做什么 |
|---|---|---|
| M2 是否普遍下降？ | 各可配对 benchmark 的 drop 与区间；分 C/I/W 报告 | 把 MedPIC 非配对差和 MCF EA 合成一条“普遍下降” |
| benchmark 之间是否不同？ | 按任务/原生协议分别比较效应与失败谱 | 用原始 accuracy 排名直接解释 CF 难度 |
| 同类跨集是否相似？ | 在共同操作、任务和足够来源覆盖下比较；CPV/Cultural 为同源构造复制 | 将单一 benchmark 内成千上万变体当跨来源重复 |
| 不同类型是否系统不同？ | 优先同一原题的交叉对照，如 Cultural 的 Id、Context、组合、中性 | 让 dataset 与 type 完全绑定后宣称独立类型效应 |
| taxonomy 是否有意义？ | 类型是否增加超出来源/格式的解释、是否在留出来源上保留方向 | 将无显著差异解释成“证实同类相同” |

##### 10.2 统计实施

- 主要效应做 2,000 次 source-cluster bootstrap；原题全部变体一起重采样。跨 CPV/Cultural 的同源题尽可能统一源题键。
- 两条件成对正确性可用 McNemar；预先限定主要比较，提供 Holm 校正。多标签探索其余结果标记 exploratory。
- 同类“足够相似”预设 ±5 个百分点作探索性等价范围，报告两单侧检验或等价 90% CI；区间太宽就是证据不足，不是相同。
- 可比子域内比较仅有 dataset/source/format/长度的模型与加入 operation 的模型；先检查 design matrix、实际变异与类别覆盖。
- 若 type 完全嵌套在 dataset，输出 `NOT_IDENTIFIABLE`。正则化、随机效应和增加样本不能凭空产生缺失的交叉对照。
- 留一 benchmark/source 验证仅用于训练与测试均有相应类别、且评价语义一致的子域；不适用时报告原因。
- 300 对的配对估计通常不足以确认几百分点的等价；例如 discordant probability≈0.3 时，零附近 drop 的近似 95% 半宽约 6.2pp。这是设计示例，不是预计效果。

本轮最强的 taxonomy 检验机会是 **同一 Cultural-Cues 原题的操作交叉**。严格临床 C 组的“跨来源诊断更新规律”还需要 MamaBench 或另一个可用独立来源。

#### 11. 要记录什么，才能解释错误

保存原始响应、解析答案、各阶段原始文档/生成文档/最终选择、查询、模型和 prompt 配置、输入/输出 token、阶段时间、无效与截断状态。不得只存最后 accuracy。

低成本分析可以计算：reference/variant 文档重叠、新增信息关键词覆盖、检索分数变化、生成文档比例、错误转移。它们只是机制线索。

**相同检索文档不必然失败**：同一篇鉴别诊断文档可能同时覆盖两种情况。仅凭相似度或 LLM 自评不能声称“正确证据缺失”或“生成内容不真实”。若后续需要因果归因，再单独做固定证据、充分证据或模块干预实验，不在首轮自动展开。

#### 12. 运行成本怎样控制，而不偷偷改 baseline

允许的优化：移除本轮不需要的专家调用；常驻 Llama 服务；跨病例批处理；重排微批；检索与其他病例生成重叠；相同原题精确复用；重复评估离线计算；在显存允许时测试独立服务副本。

不允许的“加速”：删除 KGCC/KADS；减少基线规定文档/生成候选/轮次；换小模型或量化后仍使用同一基线名；缩短生成上限截掉推理；只对已知难题调用模块；跳过慢题；语义缓存把仅差否定词的病例合并；把选项似然/多排列集成当作原 reader。

vLLM 的 prefix caching 主要减少重复前缀 prefill，不能省掉实际生成 token；并发上限与 token batch 应由吞吐、排队和 KV 抢占一起判断，而不是看 GPU 利用率。[S24–S25]

历史 4h39 是 full sidecar，里面基线相关阶段约 1h43，但该阶段还包含 M0/M2 与输入展开，**不能直接推断一个原生 benchmark 的准确用时**。[H2]

将 24 小时作为执行批次预算而不是保证。先用代表性输入实测各类型成本，列出 M2 任务数、LLM 调用数、预期 token 和余量。若超过预算，在看到正式结果前采用事先声明的紧缩档。执行中保留完整未完成清单，不能把运行不完整伪装成全量。

#### 13. 图表由研究问题决定

此时不生成结果图。执行完成后，仅生成数据支持的以下图表：

1. **配对 drop + 95% CI 图**：只放可配对、同语义的指标；MedPIC 和 MedCounterFact 独立 panel/file，不做误导的共同排序。
2. **四格错误转移 / correct revision 与 harmful flip 图**：回答“不会更新”还是“乱更新”，同时显示分母。
3. **类别×benchmark 覆盖及失败谱图**：空单元标 NA，不补 0；显示哪些分类结论有交叉证据。
4. **Cultural Id/Context/组合相对 Original 与 Neutral 的对比图**：这是有明确组内因子设计的类型检验。
5. **M0/M1/M2 敏感性差异图**与 **吞吐/成本表**：分别定位 RAG 附加效应和效率。
6. **实际执行流程图**：标清数据协议分流、三个方法、独立推理与离线配对。未执行的 optional 支路不画成完成状态。

不需要雷达图、强行全库总分或没有来源的临床危害图。若某图缺少数据，报告为何不生成。

#### 14. 研究推进与结果判读

| 阶段 | 交付 | 继续条件的含义 |
|---|---|---|
| 资料与当前代码核对 | 来源/配置差异、数据可用性与调用链 | 只排除无效接口，不因没掉点停止 |
| taxonomy 与样本冻结 | 标签规则、交叉覆盖、来源关系、采样清单 | 不看模型结果分组 |
| 小规模合同与性能测试 | 每集真实样本、各方法输入输出、token/吞吐 | 系统性格式错先修；不搞极端 fail-closed |
| 首轮 screening | 五入口的三方法预测、阶段记录、完整性计数 | 固定计划执行；负结果完整保留 |
| 离线分析 | 指标、CI、可识别性、图表与失败模式 | 决定后续收窄范围而非自动加模块 |
| 后续研究设计 | 选择一个可重复、可修复机制；确定独立确认集 | 本轮不实现新方法 |

结果没有下降，是对原始假设有信息的结果；不同 benchmark 下降不同但类型不能解释，也有研究价值。只有当类型与错误模式的联系跨来源复现，才能逐步升级 taxonomy 主张。若只在同一个 MedQA 衍生家族中成立，应明确写成同源构造下的结果。

#### 15. 相关方法在本轮的角色

ECR-Agent、EA-RAG、CF-RAG、CPG、CoRFu 仍是后续优化的最近邻候选，但不进入首轮推理矩阵。现在就把它们全接回去，会把“基础失效是什么”与“哪个插件涨点”重新混为一谈。

分类是实验组织与可检验假设，不必硬包装成独立理论贡献。首轮完成后才能决定：做临床更新方法、研究无关变化敏感性，还是聚焦证据世界冲突。这不是提前放弃方法，而是避免重复过去“先搭复杂模块，后发现任务与指标没对齐”的路径。[H1–H2]

#### 16. 来源索引

以下是本方案使用的关键原始来源，而非“全部论文已穷尽”的声明。访问核验日期为 2026-09-06；文件下载后的 revision 和行数由执行报告补记。

- **S01** MedRGAG paper: https://arxiv.org/html/2510.18297v1
- **S02** MedRGAG official main: https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py
- **S03** MedRGAG official implementation: https://github.com/ll0ruc/MedRGAG/blob/master/src/medrgag.py
- **S04** MedEinst paper: https://aclanthology.org/2026.acl-long.1847/ ; https://arxiv.org/html/2601.06636v1
- **S05** MedEinst data and BTR definition: https://huggingface.co/datasets/zhui711/MedEinst
- **S06** MedPIC paper: https://arxiv.org/html/2608.03028v1
- **S07** MedPIC data: https://huggingface.co/datasets/TIM0927/MedPIC-Bench
- **S08** CPV paper: https://aclanthology.org/2025.naacl-long.114/ ; code: https://github.com/kenza-ily/diagnose_treat_bias_llm
- **S09** CPV-MedQA data: https://huggingface.co/datasets/kenza-ily/medqa-cpv
- **S10** Cultural-Cues paper: https://arxiv.org/html/2601.20102v1
- **S11** Cultural-Cues official repo: https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs ; inputs: `Data/final_augment_test_questions.json`, `Data/test.jsonl`
- **S12** MedCounterFact paper: https://arxiv.org/html/2601.11886v1
- **S13** MedCounterFact official data: https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence ; field specification: https://raw.githubusercontent.com/KaijieMo-kj/Counterfactual-Medical-Evidence/main/DataFormat.md
- **S14** MamaBench: https://arxiv.org/html/2607.14385v2 ; gated data: https://huggingface.co/datasets/HelpMum-Personal/MamaBench/tree/main
- **S15** Laboratory causal reasoning: https://www.nature.com/articles/s41746-026-02632-3 ; https://github.com/balubhasuran/LLM_Causality_LabTest
- **S16** CLIR: https://arxiv.org/html/2607.09880v1 ; https://huggingface.co/datasets/winall/CLIR-Bench
- **S17** FairMedQA / AMQA: https://arxiv.org/html/2505.19562v2 ; https://github.com/XY-Showing/AMQA ; actual records: https://huggingface.co/datasets/Showing-KCL/AMQA
- **S18** MedEqualQA: https://aclanthology.org/2025.sciprodllm-1.4/ ; https://github.com/rajarshi51382/MEDEQUALQA
- **S19** MediEval: https://aclanthology.org/2026.acl-long.734/
- **S20** ECG-Expert-QA: https://arxiv.org/html/2502.17475v2 ; GenMedicalEval: https://github.com/MediaBrain-SJTU/GenMedicalEval
- **S21** Oncology counterfactual sensitivity: https://arxiv.org/html/2605.30590v1
- **S22** CLadder: https://github.com/causalNLP/cladder
- **S23** Behavioral testing / contrast sets: https://aclanthology.org/2020.acl-main.442/ ; https://aclanthology.org/2020.findings-emnlp.117/
- **S24** vLLM 0.8.5 performance: https://docs.vllm.ai/en/v0.8.5/performance/optimization.html
- **S25** vLLM prefix caching: https://docs.vllm.ai/en/v0.8.5/features/automatic_prefix_caching.html

**没有执行的事情：**本轮没有修改用户服务器，没有跑任何新 LLM benchmark，没有重新拟合模型，也没有生成带假结果的图。详细执行规范见同目录 `CODEX_PROMPT.md`。

<a id="record-0282"></a>

## acquisition.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/acquisition.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/acquisition.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### Acquisition

Exact-input reuse: CPV has 665 released/reference records but 570 unique visible tasks. Cultural has 1,500 records but 1,499 unique visible tasks: source group `cultural:90`, `t3_i`, is an exact visible-input no-op relative to its Original. That author-labeled Id condition remains in the declared main analysis and shares the exact-input prediction; it is not removed or relabeled using model outcomes.

- medeinst: [zhui711/MedEinst](https://huggingface.co/datasets/zhui711/MedEinst), revision `354f4b527e764a8f2bebea8f71be55e0a6966402`; source files in acquisition.json.
- medpic: [TIM0927/MedPIC-Bench](https://huggingface.co/datasets/TIM0927/MedPIC-Bench), revision `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983`; source files in acquisition.json.
- cpv: [kenza-ily/medqa-cpv](https://huggingface.co/datasets/kenza-ily/medqa-cpv), revision `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5`; source files in acquisition.json.
- medcounterfact: [KaijieMo-kj/Counterfactual-Medical-Evidence](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence), revision `f35b98063b51a63e677829b6d173029d98dd3b1e`; source files in acquisition.json.
- cultural: [HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs), revision `5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f`; source files in acquisition.json.

Released rows: MedEinst 10766; MedPIC 467; CPV 12310 in 1202 groups; Cultural 150 groups × 10 = 1500 inputs; MedCounterFact 203 original + 809 replaced. Cultural Neutral is absent. Four existing caches match current remote revisions checked 2026-09-06.

CPV authentic question field is verified against author create.py (case_text and question both initialized from original MedQA question). Variants use case_text alone. Cultural originals all match author test.jsonl by complete normalized question, exact options and gold. No published model answers downloaded.

MedPIC official pair map unavailable: GF–CF is unpaired_composition_gap. MedCounterFact aligns only metadata.id; original metadata.question and treatment fields never enter model inputs. Public author releases without repository license remain local; only download code, IDs and derived aggregate outputs are committed.

Cultural slots follow the paper’s C1/C2/C3 order: t1 Indigenous Canadian, t2 Middle-Eastern Muslim, t3 Southeast Asian. Id, Context, and Id+Context retain the author operations. See https://arxiv.org/html/2601.20102v1 . The source file contains no Neutral field despite its presence in paper tables.

<a id="record-0283"></a>

## baseline_contract.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/baseline_contract.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/baseline_contract.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### medrgag_llama_base: local reproduction contract

Starting repository HEAD: `1e01b3a33c378041c64a76cce70ed381e4280d35`, current branch main. Existing uncommitted documentation edits and archived AGENTS changes are retained separately. Research authority: `/home/data3/txy/RESEARCH_PLAN.md`, copied alongside this report. The current conversation defines scope.

Formal workers started at 2026-09-06 08:56:18 CST with the new working-tree implementation. Its first checkpoint commit is `a3881eb138451f0e3dc9b8e1c10b3faea85d7c37` (09:03:04 CST). Subsequent changes add offline analyses/exports, resume shortcuts and the explicitly documented supplementary repeat RNG correction; the primary prompts, input file, decoding budgets and request seeds are unchanged.

The latest reusable baseline is `run_cfshift.py::run_baseline` → `run_gate_b.py::run_m2`; no sidecar function is needed. This is the actual recent CF baseline, distinct from the older v15 guided sentence-label summary experiment. The new runner reuses its prompt builders, parsers, Llama backend, sparse retrieval and MedCPT ranking; only task I/O, scheduling, provenance and resume are adapted.

| Stage | Actual file/function | Model | Decoding / configuration | Input → output |
|---|---|---|---|---|
| Initial retrieval | `run_gate_b.LocalRetriever`, `src/medrgag_retrieval.DualBM25Retriever.retrieve` | BM25 | 32 hits independently per source | question + native options → 64 candidates |
| Initial reranking | `src/medrgag_retrieval.MedCPTRanker.rank` | ncbi MedCPT Cross Encoder | FP32, pair max_length 512, descending logits, stable ties | 64 candidates → 5 external documents |
| KGCC summary | `src/medrgag_logic.build_summary_prompt`, screening `Runner.llm` | Llama | T=0, top_p=1, max=64; 5 calls | current independent task + each document → useful information |
| KGCC exploration | `build_explore_prompt`, `parse_knowledge_points` | Llama | T=0, max=1024; 1 call | task + summaries → 3 missing knowledge points |
| Complementary generation | `build_generation_slots`, `clean_generated_text` | Llama | T=1.2, top_p=.9, top_k=50, presence_penalty=1, max=256; 5 calls | 3 knowledge-conditioned + 2 question-only slots → 5 documents |
| Original KADS | `build_selection_prompt`, `run_gate_b.selection_ids` | Llama | T=0, max=2048; 1 call | 5 retrieved + 5 generated passages → up to 5 selected IDs |
| Final reranking | `MedCPTRanker.rank` | same MedCPT | same tokenization/scoring/order | selected documents → up to 5 reader documents |
| Reader M0/M1/M2 | screening `reader_prompt`, original JSON answer reader contract and `parse_answer` | same Llama | T=0, top_p=1, max=64; one independent request per method | same native task + 0 / 5 initial / up to 5 selected external documents → raw JSON answer |

Llama checkpoint and tokenizer: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`; BF16, tensor parallel=1, eager vLLM 0.8.5. No quantization, likelihood scoring, voting or permutation ensemble. The local checkpoint has no separately verifiable remote revision; configuration files and local checkpoint location are recorded, rather than inventing a revision. The installed tokenizer chat template is archived in each worker cache. MedCPT: `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder`.

Corpus/index: `/home/data3/txy/MedRGAG/corpus/{textbooks,wikipedia}/index/bm25`; existing corpus resolvers use those source directories. Neither PubMed nor historical MA-RAG MedCorp3 is substituted. BM25's configured source balance is before cross-encoder reranking; the final top five are not forced source-balanced.

Actual vLLM startup uses the V1 engine, with prefix caching and chunked prefill enabled by the installed defaults, KV cache dtype auto (BF16 model), no speculative decoding, and no CUDA graph capture because eager mode is retained. These are verified in both formal worker startup logs. Engine-internal prefix hit counters are unavailable in the saved per-request API metrics; reported stage-cache hits must not be interpreted as prefix-cache hit rates.

Task changes are frozen before formal predictions: native diagnoses request exactly one actual diagnosis; multi-select keeps all option keys and exact-set scoring; evidence comparison adds explicit uncertainty. Mandatory MedCounterFact article_summaries are retained in every task-aware stage and every reader, outside KADS's external-document candidates. External retrieval is enabled for that dataset, correcting the old fixed-only pilot path. No metadata.question, metadata treatment labels, gold, pair text, edit label or previous answer enters the solver. For open tasks only, MCQ-specific auxiliary wording is replaced with medical-question wording; actual complete prompts are stored in compressed local archives.

Preflight found 11 mandatory tasks beyond the old 32768 context window, maximum approximately 48747 tokens. Capacity is therefore 65536 for all methods; completion budgets stay unchanged. Complete prompts are checked; overflow is recorded as a technical failure, never silently truncated. This preserves task content and is an explicit capacity adaptation, not the old 32K experiment.

The historical generator seed was unset. This run uses preassigned, role-independent seeds from opaque input ID, stage and slot, plus master seed 20260906. Repeated-input noise experiment uses master seed+1; no best-seed selection. Temperatures and output budgets remain the recent baseline's values. Exact source text/options/evidence/format deduplication shares predictions only for identical visible tasks. Resume requires equal frozen config and unchanged prepared input list.

Differences from published mixed-model MedRGAG: all auxiliary roles use Llama instead of hosted GPT; local prompt/JSON parser adaptations and short reader budget follow the recent local CF baseline; this does not use the earlier v15 constrained summary labels. Official code was checked as provenance, not used to overwrite local decoding. Official references: https://github.com/ll0ruc/MedRGAG and https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py.

Excluded call paths: Profile/DDXPlus scoring, CFShift, CPG, CF-KADS, ECR, RiskRoute, residual fusion, MA-RAG, Qwen, NICE/WM, teacher/judge. Only `run_gate_b` is imported from historical runners; `run_cfmoe.py` and `run_cfshift.py` are not imported or run. A completed independent input requires 15 LLM requests: M0+M1+5 summaries+1 explorer+5 generators+1 selector+M2. Logs permit checking that count and include source IDs, tokens, raw responses and full prompts. No format repair (zero extra attempts). Network acquisition has at most 3 attempts; model/backend failures exit with a durable error and resume from completed stages.

Runtime drift discovered at smoke: shared Transformers was 5.16.1, incompatible with vLLM 0.8.5 (`all_special_tokens_extended`). This task uses a local PYTHONPATH overlay pinned to project-recorded Transformers 4.53.2, tokenizers 0.21.4, huggingface-hub 0.30.2; shared model packages are not downgraded. Auxiliary pyarrow and matplotlib were added for native Parquet reading and requested figures.

KADS task-format clarification before formal inference: its original template repeats question text twice. Mandatory article_summaries appear fully in the second question instance only; the first retains the complete top-level question. This avoids duplicating up to 48K tokens of evidence without discarding any article or changing candidate budgets. Five affected smoke select/reader results were recomputed; old attempts remain in cache/smoke_pre_evidence_dedup.

Exposure correction retained the frozen 300-pair primary sample: 299 have no narrative match in the 163 scanned historical assets, one (`case_13504`) was previously used but has a malformed official heading (`Sym.`), initially missed by a heading-dependent scanner. The corrected full-text scanner labels it exposed; there is no pristine-test claim and no outcome-based resampling.

Repeat RNG audit: the original master-seed+1 formula overlapped neighboring generation-slot streams; notably, repeat question-only slot 3 shared both prompt and seed with primary slot 4. Primary inference is unchanged. The fixed 20-input repeat now adds a constant 1,000,000,000 stream offset, verified disjoint from all 18,870 primary generation seeds, and writes to `cache/repeat_independent`. The first repeat stays intact in `cache/repeat` and is reported as superseded correlated-stream noise/cost, not as an independent replicate. See `rng_repeat_correction.json`. No seed or item was chosen using accuracy, and neither repeat is ensembled into the primary answers.

<a id="record-0284"></a>

## data_checks.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/data_checks.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/data_checks.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### Five source-unit checks per benchmark

Full prepared-set audit: normalization preserves internal punctuation and numeric operators; zero within-item option-text collisions and zero collisions among the 46 canonical diagnosis labels were found. All six recorded CPV/Cultural source-overlap pairs also match with punctuation retained (NFKC, case and whitespace only). The historical question-suffix matcher was made tolerant of the already-trimmed terminal question mark: rescanning the same 163 frozen files still finds 3,550 previously exposed official test cases, with zero changes to this run's exposure labels or sample IDs.
Inference receives only item_id, question, options, fixed_evidence, answer_format. No gold/group/role/taxonomy enters solver.
Full prepared inputs stay local and are not redistributed.

#### medeinst:case_17052
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000000: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1379/0.
- s000001: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=1387/0.

#### medeinst:case_123636
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000002: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1193/0.
- s000003: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=1293/0.

#### medeinst:case_56300
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000004: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1196/0.
- s000005: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=890/0.

#### medeinst:case_24586
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000006: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=859/0.
- s000007: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=912/0.

#### medeinst:case_45856
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000008: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1240/0.
- s000009: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=980/0.

#### medpic:SS-HF-HFREF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000838: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=348/0.

#### medpic:SS-HF-HFPEF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000839: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=330/0.

#### medpic:SS-HF-NOHF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000840: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=388/0.

#### medpic:SS-HF-HFREF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000841: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=402/0.

#### medpic:SS-HF-HFPEF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000842: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=353/0.

#### cpv:medqa_00813
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001305: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=675/0.
- s001306: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=685/0.

#### cpv:medqa_01076
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001316: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=780/0.
- s001317: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=790/0.

#### cpv:medqa_00448
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001327: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=1582/0.
- s001328: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=1592/0.

#### cpv:medqa_00585
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001338: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=727/0.
- s001339: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=737/0.

#### cpv:medqa_01242
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001349: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=514/0.
- s001350: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=524/0.

#### medcounterfact:131
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003374: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=167/45462.
- s003375: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=142/45897.

#### medcounterfact:37
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003379: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=216/1397.
- s003380: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=174/1327.

#### medcounterfact:152
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003384: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=111/4843.
- s003385: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=93/4661.

#### medcounterfact:108
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003389: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=121/37104.
- s003390: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=106/36700.

#### medcounterfact:119
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003394: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=133/60800.
- s003395: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=130/60369.

#### cultural:0
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001875: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=947/0.
- s001876: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=984/0.

#### cultural:1
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001885: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=773/0.
- s001886: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=820/0.

#### cultural:2
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001895: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=738/0.
- s001896: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=796/0.

#### cultural:3
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001905: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=477/0.
- s001906: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=515/0.

#### cultural:4
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001915: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=404/0.
- s001916: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=448/0.

Potential ambiguities: MedPIC has no official pair map; MedEinst multi-edit taxonomy remains unresolved; CPV no-op and sex-specific clinical text are flagged; Cultural Neutral absent and options can exceed four; MedCounterFact original metadata text never fills replacement input.
Raw source checks and complete prompts are retained locally; do not paste license-unclear text into Git.

<a id="record-0285"></a>

## findings.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/findings.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/findings.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### 五入口 baseline screening：结果解读与验收

**Scope clarification: completed sampled screening only, not the entire test sets. Full-release expansion is tracked in [results_cf_full_test](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0292).**

本轮完整档已完成。结果支持“不同来源/任务格式下表现不同”，不支持“MedRGAG 普遍放大反事实敏感性”；独立跨来源 taxonomy 效应不可识别。以下结论限定于本地 all-Llama reproduction、冻结样本和当前解析合同，不能推广为论文原模型的精确复现或临床安全评价。

#### 实际完成范围

| 入口/协议 | source groups | 输入记录 | 完成率 | M0 | M1 | M2 |
|---|---:|---:|---:|---:|---:|---:|
| MedEinst 原生主样本 | 300 对 | 600 | 100% | 10.83% | 9.00% | 7.67% |
| MedPIC 原生多选 | 467 | 467 | 100% | 35.97% | 36.83% | 30.84% |
| CPV 原生单选 | 60 | 665 | 100% | 57.58% | 59.85% | 55.30% |
| Cultural 原生单选 | 150 | 1500 | 100% | 62.53% | 61.53% | 66.13% |
| MedCounterFact 证据关系 | 80 | 400 | 100% | 67.25% | 63.75% | 66.75% |
| MedEinst 冻结四选项辅助 | 60 对 | 120 | 100% | 46.67% | 43.33% | 55.00% |

表中按源题先平均；CPV 的 micro 分数另为 57.14%/59.40%/54.89%。MedEinst 是 canonical-match screening；MedPIC 是 exact-set；MedCounterFact 是 EA，不能与诊断 accuracy 平均，也不代表临床安全。四选项辅助另补 59 对的原生结果（118 输入），与主样本重合的 1 对只运行一次。总共 3,870 条评价记录、3,774 个唯一可见输入、11,322 个方法预测。

五入口均取得作者公开数据并固定 revision；全部采样在正式效果检查前冻结，没有采用紧缩档。Cultural 的真实发布是 150×10=1,500 条，没有 Neutral，不能宣称完成 1,650 条设计。MedPIC 无可核验官方 pair map，未构造所谓 89 对。CPV 使用作者原始 question 恢复 reference，变体使用完整 case_text，未把两个患者问题拼接。MedCounterFact 80 组均有四种替换，保留四 MainCategory 和全部题内证据。原始公开文本只留本地；Cultural/MedCounterFact 未发现明确仓库再分发许可，不提交原文。

MedEinst 扫描 163 份历史资产，找到 3,550 个官方 test 病例的完整叙述匹配；主样本为 299 个未匹配病例和 1 个已曝光病例，不能称 pristine。CPV/Cultural 有 6 个完整原题文本匹配、原生选项集合不同的来源重叠组，已做保守聚类和去重叠敏感性。数据规模、revision、五条 source-unit 自检及已知歧义见 acquisition.md、data_checks.md、benchmark_summary.csv。

#### 真实基线及执行证据

复用 `run_cfshift.py::run_baseline` 所指向的 `run_gate_b.py::run_m2` 基础主干符号及外部 MedRGAG prompt/parser；没有运行 CFShift 本身。Llama-3.1-8B-Instruct BF16、同 checkpoint/tokenizer、vLLM 0.8.5；全部辅助 LLM 阶段均用 Llama。Textbooks/Wikipedia 各 BM25 32 候选，经 FP32 MedCPT 取 5 文档；5 个 KGCC 摘要→3 个知识点→5 个补充文档→原 KADS 从 10 候选选最多 5 个→MedCPT→原本地 JSON reader。

KGCC/reader 为温度 0；补充生成温度 1.2、top_p 0.9、top_k 50；摘要/知识探索/生成/KADS/reader 上限为 64/1024/256/2048/64 token。为完整保留最长题内证据，容量由历史 32K 扩为 65,536；实际最长 prompt 51,307 token，无输入裁剪或 overflow。开放诊断、多选、证据比较只做任务 I/O 适配。与官方混合模型、早期 v15 约束标签输出不同，正式命名 `medrgag_llama_base`，完整调用表和 prompt 见 baseline_contract.md 及本地持久化缓存。

56,610 个主 LLM 请求严格对应每输入 15 次：3 reader、5 summary、1 explore、5 generate、1 select。各输入都执行了 KGCC/KADS；无额外专家或 judge 调用。31 条并发预取重叠检索结果完全一致，成本保留。其他用户的 GPU 进程未终止。

#### 下降、稳定与方法差异

| M2 原题→变体 | 配对数/源组 | drop，95% source-cluster CI |
|---|---:|---|
| MedEinst 原生 | 300/300 | +6.67 pp [2.67, 10.67] |
| CPV | 605/60 | −2.17 pp [−10.67, 5.83] |
| Cultural | 1350/150 | −0.15 pp [−5.56, 5.11] |
| MedCounterFact EA | 320/80 | −0.62 pp [−7.19, 5.94] |

MedEinst 的 M0 drop 为 6.33 pp，M2−M0 drop amplification 仅 +0.33 pp [−3.67, 4.34]。另外三个配对入口的 M2 amplification 也都跨零。因此，没有证据证明 M2 比 Direct 更普遍地放大编辑敏感性；区间跨零也不能证明等价。跨来源 ±5pp 等价检验因缺乏相容来源覆盖 unavailable。

方法整体得分差异与原题→变体变化是不同问题。MedPIC M2−M0 为 −5.14 pp [−8.99, −1.50]，M2−M1 为 −6.00 pp [−10.06, −2.14]；M2 相对 Direct 修复 29 题、引入 53 错，条件伤害率 53/168=31.55%。MedEinst 原生 M2−M0 为 −3.17 pp [−5.33, −1.00]。CPV、Cultural、MedCounterFact 的 M2−M0 区间均跨零，Cultural 点估计为 +3.60 pp。MedPIC 三方法均有 GF 高于 CF 的未配对构成差：16.92/17.43/14.76 pp；没有 pair map，不能称原题被编辑后下降。

MedEinst M2 四格为 n11/n10/n01/n00=1/32/12/255；reference 正确仅 33/300，variant 正确 13/300。旧答案坚持为 15/33=45.45%，不能把其余错误都叫“不更新”。大量低分及 floor effect 与规范化合同共同限制解释。Cultural M2 有 138 个正确→错误和 140 个错误→正确，整体均值接近不变掩盖了双向变化。CPV 相应为 49/62，MedCounterFact 为 22/24。完整 correct revision/preservation、semantic flip、changed/stable wrong 和 invalid 记录见 transitions.csv。

#### 输出合同、格式敏感性与阶段限制

MedEinst 主样本 M0/M1/M2 未映射诊断为 323/462/432，占 53.83%/77.00%/72.00%；M2 另有 3 个歧义诊断。未映射不等于医学语义错误，未增加结果驱动的别名，也未调用医学 judge。其余原生格式非法数：CPV 0/0/0，Cultural 9/3/1，MedPIC 10/1/4，MedCounterFact 0/0/0。MedCounterFact uncertainty 为 0/7/1，单列于拒绝及格式非法。

相同冻结 60 对内，四选项相对原生的 M2 reference/variant 增益为 +38.33/+56.67 pp，95% CI 分别 [25.00,51.67]/[45.00,68.33]。辅助四选项 M2 drop 为 −10 pp [−30,10]，不能替代 300 对原生结论；其选项构造和辅助样本来源都影响难度。

原 KADS/parser 的最终文档数分布为：5 篇 3375，4 篇 33，3 篇 10，2 篇 7，1 篇 5，0 篇 344。零篇占 9.12%；抽查包含生成了选档叙述但不符合原解析标记的响应。它们是必须披露的本地基线阶段格式失败，不能把其结果解释成理想 KADS 的纯检索效应。没有事后修改解析器、补文档、换答案或重跑挑种子。所有请求仍完成知识生成和最终 reader；MedCounterFact 题内证据始终保留。

原预算下 summary/generate/select 达 token 上限分别为 8877/18870、14152/18870、219/3774；最终 M0/M1/M2 为 9/0/1。保留这些自然截断，不缩短预算以加速。20 条固定独立随机流复测中，19 个有效语义比较有 7 次变化，原始输出变化 10/20；样本很小，只估计本实现随机性，不扣除噪声或择优。原 master+1 复测存在跨槽位种子重叠，已透明保留并另计成本，最终独立复测使用固定流偏移，详见 rng_repeat_correction.json。

#### Taxonomy 与可支持的范围

MedEinst 的临床信息更新及 MedPIC 临床规则条件题最接近窄临床 CF；CPV/Cultural 是患者身份/情境变换下的答案保持任务；MedCounterFact 是假设证据世界。三者评价语义不能混合。MedEinst 复合编辑保守标为 mixed_or_unresolved，没有为制造掉点重分组。

clinical_update 与 evidence-world 设计矩阵秩不足；answer_invariance 在两个 MedQA 构造内满秩，但只有一个原始来源家族。identity 虽跨 CPV/Cultural，仍只是同源构造重复。所有独立跨来源 taxonomy 结论为 NOT_IDENTIFIABLE。保留同源描述性回归、组内比较及 2,000 次 cluster bootstrap；没有以正则化、删除 source 控制或把 reference 正误当无噪声难度来强行识别。MedPIC 静态 GF 行标签的规则修正及敏感性完整保留，不改样本或预测。

#### 成本与下一步

正式批次 2026-09-06 08:56:18–13:28:14 CST，共 16,316 秒（4 小时 31 分 56 秒），GPU0/GPU2 两副本，GPU1 预取耗时 4,592.89 秒。复测利用释放后的 GPU2 与最后一个主分片短暂重叠，13:32:32 完成；从正式启动到全部推理结束 4 小时 36 分 14 秒。前置 smoke/兼容性准备独立记录于 performance_test.json，不冒充正式批次吞吐。

主任务 56,610 请求、97,047,730 prompt token、11,521,838 completion token。含两次复测及废弃 smoke 的实际总计 57,140 请求、99,197,477 prompt token、11,649,160 completion token。精确去重 96 输入节省 1,440 次主 LLM 调用；复用审核后的 25 条 smoke 全阶段，历史答案缓存使用为零。prompt token 是逻辑计数，含前缀缓存，不能当作实际重算 prefill 数。vLLM V1 前缀缓存/分块预填充默认开启，但未暴露本次 prefix hit/queue 统计，留 NA。没有 transport 失败或格式 repair。最大耗时阶段为 KADS；完整 stage wall sum 与重叠批次 makespan 分开报告。

唯一建议的后续机制检验：原 KADS 输出与解析格式失配导致的证据丢失，是否解释同一题上的 M2−M1 变化。当前 344 个空选档及双向预测变化足以提出这个问题，尚不能证明因果；本轮不实施解析修复实验、新方法或额外 judge。

代码、统计、SVG/PNG 图和 Mermaid 源码均已落盘。复现入口为 `bash scripts/cf_baseline_screening.sh prepare|run|analyze`（分别执行）。工作从当前本地 HEAD `1e01b3a` 开始，首个代码/协议提交 `a3881eb` 在正式启动之后的 09:03:04 创建；最终提交号由 Git 历史及交付回复记录。没有推送，用户原有未提交修改保持原状。

<a id="record-0286"></a>

## smoke_review.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/smoke_review.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/smoke_review.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### Smoke acceptance

25 independent inputs, five per dataset, all three methods; 375 current LLM requests. Reviewed all 75 raw reader responses and sampled complete saved prompts. No gold, paired-case body, dataset operation or reference/trap role is available to solver_input. All options retained (MedPIC multi-select arrays; Cultural five-option example); open diagnosis returns actual diseases rather than a placeholder. Mandatory evidence is retained in M0/M1/M2 and external retrieval/KGCC/KADS executed.

MedEinst outputs include diagnoses outside the canonical list; these remain unmapped in conservative screening, not repaired with gold or post-hoc medical aliases. This is scoring coverage, not a JSON placeholder failure.

One native CPV source group and one Cultural source group are included only partially in the five-input smoke; full groups are scheduled for formal completion. The five MedCounterFact inputs cover a complete original+four-variant source group with about 11K mandatory tokens each. Separate 20-input second-seed M2 run uses frozen random IDs; its raw answers have not been used for sample or tier selection.

Tests: tests/test_cf_baseline_screening.py, two tests pass (visible-field filtering, mandatory evidence, full options, task parsing, contradictory answers, stable independent seeds, metric identities). Input preflight: 3774 items; max mandatory reader 48747 tokens; 0 overflows at 65536 capacity. Full KADS includes only one copy of mandatory evidence to prevent duplication overflow.

Later algebraic seed audit found cross-slot overlap between the first repeat and primary run, including one identical question-only prompt/seed per item. Its 361.45-second timing remains a valid full-pipeline throughput probe. Its noise estimate is superseded by the same frozen 20 inputs with a disjoint repeat stream; both outputs and costs remain available. See `rng_repeat_correction.json`; primary seeds and predictions are unchanged.

Runtime compatibility failures and replaced smoke select/reader artifacts are retained locally under cache. No transport error is treated as a model wrong answer.

<a id="record-0287"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening`。

### Cross-benchmark all-Llama baseline screening

**Scope clarification: completed sampled screening only, not the entire test sets. Full-release expansion is tracked in [results_cf_full_test](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0292).**

Status: **complete**; unique method predictions 11322/11322.

Local baseline and exact stage contract: [baseline_contract.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0283). Public source revisions and release discrepancies: [acquisition.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0282).

#### Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M0 | 665 | 57.58% | [45.00%, 70.00%] | 57.14% | 0 | 60/60 |
| cpv | M1 | 665 | 59.85% | [47.88%, 71.67%] | 59.40% | 0 | 60/60 |
| cpv | M2 | 665 | 55.30% | [45.45%, 65.31%] | 54.89% | 0 | 60/60 |
| cultural | M0 | 1500 | 62.53% | [55.67%, 69.60%] | 62.53% | 9 | 150/150 |
| cultural | M1 | 1500 | 61.53% | [54.73%, 68.60%] | 61.53% | 3 | 150/150 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M0 | 400 | 67.25% | [57.50%, 76.50%] | 67.25% | 0 | 80/80 |
| medcounterfact | M1 | 400 | 63.75% | [54.25%, 73.00%] | 63.75% | 0 | 80/80 |
| medcounterfact | M2 | 400 | 66.75% | [57.49%, 75.50%] | 66.75% | 0 | 80/80 |
| medeinst | M0 | 600 | 10.83% | [8.66%, 13.17%] | 10.83% | 323 | 300/300 |
| medeinst | M1 | 600 | 9.00% | [7.00%, 11.33%] | 9.00% | 462 | 300/300 |
| medeinst | M2 | 600 | 7.67% | [5.83%, 10.00%] | 7.67% | 435 | 300/300 |
| medpic | M0 | 467 | 35.97% | [31.69%, 40.26%] | 35.97% | 10 | 467/467 |
| medpic | M1 | 467 | 36.83% | [32.55%, 41.11%] | 36.83% | 1 | 467/467 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

#### Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M0 | 605/60 | -1.00 pp | [-4.00, 1.00] pp | NA / 0 |
| cpv/native | M1 | 605/60 | 2.00 pp | [-2.33, 7.33] pp | NA / 0 |
| cpv/native | M2 | 605/60 | -2.17 pp | [-10.67, 5.83] pp | NA / 0 |
| cultural/native | M0 | 1350/150 | 2.37 pp | [-0.81, 5.41] pp | NA / 0 |
| cultural/native | M1 | 1350/150 | -0.22 pp | [-4.07, 3.78] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M0 | 320/80 | 1.88 pp | [-2.50, 6.56] pp | NA / 0 |
| medcounterfact/native | M1 | 320/80 | 1.56 pp | [-5.62, 8.76] pp | NA / 0 |
| medcounterfact/native | M2 | 320/80 | -0.62 pp | [-7.19, 5.94] pp | NA / 0 |
| medeinst/derived_four_way | M0 | 60/60 | 0.00 pp | [-20.00, 20.04] pp | 64.29% / 28 |
| medeinst/derived_four_way | M1 | 60/60 | -10.00 pp | [-30.00, 10.00] pp | 60.87% / 23 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-30.00, 10.00] pp | 43.33% / 30 |
| medeinst/native | M0 | 300/300 | 6.33 pp | [1.33, 11.67] pp | 85.71% / 42 |
| medeinst/native | M1 | 300/300 | 4.00 pp | [-0.67, 8.67] pp | 51.52% / 33 |
| medeinst/native | M2 | 300/300 | 6.67 pp | [2.67, 10.67] pp | 45.45% / 33 |

#### Changes relative to Direct and retrieval-only
| Benchmark/protocol | Comparison | Source groups | Source-mean score gain | 95% CI | Introduced errors / items | Conditional harm |
|---|---|---:|---:|---|---:|---:|
| cpv/native | M1-M0 | 60 | 2.27% | [-6.36, 10.91] pp | 45/665 | 11.84% |
| cpv/native | M2-M0 | 60 | -2.27% | [-10.45, 5.61] pp | 68/665 | 17.89% |
| cpv/native | M2-M1 | 60 | -4.55% | [-14.09, 4.85] pp | 100/665 | 25.32% |
| cultural/native | M1-M0 | 150 | -1.00% | [-6.13, 3.87] pp | 135/1500 | 14.39% |
| cultural/native | M2-M0 | 150 | 3.60% | [-0.60, 7.80] pp | 118/1500 | 12.58% |
| cultural/native | M2-M1 | 150 | 4.60% | [-0.00, 9.27] pp | 140/1500 | 15.17% |
| medcounterfact/native | M1-M0 | 80 | -3.50% | [-7.00, -0.25] pp | 24/400 | 8.92% |
| medcounterfact/native | M2-M0 | 80 | -0.50% | [-3.75, 2.75] pp | 14/400 | 5.20% |
| medcounterfact/native | M2-M1 | 80 | 3.00% | [-0.75, 6.50] pp | 14/400 | 5.49% |
| medeinst/derived_four_way | M1-M0 | 60 | -3.33% | [-11.67, 4.17] pp | 13/120 | 23.21% |
| medeinst/derived_four_way | M2-M0 | 60 | 8.33% | [0.83, 15.83] pp | 7/120 | 12.50% |
| medeinst/derived_four_way | M2-M1 | 60 | 11.67% | [3.33, 21.67] pp | 9/120 | 17.31% |
| medeinst/native | M1-M0 | 300 | -1.83% | [-4.33, 0.50] pp | 34/600 | 52.31% |
| medeinst/native | M2-M0 | 300 | -3.17% | [-5.33, -1.00] pp | 31/600 | 47.69% |
| medeinst/native | M2-M1 | 300 | -1.33% | [-3.50, 0.83] pp | 27/600 | 50.00% |
| medpic/native | M1-M0 | 467 | 0.86% | [-1.71, 3.64] pp | 20/467 | 11.90% |
| medpic/native | M2-M0 | 467 | -5.14% | [-8.99, -1.50] pp | 53/467 | 31.55% |
| medpic/native | M2-M1 | 467 | -6.00% | [-10.06, -2.14] pp | 56/467 | 32.56% |

Gain intervals use source means. Introduced-error and conditional-harm columns retain their specified item-level denominators; for M2−M1, the comparator is M1. Positive paired amplification means greater reference-to-variant sensitivity than Direct; it is not a causal finding.

| Benchmark/protocol | Method | Drop amplification vs Direct | 95% CI |
|---|---|---:|---|
| cpv/native | M1 | 3.00 pp | [-2.00, 8.67] pp |
| cpv/native | M2 | -1.17 pp | [-9.17, 6.50] pp |
| cultural/native | M1 | -2.59 pp | [-6.96, 2.00] pp |
| cultural/native | M2 | -2.52 pp | [-8.37, 3.19] pp |
| medcounterfact/native | M1 | -0.31 pp | [-6.88, 5.94] pp |
| medcounterfact/native | M2 | -2.50 pp | [-8.44, 3.44] pp |
| medeinst/derived_four_way | M1 | -10.00 pp | [-23.33, 5.00] pp |
| medeinst/derived_four_way | M2 | -10.00 pp | [-26.67, 6.67] pp |
| medeinst/native | M1 | -2.33 pp | [-7.33, 3.00] pp |
| medeinst/native | M2 | 0.33 pp | [-3.67, 4.34] pp |

| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |
|---|---:|---:|---|
| M0 | 284/183 | 16.92 pp | [8.52, 25.68] pp |
| M1 | 284/183 | 17.43 pp | [9.15, 26.19] pp |
| M2 | 284/183 | 14.76 pp | [6.63, 22.90] pp |

MedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.

#### Interpretation and limits
The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.

Errors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.

Native/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.

#### Cost and next research decision
Recorded main-run LLM requests (including frozen sensitivity inputs): 56610; prompt tokens: 97047730; completion tokens: 11521838. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches cause evidence loss that explains M2−M1 changes within the same source question. Current empty-selection/document-count records motivate this question but do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 99197477 logical prompt tokens and 11649160 completion tokens. Exact visible-input deduplication removes 96 duplicate tasks and avoids 1440 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

#### Execution and parsing details
Formal concurrent batch elapsed: 4.53 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 57140. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M0 | 0 | 0 | 0 | 0 |
| cpv | M1 | 0 | 0 | 0 | 0 |
| cpv | M2 | 0 | 0 | 0 | 0 |
| cultural | M0 | 9 | 0 | 0 | 0 |
| cultural | M1 | 3 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M0 | 0 | 0 | 0 | 0 |
| medcounterfact | M1 | 0 | 0 | 0 | 7 |
| medcounterfact | M2 | 0 | 0 | 0 | 1 |
| medeinst | M0 | 0 | 323 | 0 | 0 |
| medeinst | M1 | 0 | 462 | 0 | 0 |
| medeinst | M2 | 3 | 432 | 3 | 0 |
| medpic | M0 | 10 | 0 | 0 | 0 |
| medpic | M1 | 1 | 0 | 0 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

#### Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M0 | reference | 60 | 31.67% | [20.00, 43.37] pp |
| M0 | variant | 60 | 38.33% | [25.00, 51.67] pp |
| M1 | reference | 60 | 33.33% | [21.67, 45.00] pp |
| M1 | variant | 60 | 43.33% | [28.33, 56.67] pp |
| M2 | reference | 60 | 38.33% | [25.00, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 344, 1: 5, 2: 7, 3: 10, 4: 33, 5: 3375}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0285), [validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_screening/validation.json).

<a id="record-0288"></a>

## RESEARCH_PLAN.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/RESEARCH_PLAN.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/RESEARCH_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

正文与[已合入记录](#record-0281)相同，统一在该处维护。

<a id="record-0289"></a>

## acquisition.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/acquisition.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/acquisition.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

### Acquisition

- medeinst: [zhui711/MedEinst](https://huggingface.co/datasets/zhui711/MedEinst), revision `354f4b527e764a8f2bebea8f71be55e0a6966402`; source files in acquisition.json.
- medpic: [TIM0927/MedPIC-Bench](https://huggingface.co/datasets/TIM0927/MedPIC-Bench), revision `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983`; source files in acquisition.json.
- cpv: [kenza-ily/medqa-cpv](https://huggingface.co/datasets/kenza-ily/medqa-cpv), revision `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5`; source files in acquisition.json.
- medcounterfact: [KaijieMo-kj/Counterfactual-Medical-Evidence](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence), revision `f35b98063b51a63e677829b6d173029d98dd3b1e`; source files in acquisition.json.
- cultural: [HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs), revision `5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f`; source files in acquisition.json.

Released rows: MedEinst 10766; MedPIC 467; CPV 12310 in 1202 groups; Cultural 150 groups × 10 = 1500 inputs; MedCounterFact 203 original + 809 replaced. Cultural Neutral is absent. Four existing caches match current remote revisions checked 2026-09-06.

CPV authentic question field is verified against author create.py (case_text and question both initialized from original MedQA question). Variants use case_text alone. Cultural originals all match author test.jsonl by complete normalized question, exact options and gold. No published model answers downloaded.

MedPIC official pair map unavailable: GF–CF is unpaired_composition_gap. MedCounterFact aligns only metadata.id; original metadata.question and treatment fields never enter model inputs. Public author releases without repository license remain local; only download code, IDs and derived aggregate outputs are committed.

Full-test scope clarification: Cultural final_augment_test_questions.json is the entire author-released counterfactual benchmark (150 source groups, 1500 actual conditions). The accompanying test.jsonl contains 1273 underlying MedQA originals and is used for source mapping; its unaugmented remaining questions are not additional Cultural-Cues CF examples. Similarly, CPV coverage is all 12310 released variants in 1202 groups plus their authentic originals, not unrelated MedQA source-pool questions. No agent subsampling is applied to either released benchmark.

<a id="record-0290"></a>

## baseline_contract.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/baseline_contract.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/baseline_contract.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

#### Current required method scope

User explicitly narrowed remaining full-test inference to **M2 only**. Existing M0/M1 outputs (5832 each) and all their costs are preserved as historical auxiliary records; they are not required complete-test comparisons. See method_scope.json. The historical three-method contract below explains already executed work.

### medrgag_llama_base: complete released test-set expansion

Expansion starts from repository `bc31166fcbca514138ae5db38ab4a73a4b2f3312`, launched 2026-09-06 13:44:17 CST. Scope: all official MedEinst test rows and all released evaluation rows/groups of the other four resources. Prior sampled screening is retained in `../results_cf_screening`. Its provenance below is historical.

The expansion uses `config.json`: context capacity 98,304, required by the full release’s 62,682-token mandatory task plus unchanged KADS context. This changes capacity only; checkpoint, BF16, templates, token budgets, candidate/document counts and seeds stay fixed. The 3,774 earlier inputs keep identical IDs/text and cached stages produced at capacity 65,536; see cache_reuse.json. At initial expansion startup, GPU0 used .50 memory allocation after one pre-request failure at .45, and GPU2 used .45. Both subsequently resumed at .75 as documented below. No model request was produced by the failed startup.

Starting repository HEAD: `1e01b3a33c378041c64a76cce70ed381e4280d35`, current branch main. Existing uncommitted documentation edits and archived AGENTS changes are retained separately. Research authority: `/home/data3/txy/RESEARCH_PLAN.md`, copied alongside this report. The current conversation defines scope.

Formal workers started at 2026-09-06 08:56:18 CST with the new working-tree implementation. Its first checkpoint commit is `a3881eb138451f0e3dc9b8e1c10b3faea85d7c37` (09:03:04 CST). Subsequent changes add offline analyses/exports, resume shortcuts and the explicitly documented supplementary repeat RNG correction; the primary prompts, input file, decoding budgets and request seeds are unchanged.

The latest reusable baseline is `run_cfshift.py::run_baseline` → `run_gate_b.py::run_m2`; no sidecar function is needed. This is the actual recent CF baseline, distinct from the older v15 guided sentence-label summary experiment. The new runner reuses its prompt builders, parsers, Llama backend, sparse retrieval and MedCPT ranking; only task I/O, scheduling, provenance and resume are adapted.

| Stage | Actual file/function | Model | Decoding / configuration | Input → output |
|---|---|---|---|---|
| Initial retrieval | `run_gate_b.LocalRetriever`, `src/medrgag_retrieval.DualBM25Retriever.retrieve` | BM25 | 32 hits independently per source | question + native options → 64 candidates |
| Initial reranking | `src/medrgag_retrieval.MedCPTRanker.rank` | ncbi MedCPT Cross Encoder | FP32, pair max_length 512, descending logits, stable ties | 64 candidates → 5 external documents |
| KGCC summary | `src/medrgag_logic.build_summary_prompt`, screening `Runner.llm` | Llama | T=0, top_p=1, max=64; 5 calls | current independent task + each document → useful information |
| KGCC exploration | `build_explore_prompt`, `parse_knowledge_points` | Llama | T=0, max=1024; 1 call | task + summaries → 3 missing knowledge points |
| Complementary generation | `build_generation_slots`, `clean_generated_text` | Llama | T=1.2, top_p=.9, top_k=50, presence_penalty=1, max=256; 5 calls | 3 knowledge-conditioned + 2 question-only slots → 5 documents |
| Original KADS | `build_selection_prompt`, `run_gate_b.selection_ids` | Llama | T=0, max=2048; 1 call | 5 retrieved + 5 generated passages → up to 5 selected IDs |
| Final reranking | `MedCPTRanker.rank` | same MedCPT | same tokenization/scoring/order | selected documents → up to 5 reader documents |
| Reader M0/M1/M2 | screening `reader_prompt`, original JSON answer reader contract and `parse_answer` | same Llama | T=0, top_p=1, max=64; one independent request per method | same native task + 0 / 5 initial / up to 5 selected external documents → raw JSON answer |

Llama checkpoint and tokenizer: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`; BF16, tensor parallel=1, eager vLLM 0.8.5. No quantization, likelihood scoring, voting or permutation ensemble. The local checkpoint has no separately verifiable remote revision; configuration files and local checkpoint location are recorded, rather than inventing a revision. The installed tokenizer chat template is archived in each worker cache. MedCPT: `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder`.

Corpus/index: `/home/data3/txy/MedRGAG/corpus/{textbooks,wikipedia}/index/bm25`; existing corpus resolvers use those source directories. Neither PubMed nor historical MA-RAG MedCorp3 is substituted. BM25's configured source balance is before cross-encoder reranking; the final top five are not forced source-balanced.

Actual vLLM startup uses the V1 engine, with prefix caching and chunked prefill enabled by the installed defaults, KV cache dtype auto (BF16 model), no speculative decoding, and no CUDA graph capture because eager mode is retained. These are verified in both formal worker startup logs. Engine-internal prefix hit counters are unavailable in the saved per-request API metrics; reported stage-cache hits must not be interpreted as prefix-cache hit rates.

Task changes are frozen before formal predictions: native diagnoses request exactly one actual diagnosis; multi-select keeps all option keys and exact-set scoring; evidence comparison adds explicit uncertainty. Mandatory MedCounterFact article_summaries are retained in every task-aware stage and every reader, outside KADS's external-document candidates. External retrieval is enabled for that dataset, correcting the old fixed-only pilot path. No metadata.question, metadata treatment labels, gold, pair text, edit label or previous answer enters the solver. For open tasks only, MCQ-specific auxiliary wording is replaced with medical-question wording; actual complete prompts are stored in compressed local archives.

Preflight found 11 mandatory tasks beyond the old 32768 context window, maximum approximately 48747 tokens. Capacity is therefore 65536 for all methods; completion budgets stay unchanged. Complete prompts are checked; overflow is recorded as a technical failure, never silently truncated. This preserves task content and is an explicit capacity adaptation, not the old 32K experiment.

The historical generator seed was unset. This run uses preassigned, role-independent seeds from opaque input ID, stage and slot, plus master seed 20260906. Repeated-input noise experiment uses master seed+1; no best-seed selection. Temperatures and output budgets remain the recent baseline's values. Exact source text/options/evidence/format deduplication shares predictions only for identical visible tasks. Resume requires equal frozen config and unchanged prepared input list.

Differences from published mixed-model MedRGAG: all auxiliary roles use Llama instead of hosted GPT; local prompt/JSON parser adaptations and short reader budget follow the recent local CF baseline; this does not use the earlier v15 constrained summary labels. Official code was checked as provenance, not used to overwrite local decoding. Official references: https://github.com/ll0ruc/MedRGAG and https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py.

Excluded call paths: Profile/DDXPlus scoring, CFShift, CPG, CF-KADS, ECR, RiskRoute, residual fusion, MA-RAG, Qwen, NICE/WM, teacher/judge. Only `run_gate_b` is imported from historical runners; `run_cfmoe.py` and `run_cfshift.py` are not imported or run. A completed independent input requires 15 LLM requests: M0+M1+5 summaries+1 explorer+5 generators+1 selector+M2. Logs permit checking that count and include source IDs, tokens, raw responses and full prompts. No format repair (zero extra attempts). Network acquisition has at most 3 attempts; model/backend failures exit with a durable error and resume from completed stages.

Runtime drift discovered at smoke: shared Transformers was 5.16.1, incompatible with vLLM 0.8.5 (`all_special_tokens_extended`). This task uses a local PYTHONPATH overlay pinned to project-recorded Transformers 4.53.2, tokenizers 0.21.4, huggingface-hub 0.30.2; shared model packages are not downgraded. Auxiliary pyarrow and matplotlib were added for native Parquet reading and requested figures.

KADS task-format clarification before formal inference: its original template repeats question text twice. Mandatory article_summaries appear fully in the second question instance only; the first retains the complete top-level question. This avoids duplicating up to 48K tokens of evidence without discarding any article or changing candidate budgets. Five affected smoke select/reader results were recomputed; old attempts remain in cache/smoke_pre_evidence_dedup.

Exposure correction retained the frozen 300-pair primary sample: 299 have no narrative match in the 163 scanned historical assets, one (`case_13504`) was previously used but has a malformed official heading (`Sym.`), initially missed by a heading-dependent scanner. The corrected full-text scanner labels it exposed; there is no pristine-test claim and no outcome-based resampling.

Repeat RNG audit: the original master-seed+1 formula overlapped neighboring generation-slot streams; notably, repeat question-only slot 3 shared both prompt and seed with primary slot 4. Primary inference is unchanged. The fixed 20-input repeat now adds a constant 1,000,000,000 stream offset, verified disjoint from all 18,870 primary generation seeds, and writes to `cache/repeat_independent`. The first repeat stays intact in `cache/repeat` and is reported as superseded correlated-stream noise/cost, not as an independent replicate. See `rng_repeat_correction.json`. No seed or item was chosen using accuracy, and neither repeat is ensembled into the primary answers.


Full-test capacity restart at 2026-09-06T16:41:08.698383+08:00: the two task-owned engines were restarted once at `gpu_memory_utilization=0.75` to use free memory for KV cache (GPU0 348720, GPU2 360480 tokens). Model, BF16, 98,304-token capacity, prompt/decoder budgets, input IDs and seeds are unchanged. All durable stages were reused. Unreturned tokens from at most one batch per engine are unavailable; see `capacity_restart.json`. Other user processes and the concurrent retrieval worker continued.

Length scheduling: both retrieval and inference sort all frozen items by `(reader_task_tokens, item_id)` before disjoint sharding; batch/chunk64 uses the same stable item/stage/slot seeds and decoder budgets. All inputs are retained. See throughput_restart.json.

<a id="record-0291"></a>

## data_checks.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/data_checks.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/data_checks.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

### Five source-unit checks per benchmark
Inference receives only item_id, question, options, fixed_evidence, answer_format. No gold/group/role/taxonomy enters solver.
Full prepared inputs stay local and are not redistributed.

#### medeinst:case_69476
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s003774: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=935/0.
- s003775: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=938/0.

#### medeinst:case_35528
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s003776: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=805/0.
- s003777: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=791/0.

#### medeinst:case_103449
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s003778: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=844/0.
- s003779: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=899/0.

#### medeinst:case_130135
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s003780: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1175/0.
- s003781: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=940/0.

#### medeinst:case_108850
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s003782: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1261/0.
- s003783: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=1308/0.

#### medpic:SS-HF-HFREF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000838: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=348/0.

#### medpic:SS-HF-HFPEF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000839: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=330/0.

#### medpic:SS-HF-NOHF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000840: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=388/0.

#### medpic:SS-HF-HFREF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000841: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=402/0.

#### medpic:SS-HF-HFPEF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000842: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=353/0.

#### cpv:medqa_00674
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=16; mapping=official.
- s013811: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=327/0.
- s013811: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=327/0.

#### cpv:medqa_01036
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s013812: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=478/0.
- s013813: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=488/0.

#### cpv:medqa_01020
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s013823: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=1015/0.
- s013824: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=1025/0.

#### cpv:medqa_01083
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s013834: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=813/0.
- s013834: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=813/0.

#### cpv:medqa_00684
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s013835: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=802/0.
- s013836: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=812/0.

#### medcounterfact:259
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s024668: format=relation; option keys=[]; evidence articles=3; gold type=str; role=reference; input lengths=111/6119.
- s024669: format=relation; option keys=[]; evidence articles=3; gold type=str; role=variant_1; input lengths=90/6160.

#### medcounterfact:95
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003589: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=136/3863.
- s003590: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=128/3833.

#### medcounterfact:164
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003464: format=relation; option keys=[]; evidence articles=3; gold type=str; role=reference; input lengths=153/6788.
- s003465: format=relation; option keys=[]; evidence articles=3; gold type=str; role=variant_1; input lengths=116/6190.

#### medcounterfact:70
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s024673: format=relation; option keys=[]; evidence articles=3; gold type=str; role=reference; input lengths=125/136988.
- s024674: format=relation; option keys=[]; evidence articles=3; gold type=str; role=variant_1; input lengths=118/136771.

#### medcounterfact:91
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003474: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=139/79702.
- s003475: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=123/78871.

#### cultural:0
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001875: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=947/0.
- s001876: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=984/0.

#### cultural:1
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001885: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=773/0.
- s001886: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=820/0.

#### cultural:2
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001895: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=738/0.
- s001896: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=796/0.

#### cultural:3
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001905: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=477/0.
- s001906: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=515/0.

#### cultural:4
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001915: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=404/0.
- s001916: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=448/0.

Potential ambiguities: MedPIC has no official pair map; MedEinst multi-edit taxonomy remains unresolved; CPV no-op and sex-specific clinical text are flagged; Cultural Neutral absent and options can exceed four; MedCounterFact original metadata text never fills replacement input.
Raw source checks and complete prompts are retained locally; do not paste license-unclear text into Git.

Full-release coverage test passed: all 10,766 MedEinst test rows, 467 MedPIC rows, 12,310 CPV variants plus 1,202 authentic references, 1,500 Cultural rows, 203+809 MedCounterFact rows. Exact visible-input duplicates keep every evaluation label. Eleven duplicate inputs have conflicting official gold; flagged in evaluation labels and duplicate_gold_conflicts.json. MedCounterFact IDs 147/43/66 each lack one released category variant; nothing is synthesized. Full source overlap mapping contains 142 CPV/Cultural source links. Prior 20-input repeat and 25-input smoke are retained fixed auxiliary samples, not fresh random full-population samples.

Prespecified full-release sensitivity (2026-09-06 14:05 CST): retain all 11 identical-control/trap, conflicting-gold MedEinst pairs in the primary test; additionally report the same metrics excluding these flagged pairs. Flags were identified in data preparation, independent of predictions; no inference or gold is changed.

<a id="record-0292"></a>

## findings.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/findings.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/findings.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

### MedRGAG-Llama 基础版：五入口完整测试结果

状态：**完成并通过验收**。2026-09-07 05:16:18 CST 推理完成，05:17:09 首次完整分析完成。本轮最终要求只有 M2；共完成 25,280/25,280 个唯一输入，对应 27,377 条评价记录。旧 M0/M1 各 5,832 条仅作为历史辅助记录保留，不构成全测试集对照。

#### 数据范围和完成率

| 入口 / 协议 | 完成源题组 / 计划 | 全部评价记录 | 唯一输入 | 完成率 |
|---|---:|---:|---:|---:|
| MedEinst 官方 test，原生诊断 | 5,383/5,383 | 10,766 | 10,755 | 100% |
| MedPIC，原生多选 | 467/467 行级单元 | 467 | 467 | 100% |
| CPV-MedQA，全部变体及真实原题 | 1,202/1,202 | 13,512 | 11,427 | 100% |
| Cultural-Cues，全部原题及发布变体 | 150/150 | 1,500 | 1,499 | 100% |
| MedCounterFact，原题及全部发布替换 | 203/203 | 1,012 | 1,012 | 100% |
| MedEinst 冻结四选项辅助敏感性 | 60/60 | 120 | 120 | 100% |

五个入口的原生数据均为完整发布范围；最后一行是预定辅助协议，不是第二个 MedEinst benchmark，也不是全 test 的四选项转换。CPV 包含 12,310 个变体和 1,202 个真实原题。Cultural 附带的 1,273 条 MedQA 原题文件用于来源映射，作者实际发布的增强评估集是 150 组。数据 revision、下载路径、字段检查见 [acquisition.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0289)、[data_checks.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0291)；推理输入与标签保持分离。

#### 实际基础调用链

采用本地 `medrgag_llama_base`，不是 exact published SOTA reproduction。复用 `run_cfshift.py::run_baseline` 所指向的 `run_gate_b.py::run_m2` 基础实现及 MedRGAG prompt/retrieval helpers，由 `scripts/run_cf_baseline_screening.py` 调度：

Textbooks/Wikipedia 各 BM25 32 候选 → MedCPT 排序取初始 5 文档 → 5 次 KGCC 摘要 → 3 个缺失知识点 → 5 次补充文档生成 → 原始 KADS 从 10 候选选最多 5 个 → MedCPT 最终排序 → 原始任务适配 JSON reader。

Llama checkpoint/tokenizer：`/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`，BF16，原 chat template。MedCPT：本地 `ncbi-MedCPT-Cross-Encoder`，FP32、pair max_length 512。Llama 上下文容量 98,304；摘要/探索/生成/KADS/reader 上限分别为 64/1,024/256/2,048/64 tokens。生成 T=1.2、top_p=.9、top_k=50、presence_penalty=1；其余阶段 T=0。完整参数与各实际函数在 [baseline_contract.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0290)。与论文混合模型配置的差别是全部生成/reader 均用本地 Llama，并为开放诊断、多选、证据比较作最小 I/O 适配；没有声称远端 checkpoint revision 已核实。

MedCounterFact 顶层问题和完整 article_summaries 在各必要阶段保留，不由 KADS 删除。原题/变体独立推理，输入不含 gold、配对正文、role、taxonomy。没有启动 Profile/DDX、CFShift scorer、CFMoE/sidecar、Qwen、反事实生成方法、gate/adapter、judge、训练或全选项似然评分。缓存记录只包含基础摘要、探索、生成、选择、reader 和检索/排序阶段；M2 的 13 次 LLM 调用预算逐输入验收通过。

#### M2 原生结果

分数按源题组先平均；micro 分数另列。区间为 2,000 次源题组 cluster bootstrap。

| 数据集 | 源题平均分数 | 95% CI | Micro 分数 | 正确评价记录 / N |
|---|---:|---|---:|---:|
| MedEinst canonical match | 8.26% | [7.76%, 8.75%] | 8.26% | 889/10,766 |
| MedPIC exact-set | 30.84% | [26.77%, 34.90%] | 30.84% | 144/467 |
| CPV-MedQA accuracy | 67.09% | [64.89%, 69.35%] | 67.20% | 9,080/13,512 |
| Cultural-Cues accuracy | 66.13% | [60.60%, 71.80%] | 66.13% | 992/1,500 |
| MedCounterFact evidence agreement | 66.50% | [60.59%, 72.12%] | 66.50% | 673/1,012 |

MedEinst raw-exact 为 5.49%，canonical match 为 8.26%。7,749/10,766（71.98%）条诊断未映射到冻结官方标签清单，另有 68 条歧义诊断。未映射不等于 JSON 格式错误，也不能据此断言全部为医学语义错误；此处是确定性规范化匹配 screening，不是作者官方语义 evaluator。未按结果增加同义词或调用 judge。

MedPIC option F1：micro 49.96%，macro 46.77%；平均预测集合大小 1.486，真实集合大小 1.343。GF 为 104/284（36.62%），CF 为 40/183（21.86%），差 14.76 pp，CI [6.63,22.90] pp。这是 **unpaired_composition_gap**，没有恢复或编造官方配对。

MedCounterFact 输出分布：higher 317、lower 376、no difference 304、uncertainty 15；uncertainty 为合法输出，单独计数。EA 不与临床 accuracy 平均，也不解释为临床安全性。

#### 配对变化和错误结构

正 drop 表示原题分数高于变体。多变体先源题内平均，避免变体多的题权重更大。

| 原生数据集 | 配对数 / 源题组 | 原题分数 → 变体分数（源题平均） | Drop | 95% CI |
|---|---:|---|---:|---|
| MedEinst | 5,383/5,383 | 9.16% → 7.36% | +1.80 pp | [0.74,2.86] pp |
| CPV | 12,310/1,202 | 67.39% → 67.06% | +0.33 pp | [-1.34,2.08] pp |
| Cultural | 1,350/150 | 66.00% → 66.15% | -0.15 pp | [-5.56,5.11] pp |
| MedCounterFact EA | 809/203 | 67.00% → 66.38% | +0.62 pp | [-3.33,4.68] pp |

MedEinst 规范化匹配下降的 McNemar p=.000988，预定 native 比较族 Holm 修正后 p=.02864。其余三个整体配对效应区间包含 0；这不证明完全相同或等价，也不支持“所有 benchmark 都下降”。MedPIC 的非配对差不能与上述 drop 混用。M0/M1 未完成全量，按用户最新要求不报告跨方法 amplification 或归因于检索的额外效应。

MedEinst 四格 n11/n10/n01/n00 = 19/474/377/4,513；pair accuracy 19/5,383=0.35%。原题正确的 493 对中，变体正确 19 对，仍输出旧 gold 的 199 对，BTR=199/493=40.37%。这区分了正确换诊断、旧答案持续和其他错误，不能把全部 474 个变体错误都叫作不更新。CPV、Cultural、MedCounterFact 的 raw pair conditional failure 分别为 1,005/8,310=12.09%、138/891=15.49%、57/542=10.52%；完整变化/稳定错误与 invalid 分开保存在 [transitions.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/transitions.csv)。

Cultural 跨文化汇总中，相对 Original 的 Id、Context、Id+Context drop 分别为 +0.89、-2.44、+1.11 pp，各自区间均包含 0；不存在可用 Neutral 条件。文化与官方操作切片在 [category_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/category_metrics.csv)、[paired_effects.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/paired_effects.csv)。

#### 格式和预定敏感性

冻结 60 对四选项辅助结果为 66/120=55.00%，control/trap 为 50.00%/60.00%，drop=-10.00 pp，CI [-28.37,8.33] pp。同一 60 对的原生结果仅 7/60 和 2/60；四选项减原生的差分别为 +38.33 pp（CI [26.67,51.67]）和 +56.67 pp（CI [45.00,68.33]）。这种巨大协议差异限制了 MedEinst 的解释；不能用派生选项结果替代完整原生 test 结论。

MedEinst 历史曝光 3,849 组，历史未匹配到叙述的 1,534 组。两组 canonical 分数为 8.37%/7.99%，配对 drop 分别 +2.13 pp（CI [.91,3.43]）和 +.98 pp（CI [-1.04,2.93]）。未称后者严格 pristine。排除发布集中 11 个“输入完全相同而 gold 不同”的病例后，5,372 组 drop 为 +1.79 pp（CI [.69,2.83]），主分析仍保留全部官方行。

去除 CPV/Cultural 的 142 个跨资源共享来源映射后，CPV 保留 1,060 组、drop +.06 pp（CI [-1.80,1.95]）；Cultural 仅余 8 组，区间很宽，不能作独立来源复现证据。CPV 事前质量标记阴性且组完整的 920 组 drop +.69 pp（CI [-1.35,2.77]）。这些敏感性按预定规则全部报告，不挑选最好结果。

固定 20 个输入的独立 seed 辅助复测完成；19 个双有效输出中语义 flip 7/19，raw response 变化 10/20。该样本继承自早期 screening，不是全 test 的新随机样本，不选最佳 seed、不集成、不从主分数中扣除随机变化。

#### 类型可识别性与结论边界

MedEinst 属于临床更新；MedPIC 为 guideline-following/临床患者信息改变任务，但缺正式 pair map。CPV/Cultural 属于答案应保持的身份/文化变换；MedCounterFact 属于假设证据世界。这三类评价语义不合并成总体 CF accuracy。

完整 coverage 表已冻结并保留。临床更新与假设证据世界的设计矩阵秩不足；身份/文化域在 MedQA 构造内部满秩，但 CPV 和 Cultural 同源，无法验证独立临床来源的类型规律。三域跨独立来源 taxonomy 均为 **NOT_IDENTIFIABLE**。没有删除 dataset 控制、靠正则化强造系数或因掉点重新分组；没有适用的独立跨源 ±5 pp 等价证据，leave-one-source 不可用。细节见 [taxonomy_identifiability.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/taxonomy_identifiability.json)、[explanatory_models.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/explanatory_models.json)。

本轮对“各数据来源的变化模式不同”提供部分描述性支持；不支持“所有数据集显著退化”，不能从当前结果证明 taxonomy、检索因果失败或临床危害。低 MedEinst canonical 分数尤其受开放输出映射协议限制。

#### 成本、监控和验收

完整扩展批次从 2026-09-06 13:44:17 到 2026-09-07 05:16:18，makespan **55,921 秒（15 小时 32 分 01 秒）**，包含并发、受控重启和异常停机，不是 stage wall-time 之和。此前已完成的抽样批次约 4 小时 32 分钟，其 3,774 个完全相同输入/阶段被复用。本轮新增 21,506 个唯一输入；该 15.53 小时是已有缓存的扩展实测，不是从零无缓存的完整重跑耗时。

M2 主干共 328,640 次 LLM 调用；加保留的 M0/M1 11,664 次，共 340,304 次。再计固定复测及已作废 smoke/复测尝试 530 次，总记录 **340,834 次**，logical prompt tokens **449,853,293**，completion tokens **77,488,473**。扩展新增 283,694 次记录调用、350,655,816 prompt tokens、65,839,313 completion tokens。完全相同可见输入去重 2,097 条，按 M2 每题 13 次避免 27,261 次调用；没有跨反事实语义近似复用。

主推理使用 GPU0/2 的 NVIDIA H20（各约 97,871 MiB），检索预取曾使用 GPU1，vLLM 0.8.5，最终 batch/chunk64、GPU memory allocation .75；未停止其他用户进程。候选数/文档数/解码预算未为加速减少。后段把已完成奇数分片之外的 1,061 个输入按现有参数分成 531/530 两组，集合验收互斥且无遗漏。

KADS select 的已记录并发阶段批次时间累计约 55,308 秒，是主要 LLM 时间来源；生成约 27,794 秒，摘要约 21,288 秒，探索约 18,313 秒。它们包含已复用历史工作，不能相加充当本轮 makespan。原始预算到达 token 上限的次数：summary 58,136/126,400，generate 93,488/126,400，explore 73/25,280，select 1,273/25,280，M2 reader 1/25,280。未因此延长或缩短预算。prefix-cache 的 logical token 数不等于物理重算 tokens；本地 vLLM 接口没有返回可用 queue-time 指标。runtime cache-hit 计数仅覆盖各 worker 最新进程记录，历史精确复用另列。

20:31 左右旧任务进程曾退出，Luna 在 21:02 报告，主代理直到用户 21:30 询问才接手，存在监控响应延迟；没有错误地把这段时间记成有效推理。原因未证实，无 Python traceback，内核日志不可读。21:31 从已校验缓存恢复到独立 tmux，此后主代理持续检查 Luna 心跳并处理尾部分配，直到完整结束。受控容量/调度重启及该异常退出期间未返回的 tokens 不可测，已记录 totals 不含它们；不把估计上限当实际成本。原记录见 capacity_restart.json、throughput_restart.json、unexpected_exit_restart.json、tail_rebalance.json。

最后所有 source groups/输入完成，pending transport=0，网络重试=0，format repair=0。原生评价记录中格式/歧义 invalid：MedEinst 68、CPV 6、Cultural 1、MedPIC 4、MedCounterFact 0；MedEinst 未映射 7,749 另列。3 个合同/数据/指标测试通过；全量阶段 key、5/1/5/1/1 调用数、seed/config/token limits、文档缓存一致性、所有 gzip prompt 引用、全表配对恒等式通过。25,349 条检索记录中含 69 条重复缓存记录，重复的排序文档 ID/正文一致；LLM 阶段无重复 key。见 [artifact_audit.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/artifact_audit.json)、[validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/validation.json)。

原始 KADS/parser 最终选文档数：0/1/2/3/4/5 对应 2,561/10/28/37/130/22,514 个输入；10.13% 为空选择，仍执行全部 M2 阶段，没有事后填文档。一个后续值得检验的机制是：原始 KADS 输出/解析失配造成的空证据，是否与同源题的错误换答相关。本轮保存的是 association/proxy，不能证明因果；没有实施新 parser、gate 或方法。

#### 可用性和交付

没有访问受限而跳过的核心入口。Cultural 的 Neutral 未发布；MedPIC 没有可验证官方 pair map；MedCounterFact 的 147/43/66 三个原题各缺一个发布变体类别，这些未发布记录不计模型失败。MedEinst/MedPIC/CPV 许可信息与另外两库未明确许可的情况见 acquisition；原始文本、模型权重、检索库与凭据不提交 Git。

[summary.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0294) 是自动生成摘要；[benchmark_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/benchmark_metrics.csv)、[paired_effects.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/paired_effects.csv)、[statistics.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/statistics.json)、[efficiency.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/efficiency.csv) 为机器可读结果。9 张实际数据图均导出 SVG/PNG，见 figures/；流程图保留 [flow.mmd](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/flow.mmd)，没有下载大型渲染环境。全部准备/运行/分析及审计命令在 [commands.sh](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/commands.sh)，阶段正文通过本地可恢复缓存引用保存。

开始代码 HEAD：`1e01b3a33c378041c64a76cce70ed381e4280d35`；全量扩展起点 `bc31166fcbca514138ae5db38ab4a73a4b2f3312`；完成时执行代码 checkpoint `8630dfc`，其后只修正 M2 计划计数元数据、补充验收和报告。最终交付 commit 由本目录 Git 历史及最终回复记录；未推送远端，用户原有未提交修改保留。

<a id="record-0293"></a>

## smoke_review.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/smoke_review.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/smoke_review.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

正文与[已合入记录](#record-0286)相同，统一在该处维护。

<a id="record-0294"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test`。

### Cross-benchmark all-Llama baseline screening

Status: **complete**; unique method predictions 25280/25280.

Evaluation scope: entire official test/released evaluation data; no source-group sampling.

Local baseline and exact stage contract: [baseline_contract.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0290). Public source revisions and release discrepancies: [acquisition.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0289).

#### Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M2 | 13512 | 67.09% | [64.89%, 69.35%] | 67.20% | 6 | 1202/1202 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M2 | 1012 | 66.50% | [60.59%, 72.12%] | 66.50% | 0 | 203/203 |
| medeinst | M2 | 10766 | 8.26% | [7.76%, 8.75%] | 8.26% | 7817 | 5383/5383 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

#### Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M2 | 12310/1202 | 0.33 pp | [-1.34, 2.08] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M2 | 809/203 | 0.62 pp | [-3.33, 4.68] pp | NA / 0 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-28.37, 8.33] pp | 43.33% / 30 |
| medeinst/native | M2 | 5383/5383 | 1.80 pp | [0.74, 2.86] pp | 40.37% / 493 |

#### Method scope
Only MedRGAG-Llama base (M2) is required after the explicit user scope correction. Previously completed Direct/retrieval-only outputs are preserved in auxiliary_predictions.jsonl and are not completed full-test comparisons. No cross-method amplification is estimated in this report.

| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |
|---|---:|---:|---|
| M2 | 284/183 | 14.76 pp | [6.63, 22.90] pp |

MedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.

#### Interpretation and limits
The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.

Errors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.

Native/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.

#### Cost and next research decision
Recorded LLM requests (including frozen sensitivity and preserved auxiliary readers): 340304; prompt tokens: 447703546; completion tokens: 77361151. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches explain evidence loss associated with M2 reference/variant prediction changes. These saved stage proxies do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 449853293 logical prompt tokens and 77488473 completion tokens. Exact visible-input deduplication removes 2097 duplicate tasks and avoids 27261 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

#### Execution and parsing details
Formal concurrent batch elapsed: 15.53 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 340834. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M2 | 6 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M2 | 0 | 0 | 0 | 15 |
| medeinst | M2 | 68 | 7749 | 68 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

#### Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M2 | reference | 60 | 38.33% | [26.67, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 2561, 1: 10, 2: 28, 3: 37, 4: 130, 5: 22514}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0292), [validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_test/validation.json).

Full-test expansion: 283694 newly executed requests; 350655816 prompt tokens; 65839313 completion tokens. Aggregate workload above includes prior screening stages reused by exact input equality. The fixed auxiliary 20-input repeat is inherited from the earlier screening subset, not a new random sample of the enlarged test population. See cache_reuse.json for context-capacity provenance.

<a id="record-0295"></a>

## RESEARCH_PLAN.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/RESEARCH_PLAN.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/RESEARCH_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

正文与[已合入记录](#record-0281)相同，统一在该处维护。

<a id="record-0296"></a>

## acquisition.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/acquisition.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/acquisition.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

正文与[已合入记录](#record-0289)相同，统一在该处维护。

<a id="record-0297"></a>

## baseline_contract.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/baseline_contract.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/baseline_contract.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

### Full-test reader completion contract

Current comparison: M0 direct_llama, M1 retrieval_only_llama, M2 medrgag_llama_base. Only missing M0/M1 calls execute in this batch; M2 remains an exact cached result. The authoritative inherited M2 pipeline is documented in [the original contract](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0290).

| Method/stage | Actual function | Model | Configuration | Input/output |
|---|---|---|---|---|
| M0 | run_cf_baseline_screening.Runner.run_chunk, mode=readers; reader_prompt; Runner.llm | local Llama-3.1-8B-Instruct | BF16, original chat template, T=0, top_p=1, max_tokens=64, same per-item/stage seed | frozen independent task, all native options, mandatory evidence; JSON answer |
| M1 | same reader path, with Runner.retrieve exact cache | same Llama | same decoding; initial external reader documents=5 | same task plus unchanged first BM25/MedCPT top5; JSON answer |
| M2 | exact copied stage/answer cache from completed full run | same Llama | original complete KGCC/generation/KADS/reader configuration | no newly executed M2 calls |

Checkpoint and tokenizer: /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct. Context capacity 98304; no quantization or decoder change. Initial retrieval is the same source-balanced BM25 32/source, MedCPT top 5 used by M2, already cached for every item. No new retrieval/reranking, KGCC, complementary generation, KADS, sidecar or judge is required.

Full input and evaluation labels, native answer formats, canonical mapping, parser, invalid policy, seed 20260906 and frozen taxonomy are identical to the original full run. Mode=readers returns immediately after M0/M1 and preserves all model parameters. No sample reduction or option truncation. MedCounterFact mandatory article evidence remains in both readers.

A new independent cache copy preserves the original completed M2 result directory and GitHub archive. Previously completed 5832 predictions per reader are retained; 19448 missing predictions per method are planned (38896 new LLM calls). The same full 25280 unique inputs are compared across all 3 methods. The fixed 20-input M2 seed repeat is inherited, not repeated or ensembled. See reader_completion.json, config.json and cache_reuse.json.

<a id="record-0298"></a>

## data_checks.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/data_checks.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/data_checks.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

正文与[已合入记录](#record-0291)相同，统一在该处维护。

<a id="record-0299"></a>

## findings.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/findings.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/findings.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

### 完整测试集：Direct / retrieval-only / MedRGAG-Llama 对照结果

**完成并验收。M0、M1、M2 各 25,280/25,280 个唯一输入，合计 75,840 条预测、82,131 条方法×评价记录。** 2026-09-07 19:29:22 CST 推理结束，19:31:50 离线分析结束。本次按用户要求补齐此前中止的 M0/M1，保留各 5,832 条旧预测，新增各 19,448 条。M2 和全部上游阶段逐字节复用。

#### 完整发布范围

| 入口 / 协议 | 完成源题组或行级单元 | 评价记录 / 方法 | 唯一输入 / 方法 | 完成率 |
|---|---:|---:|---:|---:|
| MedEinst 官方 test，原生诊断 | 5,383 | 10,766 | 10,755 | 100% |
| MedPIC，原生多选 | 467 | 467 | 467 | 100% |
| CPV-MedQA，真实原题及全部变体 | 1,202 | 13,512 | 11,427 | 100% |
| Cultural-Cues，全部发布源题及变体 | 150 | 1,500 | 1,499 | 100% |
| MedCounterFact，原题及全部发布替换 | 203 | 1,012 | 1,012 | 100% |
| MedEinst，预定四选项辅助 | 60 | 120 | 120 | 100% |

五个入口原生协议均覆盖实际完整发布范围。四选项是冻结的 60 对辅助敏感性协议。CPV 包含 1,202 个真实原题和 12,310 个变体；Cultural 的 1,273 条 MedQA 原题文件是映射池，发布增强评估集为 150 组。此次沿用相同 revision、样本列表、opaque IDs、taxonomy、来源映射和历史曝光标记，没有重新抽样。来源及字段核对见 [acquisition.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0296)、[data_checks.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0298)。

#### 同一模型和调用合同

本地 Llama-3.1-8B-Instruct，BF16、原 tokenizer/chat template，reader temperature=0、max_tokens=64、相同逐输入/阶段 seed；上下文容量 98,304。M0 使用完整合法任务输入；M1 使用同一输入加 M2 的首次 source-balanced BM25/MedCPT top-5 文档。MedCounterFact 必需题内证据和全部原生选项在两者中完整保留。

M2 继承已完成的基础链：两库各 BM25 32 候选 → MedCPT top 5 → KGCC 摘要 5 次及缺失知识探索 1 次 → 补充生成 5 次 → 原始 KADS 1 次 → 最终 MedCPT/reader。模型、采样预算、候选和文档数未改变。新增 `readers` 入口在 M0/M1 后返回，既有全部 M2 阶段与检索缓存无变化；无 Profile、CFShift scorer、CFMoE、sidecar、judge、训练或新方法调用。实际函数和参数见 [baseline_contract.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0297)、[config.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/config.json)。这是 local all-Llama reproduction，与论文混合模型配置有别。

#### 主结果与方法差异

下表为源题组内平均后跨源题平均。差异单位为百分点，95% CI 来自 2,000 次源题组 cluster bootstrap；完整分数区间、micro 分数和分母见 [benchmark_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/benchmark_metrics.csv)。

| 原生入口 / 指标 | M0 Direct | M1 retrieval-only | M2 MedRGAG | M2−M0（pp；95% CI） |
|---|---:|---:|---:|---:|
| MedEinst / canonical match | 10.93% | 7.75% | 8.26% | -2.68 [-3.21, -2.07] |
| MedPIC / exact-set | 35.97% | 36.83% | 30.84% | -5.14 [-8.99, -1.50] |
| CPV-MedQA / accuracy | 61.59% | 63.78% | 67.09% | +5.50 [3.60, 7.34] |
| Cultural-Cues / accuracy | 62.53% | 61.53% | 66.13% | +3.60 [-0.60, 7.80] |
| MedCounterFact / EA | 66.31% | 61.87% | 66.50% | +0.20 [-1.97, 2.56] |

CPV 上 M2 高于 M0 和 M1；MedPIC 上 M2 低于二者。MedEinst 的规范化匹配中 M2 低于 M0，与 M1 的差异区间包含 0。Cultural 上 M2−M0 为 +3.60 pp，但区间包含 0；M2−M1 的区间下界为 0 附近。MedCounterFact 上 M2 与 M0 接近，M1 比 M0 低 4.43 pp（CI [−7.19,−2.07]），M2 比 M1 高 4.63 pp（CI [2.17,7.19]）。这些是各原生指标上的描述性比较，不合并成总体 CF accuracy。

MedPIC option F1 micro / macro：M0 49.53% / 46.73%，M1 51.26% / 47.59%，M2 49.96% / 46.77%。平均预测集合大小为 1.139 / 1.214 / 1.486，真实集合大小 1.343。exact-set 与 F1 的差异提示预测集合内容及大小都影响结果。GF/CF 和官方 operation 切片见 [category_metrics.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/category_metrics.csv)；GF−CF 为非配对 composition gap。

#### 原题到变体的变化

正 drop 表示原题分数高于变体；多变体先在源题组内平均。括号均为未作多重校正的 95% CI（pp）。

| 原生入口 | Pairs / groups | M0 drop | M1 drop | M2 drop | M2 drop−M0 drop |
|---|---:|---:|---:|---:|---:|
| MedEinst | 5383 / 5383 | +5.59 [4.38, 6.80] | +1.60 [0.58, 2.66] | +1.80 [0.74, 2.86] | -3.79 [-4.87, -2.69] |
| CPV-MedQA | 12310 / 1202 | +0.07 [-0.54, 0.68] | +0.58 [-0.38, 1.56] | +0.33 [-1.34, 2.08] | +0.26 [-1.49, 2.06] |
| Cultural-Cues | 1350 / 150 | +2.37 [-0.81, 5.41] | -0.22 [-4.07, 3.78] | -0.15 [-5.56, 5.11] | -2.52 [-8.37, 3.19] |
| MedCounterFact | 809 / 203 | +1.48 [-1.35, 4.43] | +3.94 [-0.25, 8.13] | +0.62 [-3.33, 4.68] | -0.86 [-4.43, 2.46] |

MedEinst 的 M2 drop 小于 Direct，但 M2 的总体 canonical 分数也更低，不能只凭较小 drop 宣称诊断更可靠。其余入口 M2 的整体 drop 及相对 Direct 的 amplification 区间均包含 0；这不证明等价。M1 的 amplification、各条件四格及分母完整保存在 [amplification.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/amplification.csv)、[paired_effects.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/paired_effects.csv)。

本次恢复三方法比较，预定 native Holm 检验族从旧 M2-only 报告的 29 项扩大为 87 项。MedEinst 的 M0/M1/M2 原始 McNemar p 分别约 1.11e−18 / .00308 / .000988，Holm 后约 9.69e−17 / .2616 / .08494。M2 原始预测、drop、CI 和未校正 p 均与旧报告相同，校正后 p 的变化来自比较族扩大。多变体整体不套用把每个变体视为独立源题的 McNemar 检验。

Cultural 相对 Original、跨文化平均的 Id / Context / Id+Context drop：M0 为 +2.00 / +1.56 / +3.56 pp；M1 为 −0.22 / −0.44 / 0.00 pp；M2 为 +0.89 / −2.44 / +1.11 pp。各自源题组区间均包含 0；完整条件及区间在 paired_effects.csv。

#### 错误结构与输出合同

MedEinst 原生的旧答案持续 BTR：M0 622/739=84.17%，M1 219/460=47.61%，M2 199/493=40.37%。正确原题及正确变体的 pair accuracy 分别为 4/5,383、4/5,383、19/5,383。invalid 不自动计旧答案持续；未映射和歧义也不被挑选成碰巧等于 gold 的答案。

CPV 中，原题正确后变体出错的 raw-pair conditional failure 为 M0 131/7,590=1.73%，M1 353/7,925=4.45%，M2 1,005/8,310=12.09%；Cultural 为 7.22% / 8.45% / 15.49%。各方法“原题正确”集合不同；这些条件比例须与源题组分数及 amplification 同看。正确修正/保持、语义 flip、changed-but-wrong、stable-but-wrong 在 [transitions.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/transitions.csv) 分开保存。

M2 相对 Direct 既修正错误，也引入新错误。下表 H 是模型答题错误变化，非临床伤害标注。

| 原生入口 | R：M0 错/M2 对 | H：M0 对/M2 错 | H / 全部记录 | H / M0 正确 |
|---|---:|---:|---:|---:|
| MedEinst | 328 | 616 | 5.72% | 52.34% |
| MedPIC | 29 | 53 | 11.35% | 31.55% |
| CPV-MedQA | 1714 | 957 | 7.08% | 11.50% |
| Cultural-Cues | 172 | 118 | 7.87% | 12.58% |
| MedCounterFact | 38 | 36 | 3.56% | 5.37% |

| 原生入口 | M0 格式/歧义 invalid | M1 格式/歧义 invalid | M2 格式/歧义 invalid |
|---|---:|---:|---:|
| MedEinst | 11 | 7 | 68 |
| MedPIC | 10 | 1 | 4 |
| CPV-MedQA | 17 | 0 | 6 |
| Cultural-Cues | 9 | 3 | 1 |
| MedCounterFact | 0 | 0 | 0 |

MedEinst 未映射诊断另列：M0 6,416/10,766（59.60%），M1 8,572/10,766（79.62%），M2 7,749/10,766（71.98%）；raw-exact 为 7.54% / 4.96% / 5.49%。未映射 JSON 诊断与 malformed output 不同，在冻结 canonical 协议中计错。MedCounterFact uncertainty 为合法输出：M0/M1/M2 分别 5/31/15 条；higher/lower/no-difference 分布完整保存在 metrics.json。

冻结 60 对 MedEinst 辅助中，四选项分数 M0/M1/M2 为 46.67% / 43.33% / 55.00%；相同病例的 native 分数为 11.67% / 5.00% / 7.50%。各方法 reference 与 variant 的四选项−native 区间均高于 0（见 [sensitivities.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/sensitivities.json)）。该协议差异很大，辅助题的选择和选项构造限制了外推，不能用四选项替代全 test 的原生诊断结论。

#### 类型、来源与局限

MedEinst 是临床更新；MedPIC 是患者信息/指南推理的行级任务；CPV 和 Cultural 是答案应保持的身份/文化变换；MedCounterFact 是假设证据世界。三域跨独立临床来源 taxonomy 均为 **NOT_IDENTIFIABLE**。临床更新与假设证据域存在秩不足；身份/文化域仅在同源 MedQA 构造内部可估计描述性关系。CPV/Cultural 有 142 个跨资源源题映射，不能把它们当独立临床来源复现。来源映射、矩阵秩和探索模型在 source_overlap.json、taxonomy_identifiability.json、explanatory_models.json。

MedEinst 主分数是冻结标签规范化匹配，不是作者官方语义诊断评分；高未映射率及原生/四选项差异限制医学解释。MedPIC 缺可验证官方 pair map；Cultural 未发布 Neutral；MedCounterFact 的 147/43/66 三个源题各缺一个发布变体类别。完整发布集中的这些缺项不计为模型失败。MedCounterFact EA 不代表临床安全，也不与诊断 accuracy 平均。

预定曝光、质量标记、去除重叠源题、MedEinst 去除 11 个相同输入而 gold 冲突病例的敏感性全部保留；没有据结果删题或增加医学别名。固定 20 输入的 M2 独立 seed 复测沿用旧结果：19 个双有效输出中语义 flip 7/19，raw 变化 10/20；其早期样本不能代表全 test 的随机性，也未用于集成或分数校正。

#### 本次成本、验收和交付

补跑时间为 2026-09-07 18:44:08—19:29:22 CST，makespan **2,714 秒（45 分 14 秒）**；离线分析再用 148 秒。使用 GPU0/2 的 H20、vLLM 0.8.5、BF16、batch/chunk 64、GPU memory .75。较快分片先正常退出，另一分片继续完成；推理没有重启，没有降候选数、文档数、token 上限或精度。Luna max 负责只读监督，主代理核对心跳、处理初期监控刷新问题并独立验收。

新增 **38,896 次 LLM 请求**，logical prompt tokens **33,914,033**、completion tokens **339,142**。M0/M1 各复用 5,832 条旧答案，M2 全部 25,280 输入及其 328,640 次主干 LLM 阶段记录复用。新增 M0 有 2 次到达原 token 上限，M1 为 0；保留原始输出并按同一规则评分，format repair=0，网络重试=0，pending/transport failure=0。

含旧缓存的三方法主运行共 379,200 次记录调用、481,617,579 prompt tokens、77,700,293 completion tokens；再计旧复测及作废尝试，共 379,730 次、483,767,326 prompt tokens、77,827,615 completion tokens。旧 M2 扩展批次的 15 小时 32 分钟及历史未返回 token 限制保存在 [prior_run_efficiency.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/prior_run_efficiency.json)，不计入本次 45 分钟。精确可见输入去重 2,097 条，逻辑上避免三方法主干 31,455 次请求。logical tokens 包含缓存前缀，不等于物理重算 tokens。

[reader_completion_efficiency.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/reader_completion_efficiency.csv) 单列这次两个 reader 的调用、tokens、阶段时间和截断；[efficiency.csv](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/efficiency.csv) 包含所有已记录历史阶段。阶段时间并行重叠，不能相加作为 makespan。当前 reader 进程的 cache-hit 计数另存 [execution_provenance.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/execution_provenance.json)；metrics.json 还保留历史 worker-2 的 runtime，不把其旧 M2 命中计数误作本次新调用。接口未返回可用 queue time。

4 项合同/覆盖/指标测试通过；全量阶段 key/seed/config/budget、完整 durable prompt 引用、旧 reader 字节前缀和全部非 reader 缓存字节一致性审计通过。M2 导出预测、主指标和 paired 指标与旧结果完全相同。所有表的四格、drop、gain、OCP、source-macro 和 amplification 恒等式通过。见 [artifact_audit.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/artifact_audit.json)、[validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/validation.json)。

10 张实际数据图均有 SVG/PNG，见 [figures/](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/figures)；流程图源码见 [flow.mmd](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/flow.mmd)。从仓库根目录执行 `bash cf_medrgag_validation_pack/results_cf_full_comparison/commands.sh` 即可依次 prepare/readers/analyze/audit，完整缓存下会跳过已完成推理。数据和模型资产要求与旧完整运行相同。原始 benchmark 文本、模型/检索库、凭据及大型正文缓存留在服务器，下载器、IDs、原生预测和派生结果按既有归档约定提供。

本次推理代码基于 commit `79a9454`，M2 来源结果 commit `638f1e3ad116ffdad609e74bb5a9f019a196911e`；本报告和脚本随最终结果提交，GitHub 独立快照列在仓库 `benchmarks/` 索引，保留旧 M2-only 快照。

#### 研究判断

本轮支持“不同入口的表现及变化模式不同”的描述性结论；不支持统一退化或统一提升，也不能验证跨独立来源 taxonomy。一个后续值得检验的机制是原始 KADS 输出/解析造成的空证据，是否与 M2−M1 的错误换答相关。已有 2,561/25,280（10.13%）空选择及文档来源记录提供线索；当前只有 proxy/association，没有开展新的 parser、gate、judge 或因果实验。

<a id="record-0300"></a>

## smoke_review.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/smoke_review.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/smoke_review.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

正文与[已合入记录](#record-0286)相同，统一在该处维护。

<a id="record-0301"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison`。

### Cross-benchmark all-Llama baseline screening

Status: **complete**; unique method predictions 75840/75840.

Evaluation scope: entire official test/released evaluation data; no source-group sampling.

Current batch completes the previously stopped M0/M1 readers on the exact same entire test set. All 25,280 M2 predictions and their stages are inherited unchanged. Full three-method results are now compared; current batch wall time covers only the missing M0/M1 calls.

Local baseline and exact stage contract: [baseline_contract.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0297). Public source revisions and release discrepancies: [acquisition.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0296).

#### Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M0 | 13512 | 61.59% | [58.86%, 64.24%] | 61.60% | 17 | 1202/1202 |
| cpv | M1 | 13512 | 63.78% | [61.08%, 66.58%] | 63.85% | 0 | 1202/1202 |
| cpv | M2 | 13512 | 67.09% | [64.89%, 69.35%] | 67.20% | 6 | 1202/1202 |
| cultural | M0 | 1500 | 62.53% | [55.67%, 69.60%] | 62.53% | 9 | 150/150 |
| cultural | M1 | 1500 | 61.53% | [54.73%, 68.60%] | 61.53% | 3 | 150/150 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M0 | 1012 | 66.31% | [60.20%, 72.22%] | 66.30% | 0 | 203/203 |
| medcounterfact | M1 | 1012 | 61.87% | [55.96%, 67.78%] | 61.86% | 0 | 203/203 |
| medcounterfact | M2 | 1012 | 66.50% | [60.59%, 72.12%] | 66.50% | 0 | 203/203 |
| medeinst | M0 | 10766 | 10.93% | [10.39%, 11.48%] | 10.93% | 6427 | 5383/5383 |
| medeinst | M1 | 10766 | 7.75% | [7.26%, 8.23%] | 7.75% | 8579 | 5383/5383 |
| medeinst | M2 | 10766 | 8.26% | [7.76%, 8.75%] | 8.26% | 7817 | 5383/5383 |
| medpic | M0 | 467 | 35.97% | [31.69%, 40.26%] | 35.97% | 10 | 467/467 |
| medpic | M1 | 467 | 36.83% | [32.55%, 41.11%] | 36.83% | 1 | 467/467 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

#### Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M0 | 12310/1202 | 0.07 pp | [-0.54, 0.68] pp | NA / 0 |
| cpv/native | M1 | 12310/1202 | 0.58 pp | [-0.38, 1.56] pp | NA / 0 |
| cpv/native | M2 | 12310/1202 | 0.33 pp | [-1.34, 2.08] pp | NA / 0 |
| cultural/native | M0 | 1350/150 | 2.37 pp | [-0.81, 5.41] pp | NA / 0 |
| cultural/native | M1 | 1350/150 | -0.22 pp | [-4.07, 3.78] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M0 | 809/203 | 1.48 pp | [-1.35, 4.43] pp | NA / 0 |
| medcounterfact/native | M1 | 809/203 | 3.94 pp | [-0.25, 8.13] pp | NA / 0 |
| medcounterfact/native | M2 | 809/203 | 0.62 pp | [-3.33, 4.68] pp | NA / 0 |
| medeinst/derived_four_way | M0 | 60/60 | 0.00 pp | [-20.00, 21.67] pp | 64.29% / 28 |
| medeinst/derived_four_way | M1 | 60/60 | -10.00 pp | [-28.33, 10.00] pp | 60.87% / 23 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-28.37, 8.33] pp | 43.33% / 30 |
| medeinst/native | M0 | 5383/5383 | 5.59 pp | [4.38, 6.80] pp | 84.17% / 739 |
| medeinst/native | M1 | 5383/5383 | 1.60 pp | [0.58, 2.66] pp | 47.61% / 460 |
| medeinst/native | M2 | 5383/5383 | 1.80 pp | [0.74, 2.86] pp | 40.37% / 493 |

#### Changes relative to Direct and retrieval-only
| Benchmark/protocol | Comparison | Source groups | Source-mean score gain | 95% CI | Introduced errors / items | Conditional harm |
|---|---|---:|---:|---|---:|---:|
| cpv/native | M1-M0 | 1202 | 2.19% | [0.17, 4.15] pp | 909/13512 | 10.92% |
| cpv/native | M2-M0 | 1202 | 5.50% | [3.60, 7.34] pp | 957/13512 | 11.50% |
| cpv/native | M2-M1 | 1202 | 3.31% | [1.47, 5.20] pp | 1178/13512 | 13.65% |
| cultural/native | M1-M0 | 150 | -1.00% | [-6.13, 3.87] pp | 135/1500 | 14.39% |
| cultural/native | M2-M0 | 150 | 3.60% | [-0.60, 7.80] pp | 118/1500 | 12.58% |
| cultural/native | M2-M1 | 150 | 4.60% | [-0.00, 9.27] pp | 140/1500 | 15.17% |
| medcounterfact/native | M1-M0 | 203 | -4.43% | [-7.19, -2.07] pp | 67/1012 | 9.99% |
| medcounterfact/native | M2-M0 | 203 | 0.20% | [-1.97, 2.56] pp | 36/1012 | 5.37% |
| medcounterfact/native | M2-M1 | 203 | 4.63% | [2.17, 7.19] pp | 31/1012 | 4.95% |
| medeinst/derived_four_way | M1-M0 | 60 | -3.33% | [-10.83, 4.17] pp | 13/120 | 23.21% |
| medeinst/derived_four_way | M2-M0 | 60 | 8.33% | [0.83, 15.83] pp | 7/120 | 12.50% |
| medeinst/derived_four_way | M2-M1 | 60 | 11.67% | [3.33, 20.83] pp | 9/120 | 17.31% |
| medeinst/native | M1-M0 | 5383 | -3.19% | [-3.79, -2.56] pp | 741/10766 | 62.96% |
| medeinst/native | M2-M0 | 5383 | -2.68% | [-3.21, -2.07] pp | 616/10766 | 52.34% |
| medeinst/native | M2-M1 | 5383 | 0.51% | [-0.04, 1.05] pp | 425/10766 | 50.96% |
| medpic/native | M1-M0 | 467 | 0.86% | [-1.71, 3.64] pp | 20/467 | 11.90% |
| medpic/native | M2-M0 | 467 | -5.14% | [-8.99, -1.50] pp | 53/467 | 31.55% |
| medpic/native | M2-M1 | 467 | -6.00% | [-10.06, -2.14] pp | 56/467 | 32.56% |

Gain intervals use source means. Introduced-error and conditional-harm columns retain their specified item-level denominators; for M2−M1, the comparator is M1. Positive paired amplification means greater reference-to-variant sensitivity than Direct; it is not a causal finding.

| Benchmark/protocol | Method | Drop amplification vs Direct | 95% CI |
|---|---|---:|---|
| cpv/native | M1 | 0.52 pp | [-0.61, 1.67] pp |
| cpv/native | M2 | 0.26 pp | [-1.49, 2.06] pp |
| cultural/native | M1 | -2.59 pp | [-6.96, 2.00] pp |
| cultural/native | M2 | -2.52 pp | [-8.37, 3.19] pp |
| medcounterfact/native | M1 | 2.46 pp | [-1.35, 6.04] pp |
| medcounterfact/native | M2 | -0.86 pp | [-4.43, 2.46] pp |
| medeinst/derived_four_way | M1 | -10.00 pp | [-25.00, 5.00] pp |
| medeinst/derived_four_way | M2 | -10.00 pp | [-26.67, 5.04] pp |
| medeinst/native | M1 | -3.99 pp | [-5.22, -2.79] pp |
| medeinst/native | M2 | -3.79 pp | [-4.87, -2.69] pp |

| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |
|---|---:|---:|---|
| M0 | 284/183 | 16.92 pp | [8.52, 25.68] pp |
| M1 | 284/183 | 17.43 pp | [9.15, 26.19] pp |
| M2 | 284/183 | 14.76 pp | [6.63, 22.90] pp |

MedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.

#### Interpretation and limits
The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.

Errors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.

Native/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.

#### Cost and next research decision
Recorded main-run LLM requests (including frozen sensitivity inputs): 379200; prompt tokens: 481617579; completion tokens: 77700293. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches cause evidence loss that explains M2−M1 changes within the same source question. Current empty-selection/document-count records motivate this question but do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 483767326 logical prompt tokens and 77827615 completion tokens. Exact visible-input deduplication removes 2097 duplicate tasks and avoids 31455 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

#### Execution and parsing details
Formal concurrent batch elapsed: 0.75 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 379730. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M0 | 17 | 0 | 0 | 0 |
| cpv | M1 | 0 | 0 | 0 | 0 |
| cpv | M2 | 6 | 0 | 0 | 0 |
| cultural | M0 | 9 | 0 | 0 | 0 |
| cultural | M1 | 3 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M0 | 0 | 0 | 0 | 5 |
| medcounterfact | M1 | 0 | 0 | 0 | 31 |
| medcounterfact | M2 | 0 | 0 | 0 | 15 |
| medeinst | M0 | 11 | 6416 | 10 | 0 |
| medeinst | M1 | 7 | 8572 | 7 | 0 |
| medeinst | M2 | 68 | 7749 | 68 | 0 |
| medpic | M0 | 10 | 0 | 0 | 0 |
| medpic | M1 | 1 | 0 | 0 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

#### Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M0 | reference | 60 | 31.67% | [20.00, 45.00] pp |
| M0 | variant | 60 | 38.33% | [25.00, 51.67] pp |
| M1 | reference | 60 | 33.33% | [21.67, 45.00] pp |
| M1 | variant | 60 | 43.33% | [30.00, 56.67] pp |
| M2 | reference | 60 | 38.33% | [26.67, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 2561, 1: 10, 2: 28, 3: 37, 4: 130, 5: 22514}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](/home/data3/txy/docs/archive/native_baseline_screening.md#record-0299), [validation.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cf_full_comparison/validation.json).

Full-test reader completion: 38896 newly executed requests; 33914033 prompt tokens; 339142 completion tokens. Aggregate workload above includes prior screening stages reused by exact input equality. The fixed auxiliary 20-input repeat is inherited from the earlier screening subset, not a new random sample of the enlarged test population. See cache_reuse.json and prior_run_efficiency.json for exact reuse and prior-cost provenance.
