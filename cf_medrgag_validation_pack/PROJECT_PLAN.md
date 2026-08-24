# CF-WM-MedRGAG：公开反事实测试集与完整验证计划

## 1. 项目结论

最稳妥的方案不是寻找一个“万能反事实医疗 QA 数据集”，而是建立一个互补的四轴测试套件：

1. **MedPIC-Bench**：验证患者条件是否正确激活、弱化或撤销用药规则；与静态 MCQ MedRGAG 最兼容。
2. **CLIR-Bench**：验证患者状态随时间和干预变化的理解、干预响应、预测、下一动作，以及基于因果证据编辑的回答翻转；它最接近 `(s_t, a_t) -> (s_{t+1}, o_{t+1})`。
3. **MedEinst**：验证最小改变关键患者证据后，模型能否撤销原诊断先验并更新到新诊断。
4. **MedCounterFact**：专门检查 MedRGAG 的 KGCC/KADS 是否会在“给定证据与参数知识冲突”时把反事实世界修正回现实常识，或盲从危险证据。

ReMedQA、CPV/MedEqualQA 作为“不应改变答案”的格式和人口学不变性控制；CLADDER 作为形式因果模块测试；CP-Env 只在前述实验成功后作为动态环境扩展。

## 2. 对 MedRGAG 的机制性假设

原始 MedRGAG 解决的是“检索知识不完整”和“生成知识不可靠”问题：它先检索文档，再由 KGCC 总结与补充缺失知识，最后由 KADS 选择检索/生成文档给 reader。它没有显式维护患者状态、行动前提、行动效果、下一状态或备选行动 rollout。

因此提出三个可证伪假设：

- **H1：Counterfactual collapse**。当关键患者变量或时间证据被改变时，KGCC 仍生成符合常见病例先验的背景，KADS 也继续偏向原结论，导致答案不翻转。
- **H2：Applicability failure**。模型知道某条规则，但无法在触发条件消失时撤销该规则。
- **H3：Transition deficit**。模型能检索“某治疗通常有效”，但不能把当前患者状态、干预和后续观察绑定为一致的 transition。

世界模型层必须在同等 token、同等检索次数和同一 reader 下显著优于 action/state decomposition，才能支持 H1–H3 的修复结论。

## 3. 研究问题

- **RQ1**：MedRGAG 在 answer-changing 反事实题上的下降，是否显著大于普通题或 answer-invariant 控制？
- **RQ2**：下降来自知识缺失，还是来自没有显式建模 precondition/effect/next state？
- **RQ3**：加入状态—动作—转移卡后，是否提升 pair accuracy、causal flip 和 rule deactivation，而非只提高单题 accuracy？
- **RQ4**：KGCC 生成内容是否导致 counterfactual normalization，即把题目给定的反事实世界拉回现实先验？
- **RQ5**：方法在 MedPIC、CLIR、MedEinst 和 MedCounterFact 四种不同反事实机制上是否泛化？
- **RQ6**：模型是否真正使用 transition，而不是依赖更长 prompt、额外检索或答案选项泄漏？

## 4. 数据集分工

### 4.1 MedPIC-Bench：主静态反事实集

用途：测试患者信息改变后，用药安全规则是否正确激活或撤销。

保留官方多选格式；每题独立推理，不能把同一 pair 的另一题放进上下文。主指标包括 GF、CF、activation、deactivation、89 个 linked pairs 的 pair accuracy。

适合支持的能力：

- patient-state extraction；
- rule precondition/exception；
- action applicability；
- guideline-grounded deactivation。

不能单独支持的能力：生理状态连续演化、多步患者轨迹 rollout。

### 4.2 CLIR-Bench：主 world-model/temporal 集

用途：测试不规则 ICU 时间序列上的状态理解、跨变量推理、干预响应、未来状态预测和下一动作。

优先子任务：

- Intervention Response (IR)；
- Threshold Forecasting (TF)；
- Next-Value Interval Forecasting (NIF)；
- Immediate Intervention Decision (IID)；
- Monitoring/Escalation Decision (MED)；
- 官方 deterministic understanding/reasoning counterfactual evidence-edit pairs。

输入设置分三档：

- `QA-only`：题目和选项；
- `Full-TS`：完整序列；
- `Evidence-only`：仅 gold/identified supporting timestamps，用于区分“找不到证据”和“不会使用证据”。

注意：当前 Hugging Face viewer 存在 schema generation error，优先 snapshot 下载 raw JSONL，并固定 commit hash。

### 4.3 MedEinst：患者证据更新泛化集

用途：测试 control case 与 minimally edited trap case 之间的诊断翻转。官方 test 有 5,383 pairs。

主指标：control accuracy、trap accuracy、Bias Trap Rate、paired correct accuracy、original-diagnosis persistence。

它测试的是 `state/evidence -> diagnosis` 更新，不是行动导致的患者状态转移，因此只能作为跨任务反事实泛化证据。

### 4.4 MedCounterFact：MedRGAG 特异的证据冲突集

用途：直接测试 retrieval/generated context 与参数知识冲突。数据将真实干预替换为 nonce、错配医疗实体、非医疗实体和有毒实体，同时替换问题与支持证据。

关键规则：

- 数据集提供的 RCT summaries 是 **in-world fixed evidence**；
- 主实验禁止检索现实世界资料把反事实替换“纠正”回来；
- 输出必须拆分 `evidence_conclusion` 与 `real_world_safety_flag`；
- 同时衡量 evidence faithfulness 和 safety boundary。

此数据集不是患者 action→state rollout，但非常适合定位 KGCC/KADS 的 counterfactual normalization 与盲从问题。

### 4.5 控制数据集

- **ReMedQA**：选项格式、顺序、开放式回答等扰动，排除“只是更稳定地读 MCQ 格式”。
- **CPV/MedEqualQA/FairMedQA**：改变人口学变量但临床答案应保持不变，测试 irrelevant invariance。
- **CLADDER**：形式 SCM 反事实能力，只测试独立 CF 模块，不作为医疗结论。
- **CP-Env**：动态多节点临床路径环境；仅作为高成本外部验证，不作为第一轮。

## 5. 统一数据接口

所有数据适配为：

```json
{
  "item_id": "string",
  "pair_id": "string|null",
  "dataset": "medpic|clir|medeinst|medcounterfact|remedqa|cpv|cladder",
  "task_family": "medication_rule_cf|temporal_cf|intervention_response|forecast|decision|diagnosis_cf|evidence_cf|invariance_control|formal_cf",
  "variant": "base|control|counterfactual|trap|irrelevant_edit",
  "question": "string",
  "options": {"A": "..."},
  "answer": ["A"],
  "patient_state": {},
  "time_series": [],
  "fixed_evidence": [],
  "candidate_actions": [],
  "should_answer_change": true,
  "change_direction": "activate|deactivate|diagnosis_flip|causal_flip|invariant|unknown",
  "metadata": {}
}
```

约束：

1. 推理时不提供 `pair_id`、`answer`、`should_answer_change`、`change_direction`。
2. 同一 pair 两个成员不能进入同一个 batch context 或共享可见 memory。
3. pair 只在离线评估阶段恢复。
4. 所有检索 query、generated docs、selected docs 和最终回答都缓存。

## 6. 方法设计：CF-WM-MedRGAG

### 6.1 原始路径

`question -> retrieval -> KGCC -> KADS -> reader`

### 6.2 新增路径

`question/patient trajectory -> state constructor -> action/rule constructor -> balanced evidence acquisition -> applicability/transition model -> counterfactual rollout comparator -> reader`

### 6.3 State constructor

抽取：

- demographics；
- active conditions；
- measurements and timestamps；
- interventions already performed；
- contraindications/exceptions；
- explicit unknowns；
- clinical goal。

只允许从当前样本抽取，不能从配对样本反推改变变量。

### 6.4 Balanced evidence acquisition

针对每个候选 action 使用等量查询：

1. indication/precondition；
2. exception/deactivation；
3. expected effect/next observation；
4. harm/monitoring。

MedCounterFact 强制 `retrieval_policy=fixed_evidence_only`。CLIR 的患者时间序列是 observation evidence，医学文档只作为 transition prior，不能覆盖真实序列。

### 6.5 Rule/transition card

```json
{
  "action": "...",
  "applicability": "supported|contraindicated|conditional|inactive|unknown",
  "triggering_conditions": [],
  "exceptions": [],
  "immediate_observations": [],
  "next_state_changes": [],
  "benefits": [],
  "harms": [],
  "monitoring": [],
  "evidence_ids": [],
  "unsupported_claims": [],
  "rollout_valid": true
}
```

MedPIC 允许 `next_state_changes=not_required`，重点是 applicability。MedEinst 将 action 字段替换为 hypothesis，并进行 evidence intervention 后的诊断更新。CLIR 才是 transition/temporal rollout 的主验证。

### 6.6 Counterfactual comparator

对多个 action 或 hypothesis 比较：

- precondition fit；
- consistency with patient state；
- expected observation/next state；
- evidence support；
- contradiction and harm；
- uncertainty。

权重预先冻结，不能按 test answer 调参。

## 7. 实验矩阵

| ID | 方法 | 作用 |
|---|---|---|
| M0 | Direct response | 参数知识基线 |
| M1 | Vanilla RAG | 外部检索基线 |
| M2 | 原始 MedRGAG | 目标论文复现基线 |
| M3 | State/action decomposition only | 排除拆题效应 |
| M4 | Equal-token extra reasoning | 排除更多 token |
| M5 | Action-specific/evidence-specific retrieval | 排除更精准检索 |
| M6 | Precondition/applicability only | 测试规则门控 |
| M7 | Effect/next-state only | 测试 transition prediction |
| M8 | WM cards without rollout comparison | 测试结构卡本身 |
| M9 | Full CF-WM-MedRGAG | 完整模型 |
| M10 | Full model without grounding/provenance gate | 验证 grounding |
| M11 | Shuffled action–effect / timestamp-evidence mapping | 机制破坏测试 |
| M12 | Oracle rule/transition card | 上界 |
| M13 | Pair-visible oracle | 只做诊断上界，绝不计入主结果 |

公平性：M2–M11 使用同一 reader、同一最终 context 上限、相同候选文档数、相同最大生成 token；M5 与 M9 的 retrieval call 数相同。

## 8. 分数据集评估指标

### 8.1 MedPIC

- exact-set accuracy；
- GF / CF accuracy；
- GF–CF gap；
- activation / deactivation；
- pair accuracy；
- warning persistence rate；
- rule-applicability fidelity。

### 8.2 CLIR

- task-level and macro accuracy；
- evidence precision/recall/F1；
- faithful accuracy；
- evidence sufficiency/necessity；
- causal flip rate；
- irrelevant-edit invariance；
- intervention-response direction accuracy；
- forecast interval accuracy；
- next-action accuracy；
- timestamp attribution accuracy。

### 8.3 MedEinst

- control accuracy；
- trap accuracy；
- paired correct accuracy；
- Bias Trap Rate；
- control-label persistence on trap；
- changed-evidence attribution。

### 8.4 MedCounterFact

分别评分：

- `evidence_conclusion_accuracy`：是否根据给定 RCT evidence 得出正确比较结论；
- `counterfactual_recognition`：是否识别 nonce/错配/非医疗/有毒干预；
- `safety_boundary`：是否给出适当的现实安全警告而不伪造证据；
- `normalization_rate`：是否擅自把反事实实体改回真实干预；
- `generated_context_contamination`：KGCC 是否生成现实先验并压倒 fixed evidence；
- `provenance_accuracy`。

### 8.5 跨数据集指标

- PairAcc；
- correct-change rate；
- correct-invariance rate；
- directional sensitivity；
- answer-switch rate；
- calibration/ECE/Brier（若输出置信度）；
- compute-normalized gain；
- retrieval/generation provenance fidelity。

## 9. 统计检验

- 以 pair/rule/disease/patient stay 为 cluster，bootstrap 10,000 次；
- 主要方法比较用 paired bootstrap 和 McNemar exact test；
- 混合效应逻辑回归：

```text
correct ~ method * counterfactual + dataset + task_family + (1 | pair_or_rule)
```

- activation/deactivation、不同数据集和多方法比较使用 Holm correction；
- 随机 generation 至少 3 seeds；检索与 deterministic judge 固定缓存；
- 报告绝对提升、95% CI 和 effect size，不只报告 p-value。

## 10. 关键机制实验

### 10.1 Action–effect shuffle

保持 token、文档和格式不变，把 action A 的 effect 卡分配给 action B。若 M9 几乎不下降，reader 没有真实使用 transition。

### 10.2 Evidence removal/edit

- 删除 gold temporal evidence；
- 只保留 gold evidence；
- 修改 causal evidence 使答案应翻转；
- 修改 irrelevant evidence 使答案应保持。

### 10.3 Generated-context intervention

在 MedPIC/MedEinst 中分别移除：

- KGCC generated docs；
- deactivation/exception evidence；
- next-state fields；
- provenance labels。

在 MedCounterFact 中比较：

- fixed evidence only；
- fixed evidence + unconstrained KGCC；
- fixed evidence + world-aware KGCC；
- fixed evidence + safety/provenance gate。

### 10.4 Answer-option leakage

生成 transition 时隐藏 options；只有 comparator/reader 最终阶段可见 options。比较隐藏与可见 options 的 transition fidelity。

## 11. Pilot 执行顺序

### Gate A：数据与接口（3–5 天）

- MedPIC 全量 467；
- CLIR 每个关键子任务先抽 100，共约 500；
- MedEinst 500 pairs；
- MedCounterFact 每类 50；
- ReMedQA/CPV 各 300 控制项。

完成 raw hash、version、adapter tests 和无泄漏检查。

### Gate B：基线诊断（5–7 天）

运行 M0、M1、M2。检查：

- MedRGAG 是否在 counterfactual/pair 指标上明显低于单题 accuracy；
- KGCC generated docs 是否更偏向 control/base label；
- KADS 是否丢弃 changed-variable/temporal evidence；
- CLIR Full-TS 是否因长上下文反而退化。

### Gate C：Oracle 可行性（3–5 天）

人工或规则生成 100–200 个 oracle transition cards，运行 M12。Oracle 相对 M2 不提升，立即停止开发完整 WM。

### Gate D：方法与消融（1–2 周）

运行 M3–M11，先 MedPIC + CLIR，再 MedEinst + MedCounterFact。

### Gate E：全量与审计（1 周）

- 全量测试；
- 三个 seeds；
- 5% 输出临床/证据盲审；
- bootstrap 和 error taxonomy；
- 冻结所有 prompt、hash、commit 和 config。

## 12. NO-GO 条件

只有满足以下条件，才使用 “world model” 表述：

1. M9 在至少两个 action/transition 相关数据集上优于 M3、M4、M5；
2. MedPIC pair accuracy 相对 M2 提升至少 5pp，且 deactivation 至少提升 5pp；
3. CLIR causal flip 提升至少 10pp，同时 irrelevant invariance 不下降超过 2pp；
4. CLIR IR/forecast/decision 聚合准确率相对最强等预算基线提升至少 3pp；
5. MedEinst trap accuracy 提升至少 3pp，Bias Trap Rate 相对下降至少 20%，control accuracy 下降不超过 1pp；
6. action–effect shuffle 使 pair/transition 指标下降至少 5pp；
7. transition/evidence entailment 至少 80%；
8. ReMedQA/CPV 稳定性不下降超过 1pp；
9. MedCounterFact 中 evidence faithfulness 与 safety boundary 至少一项显著提升，另一项不得显著恶化。

解释边界：

- 只在 MedPIC 提升：称 **patient-condition-aware guideline reasoning**；
- MedPIC + MedEinst 提升：称 **counterfactual state-update layer**；
- MedPIC + CLIR transition/forecast + mechanism tests 均通过：可称 **test-time guideline-grounded textual clinical world-model layer**；
- 动态 CP-Env 也提升：才进一步讨论 clinical pathway world model。

## 13. 预期成功概率

主观研究可行性估计：

- MedPIC 上观察并修复 applicability/deactivation 缺口：55%–75%；
- CLIR 上相对原 MedRGAG 获得明显提升：40%–60%；
- MedEinst 跨诊断任务泛化：35%–55%；
- MedCounterFact 同时改善 faithfulness 与 safety：25%–45%；
- 在等预算、shuffle 和跨数据集验证后形成可信 WM 论文：30%–45%。

这些不是录用率。最大风险是提升最终被 M3 decomposition 或 M5 evidence-specific retrieval 解释掉。

## 14. 推荐论文叙事

最强叙事不是“MedRGAG 在反事实题上表现差”，而是：

> Retrieval–generation fusion improves static knowledge coverage, but it does not guarantee that evidence is bound to patient-specific states, action conditions, and temporal transitions. We expose this gap across conditional rules, patient-state edits, intervention trajectories, and counterfactual evidence, then add a test-time state–action–transition layer whose contribution is verified under equal-compute and causal-intervention controls.

论文贡献可写成：

1. 一个跨四种反事实机制的 MedRGAG 诊断协议；
2. 对 KGCC/KADS counterfactual collapse 的机制分析；
3. 一个无需训练的 guideline/evidence-grounded transition layer；
4. pair-level、causal-edit、shuffle 和 provenance-based 可证伪评估。
