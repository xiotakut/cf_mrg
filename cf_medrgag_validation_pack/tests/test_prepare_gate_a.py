import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GateAPrepTest(unittest.TestCase):
    def test_local_sources_are_seeded_cached_and_answer_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "sources"
            sources.mkdir()

            def jsonl(name, rows):
                path = sources / name
                path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
                return {"name": name, "url": path.as_uri()}

            medpic = sources / "medpic.json"
            medpic.write_text(json.dumps([
                {"instance_id": "p1", "patient_vignette": "patient one", "question": "avoid?", "options": {"A": "a", "B": "b"}, "answer": ["A"], "metadata": {"gold_answer": "leak"}},
                {"instance_id": "p2", "patient_vignette": "patient two", "question": "avoid?", "options": {"A": "a", "B": "b"}, "answer": ["B"]},
            ]), encoding="utf-8")
            clir_files = []
            clir_tasks = {
                6: "intervention_response", 7: "threshold_forecasting", 8: "next_value_interval_forecasting",
                9: "clinical_timeseries_summarization", 10: "immediate_intervention_decision",
            }
            clir_evidence = {
                6: {"intervention_event_hour": 1, "baseline_observation": {"hour": 0, "value": 2}, "post_observations": [{"hour": 2, "value": 1}], "model_direction": "decrease"},
                7: {"anchor_time": 1, "future_observations": [{"hour": 2, "value": 1}], "condition_met": True},
                8: {"anchor_time": 1, "recent_visible_same_variable_observations": [{"hour": 0, "value": 2}], "target_observation": {"hour": 2, "value": 1}, "answer_interval": {"low": 0, "high": 2}},
                9: "all",
                10: {"event_hour": 1, "category_combination": "Drugs", "events": [{"text": "Drug X", "hour": 1, "category": "Drugs", "label": "answer"}]},
            }
            for number in range(6, 11):
                clir_files.append({**jsonl(f"t{number}.jsonl", [
                    {"id": f"t{number}-a", "question": "q\n\nOptions:\nA. yes\nB. no", "answer": "A", "episode_id": f"e{number}", "evidence": clir_evidence[number]},
                    {"id": f"t{number}-b", "question": "q\n\nOptions:\nA. yes\nB. no", "answer": "B", "episode_id": f"e{number}", "evidence": clir_evidence[number]},
                ]), "task": clir_tasks[number], "pilot_count": 1})
            medeinst = jsonl("medeinst.jsonl", [
                {"case_id": case, "case_type": variant, "narrative": f"{case} {variant}", "ground_truth": diagnosis}
                for case, diagnosis in (("c1", "d1"), ("c2", "d2")) for variant in ("control", "trap")
            ])
            originals = jsonl("original.jsonl", [
                {"index": index, "question": f"original {pair}", "article_summaries": [f"evidence {pair}"], "metadata": {"id": pair, "answer": "same"}}
                for index, pair in enumerate(("m1", "m2", "m3", "m4"), 1)
            ])
            replacements = jsonl("replaced.jsonl", [
                {"index": index + 10, "question": f"replacement {category}", "article_summaries": [f"fixed {category}"], "metadata": {"id": f"m{index + 1}", "answer": "higher", "MainCategory": category}}
                for index, category in enumerate(("OOD", "ID", "Nonsense Tokens", "poison"))
            ])
            remedqa_rows = sources / "remedqa-rows.json"
            remedqa_rows.write_text(json.dumps({"num_rows_total": 1, "rows": [{"row": {"id": "r1", "question": "rq", "options": ["a", "b"], "answer": "A"}}]}), encoding="utf-8")
            cpv_rows = sources / "cpv-rows.json"
            cpv_rows.write_text(json.dumps({"num_rows_total": 5, "rows": [
                {"row": {"case_id": "valid", "question": "same base", "case_text": "male-injected case", "option_a": "a", "option_b": "b", "answer": "answer text", "answer_idx": "A"}},
                {"row": {"case_id": "valid", "question": "same base", "case_text": "female-injected case", "option_a": "a", "option_b": "b", "answer": "answer text", "answer_idx": "A"}},
                {"row": {"case_id": "invalid", "question": "same invalid base", "case_text": "unchanged case", "option_a": "a", "option_b": "b", "answer": "answer text", "answer_idx": "A"}},
                {"row": {"case_id": "invalid", "question": "same invalid base", "case_text": "unchanged case", "option_a": "a", "option_b": "b", "answer": "answer text", "answer_idx": "A"}},
                {"row": {"case_id": "invalid", "question": "same invalid base", "case_text": "partly changed case", "option_a": "a", "option_b": "b", "answer": "answer text", "answer_idx": "A"}},
            ]}), encoding="utf-8")

            base = {"revision": "pinned", "license": {"declared": "test"}, "capabilities": {}, "repo_id": "fixture/repo"}
            registry = {
                "registry_version": 1,
                "datasets": {
                    "medpic": {**base, "source": "huggingface", "file": {"name": "medpic.json", "url": medpic.as_uri()}, "pilot": {"count": 2, "selector": "all_rows"}},
                    "clir": {**base, "source": "huggingface_raw_snapshot", "files": clir_files, "pilot": {"count": 5, "seed": 13, "selector": "seeded"}},
                    "medeinst": {**base, "source": "huggingface", "file": medeinst, "pair_key": "case_id", "pilot": {"count": 1, "seed": 13, "count_unit": "pairs", "selector": "seeded"}},
                    "medcounterfact": {**base, "source": "github", "files": [{**originals, "role": "original"}, {**replacements, "role": "replacement"}], "pair_key": "metadata.id", "pilot": {"count": 4, "seed": 13, "selector": "seeded"}},
                    "remedqa": {**base, "source": "huggingface", "files": ["unused.parquet"], "split": ["medqa_mcq"], "pair_key": "id", "rows_urls": {"medqa_mcq": remedqa_rows.as_uri()}, "pilot": {"count": 1, "seed": 13, "selector": "seeded"}},
                    "cpv": {**base, "source": "huggingface", "file": "unused.parquet", "split": "train", "pair_key": "case_id", "rows_url": cpv_rows.as_uri(), "pilot": {"count": 1, "seed": 13, "selector": "seeded"}},
                },
            }
            registry_path = root / "registry.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            work = root / "work"
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "prepare_gate_a.py"), "--sources", str(registry_path), "--work-dir", str(work)], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

            inference = [json.loads(line) for line in (work / "pilot.inference.jsonl").read_text().splitlines()]
            gold = [json.loads(line) for line in (work / "pilot.gold.jsonl").read_text().splitlines()]
            manifest = json.loads((work / "gate_a_manifest.json").read_text())
            self.assertEqual(manifest["selected_row_counts"], {"medpic": 2, "clir": 5, "medeinst": 2, "medcounterfact": 8, "remedqa": 1, "cpv": 2})
            self.assertEqual(len(inference), len(gold))
            forbidden = {"answer", "gold_answer", "pair_id", "case_id", "change_direction", "should_answer_change", "category"}
            def keys(value):
                if isinstance(value, dict):
                    return set(value) | set().union(*(keys(child) for child in value.values()), set())
                if isinstance(value, list):
                    return set().union(*(keys(child) for child in value), set())
                return set()
            self.assertTrue(all(not (keys(row) & forbidden) for row in inference))
            self.assertTrue(all(not ({"source_record_id", "source_file"} & set(row["metadata"])) for row in inference))
            self.assertEqual({row["variant"] for row in inference}, {"item"})
            self.assertTrue(all(row["item_id"].startswith(row["dataset"] + "-") and len(row["item_id"].rsplit("-", 1)[-1]) == 32 for row in inference))
            self.assertTrue(all(":" not in row["item_id"] and set(row["item_id"].rsplit("-", 1)[-1]) <= set("0123456789abcdef") for row in inference))
            self.assertTrue(all(row["input_hash"] == hashlib.sha256(json.dumps({key: value for key, value in row.items() if key != "input_hash"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest() for row in inference))
            self.assertEqual(next(row for row in inference if row["dataset"] == "medpic")["options"], {"A": "a", "B": "b"})
            self.assertTrue(all(row["fixed_evidence"] for row in inference if row["dataset"] == "medcounterfact"))
            self.assertTrue(all(row["metadata"]["retrieval_policy"] == "fixed_evidence_only_primary" for row in inference if row["dataset"] == "medcounterfact"))
            self.assertTrue(all(not row["fixed_evidence"] for row in inference if row["dataset"] == "clir" and row["task_family"] in {"threshold_forecasting", "clinical_timeseries_summarization", "immediate_intervention_decision"}))
            self.assertTrue(all(row["fixed_evidence"][0].get("post_observations") for row in inference if row["dataset"] == "clir" and row["task_family"] == "intervention_response"))
            self.assertTrue(all(row["fixed_evidence"][0].get("recent_visible_same_variable_observations") for row in inference if row["dataset"] == "clir" and row["task_family"] == "next_value_interval_forecasting"))
            forbidden_evidence = {"model_direction", "condition_met", "future_observations", "target_observation", "answer_interval", "category_combination", "events", "category", "label"}
            self.assertTrue(all(not (keys(row["fixed_evidence"]) & forbidden_evidence) for row in inference if row["dataset"] == "clir"))
            self.assertTrue(all(isinstance(row["fixed_evidence"], list) for row in inference if row["dataset"] == "clir"))
            self.assertTrue(all(row["options"] for row in inference if row["dataset"] == "clir"))
            self.assertTrue(all(row["options"] == {"A": "a", "B": "b"} for row in inference if row["dataset"] == "cpv"))
            self.assertEqual({row["question"] for row in inference if row["dataset"] == "cpv"}, {"male-injected case", "female-injected case"})
            self.assertNotIn("invalid", {row["pair_id"] for row in gold if row["dataset"] == "cpv"})
            self.assertTrue(all(row["answer"] == ["A"] for row in gold if row["dataset"] == "cpv"))
            self.assertTrue(any(row["pair_id"] for row in gold if row["dataset"] == "medeinst"))
            self.assertEqual({row["variant"] for row in gold if row["dataset"] == "medeinst"}, {"control", "trap"})
            self.assertEqual({row["metadata"].get("counterfactual_category") for row in gold if row["dataset"] == "medcounterfact" and row["variant"] == "counterfactual"}, {"medical", "non_medical", "nonce", "toxic"})
            self.assertEqual({artifact["kind"] for name in ("remedqa", "cpv") for artifact in manifest["datasets"][name]["artifacts"]}, {"datasets_server_rows"})
            self.assertEqual(manifest["bindings"]["inference_sha256"], hashlib.sha256((work / "pilot.inference.jsonl").read_bytes()).hexdigest())
            self.assertTrue(all(manifest["adapters"][dataset]["status"] == "pass" for dataset in manifest["adapters"]))
            self.assertTrue(all(manifest["raw_artifacts"][dataset] for dataset in manifest["raw_artifacts"]))


if __name__ == "__main__":
    unittest.main()
