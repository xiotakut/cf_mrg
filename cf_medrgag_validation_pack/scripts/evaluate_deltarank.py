#!/usr/bin/env python3
"""Evaluate the closed-set DeltaRank-MedRGAG pilot."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


RANK_METHODS = (
    "target_only_ranker",
    "medrgag_evidence_ranker",
    "full_pair_ranker",
    "pair_aware_ranker",
)
SCORE_METHODS = ("delta_profile_ranker", "shuffled_delta", "shuffled_profile")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def revision_metrics(final: dict[str, int | None], baseline: dict[str, int | None],
                     truth: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pair_ids = sorted(truth)
    n = len(pair_ids)
    baseline_correct = sum(baseline.get(key) == truth[key]["trap"]["label_id"] for key in pair_ids)
    final_correct = sum(final.get(key) == truth[key]["trap"]["label_id"] for key in pair_ids)
    repairs = sum(baseline.get(key) != truth[key]["trap"]["label_id"]
                  and final.get(key) == truth[key]["trap"]["label_id"] for key in pair_ids)
    harms = sum(baseline.get(key) == truth[key]["trap"]["label_id"]
                and final.get(key) != truth[key]["trap"]["label_id"] for key in pair_ids)
    changes = sum(final.get(key) is not None and final.get(key) != baseline.get(key) for key in pair_ids)
    result = {
        "n": n,
        "accuracy": ratio(final_correct, n),
        "baseline_accuracy": ratio(baseline_correct, n),
        "baseline_correct": baseline_correct,
        "baseline_wrong": n - baseline_correct,
        "final_correct": final_correct,
        "repairs": repairs,
        "harms": harms,
        "repair_rate": ratio(repairs, n - baseline_correct),
        "introduced_error_rate": ratio(harms, n),
        "conditional_harm_rate": ratio(harms, baseline_correct),
        "original_correct_preservation": ratio(baseline_correct - harms, baseline_correct),
        "net_correction": ratio(repairs - harms, n),
        "answer_change_coverage": ratio(changes, n),
        "beneficial_revision_precision": ratio(repairs, changes),
        "invalid_count": sum(final.get(key) is None for key in pair_ids),
    }
    assert math.isclose(result["net_correction"], result["accuracy"] - result["baseline_accuracy"], abs_tol=1e-12)
    if result["conditional_harm_rate"] is not None:
        assert math.isclose(result["conditional_harm_rate"],
                            1 - result["original_correct_preservation"], abs_tol=1e-12)
    assert repairs - harms == final_correct - baseline_correct
    return result


def pair_metrics(control: dict[str, int | None], trap: dict[str, int | None],
                 truth: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pair_ids = sorted(truth)
    n = len(pair_ids)
    control_correct = sum(control.get(key) == truth[key]["control"]["label_id"] for key in pair_ids)
    trap_correct = sum(trap.get(key) == truth[key]["trap"]["label_id"] for key in pair_ids)
    both = sum(control.get(key) == truth[key]["control"]["label_id"]
               and trap.get(key) == truth[key]["trap"]["label_id"] for key in pair_ids)
    bias_traps = sum(control.get(key) == truth[key]["control"]["label_id"]
                     and trap.get(key) == truth[key]["control"]["label_id"] for key in pair_ids)
    persistence = sum(control.get(key) is not None and trap.get(key) == control.get(key) for key in pair_ids)
    correct_flips = sum(trap.get(key) == truth[key]["trap"]["label_id"]
                        and trap.get(key) != truth[key]["control"]["label_id"] for key in pair_ids)
    return {
        "control_accuracy": ratio(control_correct, n),
        "trap_accuracy": ratio(trap_correct, n),
        "both_correct_pair_accuracy": ratio(both, n),
        "bias_trap_rate": ratio(bias_traps, control_correct),
        "bias_trap_numerator": bias_traps,
        "bias_trap_denominator": control_correct,
        "old_answer_persistence": ratio(persistence, n),
        "correct_flip_rate": ratio(correct_flips, n),
        "control_invalid_count": sum(control.get(key) is None for key in pair_ids),
        "trap_invalid_count": sum(trap.get(key) is None for key in pair_ids),
    }


def rank_metrics(rankings: dict[str, list[int]], truth: dict[str, dict[str, Any]],
                 baseline: dict[str, int | None]) -> dict[str, Any]:
    pair_ids = sorted(truth)
    ranks, control_ranks = [], []
    for pair_id in pair_ids:
        ranking = rankings.get(pair_id, [])
        gold = truth[pair_id]["trap"]["label_id"]
        old = truth[pair_id]["control"]["label_id"]
        ranks.append(ranking.index(gold) + 1 if gold in ranking else None)
        control_ranks.append(ranking.index(old) + 1 if old in ranking else None)
    baseline_wrong = [key for key in pair_ids if baseline.get(key) != truth[key]["trap"]["label_id"]]
    result = {
        "recall_at_1": ratio(sum(value is not None and value <= 1 for value in ranks), len(pair_ids)),
        "recall_at_5": ratio(sum(value is not None and value <= 5 for value in ranks), len(pair_ids)),
        "recall_at_10": ratio(sum(value is not None and value <= 10 for value in ranks), len(pair_ids)),
        "mean_gold_rank_when_present": (sum(value for value in ranks if value is not None)
                                        / sum(value is not None for value in ranks)) if any(value is not None for value in ranks) else None,
        "mean_control_rank_when_present": (sum(value for value in control_ranks if value is not None)
                                           / sum(value is not None for value in control_ranks)) if any(value is not None for value in control_ranks) else None,
        "missing_gold_count": sum(value is None for value in ranks),
        "invalid_count": sum(not rankings.get(key) for key in pair_ids),
    }
    for k in (5, 10):
        count = sum(truth[key]["trap"]["label_id"] in rankings.get(key, [])[:k] for key in baseline_wrong)
        result[f"oracle_top{k}_repairs"] = count
        result[f"oracle_top{k}_repair_capacity"] = ratio(count, len(baseline_wrong))
    return result


def residual_predictions(scores: dict[str, dict[str, Any]], baseline: dict[str, int | None],
                         threshold: float) -> dict[str, int | None]:
    result = {}
    for pair_id, value in scores.items():
        ranking, margin = value.get("ranked_label_ids", []), value.get("delta_margin")
        if value.get("status") != "ok" or not ranking or margin is None:
            result[pair_id] = None
        elif margin >= threshold:
            result[pair_id] = ranking[0]
        else:
            result[pair_id] = baseline.get(pair_id)
    return result


def threshold_curve(scores: dict[str, dict[str, Any]], baseline: dict[str, int | None],
                    truth: dict[str, dict[str, Any]], split: str) -> list[dict[str, Any]]:
    margins = sorted({value["delta_margin"] for value in scores.values()
                      if value.get("status") == "ok" and value.get("delta_margin") is not None})
    if not margins:
        return []
    thresholds = margins + [margins[-1] + 1]
    return [{"split": split, "threshold": threshold,
             **revision_metrics(residual_predictions(scores, baseline, threshold), baseline, truth)}
            for threshold in thresholds]


def best_points(curve: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not curve:
        return None, None
    best = max(curve, key=lambda row: (row["accuracy"], row["net_correction"],
                                      row["answer_change_coverage"]))
    positive = [row for row in curve if row["net_correction"] > 0]
    conservative = max(positive, key=lambda row: (
        -1 if row["original_correct_preservation"] is None else row["original_correct_preservation"],
        row["accuracy"], row["net_correction"], row["answer_change_coverage"],
    )) if positive else None
    return best, conservative


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{100 * value:.2f}%"
    return str(value)


def evaluate(dev_path: Path, test_path: Path, labels_path: Path, deltas_path: Path,
             mcq_path: Path, candidates_path: Path, output_dir: Path) -> dict[str, Any]:
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    pairs = read_jsonl(dev_path) + read_jsonl(test_path)
    truth_all = {row["pair_id"]: row for row in pairs}
    split_ids = {split: sorted(row["pair_id"] for row in pairs if row["split"] == split)
                 for split in ("dev", "test")}
    deltas = {row["pair_id"]: row for row in read_jsonl(deltas_path)}
    mcq = read_jsonl(mcq_path)
    candidates = {row["pair_id"]: row for row in read_jsonl(candidates_path)}
    if set(truth_all) != set(deltas) or set(truth_all) != set(candidates):
        raise ValueError("pair coverage differs across final artifacts")
    mcq_keys = [(row["pair_id"], row["method"], row["view"], row["member"]) for row in mcq]
    if len(mcq_keys) != len(set(mcq_keys)) or len(mcq) != 10 * len(pairs):
        raise ValueError("MCQ rows must cover ten method/view/member cells per pair")
    mcq_index = {key: row for key, row in zip(mcq_keys, mcq)}

    metrics_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = list(mcq)
    operating: dict[str, Any] = {}
    curves: dict[str, list[dict[str, Any]]] = {}
    score_by_split: dict[str, dict[str, dict[str, Any]]] = {}
    baseline_by_split: dict[str, dict[str, int | None]] = {}

    for split in ("dev", "test"):
        pair_ids = split_ids[split]
        truth = {key: truth_all[key] for key in pair_ids}
        baseline = {key: mcq_index[(key, "medrgag_mcq_proxy", "four_way", "trap")]["predicted_label_id"]
                    for key in pair_ids}
        baseline_by_split[split] = baseline
        for method in ("legacy_open_medrgag", "direct_mcq", "medrgag_mcq_proxy"):
            views = ("open",) if method == "legacy_open_medrgag" else ("two_way", "four_way")
            for view in views:
                control = {key: mcq_index[(key, method, view, "control")]["predicted_label_id"] for key in pair_ids}
                trap = {key: mcq_index[(key, method, view, "trap")]["predicted_label_id"] for key in pair_ids}
                metrics_rows.append({"split": split, "method": method, "view": view,
                                     **revision_metrics(trap, baseline, truth),
                                     **pair_metrics(control, trap, truth)})

        for method in RANK_METHODS:
            rankings = {key: candidates[key]["rankings"][method]["ranked_label_ids"] for key in pair_ids}
            final = {key: rankings[key][0] if rankings[key] else None for key in pair_ids}
            metrics_rows.append({"split": split, "method": method, "view": "49_way",
                                 **revision_metrics(final, baseline, truth),
                                 **rank_metrics(rankings, truth, baseline)})
            for key in pair_ids:
                prediction_rows.append({"pair_id": key, "split": split, "method": method,
                                        "view": "49_way", "member": "trap",
                                        "predicted_label_id": final[key], "ranked_label_ids": rankings[key],
                                        "status": candidates[key]["rankings"][method]["status"]})

        for method in SCORE_METHODS:
            values = {key: candidates[key]["scores"][method] for key in pair_ids}
            rankings = {key: value["ranked_label_ids"] for key, value in values.items()}
            final = {key: ranking[0] if ranking else None for key, ranking in rankings.items()}
            metrics_rows.append({"split": split, "method": method, "view": "49_way_rerank",
                                 **revision_metrics(final, baseline, truth),
                                 **rank_metrics(rankings, truth, baseline)})
            for key in pair_ids:
                prediction_rows.append({"pair_id": key, "split": split, "method": method,
                                        "view": "49_way_rerank", "member": "trap",
                                        "predicted_label_id": final[key], "ranked_label_ids": rankings[key],
                                        "status": values[key]["status"],
                                        "delta_margin": values[key].get("delta_margin")})
        real_scores = {key: candidates[key]["scores"]["delta_profile_ranker"] for key in pair_ids}
        score_by_split[split] = real_scores
        always = {key: value["ranked_label_ids"][0] if value["ranked_label_ids"] else None
                  for key, value in real_scores.items()}
        metrics_rows.append({"split": split, "method": "delta_always_apply", "view": "residual",
                             **revision_metrics(always, baseline, truth)})
        for key in pair_ids:
            prediction_rows.append({"pair_id": key, "split": split,
                                    "method": "delta_always_apply", "view": "residual",
                                    "member": "trap", "predicted_label_id": always[key],
                                    "status": real_scores[key]["status"]})
        curves[split] = threshold_curve(real_scores, baseline, truth, split)

    best, conservative = best_points(curves["dev"])
    operating["best_accuracy_dev"] = best
    operating["conservative_dev"] = conservative
    selected_thresholds = {
        "delta_residual": best["threshold"] if best else None,
        "delta_residual_conservative": conservative["threshold"] if conservative else None,
    }
    for method, threshold in selected_thresholds.items():
        for split in ("dev", "test"):
            truth = {key: truth_all[key] for key in split_ids[split]}
            baseline = baseline_by_split[split]
            if threshold is None:
                operating[f"{method}_{split}"] = None
                continue
            final = residual_predictions(score_by_split[split], baseline, threshold)
            values = revision_metrics(final, baseline, truth)
            operating[f"{method}_{split}"] = {"threshold": threshold, **values}
            metrics_rows.append({"split": split, "method": method, "view": "residual",
                                 "threshold": threshold, **values})
            for key in split_ids[split]:
                prediction_rows.append({"pair_id": key, "split": split, "method": method,
                                        "view": "residual", "member": "trap",
                                        "predicted_label_id": final[key],
                                        "baseline_label_id": baseline[key], "threshold": threshold,
                                        "status": "ok" if final[key] is not None else "invalid"})

    test_rows = {(row["method"], row["view"]): row for row in metrics_rows if row["split"] == "test"}
    target = test_rows[("target_only_ranker", "49_way")]
    profile = test_rows[("delta_profile_ranker", "49_way_rerank")]
    shuffle_delta = test_rows[("shuffled_delta", "49_way_rerank")]
    shuffle_profile = test_rows[("shuffled_profile", "49_way_rerank")]
    residual = test_rows.get(("delta_residual", "residual"))
    positive_signal = (profile["recall_at_5"] > target["recall_at_5"]
                       and shuffle_delta["recall_at_5"] < profile["recall_at_5"]
                       and shuffle_profile["recall_at_5"] < profile["recall_at_5"]
                       and profile["oracle_top10_repair_capacity"] is not None
                       and profile["oracle_top10_repair_capacity"] >= .8)
    positive_residual = bool(conservative is not None and residual and residual["net_correction"] > 0
                             and residual["repairs"] > residual["harms"]
                             and residual["answer_change_coverage"] > 0)
    invalid_outputs = {
        "mcq": sum(row["status"] != "ok" for row in mcq),
        "ranking": sum(candidates[key]["rankings"][method]["status"] != "ok"
                       for key in candidates for method in RANK_METHODS),
        "scoring": sum(candidates[key]["scores"][method]["status"] != "ok"
                       for key in candidates for method in SCORE_METHODS),
    }
    nonempty_delta = {split: sum(bool(deltas[key]["added_findings"] or deltas[key]["removed_findings"]
                                         or deltas[key]["changed_findings"]) for key in split_ids[split])
                      for split in ("dev", "test")}
    result = {
        "sample_sizes": {split: len(values) for split, values in split_ids.items()},
        "ontology": {"labels": len(labels), "labels_observed_in_pilot": len({
            truth_all[key][member]["label_id"] for key in truth_all for member in ("control", "trap")})},
        "delta_nonempty": nonempty_delta,
        "methods": metrics_rows,
        "operating_points": operating,
        "invalid_outputs": invalid_outputs,
        "positive_counterfactual_signal": positive_signal,
        "positive_residual_augmentation": positive_residual,
        "world_model_claim_supported": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "predictions.jsonl", prediction_rows)
    (output_dir / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                               encoding="utf-8")
    write_csv(output_dir / "metrics.csv", metrics_rows)
    write_csv(output_dir / "tradeoff.csv", curves["dev"] + curves["test"])
    summary = build_summary(result, test_rows)
    (output_dir / "summary.md").write_text(summary, encoding="utf-8")
    return result


def build_summary(result: dict[str, Any], test: dict[tuple[str, str], dict[str, Any]]) -> str:
    legacy = test[("legacy_open_medrgag", "open")]
    direct2, med2 = test[("direct_mcq", "two_way")], test[("medrgag_mcq_proxy", "two_way")]
    med4 = test[("medrgag_mcq_proxy", "four_way")]
    target, pair, profile = (test[(name, view)] for name, view in (
        ("target_only_ranker", "49_way"), ("pair_aware_ranker", "49_way"),
        ("delta_profile_ranker", "49_way_rerank")))
    shuffled_delta = test[("shuffled_delta", "49_way_rerank")]
    shuffled_profile = test[("shuffled_profile", "49_way_rerank")]
    always = test[("delta_always_apply", "residual")]
    residual = test.get(("delta_residual", "residual"))
    best = result["operating_points"]["best_accuracy_dev"]
    conservative = result["operating_points"]["conservative_dev"]
    bottleneck = ("candidate generation" if profile["oracle_top10_repair_capacity"] is not None
                  and profile["oracle_top10_repair_capacity"] < .8 else
                  "delta/profile scoring" if always["net_correction"] <= 0 else
                  "residual selection" if not result["positive_residual_augmentation"] else "none observed")
    rows = [
        ("legacy_open_medrgag", legacy), ("direct_mcq/two_way", direct2),
        ("medrgag_mcq_proxy/two_way", med2), ("medrgag_mcq_proxy/four_way", med4),
        ("target_only_ranker", target), ("pair_aware_ranker", pair),
        ("delta_profile_ranker", profile), ("delta_always_apply", always),
    ]
    if residual:
        rows.append(("delta_residual", residual))
    table = ["| Method | Accuracy | R@5 | R@10 | Repairs | Harms | Conditional harm | Net | Invalid |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, row in rows:
        table.append(f"| {name} | {fmt(row.get('accuracy'))} | {fmt(row.get('recall_at_5'))} | "
                     f"{fmt(row.get('recall_at_10'))} | {row.get('repairs', 'NA')} | {row.get('harms', 'NA')} | "
                     f"{fmt(row.get('conditional_harm_rate'))} | {fmt(row.get('net_correction'))} | "
                     f"{row.get('invalid_count', 'NA')} |")
    selected = result["operating_points"].get("delta_residual_test")
    return "\n".join([
        "# DeltaRank-MedRGAG pilot", "",
        "## Outcome", "",
        ("The pilot provides positive counterfactual ranking signal." if result["positive_counterfactual_signal"]
         else "The pilot does not meet the predefined criteria for positive counterfactual ranking signal."),
        ("The residual augmentation hypothesis is supported." if result["positive_residual_augmentation"]
         else "The residual augmentation hypothesis is not supported; a no-op is not counted as success."),
        "No result supports a world-model claim.", "",
        "## Data and output space", "",
        f"Development used {result['sample_sizes']['dev']} official train/reference pairs; test used "
        f"{result['sample_sizes']['test']} official test pairs. The fixed DDXPlus ontology has "
        f"{result['ontology']['labels']} labels; {result['ontology']['labels_observed_in_pilot']} occur in the sampled data.",
        f"Structured deltas were nonempty for {result['delta_nonempty']['dev']} development and "
        f"{result['delta_nonempty']['test']} test pairs.", "",
        "## Main test table", "", *table, "",
        "## Required comparisons", "",
        f"1. MCQ adaptation: legacy open accuracy {fmt(legacy['accuracy'])}; four-way MedRGAG MCQ "
        f"{fmt(med4['accuracy'])} (difference {fmt(med4['accuracy'] - legacy['accuracy'])}).",
        f"2. Two-way counterfactual accuracy: direct {fmt(direct2['trap_accuracy'])}; MedRGAG MCQ "
        f"{fmt(med2['trap_accuracy'])}.",
        f"3. Structured delta: pair-aware R@5/R@10 {fmt(pair['recall_at_5'])}/{fmt(pair['recall_at_10'])}; "
        f"target-only {fmt(target['recall_at_5'])}/{fmt(target['recall_at_10'])}.",
        f"4. DDXPlus profiles: delta-profile R@5 {fmt(profile['recall_at_5'])} versus pair-aware "
        f"{fmt(pair['recall_at_5'])}.",
        f"5–6. Always-apply produced {always['repairs']} repairs and {always['harms']} harms.",
        (f"7. Best development-selected residual threshold was {best['threshold']}; on test it produced "
         f"{selected['repairs']} repairs, {selected['harms']} harms, net {fmt(selected['net_correction'])}, "
         f"and coverage {fmt(selected['answer_change_coverage'])}." if best and selected else
         "7. No valid residual operating point was available."),
        f"8. Shuffled-delta R@5 {fmt(shuffled_delta['recall_at_5'])} versus real {fmt(profile['recall_at_5'])}.",
        f"9. Shuffled-profile R@5 {fmt(shuffled_profile['recall_at_5'])} versus real {fmt(profile['recall_at_5'])}.",
        f"10. The main observed bottleneck is {bottleneck}.", "",
        "## Operating points", "",
        f"Best-accuracy development point: {json.dumps(best, sort_keys=True)}",
        (f"Conservative positive-net development point: {json.dumps(conservative, sort_keys=True)}" if conservative
         else "Conservative point: no useful selective operating point had positive development net correction."),
        "The full observed development margin curve is in `tradeoff.csv`; no fixed 1%/2% gate was imposed.", "",
        "## Oracle and validity diagnostics", "",
        f"For the delta-profile candidate set, oracle top-5/top-10 repair capacity was "
        f"{fmt(profile['oracle_top5_repair_capacity'])}/{fmt(profile['oracle_top10_repair_capacity'])}.",
        f"Invalid outputs: {json.dumps(result['invalid_outputs'], sort_keys=True)}. Invalid final outputs count as wrong, "
        "not as PRESERVE.", "",
        "## Limitations", "",
        "This is a local all-Llama MedRGAG proxy, not the published mixed-model configuration. Hard negatives use "
        "deterministic DDXPlus profile overlap. The official train and test files observed here cover 46 of the 49 "
        "ontology labels. The 49-way scorer reranks a top-10 candidate set, so its ceiling depends on candidate recall. "
        "NICE, medication-oriented rules, the prior atomic-rule pipeline, and the prior hard conjunctive gate are not "
        "part of this active experiment.", "",
    ])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--deltas", type=Path, required=True)
    parser.add_argument("--mcq", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = evaluate(args.dev, args.test, args.labels, args.deltas, args.mcq,
                      args.candidates, args.output_dir)
    print(json.dumps({"samples": result["sample_sizes"],
                      "positive_signal": result["positive_counterfactual_signal"],
                      "positive_residual": result["positive_residual_augmentation"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
