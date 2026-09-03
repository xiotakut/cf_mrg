import importlib.util
import inspect
import json
import math
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREPARE = load("test_prepare_marag", "prepare_marag_medeinst.py")
PARSE = load("test_parse_marag", "parse_marag_outputs.py")
RUN = load("test_run_marag", "run_marag_cf.py")
NATIVE = load("test_native_marag", "run_cf_marag_native.py")
EVALUATE = load("test_evaluate_marag", "evaluate_marag_cf.py")


class MaragAdapterTest(unittest.TestCase):
    def pair(self):
        return {
            "pair_id": "p1", "source_case_id": "c1", "split": "dev",
            "control": {"narrative": "Symptoms:\n- old", "label_id": 1},
            "trap": {"narrative": "Symptoms:\n- new", "label_id": 2},
            "delta": {"added_findings": ["new"], "removed_findings": ["old"],
                      "changed_findings": []},
            "views": {"four_way": {
                "A": {"label_id": 1, "label": "D1"},
                "B": {"label_id": 2, "label": "D2"},
                "C": {"label_id": 3, "label": "D3"},
                "D": {"label_id": 4, "label": "D4"},
            }},
        }

    def test_three_records_share_options_without_answer_annotation(self):
        mapping, records = PREPARE.marag_records(self.pair(), 12)
        self.assertEqual([row["id"] for row in records], [12, 13, 14])
        self.assertTrue(all(row["option"] == records[0]["option"] for row in records))
        self.assertEqual(mapping["option_to_label_id"], {"A": 1, "B": 2, "C": 3, "D": 4})
        self.assertTrue(all("answer" not in row["question"].lower() for row in records))

    def test_parse_round_preserves_majority_and_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            rows = []
            for index, answer in enumerate("AAAB", 1):
                rows.append({"answer_id": index, "prediction": answer, "response": answer,
                             "token_entropies": [0.1, 0.3]})
            (path / "round_1.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            (path / "metadata.json").write_text("{}\n", encoding="utf-8")
            result = PARSE.parse_question(path, {
                "pair_id": "p", "source_case_id": "c", "split": "dev",
                "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4},
            }, "trap", 4)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["official_prediction"], "A")
        self.assertEqual(result["vote_counts"], {"A": 3, "B": 1, "C": 0, "D": 0})
        self.assertAlmostEqual(sum(math.exp(value) for value in result["vote_scores"].values()), 1.0)

    def test_tie_is_explicit_not_gold_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            rows = [{"prediction": answer, "response": answer, "token_entropies": [0.2]}
                    for answer in "AABB"]
            (path / "round_1.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            (path / "metadata.json").write_text("{}\n", encoding="utf-8")
            result = PARSE.parse_question(path, {
                "pair_id": "p", "source_case_id": "c", "split": "dev",
                "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4},
            }, "trap", 4)
        self.assertTrue(result["vote_tie"])
        self.assertEqual(result["status"], "invalid")
        self.assertIsNone(result["official_prediction"])

        pair = self.pair()
        sidecar = {
            "status": "ok", "fusion_status": "ok", "option_label_ids": [1, 2, 3, 4],
            "option_scores": {
                "profile_no_document": {str(key): float(key) for key in range(1, 5)},
                "cpg_core": {str(key): float(key) for key in range(1, 5)},
            },
        }
        features, _, _, ids = RUN.feature_tensor(
            "marag", [pair], {"p1": sidecar}, {("dev", "p1", "trap"): result}, 1.0)
        self.assertEqual(len(features), 1)
        self.assertEqual(ids, ["p1"])
        with self.assertRaisesRegex(ValueError, "no valid development"):
            RUN.fit_entropy_temperature([{**result, "final_candidates": []}], {})

    def test_only_well_formed_vote_tie_is_scorable(self):
        valid = {"status": "invalid", "error": "vote tie", "vote_tie": True,
                 "vote_counts": {"A": 2, "B": 2, "C": 0, "D": 0},
                 "vote_scores": {letter: -1.0 for letter in "ABCD"},
                 "final_candidates": [{"label_id": i, "mean_token_entropy": 0.2}
                                      for i in range(4)]}
        self.assertTrue(RUN.scorable_marag(valid))
        self.assertFalse(RUN.scorable_marag({**valid, "final_candidates": []}))
        self.assertFalse(RUN.scorable_marag({**valid, "error": "option parse failure"}))

    def test_score_export_has_vote_and_entropy_vectors(self):
        row = {
            "pair_id": "p", "source_case_id": "c", "split": "dev", "member": "trap",
            "status": "ok", "error": None, "official_prediction": "A",
            "official_label_id": 1, "vote_tie": False, "consensus_strength": 0.75,
            "rounds_used": 1, "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4},
            "final_candidates": [
                {"label_id": label, "mean_token_entropy": entropy}
                for label, entropy in ((1, 0.1), (1, 0.2), (1, 0.3), (2, 0.4))
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "rounds.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
            (path / "config.json").write_text('{"entropy_temperature": 1.0}\n',
                                                encoding="utf-8")
            result = RUN.export_option_scores(path / "rounds.jsonl", path / "config.json",
                                               path / "scores.jsonl")
            exported = json.loads((path / "scores.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(result, {"rows": 1, "scorable": 1, "non_scorable": 0})
        self.assertEqual(set(exported["vote_scores"]), set("ABCD"))
        self.assertEqual(set(exported["entropy_vote_scores"]), set("ABCD"))
        self.assertTrue(all(math.isfinite(value) for value in exported["entropy_vote_scores"].values()))

    def test_missing_entropy_is_invalid_not_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            rows = [{"prediction": "A", "response": "A", "token_entropies": []}
                    for _ in range(4)]
            (path / "round_1.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            (path / "metadata.json").write_text("{}\n", encoding="utf-8")
            result = PARSE.parse_question(path, {
                "pair_id": "p", "source_case_id": "c", "split": "dev",
                "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4},
            }, "trap", 4)
        self.assertEqual(result["status"], "invalid")
        self.assertIsNone(result["official_prediction"])

    def test_incomplete_or_unparseable_round_is_invalid(self):
        mapping = {"pair_id": "p", "source_case_id": "c", "split": "dev",
                   "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            rows = [{"prediction": None, "response": "", "token_entropies": [0.2]}
                    for _ in range(4)]
            (path / "round_1.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            self.assertEqual(PARSE.parse_question(path, mapping, "trap", 4)["status"], "invalid")
            (path / "metadata.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(PARSE.parse_question(path, mapping, "trap", 4)["status"], "invalid")

    def test_runtime_invalid_metadata_precedes_round_parsing(self):
        mapping = {"pair_id": "p", "source_case_id": "c", "split": "dev",
                   "option_to_label_id": {"A": 1, "B": 2, "C": 3, "D": 4}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "metadata.json").write_text(
                json.dumps({"status": "invalid", "error": "missing </think>"}), encoding="utf-8")
            result = PARSE.parse_question(path, mapping, "trap", 4)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["error"], "missing </think>")
        self.assertFalse(EVALUATE.complete_cost_row(result))

    def test_native_runner_does_not_read_gold(self):
        source = inspect.getsource(NATIVE.run)
        self.assertNotIn('dataset["answer"]', source)
        self.assertNotIn("dataset['answer']", source)
        self.assertIn('query_tokens += len(query_output["logprobs"])', source)

    def test_upstream_patch_resumes_only_completed_questions(self):
        patch = (ROOT / "results_marag_cf/marag_logging.patch").read_text(encoding="utf-8")
        self.assertIn("if (path / 'metadata.json').exists()", patch)

    def test_trigger_composite_reuses_baseline_outside_triggered_subset(self):
        base = {"method": "marag_int", "split": "dev", "pair_id": "p1", "member": "trap",
                "official_prediction": "A"}
        rerun = {**base, "method": "cf_trigger_only", "official_prediction": "B",
                 "counterfactual_triggered": False}
        triggered = {**rerun, "pair_id": "p2", "counterfactual_triggered": True}
        base2 = {**base, "pair_id": "p2"}
        rows = PARSE.isolate_trigger([base, base2, rerun, triggered])
        values = {row["method"] + row["pair_id"]: row for row in rows}
        self.assertEqual(values["cf_trigger_onlyp1"]["official_prediction"], "A")
        self.assertTrue(values["cf_trigger_onlyp1"]["baseline_reused"])
        self.assertEqual(values["cf_trigger_onlyp2"]["official_prediction"], "B")
        self.assertFalse(values["cf_trigger_onlyp2"]["baseline_reused"])

    def test_trigger_uses_final_consensus_only_with_round_budget(self):
        rounds = [
            [{"prediction": value} for value in "ABAB"],
            [{"prediction": "A"} for _ in range(4)],
        ]
        options = {"A": 1, "B": 2, "C": 3, "D": 4}
        self.assertTrue(NATIVE.should_append_trigger(rounds, options, 2, 1.2, 1.0, 4))
        self.assertFalse(NATIVE.should_append_trigger(rounds, options, 2, 1.2, 1.0, 2))
        self.assertFalse(NATIVE.should_append_trigger(rounds, options, 1, 1.2, 1.0, 4))

    def test_missing_cpg_is_not_disagreement(self):
        self.assertIsNone(EVALUATE.disagreement(1, None))
        self.assertFalse(EVALUATE.disagreement(1, 1))
        self.assertTrue(EVALUATE.disagreement(1, 2))
        self.assertEqual(EVALUATE.OWN_BASE_REFERENCES,
                         {"full_cf_marag_native_plus_adapter": "full_cf_marag_native"})
        self.assertEqual(EVALUATE.method_base("full_cf_marag_native_plus_adapter"),
                         "full_cf_marag_native")


if __name__ == "__main__":
    unittest.main()
