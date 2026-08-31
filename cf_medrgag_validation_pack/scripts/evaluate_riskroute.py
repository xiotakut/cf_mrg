#!/usr/bin/env python3
"""Evaluate a frozen RiskRoute-CF controller on the one-shot confirmatory test."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

import run_riskroute as RR


ROOT = RR.ROOT
RESULTS = RR.RESULTS
CACHE = ROOT / "results_cfmoe/cache/riskroute"


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def two_expert_route(records: list[dict[str, Any]], q: dict[str, np.ndarray], harm_lambda: float,
                     calibrated: bool = True) -> tuple[dict[str, int | None], dict[str, str], int]:
    valid = [row for row in records if row["status"] == "ok"]
    harm = q["h_profile"] if calibrated else np.zeros(len(valid))
    predictions, choices, ties = RR.route_two(q["q_medrgag"], q["q_profile"], harm, valid, harm_lambda)
    by_id = {row["case_id"]: prediction for row, prediction in zip(valid, predictions)}
    choice = {row["case_id"]: value for row, value in zip(valid, choices)}
    for row in records:
        by_id.setdefault(row["case_id"], None); choice.setdefault(row["case_id"], "invalid")
    return by_id, choice, ties


def heuristic(records: list[dict[str, Any]], kind: str) -> tuple[dict[str, int | None], dict[str, str], int]:
    predictions, choices, ties = {}, {}, 0
    for row in records:
        key = row["case_id"]
        if row["status"] != "ok":
            predictions[key], choices[key] = None, "invalid"
            continue
        med = {int(label): value for label, value in row["expert_probabilities"]["medrgag"].items()}
        profile = {int(label): value for label, value in row["expert_probabilities"]["profile"].items()}
        if kind == "confidence":
            med_value, profile_value = max(med.values()), max(profile.values())
        else:
            med_value = RR.probability_summary(med)[1]
            profile_value = RR.probability_summary(profile)[1]
        if math.isclose(med_value, profile_value, abs_tol=1e-12):
            ties += 1
        choose_profile = profile_value >= med_value
        predictions[key] = row["profile_prediction"] if choose_profile else row["medrgag_prediction"]
        choices[key] = "profile" if choose_profile else "medrgag"
    return predictions, choices, ties


def three_path(records: list[dict[str, Any]], q: dict[str, np.ndarray]) -> tuple[dict[str, int | None], dict[str, str], int]:
    valid = [row for row in records if row["status"] == "ok"]
    predictions, choices, ties = {}, {}, 0
    names = ("medrgag", "profile", "cf_kads")
    targets = ("q_medrgag", "q_profile", "q_cf_kads")
    for index, row in enumerate(valid):
        values = {name: float(q[target][index]) for name, target in zip(names, targets)}
        peak = max(values.values())
        candidates = [name for name in names if math.isclose(values[name], peak, abs_tol=1e-12)]
        if len(candidates) > 1:
            ties += 1
            candidates.sort(key=lambda name: (
                -max(map(float, row["expert_probabilities"].get(name, {}).values() or [float("-inf")])),
                {"profile": 0, "cf_kads": 1, "medrgag": 2}[name]))
        chosen = candidates[0]
        prediction = (row["medrgag_prediction"] if chosen == "medrgag" else
                      row["profile_prediction"] if chosen == "profile" else
                      row["profile_cf_kads_prediction"])
        predictions[row["case_id"]], choices[row["case_id"]] = prediction, chosen
    for row in records:
        predictions.setdefault(row["case_id"], None); choices.setdefault(row["case_id"], "invalid")
    return predictions, choices, ties


def oracle(records: list[dict[str, Any]]) -> dict[str, int | None]:
    values = {}
    for row in records:
        if row["status"] != "ok":
            values[row["case_id"]] = None
        elif row["profile_prediction"] == row["gold_label_id"]:
            values[row["case_id"]] = row["profile_prediction"]
        else:
            values[row["case_id"]] = row["medrgag_prediction"]
    return values


def method_metrics(prediction: dict[str, int | None], choice: dict[str, str],
                   records: list[dict[str, Any]]) -> dict[str, Any]:
    truth = {row["case_id"]: {"control": {"label_id": row["control_gold_label_id"]},
                               "trap": {"label_id": row["gold_label_id"]}} for row in records}
    baseline = {row["case_id"]: row["medrgag_prediction"] for row in records}
    control = {row["case_id"]: row["medrgag_control_prediction"] for row in records}
    value = {**RR.CF_EVAL.revision_metrics(prediction, baseline, truth),
             **RR.CF_EVAL.pair_metrics(control, prediction, truth)}
    valid_choices = [choice.get(row["case_id"]) for row in records if choice.get(row["case_id"]) != "invalid"]
    is_router = any(item in {"medrgag", "profile", "cf_kads"} for item in valid_choices)
    value["profile_routing_coverage"] = (sum(item in {"profile", "cf_kads"} for item in valid_choices)
                                          / len(valid_choices) if valid_choices and is_router else None)
    value["beneficial_routing_precision"] = value["beneficial_revision_precision"]
    value["error_correction_rate"] = value["repair_rate"]
    value["robust_accuracy"] = value["both_correct_pair_accuracy"]
    return value


def routing_diagnostics(predictions: dict[str, dict[str, int | None]],
                        choices: dict[str, dict[str, str]], records: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in records if row["status"] == "ok"]
    result: dict[str, Any] = {
        "medrgag_profile_prediction_agreement_count": sum(
            row["medrgag_prediction"] == row["profile_prediction"] for row in valid),
        "n": len(valid),
    }
    result["medrgag_profile_prediction_agreement_rate"] = ratio(
        result["medrgag_profile_prediction_agreement_count"], len(valid))
    result["routers"] = {}
    for method in ("calibrated_forced_router", "risk_aware_router"):
        routed = predictions[method]
        changed = [row for row in valid if routed[row["case_id"]] != row["profile_prediction"]]
        prevented = sum(row["profile_prediction"] != row["gold_label_id"]
                        and row["medrgag_prediction"] == row["gold_label_id"]
                        and routed[row["case_id"]] == row["gold_label_id"] for row in changed)
        lost = sum(row["profile_prediction"] == row["gold_label_id"]
                   and row["medrgag_prediction"] != row["gold_label_id"]
                   and routed[row["case_id"]] != row["gold_label_id"] for row in changed)
        result["routers"][method] = {
            "selected_medrgag_count": sum(choices[method][row["case_id"]] == "medrgag" for row in valid),
            "selected_profile_count": sum(choices[method][row["case_id"]] == "profile" for row in valid),
            "prediction_agreement_with_profile_count": len(valid) - len(changed),
            "prediction_agreement_with_profile_rate": ratio(len(valid) - len(changed), len(valid)),
            "effective_profile_override_count": len(changed),
            "prevented_profile_harms": prevented,
            "lost_profile_repairs": lost,
            "net_correctness_from_effective_overrides": prevented - lost,
        }
    return result


def method_specific_control_appendix(predictions: dict[str, dict[str, int | None]],
                                     choices: dict[str, dict[str, str]],
                                     rows: list[dict[str, Any]], fusion: dict[str, Any]) -> dict[str, Any]:
    truth = {row["case_id"]: {"control": {"label_id": row["control_gold_label_id"]},
                               "trap": {"label_id": row["gold_label_id"]}} for row in rows}
    branch_method = {"medrgag": "medrgag_mcq_proxy", "profile": "profile_no_document",
                     "cf_kads": "profile_cf_kads"}
    methods = {}
    for method, trap_prediction in predictions.items():
        if method == "oracle_two_expert":
            methods[method] = {"status": "not_applicable_to_gold_oracle"}
            continue
        controls = {}
        for row in rows:
            key = row["case_id"]
            chosen = choices[method][key]
            if chosen == "fusion":
                controls[key] = RR.CFMOE_RUN.prediction_for(row, "learned_fusion", fusion, control=True)
            elif chosen in branch_method:
                controls[key] = RR.CFMOE_RUN.prediction_for(row, branch_method[chosen], fusion, control=True)
            else:
                controls[key] = None
        methods[method] = {"status": "appendix_nonprimary", **RR.CF_EVAL.pair_metrics(
            controls, trap_prediction, truth)}
    return {
        "protocol": "nonprimary appendix; control follows each selected branch: baseline_control_label_id for MedRGAG, saved control_scores for Profile/CF-KADS, existing control fusion for learned fusion; no new inference",
        "main_protocol_remains": "unchanged MedRGAG reader control prediction for every method",
        "methods": methods,
    }


def selective(records: list[dict[str, Any]], prediction: dict[str, int | None],
              confidence: dict[str, float], thresholds: dict[str, float]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    valid = [row for row in records if row["status"] == "ok"]
    ordered = sorted(valid, key=lambda row: (-confidence[row["case_id"]], row["case_id"]))
    curve = []
    risks = []
    for count, row in enumerate(ordered, 1):
        selected_rows = ordered[:count]
        correct = sum(prediction[value["case_id"]] == value["gold_label_id"] for value in selected_rows)
        risk = 1 - correct / count
        risks.append(risk)
        repairs = sum(value["medrgag_prediction"] != value["gold_label_id"]
                      and prediction[value["case_id"]] == value["gold_label_id"] for value in selected_rows)
        harms = sum(value["medrgag_prediction"] == value["gold_label_id"]
                    and prediction[value["case_id"]] != value["gold_label_id"] for value in selected_rows)
        curve.append({"kind": "test_ranked_curve", "target_coverage": None,
                      "threshold": confidence[row["case_id"]], "selected": count,
                      "coverage": count / len(records), "selective_accuracy": correct / count,
                      "selective_risk": risk, "repairs": repairs, "harms": harms,
                      "abstention_rate": 1 - count / len(records)})
    points = {}
    for target, threshold in thresholds.items():
        chosen = [row for row in valid if confidence[row["case_id"]] >= threshold]
        correct = sum(prediction[row["case_id"]] == row["gold_label_id"] for row in chosen)
        repairs = sum(row["medrgag_prediction"] != row["gold_label_id"]
                      and prediction[row["case_id"]] == row["gold_label_id"] for row in chosen)
        harms = sum(row["medrgag_prediction"] == row["gold_label_id"]
                    and prediction[row["case_id"]] != row["gold_label_id"] for row in chosen)
        base_correct = sum(row["medrgag_prediction"] == row["gold_label_id"] for row in chosen)
        point = {"target_calibration_coverage": int(target) / 100, "threshold": threshold,
                 "selected": len(chosen), "test_coverage": len(chosen) / len(records),
                 "selective_accuracy": ratio(correct, len(chosen)),
                 "selective_risk": ratio(len(chosen) - correct, len(chosen)),
                 "repairs": repairs, "harms": harms,
                 "conditional_harm_rate": ratio(harms, base_correct),
                 "abstention_rate": 1 - len(chosen) / len(records)}
        points[target] = point
        curve.append({"kind": "frozen_calibration_operating_point", "target_coverage": int(target) / 100,
                      "threshold": threshold, "selected": len(chosen), "coverage": point["test_coverage"],
                      "selective_accuracy": point["selective_accuracy"], "selective_risk": point["selective_risk"],
                      "repairs": repairs, "harms": harms, "abstention_rate": point["abstention_rate"]})
    return {"aurc": float(np.mean(risks)), "frozen_operating_points": points,
            "curve_note": "ranked test curve is diagnostic; 80/90/95 thresholds were frozen on calibration"}, curve


def bootstrap_metric(prediction: dict[str, int | None], records: list[dict[str, Any]], indices: np.ndarray
                     ) -> tuple[float, float, float]:
    chosen = [records[index] for index in indices]
    correct = np.asarray([prediction[row["case_id"]] == row["gold_label_id"] for row in chosen], dtype=float)
    base_correct = np.asarray([row["medrgag_prediction"] == row["gold_label_id"] for row in chosen], dtype=bool)
    harm = base_correct & ~correct.astype(bool)
    repairs = ~base_correct & correct.astype(bool)
    accuracy = float(correct.mean())
    conditional_harm = float(harm.sum() / base_correct.sum()) if base_correct.any() else float("nan")
    net = float((repairs.sum() - harm.sum()) / len(chosen))
    return accuracy, conditional_harm, net


def paired_bootstrap(methods: dict[str, dict[str, int | None]], records: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = (
        ("profile_no_document", "medrgag"),
        ("calibrated_forced_router", "profile_no_document"),
        ("risk_aware_router", "profile_no_document"),
        ("risk_aware_router", "learned_fusion_existing"),
        ("risk_aware_router", "confidence_heuristic"),
        ("risk_aware_router", "uncalibrated_router"),
    )
    generator = np.random.default_rng(RR.SEED)
    result = {}
    for left, right in comparisons:
        observed_left = bootstrap_metric(methods[left], records, np.arange(len(records)))
        observed_right = bootstrap_metric(methods[right], records, np.arange(len(records)))
        samples = [[], [], []]
        for _ in range(1000):
            indices = generator.integers(0, len(records), len(records))
            l_value, r_value = bootstrap_metric(methods[left], records, indices), bootstrap_metric(methods[right], records, indices)
            for metric in range(3):
                samples[metric].append(l_value[metric] - r_value[metric])
        names = ("accuracy_difference", "conditional_harm_difference", "net_correction_difference")
        result[f"{left}_minus_{right}"] = {
            name: {"difference": observed_left[index] - observed_right[index],
                   "ci_low": float(np.nanpercentile(samples[index], 2.5)),
                   "ci_high": float(np.nanpercentile(samples[index], 97.5)), "samples": 1000}
            for index, name in enumerate(names)}
    return result


def evidence_metrics(rows: list[dict[str, Any]], records: list[dict[str, Any]],
                     temperatures: dict[str, float]) -> dict[str, Any]:
    by_id = {row["case_id"]: row for row in records}
    result = {}
    for method in ("profile_original_kads", "profile_cf_kads"):
        no_correct, with_correct, features = [], [], []
        for row in rows:
            record = by_id[row["case_id"]]
            document_scores = RR.scores(row, method)
            if record["status"] != "ok" or not RR.finite_scores(document_scores, row["option_label_ids"]):
                continue
            no_correct.append(record["profile_prediction"] == row["gold_label_id"])
            with_correct.append(RR.argmax(document_scores) == row["gold_label_id"])
            no_probability = {int(key): float(value) for key, value in record["expert_probabilities"]["profile"].items()}
            document_temperature = temperatures["cf_kads"] if method == "profile_cf_kads" else temperatures["profile"]
            document_probability = RR.softmax(document_scores, document_temperature)
            features.append(RR.probability_summary(no_probability)[1]
                            - RR.probability_summary(document_probability)[1])
        harm = np.asarray([left and not right for left, right in zip(no_correct, with_correct)], dtype=int)
        benefit = np.asarray([not left and right for left, right in zip(no_correct, with_correct)], dtype=int)
        score = np.asarray(features)
        def separability(target: np.ndarray, values: np.ndarray) -> dict[str, Any]:
            return {"auroc": float(roc_auc_score(target, values)),
                    "auprc": float(average_precision_score(target, values))} if len(set(target)) == 2 else {
                        "auroc": None, "auprc": None}
        result[method] = {
            "n": len(no_correct), "invalid_count": len(rows) - len(no_correct),
            "evidence_induced_harm_rate": ratio(int(harm.sum()), sum(no_correct)),
            "evidence_induced_benefit_rate": ratio(int(benefit.sum()), len(no_correct) - sum(no_correct)),
            "harm_count": int(harm.sum()), "benefit_count": int(benefit.sum()),
            "interference_score": f"profile_no_document_margin_minus_{method}_margin",
            "harm_separability": separability(harm, score),
            "benefit_separability": separability(benefit, -score),
        }
    return result


def static_control(path: Path) -> dict[str, Any]:
    rows = RR.read_jsonl(path)
    by_source: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_source.setdefault(row["source_id"], []).append(row)
    baseline = {row["item_id"]: row["original_medrgag_prediction"] for row in rows}
    riskroute = dict(baseline)
    def values(predictions: dict[str, Any]) -> dict[str, Any]:
        return {
            "accuracy": sum(predictions[row["item_id"]] == row["gold_content"] for row in rows) / len(rows),
            "ReAcc": sum(all(predictions[row["item_id"]] == row["gold_content"] for row in cluster)
                         for cluster in by_source.values()) / len(by_source),
            "ReCon": sum(len({predictions[row["item_id"]] for row in cluster}) == 1
                         and all(predictions[row["item_id"]] is not None for row in cluster)
                         for cluster in by_source.values()) / len(by_source),
        }
    base_metrics, routed_metrics = values(baseline), values(riskroute)
    return {"source_questions": len(by_source), "rows": len(rows), "applicability": False,
            "prediction_by_prediction_equal": all(baseline[key] == riskroute[key] for key in baseline),
            "baseline": base_metrics, "riskroute": routed_metrics,
            "accuracy_equal": base_metrics["accuracy"] == routed_metrics["accuracy"],
            "ReAcc_equal": base_metrics["ReAcc"] == routed_metrics["ReAcc"],
            "ReCon_equal": base_metrics["ReCon"] == routed_metrics["ReCon"]}


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def summary(metrics: dict[str, Any]) -> str:
    methods = metrics["methods"]
    risk, profile = methods["risk_aware_router"], methods["profile_no_document"]
    success = metrics["success_assessment"]
    pareto = success["strong_pareto"]
    selective_points = metrics["selective"]["frozen_operating_points"]
    coefficients = sorted(metrics["feature_analysis"], key=lambda row: -abs(row["harm_coefficient"] or 0))[:3]
    bootstrap = metrics["bootstrap"]["risk_aware_router_minus_profile_no_document"]
    routing = metrics["routing_diagnostics"]
    forced_route = routing["routers"]["calibrated_forced_router"]
    risk_route = routing["routers"]["risk_aware_router"]
    temperature_cal = metrics["calibration"]["temperature"]["calibration"]
    temperature_improvements = {
        name: sum(value["after"][metric] < value["before"][metric]
                  for metric in ("ece", "brier", "nll"))
        for name, value in temperature_cal.items()
    }
    main_correctness = metrics["calibration"]["correctness_estimators"]
    platt_improvements = {
        metric: sum(main_correctness[name]["after"][metric] < main_correctness[name]["before"][metric]
                    for name in ("q_medrgag", "q_profile", "h_profile"))
        for metric in ("ece", "brier", "nll")
    }
    temperature_test = metrics["calibration"]["test_temperature"]
    temperature_test_improvements = {
        name: sum(value["after"][metric] < value["before"][metric]
                  for metric in ("ece", "brier", "nll"))
        for name, value in temperature_test.items()
    }
    correctness_test = metrics["calibration"]["test_correctness"]
    platt_test_improvements = {
        metric: sum(correctness_test[name]["after"][metric] < correctness_test[name]["before"][metric]
                    for name in ("q_medrgag", "q_profile", "h_profile"))
        for metric in ("ece", "brier", "nll")
    }
    test_correctness_detail = "; ".join(
        f"{name} ECE/Brier/NLL "
        f"{correctness_test[name]['before']['ece']:.3f}/"
        f"{correctness_test[name]['before']['brier']:.3f}/"
        f"{correctness_test[name]['before']['nll']:.3f} -> "
        f"{correctness_test[name]['after']['ece']:.3f}/"
        f"{correctness_test[name]['after']['brier']:.3f}/"
        f"{correctness_test[name]['after']['nll']:.3f}"
        for name in ("q_medrgag", "q_profile", "h_profile")
    )
    exploratory = metrics["exploratory_existing_fresh_1000"]
    exploratory_features = sorted(
        exploratory["repair_vs_harm_feature_separability"],
        key=lambda row: -(row["orientation_free_separability_auroc"] or 0))[:3]
    exploratory_qp = exploratory["correctness_calibration_on_exploratory_fresh_1000"]["q_profile"]
    lines = [
        "# RiskRoute-CF results", "",
        "RiskRoute-CF is uncertainty-calibrated, safety-aware expert routing for paired counterfactual Medical RAG. It is not a clinical safety guarantee or a world model.", "",
        "## Confirmatory new 1,000-pair test", "",
        "| Method | Accuracy | Repairs | Harms | CHR | OCP | Net correction | Profile coverage | Invalid |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("medrgag", "profile_no_document", "learned_fusion_existing", "confidence_heuristic",
                 "margin_heuristic", "uncalibrated_router", "calibrated_forced_router", "risk_aware_router",
                 "three_path_router"):
        value = methods[name]
        lines.append(f"| {name} | {pct(value['accuracy'])} | {value['repairs']} | {value['harms']} | "
                     f"{pct(value['conditional_harm_rate'])} | {pct(value['original_correct_preservation'])} | "
                     f"{pct(value['net_correction'])} | {pct(value['profile_routing_coverage'])} | {value['invalid_count']} |")
    lines += ["", "## Appendix: method-specific control prediction", "",
              "This nonprimary view follows each selected trap-side branch: the reader baseline control for MedRGAG, saved control scores for Profile/CF-KADS, and existing control fusion for learned fusion. The main table above keeps the unchanged MedRGAG reader control for every method.", "",
              "| Method | Control accuracy | Both-correct pair accuracy | Bias Trap Rate |",
              "|---|---:|---:|---:|"]
    for name in ("medrgag", "profile_no_document", "learned_fusion_existing", "confidence_heuristic",
                 "margin_heuristic", "uncalibrated_router", "calibrated_forced_router", "risk_aware_router",
                 "three_path_router"):
        value = metrics["method_specific_control_appendix"]["methods"][name]
        lines.append(f"| {name} | {pct(value['control_accuracy'])} | "
                     f"{pct(value['both_correct_pair_accuracy'])} | {pct(value['bias_trap_rate'])} |")
    lines += ["", "## Phase-0 exploratory analysis", "",
              "The previously observed fresh-1,000 was evaluated only after freezing the model and never selected features, lambda, or thresholds. "
              f"Its two-expert oracle/profile/risk-aware accuracies are "
              f"{pct(exploratory['two_expert_oracle']['accuracy'])}/{pct(exploratory['profile']['accuracy'])}/"
              f"{pct(exploratory['risk_aware_router']['accuracy'])}; risk-aware repairs/harms are "
              f"{exploratory['risk_aware_router']['repairs']}/{exploratory['risk_aware_router']['harms']}. "
              f"Frozen q_profile Platt ECE is {exploratory_qp['before']['ece']:.3f} -> "
              f"{exploratory_qp['after']['ece']:.3f}. Strongest orientation-free single-feature repair/harm AUROCs: " +
              ", ".join(f"`{row['feature']}`={row['orientation_free_separability_auroc']:.3f}"
                        for row in exploratory_features) + ". Development-trained coefficients are saved alongside these diagnostics.",
              "", "## Required answers", "",
              f"1. Two-expert oracle upper bound: {pct(methods['oracle_two_expert']['accuracy'])}.",
              "2. Strongest repair/harm indicators by the frozen standardized harm model: " +
              ", ".join(f"`{row['feature']}` ({row['harm_coefficient']:+.3f})" for row in coefficients) + ".",
              "3. Calibration: temperature scaling improved ECE/Brier/NLL for " +
              f"{sum(value == 3 for value in temperature_improvements.values())}/{len(temperature_improvements)} experts; "
              f"Platt improved ECE for {platt_improvements['ece']}/3, Brier for "
              f"{platt_improvements['brier']}/3, and NLL for {platt_improvements['nll']}/3 main estimators. "
              "These are calibration-split fit/selection results. On confirmatory test, temperature improved all three metrics for "
              f"{sum(value == 3 for value in temperature_test_improvements.values())}/{len(temperature_test_improvements)} experts; "
              f"among the three main estimators, Platt improved ECE for {platt_test_improvements['ece']}/3, "
              f"Brier for {platt_test_improvements['brier']}/3, and NLL for {platt_test_improvements['nll']}/3. "
              f"Confirmatory values: {test_correctness_detail}. The secondary q_cf_kads Platt calibration worsens "
              f"ECE/Brier/NLL {correctness_test['q_cf_kads']['before']['ece']:.3f}/"
              f"{correctness_test['q_cf_kads']['before']['brier']:.3f}/"
              f"{correctness_test['q_cf_kads']['before']['nll']:.3f} -> "
              f"{correctness_test['q_cf_kads']['after']['ece']:.3f}/"
              f"{correctness_test['q_cf_kads']['after']['brier']:.3f}/"
              f"{correctness_test['q_cf_kads']['after']['nll']:.3f}. Full values are in `calibration_metrics.json`.",
              f"4. Calibrated forced router accuracy {pct(methods['calibrated_forced_router']['accuracy'])}; confidence "
              f"{pct(methods['confidence_heuristic']['accuracy'])}, margin {pct(methods['margin_heuristic']['accuracy'])}. "
              f"However, forced-router predictions match Profile on {forced_route['prediction_agreement_with_profile_count']}/"
              f"{routing['n']} rows despite selecting MedRGAG {forced_route['selected_medrgag_count']} times, so it realizes no capability selection gain.",
              f"5. Risk-aware CHR {pct(risk['conditional_harm_rate'])} vs profile {pct(profile['conditional_harm_rate'])}.",
              f"6. Accuracy cost relative to profile: {100 * (risk['accuracy'] - profile['accuracy']):+.1f}pp.",
              f"7. Accuracy/harm Pareto improvement: {'Yes' if pareto else 'No'}.",
              f"8. CPG incremental value (accuracy/CHR): full {pct(risk['accuracy'])}/"
              f"{pct(risk['conditional_harm_rate'])} vs without CPG "
              f"{pct(methods['router_without_cpg_features']['accuracy'])}/"
              f"{pct(methods['router_without_cpg_features']['conditional_harm_rate'])}.",
              f"9. Interference-feature incremental value (accuracy/CHR): full {pct(risk['accuracy'])}/"
              f"{pct(risk['conditional_harm_rate'])} vs without interference "
              f"{pct(methods['router_without_interference_features']['accuracy'])}/"
              f"{pct(methods['router_without_interference_features']['conditional_harm_rate'])}.",
              f"10. Three-path {pct(methods['three_path_router']['accuracy'])} vs two-expert risk-aware {pct(risk['accuracy'])}.",
              "11. Frozen selective operating points: " + "; ".join(
                  f"target {key}% -> test coverage {pct(value['test_coverage'])}, accuracy {pct(value['selective_accuracy'])}, risk {pct(value['selective_risk'])}"
                  for key, value in selective_points.items()) + f"; AURC={metrics['selective']['aurc']:.4f}.",
              f"12. New-test reproduces the strict calibration direction: {metrics['calibration_direction']['replicated']} "
              f"(within-1pp accuracy direction: {metrics['calibration_direction']['replicated_within_one_point_accuracy']}). "
              f"Calibration/test risk-minus-profile accuracy={100 * metrics['calibration_direction']['calibration_accuracy_difference']:+.1f}/"
              f"{100 * metrics['calibration_direction']['test_accuracy_difference']:+.1f}pp; CHR difference="
              f"{100 * metrics['calibration_direction']['calibration_chr_difference']:+.1f}/"
              f"{100 * metrics['calibration_direction']['test_chr_difference']:+.1f}pp.",
              f"13. Static ReMedQA: prediction equality={metrics['static_control']['prediction_by_prediction_equal']}; "
              f"accuracy/ReAcc/ReCon={pct(metrics['static_control']['riskroute']['accuracy'])}/"
              f"{pct(metrics['static_control']['riskroute']['ReAcc'])}/{pct(metrics['static_control']['riskroute']['ReCon'])}.",
              f"14. Safety-aware counterfactual routing claim: {success['claim']}. "
              f"Strong={success['strong_pareto']}, medium-A={success['medium_accuracy_preserving_harm_reduction']}, "
              f"medium-B={success['medium_accuracy_gain']}, selective-significant={success['selective_positive']} "
              f"(descriptive improvement={success['selective_descriptive_improvement']}; no selective risk-difference CI).",
              "15. No clinical safety guarantee.", "16. No world-model claim.", "",
              "## Routing mechanism diagnosis", "",
              f"MedRGAG and Profile originally agree on {routing['medrgag_profile_prediction_agreement_count']}/{routing['n']} rows. "
              f"Risk-aware routing matches Profile on {risk_route['prediction_agreement_with_profile_count']}/{routing['n']} rows and makes "
              f"{risk_route['effective_profile_override_count']} effective overrides: it prevents {risk_route['prevented_profile_harms']} "
              f"Profile harms but loses {risk_route['lost_profile_repairs']} Profile repairs (net {risk_route['net_correctness_from_effective_overrides']:+d}). "
              "This mechanism-level result is not a successful capability router.", "",
              "## Paired bootstrap", "",
              f"Risk-aware minus profile accuracy: {100 * bootstrap['accuracy_difference']['difference']:+.1f}pp "
              f"(95% CI {100 * bootstrap['accuracy_difference']['ci_low']:+.1f} to {100 * bootstrap['accuracy_difference']['ci_high']:+.1f}pp); "
              f"CHR difference {100 * bootstrap['conditional_harm_difference']['difference']:+.1f}pp "
              f"(95% CI {100 * bootstrap['conditional_harm_difference']['ci_low']:+.1f} to {100 * bootstrap['conditional_harm_difference']['ci_high']:+.1f}pp).", "",
              "## Execution note", "",
              "An initial isolated two-shard option-scoring run produced 120 debug rows and was intentionally stopped after document scoring completed. "
              "Those rows were excluded; formal option scores were exact-ID merged only from the clean three-shard `option3` directory.", "",
              "## Limitations", "",
              "- This is a four-option pair-aware MedEinst proxy, not official open-diagnosis SOTA or clinical deployment evidence.",
              "- The local all-Llama MedRGAG path is a proxy for the paper configuration.",
              "- The harm estimator has only 5 positive calibration rows (36 on confirmatory test), so its calibration and risk penalty are data-limited.",
              "- Selective DEFER is evaluated as abstention and is never replaced by MedRGAG.", ""]
    return "\n".join(lines)


def parse_feature_analysis(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    strings = {"feature", "selection_note"}
    return [{key: (value if key in strings else value == "True" if key == "used_by_router"
                   else float(value) if value not in {"", None} else None)
             for key, value in row.items()} for row in rows]


def evaluate(output_dir: Path, cache: Path) -> dict[str, Any]:
    model = json.loads((output_dir / "router_models.json").read_text(encoding="utf-8"))
    if model["status"] != "frozen_before_new_test_access":
        raise ValueError("router model is not frozen")
    rows = RR.read_jsonl(cache / "expert_scores.test.jsonl")
    documents = {row["pair_id"]: row for row in RR.read_jsonl(cache / "document_scores.test.jsonl")}
    matches = {row["pair_id"]: row for row in RR.read_jsonl(cache / "matches.test.jsonl")}
    records, _ = RR.feature_records(rows, documents, matches, model["temperatures"], model["feature_means"])
    valid = [row for row in records if row["status"] == "ok"]
    raw, calibrated = RR.router_probabilities(model["main"], records, split_seed=11)
    for index, row in enumerate(valid):
        row["routing_probabilities"] = {"raw": {key: float(value[index]) for key, value in raw.items()},
                                        "calibrated": {key: float(value[index]) for key, value in calibrated.items()}}

    predictions: dict[str, dict[str, int | None]] = {}
    choices: dict[str, dict[str, str]] = {}
    ties: dict[str, int] = {}
    predictions["medrgag"] = {row["case_id"]: row["medrgag_prediction"] if row["status"] == "ok" else None for row in records}
    choices["medrgag"] = {row["case_id"]: "medrgag" if row["status"] == "ok" else "invalid" for row in records}
    predictions["profile_no_document"] = {row["case_id"]: row.get("profile_prediction") for row in records}
    choices["profile_no_document"] = {row["case_id"]: "profile" if row["status"] == "ok" else "invalid" for row in records}
    fusion = json.loads((ROOT / "results_cfmoe/fusion_weights.json").read_text(encoding="utf-8"))
    predictions["learned_fusion_existing"] = {row["case_id"]: RR.CFMOE_RUN.prediction_for(row, "learned_fusion", fusion)
                                               for row in rows}
    choices["learned_fusion_existing"] = {row["case_id"]: "fusion" if predictions["learned_fusion_existing"][row["case_id"]] is not None else "invalid" for row in rows}
    for name, kind in (("confidence_heuristic", "confidence"), ("margin_heuristic", "margin")):
        predictions[name], choices[name], ties[name] = heuristic(records, kind)
    predictions["uncalibrated_router"], choices["uncalibrated_router"], ties["uncalibrated_router"] = two_expert_route(records, raw, 0, calibrated=False)
    predictions["calibrated_forced_router"], choices["calibrated_forced_router"], ties["calibrated_forced_router"] = two_expert_route(records, calibrated, 0)
    predictions["risk_aware_router"], choices["risk_aware_router"], ties["risk_aware_router"] = two_expert_route(
        records, calibrated, model["main"]["lambda_harm"])
    predictions["router_without_calibration"] = dict(predictions["uncalibrated_router"])
    choices["router_without_calibration"] = dict(choices["uncalibrated_router"])
    predictions["router_without_harm_predictor"] = dict(predictions["calibrated_forced_router"])
    choices["router_without_harm_predictor"] = dict(choices["calibrated_forced_router"])
    for short, key in (("router_without_cpg_features", "without_cpg_features"),
                       ("router_without_interference_features", "without_interference_features"),
                       ("router_with_shuffled_features", "shuffled_features")):
        _, probability = RR.router_probabilities(model["ablations"][key], records, split_seed=19)
        predictions[short], choices[short], ties[short] = two_expert_route(
            records, probability, model["ablations"][key]["lambda_harm"])
    predictions["three_path_router"], choices["three_path_router"], ties["three_path_router"] = three_path(records, calibrated)
    predictions["oracle_two_expert"] = oracle(records)
    choices["oracle_two_expert"] = {row["case_id"]: "oracle" if row["status"] == "ok" else "invalid" for row in records}

    metrics_path = output_dir / "metrics.json"
    previous = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    methods = {name: method_metrics(prediction, choices[name], records) for name, prediction in predictions.items()}
    control_appendix = method_specific_control_appendix(predictions, choices, rows, fusion)
    confidence = {row["case_id"]: float(max(calibrated["q_medrgag"][index], calibrated["q_profile"][index]))
                  for index, row in enumerate(valid)}
    selective_metrics, curve = selective(records, predictions["risk_aware_router"], confidence,
                                          model["selective"]["thresholds_from_calibration"])
    correctness_test = {}
    targets = {
        "q_medrgag": np.asarray([row["medrgag_correct"] for row in valid], dtype=int),
        "q_profile": np.asarray([row["profile_correct"] for row in valid], dtype=int),
        "h_profile": np.asarray([row["profile_harm"] for row in valid], dtype=int),
        "q_cf_kads": np.asarray([row["profile_cf_kads_prediction"] == row["gold_label_id"] for row in valid], dtype=int),
    }
    for target in targets:
        correctness_test[target] = {"before": RR.binary_metrics(raw[target], targets[target]),
                                    "after": RR.binary_metrics(calibrated[target], targets[target])}
    temperature_test = {short: RR.temperature_report(rows, expert, model["temperatures"][short])
                        for short, expert in RR.EXPERTS.items()}
    static = static_control(ROOT / "results_cfmoe/cache/remedqa_scores.jsonl")
    boot = paired_bootstrap(predictions, records)
    fresh_rows = [row for row in RR.read_jsonl(RR.CFMOE / "expert_scores.jsonl")
                  if row["split"] == "fresh_test"]
    fresh_documents = {row["pair_id"]: row for row in RR.read_jsonl(RR.CFMOE / "document_scores.jsonl")
                       if row["split"] == "fresh_test"}
    fresh_matches = {row["pair_id"]: row for row in RR.read_jsonl(RR.CFMOE / "cache/matches.full.jsonl")}
    fresh_records, _ = RR.feature_records(fresh_rows, fresh_documents, fresh_matches,
                                          model["temperatures"], model["feature_means"])
    exploratory = RR.exploratory_metrics(fresh_records, model["main"])
    calibration_records = [row for row in RR.read_jsonl(output_dir / "calibration_features.jsonl")
                           if row["status"] == "ok"]
    calibration_profile = RR.revision_counts([row["profile_prediction"] for row in calibration_records],
                                              calibration_records)
    calibration_base_correct = sum(row["medrgag_correct"] for row in calibration_records)
    calibration_profile_chr = calibration_profile["harms"] / calibration_base_correct
    calibration_risk = model["main"]["calibration_operating_point"]
    calibration_risk_chr = calibration_risk["harms"] / calibration_base_correct
    calibration_direction = {
        "calibration_accuracy_difference": calibration_risk["accuracy"] - calibration_profile["accuracy"],
        "test_accuracy_difference": methods["risk_aware_router"]["accuracy"] - methods["profile_no_document"]["accuracy"],
        "calibration_chr_difference": calibration_risk_chr - calibration_profile_chr,
        "test_chr_difference": (methods["risk_aware_router"]["conditional_harm_rate"]
                                - methods["profile_no_document"]["conditional_harm_rate"]),
    }
    calibration_direction["replicated"] = bool(
        calibration_direction["calibration_accuracy_difference"] >= 0
        and calibration_direction["calibration_chr_difference"] < 0
        and calibration_direction["test_accuracy_difference"] >= 0
        and calibration_direction["test_chr_difference"] < 0)
    calibration_direction["replicated_within_one_point_accuracy"] = bool(
        calibration_direction["calibration_accuracy_difference"] >= -.01 - 1e-12
        and calibration_direction["calibration_chr_difference"] < 0
        and calibration_direction["test_accuracy_difference"] >= -.01 - 1e-12
        and calibration_direction["test_chr_difference"] < 0)
    risk_value, profile_value = methods["risk_aware_router"], methods["profile_no_document"]
    strong = (risk_value["accuracy"] >= profile_value["accuracy"]
              and risk_value["conditional_harm_rate"] < profile_value["conditional_harm_rate"]
              and risk_value["repairs"] > risk_value["harms"])
    medium_a = (risk_value["accuracy"] >= profile_value["accuracy"] - .01 - 1e-12
                and risk_value["conditional_harm_rate"] <= .75 * profile_value["conditional_harm_rate"])
    medium_b = (risk_value["accuracy"] >= profile_value["accuracy"] + .01
                and risk_value["conditional_harm_rate"] <= profile_value["conditional_harm_rate"])
    selective_descriptive = any(
        point["test_coverage"] >= .8 and point["selective_risk"] <= .75 * (1 - risk_value["accuracy"])
        for point in selective_metrics["frozen_operating_points"].values())
    # Frozen operating points remain descriptive unless their risk difference receives its own CI.
    selective_positive = False
    success_assessment = {
        "strong_pareto": strong,
        "medium_accuracy_preserving_harm_reduction": medium_a,
        "medium_accuracy_gain": medium_b,
        "selective_positive": selective_positive,
        "selective_descriptive_improvement": selective_descriptive,
        "selective_significance_tested": False,
        "selective_rule": "descriptive only; it cannot independently support the claim without a risk-difference CI",
        "claim": ("Supported on this paired benchmark by a prespecified success criterion"
                  if strong or medium_a or medium_b or selective_positive
                  else "Not supported by the prespecified benchmark success criteria"),
    }
    parsed_features = parse_feature_analysis(output_dir / "feature_analysis.csv")
    metrics = {
        **previous,
        "exploratory_existing_fresh_1000": exploratory,
        "protocol": model["protocol"] | {"new_test_pairs": len(records), "valid_pairs": len(valid),
                                          "invalid_pairs": len(records) - len(valid),
                                          "static_applicability_bypass": True,
                                          "execution_note": "isolated 120-row 2-shard option debug output was excluded; formal scores exact-merged only from option3"},
        "methods": methods, "router_ties": ties,
        "routing_diagnostics": routing_diagnostics(predictions, choices, records),
        "method_specific_control_appendix": control_appendix,
        "calibration": {"temperature": model["temperature_metrics"],
                        "correctness_estimators": model["main"]["calibration_metrics"],
                        "test_temperature": temperature_test, "test_correctness": correctness_test},
        "selective": selective_metrics, "bootstrap": boot,
        "calibration_direction": calibration_direction, "success_assessment": success_assessment,
        "evidence_induced_harm": evidence_metrics(rows, records, model["temperatures"]),
        "static_control": static, "feature_analysis": parsed_features,
        "claims": {"clinical_safety_guarantee": False, "world_model": False},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    probability_existing = [row for row in RR.read_jsonl(output_dir / "expert_probabilities.jsonl")
                            if row.get("split") in {"dev", "calibration"}]
    RR.write_jsonl(output_dir / "expert_probabilities.jsonl", probability_existing + records)
    prediction_rows = []
    for method, values in predictions.items():
        for row in records:
            key = row["case_id"]
            prediction_rows.append({"case_id": key, "source_case_id": row["source_case_id"], "split": "new_test",
                                    "method": method, "prediction": values[key],
                                    "selected_expert": choices[method][key],
                                    "baseline_prediction": row["medrgag_prediction"],
                                    "gold_label_id": row["gold_label_id"],
                                    "status": "ok" if values[key] is not None else "invalid"})
    RR.write_jsonl(output_dir / "router_predictions.jsonl", prediction_rows)
    with (output_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = sorted({"method"} | {key for value in methods.values() for key in value})
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader(); writer.writerows({"method": name, **value} for name, value in methods.items())
    with (output_dir / "risk_coverage.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(curve[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(curve)
    (output_dir / "bootstrap.json").write_text(json.dumps(boot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "calibration_metrics.json").write_text(json.dumps(metrics["calibration"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(summary(metrics), encoding="utf-8")
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=RESULTS)
    parser.add_argument("--cache", type=Path, default=CACHE)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = evaluate(args.output_dir, args.cache)
    main = result["methods"]["risk_aware_router"]
    print(json.dumps({"accuracy": main["accuracy"], "repairs": main["repairs"], "harms": main["harms"],
                      "conditional_harm_rate": main["conditional_harm_rate"],
                      "profile_routing_coverage": main["profile_routing_coverage"]}, sort_keys=True))
