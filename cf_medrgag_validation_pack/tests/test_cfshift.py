import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run = load("test_run_cfshift", ROOT / "scripts" / "run_cfshift.py")
evaluate = load("test_evaluate_cfshift", ROOT / "scripts" / "evaluate_cfshift.py")


class FakeTokenizer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        return messages[-1]["content"]


class CFShiftTests(unittest.TestCase):
    def test_metric_identities_and_conditional_harm(self):
        truth = {
            "p1": {"trap": {"label_id": 1}},
            "p2": {"trap": {"label_id": 2}},
            "p3": {"trap": {"label_id": 3}},
        }
        baseline = {"p1": 1, "p2": 0, "p3": 3}
        final = {"p1": 0, "p2": 2, "p3": 3}
        value = evaluate.revision_metrics(final, baseline, truth)
        self.assertEqual((value["repairs"], value["harms"]), (1, 1))
        self.assertEqual(value["introduced_error_rate"], 1 / 3)
        self.assertEqual(value["conditional_harm_rate"], 1 / 2)
        self.assertEqual(value["original_correct_preservation"], 1 / 2)
        self.assertEqual(value["net_correction"], 0)

    def test_preference_shift_formula(self):
        target = {0: -2.0, 1: -1.0, 2: -3.0, 3: -4.0}
        control = {0: -1.0, 1: -3.0, 2: -2.0, 3: -4.0}
        score = evaluate.relative_scores(target, control, baseline=0)
        self.assertEqual(score[0], 0)
        self.assertEqual(score[1], 4)
        with_profile = evaluate.relative_scores(target, control, 0, {0: -1, 1: 1, 2: 0, 3: 0})
        self.assertEqual(with_profile[1], 5)

    def test_profile_polarity_and_normalization(self):
        matches = [
            {"operation": "added", "matched_evidence_id": "E1", "similarity": .8},
            {"operation": "removed", "matched_evidence_id": "E2", "similarity": .5},
        ]
        raw = evaluate.raw_profile([0, 1], matches, {0: {"E1"}, 1: {"E2"}})
        self.assertEqual(raw, {0: .8, 1: -.5})
        normalized = evaluate.zscore(raw)
        self.assertTrue(math.isclose(sum(normalized.values()), 0, abs_tol=1e-12))

    def test_two_permutations_map_back_to_labels(self):
        scorer = run.ChoiceScorer(type("Backend", (), {"tokenizer": FakeTokenizer()})())
        scorer._score_single_token = lambda prompts, keys: [
            {"A": 0.0, "B": -1.0, "C": -2.0, "D": -3.0} for _ in prompts
        ]
        options = {key: {"label": f"d{index}", "label_id": index}
                   for index, key in enumerate("ABCD")}
        result = scorer.score_contexts({"target": "case"}, options)["target"]
        self.assertEqual(set(result["log_scores"]), {"0", "1", "2", "3"})
        self.assertTrue(math.isclose(sum(result["probabilities"].values()), 1, abs_tol=1e-12))
        self.assertTrue(all(math.isclose(value, .25) for value in result["probabilities"].values()))

    def test_candidate_audit_union_and_rrf(self):
        methods = ("a", "b", "c", "d")
        candidate = {"pair_id": "p", "rankings": {}, "scores": {}, "split": "dev"}
        for index, method in enumerate(methods):
            ranking = list(range(10))
            if index == 3:
                ranking[-1] = 42
            candidate["rankings"][method] = {"ranked_label_ids": ranking, "status": "ok"}
        pair = {"pair_id": "p", "trap": {"label_id": 42}}
        mcq = {"pair_id": "p", "method": "medrgag_mcq_proxy", "view": "four_way",
               "member": "trap", "predicted_label_id": 0}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, rows in (("c.jsonl", [candidate]), ("d.jsonl", [pair]),
                               ("t.jsonl", [pair]), ("m.jsonl", [mcq])):
                run.write_jsonl(root / name, rows)
            value = run.audit_candidates(root / "c.jsonl", root / "d.jsonl", root / "t.jsonl",
                                         root / "m.jsonl", root / "out.json")
            self.assertEqual(value["dev"]["oracle_union_repairs_at_20"], 1)
            self.assertTrue((root / "out.json").exists())

    def test_residual_invalid_is_not_preserve(self):
        component = {"p": {"status": "invalid", "baseline": 1, "methods": {}}}
        self.assertIsNone(evaluate.residual(component, "cf_shift_ranker", 0)["p"])


if __name__ == "__main__":
    unittest.main()
