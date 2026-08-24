import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_gate_d.py"
SPEC = importlib.util.spec_from_file_location("run_gate_d", SCRIPT)
gate_d = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(gate_d)


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return list(text.encode())

    def decode(self, tokens, skip_special_tokens=True):
        return bytes(tokens).decode(errors="ignore")

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        return "\n".join(message["content"] for message in messages) + "\nASSISTANT:"


class FakeBackend:
    tokenizer = FakeTokenizer()

    def __init__(self):
        self.calls = 0
        self.prompts = []
        self.max_tokens = []

    def generate(self, prompts, max_tokens, **kwargs):
        self.calls += len(prompts)
        self.prompts.extend(prompts)
        limits = [max_tokens] * len(prompts) if isinstance(max_tokens, int) else max_tokens
        self.max_tokens.extend(limits)
        card = {**gate_d.fallback_card({"id": "A", "text": "alpha"}, ["D0"]), "candidate_id": "A"}
        score = lambda candidate_id: {"candidate_id": candidate_id, "precondition_fit": 1.0, "state_consistency": 1.0, "effect_consistency": 1.0, "evidence_support": 1.0, "harm_or_contradiction_penalty": 0.0, "uncertainty_penalty": 0.0, "total": 4.0}
        comparator = {"candidate_scores": [score("A"), score("B")], "selected_candidate_ids": ["A"], "causal_determinants": [], "comparison_valid": True}
        return [{"raw_response": json.dumps(comparator if "candidate_scores" in prompt else card) if limit in {1024, 2048, 3072} else '{"answer":"A"}', "prompt_tokens": len(prompt), "completion_tokens": limit if kwargs.get("ignore_eos") else 5, "finish_reason": "length" if kwargs.get("ignore_eos") else "stop"} for prompt, limit in zip(prompts, limits)]


def write_rows(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class GateDRunnerTest(unittest.TestCase):
    def test_incomplete_card_gets_one_json_repair_retry(self):
        backend = FakeBackend()
        candidates = [{"id": "A", "text": "alpha", "type": "action"}]
        initial_usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "finish_reasons": ["length"]}
        cards, raws, retries, final_usage = gate_d.finalize_cards(
            ["unfinished explanation"], candidates, [["D0"]], initial_usage, backend, 4096
        )
        self.assertEqual(retries, [1])
        self.assertEqual(cards[0]["retry_count"], 1)
        self.assertTrue(gate_d.complete_card_response(raws[0]))
        self.assertEqual(backend.max_tokens, [2048])
        self.assertEqual(final_usage["completion_tokens"], 10)

    def test_comparator_requires_full_candidate_coverage_and_selection(self):
        candidates = [{"id": "A"}, {"id": "B"}]
        self.assertFalse(gate_d.complete_comparator_response('{"candidate_scores":[]}', candidates))
        backend = FakeBackend()
        raw = backend.generate(["candidate_scores"], 1024)[0]["raw_response"]
        self.assertTrue(gate_d.complete_comparator_response(raw, candidates))
        self.assertEqual(gate_d.normalize_comparator(raw, candidates)["selected_candidate_ids"], ["A"])

    def test_comparator_uses_final_strict_retry(self):
        class SecondRetryBackend(FakeBackend):
            def generate(self, prompts, max_tokens, **kwargs):
                outputs = super().generate(prompts, max_tokens, **kwargs)
                if max_tokens in {1024, 2048}:
                    for output in outputs:
                        output["raw_response"] = "incomplete"
                return outputs

        item = {"item_id": "x", "dataset": "medpic", "question": "Q", "options": {"A": "a", "B": "b"}}
        state = {"state": gate_d.empty_state(), "candidates": [{"id": "A"}, {"id": "B"}]}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparator.jsonl"
            backend = SecondRetryBackend()
            gate_d.run_comparators([item], {"x": state}, {"x": []}, path, backend, 16, 32256)
            row = json.loads(path.read_text())
            self.assertEqual(row["retry_count"], 2)
            self.assertEqual(backend.max_tokens, [1024, 2048, 3072])
            self.assertLessEqual(len(backend.tokenizer.encode(backend.prompts[-1])) + 3072, 32768)

    def test_auxiliary_stage_token_budgets_fit_model_window(self):
        self.assertEqual(gate_d.stage_input_limit(32256, 1024), 31744)
        self.assertEqual(gate_d.stage_input_limit(32256, 7000), 25768)
        tokenizer = FakeTokenizer()
        rendered = gate_d.gb._stage_chat(tokenizer, "x" * 50000, gate_d.stage_input_limit(4096, 1024))
        self.assertLessEqual(len(tokenizer.encode(rendered)) + 1024, 4096 + 512)

    def test_candidate_fallback_clir_mcf_and_medeinst_parse(self):
        clir = {"dataset": "clir", "question": "Q\nA. alpha\nB. beta\nC. gamma\nD. delta", "options": {}}
        self.assertEqual([row["id"] for row in gate_d.candidates_for(clir, {})], list("ABCD"))
        mcf = {"dataset": "medcounterfact", "question": "Q", "options": None}
        self.assertEqual([row["id"] for row in gate_d.candidates_for(mcf, {})], ["higher", "lower", "no difference"])
        medeinst = {"dataset": "medeinst", "question": "Q", "options": None}
        parsed = {"candidate_actions_or_hypotheses": [
            {"id": "H0", "text": "Pneumonia", "type": "diagnosis"},
            {"id": "H0", "text": "Pneumonia", "type": "diagnosis"},
            {"text": "...", "type": "diagnosis"},
            {"text": "Order CT", "type": "action"},
            {"text": "Influenza", "type": "diagnosis"},
            {"text": "Pulmonary embolism", "type": "diagnosis"},
            {"text": "Heart failure", "type": "diagnosis"},
            {"text": "Tuberculosis", "type": "diagnosis"},
        ]}
        candidates = gate_d.candidates_for(medeinst, parsed)
        self.assertEqual(len(candidates), 5)
        self.assertEqual(candidates[0]["text"], "Pneumonia")
        self.assertEqual([row["id"] for row in candidates], ["H0", "H1", "H2", "H3", "H4"])
        with self.assertRaisesRegex(ValueError, "exactly 5"):
            gate_d.candidates_for(medeinst, {})
        self.assertNotIn("answer", json.dumps(candidates).lower())
        remedqa = {"dataset": "remedqa", "question": "Q", "options": {"A": "one"}}
        self.assertEqual(gate_d.candidates_for(remedqa, {"candidate_actions_or_hypotheses": [{"id": "A", "text": "one", "type": "outcome"}]})[0]["type"], "rule_judgment")
        self.assertEqual(gate_d.candidates_for(remedqa, {})[0]["type"], "rule_judgment")

    def test_query_round_robin_and_mcf_never_calls_external(self):
        candidates = []
        for candidate in ("A", "B"):
            candidates.append({"candidate_id": candidate, "queries": [
                {"documents": [{"id": f"{candidate}-{query}-{rank}", "contents": "x"} for rank in range(5)]}
                for query in range(4)
            ]})
        chosen = gate_d.round_robin_context(candidates)
        self.assertEqual(len(chosen), 5)
        self.assertEqual([row["id"].split("-")[0] for row in chosen], ["A", "B", "A", "B", "A"])

        class NoExternal:
            def retrieve(self, query, count):
                raise AssertionError("MCF must not retrieve externally")

        item = {"item_id": "m", "dataset": "medcounterfact", "question": "Q", "options": None, "fixed_evidence": ["one", "two"]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_rows(root / "state_action.jsonl", [{"item_id": "m", "dataset": "medcounterfact", "candidates": gate_d.candidates_for(item, {})}])
            self.assertEqual(gate_d.run_retrieval([item], root, NoExternal()), 1)
            retrieval = json.loads((root / "action_retrieval.jsonl").read_text())
            self.assertEqual(retrieval["policy"], "fixed_only")
            self.assertEqual(len(json.loads((root / "action_context.jsonl").read_text())["documents"]), 5)

    def test_card_projections_shuffle_and_json_parser(self):
        self.assertEqual(gate_d.last_json_object('draft {"x":1}\nfinal {"y":{"z":2}}')["y"], {"z": 2})
        cards = [
            gate_d.fallback_card({"id": "A", "text": "alpha"}, ["D0"]),
            gate_d.fallback_card({"id": "B", "text": "beta"}, ["D1"]),
        ]
        cards[0]["immediate_observations"] = ["effect-a"]
        cards[1]["immediate_observations"] = ["effect-b"]
        applicability = gate_d.project_cards(cards, "applicability")
        effects = gate_d.project_cards(cards, "effect")
        self.assertIn("applicability", applicability[0]); self.assertNotIn("immediate_observations", applicability[0])
        self.assertNotIn("rollout_valid", applicability[0])
        self.assertIn("immediate_observations", effects[0]); self.assertNotIn("applicability", effects[0])
        shuffled = gate_d.shuffled_cards("item", cards)
        self.assertEqual(gate_d.shuffled_cards("item", cards), shuffled)
        self.assertNotEqual([row["shuffle_source_candidate_id"] for row in shuffled], ["A", "B"])
        self.assertEqual(shuffled[0]["candidate_id"], "A")
        self.assertEqual(shuffled[0]["action"], "alpha")
        self.assertNotEqual(shuffled[0]["immediate_observations"], cards[0]["immediate_observations"])

    def test_all_methods_fake_e2e_and_resume(self):
        item = {"item_id": "x", "dataset": "medpic", "question": "Q", "options": {"A": "alpha", "B": "beta"}, "fixed_evidence": []}
        state = {"item_id": "x", "dataset": "medpic", "state": gate_d.empty_state(), "decision_goal": "Q", "requested_transition_target": "evidence_conclusion", "candidates": gate_d.candidates_for(item, {}), "usage": {"completion_tokens": 5}}
        documents = [{"id": f"D{index}", "contents": f"base doc {index}"} for index in range(2)]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_rows(root / "state_action.jsonl", [state])
            action_documents = [{"id": f"A{index}", "contents": f"action doc {index}"} for index in range(5)]
            write_rows(root / "action_context.jsonl", [{"item_id": "x", "dataset": "medpic", "documents": action_documents}])
            write_rows(root / "action_retrieval.jsonl", [{"item_id": "x", "dataset": "medpic", "candidates": [
                {"candidate_id": candidate, "queries": [{"documents": [{"id": f"{candidate}-{kind}-{index}", "contents": f"{candidate} evidence {kind}-{index}"} for index in range(5)]} for kind in range(4)]}
                for candidate in ("A", "B")
            ]}])
            write_rows(root / "M2.rerank.jsonl", [{"item_id": "x", "dataset": "medpic", "documents": documents}])
            backend = FakeBackend()
            counts = gate_d.run_methods([item], root, backend, gate_d.METHODS, 16, 4096, 32)
            self.assertEqual(counts, {method: 1 for method in gate_d.METHODS})
            first_calls = backend.calls
            self.assertTrue(all(len(backend.tokenizer.encode(prompt)) + budget <= 4096 + 512 for prompt, budget in zip(backend.prompts, backend.max_tokens)))
            self.assertEqual(gate_d.run_methods([item], root, backend, gate_d.METHODS, 16, 4096, 32), {method: 0 for method in gate_d.METHODS})
            self.assertEqual(backend.calls, first_calls)
            parametric = json.loads((root / "parametric_cards.jsonl").read_text())
            self.assertTrue(all(card["evidence_ids"] == [] for card in parametric["cards"]))
            reasoning = json.loads((root / "M4.reasoning.jsonl").read_text())
            self.assertEqual(reasoning["target_completion_tokens"], 20)
            self.assertEqual(reasoning["usage"]["completion_tokens"], 20)
            self.assertIn(20, backend.max_tokens)
            self.assertTrue(any("no retrieved or fixed evidence" in prompt for prompt in backend.prompts))
            self.assertTrue(any("Configured output-token budget: 20" in prompt and "Base evidence:" in prompt for prompt in backend.prompts))
            self.assertIn("A evidence", backend.prompts[0]); self.assertNotIn("B evidence", backend.prompts[0])
            self.assertIn("B evidence", backend.prompts[1]); self.assertNotIn("A evidence", backend.prompts[1])
            reader_prompts = backend.prompts[-len(gate_d.METHODS):]
            self.assertIn('"decision_goal": "Q"', reader_prompts[0])
            self.assertIn("Document [4]: ", reader_prompts[0])
            self.assertIn("Computation-matched extra reasoning", reader_prompts[1]); self.assertNotIn("Extracted state and actions", reader_prompts[1])
            self.assertNotIn("Extracted state and actions", reader_prompts[2])
            self.assertTrue(all("Extracted state and actions" in prompt for prompt in reader_prompts[3:]))
            for method in gate_d.METHODS:
                row = json.loads((root / f"{method}.jsonl").read_text())
                self.assertEqual(row["method"], method)

    def test_phase_preflight_requires_complete_coverage(self):
        items = [{"item_id": "a"}, {"item_id": "b"}]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stage.jsonl"
            with self.assertRaises(FileNotFoundError):
                gate_d.require_rows(path, items, "stage")
            write_rows(path, [{"item_id": "a"}])
            with self.assertRaisesRegex(ValueError, "cover balanced60"):
                gate_d.require_rows(path, items, "stage")


if __name__ == "__main__":
    unittest.main()
