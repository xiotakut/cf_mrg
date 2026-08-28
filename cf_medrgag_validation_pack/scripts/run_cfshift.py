#!/usr/bin/env python3
"""Prepare and run the compact CFShift-MedRGAG experiment."""

from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
import math
import random
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct")
DEFAULT_MEDCPT = Path("/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder")
LETTERS = "ABCD"
STAGE_FILES = (
    "retrieval.jsonl", "M0.jsonl", "M2.summary.jsonl", "M2.explore.jsonl",
    "M2.generate.jsonl", "M2.select.jsonl", "M2.rerank.jsonl", "M2.jsonl",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def split_rows(rows: list[dict[str, Any]], index: int, count: int,
               limit: int | None = None) -> list[dict[str, Any]]:
    values = rows[:limit] if limit else rows
    return [row for offset, row in enumerate(values) if offset % count == index]


def option_view(names: list[str], seed: str, label_ids: dict[str, int]) -> dict[str, dict[str, Any]]:
    values = list(names)
    random.Random(seed).shuffle(values)
    return {LETTERS[index]: {"label": name, "label_id": label_ids[name]}
            for index, name in enumerate(values)}


def adapt_pair(pair: dict[str, Any], split: str, seed: int, conditions: dict[str, Any],
               profiles: dict[str, set[str]], label_ids: dict[str, int], delta_rank: Any) -> dict[str, Any]:
    case_id = str(pair["case_id"])
    control_name, trap_name = pair["control"]["ground_truth"], pair["trap"]["ground_truth"]
    negatives = []
    for candidate in sorted(set(conditions) - {control_name, trap_name}):
        overlap = max(
            len(profiles[candidate] & profiles[control_name]) / len(profiles[candidate] | profiles[control_name]),
            len(profiles[candidate] & profiles[trap_name]) / len(profiles[candidate] | profiles[trap_name]),
        )
        negatives.append((overlap, candidate))
    hard = [name for _, name in sorted(negatives, key=lambda value: (-value[0], value[1]))[:2]]
    pair_id = f"{split}-{case_id}"
    return {
        "pair_id": pair_id,
        "source_case_id": case_id,
        "split": split,
        "control": {"age": pair["control"]["age"], "sex": pair["control"]["sex"],
                    "narrative": pair["control"]["narrative"], "label": control_name,
                    "label_id": label_ids[control_name]},
        "trap": {"age": pair["trap"]["age"], "sex": pair["trap"]["sex"],
                 "narrative": pair["trap"]["narrative"], "label": trap_name,
                 "label_id": label_ids[trap_name]},
        "views": {"four_way": option_view([trap_name, control_name, *hard],
                                             f"{seed}:{pair_id}:four", label_ids)},
        "hard_negative_labels": hard,
        "delta": delta_rank.structured_delta(pair["control"]["narrative"], pair["trap"]["narrative"]),
    }


def prepare(train_raw: Path, test_raw: Path, conditions_path: Path, old_dev_path: Path,
            old_test_path: Path, output_dir: Path, dev_count: int, calibration_count: int,
            fresh_count: int, seed: int) -> dict[str, Any]:
    delta_rank = load_script("cfshift_deltarank", ROOT / "scripts" / "run_deltarank.py")
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    names = sorted(conditions)
    label_ids = {name: index for index, name in enumerate(names)}
    profiles = {name: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    train = delta_rank.paired_rows(train_raw)
    test = delta_rank.paired_rows(test_raw)
    by_train_id = {str(row["case_id"]): row for row in train}
    by_test_id = {str(row["case_id"]): row for row in test}

    old_dev = read_jsonl(old_dev_path)
    old_test_ids = {row["source_case_id"] for row in read_jsonl(old_test_path)}
    reused_ids = {row["source_case_id"] for row in old_dev}
    if len(old_dev) > dev_count or not reused_ids <= set(by_train_id):
        raise ValueError("old development rows cannot be reused")
    remaining_train = [row for row in train if str(row["case_id"]) not in reused_ids]
    extra = delta_rank.balanced_sample(remaining_train, dev_count - len(old_dev) + calibration_count, seed + 17)
    dev_source = [by_train_id[row["source_case_id"]] for row in old_dev] + extra[:dev_count - len(old_dev)]
    calibration_source = extra[dev_count - len(old_dev):]
    fresh_source = delta_rank.balanced_sample(
        [row for row in test if str(row["case_id"]) not in old_test_ids], fresh_count, seed + 29)

    splits = {
        "dev": [adapt_pair(row, "dev", seed, conditions, profiles, label_ids, delta_rank)
                for row in dev_source],
        "calibration": [adapt_pair(row, "calibration", seed, conditions, profiles, label_ids, delta_rank)
                        for row in calibration_source],
        "fresh_test": [adapt_pair(row, "fresh_test", seed, conditions, profiles, label_ids, delta_rank)
                       for row in fresh_source],
    }
    # Preserve byte-for-byte option construction for the 300 reusable DeltaRank development pairs.
    old_by_source = {row["source_case_id"]: row for row in old_dev}
    for row in splits["dev"]:
        if row["source_case_id"] in old_by_source:
            old = old_by_source[row["source_case_id"]]
            if row["views"] != {"four_way": old["views"]["four_way"]}:
                raise ValueError("reused four-way view changed")

    all_rows = [row for values in splits.values() for row in values]
    for values in splits.values():
        donors = [row["pair_id"] for row in values]
        for index, row in enumerate(values):
            row["shuffle_source_pair_id"] = donors[(index + 1) % len(donors)]
    if len({row["source_case_id"] for row in all_rows}) != len(all_rows):
        raise ValueError("source case IDs overlap across splits")
    if old_test_ids & {row["source_case_id"] for row in splits["fresh_test"]}:
        raise ValueError("fresh test overlaps the inspected DeltaRank test")
    output_dir.mkdir(parents=True, exist_ok=True)
    for split, rows in splits.items():
        write_jsonl(output_dir / f"{split}.jsonl", rows)
    return {split: len(rows) for split, rows in splits.items()} | {
        "fresh_excluded": len(old_test_ids),
        "nonempty_deltas": sum(bool(row["delta"]["added_findings"] or row["delta"]["removed_findings"]
                                    or row["delta"]["changed_findings"]) for row in all_rows),
    }


def audit_candidates(candidate_path: Path, dev_path: Path, test_path: Path,
                     mcq_path: Path, output: Path) -> dict[str, Any]:
    candidates = {row["pair_id"]: row for row in read_jsonl(candidate_path)}
    baseline_rows = read_jsonl(mcq_path)
    baseline = {row["pair_id"]: row["predicted_label_id"] for row in baseline_rows
                if row["method"] == "medrgag_mcq_proxy" and row["view"] == "four_way"
                and row["member"] == "trap"}
    result: dict[str, Any] = {}
    for split, path in (("dev", dev_path), ("test", test_path)):
        truth = {row["pair_id"]: row["trap"]["label_id"] for row in read_jsonl(path)}
        methods = sorted(next(iter(candidates.values()))["rankings"])
        per_method = {}
        for method in methods:
            ranks = {key: candidates[key]["rankings"][method]["ranked_label_ids"] for key in truth}
            per_method[method] = {
                "recall_at_5": sum(truth[key] in ranks[key][:5] for key in truth) / len(truth),
                "recall_at_10": sum(truth[key] in ranks[key][:10] for key in truth) / len(truth),
                "unique_gold_coverage": sum(
                    truth[key] in ranks[key] and all(truth[key] not in candidates[key]["rankings"][other]["ranked_label_ids"]
                                                     for other in methods if other != method)
                    for key in truth),
            }
        fused: dict[str, list[int]] = {}
        union: dict[str, list[int]] = {}
        for key in truth:
            scores: dict[int, float] = defaultdict(float)
            for method in methods:
                for rank, label_id in enumerate(candidates[key]["rankings"][method]["ranked_label_ids"], 1):
                    scores[label_id] += 1 / (60 + rank)
            fused[key] = sorted(scores, key=lambda label: (-scores[label], label))
            union[key] = list(dict.fromkeys(label for rank in range(10) for method in methods
                                             for label in candidates[key]["rankings"][method]["ranked_label_ids"][rank:rank + 1]))
        wrong = [key for key in truth if baseline.get(key) != truth[key]]
        result[split] = {
            "individual": per_method,
            "union_recall_at_10": sum(truth[key] in union[key][:10] for key in truth) / len(truth),
            "union_recall_at_20": sum(truth[key] in union[key][:20] for key in truth) / len(truth),
            "rrf_recall_at_10": sum(truth[key] in fused[key][:10] for key in truth) / len(truth),
            "rrf_recall_at_20": sum(truth[key] in fused[key][:20] for key in truth) / len(truth),
            "baseline_wrong": len(wrong),
            "oracle_union_repairs_at_10": sum(truth[key] in union[key][:10] for key in wrong),
            "oracle_union_repairs_at_20": sum(truth[key] in union[key][:20] for key in wrong),
            "note": "Union ordering is deterministic rank-wise interleaving; RRF uses k=60.",
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def evidence_descriptor(evidence: dict[str, Any]) -> str:
    meanings = [str(value.get("en", "")) for value in evidence.get("value_meaning", {}).values()]
    return " | ".join(str(value) for value in (
        evidence.get("question_en", ""), evidence.get("code_question", ""),
        evidence.get("data_type", ""), evidence.get("default_value", ""),
        "; ".join(map(str, evidence.get("possible-values", []))), "; ".join(meanings),
        "antecedent" if evidence.get("is_antecedent") else "symptom",
    ) if value != "")


def finding_rows(delta: dict[str, Any]) -> list[dict[str, str]]:
    rows = ([{"finding": value, "operation": "added"} for value in delta["added_findings"]]
            + [{"finding": value, "operation": "removed"} for value in delta["removed_findings"]])
    for value in delta["changed_findings"]:
        rows.extend(({"finding": value["old"], "operation": "old_value"},
                     {"finding": value["new"], "operation": "new_value"}))
    return rows


def match_evidence(data_paths: list[Path], evidences_path: Path, output: Path,
                   medcpt: Path, device: str, batch_size: int) -> dict[str, Any]:
    pairs = [row for path in data_paths for row in read_jsonl(path)]
    evidences = json.loads(evidences_path.read_text(encoding="utf-8"))
    docs = [{"id": key, "contents": evidence_descriptor(value)} for key, value in sorted(evidences.items())]
    import sys
    sys.path.insert(0, "/home/data3/txy/MedRGAG")
    from src.medrgag_retrieval import MedCPTRanker
    ranker = MedCPTRanker(medcpt, device=device)
    cache: dict[str, tuple[str, float, float]] = {}
    try:
        for finding in sorted({value["finding"] for pair in pairs for value in finding_rows(pair["delta"])}):
            logits = []
            for start in range(0, len(docs), batch_size):
                logits.extend(ranker.score(finding, docs[start:start + batch_size]))
            index = max(range(len(logits)), key=lambda i: logits[i])
            cache[finding] = (docs[index]["id"], 1 / (1 + math.exp(-logits[index])), logits[index])
    finally:
        ranker.close()
    rows = []
    for pair in pairs:
        matches = [{**value, "matched_evidence_id": cache[value["finding"]][0],
                    "similarity": cache[value["finding"]][1], "medcpt_logit": cache[value["finding"]][2]}
                   for value in finding_rows(pair["delta"])]
        rows.append({"pair_id": pair["pair_id"], "split": pair["split"], "delta": pair["delta"],
                     "matches": matches})
    write_jsonl(output, rows)
    similarities = [value["similarity"] for row in rows for value in row["matches"]]
    return {"pairs": len(rows), "unique_findings": len(cache), "matches": len(similarities),
            "similarity_min": min(similarities), "similarity_mean": sum(similarities) / len(similarities),
            "similarity_max": max(similarities)}


def mcq_items(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for pair in pairs:
        options = {key: value["label"] for key, value in pair["views"]["four_way"].items()}
        for member in ("control", "trap"):
            items.append({"item_id": f"{pair['pair_id']}::four_way::{member}", "dataset": "medeinst",
                          "question": pair[member]["narrative"] + "\n\nWhich diagnosis best fits this patient?",
                          "options": options, "fixed_evidence": []})
    return items


def cache_key(row: dict[str, Any]) -> str:
    return str(row.get("key") or row.get("item_id"))


def seed_cache(item_ids: set[str], old_root: Path, output_dir: Path) -> int:
    copied = 0
    for filename in STAGE_FILES:
        target = output_dir / filename
        existing = {cache_key(row) for row in read_jsonl(target)} if target.exists() else set()
        rows = []
        for source in sorted(old_root.glob(f"shard-*/{filename}")):
            for row in read_jsonl(source):
                item_id = str(row.get("item_id", ""))
                key = cache_key(row)
                if item_id in item_ids and key not in existing:
                    rows.append(row); existing.add(key)
        if rows:
            with target.open("a", encoding="utf-8") as stream:
                for row in rows:
                    stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            copied += len(rows)
    return copied


def run_baseline(data_paths: list[Path], output_dir: Path, model: Path, old_cache: Path | None,
                 shard_index: int, shard_count: int, limit: int | None, batch_size: int,
                 max_model_len: int, gpu_memory: float) -> dict[str, Any]:
    all_pairs = [row for path in data_paths for row in read_jsonl(path)]
    pairs = split_rows(all_pairs, shard_index, shard_count, limit)
    items = mcq_items(pairs)
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = seed_cache({item["item_id"] for item in items}, old_cache, output_dir) if old_cache else 0
    gate_b = load_script("cfshift_gate_b", ROOT / "scripts" / "run_gate_b.py")
    retrievals = gate_b.prepare_retrievals(items, output_dir / "retrieval.jsonl")
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory)
    gate_b.run_m0(items, output_dir / "M0.jsonl", backend, batch_size, max_model_len - 512, 64)
    gate_b.run_m2(items, retrievals, output_dir, backend, batch_size, max_model_len - 512, 64)
    direct = {row["item_id"]: row for row in gate_b.read_jsonl(output_dir / "M0.jsonl")}
    medrgag = {row["item_id"]: row for row in gate_b.read_jsonl(output_dir / "M2.jsonl")}
    selected = {row["item_id"]: row["documents"] for row in gate_b.read_jsonl(output_dir / "M2.rerank.jsonl")}
    rows = []
    for pair in pairs:
        option_ids = {key: value["label_id"] for key, value in pair["views"]["four_way"].items()}
        members = {}
        for member in ("control", "trap"):
            item_id = f"{pair['pair_id']}::four_way::{member}"
            values = {}
            for method, cache in (("direct_mcq", direct), ("medrgag_mcq_proxy", medrgag)):
                answer = str(cache[item_id]["prediction"]["answer"] or "").strip().upper()
                values[method] = {"option": answer if answer in option_ids else None,
                                  "label_id": option_ids.get(answer),
                                  "status": "ok" if answer in option_ids else "invalid",
                                  "usage": cache[item_id]["usage"],
                                  "raw_response": cache[item_id]["raw_response"] if answer not in option_ids else None}
            members[member] = {"predictions": values, "selected_documents": selected[item_id]}
        rows.append({"pair_id": pair["pair_id"], "split": pair["split"], **members})
    write_jsonl(output_dir / "baseline.jsonl", rows)
    return {"pairs": len(rows), "seeded_cache_rows": copied,
            "invalid": sum(value["status"] != "ok" for row in rows for member in ("control", "trap")
                           for value in row[member]["predictions"].values())}


def render_choice_prompt(tokenizer: Any, context: str, options: list[tuple[str, str]]) -> str:
    body = context + "\n\nAnswer options:\n" + "\n".join(f"{key}. {label}" for key, label in options)
    body += "\n\nChoose the single best diagnosis. Return one option letter only.\nAnswer:"
    return tokenizer.apply_chat_template(
        [{"role": "system", "content": "You score a synthetic medical multiple-choice benchmark."},
         {"role": "user", "content": body}], tokenize=False, add_generation_prompt=True)


class ChoiceScorer:
    def __init__(self, backend: Any) -> None:
        self.backend = backend

    def _score_single_token(self, prompts: list[str], keys: list[str]) -> list[dict[str, float]]:
        # vLLM 0.8.5 does not guarantee every allowed token appears in returned top-logprobs.
        # Prompt likelihood is exact for both one-token and multi-token option labels.
        return self._score_sequences(prompts, keys)

    def _score_sequences(self, prompts: list[str], keys: list[str]) -> list[dict[str, float]]:
        from vllm import SamplingParams
        full_ids, spans = [], []
        for prompt in prompts:
            base = self.backend.tokenizer.encode(prompt, add_special_tokens=False)
            for key in keys:
                suffix = self.backend.tokenizer.encode(key, add_special_tokens=False)
                full_ids.append(base + suffix); spans.append((len(base), suffix))
        outputs = self.backend.model.generate(prompt_token_ids=full_ids,
                                              sampling_params=SamplingParams(temperature=0, max_tokens=1,
                                                                             prompt_logprobs=0, seed=42),
                                              use_tqdm=False)
        values = []
        for output, (start, suffix) in zip(outputs, spans):
            score = sum(output.prompt_logprobs[start + offset][token_id].logprob
                        for offset, token_id in enumerate(suffix))
            values.append(float(score))
        return [{key: values[index * len(keys) + offset] for offset, key in enumerate(keys)}
                for index in range(len(prompts))]

    def score_contexts(self, contexts: dict[str, str], options: dict[str, dict[str, Any]]) -> dict[str, Any]:
        stored = [(key, value["label"], value["label_id"]) for key, value in options.items()]
        prompts, metadata = [], []
        for context_name, context in contexts.items():
            for permutation, ordered in (("forward", stored), ("reverse", list(reversed(stored)))):
                displayed = [(LETTERS[index], value[1]) for index, value in enumerate(ordered)]
                prompts.append(render_choice_prompt(self.backend.tokenizer, context, displayed))
                metadata.append((context_name, permutation, ordered))
        raw = self._score_single_token(prompts, list(LETTERS))
        values: dict[str, Any] = defaultdict(lambda: {"permutations": {}})
        for score, (context_name, permutation, ordered) in zip(raw, metadata):
            by_label = {str(value[2]): score[LETTERS[index]] for index, value in enumerate(ordered)}
            normalizer = math.log(sum(math.exp(value) for value in by_label.values()))
            values[context_name]["permutations"][permutation] = {
                label: value - normalizer for label, value in by_label.items()}
        for value in values.values():
            forward, reverse = value["permutations"]["forward"], value["permutations"]["reverse"]
            averaged = {label: (forward[label] + reverse[label]) / 2 for label in forward}
            normalizer = math.log(sum(math.exp(score) for score in averaged.values()))
            value["log_scores"] = {label: score - normalizer for label, score in averaged.items()}
            value["probabilities"] = {label: math.exp(score) for label, score in value["log_scores"].items()}
            if not math.isclose(sum(value["probabilities"].values()), 1, abs_tol=1e-6):
                raise ValueError("choice probabilities do not sum to one")
        return dict(values)


def document_text(documents: list[dict[str, Any]]) -> str:
    return "\n\n".join(f"[D{index}] {row.get('contents', '')}" for index, row in enumerate(documents, 1))


def run_scores(data_paths: list[Path], baseline_path: Path, output_dir: Path, model: Path,
               shard_index: int, shard_count: int, limit: int | None, max_model_len: int,
               gpu_memory: float) -> dict[str, Any]:
    all_pairs = [row for path in data_paths for row in read_jsonl(path)]
    pair_map = {row["pair_id"]: row for row in all_pairs}
    baseline = {row["pair_id"]: row for row in read_jsonl(baseline_path)}
    pairs = split_rows(all_pairs, shard_index, shard_count, limit)
    local_donors = ({row["pair_id"]: pairs[(index + 1) % len(pairs)]["pair_id"]
                     for index, row in enumerate(pairs)} if limit else {})
    required = {row["pair_id"] for row in pairs} | {local_donors.get(row["pair_id"], row["shuffle_source_pair_id"])
                                                     for row in pairs}
    if not required <= set(baseline):
        raise ValueError("baseline lacks target or shuffled-control pairs")
    gate_b = load_script("cfshift_score_gate_b", ROOT / "scripts" / "run_gate_b.py")
    import vllm
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory)
    scorer = ChoiceScorer(backend)
    score_path = output_dir / "option_scores.jsonl"
    existing = read_jsonl(score_path) if score_path.exists() else []
    done = {row["pair_id"] for row in existing}
    rows = list(existing)
    for pair in pairs:
        if pair["pair_id"] in done:
            continue
        donor = pair_map[local_donors.get(pair["pair_id"], pair["shuffle_source_pair_id"])]
        base, donor_base = baseline[pair["pair_id"]], baseline[donor["pair_id"]]
        contexts = {
            "direct_target_scores": pair["trap"]["narrative"],
            "direct_control_scores": pair["control"]["narrative"],
            "medrgag_target_scores": pair["trap"]["narrative"] + "\n\nSelected evidence:\n" +
                                     document_text(base["trap"]["selected_documents"]),
            "medrgag_control_scores": pair["control"]["narrative"] + "\n\nSelected evidence:\n" +
                                      document_text(base["control"]["selected_documents"]),
            "pair_prompt_scores": "Control case:\n" + pair["control"]["narrative"] +
                                  "\n\nTrap case:\n" + pair["trap"]["narrative"] +
                                  "\n\nStructured change:\n" + json.dumps(pair["delta"], ensure_ascii=False),
            "shuffled_control_scores": donor["control"]["narrative"] + "\n\nSelected evidence:\n" +
                                       document_text(donor_base["control"]["selected_documents"]),
        }
        try:
            scores = scorer.score_contexts(contexts, pair["views"]["four_way"])
            status, error = "ok", None
        except (KeyError, ValueError, RuntimeError) as exc:
            scores, status, error = {}, "invalid", f"{type(exc).__name__}: {exc}"
        row = {"pair_id": pair["pair_id"], "split": pair["split"], "status": status,
               "error": error, "scores": scores, "shuffle_source_pair_id": donor["pair_id"],
               "model": str(model), "permutations": ["forward", "reverse"],
               "vllm_version": vllm.__version__,
               "scoring_implementation": "two-permutation option-sequence prompt log-likelihood",
               "medrgag_baseline": {
                   "baseline_option": base["trap"]["predictions"]["medrgag_mcq_proxy"]["option"],
                   "baseline_label_id": base["trap"]["predictions"]["medrgag_mcq_proxy"]["label_id"],
                   "control_selected_documents": base["control"]["selected_documents"],
                   "trap_selected_documents": base["trap"]["selected_documents"],
               }}
        output_dir.mkdir(parents=True, exist_ok=True)
        with score_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
        rows.append(row)
    return {"pairs": len(rows), "new_pairs": len(rows) - len(existing),
            "invalid": sum(row["status"] != "ok" for row in rows)}


def merge(inputs: list[Path], output: Path) -> int:
    rows = [row for path in inputs for row in read_jsonl(path)]
    keys = [row["pair_id"] for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate merged pair IDs")
    write_jsonl(output, sorted(rows, key=lambda row: row["pair_id"]))
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--train-raw", type=Path, required=True); prep.add_argument("--test-raw", type=Path, required=True)
    prep.add_argument("--conditions", type=Path, required=True); prep.add_argument("--old-dev", type=Path, required=True)
    prep.add_argument("--old-test", type=Path, required=True); prep.add_argument("--output-dir", type=Path, required=True)
    prep.add_argument("--dev-pairs", type=int, default=800); prep.add_argument("--calibration-pairs", type=int, default=200)
    prep.add_argument("--fresh-test-pairs", type=int, default=500); prep.add_argument("--seed", type=int, default=13)
    audit = sub.add_parser("audit")
    audit.add_argument("--candidates", type=Path, required=True); audit.add_argument("--dev", type=Path, required=True)
    audit.add_argument("--test", type=Path, required=True); audit.add_argument("--mcq", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    match = sub.add_parser("match")
    match.add_argument("--data", type=Path, nargs="+", required=True); match.add_argument("--evidences", type=Path, required=True)
    match.add_argument("--output", type=Path, required=True); match.add_argument("--medcpt", type=Path, default=DEFAULT_MEDCPT)
    match.add_argument("--device", default="cuda:0"); match.add_argument("--batch-size", type=int, default=64)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--data", type=Path, nargs="+", required=True); baseline.add_argument("--output-dir", type=Path, required=True)
    baseline.add_argument("--model", type=Path, default=DEFAULT_MODEL); baseline.add_argument("--old-cache", type=Path)
    score = sub.add_parser("score")
    score.add_argument("--data", type=Path, nargs="+", required=True); score.add_argument("--baseline", type=Path, required=True)
    score.add_argument("--output-dir", type=Path, required=True); score.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    for command in (baseline, score):
        command.add_argument("--shard-index", type=int, default=0); command.add_argument("--shard-count", type=int, default=1)
        command.add_argument("--limit", type=int); command.add_argument("--max-model-len", type=int, default=32768)
        command.add_argument("--gpu-memory-utilization", type=float, default=.55)
    baseline.add_argument("--batch-size", type=int, default=16)
    combine = sub.add_parser("merge")
    combine.add_argument("--inputs", type=Path, nargs="+", required=True); combine.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        result = prepare(args.train_raw, args.test_raw, args.conditions, args.old_dev, args.old_test,
                         args.output_dir, args.dev_pairs, args.calibration_pairs, args.fresh_test_pairs, args.seed)
    elif args.command == "audit":
        result = audit_candidates(args.candidates, args.dev, args.test, args.mcq, args.output)
    elif args.command == "match":
        result = match_evidence(args.data, args.evidences, args.output, args.medcpt, args.device, args.batch_size)
    elif args.command == "baseline":
        target = args.output_dir / f"shard-{args.shard_index:03d}-of-{args.shard_count:03d}"
        result = run_baseline(args.data, target, args.model, args.old_cache, args.shard_index, args.shard_count,
                              args.limit, args.batch_size, args.max_model_len, args.gpu_memory_utilization)
    elif args.command == "score":
        target = args.output_dir / f"shard-{args.shard_index:03d}-of-{args.shard_count:03d}"
        result = run_scores(args.data, args.baseline, target, args.model, args.shard_index, args.shard_count,
                            args.limit, args.max_model_len, args.gpu_memory_utilization)
    else:
        result = {"rows": merge(args.inputs, args.output)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
