#!/usr/bin/env python3
"""Parse official MA-RAG round logs without changing its voting behavior."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


LETTERS = "ABCD"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def round_candidates(path: Path, mapping: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for value in read_jsonl(path):
        entropies = [float(item) for item in value.get("token_entropies", [])]
        prediction = value.get("prediction")
        candidates.append({
            "prediction": prediction,
            "label_id": mapping["option_to_label_id"].get(prediction),
            "mean_token_entropy": sum(entropies) / len(entropies) if entropies else None,
            "generated_tokens": len(value.get("logprobs", entropies)),
            "response": value.get("response", "")[:500],
        })
    return candidates


def parse_question(path: Path, mapping: dict[str, Any], member: str, expected_n: int) -> dict[str, Any]:
    round_paths = sorted(path.glob("round_*.jsonl"), key=lambda value: int(value.stem.split("_")[-1]))
    metadata_path = path / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    if metadata.get("status") == "invalid":
        return {"pair_id": mapping["pair_id"], "source_case_id": mapping["source_case_id"],
                "split": mapping["split"], "member": member, "status": "invalid",
                "error": metadata.get("error", "runtime failure"), "rounds_used": len(round_paths),
                "runtime_metadata": metadata}
    if not round_paths or not metadata_path.exists():
        return {"pair_id": mapping["pair_id"], "source_case_id": mapping["source_case_id"],
                "split": mapping["split"], "member": member, "status": "invalid",
                "error": "no completion metadata" if round_paths else "no completed round"}
    all_round_candidates = [round_candidates(value, mapping) for value in round_paths]
    first_candidates = all_round_candidates[0]
    candidates = all_round_candidates[-1]
    valid = (len(candidates) == expected_n
             and all(value["prediction"] in mapping["option_to_label_id"]
                     and value["mean_token_entropy"] is not None
                     and math.isfinite(value["mean_token_entropy"]) for value in candidates))
    counts = Counter(value["prediction"] for value in candidates
                     if value["prediction"] in mapping["option_to_label_id"])
    first_counts = Counter(value["prediction"] for value in first_candidates
                           if value["prediction"] in mapping["option_to_label_id"])
    vote_counts = {letter: counts[letter] for letter in LETTERS}
    leaders = [letter for letter in LETTERS if counts[letter] == max(counts.values(), default=0)]
    vote_tie = len(leaders) != 1
    official_letter = leaders[0] if valid and not vote_tie else None
    alpha = 0.5
    vote_scores = {letter: math.log((vote_counts[letter] + alpha) / (expected_n + 4 * alpha))
                   for letter in LETTERS}
    return {
        "pair_id": mapping["pair_id"], "source_case_id": mapping["source_case_id"],
        "split": mapping["split"], "member": member,
        "status": "ok" if valid and not vote_tie else "invalid",
        "error": (None if valid and not vote_tie else "vote tie" if valid
                  else "candidate count, option parse, or entropy contract failure"),
        "rounds_used": len(round_paths), "final_candidates": candidates,
        "total_candidate_generations": sum(map(len, all_round_candidates)),
        "total_generated_tokens": sum(candidate["generated_tokens"]
                                      for values in all_round_candidates for candidate in values),
        "retrieval_queries": metadata.get("retrieval_queries"),
        "retrieved_documents": metadata.get("retrieved_documents"),
        "query_generated_tokens": metadata.get("query_generated_tokens"),
        "wall_clock_seconds": metadata.get("wall_clock_seconds"),
        "counterfactual_triggered": metadata.get("counterfactual_triggered"),
        "initial_candidate_pool_reused": metadata.get("initial_candidate_pool_reused", False),
        "first_round_predictions": [value["prediction"] for value in first_candidates],
        "first_round_vote_counts": {letter: first_counts[letter] for letter in LETTERS},
        "first_round_unanimous": len(first_counts) == 1 and len(first_candidates) == expected_n,
        "option_to_label_id": mapping["option_to_label_id"],
        "vote_counts": vote_counts, "vote_scores": vote_scores,
        "consensus_strength": max(vote_counts.values()) / expected_n,
        "unanimous": len(leaders) == 1 and max(vote_counts.values()) == expected_n,
        "vote_tie": vote_tie, "official_prediction": official_letter,
        "official_label_id": mapping["option_to_label_id"].get(official_letter),
    }


def isolate_trigger(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = {(row["split"], row["pair_id"], row["member"]): row for row in rows
                if row["method"] == "marag_int"}
    result = []
    for row in rows:
        if row["method"] != "cf_trigger_only":
            result.append(row)
            continue
        if row.get("counterfactual_triggered"):
            result.append({**row, "source_method": "cf_trigger_only", "baseline_reused": False})
            continue
        source = baseline.get((row["split"], row["pair_id"], row["member"]))
        if source is None:
            raise ValueError("cf_trigger_only requires matching marag_int output")
        result.append({**source, "method": "cf_trigger_only", "source_method": "marag_int",
                       "baseline_reused": True, "counterfactual_triggered": False})
    return result


def parse_runs(mapping_path: Path, runs: list[str], expected_n: int, output: Path) -> dict[str, Any]:
    mappings = read_jsonl(mapping_path)
    by_member_id = {
        (mapping["split"], member, mapping[f"{member}_marag_id"]): mapping
        for mapping in mappings for member in ("control", "trap", "pair_prompt")
    }
    rows = []
    for specification in runs:
        parts = specification.split(":", 4)
        if len(parts) == 3:
            method, (split, member, raw_path) = "marag_int", parts
            candidates = expected_n
        elif len(parts) == 5:
            method, split, member, candidates, raw_path = parts
            candidates = int(candidates)
        else:
            method, split, member, raw_path = parts
            candidates = expected_n
        evaluations = Path(raw_path) / "evaluations"
        for question in sorted(evaluations.glob("question_*"), key=lambda value: int(value.name.split("_")[-1])):
            item_id = int(question.name.split("_")[-1])
            mapping = by_member_id.get((split, member, item_id))
            if mapping is None:
                raise ValueError(f"no mapping for {split}:{member}:{item_id}")
            row = parse_question(question, mapping, member, candidates)
            row["method"] = method
            rows.append(row)
    rows = isolate_trigger(rows)
    keys = [(row["method"], row["split"], row["pair_id"], row["member"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate parsed MA-RAG member")
    write_jsonl(output, rows)
    return {"rows": len(rows), "valid": sum(row["status"] == "ok" for row in rows),
            "invalid": sum(row["status"] != "ok" for row in rows),
            "unanimous": sum(row.get("unanimous", False) for row in rows)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--run", action="append", required=True,
                        help="method:split:member[:candidates]:path")
    parser.add_argument("--candidates", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(parse_runs(args.mapping, args.run, args.candidates, args.output), sort_keys=True))
