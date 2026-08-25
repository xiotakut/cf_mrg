import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_gate_b.py"
SPEC = importlib.util.spec_from_file_location("run_gate_b", SCRIPT)
gate_b = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(gate_b)


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
        self.kwargs = []
        self.prompts = []

    def generate(self, prompts, max_tokens, **kwargs):
        self.calls += len(prompts)
        self.kwargs.append(kwargs)
        self.prompts.extend(prompts)
        return [
            {
                "raw_response": '{"answer":"A"}',
                "prompt_tokens": len(prompt),
                "completion_tokens": 5,
                "finish_reason": "stop",
            }
            for prompt in prompts
        ]


class GateBRunnerTest(unittest.TestCase):
    def test_bracketed_and_unbracketed_selection_ids(self):
        self.assertEqual(
            gate_b.selection_ids("Reasoning: 1 2 3\nFinal Selection: [5] [8] [2] [9] [3]"),
            [5, 8, 2, 9, 3],
        )
        self.assertEqual(
            gate_b.selection_ids("Reasoning: choose 1 and 4\nFinal Selection: 5 8 2 9 3"),
            [5, 8, 2, 9, 3],
        )
        self.assertEqual(
            gate_b.selection_ids("Final Selection: 1 2\nReasoning: 7\nFinal Selection: 9, 9, 8, 10, 7"),
            [9, 8, 7],
        )

    def test_dataset_answer_contracts_and_last_json(self):
        base = {"question": "Q", "fixed_evidence": []}
        medpic = gate_b._question_text({**base, "dataset": "medpic", "options": {"A": "x"}})
        clir = gate_b._question_text({**base, "dataset": "clir", "options": {"A": "x", "B": "y"}})
        clir_embedded = gate_b._question_text({**base, "dataset": "clir", "options": {}})
        counterfact = gate_b._question_text({**base, "dataset": "medcounterfact", "options": None})
        diagnosis = gate_b._question_text({**base, "dataset": "medeinst", "options": None})
        self.assertIn("array of one or more option keys", medpic)
        self.assertIn("exactly one option key string", clir)
        self.assertIn("exactly one A/B/C/D option key string", clir_embedded)
        self.assertIn('"higher", "lower", or "no difference"', counterfact)
        self.assertIn("only a concise diagnosis label", diagnosis)
        prompt = gate_b.build_reader_chat(FakeTokenizer(), {**base, "item_id": "c", "dataset": "clir", "options": {}}, "", 1000)
        self.assertIn("Always choose the best available option; never abstain.", prompt)
        self.assertEqual(
            gate_b.parse_answer('draft {"answer":"A"}\nfinal {"answer":"B"} trailing'),
            "B",
        )

    def test_balanced_reference_hash_and_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ids = [f"id-{index}" for index in range(60)]
            reference = root / "reference.json"
            reference.write_text(json.dumps(ids), encoding="utf-8")
            digest = hashlib.sha256(reference.read_bytes()).hexdigest()
            inference = root / "inference.jsonl"
            gold = root / "gold.jsonl"
            inference.write_text(
                "".join(json.dumps({"item_id": item_id}) + "\n" for item_id in reversed(ids)),
                encoding="utf-8",
            )
            gold.write_text(
                "".join(json.dumps({"item_id": item_id}) + "\n" for item_id in ids),
                encoding="utf-8",
            )
            rows = gate_b.load_balanced_pilot(inference, gold, reference, digest)
            self.assertEqual([row["item_id"] for row in rows], ids)

    def test_head_tail_context_and_m0_resume(self):
        tokenizer = FakeTokenizer()
        item = {
            "item_id": "x",
            "dataset": "medcounterfact",
            "question": "Q?",
            "options": None,
            "fixed_evidence": ["HEAD" + "m" * 500 + "TAIL"],
        }
        prompt = gate_b.build_reader_chat(tokenizer, item, gate_b._evidence_text(item), 400)
        self.assertIn("HEAD", prompt)
        self.assertIn("TAIL", prompt)
        self.assertIn("evidence truncated", prompt)
        self.assertLessEqual(len(tokenizer.encode(prompt)), 400)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "M0.jsonl"
            backend = FakeBackend()
            generated = gate_b.run_m0([item], output, backend, 16, 400, 32)
            self.assertEqual(generated, 1)
            self.assertEqual(gate_b.run_m0([item], output, backend, 16, 400, 32), 0)
            self.assertEqual(backend.calls, 1)
            row = json.loads(output.read_text())
            self.assertEqual(row["prediction"]["answer"], "A")
            self.assertEqual(
                set(row),
                {"item_id", "dataset", "method", "raw_response", "prediction", "usage"},
            )

    def test_retrieval_routing_and_m2_chain(self):
        class FakeRetriever:
            def __init__(self):
                self.calls = []

            def retrieve(self, query, count):
                self.calls.append((query, count))
                return [
                    {"id": f"external-{index}", "source": "external", "contents": f"doc {index}"}
                    for index in range(count)
                ]

        items = [
            {"item_id": "mcf", "dataset": "medcounterfact", "question": "Q", "options": None, "fixed_evidence": ["fixed evidence"]},
            {"item_id": "clir", "dataset": "clir", "question": "Q", "options": {"A": "x"}, "fixed_evidence": [{"observation": 1}]},
            {"item_id": "clir-empty", "dataset": "clir", "question": "Q", "options": {}, "fixed_evidence": []},
            {"item_id": "medpic", "dataset": "medpic", "question": "Q", "options": {"A": "x"}, "fixed_evidence": []},
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retriever = FakeRetriever()
            documents = gate_b.prepare_retrievals(items, root / "retrieval.jsonl", retriever)
            self.assertTrue(all(row["source"] == "fixed" for row in documents["mcf"]))
            self.assertEqual(documents["mcf"][0]["contents"], "fixed evidence")
            self.assertEqual([row["contents"] for row in documents["mcf"][1:]], ["", "", "", ""])
            self.assertTrue(all(row["source"] == "external" for row in documents["clir"]))
            self.assertEqual(len(documents["clir"]), 5)
            self.assertEqual(len(documents["clir-empty"]), 5)
            self.assertTrue(all(row["source"] == "external" for row in documents["clir-empty"]))
            self.assertEqual(len(documents["medpic"]), 5)
            self.assertEqual([count for _, count in retriever.calls], [5, 5, 5])

            reader = FakeBackend()
            gate_b.run_reader_method(
                "M1",
                [items[1]],
                {"clir": [{"contents": "external body", "medcpt_score": 99, "source": "external"}]},
                root / "M1.jsonl",
                reader,
                16,
                4096,
                32,
            )
            self.assertIn("Patient observations:", reader.prompts[0])
            self.assertIn('"observation": 1', reader.prompts[0])
            self.assertIn("Document [0]: external body", reader.prompts[0])
            self.assertNotIn("medcpt_score", reader.prompts[0])

            backend = FakeBackend()
            class FakeRanker:
                def rank(self, query, values):
                    return values

            count = gate_b.run_m2(
                [items[-1]],
                {"medpic": documents["medpic"]},
                root,
                backend,
                16,
                4096,
                32,
                FakeRanker(),
            )
            self.assertEqual(count, 1)
            self.assertEqual(backend.calls, 13)
            self.assertIn(1.0, [kwargs.get("presence_penalty") for kwargs in backend.kwargs])
            self.assertTrue(any("# Retrieved Document" in prompt and "A: x" in prompt for prompt in backend.prompts))
            result = json.loads((root / "M2.jsonl").read_text())
            self.assertEqual(result["method"], "M2")
            self.assertEqual(result["prediction"]["answer"], "A")

    def test_mcf_contiguous_buckets_and_selection_profile(self):
        values = [f"evidence-{index}" for index in range(7)]
        documents = gate_b.fixed_documents({"fixed_evidence": values}, 5)
        self.assertEqual(len(documents), 5)
        flattened = [part for document in documents for part in document["contents"].split("\n\n") if part]
        self.assertEqual(flattened, values)
        payload = gate_b.selection_payload([{"item_id": "x"}], "abc")
        self.assertEqual(payload["m2_profile"], "released-code-intent-all-llama")


if __name__ == "__main__":
    unittest.main()
