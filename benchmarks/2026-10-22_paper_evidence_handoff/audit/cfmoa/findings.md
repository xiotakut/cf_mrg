> 轻量阅读副本：下文“本包”、原路径和历史核查状态按完整交接包的范围理解。本轻量目录真正交付哪些文件，以根目录 `EVIDENCE_INDEX.csv` 和 `SELECTION_AND_VALIDATION.json` 为准；缺少的层不能视为已经取得。

# CF-MoA证据审计（2026-10-22）

本记录是交接包的审计证据。只扫描、读取、复制/编码与从保存分数重汇总；没有训练、模型推理、预测、评分器或新人工打分。本次首先独立枚举实际文件、查看运行输出字段及收据，再查研究文档与论文主张。论文/底稿没有被用来证明实验完成。

## 检查范围与状态语义

完整文件枚举在 `audit/cfmoa/scanned_files.json`，共11,300文件，根目录是 `/home/data3/txy/cf_moa`、`Documents/Codex/2026-09-21/cf_moa`、`2026-09-23/cf_moa_minimal_revision_20260923`、`2026-09-24/cf_moa_candidate_verify_20260924`、同日`cf_moa_v4_trigger_diagnosis_20260924`和`cf_moa_rcv_completion_20260924`。09-21原运行包约10.55GB，RCV包约62.89GB，包含重复快照及SQLite；这些体积不能当作独立实验数量。另读取`docs/research/cf_moa.md`与相关LaTeX表格来提取待核查主张、采用决定。未对这六根目录之外的所有服务器路径穷尽搜索；因此下文“未找到”均限此范围。

`runs.json`包含12个主逻辑方法/骨干行、6个123输入操作消融行、232个有非空运行输出佐证的物理执行/缓存/fixture行、2个明确延后项目及1个初次队列未启动项目，共253行。物理行不是253项独立实验，不能相加分母或调用次数。带`fixture`、`replay`、`complete_run`、`assembly_new_model_requests=0`的记录明确另标；旧脚本/计划存在与真实推理完成不等价。对子目录内只有准备脚本、测试日志而没有运行结果的项目，保留准备身份。

## 已核对的论文主结果

主源根：`/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/`，下称`RCV/`。

- `full_v5/analysis/{m4,m5}/native_scored.jsonl`各93,696条，即六臂×15,616原生映射；逐行与`offline/evaluations.jsonl`的`record_id/request_id`及`offline/items.jsonl`连接，无重复键/缺失连接。各臂`per_input_status.jsonl`都有13,905唯一request_id。核查结果在`join_checks.json`。
- `native_units.jsonl`、`pairs.jsonl`和`per_input_status.jsonl`重新汇总72个类别均值、24个pair计数、12个输入正确数、132个来源分层值、60个格式分层值，与保存汇总一致（浮点容差1e-10）。归档统计脚本原样复制至`scripts/cfmoa/summarize_existing_results.py`，以`--draws 5000 --seed 240924`对保存分数重复家族bootstrap；36个点差和36个区间一致。新输出在`reaggregation/`。本次不调用原评分器。
- ALL是6,104个非reference原生单位等权均值，不能用13,905输入准确率替代。类别单位分母R1/R2/R3/R4/R5为2,866/79/733/13/3,600，类别重叠，不能相加得到ALL。13,905输入含reference侧；pair正确要求两侧均正确，保持/响应对为6,838/1,780，按family分组配对bootstrap保留单位权重，不先把每family压成等权均值。
- B相对C0的ALL变化：M4 48.198995%→58.292377%，+10.093381pp；M5 47.348733%→59.361621%，+12.012888pp（完整精度以`tables.json`对应行及保存`quality_summary.json`为准）。C3相对B：M4 −1.810834pp，95%区间[−2.528730,−1.081938]；M5 +0.927261pp，区间[+0.303853,+1.556159]。两骨干方向相反，不能把B−C0当作新增候选验证模块增量。
- 原生不可用不是错误答案同义词，仍保留全分母并以0贡献端到端成功率：M4 B/C2/C3/C5各51不可用、C4为157；M5对应各22、C4为86，C0为0。完整`quality_summary.json`和`per_input_status.jsonl`保留错误与不可用分类；未删失败行。
- 123输入共享支持消融：保存738条`operation_ablations/per_input_status.jsonl`和738条`native_scored.jsonl`，按每骨干×3臂×123重汇总一致。M4 B/禁add/禁remove正确69/43/53，M5为71/48/60；不可用分别1/14且每臂都保留；禁add修复/误伤3/29与4/27，禁remove为2/18与0/11。记录在`operation_reaggregation.json`。这是完整规则能力子集，不是旧121/52面板，也不是13,905全量新的系统结果。历史`receipt.json`记53条新评分发生在原机制实验；本次仅读取保存分数。
- `closeout_20260928/costs/per_input_cost_coverage.jsonl.gz`按method/arm重加保存归因字段，48个方法费用字段与`per_method_costs.json`一致（详见`cost_reaggregation.json`）。C0共同上游费用未知，不能填0；每骨干每方法2,503旧head输入缺模型耗时，已知费用小计不能称完整端到端时延。当前full-v5物理请求162,979是跨臂实际执行库存，不能除以六或将各方法继承成本相加。物理对账保留M4 39与M5 36个“physical minus final rows”差额；M5还记录28次失败callback、108跨运行回放事件。见`costs/physical_reconciliation.json`、`transfer_cost_reconciliation.json`。本次复核保存的逐输入归因总和，没有重新测量耗时。

表级/单元级映射在`tables.json`（含12个不可用计数、2个C3额外请求差值及4个支持消融差值）。另直接解析当前活动LaTeX八张CF数值表与主系统表B两行，共268个数字字面单元均按其小数位与重汇总一致，见`paper_literal_checks.json`；并在`HANDOFF_ONLY=1`下仅从交付manifest读取评分通过186项便携复算，见`portable_recheck/validation.json`。它们有充分证据支持**已暴露v5上的描述性结果和有限机制消融**；不是独立确认、临床泛化或选择校正推断。

## 逐层记录的含义与连接

`full_v5/inference/{m4,m5}.jsonl`每行有request_id、native_input、baseline_answer、baseline_response、original_context、answer_schema。`original_context`是真实原消息，往往已嵌入检索文档；另一个`retrieved_context=[]`字段不表示没有检索上下文。参考答案、role、labels在单独`offline/evaluations.jsonl`；`offline/provenance.jsonl`关联request_id、item_id、family、record_id与原C0输入/预测/评分文件行号及hash。只有在包中已交付或GitHub确有原文件时，这些路径才可供另一个agent直接读取；服务器路径本身不算交付。

`full_v5/analysis/*/receipt.json:input_sources`给出实际参与终态汇总的cache union和分片proposal文件及SHA；M4有8源，M5有11源。每个`proposals.jsonl`以task_id=`request_id:arm`、method、input_hash联结结果、已解析native_answer、callback/费用；同目录`model_calls.jsonl`保存request.messages、schema、seed、温度、result和physical原始response。实际原文不在`native_scored.jsonl`：后者仅逐项评分与来源元数据，不能叫完整模型原始记录。

对大JSONL采用`evidence/exports/cfmoa/`与`evidence/exports/cfmoa_tail/`两个不重叠源文件分区内容寻址无损交付：保存每源path/size/SHA、每行原字节SHA与编码方式、原始JSON字段，长字符串以SHA256块引用去重，保留失败、重试、缓存条目及所有样本。`source_exports.json`是交付原路径清单；它与`export_receipt.json`、解码验证收据一起判定是否完整。目录扫描中未交付的SQLite和重复物理副本应在总manifest标为“仅有索引，尚未交付”，不可用“已找到”替代“已交付”。

## 实际方法与版本绑定

以下主要组件在`RCV/method_spec.resolved.json:method_source_bindings`保存哈希；本次20项主要实现/分析脚本/评分源hash核查都相等，见`version_checks.json`。这是局部版本证据，不证明所有传递依赖、解释器/库、模型权重运行时版本均已锁定。完整运行时依赖闭包及模型checkpoint哈希未在上述核查范围建立；必须写“运行时完整版本未核实”。

1. `cf_moa/controller/strong_legacy.py:select`按当前能力固定优先级：诊断格式→旧目录核；药物规则eligible→共享规则核；完整给定模型capability→A4；single/robustness_single/relation且有结构原消息→F；否则原透传。代码不按离线R标签选择专家。`minimal_operations.py:operation_record`把规则核标为A1/A2，目录核A3，给定模型A4，F为A5；没有五独立模型同时讨论或全局生成聚合器。
2. `minimal_operations.py:rule_operations`从一次原规则执行投影MET/CONTRADICTED/UNKNOWN、add/remove集合，仍调用旧assembler；None互斥、UNKNOWN继承、无效初答等旧政策保留。123规则消融把选定状态在独立组装视图映为UNKNOWN，不能写成重新事实提取或训练两个模型。
3. `agents/a5_candidate_verify.py`只在旧F普通投票路径处理已生成合法candidate，取每个key最早完整原response；C2不附保存理由、C3附不受信任的保存理由。每个candidate两次A/B编码交换，分别softmax归一后平均TRUE概率，选最高并返回所选既有完整response。它是未经校准的排序信号。无效旧vote留trace但不变成candidate。NLI路径仍用旧F。C4旧F投票池加三次普通生成；C5同candidate和理由联合选择。见`controller/moa_rcv.py`、`agents/a5_pool_expansion_control.py`、`agents/a5_joint_selector.py`。
4. 实际各片`runs/*/plan.json`嵌入protocol/profiles、选中input/task ID和`scheduler_source.sha256`；示例`full_v5/batch8/runs/m4/plan.json`及M5尾片plan绑定调度源`db06c973...`。运行model_calls physical.request另保存engine kwargs和真正调用参数，优于用当前config文件名猜版本。目录取分temperature0/max_tokens1；事实抽取temperature0/max_tokens2048；普通F读出temperature0.7/max_tokens2048。Qwen的enable_thinking=false、YaRN等在profile/physical request；具体每次请求以其实际记录为准。缓存继承源不自动被新调度器hash“覆盖”为同一次新运行。
5. `analysis/*/receipt.json:scorer_sources`保存原analyze_cf_baseline_screening.py、prepare_cf_baseline_screening.py、canonical_labels.json与native_scoring.py hash；分析脚本hash为`ce260398...`，本次逐一核对。C0复用旧原生评分；其余whole-response缓存键包括骨干、完整response、完整eval映射（除本地request handle）、输入和scorer身份。评分器代码只阅读，未执行。
6. `closeout.../costs/per_input_routes.jsonl`实际27,810条路由为每骨干3,560目录、123规则、10,178 F、44透传、**0 A4**。因此R4的13标签单位仍在全量分母，但论文不能说临床v5验证了A4真实执行；给定模型实验另见heads子审计。

## 方法选择及发现的历史负结果

这些记录的“原因”来自保存decision，不是本次根据最终分数推造动机；执行还需与表内非空proposal/model_calls/评分文件合读。

- 默认B身份在`2026-09-23/cf_moa_minimal_revision_20260923/decision.json`明确为`adopted_B_five_operations_v1`。242缓存B接口等价，F普通重答不开启。保存的理由是历史121小幅增量未在预定自然52稳定保持：三个seed的M4为34/31/32（B35）、M5为25/23/24（B26）；全231新请求已落盘，不用最好seed替代完整报告。`analysis/combined_summary.json`及seeds/natural_runs原始制品在清单。
- `RCV/closeout_20260928/method_identity.final.json`与`final_status.json`继续默认B，C3=`cf_moa_rcv_rationales_v1`只是research_extension，`research_extension_default_adopted=false`。主结果的跨骨干反向不能解释为最终C3被采用。
- 09-21 `freeze_preparation/a1_r5_non_adoption_decision.json`保留A1 r5两骨干121输入：55/42正确、30/61不可用；`a1_v2_relational_20260922/relation_codes/complete/*_scores/complementarity_inputs.jsonl`为逐项证据。M4旧sampling_development停在59完成、1失败、57未提交；加4个smoke合63完成，不得伪称完整121。
- `a5_f_preparation/a5_non_adoption_decision.json`明确新A5复判未采用、转向真实旧F；不应把F改名成新A5候选成功。`single_agent_preparation/stable_tool_json_r2/development/*/status.json`有M4 7完成/1失败/107未提交，M5 67/1/47；有对应非空输出，但不是完成的同工具单agent质量对照。
- `a2_control_preparation/live/smoke` M4 1完成，M5 0完成/1失败，严格包装拒绝额外None键；后续原parser兼容修复/回放不能抹掉该次失败。四项CPU控制与此未完成模型执行对照属于不同实验。
- `router_aggregation_preparation`发现多版实际聚合及失败，不能仅保留最后完整表。v2 crossfield扩展0完成/1失败/115未提交；简洁原生解释v3扩展M4 46/1/68；先证据v4停在31完成/1失败/210未提交（包括smoke后完整分母）；后续完整含A1聚合以242两骨干121输入组装与原生评分保存，79/74正确，低于B87/82，未采用。各版先后和确切计数在对应status与`docs/research/cf_moa.md`阶段记录；不是同一最终方法的额外样本。
- `incremental_revision_20260923/smoke/negative_diagnosis/decision.json`：A1_delta 6诊断全部不可用、0裁决，无资格扩大。`a3_quality_analysis/non_adoption_decision.json`记录A3真实固定8输入×三臂：M4关键编辑4/8与原题重评分持平，M5关键编辑3/8低于B/重评分4/8，不采用。
- `effect_first_revision_20260923`实际cycle1–4与全部输出均保留。cycle1 light_A1 M4/M5 19/23低于B24/28；A5 89/83与匹配redo同正确数。cycle2 A1主臂19/23、控制21/23，A3主臂2/3低于B3/4，A5 scope32与普通重答30/31相同。cycle3和cycle4也未采用；cycle4固定34主臂18/15低于B23/19，M4 d00077三臂截断、M5 d00050旧B不可用保留。决定文件分别为`non_adoption_decision.json`、`cycle2/decision.json`、`cycle3/decision.json`、`cycle4/decision.json`。这些是已执行负结果，不是仅计划。
- 候选验证09-24初始队列与`recovery_gpu23`分开保存；初始初始化失败不因恢复成功消失。`full_v5/readout_parallel_m5_20260926/gpu2`和`gpu2_recovery1`及尾片属于同一M5逻辑实验，不新增数据独立性。历史自然52的M5 C0保留48/52，不用新版full-v5 C0齐全反推自然52四缺项已补。

上述历史行的大部分没有进入主表，是方法开发/负结果/失败来源；各运行有非空制品而未找到显式采用原因时，注册表保持“未核实采用理由”，不根据分数猜原因。

## 验证范围与尚未闭合证据

`RCV/confirmation/`81个文件包括准备脚本、draft plan、inference输入、缓存可行性与测试，不是实际确认预测。`method_spec.resolved.json:confirmation_seed_replica.state=implementation_prepared_not_frozen_or_run`；`closeout.../final_status.json:not_executed_or_deferred`明确冻结后新family确认与独立F池复本未执行/延后，natural52 M5 C0四旧缺项也未补。故三者属于**未执行（显式状态有依据）**，不是仅凭文件缺失推断未执行。

完整v5是历史暴露开发范围；121历史、52自然面板与后续扩展均参与方法/提示选择，不能从“范围冻结”“同样本缓存回放通过”“旧held-out参数profile”推导独立临床验证。即使新的源码hash锁住，也不能使已经看过结果的v5转为确认集。

尚需在主交接中明示：大文件是否真正交付以总manifest与source_exports为准；20项局部source锁吻合并不构成全部运行环境/权重版本担保；原C0共同费用和旧head部分耗时缺失；本次统计一致验证覆盖保存分数与汇总，没有重新评估评分规则的医学正确性、源标签正确性或所有旧运行的结论真实性。对于找不到明确原因的放弃项目，保留“未找到依据”，检查范围就是本节列出的文件树和相应研究记录。


### 补充：候选验证初次 complete 状态的失败含义

`cf_moa_candidate_verify_20260924/runs/m4/status.json`保存 status=complete、complete=8，但 verification_failed=8、verification_fallback_saved_F=8、submission_attempts=32、failed_attempts=32、physical_model_requests=0；且显式标注 `complete_means_execution_finished_not_verification_success=true`。因此该物理片为初始化/核验失败后旧F回退，不是8成功新生成。`queue/user_stop_receipt.json` 的 `M5_never_started=true` 只证明初次M5队列未启动；恢复路径的后续实际执行仍单独保留。registry已分列该计划项，不能从仅 complete 字面判成功。


最终主表的物理源选用也逐项标明：19个 `analysis/*/receipt.json:input_sources` 中17个运行分片proposal直接匹配物理registry行，另2个为已完成缓存union。17行标为间接进入逻辑六臂主表、不是新增表行；GPU2失败/恢复等未直接列入终态源的记录保留费用/失败审计身份，不能只从路径缺席排除其经缓存复用的可能。


### 2026-10-23 在 data4 重建

原交接包因磁盘空间已由用户删除，本轮从原会话脚本和仍存在的原始证据重新构建。旧审计中“初次 M5 队列未启动”行的骨干文字曾误写 Qwen2.5-7B-Instruct，现依据原 plan 的 `protocol.profiles.M5.model` 纠正为 Qwen3-8B；仍保留未启动身份，不改变实验事实。旧值、新值及原 plan SHA-256 见 `audit/rebuild/cfmoa/metadata_correction.json`。所有原实验文件保持只读。


### 原始JSONL交付最终验证

两分区共484源、369,431行、34,880,293,192原字节，压缩容器410,138,839字节；独立解码逐行SHA与整源SHA全部通过。21个历史最终输入/分析源哈希绑定全部一致，凭证扫描0命中。453源关联registry行，31源只有明确原目录和记录内来源，未补造独立运行身份。21个空原件也保留，不代表执行完成。所有原始行均保留，不能把导出行数当样本数或模型请求数。详见`audit/cfmoa/raw_delivery_validation.json`和两个`evidence/exports/cfmoa*/decode_validation.json`。其他原件的实际交付状态以总manifest为准。


### 最终原始调用与proposal任务连接核查

从交付的两个压缩分区仅读取保存字段，19个full-v5物理目录的proposal.task_id都按物理目录＋模型与model_calls.request_id连接：43124条保存callback的proposal全部存在对应raw任务记录，模型字段全部与源目录一致。总113442条proposal、163154条raw调用记录；后者不是去重物理请求数。57个raw任务无同目录终态proposal，保留此未闭合状态；其失败、重试或跨目录复用归属须结合日志，不能仅凭集合差推断，也不能删除或算作正确终态。此核查是任务ID覆盖，并非逐callback载荷完全相等或重试身份的穷尽裁定；cache union仍由另存历史来源及SHA绑定。详见`raw_task_join_checks.json`和`scripts/cfmoa/check_raw_task_joins.py`。


本轮重建最终核验：484源、369,431原行、34,880,293,192原字节，独立逐行及整源SHA全部通过；15项旧范围/数量与任务连接对照、186项仅从本地交付内容读取的保存分数重汇总均通过，见 `audit/rebuild/cfmoa/equivalence_check.json`。本轮没有模型调用、训练、原生评分、原件改写或实验进程操作。按用户随后明确的发布范围，完整证据仅保留在 data4 本地，GitHub写作入口使用root维护的轻量 `writer_starter`，本子任务未生成大tar发布附件。
