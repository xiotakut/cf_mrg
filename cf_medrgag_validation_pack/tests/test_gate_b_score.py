from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "score_gate_b.py"
SPEC = importlib.util.spec_from_file_location("score_gate_b", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def row(item_id: str, dataset: str, answer, *, options=None, pair_id=None):
    inference = {"item_id": item_id, "dataset": dataset, "options": options}
    gold = {"item_id": item_id, "dataset": dataset, "answer": answer, "pair_id": pair_id}
    return inference, gold


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class GateBScoreTests(unittest.TestCase):
    def test_real_answer_shapes_and_normalization(self) -> None:
        fixtures = [
            (*row("medpic-9f78a05ca4097a72868853f89086c588", "medpic", ["C", "E"], options={"A": "Metformin", "C": "Doxazosin", "E": "Prazosin"}), {"answer": ["E", "C"]}),
            (*row("clir-b844dc0de5ee84cf9c462d22aecca4ef", "clir", ["A"], options={"A": "Decrease", "B": "Increase"}), {"answer": "Decrease."}),
            (*row("clir-7d7fa6b4651abbfa3e516104608ac4db", "clir", ["A"], options={}), {"answer": "Ａ。"}),
            (*row("remedqa-e65e920ff6ab0cdccfc7da66aec82f4b", "remedqa", ["Ketotifen eye drops"], options={"A": "Erythromycin ointment", "B": "Ketotifen eye drops"}), {"answer": "B"}),
            (*row("remedqa-8eab3e3b6eb081ff2505a2f76194d752", "remedqa", ["II"], options={"I": "Erythromycin ointment", "II": "Ketotifen eye drops"}), {"answer": "II"}),
            (*row("medeinst-66e9f073d4d1acebd6aae743ed80f510", "medeinst", ["Bronchitis"]), {"answer": "  BRONCHITIS!  "}),
            (*row("medcounterfact-4f4ec4d45af234134c235d0671c129be", "medcounterfact", ["no difference"]), {"prediction": {"evidence_conclusion": "same"}}),
        ]
        inference, gold, predictions = zip(*fixtures)
        predictions = [{"item_id": g["item_id"], **prediction} for g, prediction in zip(gold, predictions)]
        summary, scored = MODULE.score_rows(list(reversed(inference)), list(gold), list(reversed(predictions)))
        self.assertEqual(7, summary["correct"])
        self.assertTrue(all(row["correct"] for row in scored))

    def test_medpic_is_exact_set_and_roman_is_not_alphabetic(self) -> None:
        first = row("medpic", "medpic", ["A", "B", "C", "D", "E"], options={key: key for key in "ABCDE"})
        second = row("roman", "remedqa", ["II"], options={"I": "one", "II": "two", "III": "three", "IV": "four"})
        predictions = [
            {"item_id": "medpic", "answer": ["A", "B", "C", "D"]},
            {"item_id": "roman", "answer": "B"},
        ]
        summary, scored = MODULE.score_rows([first[0], second[0]], [first[1], second[1]], predictions)
        self.assertEqual(0, summary["correct"])
        self.assertEqual([False, False], [row["correct"] for row in scored])

    def test_pair_accuracy_requires_every_member_and_ignores_singletons(self) -> None:
        fixtures = [
            (*row("me-control", "medeinst", ["Bronchitis"], pair_id="case_100515"), {"answer": "Bronchitis"}),
            (*row("me-trap", "medeinst", ["Pneumonia"], pair_id="case_100515"), {"answer": "Bronchitis"}),
            (*row("mcf-original", "medcounterfact", ["higher"], pair_id="2"), {"evidence_conclusion": "higher"}),
            (*row("mcf-cf", "medcounterfact", ["higher"], pair_id="2"), {"answer": "higher"}),
            (*row("remedqa-subset", "remedqa", ["D"], options={"D": "Ketotifen"}, pair_id="0004"), {"answer": "D"}),
        ]
        inference, gold, predictions = zip(*fixtures)
        predictions = [{"item_id": g["item_id"], **prediction} for g, prediction in zip(gold, predictions)]
        summary, _ = MODULE.score_rows(list(inference), list(gold), list(predictions))
        self.assertEqual(2, summary["pairs"])
        self.assertEqual(1, summary["pair_correct"])
        self.assertEqual(0.5, summary["pair_accuracy"])
        self.assertIsNone(summary["datasets"]["remedqa"]["pair_accuracy"])

    def test_prediction_subset_and_nested_answers_use_full_gold_pair_membership(self) -> None:
        fixtures = []
        for index, answer in enumerate(("D", "B", "Ketotifen", "II")):
            fixtures.append(row(f"remedqa-{index}", "remedqa", [answer], pair_id="0004"))
        for index in range(10):
            fixtures.append(row(f"cpv-{index}", "cpv", ["D"], options={"D": "right"}, pair_id="medqa_00003"))
        inference = [item[0] for item in fixtures]
        gold = [item[1] for item in fixtures]
        predictions = [
            {"item_id": "remedqa-0", "prediction": {"answer": "D"}},
            {"item_id": "remedqa-1", "prediction": {"answer": "B"}},
            *[
                {"item_id": f"cpv-{index}", "prediction": {"answer": "D"}}
                for index in range(10)
            ],
        ]
        summary, scored = MODULE.score_rows(inference, gold, predictions)
        self.assertEqual(12, summary["rows"])
        self.assertEqual(12, summary["correct"])
        self.assertEqual(1, summary["pairs"])
        self.assertEqual(1.0, summary["pair_accuracy"])
        self.assertIsNone(summary["datasets"]["remedqa"]["pair_accuracy"])
        self.assertEqual(1.0, summary["datasets"]["cpv"]["pair_accuracy"])
        self.assertEqual(12, len(scored))

    def test_cli_writes_summary_and_scored_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inference, gold = row("cpv-item", "cpv", ["D"], options={"A": "wrong", "D": "right"})
            paths = {name: root / name for name in ("inference.jsonl", "gold.jsonl", "predictions.jsonl", "summary.json", "scored.jsonl")}
            write_jsonl(paths["inference.jsonl"], [inference])
            write_jsonl(paths["gold.jsonl"], [gold])
            write_jsonl(paths["predictions.jsonl"], [{"item_id": "cpv-item", "answer": "right"}])
            subprocess.run([
                sys.executable, str(SCRIPT),
                "--inference", str(paths["inference.jsonl"]),
                "--gold", str(paths["gold.jsonl"]),
                "--predictions", str(paths["predictions.jsonl"]),
                "--summary", str(paths["summary.json"]),
                "--scored", str(paths["scored.jsonl"]),
            ], check=True, capture_output=True, text=True)
            self.assertEqual(1.0, json.loads(paths["summary.json"].read_text())["accuracy"])
            self.assertTrue(json.loads(paths["scored.jsonl"].read_text())["correct"])


if __name__ == "__main__":
    unittest.main()
