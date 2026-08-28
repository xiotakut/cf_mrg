# CF-KADS-MoE results

This is counterfactual evidence selection and expert fusion, not a world model.

## MedEinst fresh 1,000-pair confirmatory result

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

## Required answers

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

## Paired bootstrap

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

## Limitations

- The local all-Llama MedRGAG path is a proxy for the paper configuration.
- Four-option pair-aware accuracy is not official open-diagnosis SOTA.
- The 27 CPG invalid rows are structural not-applicable cases with no valid edit, not runtime failures; they are neutral only inside fusion.
- Selected-evidence coverage/count correlations with harm are near zero; generated-only is worse than retrieved-only and CF-KADS partly repairs KADS, but document factual error is unidentifiable and no-document remains best.
- The official CPG specialist/judge code (commit 265d1ae) ran a non-blocking 5-case dev pilot: Round 0 plus at most one peer-discussion round (0 cases reached that round; accuracy=40.0%, invalid=0). It was excluded from fusion and confirmatory claims.

## MedPIC second-dataset result

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


## ReMedQA static control

Profile, CPG and ECR are disabled because these inputs have no patient-state delta.

| Method | Accuracy | ReAcc | ReCon | Invalid |
|---|---:|---:|---:|---:|
| medrgag_standard_reader_adapter | 71.0% | 53.0% | 60.0% | 0 |
| option_logprob_averaging | 61.8% | 44.0% | 61.0% | 0 |
| medrgag_evidence_logprob | 71.8% | 51.0% | 56.0% | 0 |
| final_static_fusion | 68.5% | 52.0% | 61.0% | 0 |

`medrgag_standard_reader_adapter` appends canonical options after the raw official-format prompt, so it is not an exact-format official reader reproduction.
