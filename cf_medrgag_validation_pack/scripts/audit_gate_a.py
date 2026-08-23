#!/usr/bin/env python3
"""Audit the frozen Gate-A boundary before any inference is allowed.

JSON is preferred for the source registry.  The small YAML reader exists only
to read this pack's simple ``configs/datasets.yaml`` registry; it deliberately
does not pretend to be a general YAML parser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DATASETS = ("medpic", "clir", "medeinst", "medcounterfact", "remedqa", "cpv")
CF_CATEGORIES = {"nonce", "medical", "non_medical", "toxic"}
FORBIDDEN_KEY_PARTS = ("answer", "gold", "pair", "counterpart", "change")
FORBIDDEN_INFERENCE_KEYS = {"case_id", "cluster_id", "raw_case_id", "source_file", "source_record_id", "source_role"}
CLIR_ALLOWED_EVIDENCE_KEYS = {
    "intervention_response": {
        "source", "intervention_event_hour", "context_end_time", "intervention_items_at_event_hour",
        "response_variable", "response_variable_label", "baseline_observation", "post_observations",
    },
    "next_value_interval_forecasting": {
        "source", "anchor_time", "horizon_hours", "target_variable", "target_variable_label",
        "previous_same_variable_observation", "recent_visible_same_variable_observations",
    },
}
PAIR_ROLE_VALUES = {"base", "control", "counterfactual", "irrelevant_edit", "original", "replaced", "trap"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return {}
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value.split(" #", 1)[0].strip()


def load_registry(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("source registry must be an object")
        return value
    except json.JSONDecodeError:
        datasets: dict[str, dict[str, Any]] = {}
        current: dict[str, Any] | None = None
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip() or line.strip() == "datasets:":
                continue
            match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
            if match:
                current = datasets.setdefault(match.group(1), {})
                continue
            match = re.match(r"^    ([A-Za-z0-9_-]+):\s*(.*)$", line)
            if match and current is not None:
                current[match.group(1)] = _scalar(match.group(2))
        return {"datasets": datasets}


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows, errors = [], []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{path.name}:{line_no}: row is not an object")
            continue
        rows.append(row)
    return rows, errors


def _status(problems: list[str], missing: list[str]) -> str:
    return "fail" if problems else "insufficient" if missing else "pass"


def _check(problems: list[str] | None = None, missing: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    problems, missing = problems or [], missing or []
    return {"status": _status(problems, missing), "problems": problems, "missing": missing, **extra}


def _identity(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("dataset", "")), str(row.get("item_id", ""))


def _nested_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            found.append(name)
            found.extend(_nested_keys(child, name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_nested_keys(child, f"{prefix}[{index}]"))
    return found


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for child in value.values() for text in _strings(child)]
    if isinstance(value, list):
        return [text for child in value for text in _strings(child)]
    return []


def _keyed_strings(value: Any, key_parts: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if any(part in str(key).lower() for part in key_parts):
                found.extend(_strings(child))
            found.extend(_keyed_strings(child, key_parts))
    elif isinstance(value, list):
        for child in value:
            found.extend(_keyed_strings(child, key_parts))
    return found


def _has_repository_observations(row: dict[str, Any]) -> bool:
    if row.get("time_series"):
        return True
    evidence = row.get("fixed_evidence")
    if not isinstance(evidence, list) or not evidence:
        return False
    task = str(row.get("task_family", ""))
    objects = [value for value in evidence if isinstance(value, dict)]
    if task == "intervention_response":
        return any(value.get("baseline_observation") and value.get("post_observations") for value in objects)
    if task == "next_value_interval_forecasting":
        return any(value.get("recent_visible_same_variable_observations") for value in objects)
    return False


def _exposes_secret(value: str, secret: str) -> bool:
    return bool(secret) and bool(re.search(rf"(?<![a-z0-9]){re.escape(secret)}(?![a-z0-9])", value))


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def _evidence_check(spec: Any, base: Path, name: str) -> dict[str, Any]:
    if not isinstance(spec, dict):
        return _check(missing=[f"{name} capability declaration"])
    if spec.get("available") is False:
        return _check(problems=[f"{name} is declared unavailable"])
    if spec.get("available") is not True:
        return _check(missing=[f"{name}.available=true"])
    path_value, expected = spec.get("evidence_path"), spec.get("evidence_sha256")
    if not path_value or not expected:
        return _check(missing=[f"{name} evidence_path/evidence_sha256"])
    path = _resolve(base, str(path_value))
    if not path.is_file():
        return _check(problems=[f"{name} evidence file missing: {path}"])
    actual = sha256_file(path)
    if actual != expected:
        return _check(problems=[f"{name} evidence hash mismatch"], expected_sha256=expected, actual_sha256=actual)
    return _check(evidence=str(path), sha256=actual)


def audit_gate_a(
    source_registry_path: Path,
    manifest_path: Path,
    inference_path: Path,
    gold_path: Path,
) -> dict[str, Any]:
    registry = load_registry(source_registry_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inference, inference_errors = load_jsonl(inference_path)
    gold, gold_errors = load_jsonl(gold_path)
    checks: dict[str, dict[str, Any]] = {}

    bindings = manifest.get("bindings", {}) if isinstance(manifest, dict) else {}
    binding_problems, binding_missing = [], []
    for key, path in (
        ("source_registry_sha256", source_registry_path),
        ("inference_sha256", inference_path),
        ("gold_sha256", gold_path),
    ):
        expected = bindings.get(key)
        if not expected:
            binding_missing.append(key)
        elif expected != sha256_file(path):
            binding_problems.append(f"{key} mismatch")
    checks["manifest_bindings"] = _check(binding_problems, binding_missing)

    sources = registry.get("datasets", registry)
    source_problems, source_missing, verified_raw = [], [], {}
    license_problems = []
    declared_raw = manifest.get("raw_artifacts", {}) if isinstance(manifest, dict) else {}
    for dataset in DATASETS:
        spec = sources.get(dataset) if isinstance(sources, dict) else None
        if not isinstance(spec, dict):
            source_missing.append(f"{dataset} source entry")
            continue
        if not spec.get("revision"):
            source_missing.append(f"{dataset}.revision")
        license_spec = spec.get("license")
        if not isinstance(license_spec, dict):
            source_missing.append(f"{dataset}.license declaration")
        elif not license_spec.get("declared") or str(license_spec.get("status", "")).startswith("missing"):
            license_problems.append(f"{dataset} license is unresolved: {license_spec.get('status', 'missing declaration')}")
        artifacts = declared_raw.get(dataset) if isinstance(declared_raw, dict) else None
        raw_base = manifest_path.parent
        if artifacts is None:
            artifacts = spec.get("raw_artifacts")
            raw_base = source_registry_path.parent
        if not isinstance(artifacts, list) or not artifacts:
            source_missing.append(f"gate_a_manifest.raw_artifacts.{dataset}")
            continue
        expected_files = spec.get("files", [spec.get("file")] if spec.get("file") else [])
        expected_names = {str(row.get("name")) if isinstance(row, dict) else str(row) for row in expected_files}
        verified_raw[dataset] = 0
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict) or not artifact.get("path") or not artifact.get("sha256"):
                source_missing.append(f"{dataset}.raw_artifacts[{index}] path/sha256")
                continue
            source_name = str(artifact.get("source_name", Path(str(artifact["path"])).name))
            if expected_names and source_name not in expected_names:
                source_problems.append(f"{dataset} undeclared source artifact: {source_name}")
                continue
            raw_path = _resolve(raw_base, str(artifact["path"]))
            if not raw_path.is_file():
                source_problems.append(f"{dataset} raw artifact missing: {raw_path}")
                continue
            actual = sha256_file(raw_path)
            if actual != artifact["sha256"]:
                source_problems.append(f"{dataset} raw artifact hash mismatch: {raw_path}")
                continue
            verified_raw[dataset] += 1
        if expected_names:
            bound_names = {str(row.get("source_name", Path(str(row.get("path", ""))).name)) for row in artifacts if isinstance(row, dict)}
            missing_names = sorted(expected_names - bound_names)
            if missing_names:
                source_problems.append(f"{dataset} source files not hash-bound: {missing_names}")
    checks["source_revisions_and_raw_hashes"] = _check(source_problems, source_missing, verified_raw_artifacts=verified_raw)
    checks["source_licenses"] = _check(license_problems)

    parse_problems = inference_errors + gold_errors
    inference_ids = [_identity(row) for row in inference]
    gold_ids = [_identity(row) for row in gold]
    duplicates = [identity for identity, count in Counter(inference_ids).items() if count > 1]
    gold_duplicates = [identity for identity, count in Counter(gold_ids).items() if count > 1]
    if duplicates:
        parse_problems.append(f"duplicate inference identities: {duplicates[:5]}")
    if gold_duplicates:
        parse_problems.append(f"duplicate gold identities: {gold_duplicates[:5]}")
    checks["unique_identities"] = _check(parse_problems, inference_rows=len(inference), gold_rows=len(gold))
    missing_gold = sorted(set(inference_ids) - set(gold_ids))
    extra_gold = sorted(set(gold_ids) - set(inference_ids))
    checks["inference_gold_identity_equality"] = _check(
        ([f"{len(missing_gold)} identities missing from gold"] if missing_gold else [])
        + ([f"{len(extra_gold)} extra gold identities"] if extra_gold else []),
        missing_from_gold=missing_gold[:20],
        extra_in_gold=extra_gold[:20],
    )

    hash_problems = []
    for index, row in enumerate(inference):
        declared = row.get("input_hash")
        if not isinstance(declared, str) or not SHA256_RE.fullmatch(declared):
            hash_problems.append(f"row {index} missing valid input_hash")
            continue
        actual = sha256_json({key: value for key, value in row.items() if key != "input_hash"})
        if actual != declared:
            hash_problems.append(f"{_identity(row)} input_hash mismatch")
    checks["input_hashes"] = _check(hash_problems)

    leakage = []
    for row in inference:
        for key in _nested_keys(row):
            leaf = re.sub(r"\[\d+\]", "", key.rsplit(".", 1)[-1]).lower()
            if leaf in FORBIDDEN_INFERENCE_KEYS or any(part in leaf for part in FORBIDDEN_KEY_PARTS):
                leakage.append(f"{_identity(row)}:{key}")
    checks["no_inference_leakage"] = _check(
        [f"forbidden inference keys: {leakage[:20]}"] if leakage else [],
        forbidden_key_occurrences=len(leakage),
    )

    gold_problems = []
    gold_by_id = {_identity(row): row for row in gold}
    for row in gold:
        identity = _identity(row)
        if not all(identity):
            gold_problems.append(f"invalid gold identity: {identity}")
        if not isinstance(row.get("answer"), list) or not row["answer"]:
            gold_problems.append(f"{identity} missing non-empty answer list")
        if not row.get("cluster_id"):
            gold_problems.append(f"{identity} missing cluster_id")
        if row.get("pair_id") is not None:
            if not isinstance(row.get("should_answer_change"), bool) or not row.get("change_direction"):
                gold_problems.append(f"{identity} paired gold lacks change metadata")
    checks["gold_completeness"] = _check(gold_problems)

    counts = Counter(dataset for dataset, _ in inference_ids)
    expected_rows = {"medpic": 467, "clir": 500, "medeinst": 1000, "medcounterfact": 400}
    count_problems = [f"{dataset}: expected {target}, found {counts.get(dataset, 0)}" for dataset, target in expected_rows.items() if counts.get(dataset, 0) != target]
    clir_counts = Counter(str(row.get("task_family", "")) for row in inference if row.get("dataset") == "clir")
    clir_files = sources.get("clir", {}).get("files", []) if isinstance(sources, dict) else []
    clir_targets = {str(row.get("task")): int(row.get("pilot_count", 0)) for row in clir_files if isinstance(row, dict) and row.get("task")}
    count_problems.extend(f"clir/{task}: expected {target}, found {clir_counts.get(task, 0)}" for task, target in sorted(clir_targets.items()) if clir_counts.get(task, 0) != target)
    adapters = manifest.get("adapters", {}) if isinstance(manifest, dict) else {}
    adapter_missing = []
    for dataset in DATASETS:
        value = adapters.get(dataset) if isinstance(adapters, dict) else None
        if not isinstance(value, dict) or value.get("status") != "pass" or not value.get("evidence"):
            adapter_missing.append(f"{dataset} passing adapter evidence")
    checks["adapters_and_target_counts"] = _check(count_problems, adapter_missing, dataset_counts=dict(counts), clir_task_counts=dict(clir_counts))

    pairs: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    clusters: dict[tuple[str, str], int] = Counter()
    for row in gold:
        dataset = str(row.get("dataset", ""))
        if row.get("pair_id") is not None:
            pairs[(dataset, str(row["pair_id"]))].append(row)
        if row.get("cluster_id"):
            clusters[(dataset, str(row["cluster_id"]))] += 1
    malformed_pairs = [key for key, rows in pairs.items() if len(rows) < 2]
    checks["pair_and_cluster_structure"] = _check(
        [f"non-two-member pairs: {malformed_pairs[:20]}"] if malformed_pairs else [],
        pair_counts=dict(Counter(dataset for dataset, _ in pairs)),
        cluster_counts=dict(Counter(dataset for dataset, _ in clusters)),
    )

    inference_by_id = {_identity(row): row for row in inference}
    blindness = []
    for (dataset, pair_id), pair_rows in pairs.items():
        pair_roles = {str(row.get("variant", "")).lower() for row in pair_rows if str(row.get("variant", "")).lower() in PAIR_ROLE_VALUES}
        if len({str(row.get("variant", "")).lower() for row in pair_rows}) > 1:
            pair_roles.update(str(row.get("variant", "")).lower() for row in pair_rows if row.get("variant"))
        for gold_row in pair_rows:
            current = inference_by_id.get(_identity(gold_row), {})
            secrets = {pair_id.lower()}
            secrets.update(value.lower() for value in _keyed_strings(gold_row.get("metadata", {}), ("case_id", "raw_case_id", "source_record_id")) if value)
            visible = [str(current.get("item_id", "")), str(current.get("variant", ""))] + _strings(current.get("metadata", {}))
            for value in visible:
                lowered = value.lower()
                for secret in secrets:
                    if _exposes_secret(lowered, secret):
                        blindness.append(f"{_identity(gold_row)} exposes pair/case id {secret!r}")
                        break
                for role in pair_roles:
                    if role and re.search(rf"(^|[^a-z0-9]){re.escape(role)}([^a-z0-9]|$)", lowered):
                        blindness.append(f"{_identity(gold_row)} exposes pair role {role!r}")
                        break
    checks["pair_blind_inference_values"] = _check(
        [f"pair-visible inference values: {blindness[:20]}"] if blindness else [],
        violations=len(blindness),
    )

    cpv_question_problems = []
    for (dataset, pair_id), pair_rows in pairs.items():
        if dataset != "cpv":
            continue
        questions = [" ".join(str(inference_by_id.get(_identity(row), {}).get("question", "")).split()) for row in pair_rows]
        if not questions or any(not question for question in questions) or len(set(questions)) != len(questions):
            cpv_question_problems.append(f"CPV unit {pair_id}: {len(set(questions))} distinct questions for {len(questions)} rows")
    checks["cpv_variant_questions"] = _check(
        [f"non-distinct CPV variant questions: {cpv_question_problems[:20]}"] if cpv_question_problems else [],
        units_checked=sum(dataset == "cpv" for dataset, _ in pairs),
    )

    capabilities = manifest.get("capabilities", {}) if isinstance(manifest, dict) else {}
    registry_medpic = sources.get("medpic", {}).get("capabilities", {}) if isinstance(sources, dict) else {}
    medpic_cap = _evidence_check(capabilities.get("medpic_official_linked_pairs"), manifest_path.parent, "MedPIC official linked-pair mapping")
    if registry_medpic.get("official_pair_map") is not True:
        medpic_cap.setdefault("problems", []).append("source registry declares medpic.capabilities.official_pair_map=false or missing")
        medpic_cap["status"] = "fail"
    medpic_pairs = sum(dataset == "medpic" for dataset, _ in pairs)
    if medpic_pairs != 89:
        medpic_cap.setdefault("problems", []).append(f"expected 89 MedPIC pairs, found {medpic_pairs}")
        medpic_cap["status"] = "fail"
    medpic_cap["observed_pairs"] = medpic_pairs
    checks["medpic_official_89_linked_pairs"] = medpic_cap

    registry_clir = sources.get("clir", {}).get("capabilities", {}) if isinstance(sources, dict) else {}
    repository_problems = [] if registry_clir.get("repository_evidence") is True else ["source registry declares CLIR repository_evidence=false or missing"]
    repository_missing = [] if verified_raw.get("clir", 0) else ["verified CLIR raw repository artifact"]
    no_observations = [str(row.get("item_id")) for row in inference if row.get("dataset") == "clir" and not _has_repository_observations(row)]
    if no_observations:
        repository_problems.append(f"{len(no_observations)} CLIR rows lack repository observations; a sole TSS ['all'] marker is not evidence")
    checks["clir_repository_evidence"] = _check(repository_problems, repository_missing, verified_raw_artifacts=verified_raw.get("clir", 0), rows_without_observations=len(no_observations))

    derived = []
    for row in inference:
        if row.get("dataset") != "clir":
            continue
        evidence = row.get("fixed_evidence", [])
        allowed = CLIR_ALLOWED_EVIDENCE_KEYS.get(str(row.get("task_family", "")), set())
        if not isinstance(evidence, list):
            derived.append(f"{row.get('item_id')}:fixed_evidence is not a list")
            continue
        for index, value in enumerate(evidence):
            if not isinstance(value, dict):
                derived.append(f"{row.get('item_id')}:fixed_evidence[{index}] is not an observation object")
                continue
            for key in sorted(set(value) - allowed):
                derived.append(f"{row.get('item_id')}:fixed_evidence[{index}].{key}")
    checks["clir_no_answer_derived_evidence"] = _check(
        [f"non-observable or answer-derived CLIR evidence: {derived[:20]}"] if derived else [],
        forbidden_field_occurrences=len(derived),
    )
    clir_full_ts = _evidence_check(capabilities.get("clir_full_ts"), manifest_path.parent, "CLIR Full-TS repository evidence")
    if registry_clir.get("full_timeseries") is not True:
        clir_full_ts.setdefault("problems", []).append("source registry declares clir.capabilities.full_timeseries=false or missing")
        clir_full_ts["status"] = "fail"
    empty_ts = [row.get("item_id") for row in inference if row.get("dataset") == "clir" and not row.get("time_series")]
    if empty_ts:
        clir_full_ts.setdefault("problems", []).append(f"{len(empty_ts)} CLIR rows lack Full-TS observations")
        clir_full_ts["status"] = "fail"
    clir_full_ts["rows_with_full_ts"] = counts.get("clir", 0) - len(empty_ts)
    checks["clir_full_ts"] = clir_full_ts

    clir_pairs_cap = _evidence_check(capabilities.get("clir_official_causal_edit_pairs"), manifest_path.parent, "CLIR official causal-edit mapping")
    if registry_clir.get("official_edit_pairs") is not True:
        clir_pairs_cap.setdefault("problems", []).append("source registry declares clir.capabilities.official_edit_pairs=false or missing")
        clir_pairs_cap["status"] = "fail"
    clir_pairs = [rows for (dataset, _), rows in pairs.items() if dataset == "clir" and any(row.get("should_answer_change") is True for row in rows)]
    declared_pair_count = capabilities.get("clir_official_causal_edit_pairs", {}).get("pair_count") if isinstance(capabilities.get("clir_official_causal_edit_pairs"), dict) else None
    if not clir_pairs:
        clir_pairs_cap.setdefault("missing", []).append("at least one bound CLIR causal-edit pair")
        if clir_pairs_cap["status"] == "pass":
            clir_pairs_cap["status"] = "insufficient"
    if declared_pair_count is not None and declared_pair_count != len(clir_pairs):
        clir_pairs_cap.setdefault("problems", []).append(f"declared {declared_pair_count} CLIR causal pairs, found {len(clir_pairs)}")
        clir_pairs_cap["status"] = "fail"
    clir_pairs_cap["observed_pairs"] = len(clir_pairs)
    checks["clir_official_causal_edit_pairs"] = clir_pairs_cap

    fixed_problems = []
    for row in inference:
        if row.get("dataset") != "medcounterfact":
            continue
        policy = row.get("retrieval_policy", row.get("metadata", {}).get("retrieval_policy") if isinstance(row.get("metadata"), dict) else None)
        if not row.get("fixed_evidence"):
            fixed_problems.append(f"{row.get('item_id')} has no fixed evidence")
        if policy != "fixed_evidence_only_primary":
            fixed_problems.append(f"{row.get('item_id')} retrieval policy is not fixed-evidence-only")
    checks["medcounterfact_fixed_evidence"] = _check(fixed_problems)
    registry_mcf = sources.get("medcounterfact", {}).get("capabilities", {}) if isinstance(sources, dict) else {}
    if registry_mcf.get("fixed_evidence") is not True:
        checks["medcounterfact_fixed_evidence"]["problems"].append("source registry lacks fixed_evidence capability")
        checks["medcounterfact_fixed_evidence"]["status"] = "fail"

    categories = Counter()
    for row in gold:
        if row.get("dataset") != "medcounterfact" or row.get("variant") not in {"counterfactual", "replaced"}:
            continue
        metadata = row.get("metadata", {}) if isinstance(row.get("metadata"), dict) else {}
        category = str(metadata.get("counterfactual_category", metadata.get("MainCategory", metadata.get("main_category", "")))).lower().replace("-", "_").replace(" ", "_")
        categories[category] += 1
    category_problems = [f"MedCounterFact/{category}: expected 50, found {categories.get(category, 0)}" for category in sorted(CF_CATEGORIES) if categories.get(category, 0) != 50]
    medeinst_pairs = sum(dataset == "medeinst" for dataset, _ in pairs)
    if medeinst_pairs != 500:
        category_problems.append(f"MedEinst: expected 500 pairs, found {medeinst_pairs}")
    checks["pair_category_targets"] = _check(category_problems, medcounterfact_categories=dict(categories), medeinst_pairs=medeinst_pairs)
    control_units = {}
    control_problems = []
    for dataset in ("remedqa", "cpv"):
        pilot = sources.get(dataset, {}).get("pilot", {}) if isinstance(sources, dict) else {}
        target = int(pilot.get("count", 300))
        unit_ids = {str(row.get("pair_id") or row.get("cluster_id")) for row in gold if row.get("dataset") == dataset and (row.get("pair_id") or row.get("cluster_id"))}
        control_units[dataset] = len(unit_ids)
        if len(unit_ids) != target:
            control_problems.append(f"{dataset}: expected {target} {pilot.get('count_unit', 'units')}, found {len(unit_ids)}")
    checks["control_counts"] = _check(control_problems, **control_units)

    blockers = []
    for name, result in checks.items():
        if result["status"] != "pass":
            details = result.get("problems", []) + result.get("missing", [])
            blockers.append({"check": name, "status": result["status"], "details": details})
    return {
        "schema_version": 1,
        "decision": "proceed" if not blockers else "stop_before_inference",
        "checks": checks,
        "blockers": blockers,
        "inputs": {
            "source_registry": str(source_registry_path),
            "source_registry_sha256": sha256_file(source_registry_path),
            "gate_a_manifest": str(manifest_path),
            "gate_a_manifest_sha256": sha256_file(manifest_path),
            "inference": str(inference_path),
            "inference_sha256": sha256_file(inference_path),
            "gold": str(gold_path),
            "gold_sha256": sha256_file(gold_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-registry", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--inference", required=True, type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = audit_gate_a(args.source_registry, args.manifest, args.inference, args.gold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": report["decision"], "output": str(args.output), "blockers": len(report["blockers"])}, sort_keys=True))
    return 0 if report["decision"] == "proceed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
