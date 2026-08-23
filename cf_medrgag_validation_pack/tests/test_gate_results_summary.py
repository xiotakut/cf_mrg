from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_gate_results.py"
SPEC = importlib.util.spec_from_file_location("summarize_gate_results", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class GateResultsSummaryTest(unittest.TestCase):
    def test_slices_complete_pairs_and_delta(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inference, gold = [], []

            def add(item_id, dataset, *, variant="item", pair_id=None, category=None):
                inference.append({"item_id": item_id, "dataset": dataset})
                gold.append({"item_id": item_id, "dataset": dataset, "variant": variant, "pair_id": pair_id, "category": category})

            add("me-control", "medeinst", variant="control", pair_id="me")
            add("me-trap", "medeinst", variant="trap", pair_id="me")
            for category in MODULE.MCF_CATEGORIES:
                add(f"{category}-original", "medcounterfact", variant="original", pair_id=category)
                add(f"{category}-cf", "medcounterfact", variant="counterfactual", pair_id=category, category=category)
            for task in MODULE.CLIR_TASKS:
                add(task, "clir", variant=f"{task}_file.jsonl")
            add("medpic", "medpic")
            for index in range(4):
                add(f"remedqa-{index}", "remedqa", pair_id="remedqa")
            for index in range(3):
                add(f"cpv-{index}", "cpv", pair_id="cpv")
            write_jsonl(root / "inference.jsonl", inference)
            write_jsonl(root / "gold.jsonl", gold)

            selected = {row["item_id"] for row in gold if not row["item_id"].startswith(("remedqa-", "cpv-"))}
            selected.update({"remedqa-0", "cpv-0"})
            for method in ("M2", "M12"):
                wrong = {"me-trap", "Poison-cf", "t8"} if method == "M2" else set()
                scored = [
                    {"item_id": row["item_id"], "dataset": row["dataset"], "pair_id": row["pair_id"], "correct": row["item_id"] not in wrong}
                    for row in gold if row["item_id"] in selected
                ]
                write_jsonl(root / f"{method}.scored.jsonl", scored)
                (root / f"{method}.summary.json").write_text(json.dumps(self.summary(scored, gold)), encoding="utf-8")

            result = MODULE.summarize(root / "inference.jsonl", root / "gold.jsonl", root, ["M2", "M12"])
            m2 = result["methods"]["M2"]
            self.assertEqual({"correct": 0, "n": 1, "accuracy": 0.0}, m2["slices"]["medeinst"]["trap"])
            self.assertEqual(1, m2["slices"]["medcounterfact"]["counterfactual_rows_by_category"]["Poison"]["n"])
            self.assertEqual(0.0, m2["slices"]["medcounterfact"]["complete_pairs_by_category"]["Poison"]["accuracy"])
            self.assertEqual(0.0, m2["slices"]["clir"]["t8"]["accuracy"])
            self.assertEqual(5, m2["base"]["complete_pairs"]["overall"]["n"])
            self.assertNotIn("remedqa", m2["base"]["complete_pairs"]["datasets"])
            self.assertNotIn("cpv", m2["base"]["complete_pairs"]["datasets"])
            self.assertGreater(result["delta_pp_vs_M2"]["M12"]["base"]["overall"], 0)
            self.assertEqual(0.0, result["delta_pp_vs_M2"]["M2"]["base"]["overall"])

            output = root / "comparison.json"
            subprocess.run([
                sys.executable, str(SCRIPT),
                "--inference", str(root / "inference.jsonl"),
                "--gold", str(root / "gold.jsonl"),
                "--run-dir", str(root),
                "--methods", "M2", "M12",
                "--output", str(output),
            ], check=True)
            self.assertEqual(result, json.loads(output.read_text(encoding="utf-8")))

    @staticmethod
    def summary(scored: list[dict], gold: list[dict]) -> dict:
        by_dataset = defaultdict(list)
        by_id = {row["item_id"]: row for row in scored}
        for row in scored:
            by_dataset[row["dataset"]].append(row["correct"])
        full, selected = defaultdict(set), defaultdict(set)
        for row in gold:
            if row["pair_id"] is not None:
                key = row["dataset"], row["pair_id"]
                full[key].add(row["item_id"])
                if row["item_id"] in by_id:
                    selected[key].add(row["item_id"])
        pairs = {key: all(by_id[item]["correct"] for item in members) for key, members in selected.items() if len(full[key]) >= 2 and members == full[key]}

        def metrics(values):
            return len(values), sum(values), sum(values) / len(values) if values else None

        rows, correct, accuracy = metrics([row["correct"] for row in scored])
        pair_count, pair_correct, pair_accuracy = metrics(list(pairs.values()))
        datasets = {}
        for dataset, values in by_dataset.items():
            n, c, a = metrics(values)
            pair_values = [value for (name, _), value in pairs.items() if name == dataset]
            pn, pc, pa = metrics(pair_values)
            datasets[dataset] = {"rows": n, "correct": c, "accuracy": a, "pairs": pn, "pair_correct": pc, "pair_accuracy": pa}
        return {"rows": rows, "correct": correct, "accuracy": accuracy, "pairs": pair_count, "pair_correct": pair_correct, "pair_accuracy": pair_accuracy, "datasets": datasets}


if __name__ == "__main__":
    unittest.main()
