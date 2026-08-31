# RiskRoute-CF results

RiskRoute-CF is uncertainty-calibrated, safety-aware expert routing for paired counterfactual Medical RAG. It is not a clinical safety guarantee or a world model.

## Confirmatory new 1,000-pair test

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

## Appendix: method-specific control prediction

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

## Phase-0 exploratory analysis

The previously observed fresh-1,000 was evaluated only after freezing the model and never selected features, lambda, or thresholds. Its two-expert oracle/profile/risk-aware accuracies are 82.2%/77.7%/76.9%; risk-aware repairs/harms are 349/34. Frozen q_profile Platt ECE is 0.059 -> 0.051. Strongest orientation-free single-feature repair/harm AUROCs: `profile_margin`=0.788, `profile_max_probability`=0.724, `profile_kads_margin_delta`=0.721. Development-trained coefficients are saved alongside these diagnostics.

## Required answers

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

## Routing mechanism diagnosis

MedRGAG and Profile originally agree on 516/1000 rows. Risk-aware routing matches Profile on 961/1000 rows and makes 39 effective overrides: it prevents 8 Profile harms but loses 18 Profile repairs (net -10). This mechanism-level result is not a successful capability router.

## Paired bootstrap

Risk-aware minus profile accuracy: -1.0pp (95% CI -2.0 to +0.0pp); CHR difference -1.9pp (95% CI -3.3 to -0.7pp).

## Execution note

An initial isolated two-shard option-scoring run produced 120 debug rows and was intentionally stopped after document scoring completed. Those rows were excluded; formal option scores were exact-ID merged only from the clean three-shard `option3` directory.

## Limitations

- This is a four-option pair-aware MedEinst proxy, not official open-diagnosis SOTA or clinical deployment evidence.
- The local all-Llama MedRGAG path is a proxy for the paper configuration.
- The harm estimator has only 5 positive calibration rows (36 on confirmatory test), so its calibration and risk penalty are data-limited.
- Selective DEFER is evaluated as abstention and is never replaced by MedRGAG.
