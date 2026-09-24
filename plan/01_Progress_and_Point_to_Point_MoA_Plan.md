# CF-MoA 候选验证进展验收与点到点收口计划

**日期：2026-09-24。对应第15章，截至当日14:03:26完成的运行。**

**当前决定：保留 `candidate_with_rationales` 为唯一主研究候选，停止改造其提示与算法；把它接入五操作系统，完成同资源对照、完整任务评价与冻结后验证。旧默认 B 继续保存为基线，不用新的结果覆盖它。**

本文是实施计划，不代表在本次会话中已经修改远端代码、运行GPU或完成新的医学评分。核读范围为新报告第15章、运行说明、公开结果/反例及实际验证器、runner、控制和评分代码；私有病例全文仍在原服务器，不重新要求用户导出。

## 1. 本轮究竟完成了什么

本轮不是又一个未能生成的原型。95个已触发的输入—骨干组合复用，88个普通投票组合中的195个不同候选接受了两实验臂、两种编码的780次真实取分；其余7组NLI按原F返回。得到176条验证输出、14条NLI直返，全部190条完成。新方法没有重新生成长答案，也没有覆盖R1–R4和原F。[S1][S2]

| 完整范围 | B正确输入 | 无理由验证 | 带理由验证 | B原生单元均分 | 带理由原生均分 |
|---|---:|---:|---:|---:|---:|
| 历史121 / M4 | 87/121 | 87/121 | 88/121 | 70.27% | 71.62% |
| 历史121 / M5 | 82/121 | 83/121 | 87/121 | 64.41% | 68.92% |
| 自然52 / M4 | 35/52 | 33/52 | 35/52 | 60.37% | 66.67% |
| 自然52 / M5 | 26/52 | 27/52 | 28/52 | 49.26% | 48.15% |

无理由合计18修复/18误伤；带理由17修复/9误伤，即跨这些开发范围和骨干净增8个正确输入。71组池中含正确键时，B与无理由均选择正确38组，带理由46组。17组没有正确候选，选择器没有扩展候选能力。[S3]

**结论：候选理由辅助选择出现了可保留的开发信号，但没有证明稳定泛化；既不是全部失败，也不是已经完成论文主结果。**

### 1.1 为什么自然M5多对两题，原生分反而低

原生单元不是每个输入等权。该臂在两个五输入单元分别改善0.4，在另一个独立单元损失1；参考端不计入原生ALL。于是18单元等权差值为 `(-1+0.4+0.4)/18=-1.111` 个百分点。这不是评分错误，不能把主指标改成正确输入数来消除它。[S1]

### 1.2 还没有解决的三件事

1. 保持配对未一致提升：历史M4 48→47、M5 44→46；自然M4 17→16、M5 10→9。应变只有4/2对且未增加新证据。[S1]
2. 原生完整字段没有一起改善：自然M4有旧候选的非法document集合被选回，辅助valid 12→11；主答案正确不能当作文档检测/纠正都正确。[S1]
3. 当前提供的是各方法绝对配对指标的区间，还没有新方法相对B的**配对家族差值区间**。用两个绝对区间是否重叠判提升是不正确的。[S1][S8]

### 1.3 执行是否偏离计划

方法层面基本没有：全候选、最早完整响应、双编码归一、不给票数/F赢家、不新生成答案、NLI不转票、保持完整分母，均已落实。[S4][S5]

有真实工程故障：首次32次初始化失败未及时中断共享引擎；重复record_id和空NLI分母分析出错。限定修复后780次真实取分全部完成，没有证据把现有质量差异归为打分实现错误。此前的失败与本次成功分别保留即可，不再重做整套防护或以此解释语义误伤。[S1][S2]

## 2. MoA最终定位：固定能力路由 + 五操作专家 + 局部候选聚合

工作名建议：**CF-MoA: Routed Counterfactual Operations with Rationale-Guided Candidate Verification**。

原MoA强调后层利用多份模型输出；Self-MoA表明同一骨干也可构成多提议者系统。我们的具体系统应写成**工具增强、按操作路由的稀疏框架**，不能宣称五套独立训练模型或五位专科医生共同诊断。[P1][P2]

当前的确切结构：A1/A2共享一份规则执行，A3使用目录比较，A4执行题内明确模型，A5产生稳健候选；候选验证器是A5内部的选择/聚合阶段或控制层，不额外命名第六位医学专家。

如果最终论文坚持“五个互相独立的LLM agent，每题共同讨论”，现有实现不满足该主张；不能靠改变图中名称满足。当前最简路线是保留五个**操作职责**，把实际新增贡献限定为有理由的候选选择及其在整体框架中的应用。

### 2.1 五个角色与已有代码的对应

| 角色 | 实际功能 | 当前来源 | 新增工作 |
|---|---|---|---|
| A1 支持建立 | 保存MET支持，补入未选但成立的项 | `minimal_operations.rule_operations` | 注册角色与输出记录，不再训练泛用支持审计 |
| A2 支持撤销 | 保存失效路径、删除失效已选项、保留UNKNOWN合同 | 同一次旧规则执行 | 同A1共享抽取与执行，不重新算一遍 |
| A3 候选比较 | 固定目录评分、校正和原生映射 | 采用A3及旧R1入口 | 直通，不再加自由诊断改写 |
| A4 后果执行 | 完整给定模型与状态中的typed intervention | 采用A4 | 保留条件范围，不能替代HIV等无完整模型任务 |
| A5 稳健回答 | NLI原双路径；其他支持任务原F采样/投票 | 采用 `run_legacy` | 普通投票有分歧时接当前RCV验证器 |

A1/A2是操作分解，不是两个新独立算法。形式上，合法普通实体集合下，`add = MET - S0`，`remove = CONTRADICTED ∩ S0`；最终仍调用旧assembler处理None、UNKNOWN和特殊政策，而不是自己重写组装。[S6]

### 2.2 在线调用图

```text
当前题 + 原生格式 + 允许的原上下文 + 同题初答
                 │
                 ▼
       strong_legacy.select(packet)
        ├─ diagnosis              → A3原目录 → 原生输出
        ├─ 原规则eligible          → A1/A2共享执行 → 原assembler
        ├─ 完整显式模型合同        → A4原执行器 → 原生输出
        ├─ F支持的格式/上下文      → A5采用F
        │                            ├─ NLI → 原F直接输出
        │                            ├─ 普通票K<2 → 原F直接输出
        │                            └─ 普通票K≥2
        │                                 → RCV逐候选两编码取分
        │                                 → 返回胜出候选整份响应
        └─ 未覆盖                  → 原兼容透传
```

路由顺序严格继承现有 `strong_legacy.select`；不依据R标签、家族、source_id、reference身份、输入编号或已知对错选分支。[S7]

**不再增加全局生成式裁决。** A1–A4结果不经过A5验证器重写。多个旧F回答之间的选择就是当前真正被验证的跨输出聚合；还没有证据声称多种专科/五个不同操作在同一道题上联合带来增益。

## 3. 剩余工作总表：输入、修改点、产物与验收一一对应

| 编号 | 任务 | 使用哪些现有内容 | 必须产出 | 是否新增模型 |
|---|---|---|---|---|
| P0 | 固定唯一主研究候选与对照 | 本次两个arm、旧B与已存控制 | `research_method_spec.json` | 否 |
| P1 | 补相对B的家族配对差值 | 原始native映射、单位分数、pairs与family | `paired_effects.json`、风险/收益分层 | 否 |
| P2 | 把saved-F实验接到完整在线系统 | 现有minimal入口、F、验证器 | 一个新的薄控制器，cached/live两路径 | 仅小型在线连通验证 |
| P3 | 补足五操作覆盖与方法消融 | 旧工具缓存、冻结v5全部合法输入 | 覆盖矩阵、规则操作消融、R4分表 | 缓存不足及新验证部分 |
| P4 | 同信息/预算对照 | 相同候选池和原生合同 | 固定比较矩阵与质量—成本表 | 必要控制的缺失调用 |
| P5 | 扩到完整任务及冻结后新范围 | v5与真实暴露清单；未用于选择的合法家族 | 开发回归、冻结后评价、独立身份清单 | 是，复用B只执行增量 |
| P6 | 完成论文叙事和交付 | P1–P5真实结果 | 架构图、算法、五张主表、局限与运行入口 | 否 |

P1和P2可并行，不把“所有微小分层都显著上涨”设为集成前置条件。新的候选需要真实扩大评价，而不是在已经暴露的小面板上调到全部上涨。

## 4. P0：固定研究版本，不等于立即替换默认B

### 输入

本轮实际代码 `agents/a5_candidate_verify.py`、`plan/runtime_plan.json`、`data/decision.json`。

### 具体决定

- 主研究候选：`candidate_with_rationales`。
- 必备消融：`candidate_only`。
- 强基线：`adopted_B_five_operations_v1`。
- 普通重答替换：继续关闭，不再用于主方法。
- 参数：双编码分别归一后平均；全部不同合法候选；每键最早完整响应；精确平票优先旧F。
- 不新加阈值，不按骨干/来源选择表现最好arm，不把n00014等个案加入路由黑名单。
- 不增加长理由生成、局部编辑或额外检索。当前候选只使用已经存在的合法资料与F响应。

`ModelSession.score`本来按temperature=0、max_tokens=1执行；原F生成仍保持自身0.7等采用参数。不得为了“统一配置”把两者改成一样。[S4][S5]

### 产物与完成条件

新研究配置和一页方法合同，写清角色、路由、F候选来源、verifier、输出与成本。源码和实际提示与本轮一致。旧默认配置不覆盖，新研究入口可被显式选择执行。

**不要把“不默认采用”理解为“不能做主研究候选或不能扩大评测”。** 前者保护历史结果身份，后者是正常科研流程。

## 5. P1：只补缺失统计，不再重评分780次请求

### 5.1 数据连接

现成可用：`quality_summary.json`、`per_input_status.jsonl/csv`、`native_scoring_metadata.jsonl`及服务器对应完整 `native_scored.jsonl`、原 `evaluations.jsonl`、`pairs.jsonl`。

用 `(panel, model, record_id)` 对齐相同原生评分映射；用现有evaluation中的unit关系构造原生单元；用已保存request→family连接到母题。不能靠拆字符串猜family，也不能把reference端强加进ALL。

报告中的 `quality_summary.reports[].native_unit_metrics.units` 已给出评分单元。过滤 `category == ALL`，避免同一单元因为R标签共现被重复加入。

### 5.2 新计算

主效应：`mean_native_unit_score(RCV) - mean_native_unit_score(B)`，面板与骨干分开。保持和应变指标分别计算相同合格pair上的 `both_correct_RCV - both_correct_B`。

进行5000次配对family bootstrap：同一次抽样对B/候选取相同家族，连带取该家族所有原生单元/pair。每次按照原生单元原权重重新计算差值，**不擅自改成家族均分或端点均分**。

输出各层的点估计、95%差值区间、家族数、单元数、修复/误伤以及leave-one-family-out影响。区间不能抵消已经根据这些数据选方法的偏差；这仍是开发条件下的描述性区间。

### 5.3 风险定位

对新带理由臂的全部17修复和9误伤使用现成私有trace逐例读取，而非只看四个smoke例子。记录：候选集合、两编码分数、正确/错误响应中的实际理由、主任务范围、辅助字段。

分类只能写“在文本中观察到的现象”或“待验证假设”。例如n00014已有理由读到了NOT，不能虚构成漏读否定。评分0.985仍可选错，不应据此直接设置0.9信任阈值。[S9]

原生辅助valid/exact已有分数原样报告，暂不加“辅助错就取消主答”的防御门。后续若研究联合任务，应单列完整响应适配改版，双方用同一可见schema规则处理，不能事后按gold修字段。

### 5.4 可直接使用的统计脚本

随包 `paired_cluster_effects.py` 不读取病例和gold答案，不调用模型或原grader。输入是按现有评分合同整理后的JSONL，每行一个原生单元或合法pair：

```json
{"panel":"natural52","model":"M5","metric":"native_ALL","candidate":"RCV_rationales_v1","family_id":"真实母题ID","atom_id":"真实原生unit_id","baseline_score":0.2,"candidate_score":0.6,"weight":1}
```

对pair另设 `metric=maintain_both_correct` 或 `respond_both_correct`，atom_id用真实pair_id，baseline/candidate写0或1。缺失/失败如何入分必须遵循旧评分，不由脚本删掉。

```bash
python paired_cluster_effects.py --input paired_atoms.jsonl \
  --output paired_effects.json --resamples 5000 --seed 240924
```

本会话只通过了10项合成单元测试，没有将该脚本运行在私有完整家族数据上，也没有获得新的真实置信区间。

### 完成条件

已有四格原生点估计复现，包括自然M5 −1.111个百分点；输出相对B的差值区间而非两份绝对区间。0新增模型调用，不要求所有区间都大于0才能进行P2。

## 6. P2：明确改哪一个文件、接哪一个函数

### 6.1 已确认的断点

当前 `evaluation/candidate_verify_runner.py::load_plan` 从95组保存样本读取packet、B和F提议。它已经正确测试了候选选择，但仍是**固定旧候选池上的实验入口**，不能用它冒充“每道新题从头生成F候选再验证”的完整系统。[S5]

当前 `controller/minimal_operations.py::run` 已经会按Router真实调用旧A1/A2/A3/A4/F，但可选F增量仍是旧 `a5_premise.run(control=True)`。新候选验证应接在这个F调用之后，而不是另起一套通用controller。[S6]

### 6.2 建议修改边界

优先新建 `controller/moa_rcv.py` 薄入口，或在minimal入口增加明确的实验mode而保持旧默认不动；二者择一实现，不复制旧head执行代码。建议新增：

```text
cf_moa/controller/moa_rcv.py          # 薄整合入口
cf_moa/configs/moa_rcv_v1.json        # 新研究版本
cf_moa/evaluation/run_moa_rcv.py      # 共用旧native runner、journal、backend
```

上述是建议新增路径，不是声称仓库已有同名文件。

### 6.3 F分支唯一新增调用

```python
# 插入现有 component == 'F' 分支，采用F只执行一次。
proposal = old_f.run_legacy(packet, session)
native = proposal.native_proposal

verification = a5_candidate_verify.run(
    packet,
    session,
    base_native_answer=native,
    saved_proposal=proposal.to_dict(),
    include_rationales=True,
    config={"seed": 42},
)
native = verification["native_answer"]
```

该调用签名已由公开实际代码核对。其内部已经处理NLI、无分歧、原F不可用以及显式技术失败返回，不需要在外面再写第二套资格门。

非F分支继续原 `legacy_router.optimize` 或 `a4.run`；A1/A2继续用同一个 `rule_operations`，不增加两次LLM调用。`initial_native` 和 `packet.baseline_answer` 仍来自同一当前题，不能误用历史另一端。

### 6.4 cached 与 live 双路径

- `cached`：注入同一输入/模型/配置绑定的原F提议与已保存score响应，核对新controller返回与本轮190条输出逐项一致。保留原native值类型，不为了统一JSON重新生成答案。
- `live`：真实执行采用head一次，再由新验证器即时从它的trace抽候选。不要读取固定95列表挑题；新问题是否触发由本次F内部route和候选K决定。
- 缓存不完整时生成缺失部分，不将缺F trace当作不适用。原模型初答不等于已有F完整池。

### 6.5 结果记录

沿用当前结果字段，新增研究variant、selected_component、roles、F route、K、候选代表index、两编码分数、最终完整响应hash、调用分项。无需再造深层审计JSON，也无需每个专家输出同一张知识表。

若F和验证器共享同一个ModelSession，最外层cost应为整个任务的一次 `cost_since(checkpoint)`；分项取差值。不能把proposal.cost与session.total双加，也不能因缓存省了本次计算就省掉部署成本。

### 6.6 最小验收，不再展开大规模防御测试

采用当前已有回放覆盖验证不改输出；对以下路径各取一个合法现有例子连通：规则、诊断、完整模型R4、F普通无分歧、F普通有分歧、F-NLI、兼容透传。M4/M5保留自身模板与配置。

cached一致性核对可全部用旧记录；live例子只证明入口和成本贯通，不作为新准确率。真实重采样不要求逐字重现旧F，不为匹配旧输出重复抽样。

技术失败记录该题并按当前合同处理，普通答错继续批次。共享engine无法初始化才停止受影响作业；不让32次相同初始化失败重演，也不自动扩展到未授权GPU。

## 7. P3：R1–R5的能力覆盖如何补齐，不重新发明五个头

### 7.1 覆盖矩阵

按当前可见capability、原生格式、离线R标签和来源分别列 `eligible / activated / answered / fallback / scored`。R标签可以离线统计，不进入路由。

当前历史121中只有9规则、8诊断、104 F，A4无适用题；自然52全部由F路由。故本轮正信号主要来自A5，不能说验证器分别提升五个head。[S1]

### 7.2 A1/A2的正确消融

无需独立新训练。保存同一组facts、规则状态和初答，比较原输出与禁用补入操作、禁用撤销操作的**机制消融**。禁用A1可通过将原MET项中原先未选者在组装视图中视作未知，使其不新增；禁用A2可将被撤销项在组装视图中视作未知，使其按旧初答继承。仅在单独消融视图执行并交由同一assembler，明确这是改变执行政策的对照，绝不反写真实事实或正式MET状态。

如果特殊None/无效初答导致上述视图没有清楚语义，直接使用公开已有操作消融入口或逐项规范，并单列适用范围；不要为了完成一张表编造等价性。它证明支持增加/撤销的必要性，不证明两个独立LLM协作。

### 7.3 A3与A4

A3保留原目录强对照，不将自由字符串诊断重新加入主输出。

A4分两张表：原v5任务上的实际覆盖与结果；明确给定生理模型的动作忠实、数值及命题结果。后者可引用历史冻结实验并标日期，新系统接口验证另标；24旧profile不因包装后又称独立新患者。

### 7.4 R5

旧NLI策略原样保留，候选验证只作用于普通投票。必须扩大真实合格的保持与应变成对测量，当前2/4应变对不足以声称有普遍响应能力。不要将人口/措辞变化自动当作医学无关；优先用已有来源提供的资格与目标合同。

## 8. P4：最小完整对照集，不再造失败的万能工具代理

| 编号 | 对照 | 要回答什么 | 新计算 |
|---|---|---|---|
| C0 | 同题原方法/骨干原生输出 | 整体head系统相对原始起点的收益 | 优先复用正确版本缓存 |
| C1 | B：所有现有采用head，无新验证 | 新增候选选择是否有价值 | 和RCV共享同一次F池 |
| C2 | 同池candidate_only | 理由是否有额外信息 | 已测面板直接复用；新范围2K取分 |
| C3 | 同池candidate_with_rationales | 主研究方法 | 同上 |
| C4 | 旧票+三份补充回答 | 是否只是额外采样/更大池 | 已有面板缓存；新范围单列费用 |
| C5 | 单agent同池一次整体选择（有理由） | 是否需要逐候选二元核验 | 仅补一个固定控制，不作为提示网格 |

C5不得获得少于主方法的信息：同完整当前题、全部候选与理由、同原生目标。让一个控制调用在候选间直接选择，并返回选中原完整响应，不重写辅助字段。可用现有score接口在候选编码上取分，采用两个预定正/反编码映射；计算通常少于2K，此时按质量—成本比较，不虚称计算完全匹配。不要机械重复相同temperature=0请求来制造“等预算”。

C2与C3有相同评分次数，不是严格相同输入token，因为C3多理由。其机制比较与费用均应报告。C4三份响应不能记为一次，也不能因为本轮复用而记部署免费。

### 8.1 Router无需另开大项目

主Router是能力规则，不用R标签、不学习gold。因此用激活和覆盖矩阵说明它完成什么；不能宣称训练出了强router。新增局部触发是普通F有至少2个合法候选；NLI/无分歧原样返回。

把验证器应用到K=1时，选择结果必然不变；可用离线计数报告节省的 `2 × 单候选题数` 次逻辑score，没必要花GPU真的验证同一候选。也不要强制全部五个专家处理不适用题，再称路由相对“全五agent”显著更强。

### 8.2 关于经典MoA对照与论文措辞

同骨干F多次生成属于同模型多提议者，C5可作为实际的同池聚合控制。它不是原始异构多层MoA的完整复现，需命名为 `same_pool_joint_selector`。若论文要声称超过原MoA、Self-MoA或CFDX原方法，应额外按其真实协议实现并计费；第一轮不以此作为当前主线集成的前置条件。

## 9. P5：从小面板走到完整任务，再到真正冻结后证据

### 9.1 当前173输入槽/骨干的用途

历史121和自然52继续分表，是已暴露开发范围。两骨干不是独立患者复制，也不合成一个高置信度346独立样本检验。此处的8净增只是描述性总数。

### 9.2 完整v5回归

使用当前冻结v5完整合法输入manifest，而不是再挑“F有正确候选”的题。现有文档记录13,905个唯一模型输入，执行时以真实manifest与评分映射核对；不得为匹配一个记忆中的数目删除样本。[S1]

先产生 `cache_coverage.csv`：逐输入列采用B/完整F池/实际原上下文/评分映射是否已存在。只复用方法、输入、原上下文与版本吻合的缓存。

- 已有完整F池：只运行缺失RCV或对照的score。
- 只有原模型答案没有F池：必须生成采用F候选一次；C1/C2/C3共享它，不能各跑一次再比较不同池。
- 非F分支：新控制器与旧B等价，复用正确缓存，单独记录角色。
- F无分歧/NLI：不额外验证，完整分母仍保留。
- 完整范围的B成本和增量成本各报，缓存回归不冒称fresh端到端延迟。

第一优先M4/M5，完成后再用已冻结方法扩到其余原方法；不一开始重跑全部七方法的检索和生成链。任何预算受限执行先标 `partial / completed coverage`，不能把未跑输入当成正确或从总范围静默消失。

### 9.3 新确认数据的身份

coding agent从现有可合法访问资料和历史日志完成**一次**暴露清单，单位为母题/病例/规则机制。排除参与本轮提示选择、调参和模型训练的家族。分类或资格资料曾被处理不自动等于完全盲，精确记录接触类型。

在看新候选输出前冻结来源、资格、所有端点、数量和评分合同；尽量使用该预定合格范围的全部家族。若预算只能抽样，在推理前按固定种子、来源与原生格式选择家族，保留全部相关端点；不按模型表现回收/替换题目。

已经暴露的v5与D不能重新随机拆分后声称独立。若找不到足够真正未用于开发的合法材料，报告开发结果并单列跨家族评估；不是暂停整个系统集成，也不能虚构确认结论。

### 9.4 稳定性该改变什么

验证器temperature=0，不要只把其seed从42换成43/44且继续用同一F池就宣称独立稳定性。

先比较固定同池选择能力；在冻结后范围至少增加一个独立候选生成复本，使F的生成seed表按预先说明的映射改变，B和RCV共享该复本。第一复本用采用配置，第二复本为明确命名的seed重复实验，生成温度、模板、工具等不变。不要根据结果选择某个seed表。

若预算允许再增加一个候选池复本，分别报告，再汇总配对差值；不能把三个随机结果作为三倍患者。具体seed映射在现有F实际接口上实现并写清，不凭空给其不存在的base_seed参数。

### 9.5 采用准则

- 主指标沿用原生ALL非参考单元均分；配对保持与应变、辅助块和费用是必报的独立维度。
- 研究候选进入扩大评价不需要每个小分层都无下降；不是零误伤产品门。
- “稳定提升”需要冻结后不同家族、两骨干及候选生成重复中具有可解释的正向证据。区间跨零则明确不确定，不挑最好一个说稳定。
- 若一个骨干或任务明显受损，限制结论适用范围，但不能根据已知source_id或gold在线拼出赢家。
- 若主指标仍无增量，系统仍能作为统一强head框架交付，候选验证保留研究分支；不为证明MoA名字再次改评分或重造五agent。

## 10. 唯一可选的后续方法修改，不作为当前收口前置

当前先冻结方法去扩大验证。若P1真实日志显示编码依赖或理由误导在多个家族反复发生，之后只开**一个有明确原因的修订**，例如同池联合相对排序；C5本来就会给出该机制的对照信号。若该控制更好，直接采用简单控制为新候选，而不是因为不够“反事实”拒绝它。

不预设用高分阈值解决：已有错误候选均值约0.985；也不按source或n00014这样的ID作保留规则。候选中的17覆盖失败属于另一类问题，本轮不临时补检索或新生成，否则不能继续归因选择机制。[S9]

## 11. P6：论文与演示应该交付什么

### 五张主表

1. **整体原生效果表**：C0、B、RCV，各骨干×来源×R分层，ALL去重，覆盖与回退。
2. **候选选择机制表**：C1–C5，同池覆盖、选择正确率、修复/误伤、无理由与理由差。
3. **CF行为表**：合格保持与应变双正确、原生特殊字段、R4模型内独立表。
4. **操作消融与覆盖表**：A1/A2共享核说明、A3目录、A4作用域、A5选择阶段，禁止重复计独立贡献。
5. **质量—成本与稳定性表**：完整B成本+增量，固定池和重新生成池分开，缓存与live分开。

### 架构图标注

五个操作框颜色一致；A1/A2用共享底座连线；A5画“候选生成→局部验证→完整响应选择”。Router为可见能力条件，不标“学习到的反事实类别”；全局不画不存在的五人辩论。

### 方法陈述

可写：在医疗反事实任务上，将不同可执行操作组织成统一框架，并检验旧候选理由如何帮助局部选择。

不可写：五个新独立医学模型、普遍提升所有R1–R5、新校准临床概率、实时患者模型、已完成独立验证、全部收益来自协作。

## 12. 点到点最终验收清单

| 完成项 | 最小证据 | 不需要的额外工作 |
|---|---|---|
| 唯一候选冻结 | 参数/提示/代表选择与本轮一致 | 不新增提示网格 |
| 统计补齐 | 相对B的家族差值区间 | 不重生成或重算旧全部评分 |
| 五角色整合 | cached同响应一致 + 小型live调用路径 | 不重构整个日志/依赖管理 |
| 完整原生回归 | 全manifest/缓存覆盖/完整分母 | 不重复旧F池或旧检索 |
| 控制与消融 | C0–C5实际身份与费用 | 不制造弱万能工具agent |
| 冻结后验证 | 真实暴露与家族清单、先定后跑 | 不把开发自然52称盲测 |
| 正文交付 | 五张表、真实架构、运行命令与限制 | 不强行将共享核写成独立agent |

## 13. 已核读来源

下列来源核读于2026-09-24。只通过网络核对公开部分，私有原文与执行环境没有在本会话重新运行。

[S1] 完整报告第15章：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/docs/research/cf_moa_experiment_report.md#candidate-verification-execution

[S2] 运行与交付：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/RUN_AND_DELIVERY.md

[S3] 原生与分层结果：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/data/quality_summary.json

[S4] 实际候选验证器：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/source_snapshot/cf_moa/agents/a5_candidate_verify.py

[S5] 固定池运行入口与源码说明：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/source_snapshot/cf_moa/evaluation/candidate_verify_runner.py
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/SOURCE_ENTRY.md

[S6] 五操作旧基线：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_minimal_v4/source_snapshot/cf_moa/controller/minimal_operations.py

[S7] 固定强基线路由：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/source_snapshot/cf_moa/controller/strong_legacy.py

[S8] 实际评分与成本：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/analysis_code/score_candidate_experiment.py
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/data/cost_summary.json

[S9] 固定smoke反例元数据：
https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-24_cf_moa_candidate_verification/data/fixed_smoke_counterexample_metadata.jsonl

[P1] Mixture-of-Agents Enhances Large Language Model Capabilities：
https://arxiv.org/abs/2406.04692

[P2] Rethinking Mixture-of-Agents: Is Mixing Different Large Language Models Beneficial?：
https://arxiv.org/abs/2502.00674

[P3] Language Models (Mostly) Know What They Know（候选正确性评估参照，不代表复现）：
https://arxiv.org/abs/2207.05221
