# RiskRoute-CF validation pack

**RiskRoute-CF** is uncertainty-calibrated, risk-aware expert routing for paired counterfactual Medical RAG. It predicts whether each valid trap case should use the original MedRGAG reader answer or the existing no-document delta-profile answer. It does not add another reasoning expert, use a hard preserve/revise gate, or claim clinical safety or a world model.

The compact implementation is in [`scripts/run_riskroute.py`](scripts/run_riskroute.py) and [`scripts/evaluate_riskroute.py`](scripts/evaluate_riskroute.py). Exact commands and the full report are in [`results_riskroute/commands.sh`](results_riskroute/commands.sh) and [`results_riskroute/summary.md`](results_riskroute/summary.md).

## Method and protocol

- The MedRGAG branch outputs the original reader's `baseline_label_id`; its four option scores are reliability features only. The Profile branch outputs the no-document profile argmax.
- Fifteen interpretable, label-ID-free features cover uncertainty, expert agreement, CPG availability/agreement, matched-evidence similarity, and CF-KADS interference. CPG structural N/A uses the development mean plus an availability indicator.
- Scalar temperature scaling is fit on development for MedRGAG option scores, Profile, CPG, CF-KADS, and Direct. L2 logistic models estimate MedRGAG correctness, Profile correctness, and Profile-induced harm; calibration-only Platt scaling calibrates these estimators.
- Forced choice always selects MedRGAG or Profile for every valid paired row. The risk score is `q_profile - q_medrgag - lambda_harm * h_profile`; calibration selected `lambda_harm=2` from `{0, 0.5, 1, 2}` using `(repairs - 2 * harms) / N`.
- Core score failures are invalid and never become MedRGAG predictions. Exact ties use the prespecified higher calibrated option confidence, then Profile on an exact confidence tie.
- Inputs without a control case, trap case, and structured delta have `applicability=false` and return MedRGAG unchanged. This is the method's domain boundary, not an uncertainty gate.

Development contains 800 official MedEinst train/reference pairs and calibration contains 200 disjoint pairs. The previously observed fresh 1,000 are exploratory only and did not select features, variants, lambda, or thresholds. A new seed-113 sample of 1,000 complete official test pairs was selected after excluding every `source_case_id` used by DeltaRank, CFShift, or CF-KADS-MoE. Features, temperatures, models, lambda, and selective thresholds were frozen before the new test was scored. All 1,000 confirmatory rows were valid; all forced routers produced an answer.

## Confirmatory new-test result

| Method | Accuracy | Repairs | Harms | CHR | OCP | Net correction | Profile coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| MedRGAG reader | 41.8% | 0 | 0 | 0.00% | 100.00% | 0.0% | 0.0% |
| Profile, no document | 74.3% | 361 | 36 | 8.61% | 91.39% | 32.5% | 100.0% |
| Confidence heuristic | 71.0% | 318 | 26 | 6.22% | 93.78% | 29.2% | 89.8% |
| Margin heuristic | 67.6% | 277 | 19 | 4.55% | 95.45% | 25.8% | 79.7% |
| Uncalibrated router | 74.3% | 361 | 36 | 8.61% | 91.39% | 32.5% | 74.1% |
| Calibrated forced router | 74.3% | 361 | 36 | 8.61% | 91.39% | 32.5% | 78.8% |
| Risk-aware router | 73.3% | 343 | 28 | 6.70% | 93.30% | 31.5% | 74.8% |
| Three-path router | 76.2% | 386 | 42 | 10.05% | 89.95% | 34.4% | 86.4% |
| Existing learned fusion | 81.0% | 443 | 51 | 12.20% | 87.80% | 39.2% | n/a |

The two-expert oracle is 77.9%. Risk-aware routing reduces Profile harms from 36 to 28 and CHR from 8.61% to 6.70%, but accuracy falls from 74.3% to 73.3%. The paired-bootstrap risk-minus-Profile difference is -1.0 accuracy point (95% CI -2.0 to 0.0) and -1.91 CHR points (95% CI -3.34 to -0.73). This is an accuracy–risk trade-off, not a Pareto improvement. It misses the prespecified strong and medium criteria, so the confirmatory benchmark does not support a positive safety-aware routing claim.

MedRGAG and Profile agree on 516/1,000 original predictions. The calibrated forced router selects MedRGAG 212 times, but all of those rows have the same final label as Profile; its final predictions equal Profile on 1,000/1,000 rows and provide no capability-selection gain. Risk-aware routing differs from Profile on only 39 rows: it prevents 8 Profile harms but loses 18 Profile repairs, for a net loss of 10 correct answers.

The calibration direction is reproduced only under the explicitly reported within-1pp accuracy tolerance: calibration/test risk-minus-Profile accuracy is 0.0/-1.0 points and CHR is -2.30/-1.91 points. Strict non-decreasing accuracy does not replicate.

## Calibration, evidence, and selective analysis

On confirmatory test, temperature scaling improves ECE, Brier, and NLL for all five option-score experts. Platt scaling improves all three metrics for `q_profile` (ECE 0.03655→0.03460, Brier 0.14815→0.14813, NLL 0.45120→0.44970) and the harm estimator (0.23566→0.01440, 0.16795→0.03189, 0.50460→0.11464). For `q_medrgag`, ECE/Brier improve slightly while NLL worsens from 0.37952 to 0.38266. Secondary `q_cf_kads` Platt calibration worsens ECE/Brier/NLL from 0.0698/0.1973/0.5784 to 0.0923/0.2018/0.5884. The harm target has only 5 positive calibration rows (36 on test), so its calibration and penalty are data-limited. Calibration-split fit metrics and external test metrics are kept separate in [`results_riskroute/calibration_metrics.json`](results_riskroute/calibration_metrics.json).

Original KADS evidence has 34.32% evidence-induced harm and 33.85% evidence-induced benefit relative to Profile no-document. CF-KADS has 24.90% harm and 50.19% benefit. Its margin-difference harm classifier reaches AUROC 0.627/AUPRC 0.337; these are interference diagnostics, not a new retrieval method.

Selective thresholds were frozen from calibration quantiles. Calibration targets 80%/90%/95% yield actual test coverage 62.7%/81.1%/89.3%, selective accuracy 88.84%/80.89%/77.27%, and selective risk 11.16%/19.11%/22.73%; AURC is 0.09883. The full test-ranked curve is diagnostic, and the frozen operating points are descriptive because no selective risk-difference significance test was prespecified.

On 400 static ReMedQA rows (100 source questions), RiskRoute-CF and MedRGAG are prediction-by-prediction identical: 71.0% accuracy, 53.0% ReAcc, and 60.0% ReCon.

## Running and outputs

After the local private releases, corpus, model, and historical caches are available at the documented paths:

```bash
cd cf_medrgag_validation_pack
bash results_riskroute/commands.sh
```

The command file records the 20-case smoke test, development fit, calibration freeze, unseen-test selection, exact three-GPU scoring/merge sequence, evaluation, and tests. It exports `TMPDIR=/home/data3/txy/.cache/riskroute_tmp`. An initial isolated two-shard option debug run produced 120 rows and was stopped; those rows are not inputs to the formal exact merge.

Tracked outputs under [`results_riskroute/`](results_riskroute/) are:

- `dev_features.jsonl`, `calibration_features.jsonl`, and `new_test.jsonl`;
- `expert_probabilities.jsonl` and `router_predictions.jsonl`;
- `router_models.json`, `calibration_metrics.json`, and `feature_analysis.csv`;
- `metrics.json`, `metrics.csv`, `bootstrap.json`, and `risk_coverage.csv`;
- `summary.md` and `commands.sh`.

Expensive prompt/model caches remain ignored under `results_cfmoe/cache/riskroute/`. Historical CF-KADS-MoE findings remain in [`results_cfmoe/summary.md`](results_cfmoe/summary.md); CFShift and DeltaRank artifacts remain under their existing result directories.
