# Counterfactual medical RAG validation pack

Current scope correction: **the entire released test sets**, with no source-group sampling. The full-test run completed on 2026-09-07; results are in [results_cf_full_test](results_cf_full_test/findings.md): 25,280 unique inputs / 25,280 M2 predictions completed (100%) (user narrowed the final scope to MedRGAG-Llama base only; earlier M0/M1 outputs are preserved), reusing 3,774 identical earlier inputs. The completed screening described below was a sampled experiment, not full test-set coverage.

Full-set commands from `cf_medrgag_validation_pack`: set `export CF_SCREENING_OUTPUT=results_cf_full_test`, then `bash scripts/cf_baseline_screening.sh prepare --tier full-test`, `bash scripts/cf_baseline_screening.sh run`, and `bash scripts/cf_baseline_screening.sh analyze`.

Current work: [all-Llama baseline screening](results_cf_screening/summary.md), with [source acquisition](results_cf_screening/acquisition.md), [actual baseline contract](results_cf_screening/baseline_contract.md), and [commands](results_cf_screening/commands.sh). The fixed three methods use independent current-case inputs and native answer formats. MedEinst four-option sensitivity is separate from native diagnosis; Cultural-Cues has 1,500 released inputs and no Neutral field. Historical experiments remain below and in their original result directories.

Completed: 11,322/11,322 method predictions plus 20 independent-seed repeats. Read the [findings and limitations](results_cf_screening/findings.md), including native diagnosis mapping, original KADS selection failures, and the non-identifiable cross-source taxonomy.

Run `bash scripts/cf_baseline_screening.sh prepare`, `bash scripts/cf_baseline_screening.sh run`, then `bash scripts/cf_baseline_screening.sh analyze`. The run command includes the fixed 20-input disjoint-stream repeat after the main batch. Analysis refuses incomplete predictions or repeats unless explicitly passed `--partial`.

## Historical CF-Residual Adapter

**CF-Residual Adapter** tests whether one counterfactual sidecar transfers across two structurally different medical-RAG bases. The base system supplies a four-option score distribution; the unchanged sidecar supplies control-to-trap delta/profile and CPG scores; a small calibrated linear model returns a forced-choice diagnosis.

The integration code is intentionally small:

- `scripts/prepare_marag_medeinst.py` creates one shared MedEinst four-option mapping for MA-RAG and MedRGAG;
- `scripts/parse_marag_outputs.py` preserves official MA-RAG majority predictions while exposing smoothed vote and entropy-weighted scores;
- `scripts/run_marag_cf.py` fits or applies the portable score adapter;
- `scripts/run_cf_marag_native.py` contains the separate, non-confirmatory MA-RAG-native variants;
- `scripts/evaluate_marag_cf.py` computes pair, revision, false-consensus, efficiency, and paired-bootstrap metrics.

The official MA-RAG checkout remains external at `/home/data3/txy/MA-RAG` (commit `423f031cc0ffca679a047c885be999b9604100a9`). The project records only integration code and two small upstream compatibility/resume patches; it does not vendor or silently alter the official baseline.

## Protocol

- Pair-aware four-option MedEinst MCQ proxy, not official open diagnosis.
- Development/calibration/fresh test: 400/150/500 disjoint pairs.
- Fresh seed: 223; overlap with all earlier test suites: zero.
- MA-RAG-int: Qwen3-8B, `N=8`, `T=4`, BM25 plus MedCPT-Cross-Encoder over MedCorp3 (PubMed, Textbooks, Wikipedia).
- Sidecar: Llama-3.1-8B-Instruct, unchanged no-document Profile and CPG formulas.
- Frozen entropy temperature: `0.05000032401354733`; frozen L2 choice: `0`.
- Invalid output is counted separately and never replaced by a base prediction.

The official MA-RAG majority vote remains the baseline. Continuous vote scores are fusion inputs only. Complete 4-4 ties are official-invalid but remain numerically scorable by the forced-choice adapter; incomplete or runtime-invalid samples remain invalid.

## Main result

| Method | Accuracy | Repairs | Harms | CHR | OCP | Pair accuracy | BTR | Invalid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MA-RAG-int | 39.2% | 0 | 0 | 0.00% | 100.00% | 17.6% | 66.76% | 8 |
| MA-RAG + CF adapter | 80.0% | 210 | 6 | 3.06% | 96.94% | 52.6% | 13.18% | 1 |
| Profile-only | 79.4% | 226 | 25 | 12.76% | 87.24% | 42.8% | 12.19% | 0 |
| Adapter without MA-RAG | 81.8% | 229 | 16 | 8.16% | 91.84% | 55.0% | 8.31% | 1 |
| MedRGAG-style | 40.8% | 0 | 0 | 0.00% | 100.00% | 17.6% | 60.54% | 0 |
| MedRGAG + CF adapter | 82.4% | 220 | 12 | 5.88% | 94.12% | 47.0% | 10.88% | 0 |

The MA-RAG and MedRGAG gains are +40.8 points (95% CI +36.6 to +45.4) and +41.6 points (+37.0 to +46.2). Cross-framework transfer is supported. Genuine MA-RAG synergy is not: full-minus-Profile is +0.6 points with CI crossing zero, and removing MA-RAG increases accuracy by 1.8 points.

The without-MA-RAG ablation removes MA-RAG inputs from the model while retaining the same runtime-eligible cohort; it does not replace the single MA-RAG runtime failure with a sidecar prediction.

Real-minus-shuffled accuracy differences are +30.0 points for delta, +37.6 for diagnosis Profile, and +7.0 for CPG; all paired-bootstrap intervals are above zero. MA-RAG produces 273 wrong-unanimous stops among 500 questions, and the post-hoc adapter repairs 190.

Seven MA-RAG trap outputs are exact vote ties and one is a recorded runtime failure. The adapter resolves five tied distributions correctly and leaves the runtime case invalid; the large improvement remains after excluding all ties.

## Scope and compatibility

The user-approved final scope includes the portable adapter, both base frameworks, the pair-prompt control, shuffles, false-consensus analysis, and static bypass checks. Fresh native MA-RAG, direct-Qwen, and three-seed robustness were deliberately not run. Completed native development/calibration results remain supplementary and non-confirmatory in `results_marag_cf/native_dev_cal_metrics.json`.

Static inputs do not activate the sidecar. The prior RiskRoute-CF static control verifies exact prediction equality on 400 ReMedQA rows for MedRGAG (71.0% accuracy, 53.0% ReAcc, 60.0% ReCon). For the 100-item MA-RAG MedQA check (72.0% accuracy), the bypass is a direct pass-through of the stored base prediction, not a second stochastic run. This is deterministic applicability isolation, not a learned safety guarantee.

The portable adapter adds no MA-RAG rounds, queries, or documents. Its one shared Llama sidecar took about 4 h 38 m 52 s for 500 pairs and recorded 3,312,304 generation-stage completion tokens; exact option-likelihood passes are additional and not counted by that token field.

## Outputs

`results_marag_cf/` contains:

- `dev.jsonl`, `calibration.jsonl`, `fresh_test.jsonl`, and `marag_dataset_map.jsonl`;
- `marag_rounds.jsonl`, `marag_option_scores.jsonl`, and `cf_expert_scores.jsonl`;
- `fusion_config.json`, `predictions.jsonl`, `metrics.json`, `metrics.csv`, and `bootstrap.json`;
- `false_consensus.csv`, `efficiency.csv`, `static_compatibility.json`, and `native_dev_cal_metrics.json`;
- `summary.md` and `commands.sh`.

Expensive raw retrieval and generation caches are ignored under `results_marag_cf/cache/`. `results_marag_cf/commands.sh` is an execution record to inspect and adapt, not a one-click driver: the Qwen services and retriever were run in separate terminals, and rerunning inference requires the private data, local models, MedCorp3, and external MA-RAG checkout.

This work supports counterfactual residual adaptation under a controlled pair-aware protocol. It provides no official MA-RAG benchmark claim, no clinical safety guarantee, and no world-model claim. Historical RiskRoute-CF and CF-KADS-MoE results remain in their original directories.
