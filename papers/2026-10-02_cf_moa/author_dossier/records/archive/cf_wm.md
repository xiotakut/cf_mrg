# 历史：CF-WM与修正版实验

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。该方向未建立独立world-model收益。保留Gate阶段、无效M12 label oracle、修正后的gold-free设置及303条分析。修正版完整报告从本地Git b714735找回；同路径当前文件属于DeltaRev。

## 修正版报告的版本来源

本地仓库`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg`提交`b714735`的`cf_medrgag_validation_pack/results/summary.md`已完整收入本文，并保存[恢复原文](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/cf_wm_results_b714735.md)。其中相对命令属于该提交及当时运行目录；当前同路径报告和部分制品已用于DeltaRev，不能拿当前文件替代历史证据。原Git对象保留，可用`git show b714735:路径`读取对应版本。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [GATE_A_RESULTS.md](#record-0266)
- [GATE_B_D_RESULTS.md](#record-0267)
- [PROJECT_PLAN.md](#record-0268)
- [ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md](#record-0269)
- [EXPERIMENT_CHRONOLOGY.md](#record-0270)
- [AGENT_HANDOFF.md](#record-0271)
- [UPLOAD_CONTENTS.md](#record-0272)
- [SOURCES.md](#record-0353)
- [Git b714735：修正版CF-WM完整报告](#record-0417)

<a id="record-0266"></a>

## GATE_A_RESULTS.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/GATE_A_RESULTS.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/GATE_A_RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack`。

### Gate A 公开数据执行结果

执行日期：2026-08-23
规范运行：`private_data/gate-a-public-20260823-seed13-v3`
机器可读报告：`results/gate_a_report.public-seed13.json`
最终决定：`stop_before_inference`

#### 结果

已用固定 revision 的真实公开源完成当前计划的 Gate A。最终冻结 6,577 条 inference 和 6,577 条 gold；数据适配、目标计数、哈希、pair/control 结构与固定证据策略通过，但公开材料不足以执行计划要求的正式推理实验。因此按 `PROJECT_PLAN.md` 的 Gate 顺序停止，没有运行 M0–M13，也没有调用模型、GPU 或推理 API。

| 数据集 | 固定 revision | 原始数据 | 最终 pilot |
|---|---|---:|---:|
| MedPIC | `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983` | 467 行 | 467 行 |
| CLIR | `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` | 3,000 行 | t6–t10 各 100，共 500 行 |
| MedEinst | `354f4b527e764a8f2bebea8f71be55e0a6966402` | 10,766 行 | 500 pairs / 1,000 行 |
| MedCounterFact | `f35b98063b51a63e677829b6d173029d98dd3b1e` | 1,012 行 | 200 pairs / 400 行；四类各 50 |
| ReMedQA | `3abb4b47a5859c7b46c0a1872a58c82e2e3029e3` | 5,036 行 | 300 IDs / 1,200 行 |
| CPV | `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5` | 12,310 行 | 300 case IDs / 3,010 行 |

CPV 的 300 个控制单元均使用实际 `case_text` 人口学变体，其中 298 组含 10 行、2 组含 15 行。CLIR 只有 t6/t8 共 200 行具备可安全使用的公开观测；t7/t9/t10 共 300 行没有可用的历史观测。

#### Gate 决定

20 项检查中 15 项通过，5 项阻断：

1. MedCounterFact 仓库和 ReMedQA dataset card 没有明确 license。
2. MedPIC 公开 467 行没有计划所需的官方 89 linked-pair map。
3. CLIR 有 300/500 行缺少可用的 repository observations。
4. CLIR 500/500 行都没有计划要求的 Full-TS。
5. CLIR 公开源没有官方 causal-edit pair map。

因此当前结果是数据/接口边界的 `stop_before_inference`，不是模型效果上的 NO-GO，也没有用此前的 Luna 代理实验替代本计划。

#### 冻结哈希

| 产物 | SHA-256 |
|---|---|
| `configs/gate_a_sources.json` | `1389258e6248a862d88e7f8894ba96e2bf80e72916425f5d9ca8d313e3740bc5` |
| `gate_a_manifest.json` | `a34ae77072a73f275d7ec28cfbccd1e5534142d2ab506ab84e0950c10fe7cf9c` |
| `pilot.inference.jsonl` | `307d7d88cdad367a7e4e5f2beb0741247c3fb68a7b359c252c1fd46777b32e96` |
| `pilot.gold.jsonl` | `c53231e2e12b169c6abc8295e50a0cff32719112c214a34b85e8828e9cfbf25e` |
| `gate_a_report.json` | `c4f2851a5d33c1882bc85d6054f1b7adf1c1d176e0eea41332bcfbc20a7733df` |

#### 执行与验收

- `result_audit`：数据源、revision、许可与真实结果数值检查。
- `code_test_audit`：数据准备、adapter、pilot 冻结与测试。
- `provenance_audit`：独立 Gate-A 审计器。
- 主 Agent：真实集成运行、结果复算与最终 Gate 决定。

最终测试：`python3 -m unittest discover -s tests -v`，4/4 通过；`py_compile` 通过。

<a id="record-0267"></a>

## GATE_B_D_RESULTS.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/GATE_B_D_RESULTS.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/GATE_B_D_RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack`。

### Gate B–D 实验结果

> **历史有效性说明：** 本文中的 M12 在构造 transition cards 时读取了 gold answer / correct candidate，因此是无效的 label oracle，而不是 transition oracle。其代码路径、数值和产物仅保留为 integration/parser 的历史记录，必须排除在 revised experiment 的主分析、上界比较和世界模型结论之外。本次替代条件是完全不读取 gold 的 `teacher_transition`。

#### 结论

balanced60、seed 13 的真实 pilot 已完成。Gate C 的 oracle 检查通过，但 Gate D 只满足 1/4 个冻结推进条件，因此 **NO-GO：停止在 Gate D，不进入 Gate E 的全量三种子实验，也不支持 textual clinical world model 表述**。

Gate C：M12 oracle 为 30/60（50.00%），M2 为 17/60（28.33%），提升 13 题、21.67 pp，超过 2 pp 门槛。

Gate D 的最佳非 oracle 方法是 M10，而不是完整方法 M9：M10 为 23/60（38.33%）、PairAcc 7/18（38.89%）；M9 为 21/60（35.00%）、PairAcc 5/18（27.78%）。

#### 主结果

所有方法使用同一组 60 个 item；PairAcc 只统计其中 18 个成员完整的 pair。

| 方法 | Accuracy | PairAcc |
|---|---:|---:|
| M0 | 21/60 (35.00%) | 6/18 (33.33%) |
| M1 | 21/60 (35.00%) | 6/18 (33.33%) |
| M2 | 17/60 (28.33%) | 4/18 (22.22%) |
| M3 | 17/60 (28.33%) | 3/18 (16.67%) |
| M4 | 15/60 (25.00%) | 4/18 (22.22%) |
| M5 | 20/60 (33.33%) | 6/18 (33.33%) |
| M6 | 21/60 (35.00%) | 6/18 (33.33%) |
| M7 | 22/60 (36.67%) | 6/18 (33.33%) |
| M8 | 22/60 (36.67%) | 6/18 (33.33%) |
| M9 | 21/60 (35.00%) | 5/18 (27.78%) |
| M10 | 23/60 (38.33%) | 7/18 (38.89%) |
| M11 | 22/60 (36.67%) | 6/18 (33.33%) |
| M12 | 30/60 (50.00%) | 5/18 (27.78%) |

M9 相对 M2 为 +4/60（+6.67 pp）和 +1/18 pair（+5.56 pp），但这不足以通过机制检验：

| 冻结条件 | 结果 | 判定 |
|---|---|---|
| M9 严格优于 M3 和 M5 | 21 > 17，21 > 20 | PASS |
| shuffle 使完整 PairAcc 至少下降 1/18 | M9 5/18，M11 6/18；反而上升 1 pair | FAIL |
| MedEinst trap 至少 +1/10，control 不下降 | M2 为 1/10、1/10；M9 为 1/10、0/10 | FAIL |
| CLIR t6+t7+t8+t10 比最佳等预算基线至少 +1/8 | M9 3/8，M8 3/8 | FAIL |

M9 还低于 M8 的整体 22/60、6/18；去掉 grounding/provenance gate 的 M10 又高于 M9。这组 pilot 没有显示完整 transition/comparator 机制带来稳定收益。

#### 运行与验收

- 样本：MedPIC 10、CLIR 10、MedEinst 20、MedCounterFact 16、ReMedQA 2、CPV 2。
- 模型：本地 Meta-Llama-3.1-8B-Instruct，32k context，reader temperature 0。
- M3–M11 各 60/60 unique；预测 null/empty 均为 0，reader 540/540 均 `finish=stop`。
- state/action 共 254 个候选；retrieval 1,016 条 query record；每题固定 5 个 context 槽位。
- grounded cards 254/254、parametric cards 254/254 均通过严格 schema；M11 的 254 个 action/effect bundle 全部实际错配且 action 本身保持不变。
- M4 的 60 题 auxiliary completion 与 M9 逐题等 token，总计 258,356 tokens，误差为 0。
- Gate D 总 LLM token：4,108,920。
- 单元测试 27/27 通过；`py_compile`、`git diff --check` 通过；GPU 0–2 已释放。

#### 产物与复现

- 汇总：`results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json`
- 原始预测、逐项评分、summary 和中间缓存：`results/gate-b-real-20260824-seed13-v4/`
- 固定样本：`configs/balanced60_seed13.json`，SHA-256 `c16f7828466ca5dc1165e255f2a9d42fc2b3b8cf211503595a35490bb7f0a0f9`
- Gate D runner SHA-256：`f49e91f22cbc67940912bc01dd3058495fd53df4e4af7db4e385f4efad9921d8`
- 汇总 SHA-256：`3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e`

重新聚合现有评分结果：

```bash
python3 scripts/summarize_gate_results.py \
  --inference results/balanced60-seed13/pilot.inference.jsonl \
  --gold results/balanced60-seed13/pilot.gold.jsonl \
  --run-dir results/gate-b-real-20260824-seed13-v4 \
  --methods M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 \
  --output results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json
```

#### 结果边界

这是单种子 60-item pilot，只能用于推进/停止决策。当前公开资产没有 MedPIC 官方 pair mapping，也没有 CLIR Full-TS 和官方 edit pairs；ReMedQA/CPV 在本样本中也没有完整 pair。因此不报告这些缺失单元对应的正式机制指标或显著性结论。

<a id="record-0268"></a>

## PROJECT_PLAN.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/PROJECT_PLAN.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/PROJECT_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack`。

### CF-WM-MedRGAG：公开反事实测试集与完整验证计划

#### 1. 项目结论

最稳妥的方案不是寻找一个“万能反事实医疗 QA 数据集”，而是建立一个互补的四轴测试套件：

1. **MedPIC-Bench**：验证患者条件是否正确激活、弱化或撤销用药规则；与静态 MCQ MedRGAG 最兼容。
2. **CLIR-Bench**：验证患者状态随时间和干预变化的理解、干预响应、预测、下一动作，以及基于因果证据编辑的回答翻转；它最接近 `(s_t, a_t) -> (s_{t+1}, o_{t+1})`。
3. **MedEinst**：验证最小改变关键患者证据后，模型能否撤销原诊断先验并更新到新诊断。
4. **MedCounterFact**：专门检查 MedRGAG 的 KGCC/KADS 是否会在“给定证据与参数知识冲突”时把反事实世界修正回现实常识，或盲从危险证据。

ReMedQA、CPV/MedEqualQA 作为“不应改变答案”的格式和人口学不变性控制；CLADDER 作为形式因果模块测试；CP-Env 只在前述实验成功后作为动态环境扩展。

#### 2. 对 MedRGAG 的机制性假设

原始 MedRGAG 解决的是“检索知识不完整”和“生成知识不可靠”问题：它先检索文档，再由 KGCC 总结与补充缺失知识，最后由 KADS 选择检索/生成文档给 reader。它没有显式维护患者状态、行动前提、行动效果、下一状态或备选行动 rollout。

因此提出三个可证伪假设：

- **H1：Counterfactual collapse**。当关键患者变量或时间证据被改变时，KGCC 仍生成符合常见病例先验的背景，KADS 也继续偏向原结论，导致答案不翻转。
- **H2：Applicability failure**。模型知道某条规则，但无法在触发条件消失时撤销该规则。
- **H3：Transition deficit**。模型能检索“某治疗通常有效”，但不能把当前患者状态、干预和后续观察绑定为一致的 transition。

世界模型层必须在同等 token、同等检索次数和同一 reader 下显著优于 action/state decomposition，才能支持 H1–H3 的修复结论。

#### 3. 研究问题

- **RQ1**：MedRGAG 在 answer-changing 反事实题上的下降，是否显著大于普通题或 answer-invariant 控制？
- **RQ2**：下降来自知识缺失，还是来自没有显式建模 precondition/effect/next state？
- **RQ3**：加入状态—动作—转移卡后，是否提升 pair accuracy、causal flip 和 rule deactivation，而非只提高单题 accuracy？
- **RQ4**：KGCC 生成内容是否导致 counterfactual normalization，即把题目给定的反事实世界拉回现实先验？
- **RQ5**：方法在 MedPIC、CLIR、MedEinst 和 MedCounterFact 四种不同反事实机制上是否泛化？
- **RQ6**：模型是否真正使用 transition，而不是依赖更长 prompt、额外检索或答案选项泄漏？

#### 4. 数据集分工

##### 4.1 MedPIC-Bench：主静态反事实集

用途：测试患者信息改变后，用药安全规则是否正确激活或撤销。

保留官方多选格式；每题独立推理，不能把同一 pair 的另一题放进上下文。主指标包括 GF、CF、activation、deactivation、89 个 linked pairs 的 pair accuracy。

适合支持的能力：

- patient-state extraction；
- rule precondition/exception；
- action applicability；
- guideline-grounded deactivation。

不能单独支持的能力：生理状态连续演化、多步患者轨迹 rollout。

##### 4.2 CLIR-Bench：主 world-model/temporal 集

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

##### 4.3 MedEinst：患者证据更新泛化集

用途：测试 control case 与 minimally edited trap case 之间的诊断翻转。官方 test 有 5,383 pairs。

主指标：control accuracy、trap accuracy、Bias Trap Rate、paired correct accuracy、original-diagnosis persistence。

它测试的是 `state/evidence -> diagnosis` 更新，不是行动导致的患者状态转移，因此只能作为跨任务反事实泛化证据。

##### 4.4 MedCounterFact：MedRGAG 特异的证据冲突集

用途：直接测试 retrieval/generated context 与参数知识冲突。数据将真实干预替换为 nonce、错配医疗实体、非医疗实体和有毒实体，同时替换问题与支持证据。

关键规则：

- 数据集提供的 RCT summaries 是 **in-world fixed evidence**；
- 主实验禁止检索现实世界资料把反事实替换“纠正”回来；
- 输出必须拆分 `evidence_conclusion` 与 `real_world_safety_flag`；
- 同时衡量 evidence faithfulness 和 safety boundary。

此数据集不是患者 action→state rollout，但非常适合定位 KGCC/KADS 的 counterfactual normalization 与盲从问题。

##### 4.5 控制数据集

- **ReMedQA**：选项格式、顺序、开放式回答等扰动，排除“只是更稳定地读 MCQ 格式”。
- **CPV/MedEqualQA/FairMedQA**：改变人口学变量但临床答案应保持不变，测试 irrelevant invariance。
- **CLADDER**：形式 SCM 反事实能力，只测试独立 CF 模块，不作为医疗结论。
- **CP-Env**：动态多节点临床路径环境；仅作为高成本外部验证，不作为第一轮。

#### 5. 统一数据接口

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

#### 6. 方法设计：CF-WM-MedRGAG

##### 6.1 原始路径

`question -> retrieval -> KGCC -> KADS -> reader`

##### 6.2 新增路径

`question/patient trajectory -> state constructor -> action/rule constructor -> balanced evidence acquisition -> applicability/transition model -> counterfactual rollout comparator -> reader`

##### 6.3 State constructor

抽取：

- demographics；
- active conditions；
- measurements and timestamps；
- interventions already performed；
- contraindications/exceptions；
- explicit unknowns；
- clinical goal。

只允许从当前样本抽取，不能从配对样本反推改变变量。

##### 6.4 Balanced evidence acquisition

针对每个候选 action 使用等量查询：

1. indication/precondition；
2. exception/deactivation；
3. expected effect/next observation；
4. harm/monitoring。

MedCounterFact 强制 `retrieval_policy=fixed_evidence_only`。CLIR 的患者时间序列是 observation evidence，医学文档只作为 transition prior，不能覆盖真实序列。

##### 6.5 Rule/transition card

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

##### 6.6 Counterfactual comparator

对多个 action 或 hypothesis 比较：

- precondition fit；
- consistency with patient state；
- expected observation/next state；
- evidence support；
- contradiction and harm；
- uncertainty。

权重预先冻结，不能按 test answer 调参。

#### 7. 实验矩阵

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

#### 8. 分数据集评估指标

##### 8.1 MedPIC

- exact-set accuracy；
- GF / CF accuracy；
- GF–CF gap；
- activation / deactivation；
- pair accuracy；
- warning persistence rate；
- rule-applicability fidelity。

##### 8.2 CLIR

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

##### 8.3 MedEinst

- control accuracy；
- trap accuracy；
- paired correct accuracy；
- Bias Trap Rate；
- control-label persistence on trap；
- changed-evidence attribution。

##### 8.4 MedCounterFact

分别评分：

- `evidence_conclusion_accuracy`：是否根据给定 RCT evidence 得出正确比较结论；
- `counterfactual_recognition`：是否识别 nonce/错配/非医疗/有毒干预；
- `safety_boundary`：是否给出适当的现实安全警告而不伪造证据；
- `normalization_rate`：是否擅自把反事实实体改回真实干预；
- `generated_context_contamination`：KGCC 是否生成现实先验并压倒 fixed evidence；
- `provenance_accuracy`。

##### 8.5 跨数据集指标

- PairAcc；
- correct-change rate；
- correct-invariance rate；
- directional sensitivity；
- answer-switch rate；
- calibration/ECE/Brier（若输出置信度）；
- compute-normalized gain；
- retrieval/generation provenance fidelity。

#### 9. 统计检验

- 以 pair/rule/disease/patient stay 为 cluster，bootstrap 10,000 次；
- 主要方法比较用 paired bootstrap 和 McNemar exact test；
- 混合效应逻辑回归：

```text
correct ~ method * counterfactual + dataset + task_family + (1 | pair_or_rule)
```

- activation/deactivation、不同数据集和多方法比较使用 Holm correction；
- 随机 generation 至少 3 seeds；检索与 deterministic judge 固定缓存；
- 报告绝对提升、95% CI 和 effect size，不只报告 p-value。

#### 10. 关键机制实验

##### 10.1 Action–effect shuffle

保持 token、文档和格式不变，把 action A 的 effect 卡分配给 action B。若 M9 几乎不下降，reader 没有真实使用 transition。

##### 10.2 Evidence removal/edit

- 删除 gold temporal evidence；
- 只保留 gold evidence；
- 修改 causal evidence 使答案应翻转；
- 修改 irrelevant evidence 使答案应保持。

##### 10.3 Generated-context intervention

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

##### 10.4 Answer-option leakage

生成 transition 时隐藏 options；只有 comparator/reader 最终阶段可见 options。比较隐藏与可见 options 的 transition fidelity。

#### 11. Pilot 执行顺序

##### Gate A：数据与接口（3–5 天）

- MedPIC 全量 467；
- CLIR 每个关键子任务先抽 100，共约 500；
- MedEinst 500 pairs；
- MedCounterFact 每类 50；
- ReMedQA/CPV 各 300 控制项。

完成 raw hash、version、adapter tests 和无泄漏检查。

##### Gate B：基线诊断（5–7 天）

运行 M0、M1、M2。检查：

- MedRGAG 是否在 counterfactual/pair 指标上明显低于单题 accuracy；
- KGCC generated docs 是否更偏向 control/base label；
- KADS 是否丢弃 changed-variable/temporal evidence；
- CLIR Full-TS 是否因长上下文反而退化。

##### Gate C：Oracle 可行性（3–5 天）

人工或规则生成 100–200 个 oracle transition cards，运行 M12。Oracle 相对 M2 不提升，立即停止开发完整 WM。

##### Gate D：方法与消融（1–2 周）

运行 M3–M11，先 MedPIC + CLIR，再 MedEinst + MedCounterFact。

##### Gate E：全量与审计（1 周）

- 全量测试；
- 三个 seeds；
- 5% 输出临床/证据盲审；
- bootstrap 和 error taxonomy；
- 冻结所有 prompt、hash、commit 和 config。

#### 12. NO-GO 条件

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

#### 13. 预期成功概率

主观研究可行性估计：

- MedPIC 上观察并修复 applicability/deactivation 缺口：55%–75%；
- CLIR 上相对原 MedRGAG 获得明显提升：40%–60%；
- MedEinst 跨诊断任务泛化：35%–55%；
- MedCounterFact 同时改善 faithfulness 与 safety：25%–45%；
- 在等预算、shuffle 和跨数据集验证后形成可信 WM 论文：30%–45%。

这些不是录用率。最大风险是提升最终被 M3 decomposition 或 M5 evidence-specific retrieval 解释掉。

#### 14. 推荐论文叙事

最强叙事不是“MedRGAG 在反事实题上表现差”，而是：

> Retrieval–generation fusion improves static knowledge coverage, but it does not guarantee that evidence is bound to patient-specific states, action conditions, and temporal transitions. We expose this gap across conditional rules, patient-state edits, intervention trajectories, and counterfactual evidence, then add a test-time state–action–transition layer whose contribution is verified under equal-compute and causal-intervention controls.

论文贡献可写成：

1. 一个跨四种反事实机制的 MedRGAG 诊断协议；
2. 对 KGCC/KADS counterfactual collapse 的机制分析；
3. 一个无需训练的 guideline/evidence-grounded transition layer；
4. pair-level、causal-edit、shuffle 和 provenance-based 可证伪评估。

<a id="record-0269"></a>

## ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack`。

### Archived CF-WM-MedRGAG Implementation Contract

> Archived on 2026-09-06. This document preserves an earlier WM-oriented
> experiment contract. It is not active coding-agent instruction, and current
> work does not pursue the WM direction.

#### Objective

Implement a reproducible evaluation of whether an explicit state–action–transition layer improves counterfactual medical reasoning beyond MedRGAG's retrieval, context generation, and document selection.

#### Non-negotiable invariants

1. **No pair leakage.** Never expose the paired item, `pair_id`, counterpart label, change direction, or gold answer at inference time.
2. **No outcome-based selection.** Never select items because MedRGAG answered them incorrectly.
3. **Preserve official tasks.** MedPIC remains exact-set multi-select; MedEinst remains open diagnosis; CLIR remains its official MCQ/time-series format; MedCounterFact uses its supplied evidence.
4. **Fixed evidence for MedCounterFact.** External retrieval is disabled in the primary setting. The supplied RCT summaries define the in-world evidence. Real-world plausibility is scored separately.
5. **Patient data outranks priors.** In CLIR, observed timestamps and interventions are authoritative for the specific trajectory; medical documents provide priors but cannot overwrite observations.
6. **Equal-compute comparisons.** Hold reader, context limit, retrieval calls, document count, and output-token budget constant across M2–M11 whenever the comparison claims mechanism-level improvement.
7. **No option leakage into transition generation.** Default transition cards are generated without answer options. Options are visible only to the comparator/reader.
8. **No test prompt tuning.** Tune only on declared development samples. Freeze prompts and hashes before running official test sets.
9. **Version pinning.** Record dataset commit/hash, code commit, model revision, tokenizer revision, prompts, environment, and random seeds.
10. **Cache every stage.** Store retrieval results, summaries, missing-knowledge items, generated documents, selected documents, state cards, transition cards, and final predictions.
11. **Structured outputs only.** Validate every LLM output against JSON Schema; retry at most twice; then mark invalid rather than silently repairing semantics.
12. **Claim discipline.** Do not call the method a world model unless `configs/no_go.yaml` passes.

#### Dataset routing

- `medpic`: conditional medication rule and action applicability.
- `clir`: temporal state, intervention response, forecasting, decision, and evidence-edit counterfactuals.
- `medeinst`: diagnosis revision under minimally changed discriminative evidence.
- `medcounterfact`: evidence–parametric conflict and safety boundary.
- `remedqa/cpv/medequalqa`: answer-invariant controls.
- `cladder`: formal causal sanity test only.

#### Required experiment order

1. Validate adapters and leakage checks.
2. Run M0/M1/M2.
3. Run oracle M12 on a preregistered pilot.
4. If oracle passes, run M3/M4/M5 controls.
5. Only then run M6–M11.
6. Freeze results before any qualitative error selection.

#### Logging fields

Every prediction must log:

- run ID, item ID, dataset and task family;
- method ID and seed;
- input hash and visible fields;
- retrieval queries and document IDs;
- generated and selected contexts with provenance;
- state/action/transition JSON;
- model revisions and generation parameters;
- raw response, parsed response, parse status;
- latency, prompt tokens, completion tokens, and call count.

#### Evaluation safety

- Never present benchmark outputs as clinical advice.
- Do not infer real patient treatment from de-identified or synthetic benchmark cases.
- For toxic/non-medical MedCounterFact items, report both evidence-conditioned conclusion and real-world safety warning as separate fields.

<a id="record-0270"></a>

## EXPERIMENT_CHRONOLOGY.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/EXPERIMENT_CHRONOLOGY.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/EXPERIMENT_CHRONOLOGY.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff`。

### Experiment chronology

This is the operational history of the run, including attempts that were superseded. Exact visible agent messages are retained in `handoff/transcripts/`.

#### 1. Repository and plan setup

- Cloned `https://github.com/xiotakut/cf_mrg` into the current workspace.
- The repository initially contained only `cf_medrgag_validation_pack.zip`.
- Inspected and extracted the archive into `cf_medrgag_validation_pack/`.
- The requested `/home/data3/txy/agent.md` did not exist. The applicable files found and read were `/home/data3/txy/AGENTS.md` and this pack's `AGENTS.md`.
- Used Ponytail Full: reused the existing MedRGAG checkout, environment, retrievers, prompt builders, and vLLM model rather than creating a parallel framework.

#### 2. Initial SubAgent split

The work was split among result/source auditing, provenance/Gate-A audit, implementation/tests, runner mapping, and compute probing. Six completed SubAgent transcripts are stored under `handoff/transcripts/`:

- `result_audit`: initial plan/result audit;
- `code_test_audit`: Gate-A preparation implementation and tests;
- `provenance_audit`: Gate-A fail-closed audit implementation and tests;
- `source_hunt`: public source verification, scorer, balanced60 reference, independent result recomputation;
- `runner_map`: MedRGAG reuse map, Gate-D design, semantic audits, final artifact audit;
- `compute_probe`: GPU/model smoke tests, Gate-B/Gate-C/Gate-D implementation and real runs.

After the user explicitly said to focus on experimental results, further defensive-gap investigation stopped.

#### 3. Public source findings and Gate A

- MedPIC-Bench: 467 public questions. The public files do not contain the paper's official 89-pair mapping, so official MedPIC PairAcc cannot be reconstructed.
- CLIR-Bench: 11 tasks × 600 rows. The public repository supplies QA/evidence records but not Full-TS trajectories or official counterfactual edit pairs.
- MedEinst: 5,383 valid test control/trap pairs. The raw train files contain 10,609 pairs, differing from the README count.
- MedCounterFact: 203 originals plus 809 replacements. The valid repository path is `KaijieMo-kj/Counterfactual-Medical-Evidence`.
- ReMedQA and CPV were usable. MEDEQUALQA's repository contained no dataset. FairMedQA was available from Zenodo rather than the assumed Hugging Face location.
- Missing official MedPIC/CLIR units were not fabricated. The pilot uses only materializable public tasks.

Gate-A v3 contains 6,577 rows:

| Dataset | Rows |
|---|---:|
| MedPIC | 467 |
| CLIR | 500 |
| MedEinst | 1,000 |
| MedCounterFact | 400 |
| ReMedQA | 1,200 |
| CPV | 3,010 |

The preparation/audit tests cover source revisions, artifact hashes, row counts, identity, pair blindness, gold separation, evidence availability, and control construction. Gate-A tests passed.

#### 4. balanced60 and compute probe

The frozen seed-13 sample contains:

- MedPIC 10;
- CLIR 10: two each from t6–t10;
- MedEinst 20: ten complete two-member pairs;
- MedCounterFact 16: eight complete pairs, two per counterfactual category;
- ReMedQA 2 and CPV 2: row-level controls, not complete pairs.

The exact item list is `configs/balanced60_seed13.json`.

GPU/model probing established:

- GPUs 0–2 were free H20 devices; GPU 3 was occupied by another process and never used;
- local Llama-3.1-8B-Instruct loaded successfully through vLLM 0.8.5;
- 32k context worked at `gpu_memory_utilization=0.5` with eager execution;
- the final policy used 32,768 model length, 32,256 reader input tokens, and 512 reader output tokens;
- overlength MedCounterFact input used deterministic head/tail evidence truncation.

#### 5. Gate B: M0, M1, M2

- Implemented a single batched vLLM runner with resume-safe JSONL stages.
- M0 is direct response.
- M1 uses external retrieval; CLIR keeps patient observations visible and MedCounterFact is fixed-evidence-only.
- M2 uses the released-code-intent all-Llama chain: five summaries, exploration, five generations, selection, MedCPT rerank, shared reader.
- Reader answers are parsed with dataset-specific output contracts. MedPIC uses exact sets; CLIR uses one A–D key even when options are embedded in the question; MedCounterFact uses the fixed three-value enum.

Important superseded attempt:

- The first M2 selector parser recognized mostly bracketed selections and treated many valid `Final Selection:` lines as empty. The pre-fix artifacts are retained with `pre-selector-fallback` in their names.
- A minimal final-line parser restored valid unbracketed selections. The corrected M2 accuracy changed from 21/60 to 17/60. PairAcc remained 4/18.

Final Gate-B results: M0 21/60 and 6/18; M1 21/60 and 6/18; M2 17/60 and 4/18.

#### 6. Gate C: M12 oracle

- M12 reads only the current item's gold answer/evidence to build rule-based oracle cards. It never receives pair ID, counterpart row, change direction, or counterpart label.
- It reuses M2 reranked documents and the shared reader; card construction and planning require no extra LLM calls.
- M12 produced 60/60 predictions and scored 30/60, PairAcc 5/18.
- The +21.67 pp row gain over M2 passed the frozen 2 pp oracle gate, allowing Gate D.

#### 7. Gate-D implementation audits before the real run

The first Gate-D implementation passed fake tests but a semantic audit found four substantive mismatches:

1. M10 merely removed `evidence_ids` from already grounded cards;
2. M11 moved action and effect together instead of breaking the mapping;
3. M4 inserted filler text rather than matching actual auxiliary generation tokens;
4. a combined `all` phase could keep vLLM alive while loading MedCPT.

The fixes were:

- regenerate M10 parametric cards independently with evidence omitted;
- keep each target action fixed and derange only effect/timestamp/evidence bundles;
- generate M4 auxiliary reasoning with the exact per-item M9 completion-token budget and `ignore_eos`;
- keep `state`, `retrieval`, and `run` as three separate process phases.

Additional corrections made before the real run:

- use candidate-specific evidence for transition cards;
- include the complete state/goal/target/candidate document in applicable methods;
- remove `rollout_valid` from the M6 projection;
- enforce auxiliary prompt + output length within 32k;
- preserve extractor candidate types and use dataset-aware fallbacks.

#### 8. Gate-D real state and retrieval stages

The first state run yielded only one MedEinst candidate per item, total C=174. This was rejected because the diagnosis ablation requires five distinct hypotheses.

- The old file is retained as `state_action.pre-medeinst-candidate-fix.jsonl`.
- A first strict rerun failed because one long response had no complete JSON.
- The state prompt was made concise and required complete JSON below 900 tokens.
- The fresh state run completed with C=254: every MedEinst item has H0–H4, five distinct diagnosis candidates.

Retrieval completed in about 11m38s:

- 60 items, 254 candidates, four query types per candidate, 1,016 query records;
- 824 external retrieval calls;
- MedCounterFact made zero external calls and used fixed evidence only;
- action context is five slots per item: 250 nonempty and 50 expected MedCounterFact padding slots.

#### 9. Gate-D run interruptions and repairs

##### Grounded cards

The first grounded-card pass produced 17 incomplete cards out of 254: 13 length-truncated and four non-JSON responses. The run was stopped before M9 comparator output existed.

- Original file retained as `grounded_cards.pre-schema-retry.jsonl`.
- Added strict required-field validation and one 2,048-token JSON repair.
- Rebuilt 60 unique rows; all 254 cards passed schema.

##### M9 comparator

The first M9 comparator batch was invalid at scale: 44 of the first 48 ended by length and 43 had empty candidate scores, silently selecting the first candidate. The run stopped at 48 rows.

- Original file retained as `M9.comparator.pre-schema-retry.jsonl`.
- Added complete candidate-score coverage, nonempty legal selection, and `comparison_valid=true` checks.
- Added a compact 2,048-token full-prompt retry. Final M9 comparator: 60/60 valid, 59 retries.

##### M4 equal compute

The initial exact-token implementation generated one item at a time and was too slow. vLLM was extended minimally to accept a per-prompt `max_tokens` list.

- M4 then ran in variable batches of 16.
- All 60 rows satisfy target tokens = actual tokens.
- Total completion tokens: 258,356; per-item range 2,513–7,186.

##### Parametric cards and M10

- Parametric cards completed 254/254; two cards required repair; every `evidence_ids` list is empty.
- M10 comparator completed 60/60; 52 rows required the compact retry.

##### M11

- All 254 shuffled cards retained the target action and took the effect/timestamp/evidence bundle from a different candidate.
- One early M11 comparator attempt still failed after the 2,048-token retry, so a final 3,072-token retry path was added with hard failure after that.
- The resumed canonical run needed 58 first retries and no second retry; all 60 rows were valid.

##### Readers and scoring

- M3–M11 each produced exactly 60 unique predictions.
- All 540 reader generations ended with `finish=stop`; null and empty answers were zero.
- Scoring was independently recomputed by the main agent and two SubAgents. Stored summaries and the canonical comparison matched exactly.

#### 10. Final decision

The full result table is in `GATE_B_D_RESULTS.md`. Gate E was rejected because only one of four frozen continuation checks passed. This is the completed experimental outcome, not an unfinished run.

#### 11. Revised gold-free experiment

The follow-up implementation replaced the invalid M12 concept and removed M12 from the active historical runner. M12 had marked the correct answer as supported/selected and was a label oracle, not a transition oracle. `teacher_transition` now receives no gold, pair member, correct candidate, or answer label and emits only neutral transition fields.

The revised runner added the requested task-specific routes and controls without creating a new gate framework:

- option-independent cards for action selection;
- option-hidden free transition followed by a matcher for CLIR outcome/forecast tasks;
- explicit diagnosis-state updating for MedEinst;
- fixed-evidence-world conclusion plus separate safety flag for MedCounterFact;
- direct rank, structured no-transition, candidate retrieval, equal-token reasoning, transition/no-comparator, grounded/parametric/teacher cards, and two shuffles;
- claim-level citations with empty unsupported IDs, a text-based automated evidence judge, and dataset-specific reader schemas.

##### Fresh sample and contract debugging

The deterministic initial draw contained 320 examples: 80 each from MedPIC, CLIR, MedEinst, and MedCounterFact. It had zero overlap with balanced60 or prior result artifacts. CLIR was restricted to t6 and t8 because t7/t10 expose no usable pre-anchor patient observations after targets are removed.

During a sharded dry start, model outputs exposed several parser/contract defects: teacher JSON shape, structured compact repair, transition-card truncation, evidence-world reader/matcher shape, MedEinst duplicate hypotheses, and direct-rank diagnosis mapping. Each change kept the first prompt or scientific semantics fixed where possible, used one repair, and stopped silently replacing invalid output. Triggering items and official-pair counterparts were removed without reading correctness. The final analysis contains 303 items; exact IDs/reasons are in `results/debug_exclusions.json`.

After the final freeze, any remaining one-repair failure was persisted as null/incorrect and execution continued. Shared state failures fan out to all state-dependent methods while direct/proxy still run. This eliminated sample deletion based on parse success.

##### Real run

Three GPU shards produced 3,939 predictions (13 × 303) and 1,818 card rows (6 × 303). Every method covers the same ID set. Both shuffles have 150 applicable MedPIC/MedEinst rows and 153 fixed-action not-applicable rows. Mechanical merge normalization only canonicalized exact option-text aliases, safety aliases, state logging, shuffle provenance, and applicability metadata; it did not change medical answers.

The online run had 35 explicit contract failures. Post-run inspection found 326 additional MedEinst method rows that copied the schema placeholder `concise diagnosis`; these were uniformly marked null/incorrect without gold. The code now rejects that placeholder, but the rows were not regenerated after inspecting the fresh outputs. Consequently MedEinst is treated as an invalid branch for mechanism interpretation, with non-MedEinst and common-clean sensitivities reported.

##### Mechanism inspection and evaluation

The fixed automated sample judged 100 full-transition cards and 1,567 claims. Valid citation rate was 38.2%; entailment among cited claims 66.9%; unsupported 60.8%; contradiction 9.6%. The prohibited-string scan was 0%; the model judge separately flagged 2.2% for possible option leakage.

Final accuracy was 20.8% for full transition, versus 31.7% proxy, 30.7% direct rank, 27.1% structured no-transition, and 26.7% equal-token reasoning. On applicable items, effect shuffle and full-card shuffle exceeded full transition by 2.7 and 4.0 percentage points. Excluding MedEinst or every item with any parse failure leaves the same negative ordering.

The canonical revised results and exact confidence intervals are in `results/summary.md` and `results/metrics.json`. This result is fresh and gold-unseen, but because contracts were debugged on the initial draw it must not be described as a pristine untouched held-out benchmark.

<a id="record-0271"></a>

## AGENT_HANDOFF.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/AGENT_HANDOFF.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/AGENT_HANDOFF.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff`。

### Agent handoff

#### Current classified benchmark entry (2026-09-09)

Use [v3 exclusive R1–R5](/home/data3/txy/docs/data/construction.md#record-0316)
for the current classified benchmark: 3,105 units, R1–R5 counts
1,601/77/324/13/1,090, complete M0/M1 results. Load the package's current
`labels`, input/evaluation JSONL, and `results/` using the read-only example in
`/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md`. The local v3 package has not been
published. The remaining sections preserve the older WM experiment; their
commands and "current revised" wording apply only to that historical run.

#### Historical WM state

The revised gold-free experiment requested after the historical Gate B–D pilot is complete. Its fresh, gold-unseen analysis contains 303 items and 13 methods. The result is negative: `full_transition` is below the local MedRGAG proxy, direct rank, structured no-transition, and equal-token reasoning; both shuffle controls are more accurate than the unshuffled method.

- Scientific conclusion: current implementation does not establish a distinct world-model effect
- Branch at handoff: `main`
- Repository: `xiotakut/cf_mrg`
- Revised analysis: 303 items, seed 13 runner/bootstrap
- Model: local Meta-Llama-3.1-8B-Instruct
- Final revised outputs: 3,939 predictions, 1,818 card rows, 100 judged cards / 1,567 judged claims
- Final implementation tests: 71/71 passed
- GPU state after the run: GPUs 0–2 released; GPU 3 belongs to an unrelated Qwen process

Read `results/summary.md` and `results/metrics.json` before changing prompts. The analysis is gold-unseen but not a pristine untouched held-out benchmark: parser contracts were repaired against outputs from an initial 320-item draw, and the 17 triggering/debug counterpart items were excluded before gold scoring. Do not reinterpret the MedEinst branch without addressing its documented open-answer placeholder failure on a genuinely new sample.

#### Read in this order

1. `ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md` for historical protocol only
2. `PROJECT_PLAN.md`
3. `results/summary.md` and `results/metrics.json`
4. `scripts/run_experiments.py`, `scripts/evaluate.py`, and `scripts/inspect_mechanism.py`
5. `GATE_A_RESULTS.md` and `GATE_B_D_RESULTS.md` for historical context
6. `handoff/EXPERIMENT_CHRONOLOGY.md`
7. `results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json` for the old pilot only

Visible main-agent and SubAgent transcripts are in `handoff/transcripts/`. They intentionally contain task/user messages and visible commentary/final messages only; hidden reasoning, system/developer instructions, tool-internal payloads, and credentials are not exported.

#### Implementation map

| File | Purpose |
|---|---|
| `scripts/prepare_gate_a.py` | Download pinned public sources and build the public Gate-A pack |
| `scripts/audit_gate_a.py` | Fail-closed manifest/count/pair/gold/evidence checks |
| `scripts/run_gate_b.py` | balanced60 selection and M0/M1/M2/M12 execution |
| `scripts/score_gate_b.py` | Dataset-aware row and complete-pair scoring |
| `scripts/run_gate_d.py` | Three-phase Gate-D runner for M3–M11 |
| `scripts/summarize_gate_results.py` | Canonical overall, dataset, pair, and slice aggregation |
| `scripts/run_experiments.py` | Revised 13-condition, gold-free, task-routed runner |
| `scripts/evaluate.py` | Offline gold join, dataset/pair metrics, paired bootstrap, and sensitivity analysis |
| `scripts/inspect_mechanism.py` | Automated claim/evidence grounding and leakage inspection |
| `tests/` | 71 passing unit/integration tests for historical and revised paths |

Gate-D execution is deliberately split into separate `state`, `retrieval`, and `run` processes. This avoids loading vLLM and MedCPT in the same GPU lifecycle.

#### Canonical artifacts

Current revised artifacts:

- `results/heldout.inference.jsonl` and `results/heldout.gold.jsonl`: fixed 303-item analysis split.
- `results/medrgag_documents.jsonl`: selected/reranked proxy evidence for all 303 items.
- `results/predictions.jsonl` and `results/cards.jsonl`: complete revised predictions/cards.
- `results/metrics.csv`, `results/metrics.json`, and `results/summary.md`: final evaluation.
- `results/mechanism_judgments.jsonl` and `results/mechanism_metrics.json`: fixed automated inspection.
- `results/debug_exclusions.json`: all 17 pre-score exclusions and reasons.

Historical pilot artifacts:

- `results/balanced60-seed13/`: the exact 60 inference/gold rows needed to inspect and rescore this pilot.
- `results/gate-a-public-20260823-seed13-v3/`: final Gate-A manifest and report. Raw downloaded datasets are rebuilt through `prepare_gate_a.py`.
- `results/gate-b-real-20260824-seed13-v4/`: all current predictions, scores, summaries, cards, retrieval caches, comparator caches, shuffle output, and pre-fix attempt backups.
- `handoff/LOCAL_PRIVATE_DATA.sha256`: hashes for every local-only file that existed under `private_data/` at handoff time.
- `handoff/UPLOAD_MANIFEST.sha256`: hashes for the committed validation-pack handoff files.
- `configs/balanced60_seed13.json`: frozen ordered item IDs.

Important hashes:

| Artifact | SHA-256 |
|---|---|
| balanced60 IDs | `c16f7828466ca5dc1165e255f2a9d42fc2b3b8cf211503595a35490bb7f0a0f9` |
| Gate-B runner at execution | `2c28d2715a2eb748148236a620dfd9a6da1c9aeb4f28002e4afcd2f17d7043d9` |
| Gate-B runner in this handoff | `dc0df989aae2537b0858f26d40a78f33e7d4e923d9b5b04ba239eeefb1284ab8` |
| Gate-D runner | `f49e91f22cbc67940912bc01dd3058495fd53df4e4af7db4e385f4efad9921d8` |
| canonical comparison | `3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e` |
| Gate-D state/action | `aa1a9653fb255944d7029e63c583a7e4f4dc31865eef45dc7d1bbfc3c832c378` |
| action retrieval | `9c25b973eb57e9b7584df0a0dff43bb338e547f14c792c8d38d883e8988fe5af` |
| action context | `0534d2237d96f77964054190bcff48a2528d2ec6f8af242b050b311b77f9f4ed` |

The only Gate-B runner change after execution was replacing its `/tmp` default balanced60 reference with the byte-identical repository file in `configs/`; method logic and the reference SHA are unchanged.

#### Final result

| Method | Accuracy | Complete PairAcc |
|---|---:|---:|
| M0 | 21/60 | 6/18 |
| M1 | 21/60 | 6/18 |
| M2 | 17/60 | 4/18 |
| M3 | 17/60 | 3/18 |
| M4 | 15/60 | 4/18 |
| M5 | 20/60 | 6/18 |
| M6 | 21/60 | 6/18 |
| M7 | 22/60 | 6/18 |
| M8 | 22/60 | 6/18 |
| M9 | 21/60 | 5/18 |
| M10 | 23/60 | 7/18 |
| M11 | 22/60 | 6/18 |
| M12 | 30/60 | 5/18 |

Gate C passed because M12 improved over M2 by 13/60 rows (+21.67 pp). Gate D passed only the condition that M9 strictly beat M3 and M5. It failed all three mechanism/continuation checks:

- shuffle did not hurt: M11 improved over M9 by 1 row and 1 complete pair;
- MedEinst trap stayed 1/10 while control fell from 1/10 to 0/10;
- CLIR t6+t7+t8+t10 was 3/8 for both M9 and the best equal-budget baseline M8.

M10, which removes the grounding/provenance gate, was the best non-oracle method. The pilot therefore does not support a textual clinical world-model claim.

#### Local dependencies not stored in Git

These paths existed on the execution host:

- MedRGAG checkout and Python environment: `/home/data3/txy/MedRGAG`, `/home/data3/txy/MedRGAG/.venv`
- Llama model: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`
- MedCPT cross encoder: `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder`
- Java used by Pyserini: `/home/data3/txy/.local/medrgag-jdk-21`
- BM25 indexes and local Wikipedia/textbook corpora: under the existing MedRGAG workspace
- Raw public downloads and full 6,577-row Gate-A v3 pack: local `private_data/`, reproducible from the pinned source manifest

#### Verification

From `cf_medrgag_validation_pack/`:

```bash
python3 -m unittest discover -v tests
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/summarize_gate_results.py \
  --inference results/balanced60-seed13/pilot.inference.jsonl \
  --gold results/balanced60-seed13/pilot.gold.jsonl \
  --run-dir results/gate-b-real-20260824-seed13-v4 \
  --methods M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 \
  --output /tmp/cf_mrg-comparison-check.json
sha256sum /tmp/cf_mrg-comparison-check.json
```

The last hash must be `3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e`.

<a id="record-0272"></a>

## UPLOAD_CONTENTS.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/UPLOAD_CONTENTS.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff/UPLOAD_CONTENTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/handoff`。

### GitHub upload contents

#### Included

- Entire validation-pack implementation, prompts, configs, schemas, tests, and reports.
- Exact balanced60 inference/gold rows and ordered ID list.
- Final Gate-A manifest/report.
- All 65 files from the canonical Gate-B/C/D run directory, including:
  - M0–M12 predictions, scored rows, and summaries;
  - retrieval, state, card, comparator, M4 reasoning, and shuffle caches;
  - canonical comparison;
  - superseded M2 selector, state, grounded-card, and M9 comparator attempts.
- Visible-message transcripts for the main Agent and six SubAgents.
- Detailed handoff and experiment chronology.
- SHA-256 inventory for all local `private_data/` files.
- SHA-256 inventory for the committed validation-pack files.

#### Not included

- Three duplicated copies of downloaded raw public datasets under `private_data/` (about 265 MB total). Their pinned sources and hashes are retained, and Gate A rebuilds them.
- Local model weights, BM25 indexes, Wikipedia/textbook corpora, Python environment, and Java runtime.
- Raw Codex session JSONL files. Those include hidden reasoning, system/developer instructions, and tool-internal payloads; the visible/task messages are exported instead.
- GitHub credentials or any local authentication files.

No Git LFS dependency is needed: the largest committed artifact is about 8.1 MB.

<a id="record-0353"></a>

## SOURCES.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/references/SOURCES.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/references/SOURCES.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/references`。

### Primary Sources and Public Resources

#### Target method

- Li et al. (2026), *From Retrieval to Generation: Unifying External and Parametric Knowledge for Medical Question Answering*.
- Code: `https://github.com/ll0ruc/MedRGAG`

#### Core public counterfactual/temporal benchmarks

- MedPIC-Bench paper: `https://arxiv.org/abs/2608.03028`
- MedPIC-Bench data: `https://huggingface.co/datasets/TIM0927/MedPIC-Bench`
- CLIR-Bench paper: `https://arxiv.org/abs/2607.09880`
- CLIR-Bench data: `https://huggingface.co/datasets/winall/CLIR-Bench`
- MedEinst paper: `https://aclanthology.org/2026.acl-long.1847/`
- MedEinst data: `https://huggingface.co/datasets/zhui711/MedEinst`
- MedEinst repository: `https://github.com/zhui711/MedEinst`
- MedCounterFact paper: `https://aclanthology.org/2026.findings-acl.1847/`
- MedCounterFact data: `https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence`

#### Controls and extensions

- ReMedQA data: `https://huggingface.co/datasets/disi-unibo-nlp/ReMedQA`
- ReMedQA repository: `https://github.com/disi-unibo-nlp/remedqa`
- CLADDER repository: `https://github.com/causalNLP/cladder`
- CP-Env repository: `https://github.com/SPIRAL-MED/CP_ENV`
- CP-Env paper: `https://arxiv.org/abs/2512.10206`
- MedEqualQA paper: `https://aclanthology.org/2025.sciprodllm-1.4/`
- FairMedQA paper: `https://arxiv.org/abs/2505.19562`

#### Access/licensing note

Record the exact dataset revision and inspect upstream terms before redistributing adapted copies. In particular, MedCounterFact's repository should be checked for an explicit license and upstream evidence terms before public release of derivatives.

<a id="record-0417"></a>

## Git b714735：修正版CF-WM完整报告

来源：[Documents/Codex/2026-09-14/documentation_migration/cf_wm_results_b714735.md](/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration/cf_wm_results_b714735.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-09-14/documentation_migration`。

### Revised counterfactual / transition experiment

#### Result

The result is **negative for the world-model hypothesis**. On the 303-item fresh, gold-unseen analysis, `full_transition` reached 63/303 (20.8%), below `medrgag_proxy` at 96/303 (31.7%), `direct_rank` at 93/303 (30.7%), and `structured_no_transition` at 82/303 (27.1%). Candidate-effect and full-card shuffling did not reduce accuracy: on the 150 items where within-item shuffling was defined, both shuffled conditions were more accurate than `full_transition`.

This is not an exact reproduction of the published MedRGAG system. `medrgag_proxy` is the repository's local all-Llama retrieval/generation/selection proxy. The result supports neither a distinct transition-model benefit nor a general clinical world-model claim.

#### Data and freeze policy

The initial fresh sample contained 320 items with zero overlap with `balanced60` or prior repository result artifacts. Seventeen items used while repairing parser contracts, plus complete-pair counterparts where applicable, were excluded before gold accuracy was inspected. The final fixed analysis contains 303 items:

| Dataset / task | Items | Official complete pairs |
|---|---:|---:|
| MedPIC action selection | 78 | unavailable |
| CLIR prospective intervention response | 40 | unavailable |
| CLIR next-value interval forecasting | 39 | unavailable |
| MedEinst diagnosis state update | 72 | 36 |
| MedCounterFact evidence-world reasoning | 74 | 37 |
| **Total** | **303** | **73** |

Because parser/prompt contracts were repaired after inspecting outputs from the initial 320, this is a fresh gold-unseen analysis after pre-accuracy contract debugging, not a pristine untouched held-out benchmark. Triggering items were excluded without consulting correctness, and no item was removed after the final freeze.

CLIR t7 and t10 were not used because the available public inference records contain no pre-anchor patient observations after target fields are removed. No pair mapping, temporal evidence, activation label, or safety label was guessed.

#### Implementation note

- The historical M12 path read the answer/correct candidate and was a label oracle. Its active functions and CLI method were removed from `scripts/run_gate_b.py`; historical artifacts remain explicitly labeled invalid for revised analysis.
- `teacher_transition` is gold-free and emits only nine neutral transition fields. It is a same-Llama prompt upper bound, not a gold oracle and not a stronger external-model upper bound.
- A task router separates action selection, option-hidden outcome prediction, prospective temporal forecasting, diagnosis state update, and fixed-evidence-world reasoning.
- Action cards are generated independently without labels or competing option text. Fixed-action outcome options are hidden until a separate matcher runs. MedCounterFact keeps the local evidence conclusion separate from the real-world safety flag.
- Missing or invalid evidence citations remain empty and unsupported. Claim/evidence entailment is judged from the cited text rather than from ID presence.
- Final readers use dataset-specific provenance-aware schemas. Reader citations are filtered to actual input evidence IDs.
- The controls are direct, local MedRGAG proxy, decomposition only, candidate retrieval, direct rank, structured no-transition, and approximately equal-token reasoning. The transition variants include no-comparator, full, parametric, effect shuffle, full-card shuffle, and gold-free teacher.
- The runner permits one JSON repair. A second contract failure is persisted as `prediction=null` and counted wrong; it is never silently replaced.

#### Main results

Token totals are observed per-condition attribution from runner records; shared state/card calls can be attributed to more than one condition and therefore must not be summed as a wall-clock execution total.

| Method | Correct / 303 | Accuracy | Parse failures | Attributed tokens |
|---|---:|---:|---:|---:|
| `direct` | 94 | 31.0% | 1 | 1.09M |
| `medrgag_proxy` | 96 | 31.7% | 10 | 1.23M |
| `decomposition_only` | 98 | **32.3%** | 6 | 1.47M |
| `candidate_retrieval` | 89 | 29.4% | 32 | 1.46M |
| `direct_rank` | 93 | 30.7% | 2 | 1.49M |
| `structured_no_transition` | 82 | 27.1% | 25 | 2.57M |
| `equal_token_reasoning` | 81 | 26.7% | 12 | 3.75M |
| `transition_no_comparator` | 70 | 23.1% | 49 | 2.84M |
| `full_transition` | 63 | 20.8% | 64 | 3.83M |
| `parametric_transition` | 55 | 18.2% | 23 | 3.18M |
| `effect_shuffle` | 67 | 22.1% | 43 | 3.85M |
| `full_card_shuffle` | 69 | 22.8% | 22 | 3.86M |
| `teacher_transition` | 59 | 19.5% | 72 | 2.32M |

The approximately token-matched non-transition control averaged 12,373 attributed tokens/item, versus 12,650 for `full_transition`, and was 5.9 percentage points more accurate.

#### Paired comparisons

Confidence intervals use 1,000 paired bootstrap resamples. Shuffle comparisons include only the 150 MedPIC/MedEinst items where within-item shuffling is meaningful; fixed-action CLIR/MedCounterFact rows are marked not applicable.

| Difference | n | Delta | 95% CI |
|---|---:|---:|---:|
| full − `medrgag_proxy` | 303 | −10.9 pp | [−15.5, −5.9] |
| full − `direct_rank` | 303 | −9.9 pp | [−15.8, −4.0] |
| full − `structured_no_transition` | 303 | −6.3 pp | [−11.6, −1.3] |
| full − `equal_token_reasoning` | 303 | −5.9 pp | [−10.9, −1.3] |
| full − `transition_no_comparator` | 303 | −2.3 pp | [−4.6, −0.3] |
| full − `effect_shuffle` | 150 | −2.7 pp | [−6.0, 0.0] |
| full − `full_card_shuffle` | 150 | −4.0 pp | [−8.0, −0.7] |
| full − `parametric_transition` | 303 | +2.6 pp | [−2.0, +7.3] |

#### Dataset results

| Method | MedPIC (78) | CLIR (79) | MedEinst (72) | MedCounterFact (74) |
|---|---:|---:|---:|---:|
| `medrgag_proxy` | 21.8% | 27.8% | 8.3% | 68.9% |
| `direct_rank` | 29.5% | 27.8% | 4.2% | 60.8% |
| `structured_no_transition` | 17.9% | 21.5% | 1.4% | 67.6% |
| `equal_token_reasoning` | 16.7% | 25.3% | 1.4% | 63.5% |
| `transition_no_comparator` | 24.4% | 16.5% | 1.4% | 50.0% |
| `full_transition` | 14.1% | 17.7% | 1.4% | 50.0% |
| `parametric_transition` | 24.4% | 22.8% | 1.4% | 23.0% |
| `effect_shuffle` | 19.2% | 17.7% | 1.4% | 50.0% |
| `full_card_shuffle` | 20.5% | 17.7% | 2.8% | 50.0% |

`full_transition` did not beat both ranking and structured controls on either MedPIC or CLIR. Its CLIR intervention-response / interval-forecast accuracies were 15.0% / 20.5%, versus 22.5% / 33.3% for the proxy and 32.5% / 23.1% for direct rank. Grounded cards only clearly exceeded parametric cards on MedCounterFact; they were worse on MedPIC and CLIR.

For the 37 official MedCounterFact pairs, both-correct accuracy was 16/37 (43.2%) for full transition, 22/37 (59.5%) for the proxy, 18/37 (48.6%) for direct rank, and 20/37 (54.1%) for structured no-transition. MedCounterFact safety labels are null in the available gold, so safety-flag accuracy is unavailable.

#### Mechanism inspection

A fixed seed-13 sample of 100 `full_transition` cards (39 MedPIC, 36 MedEinst, 16 MedCounterFact, 9 CLIR) produced 1,567 claims for the automated evidence judge.

| Metric | Result |
|---|---:|
| Claims with a valid citation | 598/1,567 (38.2%) |
| Entailed among cited claims | 400/598 (66.9%) |
| Unsupported claims | 953/1,567 (60.8%) |
| Contradicted claims | 150/1,567 (9.6%) |
| Hard prohibited-string matches | 0/1,567 (0.0%) |
| Judge-flagged option leakage | 34/1,567 (2.2%) |

The hard scan found no `correct answer`, `gold answer`, or equivalent prohibited strings. The 2.2% judge flag is reported separately because automated comments indicate some flags may reflect incorrect/unsupported claims rather than confirmed answer leakage.

#### Failure accounting and sensitivity

The online run recorded 35 one-repair contract failures. Post-run schema inspection found another 326 MedEinst method-rows whose reader copied the literal schema example `concise diagnosis`; these were uniformly changed to explicit parse failures and counted wrong, without consulting gold or changing the sample. The future runner now rejects that placeholder. Because this affects methods unevenly, MedEinst is not used as evidence for or against the transition mechanism in the scientific interpretation.

The negative result is not caused by this correction:

| Sensitivity analysis | full | proxy | direct rank | structured | effect shuffle | full-card shuffle |
|---|---:|---:|---:|---:|---:|---:|
| Exclude MedEinst (n=231) | 26.8% | 39.0% | 39.0% | 35.1% | 28.6% | 29.0% |
| Exclude every item with any parse failure (n=226) | 27.0% | 39.4% | 39.8% | 35.0% | 28.3% | 28.8% |

On pairwise complete cases, full remained below proxy by 11.7 pp, direct rank by 11.7 pp, and structured scoring by 7.6 pp. These are diagnostic sensitivities; the primary table conservatively counts every failure as wrong.

#### Answers to the research questions

1. **Versus MedRGAG proxy:** no; −10.9 pp.
2. **Versus direct ranking:** no; −9.9 pp.
3. **Versus structured scoring:** no; −6.3 pp.
4. **Effect shuffle:** no degradation; the shuffle was +2.7 pp relative to full.
5. **Full-card shuffle:** no degradation; the shuffle was +4.0 pp relative to full.
6. **Grounding versus parametric cards:** mixed by dataset and only +2.6 pp overall with a CI crossing zero; grounding quality was weak.
7. **Benefiting datasets/tasks:** none established against both required controls; MedCounterFact was the only clear grounded-over-parametric slice.
8. **Claim support:** insufficient—only 38.2% cited and 60.8% unsupported.
9. **Scientific conclusion:** negative. This implementation does not establish a distinct world-model effect.

#### Metric availability and limitations

- MedPIC activation/deactivation and guideline labels were unavailable, so only exact-set accuracy is reported.
- CLIR t7/t10, official pairs, and supporting-timestamp labels were unavailable; only prospective t6 and t8 metrics are reported.
- MedCounterFact safety labels and generated-context contamination labels were unavailable; those metrics are omitted.
- MedEinst's open-diagnosis reader contract failed systematically. Its primary rows remain for transparency, but conclusions rely on the non-MedEinst sensitivity.
- The teacher uses the same local Llama model, not a stronger external teacher. It is gold-free but not a true capability upper bound.
- This is one model and one fresh gold-unseen sample after contract debugging. Bootstrap intervals quantify item sampling uncertainty, not model/seed variation.
- The proxy's precomputed KGCC/KADS token cost is outside runner token logs. Batched transition failures can also omit discarded sibling-generation tokens.

Detailed overall, dataset, task, pair, token, sensitivity, and bootstrap results are in `metrics.json`; per-item outputs are in `predictions.jsonl`, transition cards in `cards.jsonl`, and automated judgments in `mechanism_judgments.jsonl`.

#### Commands used

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/run_experiments.py \
  --inference results/heldout.inference.jsonl \
  --medrgag-documents results/medrgag_documents.jsonl \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --output-dir results

CUDA_VISIBLE_DEVICES=0 python3 scripts/inspect_mechanism.py \
  --cards results/cards.jsonl --sample-size 100 --seed 13 \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct

python3 scripts/evaluate.py \
  --predictions results/predictions.jsonl \
  --gold results/heldout.gold.jsonl \
  --mechanism-metrics results/mechanism_metrics.json \
  --metrics-csv results/metrics.csv \
  --metrics-json results/metrics.json \
  --summary results/summary.md \
  --seed 13 --bootstrap-samples 1000
```
