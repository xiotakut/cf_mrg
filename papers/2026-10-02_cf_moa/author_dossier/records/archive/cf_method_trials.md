# 历史：CF方法连续探索

最新状态：2026-09-14（Asia/Shanghai，文档迁移时）。按DeltaRev、DeltaRank、CFShift、CF-KADS-MoE、RiskRoute保存实际尝试、失败与结论。微弱收益、未支持的机制主张及负结果按原协议保留；不与当前独立输入v5直接比较。

[工作区总入口](/home/data3/txy/docs/README.md) · [记录归属与迁移证据](/home/data3/txy/docs/workspace.md#documentation-migration-20260914)

本文是该方向的长期主记录。下文按来源章节合入实际正文，保留历史配置、成功/失败尝试、结果与证据。历史段落中的“当前”“继续在原文件更新”和运行中状态均以其原记录日期为准；今后在本文件续写。

## 内容导航

- [9. Later counterfactual project chronology](#record-0037)
- [summary.md](#record-0273)
- [summary.md](#record-0274)
- [summary.md](#record-0275)
- [summary.md](#record-0276)
- [summary.md](#record-0277)

<a id="record-0037"></a>

## 9. Later counterfactual project chronology

来源：[MEDRGAG_WORKSPACE_GUIDE.md](/home/data3/txy/MEDRGAG_WORKSPACE_GUIDE.md)，原文第1348行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy`。

#### 9. Later counterfactual project chronology

The Git repository for the later work is:

```text
/home/data3/txy/Documents/Codex/2026-08-23/
  https-github-com-xiotakut-cf-mrg
remote: https://github.com/xiotakut/cf_mrg
branch: main
```

The experiments were iterative. Development sets and cached model outputs were
deliberately reused, so successive commits are not independent replications.

| Commit | Experiment | Data and purpose | Result |
|---|---|---|---|
| `b714735` | revised gold-free transition/WM test | 303 held-out items across MedPIC, CLIR, MedEinst, MedCounterFact | Negative: full transition 20.8%, below the local MedRGAG proxy at 31.7% |
| `f2652d0` | DeltaRev-MedRGAG | 40 development + 160 test MedEinst pairs | No useful repair; hard fail-closed behavior; no WM support |
| `c5b20e2` | DeltaRank-MedRGAG | 300 development + 300 test pairs | Four-way base 45.33%; residual +1.0 point, 5 repairs and 2 harms |
| `9768abe` | CFShift-MedRGAG | 800 development + 200 calibration + 500 fresh pairs | Profile signal strong; pure shift added only 0.2 point and its CI crossed zero |
| `1b95f9b` | CF-KADS-MoE | reused 800/200 + 1,000 fresh pairs | Profile 77.7%; learned fusion 78.5%, a nonsignificant +0.8 point; MedPIC transfer negative |
| `212866d` | RiskRoute-CF | reused 800/200 + another 1,000-pair test | Router 73.3% versus Profile 74.3%; no risk/accuracy Pareto improvement |
| `53aaff6` | CF-Residual Adapter for MA-RAG | 400 development + 150 calibration + 500 later test pairs | Large base-to-adapter gains on both interfaces; no MA-RAG synergy |
| `1e01b3a` | evidence handoff | no inference | Added the dataset-lineage, fairness, timing, asset, and missing-control audit |
| `638f1e3`, archive `6a174dc` | full-release M2 baseline | 25,280 unique inputs, five entries plus frozen sensitivity | Complete M2; native protocols, no sidecar; M0/M1 then partial |
| `79a9454`, result `3a6b5ab`, archive `d922324` | full M0/M1/M2 comparison | Same 25,280 inputs per method; 38,896 missing reader calls added | 100% all methods; M2 unchanged; heterogeneous effects, taxonomy not identifiable |

The historical adapter trajectory through 2026-09-05 was:

```text
old transition/world-model route: stopped after negative evidence
        |
        v
control-to-trap option-score change + disease profile: consistently strong
        |
        v
CPG and small forced-choice score fusion: portable sidecar
        |
        v
MedRGAG-style and MA-RAG interface evaluation on one MedEinst MCQ protocol
```

Do not describe this trajectory as five-dataset success. Its positive
evidence is concentrated on MedEinst. MedPIC transfer was negative, while
ReMedQA served as a static/invariance control.

<a id="record-0273"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results`。

### DeltaRev-MedRGAG pilot

The paired main pilot contains 200 MedEinst pairs (40 development, 160 test). MedPIC is unavailable for the paired pilot because the local official linked-pair map is absent. NICE is unavailable and was not replaced by KGCC. All answer accuracies use strict normalized exact match (NFKC, casefold, whitespace collapse, and terminal-punctuation trimming); no post-hoc clinical-equivalence rescoring was performed.

1. Old-answer persistence: 0.2125 on test, defined as the M2 trap prediction equaling its paired M2 control prediction.
2. Official changed-variable recovery: NA; MedEinst has no official edit metadata. The requested deterministic/LLM-only/hybrid three-way delta-quality comparison is not valid: LLM-only extraction had 200/200 contract failures (0 usable outputs). The main full path used deterministic/hybrid delta output and must not be read as LLM-only delta success.
3. Decision-change retrieval versus normal retrieval: ordinary triangular retrieval was higher (0.0312 vs 0.0250; difference +0.0062); full residual revision versus standard-evidence revision was tied (0.0938 vs 0.0938; difference +0.0000). Recall/MRR remain NA without decisive evidence references.
4. EA-RAG-style comparison: ordinary triangular retrieval was lower (0.0312 vs 0.0813; difference -0.0500); full residual revision versus EA-evidence revision was tied (0.0938 vs 0.0938; difference +0.0000). EA-RAG-style is a deterministic coverage-audit proxy, not an exact reproduction.
5. Source-rule upper bound: NA; no official decisive source span is local.
6. Selective revision positive net correction: False; test net=0.0, harm=0.0, preserve net=0.0, standard-evidence net=0.0, EA-evidence net=0.0.
7. Harm-budget operating points were selected on development only. At the <=2% dev-budget threshold 1.0, test harm=0.0, repairs=0, harms=0, revision coverage=0.00625, and answer-change coverage=0.00625. At the <=1% dev-budget threshold 1.0, test harm=0.0, repairs=0, harms=0, revision coverage=0.00625, and answer-change coverage=0.00625. Threshold comparison is inclusive (`score >= threshold`), so threshold 1.0 can still revise score-1.0 cases. The development budget is not a guarantee on test.
8. Baseline errors repaired: 0.
9. Baseline-correct answers damaged: 0.
10. Component diagnosis: no ablation produced a positive net-correction drop; inspect contract failures and routing before attributing a component. The most frequent recorded failure stage was `rule_extraction` (1307 proposal rows). Atomic-rule extraction contract failure was 0.7274 with nonempty rule sets on 0.2532 of rows; verifier contract failure was 0.0162. LLM-only delta extraction failed on 1.0000, while the full method's hybrid delta failed on 0.0300. Retrieval recorded 1 query errors. These are coverage/contract diagnostics only; retrieval attribution remains limited by missing official evidence references.
11. Selective counterfactual decision revision supported: False. This is not supported under the stated conservative criteria, not proof of a latent state model.
12. World-model claim: no; this is selective evidence-constrained revision.

#### Main test metrics

| Method | Strict exact-match accuracy | Harm | Net correction | Repairs | Harms | Failures |
|---|---:|---:|---:|---:|---:|---:|
| `direct` | 0.0000 | 0.0938 | -0.0938 | 0 | 15 | 1 |
| `medrgag_proxy` | 0.0938 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| `decomposition_only` | 0.1000 | 0.0500 | 0.0063 | 9 | 8 | 5 |
| `direct_counterfactual_prompt` | 0.0500 | 0.0750 | -0.0437 | 5 | 12 | 3 |
| `direct_answer_revision` | 0.0312 | 0.0938 | -0.0625 | 5 | 15 | 9 |
| `standard_question_retrieval` | 0.0250 | 0.0750 | -0.0688 | 1 | 12 | 0 |
| `candidate_specific_retrieval` | 0.0375 | 0.0688 | -0.0563 | 2 | 11 | 0 |
| `ea_rag_style_retrieval` | 0.0813 | 0.0437 | -0.0125 | 5 | 7 | 4 |
| `delta_only_retrieval` | 0.0563 | 0.0813 | -0.0375 | 7 | 13 | 4 |
| `triangular_decision_change_retrieval` | 0.0312 | 0.0688 | -0.0625 | 1 | 11 | 4 |
| `always_preserve` | 0.0938 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| `always_revise` | 0.0563 | 0.0938 | -0.0375 | 9 | 15 | 0 |
| `llm_verifier_without_evidence` | 0.0750 | 0.0563 | -0.0187 | 6 | 9 | 4 |
| `evidence_verifier_with_standard_retrieval` | 0.0938 | 0.0000 | 0.0000 | 0 | 0 | 129 |
| `evidence_verifier_with_ea_rag_retrieval` | 0.0938 | 0.0000 | 0.0000 | 0 | 0 | 124 |
| `full_deltarev` | 0.0938 | 0.0000 | 0.0000 | 0 | 0 | 118 |

MedEinst paired baseline diagnostics: control accuracy=0.1, trap accuracy=0.09375, both-correct pair accuracy=0.00625, Bias Trap Rate=0.5625 among 16 control-correct pairs, and original-diagnosis persistence=0.2125. Correct invariance is NA because all MedEinst pairs are change/trap pairs.

#### Ablation diagnostics

- `without_delta`: net=0.0000, harm=0.0000, failures=160
- `without_baseline_answer_in_query`: net=0.0000, harm=0.0000, failures=117
- `refute_only_retrieval`: net=0.0000, harm=0.0000, failures=104
- `without_preserve_evidence`: net=0.0000, harm=0.0000, failures=125
- `without_alternative_support_requirement`: net=0.0000, harm=0.0000, failures=118
- `without_entailment_check`: net=0.0000, harm=0.0000, failures=118
- `without_patient_applicability_check`: net=0.0000, harm=0.0000, failures=118
- `shuffled_delta`: net=0.0000, harm=0.0000, failures=160
- `shuffled_rule_evidence`: net=0.0000, harm=0.0000, failures=118
- `kgcc_generated_docs_as_decisive_evidence`: net=0.0000, harm=0.0000, failures=139

`without_delta` had 160/160 test contract failures and 200/200 overall relevance-stage failures; `shuffled_delta` had 160/160 test contract failures and 200/200 overall relevance-stage failures. Their zero net correction reflects fail-closed preservation, not successful mechanism evidence. More generally, the high atomic-rule extraction failure rate makes null ablation effects non-informative.

#### Paired bootstrap comparisons

- `full_deltarev_vs_always_preserve`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_medrgag_proxy`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_evidence_verifier_with_standard_retrieval`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_evidence_verifier_with_ea_rag_retrieval`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_direct_answer_revision`: accuracy difference=+0.0625, paired-bootstrap 95% CI=[+0.0125, +0.1187]

#### Gold-label oracle gate diagnostic (outside the main table)

The oracle gate could repair 2 baseline errors among already proposed full-method alternatives, with harms fixed to zero by construction because it uses test labels to revise only when correctness improves. This is analysis only and was not used for inference, threshold selection, or the main method table.

#### Limitations and expansion decision

This is a single MedEinst pilot using a local all-Llama MedRGAG proxy. MedPIC official linked pairs, official delta metadata, decisive source references, retrieval Recall/MRR, the source-rule upper bound, and NICE are unavailable. The three-way delta-quality comparison is invalid because there is no official delta reference and LLM-only extraction produced 0/200 usable outputs. Delta nonempty coverage, document coverage, EA audit coverage, and rule contract rates are operational artifact diagnostics—not official delta accuracy, evidence recall, or MRR. Accuracy is strict normalized exact match: clinically related or potentially equivalent-in-context labels such as `Bronchitis` and `Chronic Bronchitis` count as different, and no post-hoc rescoring was performed. EA-RAG-style is a proxy reproduction. Thresholds were selected on development, while test was used only for final reporting. MedCounterFact and MediEval were not run under the frozen pilot; the conservative stop decision is to diagnose the reported bottleneck before extension. CLIR remains a separate optional transition experiment.

<a id="record-0274"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_deltarank`。

### DeltaRank-MedRGAG pilot

#### Outcome

The pilot does not meet the predefined criteria for positive counterfactual ranking signal.
The residual augmentation hypothesis is not supported; a no-op is not counted as success.
No result supports a world-model claim.

#### Data and output space

Development used 300 official train/reference pairs; test used 300 official test pairs. The fixed DDXPlus ontology has 49 labels; 44 occur in the sampled data.
Structured deltas were nonempty for 293 development and 297 test pairs.

#### Main test table

| Method | Accuracy | R@5 | R@10 | Repairs | Harms | Conditional harm | Net | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy_open_medrgag | 10.33% | NA | NA | 6 | 111 | 81.62% | -35.00% | 221 |
| direct_mcq/two_way | 61.00% | NA | NA | 66 | 19 | 13.97% | 15.67% | 0 |
| medrgag_mcq_proxy/two_way | 59.00% | NA | NA | 62 | 21 | 15.44% | 13.67% | 0 |
| medrgag_mcq_proxy/four_way | 45.33% | NA | NA | 0 | 0 | 0.00% | 0.00% | 0 |
| target_only_ranker | 13.33% | 45.67% | 55.33% | 21 | 117 | 86.03% | -32.00% | 0 |
| pair_aware_ranker | 13.67% | 43.33% | 53.67% | 20 | 115 | 84.56% | -31.67% | 0 |
| delta_profile_ranker | 27.67% | 49.00% | 61.00% | 25 | 78 | 57.35% | -17.67% | 2 |
| delta_always_apply | 27.67% | NA | NA | 25 | 78 | 57.35% | -17.67% | 2 |
| delta_residual | 46.33% | NA | NA | 5 | 2 | 1.47% | 1.00% | 2 |

#### Required comparisons

1. MCQ adaptation: legacy open accuracy 10.33%; four-way MedRGAG MCQ 45.33% (difference 35.00%).
2. Two-way counterfactual accuracy: direct 61.00%; MedRGAG MCQ 59.00%.
3. Structured delta: pair-aware R@5/R@10 43.33%/53.67%; target-only 45.67%/55.33%.
4. DDXPlus profiles: delta-profile R@5 49.00% versus pair-aware 43.33%.
5–6. Always-apply produced 25 repairs and 78 harms.
7. Best development-selected residual threshold was 4; on test it produced 5 repairs, 2 harms, net 1.00%, and coverage 3.67%.
8. Shuffled-delta R@5 42.00% versus real 49.00%.
9. Shuffled-profile R@5 40.33% versus real 49.00%.
10. The main observed bottleneck is candidate generation.

#### Operating points

Best-accuracy development point: {"accuracy": 0.4866666666666667, "answer_change_coverage": 0.02666666666666667, "baseline_accuracy": 0.49, "baseline_correct": 147, "baseline_wrong": 153, "beneficial_revision_precision": 0.375, "conditional_harm_rate": 0.027210884353741496, "final_correct": 146, "harms": 4, "introduced_error_rate": 0.013333333333333334, "invalid_count": 8, "n": 300, "net_correction": -0.0033333333333333335, "original_correct_preservation": 0.9727891156462585, "repair_rate": 0.0196078431372549, "repairs": 3, "split": "dev", "threshold": 4}
Conservative point: no useful selective operating point had positive development net correction.
The full observed development margin curve is in `tradeoff.csv`; no fixed 1%/2% gate was imposed.

#### Oracle and validity diagnostics

For the delta-profile candidate set, oracle top-5/top-10 repair capacity was 39.63%/49.39%.
Invalid outputs: {"mcq": 899, "ranking": 0, "scoring": 27}. Invalid final outputs count as wrong, not as PRESERVE.

#### Limitations

This is a local all-Llama MedRGAG proxy, not the published mixed-model configuration. Hard negatives use deterministic DDXPlus profile overlap. The official train and test files observed here cover 46 of the 49 ontology labels. The 49-way scorer reranks a top-10 candidate set, so its ceiling depends on candidate recall. NICE, medication-oriented rules, the prior atomic-rule pipeline, and the prior hard conjunctive gate are not part of this active experiment.

<a id="record-0275"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfshift/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfshift/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfshift`。

### CFShift-MedRGAG results

CFShift is counterfactual preference-shift reranking, not a world model.

Data: 800 official train/reference development pairs, 200 separate calibration pairs, and 500 fresh official test pairs. The fresh set excludes all 300 inspected DeltaRank test cases.

#### Main fresh-test table

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Conditional harm | Net | Change coverage | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| direct_mcq | 46.00% | 14.40% | 62.80% | 55 | 55 | 23.91% | 0.00% | 29.60% | 0 |
| medrgag_mcq_proxy | 46.00% | 16.20% | 55.43% | 0 | 0 | 0.00% | 0.00% | 0.00% | 0 |
| direct_target_logprob | 53.60% | 20.20% | 54.23% | 82 | 44 | 19.13% | 7.60% | 30.80% | 0 |
| pair_prompt | 49.40% | 16.60% | 59.23% | 80 | 63 | 27.39% | 3.40% | 37.00% | 0 |
| target_margin_ranker | 44.20% | 16.00% | 52.28% | 35 | 44 | 19.13% | -1.80% | 20.20% | 0 |
| cf_shift_ranker | 44.40% | 20.20% | 35.27% | 46 | 54 | 23.48% | -1.60% | 28.00% | 0 |
| cf_shift_profile_ranker | 60.00% | 28.60% | 21.99% | 102 | 32 | 13.91% | 14.00% | 33.40% | 0 |
| cf_shift_profile_shuffled_control | 57.00% | 23.20% | 38.17% | 83 | 28 | 12.17% | 11.00% | 25.60% | 0 |
| cf_shift_profile_shuffled_delta | 44.40% | 21.60% | 34.02% | 58 | 66 | 28.70% | -1.60% | 31.60% | 0 |
| cf_shift_profile_shuffled_profile | 35.20% | 16.00% | 35.27% | 32 | 86 | 37.39% | -10.80% | 36.20% | 0 |
| no_medrgag_evidence | 64.40% | 30.80% | 33.46% | 120 | 28 | 12.17% | 18.40% | 36.00% | 0 |
| no_cf_shift | 44.20% | 16.00% | 52.28% | 35 | 44 | 19.13% | -1.80% | 20.20% | 0 |
| cf_shift_residual | 47.60% | 18.40% | 51.55% | 14 | 6 | 2.61% | 1.60% | 5.80% | 0 |
| cf_shift_profile_residual | 59.00% | 34.40% | 10.85% | 154 | 89 | 38.70% | 13.00% | 60.40% | 0 |

#### Required questions

1. Option log-probability vs generated MCQ: MedRGAG-evidence log-prob 44.20% vs generated MedRGAG 46.00%; direct log-prob 53.60% vs generated direct 46.00%.
2. Control→trap shift vs target margin: 44.40% vs 44.20%.
3. Pair accuracy / correct flip: CFShift 20.20% / 44.40%; target margin 16.00% / 44.20%.
4. BTR: CFShift 35.27%; target margin 52.28%.
5. DDXPlus profile value: profile 60.00%; no profile 44.40%; supported=True.
6. Real vs shuffled control: 60.00% vs 57.00%.
7. Real vs shuffled delta: 60.00% vs 44.40%.
8. Real vs shuffled profile: 60.00% vs 35.20%.
9–10. CF residual repairs=14, harms=6; profile residual repairs=154, harms=89.
11. Calibration-selected thresholds: CF=4.874999910593033; profile=-4.474590603476527.
12. Fresh residual direction reproduces calibration: CF=True; profile=True.
13. Counterfactual preference updating: directional criteria are met across all splits=True, but the pure CF fresh accuracy gain is 0.20% (95% CI -2.60% to 3.20%); this is preliminary rather than conclusive support.
14. Residual MedRGAG augmentation: frozen criteria are met=True. The conservative CF residual is supported=True; the profile residual is supported by net correction=True but has 38.70% conditional harm.
15. World-model claim: No.

#### Probability diagnostics

```json
{
  "fraction_gold_shift_gt_control_shift": 0.606,
  "mean_cf_shift_control_diagnosis": -1.8696249925840676,
  "mean_cf_shift_gold_trap": -0.3673750004065805,
  "mean_target_margin_control_diagnosis": -1.9214999992004742,
  "mean_target_margin_gold_trap": -1.5920000029385555,
  "target_nll": 2.126967686647427
}
```

#### Paired mechanism bootstrap

Paired by case ID with 1,000 bootstrap samples; differences are real minus control.

```json
{
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_control_accuracy": {
    "ci_high": 0.062,
    "ci_low": -0.006,
    "difference": 0.03,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_control_correct_flip": {
    "ci_high": 0.062,
    "ci_low": -0.006,
    "difference": 0.03,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_control_mean_gold_shift": {
    "ci_high": 1.2437890905230016,
    "ci_low": 0.7018736263234314,
    "difference": 0.9641371147117025,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_control_pair_accuracy": {
    "ci_high": 0.078,
    "ci_low": 0.03,
    "difference": 0.054,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_delta_accuracy": {
    "ci_high": 0.19,
    "ci_low": 0.122,
    "difference": 0.156,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_delta_correct_flip": {
    "ci_high": 0.19,
    "ci_low": 0.122,
    "difference": 0.156,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_delta_mean_gold_shift": {
    "ci_high": 1.4382123342313506,
    "ci_low": 1.0033849286630911,
    "difference": 1.2225757890387148,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_delta_pair_accuracy": {
    "ci_high": 0.096,
    "ci_low": 0.044,
    "difference": 0.07,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_profile_accuracy": {
    "ci_high": 0.288,
    "ci_low": 0.208,
    "difference": 0.248,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_profile_correct_flip": {
    "ci_high": 0.288,
    "ci_low": 0.208,
    "difference": 0.248,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_profile_mean_gold_shift": {
    "ci_high": 2.4102106212675922,
    "ci_low": 1.8187335351308305,
    "difference": 2.1137235968738985,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_profile_pair_accuracy": {
    "ci_high": 0.156,
    "ci_low": 0.096,
    "difference": 0.126,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.184,
    "ci_low": 0.096,
    "difference": 0.14,
    "samples": 1000
  },
  "cf_shift_profile_ranker_minus_medrgag_mcq_proxy_net_correction": {
    "ci_high": 0.184,
    "ci_low": 0.096,
    "difference": 0.14,
    "samples": 1000
  },
  "cf_shift_profile_residual_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.188,
    "ci_low": 0.066,
    "difference": 0.13,
    "samples": 1000
  },
  "cf_shift_profile_residual_minus_medrgag_mcq_proxy_net_correction": {
    "ci_high": 0.188,
    "ci_low": 0.066,
    "difference": 0.13,
    "samples": 1000
  },
  "cf_shift_ranker_minus_target_margin_ranker_accuracy": {
    "ci_high": 0.032,
    "ci_low": -0.026,
    "difference": 0.002,
    "samples": 1000
  },
  "cf_shift_ranker_minus_target_margin_ranker_correct_flip": {
    "ci_high": 0.032,
    "ci_low": -0.026,
    "difference": 0.002,
    "samples": 1000
  },
  "cf_shift_ranker_minus_target_margin_ranker_mean_gold_shift": {
    "ci_high": -0.1118750011751399,
    "ci_low": -0.603625005809372,
    "difference": -0.3673750004065805,
    "samples": 1000
  },
  "cf_shift_ranker_minus_target_margin_ranker_pair_accuracy": {
    "ci_high": 0.064,
    "ci_low": 0.024,
    "difference": 0.042,
    "samples": 1000
  },
  "cf_shift_residual_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.034,
    "ci_low": -0.002,
    "difference": 0.016,
    "samples": 1000
  },
  "cf_shift_residual_minus_medrgag_mcq_proxy_net_correction": {
    "ci_high": 0.034,
    "ci_low": -0.002,
    "difference": 0.016,
    "samples": 1000
  },
  "no_medrgag_evidence_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.228,
    "ci_low": 0.142,
    "difference": 0.184,
    "samples": 1000
  },
  "no_medrgag_evidence_minus_medrgag_mcq_proxy_net_correction": {
    "ci_high": 0.228,
    "ci_low": 0.142,
    "difference": 0.184,
    "samples": 1000
  }
}
```

#### Calibration operating point

CF residual threshold 4.874999910593033: repairs=9, harms=6, net=1.50%, coverage=8.50%.
Profile residual threshold -4.474590603476527: repairs=62, harms=31, net=15.50%, coverage=59.00%.

#### Existing 49-way candidate audit

This is a zero-cost secondary diagnostic; it does not enter the four-way main comparison.

```json
{
  "dev": {
    "baseline_wrong": 153,
    "individual": {
      "full_pair_ranker": {
        "recall_at_10": 0.46,
        "recall_at_5": 0.36666666666666664,
        "unique_gold_coverage": 7
      },
      "medrgag_evidence_ranker": {
        "recall_at_10": 0.5266666666666666,
        "recall_at_5": 0.44,
        "unique_gold_coverage": 30
      },
      "pair_aware_ranker": {
        "recall_at_10": 0.5466666666666666,
        "recall_at_5": 0.43,
        "unique_gold_coverage": 17
      },
      "target_only_ranker": {
        "recall_at_10": 0.49666666666666665,
        "recall_at_5": 0.38,
        "unique_gold_coverage": 4
      }
    },
    "note": "Union ordering is deterministic rank-wise interleaving; RRF uses k=60.",
    "oracle_union_repairs_at_10": 88,
    "oracle_union_repairs_at_20": 111,
    "rrf_recall_at_10": 0.53,
    "rrf_recall_at_20": 0.7333333333333333,
    "union_recall_at_10": 0.6166666666666667,
    "union_recall_at_20": 0.7333333333333333
  },
  "test": {
    "baseline_wrong": 164,
    "individual": {
      "full_pair_ranker": {
        "recall_at_10": 0.48333333333333334,
        "recall_at_5": 0.37666666666666665,
        "unique_gold_coverage": 5
      },
      "medrgag_evidence_ranker": {
        "recall_at_10": 0.5333333333333333,
        "recall_at_5": 0.4633333333333333,
        "unique_gold_coverage": 23
      },
      "pair_aware_ranker": {
        "recall_at_10": 0.5366666666666666,
        "recall_at_5": 0.43333333333333335,
        "unique_gold_coverage": 6
      },
      "target_only_ranker": {
        "recall_at_10": 0.5533333333333333,
        "recall_at_5": 0.45666666666666667,
        "unique_gold_coverage": 3
      }
    },
    "note": "Union ordering is deterministic rank-wise interleaving; RRF uses k=60.",
    "oracle_union_repairs_at_10": 90,
    "oracle_union_repairs_at_20": 112,
    "rrf_recall_at_10": 0.5733333333333334,
    "rrf_recall_at_20": 0.71,
    "union_recall_at_10": 0.59,
    "union_recall_at_20": 0.7133333333333334
  }
}
```

#### Remaining bottleneck

MedRGAG selected-evidence context interference and score separation.

The no-MedRGAG-evidence scorer reaches 64.40% versus 60.00% with selected evidence on fresh test. Real control improves profile accuracy over shuffled control by 3.00%, but its 95% CI (-0.60% to 6.20%) includes zero; pair accuracy and mean gold shift show clearer positive differences.

#### Limitations

- Local all-Llama MedRGAG is a proxy, not the paper's mixed-model configuration.
- Option log probabilities are model scores under two fixed label permutations, not clinical probabilities.
- DDXPlus evidence matching uses deterministic MedCPT best-match logits; it is not manually adjudicated.
- 162 control/trap items have an empty unchanged KADS selection.
- 28 pairs have no observable structured finding change after formatting normalization.
- Gold control anchoring is diagnostic only and excluded from the main interpretation.
- No result supports a world-model claim.

<a id="record-0276"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfmoe/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfmoe/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_cfmoe`。

### CF-KADS-MoE results

This is counterfactual evidence selection and expert fusion, not a world model.

#### MedEinst fresh 1,000-pair confirmatory result

Pair-aware methods use control/trap/delta; `medrgag_mcq_proxy`, the `medrgag` option-score expert, and `direct_logprob` are separate trap-only single-case baselines.

| Method | Accuracy | Pair/robust accuracy | BTR | Repairs | Harms | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| medrgag_mcq_proxy | 45.4% | 17.2% | 59.1% | 0 | 0 | 0 |
| medrgag | 47.5% | 20.7% | 53.4% | 94 | 73 | 0 |
| direct_logprob | 49.4% | 18.2% | 61.9% | 140 | 100 | 0 |
| no_medrgag_evidence | 57.1% | 26.6% | 44.9% | 204 | 87 | 0 |
| profile_no_document | 77.7% | 41.5% | 12.4% | 368 | 45 | 0 |
| profile_original_kads | 58.4% | 31.9% | 25.0% | 200 | 70 | 0 |
| profile_cf_kads | 68.5% | 19.3% | 37.1% | 333 | 102 | 0 |
| profile_cf_kads_contrastive | 68.9% | 19.5% | 37.3% | 336 | 101 | 0 |
| cpg_core | 54.9% | 34.3% | 22.9% | 289 | 194 | 27 |
| ecr_lite | 58.0% | 34.3% | 23.6% | 302 | 176 | 0 |
| profile_plus_cpg | 70.7% | 40.7% | 15.9% | 362 | 109 | 0 |
| medrgag_plus_cpg | 53.0% | 28.1% | 38.2% | 187 | 111 | 0 |
| profile_plus_ecr | 70.0% | 36.7% | 17.7% | 338 | 92 | 0 |
| uniform_fusion | 69.9% | 37.1% | 26.9% | 288 | 43 | 0 |
| learned_fusion | 78.5% | 44.6% | 7.5% | 394 | 63 | 0 |
| shuffled_delta | 48.9% | 27.1% | 33.9% | 143 | 108 | 0 |
| shuffled_profile | 41.0% | 23.2% | 38.4% | 109 | 153 | 0 |
| shuffled_cpg_edit | 39.9% | 17.7% | 56.8% | 127 | 182 | 27 |
| oracle_expert_selector | 96.3% | 65.0% | 1.9% | 514 | 5 | 0 |

#### Required answers

1. Previous signal replication: profile_original_kads=58.4% vs MedRGAG=45.4% (+13.0pp, close to the old +14pp); historical `no_medrgag_evidence`=57.1% (+11.7pp, positive but smaller than the old +18.4pp). The separately defined true profile_no_document is 77.7% (+32.3pp).
2. Strongest expert: profile_no_document.
3. Expert complementarity: oracle=96.3%, gap over strongest=18.6%.
4. Learned fusion vs calibration-selected strongest `profile_no_document`: 78.5% vs 77.7%; +0.8pp with 95% CI [-1.6,+3.3]pp, so the gain is not significant.
5. Selected-evidence interference: original KADS=58.4%, no document=77.7%; evidence-only repairs=68, harms=261. Mean delta coverage on harms=0.8456536440625326, generated ratio=0.6725415070242655, document count=4.839080459770115, score-std ratio=1.4140023055458693. Retrieved-only=70.8%, generated-only=64.8%. Document factual error is not identifiable without document-level factuality labels.
6. CF-KADS repair: top1=64.1%, top3=68.5%, top5=67.7%, contrastive=68.9%.
7. CPG core: 54.9% vs direct 49.4%.
8. ECR-lite: 58.0% vs profile-only 77.7%.
9. Real/shuffle: real profile KADS 58.4%, shuffled delta 48.9%, shuffled profile 41.0%; CPG 54.9%, shuffled edit 39.9%.
10. MedPIC: no second-dataset positive result. Best non-baseline CF method `standard_rag`=6.6%; MedRGAG=20.8%; row-level CF difference=-14.2pp, 95% CI [-20.2,-8.2]pp. Official linked-pair retrieval stagnation is not estimable because the release has no pair map.
11. ReMedQA/static control: final static fusion accuracy=68.5%, ReAcc=52.0%, ReCon=61.0%; accuracy is below the reader adapter (71.0%), so static accuracy was not preserved by fusion.
12. Supported story: strong MedEinst evidence for counterfactual evidence control and option-score expert fusion, but no cross-dataset improvement claim because MedPIC is negative.
13. World-model claim: No. The method is counterfactual evidence selection and expert fusion, not a world model.

#### Paired bootstrap

```json
{
  "cpg_core_minus_direct_logprob_accuracy": {
    "ci_high": 0.095,
    "ci_low": 0.014,
    "difference": 0.055,
    "samples": 1000
  },
  "cpg_core_minus_shuffled_cpg_edit_accuracy": {
    "ci_high": 0.188,
    "ci_low": 0.109,
    "difference": 0.15,
    "samples": 1000
  },
  "ecr_lite_minus_profile_no_document_accuracy": {
    "ci_high": -0.165,
    "ci_low": -0.23,
    "difference": -0.197,
    "samples": 1000
  },
  "learned_fusion_minus_profile_no_document_accuracy": {
    "ci_high": 0.033,
    "ci_low": -0.016,
    "difference": 0.008,
    "samples": 1000
  },
  "no_medrgag_evidence_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.15,
    "ci_low": 0.085,
    "difference": 0.117,
    "samples": 1000
  },
  "profile_cf_kads_minus_profile_original_kads_accuracy": {
    "ci_high": 0.14,
    "ci_low": 0.063,
    "difference": 0.101,
    "samples": 1000
  },
  "profile_no_document_minus_medrgag_mcq_proxy_accuracy": {
    "ci_high": 0.362,
    "ci_low": 0.288,
    "difference": 0.323,
    "samples": 1000
  },
  "profile_original_kads_minus_shuffled_delta_accuracy": {
    "ci_high": 0.119,
    "ci_low": 0.071,
    "difference": 0.095,
    "samples": 1000
  },
  "profile_original_kads_minus_shuffled_profile_accuracy": {
    "ci_high": 0.201,
    "ci_low": 0.144,
    "difference": 0.174,
    "samples": 1000
  }
}
```

#### Limitations

- The local all-Llama MedRGAG path is a proxy for the paper configuration.
- Four-option pair-aware accuracy is not official open-diagnosis SOTA.
- The 27 CPG invalid rows are structural not-applicable cases with no valid edit, not runtime failures; they are neutral only inside fusion.
- Selected-evidence coverage/count correlations with harm are near zero; generated-only is worse than retrieved-only and CF-KADS partly repairs KADS, but document factual error is unidentifiable and no-document remains best.
- The official CPG specialist/judge code (commit 265d1ae) ran a non-blocking 5-case dev pilot: Round 0 plus at most one peer-discussion round (0 cases reached that round; accuracy=40.0%, invalid=0). It was excluded from fusion and confirmatory claims.

#### MedPIC second-dataset result

No official pair map exists, so only row-level official metrics are reported.

| Method | Exact-set | GF | CF | Option F1 | Activation | Deactivation | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|
| medrgag_proxy | 34.7% | 43.7% | 20.8% | 53.0% | 40.8% | 0.0% | 2 |
| direct_logprob | 5.8% | 7.0% | 3.8% | 21.3% | 9.9% | 0.0% | 0 |
| standard_rag | 10.1% | 12.3% | 6.6% | 26.4% | 12.7% | 1.5% | 0 |
| parameter_scaffold | 4.7% | 6.0% | 2.7% | 12.1% | 7.0% | 0.0% | 0 |
| coverage_audit | 9.6% | 13.0% | 4.4% | 23.8% | 8.5% | 0.0% | 0 |
| contrastive_retrieval | 10.1% | 12.3% | 6.6% | 24.9% | 12.7% | 1.5% | 0 |
| ea_rag_style_full | 7.7% | 8.8% | 6.0% | 24.6% | 12.7% | 1.5% | 0 |
| cf_kads | 7.5% | 8.1% | 6.6% | 26.7% | 14.1% | 0.0% | 0 |
| soft_fusion | 6.4% | 8.1% | 3.8% | 42.6% | 4.2% | 0.0% | 2 |

Contrastive retrieval added documents on 221/467 rows; linked GF/CF separation was not estimated without an official pair map.


#### ReMedQA static control

Profile, CPG and ECR are disabled because these inputs have no patient-state delta.

| Method | Accuracy | ReAcc | ReCon | Invalid |
|---|---:|---:|---:|---:|
| medrgag_standard_reader_adapter | 71.0% | 53.0% | 60.0% | 0 |
| option_logprob_averaging | 61.8% | 44.0% | 61.0% | 0 |
| medrgag_evidence_logprob | 71.8% | 51.0% | 56.0% | 0 |
| final_static_fusion | 68.5% | 52.0% | 61.0% | 0 |

`medrgag_standard_reader_adapter` appends canonical options after the raw official-format prompt, so it is not an exact-format official reader reproduction.

<a id="record-0277"></a>

## summary.md

来源：[Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_riskroute/summary.md](/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_riskroute/summary.md)，原文第1行起。命令以原文指定工作目录为准；相对文件引用原属 `/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_riskroute`。

### RiskRoute-CF results

RiskRoute-CF is uncertainty-calibrated, safety-aware expert routing for paired counterfactual Medical RAG. It is not a clinical safety guarantee or a world model.

#### Confirmatory new 1,000-pair test

| Method | Accuracy | Repairs | Harms | CHR | OCP | Net correction | Profile coverage | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| medrgag | 41.8% | 0 | 0 | 0.0% | 100.0% | 0.0% | 0.0% | 0 |
| profile_no_document | 74.3% | 361 | 36 | 8.6% | 91.4% | 32.5% | 100.0% | 0 |
| learned_fusion_existing | 81.0% | 443 | 51 | 12.2% | 87.8% | 39.2% | n/a | 0 |
| confidence_heuristic | 71.0% | 318 | 26 | 6.2% | 93.8% | 29.2% | 89.8% | 0 |
| margin_heuristic | 67.6% | 277 | 19 | 4.5% | 95.5% | 25.8% | 79.7% | 0 |
| uncalibrated_router | 74.3% | 361 | 36 | 8.6% | 91.4% | 32.5% | 74.1% | 0 |
| calibrated_forced_router | 74.3% | 361 | 36 | 8.6% | 91.4% | 32.5% | 78.8% | 0 |
| risk_aware_router | 73.3% | 343 | 28 | 6.7% | 93.3% | 31.5% | 74.8% | 0 |
| three_path_router | 76.2% | 386 | 42 | 10.0% | 90.0% | 34.4% | 86.4% | 0 |

#### Appendix: method-specific control prediction

This nonprimary view follows each selected trap-side branch: the reader baseline control for MedRGAG, saved control scores for Profile/CF-KADS, and existing control fusion for learned fusion. The main table above keeps the unchanged MedRGAG reader control for every method.

| Method | Control accuracy | Both-correct pair accuracy | Bias Trap Rate |
|---|---:|---:|---:|
| medrgag | 56.4% | 16.7% | 62.8% |
| profile_no_document | 57.5% | 39.3% | 16.2% |
| learned_fusion_existing | 56.3% | 44.9% | 8.5% |
| confidence_heuristic | 57.1% | 36.2% | 24.9% |
| margin_heuristic | 56.4% | 32.7% | 33.5% |
| uncalibrated_router | 57.3% | 39.1% | 16.1% |
| calibrated_forced_router | 57.2% | 39.0% | 16.1% |
| risk_aware_router | 57.2% | 38.5% | 18.5% |
| three_path_router | 55.3% | 38.9% | 15.0% |

#### Phase-0 exploratory analysis

The previously observed fresh-1,000 was evaluated only after freezing the model and never selected features, lambda, or thresholds. Its two-expert oracle/profile/risk-aware accuracies are 82.2%/77.7%/76.9%; risk-aware repairs/harms are 349/34. Frozen q_profile Platt ECE is 0.059 -> 0.051. Strongest orientation-free single-feature repair/harm AUROCs: `profile_margin`=0.788, `profile_max_probability`=0.724, `profile_kads_margin_delta`=0.721. Development-trained coefficients are saved alongside these diagnostics.

#### Required answers

1. Two-expert oracle upper bound: 77.9%.
2. Strongest repair/harm indicators by the frozen standardized harm model: `medrgag_profile_agree` (-3.077), `profile_margin` (-2.839), `profile_max_probability` (+1.905).
3. Calibration: temperature scaling improved ECE/Brier/NLL for 5/5 experts; Platt improved ECE for 2/3, Brier for 3/3, and NLL for 3/3 main estimators. These are calibration-split fit/selection results. On confirmatory test, temperature improved all three metrics for 5/5 experts; among the three main estimators, Platt improved ECE for 3/3, Brier for 3/3, and NLL for 2/3. Confirmatory values: q_medrgag ECE/Brier/NLL 0.066/0.114/0.380 -> 0.066/0.114/0.383; q_profile ECE/Brier/NLL 0.037/0.148/0.451 -> 0.035/0.148/0.450; h_profile ECE/Brier/NLL 0.236/0.168/0.505 -> 0.014/0.032/0.115. The secondary q_cf_kads Platt calibration worsens ECE/Brier/NLL 0.070/0.197/0.578 -> 0.092/0.202/0.588. Full values are in `calibration_metrics.json`.
4. Calibrated forced router accuracy 74.3%; confidence 71.0%, margin 67.6%. However, forced-router predictions match Profile on 1000/1000 rows despite selecting MedRGAG 212 times, so it realizes no capability selection gain.
5. Risk-aware CHR 6.7% vs profile 8.6%.
6. Accuracy cost relative to profile: -1.0pp.
7. Accuracy/harm Pareto improvement: No.
8. CPG incremental value (accuracy/CHR): full 73.3%/6.7% vs without CPG 74.3%/8.6%.
9. Interference-feature incremental value (accuracy/CHR): full 73.3%/6.7% vs without interference 72.7%/7.4%.
10. Three-path 76.2% vs two-expert risk-aware 73.3%.
11. Frozen selective operating points: target 80% -> test coverage 62.7%, accuracy 88.8%, risk 11.2%; target 90% -> test coverage 81.1%, accuracy 80.9%, risk 19.1%; target 95% -> test coverage 89.3%, accuracy 77.3%, risk 22.7%; AURC=0.0988.
12. New-test reproduces the strict calibration direction: False (within-1pp accuracy direction: True). Calibration/test risk-minus-profile accuracy=+0.0/-1.0pp; CHR difference=-2.3/-1.9pp.
13. Static ReMedQA: prediction equality=True; accuracy/ReAcc/ReCon=71.0%/53.0%/60.0%.
14. Safety-aware counterfactual routing claim: Not supported by the prespecified benchmark success criteria. Strong=False, medium-A=False, medium-B=False, selective-significant=False (descriptive improvement=True; no selective risk-difference CI).
15. No clinical safety guarantee.
16. No world-model claim.

#### Routing mechanism diagnosis

MedRGAG and Profile originally agree on 516/1000 rows. Risk-aware routing matches Profile on 961/1000 rows and makes 39 effective overrides: it prevents 8 Profile harms but loses 18 Profile repairs (net -10). This mechanism-level result is not a successful capability router.

#### Paired bootstrap

Risk-aware minus profile accuracy: -1.0pp (95% CI -2.0 to +0.0pp); CHR difference -1.9pp (95% CI -3.3 to -0.7pp).

#### Execution note

An initial isolated two-shard option-scoring run produced 120 debug rows and was intentionally stopped after document scoring completed. Those rows were excluded; formal option scores were exact-ID merged only from the clean three-shard `option3` directory.

#### Limitations

- This is a four-option pair-aware MedEinst proxy, not official open-diagnosis SOTA or clinical deployment evidence.
- The local all-Llama MedRGAG path is a proxy for the paper configuration.
- The harm estimator has only 5 positive calibration rows (36 on confirmatory test), so its calibration and risk penalty are data-limited.
- Selective DEFER is evaluated as abstention and is never replaced by MedRGAG.
