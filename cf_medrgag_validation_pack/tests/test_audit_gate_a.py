from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_gate_a.py"
SPEC = importlib.util.spec_from_file_location("audit_gate_a", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GateAAuditTests(unittest.TestCase):
    def build_fixture(self, root: Path, *, missing_capabilities: bool = False, semantic_issues: bool = False) -> tuple[Path, Path, Path, Path]:
        inference, gold = [], []

        def add(dataset: str, item_id: str, *, pair_id=None, variant="base", task="control", category=None, change=False, question="Q") -> None:
            visible_id = item_id if semantic_issues else f"opaque-{len(inference):06d}"
            row = {
                "dataset": dataset,
                "item_id": visible_id,
                "task_family": task,
                "variant": variant if semantic_issues else "independent",
                "question": question,
                "options": {"A": "x", "B": "y"},
                "patient_state": {},
                "time_series": [{"event_id": "E1", "hour": 1}] if dataset == "clir" and not missing_capabilities else [],
                "fixed_evidence": ["RCT-1"] if dataset == "medcounterfact" else [],
                "candidate_actions": [],
                "metadata": {"retrieval_policy": "fixed_evidence_only_primary"} if dataset == "medcounterfact" else {},
            }
            if semantic_issues and dataset == "clir":
                if task == "clinical_timeseries_summarization":
                    row["time_series"] = []
                    row["fixed_evidence"] = [{"TSS": ["all"]}]
                elif task == "immediate_intervention_decision":
                    row["fixed_evidence"] = [{"events": [{"text": "direct target intervention"}]}]
                else:
                    row["fixed_evidence"] = [{"model_direction": "increase"}]
            if semantic_issues and dataset == "medeinst":
                row["metadata"].update({"source_record_id": "unrelated-raw-id", "source_file": "hidden-role.jsonl"})
            row["input_hash"] = MODULE.sha256_json(row)
            inference.append(row)
            metadata = {"counterfactual_category": category} if category else {}
            gold.append({
                "dataset": dataset,
                "item_id": visible_id,
                "variant": variant,
                "answer": ["A"],
                "pair_id": pair_id,
                "cluster_id": pair_id or item_id,
                "should_answer_change": change if pair_id is not None else None,
                "change_direction": "causal_flip" if pair_id is not None else None,
                "metadata": metadata,
            })

        for pair in range(89):
            add("medpic", f"mp-{pair}-a", pair_id=f"mp-{pair}")
            add("medpic", f"mp-{pair}-b", pair_id=f"mp-{pair}", variant="counterfactual", change=True)
        for index in range(467 - 178):
            add("medpic", f"mp-u-{index}")
        clir_tasks = sorted({
            "intervention_response",
            "threshold_forecasting",
            "next_value_interval_forecasting",
            "clinical_timeseries_summarization",
            "immediate_intervention_decision",
        })
        for task in clir_tasks:
            for index in range(100):
                pair_id = f"clir-{task}-0" if index < 2 else None
                add("clir", f"clir-{task}-{index}", pair_id=pair_id, variant="counterfactual" if index == 1 else "base", task=task, change=index == 1)
        for pair in range(500):
            add("medeinst", f"me-{pair}-control", pair_id=f"me-{pair}", variant="control", task="diagnosis_cf")
            add("medeinst", f"me-{pair}-trap", pair_id=f"me-{pair}", variant="trap", task="diagnosis_cf", change=True)
        categories = sorted(MODULE.CF_CATEGORIES)
        for category in categories:
            for index in range(50):
                pair = f"mcf-{category}-{index}"
                add("medcounterfact", f"{pair}-original", pair_id=pair, variant="original", task="evidence_cf")
                add("medcounterfact", f"{pair}-cf", pair_id=pair, variant="counterfactual", task="evidence_cf", category=category, change=False)
        for index in range(300):
            add("remedqa", f"remedqa-{index}", task="invariance_control")
        for index in range(300):
            pair = f"cpv-{index}"
            add("cpv", f"{pair}-a", pair_id=pair, task="invariance_control", question="same" if semantic_issues else f"variant A {index}")
            add("cpv", f"{pair}-b", pair_id=pair, task="invariance_control", question="same" if semantic_issues else f"variant B {index}")

        inference_path, gold_path = root / "pilot.inference.jsonl", root / "pilot.gold.jsonl"
        write_jsonl(inference_path, inference)
        write_jsonl(gold_path, gold)

        source_files = {
            "medpic": ["questions.json"],
            "clir": [f"{task}.jsonl" for task in clir_tasks],
            "medeinst": ["test.jsonl"],
            "medcounterfact": ["MedCounterFact_original_data.jsonl", "MedCounterFact_replaced_data.jsonl"],
            "remedqa": ["mcq.parquet"],
            "cpv": ["train.parquet"],
        }
        sources = {"datasets": {}}
        raw_artifacts = {}
        for dataset in MODULE.DATASETS:
            raw_artifacts[dataset] = []
            for name in source_files[dataset]:
                raw = root / f"{dataset}-{Path(name).name}"
                raw.write_text(f"raw {dataset} {name}\n", encoding="utf-8")
                raw_artifacts[dataset].append({"path": raw.name, "source_name": name, "sha256": file_hash(raw)})
            sources["datasets"][dataset] = {
                "revision": "a" * 40,
                "license": {"declared": "CC-BY-4.0", "status": "declared_in_dataset_card"},
                "files": source_files[dataset],
                "pilot": {"count": 300 if dataset in {"remedqa", "cpv"} else 0, "count_unit": "cluster_id"},
                "capabilities": {"official_pair_map": True, "fixed_evidence": True},
            }
        sources["datasets"]["clir"]["files"] = [{"name": f"{task}.jsonl", "task": task, "pilot_count": 100} for task in clir_tasks]
        sources["datasets"]["clir"]["capabilities"] = {"repository_evidence": True, "full_timeseries": True, "official_edit_pairs": True}
        source_path = root / "sources.json"
        source_path.write_text(json.dumps(sources), encoding="utf-8")

        capabilities = {}
        if not missing_capabilities:
            for name in ("medpic_official_linked_pairs", "clir_full_ts", "clir_official_causal_edit_pairs"):
                evidence = root / f"{name}.json"
                evidence.write_text(json.dumps({"source": "official", "revision": "a" * 40}), encoding="utf-8")
                capabilities[name] = {"available": True, "evidence_path": evidence.name, "evidence_sha256": file_hash(evidence)}
            capabilities["clir_official_causal_edit_pairs"]["pair_count"] = 5
        manifest = {
            "bindings": {
                "source_registry_sha256": file_hash(source_path),
                "inference_sha256": file_hash(inference_path),
                "gold_sha256": file_hash(gold_path),
            },
            "adapters": {dataset: {"status": "pass", "evidence": "test passed"} for dataset in MODULE.DATASETS},
            "capabilities": capabilities,
            "raw_artifacts": raw_artifacts,
        }
        manifest_path = root / "gate_a_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return source_path, manifest_path, inference_path, gold_path

    def test_passing_full_gate_a_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self.build_fixture(Path(directory))
            report = MODULE.audit_gate_a(*paths)
            self.assertEqual("proceed", report["decision"])
            self.assertFalse(report["blockers"])
            self.assertTrue(all(value["status"] == "pass" for value in report["checks"].values()))

    def test_stops_when_pair_and_full_ts_evidence_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self.build_fixture(Path(directory), missing_capabilities=True)
            report = MODULE.audit_gate_a(*paths)
            self.assertEqual("stop_before_inference", report["decision"])
            self.assertNotEqual("pass", report["checks"]["medpic_official_89_linked_pairs"]["status"])
            self.assertEqual("fail", report["checks"]["clir_full_ts"]["status"])
            self.assertNotEqual("pass", report["checks"]["clir_official_causal_edit_pairs"]["status"])

    def test_stops_on_pair_visibility_duplicate_cpv_and_derived_clir_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self.build_fixture(Path(directory), semantic_issues=True)
            report = MODULE.audit_gate_a(*paths)
            self.assertEqual("stop_before_inference", report["decision"])
            self.assertEqual("fail", report["checks"]["pair_blind_inference_values"]["status"])
            self.assertEqual("fail", report["checks"]["no_inference_leakage"]["status"])
            self.assertEqual("fail", report["checks"]["cpv_variant_questions"]["status"])
            self.assertEqual("fail", report["checks"]["clir_no_answer_derived_evidence"]["status"])
            self.assertEqual("fail", report["checks"]["clir_repository_evidence"]["status"])
            self.assertEqual(100, report["checks"]["clir_repository_evidence"]["rows_without_observations"])


if __name__ == "__main__":
    unittest.main()
