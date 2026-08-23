# Visible transcript: /root/code_test_audit

- Session: `01a02f2f-585e-7ad2-ba38-1d8dfc60d95d`
- Timestamps: UTC
- Scope: user/task messages and visible agent commentary/final messages only.

## 2026-08-23T15:13:50.679Z — Agent commentary

I’m applying Ponytail Full to keep this audit focused on the smallest decisive code paths and tests. I’ll inspect the repository guidance first, then trace and verify without touching canonical artifacts.

## 2026-08-23T15:13:58.532Z — Agent commentary

The workspace contract confirms this is a provenance and leakage audit: predictions must be written before gold is joined, completed outputs are immutable, and no inference should be rerun. I’m now tracing the matched-greedy branch and its reader/evaluation helpers end to end.

## 2026-08-23T15:14:25.639Z — Agent commentary

The implementation has the key safeguards in the actual execution path: output existence is checked before any model import, all 170 chat prompts are deduplicated before one `generate` call, mapped back by stored indices, and equality is reasserted before predictions are written. The gold-bearing P2 file is first opened only after prediction persistence; I’m validating those claims against the frozen artifacts now.

## 2026-08-23T15:14:40.840Z — Agent commentary

The frozen artifacts agree with the repaired path: 170 predictions, 128 unique prompts, 42 paired groups, 86 singletons, one generation call, and all 42 paired outputs match in raw/strict/author form. Predictions and frozen inputs contain no gold/correctness fields; gold appears only in the 170 evaluation rows. The overwrite guard also fails closed before inference. I’m running the full CPU-only local suite for the final acceptance count.

## 2026-08-23T15:14:46.034Z — Agent commentary

The full suite found one failure unrelated to matched-greedy: the counterfactual fixture is rejected by its own private-path guard (`counterfactual contexts must be stored below private_data/ or cache/`). I’m checking whether this is an actual code/test defect or an invocation/environment issue; I won’t edit it under this audit.

## 2026-08-23T15:15:21.643Z — Agent final_answer

PASS for the accepted matched-greedy repair, with one unrelated full-suite failure.

Evidence:

- 85 items × 2 conditions form 170 prompt records; deduplication requires 128 unique prompts, 42 pairs, and 86 singletons: [run_p4_proxy_pilot.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/scripts/run_p4_proxy_pilot.py:1084).
- Exactly one `model.generate(unique_prompts, ...)` call is made and outputs are mapped back through stored indices: lines 1124–1138.
- Mapping completeness and paired MD/MW identity are asserted: lines 1103–1122.
- The 42 identical pairs must match in user prompt, chat prompt, raw response, strict prediction, and author prediction before any write: lines 845–897 and 1215–1222.
- Existing prediction/result/summary files cause an immediate `FileExistsError` before model imports: lines 900–915. Verified with expected exit code 1.
- Both conditions use the same base prompt, neutral-state envelope, payload schema, chat template, temperature 0, seed 42, and 512-token ceiling: lines 927–1037.
- All 85 paired prompts are explicitly required to have equal input-token counts: lines 990–1017.
- Predictions are persisted before P2 containing gold labels is opened; evaluation then adds gold/correctness into separate result rows: lines 1224–1242.
- Actual reader helpers are upstream [medrgag_logic.py](/home/data3/txy/MedRGAG/src/medrgag_logic.py:312): `reader_documents`, `author_answer_parser` at line 332, and `strict_answer_parser` at line 353. Pack-local [accuracy.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/src/evaluation/accuracy.py:10) is not used by this historical runner; evaluation is performed inline.

Frozen-artifact verification:

- 170 predictions and 170 results; 85 unique items and 85 rows per condition.
- 42 identical source-ranking pairs.
- 42/42 identical raw responses, strict predictions, and author predictions.
- 85/85 equal input-token counts; both conditions total 160,457 input tokens.
- Summary records 128 unique prompts, 42 paired groups, 86 singletons, and one generation call.
- Predictions and input rows contain no top-level gold, correctness, answer, or prediction leakage fields.
- Results contain gold only as `gold_answer`, plus post-hoc correctness fields.
- Prediction values are preserved exactly in all 170 result rows.
- Recorded result: strict 64/85 versus 64/85; author 65/85 versus 65/85.

Tests:

- Focused tests: 3/3 passed.
- Full CPU-only suite: 36/37 passed; 1 failed.
- Failure is unrelated and appears to be a stale counterfactual fixture: [test_counterfactual_runner.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/tests/test_counterfactual_runner.py:17) creates contexts directly under a temporary directory, while [run_counterfactual_variants.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/scripts/run_counterfactual_variants.py:170) requires them below `private_data/` or `cache/`. The fixture also omits newly required `context_sha256` bindings at lines 109–110.

No files or canonical artifacts were changed.

## 2026-08-23T15:15:41.329Z — Agent commentary

Ponytail Full points to a fixture-only repair: place the temporary context under the runner’s existing private boundary and bind each sealed relation to the exact context hash the production validator computes. I’ll leave runner logic and artifacts untouched.

## 2026-08-23T15:15:48.206Z — Agent commentary

The contract has only one caller and confirms the fixture drift: the runner checks the path boundary before loading, then requires each `relevant`/`irrelevant_control` relation’s hash to equal `sha256_json(context without context_sha256)`. I’m applying exactly those two fixture updates.

## 2026-08-23T15:16:10.610Z — Agent commentary

The fixture-only fix now passes its original behavioral assertion, and the complete CPU suite is green. I’m collecting the final status evidence; this directory is not a Git worktree, so I’ll report that explicitly and use filesystem scope checks instead of inventing Git diff state.

## 2026-08-23T15:16:18.541Z — Agent final_answer

PASS.

Changed only [tests/test_counterfactual_runner.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-dietrichgebert-ponytail-skill/medrgag_wm_validation_pack/tests/test_counterfactual_runner.py:29):

```diff
- contexts_path = root / "contexts.jsonl"
+ contexts_path = root / "private_data" / "contexts.jsonl"
+ contexts_path.parent.mkdir()

- "expected_candidate_id": "A"
+ "expected_candidate_id": "A", "context_sha256": sha256_json(contexts[1])

- "expected_candidate_id": "A"
+ "expected_candidate_id": "A", "context_sha256": sha256_json(contexts[2])
```

This exactly matches the production hash calculation over each changed context.

Tests:

- Targeted: 1/1 passed.
- Full CPU-only suite: 37/37 passed in 0.356 seconds.

Status evidence:

- Workspace is not a Git worktree, so `git status` is unavailable.
- Recent source scan showed only `tests/test_counterfactual_runner.py`.
- Recent canonical-artifact scan was empty.
- No production logic or canonical artifacts changed.

## 2026-08-23T15:18:43.636Z — Agent commentary

I’m using Ponytail Full for this mapping: reuse the smallest existing interfaces, name only pilot-blocking gaps, and avoid formal-study scaffolding. I’ll trace the current plan against the implemented modules and their tests, read-only.

## 2026-08-23T15:18:56.193Z — Agent commentary

The first major integration fact is already clear: the reusable pack has mature state/query/retrieval/card/rollout/cache primitives, but its existing M0–M10 registry uses the earlier study’s method meanings. I’m now checking each interface’s actual payload assumptions so the mapping won’t falsely label semantic mismatches as reuse.

## 2026-08-23T15:20:54.523Z — Agent final_answer

Read-only mapping complete. The reusable implementation covers most mechanics; the main work is adapting task semantics and renumbering the method registry.

### Pipeline reuse and real gaps

| Step | Reuse exactly | Existing tests | Pilot-blocking gap / recommended owner |
|---|---|---|---|
| Unified item + visibility | `src/data/loaders.py:Item`, `load_items`, `write_question_view`, `load_question_jsonl`; `src/medrgag_adapter/baseline.py:answer_free`; recursive guards in `scripts/run_variants.py:_reject_gold` | `test_answer_key_isolation.py`, `test_slice_builder_has_no_prediction_fields.py` | Current `Item` is MCQ-only and `load_items` leaves `pair_id`, `should_answer_change`, `change_direction`, nested gold, trajectory and fixed evidence in metadata. Extend `src/data/loaders.py` with `BenchmarkRecord.inference_view()` / `evaluation_view()` and four raw adapters. Inference view must deep-reject pair/gold/change fields while retaining patient state, time series, fixed evidence and candidate actions. |
| Task routing | `state_constructor.construct_state` decision-mode mapping; `wm.router.route`; `effective_method_ids` | `test_non_action_router_matches_m0_input.py`, `test_action_constructor.py` | Existing routing is action-tier-only. Add `src/data/task_router.py: route_task(item) -> TaskSpec` containing `task_family`, output type, evidence policy, card mode, and allowed methods for MedPIC/CLIR/MedEinst/MedCounterFact. |
| State/action extraction | `extract_state`, `construct_state`, `construct_actions`; prompt/schema retry through `prompt_json` | `test_provider_wiring.py`, `test_action_constructor.py`, `test_json_schema_validation.py` | `extract_state` currently sees answer options and not structured patient trajectory/fixed evidence. Extend its visible-input argument and schema; default transition generation must hide options. Candidates must come from declared actions/hypotheses, not option-derived answer labels. Add diagnosis/evidence-conflict task modes. |
| Fixed-evidence policy | `Evidence`, `PrivateEvidenceStore`, `transition_with_provider` | `test_provider_wiring.py`, privacy tests | Add `src/wm/evidence_policy.py: acquire_evidence(item, task, actions, search=None)`. Policies: `fixed_evidence_only` for MedCounterFact, `trajectory_primary` for CLIR, `balanced_retrieval` where allowed. Fixed-only must never invoke search; CLIR observations must remain distinct from document priors. |
| Balanced query planning | `plan_queries`, `plan_queries_with_provider`, `balanced_retrieve` already enforce four symmetric query types and passage budgets | `test_balanced_action_retrieval_budget.py`, `test_stage_e_context_prep.py` | Generalize NICE naming/source and allow task-provided candidate kind (`action` or `hypothesis`). Fixed-evidence tasks bypass querying. Preserve symmetry checks for M5/M9. |
| Transition/rule cards | `transition_card`, `transition_with_provider`, `schemas/transition_rollout.schema.json`, evidence-ID validation | `test_provider_wiring.py`, `test_stage_e_context_prep.py`, schema/privacy tests | Extend the existing schema rather than creating a parallel card type: add `inactive`, triggering conditions/exceptions, provenance/source type, hypothesis mode, and explicit `next_state_not_required`. Ensure option-hidden generation. |
| Rollout comparator | `select_rollout` is deterministic, frozen-weight, one-step comparison with provenance IDs | `test_rollout_selector.py` | Extend its applicability map for `inactive`; score contradiction/harm and task-specific state consistency. Interface: `select_rollout(..., weights=FROZEN_WEIGHTS, task_family=...)`. Keep one comparator. |
| Reader + logging | `normalize_final_answer`, `prompt_json` retry, `audit_metadata`, `item_result`, `persist_variant_results`, immutable writes | `test_prompt_hash_saved.py`, `test_reproducible_seeded_decoding.py`, `test_variant_dispatch.py`, `test_path_traversal.py` | Current reader only accepts one A–Z choice. Add task-aware normalization for exact-set MedPIC, open-diagnosis MedEinst, CLIR formats, and MedCounterFact’s separate evidence conclusion/safety flag. Extend result rows with task family, visible-input hash/fields, raw response, parse status, queries/document IDs, context provenance, revisions, parameters and call count. |
| Cache | `ContentAddressedCache`; `AllLlamaMedRGAG._call` already caches by stage, prompt, payload, model and decode settings | `test_cache_is_content_addressed.py`, `test_all_llama_integration.py` | Stage-E provider/retrieval paths are not cached. Add optional cache use at `prompt_json`/evidence acquisition and include dataset revision, visible-input hash, prompt/schema hash, model/decode and evidence policy in keys. Reuse the existing cache class. |
| Evaluation | `accuracy`, `paired_bootstrap`, `exact_mcnemar`, `holm_correction`, `summarize_cost`, transition fidelity | `test_paired_stats.py`, `test_counterfactual_runner.py` | Current answer loader and `pair_metrics` cannot score exact sets, open diagnosis, CLIR evidence/timestamps, or MedCounterFact dual outputs. Add one task-dispatched evaluator in `src/evaluation/task_metrics.py`; recover pair IDs only there. No new statistics framework is needed for the pilot. |

### M0–M13 mapping

The existing registry IDs must not be reused unchanged because their meanings are shifted.

| Current-plan method | Reusable implementation |
|---|---|
| M0 Direct response | New thin dispatch branch using the shared reader with no documents/cards. |
| M1 Vanilla RAG | Existing old-M0 reader path over retrieved documents only. |
| M2 Original MedRGAG | `AllLlamaMedRGAG.run_item`, `scripts/run_all_llama.py`, or sealed external binding. The old dispatcher’s M0 is only a reader replay, not the complete KGCC/KADS pipeline. |
| M3 State/action decomposition | Existing old M1: `decompose`. |
| M4 Equal-token reasoning | Existing old M2: `equal_budget_prompt` and measured ledger. |
| M5 Evidence-specific retrieval | Existing old M3 plus generalized evidence sources. |
| M6 Preconditions/applicability only | Existing old M4 card projection. |
| M7 Effect/next-state only | Existing old M5 card projection. |
| M8 Cards without comparator | Existing old M6. |
| M9 Full CF-WM | Existing old M7: cards + `select_rollout`. |
| M10 Without grounding/provenance gate | Existing old M8 parametric/unsupported-card path, adapted to the new provenance semantics. |
| M11 Shuffled mapping | Existing old M9: `shuffle_action_effect_mapping`; tested by `test_shuffled_mapping_changes_rollout_ids.py`. |
| M12 Oracle cards | Existing old M10 oracle path and prerequisite checks. |
| M13 Pair-visible oracle | Missing by design. Add an explicitly gated diagnostic-only branch requiring a sealed pair artifact and `allow_pair_visible_oracle=True`; never expose it through normal inference defaults. |

Update ownership: `src/experiment_runner.py` registry/dispatch, `scripts/run_variants.py` orchestration, `tests/test_method_registry.py` and `tests/test_variant_dispatch.py`. Preserve `BudgetLedger`, immutable persistence, prerequisite failure, and shared-reader mechanics.

### Minimal integration order

1. Freeze the new M0–M13 meanings and add four dataset adapters with separated inference/evaluation views.
2. Add `TaskSpec` routing and fixed/trajectory/retrieval evidence policies.
3. Extend state/action input and schemas; enforce option-hidden transition generation.
4. Wire existing query/retrieval/card/comparator stages through the evidence policy and content-addressed cache.
5. Add task-aware reader normalization and complete trace logging.
6. Remap the dispatcher and baselines; keep M13 explicitly diagnostic-only.
7. Add one fixture per dataset covering visibility, output parsing and evidence policy.
8. Run M0/M1/M2 first, then M12 oracle; only implement/run M3–M11 after the oracle gate.

Deferred as nonessential to a runnable four-dataset pilot: mixed-effects modeling, CLADDER/CP-Env, control-dataset adapters, full reviewer workflow, and expanded formal no-go scaffolding. No files were changed.

## 2026-08-23T15:27:12.559Z — Agent commentary

I’m applying Ponytail Full to Gate A: one standard-library acquisition script, one focused fixture test, and no framework beyond the required immutable inference/gold split. I’ll inspect the source registry contract and current pack layout before writing.

## 2026-08-23T15:30:07.538Z — Agent commentary

The source registry has now landed, so I’m switching from a guessed contract to its exact fields. I’ll honor its seeded selectors with `random.Random(seed).sample` over stable sorted records, including MedCounterFact companion originals.

## 2026-08-23T15:30:50.604Z — Agent commentary

The live source samples confirm the adapter details: MedPIC uses exact-set answers; CLIR embeds MCQ options in question and stores anchor evidence separately; MedEinst is paired open diagnosis; MedCounterFact stores pair/category/answer inside metadata and article summaries at top level. I’m implementing to those real shapes plus the registry’s datasets-server requirement for controls.

## 2026-08-23T15:32:39.835Z — Agent commentary

The first targeted run found one concrete bug in source normalization: Python evaluated the fallback `entry["file"]` even when `files` existed. I’m applying the one-line lazy fallback and rerunning.

## 2026-08-23T15:33:09.003Z — Agent commentary

A live rows-API check exposed two production-shape issues before handoff: ReMedQA’s registry list names API splits under config `default` (not configs), and CPV exposes `option_a`…`option_d` plus `answer_idx`. I’m correcting those exact adaptations and extending the fixture assertions.

## 2026-08-23T15:34:39.602Z — Agent commentary

The focused Gate-A test is green after the real-shape fixes. I’ve also aligned the manifest with the newly landed auditor contract—bindings, raw artifact names/hashes, adapter evidence, and explicit unavailable capabilities—and I’m running both Gate-A test modules together.

## 2026-08-23T15:35:28.745Z — Agent commentary

All three local Gate-A tests pass, including the independent auditor’s pass and fail-closed fixtures. I’m doing one final read-only check of the real MedCounterFact category/pair distribution to ensure the seeded non-overlap selection can actually produce the auditor’s 200 replacements plus 200 distinct companion originals.

## 2026-08-23T15:35:40.046Z — Agent commentary

The real check found one concrete schema alias: the repository calls the nonce category `Nonsense Tokens`. The 203 shared pair IDs are sufficient for four disjoint seeded groups of 50, so I’m adding that alias while retaining the deduplicated-original boundary.

## 2026-08-23T15:36:09.708Z — Agent final_answer

Implemented Gate-A acquisition/adaptation in:

- [prepare_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/prepare_gate_a.py)
- [test_prepare_gate_a.py](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/tests/test_prepare_gate_a.py)

Delivered:

- Pinned HF/GitHub raw acquisition and SHA-256 cache.
- Revision-bound datasets-server rows API for ReMedQA/CPV.
- Frozen seeded selection for all declared boundaries.
- MedCounterFact’s four disjoint 50-row categories plus companion originals.
- Physically separate inference/gold JSONL with recursive leakage rejection.
- Canonical per-row `input_hash`.
- Auditor-compatible bindings, raw artifacts, adapter evidence and capabilities.
- Official exact-set, MCQ/evidence, open-diagnosis and fixed-evidence formats.

Verification:

- Full local suite: 3/3 passed.
- Syntax compilation: passed.
- Real-source shapes checked for all core datasets and controls.
- No model inference or canonical Gate-A run performed.
- No files outside the two assigned paths edited.

## 2026-08-23T15:45:59.958Z — Agent commentary

我继续用 Ponytail Full：只修复三个语义根因——CPV 可见问题字段、不可逆 inference 身份、CLIR evidence allowlist；不会改审计器或其他生产文件。先读取现有 v2 原始缓存和真实字段形状，再补最小回归测试。

## 2026-08-23T15:47:55.188Z — Agent commentary

真实 v2 检查确认：CPV 有足够的结构有效组，问题是冻结抽样前未过滤“同一 `case_id` 所有 `case_text` 相同”的组；CLIR 五个任务的泄漏字段也各不相同。我会用一个小 allowlist 函数按可观测字段投影，并让不安全的 TSS `\"all\"` 返回空证据。

## 2026-08-23T15:48:41.315Z — Agent commentary

首个回归失败来自测试本身：短 raw ID `c1` 可能自然出现在 32 位十六进制摘要中，这不代表可逆泄漏。我会把断言改为结构性检查（无 raw 分隔符、固定 opaque hex），不削弱生产修复。

## 2026-08-23T15:48:53.861Z — Agent commentary

目标测试与当前完整套件已全绿。现在我用真实 v2 缓存做最后的只读语义检查：遍历 3,000 条 CLIR raw 验证投影中没有派生答案字段，并抽取真实 CPV rows 验证 `case_text` 覆盖 `question`。不会重写 v2。

## 2026-08-23T15:49:29.645Z — Agent commentary

我已按 Ponytail Full 完成最小修复：只改 acquisition 脚本和对应测试；目标测试、全量 CPU 测试以及真实 v2 raw 的只读语义检查均通过。现在整理精确行号与状态证据。

## 2026-08-23T15:49:48.168Z — Agent final_answer

PASS。

仅修改：

- `scripts/prepare_gate_a.py`
- `tests/test_prepare_gate_a.py`

关键修复：

- `prepare_gate_a.py:239-253`：CLIR evidence 改为语义 allowlist；过滤未来 observation、派生答案字段及 TSS `"all"`。
- `prepare_gate_a.py:256-262`：生成确定性 opaque SHA-256 `item_id`。
- `prepare_gate_a.py:317-321`：CPV 抽样前排除少于两行或 `case_text` 无变化的 case groups。
- `prepare_gate_a.py:376-383`：gold 保留真实 variant；CPV question 使用人口学注入后的 `case_text`。
- `prepare_gate_a.py:400-418`：inference metadata 不再暴露 `source_record_id`，variant 固定为中性 `"item"`。
- `prepare_gate_a.py:424-447`：gold 保留真实 `pair_id`、variant 和变化语义。

测试新增真实形状回归覆盖：

- CPV 有效/无效人口学组筛选。
- 注入后的两个 `case_text` 成为不同 inference question。
- opaque item ID 格式及 metadata 隐私。
- inference/gold variant 隔离。
- CLIR t6–t10 泄漏字段过滤和 TSS 空证据。

结果：

- Targeted：`1/1` passed
- Full CPU suite：`4/4` passed
- `py_compile`：`2/2` passed
- 真实 v2 raw 只读检查：
  - CLIR：3000 行，投影后 forbidden 字段 `0`
  - TSS 非空 evidence：`0`
  - CPV：确认 question 使用 `case_text`、ID opaque、无 `source_record_id`

Git 状态为 `?? ./`：整个 validation pack 在上层仓库中尚未跟踪，因此 `git diff` 无输出，不能声称工作树 clean。未修改 canonical v2 artifacts，未运行模型推理或网络下载。

## 2026-08-23T15:53:09.304Z — Agent commentary

我会按 Ponytail Full 做只读验收：先读取当前契约与 root 的最小补丁，再跑全套测试、编译检查和真实 v3 定点断言；不会修改任何文件。

## 2026-08-23T15:53:33.287Z — Agent commentary

代码路径符合新的最小设计：CPV 已改为“组内每一行 `case_text` 都唯一”，CLIR evidence 已按 task 分流，且 inference metadata 已去掉 source ID/file。接下来我会验证 auditor 的短数字边界行为和 v3 实物，而不只依赖 fixture。

## 2026-08-23T15:55:16.660Z — Agent final_answer

验收结论：实现与 v3 数据 PASS；audit 契约有 1 个真实缺口，整体应记为 FAIL 待补。

- CPV：严格要求组内每行 `case_text` 唯一，见 `prepare_gate_a.py:318-323`。v3 为 300 个 case、3010 行，所有组 question 全部非空且逐行不同。
- CLIR：task-level allowlist 正确，见 `prepare_gate_a.py:239-254`：
  - t6 保留 post observations；
  - t8 保留 pre-anchor history；
  - t7/t9/t10 全为空。
- Metadata：v3 全部 6577 行均无 `source_record_id`/`source_file`。
- Item ID：全部匹配 `<dataset>-<32 hex>`，无重复；相同输入重复计算稳定，不同 raw ID 得到不同 ID。
- Auditor 短数字 pair ID：验证 `1`、`12`、`007`；嵌入 hash 不误报，独立或分隔暴露能捕获，见 `audit_gate_a.py:171-172`。

发现的缺口：

- `audit_gate_a.py:22` 和 `:300-310` 的通用 leakage 检查不禁止 `source_record_id`/`source_file`。
- `audit_gate_a.py:371-383` 只有在暴露值恰好匹配 gold 已知 secret 时才失败。
- 因此 inference 若新增无对应 gold secret 的 `metadata.source_record_id` 或 `source_file`，auditor 会漏报。当前 v3 数据安全，但契约没有守住该边界。

验证结果：

- 全套测试：4/4 passed
- `py_compile`：4/4 files passed
- v3 定点断言：6577/6577 行通过
- fresh v3 audit：20 checks，5 个预期 capability/license blockers；无新增数据缺陷
- 未修改任何文件；Git 仍显示整个 pack 为 `?? ./`。
