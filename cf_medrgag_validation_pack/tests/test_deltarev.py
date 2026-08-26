import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


run = load("run_deltarev_test", ROOT / "scripts" / "run_deltarev.py")
evaluate = load("evaluate_deltarev_test", ROOT / "scripts" / "evaluate_deltarev.py")


class Backend:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0
        self.max_tokens = []
        self.prompts = []

    def generate(self, prompts, max_tokens, **kwargs):
        self.calls += 1
        self.max_tokens.append(max_tokens)
        self.prompts.extend(prompts)
        raw = self.responses.pop(0)
        return [{"raw_response": raw, "prompt_tokens": 2, "completion_tokens": 3}]


class Retriever:
    def retrieve(self, query, count):
        return [{"id": f"{query}-{index}", "source": "wikipedia", "contents": f"{query} evidence {index}"}
                for index in range(count)]


class ErrorRetriever(Retriever):
    def retrieve(self, query, count):
        if query == "bad":
            raise RuntimeError("textbooks returned 0 hits")
        return super().retrieve(query, count)


class DeltaRevTest(unittest.TestCase):
    def test_prepare_is_answer_free_and_family_disjoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, inference, gold = root / "raw.jsonl", root / "inference.jsonl", root / "gold.jsonl"
            rows = []
            for family in range(100):
                for case in range(2):
                    case_id = f"case-{family}-{case}"
                    rows += [
                        {"case_id": case_id, "case_type": "control", "age": 40, "sex": "F",
                         "narrative": f"old text {family} {case}", "ground_truth": f"old dx {family}"},
                        {"case_id": case_id, "case_type": "trap", "age": 40, "sex": "F",
                         "narrative": f"new text {family} {case}", "ground_truth": f"new dx {family}"},
                    ]
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows))
            result = run.prepare_pilot(raw, inference, gold)
            self.assertEqual(result["pairs"], 200)
            visible = run.read_jsonl(inference)
            hidden = run.read_jsonl(gold)
            self.assertEqual({row["split"] for row in visible}, {"dev", "test"})
            serialized = inference.read_text().casefold()
            for forbidden in ("ground_truth", "control_answer", "trap_answer", "source_case_id", '"family"'):
                self.assertNotIn(forbidden, serialized)
            dev = {tuple(row["family"]) for row in hidden if row["split"] == "dev"}
            test = {tuple(row["family"]) for row in hidden if row["split"] == "test"}
            self.assertFalse(dev & test)
            self.assertEqual((len(dev), len(test)), (20, 80))

    def test_prepare_supports_97_eligible_families(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); raw = root / "raw"; inference = root / "inference"; gold = root / "gold"
            rows = []
            for family in range(97):
                for case in range(3):
                    for role, diagnosis in (("control", f"old {family}"), ("trap", f"new {family}")):
                        rows.append({"case_id": f"c-{family}-{case}", "case_type": role, "age": 1,
                                     "sex": "F", "narrative": f"{role} {family} {case}",
                                     "ground_truth": diagnosis})
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows))
            run.prepare_pilot(raw, inference, gold)
            hidden = run.read_jsonl(gold)
            self.assertEqual(sum(row["split"] == "dev" for row in hidden), 40)
            self.assertEqual(sum(row["split"] == "test" for row in hidden), 160)
            dev = {tuple(row["family"]) for row in hidden if row["split"] == "dev"}
            test = {tuple(row["family"]) for row in hidden if row["split"] == "test"}
            self.assertFalse(dev & test)

    def test_preserve_is_exact_and_does_not_call_reviser(self):
        baseline = {"answer": "Bronchitis", "format": [1, 2]}
        called = []
        result = run.preserve_or_revise(baseline, False, lambda: called.append(True))
        self.assertIs(result, baseline)
        self.assertEqual(called, [])

    def test_deterministic_delta_ignores_layout_whitespace(self):
        old = "Symptoms:\n- fever\n  - cough"
        new = "Symptoms:  \n- fever  \n    - cough"
        self.assertEqual(run.deterministic_delta(old, new)["changed_variables"], [])

    def test_revision_requires_all_seven_conditions(self):
        base = {"rule_id": "R", "rule_entailed": True, "patient_applicable": True,
                "relation_to_baseline": "refute", "supported_alternatives": ["Pneumonia"],
                "alternative_support_entailed": True,
                "conflict_status": "none", "computed_features": {
                    "source_authority": 1, "refute_preserve_margin": 1, "cross_query_agreement": 1}}
        allowed, score, alternatives = run.revision_allowed("relevant", [base], .9)
        self.assertTrue(allowed); self.assertEqual(alternatives, ["Pneumonia"]); self.assertGreaterEqual(score, .9)
        mutations = [
            ("irrelevant", base),
            ("relevant", {**base, "rule_entailed": False}),
            ("relevant", {**base, "patient_applicable": False}),
            ("relevant", {**base, "relation_to_baseline": "support"}),
            ("relevant", {**base, "supported_alternatives": []}),
            ("relevant", {**base, "alternative_support_entailed": False}),
            ("relevant", {**base, "conflict_status": "unresolved"}),
        ]
        for relevance, row in mutations:
            self.assertFalse(run.revision_allowed(relevance, [row], .9)[0])
        self.assertFalse(run.revision_allowed("relevant", [base], 1.01)[0])
        conflict = {**base, "conflict_status": "unresolved"}
        self.assertFalse(run.revision_allowed("relevant", [base, conflict], 0)[0])

    def test_gate_score_uses_only_joint_decisive_evidence(self):
        weak_refute = {
            "rule_id": "R1", "rule_entailed": True, "patient_applicable": True,
            "relation_to_baseline": "refute", "supported_alternatives": [],
            "alternative_support_entailed": False, "conflict_status": "none",
            "computed_features": {"source_authority": 0, "refute_preserve_margin": 0,
                                  "cross_query_agreement": 0},
        }
        weak_alternative = {
            "rule_id": "R2", "rule_entailed": True, "patient_applicable": True,
            "relation_to_baseline": "neutral", "supported_alternatives": ["Pneumonia"],
            "alternative_support_entailed": True, "conflict_status": "none",
            "computed_features": {"source_authority": 0, "refute_preserve_margin": 0,
                                  "cross_query_agreement": 0},
        }
        strong_support = {
            "rule_id": "R3", "rule_entailed": True, "patient_applicable": True,
            "relation_to_baseline": "support", "supported_alternatives": [],
            "alternative_support_entailed": False, "conflict_status": "none",
            "computed_features": {"source_authority": 1, "refute_preserve_margin": 1,
                                  "cross_query_agreement": 1},
        }
        allowed, score, _ = run.revision_allowed(
            "relevant", [weak_refute, weak_alternative, strong_support], .7)
        self.assertFalse(allowed)
        self.assertLess(score, .7)

    def test_deterministic_candidate_uses_positive_support_counts(self):
        rows = [
            {"rule_id": "R1", "rule_entailed": True, "patient_applicable": True,
             "relation_to_baseline": "refute", "supported_alternatives": [],
             "alternative_support_entailed": False, "conflict_status": "none"},
            {"rule_id": "R2", "rule_entailed": True, "patient_applicable": True,
             "relation_to_baseline": "support", "supported_alternatives": ["Pneumonia"],
             "alternative_support_entailed": True, "conflict_status": "none"},
        ]
        selected = run.deterministic_candidate(["Pneumonia", "Influenza"], "Bronchitis", rows)
        self.assertEqual(selected["candidate_answer"], "Pneumonia")
        self.assertEqual(selected["decisive_rule_ids"], ["R1", "R2"])

    def test_verifier_requires_exact_rule_id_coverage(self):
        rules = [
            {"rule_id": "R1", "evidence_id": "D0", "polarity": "positive", "target": "Pneumonia"},
            {"rule_id": "R2", "evidence_id": "D0", "polarity": "positive", "target": "Pneumonia"},
        ]
        def verification(rule_id):
            return {"rule_id": rule_id, "rule_entailed": True, "patient_applicable": True,
                    "relation_to_baseline": "refute", "supported_alternatives": ["Pneumonia"],
                    "alternative_support_entailed": True, "conflict_status": "none"}
        backend = Backend([
            json.dumps({"verifications": [verification("R1")]}),
            json.dumps({"verifications": [verification("R1"), verification("R2")]})])
        verified, usage = run._verify_rules(
            backend, "case", "Bronchitis", ["Pneumonia"], rules,
            [{"id": "D0", "contents": "text", "source": "wikipedia", "query_index": 0}])
        self.assertEqual({row["rule_id"] for row in verified}, {"R1", "R2"})
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(backend.max_tokens, [384, 384])

    def test_verifier_accepts_exact_rule_keyed_json_alias(self):
        rule = {"rule_id": "R1", "evidence_id": "D0", "polarity": "positive",
                "target": "Pneumonia"}
        row = {"rule_id": "R1", "rule_entailed": True, "patient_applicable": True,
               "relation_to_baseline": "refute", "supported_alternatives": ["Pneumonia"],
               "alternative_support_entailed": True, "conflict_status": "none"}
        backend = Backend([json.dumps({"R1": row})])
        verified, usage = run._verify_rules(
            backend, "case", "Bronchitis", ["Pneumonia"], [rule],
            [{"id": "D0", "contents": "text", "source": "wikipedia", "query_index": 0}])
        self.assertEqual([value["rule_id"] for value in verified], ["R1"])
        self.assertEqual(usage["retry_count"], 0)
        self.assertEqual(backend.max_tokens, [384])

    def test_rule_extractor_repairs_more_than_two_with_bounded_output(self):
        def rule(index):
            return {"condition": f"c{index}", "target": "Pneumonia", "polarity": "positive",
                    "decision_effect": "supports", "exceptions": [], "population_scope": "adults",
                    "evidence_id": "D0", "evidence_span": f"c{index} supports Pneumonia",
                    "source_type": "textbook"}
        backend = Backend([
            json.dumps({"rules": [rule(index) for index in range(3)]}),
            json.dumps({"rules": [rule(0)]}),
        ])
        rules, usage = run._extract_rules(
            backend, "case", "Bronchitis", ["Pneumonia"],
            [{"id": "D0", "contents": "c0 supports Pneumonia", "source": "textbooks"}])
        self.assertEqual(len(rules), 1)
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(backend.max_tokens, [384, 384])

    def test_rule_extractor_prompt_truncates_documents_only(self):
        backend = Backend(['{"rules":[]}'])
        tail = "TAIL_MUST_NOT_REACH_MODEL"
        document = {"id": "D0", "source": "textbooks", "contents": "x" * 1200 + tail}
        run._extract_rules(backend, "case", "Bronchitis", ["Pneumonia"], [document])
        self.assertNotIn(tail, backend.prompts[0])
        self.assertIn("x" * 100, backend.prompts[0])

    def test_compact_rule_contract_rejects_case_copy_and_unknown_target(self):
        rule = {"condition": "c", "target": "Pneumonia", "polarity": "positive",
                "decision_effect": "supports", "exceptions": [], "population_scope": "adults",
                "evidence_id": "D0", "evidence_span": "c supports Pneumonia",
                "source_type": "textbook"}
        allowed = {run.normalize_answer("Bronchitis"), run.normalize_answer("Pneumonia")}
        self.assertTrue(run.rule_valid({"rules": [rule]}, allowed))
        self.assertFalse(run.rule_valid({"rules": [{**rule, "condition": "x" * 81}]}, allowed))
        self.assertFalse(run.rule_valid({"rules": [{**rule, "target": "Unknown"}]}, allowed))
        self.assertFalse(run.rule_valid({"rules": [{**rule, "exceptions": "none"}]}, allowed))

    def test_empty_rules_skip_verifier_model_call(self):
        backend = Backend([])
        verified, usage = run._verify_rules(backend, "case", "old", ["new"], [], [])
        self.assertEqual(verified, [])
        self.assertEqual(backend.calls, 0)
        self.assertEqual(usage["calls"], 0)
        self.assertFalse(usage["contract_failure"])

    def test_negative_refute_cannot_self_authorize_alternative(self):
        rules = [{"rule_id": "R1", "evidence_id": "D0", "polarity": "negative",
                  "target": "Bronchitis"}]
        claimed = {"rule_id": "R1", "rule_entailed": True, "patient_applicable": True,
                   "relation_to_baseline": "refute", "supported_alternatives": ["Pneumonia"],
                   "alternative_support_entailed": True, "conflict_status": "none"}
        verified, _ = run._verify_rules(
            Backend([json.dumps({"verifications": [claimed]})]), "case", "Bronchitis",
            ["Pneumonia"], rules,
            [{"id": "D0", "contents": "Avoid Bronchitis", "source": "wikipedia", "query_index": 0}])
        self.assertFalse(verified[0]["alternative_support_entailed"])
        self.assertEqual(verified[0]["supported_alternatives"], [])

    def test_model_answer_rejects_generic_placeholder(self):
        backend = Backend(['{"answer":"concise diagnosis"}', '{"answer":"Pneumonia."}'])
        answer, usage = run._model_answer(backend, "case")
        self.assertEqual(run.normalize_answer(answer), "pneumonia")
        self.assertEqual(usage["retry_count"], 1)

    def test_model_answer_repairs_wrong_top_level_key_once(self):
        backend = Backend(['{"diagnosis":"label-x17"}', '{"answer":"label-x17"}'])
        answer, usage = run._model_answer(backend, "synthetic case without a diagnosis name")
        self.assertEqual(answer, "label-x17")
        self.assertEqual(backend.calls, 2)
        self.assertEqual(usage["retry_count"], 1)
        self.assertTrue(all('field named "answer"' in prompt and '{"answer":""}' in prompt
                            for prompt in backend.prompts))
        self.assertTrue(all("pneumonia" not in prompt.casefold() for prompt in backend.prompts))

    def test_model_answer_accepts_correct_contract_in_one_call(self):
        backend = Backend(['{"answer":"label-x17"}'])
        answer, usage = run._model_answer(backend, "synthetic case")
        self.assertEqual(answer, "label-x17")
        self.assertEqual(backend.calls, 1)
        self.assertEqual(usage["retry_count"], 0)
        self.assertIn('field named "answer"', backend.prompts[0])
        self.assertNotIn("pneumonia", backend.prompts[0].casefold())

    def test_rule_span_must_resolve_to_unique_current_document(self):
        documents = [{"id": "D0", "contents": "Avoid Drug A in severe impairment.", "source": "textbooks"}]
        rule = {"condition": "impairment", "target": "Drug A", "polarity": "negative",
                "decision_effect": "avoid", "exceptions": [], "population_scope": "adults",
                "evidence_id": "D0", "evidence_span": "avoid drug a", "source_type": "guideline"}
        accepted = run.validate_rule_spans([rule], documents)
        self.assertEqual(accepted[0]["evidence_span"], "Avoid Drug A")
        self.assertEqual(len(run.validate_rule_spans(
            [{**rule, "condition": "renal contraindication"}], documents)), 1)
        self.assertEqual(run.validate_rule_spans([{**rule, "evidence_id": "D9"}], documents), [])
        self.assertEqual(run.validate_rule_spans([{**rule, "evidence_span": "invented"}], documents), [])

    def test_retrieval_budget_is_fixed_and_round_robin(self):
        rows, errors = run.retrieve_queries(
            Retriever(), ["q1", "q2", "q3"], "candidate_specific_retrieval", 10)
        self.assertEqual(len(rows), 10)
        self.assertEqual(errors, [])
        self.assertEqual([row["id"] for row in rows], [f"D{index}" for index in range(10)])
        self.assertEqual({row["query_index"] for row in rows}, {0, 1, 2})

    def test_retrieval_runtime_error_discards_partial_docs_without_model_calls(self):
        documents, errors = run.retrieve_queries(
            ErrorRetriever(), ["good", "bad"], "standard_question_retrieval", 10)
        self.assertEqual(documents, [])
        self.assertEqual(errors, [{"method": "standard_question_retrieval", "query_index": 1,
                                   "query": "bad", "error": "textbooks returned 0 hits"}])
        backend = Backend([])
        answer, answer_usage = run.answer_with_retrieval(backend, "reader", errors)
        rules, verified, extract_usage, verify_usage = run.rules_with_retrieval(
            backend, "case", "old", ["new"], documents, errors)
        self.assertIsNone(answer)
        self.assertEqual((rules, verified), ([], []))
        self.assertEqual(backend.calls, 0)
        self.assertEqual(answer_usage["skipped"], "retrieval_error")
        self.assertEqual(extract_usage["skipped"], "retrieval_error")
        self.assertEqual(verify_usage["skipped"], "retrieval_error")

    def test_retrieval_contract_dependencies_are_explicit(self):
        failures = ["hybrid_delta", "hypotheses", "relevance"]
        self.assertEqual(run.retrieval_dependency_failures("standard_question_retrieval", failures), [])
        self.assertEqual(run.retrieval_dependency_failures("candidate_specific_retrieval", failures),
                         ["hypotheses"])
        self.assertEqual(run.retrieval_dependency_failures("ea_rag_style_retrieval", failures),
                         ["hybrid_delta"])
        self.assertEqual(run.retrieval_dependency_failures("delta_only_retrieval", failures),
                         ["hybrid_delta"])
        self.assertEqual(run.retrieval_dependency_failures(
            "triangular_decision_change_retrieval", failures), ["hybrid_delta", "hypotheses"])

    def test_ea_coverage_audit_detects_uncovered_delta(self):
        delta = {"changed_variables": [
            {"name": "oxygen saturation", "new_value": "82 percent"},
            {"name": "temperature", "new_value": "39 C"},
        ]}
        documents = [{"contents": "Oxygen saturation fell to 82 percent."}]
        audit = run.evidence_coverage_audit(delta, documents)
        self.assertEqual([row["covered"] for row in audit], [True, False])

    def test_model_json_gets_exactly_one_repair(self):
        backend = Backend(["not json", '{"ok":true}'])
        parsed, usage = run.one_repair(backend, "first", lambda row: row.get("ok") is True, "repair")
        self.assertEqual(parsed, {"ok": True}); self.assertEqual(backend.calls, 2)
        self.assertEqual(usage["retry_count"], 1)

    @staticmethod
    def fixture():
        gold = [
            {"pair_id": "d1", "split": "dev", "control_answer": "old", "trap_answer": "new"},
            {"pair_id": "d2", "split": "dev", "control_answer": "old", "trap_answer": "new"},
            {"pair_id": "t1", "split": "test", "control_answer": "old", "trap_answer": "new"},
            {"pair_id": "t2", "split": "test", "control_answer": "old", "trap_answer": "new"},
        ]
        baselines = {row["pair_id"]: {"members": {
            "control": {"baseline_answer": "old" if row["pair_id"] != "t2" else "wrong"},
            "trap": {"baseline_answer": "old"}}} for row in gold}
        proposals = {(row["pair_id"], "full_deltarev"): {
            "pair_id": row["pair_id"], "method": "full_deltarev", "baseline_answer": "old",
            "proposed_answer": "new", "verifier_score": .8 if row["pair_id"] != "d2" else .2,
            "gate_without_threshold": True, "status": "ok"} for row in gold}
        return gold, baselines, proposals

    def test_threshold_curve_uses_dev_gold_only(self):
        gold, baselines, proposals = self.fixture()
        first = evaluate.threshold_curve(gold, baselines, proposals)
        for row in gold:
            if row["split"] == "test": row["trap_answer"] = "completely changed test gold"
        second = evaluate.threshold_curve(gold, baselines, proposals)
        self.assertEqual(first, second)

    def test_btr_denominator_and_target_accuracy(self):
        gold, baselines, proposals = self.fixture()
        metrics, _ = evaluate.score_method(gold, baselines, proposals, "full_deltarev", .9, "test")
        self.assertEqual(metrics["bias_trap_denominator"], 1)
        self.assertEqual(metrics["bias_trap_rate"], 1.0)
        self.assertEqual(metrics["accuracy"], metrics["trap_accuracy"])
        self.assertNotEqual(metrics["accuracy"], metrics["member_accuracy"])

    def test_btr_is_unavailable_with_no_correct_controls(self):
        gold, baselines, proposals = self.fixture()
        for row in gold:
            baselines[row["pair_id"]]["members"]["control"]["baseline_answer"] = "never correct"
        metrics, _ = evaluate.score_method(gold, baselines, proposals, "full_deltarev", .9, "test")
        self.assertEqual(metrics["bias_trap_denominator"], 0)
        self.assertIsNone(metrics["bias_trap_rate"])

    def test_target_only_retrieval_has_no_fabricated_control_metrics(self):
        gold, baselines, _ = self.fixture()
        proposals = {(row["pair_id"], "standard_question_retrieval"): {
            "pair_id": row["pair_id"], "method": "standard_question_retrieval",
            "baseline_answer": "old", "proposed_answer": "new", "status": "ok",
            "gate_without_threshold": True, "verifier_score": 1.0, "control_prediction": None}
            for row in gold}
        metrics, _ = evaluate.score_method(
            gold, baselines, proposals, "standard_question_retrieval", .5, "test")
        self.assertIsNone(metrics["control_accuracy"])
        self.assertIsNone(metrics["pair_accuracy"])
        self.assertIsNone(metrics["bias_trap_rate"])

    def test_partial_method_controls_keep_pair_metrics_and_count_missing_as_wrong(self):
        gold, baselines, _ = self.fixture()
        proposals = {}
        for index, row in enumerate(gold):
            proposals[(row["pair_id"], "direct")] = {
                "pair_id": row["pair_id"], "method": "direct", "baseline_answer": "old",
                "proposed_answer": "new", "status": "ok", "gate_without_threshold": True,
                "verifier_score": 1.0, "control_prediction": "old" if index else None}
        metrics, _ = evaluate.score_method(gold, baselines, proposals, "direct", .5, "dev")
        self.assertEqual(metrics["missing_control_prediction_count"], 1)
        self.assertEqual(metrics["control_accuracy"], .5)
        self.assertEqual(metrics["pair_accuracy"], .5)
        self.assertIsNotNone(metrics["bias_trap_rate"])
        self.assertIsNone(metrics["revision_coverage"])

    def test_direct_revision_uses_shared_control_but_not_failure_fallback(self):
        gold, baselines, _ = self.fixture()
        proposals = {(row["pair_id"], "direct_answer_revision"): {
            "pair_id": row["pair_id"], "method": "direct_answer_revision",
            "baseline_answer": "old", "proposed_answer": "new", "status": "ok",
            "gate_without_threshold": False, "verifier_score": 0, "control_prediction": None}
            for row in gold}
        metrics, _ = evaluate.score_method(
            gold, baselines, proposals, "direct_answer_revision", .5, "dev")
        self.assertIsNotNone(metrics["control_accuracy"])
        self.assertEqual(metrics["control_metric_note"],
                         "shared unchanged M2 control for direct answer-revision baseline")
        failed = {**next(iter(proposals.values())), "status": "contract_failure"}
        self.assertIsNone(evaluate.final_answer(failed, .5))

    def test_unavailable_metrics_are_explicit_na(self):
        self.assertIsNone(evaluate.NA["recall_at_5"])
        self.assertIsNone(evaluate.NA["source_rule_upper_bound"])
        self.assertIsNone(evaluate.NA["without_nice"])

    def test_non_residual_parse_failure_is_not_m2_fallback(self):
        proposal = {"method": "standard_question_retrieval", "baseline_answer": "old",
                    "proposed_answer": None, "status": "parse_failure"}
        self.assertIsNone(evaluate.final_answer(proposal, .5))
        direct_revision = {**proposal, "method": "direct_answer_revision"}
        self.assertIsNone(evaluate.final_answer(direct_revision, .5))
        residual = {**proposal, "method": "full_deltarev"}
        self.assertEqual(evaluate.final_answer(residual, .5), "old")

    def test_failure_counts_and_exact_preserved_cell(self):
        gold, baselines, _ = self.fixture()
        proposals = {}
        for index, row in enumerate(gold):
            proposals[(row["pair_id"], "full_deltarev")] = {
                "pair_id": row["pair_id"], "method": "full_deltarev", "baseline_answer": "old",
                "proposed_answer": "new", "verifier_score": .9, "gate_without_threshold": False,
                "status": "parse_failure" if index == 0 else "contract_failure" if index == 1 else "ok"}
        metrics, _ = evaluate.score_method(gold, baselines, proposals, "full_deltarev", .5, "dev")
        self.assertEqual(metrics["parse_failure_count"], 1)
        self.assertEqual(metrics["contract_failure_count"], 1)
        self.assertEqual(metrics["missing_count"], 0)
        self.assertEqual(metrics["baseline_correct_preserved_correct"], 0)

    def test_failed_residual_is_not_counted_as_revision_coverage(self):
        gold, baselines, proposals = self.fixture()
        for proposal in proposals.values():
            proposal["status"] = "contract_failure"
        metrics, _ = evaluate.score_method(gold, baselines, proposals, "full_deltarev", .5, "test")
        self.assertEqual(metrics["revision_coverage"], 0.0)
        self.assertEqual(metrics["answer_change_coverage"], 0.0)

    def test_shuffle_mapping_is_stable_and_never_self(self):
        pairs = [{"pair_id": f"p{index}", "split": "dev"} for index in range(3)]
        first = run.shuffle_source_map(pairs)
        second = run.shuffle_source_map(list(reversed(pairs)))
        self.assertEqual(first, second)
        self.assertTrue(all(target != source for target, source in first.items()))

    def test_merge_rejects_conflicting_shards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); a, b, out = root / "a", root / "b", root / "out"
            a.write_text('{"pair_id":"p","value":1}\n'); b.write_text('{"pair_id":"p","value":2}\n')
            with self.assertRaises(ValueError):
                run.merge_jsonl([a, b], out, ("pair_id",))

    def test_merge_normalizes_only_missing_retrieval_and_rule_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_retrieval = root / "old_retrieval"
            new_retrieval = root / "new_retrieval"
            retrieval_out = root / "retrieval_out"
            kept_error = [{"method": "shuffled_delta", "query_index": 0,
                           "query": "q", "error": "0 hits"}]
            old_retrieval.write_text(
                json.dumps({"pair_id": "p1", "artifact_type": "base",
                            "results": {"standard_question_retrieval": [],
                                        "ea_rag_style_retrieval": []}}) + "\n" +
                json.dumps({"pair_id": "p1", "artifact_type": "shuffled_delta", "results": []}) + "\n")
            new_retrieval.write_text(
                json.dumps({"pair_id": "p2", "artifact_type": "base", "results": {},
                            "errors": {"standard_question_retrieval": kept_error}}) + "\n" +
                json.dumps({"pair_id": "p2", "artifact_type": "shuffled_delta", "results": [],
                            "errors": kept_error}) + "\n")
            run.merge_jsonl([old_retrieval, new_retrieval], retrieval_out,
                            ("pair_id", "artifact_type"), "retrieval")
            rows = {(row["pair_id"], row["artifact_type"]): row
                    for row in run.read_jsonl(retrieval_out)}
            self.assertEqual(rows[("p1", "base")]["errors"], {
                "standard_question_retrieval": [], "ea_rag_style_retrieval": []})
            self.assertEqual(rows[("p1", "shuffled_delta")]["errors"], [])
            self.assertEqual(rows[("p2", "base")]["errors"],
                             {"standard_question_retrieval": kept_error})
            self.assertEqual(rows[("p2", "shuffled_delta")]["errors"], kept_error)

            old_rules, new_rules, rules_out = root / "old_rules", root / "new_rules", root / "rules_out"
            old_rules.write_text('{"pair_id":"p1","retrieval_method":"standard"}\n')
            new_rules.write_text(json.dumps({"pair_id": "p2", "retrieval_method": "standard",
                                             "retrieval_errors": kept_error}) + "\n")
            run.merge_jsonl([old_rules, new_rules], rules_out,
                            ("pair_id", "retrieval_method"), "rules")
            rules = {row["pair_id"]: row for row in run.read_jsonl(rules_out)}
            self.assertEqual(rules["p1"]["retrieval_errors"], [])
            self.assertEqual(rules["p2"]["retrieval_errors"], kept_error)

    def test_proposal_merge_recomputes_exact_dependency_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); raw = root / "raw_proposals.jsonl"; merged = root / "merged.jsonl"
            methods = ("decomposition_only", "without_delta", "shuffled_delta",
                       "shuffled_rule_evidence", "kgcc_generated_docs_as_decisive_evidence",
                       "standard_question_retrieval", "evidence_verifier_with_standard_retrieval",
                       "ea_rag_style_retrieval", "evidence_verifier_with_ea_rag_retrieval",
                       "candidate_specific_retrieval", "delta_only_retrieval",
                       "triangular_decision_change_retrieval", "full_deltarev",
                       "without_alternative_support_requirement", "without_entailment_check",
                       "without_patient_applicability_check", "refute_only_retrieval",
                       "without_baseline_answer_in_query", "without_preserve_evidence")
            proposals = []
            for pair_id in ("p1", "p2"):
                for method in methods:
                    details = {"stage_failures": []}
                    if method == "candidate_specific_retrieval":
                        details["stage_failures"] = ["hypotheses"]
                    if method == "full_deltarev" and pair_id == "p1":
                        details["stage_failures"] = ["relevance"]
                    if method == "without_delta" and pair_id == "p1":
                        details["stage_failures"] = ["hybrid_delta", "without_delta_relevance"]
                    if method == "shuffled_delta" and pair_id == "p1":
                        details["stage_failures"] = ["hybrid_delta", "shuffled_relevance"]
                    if method == "standard_question_retrieval" and pair_id == "p1":
                        details["stage_failures"] = ["retrieval"]
                    if method == "decomposition_only" and pair_id == "p1":
                        details.update({"usage": {"contract_failure": True},
                                        "control_usage": {"contract_failure": False}})
                    proposals.append({"pair_id": pair_id, "method": method, "status": "ok",
                                      "details": details})
            raw.write_text("".join(json.dumps(row) + "\n" for row in proposals))
            def usage(failure=False):
                return {"contract_failure": failure}
            deltas = [{"pair_id": pair_id, "usage": {"hybrid": usage(True)}} for pair_id in ("p1", "p2")]
            retrieval_error = lambda method: [{"method": method, "query_index": 0,
                                                "query": "q", "error": "0 hits"}]
            retrievals = [
                {"pair_id": "p1", "artifact_type": "base", "errors": {
                    method: retrieval_error(method) for method in (
                        "standard_question_retrieval", "candidate_specific_retrieval",
                        "delta_only_retrieval", "triangular_decision_change_retrieval",
                        "refute_only_retrieval", "without_baseline_answer_in_query",
                        "without_preserve_evidence")}},
                {"pair_id": "p2", "artifact_type": "base", "errors": {}},
                {"pair_id": "p1", "artifact_type": "shuffled_delta", "source_pair_id": "p2",
                 "errors": retrieval_error("shuffled_delta")},
                {"pair_id": "p2", "artifact_type": "shuffled_delta", "source_pair_id": "p1"},
            ]
            rules = []
            for pair_id in ("p1", "p2"):
                for method in ("standard_question_retrieval", "shuffled_delta",
                               "shuffled_rule_evidence", "kgcc_generated_decisive",
                               "triangular_decision_change_retrieval"):
                    fail = pair_id == "p1"
                    rules.append({"pair_id": pair_id, "retrieval_method": method,
                                  "usage": {"extractor": usage(fail), "verifier": usage(fail)}})
            for path, values in ((root / "deltas.jsonl", deltas),
                                 (root / "retrieval.jsonl", retrievals),
                                 (root / "rules.jsonl", rules)):
                path.write_text("".join(json.dumps(row) + "\n" for row in values))
            run.merge_proposals([raw], merged)
            rows = {(row["pair_id"], row["method"]): row for row in run.read_jsonl(merged)}
            expected = {
                "decomposition_only": ["hybrid_delta", "hypotheses", "decomposition"],
                "without_delta": ["hypotheses", "without_delta_relevance",
                                  "standard_retrieval", "standard_rule_extraction", "standard_verification"],
                "shuffled_delta": ["hypotheses", "donor_hybrid_delta", "shuffled_retrieval",
                                   "shuffled_relevance", "shuffled_rule_extraction", "shuffled_verification"],
                "shuffled_rule_evidence": ["hypotheses", "relevance", "donor_hybrid_delta",
                                            "donor_hypotheses", "shuffled_evidence_verification"],
                "kgcc_generated_docs_as_decisive_evidence": ["hybrid_delta", "hypotheses", "relevance",
                                                              "kgcc_rule_extraction", "kgcc_verification"],
            }
            for method, failures in expected.items():
                self.assertEqual(rows[("p1", method)]["details"]["stage_failures"], failures)
                self.assertEqual(rows[("p1", method)]["status"], "contract_failure")
            self.assertEqual(
                rows[("p2", "shuffled_rule_evidence")]["details"]["stage_failures"],
                ["hypotheses", "donor_hybrid_delta", "donor_hypotheses",
                 "donor_triangular_retrieval", "donor_triangular_rule_extraction"])
            for method in ("standard_question_retrieval", "evidence_verifier_with_standard_retrieval",
                           "ea_rag_style_retrieval", "evidence_verifier_with_ea_rag_retrieval",
                           "candidate_specific_retrieval", "delta_only_retrieval",
                           "triangular_decision_change_retrieval", "full_deltarev",
                           "without_alternative_support_requirement", "without_entailment_check",
                           "without_patient_applicability_check", "refute_only_retrieval",
                           "without_baseline_answer_in_query", "without_preserve_evidence"):
                self.assertEqual(rows[("p1", method)]["status"], "contract_failure")
            self.assertEqual(rows[("p1", "standard_question_retrieval")]["details"]["stage_failures"],
                             ["standard_question_retrieval"])
            self.assertNotEqual(raw.read_text(), merged.read_text())

    def test_proposal_merge_requires_sibling_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "raw_proposals.jsonl"
            raw.write_text('{"pair_id":"p","method":"full_deltarev"}\n')
            with self.assertRaises(ValueError):
                run.merge_proposals([raw], Path(directory) / "merged.jsonl")

    def test_evaluator_writes_thresholded_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); gold_path = root / "gold"; baseline_path = root / "baseline"
            proposal_path = root / "proposals"; delta_path = root / "deltas"
            retrieval_path = root / "retrieval"; rule_path = root / "rules"; output = root / "results"
            gold, baselines, proposals, deltas, retrievals, rules = [], [], [], [], [], []
            for index in range(200):
                pair_id = f"p{index}"; split = "dev" if index < 40 else "test"
                gold.append({"pair_id": pair_id, "split": split, "control_answer": "old", "trap_answer": "new"})
                baselines.append({"pair_id": pair_id, "members": {
                    "control": {"baseline_answer": "old"}, "trap": {"baseline_answer": "old"}}})
                for method in ("full_deltarev", "always_preserve", "medrgag_proxy"):
                    proposals.append({"pair_id": pair_id, "method": method, "baseline_answer": "old",
                                      "proposed_answer": "new" if method == "full_deltarev" else "old",
                                      "verifier_score": .9, "gate_without_threshold": method == "full_deltarev",
                                      "status": "ok", "control_prediction": None})
                proposals.append({"pair_id": pair_id, "method": "without_nice", "baseline_answer": "old",
                                  "proposed_answer": None, "verifier_score": None,
                                  "gate_without_threshold": False, "status": "unavailable",
                                  "control_prediction": None})
                deltas.append({"pair_id": pair_id,
                               "deterministic": {"changed_variables": [{}]},
                               "llm_only": {"changed_variables": [{}]},
                               "hybrid": {"changed_variables": [{}]},
                               "usage": {"llm": {"contract_failure": False, "retry_count": 0},
                                         "hybrid": {"contract_failure": False, "retry_count": 1}}})
                documents = [{"id": f"D{number}"} for number in range(10)]
                retrievals.extend([
                    {"pair_id": pair_id, "artifact_type": "base",
                     "results": {method: documents for method in evaluate.RETRIEVAL_METHODS},
                     "errors": {method: [] for method in evaluate.RETRIEVAL_METHODS},
                     "ea_rag_style": {"coverage_audit": [{"covered": True}]}},
                    {"pair_id": pair_id, "artifact_type": "shuffled_delta",
                     "results": documents, "errors": []},
                ])
                for method in evaluate.RULE_METHODS:
                    usage = {"verifier": {"calls": 1, "contract_failure": False, "retry_count": 0}}
                    if method != "shuffled_rule_evidence":
                        usage["extractor"] = {"calls": 1, "contract_failure": False, "retry_count": 0}
                    rules.append({"pair_id": pair_id, "retrieval_method": method,
                                  "rules": [{"rule_id": "R0"}],
                                  "verifications": [{"rule_id": "R0"}], "usage": usage})
            for path, rows in ((gold_path, gold), (baseline_path, baselines), (proposal_path, proposals),
                               (delta_path, deltas), (retrieval_path, retrievals), (rule_path, rules)):
                path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            metrics = evaluate.evaluate(gold_path, baseline_path, proposal_path, delta_path,
                                        retrieval_path, rule_path, output, 100)
            self.assertEqual(metrics["methods"]["full_deltarev"]["test"]["repairs"], 160)
            self.assertEqual(metrics["strict_operating_point_test"]["repairs"], 160)
            self.assertEqual(metrics["primary_operating_point_test"]["repairs"], 160)
            self.assertIn("revision_coverage", metrics["primary_operating_point_test"])
            self.assertIn("answer_change_coverage", metrics["strict_operating_point_test"])
            self.assertIn("availability_notes", metrics)
            self.assertEqual(metrics["artifact_diagnostics"]["delta_rows"], 200)
            self.assertEqual(metrics["artifact_diagnostics"]["retrieval_rows"], 400)
            self.assertEqual(metrics["artifact_diagnostics"]["rule_rows"], 2200)
            self.assertEqual(metrics["artifact_diagnostics"]["delta"]["hybrid"]["retry_rate"], 1.0)
            self.assertEqual(metrics["artifact_diagnostics"]["delta"]["llm_only"]
                             ["contract_failure_count"], 0)
            self.assertEqual(metrics["artifact_diagnostics"]["rules"]["overall"]
                             ["extractor_applicable_rows"], 2000)
            self.assertEqual(metrics["artifact_diagnostics"]["rules"]["overall"]
                             ["verifier_applicable_rows"], 2200)
            self.assertEqual(metrics["artifact_diagnostics"]["retrieval"]
                             ["ea_rag_style_retrieval"]["coverage_audit_proxy_covered_rate"], 1.0)
            self.assertTrue(metrics["hypothesis_supported"])
            predictions = evaluate.read_jsonl(output / "predictions.jsonl")
            self.assertEqual(len(predictions), 800)
            unavailable = [row for row in predictions if row["method"] == "without_nice"]
            self.assertEqual(len(unavailable), 200)
            self.assertTrue(all(row["status"] == "unavailable" and row["final_answer"] is None
                                and row["decision"] == "UNAVAILABLE" for row in unavailable))
            self.assertEqual(metrics["unavailable_prediction_rows"], {"without_nice": 200})
            self.assertFalse(metrics["evaluation_policy"]["clinical_equivalence_rescoring"])
            self.assertIn("strict normalized exact match", metrics["evaluation_policy"]["answer_matching"])
            self.assertIn("gate_passed", predictions[0])
            self.assertIn("stage_failures", predictions[0])
            self.assertTrue((output / "tradeoff.csv").exists())
            csv_header = (output / "metrics.csv").read_text().splitlines()[0]
            for field in ("error_correction_rate", "correct_change", "old_answer_persistence",
                          "baseline_correct_preserved_correct", "parse_failure_count",
                          "contract_failure_count", "missing_control_prediction_count"):
                self.assertIn(field, csv_header)
            summary = (output / "summary.md").read_text()
            self.assertIn("At the <=2% dev-budget threshold", summary)
            self.assertIn("## Main test metrics", summary)
            self.assertIn("## Ablation diagnostics", summary)
            self.assertIn("## Paired bootstrap comparisons", summary)
            self.assertIn("Threshold comparison is inclusive", summary)
            self.assertIn("## Gold-label oracle gate diagnostic (outside the main table)", summary)
            self.assertIn("Atomic-rule extraction contract failure", summary)
            self.assertIn("three-way delta-quality comparison is not valid", summary)
            self.assertIn("strict normalized exact match", summary)
            self.assertIn("no post-hoc rescoring", summary)
            self.assertIn("fail-closed preservation, not successful mechanism evidence", summary)
            self.assertIn("null ablation effects non-informative", summary)
            self.assertIn("## Limitations and expansion decision", summary)
            self.assertIn("coverage/contract diagnostics only", summary)

    def test_artifact_diagnostics_fail_on_incomplete_pair_coverage(self):
        with self.assertRaises(ValueError):
            evaluate.artifact_diagnostics({"p"}, [], [], [], [])


if __name__ == "__main__":
    unittest.main()
