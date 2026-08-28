#!/usr/bin/env python3
"""Calibrate and evaluate CFShift-MedRGAG."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable


PROFILE_WEIGHTS = (0.5, 1.0, 2.0)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def argmax(values: dict[int, float]) -> int | None:
    return min(values, key=lambda key: (-values[key], key)) if values else None


def softmax(values: dict[int, float]) -> dict[int, float]:
    peak = max(values.values())
    weights = {key: math.exp(value - peak) for key, value in values.items()}
    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def revision_metrics(final: dict[str, int | None], baseline: dict[str, int | None],
                     truth: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ids = sorted(truth); n = len(ids)
    base_correct = sum(baseline.get(key) == truth[key]["trap"]["label_id"] for key in ids)
    final_correct = sum(final.get(key) == truth[key]["trap"]["label_id"] for key in ids)
    repairs = sum(baseline.get(key) != truth[key]["trap"]["label_id"]
                  and final.get(key) == truth[key]["trap"]["label_id"] for key in ids)
    harms = sum(baseline.get(key) == truth[key]["trap"]["label_id"]
                and final.get(key) != truth[key]["trap"]["label_id"] for key in ids)
    changes = sum(final.get(key) is not None and final.get(key) != baseline.get(key) for key in ids)
    result = {
        "n": n, "accuracy": ratio(final_correct, n), "baseline_accuracy": ratio(base_correct, n),
        "baseline_correct": base_correct, "baseline_wrong": n - base_correct, "final_correct": final_correct,
        "repairs": repairs, "harms": harms, "repair_rate": ratio(repairs, n - base_correct),
        "introduced_error_rate": ratio(harms, n), "conditional_harm_rate": ratio(harms, base_correct),
        "original_correct_preservation": ratio(base_correct - harms, base_correct),
        "net_correction": ratio(repairs - harms, n), "answer_change_coverage": ratio(changes, n),
        "beneficial_revision_precision": ratio(repairs, changes),
        "invalid_count": sum(final.get(key) is None for key in ids),
    }
    assert math.isclose(result["net_correction"], result["accuracy"] - result["baseline_accuracy"], abs_tol=1e-12)
    if result["conditional_harm_rate"] is not None:
        assert math.isclose(result["conditional_harm_rate"],
                            1 - result["original_correct_preservation"], abs_tol=1e-12)
    assert repairs - harms == final_correct - base_correct
    return result


def pair_metrics(control: dict[str, int | None], trap: dict[str, int | None],
                 truth: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ids = sorted(truth); n = len(ids)
    control_correct = sum(control.get(key) == truth[key]["control"]["label_id"] for key in ids)
    trap_correct = sum(trap.get(key) == truth[key]["trap"]["label_id"] for key in ids)
    both = sum(control.get(key) == truth[key]["control"]["label_id"]
               and trap.get(key) == truth[key]["trap"]["label_id"] for key in ids)
    bias = sum(control.get(key) == truth[key]["control"]["label_id"]
               and trap.get(key) == truth[key]["control"]["label_id"] for key in ids)
    persistence = sum(control.get(key) is not None and trap.get(key) == control.get(key) for key in ids)
    flips = sum(trap.get(key) == truth[key]["trap"]["label_id"]
                and trap.get(key) != truth[key]["control"]["label_id"] for key in ids)
    return {"control_accuracy": ratio(control_correct, n), "trap_accuracy": ratio(trap_correct, n),
            "both_correct_pair_accuracy": ratio(both, n), "bias_trap_rate": ratio(bias, control_correct),
            "bias_trap_numerator": bias, "bias_trap_denominator": control_correct,
            "old_answer_persistence": ratio(persistence, n), "correct_flip_rate": ratio(flips, n),
            "control_invalid_count": sum(control.get(key) is None for key in ids),
            "trap_invalid_count": sum(trap.get(key) is None for key in ids)}


def as_scores(row: dict[str, Any], name: str) -> dict[int, float]:
    if row["status"] != "ok" or name not in row["scores"]:
        return {}
    return {int(key): float(value) for key, value in row["scores"][name]["log_scores"].items()}


def zscore(values: dict[int, float]) -> dict[int, float]:
    mean = sum(values.values()) / len(values)
    variance = sum((value - mean) ** 2 for value in values.values()) / len(values)
    scale = math.sqrt(variance)
    return {key: (value - mean) / scale if scale else 0.0 for key, value in values.items()}


def raw_profile(options: list[int], matches: list[dict[str, Any]], profiles: dict[int, set[str]],
                assignment: dict[int, int] | None = None) -> dict[int, float]:
    signs = {"added": 1, "new_value": 1, "removed": -1, "old_value": -1}
    return {label: sum(signs[value["operation"]] * float(value["similarity"])
                       for value in matches if value["matched_evidence_id"] in profiles[(assignment or {}).get(label, label)])
            for label in options}


def relative_scores(target: dict[int, float], control: dict[int, float], baseline: int,
                    profile: dict[int, float] | None = None, weight: float = 1.0) -> dict[int, float]:
    return {label: (target[label] - target[baseline])
            + ((target[label] - target[baseline]) - (control[label] - control[baseline]))
            + weight * (profile or {}).get(label, 0.0) for label in target}


def target_scores(target: dict[int, float], baseline: int) -> dict[int, float]:
    return {label: value - target[baseline] for label, value in target.items()}


def components(pairs: list[dict[str, Any]], baseline_rows: list[dict[str, Any]],
               score_rows: list[dict[str, Any]], match_rows: list[dict[str, Any]],
               conditions: dict[str, Any], weight: float) -> dict[str, dict[str, Any]]:
    pair_map = {row["pair_id"]: row for row in pairs}
    baseline = {row["pair_id"]: row for row in baseline_rows if row["pair_id"] in pair_map}
    scores = {row["pair_id"]: row for row in score_rows if row["pair_id"] in pair_map}
    matches = {row["pair_id"]: row for row in match_rows if row["pair_id"] in pair_map}
    name_to_id = {name: index for index, name in enumerate(sorted(conditions))}
    profiles = {name_to_id[name]: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    if set(pair_map) != set(baseline) or set(pair_map) != set(scores) or set(pair_map) != set(matches):
        raise ValueError("pair coverage differs across CFShift artifacts")
    result = {}
    for pair_id, pair in pair_map.items():
        base = baseline[pair_id]
        base_label = base["trap"]["predictions"]["medrgag_mcq_proxy"]["label_id"]
        direct_t, direct_c = as_scores(scores[pair_id], "direct_target_scores"), as_scores(scores[pair_id], "direct_control_scores")
        target, control = as_scores(scores[pair_id], "medrgag_target_scores"), as_scores(scores[pair_id], "medrgag_control_scores")
        pair_prompt = as_scores(scores[pair_id], "pair_prompt_scores")
        shuffled_control = as_scores(scores[pair_id], "shuffled_control_scores")
        options = [value["label_id"] for value in pair["views"]["four_way"].values()]
        valid = base_label is not None and all(set(values) == set(options)
                                              for values in (direct_t, direct_c, target, control, pair_prompt, shuffled_control))
        if not valid:
            result[pair_id] = {"status": "invalid", "baseline": base_label, "methods": {}}
            continue
        real = zscore(raw_profile(options, matches[pair_id]["matches"], profiles))
        donor_id = pair["shuffle_source_pair_id"]
        donor = zscore(raw_profile(options, matches[donor_id]["matches"], profiles))
        rotated = {label: options[(index + 1) % len(options)] for index, label in enumerate(options)}
        shuffled_profile = zscore(raw_profile(options, matches[pair_id]["matches"], profiles, rotated))
        target_only = target_scores(target, base_label)
        cf = relative_scores(target, control, base_label)
        cf_profile = relative_scores(target, control, base_label, real, weight)
        method_scores = {
            "direct_target_logprob": direct_t,
            "pair_prompt": pair_prompt,
            "target_margin_ranker": target_only,
            "cf_shift_ranker": cf,
            "cf_shift_profile_ranker": cf_profile,
            "cf_shift_profile_shuffled_control": relative_scores(target, shuffled_control, base_label, real, weight),
            "cf_shift_profile_shuffled_delta": relative_scores(target, control, base_label, donor, weight),
            "cf_shift_profile_shuffled_profile": relative_scores(target, control, base_label, shuffled_profile, weight),
            "no_medrgag_evidence": relative_scores(direct_t, direct_c, base_label),
            "no_cf_shift": target_only,
        }
        gold_anchor = pair["control"]["label_id"]
        method_scores["gold_control_anchor_diagnostic"] = relative_scores(target, control, gold_anchor, real, weight)
        result[pair_id] = {
            "status": "ok", "baseline": base_label, "direct_control": argmax(direct_c),
            "medrgag_control": argmax(control), "methods": method_scores,
            "profile_shift": real,
            "probability_metrics": {
                "target_gold_margin": target[pair["trap"]["label_id"]] - target[base_label],
                "target_control_margin": target[pair["control"]["label_id"]] - target[base_label],
                "gold_cf_shift": (target[pair["trap"]["label_id"]] - target[base_label])
                                 - (control[pair["trap"]["label_id"]] - control[base_label]),
                "control_cf_shift": (target[pair["control"]["label_id"]] - target[base_label])
                                    - (control[pair["control"]["label_id"]] - control[base_label]),
                "target_nll": -target[pair["trap"]["label_id"]],
            },
        }
    return result


def predicted(component: dict[str, dict[str, Any]], method: str) -> dict[str, int | None]:
    return {key: argmax(value["methods"].get(method, {})) if value["status"] == "ok" else None
            for key, value in component.items()}


def margins(component: dict[str, dict[str, Any]], method: str) -> dict[str, float | None]:
    result = {}
    for key, value in component.items():
        if value["status"] != "ok" or method not in value["methods"]:
            result[key] = None; continue
        scores, baseline = value["methods"][method], value["baseline"]
        alternative = min((label for label in scores if label != baseline),
                          key=lambda label: (-scores[label], label))
        result[key] = scores[alternative] - scores[baseline]
    return result


def residual(component: dict[str, dict[str, Any]], method: str, threshold: float) -> dict[str, int | None]:
    result = {}
    for key, value in component.items():
        if value["status"] != "ok":
            result[key] = None; continue
        scores, baseline = value["methods"][method], value["baseline"]
        alternative = min((label for label in scores if label != baseline),
                          key=lambda label: (-scores[label], label))
        result[key] = alternative if scores[alternative] - scores[baseline] >= threshold else baseline
    return result


def truth_by_split(pairs: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    return {split: {row["pair_id"]: row for row in pairs if row["split"] == split}
            for split in sorted({row["split"] for row in pairs})}


def generated_predictions(baseline_rows: list[dict[str, Any]], method: str, member: str) -> dict[str, int | None]:
    return {row["pair_id"]: row[member]["predictions"][method]["label_id"] for row in baseline_rows}


def calibrate(pairs: list[dict[str, Any]], baseline_rows: list[dict[str, Any]], score_rows: list[dict[str, Any]],
              match_rows: list[dict[str, Any]], conditions: dict[str, Any], output: Path) -> dict[str, Any]:
    split_truth = truth_by_split(pairs)
    if set(split_truth) != {"calibration", "dev"}:
        raise ValueError("calibration requires only dev and calibration rows")
    baseline_all = generated_predictions(baseline_rows, "medrgag_mcq_proxy", "trap")
    weight_results = []
    for weight in PROFILE_WEIGHTS:
        values = components(pairs, baseline_rows, score_rows, match_rows, conditions, weight)
        truth = split_truth["dev"]
        final = {key: predicted(values, "cf_shift_profile_ranker")[key] for key in truth}
        base = {key: baseline_all[key] for key in truth}
        weight_results.append({"weight": weight, **revision_metrics(final, base, truth)})
    chosen_weight = max(weight_results, key=lambda row: (row["accuracy"], -abs(row["weight"] - 1)))["weight"]
    values = components(pairs, baseline_rows, score_rows, match_rows, conditions, chosen_weight)
    config: dict[str, Any] = {"profile_weight": chosen_weight, "development_weight_analysis": weight_results,
                              "thresholds": {}, "calibration": {}}
    baseline_cal = {key: baseline_all[key] for key in split_truth["calibration"]}
    for source, residual_name in (("cf_shift_ranker", "cf_shift_residual"),
                                  ("cf_shift_profile_ranker", "cf_shift_profile_residual")):
        observed = [value for key, value in margins(values, source).items()
                    if key in split_truth["dev"] and value is not None]
        thresholds = sorted(set(observed))
        if thresholds:
            thresholds = [thresholds[0] - 1e-9, *thresholds, thresholds[-1] + 1e-9]
        development_curve, curve = [], []
        for threshold in thresholds:
            final_all = residual(values, source, threshold)
            development_final = {key: final_all[key] for key in split_truth["dev"]}
            development_base = {key: baseline_all[key] for key in split_truth["dev"]}
            development_curve.append({"threshold": threshold,
                                      **revision_metrics(development_final, development_base,
                                                         split_truth["dev"])})
            final = {key: final_all[key] for key in split_truth["calibration"]}
            curve.append({"threshold": threshold,
                          **revision_metrics(final, baseline_cal, split_truth["calibration"])})
        positive = [row for row in curve if row["net_correction"] > 0]
        selected = max(positive, key=lambda row: (
            row["net_correction"], -1 if row["beneficial_revision_precision"] is None
            else row["beneficial_revision_precision"], row["answer_change_coverage"])) if positive else None
        config["thresholds"][residual_name] = selected["threshold"] if selected else None
        config["calibration"][residual_name] = {"selected": selected, "curve": curve,
                                                "development_curve": development_curve,
                                                "status": "selected" if selected else "no useful residual operating point"}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return config


def bootstrap_difference(ids: list[str], left: dict[str, float], right: dict[str, float],
                         samples: int = 1000, seed: int = 13) -> dict[str, float]:
    rng = random.Random(seed); values = []
    for _ in range(samples):
        draw = [ids[rng.randrange(len(ids))] for _ in ids]
        values.append(sum(left[key] - right[key] for key in draw) / len(draw))
    values.sort()
    return {"difference": sum(left[key] - right[key] for key in ids) / len(ids),
            "ci_low": values[int(.025 * samples)], "ci_high": values[int(.975 * samples) - 1],
            "samples": samples}


def evaluate(pairs: list[dict[str, Any]], baseline_rows: list[dict[str, Any]], score_rows: list[dict[str, Any]],
             match_rows: list[dict[str, Any]], conditions: dict[str, Any], config: dict[str, Any],
             audit: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    splits = truth_by_split(pairs)
    values = components(pairs, baseline_rows, score_rows, match_rows, conditions, config["profile_weight"])
    baseline_trap = generated_predictions(baseline_rows, "medrgag_mcq_proxy", "trap")
    baseline_control = generated_predictions(baseline_rows, "medrgag_mcq_proxy", "control")
    direct_trap = generated_predictions(baseline_rows, "direct_mcq", "trap")
    direct_control = generated_predictions(baseline_rows, "direct_mcq", "control")
    main_sources = (
        "direct_target_logprob", "pair_prompt", "target_margin_ranker", "cf_shift_ranker",
        "cf_shift_profile_ranker", "cf_shift_profile_shuffled_control",
        "cf_shift_profile_shuffled_delta", "cf_shift_profile_shuffled_profile",
        "no_medrgag_evidence", "no_cf_shift", "gold_control_anchor_diagnostic",
    )
    method_predictions = {method: predicted(values, method) for method in main_sources}
    method_predictions.update({"direct_mcq": direct_trap, "medrgag_mcq_proxy": baseline_trap,
                               "cf_shift_always_apply": method_predictions["cf_shift_ranker"],
                               "cf_shift_profile_always_apply": method_predictions["cf_shift_profile_ranker"]})
    for source, name in (("cf_shift_ranker", "cf_shift_residual"),
                         ("cf_shift_profile_ranker", "cf_shift_profile_residual")):
        threshold = config["thresholds"][name]
        method_predictions[name] = (residual(values, source, threshold) if threshold is not None
                                    else {key: None for key in values})

    metrics_rows, prediction_rows = [], []
    similarities = sorted(value["similarity"] for row in match_rows for value in row["matches"])
    permutation_differences = sorted(
        abs(value["permutations"]["forward"][label] - value["permutations"]["reverse"][label])
        for row in score_rows if row["status"] == "ok" for value in row["scores"].values()
        for label in value["permutations"]["forward"])
    pair_map = {row["pair_id"]: row for row in pairs}
    names = sorted(conditions)
    profile_ids = {index: set(conditions[name].get("symptoms", {})) |
                          set(conditions[name].get("antecedents", {})) for index, name in enumerate(names)}
    covered_matches = sum(
        any(value["matched_evidence_id"] in profile_ids[option["label_id"]]
            for option in pair_map[row["pair_id"]]["views"]["four_way"].values())
        for row in match_rows if row["pair_id"] in pair_map for value in row["matches"])
    metrics: dict[str, Any] = {"profile_weight": config["profile_weight"], "thresholds": config["thresholds"],
                               "calibration": config["calibration"], "existing_candidate_audit": audit,
                               "methods": {}, "mechanism_bootstrap": {},
                               "data_diagnostics": {
                                   "pairs": len(pairs),
                                   "medrgag_selected_document_empty_items":
                                       sum(not row[member]["selected_documents"] for row in baseline_rows
                                           if row["pair_id"] in pair_map for member in ("control", "trap")),
                                   "models": sorted({row.get("model") for row in score_rows if row.get("model")}),
                                   "vllm_versions": sorted({row.get("vllm_version") for row in score_rows
                                                            if row.get("vllm_version")}),
                                   "scoring_implementations": sorted({row.get("scoring_implementation")
                                                                       for row in score_rows
                                                                       if row.get("scoring_implementation")}),
                                   "zero_structured_delta": sum(not (row["delta"]["added_findings"]
                                                                     or row["delta"]["removed_findings"]
                                                                     or row["delta"]["changed_findings"])
                                                                for row in pairs),
                                   "evidence_matches": len(similarities),
                                   "evidence_match_current_option_profile_coverage":
                                       ratio(covered_matches, len(similarities)),
                                   "match_similarity_mean": sum(similarities) / len(similarities),
                                   "match_similarity_p10": similarities[len(similarities) // 10],
                                   "match_similarity_median": similarities[len(similarities) // 2],
                                   "match_similarity_p90": similarities[9 * len(similarities) // 10],
                                   "option_score_invalid": sum(row["status"] != "ok" for row in score_rows),
                                   "permutation_absolute_logscore_difference_mean":
                                       sum(permutation_differences) / len(permutation_differences),
                                   "permutation_absolute_logscore_difference_median":
                                       permutation_differences[len(permutation_differences) // 2],
                               }}
    for split, truth in splits.items():
        ids = sorted(truth); base = {key: baseline_trap[key] for key in ids}
        metrics["methods"][split] = {}
        for method, all_final in method_predictions.items():
            final = {key: all_final[key] for key in ids}
            if method == "direct_mcq":
                control = {key: direct_control[key] for key in ids}
            elif method in {"medrgag_mcq_proxy", "cf_shift_residual", "cf_shift_profile_residual"}:
                control = {key: baseline_control[key] for key in ids}
            elif method in {"direct_target_logprob", "pair_prompt", "no_medrgag_evidence"}:
                control = {key: values[key]["direct_control"] if values[key]["status"] == "ok" else None for key in ids}
            else:
                control = {key: values[key]["medrgag_control"] if values[key]["status"] == "ok" else None for key in ids}
            row = {"split": split, "method": method, **revision_metrics(final, base, truth),
                   **pair_metrics(control, final, truth)}
            metrics_rows.append(row); metrics["methods"][split][method] = row
            for key in ids:
                prediction_rows.append({"pair_id": key, "split": split, "method": method,
                                        "control_prediction": control[key], "trap_prediction": final[key],
                                        "baseline_prediction": base[key],
                                        "status": "ok" if final[key] is not None else
                                        ("no_useful_calibration_point" if method.endswith("residual") and
                                         config["thresholds"][method] is None else "invalid")})
        probability = [values[key]["probability_metrics"] for key in ids if values[key]["status"] == "ok"]
        metrics["methods"][split]["probability_metrics"] = {
            "mean_target_margin_gold_trap": sum(row["target_gold_margin"] for row in probability) / len(probability),
            "mean_target_margin_control_diagnosis": sum(row["target_control_margin"] for row in probability) / len(probability),
            "mean_cf_shift_gold_trap": sum(row["gold_cf_shift"] for row in probability) / len(probability),
            "mean_cf_shift_control_diagnosis": sum(row["control_cf_shift"] for row in probability) / len(probability),
            "fraction_gold_shift_gt_control_shift": sum(row["gold_cf_shift"] > row["control_cf_shift"] for row in probability) / len(probability),
            "target_nll": sum(row["target_nll"] for row in probability) / len(probability),
        }
        if split == "fresh_test":
            comparisons = (("cf_shift_profile_ranker", "cf_shift_profile_shuffled_control"),
                           ("cf_shift_profile_ranker", "cf_shift_profile_shuffled_delta"),
                           ("cf_shift_profile_ranker", "cf_shift_profile_shuffled_profile"),
                           ("cf_shift_ranker", "target_margin_ranker"))
            for left, right in comparisons:
                left_values = {key: float(method_predictions[left][key] == truth[key]["trap"]["label_id"]) for key in ids}
                right_values = {key: float(method_predictions[right][key] == truth[key]["trap"]["label_id"]) for key in ids}
                metrics["mechanism_bootstrap"][f"{left}_minus_{right}_accuracy"] = bootstrap_difference(ids, left_values, right_values)
                left_pair = {key: float(values[key]["medrgag_control"] == truth[key]["control"]["label_id"]
                                             and method_predictions[left][key] == truth[key]["trap"]["label_id"])
                             for key in ids}
                right_pair = {key: float(values[key]["medrgag_control"] == truth[key]["control"]["label_id"]
                                              and method_predictions[right][key] == truth[key]["trap"]["label_id"])
                              for key in ids}
                metrics["mechanism_bootstrap"][f"{left}_minus_{right}_pair_accuracy"] = bootstrap_difference(
                    ids, left_pair, right_pair)
                left_flip = {key: float(method_predictions[left][key] == truth[key]["trap"]["label_id"]
                                             and method_predictions[left][key] != truth[key]["control"]["label_id"])
                             for key in ids}
                right_flip = {key: float(method_predictions[right][key] == truth[key]["trap"]["label_id"]
                                              and method_predictions[right][key] != truth[key]["control"]["label_id"])
                              for key in ids}
                metrics["mechanism_bootstrap"][f"{left}_minus_{right}_correct_flip"] = bootstrap_difference(
                    ids, left_flip, right_flip)
                valid_ids = [key for key in ids if values[key]["status"] == "ok"]
                left_shift = {key: values[key]["methods"][left][truth[key]["trap"]["label_id"]]
                                   - values[key]["methods"][left][values[key]["baseline"]] for key in valid_ids}
                right_shift = {key: values[key]["methods"][right][truth[key]["trap"]["label_id"]]
                                    - values[key]["methods"][right][values[key]["baseline"]] for key in valid_ids}
                metrics["mechanism_bootstrap"][f"{left}_minus_{right}_mean_gold_shift"] = bootstrap_difference(
                    valid_ids, left_shift, right_shift)
            for method in ("cf_shift_residual", "cf_shift_profile_residual",
                           "cf_shift_profile_ranker", "no_medrgag_evidence"):
                method_values = {
                    key: float(method_predictions[method][key] == truth[key]["trap"]["label_id"])
                    for key in ids
                }
                baseline_values = {
                    key: float(baseline_trap[key] == truth[key]["trap"]["label_id"])
                    for key in ids
                }
                difference = bootstrap_difference(ids, method_values, baseline_values)
                metrics["mechanism_bootstrap"][
                    f"{method}_minus_medrgag_mcq_proxy_accuracy"
                ] = difference
                # With a common baseline, the accuracy difference and net correction are identical.
                metrics["mechanism_bootstrap"][
                    f"{method}_minus_medrgag_mcq_proxy_net_correction"
                ] = difference

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "predictions.jsonl", prediction_rows)
    fields = sorted({key for row in metrics_rows for key in row})
    with (output_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n"); writer.writeheader(); writer.writerows(metrics_rows)
    tradeoff = []
    for name, value in config["calibration"].items():
        for split, curve in (("development", value["development_curve"]),
                             ("calibration", value["curve"])):
            for row in curve:
                tradeoff.append({"method": name, "split": split,
                                 "selected": split == "calibration" and
                                 config["thresholds"][name] == row["threshold"], **row})
    if tradeoff:
        fields = sorted({key for row in tradeoff for key in row})
        with (output_dir / "tradeoff.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fields, lineterminator="\n"); writer.writeheader(); writer.writerows(tradeoff)
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(summary(metrics, len(read_jsonl(output_dir / "dev.jsonl")),
                                                       len(read_jsonl(output_dir / "calibration.jsonl")),
                                                       len(read_jsonl(output_dir / "fresh_test.jsonl"))), encoding="utf-8")
    return metrics


def pct(value: Any) -> str:
    return "NA" if value is None else f"{100 * value:.2f}%"


def summary(metrics: dict[str, Any], dev_n: int, calibration_n: int, test_n: int) -> str:
    fresh = metrics["methods"]["fresh_test"]
    methods = ("direct_mcq", "medrgag_mcq_proxy", "direct_target_logprob", "pair_prompt",
               "target_margin_ranker", "cf_shift_ranker", "cf_shift_profile_ranker",
               "cf_shift_profile_shuffled_control", "cf_shift_profile_shuffled_delta",
               "cf_shift_profile_shuffled_profile", "no_medrgag_evidence", "no_cf_shift",
               "cf_shift_residual", "cf_shift_profile_residual")
    lines = [
        "# CFShift-MedRGAG results", "", "CFShift is counterfactual preference-shift reranking, not a world model.", "",
        f"Data: {dev_n} official train/reference development pairs, {calibration_n} separate calibration pairs, "
        f"and {test_n} fresh official test pairs. The fresh set excludes all 300 inspected DeltaRank test cases.", "",
        "## Main fresh-test table", "",
        "| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Conditional harm | Net | Change coverage | Invalid |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in methods:
        row = fresh[method]
        if method.endswith("_residual") and metrics["thresholds"][method] is None:
            lines.append(f"| {method} | NA | NA | NA | NA | NA | NA | NA | NA | {row['invalid_count']} |")
            continue
        lines.append(f"| {method} | {pct(row['accuracy'])} | {pct(row['both_correct_pair_accuracy'])} | "
                     f"{pct(row['bias_trap_rate'])} | {row['repairs']} | {row['harms']} | "
                     f"{pct(row['conditional_harm_rate'])} | {pct(row['net_correction'])} | "
                     f"{pct(row['answer_change_coverage'])} | {row['invalid_count']} |")
    profile = fresh["cf_shift_profile_ranker"]; cf = fresh["cf_shift_ranker"]; target = fresh["target_margin_ranker"]
    shuffled_control = fresh["cf_shift_profile_shuffled_control"]
    shuffled_delta = fresh["cf_shift_profile_shuffled_delta"]
    shuffled_profile = fresh["cf_shift_profile_shuffled_profile"]
    no_evidence = fresh["no_medrgag_evidence"]
    cf_residual = fresh["cf_shift_residual"]
    profile_residual = fresh["cf_shift_profile_residual"]
    selected_cf = metrics["thresholds"]["cf_shift_residual"]
    selected = metrics["thresholds"]["cf_shift_profile_residual"]
    selected_cf_calibration = metrics["calibration"]["cf_shift_residual"]["selected"]
    selected_calibration = metrics["calibration"]["cf_shift_profile_residual"]["selected"]
    split_methods = metrics["methods"]
    positive_shift = all(
        split_methods[split]["cf_shift_ranker"]["accuracy"]
        > split_methods[split]["target_margin_ranker"]["accuracy"]
        and split_methods[split]["cf_shift_profile_ranker"]["accuracy"]
        > split_methods[split]["cf_shift_profile_shuffled_control"]["accuracy"]
        and split_methods[split]["cf_shift_profile_ranker"]["accuracy"]
        > split_methods[split]["cf_shift_profile_shuffled_delta"]["accuracy"]
        for split in ("dev", "calibration", "fresh_test")
    )
    positive_profile = all(
        split_methods[split]["cf_shift_profile_ranker"]["accuracy"]
        > split_methods[split]["cf_shift_ranker"]["accuracy"]
        and split_methods[split]["cf_shift_profile_ranker"]["accuracy"]
        > split_methods[split]["cf_shift_profile_shuffled_profile"]["accuracy"]
        for split in ("dev", "calibration", "fresh_test")
    )
    def useful_residual(threshold: float | None, row: dict[str, Any]) -> bool:
        return (threshold is not None and row["net_correction"] > 0 and row["repairs"] > row["harms"]
                and row["answer_change_coverage"] >= .05)
    cf_residual_positive = (selected_cf_calibration is not None
                            and useful_residual(selected_cf, cf_residual))
    profile_residual_positive = (selected_calibration is not None
                                 and useful_residual(selected, profile_residual))
    residual_positive = cf_residual_positive or profile_residual_positive
    diagnostics = metrics["data_diagnostics"]
    if diagnostics["option_score_invalid"] / diagnostics["pairs"] > .05:
        bottleneck = "option-scoring validity"
    elif diagnostics["evidence_match_current_option_profile_coverage"] < .5:
        bottleneck = "DDXPlus evidence-to-option profile coverage"
    elif cf["accuracy"] <= target["accuracy"]:
        bottleneck = "counterfactual preference-shift ranking"
    elif not residual_positive:
        bottleneck = "residual selection / score separation"
    elif (no_evidence["accuracy"] > profile["accuracy"]
          and metrics["methods"]["calibration"]["no_medrgag_evidence"]["accuracy"]
          > metrics["methods"]["calibration"]["cf_shift_profile_ranker"]["accuracy"]):
        bottleneck = "MedRGAG selected-evidence context interference and score separation"
    else:
        bottleneck = "residual score separation"
    pure_shift_bootstrap = metrics["mechanism_bootstrap"][
        "cf_shift_ranker_minus_target_margin_ranker_accuracy"]
    control_bootstrap = metrics["mechanism_bootstrap"][
        "cf_shift_profile_ranker_minus_cf_shift_profile_shuffled_control_accuracy"]
    lines += ["", "## Required questions", "",
              f"1. Option log-probability vs generated MCQ: MedRGAG-evidence log-prob "
              f"{pct(fresh['target_margin_ranker']['accuracy'])} vs generated MedRGAG "
              f"{pct(fresh['medrgag_mcq_proxy']['accuracy'])}; direct log-prob "
              f"{pct(fresh['direct_target_logprob']['accuracy'])} vs generated direct "
              f"{pct(fresh['direct_mcq']['accuracy'])}.",
              f"2. Control→trap shift vs target margin: {pct(cf['accuracy'])} vs {pct(target['accuracy'])}.",
              f"3. Pair accuracy / correct flip: CFShift {pct(cf['both_correct_pair_accuracy'])} / {pct(cf['correct_flip_rate'])}; target margin {pct(target['both_correct_pair_accuracy'])} / {pct(target['correct_flip_rate'])}.",
              f"4. BTR: CFShift {pct(cf['bias_trap_rate'])}; target margin {pct(target['bias_trap_rate'])}.",
              f"5. DDXPlus profile value: profile {pct(profile['accuracy'])}; no profile {pct(cf['accuracy'])}; supported={positive_profile}.",
              f"6. Real vs shuffled control: {pct(profile['accuracy'])} vs {pct(shuffled_control['accuracy'])}.",
              f"7. Real vs shuffled delta: {pct(profile['accuracy'])} vs {pct(shuffled_delta['accuracy'])}.",
              f"8. Real vs shuffled profile: {pct(profile['accuracy'])} vs {pct(shuffled_profile['accuracy'])}.",
              (f"9–10. CF residual repairs={cf_residual['repairs']}, harms={cf_residual['harms']}; "
               f"profile residual repairs={profile_residual['repairs']}, harms={profile_residual['harms']}."
               if selected_cf is not None or selected is not None else
               "9–10. Repairs/harms are not applicable because calibration found no useful residual operating point."),
              f"11. Calibration-selected thresholds: CF={selected_cf if selected_cf is not None else 'none'}; "
              f"profile={selected if selected is not None else 'none'}.",
              f"12. Fresh residual direction reproduces calibration: CF={cf_residual_positive}; "
              f"profile={profile_residual_positive}.",
              (f"13. Counterfactual preference updating: directional criteria are met across all splits={positive_shift}, "
               f"but the pure CF fresh accuracy gain is {pct(pure_shift_bootstrap['difference'])} "
               f"(95% CI {pct(pure_shift_bootstrap['ci_low'])} to {pct(pure_shift_bootstrap['ci_high'])}); "
               "this is preliminary rather than conclusive support."),
              (f"14. Residual MedRGAG augmentation: frozen criteria are met={residual_positive}. "
               f"The conservative CF residual is supported={cf_residual_positive}; the profile residual "
               f"is supported by net correction={profile_residual_positive} but has "
               f"{pct(profile_residual['conditional_harm_rate'])} conditional harm."),
              "15. World-model claim: No.", "", "## Probability diagnostics", "",
              "```json", json.dumps(fresh["probability_metrics"], indent=2, sort_keys=True), "```", "",
              "## Paired mechanism bootstrap", "",
              "Paired by case ID with 1,000 bootstrap samples; differences are real minus control.", "",
              "```json", json.dumps(metrics["mechanism_bootstrap"], indent=2, sort_keys=True), "```", "",
              "## Calibration operating point", "",
              ("CF residual: no calibration threshold had positive net correction."
               if selected_cf_calibration is None else
               f"CF residual threshold {selected_cf_calibration['threshold']}: "
               f"repairs={selected_cf_calibration['repairs']}, harms={selected_cf_calibration['harms']}, "
               f"net={pct(selected_cf_calibration['net_correction'])}, "
               f"coverage={pct(selected_cf_calibration['answer_change_coverage'])}."),
              ("Profile residual: no calibration threshold had positive net correction."
               if selected_calibration is None else
               f"Profile residual threshold {selected_calibration['threshold']}: "
               f"repairs={selected_calibration['repairs']}, harms={selected_calibration['harms']}, "
               f"net={pct(selected_calibration['net_correction'])}, "
               f"coverage={pct(selected_calibration['answer_change_coverage'])}."), "",
              "## Existing 49-way candidate audit", "",
              "This is a zero-cost secondary diagnostic; it does not enter the four-way main comparison.", "",
              "```json", json.dumps(metrics["existing_candidate_audit"], indent=2, sort_keys=True), "```", "",
              "## Remaining bottleneck", "", bottleneck + ".", "",
              "The no-MedRGAG-evidence scorer reaches " + pct(no_evidence["accuracy"]) +
              " versus " + pct(profile["accuracy"]) +
              " with selected evidence on fresh test. Real control improves profile accuracy over shuffled "
              f"control by {pct(control_bootstrap['difference'])}, but its 95% CI "
              f"({pct(control_bootstrap['ci_low'])} to {pct(control_bootstrap['ci_high'])}) includes zero; "
              "pair accuracy and mean gold shift show clearer positive differences.", "",
              "## Limitations", "",
              "- Local all-Llama MedRGAG is a proxy, not the paper's mixed-model configuration.",
              "- Option log probabilities are model scores under two fixed label permutations, not clinical probabilities.",
              "- DDXPlus evidence matching uses deterministic MedCPT best-match logits; it is not manually adjudicated.",
              f"- {metrics['data_diagnostics']['medrgag_selected_document_empty_items']} control/trap items have an empty unchanged KADS selection.",
              f"- {metrics['data_diagnostics']['zero_structured_delta']} pairs have no observable structured finding change after formatting normalization.",
              "- Gold control anchoring is diagnostic only and excluded from the main interpretation.",
              "- No result supports a world-model claim.", ""]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("calibrate", "evaluate"):
        command = sub.add_parser(name)
        command.add_argument("--data", type=Path, nargs="+", required=True)
        command.add_argument("--baseline", type=Path, required=True)
        command.add_argument("--scores", type=Path, required=True)
        command.add_argument("--matches", type=Path, required=True)
        command.add_argument("--conditions", type=Path, required=True)
        if name == "calibrate":
            command.add_argument("--output", type=Path, required=True)
        else:
            command.add_argument("--config", type=Path, required=True)
            command.add_argument("--audit", type=Path, required=True)
            command.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pairs = [row for path in args.data for row in read_jsonl(path)]
    baseline, scores, matches = read_jsonl(args.baseline), read_jsonl(args.scores), read_jsonl(args.matches)
    conditions = json.loads(args.conditions.read_text(encoding="utf-8"))
    if args.command == "calibrate":
        result = calibrate(pairs, baseline, scores, matches, conditions, args.output)
    else:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        audit = json.loads(args.audit.read_text(encoding="utf-8"))
        result = evaluate(pairs, baseline, scores, matches, conditions, config, audit, args.output_dir)
    print(json.dumps({"status": "ok", "keys": sorted(result)}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
