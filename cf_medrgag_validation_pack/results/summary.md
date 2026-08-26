# DeltaRev-MedRGAG pilot

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

## Main test metrics

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

## Ablation diagnostics

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

## Paired bootstrap comparisons

- `full_deltarev_vs_always_preserve`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_medrgag_proxy`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_evidence_verifier_with_standard_retrieval`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_evidence_verifier_with_ea_rag_retrieval`: accuracy difference=+0.0000, paired-bootstrap 95% CI=[+0.0000, +0.0000]
- `full_deltarev_vs_direct_answer_revision`: accuracy difference=+0.0625, paired-bootstrap 95% CI=[+0.0125, +0.1187]

## Gold-label oracle gate diagnostic (outside the main table)

The oracle gate could repair 2 baseline errors among already proposed full-method alternatives, with harms fixed to zero by construction because it uses test labels to revise only when correctness improves. This is analysis only and was not used for inference, threshold selection, or the main method table.

## Limitations and expansion decision

This is a single MedEinst pilot using a local all-Llama MedRGAG proxy. MedPIC official linked pairs, official delta metadata, decisive source references, retrieval Recall/MRR, the source-rule upper bound, and NICE are unavailable. The three-way delta-quality comparison is invalid because there is no official delta reference and LLM-only extraction produced 0/200 usable outputs. Delta nonempty coverage, document coverage, EA audit coverage, and rule contract rates are operational artifact diagnostics—not official delta accuracy, evidence recall, or MRR. Accuracy is strict normalized exact match: clinically related or potentially equivalent-in-context labels such as `Bronchitis` and `Chronic Bronchitis` count as different, and no post-hoc rescoring was performed. EA-RAG-style is a proxy reproduction. Thresholds were selected on development, while test was used only for final reporting. MedCounterFact and MediEval were not run under the frozen pilot; the conservative stop decision is to diagnose the reported bottleneck before extension. CLIR remains a separate optional transition experiment.
