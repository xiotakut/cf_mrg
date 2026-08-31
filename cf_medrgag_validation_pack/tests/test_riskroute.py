import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("test_run_riskroute", ROOT / "scripts/run_riskroute.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
eval_spec = importlib.util.spec_from_file_location("test_evaluate_riskroute", ROOT / "scripts/evaluate_riskroute.py")
evaluate = importlib.util.module_from_spec(eval_spec)
eval_spec.loader.exec_module(evaluate)


def example_row():
    labels = [0, 1, 2, 3]
    med = {"0": -2.0, "1": 0.0, "2": -3.0, "3": -4.0}
    profile = {"0": 0.0, "1": -2.0, "2": -3.0, "3": -4.0}
    return {
        "case_id": "p", "source_case_id": "s", "split": "dev", "status": "ok",
        "gold_label_id": 0, "control_gold_label_id": 1,
        "baseline_label_id": 0, "baseline_control_label_id": 1,
        "option_label_ids": labels, "cpg_structurally_not_applicable": False,
        "raw_expert_status": "ok",
        "option_scores": {
            "medrgag": med, "profile_no_document": profile, "cpg_core": profile,
            "profile_cf_kads": profile, "direct_logprob": med,
            "no_medrgag_evidence": med, "profile_original_kads": med,
        },
    }


class RiskRouteTests(unittest.TestCase):
    def test_feature_contract_and_actual_branch_agreement(self):
        row = example_row()
        document = {"variants": {"cf_kads_top3": [], "original_kads_top5": []},
                    "candidate_documents": []}
        match = {"matches": [{"similarity": .8}]}
        record = run.raw_feature_record(row, document, match, {name: 1.0 for name in run.EXPERTS})
        self.assertEqual(len(run.FEATURE_NAMES), 15)
        self.assertEqual(record["features"]["medrgag_profile_agree"], 1.0)
        self.assertNotEqual(record["expert_predictions"]["medrgag"], row["baseline_label_id"])
        self.assertFalse(any("gold" in name or "label_id" in name for name in run.FEATURE_NAMES))

    def test_features_do_not_read_gold(self):
        row = example_row()
        document = {"variants": {}, "candidate_documents": []}
        temperatures = {name: 1.0 for name in run.EXPERTS}
        left = run.raw_feature_record(row, document, {"matches": []}, temperatures)
        right = run.raw_feature_record({**row, "gold_label_id": 3}, document, {"matches": []}, temperatures)
        self.assertEqual(left["features"], right["features"])

    def test_invalid_core_score_never_falls_back(self):
        row = example_row()
        row["option_scores"] = {**row["option_scores"], "profile_no_document": {}}
        record = run.raw_feature_record(row, {}, {}, {name: 1.0 for name in run.EXPERTS})
        self.assertEqual(record["status"], "invalid")
        predictions, choices, _ = evaluate.two_expert_route(
            [record], {"q_medrgag": np.asarray([]), "q_profile": np.asarray([]),
                       "h_profile": np.asarray([])}, 0)
        self.assertIsNone(predictions[row["case_id"]])
        self.assertEqual(choices[row["case_id"]], "invalid")

    def test_exact_tie_uses_declared_confidence_rule(self):
        record = {"profile_prediction": 1, "medrgag_prediction": 0,
                  "expert_probabilities": {"medrgag": {"0": .4, "1": .3, "2": .2, "3": .1},
                                             "profile": {"0": .1, "1": .7, "2": .1, "3": .1}}}
        prediction, choice, ties = run.route_two(np.asarray([.5]), np.asarray([.5]), np.asarray([0.]),
                                                 [record], 0)
        self.assertEqual((prediction, choice, ties), ([1], ["profile"], 1))

    def test_appendix_medrgag_control_uses_reader_branch(self):
        row = example_row()
        row["control_scores"] = {"medrgag": {"0": -2, "1": -1, "2": 4, "3": -3}}
        result = evaluate.method_specific_control_appendix(
            {"medrgag": {row["case_id"]: row["baseline_label_id"]}},
            {"medrgag": {row["case_id"]: "medrgag"}}, [row], {})
        self.assertEqual(result["methods"]["medrgag"]["control_accuracy"], 1.0)

    def test_revision_metric_identities(self):
        truth = {"a": {"trap": {"label_id": 1}}, "b": {"trap": {"label_id": 0}}}
        value = run.CF_EVAL.revision_metrics({"a": 1, "b": 1}, {"a": 0, "b": 0}, truth)
        self.assertEqual(value["repairs"] - value["harms"], value["final_correct"] - value["baseline_correct"])
        self.assertAlmostEqual(value["net_correction"], value["accuracy"] - value["baseline_accuracy"])
        self.assertAlmostEqual(value["conditional_harm_rate"], 1 - value["original_correct_preservation"])

    def test_selective_thresholds_are_calibration_quantiles(self):
        thresholds = run.selective_thresholds(np.asarray([.9, .8, .7, .6, .5]))
        self.assertEqual(thresholds, {"80": .6, "90": .5, "95": .5})

    def test_feature_analysis_selection_note_stays_text(self):
        rows = evaluate.parse_feature_analysis(ROOT / "results_riskroute/feature_analysis.csv")
        self.assertTrue(rows)
        self.assertIsInstance(rows[0]["selection_note"], str)
        self.assertIsNone(next(row for row in rows if row["feature"] == "medrgag_margin")
                          ["nonmissing_standard_deviation"])


if __name__ == "__main__":
    unittest.main()
