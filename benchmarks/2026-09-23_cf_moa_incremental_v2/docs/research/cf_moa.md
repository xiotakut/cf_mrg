> 本文为版本2发布时固定的持续主记录快照；最新实验终态截至2026-09-23 14:25。历史等待/暂停保留原时点，先读[版本2报告](cf_moa_experiment_report.md#incremental-revision-v2)。

# CF-MoA：操作路由与五专家组合原型

最新状态：2026-09-23（Asia/Shanghai）。[新计划本轮完成](#incremental-revision-execution-20260923)：36条归因、A2原parser缓存兼容、新B确定性封装及控制/暴露审计完成；B的242答案值保持，241条接口合法、M5 d00050仍不可用。A1_delta 6/6诊断不可用、0裁决，未通过资格、不扩展。A3两骨干完整8题×3臂已推理/回放/原生开发评分：M4关键编辑4/8与原题重评分4/8持平（B3/8）；M5关键编辑3/8低于B/重评分4/8，因此不采用、继续旧目录核。GPU本轮254新调用结束、2/3已释放；全部负结果与旧A2/A3/A4/F保持。A5新版、完整同工具控制、独立资格及共同冻结仍未完成，独立评估未开启。

修订前状态（保留当时记录）：2026-09-23（Asia/Shanghai）。A1 r5不采用，A5候选保留负结果、不再生成。真实旧F两骨干各121输入、合725请求（363/362）已完整回放评分；固定强旧组合成功率70.27%/64.41%，M5未超过原R1。同工具r2两骨干开发截断首错停，失败和完整分母保留。原A2/A3/A4不重跑。新增A2同事实控制真实smoke为M4验收通过、M5因新增严格包装拒绝额外None键而停止；历史parser同响应可解析，适配偏差已诊断并暂停扩展、等待用户处理决定。此次共2新请求，无重复生成；后续仅补停止/报告门禁，59项合并回归及242条无gold政策核验通过；四项固定CPU对照已离线评分，原A2各8/9适用题，但原R2仅7题且含2不支持，模型执行对照未评分。A3默认关闭编辑臂四项限定修复已完成：79项合并回归、242条默认输出缓存回放及16条真实tokenizer CPU预检通过；真实编辑推理保持暂停，0新增模型调用。A3 §7.4控制另完成无模型准备：37项针对性测试、242输入/726控制行及80条唯一score请求实际tokenizer检查通过，未评分。A2 parser处理仍待答，模型作业状态见最新工程段。用户授权的离线互补分析已完成并独立核验：每骨干121输入，强旧组合正确87/82，含未采用A1的离线上界90/86；在两旧控制联合上界之外A1仅新增2/1题，仍未采用。0新模型调用，Router聚合smoke最新状态见下、独立评测未开启，见[互补分析](#complementarity-analysis-20260922)。新增[A3配对控制及冻结校验CPU验收](#a3-paired-execution-20260922)已完成：64项合并测试、242输入流程与224个真实tokenizer/grammar预检通过；冻结清单仍not_ready，0新模型。详见[F结果](#f-complete-development-20260922)、[离线输入审计](#complementarity-input-audit-20260922)、[A2准备](#a2-control-preparation-20260922)、[本次parser差异](#a2-control-parser-difference-20260922)、[固定CPU对照结果](#a2-fixed-cpu-controls-20260922)、[A3准备诊断](#a3-edit-readiness-20260922)与[限定修复验收](#a3-edit-repair-20260922)。

此前工程节点（2026-09-23）：[简洁原生解释独立聚合候选](#native-explanation-stability-20260923)的双骨干各6题smoke通过，扩展在M4 d00051重复原生解释并截断后首错停止。完整242分母为58完成/1失败/183未提交，59新聚合952561/23872 token，0专家重生成；2435项实际入口核验通过，独立终态复核另记。GPU2已释放，不续跑、不增加预算、没有完整开发成绩或采用结论。[旧v2参考采样回放](#sampling-reference-replay-20260923)完成5109项终检：M5 121完成，M4 63完成/1原截断/57未提交，0新模型，仍非完整双骨干对照。[A1缓存多专家准备](#multiexpert-cache-feasibility-20260923)仅CPU实验；[原控制器242题首轮入口及全量请求验收](#multiexpert-request-preflight-20260923)已完成：484实际请求、3766个grammar/parser正负fixture通过，独立39835项核验通过。有限补查生命周期另完成7固定输入/13场景/19槽及1409项独审，4个正向场景真实复用F后重建audit并关闭补查，19次聚合响应均为合成数据；初次fixture错误与unknown=1原记账保留，0新模型/评分，没有放行推理。[证据清单](#freeze-evidence-inventory-20260923)仍未冻结。A1/A5未采用、A2 parser待决、A3编辑暂停。拟议的按原角色配置单agent另发现facts上下文容量阻断，方法选择已询问、受影响提案暂停。默认每题单专家，核心协作增量、共同冻结与独立评测尚未完成。

修订前最近完整运行（2026-09-23T09:27:18.153517+08:00）：[含A1聚合完整开发结果](#saved-a1-complete-development-20260923)为79/121、74/121，原生单元均分0.6306306306/0.5405405405，低于强旧87/82及其主指标，保留负结果、不采用。完整242题推理/终检/修复后合并/原生评分/三核心比较均完成；原合并键名失败保留。两项GPU作业及[完整激活与证据使用离线汇总](#saved-a1-complete-evidence-use-20260923)均已结束。A1/A5仍未采用，A3编辑及同工具/独立范围问题待决，尚未共同冻结或独立评测。[当前开发交付索引](#development-delivery-index-20260923)已整理，旧运行包导航已修正。 [目标现为阻塞](#goal-blocked-handoff-20260923)，等待上述处理决定。

上一候选终态（2026-09-23）：[先证据后原生答案v4](#aggregation-evidence-first-terminal-20260923)保留双骨干各8题成功smoke；扩展在M4 d00021重复原生解释并2048截断后首错停止，M5扩展未启动。完整242分母31完成/1失败/210未提交，共32新聚合687218输入/14586输出token，旧专家0重生成、未知用量0。终态实际请求/原parser/来源/费用检查已通过，GPU2释放；未合并为完整结果、未评分/未采用。A1旧缓存的v4注册来源绑定仅CPU完成，不放行多专家推理。历史失败和A2/A3/A4已有效结果保持。

上一离线任务节点（2026-09-23 02:12）：按最新请求完成[离线互补分析重放](#complementarity-replay-20260923)，13个结果制品与此前完成版逐字节一致、111个源文件及旧制品前后未变。0新模型调用、0原生重评分，A3编辑臂继续暂停；未因本次离线分析启动任何聚合smoke。

本文负责独立的系统研究问题：在相同合法输入与资源约束下，支持补全、支持撤销、候选比较、干预执行、抗干扰五种操作能否形成互补，稀疏路由与证据聚合是否超过强单系统。已有单head的研发与负结果继续归各自主记录；因本轮已有明确实现、对照与交付任务，按系统方法身份新建主记录。

## 2026-09-21：启动与约束

用户要求实现Router＋五专家原型，采用上传的执行计划（本地制品：`/home/data3/txy/.codex/attachments/288ca16f-8a4c-4f0f-91f1-fa554ee6a4e4/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md`）作为参考，并明确：遇到违背方案或与当前进度不匹配的问题，立即暂停进程、报告并询问解决方案。附件中的建议与历史描述不自动覆盖用户要求或本地已验证状态。暂停只涉及本任务，不中断其他健康作业。

正式v5、原生评分、历史基线与已有head制品保持原身份。v5只能作为已暴露开发证据；专家、视图资格、路由、预算、提示、聚合、随机种子与评分冻结后，才进入未用于本轮选择的评测。gold、R标签、分类理由、作者答案解释、隐藏配对端与来源ID答案旁路均不进入推理。源ID只在隔离的评测/证据账本保留。

实施顺序为：实际版本锁定及R1分派迁移回放→统一合同和请求/成本trace→独立A1、一个A5受控多视图候选、R2/R4薄适配及可关闭A3编辑→专家独立输出和互补矩阵→稀疏路由与证据聚合→冻结后的评测。任何候选未过对照时保留真实身份、失败与负结果，不改名宣布成功；既不强制保持，也不强制翻转。

## 阶段A：实际位置与采用版本核对

| 组件 | 本地实际入口 | 当前可继承内容与边界 |
|---|---|---|
| 旧R1分派 | `Documents/Codex/2026-09-16/r1_head_experiments/candidate/r1_head.py` | `optimize`按原生格式/规则覆盖分派到目录、规则或透传；不是独立支持补全。旧2866×7输入、75264缓存回调为历史验证，待新控制层重新回放。 |
| R2 | `Documents/Codex/2026-09-14/new-chat/r2_condition_head.py` | 正向事实＋问句范围＋三值重算，UNKNOWN继承。与R1采用包内六个已核对的R2/R3执行文件逐字相同；不选用后续失败提取器。 |
| R3 | `Documents/Codex/2026-09-16/r1_head_experiments/candidate/r3_catalog_distribution_head.py` | 49公开疾病目录、六排列、既定无内容先验校正多数票；单次/未校正控制分别保留，不继承训练病例标签检索。49目录与原生46标签评分范围差异是已有合同，不能补映射抬分。 |
| R4 | `Documents/Codex/2026-09-17/r4_structural_head/physiology_head/frozen_method/physiology_head/head_v2.py` | 22:49冻结的typed局部干预，依赖同包的head、executor与作者模型。仅完整给定模型、参数、13状态及辅助状态、计划/餐食、120分钟窗口、指定三类数值问句。历史布尔/临床失败头不作默认。 |
| R5旧F | `Documents/Codex/2026-09-18/r5_head/delivery/r5_head.py` | 最终两路径×两映射NLI及其他支持格式五票/三票早停。`consensus/delivery`只是旧五票阶段；W/X/Y及CAD计划不是采用版本。 |

上述位置均实际存在；运行包及其已检查父目录没有单独Git根或附加AGENTS，适用工作区共同指令。已核对主记录：R1（本地制品：`/home/data3/txy/docs/research/optimization.md#r1-core-head-delivery`）、R2（本地制品：`/home/data3/txy/docs/research/r2_support_head.md#r2-execution-guide`）、R3（本地制品：`/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-head-delivery`）、R4（本地制品：`/home/data3/txy/docs/research/r4_consequence_head.md#r4-physiology-method`）、R5（本地制品：`/home/data3/txy/docs/research/r5_invariance_head.md#r5-final-delivery`）、原生协议（本地制品：`/home/data3/txy/docs/evaluation/protocol.md`）。没有宣称全文逐读所有历史日志/病例。

本轮代码拟放在`/home/data3/txy/cf_moa/`，通过适配引用已锁定的历史执行核；本轮证据放在`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/`。旧回放脚本会写回原目录，因此新回放必须将输出定向到本轮证据位置后执行，不能直接重跑覆盖旧收据。

资源只读快照显示四卡均有活动负载，尚未申请或占用GPU。当前仅进行文件核读与CPU开发。成本：本任务新增模型调用0、训练0、生理积分0；尚无互补矩阵、质量分数或冻结后评估结论。

### 旧分派迁移回放完成

新控制层（本地制品：`/home/data3/txy/cf_moa/controller/legacy_router.py`）复用采用包中的目录/规则模块，保持旧三个分支和全部返回字段；原`r1_head.py`作为历史证据保留。调用前只向新控制层传入`question/options/fixed_evidence/answer_format`。通过离线回放驱动（本地制品：`/home/data3/txy/cf_moa/evaluation/replay_legacy.py`）调用旧验证程序，每题将新旧入口的完整返回值和全部回调请求逐项比较，再执行原有分支/原生评分检查。

实际运行七方法各2866题（1780目录、72规则、1014透传），合20062输入、74760目录分数缓存回调＋504事实缓存回调＝75264；同缓存还供新旧返回值的内存核对，不计为新生成。运行退出0、127.367秒CPU墙钟，新增模型调用0、训练0、积分0。所锁旧代码/JSON/原回放证据逐项SHA-256未变。这里确认迁移等价，不是新质量实验或新泛化分数。

证据：采用版本清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/historical_versions.json`）、迁移收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_a_replay/migration_receipt.json`）、完整回放收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_a_replay/candidate_replay.json`）、逐题原生结果（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_a_replay/candidate_replay_scored.jsonl`）、日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_a_replay.log`）。命令见运行包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/README.md`）。

## 阶段B：统一合同与薄适配（未完成）

已实现输入/提议合同（本地制品：`/home/data3/txy/cf_moa/contracts.py`）、来源定位（本地制品：`/home/data3/txy/cf_moa/tools/provenance.py`）、逐次请求/预算/成本记录（本地制品：`/home/data3/txy/cf_moa/tools/adapters.py`），以及A2、A3旧目录、A4和A5旧F的薄适配。InputPacket仅接收原生白名单和明确给定的工具/模型输入；患者引用定位与模型语义判断分开，不将引用存在当作医学蕴含。实际扫描13905个v5输入，所有fixed_evidence为字符串列表，共30065个字符串元素；本次未改变输入或评分。

9项单元测试（本地制品：`/home/data3/txy/cf_moa/tests/test_contracts.py`）通过（0.013秒）：禁止元数据/隐藏配对字段、普通文本不误删、外部文献不充当患者事实、不适用状态、缺码额外请求预算、R2添加与删除/CrCl不被eGFR替代、移动事件不复制、F完整保留辅助字段。这些是程序fixture与有限边界检查，不是专家质量评测，也尚未覆盖R4采用配置的完整回调合同。

旧F适配回放（本地制品：`/home/data3/txy/cf_moa/evaluation/replay_f_adapter.py`）使用09-18真实live_smoke的两骨干各3个输入（NLI/relation/robustness_single）：6份完整结果、24个实际历史请求逐项一致；messages、schema及顺序、seed、temperature、max_tokens、代码映射与完整返回值均核对。历史输入/输出token为151218/4630，属于缓存原请求，不是本轮新生成。新生成0。证据：收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_b_f_replay/receipt.json`）、专家封装输出（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_b_f_replay/proposals.jsonl`）、逐次请求trace（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_b_f_replay/calls.jsonl`）、单元测试日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_b_tests.log`）。没有将这6个旧样本称为新独立验证。

<a id="a4-config-pause"></a>

## 2026-09-21：A4适配参数漂移与即时暂停

在准备A4真实请求回放时，静态读取实际配置发现：新增A4回调（本地制品：`/home/data3/txy/cf_moa/agents/a4_intervention_execution.py`）调用`session.generate(messages, schema, stage=...)`未显式传温度，公共回调（本地制品：`/home/data3/txy/cf_moa/tools/adapters.py:61`）默认`temperature=0`。原R4 `v2/dev`及`v2/heldout`的M4、M5四份配置均为`temperature=0.7`、seed42、max_tokens2048；M4原guided_json为true，M5为false。当前新适配层因此尚不满足采用版请求等价，不能把温度0默认为旧R4，或沿用旧质量结论。该问题由本轮新增适配引入，不是原R4失败或性能退步结果。

按用户本轮“遇到任何和违背文档或者和我们目前进度不匹配的问题直接暂停进程并且向我汇报问题并询问解决方案”的明确要求，立即停止后续实施/实验，只核实四份配置并保存现场。旧R1回放与F回放均已结束，无本任务新模型/训练/积分作业需要终止；其他健康作业保持。**未修正温度并自行继续，尚未启动A1、A5新候选、A3编辑臂、互补分析或Router/聚合。**

已向用户提出待决定方案：让A4显式继承采用版完整生成配置，保留两骨干原有解码差异，补做精确请求和结果回放，通过后恢复原计划；或保持暂停先审阅现场。等待用户回复，不能以等待时间视为批准。现场证据：静态问题收据及四份配置（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/pause_a4_generation_config/issue.json`）、暂停前代码快照（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/pause_a4_generation_config/code_before_resolution.tar.gz`）、代码哈希清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/pause_a4_generation_config/code_manifest.json`）。

阶段交付限制：现有代码是未完成原型，尚无五专家能力比较、互补矩阵、同预算控制主结果或冻结后评估报告；不能称CF-MoA已实现、已采用或优于旧系统。本轮新增模型调用0、训练0、数值积分0。正式v5、原生评分和历史基线均未修改。

<a id="a4-config-resume"></a>

## 2026-09-21：用户授权恢复完整配置与分层验收（进行中）

用户明确选择“恢复采用版配置，回放通过后继续”：两骨干分别继承模型、消息/模板、所有采样与长度参数、原seed、重试/回退和工具参数；公共默认值不得覆盖。请求一致性和输出回放一致性分开验收。随后少量固定开发输入真实调用只检验配置到达执行引擎、工具和原生格式，不要求新采样文本等于历史，不调参、不为命中旧答案重采样。验收通过后直接继续原计划，不再等待确认。仅在采用来源不明确、无法解释的请求差异或同缓存的新旧原生结果不同时暂停受影响的A4路径；其他不受影响开发可继续。此新增要求取代前次暂停所等待的处理决定。

只读追溯已定位`physiology_head/v2/heldout/{m4,m5}/config.json`及对应开发配置；实际冻结驱动通过`--version v2`绑定`head_v2`，模型执行沿用`2026-09-16/r1_head_experiments/relations/experiment.py:run_model`。M4为Llama、guided_json=true；M5为Qwen、enable_thinking=false、YaRN、guided_json=false。两者原每请求seed42、temperature0.7、top_p1、top_k-1、max_tokens2048，配置其他项逐份保留。原数值执行核及回退保持引用冻结源码。以上是来源核读，尚不是修复验收或新增质量结果。修复证据将写入本轮运行包`a4_config_repair/`。

### 完整配置修复及两层离线验收通过

明确采用配置绑定（本地制品：`/home/data3/txy/cf_moa/tools/adopted.py`）逐份读取本轮保存的M4配置（本地制品：`/home/data3/txy/cf_moa/configs/a4_m4.json`）与M5配置（本地制品：`/home/data3/txy/cf_moa/configs/a4_m5.json`），校验其与原采用文件及依赖清单（本地制品：`/home/data3/txy/cf_moa/configs/a4_sources.json`）的SHA-256。A4改用`generate_adopted`，不进入公共`generate`默认值合并。模型、dtype、上下文、KV、batch、消息模板、guided模式及所有采样字段均保留；工具仍调用原冻结执行核。原seed42每请求不变；没有新增模型重试，非法工具动作沿用原inline回退。

请求层独立调用旧R4与新A4入口，在生成前截获完整messages/schema；再以原渲染函数对历史实际prompt与token数核对。通过AST只提取原`run_model`函数、把LLM替换为观察器、保留真实vLLM 0.8.5 SamplingParams，捕获原始LLM构造与generate入参；与新物理适配器逐字段比较，包含Struct序列化默认省略的全部默认字段。该观察器不加载模型，不构成真实调用。两骨干各72题、合144题全部无差异：M4请求收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_config_repair/m4/requests/receipt.json`）、M5请求收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_config_repair/m5/requests/receipt.json`），同目录requests.jsonl保留完整新旧请求。

输出层随后给新旧入口注入同一条真实历史patch响应，比较完整trace（解析、干预、回退）、实际求解器调用（包含默认参数）及原生答案。M4/M5各72/72一致，每骨干四动作各18题；M5原17条外层JSON无效但工具字段完整的响应仍按原逻辑执行，没有纠正文案或换响应。共144条历史响应，历史输入/输出token分别737214/27092；本轮新增模型0，实际求解器288次、事实/反事实共576条120分钟CPU积分，两个回放阶段63.133与64.452秒。这里证明适配等价，不能当新准确率或独立泛化：M4回放收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_config_repair/m4/replay/receipt.json`）、M5回放收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_config_repair/m5/replay/receipt.json`），replay.jsonl含逐题完整结果和实际执行参数。

新增回归检查覆盖公共temperature默认0而A4仍0.7、两骨干各自完整配置、必须明确骨干及非法动作保持原inline回退且不重试。旁查A2的采用事实配置为seed42/temperature0/max2048，A3采用评分为seed42/temperature0/max1，F在原head显式指定各路径seed和温度；未发现另一个已确定温度漂移。A2/A3现显式传入原回调参数以避免未来公共默认变化；其余骨干/物理解码须在对应后端接入时绑定，不能以这次静态检查冒称其他专家已完成新的物理层验收。没有参数搜索。成本封装另将工具包裹的模型耗时从工具exclusive秒中分开，避免将同一段耗时相加两次；早期回放原始trace保持，成本汇总应按调用字段分别解释。

### 少量真实调用待资源，其他CPU开发继续

真实检查驱动（本地制品：`/home/data3/txy/cf_moa/evaluation/a4_live_check.py`）固定开发文件下标0/3/6/9，即首profile四动作各一题，每骨干4调用，按原batch4、原参数执行并记录引擎add_request实际接收值。不读取历史答案决定生成、不比较新旧文本、不为命中旧答案重采样。当前GPU0–3空闲24313/24397/27769/25387 MiB；M4权重约14.99 GiB＋固定KV16 GiB，M5约15.29＋18 GiB，均无法容纳于现有空闲。两次启动前资源检查退出75，模型未加载、0生成；状态分别在a4_live_check/m4（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_live_check/m4/status.json`）与m5（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_live_check/m5/status.json`）。没有降低原KV、修改上下文/精度或终止其他作业。已询问可用GPU时段/节点，等待资源不作为通过真实验收；同时继续不受影响的CPU实现。

后续CPU计划：独立A1两阶段支持覆盖→原生重判；唯一A5候选采用完整锚点＋两种有资格的代码重映射视图，分歧最多一次原文复判，无资格保留旧F路径；A3受控编辑单列、默认关闭。先完成专家边界测试与开发独立输出/互补矩阵，再接路由及聚合。未运行候选不得称有效或采用。R5既有记录提示合法U+2029不能用splitlines切JSONL，本轮通用读入改用文件逐行迭代；不读取未暴露D逐题内容。

### 附加发现：Llama运行token与准备token相差一个BOS

在给旧F回放（本地制品：`/home/data3/txy/cf_moa/evaluation/replay_f_adapter.py`）增加实际渲染/物理参数核查时，首次检查停止于token计数断言：失败日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_c_f_physical_replay.log`）。完整prompt逐字相同，不是提示或模型参数漂移。只读追溯vLLM 0.8.5 `InputPreprocessor._tokenize_prompt`及`encode_tokens`确认服务端采用tokenizer默认特殊token策略；新预算预估误用了`add_special_tokens=False`。M4首条F实际2290 vs预估2289，首条R4实际4910 vs原准备文件4909；M5分别2115/2115、5297/5297。原Llama运行自动加BOS，新旧实际请求均如此。

修复仅让预算预估沿用服务的默认编码策略，并在真实backend中核对返回的完整prompt_token_ids；没有改模型输入、模板、采样或seed。A4请求核查现分开比较“原准备token数”与“原真实运行token数”，用另一次仅请求审计验证全部144题，无需重复576次数值积分。补充特殊token预算回归；首轮失败日志保留。该问题不使此前同缓存的新旧原生结果不一致，也不意味着已完成真实调用。新检查位置为a4运行token核查（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a4_config_repair/runtime_token_check`）和F修复后物理回放（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_c_f_physical_replay_fixed`），最终状态以各receipt.json为准。

## 阶段C：独立能力与后续运行接口的CPU首版

A1（本地制品：`/home/data3/txy/cf_moa/agents/a1_support_completion.py`）自行生成候选—患者事实—知识条件—问句范围覆盖记录，区分可能漏用、未绑定与缺知识；逐引用定位后进行原题原生重判。可以读取相同公开目录和有限规则资料，不调用A2/A3决定。外部资料不能登记为患者事实；无来源模型知识单列；覆盖缺项和失败引用保留。首版只重读已有完整上下文，额外检索关闭。支持提议是模型判断，不冒称确定性医学证明。

A5（本地制品：`/home/data3/txy/cf_moa/agents/a5_robust_readout.py`）只新增`qualified_code_views_original_adjudication_v1`一个候选：完整原始消息作为锚点，追加两个明确双射代码表，原题、患者数值/单位/否定/时间/主体、文献和辅助输出合同保留。相对选项或原题对选项代码的依赖不具资格。各视图返回完整JSON并回映语义；答案及非自由解释辅助字段均一致时使用完整新锚点，否则最多一次带原文来源定位的复判。没有稳定即正确、必须维持初答或必须翻转的规则。无合格视图返回旧F的真实variant身份并注明requested_candidate，不能把F回退记成新A5成功。

A3编辑（本地制品：`/home/data3/txy/cf_moa/tools/bounded_edits.py`）为`fixed_catalog_bounded_evidence_delta_v1`，默认不启用。强目录六排列先执行，从其当前输入分布固定两个候选；最多两个单独可见句段探针，删除与明确否定是不同操作。程序仅允许局部否定插入/positive→negative或完整显式否定前缀，其他文本不改；目标问句、数值重写、隐藏端引用不能通过。实际比较同目录顺序/同代码集合下的原始log概率margin及有向delta，最终回到完整原题。零差分无需翻答；所有探针标hypothetical，临床可实现性未建立。代码和fixture不证明该臂优于旧目录或同预算控制。

独立运行器（本地制品：`/home/data3/txy/cf_moa/evaluation/native_runner.py`）每次只运行一个专家，输入只读InputPacket，逐题记录完整提议、逻辑/物理调用、失败、成本和工具trace。事实、目录、readout两骨干配置分别从历史源复制并校验；新候选设置（本地制品：`/home/data3/txy/cf_moa/configs/prototype.json`）与采用版参数分开，当前固定seed42、温度0.7、A1覆盖4096/原答2048、A3编辑1024、A5单次2048，没有搜索。R5原F的KV配置为16384blocks（比A4更大），readout工作需约56 GiB空闲；此处保留原参数，未启动GPU。A3编辑所用新生成/评分共享readout后端，尚需在后续实际开发对照中明确与旧目录独立运行器的资源差异。

原生评分接口（本地制品：`/home/data3/txy/cf_moa/evaluation/native_scoring.py`）在隔离的离线进程提取执行原`norm/parse/score`函数并引用原46标签映射，不修改评分原件。保留非法多选、未映射诊断、robustness辅助字段及其原无语义纠错判分边界。互补矩阵函数（本地制品：`/home/data3/txy/cf_moa/evaluation/complementarity.py`）要求所有专家包含同一输入集合与unsupported/失败，拒绝重复输入×专家，oracle仅为离线上界；配对指标（本地制品：`/home/data3/txy/cf_moa/evaluation/paired_metrics.py`）要求显式合格保持/应变账本、按原生gold核关系并按family做区间。这里只写了计算程序和fixture，**尚无真实互补矩阵或任何Router/聚合成绩**。

程序验证依次扩展至27项通过，后补BOS预算测试。保留三类先前程序失败及修复：`stage_c_unit_attempt1.log`为测试with换行语法错误；attempt2为fixture两候选共享同一引用字典，修改B时同时改了A，已改为独立拷贝；attempt5为直接导入旧评分器缺少历史prepare依赖，改为从原源提取三个纯评分函数，原评分逻辑与文件保持。attempt3/4/6分别21/24/27项通过；这些是程序验证而非实验负分或方法质量提升。最终全套日志见stage_c_unit_final.log（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/stage_c_unit_final.log`），实际数量以最终运行日志为准。所有失败日志均在本轮证据包保留。

当前仍需：A4两骨干各4题真实调用；固定开发成员、独立专家输出、同资源/同预算强对照与互补矩阵；再接稀疏路由、证据聚合及其控制；最后共同冻结并运行未参与选择的独立评测。未达到这些条件前，A1、新A5、A3编辑均是未采用的待验证候选，不能用工程测试宣布研究目标完成。

<a id="cpu-preparation"></a>

## 2026-09-21：等待用户提供GPU期间的CPU准备（本轮已完成）

用户要求先推进不需GPU的部分，并自行设置资源获取脚本、获得资源后通知。本轮不启动模型或占卡程序。已开始准备固定开发清单、隔离的推理包与评测账本、原生评分核对、逐题续跑与成本日志、对照及冻结前门槛。真实独立输出和互补矩阵仍先于新路由聚合；这些准备不能作为已冻结或质量通过。

资源估计修正：先前36 GiB（A4）与56 GiB（readout）门槛主要计算权重和固定KV，未充分计入vLLM V1在block override之前对max_model_len的容量检查及总显存utilization余量。核读本机0.8.5的`v1/worker/gpu_worker.py:determine_available_memory`和`v1/core/kv_cache_utils.py:check_enough_kv_cache_memory`，现按模型配置/权重索引、固定KV、完整上下文容量及3 GiB未实测运行余量估算；H20（97871 MiB）建议A4空闲42 GiB、readout空闲60 GiB、facts/catalog空闲28 GiB。它们是保守启动估计，尚无本轮GPU峰值验证，不是参数搜索或模型配置变更。两骨干可用一张卡顺序运行；不降低KV、上下文、精度、温度或seed。原等待资源收据与旧快照保留。准备证据放在本轮运行包`cpu_preparation/`。

### 固定开发清单与评测隔离

准备程序（本地制品：`/home/data3/txy/cf_moa/evaluation/prepare_development.py`）只读取已经暴露的正式v5资料。以来源×原生格式×原R标签组合分层，每层按固定SHA排序选2个家族，再纳入被选家族的全部原生端点、任务及变体。成员选择不读取本轮新模型结果；R标签只用于离线分层，不进入专家输入。得到40家族、74单元、每骨干121个唯一原生输入与157条原生评分映射；是少量开发pilot，不能用其分布估计全v5或新泛化。

推理目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development/inference`）只含白名单原生输入、各自骨干完整已保存消息、各自初答、原生输出合同和公开工具/预算。题号为不含来源/R含义的不透明句柄；gold、R标签、原题ID、家族和配对端账本另存offline目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development/offline`），模型运行器不读取该目录。原有检索截断量如实记录，本次未再截断上下文。M5历史v5未启用guided JSON；本轮readout使用原F已经明确采用的M4原生schema，来源在原`r5_head/consensus/experiment.py`，不能将其说成M5历史v5原来就用了结构解码。

原生配对按原unit/task中的reference对应关系建立，只有原生候选语义集合可直接对齐时才登记保持/应变。77对中保持73、应变4；另11条无唯一reference或需额外语义资格核对的记录保留原因。关系来自原生候选与gold，不从R类强制推断翻转。这只承袭原基准标签资格，不是新的临床真值审计；应变数量很小，不足以支持A5采用，后续强控制仍必须完成。R4生理模型开发/真实检查单列，v5 HIV题没有被补造模型参数。

首次导出在核对历史评分时因新脚本误设M4评分路径而停止，输出保存在`development_attempt1_partial/`，日志`development_attempt1.log`。纠正到真实的M4 `scores/`与M5 `completed_m0_m2_m5/`后，用同一固定成员成功导出；未根据分数换题。两个骨干各157条、共314条原生结果字段及相关文档检测字段与历史文件一致。随后通过独立评分CLI（本地制品：`/home/data3/txy/cf_moa/evaluation/score_run.py`）对同一批历史初答再做端到端接口验收，保持314/314一致；这属于离线重算，新增模型调用0，不是新专家输出或互补矩阵。第一次辅助脚本启动缺少工作区PYTHONPATH的错误及正确重启日志均保留。

### 请求预检与可恢复运行

CPU首请求预检（本地制品：`/home/data3/txy/cf_moa/evaluation/preflight_development.py`）遍历121输入×7入口×2骨干＝1694条路径，截获适用入口的首个请求后停止，不注入答案。两骨干分别：A1 111、A2 9、A3 8、A3_edit 8、A4 0、A5 104、F 104条首请求；合688条按真实模板和SamplingParams构造、校验元数据边界及token容量，最高35472输入token。其余1006条为明确不适用；A4在该v5包全部不适用符合其给定完整生理模型的范围。所有backend的start被禁止，实际模型加载0、生成0、积分0。预检耗时53.450秒，只覆盖首请求；后续覆盖/复判请求须由实际保存的响应决定，未冒称全部动态路径已验收。

独立运行器（本地制品：`/home/data3/txy/cf_moa/evaluation/native_runner.py`）新增SQLite WAL与FULL同步的逐请求日志（本地制品：`/home/data3/txy/cf_moa/evaluation/journal.py`）。提交前持久化请求/序号，完成后保存原始值、实际物理请求和token事件；`--resume`核对完整输入文件、预算、配置、候选及代码指纹，跳过已完成题，从同次运行已保存响应继续。无效JSON、错误答案、明确失败均不会触发重采样。若已提交但响应未落盘，则保留未决身份与未知用量、阻断该题重抽；不能把缺失成本写成0。旧head内部允许的原生回退继续保留。每题成本同时区分本次回放、同次实验唯一模型请求和中断前未完整记录的工具成本。

A4小批真实检查保持原batch4；新增提交意图与完整返回批次的fsync记录，先保存批次再做CPU解释。已有意图文件阻止自动重复提交；没有改messages、temperature、seed、长度、guided模式或求解器。真实执行尚未发生，也未覆盖原资源等待收据。真实检查恢复仍以原两骨干各4题计划为准。

最终38项测试（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/unit_final.log`）全部通过（0.300秒），包括家族完整纳入、Unicode段落分隔、不同消息保留、配置不被显存门槛修改、原生单元等权、重开持久化日志后的同响应恢复、服务失败与未决调用保留、请求/预算变更拒绝复用、完整负结果不重跑及A4不重复提交。`unit_attempt2.log`保留一次假后端fixture缺少初始化耗时字段的失败；补齐fixture后37项通过，随后加入A4批次防重提测试达38项。均为程序验证，没有候选质量分数。

### 对照、冻结门槛与GPU交接

核心对照计划（本地制品：`/home/data3/txy/cf_moa/configs/control_plan.json`）分别列出旧R1/R2/R3/R4/F、同资源单agent、同预算采样和top-1。所有控制层、专家、缺码、追问及聚合调用纳入同一上限；同时报告实际花费及预算匹配前缀，不能仅凭相同上限声称实际成本相同。旧头各自完整引擎配置保留；需要相同引擎诊断时单列，不能把不同KV/上下文容量说成同显存资源。单agent、采样、top-1及聚合仍为待实现/待运行，不是已完成对照。A3编辑保持默认关闭；新A5只有一个候选，回退仍保留F身份。

冻结就绪清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/freeze_readiness.json`）明确保持未就绪：真实A4验收、专家独立输出、互补矩阵、核心对照、新路由与证据聚合、最终采用/未采用决定以及独立评测暴露清单均尚需完成。未读取独立D输入或打分；新候选没有因CPU工程通过而改称采用。之后仍先保存真实独立输出及互补矩阵，再接新路由聚合。

本轮新增模型调用0、训练0、数值积分0；此前A4回放的576次数值积分不重复计入本轮CPU准备。导出成功阶段8.215秒、首请求预检53.450秒，其他离线评分/测试/哈希核查成本见各日志与成本清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/cost_inventory.json`），未测量的总交互耗时不补造。代码、配置、推理/评测分离文件、逐请求预检、失败日志、原生评分、续跑与资源交接命令见运行包入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/README.md`）；本轮另存CPU开发快照，先前快照保持。

封存核查完成：193份锁定来源逐项SHA-256未变（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/preservation.json`），包含历史head、采用配置、原生评分及本轮引用的v5输入/原答/评分来源；A4请求与原生执行的六份关键实现/配置相对通过回放的旧检查点未变。41份Python源码可解析，171个当前文档本地链接均可定位。CPU快照清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/checkpoint_manifest.json`）明确标为开发检查点，不是方法冻结。

<a id="restart-20260922"></a>

## 2026-09-22：重启后核验与恢复真实运行（进行中）

用户明确要求检查重启后的进度和资源。机器启动时间为2026-09-22 11:15:17，11:23检查四张H20各空闲97367/97871 MiB、利用率0%，没有GPU计算进程；约483 GiB可用主存、工作盘约1.1 TiB可用。当前GPU UUID已重新记录，按当前设备编号选择GPU0。Python3.10.12、torch2.6.0、vLLM0.8.5与采用环境一致，不安装或调整依赖。

逐项核对CPU检查点代码、193份锁定来源及各采用配置，没有差异；A4两个旧目录仍为等待资源，均无batch_intent或generations，不存在重启后未知响应的已提交批次。先将原等待状态与计划复制到本轮`restart_20260922/before_m4`、`before_m5`保留，再在原固定计划目录继续。证据：重启检查（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/restart_check.json`）。没有改正式v5、原生评分、历史head、原温度/seed/输出长度或工具配置。

执行安排：GPU0顺序加载M4/M5，分别运行固定开发下标0/3/6/9，共8次原参数请求；只验收最终引擎请求、工具执行和原生格式，不以新文本与旧答案一致作为成功条件，不为答案重采样。日志放在`restart_20260922/a4_m4.log`和`a4_m5.log`，实际提交/响应/逐题提议沿用`a4_live_check/{m4,m5}/`。验收通过即继续已授权的专家独立开发输出阶段；实际结果尚待回写。

### M4首批完成；同步入口返回方式的观察边界修正

M4实际4次请求完成，输入19598、输出529 token，batch4生成4.999秒、初始化56.602秒、总73.194秒；动作执行与完整数值格式均4/4，新增8次数值积分。首轮验收因四题均观察到`output_kind:0→2`而退出1，立即暂缓M5并保留初始失败收据与代码（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/output_kind_issue`）。没有重采样或将失败状态直接删掉。

核读已安装vLLM0.8.5 `entrypoints/llm.py:1350`：`LLM._validate_and_add_requests`在发给引擎前将`SamplingParams.output_kind`统一改为`FINAL_ONLY`，0是调用前的CUMULATIVE、2是引擎收到的FINAL_ONLY。旧采用worker也调用同一`LLM.generate`；该字段是同步结果返回方式，不是temperature/seed/采样分布漂移。原验收错误地跨两个观察位置作全字段等值比较。

修复观察器：让已安装的真实同步入口在参数副本和无模型观察器上执行，得到应送达引擎的全字段，再与实际`add_request`字段比较；没有忽略某个差异字段，也没有改原调用参数。新增回归验证副本转换不修改原参数，并且temperature漂移仍能检出。同批次重验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/output_kind_revalidation/receipt.json`）重新运行旧worker请求捕获，4/4调用前参数、应有/实际最终请求完全一致；再给旧head注入本次已保存响应，完整trace、动作、求解器调用和原生答案与已保存的新A4输出一致。重验0模型调用，4条响应复用、8次CPU积分、6.729秒。原始generations/proposals和首次失败差异保留；M4状态新增重验收据引用后置为passed。已排除“无法解释的请求差异”，按用户授权继续M5，不更改温度、提示或seed。

### 两骨干真实验收完成；启动独立专家开发队列

M5固定4题首轮完成并通过，最终引擎请求无差异，动作执行、inline JSON及完整原生数值格式均4/4；实际输入21133、输出1006 token，生成5.797秒、初始化53.378秒、总66.934秒，新增8次CPU积分。两骨干合计8次新模型调用、40731输入/1535输出token、16次真实流程积分；加上M4同响应重验的8次积分，本次验收共24次积分，未再次计入昨日回放的576次。货币费用未计量。完整成本见A4成本收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/a4_cost_inventory.json`）。当前39项程序测试（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/unit_engine_boundary.log`）全部通过（4.773秒）。这些只确认运行/等价性，不作为候选质量采用或独立泛化结论。

按用户“通过后直接继续”的授权，准备让M4/GPU0、M5/GPU1分别顺序执行A2、A3、A4、A1、唯一A5及旧F；两个骨干使用同一已固定40家族、各121输入的开发包。A4在该v5包应全部报告不适用，完整生理模型的验收仍单列，不能补造模型覆盖HIV题。A3编辑臂不启动。每条路径保留原生输出、失败/不适用、物理请求、完整真实成本；完整输出保存后才由独立离线子进程评分并计算互补矩阵，队列不连接新路由或聚合，不读取独立D。

为防后续控制层开发改变续跑代码指纹，保存独立采集代码快照清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/expert_snapshot_manifest.json`），队列从该副本运行，输入与输出使用绝对路径。该快照是固定开发执行版本，不是研究方法冻结；原采用配置、采样、提示和求解器均保持。队列脚本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/run_independent_queue.py`）不自动重试；返回非零或有未决响应/未知模型用量则停止该骨干队列并保留记录。辅助快照命令首次误用不存在的系统`python`，退出127、未执行任何脚本；改用已核验的虚拟环境解释器成功，失败日志保留，未产生模型调用。

独立开发队列已于2026-09-22 11:39:51 +0800启动，M4/GPU0父进程21635、M5/GPU1父进程21636，起始入口均为A2；GPU2/3未使用。每骨干121输入×6入口，共1452份含不适用/失败的预期提议记录；模型调用数随各已固定方法原生分支确定，不将这些记录数量称为调用次数。启动收据、固定代码、命令与恢复说明见重启运行包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/README.md`），实际状态以`expert_development/{m4,m5}/queue_status.json`和逐专家日志为准。

11:41首段核查：两个骨干A2各121份提议全部保存，失败0、未决0；各有9条实际适用调用，其余112条明确不适用。两骨干共18次新增模型调用、10260输入/3103输出token，调用生成墙钟分别24.808秒与34.144秒。队列均已进入A3；GPU0/1正常使用，GPU2/3各仍空闲97367 MiB。此时尚未评分，不据此作质量结论；首段进度与成本快照（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/initial_queue_progress.json`）保留实际分母与进程信息。

<a id="a1-schema-pause"></a>

## 2026-09-22：A1结构解码兼容性失败，暂停并等待用户决定

用户重新发送完整目标，并再次要求遇到方案或进度不匹配时立即暂停、汇报并询问。本轮新附件与此前附件SHA-256完全相同（`4d27d8ddefd639da24e836f7e95728879c192707986130c4af21a1fa6025b522`）；其“尚未修改/执行”是09-21方案发布时的历史状态，不能覆盖本地已发生的工作。附件作为参考，当前用户约束优先。本轮检查时两队列已经停止、GPU计算进程为空；未重新启动任何模型任务，也未推进A5、F、路由或聚合。

### 已完成与实际失败范围

A2和A3的两骨干独立输出已全部落盘，每入口各121条（含不适用）；A2各9次、A3各48次真实模型调用，合114次，282822输入/3199输出token。A4在当前v5包各121条均不适用、0模型/积分，完整生理模型的两骨干各4题真实验收仍有效。A1每骨干10条不适用、111条执行失败，均没有候选答案；A5、F没有启动，互补矩阵没有生成。不能把A1的运行错误称为质量负分，也不能把`status=complete`理解为成功：旧字段只表示遍历完毕，其内部明确记录failed=111。

A1全部错误为`ValueError: The provided JSON schema contains features not supported by xgrammar.`。本地A1新增coverage schema含`minItems=1, maxItems=12`，已安装vLLM0.8.5的`v1/structured_output/backend_xgrammar.py`显式拒绝这两个数组关键字。CPU首请求预检只调用prepare/count_tokens，没有走实际结构输出验证，因此此前688个请求构造通过与39项程序测试不能证明这条动态入口可执行。默认关闭的A3编辑schema也含maxItems，需在修复时一并预检；它本轮未执行。

另一项缺陷属于运行控制：native_runner捕获每题所有Exception后继续下一题，队列仅在整个专家子进程结束后检查未决用量。结果两个骨干分别重复了111条同类基础设施失败，未按用户要求在首个运行错误停止。此前“遇到运行错误停止相应队列”的说明过宽，实际实现没有做到首错立即停止；保留原日志与原说明作为历史事实，并在此纠正。已完成的A2/A3无失败或未知用量，不需要重采样。

### 已完成的只读诊断与成本辨认

诊断程序（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/diagnose_a1_schema.py`）逐条读取两份SQLite日志，只读打开；禁止LLM初始化与backend.start，将222条完整物理请求逐字段重建，并调用已安装的真实`LLMEngine.add_request`及`Processor`验证路径。222/222复现完全相同错误，均发生在output注册和EngineCore提交之前；模型加载0、新模型调用0、积分0。逐请求诊断与收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/a1_schema_pause/receipt.json`）保存本地引擎源码哈希及每题证据。

据此可将原A1的222条记录解释为“进入外层调用但在引擎核心接收前拒绝”，题目生成响应与token均为0；这不是用缺失响应假定成本为0。旧journal/status中的222个未决用量标记原样保留，新增诊断单列，不覆盖历史收据。两次模型初始化约25.361秒、A1子进程总墙钟约76.514秒等真实开销仍计入资源成本；没有测量GPU能耗或货币费用。此前A4及A2/A3成本不重复计入本轮诊断。

保存核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/a1_schema_pause/progress_and_preservation.json`）：57份采集快照文件未变，当前57份生产文件与启动快照也一致，本轮未修改专家、采样、提示、配置、评分或历史代码。没有改正式v5，没有读取独立D，没有用答案决定是否重跑。

### 待用户确认的具体修复方案（未应用）

建议修复传输层的结构解码兼容性，同时保留A1完整schema、候选身份及coverage的1–12条合同；补实际vLLM入口的CPU预检和加载前检查；将配置/服务等基础设施错误与普通无效模型输出、错误答案分开，在首个基础设施错误或未知用量出现后停止受影响队列。保留这次失败身份和记录，在新链接的运行目录进行固定小样本验收，通过后继续原固定开发清单；复用已经完成的A2/A3/A4，不修改温度、seed、提示、成员或候选算法。

为使选择具体，已在隔离证据目录做CPU语法可行性检查，没有改生产代码：直接调用xgrammar的JSON-schema→EBNF转换虽然通过入口，却错误允许coverage长度0和13，**此直接转换方案不采用**。失败边界检查（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/a1_schema_pause/grammar_feasibility.json`）及首次断言中断日志保留。随后仅在候选语法制品中显式加入有限数组规则，长度0–14共15个边界用例全部符合1–12合同，实际入口验证也通过；候选可行性收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/restart_20260922/a1_schema_pause/explicit_bound_feasibility.json`）明确这只是首份schema、小测试词表的CPU验证，**不是生产修复、完整等价证明或模型运行通过**。恢复前仍必须覆盖全部不同schema、两骨干真实tokenizer、无效字段边界及完整回归。

按本条用户明确暂停要求，当前停在保存证据及提出解决方案的位置，等待用户选择“按方案修复并继续”或保持暂停；未把等待时间当作授权。

<a id="a1-schema-repair"></a>

## 2026-09-22：获准修复A1兼容性与首错停止（进行中）

用户已明确授权按建议修复并恢复，取消整体暂停。仅修A1解码兼容性和运行/验收设施，原提示、模型、参数、输入及parser合同不变；先schema与真实入口CPU预检、首错停止回归，再做两骨干固定小样本真实A1验收，通过后新目录运行完整A1，两骨干均完成后才运行A5、F和互补矩阵。A2/A3/A4已有有效结果复用，原222条失败及此前诊断保留。修复证据目录为`a1_schema_repair_20260922/`，启动manifest保存生产代码与全部已有逐题结果的哈希；此处没有独立Git仓库，修复版本使用源码快照内容哈希标识，不伪造commit。

兼容性修复已实现：仅在NativeBackend识别完全相同的A1覆盖schema时，用同一xgrammar的显式有界EBNF表达1–12条coverage；逻辑schema、全部字段/必填/类型/枚举/offset范围及原parser保持，A1源文件与提示构造文件逐字未改。两个骨干各111个原逻辑请求与保存的失败批次完全相同，物理请求除guided_decoding外逐字段一致；各6种覆盖schema及实际原生答案schema使用真实tokenizer编译，432个边界用例与原parser一致。CPU阶段25.029秒、0模型/积分。

首次CPU验收在诊断枚举的斜杠序列化用例停止；本机原转换器同样只接受JSON的`\\/`枚举写法，两种JSON表示经原parser得到同一标签。修正测试制品的表示约定，并加原转换器/兼容转换器的对照回归；没有改候选标签或模型生成策略。失败日志及部分制品在`cpu_preflight_attempt1*`保留。单元测试先42项通过，新增该回归后43项全部通过（5.257秒）。另纠正尚未执行的smoke成员准备：关系题无原生候选、A1不适用，固定选择multi/single/diagnosis/robustness_single各第一题，不依据任何新结果换题。

首错停止回归已验证：确定的早期schema拒绝或提交后结果未知均锁存first_error；后续题以及head内部捕获异常后的回退调用均不得发送。保存request_id、类别、提交/完成/在飞或未知数量，状态为stopped_on_error，主评分入口拒绝该停止批次。已完成输出、在飞未决记录及未提交题清单保留；原方法内部正常处理的格式/来源绑定不合格单独计数，不偷偷更改head语义。修复源快照及完整diff已保存；接下来按固定四题每骨干真实运行A1全流程，只有真实模型返回并经原parser验证后才允许完整A1。

真实smoke启动时GPU0被另一进程占用，空闲15123 MiB，低于固定readout门槛61440 MiB；M4资源准入退出75、提交0请求，等待收据另存`smoke_m4_resource_wait/`。不干预该进程、不改采用配置，转用空闲GPU2从同一未提交smoke目录恢复；M5使用GPU1。

### 真实smoke完成：兼容性问题解决，M5出现固定长度上限截断

两个骨干各4题、每题原A1两次请求，共16次真实模型调用已经完成；真实入口收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/live_request_acceptance.json`）确认16/16确实提交EngineCore、产生输出，实际请求参数逐字段一致。M4四题覆盖表与原生答案均通过原parser，M5三题通过、一题失败；完整smoke验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/smoke_acceptance.json`）保持failed，不能把7/8写成整体通过。

具体失败是M5的`d00003`、第0次A1覆盖表请求：原temperature=0.7、seed42、max_tokens=4096均确实传入；生成4096 token后`finish_reason=length`，JSON在一段引用字符串中截断，原parser报`Unterminated string ...`。这次是进入真实模型后的输出长度失败，与原222次请求在引擎入口前被拒绝不同。没有重新抽取该题、换题、续写残片、增加长度或改提示。未改动的A1内部处理随后执行其既定原生答案调用，返回244 token的有效原生答案，并将覆盖表失效记录为partial；这条有效末答不能替代用户要求的完整覆盖表验收。具体不兼容点（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/m5_output_limit_issue.json`）已单独保存。

成功解析的7题中，6题有原来源绑定/重复覆盖拒绝记录，照常保留为语义负结果/partial，不在兼容性修复中调整A1。smoke只证明请求和合同运行情况，不据此采用新A1或声称支持审查质量有效。

运行器的首错停止进一步覆盖“原head已经返回，但输出合同不合法”的情况：原head内部控制流仍保持，外层保留完整提议与raw响应、标记invalid_output并锁存first_error，禁止下一个实验输入；来源绑定语义不合格继续独立计数。新增早期无效输出回归后44项测试（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/unit_output_contract_stop.log`）通过（5.202秒）。该外层控制补充在smoke之后完成，代码快照另存`fixed_code_output_stop/`，没有覆盖实际smoke使用的`fixed_code/`及其原status。两版本的A1、提示/parser、配置、NativeBackend/VLLMBackend及三个grammar函数完全一致；没有为验证外层停止策略再生成一遍smoke。

本轮实际成本为16次模型调用、88276输入/20790输出token，生成墙钟约341.971秒；模型加载和各运行总墙钟见成本清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/cost_inventory.json`）。新增训练0、积分0、未决模型用量0，CPU语法/评分检查不计为模型调用；货币费用和GPU能耗未计量。A2/A3/A4有效输出与原222条失败的40份关键原始文件SHA-256保持，验证见preservation_after.json（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/preservation_after.json`）。

按用户边界，本轮不自行改变4096上限或放宽smoke合格标准；A1正式批次尚未启动，待决定M5-A1路径如何处理。未把整个项目恢复为全面暂停：已完成两骨干A2/A3共四份已有输出的原生离线评分（每份121输入/157评分映射，合628次原生映射评分），保存在`retained_expert_scores/`，0新增模型调用。A5、F及完整互补矩阵因用户指定的A1完成前置条件尚不启动，新路由/聚合与独立评测也不越过门槛。

修复代码、配置、前后schema及wire diff、真实请求/逐题trace、完整失败与成本、源快照和后续决定点统一见本次修复包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/README.md`）。下一步需用户选择：保持当前参数并将M5-A1记为未通过、先继续已通过路径；或者明确授权一个独立记录的输出预算变更。后者超出本次仅兼容性修复的授权，不能自动执行，也不能抹去这次负结果。

<a id="a1-d00003-trace-diagnosis"></a>

## 2026-09-22：仅审阅M5-A1 d00003完整trace，归类B并确认C

用户本次明确选择第三项“暂缓A1，先审阅完整trace”，取代上一节末尾等待的选择。仅读取既有smoke响应和合法InputPacket；不生成、不续写、不结构恢复、不提高max_tokens、不修改prompt/schema/模型/seed/温度，不读取gold、R标签或隐藏配对端。两骨干正式A1、A5/F正式推理与依赖完整A1的矩阵均保持暂停；A5/F代码准备仍可独立进行，本次没有改其代码。A2/A3保存结果和A4验收继续有效。

诊断证据放在原修复包的d00003_trace_diagnosis（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/d00003_trace_diagnosis/README.md`）。使用严格的JSON前缀词法遍历，只统计已生成的完整/未完整节点，不补字符串、字段或括号，不将前缀转成可评分结果；另用原A1 parser检查7份已完整响应。以下统计完全来自已保存的16次历史smoke调用，不是新采样。

### 截断位置与长度口径

M5 d00003第0次覆盖表调用已被EngineCore接收，实际输入12375、输出**4096 token**，`finish_reason=length`；保存文本**18101个Unicode字符**。最后完成的字段是`$.coverage[0].knowledge_conditions[7].references[8].ref = "F8"`，截断在同一对象的`quote`字符串内。该字符串从零起始字符18008开始（第101行、第33列），已写入93个字符，包含开引号但没有闭引号。最后完整引用对象为`references[7]`（F7）；最后完整行级字段为`patient_facts`，最后完整顶层字段为`scope`。

全段JSON仍停在候选A的第8个知识条件、第9个引用。当前引用还没有完成`quote`和`start`，候选A的`binding/question_scope/support_state/coverage_issue`均未开始；候选B/C/D的coverage行和顶层`unresolved`均未开始。因此语义内容和结构都未完成，**不是仅缺闭合符号**。尽管A行的知识陈述里已经零散讨论其他候选，这不能替代每个候选的绑定、范围、状态与缺口字段。

实际生成token以原event为准；原trace没有保存输出token IDs，无法精确把4096逐token分摊给字段。下面字段token均是**同模型本地tokenizer对原始子串重新编码**、不加特殊token的长度，不冒充引擎逐字段生成用量。M5全文重新编码为4086、M4同题为1414，与实际4096/1428有差异；可见文本重编码不保证还原原生成token序列。已额外用正式入口依赖位置的transformers4.51.3/tokenizers0.21.4复核，8份覆盖响应和全部主要字段与初始统计逐项一致。字符数含该字段值的JSON引号/括号及内部空白，嵌套字段相互包含，不可相加当总长。

| M5字段/节点 | 已见字符 | 重编码token | 完成情况 |
|---|---:|---:|---|
| `scope` | 402 | 74 | 完整 |
| `coverage`整体前缀 | 17670 | 4002 | 未完整 |
| 候选A行整体前缀 | 17664 | 4000 | 未完整 |
| A的`candidate` | 3 | 2 | 完整 |
| A的`patient_facts` | 402 | 98 | 完整、2项 |
| A的`knowledge_conditions` | 17181 | 3883 | 8项已开始、7项完整 |
| 第8个知识条件 | 2389 | 538 | 未完整 |
| 该条件的`references` | 2209 | 504 | 9项已开始、8项完整 |
| 截断的`quote`字符串 | 93 | 18 | 未完整 |
| A的4个剩余必填字段、B/C/D行、`unresolved` | 0 | 0 | 尚未生成 |

coverage实际是**1条已开始、0条完整、仅候选A**；完整条目的平均/最大token均为**N/A，分母为0**。若只描述唯一未完成前缀，其当前长度为4000重编码token，不能把它写成完整条目的平均/最大。7条完整知识条件平均476.57、最大659重编码token；5个完整非空引用数组各10项，当前第6个非空引用数组尚未完成。完整知识引用对象58个，另有患者引用2个。

### 重复与来源位置检查

60个完整引用对象只有16个不同的`(ref, quote, start)`，即**44次对象内容重复**；引文文本只有7种。一段242字符、46重编码token的引文被完整复制**47次**，共11374字符，占整个响应62.84%；截断的引文又是该段的开头。全部完整引用对象占15285字符，即响应84.44%。五个知识条件反复展开F0–F9整组来源，另一个条件在继续同型展开；四个候选的描述被放进同一个A行，而不是形成四行候选绑定。

没有发现已完整`statement`的逐字重复，也没有多个完整coverage行可据此称“候选行重复”；异常主要是引用数组反复复制、同类理由继续扩张及候选作用域混用，不能仅因陈述措辞不同就认定没有循环。这里描述的是已见重复模式，不证明模型会无限循环。

另以原`bind_quote`对前缀内60个完整引用做只读定位检查：**1个精确匹配，59个不匹配**。例如那段重复47次的长引文可在合法原消息C1中找到，但并不存在于生成时指称的F2–F9来源内；有些Q/F引文实际存在但offset错误。这个发现是来源位置不匹配，未进行医学蕴含或答案对错评分。即使仅补全JSON，已经生成的引用也不会因此变成合格来源绑定，进一步排除“只差有限收尾token”的解释。

### 与其他smoke题的输入规模比较

两骨干四题的`native_input`逐题哈希一致，但原方法消息不同，保留各自采用路径。下表“已有检索块”按原上下文中的`Document [0]`至`Document [7]`标题计数；每题均为8。d00003另有10条互不相同的fixed_evidence，共12598字符，在原消息中以D0–D9再次呈现；这些再呈现和source map的F0–F9是同一批固定证据，不能算成额外独立证据。显式`retrieved_context`列表均为空，不意味着原消息没有检索资料。

| 输入 | A1候选数 | 题面字符 | 已有检索块/另给固定证据 | M5实际输入token | M5实际覆盖输出token | 原提示要求的coverage规模 |
|---|---:|---:|---:|---:|---:|---|
| d00000 | 5 | 455 | 8 / 0 | 7793 | 3101 | 全部5个候选 |
| d00001 | 5 | 711 | 8 / 0 | 4217 | 2575 | 全部5个候选 |
| d00008 | 49（公开目录） | 578 | 8 / 0 | 4237 | 3095 | 最多12个，并报告未全覆盖 |
| d00003 | 4 | 470 | 8 / 10 | 12375 | 4096，截断 | 全部4个候选 |

d00003候选最少，题面长度不异常（两骨干题面均89重编码token）；异常的是更长的证据/原消息以及M5把资料扩成重复引文。M5该题输入为其他三题的1.59–2.93倍。按候选数，预期只需4条coverage，而不是比49目录题更多的候选行；按引用展开，没有合理有限输出估计，因为嵌套条数和文本长度未约束。不能把实际重复消耗当作任务必需的输出规模，也不能单凭4题推断这一现象在全部开发输入的发生率。

### M4同题结构与余量估计

M4同题覆盖表实际生成**1428 token**、6705字符，正常stop，顶层`scope/coverage/unresolved`均完整；其随后原生答案333 token，全流程合1761输出token。覆盖4行A/B/C/D，每行198字符、49重编码token，平均/最大均49；覆盖数组整体838字符、203重编码token。**但四行的patient_facts/knowledge_conditions都为空，binding/question_scope均为unsourced，support_state均unknown。** `unresolved`有30项（25种、5次重复），5789字符/1190重编码token，占输出字符86.34%。这只能证明另一骨干可以完成结构，不能证明相同的有效证据审计可在1428 token完成，或声称A1在M4方法质量上成功。旧`applicability=supported`及“格式通过”记录保持原样，本节补充解释其局限，不重写历史输出。

M5同题覆盖失败后，原head仍执行了既定native_answer调用，生成244 token，返回原生`step_by_step_thinking/answer_choice/errors`结构。该缓存末答保留但**不替代失败的A1语义结果**。M5该题已有全流程成本为16753输入/4340输出token，覆盖生成73.346秒＋末答4.467秒；这些均属原smoke成本，本次不重复计新用量。

**剩余token不能给出可靠有限预测。** 当前A行已消耗约4000重编码token还未收尾；若后续遵守覆盖全部4候选且其余3行延续这个展开尺度，B/C/D行本身就约需12000 token，另外还有A行收尾、`unresolved`和分隔结构。这是明确假设下的量级外推，既不是实际续写结果，也不是建议把上限设成某个数；模型可能提前收敛，也可能继续膨胀。schema只约束顶层coverage为1–12，patient_facts、knowledge_conditions、references、unresolved都无maxItems，自由字符串也无maxLength，所以不存在可由当前合同保证的有限完成余量。

### 分类及待审阅的新版本方案（均未实施）

按用户规则，**直接失败模式归B：M5生成稳定性/合同理解问题；同时满足C的结构条件。** A不成立（并非正常无重复且有限收尾），D不成立（语义与必填结构远未完成）。不增加M5预算，也不提高M4预算，不做结构恢复实验。

对应B的最小提示修复建议只针对已观测的行为：每个候选只出现一行；只写该候选的事实—条件绑定；同一条件不重复列相同来源；引文必须来自声明的ref及精确offset，不把C1文字换名归入F；不同条件共享证据时引用同一条已建立的证据记录。保留未知/缺失区分和全部语义字段，不强制保持或翻转答案。这里的提示改动会影响方法输出，必须作为新A1版本及独立目录；不是上一轮inference/schema compatibility fix。本次没有应用这些语句或改解码参数。

考虑C，优先形成一个两骨干共同验证的紧凑合同草案，而不是只给M5补丁：候选coverage去重；患者证据用合法来源的`ref/start/end`或无损ID表示，quote由当前输入确定性还原；知识条件单独建表，保留visible_source/model_knowledge及来源关系；candidate只引用事实/条件ID，仍保存binding、question_scope、三态支持、coverage_issue和unresolved。重复引用不再复制正文，各类数组和自由文本必须有预先冻结的显式上界；达到容量却仍有未表达内容时明确overflow、不作为成功、不删失败分母。ID展开回原语义记录必须先通过无gold的映射/回放检查。**无损去重可验证，但对原本无限自由文本施加有限界不能宣称对所有旧输出严格等价**；若必须丢失独立事实、知识或改变支持判断才装得下，应继续按方法不兼容报告，不能包装成纯schema修复。

后续若获准实施新版本，应先固定共同合同/提示及容量，再对两骨干同一组4个smoke输入各运行一次；保留原模型、temperature0.7、seed42和4096/2048两阶段上限，不按结果反复重抽。分别检查语法、候选覆盖、来源定位、非空有效绑定与原生答案结构，空数组或引用存在不自动等于审计成功。比较时单列两骨干实际输入/输出token、模型调用和延迟；两骨干共用新增预算/合同规则，原v1及本次失败保持身份。主实验仍需按原计划做同资源、同实际成本/预算对照，不能把压缩节省的token当作已证明的方法收益。该段仅是诊断后的方案，未开启新smoke或正式运行。

### 失败身份、保存与成本

新增failure_status.json（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_schema_repair_20260922/d00003_trace_diagnosis/failure_status.json`）明确：`inference_started=true`、`failure_type=output_truncation`、`semantic_result=unavailable`、`method_score=not_scored`、`included_in_failure_denominator=true`、`treated_as_answer_error=false`。本次截断保留在M5 4个已尝试smoke输入中的1个、两骨干8个中的1个；这是运行截断率的分母，不能称为答案错误率，也不能删除后报主结果。旧222条pre-engine失败属于另一历史批次，继续单列保留，不与这8个smoke输入混池。原raw/status/proposal/journal保持，不把外层历史`complete`改成当时并未发生的停止状态。

本次新增模型调用0、生成token0、求解器0、训练0。两个主要CPU统计脚本分别5.500秒和4.160秒；另有本地tokenizer版本复核与文件哈希核验，未作为GPU推理计费。239份受保护的生产代码、配置、原失败、smoke和已有专家/A4制品SHA-256未变。只新增诊断脚本、统计/状态侧文件并续写本主记录及入口；没有读取独立评测D、生成互补矩阵、发布采用结论或启动后台实验。

<a id="a1-v2-development"></a>

## 2026-09-22：A1-v2有界证据ID审计，新方法开发

用户接受B/C诊断，授权实现A1-v2并在计划目标内自主处理常规选择。A1-v1保持停用，不加预算；A2/A3已有输出及A4验收继续有效、不重跑；A5/F和互补矩阵正式推理继续暂停。代码和证据位于`cf_moa/agents/a1_bounded_coverage.py`、`cf_moa/configs/a1_v2.json`及`Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/`。独立原始版本身份为`bounded_evidence_id_coverage_audit_v2`，不是单纯兼容性修复。

首版固定上界为：每个证据索引片段最多320字符、整个索引最多512项；coverage最多12行；每行患者证据最多4个、知识ID最多3个；共享知识表最多12项、每项来源ID最多3个；scope/知识陈述/绑定文本上限分别160/160/128字符，unresolved最多8项、每项detail最多96字符。当前全部合法来源按句子/空白边界索引，保留原字符offset和SHA-256，非空白文本不丢失；只有Q能作患者证据。模型只生成ID，程序确定性还原quote/ref/start；来源位置检查与医学蕴含仍分开。证据索引或生成内容溢出明确unavailable，不以原答案代填；结论性状态缺患者—知识绑定、未知K、重复候选/ID或虚报全覆盖均单独记semantic invalid。全空审计记degenerate/partial，不称方法成功。保持原骨干profile、temperature0.7、seed42、4096/2048两阶段上限；新有限grammar只生成紧凑JSON，额外属性和无限空白均不可生成。

单元测试52项通过（6.102秒），包括原44项和8项v2/来源ID/真实grammar/停止回归。实际v2入口的人工早期无效审计会在第三个物理fixture调用后停止：已有首题2次调用保留，失败题只有覆盖调用，无末答和后续题提交。两骨干完整开发输入的CPU真实grammar审计另行运行中；每个真实smoke请求仍先经过正式backend的验证/编译再提交模型。

冻结首版代码66文件，内容哈希`39c8308b10f4e5d5aaab0ac053d09c71d2eefe5d8116b1a3e989a88fb0099bda`，见`frozen_manifest.json`、`frozen_code/`和`method.diff`。按预先固定的d00000/d00001/d00008/d00003运行两骨干各4题：M4使用GPU1、M5使用GPU2；GPU3按M4后M5运行同资源单次作答对照，各4次。该对照保留同一合法输入、公共资源和证据表，只有一次2048-token末答，不伪称同总预算采样。GPU0起初被其他PID34776占用、未干预；该外部作业后来结束，四卡再次空闲。

**首版v2的真实语义门槛未通过，未启动正式A1-v2批次。** M4四题均semantic invalid；M5三题semantic invalid、一题知识表全空而degenerate。8份审计JSON均完整、没有4096截断，但所有知识表为空，随后出现未定义K引用、缺候选却自称complete、无知识绑定却给结论性状态；M5唯一继续末答的退化审计仍不当成功。原native_runner的complete只表示已遍历，本处明确语义失败。加上8次同资源对照，共17次实际新调用、190428输入/5754输出token、生成墙钟187.885秒，见`initial_live_outcome.json`；0求解器/训练，原v1和新v2失败均保留，不重新抽同配置。

CPU补查`knowledge_branch_diagnostic.json`确认两骨干的实际tokenizer都能沿真实token序列接受非空知识表，空/非空分支均合法；不是grammar排除了知识定义（0新模型调用，20.954秒）。进一步只读发现明确的提示角色冲突：原方法system强制输出原生`step_by_step_thinking/answer_choice`，A1审计却仅在后加user消息要求另一JSON合同。此冲突真实存在，但尚未证明它独自导致所有失败。

下一步预先固定一次两臂对照，不增加预算、不改schema：r1仅把原完整消息序列作为引用数据保留，用审计system明确当前阶段；r2在r1上再显式呈现实际JSON schema和知识表定义/引用规则。两个骨干×两个修订各同4题、各一次，不根据答案换题或重抽；原v2负结果保持真实身份。按预先规则，若r1和r2都过结构/来源/非退化门槛，优先较少提示变动的r1；只有r2过两骨干时保留r2；均未过则不进入正式批次。选择依据是运行合同与来源绑定，不读取gold或主任务分数，仍不构成独立评测或质量采用。现四张空卡可各运行一个骨干×修订，待实现及CPU检查后启动；该段记录的是计划。

### 固定两臂对照完成：无采用版本，正式批次保持未启动

增加原始完整消息按引用数据保留的回归后53项测试通过；两臂冻结代码哈希`f7c36dabe40fd63980d3176597998dc32fe7379f47d1d667425901ad7cc26739`，全部8个smoke实际schema与首版逐项相同，`a1_v2.json`逐字相同。身份分别为`bounded_evidence_id_coverage_audit_v2_system_context_r1`与`bounded_evidence_id_coverage_audit_v2_explicit_contract_r2`；前者运行GPU0/M4、GPU1/M5，后者GPU2/M4、GPU3/M5。四个进程均退出0、运行已结束；这只表示请求遍历收尾，不表示方法验收通过。

| 候选或对照 | M4基础程序门槛 | M5基础程序门槛 | 新模型调用 | 输入/输出token | 当前结论 |
|---|---:|---:|---:|---:|---|
| 初版A1-v2 | 0/4 | 0/4 | 9 | 101949 / 3345 | 共享知识表全空、未定义引用或退化审计，未采用 |
| system_context_r1 | 0/4 | 0/4 | 9 | 103095 / 3424 | 单独隔离原system没有解决空表，未采用 |
| explicit_contract_r2 | 2/4 | 3/4 | 13 | 170459 / 9921 | 生成非空知识表，但跨字段错误未解决，未采用 |
| 同资源单次作答对照 | 4/4原生格式有效 | 4/4原生格式有效 | 8 | 88479 / 2409 | 保存为控制输出；没有评分，不是同总预算采样结果 |

每个分母都是预先固定的4个已尝试输入，没有删除失败后重算。基础程序门槛仅指schema、来源ID/关系检查和非空患者—知识路径，不是医学正确率。r2的M4 d00000重复知识条件，d00008有知识来源/引用矛盾及重复K引用；M5 d00008有来源/引用矛盾及重复候选。其他5题通过这些程序检查，但不据此认为其知识蕴含或答案正确。预先的双骨干规则选出`None`，未挑一个骨干的配置拼接成功，也未恢复正式A1。

进一步记录字符容量边界：r2的M4 d00000/d00008/d00003和M5全部4题存在某个scope、statement或binding恰好达到既定字符上限。部分文本止于句中，说明有限grammar虽然避免长引用与无界扩张，仍可能在结构完整时截去自由文本内容；不能把JSON有效当作语义完整，也不能只看5/8便宣布解决。`*_acceptance_and_replay.json`逐题保留`text_capacity_hits`。这些命中是容量诊断，不能单凭等于上界证明每条语义丢失；本轮没有放宽字段长度或token预算，也没有通过删掉这些样本形成主结果。

同题对照中，r2 d00003的M4覆盖表为813实际输出token、3383字符，末答854 token；M5覆盖表841 token、3417字符，末答210 token，均正常stop。但M4 scope/一条知识陈述、M5部分binding触及字符上界，因此这些结果仅说明新表示改变了失败形态，不替代原V1的4096-token截断失败，也不说明全部审计内容已恢复。

39次真实调用均有EngineCore提交和正输出token，最终发往模型的完整请求与预期入口逐字段相同，seed/temperature/max_tokens正确；两骨干模型与其各自采用profile未变。用同一条保存响应通过实际专家入口和原parser回放，32份结果、39次回调的全部提议内容一致（只排除真实运行耗时和成本元信息），0新增生成。见初版与对照验收/回放（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/initial_acceptance_and_replay.json`）、两臂验收/回放（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/comparison_acceptance_and_replay.json`）。

本轮真实成本合39调用、463982输入/19099输出token，逐调用生成墙钟之和587.343秒、模型初始化之和111.402秒、各run墙钟之和948.544秒；后两项包含并行进程，不能当日历经过时间相加。货币费用与GPU能耗未测量，训练0，真实实验求解器0；旧V1/A2/A3/A4成本没有重复算作新调用。103份历史结果文件及A1-v1源文件哈希不变，A2/A3/A4重跑为0。完整制品、配置、diff、逐题trace、请求/结果回放与成本见交付运行包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/README.md`）。

后续真正未解决的工作是把候选/知识引用唯一性和来源类型条件更完整地表达为生成约束，同时处理有限文本容量的可核验表达；不能以补格式、删除不合格条目、单独给M5增预算或恢复原答案代替。当前交付为已实现且有真实负结果的开发候选，不是五专家系统整体完成、最终方法冻结、采用版本或独立评测报告。A5/F与矩阵遵照最新用户要求继续不运行，独立D未打开。

全量CPU检查随后完成：两骨干各121输入，共242输入，其中222个适用首请求全部经真实vLLM验证及各自tokenizer的xgrammar编译，448个边界用例与原JSON parser一致；另20个输入不适用、无模型调用。适用输入的证据索引最多310项，均低于512上限，0个索引溢出，完整非空白来源内容逐一核对未丢失；全局1913项最大值来自不适用输入，不能误写成适用请求突破上界。初版完整提示的首请求最多22080输入token，CPU墙钟1550.639秒、模型加载0、生成0；两个提示修订的输出schema保持相同，其实际固定smoke请求另经各自正式入口preflight。见全量CPU收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/cpu_preflight/receipt.json`）与适用范围拆分（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/cpu_preflight/applicability_summary.json`）。结束时四卡均空闲，本任务无后台模型作业；交付状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/delivery_status.json`）、最终核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_20260922/final_verification.json`）明确无正式采用版本，当前生产`.py/.json`与最新对照源码快照一致。


<a id="a1-v2-relational"></a>

## 2026-09-22：A1-v2关系约束r3与固定预算采样对照（开发中）

这是授权的新A1方法版本范围内的结构修订，不称兼容性修复。证据包为`Documents/Codex/2026-09-21/cf_moa/a1_v2_relational_20260922/`；启动manifest保留历史结果哈希和修改前源码。r3身份`bounded_evidence_id_coverage_audit_v2_relational_r3`，此前首版/r1/r2仍为各自负结果，未覆盖。

预先固定设计：coverage由候选ID作键；≤12候选全部必填，>12时允许模型自由选择1–12项、按目录序输出，未审计ID由程序登记，末答仍见完整输入和目录。知识条件内联保存statement/origin/evidence_ids，消除模型自造K定义/引用关系；按完整条件去重后仍限12种，每行最多3条，超过记不可用，不删除内容。visible_source要求1–3引用，model_knowledge要求空引用；结论性状态要求患者证据和条件，unknown允许空值。证据ID集合按目录序、禁止重复；患者来源仅Q，offset与SHA校验保持。原scope、绑定、状态、覆盖问题、未解决项和知识内容均保留。文本上限仍160/160/128/96字符；达到上限只表明容量未核实，按保守容量失败记录，不能宣称医学答案错误或语义完整。此项规则不强制保持旧答案或翻转。

计划门槛：真实入口grammar/tokenizer预检与单元测试后，在同一固定d00000/d00001/d00008/d00003上两骨干各一次smoke。必须两骨干均通过schema、来源关系、非退化及容量检查才扩大A1开发批次；无gold选择。模型/profile、temperature0.7、seed42、audit4096/native2048不变。A5/F和矩阵仍不进入正式推理。

并行对照为`same_budget_native_sampling_3x2048_v1`，完整原消息和原生schema，固定seed42/43/44、temperature0.7，每次2048，最大输出分配6144与A1两阶段相同。按原生answer_choice投票，多选规范为集合，其余精确字符串，平票取最早出现，保留首个获胜响应的全部辅助字段。固定3次，无提前多数停止、无失败补抽、无F路径或额外资源注入。真实输入token、输出token、调用数和时间分别报告；相同上限不等于相同实际成本。它是计划中的控制，不冒充A5或第六专家。任何schema/运行错误立即停止后续抽样及后续题，保存已完成输出。


### 核心计划重新确认（2026-09-22）

用户新上传并要求严格执行的附件`0faa7315-30c9-428f-93e7-d47326d8ac96`已全文核对，共414行，与前一份逐字相同，SHA-256为`4d27d8ddefd639da24e836f7e95728879c192707986130c4af21a1fa6025b522`。本地真实实现目录为`/home/data3/txy/cf_moa/`，未发现单独的工作区`cf/`目录；因此将附件原文保存为该目录的[核心计划](../../plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)，不另建影子工程、不迁移现有代码。README与AGENTS入口指向它，机器可读阶段/约束/未完成对照清单在`configs/execution_plan.json`。此为执行基准登记，不是方法冻结。

核对后当前A1-v2的候选—患者事实—知识条件—范围记录、同预算采样控制、A2/A4复用及A3可关闭边界与计划一致。尚未完成的要求继续明确保留：完整独立专家结果及互补矩阵、路由/证据聚合、全工具同资源单agent、标亮证据/角色提示/Self-MoA及其他核心机制对照、独立冻结后评测等。四题smoke只是开发资格检查，不能替代上述交付。新附件没有新增解除A5/F/矩阵正式推理暂停的明确指示，因此沿用用户此前边界。


### r3固定smoke完成；容量问题仍未通过，采样控制可继续

59项测试通过（7.354秒），包括两新入口的真实调用路径fixture停止回归；冻结源码哈希`bb485ea8450c4600430653eebe0d7a7cdb1151cae04a3e37464cd90b11463432`，73文件。GPU0/M4、GPU1/M5运行r3各4题，GPU2/M4、GPU3/M5运行固定三次采样各4题；四进程均退出0。r3为M4 2/4、M5 1/4通过预定完整程序门槛，8份结构均有效、跨字段关系错误0，但5份触及文本容量，故双骨干门槛失败，不进正式A1批次，不以3份合格样本计算缩减主结果。采样控制两骨干各4/4原生格式有效，24次调用固定完成，无补抽；这不是质量采用。

16份完整提议与35次模型回调同缓存回放一致；35份EngineCore请求逐字段一致且都有正输出token。完整合法输入审计242条（222适用、20不适用）已完成，222条ID来源与非空白内容保持、schema构造通过，0模型调用、9.022秒。真实tokenizer的grammar构建在每个实际请求提交前执行；单元fixture不是模型预检的替代。证据为`input_audit.json`、`acceptance_and_replay.json`及逐题proposals/model_calls。

本轮smoke及控制实际成本：35调用、203741输入/15744输出token、生成墙钟之和504.305秒；没有评分或独立评测。候选r3仍未采用。解码层的紧凑JSON不接受常见换行/缩进；这可能影响模型自然结束短字段，但当前尚未证明因果。接下来先做CPU tokenizer格式可达性诊断，不增加文字容量或输出预算、不改临床内容；若诊断支持，再预先固定一个仅解码空白变化的对照，保留r3负结果。

用户已澄清核心目录正是`cf_moa/`，此前落位一致。原计划及最新暂停边界持续生效。已通过真实格式检查的固定三次采样控制拟按相同冻结代码扩展至其余117条开发输入/骨干，原4条成功smoke复用、不重跑；它是计划要求的独立控制，可与A1诊断并行，A5/F/矩阵不启动。


### 预先固定的解码空白对照r4

CPU实际tokenizer诊断已完成（65.599秒、0模型调用）：两骨干各2种候选规模，共24条可达性检查。紧凑序列可被原grammar完整接受；通常的缩进JSON在首个token就被排除；只增加结构边界0–16个空白后，同一语义fixture的紧凑/缩进形式均可接受，17个冒号后空白仍被拒绝。这证明存在格式限制，不证明它已造成全部容量失败；没有测量模型logits，不能据此宣布根因已修好。见`format_reachability.json`。

在完整原计划范围内固定一个解码对照：`bounded_evidence_id_coverage_audit_v2_bounded_whitespace_r4`。唯一请求差异为审计阶段显式`decoding_revision=bounded_whitespace_16_r4`及对应grammar允许的有限空白；逻辑schema、所有prompt/messages、临床字段语义与字符上限、parser、模型profile、seed42、temperature0.7、4096/2048预算不改。旧默认grammar与8份已发r3审计请求逐字一致。两个骨干只各同4题一次，不按结果重抽；沿用双骨干全题资格门槛，失败保留r4身份，不扩大预算。当前仍属A1-v2方法的开发解码对照，不将整个A1-v2重新描述为V1兼容性修复。


### 不调用模型的A5停止策略补齐

按核心计划和此前first-error要求离线审查发现：唯一新A5候选在某视图JSON无效时，原实现会记录error后继续其他视图，随后可能复判。后端运行异常已能锁住，返回的schema错误仍需专家内立即收尾。已补为保存已完成/失败视图并返回不可评分提议，runner随后标记stopped_on_error；不发送后续视图、复判或后续题。旧F执行核和薄适配未改，不新增A5候选、不开展A5/F正式推理。增加实际A5入口fixture回归验证只发送1个失败请求、后续输入未提交；这是执行错误策略修复，不是A5方法调参。代码`agents/a5_robust_readout.py`，证据`a5_first_error_preparation.log`；该补丁未注入正在运行的冻结A1/采样进程。


空白对照测试61项通过（8.793秒），同逻辑请求除显式解码标识外完全一致；两骨干最终prompt、所有采样字段、model engine仅grammar内容有差别。r4冻结源码哈希`da068e00ae2be61b9826156994a4063754d327df34bf2be4fb18680d794ceff7`，证据`whitespace_diagnostic/`。运行时发现其他用户作业也已进入四张卡，未干预；GPU0/1仍通过既有显存准入，未降低任何采用参数。此阶段延迟受共享负载影响，不能直接与早先空卡时延作方法速度结论。A5停止策略相关12项fixture测试另通过（0.111秒），0真实A5/F调用。


### r4结果：有限空白不是充分修复

两个骨干均2/4通过完整程序门槛，r4未通过、不采用、不扩展正式A1。M4 d00000生成15种不同条件而超过沿用的共享12项上限，d00008的scope触顶；M5 d00000、d00003的binding触顶。其他4题程序有效并有独立原生答案，但不是医学正确率。8份结果/12回调同缓存回放一致，12份最终EngineCore请求及实际采样参数一致；8个首审计逻辑请求与r3比较，唯一新增字段是decoding_revision，prompt/schema/采样不变。0截断/运行错误，4个语义/容量负结果均在原4题分母内保留。

实际增加12调用、147799输入/8577输出token、生成墙钟之和423.987秒。`whitespace_diagnostic/acceptance_and_replay.json`、`actual_first_request_parity.json`和`cost.json`保存证据。两个r4进程已收尾；其成功/负结果均不替代r3记录。CPU又完成分批结果装配工具及2项回归：只允许同策略、同代码、无重复、完整分母的已完成批次合并，schema/runtime停止批次拒绝主结果装配，语义负结果保持；用于复用采样smoke，不触发互补矩阵。

下一固定开发修订拟继续使用证据ID及状态码：scope改为对完整当前问句的确定性S0绑定，模型不再复述截短scope；binding改为支持/矛盾/缺事实/缺知识/范围不适用/未决等关系码，与原patient_fact_ids和knowledge_conditions共同解释。保留各知识陈述及其来源，不删核心语义字段；原生末答仍见完整原题、所有资源，允许保持或更改。内联形式的知识总上界按12候选×3条件=36明确计数，撤去已不对应实际共享表的额外12种限制；这是合同容量结构修订，不能称r3同配置成功，最大4096/2048 token仍不变。先测试、冻结、两骨干同4题各一次，沿用完整程序门槛；不以此自动宣布方法采用。


状态码合同修订`bounded_evidence_id_coverage_audit_v2_relation_codes_r5`代码、68项测试（8.939秒）及冻结完成，源码哈希`91e4054213a72c7177d170f196e9c3f6a63eeb0775da482084104f5e4437c066`，证据`relation_codes/`。其中r5是A1-v2的合同修订编号，不是R5专家或结果重命名。新schema限制scope=S0、关系码与supported/contradicted/unknown一致；确定性展开保留候选、患者事实、知识条件、绑定、完整问句范围、支持状态、覆盖问题和未解决项。剩余自由知识陈述160字符/未决详情96字符的容量失败规则继续有效，不通过删除文本来伪装成功。两骨干各同4题一次smoke正在按冻结入口启动；通过完整门槛之前不扩展A1。


生产代码兼容性再核验：当前代码重新回放r3/r4及原生采样控制的24份保存结果、47次模型回调，全部提议与请求一致（仅排除成本和本次准备耗时），0新模型调用。启动账本中154份原始结果文件哈希均未变，见`production_regression_and_preservation.json`。控制配置清单明确区分已实现的固定三次采样、A1资源单答局部控制与仍待实现的全工具同资源单agent，不用前两项顶替后者。


### 固定三次原生采样M4扩展：真实首错停止（未恢复）

M4在第60个扩展输入d00063的seed42第一抽，真实生成2048 token / 12435可见字符，finish_reason=length，截断在step_by_step_thinking字符串中，未完成answer_choice。原始完整当前请求为32583输入token；没有删减长上下文。此为`output_truncation`，inference_started=true、semantic_result=unavailable、method_score=not_scored，不记为答案错误。

runner自动stopped_on_error并退出1：first_error request_id=d00063、ordinal0、schema类别，已提交/完成178、在飞0。该题seed43/44及其后57题均未发送；已完成59题/178调用和原4题smoke保存不变。扩展分母117=59完整+1失败+57未提交；合并研究范围121=63完整+1失败+57未提交。不能把后两类删掉组成主准确率，也不能用同配置补抽。M4控制路径保持停止，M5控制和A1 smoke是独立冻结路径，可正常收尾。当前不调整其2048单抽上限、提示或seed。

M4扩展成本178新调用、685284输入/49796输出token、生成墙钟之和1295.804秒；启动和请求记录含首错时真实数量。`sampling_development/m4_failure_classification.json`是补充诊断，原proposals/journal未覆写。此负结果属于同预算原生采样控制，不归因A1或基础设施，暂不生成该控制M4主结果。


### 状态码r5两骨干smoke通过，进入完整开发批次（不是质量采用）

M4/M5均4/4通过冻结程序门槛：8份审计JSON及原生末答有效，引用/来源检查通过，bound_paths非零，0文本饱和、0重复关系/截断。8份完整结果、16次缓存回调经真实专家/parser入口回放一致，16份EngineCore请求与入口预计逐字段相同，temperature/seed/max_tokens正确且都有实际正输出token；不是mock parser验收。实际smoke成本16调用、200990输入/11259输出token，生成墙钟之和522.088秒，未使用gold选择，未做独立评测。

依照此前“兼容与两骨干真实检查通过后直接继续”的授权，复用4题/骨干成功smoke，按同一冻结源码和参数运行剩余117条/骨干（预计107适用+10不适用），完整分母121不变；不同于重新生成已有效结果。新制品在`relation_codes/development/`，extension_manifest逐项链接原V1失败、各V2负结果、源码/config/schema diff、实际preflight/smoke回放和输入哈希。first-error停止仍有效；语义/容量负结果单独保留，不代填旧答案、不删除分母。A2/A3/A4不重跑，A5/F/矩阵正式推理仍暂停，M4采样控制的截断也不因A1资格通过而清除。


### A1同资源单次作答控制扩展准备

GPU2因M4原生采样停止而释放后，分配给独立的A1同资源单答控制；该控制先前两骨干各4题已有效，不重跑。已核对其采用源码与首版冻结code_lock完全相同，8份已存resource_hash与当前状态码A1的完整合法资源渲染一致。使用原冻结源、原2048/0.7/seed42/profile扩展剩余117条/骨干，先M4后M5的固定队列遇首错即停止，不替代或恢复已失败的三抽采样路径。证据`resource_control_development/`。这补齐计划中的A1同知识/规则比较，仍不能称整个五专家系统的全工具单agent控制，也不声称与两阶段A1总成本相同。A5/F无调用。


### 离线评分封装：不可用与答错分开，分母不删

在正式离线评分前发现新原型的score_proposal封装会把native_proposal=None传为空输出，随后将原生函数返回的false直接标为答错。按用户“不可用、不可评分且保留失败分母”的要求，现只在新封装层对缺失答案标记correct=null、method_score=not_scored、semantic_result=unavailable；原生评分函数及有答案时的原生判定保持逐字不变，历史评分文件不重算/不覆写。原生函数对空值的调用仅保留任务标签规范化结果，不把它计作该方法的答案评分。

完整样本/母题/配对的成功率分母仍包括不可用项；字段另报不可用数、已评分数及实际错误答案数。沿用的score/mean_native_unit_score数值字段明示为完整分母的end-to-end native success，不把每个不可用样本伪标成错误答案，也不只对成功子集计算主结果。矩阵的“错误修复”和“从不可用恢复”分别计数；没有运行实际互补矩阵，只做合成fixture回归。stopped_on_error运行仍禁止主结果装配/评分。原生source_lock保存于`native_scorer_unchanged.json`，不涉及正式v5或采用基线变更。首次测试命令误写不存在的类名CPUPreparationTests，保留失败日志；按实际PreparationTests重跑，未产生任何模型请求。


完整A1开发批次早期已出现剩余自由字段容量负结果：M4 d00006知识statement触160，M5 d00007/d00009/d00010/d00012知识或unresolved detail触上限；均JSON完整、来源关系通过，按冻结容量政策返回unavailable/not_scored，不是答案错误。四题smoke通过不能外推完整开发全成功，当前不宣称采用。上述预定义语义/容量负结果与schema/基础设施错误分开计数，固定批次继续完成覆盖审计，不在运行中改参数、挑样本或加预算；任何schema/runtime错误仍首错停。A5/F/矩阵继续暂停。不可用评分封装相关12项测试已通过（0.122秒），三份原生评分/规范化/标签文件哈希与之前保留的A2评分收据逐项相同。


### M5固定三抽原生采样完整收尾

M5扩展117条全部返回原生结果；与原4条smoke按同一冻结policy/code_lock严格无重复装配为121输入、363调用。121份结果与363次回调的实际专家入口/原parser同缓存回放全部一致，最终EngineCore请求逐字段一致、实际推理与采样参数确认；验证与装配0新模型调用。总成本（含复用smoke的原始成本，不重复算作新增）为1423860输入/97863输出token、生成墙钟之和2269.589秒；扩展本身351调用、1393656输入/94587输出token。M4仍是独立的stopped_on_error负结果，不因M5完整而宣布两骨干通过。

另在隔离离线流程按未改原生函数评分M5的121输入/157原生映射，主完整范围74个非reference基准unit等权成功率（不是74个独立患者/家族）为0.599099，不含独立泛化声明。配对维持/应变计数见`sampling_complete/m5_scores/paired_metrics.json`；只运行了该控制自身的原生/配对统计，没有构建依赖完整A1的互补矩阵，没有更改正在运行的A1合同或任何参数。原生源及本次离线封装的哈希随评分收据保存。


强旧head控制的CPU可复用范围核对：迁移成功的20062条缓存是历史R1非reference范围，不能直接称为当前121输入的完整强控制。当前M4/M5各37条能按原item_id对应，剩余须按真实原生分派、已有A2/A3输出和原始路径补齐合法复用；此处未根据R标签选答案或运行任何模型，未伪造缺失控制。清单为`legacy_strong_control_cache_scope.json`。M5采样的74个ALL单位是原评分的非reference基准unit，而完整开发选择按40个家族保留所有相关端点/任务，不能把单位数当独立患者数。


本阶段CPU准备最终回归69项通过（日志`unit_final_preparation.log`）；154份受保护历史结果再次核对未变。活动进程、冻结配置、已停止控制和未完成任务记录在`checkpoint.json`，实际逐题状态由`live_status.py`只读观察。完整目标仍active，尚不具备系统采用、主实验冻结或独立评测结论。

### 2026-09-22：完整开发范围的旧R1控制复用与同资源控制收尾

新增旧R1开发回放驱动（本地制品：`/home/data3/txy/cf_moa/evaluation/replay_legacy_development.py`），只读当前合法InputPacket、原始初答和已保存A2/A3回调，不读gold、类别或配对账本。按旧入口的实际题型/规则资格选择分支，新旧入口分别注入相同响应，逐次检查完整逻辑请求；原生答案和完整旧结果相同后才保存对照。原题直通保留历史完整JSON和辅助字段；规则/目录分支保留原来的列表/诊断答案合同，不编造新解释。

M4/M5各121输入全部核对：9规则、8目录、104原始路径，每骨干57个已存模型响应在新旧入口各回放一次，共242输入/228缓存回调、0新生成。原始输出、来源配置和历史代码哈希均未变。此结果是完整开发范围的`adopted_R1_dispatch_saved_callbacks_v1`，其新旧原生输出一致，不是已完成R1+R4+F组合，也不把当前新采样的A2/A3响应伪称为历史R1原批次生成。证据在`a1_v2_relational_20260922/legacy_dispatch_reuse/`。

随后在隔离离线流程评分，各121输入/157原生映射、40个选中家族；74个非reference基准unit的等权完整分母成功率为M4 0.700000、M5 0.666667。M4有2个唯一输入继承原始不可用答案，保持not_scored和完整分母；M5无不可用。已评分错误答案分别38/42个唯一输入。保持对双正确35/73、38/73；应变对1/4、1/4。这里是旧控制自身开发结果，不是五专家互补矩阵或独立泛化。请求漂移/多余缓存回调拒绝测试2项通过；首次fixture重复传schema的程序错误及修复日志分别保留为`unit.log`、`unit_fixed.log`，未影响真实推理或控制结果。

同资源A1单答控制M4扩展117输入全部完成，复用原4条smoke后为121输入：111适用原生结果、10不适用零调用。原冻结入口下121份结果及111次实际请求全部一致，包含服务端参数与同响应原parser回放；没有为了匹配历史重新生成。总历史实际成本（复用只计一次）111调用、1115153输入/27670输出token、模型生成墙钟之和882.929秒；本轮装配/回放/评分新增0调用。完整分母74个非reference unit成功率0.527027，10个unsupported仍保留not_scored，不能将其删除后与全任务控制声称相同覆盖。它是A1同知识/规则单答控制，仍不替代五专家系统的全工具单agent。证据`resource_control_complete/m4`及`m4_acceptance_and_replay.json`、`m4_scores/`。

此时A1状态码r5两骨干完整批次与M5资源控制继续按原冻结配置运行；容量/语义负结果保持原身份，不在运行中改方法或预算。A2/A3无新推理，A4验收继续有效，A5/F/矩阵的正式推理暂停继续有效。

M5资源控制随后完整收尾：111适用原生结果、10不适用，121份同响应回放和111份实际请求验收一致；总历史成本111调用、1088510输入/32401输出token、模型生成墙钟之和1204.653秒。完整74 unit成功率0.536036；保持对44/73、应变对1/4双正确，37个唯一输入有实际错误答案，10个unsupported不可评分但保留分母。装配、回放和评分均0新调用，原4条smoke未重跑，GPU2资源队列正常退出0。两骨干控制不是同实际总算力比较，运行时还存在共享GPU负载，不能将两次墙钟差异直接解释为方法速度。

### 同预算标亮证据控制：代码与CPU验收（无模型调用）

按核心计划§5.5准备独立控制`same_resources_bounded_evidence_highlighting_v1`：代码（本地制品：`/home/data3/txy/cf_moa/controller/evidence_highlighting.py`）、配置（本地制品：`/home/data3/txy/cf_moa/configs/evidence_highlighting.json`）。与A1状态码r5共享完整原题和同一候选/规则/目录/证据ID资料；第一步只为候选选0–4个已有来源ID，至多12个候选行，不生成知识条件、支持状态或绑定解释。第二步看完整原题、所有资源和定位后的高亮来源，输出完整原生答案，允许维持或更改。大目录明确partial且末答仍看全部候选，候选未高亮不等于拒绝；溢出保留不可用，不代填初答。这是机制控制，不能改名为新的A1成功结果。

两步预设上限4096/2048、temperature0.7、seed42及各自readout profile与A1相同，记录实际tokens/时延，不声称等上限就是等实际成本。只含有限ID对象/数组的schema独立登记到现有有界空白解码器；原A1合同和正在运行的冻结目录不变。4项CPU测试通过，验证原生辅助字段、允许改答、完整资源hash、实际xgrammar对重复/外来ID的拒绝及正式runner首错后不发末答/下一题。完整回归75项通过（9.522秒）。实际两模型tokenizer的全开发输入grammar检查正在进行；这些CPU检查不冒充请求已进入模型，真实入口smoke仍待执行。

新增控制后的回归另用当前生产入口重放r3/r4/r5、固定采样和资源控制的40份已存结果/71回调，完整请求与提议一致，154份受保护历史文件无变化，0模型加载/生成。首次回归脚本误将prepare边界与EngineCore入口跨层比较，产生output_kind 0/2和外层键差异；修正为分别比较原prepare请求和经原同步入口转换后的最终请求，全部一致。未修改采样参数、提示或采用实现。首次脚本错误和修正日志均保留于`highlight_preparation/production_replay*.log`；这是验收脚本层次错误，不是已发现的模型请求漂移。


标亮控制的两模型实际tokenizer CPU检查已完成：222适用请求全部构建grammar，20不适用无请求，16边界检查一致，最大首阶段输入23888 token；耗时422.974秒、模型加载/生成均0。配置/源码已另存`highlight_preparation/frozen_code`，源码哈希`cd257d763d8c0e16e91dc256fada834a7d9e8b76e183f87d4e226ec4f8ac037f`。下一步在空出的GPU2按固定M4→M5队列各运行既定4题、每题至多高亮和原生末答两次，4096/2048、0.7、seed42不变；正式入口实际preflight、EngineCore记录和原parser检验，首错停止、不补抽、不比历史文本逐字一致。此为新增控制的真实smoke，不恢复失败的M4三抽控制、不启动A5/F或矩阵。启动和实际成本另记`highlight_preparation/smoke/`。


标亮控制两骨干各4/4真实入口通过，8完整原生答案、16最终请求与16同响应回调一致，实际输出均正token；成本197597输入/3182输出token、模型生成墙钟之和158.739秒。M4 d00000高亮ID总数0是合同允许的实际选择，保留，不改提示强迫引用、不重采样。大目录各12行保持partial，完整原生答案仍见全部合法候选。这是格式/执行验收，不是效果采用。按同一冻结源码和参数在GPU2扩展每骨干剩余117输入，先M4后M5；原4条smoke各自复用，完整分母121，任一路径首个schema/runtime错误则停止队列。启动manifest为`highlight_preparation/development/extension_manifest.json`。A1当前主批次不改，A2/A3/A4不重跑，A5/F/矩阵暂停和独立评测未开启的边界保持。


范围补证：M4三抽截断的d00063属于无显式候选的relation任务，两骨干完整上下文分别141991/140711字符；A1及资源/标亮控制对此均按既定有限候选能力返回unsupported、0请求。同资源控制完整收尾不代表已经修复该长上下文截断，更不能用它替换原三抽失败。该控制覆盖差别与10个unsupported分母均保留，见`long_relation_scope_check.json`。A1完整批次的收尾回放脚本`relation_codes/assess_development.py`已准备（只做语法检查，尚未对未完成批次执行），届时必须包含语义/容量负结果并单列请求一致性与方法可用率。

### 同工具单agent控制：CPU实现与输入容量问题

2026-09-22继续实现计划§12.2的完整同工具单agent对照，代码为控制循环（本地制品：`/home/data3/txy/cf_moa/controller/single_agent_tools.py`）、共用工具（本地制品：`/home/data3/txy/cf_moa/tools/single_agent_tools.py`）及单独配置（本地制品：`/home/data3/txy/cf_moa/configs/single_agent_tools.json`）。由同一模型选择工具、填写参数、读取结果后给出完整原生答案；不调A1–A5专家提议入口，不靠专家身份投票。保留独立ControlResult/control_id，未把它命名为第六医学专家或A1。可用资源包括当前完整原始消息、当前初答、公开目录/原骨干先验、有限规则、合格代码视图，以及仅在输入明确完整时可用的原生理求解器。原规则resolve、六排列评分/校正/映射、局部动作编译和求解器均直接复用已核对执行核；可关闭A3编辑仍为off，与默认专家配置相同。

最多4个不同工具动作，选择/参数/视图/原生末答均计实际模型调用，目录每次为完整6评分；生成采用该新控制明确的readout配置、seed42/temperature0.7及128/2048/2048/2048阶段上限，不修改A2原facts温度0或A4采用设置。原模型/缓存配置的facts/catalog/A4与这个新readout控制的差别继续单列，不声称GPU配置完全相同。所有调用共用原输入预算；不足时保留unavailable，不代填初答。模型格式错误首错停；有效JSON却不能指定合法动作的工具语义失败另记，不假装求解成功。该控制可能使用A5共享视图，故其真实模型推理也保持未启动，不能通过控制名称绕过A5/F暂停。

首轮7项fixture测试通过，随后完整82项测试通过（9.389秒），涵盖原执行核一致、CrCl数值来源、完整辅助字段回映、允许保持/改答、正式runner首错停止、预算耗尽及未提供模型不得发明模型。这些是CPU程序检查，0新模型调用，不是方法效果。随后真实readout/tokenizer/xgrammar的CPU请求检查在M4 d00005停止：原题138665字符、没有有限候选；却被重复展开为1898段、603604字符的证据索引，首请求达到248436 token，超过原131072上下文。此控制首次CPU容量失败保留为`same_tools_single_agent_v1 / initial_full_index_r0`，源码哈希`c99a938851d9e441f0cbd57c0a6f3da68c91eaaf8e6a0369f3bfe04339c7daba`，inference_started=false、semantic_result=unavailable、method_score=not_scored，0模型加载/调用。M5同题只做长度诊断（1886段、600080索引字符），未将其写成已执行该模型预检。

修正限定为输入重复表示：有限候选审计本就不适用的输入，不再把未使用的A1索引全文重复附加；完整原始消息和当前初答仍逐字保留，这些任务仍进入该单agent的原生答题路径，不改成unsupported。有候选且适用的输入继续获得完整相同ID表，模型上限、采样参数和实际来源均不改。新增原文保留/无候选仍可改答的回归，并以`finite_candidate_index_only_r1`记录这次序列化修订；原始代码、CPU失败和长度诊断在`single_agent_preparation/initial_code`、`receipt.json`、`initial_failure_diagnosis.json`保留。后续CPU结果写入独立`finite_candidate_index_r1/`，尚不能称真实入口验收通过。现有A1/标亮冻结批次不受影响，未重跑A2/A3/A4。


同工具控制的修订r1 CPU预检已完成：两骨干各121开发输入＋1条单独已暴露生理fixture，900份实际backend/tokenizer请求准备全部通过，最大输入44842 token；105.534秒、0模型加载/生成。83项回归测试通过（9.469秒），其中新增无候选长题不重复展开索引、完整原文保留且仍可原生改答的检查。验收源码另存`single_agent_preparation/finite_candidate_index_r1/frozen_code`，code_lock哈希`b240f02190603f98c6d825b96af01863cbeba18a3ea4b6c7ec85839cbd72c481`。初次r0超限负结果与源码保持。这里没有生成工具参数、视图或最终答案；之后真实调用中的动态观察仍需逐请求预检。因此CPU通过不算真实smoke通过，不启动共享A5视图的控制推理，也没有系统效果或独立评测结论。证据导航与preparation_manifest已保存，控制状态同步到`configs/control_plan.json`。


<a id="a1-r5-complete"></a>

### A1-v2 relation_codes_r5完整开发收尾：请求通过、方法未采用

M4/M5两条冻结扩展均正常退出，未发生schema/基础设施错误；各117条新扩展与原4条smoke按完全相同的code_lock、输入哈希、profile和policy无重复装配为各121输入。使用`relation_codes/frozen_code`的真实A1入口分别重放完整输出（包括不适用、容量和语义负结果），202＋171＝373次缓存回调全部精确一致；对应373份实际EngineCore请求逐字段核对、实际正输出token和0.7/42/4096或2048参数均通过。装配/回放/评分新增模型调用0，原批次没有重采样。

| r5完整范围（每骨干121输入） | M4 | M5 |
|---|---:|---:|
| 有完整原生答案 | 91 | 60 |
| 字段触容量上界，按冻结规则不可用 | 17 | 51 |
| 语义关系无效 | 3 | 0 |
| 能力不适用，零调用 | 10 | 10 |
| 实际错误答案（唯一输入） | 36 | 18 |
| 完整分母原生成功率（74非reference unit等权） | 0.404505 | 0.230631 |
| 保持对双正确（73对/25家族） | 25/73 | 15/73 |
| 应变对双正确（4对/4家族） | 0/4 | 0/4 |

本范围为40个已暴露家族、121唯一原生输入、157原生评分映射。74是原评分的非reference基准unit，不是74个独立患者；R类别可重叠不能求和。不可用30/61个输入的correct=null、method_score=not_scored，仍保留完整成功率/失败分母，不记为错误答案。保持对按家族聚类的95% bootstrap区间M4[0.153846,0.535714]、M5[0.050826,0.380968]；仅4个应变家族和0/4结果不能支持广泛临床推断，bootstrap的零区间也不表示真实不确定性为零。详细配对及评分收据见各`complete/{m}_scores/`。

容量诊断与V1截断分开：本轮负结果的JSON完整，知识statement触160字符或unresolved.detail触96字符，按预先冻结的“未验证内容完整性”政策返回不可用。M4知识字段触界涉及16题/32字段，未决说明2题/2字段（其中1题重叠）；M5分别9题/14字段和50题/84字段（8题重叠）。M4另3题包含重复知识条件，保留audit_semantic_invalid。两骨干所有调用最大实际输出分别2460/3217 token，未触4096；没有证据支持通过增加输出预算解决这次合同负结果，也不通过事后删除未决字段把它算成功。原V1的222个grammar失败和M5 d00003的4096截断仍保留原身份。

同资源单答完整成功率为0.527027/0.536036，旧R1分派控制0.700000/0.666667；M4标亮控制0.527027（M5当时仍运行），M5三抽控制0.599099。A1 r5当前低于已完成核心控制，且存在明显适用范围内不可用，因此**不采用**为系统默认A1；不把程序回放通过写成方法通过，也不将控制改名为A1。这里只汇总各自离线结果，没有运行五专家互补矩阵、oracle或路由选择。M4三抽已停止，不能用成功子集给它补主分数；旧R1控制还不等于含R4/F的完整强旧系统。等最大输出分配不等于等实际成本。

r5真实成本（含原smoke恰好一次）：M4为202调用、2276784输入/108175输出token、生成墙钟之和5758.676秒；M5为171调用、1933533输入/120322输出token、4901.570秒。合373调用、4210317输入/228497输出token、10660.247秒；不含原先RAG/初答的历史成本，不将共享卡负载下的生成墙钟和解释为独占GPU方法速度。所有请求、实际模型事件、提议、逐题失败和cost均在`relation_codes/complete/`及链接的原smoke/development内；分析脚本`review_complete.py`只读这些制品与隔离评分结果，不发模型请求。

下一阶段仍受用户明确暂停约束。A5/F固定四题资格检查的源码和合法输入正在`a5_f_preparation/`准备；按预先输入顺序选第一个普通单选、带必需辅助字段题、NLI、无合格视图的relation，编号d00001/d00003/d00023/d00005，两骨干相同结构、各自原消息不变。该选择不读gold、配对或按模型答对选择。每骨干A5最多17、F最多21次主请求（实际缺码请求另计，仍受每题原总预算限制），真实启动须先处理既有暂停，当前0调用。A5/F、互补矩阵、独立评测均没有因r5收尾自动解锁。


A5/F固定方案的CPU预检已完成：34请求（两骨干首入口、合格视图及6个合成分歧的定向复判分支）均通过实际readout backend/tokenizer/xgrammar准备，最大输入35165 token，12.545秒，0模型加载/生成。合成分歧只用于经过原parser到达自适应分支，不是历史真实响应、模型能力或真实smoke。源码锁`15acbdf558a78e6d9232ce45043c8031ec908ef3a36f06065585adf891519043`、各骨干原配置及来源在`a5_f_preparation/frozen_code`和manifest，命令已准备但未执行。

启动方案去除一次重复F生成：每骨干A5仅对3个合格视图输入真实运行（最多12次主请求）；F对4个合同输入运行（最多21次），relation d00005的已存F响应随后经过真实A5回退入口逐请求回放，保留旧F身份和实际成本。因此预定主请求上界每骨干33、两骨干66，缺码请求仍实际计费并受原逐题预算约束；不把回放算成新推理。A1 r5不采用，A2/A3/A4不重跑，矩阵仍暂停。已向用户请求决定是否解除A5/F固定smoke及通过后的当前开发扩展暂停；这是来自用户先前明确暂停的待答权限问题，不因GPU空闲或CPU检查通过自动放行。在回复前只继续现有标亮控制收尾和CPU工作。

154份受保护历史制品再次核对全部未变；核心计划与用户指定附件逐字一致，校验见`relation_codes/complete/preservation_check.json`。


用户随后明确“解除 A5/F 暂停，按固定方案分阶段执行”。本阶段据此只启动已准备的两骨干真实smoke，并在实际请求/同响应回放验收通过后允许扩展当前121输入开发范围；矩阵与独立评测不随之放行。授权原文及范围存`a5_f_preparation/authorization.json`。资源复查GPU1/3各97367 MiB空闲，分别分配M4/M5；每骨干A5三题后F四题串行，首个runtime/schema错误停止该队列，已完成/在飞响应保留。原A1负结果、A2/A3/A4输出及采用参数保持。本次启动及逐调用成本记录在`a5_f_preparation/smoke/{m4,m5}`，后续不能把CPU合成分支检查当作真实模型验收。


### A5固定smoke首错停止：两骨干复判发生结构性异常展开

按授权实际启动M4/GPU1、M5/GPU3，均在A5 d00003的ordinal3（唯一原文复判）输出2048 token、finish_reason=length后原parser失败，runner与外层固定队列均stopped_on_error。每骨干计划3个A5输入，实际1成功（d00001）、1失败（d00003）、1未提交（d00023）；均提交/完成7请求、在飞0。其后的4个F输入未发送，F目前仍0新调用；并非F方法失败。没有扩展正式A5、补抽、增加上限或删除失败分母。

M4复判7608字符，完整native_answer为2138字符/484独立重分词token；随后5452个连续结构空白约1558 token，引用依据和reason尚未开始。M5复判3290字符，完整native_answer为1377字符/292 token；第一个引用的quote完成，但start生成了1682位、超出所有合法来源长度的整数，末端呈周期重复，引用对象未完成、reason缺失。两者属于生成退化/无界结构序列化问题，不是正常输出只差有限闭合，也不支持加预算。部分native_answer可诊断读取，但不作为原方法成功或修复结果评分。补充分类统一inference_started=true、failure_type=output_truncation、semantic_result=unavailable、method_score=not_scored；原proposal、journal及first_error分类不覆写。

14份最终EngineCore请求的参数和实际输入接受记录全部一致；4份已保存提议（含两份失败）经同一冻结A5入口、原parser和14缓存回调重放完全相同，证明失败保存正确，不是方法通过。只读诊断0模型加载/生成，原smoke全部文件校验未变。主证据`a5_f_preparation/smoke_diagnosis/receipt.json`和`position_and_classification.json`：后者明确旧词法helper的current_path是最后访问节点，不是M4空白等待时的栈位置，并补充数字尾部重复统计。两骨干总真实成本14调用、71183输入/7462输出token、模型生成墙钟之和123.551秒；CPU预检曾通过34请求，只证明grammar可构建，不能预防这些生成退化。

当前只检查不改prompt、逻辑schema或模型参数的最小解码限制：限制JSON结构空白，并利用当前合法来源长度限制引用start的整数序列；不删除任何原生辅助字段、引用或理由，不把不合法巨大offset视作方法语义。尚未应用或实际验证此修订，不重启原失败批次。

标亮证据控制M5也已完成并通过完整121提议/222请求原入口回放；两骨干各111可用、10不适用，0新回放/评分调用。M5完整74 unit成功率0.549550，保持45/73、应变1/4，36个唯一错误答案；10个unsupported仍not_scored并保留分母。M5历史实际成本（含原smoke一次）222调用、2416948输入/45710输出token、1399.852秒。两骨干标亮控制合444调用、4868737输入/87345输出token、2659.685秒，没有以控制结果替代r5负结果。r5及全部已完成控制汇总在`relation_codes/complete/development_review.json`，没有互补矩阵或独立评测。


A5最小结构解码修订已完成CPU验收并按已授权分阶段资格流程启动固定真实检查。新增可选入口`A5_structural_compat`，方法身份仍是唯一`qualified_code_views_original_adjudication_v1`，解码修订单列`bounded_a5_whitespace_reference_offset_r1`，不是重命名原候选为成功。原A5默认/F入口保持；完整逻辑schema、prompt、引用ref/quote/start和reason、原生辅助字段、seed42/temperature0.7/2048均不改。仅对复判EBNF结构空白设0–16，并将start的十进制序列限制为0至当前完整可见来源最大字符数；每个原本有效引用仍可表示，实际ref/quote/位置原验证仍执行。没有给一般文本、数组或其他数值字段偷偷加容量上限。

5项新增测试及完整88项回归通过（9.595秒）。两真实骨干分别复用d00003原3个有效视图，经正式新入口捕获复判请求，逐字段证明除声明的decoder/source bound外原请求不变，实际tokenizer/xgrammar通过且拒绝原失败前缀、超长结构空白和越界offset；旧默认A5的4份已保存提议和14个请求也仍精确一致。源锁`996876e1ade377d8a93c1afdba82ed9c516870610bc9f7e5b92ee6558c8894e1`，diff、CPU收据与完整快照在`a5_f_preparation/structural_compat_cpu/`。这是非语义结构修订，仍未证明新生成稳定性或效果，不增加上限。

为了不重跑有效视图，新增严格的前缀复用驱动：d00001三视图直接回放原有效答案；d00003前三视图逐逻辑/物理请求核对后复用，仅重新生成已改变解码的复判；d00023此前未提交，按原计划首次运行。另3项实际runner回归通过（5.576秒），验证源请求漂移会在任何新提交前停止、只有新RPC计为本轮提交、首新错误不发送后题、整题一致结果零模型加载。首次源事件与新事件分账，不能把回放伪称新生成或从成本中抹掉原14请求。

新目录`structural_compat_cpu/smoke/{m4,m5}`，GPU1/3，预定每骨干最多5个新请求；新launch_manifest链接原失败和全部验收，原smoke/journal不恢复或覆写。F仍未发送；修订真实检查未通过前不扩A5，不启动矩阵、独立评测或A1重跑。


<a id="gpu-staged-execution-20260922"></a>

### 2026-09-22：GPU分阶段执行、A5修订负结果与独立F扩展

用户询问GPU为何空闲后重新核查：模型生成一直使用vLLM CUDA，CPU用于tokenizer/grammar、回放、代码和原生评分。A5两条修订smoke在约一分钟内各一个新复判请求后再次首错停止，GPU随后释放；不能把已停止队列当成仍在生成。为避免独立控制等待A5，将此前完全未发送的F四题移至GPU0/2并行，原A5-first队列的F未提交记录保留，采用源码、输入、prompt、schema、参数和内部早停均不变。独立调度manifest在`a5_f_preparation/f_independent_smoke/launch_manifest.json`；未中断其他健康负载。共享卡实测利用率一度均100%，不把这些瞬时数值或生成墙钟当作独占性能比较。

A5结构修訂每骨干实际只新增d00003一次复判，原6份有效视图逐逻辑/物理请求复用；d00023仍未发送。两新请求已由实际EngineCore接受并各生成2048 token、finish_reason=length。M4新输出9223字符，native_answer完整6830字符/1483独立重分词token，disagreement_basis完整5项915字符/278 token，reason已1418字符/266 token仍未结束。最长结构空白降至16，偏移整数有限，但5条完整引用均不能精确绑定；native解释有3种句子各重复2次。M5输出11549字符，仍停在首个native_answer.step_by_step_thinking字符串，11497字符/2032独立重分词token，未完成任何标量；10种完整句子重复36次，最多5次、重复冗余约4467字符。两者语义均未完整，不是仅补闭合结构；结构修订不足以使此候选通过真实入口资格，保留原身份和负结果，不增加预算、不恢复正式A5。

新A5真实成本合2调用、31452输入/4096输出token、生成墙钟之和78.741秒；原14失败批次调用成本另保留，复用12视图不再计新生成。实际2请求的prepare/EngineCore/参数一致；完整4份提议（含2份失败）用14缓存回调重放完全一致，原新旧smoke文件校验未变。证据`a5_f_preparation/structural_compat_cpu/smoke_diagnosis/receipt.json`。诊断helper最初假定至少一个标量已结束，遇M5首字符串截断报错；已改为last_terminated_node=null，原诊断错误日志保留。这是分析程序修正，未修改模型输出、实验源码或评分。

F两骨干各4/4完整原生输出通过，M4 16/M5 15真实请求（含原NLI评分及生成），31份EngineCore请求和8份完整输出经冻结F入口/原parser回放一致，未要求重新采样文本与历史逐字相同。M4实际181981输入/4989输出token、136.545秒；M5 154841/2354、86.758秒。合31调用、336822输入/7343输出token、223.303秒，回放新增0。验收脚本`a5_f_preparation/assess_f.py`与收据在`f_independent_smoke/{m}_acceptance.json`。据用户已授权阶段，在GPU0/2启动各剩余117输入，原4题各自只复用一次；完整范围仍为各121输入/40已暴露家族/157原生映射，首错停止并保留所有未提交项。启动记录`a5_f_preparation/f_development/extension_manifest.json`，尚未收尾、没有主分数。

### 同工具单agent真实smoke与回放边界

A5/F共享视图暂停解除后，计划核心控制same_tools_single_agent_v1使用先前CPU通过的冻结源码b240f02190603f98c6d825b96af01863cbeba18a3ea4b6c7ec85839cbd72c481，在GPU1/3运行固定6条开发输入（首规则、首目录及既定A5/F四题）＋1条原已暴露生理fixture。生理fixture独立标记，不加入v5分母。未调用专家提议或A5复判入口。最初准备脚本误把本地NLI当作独立answer_format=nli，选择器失败、未生成输入文件；两个CLI随后在加载输入前退出，0模型/0请求。此准备错误及日志保留`single_agent_preparation/smoke_prelaunch_selector_error/`，修正为沿用已冻结的合法四题列表后才实际启动；没有按模型答案挑样本。

M4在d00000选择规则工具后，参数生成2048截断，原parser失败；submitted/completed=2、in_flight=0、后6项未发送。生成真实成本36375输入/2059输出token、57.973秒；不记为原生错误答案，不从计划7项中删除。M5七项均给出完整原生答案，30请求、562024输入/3701输出token、144.687秒，包括真实规则、六排列目录、视图及给定生理求解工具。M4的失败提议及2缓存回调完整重放一致。M5原入口回放在首规则题的末答请求发现差异：工具facts字典来自原执行核的新进程键迭代顺序不同，内容和值完全相同，但写入prompt的JSON键序不同；原始消息、其他资源和末答指令相同。保留`smoke/replay_request_difference.json`及原验收错误日志，不把生成合法等同请求回放通过，当前不扩此控制。历史R2/A2执行核和已保存结果不改。后续修复应限定新控制的确定性工具结果序列化，并单独声明解码修订，不通过忽略请求差异假装验收成功。


用户在2026-09-22T17:54:09.713281+08:00明确选择“保留 A5 负结果，推进旧 F”。据此A5唯一受控视图候选及其结构修订均不采用、停止新增生成；稳健分支继续采用真实身份legacy_f_equal_nli_paths_else_full_maj5进行当前开发范围验收，不将F改名为新A5成功。决策证据`a5_f_preparation/a5_non_adoption_decision.json`，原失败、成本、分母与代码保留。矩阵和独立评测未因此解锁。同工具控制的独立工程修复可以继续，不重新运行A5复判。


同工具控制的修复限定在新控制层，版本标记`finite_candidate_index_r1_stable_rule_facts_r2`：规则核原值、列表次序和输入保持，只在工具结果写入prompt之前按固定键序排列facts；对工具参数生成的JSON结构空白设0–16，不限制字符串内容、不删除事实字段、不改逻辑schema或0.7/42/128/2048等原参数。旧M4输出5513字符，其中结构空白5127、最大连续5092，确认不是正常语义内容不足。原7题M5生成结果及键序差异保留，没有忽略差异算通过。

新增稳定序列化/语法边界回归，完整90项通过（11.042秒）；首次测试调用了本地版本不存在的accept_string API，日志保留，改用已安装xgrammar的调试接受接口后通过。r2固定7题的46个实际backend/tokenizer CPU请求准备通过，另正式控制入口用32个旧回调作CPU分支fixture，逐请求确认改变仅为声明的参数grammar或规则facts键序；改变过的请求不作为真实成功复用。源码锁`6ed4c0912e4f8b048f14edbe20b1092f52e9993713b113aab6eee3735313f6cc`，diff及CPU收据在`single_agent_preparation/stable_tool_json_r2/`。

两骨干修复smoke在GPU1/3启动，仍各6个开发输入＋1个独立生理fixture，原M4只复用1个有效选择请求，M5复用26个逐逻辑/物理请求完全一致的有效前缀；所有改变过的请求实际新生成，原错误响应不复用。原32调用和新调用分别记账，prefix_replay保存来源/原成本；首错机制保持。该控制不调用A5复判，不恢复已决定放弃的A5候选。

强旧系统控制按核心计划继续CPU准备，固定可见能力顺序为原R1诊断/规则谓词→完整给定模型A4→采用F适用格式→原R1透传，身份`adopted_R1_R4_F_capability_composite_v1`。策略在当前F开发评分前保存，两个骨干均固定17输入选择原R1、104输入选择F，当前开发输入无A4能力；不是新MoA路由、oracle或互补矩阵。三项控制测试覆盖原谓词、模型完整性、停止批次/错误身份不得装配。manifest与源码在`a5_f_preparation/strong_legacy_preparation/`；尚未装配/评分，必须等完整F及回放通过。


同工具r2两骨干各7/7真实输出均通过，60个逻辑回调（33新调用＋27个原有效前缀）逐请求/原parser/原工具重算回放完全一致，规则facts键序漂移已消除；不把原M4失败或M5原回放差异改写成未发生。新增成本33调用、612509输入/5240输出token、生成墙钟之和271.128秒。各6条开发smoke与1条给定模型fixture只做无生成范围导出，完整7题父批次保留；27个继承回调中26个属于开发、1个属于单独fixture，原真实成本/来源均单列。随后在GPU1/3按相同源码、prompt/参数/预算/首错机制扩展各剩余115开发输入，原6题复用一次，仍121完整分母，fixture不混入v5。启动清单`single_agent_preparation/stable_tool_json_r2/development/extension_manifest.json`。


同工具r2 M4正式开发扩展在d00012的code_view_2输出2048 token、finish_reason=length时首错停止；当时submitted/completed=40、in_flight=0。扩展115题中7完整、1失败、107未提交；加原6条开发smoke后完整计划121为13完整、1失败、107未提交，不删除失败/未提交项、不算主分数。失败输出9761字符且结构空白仅1字符，发生在视图原生生成，不是刚修复的工具参数空白问题；不通过再改温度、预算或重抽掩盖。新扩展实际408241输入/7839输出token、237.456秒，所有8份保存提议（含失败）和40回调经冻结r2入口精确回放；记录`development/m4_stopped_acceptance.json`与`m4/failure_diagnosis.json`。统一inference_started=true、failure_type=output_truncation、semantic_result=unavailable、method_score=not_scored，原始错误记录不覆写。M5相同固定控制继续，未受此骨干停止牵连。


<a id="f-complete-development-20260922"></a>

### 旧F完整开发与固定强旧组合对照

两骨干各117条F扩展与原4条smoke按完全相同输入/配置/源码无重复装配为121输入。M4 363、M5 362实际请求均核对到EngineCore的采样参数和接受记录，242个完整提议（含不适用）及725个回调经原冻结F入口、原parser精确回放。离线装配、回放、评分不新增模型调用；不对历史文本作重采样匹配。F仍保留`legacy_f_equal_nli_paths_else_full_maj5`，没有改名为新受控视图A5成功。

| 当前开发指标 | M4 | M5 |
|---|---:|---:|
| F适用并有完整原生答案 / 全部输入 | 104/121 | 104/121 |
| F不适用（保留完整分母） | 17 | 17 |
| F完整分母原生成功率（74非reference unit） | 0.567568 | 0.509009 |
| F实际错误答案（唯一输入） | 28 | 34 |
| 固定强旧组合完整分母原生成功率 | 0.702703 | 0.644144 |
| 强旧组合实际错误答案（唯一输入） | 34 | 39 |
| 原R1分派控制完整分母成功率 | 0.700000 | 0.666667 |
| F及强旧组合保持对双正确 | 48/73 | 44/73 |
| 强旧组合应变对双正确 | 1/4 | 1/4 |

这些是相同40已暴露家族、121输入、157原生映射的开发结果，74是原评分unit、不是独立患者数。F的17个unsupported为不可用/不评分，仍进入完整成功率分母；本轮4个应变对均落在F不支持的多选范围，因此F单独为0/4、8个端点不可评分，不能据此声称F错误地强制保持。强旧组合对这些端点使用原R1/A2，4对应变均可评分。保持对25家族聚类95%区间M4[0.442542,0.844183]、M5[0.410912,0.796627]；应变只有4家族，区间[0,0.75]且证据很弱。没有把R标签用于选择组件，也没有运行五专家oracle或互补矩阵。

强旧组合是本次在F评分前声明的固定组件控制：每骨干17输入使用已核验的原R1规则/目录输出，104输入使用本次已保存F；本范围没有完整给定模型，A4分支未激活，不补写原HIV或一般临床能力。组合的F属于本次新推理，R1/A2/A3部分为已保存输出复用，组装本身0新调用，不能全称为旧历史预测。M5组合低于仅R1控制2.252百分点，M4仅高0.270点；两个对照同时保留，不按骨干挑最好结果再称同一统一改善，更不把它算作MoA收益。

原F包含预先固定最多五票/三票早停和无效票处理。逐生成附加审计发现M4两次、M5一次JSON截断票（合3/685个带JSON合同的生成；另8个原有自由分析、32次一token评分）。其invalid_reasons、原raw、seed、所有实际token与最终选票都保留；这是原F已定义的有界内部处理，未改成错误后反复重抽，也未删题。最终原生结果的非预期schema/runtime错误为0，不能把这个0解释为内部所有生成都完美。对应证据`f_complete/{m}_constituent_audit.json`，原F源码aggregate/optimize保持。

真实F成本：M4 363调用、1680221输入/82816输出token、1823.843秒；M5 362调用、1606897/82405、2250.760秒。合725调用、3287118输入/165221输出token、4074.603秒生成墙钟之和；包含原smoke各一次，不含共同历史RAG/初答成本，不把共享GPU墙钟当独占速度。强旧组合选中资源另含原R1的114次已发生事实/目录回调，合839次资源调用、3569940输入/168420输出token；这114次不重复计为本轮新推理。逐题源指针与原成本在`strong_legacy_complete/`，两模型完整回放/评分/阶段报告和合并收据在`f_complete/`，总入口`combined_stage_report.json`。独立评测尚未开启。

<a id="same-tools-stopped-20260922"></a>

### 同工具控制双骨干停止、失败分母与离线准备

M5同工具r2于18:35在d00073的第二代码视图触发首个原生schema错误，runner自动停止新提交；当时submitted/completed=319、in_flight=0，最后实际调用正是失败调用，后47条扩展输入均未发送。原115条扩展为67完整、1失败、47未提交，加6条已验收开发smoke后完整121分母为73/1/47。失败输出2048 token、6480字符，其中字符串外空白5628字符、最长连续5620；最后完整字段是answer_choice，之前step_by_step_thinking字符串806字符已闭合，但必填errors尚未开始，因此不属于全部语义内容齐全、仅缺JSON闭合。故障位于原生code_view_2生成，工具参数空白修订不覆盖此请求；不扩大该修订、不增预算、不再次抽样。

M5全部68份已保存扩展提议（含失败）及319实际回调经冻结r2正式入口和原parser回放完全一致，2.337秒CPU、0新增模型调用。原记录不覆写，另附诊断统一标记inference_started=true、failure_type=output_truncation、semantic_result=unavailable、method_score=not_scored；它不是答案错误。证据在`single_agent_preparation/stable_tool_json_r2/development/m5_stopped_acceptance.json`及`m5/failure_diagnosis.json`。本次扩展成本4152793输入/45480输出token、1352.927秒；M4此前40调用及13/1/107全分母状态继续保留。

两骨干均不装配为“完整成功批次”，不只对完成子集计算主结果。逐题完整计划索引为`development/{m}_full_scope_status.jsonl`，记录已完成、失败、未提交与原trace来源；汇总`development/stopped_stage_report.json`。同工具控制全部历史真实实验成本为424新调用、5771942输入/64319输出token、2064.170秒生成墙钟之和，包含原smoke失败/回放差异、r2新请求、两个停止扩展及独立生理fixture；27个已发生有效前缀不重复记新调用，fixture不进入v5分母。此成本不能当作一个完整121题控制的平均性能或等成本比较。本任务模型进程均已退出，健康的其他任务保持。

A2/A3/A4已有各121输出仅做独立离线原生评分，新增模型0、未重跑专家，收据在`expert_development/{m}/{A2,A3,A4}_scores/`。A2每骨干9原生可用、112不适用，实际错误答案1；A3每骨干8可用、113不适用，实际错误M4/M5为5/4。A4当前121输入均无完整给定模型，全部unsupported、实际错误答案0，不能解读为通用临床零准确率，也不拿单独生理验收填入当前分母。所有不适用项保留，原生评分只在隔离离线进程读取评测账本。

互补分析仍服从用户此前独立暂停，已提出仅解除离线分析的异步问题，尚无答复；等待不视为批准。固定准备清单`complementarity_preparation/plan.json`锁定每骨干A1 r5、A2、A3、A4、真实F的完整121输入及结果哈希、原R1和固定强旧组合对照。A1保持未采用候选，A5失败批次独立保留，稳健列不改名为新A5；计划分别报告覆盖、可用性、重叠范围修复/误伤、不可用恢复、离线oracle上界与真实成本。当前数据尚未计算矩阵、未调用Router/聚合、未接触独立D。

离线分析代码补齐缓存实际资源记账和不可用恢复计数：组装0新生成不等于原专家0资源，优先读取前缀复用的逻辑实际成本或旧head来源成本；缺失用量不填0。6项成本/评测隔离fixture测试通过，日志`a5_f_preparation/cached_cost_unit.log`。单元fixture不是当前数据的互补实验，也不是新方法采用依据。

阶段收尾核验：193份采用源、154份受保护历史输出/A4验收制品、3份原生评分源均与既有SHA-256一致；核心计划与用户最新附件逐字相同。实际F源码快照72文件、同工具r2快照74文件也与各自运行锁一致。证据`a5_f_preparation/f_complete/final_preservation.json`、`frozen_source_final_check.json`。本次只更新原型状态清单、运行导航和主记录，未改冻结运行配置；变更前状态元数据保留`status_metadata_before_closeout.json`。交接`a1_v2_relational_20260922/checkpoint.json`及`f_complete/closeout_status.json`明确active_sessions为空，不把已经退出的GPU队列继续报告为运行中。

<a id="complementarity-input-audit-20260922"></a>

### 互补分析的输入审计与缺失成本修复（仅CPU准备）

上一目标轮已完成F/控制收尾与保留校验，属于实质进展。本轮未把自动目标续行视为解除用户暂停，仅推进已授权的无模型代码、单元测试及数据审计。新增`evaluation/complementarity_data.py`，按两骨干分别核验原计划指定的五角色与两个旧控制：源码/输出哈希、原生评分源、专家和variant真实身份、每条合法输入哈希、全计划分母、原生多映射与唯一输入记录的一致性、unavailable和错误答案的区分、原始成本复制。停止批次、删失项、重复项、不同骨干/输入混入及将F改名为A5均不能通过。该入口不加载模型后端，不重算分数、不读隐藏配对端，不生成路由或互补矩阵。

真实数据审计前的合成反例发现：`head_resources({'new_model_requests': 1})`原先把缺失token填为0且complete=true；已有一新一缓存调用但缺少缓存token时也会低报。修复后缺失用量为null/incomplete，仅对应调用数能证明为零时才使用零；保留missing_usage/unresolved标记，不修改原始成本。原错误行为保存在`complementarity_preparation/validation/start.json`，修复前源码、diff和最终源锁在同目录。另在矩阵计算函数增加骨干分离检查，当前仅以fixture验证。

首轮19项单元测试通过，实际审计随后遇到新审计器自身的KeyError：原R1缓存复用状态使用inputs字段，普通runner使用complete。原R1记录本身完整且未损坏；保留`data_audit.log`、`data_audit_initial.py`及失败说明后，使核验器识别两种既有计数字段并逐一核对完整分母，未改旧制品、未放宽停止检查。增加针对原收据字段及错误计数的回归后20项测试通过（0.093秒）。日志`unit_after_receipt_fix.log`；这是数据核验代码修复，不是方法版本或生成参数调整。

最终`validation/data_audit.json`核验M4/M5各7份完整已保存结果，每份121输入/157原生映射，合14份/1694输入记录；A1 r5保持未采用候选、真实F保持旧稳健组件、两个旧控制各自独立。所有保存成本可追溯，修复前后读取这1694条真实成本的结果完全相同，证据`cost_reader_regression.json`。只做既有记录一致性检查，不能据此主张专家互补、在线增益或独立泛化。原`complementarity_preparation/plan.json`未改，matrix_computed=false，0新增模型调用，原暂停仍有效。

<a id="a2-control-preparation-20260922"></a>

### A2同事实机制对照准备：采用核保持，模型执行尚未开始

本轮继续核心计划6.3允许的代码、单元测试与数据审计，不将自动目标续行视为解除矩阵暂停。A5负结果和真实旧F身份保持。新增对照实现（本地制品：`/home/data3/txy/cf_moa/controller/a2_controls.py`）、无模型准备入口（本地制品：`/home/data3/txy/cf_moa/evaluation/prepare_a2_controls.py`）及固定配置（本地制品：`/home/data3/txy/cf_moa/configs/a2_controls.json`）；不修改A2采用源、不重跑事实提取，也不从离线gold选择政策。本次没有GPU模型作业，模型执行控制尚无真实响应或质量结果。

同覆盖范围按原A2可见能力判断，两骨干各121计划输入、9适用、112不适用；逐题范围及输入哈希全部保留。对照分别为同覆盖常数None、遇当前明确失效路径即删除但不检查其他剩余支持的消融、汇总全部剩余路径后只删不新增的更强控制，以及原完整支持重算。前一种删除消融不声称该路径曾支持初答，也不推断隐藏配对端发生了什么；后者用于避免仅靠较弱删除政策论证重算。两删除控制都保留原UNKNOWN继承和非法初答，不将未提及改为否定。d00050两骨干原初答均不符合原选项集合合同，原A2因此未应用；本轮保持其原生输出及原因，不通过修复初答抬分。尚未对新控制评分；后续必须分开报告撤销侧与仍有有效支持侧，不能只报多数总分。

模型执行对照锁定09-14实际充分推理控制的完整配置，来源为`r2_samefacts_reasoning_{llama,qwen}/config.json`，原指令及最终JSON读取来自`r2_samefacts_control.py`、`r2_samefacts_reasoning.py`和实际`analyze_v5.py:objects`。只抽取相应函数，不导入旧driver的顶层评分/数据载入逻辑。两骨干原seed42、temperature0、max_tokens8192、guided_json=false各自保持，M5保留原thinking与YaRN、M4保留其原模型设置。8192是独立历史强执行控制的既有上限，不是增加A1/A5或已停止同工具臂的预算；这个额外执行臂成本不对称，不能声称已完成同实际预算控制。准备时使用同一当前输入的已清洗事实与问句范围规则，固定事实键序；模型请求不含原程序答案、支持状态、gold、R标签或另一病例。沿用旧控制最终JSON要求，原无grammar配置不能描述为xgrammar成功生成。

首轮17测试通过，真实缓存准备随后发现新增核验器对完整trace的字典比较失败。诊断确认采用的`r2_indexed_head.clean_facts`遍历required_fields集合，使`evidence_errors`列表顺序随进程变化；原生答案和其他trace内容未改变。保留首轮错误、日志和代码，仅在比较时对这一诊断列表按完整内容排序，保留重复次数；缺项、内容变化、支持路径或答案变化仍拒绝，不重写旧trace或修改执行核。新增回归后18项测试通过（0.077秒）。另在PYTHONHASHSEED=0/1两个CPU进程对全部18条缓存各回放一次：M5 d00095，及另一进程的d00018出现诊断排列差异，原生答案与其他字段全部一致；这是进程哈希诊断，不更改模型seed或重采样。

最终准备保存242条全范围CPU控制记录、18条模型执行请求及其逻辑/物理参数、当前输入哈希绑定事实文件和来源。M4/M5最大执行输入分别1862/1864 token；每骨干固定首个适用d00000为未来smoke，其余8条为验收后的扩展清单，尚未发送。原9次事实提取资源分别5206输入/1531输出token与5054/1572；本次全部复用、新模型调用0。常数控制本身不需要事实调用；删除/重算各计原事实成本，模型执行另计将来的真实请求，不把复用写成原资源零成本。没有计算矩阵、没有开启独立评测。

证据：准备收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/prepared/receipt.json`）、失败与修复索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/README.md`）、源码/配置manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/manifest.json`）。本轮检查历史位置清单中60文件、154份既有输出/A4验收、3份评分源以及A2准备锁中的9文件均未变；核心计划仍与附件同哈希。这里的60是本轮具体清单范围，不把早前193文件核验冒称本次重新检查。后续待实现控制的实际首错停止入口、两骨干真实smoke/请求验收与分成本评分；当前CPU请求准备不能替代这些验收。


### A2独立模型执行控制：首错停止入口完成，启动固定smoke

上一轮为实质进展。本轮补齐`evaluation/a2_control_runner.py`：复用既有RunJournal和串行首错停止，按当前输入哈希加载单份已保存事实，校验请求与准备记录完全相同；旧facts、控制模型新增请求、未决传输分别记成本，缓存事实也占共同预算。不适用输入不加载事实或模型。截断/格式失败保存原文本、inference_started、unavailable/not_scored并阻止后续输入；重启同一stopped identity不会重采样。固定smoke为每骨干d00000一题，扩展为其余120输入（8适用＋112不适用）；扩展前核验实际EngineCore接收参数、prompt token和同响应原parser/组装器回放。

34项相关单元测试通过（0.518秒），覆盖确定的早期截断、JSON失败、未决传输、已完成/未提交分母、缓存预算、非法cache、请求漂移和跨阶段身份/成本。两骨干CLI各9条真实模板/tokenizer/sampling请求准备与先前18条记录一致；这些CPU检查明确actual_model_preflight_passed=false，不冒称真实推理。原充分推理配置没有固定KV override，新增资源估计兼容自动KV，未添加override或改采用参数；其他固定KV配置的回归通过。

现按原计划6.3及用户对常规推进的授权，启动单独的同事实模型执行控制；不是重新运行原A2专家，也不恢复A1/A5/矩阵/Router或独立评测。固定历史8192配置、事实/规则与smoke顺序不变，先两骨干各1请求，实际请求和回放验收成功后才推进其余8个适用输入。GPU0/3启动前估计满足采用资源，其他健康进程不动。源码、配置、CPU验收和分配在`a2_control_preparation/live/frozen_manifest.json`；这是本控制运行快照，不是系统最终冻结。实际状态和成本待模型返回后补记。


用户误停对话后明确要求继续。恢复时直接核验原session 74842/96814及GPU进程、SQLite journal，两个任务均未被误停终止；M4随后原进程退出0、smoke及实际请求/原parser回放验收通过，M5原进程仍在生成。没有启动替代进程或重复请求。观测存`a2_control_preparation/live/interruption_resume_observation.json`；后续按原固定阶段继续，矩阵原暂停未解除。


<a id="a2-control-parser-difference-20260922"></a>

### A2严格包装v1与历史原生parser差异：保留失败，扩展暂停

两条smoke均实际进入模型且正常返回。M4/GPU0为844输入/844输出token、16.6048秒模型墙钟，正常stop；原生状态到答案及EngineCore实际请求验收通过、退出0。M5/GPU3为830输入/5415输出token、74.3270秒，正常stop并已闭合`</think>`，不是8192上限截断。M5完整最终JSON多出`A:UNKNOWN`，请求执行候选仅B/C/D/E；A是原生None选项。当前严格包装因此返回unavailable，first_error为OutputSchemaError，1提交/1完成/0在飞，原记录status=invalid_output、failure_type=output_schema、inference_started=true、method_score=not_scored，退出1。未扩展、未丢弃失败或重复生成。

进一步用实际历史`r2_samefacts_reasoning.py:parse_states`和`analyze_v5.py:objects`的原函数定义、同一缓存响应以及采用`r2_program_head.assemble`独立核对，M4历史/新包装同为[B,E]；M5历史parser接受含A的map，原组装器只遍历实际候选、忽略额外键并得[B,E]，新包装则返回null。此差异由本轮新增的`jsonschema.validate`严格检查引入，先前称“原parser验收”不够准确：实际是原读取函数之后又加了更强有限键约束。配置中的“仅调整范围/匹配/序列化”描述遗漏这一变化。不能把它写成旧强控制自身必然无效，也不能以失败的较弱适配证明A2方法优势。

已保留严格包装v1的源码快照、原请求、原响应、失败计数和完整121输入状态。两骨干smoke以外各120输入均未发送；M4的成功不能拼成完整主结果。2次实际新增合计1674输入/6259输出token、90.9318秒模型墙钟；两份缓存事实另计2个历史请求、1104输入/318输出token，未记为新调用。所有受测模型进程已退出。完整诊断见`a2_control_preparation/live/parser_parity_diagnosis.json`及脚本，阶段收据见`live/stage_report.json`，源快照108文件与运行manifest一致。诊断未读gold、未评分，也没有把历史parser诊断输出替换当前失败。

按用户要求，在发现与复用历史原生行为约定不一致后，暂停后续批次并提出具体处理选择：保留严格版失败，以独立修订恢复历史parser原生行为，先仅回放这两条真实响应、验收后继续固定扩展；或保留当前判定并停止这个控制。当前等待明确答复，不把继续原目标或等待时间当作放宽合同的批准。此期间仅补验收失败记账的独立回归与离线报告代码；不改prompt、seed、temperature或输出预算。另发现潜在记账缺口：smoke推理已写complete后若验收抛错，原入口只进程退出、没有更新失败状态；本次M4未触发该缺口。以下修复仅进入工作树，实际运行快照与旧结果保持。

验收停止机制修复完成：真实验收入口抛错后保存`acceptance_failed.json`、首错请求及提交/完成/在飞计数，状态为`stopped_on_error`，基础设施/验收失败单列；已完成响应与成本保留。扩展必须同时持有未变的通过收据和再次验收，离线组装也检查同政策、完整阶段及四份来源哈希。17项相关测试通过；另用纯文件核验器检查实际保存的M4通过、M5停止，前者接受、后者拒绝，没有模型回放或改判。证据：修复与diff（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/runner_validation/acceptance_fix/receipt.json`）、实际保存阶段检查（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/runner_validation/acceptance_fix/saved_smoke_gate_audit.json`）。

离线A2机制对照报告器（本地制品：`/home/data3/txy/cf_moa/evaluation/a2_control_report.py`）完成代码准备：四个预先固定CPU政策保留全部121输入与112不适用，区分原生映射、唯一输入、非reference单位和来源家族；分报原R2与同覆盖范围、原生None/仍有实质答案两侧、修复/误伤/不可用及复用事实成本。侧别仅为评分侧标签，不能冒称因果撤销验证，也不进入推理。可选模型控制须完整121输入、9次实际请求及同响应原生回放验收，并绑定原阶段、组装输出和smoke收据；仅smoke、停止批次、成功子集或缺少验收均拒绝。当前数据尚未评分，未生成互补矩阵。10项报告fixture与13项既有组装/评分/成本测试通过；初次fixture缺少空proposals文件的测试失败保留，不混作实际实验失败。报告代码与命令记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/report_preparation/README.md`）。

上述两项合并后，A2控制、runner、组装、首错停止、CPU准备、报告、缓存成本和评测边界共55项回归通过（0.967秒）：合并测试日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/runner_validation/integrated/unit.log`）。本次收尾0新模型调用、0当前数据质量评分；历史parser修订仍待用户决定，未更改严格v1失败或冻结快照。A2/A3原输出、A4验收和旧F结果继续有效，矩阵、Router和独立评测仍未开启。

进一步只读复审发现，初版报告器给CPU决策文件现场计算哈希，且只核对完整重算与原A2；这不足以发现另外三臂被改写的答案或成本。报告尚未在当前数据执行，因此没有受影响的实际分数。保留该缺口记录及初版测试/源码，新增评分前的无gold确定性政策回放：核验原准备快照的`choose` AST与配置，从哈希绑定的原A2选项支持trace、当前合法输入重算四政策，逐字段比较决策、状态、适用性、成本与来源。没有事后补造历史输出锁，没有修改旧准备制品。修复diff与收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/report_preparation/policy_replay_fix/README.md`）。

修复后的27项局部测试、最终59项合并回归均通过（合并1.712秒）。真实已保存数据的独立纯核验覆盖两骨干各121条、合242条完整记录；18个适用输入×4政策共72个有效决策全部一致，224个不适用输入的状态/空答案/零成本也保留。核验进程显式阻止打开offline评测文件，未导入模型后端或推理runner，0生成、0评分、未计算矩阵。无gold核验收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/runner_validation/integrated/saved_cpu_policy_audit.json`）、最终测试日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/runner_validation/integrated/unit_after_policy_audit.log`）。实际严格v1快照108文件以及工作树parser/原配置未变；已保存M5失败仍不可评分，未被回放诊断答案替换。

<a id="a2-fixed-cpu-controls-20260922"></a>

### A2四项固定CPU机制对照：当前开发范围离线评分

上一目标轮完成了停止机制、报告保真门禁和实际242条无gold核验，属于实质进展。本轮依核心计划6.3继续不受模型parser偏差影响的固定机制对照，使用原A2已保存事实、四个此前声明的政策及原生评分，全部121输入/骨干纳入。只在单独评分进程读取已暴露开发gold/R分层；不运行模型、不重跑A2/A3/A4、不更改政策、输入或输出，不恢复矩阵或独立评测。A2模型控制仍待用户决定，不能把其未完成结果混入本次四臂。源与启动收据、逐题包装及评分将写入`a2_control_preparation/offline_controls/`；此处先记启动，结果待实际命令完成后补齐。

两骨干评分命令均退出0。每个政策均保存121唯一输入、157原生映射，含69参考映射与88非参考映射；非参考按原协议对应74等权unit，完整范围40来源家族。适用范围固定9输入/9家族，其余112为unsupported而非错误答案；不按分数删除或替代。完整重算本次314条原生评分与此前A2评分逐字段一致（仅方法身份字段不同），两骨干unit汇总也完全一致；独立只读复核及26个来源哈希/骨干均通过。

| 固定政策 | M4适用范围正确数 | M5适用范围正确数 | 原生None侧（两骨干均2题） | 仍有实质答案侧（各7题，M4/M5） |
|---|---:|---:|---:|---:|
| 原A2完整支持重算 | 8/9 | 8/9 | 1/2 | 7/7、7/7 |
| 同覆盖常数None | 2/9 | 2/9 | 2/2 | 0/7、0/7 |
| 遇失效路径即删除，不重算剩余路径 | 3/9 | 2/9 | 1/2 | 2/7、1/7 |
| 完整路径重算后只删不新增 | 4/9 | 2/9 | 1/2 | 3/7、1/7 |

原R2非reference范围必须另报：共7输入，None侧2、实质答案侧3、不支持且无法按multi答案分类2。四臂完整7输入的正确数M4为4/2/1/2，M5为4/2/1/1，顺序同上；两条unsupported保留，不能仅报覆盖内5条。完整重算的原R2实质答案侧为3/3，None侧仍1/2。该分层是离线原生答案侧，不是从隐藏配对端推出支持被撤销的因果证明。

逐题机制核读：完整重算相对初答修复M4四题、M5六题，均无已正确答案误伤；修复全部来自有效支持侧的补选/重判。更强的“重算后只删”在这9题上未改变任何初答，因此完整重算对它的优势主要反映允许补全完整答案，不能归因于纯撤销操作。较弱删除臂在M4四题删除6个选项、M5两题删除3个选项，这些选项在当前trace中均仍有1–2条MET路径；M4 d00103因此由正确变错，M5受删两题本已错误。这里没有推断失效路径曾是初答真实使用的依据。d00050两骨干原初答无效继续保留：M4混选None与实质项，M5输出文本而非原生key，完整重算及删除臂都没有修复；常数None在该题正确，不隐去这项反例。

成本：本次离线评分/分析0新模型请求。三项依赖事实的政策各归属同一组9个历史事实请求，M4 5206输入/1531输出token、24.8084秒原记录模型墙钟；M5 5054/1572、34.1438秒。常数None不使用事实请求。三臂共享事实不能相加声称54次新生成；两骨干实际复用来源合18个旧请求，新的模型执行对照2次smoke成本另存，不计入这些CPU臂。共有8份固定政策逐题包装/评分，附当前初答评分；原A2预测和旧评分文件不变。

补充事后描述性不确定性分析，使用来源家族cluster bootstrap、seed42、10000次、95%百分位区间，参数不是经结果搜索选择，也不宣称为预注册确认检验。两骨干完整重算适用范围8/9的区间均[66.7%,100%]；原R2完整7输入4/7的区间均[14.3%,85.7%]。对常数None的原R2差值区间均[−28.6,71.4]百分点，显示该子组证据不足以确认稳定优势。所有臂与配对差值区间、18条机制trace和复核脚本均保存；小样本、共享规则来源及已暴露开发身份仍限制泛化。结论仅支持保留原A2完整支持政策，不采用常数/删除控制替代它；尚不能证明新MoA、纯支持撤销机制或相近资源模型执行器优势。

证据：M4四臂报告（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/offline_controls/m4/report.json`）、M5四臂报告（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/offline_controls/m5/report.json`）、逐题机制trace（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/offline_controls/mechanism_trace.jsonl`）、原结果一致性与区间（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a2_control_preparation/offline_controls/analysis.json`）。A2模型控制的严格parser偏差仍待用户处理选择；矩阵、Router、独立评测均未开启，本轮不调用GPU。

<a id="a3-edit-readiness-20260922"></a>

### 默认关闭A3编辑臂的无模型准备核查

上一目标轮完成四项固定CPU机制对照、原评分一致性核验及成本/小样本分析，属于实质进展。本轮转向核心计划7.2/7.4尚未完成的独立A3编辑臂：先核查当前可见句段、固定候选及代码映射、精确补丁范围、错误状态与后续请求grammar，保持默认关闭。此前记录已指出其`maxItems`尚未适配当前xgrammar，初始三项fixture不能证明真实多阶段入口可运行。先保存源码并以已保存A3分数仅回放目录前缀、截获后续编辑请求做CPU检查；不生成新编辑、不给当前样本质量评分、不改变采用A3或其历史输出。证据目录为`a3_edit_preparation/`，A2模型parser决定与矩阵暂停继续保持。

审查已确认四处不符合计划的准备缺陷，保持A3编辑臂关闭并向用户提交限定修复选择，尚未改变实现、prompt/schema或采样设置：

1. 合成editor响应`{`被捕获后作为partial并保留旧native答案，`output_flags`的schema/semantic标志均False；实际A3入口与标志函数已复现，意味着runner看不到这个schema错误。这里没有把七个fixture回调声称为真实模型调用，也未声称运行了完整journal停止测试。
2. `apply_edit`用全局字符串替换改写每条消息；另一消息引用完全相同题面时也被修改。实际合成例可同时改动system中的文档引用和user当前题面，但trace仍写prefix/suffix unchanged，不能证明未授权消息未改。
3. `Give the most likely diagnosis.`等无问号祈使式目标指令可被识别为证据并删除。已有黑名单与含问号过滤不足以证明目标问题不变。
4. 从真实A3构造路径得到的`edits.maxItems=2`经当前guidance与实际vLLM0.8.5/xgrammar0.1.18 validator仍报不支持。只截获目录评分首请求的旧预检没有覆盖后续editor请求。

前三项为纯合成边界复现，第四项还通过实际安装校验器检查；复现脚本、45项来源哈希与结构化证据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/findings.json`）均已保存。属于未启动实验臂的实现准备失败，不新增为模型答案错误或质量负结果；此前A3采用输出继续有效。

另对当前真实合法输入逐条审计：两骨干各121输入，其中8适用、113不适用；用原缓存精确核对并回放各48个目录评分回调，共96个，所有原逻辑请求与已保存raw scores一致。每个适用输入从实际A3路径截获下一editor请求，共16条，均未提交；固定seed42、temperature0.7、max_tokens1024保持。原题含578–1340字符、17–41个当前可编辑片段。当前每题在原消息中只完整出现一次，每骨干241个片段的删除检查未发现修改其他消息；此范围结果不否定多副本合成用例的缺陷，也不能证明目标指令分割在其他题型安全。未读offline gold/R/配对数据，未导入模型后端，0质量评分：实际输入与缓存前缀核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/input_audit_receipt.json`）。

进一步分别用M4/M5真实readout配置和tokenizer，对截获的d00008请求调用实际`NativeBackend.prepare/preflight`：2384/2183输入token，均在grammar门报`SchemaCompatibilityError`，模型未加载且physical_calls=0。此CPU失败不是一次进入模型的smoke，不能满足真实模型preflight验收；两骨干物理请求与预检记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/captured_editor_preflight.json`）。本次0新模型调用；所回放旧目录96请求仅作来源成本参考，M4原142632输入/48输出token、5.9661秒，M5原129930/48、6.5016秒，不能重复计为新消耗。

提交的修复范围是：将题面副本与可编辑证据位置明确绑定、保护目标指令且验证完整消息差异；保持0–2独立探针的原schema语义，仅做xgrammar等价转换；让结构失败进入首错停止与失败分母，同时保留合法空探针列表及真实语义拒绝的独立身份。旧目录、原初答、候选/代码映射、温度、seed及1024/2048预算均保持；先做无模型边界、grammar、完整停止机制回归和缓存回放，再提交真实smoke及匹配控制的固定方案。当前等待用户对这次计划偏差的处理选择，不因自动目标续行启动编辑臂，也不修补旧A3结果。

运行交接：A2原生parser处理与互补矩阵解除暂停的同一待答条件已持续三个目标轮；期间分别完成停止/报告修复、CPU机制评分、本次A3准备诊断，均记为实质进展，未冒称等待GPU作业。现`pgrep cf_moa.evaluation`确认没有本任务运行进程，这轮可独立诊断已完成；余下受影响实验及矩阵/路由顺序需要用户处理选择，不能用反复轮询或额外文档冒充继续实验。自动目标已标记`blocked`，不是完成，也未中止其他健康作业。待答项包括A2历史parser恢复、A3限定准备修复，以及仍明确暂停的矩阵阶段；目前没有发布、冻结后评估或新MoA采用结论。


<a id="a3-edit-repair-20260922"></a>

### A3编辑臂限定修复：用户授权与启动

用户明确选择“按上述范围修复，A3 编辑臂暂不运行模型（建议）”。本次恢复四项代码修复与CPU验收：当前题面出现位置绑定、目标指令保护、原0–2探针schema的等价xgrammar转换、结构失败传播至首错停止。原采用目录头、prompt、逻辑schema、模型、seed42、temperature0.7和editor1024/final2048上限保持；合法空探针及语义拒绝分别记录。修复前源码和既有缺陷诊断保持，新增证据存入`a3_edit_preparation/repair/`。本轮不执行编辑臂真实smoke/批量推理，不恢复A2 parser扩展、矩阵、Router或独立评测；CPU通过也不等于真实模型验收或方法采用。


#### 限定修复完成与验收

四项修复均完成。题面只绑定唯一当前user消息中的精确出现位置；字符串合同只接受唯一出现，其他角色的同文引用不改，多副本不猜测。局部补丁后由原始packet快照独立构建预期结果，检查绑定消息之外的所有内容、题面外的前后文、其他native字段及整包差异。证据资格使用有限英文临床陈述/字段/属性形式，保护Give/Identify等无问号目标和混合任务句。它不是通用指令理解，也不证明反事实临床可实现性。

无模型预审发现第一版正向资格过窄：每骨干241→182，会误排除部分原临床复合句/属性。修复这些识别遗漏后，最终241→206；仅移除35个text/分隔符/Symptoms/Antecedents布局与章节头，原临床证据全部保留，既有Q:N、文字及offset不变。中间观察按当时来源保存，未补造该中间版完整源码快照，见`repair/boundaries/intermediate_qualification_review.json`。最终412次合法局部删除均通过完整packet差异核验。

原editor逻辑schema保持原字段、必填、枚举、额外字段禁止及0–2条探针；兼容层只改当前xgrammar转换器的一行数组续项递归，其余JSON字符串、空白规则保持。精确注册只作用于此原合同，schema或安装转换器布局变化会拒绝未经核验的重写。原16捕获schema通过288个compiler/matcher与原parser边界对照；不增加预算、不增加空白限制或调整采样。允许span列表及对应enum因上述边界修复发生变化，与grammar兼容改动分开归因。

editor或最终原生JSON解析失败、或生成结束原因为length时，新编辑臂返回保留原文/旧目录来源/探针/成本的不可评分提议，并传入真实runner的schema首错停止，不再悄悄返回旧答案冒充成功。失败标记inference_started=true、semantic_result=unavailable、method_score=not_scored；output_schema与output_truncation分开标明。合法空列表仍保留原目录结果，非法局部编辑独立计semantic_invalid；删除不等于否定，不强迫保持或翻转。

实际RunJournal合成回归覆盖先完成一题后editor失败，以及合法probe后final失败：分别14/9个fixture回调后停止，未提交项保持，全分母、已完成原文、成本和first_error(request_id/ordinal/category/submitted/completed/in_flight)均保存。恢复同一stopped journal不能重采样，主评分入口拒绝停止批次。合成回调不算GPU调用或临床预测。与A2控制、A4采用配置、合同及旧停止测试合并，共79项通过（12.592秒），日志`repair/combined_unit.log`。

两骨干各121条默认A3提议与旧保存结果除运行成本外逐字段相同，resources/applicable/run函数AST保持；96个唯一旧目录请求分别经默认入口和可选编辑前缀执行，共192次缓存回放，旧成本不重复计为新消耗。16条修复后editor请求经过真实两骨干readout配置、tokenizer、prepare/preflight及grammar编译，全部CPU通过。原请求另作同样检查，原d00008物理差异仅JSON guidance→grammar；修复后16条的其他变化仅来自允许span列表/枚举及相应prompt/grammar，完整模型、采样、原context、固定pair和指令文字均保持。d00008因去布局，M4/M5输入从2384/2183变2229/2013 token；这不是删原题或改变输出上限。全部预检禁止model start/generate，不能称请求已进入模型计算；尚无真实editor/final响应验收。

最终193份历史采用源、154份原结果与A4验收制品、3份原生评分源哈希保持。原缺陷记录保留；修复采用精确源码快照/SHA-256，没有虚构Git提交。本次0新模型调用、0新输入/输出token、0模型加载；CPU耗时分别保存在测试、回放和预检收据。源码/prompt/schema AST、每骨干采用采样与原生评分保持的证据见总验收收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/repair/receipt.json`）、完整diff（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/repair/source_diff.patch`）和运行索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/repair/README.md`）。

本次只采用实现修复，不采用A3编辑机制的质量结论；variant保持原真实身份，另加implementation revision。编辑臂仍默认关闭且真实模型暂停。固定首个适用d00008的双骨干smoke及§7.4必要匹配控制已存为后续计划，尚未执行，控制操作也未在本次实现/冻结；不将随机编辑自动叫无关编辑、不把同上限叫同实际成本。A2 parser处置仍待答；互补矩阵、Router、聚合和独立评测没有解除暂停。


<a id="a3-fixed-control-preparation-20260922"></a>

### A3 §7.4固定对照的无模型准备

上一轮四项限定修复和验收为实质进展；本轮继续用户允许的无模型代码/单元测试/数据审计，不将自动续行视为解除任何模型或矩阵暂停。准备单次原目录、同六排列未校正多数票与原校正三种明确身份的缓存对照，以及仅依赖当前合法题面的固定seed随机局部编辑请求。使用已有完整score/原生输出核对，不加载offline gold、不计算新质量分数；随机编辑不自动称“无关”，额外重评分和最终原题重答仍待真实调用许可及完整匹配控制。证据放`a3_edit_preparation/controls/`，保持刚完成的A3修复源码及旧默认输出。

配置复核再次确认旧A3缓存属于catalog profile，而编辑臂真实入口未来将整条session绑定readout profile。它们的context/KV/执行批量参数不同，旧逻辑请求一致不能证明新引擎物理分数或资源相同。因此缓存对照仅保留原catalog身份；未来匹配引擎控制必须显式同profile，不能用旧缓存替代尚未生成的编辑前缀。


#### 固定控制准备完成，未进入模型或质量评测

新增`controller/a3_catalog_controls.py`、`controller/a3_random_edits.py`、`evaluation/prepare_a3_controls.py`及`configs/a3_controls.json`。三个catalog对照固定为首个原目录单次分数、六固定排列未校正多数票、原六排列校正多数票；都使用原aggregate/calibrate和公开目录最终平票规则。未校正多数票明确作为本次控制身份，不冒称原kernel.optimize的mean_probability政策；合成反例确认两者可能不同。来源计划、当前输入hash、完整请求/顺序/代码/schema/seed、模型配置与事件hash、完整有限score及原始用量逐项校验；缺项/不匹配拒绝，不回退伪装成功。不适用项保留unsupported/无原生提议。

随机位置只依赖固定seed42、当前question＋合格span的hash及span ID，按固定hash排序无放回选择；request_id、初答、骨干偏好不参与排序。只准备与未来当前题有效探针数量/操作序列对应的0–2条操作，显式否定使用既有允许的`It is not the case that <原span>`，不改原专家prompt/schema。现枚举空、D、N、DD、DN、ND、NN共7个可能序列作CPU准备，没有择优序列，也没有运行7实验臂；随机位置可能与关键位置重合，保留重合而不重抽，不能叫已知“无关证据”。各probe独立从原packet生成，完整差异检查、请求与位置trace保存，无伪造delta/原生答案。

两骨干分别保留121全输入、8适用与113不适用；每个catalog控制121行，合726行。原校正答案和完整legacy details、raw scores全部与原保存A3相同；共96个唯一旧目录回调为来源，single每骨干引用8次，两个六次控制各引用48次，跨臂union仍48次/骨干，不能相加成新消耗。各臂保留原input/output tokens及模型秒数，原96次合272562输入/96输出token仅作来源成本；本次新增调用和tokens均0。242完整scope、112操作准备（16空/96非空）、160随机probe请求和160匹配数量原题重评分请求均未提交，尚无新质量分数或真实编辑输出。

独立只读审查把上述计划按(method,request_hash)去重，64个随机probe＋16个原题重评分共80唯一score请求全部通过真实readout tokenizer/prepare/preflight。49个代码各自为单token，实际score仍seed42/temperature0/max_tokens1/logprobs2048，走allowed_token_ids而不是xgrammar；不得因preflight通用返回compiled就说这些score编译了grammar。model start/generate被禁止，physical_calls=0。对全部16适用输入的112操作序列，改request_id不变、更换初答仍相同位置、局部补丁保持、原目录代码映射均核验。另16个原题重评分请求与历史catalog ordinal0的完整逻辑请求、实际prompt、sampling及input tokens一致，engine差异逐字段保存在`controls/design_review/score_profile_comparison.json`；数值一致性仍未验证。只有CPU物理请求准备，没有进入模型计算或得到readout分数。

本轮37项针对性合并测试通过（0.203秒，含新增11目录控制＋6随机准备测试）。真实准备首版发现外层`source.original_catalog_config_hash`误标了config payload摘要，而NativeProfile实际摘要包括role；内层trace和事件hash校验自始正确。先保存首版脚本、`prepared/`和日志，再仅修正该元信息并生成`prepared_v2/`（1.56秒CPU）；726行控制外层hash及208个跨臂重复事件引用均核对正确，10个JSONL前后除该字段外逐行一致。此问题不记作模型失败或答案错误，也不覆盖首版。更正见精确记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/correction.json`）。另纠正原型README中“同工具仍仅CPU准备”的旧句，使之与已有smoke通过后开发截断状态一致；未改旧实验身份。

193份历史采用源、154份保护结果/A4验收、3份原生评分源及上一轮A3修复源码/收据均保持。全部新代码和配置保存精确快照/hash，没有虚构Git提交；运行入口禁止读取offline gold/R/配对数据。总证据见控制准备收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/receipt.json`）、当前prepared_v2（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/prepared_v2/receipt.json`）、命令与逐题制品导航（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/README.md`）。

本轮是控制代码和数据准备，不是主实验或采用。尚未实现/冻结完整配对控制runner及最终原题重答政策；未来关键/随机/原题重评分必须使用同一实际readout前缀的固定pair并对每臂计入六次前缀、editor、有效probe和final的全部资源。共享物理调用在实验总账去重，但不能把某臂逻辑资源写零；同调用上限、同probe数/操作类仍不保证同实际token/时间或同否定表面形式。原catalog缓存不能充当未验收的readout前缀。A3模型暂停、A2 parser待处理、互补矩阵/Router/独立评测未开启的状态均保持，整体目标未完成。


<a id="complementarity-analysis-20260922"></a>

### 离线互补分析：已完成，保留未采用身份

用户明确选择“运行已准备的离线互补分析（建议）”。本轮授权仅限`complementarity_preparation/plan.json`既定两骨干各121输入、五角色真实身份与两个旧控制的保存输出分析，保持A1 r5未采用和F真实旧组件身份。先重验84个分析源及完整输入/评分/成本合同，再分别按骨干计算矩阵、逐题方向变化和来源成本；不调用模型、不运行Router、不作独立评测或采用声明。此前只读运行核对未发现本任务模型进程；A2 parser处置仍待答、A3真实编辑暂停保持。新证据与本次授权独立存入`complementarity_preparation/analysis/`，原计划和暂停历史保留。

**验收与分母。** 14个保存运行、1694条专家/控制输入记录、2198条原生评分映射通过当前输入hash、原生评分来源、真实variant、完整分母及成本核验；84个历史分析源未变。每骨干121个唯一合法输入、157条原生映射、40母题家族，输入成功定义沿用保存结果：该输入的全部原生映射均正确；不可用仍是null/not_scored，留在分母且不记为答错。此处包含参考端，不能与原74个非参考单元的原生宏平均混用；强旧组合此前70.27%/64.41%的74单元成绩保持，不能用本次121输入计数改写“M5未超过旧R1”的原单元指标结论。

每骨干保存25个专家有向矩阵单元及49个含旧控制单元，共242条逐题trace、98条方向集合trace。独立程序不调用矩阵函数，从原始保存记录直接重算所有148个矩阵单元（含两种表中的重复）、1694条逐输入状态、14份单方法成本及全部方向集合，均一致。逐题trace含原生提议、输入hash、版本、正确/不可用、资源与源路径，不写在线选择。

| 身份 | 适用输入 M4/M5 | 可评分 M4/M5 | 正确 M4/M5 | 答错 M4/M5 | 不可用 M4/M5 |
|---|---:|---:|---:|---:|---:|
| A1 r5，未采用 | 111/111 | 91/60 | 55/42 | 36/18 | 30/61 |
| 原A2 | 9/9 | 9/9 | 8/8 | 1/1 | 112/112 |
| 原A3目录，无编辑 | 8/8 | 8/8 | 3/4 | 5/4 | 113/113 |
| 已验收A4 | 0/0 | 0/0 | 0/0 | 0/0 | 121/121 |
| 真实旧F | 104/104 | 104/104 | 76/70 | 28/34 | 17/17 |
| 旧R1分派 | 121/121 | 119/121 | 81/79 | 38/42 | 2/0 |
| 固定强旧组合 | 121/121 | 121/121 | 87/82 | 34/39 | 0/0 |

A1的不可用细分仍为M4 10不支持＋17内容容量未验证＋3语义无效；M5 10不支持＋51容量未验证。没有删除失败、借旧答案填充或改变方法采用状态。A4本范围缺明确生理模型，全部不支持；已有生理模型实验验收不填入此分母。A5负结果仍保留在原批次，表内F为旧F而非重命名后的A5。

**方向与互补空间。** 下表均为“以左侧旧方法为起点、改看A1”的离线比较；误伤只指原对→A1答错，原对→A1不可用另列，不能只报净修复而掩盖可用性损失。

| 起点 | 共同适用 M4/M5 | 修复答错 M4/M5 | 误伤答对 M4/M5 | 原对→不可用（共同适用） M4/M5 | 原不可用→正确（全范围） M4/M5 |
|---|---:|---:|---:|---:|---:|
| 旧F | 94/94 | 2/4 | 3/2 | 14/27 | 2/2 |
| 旧R1 | 111/111 | 8/9 | 13/7 | 16/33 | 1/0 |
| 强旧组合 | 111/111 | 3/4 | 10/7 | 17/32 | 0/0 |

旧F的全范围不可用恢复2/2来自能力范围外，不是共同适用中的修复。反向矩阵与每项request_id集合均保存，可用性与答错不互相替代。去除A1后，A2/A3/F三者的覆盖分别9/8/104、彼此不重叠，保存答案的正确集合恰与强旧组合相同：87/82；这是既有能力分派，不是多专家协作增量。

| 离线正确答案上界，分母各121 | M4 | M5 |
|---|---:|---:|
| 去A1的现有组件集合 | 87 | 82 |
| 含未采用A1的五角色来源集合 | 90 | 86 |
| 仅强旧组合＋旧R1两控制 | 91 | 89 |
| 五角色来源＋两旧控制全部 | 93 | 90 |

A1相对强旧组合仅新增3/4题，分别集中于2个母题家族；若已允许两个旧控制离线择优，A1新增空间进一步仅2/1题。按预先固定seed42、10000次40家族成组有放回抽样、组内保留全部输入，五角色离线上界相对强旧组合增量为+2.48/+3.31个百分点，95%描述性percentile区间为[0,6.48]/[0,8.55]。A1自身相对强旧组合含不可用分母的成功率差为−26.45/−33.06点，区间[−39.13,−14.06]/[−48.84,−19.08]。这些是已暴露开发上界及描述性不确定性，未作多重比较校正，不是新独立评测、显著性采用结论或实现了的MoA收益。oracle含评分信息，仅限离线，不进入推理或路由。

**资源。** 下列为各版本保存结果的实际head资源，包括缓存原调用；不含共同历史初答RAG成本。强旧组合与其组成头共享来源，不能把这些表行相加冒充额外实验花费；矩阵每个base行重复other成本，也不能跨单元求和。

| 身份 | M4 请求／输入token／输出token | M5 请求／输入token／输出token |
|---|---:|---:|
| A1 r5 | 202 / 2,276,784 / 108,175 | 171 / 1,933,533 / 120,322 |
| A2 | 9 / 5,206 / 1,531 | 9 / 5,054 / 1,572 |
| A3 | 48 / 142,632 / 48 | 48 / 129,930 / 48 |
| A4 | 0 / 0 / 0 | 0 / 0 / 0 |
| 旧F | 363 / 1,680,221 / 82,816 | 362 / 1,606,897 / 82,405 |
| 旧R1分派 | 57 / 147,838 / 1,579 | 57 / 134,984 / 1,620 |
| 强旧组合 | 420 / 1,828,059 / 84,395 | 419 / 1,741,881 / 84,025 |

本轮0新模型请求、0新模型输入/输出token、0模型加载；主矩阵程序成功运行CPU墙钟0.910秒，bootstrap计算0.561秒，其他核验耗时分别见收据，不将旧GPU生成成本记为本次CPU计算。未重跑A2/A3/A4，A1/A5未采用身份和历史负结果均保持，原生评分及正式v5未改。

**本轮报告脚本错误保留。** 首次序列化逐题诊断时，脚本错误地假定旧R1提议也具有可选`unresolved`字段，触发KeyError；首版源码、日志及未完成`results/`均保留。只将缺失可选诊断字段写成明确未知说明后，另存完整`results_v2/`；首版已有3个M4矩阵制品与完成版逐字节相同。这是离线报告字段兼容修复，未改原生答案、评分、可用状态或实验配置，不计为模型失败。

证据与命令见运行索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/README.md`）、完整分析收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/results_v2/receipt.json`）、独立数值核对（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/independent_checks/actual_analysis_comparison.json`）、家族不确定性（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/uncertainty/results/report.json`）。本阶段交付完成；尚不足以采用A1或宣称专家组合已超过强旧系统。Router、证据聚合、共同冻结及独立评测仍未执行；A2 parser处置待答、A3真实编辑暂停保持。


<a id="complementarity-replay-20260923"></a>

#### 2026-09-23：按当前请求重放既定离线分析

恢复工作时核对发现已有完整`results_v2/`，因此不覆盖旧结果，按原计划、原分析脚本和原保存评分，在新证据目录`analysis/replay_20260923_0210/`执行同一分析。前置审计再次通过14个运行、1694条专家/控制记录和2198条原生映射；两骨干各121输入，失败/不可用及参考端口径保持。核心矩阵计算墙钟1.120秒、CPU 1.117秒，0模型加载/请求/token、0原生重评分；没有重跑专家、修改方法、启用Router或进行独立评测。

13个矩阵、汇总和trace文件与旧完成版逐字节一致，111个分析代码、来源和旧制品前后SHA-256一致；新收据另核对96个来源锁。共242条逐题trace、98个方向集合，逐题保留7个身份。独立核对直接从原评分行重算14份身份计数与成本、148个矩阵单元、98个方向集合、6个oracle集合，并复算40家族、seed42、10000次抽样的10项比较，均一致，未调用矩阵实现或原生评分器。

结论保持：强旧组合正确87/82，含未采用A1的五角色离线上界90/86；两旧控制联合上界91/89，全部七来源93/90。A1超出两旧控制联合仅新增2/1题，仍不足以采用；A5负结果保持，F仍为真实旧F。去除A1后的组件集合与强旧组合正确集合相同，当前互补分析不证明多专家协作增量。

本次辅助验真脚本首次运行因收据相对路径与绝对路径混用触发`ValueError`，尚未开始制品比较；原脚本与失败日志保留。只给路径加`resolve()`后独立重跑核验通过，未触碰原分析脚本、数据、答案、评分或先前结果。证据与复现命令见本次运行索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/replay_20260923_0210/README.md`）、新分析收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/replay_20260923_0210/results/receipt.json`）、逐字节及来源核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/complementarity_preparation/analysis/replay_20260923_0210/verification.json`）。A2 parser待处理、A3编辑模型暂停保持；不把本次请求当作新方法模型启动授权。

<a id="a3-paired-execution-20260922"></a>

### A3配对控制执行器与共同冻结校验：CPU验收完成

上一轮离线互补矩阵已完成，属于实质进展。本轮继续用户允许的无模型代码准备，补齐关键编辑／随机编辑／原题重评分三臂共享前缀、固定pair、最终原题重答、真实物理成本去重和首错停止闭环。使用单独paired variant及共同中性final说明，原A3与原可选编辑prompt/schema均保持；不会把新paired输出伪装成原方法。原16次全局预算不增加，空／全部拒绝探针沿用无final的旧行为。另并行实现最小共同冻结清单校验，不创建通过的真实冻结、不打开独立评测；A2 parser待答、A3真实模型暂停保持。证据分别放`a3_edit_preparation/controls/paired_execution/`和`freeze_preparation/`，合成fixture明确不当临床结果或模型验收。

已完成新的配对控制实现（本地制品：`/home/data3/txy/cf_moa/controller/a3_paired_controls.py`）与持久runner（本地制品：`/home/data3/txy/cf_moa/evaluation/a3_paired_runner.py`），身份为`fixed_pair_critical_random_original_rescore_v1`。三臂都由同一实际readout配置的六次目录评分及一次editor派生；固定pair仍取原校正结果的mean probabilities、margin取第一次原目录顺序的raw log probabilities。旧catalog缓存不冒充readout前缀。编辑请求与旧可选A3入口在两骨干fixture上逐字段一致；新paired final中性说明和检查记录呈现单独固定，明确区别假设编辑与原题重复评分，完整原消息/schema及seed42、temperature0.7、editor1024/final2048均保持。旧A3文件整体hash未变，因此该新比较政策不是原方法的静默提示修改或兼容性修复。

关键编辑通过原局部边界检查后，随机臂只接收其有效操作数/类型，按此前seed42题面/span hash排序选位置；与关键位置重合保留并报告，不强制重采样，也不叫医学无关。原题对照对每个有效探针发一次新的完整原题score请求，相同内容仍有独立调用ordinal，不以同hash缓存伪装新采样。所有臂使用同一pair/code mapping和共同final政策；0个合格探针保持原目录输出、partial状态且不增加final。部分语义拒绝单独计数，匹配剩余有效操作，不补造探针。正常0/1/2探针的全实验唯一物理请求为7/13/16；每臂逻辑成本含共享前缀，为7/9/10。全局请求、输入token和输出token预算均保持原InputPacket限制；缺码回补也占预算，满16次后不能继续第17次。

runner将输入内容hash、顺序、逐题预算、两骨干readout配置/来源、prompt政策、核心源码及目录/先验绑定入SQLite计划。相同题号换输入、配置或政策不可续跑，已有输出也需plan_hash一致；执行结束必须消费完缓存尾部。首个schema/基础设施错误后后续臂及后续题停止，先完成臂、正在执行臂的raw records、成本及完整分母保留。语义invalid不混作基础设施错误；恢复不会重复采样或把CPU缓存读取耗时写作原模型耗时，预算挡下的未提交尝试与实际请求分开。

独立审查发现并修复了新实现初稿的计划绑定/缓存尾部缺口、后验profile失败ordinal偏一、空探针supported误标、恢复成本时间归因和未提交final误计实际调用。最初8项fixture虽通过，未覆盖这些边界，不能作为完整验收；追加后11项针对性通过，再加入跨臂输入/输出token上限与部分有效编辑检查，最终与旧A3、随机/目录控制、输入合同、冻结校验合并64项通过（3.767秒）。独立审查记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/execution_review/design_review.md`）保留发现与修复核验；新schema失败、错误profile及缺码耗尽预算三例已持久保存实际runner的SQLite/逐题/逐臂/first_error证据，回调数分别11/1/16。它们都是明确标记的合成失败，不是新医学实验失败。

另对当前两骨干各121个合法输入，实际配对runner保留全部242条状态（16适用、226不支持），固定两个合格span的删除/否定fixture完成256个合成回调。只读取inference文件、公开资源和配置，audit hook禁止`/offline/`访问；未读旧预测、gold、R标签或隐藏配对端。原parser真实执行，没有mock parser。按method＋request_hash去重的224个请求，全部通过安装版本的真实tokenizer、NativeBackend.prepare及xgrammar预检，start/generate_batch全程禁止；48个final请求的原消息和原生schema逐字相同。此项CPU墙钟49.274秒，47个来源hash保持。

基于合成响应形成的完整请求，单题16次请求的实际tokenizer输入长度合计M4为41654–57420、M5为38181–54286，输出上限合计均7180，符合原预算。这是CPU容量计数；fixture的10输入/1输出占位计数另列，均不算模型消耗，也不保证未来真实editor/分数文本相同。每臂请求数相同不代表实际token/时间相等。此次真实模型加载/请求/输入输出token均为0，未评分，不能把CPU预检宣称为真实模型计算或方法质量验收。

并行完成共同冻结清单校验器（本地制品：`/home/data3/txy/cf_moa/evaluation/freeze_manifest.py`）：要求M4/M5同时声明，hash绑定真实专家/采用决定、代码/提示/目录/规则/视图/预算/路由/聚合/seed/原生评分、已保存单专家输出和开发互补来源，以及两骨干核心控制完整状态/分母与开发、独立范围元信息。单骨干、源漂移、负候选伪装采用、缺失/重复/停止对照或家族重叠不能通过。16项独立fixture通过；没有遍历独立数据或执行冻结。当前真实未冻结草稿返回`not_ready`与61个结构缺项，涉及无冻结时间、Router/聚合、未规范化的采用/控制来源和未确定独立范围；该数量不是61个实验失败，也不推翻既有有效输出。哈希/声明检查本身不能证明未暴露事实或科学采用资格。初稿A1来源链不全和一次命令路径失败均保留，更正稿独立保存，不伪造真实通过的冻结manifest。

193个历史采用源、154个保留结果/A4验收、3个原生评分源、5个原A3/准备配置及84个互补分析源hash未变，核心计划原文未改。源码快照及精确hash代替不存在的Git提交。完整交付见配对CPU运行索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/paired_execution/README.md`）、真实输入与预检收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a3_edit_preparation/controls/paired_execution/data_preflight/results/receipt.json`）、冻结准备收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/receipt.json`）。本轮完成工程准备，A3真实模型仍暂停；A2 parser仍待处理，Router/聚合尚未实现，共同冻结和独立评测未完成，整体目标保持活动。


<a id="router-aggregation-cpu-20260922"></a>

### Router与证据聚合：CPU实现与请求兼容性验收完成

上一轮A3配对runner与共同冻结校验为实质进展，当前继续计划阶段D的控制层代码/单元测试准备。已有单专家输出和离线互补矩阵均已保存，开始实现仅看当前合法输入的固定稀疏路由、top-1/全适用对照入口、有证据约束的审议与至多一次追加检查，以及跨专家共享真实请求/工具预算、采用配置绑定、逐阶段成本和首错停止。A1 r5与A5仍未采用；A1只有显式研究配置才能作为未采用候选测试，默认关闭，旧F保留真实身份，A3仍旧目录且编辑模型暂停。此轮不运行路由质量实验、模型生成或独立评测，不根据逐题gold选专家或伪装方法采用；新证据在`router_aggregation_preparation/`。


**实现与限定验收（2026-09-22）。** 已新增`sparse_router.py`、`evidence_aggregation.py`、`moa_execution.py`及持久化`moa_runner.py`。默认能力检查分别复用原A2、原A3目录和A4完整模型合同；F保留真实variant，A1必须在路由配置和调用方双重显式启用才作为未采用研究候选出现，A5负候选始终关闭。首轮稀疏最多2专家、最多1次追加，top-1和全适用对照禁止追加。无专家适用时按完整原题重判，不强制保持初答；输入题号不作路由特征，不读取评分、R或隐藏配对信息。

聚合分别保存提议、每条claim及修改的程序资格、来源绑定、采用/拒绝标识与理由。A1支持补全与A2三值规则路径按候选/当前范围/显式路径ID保留独立贡献，未知不作假、删除一条不抹去其他路径；不同命名路径是否语义等价仍未验证。A2审计通过原`optimize`及保存事实响应作纯CPU复核，保持原解析/异常回退；A2列表、M5 d00050带选项描述的原值及A3诊断字符串保持原样，不用新外层schema补造解释。F的历史agent_id虽为A5，外层仍明确F＋原variant，不伪装新A5。A3模型偏好、F稳定建议及自报置信度不升级为患者事实；引用定位不等于蕴涵。A4程序权威必须有当前输入/给定模型/实际结果绑定的工具收据，且只在给定模型范围内成立；本次不重新积分。

新聚合使用单独身份`current_input_evidence_constrained_deliberation_v1`，固定seed42、temperature0.7、max_tokens2048；这是新控制层政策，不改任何旧专家参数。完整原消息与原生schema嵌入新聚合请求，要求逐项adopt/reject与理由，程序拒绝的项目不能被重新采用；四个可空冲突槽、至多一次定向检查。并不把异质分数平均，也不强制改答或保持。模型声明采用某证据仍不等于已经证明因果协作收益。

协调器分别绑定facts/catalog/readout及独立A4完整配置，A4不能替换为通用NativeBackend；多个owner确实共享同一backend时初始化时间按对象去重。所有专家、聚合和追加检查共享原逐题16请求/4工具及原token预算，不能换session重置。持久journal同时锁输入、顺序、预算、配置和源码，恢复逐请求比对，缓存事件的模型/profile亦重新核对，无法确定完成的请求不重采样。逐阶段成本从真实物理ordinal统计：preflight/预算挡下的请求为0调用，transport不确定成本保持unknown；报告token与预留请求矛盾时不称完整成本。已完成旧输出继续保留；中断但尚未落完整输出的历史工具成本可能未知，本次CPU重建时间与之分开。审计中途失败仍计已耗CPU，无法恢复的program check数量标null/incomplete。

67项合并回归通过（unittest 2.304秒、外层2.468秒），覆盖路由15、聚合17、集成19及原合同/A4默认值/首错回归；另独立复查6项和审计异常停止，不累加成额外临床样本。初次集成fixture的请求字段顺序错误、未完成缓存构造假设、缓存事件profile防御检查缺口及其修复日志均保留。最初怀疑“旧A3会吞评分回调错误”经实际采用源和真实入口核验不成立：A3评分和A2生成回调均在原try外，原来就向外传播；该误判已纠正，新增first-error latch的吞错验证只称明确合成调度fixture，不把它说成修好了旧A2/A3方法缺陷。

首轮真实tokenizer CPU预检在并行源码收尾期间启动，结束时源码hash漂移守卫拒绝验收；原start/log及失败说明保留。该轮没有模型调用、没有原专家输出重跑，未保存的内存请求细节不补造。固定源码后另建`data_preflight/results_v2/`，逐请求保存进度，完成结果待后续本节补记。既有193采用源、154结果/A4验收、3原生评分源、11本轮保护的原专家/核心计划/配置以及84互补来源hash均未变。完整工程证据见本轮运行索引（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/README.md`）及独立审查（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/integration_review/controller_review.md`）。


**固定源码请求审计已完成。** 两骨干各121条当前合法输入，保存726个三模式能力计划、242份已有专家提议审计及484个聚合请求（追加门开/关各一份）。实际采用readout tokenizer、NativeBackend准备和安装版xgrammar全部通过；真实聚合parser解析来自schema的合成fixture，未使用mock parser，仍不是模型已生成有效回答。完整原消息及Errors等原生schema字段逐项相同。18次A2保存事实的原解析/规则CPU复核完成，全部当前选中提议的程序资格通过；“资格通过”不等于医学正确或蕴涵证明。脚本用audit hook禁止offline gold/R/评分文件读取，禁止模型start/generate；本次CPU墙钟364.695秒，实际模型请求/输入/输出token均0。源锁结束复查与逐行制品计数均通过，首轮source-drift失败保留，不覆盖。

默认每骨干A2为9题、A3为8题、旧F为104题；A4在此范围均不支持，A1/A5默认关闭。三模式在本范围选中集合完全一致、每题仅一位专家，因此当前代码不是已证实的多专家协作改善，top-1/全适用/稀疏也不能仅凭不同名字当作不同混合机制成果。聚合程序决定数范围M4为2–57、M5为2–58；单请求完整输入实测5503–96881／4885–103868 token。请求同时保留原消息并在合法输入数据包呈现必要证据，存在大上下文及重复呈现开销，未为节省token截断/改写旧专家上下文。上述为准备长度而非模型消耗，也没有证明固定2048输出预算在真实生成中足够；后续任何live验证必须单列全部专家＋聚合成本和同预算控制，不能把CPU语法通过当作真实模型或质量通过。

最终源码8文件有精确快照/SHA（无虚构Git提交），代码配置、逐题请求/审计、回归、保留失败、成本与范围限制均在本轮完整收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/receipt.json`）及固定源码预检收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/data_preflight/results_v2/receipt.json`）。此轮没有live后端调度或路由质量实验，没有重跑A2/A3/A4，也没有新采用、共同冻结或独立评测。A1 r5与A5负结果、A2新增控制parser待决、A3编辑模型暂停继续保持；整体研究目标仍未完成。


<a id="cached-prefix-aggregation-20260922"></a>

### 旧专家缓存衔接与固定聚合smoke准备

上一轮Router/聚合CPU实现为实质进展。本轮重新核对时GPU0完全空闲，GPU1/2仍有健康负载，未把“四张可用”的旧口述当作当前事实。沿用户整体计划与通过兼容性检查后继续的授权，推进新聚合的固定小规模开发smoke准备；只新增聚合模型调用，不重跑A2/A3/A4，不恢复A1-v1或A5负候选，不触碰明确暂停的A3编辑模型和独立评测。当前默认三模式在本开发范围都只有一位有效专家，smoke仅验证新聚合运行/格式，不能作为多专家协作增量或采用。

独立原入口缓存回放覆盖六个完整来源、726提议/839回调，原生答案与证据内容保持，0新模型/评分。发现旧A2集合遍历导致claims数组、facts键序和按field的evidence_errors次序跨Python进程变化；保存提议原序是新聚合的固定输入。新缓存入口直接沿用保存proposal，原入口回放只作验收，不修改旧A2。新聚合审计另仅将evidence_errors按唯一非空field进行全内容相等检查，其余字段/数组保持严格；真实M5 d00018/d00095跨两个hashseed的实际请求digest一致，内容变更、缺失/重复字段仍拒绝。该修复不更换事实parser或放开待决的A2严格执行对照。

新增cached_experts/cached_moa入口把来源文件hash、合法输入、版本/profile、逐回调ordinal、请求/响应、来源内成本与新journal计划绑定。缓存专家响应消耗原方法预算，新聚合独立加载原readout配置；恢复不得重复计费或重采样。复用的工具仍占原工具额度，历史耗时与当前CPU重建分开；first_error的新提交/完成/在飞计数排除历史回调，旧专家原成本单列。72项合并测试通过，另11项缓存入口测试在禁止读取offline/评分及禁止建立真实模型的守卫下通过。

离线预算审计242题均可容纳原专家实际资源＋首次聚合输入与2048输出预留，总调用2–7；两骨干输入总量范围8433–227489／8406–271603，仍在原16调用/400000输入/32768输出/4工具上限。历史专家839调用、3569940输入/168420输出token、4146.022736秒模型归因时间属于已发生来源成本，不因缓存写零，也不作为本次新花费。最大57/58决策的固定合成响应实测1491/1553token；仅证明这份语法样本可放下，不能证明真实解释与理由在2048内足够。

当前正在完整新runner的缓存＋合成聚合流程验收，之后按未看gold的固定规则选少量适用分支、最多决策对象及最长输入作真实聚合smoke。保持seed42/temperature0.7/max_tokens2048、完整原题和schema，不为成功调参；首个非预期错误后不提交后续实验请求，保留已完成/失败/未提交完整计划。新证据在`router_aggregation_preparation/cached_prefix/`；原CPU预检、排序比较失败、修复前后与历史负结果都保留。


**本轮中间验收与资源变化。** 首次完整缓存＋fixture流程已完成M4 121题，但脚本随后将ModelSession构造的请求外层键序与先前CPU预检脚本的外层键序直接作有序digest比较，触发误报。完整对象相等、每个messages/schema/采样值相同；仅顶层kind位置不同。保存原脚本、完整M4输出与差异凭据后，第二份`prepared_v2/`只调整检查边界：完整对象相等＋嵌套消息/schema有序hash相同＋仅对齐外层映射次序后的完整hash相同。没有改变发往后端的消息/schema/参数，不改全局digest、没有重新生成模型输出。

独立CLI审查另发现首稿回放证明范围验证、续跑证明绑定、跨输出目录GPU互斥以及未提交/不确定提交成本边界缺口；这些属于新入口工程缺陷，修复与专门回归正在进行，旧专家/评分不改。22:53左右重新读资源，四卡均被其他任务使用，GPU0空闲显存91687MiB低于采用版0.95初始要求（约92977MiB）；未启动模型或中断其他健康任务。不能依据本轮早先空卡快照声称当前资源仍可运行。


**资源判断更正（同轮22:56）。** 上段0.95来自错误引用其他阶段要求，不能作为本轮两readout的采用参数。直接加载`profile(M4/M5, readout)`后确认两者实际均0.85、上下文131072；GPU0当时91687MiB均满足初始约83190MiB和当前CPU估计。原错误判断保留并明确撤回，不降低配置来适配资源。其他卡仍有健康任务，固定GPU0顺序smoke可在最终验收后重新按实时余量准入；锁只能互斥本原型作业，不能声称独占整张共享卡。


**固定smoke启动前验收。** `prepared_v2`两骨干共242输入、839原来源回调＋242明确合成聚合回调全部完成，246.050秒CPU；每条最终请求与既有tokenizer预检按上述完整内容和内部次序一致，原proposal有序digest逐条相同。最后两处入口守卫修复后，81项合并测试通过（9.609秒），独立禁模型/评分守卫下20项通过（6.197秒）。再次固定并跑两骨干共10输入的合成验收通过；相对全量prepared的仅两项源差为新CLI证明锁完整性与缓存失败成本字段，计划内容/参数/请求均不变。原全量计划与新锁定计划分别保留。

固定输入按原输入顺序取A2/A3/F首个适用题，再取最大决定数和最长聚合输入，稳定处理并列、去重后两骨干均为d00000/d00008/d00001/d00018/d00063，不读取gold。`fixed_smoke.json`绑定完整输入/源/计划/source-proof/产品和启动脚本hash；GPU0依次M4再M5，任何非预期错误均阻止后续题和后一骨干。配置仍seed42、temperature0.7、聚合max_tokens2048；仅原readout加载模型，原专家通过839来源中对应缓存前缀，不生成新专家响应。开始执行的证据与实时状态写`cached_prefix/live/`、`smoke_stage_status.json`和每骨干日志，不预写成功或已耗模型tokens。


**真实smoke首错停止，未通过。** GPU0 M4 d00000实际加载采用readout进入V1 engine计算；1次新聚合请求16347输入／1033输出token，batch size1，finish_reason=stop，模型归因墙钟40.584555秒。原A2仅复用1次历史560／159token（3.763815秒原模型成本）；逻辑总成本为2调用、16907／1192token，不能把来源成本当本次新花费。完整返回4256可见字符、18个decisions，JSON闭合且符合基础schema，但c0–c3均null，additional_check却为非空robust_readout对象，description空串，违反既有跨字段约束。不是截断，不增加输出上限，不将native_answer子字段直接抽出评分或成功替换；inference_started=true、semantic_result=unavailable、method_score=not_scored。

首错后M4剩余4题与M5全部5题均未提交，固定10输入分母全部保留（1失败、9未提交），新专家生成0。`live/m4/status.json`和SQLite永久保留当时原始error_category=schema、ordinal=2；独立诊断发现其真实含义为聚合semantic_invalid，实际aggregate ordinal=1（ordinal0为A2缓存）。原因是OutputSchemaError继承RuntimeError，控制器except遗漏该类，fallback误用了已递增的backend.ordinal。这两个元信息缺陷另做无模型修复/回放，不重写本次失败或更改parse接受集合。

父进程退出时等待本次V1 engine子进程超过150秒，durable状态已stopped_on_error且in_flight=0。核验/proc父子关系和完整本次CLI参数后，仅向本次空闲engine PID376046发送SIGTERM，父/阶段runner自行退出1；GPU0本任务约49.8GB占用已释放，其他作业保持。`cleanup.json`保存识别依据和原状态hash；不是中断在飞推理或抹掉失败。新CLI将显式调用安装版core_client.shutdown释放自己加载的聚合引擎；仅CPU mock验收，尚未重开模型验证自动释放。全部原提示/schema/采样/路由和原专家保持，当前聚合候选仍未通过、真实扩展停止。


**工程收尾验收。** 最终89项合并回归通过（12.338秒），真实失败响应的无模型回放仍被同一语义合同拒绝，正确归semantic_invalid并指向实际ordinal1，后续四题不提交；JSON/schema及长度截断仍归各自错误。控制器保留原解析异常对象，聚合语义invalid单独计数；没有自动把空对象置null或采纳不完整提议。聚合build_request、POLICY、OPERATIONS、VARIANT与audit的AST相对真实smoke源码完全相同；prompt/schema/预算/参数/路由未改。新增显式core.shutdown经过完整、停止和抛异常三种CPU路径验证，尚未新增GPU运行证明自动释放；实际失败批次的手动空闲引擎清理证据单列。

独立真实trace审计47项请求/配置/保存源/成本/分母与停止核验通过，只证明记录与运行边界，绝不宣称方法smoke通过。193采用源、154保护结果/A4验收、3原生评分、84互补源和核心计划保持；原失败9制品hash保持。首版比较误报、资源0.95误引用、fixture初次错误、原元信息缺陷与真实负结果均保留。源码快照/hash代替不存在的Git提交。证据导航见缓存衔接包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/cached_prefix/README.md`）、总收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/cached_prefix/receipt.json`）、真实trace独立核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/cached_prefix/live_independent_check.json`）、工程回归（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/cached_prefix/post_smoke_repair/engineering_acceptance.json`）。原fixed_smoke绑定失败时源码，当前诊断修复不重写它、不据此继续旧批次；后续若改模型可见合同，需独立身份/配置与真实入口预检，不能静默修答案宣称成功。本轮是缓存工程进展及一次真实负结果，整体目标仍未完成，共同冻结和独立评测未启动。


<a id="aggregation-decoder-contract-20260922"></a>

### 聚合既有合同的显式解码约束准备

上一轮为实质进展：完整缓存入口验收、真实smoke暴露跨字段错误、原失败与成本保留，89项工程回归完成。本轮先核当前源码、计划和资源，再独立检查是否能只通过显式decoder revision表达既有语义约束（非空理由/冲突描述，非null追加检查需有实际未解冲突），保持完整原生答案、prompt/schema、采样与parser接受集合。旧失败批次不恢复；不以把无效空对象改null来成功替换，也不提高token上限。当前仅无模型探针与实现边界评审；若不能语义等价表达，将如实记录缺口，不偷偷收缩到英语或禁止合法值。证据在`router_aggregation_preparation/decoder_contract_preparation/`。并行核对核心对照与当前互斥专家覆盖下的目标缺口，不把仅单专家的默认路由包装成MoA提升。A3编辑模型、A2待决控制及独立评测状态保持。


独立探针确认当前安装xgrammar 0.1.18：根部可用“无冲突＋null检查”与“首个非null冲突槽＋原nullable检查”分支表示已有依赖，原native_answer规则不动。非空文本需按Python.strip的29个Unicode空白码点及JSON转义判断，不能用ASCII或minLength1替代。首版精确Unicode转义131072个大小写BMP用例通过，但原文NBSP等测试暴露installed否定字符类未排除部分Unicode空白；该版尚未验收、没有模型调用。后续改用正向允许区间表示补集，保留全部合法Unicode内容后再测。显式新decoder仅用于聚合，原NativeBackend/schema_compat及旧专家回调不改。

并行只读计划核查定位到实质交付缺口：现有score_run只适配单专家plan.expert/proposal.native_proposal，新Router输出使用native_answer及expert_runs，需要独立离线评分入口。正在新增桥接并复用原生scorer、配对及单位汇总，完整停止/缺失/来源漂移守卫先于主结果；当前失败smoke不评分。当前top1仍有一次相同合并器调用，须与直接旧分派区分；三模式覆盖集合在现范围相同，不据名称声称协作。核心对照总体缺口见本轮`plan_gap_review.md`，不把同工具7条smoke中额外合成生理fixture混入121开发分母。

**Unicode失败诊断与候选边界。** 两种字符类实现均未验收：当前xgrammar 0.1.18对多字节首字节的字符类匹配未按码点比较，正向类拒绝合法中文/emoji，否定类接纳本应排除的Unicode空白。实际token接受、debug字符串与UTF8 bytes三条路径的180项探针一致；不是只凭mock字符串推断。转义BMP的131072项通过不抵消原文Unicode失败。完整`aggregation_consistency_v1`作为未采用尝试归档，失败源码/日志和上游固定版本证据保留，不升级依赖、不限制为ASCII。

本轮转为显式独立候选`aggregation_crossfield_v1`，只把已有“非null补查须至少一条非null冲突”依赖编入grammar；它是**部分解码指导，不是全部语义约束修复**。原字符串/native规则、prompt、逻辑schema、parser、seed42、temperature0.7、max_tokens2048保持。非空reason/description仍由原parser严格验收，若模型生成空白仍首错停、不可评分。此选择不改变方法的可接受答案集合，也不保证新采样分布或文本等于旧批次；任何真实smoke都使用单独revision/配置和输出目录，旧失败1条及未提交9条继续保留。目前产品实现/CPU验收进行中，尚无本轮新模型调用。

**CPU验收通过，独立固定smoke启动。** `aggregation_crossfield_v1`专项8项及评分桥23项包含在125项合并回归内，全部通过（26.548秒）。两骨干实际tokenizer/vLLM/xgrammar预检20请求（各5固定输入×开/关补查）与30个原parser fixture全部通过；原prompt/schema/native及除guided JSON→grammar外的全部物理采样字段相同，真实模型0。scope仍为原d00000/d00008/d00001/d00018/d00063，不按新结果更换题目。新`fixed_smoke.json`绑定两份plan、全部源码、输入和专家缓存来源，保留旧失败批次引用；将按M4→M5在GPU2顺序执行，首个非预期错误停止后续题目/骨干，不重采样。资源入口再次核`.85`原profile初始空闲显存要求，绝不降低配置适配资源。只新增聚合请求；无专家新生成，无主结果或独立评测。运行日志与状态在本轮`decoder_contract_preparation/`，阶段是开发入口smoke而非方法采用。

**评分桥与保护核验。** 新独立入口`cf_moa/evaluation/score_moa_run.py`仅接收完整的已暴露开发run，沿用原生评分、配对与单位汇总。完整plan/input/budget、每份缓存来源、durable journal和导出、每个聚合实际请求/profile/revision、原parser原生结果均先核验；任何停止、缺失、重复、来源漂移或语义无效均不能形成主结果。没有从失败raw中提取native子对象评分，也没有把桥接包装成A1。23项测试只用合成标签经真实原评分函数，0真实开发评分/独立数据读取。请求绑定补强时曾误将NativeProfile hash当裸config hash，5项回归暴露后修正为真实profile定义，失败日志与前后验证均保存于evaluation_bridge（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/decoder_contract_preparation/evaluation_bridge/README.md`）。独立哈希复核435分组条目/414唯一保护文件及原失败9制品全部未变。当前源快照144文件及三处入口diff已保存，后续启动不修改已锁定的运行源。

**真实smoke首错停止（本候选未通过）。** GPU2实际入口完成M4前三题d00000/d00008/d00001，原parser均通过；第四题d00018达到2048输出token、finish_reason=length，原生结果不可用，保留为`failure_type=output_truncation`、`semantic_result=unavailable`、`method_score=not_scored`。已捕获实际模型回执，inference_started=true；不是答错，也不抽取raw里的native子对象评分。首错指向正确的aggregate ordinal1，出现时submitted/completed均4、in_flight0；后续M4 d00063和M5五题全部未提交。独立新批次10输入完整分母为3完成/1失败/6未提交，原JSON-guided批次1失败/9未提交及完整一致性grammar失败探针另行保留。

本次4个新聚合模型请求累计59448输入/3820输出token，实际模型墙钟153.712352秒；复用旧专家11回调的历史成本另列21573/924token、20.094981秒，逻辑总计15调用/81021输入/4744输出token。原专家无新生成。M4执行墙钟190.826645秒；完整成本留在status、逐题proposal与物理回执。没有增加预算/重复采样或继续M5，也没有主结果/独立评测。显式engine_core.shutdown实际返回（0.208646秒），父CLI及阶段runner退出1，GPU2空闲显存回到89393MiB；无需像旧失败批次那样手动终止空闲引擎。接下来仅无模型核对截断内容、输出规模和独立实际入口/成本审计，状态保持未通过。

**真实入口独立核对通过。** 198项只读核验通过、0未解释差异：四个新请求的grammar等于已验收实现与预检hash，prompt/schema、实际模型配置和所有采样字段在同一LLM入口边界一致；旧专家原提议与响应/物理记录保持。初次审计把prepare快照与engine ingress跨边界比较，四项只差安装版同步入口自动设置的output_kind=CUMULATIVE→FINAL_ONLY；已保留误报，用原LLM._validate_and_add_requests无模型转换后逐字段再比，没有忽略该字段或修改运行。两次审计进程的过严导入守卫也另留日志，不归为实验模型失败。实际截断分类、ordinal、首错时数量、全部未提交题目、新旧成本和自动清理回执均一致；所有原run制品hash未变。证据见独立live审计（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/decoder_contract_preparation/live_independent_check.json`）。

**d00018完整截断诊断。** 正式入口NativeBackend的tokenizer栈为transformers4.51.3/tokenizers0.21.4；初次辅助长度脚本直接导入5.16.1/0.23.1，虽模型文件相同但不是运行栈，原脚本/结果保留为非正式统计，已在正式栈重算，40个结构fixture计数完全一致。d00018真实2048 token、8203可见字符；native_answer已完整（1132字符/独立编码238token），57个decisions均完整（6970字符/1772token），原生字段完整不使整个聚合结果可评分。最后完整字段为`unresolved_conflicts.c2=null`，停在`c3:`后的值位置，additional_check尚未开始。各字段独立编码token不具有严格可加性。

57条reason共3种，全部逐字复制对应程序audit说明；其中两模板分别重复32次（每条15token）和24次（每条13token），reason均值14.12、最大15token。无重复decision键、无无限循环；原生解释4句没有逐句重复。有限表格的模板复述提供很少逐项区分，不能当作已建立证据归因或协作收益。合同仍允许自由字符串无长度上界；本题结构fixture仅789/1085token（紧凑/通常空格），M5同题58决策为839/1140，因此不是结构本身必定装不下2048，但fixture不证明真实充分解释所需预算。

剩余c3和additional_check仍有不同语义值，不能认定只差括号。仅作为结构假设核算：null/null后缀8token；短冲突无补查21；冲突+补查的极短/短句后缀76/95。它们是正式tokenizer的条件编码参考，不是模型实际续写、无条件上界或可直接修复答案；没有生成这些后续、修复原run或评分。M5本题没有真实输出，不能用另一方法的历史M5响应代替。详细结构/重复/字段长度见输出预算与截断审计（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/decoder_contract_preparation/output_budget_audit.json`）。

**本轮结论与后续。** 工程推进成立：独立MoA评分桥、显式部分解码、完整入口/成本审计与自动GPU退出均已有证据；当前聚合候选仍未通过固定smoke，正式扩展和共同冻结未开启。保持2048、原prompt/schema/parser及两失败批次身份，不继续当前run、不重采样碰答案。下一步可先无模型核查紧凑JSON序列化是否能保持全部语义值与parser接受集合，并另列显式decoder候选；此处仅计划，尚未实现/调用，不能把假设8token后缀当成预算放宽依据。逐项理由的证据价值、当前互斥覆盖下的协作缺口和核心同资源对照仍需真实验证；不能仅消除格式失败就宣称系统成功。A3编辑真实模型与A2待决控制的状态保持，正式v5/历史原生评分不变。

<a id="aggregation-compact-decoder-20260922"></a>

### 紧凑JSON序列化候选：CPU通过，M5固定smoke仍截断

上一轮判为实质进展：部分跨字段decoder与评分桥完成，4次真实聚合暴露d00018输出截断，完整诊断和失败成本已保存。恢复时核验当前源码与两个失败批次终态，本任务无活动模型进程，核心计划hash保持。保持原57项决策及全部原生字段，不强制null补查、不补JSON后评分；本轮先研究只去JSON结构性空白的独立`aggregation_crossfield_compact_v1`。字符串内空白/Unicode、原prompt/schema/parser、seed42/temperature0.7/max_tokens2048与跨字段依赖保持。必须证明完整语义值仍可表示，而不是为了过长度关删字段或压掉冲突分支。新证据在`router_aggregation_preparation/compact_aggregation_preparation/`，前两失败批次均不续跑/覆盖。

并行核查核心top-1控制目前仍带合并器的问题，准备明确区分纯分派与top1＋合并器的可执行规范；当前专家适用范围互斥这一限制保持，不按gold/R标签挑专家，不重命名A1/A5负结果。A3编辑模型、A2待决控制、正式v5与独立评测状态保持。当前是无模型代码/CPU准备，尚无本轮新的GPU请求或候选通过结论。

**2026-09-23 00:03前后，CPU验收通过并准备独立smoke。** 安装版xgrammar原生`any_whitespace=False, indent=None, separators=(',',':')`可保留全部值而去结构空白；generic数组/对象两条续接规则仍硬编码逗号后空格，已按完整已知规则限定替换并在转换格式漂移时拒绝，字符串规则未动。新10项＋旧8项专项守卫测试通过；137项合并测试通过（29.416秒）；两骨干原5输入×开/关检查的20请求及30个原parser fixture实际tokenizer/vLLM/xgrammar预检通过。复杂enum/const与词法数值/转义测试另核原生值保持。早期测试误把旧grammar也不接受的pretty数组enum/数值排版当作基准，失败日志保留，改用旧规则确实接受的表示验证，不修改旧grammar或数值规则。

此候选仅改变结构性序列化及显式revision；原JSON-guided与crossfield-guided入口均仍可调用，原prompt/schema、全物理参数/profile、seed42/temperature0.7/max_tokens2048保持。新的`fixed_smoke.json`锁定原d00000/d00008/d00001/d00018/d00063，M4→M5顺序、GPU2，首错停整个阶段。先重新核采用配置的实时显存要求，再开始真实聚合；专家仍仅复用缓存。原两失败run的13项最近制品及旧文件全部原样，不能以新序列化通过来覆盖它们。独立当前源快照与运行记录均保存在本轮compact目录。


**2026-09-23：全范围CPU验收与真实smoke终态。** 全开发两骨干各121输入、检查门开/关各一次，484个请求及726个原parser fixture通过实际tokenizer/vLLM/xgrammar预检（CPU 346.707秒）；这是输入编译/解析验收，0模型生成，不能代替长度或质量保证。独立2926项收据/范围/当前grammar/104生产源锁核验通过，不重复编译tokenizer。脚本旧docstring仍写fixed smoke，实际完整输入清单和全范围收据明确为242输入，原脚本及hash保持。

固定GPU2两骨干smoke共10输入，M4 5完成/0失败，M5 3完成/1截断/1未提交。M4依次输出887、503、228、1756、660 token；M5前三题1189、320、398 token，d00018在2048 token上限截断；M5 d00063未提交。全阶段8完成、1不可评分截断、1未提交，不能将前三/八条成功抽出作为主结果。M5 first_error为d00018、实际ordinal 1、schema/output_contract；当时4已提交、4完成、0在飞。原输出记录保持`inference_started=true / failure_type=output_truncation / semantic_result=unavailable / method_score=not_scored`，不记答案错误，不删除失败分母。没有改温度、seed、提示、schema、输出上限或重新采样；旧专家只精确回放。

| 成本与状态 | M4 | M5 | 合计 |
|---|---:|---:|---:|
| 新聚合调用 | 5 | 4 | 9 |
| 新输入/输出token | 156329 / 4034 | 59626 / 3955 | 215955 / 7989 |
| 新模型秒 | 225.054 | 183.964 | 409.018 |
| 计入方法预算的旧回调 | 15 | 11 | 26 |
| 旧输入/输出token | 152181 / 2602 | 19040 / 1158 | 171221 / 3760 |
| 旧模型秒 | 68.016 | 33.693 | 101.708 |
| 本次runner墙钟秒 | 263.457 | 221.759 | 485.216 |

独立真实trace核验436/436通过：最终服务入口、显式grammar、原消息/原生schema/全解码字段与对应CPU预检一致，所有新raw文本无结构性空白，完整响应经原parser处理且语义字段未后改，26旧回调与源结果/成本相同。M4、M5均调用engine shutdown正常返回（0.266/0.309秒），本任务模型进程结束；其他用户作业未干预。首次审计用SQLite `mode=ro`在关闭数据库旁创建4个缓存sidecar，导致“目录完全不变”检查失败；所有此前存在的文件hash始终未变。初稿/日志/sidecar事实保留，改在live目录之外的私有副本审计后通过，未修改原SQLite或模型结果。

**M5 d00018截断诊断。** 真实2048输出token，8508可见字符；单独重新tokenize文本为2046，不取代服务端真实生成计数。原生答案对象完整（1247字符/260单独token），决策表已输出7231字符/1780单独token。58个要求ID中53项完整，最后完整字段为`decisions.p0x19.status`，在`p0x19.reason`字符串中截断；p0x20–23未生成，冲突四槽和additional_check均未开始。不存在重复JSON键；53条理由有24种文本、29次精确重复，19条使用同一“recompute path”句式，理由平均20.585/max56 token，完整项平均28.585/max64 token。没有观察到无限循环，但逐项理由重复与展开占据大部分预算。

同一新候选M4同题真实1756输出token、7905字符，57/57决策和所有尾部字段完整；理由平均14.053/max15 token，55项直接沿用程序审计说明。两骨干本就保存各自专家提议，因此决策数57/58不同，未为过关删减字段。M5还差1个部分项+4个完整项；按已完成项长度只作体积参照为约143–320 token，再加键/分隔符和未知冲突/检查字段；若假设尾部全null，固定尾部另31单独token。该假设不是模型未生成的决定，schema文本也没有有限上界，不能据此承诺增加某个上限必成功。语义尚不完整，明确不是仅缺JSON括号。诊断仅CPU 7.371秒、0新增生成，未修复/评分原失败。

证据见完整逐题trace与成本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/smoke_stage_status.json`）、完整开发预检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/full_preflight/receipt.json`）、独立trace验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/live_independent_check.json`）、截断诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/truncation_diagnosis.json`）。此候选仅M4完成固定入口验收，两骨干共同扩展门未过，当前不启动完整聚合批次。已有有效结果、前两聚合失败以及A1/A5负结果均保持原身份。

**纯top-1分派对照。** 单独身份`top1_native_dispatch_v1`，只根据当前合法输入固定选一位A2/A3/F，直接保留完整原生提议；无合并器、无追加检查、不根据正确率改路由。两骨干各121输入完整保存，0失败/未提交，各120 supported＋1 partial；合839旧模型回调/18旧工具记录，0新模型、0新工具、0聚合。各骨干旧成本为420/419请求、1828059/1741881输入token、84395/84025输出token、1854.618/2291.405模型秒；它们与强旧来源共享，不重复计为新的实验支出。当前CPU运行15.442/12.861秒，7项回归2.279秒通过，其中早期第二题人工失败后最后两题未发送且旧回调可追踪。

每骨干120/121条与强旧完整native一致；d00050的A2原提议是partial/list，而旧R1的`applied=false/used_original=true`包装保留含解释的原答案dict，投影answer_choice相同。该差别有源码与完整旧入口回放解释，纯top-1保持自己的list、不替换成强旧dict、不抹除partial。独立旧R1 34输入＋F 208输入的839缓存回调核对请求/响应/配置/成本；另10578项制品/SQLite/原提议核验通过。工程完成不自动推出质量相同；评分使用单独无模型离线导出与未改动原生评分，不伪造aggregation记录。当前生产`top1`仍是top1＋合并器，二者明确区分，不能用名称冒充已做纯分派对照。

**保护与辅助错误记录。** 193采用来源、154旧专家/A4验收、3原生评分、84互补来源、核心计划、首版9失败制品、上一版13失败制品及本次146源码快照核验通过，582个去重文件保持。保护报告初稿误把快照metadata dict当hash字符串比较，146个比较因此误报；初稿`preservation_final.json`保留，修正读取sha256并另核快照实际内容，`preservation_v2.json`全部通过。纯top-1终检首稿的检查器键名笔误也保留在attempt_history，均不是模型失败或结果修改。以上未改变正式v5、原生评分、采用参数或历史基线；共同冻结与独立评测尚未开始，整体目标未完成。


**纯top-1离线评分完成。** 在单独评分进程验证SQLite、来源、完整121输入/157映射及所有原生辅助字段后，原行逐值导出，调用未修改的`score_run`；不伪造聚合记录，`top1_native_dispatch_v1`与实际selected expert variant分别保留。6项停错/缺失/重复/漂移/完整native门禁测试通过（18.923秒）。M4为87正确/34错误/0不可用；M5为82/39/0，分母各121。74个非参考等权原生单元均值70.2703%/64.4144%，与既有强旧组合汇总相同；这不是同一算法的证明，d00050完整原生差异及适用状态照常保留，也不是多专家聚合提升。评分CPU墙钟6.784/7.040秒、0新模型；独立2299项保存分数/输入/原生映射与单元汇总重建通过，不再次评分模型。证据：评分与逐题制品（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/pure_top1/scoring/receipt.json`）、独立评分核对（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/pure_top1/scoring/independent_check.json`）。现有开发数据身份保持，未读取未参与选择的独立评测。


最终独立交叉审查从A2/A3/F原保存分数出发完成5020/5020检查（6.817秒）：242条完整proposal及顺序保留，314条原生映射仅控制expert身份改为`top1_native_dispatch_v1`，实际专家variant、判分和辅助字段严格一致；单元/配对汇总独立重建一致，839次旧模型和18条工具成本完整，d00050 partial/list原样。未重复运行scorer、未连接原SQLite、0新模型，原run全部文件清单和字节hash前后相同。详见独立交叉核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/pure_top1_scoring_independent_check.json`）。阶段总收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/receipt.json`）与交付源核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/compact_aggregation_preparation/root_delivery_check.json`）已保存；此轮是工程/控制推进与真实负结果，整体目标保持未完成，聚合扩展暂停而不是整体暂停。


<a id="aggregation-reason-codes-v2-20260923"></a>

### 聚合v2原因码：CPU验收完成，真实smoke因语义冲突停止

上一轮为实质进展：纯top-1开发对照完整、与强旧汇总相同；紧凑聚合的M5截断定位于53/58决策，固定批次停止且GPU释放。本轮核验原总收据48制品及停止状态后，继续计划内控制层研发：采用显式新方法`evidence_reason_codes_v2`，每个原决策ID保留，模型选择有限采用/拒绝原因类别；原审计证据、范围、程序资格理由及完整原生输出合同保持，四个冲突自由说明和至多一次追加检查保持。不把程序资格当医学正确，不强制采用工具、保留初答或翻转。

此方案减少逐项自由解释细度，不能称语义等价的兼容修复；与前面三个聚合候选分开保存，0旧专家重生成，不增加2048输出上限、temperature或seed。原生答案和冲突文字仍无总长度硬上界，CPU体积检查不保证smoke必通过。先完成真实入口可复核的新合同/解码/回归准备，不启动失败批次续跑。证据目录`router_aggregation_preparation/aggregation_audit_v2_preparation/`。并行准备完整分母及实际资源绑定的核心对照账本，避免把旧3×2048采样误标为当前MoA严格成本匹配；不读独立评测，A3编辑模型和A2待决路径保持暂停。

**实现及CPU验收。** 新逻辑合同与`aggregation_reason_codes_compact_v2`解码必须共同显式选择，默认v1入口不变；全部原决策ID、审计来源、原生字段、四个冲突说明和一次可选检查保持。8个固定码区分支持采用、限定采用和六类拒绝，其中RP只用于程序已拒绝项；程序合格项仍可采用或拒绝。RU表示尚有实质未解不确定性，parser要求实际冲突说明。固定码到说明文本的解码明确标为类别解释，不能冒充模型生成的逐项医学理由。新grammar保留旧紧凑序列化和补查依赖；RU→冲突、非空白文字仍是parser门禁，未宣称全部语义都由grammar保证。

129项入口/回归测试通过（32.159秒），另15项新合同专项通过（100.917秒），是两个套件合计144项而非一次144项测试。固定两骨干20请求/50fixture实际tokenizer预检通过；完整242开发输入、检查开关各一次共484请求/1210fixture通过（354.988秒），0模型生成。独立3894项收据/范围/重建请求/profile/106生产源锁核验通过。实际采用栈为transformers4.51.3、tokenizers0.21.4、vLLM0.8.5、xgrammar0.1.18。原native/conflict/check schema及所有非guidance物理参数保持，prompt与decision schema按新方法明确变化。d00018保留M4/M5各57/58项，独立编码决策表401/445token，只是体积参照而非模型预算成功保证。150源文件快照、schema/prompt及入口diff已保存，未以不存在的Git提交替代实际hash。

**固定真实入口smoke。** 2026-09-23约00:42在GPU2按原采用完整readout profile启动，实时资源门通过；d00000/d00008/d00001/d00018/d00063顺序固定，两骨干M4→M5，首错停止整个阶段。M4前三题完成，第4题d00018为`AggregationSemanticError/semantic_invalid`：57个决策均存在，AC16、AS9、RN31、RU1，四个冲突槽全null，补查null。完整JSON通过结构schema及实际grammar，finish_reason=stop、输出669token，未达2048上限。RU与缺失冲突说明违反本版parser；不是截断、不是答案错误，不提取其中native子对象成功替换/评分。仍为inference_started=true、semantic_result=unavailable、method_score=not_scored；该inference事实来自真实engine回执，未改写原run元数据。

首错实际aggregate ordinal1、4submitted/4completed/0in_flight，另11旧源回调单列。固定10输入完整分母为3完成/1语义无效/6未提交（M4剩1、M5全5），失败样本与未提交项不删。阶段与CLI退出1，engine_core.shutdown正常返回（0.293秒），无需手动停止引擎。新聚合4次共59040输入/1978输出token、90.953模型秒，runner墙钟131.103秒；旧专家11回调历史21573/924token、20.095模型秒，仅计方法资源，不记为本次新支出。未新生成任何专家，未重试、调温度/seed/上限，未做质量评分/独立评测。

独立真实trace审计222/222通过（7.410秒）：服务入口、grammar、全profile及非guidance参数一致，所有原生字段未经事后修改，码→固定说明展开透明，旧专家原响应/成本精确复用，停止分母和清理回执一致。SQLite仅复制关闭后的源库到私有目录检查，原live清单与字节保持、未产生sidecar副作用。此审计证明运行记录可信，**不代表方法smoke通过**。证据：阶段终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/smoke_stage_status.json`）、完整CPU预检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/preflight/receipt.json`）、真实入口独立核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/live_independent_check.json`）。新版未过两骨干扩展门；当前仅继续无模型诊断和组装守卫准备，不将前三条拼成主结果。

**停止后原响应诊断。** 四条新响应真实输出543/577/189/669token；末题1962可见字符（重新编码663token，含停止等边界差别，不能覆盖engine实际669）。native值1123字符/独立229token，决策表719字符/独立398token，冲突对象41字符/21token，补查null为4字符/1token；独立字段编码不能直接相加。唯一RU位于p0x11，57/57项和全部JSON尾部已闭合。真实原parser回放前三题结果逐值一致，末题同一错误；实际grammar仍接受末题，定位到已知parser-only跨字段条件，不是grammar编译故障或输出长度不足。CPU诊断15.035秒、0生成/评分，原live文件清单/hash保持。辅助脚本首版在lazy compiler初始化前调用compile报错；源码/日志保留，改为先走正式preflight初始化，未改产品或失败结果。见结构及长度诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/semantic_failure_diagnosis.json`）。后续可先无模型验证独立decoder表达已有RU→实际冲突依赖的能力；此处仅下一步计划，不改本版提示/parser、不自动替换RU或编造冲突、不继续本失败批次。

**阶段收尾。** 独立诊断54/54项复核通过，实际回执/57码/字段字符长度/旧parser分类一致；229/398等字段token沿用已锁定实际tokenizer诊断，不冒充另一遍新tokenize。930去重文件的保护核验通过：193采用来源、154旧专家/A4验收、3原生评分、84互补来源、核心计划、三个既往失败批次及旧冻结快照/当前150源码及其快照保持；当前106生产源锁在GPU运行、CPU预检、最终交付时一致。原v1 parser/grammar/native backend不变，本轮显式v2入口改动按diff保存，未错误要求新入口等于旧源码。

未通过smoke时，剩余116题每骨干仅作为inactive分拆意向记录；未创建可执行扩展计划或生成合并主结果。包内仅允许合成聚合事件的组装原型完成8项回归（2.376秒），核原生/逐轮parser/物理调用与时间戳不变、成本一次计入、停止/活动锁在读SQLite前拒绝、缺失/重复/漂移时保持完整分母。初次fixture连接未关闭导致WAL门拒绝的日志保留；真实激活、完整proof生命周期、121题组装与评分桥验收均仍待完成，不能把合成回归写成真实扩展已就绪。见未激活扩展准备（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/extension_preparation/receipt.json`）。

本轮总收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/receipt.json`）与最终交付核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/aggregation_audit_v2_preparation/root_delivery_check.json`）锁定79制品及106生产源，全部一致；本任务模型进程为0，其他健康GPU作业未触碰。本轮属于新候选实现/验收与真实负结果，持续目标仍active且未完成，未作共同冻结或独立评测。

<a id="control-resource-alignment-20260923"></a>

### 核心对照的资源及完整分母准备（无新推理）

本轮同计划§12.2完成242合法输入的资源账本、484个固定采样计划与历史四类核心对照状态复核，0模型/评分/独立输入。强旧与纯top-1共享839个实际旧模型调用，2517个逻辑别名引用去重计费，不按三份结果重复计新支出。真实输入、全部原采样/引擎profile、工具资格、知识资源和完整原生合同绑定；不将来源初始化或未知历史初答成本记作零。实际tokenizer CPU计数26.783秒，18项独立汇总检查通过；辅助检查器最初错误的排序digest假设保留并已修正。

| 当前对照，分母各121 | M4完成／无效／未提交 | M5完成／无效／未提交 | 历史模型请求M4／M5 |
|---|---:|---:|---:|
| 强旧组合 | 121／0／0 | 121／0／0 | 420／419 |
| 纯top-1 | 121／0／0 | 121／0／0 | 同420／419，无新增 |
| 同工具r2 | 13／1／107 | 73／1／47 | 67／346 |
| 原3×2048采样 | 63／1／57 | 121／0／0 | 190／363 |

同工具包括6开发smoke＋115扩展，额外生理fixture不进入121分母；历史其他失败smoke成本另列。同预算采样包括4smoke＋117扩展，M4失败题已用1次请求后未发送剩余draws。停止的对照不得通过删除失败/未提交行生成主结果。

明确准备两种未来采样预算定义：第一是原16调用/400000输入/32768输出/4工具共同上限；第二是已保存单个选中专家实际资源加一个预先固定聚合请求和2048输出预留的参考向量。均在生成前由完整原请求长度固定可容纳draw数，seed从42递增、每次完整2048上限，保留未花费预算；不足一次完整请求时不可用而不缩短上下文/输出上限。二者是同上限比较，不能称实际计算支出严格相等，也不得依据答案质量、早期一致或实际短输出选择采样前缀。

**版本边界。** 此参考向量明确绑定上一版`aggregation_crossfield_compact_v1`全CPU请求，未采用且不能改名算成本轮reason_codes_v2。原共同上限分布为M4 116题×16＋5题×12次、M5 116×16＋5×11；旧紧凑参考向量分别119×1＋2×2、120×1＋1×2。新v2或任何未来prompt/schema/资源变化都需新的完整CPU重算，现有表不覆盖更新。当前spec只是准备，生产采样runner仍是原三次，不静默改原配置启用新计划。

同工具r2使用readout backend承担内部工具请求，而原facts/catalog有自己的完整profile；例如药物事实抽取原temperature0、r2为0.7，context/KV/GPU比例亦不同。已提出显式新控制身份`same_tools_single_agent_adopted_role_profiles_v1_PROPOSAL_ONLY`，按角色绑定完整原readout/facts/catalog/A4配置；这会改变r2部分实际请求及引擎条件，**不是修复旧r2或可续跑结果**，当前未接入runner/未实际调用。原同资源含义、完整context preflight及新身份需一起验收。现同工具不完整、两骨干采样不完整、MoA smoke未过，readiness共同冻结仍false；不能写冻结后报告或独立成绩。证据：核心对照准备包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/README.md`）、固定规范（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/fixed_control_specification.json`）、完整状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/readiness.json`）。

<a id="reason-codes-crossfield-decoder-20260923"></a>

### v2既有RU依赖的独立解码候选

上一轮为实质进展：新方法实现/144测试、484真实tokenizer预检、4次真实调用及语义失败诊断/独立核验和资源对照账本均完成。本轮恢复先重读实际核心计划、主记录，核验79旧制品与106生产源；上一失败批次stopped_on_error、无本任务模型。继续计划内受证据约束聚合：仅准备显式`aggregation_reason_codes_crossfield_v3`，逻辑仍`evidence_reason_codes_v2`，原prompt/schema/parser、.7/42/2048和完整骨干profile不改，表达既有RU→至少一个非null冲突条件。语言目标是原canonical compact语言与既有条件的交集；不声称覆盖任意JSON排版/转义或已解决非空/医学语义。非空说明继续原parser把关，不从失败raw自动生成冲突或改原因码。

实现以固定ID顺序的有限状态后缀表示是否已见RU，规则规模线性；无RU保留原全部冲突/补查分支，有RU只收紧原本无效的全null冲突。原native/basic/string规则保留字节。旧v2 decoder仍独立可用，旧失败不可续跑。新证据位于`router_aggregation_preparation/reason_codes_crossfield_preparation/`；先单元/真实入口CPU验收，再决定独立同10题固定smoke。并行在核心对照证据包准备固定k采样执行入口，仅CPU、独立身份、旧参考向量不得冒充新v2成本；A2待决与A3编辑模型暂停保持。

**CPU验收通过，准备固定真实入口。** 64项原入口合并测试30.941秒、新decoder入口5项3.616秒、独立语言/tokenizer12项243.269秒均通过；后者包含1024跨字段组合、686码组合、两骨干8合法/4负例token序列。旧669-token响应由旧grammar接受、新grammar拒绝，原parser仍同semantic_invalid；保留/修改原生答案均可，不强制采用或保持。独立tokenizer专项使用同tokenizer、单线程compiler及默认词表元数据，不冒充正式服务配置；正式VLLMBackend的model-config词表/8线程gate另有20请求/50fixture通过（70.328秒），提示/schema/parser与全部非guidance物理字段相同。完整242输入CPU预检继续，无模型。

153源码/测试/config快照及522行差异已存；原逻辑v2方法文件、v1/v2 grammar、native backend和核心计划hash保持。新`fixed_smoke`仍同d00000/d00008/d00001/d00018/d00063、M4→M5、GPU2、.7/42/2048及首错全阶段停止，独立目录，不续跑旧失败。准备脚本曾在最终独立日志尚未复制时被文件存在门挡住，0模型/0run目录；通过后才激活。仅新聚合，全部旧专家精确回放，无质量评分/独立评测。

**全范围CPU门完成。** 两骨干各121输入×检查门开关合484请求/1210fixture通过，449.049秒、0生成。独立3894/3894核验10.753秒，通过107生产源锁并对上一版AV2逐字段验证消息/schema/所有非guidance参数相同；固定模型门仍独立判断。GPU2采用profile显存门通过，01:12:57 M4引擎就绪，当前stage运行中，已有前三条完成；未提前写两骨干通过或采用。

<a id="fixed-k-control-executor-20260923"></a>

### 固定k原生采样入口及旧请求复用审计

核心对照从只读预算规范进一步实现为包内独立入口`fixed_sampling.py`，沿用原native_sampling原生投票键、完整最早赢家对象、ModelSession和durable JournalBackend/SourceRunJournal。所有k、seed42起的序列、完整prompt/schema/profile及累计输入/输出预留在生成前固定；每draw原.7/2048，不按已生成长度/投票一致性临时补采。k=0记为推理前不可用且保持分母，首个非预期schema/基础设施/语义错误停止后续。原生产3×2048/r2配置和历史未改；两个新控制身份明确为`native_sampling_fixed_k_common_envelope_v1`及`native_sampling_fixed_k_cached_reference_envelope_v1`。

11项CPU回归3.690秒通过，包括原生辅助字段、平票最早对象、早期错误后不再发后续draw/题、预算不足分母、源/参数/k漂移、同run续接不重算成本、未知在飞不重试、完整profile初始空闲显存门及准确错误ordinal。独立审查修正了包内GPU门未包含完整profile比例、回调后用量错误错误定位下一ordinal两点；没有改旧runner。四份完整121输入计划绑定原共同预算1916/1911draw及旧compact参考123/122draw，源终检73项与重建全部一致。最初8测试及静态计划保留为未运行历史，最终源绑定不同，不作为当前执行配置。

**旧响应不可重复生成。** 原三次采样553条已执行物理请求与新共同预算对应前3draw的完整值、嵌套顺序、model/profile、实际NativeBackend物理参数及安装版engine ingress全部一致。仅logical最外层键次序不同，旧/新ordered digest必须分别保留并用明确映射证明，不改变全局digest或忽略内层prompt/schema次序。M4 189正常＋d00063 seed42一条2048截断，M5 363正常；旧费用M4 718827/53351token、1343.383秒，M5 1423860/97863token、2269.589秒，只计一次历史物理费用。审计36.398秒CPU、0生成/评分/旧SQLite/gold读取，完整242输入保留。

新共同预算容量尚缺M4 1726槽（173旧seed未提交＋1553新seed）、M5 1548新seed槽，仅为计划差额而非未来支出或授权。M4 d00063旧失败请求精确相同，不能重新生成碰不同答案或越过它填表。当前入口仅支持同run恢复，跨旧run导入尚未实现；为防止重复花费，真实CLI即使给live标志也在GPU查询/建输出/建后端前明确拒绝，状态`blocked_pending_old_sampling_reuse`，0本轮控制模型。代码核与测试完成不等于实际核心对照已齐。证据：入口及当前计划（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/README.md`）、收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/receipt.json`）、553请求复用审计（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/reuse_audit.md`）。旧compact参考明确不用于本轮v2，新版完整参考向量另行无模型绑定，不能依据smoke质量调整。


**RU decoder固定smoke完成（2026-09-23）。** 两骨干均5/5完成、0失败/未提交、first_error=null；均保持原.7/42/2048，所有原native字段、logical v2 prompt/schema/parser和非guidance物理参数不变。独立531/531真实入口检查通过，原run文件清单和字节hash保持；M4/M5引擎shutdown均正常返回（0.257/0.317秒）。M4新5聚合156215输入/2674输出token、185.047模型秒；M5新5聚合163358/2842token、227.494模型秒；合10新请求319573/5516token、412.541模型秒，runner墙钟分别234.474/279.586秒。30旧专家精确回调的历史313109/4588token、126.865模型秒另列，0专家新生成。完整JSON和parser通过仅证明本批入口合法，不是质量提升或共同冻结。之前RU缺冲突失败、三个更早聚合失败均原样保持。

**剩余输入生命周期准备。** 包内独立helper完成20项CPU回归（11.819秒），完整CPU/双骨干5题/独立审计及释放锁是准备与启动前置门。通过后仅拆分未生成的116题各骨干，沿用原cached_moa入口、严格原plan/source proof、全阶段首错停止，无自动重试或重复smoke。将来5+116组装逐项验证原parser/native、完整物理请求/响应与真实时间戳，旧新费用分别计且不重复；缺失/失败/漂移不能生成部分主结果。回归中的组装与评分桥仅两题合成数据，真实121题组装尚未执行。107生产源hash保持；当前正进行独立helper审阅，尚未启动扩展。证据：真实smoke独立收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/live_independent_check.json`）、扩展helper与边界（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_preparation/README.md`）。

**当前v2＋crossfield_v3成本参考重绑定。** 另完成242条预算向量及4246项检查（6.717秒CPU），采用正式首轮check_used=False的完整prompt；242×5种追加操作均无可用第二专家，不能假定额外执行了检查。旧专家420/419调用加每题一次预留聚合，参考调用上限541/540；完整聚合输入1627899/1614001token，合旧专家参考输入3455958/3355882，聚合输出每题固定预留2048。固定原生采样k合123/122，虽与旧CC数量巧合相同，已按当前v2/v3请求及来源重新绑定。原native采样token长度精确hash验证复用CA既有实际tokenizer收据，0新tokenize/grammar/模型/评分；聚合实际秒数仍null，不把预算写成实耗。独立复核175hash及242行字段/汇总通过，839旧物理ID只计一次。旧CA表未改；新参考表尚未接真实runner，原缓存未导入和M4已知sampling截断门继续保持。首版辅助脚本读取了不存在的draws字段（实际字段为draw_count）而停止，保留错误日志、未写部分表；修正只影响准备脚本。证据：当前参考资源与收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/control_reference_preparation/README.md`）。


**启动前外部helper审阅发现与修复中。** 首份`extension_run/`只准备、0模型、从未启动；独立静态审阅发现启动门只检查列出的来源hash，没有重新检查manifest中实际run路径是否仍为116题分区，误指已绑定5题smoke路径可能重复调用。另发现组装的callback finish_reason/profile/token与durable物理事件需要逐值绑定，避免损坏trace将真实length冒作stop。未发现实际smoke发生这类损坏，531项真实trace核验仍通过；这是辅助生命周期守卫缺口。仅暂停扩展启动并修包内helper，保存修前代码、准备计划与回归，不改生产方法、原专家/旧结果或smoke。补查补充核对：10题中模型提出4次请求（M4 d00018；M5 d00000/d00018/d00063），原router均记录not_available、choice=null、executed=false，没有第二轮聚合；不能把10/10写成补查执行臂通过。


**外部守卫修复完成并启动固定扩展。** 独立审阅三项缺口（manifest实际分区、聚合durable事件、旧专家durable外层请求与source_reuse身份）已补；19项既有非评分回归＋10项新回归合29项通过（30.550秒），原第20项两题synthetic scorer此前通过，此次没有重复评分。旧两个调度fixture缺少新manifest字段造成初次测试失败，失败日志保留，调度隔离测试与独立真实分区测试分别验证。原助手跨agent续写一度被平台thread limit拒绝，改由独立审阅agent承担修复、根再核代码，不影响模型或结果。107生产source-lock不变，方法prompt/schema/parser/采样完全未动。

修后重新在`extension_run_guarded/`准备，真实完整smoke门、原parser及来源均验证通过；根另外重建116分区/原生产plan，两个新输出目录均不存在，manifest SHA256=`4894fd26e3b2e1a18431d46e1400a91caf1fcea4b387f9efd91c17fcba3bfee5`。原`extension_run/`只准备而未运行，hash绑定旧helper后自然不可启动，永久保留。2026-09-23在GPU3（同H20、启动前97364MiB空闲）启动两骨干顺序M4→M5；各116题只做新聚合，原5题原样复用，首错停止后续阶段，不自动重试。exec session51069；独立评测与开发质量评分尚未启动。CPU并行只准备严格旧采样响应导入，M4 d00063已知length失败必须保留，绝不重采或绕过。证据：外部守卫修订验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_preparation/review_repair_receipt.json`）、固定扩展启动清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_launch.json`）。


**后续离线评分入口准备（仅计划）。** 当前原`score_moa_run`使用SQLite `mode=ro`，关闭库旁可能产生sidecar；生产源已锁定且评分行为本轮不改。若两骨干完整通过，将先执行5+116无损组装与独立核验，再对终态组装结果的逐字私有副本调用原scorer，原组装及smoke/extension源目录保持不动，复制来源/hash显式登记。这里只确定执行隔离方式，未复制真实评分输入、未读取新质量结果或启动评分。


**扩展真实首错停止（2026-09-23）。** M4剩余列表首题d00002的聚合ordinal3返回finish_reason=length、2048输出token，原parser记OutputSchemaError/output_truncation；状态inference_started=true（实际engine调用证据）、semantic_result=unavailable、method_score=not_scored，不算答案错误、不删除。新聚合8371输入/2048输出token、45.148模型秒；3旧F回调历史8007/554token、12.173模型秒单列。首错1submitted/1completed/0in_flight；M4扩展0完成/1失败/115未提交，M5扩展116全部未启动；合原smoke完整242分母为10完成/1失败/231未提交。阶段与CLI退出1，engine shutdown正常返回0.259秒，runner墙钟77.288秒。没有续跑、重采、改预算、结构恢复或评分。

结构初诊：10238字符在原生step_by_step_thinking首值内截断，没有任何完整值字段；answer_choice、2项决策、四冲突槽与追加检查均未开始。将serialized\n仅用于分段显示后，42句片段/22种、32段片段/14种，同一个348字符段落重复12次；不是需要输出很多证据项，也不是只缺闭合括号。归为本聚合版本的原生解释生成重复/稳定性问题，不单独增预算。完整CPU tokenizer长度/合同诊断和独立终态审计正在保存；当前GPU无本任务模型，下一候选尚未实现或启动。


**扩展诊断与终态验收完成。** CPU原响应诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_truncation_diagnosis.json`）8.062秒、0模型/grammar编译/评分/JSON恢复：真实输出2048token，可见文本重编码2047，差异不覆盖engine计数；native对象未闭合部分10221字符/2044独立token，首字符串内容10195字符/2037独立token。重复最长组348字符/67独立token，出现12次；总18次重复段落、20次重复句子片段。题面1320字符、4选项、2决策，完整模型输入8371token，远低于已通过smoke最大97175；旧F完整原生参考755字符/171独立token，未拿来替换失败聚合。M5同题聚合未提交，不补生成比较。缺少答案及整个证据尾部，既非仅结构闭合，也无可信有限继续token估计。

独立终态审计（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_terminal_independent_check.json`）71/71通过、9.630秒：实际入口全部参数/grammar、首错、3旧回调、完整分母与清理均一致；原smoke和extension文件清单/hash未变。审计的raw_sha256字段沿用contracts.digest(raw)（JSON字符串序列化digest），诊断raw_sha256是UTF-8文本字节SHA，两者算法明确不同、不误比较。含smoke本轮总11新聚合327944输入/7564输出token、457.689模型秒；33旧回调历史321116/5142token、139.038模型秒。新费用与方法复用资源分别保存，242逐题终态清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/full_scope_status.jsonl`）保留每题输入hash/预算/来源及未评分状态，无部分主结果。终态保护复核（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/preservation_terminal.json`）1177文件仍全部保持。两骨干共同完整开发门未过，本候选不采用，不拼接旧版本填齐；独立评测与共同冻结未开始。


原响应诊断另经25/25独立检查通过（0.116秒），字符/首未完值/重复8组/旧F原proposal和两种hash定义一致；token数仅精确绑定现有实际tokenizer收据，没有重复tokenize。见诊断独立验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/extension_diagnosis_independent.json`）。

<a id="sampling-import-ledger-20260923"></a>

### 旧采样只读映射入口：保留真实时间、费用与停止边界

并行交付CE/old_response_import/map_import.py，绑定553条旧全请求/profile、仅允许明确记录的外层JSON键置换，保留旧/目标两个ordered digest及全部原生辅助字段。4份已终止源库在持原run锁且WAL无待写入时复制到私有临时文件，仅对副本immutable只读查询；原库0连接/0sidecar/0修改，原started/finished和event.elapsed完整保留，不用本次准备时间伪造历史物理时间。

10项边界回归0.042秒通过，真实只读映射10.504秒，另2566项算术/hash检查0.672秒通过，207来源hash不变。553旧物理请求历史2142687输入/151214输出token、3612.973模型秒和3691.041调用墙钟秒分别保留，二者有重叠、不能相加。四种目标映射共享同一旧物理库存，分配视图不能相加计新费用；本次0模型/分词/评分/gold/独立数据。

| 准备目标（各121题） | 固定draw | 旧draw可映射 | 缺失draw | 只读顺序预览 |
|---|---:|---:|---:|---|
| M4共同上限 | 1916 | 190 | 1726 | d00000 seed45缺失处停止 |
| M5共同上限 | 1911 | 363 | 1548 | d00000 seed45缺失处停止 |
| M4当前v2参考 | 123 | 65 | 58 | 63题可用；d00063 seed42原截断；后57不继续 |
| M5当前v2参考 | 122 | 122 | 0 | 121题映射可用，未执行目标控制/评分 |

**不是已实现durable导入。** 现CE只接受旧compact参考身份、同run请求hash及常规新请求成本；直接塞旧calls会改写请求身份、误计新费用，并把未来draw提前插到缺失/失败点之后。按小范围边界，本次交付可执行只读映射和真实资源账本，后续仍需专门的历史采样成本/双请求hash/逐槽回放适配；原blocked_pending_old_sampling_reuse门保持，不用重命名或映射可用状态宣称对照完成。已知M4失败和每目标121分母完整保留。证据：入口与明确缺口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/old_response_import/README.md`）、最终收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/old_response_import/final_receipt.json`）。

**本轮交接。** 总收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/receipt.json`）与根终检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/reason_codes_crossfield_preparation/root_delivery_check.json`）通过107生产源及23关键制品绑定；全部本任务模型已退出，GPU2/3各4MiB占用，其他作业未触碰。属于工程推进、固定smoke通过及扩展真实负结果，不是整体完成或方法采用。正式v5/评分/历史采用版保持，A1/A5未采用，A2决策待答，A3模型暂停；有意义的多专家协作、完整核心控制、共同冻结与独立评测尚未完成。


<a id="native-explanation-stability-20260923"></a>

### 原生解释重复后的独立聚合候选与采样回放推进（准备）

上一goal轮属于实质进展：RU decoder固定10题通过，但M4 d00002在原生解释首字段反复展开而截断，完整242分母与负结果已验真；旧553采样映射可执行但尚非正式目标回放。本轮重新读取指令、核心计划和终态收据，23制品/107当时生产source-lock一致，确认无本任务模型存活，不续跑失败扩展。

按重复生成这一原因，仅准备独立新聚合方法`evidence_reason_codes_concise_native_v3`：保留原完整native schema/parser、每项理由码、全部证据/冲突及追加检查政策，使用同RU decoder、同采用模型/.7/42/2048，只增加解释简洁、不反复重述、完成后继续其余必填字段的提示。该提示变化不是v2的纯兼容修复，也不是已经稳定的证明；不删字段、限合法答案、强保持/强翻转、不补闭合或提升输出预算。先独立设计审阅、程序/实际入口CPU验收，固定开发smoke预先设为原五题加d00002，两骨干各6；新增项来自已确认的失败机制，仍为开发诊断，不能包装独立评测。原生自由解释仍没有总长度保证。此时尚未实现或模型执行。证据目录`router_aggregation_preparation/native_explanation_stability_preparation/`。

并行仅在CE新子目录实现采样专用逐draw回放账本，目标是从只读映射推进到实际原生投票/完整输出/失败分母验收；CPU准备与正式回放分开，暂不启动新模型或评分，不改旧CE/原采样失败。历史采样成本需独立于新物理费用和专家复用费用，完整保留旧/目标两个请求hash以及原物理时间。当前默认路由仍单专家，以上只能推进控制层和控制实验，不能证明核心计划§2.3的协作增量；五专家互补、核心完整对照、共同冻结及独立评测仍未满足。

**CPU准备收尾（2026-09-23，用户转向离线互补分析时）。** 新候选实现及分派已保存，77项入口/首错/合同测试通过（46.153秒，含合成评分桥测试，不是实际开发评分）。独立实现审阅53项通过；固定24个请求/60个fixture的实际tokenizer/grammar CPU预检及267项独立核验通过，输入提示每请求增加107 token，schema、原生parser、采样及RU grammar不变。后台全量CPU预检也已结束：242输入、484请求、1210个fixture，454.499秒；其独立全量复核尚未执行，不视为全部门禁通过。证据见实现审阅（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/implementation_review.md`）及全量CPU收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/preflight/receipt.json`）。未准备或启动新候选真实smoke，旧成功raw仅作parser回放，不能记为新提示推理成功。

采样专用回放runner另在`control_alignment_preparation/executor_preparation/sampling_replay_execution/`实现，13项合成测试通过（1.814秒），实现收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/sampling_replay_execution/implementation_receipt.json`）标明待root审阅。尚未绑定实际计划、未执行真实历史采样回放；合成63完成/1失败/57未提交不当实际结果。原207项锁、旧采样及负结果不变；对当前聚合代码的差异单独列为待审来源变化，不能覆盖旧锁。按用户当前离线分析请求，以上仅收尾CPU准备，0新模型、0实际开发/独立评分。

**继续阶段目标（2026-09-23，启动记录）。** 前轮已完成离线重放及独立核验，属于实质进展；本轮继续原目标，A2 parser待决与A3编辑暂停不变。当前GPU2/3各97364MiB空闲，0/1有其他作业。本候选全量预检独立4867项核验通过（8.796秒），固定12题从原121输入导出，原source proof与execution_plan重新绑定；准备在GPU2顺序运行M4/M5各6题，只生成新提示的聚合，旧专家与旧聚合失败不再生成。首次prepare因旧保护清单含当时`moa_execution.py`而停，属于已审的新方法注册差异，0模型/0输入导出；原源码与日志保留，修正为明确保留旧锁、核对旧源码冻结副本并单列唯一已知差异，其他保护锁仍严格一致。修后prepare通过，固定清单及资源快照已保存，真实启动及结果另记。

同预算回放入口经独立13测试、8602项源码/553旧raw及两实际plan核验通过（7.281秒）；root另核两plan hash，允许实际CPU回放M5后M4，输出新存`sampling_replay_execution/replayed_reference/`。固定旧逻辑v2+RU参考身份、各121输入、计划122/123 draw；M4原d00063 seed42截断必须原样停止，不填补后续缺失、不重采。该成本参考不等于新简洁提示v3的同预算对照，需后续另作资源重绑定，不能改名。此时尚未完成实际目标回放或评分。


**固定真实smoke验收与剩余开发启动。** GPU2的M4/M5各6/6完成，12新聚合337295输入/6576输出token、275.448模型秒；36旧专家回调328514/5730token、159.065模型秒单列。M4 d00002本版本363输出token、M5同题527，两者完整通过原合同，旧v2重复解释截断仍保留。没有改max_tokens、温度、seed或补闭合；旧raw回放不充作本版本生成。627项真实入口验真确认消息/schema、完整vLLM采样、RU grammar、实际模型、费用、原生解析及清理均一致，另277项独立来源/终态绑定通过。108生产锁及1199个历史保护文件/制品未变，唯一此前已审的分派版本差异保留旧源码副本，不伪称旧生产hash全同。证据：固定12收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/smoke_receipt.json`）、实际入口验真（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/live_independent_check.json`）。

新外部扩展helper在原已验收版本基础上只改明确方法身份、相应CPU状态名和6+115分区，29项无评分回归30.249秒通过；manifest分区、已完成smoke、原专家、durable事件与参数绑定守卫保留。全体121题按原顺序去除本版本固定6题，M4/M5各115，合230；完整门重新通过并确认资源后，在GPU2启动exec session21816，记录于扩展启动（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/extension_launch.json`）。首个非预期错误后停止后续题与后续骨干，不自动resume。此段仅为启动记录，尚未组装完整主结果、评分、采用或进入独立评测。

**扩展首错停止与只读诊断。** M4先完成46扩展题，第47题d00051聚合ordinal6返回length/2048；首错时47提交/47完成/0在飞，169旧专家回调单列。M4扩展46完成/1失败/68未提交，M5扩展115全部未启动；合固定12题，完整242分母为58/1/183，M4 52/1/68、M5 6/0/115。CLI退出1，引擎shutdown返回0.236秒，runner墙钟600.786秒；GPU2释放，未触碰其他GPU作业。失败inference_started=true、failure_type=output_truncation、semantic_result=unavailable、method_score=not_scored，不算答案错误、不删分母。

本版本合59新聚合952561输入/23872输出token、741.896模型秒；205旧专家回调1069888/37437token、864.530历史模型秒另列。派生的原入口核验2435项通过（14.499秒），逐项核参数、原生parser、原raw/grammar、来源回调、首错、费用和释放；只连接已关闭库的私有副本，原制品不变，独立审阅另记。全242逐题状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/full_scope_status.jsonl`）与完整分母收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/full_scope_receipt.json`）没有拼接不同方法或删除未完成题。

独立终态核验另2091项通过（4.691秒）：47次聚合完整逻辑/物理/服务入口参数、46次成功parser与d00051原截断、169条旧来源回调、完整58/1/183、M5未启动和释放均一致；只读1个私有immutable库，0生成/分词/grammar/评分。独立核验脚本首版将实际not_submitted_after_error误写成not_submitted而停，初版代码/log保留，仅修核验枚举，未改run。见独立终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/extension_terminal_independent_check.json`）。

实际tokenizer原响应诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/extension_truncation_diagnosis_corrected.json`）：原raw 10535字符，实际2048token，可见文本重编码2046；停在第一个step_by_step_thinking字符串，没有完整值字段，答案与3项决策均未开始。646字符/独立124token段落出现11次，66句片段只有12种。题面1340字符、实际输入7538token，不是大数组或仅缺闭合；没有可信有限继续token估计。该版简洁提示未在完整开发范围解决重复稳定性，不加预算、不恢复JSON、不续跑或评分。M5同题未提交，不为比较另生成。

首次诊断误把旧A3的原生字符串用list(native)标成对象keys；初版脚本/报告/log保留，仅修诊断引用元信息为native_type=str、keys=null，未改变任何预测或失败。诊断沿用了saved_F_native_reference字段名，但实际source_owner=A3，以真实来源为准，不能写作F结果或替换聚合答案。追加514项独立核验通过（0.608秒），重数242输入/59新调用/205旧回调、字符/重复片段和元信息修正；token数明确复用原CPU tokenizer证据，没有重新生成或分词，见全分母及诊断独立核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/extension_diagnosis_independent.json`）。终态1357文件保护复核通过，含1199历史制品、155当前源码/测试快照及108生产文件；149是含外部采用源的完整执行锁，计数字段首版标签已单独留存并澄清。先前全部失败及正式v5/评分保持，当前候选未采用。

**阶段交付。** 总收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/receipt.json`）与根交付核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/root_delivery_check.json`）绑定33项关键制品、108生产源码，全部通过。此前GPU2释放后又有其他任务使用该卡，未触碰其进程；本阶段没有活动模型session。属于明确新候选的真实扩展负结果和可信交付，整体目标仍active；没有把58条前缀作为完整主结果，未开始共同冻结或独立评测。

<a id="sampling-reference-replay-20260923"></a>

### 固定v2参考的真实旧采样CPU回放完成

13项合成回归、8602项独立入口与计划审阅后，两个实际目标回放各执行一次：M5 121完成、122历史draw；M4 63完成、d00063 seed42原2048截断1条、后57未提交，65历史draw。每骨干原121分母保留，失败inference_started=true、semantic_result=unavailable、method_score=not_scored；未修复、跳过或重采该响应。新专用SQLite按固定顺序先写started再读原响应，原/目标请求hash、完整native辅助字段、原物理事件及真实started/finished均保存，费用独立为historical_sampling_replay；没有调用模型/原生评分或把历史时间改成当前CPU时间。

两骨干合187历史物理调用770961输入/52254输出token、1351.896历史模型秒；本轮新增模型/token为0。原共享专家成本不计入此采样账本。实际目标终态经5109项独立验真（12.203秒），以旧4＋新2个已关闭库的私有immutable副本查账，原库零连接、原run文件hash不变。M5完整native投票和最早获胜完整输出、M4首错计数/无后续尾部及所有raw/双hash/成本一致。此为真正执行目标CPU回放，不再只称可映射；但M4主结果仍不完整、不评分为答案错误。证据：最终收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/sampling_replay_execution/replayed_reference/final_receipt.json`）、独立终检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/executor_preparation/sampling_replay_execution/terminal_independent_review/receipt.json`）。

本身份仍为旧逻辑v2+RU参考。新简洁提示v3资源表另在NS/control_reference_preparation按完整242实际tokenizer请求准备，每题增加107输入token，但原生采样k/seeds/完整请求未变；要关联新参考必须提供独立映射收据，不能改写或重命名本批v2结果。没有读取新聚合输出长短/正确性决定k，预算上限比较不等于完全相同的已实现计算成本。

新v3参考资源表完成5044项准备检查及5481项独立核验（分别7.440、8.436秒），190来源hash保持。两骨干121题的聚合输入预留分别1640846/1626948 token，均较原参考增加12947（121×107）；原生采样固定draw总数仍123/122，完整请求/profile逐项相同。当前仅资源规范与复用绑定准备，0模型/新增分词/质量评分，不把同上限写成实际费用相等。证据：新参考验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/control_reference_preparation/independent_check.json`）。

**新参考的显式复用绑定完成。** 在独立replay_reuse_binding目录新增242输入索引与187条唯一历史物理调用分配表，逐题证明新v3参考与旧v2实际回放的k/seeds/完整native请求/profile相同，保留原请求、旧target、新reference三种hash及原native/辅助字段、时间、费用。源结果永久保持native_sampling_reference_reason_codes_v2_crossfield_v3_v1身份；v3只是资源参考关联，没有创建新结果或改名。本轮0模型/分词/评分/SQLite连接；10项边界回归通过，准备18.592秒，249来源前后不变，109个工作区保护项明确为108代码/config加核心计划。

另8761项独立核验通过（11.745秒）：242=184原完成+1原失败+57原未提交，187个唯一draw计770961/52254token、1351.896历史模型秒；M4 63/1/57和d00063 seed42首错、M5 121/0/0均保持。多份分配视图不能重复累计同一批旧支出，不跳失败补draw，仍不能称完整双骨干对照或实际费用严格相等。证据：明确复用manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/control_reference_preparation/replay_reuse_binding/manifest.json`）、独立绑定核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/control_reference_preparation/replay_reuse_binding/independent_check.json`）。

<a id="multiexpert-cache-feasibility-20260923"></a>

### 未采用A1缓存参与多专家实验的CPU可行性

为检验核心计划要求的实际多专家证据使用，仅在独立证据包开启原Router的两个显式实验门进行CPU审计，生产默认与采用状态不变。各121合法输入选择分布均为A2+A1 9、A3+A1 8、A1+F 12、仅A1 82、仅F 10；双选择各29题，其中程序引用/范围审计可接受两个证据所有者的M4/M5分别22/18题。该数不证明医学互补、最终采用或成绩提升。A1 r5原生可用91/60，原不可用30/61与完整分母保留，不根据质量挑题。

373条原A1调用及242提议走当前原入口回放，除明确的准备计时外行为一致。初次539检查中4个来源差异（两骨干各涉及adapters.py和schema_compat.py）原样保留；后续1512项源码/实际请求核验说明：adapter新增可选None参数未被r5使用，schema新增其他方法分派，r5全部373请求的旧/当前guidance保持逐字一致。旧冻结源码hash与旧plan绑定，原差异收据没有覆写成全通过。缓存前缀加首轮2048预留在242题均满足原预算，但双专家最多112/102项决策，实际输出长度及新grammar入口仍待验收。

生产缓存入口目前仅接纳A2/A3/F；A1旧plan的真实expert为A1_v2_codes、外层角色A1、真实候选r5，不能简单改名接入。下一步限定为包外实验reader/backend与CPU回归、严格来源证明和双门传播，0模型/0评分，当前没有放行多专家正式推理。最终CPU可行性收据6项通过；辅助汇总脚本首版读错成本字段的日志保留，改为完整引用原成本结构。证据：准备边界与制品导航（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/README.md`）、来源差异说明（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/source_drift_review.json`）。

**独立实验缓存入口交付。** 包内ExperimentalSavedExperts与ExperimentalReplayBackend已实现，完整绑定当前input/budget、双实验门、真实A1_v2_codes/r5身份、原来源/profile/顺序及全部提议字段。复用现SourceJournalBackend；模块没有任何模型工厂入口，连aggregate也明确拒绝。A5和A3编辑源不能进入。原A1不可用记录、cost及辅助字段逐值保留，生产与默认路由不改。

首版12测试后，实际CPU前缀回放完整242输入、300个被选提议、631旧回调（373来自A1），787项通过、216.253秒，0聚合/新模型/评分。M4/M5旧资源332/299调用、3289848/2931698输入token、138405/138781输出token；费用只作历史方法资源。前缀输出不是最终聚合答案。两个A1实验门会在82题将F主路径替换为A1，并非仅增加专家；其中A1独选且原生不可用13/40题，未补答案、未删分母，未来实验必须如实报告此配置身份。

根独立审阅发现外层durable plan.method未与来源骨干绑定；原完整CPU回放实际使用了正确骨干，缺口只在守卫。保留10项修前源码/证明/测试/全前缀制品快照，仅增加一条method相等检查；原审阅对完整cached_sources的疑虑随后纠正，因为基类已有digest守卫，没有重复实现。修后14测试29.972秒通过，错误骨干及篡改proof/budget在0回调前拒绝；来源证明显式重建，旧锁与原证明不覆盖。全631回放明确复用修前正确scope证据，AST证明除构造守卫外不变，没有冒称重新回放。包内9项收尾与根211项源码/来源/修复审阅通过。首前缀脚本SQLite audit hook误将bytes当str的启动失败亦保留，修正仅路径解码、当时0回调。

该CPU缓存包可用于后续明确实验入口准备，实际多专家请求/grammar、共享预算与追加检查生命周期仍待验收，本轮未生成新A1或多专家聚合。见reader验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/reader_validation_receipt.json`）及独立限范围接受（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/root_reader_acceptance.json`）。

<a id="single-agent-role-capacity-20260923"></a>

### 同工具原角色配置提案的容量阻断（未推理）

对此前只写为PROPOSAL_ONLY的same_tools_single_agent_adopted_role_profiles_v1完成静态审阅，41来源hash保持，0模型/分词/评分/SQLite。现r2所有阶段实际共用readout后端，stage仅留trace，不能只换配置或按kind猜角色。按完整原facts配置接线时，已有真实tokenizer收据的d00000参数请求M4/M5为18796/19835输入token，加原2048输出预留达20844/21883，均超过facts原16384容量。相关完整prompt渲染代码与旧冻结版一致；这不是可忽略的默认字段差异。

新提案另须显式逐角色decoder：A4 M4原普通guided JSON、M5无guidance，不能默默沿用r2统一bounded参数grammar；原严格单agent parser也不等于旧R4解析行为。facts温度变原0及角色引擎容量均为新控制身份变化。原r2的M4 d00012/M5 d00073 code_view_2截断完整保留；角色接线不修复这两条生成错误。原46条CPU检查仅每骨干6题加生理fixture，不构成新角色或全121验收。

因此该未运行提案保持not_ready。已按用户重大差异需询问的边界，询问保留旧负结果暂缓该提案，或另立紧凑且语义保持的工具输入新版本；未得到回答前不改prompt/容量/输出预算，也不启动该路径。其他缓存准备与终态诊断继续，不保持整体暂停。证据：具体差异、来源和最小实现边界（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/control_alignment_preparation/adopted_role_profile_preparation/README.md`）。

<a id="multiexpert-request-preflight-20260923"></a>

### 多专家缓存到聚合请求与有限补查流程的CPU验收

继续已授权的无模型准备：使用已验收的包外A1缓存reader、原Router两个显式实验门、原聚合v3合同及0.7/42/2048参数，对两骨干各121输入生成首轮与check_used=true的实际请求，走真实NativeBackend.prepare、已安装tokenizer/xgrammar与原parser。后者只是在首轮audit上关闭追加检查的静态模板，不能当作获得新专家结果后的第二轮验收。独立并行调用原execute，回放历史专家前缀，在聚合count_tokens处捕获以核验首轮可达性；不生成聚合响应、不改生产108文件、不重跑专家、不评分。A1无native/semantic_invalid逐值保留，只有原output_schema_invalid规则决定run_expert是否抛错。

证据分别在实际请求预检包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/request_preflight`）与控制器可达性包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/controller_reachability_preparation`）。完整双骨干首轮、静态请求和独立复核现已结束；这些CPU结果不能放行真实聚合。此前v3重复截断负结果、A1/A5未采用、A2待决和A3编辑模型暂停保持。

**原控制器前缀实测完成。** 两骨干均121/121走到真实execute构造的aggregate.count_tokens入口，合631旧回调（332/299），256.767秒CPU墙钟。捕获后停止，不调用聚合tokenizer/parser/模型，不创建成功原生答案。每骨干150个选择提议，schema_invalid均0、semantic_invalid为3/0、无native为20/51；原audit拒绝相应20/51提议，A1独选且无native的13/40题仍在分母。程序没有把semantic_invalid或None改称run_expert首错，也没有修改其原schema停止规则。每骨干82题有尚未用过且缓存覆盖齐全的F可追加，另外39题无可追加owner；全部五种操作各核对至多一次限制，每骨干605次第二检查拒绝。这个菜单是CPU假设冲突查询，不是模型真的要求追加检查，更不是已完成第二轮。根独立保存记录/代码核验4738项通过、1.316秒；见入口实测收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/controller_reachability_preparation/receipt.json`）和独立限范围核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/controller_reachability_preparation/root_check.json`）。该入口捕获与下述完整grammar/parser预检分别验收，不互相代替。

追加预算补表仅使用原A1/F请求实际资源和两轮各2048预留：164条可追加路径均在原16调用/400000输入/32768输出/4工具上限内，最多10模型请求，M4/M5最大输出预留6693/7871。两轮聚合输入剩余额度最低337924/333351，按两次131072上下文的宽松上界亦够用；此补表本身没有检验实际第二轮prompt或parser生命周期，后述有限场景也不覆盖全部164条路径。首版新审计误假定所有F调用max_tokens=2048，遇到每骨干16条原score请求max_tokens=1后断言停止；初稿与日志保留，只改审计读取原kind/max_tokens，旧参数和源均未变。见补查预算收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/controller_reachability_preparation/additional_budget_receipt.json`）。03:19交接时静态预检为154/484请求且无错误，健康CPU session25246继续；其后完整终态如下。

**全量请求预检终态。** session25246实际退出0；242输入、484首轮/静态关门请求、3766个真实grammar及原parser正反fixture全部通过，其中1210正例、2556预期拒绝，1369.714秒，185来源锁（含108生产）保持。M4/M5首轮实际输入token最高97282/104269，最大决策数112/102；全部原上下文与共享预算检查通过，这不证明模型能在2048内稳定生成。13/40题没有可接受原生提议依旧完整保留；额外检查后的audit/request另由下述有限生命周期测试验证，不能拿本批静态check_used模板代替。0新模型/A1调用/评分；历史332/299回调对应3289848/2931698输入、138405/138781输出token和6485.907/5407.398模型秒，均为既有支出，不计为本轮新推理。见全量收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/request_preflight/full/receipt.json`）。

独立终检39835项通过（42.667秒），203来源前后保持：242个首轮完整请求与原execute捕获逐值、按键顺序hash一致；484请求的引擎配置及去guidance后的全部采样字段与旧NS同骨干配置一致，服务入口按真实FINAL_ONLY转换后比较。仅补4个边界实际prepare/tokenizer和108次原parser复核，没有重复全量分词。完整原生字段、原A1不可用状态、合成fixture标签、历史成本与0新费用均保持；见独立预检收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/request_preflight/independent/receipt.json`）。

**有限追加检查生命周期终态。** 按原输入顺序、route和flags预先选7个固定输入，覆盖可用A1、无native A1、无可追加owner和原semantic-invalid提议，执行13个独立CPU场景、共19个输入槽。聚合的19条响应均为明确标记的合成数据，通过原execute/run_packets、原parser及真实prepare/tokenizer/grammar；没有模型生成。7个正向场景完成，其中4个在完整首轮解析通过后真实回放旧F，重新构建含F的audit并关闭第二轮补查；另外3个没有可追加owner，保留not_available。6个注入截断、语义无效或二次补查的负向场景均按原分类首错停止，真实聚合ordinal为2或6，随后6个sentinel输入均0提交。此为有限合成流程验证，不是模型主动协作或全242题二轮成功。执行132.509秒，见场景与成本收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/additional_check_lifecycle_preparation/attempt2/receipt.json`）。

初次fixture使用json.dumps默认结构空格，与现compact grammar不符，首场景在grammar断言处失败；随后包装又因合成调用计数未隔离而报错，当时0完成场景、0模型，24.217秒。原脚本、日志、库和失败输出保留。修订只作用于包外fixture的紧凑序列化、合成记账及显式标签，另存attempt2，未改生产prompt/schema/parser/参数。原RunJournal保留4提交/3完成/unknown=1；SourceRunJournal与初次status保留1提交/0完成/unknown=1。另以禁止模型构造/生成的CPU工厂证据说明实际新模型为0，不把原unknown静默归零或隐藏原失败。参见首次失败（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/additional_check_lifecycle_preparation/diagnostic_failure.json`）及原始与合成分类账本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/additional_check_lifecycle_preparation/terminal_counter_receipt.json`）。

attempt2共44次历史来源回调，重复场景去重后为26个既有物理请求：135413输入/10284输出token、404.464历史模型秒；合成响应的token长度与CPU时间单列，不算新推理费用。独立终态1409项通过（4.897秒），289个非SQLite来源保持，重放全部19条原parser结果，核四个正向F新audit、六次首错及后续0提交、原生提议逐值保留和原unknown=1。该独审没有读取SQLite字节、连接数据库、重跑tokenizer或场景；14个本任务库hash明确引用既有终态收据，未冒称重新读库。见生命周期独审（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/additional_check_lifecycle_preparation/independent_terminal.json`）。两项CPU验收收尾后释放本次108生产源码锁，旧proof/制品保持原版本；没有据此解除v3生成负结果、采用A1或放行新模型。

<a id="freeze-evidence-inventory-20260923"></a>

### 已有控制与开发范围的冻结材料绑定（仍未冻结）

为避免旧草稿把已完成对照继续列成空值，新增包外证据清单，原草稿、结果及生产代码保持。仅从既有manifest生成40家族/121输入的已暴露开发范围元数据，绑定两骨干强旧和纯top-1的原plan/status/输入hash及真实variant。全部16个核心控制槽和五专家槽保留；A1仍关闭、稳健槽仍是真实F，其他控制、共同采用决策和独立范围不补造。7项来源清单差异全部记录，其中6项为持续主记录的固定快照定位，1项为执行状态配置的当前观察，不改写旧历史锁。

原validator未修改：两骨干top-1现有scope/status绑定通过；强旧原status没有failed字段，新收据保留null，validator仍拒绝这一元数据缺项。此缺项不等于原强旧实验失败，其121完成与原评分继续有效。总体仍not_ready：没有冻结时间，缺共同决策/其他控制/独立范围；未读取独立数据、未评分或推理。生成时50个来源与108生产文件保持，后续主记录正常更新不改变已存固定文档快照。见证据清单说明（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/evidence_inventory_20260923/README.md`）、新草稿（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/evidence_inventory_20260923/current_unfrozen_draft.json`）及实际拒绝报告（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/evidence_inventory_20260923/validation.json`）。

后续独立元数据审阅303项通过（0.410秒），133个实际检查来源前后保持；未重新运行准备程序或validator、未读取链接的评分文件/独立数据。继续保留强旧原status缺字段及not_ready结论，见独立收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/evidence_inventory_20260923/independent_check.json`）。

<a id="aggregation-evidence-first-design-20260923"></a>

### 先写证据决策、后写完整原生答案：一个新方法假设的静态审阅

针对v3的d00051在首个自由解释字段重复11次、2048截断，提出一个独立待实现候选evidence_first_concise_native_v4：保持完整逻辑/native schema、原parser和0.7/42/2048，仅显式增加外层生成顺序说明，并用单独decoder输出decisions→unresolved_conflicts→additional_check→native_answer。它改变生成条件，是新方法假设，不是兼容性修复，也不保证解决重复；内部原生解释仍可能截断。截断前完成审计前缀依然不能评分或提前执行工具，须整条原生JSON验收后才能按原规则追加一次检查。

只读484份已存grammar显示，不能只换prompt或root一行：四个最外层属性还有依赖旧顺序的lookahead，需同步精确重建其后继，同时保持native内部语言及RU/check依赖。审阅纠正了最初root-only草图；尚未实现、编译或运行该候选。建议固定每骨干8题（原6+d00051+首个有errors原生字段的d00003），全局首错停止；新prompt/token预算参考须实际重算，不能预设旧k不变。18来源保持、0模型/分词/grammar编译/parser/评分/数据库连接。见完整设计边界与预定验收建议（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_design_review/README.md`）。旧v3失败和对照身份不变，当前不以此审阅放行模型。

**后续隔离CPU原型启动。** 在evidence_first_preparation（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation`）实现薄提示/parser封装和独立顺序decoder，尚不注册生产分派，避免改变正在运行的MC预检108源码锁。完整逻辑schema和原生内部grammar保持，仅外层root及四个外层属性的后继lookahead改变；旧v3与RU方法保留。实际空决策合同仍由原schema_for生成并测试，不手动删决策而遗留冲突ID。组件检查使用真实xgrammar EBNF matcher与原parser、明确合成响应；TokenizerInfo([])仅检查字符串语言，不当作实际服务tokenizer预检。已启动8项组件测试，包括484原开发请求的逐字段不变性、正反RU/check组合、原生errors字段、截断拒绝和答案保持/改变都允许。尚未完成测试或真实入口验收，0模型/评分。

同期的[有限追加检查CPU生命周期验收](#multiexpert-request-preflight-20260923)已完成并独立核验，完整过程、初次fixture失败及成本归该小节。该验收沿用原v3合同和合成聚合响应，不能当作本EF候选的入口或生成验收。

隔离组件8项测试已通过（13.690秒），其中逐字段核对484请求，768组RU/冲突/check条件在原顺序与新顺序间保留相同完整值语义；空决策/all-RP、原生errors、Unicode及截断拒绝保留。独立审阅另对484份已有实际schema/grammar应用外层转换、检查20426条非root规则，确认改变仅root及3/4个外层后继；native内部、属性body及RU/check helper保持。总22111项源码/hash/结构检查通过（0.914秒），不重复编译或分词、不冒称真实服务入口。独立checker初稿有一个解析前括号SyntaxError，0检查/0读写，修正仅checker，已在收据说明，候选代码无更改。见组件收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/component_receipt.json`）和独立审阅（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/independent_component_review.json`）。已准备显式注册diff及入口回归，但生产108锁释放前不应用；实际双骨干服务预检、资源匹配及固定smoke仍待执行。


**显式注册与入口回归启动（03:44）。** MC全量预检及追加检查生命周期的来源锁均已释放。独立注册审阅确认24个既有method/decoder组合行为保持、新候选只接受显式v4方法＋v4顺序decoder；随后应用两处注册改动、两个独立模块和两个回归测试，生产来源从108变为110（含测试的完整快照159）。默认路径、旧v2/v3、原生schema/parser、采用配置及历史证据不改。外部原型快照保留，生产副本只修正说明和测试import。新source锁及前后diff见注册包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/registration/application_receipt.json`）。

旧MC的A1缓存proof包含本次两处注册源码，其旧锁仅证明旧版本；不会覆盖旧proof或声称它对新版本仍有效。当前v4固定smoke只准备已有默认A2/A3/F缓存，其原来源proof和全部专家内容保持。当前focused回归session53168运行；其中原生评分桥使用临时合成fixture，不是开发质量重评分。实际tokenizer预检和模型smoke尚未启动，不以注册成功宣布采用。

注册后的68项针对性回归全部通过（47.277秒，session53168实际退出0），含新v4入口、旧v2/v3/decoder、缓存及首错停止。159个源码/测试快照前后未变；临时GPU锁fixture产生ResourceWarning但没有实际模型加载。见入口验收终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/registration/receipt.json`）。下一步固定16输入/32请求、再全242/484实际tokenizer预检；03:45只读资源快照GPU3空闲97364MiB，其他健康作业保持，模型尚未启动。

**固定实际CPU预检完成，全量已启动（03:49）。** 固定两骨干各8题、32个开门/关门请求、480个grammar/parser fixture通过，含12个仅重排外键的历史成功响应；这些历史响应没有记作新v4输出。实际耗时92.349秒，所有原生字段、非guidance物理参数及完整合同保持，固定样本新提示相对v3均增加105输入token；不据固定样本推定全量。110生产锁保持，0模型/开发评分。见固定预检收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/preflight_fixed/receipt.json`）。全242输入/484请求已在session76730启动，保存于preflight_full；此时尚未完成，也不放行GPU。

**全量CPU验收与真实固定试跑启动（04:00）。** 242输入/484请求/7078个grammar与原parser正反fixture全部通过（514.982秒），含12个仅外键重排的旧成功响应，仍不是新模型输出。全234来源含110生产锁保持，M4/M5各121题实际新提示均比v3增加105token；两骨干首轮总输入token1653551/1639653。见全量收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/preflight_full/receipt.json`）。GPU阶段9项有限停止机制测试已通过，固定8题×2骨干，完整242分母保留、原0.7/42/2048、旧专家只复用，任何首错阻止后续输入与骨干。

准备时发生一次根/子任务重复prepare：根session94081退出0形成唯一完整274pins清单，子任务52852在首个exclusive目录mkdir被FileExistsError拒绝，未写输入/manifest、0模型。两者用了同一prepare.log，最终共享日志只留拒绝栈；已明确记此日志限制并另存duplicate_prepare_refused.log，根实际exit0来自工具终态，随后重新验证完整清单。原GPU3在启动前被其他作业占用，GPU2空闲97364MiB；保存原GPU3未启动manifest后，仅将新运行manifest的gpu改2，方法/参数/选题无变化。详见启动前核对记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/gpu_preparation/prelaunch_reconciliation.json`）。接下来启动独立v4固定试跑，不恢复任何旧失败批次，也不自动扩展或评分。

**新提示的同预算参考完成。** 基于全242题实际新prompt长度及已绑定原native请求计数重算，M4/M5各121题均增加105输入token；固定公式得到k变化0题，M4为119题k1＋2题k2（123draw），M5为120题k1＋1题k2（122draw）。旧839个唯一物理请求继续单独计账。新参考输入总量3481610/3381534、调用上限合541/540、旧输出实际＋新聚合预留合332203/331833。它们是增量资源上限，不是已花费或实际成本相等，也不把原采样184完成/1截断/57未提交改名成v4成功。一次CPU准备5.287秒、291来源保持，0模型/分词/评分/SQLite；见资源参考收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/control_reference_preparation/receipt.json`）及逐题资源表（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/control_reference_preparation/reference_resources.jsonl`）。

**真实固定16题全部完成（04:08）。** session35587实际退出0，M4/M5均8完成/0失败/0未提交；原固定题包括此前d00002/d00051截断点与原生errors的d00003。两引擎均按原shutdown显式释放。新聚合16调用、383797输入/8631输出token、324.249模型秒；旧专家54历史回调、391346输入/7539输出token、204.265历史模型秒单独计，不是新花费。完整242分母当前16完成/0失败/226未提交，未评分/未采用，真实entry/raw/parser及成本终检正在进行。

利用等待时间准备剩余113×2执行器（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/extension_preparation/run_remaining.py`），3项CPU停止门回归通过（1.455秒），保留早错不发另一骨干、资源不足0提交、不完整退出0拒绝、完整242及未知提交状态。此时只准备代码，没有创建extension_run或启动扩展；必须先取得16题真实入口完整验收，再由根单独执行，旧8题不重跑。

**实际入口终检通过与剩余范围启动（04:13）。** 新checker首次41502退出1，原因一为错误将audit_hash自字段纳入digest；原因二为16题中4题program_checks[0].elapsed_seconds与静态预检不同，带来合法派生hash变化。全部proposals（含cost/native）、decisions、support_paths等逐字段一致。修正仅checker：两audit分别自校验，只按具体CPU耗时字段比较差异，再从真实audit重建模型请求并核对实际引擎；第二次60934退出0，完整请求/原parser/原生答案、旧来源、分母及新旧成本均通过，未知用量0。原失败、4个原/现值、脚本前后及日志见修复收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/check_fixed_live_repair_summary.json`），实际终态见16题验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/fixed_live_receipt.json`）。没有改模型输出或重新生成。

扩展prepare session93407退出0：两骨干各121去固定8后剩余113、保持原输入顺序和完整预算，source/缓存/全部原实际验收绑定。将用GPU2顺序运行M4→M5，任一首错停止另一骨干和后续题；原16完整保留，整体242分母。不存在自动恢复、重采样、预算增大或原专家新调用。见扩展manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/extension_run/manifest.json`）；此处是启动记录，尚无扩展结果或完整开发质量结论。

运行交接：根已唯一启动extension session50796（GPU2）；不重复命令、不改110生产源码或旧16制品。入口摘要更新的首个辅助脚本因沿用旧导航文案断言而中止，主记录已先写入；核读当前README锚点后补齐，未影响实验配置或运行。扩展终态、逐题费用与完整开发评分仍待完成。


<a id="aggregation-evidence-first-terminal-20260923"></a>

### v4扩展首错终态与重复解释诊断

扩展M4子进程exit1，原session50796已结束，原shutdown返回且GPU2回到97364MiB可用。M4剩余113题为15完成/1失败/97未提交，M5剩余113题完全未启动；与原固定16合计242题31完成/1失败/210未提交。失败是d00021的output_truncation：inference_started=true、semantic_result=unavailable、method_score=not_scored；不当作答案错误、不删失败分母、不恢复旧run、不增加2048上限。首错时新模型attempted/submitted/completed各16，in_flight=0；61次旧专家缓存回调另记，后续题与另一骨干均未提交。

独立扩展终态checker先通过7项有限CPU回归（0.768秒），之后只在writer关闭后运行一次，session74661退出0、14.904秒。逐字段核对当前实际请求与全范围preflight，核对引擎采样、grammar、原parser、完整旧expert缓存、错误位置、停止尾部及费用；未连接SQLite、未重新分词/模型调用/评分。旧16收据及来源前后保持。见完整242终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/full_scope_receipt.json`）和checker交付（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/extension_preparation/checker_delivery.json`）。这里是运行证据核验通过，实验状态仍stopped_on_error，不代表方法成功。

扩展新增16聚合，303421输入/5955输出token、194.699模型秒；包含原smoke后合32新聚合、687218/14586token、518.948模型秒。115次历史专家回调787539/20173token、508.610历史模型秒单独列账，0专家重新生成、未知费用0。没有把缓存当免费新调用。因为完整开发范围未完成，未执行8+113结果拼接或原生主评分，原计划的完整结果汇总准备随该门停止。

**完整失败trace诊断。** 根session94148一次只读运行退出0，8.255秒，使用原M4实际tokenizer但不加载模型，不读取gold/评分/数据库，不写回原输出。生成2048 token、9902可见字符。最后完整字段为additional_check（null），之后停在native_answer.step_by_step_thinking字符串内，answer_choice尚未开始。三条decisions完整，决策值对象35字符/20个独立分词token；unresolved_conflicts为41字符/21token；additional_check为4字符/1token。未闭合native_answer为9748字符/1990token，其中解释片段9722字符/1983token。分字段独立分词不保证相加等于模型实际2048。

解释中108个句段仅22个不同句段，精确重复86次，最常见一句出现40次；没有重复JSON键或决策表循环。该题题面1042字符、请求7313输入token、仅3个决策ID；本批23条完成M4输出的题面104–1602字符、决策2–57个、输入6116–97387token、输出142–2031token。因此失败并非异常大的决策表；分类为生成稳定性/重复原生解释。语义和原生答案尚未完成，不能只补闭合或按审计前缀评分，没有有限的有用继续token估计。M5同题聚合未提交，不为诊断生成对照。保存的旧A3提议是独立历史答案，不用于替换失败聚合。见结构与长度诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/extension_truncation_diagnosis.json`）、只读诊断代码（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/diagnose_extension.py`）与日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/extension_truncation_diagnosis.log`）。当前不重试、不改模型/提示/预算，只允许另行明确身份的稳定性方案审阅。

**A1缓存来源绑定CPU完成。** 另一路在/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/evidence_first_source_binding_preparation显式生成新proof，保留旧proof及methods字典不变。旧180来源锁精确仅两处聚合selector变化，均对应本次EF注册before/after；原A1 prompt/config/parser/输入/输出/373条历史回调内容不变。现原ExperimentalSavedExperts只构造读取两骨干各121缓存，921项核对、31.652秒（session98323退出0），277来源前后保持。旧373次A1回放及242题原控制器前缀验证明确继承既存证据，本次0回调重放/0grammar/0分词/0模型/0评分/0SQLite。原native不可用30/61（含各10unsupported）保留；A1未采用、默认关闭，不声称v4多专家请求或生成已验收。见来源绑定说明（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/evidence_first_source_binding_preparation/README.md`）与收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/multiexpert_cached_preparation/evidence_first_source_binding_preparation/receipt.json`）。


**后续固定采样稳定性方案，仅审阅。** 一次本地vLLM 0.8.5源码审阅得到待验证候选`aggregation_v4_output_frequency_0p1_v1`：只对明确选择的新聚合采样固定frequency_penalty=0.1，两骨干同值，原v4 prompt/schema/parser、0.7/42/2048及旧专家不变。0.1是预先固定试值，不经搜索、不递增到成功；属于新采样方法，不能当恢复采用配置。当前NativeBackend不转发此字段，未来须显式独立入口并验收到真实engine，不能只写配置。源码显示V1先grammar mask再penalty，有限扣分不解除非法token屏蔽，但会影响整段JSON的原因码/数字/医学词，不能称只删重复或保证语义不变；V1拒绝逐请求自定义logits_processors，暂不做字段内硬ngram禁令。

拟议验证顺序为实际参数与CPU logits回归、原parser和正式请求预检，再单独决定真实smoke；若执行，固定每骨干原8+d00021共18个已暴露开发输入、首错跨阶段停止、旧expert不重生成。当前只完成方案，0实现/0模型/0grammar/0评分；未启动这些检查或新推理。未来协作比较还需同采样政策的同预算/同资源控制，旧默认采样不得改名。原默认每题单专家、A1未采用的限制保持。见有界方案及本地代码依据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_review/proposal_only.md`）。根另核查110生产锁与诊断来源保持，所有本批模型进程已结束；共同冻结、核心对照与独立评测仍未完成。


<a id="aggregation-fixed-frequency-cpu-20260923"></a>

### 固定输出频次惩罚：隔离CPU实现启动

按既定唯一0.1试值实现隔离候选。为避免向通用适配器增加默认覆盖和额外参数轴，完整方法使用显式contract `aggregation_v4_output_frequency_0p1_v1`＋decoder `aggregation_evidence_first_frequency_0p1_v1`配对；底层仍原v4 prompt/schema/parser/grammar，提示字节和0.7/42/2048不改。新metadata明确采样身份和0.1，物理SamplingParams单独构造并记录唯一频次差异。当前仅外部原型，110生产源码不变，不启动模型或沿用旧失败身份。CPU工作包含全484逻辑请求保持、双骨干真实prepare/同步ingress比较、原parser完整字段/截断拒绝，以及实际vLLM penalty数值行为；来源与代码见准备包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation`）。


隔离原型5项测试通过（19.817秒，session65812），全484请求中只有显式采样身份改变，12次双骨干真实prepare/同步ingress比较仅frequency从0变0.1。实际vLLM penalty另9项CPU数值测试通过（0.040秒，导入合7.725秒，session85628），CUDA未初始化；原prompt-only token、padding/batch计数、负无穷mask和唯一合法重复token保持预定行为。随后两selector的临时映射66项比较确认35旧配对及7旧decoder结果保持，才应用两处注册和两个独立模块，生产110→112。正式入口16项回归通过（22.819秒，session74741），含原v4、缓存原提议、原生评分桥合成fixture及首错停止；未重跑开发质量评分。见注册验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/registration_receipt.json`）及实际penalty验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/penalty_kernel_receipt.json`）。

响应用户对GPU空闲的进度提醒，后续仅针对固定每骨干9题做36开/关门实际入口预检，然后直接进行预定GPU2试跑；不再串行重复全484的grammar/parser检查。未改变的全范围消息/schema/预算仍有逐请求一致性证据，但本次预检只放行固定18题；扩展须单独确认完整smoke与实际入口。其他三张卡已有健康作业，不抢占。旧失败不恢复、A2/A3/A4不重生成，A3编辑仍暂停。


**固定CPU预检通过，GPU试跑已启动（04:45）。** session25945退出0，82.578秒，两骨干各9题的36开/关门实际tokenizer/xgrammar请求及108个原parser正负fixture通过。所有实际prompt、schema、grammar、输入token与原v4预检一致，物理及同步ingress仅frequency_penalty=0→0.1；新完整方法身份和源锁单独保存。3项外部停止门假子进程测试通过（0.085秒），早错/资源不足/退出0但部分完成均阻止M5，完整242分母保留。根唯一启动session71118，GPU2原M4引擎04:45:25就绪；随后仅在M4九题完整且引擎shutdown后切M5。记录与资源参考工作在GPU期间并行，不重复全量grammar核验。见固定预检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/preflight_fixed/receipt.json`）、正式运行manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/live_run/manifest.json`）和运行状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/live_run/stage_status.json`）。保持112生产源锁，不恢复旧失败、不新增专家请求、不评分本次未结束试跑；完整终态待补。


GPU运行期间已完成固定频次政策的同预算资源绑定（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/control_reference_preparation/receipt.json`）（session77429退出0，4.880秒，324来源含112生产锁前后保持）。242行原k保持，M4/M5为123/122draw；839个旧专家物理ID及成本逐项不变，参考输入3481610/3381534、旧输出实际＋新预留332203/331833。484个新逻辑请求与旧v4仅revision差异的证据明确来自已执行测试与静态绑定；36实际服务预检另核，没有重跑484物理预检。新native sampling入口尚pending，实际新请求/hash/结果均null；旧默认frequency=0的187次采样不能变成本0.1候选的匹配结果，也没有读取或导入这些旧响应。本项0模型/分词/grammar/评分/SQLite，只是成本参考准备，不是已完成对照。


**固定18题完成及剩余224题启动（2026-09-23T04:58:27+08:00）。** 原session71118退出0，两骨干各9/9完成；根终态验收session20337退出0，核对实际引擎frequency=0.1、完整原请求/原parser/原生字段、缓存来源、首错策略和新旧成本。新增18次聚合397957输入/6965输出token、294.219模型秒，0专家重生成；全242分母为18完成/224尚未扩展。见实际入口收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/fixed_live_receipt.json`）。这不是开发质量评分或采用结论。

扩展执行器3项有限停止回归通过（0.092秒）；prepare session5924退出0，原每骨干121题去固定9后保持剩余112原顺序、原预算和缓存。根唯一启动session14716，GPU2依次M4→M5，首错停止后续请求与另一骨干，不重跑原18题、不重试或加预算。见扩展manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/extension_run/manifest.json`）与阶段状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/extension_run/stage_status.json`）。用户再次指出CPU串行工作延误GPU衔接：此后已通过的全量grammar/分词不重复，GPU期间只并行准备必要终态检查和未完成控制。此时资源实测GPU0/2空闲，GPU1/3有其他作业；GPU0可用于另行就绪的独立对照，当前不挪动其他作业，也不因卡空闲重跑有效专家。


**GPU期间的交付准备与历史计数补证。** 扩展终态checker已复用原实际入口/成本/首错检查，少量适配自检通过（2.135秒，0新分词/grammar）；9+112无损合并入口另通过3项合成fixture（5.149秒，session35180），真实合并和原生评分均等待完整242题终态通过。见合并准备（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/assembly_preparation_receipt.json`）。这两项不改变正在运行的112份生产源或旧专家输出。

强旧控制此前status缺少failed字段，现另由两骨干各121条完整原始输出、原plan全部input_hash及6份原来源锁重算：各121 complete、0 failed、0 not_submitted、0 native unavailable。原status及原收据保持缺字段，新增独立派生状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/freeze_preparation/strong_control_status_from_rows/receipt.json`）明确计数证据，供后续冻结清单引用；不是把缺失默认补0，也未重跑模型/评分。首次辅助脚本误以为旧包装proposal内有input_hash而KeyError退出，旧源码和失败日志保留；修正只读取实际外层row绑定后退出0，失败时未创建输出目录。共同冻结仍未就绪。

本轮再次将两项受影响对照的明确选择发给用户：A2恢复历史原生parser后回放扩展，以及同工具原facts容量不足时是否另立紧凑等价输入版本。回复未到之前只暂停各自路径，GPU聚合与独立采样控制准备照常。A3编辑臂继续暂停。


**匹配频次的原生采样控制启动（2026-09-23T05:08:48+08:00）。** 最小外部入口复用原fixed_sampling的draw/parser/投票/预算/first-error内核，保留原文件；只更换其明确的旧计划身份校验并接独立frequency=0.1后端，不改112生产源。3项必要回归通过（6.018秒）；两骨干固定各2输入、合6 draw的实际prepare/xgrammar/同步ingress和12个原parser fixture通过（20.142秒，session99056），原物理字段仅frequency 0→0.1。固定输入M4 d00000/d00005、M5 d00000/d00101，包含原范围各首个k=2题，按输入/预算而非正确性选择；seed42/43及2048上限保持。

根唯一启动GPU0 session21247，与GPU2聚合扩展并行。当前仅4题smoke放行，原生采样无旧expert缓存调用；旧187次默认frequency采样不复用。完整242预算固定M4/M5 123/122 draw，本次4/6通过真实入口终态后才准备用原2+剩119扩展；首错全停，原失败保留。见固定采样预检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/prepared/receipt.json`）与GPU阶段（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/live_smoke/stage_status.json`）。预算是固定参考资源上界，实际token费用另报，不把同上界说成完全相同实际算力。


**D资格核对单独暂停。** 元数据任务意外阅读到主记录内D的8组强控资格摘要，超出本次范围。已停止受影响路径、保存准确访问记录并询问用户；未打开D逐题/gold/模型结果或改变任何开发方法。暴露沿革完整正文归数据构建记录（本地制品：`/home/data3/txy/docs/data/construction.md#cf-moa-independent-summary-exposure`），开发GPU聚合及采样对照继续；不将已有历史资格审核或本次摘要阅读说成全盲。


**采样真实入口通过，剩余范围接续GPU0（2026-09-23T05:14:52+08:00）。** 固定smoke session21247实际退出0，两骨干各2题/3draw完成；终态核对session64483退出0（3.610秒），6个实际请求/EngineCore接收参数、seed42/43、原parser/完整辅助字段投票及成本一致。实际75563输入/1998输出token、57.655模型秒，0旧专家模型调用，未评分。见终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/terminal_receipt.json`）。

3项扩展停止门回归通过（0.031秒），prepare session77910退出0；根唯一启动session10802 GPU0，保持原4题6draw，按原顺序运行剩余每骨干119题，M4/M5分别120/119draw。完整分母仍242，任何首错停止当前尾部及下一骨干，失败不作为答案错误也不删分母、不续跑或改参数。见扩展准备（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/extension_prepared/receipt.json`）及运行状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/live_extension/stage_status.json`）。与GPU2聚合运行并行；实际扩展费用/完整原生评分待终态，不把预设预算上界当已用费用。


**M4聚合完整运行完成、M5接续（2026-09-23T05:22:01+08:00）。** GPU2的M4扩展112/112 complete、0 failed/0 not_submitted，含原固定9后达到本骨干完整121题。扩展实际记录为112新聚合、1456624输入/35520输出token、982.444模型秒；该成本是扩展部分，原9题另见smoke收据。M4引擎已退出，M5引擎05:20:36就绪、首条新结果已保存，原session14716继续运行。当前不先对M4单骨干评分；完整242终态才执行已准备的原入口核验和无损合并。GPU0采样扩展同时健康运行（已保存M4前73条，session10802），不重试或改变预算。

采样完整原生评分入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/score_complete.py`）已准备，只在两骨干242题/245draw全成功后透明封装原完整native_answer并调用未改score_run；任何失败/未完成在读取offline标签前拒绝，不重建采样答案或更改投票。两项有限门检通过，实际评分尚未执行。真正双专家路径的固定11题CPU入口预检随后已完成，session46624退出0、161.604秒：11个原execute首请求、13个实际栈请求（含2个静态post-F模板）、26个原parser正/length负fixture及47个历史callback回放通过；302来源含112生产源保持，0新模型/评分。A1原None/semantic-invalid及未采用身份保留，尚未放行模型、不重新生成A1。每骨干完整scope的原可见路由为29双专家/82仅A1/10仅F；不得把全242称双专家协作，当前默认单专家聚合也不能借完整运行声称协作收益。见多专家固定准备（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/multiexpert_preparation/prepared/receipt.json`）。


**GPU利用与CPU开销核对（2026-09-23 05:30）。** 用户再次指出CPU工作阻碍进度。只读确认GPU0/2的当前模型日志均为CUDA、Flash Attention与GPU KV，每骨干仅初始化一次；GPU1/3有其他活动作业。M4采样剩余119题/120 draw完整完成，新增487896输入/32144输出token、629.510模型秒，连同原2题构成121/121；M5继续，不等待CPU报告。资源与已保存计数见现场快照（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/resource_observation_20260923_0532.json`）。本次检查不新调用模型、不分词/编译grammar/评分，不中断现有作业。

代码只读检查发现每draw有多次prepare/count_tokens路径，grammar虽按hash缓存，准备和编码仍重复；journal.export每题全量重写截至当前的输出，存在可优化开销。原生采样M4本批总运行703.41秒，其中LLM.generate计629.51秒；聚合M4本批1336.34秒，其中LLM.generate计982.44秒。差额分别73.90/353.89秒，包含初始化、准备、审计和落盘，现有计时不能全部归因于某项CPU瓶颈。前期过量串行CPU预检确实延误GPU衔接；当前继续两GPU并行、复用已有验收。无语义变化的准备缓存和增量导出仅列为后续工程优化，尚未实现；不修改运行中的112份生产源码或配置。依据：cf_moa/tools/vllm_backend.py的prepare/count_tokens，cf_moa/tools/adapters.py预算计数，cf_moa/evaluation/journal.py的export。


GPU继续运行时，对多专家固定入口只做一次0.6秒量级的请求守卫检查：13条已存请求轻量重建逐字段相同；两骨干d00000/d00018共4条A2审计计时增加1秒并重绑audit_hash后，模型request仍相同。计时与外层hash不进入messages，故无需放宽精确请求守卫。11首轮＋仅两骨干d00001可追加F的2个第二轮模板覆盖可达生命周期。0模型/分词/grammar/评分、0生产或准备源修改；尚未放行多专家GPU。


**固定频次候选首错终态（2026-09-23 05:35）。** 原session14716实际退出1。M4扩展112完成，M5扩展40完成/1语义无效/71未提交；连同保留18题，完整242为170完成/1invalid_output/71not_submitted_after_error。首错为M5 d00047、AggregationSemanticError（Empty unresolved conflict），当时本骨干新请求attempted/submitted/completed均41、在飞0；后续71未提交，原shutdown已返回。此失败不归为答案错误、不删分母、不重试、不加预算，不把完整M4当完整双骨干结果。

根只在writer终止后运行一次check_extension.py --terminal-confirmed，session73908退出0、20.690秒，实际请求、引擎采样、原parser、首错尾部、缓存来源及费用核对通过。新增171次聚合、2419212输入/56954输出token、1876.340模型秒；597次历史专家回调及2632524/116679 token、2888.711历史模型秒单列，0专家重生成、未知费用0。未创建完整结果合并或主评分。见完整终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/full_scope_receipt.json`）与终态日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/extension_terminal_audit.log`）。GPU0采样继续，不因聚合失败中断独立对照。

前述性能计时进一步澄清：invocation_seconds从题目循环前开始，包含首题延迟加载模型，但不含此前所有计划核验、设备准入和tokenizer初始化；live_model_seconds是llm.generate包围的墙钟，包含引擎处理，不能称纯CUDA kernel时间。此口径修正不改变成本记录或运行行为。


<a id="frequency-sampling-complete-20260923"></a>

**匹配采样完整评分与对照完成。** session10802实际退出0，两骨干各121输入/157原生映射、74非reference单位、40家族全部保留，M4/M5实际123/122 draw。score_complete.py终态验收及未改原生评分session97752退出0，245实际引擎请求的参数、seed、原parser、完整辅助字段投票、来源与成本一致；0专家重生成。总新输入1032749、输出65459 token、1674.480模型秒（M4为555460/33356/660.625，M5为477289/32103/1013.855）。评分收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/complete_scoring/receipt.json`）绑定原draw与透明评分封装；没有把旧frequency=0采样替换为当前结果。

外部比较入口先通过2个合成门检，再读取完整现成评分，退出0、0.120秒；不重复原生评分或bootstrap。各121唯一输入正确数：采样79/73、强旧组合87/82、top-1也是87/82；各157映射正确98/94 vs110/107；74非reference单位原生均分60.36%/57.21% vs70.27%/64.41%。相对强旧或top-1，采样修复8/7、误伤16/16，净少8/9题。合法保持配对双正确为40/73、42/73，对照48/73、44/73；应变双正确两骨干均0/4，对照均1/4。配对关系是否成立另列，未以保持或翻转替代双正确；既有家族bootstrap区间完整保留，4组应变不能支持宽泛推论。

强旧/top-1各自引用同一组历史420/419调用，不相加：合3569940输入/168420输出token、4146.023历史模型秒。当前采样是预先固定同资源上界参考，实际用量不同，不能声称相同实际算力。比较制品包含242逐题trace与完整计数/成本，见对照汇总（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/result_comparison_preparation/complete_comparison/summary.json`）和逐题trace（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/result_comparison_preparation/complete_comparison/per_input_trace.jsonl`）。原失败聚合只展示170/1/71、错误身份与费用，无主分；同工具/共同冻结/独立评测仍缺，不能据此采用系统。

**空冲突描述诊断及有界修复准备。** d00047记录finish_reason=stop、775输出token/1973字符，57个决策ID、4个非null冲突和一个追加检查全部生成；五个description均为空串，原schema合法但原parser的strip非空约束拒绝。原生两字段已闭合（解释815字符、6句均唯一），不抽取原生答案替代失败系统结果。c0/c3是同一空条目重复，无解释循环或长度耗尽。一次原parser回放复现原异常，原文件保持，0模型/分词/评分，见诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/semantic_failure_d00047_diagnosis/diagnosis.json`）。

新增外部非空白decoder原型目标为原canonical grammar与原parser非空白约束的交集；null仍合法，原native字符串不受约束。显式新decoder aggregation_evidence_first_nonblank_frequency_0p1_v1，逻辑contract/消息/schema/parser/0.7/42/2048/freq0.1保持；112生产源不改。固定smoke预先确定为两骨干各原9题加d00047，共20题，不先反复重试失败题。真实入口脚本及两项父级首错/退出0但部分完成门检通过（0.016秒），实际预检和模型尚未放行。Unicode边界原型首测失败保留，正按精确等价约束修复，不能用minLength=1或ASCII近似掩盖；若不能保持合法输出集合则停止此修复。


**非空白原型失败与最小修复范围明确。** 精确Python strip非空白约束原型尝试两种Unicode字符类表示，分别漏拒空白和误拒合法的U+0085包围x；源码、测试日志和grammar diff均保留，停止收据未写通过。根追加最小实际Qwen tokenizer检查（session81776退出0，1.862秒、3个grammar/12输入、0模型）证实问题同时出现在accept_token，不能归咎于合成vocabulary或仅debug接口。具体：[^\u0085]仍接受U+0085；[\u0086-\u00ff]拒绝区间内U+00A0与é；单点类正常。见原型停止收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonblank_decoder_preparation/decoder_receipt.json`）与正式tokenizer最小证据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonblank_decoder_preparation/actual_tokenizer_unicode_probe.json`）。不修改现有vLLM/xgrammar安装，不放行该原型。

在用户允许的局部工程调整范围内，另立更小的nonempty-description解码修复：仅用原basic_string_sub的既有非闭合分支排除长度0字符串，不添加Unicode空白字符类。必须明确它没有实现全部非空白约束；纯空白仍由原parser判semantic_invalid并首错停止。因为原parser本来拒绝空串，这种限制不删除任何原parser合法输出，也不放宽方法接受条件。新decoder身份aggregation_evidence_first_nonempty_frequency_0p1_v1，原逻辑方法/所有提示、schema、parser、采样参数和固定20清单保持；旧两次失败不覆盖、不重命名成成功。该版本仍待有限回归与正式入口预检，0新模型。

独立审查另发现外部父级runner在子进程异常退出、缺少最终input_status时会误标固定题为未提交；已修正为submission_unresolved_no_durable_input_status，并保留已导出的完成项。旧原型入口3项回归通过（含新增缺失终态场景），同修复复用到新入口；新目录首次门检因decoder文件尚未完成而ModuleNotFoundError，原日志保留、无推理，待依赖就绪再验证。生产112源及已有运行结果均未改。


**nonempty-description有限验收及固定GPU启动（2026-09-23T05:55:58.834087+08:00）。** 新decoder346项检查/152个字符串边界/15个原parser fixture、7次matcher编译通过，测试逻辑1.49秒（进程4.64秒），0模型/真实tokenizer/评分；原d00047空描述被拒绝、两骨干各1条旧合法响应完整保持。Unicode和ASCII纯空白明确仍可通过grammar，但由不变parser拒绝；没有声称完整非空白约束。只改变11个描述叶子/lookahead引用并新增1个沿用旧非闭合分支的rule；旧nonblank停止收据保持。见decoder收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/decoder_receipt.json`）。

父级runner依赖就绪后3项回归通过（0.023秒），其中缺失最终状态不推断未提交、已有完成项保留。固定20实际入口预检session50045退出0，68.196秒：每骨干10个真实tokenizer/xgrammar请求、同步ingress逐字段比较及40个原parser正/length负fixture通过；与旧请求相比仅显式decoder身份和物理grammar改变，消息/schema/完整采样政策/输入token/资源预留保持。只检查实际可达首轮，当前默认路由无未使用可用专家，不额外重跑全484或不可能的第二轮。见预检收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/prepared/receipt.json`），112生产源及旧专家来源未变。

根唯一启动session85696，GPU2按M4→M5固定20题，first-error跨题/跨骨干停止，不重试/恢复/自动扩展。当前启动状态见manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/live_run/manifest.json`）与阶段状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/live_run/stage_status.json`）；全部242分母保留，未放行的222明确标记。没有把CPU预检记为模型成功，实际推理/终态成本待补；终态checker与记录在GPU期间准备，不能用部分输出宣称质量或采用。


固定20真实推理已确认进入CUDA计算：GPU2原M4引擎05:55:19 ready，现场约49801MiB占用/60%利用率；首4个固定输入已保存complete（至d00018），原session85696仍存活。M5尚未开始，本次没有提前评分/完整成功结论。后续仅轮询该句柄，writer终止后执行一次新终态核验，不因观察超时重启。

<a id="gpu-continuation-after-fixed20-20260923"></a>

### 固定20通过后的GPU衔接与并行执行（2026-09-23T06:10:09.127438+08:00）

用户再次指出GPU空闲而CPU流程拖慢进度。现场核对时GPU0/2空闲、GPU1/3已有其他健康作业；GPU2原session85696已退出0，而非模型正在CPU上生成。根立即执行一次已准备的终态checker（session48806退出0）：固定20全部完成，实际新聚合20调用、459043输入/8807输出token、364.556697429模型秒；历史68回调、426418输入/8174输出token、217.219558895秒，0专家重生成、0未知费用。原parser、请求、缓存来源和首错状态验收通过；这是可执行性验收，尚未评分或采用。见真实验收收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/fixed_live_receipt.json`）。

此前CPU检查串行及GPU任务衔接造成等待；本次不重复全484条分词/grammar。扩展准备复用已有请求证据，明确投影新decoder与frequency政策，并逐字段匹配本次20条真实预检；3个停止门合成测试保持。prepare session21086退出0后，根唯一启动GPU2 session56894，保留原20，按原顺序运行其余111×2；M4引擎06:07:29 ready，现场49801MiB、64%利用率，已有8条输出至d00012。完整242分母保留，首错跨两骨干停止、不重试、不增加输出上限。见扩展manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/extension_prepared/manifest.json`）、阶段状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/extension_live/stage_status.json`）。

另一条独立开发实验复用未采用A1 r5原输出及采用专家，固定M4 6题/M5 5题、最多13次新聚合。新实际入口13请求及26 parser fixture于session41995退出0（110.542秒）；旧11次execute、47缓存回调及全范围预算证据明确继承，本次未重复回放。根审阅原child、首错门、完整分母和新严格请求守卫后，写入独立固定范围放行记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/root_release.json`），唯一启动GPU0 session25907。当前仅入口初始化，尚不宣称实际完成或质量改善；其他核验准备与GPU2推理并行。见准备收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/prepared/receipt.json`）及运行状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/live_run/stage_status.json`）。

A1保留未采用/None/语义无效身份，不重新生成或填补；A2/A3/A4/F既有结果保持，A3编辑不运行。该实验完整路由每骨干29题双专家、82题仅A1、10题仅F，不能把242题都称为多专家协作。已完成245draw采样属于默认A2/A3/F资源参考，尚不是本A1激活版本的匹配对照；因此本次只放行固定入口试跑，不据此作资源匹配、收益、冻结或采用结论。


**并行试跑首错终态（2026-09-23T06:12:41.060985+08:00）。** GPU0 M4引擎06:09:19已真实进入CUDA运行；session25907实际退出1，M4 d00008出现`OutputSchemaError`，错误为`Unterminated string starting at ... char 1641`。停止时2个真实请求已提交且完成、在飞0；首题complete、第2题invalid_output，M4其余4题与M5全部5题未提交，231后续范围未放行，完整242为1完成/1无效/240未提交。原生质量未评分，A1未采用，0专家重生成，不把失败删去或重试。

当前费用来自durable status：新聚合2调用、93989输入/1381输出token、65.89328598模型秒；旧专家11缓存回调、55915输入/3394输出token、160.344088265秒，unknown=0。引擎shutdown成功，GPU0释放；请求/响应/费用完整终检与失败结构诊断正在准备，尚不声称终态审计完成，也未把原因臆测为输出预算不足。见首错状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/live_run/live/m4/status.json`）、完整分母状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/live_run/stage_status.json`）。健康GPU2 session56894继续，现场M4已有31条完整扩展输出；两个骨干仍按既定顺序，不因GPU0释放重复生成或扩展失败试验。

<a id="multiexpert-stop-syntax-diagnosis-20260923"></a>

### 缓存多专家d00008：stop但原始JSON无效（2026-09-23T06:22:43.062087+08:00）

根执行固定11终态审计session68307，实际退出0：核对2条真实模型请求/引擎入口、11个原专家来源回调、原parser失败、跨骨干首错停止、完整242分母及前节所列成本；0新模型/分词/grammar/专家回调执行。全部来源保持，unknown=0，GPU0已清理。审计通过确认的是停止与证据忠实，**不是该候选输出通过或可以扩展**。见终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/fixed_live_receipt.json`）。

原响应的最小诊断已保存：M4 d00008实际58340输入/881输出token、41.552402509模型秒、finish_reason=stop，1644可见字符（全部ASCII）；上限仍2048，没有预算耗尽证据。112个decision条目、四槽conflicts及additional_check顶层字段已闭合；最后完整嵌套字段是native_answer.step_by_step_thinking，内容只有两个标点字符。answer_choice在char1641开串后未闭合，缺少完整原生答案及语义内容。直接json.loads与原_json同位置失败，原parser不做围栏截取或反转义；两份持久化raw相同，因此不是parser加工造成的破坏。原状态继续为output_schema、semantic_result=unavailable、method_score=not_scored，不按答案错误打分，也不恢复不完整前缀。详见诊断数据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/diagnosis.json`）。

现有物理事件只记录输出token数量和finish_reason，没有实际输出token ID序列及具体stop_reason；request.stop及stop_token_ids为空仍不能证明实际EOS机制，因为本地模型generation_config还定义多个EOS。当前不能据此认定是grammar、mask、EOS或反分词的哪一环出错。同题新旧grammar的native/basic_string规则静态相同，但不替代运行期证明。

一次仅本题实际M4 tokenizer的离线grammar probe启动为session66076；最后快照wall2:04、CPU2:11、约106%CPU，随后TERM退出143，未产生结果文件。脚本缺少阶段刷新日志，无法区分停在编译还是匹配，不能宣称任何probe通过。原日志及单独停止收据保留，不继续CPU重试。为补齐真实生成序列，准备在空闲GPU0做**一次**原消息/模型/schema/grammar/参数完全相同的独立telemetry诊断，仅额外记录output token IDs和stop_reason；根尚未启动该新模型调用。该诊断不恢复旧批次、不替换负结果、不评分、不搜索参数；GPU2健康扩展继续。

同时完成完整242成功后才可执行的无损合并与原生评分入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/ASSEMBLY_README.md`），两项合成门通过；尚未实际合并或评分。修正原型README（本地制品：`/home/data3/txy/cf_moa/README.md`）中已过时的“仅CPU/没有live launcher”、旧采样被写成唯一当前控制及独立范围措辞；README不在运行锁中，生产112源与核心计划未修改。


**M4完整生成与单请求GPU诊断启动（2026-09-23T06:31:44.051710+08:00）。** GPU2 session56894仍实际存活，M4扩展111全部complete，加原固定10为121；父级已切M5，不提前评分。完整合并/评分之后的三核心对照比较脚本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/compare_complete.py`）另已准备，仅做语法解析，尚未实际比较：复用强旧、top-1及245draw采样的完整原生分数/配对指标与已有区间，输出逐题修复/误伤及新旧成本，不重评分控制、不重算其区间、不混入失败A1组合，不把实际资源近似写成严格同成本。

单请求telemetry准备的初次InputPacket property误读导致KeyError（0模型），原日志保留；随后用原构造器计算input_hash，未给输入补字段。源码第二次修订仅加入真实core.add_request只读采样快照，旧源码/准备收据保留，新prepare退出0；没有分词、grammar或专家回放。根读取完整脚本和最后diff，核对最终源码/receipt哈希并写固定单请求放行记录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/telemetry_authorization.json`），唯一启动GPU0 session26284。该单次调用与原M4 d00008 logical/physical请求逐字段绑定，原0.7/42/2048/frequency0.1与模型配置保持；结果无论可解析与否均不替换原负结果或用于选参数。模型真实计算、费用与停止原因以独立诊断目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/telemetry_live`）终态记录为准，当前不得写成已完成。

<a id="aggregation-runtime-eos-alignment-20260923"></a>

### 实际额外EOS提前停止与有限修复决定（2026-09-23T06:41:40.564766+08:00）

单请求GPU0诊断session26284已实际退出0，表示诊断完成；原parser仍拒绝，不表示方法输出成功。真实计算58340输入/881输出token、44.171550748模型秒，初始化21.089971493秒、诊断总86.885944202秒；0专家新请求、unknown=0，engine正常shutdown并释放GPU。原批次两次调用的65.89328598秒保持，新增诊断费用单独记录。见单请求终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/telemetry_live/receipt.json`）。

此次实际输出881个token，最后一枚128008（eom），stop_reason=128008；真正core提交的primary EOS=128009、额外stop IDs=128001/128008、总集合三枚。新raw与旧失败逐字节同SHA `0b07662a61d9ab4049604123669662be167f2a9e1cd9333717b1bf49cb4e48c1`。一次实际tokenizer.json后端解码确认：跳过special的完整序列、去最后一枚的序列均精确还原同一未闭合JSON；保留special只在末尾增加eom字面标记，仍是char1641未闭合字符串。只有最后一枚为special，因此不是反分词隐藏了原本合法的闭合结构，也不是2048预算耗尽。此实际token序列属于**新诊断**，不回填成原调用本来已记录的token IDs。见实际token分析（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/telemetry_analysis.json`）。

随后有限补证仅额外加载一次真正M4 AutoTokenizer（连同前次解码合2次），使用同一个极小JSON object/string合同，默认TokenizerInfo与显式core EOS union各编译1次，固定12项检查，7.131秒、0新模型。默认Info实际仅含128009；字符串未闭合时，128001/128008均mask允许且accept成功、matcher不终止，而vLLM会按同token结束请求。显式union后，未闭合时三枚全部mask拒绝；完整JSON后三枚均正常终止。见toy收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/toy_eos_union_probe/receipt.json`）与说明（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/d00008_failure_diagnosis/toy_eos_union_probe/README.md`）。这证明该集成边界存在提前停止通路；没有重编译286000字符的本题grammar或伪称已捕获原调用的逐步GPU mask。

根决定实施**停止协议工程修复**：沿用已经toy验证的TokenizerInfo显式EOS union路径，不再增加matcher override试验轴。外部backend保持原NonemptyBackend的消息、逻辑/物理请求、schema、grammar文本、原parser、温度0.7、seed42、2048上限及frequency0.1；只把CPU preflight与真实engine的grammar TokenizerInfo停止集合对齐实际服务端集合。实际engine子进程必须留下PID、有效stop IDs、模型/grammar/源码hash证据，并与core请求union逐项一致；只支持已观测本地fork，若原runtime返回非fork则拒绝，不改启动法或安装库。此修复不会追溯改写原负结果或正式v5/原生评分/旧head。

修复入口在独立准备目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation`）实现，当前仅代码准备，未放行新模型。计划继承原固定11题与13请求模板/47专家回调证据，本次CPU实际只验证两骨干各d00008一条新编译器入口；其余未变请求/26 parser fixtures明确继承，不重复全量预检。随后仍须固定真实试跑、首错停止、全部242分母与独立费用，不能用toy结论直接宣称完整修复或采用。GPU2旧nonempty候选继续其既定实验，原M4全部121完成、M5当前已有40条完整扩展输出；已有有效A2/A3/A4/F不重跑。


**有限预检完成与GPU0直接衔接（2026-09-23T06:48:04.179899+08:00）。** 用户再次指出CPU串行阻塞。两条实际预检session75626退出0、44.332582秒：M4/M5仅d00008，logical/physical/engine ingress及token数量与原准备完全一致；TokenizerInfo停止集合分别为128001/128008/128009与151643/151645。其余13模板、26parser fixtures、47旧callback证据明确继承，本次0新parser/专家回放/模型；另4项原入口及首错guard回归0.019秒通过。未追加全量CPU扫描。见两请求收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/prepared/receipt.json`）。

根读取完整backend/entry及继承的实际run/child路径，核对最终源码和收据hash，写固定11放行（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/root_release.json`），直接启动GPU0 session22307（entry.py run --authorization root_release.json），与健康GPU2 session56894并行。GPU0为原M4六题/M5五题顺序、全球首错停止；0专家重生成，不扩展/评分/采用。当前仅已启动，真实engine子PID、core/compiler/matcher EOS及输出token绑定由终态证据确认，不把CPU通过称作live成功。终检补层在GPU运行期间准备，不挡启动。

只读资源快照GPU0空闲6MiB、GPU2约54319MiB/54%利用率，GPU1/3为其他活动任务。模型一直在CUDA计算；CPU主要执行grammar/JSON/缓存/评分路径，现有实现没有可直接切换的GPU执行方式。前期过多串行预检是流程开销，继续复用未变验收、限定补测与GPU并行，不为占满GPU重跑有效结果。当前原nonempty的M4完整121、M5完整78仅为运行进度，尚无本候选完整评分。


**停止协议修复固定11完整终态（2026-09-23T06:57:39.159788+08:00）。** session22307实际退出0，M4六题/M5五题全部complete；完整242分母为11完成/231后续未放行。根执行唯一真实终检session70248，12.254秒退出0：终态收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/fixed_live_receipt.json`）核对原请求/原parser、47旧来源回调、完整费用及engine清理，两骨干有效EOS分别128001/128008/128009和151643/151645。实际engine子PID为660533/662888，分别不同于父659932/662036；core、编译Info、matcher、grammar/request hash及全部11实际输出token/stop_reason绑定均通过，missing_proof=[]。这支持本固定范围停止协议修复有效，不能推出质量增益或A1采用。原d00008失败及一次精确诊断仍独立保留。

新增聚合11请求、346454输入/8105输出token、333.312637155模型秒；47历史专家回调308611输入/18627输出token、824.891933825历史模型秒单列，0专家新生成，unknown=0。11题没有触发追加F的新聚合；预先准备的post-F模板不冒称已实际发生。此固定组不评分、不替代旧结果，GPU0已正常释放。

下一步仍是原242开发范围，保留11后剩M4 115/M5 116。轻量扩展准备将从当前合法InputPacket及冻结保存提议重建当前合同audit/request，预期231初始＋162可达post-F逻辑模板；post-F明确加入原F提议再audit，不合成模型响应。旧484全量预检属于v3且其closed模板使用初始audit，不能充当当前EOS/v4范围实际验收。仅以固定11原13模板作逻辑等价锚点，实际tokenizer/grammar/context及预算保留在每个正式runtime请求的原门中；任何首错全局停止。当前只新增准备代码，根尚未放行扩展。


<a id="nonempty-complete-development-20260923"></a>

### 默认A2/A3/F聚合完整开发结果：运行通过、效果未过对照（2026-09-23T07:07:37.672245+08:00）

GPU2原session56894实际退出0，两个骨干各保留10＋扩展111，完整242全部complete。唯一终态审计session29025已结束并生成成功收据，14.672秒，检查实际请求/原parser、原专家来源、engine清理、完整分母及费用；该次轮询工具结果被根的输出格式错误丢失，shell退出码未另行保存，不补造为已直接看到exit0，收据及日志完整存在。随后无损合并session58387与原生评分session38527均实际退出0；三核心对照比较命令退出0，0.275秒。没有重生成任何旧专家，也没有重评分旧控制。

| 已暴露开发指标 | 默认聚合M4 | 强旧/top-1 M4 | 默认聚合M5 | 强旧/top-1 M5 |
|---|---:|---:|---:|---:|
| 唯一输入正确/121 | 75 | 87 | 73 | 82 |
| 原生映射正确/157 | 97 | 110 | 97 | 107 |
| 74个非参考原生单元平均分 | 56.76% | 70.27% | 54.05% | 64.41% |
| 保持关系双正确/73 | 44 | 48 | 45 | 44 |
| 应变关系双正确/4 | 0 | 1 | 0 | 1 |

每骨干121唯一输入/157原生映射/40来源家族，保持73对/25家族、应变4对/4家族；已有家族bootstrap区间随原评分保留，没有新增bootstrap或独立数据。相对强旧和top-1，M4修复2/误伤14/净−12，M5修复3/误伤12/净−9。相对旧245draw参考，M4修复6/误伤10/净−4，M5修复4/误伤4/净0；该参考的退化限制见下一节。默认仍是每题单专家加聚合，没有多专家协作增益证据。格式全部可解析、费用完整与执行成功不能代替方法质量，当前候选不采用；不改名成成功，也不强制保持旧答案来修分。

新聚合合242调用、3293204输入/85774输出token、2934.248828301模型秒；其中M4 121/1653551/38859/1095.343613688秒，M5 121/1639653/46915/1838.905214613秒。原专家839缓存调用、3569940输入/168420输出token、4146.022736064历史模型秒单列，0专家新生成、unknown=0。共同已有初答资源按原协议排除，strong/top-1共享历史调用不相加；模型秒是服务端调用墙钟，不当作GPU kernel时间。

证据：完整终态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/full_scope_receipt.json`）、无损合并（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/complete_run/receipt.json`）、原生评分（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/complete_scores/receipt.json`）、核心对照汇总（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/complete_comparison/summary.json`）、242逐题修复/误伤和成本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/complete_comparison/per_input_trace.jsonl`）。逐题完整原生答案、原模型调用及SQLite journal在complete_run/m4与m5保留，原固定/扩展输出未覆盖。正式v5和原生grader未改；A1缓存EOS组合单列，不能把它与此未对齐EOS版本的比较称为纯加/去A1消融。

<a id="sampling-reference-budget-audit-20260923"></a>

### 245draw参考的预算含义与固定3draw控制决定（2026-09-23T07:07:37.672245+08:00）

只读预算审计发现，原NC按逐题旧专家实际调用/输入/输出，加1次聚合输入及2048输出预留建立reference cap，k=min(16,调用cap,输入cap/native prompt,输出cap/2048)。所有242题均受输出预留限制：M4 119题k1＋2题k2，M5 120题k1＋1题k2，共245draw。既定平票选最早draw意味着k≤2时每题最终答案必然等于seed42首draw；因此这是有效的低调用参考结果，不能称充分的多采样多数票收益检验。

reference cap合1081调用/6863144输入/664036输出，输出为168420历史实际＋495616聚合预留；NC实际245调用/1032749输入/65459输出/1674.479982404模型秒。更具体地，旧sampler把自身Budget换成更紧reference cap，方法仍持16请求/400000输入/32768输出/4工具公共Budget，二者没有执行完全相同的硬上限。旧结果和原身份不修改，不声称严格实际费用相等。含A1新臂的A1成本、较长聚合及可能post-F/第二聚合也未计入旧参考表。详见预算审计（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/budget_scope_audit.json`）。

根在读取上述候选正确率前，按核心对照需要选定一个独立固定3draw控制：沿用双方已有公共16/400000/32768/4硬上限，每题固定seed42/43/44，原temperature0.7、max_tokens2048、frequency0.1不变；共同上限不等于花满预算或严格实际资源相等。保留旧245，只有逐字段相同请求才复用；需新增239个seed43＋242个seed44，共481新请求，预计新增输入1866328、输出最大预留985088，实际输出/时延未知。当前只实现准备，尚无新模型调用/成绩，不按正确率调k或选择seed，完整首错/分母与实际成本仍要求保留。


**含A1扩展首次启动失败与保留现场（2026-09-23T07:16:11.983861+08:00）。** 393逻辑模板初次准备session29736退出0、67.916秒，原13锚点相同，0分词/grammar/专家回调/模型。根审阅发现save_status错误使用splitlines，会拆开JSON字符串中U+2029；启动前归档初次9文件并改为物理行迭代，4项有限回归0.035秒通过，393模板与13锚点不重建、不改字节，明确源码重绑定（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_jsonl_rebind.json`），另1.157秒hash核验通过。

根读取完整runner与修复diff并写单独release，启动GPU0剩231为session26140；实际退出1。M4尚未创建SourceRunJournal数据库即触发RuntimeError `Terminal audit cannot open a database`：runner为复用cost_helpers导入terminal checker，间接安装只读审计的进程全局hook，污染真实入口。异常位于backend构造、设备锁和run_packets之前，M4目录只有run.lock，M5未启动。新增提交/完成/在飞均0、新模型0；request_id尚未分配（null），阶段是初始化基础设施错误，semantic_result unavailable / method_score not_scored。不能把它记成答案错误或方法输出失败。

原parent因缺少durable journal/export保守记11已完成/115提交状态未解析/116未提交、费用仅下界，原状态原样保留；单独诊断（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_startup_failure.json`）用准确控制流及退出证据补明本次0模型，不回写原status或补造逐题成功。固定11真实验收继续有效。仅暂停此入口，另行准备无审计副作用的纯成本助手及独立修复入口/输出目录，复用393/13及固定11；增加真实SourceRunJournal临时DB构造回归，禁止模型，不重试原目录。其他固定3draw和同池top1准备继续。

**固定11的实际提议采用范围。** 对保存trace做一次只读item identity/kind→原始模型原因码→final adjudication核对，11条audit hash/条目集合一致：9题激活双专家，仅6题对两个专家的非proposal条目均采用，即M4/M5各d00000、d00008、d00003。M4 d00011/d00018及M5 d00018的A1原生提议不可用，只有程序RP拒绝的proposal，不能算实际双来源采用；两骨干d00001均只选A1。A3和F的单个claim分别是目录模型偏好及稳健性建议，references为空，不冒充新增可定位医学事实。两骨干d00000的A2与A1带引用claim还共享同一引用，条目数含重复绑定，不能当独立证据增量。M4 d00000/d00008原生解释均只有两个标点字符，虽原合同parser通过仍解释不足。上述只是逐项采用声明，不是因果贡献或质量证据，也不能把固定smoke比例外推全242。原两trace SHA为M4 93b0e9beb49220605000865ba39342f57b6e7189ca9bca1455c1e9487e8c446b、M5 7c09dd58c8f074899b89af5e32bb03a8fe097d35fff6c4f726bb0efb7b8bd3dc，未模型/评分/重放parser。

**同池top-1缺口与无模型准备。** 原pure_top1的池为A2/A3/F（9/8/104），不能直接充当含A1 EP的相同专家池控制。冻结EP首选每骨干是A2 9/A3 8/A1 94/F 10；94个首选A1中M4 16、M5 44个原native_proposal为None，必须保留unavailable及真实历史成本，不按可用性换F。开始单列同池top1直返控制准备，复用原缓存与冻结路由，不聚合/补查/回退、不新模型。此控制与EP的差异含聚合及多专家两个因素，不能单独证明多专家因果增量；尚未运行或评分。

<a id="parallel-gpu-runtime-20260923"></a>

### 消除检查串行阻塞并启动两卡任务（2026-09-23T07:26:37.033848+08:00）

用户再次指出有空闲GPU而CPU准备持续拖慢。检查确认GPU0/2/3空闲、GPU1为其他健康任务。缓存回放、原生评分及JSON/来源检查属于CPU工作；真正延迟GPU启动的是此前重复准备/串行审核及checker导入污染，不是模型应当用CPU计算。此后已完成准备直接推进GPU，离线评分/独立终检准备与模型并行，不再新增全范围tokenizer/grammar扫以替代原runtime门，也不为填满卡重跑有效专家。

独立修复仅将终检器导入替换成无副作用纯成本函数，使用新入口、prepared和输出目录；原方法、prompt/schema、采样及393逻辑模板/13锚点字节不变。真实child临时SQLite回归14.094秒通过，实际经过来源/plan门和SourceRunJournal后在固定设备锁处退出75、backend未构造，0模型；两次测试观察失败保留，真实原因是审计路径bytes被str化导致比较错误，用os.fsdecode修正观察，非运行方法改动。最终hash绑定1.209秒通过，没有重复重建模板。原session26140启动失败、11/115unknown/116原状态及单独0模型诊断全部保留。

根核读独立入口diff、纯成本函数及固定11来源，写新release（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_runtime_repair_root_release.json`）后启动GPU0 session33956，命令 `PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0 /home/data3/txy/MedRGAG/.venv/bin/python extension_runtime_repair.py run --authorization extension_runtime_repair_root_release.json`。只运行剩M4 115/M5 116，保留固定11、首错停止；修复收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_runtime_repair_ready.json`）、运行日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_runtime_repair_stage.log`）及独立输出（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_runtime_repair_live/stage_status.json`）。启动不等于完成，尚无完整质量结论或采用。

GPU2 session74468并行执行固定3draw控制；根核对原JournalBackend与缓存/新请求切换、原native parser/vote及预算，绑定release（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/root_release.json`）。命令 `PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=2 /home/data3/txy/MedRGAG/.venv/bin/python control.py run --gpu 2 --authorization root_release.json`。242输入/726逻辑draw，245先前同请求采样复用、481计划新增，按固定seed42/43/44及原公共16/400000/32768/4上限；历史采样费用明确为prior_sampling_control，非专家费用，不称严格实际资源相等。已见引擎ready和GPU2显存49121MiB/利用率69%的瞬时快照；最终调用/时延由journal出具。

同池top-1缓存session7249实际退出0：242分派、502历史回调、0模型/聚合/补查；M4/M5原生可用105/77，None为16/44，不回退。两骨干历史输入2795061/2483204、输出97629/100073token，模型秒4831.1535/3981.2811，缓存执行墙钟100.52/85.50秒；与GPU调用分开。3实际缓存回归通过，完成后只读242提议/1376字段均原样。根完整核读score.py与原score_run的None/not_scored/完整分母行为，已授权单独原生评分，尚未收到评分终态。证据：完成收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/same_pool_top1_control/receipt.json`）、只读核验（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/same_pool_top1_control/completion_read_only_check.json`）。

默认聚合已有评分另做0.491秒离线路由拆分，0模型/0新增原生评分：route_breakdown.json（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/complete_comparison/route_breakdown.json`）。M4的A2/A3/F分别0/9、0/8、75/104正确，对应top1为8/9、3/8、76/104；M5分别3/9、1/8、69/104，对应8/9、4/8、70/104。损失集中于A2/A3聚合，当前证据显示有效原生数组的内容遗漏或改变，尚未建立接口字段错误；不据此强制保留专家答案或改动正在运行的冻结候选。

**并行实算与同池评分终态（2026-09-23T07:28:13.535564+08:00）。** GPU0/2均已产生真实live模型事件，仍运行中、无失败；瞬时GPU0利用率曾达100%。只读journal的运行快照（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_relational_20260922/gpu_parallel_runtime_snapshot.json`）明确区分新模型与缓存回调，非最终费用。GPU3暂无已放行独立任务，不用重复生成填卡。

同池top-1原生评分session81602实际退出0，固定入口只运行一次；完整242输入/314映射保留。M4正确72/121、错误33、不可用16；M5正确57/121、错误20、不可用44。74非参考原生单元均分0.6072072072/0.4063063063；None保持not_scored、仍在完整成功率分母，不称错误答案。历史费用仍266/236请求、0新模型；离线评分23.93/21.28秒，原缓存receipt与评分入口hash未变。独立评分收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/same_pool_top1_control/scoring/receipt.json`） SHA e2b8e32b7278f6ba41010673d92fdf3c240e3d9091dbdd7035537e28c9510c61。该控制只为正在运行的同池组合提供直返基准，不据此宣称A1或组合采用。

**交付记录补齐与结束后处理准备（2026-09-23）。** 两条实际会话33956/74468再次轮询均确认存活；上一目标回合完成了两卡启动和同池评分，属于实质进展。当前继续运行，尚未以未完成部分评分。根已全文审阅独立EOS扩展终检入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/check_extension_runtime_repair_terminal.py`）：仅将原审计中依赖事前physical的三处断言改为实际runtime logical/physical/grammar绑定，继承完整sampling/model及child EOS证据，明确393模板没有事前physical预检。代码尚未执行实际终检，须等原会话终止且writer锁释放。固定3draw终检及含A1无损合并/原生评分入口在并行准备，不改变运行中源码与配置。

既有A1 r5、A5负结果现补为可独立引用的结构化身份说明：[A1 r5未采用](../../../2026-09-23_cf_moa_process/data/a1_non_adoption.json)、[A5未采用身份绑定](../../../2026-09-23_cf_moa_process/data/a5_non_adoption.json)。A1直接读取原保存原生评分：M4正确55/121、错误36、不可用30；M5正确42/121、错误18、不可用61，绑定两评分文件和实现来源，0重新评分/模型。A5引用用户确认的旧负决定，F仍是独立旧组件；旧文件中当时的矩阵暂停文字作为历史保存，不重施已解除的暂停。此项只是落实既有未采用决定，不是新方法选择、共同冻结或独立泛化验收；既有freeze草案不被改写为ready。

**两项运行的后处理已准备、未执行。** 根全文审阅固定3draw终检（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/check_terminal.py`），SHA 8cd320b2cf9c5dc0775ca09ed51016972483c1686ec77eb5e4b4af944562d022；独立CLI才安装hook，不导入模型、不读评分标签、不分词/编译grammar。准备仅6项有限断言0.020秒，真实终检须根确认parent会话结束后运行，尚未认证live结果。

含A1完整结果的无损合并/评分入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/assemble_and_score.py`），SHA 604b69d841f36e9c7acbe07ac5e6eff4685f020dcfbd5cc138f6ff6d0dc81c56，根已全文及原score_moa_run身份/分母核对。只适配既有writer和来源校验的6+115/5+116、adopted+A1双来源证明、既有实验缓存reader及当前EOS外层身份；准备2项有限gate/diff检查0.116秒，0live读取/模型/分词/grammar/回放。它要求完整242且已完成实际终检后，先核4个原journal再写新完整目录，原None提议与费用不替换；`assemble`和`score`须分别执行，原生grader不改。固定3draw评分桥另行准备。两原GPU会话33956/74468随后各等待50秒仍确认存活，未因观察等待重启。

**固定3draw评分桥审阅完成（2026-09-23）。** score_complete.py（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/score_complete.py`） SHA f0cff8b52df616482567335c1a21c24a52d5c4c7ce82874ad4b74b5a7b996989，沿用原score_run及完整winner native对象的透明外层封装，唯一前门是完整242/726实际终检和全部source hash保持。245历史采样与481新调用各自留原成本，不冒充专家缓存、严格等实际资源或花满公共预算。准备仅AST语法确认0.005秒、0新测试/模型/live读取；根已全文审阅，未执行评分。比较入口仅准备处理正确/错误/不可用三状态及同池top1、强旧、fixed3的对齐，不读取尚未结束的结果来挑方法。

**固定3draw M4完成并切换M5（2026-09-23T07:48:45.585908+08:00）。** M4实际status为complete，121完成/0失败/0未提交、first_error=null，cleanup确认native_core_shutdown_returned。240新采样919757输入/64347输出token、1192.344816929模型秒；123历史采样555460输入/33356输出token、660.624724018历史模型秒，unknown=0。GPU2原parent74468保持运行并实际构造M5 child，其引擎日志07:47:33报告ready；parent stage的runs数组在全阶段终态前仍是初始空列表，不能把该快照误判未启动或补造父进程退出码。以上M4终态来自实际child status/cleanup与M5 journal，不等于完整双骨干终检或质量通过。M4状态（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/live_run/m4/status.json`）、清理（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/live_run/m4/engine_cleanup.json`）、M5日志（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/live_run/m5.log`）。

EP三核心控制比较入口（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/compare_complete.py`） SHA 2bc946274f5e5ed1ebc725e610aabceb001ef99b3e84f71b322b3b14039f323c，根已全文及已完成控制实际字段核读；只准备，尚未比较。一个9组合纯fixture核对正确/错误/不可用3×3转移：仅错误→正确称修复、正确→错误称误伤，不可用恢复另列。要求当前EP、fixed3及同池top1均完整原生评分，逐骨干121/157/40家族与原scorer来源对齐；77配对实际覆盖29家族，保持73对/25家族、应变4对/4家族，不能误称配对也有40家族。保留原区间，0模型/重评分/bootstrap。默认NP因EOS与专家池不同未纳入纯消融；同工具控制和独立范围缺口仍明确保留。

<a id="gpu-cpu-scheduling-diagnosis-20260923"></a>

**GPU与CPU调度诊断（2026-09-23 08:07）。** 用户再次质疑CPU拖慢，根核实GPU0/2实际计算，短采样分别0–100%/44–100%，GPU1为其他健康任务、GPU3空闲；同期结果持续增加，不能把显存占用当作持续计算，也不能把请求间空档都归因于某一个CPU步骤。只读定位到：`moa_runner.py:143`每题调用`journal.export`，`journal.py:138`全量读取/解析并重写累计请求和结果，累积工作量呈平方增长；观察时M4两个导出文件合226572400字节。C3新增draw还有重复请求分词。EP前102条实际grammar预检分别为102个不同guidance，记录编译共292.867秒、均2.871秒、最大10.145秒；已有按guidance缓存，不能误称相同grammar反复编译。这些统计未测完整CPU分项墙钟，不把全部GPU停顿归给导出。

两父入口各绑定一张卡并同步执行M4→M5；首错停止本身并不要求单卡，但当前没有跨卡统一停止协调，直接额外启动M5会与父进程后续启动冲突。当前健康批次继续，不热改hash绑定源码、不重复生成；GPU3没有可直接追加的独立已准备任务。后续工程改进方向为增量/后台导出、按完整请求与模型身份缓存token计数、协调多卡首错提交；本次仅诊断，尚未实现或验证这些性能修复。SQLite持久化、请求参数、费用与失败分母必须保持。0诊断模型、0测试、0运行源码修改。证据：资源采样、进度及源码位置（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_relational_20260922/gpu_cpu_scheduling_diagnosis_20260923.json`）。

**含A1组合M4完整完成并启动M5扩展（2026-09-23T08:14:26.302299+08:00）。** GPU0父会话33956仍在运行；其M4扩展子进程实际返回0，115完成/0失败/0未提交、first_error=null；加原固定6题，M4完整121题已保存。引擎清理为aggregate_core_shutdown_returned，父级已启动M5剩116题；当前启动/加载不冒称M5已产生新模型结果，也不把暂时释放显存误判为停止。

M4扩展实际新聚合115次、3073581输入/56101输出token、1959.962699356模型秒；305历史专家回调、3119389输入/128321输出token、6003.015479916历史模型秒单列。未知用量0、用量分歧0，历史来源CPU回放11.955562247秒。此处费用仅115扩展，不含原固定6；不混为完整双骨干费用或质量得分。完整终检/合并/评分仍等待M5和父进程终态。证据：M4里程碑与原状态路径（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/a1_v2_relational_20260922/multiexpert_M4_complete_milestone.json`）。

<a id="fixed3-complete-development-20260923"></a>

### 固定三次采样公共上限对照完整开发结果（2026-09-23T08:26:24.541668+08:00）

GPU2原父会话74468实际退出0，两骨干各121题、合242题完整完成，0失败/0未提交/0不可用；两child退出0且native_core_shutdown_returned，现场GPU2显存降至4MiB。一次终态验收72096实际退出0，26.587秒；确认完整726逻辑draw、481新模型＋245精确历史采样复用、实际请求/原parser与投票、费用及来源一致。随后原生评分74795实际退出0，23.138秒，评分新增模型0。没有重跑旧专家或覆盖旧采样结果。

| 指标 | M4 | M5 |
|---|---:|---:|
| 完整唯一输入正确数 | 84/121 | 74/121 |
| 错误／不可用输入 | 37／0 | 47／0 |
| 正确原生映射 | 109/157 | 95/157 |
| 74个非参考原生单元均分 | 0.6576576577 | 0.5945945946 |
| 保持配对双方正确 | 50/73 | 43/73 |
| 应变配对双方正确 | 0/4 | 0/4 |
| 保持／应变有效关系 | 58/73、0/4 | 59/73、1/4 |

原强旧完整输入正确87/82、原生单元均分0.7027027027/0.6441441441；本对照这两项主指标均较低。M4保持双方正确50/73高于强旧48/73，是单独的描述性配对结果，不能概括成整体胜出。原配对区间已保存在评分制品，保持覆盖25家族、应变4家族；本次没有另作bootstrap、重新挑种子或以新结果调整正在运行的聚合。此结果保留为身份`native_sampling_fixed3_common_cap_frequency_0p1_v1`的完整开发控制，不替换历史版本。

新481调用实际1866328输入/128768输出token、3176.071480493模型秒；245历史采样实际1032749输入/65459输出token、1674.479982404历史模型秒另列，unknown=0。逐骨干新调用240/241，历史123/122。terminal中reused_head字段只是既有账本别名，source_kind明确prior_sampling_control，与reused_sampling不能重复相加。固定seed42/43/44、temperature0.7、max_tokens2048、frequency_penalty0.1与原公共16调用/400000输入/32768输出/4工具上限保持；只称相同公共资源上限的固定三次采样，不宣称实际成本严格相等或耗尽预算。仍是已暴露开发范围，没有共同冻结或独立评测结论。

证据：[实际会话退出及成本汇总](../../../2026-09-23_cf_moa_process/data/fixed3_execution_receipt.json)、终态验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/terminal_receipt.json`）、完整原生评分（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/native_sampling_control/common_cap_three_draw_control/complete_scoring/receipt.json`）；两骨干逐题原始draw与请求在`live_run/{m4,m5}/`，原生逐题分数和配对记录在`complete_scoring/{m4,m5}/`。GPU0多专家M5仍运行，三核心对照比较入口继续等待其完整终检和评分。

<a id="saved-a1-complete-postprocessing-20260923"></a>

### 含A1组合完整推理终态及合并字段修复（2026-09-23T09:19:01.892829+08:00）

GPU0父会话33956实际退出0：原固定11加本次231扩展，完整242题全部保存，无首错，两个扩展child均正常清理，现场GPU0释放至6MiB。一次终态审计78376实际退出0，67.956秒；确认完整分母、真实请求/原parser、双来源证明、EOS协议与完整费用，0新专家生成。实际新聚合242调用、5857532输入/130187输出token、5020.109051603模型秒；631历史专家回调、6221546输入/277186输出token、11893.305803881历史模型秒，unknown=0。此时尚未评分。

首次合并48880退出1，错误为`KeyError: allow_unadopted`，发生在任何完整输出目录创建之前。真实四份来源计划均使用`experimental_allow_unadopted=true`；脚本把读取键名写错，早期合成测试没有覆盖这个真实结构。这是后处理错误，未改变推理结果、原生答案、费用或方法身份，不记作方法答案错误。原失败日志、脚本SHA604b69d841f36e9c7acbe07ac5e6eff4685f020dcfbd5cc138f6ff6d0dc81c56及原准备目录已保存在`assembly_plan_key_fix/before/`，失败记录不覆盖。

修复严格只改该读取键名，原True门禁和decoder门禁保持；实际四计划回归（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/assembly_plan_key_fix/regression_receipt.json`）验证原谓词在四份计划均失败、修正谓词均通过，显式false、缺实验键但伪加旧别名、decoder漂移仍拒绝。四来源计划hash前后不变；原两项准备测试0.093秒重绑定新脚本SHA2c0600652fb1af875ea279a26457372c00a6fc123f90c7785a84319db9039306，0模型/评分。修复后仅重新执行合并，仍须实际成功后才评分；没有重跑推理或终态审计。见单行diff（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/assembly_plan_key_fix/schema_field_read.diff`）、失败现场（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/assembly_plan_key_fix/failure.json`）、原始终态验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/extension_runtime_repair_live_receipt.json`）及[执行记录](../../../2026-09-23_cf_moa_process/data/ep_execution_receipt.json)。

<a id="saved-a1-complete-development-20260923"></a>

### 含A1组合完整开发评分与三核心对照（2026-09-23T09:27:18.153517+08:00）

单行计划键名修复后，合并46638实际退出0，原生评分23214实际退出0，三核心比较命令退出0、0.487秒。四份原始结果无损合并，完整两骨干各121唯一输入/157原生映射/74非参考原生单元/40家族；242条逐题比较均保留。旧评分器、原专家输出与方法身份保持，评分及比较新增模型0、没有重新bootstrap。原合并48880失败及修复前后源码、回归和日志仍保留。

| 对照／候选 | M4正确／121 | M5正确／121 | M4原生单元均分 | M5原生单元均分 |
|---|---:|---:|---:|---:|
| 强旧head | 87 | 82 | 0.7027027027 | 0.6441441441 |
| 固定三次采样公共上限对照 | 84 | 74 | 0.6576576577 | 0.5945945946 |
| 相同专家池top-1 | 72 | 57 | 0.6072072072 | 0.4063063063 |
| 含未采用A1的稀疏聚合候选 | 79 | 74 | 0.6306306306 | 0.5405405405 |

候选M4/M5均0不可用，错误42/47；正确原生映射100/157、98/157。**不采用该候选，保留完整负结果及原身份** `experimental_saved_A1_r5_adopted_sparse_nonempty_frequency_0p1_eos_aligned_v1`。双骨干相对强旧各少8个正确输入；相对三次采样为M4少5、M5唯一输入数持平，但两骨干原生等单元均分均较低。不能以格式完整、全量成功执行或局部计数增加宣布协作有效；A1 r5和A5已有不采用决定保持。

按正确／错误／不可用三状态逐题对齐：相对强旧，M4修复6／误伤14，M5修复4／误伤12。相对同池top-1，M4错误修复7／误伤14，另16个不可用恢复可用、其中14正确；M5错误修复2／误伤12，另44个不可用恢复可用、其中27正确。因此同池总正确数增加7/17含大量不可用恢复，不能把这些全称作错误修复或纯协作收益；原已可评分输入上的误伤仍多于修复。相对三次采样，M4修复5／误伤10，M5修复5／误伤5。

保持双方正确为42/73、45/73，合法保持关系49/73、55/73；应变双方正确及合法关系均0/4。保持25家族、应变4家族，保留原家族分组区间，不与完整40家族混淆。没有把单独生理模型实验补入此原生开发范围；小子组计数不外推通用能力。

本候选完整费用：新聚合242调用、5857532输入/130187输出token、5020.109051603模型秒；631历史专家回调、6221546输入/277186输出token、11893.305803881历史模型秒另列。M4新121调用3257045/59658 token、2094.954565738秒；M5新121调用2600487/70529 token、2925.154485865秒。历史来源分别332/299调用。共同已有初答成本按原协议排除，共享控制费用不相加；模型秒是原服务调用墙钟，非GPU kernel时间。此固定三次采样仅匹配公共上限，实际资源不相等；同工具单agent仍不完整，不能写成所有资源控制均已满足。

证据：[完整比较](../../../2026-09-23_cf_moa_process/data/comparison_summary.json)、[242题转移与费用trace](../../../2026-09-23_cf_moa_process/data/per_input_status.csv)、原生评分收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/complete_scores/receipt.json`）、[未采用决定](../../../2026-09-23_cf_moa_process/data/non_adoption_decision.json)及[执行退出记录](../../../2026-09-23_cf_moa_process/data/ep_execution_receipt.json)。[完整激活分布与证据使用汇总](#saved-a1-complete-evidence-use-20260923)已完成，0新模型/评分；尚未共同冻结，独立范围待决，未运行独立评测。默认旧F和已有效A2/A3/A4保持，A3编辑模型继续暂停。

<a id="saved-a1-complete-evidence-use-20260923"></a>

### 完整多专家激活与证据使用描述性审计（2026-09-23T09:33:26.120581+08:00）

按核心计划的协作检查要求，对已完成的242条合并trace各作一次物理行读取，用既有原生correct和已对齐top-1结果做描述性统计；成功扫描与汇总耗时1.347秒，新增模型、原生重评分、参数搜索均0。来源输入hash、实际原始决策与最终adopt/reject逐项一致，报告保留源码及读取字节hash。准备阶段曾错误假定top-1评分表有input_hash，读取时退出；未扫描完整proposals或写结果，改取已经完成输入对齐的比较trace后才成功执行，原准备错误记入报告。

两骨干各121题的实际激活完全相同：A1单独82、F单独10、A1+A2共9、A1+A3共8、A1+F共12。每骨干29题激活两专家，其余92题为一专家；全部仅一轮聚合，没有触发额外补查。A4在此输入范围不适用，A5未采用，没有据此扩大其权限或重新生成。

| 描述性子集 | M4正确／该子集分母 | M5正确／该子集分母 |
|---|---:|---:|
| 实际激活至少两专家 | 14/29 | 16/29 |
| 最终声明adopt至少两专家的claim/change（排除原生答案proposal本身） | 11/22 | 9/17 |
| 两专家均有adopt且程序接受、带精确位置引用的claim | 1/7 | 0/4 |
| 被调用A1原生提议为None的输入，聚合最终答案 | 14/20 | 30/51 |

激活、声明采纳、引用定位、语义蕴含与因果贡献分别报告。两专家均有定位引用的7/4题全部为A1+A2，且存在跨专家重复引用，不能称为独立新增证据。A3/F无绑定引用的意见仍保留原身份，不升格为患者事实。A1原输出None不改成错误或成功，以上只统计聚合答案；它与top-1不可用16/44题是不同子集。原None对应overflow、incomplete及semantic_invalid标志全部保留，标志可重叠、不能相加充当输入总数。

M4有4条解释不超过32个非空白字符，其中2条非空解释仅含标点；这两条原生答案均错误。M5没有上述短解释。阈值仅作描述，不新增评分过滤、不删题、不修补答案。程序定位审计未发现adopt不合格条目，并不证明临床蕴含正确；完整结果仍不足以支持协作收益，原未采用决定保持。

证据：一次扫描脚本（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/complete_comparison/evidence_use_report.py`）、[汇总与来源hash](../../../2026-09-23_cf_moa_process/data/evidence_use_summary.json)、242题证据使用分类trace（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/router_aggregation_preparation/native_explanation_stability_preparation/evidence_first_preparation/stability_preparation/nonempty_description_preparation/multiexpert_preparation/eos_alignment_preparation/complete_comparison/evidence_use_trace.jsonl`）。本批GPU推理、原生评分、三核心比较及该离线汇总均结束；同工具单agent尚不完整，A2原parser恢复、同工具输入/上下文版本与独立评测范围仍有待决项，A3编辑模型保持暂停，尚未共同冻结或开展独立评测。GPU瓶颈修复仅完成[定位](#gpu-cpu-scheduling-diagnosis-20260923)，增量导出与跨卡首错协调尚未实施，不写成已加速。

<a id="development-delivery-index-20260923"></a>

### 完整开发交付索引与未完成范围（2026-09-23T09:38:17.895490+08:00）

本轮核对发现运行包README仍将已经完成的互补分析标为暂停，已修正该导航；代码README也明确execution_plan.json是历史阶段快照，不能作为当前运行权限。新增[开发交付索引](../../../2026-09-23_cf_moa_process/data/development_delivery_index.json)绑定31份计划、采用源、验收、评分、成本、负结果和阻断证据，并导航到各自原始trace及运行快照。读取现有小收据及其哈希，未重新扫描完整trace，0模型、0评分、0测试；没有修改原实验结果、原生评分或旧冻结索引。

EP完整推理/评分/比较、同池top-1和完整证据使用的旧缺口已解决；三次采样完整，但仅匹配共同预算上限。强旧控制旧状态缺failed字段是登记差异，已有逐题导出的完整计数，不能据旧校验报错要求重跑。旧unfrozen draft保持历史身份，新交付索引不冒充共同冻结，也不将其缺少某臂绑定解释成该臂从未执行。独立复核同样确认这些边界。

仍未完成同工具单agent完整控制、最终共同版本与全部所需对照绑定、独立范围资格决定及冻结后评估。A1/A5和EP未采用；A2原parser恢复与同工具输入/profile容量问题仍待处理决定，A3编辑模型仍暂停。没有为了占用空闲GPU自行扩大上下文、改prompt或启动独立数据推理。该索引满足阶段交付导航，不能据此宣布完整目标完成。

<a id="goal-blocked-handoff-20260923"></a>

### 目标阻断交接（2026-09-23T09:41:48.404323+08:00）

完整开发交付后，连续三个目标轮确认相同方法/范围决定仍待答，均为无进展复核，不计为实验进展或正在等待健康进程。当前无本任务模型作业。目标服务已实际标记blocked；目标未完成、范围不缩小。A2独立控制的原parser恢复、同工具完整输入在采用facts容量下超限及逐角色配置方案、独立评测范围暴露资格仍需处理决定；不以自动续行视为答复，不重复生成或扩大预算。其诊断、固定方案及已有结果均在[开发交付索引](../../../2026-09-23_cf_moa_process/data/development_delivery_index.json)，暂停只涉及后续依赖工作，既有A2/A3/A4/F验收及全部负结果继续有效。

共同冻结和冻结后评估报告尚未完成；当前组合候选未通过核心对照、不采用。再次恢复时应从上述明确决定及已有制品接续，不重建数据、不重跑已有效批次；若同一阻断仍在，恢复后的阻断计数重新开始。GPU日志/调度优化仍只是已定位工程问题，未把它写成已解决或以占卡替代必要的方法决定。

<a id="cf-moa-process-report-20260923"></a>

### 用户要求的完整过程报告与GitHub发布准备（2026-09-23T11:58:03.021401+08:00）

用户明确要求把完整计划完成情况、遇到的问题、处理方案和全部主要错误集中成文并上传GitHub。因此新增[CF-MoA完整执行过程报告](cf_moa_experiment_report.md)，与本文的持续研究日志职责分开；报告回顾09-21至09-23，当前1022行，覆盖阶段A–E、A4采用配置、A1-v1/v2各修订、A5/旧F、A2/A3、互补分析、各Router/聚合候选、成本和调度问题、负结果及剩余阻断。阶段历史没有被最新状态覆盖；正式v5、评分及原实验输出保持。

隔离发布工作区为`/home/data3/txy/Documents/Codex/2026-09-23/cf_moa_github_publish`，目标为既有`xiotakut/cf_mrg`的main，包路径`benchmarks/2026-09-23_cf_moa_process/`。发布主稿、本文截至实验交接的快照、原核心计划及精简结果/成本/逐题状态；不上传完整敏感请求、模型正文或大型缓存。已完成发布哈希、242行状态计数/三控制转移、费用和112处链接核验，0模型/原生评分。首次只读摘要探测误用失效会话变量而报NameError，读取前退出后改为明确绝对路径；引用式Markdown链接转换遗漏在发布前修正，未改变研究内容。已实际推送并完成远端字节核验，提交`3c43afa`；[GitHub报告](https://github.com/xiotakut/cf_mrg/blob/main/benchmarks/2026-09-23_cf_moa_process/docs/research/cf_moa_experiment_report.md)可读，发布工作区干净。首次raw媒体读取有两处转义差异，改用Git blob base64后确认四个主文件与发布副本逐字一致，未修改研究内容；完整发布与核验归工作区发布记录（本地制品：`/home/data3/txy/docs/workspace.md#cf-moa-process-github-20260923`）。准备证据位于`Documents/Codex/2026-09-21/cf_moa/publication_report_20260923/`。本次文档任务不解除A3编辑、方法/范围决策或原研究目标阻断。

<a id="baseline-delta-plan-revision-20260923"></a>

### 基于强旧答案的增量协作计划修订（2026-09-23T13:03:50.275591+08:00）

用户审阅截至09:41的公开过程与摘要后，明确要求先更新`cf_moa`核心计划；同时说明GPU2/3是可直接使用的本任务占位空白进程，GPU0空闲。已将其12节审阅、阶段表、关键统计、下一轮顺序、异常分层和S1–S12来源写入[当前核心计划](../../plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md)。原设计要求的全候选审计与完整重答收缩为目标化支持和局部修改裁决，属于新的方法计划，不称兼容修复或已证明有效。本文只记录登记过程，完整方案以核心计划为准。

前置工作为既有6/4修复与14/12误伤的逐条来源/路由/聚合/原生输出归因，未知原因记unknown；绑定有效控制；以旧完整响应恢复A2单独控制的原生parser语义；另版准备不丢患者原文/关键证据的紧凑工具I/O；只做独立集暴露元数据清单。用户已给出这三项原阻断的处理方向，不需要重复询问同一决定。历史目标服务blocked是先前状态，本次没有把完整科研目标标为完成，也不以文档更新冒充上述工作完成。

后续仅预先固定一个A1_delta与一个修改裁决候选，比较强旧B、同预算目标化重答、增量提议＋裁决，另用无条件重生成和证据去除/仅答案控制解释误伤。A3沿用已修复配对runner，随机编辑称合格随机位置而非已知无关；A5另版支持格式双向检验，F不改名。新试验独立登记，不自动恢复旧失败。方法显示增量后再补完整资源控制和必要消融，满足资格与共同冻结后才做独立质量评估。GPU授权单独记录，实际启动再核对资源/占位身份，本次没有释放占位或启动引擎。

版本保全：原26940字节计划SHA-256`4d27d8ddefd639da24e836f7e95728879c192707986130c4af21a1fa6025b522`及原manifest、导航、本文更新前状态已备份在修订证据目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/plan_revision_20260923/README.md`）。新[计划manifest](../../plan/execution_plan.json)绑定新计划hash、旧快照、当前已完成状态与未执行步骤；同步代码AGENTS/README及docs入口。旧development_delivery索引和A3的verify_preservation/verify_sources、旧evidence_inventory准备器含原计划路径/hash断言，继续保留，不因计划更新批量修改或重跑。后续新执行须显式绑定新计划与已有执行逻辑；旧原计划核验解析到字节不变快照，不能宣称旧硬路径仍与新计划hash相等。

实际验证只涵盖文档/配置一致性：独立只读核对小型公开制品本地副本，正确数、原生均分、修复/误伤、可用性恢复、激活分布和3.58/3.18输入token比与审阅一致；完整12节复核没有遗漏。未读取病例大trace或独立gold，未开始第1步逐题归因，未重做矩阵、旧头回放或全范围测试。准备时`git -C cf_moa status`确认这里不是独立Git仓库并退出128；另一只读摘要核查误把summaries列表当字典，AttributeError退出后按列表结构完成，均无实验影响。文档hash、旧快照、新旧绑定与本地链接验收详见收据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/plan_revision_20260923/receipt.json`）。本次0新模型、0评分、0训练，未改原推理代码/生成参数或远端历史包。

<a id="incremental-revision-execution-20260923"></a>

### 新修订计划实际启动（2026-09-23T13:30:21.645740+08:00）

用户明确“继续推进新计划”。已并行启动36条相对强旧修复/误伤trace归因、A2单独控制旧完整响应parser兼容修复、新版紧凑工具合同与独立集暴露元数据审计；根任务准备一个A1_delta与一个局部裁决原型及固定smoke。仅按当前合法输入构造请求，不将离线评分/病例配对引入在线选择，既有121成员与分母不改。资源实查GPU0约94895 MiB空闲、保留其他用户约2462 MiB进程；GPU2/3的80 GiB占位PID810889/811119均为txy的gpu_watch.py，已确认用户资源授权，尚未释放。证据在本轮目录（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/README.md`）。此条为启动而非完成；暂0模型/评分，无独立gold读取。

#### 固定技术smoke放行（2026-09-23T13:45:09.825335+08:00）

前置36条归因、A2原parser兼容缓存验收、紧凑工具合同及暴露元数据清单已完成。用户另明确选择新B接口确定性封装，242条答案值保持，M4 121条/M5 120条满足完整原生schema；M5 d00050保留不可用。新A1_delta和局部裁决为一个独立开发候选；同格式首题d00000/d00001/d00003固定作两骨干技术smoke，不按结果选题。每题B、目标重答、delta裁决、无条件重答四臂，非基线每臂最多2请求、诊断1024＋原生2048，temperature0.7/seed42及采用readout保持，实际费用另记。30实际backend grammar请求与24原型回归通过；独审发现的截断误接受、跨卡提交窗口、非原子首错发布、来源锁与字段/骨干绑定问题均在新调用前修正，失败测试/修改证据保留。GPU0/M4、GPU2/M5并行，启动前只释放已核实的本任务GPU2占位。共享首错原子停止，已飞行正常收尾；每运行仅终态一次累计JSONL导出，SQL持续落盘。见放行manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/smoke/release.json`）。不是共同冻结、质量采用或独立评估放行。

#### 前置审阅与接口修复完成

36条归因的逐题审阅（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/trace_attribution/review.md`）保留原6/4修复和14/12误伤：6份历史JSONL各扫描一次、约156 MB/1.32秒，后续只读选定子集。26误伤中24个正确专家候选已实际送入聚合，其中23个被声明adopt；11个还有采纳MET路径却丢对应选择。直接可见多选收缩、答案与解释矛盾、假设替代当前条件、独立路径丢失和4条目录标签改写。10修复中5匹配正确A1、4是聚合新正确键、1为原生键重表达，不能统一归因协作。36条均满足当时schema；空解释/标点不事后新增失败规则。医学蕴含、因果和别名计分原因未知的字段保留unknown。该36条是诊断子集，不用其ID/gold选smoke或在线策略，不替换121分母；0新模型/评分/矩阵重算。

[A2兼容收据](../../data/a2_parser_summary.json)：新增显式`historical_native_v2`，默认strict_v1及其负结果保持；使用锁定旧parse_states和assemble。18适用请求含配置逐字段相同，两骨干各d00000真实完整缓存响应经实际控制入口均回到[B,E]，M5额外None键仅诊断保留。41测试含8新回归通过、37份旧源hash保持；两次历史executor原费用1674输入/6259输出token、90.932秒单列，当前0新生成/评分。第一次测试预期ValueError而实际正确抛JournalConflict，已修fixture并保留初始日志。不是完整新控制或live验收。

紧凑工具合同（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/compact_control/README.md`）完成50项来源绑定检查，8个骨干×角色profile独立保留；去重阶段说明和历史、保留原文/证据/单位/否定/时间，按实际stage选择facts/catalog/readout/A4。设计已成文，未实现容量与真实运行验收，不能写成同工具控制已完成。暴露元数据清单（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/exposure_audit/README.md`）记录既有资格全文与强控摘要暴露，09-18后全主体用途和家族隔离仍unknown；本次不打开D题/gold/质量分数，不以其选择候选或裁范围。

B合同核查发现旧强组合两骨干各16条为list/str，且M5 d00050旧dict枚举非法，不能直接作为新计划的完整原生回退。先暂停受影响路径并询问，用户已明确选择“新B接口版确定性封装”。新接口（本地制品：`/home/data3/txy/cf_moa/controller/baseline_native.py`）及242行验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/baseline_contract/v2/README.md`）用真实规则/目录执行摘要填32条解释字段，标明非模型推理；210原dict完整保持、全部答案值逐值不变。8测试通过，M4 121合法、M5 120合法/1不可用；d00050继续失败，旧分数未改。全部原始组件记录/路径/行hash和历史费用保留，未截取旧失败半答案。

#### 新增量候选技术smoke终态与负结果（2026-09-23T13:56:24.477953+08:00）

M4/M5各3题×4臂均写完12条，合24个输入×臂；两骨干分别13/15真实调用，费用89676/3586和101932/3514输入/输出token，模型墙钟92.5724/109.6185秒；合28调用、191608输入/7100输出token、202.1909秒。完整分母、原响应、finish_reason和SQL均保留，每骨干仅终态导出一次。0旧专家重生成、0原生质量评分。

**运行完成不代表A1成功**：6/6 A1_delta虽均请求ADD_SUPPORT，但同时输出model_knowledge与可定位knowledge_evidence，触发`unsourced_knowledge_masquerades_as_citation`；合格提议0、真实修改裁决0，全部按事前新合同回退到完整B。M4 d00003两个重答控制草稿在1024输出截断，也按原合同记audit_unavailable，不增加预算或重抽。当前`targeted_support_delta_v1`未建立执行/增量资格，停止扩展该候选，不凭B可用性宣称新增专家成功；后续诊断与方法改版必须另行保留身份。

[独立终态验收](../../data/a1_delta_summary.json)核对28实际EngineCore入口、profile、采样、grammar、token及24个原控制器同缓存响应重放，全部一致，新增验收调用/评分均0。最初收据用technical_smoke_passed表示执行验收，已保留原件并明确改为`passed_execution_audit_incremental_qualification_not_established`，不修改实验结果。

另发生资源释放缺陷：两输出循环已完成且无在飞请求，但engine仍驻留。13:50:37仅对本任务已完成的904149/904159子进程发送SIGTERM，两主Python随后exit0，GPU0/2各释放约97 GiB；不把这项生命周期缺陷改写成模型失败，不重跑28调用。清理证据（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/smoke/lifecycle_cleanup.json`）单列；未来runner的显式退出修复另版、旧冻结源码保持。

#### A3独立配对真实烟测启动（2026-09-23T13:56:24.477953+08:00）

沿用既有`fixed_pair_critical_random_original_rescore_v1`、readout与共享前缀，47个来源保持，旧64回归/224实际tokenizer验收不重复运行。固定合法输入按原顺序前2个适用题d00008/d00011，各12个合格span，两骨干同题；不读gold、归因类别或隐藏配对端选题。三臂为关键编辑、随机合格位置编辑、原题重评分；随机位置允许与关键重合，不称已知无关。editor1024/final2048、采用profile和seed42不改，总硬上限64实际调用。

已绑定新计划与旧执行源的准备manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_smoke_preparation/manifest.json`）。释放已确认本任务GPU3占位811119，13:55左右GPU3启动M4；只有终态无非预期错误才另放行M5。原runner的首错域是本骨干，因此本次顺序启动确保发现错误后不启动第二骨干，不声称已有跨进程屏障。此阶段是独立新试验，不重跑旧A3结果、不解除A1扩展限制、不自动解锁其余6个A3适用输入或独立集。

#### A3固定烟测完成与增量runner退出修复（2026-09-23T14:03:09.566543+08:00）

A3两骨干各2题×3臂完整落盘，M4 32调用/96320输入/1239输出token/23.1076秒模型墙钟，M5 26调用/70457输入/1437输出token/36.3830秒；合58调用/166777输入/2676输出token/59.4906秒。实际GPU3分别运行约50.95/64.17秒，两进程均exit0且显式core.shutdown，GPU3已释放。历史旧A3未重跑；本次shared prefix使用事先规定的readout源，不能冒充旧catalog引擎缓存。

M4四个delete均通过局部资格；M5各题一个delete合格、一个explicit_negation因改动原span其他字符被拒绝，2个输入保留semantic_invalid与partial，不剔除结果。每题三臂都使用同一有效操作数/类型和共享前缀。M4 d00008随机位置与关键编辑完全重合，其余三题无重合；重复评分本身也有小幅边际差异。12臂原生结果可追踪，同一骨干同题三臂答案完全相同，不能据这些smoke称编辑有质量增益或临床因果效应。尚未调用评分器。

58请求实际入口与原控制器回放（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_smoke_preparation/live_acceptance/receipt.json`）已通过，核验真实engine接受、完整profile/采样/grammar、原始题与固定pair、物理去重费用。回放首次将CPU callback墙钟与历史GPU callback墙钟直接比较导致验收脚本AssertionError；仅排除callback_seconds/model_callback_seconds后通过，原模型事件时长、token与语义状态仍严格比较；首次日志保留，0新模型/重评分/原结果修改。后续若扩大，只固定全部合法适用8题而不挑选有利子集，已有效2题复用、另6题单独登记，阶段放行前不调用。

新增量runner资源释放已作独立工程修复`explicit_v1_engine_shutdown_r1`：原guard强闭包形成引用环且main未显式shutdown已由本地vLLM源码/无GPU引用图确认；旧live驻留唯一根因未有堆栈，仍记推断。改为weakref guard、finally调用engine_core.shutdown并关闭SQL，清理异常单列lifecycle.json，不覆盖推理结果或原异常；35回归含11新增通过、12份方法/协议/旧结果hash保持。[修复收据](../../evidence/lifecycle_fix_receipt.json)保留before/diff/after。未为关闭测试重新加载模型，旧smoke源码快照与当前future-runner hash区分。

A1负结果进一步归为接口约定与目标绑定不足，而非M5特有或总token耗尽：6个诊断仅96–173输出token；prompt说明model_knowledge及visible_source需引用，但model_knowledge必须knowledge_evidence=NONE的逆向条件只在validator显式，不能把全部失败归咎模型。另有知识条件讨论非当前target，M4 d00001知识条件到320字符边界；不通过忽略引用错误或抽取字段改为成功，也不自动增加预算。[诊断决定](../../data/a1_delta_summary.json)保留当前候选未通过资格及0裁决身份。

#### A3完整适用范围的有界开发阶段启动（2026-09-23T14:14:38.558832+08:00）

在两骨干实际smoke及[独立复核](../../data/a3_development_summary.json)完成后，按核心计划推进一次完整受控开发，不按smoke正确性或已有误伤类别选题。固定既有每骨干121输入中全部8个A3适用题，113个不适用成员原样保留。d00008/d00011同请求有效结果与真实成本直接复用；剩余d00021/d00035/d00051/d00068/d00070/d00077另建阶段，每骨干6题×3臂，最多192新增实际请求。

新manifest（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_development_preparation/manifest.json`）SHA-256为`c3d3927e136a53446fb613e0b3f6c860774f30ca190904fbbc96a59249c0027a`；原A3 plan除输入子集完全相同，方法核、prompt、readout、参数和输出合同不改。薄CLI复用已验收共享stop/真实transport guard及显式shutdown，RunJournal新增首错原子发布；peer-stop先记本地journal再抛，避免旧核内部catch把停止伪装成功。3项独立协调回归验证首错传播、在飞收尾/后续不发及允许partial不触发首错；M5旧烟测拒绝编辑不删除、不重判。两default inspect通过，未授权release试验在输出/模型之前被拒绝。

已核全部源hash，单独release后GPU2/M4与GPU3/M5同时启动；GPU0出现其他任务，未触碰。每卡首错或共享首错均阻止后续提交；已飞保留。运行前离线质量协议（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_quality_analysis/protocol.json`）与脚本哈希已冻结，只有两骨干8题齐全且无停止才能读取开发offline评分；报告强旧B、同readout共享前缀、关键/随机/原题重评分及修复/误伤/不可用。8题面板不冒充121主表或独立评估；新A1/A5及独立集均未放行。

#### A3完整开发推理与终态验收完成（2026-09-23T14:21:16.588062+08:00，评分前）

新增两骨干各6题全部完成：M4 93请求/327229输入/4695输出token/84.4231秒模型墙钟，M5 75请求/239256输入/4012输出token/101.1928秒；GPU2/3同时运行约116.82/134.83秒。两进程exit0，新的weak guard＋显式close在本阶段真实运行后均记录engine_shutdown、journal closed、无清理错误；未为生命周期修复单独重跑模型。实际共享首错文件不存在，无基础设施/schema失败、无在飞/未知费用。

加直接复用的烟测，完整8题×两骨干×三臂共48结果，物理费用226请求/733262输入/11383输出token/245.1066秒；共享前缀按物理请求只计一次，不能把三臂logical_cost相加当实验费用。原121分母及113不适用输入不变。这是独立A3开发候选的实验总费用，不是单臂独占延迟或整个MoA总费用。

M4完整8题总15个编辑通过/1个拒绝；M5总8通过/8拒绝，拒绝分布在7题。M5 d00077两个编辑均不合格，仅7次共享调用，三臂均按原合同保留目录结果和partial；没有原生final生成，不能把48臂结果写成48次真实final，本面板真实final为45次。拒绝、能力与原生答案可用性分别记录，没有删除任何输入/臂/失败编辑。

开发终态验收（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_development_preparation/live_acceptance/receipt.json`）核对新增168实际EngineCore请求、profile/参数/grammar/token、12个新输入的原控制器同响应回放及逻辑/物理成本，全部通过。旧烟测只核冻结hash，不重复回放/生成；验收0模型/评分/gold。完整统计与结构分别见[费用](../../data/cost_summary.json)与[执行结构](../../data/a3_development_summary.json)。

评分前独审发现原score.py门禁未在读标签前断言精确三臂，且检查的是旧runner不写的status.shared_first_error。尚未执行该脚本、未读取开发gold；修复另存score_v2.py，保留原绑定脚本与方法/评分协议，补精确48臂、完整8ID及实际stage release共享latch不存在等检查。只加强离线完整性门，不改原生评分或选择输入；门禁通过后才做一次开发评分。

#### A3原生开发评分、未采用与本轮交接（2026-09-23T14:25:19.709074+08:00）

评分门禁修复另版`score_v2.py`，SHA-256 `3a6ba91d5884a0eec4521346bfbca22820135afc685848571a62f59fbb4b70b7`，原score.py与预先固定协议不变；26项正反门禁与实际48臂/B完整性检查通过，独立AST对比确认原correct、比较、count gate表达式未变。完成真实入口验收及该门禁后仅执行一次离线脚本，exit0；五种方案×8输入×两骨干共80条原生评分判定，0新模型/独立gold访问，旧native scorer及历史评分不改。新代码仅增加前置完整性检查及描述性原生record/单元统计，不重新选方法或输入。

| 固定8题开发方案 | M4正确/8 | M5正确/8 | M4覆盖4个非参考单元均分 | M5覆盖4个非参考单元均分 |
|---|---:|---:|---:|---:|
| 新B接口版（原答案值保持） | 3 | 4 | 50% | 50% |
| 同readout共享前缀目录结果 | 3 | 4 | 50% | 50% |
| 关键局部编辑 | 4 | 3 | 75% | 25% |
| 随机合格位置编辑 | 3 | 3 | 50% | 25% |
| 原题重复评分 | 4 | 4 | 75% | 50% |

每个方案原生映射8条，答案不可用0；其中M5无编辑资格的d00077按预定部分适用回退保留，不称编辑成功。上表仅固定A3面板与其覆盖的4个非参考单元，不能替换原121输入/157映射/74单元主结果，也不是独立泛化成绩。两个指标权重不同，分别列出。

相对强旧B，M4关键臂修复1、误伤0（d00070），但同预算原题重评分修复同一题；相对重评分修复/误伤均0。M5关键臂修复0、误伤1（d00068），随机臂出现相同误伤，原题重评分保持B正确性。两骨干预先定义增量gate均false，故`fixed_pair_critical_random_original_rescore_v1`**不采用**，继续使用已采用旧目录核，不通过追加编辑prompt/grammar/预算轮次改名宣称成功。证据包括[原生汇总](../../data/a3_development_summary.json)、[逐题结果](../../data/a3_input_status.csv)、原生覆盖单元（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/incremental_revision_20260923/a3_quality_analysis/results/native_unit_metrics_panel.json`）与[未采用决定](../../data/a3_development_summary.json)。

本轮累计254次真实新模型调用：A1/控制技术smoke28、A3完整配对实验226；924870输入/18483输出token，累计记录模型墙钟447.2975秒。该合计是实验实际物理费用，历史B成本另保留在来源和方法账中，不将跨臂共同前缀或复用smoke重复计费。GPU0/2用于新增量smoke，GPU3用于A3 smoke，GPU2/3用于A3开发并行；本任务已全部退出，其他用户GPU0/1作业未触碰。[成本账](../../data/cost_summary.json)与每个journal/逐题trace保留。

已完成的底座继续复用：新B接口、A2原parser兼容、来源与范围隔离、真实入口/首错/生命周期验收；两个新增机制本轮均未取得增量资格。下一阶段仍为新A5合格格式双向面板与短诊断合同（尚未实现/推理）；A1进一步方法改版须另定有限候选，不能自动重试当前失败版。完整同工具控制/必要消融依赖新的增量证据，独立范围资格未知、共同冻结和独立质量评估继续不放行。此次不是完整Router＋五专家方法验收成功。

终态[独立计数复核](../../data/a3_development_summary.json)仅读已评分制品，80行唯一输入×方案、80原生行与10组unit报告全部一致；没有再读原offline gold或重跑评分器，不能当作独立原生标签复现。新增[本轮交付索引](../../evidence/development_delivery_index.json)绑定22份主要收据、决定与成本，源码/配置/逐题trace见各收据；不是共同冻结清单。


<a id="cf-moa-report-v2-20260923"></a>

### 版本2过程报告与发布交接（2026-09-23）

按用户要求，在既有[完整过程报告](cf_moa_experiment_report.md#incremental-revision-v2)续写修订计划、新B接口、A2缓存兼容、A1_delta与A3真实受控检验、错误/修复和成本。报告实验截止14:25；前十章保留09:41历史状态，第11章承接本轮终态，不用新8题面板覆盖旧121题比较。公开副本另建版本2目录，旧发布包不覆盖；病例全文、答案/gold和完整模型trace留服务器。研究结论不因出版改变，本次0新模型、0原生重评分。发布和远端核验归工作区记录（本地制品：`/home/data3/txy/docs/workspace.md#cf-moa-incremental-v2-github-20260923`），构建证据在发布包（本地制品：`/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/publication_v2_20260923/README.md`）。
