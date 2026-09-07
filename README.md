# cf_mrg

本次及后续 benchmark 结果统一归档在 **[benchmarks/](benchmarks/README.md)**。最新：[2026-09-07 MedRGAG-Llama 完整测试](benchmarks/2026-09-07_medrgag_llama_base_full_test/README.md)。

Current scope correction: **the entire released test sets**, with no source-group sampling. The full-test run completed on 2026-09-07; results are in [cf_medrgag_validation_pack/results_cf_full_test](cf_medrgag_validation_pack/results_cf_full_test/findings.md): 25,280 unique inputs / 25,280 M2 predictions completed (100%) (user narrowed the final scope to MedRGAG-Llama base only; earlier M0/M1 outputs are preserved), reusing 3,774 identical earlier inputs. The completed screening described below was a sampled experiment, not full test-set coverage.

Full-set commands from `cf_medrgag_validation_pack`: set `export CF_SCREENING_OUTPUT=results_cf_full_test`, then `bash scripts/cf_baseline_screening.sh prepare --tier full-test`, `bash scripts/cf_baseline_screening.sh run`, and `bash scripts/cf_baseline_screening.sh analyze`.

The completed experiment is **cross-benchmark all-Llama baseline screening**: independent native-task Direct, retrieval-only, and MedRGAG-Llama inference on MedEinst, MedPIC, CPV-MedQA, Cultural-Cues, and MedCounterFact. All 11,322 planned method predictions and the fixed 20-input independent-seed repeat are complete. See the [findings and limitations](cf_medrgag_validation_pack/results_cf_screening/findings.md), [baseline contract](cf_medrgag_validation_pack/results_cf_screening/baseline_contract.md), [frozen sample counts](cf_medrgag_validation_pack/results_cf_screening/benchmark_summary.csv), and [metric tables](cf_medrgag_validation_pack/results_cf_screening/summary.md). No counterfactual sidecar was loaded in this experiment.

From `cf_medrgag_validation_pack`, the commands are `bash scripts/cf_baseline_screening.sh prepare`, `bash scripts/cf_baseline_screening.sh run`, and `bash scripts/cf_baseline_screening.sh analyze`. Runtime setup and the actual execution record are in [commands.sh](cf_medrgag_validation_pack/results_cf_screening/commands.sh). Native input text and large stage caches remain local.

The previous **CF-Residual Adapter** study below is historical. It combines unchanged control/trap option scores, DDXPlus delta-profile alignment, and Counterfactual Probability Gap scores through a small frozen linear fusion model.

## Confirmatory result

Development used 400 official MedEinst train/reference pairs, calibration used a disjoint 150, and the frozen adapter was evaluated once on 500 unused official test pairs. Methods share the same paired benchmark and four options; the counterfactual sidecar sees the pair, while the trap-only base baselines see only the trap case.

| Base framework | Base accuracy | Base + CF adapter | Difference (95% paired-bootstrap CI) |
|---|---:|---:|---:|
| MA-RAG-int, Qwen3-8B | 39.2% | 80.0% | +40.8 points [+36.6, +45.4] |
| MedRGAG-style, Llama-3.1-8B | 40.8% | 82.4% | +41.6 points [+37.0, +46.2] |

The result supports cross-framework transfer under this protocol. It does not establish MA-RAG synergy: Profile-only reaches 79.4%, and the adapter without any MA-RAG score reaches 81.8%, above the full MA-RAG adapter. Real delta, Profile, and CPG signals beat their shuffled controls by 30.0, 37.6, and 7.0 points respectively.

MA-RAG ends with a wrong unanimous candidate pool on 273/500 questions (54.6%). The post-hoc adapter repairs 190/273 of these cases, showing that patient-state conflict can expose errors missed by answer-to-answer conflict. The fresh native trigger and seed-robustness extensions were not run after the user narrowed the final scope to the portable core experiment.

This is not an official open-diagnosis MedEinst result, a reproduction of MA-RAG's original seven-benchmark table, a clinical safety guarantee, or a world-model claim.

## Run and inspect

The implementation and tracked outputs are under [`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/). See the exact [commands](cf_medrgag_validation_pack/results_marag_cf/commands.sh), full [report](cf_medrgag_validation_pack/results_marag_cf/summary.md), frozen [fusion configuration](cf_medrgag_validation_pack/results_marag_cf/fusion_config.json), and [metrics](cf_medrgag_validation_pack/results_marag_cf/metrics.json).

Historical RiskRoute-CF, CF-KADS-MoE, CFShift, DeltaRank, DeltaRev, and transition-card results remain in their existing result directories.
