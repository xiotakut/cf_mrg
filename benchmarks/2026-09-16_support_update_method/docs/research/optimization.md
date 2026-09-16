# 医疗反事实优化：研究总览与跨head经验

2026-09-16写作交付：[R1–R3支持更新与候选重决策论证稿](support_update_method.md)已完成，按用户要求通读指定三会话的可读正文及三方向主记录、运行与失败文档，参考MedRAG、Self-BioRAG、CF-RAG组织“低分现象—原因—失败取舍—方法—证据”的完整论述。新文档专门承接跨方向论文叙述，本页与R2/R3主记录继续承担各自实验历史，避免复制运行日志；可核对的阅读范围与[证据清单](../../evidence/reading_scope.md)随稿保存。本次仅写作、文献核对和制品核验，0新模型调用，默认head与正式v5不变。

2026-09-16审计补充：[R1/R2同口径交叉审计完成](#r1-cross-head-evidence-audit)，R1的20062条白名单输入回放、正式基线及140分层重算一致，R2的553条回放也通过；本轮0新模型调用。既有开发收益保留，评分适配、常数None及独立验证边界分别报告，另一会话的定向开发继续在原章节记录。

2026-09-16晚：[冻结验证后的定向开发已完成](#r1-postvalidation-refinement)：270次新调用，全部GPU/CPU任务结束。旧事实下限定问句的组合使33端21→28、25→33；新事实提取在两骨干及七方法真实R2回归均退步，不采用；广域删UNKNOWN因缺失相互作用等支持产生R1误伤。无目录单名诊断使47例canonical4→27、20→22，Llama23个修复均来自原已有目标的列表/命名/描述，进一步限定推理主张。保留窄范围组合候选，现有默认head与正式v5不变；本轮全部为已暴露开发。

2026-09-16后续：[R1冻结后验证与归因对照全部完成](#r1-frozen-validation-complete)，1660次新调用、630缓存回调，相关GPU与离线分析均结束。ASCENT47冻结头38/39，与单次目录总体同分；原生自由回答的单标签未映射不能当医学错误。用药33端程序21/25，优于同facts模型执行6/17，但独立临床来源仍缺失。关系201的普通重答→目标提示为M4 102→118、M5 120→122，M4有增量信号，M5未确认。现有头、标签和正式v5保持，当前证据支持有限组件，尚不足以支持泛用R1主张。

2026-09-16此前开发轮：R1诊断、用药、单选、关系实验及分析全部结束。[R1主候选完整交付验证](#r1-core-head-delivery)完成，2866×7输入的独立入口回放通过；七方法原正确861/898/766/798/819/858/901，head为1329/1323/1260/1225/1367/1317/1331。旧R3复用与新增范围贡献分别记录。单选完整202试验未采用；[关系201问句族](#r1-relation-extension-complete)的无旧答目标提示在两骨干均提升，额外删除检索无一致增量，保留范围内候选而未并入完整七方法头。本轮47434次已记录新调用，全部本任务GPU作业结束；成本、负结果、资源失败和未知原因中断均保留，正式v5不变。

2026-09-16：[R1头接续调查已完成](#r1-head-investigation)。已恢复指定对话的全部可读用户/助手正文，分工通读R2/R3主记录与运行文档，核查Delta系列及R1六来源的论文/公开代码，并离线重建2866单元的来源、重合和七方法成绩。确定先扩展冻结诊断头至另外1100题、有限用药规则至另外62题，再研究788题证据关系与原生单选缺口。本轮新增模型调用0；这是调查与后续方案，尚未完成R1头实验。阅读边界、来源版本、负结果及制品均见本节。

既有R2/R3完成状态（2026-09-15，Asia/Shanghai）：R3本轮寻找与交付已完成，原模型目录重决策头取得七方法共同提升，作为主要开发成果保留；额外NLI及三批新来源验证已收尾，当前无本任务GPU作业。独立接口、完成依据及泛化边界见[最终交付](r3_candidate_comparison.md#r3-head-delivery)。完整计划、负结果与结果归[R3主记录](r3_candidate_comparison.md)；此前病例标签直返头仍保留为有监督检索对照，见[自我反驳与取舍](r3_candidate_comparison.md#r3-head-self-review)。R2已形成独立支持重算接口及完整实验系列，现拆入[R2支持重算head主记录](r2_support_head.md)。当前选用版本、成功与失败、跨方法结果、成本和研究边界统一见[本轮交付](r2_support_head.md#r2-head-delivery)；其他head可参考[已提炼的构建经验](#cross-head-lessons)。

本文负责跨方向的文献取舍、研究问题定位、误差诊断与后续head探索。独立R2、R3方向的完整叙述分别在各自主文档续写；其他方向尚未形成独立实验系列时继续在本文记录。历史段落中的计划与“当前”按原阶段理解，不构成新的运行指令。

2026-09-16此前答疑：[当时R1结果的论文用途判断](#r1-paper-readiness)：可作为方法组件、迁移实验与主要开发结果；“泛用新增支持机制”的核心主张仍需冻结后的独立验证及相应归因证据。本文记录的是证据判断和后续优先级建议，没有启动新实验或改动已完成R2/R3的任务状态。

当前研究口径补充：允许在已暴露v5上继续开发提示、范围解析和决策策略，其方法价值由后续独立评测判断，见[开发数据与泛化证据](#development-generalization-boundary)。

2026-09-15补充：[历史Adapter对当前R1–R5的适用性](#adapter-current-classification)。可借用评分与融合组件，旧配对四选一实现不能原样作为v5方法；本次为适用性分析，未启动移植或新实验。

工作区总入口（本地来源：`/home/data3/txy/docs/README.md`） · [本次拆分记录](r2_support_head.md#r2-documentation-split) · 原文归属与初次迁移（本地来源：`/home/data3/txy/docs/workspace.md#documentation-migration-20260914`）

<a id="development-generalization-boundary"></a>

## 2026-09-14：开发数据与泛化证据的关系

用户进一步明确：根据已见测试题调prompt、判断问句范围或选择策略，本身不否决方法；若后续独立证据支持在相应类别上的泛化，这些组件可以采用并写入论文。接受这一研究标准。此前强调测试集复用的目的，是限定已有分数的证明力；若被理解成“用测试反馈开发过的方法一律无效”或“后续只能在公开train上开发”，则过度收紧，应按本节修正。

已暴露v5可以明确作为当前研究的开发范围，继续用于错误分析、提示和策略选择；它原先作为正式v5评测的数据身份及历史基线结果保留，不能抹去后续暴露记录。无需因其最初名为test而丢弃从中得到的方法，也无需为了开展开发试验等待全部新评测数据就绪。用于最终声明的独立评测则应与开发分开，在候选、配置及评分固定后检验，并据实际病例、模板与来源覆盖解释适用范围。后续若根据该独立评测错误继续修改，新版需要另有未参与调优的证据。

方法选择据收益及边界判断：prompt、手工规则、问句范围和选择策略都可以构成可复现的方法组件，不要求它们没有人工设计或必须算法原创。对R2，若冻结版本在新的病例、不同问句表达及撤销/仍有支持两侧，相对资源匹配对照保持增益，就可以按该验证范围报告方法贡献；当前79题和已修复合成探针继续标为开发证据。跨来源或临床泛化需有对应评测，本项目不将未经开展的更广验证设为所有窄范围研究结果的前提。

R3最近邻当前仍保留为监督检索对照，其核心方法定位的撤回还涉及未建立候选比较归因、额外资源和原方法被替代等原因，而非仅因测试集调优。未来若独立评测支持某种检索方法，应按实际方法身份和资源条件重新判断；不能以“曾经见过测试反馈”永久否决，也不能把开发高分自动升级为机制贡献。

本次只修正研究标准及R2/R3主记录中的相应表述，没有新模型调用、数据重划或评分变更。下一步开发和新评测准备可分别推进；尚不将任何泛化验证写为已完成。

## 内容导航

- [R1冻结后验证：完成结论与成本](#r1-frozen-validation-complete)
- [R1冻结后独立验证与关键归因对照](#r1-frozen-validation)
- [当前R1结果的论文用途判断](#r1-paper-readiness)
- [R1主候选完整结果与接口](#r1-core-head-delivery)
- [R1关系扩展、最终取舍与全部成本](#r1-relation-extension-complete)
- [R1错因诊断与实际方法试验](#r1-head-experiments)
- [R1头接续调查：历史、Delta与六来源方法](#r1-head-investigation)
- [历史Adapter对当前R1–R5的适用性](#adapter-current-classification)
- [其他head可参考的R2经验](#cross-head-lessons)
- [R3事实、候选比较与检索探索](#r3-start)
- [R2方法、成功与失败完整记录](r2_support_head.md)
- [论文贡献定位](#record-0139)
- [文献与服务器证据对照](#record-0255)
- [旧五方法分类表现与优先级](#record-0411)
- [旧R2章节链接](#r2-moved-sections)

<a id="adapter-current-classification"></a>

## 2026-09-15：历史Adapter对当前R1–R5的适用性

触发：用户询问旧CF-Residual Adapter能否用于当前分类。核对[分类定义](../data/classification.md#record-0253)、[v5可见信息](../evaluation/protocol.md#record-0190)和Adapter代码解释（本地来源：`/home/data3/txy/docs/archive/cf_residual_adapter.md#adapter-implementation-clarification`）。本次仅作方法适用性分析，没有新训练、推理或当前五类成绩，不将旧500对结果迁移为当前证据，也未决定恢复整套旧方法。

分类描述推理现象，本身不禁止评分融合方法；实际限制来自输入权限、题型及知识覆盖。旧方法同时读取control/trap/delta，并依赖构造的四选一诊断空间及DDXPlus疾病特征。当前原题与变体独立推理，不能额外读取隐藏参考病例、配对答案、分类标签或分类理由；题干原本给出的病史/前后状态仍可使用。旧选项构造使用两端诊断标签，不能在当前开放题中按gold补入候选。

可探索的最小迁移为当前输入内的候选评分：原生选项直接使用；开放诊断必须由固定目录或模型生成候选并测候选覆盖。把Profile改成当前患者事实与一般知识的匹配后，已不再是旧的control→trap公式；如尝试CPG，编辑只能来自可见题干，模拟编辑不等于官方前态或医学因果证据。评分归一化、线性融合和离线修复/误伤分析可借用，特征和系数需重新确定，不能沿用旧9维配置宣称可直接使用。

按任务含义判断：R3候选重新比较与旧评分路径最接近；R1可借用支持评分，但新增支持不等于确诊；R2须逐选项、逐规则处理支持及反证，允许多选并保留其他有效支持，四选一argmax不够；R4需要额外的前提到后果关系，仅似然变化不足以建立后果推导；R5应测无关变化下的正确性与保持性，不能默认复制另一侧答案。R1–R3可共现，类别用于离线分层，不能用隐藏类别标签选择推理分支。

若后续开展，最先候选是原生选择题上的单输入评分对照，按实际样本分层报告R1/R3及R5；至少比较原方法、额外评分路径单独、融合后的输出，以区分专家能力与融合增量，并计入额外评分成本。监督融合可以用明确开发数据拟合，已暴露v5也可标为开发范围；独立评测按病例组隔离，配对及同病例变体不跨开发/评测，旧实验暴露需计入。现有R2/R3开发候选保持原身份，这一分析不替代其结果或后续评测。

<a id="cross-head-lessons"></a>

## 从R2提炼的其他head构建经验

2026-09-14。以下是已有实验支持的设计判断与下一方向的候选用法；各项证据的完整主记录在[R2支持重算head](r2_support_head.md)。以下结论来自R2，不能代替R3等方向的独立验证；已开展的R3见其主文档，不为尚未开展的方向预建主文档。

**先定位要修复的环节，再选择干预。** R2同时出现过规则已在文献中却算错、把文献中的他人病例当患者、药物与规则错绑、解释与选择反向、问句范围错配。追加检索、加长推理和拆出动作映射各解决不同问题，不能把它们当可互换的“增强”。其他head可复用“当前事实—来源规则—目标候选—任务动作”的定位方式，具体机制仍须由本方向的实际错误支持。见[失败索引](r2_support_head.md#r2-failure-index)。

**明确head能改变什么，以及不知道时如何返回。** R2的完整重建、只删除旧选项、添加MET并继承UNKNOWN是不同决策政策。只删除无法补漏选；空规则、没找到文献或患者未提及不等于反证。R1的新增支持、R3的候选重排、R4的后果传播、R5的保持判断可分别据此界定操作范围；这些是后续设计方向，尚无跨类收益结论。见[R2方法定义](r2_support_head.md#r2-head-method-draft)。

**让模型承担可定位的事实提取，让程序承担明确的组合。** R2固定公开规则后出现双侧改善；句ID提高可追溯性，正向布尔表示加程序取反修复实际极性反例。可借用这一分工思想，但句ID存在不证明语义蕴含，规则也可能覆盖不全。事实来自当前患者，规则来自一般资料，两者的权限不能混同。详见[成功路径与新发现](r2_support_head.md#r2-development-lessons)。

**用有区分力的控制识别增益来源。** 普通局部复核增分但伤保留；充分thinking重答超过同配置条件提示；充分推理的同事实执行接近程序；仅MET与同覆盖总选None总分持平。这些对照分别排查额外计算、输入事实、最终政策与标签不平衡。后续head应选择能够改变本方向判断的控制，不固定复制整套实验菜单。见[预算控制](r2_support_head.md#r2-thinking-result)、[同事实执行](r2_support_head.md#r2-samefacts-reasoning)、[政策控制](r2_support_head.md#r2-selection-policy)。

**同时看修复、损伤和中间行为。** 79题总分会被66个None答案支配；整题exact match的0误伤也可能掩盖错误题中已正确选项被删除。原生无效、UNKNOWN、字段准确和最终答案是不同观察。未来按各类实际失败结构选择分层，不能机械套用R2的66/9划分。见[局部撤回中的真实误删](r2_support_head.md#r2-binding-failures)和[当前结果的限制](r2_support_head.md#r2-head-delivery)。

**拆开method迁移与组件复用。** 当前R2保留原模型权重，以两骨干实际生成事实、再与七方法原答案离线组合。原答案×提取骨干对照有助于定位继承与回退影响；它不是七个完整方法的新运行，也不能分离初答中所有检索与模型贡献。Qwen的覆盖外再答路由在Llama上频繁截断，说明默认策略需考虑原骨干的实际输出行为。见[交叉控制](r2_support_head.md#r2-scope-cross-control)、[路由试验](r2_support_head.md#r2-task-scoped-complete)。

**反例用于验证机制，独立数据用于扩大结论。** 简单虚构规则上两种提示都满分，不能区分真实医学规则的读取能力；新48题只有3个机制模板，一旦看过并据此改表示，就成为已暴露开发反例。其他head可从真实错误构造撤销与保留的对照，但模板变体不能算独立临床病例，也不能把gold或隐藏来源标签加进推理输入。见[初始规则探针](r2_support_head.md#r2-fictional-rule-probes)、[范围与正向表示](r2_support_head.md#r2-positive-facts)。

**失败要连同修正后的结论保存。** tuple/list错误使部分串联结果被低估，修复后必须撤回旧结论；共享显存初始化失败则不说明方法无效。保存实际请求、原始输出、冻结代码和评分版本，后续才可用离线重算替代重复生成。经验按已确认原因写，尚未解释的driver退出问题保持未确认。见[执行失败及恢复](r2_support_head.md#r2-engineering-failures)。

后续只有在某一head形成独立研究问题、具体实验系列和需要持续接手的结论后，再按AGENTS拆分标准（本地来源：`/home/data3/txy/AGENTS.md#documentation-growth`）建立其主记录；起步计划与单次摸索继续记录于本文。R2的完整实验历史统一续写新主文档。

2026-09-15，R3补充了两项跨head经验：原文引用可定位但仍可能不蕴含所判事实；合成训练中未生成某疾病—特征组合，也可能被统计程序放大为不适用于CF混合背景的强反证。该轮没有得到有效新头，完整数字、具体反例及实现修正统一见[R3事实与训练统计试验](r3_candidate_comparison.md#r3-empirical-feature-head)。其他方向引入知识组合前，应核对中间量的语义和来源生成机制。

同日后续，[R3事实接口对照](r3_candidate_comparison.md#r3-fact-scope-factorial)发现字段说明有局部作用，取消解码约束没有改变该批语义判断；R2式三值/句ID迁移也未形成两骨干共同收益。其他head可复用接口形式，但须重新验证其主体、时间和未知语义，不能继承R2的有效性结论。相关NLI文献的闭世界假设亦不能直接用于当前患者的未报告信息。

<a id="record-0139"></a>

## 15. 论文贡献定位：实现纠错、工程优化与研究候选（2026-09-13）

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md`），原文第635行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md`。

#### 15. 论文贡献定位：实现纠错、工程优化与研究候选（2026-09-13）

按当前证据，本轮还不宜把任何单项修复直接表述为已经确立的新算法贡献。以下是保守定位，不是穷尽相关工作的创新性审查。

| 已做工作 | 目前定位 | 可在论文中如何使用 |
|---|---|---|
| M4明确JSON、选项键、原生类型约束 | 任务输出适配与可靠性改进 | 实现细节/可靠性实验；承认原适配验证不足 |
| M4采用xgrammar/JSON Schema | 使用已有技术改进输出可靠性，改变解码过程 | 引用现成方法，作为对照或实现组件；不称发明约束解码 |
| M6带标题的单引号字典、显式诊断包装、Errors字段兼容 | 复现/任务适配缺口的修复，其中也有继承的上游格式假设 | 定义确定性后处理规则、保留原始结果、报告值保持和评分影响；当前代码本身不是强算法创新 |
| M6 formatter生成会改写既有答案的对照 | 有研究价值的经验发现 | 系统验证结构有效与语义保留的差别；当前52条证据规模不足以支持普遍结论 |
| M3 CPU熵向量化、PubMed偏移读取 | 标准工程优化/补齐既有机制所需数据 | 实现与效率附录，局部等价性、局部耗时；不能称改进推理算法 |
| GPU分片、批量、长度分组、缓存恢复、借用保护 | 执行系统工程 | 复现、资源管理和实测吞吐；当前缺少新的调度算法及受控系统评估 |
| M7动作解析 | 尚待核查 | 兼容实现有偏差则修复；模型缺动作则是真实协议失败，不先预设为bug |
| M7熵/最小步数/8步耗尽 | 当前方法机制的失败，尚未修复 | 先核实上游一致性；放宽阈值、增加预算等是新配置/方法变体，不是自动成立的创新 |

XGrammar已经研究高效结构化生成：[原论文](https://arxiv.org/abs/2411.15100)。JSONSchemaBench已经将schema支持、效率及下游任务质量作为结构化生成的评估维度：[原论文](https://arxiv.org/abs/2501.10868)。因此“使用JSON约束”“结构正确不等于任务正确”本身都不能声称为本工作首次提出。

有潜力继续研究的方向是：在医学多阶段任务中，将显式答案保留、可验证输出适配和完整失败分类做成统一协议，并通过多模型/多方法/独立数据验证其收益与边界。若原输出已经明确选择一个答案，仅执行可验证的表示转换；缺失或冲突则保留失败，不能用gold挑选。当前兼容解析只建立了有限样本的值保持证据，未形成普遍语义等价证明，也没有完成创新性审查。另一研究候选是基于TC状态轨迹的预算分配/停止策略，但目前没有设计或验证新策略，不能列入已完成贡献。

论文报告应区分原复现版本、修正后的基线和真正的新方法；先修复可确认实现偏差，锁定统一适配规则，再在独立数据上验证方法增益。不能将修复前被接口损失压低的基线作为唯一比较对象，也不能在同一测试样本上调规则后声称独立泛化。格式/协议有效率、原生正确率、显式答案保留率、失败覆盖和计算成本应分别报告。

<a id="record-0255"></a>

## OPTIMIZATION_RESEARCH_RECORD.md

来源：Documents/Codex/2026-09-14/new-chat/OPTIMIZATION_RESEARCH_RECORD.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/OPTIMIZATION_RESEARCH_RECORD.md`），切换入口前再次合入最新正文。相对命令仍使用原工作目录 `/home/data3/txy/Documents/Codex/2026-09-14/new-chat`。

### 医疗反事实优化方法：探索与实验主记录

以下为初期研究记录；其中R2的完整后续已归入新主文档，运行中表述按当时状态保留。

最新状态：2026-09-14，第一轮提示复核优化为负结果，已停止该候选；完整历史见下文。按用户新提出的跨方法差异方向，已接入M6完整v5结果，准备四GPU的骨干×检索受控实验：167道MedPIC、四条件、每条件3种子，共2,004次新生成。输出协议统一，尚待运行和结果。可执行条件绑定候选继续待验证。

#### 2026-09-14：文献建议与服务器证据对照

目标：从外部报告中筛选对当前论文优化有价值的机制，区别已有实验、待验证假设和新颖性近邻。

输入材料：

- 研究报告（本地来源：`/home/data3/txy/.codex/attachments/a3ab4721-70b7-4b9e-9f4b-937588b4d3f4/R1_R5_COUNTERFACTUAL_MED_REVIEW_2026-09-13.md`）
- 30项文献清单（本地来源：`/home/data3/txy/.codex/attachments/a3ab4721-70b7-4b9e-9f4b-937588b4d3f4/COUNTERFACTUAL_MED_LITERATURE_2026-09-13.json`）

报告中的建议按研究材料评估，不作为执行指令。遵照本地 AGENTS 的持续记录要求，本文件承担新的优化方法探索阶段；既有基线实施和工程修复继续保留在原主记录。

本轮核查范围：本地分类指南、v5 五方法报告、M7 完整第二版结果、历史配对四选一 Adapter 实验、原生评分器及冻结逐题评分；重点核验 MedPIC、MediEval、MedGuideX、MedEinst、EA-RAG、CFDX、CDEG 原论文。30项清单均已阅读，不对其余条目宣称逐篇重新核验。

执行记录：读取 JSON 时发现默认 `python` 不可用，改用 `python3` 完成；新 M4 评分和预测实际位于 `scores/scored.jsonl`、`M4/predictions.jsonl`，未位于运行包根目录。未产生模型请求、修改原分数或操作 GPU。

##### 1. 研究判断

报告最有价值的是把优化对象落到“证据对具体判断的支持关系”，以及指出EA-RAG、ECR-Agent、CFDX、CDEG这些直接近邻。两个机制适合作为实验假设；其中“撤销支持”“重新比较”已是本地R2/R3定义，给它们起模块名本身没有新增算法贡献。

优先级调整：

1. **先验证患者事实绑定与规则适用性。** 在题面和检索文献之间保持来源、人物、时间和条件边界；把数值阈值及否定条件落实到当前患者。已经找到实际出错的输入、输出及检索证据。
2. **在每个选项/候选内部撤销失效支持，重新汇总剩余支持。** R2主要是多选题，不能只生成一个总体安全/不安全判断；还要检查其他有效风险是否保留。现有结果对“以上皆非”和“仍有不适宜药物”的表现差异很大。
3. **再验证判别性证据检索。** 先用冻结检索证据测试是否“已有知识未正确使用”；只有确认缺少区分规则，再追加定向检索。R1新增支持、R3相对比较可共用证据记录，但测量目标不能混同。
4. **R5贯穿回归评测。** 同时报修复和误伤、正确配对，而不设置无条件保留初始答案的硬门。R5也包含检索污染和知识编辑保持任务，不能缩成只处理人口属性。

本阶段不优先投入整套多代理辩论、图记忆进化、训练流水线或医学影像生成。先回答最小机制是否解决已观察到的问题，再决定是否增加复杂度。

##### 2. 报告缺少的本地历史与最新结果

**CFDX/CPG已在本地借鉴过。** 历史CF-Residual Adapter使用了配对病例、DDXPlus Profile和CPG式编辑/似然评分。500对冻结四选一实验中，MA-RAG＋学习Adapter为80.0%，去掉MA-RAG为81.8%，Profile-only为79.4%；Adapter相对Profile的差值置信区间跨0。MA-RAG原生delta query在开发/校准上为+3.75/+1.33个百分点，full native为+0.25/+1.33；纯trigger与原基线完全一致。由此应降低“再做CPG＋融合/触发器”的优先级，也不能把历史结果概括成所有CF信号无效。该结果属于配对可见、固定四选一协议，当前v5采用独立输入及来源原生题型，数字不能直接转移。证据：历史方法与500对结果（本地来源：`/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md:1342`）。

**M7已完成。** 完整第二版TC-RAG于09-14完成全部13,905输入；R1/R2/R3/R4/R5/ALL分别31.44/29.11/28.92/30.77/66.17/49.43%。它更新了报告的比较范围，R1最高点估计也从M2的31.33%变成M7的31.44%；这0.11个百分点未经显著性检验，不作为优势证据。M6已换成MedGENIE并在运行记录中标记全量启动，不能继续用暂停i-MedRAG代表当前M6。证据：M7结果（本地来源：`/home/data3/txy/docs/baselines/tcrag.md#record-0403`）、M6运行包（本地来源：`/home/data3/txy/docs/baselines/medgenie.md#record-0398`）。本轮未监督或操作这些运行。

**部分建议已有基础设施。** 现有M2保留五候选、KGCC/KADS和重排；v5评分代码已输出R5配对正确性与一致性；历史Adapter已计算repairs/harms等指标。后续应复用这些接口，补齐新方法的成对比较，不重复搭建通用框架。证据：基线实现记录（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md:74`）、现有评分实现（本地来源：`/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured/code/analyze_v5.py`）。

##### 3–4. R2初始离线诊断与病例证据

完整正文已迁入[R2初始诊断](r2_support_head.md#r2-initial-diagnosis)，包括66/9分层、患者与规则错绑、数值及问句范围案例。

##### 5. R1/R3的诊断未映射：已有直接证据支持混合归因

从新M4的MedEinst、R3、非reference、`unmapped_diagnosis=true`的421个单位中，按unit_id排序后用seed=20260914无放回抽取24个。这里只检查输出和冻结诊断名称的关系，不是盲法临床语义重评，不估计全体“实际正确率”。

- `case_87004`和`case_7590`：gold为`Pulmonary embolism`，输出为`Pulmonary Embolism (PE)`，被判未映射。可直接看到括号缩写导致的名称匹配损失。
- `case_85920`：gold为`Bronchitis`，输出为`Tonsillitis`；`case_74253`：gold为`Pulmonary embolism`，输出为`Hypertrophic Cardiomyopathy`。这不是简单清理括号可以解决的差异。
- 另有`Possible NSTEMI / STEMI`与`Myocardial Infarction`、`Unstable angina`与`acute coronary syndrome`等粒度关系，需统一语义标准评估，不能按字符串相近直接补成正确。

原生诊断题型和官方诊断语义评价并不是同一概念。当前评分器使用冻结canonical名称匹配；未映射按错误计入主分数。报告强调unmapped需审计这一点值得保留，但后续应明确“本地冻结canonical分数”，不要让读者以为这是原论文官方语义评分。任何新增别名/语义评委只作为单列辅助分析，不能根据这24题修改历史主分数。

证据：24个随机样例及原始输出（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/audit_cases.jsonl`）、原评分器（本地来源：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/analyze_cf_baseline_screening.py:36`）。

##### 6. 文献取舍与需要收紧的新颖性判断

| 文献 | 本轮保留的价值 | 与本地证据相连的判断 |
|---|---|---|
| MedPIC（C02） | 患者条件激活/撤销风险的测试场景 | 优先做逐选项规则条件审计，但控制“以上皆非”分布和其他风险保留；它是基准，不是修复算法 |
| MediEval/CoRFu（C05） | 知识真实性与患者支持性分离 | 最贴合检索病例事实移植错误；训练部分暂留后续 |
| MedGuideX（C06） | 可执行规则及反事实监督 | 最贴合数值阈值检查；初期借鉴规则执行，不复制完整训练路线 |
| MedEinst/ECR-Agent（C01） | 患者Present/Absent/Missing与候选证据审计 | 三状态区分已有明确先例，不能声称新发明；图和记忆学习不是最小必要实现 |
| MamaBench/EA-RAG（C03） | 证据覆盖、对比子查询、错误模板 | 若加入判别性检索，应列为直接机制对照；外部病例能否作为新确认来源须先去重 |
| CFDX（C04） | 有限证据编辑与诊断偏好敏感性 | 本地已有改写及消融记录，优先复用历史经验；原文CPG跨候选绝对差定义不直接照搬 |
| CDEG（C07） | 缺失/忽略/阻止修订证据及选择性介入 | 已读取方法正文，重叠比报告摘要描述更直接；“有依据才改、否则保留”不能单独作为创新点 |

一手核验：

- [MedPIC](https://arxiv.org/html/2608.03028v1)明确用多选exact match，并报告风险激活、撤销及配对表现。
- [MediEval](https://arxiv.org/html/2512.20822v1)的CoRFu是在偏好目标中加入错误惩罚；定向Q1/Q2在其两骨干实验中比混合和课程更稳定。这里借鉴其患者支持性区分，不能把其四分类分数代入v5。
- [MedGuideX](https://arxiv.org/html/2605.26567v1)构造CF时丢弃执行结果不变样本；最佳报告组合是事实/CF混合SFT后接事实RL。若借其训练配方，本项目仍需另外保证合法保持样本。
- [ECR-Agent](https://arxiv.org/html/2601.06636v1)已区分肯定、否定和未提及，以训练集形成疾病图及示例库，并比较候选的判别性证据。
- [EA-RAG](https://arxiv.org/html/2607.14385v1)抽取参数、审计覆盖、生成对比查询，并使用错误分类推理模板。“分类错误后针对性RAG”已有直接工作。
- [CFDX](https://arxiv.org/html/2603.27820v1)的方法公式比较原诊断与编辑后生成诊断的概率差并取绝对值；若借鉴敏感性信号，应固定同一候选概念、保留方向并控制名称长度，而不是把它视为临床因果效应。
- [CDEG](https://arxiv.org/html/2608.22899v1)第Selective Intervention节明确：当前证据仍支持来源诊断时不沿该修订边介入；否则分别引导补采或重审。它还记录blocking evidence和修改适用性。正文说明图构建病例与评测病例隔离；本轮未核查其代码执行是否落实全部声明。

其余23项保留在文献背景/候选来源：C08/C09为后续R5偏好或聚合对照；C10/C17用于检索污染与题设语义边界；C11、C12–C16、C18/C19用于鲁棒性背景及可能的确认数据；C20/C21、F01–F03用于R4/因果边界；M01–M06为跨模态参考。本轮不将它们排成23个待实现模块，也没有逐项重新核实实现可用性。该处C/M为附件文献ID，与服务器数据集ID或基线方法ID不同。

##### 7. R2早期实验计划

原计划及后续范围调整保留于[R2早期计划](r2_support_head.md#r2-initial-plan)和[完整实验历史](r2_support_head.md#r2-history)。

##### 8. 本轮状态、验证及限制

- 已完成：两份附件全部读取；本地规则、历史Adapter和最新六方法结果核对；7篇核心论文的方法文本核验；450条已有MedPIC/R2方法评分离线分类；421条新M4/R3未映射池中固定抽24条；10条新M4/R2示例抽查；3条真实归档prompt保存，其中2条完成具体来源/数值核对。
- 验证：脚本内检查每方法恰好75个不同单位、每题为multi、错误分区合计75、66/9参考答案分组、所需3个prompt均存在。脚本运行完成，无模型或检索请求；额外医学知识查询未用于改写gold。
- 尝试：先生成基础错误分解和24条样例，再补充“以上皆非”分层及各分层无效数，重跑同一离线脚本。每次执行为秒级CPU工作，最后一次工具记录约2秒；未记录CPU/内存峰值。读取默认路径缺失后按RESULTS纠正路径，不涉及结果丢失。
- 已产物：脚本（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/audit_existing_results.py`）、结果JSON（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/offline_summary.json`）、执行输出（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/audit_execution.log`）、案例JSONL（本地来源：`/home/data3/txy/Documents/Codex/2026-09-14/new-chat/audit_cases.jsonl`）、上述3个prompt JSON及本主记录。复查命令：`python3 /home/data3/txy/Documents/Codex/2026-09-14/new-chat/audit_existing_results.py`。
- 限制：本轮不是全仓库逐文件审计，也不是30篇论文完整复现；原始输出抽查不建立错误机制总体发生率；所有临床gold保持原状。v5已经参与开发决策，后续在v5提高分数不自动构成独立泛化证明。未启动新推理或训练、未修改冻结数据/评分器、未操作现有GPU作业。新方法是否有效与是否有足够新颖性均待实验及进一步近邻比较。

<a id="r2-moved-sections"></a>

## R2历史章节已迁出

2026-09-14：本方向完整迁入[R2支持重算head](r2_support_head.md)，包括失败与更正；[拆分说明与备份](r2_support_head.md#r2-documentation-split)。以下锚点只为既有引用导航，今后续写新主记录。

<a id="r2-independent-interface"></a>

[r2-independent-interface](r2_support_head.md#r2-independent-interface)

<a id="r2-head-continuation"></a>

[r2-head-continuation](r2_support_head.md#r2-head-continuation)

<a id="r2-head-current"></a>

[r2-head-current](r2_support_head.md#r2-head-current)

<a id="r2-executable-rule-head"></a>

[r2-executable-rule-head](r2_support_head.md#r2-executable-rule-head)

<a id="r2-native-answer-type-fix"></a>

[r2-native-answer-type-fix](r2_support_head.md#r2-native-answer-type-fix)

<a id="r2-task-scoped-complete"></a>

[r2-task-scoped-complete](r2_support_head.md#r2-task-scoped-complete)

<a id="r2-all-methods-scoped"></a>

[r2-all-methods-scoped](r2_support_head.md#r2-all-methods-scoped)

<a id="r2-evidence-first"></a>

[r2-evidence-first](r2_support_head.md#r2-evidence-first)

<a id="r2-selection-policy"></a>

[r2-selection-policy](r2_support_head.md#r2-selection-policy)

<a id="r2-scope-cross-control"></a>

[r2-scope-cross-control](r2_support_head.md#r2-scope-cross-control)

<a id="r2-evidence-scope-complete"></a>

[r2-evidence-scope-complete](r2_support_head.md#r2-evidence-scope-complete)

<a id="r2-positive-facts"></a>

[r2-positive-facts](r2_support_head.md#r2-positive-facts)

<a id="r2-head-delivery"></a>

[r2-head-delivery](r2_support_head.md#r2-head-delivery)

<a id="r2-head-method-draft"></a>

[r2-head-method-draft](r2_support_head.md#r2-head-method-draft)

<a id="七方法离线分析完成"></a>

[七方法离线分析完成](r2_support_head.md#r2-seven-method-diagnosis)

<a id="record-0411"></a>

## README.md

来源：Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/README.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/README.md`），原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority`。

### v5 M0/M2/M3/M4/M5 分类表现与优化优先级

**最新五方法总表（2026-09-13，新M4全量修复版）：[M0/M2/M3/新M4/M5 v5 benchmark](../evaluation/v5.md#record-0410)。本页原M4数值及图表保留为历史版本；当前比较请使用新总表。**

2026-09-13。使用五方法已完成的原正式v5结果，各13,905独立输入；不混入M4/M6修复试验、不加入M6/M7未完成结果。分类均沿用冻结evaluation_labels。

!五方法分类表现（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/v5_category_comparison.png`）

主图PDF（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/v5_category_comparison.pdf`） · 主图SVG（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/v5_category_comparison.svg`） · 完整精度CSV（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/category_scores_merged.csv`）

#### 分类总表

主指标：单元内非reference原生任务正确率平均，再对类别内单元等权；分类总体表现取五方法等权均值。均值不是新模型的分数，也不是投票集成准确率。

| 类别 | 单元数 | M0 | M2 | M3 | M4 | M5 | 五方法均值 |
|---|---:|---:|---:|---:|---:|---:|---:|
| R1 新增支持 | 2866 | 30.04% | 31.33% | 26.73% | 21.53% | 28.58% | 27.64% |
| R2 撤销支持 | 79 | 8.86% | 7.59% | 34.18% | 6.33% | 41.77% | 19.75% |
| R3 重新比较 | 733 | 17.87% | 24.69% | 8.59% | 14.32% | 25.24% | 18.14% |
| R4 推导后果 | 13 | 38.46% | 53.85% | 38.46% | 23.08% | 53.85% | 41.54% |
| R5 保持判断 | 3600 | 65.70% | 65.88% | 73.37% | 39.63% | 63.42% | 61.60% |
| ALL 整体（去重） | 6104 | 48.10% | 48.81% | 51.61% | 29.76% | 47.35% | 45.13% |

按原始平均分从低到高：**R3（18.14）→R2（19.75）→R1（27.64）→R4（41.54）→R5（61.60）**。排除M4后分别为19.10、23.10、29.17、46.15、67.09，排序相同。因此排序并非仅由M4格式损失造成，但不能据此排除其他方法的评分/格式混杂。

类别可重叠，ALL对6,104单元去重，不是五类别均值。R3的733单元全部包含于本次R1集合，不能将两类改进当成独立验证。R4为13个单元的作者预期答案一致率。这里只描述点估计，不声称R3比R2在统计上显著更难。

#### 低分原因决定优化类型

!错误构成（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/v5_category_error_decomposition.png`）

错误图PDF（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/v5_category_error_decomposition.pdf`） · 错误分解CSV（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/loss_decomposition.csv`） · 逐方法分解（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/loss_by_method.csv`） · 来源构成（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/category_source_counts.csv`）

分解使用与主分数相同的任务→单元→方法权重，每行合计100个百分点。不是原始请求计数。

| 类别 | 原生正确 | 有效但错误 | 诊断未映射 | 格式/终态无效 |
|---|---:|---:|---:|---:|
| R1 | 27.64 | 24.04 | 42.34 | 5.98 |
| R2 | 19.75 | 63.54 | 0.00 | 16.71 |
| R3 | 18.14 | 12.44 | 63.30 | 6.11 |
| R4 | 41.54 | 43.08 | 0.00 | 15.38 |
| R5 | 61.60 | 28.32 | 0.00 | 10.08 |

“诊断未映射”可能是错诊、过泛标签、别名或包装差异，不能直接判为语义正确或将这些分数加回。必须先做规则固定、独立复核的误差审计。“格式/终态无效”按原评分字段定义，也包括含糊诊断和M3流程失败被序列化为空答案，不全是JSON语法错误。

#### 推荐的研究顺序

**表现筛查顺序是R3→R2→R1；实际工作分两条线推进。**

1. **优先排查R3，并与R1一起校准诊断输出及评分口径。** R3五个方法都不超过25.24%，但63.30个百分点为诊断未映射；680/733（92.8%）来自MedEinst。R1也有42.34个百分点未映射，且包含全部R3。先区分错诊与表示不兼容，建立可信基线后再判断“重新比较候选”是否为共同推理短板。此处的评分/格式修正归为评测可靠性，不能冒充新推理方法。
2. **优先在R2验证真正的推理优化假设。** R2有63.54个百分点是有效但错误，未映射诊断为0，更适合检查支持条件撤销后是否仍沿用旧结论、是否未移除失效候选。以上是待验证机制，不能仅凭低分宣布根因。R2仅79单元，75（94.9%）来自MedPIC-Bench；应增加独立来源/病例验证，避免只学会某种多选任务格式。M3/M5为34.18/41.77，Llama三方法仅6.33–8.86，还需控制骨干差异。
3. **统一方法候选覆盖R1/R2/R3，R5作为保持能力检查。** 可研究“证据变化与候选支持更新”：在可见输入中识别相关且可信的新证据、失效支持与不相关变化，据此重新比较候选；对无关或不可信扰动避免不必要改判。不能把所有给定错误证据当真实事实，也不能在没有正式题对时向模型提供额外前后样本。这目前是研究假设，尚未实现或证明新颖。分类标签仅用于离线分析，不作为推理时的oracle路由输入。
4. **R1作为较大规模的联合验证范围。** 有2,866单元，可检验统一方法能否利用新增支持，同时报告来源/题型分层，避免诊断任务占比支配结论；R3是其子集，不能重复累加样本量。
5. **R4暂不作为主攻方向；R5不作为当前最弱类别，却必须保留。** R4只有13单元且仅一个来源，当前无法支持稳定的跨方法结论。R5有3,600单元、8来源各450，适合检验“该保持时是否保持”，防止优化R1–R3时变得过度改判，也会显著影响ALL。

若只选一个原始低分类别深入：先选R3做诊断审计。若马上要设计一个可验证的推理机制：先以R2的“撤销支持”做小规模机制实验，再联合R1/R3验证，并以R5检查是否引入副作用。两种优先级不冲突，分别对应测量排查和方法研究。

#### 研究约束与复现

不能仅从分类均分断言具体认知机制故障：当前指标是原生任务正确率，不是直接监督“支持关系更新”的独立金标。需要抽查同题过程及候选依据，并控制骨干、输入、计算预算和输出适配。五方法中的Llama/Qwen、检索语料、多轮预算不同，均值反映这组具体系统，不代表模型总体。

该v5结果已用于发现短板，后续新方法需在独立开发/验证划分上调规则，保留按病例/来源分组的独立测试，不能继续在同一批公开分析样本上反复调优后宣称未见测试增益。没有新增显著性或置信区间分析。

构图与汇总脚本（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/build_report.py`）从原始CSV及scored.jsonl重建图表；验证收据（本地来源：`/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/v5_category_priority/validation.json`）确认25个方法×类别分数与错误分解一致、每行分解合计100。仅离线读取，不重跑生成、不改评分。PNG/PDF/SVG和完整精度CSV均已导出。

分类语义依据原分类说明（本地来源：`/home/data3/txy/docs/data/construction.md#record-0349`）：R1新增支持、R2撤销支持、R3重新比较、R4推导后果、R5保持判断。


<a id="r3-start"></a>

## R3独立研究入口

2026-09-14：R3候选比较与临床查询已形成独立研究问题、接口和实验系列，全部启动计划、审计、报错、负结果、反例及后续对照整体迁入[R3主记录](r3_candidate_comparison.md#r3-start)。复核/查询的负结果和最终训练病例记忆头的确认结果均保留；当前实验状态和后续完整叙述只在该文续写。[拆分说明与备份](r3_candidate_comparison.md#r3-documentation-split)。

<a id="r1-head-investigation"></a>

## 2026-09-16：R1头接续调查

**启动时记录（现已完成调查，见下文）。** 研究对象为冻结v5的R1新增支持，不改变既有分类、原生任务或正式成绩。用户指定完整阅读对话`01a09dd7-8667-7ab0-8a9e-7051b56031e7`及R2/R3相关记录，追查被遗忘的Delta模块，并逐一核查R1来源论文和公开实现。原对话位置为`/home/data3/txy/.codex/sessions/2026/09/14/rollout-2026-09-14T10-55-42-01a09dd7-8667-7ab0-8a9e-7051b56031e7.jsonl`。本轮分工阅读历史、R2/Delta、R3及来源研究，保留阅读覆盖与证据位置；不把程序扫过文件等同于逐段阅读，不将摘要当完整原文。

依据已有`v5_category_priority/category_source_counts.csv`，R1共2866单元：MedEinst1780、MedCounterFact788、AMQA134、MedPIC96、Cultural67、CPV1。R3共733单元且全含于R1；后续须分别呈现重合733与R1其余2133，不能将两者计作独立验证。接下来离线核对冻结成员、已有各来源成绩及现成head覆盖，并核查六来源论文/代码。原始证据、阅读索引与离线结果集中放入`Documents/Codex/2026-09-16/r1_head_investigation/`；完整研究结论仍在本节续写。

### 调查完成：阅读范围与继承的决策

上述启动工作已完成；以下为本次新增结论。证据包为r1_head_investigation（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/README.md`），不是新的长期主记录。

指定会话113,391,220字节、18,231事件；去重后的520条用户/助手正文（含18条实际用户消息、3条目标及一条仅存event的助手消息）全部按时间阅读，1952次调用/结果全量建索引，相关工具输出回到原记录追证。阅读不是只看最后一条总结。R2主文1704行、61份R2运行文档、最终8模块670行；R3主文1917行、75份R3运行文档、最终11模块865行均分工全文阅读。Delta试验748行、Residual Adapter1364行归档全文阅读，DeltaRank530行实现及DeltaRev/后续分支相关实现核对。另完整阅读原会话两附件，并核对来源、构建、协议与分类的有关章节。逐项清单和旧错误定位见历史覆盖（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/history/README.md`）、历史决策索引（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/history/findings.md`）、R2/Delta阅读附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/r2_delta_medpic_cpv_review.md`）、R3阅读附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/r3_review_notes.md`）。工具输出约1319万字符未全部逐字重读；31次加密压缩正文不可读，171条旧输出本身带截断。不能将本轮表述成113MB每一字符均已读完。

原会话已明确三项后续标准：沿用各方法自己的模型与实际流程上下文；允许借现成方法，不要求算法原创；已暴露v5可以用于开发，开发有效与独立泛化分开判断。R3七方法共同提高已经完成当时寻找有效头的目标，不能再因未到90%、方法差距未缩小或校正组件不是每骨干都提高而改写成“没有成果”。本轮R1接续从这一已完成结果出发。

### 冻结范围与已有成绩的离线重建

读取正式`items.jsonl`、`evaluation.jsonl`和当前七方法评分，按`evaluation_labels`选R1、排reference。2866单元恰各有一个非reference原生任务；未增加任务或修改评分。R3 733全是R1子集。本轮重建与正式七方法R1全精度均分一致，逐条核对既有R3头中的原正确性与正式基线一致，才做重合贡献计算。脚本、输入路径和核对目的见analyze_existing.py（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/analyze_existing.py`）、provenance.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/provenance.json`）。

| R1来源 | 全部 | 与R3重合 | 其余 | 原生任务与现有接口 |
|---|---:|---:|---:|---|
| M01 MedEinst | 1780 | 680 | 1100 | 开放诊断；全部落在现49疾病目录范围 |
| M02 MedPIC | 96 | 10 | 86 | 多选用药；72符合现R2接口，其中62在R3之外 |
| M12 AMQA / FairMedQA | 134 | 43 | 91 | 单选；现R3入口对这类保持原答 |
| M10 CPV | 1 | 0 | 1 | 单选；单例不足以评估该来源普遍收益 |
| M11 Cultural | 67 | 0 | 67 | 单选；现头保持原答 |
| M20 MedCounterFact | 788 | 0 | 788 | 给定证据的四类关系判断；现头未优化 |
| 合计 | 2866 | 733 | 2133 | 不能把R1与R3样本数相加 |

现有两个有效干预分支在接口上可覆盖1852/2866（64.62%）＝1780诊断＋72规则多选。其中旧R3实际干预过680＋10＝690题；另43单选只是透传。**接口覆盖1852不等于已经在1852题证明有效。** 尚无对应干预分支的1014题＝24未覆盖多选＋202单选＋788关系。

新1100诊断覆盖30种gold病种，旧680仅9种；全部gold在现公共49目录及冻结46标签评分词表内。前三种Bronchitis321、COPD161、NSTEMI/STEMI117合599/1100，必须同时报告病种宏平均。原七方法在1100题仅43/29/14/33/34/31/36题正确，即1.27%–3.91%；“未映射诊断”609/742/876/818/804/787/823。种子20260916固定抽12条M4原答，读到Myocarditis→Centipede bite、Anemia→Panic disorder等明确不同标签，也有答对与表述含糊，说明不能把全部未映射当别名自动加分；这12条不是临床金标重审或总体错误比例估计。目录与暴露检查（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/diagnosis_scope_check.json`）、原答抽样（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/r1_diagnosis_sample.jsonl`）。其中813/1100有更早CF研究暴露记录，全部已有v5结果。

其余来源的七方法原生正确率范围：MedPIC全96为30.21%–52.08%；AMQA全134为52.99%–71.64%；Cultural67为89.55%–98.51%；CPV1全部错；MedCounterFact788为51.02%–67.13%，各方法无效仅0–14，主要是有效但错误的关系判断。故诊断扩展与证据关系比对已经接近满分的文化题统一重写更有研究空间。完整按来源、方法、R3重合分层见source_scores.csv（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/source_scores.csv`）。

仅将**已知R3成员**的现成输出离线替入R1总数，可以量化已取得成果的贡献：

| 方法 | 原R1正确/2866 | 旧R3带来的净增 | 离线组合正确/2866 | 对应百分比 |
|---|---:|---:|---:|---:|
| M0 | 861 | +207 | 1068 | 30.04→37.26 |
| M2 | 898 | +159 | 1057 | 31.33→36.88 |
| M3 | 766 | +175 | 941 | 26.73→32.83 |
| M4 | 798 | +163 | 961 | 27.84→33.53 |
| M5 | 819 | +258 | 1077 | 28.58→37.58 |
| M6 | 858 | +148 | 1006 | 29.94→35.10 |
| M7 | 901 | +137 | 1038 | 31.44→36.22 |

该表是已知重合集合的**历史结果记账**，不是运行时按R3标签选择方法，不是自动路由在完整R1的新成绩；不能替代1100/62题扩展。其新增模型调用为0。完整精度及身份字段（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/existing_r3_contribution.csv`）。

### 找回Delta系列：可借什么、为何不能原样恢复

“Delta开头”并非一个模块。最早至少有DeltaRev与DeltaRank，之后Profile/CPG/Residual Adapter延续了差分打分；另有R3训练病例的delta-memory试验。完整历史仍分别归CF方法试验（本地来源：`/home/data3/txy/docs/archive/cf_method_trials.md`）、Residual Adapter（本地来源：`/home/data3/txy/docs/archive/cf_residual_adapter.md`）、[R3病例记忆](r3_candidate_comparison.md#r3-start)，这里记对R1的新增适用性判断。

| 历史路线 | 已有结果与实际输入 | 本次取舍 |
|---|---|---|
| DeltaRev | 200配对MedEinst，40开发/160测试；baseline与full均9.38%，0修复0误伤；规则抽取失败72.74% | 不是遗忘了一条已证明有效的修复路径；不作为R1默认头恢复 |
| DeltaRank | 300开发＋300测试，49目录top10重排及四选一残差；测试45.33→46.33%，5修复2误伤，开发净负 | 只能说局部小收益；评分/候选约束可参考，不能将差分本身当稳定有效机制 |
| 后续Profile/CPG | 典型分数为`2 logp_trap(a) − logp_control(a) + 2 z(delta匹配)`；CPG依官方pair.delta恢复/删除/否定前两条发现 | 旧任务显式用两端及编辑元数据；当前原生单输入不拥有这些字段 |
| Residual Adapter | 500对MA+learned80.0%，独立训练的without-MA配置81.8%，Profile79.4%；相对Profile的区间跨0 | 不等于已经移植到七原方法，也不等于从一个冻结网络关掉MA就提升；不先为R1重新训练 |
| R3 delta-memory | train差分/近邻病例曾有高分，但最近标签直返更强，近模板监督是主要资源 | 保留监督检索对照身份，不重新包装成原模型支持推理 |

代码还确认旧DeltaRank候选四选一由trap/control gold加两个困难负例构成（`run_deltarank.py:prepare`）；这在当时配对实验里有明确协议，移入v5会改变输入权限。旧“fresh”排除未完全覆盖DeltaRev及旧cal尾部，保守491组结果和完整暴露沿革已留在Adapter归档，不能当今天新独立测试。

能移植的是同一候选下的log-prob评分、名称规范、目录/额外调用匹配对照，以及固定后比较增益的实验方式。若以后只从当前输入做暂隐/自造反事实，其身份是模型自行构造的干预，不能假称拿到了真实pair.delta，也不能将概率变化自动解释成临床因果支持。此前R3的实际暂隐、CAD和反向病例似然已经给出负结果，暂不重复开展。

### 六个benchmark原论文与公开实现逐项调查

截至2026-09-16核对官方论文、实际仓库树及相关代码；取得源码与证明优化有效分别判断。固定提交和本地快照见证据包`sources/`，论文/代码版本不替换冻结v5数据。

**M01 MedEinst：确实提出ECR-Agent，但目前不能直接运行作者实现。** 最新[ACL论文](https://aclanthology.org/2026.acl-long.1847.pdf)给出DCI事实/候选流程、General/Pivot等关系、分层审计与CGME纠错记忆。它使用Qwen3-32B、GPT-5 critic、853训练种子、最多三轮纠错、PubMed/OpenTargets等资源，不是简单把每条支持＋1。论文称代码公开，而[官方仓库](https://github.com/zhui711/MedEinst)实际完整树仍只有网站等文件、README写Coming Soon。可参考算法和附录提示；当前本地8B关系表失败不能叫完整ECR复现失败，亦不能用近邻答案直返冒充ECR。当前优先复用已交付目录头；需要ECR时另列资源明确的重实现对照，不先等待缺失代码。

**M02 MedPIC：MedRule2Pair是出题流程，不是答题修复头。** [论文](https://arxiv.org/html/2608.03028v1)用规则构造只在关键条件上不同的题对，评测时每端独立呈现、不告诉配对关系。[官方HF](https://huggingface.co/datasets/TIM0927/MedPIC-Bench/tree/main)固定revision只有README、questions.json等三个文件，没有完整规则库、生成实现或优化头；公开PDF/HTML提到supplement但本次未取得完整补充提示。最有用的联系是本地R2已实现的规则重算，它既能撤销也能激活支持，直接按现72题资格扩展即可；不能照论文名字假设剩余24题规则已经具备。

**M12 AMQA / FairMedQA：有攻击生成和评测代码，没有已验证的通用修复头。** [AMQA v1](https://arxiv.org/html/2505.19562v1)与同号[FairMedQA v2](https://arxiv.org/html/2505.19562v2)是版本沿革，不是两个R1来源。[公开代码](https://github.com/XY-Showing/AMQA)中`no_cot/cot1/cot2`可直接提取为原模型提示对照，cot2加“忽略非临床信息”；生成环节最多三次，gold用于构造攻击，不能进入优化推理。作者保持临床答案不变的构造目标，不等于本地每条新增叙述都无临床影响；治疗环境/访问条件须结合题目判断。1273→801的过滤是题目资格，不是按求解器答对筛简单题。另篇2507.15337的延迟选项方法已在R3试过、没有共同收益，不与AMQA混写。详见原文、代码和附件复核（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/history/amqa_and_attachment_review.md`）。

v2全文补查发现另外发布的[Zenodo复制包](https://zenodo.org/records/18146153)，已取得并读完375行评测脚本；其中有`naive/role/aware/few/cot/mix`六种提示，比旧GitHub提供更多可用控制。正文及133行结果CSV没有六策略比较，故代码存在不等于作者证明有效。aware/mix全面去人口属性权重仅适于实际符合答案不变条件的题；few带两个同选D的示例，确切短语在该801种子无命中仍不能证明跨USMLE独立。v2主文GPT-4o与附录/代码GPT-4.1＋mini的生成版本不齐；评测脚本还存在provider分支不齐、回退逐字符抓A–D、温度参数未传等实际问题。后续只借提示/输入组织，沿用本地原模型callback和严格评分。新增快照与差异证据已保存在同一阅读附件。

**M10 CPV：确有缓解策略，但训练和输入不适合原样接头。** [NAACL正式论文](https://aclanthology.org/2025.naacl-long.114/)比较普通提示、假设反事实背景、CoT及GPT-4o-mini微调（MCQ1409、XPL4044训练例），部分性别偏差降低会伴随族群方向退步，没有统一最好策略。[官方仓库](https://github.com/kenza-ily/diagnose_treat_bias_llm)有提示/评测和私有ft模型ID，没有公开对应训练流水线与完整训练样本；当前MedQA/MedMCQA/PubMedQA接口与论文JAMA来源还须区分。XPL提示的SOLUTION字段直接给正确答案，不能用于当前无标签作答；想象未提供背景也不等于使用当前新增事实。本地仅1题，先纳入原生单选统一比较，不为它单建训练工程。

静态核查还发现当前CPV人口替换没有实现文档声称的整段代词替换，可保留旧man/woman；GenderBias默认度量`case_text`而非模型解释。它们会改变数据/指标含义，故本轮不直接运行上游生成器或复制其评价；不修改上游工程，具体位置见R2/Delta/来源附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/r2_delta_medpic_cpv_review.md`）。

**M11 Cultural：有清晰控制设计和推理脚本，没有专用去偏头。** [论文](https://arxiv.org/html/2601.20102v1)区分身份、社会情境、二者组合，并给长度匹配中性控制及仅选项/简短解释设置；[作者代码](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs)是这些条件的普通生成。解释条件剔除不完整答案导致147与150等分母差异，不能在本地照搬成丢弃无效输出。可借等长度和等调用控制；不可一律删掉年龄、家族史、经济访问限制，也不可凭群体身份补未提供的个体事实。当前67题已有高准确率，优先检查误伤与保持，不强制施加昂贵重写。

**M20 MedCounterFact：最值得新增的是问句目标与给定证据的绑定。** [正式论文](https://aclanthology.org/2026.findings-acl.1847/)比较无证据、给定证据、专家措辞、怀疑措辞和CoT/no-CoT，任务输出Higher/Lower/No Difference/Uncertain。专家措辞无明显修复，怀疑措辞增加不确定回答，不能直接称成功头；证据遵循分数也不等同真实临床安全。[官方仓库](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence)目前公开数据/格式说明，推理代码仍待发布。作者2026年3月修正数据的沿革不自动覆盖本地冻结788单元。

进一步追到其上游[MedEvidence论文](https://arxiv.org/abs/2505.22787)与[官方代码](https://github.com/zy-f/med-evidence)：这里实际有`SimpleClosedRAG`、问题定向逐篇摘要、证据质量提示及长文refine链。最小可借的是“明确问句的治疗A/对照B/结局/人群，再从当前证据回答四类关系”的提示和原模型回调。逐篇摘要与长文链是可比较选项，不是预设必要模块；先复用给定证据，不增检索库或复制整套LangChain依赖。上游单篇一致性提示另有统计显著性/Insufficient Data规则，不能未经任务核对直接代替本地多篇四类评分。

一个当前输入实例是M20:2:variant_1，问MS中的医生印象认知改善；证据同时含主要结局无效、次要医生印象和另一研究结果。它提示应绑定**具体结局与研究范围**，不能见“主要结局无效”就把问句所指次要结局也判无差异，更不能按支持论文数量投票或把任意单个p值阈值作全局规则。此处是任务结构例子，不是已完成788题错误归因或新头结果。

### R1接续方案：先复用，再补真正缺口

方案状态为**已确定、未启动推理**。不需要六个来源各建一套代理；保持一个薄入口，按原生`answer_format`和可见题目条件选适用支路。来源编号和R标签只用于离线分层，不进入推理路由；原模型、原生题目/选项/固定证据及原方法实际上下文都保留。

1. **先完成诊断分支的同域扩展。** 直接将冻结`r3_optimization_head.py`应用到另外1100 MedEinst诊断；先M4/M5、随后七方法。固定49目录、六排列、原提示/模型及先验组合，同时报告原答、单次order0、未校正票、校正票；后三者可由同批分布离线计算。目录与模板相同的无内容先验可复用，不能按R1 gold重估。预算1100×6×2＝13,200条患者评分，两骨干；七方法46,200条，完全同请求可减少，缺失候选码补评分另计。M6/M7须保留原status验收与真实最终上下文，先逐项复现基线再归因修复。详细准备契约见R3阅读附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_investigation/r3_review_notes.md`）。
2. **冻结R2规则扩展新增支持。** 现72道可适用MedPIC中10道已有R3实验，另外62道按两原骨干最多124次事实生成，完全同请求的旧缓存核对后复用；用各方法原答案离线组合时如实标注调用身份。状态执行是`MET ∪ (原选择 ∩ UNKNOWN)`，因此支持成立时加入，不只是删旧选项。报告全96、覆盖72和未覆盖24，以及新增、保留、撤销与误伤；未覆盖部分保持原答。若要增加规则，必须有真实错题和相应公开指南，不先大规模生成医疗规则图。
3. **关系任务从作者原生提示对照开始。** MedCounterFact788在保持原模型/上下文下，先设一次直接重读四类判断的等调用控制，以及单次明确A/B/结局/人群范围的判断提示。先在事先固定的小开发子集核对具体错因，再决定是否值得增加一次结构化目标提取；本轮不预报新增模块收益。若两阶段版本需要两次调用，对照也匹配两次预算。当前给定证据按来源的假设世界理解，不用真实药物知识把替换实体擅自改回去。最终输出继续使用本地四类规范，不重定义评分；缺证据与无差异保留区别。
4. **原生单选202题单独评估。** AMQA134＋Cultural67＋CPV1，其中43曾进入R3但原样透传。优先保留完整题目和选项，在原模型追加一次目标明确的重决策（问诊断、机制、处置或事实），并以作者naive/简短cot做等调用控制；旧cot2与新版aware仅在满足其信息不变假设的分析范围比较，不直接把六种策略全部扫一轮。无需再试已经失败的先隐藏选项再映射。Cultural用同一冻结流程检查误伤，不按来源单独挑最优prompt；出现具体保留/删除事实错误后再决定是否增加筛选。仅1道CPV不形成专属方法结论。
5. **汇总和完成标准。** 固定版在完整2866及六来源报告原生准确率、repair/harm、无效、覆盖，诊断另报病种宏平均；旧重合733与新增2133分开。R5保留题用于评估误伤，不以R标签作运行开关。有效开发提升即可作为相应范围的结果交付，不追加未经约定的90%门槛或要求每个附加组件都提高；无效分支记录并停止。更广泛独立结论另用未参与开发且符合R1新增支持语义的病例/来源，不把普通诊断集、同v5扩展或历史CF尾部冒称独立R1。

### 直接继承的失败教训与本轮限制

R2曾因tuple/list解析错误低估同事实LLM，修复后Qwen43/79对程序44、Llama35对34；故运行前先保证原生解析与基线逐项一致，不凭坏控制宣称程序优势。R2现在的有限规则组合成功仍成立，但句ID存在不保证语义正确，UNKNOWN不是false，多路径中一条撤销也不使全部支持失效。R3已经实际尝试过反事实暂隐、逐候选真假、关系计数、知识均分/筛选、训练统计和NLI；更细结构或更好探针没有带来稳定端任务收益，不能遗忘后当新点子反复重跑。训练生成器中0频率也不是临床排除规则。

本轮的边界集中如下：只做历史/文献/代码调查和既有结果离线分析，新模型调用0，正式v5不变；没有声称完整R1头已实现。1852是现接口范围，离线混合表是既有贡献记账，均不是新泛化证据。来源代码尚缺的地方按实际树/版本标注；论文给的强模型、标注记忆与额外医学资源不能悄悄计入原模型头。读取覆盖的不可读与截断范围已在上文及索引公开。后续应从冻结头的1100＋62扩展起步，把新的设计工作集中在关系与原生单选实际缺口。

<a id="r1-head-experiments"></a>

## 2026-09-16：R1错因诊断与方法试验

**最新状态（2026-09-16）：七方法完整R1主候选和20062输入的独立包回放已完成，见[交付结果](#r1-core-head-delivery)。单选全202扩展未采用；关系201问句族及全部已排定运行/分析完成，最终取舍与成本见[收尾记录](#r1-relation-extension-complete)，没有新增排队任务。** 用户明确要求先找R1当前低分原因，再采用上述调研方法形成方案并实验。沿用冻结2866单元、七方法正式评分和原模型；新增运行包为`Documents/Codex/2026-09-16/r1_head_experiments/`，按diagnosis/rules/mcq/relations存不同分支。主记录继续在本文，未另建研究主文档。

先读取原题、实际输出和必要原上下文，按来源/病种/错误类型保留抽样证据；“invalid”“未映射”仅为评分状态，不直接等同根因。诊断分支准备固定病种分层试跑再扩1100；规则分支核对72适用题与旧缓存后做事实生成；单选分支先分析202题；关系分支分析788题的目标、结局与证据使用。新方法选用发生在错因诊断之后，保留原生重答和必要同资源对照，不在同一小样本扫描大量提示。

资源启动快照：GPU0/1/2/3总显存各约97.9GB，已用43.4/42.8/72.5/6.7GB，均有其他用户任务；不终止任何已有进程。计划本任务诊断队列GPU1，规则短队列GPU3后交接单选，关系GPU0；单个8B进程先按约30%总显存配置，加载前再次检查真实余量。权重、精度和完整上下文不因调度变化；实际配置、成本、启动失败或恢复分别保存。此处是资源安排，不能当作所有GPU任务已经运行。

**首次初始化失败及恢复。** 诊断M4的60题pilot在加载阶段失败，0评分、M5尚未启动；原因是根代理误将旧vLLM 0.8.5的`gpu_memory_utilization`解释为单进程占比。实际`MedRGAG/.venv/lib/python3.10/site-packages/vllm/v1/worker/gpu_worker.py:195`把全卡其他进程显存计入non_torch，0.30×总显存会先算出负的可用KV，即使物理余量够用。这是R3已有记录的运行经验，本次未正确沿用。改为0.95总卡预算并固定2048 KV块，实际权重约15GiB、KV约4GiB；按物理空闲检查而非将0.95说成占95%。保留首失败日志，再以相同请求/模型重试。规则/单选同步采用此已核实配置；关系因原上下文最长74k，固定8192块、保留131072上限，并与GPU3短队列错开profile共享运行。GPU0/1他人显存后增至约60GB，因此关系不再安排GPU0。尚未改变模型、精度或裁短输入。

### 首轮实际错因及据此冻结的试验

从错误总量看，M4/M5在全R1分别错2068/2047题，其中MedEinst错1544/1586、MedCounterFact错386/345；两来源合计占错误93.33%/94.33%。因此总体低分主要由开放诊断和证据关系贡献，不能用Cultural或单选的少数错例概括全部R1机制；本轮优先实验也据此安排。

**诊断。** 新1100题M4/M5原评分2200项一致，正确33/34、未映射818/804、有效错诊225/235；旧表面标签清理在两骨干均0修复0误伤。分层读取119个原答案字段，完整核查24题题面/解释后，确认真换病、粒度或目录名称不兼容、检索标题牵引同时存在，例如Myocarditis→Yaws、急性胸痛仍归Panic、Bronchitis→Acute bronchitis。s005651的答案字符串内`}`触发冻结评分regex的malformed，实际诊断仍错，修解析也不改变该题正确性。保留原评分，先用30病种各尽量2例的60题pilot，比较原答/order0/六票/校正；不是按模型成绩选题。证据及命令在diagnosis（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/diagnosis/README.md`）。

**用药多选。** 全96题M4/M5正确29/33。实读全部题目/选项/原答案及34份分层完整解释，见把多选当单选、明说两个风险却只输出第一个、把检索未提当无风险、新增支持未执行、动作与阈值或字母对应错误；既有规则尚未覆盖全部DDI。冻结71规则先迁移72适用题，每骨干11份旧事实完全同请求复用（10 R3＋1 R2）、61新事实，共122新事实；七方法用各自原初答组合。samefacts模型执行控制另生成/复用并计费；dict字段顺序不同的不冒称同请求。覆盖外24不凭空扩规则，见rules（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/rules/README.md`）。

**原生单选。** 全202题M4/M5正确131/149且0无效，故主要不是JSON问题。固定24题分层审阅包括任务目标错置、证据与最终选项矛盾、经济背景代替医学判断、真实知识关联不足及检索偏题；也有背景信息确实有用的正例，不能整体删去。两臂均保留原上下文/原答案：简短重答对照与目标范围提示各一调用，原解码预算不变；pilot共96调用，完整202两骨干两臂808调用含pilot可复用。证据见mcq（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/mcq/README.md`）。

**证据关系。** 原788题/201源组M4/M5正确402/443，无效6/5；分别203/209答uncertainty。26例错误方向审阅包中，11个短病例完整证据与其余相关段落显示：把额外检索当题附研究、拒识实际已出现的替换名、A/B方向反转、复合/次要结局移用，以及多研究汇总困难。全部788×2原预测截断计数为0，准备器也确认每段fixed_evidence都在原上下文，不再把普遍错误归给截断。M20:56两模型明确B更高却答A更高；M20:145 M4把6.4%对4.5%答lower；M20:140将复合结局HR移到死亡率。由此冻结三臂redo/evidence_scope/target_scope，逐级控制证据角色、目标与方向绑定；64题/64源组分层pilot合384调用，保留四标签及原生严格评分。当前gold不含uncertainty不能成为删选项依据。另有三例点估计/显著性口径未解释差异，见数据审核记录（本地来源：`/home/data3/txy/docs/data/construction.md#r1-medcounterfact-label-scope`），保持其原分母。原始审阅、prompt与长文配置见relations（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/README.md`）。

### 诊断首轮结果与扩展启动

60题/30病种pilot已完成720条患者评分，输入2,084,076token、输出720、缺失代码补分0；恢复后队列约201秒。M4/M5原正确3/3，order0为13/16，六排列未校正18/17，冻结校正18/17；对原答修复15/14、误伤0/0，校正宏平均约0.328/0.311。因此已确认冻结诊断头在新增R1范围有初步实质收益，增益不归给本轮没有增量的先验校正。Qwen两条输出选公共49目录中的Whooping cough，不在冻结46评分词表内，保留为真实无效结果，不按gold删候选。

按已授权计划，原封不动扩展其余1040题，每模型6240条分布、两骨干合12480；GPU1顺序M4→M5。pilot与其余分层保存，不把后者称独立泛化。其他五方法的原上下文/终态准备并行推进，尚未启动其GPU评分。

后续准备已完成：另五方法5500个原上下文/基线一致，最长请求M0/M2/M3/M6/M7为1630/2771/8660/4740/15073token，不需要裁短；原模板先验可复用。M0/M2有762条分布请求完全相同，可实际复用，其余预计32238新评分（缺码补分另计）。据旧680题七方法证据及本轮两骨干pilot收益，启动GPU0的M0→M2→M6；GPU1完成当前两骨干后再M3→M7。调度提前不改变冻结策略及题目选择。

关系分支在两骨干pilot结果尚未齐备时先固定后续样本：未入pilot的137源组各随机一个变体，种子20260917；若出现共同有效候选，先与redo做548调用的源组扩展，累计覆盖全部201源组。全788含同组多名称变体，此步优先检查不同研究的迁移；仍是已暴露开发，不能把201题外推成788题新分数。完整788请求保留，选择和实际是否扩展另记。

### 用药冻结迁移完成：收益、实际反例及未采用的范围门

两骨干事实与同事实模型执行均完成，GPU队列退出0、用时930.54秒。新增260调用＝122事实＋138执行，复用28＝22事实＋6执行；全部无length停止。实际输入/输出token分别177010/78299。七方法为现有原答与对应原骨干事实的离线组合，没有重跑七套检索流程；完整结果与成本（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/rules/RESULTS.md`）、逐题评分（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/rules/scored.jsonl`）保留。

| 方法 | 原正确/96 | 冻结规则程序 | 修复/误伤 | 同事实模型执行 |
|---|---:|---:|---:|---:|
| M0 | 38 | 66 | 29/1 | 47 |
| M2 | 34 | 58 | 26/2 | 38 |
| M3 | 50 | 60 | 13/3 | 50 |
| M4 | 29 | 58 | 31/2 | 36 |
| M5 | 33 | 57 | 27/3 | 41 |
| M6 | 32 | 62 | 32/2 | 38 |
| M7 | 38 | 56 | 19/1 | 44 |

旧R3的10题程序结果完全复现10/10/8/10/10/10/8；新增覆盖62题为36/33/35/36/29/34/31。未覆盖24题保持原答。冻结程序在七方法都提高，且优于同事实模型执行，支持规则组合这一具体贡献；但不说明所有患者事实和每个修复都正确。

真实反例包括：s001061题面是orthostatic syncope，Llama却抽bradycardia_related_syncope=True，并因该错误事实将donepezil置为MET而碰巧得分；Qwen抽False。s001067/s001079存在delirium、dementia下H2/prochlorperazine范围差异；s001055的gastroparesis例外还受未给疗程与默认例外政策影响。这些错误没有靠逐题特例修改规则。

对s001130等加药题，最初将现象称为“只问DDI却用单药规则”的路由错误，随后**逐字核查全部9个触发题后撤回这一过强解释**：它们问句均为`potentially inappropriate to add to this patient's current regimen`，未写only或明确限定drug–drug interactions，泛问加药安全时单药PIM也可能相关。来源内部patient_info_type不能成为推理权限之外的范围信号。统一原答透传9题（8原覆盖）的离线控制使七方法程序为65/58/61/57/56/61/55，合417→413/672，减3处误伤也丢7处修复。**不采用的首要理由是可见问句不足以证明排他范围**，不能把分数下降当作采用/拒绝正确范围的唯一依据。完整题干、触发规则及两骨干路径在`rules/scope_triggered_items.jsonl`和分支README；s001130保留为来源答案与泛问加药范围的限制，不宣称已证实路由错误。

终态口径也经实查澄清：M6全96原终态ok；M7原92 ok、3 invalid/accepted、1 invalid/budget_exhausted。原baseline及初答始终按原接受条件，未解析未接受thought补原分。按本轮一度过宽的“保留终态”解释，samefacts主表曾强制继承原non-ok而得到43；核对旧R3协议后恢复额外head新生成输出单独评分的44，43仅为strict-native敏感性。程序56不受影响。原终态、43的当时制品、修正说明均保留；额外head输出不冒称原TC流程已经修复，也不能给对照单方面增加终态门。

### 关系首骨干进展与单选启动失败恢复

关系M4的64题pilot完成192调用，约797秒：原33，redo35（修复5/损伤3）、evidence_scope36（6/3）、target_scope37（9/5），全部有效。逐题过程既有真实目标修复（M20:140由复合结局改为死亡率12.7对11.1），也有新增范围错误（M20:264明明问首次复诊启用率却转用12个月使用率）；M20:48得分修复仍以短期镇痛外推24小时，不能把答案正确等同于过程忠实。Qwen继续运行，尚未选择扩展臂。证据`relations/provisional_m4.json`、`pilot_m4_changes.jsonl`。

单选首次GPU命令使用仅有评分依赖的MedRAG虚拟环境，import vllm即失败，0模型加载、0生成；保留`mcq/pilot/M4/import_failure.log`后改用已有MedRGAG解释器。请求、模型和生成配置未改，没有新装依赖。该准备错误及恢复归分支README；健康的其他队列未中断。

关系四个M4得分修复随后完成完整证据复核：审阅附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/repair_evidence_review.md`）实读8段、79670字符。ECT/霍乱例确有题附研究重新绑定；死亡率例虽然改正12.7对11.1，却新增了原题附证据和实际prompt中没有的对应HR/CI/p值，不能称完全忠实修复；24±12小时疼痛例仍错引文档、从即刻结果外推并忽略day1无差异；clinician印象例抓对所问数字方向，但夸大总体记忆改善。四例为定向审阅，不能把比例推广到整个pilot；得分保留，机制解释据此收窄。

13:25发生新的实际共享资源争用：GPU3出现其他用户约35GiB的新EngineCore，占用与关系Qwen、正在加载的单选Qwen叠加。单选M5在KV初始化报`No available memory for the cache blocks`后自行退出1，0生成；检查时原父/子PID已退出，没有向其他用户或任何存活健康进程发信号。完整失败日志保留，改为等关系pilot释放后恢复单选，后续GPU3大/小队列串行加载。GPU2当时仅约22GiB空闲，也未扩充任务。诊断GPU0/1及关系当前生成保持运行。

M4新增诊断1100题已完成分布生成，最终接口回放等两骨干齐备后执行：原33→单次158→未校正258→冻结校正275，校正修复256/损伤14，宏平均0.05184→0.32022。收益不是所有病种均匀：COPD急性加重0→92/161、Pneumonia5→37/65、NSTEMI/STEMI0→32/117、Panic2→22/24；最大类Bronchitis仅12→13/321，Myocarditis1→0/13、TB1→0/11。校正相对未校正为54修复/37误伤，净+17；11无效为公共49目录的Whooping cough10、原拼写Larygospasm1，仍保留冻结评分。完整中间证据归`diagnosis/remaining/m4/interim_summary.json`和`error_audit.json`，不能以总提升宣称诊断已普遍解决。

对最大残留类的六例进一步审核发现，原解释多已提及新增咳痰，而不是全都漏读；目录内Pneumonia竞争、渐进误写acute、背景推断及prior翻转均有具体实例。作者12端与本地输入/gold逐字一致，未发现这六例映射错误；同时v5具体R1目标只是新增Bronchitis相容支持，完整原生评分却要求作者唯一诊断。两者不能等同，临床排他性未由本轮验收。完整来源/分类事实归构建主记录（本地来源：`/home/data3/txy/docs/data/construction.md#r1-bronchitis-support-scope`），方法过程、六票及选样归`diagnosis/bronchitis_review.md`。这一限制影响对低分原因的解释，不抹去目录头已测得的原生任务增益。

### 首轮提示负结果及关系上下文对照启动

关系三臂完整384调用已结束，1754.51秒成功模型运行，输入4404831/output71545 token，无无效或截断。两骨干同64题原正确均33；M4 redo/evidence_scope/target_scope为35/36/37，M5均31。Qwen redo和evidence_scope均0修复/2损伤，target_scope2/4；相对redo没有跨骨干共同增量，因此**不采用这版带原答案的复核提示，也不运行其137组扩展**。已准备的扩展清单保留为未执行。完整`relations/pilot_summary.json`保留各标签分布及配对修复/损伤。

MCQ的96调用也已完成：M4同24题原12→redo14（4修复/2损伤）→task_scope13（4/3）；M5三者均12且最终选项不变。全部0无效/0截断，输入271092/output24264 token；成功M4/M5用时366.3/166.9秒，含初始化134.3/74.9秒；共享显存失败另观察208.6秒、0调用。Qwen47/48份解释发生文字变化，说明确有新生成但未改变答案。范围提示未可靠落实选项一致，例如s002080解释末尾说Histoplasma却输出E/Blastomyces。**不采用、不扩大余178题，不按骨干/来源拼接最好输出**。完整`mcq/pilot/summary.json`和`changed_cases.jsonl`保留。

关系分支据此启动一次有限的上下文机制比较：仍用同64个已暴露pilot、原骨干/采样/schema/原系统指令及同一target_scope文字，共256新调用。`no_draft`去掉此前额外拼入的旧答案，保留全部原上下文；`supplied_only`进一步只保留原user内容从`Here is the question:`起的逐字块，包含全部fixed_evidence及原输出指令。后者借用来源论文的给定证据输入组织，是本地原骨干适配，不称已取得作者推理实现。准备器逐题核对没有裁掉题附证据、没有加入参考端/替换元数据/gold；最长输入M4 66456、M5 73600 token。MCQ释放GPU3后顺序运行M4→M5；主记录为计划/启动，结果未出。证据`relations/context_plan.json`、`context_requests.jsonl`及`context_queue.log`。

第二组256个实际prompt另由独立CPU审阅全部按原tokenizer精确重建通过，见`relations/context_input_audit.json/md`。两臂无意外裁切或附入旧答，单题完整题附材料最多254232字符；supplied_only最大61798/68554token。它同时移除前置检索与缩短文本，后续分差不能仅归因二者之一。

### 诊断两骨干1100题完成及独立R1包准备

M4/M5新增1100均完成，共13200新分布评分，prior新调用0；从新`candidate/r1_head.optimize`逐字回放13200条缓存请求，评分与原诊断分支一致。完整`diagnosis/summary.json`与`scored.jsonl`已经产出。原答/order0/六票/校正分别M4=33/158/258/275，M5=34/180/312/308；校正对原答修复/损伤256/14、287/13，宏平均0.05184→0.32022、0.08598→0.28970。校正相对六票是+17/−4，所以只确认冻结整个头在两骨干有效，不能称先验校正均有贡献；保持统一冻结策略，不挑每骨干最高臂。pilot与剩余1040各自单列，均为暴露开发。

独立推理包已组装在r1_head_experiments/candidate（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/candidate/README.md`），10支持模块逐字沿用已交付R3包，入口改名`r1_head.optimize`但函数逻辑不变。包含公共目录/规则及匹配模板prior，11模块独立导入已通过；没有训练病例库或R类别路由。全2866×7入口回放将在其余方法齐备后执行，目前不能将它写成已完成。R1中1780诊断、72规则覆盖、1014原答透传的分支范围已明确；失败的关系/单选提示不暗中放入该包。

### 单选去旧答案的有限对照准备

首轮Qwen的48个选项全未改变而47份解释被改写，可能受额外附入旧答案牵引；为区分该输入组织问题，沿用同24题、两骨干、redo/task_scope两臂再准备96新调用。两臂同时去除额外assistant旧答案和“The previous answer is a fallible draft”一句，其余原上下文、题目、选项和提示保持；仍用原权重、温度、schema与2048输出预算。共享显存下关闭CUDA graph以减少占用，不改变解码设置；它改变执行调度，因此不能把旧/新每项随机输出变化作为严格确定性的单因素因果估计。请求与计划见`mcq/fresh/plan.json`，目前准备完成、尚未生成。仅此一次有限补充，首轮负结果继续保留，不自动扩全202或按方法挑最好臂。

### 关系去旧答/题附证据对照完成，固定137组扩展

第二组256新调用已完成，全部0无效/0length停止，输入2422044、输出58088 token；两骨干成功运行共1871.56秒（含加载，共享GPU时间，不是独占性能基准）。同64题原33/33，完整上下文去旧答`no_draft`为39/40（修复/损伤11/5、9/2），仅题附证据`supplied_only`为41/44（10/2、14/3）。后者对前者为6修复/4损伤、8/4；因此目前两骨干都有净增益，但样本是已经参与开发的64题。0uncertainty-gold并未用于删候选，第二组仍实际输出8–10个uncertainty。

按在第一轮结果出来前已经固定的seed20260917清单，启动准备其余137来源组各一个变体的扩展。保持上述两个版本，不再用已失败的附旧答案redo作为唯一控制；两骨干548调用，分别报告137与合计201组，不替换全788得分。新的`context_extension_requests.jsonl`与旧未运行三臂`extension_requests.jsonl`分开；旧版本继续记未执行。计划先在GPU3完成短单选补充，再运行关系扩展，和已接手的M7按实际余量并行；不改变原权重、生成/评分或删除题附证据。证据`relations/context_summary.json`、`context_extension_plan.json`。

### 七方法扩展中间进展与实际资源调度

M0/M2新增1100的分布生成已完成，原答/order0/未校正/校正分别43/131/257/285与29/162/295/278，接口回放随后统一执行。M0新6600调用，M2新5838加762条逐字同请求复用，均无缺码补分。校正相对未校正的+28/−17进一步说明不能把全头增益都归给先验校正，统一冻结版本不随这些分数改动。M6已接GPU0，M3在GPU1，M7于关系64题对照释放GPU3后开始；健康进程保持，队列调整只影响尚未开始的任务。

M7实际825批请求的16-token块前缀树容量审核最多1498块；2048块足够容纳这些已知共享前缀请求，因此保留原配置。该数是实际token结构的CPU分析，不是测得的调度峰值或普遍无抢占保证；具体证据`diagnosis/other_methods/m7/kv_capacity_audit.json`。新增他人任务使GPU0/1余量缩小、GPU3另一个35GB作业结束后释放，按实际空闲调度，未干预他人进程。

### 单选补充完成：选择简单重答做完整202题检查

去旧答96调用完成，原24题正确M4/M5均12，简单redo为17/14（修复/误伤7/2、3/1），task_scope15/12（3/0、2/2）。task_scope相对redo为3修复/5误伤、1/3，复杂提示没有额外价值；两骨干均0无效/截断。新增输入243976、输出22510token，两worker成功运行172.19＋162.82秒、含初始化18.40＋18.80秒。完整`mcq/fresh/summary.json`保存，先前附旧答案版本的负结果不改写。

由于简单fresh redo已在两骨干取得共同增益，现作出有结果依据的扩展决定：固定其原样提示，在完整202（AMQA134/Cultural67/CPV1）检查，而不是按先前“没有自动扩展计划”机械停止。每骨干已有24个逐字同请求结果复用，新增178，共356新调用；pilot按原答正确性富集，不能据其比例外推，所以另报pilot24、剩余178及全202。`mcq/fresh_full/plan.json`已准备；GPU0/1在各自诊断M6/M3健康结束后接M4/M5，不改权重/采样/schema或扫描其他提示。该试验仅两骨干/其原上下文，不自动写成七方法统一头结果。

关系137组两臂扩展已于单选fresh结束、显存释放后在GPU3启动，与健康M7并行。548条实际渲染输入另核对通过，最长71563token，完整题附材料单题最多258112字符；所有题附证据及原schema保留。64组原正确33/33，其余137组67/79；合计201组100/112。类别组成53 higher、56 lower、92 no difference，见`relations/grouped_scope.json`。

### 关系上下文候选的完整限定过程审核

为区分分数改善与实际证据使用，固定两骨干共同修复中题附材料最短2例，加两骨干supplied_only全部5个不重叠误伤；已读完7题、10个材料块216699字符、14原解释及14新解释，并核对实际prompt包含材料。完整审阅附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/context_case_review.md`）及结构化定位保留，不以选中7例估计总体过程正确率。

共同修复中确有从现实名称先验回到假设研究的改善：疲劳量表及ECT/霍乱比较的A/B数字方向有依据。仍有M4误称第二篇没有ECT、把首次复查改为3个月使用率、弃用/退出与分母混淆等，正确分数也不意味着这些过程已修好。全部误伤包括真实时间/结局读取退步，以及问句宽泛对照与具体wait-list研究、点估计和显著性口径的映射歧义；不能全归幻觉，也不据此宣告gold错误。保持同两臂与原评分，人工审核到此停止。

本审核还触发了分组身份纠正：M20的group_id是问句族，201问句族只有91个original_review，且pilot与扩展有重合。完整事实归数据构建记录（本地来源：`/home/data3/txy/docs/data/construction.md#r1-medcounterfact-question-groups`）；早期“不同研究迁移”解释收窄为不同问句族上的开发扩展，原先已经明确的“非独立泛化”边界保持。没有因看到这些结果重抽扩展题。

### 汇总范围中的R5保留项

按冻结`evaluation_labels`核对，2866个R1中450同时选入R5，全部为M20关系题；不是把旧语义标签中未选的成员追加进分母。当前诊断＋规则主候选对这450题全部原答透传，最终完整汇总另列`r5_overlap`。关系201问句族试验另列其中实际选中的R5题修复/误伤，不能由R1总体净增益代替该分析。R1以外的R5没有在本轮重新运行，不据当前结果声称完整3600个R5上的通用保留性。

### 扩展运行的失败、中断与原样恢复

MCQ full202的M5先在旧vLLM的共享显存profile断言失败：加载期间空闲从27514044416增到38719127552 bytes，违背`initial_free > current_free`前提；0新预测，并非输入超长或本次显存不足。随后第一次恢复因为未先迁走旧gpu1输出目录，在原runner的mkdir处FileExistsError，仍0调用/0模型加载，这是实际调度失误。两次分别保留在`mcq/fresh_full/M5/failures/initial_shared_memory_profile/`及`retry_directory_exists/`。迁走失败目录后，完全相同请求/配置重试完成178新调用，用时331.52秒含25.49秒初始化；已有24条fresh redo精确复用，不重复生成。M4在M6诊断正常结束后接GPU0，健康任务未被中断。

关系扩展另发生未解释的进程退出：14:38:07最后保存M4的136/274条，此后发现worker与GPU engine均不存在，原exec session5104不可恢复；worker/queue日志没有traceback，M5尚未启动。根任务没有发停止信号，不能仅凭用户消息时间或显存释放推断退出原因。原日志、runtime、配置及中断证据保存于`relations/m4/failures/context_extension_interruption/`，已保存136条均可解析且与冻结请求前缀逐项对应。

恢复只补M4剩余138条，并继续已排定的M5 274条；保持原模型、seed、批大小、解码、全部请求及评分。runner现在先验证已有结果是完整请求的批边界前缀，再继续原顺序；原日志不覆盖。调度改为记录PID的持久后台进程，M4在GPU3恢复，M7诊断正常结束、物理余量足够后再并行M5。中断时下一批最多4条可能已开始但没有持久化，无法核清其实际token/耗时；最终调用成本将明确为已记录完成调用，额外在途损耗标未知，不能假记为0。

<a id="r1-core-head-delivery"></a>

### R1主候选完整汇总与独立入口回放完成

冻结2866原生R1成员、七原方法结果及原评分不变。诊断全1780×7×4决策对照49840行齐备，12460原生诊断评分逐项与正式基线一致；其中旧680题分布复用，新1100实际新增45438分布评分、762个M0/M2完全相同请求复用，无缺码补分、无新增prior调用。新诊断输入153950700token，输出45438token；9个模型worker累计记录14335.94秒含初始化及共享GPU争用，不能当作独占速度。

最终组合为公共49目录六排列重决策＋冻结先验校正、72适用用药题的71规则程序、1014其他任务原答透传。七方法完整结果如下；关系与单选试验未纳入该表。

| 方法 | 原答/2866 | 仅复用旧R3的记账/2866 | 当前R1头/2866 | 准确率原→头 | 修复/误伤 | 本轮新增范围净增 |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 861 | 1068 | 1329 | 30.04%→46.37% | 479/11 | +261 |
| M2 | 898 | 1057 | 1323 | 31.33%→46.16% | 434/9 | +266 |
| M3 | 766 | 941 | 1260 | 26.73%→43.96% | 506/12 | +319 |
| M4 | 798 | 961 | 1225 | 27.84%→42.74% | 481/54 | +264 |
| M5 | 819 | 1077 | 1367 | 28.58%→47.70% | 584/36 | +290 |
| M6 | 858 | 1006 | 1317 | 29.94%→45.95% | 471/12 | +311 |
| M7 | 901 | 1038 | 1331 | 31.44%→46.44% | 433/3 | +293 |

本轮新增范围指2133个不与R3重合的R1成员；其中1100诊断和62规则覆盖题实际扩展，其余透传。旧R3列只是历史结果记账，不是推理时按R3标签路由。新头始终按原生接口/题面路由。

| 方法 | 新增2133原答→头 | 旧733原答→头 |
|---|---:|---:|
| M0 | 730→991 | 131→338 |
| M2 | 717→983 | 181→340 |
| M3 | 703→1022 | 63→238 |
| M4 | 575→839 | 223→386 |
| M5 | 634→924 | 185→443 |
| M6 | 701→1012 | 157→305 |
| M7 | 689→982 | 212→349 |

主候选比原答均提高14.83–19.12个百分点，但方法间最高最低差从4.71变为4.95个百分点，不能称方法差距缩小。M4有54个原正确被改错，M5有36个，净收益不等于逐题安全；R1内450个选中R5全为透传，0新增修复/损伤，不能扩称R1外R5的保留性。M7的11个原non-ok诊断终态仍保留：新terminal head可独立给新答案；若另强制继承原status，诊断634变631，完整R1相应1331变1328。M6对应敏感性不改597诊断正确。

**真实独立入口已回放完成。** `candidate/r1_head.optimize`在2866×7=20062个输入运行，调用74760次缓存疾病分布和504次缓存事实，共75264回调，0新模型调用；诊断渲染prompt与实际生成请求逐字对应，事实请求的messages/schema对象一致；答案/原生得分/分支与完整汇总一致，11推理模块均来自独立包自身。每方法1780目录、72规则、1014透传；没有gold、参考端、来源/R标签路由或训练病例答案库。`candidate.json`现为`complete_cached_replay_verified`。

复现/接手：独立包说明（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/candidate/README.md`）、全R1机器结果（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/core_r1_summary.json`）、逐题评分（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/core_r1_scored.jsonl`）、回放证明（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/candidate_replay.json`）。主结果是同来源已暴露开发，不是七套完整检索流程重跑、独立泛化或临床有效性证明；R3旧成果未改写，正式v5选用表未替换。

### 诊断贡献分解与为什么新增范围仍难

全1780诊断的冻结四臂如下，所有目录控制使用相同患者分布，后处理不另生成；先验沿用原方法模板，无本轮gold估计。

| 方法 | 原答 | 单次order0 | 六票未校正 | 冻结校正 | 30病种宏平均原→校正 |
|---|---:|---:|---:|---:|---:|
| M0 | 159 | 430 | 571 | 599 | 0.0599→0.3276 |
| M2 | 192 | 482 | 620 | 593 | 0.0690→0.3516 |
| M3 | 47 | 431 | 525 | 531 | 0.0448→0.3830 |
| M4 | 236 | 497 | 617 | 634 | 0.0752→0.3671 |
| M5 | 194 | 562 | 714 | 718 | 0.1116→0.3587 |
| M6 | 168 | 433 | 560 | 597 | 0.1043→0.3453 |
| M7 | 222 | 582 | 640 | 634 | 0.1546→0.3982 |

六票对单次order0在七方法的微准确率均有增益；校正对未校正却为+28/−27/+6/+17/+4/+37/−6，不能称其微平均贡献一致。30病种宏平均在七方法均高于未校正，表明评价权重会改变对校正贡献的判断；维持同一冻结策略，不按各方法的最高分切换。代码/类别有效输出并不意味着事实推理已经正确，目录与冻结评分词表差异造成的无效仍照常记错。

旧680只有9个gold类；新增1100中共有9类562题、新增21类538题。各方法冻结head在这562共有类只对81/75/71/61/60/69/60，反而新增21类正确204/203/256/214/248/252/256。共有9类的混合比例本身变化很大，故进一步逐类查看：Pulmonary embolism旧205题head正确189/184/44/188/177/163/164，新23仅6/8/4/1/1/5/1；Possible NSTEMI/STEMI旧138正确101/112/86/87/116/91/85，新117为41/41/48/32/50/38/41。这两类新旧目录输出均有效，差距不由无效格式或新增病种本身解释。它说明R1新增病例内容/目标难度需要单独分析，但当前非随机病例组成不能识别其临床或构造层面的因果原因。完整逐类分母和无效见病种分层（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/diagnosis/all_methods_1780/class_scope_comparison.md`）。

### 单选完整202的扩展负结果：不纳入头

固定fresh redo的全202已经完成：M4原131→134，17修复/14误伤；M5原149→135，8/22。把用于选择的24题拿开，剩余178分别119→117、137→121，两个骨干均净退步，故pilot上的共同收益未延续。保持原答，不采用简单redo或更长task_scope，不再增加提示/种子/来源特例。

本阶段356新调用＋48逐字相同pilot结果复用，新输入848548、输出81248token，两模型成功worker共974.61秒，0无效/0length停止。M5两次初始化/恢复失败已递归纳入`mcq/fresh_full/summary.json`，这项离线补录没有改变预测/评分或增加调用。全202及24/178、三个来源、逐题修复/误伤均已保存；当前全R1主候选继续透传这202题。

<a id="r1-relation-extension-complete"></a>

### 关系201问句族扩展完成：目标重答有效，删除检索没有共同增量

2026-09-16 15:26（Asia/Shanghai），最后的M5扩展结束。M4恢复仅补138条，保留此前136条；两模型各274条、退出码均0，持久协调器完成原生评分与201问句族合并。本轮所有已排定GPU作业和分析结束，没有继续启动模型试验。`no_draft`保留全部原上下文，追加固定A/B、结局、人群与时间范围提示，不拼入旧答案；`supplied_only`在此基础上删除原user中题目前的额外检索段，完整保留题目、题附证据和原输出约束。两臂都沿用原骨干和解码。

| 范围 | 方法 | 原正确 | no_draft | supplied_only | no_draft对原答修复/误伤 | supplied_only对原答修复/误伤 |
|---|---|---:|---:|---:|---:|---:|
| 全201 | M4 | 100 | 123 | 130 | 39/16 | 42/12 |
| 全201 | M5 | 112 | 132 | 131 | 30/10 | 37/18 |
| 原pilot64 | M4 | 33 | 39 | 41 | 11/5 | 10/2 |
| 原pilot64 | M5 | 33 | 40 | 44 | 9/2 | 14/3 |
| 其余137 | M4 | 67 | 84 | 89 | 28/11 | 32/10 |
| 其余137 | M5 | 79 | 92 | 87 | 21/8 | 23/15 |

两个无旧答版本相对原答的收益都延续到137扩展，支持这条原模型目标重答路线。删除检索的额外贡献却不一致：全201相对no_draft是M4修复24/误伤17、净+7，M5为17/18、净−1；在未用于本轮候选选择的137问句族上分别+5/−5。因此保留**完整原上下文＋无旧答目标重答**作为两骨干、201问句族范围内的关系候选，`supplied_only`作为有局部收益的研究对照，不按模型分别选最优臂，也不声称检索普遍有害。此处没有新增简单无目标提示的等调用控制，现有设计不能将相对原答的全部收益单独归因于目标提示或解除旧答影响；温度0.7单种子结果也不是确定性因果估计。

分组解释按纠正后的91个original_review保留：扩展中pilot已见review的68题，M4原/no_draft/supplied_only为30/40/41，M5为36/45/43；pilot未见review的69题，M4为37/44/48，M5为43/47/44。后者仍在已暴露v5内，而且review ID不保证临床研究独立，不能称独立泛化。选中R5重合118题，no_draft使M4 61→73（25修复/13误伤）、M5 63→79（22/6）；supplied_only均为78（27/10、25/10）。净提升不代表原正确题全部保留。

扩展548次新完成调用，输入5767673、输出124574token，已记录worker4192.34秒，0 length停止。M5 supplied_only唯一无效s003578已追到原始输出：320token正常stop，但JSON解释字符串含未转义换行，冻结解析器判malformed；可见answer_choice为lower，与gold一致，no_draft也正确。故全201相对no_draft的−1包含这一格式损失，不能全部解释为关系语义退步；即便事后将该可见选项算作语义正确，supplied_only也只是全201打平132、扩展88仍低于92。该算术敏感性不替换正式原生分数，不修输出或重跑，见无效核查（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/context_extension_invalid_audit.json`）。中断前已保存136条只计一次，M4恢复1091.34秒与原已记录1344.36秒合为2435.70秒；M5为1756.64秒。未知在途成本仍按上文保留。

结果证据：扩展137评分（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/context_extension_summary.json`）、全部201及分层（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/context_all201_summary.json`）、1206行配对结果（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/context_all201_scored.jsonl`）、执行状态（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/diagnosis/relations_persistent_state.json`）。关系只覆盖M4/M5各201题，未替换七方法全788关系答案或完整2866主表；不能把部分输入上的提升换算成全范围新分数。

### 本轮成本、交付与仍未解决的部分

成本汇总（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/cost_summary.json`）由各完成runtime和原始输出统计，脚本为同包`summarize_costs.py`。新增完成调用共**47434**，输入168085874、输出505966token；累计已记录worker24894.60秒（约6.92小时），含成功加载、共享卡争用和中断前已记录时段。多个worker并行，故这不是任务墙钟时间、独占GPU小时或速度基准。输入token按各请求完整prompt累计，未扣共享前缀缓存节省的计算量。

| 分支/阶段 | 新完成调用 | 输入token | 输出token | 已记录worker秒 |
|---|---:|---:|---:|---:|
| 新1100诊断、七方法 | 45438 | 153950700 | 45438 | 14335.94 |
| 用药事实＋同事实执行 | 260 | 177010 | 78299 | 897.37 |
| 单选旧答pilot | 96 | 271092 | 24264 | 533.26 |
| 单选去旧答pilot | 96 | 243976 | 22510 | 335.02 |
| 单选完整扩展新增178 | 356 | 848548 | 81248 | 974.61 |
| 关系三臂pilot | 384 | 4404831 | 71545 | 1754.51 |
| 关系无旧答/删除检索pilot | 256 | 2422044 | 58088 | 1871.56 |
| 关系其余137两臂扩展 | 548 | 5767673 | 124574 | 4192.34 |

规则表中897.37秒是四个worker之和，前文930.54秒是含队列间隔的整队列耗时，统计对象不同。复用另列：旧680诊断28560条分布、新范围M0/M2同请求762条、规则28调用、单选pilot48输出、无新增prior；独立完整包75264次缓存回调属于CPU回放，不计新增模型调用。五项加载/调度失败均0新完成生成，证据路径列于成本JSON；另有关系中断最多4条在途请求的实际调用数、token与额外耗时未知，所以47434是**已记录完成数**，不是包含不可恢复损耗的精确总计算数。

本轮交付是可调用且经过完整回放的R1开发头，以及四分支的实际错因、对照和负结果。主体收益来自R3目录重决策向新1100诊断的迁移和R2规则对新增支持的执行；并非恢复旧Delta就获得收益，也不是单纯格式清理。关系无旧答目标重答提供范围内的新证据；单选简单重答、长目标提示以及关系额外删除检索均没有形成可并入统一完整头的依据。

**限制与后续方向。** 主候选完整准确率仍只有42.74%–47.70%，干预1852题，1014题透传；疾病粒度/真实错诊、事实提取与规则范围、关系的目标绑定和来源统计口径仍未完全解决。6个Bronchitis来源对照还表明“新增相容支持”不必推出唯一临床诊断，相关构造事实见主审核记录（本地来源：`/home/data3/txy/docs/data/construction.md#r1-bronchitis-support-scope`）。正确gold也可能伴随错误解释。所有结果属于已暴露同来源开发，旧R3与本轮新增贡献已分开；正式v5、gold、评分和R2/R3原交付不改。若继续研究，应先处理这些已确认的语义缺口，再冻结方法做符合R1语义的独立验证；本轮不据此自动启动新任务。

<a id="r1-paper-readiness"></a>

### 2026-09-16：当前R1结果能支撑怎样的论文主张

触发：用户在确认当前head尚非泛用R1机制后，询问是否够用于论文。本次复核上述完整结果、贡献分解、研究主张和开发/泛化约定，没有新模型调用、评分变更或新的文献新颖性调查。以下是基于现有证据的研究判断，不是投稿结果预测，也未替用户改定整篇论文定位。

**可以写入论文。** 当前头适合作为有明确适用范围的方法组件，以及分类评测中的针对性优化和跨方法迁移实验。全2866上七方法均提升14.83–19.12个百分点，剥离旧R3重合后新增范围仍均有收益；完整接口回放、错误归因、消融与失败记录构成可追溯证据。是否有论文价值不由必须达到某个绝对准确率、覆盖所有来源或采用单一算法决定；公开规则和多分支实现均可作为方法，结论范围须与实际验证一致。

**现有证据不足以支撑“已经构建跨任务泛用的新增支持推理头”。** 当前主要机制是既有R3目录重决策及R2有限规则的迁移，1014题透传；关系只形成两骨干201题开发候选，单选扩展为负结果。七方法迁移仍使用同一病例范围，不能替代新数据验证。R3的733题包含于R1，因此应把共有机制与跨类复用写清，避免将重合病例计作独立证据或把同一机制包装成三套独立新算法。

**最重要的证据缺口是冻结后的独立R1验证。** 若论文主张限于目录诊断与有限用药规则，应在这两个真实声明范围内取得未参与调优、病例或原始研究分组隔离的新R1证据，保持题目、候选资源、评分及方法先固定，同时报告修复、误伤和必要的配对/保持表现。应先核实新例确有R1新增支持语义，普通诊断题本身不能替代该验证。更广任务通用性需要相应覆盖的证据；它不是使用当前有限结果的先决条件。

**机制归因按已有证据写，并只补主张真正需要的缺口。** 现有单次目录、六排列未校正、校正，以及同事实模型执行控制已经有用，不要求重复运行。它们支持目录决策/投票和有限规则执行的具体结论，校正的微平均收益不一致。若要进一步声称收益来自R1特有的支持更新，应检验相对同候选资源、同计算预算的一般重决策是否仍有增量，并把名称/输出适配与语义修复分开。关系臂目前缺少“去旧答但不加目标指令”的简单等调用重答对照；在补齐前可保留为辅助开发结果。

当前建议是保留已完成头及负结果，优先补独立验证和与所选主张直接相关的对照，再根据结果决定扩大机制范围。旧Adapter的历史高分不能补足当前原生单输入R1的证据缺口；接回它也不自动构成论文所需的增量。本次未为此启动新的训练、数据收集或GPU队列，R2/R3既有完成状态保持。

<a id="r1-frozen-validation"></a>

### 2026-09-16：冻结后独立验证与关键归因对照启动

用户明确授权优先完成这两项工作。运行包为`Documents/Codex/2026-09-16/r1_head_validation/`；`plan.json`与`frozen_head/`保存当前R1接口、49目录、71规则、原模型配置及现有先验，不按本轮新预测改提示、规则、目录或融合策略。原v5及上一轮完整结果保持，R2/R3已完成任务不重启。此处记录本次独立研究验证，制品包README只维护命令与导航。

**诊断资格计划。** ASCENT原生任务为逐步病例信息下的诊断，优先考虑尚未逐题用于方法开发的test，并另列train剩余范围；旧train阅读、接口开发、同病例组及本项目MedQA派生重合均须追溯。严格限定目标完整匹配现有49目录，不加别名或改变为四选一，按每病例最后一个兼容原生阶段（上下文段数最大、同长取原行号）选择一次，所有选中候选均保留审核去向。R1资格要求可定位的先前信息、新增事实及其对目标的实质支持；不要求既往Imp非空或答案必须改变，也不把普通诊断自动算R1。CUPCase原生四选一在现头走透传，改成49目录会改变原任务，因此本轮不拿该改造充当冻结头验证。来源选择先于模型预测，最终分母以资格完成清单为准。

**用药来源限制。** 旧MedPIC的183 CF和284 GF全部曾用于历史方法检查/基线，不能只排除v5的167题就把剩余称为独立病例。当前先核对官方来源沿革与真正外部的可评分R1问题；若只有新受控规则病例可构建，将明确归为冻结后机制探针，不冒称独立临床数据。尚未启动本分支模型推理。

**关系关键对照计划。** 既定201问句族/91个original_review，比较普通简短redo与已选target_scope；两臂都保留相同完整原上下文、不附旧答案、原模型及解码。两臂本轮重新生成，避免把新普通重答只与旧批次结果直接作单因素解释；M4/M5各402，共804新调用。沿用batch4、seed42、131072长度上限、8192 KV块、eager；没有截断输入、删除检索或扫更多提示。归因依然属于已暴露开发，按原始review做配对分组统计，并保留与历史同请求目标臂的重复性比较。17:16资源快照GPU0/1分别空闲55259/53653MiB，分配M4/M5各一卡，启动前再核实至少40GiB；.95是旧vLLM总卡预算，不是本进程占卡比例。所有他人任务保持，队列用持久后台进程记录PID和日志。

本次启动期没有新模型结果。完整完成标准是冻结资格范围后运行、原生评分/必要控制、修复/误伤及独立性边界、失败与实际成本归档；按本轮结果临时修改方法或扩大样本不属于该冻结验证。


**17:35资格冻结及实际启动。** ASCENT已固定47病例（test5/train42），所有原文、排除与重合事实统一见构建记录（本地来源：`/home/data3/txy/docs/data/construction.md#r1-frozen-validation-qualification`）。新诊断运行器`diagnosis/run_validation.py`直接调用冻结head模块和原骨干，完整保留原生单user Text；追加目录请求仍按既有接口重复当前病例。四臂是原生自由生成、单次order0、六次未校正和六次冻结校正，另有零调用复制最后既往Imp控制；后者用于23/47既往已命名目标的混淆。两模型各47×7，658次主要调用，缺失code的同prompt补分另计。最大head输入M4/M5为1605/1588token，自由生成558/537；不截断，原生baseline用temperature0.7、seed42、max2048、不强制JSON。预先固定最后完整boxed抽取与单层text/mathrm包裹去除，不修正诊断内容；评分沿用项目canonical-name而不是作者LLM语义F1。

49目录、六排列、融合及旧m4/m5先验完全不改。新来源是单user模板，而旧先验来自原MedRAG模板；此次衡量严格冻结参数的模板迁移，未按新来源重新拟合先验，未校正臂同时报告。不能把这两原骨干成绩写成两套原RAG流程或七方法新结果。prepare成功且gold只由CPU检查/分析读取；持久队列PID978911于GPU0启动，加载前空闲39879MiB，固定2048 KV块及eager，四worker顺序执行。

关系对照初次17:19 GPU0空闲38345MiB低于40GiB门槛而在加载前退出，0调用；原日志归`relations_control/failures/initial_gpu0_below_margin/`。随后M4在GPU3空闲47021MiB时恢复，持久协调器PID963486；17:29 M5在GPU1空闲55779MiB时提前并行，supervisor PID973766，原串行队列改为等待该进程避免重复启动。两臂输入/配置/804调用计划不变，未打断其他作业。

用药来源审核未取得兼容的独立临床集，另已冻结11组33端的新受控机制探针；第09组资格缺陷及初版执行器“通过但语义不合格”保留在构建记录。后续使用两个原骨干各原答案、事实提取、同事实模型执行三调用，共198计划调用，按组报告基础/新增支持/无关信息三端和修复误伤。该分支排在诊断GPU0队列完成后，仍无临床独立性主张。


**诊断首次加载失败与恢复。** 17:33新增direct worker遗漏既有`EXTRA_SITE`导入路径，MedRGAG环境默认新版transformers的`TokenizersBackend`缺少vLLM0.8.5所需`all_special_tokens_extended`，权重加载前退出1、0调用。修复仅沿用已有兼容site-packages路径，不升级或更改环境、方法。旧prepare/日志/runtime归`diagnosis/failures/initial_transformers_incompatibility/`；重新prepare后两模型的head请求、direct请求、配置、token ID和先验均逐字一致，证据`request_comparison.json`。恢复队列PID983715，GPU0加载前空闲37859MiB；诊断成功后再启动规则队列。


**预先固定的解释边界。** 独立静态审核确认47输入逐字对应原Arrow Text，推理工作进程只读prompt/config/token IDs；11份冻结代码和资源一致。当前head接口要求调用方提供相应先验，本次计划特意冻结旧MedRAG先验，因而评估的是完整旧参数向ASCENT单user模板的严格迁移。若校正没有增量，只能据此判断该冻结参数迁移，不能推断为按新模板重新计算content-free prior的校正算法普遍无效；本轮不看新结果重新校准或增设择优策略。


<a id="r1-frozen-diagnosis-results"></a>

#### ASCENT47：冻结验证完成，额外投票/旧先验未形成稳定增量

17:44，诊断四个worker及分析全部退出0，规则等待队列随后才接用GPU0。固定47病例/14个目标病种，贫血12例；test5和train42均按预先范围分别报告。下表均为完整47的项目canonical-name准确数；原生自由生成按预先固定boxed抽取，非ASCENT官方LLM语义F1。

| 原骨干 | 原生自由生成 | 最后既往Imp复制 | 单次order0 | 六票未校正 | 冻结校正head | 冻结head宏平均 |
|---|---:|---:|---:|---:|---:|---:|
| Llama/M4骨干 | 4 | 19 | 38 | 39 | 38 | 78.57% |
| Qwen/M5骨干 | 20 | 19 | 39 | 39 | 39 | 86.05% |

自由生成M4/M5分别42/25无效（包括目录未映射），所以其相对head的+34/+19不能直接当作医学推理改进；逐条原输出语义/格式审核继续，冻结分数保持。相同目录资源下，六票对order0是M4修复2/误伤1、M5修复2/误伤2；校正相对未校正是M4修复0/误伤1、M5全无变化。冻结head整体恰与单次目录同分。此47例没有证明投票或旧先验校正的稳定增量；M5宏平均有所改善仍与微准确率结论分开。

既往已出现目标的23例，复制最后Imp只对19（4例最后Imp不能完整匹配），冻结head两模型均23/23；此前未命名目标的24例，单次order0两者16，未校正也两者16，校正15/16。后者说明模型并非全部只复制旧名称，同时也是主要余下错题范围；不能只展示包含历史目标的高分。原生test5的所有目录臂两模型均4/5；train42单次34/35、未校正35/35、校正34/35。test太小且目录/资格条件化，不代表完整ASCENT。

本批实际新调用658（每骨干47原生生成＋282单token评分），没有缺code补分或新prior；输入662047、输出12383token，四worker累计437.15秒，完成队列墙钟469.58秒，0生成截断。冻结入口回放564次缓存回调全部一致、0额外调用。首次兼容依赖失败为0调用，未形成完整worker耗时记录，成本不伪补精确值；旧失败原始日志保留。证据：summary.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/diagnosis/summary.json`）、逐题评分（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/diagnosis/scored.jsonl`）、冻结运行配置（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/diagnosis/prepared.json`）。本次不据结果换成某骨干特定策略、重算先验或改变47分母。


**自由回答审核的重要纠正（评分不变）。** 94条两骨干原生输出已全部阅读，均有完整boxed且抽取成功；M4的42、M5的25个“invalid”是项目单标签canonical解析类别，不能表述成ASCENT盒格式失败。原始提示允许多个疾病或相关系统，Llama常给含目标的列表，Qwen存在SLE/GBS/TB等别名及疾病亚型；本项目单名指标不能将这些全部判为原生语义错误。因此4→38、20→39只是在已声明目录指标下的数值，不支撑原生诊断能力的大幅提升；本轮同目录order0/未校正/校正对照是更直接的机制证据。后验逐例语义计数仅作敏感性审核，不替换原分或冒称作者F1。此外冻结`previous_target_named`仅匹配既往Imp，未命名24不表示整个既往原文未提到目标，例如train1961在Reason中已写AF；保留原分层并收窄其解释。


<a id="r1-frozen-rules-results"></a>

#### 新规则探针33端：程序执行有增量，事实与UNKNOWN合并仍有缺口

诊断释放GPU0后，持久规则队列PID987624完成两个原骨干的普通答题、事实抽取、同事实执行六个worker，全部退出0；最终11组33端（基础/新增支持/无关信息各11），初版第09组排除且未补抽样。用药独立公开临床来源缺口仍然存在，本批只称同规则来源的冻结后受控机制探针。

| 原骨干 | 普通初答 | 同事实模型执行 | 冻结程序head | head对初答修复/误伤 | 三端全对（初答→模型执行→head） |
|---|---:|---:|---:|---:|---:|
| Llama | 7/33 | 6/33 | 21/33 | 14/0 | 0→0→5/11 |
| Qwen | 6/33 | 17/33 | 25/33 | 19/0 | 0→3→6/11 |

同事实对照严格共享候选相关规则、清理后的三值facts、动作/范围和选项，66个实际payload逐一匹配。两个状态执行器均不接金标、手定facts或另一端；执行状态之后再用同一assemble函数和本题该骨干原答案组合，原答不向任一状态执行器额外展示。程序对模型执行在两骨干均更高，支持有限规则执行器在此任务内有增量；模型执行状态与程序不同的任务分别27/33、13/33，逐项分歧和修复误伤继续在包内归因。

head在基础/新增支持/无关信息三端分别Llama5/9/7（各11）、Qwen8/11/6。新增支持能正确执行不保证稳定保持：同一病例基础→无关信息的答案集合保持仅7/11、8/11，Qwen有2个本来正确的基础端在无关端变错；这与上表“每输入相对自身普通初答误伤0”是不同配对和分母。11组中10组gold应变化，另1组增加第二个支持而保持答案；10组包含原先已成立的药物支持。

事实原文审核识别具体语义问题：Llama将eGFR当CrCl，证据检查拒绝后为UNKNOWN；新增CrCl48时仍有读取旧54的错误。Qwen第02组基础及无关端将“射血分数尚未分类”误抽为`hf_reduced_ef=false`，错误否定会删除原答中的verapamil/diltiazem而碰巧提高gold分数。句ID存在不足以保证语义蕴含。以手定事实替换模型facts、仍保留同一实际原答的离线敏感性为Llama22/33、Qwen23/33，对比实际21/25，证明不是所有表面增益都来自正确事实提取；该敏感性不是额外模型结果或保证上限。初版纯手facts/None初答36/36只检查有限规则程序，不能替代真实初答合并和资格审核。

198次新调用，输入105843、输出52979token，六worker累计449.26秒，0 length停止/0原生答案无效；等待诊断后的整队列墙钟811.10秒，包含等待，不能写成独占GPU耗时。冻结head66次缓存事实回调一致，没有新增推理。eager与2048 KV块在实际config的model_kwargs中传入旧runner；没有改权重/71规则/标签。证据：summary（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/rules/probes/summary.json`）、手定事实审核（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/rules/probes/manual_fact_audit.jsonl`）、运行及导航（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/rules/probes/README.md`）。本轮不在这些新探针上修提示、改UNKNOWN策略或挑新规则。


**两项逐例归因完成（CPU离线，无追加生成）。** 诊断94条原答与47病例已全部审阅，完整分类见诊断审核（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/diagnosis/result_audit.md`）。Llama/Qwen原答分别为：冻结正确4/20，纯名称差异2/6，同病附描述2/1，含目标多诊断25/0，过细/过粗或相关系统5/10，另一疾病或阶段9/10。34/21条冻结修复中，从“另一疾病/阶段”类别转到gold的仅4/6，不能把余下列表、名称及粒度适配一并称医学推理修复。事后只接受纯名称变体会得到6/26，但不替换原4/20；更宽松的“至少含目标身份或明确亚型”35/34包含错误备选，既不是准确率也不是官方F1，不据此选头。Llama在test211、train129、train367原回答含目标，最终头却丢失目标，因原列表已按冻结指标计错而未进入误伤数；Qwen另有train2243肺炎亚型→COPD的隐藏内容退步。

复制控制仅排除完整照抄最后Imp；以前Reason和Findings中的名字仍可利用，也没有暂隐新增Findings的配对诊断对照。因此本轮独立47仅支撑有限目录接口迁移及同资源消融，不识别新增事实利用的独立因果贡献。既往字面名称的扩展审核为Imp23、Reason24、Imp或Reason26、再含既往Findings27；原23/24冻结分层不改。

规则逐例归因见RESULTS（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/rules/probes/RESULTS.md`）。程序相对同facts模型执行：Llama修复15/误伤0，Qwen9/1；Qwen该1误伤是模型执行把未知HF当false而偶然删掉错选，不能用结果正确性证明它执行规则更忠实。Llama剩余12错分为9个UNKNOWN保留原答额外选项、2个初答将None与药物混选导致冻结程序直接回退、1个CrCl事实失误；Qwen8错均为UNKNOWN继承额外选项。模型输出在原生多选格式上可以有效，程序自己的None互斥初答检查仍可能回退，两种invalid定义分开。

实际程序MET支持路径在11组中新增10/11、11/11，既有及无关信息端的MET路径保持均11/11（第12组原先为空，另报10个非空组）；然而最终新增选项集合完整激活仅4/10、7/10个应变更组，差别来自初答继承/事实及组装。该4/7是组数而非药物选项总数。Qwen基础正确→无关端错误的两组为01与07，主要由无关措辞下初答多选后UNKNOWN保留带入；支持程序稳定不等于最终答案稳定。后续若改该策略必须重新开发后再冻结验证，本批保持所有结果与失败。


**关系M5先行完成201的阶段归因（M4仍在运行）。** 固定两臂402新调用全部完成、无无效或截断；原112，fresh redo120，target_scope122。target对redo修复18/误伤16，净+2/201（+1.00个百分点）；91-review聚类bootstrap95%区间[-5.19,+7.37]个百分点，sign-flip p=.887。原137扩展部分redo87、target86。相同target请求旧132→本次122，7修复/17误伤，31题原生预测改变、147题原文改变。已核对目标prompt逐字一致、配置相同；配对批次顺序不同，当前证据不能确定随机数、数值核或其他执行细节的具体原因，不把单次重复差异归因定死。该骨干尚不支持稳定的目标指令增量，不能只拿旧target132对新redo120作为本轮单因素对照。最终联合判断等M4完整范围结束，不重跑择优。证据`relations_control/m5_completed_summary.json`，M5记录402调用、输入4922369、输出86833token、worker1427.28秒（含53.38秒初始化）；与后续联合表为同一批预测，成本不重复计。


<a id="r1-frozen-relations-results"></a>

#### 关系201完整归因：M4有增量信号，M5未确认

18:28:32，804次新调用后的联合离线分析退出0，最终核查完成，相关协调器与worker均退出。此表用两臂本轮新生成的结果；旧target只用于独立的重复性观察。

| 方法 | 原答案 | fresh redo | 固定target_scope | target对redo修复/误伤 | 净增（百分点） | 91-review聚类95%区间 |
|---|---:|---:|---:|---:|---:|---:|
| M4 | 100/201 | 102/201 | 118/201 | 34/18 | +7.96 | [1.03,14.93] |
| M5 | 112/201 | 120/201 | 122/201 | 18/16 | +1.00 | [−5.19,7.37] |

cluster sign-flip p分别.0431/.8867；区间及检验用预定10000次、seed20260918，按91个original_review保留问句簇。它们是已暴露范围、单生成种子、未做多重比较校正的描述性统计，review ID还可能共享临床原研究，不据此称为独立临床显著性或跨骨干稳定效果。M4支持目标指令超出普通重答的增量；M5未确认。原137扩展部分M4 redo72→target82（+10），M5 87→86（−1）；不能只保留两个骨干各自较有利的分层。原pilot64为30→36、33→36；R5重合118为57→69、67→70，完整分母见机器结果。

唯一无效为M4 redo `s003566`，在2048 token解释重复中截断、没有`answer_choice`，冻结解析为malformed JSON；同题target输出lower而gold为no difference，也错误，所以该截断不贡献target相对redo的+16修复/误伤。保持原输出、分母和评分，没有修复文本或重跑。证据invalid_audit.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/relations_control/invalid_audit.json`）。

相同target请求的旧→新正确数为M4 123→118、M5 132→122；分别7修复/12误伤、7/17，原生预测改变35/31题，原文改变128/147题。逐字prompt和token长度相同，配置直接复制，新旧复用同一run_model；LLM及每条SamplingParams均显式沿用seed/temperature/top_p/top_k/max_tokens，未发现漏seed或提示漂移。配对批次顺序不同，但变化具体原因未识别，不能断言某个数值核或随机机制导致。seed42不是逐字确定性的保证；没有追加种子、重复到满意或改prompt。

**收尾调度失败也保留。** M4完成后，旧串行协调器在采用已完成GPU1 M5状态之前先检查GPU3空闲36800MiB，触发已无必要的40GiB加载门槛而退出。此时两模型804输出均已保存，0额外调用、0新加载；直接离线执行analyze/finalize成功，未重启模型。原失败在`failures/post_m4_stale_gpu3_guard/`，恢复退出状态见`offline_analysis.json`；启动期GPU0资源门槛失败也继续保留，两次检查的额外墙钟耗时未记录，不补造为精确0。

本分支实际输入9556230、输出184731token；M4/M5 worker3904.99/1427.28秒，合5332.27秒，含加载与共享卡争用；1 length停止和1无效是同一输出。M5先行表是本次同批预测的阶段分析，成本不另加。结果/分层/配对/旧target重复性/成本：summary.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/relations_control/summary.json`）、逐题评分（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/relations_control/scored.jsonl`）、运行导航（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/relations_control/README.md`）。关系仍只验证M4/M5、201问句族，未用它替换七方法全788关系项或2866主表。

<a id="r1-frozen-validation-complete"></a>

#### 本轮完成判断、成本与论文主张

用户授权的冻结后验证与关键对照本轮已完成：方法先冻结，资格先于预测，固定范围全部生成和评分，控制与负结果保留。新增模型完成调用**1660**，输入**10324120**、输出**250093**token；累计已记录worker **6218.68秒（1.73小时）**，不是独占GPU小时或整任务墙钟。CPU冻结入口回放630次（诊断564＋规则66）、同facts载荷66条一致，不计新模型调用。全部本轮GPU作业和离线分析均结束。

| 阶段 | 新完成调用 | 输入token | 输出token | 已记录worker秒 |
|---|---:|---:|---:|---:|
| ASCENT47×两骨干 | 658 | 662047 | 12383 | 437.15 |
| 规则33端×两骨干×三阶段 | 198 | 105843 | 52979 | 449.26 |
| 关系201×两骨干×两臂 | 804 | 9556230 | 184731 | 5332.27 |

成本按完成原始调用计数，输入累计不扣前缀缓存节省；兼容依赖失败和两次调度检查失败均0新完成调用，缺失耗时明确保留。准备脚本的两次失败及暴露语料范围纠正归构建记录；模型/调度失败归本节和制品，不把失败历史改写为首次成功。全轮汇总（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_validation/summary.json`）由同包`summarize_validation.py`从三个完成summary离线收集，不混合三个不同任务的准确率。

**论文结论应收窄到证据支持的组件。** 新诊断数据支持固定49目录接口可迁移，但head与单次目录整体同分，旧先验校正没有带来额外准确数；投票有局部修复及宏平均变化，尚未形成稳定额外微准确率增益。自由生成的巨大canonical分差混合列表、命名和粒度，不应写成临床推理大幅提高。33端规则实验支持程序执行超出同facts模型执行的价值，同时暴露UNKNOWN继承和有利事实错误；它没有填补独立临床泛化。关系目标提示在M4有增量信号，M5未确认且同请求重跑有波动。因此当前可写有限任务组件、明确的机制对照与限制；“跨任务泛用R1新增支持推理头”仍未被这些结果建立。

本轮不据新验证结果重选策略或改已有头。若进入下一开发轮，优先研究已确认的UNKNOWN合并、事实语义蕴含，以及与原生多诊断/粒度相符的评价；调整后需要新冻结病例。该方向是后续优先级，不是已执行修复，也不把刚暴露的47/33重新称为新holdout。关系额外提示的跨骨干稳定性、诊断是否真正利用新增Findings，以及用药独立临床病例仍是未解决证据缺口。


<a id="r1-cross-head-evidence-audit"></a>

## 2026-09-16：R1/R2同口径交叉审计完成

**完成；本轮新增模型调用0。** 用户要求读取指定会话并对此前R1、R2做与现有归因/验证相同的检查。会话`01a0a866-0afc-7803-a5d3-a915d7b45e1b`实际推进R1，`01a09dd7-8667-7ab0-8a9e-7051b56031e7`保存此前R2/R3探索。分工全文读取R1/R2/R3主记录、两会话的可读真实消息及有关协议、分类和构建章节；历史快照、原行号与阅读边界见历史审阅附件（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/history_scope.md`），没有把113MB日志中全部工具输出称作逐字通读。另一会话正在进行的[定向开发](#r1-postvalidation-refinement)由原任务继续记录，本次固定核查已交付主候选和第一轮冻结验证。

### 本轮新增的实现与制品核验

最小CPU审计脚本（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/r1_verify.py`）用于检出主表/基线版本漂移、隐藏元数据依赖和缓存结果不一致；若失败则定位具体输入并修正结论，不重跑模型择优。实际结果全部通过：

- 当前2866×7＝20062条原基线逐项与正式选用源一致，140个来源/重合/保持分层由逐题制品重算一致。
- 只传`question/options/answer_format/fixed_evidence`，不传题号、gold、分类或来源字段，冻结入口仍重现全部20062个答案、分支及原生评分。每方法1780目录、72规则、1014透传；74760次疾病分布缓存和504次事实缓存回调，新推理0。
- 11个推理模块与第一轮验证的`frozen_head`逐字一致。事实请求messages/schema逐项一致；诊断本轮使用既有分布并核对原上下文，不重复进行此前已完成的tokenizer渲染审计。新核验不代替真实生成或临床语义重审。
- ASCENT47、规则33端、关系201各臂的逐题分母和正确数也独立重算吻合，见r1_validation_verify.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/r1_validation_verify.json`）；未重跑模型或重复统计区间计算。

CPU核验实际11.92秒，收据为r1_verify.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/r1_verify.json`）；完整冻结审阅见r1_audit.md（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/r1_audit.md`）。未发现需改写旧主表的错算或运行时按gold/R标签查答。原模型、head、评分和正式v5均未修改。

### 跨类别重合与同一结果的一致性

新增交叉脚本（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/audit_overlap.py`）直接连接冻结evaluation与三个交付包，目的在于避免把重合结果当独立证据，以及识别同题复用不一致。R1∩R2为4题（s001111/s001115/s001121/s001125），R2∩R3为其中3题，R3的733题全部包含于R1。三个类别3678次成员计数对应2941个唯一比较单元，不能相加声称3678个独立病例。R1/R2的28条、R1/R3的5131条及R2/R3的21条方法×输入，其答案、正确性和invalid全部一致；完整ID和结果在cross_head_overlap.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_r2_evidence_audit/cross_head_overlap.json`）。这证明交付包复用一致，不是新的泛化证据。R2详细审计归[R2主记录](r2_support_head.md#r2-cross-head-evidence-audit)。

### 既有成果与证据缺口的复核结论

[2866主表](#r1-core-head-delivery)的七方法开发提升成立，剥离旧733后新增2133范围仍各净增261–319题。主要贡献是目录决策及有限规则迁移；1014题透传，R1内450个R5重合题亦透传。不能据此宣称跨所有任务的R1机制或完整R5无害性。

同资源对照应继续保留：1780诊断六票相对单次目录在七方法微准确率均提高；先验校正相对六票却有M2 −27、M7 −6，不能称每个组件在每个方法均有效。冻结ASCENT47的完整头与单次目录同为Llama38/Qwen39，原生多诊断/别名/粒度与项目单标签评分的差异仍阻止把自由答4/20到头38/39称医学推理大幅提高。33端受控规则探针的程序21/25对同facts模型6/17支持范围内执行增量，但不能冒称独立临床R2或R1验证；事实误抽、有利错误及UNKNOWN继承已在原归因中保留。关系201的普通重答对目标提示为M4 102→118、M5 120→122，仍是已暴露数据上的有限归因，未加入七方法主候选。

以上缺口大多已由此前实验发现，本轮没有将其改写为新的失败或撤销已有开发成果。下一步研究优先级仍是语义可靠的事实提取、明确问句下的UNKNOWN合并、匹配原生任务的诊断评价以及新冻结范围；另一会话已经在推进前三项，本次不重复启动GPU。


<a id="r1-postvalidation-refinement"></a>

## 2026-09-16晚：冻结验证后的定向开发

**启动与范围（计划/准备中）。** 用户要求按已确认问题继续实验，并授权在其他可用GPU并行。上一轮明确暴露了三类问题：规则支撑已正确但UNKNOWN沿用原答；事实引用合法但语义不蕴含；诊断自由多标签输出与单目录评分不等价。本轮分别干预这三层，不新增多臂网格，也不据新分数改写上一轮冻结结论。旧47 ASCENT与33规则端已用于诊断，所有复用成绩均属于开发；来源资格、排除和暴露沿革继续保留，正式v5与旧frozen_head保持。

预定工作：①CPU复用真实原答与缓存事实，对比冻结组合和至多两种问句语义约束的组合；检查旧R1/R2/R3可得缓存回归，未被规则覆盖的选项不能被无条件删去。②预先固定一个字段证据蕴含提取提示，重点针对否定越界、CrCl/eGFR变量串用、疾病由讨论推断等已确认问题；在两原骨干上新运行，与冻结facts及相同组合策略成对比较。③47例原生输入新增不提供49目录的单当前诊断输出控制，两骨干94次计划调用，拆分命名/输出约束与目录资源收益；源官方语义评测可用性先核实，不把canonical未映射当医学错误。

资源实查：GPU1的82236MiB进程是本用户`gpu_watch.py`80GiB预留，PID1015441、父PID1015382，18:27:22持有，计划20:27:22释放；没有运行模型实验。新worker准备就绪后停止此预留监督器并将GPU1交给实际计算。GPU0另有用户小显存高计算任务，GPU2/3有其他用户模型，保持这些作业运行。独立分工负责组合、事实和诊断，根代理统一资源与主记录。

证据包：[r1_head_refinement](../../evidence/r1_head_refinement.md)，预先范围为plan.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/plan.json`）。实际尝试、失败、资源和分数在完成关键阶段后追加。

推理前细化：事实臂固定每骨干33受控端＋55旧R2实际覆盖题，共176调用；诊断94调用，合计270计划新调用。组合两个新候选都保留无适用规则路径选项的有效原答：即便题目限定已记录支持，也不能把有限71规则缺项当作完整AGS阴性；两候选只区别是否要求末问明确建立支持，广域候选仅作诊断对照。旧全MET策略保留为历史控制而不重新包装为新方案。事实候选保留旧options可见性，避免同时改变可见信息和提取表示；记录为证据短引用＋显式蕴含状态的组合设计，不单独归因于字段次序。两分支计划在GPU1各用`.45`全卡预算、eager、固定2048KV块并行，每支顺序处理Llama/Qwen。

资源交接已执行：19:20:14对本用户预留监督器1015382发送SIGTERM，其finally正常释放holder，状态`stopped`/`holders=[]`，GPU1空闲97367MiB；没有终止模型或他人进程。诊断持久queue PID1040377于19:20启动，首M4 worker1040411加载；resource_handoff.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/resource_handoff.json`）保存实际操作。CPU先完成1291条原head回放一致（66探针＋672 R1＋553 R2）；广域covered-support对旧R1出现每method1–5误伤，M4 58→56/96，不因总分局部提升忽略伤害。明确支持门控初版漏掉`established renal indication`插入词，30/33触发，保留首次制品后修正此已预定范围实现并重算；此修复发生在已见开发输出后，不能称冻结独立结论。



### 无目录诊断输出控制完成

两原骨干各47次，完整原生上下文不变，追加同一条要求：在最后Findings阶段给出证据支持且粒度适当的一个疾病/系统名，不列鉴别、替代项或无依据亚型，仍使用boxed。不提供49目录；temperature0.7/top_p1/top_k−1/seed42/max_tokens2048/batch8保持，资源预算改`.45`。预先解释此控制改变原任务允许复数的输出约束，不能当ASCENT原生任务的等价替换，也不是单独的目录因果消融。

| 骨干，n=47 | 旧原生自由答 | 新无目录单名 | 旧单次目录order0 | 旧校正六票 | 单名相对自由答修复/误伤 |
|---|---:|---:|---:|---:|---:|
| Llama/M4 | 4 | 27 | 38 | 38 | 23/0 |
| Qwen/M5 | 20 | 22 | 39 | 39 | 8/6 |

这是相同冻结canonical-name评分的开发成绩。94新答全部完整boxed、单个最终回答，0截断；单名相对order0仍有M4 13修复/2误伤、M5 17/0，方向为从单名变目录。Llama不提供目录也上升23题，支持输出形式/目标阶段指令能影响巨大旧分差；Qwen6个反向变化说明不是无伤通用修复。与目录臂还同时存在候选资源、请求结构和单token概率决策区别，不能将剩余差距全部归为目录或临床推理。

作者官方逐实体语义P/R/F1要求外部GPT‑4.1五次判断，当前没有这批新臂的既存判断或忠实本地后端，本轮未调用外部API；不将未运行写成已确认鉴权失败或凭据缺失。名称别名、多诊断、粒度和阶段/病因答案分别审阅，未按gold逐题扩充评分映射。94新调用输入35677、输出932 token，两worker含加载71.93秒；诊断于19:22前完成，快于另一分支准备，实际两类模型worker未重叠，不把计划并行写成已并行完成。facts持久queue1043279随后在GPU1运行176请求，初次加载17.35秒。证据：诊断预先方案（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/diagnosis/prepared.json`）、诊断汇总（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/diagnosis/summary.json`）。

新提取Llama先完成88调用，其中group12 base/irrelevant两条达到2048上限。代理中途先推测解析失败，随后目测误判为完整JSON后接空白；根代理实际`json.loads`复核确认均缺最外层闭括号（4开/3闭），去尾空白后280字符、总5494字符，严格解析确实失败。保留原输出、错误与回退，不补括号或重跑；根复核证据（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/facts/length_output_root_audit.json`）。模型length、JSON失败及最终答案invalid分开统计，不能凭看到字段内容就当结构完成。

### 同事实答案组合对照完成

原head在1291输入×方法记录逐条复现（33×2＋96×7＋79×7）；三个政策合计3873条离线评分，0新模型调用。R1与R2实际共享s001111/115/121/125四题，R3用药10题是R1子集，不能合并为独立样本。候选A仅末问明确只据记录、要求已建立理由/指征时，将有适用规则路径的选项限制为MET；无paths选项仍沿用有效原答。候选B取消问句门控，其余相同。数值、事实、规则及默认例外政策不变。

A在33端：Llama21→28，7修复/0同题误伤；Qwen25→33，8/0。三端全对组5→7/11、6→11/11；基础与无关端答案不变7→9/11、8→11/11。Llama基础正确→无关端错误新增1组，是基础先被修对而无关端仍错，与同题无误伤不同。剩余5错为2次保留无规则Amlodipine、2次原None＋药物冲突且覆盖不足而整体回退、1次CrCl漏提取。手事实加同实际原答得到29/33、33/33，只是敏感性，不能称模型上界。Qwen即使修正此前有利false-EF事实也仍33/33，因此最终满分不证明facts语义无误。

A对96×7旧R1、79×7旧R2均不触发，逐条保持；这证明当前改动范围狭窄，不是在真实临床题中验证了新选择政策。B的原R1七方法正确数66/58/60/58/57/62/56→65/58/61/56/58/62/59，合计18次方法×题误伤；原R2 29/23/43/39/46/38/37→35/32/52/50/49/44/46，但s001086的M0/M3/M5仍被误删Prochlorperazine。

**覆盖必须看具体支持路径，不能只看药物有无规则。** s001132中gabapentin/pregabalin有跌倒规则，题面真正支持来自与现用oxycodone的组合；s001140有TMP-SMX肾规则，原题涉及现用phenytoin。B因已有路径UNKNOWN而删去本应保留的药物，虽然没有删除“完全无paths”的选项，仍犯了不完整知识覆盖的错误。s001128/134/142/144的现用药相互作用、s001075未明确激素途径也有实测伤害。没有按item或R标签加例外掩盖这些失败。A保留为明确问句的开发机制候选，B不全域采用；原R1/R2/R3接口不替换。

CPU两次准备失败分别是Python3.10不支持星号下标语法、诊断统计对真实单选R2行执行None-membership；均在完成评分前修复，日志保留。首次门控缺renal的30/33结果26/31，以及修正后的28/33，都在组合固定报告（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/composition/RESULTS.md`）与`before_renal_gate_fix/`保留；事实输入和评分没有改写。

### 新事实提取与2×2归因完成：不采用该提取候选

每骨干33端＋55实际覆盖题共88次新生成，176次均实际完成。固定一个候选：保持旧字段定义、positive aliases、options可见性、71规则、scope和原答，改为先输出所引句中的短原文，再输出established/ruled_out/not_established或数值；逐字引用与变量检查后映回原三值事实。此为表示/提示/引用检查的组合，不是单独字段次序因果实验。温度0、2048输出预算保持，结果后没有再调prompt或补跑。

| 骨干 | 33端旧facts＋旧组合 | 33端旧facts＋A | 33端新facts＋旧组合 | 33端新facts＋A | 旧R2全79，旧→新facts |
|---|---:|---:|---:|---:|---:|
| Llama | 21 | 28 | 20 | 23 | 39→36 |
| Qwen | 25 | 33 | 22 | 31 | 46→42 |

固定旧组合，33端Llama1修复/2伤、Qwen0/3；R2全79分别0/3、0/4。固定A，新facts在33端为Llama1修/6伤、Qwen0/2。完整2×2是619输入×方法配对、2476离线评分；55新facts按既有同骨干映射接七方法，全79依序M0/M2/M3/M4/M5/M6/M7从29/23/43/39/46/38/37→25/18/40/36/42/33/35，各0修复、2–5伤。24未覆盖题仍回退同原答并保留在79分母。A不触发真实题，不能将其无变化称临床安全选择器已验证。

**失败包含表示与事实语义两层。** Llama把第01组三个小写`a 69-year-old woman`改成大写A导致年龄引用被拒，漏掉第07组已明确doxepin10；Qwen第07组剂量及第12组CrCl48原始值正确但引用添词/改写被拒。Llama已修回新增CrCl48，但第12组基础/无关两次缺闭括号失败；Qwen s001076在首字段输出重复空白达2048，第三次真实JSON失败。严格解析失败分别2/88、1/88；引用拒绝21/27字段；最终33端invalid均0、原R2全79 invalid为3/10，不能将最终回退答案有效与抽取成功混同。

两骨干33端全部已改变的成功抽取字段另做人工解释，加整体JSON失败：Llama16字段退步、1改进、2条整体失败；Qwen7字段退步、5改进、2次拒绝后值改善。这些是已变字段审核，未覆盖不变字段，不是全facts精度。Qwen未分类EF两项clean false→null来自模型仍输出ruled_out却无证据而被拒，不能称语义推断已正确。证据`facts/probe_changed_field_audit_summary.json`及逐字段原文。

根在生成前通读33探针及55实际题，并对真实R2全部13个答案变化（Llama6/Qwen7）全文复核：共7次正确→错误，无修复。s001107明确无HF却提为null；s001117男性及尿路用途丢失；s001121明确溃疡史因生成引用提前闭合括号被拒；s001076为格式失败。精神分裂/双相病例的AP accepted indication由true→null，使默认推荐例外失效；这涉及“当前诊断”到“拟用药目的”的任务语境绑定，不能仅据gold将所有null判为医学错误。并列否定被展开成非原文完整句也会被逐字检查拒绝，单纯大小写不解决。逐题见根原文复核（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/facts/root_native_answer_review.json`）。

仅大小写恢复的后验敏感性0新调用：只有case-insensitive完全相同子串才恢复原文字母大小写，不改数字、否定、词序、括号或JSON。共4条引用被恢复，33端strict20/22→21/22，原R2仍36/42；未挽回结论。它与严格主结果分开保存，不为保留候选扩大容错规则。

分析本身的失败也保留：初始known-fact审计用`.get(field)==None`可能把缺整份facts的失败当正确，改为要求字段实际存在；原审计及summary保留initial_*。初次changed_answers因tuple/list表示差异把169条当变化，根复核后规范化比较，实际19条（探针6＋真实13）；原错误文件保留，所有模型输出和主准确数不变。诊断CPU审阅脚本一次重复keyword语法错误修复，0新调用。一次根定位大小写敏感性文件误用路径，随后按实际目录读取，未改数据。

### 本轮取舍、成本与结束状态

保留A作为明确已记录支持问句的机制开发候选；不采用新事实臂，也不全域采用B。B在R2七方法56次修复中50次落在gold-None66题，3次伤害均在保留9题；R1全部96 gold均含实质选项，其预测None反而增加。不得按不可见R1/R2标签切换政策规避这些失败。真实问题是支持路径覆盖及事实/拟用目的绑定，不能只靠增加引用要求或更积极删UNKNOWN解决。

诊断94新答完整审核后，Llama从自由答到单名的23修复分解为旧含目标列表19、同病描述2、名称2，0来自旧“不同疾病/阶段”；Qwen8修复伴6伤，包含bronchiectasis→cystic fibrosis等内容改变。目录order0相对单名的剩余修复也混合名称、粒度与不同疾病/阶段，详见[诊断完整审阅](../../evidence/diagnosis_refinement_results.md)，不将canonical分差改称官方临床推理F1。

实际新增完成**270调用**（诊断94＋facts176），输入**156959**、输出**55768**token，四worker含加载累计**369.77秒（6.16分钟）**。CPU原head回放1291条，组合3873评分、2×2另2476评分及大小写敏感性均不重复计模型调用。GPU1预留正常交接后运行所有worker，两个模型分支因诊断先快速完成而实际顺序，CPU分析并行；没有使用或终止他人GPU进程。结束实查GPU1占用0MiB、空闲97367MiB，两个持久queue均complete，相关PID均退出。主汇总由summarize_refinement.py（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/summarize_refinement.py`）核对270调用和两个完成状态后写summary.json（本地来源：`/home/data3/txy/Documents/Codex/2026-09-16/r1_head_refinement/summary.json`）。

本轮计划及追加的必要归因均已完成，旧frozen_head与正式v5保持。局限集中为：新策略只在已暴露开发探针有效；没有新独立临床holdout；71规则支持路径不完备；诊断未完成作者外部语义评价。下一阶段若继续形成新版，应先解决药物具体支持路径和拟用目的绑定，并在候选/评分固定后用新病例验证；该后续方向尚未实施，不将本轮开发重称独立确认。
