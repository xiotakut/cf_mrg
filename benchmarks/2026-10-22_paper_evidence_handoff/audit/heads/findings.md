> 轻量阅读副本：下文“本包”、原路径和历史核查状态按完整交接包的范围理解。本轻量目录真正交付哪些文件，以根目录 `EVIDENCE_INDEX.csv` 和 `SELECTION_AND_VALIDATION.json` 为准；缺少的层不能视为已经取得。

# R1–R3、R4/A4与R5证据审计（2026-10-22）

2026-10-23重建说明：原交接包因data3空间不足被用户删除，本文件从原会话保存的创建内容与修正恢复，以下2026-10-22数量、字节数和整理过程属于历史记录。当前data4重建的执行、计数与验证见`../rebuild/baselines_heads/rebuild_status.json`；压缩容器的时间戳/字节数可以不同，源身份与解码内容重新核验。旧导出器失败证据见`../rebuild/baselines_heads/historical_export_failures.json`；本次没有重演已经修正的错误，也没有新模型调用或评分。

本审计先递归遍历实际文件，再读取研究记录和论文定位主张。没有运行模型、评分器、预测解析器或实验代码；重汇总只对已保存 `correct`、`original_correct`、`joint_numeric_correct`、`all_outputs_correct` 求和。未改原件。论文与研究记录仅用于主张、选择理由和线索，完成状态以实际请求、响应、评分、runtime相互支持。

## 检查范围与交付范围

物理扫描：`Documents/Codex/2026-09-14/new-chat/`，09-16下除发布副本外各研究目录，09-17全部head目录，09-18/r5_head。扫描排除`.git`、`__pycache__`、python依赖副本和文档迁移副本，记录8669文件，约8.00GB；199个逻辑实验/研究准备目录分层登记。`inventory.json`为完整范围索引，`runs.json`加29个论文精确运行入口；它们不能跨行相加为实验总调用数。09-14以前的七基线及CF-MoA系统运行由其他分工核查，本审计不据这些范围之外的缺失推断“从未执行”。

候选交付7104文件约2.456GB原始文本，逐文件gzip估算233.2MB（尚可哈希去重）。主表head链、A4保留集和ASCENT/CUPCase验证优先保留实际请求与原响应；历史未采用方案保留全部已发现逐项评分、代码、配置、汇总和关键日志，大型历史上下文/请求/训练特征按`omitted_files.json`逐件标“仅有索引，尚未交付”。服务器路径不能替代交付。最终交付情况以总FILE_MANIFEST为准。

A4 `physiology_head/v2/heldout/executions.jsonl`共1127行（不是288×全部投影臂）：全行导出为`evidence/exports/heads/a4_heldout_executions_semantic.jsonl.gz`，仅去掉`factual_trajectory.trajectory`和`counterfactual_trajectory.trajectory`两个长数值数组。全部ID、plan、action数组、执行值、错误及求解器字段保留；每行附原行号、原SHA与被省数组的规范JSON SHA。完整模型响应另在两骨干`matched_raw.jsonl`，不能把该语义导出叫完整轨迹。导出规则与SHA在`a4_execution_export_receipt.json`。

## 论文表值的直接核对

`tables.json`共136单元，其中122单元已用保存逐项分数重新汇总，均与论文主张一致；14个恒None单元仅有既有摘要，本次没有重新生成或评分。`scripts/heads/reaggregate.py`和`source_checks.py`记录输入和筛选口径；`reaggregate_packaged.py`经FILE_MANIFEST读取包内保存分数，可不依赖服务器重算。

七系统固定顺序M0/M2/M3/M4/M5/M6/M7：

- R1，2866单位：原861/898/766/798/819/858/901，head1329/1323/1260/1225/1367/1317/1331。来源`09-16/r1_head_experiments/core_r1_scored.jsonl`。
- R2，79单位：原7/6/27/23/33/15/23，head29/23/43/39/46/38/37。head来源`09-14/new-chat/r2_question_scope_analysis/positive_facts_scored.jsonl`，只取`policy=inherit_unknown`；原答来源`r2_program_all_methods/scored.jsonl`只取`baseline`。
- R3，733单位：原131/181/63/223/185/157/212，head338/340/238/386/443/305/349。来源`r3_calibrated_all_methods/complete_head_scored.jsonl`。
- R3四控制臂680单位由`r3_calibrated_all_methods/scored.jsonl`的`variant`分别重汇总；七系统共28个单元一致。M4 203/339/359/359，M5 160/382/402/410（original/order0/uncalibrated/calibrated）；不支持“校正对所有系统有增量”。
- A4给定模型保留集288题×2骨干×4论文臂×3指标共24单元一致：typed patch二元/联合数值/完整输出两骨干均288；full联合数值M4/M5为270/222；普通重答联合数值0/0；patch_no_do为67/67。来源`09-17/r4_structural_head/physiology_head/v2/heldout/scored.jsonl`。数值容差1 mg/dL。
- ASCENT47目录单次38/39、未校正39/39、校正38/39。CUPCase三批4+8+6=18条：单次15/18、未校正16/17、校正15/16、字符归一15/14。重汇总文件与筛选见`source_check_reaggregates.json`。不能把2例adapter/格式探针再加进18分母。

**R2恒None证据边界。** `09-16/r1_r2_evidence_audit/r2_checks.json`保存`same_coverage_none=48/47/58/58/56/52/54`，对应脚本`check_r2.py`在当时构造此控制。定向检查09-14/new-chat、09-16/r1_r2_evidence_audit及r2_r3_paper_audit，未找到恒None独立逐项评分文件，故本次只保留摘要。`positive_facts_scored.jsonl`的`support_only`总分恰相同，但它在9道保留题为5/9，绝不是恒None的0/9；不能用它冒充恒None逐项记录。审计初次尝试这一代理后已纠正，收据`audit_correction_constant_none.json`保留过程；这不是论文原始数值冲突。

## 运行身份、复用与证据层

七系统head不是七条完全新在线流水线。R2以及R1/R3的规则分支使用两套原骨干facts，离线组合每系统自身已有答案；同一facts不能按七方法重复计算模型调用。`r2_positive_facts_{llama,qwen}`各有71新raw和128复用raw；输入223条含24透传，因此“223 inputs”“71新请求”“199已有事实输出”不是同一分母。native55事实中各27新/28复用的既有记录在`r1_r2_evidence_audit/r2_checks.json.physical_fact_provenance`，本审计没有将回放当新增生成。

R3新增五系统 `r3_calibrated_all_methods/m*/raw_calls.jsonl`按(item_id,order,forced_code)检查唯一：M0/M2/M3/M6/M7分别3840/3354/3840/3840/3840，总18714；另486复用。R1新增五系统1100诊断部分相同键下6600/5838/6600/6600/6600。M4/M5与旧40/128/552分段及先验调用须按既有request来源拼接，不把最终`scored`全范围再算一批推理。

自行连接三head的(method,item_id)，R1∩R2=4、R1∩R3=733、R2∩R3=3；联合2941唯一单位。交集分别28/5131/21方法×输入条，保存correct/invalid全部相同，见`head_overlap_recomputed.json`。3678类别成员数不能称3678独立病例。

核心材料分层：

- R1/R3诊断 `inputs.jsonl`含item、original_answer/response、original_prompt和provenance；`requests.jsonl`含item_id/order及实际渲染prompt；`raw_calls.jsonl`含原单token响应与49类logprobs；`scored`含解析答案和冻结正确性。这是有实际模型原记录的目录，不能把单独`scored`元数据称为原始模型记录。
- R2 `inputs.jsonl`含item、documents、initial_response/answer；`requests`含messages/schema；新`raw_predictions`及`reused_predictions`都含raw_response，复用行另有provenance；`extractions`/trace与评分分层保存。head实际请求只见当前问题与选项，documents保存在输入包装不等于送给提取模型；以真实messages为准。
- A4 `inputs`给定模型与状态，`evaluation`参考答案，`matched_requests`实际prompt/schema，`matched_raw`原响应，`executions`工具动作/轨迹，`scored`冻结指标，`matched_runtime`记录864/864。三模型臂redo/full/patch产生864调用/骨干；no_do/inline是保存输出的CPU投影，不再算模型调用。
- `layer_key_inventory.json`记录上述代表目录实际字段与行数；其余历史系列只完成文件层盘点，未对每一行做语义审查。缺失层和过大未交付层不合并称“完整”。

多数早期head目录有源码、配置、runtime和回放收据，但没有能对每个历史调用绑定的当时源码SHA/提交号；RUN_REGISTRY应保留“运行时版本未核实”。本次哈希只能证明当前交付字节，不可倒推运行版本。A4例外较强：冻结方法副本、`heldout/frozen_code_comparison.json`运行后unchanged收据存在，当前6个核心代码/配置逐字SHA亦相等（`a4_frozen_hash_check.json`）；这仍不等于所有依赖、模型权重都已绑定不可变版本。

## 方法事实与选择边界

R2实际入口见`r2_positive_facts_llama/r2_condition_head.py`：先eligible；一次模型抽事实；clean_extraction；execute_scoped；assemble；不可覆盖或无效事实回退同一当前题初答。三值规则及UNKNOWN继承由`r2_program_head.py`/`r2_action_scope.py`实现；71规则、55覆盖/24透传有保存trace和审计支持。句ID合法不保证语义正确；历史最终s001058对用药意图事实错绑仍被记录，不能称事实提取已经无错。Qwen较早充分推理控制43/79与程序44/79、Llama35/79与34/79属于旧facts版本；`r2_r3_paper_audit/r2_cached_controls.json`只能在完整payload相同的26/29条子集复用，不能作为最终55题全匹配对照。

R3实际入口`r3_calibrated_all_methods/candidate/r3_optimization_head.py`按answer_format=diagnosis进入目录，否则eligible规则，否则原答案。`r3_catalog_distribution_head.py`固定seed20260916生成原序+5排列，log prior按order扣除后做疾病对齐多数票，平票用平均概率；失败回退原答。目录49名称，评分器46归一键不是同一资源。`raw_calls`1-token length停止是此打分接口本身，不等于普通生成被截断的失败。

R3历史记忆/相似病例答案路线与最终公共目录路线分别保存，不能改名成同一A3方法。历史候选（患者背景对比、pairwise、pointwise、关系/NLI、知识分配等）有实际分数和原输出，并非仅计划；没有全部纳入论文主表。为何未采用仅在对应主记录已有原因时引用，否则保留未找到采用依据。尤其单目录收益远大于额外校正的共同增益，避免将格式/名称落地全写成新临床推理。

R1后续`r1_head_refinement`的事实/组合/单诊断控制是在ASCENT47与33端验证结果已见后开展，属于重新开发；其输出已保存，冻结主表未换。不能因目录含validation/frozen就将后续选择称独立测试。

R4原临床HIV13、关系绑定、形式/生物执行、临床先验/绑定等早期尝试的scored/raw已存在；原clinical失败应保留，不能仅交付288/288成功表。最终A4的给定模型范围来自`physiology_head`实现，要求公开模型、参数、完整初态与factual动作表；typed patch仅修改指令规定部分，数值工具计算后果。24 profile×4情景×3时间点=288题，源自同一模拟机制，不是288患者或新临床参考。

R5首轮boundary双骨干方向不同、文档范围修订、consensus/F、目标支持/原句、线性训练与实体视图等目录均真实存在。现有交付F是有限原生分类组件，后续研究并未自动替换它。`mechanism_research/entity_view_pilot/final_status.json`明确880新前向、0新生成、complete_not_adopted；对应feature runtime/输出存在，理由为M4 R5伤害及M5强控制伤害。`premise_supervision_pilot`实际只含plan.json；结合主记录明确尚无trainer/特征/成绩，可标最后五头方案未执行（检查范围限定该目录）。不把它与此前真实训练试验混淆。

## 冻结检查真正执行到哪里

A4 v2 heldout的288题真实执行已核实；`preparation.json.status=prepared_not_run`只是准备时记录，随后matched_runtime complete/raw/scored齐全，不能单读旧准备状态判未执行。ASCENT47、CUPCase4+8+6、R1规则33端也有真实响应与评分；但分别受目录资格、来源train/test与同规则机制约束，后来有开发暴露。R5早期组合F的冻结后小范围检查与后期预备128母题+8强控是不同阶段；`mechanism_research/data/context_summary.json.confirmation_requests_created=0`及相关计划/主记录支持后者未进入确认推理，不应抹去前者已执行检查。

这些冻结检查都不能替代最终CF-MoA B/C3选定后的独立临床或家族隔离确认。最终系统的确认、独立候选池F复本状态由CF-MoA审计单独裁定；本报告不从“某个旧head做过holdout”推导整篇论文已具有最终独立泛化证据。

## 仍需保留的缺口

1. 早期各逻辑系列运行时源码/依赖/评分器SHA大多没有充分绑定。需取得当时已保存快照清单、原commit或完整launcher记录才可提升状态；当前最新源码不是替代品。
2. 恒None独立逐项控制记录在上述定向范围未找到，现有摘要保留；不能为补证新评分。若历史已有逐项制品，补入即可。
3. 历史大请求/输出、训练特征及部分来源数据只索引未交付，具体逐件列出，影响这些未采用方案的完整逐调用重建，不影响本次已经重汇总的核心表数值。
4. 主体原始raw与actual prompt已推荐交付，但未逐一语义核查全部历史响应；score存在不保证所有回答内容或参考答案正确。
5. 研究选择理由无法由成绩反推；未逐系列找到决策依据的登记仍是未核实采用身份。论文要写特定失败动机时须沿登记的summary/log和主记录找到明确原文，不能补造。

## 追加：历史版本哈希收据的直接核对

进一步对本扫描范围名称含hash/freeze的JSON提取实际文件SHA声明，共284项：234项原记录路径当前字节一致，50项由保留的冻结/历史源码副本匹配，全部找到原SHA字节；结果`recorded_hash_checks.json`。没有仅凭当前文件时间判断版本。按basename未匹配的历史Python声明还对全扫描Python源码逐SHA查找，确认旧`analyze_development.py`修订以不同文件名保留，不能误报丢失。R5有关逻辑行已注明收据范围，但完整依赖和每条模型调用的版本绑定仍不可仅由这些分析快照推出。

具体例：`entity_view_pilot/execution_source_hashes.json`声明的`learned_features.py` SHA `1595147dfd92998fde9387e1f7d1e20e262430488b6bddc2432633e5d1b0c539`在`entity_view_pilot/source/learned_features.py`等冻结副本匹配；应交付该副本，不用后续共享worker替换。当时的final_status还明确shared worker在pilot结束后另行修复。版本沿革是方法证据的一部分，并非所有同名文件均可互换。

## 2026-10-23 data4重建验收

重新盘点8,669文件、199历史逻辑目录，加29论文入口，共228条运行登记与136映射；7104候选文件集合与旧记录的数量和字节数一致。284个旧SHA声明再次全部匹配（234原路径、50冻结副本），A4六个冻结比较保持一致。仅使用已复制包内评分的`HANDOFF_ONLY=1`复核122格通过，14格恒None摘要保持未重评分；主稿14表依赖均在包内找到。A4语义导出1,127行的全部保留JSON值及省略数组规范SHA也逐行与原件核对一致。新收据：`packaged_reaggregate_receipt.json`、`active_table_review.json`、`a4_semantic_export_validation.json`。本次0模型调用、0新预测、0新评分。
