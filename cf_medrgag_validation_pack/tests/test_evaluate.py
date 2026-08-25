from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    value = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(value)
    return value


class EvaluateTest(unittest.TestCase):
    def test_sensitivity_keeps_primary_failures_but_reports_clean_subsets(self):
        ev = module("evaluate")
        rows = []
        for identifier, dataset in (("a", "medpic"), ("b", "medeinst")):
            for method in ("full_transition", "medrgag_proxy", "direct_rank", "structured_no_transition", "effect_shuffle", "full_card_shuffle", "parametric_transition"):
                rows.append({
                    "id": identifier, "dataset": dataset, "task_type": "x", "method": method,
                    "correct": method == "full_transition", "parse_failure": identifier == "b" and method == "full_transition",
                    "shuffle_applicable": True,
                })
        result = ev.evaluate(rows, bootstrap_samples=20)
        self.assertEqual(result["methods"]["full_transition"]["overall"]["n"], 2)
        self.assertEqual(result["sensitivity"]["exclude_medeinst"]["methods"]["full_transition"]["n"], 1)
        self.assertEqual(result["sensitivity"]["common_no_parse_failure_items"]["methods"]["full_transition"]["n"], 1)
        self.assertEqual(result["sensitivity"]["pairwise_complete_case"]["full_transition-medrgag_proxy"]["n"], 1)

    def test_bias_trap_rate_conditions_on_correct_control(self):
        ev = module("evaluate")
        rows = [
            {"id": "c1", "dataset": "medeinst", "correct": True, "prediction": "old", "gold": "old", "pair_id": "1", "pair_role": "control"},
            {"id": "t1", "dataset": "medeinst", "correct": False, "prediction": "old", "gold": "new", "pair_id": "1", "pair_role": "trap"},
            {"id": "c2", "dataset": "medeinst", "correct": False, "prediction": "wrong", "gold": "old", "pair_id": "2", "pair_role": "control"},
            {"id": "t2", "dataset": "medeinst", "correct": False, "prediction": "old", "gold": "new", "pair_id": "2", "pair_role": "trap"},
        ]
        self.assertEqual(ev.bias_trap_rate(rows), {"n": 1, "correct": 1, "accuracy": 1.0})

    def test_metrics_pairs_bootstrap_and_outputs(self) -> None:
        ev = module("evaluate")
        rows = []
        for method, outcomes in {"full_transition": (True, True), "direct_rank": (True, False), "effect_shuffle": (False, False)}.items():
            for index, correct in enumerate(outcomes):
                rows.append({"id": str(index), "dataset": "medeinst", "task_type": "diagnosis_state_update", "method": method, "prediction": "new" if index else "old", "gold": "new" if index else "old", "correct": correct, "pair_id": "p", "pair_role": "trap" if index else "control", "answer_should_change": True, "token_usage": {"total_tokens": 10}})
        result = ev.evaluate(rows, bootstrap_samples=100)
        self.assertEqual(1.0, result["methods"]["full_transition"]["overall"]["accuracy"])
        self.assertEqual(1.0, result["methods"]["full_transition"]["pairs"]["both_correct"]["accuracy"])
        self.assertEqual(0.5, result["comparisons"]["full_transition-direct_rank"]["delta"])
        self.assertEqual(1.0, result["methods"]["full_transition"]["pairs"]["correct_change"]["accuracy"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ev.write_outputs(result, root / "metrics.csv", root / "metrics.json", root / "summary.md")
            self.assertIn("full_transition", (root / "summary.md").read_text())
            self.assertEqual(100, json.loads((root / "metrics.json").read_text())["bootstrap_samples"])

    def test_parse_failures_are_counted_as_wrong_and_reported(self) -> None:
        ev = module("evaluate")
        rows = ev.join_gold(
            [{"id": "x", "dataset": "clir", "task_type": "temporal_forecasting", "method": "direct_rank", "prediction": None, "parse_failure": True}],
            [{"id": "x", "dataset": "clir", "answer": "A"}],
        )
        result = ev.evaluate(rows, bootstrap_samples=10)
        self.assertEqual(0, result["methods"]["direct_rank"]["overall"]["correct"])
        self.assertEqual(1, result["methods"]["direct_rank"]["parse_failures"])

    def test_mechanism_precomputed_and_leakage(self) -> None:
        ins = module("inspect_mechanism")
        cards = [{"id": "x", "method": "full_transition", "task_type": "action_selection", "state": {}, "action": "drug", "evidence": [{"id": "D1", "text": "Drug lowers pressure."}], "transition": {"claims": [{"claim": "Drug lowers pressure; not the correct answer.", "evidence_ids": ["D1"]}, {"claim": "Monitor pulse.", "evidence_ids": ["missing"]}]}}]
        judgment = {"precondition_correct": True, "effect_correct": True, "temporally_consistent": True, "evidence_support": "entailed", "option_leakage": False, "comments": "ok"}
        precomputed = [{"id": "x", "claim_index": 0, "judgment": judgment}, {"id": "x", "claim_index": 1, "judgment": {**judgment, "evidence_support": "not_supported"}}]
        self.assertFalse(ins.valid_judgment({**judgment, "option_leakage": "false"}))
        rows, summary = ins.inspect(cards, precomputed)
        self.assertEqual(2, len(rows))
        self.assertEqual(0.5, summary["claim_citation_rate"])
        self.assertEqual(0.5, summary["unsupported_claim_rate"])
        self.assertEqual(0.5, summary["prohibited_leakage_rate"])
        self.assertEqual(0.5, summary["hard_prohibited_string_rate"])
        self.assertEqual(0.0, summary["judge_option_leakage_rate"])

    def test_mechanism_includes_uncited_transition_statements(self) -> None:
        ins = module("inspect_mechanism")
        transition = {
            "expected_observations": ["cited", "omitted by grounding"],
            "claim_grounding": [{"claim": "cited", "evidence_ids": ["D1"]}],
        }
        extracted = ins.claims({"transition": transition})
        self.assertEqual([claim["claim"] for claim in extracted], ["cited", "omitted by grounding"])
        self.assertEqual(extracted[1]["evidence_ids"], [])

    def test_gold_join_and_nested_cards(self) -> None:
        ev, ins = module("evaluate"), module("inspect_mechanism")
        joined = ev.join_gold(
            [{"id": "x", "dataset": "medeinst", "task_type": "diagnosis_state_update", "method": "direct", "prediction": {"open_answer": "Pneumonia."}}],
            [{"item_id": "x", "dataset": "medeinst", "answer": "pneumonia"}],
        )
        self.assertTrue(joined[0]["correct"])
        judgment = {"precondition_correct": True, "effect_correct": True, "temporally_consistent": True, "evidence_support": "entailed", "option_leakage": False, "comments": "ok"}
        rows, _ = ins.inspect(
            [
                {"id": "x", "method": "full_transition", "evidence": [{"id": "D", "text": "effect"}], "cards": [{"action": "a", "claim_grounding": [{"claim": "effect", "evidence_ids": ["D"]}]}]},
                {"id": "x", "method": "effect_shuffle", "cards": [{"action": "a", "claim_grounding": [{"claim": "must not be judged", "evidence_ids": []}]}]},
            ],
            [{"id": "x", "card_index": 0, "claim_index": 0, "judgment": judgment}],
        )
        self.assertEqual(["D"], rows[0]["valid_evidence_ids"])

    def test_fails_on_method_coverage_mismatch(self) -> None:
        ev = module("evaluate")
        rows = [
            {"id": "a", "dataset": "clir", "task_type": "temporal_forecasting", "method": "direct", "correct": True},
            {"id": "a", "dataset": "clir", "task_type": "temporal_forecasting", "method": "full_transition", "correct": True},
            {"id": "b", "dataset": "clir", "task_type": "temporal_forecasting", "method": "direct", "correct": True},
        ]
        with self.assertRaisesRegex(ValueError, "identical item IDs"):
            ev.evaluate(rows)

    def test_shuffle_comparison_excludes_noops(self) -> None:
        ev = module("evaluate")
        rows = []
        for method in ("full_transition", "effect_shuffle"):
            rows += [
                {"id": "usable", "dataset": "medpic", "task_type": "action_selection", "method": method, "correct": method == "full_transition", "shuffle_applicable": True},
                {"id": "noop", "dataset": "clir", "task_type": "outcome_prediction", "method": method, "correct": True, "shuffle_applicable": False},
            ]
        comparison = ev.evaluate(rows, bootstrap_samples=20)["comparisons"]["full_transition-effect_shuffle"]
        self.assertEqual(1, comparison["n"])
        self.assertEqual(1.0, comparison["delta"])

    def test_nested_token_usage_uses_top_total_without_double_counting(self) -> None:
        ev = module("evaluate")
        metrics = ev.token_metrics([{"token_usage": {
            "total_tokens": 9,
            "state": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "transition": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "method_specific": {"total_tokens": 0},
            "reader": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
        }}])
        self.assertEqual(4, metrics["prompt_tokens"]["total"])
        self.assertEqual(5, metrics["completion_tokens"]["total"])
        self.assertEqual(9, metrics["total_tokens"]["total"])

    def test_positive_requires_parametric_and_mechanism_grounding(self) -> None:
        ev = module("evaluate")
        comparisons = {
            name: {"delta": delta}
            for name, delta in {
                "full_transition-medrgag_proxy": .04,
                "full_transition-direct_rank": .04,
                "full_transition-structured_no_transition": .04,
                "full_transition-effect_shuffle": .02,
                "full_transition-full_card_shuffle": .04,
                "full_transition-parametric_transition": 0.0,
            }.items()
        }
        result = {"comparisons": comparisons, "methods": {
            "full_transition": {"datasets": {"medpic": {"accuracy": .6}}},
            "direct_rank": {"datasets": {"medpic": {"accuracy": .5}}},
            "structured_no_transition": {"datasets": {"medpic": {"accuracy": .55}}},
        }}
        self.assertEqual("mixed", ev.hypothesis_conclusion(result))
        result["transition_mechanism"] = {
            "claim_citation_rate": .6, "claim_entailment_rate": .8,
            "unsupported_claim_rate": .4, "contradiction_rate": .05,
        }
        self.assertEqual("positive", ev.hypothesis_conclusion(result))
        comparisons["full_transition-parametric_transition"]["delta"] = -.01
        self.assertEqual("mixed", ev.hypothesis_conclusion(result))

    def test_positive_requires_medpic_or_clir_transition_gain(self) -> None:
        ev = module("evaluate")
        result = {
            "comparisons": {name: {"delta": .04} for name in (
                "full_transition-medrgag_proxy", "full_transition-direct_rank",
                "full_transition-structured_no_transition", "full_transition-effect_shuffle",
                "full_transition-full_card_shuffle", "full_transition-parametric_transition",
            )},
            "transition_mechanism": {
                "claim_citation_rate": .6, "claim_entailment_rate": .8,
                "unsupported_claim_rate": .4, "contradiction_rate": .05,
            },
            "methods": {
                "full_transition": {"datasets": {"medpic": {"accuracy": .5}, "clir": {"accuracy": .5}}},
                "direct_rank": {"datasets": {"medpic": {"accuracy": .5}, "clir": {"accuracy": .4}}},
                "structured_no_transition": {"datasets": {"medpic": {"accuracy": .4}, "clir": {"accuracy": .5}}},
            },
        }
        self.assertEqual("mixed", ev.hypothesis_conclusion(result))
        result["methods"]["full_transition"]["datasets"]["clir"]["accuracy"] = .6
        self.assertEqual("positive", ev.hypothesis_conclusion(result))


if __name__ == "__main__":
    unittest.main()
