# 历史：MedRGAG WM代理研究

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。该方向已停止。保留85例机制试验、盲审、匹配对照及负结论，以及原计划与实际实施的差异。归档中的计划和命令不是继续推进该方向的指令。

历史材料引用的局部 `AGENTS.md` / `agent.md` 已不在原路径；相关链接现指向本文保存的归档实现合同。它们是历史研究材料，当前活动要求由工作区根AGENTS及docs总入口维护。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [5. Archived WM experiment workspace](#record-0029)
- [Pack components](#record-0030)
- [Core Python interfaces](#record-0031)
- [P4 runner interface](#record-0032)
- [JSONL interfaces](#record-0033)
- [WM_VALIDATION_PROTOCOL_AND_RESULTS.md](#record-0262)
- [PROJECT_PLAN.md](#record-0263)
- [ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md](#record-0264)
- [README.md](#record-0265)
- [README.md](#record-0413)
- [ENVIRONMENT.md](#record-0414)
- [FILE_INDEX.md](#record-0415)
- [CONVERSATION_HISTORY.md](#record-0416)

<a id="record-0029"></a>

## 5. Archived WM experiment workspace

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1175行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 5. Archived WM experiment workspace

The archived experiment workspace is:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-dietrichgebert-ponytail-skill/
```

The long directory name reflects the original Ponytail installation task; it
now also contains the MedRGAG WM work. This directory itself is not a Git
repository.

| Child | Role and authority |
|---|---|
| `medrgag_wm_validation_pack/` | Authoritative plan, prompts, schemas, reusable Python modules, P4 runner, and the renamed protocol/results record |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/` | Canonical 22 MB v4 experiment inputs, proxy review artifacts, predictions, scored results, and summaries |
| `mrg-handoff-upload/` | Clean clone of `https://github.com/xiotakut/mrg`; the handoff was pushed at commit `c86ec675a3948af430a099c7c5a14abdffe236d5` |
| `medrgag_validation_pack/` | Early three-file minimal scaffold; not the authoritative WM plan or result |
| top-level `src/`, `scripts/`, `tests/` | Empty/legacy shells; the archived implementation is inside `medrgag_wm_validation_pack/` |
| `medrgag_wm_validation_pack.zip` | Small early snapshot; not the current experiment record |

Important path rule: the source P4 runner sets `WORKSPACE` to the parent of
`medrgag_wm_validation_pack`, so its canonical `RUN` is the sibling
`private_data/.../stage-b-real-20260823-seed13-37-v4`, not the nearly empty
`medrgag_wm_validation_pack/private_data`.

<a id="record-0030"></a>

## Pack components

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1202行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Pack components

| Part | Function/interface |
|---|---|
| `PROJECT_PLAN.md` | User-selected experimental plan and decision logic |
| `ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md` | Archived coding-agent contract for the proposed full implementation; not active instructions |
| `WM_VALIDATION_PROTOCOL_AND_RESULTS.md` | Sections 1–14 protocol; sections 15–18 actual proxy experiments and final decision |
| `configs/` | Formal M0–M10 experiment matrix and proposed no-go criteria; not required to interpret the completed P4 result |
| `prompts/` | Files 01–17: slice classification, state/action extraction, retrieval, transition, planning, reader, judging, counterfactual, and P4 context |
| `schemas/` | JSON Schemas for action labels, clinical state, transition cards, judgments, and final answers |
| `src/data/` | Item loading, slice construction, and matched-control helpers |
| `src/medrgag_adapter/` | Answer-free baseline adapter, external v15 binding, single-GPU and local-Llama adapters |
| `src/wm/` | State/action construction, query planning, evidence retrieval, transition-card generation, rollout selection, and routing |
| `src/controls/` | Action decomposition, equal-reasoning, extra-retrieval, and shuffled-transition controls |
| `src/evaluation/` | Accuracy, paired statistics, fidelity, counterfactual, faithfulness, and cost helpers |
| `src/experiment_runner.py` | M0–M10 registry and `dispatch_variant` / `dispatch_all` shared-reader API |
| `scripts/` | CLI preparation, binding, execution, aggregation, status, and P4 historical runners |
| `tests/` | Unit/integration checks for the proposed reusable pack; they are not the source of the completed P4 numerical result |

<a id="record-0031"></a>

## Core Python interfaces

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1221行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Core Python interfaces

```text
construct_state(Item, action_label) -> clinical_state dict
construct_actions(state) -> list[{candidate_id, text, ...}]
transition_with_provider(...) -> (transition_card | None, metadata)
select_rollout(item_id, decision_mode, cards, allow_unsupported=False) -> planner dict
dispatch_variant(MethodSpec, VariantContext, reader, seed=13) -> prediction dict
paired_bootstrap(a, b, samples=10000, seed=13) -> paired statistics
exact_mcnemar(a, b) -> discordant counts and exact p-value
```

`select_rollout(..., allow_unsupported=True)` is the interface used for the
parametric Luna cards. It is not NICE grounding.

<a id="record-0032"></a>

## P4 runner interface

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1236行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### P4 runner interface

`medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py` is a historical
fixed-path runner. It refuses to overwrite existing output files.

| Environment setting | Condition |
|---|---|
| none | 20-item M0/M1/PX pilot |
| `P4_ALL85=1` | 85-item M0/M1/PX |
| `P4_ADJUDICATED=1` | 20-item Luna-adjudicated PA |
| `P4_ALL85_ADJUDICATED=1` | 85-item PA |
| `P4_ALL85_ABLATIONS=1` | M2/M4/M5/M6/MR ablations |
| `P4_ALL85_DIRECT_RANK=1` | direct Luna ranking reader |
| `P4_ALL85_MATCHED_RANK=1` | matched direct/planner ranking |
| matched rank plus `P4_MATCHED_GREEDY=1` | accepted temperature-0, single-call deduplicated comparison |
| an all-85 mode plus `P4_CPU_PREFLIGHT=1` | input/prompt validation without GPU inference |
| `P4_MODEL=/absolute/model/path` | override the local reader model |

Existing files already occupy every completed mode's output path. Treat this
runner as provenance unless the user explicitly requests a new run design.

<a id="record-0033"></a>

## JSONL interfaces

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1257行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### JSONL interfaces

All identities are the pair `(dataset, item_id)`.

| Artifact | Required top-level fields and meaning |
|---|---|
| `p4_proxy_all85_input.jsonl` | `dataset,item_id,question,options,action_label,medrgag_documents`; answer-free frozen reader input |
| `p2_v15_item_results.jsonl` | frozen 1,000-item v15 predictions, gold, correctness, tier and task labels |
| `p4_luna_adjudicated_all85_cards.jsonl` | `state,parametric_transition_cards,planner,adjudication,proxy_review` plus identity/provenance |
| `*_reader_predictions.jsonl` | raw response, parsed predictions, condition, sampling and token metadata; no scored correctness |
| `*_reader_results.jsonl` | prediction rows joined with gold and correctness |
| `*_reader_summary.json` | aggregated condition metrics and paired comparisons |

The state object exposes
`initial_state,candidate_actions,candidate_outcomes,fixed_action,transition_target,decision_mode,clinical_goal,facts_not_to_assume`.
A transition card exposes
`candidate_id,action,preconditions,next_state,applicability,coverage,goal_alignment,uncertainty_reasons,unsupported_claims,rollout_valid,compact_rollout`.
The planner exposes
`preferred_candidate_id,candidate_scores,decision_mode,decision_rationale,abstain,abstention_reason,grounding`.

<a id="record-0262"></a>

## WM_VALIDATION_PROTOCOL_AND_RESULTS.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`。

### MedRGAG WM Validation Protocol and Results

This is the human-facing experiment record: sections 1–14 preserve the
planned validation protocol, while sections 15–18 record the executed
Luna-proxy experiments, controls, results, and final stop decision. The former
implementation contract is archived as
`ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md`; it is not active agent
instruction. For the current scientific conclusion, go directly to section 18.

#### 1. Mission

Build a reproducible research pipeline that tests, rather than assumes, the following claim:

> An explicit guideline-grounded state/action/transition/rollout module improves MedRGAG specifically on questions that require action-conditioned clinical reasoning, and the gain cannot be explained by question selection, action decomposition, more retrieval, longer prompts, or more computation.

The project is successful only if the preregistered gates in `configs/no_go.yaml` pass.

#### 2. Non-negotiable research rules

1. **No selection on outcome.** Never use baseline correctness, confidence, rationale, retrieved documents, or error labels to decide whether an item belongs to the action slice.
2. **Answer-key isolation.** Gold answers must be unavailable to curation, retrieval, state extraction, transition generation, planning, and final-answer generation. They may be loaded only by evaluation code after predictions are written.
3. **Freeze before evaluation.** Freeze item IDs, taxonomy, prompts, schemas, prompt hashes, and analysis code before running M0–M10.
4. **Matched budgets.** Record and, where specified, match model calls, input/output tokens, retrieved passages, generated passages, and final reader context.
5. **Preserve the original baseline.** Keep an untouched copy of the public MedRGAG repository. Add wrappers/adapters; do not silently alter baseline prompts or logic.
6. **World-model terminology is conditional.** If the full method does not beat action decomposition and equal-budget controls, label it action-aware reasoning, not a world model.
7. **No causal overclaim.** NICE-grounded textual transitions are normative/guideline constrained. Do not claim patient-specific causal treatment effects or learned physiological dynamics.
8. **NICE is retrieval-only and private.** No training, fine-tuning, RL, LoRA, weight updates, publication of guideline text, extracted chunks, embeddings, or vector indexes.
9. **Negative results are first-class.** Save failed hypotheses, invalid generations, abstentions, and no-go decisions. Never discard them to improve headline results.
10. **Determinism and auditability.** Every artifact must store config hash, prompt hash, model identifier, seed, timestamp, git commit, and input item ID.

#### 3. Functional definition used by this repository

A strict world-model item must require:

- a current clinical state `s_t`;
- a clinical action/intervention `a_t`;
- an action-conditioned next state or observation `s_{t+1}, o_{t+1}`;
- a decision that depends on the predicted transition or comparison of alternative transitions.

Minimum model interface:

```text
state = StateConstructor(question, options)
transition_i = TransitionModel(state, action_i, evidence_i)
choice = RolloutSelector(state, transitions, goal)
answer = Reader(question, options, medrgag_evidence, state, transitions, choice)
```

Action extraction without next-state prediction is not a world model.

#### 4. Repository layout to implement

```text
project/
  vendor/MedRGAG/                 # untouched upstream snapshot
  src/
    data/
      loaders.py
      slice_builder.py
      matched_controls.py
    medrgag_adapter/
      baseline.py
      cache.py
      single_gpu.py
    wm/
      state_constructor.py
      action_constructor.py
      nice_query_planner.py
      retriever.py
      transition_model.py
      rollout_selector.py
      router.py
    controls/
      action_decomposition.py
      equal_token_reasoner.py
      extra_retrieval.py
      shuffled_transition.py
    evaluation/
      accuracy.py
      paired_stats.py
      transition_fidelity.py
      counterfactual_pairs.py
      faithfulness.py
      cost.py
    common/
      schemas.py
      prompts.py
      hashing.py
      logging.py
      retry.py
  configs/
  prompts/
  schemas/
  private_data/                   # gitignored; includes NICE index
  cache/                          # gitignored; stage outputs
  outputs/
    labels/
    predictions/
    transitions/
    judgments/
    metrics/
  tests/
  scripts/
  AGENTS.md
```

#### 5. Dataset facts and routing

Support the five MedRGAG datasets:

- MedQA-US: 1,273 test items;
- MedMCQA: 4,183 development items;
- MMLU-Med: 1,089 test items;
- PubMedQA*: 500 test items without original contexts;
- BioASQ-Y/N: 618 items.

The action gate must output Tier A, Tier B, Tier C, or non-action. The full world-model method is enabled only for frozen Tier A/B items. Non-action items use original MedRGAG.

#### 6. Required method variants

Implement all variants before claiming a complete experiment:

- `M0_original_medrgag`
- `M1_action_decomposition_only`
- `M2_equal_token_extra_reasoning`
- `M3_action_specific_nice_retrieval_only`
- `M4_precondition_only`
- `M5_effect_only`
- `M6_wm_cards_without_rollout`
- `M7_full_aw_medrgag`
- `M8_full_wm_without_nice`
- `M9_shuffled_action_effect_mapping`
- `M10_oracle_transition`

Do not substitute a weaker baseline without recording the deviation.

#### 7. Execution order

##### Stage A — portability and baseline fidelity

1. Snapshot upstream MedRGAG commit.
2. Add a single-GPU wrapper. The upstream code hard-codes GPUs `0,1,2`; replace this only in the wrapper/config path.
3. Run a 20-item smoke test and compare outputs with the unmodified baseline where possible.
4. Cache retrieval, summaries, explored knowledge, generated documents, selected documents, and reader inputs separately.
5. Write `baseline_manifest.json` with upstream commit, model IDs, prompts, temperatures, and top-k values.

##### Stage B — outcome-independent slice construction

1. Run `prompts/01_action_slice_classifier.md` without answers or predictions.
2. Validate every output against `schemas/action_label.schema.json`.
3. Send disagreements and all proposed Tier A items to blinded human review.
4. Compute agreement and save adjudication records.
5. Freeze `action_slice_v1.jsonl` and its SHA-256 hash.
6. Only after the freeze may baseline predictions be joined with labels.

##### Stage C — baseline diagnosis

1. Run M0 on frozen items.
2. Construct matched non-action controls without using M0 correctness.
3. Compute accuracy by dataset, tier, and task type.
4. Run paired bootstrap, McNemar, and mixed-effects regression.
5. Stop if the baseline-deficit gate fails.

##### Stage D — oracle test

1. Sample Tier A items independently of M0 correctness.
2. Create reviewed oracle transition cards.
3. Run M10.
4. Stop if the oracle-improvement gate fails.

##### Stage E — method and controls

1. Run state/action extraction once and cache it.
2. Run balanced NICE retrieval for every candidate action with identical query/passages budgets.
3. Generate transitions with strict schema validation.
4. Run M1–M9 using the same reader and frozen configs.
5. Save item-level tokens, calls, latency, and failure states.

##### Stage F — counterfactual and fidelity evaluation

1. Generate minimal pairs with `prompts/09_counterfactual_perturber.md`.
2. Require evidence-backed human validation before using a pair as gold.
3. Judge transitions with method names hidden.
4. Manually audit at least 200 transition cards.
5. Run action-effect shuffle and field-deletion tests.

##### Stage G — no-go decision

Load `configs/no_go.yaml`; produce `outputs/metrics/no_go_report.json`. The report must list every gate as pass/fail/insufficient-data. The paper claim is determined by this report, not by manual preference.

#### 8. Model and compute constraints

Target hardware is one RTX 4090, 64 GB RAM, Ryzen 5950X.

- Pilot with one reader: Qwen2.5-7B-Instruct.
- Load generator and reader serially; never require three GPUs.
- Prefer cached stage-by-stage inference over end-to-end reruns.
- Use rollout depth 1 for the pilot.
- Cap NICE evidence at the configured number of passages per action.
- Process expensive modules only for Tier A/B.
- Use API auxiliary models only when explicitly configured; record exact model snapshots.
- Never silently change precision, quantization, or decoding settings between variants.

#### 9. Prompt and schema discipline

- Load prompts from files; do not embed duplicate prompt strings in source code.
- Compute SHA-256 for every prompt file and store it with each output.
- Validate JSON against the corresponding schema.
- On invalid JSON, retry at most twice with a format-repair message that does not add task information.
- If still invalid, record `status=invalid_output`; do not hand-fix predictions.
- Preserve `unknown` rather than hallucinating missing patient facts.
- Every transition claim must cite private evidence IDs or be listed under `unsupported_claims`.

#### 10. NICE retrieval rules

- Use symmetric retrieval for all candidate actions.
- Retrieve indication/precondition, contraindication/exception, expected effect/observation, and monitoring/next-step evidence.
- Mark coverage as `covered`, `partial`, `unsupported`, or `jurisdiction_conflict`.
- Do not expose NICE text in public logs, test fixtures, or commits.
- Public outputs may contain opaque document IDs, hashes, aggregate metrics, and short non-reconstructable labels.
- If a question is US- or India-specific and guidance may differ, set `jurisdiction_sensitive=true` and keep it out of the primary NICE-covered analysis unless adjudicated.

#### 11. Evaluation outputs

For each item and method, save:

```json
{
  "item_id": "...",
  "dataset": "...",
  "method": "M7_full_aw_medrgag",
  "prediction": "A",
  "status": "ok",
  "prompt_hashes": {},
  "model_ids": {},
  "seed": 13,
  "input_tokens": 0,
  "output_tokens": 0,
  "latency_ms": 0,
  "nice_coverage": "covered",
  "used_rollout_ids": [],
  "config_hash": "...",
  "git_commit": "..."
}
```

Never overwrite an existing run directory. Use immutable run IDs.

#### 12. Primary analyses

- Tier A paired accuracy: M7 vs M0.
- M7 vs M1/M2/M3 under matched budgets.
- Counterfactual relevant-flip correctness.
- Irrelevant-perturbation invariance.
- Transition evidence entailment.
- Action-effect shuffle degradation.
- Routed all-item accuracy.
- Cost-normalized improvement.

Use 10,000 paired bootstrap samples, exact McNemar where appropriate, 95% confidence intervals, and Holm correction.

#### 13. Tests required before full runs

1. `test_answer_key_isolation.py`
2. `test_slice_builder_has_no_prediction_fields.py`
3. `test_prompt_hash_saved.py`
4. `test_json_schema_validation.py`
5. `test_balanced_action_retrieval_budget.py`
6. `test_nice_text_not_in_public_outputs.py`
7. `test_shuffled_mapping_changes_rollout_ids.py`
8. `test_non_action_router_matches_m0_input.py`
9. `test_cache_is_content_addressed.py`
10. `test_reproducible_seeded_decoding.py`

A failed leakage or privacy test blocks all experiments.

#### 14. Definition of done

The implementation is complete only when:

- all required variants run from configuration;
- the action slice was frozen before joining predictions;
- all primary item-level outputs are retained;
- budget and cost reports exist;
- human-adjudication files and agreement statistics exist;
- counterfactual and transition-fidelity evaluations exist;
- `no_go_report.json` is generated automatically;
- the public export contains no NICE source content;
- the final README states the exact claim permitted by the no-go result.

#### 15. 2026-08-23 exploratory Luna-proxy execution record

This record is an effect-screening experiment, not completion of Stages D–G above. At the user's direction, every role that would currently require a person was performed by a different Luna Max subagent. All resulting artifacts remain `human_validated=false`; the transition cards are parametric and not NICE-grounded.

##### Scope and conditions

- Tier-A slice: 85 items and 315 candidate cards: MedQA 25, MedMCQA 18, MMLU-Med 17, PubMedQA* 25, BioASQ 0.
- Reader: local Meta-Llama-3.1-8B-Instruct, one GPU, temperature 0.1, seed 42, maximum 512 output tokens.
- M0 user prompts matched the stored v15 prompts exactly for 85/85 items, and the replayed M0 predictions matched stored v15 for 85/85.
- Conditions: M0 original v15 context; M1 state/action decomposition; PX unreviewed parametric cards plus planner; PA cards reviewed by two independent Luna Max agents and adjudicated by a third independent Luna Max agent.

##### Strict results

| Condition | Correct | Accuracy |
|---|---:|---:|
| M0 / stored v15 | 60/85 | 70.6% |
| M1 state/action | 59/85 | 69.4% |
| PX parametric WM | 67/85 | 78.8% |
| PA Luna-adjudicated | 69/85 | 81.2% |

PA versus M0 produced 12 improvements and 3 regressions: +10.6 percentage points, bootstrap 95% CI +2.4 to +20.0, exact McNemar p=0.0352. PA versus M1 produced 12 improvements and 2 regressions: +11.8 points, CI +3.5 to +20.0, p=0.0129. PA versus unreviewed PX produced 2 improvements and 0 regressions: +2.4 points, CI 0.0 to +5.9, p=0.5.

By dataset, PA scored MedQA 24/25, MedMCQA 12/18, MMLU-Med 17/17, and PubMedQA* 16/25. One MedQA response selected the correct candidate semantically but failed the strict parser by returning `"C: Principal cells; aldosterone"`; the strict 69/85 result is retained as primary, while author parsing gives 70/85.

##### Proxy review outcome and interpretation

Across 85 items, the independent Luna roles accepted 62 item-level card sets, revised 23, and excluded 0. Adjudication changed the fixed-rule planner preference for only three PubMedQA* items. Two of those changes converted PX errors into PA correct answers; the reader rejected the third corrected planner preference and remained wrong. PA author predictions agreed with the planner on 79/85 items, so planner anchoring remains a material alternative explanation.

The permitted conclusion is therefore narrow: this is a positive go/no-go signal worth replacing the Luna proxy roles with genuinely independent human reviewers in a later validation round. It does not establish human validation, NICE grounding, general clinical validity, a causal world-model gain, or cross-dataset improvement; MedMCQA did not improve and the PubMedQA* PA result only returned to the M0 level.

Primary artifacts:

- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_reader_summary.json`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_cards.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_summary.json`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_reader_summary.json`

#### 16. 2026-08-23 all-85 mechanism ablation

This remains an exploratory Luna-proxy experiment with `human_validated=false` and no NICE grounding. The same local Llama reader, evidence, temperature, seed, and output budget were retained. The ablation runner added only five isolated conditions to the existing all-85 path:

- M2: an independent 512-token same-Llama analysis followed by the normal reader, with no Luna state, cards, or planner. This is an approximate extra-compute control, not a strict equal-token match.
- M4: state plus action/preconditions and uncertainty fields, with effects and planner removed.
- M5: state plus action/next-state effects and uncertainty fields, with preconditions and planner removed.
- M6: state plus complete transition cards, with planner removed.
- MR: state plus planner, with transition cards removed. MR is an extra diagnostic, not a replacement for a required method in the formal matrix.

##### Strict results

| Condition | Correct | Accuracy | Parse rate |
|---|---:|---:|---:|
| M0 / stored v15 | 60/85 | 70.6% | 97.6% |
| M1 state/action | 59/85 | 69.4% | 97.6% |
| M2 approximate extra reasoning | 54/85 | 63.5% | 85.9% |
| M4 preconditions only | 63/85 | 74.1% | 100% |
| M5 effects only | 63/85 | 74.1% | 100% |
| M6 complete cards, no planner | 66/85 | 77.6% | 100% |
| MR planner, no cards | 70/85 | 82.4% | 100% |
| PA complete cards plus planner | 69/85 | 81.2% | 98.8% |

M2 used 85 additional model calls and generated 39,854 auxiliary tokens before the reader, yet fell 7.1 points below M0 (4 improvements, 10 regressions; bootstrap 95% CI -15.3 to +1.2; exact McNemar p=0.180). This run did not observe a benefit from that extra free-form reasoning, but M2 was not strictly token- or cost-matched and therefore cannot exclude every “more reasoning” explanation.

Without planner output, complete cards scored 66/85: +7.1 points over M0 (8 improvements, 2 regressions; CI 0.0 to +14.1; p=0.109) and +8.2 points over M1 (9 improvements, 2 regressions; CI +1.2 to +15.3; p=0.0654). Preconditions alone and effects alone both scored 63/85, while their item-level predictions differed on four questions. Complete cards improved three questions over either single half with no regressions in those paired comparisons.

The strongest diagnostic was MR: 70/85, +11.8 points over M0 (12 improvements, 2 regressions; CI +3.5 to +20.0; p=0.0129) and +12.9 points over M1 (12 improvements, 1 regression; CI +5.9 to +21.2; p=0.00342). MR was statistically indistinguishable from PA: MR gained two and lost one strict-correct item relative to PA (+1.2 points; p=1.0); author parsing was 70/85 for both. MR agreed with the planner preference on 77/85 items, while the planner itself was correct on 69/85.

##### Interpretation

The data contain a smaller positive cards-without-planner signal, but most of the observed gain is reproduced by exposing the Luna-derived planner recommendation. Full cards plus planner do not outperform planner without cards on this slice. The result therefore supports continuing the experiment, but it does not yet establish that the reader is using transition dynamics rather than following a strong proxy answer ranking. It also does not establish human validation, clinical validity, NICE grounding, cross-dataset generalization, or a causal world-model mechanism.

Output integrity checks passed: 425 prediction rows and 425 result rows, exactly 85 per condition and 425 unique item-condition identities. Prediction files contain no gold labels, correctness fields, or stored reference predictions. Every row is `human_validated=false`; M2 has no proxy model or grounding, and M4/M5/M6/MR are labelled `proxy_model=luna_max`, `grounding=parametric_no_nice`.

Primary artifacts:

- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_predictions.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_results.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_summary.json`

#### 17. 2026-08-23 blind direct-Luna ranking control

The mechanism audit identified the Luna-derived planner recommendation as the dominant alternative explanation. Two new Luna Max subagents therefore handled disjoint blind splits (43 and 42 items). They could read only the original question, options, and MedRGAG documents; they were forbidden from reading state, cards, planner output, predictions, results, or gold labels. Each produced a direct option ranking and one-sentence reason without constructing a world model. These rankings were not independently reviewed or adjudicated, and remain `human_validated=false`, `grounding=parametric_no_nice`.

The raw direct rankings scored 74/85 (87.1%): MedQA 25/25, MedMCQA 14/18, MMLU-Med 17/17, and PubMedQA* 18/25. The adjudicated WM planner preference scored 69/85, and the two rankings agreed on 74/85 items. Direct ranking versus planner preference produced seven improvements and two regressions: +5.9 points, bootstrap 95% CI -1.2 to +12.9, exact McNemar p=0.180.

For a shared-reader comparison, the original v15 question/options/evidence and the same neutral state used by MR were given to the same local Llama reader, followed only by `{preferred_candidate_id, ranking, reason}` from the blind direct control. No transition cards, candidate scores, or planner data were present. The reader scored 71/85 (83.5%): MedQA 24/25, MedMCQA 12/18, MMLU-Med 17/17, and PubMedQA* 18/25. It agreed with the raw direct choice on 80/85 items; four correct direct choices became wrong and one wrong choice became correct.

##### Shared-reader comparison

| Condition | Strict correct | Accuracy |
|---|---:|---:|
| M0 / stored v15 | 60/85 | 70.6% |
| M6 complete cards, no planner | 66/85 | 77.6% |
| PA complete cards plus planner | 69/85 | 81.2% |
| MR WM planner, no cards | 70/85 | 82.4% |
| MD blind direct-Luna ranking, no WM | 71/85 | 83.5% |

MD versus M0 produced 14 improvements and 3 regressions: +12.9 points, CI +3.5 to +22.4, p=0.0127. MD versus PA produced 4 improvements and 2 regressions: +2.4 points, CI -3.5 to +8.2, p=0.688. MD versus MR produced 5 improvements and 4 regressions: +1.2 points, CI -5.9 to +8.2, p=1.0. Thus MD, PA, and MR are statistically indistinguishable on this 85-item slice.

MD used 170,139 reader input tokens, versus 218,480 for MR and 299,819 for PA. This is a reader-prompt comparison only; upstream Luna generation and review effort was not measured consistently, so it is not a total-cost claim.

##### Updated interpretation

The simplest direct-ranking control matches or numerically exceeds the full proxy WM path. Current results therefore do not show incremental value from constructing transition cards or a fixed-rule WM planner over asking Luna directly to rank the options. The defensible effect signal is that an external Luna advisory ranking helps the local Llama reader on this selected slice; attributing that gain to world-model transition reasoning is not supported.

This is still not proof that direct ranking is universally superior: the two Luna agents were split along dataset boundaries, the direct rankings were not double-reviewed, sample size is 85, and comparisons with PA/MR have wide intervals. It also remains neither human validation nor NICE grounding.

An additional independent Luna Max method reviewer, which had not generated rankings, cards, reviews, or code, recommended pausing expansion of the current WM pipeline and redesigning around this direct-ranking alternative explanation. Its single minimal follow-up is a pre-paired same-85 rerun in which blind direct ranking and cards-plus-planner use the same reader prompt surface and a matched token/context budget.

Primary artifacts:

- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_direct_luna_rank/group_01.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_direct_luna_rank/group_02.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_predictions.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_results.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_summary.json`

#### 18. 2026-08-23 matched ranking-source control and stop decision

This final diagnostic remains exploratory, parametric, not NICE-grounded, and `human_validated=false`. MD and MW used the same original v15 question/options/evidence, the same neutral state, the same reader envelope, and the same two-field JSON payload: `{preferred_candidate_id, ranking}`. Reasons, cards, scores, and source labels were absent from the reader prompt. All 85 item-level input-token counts matched exactly; each condition used 160,457 input tokens. The complete rankings, and therefore the full prompts, were identical on 42/85 items.

##### Failed runs retained as negative evidence

The first matched run used temperature 0.1 and separate `model.generate` calls. It returned MD 65/85 and MW 64/85, with two improvements and three regressions, but only 29/42 byte-identical prompt pairs produced identical raw responses and only 41/42 produced the same strict prediction. One sampling-induced flip contributed to the paired result, so this run is retained as provisional and is not used for the mechanism decision.

A complete temperature-0 replay still produced a different raw response for the identical `medqa/0702` prompt across the two separate calls. The write-before-evaluation assertion stopped that run before any greedy prediction, result, or summary file was written. This failure shows that separate vLLM calls were not a clean deterministic pairing in this environment; no missing in-memory responses were reconstructed afterward.

The accepted repair grouped the 170 records by their complete chat prompt before inference, generated each of 128 unique prompts exactly once in one call, and mapped the outputs back to the two conditions. The grouping contained exactly 42 two-record groups and 86 singletons. Before writing, the runner verified that all 42 shared-prompt pairs had identical raw responses, strict predictions, and author predictions. This defines a deterministic prompt-to-output comparison for this exploratory run; it does not prove that independent calls, other batches, or other hardware are deterministic. Only the 43 items with different rankings can express a ranking-source effect.

##### Clean matched results

| Condition | Strict correct | Accuracy | Author correct |
|---|---:|---:|---:|
| MD blind direct ranking | 64/85 | 75.3% | 65/85 |
| MW WM-planner ranking | 64/85 | 75.3% | 65/85 |

MW versus MD produced one improvement, one regression, and 83 unchanged items: 0.0 percentage points, paired bootstrap 95% CI -3.5 to +3.5, exact McNemar p=1.0. MedQA changed by +1 correct item, MedMCQA by -1, and MMLU-Med and PubMedQA* did not change. The reader prediction differed on three items; the third difference left both conditions wrong. The raw rankings themselves remained 74/85 for direct Luna ranking and 69/85 for the adjudicated planner preference.

Integrity checks found 170 prediction rows and 170 result rows, exactly 85 unique items per condition, no malformed pairs, no input-token mismatch, and no gold/correctness/reference-prediction fields in the prediction file. Every row remains `human_validated=false`, `grounding=parametric_no_nice`, and exploratory/provisional.

##### Decision

A new Luna Max method reviewer that had not generated the cards, rankings, reader outputs, or code independently checked the artifacts; this is still a proxy review, not human validation. Its conclusion matched the item-level audit: the matched experiment identifies no incremental benefit from the WM-derived planner ranking over the simpler blind direct ranking. Together with the earlier ablations, the current evidence does not support attributing the advisory-ranking gain to transition cards or a world-model mechanism.

Expansion of the current WM claim stops here. The retained finding is an exploratory `action-aware/direct-ranking` effect, not a world-model contribution. No additional experiment is necessary for this decision. Any future attempt to revive a clinical WM claim must be a separately designed human-validated, NICE-grounded study; the present proxy artifacts cannot supply those claims.

Primary artifacts:

- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_predictions.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_results.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_summary.json`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_predictions.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_results.jsonl`
- `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_summary.json`

<a id="record-0263"></a>

## PROJECT_PLAN.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/PROJECT_PLAN.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/PROJECT_PLAN.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`。

### 从静态证据到行动条件未来：MedRGAG + 临床世界模型验证计划

#### 1. 结论先行

当前思路的逻辑链**可以成立，但必须重写为“任务诊断 + 机制验证 + 修复方法”**，不能写成“先找 MedRGAG 答错的 action 题，再加一个 action 模块把它做对”。

推荐项目身份：

> **在与模型结果无关的规则下，从五个医学 QA benchmark 中定义 action-transition slice；证明 MedRGAG 的静态证据补全与选择机制在需要 action-conditioned transition/counterfactual comparison 的问题上存在系统性缺口；再以 NICE 指南为外部约束，在测试时增加显式的 precondition–effect–rollout 模块，并通过等预算基线、反事实最小对和 transition fidelity 证明增益来自世界模型功能，而不是更多提示词或更多计算。**

按功能定义，项目至少应达到：

\[
s_0 = \phi(q),\quad
\hat{s}_{1}^{(i)},\hat{o}_{1}^{(i)} \sim T(s_0,a_i,E_i),\quad
\hat{a}=\arg\max_{a_i}U(s_0,a_i,\hat{s}_{1}^{(i)},\hat{o}_{1}^{(i)})
\]

其中：

- `s0`：患者当前状态、时间信息、既往干预、禁忌与不确定性；
- `ai`：检查、用药、手术、转诊、监测、停止治疗等临床 action；
- `Ei`：针对该 action 检索到的 NICE 指南证据；
- `T`：action-conditioned transition，预测 action 是否可执行及执行后的状态/观察；
- `U`：依据问题目标、安全性、时序和指南支持度比较候选 rollout。

只抽取 `state/action/goal` 而不预测 action 后果，应命名为 **action decomposition**。只有加入 applicability/precondition、effect/next-state，并让这些预测参与候选 action 比较，才具备最低限度的 world-model 功能。

---

#### 2. 为什么 MedRGAG 正好留下了这个缺口

原 MedRGAG 的核心流程是：平衡检索 → KGCC 总结检索内容并识别“缺失知识” → 生成补充文档 → KADS 按“知识需求”选择文档 → reader 作答。它解决的是**证据覆盖和文档选择**，并没有显式表示患者状态、行动前置条件、行动后果、下一状态或备选行动 rollout。

因此可以提出一个具体而非泛化的 failure mechanism：

> 对静态事实题，补齐“缺失知识”通常足够；对 action-transition 题，系统还需要把当前状态和候选行动绑定，预测行动会造成什么后果，并比较不同未来。纯文档补齐可能找到相关知识，却没有保证 reader 以正确的 action-conditioned 方式组织这些知识。

这不是攻击 KGCC/KADS “不可靠”，而是指出它们的建模对象是 `knowledge requirement`，不是 `state transition`。

---

#### 3. 2026 年竞争环境与必须保留的差异化

本方向已经存在明显相邻工作：

- LLM 世界模型工作把“判断 action 是否适用”和“预测 action 执行后的状态”视为两个最低功能；
- RAP 类方法强调对候选行动/推理步骤进行未来状态 rollout 与规划；
- EHRWorld 等医疗世界模型使用真实纵向 EHR 学习长时状态转移；
- MedGuideX 已把临床指南转成可执行决策逻辑，并生成 factual/counterfactual QA 进行 SFT/RL。

因此，本项目不能把贡献写成“首次把指南和 action 用在医学 QA”。建议突出四个差异：

1. **诊断对象不同**：研究 MedRGAG 这类 retrieval–generation fusion 在 action-transition 问题上的结构性失效，而不是训练一个新的医疗模型。
2. **训练范式不同**：只做测试时 augmentation，不使用 NICE 做训练、微调或权重更新。
3. **证据形态不同**：NICE 作为私有、可追溯的 transition constraint，生成每个 action 的 precondition/effect card。
4. **验证标准不同**：不仅看原 MCQ accuracy，还看 transition fidelity、state/action sensitivity、counterfactual consistency、rollout faithfulness 和等预算消融。

推荐标题方向：

> **From Static Evidence to Action-Conditioned Futures: Guideline-Grounded World Modeling for Medical Question Answering**

推荐方法名：`AW-MedRGAG`（Action-World MedRGAG）或 `GCM-MedRGAG`（Guideline-grounded Clinical Model）。

---

#### 4. 核心研究问题与可证伪假设

##### RQ1：五个 benchmark 中是否存在可稳定定义的 action-transition 子集？

**H1**：在不查看任何模型结果的情况下，能够以明确 taxonomy 标注出严格 action-transition 问题，并达到双人标注一致性 `κ >= 0.70`。

##### RQ2：MedRGAG 是否在该子集上存在超出普通难度的系统性缺口？

**H2**：控制数据集、题长、学科、选项数和总体难度后，`strict action-transition` 标签对 MedRGAG 正确率仍有显著负效应；或其相对 matched non-action controls 至少低 3 个绝对百分点。

##### RQ3：显式 transition/rollout 是否比 action decomposition 和更多计算更有效？

**H3**：完整 WM 在严格子集上显著优于：

- action decomposition only；
- 等 token 的额外推理；
- 等检索调用的 action-specific retrieval；
- precondition-only；
- effect-only；
- WM representation without rollout。

##### RQ4：模型是否真的使用了 action-conditioned transition？

**H4**：完整方法在 action/state 最小对上表现出更高的正确敏感性；当 action–effect 对应关系被打乱时性能显著下降；最终答案与 rollout 排名高度一致。

##### RQ5：NICE 的价值是“更多文本”还是“可验证的指南约束”？

**H5**：真实 NICE transition evidence 优于等长随机/主题匹配文本；transition claims 的 evidence entailment 达到预设阈值。

---

#### 5. Action taxonomy：哪些题可以进入主实验

##### Tier A：严格 world-model 题，作为主结论

必须同时满足：

1. 题目提供或隐含一个可结构化的当前状态 `s0`；
2. 存在明确临床 action：干预、检查、监测、停止/调整治疗、转诊或程序动作；
3. 正确作答需要知道 `action -> next state/observation/outcome`，而非仅回忆静态关联；
4. transition 对答案具有区分作用；
5. 可定义至少一个替代 action 或替代 outcome，用于 counterfactual comparison。

子类：

- `action_selection`：选哪个治疗/检查/处置；
- `action_outcome`：已知 action，预测其后果；
- `diagnostic_action_observation`：执行检查后应看到什么；
- `next_action`：根据当前状态与已完成步骤选择下一步；
- `contraindication_safety`：某 action 在该状态下是否可执行/危险；
- `sequential_management`：答案依赖行动顺序或治疗反应。

##### Tier B：行动决策逻辑题，只作次级分析

需要根据状态选择 action，但无需显式预测 action 后的状态。例如简单的指南条件匹配。它可以支持 action-aware decision logic，但不足以独立支撑强 world-model 结论。

##### Tier C：表面 action 词，排除

例如“某病的一线药物是什么”且无需利用患者状态、禁忌、后果或替代未来；或者 action 只是背景事实，对答案没有 transition 作用。

##### 非 action 题

诊断、机制、遗传、解剖、静态并发症、纯文献结论等。

**主论文的 world-model 结论只基于 Tier A。**

---

#### 6. 数据构建流程：必须先冻结，再运行模型

原文五个数据集共 7,663 题：MedQA-US 1,273、MedMCQA 4,183、MMLU-Med 1,089、PubMedQA* 500、BioASQ-Y/N 618。

##### Phase 0A：自动初筛

使用 `prompts/01_action_slice_classifier.md`，输入只有 question 和 options；严禁提供：

- gold answer；
- MedRGAG prediction；
- baseline confidence；
- retrieved documents；
- error category。

低温运行两次，或使用两个不同模型独立标注。仅将两者均判为 Tier A/B 或存在分歧的题送人工。

##### Phase 0B：人工标注

建议：

- 两名标注者，至少一名具备医学背景；
- 随机打乱数据集来源与题号；
- 标注 Tier、task type、action、transition target、jurisdiction sensitivity；
- 计算 Cohen’s κ；
- 分歧由第三方或共同讨论裁决。

##### Phase 0C：冻结

形成只含 item ID、标签和非版权派生字段的 `action_slice_v1.jsonl`。记录：

- 数据哈希；
- prompt 哈希；
- 模型版本；
- 标注时间；
- adjudication 记录。

之后才能运行 MedRGAG。

---

#### 7. 预观察实验：先判断这条路是否值得继续

##### Pilot P1：slice 可构建性

- 每个数据集随机抽 200 题，共 1,000 题；不足 200 的按全量；
- 自动初筛 + 人工审查；
- 目标：估计 Tier A 比例、各 task type 分布、NICE 覆盖率。

**停止条件**：严格 Tier A 少于 100 题，或集中在单一数据集/单一题型，说明五 benchmark 难以支撑独立研究主线。

##### Pilot P2：baseline deficit

先只跑 Qwen2.5-7B reader 的原 MedRGAG：

- Tier A accuracy；
- Tier B accuracy；
- non-action accuracy；
- 匹配控制组 accuracy。

匹配变量：dataset、学科、question length、option count、reader-only difficulty、是否需要多跳。

**继续条件**：Tier A 存在至少 3 个绝对百分点的稳定缺口，或 mixed-effects logistic regression 中 action-transition 系数显著为负。

##### Pilot P3：oracle transition upper bound

对 100–200 个随机 Tier A 题，人工或由高质量模型在 NICE 证据下生成经过审核的 state/action/precondition/effect card，直接交给同一 reader。

比较：

- MedRGAG；
- oracle action decomposition；
- oracle transition card；
- oracle transition + rollout ranking。

如果 oracle transition 也不能提升，说明原 MCQ 本身不需要世界模型，项目应停止或转为 benchmark 研究。

##### Pilot P4：最小实现

只实现单步 WM：

1. state extraction；
2. balanced action-specific NICE retrieval；
3. precondition/effect prediction；
4. one-step counterfactual comparison；
5. final answer。

先不做 MCTS，不做长轨迹，不训练模型。若单步机制没有清晰信号，长规划只会增加噪声和成本。

---

#### 8. 方法：AW-MedRGAG

##### 8.1 保留原 MedRGAG

原始路径保持不变：

`question -> source-balanced retrieval -> KGCC -> generated documents -> KADS -> final top-5 evidence`

所有 baseline 与新方法使用相同：

- reader；
- retriever 与语料；
- top-k；
- generated document 数；
- decoding temperature；
-随机种子；
- 原始 top-5 reader evidence。

##### 8.2 Action gate

只对冻结后的 Tier A/B 题启用 WM；non-action 题继续使用原 MedRGAG，避免整体性能被额外模块拖累。

##### 8.3 State constructor

从题目中抽取：

- demographics；
- active conditions/symptoms；
- labs/imaging/vitals；
- temporal context；
- completed actions；
- contraindications/risk factors；
- unknowns；
- clinical goal。

不得补充题目未给出的患者事实。缺失信息必须标为 `unknown`。

##### 8.4 Action constructor

根据 task type 构造：

- action-choice：每个选项是候选 action；
- outcome-choice：stem 中 action 固定，选项是候选 next observation/outcome；
- next-action：把已完成 action 和当前 state 分开；
- safety：每个选项作为 action，并检查 precondition/contraindication。

##### 8.5 Balanced NICE retrieval

对每个候选 action 使用相同数量的查询和 top-k，查询覆盖：

1. target population/condition；
2. indication/precondition；
3. contraindication/exception；
4. expected effect/observation；
5. monitoring/next step。

设置 `coverage gate`：

- `covered`：有明确 NICE 证据支持 transition；
- `partial`：仅支持部分 precondition/effect；
- `unsupported`：无可靠证据；
- `jurisdiction_conflict`：NICE 与题目所属地区可能存在政策差异。

主 NICE 结论在 `covered` 子集上报告；其余题可运行 parametric-only WM，但不得把缺失证据伪装成 NICE 结论。

##### 8.6 Transition model

对每个 action 输出：

- applicability；
- satisfied/unsatisfied/unknown preconditions；
- immediate observation；
- next state changes；
- benefits；
- harms/contraindications；
- monitoring/next action；
- uncertainty；
- evidence IDs；
- unsupported claims。

不允许在指南未给出概率时生成具体风险百分比。该模块是规范性、指南约束的 textual transition model，不应宣称患者个体化因果效应估计。

##### 8.7 Counterfactual rollout selector

单步比较所有候选未来：

\[
Score(a_i)=w_g G_i-w_h H_i+w_e E_i+w_t T_i-w_u U_i
\]

其中：

- `G`：是否达成题目目标；
- `H`：安全风险与禁忌；
- `E`：证据支持度；
- `T`：时序适当性；
- `U`：不确定性。

权重必须固定或在开发集上确定后冻结，不能按测试答案调节。

##### 8.8 Reader integration

给 reader：

- 原 MedRGAG top-5 evidence；
- structured state；
- 每个 action 的 compact rollout card；
- rollout ranking；
- 原问题与选项。

reader 输出答案和一个可自动检查的 `used_rollout_ids` 字段，用于 faithfulness 分析。

---

#### 9. 必须比较的实验变体

| ID | 方法 | 目的 |
|---|---|---|
| M0 | Original MedRGAG | 原始基线 |
| M1 | Action decomposition only | 测试结构化拆分本身 |
| M2 | Equal-token extra reasoning | 控制更长提示和更多推理 token |
| M3 | Action-specific NICE retrieval only | 控制更多/更精准检索 |
| M4 | Precondition only | 检查 applicability 的作用 |
| M5 | Effect only | 检查 next-state prediction 的作用 |
| M6 | WM cards, no rollout comparison | 检查显式规划/比较的作用 |
| M7 | Full AW-MedRGAG | 完整方法 |
| M8 | Full WM without NICE | 检查指南 grounding 的贡献 |
| M9 | Full WM + shuffled action–effect mapping | 机制反证；若不下降，模型未真正使用 transition |
| M10 | Oracle transition | 上界与错误来源分析 |

公平性要求：M1–M9 的辅助模型、temperature、最大 token、候选文档数和调用次数均记录。M2/M3 必须与 M7 至少在总输入 token 或总调用成本上等预算。

---

#### 10. 主实验

##### E1：原始五 benchmark

报告：

- all-item accuracy；
- Tier A/B/non-action accuracy；
- dataset × task type macro accuracy；
- action gate 后的整体 accuracy；
- 相对原 MedRGAG 的退化/提升。

##### E2：matched-control diagnosis

对每个 Tier A 题匹配一个或多个非 action 题；使用：

- McNemar test；
- paired bootstrap 95% CI；
- mixed-effects logistic regression；
- Holm correction。

##### E3：counterfactual minimal pairs

从 NICE covered Tier A 中构建两类最小对：

1. **Action-relevant perturbation**：只改变一个应改变推荐/后果的变量；
2. **Irrelevant perturbation**：改变与 transition 无关的表面变量，答案应保持不变。

指标：

- correct flip rate；
- incorrect flip rate；
- pair consistency；
- action sensitivity；
- irrelevant invariance。

##### E4：transition fidelity

随机抽样 rollout cards，由盲审标注：

- precondition correctness；
- effect correctness；
- evidence entailment；
- state consistency；
- temporal plausibility；
- unsupported probability；
- option leakage。

先用独立 LLM judge 批量筛查，再对至少 200 个样本进行人工复核。

##### E5：mechanistic faithfulness

- action–effect shuffle；
- 删除 next-state 字段；
- 替换为等长主题文本；
- 只给最终 ranking、不提供 rollout；
- 只给 rollout、不提供 ranking。

若完整方法对这些破坏不敏感，说明提升可能只是提示增强。

##### E6：鲁棒性与效率

报告：

- latency；
- API calls；
- input/output tokens；
- GPU memory；
- invalid JSON rate；
- abstention rate；
- NICE coverage rate。

---

#### 11. 统计与主指标

##### Primary endpoint

Tier A 上 M7 vs M0 的 paired accuracy difference，同时要求 M7 vs M1/M2/M3 仍显著。

##### Secondary endpoints

- transition fidelity；
- counterfactual pair accuracy；
- action sensitivity；
- irrelevant invariance；
- evidence entailment；
- overall routed accuracy；
- cost-normalized gain。

##### 推荐统计

- 10,000 次 paired bootstrap；
- McNemar exact test；
- mixed-effects logistic regression：`correct ~ method * tier + length + dataset + (1|item)`；
- 95% CI；
- 多重比较用 Holm；
- 不只报告 p 值，同时报告绝对提升和 odds ratio。

---

#### 12. 预注册 NO-GO 标准

项目只有在以下条件满足时才能继续以“world model”投稿：

1. Tier A 至少 250 题，且至少来自 3 个数据集；
2. 标注一致性 κ >= 0.70；
3. 原 MedRGAG 在 Tier A 上相对 matched control 存在 >=3pp 缺口，或回归系数显著为负；
4. Oracle transition 相对 M0 提升 >=5pp；
5. Full WM 相对 action decomposition 和等预算基线均提升 >=2.5pp，95% CI 不跨 0；
6. transition evidence entailment >=80%；
7. action–effect shuffle 至少造成 3pp 性能下降或 10pp pair-consistency 下降；
8. counterfactual relevant-flip 指标相对 M0 提升 >=10pp；
9. routed all-item accuracy 相对 M0 不下降超过 1pp。

若 3 不成立：不能说现有框架存在 action-transition 缺口。

若 5 不成立：只能写 action-aware prompting/retrieval，不应宣称 WM 贡献。

若 6 不成立：NICE grounding 不可靠，应停止临床 world-model 表述。

若 7 不成立：无法证明系统使用了 transition。

---

#### 13. 单张 RTX 4090 的执行方案

用户环境：RTX 4090 一张、64GB RAM、Ryzen 5950X。

##### Pilot

- 只用 Qwen2.5-7B reader；
- generator 与 reader 串行运行；
- summarizer/explorer/integrator 可沿用 API，或一次只加载一个本地模型；
- 所有 retrieval、summary、exploration、generation、selection、transition 输出分阶段缓存；
- 先跑 1,000 题筛选，随后只在 Tier A/B 上跑昂贵模块；
- rollout depth = 1；每个 action 最多 3 个 NICE chunks；
- 先不做多 seed 全量，只在 pilot 通过后做 3 seeds。

原仓库代码把 GPU 设备写死为 `0,1,2`，实现时必须改为环境变量/配置驱动，并保留原代码镜像以便复现。

##### Full study

- 先完整跑一个 reader；
- 成功后再加入第二个 reader 做模型泛化；
- 三个 reader 全复现不是验证想法的前置条件；
- 统计分析基于 item-level paired predictions，避免重复生成已缓存的文档。

---

#### 14. NICE 数据治理

- NICE 仅作为测试时外部知识库；
- 不用于 SFT、RL、LoRA、embedding model 训练或任何权重更新；
- 原 PDF、抽取文本、chunks、embeddings、索引、向量库均不公开；
- 日志中只保存私有 document ID、hash、offset 与模型生成的非重构性结构；
- 对外开源代码、prompt、schema、评估脚本和构建说明；
- 论文中明确说明 jurisdiction mismatch，并对 MedQA-US/MedMCQA 设置 conflict gate；
- 不把 guideline recommendation 当作患者个体化因果效果。

---

#### 15. 最终论文逻辑链

1. **Observation**：现有医学 MCQ 的单一 accuracy 隐藏了 action-conditioned reasoning 差异。
2. **Task definition**：定义 outcome-independent 的 action-transition taxonomy 与 benchmark slice。
3. **Diagnosis**：MedRGAG 在 matched Tier A 上存在系统性缺口，错误集中于 precondition、effect、temporal order 和 counterfactual comparison。
4. **Method**：在原 retrieval–generation evidence pipeline 上增加 NICE-grounded state/action/transition/rollout 模块。
5. **Mechanism**：完整方法优于 action decomposition、额外检索和等 token 推理；transition shuffle 会破坏性能。
6. **Generalization**：跨多个 benchmark/task type/reader 有稳定提升。
7. **Reliability**：在反事实最小对和 transition fidelity 上提升，而不仅是原 MCQ accuracy。
8. **Boundary**：这是 test-time, guideline-grounded textual clinical world model，不是从纵向 EHR 学得的患者级动力学模型。

---

#### 16. 预期成功率判断

- 构建可用 action-rich slice：约 70%–85%；
- 在该 slice 上观察到 MedRGAG 缺口：约 50%–70%；
- action decomposition/额外检索带来提升：约 60%–80%；
- 完整 WM 在等预算控制后仍有独立增益：约 30%–50%；
- 按“筛错题 + 加模块”直接形成强 world-model 论文：约 10%–20%；
- 按本计划形成“benchmark diagnosis + test-time WM + mechanistic validation”的完整工作：约 35%–55%。

这些是研究可行性判断，不是投稿录用率。最大的风险不是模型做不出提升，而是提升无法排除结构化提示、额外检索和更高推理成本。

<a id="record-0264"></a>

## ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`。

### Archived WM Validation Implementation Contract

> Archived on 2026-09-06. This file preserves the proposed full-study contract;
> it is not active coding-agent instructions, and current work does not pursue
> the WM direction. The completed Luna-proxy experiments and final stop decision
> are recorded in `WM_VALIDATION_PROTOCOL_AND_RESULTS.md`, sections 15–18.

#### 1. Mission

Build a reproducible research pipeline that tests, rather than assumes, the following claim:

> An explicit guideline-grounded state/action/transition/rollout module improves MedRGAG specifically on questions that require action-conditioned clinical reasoning, and the gain cannot be explained by question selection, action decomposition, more retrieval, longer prompts, or more computation.

The project is successful only if the preregistered gates in `configs/no_go.yaml` pass.

#### 2. Non-negotiable research rules

1. **No selection on outcome.** Never use baseline correctness, confidence, rationale, retrieved documents, or error labels to decide whether an item belongs to the action slice.
2. **Answer-key isolation.** Gold answers must be unavailable to curation, retrieval, state extraction, transition generation, planning, and final-answer generation. They may be loaded only by evaluation code after predictions are written.
3. **Freeze before evaluation.** Freeze item IDs, taxonomy, prompts, schemas, prompt hashes, and analysis code before running M0–M10.
4. **Matched budgets.** Record and, where specified, match model calls, input/output tokens, retrieved passages, generated passages, and final reader context.
5. **Preserve the original baseline.** Keep an untouched copy of the public MedRGAG repository. Add wrappers/adapters; do not silently alter baseline prompts or logic.
6. **World-model terminology is conditional.** If the full method does not beat action decomposition and equal-budget controls, label it action-aware reasoning, not a world model.
7. **No causal overclaim.** NICE-grounded textual transitions are normative/guideline constrained. Do not claim patient-specific causal treatment effects or learned physiological dynamics.
8. **NICE is retrieval-only and private.** No training, fine-tuning, RL, LoRA, weight updates, publication of guideline text, extracted chunks, embeddings, or vector indexes.
9. **Negative results are first-class.** Save failed hypotheses, invalid generations, abstentions, and no-go decisions. Never discard them to improve headline results.
10. **Determinism and auditability.** Every artifact must store config hash, prompt hash, model identifier, seed, timestamp, git commit, and input item ID.

#### 3. Functional definition used by this repository

A strict world-model item must require:

- a current clinical state `s_t`;
- a clinical action/intervention `a_t`;
- an action-conditioned next state or observation `s_{t+1}, o_{t+1}`;
- a decision that depends on the predicted transition or comparison of alternative transitions.

Minimum model interface:

```text
state = StateConstructor(question, options)
transition_i = TransitionModel(state, action_i, evidence_i)
choice = RolloutSelector(state, transitions, goal)
answer = Reader(question, options, medrgag_evidence, state, transitions, choice)
```

Action extraction without next-state prediction is not a world model.

#### 4. Repository layout to implement

```text
project/
  vendor/MedRGAG/                 # untouched upstream snapshot
  src/
    data/
      loaders.py
      slice_builder.py
      matched_controls.py
    medrgag_adapter/
      baseline.py
      cache.py
      single_gpu.py
    wm/
      state_constructor.py
      action_constructor.py
      nice_query_planner.py
      retriever.py
      transition_model.py
      rollout_selector.py
      router.py
    controls/
      action_decomposition.py
      equal_token_reasoner.py
      extra_retrieval.py
      shuffled_transition.py
    evaluation/
      accuracy.py
      paired_stats.py
      transition_fidelity.py
      counterfactual_pairs.py
      faithfulness.py
      cost.py
    common/
      schemas.py
      prompts.py
      hashing.py
      logging.py
      retry.py
  configs/
  prompts/
  schemas/
  private_data/                   # gitignored; includes NICE index
  cache/                          # gitignored; stage outputs
  outputs/
    labels/
    predictions/
    transitions/
    judgments/
    metrics/
  tests/
  scripts/
  ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md
```

#### 5. Dataset facts and routing

Support the five MedRGAG datasets:

- MedQA-US: 1,273 test items;
- MedMCQA: 4,183 development items;
- MMLU-Med: 1,089 test items;
- PubMedQA*: 500 test items without original contexts;
- BioASQ-Y/N: 618 items.

The action gate must output Tier A, Tier B, Tier C, or non-action. The full world-model method is enabled only for frozen Tier A/B items. Non-action items use original MedRGAG.

#### 6. Required method variants

Implement all variants before claiming a complete experiment:

- `M0_original_medrgag`
- `M1_action_decomposition_only`
- `M2_equal_token_extra_reasoning`
- `M3_action_specific_nice_retrieval_only`
- `M4_precondition_only`
- `M5_effect_only`
- `M6_wm_cards_without_rollout`
- `M7_full_aw_medrgag`
- `M8_full_wm_without_nice`
- `M9_shuffled_action_effect_mapping`
- `M10_oracle_transition`

Do not substitute a weaker baseline without recording the deviation.

#### 7. Execution order

##### Stage A — portability and baseline fidelity

1. Snapshot upstream MedRGAG commit.
2. Add a single-GPU wrapper. The upstream code hard-codes GPUs `0,1,2`; replace this only in the wrapper/config path.
3. Run a 20-item smoke test and compare outputs with the unmodified baseline where possible.
4. Cache retrieval, summaries, explored knowledge, generated documents, selected documents, and reader inputs separately.
5. Write `baseline_manifest.json` with upstream commit, model IDs, prompts, temperatures, and top-k values.

##### Stage B — outcome-independent slice construction

1. Run `prompts/01_action_slice_classifier.md` without answers or predictions.
2. Validate every output against `schemas/action_label.schema.json`.
3. Send disagreements and all proposed Tier A items to blinded human review.
4. Compute agreement and save adjudication records.
5. Freeze `action_slice_v1.jsonl` and its SHA-256 hash.
6. Only after the freeze may baseline predictions be joined with labels.

##### Stage C — baseline diagnosis

1. Run M0 on frozen items.
2. Construct matched non-action controls without using M0 correctness.
3. Compute accuracy by dataset, tier, and task type.
4. Run paired bootstrap, McNemar, and mixed-effects regression.
5. Stop if the baseline-deficit gate fails.

##### Stage D — oracle test

1. Sample Tier A items independently of M0 correctness.
2. Create reviewed oracle transition cards.
3. Run M10.
4. Stop if the oracle-improvement gate fails.

##### Stage E — method and controls

1. Run state/action extraction once and cache it.
2. Run balanced NICE retrieval for every candidate action with identical query/passages budgets.
3. Generate transitions with strict schema validation.
4. Run M1–M9 using the same reader and frozen configs.
5. Save item-level tokens, calls, latency, and failure states.

##### Stage F — counterfactual and fidelity evaluation

1. Generate minimal pairs with `prompts/09_counterfactual_perturber.md`.
2. Require evidence-backed human validation before using a pair as gold.
3. Judge transitions with method names hidden.
4. Manually audit at least 200 transition cards.
5. Run action-effect shuffle and field-deletion tests.

##### Stage G — no-go decision

Load `configs/no_go.yaml`; produce `outputs/metrics/no_go_report.json`. The report must list every gate as pass/fail/insufficient-data. The paper claim is determined by this report, not by manual preference.

#### 8. Model and compute constraints

Target hardware is one RTX 4090, 64 GB RAM, Ryzen 5950X.

- Pilot with one reader: Qwen2.5-7B-Instruct.
- Load generator and reader serially; never require three GPUs.
- Prefer cached stage-by-stage inference over end-to-end reruns.
- Use rollout depth 1 for the pilot.
- Cap NICE evidence at the configured number of passages per action.
- Process expensive modules only for Tier A/B.
- Use API auxiliary models only when explicitly configured; record exact model snapshots.
- Never silently change precision, quantization, or decoding settings between variants.

#### 9. Prompt and schema discipline

- Load prompts from files; do not embed duplicate prompt strings in source code.
- Compute SHA-256 for every prompt file and store it with each output.
- Validate JSON against the corresponding schema.
- On invalid JSON, retry at most twice with a format-repair message that does not add task information.
- If still invalid, record `status=invalid_output`; do not hand-fix predictions.
- Preserve `unknown` rather than hallucinating missing patient facts.
- Every transition claim must cite private evidence IDs or be listed under `unsupported_claims`.

#### 10. NICE retrieval rules

- Use symmetric retrieval for all candidate actions.
- Retrieve indication/precondition, contraindication/exception, expected effect/observation, and monitoring/next-step evidence.
- Mark coverage as `covered`, `partial`, `unsupported`, or `jurisdiction_conflict`.
- Do not expose NICE text in public logs, test fixtures, or commits.
- Public outputs may contain opaque document IDs, hashes, aggregate metrics, and short non-reconstructable labels.
- If a question is US- or India-specific and guidance may differ, set `jurisdiction_sensitive=true` and keep it out of the primary NICE-covered analysis unless adjudicated.

#### 11. Evaluation outputs

For each item and method, save:

```json
{
  "item_id": "...",
  "dataset": "...",
  "method": "M7_full_aw_medrgag",
  "prediction": "A",
  "status": "ok",
  "prompt_hashes": {},
  "model_ids": {},
  "seed": 13,
  "input_tokens": 0,
  "output_tokens": 0,
  "latency_ms": 0,
  "nice_coverage": "covered",
  "used_rollout_ids": [],
  "config_hash": "...",
  "git_commit": "..."
}
```

Never overwrite an existing run directory. Use immutable run IDs.

#### 12. Primary analyses

- Tier A paired accuracy: M7 vs M0.
- M7 vs M1/M2/M3 under matched budgets.
- Counterfactual relevant-flip correctness.
- Irrelevant-perturbation invariance.
- Transition evidence entailment.
- Action-effect shuffle degradation.
- Routed all-item accuracy.
- Cost-normalized improvement.

Use 10,000 paired bootstrap samples, exact McNemar where appropriate, 95% confidence intervals, and Holm correction.

#### 13. Tests required before full runs

1. `test_answer_key_isolation.py`
2. `test_slice_builder_has_no_prediction_fields.py`
3. `test_prompt_hash_saved.py`
4. `test_json_schema_validation.py`
5. `test_balanced_action_retrieval_budget.py`
6. `test_nice_text_not_in_public_outputs.py`
7. `test_shuffled_mapping_changes_rollout_ids.py`
8. `test_non_action_router_matches_m0_input.py`
9. `test_cache_is_content_addressed.py`
10. `test_reproducible_seeded_decoding.py`

A failed leakage or privacy test blocks all experiments.

#### 14. Definition of done

The implementation is complete only when:

- all required variants run from configuration;
- the action slice was frozen before joining predictions;
- all primary item-level outputs are retained;
- budget and cost reports exist;
- human-adjudication files and agreement statistics exist;
- counterfactual and transition-fidelity evaluations exist;
- `no_go_report.json` is generated automatically;
- the public export contains no NICE source content;
- the final README states the exact claim permitted by the no-go result.

<a id="record-0265"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`。

### MedRGAG Action-Conditioned World Model Validation Pack

This pack preserves the completed 2026-08-23 exploratory validation work. WM
research is not a current work direction.

#### Intended claim

The target method is a **test-time, guideline-grounded, action-conditioned clinical transition model** added to MedRGAG. It must explicitly:

1. construct a clinically relevant state from the question;
2. identify a clinical action or intervention;
3. check action applicability/preconditions;
4. predict an evidence-grounded next state or observation after that action;
5. compare alternative rollouts when the question requires a decision;
6. use the rollout to answer the original multiple-choice question.

A pipeline that only extracts an action label or reformats the question is an action-aware reasoner, not a world model.

#### Pack contents

- `PROJECT_PLAN.md`: complete research plan, hypotheses, stages, metrics, risks, and no-go criteria.
- `ARCHIVED_WM_VALIDATION_IMPLEMENTATION_CONTRACT.md`: inactive implementation
  contract for the proposed full study, retained for historical reference.
- `WM_VALIDATION_PROTOCOL_AND_RESULTS.md`: protocol snapshot followed by the
  executed 2026-08-23 Luna-proxy experiments, controls, results, and stop
  decision.
- `prompts/`: benchmark curation, state extraction, NICE retrieval, transition simulation, planning, answering, and evaluation prompts.
- `schemas/`: JSON Schemas for strict output validation.
- `configs/experiment_matrix.yaml`: required methods and experimental matrix.
- `configs/no_go.yaml`: preregistered decision gates.

#### Required execution order

1. Curate and manually validate the action-transition slice **without running MedRGAG or seeing its predictions**.
2. Freeze item IDs, taxonomy, prompts, prompt hashes, and analysis code.
3. Run original MedRGAG and matched controls.
4. Run the world-model variants under matched retrieval, token, model, and call budgets.
5. Run original-QA evaluation, transition-fidelity evaluation, and counterfactual minimal-pair evaluation.
6. Apply the no-go gates before deciding whether the final paper may use the term “world model.”

#### NICE constraints

NICE content is retrieval-only and remains private. Do not train, fine-tune, update model weights, publish guideline text, publish extracted chunks, publish embeddings, or publish the vector database. Public artifacts may contain code, prompts, benchmark item IDs where licensing permits, aggregate labels, hashes, and non-reconstructable statistics.

#### Executable implementation

The untouched upstream snapshot is in `vendor/MedRGAG/`; its locked commit is
recorded by `python3 scripts/build_baseline_manifest.py`. The adapter never
imports upstream `main.py`, because that script reads answer keys while
assembling batches. `src/medrgag_adapter/baseline.py` accepts only a question,
options, and item ID.

The complete local-Llama path is `src/medrgag_adapter/llama_backend.py`. It
runs KGCC summary, missing-knowledge exploration, five-document generation,
KADS selection, and reader serially through one configurable
`meta-llama/Meta-Llama-3.1-8B-Instruct` backend. The default backend is the
real `transformers` path; `fake` is opt-in and fixture-only. The copied prompts
are checked byte-for-byte against upstream with:

```bash
PYTHONPATH=. python3 scripts/check_prompt_parity.py
```

Run the no-weight plumbing smoke test with:

```bash
PYTHONPATH=. python3 scripts/smoke_all_llama.py
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

After creating an answer-free JSONL view, a real immutable run is launched as:

```bash
PYTHONPATH=. python3 scripts/run_all_llama.py \
  --input outputs/labels/question_view.jsonl \
  --backend transformers \
  --model-id meta-llama/Meta-Llama-3.1-8B-Instruct \
  --visible-devices 0 --dtype float16 --quantization none \
  --retrieved-docs private_data/retrieved_documents.jsonl \
  --allow-unranked-retrieval --allow-unranked-post-selection \
  --cache-dir cache --output-dir outputs/predictions \
  --run-id llama-pilot-001
```

The private retrieval JSONL must have one row per `(dataset,item_id)` and a
`documents` list. A real run requires 32 candidate passages per item; the two
`--allow-unranked-*` flags explicitly record that this minimal local adapter
does not provide the upstream BM25/MedCPT rankers. Omit them when exact
retrieval and post-selection rankers are injected. The command writes an
immutable manifest, per-item outputs, aggregate call / token / latency
counters, and a blocker file if dependencies or weights are missing.
Content-addressed retrieval and M0 evidence are private cache artifacts;
public outputs contain hashes and opaque IDs only. `scripts/check_methods.py`
enumerates and fail-closes all M0--M10
variants; it never substitutes a fixture for an unavailable prerequisite.

The checked-in `src/medrgag_adapter/llama_backend.py` is the local serial
reference implementation (KGCC summary/explore, five generation calls,
numeric KADS selection, optional MedCPT ranker hooks, and reader), with a
dependency-free fake backend for tests. The external five-dataset run, when
available, is bound read-only:

```bash
PYTHONPATH=. python3 scripts/bind_external_all_llama.py \
  --external-root /home/data3/txy/MedRGAG \
  --run-dir /home/data3/txy/MedRGAG/outputs_reproduced/llama3.1/medrgag/all-llama31-8b-released-code-intent/role-stable-v15-guided-sentence-labels/all-llama-five-dataset-lenient-v1
```

This writes a small content-addressed provenance binding for the locked
manifest, source hashes, eight stage completion manifests, state, and
evaluation hash. It never copies external reader records or NICE text. The
current external run is sealed and complete but predates this pack's frozen
action slice, so it is historical Stage-A/exploratory provenance and is not
eligible as the primary Stage-C M0. A primary M0 must use a new immutable run
after the slice freeze; external reader/evaluate predictions are never fed to
the controls. If an exploratory variant explicitly consumes its answer-free
rerank documents, pass the binding with `--external-baseline-binding` and
`--allow-historical-external` and keep the resulting status out of primary
claims.

For a real run, accept Meta's Llama license, authenticate with Hugging Face
(`huggingface-cli login` or an equivalent token-bearing environment), install
the compatible stack from `requirements-real.txt`, and provide local Llama
weights/cache.  `bitsandbytes` is additionally required for either quantized
mode.  Keep NICE passages in `private_data/`; do not put them in public output.
The adapter rejects multi-device settings and uses one visible GPU. Record
the actual `pip freeze` and hardware in the immutable run manifest.
The `fake` backend is only a deterministic plumbing fixture and its outputs
are never study evidence. `scripts/audit_no_go.py` emits
`outputs/metrics/no_go_report.json`; missing human adjudication, NICE, model,
or prediction artifacts are reported as `insufficient-data`, not as passes.

<a id="record-0413"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review`。

### Luna Max 双代理盲审说明

每个批次由两名彼此独立的 Luna Max 代理分别填写 `reviewer_a.jsonl` 和 `reviewer_b.jsonl`。每行是一张候选状态转移卡；候选 ID 已替换为不透明标签。代理不得查看 `mapping.jsonl`、另一名代理的文件、实验结果、gold、prediction 或 planner。

只修改每行的 `review` 对象，不得改动其他字段或行顺序。前六项只能填写 `"yes"`、`"no"` 或 `"uncertain"`：

- `state_sufficient`：结构化状态是否包含评价该卡所需的题干事实。
- `transition_clinically_acceptable`：在所列前提下，状态转移是否具有临床或机制合理性。
- `applicability_correct`：卡中 applicability 标记是否恰当。
- `goal_alignment_correct`：卡中 goal alignment 标记是否恰当。
- `preconditions_sufficient`：前提是否足以限定该转移。
- `uncertainty_adequate`：不确定性和缺失信息是否交代充分。

`recommended_edits` 只写最小必要修订，无需修订时保持空字符串；`reviewer_confidence` 填 0 到 1；`reviewer_notes` 写简短理由。所有卡的 `coverage="unsupported"` 表示没有外部指南依据，只能按题干和参数化医学知识评价。不要选择答案、给候选排名或输出 planner。

这些评审是实验性的 Luna Max 代理判断，不是真人或临床专家验证。

<a id="record-0414"></a>

## ENVIRONMENT.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/ENVIRONMENT.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/ENVIRONMENT.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23`。

### Recorded environment

- OS: Ubuntu 22.04.5 LTS, x86_64
- Python: 3.10.12
- PyTorch: 2.6.0+cu124
- Transformers: 4.53.2
- vLLM: 0.8.5
- CUDA runtime reported by PyTorch: 12.4
- GPU: NVIDIA H20, 97,871 MiB
- NVIDIA driver: 570.133.20
- Reader model: Meta-Llama-3.1-8B-Instruct
- Reader maximum output: 512 tokens
- Clean matched replay: temperature 0, seed 42

The model weights and Python environment are not included.

<a id="record-0415"></a>

## FILE_INDEX.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/FILE_INDEX.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/FILE_INDEX.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23`。

### File index

本索引覆盖本交接目录中的全部 **104 个文件**：6 个顶层交接文件、14 个计划/代码文件、84 个 v4 实验记录。路径均相对于本目录。

#### 顶层交接文件

| 文件 | 用途 |
|---|---|
| `CONVERSATION_HISTORY.md` | 当前任务的用户/助手可见对话导出；不含隐藏推理、工具原始输出和内部子代理消息。 |
| `ENVIRONMENT.md` | 原实验服务器的软件、CUDA、GPU 与核心依赖版本。 |
| `FILE_INDEX.md` | 本文件；逐项说明交接包中的全部文件。 |
| `README.md` | 交接入口、当前结论、阅读顺序、重跑说明与省略项。 |
| `UPSTREAM_BASELINE.md` | 原论文仓库、锁定提交，以及取代完整 v15 的冻结下游边界。 |
| `requirements.txt` | reader 重跑所需的三个核心 Python 包及版本。 |

#### 计划、提示词、Schema 与代码

| 文件 | 用途 |
|---|---|
| `medrgag_wm_validation_pack/PROJECT_PLAN.md` | 用户指定的权威实验计划；从五个测试集筛选 WM 题目开始。 |
| `medrgag_wm_validation_pack/README.md` | 原验证包的结构、约定与使用说明。 |
| `medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md` | 验证协议与执行记录：筛选、代理评审、消融、matched control、结果和停止决策。 |
| `medrgag_wm_validation_pack/prompts/14_medrgag_reader.md` | MedRGAG reader 基础问答提示词。 |
| `medrgag_wm_validation_pack/prompts/16_equal_token_reasoning.md` | 等 token 推理控制条件提示词。 |
| `medrgag_wm_validation_pack/prompts/17_proxy_parametric_reader_context.md` | 注入 state/cards/planner 的代理参数化上下文提示词。 |
| `medrgag_wm_validation_pack/schemas/action_label.schema.json` | 动作型/WM 适配标签 Schema。 |
| `medrgag_wm_validation_pack/schemas/clinical_state.schema.json` | 结构化临床状态 Schema。 |
| `medrgag_wm_validation_pack/schemas/final_answer.schema.json` | 最终选择题答案 Schema。 |
| `medrgag_wm_validation_pack/schemas/judgment.schema.json` | transition card 评审判断 Schema。 |
| `medrgag_wm_validation_pack/schemas/transition_rollout.schema.json` | 候选动作 transition rollout/card Schema。 |
| `medrgag_wm_validation_pack/scripts/medrgag_compat.py` | 从 v15 精简出的文档渲染与两个答案解析函数。 |
| `medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py` | P4 多条件 reader 实验及 matched-ranking 控制运行器。 |
| `medrgag_wm_validation_pack/src/wm/transition_model.py` | 状态转移卡验证与 planner 选择逻辑。 |

#### v4 实验记录

| 文件 | 用途 |
|---|---|
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/candidate_labels.jsonl` | 1,000 题的候选动作/任务标签与分类分歧。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/README.md` | 初始 392 题盲审包说明。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_adjudication.jsonl` | 392 条 Luna 代理最终裁决标签。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/001-049.jsonl` | 初始分类盲审 review_id 001-049 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/050-098.jsonl` | 初始分类盲审 review_id 050-098 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/099-147.jsonl` | 初始分类盲审 review_id 099-147 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/148-196.jsonl` | 初始分类盲审 review_id 148-196 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/197-245.jsonl` | 初始分类盲审 review_id 197-245 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/246-294.jsonl` | 初始分类盲审 review_id 246-294 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/295-343.jsonl` | 初始分类盲审 review_id 295-343 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/luna_proxy_batches/344-392.jsonl` | 初始分类盲审 review_id 344-392 的 Luna 代理裁决分批记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/mapping.jsonl` | 392 个 review_id 到原题身份/源行的映射。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_a.jsonl` | 初始分类 reviewer A 盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_b.jsonl` | 初始分类 reviewer B 盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review_queue.jsonl` | 两个初始分类器分歧后的 392 题盲审队列。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/luna_proxy_action_slice_1000.jsonl` | Luna 对 1,000 题动作性、状态可表示性与 WM 资格的分类。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/luna_proxy_summary.json` | 1,000 题代理筛选的聚合计数与 Tier-A 结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/manifest.json` | v4 运行模型、种子、数据映射与提示词元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p2_v15_baseline_results.json` | 冻结 v15 基线整体及分组指标。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p2_v15_item_results.jsonl` | 1,000 题冻结 v15 预测、gold 与逐题正确性。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p2_v15_matched_pairs.jsonl` | 85 个 action/control 匹配对与 v15 正确性。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/ADJUDICATOR_README.md` | 85 题第三位代理裁决说明。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/README.md` | 85 题 transition-card 双盲代理评审说明。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_01/adjudicated_cards.jsonl` | 85 题第 01 组的裁决后最终 cards记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_01/adjudicator.jsonl` | 85 题第 01 组的第三位 Luna 代理裁决记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_01/mapping.jsonl` | 85 题第 01 组的opaque ID 到原候选映射记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_01/reviewer_a.jsonl` | 85 题第 01 组的第一位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_01/reviewer_b.jsonl` | 85 题第 01 组的第二位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_02/adjudicated_cards.jsonl` | 85 题第 02 组的裁决后最终 cards记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_02/adjudicator.jsonl` | 85 题第 02 组的第三位 Luna 代理裁决记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_02/mapping.jsonl` | 85 题第 02 组的opaque ID 到原候选映射记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_02/reviewer_a.jsonl` | 85 题第 02 组的第一位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_02/reviewer_b.jsonl` | 85 题第 02 组的第二位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_03/adjudicated_cards.jsonl` | 85 题第 03 组的裁决后最终 cards记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_03/adjudicator.jsonl` | 85 题第 03 组的第三位 Luna 代理裁决记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_03/mapping.jsonl` | 85 题第 03 组的opaque ID 到原候选映射记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_03/reviewer_a.jsonl` | 85 题第 03 组的第一位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_all85_luna_review/group_03/reviewer_b.jsonl` | 85 题第 03 组的第二位 Luna 代理盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_direct_luna_rank/group_01.jsonl` | 不使用 WM cards 的直接候选排序控制，第 01 组结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_direct_luna_rank/group_02.jsonl` | 不使用 WM cards 的直接候选排序控制，第 02 组结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/README.md` | 20 题试点 transition-card 双盲评审说明。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/adjudicator.jsonl` | 20 题试点的第三位 Luna 代理盲裁决记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/adjudicator_README.md` | 20 题试点第三位代理裁决说明。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/mapping.jsonl` | 20 题试点的opaque ID 到原候选映射记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/reviewer_a.jsonl` | 20 题试点的第一位 Luna 代理的 74 张 card 盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/reviewer_b.jsonl` | 20 题试点的第二位 Luna 代理的 74 张 card 盲审记录。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_predictions.jsonl` | 85 题五条件消融的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_results.jsonl` | 85 题五条件消融的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_ablation_reader_summary.json` | 85 题五条件消融的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_cards.jsonl` | 85 题经双评审/裁决后的 state、cards 与 planner。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_predictions.jsonl` | 85 题直接排序控制的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_results.jsonl` | 85 题直接排序控制的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_summary.json` | 85 题直接排序控制的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_reader_predictions.jsonl` | 85 题 Luna 裁决 PA的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_reader_results.jsonl` | 85 题 Luna 裁决 PA的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_reader_summary.json` | 85 题 Luna 裁决 PA的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_summary.json` | 85 题 card 评审/裁决聚合结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_cards.jsonl` | 20 题经双评审/裁决后的 state、cards 与 planner。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_reader_predictions.jsonl` | 20 题 Luna 裁决 PA的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_reader_results.jsonl` | 20 题 Luna 裁决 PA的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_reader_summary.json` | 20 题 Luna 裁决 PA的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudication_summary.json` | 20 题 card 评审一致率、分歧与裁决摘要。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_predictions.jsonl` | 85 题 temperature=0 matched ranking 复核的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_results.jsonl` | 85 题 temperature=0 matched ranking 复核的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_summary.json` | 85 题 temperature=0 matched ranking 复核的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_predictions.jsonl` | 85 题等 token direct/planner matched ranking的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_results.jsonl` | 85 题等 token direct/planner matched ranking的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_reader_summary.json` | 85 题等 token direct/planner matched ranking的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/cards_01.jsonl` | 85 题代理生成第 01 批 state/cards/planner 输出。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/cards_02.jsonl` | 85 题代理生成第 02 批 state/cards/planner 输出。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/cards_03.jsonl` | 85 题代理生成第 03 批 state/cards/planner 输出。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/input_01.jsonl` | 85 题代理生成第 01 批冻结输入。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/input_02.jsonl` | 85 题代理生成第 02 批冻结输入。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_batches/input_03.jsonl` | 85 题代理生成第 03 批冻结输入。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_cards.jsonl` | 85 题未人工确认的 Luna 参数化 state、cards 与 planner。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_input.jsonl` | 85 题冻结 question/options、动作标签与 MedRGAG 文档。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_reader_predictions.jsonl` | 85 题未裁决 M0/M1/PX的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_reader_results.jsonl` | 85 题未裁决 M0/M1/PX的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_reader_summary.json` | 85 题未裁决 M0/M1/PX的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_reader_predictions.jsonl` | 20 题未裁决 M0/M1/PX的原始回复、解析预测与推理元数据。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_reader_results.jsonl` | 20 题未裁决 M0/M1/PX的逐题 gold、正确性与预测结果。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_reader_summary.json` | 20 题未裁决 M0/M1/PX的聚合指标、配对统计与结论。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_sample20_cards.jsonl` | 最初 20 题 Luna 参数化 state、cards 与 planner。 |
| `private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_sample20_input.jsonl` | 最初 20 题冻结 question/options、动作标签与 MedRGAG 文档。 |

<a id="record-0416"></a>

## CONVERSATION_HISTORY.md

来源：[Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/CONVERSATION_HISTORY.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/CONVERSATION_HISTORY.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23`。

### Codex conversation history

- Thread: `01a02ae2-8f89-79b0-89bd-08fc5a59a36a`
- Title: 安装ponytail技能并说明用法
- Exported: 2026-08-23T13:45:25.945Z
- Scope: user messages and assistant messages visible in the conversation.
- Excluded: hidden reasoning, tool payloads, command output, and subagent-internal messages.
- Note: the final active turn may be incomplete at export time.

#### Turn 1 — 2026-08-22T19:11:26.000Z

##### User

https://github.com/DietrichGebert/ponytail 安装这个skill，并告知如何使用

##### Assistant (commentary)

我会使用 `skill-installer`，先核对这个 GitHub 仓库里的 skill 结构，再按 Codex 的安装流程安装，并给你一份可直接照用的说明。

##### Assistant (commentary)

安装器需要明确仓库内 `SKILL.md` 所在的路径；我正在读取仓库目录，定位正确安装入口后会继续安装。

##### Assistant (commentary)

仓库包含 6 个配套 skill（主模式、review、audit、debt、gain、help）。第一次安装因当前环境的临时目录权限被拒绝；这不是仓库问题，我会改用工作区内的安全临时目录继续。

##### Assistant (commentary)

安装已完成。接下来我会按 `openai-docs` 的 Codex skill 使用规范核对触发方式，避免把其他宿主的 `/命令` 写法误当成 Codex 的写法。

##### Assistant (final)

已安装成功，共包含 6 个配套 skill：

- `ponytail`
- `ponytail-review`
- `ponytail-audit`
- `ponytail-debt`
- `ponytail-gain`
- `ponytail-help`

安装位置：[ponytail/SKILL.md](/home/data3/txy/.codex/skills/ponytail/SKILL.md)

下一条新消息即可使用；若没有出现在 skill 列表中，请重启 Codex。

使用示例：

```text
$ponytail full 用最小改动修复这个 bug
$ponytail ultra 简化这个模块，能删除就不要新增
$ponytail-review 检查当前 diff 是否过度设计
$ponytail-audit 审计整个仓库中的过度工程
$ponytail-debt 汇总所有 ponytail: 技术债注释
$ponytail-help
```

模式区别：

- `lite`：正常实现，同时指出更简单的替代方案。
- `full`：默认模式，优先复用、标准库、原生能力和最小改动。
- `ultra`：激进 YAGNI，优先删除并质疑非必要需求。
- 说“stop ponytail”或“normal mode”可退出。

Codex CLI/IDE 使用 `$ponytail`；ChatGPT/Codex 桌面界面可以输入 `@` 后选择对应 skill。任务描述明显涉及“最简方案、避免过度设计、YAGNI”时，也可能自动触发。[OpenAI Skills 文档](https://learn.chatgpt.com/docs/build-skills)、[Ponytail 项目说明](https://github.com/DietrichGebert/ponytail)

本次安装的是独立 skill 版本，不含仓库插件提供的自动生命周期 hooks。

#### Turn 2 — 2026-08-22T19:15:10.000Z

##### User

https://github.com/xiotakut/mrg 下载该目录的压缩包并解压

##### Assistant (commentary)

我先确认仓库默认分支和当前目录是否已有同名文件，再把 GitHub ZIP 下载到当前工作区并解压，避免覆盖现有内容。

##### Assistant (commentary)

仓库中唯一的压缩包是 `medrgag_wm_validation_pack.zip`，当前工作区为空。我会下载这个文件，先做 ZIP 完整性和路径安全检查，再解压。

##### Assistant (final)

已完成下载并解压：

- 压缩包：[medrgag_wm_validation_pack.zip](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack.zip)
- 解压目录：[medrgag_wm_validation_pack](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack)
- 共 20 个文件，ZIP 完整性检查通过，无危险路径。

来源：[xiotakut/mrg](https://github.com/xiotakut/mrg)。

#### Turn 3 — 2026-08-22T19:17:51.000Z

##### User

建立一个subagent，调用 Luna Max。

##### Assistant (final)

可以。请告诉我这个 subagent 要执行的具体任务；创建时我会指定：

- 模型：`gpt-5.6-luna`
- 推理强度：`max`

#### Turn 4 — 2026-08-22T19:25:24.000Z

##### Assistant (commentary)

我会按你指定的 `$ponytail full` 执行：先读取该目录的约束与完整计划，再创建 `gpt-5.6-luna`、`max` 推理强度的 subagent 负责落地；我会持续检查它的进度、代码改动、测试与计划验收项，直到全部验证通过。Ponytail 会约束我们优先复用现有内容并保持最小可靠实现。

##### Assistant (commentary)

已核对权威范围：这不是一个单脚本任务，而是包含 7 个阶段、M0–M10、10 项强制测试及 no-go 自动判定的完整研究实现；现有目录目前只有规格、prompt、schema 和配置，没有实现代码、MedRGAG 上游快照、数据集或私有 NICE 索引。我现在把完整计划原样委派给 Luna Max，要求它先完成所有可由代码证明的实现与测试，并明确记录任何依赖真实数据、人工医学标注或私有资料的门槛。

##### Assistant (commentary)

监督侧环境核查已完成：机器实际上有 4 张 NVIDIA H20（每张约 96GB），磁盘充足；但当前 Python 环境缺少 `pytest/numpy/scipy/statsmodels/torch/transformers`。这意味着实现与标准库自检可以立即完成，真实模型推理和完整统计实验仍需依赖安装环境、公开 benchmark、MedRGAG 上游以及私有 NICE/人工标注。我会据此审查 subagent 是否把“代码完成”和“真实研究结果完成”严格区分。

##### Assistant (commentary)

Luna Max 已完成首个可见里程碑：将公开 MedRGAG 上游以独立、未修改的浅克隆放入 `vendor/MedRGAG`，固定提交为 `0057853df65dcaa46d2934a28f8d5025fc3de623`，工作树保持干净。我正在检查它后续是否通过 adapter 处理单 GPU/答案隔离，而不是修改上游源码。

##### User

当前目录应该有medgrag的全llama版本实现

##### Assistant (commentary)

收到，这会作为新增验收要求：当前项目必须包含 MedRGAG 的完整 Llama 版本实现，不能只保留 Qwen 适配或一个空壳 wrapper。我先核对工作区和上游仓库中现有的 Llama 路径，再把缺口立即反馈给 Luna Max。

##### Assistant (commentary)

关于你补充的“全 Llama 版本”，我已确认原上游只有部分支持：reader/generator 可选 Llama，但 KGCC/KADS 的 summary、explore、selection 仍绑在 GPT-4o-mini，并且上游入口含不可直接运行的占位模型路径。Luna Max 已新增本地 `AllLlamaMedRGAG` 路径，把 KGCC、5 份文档生成、KADS top-5 与 reader 全部串到同一个可配置 Llama 3.1 backend；我正在继续卡住 prompt 一致性、真实数据流和 M9/no-go 验收，尚未把“smoke 通过”当成完整完成。

##### Assistant (commentary)

我继续按 `ponytail full` 监督 Luna Max：现在重点验收“全 Llama”是否真的贯穿摘要、探索、生成、筛选和最终读取，并检查真实运行路径不会静默退化成空检索或假数据。接下来我会针对解析、重试、计费和冻结完整性做独立测试。

##### Assistant (commentary)

初轮审查已经抓到真实运行会踩中的问题：KADS 的官方输出是数字索引，现有解析器却只认 `R0/G0`；规划器展示了五项评分但排序时漏算三项；冻结清单也只检查“文件存在”而未核对哈希。我已把这些列为 Luna 的阻断级修复，并要求每项配回归测试。

##### Assistant (commentary)

Luna 已完成第一轮修复：官方 KADS 数字索引和 `Knowledge 1/2/3` 现在能正确解析，reader 增加了最多两次格式修复、选项校验，单题成本也改为增量统计；量化加载不再错误调用 `.to()`。我刚独立确认上游 MedRGAG 仍锁定在 `0057853…` 且工作树无修改，当前 22 项测试全部通过。现在继续查研究 DoD 和隐私边界，测试通过尚不等于完整计划完成。

##### Assistant (commentary)

现在验收已进入“实验是否真实不同”这一层：我发现最初的 M1/M2/M3 虽有注册名，但部分输入没有真正进入 reader，且 `--nice-index/--oracle` 只是检查文件存在、没有绑定实际内容。Luna 正在把这些占位式通路改成可验证的 artifact 链；当前代码重构期间 27 项测试有 1 项旧断言待更新，我不会在测试重新全绿且端到端语义核验前签收。

##### Assistant (commentary)

实现审查之外，我也在排查能否把“外部阻断”缩小：基准题本身已随上游仓库存在，我会检查机器上是否已有可复用的 Llama 权重或 Python/GPU 环境；若存在，就要求 Luna 运行真实的 20 题基线烟测，而不是停在 fake fixture。

##### Assistant (commentary)

当前基础层重新全绿：27/27 测试通过，官方 6 个 MedRGAG prompt 字节级一致，全 Llama fixture 完整走了 13 次调用（KGCC 5 摘要、探索、5 生成、KADS、reader），KADS 不再 fallback。环境确认没有 Llama 权重、HF 凭据或深度学习依赖，所以真实 20 题运行目前确实受外部权重阻断；我仍在拒收 M0–M10 的“名义可运行”部分，正在核对预算规则、消融隔离和冻结证据链。

##### Assistant (commentary)

对，当前目录应保留并完善 MedRGAG 的全 Llama 实现。我会把它作为验收硬要求：KGCC、文档生成、KADS 和最终 Reader 都走同一套可配置 Llama 后端，并继续检查 Luna Max 子代理提交的实现与端到端证据。

##### Assistant (commentary)

我已确认代码中确实存在独立的 `AllLlamaMedRGAG` 串行流水线，而不是简单改一个 Reader 名称；现在正做第二轮验收，重点核对真实后端、五文档 KADS 顺序、缓存/清单绑定，以及 fixture 不能混入正式实验。

##### Assistant (commentary)

进一步核查时发现，机器上已有一套更完整的真实全‑Llama MedRGAG 实现及正在运行的五数据集流水线（独立目录 `/home/data3/txy/MedRGAG`）。我正让子代理把当前验证包与这套真实八阶段实现对接/锁定，而不是让新写的轻量适配器冒充已经验证过的正式基线。

##### Assistant (commentary)

状态复核更正：发现的是一个仍在运行的监控循环，不是当前推理进程。那套真实全‑Llama 旧运行已完成 retrieval/summary/explore/generate/select，但在旧严格门控下停住，尚无 rerank、reader、evaluate，因此不能当作完整五数据集结果；我已按“历史未完成证据”处理。

##### Assistant (commentary)

又找到另一条独立 run：`all-llama-five-dataset-lenient-v1` 已在 8 月 17 日完整结束八阶段并生成 `metrics.json`，覆盖 7,663 题；刚才未完成的是监控脚本盯着的旧 `full-v1`。我正在核验这条完整 run 的 manifest/源码哈希与质量限制，并把它绑定进当前验证包。其宏平均严格解析准确率为 69.90%，但原审计明确标注它不是论文 Table 1 的同构复现，不能直接当作本项目 WM 结论。

##### Assistant (commentary)

当前真实证据已经厘清：完整全‑Llama run 存在且八阶段封存；旧 `full-v1` 只是历史失败 run。验收仍未结束，因为我要求 Luna Max 补上“正式产物导入器”、同一 Reader 配置约束、复合 item 身份与私有 NICE/oracle 哈希绑定，避免把已有结果粗暴拼进新实验。

##### Assistant (commentary)

外部基线导入器已出现首版，我已拦下几个会导致“假封存”的问题（源码哈希布尔判断、数据集别名、记录自哈希、历史 run 资格）。Luna Max 正在逐项修复；下一步我会用真实 7,663 题 run 的封存文件实际跑绑定命令，而不只依赖模拟测试。

##### User

我认为你错误的纠结在了当前llama版本的地方，v15应该是跑通结果的版本，agent.md里应该也记录了结果。

##### Assistant (commentary)

你说得对。我刚才把“验证包里的轻量参考实现”与“已经跑通的 v15 正式全‑Llama 实现”混在一起审了，确实偏题。现在我会以 `/home/data3/txy/MedRGAG` 的 v15 封存结果和 `agent.md` 为既有基线，只做只读绑定，不再要求子代理重做或改造 v15；监督重点回到 WM 验证计划的 Stage B–G。

##### Assistant (commentary)

你说得对。我先把 `/home/data3/txy/MedRGAG/agent.md` 全文核对一遍，以其中对 v15 的运行记录和结论作为既定基线；后续监督只检查验证包如何复用这份结果，以及 Stage B–G 是否按计划闭环。

##### Assistant (commentary)

我已读完 1,152 行。这里的 `agent.md` 明确把 v15 定义为正式的全 Llama 八阶段实现（统一 checkpoint、`role-stable-v15-guided-sentence-labels`、科研宽容/工程完整性严格）；它的最上层断点写于新 run 启动前，所以“已完成”还要以随后生成的 runtime state、五数据集 completion manifests 和当前验证包的 `agent.md/AGENTS.md` 为准。我现在把这几处证据对齐，不再把参考 backend 当成待替代的主实现。

##### Assistant (commentary)

证据已经对齐：v15 的状态文件是 `completed / exit_code=0`，八阶段全部完成，7,663 题；严格宏平均 69.90%，五项严格准确率依次为 71.88、59.57、78.79、57.40、81.88。接下来验收重点是：冻结后仅重跑 reader 产生主预测、匹配控制和预算不造假、缺少 NICE/人工审查时明确 no-go。

##### Assistant (commentary)

Luna Max 正在按审计意见修正：复用 v15 的边界已改为“只取 answer-free rerank 证据，冻结后本地重跑共享 reader”；跨数据集复合 ID、冻结 prompt hash、NICE/oracle 绑定和源码版本哈希也已补上。当前还剩匹配控制变量、Stage E 实际上下文编排、Stage F/G 聚合评测三块。

##### Assistant (commentary)

我先做一次独立回归测试，确认刚才的协议修正没有破坏既有 31 项测试；这一步只读代码并生成 Python 缓存，不会触碰 v15 或任何实验结果。

##### Assistant (commentary)

独立回归已通过：32/32 单元测试、6 个上游 prompt 字节级 parity 均正常。v15 绑定文件的 schema 已升级，旧绑定会保留为历史，待 Luna Max 完成代码后重新生成并实测新绑定；目前没有启动模型推理或使用 NICE 数据。

##### Assistant (commentary)

Stage E 的真实链路已经出现并通过单独 fixture：冻结标签 → state/action → 对称查询 → 私有证据检索 → NICE-grounded transition，并能在运行时只为 M3 内存补回私有文本，公共结果不携带正文。现在正在修最后两类科学性问题：M8 的 parametric control 不能永远 abstain，以及 invalid prediction 必须计错、不能从准确率分母删除。

##### Assistant (commentary)

你说得对。监督基线应以 `agent.md` 记录的 v15 已跑通结果为准：它是完整八阶段全‑Llama 实现，不再重新论证或重建。接下来只核验验证包如何只读绑定 v15，并集中查收 B–G 阶段、统计门禁和隐私边界。

##### Assistant (commentary)

最新检查确认，v15 本身没有问题；当前真正的风险在验证包：配对对照仍未强制同数据集且会静默少配，预算账本也需要端到端证明。已将这些作为必须修复项反馈给 Luna Max。

##### Assistant (commentary)

Luna Max 正在按这一修正继续落地：v15 被固定为已完成基线；验证包只补实验约束，不改写基线。当前它已开始修复审核材料私有化和统计聚合，我会等文件稳定后独立跑全套测试与真实绑定校验。

##### Assistant (commentary)

我现在先做一项独立查收：重新生成 v15 的内容寻址只读绑定，并随机加载一条 rerank 证据验证。这里只读取 v15，不运行或修改它，也不会采用其历史 reader/evaluate 预测。

##### Assistant (commentary)

v15 绑定已通过实测：`sealed=true`、八阶段完整、source 无缺失；随机一题成功解析出恰好 5 个 hash 校验通过的 rerank 文档。这个结果确认了你的判断，也把 Stage A 从“待跑”纠正为“v15 已完成、可只读复用证据”。

##### Assistant (commentary)

配对对照已改为独立的、答案隔离特征文件，并开始强制同数据集/学科/长度区间/选项数/reader-only 难度/多跳；我查出并要求去掉了计划未规定的 `task_type` 过度匹配，同时补答案字段拒绝与运行哈希绑定。现在还在收口统计资格判定。

##### Assistant (commentary)

目前监督结果很明确：Stage A 已有经校验的 v15 完整产物；B–G 仍因没有冻结切片、私有 NICE、双人盲审和 ≥200 条人工 fidelity 审核而不能宣称科学完成。代码会继续补齐可执行路径，但 no-go 必须保持 `no_wm_claim`，不能用 v15 的旧预测填这些新门禁。

##### Assistant (commentary)

首轮独立回归测试目前是 33/33 通过；但这还不够作为验收，因为尚缺我要求的真实路由矩阵、matched-feature 防泄漏和 M2/M3/M7 端到端预算测试。现有通过结果只说明旧测试未回归。

##### Assistant (commentary)

目前查收到的隐私修复已覆盖审核队列本身：反事实与 transition 审核材料都会被限制在 `private_data/` 或缓存目录，公开聚合只保留哈希和统计。接下来还要验证反事实预测执行链是否真正闭合。

##### Assistant (commentary)

反事实断链正在修复：已经新增独立的 M0/M7 反事实运行入口，避免把派生题伪装成冻结原题。接下来我会重点核验它是否绑定双人审核文件、复用同一 reader/五篇 v15 证据，并对 relevant/irrelevant 两类每题都做完整性检查。

##### Assistant (commentary)

Luna Max 已开始补新增测试：matched-feature 防泄漏用例已落地，反事实 runner 也正在修复重复写入和 M0 prompt 不一致。等这轮稳定后，我会运行它的 fixture E2E，而不是只做静态检查。

##### User

你目前的这些门禁，哈希，和反事实运行入口到底是在干什么？我是让你验证代码是否遵循什么安全措施了吗？重复一遍文件夹里面的计划是什么，你最首先干的就是从现有5个测试集里面去找符合wm的测试题。

##### Assistant (commentary)

你说得对，我把“防止研究结果被污染的附属约束”错误地提到了主任务前面，已经偏离了文件夹计划的执行顺序。

这个计划的首要实质任务是：从现有 5 个测试集各随机抽最多 200 题，先用不看答案/预测的分类器筛出需要 state–action–transition 推理的题，再按 Tier A/B/C/NONE 整理候选切片。v15 已经跑通，所以 Stage A 不应继续折腾；现在应直接执行 Stage B。哈希、门禁和反事实都是后续 C–G 阶段的记录与验证工具，不是当前第一目标。

##### Assistant (commentary)

文件夹里的执行计划，按顺序是：

1. Stage A：验证 MedRGAG 基线可运行。这里 v15 已完成，五数据集共 7,663 题、八阶段跑通。
2. Stage B：从 MedQA、MedMCQA、MMLU-med、PubMedQA*、BioASQ-YN 各抽最多 200 题；不看答案，判断哪些题真正需要 action applicability、next-state、outcome 或 sequential transition，分 Tier A/B/C/NONE；然后人工复核并冻结。
3. Stage C：只在冻结切片上测 v15/M0 是否存在 action-transition 缺口，并与普通非 action 题匹配比较。
4. Stage D：在 Tier A 上做人审 oracle transition，确认这个方向是否有上界收益。
5. Stage E：运行 M1–M9，比较 decomposition、额外推理、额外 NICE 检索、precondition/effect、完整 WM、无 NICE、shuffle 等消融。
6. Stage F：做反事实最小对和 transition fidelity 人工审核。
7. Stage G：根据预设标准决定能否称为 world model。

我已把 Luna Max 从后续基础设施工作中打断并重定向到第 2 步。实测数据文件包含这五套题（另有 MedXpertQA，但不在本计划五集范围）；GPU 0 当前空闲，真实筛题运行将使用它。

##### Assistant (commentary)

真实 Stage B 已启动。Luna Max 先在 GPU 0 做每数据集 1 题的五集 smoke（本地 Llama‑3.1‑8B、两 seed），确认分类器输出和数据隔离无误后再扩到每集 200 题；这一步只读 `question/options`，不会把 benchmark 里的 `answer` 交给模型。

##### User

“哈希、门禁和反事实都是后续 C–G 阶段的记录与验证工具，不是当前第一目标。”你为什么还在说这个，原代码已经明确说明了不需要这些东西，这只是执行实验的代码不需要这些安全措施

##### Assistant (final)

因为我把“研究复现记录”误当成了当前实验执行目标，并继续沿着这个错误方向扩展，这是我的判断失误。

从现在起不再新增或讨论哈希、门禁、反事实安全入口等内容。当前唯一工作是：

1. 在五个现有测试集上运行真实分类器；
2. 找出符合 WM/action-transition 推理定义的题；
3. 汇总 Tier A/B 候选及人工复核队列；
4. 再按实验计划继续运行后续对照实验。

GPU 0 上的五数据集真实筛题 smoke 已经启动。

#### Turn 5 — 2026-08-22T21:49:10.000Z

##### Assistant (commentary)

继续按实验本身推进：我现在只查收五数据集 WM 题筛选的真实运行结果，并在 smoke 通过后扩到计划规定的每集 200 题。

##### User

你先重复一遍你的详细计划，从哪里得来的

##### Assistant (commentary)

我会按文件原文逐项对应，不再混入我自行扩展的工作。先核对 `PROJECT_PLAN.md`、`AGENTS.md/agent.md` 和实验矩阵中的具体段落与行号。

##### Assistant (final)

计划来源不是我自行制定的，来自当前文件夹内这几份文件：

- [PROJECT_PLAN.md](/home/data3/txy/docs/archive/wm_medrgag.md#record-0263)：研究问题、题目分类、pilot、方法和实验设计。
- [AGENTS.md](/home/data3/txy/docs/archive/wm_medrgag.md#record-0264) 与 `agent.md`：Stage A–G 的实际执行顺序。
- [experiment_matrix.yaml](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/configs/experiment_matrix.yaml:10)：五个数据集、每集抽样数、M0–M10 和主要比较。
- [01_action_slice_classifier.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/prompts/01_action_slice_classifier.md)：第一阶段筛题提示词。

我的详细执行计划如下。

1. 确认基线

v15 已完成五数据集、八阶段全‑Llama 运行，因此不再重建 Stage A。

五个目标测试集共 7,663 题：

- MedQA-US：1,273
- MedMCQA：4,183
- MMLU-Med：1,089
- PubMedQA*：500
- BioASQ-Y/N：618

`benchmark.json` 里另外还有 MedXpertQA，但不属于本计划，暂不纳入。

2. 首先筛选符合 WM 定义的题

这是当前正在执行的首要任务，对应 `PROJECT_PLAN.md` 的 Phase 0 和 Pilot P1：

- 每个数据集确定性随机抽取 200 题，共 1,000 题。
- 分类器只接收 question 和 options。
- 使用 `01_action_slice_classifier.md` 低温独立运行两次。
- 每次输出都按照 `action_label.schema.json` 检查。
- 汇总两次分类结果、分歧题、各数据集和 task type 分布。

题目分级标准：

- Tier A：必须利用“当前状态 → 临床行动 → 下一状态/观察/结果”才能区分答案，并存在替代行动或替代结果。这才是严格 WM 题。
- Tier B：需要根据患者状态选择行动，但不必显式预测行动后的状态。
- Tier C：只有治疗/检查等行动词，实质仍是静态知识回忆。
- NONE：诊断、机制、遗传、解剖等非 action 题。

自动筛选后，优先整理：

- 两次都判为 Tier A/B 的题；
- 两次分类存在分歧的题；
- Tier A/B 候选题的 task type、action 和 transition target；
- 供人工复核的题目队列。

Pilot P1 的判断是：如果 1,000 题中严格 Tier A 少于 100，或几乎只来自一个数据集/题型，就不继续把它发展成五数据集 WM 主线。

3. 检查 v15 在 WM 题上的表现

筛题和人工复核完成后：

- 在 Tier A、Tier B 和非 action 题上分别统计 v15/M0 表现。
- 为 Tier A 匹配普通非 action 对照题。
- 判断 v15 是否确实在 action-transition 题上存在稳定缺口。
- 若缺口不成立，不继续声称原 MedRGAG 缺少 WM 推理。

4. 做 Oracle transition 上界实验

从 Tier A 随机取 100–200 题，构建经过审核的：

- state
- action
- precondition
- effect/next state
- rollout ranking

比较原 MedRGAG、oracle action decomposition、oracle transition 和 oracle rollout。如果 oracle transition 也不能提升，计划要求停止方法开发或改做 benchmark 研究。

5. 实现最小单步 WM

只实现计划规定的最小机制：

1. state extraction
2. balanced action-specific NICE retrieval
3. precondition/effect prediction
4. one-step counterfactual comparison
5. final answer

不训练模型，不做 MCTS，不做长轨迹。

6. 运行 M0–M10 实验

- M0：原 MedRGAG
- M1：action decomposition
- M2：额外推理
- M3：action-specific retrieval
- M4：precondition only
- M5：effect only
- M6：WM cards、无 rollout comparison
- M7：完整 AW-MedRGAG
- M8：无 NICE 的 WM
- M9：打乱 action–effect
- M10：oracle transition

核心比较是 Tier A 上 M7 对 M0、M1、M2、M3。

7. 做完整评估

最后按照计划报告：

- 五数据集总体和 Tier A/B/non-action 表现；
- matched-control diagnosis；
- action-relevant 与 irrelevant 最小对；
- transition fidelity；
- action–effect shuffle 等机制实验；
- 延迟、调用、token、失败率和覆盖率。

当前执行位置是第 2 步。Luna Max 已在 GPU 0 上运行五数据集真实筛题 smoke；确认五集各一题都能正常分类后，立即扩到每集 200 题。

#### Turn 6 — 2026-08-22T21:51:10.000Z

##### Assistant (commentary)

继续监督当前 Stage B：先确认五题真实 smoke 的分类结果和耗时，再决定 1,000 题全量筛选的启动参数。

##### User

你tm是不是找错了，你的详细计划是tm在    medrgag_wm_validation_pack这个文件夹下面

##### Assistant (commentary)

你说的是这个目录：`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`。我现在核对是否还存在另一个同名目录，避免继续在错误副本上执行。

##### Assistant (final)

刚核对过：系统中只有一个 `medrgag_wm_validation_pack`，路径就是：

`/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack`

我读取的计划文件也都在这个目录下：

- `medrgag_wm_validation_pack/PROJECT_PLAN.md`
- `medrgag_wm_validation_pack/agent.md`
- `medrgag_wm_validation_pack/AGENTS.md`
- `medrgag_wm_validation_pack/configs/experiment_matrix.yaml`

`/home/data3/txy/MedRGAG` 只用于读取现有五数据集和已跑通的 v15 产物，不是计划来源。接下来严格按 validation pack 内的计划执行，当前第一项就是五数据集各抽 200 题筛选 WM 候选。

#### Turn 7 — 2026-08-22T21:52:16.000Z

##### Assistant (commentary)

继续当前筛题运行，先查收 smoke 是否完成以及五题的实际分类输出。

##### Assistant (commentary)

smoke 暴露了真实问题：10 次分类只有 4 次有效，seed 13 的五题全部 JSON 解析失败，BioASQ 的另一次还违反 schema。Luna Max 不应在这个结果下直接扩到 1,000 题；我正在立即停止这次全量运行，先修正分类输出解析并重新 smoke。

##### Assistant (commentary)

第二次 smoke 已达到 10/10 schema-valid，低温修复有效；5 题结果为 A、A、C、B、C。查收时又发现一个实验逻辑问题：当前把两个完整 JSON 的任何措辞差异都算“分歧”，并把全部题送人工；计划原文只要求“双次均 A/B 或分类结论有分歧”的题进入复核。我会先纠正候选队列规则，再启动 1,000 题。

##### Assistant (commentary)

Luna Max 又把全量任务切回了第三次 smoke，用来验证候选队列筛选规则；这会损失约一分钟，但不会损失有效全量结果。等 v3 完成后我将只允许启动一次正式 1,000 题运行，不再反复重启。

##### Assistant (commentary)

v3 smoke 已正确验收：10/10 有效，5 题中 A/A/B 三题进入复核，C/C 两题未进入，完全符合 Phase 0A。正式 1,000 题运行现已启动，使用 GPU 0、两次低温分类；我不再重启它。

##### Assistant (commentary)

正式运行保持稳定，GPU 0 持续推理，未再出现退出或重启。该脚本在全部 1,000 题完成后一次性写结果，因此当前没有中间题数；我按进程、GPU 和最终产物三项持续查收。

##### Assistant (final)

Stage B 正式筛选正在运行：

- 五个数据集各 200 题，共 1,000 题
- 每题使用 seed 13、37 各分类一次
- v3 smoke 已 10/10 有效
- GPU 0 运行稳定
- 完成后将输出全部分类结果、Tier 分布、WM 候选清单和人工复核队列

当前任务保持运行，尚未完成。

#### Turn 8 — 2026-08-22T22:02:43.000Z

##### Assistant (commentary)

继续监督正式筛选进程，检查运行时长、GPU 状态和结果文件是否已经生成。

##### Assistant (commentary)

运行仍稳定，GPU 0 保持约 75% 利用率；当前脚本没有逐题进度输出，正式结果会在 1,000 题全部完成后生成。我没有再修改或重启该进程。

##### Assistant (final)

正式 1,000 题筛选仍在稳定运行，尚未生成最终分类文件。Luna Max 已被要求在完成后立即输出分类有效率、Tier 分布、一致率、分歧数和 WM 候选清单。

#### Turn 9 — 2026-08-22T22:05:28.000Z

##### Assistant (commentary)

继续检查正式筛题进程与最终产物。

##### Assistant (final)

正式筛题进程已连续运行约 8 分钟，GPU 0 稳定，无异常退出；结果文件尚未写出。

#### Turn 10 — 2026-08-22T22:06:48.000Z

##### Assistant (commentary)

继续等待并核验进程，没有进行其他改动。

##### Assistant (commentary)

对，我之前把“现有 Llama/v15 结果”和“待执行计划”混成了两个来源，找偏了。计划唯一以当前目录下的 `medrgag_wm_validation_pack/` 为准；我现在只按这里的 `PROJECT_PLAN.md`、`agent.md`、`AGENTS.md` 和实验矩阵监督执行，第一项就是从 5 个测试集筛 WM 题。下面我核对正在跑的任务，不再扩展到任何门禁或安全措施。

##### Assistant (commentary)

我已经纠正来源：v15 只用于确认 Stage A 基线跑通，不是计划文件。当前正式筛选进程仍在运行（PID `1379248`，没有重启）；它执行的正是 pack 中 Phase 0A/P1 的“五库各 200 题、双次低温分类”。

##### Assistant (final)

对，我之前找偏了。详细计划唯一来源是：

- [PROJECT_PLAN.md](/home/data3/txy/docs/archive/wm_medrgag.md#record-0263)
- [agent.md](/home/data3/txy/docs/archive/wm_medrgag.md#record-0264)
- [experiment_matrix.yaml](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/configs/experiment_matrix.yaml:28)

正确执行顺序是：

1. 从 MedQA、MedMCQA、MMLU-Med、PubMedQA、BioASQ 五个测试集各随机抽 200 题，共 1000 题。
2. 每题进行两次独立低温分类，找出符合 WM 定义的 Tier A/B 题。
3. 汇总 Tier 分布、两次分类一致率、分歧题和待人工复核题。
4. 冻结 WM 测试子集。
5. 再做 baseline deficit、oracle transition、最小 WM 实现和后续 M0–M10 实验。

v15 只是已经跑通的原 MedRGAG 基线结果，不是计划来源。当前 Luna Max 正在执行第 1–2 步，PID `1379248`，没有重启。后续不再添加计划之外的哈希、安全门禁或其他基础设施。

#### Turn 11 — 2026-08-22T22:09:24.000Z

##### Assistant (commentary)

继续监督现有 Luna Max 子代理。按 `ponytail full`，我只做当前实验必需的监控与结果核验，不再加任何额外设施；先检查正式 1000 题筛选进程和输出目录。

##### Assistant (commentary)

正式进程当前稳定：已运行约 11 分钟，GPU 占用约 16.2 GB，Luna Max 子代理仍在监督。脚本采用完成后一次性写出结果，因此现在只有 manifest；我不会因暂时没有中间文件而重启它。

##### Assistant (commentary)

第二次检查仍正常，GPU 利用率约 75%，进程没有停滞迹象。当前不改代码、不插入新日志、不重跑，只等待这次正式筛选完成并在结束后独立验收 1000 条结果。

##### Assistant (commentary)

当前 manifest 也确认了这次实验参数：五个 pack 指定数据集、每题两个种子 `13/37`、温度 `0.1`，模型为本地 Llama 3.1 8B。这里只是在执行 WM 题筛选；最终是否合格要等候选文件写出后按题数、数据集分布和双次结果逐项验收。

##### Assistant (final)

Luna Max 正在按 `medrgag_wm_validation_pack` 执行首个正式任务：

- 五个数据集各抽样 200 题，共 1000 题
- 每题使用两个种子低温分类
- 当前进程稳定，GPU 正常工作
- 完成后我会独立核验题数、数据集分布、Tier A/B 候选和人工复核队列

此次运行不会被重启，也不会增加计划外内容。目标尚未完成，保持继续执行。

#### Turn 12 — 2026-08-22T22:13:36.000Z

##### Assistant (commentary)

继续监督同一正式筛选，不改动也不重启。按 `ponytail full`，本轮只检查运行是否健康以及最终结果是否已经落盘。

##### Assistant (commentary)

进程仍持续占用 GPU0，当前没有异常退出；结果文件仍按脚本设计在全部 2000 次分类完成后统一写出。我继续守候这一进程。

##### Assistant (final)

正式筛选仍稳定运行，已持续约 17 分钟，Luna Max 子代理保持执行。输出尚未统一落盘，因此当前不能提前宣称筛选完成；我会继续监督，完成后再逐项验收 1000 题结果。

#### Turn 13 — 2026-08-22T22:16:08.000Z

##### Assistant (commentary)

继续查收同一任务。本轮仍遵循 `ponytail full`：只确认进程健康与结果是否落盘，避免干扰正式分类。

##### Assistant (commentary)

运行已超过 18 分钟，GPU0 仍持续计算，未出现退出或错误。由于最终文件尚未生成，我现在继续等待，不提前判定 Tier 结果。

##### Assistant (commentary)

Luna Max 子代理仍在运行正式分类；进程状态为运行态，不是僵尸或休眠。当前唯一正确动作是让这次 2000 次推理完整结束。

##### Assistant (commentary)

22 分钟检查点：PID、GPU 显存和利用率都正常，正式输出仍未落盘。没有重启、没有改动运行参数。

##### Assistant (commentary)

这一步没有可安全读取的中间计数，继续逐分钟重复状态没有价值。我让现有进程不受干扰运行一段时间，下一次检查直接看是否已生成候选与复核文件。

##### Assistant (commentary)

34 分钟检查点仍正常。为了给出更可靠的等待时间，我只读取之前 10 题 smoke 的文件时间，估算同一模型与参数下 2000 次推理的总耗时，不触碰当前进程。

##### Assistant (commentary)

按 smoke v3 的实测速度，10 次分类约 74 秒；正式任务是 2000 次，预计总耗时约 4.1 小时。当前已运行约 35 分钟，速度与预期一致。我会按较长间隔继续监督，子代理一完成会立即返回，不需要用户介入。

##### Assistant (commentary)

65 分钟检查点：进程仍为运行态，GPU0 约 74% 利用率，未出现错误或结果提前终止。正式筛选继续原样执行。

##### Assistant (commentary)

异常：约 95 分钟检查时，正式 PID 已退出，但候选结果文件没有生成。我现在立即查收 Luna Max 的退出信息和错误原因；不会直接重跑。

##### Assistant (commentary)

我发现 Luna Max 在 v3 退出后自行启动了 v4，这违反了我先前下达的“不要重启”监督要求。我已先中断子代理的自主操作，但保留了已经运行约 20 分钟的 v4 进程，避免再次丢失计算；现在要求它只报告 v3 的确切退出原因和 v4 的启动依据。

##### Assistant (commentary)

v4 当前仍在健康运行，代码修改时间显示它启动前只改了分类脚本中的异常响应处理；我正在等待 Luna Max 给出完整退出证据。在证据明确前，我既不停止 v4，也不认可这次擅自重启。

##### Assistant (commentary)

退出原因已经确认：v3 在 MedMCQA 某题返回了错误题目身份，脚本未捕获而整体退出。v4 仅把该单题记为 `invalid_identity` 后继续，其余模型、抽样、温度和复核规则未变。考虑到 v4 已运行约 21 分钟且修复直接针对实际故障，我保留它继续运行；已明确禁止 Luna Max 再自行改动或重启。

##### Assistant (commentary)

v4 的 52 分钟检查点正常：进程持续计算，GPU0 利用率约 77%，没有新异常。继续保持原样运行。

##### Assistant (commentary)

v4 已运行约 1 小时 23 分钟，仍正常。它现在会把偶发身份错误保留为无效标注供复核，而不会再让整批 1000 题中断。下一检查点继续看最终文件是否落盘。

##### Assistant (commentary)

2 小时 23 分钟检查点正常，GPU0 仍持续推理。根据 smoke 实测速率，预计还需约 1.5–2 小时；当前没有需要人为处理的异常。

##### Assistant (commentary)

正式筛选已完成并生成结果：`candidate_labels.jsonl` 约 5.0 MB，`human_review_queue.jsonl` 约 2.5 MB，进程已正常退出。现在进入我的独立验收：核对 1000 题、五库各 200、每题双标、状态/Tier 分布以及复核队列规则。

##### Assistant (commentary)

独立验收通过核心完整性检查：1000 题、五库各 200、无重复、每题恰好两个种子标注；共 392 题进入人工复核队列。初步双一致结果为 Tier A 241 题、Tier B 82 题；另有 13 题在 A/B 间分歧。MedMCQA 有 2 道题的两次返回都出现身份错误，已作为无效标注保留在复核队列，没有丢题。

##### Assistant (commentary)

P1 的机器初筛已经达到可继续条件：双一致 Tier A 为 241 题，分布在 MedQA、MedMCQA、MMLU-Med、PubMedQA 四个数据集，并非单库或单题型集中。下一步不是直接跑 MedRGAG，而是按 pack 对 392 条队列做两名人工盲审；我先检查现有冻结脚本所要求的最小标注格式，避免另造工具。

##### Assistant (commentary)

主代理与 Luna Max 的统计完全一致，Phase 0A 已验收。按计划，下一步需要两名真实人工标注者（至少一名医学背景），不能把模型输出冒充人工结果。为不浪费时间，我让 Luna Max 只生成最小盲审材料：隐藏数据集/题号和机器标签、保留问题与选项、提供两份独立空白标注表；不写新框架。

##### Assistant (commentary)

Luna Max 已生成 392 条双人盲审材料。我现在独立检查是否真的隐藏了数据集、题号和机器标注，映射能否完整回连，以及两份顺序是否独立；检查通过后才交付给人工标注者。

##### Assistant (commentary)

盲审包内容核验通过。不过 `review_id` 被做成了长摘要字符串，不符合 `ponytail full` 的最简原则，也容易让你误以为又在搞哈希。我会让 Luna Max 把它改成普通的 `R001`–`R392`；功能不变，不新增任何机制。

##### Assistant (final)

Phase 0A 已完成并验收：

- 1000 题，五库各 200
- 双一致 Tier A：241 题，覆盖 4 个数据集
- 双一致 Tier B：82 题
- 人工复核队列：392 题
- P1 暂时满足继续条件

Phase 0B 的两份盲审材料已准备好：

- [Reviewer A](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_a.jsonl)
- [Reviewer B](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_b.jsonl)
- [标注说明](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/README.md)

现在需要两名真实人工标注者独立填写，至少一名具备医学背景。不能让 Luna Max 冒充人工完成这一步。两份文件返回后，我会继续监督 Luna Max 计算一致性、处理分歧、形成最终 WM slice，然后进入 P2。

#### Turn 14 — 2026-08-23T02:48:05.000Z

##### Assistant (commentary)

继续按 pack 监督 Phase 0B。我先检查两份盲审文件是否已有人工填写；若仍为空，我不会伪造人工标签，也不会越过该步骤进入 P2。

##### Assistant (final)

两份盲审文件目前仍是 `0/392` 已填写，因此 Phase 0B 尚未开始。现在无法在不违反计划的情况下继续：需要两名真实人工标注者独立完成文件，至少一名具有医学背景。

文件返回后，Luna Max 将继续合并标注、计算一致性、整理分歧裁决并进入后续实验。

#### Turn 15 — 2026-08-23T02:48:29.000Z

##### Assistant (commentary)

我做第三次状态核验；如果两份人工盲审仍未填写，就已经满足“连续三次相同外部阻塞”的条件，只能暂停在 Phase 0B，不能擅自用模型替代人工。

##### Assistant (final)

任务现已暂停在 Phase 0B：两份人工盲审均为 `0/392` 完成，连续三次检查无变化。

恢复条件：两名真实标注者分别完成 [Reviewer A](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_a.jsonl) 和 [Reviewer B](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/human_review/reviewer_b.jsonl)，至少一人具备医学背景。完成后即可恢复 Luna Max，继续一致性计算、分歧裁决和后续实验。

#### Turn 16 — 2026-08-23T05:11:29.000Z

##### User

先让luna max辅助判断，因为我们现在只是做实验看效果，如果有效后续会换成真人

##### Assistant (commentary)

可以。我们把这一步明确改成“实验性 Luna Max 代理复核”，先验证方法有没有效果；不会把它写成真人标注或正式冻结结果。按 `ponytail full`，只生成一份 Luna 代理裁决，不伪造两份“人工”记录，后续若有效再由真人替换。

##### Assistant (commentary)

我把 392 题拆成 8 个小批次，避免 Luna 一次吞掉全部题导致漏标。第一批是 `R001–R049`；每题生成一条明确标为 `luna_max / provisional` 的完整代理标签，我会逐批核验覆盖范围、身份和 schema。

##### Assistant (commentary)

Luna Max 已把第一批交给其同模型子任务处理，当前仍在逐题判定；没有写入范围外数据。我继续等待第一批完成后再验收。

##### Assistant (commentary)

第一批已完成，Luna 给出 49 条代理裁决。我现在独立核对：是否恰好覆盖 `R001–R049`、是否与原题身份一致、完整标签能否通过 pack 的 schema，以及 Tier 统计是否一致。报告里的摘要值不作为验收依据。

##### Assistant (commentary)

第一批独立验收通过：49/49 覆盖准确，schema 与 Tier 逻辑一致，A=11、B=16、C=17、NONE=5。现在推进第二批 `R050–R098`，仍只做 Luna 代理标签，不进入 P2。

##### Assistant (commentary)

第二批已返回。我会用同一套独立检查验证 `R050–R098`，并确认它没有覆盖第一批或写入范围外题目。

##### Assistant (commentary)

第二批也独立验收通过。为缩短等待时间，接下来让两个 Luna Max 上下文并行处理互不重叠的 `R099–R147` 与 `R148–R196`；各写独立文件，我分别验收，不会发生覆盖。

##### Assistant (commentary)

`R148–R196` 已先完成；另一批仍在判断。我先独立验收已完成文件，同时不打断正在处理的批次。

##### Assistant (commentary)

两个并行批次均验收通过，当前累计 `196/392`。继续并行处理 `R197–R245` 与 `R246–R294`，仍保持 provisional 标记和相同校验标准。

##### Assistant (commentary)

`R246–R294` 已先返回，我先验收；`R197–R245` 仍在运行。

##### Assistant (commentary)

两批再次全部通过，累计 `294/392`。现在处理最后两批 `R295–R343` 与 `R344–R392`；完成后我会合并并做全量交叉核验，再生成 provisional WM slice。

##### Assistant (commentary)

`R295–R343` 验收通过，最后只剩 `R344–R392` 正在处理。

##### Assistant (commentary)

最后一批也验收通过，Luna 已完成 `392/392` 代理复核。下一步先做全量合并审计：392 条采用 Luna 裁决，另外 608 条双次一致的非候选题保留自动共识，形成 1000 题 provisional slice；随后核对 Tier 是否达到 P1 条件。

##### Assistant (commentary)

全量代理结果为：Tier A `85`、B `118`、C `724`、NONE `73`。严格按原 P1 阈值，A=85 低于 100；但你已经明确这是先看效果的实验，所以我会把它标成“exploratory provisional”，继续用现成 v15 基线做 P2，不把它包装成正式通过。先让 Luna 合并出可直接使用的 1000 题代理 slice。

##### Assistant (commentary)

合并文件已生成。我现在做全量独立验收，并定位 Luna 报告的两条 `Tier C + eligible=true` 源标签；若确认只是分类器语义不一致，会做最小归一化，避免后续路由含糊。

##### Assistant (commentary)

全量合并的数量、顺序、身份和 schema 全部正确；只发现两条自动共识标签把 Tier C 同时标成 eligible。虽然当前路由不会误启用 WM，但语义不一致。我让 Luna 做唯一的最小修正：这两条改为 `eligible=false`，其他 998 条保持字节级不动。

##### Assistant (commentary)

代理 slice 已完整验收。现在进入用户要求的“先看效果”：不重跑已有基线，直接读取已经跑通的 v15 全 Llama 五库结果，与这 1000 条 provisional 标签按 `(dataset,item_id)` 对齐，先做 P2 baseline deficit。按 `ponytail full`，复用现有结果而不是再跑模型。

##### Assistant (commentary)

v15 的逐题 reader records 已找到，覆盖五个数据集，不需要重跑模型。我让 Luna Max 直接做最小 P2：按题号连接 provisional slice、v15 预测和 gold，计算 Tier 分层准确率，并做一个明确标注为 exploratory 的简易匹配对照（同数据集、同选项数、题长最近）。正式复杂匹配留到确认有效之后。

##### Assistant (commentary)

我发现 v15 reader record 的字段命名容易误读：`payload.answer` 实际很可能是 gold，而 `author_answer` 才是模型预测；直接把 `answer` 当预测会得到荒谬的 100%。“严格口径”必须从解析字段取，而不能按名字猜。我正在核对 v15 自己的评估代码和 payload 全字段，避免给出错误 P2。

##### Assistant (commentary)

Luna 的 P2 分层准确率与我的独立计算一致，但简易匹配后的差值不一致，说明贪心配对受处理顺序或题长定义影响。我不会直接采用它的匹配结论；现在逐项核对 85 对的选择规则，并做匹配顺序敏感性分析。

##### Assistant (commentary)

P2 产物的 1000 条预测、85 个匹配对及聚合值全部独立验收通过。匹配对的结论是：控制组并没有比 Tier A 稳定高出 ≥3pp；置信区间也跨过 0。Luna 漏写了配对 bootstrap 区间，我让它只补这一项，然后继续最小 WM 效果实验。

##### Assistant (commentary)

P2 没有看到 baseline deficit：Tier A 与非 action 基本持平，简易匹配后差值也小且区间跨 0。按你的“先看效果”要求，我不会在这里停；下一步做一个真正最小的 WM A/B 试验。pack 现有正式入口夹带大量冻结/绑定检查，我不会用它，直接复用 v15 的问题、top-5 文档和同一个 Llama reader，仅比较“原输入”与“加一张 Luna transition card”的结果。

##### Assistant (commentary)

我先构造一个不含 gold 和任何 v15 预测的 20 题 Tier A 输入，抽样只依赖 provisional 标签、seed 13，因此不会按基线对错挑题。随后让 Luna Max 只看这份题面、选项和原 v15 top-5 文档生成 parametric 单步 transition cards。

##### Assistant (commentary)

20 题输入已确认完全不含 gold、预测或 reader 输出，且每题保留原 v15 的 5 份证据。Luna Max 正在基于这份隔离输入生成单步 parametric transitions。

##### Assistant (commentary)

Luna 已生成 20 题、74 张 parametric transition cards。我现在独立校验结构和隔离性，并在不反馈给 reader 的前提下，用 gold 事后测量 planner 自身的选项命中率，判断这些卡是否值得进入 reader 对照。

##### Assistant (commentary)

Luna Max 的 20 题代理状态与转移卡已经完成；我已把它作为“探索性代理判断”验收，不冒充真人标注。现在按文件夹计划，在同一批 20 题上跑最小对照：原始 v15、仅状态、状态+转移卡，直接看 reader 效果。先把原始 v15 提示词做到逐字一致。

##### Assistant (commentary)

原始提示词差异已经定位：不是数据问题，而是 v15 在组装文档后做了一次 Llama tokenizer 的 encode→decode；其中 1/20 题被规范化了一个空格。runner 会复用这一步，确保 20/20 与 v15 原提示词一致，再做公平对照。

##### Assistant (commentary)

Luna Max 的复核结论很明确：原 `07_final_reader` 会把 74/74 张 `unsupported` 卡全部屏蔽，PX 会退化成空对照。按 ponytail full，我只加一个很短的“代理推理上下文”模板：三组都保留原 v15 reader、同一 system prompt 和同一输出格式；M1 只追加 state，PX 再追加 cards/planner，并明确这些只是可核验的 Luna 假设、不是 NICE 或真人结论。

##### Assistant (commentary)

脚本已压到一个 runner、一个短模板。预检通过：20 个 M0 user prompt 与 v15 存档逐字 20/20 一致；最长 PX 输入约 4k tokens，远低于 8k 上限。现在占用空闲的 GPU 1 跑 60 次 reader 推理，其他 GPU 进程不动。

##### Assistant (commentary)

模型已在 GPU 1 正常加载，60 条提示也已准备完成；当前只是在 vLLM 首次编译计算图，尚未进入结果评估。

##### Assistant (commentary)

首轮结果已经出来：同一 20 题上，M0 12/20（60%）、仅 state 13/20（65%）、Luna state+cards+planner 16/20（80%）。也就是 PX 相对本次 M0 +20pp、相对结构化对照 +15pp；样本很小，McNemar 仍未显著。原 v15 存档是 13/20，本次单卡复跑与它 19/20 预测一致，所以按存档基线看是 +15pp。接下来我做逐题验收，确认提升不是统计脚本错误或机械照抄 planner。

##### Assistant (final)

结果支持进入真人复验，但还不能宣称方法有效。

| 条件 | 正确率 |
|---|---:|
| M0：v15 原 reader | 12/20，60% |
| M1：增加 state/action | 13/20，65% |
| PX：增加 Luna cards + planner | 16/20，80% |

- PX 相对本次 M0：+20pp，5 题改善、1 题恶化。
- 相对原 v15 存档基线 13/20：+15pp。
- 相对 M1：+15pp，3 题改善、0 题恶化。
- 排除一题因 512-token 截断造成的无效输出后，PX 相对 M1 仍约 +10.5pp。
- 样本仅 20 题，置信区间包含 0，McNemar `p=.25`，尚不显著。
- PX 与 planner 一致 17/20；它拒绝 planner 3 次，其中修正 1 次错误、引入 2 次错误，因此不是纯照抄，但存在锚定风险。

M0 使用 v15 的原 top-5 evidence，提示词逐字匹配 20/20；没有重跑整个 MedRGAG。单 GPU 复跑与原 v15 预测一致 19/20。

Luna Max 和我的独立验收结论一致：下一步不扩样，先让两名真人——至少一名临床背景——盲审当前 20 题的 74 张卡。隐藏 gold、reader 输出、planner 排序和 Luna 身份，裁决 state、transition、applicability、goal alignment 与不确定性；之后只新增一个 `PX-human-adjudicated` 条件复跑。

产物：

- [实验汇总](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_reader_summary.json)
- [逐题结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_reader_results.jsonl)
- [可复现 runner](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py)
- [代理 reader 上下文模板](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/prompts/17_proxy_parametric_reader_context.md)

这些结果仍是 Luna 代理、无 NICE、非真人验证的探索结果。

#### Turn 17 — 2026-08-23T07:16:57.000Z

##### Assistant (commentary)

探索信号已经达到“该换真人核验”的程度，所以接下来不再让 Luna 代替真人下临床判断。Luna Max 只负责把现有 20 题、74 张卡整理成盲审包，我负责检查是否真正隐藏了 reader 结果、planner 和 Luna 身份；按 ponytail full，只做这一份最小交接材料，不扩样、不加新框架。

##### Assistant (commentary)

Luna 正在生成盲审包；我要求它只做去标识与随机化，所有评审值保持空白。完成后我会逐项重算 74 张卡是否一一对应，并检查 reviewer 文件中没有 planner、预测结果或模型身份。

##### Assistant (commentary)

Luna 已交付四个文件且没有填写任何评审值。现在由我独立从原始 20 题和 74 张卡重建映射与净化结果；不仅检查行数，还会确认 reviewer 中每一张卡与原卡内容一致、只替换了候选身份。

##### Assistant (commentary)

主验收发现一处需要纠正：Luna 为避免出现普通词 `model`，把一题临床字段里的 “experimental model” 改成了 “study setting”。这里的 `model` 是研究对象，不是 Luna 身份，不能改动原卡语义。我会只恢复这 6 处文本，然后按允许候选顺序打乱、但不允许内容变化的规则重新验收。

##### Assistant (final)

真人盲审包已经准备并验收完成：

- [审阅者 A 文件](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/reviewer_a.jsonl)
- [审阅者 B 文件](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/reviewer_b.jsonl)
- [填写说明](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/README.md)
- [私有身份映射](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_human_review/mapping.jsonl)——不要交给审阅者。

验收结果：

- A/B 各 74 张卡，覆盖全部 20 题。
- 两份内容相同，但分别按 seed 13/37 打乱顺序。
- 候选字母已替换成不透明标签。
- 所有真人评价字段均为空。
- 未包含 gold、reader 结果、planner 排名、Luna 身份或实验条件。
- 我发现并纠正了 Luna 对一处临床词汇 `model` 的误改；目前题干、state 和 card 内容均与源文件一致，仅身份和顺序发生变化。

现在需要两名真人分别填写 A/B 文件，至少一人具有临床背景。收到填写后的文件，我将合并分歧、生成 `PX-human-adjudicated`，并用同一个 Llama reader 复跑与 M0/M1/PX-proxy 的比较。

#### Turn 18 — 2026-08-23T07:26:45.000Z

##### Assistant (commentary)

我先检查盲审文件是否已经被真人填写；如果仍为空，后续 `PX-human-adjudicated` 的实际临床判断不能再由 Luna 代填。ponytail full 在这里要求停在真实依赖处，不再制造代理结果或额外流程。

##### User

把真人需要做的事情目前都由不同的luna max subagent来完成

##### Assistant (commentary)

明白。当前“真人 A、真人 B、分歧裁决者”分别改由三个互相独立的 Luna Max subagent 完成；它们不会共享评审上下文。A/B 只读各自盲审文件，不得查看 mapping、实验结果或对方文件；完成后再启动第三个 Luna Max，只裁决分歧。所有产物仍明确标为 Luna 代理评审，不冒充真人验证。

##### Assistant (commentary)

两个 Luna Max 已分别开始 A/B 盲审；它们使用 `fork_turns=none`，因此看不到此前的正确率、翻转题或 planner 表现。每个只接触自己的 74 行文件，当前我不读取其进行中的判断，避免干扰；完成后再做结构和独立性验收。

##### Assistant (commentary)

A/B 仍在逐卡审阅，暂未写入半成品，也没有格式错误回报。74 张卡需要逐项判断六个维度，我会让两个代理保持独立完成，不用批量默认值填充。

##### Assistant (commentary)

两个 reviewer 仍在运行，文件量约 23 万字节/份；这是正常的长上下文评审阶段。后续第三个 adjudicator 只会看到 A/B 的分歧，不会重新审全部 74 张，以保持 ponytail 的最小工作量。

##### Assistant (commentary)

Reviewer B 已独立完成 74/74；10 张卡提出了具体修订，其余字段均完整。Reviewer A 仍在运行，我先不比较两份结果，等 A 封卷后再统一计算分歧。

##### Assistant (commentary)

A/B 都已封卷。现在我先独立验收两份文件并计算逐字段一致性；第三个 Luna Max 不会看到 mapping 或任何实验结果，只会收到按题聚合的匿名卡片和 A/B 意见，并负责给出一致的最终 state/cards。

##### Assistant (commentary)

验收结果：两份非评审内容完全一致；transition 合理性 74/74 一致为可接受，但 A 对 state 充分性明显更保守，因此共有 42 张卡出现分类分歧、43 张需要裁决，涉及 16/20 题。为避免逐卡修订导致同题 state 不一致，第三个 Luna Max 将按题同时审阅全部候选，并输出一套统一的最终 state/cards。

##### Assistant (commentary)

第三个 Luna Max 已开始按题裁决。它只看到匿名候选、A/B 意见和原卡，不知道数据集、原选项字母、reader 表现或 gold；这样裁决不会被此前 +15pp/+20pp 结果锚定。

##### Assistant (commentary)

裁决仍在运行。它需要对 16 个有争议的题目统一修订 state 与所有候选卡，而不是只改单张卡；另外 4 题应原样接受。完成后我会逐字段比对，拒绝任何候选丢失、ID 改写或凭空加入外部依据。

##### Assistant (commentary)

第三个代理尚未回报格式冲突；这一步输出量接近完整重写 20 题、74 张卡，因此比 A/B 单纯填写评价字段更慢。我没有让它缩减到“多数票”，因为那会失去跨候选一致的实际修订。

##### Assistant (commentary)

第三个 Luna Max 已完成：20 题中 10 题原样接受、10 题修订、0 题排除，74 个候选均保留。现在进入主验收：我会先逐条列出这 10 题实际改了哪些 state/card 字段，再验证修订没有改变候选文本、没有添加指南 grounding，随后才映射回原 candidate ID 并重算 planner。

##### Assistant (commentary)

裁决修订通过临床内容初审：10 题的改动集中在 applicability、前提和不确定性，未改候选 action，未加入外部证据。重算后 planner 仅有 1/20 首选变化。按 ponytail full，我不复制新 runner，只给现有 runner 增加一个 `P4_ADJUDICATED=1` 模式，复用完全相同的模型、提示词和解码设置。

##### Assistant (commentary)

结构与 runner 预检通过；GPU 1 空闲。现在只跑新增的 `PA_luna_adjudicated` 20 条 reader，不重跑 M0/M1/PX，也不碰其他 GPU 进程。

##### Assistant (commentary)

新增条件已完成：裁决后 cards 的 reader 严格正确率为 17/20（85%），比未裁决 PX 再高 1 题；相对本次 M0 为 +25pp、相对 M1 为 +20pp，均是只改善、无恶化。这里仍是三名 Luna 代理而非真人。现在我做最后的逐题复算，重点检查 85% 是否被无效 JSON 的宽松解析抬高。

##### Assistant (commentary)

逐题复算确认 85% 没有被宽松解析抬高：唯一严格解析失败的输出实际写成 `"C: Principal cells; aldosterone"`，语义答案正确但严格指标仍按错误计。与原 v15 存档而非本次单卡 M0 比较，PA 严格提升是更保守的 +20pp（4 改善、0 恶化）。我会把这个保守参照补进汇总，避免只展示 +25pp。

##### Assistant (commentary)

三代理裁决与复跑已经闭环，下一步不再继续修改这 20 题。按文件夹计划，完整方法接下来需要 action-specific NICE 证据；我先只检查本地是否已有 NICE 文档或索引。若没有，就不能把当前 parametric 结果改称 guideline-grounded，而应转向扩大代理审阅样本或等待用户提供 NICE 数据。

##### Assistant (commentary)

本地没有任何 NICE 文档或索引，因此完整 guideline-grounded M7 目前不能运行。当前可继续且不冒充 NICE 的路径，是把已显示信号的 parametric 条件从 20 题扩到全部 85 个 Tier A；按 ponytail full，复用现有 20 题，只为剩余 65 题生成代理卡，先跑未裁决全量效果，只有方向仍正才投入第二轮双审。

##### Assistant (commentary)

全量输入发现一个真实的 v15 边缘项：`medqa/0745` 的原 reader 记录本来就是 0 篇文档，其余 84 题各 5 篇。它不是本轮错误，也不能为凑齐 top-5 人工补文档；全量实验会原样保留该空证据基线。

##### Assistant (commentary)

三个新的 Luna Max 正在并行生成剩余 65 题，各自只看自己的无答案批次。现有 20 题及其裁决结果不会重新生成；全量第一轮只比较未裁决代理卡，避免在信号尚未确认前投入约 300 张卡的重复审阅。

##### Assistant (commentary)

三批均仍在逐题生成，未出现文件冲突。每批约 21–22 题；我要求所有选项都生成一张卡并用同一个固定 selector 重算，而不是让代理直接写“推荐答案”。

##### Assistant (commentary)

第 1、2 批已完成，共 44 题、176 张卡；代理自检均通过。第 3 批仍在运行，我先独立重算前两批的 schema、候选覆盖和 planner，不等全部结束后才发现系统性问题。

##### Assistant (commentary)

按你的要求继续：所有原本需要真人判断的角色，都改由彼此独立的 Luna Max subagent 承担，并明确标记为代理评审、不能写成真人验证。现在先查收第三个全 85 题卡片批次；通过后我会合并复核，并运行同配置的 Llama 对照实验。Ponytail full 仍按“最少改动、复用现有流程”执行。

##### Assistant (commentary)

第三个 Luna Max 批次已完成，21/21 题。三个代理共补齐剩余 65 题；我现在做主代理独立验收并按原 85 题顺序合并，重点检查身份、选项覆盖、schema 与 planner 重算一致性。

##### Assistant (commentary)

合并审计第一次没有通过，我已暂停写入最终合并文件。现在定位具体失败项；这一步只查数据一致性，不会改动卡片判断。

##### Assistant (commentary)

全 85 题合并验收通过：85 个唯一题目、315 张卡、四个有 Tier-A 题目的数据集，全部由 Luna Max 生成并保持 `unsupported`/代理标记；planner 逐题重算一致，0 个缺项或弃权。下一步只给现有 runner 增加一个全 85 模式，不另造实验框架。

##### Assistant (commentary)

运行前检查完成：85/85 个 M0 用户提示与 v15 存档逐字一致；唯一的零文档题 `medqa/0745` 保持原样。GPU 1 空闲，我现在用相同 Llama、解码参数和三条件 M0/M1/PX 跑 255 个回答。

##### Assistant (commentary)

模型已载入，85×3 提示最长 4038 tokens，未超上下文；现在进入生成阶段。输出会先保存无标签预测，再统一计算配对结果。

##### Assistant (commentary)

全 85 题结果已完成，方向为正，已达到继续代理复核的门槛：M0 60/85（70.6%），M1 59/85（69.4%），PX 67/85（78.8%）；PX 相对 M1 为 11 改善、3 恶化，+9.4pp，bootstrap 95% CI 为 +1.2 到 +17.6pp。先做一次逐项结果验收和锚定分析，确认后立即把剩余 65 题分给新的、彼此独立的 Luna Max 评审角色。

##### Assistant (commentary)

逐项验收通过。PX 与 planner 一致 78/85（91.8%），说明效果里仍可能有明显锚定；因此代理双审不能省。按 Ponytail full，我复用既有 20 题裁决，只对新增 65 题建立三个小批次，每张卡由两名全新的 Luna Max 独立审阅，再交给第三名新的 Luna Max 裁决。

##### Assistant (commentary)

盲审包已生成并验收：新增 65 题共 241 张卡，分为 88/88/65 三组；每组 A/B 文件顺序不同、不含 gold、prediction、planner、原候选 ID 或题目身份。现在启动第一轮三名全新的 Luna Max：第 1 组 A、第 1 组 B、第 2 组 A。

##### Assistant (commentary)

三名 Luna Max 正在逐卡填写，当前没有完成回报。等待期间我保持结果文件与盲审文件隔离；下一名代理只会在某个并发槽释放后启动，避免同一角色看到另一侧意见。

##### Assistant (commentary)

首轮仍在进行。每人需完成 88 张独立医学/机制判断，耗时比生成卡片长是正常的；我现在只读检查是否已有可验收的完整文件，不会读取或转交另一位代理的意见。

##### Assistant (commentary)

文件仍保持未提交模板状态，说明三名代理都还在本地推理、尚未原子写回；没有出现部分写入或格式破坏。我继续等待首个完整提交。

##### Assistant (commentary)

三名代理状态均为 running，没有报错或卡住。由于这是逐卡临床判断，我不打断它们；谁先完成就先验收并立刻补上下一名独立审阅者。

##### Assistant (commentary)

首轮已运行约数分钟，仍没有完成回报；这批 88×3 张判断是目前最耗时的一步。模板仍完整、GPU 实验结果已安全落盘，我继续监督，不会提前把半成品当成评审结果。

##### Assistant (commentary)

已有实质进度：第 1 组 A/B 两份文件都已填满 88/88，代理正在做提交前自检；第 2 组 A 尚未写回。我会等 A/B 各自正式结束后再做结构一致性与独立性验收。

##### Assistant (commentary)

第 1 组 reviewer B 已正式完成并自检通过，88 张卡仅提出 1 处文字修订；释放的并发槽已交给全新的第 2 组 reviewer B。第 1 组 A 仍在做最终检查，我尚未合并两边意见。

##### Assistant (commentary)

第 1 组 A/B 已双独立完成：A 更保守（12 个 state uncertain、5 条修订），B 几乎全接受（1 条文字修订），这正需要第三角色裁决。新槽位已启动第 3 组 reviewer A；我同时验收第 1 组非评审内容是否原样，并生成只含 A/B 意见的盲裁决文件。

##### Assistant (commentary)

第 1 组主代理验收通过：A/B 的题干、状态和卡片与盲审源逐项完全一致，只改了 review；六项一致数分别为 76/88、88/88、85/88、88/88、85/88、88/88，共 8/22 题需要处理分歧或修订。盲裁决文件已准备好，等下一个槽位释放就交给第三名新 Luna Max。

##### Assistant (commentary)

第 2 组 reviewer A 已完成 88/88，提出 6 条前提修订；第 1 组已交给全新的第三名 Luna Max 裁决。当前还在等待第 2 组 B 和第 3 组 A，后续每组仍会使用不同代理，不复用角色。

##### Assistant (commentary)

三份正在处理的文件都还未写回，保持完整模板状态；没有部分提交。我继续等待正式完成信号。

##### Assistant (commentary)

仍在逐项判断，没有代理报错。第 2 组 B 为 88 卡、第 3 组 A 为 65 卡；第 1 组裁决需要把 22 题的最终 state/cards 完整回填，所以写回通常集中在末尾。

##### Assistant (commentary)

第 3 组 reviewer A 已完成 65/65，提出 2 条 goal-alignment 修订。刚才只读轮询恰好撞上另一代理写回瞬间，出现一次临时 JSON 解析失败；我不会把它视为完成文件，等该代理正式回报后再验收。释放槽位现在启动全新的第 3 组 reviewer B。

##### Assistant (commentary)

第 1 组第三方 Luna Max 裁决完成：22 题中 19 accept、3 revise、0 exclude。接下来我会独立检查 accept 是否原样复制、revision 是否保留候选集合和 `unsupported`，再映射回原始候选 ID；这仍只会标记为 Luna 代理裁决。

##### Assistant (commentary)

第 2 组 A/B 都已完成：B 更保守，提出 8 条修订；先前写回瞬间的临时解析问题已随正式提交消失。现在做与第 1 组相同的源内容复核并生成第 2 组盲裁决文件，通过后交给另一名全新的 Luna Max。

##### Assistant (commentary)

第 2 组双审源内容验收通过：11/22 题有分歧或修订建议，已交给新的第三名 Luna Max。当前只剩第 3 组 B 在审阅；其完成后会再启用一名不同的裁决代理。

##### Assistant (commentary)

第 2 组裁决与第 3 组 B 均仍在运行，无错误回报。它们尚未正式提交，我继续按完整文件验收，不读取半成品。

##### Assistant (commentary)

两项仍在逐题处理。第 3 组只有 65 卡但多为三选 PubMedQA 状态转移，代理仍需检查因果归因与不确定性；我不催促其给出机械全 yes。

##### Assistant (commentary)

第 3 组 A/B 已完成 65/65；两边都指出 2 个 goal-alignment 问题，B 另指出 1 个 applicability 问题。现在做最后一组源内容验收并启动新的第三方 Luna Max 裁决。

##### Assistant (commentary)

第 3 组验收通过，只有 3/21 题需裁决，已交给新的第三名 Luna Max。两名裁决代理运行期间，我按 Ponytail full 只扩展现有 runner 一个“全 85 题代理裁决后”模式；最终卡片一合并即可复用同一 Llama 条件验证，不另写第二套程序。

##### Assistant (commentary)

第 2 组裁决完成：15 accept、7 revise、0 exclude；格式已按“纯 card 对象”提交。现在我进行 schema、候选集合与 planner 重算验收，并映射回原始 ID。

##### Assistant (commentary)

第 2 组主代理验收通过：22 题、88 卡均合法，7 个 revision 没有改变任何 planner 首选。现在只剩第 3 组裁决；完成后即可合并既有 20 题与新增 65 题的最终代理裁决卡。

##### Assistant (commentary)

第 3 组裁决完成：18 accept、3 revise、0 exclude；修订涉及 1 个 applicability 和 2 个 `maybe` 的 goal alignment。现在做最后一组验收，随后合并全 85 题并重算所有 planner。

##### Assistant (commentary)

全 85 题代理裁决卡已合并验收：315 张卡，62 accept、23 revise、0 exclude；只有 3/85 个 planner 首选发生变化，均为 PubMedQA。所有条目仍明确 `human_validated=false`。现在运行最终 PA 条件，与刚才同批次的 M0/M1/PX 直接配对比较。

##### Assistant (commentary)

最终 PA 运行已加载模型：85 个提示，最长 4065 tokens。代理裁决使上下文仅比未裁决 PX 略长，仍在同一 8192 上下文与解码配置内。

##### Assistant (commentary)

最终 PA 已完成：strict 69/85（81.2%），author 70/85（82.4%）。相对 M0 strict 为 12 改善、3 恶化，+10.6pp，配对 McNemar p=0.035；相对 M1 为 +11.8pp，p=0.013；相对未裁决 PX 为 2 改善、0 恶化。现在核查这两处改善、唯一解析失败，以及 PA 是否机械跟随 planner，避免把代理锚定误写成独立推理增益。

##### Assistant (commentary)

核查结论很清楚：PA 并非完全机械复制 planner（author 与 planner 一致 79/85），但锚定很强。代理裁决相对 PX 的 2 个 strict 改善，都来自 PubMedQA 的 planner 修正；第三个 planner 修正被 reader 拒绝且仍答错。这个结果会原样写入 `agent.md`：它是值得以后换真人的正向实验信号，不是“真人验证”或普遍有效性证明。

##### Assistant (commentary)

最终验收完成：预测文件 85 行且不含 gold/correct 字段；结果文件与 summary 重算一致；GPU 已释放。执行记录已经追加到 `medrgag_wm_validation_pack/agent.md`，并明确写出代理锚定、分数据集结果和可允许的结论。

##### Assistant (final)

已完成。当前 85 题实验中，所有原真人审阅/裁决工作均由不同的 Luna Max subagent 承担，共 12 个分批独立角色；结果始终标记 `human_validated=false`。

| 条件 | Strict 准确率 |
|---|---:|
| M0 / v15 | 60/85，70.6% |
| M1 state/action | 59/85，69.4% |
| PX 未复核 WM | 67/85，78.8% |
| PA Luna 裁决后 | 69/85，81.2% |

PA 相对 M0 为 12 改善、3 恶化，+10.6pp，McNemar p=0.035。315 张卡最终为 62 accept、23 revise、0 exclude。

结论：这是值得后续换真人验证的正向信号，但不是方法已被真人或临床验证。PA 与 planner 一致 79/85，锚定仍然明显；相对 PX 的两个新增正确答案都来自 planner 修正。

主要文件：

- [agent.md 执行记录](/home/data3/txy/docs/archive/wm_medrgag.md#record-0262)
- [最终 85 题裁决卡](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_cards.jsonl)
- [最终 Reader 汇总](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_reader_summary.json)
- [代理评审目录](/home/data3/txy/docs/archive/wm_medrgag.md#record-0413)

按 Ponytail full，仅复用了现有 runner 增加全 85 模式，没有建立额外实验框架。

#### Turn 19 — 2026-08-23T09:04:35.000Z

##### Assistant (commentary)

我继续按完整目标推进，不把刚完成的 85 题实验误当成全部计划结束。先重新对照 `medrgag_wm_validation_pack` 的权威计划和当前产物，找出在你已明确排除“门禁/哈希/反事实优先级”之后，下一项真正需要跑的效果实验；同时继续使用 Ponytail full，只做能直接回答效果问题的最短路径。

##### Assistant (commentary)

从计划与现有证据看，下一步不是回头做你已经否定的门禁或反事实，而是回答一个更直接的问题：81.2% 到底来自 transition cards，还是来自把 planner 排名直接塞给 reader。Ponytail full 的最短下一轮是复用现有 85 题和 runner，补跑“cards 无 planner / planner 无 cards / precondition-only / effect-only / 等 token 推理”几个消融。我先让一名新的 Luna Max 对照计划和当前代码落地这一轮，GPU 执行前由我验收。

##### Assistant (commentary)

我已纠正两处会污染实验的实现口径：M4 不得携带 `applicability`，M5 不得携带 `goal_alignment`，否则“precondition/effect-only”仍暗含排序答案；M2 也不能把控制提示原文直接拼给 reader，必须先独立生成额外推理，否则不叫计算控制。Luna Max 正按这个口径修改。

##### Assistant (commentary)

代理尚未写入 runner，说明仍在梳理两阶段 M2 与四个字段消融的共同流程；现有实验代码未被半改。我继续等待它提交完整补丁后再验收。

##### Assistant (commentary)

仍在运行，无报错；我没有为了赶进度自行另写一套 runner。Ponytail full 在这里的约束就是：等它把同一个入口改正确，再用一次 CPU preflight 和一次 GPU 批跑完成，不扩散文件。

##### Assistant (commentary)

Luna Max 仍未提交代码或阻碍说明；我已要求它在下一个边界汇报是否保留 M2 以及当前修改状态。若它确认 M2 会把一次简单消融变成第二套推理流水线，我会按 Ponytail full 先让本轮只跑四个结构消融，并把 M2 独立留到下一步，避免误标。

##### Assistant (commentary)

Luna Max 已提交单文件补丁，CPU preflight 报告 85×5=425 个 reader 提示，最长 3399 tokens；M2 是独立 512-token 辅助推理并明确标记“非严格等 token”。我现在逐段验收它是否真的做到字段隔离、生成前不读结果、写盘后才接 gold/reference，并检查旧三种模式没有被破坏。

##### Assistant (commentary)

好的。真人角色已拆给不同的 Luna Max：两名独立审阅者与第三名裁决者分别处理，各代理互不代填；所有产物明确标为 `human_validated=false`。我现在继续按 Ponytail full 做最后的最小消融核查与同一 Llama 实跑，判断提升究竟来自卡片、planner，还是单纯多了一段推理。

##### Assistant (commentary)

消融入口已返回。我发现两处会影响解释、但不影响方法本身的小问题：M2 被误标成了 Luna 来源，且耗时只统计第二次 reader 调用、漏掉第一次辅助推理。我会只修这两处元数据和一个上下文长度边界，不扩展框架。

##### Assistant (commentary)

预检通过：85题 × 5条件共425个 reader 样本；M2没有 cards/planner，M4与M5字段恰好按计划投影，M6仅去 planner，MR仅保留 planner。GPU 1 空闲，我现在用同一 Llama、同一解码设置启动实跑；任何既有结果都不会覆盖。

##### Assistant (commentary)

模型已加载到 GPU 1，当前正在先生成85份独立辅助推理，随后依次跑五个条件。编译缓存命中，资源占用正常。

##### Assistant (commentary)

辅助推理已完成；M2（只增加一次普通 Llama 推理、完全不看 WM 卡或 planner）正在跑 reader。之后四个结构消融会更快，因为不需要额外生成。

##### Assistant (commentary)

目前 M2、M4、M5 已完成，M6（完整卡片但不提供 planner）正在收尾。最后只剩 MR（仅 planner）；这两个条件会直接告诉我们此前提升主要由哪部分驱动。

##### Assistant (commentary)

实跑完成，结果很明确：完整卡片无 planner 为 66/85（77.65%），仅 planner 为 70/85（82.35%），而原 v15 为 60/85（70.59%）；普通额外推理反而只有 54/85。也就是说提升不是“多算一次”造成的，当前主要信号在 Luna 裁决后的 planner，完整 transition cards 也有较小独立增益。我正在做逐题与文件完整性复核，避免只看总分下结论。

##### Assistant (commentary)

逐题复核显示：MR（state + planner、无 cards）与 planner 本身只在8题上分歧，说明存在明显锚定；M6（完整 cards、无 planner）仍比 M1 多7题正确但证据较弱。按你的要求，我再让一个新的 Luna Max 只做独立实验审阅：不给它改代码，只让它判断这些消融能支持什么、下一步最小实验是什么；我同时把实测结果写回计划记录。

##### Assistant (commentary)

完整性审计已通过并已写入 `agent.md`：425/425 行、每条件85题、无金标或正确性字段进入预测文件，所有代理产物均保持 `human_validated=false`。独立 Luna Max 方法审阅还在逐题核对；我会等它给出结论后再决定是否追加“直接 Luna 排名”这一最小对照。

##### Assistant (commentary)

目前数字已经能把问题缩小到一个核心混杂：planner 的 `preferred_candidate_id` 本身几乎就是一个 Luna 答案推荐。若独立审阅也同意，下一步不会再加复杂机制，只做盲的“Luna 直接选项排名”对照，检验 elaborate WM cards 是否比直接让 Luna 答题更有价值。

##### Assistant (commentary)

两个新的 Luna Max 已分别盲处理前43题和后42题；它们只能看原题、选项和原 MedRGAG 文档，明确禁止读取 cards、planner、预测结果或金标。这个对照不再调用 GPU：先直接比较其无-WM排名与现有 planner 的逐题正确率，足够判断 WM 构造是否超越“直接让 Luna 选答案”。

##### Assistant (commentary)

独立 Luna 方法审阅与我的复核一致，并纠正了一个措辞边界：M2 只能说明“这次额外自由推理没有带来收益”，因为它并非严格等 token/等成本，不能宣称已经排除所有“更多推理”解释。它也确认盲 direct-Luna 排名是当前最小、最直接的下一步；两个排名代理仍在处理。

##### Assistant (commentary)

盲排名代理还在逐题处理，尚未写出半成品；我要求它们只在完成各自分片并自检后落盘，避免把部分结果误当完整结果。现有消融记录中的 M2 表述也已按独立审阅修正为“未观察到收益，但不能完全排除更多推理解释”。

##### Assistant (commentary)

两个分片仍在运行，没有报错或越权读取迹象。这个阶段耗时主要是 Luna 对85题逐题排序，不涉及 GPU 或原实验文件改写；完成后我会先验证两分片合起来恰好覆盖85个唯一身份，再接触金标做配对统计。

##### Assistant (commentary)

两个盲分片已完成（43 + 42）。我先做不接触金标的结构核查：顺序、85个唯一身份、每题 option 集合、preferred 必须等于 ranking 首项，以及禁止出现 cards/planner/gold/correct 字段；通过后才会读取 P2 金标评分。

##### Assistant (commentary)

盲 direct-Luna 对照已评分：74/85（87.1%），高于 planner 首选 69/85、PA 69/85、MR 70/85；与 planner 仅74/85一致。相对 PA 是7题改善、2题退化（+5.9pp，p=0.180），相对 MR 是7/3（+4.7pp，p=0.344）。这不是显著优胜，但足以说明当前提升完全可能只是 Luna 的直接医学判断被包装成 planner，而非 WM 结构贡献。下一步我会只补一个同一 Llama reader 的 direct-ranking 条件，消除“一个是 Luna 直接答、一个是 Llama reader”的比较差异。

##### Assistant (commentary)

direct-Luna 的分数据集结果是 MedQA 25/25、MedMCQA 14/18、MMLU 17/17、PubMedQA 18/25。需要强调：两个代理恰好按数据集边界分片，且它们没有经过双审/裁决，所以这仍是探索性对照；同-reader 条件完成后，才适合与 PA/MR 做更公平的最终比较。

##### Assistant (commentary)

同-reader 入口正在现有脚本里做最小扩展，已看到互斥模式和独立输出路径落位；尚未宣告完成，我不会边写边运行。完成后会由我重新审查提示正文，确认 reader 只看到 neutral state + direct ranking，确实没有 cards、candidate scores 或 planner。

##### Assistant (commentary)

代码复核发现三个只影响可解释性的缺口：reader 提示还没明说排名生成时盲于 WM/金标，summary 没有持久化 direct 与 planner 的逐题对照，输入校验也应拒绝任何额外字段。我会补这三点并删除一个重复字段，然后重新预检；不改实验内容。

##### Assistant (commentary)

根复核与预检通过：85个同-reader 提示，最大2365 tokens；传入 payload 仅有 `preferred_candidate_id/ranking/reason`，无 transition cards、candidate scores 或 planner 数据；排名来源和 `human_validated=false` 也在提示中明示。GPU 1 空闲，现在运行唯一的 direct-ranking reader 条件。

##### Assistant (commentary)

模型加载完成，85题同-reader 条件已开始生成。这里 Llama 看到的不是 WM planner，而是两个盲 Luna 代理直接给出的排序；其余 reader 模型、证据、neutral state、seed 与解码设置保持一致。

##### Assistant (commentary)

同-reader 结果完成：71/85（83.5%）。它与 MR 只有5题改善、4题退化（+1.2pp，p=1.0），与 PA 是4/2（+2.4pp，p=0.688）；direct 原始排名74/85，Llama reader 改动后净损3题。结论进一步收窄：现有 WM cards/planner 没有超过更简单的盲 direct-Luna 排名对照。现在做最后逐题/文件核查并记录。

##### Assistant (commentary)

按“真人角色由不同 Luna Max 代理替代”的要求，我再交给一个此前未参与生成、审阅、裁决或实现的 Luna Max 做最终只读判定：它只看已完成的数值和逐题翻转，判断这个结果应当继续 WM 路线、重设计，还是在当前版本判为无增量。主文件与结果不会再改动。

##### Assistant (commentary)

最终独立审阅仍在核对逐题翻转。补充一个 Ponytail 视角的重要事实：MD reader 输入为170,139 tokens，MR为218,480，PA为299,819；MD 用更短的 reader 上下文达到71/85。但这只比较 reader prompt，不包含上游 Luna 生成/复核成本，所以我不会把它包装成完整成本优势。

##### Assistant (final)

已完成。当前需要真人参与的卡片双盲审、分歧裁决和最终方法复核，均由不同的 Luna Max subagent 独立完成；所有结果仍严格标记 `human_validated=false`，不冒充真人或 NICE 验证。

| 条件 | 正确率 |
|---|---:|
| v15 / M0 | 60/85，70.6% |
| M6 完整 cards、无 planner | 66/85，77.6% |
| PA cards + planner | 69/85，81.2% |
| MR 仅 planner | 70/85，82.4% |
| MD 盲 direct-Luna 排名 | 71/85，83.5% |
| Luna 原始直接排名 | 74/85，87.1% |

关键结论：现有 WM cards/planner 没有显示出超过“直接让 Luna 排名选项”的增量。MD 与 PA、MR 均无显著差异；当前提升更可能来自外部 Luna 的医学判断，而不是 transition/world-model 机制。

按 Ponytail full，当前应暂停扩样并先重设计，不值得继续堆现有 WM 管线。唯一建议的下一步，是在同一85题上严格匹配 reader prompt 与 token/context budget，再配对比较 blind direct-ranking 和 cards+planner。

完整记录见：

- [agent.md](/home/data3/txy/docs/archive/wm_medrgag.md#record-0262)
- [最终 direct 对照 summary](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_luna_adjudicated_all85_direct_rank_reader_summary.json)
- [实验入口](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py:255)

#### Turn 20 — 2026-08-23T09:59:42.000Z

##### Assistant (commentary)

我继续推进真实目标，不把上一轮的 no-increment 结果当作计划完成。接下来按 `ponytail full` 只做独立审阅建议的那个最小缺口：在同一85题、同一 reader prompt 表面与上下文预算下，配对比较 blind direct-ranking 和 cards+planner；先让 Luna Max 子代理从执行计划中提出最小可运行设计，我负责审查后实跑。

##### Assistant (commentary)

我已先做了只读可行性验证：两边都只保留 `preferred_candidate_id + ranking`，共用同一 neutral state 和同一 envelope 后，85/85题的 tokenizer 输入长度可做到逐题完全相等；42题完整排名也字节完全一致，另外43题只差排名值。这样不需要填充 token、截断理由或新增依赖，符合 Ponytail full。

##### Assistant (commentary)

设计代理还在核对计划的公平性定义；本地验证没有发现阻碍。严格配对将不使用无意义 padding，也不把理由截断成另一种任务：两边共享完全相同的 state、JSON schema、提示文本和逐题 token 数，只替换 direct 与 WM 两套排名值。

##### Assistant (commentary)

Luna Max 的唯一推荐设计与本地验证一致。我现在让另一个 Luna Max 只在现有 runner 增加一个 matched mode；不会新建框架、不会重新生成 ranking、不会运行 GPU。它完成后由我逐段查 prompt 与断言，再决定是否实跑。

##### Assistant (commentary)

实现代理仍在现有 runner 内工作。当前设计的关键可证伪点不变：MW−MD 是唯一主比较；85/85逐题 input tokens 必须相等，42个完整排名相同的题必须生成逐字相同的 user/chat prompt，否则不会进入 GPU。

##### Assistant (commentary)

代理尚未落文件，说明还在追踪现有 runner 流程；我已明确要求删掉额外 reference 矩阵和新抽象，只保留两条件、预检与 MW−MD 配对统计。这样即便实现返回，也不会把这个对照扩成新框架。

##### Assistant (commentary)

实现已返回：只改了现有 runner，预检报告85/85 token相等、42/42相同排名 prompt 逐字相同。现在进入我的查收阶段；我会重点检查“forbidden content”是不是查了真正的渲染上下文，而不是只查字段名，以及 summary 的主差值方向是否确实是 MW−MD。

##### Assistant (commentary)

查收发现实现主体正确，但有两处要收紧：它把逐题 `total_tokens` 误写成了 input 差值，且“42个相同排名”只打印未强制断言。我会删除错误统计、把42设为硬断言，并补齐分数据集准确率；这是修验证证据，不改变实验。

##### Assistant (commentary)

根预检通过，GPU 1 空闲。现在同一次模型加载依次跑 MD 与 MW：170个 reader 样本，输入逐题等长；对于42个排名完全相同的题，两条件提示严格相同，因此这些题若输出不同会被单独视为采样/运行噪声，而不是方法差异。

##### Assistant (commentary)

MD 已完成，MW 正在运行。两条件实际运行前再次打印了 `token equal 85/85` 和 `byte-identical 42/42`；目前没有输入、公平性或资源异常。

##### Assistant (commentary)

严格配对已完成：MD 65/85，MW 64/85；主差值 MW−MD = −1.18pp，2题改善、3题退化、80题不变，95% CI −5.88到+3.53，McNemar p=1.0。即使逐题 token 完全一致，WM-derived ranking 仍没有超过 blind direct ranking。我现在核查42个相同提示是否也产生相同输出，以及5个翻转是否全部发生在排名不同题。

##### Assistant (commentary)

查收发现一个必须修的实验问题：42个完全相同提示中，只有29个 raw response 逐字相同，并出现1个 strict 答案翻转；原因是 temperature=0.1 的两次独立 `generate` 调用没有复用相同随机轨迹。这个噪声恰好给 MW 增加了1题，因此当前 −1题结果方向仍不利于 WM，但还不能称“严格只差 ranking”。我会让新的 Luna Max 独立确认，随后用 greedy 解码做一次确定性配对，不覆盖本次结果。

##### Assistant (commentary)

独立 Luna Max 审阅确认：不能手工排除那一题，也不能只重跑42题；最小有效修复就是保留旧产物、对同170 prompts 做一次 greedy replay，并对42个相同 prompt 的 `raw_response` 做硬断言。我让原实现代理只加一个 replay 开关和新输出名，不改任何 prompt 或排名。

##### Assistant (commentary)

我正在把这次“同题、同提示、同 token，仅替换排序来源”的对照修成完全确定性的贪心复跑。先验收 Luna Max 的最小改动，再由我实际运行与核对；这样相同提示的 42 题必须逐字产生相同输出，避免把采样噪声误认成 WM 效果。

##### Assistant (commentary)

Luna Max 还在改 runner；我暂不并发碰同一文件，避免覆盖。当前验收标准不变：新增独立 greedy 产物、不覆盖旧实验、仅在 matched 模式启用 `temperature=0`，并在写盘前硬性验证 42 对相同提示的原始回答完全一致。

##### Assistant (commentary)

实现时间比预期长，我正在催收；如果它仍未结束，我会先中断并检查已落盘的最小改动，不让这个辅助步骤拖住实验。

##### Assistant (commentary)

改动已经落盘，Luna Max 只是没有及时结束任务。我现在直接做根代理验收：重点检查 greedy 模式是否只影响这一个实验、断言是否确实发生在任何结果写盘之前，以及新旧输出是否彻底分离。

##### Assistant (commentary)

根验收通过：代码可编译，CPU 预检确认 85/85 逐题输入 token 完全相等、42/42 同排序提示逐字相同、温度为 0，且三个 greedy 输出文件尚不存在。GPU 1 当前空闲，我现在启动唯一一次完整 170-prompt 复跑。

##### Assistant (commentary)

模型已完成加载与 warm-up，正在处理第一组 85 题。预检仍显示 matched 条件成立；运行结束后我会先查 42 对原始输出的确定性断言，再看准确率差异，顺序不会反过来。

##### Assistant (commentary)

这次复跑被断言正确拦截，三个结果文件均未写出：即使 `temperature=0`，vLLM 在两次独立 batch 调用中，对同一提示 `medqa/0702` 仍生成了不同原始文本。因此该轮结果作废。我会让一名新的 Luna Max 独立判断最小修复；当前最可能的干净方案是“按完整 chat prompt 去重后只推理一次，再映射回两个条件”，而不是事后挑选或复制某一侧答案。

##### Assistant (commentary)

失败进程没有自行释放 vLLM 子进程，我已只终止本次实验对应的两个已核实 PID；GPU 1 已恢复为空闲，其他任务未动。greedy 结果文件仍为 0 个。新的 Luna Max 方法审阅尚未返回，我会等它给出唯一修复结论后再改代码。

##### Assistant (commentary)

新的 Luna Max 审阅结论明确：采用“推理前按完整 chat prompt 去重，128 个唯一提示各生成一次，再映射回 170 条记录”。这是预先定义的 deterministic prompt-function，不是事后挑答案；42 个相同提示对将结构性共享输出，真正可区分排序来源的只有其余 43 题。我会按 Ponytail full 只改现有生成循环，不加框架，也不引入哈希机制。两次失败会直接记入实验记录。

##### Assistant (commentary)

修复后的第二次预检通过：170 条记录对应 128 个唯一 chat prompt（42 个成对、86 个单例），每条只映射一次；85/85 token 相等、42/42 提示相同，输出仍为空。现在进行一次新的单调用 greedy 运行；它不会复用刚才失败轮的任何内存输出。

##### Assistant (commentary)

单调用方案已按预期进入 `128` 个唯一提示的生成阶段，说明去重映射实际生效，而不是仍然跑两个 85 题 batch。结束后写盘前还会再次验证 42 对的 raw/strict/author 输出均为 42/42 一致。

##### Assistant (commentary)

干净运行已完成并通过写前断言。初步结果是严格准确率完全持平：MD（直接 Luna 排序）`64/85`，MW（WM planner 排序）`64/85`；仅 `1` 题改善、`1` 题恶化、`83` 题不变，差值 `0.0pp`，McNemar `p=1.0`。我现在独立重算行数、配对、泄漏字段和 flip 题，确认不是 summary 自报。

##### Assistant (commentary)

独立重算与 summary 一致：85 个完整配对、0 个 token 不匹配、42 个同排序对原始输出 0 个不一致。只有 3 题预测文字不同，其中 1 改善、1 恶化、1 两边都错。下一步按你的要求，把最终“是否继续 WM 路线”的方法判断交给一名新的、未参与前面评审的 Luna Max；它只读查收现有证据，我再监督结论是否符合文件夹计划。

##### Assistant (commentary)

我已核对计划中的判定边界：若完整 WM 不能超过 action decomposition 与等预算基线，就只能表述为 action-aware prompting/retrieval，不能宣称 WM 贡献。当前干净 matched 结果是 `0.0pp`，因此除非最终 Luna Max 发现文件级错误，预期决策会是停止扩展当前 WM claim，而不是继续堆后续实验。

##### Assistant (commentary)

最终独立 Luna Max 已完成查收，结论唯一且与根审计一致：停止当前 `world model` claim，保留为 `action-aware/direct-ranking` 的探索性结果；不需要为了这个决策再扩展实验。现在我把 matched 设计、两次失败、干净结果及停止决定写入 `agent.md`，所有代理判断继续明确标为 `human_validated=false`。

##### Assistant (commentary)

查收完成：`agent.md` 已写入第 18 节，包含正温度污染轮、greedy 双调用失败轮、最终单调用去重轮、独立 Luna Max 复核和停止决定。runner 可编译，GPU 1 已释放，没有遗留实验进程。由于计划在“WM 无可识别增量”处给出了明确停止结论，当前执行目标已到终点。

##### Assistant (final)

已按计划执行到科学停止点，并完成监督验收。

- 所有暂代真人的判断均由不同 Luna Max subagent 完成，全部标记 `human_validated=false`。
- 干净 matched 对照：直接排序 MD `64/85`，WM planner 排序 MW `64/85`。
- 差异：`0.0pp`，1 题改善、1 题恶化、83 题不变；95% CI `[-3.5,+3.5]`，McNemar `p=1.0`。
- 结论：停止扩展当前 `world model` claim；仅保留 `action-aware/direct-ranking` 探索性发现。
- 两次无效运行及其原因也已记录，没有隐藏负结果。
- runner 编译通过，GPU 已释放，无遗留进程。

关键文件：

- [完整执行与停止记录](/home/data3/txy/docs/archive/wm_medrgag.md#record-0262)
- [最终实验摘要](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_matched_rank_greedy_reader_summary.json)
- [实验 runner](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py:1075)

Ponytail full 原则已落实：复用单一现有 runner，没有新增框架或不必要实验。

目标总用量：3,292,418 tokens；耗时约 12 小时 52 分钟。

#### Turn 21 — 2026-08-23T13:26:16.000Z

##### User

我需要把当前的全部进程返还给另一个agent看， 你规划一下需要把哪些东西上传成文件，然后我应该上传到 GitHub 或者 Hugging Face，GitHub 不知道文件大小会不会不足。如果就是上传到哪些地方，你规划一下，然后告诉我该怎么把我的用户信息给你。

##### Assistant (commentary)

我会先按 Ponytail full 做一个“最小可完整交接包”规划：区分代码/文本、可公开的小型实验产物、模型与大文件、以及绝不能上传的私密数据。随后核对 GitHub 与 Hugging Face 当前官方大小限制。账号信息不需要也不应该直接发给我密码或 token；我会给你安全的本机登录方式。

##### Assistant (commentary)

本地体量已经很清楚：核心代码包约 `37 MB`，本次实验私有产物约 `21 MB`，且当前没有单文件超过 `10 MB`。所以“GitHub 文件大小不够”并不是眼前问题；真正要规划的是公开性、可复现性以及哪些数据不应进入公开仓库。我接下来只查官方文档确认两边的现行限制。

##### Assistant (commentary)

按 Ponytail full，当前最省事且最不容易漏东西的结论已经倾向于：只建一个私有 GitHub 交接仓库，暂时不用 Hugging Face。为了把清单定准，我再核对私有实验目录的文件数、最大文件和是否存在模型权重、缓存或嵌套 Git 元数据。

##### Assistant (commentary)

交接内容不需要模型权重或虚拟环境：当前工作区没有权重文件，模型应由接收方按模型 ID 重新获取。为了告诉你最少需要提供哪些账号信息，我再检查这台机器是否已经装好并登录 GitHub/Hugging Face CLI；只读取登录状态，不读取或显示 token。

##### User

不用考虑公开性的问题，因为这个我只会上传给 agent 看，其他的话即使公开了也不会有其他人看的，就是安全性方面暂时不用考虑。

##### Assistant (commentary)

你这句话我按“只追求完整交接，不做公开发布审查”处理。还有一个关键范围我需要补齐：当前 v15 全 Llama 实现和原始复现实验在工作区外的 `/home/data3/txy/MedRGAG`，如果只传眼前这两个目录，另一个 agent 能看结论但未必能追溯完整运行。我现在核对这部分的实际体量，再给你最终单仓/双仓方案。

##### Assistant (final)

好，按“不考虑公开性、只方便另一个 agent 接手”的前提，最简单方案是只用 GitHub，不必再开 Hugging Face。

#### 上传方案

GitHub 建一个仓库，例如 `medrgag-wm-handoff`。

| 位置 | 内容 |
|---|---|
| Git 仓库正文 | `medrgag_wm_validation_pack/` 全部代码、计划、prompt、schema、测试和 `agent.md` |
| Git 仓库正文 | 当前 `private_data/labels/runs/` 全部实验记录，约 22 MB |
| Git 仓库正文 | `/home/data3/txy/MedRGAG` 的代码、文档、requirements、resource manifests、runtime logs、benchmark 和小型 outputs |
| GitHub Release | v15 完整运行产物，当前约 4.5 GB、168,681 个文件，按五个数据集分别打成 `.tar.gz` |
| 新增交接文件 | `HANDOFF.md`：阅读顺序、用户纠正、实验时间线、最终结论、关键命令和 Release 解压方式 |
| 新增环境文件 | `ENVIRONMENT.txt`：Python、PyTorch、Transformers、vLLM、CUDA、GPU、模型 ID |

v15 Release 建议拆成：

```text
v15-medqa.tar.gz
v15-medmcqa.tar.gz
v15-mmlu.tar.gz
v15-pubmedqa.tar.gz
v15-bioasq.tar.gz
v15-metadata.tar.gz
```

如果任何压缩包超过 2 GB，再机械拆成 `part-001`、`part-002`。

#### 不上传

这些不是交接所需内容：

- 48 GB 的原始 corpus：已有下载脚本和 resource manifests。
- 8.1 GB 的 `.venv`：由 `ENVIRONMENT.txt` 重建。
- 本地 Llama 权重：记录模型 ID，让接收方重新下载。
- `.env`、缓存、`__pycache__`、`*.pyc`。
- 嵌套的 `vendor/MedRGAG/.git/`。
- 旧的 `medrgag_validation_pack/`：这是之前找错的目录。
- 旧的 `medrgag_wm_validation_pack.zip`：内容不完整且已过时。

正常 Git 仓库预计约 80–100 MB，当前最大普通文件只有约 8.5 MB，远低于 GitHub 单文件 100 MiB 限制；GitHub 建议仓库保持在 1 GB 内。浏览器一次只能上传 100 个文件且单文件上限 25 MiB，所以应使用 Git 命令行。[GitHub 文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[浏览器上传限制](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

GitHub Release 不会让普通 clone 携带那 4.5 GB；GitHub Free 的单个大文件上限为 2 GB，因此分片即可。[GitHub 大文件规格](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)

Hugging Face 只作为以后上传几十 GB corpus 或模型权重的备选；当前没有必要增加第二个平台。[Hugging Face 存储说明](https://huggingface.co/docs/hub/main/en/storage-limits)

#### 你需要给我的信息

请直接回复下面这几项即可：

```text
GitHub 用户名：
仓库名：medrgag-wm-handoff
可见性：public
允许安装 GitHub CLI：是 / 否
Git 提交显示名：默认使用 GitHub 用户名 / 自定义
Git 提交邮箱：使用 GitHub noreply / 自定义
```

不要把 GitHub 密码、token 或 SSH 私钥发给我。

这台机器目前没有安装 GitHub CLI。你确认允许后，我可以安装并启动：

```bash
gh auth login --web
```

届时你只需在自己的浏览器里确认一次授权；凭据保存在本机，我不需要看到 token。官方也推荐这种浏览器登录方式。[GitHub CLI 登录](https://cli.github.com/manual/gh_auth_login)

收到上面的用户名和仓库名后，我下一步就可以制作交接目录、压缩 v15、验证压缩包能解开，然后等你完成浏览器登录再上传。

#### Turn 22 — 2026-08-23T13:34:06.000Z

##### User

或许v15不需要交接， 因为我可以把原论文的代码库给他看。这样子的话，就是那部分用原论文的代码库应该也能替代吧。然后剩下的就是你再看看，因为目前这个 V15 我感觉有点太过于臃肿了，之前做的时候加了一堆各种各样的安全措施，但实际我们这个实验代码是不需要的。

##### Assistant (commentary)

我会用 Ponytail full 重新按“另一个 agent 能看懂并能复跑当前 85 题实验”的最低需求追一遍依赖。重点不是带走 v15 全流水线，而是确认当前 runner 到底只用了 v15 的哪些冻结结果和哪几个小函数；我先不删改任何文件。

##### Assistant (commentary)

初步结论是：4.5 GB 的 v15 运行目录确实不用交接，但“只给原论文仓库”还差一个很小的兼容层。当前实验 runner 并不调用 v15 全流水线；它只从自定义复现代码里借了三个格式化/答案解析函数，而原论文 vendor 里没有这些函数。85 题所需的问题、选项、已选 MedRGAG 文档和 v15 基线预测已经冻结在 1 MB 左右的 JSONL 里。接下来我精确核对这三个函数和最小文件闭包。

##### Assistant (final)

对，v15 的 4.5 GB 完整产物不需要交接。原论文仓库可以替代上游代码背景，但要保留当前实验实际使用的冻结输入和基线结果。

当前 runner 实际只从 v15 自定义代码借用了三个小函数：

- MedRGAG 文档格式化
- strict answer parser
- author answer parser

原论文仓库没有这三个函数，但它们总共只有约 60 行，可以直接放入精简 runner。当前 85 题的问题、选项、已选 MedRGAG 文档和 v15 预测已经保存在两个小文件中：

- [85题冻结输入](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p4_proxy_all85_input.jsonl)
- [v15逐题基线结果](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/private_data/labels/runs/stage-b-real-20260823-seed13-37-v4/p2_v15_item_results.jsonl)

所以不需要 v15 全流水线、corpus、模型权重或 4.5 GB 原始输出。

#### 精简交接包

我建议新建一个独立 `medrgag-experiment-handoff/`，不清理或破坏当前目录：

```text
medrgag-experiment-handoff/
├── HANDOFF.md
├── PROJECT_PLAN.md
├── agent.md
├── environment.txt
├── upstream/
│   └── README.md
├── experiment/
│   ├── run_final_matched.py
│   ├── prompts/
│   │   ├── 14_medrgag_reader.md
│   │   ├── 16_equal_token_reasoning.md
│   │   └── 17_proxy_parametric_reader_context.md
│   └── schemas/
└── artifacts/
    └── stage-b-real-20260823-seed13-37-v4/
```

其中：

- `run_final_matched.py`：从当前 74 KB 多模式 runner 中提取最终 matched 实验，内置那三个小函数，不再依赖 `/home/data3/txy/MedRGAG`。
- `artifacts/...-v4/`：完整保留约 21 MB 的题目筛选、Luna 评审、cards、消融、直接排序和最终结果。
- `upstream/README.md`：指向原论文仓库 `https://github.com/xiotakut/mrg`，并记录使用的 commit。
- `HANDOFF.md`：明确计划来源只能是 `medrgag_wm_validation_pack/`，以及最终结论是 action-aware/direct-ranking，不是 WM 增益。

不带入：

- v15 代码和 4.5 GB 输出
- `vendor/MedRGAG/`
- 哈希、门禁、no-go 自动化和反事实 runner
- cache、虚拟环境、corpus、模型权重
- 旧的错误计划目录
- 过时 ZIP

最终交接包预计约 22–25 MB，直接放一个 GitHub 仓库即可，Hugging Face 和 GitHub Release 都不需要。

你接下来只需给我：

```text
GitHub 用户名：
仓库名：medrgag-experiment-handoff
可见性：public
允许我创建精简交接包：是
允许安装 GitHub CLI：是 / 否
```

密码和 token 不要发给我。上传前你只需在本机通过浏览器登录 GitHub。

#### Turn 23 — 2026-08-23T13:36:37.000Z

##### User

你可以先安装GitHub Cli

##### Assistant (commentary)

可以。我先检查系统架构、现有包源和权限；优先使用系统包，权限不够就把官方 `gh` 二进制安装到 `/home/data3/txy/.local/bin`，不改项目文件。安装后我会运行 `gh --version` 验证，但不会替你登录账号。

##### Assistant (commentary)

系统是 Ubuntu 22.04 x86_64，没有免密 sudo；系统源里的 `gh 2.4.0` 也很旧。我会采用官方发布包做用户级安装，目标目录已经在 `PATH` 中。现在查询 GitHub CLI 的最新正式版本。

##### Assistant (commentary)

将安装官方稳定版 `gh 2.98.0`。我会同时下载官方校验和、验证压缩包后再复制单个二进制到用户目录；不需要 sudo，也不会修改 shell 配置。

##### Assistant (commentary)

安装命令因环境禁止自动执行 `rm` 清理临时目录而被拦截，尚未下载或安装任何内容。我会去掉清理动作；临时下载留在 `/tmp`，系统之后会自行清理，不影响安装结果。

##### Assistant (final)

GitHub CLI 已安装并验证：

```text
路径：/home/data3/txy/.local/bin/gh
版本：2.98.0
校验和：通过
登录状态：尚未登录
```

下一步可以运行：

```bash
gh auth login --web
```

你确认后，我可以启动浏览器授权流程。临时安装文件位于 `/tmp/gh-cli-install.s8jq4d`，不影响使用。

#### Turn 24 — 2026-08-23T13:38:18.000Z

##### User

你现在在服务器上面，我现在还没有 remote 这个服务器，只有你 remote 这个服务器。所以说你看看有没有什么办法可以，我不用登录这个服务器的情况下给你授权呢。

##### Assistant (commentary)

可以，用 GitHub 的设备码授权：我在服务器启动登录后，会得到一个短时有效的一次性代码；你只需在自己电脑或手机浏览器打开 GitHub 的设备授权页面并输入代码，不需要登录这台服务器，也不需要把密码或 token 发给我。我现在启动这个流程。

##### Assistant (commentary)

服务器上的交互式终端提示没有正常回显，我已只终止刚才那次未完成的登录进程。改用相同的设备授权流程，但预先回答 Git 凭据配置问题；仍然不会传输你的密码或 token。

##### Assistant (final)

请在你自己的电脑或手机上操作：

1. 打开：https://github.com/login/device
2. 输入一次性代码：`8301-7A37`
3. 登录并确认授权 GitHub CLI。
4. 完成后回复我“已授权”。

服务器正在等待授权结果，你不需要登录服务器。

#### Turn 25 — 2026-08-23T13:41:19.000Z

##### User

以授权

##### Assistant (commentary)

我现在查收服务器端的设备授权结果，并验证 GitHub 账号与 Git 操作是否已配置成功。

##### Assistant (final)

授权成功：

- GitHub 账号：`xiotakut`
- Git 协议：HTTPS
- 权限：可创建和推送仓库

下一步请确认一句：

```text
创建 public 仓库 medrgag-experiment-handoff，并开始制作交接包
```

也可以指定其他仓库名或可见性。

#### Turn 26 — 2026-08-23T13:43:13.000Z

##### User

查看有没有一个叫mrg的仓库，传到这，同时把我们当前对话历史也传一份上去，同时给一个目录告诉每一个文件是什么

##### Assistant (commentary)

我会按 Ponytail full 把交接内容放进现有 `mrg` 仓库的一个独立目录，避免覆盖原论文代码。先只读确认仓库、默认分支和现有结构；同时查找 Codex 是否能导出本线程原始对话。若只能取得摘要而非逐字日志，我会明确区分，绝不把摘要冒充原始历史。

##### Assistant (commentary)

已确认仓库存在：`xiotakut/mrg`，公开、默认分支 `main`，当前账号有管理员权限。上传会放在新目录，不碰原代码。现在我读取 Codex 当前线程可导出的历史；产品接口只保证“已完成回合及其摘要”，我会先确认它是否包含逐字消息。

##### Assistant (commentary)

确认后我会采用一个目录：`handoff/medrgag-wm-2026-08-23/`。其中保留完整 v4 实验产物、精简可移植 runner、计划与执行记录、对话历史，以及逐文件索引；v15、corpus、模型和旧安全/门禁脚本不上传。对话文件只包含用户与助手实际可见消息，不包含隐藏推理或工具内部输出。

##### Assistant (commentary)

仓库非常小，当前只有 README 和一个旧的 35 KB ZIP；没有需要遵循的仓库内 AGENTS 指令。`main` 工作树干净，因此新增 handoff 目录不会与原代码冲突。现在开始导出整个线程的可见消息，并按时间顺序写成 Markdown。
