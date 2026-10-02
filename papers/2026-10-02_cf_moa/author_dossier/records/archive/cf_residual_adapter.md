# 历史：CF-Residual Adapter与MA-RAG迁移

最新状态：2026-09-15（Asia/Shanghai）。补充代码核对：Adapter是外部选项评分与监督线性融合；without-base单独拟合系数，不能将消融差值解释为同一冻结融合器即时删除基础分数的效果。归档配对可见、四选一MedEinst协议上的研究；500对结果支持该设置下的跨框架迁移，但未支持MA-RAG synergy。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [Adapter实现与消融解释补充（2026-09-15）](#adapter-implementation-clarification)
- [Historical adapter result (2026-09-05)](#record-0022)
- [11. Implemented CF-Residual Adapter functionality](#record-0041)
- [11.1 Four-option and sidecar contract](#record-0042)
- [11.2 Portable methods](#record-0043)
- [11.3 Invalid and tie semantics](#record-0044)
- [11.4 Native MA-RAG variants](#record-0045)
- [13. Pilot, formal selection, and final results](#record-0049)
- [13.1 N=4/T=2 pilot](#record-0050)
- [13.2 Formal development/calibration, N=8/T=4](#record-0051)
- [13.3 Frozen 500-pair result](#record-0052)
- [13.4 Static compatibility](#record-0053)
- [13.5 Claim boundary](#record-0054)
- [14. Runtime, failures, recovery, and cost](#record-0055)
- [14.1 Restart and failure history worth preserving](#record-0056)
- [15. Canonical artifacts and local-only caches](#record-0057)
- [16. Historical adapter open questions (2026-09-05)](#record-0058)
- [summary.md](#record-0278)
- [README.md](#record-0279)

<a id="adapter-implementation-clarification"></a>

## Adapter实现与消融解释补充（2026-09-15）

本次只核对已有代码、解释历史结果，没有新推理或重算。Adapter通过额外Llama选项似然、病例变化与DDXPlus疾病特征匹配（Profile）、病例编辑前后似然差（CPG），为四个选项建立特征；再融合基础方法的选项分数。MA-RAG完整版本为9维特征的共享线性系数，MedRGAG版本为7维，without-base为4维；大模型权重不在这一步更新。开发集标签用于拟合系数和熵温度，校准集用于选择正则强度。推理调用取特征矩阵，丢弃同一构造函数返回的标签数组，再用冻结系数取最高分选项；不能把它说成整个程序从不读取标签字段。

尤其需要澄清：`fit()`分别调用`fit_variant(..., without_base=False/True)`训练完整版本及去基础分数版本；后者只使用Profile、CPG、Profile×分差、CPG×可用性四项评分特征。因此500对中的80.0%与81.8%比较的是两套分别训练的配置，不是同一冻结模型即时删除MA-RAG分数的干预。该消融仍未支持MA-RAG的额外收益；−1.8个百分点的置信区间跨0，不能推成MA-RAG稳定有害。without-base路径还沿用基础记录的有效性检查，不等于已经实现完全不运行基础方法的独立部署。

代码证据：[特征、分别拟合与预测](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/run_marag_cf.py:161)、[线性交叉熵训练与argmax](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/run_cfmoe.py:209)。历史测试数值仍以[500对冻结结果](#record-0052)为准。

<a id="record-0022"></a>

## Historical adapter result (2026-09-05)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第959行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### Historical adapter result (2026-09-05)

The earlier frozen 500-pair result was:

- MA-RAG intrinsic: 39.2%; MA-RAG + CF adapter: 80.0%, a +40.8 point
  difference with paired-bootstrap 95% CI +36.6 to +45.4;
- MedRGAG-style: 40.8%; MedRGAG + the same adapter: 82.4%, a +41.6 point
  difference with 95% CI +37.0 to +46.2;
- Profile-only: 79.4%; adapter without MA-RAG: 81.8%; consequently the result
  supports cross-interface transfer but **not** beneficial synergy with
  MA-RAG's own scores;
- the successful method is a pair-aware counterfactual sidecar, not a clinical
  world model, clinical safety system, official open-diagnosis result, or
  improvement on MA-RAG's original benchmark suite.

The result implementation was committed to `xiotakut/cf_mrg` at
`53aaff676439066f8d0b6478404c91e7ece3528f`. A later evidence handoff was
committed at `1e01b3a33c378041c64a76cce70ed381e4280d35`. Use the result commit
for code/result provenance and the handoff commit for the expanded data-lineage
and runtime audit.

The older completed 2026-08-23 WM-proxy study remains important historical
evidence. Its final prompt- and token-matched comparison was:

- blind direct ranking: 64/85 strict correct;
- WM-planner ranking: 64/85 strict correct;
- one improvement, one regression, 83 unchanged;
- delta 0.0 percentage points, bootstrap 95% CI -3.5 to +3.5, exact McNemar
  p=1.0;
- all temporary reviewer roles were distinct Luna Max agents, so artifacts
  remain `human_validated=false` and `grounding=parametric_no_nice`.

That decision is complete: those artifacts do not identify incremental value
from transition cards or a world-model planner over direct ranking. Stop the
world-model claim; retain only an exploratory
`action-aware/direct-ranking` signal. Do not rerun anything merely to learn
this conclusion.

Use these sources in this order:

| Question | Authoritative source |
|---|---|
| Where is the latest random evaluation selection? | `$CF_BENCH_V5/README.md`, `selected_targets.jsonl.gz`; use `evaluation_labels`, not semantic `labels` |
| Where is the expanded full-coverage classification? | `$CF_CLASSIFIED_FULL/DELIVERY.md`, `exports/all_reviewed_target_annotations.jsonl.gz`; target-level eligibility |
| What is the evaluated v3 benchmark and category allocation? | `$CF_BENCH_V3/README.md`, `manifest.json`, `units.jsonl`; use current `labels` |
| How do I load current questions, gold and saved results? | Section 1, “Load the current benchmark in a new conversation”; `$CF_BENCH_V3/items.jsonl`, `evaluation.jsonl`, `results/` |
| What are the current R1–R5 M0/M1 results? | `$CF_BENCH_V3/results/category_scores.csv`, `scored.jsonl`, `r1_r5_total.png` |
| What was the separate full-release comparison and claim boundary? | `$CF_FULL/findings.md`, `summary.md`, `metrics.json` |
| Where are benchmark publications? | `$CF_BENCHMARKS/README.md`; 2026-09-08 annotation archive and 2026-09-07 full comparison are published; v3 is local |
| Which data, exposure and source overlap were used in the full-release comparison? | `$CF_FULL/acquisition.md`, `data_checks.md`, `sample_plan.json`, `taxonomy.jsonl`, `source_overlap.json` |
| What was the historical adapter result? | `$CF_ADAPTER/summary.md`, `metrics.json`, `bootstrap.json` |
| What produced the current full comparison, and how was it accepted? | `$CF_FULL/commands.sh`, `baseline_contract.md`, `config.json`, `execution_provenance.json`, `validation.json`, `artifact_audit.json` |
| What did the historical adapter handoff add about reuse, cost and missing controls? | `$CF_REPO/chatgpt_handoff_2026-09-05/README.md` |
| Where is the full-release baseline implementation? | `$CF_PACK/scripts/run_cf_baseline_screening.py`; section 1 describes the v3 runtime boundary; section 11 describes the historical adapter |
| What was each earlier CF experiment? | Its own `results_*` directory and `summary.md`; see section 9 |
| What is the external MA-RAG revision and patch boundary? | `$CF_ADAPTER/commands.sh`, `marag_logging.patch`, and `marag_retriever_compat.patch` |
| What was planned? | `$WM_ARCHIVE/medrgag_wm_validation_pack/PROJECT_PLAN.md` |
| What was actually run and concluded? | `$WM_ARCHIVE/medrgag_wm_validation_pack/WM_VALIDATION_PROTOCOL_AND_RESULTS.md`, especially sections 15–18 |
| What is the final numerical result? | `$V4/p4_matched_rank_greedy_reader_summary.json` |
| What is the frozen v15 boundary consumed by the WM study? | The same v4 directory's `p2_v15_item_results.jsonl`, `p2_v15_baseline_results.json`, and `p4_proxy_all85_input.jsonl` |
| How did the full all-Llama v15 baseline run? | `MedRGAG/REPRODUCE_ALL_LLAMA.md`, the completed runtime state, and the v15 `metrics.json` described below |
| What was transferred to GitHub? | `$WM_ARCHIVE/mrg-handoff-upload/handoff/medrgag-wm-2026-08-23/README.md` and `FILE_INDEX.md` |

The files named `ARCHIVED_*IMPLEMENTATION_CONTRACT.md` preserve old proposed
study contracts. They are research history, not active coding-agent
instructions. Their stages and gates must not restart stopped work.

<a id="record-0041"></a>

## 11. Implemented CF-Residual Adapter functionality

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1486行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 11. Implemented CF-Residual Adapter functionality

The current integration added six focused scripts and one test module. It did
not vendor MA-RAG or alter the existing MedRGAG/CF formulas.

The implementation boundary was deliberately small: reuse the existing
Profile/CPG sidecar unchanged, add normal forced-choice fusion, and isolate any
MA-RAG-native behavior under separate names. The task explicitly excluded new
world models, transition cards, NICE/atomic-rule systems, the old 27-method
matrix, large MoE routers, hard preserve/revise gates, hash registries, generic
retry frameworks, and multiple timestamped result trees.

| File | Implemented behavior |
|---|---|
| `$CF_PACK/scripts/prepare_marag_medeinst.py` | Reuses the existing MedEinst loader and deterministic four-option construction; emits control, trap, and pair-prompt MA-RAG records plus one shared mapping; selects dev/cal/test while excluding configured later-test/current-train IDs |
| `$CF_PACK/scripts/parse_marag_outputs.py` | Reads completed MA-RAG rounds, preserves candidate text and entropy, computes vote counts, consensus, cost fields, and official strict-majority output; exact ties are explicit invalids rather than gold-resolved answers |
| `$CF_PACK/scripts/run_marag_cf.py` | Implements `smoke`, `fit`, `predict`, and `export-scores`; builds smoothed vote and entropy-weighted distributions, z-normalized option features, linear fusion, uniform controls, no-base ablations, and shuffle controls |
| `$CF_PACK/scripts/evaluate_marag_cf.py` | Computes accuracy, paired correctness, BTR, old-answer persistence, correct flips, repairs, harms, conditional harm, preservation, false consensus, efficiency, and 1,000-sample paired bootstrap |
| `$CF_PACK/scripts/run_cf_marag_native.py` | Contains separate native variants: pure residual trigger, delta-aware query, CF history ranking, and their full combination; never overwrites official baseline outputs |
| `$CF_PACK/scripts/run_marag_retriever.py` | Starts the upstream retriever once and avoids upstream script-mode double initialization/JNI option duplication |
| `$CF_PACK/tests/test_marag_cf.py` | Checks mappings, tie handling, no-gold inference, scorable continuous ties, invalid exclusions, trigger semantics, costs, and score export |

<a id="record-0042"></a>

## 11.1 Four-option and sidecar contract

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1508行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 11.1 Four-option and sidecar contract

Each pair has exactly the same A–D mapping for every base/method:

```text
trap diagnosis
control diagnosis
two deterministic DDXPlus-profile-overlap hard negatives
```

The trap-only MA-RAG baseline sees only the trap case. The pair-prompt baseline
sees control, trap, and structured changed findings. The Profile/CPG sidecar is
also pair-aware and uses a separate Llama-3.1-8B scoring path.

Ignoring an option-independent constant, `profile_no_document` is:

```text
2 * direct_trap_option_score
- direct_control_option_score
+ 2 * standardized_delta_profile_alignment
```

The profile term rewards added findings aligned with a diagnosis and penalizes
removed findings. It uses DDXPlus profiles and no MA-RAG retrieved documents.

CPG reuses the counterfactual edit/probability-gap idea from
`FAIRHealth/clinical-counterfactual-reasoning` at
`265d1aea88f705063bb7ff2d686547d373da7e09`. This implementation applies up to
two deterministic remove/revert/negate edits and scores exact option-sequence
likelihood changes. It does not claim to invent CPG or reproduce the full
multi-agent method.

<a id="record-0043"></a>

## 11.2 Portable methods

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1540行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 11.2 Portable methods

`run_marag_cf.py predict` produces these main methods from one frozen score
cache:

```text
marag_int_control
marag_int_trap
marag_int_pair_prompt
profile_only
cpg_core
marag_profile_uniform
marag_profile_cpg_uniform
marag_cf_learned
marag_cf_without_marag
marag_cf_shuffled_delta
marag_cf_shuffled_profile
marag_cf_shuffled_cpg
medrgag_baseline
medrgag_profile_uniform
medrgag_profile_cpg_uniform
medrgag_cf_learned
medrgag_cf_without_medrgag
```

For MA-RAG, per-option learned feature groups are:

```text
vote_score(a) = log((count(a) + 0.5) / (N + 2.0))
candidate_weight(i) = exp(-mean_entropy(i) / temperature)
entropy_score(a) = log(normalized sum of weights predicting a)
```

Each expert's four scores are z-normalized within the question before fusion.
The official majority prediction remains unchanged; continuous vote scores are
adapter inputs only.

The learned feature groups are:

```text
normalized vote score
normalized entropy-weighted vote score
normalized Profile score
normalized CPG score
vote x consensus strength
entropy vote x rounds used
Profile x MA/Profile top-1 agreement
Profile x Profile margin
CPG x availability
```

Development fits the scalar entropy temperature and linear coefficients.
Calibration selects L2 from `{0, 0.01, 0.1, 1}`. The frozen selection is
entropy temperature `0.05000032401354733` and L2 `0` for the main MA and
Med variants. Fresh inference does not refit.

This is ordinary forced-choice score fusion, not a preserve/revise gate. Every
runtime-valid item receives four scores and selects their argmax. There is no
default preserve behavior or silent baseline fallback.

<a id="record-0044"></a>

## 11.3 Invalid and tie semantics

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1600行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 11.3 Invalid and tie semantics

- Official MA-RAG uses strict majority behavior. A 4–4 or other top-count tie
  is `status=invalid`, with candidates and vote counts retained for diagnosis.
- A complete tie with all eight valid candidates, finite entropy, finite
  four-option scores, and vote total eight is still a valid continuous-score
  input to the forced-choice adapter. It is not converted into an official
  baseline prediction.
- Parse failures, incomplete pools, and runtime failures remain invalid for
  both baseline and adapter. They are never replaced with gold or a base
  prediction.
- Profile/CPG disagreement uses three states. An unavailable score is excluded
  from its disagreement denominator rather than treated as agreement.
- Efficiency summaries include only rows with all required finite cost fields
  and state their denominator/excluded count.
- `full_cf_marag_native_plus_adapter` uses full native as its own repair/harm
  reference; comparisons against original MA-RAG remain separate bootstrap
  contrasts.

<a id="record-0045"></a>

## 11.4 Native MA-RAG variants

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1619行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 11.4 Native MA-RAG variants

The official baseline code path was kept separate. Native behavior lives only
in `run_cf_marag_native.py` and separately named output roots.

- `cf_trigger_only`: after validating and reusing the complete official
  baseline history, append exactly one ordinary official-query round only when
  the final pool is unanimous, Profile disagrees above the frozen threshold,
  and round budget remains. It does not expose delta/challenger text.
- `delta_query_only`: retains normal candidate-conflict information and adds at
  most two changed-finding/challenger queries while keeping at most four total
  queries and eight documents.
- `cf_history_ranking`: adds normalized Profile/CPG scores for a candidate's
  predicted option to original `-mean_token_entropy` quality.
- `full_cf_marag_native`: combines the selected trigger, query, and ranking
  mechanisms.

Gold is never passed to the native inference judger or ranking feature path.
Baseline reuse requires source metadata and a complete first-round candidate
pool. Pilot grid selection froze Profile threshold 1.0, beta-Profile 0, and
beta-CPG 1.0.

<a id="record-0049"></a>

## 13. Pilot, formal selection, and final results

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1711行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 13. Pilot, formal selection, and final results

<a id="record-0050"></a>

## 13.1 N=4/T=2 pilot

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1713行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 13.1 N=4/T=2 pilot

The pilot used 100 development and 50 calibration pairs.

| Method | Development | Calibration |
|---|---:|---:|
| MA-RAG trap | 58% | 42% |
| MA-RAG pair prompt | 77% | 70% |
| Profile-only | 78% | 74% |
| MA learned adapter | 83% | 78% |
| Adapter without MA | 78% | 78% |
| MedRGAG-style base | 51% | 40% |
| Med learned adapter | 81% | 80% |

Wrong-unanimous stops were 32/100 on development and 21/50 on calibration.
The pilot proved that the interface worked and false consensus existed. It did
not establish synergy: the calibration adapter tied the no-MA ablation.

Pure-trigger thresholds 0, 0.5, and 1.0 produced no pilot repairs or harms.
Threshold 1.0 was frozen because it made the fewest unnecessary extra rounds at
the same accuracy. The nine history-ranking beta pairs selected beta-Profile 0
and beta-CPG 1 on development; calibration moved from 42% base to 46%.

Do not reuse the earliest native pilot directories blindly. One old “trigger”
run included delta-query behavior and was reclassified as
`cf_trigger_plus_delta_query`; an early 100-item full-native directory mixed two
query semantics across its first 82 and last 18 items and is marked
`legacy_mixed`. It was excluded from selection. The frozen pilot record is
`$CF_PACK/results_cfmoe/cache/marag_cf/native_selection.pilot.json`; the
consistent formal-native merged rounds and predictions in the same cache are
the usable native artifacts.

<a id="record-0051"></a>

## 13.2 Formal development/calibration, N=8/T=4

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1745行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 13.2 Formal development/calibration, N=8/T=4

Official MA-RAG results before opening the later test:

| Member/method | Development 400 | Calibration 150 |
|---|---:|---:|
| control | 54.75% | 53.33% |
| trap | 53.75% | 48.67% |
| pair prompt | 73.75% | 67.33% |
| Profile-only | 78.50% | 81.33% |
| MA learned adapter | 79.50% | 81.33% |
| adapter without MA | 78.50% | 81.33% |
| MedRGAG-style base | 48.00% | 44.00% |
| Med learned adapter | 78.75% | 81.33% |

The formal native diagnostics were supplementary:

| Native variant | Development | Calibration | Interpretation |
|---|---:|---:|---|
| pure trigger | 53.75% | 48.67% | exactly base; no false-consensus repairs |
| delta query | 57.50% | 50.00% | +3.75 and +1.33 points |
| history ranking | 55.75% | 48.00% | +2.0 then -0.67; unstable |
| full native | 54.00% | 50.00% | +0.25 and +1.33; small |

Fresh native variants were deliberately not run after the user narrowed the
scope to the core portable adapter.

<a id="record-0052"></a>

## 13.3 Frozen 500-pair result

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1772行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 13.3 Frozen 500-pair result

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| MA-RAG trap | 39.2% | 17.6% | 66.76% | — | — | 8 |
| MA-RAG pair prompt | 50.2% | 30.2% | 49.00% | 86 | 31 | 3 |
| Profile-only | 79.4% | 42.8% | 12.19% | 226 | 25 | 0 |
| MA-RAG + learned adapter | 80.0% | 52.6% | 13.18% | 210 | 6 | 1 |
| Adapter without MA-RAG | 81.8% | 55.0% | 8.31% | 229 | 16 | 1 |
| MedRGAG-style base | 40.8% | 17.6% | 60.54% | — | — | 0 |
| MedRGAG + learned adapter | 82.4% | 47.0% | 10.88% | 220 | 12 | 0 |
| Adapter without MedRGAG | 81.8% | 46.8% | 10.88% | 217 | 12 | 0 |

Required paired-bootstrap contrasts:

- MA adapter minus MA base: +40.8 points, 95% CI +36.6 to +45.4;
- Med adapter minus Med base: +41.6, CI +37.0 to +46.2;
- MA adapter minus pair prompt: +29.8, CI +25.2 to +34.6;
- MA adapter minus Profile: +0.6, CI -2.4 to +3.8;
- MA adapter minus adapter-without-MA: -1.8, CI -4.2 to +0.4.

Shuffle controls reduced MA adapter accuracy to 50.0% for shuffled delta,
42.4% for shuffled profile, and 73.0% for shuffled CPG. The corresponding
real-minus-shuffle differences were +30.0, +37.6, and +7.0 points, all with
confidence intervals above zero.

MA-RAG stopped with a unanimous final pool on 459/500 items and a wrong
unanimous pool on 273/500. The post-hoc adapter corrected 190/273. This supports
the existence of a false-consensus blind spot, but not the native trigger: the
trigger itself did not repair it in development/calibration.

Fresh MA trap had eight invalid outputs: seven exact vote ties and one runtime
failure. The adapter numerically resolved five tied distributions correctly
but left the runtime failure invalid. The improvement remains large when all
ties are removed. CPG had finite four-way scores on 484/500 fresh pairs and was
explicitly not applicable on 16; no score was fabricated for those rows.

<a id="record-0053"></a>

## 13.4 Static compatibility

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1809行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 13.4 Static compatibility

- The prior RiskRoute path returned exactly the stored MedRGAG prediction on
  400 ReMedQA static rows: 71.0% accuracy, ReAcc 53.0%, ReCon 60.0%.
- The MA-RAG static check is a deterministic bypass of the stored 100-item
  MedQA base prediction, with 100/100 prediction equality and 72.0% accuracy.

These checks establish applicability isolation, not learned safety.

<a id="record-0054"></a>

## 13.5 Claim boundary

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1818行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 13.5 Claim boundary

Supported:

> The same pair-aware counterfactual sidecar substantially improves two
> different medical-RAG base interfaces under one controlled four-option
> MedEinst protocol.

Not supported:

- genuine MA-RAG synergy, because removing MA-RAG is numerically better;
- broad cross-dataset transfer;
- official open-diagnosis MedEinst or original MA-RAG benchmark SOTA;
- an exact paper configuration for the local all-Llama MedRGAG proxy;
- clinical deployment or safety;
- a clinical world model.

<a id="record-0055"></a>

## 14. Runtime, failures, recovery, and cost

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1835行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 14. Runtime, failures, recovery, and cost

The server inventory observed on 2026-09-05 was:

```text
4 x NVIDIA H20, 97,871 MiB each
NVIDIA driver 570.133.20
Intel Xeon Platinum 8469C, 48 physical cores / 96 threads
491 GiB RAM, no swap
Linux 5.15.0-144-generic
vLLM 0.8.5, PyTorch 2.6.0
```

The visible end-to-end window ran from 2026-09-02 16:44:31 to the final result
commit on 2026-09-03 19:24:48, about 26 h 40 m. Reboot downtime was not logged
separately.

| Phase | Elapsed wall time | Work |
|---|---:|---|
| environment, MedQA check, smoke, pilot, grids | about 5 h visible | 450 official pilot item-runs plus native/grid work |
| formal base dev/cal | 6 h 37 m | 1,650 MA-RAG item-runs |
| parse/fit/freeze | minutes | entropy temperature, linear weights, L2 |
| formal native dev/cal | 8 h 12 m | four variants x 550 pairs = 2,200 method/item runs |
| fresh Qwen control/trap/pair | 5 h 32 m | 1,500 MA-RAG item-runs |
| fresh Llama sidecar | 4 h 38 m 52 s | concurrent with fresh Qwen, so not added again to elapsed wall time |
| evaluation/report/tests/push | about 38 m | metrics, bootstrap, documentation, verification |

Formal plus fresh unchanged MA-RAG alone generated:

```text
3,150 item-runs
45,872 candidate answers
10,332 retrieval queries
19,710 retained/retrieved documents
20,531,300 generated tokens
45.99 summed per-item wall hours, compressed by parallelism to about 12.1 h
```

One MA-RAG item is therefore not one model call: it starts with eight solver
candidates and can add query generation, retrieval/reranking, and another eight
candidates on every additional round.

The 500-pair sidecar took 4 h 38 m 52 s and recorded 3,312,304 generation-stage
completion tokens; exact option-likelihood passes are additional and were not
counted by that field. Approximate stages were 1 h 43 m for retrieval and the
MedRGAG baseline path, 47 m for option likelihood, 7 m for matching/document
scores, 2 h 1 m for raw CPG/expert scores, and 22 s for assembly.

The largest avoidable delay was running the 8 h 12 m native block before the
fresh portable result. Future order should be:

```text
smoke/pilot -> portable dev/cal fit -> portable fresh core -> optional native
```

<a id="record-0056"></a>

## 14.1 Restart and failure history worth preserving

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1890行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

##### 14.1 Restart and failure history worth preserving

- A server reboot interrupted calibration pair-prompt and one native-full
  question. Partial directories were moved under
  `/home/data3/txy/.cache/marag_interrupted/`; completed metadata-backed items
  were reused rather than rerun.
- Baseline reuse now requires source metadata and the expected candidate pool.
  A bug that called `.exists()` on a missing later round was fixed so validation
  occurs only when that round exists.
- The Llama sidecar initially failed at model startup because the wrong
  Transformers version was imported. It resumed the existing retrieval cache
  with the pinned 4.51.3 compatibility path.
- Fresh trap question 34 entered an upstream unbounded retry because a thinking
  response lacked `</think>`. Only that child was stopped; its partial directory
  was archived and an explicit runtime-invalid metadata record was written.
  The question was never replaced with a fallback prediction.
- Upstream aggregate accuracy could not consume an invalid sentinel with no
  round file; the project parser can. Use the project parser for canonical
  metrics.
- Wrapper shells originally queued direct-Qwen runs after pair prompts. When the
  user selected core-only scope, those queues were removed; pair-prompt shards
  were resumed without starting direct inference.

These failures added some overhead but were not the main cause of the one-day
runtime. The experimental matrix and millions of generated tokens were.

<a id="record-0057"></a>

## 15. Canonical artifacts and local-only caches

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1916行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 15. Canonical artifacts and local-only caches

The historical adapter output directory `$CF_ADAPTER` contains:

```text
dev.jsonl                         400 pairs
calibration.jsonl                 150 pairs
fresh_test.jsonl                  500 pairs
marag_dataset_map.jsonl         1,050 pair mappings
marag_rounds.jsonl              3,150 member rows
marag_option_scores.jsonl       3,150 score rows
cf_expert_scores.jsonl          1,050 expert rows
fusion_config.json              frozen fit/configuration
predictions.jsonl                 500 fresh prediction rows
metrics.json / metrics.csv      main metrics
bootstrap.json                  paired comparisons
false_consensus.csv             consensus analysis
efficiency.csv                  completed-row cost analysis
native_dev_cal_metrics.json     non-confirmatory native diagnostics
static_compatibility.json       bypass checks
summary.md                      narrative result
commands.sh                     exact execution record
```

`marag_option_scores.jsonl` has 3,147 scorable rows: 3,121 official-valid plus
26 complete vote ties. Three rows are non-scorable because of parse/entropy or
runtime failures and retain null vectors plus their raw error.

Expensive local assets were not uploaded:

| Asset | Approximate size |
|---|---:|
| `$CF_ADAPTER/cache/` | 92 MiB |
| `$CF_PACK/results_cfmoe/cache/` | 865 MiB |
| external MA-RAG base raw runs | 1.7 GiB |
| external MA-RAG native raw runs | 1.1 GiB |
| Qwen3-8B weights | about 16 GiB |
| Llama-3.1-8B weights | about 15 GiB |

The raw caches are useful for resuming the exact same input/configuration and
for offline analysis. They are not the source of truth for published metrics;
the compact committed files above are.

At result handoff, the focused MA-RAG suite passed 13/13, the full repository
suite passed 155/155, six integration scripts compiled, `commands.sh` passed
`bash -n`, JSON/score-vector contracts passed, and `git diff --check` passed.
Those counts describe commit `53aaff6`; rerun only checks relevant to a later
code change.

<a id="record-0058"></a>

## 16. Historical adapter open questions (2026-09-05)

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1965行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 16. Historical adapter open questions (2026-09-05)

This section is the older adapter record. Current results and limits are in
section 1. The new baseline report proposes one possible follow-up: whether
original KADS empty selection is associated with M2−M1 errors. This follow-up
has not been implemented or evaluated.

The following requested experiments were intentionally left undone after the
user chose core-only scope:

- fresh native MA-RAG trigger/query/ranking variants;
- direct-Qwen N=1/T=1 on fresh;
- three-seed robustness on a 200-pair subset;
- MA-RAG extrinsic evaluator;
- a same-extra-Llama, similar-token, non-counterfactual ensemble control.

The most important scientific gaps are:

1. **Extra-model attribution.** Pair prompt shows that merely seeing both cases
   is insufficient, and shuffled delta/profile/CPG controls support the sidecar
   signals, but no equal-budget non-CF Llama ensemble has been tested.
2. **Cross-dataset scope.** Positive evidence is still one constructed
   MedEinst MCQ protocol. The older multi-dataset and MedPIC results were
   negative or too small.
3. **Task taxonomy.** There is no frozen, clinically reviewed sample-level
   labeling of negation, temporal change, numeric change, risk-factor edits,
   irrelevant attributes, and evidence corruption.
4. **Retrieval versus evidence use.** There is no clinically verified
   sufficient-evidence oracle or document-level factuality/applicability audit.
5. **Configuration fidelity.** MA-RAG used T=4 and MedCorp3, not the full default
   T=8/full corpus; MedRGAG is an all-Llama proxy rather than a confirmed exact
   mixed-model paper configuration.
6. **Data lineage.** Any future fresh set must exclude every earlier dev,
   calibration, test, and derived variant by underlying source case, including
   DeltaRev and older calibration tails.
7. **Budget.** No numeric wall-time, GPU-hour, or money cap has been provided.
   Ask for one before launching another multi-hour matrix.

The historical recommendation was to verify sources, define sample-level
categories and regroup saved predictions before considering another model run.
The current five-label collection, source audit, classification corrections
and offline regrouping were completed and published on 2026-09-08 as described
in section 1. The earlier small taxonomy is superseded by that frozen cohort;
remaining data-access and expert-validation gaps are listed there. This update
does not start a new model experiment or choose a repair mechanism.

Do not automatically multiply every dataset by every base and native variant.
Classifying saved predictions is offline; changing only a threshold, weight, or
grouping is offline. New inference is required only when prompts, visible
fields, retrieval, documents, model behavior, or the dataset actually change.

<a id="record-0278"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf`。

### CF-Residual Adapter on MA-RAG

#### Conclusion

The frozen CF-Residual Adapter transfers to both evaluated medical-RAG architectures in the four-option, pair-aware MedEinst protocol. On the untouched 500-pair test, it raises the MA-RAG intrinsic baseline from 39.2% to 80.0% (+40.8 points, paired-bootstrap 95% CI +36.6 to +45.4) and the MedRGAG-style baseline from 40.8% to 82.4% (+41.6 points, 95% CI +37.0 to +46.2).

This supports a cross-framework counterfactual-transfer claim. It does **not** support MA-RAG synergy: the MA-RAG adapter is only 0.6 points above Profile-only (95% CI -2.4 to +3.8), while removing all MA-RAG scores increases accuracy from 80.0% to 81.8%. The positive result is therefore driven by the portable counterfactual sidecar, not by a beneficial interaction with MA-RAG's score distribution.

The `without MA-RAG` ablation removes every MA-RAG score and feature but retains the same MA-RAG runtime-eligible cohort for a paired comparison; the one runtime-failed question remains invalid rather than receiving a sidecar-only prediction.

The experiment is a four-option MCQ proxy with access to the control and counterfactual cases. It is not an official open-diagnosis MedEinst result, a reproduction of MA-RAG's seven-benchmark table, clinical deployment evidence, a safety guarantee, or a world model.

#### Protocol and frozen configuration

- Development: 400 official train/reference pairs.
- Calibration: 150 disjoint official train/reference pairs.
- Fresh test: 500 official test pairs selected with seed 223 after excluding every source ID used by DeltaRank, CFShift, CF-KADS-MoE, RiskRoute-CF, development, or calibration. The overlap count is zero.
- Every method uses the same four diagnoses and option-to-label mapping per pair.
- MA-RAG: official intrinsic implementation at upstream commit `423f031cc0ffca679a047c885be999b9604100a9`, Qwen3-8B, `N=8`, `T=4`, BM25 plus MedCPT-Cross-Encoder over MedCorp3 (PubMed, Textbooks, and Wikipedia). The unavailable/corrupt StatPearls component was not substituted.
- Counterfactual sidecar: Llama-3.1-8B-Instruct, unchanged Profile-no-document and CPG definitions, and exact option-sequence likelihood.
- Fusion: per-question normalized base/Profile/CPG scores and the small frozen linear models in `fusion_config.json`. Development fit the entropy temperature (`0.05000032401354733`) and linear weights; calibration selected zero L2 penalty; the fresh test was evaluated once without refitting.
- Invalid outputs remain invalid. No baseline fallback, preserve default, hard safety gate, or gold-dependent tie resolution is used.

The official extrinsic MA-RAG evaluator was not run because no official evaluator checkpoint was locally available. No substitute evaluator was trained.

#### Fresh-test results

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | CHR | Net correction | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MA-RAG-int trap | 39.2% | 17.6% | 66.76% | 0 | 0 | 0.00% | 0.0 points | 8 |
| MA-RAG pair prompt | 50.2% | 30.2% | 49.00% | 86 | 31 | 15.82% | +11.0 points | 3 |
| Profile-only | 79.4% | 42.8% | 12.19% | 226 | 25 | 12.76% | +40.2 points | 0 |
| CPG-only | 57.8% | 35.6% | 20.79% | 162 | 69 | 35.20% | +18.6 points | 16 |
| MA-RAG + Profile uniform | 50.6% | 27.0% | 51.58% | 58 | 1 | 0.51% | +11.4 points | 1 |
| MA-RAG + Profile + CPG uniform | 66.0% | 40.2% | 32.66% | 136 | 2 | 1.02% | +26.8 points | 1 |
| **MA-RAG + learned CF adapter** | **80.0%** | **52.6%** | **13.18%** | **210** | **6** | **3.06%** | **+40.8 points** | **1** |
| Adapter without MA-RAG | 81.8% | 55.0% | 8.31% | 229 | 16 | 8.16% | +42.6 points | 1 |
| MedRGAG-style baseline | 40.8% | 17.6% | 60.54% | 0 | 0 | 0.00% | 0.0 points | 0 |
| **MedRGAG + learned CF adapter** | **82.4%** | **47.0%** | **10.88%** | **220** | **12** | **5.88%** | **+41.6 points** | **0** |
| Adapter without MedRGAG | 81.8% | 46.8% | 10.88% | 217 | 12 | 5.88% | +41.0 points | 0 |

Repairs and harms use each method's named base framework. Original-correct preservation is 96.94% for the MA-RAG adapter and 94.12% for the MedRGAG adapter. The metric identities `net = final accuracy - base accuracy`, `CHR = 1 - OCP`, and `repairs - harms = final correct - base correct` hold for every method.

##### Invalid-output accounting

The MA-RAG trap baseline has eight invalid predictions: seven exact 4-4 vote ties and one runtime-invalid case (`case_53912`). The runtime case entered the upstream unbounded formatting retry because a thinking response lacked `</think>`; its partial directory was preserved and the case was explicitly marked invalid. The portable adapter can use the complete, finite option distributions from exact vote ties, but it cannot use the runtime-invalid case, so it has one invalid prediction.

Five of the 210 corrections counted by the metric come from correctly resolving complete base vote ties. They are not official prediction flips, because the official majority result is invalid on a tie. Excluding all seven tied rows leaves a similarly large gain (395/492 adapter-correct versus 196/492 MA-RAG-correct), so the conclusion is not driven by invalid handling. Control MA-RAG has five exact ties; the pair-prompt baseline has three.

#### Statistical comparisons and controls

All intervals below use 1,000 paired bootstrap resamples.

| Comparison | Accuracy difference (95% CI) | Pair-accuracy difference | BTR difference | CHR difference (95% CI) |
|---|---:|---:|---:|---:|
| MA-RAG adapter - MA-RAG | +40.8 [+36.6, +45.4] | +35.0 | -53.58 | +3.06 [+1.01, +5.56] |
| MedRGAG adapter - MedRGAG | +41.6 [+37.0, +46.2] | +29.4 | -49.66 | +5.88 [+3.05, +9.19] |
| MA-RAG adapter - pair prompt | +29.8 [+25.2, +34.6] | +22.4 | -35.82 | -12.76 [-17.91, -7.85] |
| MA-RAG adapter - Profile-only | +0.6 [-2.4, +3.8] | +9.8 | +0.99 | -9.69 [-14.21, -5.61] |
| MA-RAG adapter - adapter without MA-RAG | -1.8 [-4.2, +0.4] | -2.4 | +4.87 | -5.10 [-8.37, -2.13] |

The required mechanism shuffles all reduce performance:

| Adapter signal | Accuracy | Real-minus-shuffle difference | 95% CI |
|---|---:|---:|---:|
| Real adapter | 80.0% | — | — |
| Shuffled delta | 50.0% | +30.0 points | [+25.2, +35.2] |
| Shuffled profile | 42.4% | +37.6 points | [+32.6, +42.4] |
| Shuffled CPG edit | 73.0% | +7.0 points | [+4.0, +10.0] |

Thus the learned result depends on the real state delta, diagnosis profile, and CPG edit. It is not explained merely by adding another score vector.

#### MA-RAG false consensus

On the fresh test, 459/500 questions (91.8%; 93.29% among the 492 valid official predictions) end with a unanimous MA-RAG candidate pool. Of all 500 questions, 273 (54.6%; 55.49% among valid) are wrong-unanimous stops and 186 (37.2%) are correct-unanimous stops. Profile disagrees with 59.69% of unanimous pools and CPG disagrees with 56.53% of the 444 unanimous cases where CPG is available. The first-round candidate-conflict rate is 50.41% among valid cases; among the 244 first-round no-conflict cases, Profile supplies a conflicting state signal 58.20% of the time.

The post-hoc learned adapter corrects 190/273 false-consensus cases (69.60%). This supports the existence of MA-RAG's error-consensus blind spot, but it does not by itself validate the native trigger.

#### Native MA-RAG experiments: development/calibration only

The user-approved final scope stopped fresh native inference. The already completed native development/calibration experiments are retained as non-confirmatory diagnostics:

| Native method | Dev accuracy (N=400) | Dev repairs/harms | Calibration accuracy (N=150) | Calibration repairs/harms |
|---|---:|---:|---:|---:|
| MA-RAG-int | 53.75% | 0/0 | 48.67% | 0/0 |
| CF trigger only (`t=1`) | 53.75% | 0/0 | 48.67% | 0/0 |
| Delta-query only | 57.50% | 25/10 | 50.00% | 6/4 |
| CF history ranking (`beta_profile=0`, `beta_cpg=1`) | 55.75% | 21/13 | 48.00% | 6/7 |
| Full native CF-MA-RAG | 54.00% | 17/16 | 50.00% | 7/5 |
| Full native + portable adapter | 81.00% | 122/14 vs full native | 82.00% | 49/1 vs full native |

The pure trigger produces no repairs. Delta-aware retrieval is directionally positive on both splits but remains far below the portable adapter. History ranking reverses direction on calibration. The full native method gives only +0.25/+1.33 accuracy points over MA-RAG on development/calibration. Fresh native, direct-Qwen, and three-seed robustness were not run after the user narrowed the final scope to the portable core experiment, so no confirmatory native-mechanism claim is made.

#### Cost and static compatibility

The portable adapter is post-hoc: it does not add MA-RAG rounds, retrieval queries, or documents. Its CPU normalization and linear fusion cost is negligible. For the 499 MA-RAG trap cases with complete cost logs, the base averages are 1.910 rounds, 15.279 candidate generations, 3.639 retrieval queries, 6.968 documents, 6,539 generated tokens, and 54.29 seconds of per-question wall time.

The shared Llama sidecar ran from 13:12:27 to 17:51:19, or about 4 h 38 m 52 s for 500 pairs (about 33.5 seconds per pair in pipeline throughput). Its recorded generation-stage completion-token total across M0 plus M2 summary/explore/generate/select is 3,312,304, or 6,624.6 tokens per pair. Exact sequence-likelihood passes are additional and do not expose a compatible token counter. The sidecar is computed once and shared by both base frameworks.

Static applicability is deterministic. The prior RiskRoute-CF static control explicitly verifies that, on 400 ReMedQA rows, the MedRGAG static path and adapter-bypass path are identical prediction by prediction: 71.0% accuracy, 53.0% ReAcc, and 60.0% ReCon. On the existing 100-item MA-RAG MedQA check, the adapter bypass is a pass-through of the stored unmodified baseline by construction: 100/100 predictions are identical, with 72.0% accuracy and four explicit vote ties. This is not a second stochastic rerun and is applicability isolation, not a learned safety guarantee.

#### Answers to the required report questions

1. **Was official MA-RAG-int reproduced successfully?** Operationally yes under the available MedCorp3 corpus. The 100-item MedQA check completed candidate generation, retrieval, round logging, early stopping, and official majority evaluation at a plausible 72.0%. It is a small `N=4,T=2` interface check, not an exact full-MedCorp or full-table reproduction.
2. **MA-RAG accuracy on paired four-option MedEinst?** 39.2% trap accuracy (`N=500`, eight invalid outputs counted as incorrect).
3. **Wrong unanimous consensus frequency?** 273/500, or 54.6%.
4. **Does Profile-only outperform MA-RAG?** Yes, 79.4% versus 39.2%.
5. **Does the portable adapter outperform MA-RAG?** Yes, by 40.8 points with CI entirely above zero.
6. **Does it outperform pair-aware MA-RAG?** Yes, by 29.8 points with CI entirely above zero.
7. **Does the full adapter outperform Profile-only?** Numerically by 0.6 points, but not significantly.
8. **Does removing MA-RAG scores reduce performance?** No. It increases accuracy by 1.8 points; MA-RAG synergy is not supported.
9. **Do real delta, profile, and CPG signals beat shuffles?** Yes; the gains are +30.0, +37.6, and +7.0 points, with all three confidence intervals above zero.
10. **Does the native residual trigger repair false consensus?** Not on development/calibration: the selected pure trigger makes zero repairs and zero harms.
11. **Does delta-aware retrieval help beyond the portable adapter?** Not established. It is modestly positive against native MA-RAG on development/calibration, but much weaker than the adapter and has no fresh-test confirmation.
12. **Does counterfactual history ranking help?** Not stably: +2.0 points on development and -0.67 on calibration.
13. **Additional cost?** No extra MA-RAG rounds/documents/queries for the portable adapter; one shared 4 h 38 m 52 s Llama sidecar run for 500 pairs, plus negligible CPU fusion.
14. **Does the same adapter improve MedRGAG on the identical fresh test?** Yes, +41.6 points with CI entirely above zero.
15. **Is cross-framework counterfactual transfer supported?** Yes, under this same four-option, pair-aware protocol.
16. **Is genuine MA-RAG synergy supported?** No. The without-MA ablation is stronger.
17. **Is a world-model claim supported?** No. This is a counterfactual residual adapter, not a clinical world model.

#### Files and limitations

The public result files contain the frozen splits, dataset map, parsed rounds, continuous option scores, sidecar scores, frozen fusion configuration, predictions, metrics, bootstrap intervals, false-consensus rows, efficiency rows, static compatibility check, and exact command record. Expensive intermediate retrieval and generation caches remain under the ignored `results_marag_cf/cache/` directory.

The principal limitations are the pair-aware MCQ proxy, construction-source alignment between MedEinst and DDXPlus profiles, different Qwen/Llama base models across the two branches, one 500-pair confirmatory seed, and the absence of fresh native/seed-robustness runs. The result establishes portability of the CF sidecar across base-framework interfaces, not synergy, official benchmark SOTA, clinical safety, or deployment readiness.

<a id="record-0279"></a>

## README.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/chatgpt_handoff_2026-09-05/README.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/chatgpt_handoff_2026-09-05/README.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/chatgpt_handoff_2026-09-05`。

### CF medical-RAG project: evidence handoff for ChatGPT

Current local classified benchmark (2026-09-09):
[v3 exclusive R1–R5](/home/data3/txy/docs/data/construction.md#record-0316),
3,105 units with complete M0/M1 results. Read the v3 loading example in
`/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md`. This handoff preserves the
2026-09-05 adapter snapshot; its methods, results and commands are historical.

Snapshot date: 2026-09-05 (Asia/Shanghai)

Repository: `https://github.com/xiotakut/cf_mrg`

Canonical repository commit before this handoff: `53aaff676439066f8d0b6478404c91e7ece3528f`

This document collects what the repository and the visible conversation history can actually answer about datasets, prior use, current methods, results, hardware, runtime, and budget. It is an evidence handoff, not a new literature review or a new experiment.

Two reading rules matter:

1. Early files such as [`ARCHIVED_CF_WM_MEDRGAG_IMPLEMENTATION_CONTRACT.md`](/home/data3/txy/docs/archive/cf_wm.md#record-0269) and the old world-model plans describe a historical project stage. They are not the current claim.
2. The canonical result at this snapshot date was the CF-Residual Adapter report in [`results_marag_cf/summary.md`](/home/data3/txy/docs/archive/cf_residual_adapter.md#record-0278). It supports a pair-aware four-option MedEinst result, not a general medical counterfactual, SOTA, safety, or world-model claim.

#### 1. What the requested audit material can and cannot provide

| Requested information | Availability | Evidence or limitation |
|---|---|---|
| Initial “five CF test sets” | Available, but the phrase is ambiguous | The historical stack had five **roles**, while the fifth role contained more than one named control dataset. See Section 2. |
| Dataset versions, sizes, and actual usage | Available | Source revisions are in [`GATE_A_RESULTS.md`](/home/data3/txy/docs/archive/cf_wm.md#record-0266); actual inference runs are summarized below. |
| Exact IDs used in later MedEinst splits | Available in committed JSONL files | Every relevant row contains `source_case_id`; Section 4 lists the files and overlap audit. |
| Latest result table and frozen configuration | Available | [`summary.md`](/home/data3/txy/docs/archive/cf_residual_adapter.md#record-0278), [`metrics.json`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/metrics.json), and [`fusion_config.json`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/fusion_config.json). |
| Adapter-visible fields and fairness boundary | Available | Section 5 distinguishes trap-only MA-RAG, pair-prompt MA-RAG, and the pair-aware sidecar. |
| Hardware and stage timing | Mostly available | Exact server inventory and logged stage spans are in Section 7. The reboot downtime was not separately timestamped. |
| Numeric compute or money budget | **Not specified** | The user later stopped fresh native/direct/three-seed work and requested the core adapter only, but gave no GPU-hour, wall-time, or paid-API cap. |
| Systematic literature coverage | **Not available** | [`references/SOURCES.md`](/home/data3/txy/docs/archive/cf_wm.md#record-0353) is a project source list, not a PRISMA-style search ledger. Claims in the supplied ChatGPT literature discussion still require independent verification. |

#### 2. What “the original five datasets” meant

The historical recommended stack numbered five benchmark roles:

1. MedPIC-Bench
2. CLIR-Bench
3. MedEinst
4. MedCounterFact
5. An answer-invariant control role: ReMedQA plus CPV/MedEqualQA

The fifth role was not one dataset. In the actual Gate-A preparation, ReMedQA and CPV were frozen separately, so there were **six named public sources**. MedEqualQA was discussed as an alternative but was not run in the committed experiments. CLADDER and CP-Env were optional extensions and were not part of the end-to-end result.

##### 2.1 Frozen public-source inventory

These are preparation counts, not all inference counts.

| Dataset | Pinned revision | Upstream/raw size observed | Gate-A prepared subset | Unit |
|---|---|---:|---:|---|
| MedPIC | `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983` | 467 | 467 | rows; no released official linked-pair map was found |
| CLIR | `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` | 3,000 rows in the pinned snapshot | 500 | t6–t10, 100 rows each; only t6/t8 had safely usable observations |
| MedEinst | `354f4b527e764a8f2bebea8f71be55e0a6966402` | 10,766 | 500 pairs / 1,000 rows | paired cases; upstream total is 5,383 pairs |
| MedCounterFact | `f35b98063b51a63e677829b6d173029d98dd3b1e` | 1,012 | 200 pairs / 400 rows | four categories, 50 pairs each |
| ReMedQA | `3abb4b47a5859c7b46c0a1872a58c82e2e3029e3` | 5,036 | 300 source IDs / 1,200 rows | four variants per selected ID |
| CPV | `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5` | 12,310 | 300 case IDs / 3,010 rows | demographic variants |

Important caveats already recorded in Gate A:

- preparation stopped before the planned full inference because MedPIC lacked the expected linked-pair map and CLIR lacked planned Full-TS/edit-pair assets;
- MedCounterFact and ReMedQA redistribution/license terms still required upstream verification;
- the config calls CLIR’s broader official size 6,600, while the pinned raw snapshot used by Gate A contained 3,000 rows. This discrepancy has not been resolved here.

The raw public-source cache is deliberately ignored by Git and is not on GitHub. The committed Gate-A reports preserve revisions, counts, and hashes.

##### 2.2 What was actually passed through model inference

| Stage | MedPIC | CLIR | MedEinst | MedCounterFact | ReMedQA | CPV | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| balanced60 Gate-B pilot | 10 | 10 | 20 | 16 | 2 | 2 | Single-seed 60-item pilot; NO-GO for the old world-model route |
| revised gold-free heldout | 78 | 79 | 72 | 74 | 0 | 0 | 303 items after contract-debug exclusions; world-model result negative |
| CF-KADS-MoE secondary evaluation | 467 | 0 | see Section 4 | 0 | 400 rows | 0 | MedPIC row-level result negative; ReMedQA static control |

The balanced60 result is in [`GATE_B_D_RESULTS.md`](/home/data3/txy/docs/archive/cf_wm.md#record-0267). The 303-item result is preserved at commit `b714735`; its current artifacts remain under [`results/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results). The later MedPIC and ReMedQA results are in [`results_cfmoe/summary.md`](/home/data3/txy/docs/archive/cf_method_trials.md#record-0276).

Consequently, the repository does **not** contain a successful five-dataset counterfactual result. It contains:

- a negative small multi-dataset world-model experiment;
- a negative full-row MedPIC transfer attempt;
- a ReMedQA static compatibility/control result;
- extensive positive evidence concentrated on a pair-aware four-option MedEinst protocol.

#### 3. Project trajectory and what each stage established

| Commit | Date | Experiment | Main data | Outcome |
|---|---|---|---|---|
| `b714735` | 2026-08-25 | Revised gold-free transition/world-model experiment | 303 items across MedPIC, CLIR, MedEinst, MedCounterFact | Negative: full transition 20.8%, below local MedRGAG proxy 31.7% |
| `f2652d0` | 2026-08-27 | DeltaRev-MedRGAG | 40 dev + 160 test MedEinst pairs | No useful repair; heavy fail-closed behavior; no world-model support |
| `c5b20e2` | 2026-08-27 | DeltaRank-MedRGAG | 300 dev + 300 test pairs | Four-way MedRGAG 45.33%; residual +1.0 point with 5 repairs/2 harms; not a strong positive result |
| `9768abe` | 2026-08-28 | CFShift-MedRGAG | 800 dev + 200 cal + 500 fresh pairs | Profile signal strong; pure CF shift only +0.2 point over target margin and CI crossed zero |
| `1b95f9b` | 2026-08-29 | CF-KADS-MoE | reused 800/200 + 1,000 fresh pairs | Profile-no-document 77.7%; learned fusion 78.5%, only +0.8 point and not significant; MedPIC transfer negative |
| `212866d` | 2026-08-31 | RiskRoute-CF | reused 800/200 + a new 1,000-pair test | Risk-aware router 73.3% versus Profile 74.3%; no Pareto/safety-aware success |
| `53aaff6` | 2026-09-03 | CF-Residual Adapter on MA-RAG | reused 400/150 + 500 later test pairs | Large cross-interface gain, but no MA-RAG synergy; details in Section 6 |

The important scientific trajectory is therefore narrower than “a general CF system improved five datasets”:

> Repeated MedEinst experiments found that the control-to-trap score shift plus DDXPlus disease-profile alignment is powerful. Evidence-selection and risk-routing additions did not reliably beat the profile expert. The latest work attached that same sidecar to a second base interface, MA-RAG, where it again dominated the base but did not benefit from MA-RAG’s own scores.

#### 4. Exact MedEinst split reuse and data lineage

Every modern MedEinst JSONL row represents one **pair** containing both a control and a trap narrative. “500 pairs” therefore means 500 JSONL rows and 1,000 case narratives. MA-RAG additionally converts every pair into three model records: control, trap, and pair prompt.

##### 4.1 Committed split files

| Experiment | Development | Calibration | Test/fresh | Relationship |
|---|---:|---:|---:|---|
| DeltaRev | 40 | — | 160 | [`results/deltarev.gold.jsonl`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results/deltarev.gold.jsonl) |
| DeltaRank | 300 | — | 300 | [`results_deltarank/dev.jsonl`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank/dev.jsonl), [`test.jsonl`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank/test.jsonl) |
| CFShift | 800 | 200 | 500 | [`results_cfshift/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfshift) |
| CF-KADS-MoE | 800 | 200 | 1,000 | Dev/cal are exactly CFShift’s sets; fresh is new |
| RiskRoute-CF | same 800 | same 200 | 1,000 | Reuses CF-MoE training/calibration features; `new_test.jsonl` is new |
| MA-RAG CF-Residual | 400 | 150 | 500 | Dev is first 400 of the reused 800; cal is first 150 of the reused 200; later test selected with seed 223 |

Development reuse is intentional and extensive:

- all 300 DeltaRank development source IDs are inside the later 800-row CFShift/CF-MoE development set;
- CFShift and CF-MoE development sets are identical (800/800), as are their calibration sets (200/200);
- MA-RAG development contains the first 400 of those 800 and MA-RAG calibration the first 150 of those 200;
- RiskRoute also learned from the same 800/200 asset family.

This is acceptable as iterative development, but these are not independent confirmations.

##### 4.2 Later test sets and legacy exposure

The five later test files are pairwise disjoint by `source_case_id`:

- DeltaRank: 300
- CFShift: 500
- CF-KADS-MoE: 1,000
- RiskRoute: 1,000
- MA-RAG CF-Residual: 500
- total: 3,300 distinct later-test source IDs

However, the earlier DeltaRev 160-pair test was not included in the later exclusion code. Of those 160 old test IDs, 115 were subsequently reused:

| Later test | Overlap with old DeltaRev test |
|---|---:|
| DeltaRank 300 | 25 |
| CFShift 500 | 38 |
| CF-KADS-MoE 1,000 | 18 |
| RiskRoute 1,000 | 27 |
| MA-RAG CF-Residual 500 | 7 |

The current MA-RAG fresh set also contains one exact pair previously present in the older CFShift/CF-MoE calibration set: `case_180796`. A second matching ID, `case_36868`, occurs in an older training file with different narratives and labels; that one is an ID-namespace collision rather than the same pair. `case_36868` was nevertheless also present in the old DeltaRev asset.

This means the wording “excluded every source ID used by DeltaRank, CFShift, CF-KADS-MoE, RiskRoute, development, or calibration” in the existing latest summary is too broad. The selection code actually excludes:

- the four named later **test** files;
- the current MA-RAG 400/150 development/calibration subsets.

It does not exclude the older DeltaRev file or the unused tails of earlier development/calibration files. See `excluded_source_ids()` in [`prepare_marag_medeinst.py`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py).

This newly documented issue does not numerically explain the large latest gain. A conservative offline sensitivity that removes all eight MA fresh IDs seen anywhere in old DeltaRev plus the additional prior-calibration duplicate leaves 491 pairs:

| Method | Original 500 | Conservative 491 |
|---|---:|---:|
| MA-RAG | 39.2% | 39.51% |
| MA-RAG + adapter | 80.0% | 79.84% |
| Profile-only | 79.4% | 79.02% |
| Adapter without MA-RAG | 81.8% | 81.87% |
| MedRGAG | 40.8% | 40.53% |
| MedRGAG + adapter | 82.4% | 82.48% |

On the 491-row sensitivity, paired-bootstrap accuracy differences remain large:

- MA-RAG adapter minus MA-RAG: +40.33 points, 95% CI +35.64 to +44.81;
- MedRGAG adapter minus MedRGAG: +41.96 points, 95% CI +37.27 to +46.84.

This sensitivity is an audit calculation only: no model was refit or rerun, and it has not replaced the committed primary metrics.

The full ID lists remain in their canonical JSONL files. They can be extracted without copying clinical text, for example:

```bash
jq -r '.source_case_id' cf_medrgag_validation_pack/results_marag_cf/fresh_test.jsonl
```

#### 5. What the current adapter actually sees

The latest experiment mixes three distinct information conditions. They must not be described as equivalent.

| Method/input path | Sees trap case | Sees control case | Sees structured delta | Sees another model’s scores |
|---|---:|---:|---:|---:|
| `marag_int_trap` | yes | no | no | no |
| `marag_int_control` | no | yes | no | no |
| `marag_int_pair_prompt` | yes | yes | yes | no |
| `profile_only` / sidecar | yes | yes | yes | Llama option likelihoods and DDXPlus profiles |
| `marag_cf_learned` | yes | yes | yes | MA-RAG vote/entropy scores plus the Llama sidecar |
| `medrgag_cf_learned` | yes | yes | yes | MedRGAG score vector plus the same Llama sidecar |

Therefore:

- the main adapter is **pair-aware**, not an independent single-case diagnostic method;
- the trap-only MA-RAG baseline has less information;
- the pair-prompt baseline is the direct control for seeing both cases and reaches 50.2%, well below the adapter’s 80.0%;
- pair-prompt does **not** equalize the extra Llama compute. A same-model/same-budget non-CF ensemble control has not been run and is an important missing attribution experiment.

##### 5.1 Four-option construction

Every pair uses:

- the trap diagnosis;
- the control diagnosis;
- two deterministic hard negatives selected by DDXPlus profile overlap;
- one frozen A–D mapping shared by all methods for that pair.

Gold labels are used to construct the MCQ and to train/evaluate the small linear model, as in ordinary supervised MCQ experiments. They are not inserted into solver, retrieval, profile-query, or native-ranking prompts. This is a **four-option MedEinst proxy**, not the upstream open-diagnosis task.

##### 5.2 Sidecar scores

The strongest single expert is `profile_no_document`. Up to an option-independent constant, its score is:

```text
2 * direct_trap_score(option)
- direct_control_score(option)
+ 2 * standardized_delta_profile_score(option)
```

The profile term matches added/new findings positively and removed/old findings negatively against DDXPlus disease profiles. It does not use MA-RAG documents.

`cpg_core` borrows the counterfactual edit/probability-gap idea from `FAIRHealth/clinical-counterfactual-reasoning` at commit `265d1aea88f705063bb7ff2d686547d373da7e09`. This project uses deterministic remove/revert/negate edits of at most two ordered delta findings and exact option-sequence likelihood differences. It does **not** reproduce the full multi-agent discussion framework. The five-case official-code compatibility pilot was excluded from the fusion claim.

##### 5.3 Learned fusion

For MA-RAG, the frozen per-option feature groups are:

```text
MA-RAG vote score
MA-RAG entropy-weighted vote score
Profile score
CPG score
vote x consensus
entropy vote x rounds
Profile x MA-RAG agreement
Profile x Profile margin
CPG x availability
```

Development fits the entropy temperature and linear weights. Calibration selects L2 from `{0, 0.01, 0.1, 1}`. The chosen L2 is zero. The fresh test is evaluated once without refitting. Exact weights are in [`fusion_config.json`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/fusion_config.json).

There is no neural router, hard preserve/revise gate, silent baseline fallback, or gold-dependent tie resolution in the latest portable main method.

#### 6. Latest MA-RAG/MedRGAG results and the correct claim boundary

##### 6.1 Configuration

| Component | Actual configuration |
|---|---|
| MA-RAG code | Upstream commit `423f031cc0ffca679a047c885be999b9604100a9` plus two recorded logging/retriever compatibility patches |
| MA-RAG backbone | local Qwen3-8B |
| Candidate/round budget | `N=8`, `T=4` |
| Solver | thinking disabled, default temperature 0.7, max 2,048 new tokens |
| Conflict query generator | thinking enabled, temperature 0, max 8,192 new tokens |
| Retrieval | BM25 + MedCPT-Cross-Encoder |
| Corpus | **MedCorp3**: PubMed, textbooks, Wikipedia; StatPearls was corrupt/unavailable and not silently substituted |
| Sidecar | local Llama-3.1-8B-Instruct, exact option-sequence likelihood, Profile and CPG |
| Development/calibration/test | 400 / 150 / 500 pairs |
| Fresh sampling seed | 223 |
| Bootstrap | 1,000 paired resamples |

MA-RAG’s checked-out script default is `T=8`; this experiment explicitly ran `T=4`. It is an intentional cost-effective setting from the experiment prompt, not an exact reproduction of the repository default or the paper’s full benchmark table. The available intrinsic implementation was used. The extrinsic evaluator was not run because its official checkpoint was unavailable.

The MedRGAG branch is a local all-Llama implementation/proxy. It must not be called an exact reproduction of any mixed-model paper configuration without a separate paper/code audit.

##### 6.2 Fresh 500-pair result

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| MA-RAG trap | 39.2% | 17.6% | 66.76% | — | — | 8 |
| MA-RAG pair prompt | 50.2% | 30.2% | 49.00% | 86 | 31 | 3 |
| Profile-only | 79.4% | 42.8% | 12.19% | 226 | 25 | 0 |
| MA-RAG + learned adapter | 80.0% | 52.6% | 13.18% | 210 | 6 | 1 |
| Adapter without MA-RAG | **81.8%** | 55.0% | 8.31% | 229 | 16 | 1 |
| MedRGAG | 40.8% | 17.6% | 60.54% | — | — | 0 |
| MedRGAG + learned adapter | **82.4%** | 47.0% | 10.88% | 220 | 12 | 0 |
| Adapter without MedRGAG | 81.8% | 46.8% | 10.88% | 217 | 12 | 0 |

Main paired-bootstrap comparisons:

- MA-RAG + adapter minus MA-RAG: +40.8 points, 95% CI +36.6 to +45.4;
- MedRGAG + adapter minus MedRGAG: +41.6 points, 95% CI +37.0 to +46.2;
- MA-RAG + adapter minus pair prompt: +29.8 points, 95% CI +25.2 to +34.6;
- MA-RAG + adapter minus Profile-only: +0.6 points, 95% CI -2.4 to +3.8;
- MA-RAG + adapter minus adapter without MA-RAG: -1.8 points, 95% CI -4.2 to +0.4.

Mechanism shuffles reduce MA adapter accuracy from 80.0% to:

- 50.0% with shuffled delta;
- 42.4% with shuffled profile;
- 73.0% with shuffled CPG edit.

All three real-minus-shuffle confidence intervals are above zero.

##### 6.3 False consensus

- 459/500 MA-RAG final pools are unanimous;
- 273/500 are wrong-unanimous;
- the post-hoc adapter corrects 190/273 of those wrong-unanimous cases.

This demonstrates that the post-hoc state signal can expose errors missed by answer-to-answer agreement. It does not validate the native trigger by itself.

The native development/calibration diagnostics were weak:

- pure trigger: no repairs and no harms;
- delta-query: +3.75 points on dev and +1.33 on calibration;
- history ranking: +2.0 on dev and -0.67 on calibration;
- full native: +0.25 on dev and +1.33 on calibration.

Fresh native inference was stopped when the user narrowed the scope.

##### 6.4 What may and may not be claimed

Supported, with the data-lineage caveat in Section 4:

> The same pair-aware counterfactual sidecar produces large gains over two different medical-RAG base interfaces under one four-option MedEinst protocol.

Not supported:

- genuine synergy with MA-RAG: removing MA-RAG scores is numerically better;
- broad cross-dataset transfer: MedPIC was negative and the latest positive test is MedEinst only;
- improvement on MA-RAG’s original benchmark suite;
- official open-diagnosis MedEinst SOTA;
- a clinical safety guarantee;
- a clinical world model.

The most conservative interpretation is that the Llama pair-aware Profile/CPG sidecar is strong on this constructed MedEinst MCQ, while the base MA-RAG distribution contributes no demonstrated incremental value.

#### 7. Hardware, software, and runtime

##### 7.1 Server inventory

Inventory queried on the same server on 2026-09-05:

| Resource | Value |
|---|---|
| GPU | 4 × NVIDIA H20, 97,871 MiB each |
| Driver | 570.133.20 |
| CPU | Intel Xeon Platinum 8469C, 48 physical cores / 96 threads |
| RAM | 491 GiB |
| Swap | none |
| OS/kernel | Linux 5.15.0-144-generic, x86_64 |
| Main inference stack | vLLM 0.8.5, PyTorch 2.6.0 |
| Base environment Transformers | 5.16.1 |
| Sidecar compatibility path | pinned Transformers 4.51.3 via `/home/data3/txy/.cache/marag_pydeps` |

Qwen services used GPUs 1 and 2 with:

```text
dtype=bfloat16
max_model_len=32768
max_num_seqs=16
gpu_memory_utilization=0.82
seed=223
prefix caching enabled
```

Four dataset shards ran concurrently, two client runners per Qwen service, each with `num_workers=8`. GPU 3 hosted the BM25/MedCPT retrieval service. During fresh evaluation GPU 0 ran the Llama sidecar with `gpu_memory_utilization=0.55`; its code default was a 32k context.

##### 7.2 End-to-end visible timeline

The first smoke artifact was written at 2026-09-02 16:44:31 and the final commit at 2026-09-03 19:24:48: a visible window of about 26 h 40 m. Exact reboot downtime was not logged separately.

| Phase | Artifact span | Wall time | Work |
|---|---|---:|---|
| Environment, original MedQA check, smoke, pilot | 09-02 16:44–21:50 | about 5 h visible window | 450 official pilot item-runs plus 1,603 native/grid artifacts; some work overlapped |
| Formal MA-RAG dev/cal base | 09-02 22:08–09-03 04:45 | 6 h 37 m | 1,650 item-runs |
| Parse, fit, freeze | 04:47–04:50 | minutes | entropy temperature, linear weights, L2 selection |
| Formal native dev/cal | 04:53–13:05 | 8 h 12 m | four variants × 550 pairs = 2,200 method/item runs |
| Fresh Qwen control/trap/pair | 13:11–18:43 | 5 h 32 m | 1,500 item-runs |
| Fresh Llama sidecar | 13:12–17:51 | 4 h 38 m 52 s | ran concurrently with fresh Qwen; do not add it again to wall time |
| Evaluation, report, verification, commit | 18:46–19:24 | about 38 m | metrics, bootstrap, tests, documentation |

The earlier “5–6 hour” estimate referred only to the remaining fresh core stage. It did not describe the already elapsed pilot/formal/native work.

##### 7.3 Why the base inference is expensive

One MA-RAG item is not one model answer. It generates eight solver candidates, may generate conflict queries, retrieves and reranks documents, then generates another eight candidates for each additional round.

Across only the formal and fresh **unchanged MA-RAG base** runs, excluding pilot, native variants, and sidecar:

| Quantity | Formal dev/cal | Fresh | Combined |
|---|---:|---:|---:|
| MA-RAG item-runs | 1,650 | 1,500 | 3,150 |
| Candidate answers | 24,584 | 21,288 | 45,872 |
| Retrieval queries | 5,692 | 4,640 | 10,332 |
| Retained/retrieved documents | 10,814 | 8,896 | 19,710 |
| Generated tokens | 11,259,265 | 9,272,035 | 20,531,300 |
| Sum of per-item wall time | 25.08 h | 20.91 h | 45.99 h |

Parallel shards compressed those approximately 46 summed item-hours into about 12.1 elapsed hours. The server was heavily utilized; the task was simply much larger than an interactive single-inference job.

Formal native dev/cal consumed another 8 h 12 m. Its artifacts contain 36,928 candidate slots and about 16.38 million recorded candidate-pool tokens, but the first-round pools were reused, so these figures must not be interpreted as all newly generated work.

##### 7.4 Sidecar timing

For 500 fresh pairs:

| Sidecar stage | Time |
|---|---:|
| Retrieval plus MedRGAG M0/M2 baseline stages | about 1 h 43 m |
| Exact four-option likelihood scoring | about 47 m |
| Delta matching and document scoring | about 7 m |
| Raw CPG/expert option scoring | about 2 h 1 m |
| Assembly | about 22 s |
| Total | 4 h 38 m 52 s |

The generation stages recorded 3,312,304 completion tokens. Exact sequence-likelihood passes are additional and did not expose a compatible token counter. The sidecar was computed once and shared between the MA-RAG and MedRGAG comparisons; this saves experiment cost but does not make the sidecar free at deployment.

##### 7.5 Avoidable versus scientifically necessary time

Necessary for the declared frozen core protocol:

- fit/select on development and calibration before opening fresh test;
- run the official-strength MA-RAG trap distribution;
- compute the pair-aware sidecar;
- retain pair-prompt if the adapter sees both cases;
- run one untouched test after freezing.

The largest avoidable delay was running the 8 h 12 m formal native block before the main fresh result. It was requested as a supplement, but it was not a prerequisite for the portable-transfer question. Native pilot grids also expanded before the main result. A better order would have delivered the core answer roughly 8–10 hours earlier:

```text
smoke/pilot -> formal portable fit -> fresh portable core -> optional native work
```

Minor overhead came from service reload after reboot, one Transformers incompatibility at Llama initialization, one upstream unbounded `</think>` formatting retry that was recorded invalid, and process resumption. Completed item caches prevented wholesale reruns; these were not the main source of the one-day runtime.

#### 8. Reproducibility and asset inventory

##### 8.1 Public, committed artifacts

Canonical latest files:

- exact command record: [`results_marag_cf/commands.sh`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf/commands.sh);
- frozen splits and mapping: `dev.jsonl`, `calibration.jsonl`, `fresh_test.jsonl`, `marag_dataset_map.jsonl`;
- parsed MA-RAG rounds/scores: `marag_rounds.jsonl`, `marag_option_scores.jsonl`;
- sidecar scores and model: `cf_expert_scores.jsonl`, `fusion_config.json`;
- predictions/statistics: `predictions.jsonl`, `metrics.json`, `bootstrap.json`, `false_consensus.csv`, `efficiency.csv`;
- native dev/cal diagnostics: `native_dev_cal_metrics.json`;
- static check: `static_compatibility.json`;
- two small upstream patches: `marag_logging.patch`, `marag_retriever_compat.patch`.

The exact MA-RAG operational check was 100 MedQA items at `N=4,T=2`, with 72.0% accuracy. It verified the interface, retrieval, round logs, stopping, and vote path. It was not a full-paper reproduction.

##### 8.2 Local-only expensive assets

These were intentionally not committed:

| Local asset | Approximate size | Meaning |
|---|---:|---|
| `results_marag_cf/cache/` | 92 MiB | fresh sidecar intermediates and merged fresh rounds |
| `results_cfmoe/cache/` | 865 MiB | earlier MedEinst retrieval/scoring/model caches |
| external MA-RAG base runs | 1.7 GiB | raw per-question rounds under `/home/data3/txy/MA-RAG/runs/ma-rag` |
| external MA-RAG native runs | 1.1 GiB | raw native rounds |
| local Qwen3-8B weights | about 16 GiB | not in repository |
| local Llama-3.1-8B weights | about 15 GiB | not in repository |

The official MA-RAG checkout is external at `/home/data3/txy/MA-RAG`; it remains at commit `423f031...` with the two recorded runtime patches and an untracked local corpus link. The task services were stopped after completion.

Older public result directories remain useful assets:

- [`results_deltarank/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank)
- [`results_cfshift/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfshift)
- [`results_cfmoe/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfmoe)
- [`results_riskroute/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_riskroute)
- [`results_marag_cf/`](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_marag_cf)

They should be reused for offline category/error analysis. Changing only fusion weights, thresholds, or category groupings does not require model inference. Changing retrieval, prompts, visible fields, documents, or model behavior does.

#### 9. Budget facts and missing decisions

No explicit wall-time, GPU-hour, money, or paid-model budget appears in the visible conversation. The only firm operational decision was made after the user questioned the runtime:

- continue the portable core adapter;
- do not run fresh native variants;
- do not run direct-Qwen fresh baselines;
- do not run the three-seed robustness extension.

An observed preference can be stated, but it must not be mistaken for a numeric budget:

> Prioritize the shortest experiment that answers the main scientific question; disclose cumulative elapsed time and remaining ETA separately; do not start multi-hour supplements before the core result without explicit approval.

Before another large run, the user still needs to specify:

1. maximum acceptable wall time for one exploratory run;
2. maximum aggregate GPU-hours for the project;
3. whether a same-budget extra-model control is worth its cost;
4. whether small-model training or paid APIs are allowed;
5. whether the paper’s main task is independent diagnosis or explicit paired comparison.

#### 10. Direct answers to the strategic questions in the supplied ChatGPT discussion

##### Is the current evidence broad across counterfactual categories?

No. The successful modern evidence is concentrated on answer-changing MedEinst pairs. Earlier MedPIC/CLIR/MedCounterFact experiments are either small, negative, or incompatible with the same metric. ReMedQA is a static invariance control, not an answer-changing CF success.

##### Does the repository already contain a usable category taxonomy?

Only a coarse dataset/task routing taxonomy. MedEinst stores deterministic `added_findings`, `removed_findings`, and `changed_findings`, but it does not contain a frozen, clinically audited sample-level taxonomy for negation, time, numeric change, risk factor, irrelevant attribute, and so on. Creating that taxonomy would be new work.

##### Is the latest adapter an independent diagnostic method?

No. It is explicitly pair-aware. It compares control and counterfactual cases. The base trap-only scores remain useful baselines, and pair-prompt is the fairness control for access to both cases.

##### Is transfer to MA-RAG established?

Only in the interface-level sense that the same sidecar can be attached to MA-RAG and beats its base under this protocol. Genuine synergy is not established: the adapter without MA-RAG is stronger than the adapter with MA-RAG.

##### Could the gain be ordinary model ensembling or extra compute?

That explanation is not fully excluded. Pair-prompt rules out “merely seeing the control case” as a complete explanation, and the delta/profile/CPG shuffles support the specific sidecar signals. But there is no same-extra-Llama, similar-token, non-counterfactual ensemble control. This is a high-priority missing comparison.

##### Could poor base performance be only retrieval coverage?

The current artifacts show that the no-document profile expert is much stronger than the MedRGAG/MA-RAG bases and that adding selected MedRGAG evidence previously hurt the profile expert. That is evidence against a simple “more retrieval fixes everything” account, but it is not a complete causal decomposition. The repository lacks a clinically verified sufficient-evidence oracle and document-level factuality/applicability annotations.

##### Is CPG original to this project?

No. The core edit/probability-gap idea is explicitly attributed to the FAIRHealth repository/commit above. This project’s contribution is its particular deterministic edit, option-scoring, and fusion integration—not invention of the name or general idea.

##### Can the current work support a world-model claim?

No. The old world-model experiment was negative, and the current method is a counterfactual residual adapter.

#### 11. Recommended next non-inference deliverable

Before another full run, the repository can support a low-cost audit that:

1. builds a dataset/paper/config difference matrix from verified primary sources;
2. freezes a clinically reviewed sample-level change taxonomy;
3. uses all saved predictions to measure category-specific errors without rerunning models;
4. separates retrieval absence from evidence-use failure on a small reviewed subset;
5. defines one primary mechanism and a same-budget non-CF model-ensemble control;
6. records a hard runtime/GPU budget and makes native extensions opt-in.

What should **not** happen next is an automatic Cartesian product of every dataset, category, base system, and native variant. The existing history already shows that this delays the main answer and makes attribution harder.

#### 12. Minimal verification commands

```bash
# Current revision and clean worktree
git rev-parse HEAD
git status --short

# Latest complete test sizes
wc -l \
  cf_medrgag_validation_pack/results_deltarank/test.jsonl \
  cf_medrgag_validation_pack/results_cfshift/fresh_test.jsonl \
  cf_medrgag_validation_pack/results_cfmoe/fresh_test.jsonl \
  cf_medrgag_validation_pack/results_riskroute/new_test.jsonl \
  cf_medrgag_validation_pack/results_marag_cf/fresh_test.jsonl

# Latest tests
/home/data3/txy/MedRGAG/.venv/bin/python -m unittest discover \
  -s cf_medrgag_validation_pack/tests -v

# Latest machine-readable result
jq '.methods.fresh_test // .' \
  cf_medrgag_validation_pack/results_marag_cf/metrics.json
```

No new model inference was performed to create this handoff.
