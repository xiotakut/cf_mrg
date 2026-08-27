#!/usr/bin/env python3
"""Prepare and run the closed-set DeltaRank-MedRGAG pilot."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import difflib
import importlib.util
import json
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
RANK_METHODS = (
    "target_only_ranker",
    "medrgag_evidence_ranker",
    "full_pair_ranker",
    "pair_aware_ranker",
)
SCORE_METHODS = ("delta_profile_ranker", "shuffled_delta", "shuffled_profile")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def norm(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.strip().casefold().split()).rstrip(" .,:;!?")


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def paired_rows(path: Path) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(dict)
    for row in read_jsonl(path):
        if row.get("case_type") in {"control", "trap"}:
            grouped[str(row["case_id"])][row["case_type"]] = row
    return [
        {"case_id": case_id, "control": values["control"], "trap": values["trap"]}
        for case_id, values in sorted(grouped.items())
        if set(values) == {"control", "trap"}
    ]


def balanced_sample(pairs: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        by_label[pair["trap"]["ground_truth"]].append(pair)
    rng = random.Random(seed)
    for values in by_label.values():
        rng.shuffle(values)
    selected = []
    labels = sorted(by_label)
    while len(selected) < count and any(by_label.values()):
        for label in labels:
            if by_label[label] and len(selected) < count:
                selected.append(by_label[label].pop())
    if len(selected) != count:
        raise ValueError(f"only {len(selected)} complete pairs available")
    return selected


def parse_sections(text: str) -> dict[str, list[str]]:
    sections = {"demographics": [], "symptoms": [], "antecedents": []}
    section = "demographics"
    for raw in text.splitlines():
        line = " ".join(raw.strip().split())
        heading = line.rstrip(":").casefold()
        if heading in {"symptoms", "antecedents"}:
            section = heading
            continue
        if not line or set(line) == {"-"}:
            continue
        if section == "demographics" or line.startswith(("- ", "* ")):
            sections[section].append(re.sub(r"^[*-]\s*", "", line).strip(" ."))
    return sections


def structured_delta(control: str, trap: str) -> dict[str, Any]:
    old, new = parse_sections(control), parse_sections(trap)
    added: list[str] = []
    removed: list[str] = []
    changed: list[dict[str, str]] = []
    for section in ("demographics", "symptoms", "antecedents"):
        old_count, new_count = Counter(map(norm, old[section])), Counter(map(norm, new[section]))
        old_text = {norm(value): value for value in old[section]}
        new_text = {norm(value): value for value in new[section]}
        old_left = [old_text[key] for key, amount in (old_count - new_count).items() for _ in range(amount)]
        new_left = [new_text[key] for key, amount in (new_count - old_count).items() for _ in range(amount)]
        candidates = sorted(
            ((difflib.SequenceMatcher(None, norm(a), norm(b)).ratio(), i, j)
             for i, a in enumerate(old_left) for j, b in enumerate(new_left)),
            reverse=True,
        )
        used_old, used_new = set(), set()
        for similarity, i, j in candidates:
            if similarity < .68 or i in used_old or j in used_new:
                continue
            changed.append({"section": section, "old": old_left[i], "new": new_left[j]})
            used_old.add(i); used_new.add(j)
        removed.extend(old_left[i] for i in range(len(old_left)) if i not in used_old)
        added.extend(new_left[j] for j in range(len(new_left)) if j not in used_new)
    return {"added_findings": added, "removed_findings": removed, "changed_findings": changed}


def profiles_from_ddx(conditions: dict[str, Any], evidences: dict[str, Any],
                      labels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles = []
    for label in labels:
        name = label["canonical_name"]
        if name not in conditions:
            raise ValueError(f"DDXPlus profile is unmapped: {name}")
        condition = conditions[name]
        symptom_ids = list(condition.get("symptoms", {}))
        antecedent_ids = list(condition.get("antecedents", {}))
        profiles.append({
            "label_id": label["label_id"], "diagnosis": name,
            "symptom_evidence_ids": symptom_ids,
            "antecedent_evidence_ids": antecedent_ids,
            "symptoms": [evidences[key]["question_en"] for key in symptom_ids],
            "antecedents": [evidences[key]["question_en"] for key in antecedent_ids],
        })
    return profiles


def profile_similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
    a = set(left["symptom_evidence_ids"] + left["antecedent_evidence_ids"])
    b = set(right["symptom_evidence_ids"] + right["antecedent_evidence_ids"])
    return len(a & b) / len(a | b) if a | b else 0.0


def option_view(names: list[str], seed: str) -> dict[str, dict[str, Any]]:
    values = list(names)
    random.Random(seed).shuffle(values)
    return {LETTERS[index]: {"label": name} for index, name in enumerate(values)}


def prepare(train_raw: Path, test_raw: Path, conditions_path: Path, evidences_path: Path,
            output_dir: Path, dev_pairs: int, test_pairs: int, seed: int) -> dict[str, Any]:
    train_pairs, test_values = paired_rows(train_raw), paired_rows(test_raw)
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    evidences = json.loads(evidences_path.read_text(encoding="utf-8"))
    dataset_labels = {pair[member]["ground_truth"] for pair in train_pairs + test_values
                      for member in ("control", "trap")}
    if not dataset_labels <= set(conditions) or len(conditions) != 49:
        raise ValueError("official labels and DDXPlus conditions do not align")
    labels = [{"label_id": index, "canonical_name": name, "aliases": []}
              for index, name in enumerate(sorted(conditions))]
    profiles = profiles_from_ddx(conditions, evidences, labels)
    profile_by_name = {row["diagnosis"]: row for row in profiles}

    def adapt(values: list[dict[str, Any]], split: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        rows, deltas = [], []
        for pair in values:
            case_id = str(pair["case_id"])
            control_name, trap_name = pair["control"]["ground_truth"], pair["trap"]["ground_truth"]
            excluded = {control_name, trap_name}
            similarities = []
            for candidate in sorted(set(conditions) - excluded):
                similarity = max(profile_similarity(profile_by_name[candidate], profile_by_name[control_name]),
                                 profile_similarity(profile_by_name[candidate], profile_by_name[trap_name]))
                similarities.append((similarity, candidate))
            hard = [name for _, name in sorted(similarities, key=lambda row: (-row[0], row[1]))[:2]]
            pair_id = f"{split}-{case_id}"
            views = {
                "two_way": option_view([control_name, trap_name], f"{seed}:{pair_id}:two"),
                "four_way": option_view([trap_name, control_name, *hard], f"{seed}:{pair_id}:four"),
            }
            label_id = {row["canonical_name"]: row["label_id"] for row in labels}
            for options in views.values():
                for value in options.values():
                    value["label_id"] = label_id[value["label"]]
            rows.append({
                "pair_id": pair_id, "source_case_id": case_id, "split": split,
                "control": {"age": pair["control"]["age"], "sex": pair["control"]["sex"],
                            "narrative": pair["control"]["narrative"],
                            "label": control_name, "label_id": label_id[control_name]},
                "trap": {"age": pair["trap"]["age"], "sex": pair["trap"]["sex"],
                         "narrative": pair["trap"]["narrative"],
                         "label": trap_name, "label_id": label_id[trap_name]},
                "views": views, "hard_negative_labels": hard,
            })
            deltas.append({"pair_id": pair_id, "split": split,
                           **structured_delta(pair["control"]["narrative"], pair["trap"]["narrative"])})
        return rows, deltas

    dev_rows, dev_deltas = adapt(balanced_sample(train_pairs, dev_pairs, seed), "dev")
    test_rows, test_deltas = adapt(balanced_sample(test_values, test_pairs, seed + 1), "test")
    if {row["source_case_id"] for row in dev_rows} & {row["source_case_id"] for row in test_rows}:
        raise ValueError("official train and test case IDs overlap")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_jsonl(output_dir / "dev.jsonl", dev_rows)
    write_jsonl(output_dir / "test.jsonl", test_rows)
    write_jsonl(output_dir / "deltas.jsonl", dev_deltas + test_deltas)
    cache = output_dir / "cache"
    cache.mkdir(exist_ok=True)
    (cache / "profiles.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"labels": len(labels), "dev_pairs": len(dev_rows), "test_pairs": len(test_rows),
            "dev_nonempty_delta": sum(bool(row["added_findings"] or row["removed_findings"] or row["changed_findings"])
                                      for row in dev_deltas),
            "test_nonempty_delta": sum(bool(row["added_findings"] or row["removed_findings"] or row["changed_findings"])
                                       for row in test_deltas)}


def shard_rows(rows: list[dict[str, Any]], index: int, count: int, limit: int | None) -> list[dict[str, Any]]:
    values = rows[:limit] if limit else rows
    return [row for offset, row in enumerate(values) if offset % count == index]


def mcq_items(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for pair in pairs:
        for view in ("two_way", "four_way"):
            options = {key: value["label"] for key, value in pair["views"][view].items()}
            for member in ("control", "trap"):
                items.append({"item_id": f"{pair['pair_id']}::{view}::{member}", "dataset": "medeinst",
                              "question": pair[member]["narrative"] + "\n\nWhich diagnosis best fits this patient?",
                              "options": options, "fixed_evidence": []})
        for member in ("control", "trap"):
            items.append({"item_id": f"{pair['pair_id']}::legacy_open::{member}", "dataset": "medeinst",
                          "question": pair[member]["narrative"], "options": {}, "fixed_evidence": []})
    return items


def last_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    values = []
    for match in re.finditer(r"\{", text):
        try:
            value, used = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            values.append((match.start() + used, value))
    return max(values, key=lambda row: row[0])[1] if values else None


def render_prompt(backend: Any, prompt: str) -> str:
    return backend.tokenizer.apply_chat_template(
        [{"role": "system", "content": "You rank diagnoses in a synthetic benchmark. Return JSON only."},
         {"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)


def generate_json(backend: Any, prompt: str, valid: Any, max_tokens: int) -> tuple[Any, dict[str, Any]]:
    usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
             "retry_count": 0, "invalid": False, "raw_failures": []}
    repair = prompt + "\nYour previous response was invalid. Return only the exact requested JSON shape."
    for attempt, current in enumerate((prompt, repair)):
        output = backend.generate([render_prompt(backend, current)], max_tokens)[0]
        usage["calls"] += 1
        usage["prompt_tokens"] += output["prompt_tokens"]
        usage["completion_tokens"] += output["completion_tokens"]
        parsed = last_object(output["raw_response"])
        if parsed is not None and valid(parsed):
            usage["retry_count"] = attempt
            return parsed, usage
        usage["raw_failures"].append(output["raw_response"])
    usage["retry_count"] = 1
    usage["invalid"] = True
    return None, usage


def rank_prompt(pair: dict[str, Any], labels: list[dict[str, Any]], mode: str,
                delta: dict[str, Any], evidence: str = "") -> str:
    label_text = "\n".join(f"{row['label_id']}: {row['canonical_name']}" for row in labels)
    context = f"Target case:\n{pair['trap']['narrative']}"
    if mode == "medrgag_evidence_ranker":
        context += f"\n\nMedRGAG-selected evidence:\n{evidence}"
    elif mode == "full_pair_ranker":
        context = f"Control case:\n{pair['control']['narrative']}\n\n{context}"
    elif mode == "pair_aware_ranker":
        context += f"\n\nStructured change from control to target:\n{json.dumps(delta, ensure_ascii=False)}"
    return (
        f"Rank the ten most likely diagnoses from the fixed ontology.\n{context}\n\n"
        f"Ontology:\n{label_text}\n\n"
        'Return exactly {"ranked_label_ids":[10 unique integer IDs from most to least likely]}.'
    )


def ranking_valid(value: dict[str, Any], label_ids: set[int]) -> bool:
    ranked = value.get("ranked_label_ids")
    return (set(value) == {"ranked_label_ids"} and isinstance(ranked, list) and len(ranked) == 10
            and all(type(item) is int and item in label_ids for item in ranked) and len(set(ranked)) == 10)


def score_prompt(pair: dict[str, Any], delta: dict[str, Any], candidates: list[int],
                 profiles: dict[int, dict[str, Any]], profile_assignment: dict[int, int] | None = None) -> str:
    blocks = []
    for label_id in candidates:
        profile = profiles[(profile_assignment or {}).get(label_id, label_id)]
        blocks.append(json.dumps({"label_id": label_id, "diagnosis": profiles[label_id]["diagnosis"],
                                  "profile_symptoms": profile["symptoms"],
                                  "profile_antecedents": profile["antecedents"]}, ensure_ascii=False))
    return (
        "Score how the changed findings affect each candidate. Integers only: -2 strong conflict, "
        "-1 weak conflict, 0 neutral/unknown, +1 weak support, +2 strong support. "
        "removed_support is negative when a removed finding had supported the diagnosis and positive when a removed finding had conflicted.\n"
        f"Target case:\n{pair['trap']['narrative']}\n\nDelta:\n{json.dumps(delta, ensure_ascii=False)}\n\n"
        f"Candidates and fixed DDXPlus profiles:\n" + "\n".join(blocks) + "\n\n"
        'Return one JSON object whose sole top-level field is "scores": '
        '{"scores":[{"label_id":ID,"added_support":INT,"removed_support":INT,'
        '"target_case_fit":INT,"delta_fit":INT}, ...]}. Include one row for every supplied ID. '
        "Do not return Python, Markdown, an explanation, or a bare array. The first character must be { and the last } ."
    )


def scores_valid(value: dict[str, Any], candidate_ids: set[int]) -> bool:
    rows = value.get("scores")
    fields = {"label_id", "added_support", "removed_support", "target_case_fit", "delta_fit"}
    return (set(value) == {"scores"} and isinstance(rows, list) and len(rows) == len(candidate_ids)
            and {row.get("label_id") for row in rows if isinstance(row, dict)} == candidate_ids
            and all(isinstance(row, dict) and set(row) == fields
                    and type(row["label_id"]) is int
                    and all(type(row[key]) is int and -2 <= row[key] <= 2 for key in fields - {"label_id"})
                    for row in rows))


def scored_ranking(rows: list[dict[str, Any]], candidate_order: list[int]) -> tuple[list[int], dict[int, int]]:
    totals = {row["label_id"]: sum(row[key] for key in
              ("added_support", "removed_support", "target_case_fit", "delta_fit")) for row in rows}
    order = {label_id: index for index, label_id in enumerate(candidate_order)}
    return sorted(totals, key=lambda label_id: (-totals[label_id], order.get(label_id, 999), label_id)), totals


def consolidate_mcq(pairs: list[dict[str, Any]], labels: list[dict[str, Any]],
                    gate_b: Any, output_dir: Path) -> list[dict[str, Any]]:
    direct = {row["item_id"]: row for row in gate_b.read_jsonl(output_dir / "M0.jsonl")}
    medrgag = {row["item_id"]: row for row in gate_b.read_jsonl(output_dir / "M2.jsonl")}
    label_by_name = {norm(row["canonical_name"]): row["label_id"] for row in labels}
    rows = []
    for pair in pairs:
        for view in ("two_way", "four_way"):
            option_ids = {key: value["label_id"] for key, value in pair["views"][view].items()}
            for member in ("control", "trap"):
                item_id = f"{pair['pair_id']}::{view}::{member}"
                for method, cache in (("direct_mcq", direct), ("medrgag_mcq_proxy", medrgag)):
                    answer = cache[item_id]["prediction"]["answer"]
                    key = str(answer or "").strip().upper()
                    valid = key in option_ids
                    rows.append({"pair_id": pair["pair_id"], "split": pair["split"], "method": method,
                                 "view": view, "member": member,
                                 "predicted_label_id": option_ids.get(key), "option_key": key if valid else None,
                                 "status": "ok" if valid else "invalid",
                                 "usage": cache[item_id]["usage"],
                                 "raw_response": None if valid else cache[item_id]["raw_response"]})
        for member in ("control", "trap"):
            item_id = f"{pair['pair_id']}::legacy_open::{member}"
            answer = medrgag[item_id]["prediction"]["answer"]
            prediction = label_by_name.get(norm(answer))
            rows.append({"pair_id": pair["pair_id"], "split": pair["split"],
                         "method": "legacy_open_medrgag", "view": "open", "member": member,
                         "predicted_label_id": prediction, "status": "ok" if prediction is not None else "invalid",
                         "usage": medrgag[item_id]["usage"],
                         "raw_response": None if prediction is not None else medrgag[item_id]["raw_response"]})
    return rows


def run(data_paths: list[Path], labels_path: Path, profiles_path: Path, deltas_path: Path,
        output_dir: Path, model: Path, shard_index: int, shard_count: int, limit: int | None,
        batch_size: int, max_model_len: int, gpu_memory_utilization: float) -> dict[str, Any]:
    pairs = shard_rows([row for path in data_paths for row in read_jsonl(path)], shard_index, shard_count, limit)
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    profiles_list = json.loads(profiles_path.read_text(encoding="utf-8"))
    profiles = {row["label_id"]: row for row in profiles_list}
    delta_map = {row["pair_id"]: row for row in read_jsonl(deltas_path)}
    label_ids = {row["label_id"] for row in labels}
    output_dir.mkdir(parents=True, exist_ok=True)
    gate_b = load_script("deltarank_gate_b", ROOT / "scripts" / "run_gate_b.py")
    items = mcq_items(pairs)
    retrievals = gate_b.prepare_retrievals(items, output_dir / "retrieval.jsonl")
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory_utilization)
    gate_b.run_m0([item for item in items if item["options"]], output_dir / "M0.jsonl", backend,
                  batch_size, max_model_len - 512, 64)
    gate_b.run_m2(items, retrievals, output_dir, backend, batch_size, max_model_len - 512, 64)
    mcq = consolidate_mcq(pairs, labels, gate_b, output_dir)
    write_jsonl(output_dir / "mcq_predictions.jsonl", mcq)
    mcq_index = {(row["pair_id"], row["method"], row["view"], row["member"]): row for row in mcq}
    selected = {row["item_id"]: row["documents"] for row in gate_b.read_jsonl(output_dir / "M2.rerank.jsonl")}
    donor_ids = sorted(pair["pair_id"] for pair in pairs)
    donor = {pair_id: donor_ids[(index + 1) % len(donor_ids)] for index, pair_id in enumerate(donor_ids)}
    candidate_path = output_dir / "candidate_scores.jsonl"
    candidate_rows = read_jsonl(candidate_path) if candidate_path.exists() else []
    completed_candidates = {row["pair_id"] for row in candidate_rows}
    invalid_count = sum(value["status"] != "ok" for row in candidate_rows
                        for group in ("rankings", "scores") for value in row[group].values())
    for pair in pairs:
        pair_id = pair["pair_id"]
        if pair_id in completed_candidates:
            continue
        delta = delta_map[pair_id]
        evidence = "\n\n".join(doc["contents"] for doc in selected[f"{pair_id}::legacy_open::trap"])
        rankings: dict[str, Any] = {}
        for method in RANK_METHODS:
            prompt = rank_prompt(pair, labels, method, delta, evidence)
            parsed, usage = generate_json(backend, prompt, lambda value: ranking_valid(value, label_ids), 256)
            rankings[method] = {"status": "ok" if parsed else "invalid",
                                "ranked_label_ids": parsed["ranked_label_ids"] if parsed else [], "usage": usage}
            invalid_count += int(parsed is None)
        base = mcq_index[(pair_id, "medrgag_mcq_proxy", "four_way", "trap")]["predicted_label_id"]
        candidate_order = list(rankings["medrgag_evidence_ranker"]["ranked_label_ids"])
        score_ids = candidate_order + ([base] if base is not None and base not in candidate_order else [])
        score_results: dict[str, Any] = {}
        inputs = {
            "delta_profile_ranker": (delta, None),
            "shuffled_delta": (delta_map[donor[pair_id]], None),
            "shuffled_profile": (delta, {label_id: score_ids[(index + 1) % len(score_ids)]
                                         for index, label_id in enumerate(score_ids)} if score_ids else None),
        }
        for method, (used_delta, assignment) in inputs.items():
            if len(candidate_order) != 10 or base is None:
                parsed, usage = None, {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                                       "retry_count": 0, "invalid": True, "raw_failures": []}
            else:
                prompt = score_prompt(pair, used_delta, score_ids, profiles, assignment)
                parsed, usage = generate_json(backend, prompt,
                                              lambda value, ids=set(score_ids): scores_valid(value, ids), 768)
            if parsed:
                ranked, totals = scored_ranking(parsed["scores"], score_ids)
                margin = totals[ranked[0]] - totals[base]
                score_results[method] = {"status": "ok", "scores": parsed["scores"],
                                         "ranked_label_ids": ranked, "baseline_label_id": base,
                                         "delta_margin": margin, "usage": usage,
                                         "source_pair_id": donor[pair_id] if method == "shuffled_delta" else pair_id}
            else:
                score_results[method] = {"status": "invalid", "scores": [], "ranked_label_ids": [],
                                         "baseline_label_id": base, "delta_margin": None, "usage": usage,
                                         "source_pair_id": donor[pair_id] if method == "shuffled_delta" else pair_id}
                invalid_count += 1
        row = {"pair_id": pair_id, "split": pair["split"],
               "rankings": rankings, "scores": score_results}
        gate_b.append_rows(candidate_path, [row])
        candidate_rows.append(row)
    return {"pairs": len(pairs), "mcq_rows": len(mcq), "candidate_rows": len(candidate_rows),
            "invalid_rank_or_score_calls": invalid_count}


def merge(inputs: list[Path], output: Path, kind: str) -> int:
    rows = [row for path in inputs for row in read_jsonl(path)]
    if kind == "mcq":
        keys = [(row["pair_id"], row["method"], row["view"], row["member"]) for row in rows]
    else:
        keys = [row["pair_id"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate {kind} rows")
    write_jsonl(output, sorted(rows, key=lambda row: tuple(str(row.get(key, ""))
                for key in ("pair_id", "method", "view", "member"))))
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--train-raw", type=Path, required=True)
    prep.add_argument("--test-raw", type=Path, required=True)
    prep.add_argument("--conditions", type=Path, required=True)
    prep.add_argument("--evidences", type=Path, required=True)
    prep.add_argument("--output-dir", type=Path, required=True)
    prep.add_argument("--dev-pairs", type=int, default=300)
    prep.add_argument("--test-pairs", type=int, default=300)
    prep.add_argument("--seed", type=int, default=13)
    execute = sub.add_parser("run")
    execute.add_argument("--data", type=Path, nargs="+", required=True)
    execute.add_argument("--labels", type=Path, required=True)
    execute.add_argument("--profiles", type=Path, required=True)
    execute.add_argument("--deltas", type=Path, required=True)
    execute.add_argument("--output-dir", type=Path, required=True)
    execute.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    execute.add_argument("--shard-index", type=int, default=0)
    execute.add_argument("--shard-count", type=int, default=1)
    execute.add_argument("--limit", type=int)
    execute.add_argument("--batch-size", type=int, default=16)
    execute.add_argument("--max-model-len", type=int, default=32768)
    execute.add_argument("--gpu-memory-utilization", type=float, default=.55)
    combine = sub.add_parser("merge")
    combine.add_argument("--kind", choices=("mcq", "candidates"), required=True)
    combine.add_argument("--inputs", type=Path, nargs="+", required=True)
    combine.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        result = prepare(args.train_raw, args.test_raw, args.conditions, args.evidences,
                         args.output_dir, args.dev_pairs, args.test_pairs, args.seed)
    elif args.command == "run":
        target = args.output_dir / f"shard-{args.shard_index:03d}-of-{args.shard_count:03d}"
        result = run(args.data, args.labels, args.profiles, args.deltas, target, args.model,
                     args.shard_index, args.shard_count, args.limit, args.batch_size,
                     args.max_model_len, args.gpu_memory_utilization)
    else:
        result = {"rows": merge(args.inputs, args.output, args.kind)}
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
