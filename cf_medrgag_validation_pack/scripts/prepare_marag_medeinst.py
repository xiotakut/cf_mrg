#!/usr/bin/env python3
"""Prepare one shared four-option MedEinst view for MA-RAG and MedRGAG."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results_marag_cf"
CACHE = ROOT / "results_cfmoe/cache/marag_cf"
SEED = 223


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CF = load_script("marag_cfshift", ROOT / "scripts/run_cfshift.py")
DELTA = load_script("marag_deltarank", ROOT / "scripts/run_deltarank.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return CF.read_jsonl(path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    CF.write_jsonl(path, rows)


def option_letter(pair: dict[str, Any], label_id: int) -> str:
    return next(letter for letter, value in pair["views"]["four_way"].items()
                if value["label_id"] == label_id)


def changed_findings(delta: dict[str, Any]) -> str:
    lines = [f"Added: {value}" for value in delta["added_findings"]]
    lines += [f"Removed: {value}" for value in delta["removed_findings"]]
    lines += [f"Changed: {value['old']} -> {value['new']}" for value in delta["changed_findings"]]
    return "\n".join(lines) if lines else "No structured finding change was extracted."


def marag_records(pair: dict[str, Any], base_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    options = {letter: value["label"] for letter, value in pair["views"]["four_way"].items()}
    control_id, trap_id, pair_id = base_id, base_id + 1, base_id + 2
    control_question = pair["control"]["narrative"] + "\n\nWhat is the most likely diagnosis?"
    trap_question = pair["trap"]["narrative"] + "\n\nWhat is the most likely diagnosis?"
    pair_question = (
        "Original case:\n" + pair["control"]["narrative"]
        + "\n\nCounterfactual case:\n" + pair["trap"]["narrative"]
        + "\n\nChanged findings:\n" + changed_findings(pair["delta"])
        + "\n\nDiagnose the counterfactual case."
    )
    records = [
        {"id": control_id, "question": control_question, "option": options,
         "answer": option_letter(pair, pair["control"]["label_id"]),
         "question_type": "Multiple-choice question (only one correct answer)"},
        {"id": trap_id, "question": trap_question, "option": options,
         "answer": option_letter(pair, pair["trap"]["label_id"]),
         "question_type": "Multiple-choice question (only one correct answer)"},
        {"id": pair_id, "question": pair_question, "option": options,
         "answer": option_letter(pair, pair["trap"]["label_id"]),
         "question_type": "Multiple-choice question (only one correct answer)"},
    ]
    mapping = {
        "pair_id": pair["pair_id"], "source_case_id": pair["source_case_id"], "split": pair["split"],
        "control_marag_id": control_id, "trap_marag_id": trap_id, "pair_prompt_marag_id": pair_id,
        "option_to_label_id": {letter: value["label_id"]
                               for letter, value in pair["views"]["four_way"].items()},
    }
    return mapping, records


def excluded_source_ids() -> set[str]:
    paths = (
        ROOT / "results_deltarank/test.jsonl",
        ROOT / "results_cfshift/fresh_test.jsonl",
        ROOT / "results_cfmoe/fresh_test.jsonl",
        ROOT / "results_riskroute/new_test.jsonl",
    )
    return {str(row["source_case_id"]) for path in paths for row in read_jsonl(path)}


def prepare(dev_count: int, calibration_count: int, test_count: int) -> dict[str, Any]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    datasets = CACHE / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    dev = read_jsonl(ROOT / "results_cfmoe/dev.jsonl")[:dev_count]
    calibration = read_jsonl(ROOT / "results_cfmoe/calibration.jsonl")[:calibration_count]

    conditions_path = ROOT / "private_data/deltarank_sources/release_conditions.json"
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    label_ids = {name: index for index, name in enumerate(sorted(conditions))}
    profiles = {name: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    remaining: list[dict[str, Any]] = []
    fresh: list[dict[str, Any]] = []
    if test_count:
        raw_test = (ROOT / "private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/"
                    "354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl")
        excluded = excluded_source_ids() | {str(row["source_case_id"]) for row in dev + calibration}
        remaining = [row for row in DELTA.paired_rows(raw_test)
                     if str(row["case_id"]) not in excluded]
        random.Random(SEED).shuffle(remaining)
        selected = remaining[:test_count]
        if len(selected) != test_count:
            raise ValueError(f"only {len(selected)} unused complete test pairs")
        fresh = [CF.adapt_pair(row, "fresh_test", SEED, conditions, profiles, label_ids, DELTA)
                 for row in selected]
    for index, pair in enumerate(fresh):
        pair["shuffle_source_pair_id"] = fresh[(index + 1) % len(fresh)]["pair_id"]

    splits = {"dev": dev, "calibration": calibration, "fresh_test": fresh}
    mappings: list[dict[str, Any]] = []
    for split, pairs in splits.items():
        write_jsonl(RESULTS / f"{split}.jsonl", pairs)
        members = {"control": [], "trap": [], "pair_prompt": []}
        for index, pair in enumerate(pairs):
            mapping, records = marag_records(pair, 3 * index)
            mappings.append(mapping)
            for member, record in zip(members, records):
                members[member].append(record)
        for member, rows in members.items():
            (datasets / f"{split}_{member}.json").write_text(
                json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_jsonl(RESULTS / "marag_dataset_map.jsonl", mappings)

    old = excluded_source_ids() if test_count else set()
    fresh_ids = {row["source_case_id"] for row in fresh}
    if fresh_ids & old or len(fresh_ids) != test_count:
        raise ValueError("fresh test source IDs overlap or repeat")
    return {"development": len(dev), "calibration": len(calibration), "fresh_test": len(fresh),
            "remaining_unused_test_pairs": len(remaining), "seed": SEED,
            "fresh_overlap_with_prior_tests": len(fresh_ids & old)}


def original_subset(source: Path, count: int) -> dict[str, Any]:
    rows = json.loads(source.read_text(encoding="utf-8"))[:count]
    target = CACHE / "datasets/original_medqa_check.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"source": str(source), "target": str(target), "items": len(rows)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--dev", type=int, default=400)
    prep.add_argument("--calibration", type=int, default=150)
    prep.add_argument("--fresh-test", type=int, default=500)
    original = sub.add_parser("original-check")
    original.add_argument("--source", type=Path, default=Path("/home/data3/txy/MA-RAG/datasets/MedQA.json"))
    original.add_argument("--items", type=int, default=100)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = (prepare(args.dev, args.calibration, args.fresh_test) if args.command == "prepare"
              else original_subset(args.source, args.items))
    print(json.dumps(result, sort_keys=True))
