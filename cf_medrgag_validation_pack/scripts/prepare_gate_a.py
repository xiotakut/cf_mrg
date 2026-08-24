#!/usr/bin/env python3
"""Acquire pinned Gate-A sources and create separated inference/gold pilots."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import random
import re
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any


DATASETS = ("medpic", "clir", "medeinst", "medcounterfact", "remedqa", "cpv")
HIDDEN_KEYS = {
    "answer", "answers", "answer_idx", "answer_index", "answer_key", "gold", "gold_answer",
    "ground_truth", "label", "labels", "pair_id", "case_id", "cluster_id", "counterpart",
    "counterpart_id", "change_direction", "should_answer_change", "should_change",
    "evaluator_metadata", "evaluation_metadata", "category", "maincategory",
}
HIDDEN_KEY_PARTS = ("answer", "gold", "pair", "counterpart", "change")
TASKS = {
    "medpic": "medication_rule_cf",
    "medeinst": "diagnosis_cf",
    "medcounterfact": "evidence_cf",
    "remedqa": "invariance_control",
    "cpv": "invariance_control",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nested(record: dict[str, Any], dotted: str | None) -> Any:
    value: Any = record
    for part in (dotted or "").split("."):
        if not part:
            return None
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def first(record: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        value = nested(record, name)
        if value is not None:
            return value
    return default


def hidden_key(value: Any) -> bool:
    normalized = str(value).lower().replace("-", "_")
    return normalized in HIDDEN_KEYS or any(part in normalized for part in HIDDEN_KEY_PARTS)


def clean_visible(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): clean_visible(child)
            for key, child in value.items()
            if not hidden_key(key)
        }
    if isinstance(value, list):
        return [clean_visible(child) for child in value]
    return value


def assert_answer_free(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if hidden_key(key):
                raise ValueError(f"inference leakage at {path}.{key}")
            assert_answer_free(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_answer_free(child, f"{path}[{index}]")


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "source"


def _download(url: str, path: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urllib.request.urlopen(url) as response:
            data = response.read()
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
    digest = sha256_file(path)
    if expected_sha256 and digest != expected_sha256:
        raise ValueError(f"source SHA-256 mismatch for {url}")
    return {"url": url, "cache_path": str(path.resolve()), "sha256": digest, "bytes": path.stat().st_size}


def _source_url(entry: dict[str, Any], file_spec: str | dict[str, Any]) -> tuple[str, str, str | None]:
    if isinstance(file_spec, dict):
        name = str(file_spec["name"])
        if file_spec.get("url"):
            return name, str(file_spec["url"]), file_spec.get("sha256")
    else:
        name = str(file_spec)
    repo = entry["repo_id"]
    revision = entry["revision"]
    if entry["source"] == "github":
        url = f"https://raw.githubusercontent.com/{repo}/{revision}/{name}"
    else:
        quoted = urllib.parse.quote(name, safe="/")
        url = f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{quoted}?download=true"
    return name, url, file_spec.get("sha256") if isinstance(file_spec, dict) else None


def _records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as parquet
        except ImportError as exc:
            raise RuntimeError("reading official parquet sources requires pyarrow") from exc
        return parquet.read_table(path).to_pylist()
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    value = json.loads(text)
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict) and isinstance(value.get("rows"), list):
        return [row.get("row", row) for row in value["rows"] if isinstance(row, dict)]
    if isinstance(value, dict):
        return [dict(row, __source_id=str(key)) for key, row in value.items() if isinstance(row, dict)]
    raise ValueError(f"unsupported source shape: {path}")


def _rows_url(entry: dict[str, Any], config: str, split: str, offset: int, length: int) -> str:
    override = entry.get("rows_url")
    if isinstance(entry.get("rows_urls"), dict):
        override = entry["rows_urls"].get(split, entry["rows_urls"].get(config))
    if override:
        return str(override).format(offset=offset, length=length, config=config, split=split)
    query = urllib.parse.urlencode({"dataset": entry["repo_id"], "config": config, "split": split, "offset": offset, "length": length, "revision": entry["revision"]})
    return "https://datasets-server.huggingface.co/rows?" + query


def acquire_rows_api(dataset: str, entry: dict[str, Any], cache_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    splits = entry.get("split") if isinstance(entry.get("split"), list) else [entry.get("split", "train")]
    targets = [(str(entry.get("config", "default")), str(split)) for split in splits]
    target = int(entry["pilot"]["count"])
    page_size = int(entry.get("rows_page_size", 100))
    records: list[dict[str, Any]] = []
    sources = []
    for config, split in targets:
        offset = 0
        while True:
            url = _rows_url(entry, config, split, offset, page_size)
            path = cache_root / dataset / entry["revision"] / f"rows-{_safe_name(split)}-{offset}.json"
            source = _download(url, path)
            declared = entry.get("file")
            if isinstance(entry.get("files"), list):
                declared = next((value for value in entry["files"] if Path(str(value)).name.startswith(split + "-")), entry["files"][0] if len(entry["files"]) == 1 else split)
            source.update({"kind": "datasets_server_rows", "config": config, "split": split, "offset": offset, "source_name": str(declared)})
            sources.append(source)
            payload = json.loads(path.read_text(encoding="utf-8"))
            page = [row.get("row", row) for row in payload.get("rows", []) if isinstance(row, dict)]
            for row in page:
                if isinstance(row, dict):
                    records.append({**row, "__gate_a_source_config": config, "__gate_a_source_split": split})
            total = int(payload.get("num_rows_total", len(page)))
            offset += len(page)
            if not page or offset >= total:
                break
            # Joined controls need every selected ID across configs; simple CPV
            # needs enough IDs, but fetching beyond the pilot cannot change a
            # frozen seeded sample. Acquire the declared split completely.
            if len(page) < page_size:
                break
    return records, sources


def acquire_files(dataset: str, entry: dict[str, Any], cache_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specs = entry["files"] if "files" in entry else [entry["file"]]
    records: list[dict[str, Any]] = []
    sources = []
    for index, spec in enumerate(specs):
        name, url, expected = _source_url(entry, spec)
        path = cache_root / dataset / entry["revision"] / f"{index:02d}-{_safe_name(Path(name).name)}"
        source = _download(url, path, expected)
        source.update({"kind": "raw_file", "name": name, "source_name": name})
        sources.append(source)
        defaults = spec if isinstance(spec, dict) else {}
        role = defaults.get("role") or ("original" if "original" in name.lower() else "replacement" if "replaced" in name.lower() else None)
        task = defaults.get("task")
        split = defaults.get("split") or Path(name).name.split("-00000-of-", 1)[0]
        for row in _records(path):
            records.append({**row, "__gate_a_file": name, "__gate_a_role": role, "__gate_a_task": task, "__gate_a_source_split": split})
    return records, sources


def stable_key(row: dict[str, Any]) -> tuple[str, bytes]:
    identifier = first(row, "item_id", "instance_id", "id", "index", "case_id", "metadata.id", "__source_id", default="")
    return str(identifier), canonical_bytes(row)


def seeded_sample(rows: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=stable_key)
    if len(ordered) < count:
        raise ValueError(f"pilot requires {count} rows but source has {len(ordered)}")
    return sorted(random.Random(seed).sample(ordered, count), key=stable_key)


def medcounterfact_category(row: dict[str, Any]) -> str:
    value = str(first(row, "metadata.MainCategory", "MainCategory", "category", default="")).lower().replace("-", " ").replace("_", " ").strip()
    return {"ood": "OOD", "id": "ID", "nonce": "nonce", "nonsense tokens": "nonce", "poison": "poison"}.get(value, value)


def clir_visible_evidence(value: Any, task: str) -> list[dict[str, Any]]:
    """Keep only observations available for the declared CLIR task."""
    if not isinstance(value, dict):
        return []
    allowed = {
        "intervention_response": {
            "source", "intervention_event_hour", "context_end_time", "intervention_items_at_event_hour",
            "response_variable", "response_variable_label", "baseline_observation", "post_observations",
        },
        "next_value_interval_forecasting": {
            "source", "anchor_time", "horizon_hours", "target_variable", "target_variable_label",
            "previous_same_variable_observation", "recent_visible_same_variable_observations",
        },
    }
    evidence = {key: value[key] for key in allowed.get(task, set()) if key in value}
    return [clean_visible(evidence)] if evidence else []


def opaque_item_id(dataset: str, entry: dict[str, Any], row: dict[str, Any], raw_id: Any, raw_variant: str, question: str) -> str:
    material = {
        "namespace": "gate-a-item-v1", "dataset": dataset, "revision": entry["revision"],
        "raw_id": str(raw_id), "source_file": row.get("__gate_a_file"), "source_split": row.get("__gate_a_source_split"),
        "source_role": row.get("__gate_a_role"), "raw_variant": raw_variant, "visible_question": question,
    }
    return f"{dataset}-{sha256_bytes(canonical_bytes(material))[:32]}"


def select_rows(dataset: str, rows: list[dict[str, Any]], entry: dict[str, Any]) -> list[dict[str, Any]]:
    pilot = entry["pilot"]
    count, seed = int(pilot["count"]), int(pilot.get("seed", 13))
    if dataset == "medpic":
        if len(rows) != count:
            raise ValueError(f"MedPIC boundary requires exactly {count} rows; found {len(rows)}")
        return sorted(rows, key=stable_key)
    if dataset == "clir":
        selected = []
        files = entry["files"]
        for index, spec in enumerate(files):
            name = spec["name"] if isinstance(spec, dict) else str(spec)
            candidates = [row for row in rows if row.get("__gate_a_file") == name]
            per_file = int(spec.get("pilot_count", count // len(files))) if isinstance(spec, dict) else count // len(files)
            selected.extend(seeded_sample(candidates, per_file, seed + index))
        return selected
    if dataset == "medeinst":
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[str(first(row, entry.get("pair_key"), default=""))].append(row)
        complete = {key: values for key, values in groups.items() if key and {str(first(row, "case_type", "variant", default="")).lower() for row in values} >= {"control", "trap"}}
        chosen = seeded_sample([{"id": key} for key in complete], count, seed)
        return [row for marker in chosen for row in sorted(complete[marker["id"]], key=stable_key)]
    if dataset == "medcounterfact":
        originals = [row for row in rows if row.get("__gate_a_role") == "original"]
        replacements = [row for row in rows if row.get("__gate_a_role") == "replacement"]
        by_pair = defaultdict(list)
        for row in originals:
            by_pair[str(first(row, entry.get("pair_key"), default=""))].append(row)
        chosen_replacements = []
        used_pair_ids = set()
        per_category = count // 4
        for index, category in enumerate(("OOD", "ID", "nonce", "poison")):
            candidates = [row for row in replacements if medcounterfact_category(row).lower() == category.lower() and str(first(row, entry.get("pair_key"), default="")) not in used_pair_ids]
            chosen = seeded_sample(candidates, per_category, seed + index)
            chosen_replacements.extend(chosen)
            used_pair_ids.update(str(first(row, entry.get("pair_key"), default="")) for row in chosen)
        companions = {}
        for row in chosen_replacements:
            pair_id = str(first(row, entry.get("pair_key"), default=""))
            if not by_pair.get(pair_id):
                raise ValueError(f"MedCounterFact selected row lacks original companion: {pair_id}")
            for original in by_pair[pair_id]:
                companions[canonical_bytes(original)] = original
        return sorted([*chosen_replacements, *companions.values()], key=stable_key)
    pair_key = entry.get("pair_key")
    if pair_key:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            key = str(first(row, pair_key, default=""))
            if key:
                groups[key].append(row)
        if dataset == "cpv":
            groups = {
                key: values for key, values in groups.items()
                if len(values) >= 2
                and len({str(first(row, "case_text", default="")) for row in values}) == len(values)
            }
        chosen = seeded_sample([{"id": key} for key in groups], count, seed)
        return [row for marker in chosen for row in sorted(groups[marker["id"]], key=stable_key)]
    return seeded_sample(rows, count, seed)


def parse_clir_question(text: str) -> tuple[str, dict[str, str]]:
    marker = re.split(r"\n\s*Options:\s*\n", text, maxsplit=1, flags=re.I)
    if len(marker) != 2:
        return text, {}
    options = {}
    for match in re.finditer(r"(?ms)^([A-Z])\.\s*(.*?)(?=\n[A-Z]\.\s|\Z)", marker[1].strip()):
        options[match.group(1)] = " ".join(match.group(2).split())
    return marker[0].strip(), options


def normalize_options(value: Any) -> dict[str, str] | None:
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return None
    if isinstance(value, dict):
        return {str(key): str(text) for key, text in value.items()}
    if isinstance(value, list):
        return {chr(65 + index): str(text) for index, text in enumerate(value)}
    return None


def row_options(row: dict[str, Any]) -> dict[str, str] | None:
    options = normalize_options(first(row, "options", "choices"))
    if options:
        return options
    lettered = {}
    for letter in "ABCDEFGHIJ":
        value = first(row, f"option_{letter.lower()}", f"option_{letter}")
        if value is not None:
            lettered[letter] = str(value)
    return lettered or None


def normalize_answer(value: Any, dataset: str) -> list[str]:
    if isinstance(value, list):
        return [str(answer) for answer in value]
    if value is None:
        raise ValueError(f"{dataset} row has no public answer")
    if dataset == "medpic" and isinstance(value, str):
        return [part for part in re.split(r"[,\s]+", value.strip()) if part]
    return [str(value)]


def adapt(dataset: str, row: dict[str, Any], entry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    raw_id = first(row, "item_id", "instance_id", "id", "index", "__source_id", "case_id")
    if raw_id is None:
        raise ValueError(f"{dataset} row has no item identifier")
    gold_variant = str(first(row, "variant", "case_type", default=row.get("__gate_a_role") or row.get("__gate_a_source_split") or "base"))
    if dataset == "medcounterfact" and gold_variant == "replacement":
        gold_variant = "counterfactual"
    pair_id = first(row, entry.get("pair_key"))
    task = row.get("__gate_a_task") or TASKS.get(dataset, "temporal_cf")
    question = str(first(row, "question", "patient_vignette", "narrative", "prompt", "text", default="")).strip()
    if dataset == "cpv":
        question = str(first(row, "case_text", "question", default="")).strip()
    options = row_options(row)
    if dataset == "medpic" and row.get("patient_vignette"):
        question = str(row["patient_vignette"]).strip() + "\n\n" + str(row.get("question", "")).strip()
    if dataset == "clir":
        question, parsed = parse_clir_question(question)
        options = options or parsed
    answer_names = ("answer", "answers", "gold_answer", "ground_truth", "label", "metadata.answer")
    if dataset in {"remedqa", "cpv"} and first(row, "answer_idx", "answer_index") is not None:
        answer = first(row, "answer_idx", "answer_index")
    else:
        answer = first(row, *answer_names)
    fixed_evidence = first(row, "article_summaries", default=[]) if dataset == "medcounterfact" else clir_visible_evidence(row.get("evidence"), str(task)) if dataset == "clir" else first(row, "fixed_evidence", default=[])
    if isinstance(fixed_evidence, str):
        fixed_evidence = [fixed_evidence]
    elif not isinstance(fixed_evidence, list):
        fixed_evidence = [fixed_evidence] if fixed_evidence is not None else []
    metadata = {
        "source_revision": entry["revision"],
        "retrieval_policy": "fixed_evidence_only_primary" if dataset == "medcounterfact" else "repository_evidence_not_full_timeseries" if dataset == "clir" else "declared_dataset_policy",
        "evidence_role": "repository_anchor_observations" if dataset == "clir" else "fixed_in_world_evidence" if dataset == "medcounterfact" else None,
        "required_output_fields": ["evidence_conclusion", "real_world_safety_flag"] if dataset == "medcounterfact" else ["answer"],
    }
    inference = {
        "item_id": opaque_item_id(dataset, entry, row, raw_id, gold_variant, question),
        "dataset": dataset,
        "task_family": str(task),
        "variant": "item",
        "question": question,
        "options": options,
        "patient_state": clean_visible(first(row, "patient_state", default={})),
        "time_series": clean_visible(first(row, "time_series", default=[])),
        "fixed_evidence": clean_visible(fixed_evidence),
        "candidate_actions": clean_visible(first(row, "candidate_actions", default=[])),
        "metadata": clean_visible(metadata),
    }
    if not inference["question"]:
        raise ValueError(f"{dataset}/{raw_id} has no question")
    category = first(row, "metadata.MainCategory", "MainCategory", "category")
    evidence = first(row, "evidence", "gold_evidence", "supporting_timestamps", "article_summaries")
    gold = {
        "item_id": inference["item_id"],
        "dataset": dataset,
        "answer": normalize_answer(answer, dataset),
        "pair_id": str(pair_id) if pair_id is not None else None,
        "cluster_id": str(first(row, "episode_id", "stay_id", entry.get("pair_key"), default=inference["item_id"])) or inference["item_id"],
        "category": str(category) if category is not None else None,
        "variant": gold_variant,
        "evidence": evidence,
        "change_direction": first(row, "change_direction"),
        "should_answer_change": first(row, "should_answer_change"),
        "safety_flag": first(row, "safety_flag", "metadata.safety_flag"),
        "metadata": {},
    }
    if pair_id is not None:
        if dataset == "medeinst":
            gold.update({"should_answer_change": True, "change_direction": "diagnosis_flip"})
        elif dataset in {"remedqa", "cpv"}:
            gold.update({"should_answer_change": False, "change_direction": "invariant"})
        elif dataset == "medcounterfact":
            gold.update({"should_answer_change": False, "change_direction": "evidence_world_invariant"})
    if dataset == "medcounterfact" and gold_variant == "counterfactual":
        canonical_category = {"ood": "non_medical", "id": "medical", "nonce": "nonce", "poison": "toxic"}.get(medcounterfact_category(row).lower())
        gold["metadata"]["counterfactual_category"] = canonical_category
    assert_answer_free(inference)
    inference["input_hash"] = sha256_bytes(canonical_bytes(inference))
    return inference, gold


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    data = b"".join(canonical_bytes(row) + b"\n" for row in rows)
    path.write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parents[1] / "configs" / "gate_a_sources.json")
    parser.add_argument("--work-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    registry = json.loads(args.sources.read_text(encoding="utf-8"))
    entries = registry.get("datasets", {})
    if set(entries) != set(DATASETS):
        raise ValueError(f"source registry must contain exactly {list(DATASETS)}")
    args.work_dir.mkdir(parents=True, exist_ok=True)
    cache_root = args.work_dir / "raw"
    inference_rows: list[dict[str, Any]] = []
    gold_rows: list[dict[str, Any]] = []
    manifest_sources = {}
    selected_counts = {}
    seen = set()
    for dataset in DATASETS:
        entry = entries[dataset]
        for required in ("revision", "license", "pilot", "capabilities", "source", "repo_id"):
            if required not in entry:
                raise ValueError(f"{dataset} registry entry lacks {required}")
        if dataset in {"remedqa", "cpv"} and (entry.get("rows_url") or entry.get("rows_urls")):
            records, sources = acquire_rows_api(dataset, entry, cache_root)
        else:
            records, sources = acquire_files(dataset, entry, cache_root)
        selected = select_rows(dataset, records, entry)
        for row in selected:
            inference, gold = adapt(dataset, row, entry)
            key = (dataset, inference["item_id"])
            if key in seen:
                suffix = sha256_bytes(canonical_bytes(row))[:10]
                inference["item_id"] += f":{suffix}"
                gold["item_id"] = inference["item_id"]
                inference.pop("input_hash")
                inference["input_hash"] = sha256_bytes(canonical_bytes(inference))
                key = (dataset, inference["item_id"])
            if key in seen:
                raise ValueError(f"duplicate adapted item: {key}")
            seen.add(key)
            inference_rows.append(inference)
            gold_rows.append(gold)
        selected_counts[dataset] = len(selected)
        manifest_sources[dataset] = {
            "revision": entry["revision"], "license": entry["license"], "capabilities": entry["capabilities"],
            "pilot": entry["pilot"], "raw_record_count": len(records), "selected_row_count": len(selected), "artifacts": sources,
        }
    inference_path = args.work_dir / "pilot.inference.jsonl"
    gold_path = args.work_dir / "pilot.gold.jsonl"
    manifest_path = args.work_dir / "gate_a_manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite {manifest_path}")
    write_jsonl(inference_path, inference_rows)
    write_jsonl(gold_path, gold_rows)
    manifest = {
        "artifact_type": "gate_a_pilot", "registry_version": registry.get("registry_version"),
        "source_registry_sha256": sha256_file(args.sources), "answer_key_isolation": True,
        "selection_before_evaluation": True, "datasets": manifest_sources, "selected_row_counts": selected_counts,
        "inference": {"path": inference_path.name, "rows": len(inference_rows), "sha256": sha256_file(inference_path)},
        "gold": {"path": gold_path.name, "rows": len(gold_rows), "sha256": sha256_file(gold_path)},
        "bindings": {
            "source_registry_sha256": sha256_file(args.sources),
            "inference_sha256": sha256_file(inference_path),
            "gold_sha256": sha256_file(gold_path),
        },
        "raw_artifacts": {
            dataset: [
                {"path": artifact["cache_path"], "source_name": artifact["source_name"], "sha256": artifact["sha256"]}
                for artifact in manifest_sources[dataset]["artifacts"]
            ]
            for dataset in DATASETS
        },
        "adapters": {
            dataset: {"status": "pass", "evidence": f"{selected_counts[dataset]} rows adapted from pinned, SHA-256-bound sources"}
            for dataset in DATASETS
        },
        "capabilities": {
            "medpic_official_linked_pairs": {
                "available": entries["medpic"]["capabilities"].get("official_pair_map") is True,
                "reason": "source registry declares no official linked-pair map",
            },
            "clir_full_ts": {
                "available": entries["clir"]["capabilities"].get("full_timeseries") is True,
                "reason": "public repository rows contain anchor evidence, not credentialed Full-TS observations",
            },
            "clir_official_causal_edit_pairs": {
                "available": entries["clir"]["capabilities"].get("official_edit_pairs") is True,
                "reason": "source registry declares official edit pairs unavailable",
            },
        },
    }
    manifest["manifest_sha256"] = sha256_bytes(canonical_bytes(manifest))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"work_dir": str(args.work_dir.resolve()), "rows": len(inference_rows), "counts": selected_counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
