# cf_mrg

The active experiment is **RiskRoute-CF: Uncertainty-Calibrated Counterfactual Expert Routing for Safety-Aware Medical RAG**, implemented in [`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/).

RiskRoute-CF is a pair-aware controller for counterfactual MedEinst cases. It chooses between the original MedRGAG reader prediction and the strongest existing no-document delta-profile expert. CPG agreement and CF-KADS evidence-interference measurements are reliability features, not additional mandatory gates. The primary mode is forced choice: every valid paired case receives one expert prediction, and invalid rows are counted rather than replaced with MedRGAG. Static inputs without a control–counterfactual pair bypass the controller exactly.

## Confirmatory result

Development used 800 official train/reference pairs, calibration used a disjoint 200, and the frozen controller was evaluated once on 1,000 newly selected official test pairs after excluding all source IDs used by DeltaRank, CFShift, and CF-KADS-MoE. All 1,000 test rows were valid.

| Method | Accuracy | Repairs | Harms | Conditional harm | OCP | Net correction | Profile coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| MedRGAG reader | 41.8% | 0 | 0 | 0.0% | 100.0% | 0.0% | 0.0% |
| Profile, no document | 74.3% | 361 | 36 | 8.61% | 91.39% | 32.5% | 100.0% |
| Calibrated forced router | 74.3% | 361 | 36 | 8.61% | 91.39% | 32.5% | 78.8% |
| Risk-aware router | 73.3% | 343 | 28 | 6.70% | 93.30% | 31.5% | 74.8% |
| Existing learned fusion | 81.0% | 443 | 51 | 12.20% | 87.80% | 39.2% | n/a |

Risk-aware routing reduces conditional harm relative to Profile by 1.91 points (95% paired-bootstrap CI -3.34 to -0.73) while losing 1.0 point of accuracy (95% CI -2.0 to 0.0). It therefore does **not** form a Pareto improvement and does not meet the prespecified strong or medium success criteria. The result supports reporting a calibrated accuracy–risk trade-off, but not a positive benchmark claim of improved safety-aware routing.

Mechanistically, MedRGAG and Profile already agree on 516/1,000 predictions. The calibrated forced router selects MedRGAG 212 times but still matches Profile on all 1,000 final predictions, so it realizes no capability-selection gain. Risk-aware routing makes only 39 effective overrides, preventing 8 Profile harms while losing 18 Profile repairs (net -10 correct answers).

Calibration-frozen selective thresholds target 80%/90%/95% calibration coverage and achieve 62.7%/81.1%/89.3% test coverage with 88.84%/80.89%/77.27% selective accuracy. These points are descriptive; no selective risk-difference significance claim is made. On 400 static ReMedQA rows, RiskRoute-CF is prediction-by-prediction identical to MedRGAG (71.0% accuracy, 53.0% ReAcc, 60.0% ReCon).

This is a four-option, pair-aware benchmark study. It provides no clinical safety guarantee and no world-model claim.

## Run and inspect

```bash
cd cf_medrgag_validation_pack
bash results_riskroute/commands.sh
```

See the [validation-pack README](cf_medrgag_validation_pack/README.md), the exact [commands](cf_medrgag_validation_pack/results_riskroute/commands.sh), and the complete [result summary](cf_medrgag_validation_pack/results_riskroute/summary.md). Historical CF-KADS-MoE, CFShift, DeltaRank, DeltaRev, and transition-card artifacts remain under their existing result directories.
