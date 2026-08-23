# Visible transcript: /root/provenance_audit

- Session: `01a02f2f-7138-7163-8bed-1500adf579ee`
- Timestamps: UTC
- Scope: user/task messages and visible agent commentary/final messages only.

## 2026-08-23T15:13:57.000Z — Agent commentary

I’m applying Ponytail Full as requested, then I’ll audit only the frozen artifacts and handoff copies—no writes or model runs.

## 2026-08-23T15:14:04.115Z — Agent commentary

The workspace guide identifies the live v4 run as authoritative and the GitHub clone as a transfer copy. I’m now checking byte hashes, row/identity relationships, baseline completion state, and the exact final metrics against every summary/handoff surface.

## 2026-08-23T15:14:42.490Z — Agent commentary

The canonical summary is internally complete: status `complete`, matched greedy single generation call, 64/85 strict in both arms, 1/1/83 paired outcomes, CI ±3.5294 pp, p=1.0, and proxy-only provenance. One subtlety needs classification: the earlier P2 aggregate embeds `frozen:false` because it was provisional/formally ineligible, even though the later study froze those exact bytes as its input boundary. I’m checking whether any copy misstates or mutates that distinction.

## 2026-08-23T15:16:09.603Z — Agent final_answer

PASS — acceptance boundary is coherent; no rerun is needed.

Authoritative live source:
`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4`

Evidence:

- `p2_v15_item_results.jsonl`: 1,000 rows, 1,000 unique `(dataset,item_id)` identities; 200 per dataset; Tier counts A=85, B=118, C=724, NONE=73; strict 697/1000, lenient 701/1000; SHA-256 `9403ae0a177a827a5b1cded9bbf321cb97373bfd6d5b2196b3c02e4d58730ba0`.
- `p2_v15_baseline_results.json`: overall strict 697/1000 and lenient 701/1000, matching item rows; SHA-256 `d948f5b60635ecc7c83bda3536fb97670bc5c8179ce2fc0d520cdd413e913a5e`.
- `p4_proxy_all85_input.jsonl`: 85 rows and 85 unique identities; exactly the 85 P2 Tier-A identities in the same order, with no missing or extra IDs. Dataset counts are MedQA 25, MedMCQA 18, MMLU-Med 17, PubMedQA* 25; no answer/gold fields. SHA-256 `863e3299e675dca3f05fdd00667ac824728fc3350c104c827259acece47eb537`.
- Evidence-document cardinality is five for 84 items and zero for one MedQA item; this is the exact recorded boundary, not a copy discrepancy.
- Handoff copies of all three boundary files are byte-identical to live source.

Final accepted summary:

- `p4_matched_rank_greedy_reader_summary.json`: SHA-256 `8723e3f27831524012e239fc493584344839bab22bf2398db85753e67c78517e`, identical in live and handoff copies.
- Status `complete`; matched greedy temperature 0; one generation call over 128 unique prompts; all 42 shared-prompt pairs yielded identical raw/strict/author outputs.
- MD direct: 64/85 strict, 65/85 author.
- MW planner: 64/85 strict, 65/85 author.
- MW−MD: 1 improvement, 1 regression, 83 unchanged; 0.0 pp; bootstrap CI `[-3.5294,+3.5294]`; exact McNemar `p=1.0`.
- 170 prediction and 170 result rows, exactly 85 identities per condition; predictions contain no gold/correctness fields; all rows are `human_validated=false`, `grounding=parametric_no_nice`.
- Live protocol section 18, `/home/data3/txy/AGENTS.md`, summary JSON, and handoff README all agree: stop the WM claim, retain only exploratory action-aware/direct-ranking evidence, and do not rerun for this decision.

All-Llama v15 baseline:

- Runtime state: `completed`, `current_stage=done`, all eight stages listed, exit code 0, finished `2026-08-17T12:57:32Z`.
- `metrics.json` SHA-256 `02ad23c42603e42738ef2cd09802925f64f89de8ead8bf9ca1a50ead64882ba6`.
- 7,663 total questions; strict macro `69.90336487156289%`; author macro `70.02965230218278%`; `experimental_not_table1=true`.
- The status helper prints `process_alive=yes`, but PID 3569374 is a defunct zombie. This is stale liveness reporting, not an active run or incomplete result.

Handoff/Git:

- Handoff clone is clean on `main`, aligned with `origin/main`, commit `c86ec675a3948af430a099c7c5a14abdffe236d5`.
- Exactly 104 tracked handoff files; 84 files recursively in the recorded v4 run, matching README/FILE_INDEX.
- The transferred protocol is historically named `medrgag_wm_validation_pack/agent.md`; it differs from the renamed live results record only in the title and six-line explanatory preamble. Sections 1–18, final numbers, and stop decision agree.

Stale/non-authoritative surfaces:

- `/home/data3/txy/MedRGAG/agent.md` says the lenient v15 run was “not started” and its final checkpoint says full MedRGAG was not run. It predates the completed runtime state and metrics and must not be used for current status.
- The v4 `manifest.json` and P2 aggregate embed `frozen:false`, `provisional:true`, and formal-ineligibility metadata from the original proxy-label phase. “Frozen boundary” here means downstream consumption froze these exact bytes; it does not retroactively make the proxy labels formally frozen or human-validated.
- The early `medrgag_validation_pack/`, `medrgag_wm_validation_pack.zip`, and the separate current checkout’s untracked `cf_medrgag_validation_pack/` are not authoritative result sources.
- `/home/data3/txy/MedRGAG` remains at upstream tracked commit `0057853df65dcaa46d2934a28f8d5025fc3de623` with many intentional untracked reproduction files.
- Current checkout is at `d3bf7e69a40b3838c162934715ecf2024689dfd5` with untracked `cf_medrgag_validation_pack/`.

No files were modified; all untracked material was preserved.

## 2026-08-23T15:18:47.716Z — Agent commentary

I’m keeping Ponytail Full active and treating this as a read-only gate-design audit. I’ll map the four-dataset protocol to the existing evaluation interfaces, then separate deterministic public-label checks from judge-dependent claims and identify the smallest honest pilot.

## 2026-08-23T15:18:55.057Z — Agent commentary

The plan and `no_go.yaml` are not perfectly aligned: the plan’s lower claim boundary says MedPIC +3 pp, while section 12’s “world model” gate requires +5 pp; shuffle is fatal below 2 pp but full WM naming requires at least 5 pp. I’ll preserve both as staged claim levels rather than collapse them into one threshold.

## 2026-08-23T15:19:18.482Z — Agent commentary

The reusable evaluator is useful only as scaffolding: its accuracy parser assumes one string label, its method mapping is from the prior M0–M10 study, and its pair helper does not implement MedPIC exact sets, MedEinst normalized diagnosis, CLIR timestamps/intervals, or MedCounterFact’s two-headed output. I’m verifying the official dataset label surfaces before marking any metric as code-computable.

## 2026-08-23T15:22:08.822Z — Agent final_answer

Verdict: EVALUATION DESIGN PASS; CURRENT EXECUTABILITY FAIL.

The four-dataset plan is scientifically testable, but the current `cf_medrgag_validation_pack` is documentation-only. Its sole validator cannot score the study, and the reusable active-pack evaluator is tied to the earlier Tier-A/M7 study. It must be adapted before any real pilot.

## Blocking mismatches

- Current plan defines M0–M13 with M9 as full method, M11 shuffle, M12 oracle.
- Reusable `aggregate_metrics.py` hard-codes M7 as full, M9 as shuffle, M10 as oracle and requires M0–M10. Reusing it unchanged would evaluate the wrong methods.
- `accuracy.py` compares one string; it cannot score MedPIC answer sets, MedEinst normalized diagnoses, CLIR evidence/timestamps, or MedCounterFact’s two-headed output.
- `paired_bootstrap()` resamples items, not the required pair/rule/disease/stay clusters.
- `counterfactual_pairs.py` is not compatible with the proposed pair records.
- Existing `audit_no_go.py` implements the prior study’s gates, not current `configs/no_go.yaml`.
- The unified schema mixes inference-visible content and evaluator-only `answer`, `pair_id`, direction fields. A separate sanitized inference file and sealed gold/pair file are required.
- `validate_manifest.py` checks declared `inference_visible_fields`, but does not inspect actual prompts/traces, cache keys, shared memory, pair co-batching, test prompt selection, or option text in transition prompts.
- CPV has no pinned repository/revision/license in `datasets.yaml`, yet Gate A asks for 300 CPV items.
- Public CLIR currently exposes 11 JSONL files with `id`, MCQ `answer`, `answer_text`, `episode_id`, `anchor_time`, and structured gold `evidence`; the repository does not visibly provide full patient time series or explicit edit-pair metadata. Thus QA-only and gold Evidence-only scoring are available, but the stated Full-TS and official causal-edit pilot are blocked until the underlying trajectory/pair source is obtained and pinned. [Official CLIR files](https://huggingface.co/datasets/winall/CLIR-Bench/tree/main)
- MedPIC’s public rows expose exact-set answers and taxonomies, but no visible `pair_id`/change-direction field. The claimed 89 linked-pair mapping must be sourced or deterministically preregistered before pair/activation/deactivation metrics. [Official MedPIC dataset](https://huggingface.co/datasets/TIM0927/MedPIC-Bench)
- MedEinst provides the needed `case_id`, `case_type`, narrative, and `ground_truth` fields for 5,383 test pairs. [Official MedEinst card](https://huggingface.co/datasets/zhui711/MedEinst/blob/main/README.md)
- MedCounterFact provides paired IDs, fixed RCT summaries, conclusion labels, replacement category/item, and provenance metadata. [Official format](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence/blob/main/DataFormat.md)

## Smallest honest adaptive pilot

“Small” means staged, not synthetic:

1. Gate A must first create the entire declared pilot boundary:
   - MedPIC: all 467 rows.
   - CLIR: 100 from each genuinely available preregistered key task, target 500.
   - MedEinst: 500 pairs = 1,000 independent inference rows.
   - MedCounterFact: 50 per four replacement classes = 200 replaced rows plus their 200 paired originals.
   - ReMedQA and CPV: 300 each if the plan’s exact Gate A is retained.
   - No model run until pair maps, CLIR Full-TS source, CPV source, hashes, and leakage tests pass.

2. Gate B: M0, M1, M2 over the complete frozen pilot, three seeds for stochastic generator paths.

3. Gate C: M12 versus M2 on the minimum preregistered 100 oracle units, stratified across MedPIC applicability and CLIR transition tasks. Stop if gain is below 2 pp per `fatal_failures`; report uncertainty even if the point threshold passes.

4. Only if M12 passes:
   - Run M3, M4, M5 first.
   - If M9 cannot plausibly beat these controls, stop.
   - If it can, the plan explicitly requires M6–M11. Skipping M6/M7/M8/M10 would no longer be an honest execution of Gate D.
   - M13 is never required and never enters primary results; run it only as a clearly isolated diagnostic upper bound.

Thus the minimum claim-eligible method set is M0–M12 excluding M13, executed adaptively in the order:
`M0,M1,M2 → M12 → M3,M4,M5 → M6,M7,M8,M9,M10,M11`.

## Required artifact interfaces

Use four physically separate artifacts.

`pilot.inference.jsonl` — answer-free:

```json
{
  "item_id": "medpic/...",
  "dataset": "medpic",
  "task_family": "medication_rule_cf",
  "variant": "counterfactual",
  "question": "...",
  "options": {"A": "..."},
  "patient_state": {},
  "time_series": [],
  "fixed_evidence": [],
  "candidate_actions": [],
  "input_hash": "...",
  "visible_fields": ["question", "options", "patient_state"]
}
```

It must not contain `answer`, `pair_id`, counterpart identity/label, `should_answer_change`, or `change_direction`.

`pilot.gold.jsonl` — evaluator-only and sealed:

```json
{
  "item_id": "...",
  "pair_id": "...",
  "answer": ["A", "C"],
  "change_direction": "deactivate",
  "should_answer_change": true,
  "gold_evidence_ids": ["E3"],
  "cluster_id": "...",
  "strata": {}
}
```

`predictions/<run>/<method>/<seed>.jsonl`:

```json
{
  "run_id": "...",
  "item_id": "...",
  "dataset": "...",
  "task_family": "...",
  "method": "M9",
  "seed": 13,
  "input_hash": "...",
  "prediction": {
    "answer_set": ["A"],
    "diagnosis": null,
    "evidence_conclusion": null,
    "real_world_safety_flag": null,
    "evidence_ids": [],
    "confidence": null
  },
  "parse_status": "ok",
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "retrieval_calls": 0,
  "model_calls": 0,
  "trace_hash": "..."
}
```

`traces/<run>/<method>/<seed>/<item>.json`:

- Exact visible input fields and rendered prompt hashes.
- Retrieval queries and returned document IDs.
- Generated and selected contexts with provenance IDs.
- State, candidates, transition cards, comparator/rollout.
- Transition-generation visible fields and explicit `options_visible=false`.
- Raw response, parser result, retries, model/tokenizer revisions and generation parameters.
- Stage token/call/latency accounting.

Every directory needs an immutable manifest binding dataset revisions, raw/adapted/inference/gold hashes, prompts, code commit, configs, model/tokenizer revisions, item×method×seed matrix, and result count.

## Deterministic metric matrix

| Dataset | Deterministic from public labels | Needs extra mapping or judgment |
|---|---|---|
| MedPIC | Exact-set row accuracy and taxonomy-stratified GF/CF accuracy | Pair accuracy, activation/deactivation and warning persistence need authoritative linked-pair/direction mapping; applicability fidelity needs rule annotations or blinded judgment |
| CLIR | MCQ/task accuracy; direction/forecast/decision accuracy where task label defines it; evidence ID precision/recall/F1 and timestamp attribution after deterministic evidence-ID normalization | Causal flip/invariance need official edit pairs; Full-TS needs trajectory source; semantic evidence sufficiency/necessity requires controlled reruns and possibly judgment |
| MedEinst | Control accuracy, trap accuracy, paired-correct rate, control-label persistence; `BTR = #(control correct ∧ trap prediction = control gold) / #control correct` | Semantically equivalent open diagnoses require a frozen alias map or blind adjudication; changed-evidence attribution needs edit-span metadata/judgment |
| MedCounterFact | Evidence-conclusion accuracy against `higher/lower/no difference`; category recognition against `MainCategory`; literal normalization checks; exact provenance-ID accuracy | Safety boundary, semantic normalization, unsupported context contamination, and evidence/provenance faithfulness need blinded human or frozen LLM-judge review |
| ReMedQA/CPV | Official accuracy and linked-pair correct-invariance | Semantic open-answer equivalence if official scorer does not resolve it |

Pair metrics must be code, never an LLM:

- `pair_correct = base_correct && edited_correct`
- `correct_change = edited_correct && pred_base != pred_edit && gold_base != gold_edit`
- `correct_invariance = both_correct && pred_base == pred_edit` for invariant controls
- MedPIC activation/deactivation must score gold set additions/removals, not merely whether the whole prediction changed.
- Bias Trap Rate must remain conditional on control correctness.

## Statistics

For every declared comparison, align identical cluster identities first.

- Primary comparisons: M9–M2, M9–M3, M9–M4, M9–M5, M9–M8, M9–M11.
- Bootstrap 10,000 times using one sampled unit per official cluster:
  - MedPIC: linked pair/rule.
  - CLIR: patient stay or official edit pair.
  - MedEinst: `case_id`.
  - MedCounterFact: shared original/replaced `metadata.id`.
  - Controls: perturbation pair.
- Report point difference, percentile 95% CI, discordant counts and exact McNemar p-value on the same binary unit outcome.
- Do not treat three seeds as three independent items. Report each seed and the seed-mean effect; use identical seeds across methods.
- Apply Holm correction across activation/deactivation, dataset-level primary comparisons, and multiple method contrasts.
- Mixed-effects regression is secondary and cannot replace paired gates.

The active pack’s standard-library `exact_mcnemar()` and `holm_correction()` are reusable. `paired_bootstrap()` needs a cluster-aware replacement.

## Shuffle and leakage acceptance

M11 must be a seeded within-item derangement:

- MedPIC/actions: reassign effect/exception fields across candidates.
- CLIR: reassign timestamp/evidence mappings across candidate transitions.
- Preserve every byte of content, candidate count, evidence documents, reader envelope, generation budget and final context ceiling; only mapping changes.
- Validate no fixed points unless fewer than two candidates, which must be excluded/reported.
- Compare M9 and M11 on identical items/seeds.
- `<2 pp` pair/transition drop is fatal; `2–<5 pp` permits at most a limited claim; `≥5 pp` is required for textual-WM naming.

Leakage audit must mechanically establish:

- Inference file and all rendered prompts omit gold/pair/direction fields and values.
- Transition prompts omit option labels and option text.
- Pair members have independent prompt construction/cache namespaces and no shared visible memory.
- Gold/evaluator files are opened only after immutable predictions are complete.
- Prompt/config hashes predate official test inference.
- No test outcome was used for item or prompt selection.

Any pair leakage or test prompt selection invalidates the run rather than merely failing one metric.

## Gate/early-stop matrix

- Gate A: any missing revision/hash, malformed adapter, duplicate/missing identity, unavailable required pair mapping, CLIR trajectory source, or leakage → stop before inference.
- Gate B: absence of an M2 counterfactual deficit blocks a structural-failure claim, though the preregistered oracle diagnostic may still run.
- Gate C: M12 gain `<2 pp` versus M2 → fatal stop. This is stricter than the plan prose’s vague “no improvement” and follows `no_go.yaml`.
- Controls: if M9 is not better than both M3 and M5 → fatal development stop. For the stronger state-update claim it must beat M3, M4 and M5.
- Entailment `<0.70` → fatal; `0.70–<0.80` → no textual-WM claim.
- M11 drop `<2 pp` → fatal; `<5 pp` → no textual-WM claim.
- Pair leakage or test-set prompt selection → invalidate all affected results.
- ReMedQA/CPV drop >1 pp, CLIR invariance drop >2 pp, MedEinst control drop >1 pp, or a significant MedCounterFact faithfulness/safety tradeoff → no textual-WM claim.
- M13 never rescues a failed gate.

Claim thresholds should remain staged:

- Action-aware guideline reasoning: MedPIC pair and deactivation +3 pp, beating M3 or M5.
- Counterfactual state-update layer: MedPIC pair/deactivation +5 pp, MedEinst trap +3 pp, BTR relative reduction ≥20%, control drop ≤1 pp, beating M3/M4/M5.
- Textual clinical WM: all prior gates plus CLIR causal flip +10 pp, IR/forecast/decision +3 pp over strongest equal-budget control, invariance drop ≤2 pp, shuffle drop ≥5 pp, entailment ≥80%, controls ≤1 pp degradation, significant improvement on at least two action/transition datasets, and no significant MedCounterFact faithfulness/safety tradeoff.

## Commands and completion evidence

Currently executable validation only:

```bash
cd /home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack
python scripts/validate_manifest.py pilot.gold.jsonl schemas/unified_item.schema.json
```

This is insufficient because it validates the gold-containing unified record, not a sanitized inference boundary.

Reusable statistical interfaces:

```python
from src.evaluation.paired_stats import exact_mcnemar, holm_correction
from src.evaluation.cost import summarize_cost
from src.evaluation.transition_fidelity import summarize_judgments
```

Do not run the existing `aggregate_metrics.py` or `audit_no_go.py` against this study until their method mapping and gates are replaced.

A real pilot is complete only when evidence includes:

- Frozen source revisions and SHA-256 values.
- Expected Gate-A counts and authoritative pair/cluster maps.
- Sanitized inference/gold separation and leakage audit PASS.
- Complete item×method×seed prediction matrix with zero duplicates/missing rows.
- Trace and prediction hashes, real-backend marker, model/tokenizer/prompt/config hashes.
- M2–M11 token, selected-document and retrieval-call parity report.
- Oracle-card provenance/review record.
- Deterministic dataset metrics plus 10,000-draw cluster bootstrap, McNemar and Holm outputs.
- Blinded transition/safety judgment artifact with inter-reviewer agreement; LLM-only judgments must be labelled provisional.
- Current-plan no-go report with every metric `pass`, `fail`, or `insufficient-data`—never silently absent.

No files were modified; the untracked validation pack was preserved.

## 2026-08-23T15:28:28.754Z — Agent commentary

I’ll implement a single strict auditor and two focused tests. The production thresholds stay fixed to the plan; the passing fixture will generate the full declared Gate-A counts rather than weakening requirements for tests.

## 2026-08-23T15:29:52.851Z — Agent commentary

The source registry now has a concrete schema, so I’m aligning the auditor to its actual `datasets.*.{revision,license,pilot,capabilities}` fields rather than leaving a parallel convention. Then I’ll run the two target tests and the auditor against the real registry to confirm it stops for real missing evidence.

## 2026-08-23T15:31:38.775Z — Agent final_answer

Implemented the independent Gate-A auditor:

- [audit_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/audit_gate_a.py)
- [test_audit_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/tests/test_audit_gate_a.py)

It validates the actual registry schema, bound raw hashes, counts, identities, input hashes, recursive leakage, gold/pair structure, MedCounterFact fixed evidence, CLIR repository/Full-TS/edit-pair evidence, MedPIC 89-pair mapping, licenses, adapters, and controls. Any fail/insufficient check yields `stop_before_inference`; CLI exits 1 while writing the report.

Verification:

```text
python3 -m unittest -v tests/test_audit_gate_a.py
Ran 2 tests ... OK
```

Both the full-size passing fixture and realistic missing-pair/Full-TS stop case pass. `py_compile` also passes. No other files were changed.

## 2026-08-23T15:42:13.285Z — Agent commentary

I’ll treat the prepared v2 directory as immutable and independently recompute its file bindings, row/count relationships, and report statuses. I’ll specifically distinguish genuine public-source limitations from auditor/prepare schema mismatches.

## 2026-08-23T15:42:31.217Z — Agent commentary

The recorded report has exactly four blocker groups and all other checks pass. I’m now recomputing—not trusting the report—the 14 raw hashes, revision path bindings, canonical manifest self-hash, 6,642-row identity/input-hash/leakage checks, and MedCounterFact companion/category structure.

## 2026-08-23T15:43:44.018Z — Agent final_answer

独立验收结论：PASS（报告正确），但 Gate-A 应保持 `stop_before_inference`。

精确证据：

- Registry SHA-256：`9714e575ad628bc448c67fd34c50c8141c9ab2247d8c6a77b2c790c77d0dba7b`
- Manifest 文件 SHA-256：`6aa94142c029df1da3f407a583ac7da2f14f8ae01bf58f67c608d21c0018a313`
- Manifest 排除自哈希字段后的 canonical hash：`8dce7cdc5c654beecda7ab936d0c8f7dd0fbfa85b12c9a411a4bdf07039c3bca`，与声明一致。
- Inference：6,642 行，SHA-256 `c00f2ab43ed712ec25497462fbdd8da82e31df709392612867981d51ce6b4349`
- Gold：6,642 行，SHA-256 `efae89b33a419b1a1c6339862f1391b8b265af91cf2d84848ce8a468669d97e6`
- 两侧均为 6,642 个唯一身份，identity set 完全相同。
- 全部 6,642 个 `input_hash` 独立重算通过；递归禁用字段出现数为 0。
- 14 个 raw artifacts 全部存在，字节 SHA、registry revision、manifest revision及路径 revision 段全部一致。
- Registry 与 manifest 六个数据集的 revision/license/capabilities/pilot 全部一致。
- 当前 auditor 只读重算所得 `checks` 和 `blockers` 与保存报告逐字结构一致，排除陈旧报告或代码路径偏差。

报告正好 4 个 blocker 组：

1. `source_licenses`
   - MedCounterFact：`missing_repository_license`
   - ReMedQA：`missing_dataset_card_license`
   - 官方 MedCounterFact 仓库当前文件列表未显示 LICENSE；ReMedQA 数据页也未声明 License 字段。因此属于公开源许可缺失，而非适配器错误。[MedCounterFact](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence)、[ReMedQA](https://huggingface.co/datasets/disi-unibo-nlp/ReMedQA)

2. `medpic_official_89_linked_pairs`
   - Registry 明确 `official_pair_map=false`。
   - 原始行字段无 pair key；观察到官方 pair 数为 0，而计划需要 89。
   - 属于公开源能力缺失。

3. `clir_full_ts`
   - Registry 明确 `full_timeseries=false`。
   - 500/500 pilot 行无 Full-TS；公开 JSONL 只有 anchor/evidence 等字段。
   - 五个 repository files 均已下载、绑定并校验，因此不是下载或 hash 错误。

4. `clir_official_causal_edit_pairs`
   - Registry 明确 `official_edit_pairs=false`。
   - 观察到官方 causal-edit pair 数为 0。
   - 属于公开源能力缺失。

其余 13 个 checks 全部 PASS，包括 adapters/counts、CLIR repository evidence、controls、gold completeness、identity equality、input hashes、manifest bindings、MedCounterFact fixed evidence、无泄漏、pair/cluster、类别目标、raw/revision hashes、unique identities。

额外核验：

- MedCounterFact 400 行结构正确：200 counterfactual + 200 个一一对应 original companions；200 个有效 pair，无坏 companion。
- 四类各 50：`medical/non_medical/nonce/toxic`。
- MedEinst 500 pairs。
- ReMedQA 300 control IDs → 1,200 行；CPV 300 case IDs → 3,075 行，报告按控制单元计数正确。
- 数据集行数：MedPIC 467、CLIR 500、MedEinst 1,000、MedCounterFact 400、ReMedQA 1,200、CPV 3,075。

未发现 schema mismatch、计数误判、hash 漂移或 auditor bug。没有修改任何文件。

## 2026-08-23T15:46:20.118Z — Agent commentary

I’m tightening only the three requested semantic boundaries. I’ll derive pair-role secrets from the joined gold record rather than rely solely on a generic blacklist, so opaque passing fixtures remain valid while the real CPV/MedEinst-style identifiers and roles fail closed.

## 2026-08-23T15:48:02.476Z — Agent commentary

The stricter fixture suite passes. I’m doing one final read-only run against v2 to confirm the new rules catch the known defects with useful counts, without introducing unrelated false failures.

## 2026-08-23T15:48:52.525Z — Agent final_answer

Enhanced only:

- [audit_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/audit_gate_a.py)
- [test_audit_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/tests/test_audit_gate_a.py)

New fail-closed checks:

- Every CPV unit must have exactly one distinct inference question per row.
- Gold-joined pair blindness rejects pair IDs, raw case IDs, and pair roles exposed through `item_id`, `variant`, or metadata values.
- CLIR rejects `model_direction`, `condition_met`, `target_observation`, and `category_combination`.
- `["all"]` and `{"TSS":["all"]}` do not qualify as repository observations.

Verification:

```text
Ran 3 tests in 0.627s
OK
```

Passing fixture, missing-capability stop fixture, and semantic-leakage stop fixture all pass. `py_compile` also passes.

## 2026-08-23T15:53:05.150Z — Agent commentary

I’ll independently recompute v3 from bytes and replay the auditor in memory, then compare every saved field. I’ll also inspect the five failed checks against raw/public-source structure so adapter defects cannot hide behind capability labels.

## 2026-08-23T15:53:54.632Z — Agent commentary

我会把“报告一致”与“Gate 通过”分开判定：先内存重放并做递归字段差异，再从原始字节独立核验 hash、revision、绑定和 5 个失败项的源头。Ponytail Full 在这里约束为只做最小、可复现的只读检查，不生成任何新产物。

## 2026-08-23T15:54:09.676Z — Agent commentary

首轮发现一个可解释的非语义差异：用绝对路径调用时，重放报告只在 `inputs.*` 四个路径字符串上不同；审计结论并未漂移。我现在按保存报告使用的相对 CLI 接口重放，以确认真正的逐字段一致性。

## 2026-08-23T15:55:31.828Z — Agent commentary

字节绑定和 14 个原件目前全部吻合。CLIR 的 300 个缺口也呈现明确结构：t7/t9/t10 各 100 条；t6/t8 各 100 条保留了非答案导出的可见观测，500 条都没有 Full‑TS。接下来我会核对原始字段，确认这 300 条不是适配器误删了合法观测。
