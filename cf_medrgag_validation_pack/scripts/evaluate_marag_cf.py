#!/usr/bin/env python3
"""Evaluate the portable and native MA-RAG counterfactual adapters."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OWN_BASE_REFERENCES = {"full_cf_marag_native_plus_adapter": "full_cf_marag_native"}


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CF = load_script("marag_eval_cf", ROOT / "scripts/evaluate_cfshift.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def score_argmax(row: dict[str, Any], name: str, control: bool = False) -> int | None:
    source = row["control_scores"] if control else row["option_scores"]
    values = {int(key): float(value) for key, value in source.get(name, {}).items()}
    return CF.argmax(values)


def control_prediction(method: str, pair_id: str, expert: dict[str, dict[str, Any]],
                       marag: dict[tuple[str, str], dict[str, Any]], split: str) -> int | None:
    row = expert[pair_id]
    if method.startswith("medrgag"):
        return row["baseline_control_label_id"]
    if method in ("profile_only", "cpg_core"):
        return score_argmax(row, "direct_logprob", True)
    base = marag.get((split, pair_id))
    return base.get("official_label_id") if base else None


def method_base(method: str) -> str:
    if method in OWN_BASE_REFERENCES:
        return OWN_BASE_REFERENCES[method]
    if method.startswith("medrgag"):
        return "medrgag_baseline"
    if method == "direct_qwen3":
        return "direct_qwen3"
    return "marag_int_trap"


def disagreement(reference: int | None, candidate: int | None) -> bool | None:
    return None if reference is None or candidate is None else reference != candidate


def complete_cost_row(row: dict[str, Any]) -> bool:
    fields = ("rounds_used", "total_candidate_generations", "retrieval_queries",
              "retrieved_documents", "total_generated_tokens", "wall_clock_seconds")
    return all(isinstance(row.get(field), (int, float)) and math.isfinite(row[field])
               for field in fields)


def bootstrap(ids: list[str], left: dict[str, int | None], right: dict[str, int | None],
              left_control: dict[str, int | None], right_control: dict[str, int | None],
              truth: dict[str, dict[str, Any]], base: dict[str, int | None], samples: int = 1000) -> dict[str, Any]:
    randomizer = random.Random(223)

    def values(chosen: list[str]) -> tuple[float, ...]:
        def accuracy(prediction):
            return mean(prediction[key] == truth[key]["trap"]["label_id"] for key in chosen)
        left_acc, right_acc = accuracy(left), accuracy(right)
        base_correct = [key for key in chosen if base[key] == truth[key]["trap"]["label_id"]]
        left_harm = (mean(left[key] != truth[key]["trap"]["label_id"] for key in base_correct)
                     if base_correct else 0.0)
        right_harm = (mean(right[key] != truth[key]["trap"]["label_id"] for key in base_correct)
                      if base_correct else 0.0)
        def pair_accuracy(control, trap):
            return mean(control[key] == truth[key]["control"]["label_id"]
                        and trap[key] == truth[key]["trap"]["label_id"] for key in chosen)
        def btr(control, trap):
            eligible = [key for key in chosen if control[key] == truth[key]["control"]["label_id"]]
            return (mean(trap[key] == truth[key]["control"]["label_id"] for key in eligible)
                    if eligible else 0.0)
        return (left_acc - right_acc, left_harm - right_harm,
                pair_accuracy(left_control, left) - pair_accuracy(right_control, right),
                btr(left_control, left) - btr(right_control, right),
                left_acc - accuracy(base), right_acc - accuracy(base))

    observed = values(ids)
    draws = [values([randomizer.choice(ids) for _ in ids]) for _ in range(samples)]
    result = {}
    for index, name in enumerate(("accuracy_difference", "conditional_harm_difference",
                                  "pair_accuracy_difference", "bias_trap_rate_difference",
                                  "left_net_correction", "right_net_correction")):
        ordered = sorted(row[index] for row in draws)
        result[name] = observed[index]
        result[name + "_ci"] = [ordered[int(0.025 * samples)],
                                 ordered[min(samples - 1, math.ceil(0.975 * samples) - 1)]]
    return result


def evaluate(pairs_paths: list[Path], predictions_path: Path, expert_path: Path,
             marag_path: Path, output_dir: Path) -> dict[str, Any]:
    pairs = [row for path in pairs_paths for row in read_jsonl(path)]
    prediction_rows = read_jsonl(predictions_path)
    expert = {row["case_id"]: row for row in read_jsonl(expert_path)}
    rounds = read_jsonl(marag_path)
    marag_control = {(row["split"], row["pair_id"]): row for row in rounds
                     if row.get("method", "marag_int") == "marag_int" and row["member"] == "control"}
    predictions = {name: {row["pair_id"]: row["predictions"].get(name) for row in prediction_rows}
                   for name in prediction_rows[0]["predictions"]}
    saved_controls = {name: {row["pair_id"]: row.get("control_predictions", {}).get(name)
                             for row in prediction_rows}
                      for name in prediction_rows[0]["predictions"]}
    truth_by_split = {split: {row["pair_id"]: row for row in pairs if row["split"] == split}
                      for split in sorted({row["split"] for row in pairs})}
    metrics: dict[str, Any] = {"splits": {}, "supplemental_own_base": {}}
    for split, truth in truth_by_split.items():
        ids = sorted(truth)
        split_metrics = {}
        for method, all_values in predictions.items():
            final = {key: all_values[key] for key in ids}
            base_name = method_base(method)
            if base_name not in predictions:
                raise ValueError(f"missing baseline {base_name} for {method}")
            base_all = predictions[base_name]
            base = {key: base_all[key] for key in ids}
            controls = ({key: saved_controls[method][key] for key in ids}
                        if any(saved_controls[method][key] is not None for key in ids)
                        else {key: control_prediction(method, key, expert, marag_control, split)
                              for key in ids})
            split_metrics[method] = {
                "base_reference": base_name,
                **CF.revision_metrics(final, base, truth),
                **CF.pair_metrics(controls, final, truth),
            }
        metrics["splits"][split] = split_metrics
        own_base = {}
        for method, base_name in OWN_BASE_REFERENCES.items():
            if method in predictions and base_name in predictions:
                own_base[method] = {
                    "base_reference": base_name,
                    **CF.revision_metrics(
                        {key: predictions[method][key] for key in ids},
                        {key: predictions[base_name][key] for key in ids}, truth),
                }
        metrics["supplemental_own_base"][split] = own_base

    test_split = "fresh_test" if "fresh_test" in truth_by_split else sorted(truth_by_split)[-1]
    truth = truth_by_split[test_split]; ids = sorted(truth)
    comparisons = [
        ("medrgag_cf_learned", "medrgag_baseline"),
        ("marag_cf_learned", "marag_int_trap"),
        ("marag_cf_learned", "marag_int_pair_prompt"),
        ("marag_cf_learned", "profile_only"),
        ("marag_cf_learned", "marag_cf_without_marag"),
        ("marag_cf_learned", "marag_cf_shuffled_delta"),
        ("marag_cf_learned", "marag_cf_shuffled_profile"),
        ("marag_cf_learned", "marag_cf_shuffled_cpg"),
        ("full_cf_marag_native", "marag_int_trap"),
        ("full_cf_marag_native", "delta_query_only"),
        ("full_cf_marag_native_plus_adapter", "full_cf_marag_native"),
    ]
    bootstrap_result = {}
    for left, right in comparisons:
        if left not in predictions or right not in predictions:
            continue
        base_name = (right if OWN_BASE_REFERENCES.get(left) == right else method_base(left))
        left_controls = {key: saved_controls[left][key] for key in ids}
        right_controls = {key: saved_controls[right][key] for key in ids}
        result = bootstrap(
            ids, predictions[left], predictions[right], left_controls, right_controls,
            truth, predictions[base_name])
        result["base_reference_for_harm_and_net_correction"] = base_name
        bootstrap_result[f"{left}_minus_{right}"] = result

    trap_rounds = {row["pair_id"]: row for row in rounds
                   if row.get("method", "marag_int") == "marag_int"
                   and row["split"] == test_split and row["member"] == "trap"}
    false_rows = []
    repair_methods = [name for name in ("marag_cf_learned", "cf_trigger_only",
                                        "full_cf_marag_native", "full_cf_marag_native_plus_adapter")
                      if name in predictions]
    for key in ids:
        row = trap_rounds[key]
        if row.get("status") != "ok":
            continue
        wrong_unanimous = row["unanimous"] and row["official_label_id"] != truth[key]["trap"]["label_id"]
        value = {
            "pair_id": key, "unanimous": row["unanimous"], "wrong_unanimous": wrong_unanimous,
            "correct_unanimous": row["unanimous"] and not wrong_unanimous,
            "first_round_conflict": not row["first_round_unanimous"],
            "profile_disagrees": disagreement(row["official_label_id"], predictions["profile_only"][key]),
            "cpg_disagrees": disagreement(row["official_label_id"], predictions["cpg_core"][key]),
        }
        value.update({method + "_repairs": wrong_unanimous
                      and predictions[method][key] == truth[key]["trap"]["label_id"]
                      for method in repair_methods})
        false_rows.append(value)
    false_count = sum(row["wrong_unanimous"] for row in false_rows)
    unanimous_profile = [row for row in false_rows
                         if row["unanimous"] and row["profile_disagrees"] is not None]
    unanimous_cpg = [row for row in false_rows
                     if row["unanimous"] and row["cpg_disagrees"] is not None]
    first_round_profile = [row for row in false_rows
                           if not row["first_round_conflict"]
                           and row["profile_disagrees"] is not None]
    false_summary = {
        "n": len(ids),
        "eligible_denominator": len(false_rows),
        "excluded_invalid": len(ids) - len(false_rows),
        "unanimous_stop_rate": sum(row["unanimous"] for row in false_rows) / len(ids),
        "wrong_unanimous_stop_rate": false_count / len(ids),
        "correct_unanimous_stop_rate": sum(row["correct_unanimous"] for row in false_rows) / len(ids),
        "unanimous_stop_rate_among_valid": (mean(row["unanimous"] for row in false_rows)
                                               if false_rows else None),
        "wrong_unanimous_stop_rate_among_valid": (false_count / len(false_rows)
                                                     if false_rows else None),
        "correct_unanimous_stop_rate_among_valid": (
            mean(row["correct_unanimous"] for row in false_rows) if false_rows else None),
        "profile_disagreement_among_unanimous": (mean(row["profile_disagrees"]
                                                        for row in unanimous_profile)
                                                    if unanimous_profile else None),
        "profile_disagreement_among_unanimous_denominator": len(unanimous_profile),
        "cpg_disagreement_among_unanimous": (mean(row["cpg_disagrees"] for row in unanimous_cpg)
                                                if unanimous_cpg else None),
        "cpg_disagreement_among_unanimous_denominator": len(unanimous_cpg),
        "first_round_candidate_conflict_rate": (mean(row["first_round_conflict"] for row in false_rows)
                                                  if false_rows else None),
        "first_round_no_conflict_profile_conflict_rate": (
            mean(row["profile_disagrees"] for row in first_round_profile)
            if first_round_profile else None),
        "first_round_no_conflict_profile_conflict_denominator": len(first_round_profile),
    }
    for method in repair_methods:
        repaired = sum(row[method + "_repairs"] for row in false_rows)
        false_summary[method + "_repairs"] = repaired
        false_summary[method + "_repair_rate"] = repaired / false_count if false_count else None
    efficiency = {}
    for method in sorted({row.get("method", "marag_int") for row in rounds}):
        candidates = [row for row in rounds if row.get("method", "marag_int") == method
                      and row["split"] == test_split and row["member"] == "trap"]
        test_trap = [row for row in candidates if complete_cost_row(row)]
        if not test_trap:
            continue
        efficiency["marag_int_trap" if method == "marag_int" else method] = {
            "denominator": len(test_trap),
            "excluded_incomplete": len(candidates) - len(test_trap),
            "mean_rounds": mean(row["rounds_used"] for row in test_trap),
            "median_rounds": median(row["rounds_used"] for row in test_trap),
            "mean_candidate_generations": mean(row["total_candidate_generations"] for row in test_trap),
            "mean_retrieval_queries": mean(row["retrieval_queries"] for row in test_trap),
            "mean_retrieved_documents": mean(row["retrieved_documents"] for row in test_trap),
            "mean_generated_tokens": mean(row["total_generated_tokens"] for row in test_trap),
            "mean_query_generated_tokens": (mean(row["query_generated_tokens"] for row in test_trap)
                                             if all(row.get("query_generated_tokens") is not None
                                                    for row in test_trap) else None),
            "mean_wall_clock_seconds": mean(row["wall_clock_seconds"] for row in test_trap),
        }
    metrics.update({"bootstrap": bootstrap_result, "false_consensus": false_summary,
                    "efficiency": efficiency})
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n",
                                              encoding="utf-8")
    (output_dir / "bootstrap.json").write_text(json.dumps(bootstrap_result, indent=2, sort_keys=True) + "\n",
                                                encoding="utf-8")
    with (output_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["split", "method", "accuracy", "repairs", "harms", "conditional_harm_rate",
                  "original_correct_preservation", "net_correction", "answer_change_coverage",
                  "control_accuracy", "both_correct_pair_accuracy", "bias_trap_rate", "invalid_count"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n"); writer.writeheader()
        for split, methods in metrics["splits"].items():
            for method, value in methods.items():
                writer.writerow({"split": split, "method": method,
                                 **{field: value.get(field) for field in fields[2:]}})
    with (output_dir / "false_consensus.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(false_rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(false_rows)
    with (output_dir / "efficiency.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["method", *next(iter(efficiency.values()))],
                                lineterminator="\n"); writer.writeheader()
        for method, value in efficiency.items(): writer.writerow({"method": method, **value})
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=Path, action="append", required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--experts", type=Path, required=True)
    parser.add_argument("--marag-rounds", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    value = evaluate(args.pairs, args.predictions, args.experts, args.marag_rounds, args.output_dir)
    print(json.dumps({"splits": sorted(value["splits"]), "methods": len(next(iter(value["splits"].values())))},
                     sort_keys=True))
