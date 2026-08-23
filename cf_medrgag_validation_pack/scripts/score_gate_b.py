#!/usr/bin/env python3
"""Score Gate-B predictions against the frozen inference/gold JSONL files."""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


TRAILING_PUNCTUATION = ".,;:!?。；：，！？"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected a JSON object")
        rows.append(row)
    return rows


def index_by_item_id(rows: list[dict[str, Any]], name: str) -> dict[str, dict[str, Any]]:
    indexed = {}
    for row in rows:
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"{name}: missing item_id")
        if item_id in indexed:
            raise ValueError(f"{name}: duplicate item_id={item_id}")
        indexed[item_id] = row
    return indexed


def normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value))
    text = " ".join(text.strip().split()).rstrip(TRAILING_PUNCTUATION).strip()
    return text.casefold()


def tokens(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def canonicalize(values: list[Any], options: Any, dataset: str) -> list[str]:
    option_map = {}
    if isinstance(options, dict):
        option_map = {normalize(key): normalize(value) for key, value in options.items()}
    result = [option_map.get(normalize(value), normalize(value)) for value in values]
    if dataset == "medcounterfact":
        result = ["no difference" if value == "same" else value for value in result]
    return result


def prediction_value(prediction: dict[str, Any], dataset: str) -> Any:
    nested = prediction.get("prediction")
    sources = [nested, prediction] if isinstance(nested, dict) else [prediction]
    for source in sources:
        if dataset == "medcounterfact" and source.get("evidence_conclusion") is not None:
            return source["evidence_conclusion"]
        if source.get("answer") is not None:
            return source["answer"]
    return None


def score_rows(
    inference_rows: list[dict[str, Any]],
    gold_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    inference = index_by_item_id(inference_rows, "inference")
    gold = index_by_item_id(gold_rows, "gold")
    predictions = index_by_item_id(prediction_rows, "predictions")
    if inference.keys() != gold.keys():
        raise ValueError("inference and gold must contain the same item_ids")
    if not predictions.keys() <= gold.keys():
        raise ValueError("predictions contain item_ids absent from inference/gold")

    scored = []
    for item_id, expected_row in gold.items():
        if item_id not in predictions:
            continue
        visible = inference[item_id]
        prediction = predictions[item_id]
        dataset = expected_row["dataset"]
        if visible.get("dataset") != dataset:
            raise ValueError(f"dataset mismatch for item_id={item_id}")

        raw_prediction = prediction_value(prediction, dataset)
        expected = canonicalize(tokens(expected_row.get("answer")), visible.get("options"), dataset)
        predicted = canonicalize(tokens(raw_prediction), visible.get("options"), dataset)
        if dataset == "medpic":
            correct = bool(expected) and set(predicted) == set(expected)
        else:
            correct = len(expected) == len(predicted) == 1 and predicted[0] == expected[0]
        scored.append({
            "item_id": item_id,
            "dataset": dataset,
            "pair_id": expected_row.get("pair_id"),
            "expected": expected_row.get("answer"),
            "predicted": tokens(raw_prediction),
            "canonical_expected": expected,
            "canonical_predicted": predicted,
            "correct": correct,
        })

    dataset_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pair_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        dataset_rows[row["dataset"]].append(row)
        if row["pair_id"] is not None:
            pair_rows[(row["dataset"], str(row["pair_id"]))].append(row)

    full_pair_sizes: dict[tuple[str, str], int] = defaultdict(int)
    for row in gold.values():
        if row.get("pair_id") is not None:
            full_pair_sizes[(row["dataset"], str(row["pair_id"]))] += 1
    complete_pairs = {
        key: rows
        for key, rows in pair_rows.items()
        if full_pair_sizes[key] >= 2 and len(rows) == full_pair_sizes[key]
    }
    pair_results = {key: all(row["correct"] for row in rows) for key, rows in complete_pairs.items()}

    def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
        correct = sum(row["correct"] for row in rows)
        return {"rows": len(rows), "correct": correct, "accuracy": correct / len(rows) if rows else None}

    datasets = {}
    for dataset in sorted(dataset_rows):
        dataset_pairs = [value for (name, _), value in pair_results.items() if name == dataset]
        datasets[dataset] = {
            **metrics(dataset_rows[dataset]),
            "pairs": len(dataset_pairs),
            "pair_correct": sum(dataset_pairs),
            "pair_accuracy": sum(dataset_pairs) / len(dataset_pairs) if dataset_pairs else None,
        }
    all_pair_results = list(pair_results.values())
    summary = {
        **metrics(scored),
        "pairs": len(all_pair_results),
        "pair_correct": sum(all_pair_results),
        "pair_accuracy": sum(all_pair_results) / len(all_pair_results) if all_pair_results else None,
        "datasets": datasets,
    }
    return summary, scored


def write_results(summary_path: Path, scored_path: Path, summary: dict[str, Any], scored: list[dict[str, Any]]) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    scored_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    scored_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in scored), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--scored", type=Path, required=True)
    args = parser.parse_args()
    summary, scored = score_rows(load_jsonl(args.inference), load_jsonl(args.gold), load_jsonl(args.predictions))
    write_results(args.summary, args.scored, summary, scored)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
