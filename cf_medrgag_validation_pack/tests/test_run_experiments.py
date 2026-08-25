import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_experiments.py"
SPEC = importlib.util.spec_from_file_location("run_experiments", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(runner)


class Tokenizer:
    def encode(self, text, add_special_tokens=False): return list(text.encode())
    def decode(self, tokens, skip_special_tokens=True): return bytes(tokens).decode(errors="ignore")
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        return "\n".join(row["content"] for row in messages)


class Backend:
    tokenizer = Tokenizer()
    def __init__(self): self.prompts = []
    def generate(self, prompts, max_tokens, **kwargs):
        self.prompts.extend(prompts)
        rows = []
        for prompt in prompts:
            if "Extract only facts visible" in prompt:
                value = {"current_state_summary": "state", "fixed_action": "drug", "candidate_hypotheses": [], "uncertainties": []}
            elif "Predict an action-conditioned" in prompt:
                value = {
                    "current_state_summary": "state", "action": "x", "satisfied_preconditions": [],
                    "failed_preconditions": [], "expected_observations": ["lower value"],
                    "expected_state_changes": [], "contraindications_or_harms": [],
                    "monitoring_or_next_step": [], "uncertainties": [],
                }
                if "claim_grounding" in prompt:
                    value["claim_grounding"] = [{"claim": "lower value", "evidence_ids": ["BAD"], "support": "entailed"}]
            elif "Required output: {\"answer_choices\"" in prompt:
                value = {"answer_choices": ["A"], "reasoning": "r", "supporting_evidence_ids": []}
            elif "evidence_conditioned_answer" in prompt:
                value = {"evidence_conditioned_answer": "higher", "real_world_safety_flag": "uncertain", "reasoning": "fixed evidence", "supporting_evidence_ids": []}
            elif "Return ranking, selected" in prompt:
                value = {"ranking": ["A", "B"], "selected": ["A"], "reasoning": "r", "supporting_evidence_ids": []}
            elif "current-state compatibility" in prompt:
                value = {
                    "candidate_factors": [
                        {
                            "candidate_id": candidate_id,
                            "current_state_compatibility": "compatible",
                            "evidence_relevance": "relevant",
                            "guideline_applicability": "applicable",
                            "contradictions": "none",
                        }
                        for candidate_id in ("A", "B")
                    ],
                    "summary": "present state only",
                }
            elif "present-state compatibility" in prompt:
                value = {"present_state_compatibility": "compatible", "evidence_relevance": "relevant", "contradictions": [], "analysis": "r"}
            elif "cross_candidate_observations" in prompt:
                value = {"candidate_factors": [{"candidate_id": "A"}, {"candidate_id": "B"}], "cross_candidate_observations": []}
            elif "answer_choices" in prompt:
                value = {"answer_choices": ["A"], "reasoning": "r", "supporting_evidence_ids": []}
            else:
                value = {"answer_choice": "B", "reasoning": "r", "supporting_evidence_ids": []}
            raw = json.dumps(value)
            rows.append({"raw_response": raw, "prompt_tokens": len(prompt), "completion_tokens": len(raw), "finish_reason": "stop"})
        return rows


class Retriever:
    def retrieve(self, query, count):
        return [{"id": str(i), "contents": f"evidence {i}"} for i in range(count)]


class RevisedRunnerTest(unittest.TestCase):
    def test_medeinst_reader_rejects_schema_placeholder(self):
        class DiagnosisReaderBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                answer = "concise diagnosis" if len(self.prompts) == 1 else "Pneumonia"
                value = {"open_answer": answer, "reasoning": "Pneumonia best fits.", "supporting_evidence_ids": []}
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        backend = DiagnosisReaderBackend()
        parsed, usage = runner.answer_with(
            {"item_id": "dx", "dataset": "medeinst", "question": "Diagnosis?", "options": None},
            "direct", [], {}, backend, 10000, 128,
        )
        self.assertEqual(parsed["open_answer"], "Pneumonia")
        self.assertEqual(usage["retry_count"], 1)
        self.assertIn("never copy the schema placeholder", backend.prompts[1])

    def test_reader_output_exact_alias_normalization(self):
        medpic = {
            "dataset": "medpic",
            "options": {"A": "None of the above", "D": "Duloxetine"},
        }
        parsed = runner.normalize_reader_output(
            medpic, {"answer_choices": ["Duloxetine", "A"]},
        )
        self.assertEqual(parsed["answer_choices"], ["D", "A"])

        mcf = runner.normalize_reader_output(
            {"dataset": "medcounterfact"},
            {"evidence_conditioned_answer": "no difference", "real_world_safety_flag": "no difference"},
        )
        self.assertEqual(mcf["evidence_conditioned_answer"], "no difference")
        self.assertEqual(mcf["real_world_safety_flag"], "uncertain")
        self.assertTrue(mcf["safety_parse_failure"])

    def test_last_json_repairs_only_one_missing_outer_brace(self):
        self.assertEqual(runner.last_json('prefix {"a": 1'), {"a": 1})
        self.assertIsNone(runner.last_json('{"a": 1 // comment'))

    def test_router_and_option_hidden_transition(self):
        item = {"item_id": "c", "dataset": "clir", "task_family": "intervention_response", "question": "After insulin, what occurs?", "options": {"A": "secret A", "B": "secret B"}, "time_series": []}
        self.assertEqual(runner.task_mode(item), "outcome_prediction")
        self.assertNotIn("secret A", runner.state_prompt(item))
        state = {"fixed_action": "insulin"}
        prompt = runner.transition_prompt(item, state, {"id": "FIXED", "text": "insulin"}, [], False)
        self.assertNotIn("secret A", prompt)
        self.assertIn("Outcome options hidden: true", prompt)
        medpic = {"item_id": "p", "dataset": "medpic", "question": "Choose", "options": {"A": "alpha", "B": "beta"}}
        self.assertNotIn("alpha", runner.state_prompt(medpic))

        real_t6 = {**item, "fixed_evidence": [{"baseline_observation": {"value": 96}, "post_observations": [{"value": 99}], "intervention_event_hour": 3, "response_variable": "spo2"}]}
        context = runner.prediction_context(real_t6)
        self.assertIn("baseline_observation", context)
        self.assertNotIn("post_observations", context)
        self.assertNotIn("99", context)

        t7 = {**item, "task_family": "threshold_forecasting", "fixed_evidence": [{"future": "leak"}]}
        context = runner.prediction_context(t7)
        self.assertIn('"patient_evidence_available": false', context)
        self.assertNotIn("leak", context)

        t8 = {**item, "task_family": "next_value_interval_forecasting", "fixed_evidence": [{"anchor_time": 10.57, "horizon_hours": 8, "previous_same_variable_observation": {"hour": 10.5, "value": 16}, "recent_visible_same_variable_observations": [{"hour": 9.5, "value": 24}], "target_variable": "resp_rate", "target_variable_label": "respiratory rate", "answer_interval": "leak"}]}
        context = runner.prediction_context(t8)
        self.assertIn("anchor_time", context)
        self.assertIn("previous_same_variable_observation", context)
        self.assertIn("recent_visible_same_variable_observations", context)
        self.assertIn("target_variable_label", context)
        self.assertNotIn("answer_interval", context)
        self.assertTrue(runner.excluded_clir_t9({**item, "task_family": "clinical_timeseries_summarization"}))

        mcf = {"item_id": "f", "dataset": "medcounterfact", "question": "effect?", "fixed_evidence": ["local"]}
        self.assertEqual(runner.candidate_actions(mcf, {}), [{"id": "FIXED", "text": "interpret the supplied local evidence world"}])
        mcf["question"] = "Is mortality higher, lower, or the same with treatment?"
        self.assertNotIn("higher, lower", runner.inference_stem(mcf).lower())
        mcf["question"] = "Is the effect lower, higher, or the same with treatment?"
        self.assertNotIn("lower, higher", runner.inference_stem(mcf).lower())
        backend = Backend()
        state, usage = runner.build_state(mcf, backend, 10000)
        self.assertEqual(state["fixed_action"], "interpret the supplied local evidence world")
        self.assertEqual(usage["total_tokens"], 0)
        self.assertEqual(backend.prompts, [])

    def test_invalid_citations_are_not_fabricated(self):
        raw = {key: [] for key in runner.TRANSITION_KEYS}
        raw.update({"action": "x", "current_state_summary": "s", "expected_observations": ["one effect"], "claim_grounding": [{"claim": "c", "evidence_ids": ["BAD"], "support": "entailed"}, "uncited claim"]})
        card = runner.normalize_card(raw, {"id": "A", "text": "x"}, [{"id": "D1", "text": "doc"}])
        self.assertEqual(card["expected_observations"], ["one effect"])
        self.assertEqual(card["evidence_ids"], [])
        self.assertEqual(card["claim_grounding"][0]["support"], "not_supported")
        self.assertIn({"claim": "uncited claim", "evidence_ids": [], "support": "not_supported"}, card["claim_grounding"])
        self.assertEqual(card["grounding_status"], "unsupported")
        reader = {"supporting_evidence_ids": ["BAD", "D1"]}
        runner.validate_reader_citations(reader, [{"id": "D1", "text": "doc"}])
        self.assertEqual(reader["supporting_evidence_ids"], ["D1"])

    def test_transition_leakage_gets_the_single_repair(self):
        class RepairBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                leaked = len(self.prompts) == 1
                value = {
                    "current_state_summary": "state", "action": "x",
                    "satisfied_preconditions": [], "failed_preconditions": [],
                    "expected_observations": ["the correct answer" if leaked else "neutral effect"],
                    "expected_state_changes": [], "contraindications_or_harms": [],
                    "monitoring_or_next_step": [], "uncertainties": [], "claim_grounding": [],
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]
        cards, usage = runner.make_cards(
            {"item_id": "x", "dataset": "medpic", "question": "q", "options": {"A": "a"}},
            {}, {"A": []}, RepairBackend(), 10000,
        )
        self.assertEqual(cards[0]["expected_observations"], ["neutral effect"])
        self.assertEqual(usage["retry_count"], 1)

    def test_transition_schema_repair_receives_exact_shape(self):
        class SchemaRepairBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if len(self.prompts) == 1:
                    value = {"current_state_summary": "incomplete"}
                else:
                    self_test = self.prompts[-1]
                    for key in (*runner.TRANSITION_KEYS, "claim_grounding"):
                        self.assert_key = f'"{key}"' in self_test
                        if not self.assert_key:
                            raise AssertionError(f"repair prompt omitted {key}")
                    value = {key: [] for key in runner.TRANSITION_KEYS}
                    value.update({"current_state_summary": "state", "action": "x", "claim_grounding": []})
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]
        cards, usage = runner.make_cards(
            {"item_id": "x", "dataset": "medpic", "question": "q", "options": {"A": "a"}},
            {}, {"A": []}, SchemaRepairBackend(), 10000,
        )
        self.assertEqual(len(cards), 1)
        self.assertEqual(usage["retry_count"], 1)

    def test_grounded_card_repairs_truncated_long_claims_compactly(self):
        class LongGroundingBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if len(self.prompts) == 1:
                    raw = (
                        '{"current_state_summary":"state","action":"spray","satisfied_preconditions":[],'
                        '"failed_preconditions":[],"expected_observations":[],"expected_state_changes":[],'
                        '"contraindications_or_harms":[],"monitoring_or_next_step":[],"uncertainties":[],'
                        '"claim_grounding":[{"claim":"' + ("malaria LLIN and IRS detail " * 300)
                    )
                else:
                    value = {key: [] for key in runner.TRANSITION_ARRAY_KEYS}
                    value.update({
                        "current_state_summary": "malaria-exposed population",
                        "action": "spray",
                        "satisfied_preconditions": ["Malaria exposure is present."],
                        "failed_preconditions": ["One implementation condition is unknown."],
                        "expected_observations": ["Vector exposure may decline."],
                        "contraindications_or_harms": ["Implementation harms remain uncertain."],
                        "monitoring_or_next_step": ["Monitor malaria incidence."],
                        "claim_grounding": [
                            {"claim": "Malaria exposure is present.", "evidence_ids": ["D1"], "support": "entailed"},
                            {"claim": "One implementation condition is unknown.", "evidence_ids": [], "support": "not_supported"},
                            {"claim": "Vector exposure may decline.", "evidence_ids": ["D1"], "support": "entailed"},
                            {"claim": "Implementation harms remain uncertain.", "evidence_ids": [], "support": "not_supported"},
                            {"claim": "Monitor malaria incidence.", "evidence_ids": ["D1"], "support": "entailed"},
                        ],
                    })
                    raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "length"}]

        backend = LongGroundingBackend()
        cards, usage = runner.make_cards(
            {"item_id": "long-grounding", "dataset": "medpic", "question": "Choose", "options": {"A": "spray"}},
            {}, {"A": [{"id": "D1", "text": "Malaria exposure and vector-control evidence."}]},
            backend, 10000,
        )
        self.assertIn("at most eight short statements", backend.prompts[0])
        self.assertIn("at most four total short", backend.prompts[1])
        self.assertIn("Discard extra detail", backend.prompts[1])
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(sum(len(cards[0][key]) for key in runner.TRANSITION_ARRAY_KEYS), 5)
        self.assertEqual(len(cards[0]["claim_grounding"]), 5)

    def test_grounded_card_keeps_legacy_valid_first_response_without_repair(self):
        class LegacyGroundedBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {key: [] for key in runner.TRANSITION_ARRAY_KEYS}
                value.update({
                    "current_state_summary": "state", "action": "action",
                    "expected_observations": [f"legacy detail {index}" for index in range(5)],
                    "claim_grounding": [
                        {"claim": f"legacy detail {index}", "evidence_ids": [], "support": "not_supported"}
                        for index in range(5)
                    ],
                })
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        backend = LegacyGroundedBackend()
        cards, usage = runner.make_cards(
            {"item_id": "legacy-grounding", "dataset": "medpic", "question": "Choose", "options": {"A": "action"}},
            {}, {"A": []}, backend, 10000,
        )
        self.assertEqual(usage["retry_count"], 0)
        self.assertEqual(len(backend.prompts), 1)
        self.assertEqual(len(cards[0]["expected_observations"]), 5)

    def test_teacher_contract_does_not_trust_self_reported_grounding(self):
        class TeacherBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {key: [] for key in runner.TRANSITION_KEYS}
                value.update({"current_state_summary": "state", "action": "x"})
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]
        cards, usage = runner.make_cards(
            {"item_id": "x", "dataset": "medpic", "question": "q", "options": {"A": "a"}},
            {}, {"A": []}, TeacherBackend(), 10000, teacher=True,
        )
        self.assertEqual(usage["retry_count"], 0)
        self.assertNotIn("claim_grounding", cards[0])
        self.assertNotIn("claims", cards[0])
        self.assertEqual(cards[0]["grounding_status"], "not_assessed")

    def test_teacher_repairs_real_malformed_summary_shape(self):
        class MalformedTeacherBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if len(self.prompts) == 1:
                    raw = '{"current_state_summary": ["patient_age": 24], "action": "a", "satisfied_preconditions": [], "failed_preconditions": [], "expected_observations": [], "expected_state_changes": [], "contraindications_or_harms": [], "monitoring_or_next_step": [], "uncertainties": []}'
                else:
                    value = {key: [] for key in runner.TRANSITION_ARRAY_KEYS}
                    value.update({"current_state_summary": "24-year-old patient", "action": "a"})
                    raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        backend = MalformedTeacherBackend()
        cards, usage = runner.make_cards(
            {"item_id": "x", "dataset": "medpic", "question": "q", "options": {"A": "a"}},
            {}, {"A": []}, backend, 10000, teacher=True,
        )
        initial = backend.prompts[0]
        self.assertIn('"current_state_summary": "one short sentence"', initial)
        self.assertNotIn('"current_state_summary": [', initial)
        self.assertNotIn("claim_grounding", initial)
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(cards[0]["current_state_summary"], "24-year-old patient")
        self.assertNotIn("claim_grounding", cards[0])
        self.assertIn("most eight total statements", backend.prompts[1])
        self.assertNotIn("claim_grounding", backend.prompts[1])
        self.assertNotIn("Discard extra detail", backend.prompts[1])
        serialized = json.dumps(cards[0]).lower()
        self.assertNotIn("answer", serialized)
        self.assertNotIn("preferred", serialized)
        self.assertNotIn("selected", serialized)

    def test_mcf_reader_repairs_repeated_plain_text_to_compact_json(self):
        class RepeatedReaderBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if len(self.prompts) == 1:
                    raw = "The local evidence should be interpreted carefully. " * 300
                else:
                    raw = json.dumps({
                        "evidence_conditioned_answer": "same",
                        "real_world_safety_flag": "uncertain",
                        "reasoning": "This remains a schema-valid but deliberately verbose repaired explanation. " * 5,
                        "supporting_evidence_ids": ["D1"],
                    })
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "length"}]

        backend = RepeatedReaderBackend()
        parsed, usage = runner.answer_with(
            {"item_id": "mcf-reader", "dataset": "medcounterfact", "question": "Compare the groups."},
            "direct", [{"id": "D1", "text": "The local evidence reports lower mortality."}], {},
            backend, 10000, 256,
        )
        self.assertNotIn("Discard repeated or extra detail", backend.prompts[0])
        self.assertIn("Discard repeated or extra detail", backend.prompts[1])
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(parsed["evidence_conditioned_answer"], "same")
        self.assertGreater(len(parsed["reasoning"]), 240)

    def test_evidence_world_match_uses_question_and_repairs_dict_answer(self):
        class EvidenceWorldBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {
                    "evidence_conditioned_answer": {"conclusion": "same"} if len(self.prompts) == 1 else "same",
                    "real_world_safety_flag": "uncertain",
                    "reasoning": "The neutral conclusion indicates no difference.",
                    "supporting_evidence_ids": [],
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        item = {
            "item_id": "mcf-match", "dataset": "medcounterfact",
            "question": "Does the intervention change mortality?",
        }
        cards = [{
            "expected_observations": ["Mortality remains unchanged."],
            "expected_state_changes": [], "uncertainties": [], "claim_grounding": [], "evidence_ids": [],
        }]
        backend = EvidenceWorldBackend()
        parsed, usage = runner.evidence_world_match(item, cards, backend, 10000, 128)
        for prompt in backend.prompts:
            self.assertIn("Question: Does the intervention change mortality?", prompt)
            self.assertIn("Mortality remains unchanged.", prompt)
            self.assertNotRegex(prompt.lower(), r"\b(options?|gold|pair(?:_id)?)\b")
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(parsed["evidence_conditioned_answer"], "no difference")
        self.assertEqual(parsed["real_world_safety_flag"], "uncertain")

    def test_original_contracts_still_hard_fail_after_one_bad_repair(self):
        class WrongTransitionBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {key: [] for key in runner.TRANSITION_KEYS}
                value.update({"action": "a", "claim_grounding": []})
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        transition_backend = WrongTransitionBackend()
        with self.assertRaisesRegex(ValueError, "model failed JSON contract after one retry"):
            runner.make_cards(
                {"item_id": "wrong-card", "dataset": "medpic", "question": "Choose", "options": {"A": "a"}},
                {}, {"A": []}, transition_backend, 10000,
            )
        self.assertEqual(len(transition_backend.prompts), 2)

        class MissingReaderBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                raw = json.dumps({"reasoning": "missing required fields"})
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        reader_backend = MissingReaderBackend()
        with self.assertRaisesRegex(ValueError, "model failed JSON contract after one retry"):
            runner.answer_with(
                {"item_id": "wrong-reader", "dataset": "medcounterfact", "question": "Compare."},
                "direct", [], {}, reader_backend, 10000, 256,
            )
        self.assertEqual(len(reader_backend.prompts), 2)

    def test_equal_token_keeps_free_text_auxiliary_reasoning(self):
        class NestedBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if "Analyze only present-state" in prompts[0]:
                    raw = "Present-state conflict, with no future prediction."
                else:
                    value = {
                        "candidate_factors": [{
                            "candidate_id": "A",
                            "current_state_compatibility": "compatible",
                            "evidence_relevance": "relevant",
                            "guideline_applicability": "applicable",
                            "contradictions": "none",
                        }],
                        "summary": "present evidence only",
                    }
                    raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]
        block, _ = runner.equal_token_analysis(
            {"item_id": "x", "dataset": "medpic", "question": "q", "options": {"A": "a"}},
            {}, {"A": []}, NestedBackend(), 10000,
        )
        self.assertEqual(block["per_candidate_reasoning"][0]["analysis"], "Present-state conflict, with no future prediction.")

    def test_structured_factors_repair_accepts_required_legacy_shape(self):
        class HugeSummaryBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                if len(self.prompts) == 1:
                    raw = '{"candidate_factors": [], "summary": {"current_state": "' + "x" * 4000
                else:
                    rows = [{
                        "option": candidate_id,
                        "current_state_compatibility": "compatible",
                        "evidence_relevance": "relevant",
                        "guideline_applicability": "uncertain",
                        "contradictions": "none",
                    } for candidate_id in ("A", "B", "C", "D")]
                    raw = json.dumps({
                        "candidate_factors": rows,
                        "summary": {"analysis": "Present-state factors are mixed. " * 10},
                    })
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "length"}]

        item = {
            "item_id": "t8-real-shape", "dataset": "clir",
            "task_family": "next_value_interval_forecasting", "question": "Forecast the next interval.",
            "options": {"A": "0-5", "B": "6-10", "C": "11-15", "D": "16-20"},
        }
        backend = HugeSummaryBackend()
        factors, usage = runner.structured_factors(item, {"current_state_summary": "visible history"}, [], backend, 10000)
        repair_rule = backend.prompts[1].split("\n\n", 1)[0]
        self.assertIn('"summary": "one short sentence"', repair_rule)
        self.assertIn('"current_state_compatibility": "short scalar"', repair_rule)
        self.assertEqual(usage["retry_count"], 1)
        self.assertIsInstance(factors["summary"], dict)
        self.assertEqual({row["candidate_id"] for row in factors["candidate_factors"]}, {"A", "B", "C", "D"})
        self.assertTrue(all(set(row) == {
            "candidate_id", "current_state_compatibility", "evidence_relevance",
            "guideline_applicability", "contradictions",
        } for row in factors["candidate_factors"]))

    def test_structured_factors_keeps_legacy_valid_first_response_without_repair(self):
        class LegacyShapeBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {
                    "candidate_factors": [{"option": "A", "free_form_note": "legacy accepted shape"}],
                    "summary": {"current_state": "legacy structured summary"},
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        backend = LegacyShapeBackend()
        factors, usage = runner.structured_factors(
            {"item_id": "legacy", "dataset": "medpic", "question": "Choose", "options": {"A": "one"}},
            {}, [], backend, 10000,
        )
        self.assertEqual(usage["retry_count"], 0)
        self.assertEqual(len(backend.prompts), 1)
        self.assertEqual(factors["summary"], {"current_state": "legacy structured summary"})
        self.assertEqual(factors["candidate_factors"], [{"candidate_id": "A", "free_form_note": "legacy accepted shape"}])

    def test_shuffles_preserve_candidate_identity(self):
        cards = [
            {"candidate_id": "A", "action": "a", "satisfied_preconditions": ["pa"], "expected_observations": ["ea"], "evidence": [{"id": "D1", "text": "a"}], "claim_grounding": [{"claim": "pa", "evidence_ids": ["D1"]}, {"claim": "ea", "evidence_ids": ["D1"]}]},
            {"candidate_id": "B", "action": "b", "satisfied_preconditions": ["pb"], "expected_observations": ["eb"], "evidence": [{"id": "D2", "text": "b"}], "claim_grounding": [{"claim": "pb", "evidence_ids": ["D2"]}, {"claim": "eb", "evidence_ids": ["D2"]}]},
        ]
        effect = runner.shuffled(cards, "x", False)
        self.assertEqual(effect[0]["satisfied_preconditions"], ["pa"])
        self.assertEqual(effect[0]["expected_observations"], ["eb"])
        self.assertEqual([row["claim"] for row in effect[0]["claim_grounding"]], ["pa", "eb"])
        self.assertEqual({row["id"] for row in effect[0]["evidence"]}, {"D1", "D2"})
        full = runner.shuffled(cards, "x", True)
        self.assertEqual((full[0]["candidate_id"], full[0]["action"]), ("A", "a"))
        self.assertEqual(full[0]["satisfied_preconditions"], ["pb"])

    def test_comparator_drops_choice_fields(self):
        class ComparatorBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                value = {
                    "candidate_factors": [{"candidate_id": "A", "precondition_fit": "yes", "total": 1}],
                    "cross_candidate_observations": [], "selected_candidate_ids": ["A"], "ranking": ["A"],
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]
        factors, _ = runner.comparison_factors({"question": "q"}, {}, [], ComparatorBackend(), 10000)
        self.assertEqual(factors, {"candidate_factors": [{"candidate_id": "A", "precondition_fit": "yes"}], "cross_candidate_observations": []})

    def test_smoke_methods_and_no_selected_ids(self):
        item = {"item_id": "m", "dataset": "medpic", "question": "Which drug?", "options": {"A": "alpha", "B": "beta"}, "fixed_evidence": [], "time_series": []}
        backend = Backend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("direct_rank", "structured_no_transition", "equal_token_reasoning", "full_transition", "effect_shuffle", "full_card_shuffle", "teacher_transition"), root, backend, 20000, 256, Retriever())
            predictions = runner.read_jsonl(root / "predictions.jsonl")
            self.assertEqual(len(predictions), 7)
            self.assertTrue(all(row["prediction"] == ["A"] for row in predictions))
            comparator_prompts = [p for p in backend.prompts if "Compare the neutral cards" in p]
            self.assertTrue(comparator_prompts)
            self.assertTrue(all("selected_candidate_ids" not in p for p in comparator_prompts))
            cards = runner.read_jsonl(root / "cards.jsonl")
            self.assertEqual(len(cards), 4)
            for row in cards:
                expected = "not_assessed" if row["method"] == "teacher_transition" else "unsupported"
                self.assertTrue(all(card["grounding_status"] == expected for card in row["cards"]))

    def test_direct_rank_contract_failure_is_recorded_and_next_method_runs(self):
        class RankFailureBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    value = (
                        {"reasoning": "missing rank contract"}
                        if "direct medical option ranker" in prompt
                        else {"answer_choices": ["A"], "reasoning": "ok", "supporting_evidence_ids": []}
                    )
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {
            "item_id": "rank-failure", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("direct_rank", "direct"), root, RankFailureBackend(), 10000, 128, Retriever())
            rows = {row["method"]: row for row in runner.read_jsonl(root / "predictions.jsonl")}
        failed = rows["direct_rank"]
        self.assertIsNone(failed["prediction"])
        self.assertTrue(failed["parse_failure"])
        self.assertTrue(failed["reader_output"]["parse_failure"])
        self.assertEqual(failed["reader_output"]["error_stage"], "direct_rank")
        self.assertEqual(failed["reader_output"]["supporting_evidence_ids"], [])
        self.assertEqual(failed["supporting_evidence_ids"], [])
        self.assertEqual(failed["evidence_ids"], [])
        self.assertEqual(rows["direct"]["prediction"], ["A"])

    def test_direct_rank_keeps_answer_when_citation_ids_are_numeric(self):
        class NumericCitationBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {
                    "ranking": ["A", "B"], "selected": ["A"], "reasoning": "ranked",
                    "supporting_evidence_ids": [123],
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        item = {
            "item_id": "numeric-citation", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        backend = NumericCitationBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("direct_rank",), root, backend, 10000, 128, Retriever())
            row = runner.read_jsonl(root / "predictions.jsonl")[0]
        self.assertEqual(row["prediction"], ["A"])
        self.assertEqual(row["reader_output"]["supporting_evidence_ids"], [])
        self.assertEqual(row["evidence_ids"], [])
        self.assertEqual(row["token_usage"]["reader"]["retry_count"], 0)

    def test_effect_shuffle_comparison_failure_keeps_cards_and_continues(self):
        class ComparisonFailureBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "Extract only facts visible" in prompt:
                        value = {"current_state_summary": "state", "fixed_action": "", "candidate_hypotheses": [], "uncertainties": []}
                    elif "Predict an action-conditioned" in prompt:
                        value = {key: [] for key in runner.TRANSITION_ARRAY_KEYS}
                        value.update({"current_state_summary": "state", "action": "candidate", "claim_grounding": []})
                    elif "compare transition information without choosing an answer" in prompt:
                        value = {"candidate_factors": []}
                    else:
                        value = {"answer_choices": ["A"], "reasoning": "ok", "supporting_evidence_ids": []}
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {
            "item_id": "comparison-failure", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        backend = ComparisonFailureBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("effect_shuffle", "direct"), root, backend, 10000, 128, Retriever())
            runner.run([item], ("effect_shuffle", "direct"), root, backend, 10000, 128, Retriever())
            predictions = {row["method"]: row for row in runner.read_jsonl(root / "predictions.jsonl")}
            card_rows = runner.read_jsonl(root / "cards.jsonl")
        failed = predictions["effect_shuffle"]
        self.assertIsNone(failed["prediction"])
        self.assertEqual(failed["reader_output"]["error_stage"], "transition_comparison")
        self.assertTrue(failed["parse_failure"])
        self.assertEqual(len(failed["transition"]), 2)
        self.assertEqual(predictions["direct"]["prediction"], ["A"])
        self.assertEqual(len(card_rows), 1)
        self.assertEqual(card_rows[0]["method"], "effect_shuffle")

    def test_transition_generation_failure_writes_one_empty_card_row(self):
        class TransitionFailureBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "Extract only facts visible" in prompt:
                        value = {"current_state_summary": "state", "fixed_action": "", "candidate_hypotheses": [], "uncertainties": []}
                    elif "neutral clinical transition predictor" in prompt:
                        value = {"current_state_summary": []}
                    else:
                        value = {"answer_choices": ["A"], "reasoning": "ok", "supporting_evidence_ids": []}
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {
            "item_id": "generation-failure", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        backend = TransitionFailureBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("full_transition", "direct"), root, backend, 10000, 128, Retriever())
            runner.run([item], ("full_transition", "direct"), root, backend, 10000, 128, Retriever())
            predictions = {row["method"]: row for row in runner.read_jsonl(root / "predictions.jsonl")}
            card_rows = runner.read_jsonl(root / "cards.jsonl")
        failed = predictions["full_transition"]
        self.assertIsNone(failed["prediction"])
        self.assertEqual(failed["reader_output"]["error_stage"], "transition_generation")
        self.assertEqual(predictions["direct"]["prediction"], ["A"])
        self.assertEqual(len(card_rows), 1)
        self.assertEqual(card_rows[0]["cards"], [])
        self.assertTrue(card_rows[0]["parse_failure"])
        self.assertEqual(card_rows[0]["error_stage"], "transition_generation")
        self.assertIn("error", card_rows[0])
        self.assertIn("total_tokens", card_rows[0]["token_usage"])

    def test_shared_state_failure_records_dependents_and_continues_shard(self):
        class SharedStateFailureBackend(Backend):
            def __init__(self):
                super().__init__()
                self.state_calls = 0

            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    is_state = "You extract medical benchmark state" in prompt
                    if is_state:
                        self.state_calls += 1
                    if is_state and "MedEinst state failure" in prompt:
                        value = {
                            "current_state_summary": "broken state", "fixed_action": "",
                            "candidate_hypotheses": ["Pneumonia"] * 5, "uncertainties": [],
                        }
                        raw = json.dumps(value)
                        rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                    elif 'Required output: {"open_answer"' in prompt:
                        raw = json.dumps({"open_answer": "Pneumonia", "reasoning": "answered", "supporting_evidence_ids": []})
                        rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                    else:
                        rows.extend(Backend().generate([prompt], max_tokens))
                return rows

        failed_item = {
            "item_id": "state-fail", "dataset": "medeinst",
            "question": "MedEinst state failure", "options": None, "fixed_evidence": [],
        }
        next_item = {
            "item_id": "next-item", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        documents = {"state-fail": [], "next-item": []}
        backend = SharedStateFailureBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run(
                [failed_item, next_item], runner.METHODS, root, backend, 10000, 128,
                Retriever(), documents,
            )
            first_predictions = runner.read_jsonl(root / "predictions.jsonl")
            first_cards = runner.read_jsonl(root / "cards.jsonl")
            runner.run(
                [failed_item, next_item], runner.METHODS, root, backend, 10000, 128,
                Retriever(), documents,
            )
            resumed_predictions = runner.read_jsonl(root / "predictions.jsonl")
            resumed_cards = runner.read_jsonl(root / "cards.jsonl")

        failed_rows = {row["method"]: row for row in first_predictions if row["item_id"] == "state-fail"}
        dependent = set(runner.METHODS) - {"direct", "medrgag_proxy"}
        self.assertEqual(len(failed_rows), 13)
        self.assertTrue(all(failed_rows[method]["prediction"] is None for method in dependent))
        self.assertTrue(all(failed_rows[method]["reader_output"]["error_stage"] == "state_extraction" for method in dependent))
        self.assertTrue(all(
            failed_rows[method]["token_usage"]["total_tokens"]
            == failed_rows[method]["token_usage"]["state"]["total_tokens"]
            and failed_rows[method]["token_usage"]["reader"]["total_tokens"] == 0
            for method in dependent
        ))
        self.assertIsNotNone(failed_rows["direct"]["prediction"])
        self.assertIsNotNone(failed_rows["medrgag_proxy"]["prediction"])

        failed_cards = [row for row in first_cards if row["item_id"] == "state-fail"]
        self.assertEqual({row["method"] for row in failed_cards}, set(runner.TRANSITION_METHODS))
        self.assertTrue(all(row["cards"] == [] and row["parse_failure"] for row in failed_cards))
        shuffle_rows = {row["method"]: row for row in failed_cards}
        self.assertTrue(shuffle_rows["effect_shuffle"]["shuffle_applicable"])
        self.assertTrue(shuffle_rows["full_card_shuffle"]["shuffle_applicable"])

        next_rows = [row for row in first_predictions if row["item_id"] == "next-item"]
        self.assertEqual(len(next_rows), 13)
        self.assertTrue(any(row["method"] == "full_transition" and row["prediction"] is not None for row in next_rows))
        self.assertEqual(backend.state_calls, 3)
        self.assertEqual(len(resumed_predictions), len(first_predictions))
        self.assertEqual(len(resumed_cards), len(first_cards))

    def test_direct_skips_state_and_retrieval(self):
        item = {"item_id": "d", "dataset": "medpic", "question": "Q", "options": {"A": "x"}, "fixed_evidence": []}
        backend = Backend()
        with tempfile.TemporaryDirectory() as temporary:
            runner.run([item], ("direct",), Path(temporary), backend, 10000, 128)
            self.assertFalse(any("Extract only facts visible" in prompt for prompt in backend.prompts))
            row = runner.read_jsonl(Path(temporary) / "predictions.jsonl")[0]
            self.assertEqual(row["state"], {})

    def test_direct_and_proxy_logs_omit_shared_state(self):
        item = {
            "item_id": "shared-state", "dataset": "medpic", "question": "Choose.",
            "options": {"A": "one", "B": "two"}, "fixed_evidence": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run(
                [item], ("decomposition_only", "direct", "medrgag_proxy"), root,
                Backend(), 10000, 128, Retriever(), {"shared-state": []},
            )
            rows = {row["method"]: row for row in runner.read_jsonl(root / "predictions.jsonl")}
        self.assertTrue(rows["decomposition_only"]["state"])
        self.assertEqual(rows["direct"]["state"], {})
        self.assertEqual(rows["medrgag_proxy"]["state"], {})

    def test_medrgag_proxy_requires_real_documents(self):
        item = {"item_id": "d", "dataset": "medpic", "question": "Q", "options": {"A": "x"}, "fixed_evidence": []}
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "selected top-5"):
                runner.run([item], ("medrgag_proxy",), Path(temporary), Backend(), 10000, 128)

    def test_medeinst_direct_rank_maps_hypothesis_id(self):
        class DiagnosisBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "Extract only facts visible" in prompt:
                        value = {"current_state_summary": "edited case", "fixed_action": "", "candidate_hypotheses": ["d0", "d1", "d2", "d3", "d4"], "uncertainties": []}
                    else:
                        value = {"ranking": ["H2", "H0", "H1", "H3", "H4"], "selected": "H2", "reasoning": "r", "supporting_evidence_ids": []}
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": len(prompt), "completion_tokens": len(raw), "finish_reason": "stop"})
                return rows
        item = {"item_id": "dx", "dataset": "medeinst", "question": "Most likely diagnosis?", "options": None, "fixed_evidence": []}
        with tempfile.TemporaryDirectory() as temporary:
            runner.run([item], ("direct_rank",), Path(temporary), DiagnosisBackend(), 10000, 128, Retriever())
            row = runner.read_jsonl(Path(temporary) / "predictions.jsonl")[0]
            self.assertEqual(row["prediction"], "d2")

    def test_medeinst_direct_rank_repairs_nested_ranking_to_candidate_ids(self):
        class RankRepairBackend(Backend):
            def __init__(self):
                super().__init__()
                self.rank_calls = 0

            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "Extract only facts visible" in prompt:
                        value = {
                            "current_state_summary": "edited case", "fixed_action": "",
                            "candidate_hypotheses": ["d0", "d1", "d2", "d3", "d4"], "uncertainties": [],
                        }
                    elif "direct medical option ranker" in prompt:
                        self.rank_calls += 1
                        value = (
                            {
                                "ranking": [{"diagnosis": "d2"}], "selected": ["d2"],
                                "reasoning": "verbose", "supporting_evidence_ids": [],
                            }
                            if self.rank_calls == 1 else
                            {
                                "ranking": ["H2", "H0", "H1", "H3", "H4"], "selected": "H2",
                                "reasoning": "H2 best matches.", "supporting_evidence_ids": [],
                            }
                        )
                    else:
                        raise AssertionError(prompt)
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {"item_id": "dx-repair", "dataset": "medeinst", "question": "Most likely diagnosis?", "options": None, "fixed_evidence": []}
        backend = RankRepairBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("direct_rank",), root, backend, 10000, 128, Retriever())
            row = runner.read_jsonl(root / "predictions.jsonl")[0]
        rank_prompts = [prompt for prompt in backend.prompts if "direct medical option ranker" in prompt]
        self.assertNotIn("Discard malformed or repeated detail", rank_prompts[0])
        self.assertIn("Discard malformed or repeated detail", rank_prompts[1])
        self.assertIn('"selected": "H0"', rank_prompts[1])
        self.assertIn('"H2": "d2"', rank_prompts[1])
        self.assertEqual(row["prediction"], "d2")
        self.assertEqual(row["token_usage"]["reader"]["retry_count"], 1)

    def test_mcf_direct_rank_repairs_invalid_safety_enum(self):
        class SafetyRepairBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                value = {
                    "ranking": ["higher", "lower", "no difference"], "selected": "higher",
                    "reasoning": "ranked", "supporting_evidence_ids": [],
                    "real_world_safety_flag": "dangerous" if len(self.prompts) == 1 else "unsafe",
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        backend = SafetyRepairBackend()
        parsed, usage = runner.direct_rank(
            {"item_id": "mcf-rank", "dataset": "medcounterfact", "question": "Compare."},
            {}, [], backend, 10000, 128,
        )
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(parsed["real_world_safety_flag"], "unsafe")

    def test_mcf_safe_safety_alias_normalizes_without_retry(self):
        class SafeAliasBackend(Backend):
            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "direct medical option ranker" in prompt:
                        value = {
                            "ranking": ["higher", "lower", "no difference"], "selected": "lower",
                            "reasoning": "ranked", "supporting_evidence_ids": [],
                            "real_world_safety_flag": "safe",
                        }
                    else:
                        value = {
                            "evidence_conditioned_answer": "lower", "real_world_safety_flag": "safe",
                            "reasoning": "matched", "supporting_evidence_ids": [],
                        }
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {"item_id": "mcf-safe", "dataset": "medcounterfact", "question": "Does mortality change?"}
        backend = SafeAliasBackend()
        ranked, rank_usage = runner.direct_rank(item, {}, [], backend, 10000, 128)
        matched, match_usage = runner.evidence_world_match(
            item, [{"expected_observations": ["Mortality is lower."]}], backend, 10000, 128,
        )
        self.assertEqual(rank_usage["retry_count"], 0)
        self.assertEqual(match_usage["retry_count"], 0)
        self.assertEqual(ranked["real_world_safety_flag"], "none")
        self.assertEqual(matched["real_world_safety_flag"], "none")
        self.assertEqual(len(backend.prompts), 2)

    def test_medeinst_state_repairs_duplicate_diagnoses_from_visible_case(self):
        class DuplicateDiagnosisBackend(Backend):
            def __init__(self, fix=True):
                super().__init__()
                self.fix = fix

            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                hypotheses = ["Pneumonia"] * 5
                if len(self.prompts) > 1 and self.fix:
                    hypotheses = [
                        "Pneumonia", "Acute bronchitis", "Pulmonary embolism",
                        "Heart failure", "Viral respiratory infection",
                    ]
                value = {
                    "current_state_summary": "Fever, cough, and dyspnea.",
                    "fixed_action": "",
                    "candidate_hypotheses": hypotheses,
                    "uncertainties": ["Imaging is unavailable."],
                }
                raw = json.dumps(value)
                return [{"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"}]

        item = {
            "item_id": "me-duplicate", "dataset": "medeinst", "question": "What is the diagnosis?",
            "patient_state": {"symptoms": ["fever", "cough", "dyspnea"]}, "fixed_evidence": [],
        }
        backend = DuplicateDiagnosisBackend()
        state, usage = runner.build_state(item, backend, 10000)
        repair = backend.prompts[1]
        self.assertNotIn("Do not add facts or change its meaning", repair)
        self.assertIn("replace duplicates", repair)
        self.assertIn("not actions, treatments, or tests", repair)
        self.assertIn("fever", repair)
        self.assertEqual(usage["retry_count"], 1)
        self.assertEqual(len(state["candidate_hypotheses"]), 5)
        self.assertEqual(len({value.strip().casefold() for value in state["candidate_hypotheses"]}), 5)
        self.assertEqual(state["current_state_summary"], "Fever, cough, and dyspnea.")
        self.assertEqual(state["uncertainties"], ["Imaging is unavailable."])

        failing = DuplicateDiagnosisBackend(fix=False)
        with self.assertRaisesRegex(ValueError, "model failed JSON contract after one retry"):
            runner.build_state(item, failing, 10000)
        self.assertEqual(len(failing.prompts), 2)

    def test_resume_reuses_first_canonical_state_and_candidates(self):
        class ChangingStateBackend(Backend):
            def __init__(self):
                super().__init__()
                self.state_calls = 0

            def generate(self, prompts, max_tokens, **kwargs):
                self.prompts.extend(prompts)
                rows = []
                for prompt in prompts:
                    if "Extract only facts visible" in prompt:
                        self.state_calls += 1
                        prefix = "d" if self.state_calls == 1 else "changed"
                        value = {
                            "current_state_summary": f"{prefix} state", "fixed_action": "",
                            "candidate_hypotheses": [f"{prefix}{index}" for index in range(5)],
                            "uncertainties": [],
                        }
                    elif "direct medical option ranker" in prompt:
                        value = {
                            "ranking": ["H2", "H0", "H1", "H3", "H4"], "selected": "H2",
                            "reasoning": "ranked", "supporting_evidence_ids": [],
                        }
                    else:
                        value = {"open_answer": "d0", "reasoning": "answered", "supporting_evidence_ids": []}
                    raw = json.dumps(value)
                    rows.append({"raw_response": raw, "prompt_tokens": 1, "completion_tokens": 1, "finish_reason": "stop"})
                return rows

        item = {
            "item_id": "resume-state", "dataset": "medeinst", "question": "Most likely diagnosis?",
            "options": None, "fixed_evidence": [],
        }
        backend = ChangingStateBackend()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner.run([item], ("decomposition_only",), root, backend, 10000, 128, Retriever())
            first = runner.read_jsonl(root / "predictions.jsonl")[0]
            runner.run([item], ("decomposition_only", "direct_rank"), root, backend, 10000, 128, Retriever())
            rows = {row["method"]: row for row in runner.read_jsonl(root / "predictions.jsonl")}
        resumed = rows["direct_rank"]
        self.assertEqual(backend.state_calls, 1)
        self.assertEqual(resumed["state"], first["state"])
        self.assertEqual(resumed["token_usage"]["state"], first["token_usage"]["state"])
        self.assertEqual(resumed["prediction"], "d2")
        rank_prompt = next(prompt for prompt in backend.prompts if "direct medical option ranker" in prompt)
        self.assertIn('"H2": "d2"', rank_prompt)


if __name__ == "__main__":
    unittest.main()
