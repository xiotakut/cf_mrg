# 可直接交给 Coding Agent：候选验证之后的 MoA 收口任务

## 目标与当前决定

不要开始第六套支持/反事实编辑/长裁决算法。以本轮真实运行的 `a5_candidate_with_rationales_v1` 为唯一主研究候选，将其接入已经采用的五操作系统。`candidate_only`是消融，原B是强基线。默认旧文件不覆盖，新研究入口显式选择。

最终要交付：可处理新输入的 Router + 五操作专家 + A5局部候选验证；完整原生结果；相对B的配对效应；必要对照与冻结后验证。不是再交一份“接口通过、效果待测”的报告。

## 当前已经完成，不要再重复

95组旧材料和285份旧重答的导出；31组旧错误审阅；88普通票池的195候选；两臂780真实取分；190输出；原生/辅助分数；追加一票/加三票缓存控制；恢复运行和服务器GPU占位交接。

新增统计直接读取本轮 `recovery_gpu23/analysis/complete_results` 等由实际交付索引确认的路径，不猜测私有文件位置。原生映射已评分，不重新跑grader产生相同分数，更不重新运行旧F。

## 任务1：固定方法身份与比较目标（无需GPU）

将随包 `03_Research_Method_Spec.json` 作为需要接线的规格，不直接当作当前loader已支持的运行配置。

主方法保留：全部不同合法F候选、每键最早完整响应、全当前上下文、全部旧理由标为不可信、每候选两编码分别归一后平均、精确平票保留F、返回选中整份响应。

不改变旧F内部候选生成、原R1路由顺序、规则、目录、A4求解器、原生评分。不根据source_id/家族/输入编号/已知gold选择arm。NLI仍按原F直接输出。

验收产物：`method_spec.resolved.json`，明确指向实际代码和运行参数；不要重新做整个项目哈希审计。

## 任务2：补本轮缺失的统计（无需GPU）

读取既有 `native_scored.jsonl` / `native_scoring_metadata.jsonl`、`quality_summary.json`、原 `evaluations.jsonl`、`pairs.jsonl`、`per_input_status` 的family映射。

输出 `paired_atoms.jsonl`：按完整原生ALL单元一行；保持/应变pair分别另一个metric。native reference不加入ALL，同一单元的R标签重复不重复计数。每行panel/model/metric/candidate/family_id/atom_id/baseline_score/candidate_score/weight。

用随包脚本生成相对B的paired family-cluster差值区间；复现四格原生点差，尤其自然M5 −1.111个百分点。缺失输出按原评分合同入分；禁止静默删行。报告开发选择偏差，不将区间解释为未见泛化。

同时用已有私有trace核对新主臂的全部17修复/9误伤，输出现象、对应原文位置与未知原因。不得把单token验证器选中的旧理由当成它自身的完整推理过程。不要为这项阅读新增模型批次。

验收产物：`paired_effects.json`、`new_changes_review.md`、全家族效应表。统计区间跨零不阻止后续集成与预定扩大评价。

## 任务3：新增薄在线入口（主要代码接线）

真实入口：
- `controller/strong_legacy.py::select(packet)`
- `controller/minimal_operations.py::run(...)`、`rule_operations(...)`
- `agents/a5_robust_readout.py::run_legacy(...)`
- `agents/a5_candidate_verify.py::run(packet, session, base_native_answer, saved_proposal, include_rationales=..., config=...)`
- `evaluation/candidate_verify_runner.py`当前只绑定保存样本；不能把它当成fresh全流程。

建议新建 `controller/moa_rcv.py`，复用minimal/old agent的调用，不复制一份规则或诊断算法。

每道输入按strong_legacy顺序：诊断→A3；规则eligible→共享A1/A2；完整模型→A4；F支持→A5；未覆盖→旧透传。

仅F分支在取得一个真实/合法复用的 `proposal` 后追加：

```python
verification = a5_candidate_verify.run(
    packet, session,
    base_native_answer=proposal.native_proposal,
    saved_proposal=proposal.to_dict(),
    include_rationales=(mode == "candidate_with_rationales"),
    config={"seed": 42},
)
```

该函数目前只允许config中的seed。不要把新controller mode、预算、其他规格字段整个传进去导致配置错误。NLI/K<2/不可用处理沿用函数本身。

保留F原trace，另存verification trace；native输出是返回的完整响应。`f_disagreement_reanswer`保持false，不能两条增量叠加。非F路径不调用该验证器。

真实F与验证器共享session时，全任务费用用一次最外层checkpoint差分，分项按阶段记录，不能把同一旧head成本加两次。

新入口支持cached和live：cached注入同输入的原F与score用于等价核对；live真实生成原F一次再即时验证，不从95组名单决定触发。原答案不能冒充F候选池，缺trace才补生成。

验收产物：薄控制器、配置、可复用CLI。要求agent提供的CLI接口（尚非现存命令）：

```text
python -m cf_moa.evaluation.run_moa_rcv --plan PLAN --method M4 --mode cached --output OUT
python -m cf_moa.evaluation.run_moa_rcv --plan PLAN --method M5 --mode live --gpu AUTHORIZED_GPU --output OUT
```

## 任务4：最低限度连通验收，然后进入效果评测

cached模式复用当前190结果核对完整返回；非F对照旧B。不是重新GPU抽样追求旧文字复现。

live只需小批覆盖：规则、诊断、完整模型R4、F-NLI、普通F K=1、普通F K>=2、旧透传。每项保留实际调用链与成本；R4测试用原合法模型数据，绝不填造普通病例的初始状态。

增加来源差分和原生返回检查即可，不新增“理由长度/引文数量合格才可继续”的门。单题错误照样评分并继续；共享engine初始化失败只停受影响作业，不重复32次启动，不自动跑未授权GPU。

## 任务5：五角色包装与机制消融

A1/A2是同一执行核的两个操作投影，明确在代码和图上标为shared engine；各自输出add/remove及依据。最终assemble仍来自旧核。

只在单独机制消融视图中禁用add或remove，不修改原规则记录；保持UNKNOWN/None语义。它证明两种更新操作的作用，不证明两个独立模型的协作。

A3目录与A4求解结果直接返回，不经过新的全局LLM。A4模型内实验与原v5临床任务分表。A5内部“多样本候选→验证选择”是实际的生成—聚合链，不重新包装成五位医生同时辩论。

产物：角色—代码—输入—输出对应表，覆盖/激活表，真实架构图；不要为了凑五个agent增加五次模型调用。

## 任务6：固定完整对照，而不是搜更多主方案

C0原方法；C1强B；C2候选验证无理由；C3带理由主方法；C4旧池+三份追加回答；C5同候选同理由的单次整体选择。

C1/C2/C3/C5共享同一F池。C5采用有限候选编码，返回选中的旧完整响应；两次映射取分可作为较低成本控制，不用重复相同temperature=0请求凑预算。

已有121/52结果直接复用，只补C5和确实缺失调用。C4属于采样扩池控制；已付三次生成不记成免费。

报告实际token与调用而不是声称各臂严格同费用。不要再构建一套超长提示的万能工具agent才允许主实验开始。

## 任务7：完整v5与冻结后新家族

从冻结v5 manifest获取全部合法输入，先写cache_coverage逐项标明：原B、完整F trace、评分、原上下文是否可复用。各骨干先M4/M5；全量范围不因R5多再删题，不按pool_has_gold过滤。

如果无原F池，生成一次并给各臂共享。非F/无分歧/NLI不额外验证。旧cache复用不算fresh端到端独立评测；所有未运行行保持partial身份。

完整回归后，方法和控制提示不再根据确认数据调整。新确认按真实暴露账本选母题/来源范围并预先冻结全清单，相关端点不跨分割。此前自然52不是盲测，旧R4 24 profile也不是新患者。

先固定池对照，冻结后至少增加一次独立F候选生成复本，B与RCV共享复本。改变F seed表的映射必须按现有实际接口实现并记录；不能只改temperature=0验证器的seed冒充新候选能力重复。

如果合法未见材料不足，不捏造独立结论；继续完成系统与公开开发结果，将独立证据缺口明确报告。

## 最终交付

1. 新主研究配置与可运行cached/live入口。
2. 相对B的家族配对效应与全变更样本诊断。
3. 完整v5和确认范围的分母、暴露、缓存与新增成本。
4. C0–C5实际对照和A1/A2机制消融、A4独立范围。
5. 五张论文主表、真实架构/算法、采用或未采用结论。

不要以零误伤或所有小分层不下降作为科研启动门槛；也不要用正确输入数上升掩盖原生主指标下降。保持完整分母和原生目标，让最终结果决定结论。若某个更简单控制更好，就采用它，不再为了MoA名称强行保留无效结构。
