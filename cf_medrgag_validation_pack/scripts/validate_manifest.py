#!/usr/bin/env python3
"""Basic checks for unified counterfactual medical QA manifests.

Usage:
    python scripts/validate_manifest.py manifest.jsonl schemas/unified_item.schema.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit("Install jsonschema: pip install jsonschema") from exc

HIDDEN_AT_INFERENCE = {"answer", "pair_id", "should_answer_change", "change_direction"}


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: validate_manifest.py MANIFEST.jsonl SCHEMA.json", file=sys.stderr)
        return 2

    manifest_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2])
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    ids: set[str] = set()
    pair_members: dict[str, list[str]] = defaultdict(list)
    counts: Counter[str] = Counter()
    errors: list[str] = []

    for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue

        for err in validator.iter_errors(item):
            errors.append(f"line {line_no}: schema: {err.message}")

        item_id = item.get("item_id")
        if item_id in ids:
            errors.append(f"line {line_no}: duplicate item_id={item_id}")
        ids.add(item_id)
        counts[item.get("dataset", "unknown")] += 1

        pair_id = item.get("pair_id")
        if pair_id:
            pair_members[pair_id].append(item_id)

        visible = item.get("metadata", {}).get("inference_visible_fields")
        if visible:
            leaked = HIDDEN_AT_INFERENCE.intersection(visible)
            if leaked:
                errors.append(f"line {line_no}: hidden fields marked visible: {sorted(leaked)}")

    for pair_id, members in pair_members.items():
        if len(members) < 2:
            errors.append(f"pair_id={pair_id} has only {len(members)} member")

    print("Dataset counts:", dict(counts))
    print("Items:", len(ids), "Pairs:", len(pair_members))
    if errors:
        print(f"FAILED with {len(errors)} issue(s):", file=sys.stderr)
        for err in errors[:100]:
            print("-", err, file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
