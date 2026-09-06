# Medical RAG 的反事实基线筛查：研究判断与首轮实验设计

**日期：2026-09-06；用途：研究方案，不是已经完成的实验报告。**  
**本轮目标：在不加载现有反事实增强模块的情况下，研究同一医学 RAG 主干在不同受控变化任务中的表现与错误模式。**

## 0. 最终建议

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

## 1. 证据基础、已核对内容与没有核对到的内容

### 1.1 本轮资料来源

- **[H1]** 用户上传 `2026-8-23 1-32-45-Medrgag__.md`：研究讨论、旧计划、实验汇报和方向调整。
- **[H2]** 用户上传 `README.md`：2026-09-05 的 evidence handoff，记载截至 `53aaff676439066f8d0b6478404c91e7ece3528f` 的数据、结果、实现边界、硬件和运行日志。
- **[H3]** 用户上传 `literature_and_benchmarks.md` 及上一轮严格筛选报告：作为候选检索起点，不将里面的早期判断自动视为验证事实。
- **[S01–S25]** 本轮查阅的原论文、官方数据卡、作者仓库和官方文档，见文末。

### 1.2 当前 GitHub 状态的明确限制

本次尝试了用户仓库页面、原始文件和已知提交入口，但没有成功取得 `cf_mrg` 当前 HEAD 或当前代码正文。**不能声称已经审计最新分支的具体函数。** 本次能够直接核对的是上传材料里的项目快照，以及原始 MedRGAG 官方实现。

因此，“选择现有 M2 / all-Llama 基线调用链”是有历史证据支持的具体建议；“该链在当前 checkout 的具体函数与配置文件是什么”需要 Codex 首先从本地仓库定位。不要为填补这个缺口虚构函数名，也不要直接回滚整个仓库到旧提交。[H1–H2; S01–S03]

这不阻止研究设计，但限制了本文件对当前代码的保证范围。

## 2. 对研究状态的理解：哪些是主线，哪些已经不是

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

## 3. 研究问题需要怎样修正

原问题“不同 CF 类型是不是下降不同”值得检验，但存在三处逻辑风险。

### 3.1 不是所有 CF 都要求改答案

临床判别证据变化可能要求更新诊断；不决定答案的身份信息变化应该保持答案；假设证据中的实体替换可能要求保持证据比较关系，但不能因此声称现实临床建议也正确。[S04–S13]

因此应研究 **对任务要求的选择性敏感性**：该改时是否正确更新，不该改时是否保持，给定假设证据时是否按任务语义处理。

### 3.2 同类下降接近，不是分类成立的必要条件

两个属于同一类的 benchmark 可能因为文本长度、基础难度、输出形式和构造方式不同而下降不同。两个不同类也可能偶然有相同平均下降。

更可证伪的主假设是：

> 在有可比较的任务、来源和配对结构时，预先定义的变化类型，能否解释并预测一部分错误模式，而且这种解释不能完全归结为 dataset 名称或输出格式？

### 3.3 五个名称不等于五个独立来源

CPV-MedQA 与 Cultural-Cues 都源于 MedQA。MedEinst 与 DDXPlus 有数据血缘关系。多个变体也不是多个独立患者。来源关系需要显式登记并在统计中聚类，不能把几千变体当几千独立观察。[S04, S08–S11]

最重要的可识别性规则是：**一个类别只出现在一个 benchmark 时，类别效应与 benchmark 效应不可分离。增加该 benchmark 的样本数量不会自动解决这个问题。**

## 4. Benchmark 搜集与选择

### 4.1 纳入标准

一个资源进入本轮必须满足：医学文本任务；有明确的受控替换、编辑或假设；能确定该任务期望的回答行为；有公开任务记录与可用标签或官方评价定义；能在不伪造患者事实、配对、选项或答案的情况下接入。

“严格临床 CF”在本文件中特指：**遵循现实医学规则，改变患者相关条件，考察临床判断如何随之变化**。这是一项操作性范围选择，不宣称这是所有领域唯一合法的 counterfactual 定义，也不声称文本编辑已识别出个体因果效应。

文献搜索同时覆盖 clinical/medical counterfactual benchmark、minimal/contrastive clinical pairs、patient-information intervention、demographic/cultural counterfactual、hypothetical medical evidence、causal laboratory reasoning 及相关官方代码。对原清单中的边界候选回查任务与资产。

本轮完成了候选与关键原始资源核验；**没有完成所有数据库的全量导出和全引文追踪，不声称绝对穷尽全部文献。** 可核查性比无依据的“全覆盖”更重要。

### 4.2 首轮确定集合

| 资源 | 原生任务 / 原始规模 | 访问核验 | 纳入理由 | 必须保留的边界 |
|---|---|---|---|---|
| **MedEinst** | control/trap 诊断病例；论文及数据卡报告 5,383 test pairs、49 疾病 | 官方 HF 有实际记录、pair 字段、gold 与评价说明 | 最直接的诊断证据更新；项目已有资产 | 原生开放诊断；四选项是本项目派生协议；DDXPlus 同源；实际下载数量以指定 revision 为准 |
| **MedPIC-Bench** | 467 行用药安全多选；284 GF、183 CF | 官方 HF 可见题干、患者情境、答案集合和 taxonomy 字段 | 将反事实从诊断扩展到规则适用性 | 不能把 467 行称为 467 对；未取得官方映射前，GF–CF 是非配对组差 |
| **CPV-MedQA** | 人口属性变体；项目及公开 HF 为 12,310 行快照 | 官方仓库及 HF 实际字段可见 | 检验原作者规定的答案不变行为；可复用项目数据 | MedQA 衍生；年龄/性别不能普遍视为医学无关；需检查原题恢复、无操作与冲突文本 |
| **Cultural-Cues 医学 CF 集** | 150 MedQA 原题；总计 1,650 输入，含原题、中性、三文化×三操作 | 作者仓库已定位具体输入 JSON 与原题文件；本轮没有下载解析整库 | 有同一原题下 Id / Context / Id+Context / Neutral 的交叉对照 | 与 CPV 同源；不是第五个独立临床来源；不要使用发布的旧模型输出代替新实验 |
| **MedCounterFact** | 医疗证据比较；203 原始问题及四类替换，实际行数按发布文件计算 | 官方 original/replaced JSONL 及 DataFormat 可见 | 测试外部参数知识与给定假设证据的冲突 | 单列证据世界轨；EA 不是现实治疗安全准确率；原始与替换记录用 metadata.id 对齐 |

来源：MedEinst [S04–S05]；MedPIC [S06–S07]；CPV [S08–S09]；Cultural-Cues [S10–S11]；MedCounterFact [S12–S13]。

**数量结论：**可以提出五个有合理用途、存在公开资产入口的医学领域 CF 评测入口；不能据此声称本次找到了五个已完整下载、严格临床状态 CF、且互相独立的数据集。目前本轮明确、可直接推进的窄临床主集合仍是两项。

### 4.3 优先扩展、暂不运行与排除

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

## 5. Taxonomy：最终采用什么，以及怎样修订

### 5.1 第一层：任务约定，决定怎样解释分数

| 组别 | 受控变化 | 要求模型做什么 | 首轮数据 |
|---|---|---|---|
| **C：临床条件更新** | 症状、检查、病史、患者条件等 | 按新病例重算诊断或规则适用性；是否换答案以实际标签为准 | MedEinst、MedPIC |
| **I：答案不变性** | 经原任务定义为非决定性的信息 | 不让这些变化引入错误更新 | CPV、Cultural-Cues |
| **W：假设证据世界** | 题目和证据中的干预实体被替换 | 按原任务区分证据结论、认知冲突与现实合理性 | MedCounterFact |

这层是评估协议分层，不是“所有 CF 的普适理论分类”。W 不与 C/I 合成一个总准确率或总下降排行榜。

### 5.2 第二层：实际变化操作，允许跨 benchmark 复用

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

### 5.3 第三层：描述标签，不当作平级类别

- **临床目标**：diagnosis、medication eligibility/safety、evidence comparison。
- **答案关系**：`change / invariant / relation_transport / unknown`；来自官方配对与语义标签，不把答案字母是否变化作为依据。
- **变化幅度**：single-concept / linked-multiple / broad / unresolved。文本长度差是另外的数值特征。
- **来源与协议**：原始题库、构造方式、输出类型、原生/派生版本、配对可靠性。

诊断发生变化是目标结果；minimal 是幅度；temporal 是操作；它们不能并列成互斥类别。

### 5.4 设计修订与剩余风险

| 被检验的设计 | 主要问题 | 本方案的修订 |
|---|---|---|
| 按数据集名称或医学专科分组 | 不能证明 CF 类型的作用 | 使用跨集可复用操作标签，另存任务/专科 |
| 用一张互斥长列表涵盖所有概念 | 输入、输出、幅度混杂；许多样本同时落多类 | 任务约定、操作、目标/幅度分轴 |
| 按 accuracy drop 聚类后命名类型 | 分类与验证循环论证 | 先按文本及官方结构标注，冻结后再看输出 |
| 直接拟合 dataset+type 的回归 | type 与 dataset 完全共线时系数不可识别 | 先检查交叉覆盖与设计矩阵；不可识别就报告，不强行估计 |
| 以“不显著不同”说明同类相似 | 低功效也会得不显著 | 预先定义等价范围，做等价性/区间分析；否则只说未能区分 |

剩余风险仍然存在：严格临床 benchmark 少；有些类别只有一个来源；自动标签可能误判；参考标签本身可有噪声。它们不再阻止**筛查**，但阻止首轮直接宣称“普适 taxonomy 已证实”。优先补 MamaBench，是为了增加独立诊断来源，不是为了把数字变成六。

## 6. 首轮明确的样本和运行范围

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

## 7. Baseline 选择与公平性

### 7.1 使用哪个版本

从当前 checkout 中定位最近仍然保留的 **all-Llama 原始检索→KGCC→KADS→reader 的基线路径**，以历史 `medrgag_proxy / medrgag_mcq_proxy / M2` 为线索。复用当前可工作的实现，停用后加专家；不要通过回滚恢复旧的 parser、指标和 gold 隔离错误。[H1–H2]

正式名称建议：

> **MedRGAG-Llama local reproduction，原生任务合同适配版。**

不能称为“原论文精确 SOTA 复现”，因为原论文部分辅助模块使用 GPT-4o-mini，而这里采用本地 Llama。[S01–S03]

### 7.2 必须保留 / 必须关闭

| 必须保留 | 本轮关闭 |
|---|---|
| 同一 Llama-3.1-8B-Instruct checkpoint/tokenizer/精度 | MA-RAG、Qwen sidecar |
| 已有 source-balanced retrieval、BM25、MedCPT | DDXPlus Profile expert、CPG、自生成 CF edits |
| KGCC 的摘要、知识缺口探索、补充生成 | CFShift、CF-KADS、ECR-lite、delta query |
| 原始 KADS 选择与最终 reader | Fusion、RiskRoute、residual gate、verifier/corrector |
| 当前固定候选数、文档数、温度和生成长度配置 | 额外全选项似然、多排列集成、投票 |
| 原生题目必须提供的患者信息、题内证据 | NICE、transition cards、oracle、旧 WM 路径 |

官方实现可作为结构核对：多源检索、生成补充文档、联合选择、最终作答。但官方参数和当前本地实现的差异需要记录，不要一边筛查一边偷偷切换配置。[S02–S03]

### 7.3 为什么需要两个便宜的额外对照

- **M0 Direct**：同一 Llama，只看该题要求的输入。MedCounterFact 的题内证据不是“外部增强”，必须保留。
- **M1 Retrieval-only**：同一初始检索和重排结果、同一 reader；不执行 KGCC/KADS。
- **M2 MedRGAG-base**：完整基础主干。

M1 复用 M2 初始检索，不重新检索另一套语料。这两个对照只是额外 reader 调用，不是两套完整的大型框架。

### 7.4 原生任务与 MCQ 方法的不可回避冲突

无法同时做到“原生开放诊断完全不改”和“原来只接受 MCQ 的 reader 合同一个字不改”。合理方案是保留方法内部流程，允许**最小任务输入/输出适配**，并公开说明。[S03–S07]

- MedEinst 主筛查：只给当前病例，要求一个明确诊断；不能发送会被复制的 `concise diagnosis` 占位模板。主评分为冻结 canonical/来源支持 alias 的确定性规范化匹配，同时保留 raw exact 和无法归一化的比例。不能随意把不同临床亚型并为同一答案。没有可靠官方语义 evaluator 时，不冒充官方开放诊断分数。
- 四选项 60 对是输出空间敏感性，不是用较高 MCQ 分数替代原生结果；其选项构造受 gold 和 DDXPlus 血缘影响，明确标记 derived，不与原论文 SOTA 比。
- MedPIC：真正的多选集合生成与 exact-set；不要用四个独立 Yes/No 概率阈值替代原 reader。
- CPV/Cultural：保留原始所有选项与顺序；不强行截为四个。
- MedCounterFact：保留被替换的 question+article_summaries；输出比较关系/明确不确定。不要把原始 metadata 的 treatment 或 canonical question 回填到替换题。

整个 M0/M1/M2 在同一任务内使用相同的输入、答案空间、格式约定与确定性解析。

## 8. 推理协议：让比较真的只反映输入变化

每个原始/反事实输入 **独立作答**，无共享会话记忆，无上个答案，无另一病例，无 gold delta，无类别提示。pair 只在离线分析时合并。

因此“revision”在本轮指两次独立预测对病例变化的正确响应，不表示模型在一个多轮对话中明确撤回旧答案。不要偷换成记忆或信念更新实验。

必需的题内观察/证据不能被 KADS 当作可选外文档丢掉。长输入采用预先冻结的统一上下文预算；记录截断位置和是否损失任务事实。对超预算题报告不兼容或单列，不能默认“保留前半段”后把缺信息造成的失败当 reasoning 缺陷。

同一 prompt 的重复输入可能产生随机差异。额外固定 20 个输入，各执行一次不同预定 seed 的完整复测，不走预测缓存；用于估计采样噪声。它不是三种子全量实验，也不用于挑最优 seed。

## 9. 核心指标：统一可比部分，保留不可比部分

### 9.1 真正配对的正确性变化

对 source unit i 的 reference 与 variant，定义正确性 C0_i、C1_i∈{0,1}。统计：

- n11：两次均正确；n10：原来正确、变体错误；
- n01：原来错误、变体正确；n00：两次均错误。

**Drop = A_reference − A_variant = (n10 − n01)/N。** 正值表示下降，所有表统一这个符号。

同时报告四格，避免“没有平均下降”掩盖大量互相抵消的错误变化。

### 9.2 答案应变化的对

- Variant accuracy。
- Both-correct pair accuracy = n11/N。
- Conditional correct revision = n11/(n11+n10)，限定语义 gold 确实不同的 pairs。
- Old-answer persistence：原题答对且变体输出旧 gold 的数量 / 原题答对的数量；与 MedEinst 官方 BTR 对齐，并报告分母。
- Changed-but-wrong：变体确实换答案但没有换对，不当成功。

### 9.3 答案应保持的对

- Correct preservation = n11/(n11+n10)。
- Harmful flip = n10/(n11+n10)。
- Semantic flip = 预测语义发生变化的比例。
- Stable-but-wrong：两次同样错误，不能当作良好稳健性。

同一公式因任务约定不同而对应不同临床含义；不是给全库一个含糊的“consistency”。零分母报告 NA，不填 0%。

### 9.4 多变体数据

先在每个源题内按预定义变体/类别平均，再对源题平均；同时提供原始逐条件分数。原题只需推理一次，但统计仍保留不同对照关系。不要让变体多的患者在总体统计里获得更多隐含权重。

CPV 原题若无法可靠恢复，只做组内不变性，reference drop 标为不可用，不用 White/Male 替代“正常患者”。

### 9.5 无可靠配对的数据

MedPIC 报 exact-set、micro/macro option F1、集合大小、GF/CF 与官方 operation slices。GF−CF 可以展示，但名称为 **非配对构成差**，不能混进配对 drop 总体估计。只有取得官方验证映射后才计算 pair metrics。

### 9.6 MedCounterFact

EA/evidence-conditioned relation accuracy、输出不确定率、输出分布，按四类替换分开。安全/荒谬性识别仅在有合法标签或独立可靠评估时评分，否则保留定性输出而不自造 gold。**EA 高不代表临床安全高；EA 下降不必然等于临床能力下降。**

### 9.7 MedRGAG 是否额外放大变化敏感性

对于同一配对单元：

**Amplification = Drop_M2 − Drop_M0。**

再比较 M1。若三者都下降，首先是共同任务困难；若 M2 的额外下降稳定更大，才提示完整检索–生成–选择流程的附加敏感性。它仍不能单独确定是 KGCC hallucination 还是 KADS 的责任。

M2 相对 M0 的 wrong→correct 与 correct→wrong 另记为方法间 repairs/harms，不能与 reference→variant 的变化四格混用。检查 `(R−H)/N = Acc_M2−Acc_M0`。

## 10. 如何验证 taxonomy，而不是事后画漂亮图

### 10.1 五个研究问题的证据要求

| 研究问题 | 首轮可以怎样回答 | 不能做什么 |
|---|---|---|
| M2 是否普遍下降？ | 各可配对 benchmark 的 drop 与区间；分 C/I/W 报告 | 把 MedPIC 非配对差和 MCF EA 合成一条“普遍下降” |
| benchmark 之间是否不同？ | 按任务/原生协议分别比较效应与失败谱 | 用原始 accuracy 排名直接解释 CF 难度 |
| 同类跨集是否相似？ | 在共同操作、任务和足够来源覆盖下比较；CPV/Cultural 为同源构造复制 | 将单一 benchmark 内成千上万变体当跨来源重复 |
| 不同类型是否系统不同？ | 优先同一原题的交叉对照，如 Cultural 的 Id、Context、组合、中性 | 让 dataset 与 type 完全绑定后宣称独立类型效应 |
| taxonomy 是否有意义？ | 类型是否增加超出来源/格式的解释、是否在留出来源上保留方向 | 将无显著差异解释成“证实同类相同” |

### 10.2 统计实施

- 主要效应做 2,000 次 source-cluster bootstrap；原题全部变体一起重采样。跨 CPV/Cultural 的同源题尽可能统一源题键。
- 两条件成对正确性可用 McNemar；预先限定主要比较，提供 Holm 校正。多标签探索其余结果标记 exploratory。
- 同类“足够相似”预设 ±5 个百分点作探索性等价范围，报告两单侧检验或等价 90% CI；区间太宽就是证据不足，不是相同。
- 可比子域内比较仅有 dataset/source/format/长度的模型与加入 operation 的模型；先检查 design matrix、实际变异与类别覆盖。
- 若 type 完全嵌套在 dataset，输出 `NOT_IDENTIFIABLE`。正则化、随机效应和增加样本不能凭空产生缺失的交叉对照。
- 留一 benchmark/source 验证仅用于训练与测试均有相应类别、且评价语义一致的子域；不适用时报告原因。
- 300 对的配对估计通常不足以确认几百分点的等价；例如 discordant probability≈0.3 时，零附近 drop 的近似 95% 半宽约 6.2pp。这是设计示例，不是预计效果。

本轮最强的 taxonomy 检验机会是 **同一 Cultural-Cues 原题的操作交叉**。严格临床 C 组的“跨来源诊断更新规律”还需要 MamaBench 或另一个可用独立来源。

## 11. 要记录什么，才能解释错误

保存原始响应、解析答案、各阶段原始文档/生成文档/最终选择、查询、模型和 prompt 配置、输入/输出 token、阶段时间、无效与截断状态。不得只存最后 accuracy。

低成本分析可以计算：reference/variant 文档重叠、新增信息关键词覆盖、检索分数变化、生成文档比例、错误转移。它们只是机制线索。

**相同检索文档不必然失败**：同一篇鉴别诊断文档可能同时覆盖两种情况。仅凭相似度或 LLM 自评不能声称“正确证据缺失”或“生成内容不真实”。若后续需要因果归因，再单独做固定证据、充分证据或模块干预实验，不在首轮自动展开。

## 12. 运行成本怎样控制，而不偷偷改 baseline

允许的优化：移除本轮不需要的专家调用；常驻 Llama 服务；跨病例批处理；重排微批；检索与其他病例生成重叠；相同原题精确复用；重复评估离线计算；在显存允许时测试独立服务副本。

不允许的“加速”：删除 KGCC/KADS；减少基线规定文档/生成候选/轮次；换小模型或量化后仍使用同一基线名；缩短生成上限截掉推理；只对已知难题调用模块；跳过慢题；语义缓存把仅差否定词的病例合并；把选项似然/多排列集成当作原 reader。

vLLM 的 prefix caching 主要减少重复前缀 prefill，不能省掉实际生成 token；并发上限与 token batch 应由吞吐、排队和 KV 抢占一起判断，而不是看 GPU 利用率。[S24–S25]

历史 4h39 是 full sidecar，里面基线相关阶段约 1h43，但该阶段还包含 M0/M2 与输入展开，**不能直接推断一个原生 benchmark 的准确用时**。[H2]

将 24 小时作为执行批次预算而不是保证。先用代表性输入实测各类型成本，列出 M2 任务数、LLM 调用数、预期 token 和余量。若超过预算，在看到正式结果前采用事先声明的紧缩档。执行中保留完整未完成清单，不能把运行不完整伪装成全量。

## 13. 图表由研究问题决定

此时不生成结果图。执行完成后，仅生成数据支持的以下图表：

1. **配对 drop + 95% CI 图**：只放可配对、同语义的指标；MedPIC 和 MedCounterFact 独立 panel/file，不做误导的共同排序。
2. **四格错误转移 / correct revision 与 harmful flip 图**：回答“不会更新”还是“乱更新”，同时显示分母。
3. **类别×benchmark 覆盖及失败谱图**：空单元标 NA，不补 0；显示哪些分类结论有交叉证据。
4. **Cultural Id/Context/组合相对 Original 与 Neutral 的对比图**：这是有明确组内因子设计的类型检验。
5. **M0/M1/M2 敏感性差异图**与 **吞吐/成本表**：分别定位 RAG 附加效应和效率。
6. **实际执行流程图**：标清数据协议分流、三个方法、独立推理与离线配对。未执行的 optional 支路不画成完成状态。

不需要雷达图、强行全库总分或没有来源的临床危害图。若某图缺少数据，报告为何不生成。

## 14. 研究推进与结果判读

| 阶段 | 交付 | 继续条件的含义 |
|---|---|---|
| 资料与当前代码核对 | 来源/配置差异、数据可用性与调用链 | 只排除无效接口，不因没掉点停止 |
| taxonomy 与样本冻结 | 标签规则、交叉覆盖、来源关系、采样清单 | 不看模型结果分组 |
| 小规模合同与性能测试 | 每集真实样本、各方法输入输出、token/吞吐 | 系统性格式错先修；不搞极端 fail-closed |
| 首轮 screening | 五入口的三方法预测、阶段记录、完整性计数 | 固定计划执行；负结果完整保留 |
| 离线分析 | 指标、CI、可识别性、图表与失败模式 | 决定后续收窄范围而非自动加模块 |
| 后续研究设计 | 选择一个可重复、可修复机制；确定独立确认集 | 本轮不实现新方法 |

结果没有下降，是对原始假设有信息的结果；不同 benchmark 下降不同但类型不能解释，也有研究价值。只有当类型与错误模式的联系跨来源复现，才能逐步升级 taxonomy 主张。若只在同一个 MedQA 衍生家族中成立，应明确写成同源构造下的结果。

## 15. 相关方法在本轮的角色

ECR-Agent、EA-RAG、CF-RAG、CPG、CoRFu 仍是后续优化的最近邻候选，但不进入首轮推理矩阵。现在就把它们全接回去，会把“基础失效是什么”与“哪个插件涨点”重新混为一谈。

分类是实验组织与可检验假设，不必硬包装成独立理论贡献。首轮完成后才能决定：做临床更新方法、研究无关变化敏感性，还是聚焦证据世界冲突。这不是提前放弃方法，而是避免重复过去“先搭复杂模块，后发现任务与指标没对齐”的路径。[H1–H2]

## 16. 来源索引

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
