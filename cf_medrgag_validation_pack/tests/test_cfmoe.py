import importlib.util
import math
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("test_run_cfmoe", ROOT / "scripts" / "run_cfmoe.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


class CFMoETests(unittest.TestCase):
    def test_cpg_edits_are_applicable_and_change_text(self):
        pair = {
            "trap": {"narrative": "Symptoms:\n* high fever\n* cough"},
            "delta": {"changed_findings": [{"old": "mild fever", "new": "high fever"}],
                      "added_findings": ["cough"], "removed_findings": []},
        }
        edits = run.cpg_edits(pair)
        self.assertEqual({row["operation"] for row in edits}, {"revert", "remove", "negate"})
        self.assertTrue(all(row["edited_case"] != pair["trap"]["narrative"] for row in edits))
        self.assertEqual({row["finding"] for row in edits}, {"high fever", "cough"})

    def test_document_score_identity(self):
        documents = [{"id": "d", "contents": "x"}]
        scores = {"delta:0": [.8], "option:1": [.2], "option:2": [.6], "shared": [.3]}
        row = run.score_document_set(documents, scores, 1, ["1", "2"])[0]
        self.assertTrue(math.isclose(row["cf_document_score"], .8 + .2 - .3))

    def test_runtime_invalid_cannot_fuse(self):
        row = {"fusion_status": "invalid_raw_expert_score"}
        self.assertEqual(run.fused_scores(row, {}, learned=False), {})

    def test_nonfinite_option_score_is_invalid(self):
        self.assertFalse(run.valid_context_scores(
            {"context": {"log_scores": {"0": 0.0, "1": float("nan")}}}, {0, 1}))

    def test_structurally_missing_cpg_is_neutral_only(self):
        labels = [0, 1, 2, 3]
        scores = {str(label): float(label) for label in labels}
        row = {
            "fusion_status": "ok", "cpg_structurally_not_applicable": True,
            "option_label_ids": labels, "quality_features": {},
            "option_scores": {name: ({} if name == "cpg_core" else scores) for name in run.FUSION_EXPERTS},
            "control_scores": {},
        }
        fused = run.fused_scores(row, {}, learned=False)
        self.assertEqual(run.CF_EVAL.argmax(fused), 3)

    def test_merge_exact_drops_previously_observed_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run.write_jsonl(root / "split.jsonl", [{"pair_id": "new"}])
            run.write_jsonl(root / "old.jsonl", [{"pair_id": "observed"}, {"pair_id": "new"}])
            self.assertEqual(run.merge_exact([root / "split.jsonl"], [root / "old.jsonl"],
                                             root / "merged.jsonl"), 1)
            self.assertEqual(run.read_jsonl(root / "merged.jsonl"), [{"pair_id": "new"}])

    def test_remedqa_recon_uses_independent_variant_predictions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = []
            for index in range(4):
                direct = {"gold": 1.0, "other": 0.0} if index < 2 else {"gold": 0.0, "other": 1.0}
                rows.append({"item_id": f"q::{index}", "source_id": "q", "variant": str(index),
                             "status": "ok", "gold_content": "gold", "direct_scores": direct,
                             "medrgag_scores": direct, "original_medrgag_prediction": "gold"})
            run.write_jsonl(root / "scores.jsonl", rows)
            result = run.evaluate_remedqa(root / "scores.jsonl", root / "metrics.json",
                                          root / "summary.md")
            self.assertEqual(result["methods"]["option_logprob_averaging"]["ReCon"], 0.0)
            self.assertEqual(result["methods"]["option_logprob_averaging"]["ReAcc"], 0.0)

    def test_specialist_pilot_requires_an_allowed_diagnosis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = [{"pair_id": key, "trap": {"label": "Gold"},
                       "views": {"four_way": {"A": {"label": "Gold"},
                                                "B": {"label": "Other"}}}}
                      for key in ("a", "b")]
            raw = [
                {"pmc_id": "a", "discussion_result": {"history": [
                    {"role": "Judge Decision", "content": '{"final_diagnosis":"Gold"}'}]}},
                {"pmc_id": "b", "discussion_result": {"history": [
                    {"role": "Judge Decision", "content": '{"final_diagnosis":"Not an option"}'}]}},
            ]
            run.write_jsonl(root / "data.jsonl", inputs)
            (root / "raw.json").write_text(run.json.dumps(raw))
            (root / "metrics.json").write_text("{}")
            (root / "summary.md").write_text(
                "- CPG is the core edit/probability-gap module; full specialist discussion was not run.\n")
            result = run.evaluate_specialist_pilot(root / "data.jsonl", root / "raw.json",
                                                   root / "out.json", root / "metrics.json",
                                                   root / "summary.md")
            self.assertEqual(result["accuracy"], 0.5)
            self.assertEqual(result["invalid_count"], 1)


if __name__ == "__main__":
    unittest.main()
