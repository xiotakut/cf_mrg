# DeltaRank-MedRGAG pilot

## Outcome

The pilot does not meet the predefined criteria for positive counterfactual ranking signal.
The residual augmentation hypothesis is not supported; a no-op is not counted as success.
No result supports a world-model claim.

## Data and output space

Development used 300 official train/reference pairs; test used 300 official test pairs. The fixed DDXPlus ontology has 49 labels; 44 occur in the sampled data.
Structured deltas were nonempty for 293 development and 297 test pairs.

## Main test table

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

## Required comparisons

1. MCQ adaptation: legacy open accuracy 10.33%; four-way MedRGAG MCQ 45.33% (difference 35.00%).
2. Two-way counterfactual accuracy: direct 61.00%; MedRGAG MCQ 59.00%.
3. Structured delta: pair-aware R@5/R@10 43.33%/53.67%; target-only 45.67%/55.33%.
4. DDXPlus profiles: delta-profile R@5 49.00% versus pair-aware 43.33%.
5–6. Always-apply produced 25 repairs and 78 harms.
7. Best development-selected residual threshold was 4; on test it produced 5 repairs, 2 harms, net 1.00%, and coverage 3.67%.
8. Shuffled-delta R@5 42.00% versus real 49.00%.
9. Shuffled-profile R@5 40.33% versus real 49.00%.
10. The main observed bottleneck is candidate generation.

## Operating points

Best-accuracy development point: {"accuracy": 0.4866666666666667, "answer_change_coverage": 0.02666666666666667, "baseline_accuracy": 0.49, "baseline_correct": 147, "baseline_wrong": 153, "beneficial_revision_precision": 0.375, "conditional_harm_rate": 0.027210884353741496, "final_correct": 146, "harms": 4, "introduced_error_rate": 0.013333333333333334, "invalid_count": 8, "n": 300, "net_correction": -0.0033333333333333335, "original_correct_preservation": 0.9727891156462585, "repair_rate": 0.0196078431372549, "repairs": 3, "split": "dev", "threshold": 4}
Conservative point: no useful selective operating point had positive development net correction.
The full observed development margin curve is in `tradeoff.csv`; no fixed 1%/2% gate was imposed.

## Oracle and validity diagnostics

For the delta-profile candidate set, oracle top-5/top-10 repair capacity was 39.63%/49.39%.
Invalid outputs: {"mcq": 899, "ranking": 0, "scoring": 27}. Invalid final outputs count as wrong, not as PRESERVE.

## Limitations

This is a local all-Llama MedRGAG proxy, not the published mixed-model configuration. Hard negatives use deterministic DDXPlus profile overlap. The official train and test files observed here cover 46 of the 49 ontology labels. The 49-way scorer reranks a top-10 candidate set, so its ceiling depends on candidate recall. NICE, medication-oriented rules, the prior atomic-rule pipeline, and the prior hard conjunctive gate are not part of this active experiment.
