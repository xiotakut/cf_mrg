# CF-Residual Adapter on MA-RAG

## Conclusion

The frozen CF-Residual Adapter transfers to both evaluated medical-RAG architectures in the four-option, pair-aware MedEinst protocol. On the untouched 500-pair test, it raises the MA-RAG intrinsic baseline from 39.2% to 80.0% (+40.8 points, paired-bootstrap 95% CI +36.6 to +45.4) and the MedRGAG-style baseline from 40.8% to 82.4% (+41.6 points, 95% CI +37.0 to +46.2).

This supports a cross-framework counterfactual-transfer claim. It does **not** support MA-RAG synergy: the MA-RAG adapter is only 0.6 points above Profile-only (95% CI -2.4 to +3.8), while removing all MA-RAG scores increases accuracy from 80.0% to 81.8%. The positive result is therefore driven by the portable counterfactual sidecar, not by a beneficial interaction with MA-RAG's score distribution.

The `without MA-RAG` ablation removes every MA-RAG score and feature but retains the same MA-RAG runtime-eligible cohort for a paired comparison; the one runtime-failed question remains invalid rather than receiving a sidecar-only prediction.

The experiment is a four-option MCQ proxy with access to the control and counterfactual cases. It is not an official open-diagnosis MedEinst result, a reproduction of MA-RAG's seven-benchmark table, clinical deployment evidence, a safety guarantee, or a world model.

## Protocol and frozen configuration

- Development: 400 official train/reference pairs.
- Calibration: 150 disjoint official train/reference pairs.
- Fresh test: 500 official test pairs selected with seed 223 after excluding every source ID used by DeltaRank, CFShift, CF-KADS-MoE, RiskRoute-CF, development, or calibration. The overlap count is zero.
- Every method uses the same four diagnoses and option-to-label mapping per pair.
- MA-RAG: official intrinsic implementation at upstream commit `423f031cc0ffca679a047c885be999b9604100a9`, Qwen3-8B, `N=8`, `T=4`, BM25 plus MedCPT-Cross-Encoder over MedCorp3 (PubMed, Textbooks, and Wikipedia). The unavailable/corrupt StatPearls component was not substituted.
- Counterfactual sidecar: Llama-3.1-8B-Instruct, unchanged Profile-no-document and CPG definitions, and exact option-sequence likelihood.
- Fusion: per-question normalized base/Profile/CPG scores and the small frozen linear models in `fusion_config.json`. Development fit the entropy temperature (`0.05000032401354733`) and linear weights; calibration selected zero L2 penalty; the fresh test was evaluated once without refitting.
- Invalid outputs remain invalid. No baseline fallback, preserve default, hard safety gate, or gold-dependent tie resolution is used.

The official extrinsic MA-RAG evaluator was not run because no official evaluator checkpoint was locally available. No substitute evaluator was trained.

## Fresh-test results

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

### Invalid-output accounting

The MA-RAG trap baseline has eight invalid predictions: seven exact 4-4 vote ties and one runtime-invalid case (`case_53912`). The runtime case entered the upstream unbounded formatting retry because a thinking response lacked `</think>`; its partial directory was preserved and the case was explicitly marked invalid. The portable adapter can use the complete, finite option distributions from exact vote ties, but it cannot use the runtime-invalid case, so it has one invalid prediction.

Five of the 210 corrections counted by the metric come from correctly resolving complete base vote ties. They are not official prediction flips, because the official majority result is invalid on a tie. Excluding all seven tied rows leaves a similarly large gain (395/492 adapter-correct versus 196/492 MA-RAG-correct), so the conclusion is not driven by invalid handling. Control MA-RAG has five exact ties; the pair-prompt baseline has three.

## Statistical comparisons and controls

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

## MA-RAG false consensus

On the fresh test, 459/500 questions (91.8%; 93.29% among the 492 valid official predictions) end with a unanimous MA-RAG candidate pool. Of all 500 questions, 273 (54.6%; 55.49% among valid) are wrong-unanimous stops and 186 (37.2%) are correct-unanimous stops. Profile disagrees with 59.69% of unanimous pools and CPG disagrees with 56.53% of the 444 unanimous cases where CPG is available. The first-round candidate-conflict rate is 50.41% among valid cases; among the 244 first-round no-conflict cases, Profile supplies a conflicting state signal 58.20% of the time.

The post-hoc learned adapter corrects 190/273 false-consensus cases (69.60%). This supports the existence of MA-RAG's error-consensus blind spot, but it does not by itself validate the native trigger.

## Native MA-RAG experiments: development/calibration only

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

## Cost and static compatibility

The portable adapter is post-hoc: it does not add MA-RAG rounds, retrieval queries, or documents. Its CPU normalization and linear fusion cost is negligible. For the 499 MA-RAG trap cases with complete cost logs, the base averages are 1.910 rounds, 15.279 candidate generations, 3.639 retrieval queries, 6.968 documents, 6,539 generated tokens, and 54.29 seconds of per-question wall time.

The shared Llama sidecar ran from 13:12:27 to 17:51:19, or about 4 h 38 m 52 s for 500 pairs (about 33.5 seconds per pair in pipeline throughput). Its recorded generation-stage completion-token total across M0 plus M2 summary/explore/generate/select is 3,312,304, or 6,624.6 tokens per pair. Exact sequence-likelihood passes are additional and do not expose a compatible token counter. The sidecar is computed once and shared by both base frameworks.

Static applicability is deterministic. The prior RiskRoute-CF static control explicitly verifies that, on 400 ReMedQA rows, the MedRGAG static path and adapter-bypass path are identical prediction by prediction: 71.0% accuracy, 53.0% ReAcc, and 60.0% ReCon. On the existing 100-item MA-RAG MedQA check, the adapter bypass is a pass-through of the stored unmodified baseline by construction: 100/100 predictions are identical, with 72.0% accuracy and four explicit vote ties. This is not a second stochastic rerun and is applicability isolation, not a learned safety guarantee.

## Answers to the required report questions

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

## Files and limitations

The public result files contain the frozen splits, dataset map, parsed rounds, continuous option scores, sidecar scores, frozen fusion configuration, predictions, metrics, bootstrap intervals, false-consensus rows, efficiency rows, static compatibility check, and exact command record. Expensive intermediate retrieval and generation caches remain under the ignored `results_marag_cf/cache/` directory.

The principal limitations are the pair-aware MCQ proxy, construction-source alignment between MedEinst and DDXPlus profiles, different Qwen/Llama base models across the two branches, one 500-pair confirmatory seed, and the absence of fresh native/seed-robustness runs. The result establishes portability of the CF sidecar across base-framework interfaces, not synergy, official benchmark SOTA, clinical safety, or deployment readiness.
