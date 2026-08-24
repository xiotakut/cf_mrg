# Visible transcript: /root/result_audit

- Session: `01a02f2f-3bf4-79e2-82f8-826d18660dcc`
- Timestamps: UTC
- Scope: user/task messages and visible agent commentary/final messages only.

## 2026-08-23T15:13:44.223Z — Agent commentary

I’ll apply Ponytail Full to keep this audit strictly minimal and evidence-driven, then inspect the repository instructions and independently recompute the acceptance metrics without modifying files.

## 2026-08-23T15:13:52.173Z — Agent commentary

Ponytail’s effect here is to reuse the repository’s own statistics implementation and write only a temporary, read-only audit script outside the artifacts if needed. The workspace guide also points to a nested experiment contract, so I’m checking that before touching the evidence.

## 2026-08-23T15:14:45.796Z — Agent commentary

The artifact schemas are cleanly separated: predictions contain model outputs and provenance; results add gold and correctness afterward. I’m now joining them by `(dataset, item_id, condition)`, recomputing correctness and paired statistics from the rows, and separately reconstructing all 170 prompts on CPU to test byte/token identity.

## 2026-08-23T15:16:04.261Z — Agent final_answer

PASS — independent read-only numerical acceptance audit found no discrepancies.

Evidence recomputed from 170 prediction and 170 result rows:

- 170 unique `(dataset, item_id, condition)` keys; 85 unique items; exactly one MD and one MW row per item.
- Result identities exactly match the 85 input identities and are a subset of the 1,000-row P2 gold source.
- Results are an exact projection of predictions plus post-hoc fields; all gold values match P2.
- Recomputed correctness:
  - MD: strict 64/85, author 65/85.
  - MW: strict 64/85, author 65/85.
- Per dataset:
  - MedQA 25: MD 23 strict/23 author; MW 24/24.
  - MedMCQA 18: MD 12/12; MW 11/11.
  - MMLU-Med 17: MD 14 strict/15 author; MW 14/15.
  - PubMedQA* 25: both 15/15.
- Strict and author pairs both give 1 improvement, 1 regression, 83 unchanged.
- Using `src/evaluation/paired_stats.py`, `samples=10000`, `seed=13`, direction MW−MD:
  - difference 0.0;
  - CI `[-0.03529411764705882, +0.03529411764705882]`, or `[-3.5294, +3.5294]` pp;
  - exact McNemar discordants 1/1, two-sided `p=1.0`.
- Reconstructed all prompts on CPU using the recorded tokenizer and runner helpers:
  - all 85 MD/MW input-token pairs equal;
  - 160,457 total input tokens per condition;
  - 42 equal rankings, exactly 42 byte-identical user/chat prompt pairs;
  - 128 unique chat prompts: 42 paired groups and 86 singletons;
  - prompt equality iff ranking equality;
  - reconstructed token counts and source metadata exactly match prediction rows.
- Equal-ranking pairs have 42/42 identical raw responses, strict predictions, and author predictions.
- Reader predictions differ on exactly three items: one MW improvement, one regression, and one both-wrong change, matching section 18.
- Raw preferred rankings recompute to MD 74/85 and MW 69/85.
- Prediction rows contain no recursive key names indicating gold, correctness, reference, or V15 predictions.
- Every prediction/result row has `exploratory=true`, `provisional=true`, `human_validated=false`, and `grounding=parametric_no_nice`.
- All audited summary fields match recomputation; section 18’s numerical and integrity claims match.

Commands/checks used:

- Standard-library JSON joins and invariant assertions over predictions, results, input, and P2.
- Repository `paired_bootstrap` and `exact_mcnemar`.
- CPU-only prompt reconstruction with local `AutoTokenizer`; no model generation or GPU use.
- No files modified.

Artifact SHA-256:

- predictions: `84370e51340514d32cd9f2dbb80ac742c02e44f33c9668e392ac36295b8dabcb`
- results: `c13c904c26400d398448c5583bb36c86df2a4dde18401d0c3552baea2d4fb80f`
- summary: `8723e3f27831524012e239fc493584344839bab22bf2398db85753e67c78517e`

## 2026-08-23T15:18:35.097Z — Agent commentary

I’m reusing Ponytail Full and the workspace guide already read. I’ll audit the current plan’s named sources against local caches first, then verify only unresolved or mutable upstream metadata—no downloads or edits.

## 2026-08-23T15:18:43.454Z — Agent commentary

The current plan preserves four distinct official task types, so “one generic QA adapter” would be wrong. I’m checking each source’s actual local footprint, pair/gold representation, and immutable revision metadata before proposing the smallest real pilot.

## 2026-08-23T15:27:04.030Z — Agent commentary

I’ll add only the pinned source registry, explicitly encoding unavailable pair/time-series capabilities as false and keeping the JSON deterministically sorted for hashing.

## 2026-08-23T15:28:26.008Z — Agent final_answer

Implemented [gate_a_sources.json](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/configs/gate_a_sources.json).

- Contains six pinned source registries, pilot selectors/counts, licenses, files/splits, pair keys, and evidence-backed capability flags.
- Valid canonical JSON: sorted keys, two-space indentation, trailing newline.
- `git diff --check` passes.
- SHA-256: `9714e575ad628bc448c67fd34c50c8141c9ab2247d8c6a77b2c790c77d0dba7b`
- No project files other than the requested registry were changed.

## 2026-08-23T15:42:17.571Z — Agent commentary

我会只读重算 v2 的所有计数、配对/控制单元、身份与哈希，并递归扫描推理视图中的答案、配对和变化方向泄漏；不会信任现有报告汇总，也不会修改文件。

## 2026-08-23T15:42:44.018Z — Agent commentary

初步结构与报告一致：推理/金标各 6,642 行，报告声明 4 个 blocker、`stop_before_inference`。我正在进一步核对配对成员结构、控制 unit 的实际成员数分布、金标不变性，以及逐行 canonical `input_hash`，以发现汇总可能掩盖的异常。

## 2026-08-23T15:45:34.956Z — Agent final_answer

验收结论：**FAIL**。现有汇总计数正确，`stop_before_inference` 决策也正确；但发现报告未捕获的真实推理泄漏/适配异常。

精确重算：

- inference：6,642 行；gold：6,642 行；均为 6,642 个唯一身份。
- 两文件 `(dataset,item_id)` 集合及顺序完全一致，无重复。
- dataset 行数：
  - CLIR 500
  - CPV 3,075
  - MedCounterFact 400
  - MedEinst 1,000
  - MedPIC 467
  - ReMedQA 1,200
- 6,642/6,642 个 canonical `input_hash` 正确。
- 递归禁用键名扫描 `answer|gold|pair|counterpart|change`：0 次。
- 报告文件哈希绑定全部正确。

配对与控制：

- MedEinst：500 pairs；每对恰好 `control + trap`；500/500 金标诊断翻转；变化标记全部正确。
- MedCounterFact：
  - 200 counterfactual + 200 original companions；
  - 200 pairs，每对恰好一原始、一反事实；
  - 四类各 50：`ID`、`Nonsense tokens`、`OOD`、`Poison`；
  - 200/200 pair 金标相同；
  - 400/400 行 fixed evidence 非空。
- ReMedQA：300 units，每 unit 恰好四种格式；300/300 的正确答案文本跨格式保持一致。
- CPV：300 units；285 个含 10 行，15 个含 15 行，总计 3,075；金标及 invariance 标记全部一致。

报告状态：

- `decision = stop_before_inference`
- 4 个 blocker、4 个失败检查、13 个通过检查。
- blocker：
  1. `source_licenses`
  2. `medpic_official_89_linked_pairs`
  3. `clir_full_ts`
  4. `clir_official_causal_edit_pairs`

未被报告捕获的异常：

1. **CPV 适配退化，控制实验当前无效。**
   300/300 units 内所有 10/15 行的 inference `question` 完全相同。适配器使用了原始 `question`，没有使用包含人口学注入的 `case_text`；因此 3,075 行只是同一输入的重复，而非人口学反事实变体。

2. **CLIR 推理视图包含直接答案导出信息，共 400/500 行。**
   - IR 100 行含 `model_direction`
   - TF 100 行含 `condition_met` 及未来观测
   - NIF 100 行含未来 `target_observation`
   - IID 100 行含直接对应正确选项的 `category_combination`

   键名扫描虽为 0，但这是语义级 gold leakage。另 100 行 TSS 的 `fixed_evidence` 仅为 `["all"]`，并非可用时间序列证据。

3. **pair 信息仍可从推理值恢复。**
   - MedEinst 1,000 行：`source_record_id`/`item_id` 暴露 `case_id`，且 `variant` 明示 `control` 或 `trap`。
   - ReMedQA 1,200 行和 CPV 3,075 行：`source_record_id` 或 `item_id` 前缀就是离线 `pair_id`。

   因此“递归禁用键名为 0”成立，但不等于严格的 pair blindness。

SHA-256：

- inference：`c00f2ab43ed712ec25497462fbdd8da82e31df709392612867981d51ce6b4349`
- gold：`efae89b33a419b1a1c6339862f1391b8b265af91cf2d84848ce8a468669d97e6`
- manifest：`6aa94142c029df1da3f407a583ac7da2f14f8ae01bf58f67c608d21c0018a313`
- report：`df3de9a4094ed75dc51b14152f86c266efb3cee06967f60aefa7c3ba3ddccb43`

全程只读，未修改文件。

## 2026-08-23T15:47:50.556Z — Agent commentary

我只会最小修改 CPV 的能力标记与抽样选择器，并重新验证 canonical JSON 与 SHA-256。

## 2026-08-23T15:47:59.714Z — Agent final_answer

已仅修改 `configs/gate_a_sources.json`：

- CPV 新增 `visible_demographic_variants: true`
- selector 改为先筛选组内每行 `case_text` 均不同的 `case_id`，再以 seed 13 冻结抽样 300 个
- canonical JSON 与 `git diff --check` 均通过

新 SHA-256：

`1389258e6248a862d88e7f8894ba96e2bf80e72916425f5d9ca8d313e3740bc5`

## 2026-08-23T15:52:58.612Z — Agent commentary

我会以 v2 的语义缺陷为回归清单，同时独立扫描 v3 的新泄漏面：不仅检查键名，还检查可见值、组内可链接标识、角色标签和 CLIR evidence 与 gold 的可直接映射。全程只读。

## 2026-08-23T15:53:42.359Z — Agent commentary

我会继续按 Ponytail Full 做最小、只读的独立重算；现在重点量化 CPV 文本质量异常，并逐键验证 CLIR evidence allowlist，而不是依赖报告中的 pass/fail。

## 2026-08-23T15:55:04.659Z — Agent commentary

中间结论：v2 的显式 pair/role 字段泄漏已修复，6,577 个推理 ID 全部是不透明哈希且 variant 统一为 `item`。但主动语义检查发现一个新的实质问题：CPV 虽然组内问题都不同，至少 1,035 行出现 “man woman”/“woman man” 这样的冲突人口学文本；我正在核清完整影响面，并排除 CLIR 的隐蔽派生答案字段。
