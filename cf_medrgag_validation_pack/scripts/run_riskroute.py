#!/usr/bin/env python3
"""Fit and freeze the compact RiskRoute-CF controller."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results_riskroute"
CFMOE = ROOT / "results_cfmoe"
LETTERS = "ABCD"
EXPERTS = {
    "medrgag": "medrgag",
    "profile": "profile_no_document",
    "cpg": "cpg_core",
    "cf_kads": "profile_cf_kads",
    "direct": "direct_logprob",
}
FEATURE_NAMES = (
    "mean_matched_evidence_similarity",
    "medrgag_margin",
    "medrgag_entropy",
    "profile_max_probability",
    "profile_margin",
    "profile_entropy",
    "delta_profile_magnitude",
    "medrgag_profile_agree",
    "profile_cpg_agree",
    "cpg_available",
    "medrgag_profile_js",
    "profile_kads_margin_delta",
    "kads_changes_profile_top1",
    "cf_kads_delta_coverage",
    "generated_document_ratio",
)
CPG_FEATURES = {"profile_cpg_agree", "cpg_available"}
INTERFERENCE_FEATURES = {
    "profile_kads_margin_delta",
    "kads_changes_profile_top1",
    "cf_kads_delta_coverage",
    "generated_document_ratio",
}
LAMBDA_VALUES = (0.0, 0.5, 1.0, 2.0)
SEED = 13
TEST_SELECTION_SEED = 113


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CFMOE_RUN = load_script("riskroute_cfmoe", ROOT / "scripts/run_cfmoe.py")
CF_EVAL = CFMOE_RUN.CF_EVAL
CF_RUN = CFMOE_RUN.CF_RUN
DELTA_RANK = CFMOE_RUN.DELTA_RANK


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return CF_RUN.read_jsonl(path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    CF_RUN.write_jsonl(path, rows)


def scores(row: dict[str, Any], name: str) -> dict[int, float]:
    try:
        return {int(key): float(value) for key, value in row["option_scores"][name].items()}
    except (KeyError, TypeError, ValueError):
        return {}


def finite_scores(values: dict[int, float], labels: list[int]) -> bool:
    return set(values) == set(labels) and all(math.isfinite(value) for value in values.values())


def softmax(values: dict[int, float], temperature: float = 1.0) -> dict[int, float]:
    peak = max(values.values()) / temperature
    weights = {key: math.exp(value / temperature - peak) for key, value in values.items()}
    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def argmax(values: dict[int, float]) -> int | None:
    return min(values, key=lambda key: (-values[key], key)) if values else None


def probability_summary(probabilities: dict[int, float]) -> tuple[float, float, float]:
    ordered = sorted(probabilities.values(), reverse=True)
    entropy = -sum(value * math.log(max(value, 1e-15)) for value in ordered)
    return ordered[0], ordered[0] - ordered[1], entropy


def js_divergence(left: dict[int, float], right: dict[int, float]) -> float:
    middle = {key: (left[key] + right[key]) / 2 for key in left}
    def kl(source: dict[int, float]) -> float:
        return sum(value * math.log(max(value, 1e-15) / max(middle[key], 1e-15))
                   for key, value in source.items())
    return (kl(left) + kl(right)) / 2


def calibration_metrics(probabilities: list[dict[int, float]], gold: list[int], bins: int = 10) -> dict[str, Any]:
    if not probabilities:
        return {"n": 0, "accuracy": None, "nll": None, "brier": None, "ece": None}
    predictions = [argmax(value) for value in probabilities]
    confidence = np.asarray([max(value.values()) for value in probabilities])
    correct = np.asarray([prediction == target for prediction, target in zip(predictions, gold)], dtype=float)
    nll = -float(np.mean([math.log(max(value[target], 1e-15))
                          for value, target in zip(probabilities, gold)]))
    brier = float(np.mean([sum((value[key] - float(key == target)) ** 2 for key in value)
                           for value, target in zip(probabilities, gold)]))
    ece = 0.0
    for lower in np.linspace(0, 1, bins + 1)[:-1]:
        upper = lower + 1 / bins
        mask = (confidence >= lower) & (confidence < upper if upper < 1 else confidence <= upper)
        if mask.any():
            ece += float(mask.mean()) * abs(float(correct[mask].mean()) - float(confidence[mask].mean()))
    return {"n": len(gold), "accuracy": float(correct.mean()), "nll": nll,
            "brier": brier, "ece": ece, "bins": bins}


def fit_temperature(rows: list[dict[str, Any]], expert: str) -> float:
    usable = []
    for row in rows:
        labels = row["option_label_ids"]
        raw = scores(row, expert)
        if finite_scores(raw, labels):
            usable.append((raw, row["gold_label_id"]))
    def loss(log_temperature: float) -> float:
        temperature = math.exp(log_temperature)
        return -float(np.mean([math.log(max(softmax(raw, temperature)[gold], 1e-15))
                               for raw, gold in usable]))
    result = minimize_scalar(loss, bounds=(-4.0, 4.0), method="bounded")
    if not result.success:
        raise RuntimeError(f"temperature fit failed for {expert}")
    return float(math.exp(result.x))


def temperature_report(rows: list[dict[str, Any]], expert: str, temperature: float) -> dict[str, Any]:
    raw_probabilities, calibrated, gold = [], [], []
    for row in rows:
        labels = row["option_label_ids"]
        raw = scores(row, expert)
        if finite_scores(raw, labels):
            raw_probabilities.append(softmax(raw))
            calibrated.append(softmax(raw, temperature))
            gold.append(row["gold_label_id"])
    return {"temperature": temperature, "before": calibration_metrics(raw_probabilities, gold),
            "after": calibration_metrics(calibrated, gold)}


def raw_feature_record(row: dict[str, Any], document: dict[str, Any] | None,
                       evidence_match: dict[str, Any] | None,
                       temperatures: dict[str, float]) -> dict[str, Any]:
    labels = row["option_label_ids"]
    med_raw, profile_raw = scores(row, "medrgag"), scores(row, "profile_no_document")
    valid = (row.get("status") == "ok" and row.get("baseline_label_id") in labels
             and finite_scores(med_raw, labels) and finite_scores(profile_raw, labels))
    record: dict[str, Any] = {
        "case_id": row["case_id"], "source_case_id": row["source_case_id"], "split": row["split"],
        "status": "ok" if valid else "invalid", "invalid_reason": None if valid else "missing core expert score",
        "gold_label_id": row["gold_label_id"], "control_gold_label_id": row["control_gold_label_id"],
        "medrgag_prediction": row.get("baseline_label_id"),
        "medrgag_control_prediction": row.get("baseline_control_label_id"),
        "features": {}, "diagnostics": {}, "expert_probabilities": {}, "expert_predictions": {},
        "cpg_structurally_not_applicable": bool(row.get("cpg_structurally_not_applicable")),
        "cpg_runtime_invalid": row.get("raw_expert_status") != "ok",
    }
    if not valid:
        return record
    probability: dict[str, dict[int, float]] = {}
    for short, expert in EXPERTS.items():
        raw = scores(row, expert)
        if finite_scores(raw, labels):
            probability[short] = softmax(raw, temperatures[short])
            record["expert_probabilities"][short] = {str(key): value for key, value in probability[short].items()}
            record["expert_predictions"][short] = argmax(probability[short])
    med_max, med_margin, med_entropy = probability_summary(probability["medrgag"])
    profile_max, profile_margin, profile_entropy = probability_summary(probability["profile"])
    direct_pair = scores(row, "no_medrgag_evidence")
    delta_magnitude = math.sqrt(sum((profile_raw[label] - direct_pair.get(label, profile_raw[label])) ** 2
                                    for label in labels))
    cpg_available = "cpg" in probability
    original = scores(row, "profile_original_kads")
    original_probability = (softmax(original, temperatures["profile"])
                            if finite_scores(original, labels) else probability["profile"])
    original_margin = probability_summary(original_probability)[1]
    variants = (document or {}).get("variants", {})
    candidates = (document or {}).get("candidate_documents", [])
    cf_ids = {(value.get("source"), value.get("id")) for value in variants.get("cf_kads_top3", [])}
    cf_documents = [value for value in candidates if (value.get("source"), value.get("id")) in cf_ids]
    original_documents = variants.get("original_kads_top5", [])
    similarities = [float(value["similarity"]) for value in (evidence_match or {}).get("matches", [])]
    record["features"] = {
        # No match is an observed evidence-coverage gap, represented as zero rather than a parse failure.
        "mean_matched_evidence_similarity": float(np.mean(similarities)) if similarities else 0.0,
        "medrgag_margin": med_margin,
        "medrgag_entropy": med_entropy,
        "profile_max_probability": profile_max,
        "profile_margin": profile_margin,
        "profile_entropy": profile_entropy,
        "delta_profile_magnitude": delta_magnitude,
        "medrgag_profile_agree": float(row["baseline_label_id"] == argmax(probability["profile"])),
        "profile_cpg_agree": (float(argmax(probability["profile"]) == argmax(probability["cpg"]))
                              if cpg_available else None),
        "cpg_available": float(cpg_available),
        "medrgag_profile_js": js_divergence(probability["medrgag"], probability["profile"]),
        "profile_kads_margin_delta": profile_margin - original_margin,
        "kads_changes_profile_top1": float(argmax(original_probability) != argmax(probability["profile"])),
        "cf_kads_delta_coverage": max((float(value.get("delta_coverage", 0.0))
                                        for value in cf_documents), default=0.0),
        "generated_document_ratio": (sum(value.get("source") == "generated" for value in original_documents)
                                      / len(original_documents) if original_documents else 0.0),
    }
    record["diagnostics"] = {
        "matched_evidence_similarity_max": max(similarities) if similarities else None,
        "matched_evidence_count": len(similarities),
        "medrgag_score_max_probability": med_max,
    }
    record["profile_prediction"] = record["expert_predictions"]["profile"]
    record["profile_cf_kads_prediction"] = record["expert_predictions"].get("cf_kads")
    return record


def feature_records(rows: list[dict[str, Any]], documents: dict[str, dict[str, Any]],
                    evidence_matches: dict[str, dict[str, Any]],
                    temperatures: dict[str, float], means: dict[str, float] | None = None
                    ) -> tuple[list[dict[str, Any]], dict[str, float]]:
    records = [raw_feature_record(row, documents.get(row["case_id"]), evidence_matches.get(row["case_id"]),
                                  temperatures) for row in rows]
    valid = [row for row in records if row["status"] == "ok"]
    if means is None:
        means = {name: float(np.mean([row["features"][name] for row in valid
                                     if row["features"][name] is not None])) for name in FEATURE_NAMES}
    for row in valid:
        row["features"] = {name: means[name] if row["features"][name] is None else float(row["features"][name])
                           for name in FEATURE_NAMES}
        row["medrgag_correct"] = row["medrgag_prediction"] == row["gold_label_id"]
        row["profile_correct"] = row["profile_prediction"] == row["gold_label_id"]
        row["profile_harm"] = row["medrgag_correct"] and not row["profile_correct"]
    return records, means


def matrix(records: list[dict[str, Any]], names: list[str]) -> np.ndarray:
    return np.asarray([[row["features"][name] for name in names]
                       for row in records if row["status"] == "ok"], dtype=float)


def fit_binary(x: np.ndarray, y: np.ndarray, class_weight: str | None = None) -> dict[str, Any]:
    if len(set(map(int, y))) != 2:
        raise ValueError("binary fit requires both classes")
    scaler = StandardScaler().fit(x)
    model = LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=2000,
                               class_weight=class_weight, random_state=SEED).fit(scaler.transform(x), y)
    return {"mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist(),
            "coef": model.coef_[0].tolist(), "intercept": float(model.intercept_[0])}


def predict_binary(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    standardized = (x - np.asarray(model["mean"])) / np.asarray(model["scale"])
    logits = standardized @ np.asarray(model["coef"]) + float(model["intercept"])
    return 1 / (1 + np.exp(-np.clip(logits, -40, 40)))


def fit_platt(probability: np.ndarray, y: np.ndarray) -> dict[str, float]:
    logit = np.log(np.clip(probability, 1e-8, 1 - 1e-8) / np.clip(1 - probability, 1e-8, 1))[:, None]
    model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=2000, random_state=SEED).fit(logit, y)
    return {"coef": float(model.coef_[0, 0]), "intercept": float(model.intercept_[0])}


def apply_platt(model: dict[str, float], probability: np.ndarray) -> np.ndarray:
    logit = np.log(np.clip(probability, 1e-8, 1 - 1e-8) / np.clip(1 - probability, 1e-8, 1))
    value = model["coef"] * logit + model["intercept"]
    return 1 / (1 + np.exp(-np.clip(value, -40, 40)))


def binary_metrics(probability: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    clipped = np.clip(probability, 1e-15, 1 - 1e-15)
    brier = float(np.mean((probability - y) ** 2))
    nll = -float(np.mean(y * np.log(clipped) + (1 - y) * np.log(1 - clipped)))
    ece = 0.0
    for lower in np.linspace(0, 1, 11)[:-1]:
        upper = lower + .1
        mask = (probability >= lower) & (probability < upper if upper < 1 else probability <= upper)
        if mask.any():
            ece += float(mask.mean()) * abs(float(y[mask].mean()) - float(probability[mask].mean()))
    return {"n": len(y), "auroc": float(roc_auc_score(y, probability)),
            "auprc": float(average_precision_score(y, probability)), "ece": ece,
            "brier": brier, "nll": nll}


def route_two(q_medrgag: np.ndarray, q_profile: np.ndarray, profile_harm: np.ndarray,
              records: list[dict[str, Any]], harm_lambda: float) -> tuple[list[int], list[str], int]:
    predictions, choices, ties = [], [], 0
    for index, row in enumerate(records):
        gain = q_profile[index] - q_medrgag[index] - harm_lambda * profile_harm[index]
        if math.isclose(float(gain), 0.0, abs_tol=1e-12):
            ties += 1
            med_conf = max(map(float, row["expert_probabilities"]["medrgag"].values()))
            profile_conf = max(map(float, row["expert_probabilities"]["profile"].values()))
            choose_profile = profile_conf >= med_conf
        else:
            choose_profile = gain > 0
        choices.append("profile" if choose_profile else "medrgag")
        predictions.append(row["profile_prediction"] if choose_profile else row["medrgag_prediction"])
    return predictions, choices, ties


def revision_counts(predictions: list[int], records: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = [row["medrgag_prediction"] for row in records]
    gold = [row["gold_label_id"] for row in records]
    repairs = sum(base != target and pred == target for base, pred, target in zip(baseline, predictions, gold))
    harms = sum(base == target and pred != target for base, pred, target in zip(baseline, predictions, gold))
    correct = sum(pred == target for pred, target in zip(predictions, gold))
    return {"accuracy": correct / len(records), "repairs": repairs, "harms": harms,
            "utility": (repairs - 2 * harms) / len(records)}


def fit_router(dev: list[dict[str, Any]], calibration: list[dict[str, Any]], names: list[str],
               shuffled: bool = False) -> dict[str, Any]:
    dev_valid = [row for row in dev if row["status"] == "ok"]
    cal_valid = [row for row in calibration if row["status"] == "ok"]
    x_dev, x_cal = matrix(dev, names), matrix(calibration, names)
    if shuffled:
        x_dev = x_dev[np.random.default_rng(SEED + 31).permutation(len(x_dev))]
        x_cal = x_cal[np.random.default_rng(SEED + 32).permutation(len(x_cal))]
    labels = {
        "q_medrgag": np.asarray([row["medrgag_correct"] for row in dev_valid], dtype=int),
        "q_profile": np.asarray([row["profile_correct"] for row in dev_valid], dtype=int),
        "h_profile": np.asarray([row["profile_harm"] for row in dev_valid], dtype=int),
        "q_cf_kads": np.asarray([row["profile_cf_kads_prediction"] == row["gold_label_id"]
                                 for row in dev_valid], dtype=int),
    }
    cal_labels = {
        "q_medrgag": np.asarray([row["medrgag_correct"] for row in cal_valid], dtype=int),
        "q_profile": np.asarray([row["profile_correct"] for row in cal_valid], dtype=int),
        "h_profile": np.asarray([row["profile_harm"] for row in cal_valid], dtype=int),
        "q_cf_kads": np.asarray([row["profile_cf_kads_prediction"] == row["gold_label_id"]
                                 for row in cal_valid], dtype=int),
    }
    fitted: dict[str, Any] = {"feature_names": names, "shuffled": shuffled, "models": {}, "platt": {}}
    raw_cal, calibrated = {}, {}
    for target in labels:
        fitted["models"][target] = fit_binary(x_dev, labels[target], "balanced" if target == "h_profile" else None)
        raw_cal[target] = predict_binary(fitted["models"][target], x_cal)
        fitted["platt"][target] = fit_platt(raw_cal[target], cal_labels[target])
        calibrated[target] = apply_platt(fitted["platt"][target], raw_cal[target])
    fitted["calibration_metrics"] = {
        target: {"before": binary_metrics(raw_cal[target], cal_labels[target]),
                 "after": binary_metrics(calibrated[target], cal_labels[target])}
        for target in labels
    }
    variants = []
    for harm_lambda in LAMBDA_VALUES:
        predictions, choices, ties = route_two(calibrated["q_medrgag"], calibrated["q_profile"],
                                                calibrated["h_profile"], cal_valid, harm_lambda)
        value = revision_counts(predictions, cal_valid)
        variants.append({"lambda_harm": harm_lambda, **value,
                         "profile_routing_coverage": choices.count("profile") / len(choices), "ties": ties})
    chosen = max(variants, key=lambda value: (value["utility"], value["accuracy"],
                                               value["profile_routing_coverage"]))
    fitted["lambda_variants"] = variants
    fitted["lambda_harm"] = chosen["lambda_harm"]
    fitted["calibration_operating_point"] = chosen
    return fitted


def router_probabilities(model: dict[str, Any], records: list[dict[str, Any]],
                         split_seed: int = 0) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    names = model["feature_names"]
    x = matrix(records, names)
    if model.get("shuffled"):
        x = x[np.random.default_rng(SEED + 33 + split_seed).permutation(len(x))]
    raw, calibrated = {}, {}
    for target, fitted in model["models"].items():
        raw[target] = predict_binary(fitted, x)
        calibrated[target] = apply_platt(model["platt"][target], raw[target])
    return raw, calibrated


def selective_thresholds(confidence: np.ndarray) -> dict[str, float]:
    ordered = np.sort(confidence)[::-1]
    return {str(int(coverage * 100)): float(ordered[max(0, math.ceil(coverage * len(ordered)) - 1)])
            for coverage in (.8, .9, .95)}


def exploratory_metrics(records: list[dict[str, Any]], model: dict[str, Any]) -> dict[str, Any]:
    valid = [row for row in records if row["status"] == "ok"]
    raw, calibrated = router_probabilities(model, records, split_seed=7)
    forced, _, forced_ties = route_two(calibrated["q_medrgag"], calibrated["q_profile"],
                                       np.zeros(len(valid)), valid, 0.0)
    risk, choices, risk_ties = route_two(calibrated["q_medrgag"], calibrated["q_profile"],
                                         calibrated["h_profile"], valid, model["lambda_harm"])
    profile = [row["profile_prediction"] for row in valid]
    oracle = [row["profile_prediction"] if row["profile_correct"] else row["medrgag_prediction"]
              for row in valid]
    targets = {
        "q_medrgag": np.asarray([row["medrgag_correct"] for row in valid], dtype=int),
        "q_profile": np.asarray([row["profile_correct"] for row in valid], dtype=int),
        "h_profile": np.asarray([row["profile_harm"] for row in valid], dtype=int),
        "q_cf_kads": np.asarray([row["profile_cf_kads_prediction"] == row["gold_label_id"]
                                  for row in valid], dtype=int),
    }
    correctness = {
        target: {"before": binary_metrics(raw[target], labels),
                 "after": binary_metrics(calibrated[target], labels)}
        for target, labels in targets.items()
    }
    disagreement = [row for row in valid if row["medrgag_correct"] != row["profile_correct"]]
    repair_label = np.asarray([row["profile_correct"] for row in disagreement], dtype=int)
    separability = []
    for name in model["feature_names"]:
        values = np.asarray([row["features"][name] for row in disagreement], dtype=float)
        auc = float(roc_auc_score(repair_label, values)) if values.std() else None
        separability.append({
            "feature": name,
            "repair_mean": float(np.mean([row["features"][name] for row in disagreement
                                            if row["profile_correct"]])),
            "harm_mean": float(np.mean([row["features"][name] for row in disagreement
                                          if row["medrgag_correct"]])),
            "repair_class_auroc": auc,
            "orientation_free_separability_auroc": max(auc, 1 - auc) if auc is not None else None,
        })
    coefficients = {
        target: dict(zip(model["feature_names"], model["models"][target]["coef"]))
        for target in ("q_medrgag", "q_profile", "h_profile")
    }
    return {"status": "exploratory_only_previously_observed_fresh_1000",
            "n": len(records), "valid": len(valid), "invalid": len(records) - len(valid),
            "two_expert_oracle": revision_counts(oracle, valid),
            "profile": revision_counts(profile, valid),
            "calibrated_forced_router": revision_counts(forced, valid) | {"ties": forced_ties},
            "risk_aware_router": revision_counts(risk, valid) | {
                "profile_routing_coverage": choices.count("profile") / len(choices), "ties": risk_ties},
            "correctness_calibration_on_exploratory_fresh_1000": correctness,
            "repair_vs_harm_feature_separability": separability,
            "frozen_development_model_coefficients": coefficients,
            "coefficient_note": "coefficients were fitted on development; fresh-1000 was evaluation only"}


def feature_analysis(records: list[dict[str, Any]], model: dict[str, Any], output: Path) -> None:
    valid = [row for row in records if row["status"] == "ok"]
    disagreement = [row for row in valid if row["medrgag_correct"] != row["profile_correct"]]
    target = np.asarray([row["profile_correct"] for row in disagreement], dtype=int)
    coefficients = {name: dict(zip(model["feature_names"], model["models"][name]["coef"]))
                    for name in ("q_medrgag", "q_profile", "h_profile")}
    rows = []
    for name in FEATURE_NAMES:
        values = np.asarray([row["features"][name] for row in disagreement], dtype=float)
        all_values = np.asarray([row["features"][name] for row in valid], dtype=float)
        auc = float(roc_auc_score(target, values)) if len(set(target)) == 2 and values.std() else None
        repairs = [row["features"][name] for row in disagreement if row["profile_correct"]]
        harms = [row["features"][name] for row in disagreement if row["medrgag_correct"]]
        rows.append({"feature": name, "used_by_router": True,
                     "standard_deviation": float(all_values.std()),
                     "nonmissing_standard_deviation": (float(np.std([
                         row["features"][name] for row in valid
                         if row["diagnostics"].get("matched_evidence_count", 0) > 0]))
                         if name == "mean_matched_evidence_similarity" else None),
                     "selection_note": ("included; mean similarity varies on development"
                                        if name == "mean_matched_evidence_similarity" else "predeclared routing feature"),
                     "q_medrgag_coefficient": coefficients["q_medrgag"].get(name),
                     "q_profile_coefficient": coefficients["q_profile"].get(name),
                     "harm_coefficient": coefficients["h_profile"].get(name),
                     "repair_mean": float(np.mean(repairs)) if repairs else None,
                     "harm_mean": float(np.mean(harms)) if harms else None,
                     "repair_vs_harm_auroc": max(auc, 1 - auc) if auc is not None else None})
    max_rows = [row for row in disagreement if row["diagnostics"].get("matched_evidence_similarity_max") is not None]
    all_max_values = np.asarray([row["diagnostics"]["matched_evidence_similarity_max"] for row in valid
                                 if row["diagnostics"].get("matched_evidence_similarity_max") is not None], dtype=float)
    max_target = np.asarray([row["profile_correct"] for row in max_rows], dtype=int)
    max_values = np.asarray([row["diagnostics"]["matched_evidence_similarity_max"] for row in max_rows], dtype=float)
    max_auc = (float(roc_auc_score(max_target, max_values))
               if len(set(max_target)) == 2 and max_values.std() else None)
    rows.append({"feature": "matched_evidence_similarity_max", "used_by_router": False,
                 "standard_deviation": float(all_max_values.std()),
                 "nonmissing_standard_deviation": float(all_max_values.std()),
                 "selection_note": "diagnostic only; near-constant on nonmissing development rows",
                 "q_medrgag_coefficient": None, "q_profile_coefficient": None, "harm_coefficient": None,
                 "repair_mean": float(np.mean([row["diagnostics"]["matched_evidence_similarity_max"]
                                                for row in max_rows if row["profile_correct"]])),
                 "harm_mean": float(np.mean([row["diagnostics"]["matched_evidence_similarity_max"]
                                              for row in max_rows if row["medrgag_correct"]])),
                 "repair_vs_harm_auroc": max(max_auc, 1 - max_auc) if max_auc is not None else None})
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def write_commands(output: Path) -> None:
    text = """#!/usr/bin/env bash
set -euo pipefail
PY=/home/data3/txy/MedRGAG/.venv/bin/python
MODEL=/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
OUT=results_riskroute
CACHE=results_cfmoe/cache/riskroute
TMPDIR=/home/data3/txy/.cache/riskroute_tmp
mkdir -p "$TMPDIR"
export TMPDIR

$PY scripts/run_riskroute.py smoke
$PY scripts/run_riskroute.py fit
# router_models.json is frozen before the next command reads official unseen test rows.
$PY scripts/run_riskroute.py prepare-test

pids=()
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py baseline --data "$OUT/new_test.jsonl" \
    --output-dir "$CACHE/baseline" --model "$MODEL" --shard-index "$i" --shard-count 2 \
    --gpu-memory-utilization .55 &
  pids+=("$!")
done
CUDA_VISIBLE_DEVICES=2 $PY scripts/run_cfshift.py match --data "$OUT/new_test.jsonl" \
  --evidences private_data/deltarank_sources/release_evidences.json \
  --output "$CACHE/matches.test.jsonl" --device cuda:0 &
pids+=("$!")
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfshift.py merge --inputs "$CACHE"/baseline/shard-*/baseline.jsonl \
  --output "$CACHE/baseline.test.jsonl"

CUDA_VISIBLE_DEVICES=2 $PY scripts/run_cfmoe.py documents --data "$OUT/new_test.jsonl" \
  --cache-root "$CACHE/baseline" --output "$CACHE/document_scores.test.jsonl" --device cuda:0

# Runtime note: an isolated initial 2-shard debug run wrote 120 rows under cache/riskroute/option
# and was intentionally stopped after documents completed. It is not an input to this merge.
pids=()
for i in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfshift.py score --data "$OUT/new_test.jsonl" \
    --baseline "$CACHE/baseline.test.jsonl" --output-dir "$CACHE/option3" --model "$MODEL" \
    --shard-index "$i" --shard-count 3 --gpu-memory-utilization .55 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfshift.py merge --inputs "$CACHE"/option3/shard-*/option_scores.jsonl \
  --output "$CACHE/option_scores.test.jsonl"

pids=()
for i in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$i $PY scripts/run_cfmoe.py score-experts --data "$OUT/new_test.jsonl" \
    --base-scores "$CACHE/option_scores.test.jsonl" --document-scores "$CACHE/document_scores.test.jsonl" \
    --output "$CACHE/raw_experts/shard-$i.jsonl" --model "$MODEL" \
    --shard-index "$i" --shard-count 3 --gpu-memory-utilization .55 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
$PY scripts/run_cfmoe.py merge-exact --data "$OUT/new_test.jsonl" \
  --inputs "$CACHE/raw_experts/shard-0.jsonl" "$CACHE/raw_experts/shard-1.jsonl" "$CACHE/raw_experts/shard-2.jsonl" \
  --output "$CACHE/raw_experts.test.jsonl"
$PY scripts/run_cfmoe.py assemble --data "$OUT/new_test.jsonl" \
  --baseline "$CACHE/baseline.test.jsonl" --base-scores "$CACHE/option_scores.test.jsonl" \
  --matches "$CACHE/matches.test.jsonl" --document-scores "$CACHE/document_scores.test.jsonl" \
  --raw-experts "$CACHE/raw_experts.test.jsonl" \
  --conditions private_data/deltarank_sources/release_conditions.json \
  --evidences private_data/deltarank_sources/release_evidences.json \
  --output "$CACHE/expert_scores.test.jsonl"
$PY scripts/evaluate_riskroute.py
$PY -m unittest tests.test_riskroute -v
$PY -m py_compile scripts/run_riskroute.py scripts/evaluate_riskroute.py tests/test_riskroute.py
git diff --check
"""
    output.write_text(text, encoding="utf-8")
    output.chmod(0o755)


def smoke() -> dict[str, Any]:
    available = read_jsonl(CFMOE / "cache/expert_scores.train.jsonl")
    documents = {row["pair_id"]: row for row in read_jsonl(CFMOE / "cache/document_scores.train.jsonl")}
    matches = {row["pair_id"]: row for row in read_jsonl(CFMOE / "cache/matches.full.jsonl")}
    temperatures = {short: fit_temperature(available[:20], expert) for short, expert in EXPERTS.items()}
    records = []
    for start in range(len(available) - 19):
        candidate, _ = feature_records(available[start:start + 20], documents, matches, temperatures)
        valid_candidate = [row for row in candidate if row["status"] == "ok"]
        targets = ("medrgag_correct", "profile_correct", "profile_harm")
        if len(valid_candidate) == 20 and all(len({row[target] for row in valid_candidate}) == 2
                                               for target in targets):
            records = candidate
            break
    if not records:
        raise ValueError("no 20-case development smoke window contains both correctness classes")
    valid = [row for row in records if row["status"] == "ok"]
    if len(valid) != 20 or any(not math.isfinite(value) for row in valid for value in row["features"].values()):
        raise ValueError("smoke features are incomplete")
    x = matrix(records, list(FEATURE_NAMES))
    for target in ("medrgag_correct", "profile_correct", "profile_harm"):
        y = np.asarray([row[target] for row in valid], dtype=int)
        fit_binary(x, y, "balanced" if target == "profile_harm" else None)
    prediction, choices, _ = route_two(np.full(20, .5), np.full(20, .5), np.zeros(20), valid, 0)
    if len(prediction) != 20 or len(choices) != 20 or set(choices) == {"medrgag"}:
        raise ValueError("forced-choice smoke failed")
    source = available[0]
    invalid = raw_feature_record({**source, "baseline_label_id": None}, documents[source["case_id"]],
                                 matches[source["case_id"]], temperatures)
    if invalid["status"] != "invalid" or invalid["medrgag_prediction"] is not None:
        raise ValueError("invalid sample was silently converted to MedRGAG")
    return {"pairs": 20, "valid": 20, "features": len(FEATURE_NAMES),
            "experts": list(EXPERTS), "forced_choice_predictions": len(prediction),
            "invalid_policy": "marked_invalid_without_fallback"}


def fit(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    train_rows = read_jsonl(CFMOE / "cache/expert_scores.train.jsonl")
    documents = {row["pair_id"]: row for row in read_jsonl(CFMOE / "cache/document_scores.train.jsonl")}
    matches = {row["pair_id"]: row for row in read_jsonl(CFMOE / "cache/matches.full.jsonl")}
    dev_rows = [row for row in train_rows if row["split"] == "dev"]
    cal_rows = [row for row in train_rows if row["split"] == "calibration"]
    temperatures = {short: fit_temperature(dev_rows, expert) for short, expert in EXPERTS.items()}
    dev, means = feature_records(dev_rows, documents, matches, temperatures)
    calibration, _ = feature_records(cal_rows, documents, matches, temperatures, means)
    main = fit_router(dev, calibration, list(FEATURE_NAMES))
    ablations = {
        "without_cpg_features": fit_router(dev, calibration,
            [name for name in FEATURE_NAMES if name not in CPG_FEATURES]),
        "without_interference_features": fit_router(dev, calibration,
            [name for name in FEATURE_NAMES if name not in INTERFERENCE_FEATURES]),
        "shuffled_features": fit_router(dev, calibration, list(FEATURE_NAMES), shuffled=True),
    }
    cal_valid = [row for row in calibration if row["status"] == "ok"]
    _, cal_probability = router_probabilities(main, calibration)
    thresholds = selective_thresholds(np.maximum(cal_probability["q_medrgag"], cal_probability["q_profile"]))
    temperature_metrics = {
        split: {short: temperature_report(rows, expert, temperatures[short])
                for short, expert in EXPERTS.items()}
        for split, rows in (("development", dev_rows), ("calibration", cal_rows))
    }
    model = {
        "status": "frozen_before_new_test_access",
        "method": "RiskRoute-CF",
        "protocol": {
            "development_pairs": len(dev_rows), "calibration_pairs": len(cal_rows),
            "feature_selection": "predeclared_from_prompt_without_exploratory_test_selection",
            "medrgag_output": "baseline_label_id_from_medrgag_mcq_proxy_reader",
            "medrgag_scores": "reliability_features_only",
            "profile_output": "argmax_profile_no_document",
            "control_prediction": "unchanged_medrgag_control_prediction",
            "forced_choice": True, "invalid_policy": "mark_invalid_without_fallback",
            "tie_break": "higher_calibrated_option_confidence_then_profile_on_exact_confidence_tie",
            "test_selection_seed": TEST_SELECTION_SEED,
            "lambda_candidates": list(LAMBDA_VALUES), "bootstrap_samples": 1000,
        },
        "feature_names": list(FEATURE_NAMES), "feature_means": means,
        "temperatures": temperatures, "temperature_metrics": temperature_metrics,
        "main": main, "ablations": ablations,
        "selective": {"confidence": "max(q_medrgag,q_profile)",
                      "thresholds_from_calibration": thresholds,
                      "target_coverages": [0.8, 0.9, 0.95]},
    }
    (output_dir / "router_models.json").write_text(json.dumps(model, indent=2, sort_keys=True) + "\n",
                                                    encoding="utf-8")
    write_jsonl(output_dir / "dev_features.jsonl", dev)
    write_jsonl(output_dir / "calibration_features.jsonl", calibration)
    write_jsonl(output_dir / "expert_probabilities.jsonl", dev + calibration)
    feature_analysis(dev, main, output_dir / "feature_analysis.csv")
    write_commands(output_dir / "commands.sh")

    # The previously viewed fresh-1000 is evaluated only after every fitted choice above is frozen.
    full_rows = read_jsonl(CFMOE / "expert_scores.jsonl")
    fresh_rows = [row for row in full_rows if row["split"] == "fresh_test"]
    fresh_documents = {row["pair_id"]: row for row in read_jsonl(CFMOE / "document_scores.jsonl")
                       if row["split"] == "fresh_test"}
    exploratory, _ = feature_records(fresh_rows, fresh_documents, matches, temperatures, means)
    exploration = exploratory_metrics(exploratory, main)
    initial_metrics = {"exploratory_existing_fresh_1000": exploration,
                       "calibration": {"temperature": temperature_metrics,
                                       "correctness_estimators": main["calibration_metrics"]}}
    (output_dir / "metrics.json").write_text(json.dumps(initial_metrics, indent=2, sort_keys=True) + "\n",
                                              encoding="utf-8")
    return {"status": model["status"], "development": len(dev), "calibration": len(calibration),
            "features": len(FEATURE_NAMES), "lambda_harm": main["lambda_harm"],
            "selective_thresholds": thresholds, "exploratory": exploration}


def prepare_test(output_dir: Path, count: int = 1000) -> dict[str, Any]:
    model_path = output_dir / "router_models.json"
    if not model_path.exists() or json.loads(model_path.read_text(encoding="utf-8"))["status"] != "frozen_before_new_test_access":
        raise ValueError("freeze router_models.json before selecting the new test")
    raw_path = (ROOT / "private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/"
                "354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl")
    conditions = json.loads((ROOT / "private_data/deltarank_sources/release_conditions.json").read_text(encoding="utf-8"))
    label_ids = {name: index for index, name in enumerate(sorted(conditions))}
    profiles = {name: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    excluded_paths = (ROOT / "results_deltarank/test.jsonl", ROOT / "results_cfshift/fresh_test.jsonl",
                      ROOT / "results_cfmoe/fresh_test.jsonl")
    excluded = {row["source_case_id"] for path in excluded_paths for row in read_jsonl(path)}
    excluded |= {row["source_case_id"] for path in (CFMOE / "dev.jsonl", CFMOE / "calibration.jsonl")
                for row in read_jsonl(path)}
    complete = DELTA_RANK.paired_rows(raw_path)
    remaining = [row for row in complete if str(row["case_id"]) not in excluded]
    random.Random(TEST_SELECTION_SEED).shuffle(remaining)
    selected = remaining[:count]
    if len(selected) != count:
        raise ValueError(f"only {len(selected)} unseen complete official test pairs")
    rows = [CF_RUN.adapt_pair(row, "new_test", SEED, conditions, profiles, label_ids, DELTA_RANK)
            for row in selected]
    for index, row in enumerate(rows):
        row["shuffle_source_pair_id"] = rows[(index + 1) % len(rows)]["pair_id"]
    if excluded & {row["source_case_id"] for row in rows}:
        raise ValueError("new test overlaps an observed source_case_id")
    write_jsonl(output_dir / "new_test.jsonl", rows)
    return {"official_complete_test_pairs": len(complete), "excluded_source_case_ids": len(excluded),
            "remaining_before_selection": len(remaining), "new_test": len(rows),
            "sampling": "seeded_shuffle_without_label_conditioning", "seed": TEST_SELECTION_SEED}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("smoke")
    fit_parser = sub.add_parser("fit"); fit_parser.add_argument("--output-dir", type=Path, default=RESULTS)
    test = sub.add_parser("prepare-test"); test.add_argument("--output-dir", type=Path, default=RESULTS)
    test.add_argument("--pairs", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = smoke() if args.command == "smoke" else (
        fit(args.output_dir) if args.command == "fit" else prepare_test(args.output_dir, args.pairs))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
