import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUN = load("run_deltarank_test", ROOT / "scripts" / "run_deltarank.py")
EVAL = load("evaluate_deltarank_test", ROOT / "scripts" / "evaluate_deltarank.py")


class DeltaRankTest(unittest.TestCase):
    def test_structured_delta_aligns_changed_bullet(self):
        old = "Sex: F, Age: 30\n\nSymptoms:\n---\n- cough for 2 days\n- fever\n\nAntecedents:\n---\n- no smoking"
        new = "Sex: F, Age: 30\n\nSymptoms:\n---\n- cough for 5 days\n- fever\n\nAntecedents:\n---\n- no smoking"
        result = RUN.structured_delta(old, new)
        self.assertEqual(result["added_findings"], [])
        self.assertEqual(result["removed_findings"], [])
        self.assertEqual(result["changed_findings"][0]["old"], "cough for 2 days")
        self.assertEqual(result["changed_findings"][0]["new"], "cough for 5 days")

    def test_options_are_deterministic_and_unique(self):
        one = RUN.option_view(["A", "B", "C", "D"], "seed")
        two = RUN.option_view(["A", "B", "C", "D"], "seed")
        self.assertEqual(one, two)
        self.assertEqual(set(value["label"] for value in one.values()), {"A", "B", "C", "D"})

    def test_rank_and_score_contracts(self):
        self.assertTrue(RUN.ranking_valid({"ranked_label_ids": list(range(10))}, set(range(49))))
        self.assertFalse(RUN.ranking_valid({"ranked_label_ids": [0] * 10}, set(range(49))))
        scores = [{"label_id": i, "added_support": 0, "removed_support": -1,
                   "target_case_fit": 2, "delta_fit": 1} for i in range(3)]
        self.assertTrue(RUN.scores_valid({"scores": scores}, {0, 1, 2}))
        scores[0]["delta_fit"] = 3
        self.assertFalse(RUN.scores_valid({"scores": scores}, {0, 1, 2}))

    def test_metric_definitions_and_identities(self):
        truth = {
            "a": {"control": {"label_id": 0}, "trap": {"label_id": 1}},
            "b": {"control": {"label_id": 2}, "trap": {"label_id": 3}},
            "c": {"control": {"label_id": 4}, "trap": {"label_id": 5}},
        }
        baseline = {"a": 1, "b": 2, "c": 4}
        final = {"a": 0, "b": 3, "c": 4}
        result = EVAL.revision_metrics(final, baseline, truth)
        self.assertEqual((result["repairs"], result["harms"]), (1, 1))
        self.assertAlmostEqual(result["introduced_error_rate"], 1 / 3)
        self.assertEqual(result["conditional_harm_rate"], 1.0)
        self.assertEqual(result["original_correct_preservation"], 0.0)
        self.assertEqual(result["net_correction"], 0.0)

    def test_zero_denominators_are_null(self):
        truth = {"a": {"control": {"label_id": 0}, "trap": {"label_id": 1}}}
        result = EVAL.revision_metrics({"a": 1}, {"a": 0}, truth)
        self.assertIsNone(result["conditional_harm_rate"])
        self.assertIsNone(result["original_correct_preservation"])

    def test_threshold_tie_prefers_revision_coverage_not_high_threshold(self):
        curve = [
            {"threshold": 0, "accuracy": .5, "net_correction": 0, "answer_change_coverage": .3,
             "original_correct_preservation": 1.0},
            {"threshold": 1, "accuracy": .5, "net_correction": 0, "answer_change_coverage": .1,
             "original_correct_preservation": 1.0},
        ]
        best, conservative = EVAL.best_points(curve)
        self.assertEqual(best["threshold"], 0)
        self.assertIsNone(conservative)

    def test_residual_support_requires_positive_development_point(self):
        curve = [{"threshold": 4, "accuracy": .49, "net_correction": -.01,
                  "answer_change_coverage": .03, "original_correct_preservation": .97}]
        _, conservative = EVAL.best_points(curve)
        test = {"net_correction": .01, "repairs": 5, "harms": 2,
                "answer_change_coverage": .04}
        supported = bool(conservative is not None and test["net_correction"] > 0
                         and test["repairs"] > test["harms"]
                         and test["answer_change_coverage"] > 0)
        self.assertFalse(supported)

    def test_prepare_builds_49_label_closed_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = [f"Disease {i:02d}" for i in range(49)]
            conditions = {name: {"symptoms": {}, "antecedents": {}} for name in names}
            (root / "conditions.json").write_text(json.dumps(conditions))
            (root / "evidences.json").write_text("{}")

            def rows(case_id, control, trap):
                return [
                    {"case_id": case_id, "case_type": "control", "age": 30, "sex": "F",
                     "narrative": "Symptoms:\n- cough", "ground_truth": control},
                    {"case_id": case_id, "case_type": "trap", "age": 30, "sex": "F",
                     "narrative": "Symptoms:\n- fever", "ground_truth": trap},
                ]
            RUN.write_jsonl(root / "train.jsonl", rows("train", names[0], names[1]))
            RUN.write_jsonl(root / "test.jsonl", rows("test", names[2], names[3]))
            result = RUN.prepare(root / "train.jsonl", root / "test.jsonl", root / "conditions.json",
                                 root / "evidences.json", root / "out", 1, 1, 13)
            self.assertEqual(result["labels"], 49)
            dev = RUN.read_jsonl(root / "out" / "dev.jsonl")[0]
            self.assertEqual(len(dev["views"]["two_way"]), 2)
            self.assertEqual(len(dev["views"]["four_way"]), 4)

    def test_end_to_end_evaluator_writes_all_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labels = [{"label_id": i, "canonical_name": f"D{i}", "aliases": []} for i in range(10)]
            (root / "labels.json").write_text(json.dumps(labels))
            pairs, deltas, mcq, candidates = [], [], [], []
            for split, pair_id in (("dev", "dev-a"), ("test", "test-a")):
                pair = {"pair_id": pair_id, "split": split,
                        "control": {"label_id": 0}, "trap": {"label_id": 1}}
                pairs.append(pair)
                deltas.append({"pair_id": pair_id, "added_findings": ["x"],
                               "removed_findings": [], "changed_findings": []})
                for method in ("direct_mcq", "medrgag_mcq_proxy"):
                    for view in ("two_way", "four_way"):
                        for member, prediction in (("control", 0), ("trap", 0)):
                            mcq.append({"pair_id": pair_id, "split": split, "method": method,
                                        "view": view, "member": member, "predicted_label_id": prediction,
                                        "status": "ok"})
                for member, prediction in (("control", 0), ("trap", 0)):
                    mcq.append({"pair_id": pair_id, "split": split, "method": "legacy_open_medrgag",
                                "view": "open", "member": member, "predicted_label_id": prediction,
                                "status": "ok"})
                ranking = [1, 0] + list(range(2, 10))
                candidates.append({"pair_id": pair_id, "split": split,
                                   "rankings": {method: {"status": "ok", "ranked_label_ids": ranking}
                                                for method in EVAL.RANK_METHODS},
                                   "scores": {method: {"status": "ok", "ranked_label_ids": ranking,
                                                       "delta_margin": 1}
                                              for method in EVAL.SCORE_METHODS}})
            RUN.write_jsonl(root / "dev.jsonl", [pairs[0]])
            RUN.write_jsonl(root / "test.jsonl", [pairs[1]])
            RUN.write_jsonl(root / "deltas.jsonl", deltas)
            RUN.write_jsonl(root / "mcq.jsonl", mcq)
            RUN.write_jsonl(root / "candidates.jsonl", candidates)
            result = EVAL.evaluate(root / "dev.jsonl", root / "test.jsonl", root / "labels.json",
                                   root / "deltas.jsonl", root / "mcq.jsonl", root / "candidates.jsonl",
                                   root / "out")
            self.assertTrue(result["positive_residual_augmentation"])
            predictions = RUN.read_jsonl(root / "out" / "predictions.jsonl")
            self.assertTrue(any(row["method"] == "delta_always_apply" for row in predictions))
            first = (root / "out" / "predictions.jsonl").read_bytes()
            EVAL.evaluate(root / "dev.jsonl", root / "test.jsonl", root / "labels.json",
                          root / "deltas.jsonl", root / "mcq.jsonl", root / "candidates.jsonl",
                          root / "out")
            self.assertEqual(first, (root / "out" / "predictions.jsonl").read_bytes())
            for name in ("predictions.jsonl", "metrics.json", "metrics.csv", "tradeoff.csv", "summary.md"):
                self.assertTrue((root / "out" / name).exists())


if __name__ == "__main__":
    unittest.main()
