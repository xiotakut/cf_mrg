#!/usr/bin/env python3
"""Combine scored Gate results into one method comparison JSON."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


MCF_CATEGORIES = ("ID", "Nonsense tokens", "OOD", "Poison")
CLIR_TASKS = ("t6", "t7", "t8", "t9", "t10")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def index(rows: list[dict[str, Any]], name: str) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        item_id = row.get("item_id")
        if not item_id or item_id in result:
            raise ValueError(f"{name}: missing or duplicate item_id={item_id}")
        result[item_id] = row
    return result


def cell(values: list[bool]) -> dict[str, Any]:
    correct = sum(values)
    return {"correct": correct, "n": len(values), "accuracy": correct / len(values) if values else None}


def pair_groups(gold: dict[str, dict[str, Any]], selected_ids: set[str]) -> dict[tuple[str, str], set[str]]:
    full: dict[tuple[str, str], set[str]] = defaultdict(set)
    selected: dict[tuple[str, str], set[str]] = defaultdict(set)
    for item_id, row in gold.items():
        if row.get("pair_id") is None:
            continue
        key = row["dataset"], str(row["pair_id"])
        full[key].add(item_id)
        if item_id in selected_ids:
            selected[key].add(item_id)
    return {key: members for key, members in selected.items() if len(full[key]) >= 2 and members == full[key]}


def method_result(
    method: str,
    scored_rows: list[dict[str, Any]],
    stored_summary: dict[str, Any],
    gold: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scored = index(scored_rows, f"{method}.scored")
    if not scored.keys() <= gold.keys():
        raise ValueError(f"{method}: scored item absent from full gold")
    for item_id, row in scored.items():
        if row.get("dataset") != gold[item_id].get("dataset"):
            raise ValueError(f"{method}: dataset mismatch for {item_id}")

    by_dataset: dict[str, list[bool]] = defaultdict(list)
    for row in scored.values():
        by_dataset[row["dataset"]].append(bool(row["correct"]))
    complete = pair_groups(gold, set(scored))
    pair_values = {
        key: all(bool(scored[item_id]["correct"]) for item_id in members)
        for key, members in complete.items()
    }

    base = {
        "overall": cell([bool(row["correct"]) for row in scored.values()]),
        "datasets": {dataset: cell(values) for dataset, values in sorted(by_dataset.items())},
        "complete_pairs": {
            "overall": cell(list(pair_values.values())),
            "datasets": {
                dataset: cell([value for (name, _), value in pair_values.items() if name == dataset])
                for dataset in sorted({name for name, _ in pair_values})
            },
        },
    }
    _verify_base(method, base, stored_summary)

    def row_slice(dataset: str, field: str, value: str) -> dict[str, Any]:
        return cell([
            bool(scored[item_id]["correct"])
            for item_id, row in gold.items()
            if item_id in scored and row.get("dataset") == dataset and row.get(field) == value
        ])

    mcf_pair_categories = {}
    for key, members in complete.items():
        if key[0] != "medcounterfact":
            continue
        categories = {
            gold[item_id].get("category")
            for item_id in members
            if gold[item_id].get("variant") == "counterfactual"
        }
        if len(categories) != 1 or next(iter(categories)) not in MCF_CATEGORIES:
            raise ValueError(f"{method}: missing MedCounterFact category for pair {key[1]}")
        mcf_pair_categories[key] = next(iter(categories))

    slices = {
        "medeinst": {variant: row_slice("medeinst", "variant", variant) for variant in ("control", "trap")},
        "medcounterfact": {
            "counterfactual_rows_by_category": {
                category: cell([
                    bool(scored[item_id]["correct"])
                    for item_id, row in gold.items()
                    if item_id in scored
                    and row.get("dataset") == "medcounterfact"
                    and row.get("variant") == "counterfactual"
                    and row.get("category") == category
                ])
                for category in MCF_CATEGORIES
            },
            "complete_pairs_by_category": {
                category: cell([pair_values[key] for key, pair_category in mcf_pair_categories.items() if pair_category == category])
                for category in MCF_CATEGORIES
            },
        },
        "clir": {
            task: cell([
                bool(scored[item_id]["correct"])
                for item_id, row in gold.items()
                if item_id in scored and row.get("dataset") == "clir" and str(row.get("variant", "")).startswith(f"{task}_")
            ])
            for task in CLIR_TASKS
        },
    }
    return {"base": base, "slices": slices}


def _verify_cell(method: str, label: str, actual: dict[str, Any], correct: int, n: int, accuracy: Any) -> None:
    if actual["correct"] != correct or actual["n"] != n:
        raise ValueError(f"{method}: stored summary mismatch at {label}")
    if (actual["accuracy"] is None) != (accuracy is None):
        raise ValueError(f"{method}: stored summary mismatch at {label}")
    if accuracy is not None and abs(actual["accuracy"] - accuracy) > 1e-12:
        raise ValueError(f"{method}: stored summary mismatch at {label}")


def _verify_base(method: str, base: dict[str, Any], stored: dict[str, Any]) -> None:
    _verify_cell(method, "overall", base["overall"], stored["correct"], stored["rows"], stored["accuracy"])
    for dataset, actual in base["datasets"].items():
        value = stored["datasets"][dataset]
        _verify_cell(method, f"dataset.{dataset}", actual, value["correct"], value["rows"], value["accuracy"])
    pairs = base["complete_pairs"]["overall"]
    _verify_cell(method, "complete_pairs", pairs, stored["pair_correct"], stored["pairs"], stored["pair_accuracy"])
    for dataset, actual in base["complete_pairs"]["datasets"].items():
        value = stored["datasets"][dataset]
        _verify_cell(method, f"pairs.{dataset}", actual, value["pair_correct"], value["pairs"], value["pair_accuracy"])


def delta_tree(value: Any, baseline: Any) -> Any:
    if isinstance(value, dict) and {"correct", "n", "accuracy"} <= value.keys():
        if value["accuracy"] is None or baseline["accuracy"] is None:
            return None
        return (value["accuracy"] - baseline["accuracy"]) * 100
    if isinstance(value, dict):
        return {key: delta_tree(child, baseline[key]) for key, child in value.items()}
    raise ValueError("unexpected comparison tree")


def summarize(inference_path: Path, gold_path: Path, run_dir: Path, methods: list[str]) -> dict[str, Any]:
    if "M2" not in methods:
        raise ValueError("methods must include M2 for delta_pp_vs_M2")
    inference, gold = index(load_jsonl(inference_path), "inference"), index(load_jsonl(gold_path), "gold")
    if inference.keys() != gold.keys():
        raise ValueError("full inference and gold item_ids differ")
    results = {}
    selected_ids = None
    for method in methods:
        scored = load_jsonl(run_dir / f"{method}.scored.jsonl")
        current_ids = set(index(scored, f"{method}.scored"))
        if selected_ids is not None and current_ids != selected_ids:
            raise ValueError("methods were not scored on the same item_ids")
        selected_ids = current_ids
        stored = json.loads((run_dir / f"{method}.summary.json").read_text(encoding="utf-8"))
        results[method] = method_result(method, scored, stored, gold)
    return {
        "reference_method": "M2",
        "methods": results,
        "delta_pp_vs_M2": {method: delta_tree(result, results["M2"]) for method, result in results.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.inference, args.gold, args.run_dir, args.methods)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
