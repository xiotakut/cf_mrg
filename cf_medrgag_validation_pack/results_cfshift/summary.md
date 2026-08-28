# CFShift-MedRGAG results

CFShift is counterfactual preference-shift reranking, not a world model.

Data: 800 official train/reference development pairs, 200 separate calibration pairs, and 500 fresh official test pairs. The fresh set excludes all 300 inspected DeltaRank test cases.

## Main fresh-test table

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

## Required questions

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

## Probability diagnostics

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

## Paired mechanism bootstrap

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

## Calibration operating point

CF residual threshold 4.874999910593033: repairs=9, harms=6, net=1.50%, coverage=8.50%.
Profile residual threshold -4.474590603476527: repairs=62, harms=31, net=15.50%, coverage=59.00%.

## Existing 49-way candidate audit

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

## Remaining bottleneck

MedRGAG selected-evidence context interference and score separation.

The no-MedRGAG-evidence scorer reaches 64.40% versus 60.00% with selected evidence on fresh test. Real control improves profile accuracy over shuffled control by 3.00%, but its 95% CI (-0.60% to 6.20%) includes zero; pair accuracy and mean gold shift show clearer positive differences.

## Limitations

- Local all-Llama MedRGAG is a proxy, not the paper's mixed-model configuration.
- Option log probabilities are model scores under two fixed label permutations, not clinical probabilities.
- DDXPlus evidence matching uses deterministic MedCPT best-match logits; it is not manually adjudicated.
- 162 control/trap items have an empty unchanged KADS selection.
- 28 pairs have no observable structured finding change after formatting normalization.
- Gold control anchoring is diagnostic only and excluded from the main interpretation.
- No result supports a world-model claim.
