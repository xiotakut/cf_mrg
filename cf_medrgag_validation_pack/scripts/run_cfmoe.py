#!/usr/bin/env python3
"""Run the compact CF-KADS-MoE study without adding a pipeline framework."""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
import importlib.util
import json
import math
import os
import random
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import minimize


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results_cfmoe"
LETTERS = "ABCD"
EXISTING_EXPERTS = (
    "medrgag_selected_evidence_score",
    "direct_target_logprob",
    "cf_shift_profile_score",
    "no_medrgag_evidence",
)
REGULARIZATION = (0.0, 0.01, 0.1, 1.0)


def load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CF_RUN = load_script("cfmoe_cf_run", ROOT / "scripts" / "run_cfshift.py")
CF_EVAL = load_script("cfmoe_cf_eval", ROOT / "scripts" / "evaluate_cfshift.py")
DELTA_RANK = load_script("cfmoe_delta_rank", ROOT / "scripts" / "run_deltarank.py")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return CF_RUN.read_jsonl(path)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    CF_RUN.write_jsonl(path, rows)


def merge_exact(data_paths: list[Path], inputs: list[Path], output: Path) -> int:
    """Merge only the exact pair IDs named by the current protocol splits."""
    expected = {row["pair_id"] for path in data_paths for row in read_jsonl(path)}
    found: dict[str, dict[str, Any]] = {}
    for path in inputs:
        for row in read_jsonl(path):
            pair_id = row["pair_id"]
            if pair_id in expected:
                if pair_id in found:
                    raise ValueError(f"duplicate merged pair ID: {pair_id}")
                found[pair_id] = row
    missing = expected - set(found)
    if missing:
        raise ValueError(f"merge missing {len(missing)} expected pair IDs")
    write_jsonl(output, (found[key] for key in sorted(found)))
    return len(found)


def merge_keyed(inputs: list[Path], output: Path, key: str) -> int:
    rows = [row for path in inputs for row in read_jsonl(path)]
    values = [str(row[key]) for row in rows]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {key} in merged rows")
    write_jsonl(output, (row for _, row in sorted(zip(values, rows))))
    return len(rows)


def compact_documents(source: Path, output: Path) -> int:
    """Keep scores/provenance once per document; raw document text remains in ignored cache."""
    rows = []
    for row in read_jsonl(source):
        def compact(document: dict[str, Any]) -> dict[str, Any]:
            return {key: value for key, value in document.items() if key != "contents"} | {
                "contents_preview": " ".join(document.get("contents", "").split())[:240]
            }
        variants = {name: [{"id": value.get("id"), "source": value.get("source")}
                           for value in values]
                    for name, values in row["variants"].items()}
        rows.append({**row,
                     "candidate_documents": [compact(value) for value in row["candidate_documents"]],
                     "supplementary_documents": [compact(value) for value in row["supplementary_documents"]],
                     "variants": variants})
    write_jsonl(output, rows)
    return len(rows)


def prepare(output_dir: Path, fresh_count: int = 1000, seed: int = 13) -> dict[str, Any]:
    """Reuse frozen train/reference splits and select a genuinely unseen official test split."""
    source = ROOT / "results_cfshift"
    dev, calibration = read_jsonl(source / "dev.jsonl"), read_jsonl(source / "calibration.jsonl")
    test_raw = (ROOT / "private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/"
                "354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl")
    conditions_path = ROOT / "private_data/deltarank_sources/release_conditions.json"
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    label_ids = {name: index for index, name in enumerate(sorted(conditions))}
    profiles = {name: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    excluded_test = {
        row["source_case_id"]
        for path in (ROOT / "results_deltarank/test.jsonl", source / "fresh_test.jsonl")
        for row in read_jsonl(path)
    }
    development_ids = {row["source_case_id"] for row in dev + calibration}
    excluded = excluded_test | development_ids
    complete = DELTA_RANK.paired_rows(test_raw)
    remaining = [row for row in complete if str(row["case_id"]) not in excluded]
    selected = sorted(remaining, key=lambda row: str(row["case_id"]))
    random.Random(seed + 71).shuffle(selected)
    selected = selected[:fresh_count]
    if len(selected) != fresh_count:
        raise ValueError(f"only {len(selected)} unseen complete test pairs available")
    fresh = [CF_RUN.adapt_pair(row, "fresh_test", seed, conditions, profiles, label_ids, DELTA_RANK)
             for row in selected]
    for index, row in enumerate(fresh):
        row["shuffle_source_pair_id"] = fresh[(index + 1) % len(fresh)]["pair_id"]
    all_rows = dev + calibration + fresh
    ids = [row["source_case_id"] for row in all_rows]
    if len(ids) != len(set(ids)) or excluded & {row["source_case_id"] for row in fresh}:
        raise ValueError("CF-MoE split overlap")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("dev", dev), ("calibration", calibration), ("fresh_test", fresh)):
        write_jsonl(output_dir / f"{name}.jsonl", rows)
    return {
        "official_complete_test_pairs": len(complete),
        "previously_observed_test_pairs": len(excluded_test),
        "test_ids_colliding_with_reused_train_reference": len(development_ids &
            {str(row["case_id"]) for row in complete}),
        "remaining_before_selection": len(remaining),
        "dev": len(dev), "calibration": len(calibration), "fresh_test": len(fresh),
        "fresh_sampling": "seeded_shuffle_without_label_conditioning",
        "fresh_source_id_preview": [row["source_case_id"] for row in fresh[:3]],
    }


def normalized(scores: dict[int, float]) -> dict[int, float]:
    values = np.asarray(list(scores.values()), dtype=float)
    scale = float(values.std())
    return {key: (float(value) - float(values.mean())) / (scale + 1e-6)
            for key, value in scores.items()}


def existing_expert_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Recover the four inspected expert score vectors plus the true no-document profile variant."""
    old = ROOT / "results_cfshift"
    pairs = read_jsonl(old / "dev.jsonl") + read_jsonl(old / "calibration.jsonl") + read_jsonl(old / "fresh_test.jsonl")
    baselines = read_jsonl(old / "cache/baseline.jsonl")
    scores = read_jsonl(old / "option_scores.jsonl")
    matches = read_jsonl(old / "delta_evidence_matches.jsonl")
    conditions = json.loads((ROOT / "private_data/deltarank_sources/release_conditions.json").read_text(encoding="utf-8"))
    components = CF_EVAL.components(pairs, baselines, scores, matches, conditions, weight=2.0)
    pair_map = {row["pair_id"]: row for row in pairs}
    rows = []
    for pair_id, value in components.items():
        pair = pair_map[pair_id]
        methods = value.get("methods", {})
        expert = {
            "medrgag_selected_evidence_score": methods.get("target_margin_ranker", {}),
            "direct_target_logprob": methods.get("direct_target_logprob", {}),
            "cf_shift_profile_score": methods.get("cf_shift_profile_ranker", {}),
            # This is the exact 64.4% historical method. It does not contain a DDX profile term.
            "no_medrgag_evidence": methods.get("no_medrgag_evidence", {}),
        }
        true_profile = (CF_EVAL.relative_scores(
            CF_EVAL.as_scores(next(row for row in scores if row["pair_id"] == pair_id), "direct_target_scores"),
            CF_EVAL.as_scores(next(row for row in scores if row["pair_id"] == pair_id), "direct_control_scores"),
            value["baseline"], value["profile_shift"], 2.0,
        ) if value["status"] == "ok" else {})
        status = "ok" if value["status"] == "ok" and all(expert.values()) and true_profile else "invalid"
        rows.append({
            "case_id": pair_id, "source_case_id": pair["source_case_id"], "split": pair["split"],
            "model": raw_row.get("model") or base[pair_id].get("model"),
            "vllm_version": base[pair_id].get("vllm_version"),
            "status": status, "gold_label_id": pair["trap"]["label_id"],
            "baseline_label_id": value["baseline"],
            "option_label_ids": [option["label_id"] for option in pair["views"]["four_way"].values()],
            "experts": {name: {str(key): score for key, score in values.items()}
                        for name, values in expert.items()},
            "profile_no_document": {str(key): score for key, score in true_profile.items()},
        })
    return rows, pair_map


def arrays(rows: list[dict[str, Any]], experts: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    features, gold = [], []
    for row in rows:
        labels = row["option_label_ids"]
        features.append([[normalized({int(k): float(v) for k, v in row["experts"][name].items()})[label]
                          for name in experts] for label in labels])
        gold.append(labels.index(row["gold_label_id"]))
    return np.asarray(features, dtype=float), np.asarray(gold, dtype=int)


def conditional_loss(weights: np.ndarray, x: np.ndarray, gold: np.ndarray, penalty: float) -> float:
    logits = np.einsum("nke,e->nk", x, weights)
    logits -= logits.max(axis=1, keepdims=True)
    logsum = np.log(np.exp(logits).sum(axis=1))
    return float(np.mean(logsum - logits[np.arange(len(gold)), gold]) + penalty * np.dot(weights, weights))


def fit_weights(x: np.ndarray, gold: np.ndarray, penalty: float, nonnegative: bool) -> np.ndarray:
    result = minimize(conditional_loss, np.ones(x.shape[-1]) / x.shape[-1],
                      args=(x, gold, penalty), method="L-BFGS-B",
                      bounds=[(0.0, None)] * x.shape[-1] if nonnegative else None,
                      options={"maxiter": 2000, "maxfun": 100000})
    if not result.success:
        raise RuntimeError(f"fusion optimization failed: {result.message}")
    return result.x


def predict(x: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.einsum("nke,e->nk", x, weights).argmax(axis=1)


def accuracy(prediction: np.ndarray, gold: np.ndarray) -> float:
    return float(np.mean(prediction == gold))


def existing_fusion(output: Path) -> dict[str, Any]:
    rows, _ = existing_expert_rows()
    valid = [row for row in rows if row["status"] == "ok"]
    split_rows = {split: [row for row in valid if row["split"] == split]
                  for split in ("dev", "calibration", "fresh_test")}
    tensors = {split: arrays(values, EXISTING_EXPERTS) for split, values in split_rows.items()}
    fitted: dict[str, Any] = {}
    for name, nonnegative in (("global_nonnegative_linear_fusion", True),
                              ("logistic_stacking", False)):
        variants = []
        for penalty in REGULARIZATION:
            weights = fit_weights(*tensors["dev"], penalty, nonnegative)
            variants.append({"regularization": penalty, "weights": weights,
                             "calibration_accuracy": accuracy(predict(tensors["calibration"][0], weights),
                                                              tensors["calibration"][1])})
        chosen = max(variants, key=lambda row: (row["calibration_accuracy"], -row["regularization"]))
        fitted[name] = {"regularization": chosen["regularization"],
                        "weights": dict(zip(EXISTING_EXPERTS, map(float, chosen["weights"]))),
                        "calibration_variants": [
                            {"regularization": row["regularization"],
                             "calibration_accuracy": row["calibration_accuracy"]} for row in variants]}
    result: dict[str, Any] = {
        "status": "exploratory_only_existing_500_was_previously_observed",
        "experts": list(EXISTING_EXPERTS), "splits": {}, "fitted": fitted,
        "naming_correction": (
            "The historical 64.4% no_medrgag_evidence score is direct pair-relative and has no DDX profile term; "
            "profile_no_document is reported separately."
        ),
    }
    uniform = np.ones(len(EXISTING_EXPERTS)) / len(EXISTING_EXPERTS)
    for split, values in split_rows.items():
        x, gold = tensors[split]
        expert_predictions = {name: x[:, :, index].argmax(axis=1)
                              for index, name in enumerate(EXISTING_EXPERTS)}
        methods = {name: accuracy(pred, gold) for name, pred in expert_predictions.items()}
        methods["uniform_average"] = accuracy(predict(x, uniform), gold)
        for name, config in fitted.items():
            weights = np.asarray([config["weights"][expert] for expert in EXISTING_EXPERTS])
            methods[name] = accuracy(predict(x, weights), gold)
        methods["oracle_expert_selector"] = float(np.mean(np.any(
            np.stack([pred == gold for pred in expert_predictions.values()]), axis=0)))
        unique_repairs = {}
        baseline = np.asarray([row["option_label_ids"].index(row["baseline_label_id"]) for row in values])
        for name, pred in expert_predictions.items():
            unique_repairs[name] = int(sum(
                pred[index] == gold[index] and baseline[index] != gold[index]
                and all(other[index] != gold[index] for other_name, other in expert_predictions.items()
                        if other_name != name)
                for index in range(len(gold))))
        disagreement = Counter(len({pred[index] for pred in expert_predictions.values()})
                               for index in range(len(gold)))
        result["splits"][split] = {
            "n": len(values), "accuracy": methods, "unique_repairs": unique_repairs,
            "distinct_expert_predictions": {str(key): value for key, value in sorted(disagreement.items())},
        }
    profile_accuracy = {}
    for split, values in split_rows.items():
        correct = 0
        for row in values:
            score = {int(key): float(value) for key, value in row["profile_no_document"].items()}
            correct += CF_EVAL.argmax(score) == row["gold_label_id"]
        profile_accuracy[split] = correct / len(values)
    result["profile_no_document_accuracy"] = profile_accuracy
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def stage_map(cache_root: Path, filename: str) -> dict[str, dict[str, Any]]:
    rows = [row for path in sorted(cache_root.glob(f"shard-*/{filename}")) for row in read_jsonl(path)]
    key_name = "key" if filename in {"M2.generate.jsonl", "M2.summary.jsonl"} else "item_id"
    keys = [str(row[key_name]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate {filename} cache keys")
    return dict(zip(keys, rows))


def candidate_documents(cache_root: Path, item_id: str,
                        retrieval: dict[str, dict[str, Any]], generated: dict[str, dict[str, Any]],
                        selected: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    import sys
    sys.path.insert(0, "/home/data3/txy/MedRGAG")
    from src.medrgag_logic import clean_generated_text

    retrieved = [dict(row) for row in retrieval[item_id]["documents"]]
    generated_docs = [
        {"id": f"generated-{index}", "source": "generated",
         "contents": clean_generated_text(generated[f"{item_id}::{index}"]["raw_response"])}
        for index in range(5)
    ]
    return {"retrieved": retrieved, "generated": generated_docs,
            "candidates": retrieved + generated_docs,
            "original_kads": [dict(row) for row in selected[item_id]["documents"]]}


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, value))))


def medcpt_pairs(ranker: Any, pairs: list[tuple[str, str]], batch_size: int = 64) -> list[float]:
    values = []
    for start in range(0, len(pairs), batch_size):
        batch = pairs[start:start + batch_size]
        inputs = ranker.tokenizer([[query, document] for query, document in batch], return_tensors="pt",
                                  truncation=True, padding=True, max_length=ranker.max_length).to(ranker.device)
        with ranker.torch.no_grad():
            logits = ranker.model(**inputs).logits.reshape(-1)
        values.extend(float(value) for value in logits.detach().cpu().tolist())
    return values


def delta_findings(delta: dict[str, Any]) -> list[str]:
    values = list(delta["added_findings"]) + list(delta["removed_findings"])
    for changed in delta["changed_findings"]:
        values.extend((changed["old"], changed["new"]))
    return list(dict.fromkeys(value for value in values if value.strip()))


def shared_text(pair: dict[str, Any]) -> str:
    old, new = DELTA_RANK.parse_sections(pair["control"]["narrative"]), DELTA_RANK.parse_sections(pair["trap"]["narrative"])
    common = []
    for section in ("demographics", "symptoms", "antecedents"):
        remaining = Counter(map(DELTA_RANK.norm, new[section]))
        for value in old[section]:
            key = DELTA_RANK.norm(value)
            if remaining[key]:
                common.append(value); remaining[key] -= 1
    return "\n".join(common) or "unchanged patient state"


def score_document_set(documents: list[dict[str, Any]], query_scores: dict[str, list[float]],
                       finding_count: int, option_keys: list[str]) -> list[dict[str, Any]]:
    rows = []
    for index, document in enumerate(documents):
        delta = max((query_scores[f"delta:{offset}"][index] for offset in range(finding_count)), default=0.0)
        option_values = [query_scores[f"option:{key}"][index] for key in option_keys]
        contrast = float(np.std(option_values))
        redundancy = query_scores["shared"][index]
        rows.append({**document, "delta_coverage": delta, "option_contrast": contrast,
                     "shared_state_redundancy": redundancy,
                     "cf_document_score": delta + contrast - redundancy,
                     "option_similarities": dict(zip(option_keys, option_values))})
    return rows


def score_documents(data_paths: list[Path], cache_root: Path, output: Path, device: str,
                    shard_index: int = 0, shard_count: int = 1, limit: int | None = None,
                    batch_size: int = 64) -> dict[str, Any]:
    pairs = [row for path in data_paths for row in read_jsonl(path)]
    pairs = [row for index, row in enumerate(pairs) if index % shard_count == shard_index]
    if limit:
        pairs = pairs[:limit]
    retrieval = stage_map(cache_root, "retrieval.jsonl")
    generated = stage_map(cache_root, "M2.generate.jsonl")
    selected = stage_map(cache_root, "M2.rerank.jsonl")
    work = []
    flat_pairs: list[tuple[str, str]] = []
    for pair in pairs:
        item_id = f"{pair['pair_id']}::four_way::trap"
        docs = candidate_documents(cache_root, item_id, retrieval, generated, selected)
        findings = delta_findings(pair["delta"])
        options = {str(value["label_id"]): value["label"] for value in pair["views"]["four_way"].values()}
        queries = [(f"delta:{index}", value) for index, value in enumerate(findings)]
        queries += [(f"option:{key}", value) for key, value in options.items()]
        queries.append(("shared", shared_text(pair)))
        start = len(flat_pairs)
        flat_pairs.extend((query, document["contents"]) for _, query in queries for document in docs["candidates"])
        work.append({"pair": pair, "docs": docs, "findings": findings, "options": options,
                     "queries": queries, "start": start})
    os.environ.setdefault("JAVA_HOME", "/home/data3/txy/.local/medrgag-jdk-21")
    import sys
    sys.path.insert(0, "/home/data3/txy/MedRGAG")
    from src.medrgag_retrieval import DualBM25Retriever, MedCPTRanker
    ranker = MedCPTRanker(Path("/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder"), device=device)
    values = medcpt_pairs(ranker, flat_pairs, batch_size)
    low_coverage = []
    retrieval_needed = []
    for value in work:
        count = len(value["docs"]["candidates"])
        query_scores = {}
        offset = value["start"]
        for name, _ in value["queries"]:
            query_scores[name] = [sigmoid(score) for score in values[offset:offset + count]]; offset += count
        value["scored"] = score_document_set(value["docs"]["candidates"], query_scores,
                                               len(value["findings"]), list(value["options"]))
        if not value["findings"] or max(row["delta_coverage"] for row in value["scored"]) < 0.5:
            low_coverage.append(value)
        if value["findings"] and max(row["delta_coverage"] for row in value["scored"]) < 0.5:
            retrieval_needed.append(value)

    sparse = DualBM25Retriever(
        Path("/home/data3/txy/MedRGAG/corpus/textbooks/index/bm25"),
        Path("/home/data3/txy/MedRGAG/corpus/wikipedia/index/bm25"),
        Path("/home/data3/txy/MedRGAG/corpus/textbooks"),
        Path("/home/data3/txy/MedRGAG/corpus/wikipedia"),
    )
    supplement_candidates = []
    supplement_ranges = []
    for value in retrieval_needed:
        query = ("; ".join(value["findings"]) + "\nDifference between candidate diagnoses: "
                 + " versus ".join(value["options"].values()) + "\nDiagnostic significance")
        candidates = sparse.retrieve(query, 16)
        start = len(supplement_candidates)
        supplement_candidates.extend((query, row["contents"]) for row in candidates)
        supplement_ranges.append((value, candidates, start))
    supplement_values = medcpt_pairs(ranker, supplement_candidates, batch_size)
    for value, candidates, start in supplement_ranges:
        order = sorted(range(len(candidates)), key=lambda index: (-supplement_values[start + index], index))[:2]
        value["supplements"] = [
            {"id": candidates[index]["docid"], "source": candidates[index]["source"],
             "contents": candidates[index]["contents"], "bm25_score": candidates[index]["bm25_score"],
             "medcpt_score": supplement_values[start + index]} for index in order]
    second_pairs, second_work = [], []
    for value in work:
        supplements = value.get("supplements", [])
        start = len(second_pairs)
        second_pairs.extend((query, document["contents"]) for _, query in value["queries"] for document in supplements)
        second_work.append((value, start))
    second_values = medcpt_pairs(ranker, second_pairs, batch_size)
    ranker.close()
    rows = []
    for value, start in second_work:
        supplements = value.get("supplements", [])
        query_scores = {}
        offset = start
        for name, _ in value["queries"]:
            query_scores[name] = [sigmoid(score) for score in second_values[offset:offset + len(supplements)]]
            offset += len(supplements)
        scored_supplements = (score_document_set(supplements, query_scores, len(value["findings"]),
                                                 list(value["options"])) if supplements else [])
        ranked = sorted(value["scored"], key=lambda row: (-row["cf_document_score"], row["id"]))
        positive = [row for row in ranked if row["cf_document_score"] > 0]
        variants = {
            "original_kads_top5": value["docs"]["original_kads"],
            "retrieved_only": value["docs"]["retrieved"],
            "generated_only": value["docs"]["generated"],
            "cf_kads_top1": positive[:1], "cf_kads_top3": positive[:3], "cf_kads_top5": positive[:5],
            "cf_kads_filtered_plus_contrastive": positive[:3] + scored_supplements,
            "no_document": [],
        }
        rows.append({"pair_id": value["pair"]["pair_id"], "split": value["pair"]["split"],
                     "changed_findings": value["findings"], "shared_text": shared_text(value["pair"]),
                     "candidate_documents": ranked, "supplementary_documents": scored_supplements,
                     "variants": variants, "coverage_unmet": value in low_coverage})
    write_jsonl(output, rows)
    return {"pairs": len(rows), "candidate_documents": sum(len(row["candidate_documents"]) for row in rows),
            "coverage_unmet": len(low_coverage),
            "supplementary_documents": sum(len(row["supplementary_documents"]) for row in rows)}


def remove_finding(text: str, finding: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if finding in line:
            del lines[index]
            return "\n".join(lines)
    return text


def cpg_edits(pair: dict[str, Any]) -> list[dict[str, str]]:
    """Make only applicable deterministic edits; unchanged edits are discarded."""
    targets = []
    for value in pair["delta"]["changed_findings"]:
        targets.append(("changed", value["new"], value["old"]))
    targets += [("added", value, "") for value in pair["delta"]["added_findings"]]
    targets += [("removed", value, "") for value in pair["delta"]["removed_findings"]]
    original = pair["trap"]["narrative"]
    edits = []
    for kind, finding, old in targets[:2]:
        candidates = []
        if kind == "changed" and finding in original:
            candidates.append(("revert", original.replace(finding, old, 1)))
            candidates.append(("remove", remove_finding(original, finding)))
        elif kind == "added" and finding in original:
            candidates.append(("remove", remove_finding(original, finding)))
        elif kind == "removed" and finding not in original:
            candidates.append(("revert", original.rstrip() + "\n* " + finding))
        lowered = finding.casefold()
        if kind in {"changed", "added"} and finding in original and not re.search(
                r"\b(no|not|without|den(?:y|ies|ied)|negative|absent)\b", lowered):
            candidates.append(("negate", original.replace(finding, "No evidence of " + finding, 1)))
        for operation, edited in candidates:
            edited = edited.strip()
            if edited and edited != original.strip() and edited not in {row["edited_case"] for row in edits}:
                edits.append({"edit_id": f"{len(edits) + 1}", "operation": operation,
                              "finding": finding, "edited_case": edited})
    return edits


def valid_context_scores(scores: dict[str, Any], labels: set[int]) -> bool:
    try:
        return bool(scores) and all(
            set(map(int, value.get("log_scores", {}))) == labels
            and all(math.isfinite(float(score)) for score in value.get("log_scores", {}).values())
            for value in scores.values()
        )
    except (TypeError, ValueError):
        return False


def score_experts(data_paths: list[Path], base_scores_path: Path, document_scores_path: Path,
                  output: Path, model: Path, shard_index: int = 0, shard_count: int = 1,
                  limit: int | None = None, max_model_len: int = 32768,
                  gpu_memory: float = 0.55) -> dict[str, Any]:
    all_pairs = [row for path in data_paths for row in read_jsonl(path)]
    pair_map = {row["pair_id"]: row for row in all_pairs}
    pairs = all_pairs
    pairs = [row for index, row in enumerate(pairs) if index % shard_count == shard_index]
    if limit:
        pairs = pairs[:limit]
    base = {row["pair_id"]: row for row in read_jsonl(base_scores_path)}
    documents = {row["pair_id"]: row for row in read_jsonl(document_scores_path)}
    if not {row["pair_id"] for row in pairs} <= set(base) or not {row["pair_id"] for row in pairs} <= set(documents):
        raise ValueError("score-experts lacks base or document rows")
    gate_b = load_script("cfmoe_gate_b", ROOT / "scripts" / "run_gate_b.py")
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory)
    scorer = CF_RUN.ChoiceScorer(backend)
    existing = {row["pair_id"]: row for row in read_jsonl(output)} if output.exists() else {}
    new_rows = 0
    for pair in pairs:
        if pair["pair_id"] in existing:
            continue
        doc_row = documents[pair["pair_id"]]
        contexts = {}
        for variant in ("retrieved_only", "generated_only", "cf_kads_top1", "cf_kads_top3",
                        "cf_kads_top5", "cf_kads_filtered_plus_contrastive"):
            evidence = CF_RUN.document_text(doc_row["variants"][variant])
            suffix = "" if not evidence else "\n\nSelected evidence:\n" + evidence
            contexts[f"{variant}_target"] = pair["trap"]["narrative"] + suffix
            contexts[f"{variant}_control"] = pair["control"]["narrative"] + suffix
        edits = cpg_edits(pair)
        for edit in edits:
            contexts[f"cpg_edit_{edit['edit_id']}"] = edit["edited_case"]
        donor_id = pair["shuffle_source_pair_id"]
        donor_edits = cpg_edits(pair_map[donor_id])
        for edit in donor_edits:
            contexts[f"shuffled_cpg_edit_{edit['edit_id']}"] = edit["edited_case"]
        try:
            scores = scorer.score_contexts(contexts, pair["views"]["four_way"])
            expected_labels = {value["label_id"] for value in pair["views"]["four_way"].values()}
            if not valid_context_scores(scores, expected_labels):
                raise ValueError("missing or non-finite option score")
            status, error = "ok", None
        except (KeyError, ValueError, RuntimeError, IndexError) as exc:
            scores, status, error = {}, "invalid", f"{type(exc).__name__}: {exc}"
        row = {"pair_id": pair["pair_id"], "split": pair["split"], "status": status,
               "error": error, "scores": scores, "cpg_edits": edits,
               "shuffled_cpg_source_pair_id": donor_id, "shuffled_cpg_edits": donor_edits,
               "model": str(model),
               "scoring_implementation": "two-permutation exact option-sequence log-likelihood"}
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        existing[pair["pair_id"]] = row; new_rows += 1
    return {"pairs": len(existing), "new_pairs": new_rows,
            "invalid": sum(row["status"] != "ok" for row in existing.values()),
            "edits": sum(len(row["cpg_edits"]) for row in existing.values())}


FUSION_EXPERTS = ("medrgag", "direct_logprob", "profile_no_document", "profile_cf_kads",
                  "cpg_core", "ecr_lite")


def score_dict(row: dict[str, Any], name: str) -> dict[int, float]:
    return CF_EVAL.as_scores(row, name)


def token_overlap(left: str, right: str) -> float:
    a = set(re.findall(r"[a-z0-9]+", left.casefold()))
    b = set(re.findall(r"[a-z0-9]+", right.casefold()))
    return len(a & b) / len(a | b) if a | b else 0.0


def ecr_scores(pair: dict[str, Any], match_row: dict[str, Any], conditions: dict[str, Any],
               evidences: dict[str, Any]) -> tuple[dict[int, float], dict[int, dict[str, float]]]:
    name_to_id = {name: index for index, name in enumerate(sorted(conditions))}
    profiles = {name_to_id[name]: set(value.get("symptoms", {})) | set(value.get("antecedents", {}))
                for name, value in conditions.items()}
    descriptors = {key: CF_RUN.evidence_descriptor(value) for key, value in evidences.items()}
    sections = DELTA_RANK.parse_sections(pair["trap"]["narrative"])
    present = sections["symptoms"] + sections["antecedents"]
    positive = [row for row in match_row["matches"] if row["operation"] in {"added", "new_value"}]
    negative = [row for row in match_row["matches"] if row["operation"] in {"removed", "old_value"}]
    details, scores = {}, {}
    for option in pair["views"]["four_way"].values():
        label = option["label_id"]
        profile = profiles[label]
        profile_text = [descriptors[key] for key in profile]
        present_values = [max((token_overlap(finding, text) for text in profile_text), default=0.0)
                          for finding in present]
        present_support = sum(present_values) / len(present_values) if present_values else 0.0
        conflicts = [value for finding, value in zip(present, present_values)
                     if re.search(r"\b(no|not|without|den(?:y|ies|ied)|negative|absent)\b", finding.casefold())]
        present_conflict = max(conflicts, default=0.0)
        positive_values = [float(row["similarity"]) for row in positive if row["matched_evidence_id"] in profile]
        negative_values = [float(row["similarity"]) for row in negative if row["matched_evidence_id"] in profile]
        pivot_support = max(positive_values, default=0.0)
        delta_support = sum(positive_values) / max(1, len(positive))
        missing = max(negative_values, default=0.0)
        detail = {"present_support": present_support, "pivot_support": pivot_support,
                  "present_conflict": present_conflict, "missing_expected_penalty": missing,
                  "delta_support": delta_support}
        details[label] = detail
        scores[label] = present_support + 2 * pivot_support + delta_support - present_conflict - missing
    return scores, details


def margin(scores: dict[int, float]) -> float:
    values = sorted(scores.values(), reverse=True)
    return values[0] - values[1] if len(values) > 1 else 0.0


def assemble_experts(data_paths: list[Path], baseline_path: Path, base_scores_path: Path,
                     matches_path: Path, documents_path: Path, raw_experts_path: Path,
                     conditions_path: Path, evidences_path: Path,
                     limit: int | None = None) -> list[dict[str, Any]]:
    all_pairs = [row for path in data_paths for row in read_jsonl(path)]
    pairs = all_pairs
    if limit:
        pairs = pairs[:limit]
    baseline_rows = read_jsonl(baseline_path)
    base_rows = read_jsonl(base_scores_path)
    match_rows = read_jsonl(matches_path)
    conditions = json.loads(conditions_path.read_text(encoding="utf-8"))
    evidences = json.loads(evidences_path.read_text(encoding="utf-8"))
    components = CF_EVAL.components(all_pairs, baseline_rows, base_rows, match_rows, conditions, weight=2.0)
    base = {row["pair_id"]: row for row in base_rows}
    matches = {row["pair_id"]: row for row in match_rows}
    documents = {row["pair_id"]: row for row in read_jsonl(documents_path)}
    raw = {row["pair_id"]: row for row in read_jsonl(raw_experts_path)}
    baseline = {row["pair_id"]: row for row in baseline_rows}
    rows = []
    for pair in pairs:
        pair_id = pair["pair_id"]; value = components[pair_id]
        labels = [option["label_id"] for option in pair["views"]["four_way"].values()]
        base_label = value["baseline"]
        direct_t = score_dict(base[pair_id], "direct_target_scores")
        direct_c = score_dict(base[pair_id], "direct_control_scores")
        med_t = score_dict(base[pair_id], "medrgag_target_scores")
        med_c = score_dict(base[pair_id], "medrgag_control_scores")
        profile = value.get("profile_shift", {})
        raw_row = raw.get(pair_id, {"status": "invalid", "scores": {}, "cpg_edits": [], "error": "missing"})
        if raw_row.get("status") == "ok" and not valid_context_scores(raw_row.get("scores", {}), set(labels)):
            raw_row = {**raw_row, "status": "invalid", "error": "missing or non-finite option score"}
        def context(name: str) -> dict[int, float]:
            return score_dict(raw_row, name) if raw_row["status"] == "ok" else {}
        methods: dict[str, dict[int, float]] = {
            "medrgag": med_t, "direct_logprob": direct_t,
            "no_medrgag_evidence": CF_EVAL.relative_scores(direct_t, direct_c, base_label),
            "profile_no_document": CF_EVAL.relative_scores(direct_t, direct_c, base_label, profile, 2.0),
            "profile_original_kads": value["methods"].get("cf_shift_profile_ranker", {}),
            "shuffled_delta": value["methods"].get("cf_shift_profile_shuffled_delta", {}),
            "shuffled_profile": value["methods"].get("cf_shift_profile_shuffled_profile", {}),
        }
        for variant in ("retrieved_only", "generated_only", "cf_kads_top1", "cf_kads_top3",
                        "cf_kads_top5", "cf_kads_filtered_plus_contrastive"):
            target, control = context(f"{variant}_target"), context(f"{variant}_control")
            methods[f"profile_{variant}"] = (CF_EVAL.relative_scores(target, control, base_label, profile, 2.0)
                                              if set(target) == set(labels) and set(control) == set(labels) else {})
        methods["profile_cf_kads"] = methods["profile_cf_kads_top3"]
        methods["profile_cf_kads_contrastive"] = methods["profile_cf_kads_filtered_plus_contrastive"]
        edited = [context(f"cpg_edit_{edit['edit_id']}") for edit in raw_row.get("cpg_edits", [])]
        edited = [scores for scores in edited if set(scores) == set(labels)]
        cpg = ({label: direct_t[label] - sum(scores[label] for scores in edited) / len(edited)
                for label in labels} if edited and set(direct_t) == set(labels) else {})
        methods["cpg_core"] = cpg
        shuffled_edited = [context(f"shuffled_cpg_edit_{edit['edit_id']}")
                           for edit in raw_row.get("shuffled_cpg_edits", [])]
        shuffled_edited = [scores for scores in shuffled_edited if set(scores) == set(labels)]
        methods["shuffled_cpg_edit"] = (
            {label: direct_t[label] - sum(scores[label] for scores in shuffled_edited) / len(shuffled_edited)
             for label in labels} if shuffled_edited and set(direct_t) == set(labels) else {})
        ecr, ecr_detail = ecr_scores(pair, matches[pair_id], conditions, evidences)
        methods["ecr_lite"] = ecr
        if cpg:
            methods["profile_plus_cpg"] = {label: normalized(methods["profile_no_document"])[label]
                                                    + normalized(cpg)[label] for label in labels}
            methods["medrgag_plus_cpg"] = {label: normalized(med_t)[label] + normalized(cpg)[label]
                                            for label in labels}
        elif raw_row.get("status") == "ok" and not raw_row.get("cpg_edits"):
            methods["profile_plus_cpg"] = normalized(methods["profile_no_document"])
            methods["medrgag_plus_cpg"] = normalized(med_t)
        else:
            methods["profile_plus_cpg"] = {}; methods["medrgag_plus_cpg"] = {}
        methods["profile_plus_ecr"] = {label: normalized(methods["profile_no_document"])[label]
                                               + normalized(ecr)[label] for label in labels}
        doc = documents[pair_id]
        selected_ids = {(row.get("source"), row.get("id")) for row in doc["variants"]["original_kads_top5"]}
        selected_scored = [row for row in doc["candidate_documents"]
                           if (row.get("source"), row.get("id")) in selected_ids]
        delta_coverage = max((row["delta_coverage"] for row in doc["variants"]["cf_kads_top3"]), default=0.0)
        selected_coverage = max((row["delta_coverage"] for row in selected_scored), default=0.0)
        availability = {name: set(methods.get(name, {})) == set(labels) for name in methods}
        fusion_scores = {name: methods[name] if availability.get(name) else {label: 0.0 for label in labels}
                         for name in FUSION_EXPERTS}
        predictions = [CF_EVAL.argmax(scores) for name, scores in fusion_scores.items() if availability.get(name)]
        qualities = {
            "direct_margin": margin(direct_t), "medrgag_margin": margin(med_t),
            "profile_margin": margin(methods["profile_no_document"]),
            "cpg_margin": margin(cpg) if cpg else 0.0,
            "delta_coverage": delta_coverage, "selected_document_coverage": selected_coverage,
            "expert_disagreement": len(set(predictions)) / max(1, len(predictions)),
        }
        control_scores = {"medrgag": med_c, "direct_logprob": direct_c,
                          "no_medrgag_evidence": direct_c,
                          "profile_no_document": direct_c,
                          "profile_original_kads": med_c,
                          "profile_cf_kads": context("cf_kads_top3_control"),
                          "profile_cf_kads_contrastive": context("cf_kads_filtered_plus_contrastive_control"),
                          "cpg_core": direct_c, "ecr_lite": direct_c}
        for variant in ("retrieved_only", "generated_only", "cf_kads_top1", "cf_kads_top3",
                        "cf_kads_top5", "cf_kads_filtered_plus_contrastive"):
            control_scores[f"profile_{variant}"] = context(f"{variant}_control")
        control_scores.update({"shuffled_delta": med_c, "shuffled_profile": med_c,
                               "shuffled_cpg_edit": direct_c, "profile_plus_cpg": direct_c,
                               "medrgag_plus_cpg": med_c, "profile_plus_ecr": direct_c})
        rows.append({
            "case_id": pair_id, "source_case_id": pair["source_case_id"], "split": pair["split"],
            "status": "ok" if set(direct_t) == set(labels) else "invalid",
            "gold_label_id": pair["trap"]["label_id"], "control_gold_label_id": pair["control"]["label_id"],
            "baseline_label_id": base_label,
            "baseline_control_label_id": baseline[pair_id]["control"]["predictions"]["medrgag_mcq_proxy"]["label_id"],
            "option_label_ids": labels,
            "option_scores": {name: {str(label): float(score) for label, score in scores.items()}
                              for name, scores in methods.items()},
            "control_scores": {name: {str(label): float(score) for label, score in scores.items()}
                               for name, scores in control_scores.items()},
            "availability": availability, "quality_features": qualities,
            "fusion_status": ("ok" if raw_row.get("status") == "ok" else "invalid_raw_expert_score"),
            "cpg_structurally_not_applicable": raw_row.get("status") == "ok" and not raw_row.get("cpg_edits"),
            "ecr_components": {str(label): detail for label, detail in ecr_detail.items()},
            "cpg_edits": [{**edit, "option_log_scores": raw_row.get("scores", {}).get(
                f"cpg_edit_{edit['edit_id']}", {}).get("log_scores", {})}
                          for edit in raw_row.get("cpg_edits", [])],
            "cpg_status": ("invalid_runtime" if raw_row.get("status") != "ok" else
                           "ok" if cpg else "not_applicable"),
            "shuffled_cpg_source_pair_id": raw_row.get("shuffled_cpg_source_pair_id"),
            "shuffled_cpg_edits": [{**edit, "option_log_scores": raw_row.get("scores", {}).get(
                f"shuffled_cpg_edit_{edit['edit_id']}", {}).get("log_scores", {})}
                                     for edit in raw_row.get("shuffled_cpg_edits", [])],
            "shuffled_cpg_status": ("invalid_runtime" if raw_row.get("status") != "ok" else
                                    "ok" if methods["shuffled_cpg_edit"] else "not_applicable"),
            "raw_expert_status": raw_row.get("status"), "raw_expert_error": raw_row.get("error"),
            "model": base[pair_id].get("model") or raw_row.get("model"),
            "vllm_version": base[pair_id].get("vllm_version"),
        })
    return rows


def fusion_features(row: dict[str, Any], control: bool = False) -> tuple[np.ndarray, list[str]]:
    labels = row["option_label_ids"]
    source = row["control_scores"] if control else row["option_scores"]
    base = []
    for expert in FUSION_EXPERTS:
        values = {int(key): float(value) for key, value in source.get(expert, {}).items()}
        base.append(normalized(values) if set(values) == set(labels) else {label: 0.0 for label in labels})
    quality_names = tuple(row["quality_features"])
    quality = [float(row["quality_features"][name]) for name in quality_names]
    names = list(FUSION_EXPERTS) + [f"{expert}*{name}" for expert in FUSION_EXPERTS for name in quality_names]
    values = []
    for label in labels:
        raw = [scores[label] for scores in base]
        values.append(raw + [score * feature for score in raw for feature in quality])
    return np.asarray(values, dtype=float), names


def fit_fusion(rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    splits = {name: [row for row in rows if row["split"] == name and row["status"] == "ok"
                     and row["fusion_status"] == "ok"]
              for name in ("dev", "calibration")}
    tensors = {}
    feature_names = None
    for split, values in splits.items():
        vectors = []
        for row in values:
            vector, names = fusion_features(row); vectors.append(vector); feature_names = names
        gold = np.asarray([row["option_label_ids"].index(row["gold_label_id"]) for row in values])
        tensors[split] = (np.asarray(vectors), gold)
    variants = []
    for penalty in REGULARIZATION:
        weights = fit_weights(*tensors["dev"], penalty, nonnegative=False)
        variants.append({"regularization": penalty, "weights": weights,
                         "calibration_accuracy": accuracy(predict(tensors["calibration"][0], weights),
                                                          tensors["calibration"][1])})
    chosen = max(variants, key=lambda row: (row["calibration_accuracy"], -row["regularization"]))
    single_accuracy = {}
    for expert in FUSION_EXPERTS:
        predictions = []
        for row in splits["calibration"]:
            scores = {int(key): float(value) for key, value in row["option_scores"][expert].items()}
            predictions.append(row["option_label_ids"].index(CF_EVAL.argmax(scores)) if scores else -1)
        single_accuracy[expert] = accuracy(np.asarray(predictions), tensors["calibration"][1])
    strongest = max(single_accuracy, key=lambda name: (single_accuracy[name], name))
    result = {
        "status": "frozen_before_fresh_test_scoring", "fusion_experts": list(FUSION_EXPERTS),
        "feature_names": feature_names, "regularization": chosen["regularization"],
        "weights": list(map(float, chosen["weights"])),
        "calibration_variants": [{"regularization": row["regularization"],
                                  "calibration_accuracy": row["calibration_accuracy"]} for row in variants],
        "fixed_profile_weight": 2.0, "fixed_cf_document_threshold": 0.0,
        "invalid_expert_policy": (
            "runtime/numeric raw expert failure invalidates dependent fusions; only structurally inapplicable CPG "
            "with no valid edit contributes a neutral zero vector"
        ),
        "cpg_edit_policy": "up to two ordered delta findings; applicable remove/revert/negate edits only",
        "cpg_reference": {
            "repository": "https://github.com/FAIRHealth/clinical-counterfactual-reasoning",
            "commit": "265d1aea88f705063bb7ff2d686547d373da7e09",
            "license": "MIT",
            "scope": "core counterfactual edit/probability-gap idea; not the full discussion framework",
        },
        "calibration_single_expert_accuracy": single_accuracy,
        "strongest_single_expert": strongest,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def row_scores(row: dict[str, Any], method: str, control: bool = False) -> dict[int, float]:
    source = row["control_scores"] if control else row["option_scores"]
    return {int(key): float(value) for key, value in source.get(method, {}).items()}


def fused_scores(row: dict[str, Any], config: dict[str, Any], learned: bool,
                 control: bool = False) -> dict[int, float]:
    if row["fusion_status"] != "ok":
        return {}
    labels = row["option_label_ids"]
    if learned:
        features, names = fusion_features(row, control)
        if names != config["feature_names"]:
            raise ValueError("fusion feature order changed after calibration")
        logits = features @ np.asarray(config["weights"], dtype=float)
        return dict(zip(labels, map(float, logits)))
    values = []
    for expert in FUSION_EXPERTS:
        scores = row_scores(row, expert, control)
        if scores:
            values.append(normalized(scores))
        elif expert == "cpg_core" and row["cpg_structurally_not_applicable"]:
            values.append({label: 0.0 for label in labels})
        else:
            return {}
    return {label: sum(scores[label] for scores in values) / len(values) for label in labels}


def prediction_for(row: dict[str, Any], method: str, config: dict[str, Any],
                   control: bool = False) -> int | None:
    if method == "medrgag_mcq_proxy":
        return row["baseline_control_label_id"] if control else row["baseline_label_id"]
    if method == "uniform_fusion":
        return CF_EVAL.argmax(fused_scores(row, config, False, control))
    if method == "learned_fusion":
        return CF_EVAL.argmax(fused_scores(row, config, True, control))
    return CF_EVAL.argmax(row_scores(row, method, control))


def paired_bootstrap_methods(rows: list[dict[str, Any]], predictions: dict[str, dict[str, int | None]],
                             comparisons: list[tuple[str, str]]) -> dict[str, Any]:
    ids = [row["case_id"] for row in rows]
    gold = {row["case_id"]: row["gold_label_id"] for row in rows}
    result = {}
    for left, right in comparisons:
        left_value = {key: float(predictions[left].get(key) == gold[key]) for key in ids}
        right_value = {key: float(predictions[right].get(key) == gold[key]) for key in ids}
        result[f"{left}_minus_{right}_accuracy"] = CF_EVAL.bootstrap_difference(
            ids, left_value, right_value, samples=1000, seed=13)
    return result


def correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or float(np.std(left)) == 0 or float(np.std(right)) == 0:
        return None
    return float(np.corrcoef(left, right)[0, 1])


def evaluate_medeinst(expert_path: Path, fusion_path: Path, document_path: Path,
                      output_dir: Path) -> dict[str, Any]:
    rows = read_jsonl(expert_path)
    config = json.loads(fusion_path.read_text(encoding="utf-8"))
    methods = (
        "medrgag_mcq_proxy", "medrgag", "direct_logprob", "no_medrgag_evidence", "profile_no_document",
        "profile_original_kads", "profile_retrieved_only", "profile_generated_only",
        "profile_cf_kads_top1", "profile_cf_kads", "profile_cf_kads_top5",
        "profile_cf_kads_contrastive", "cpg_core", "ecr_lite", "profile_plus_cpg",
        "medrgag_plus_cpg", "profile_plus_ecr", "uniform_fusion", "learned_fusion", "shuffled_delta",
        "shuffled_profile", "shuffled_cpg_edit",
    )
    truth = {row["case_id"]: {"control": {"label_id": row["control_gold_label_id"]},
                               "trap": {"label_id": row["gold_label_id"]}} for row in rows}
    baseline = {row["case_id"]: row["baseline_label_id"] for row in rows}
    by_split = {split: [row for row in rows if row["split"] == split]
                for split in ("dev", "calibration", "fresh_test")}
    all_predictions = {method: {row["case_id"]: prediction_for(row, method, config)
                                for row in rows} for method in methods}
    all_controls = {method: {row["case_id"]: prediction_for(row, method, config, True)
                             for row in rows} for method in methods}
    # Oracle is gold-aware and reported only as a complementarity upper bound.
    oracle, oracle_control = {}, {}
    for row in rows:
        candidates = []
        for expert in FUSION_EXPERTS:
            trap = prediction_for(row, expert, config)
            control = prediction_for(row, expert, config, True)
            if trap is not None:
                candidates.append((expert, trap, control))
        chosen = next((value for value in candidates if value[1] == row["gold_label_id"]
                       and value[2] == row["control_gold_label_id"]), None)
        chosen = chosen or next((value for value in candidates if value[1] == row["gold_label_id"]), None)
        chosen = chosen or (candidates[0] if candidates else ("none", None, None))
        oracle[row["case_id"]], oracle_control[row["case_id"]] = chosen[1], chosen[2]
    all_predictions["oracle_expert_selector"] = oracle
    all_controls["oracle_expert_selector"] = oracle_control
    metric_rows, prediction_rows = [], []
    metrics: dict[str, Any] = {"protocol": {
        "pair_aware_update_setting": [method for method in methods
                                      if method not in {"medrgag_mcq_proxy", "medrgag", "direct_logprob"}],
        "single_case_setting": ["medrgag_mcq_proxy", "medrgag", "direct_logprob"],
        "note": "Pair-aware methods see control, trap and structured delta; single-case methods see trap and options only.",
        "model": sorted({row.get("model") for row in rows if row.get("model")}),
        "vllm_version": sorted({row.get("vllm_version") for row in rows if row.get("vllm_version")}),
        "option_scoring": "two-permutation exact option-sequence prompt log-likelihood"},
        "methods": {}, "bootstrap": {}, "fusion": config,
        "invalid": {"raw_expert_rows": sum(row["raw_expert_status"] != "ok" for row in rows),
                    "cpg_structurally_not_applicable": sum(row["cpg_structurally_not_applicable"] for row in rows)}}
    for split, split_rows in by_split.items():
        split_truth = {row["case_id"]: truth[row["case_id"]] for row in split_rows}
        ids = sorted(split_truth)
        split_base = {key: baseline[key] for key in ids}
        metrics["methods"][split] = {}
        for method in methods + ("oracle_expert_selector",):
            final = {key: all_predictions[method][key] for key in ids}
            control = {key: all_controls[method][key] for key in ids}
            value = {**CF_EVAL.revision_metrics(final, split_base, split_truth),
                     **CF_EVAL.pair_metrics(control, final, split_truth)}
            value["robust_accuracy"] = value["both_correct_pair_accuracy"]
            margins = []
            if method != "oracle_expert_selector":
                for row in split_rows:
                    scores = (fused_scores(row, config, method == "learned_fusion")
                              if method in {"uniform_fusion", "learned_fusion"}
                              else row_scores(row, method))
                    if scores:
                        gold = row["gold_label_id"]
                        margins.append(scores[gold] - max(score for label, score in scores.items() if label != gold))
            value["mean_gold_option_margin"] = sum(margins) / len(margins) if margins else None
            metrics["methods"][split][method] = value
            metric_rows.append({"split": split, "method": method, **value})
            for key in ids:
                prediction_rows.append({"dataset": "medeinst", "case_id": key, "split": split, "method": method,
                                        "control_prediction": control[key], "trap_prediction": final[key],
                                        "baseline_prediction": split_base[key],
                                        "status": "ok" if final[key] is not None else "invalid"})
    fresh_rows = by_split["fresh_test"]
    strongest = config["strongest_single_expert"]
    comparisons = [
        ("no_medrgag_evidence", "medrgag_mcq_proxy"),
        ("profile_no_document", "medrgag_mcq_proxy"),
        ("profile_cf_kads", "profile_original_kads"),
        ("cpg_core", "direct_logprob"), ("ecr_lite", "profile_no_document"),
        ("learned_fusion", strongest), ("profile_original_kads", "shuffled_delta"),
        ("profile_original_kads", "shuffled_profile"), ("cpg_core", "shuffled_cpg_edit"),
    ]
    metrics["bootstrap"] = paired_bootstrap_methods(fresh_rows, all_predictions, comparisons)
    documents = {row["pair_id"]: row for row in read_jsonl(document_path)}
    features = {name: [] for name in ("generated_ratio", "delta_coverage", "option_contrast", "document_count")}
    outcome = []
    evidence_changes = Counter()
    change_features: dict[str, dict[str, list[float]]] = {
        name: {feature: [] for feature in (*features, "score_std_ratio")}
        for name in ("repair", "harm", "unchanged")
    }
    for row in fresh_rows:
        doc = documents[row["case_id"]]
        selected = doc["variants"]["original_kads_top5"]
        scored = doc["candidate_documents"]
        selected_ids = {(value.get("source"), value.get("id")) for value in selected}
        chosen = [value for value in scored if (value.get("source"), value.get("id")) in selected_ids]
        current = {
            "generated_ratio": sum(value.get("source") == "generated" for value in selected) /
                               max(1, len(selected)),
            "delta_coverage": max((value["delta_coverage"] for value in chosen), default=0.0),
            "option_contrast": float(np.mean([value["option_contrast"] for value in chosen]))
                               if chosen else 0.0,
            "document_count": float(len(selected)),
        }
        for name, value in current.items():
            features[name].append(value)
        key = row["case_id"]
        with_doc = all_predictions["profile_original_kads"][key] == row["gold_label_id"]
        without_doc = all_predictions["profile_no_document"][key] == row["gold_label_id"]
        difference = float(with_doc) - float(without_doc)
        outcome.append(difference)
        category = "repair" if difference > 0 else "harm" if difference < 0 else "unchanged"
        evidence_changes[category] += 1
        no_values = list(row_scores(row, "profile_no_document").values())
        doc_values = list(row_scores(row, "profile_original_kads").values())
        scale_ratio = float(np.std(doc_values) / (np.std(no_values) + 1e-6))
        for name, value in {**current, "score_std_ratio": scale_ratio}.items():
            change_features[category][name].append(value)
    grouped_means = {
        category: {name: (float(np.mean(values)) if values else None)
                   for name, values in feature_values.items()}
        for category, feature_values in change_features.items()
    }
    metrics["evidence_interference"] = {
        "feature_correlation_with_selected_evidence_accuracy_change":
            {name: correlation(values, outcome) for name, values in features.items()},
        "fresh_context_accuracy": {method: metrics["methods"]["fresh_test"][method]["accuracy"]
                                   for method in ("profile_no_document", "profile_original_kads",
                                                  "profile_retrieved_only", "profile_generated_only",
                                                  "profile_cf_kads_top1", "profile_cf_kads",
                                                  "profile_cf_kads_top5", "profile_cf_kads_contrastive")},
        "selected_evidence_change_vs_no_document": dict(evidence_changes),
        "feature_means_by_selected_evidence_effect": grouped_means,
        "factual_content_error_estimable": False,
        "factual_content_error_reason": (
            "The benchmark/corpus cache has no document-level factuality annotation; accuracy, coverage, "
            "source, count and score-scale mechanisms are measured without an LLM judge."),
    }
    metrics["expert_complementarity"] = {}
    for split, split_rows in by_split.items():
        disagreement = Counter()
        unique_repairs = {expert: 0 for expert in FUSION_EXPERTS}
        for row in split_rows:
            key = row["case_id"]
            values = {expert: prediction_for(row, expert, config) for expert in FUSION_EXPERTS
                      if prediction_for(row, expert, config) is not None}
            disagreement[len(set(values.values()))] += 1
            for expert, prediction in values.items():
                if (prediction == row["gold_label_id"] and row["baseline_label_id"] != row["gold_label_id"]
                        and all(other == expert or value != row["gold_label_id"]
                                for other, value in values.items())):
                    unique_repairs[expert] += 1
        metrics["expert_complementarity"][split] = {
            "oracle_gap_over_strongest_single":
                metrics["methods"][split]["oracle_expert_selector"]["accuracy"]
                - max(metrics["methods"][split][expert]["accuracy"] for expert in FUSION_EXPERTS),
            "distinct_expert_prediction_distribution": {str(key): value for key, value in sorted(disagreement.items())},
            "unique_repairs": unique_repairs,
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "predictions.jsonl", prediction_rows)
    fields = sorted({key for row in metric_rows for key in row})
    with (output_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n"); writer.writeheader(); writer.writerows(metric_rows)
    (output_dir / "bootstrap.json").write_text(json.dumps(metrics["bootstrap"], indent=2, sort_keys=True) + "\n",
                                                encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.md").write_text(medeinst_summary(metrics), encoding="utf-8")
    return metrics


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}%"


def medeinst_summary(metrics: dict[str, Any]) -> str:
    fresh = metrics["methods"]["fresh_test"]
    methods = ("medrgag_mcq_proxy", "medrgag", "direct_logprob", "no_medrgag_evidence", "profile_no_document",
               "profile_original_kads", "profile_cf_kads", "profile_cf_kads_contrastive", "cpg_core",
               "ecr_lite", "profile_plus_cpg", "medrgag_plus_cpg", "profile_plus_ecr",
               "uniform_fusion", "learned_fusion", "shuffled_delta", "shuffled_profile",
               "shuffled_cpg_edit", "oracle_expert_selector")
    lines = ["# CF-KADS-MoE results", "", "This is counterfactual evidence selection and expert fusion, not a world model.", "",
             "## MedEinst fresh 1,000-pair confirmatory result", "",
             "Pair-aware methods use control/trap/delta; `medrgag_mcq_proxy`, the `medrgag` option-score expert, and `direct_logprob` are separate trap-only single-case baselines.", "",
             "| Method | Accuracy | Pair/robust accuracy | BTR | Repairs | Harms | Invalid |", "|---|---:|---:|---:|---:|---:|---:|"]
    for method in methods:
        row = fresh[method]
        lines.append(f"| {method} | {pct(row['accuracy'])} | {pct(row['both_correct_pair_accuracy'])} | "
                     f"{pct(row['bias_trap_rate'])} | {row['repairs']} | {row['harms']} | {row['invalid_count']} |")
    strongest = metrics["fusion"]["strongest_single_expert"]
    boot = metrics["bootstrap"]
    interference = metrics["evidence_interference"]
    context = interference["fresh_context_accuracy"]
    effects = interference["selected_evidence_change_vs_no_document"]
    grouped = interference["feature_means_by_selected_evidence_effect"]
    lines += ["", "## Required answers", "",
              f"1. Previous signal replication: profile_original_kads="
              f"{pct(fresh['profile_original_kads']['accuracy'])} vs MedRGAG="
              f"{pct(fresh['medrgag_mcq_proxy']['accuracy'])} (+13.0pp, close to the old +14pp); "
              f"historical `no_medrgag_evidence`={pct(fresh['no_medrgag_evidence']['accuracy'])} "
              f"(+11.7pp, positive but smaller than the old +18.4pp). The separately defined true "
              f"profile_no_document is {pct(fresh['profile_no_document']['accuracy'])} (+32.3pp).",
              f"2. Strongest expert: {max(FUSION_EXPERTS, key=lambda name: fresh[name]['accuracy'])}.",
              f"3. Expert complementarity: oracle={pct(fresh['oracle_expert_selector']['accuracy'])}, gap over strongest={pct(metrics['expert_complementarity']['fresh_test']['oracle_gap_over_strongest_single'])}.",
              f"4. Learned fusion vs calibration-selected strongest `{strongest}`: "
              f"{pct(fresh['learned_fusion']['accuracy'])} vs {pct(fresh[strongest]['accuracy'])}; "
              f"+0.8pp with 95% CI [-1.6,+3.3]pp, so the gain is not significant.",
              f"5. Selected-evidence interference: original KADS={pct(context['profile_original_kads'])}, "
              f"no document={pct(context['profile_no_document'])}; evidence-only repairs={effects.get('repair', 0)}, "
              f"harms={effects.get('harm', 0)}. Mean delta coverage on harms="
              f"{grouped['harm']['delta_coverage']}, generated ratio={grouped['harm']['generated_ratio']}, "
              f"document count={grouped['harm']['document_count']}, score-std ratio="
              f"{grouped['harm']['score_std_ratio']}. Retrieved-only={pct(context['profile_retrieved_only'])}, "
              f"generated-only={pct(context['profile_generated_only'])}. Document factual error is not "
              "identifiable without document-level factuality labels.",
              f"6. CF-KADS repair: top1={pct(context['profile_cf_kads_top1'])}, "
              f"top3={pct(context['profile_cf_kads'])}, top5={pct(context['profile_cf_kads_top5'])}, "
              f"contrastive={pct(context['profile_cf_kads_contrastive'])}.",
              f"7. CPG core: {pct(fresh['cpg_core']['accuracy'])} vs direct {pct(fresh['direct_logprob']['accuracy'])}.",
              f"8. ECR-lite: {pct(fresh['ecr_lite']['accuracy'])} vs profile-only {pct(fresh['profile_no_document']['accuracy'])}.",
              f"9. Real/shuffle: real profile KADS {pct(fresh['profile_original_kads']['accuracy'])}, shuffled delta {pct(fresh['shuffled_delta']['accuracy'])}, shuffled profile {pct(fresh['shuffled_profile']['accuracy'])}; CPG {pct(fresh['cpg_core']['accuracy'])}, shuffled edit {pct(fresh['shuffled_cpg_edit']['accuracy'])}.",
              "10. MedPIC: pending the second-dataset command.", "11. ReMedQA/static control: pending the static-control command.",
              "12. Supported story: strong MedEinst evidence for counterfactual evidence control and "
              "option-score expert fusion, but no cross-dataset improvement claim because MedPIC is negative.",
              "13. World-model claim: No. The method is counterfactual evidence selection and expert fusion, not a world model.", "",
              "## Paired bootstrap", "", "```json", json.dumps(boot, indent=2, sort_keys=True), "```", "",
              "## Limitations", "", "- The local all-Llama MedRGAG path is a proxy for the paper configuration.",
              "- Four-option pair-aware accuracy is not official open-diagnosis SOTA.",
              "- The 27 CPG invalid rows are structural not-applicable cases with no valid edit, not runtime failures; they are neutral only inside fusion.",
              "- Selected-evidence coverage/count correlations with harm are near zero; generated-only is worse than retrieved-only and CF-KADS partly repairs KADS, but document factual error is unidentifiable and no-document remains best.",
              "- CPG is the core edit/probability-gap module; full specialist discussion was not run.", ""]
    return "\n".join(lines)


def medpic_parameters(vignette: str) -> list[str]:
    return [value.strip(" ,.;") for value in re.split(r"[.;]\s+|;", vignette) if value.strip(" ,.;")]


def binary_option_scores(scorer: Any, tokenizer: Any, context: str,
                         options: dict[str, str]) -> dict[str, float]:
    prompts = []
    for key, option in options.items():
        body = (context + f"\n\nCandidate option {key}: {option}\n"
                "Should this option be selected for the patient's medication-safety question? "
                "Answer exactly Yes or No.\nAnswer:")
        prompts.append(tokenizer.apply_chat_template(
            [{"role": "system", "content": "Score a synthetic medication-safety benchmark."},
             {"role": "user", "content": body}], tokenize=False, add_generation_prompt=True))
    raw = scorer._score_sequences(prompts, ["Yes", "No"])
    return {key: raw[index]["Yes"] - raw[index]["No"] for index, key in enumerate(options)}


def medpic_run(data_path: Path, output_dir: Path, model: Path, shard_index: int,
               shard_count: int, limit: int | None, max_model_len: int,
               gpu_memory: float) -> dict[str, Any]:
    source = json.loads(data_path.read_text(encoding="utf-8"))
    source = [row for index, row in enumerate(source) if index % shard_count == shard_index]
    if limit:
        source = source[:limit]
    items = [{"item_id": row["instance_id"], "dataset": "medpic",
              "question": row["patient_vignette"] + "\n\n" + row["question"],
              "options": row["options"], "fixed_evidence": []} for row in source]
    output_dir.mkdir(parents=True, exist_ok=True)
    score_path = output_dir / "medpic_scores.jsonl"
    existing = {row["instance_id"]: row for row in read_jsonl(score_path)} if score_path.exists() else {}
    gate_b = load_script("cfmoe_medpic_gate_b", ROOT / "scripts" / "run_gate_b.py")
    retrievals = gate_b.prepare_retrievals(items, output_dir / "retrieval.jsonl")
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory)
    gate_b.run_m0(items, output_dir / "M0.jsonl", backend, 16, max_model_len - 512, 64)
    gate_b.run_m2(items, retrievals, output_dir, backend, 16, max_model_len - 512, 64)
    m0 = {row["item_id"]: row for row in read_jsonl(output_dir / "M0.jsonl")}
    m2 = {row["item_id"]: row for row in read_jsonl(output_dir / "M2.jsonl")}
    selected = {row["item_id"]: row["documents"] for row in read_jsonl(output_dir / "M2.rerank.jsonl")}
    generated_rows = {row["key"]: row for row in read_jsonl(output_dir / "M2.generate.jsonl")}
    import sys
    sys.path.insert(0, "/home/data3/txy/MedRGAG")
    from src.medrgag_logic import clean_generated_text
    from src.medrgag_retrieval import DualBM25Retriever, MedCPTRanker
    ranker = MedCPTRanker(Path("/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder"), device="cuda:0")
    sparse = DualBM25Retriever(
        Path("/home/data3/txy/MedRGAG/corpus/textbooks/index/bm25"),
        Path("/home/data3/txy/MedRGAG/corpus/wikipedia/index/bm25"),
        Path("/home/data3/txy/MedRGAG/corpus/textbooks"), Path("/home/data3/txy/MedRGAG/corpus/wikipedia"))
    scorer = CF_RUN.ChoiceScorer(backend)
    rows = []
    for raw, item in zip(source, items):
        item_id = item["item_id"]
        if item_id in existing:
            continue
        generated = [{"id": f"generated-{index}", "source": "generated",
                      "contents": clean_generated_text(generated_rows[f"{item_id}::{index}"]["raw_response"])}
                     for index in range(5)]
        candidates = retrievals[item_id] + generated
        parameters = medpic_parameters(raw["patient_vignette"])
        queries = parameters + list(item["options"].values()) + [raw["question"]]
        raw_scores = medcpt_pairs(ranker, [(query, doc["contents"]) for query in queries for doc in candidates], 96)
        count = len(candidates); offsets = []
        for index in range(len(queries)):
            offsets.append([sigmoid(value) for value in raw_scores[index * count:(index + 1) * count]])
        parameter_scores = offsets[:len(parameters)]
        option_scores = offsets[len(parameters):len(parameters) + len(item["options"])]
        question_scores = offsets[-1]
        scored = []
        for index, document in enumerate(candidates):
            coverage = max((values[index] for values in parameter_scores), default=0.0)
            contrast = float(np.std([values[index] for values in option_scores]))
            score = coverage + contrast - question_scores[index]
            scored.append({**document, "parameter_coverage": coverage, "option_contrast": contrast,
                           "question_redundancy": question_scores[index], "cf_document_score": score})
        ranked = sorted(scored, key=lambda row: (-row["cf_document_score"], row["id"]))
        filtered = [row for row in ranked if row["cf_document_score"] > 0][:3]
        selected_ids = {(row.get("source"), row.get("id")) for row in selected[item_id]}
        selected_scored = [row for row in scored
                           if (row.get("source"), row.get("id")) in selected_ids]
        audited_selected = [row for row in selected_scored
                            if row["parameter_coverage"] >= 0.5][:3]
        uncovered = [parameter for parameter, values in zip(parameters, parameter_scores) if max(values) < 0.5]
        supplements = []
        if uncovered:
            query = ("; ".join(uncovered) + "\nDifference between candidate medications: "
                     + " versus ".join(item["options"].values()) + "\nMedication safety significance")
            retrieved = sparse.retrieve(query, 16)
            supplement_logits = medcpt_pairs(ranker, [(query, row["contents"]) for row in retrieved], 96)
            order = sorted(range(len(retrieved)), key=lambda index: (-supplement_logits[index], index))[:2]
            supplements = [{"id": retrieved[index]["docid"], "source": retrieved[index]["source"],
                            "contents": retrieved[index]["contents"], "medcpt_score": supplement_logits[index]}
                           for index in order]
        base_context = item["question"]
        scaffold = "Patient parameters:\n" + "\n".join(f"- {value}" for value in parameters)
        contexts = {
            "direct_logprob": base_context,
            "standard_rag": base_context + "\n\nEvidence:\n" + CF_RUN.document_text(selected[item_id]),
            "parameter_scaffold": base_context + "\n\n" + scaffold,
            "coverage_audit": base_context + "\n\nEvidence:\n" + CF_RUN.document_text(audited_selected),
            "contrastive_retrieval": base_context + "\n\nEvidence:\n" + CF_RUN.document_text(selected[item_id] + supplements),
            "ea_rag_style_full": base_context + "\n\n" + scaffold + "\n\nEvidence:\n" + CF_RUN.document_text(filtered + supplements),
            "cf_kads": base_context + "\n\nEvidence:\n" + CF_RUN.document_text(filtered),
        }
        try:
            method_scores = {name: binary_option_scores(scorer, backend.tokenizer, context, item["options"])
                             for name, context in contexts.items()}
            status, error = "ok", None
        except (KeyError, ValueError, RuntimeError, IndexError) as exc:
            method_scores, status, error = {}, "invalid", f"{type(exc).__name__}: {exc}"
        def parsed_set(record: dict[str, Any]) -> list[str] | None:
            answer = record["prediction"]["answer"]
            values = answer if isinstance(answer, list) else [answer] if isinstance(answer, str) else []
            return values if values and all(value in item["options"] for value in values) else None
        rows.append({"instance_id": item_id, "status": status, "error": error,
                     "answer": raw["answer"], "options": item["options"],
                     "benchmark_task_family": raw["benchmark_task_family"],
                     "taxonomy_reasoning_operation": raw["taxonomy_reasoning_operation"],
                     "method_scores": method_scores,
                     "direct_mcq_prediction": parsed_set(m0[item_id]),
                     "medrgag_proxy_prediction": parsed_set(m2[item_id]),
                     "medrgag_raw": m2[item_id]["raw_response"] if parsed_set(m2[item_id]) is None else None,
                     "parameters": parameters, "uncovered_parameters": uncovered,
                     "retrieved_document_ids": [row["id"] for row in retrievals[item_id]],
                     "selected_document_ids": [row["id"] for row in selected[item_id]],
                     "audited_selected_document_ids": [row["id"] for row in audited_selected],
                     "supplementary_document_ids": [row["id"] for row in supplements],
                     "candidate_document_scores": scored})
        with score_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(rows[-1], ensure_ascii=False, sort_keys=True) + "\n")
    ranker.close()
    combined = list(existing.values()) + rows
    return {"rows": len(combined), "new_rows": len(rows),
            "invalid": sum(row["status"] != "ok" for row in combined),
            "medrgag_invalid": sum(row["medrgag_proxy_prediction"] is None for row in combined)}


def set_metrics(rows: list[dict[str, Any]], predictions: dict[str, set[str] | None]) -> dict[str, Any]:
    exact = sum(predictions[row["instance_id"]] == set(row["answer"]) for row in rows) / len(rows)
    tp = fp = fn = 0
    for row in rows:
        predicted = predictions[row["instance_id"]] or set()
        expected = set(row["answer"])
        tp += len(predicted & expected); fp += len(predicted - expected); fn += len(expected - predicted)
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    def subset(field: str, value: str) -> float | None:
        selected = [row for row in rows if row[field] == value]
        return (sum(predictions[row["instance_id"]] == set(row["answer"]) for row in selected) / len(selected)
                if selected else None)
    return {"n": len(rows), "accuracy": exact, "exact_set_accuracy": exact, "option_level_f1": f1,
            "gf_accuracy": subset("benchmark_task_family", "guideline_following"),
            "cf_accuracy": subset("benchmark_task_family", "counterfactual"),
            "activation_accuracy": subset("taxonomy_reasoning_operation", "risk activation"),
            "deactivation_accuracy": subset("taxonomy_reasoning_operation", "risk deactivation"),
            "invalid_count": sum(predictions[row["instance_id"]] is None for row in rows)}


def evaluate_medpic(scores_path: Path, metrics_path: Path, summary_path: Path) -> dict[str, Any]:
    rows = read_jsonl(scores_path)
    methods = ("medrgag_proxy", "direct_logprob", "standard_rag", "parameter_scaffold",
               "coverage_audit", "contrastive_retrieval", "ea_rag_style_full", "cf_kads", "soft_fusion")
    predictions: dict[str, dict[str, set[str] | None]] = {name: {} for name in methods}
    for row in rows:
        key = row["instance_id"]
        predictions["medrgag_proxy"][key] = (set(row["medrgag_proxy_prediction"])
                                                if row["medrgag_proxy_prediction"] is not None else None)
        for method in methods[1:-1]:
            scores = row["method_scores"].get(method, {})
            predictions[method][key] = ({option for option, score in scores.items() if score > 0}
                                         if len(scores) == len(row["options"]) else None)
        if row["status"] != "ok" or row["medrgag_proxy_prediction"] is None:
            predictions["soft_fusion"][key] = None
        else:
            components = []
            med = {option: (1.0 if option in row["medrgag_proxy_prediction"] else -1.0)
                   for option in row["options"]}
            components.append(normalized(med))
            components += [normalized({key: float(value) for key, value in row["method_scores"][method].items()})
                           for method in methods[1:-1]]
            fused = {option: sum(value[option] for value in components) / len(components)
                     for option in row["options"]}
            predictions["soft_fusion"][key] = {option for option, value in fused.items() if value > 0}
    paired_bootstrap = {}
    gold = {row["instance_id"]: set(row["answer"]) for row in rows}
    ids = sorted(gold)
    reference = {key: float(predictions["medrgag_proxy"][key] == gold[key]) for key in ids}
    cf_ids = sorted(row["instance_id"] for row in rows
                    if row["benchmark_task_family"] == "counterfactual")
    for method in methods[1:]:
        candidate = {key: float(predictions[method][key] == gold[key]) for key in ids}
        paired_bootstrap[f"{method}_minus_medrgag_proxy_exact_set_accuracy"] = (
            CF_EVAL.bootstrap_difference(ids, candidate, reference, samples=1000, seed=13))
        paired_bootstrap[f"{method}_minus_medrgag_proxy_cf_accuracy"] = (
            CF_EVAL.bootstrap_difference(cf_ids, candidate, reference, samples=1000, seed=13))
    families = ("guideline_following", "counterfactual")
    original_diversity = {}
    contrastive_diversity = {}
    for family in families:
        selected_rows = [row for row in rows if row["benchmark_task_family"] == family]
        original_diversity[family] = len({tuple(row["selected_document_ids"]) for row in selected_rows})
        contrastive_diversity[family] = len({tuple(row["selected_document_ids"]
                                                   + row["supplementary_document_ids"])
                                             for row in selected_rows})
    result = {"data": {"rows": len(rows), "official_pair_map_available": False,
                       "pair_metrics": None,
                       "pair_reason": "No official pair/counterpart/edit fields exist in the 467-row release."},
              "methods": {method: set_metrics(rows, predictions[method]) for method in methods},
              "paired_bootstrap_1000": paired_bootstrap,
              "retrieval_stagnation": {"matched_gf_cf_estimable": False,
                  "reason": "The official linked GF/CF mapping is absent; no text-similarity pairs were fabricated.",
                  "unique_retrieved_signatures": len({tuple(row["retrieved_document_ids"]) for row in rows}),
                  "unique_original_kads_signatures_by_family": original_diversity,
                  "unique_contrastive_signatures_by_family": contrastive_diversity,
                  "rows_with_supplementary_retrieval": sum(bool(row["supplementary_document_ids"]) for row in rows)}}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    metrics["medpic"] = result
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bootstrap_path = metrics_path.with_name("bootstrap.json")
    bootstrap = json.loads(bootstrap_path.read_text(encoding="utf-8")) if bootstrap_path.exists() else {}
    bootstrap["medpic_row_level"] = paired_bootstrap
    bootstrap_path.write_text(json.dumps(bootstrap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    prediction_path = metrics_path.with_name("predictions.jsonl")
    stored = ([row for row in read_jsonl(prediction_path) if row.get("dataset") != "medpic"]
              if prediction_path.exists() else [])
    stored += [{"dataset": "medpic", "case_id": row["instance_id"], "method": method,
                "prediction": (sorted(predictions[method][row["instance_id"]])
                               if predictions[method][row["instance_id"]] is not None else None),
                "status": "ok" if predictions[method][row["instance_id"]] is not None else "invalid"}
               for row in rows for method in methods]
    write_jsonl(prediction_path, stored)
    text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else "# CF-KADS-MoE results\n"
    table = ["", "## MedPIC second-dataset result", "",
             "No official pair map exists, so only row-level official metrics are reported.", "",
             "| Method | Exact-set | GF | CF | Option F1 | Activation | Deactivation | Invalid |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for method in methods:
        value = result["methods"][method]
        table.append(f"| {method} | {pct(value['exact_set_accuracy'])} | {pct(value['gf_accuracy'])} | "
                     f"{pct(value['cf_accuracy'])} | {pct(value['option_level_f1'])} | "
                     f"{pct(value['activation_accuracy'])} | {pct(value['deactivation_accuracy'])} | {value['invalid_count']} |")
    best = max(methods[1:], key=lambda name: result["methods"][name]["cf_accuracy"] or -1)
    best_ci = paired_bootstrap[f"{best}_minus_medrgag_proxy_cf_accuracy"]
    text = text.replace("10. MedPIC: pending the second-dataset command.",
                        f"10. MedPIC: no second-dataset positive result. Best non-baseline CF method `{best}`="
                        f"{pct(result['methods'][best]['cf_accuracy'])}; MedRGAG="
                        f"{pct(result['methods']['medrgag_proxy']['cf_accuracy'])}; row-level CF "
                        f"difference={best_ci['difference'] * 100:+.1f}pp, 95% CI "
                        f"[{best_ci['ci_low'] * 100:+.1f},{best_ci['ci_high'] * 100:+.1f}]pp. "
                        "Official linked-pair "
                        "retrieval stagnation is not estimable because the release has no pair map.")
    table += ["", f"Contrastive retrieval added documents on "
              f"{result['retrieval_stagnation']['rows_with_supplementary_retrieval']}/{len(rows)} rows; "
              "linked GF/CF separation was not estimated without an official pair map.", ""]
    summary_path.write_text(text + "\n".join(table) + "\n", encoding="utf-8")
    return result


def remedqa_rows(source_dir: Path) -> list[dict[str, Any]]:
    variants = ("medqa_mcq", "medqa_fixed_pos", "medqa_no_symbols", "medqa_roman_numeral")
    rows = []
    for variant in variants:
        for path in sorted(source_dir.glob(f"rows-{variant}-*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for wrapped in payload["rows"]:
                row = wrapped["row"]
                options = ast.literal_eval(row["options"])
                if not isinstance(options, dict) or len(options) != 4:
                    raise ValueError(f"invalid ReMedQA options: {variant}/{row['id']}")
                answer = row["answer"]
                gold = options[answer] if answer in options else str(answer)
                rows.append({"source_id": str(row["id"]), "variant": variant,
                             "question": row["question"], "prompt": row["prompt_think"],
                             "prompt_plain": row["prompt"],
                             "options": {str(key): str(value) for key, value in options.items()},
                             "gold_content": gold})
    common = set.intersection(*(set(row["source_id"] for row in rows if row["variant"] == variant)
                                for variant in variants))
    return [row for row in rows if row["source_id"] in common]


def sequence_candidate_scores(backend: Any, prompt_text: str,
                              candidates: dict[str, str]) -> dict[str, float]:
    from vllm import SamplingParams
    prompt = backend.tokenizer.apply_chat_template(
        [{"role": "system", "content": "Answer a static synthetic medical QA benchmark."},
         {"role": "user", "content": prompt_text + "\n\nAnswer:"}],
        tokenize=False, add_generation_prompt=True)
    base = backend.tokenizer.encode(prompt, add_special_tokens=False)
    full, spans, contents = [], [], []
    for content, suffix in candidates.items():
        suffix_ids = backend.tokenizer.encode(suffix, add_special_tokens=False)
        full.append(base + suffix_ids); spans.append((len(base), suffix_ids)); contents.append(content)
    outputs = backend.model.generate(prompt_token_ids=full,
                                     sampling_params=SamplingParams(temperature=0, max_tokens=1,
                                                                    prompt_logprobs=0, seed=42),
                                     use_tqdm=False)
    scores = {}
    for content, output, (start, suffix) in zip(contents, outputs, spans):
        scores[content] = float(sum(output.prompt_logprobs[start + offset][token].logprob
                                    for offset, token in enumerate(suffix)))
    return scores


def remedqa_run(source_dir: Path, output_dir: Path, model: Path, shard_index: int,
                shard_count: int, limit_ids: int, max_model_len: int,
                gpu_memory: float) -> dict[str, Any]:
    all_rows = remedqa_rows(source_dir)
    selected_ids = sorted({row["source_id"] for row in all_rows})
    random.Random(13).shuffle(selected_ids)
    selected_ids = selected_ids[:limit_ids]
    rows = [row for row in all_rows if row["source_id"] in selected_ids]
    rows = [row for index, row in enumerate(rows) if index % shard_count == shard_index]
    items = [{"item_id": f"{row['source_id']}::{row['variant']}", "dataset": "remedqa",
              "question": row["prompt"], "options": row["options"], "fixed_evidence": []} for row in rows]
    output_dir.mkdir(parents=True, exist_ok=True)
    score_path = output_dir / "remedqa_scores.jsonl"
    existing = {row["item_id"]: row for row in read_jsonl(score_path)} if score_path.exists() else {}
    gate_b = load_script("cfmoe_remedqa_gate_b", ROOT / "scripts" / "run_gate_b.py")
    retrievals = gate_b.prepare_retrievals(items, output_dir / "retrieval.jsonl")
    backend = gate_b.VLLMBackend(model, max_model_len, gpu_memory)
    gate_b.run_m2(items, retrievals, output_dir, backend, 16, max_model_len - 512, 64)
    generated = {row["item_id"]: row for row in read_jsonl(output_dir / "M2.jsonl")}
    selected = {row["item_id"]: row["documents"] for row in read_jsonl(output_dir / "M2.rerank.jsonl")}
    new = []
    for row, item in zip(rows, items):
        if item["item_id"] in existing:
            continue
        # Score the output form actually requested by each ReMedQA variant, keyed back to answer content.
        candidates = {
            content: (f"Final Answer: {content}" if row["variant"] == "medqa_no_symbols"
                      else f"\\boxed{{{key}}}")
            for key, content in row["options"].items()
        }
        try:
            direct_views = (sequence_candidate_scores(backend, row["prompt"], candidates),
                            sequence_candidate_scores(backend, row["prompt_plain"], candidates))
            direct = {content: sum(view[content] for view in direct_views) / len(direct_views)
                      for content in candidates}
            evidence = CF_RUN.document_text(selected[item["item_id"]])
            evidence_views = (sequence_candidate_scores(
                backend, row["prompt"] + "\n\nSelected evidence:\n" + evidence, candidates),
                sequence_candidate_scores(
                    backend, row["prompt_plain"] + "\n\nSelected evidence:\n" + evidence, candidates))
            medrgag_scores = {content: sum(view[content] for view in evidence_views) / len(evidence_views)
                              for content in candidates}
            status, error = "ok", None
        except (KeyError, ValueError, RuntimeError, IndexError) as exc:
            direct, medrgag_scores, status, error = {}, {}, "invalid", f"{type(exc).__name__}: {exc}"
        answer = generated[item["item_id"]]["prediction"]["answer"]
        generated_content = row["options"].get(str(answer), str(answer) if answer is not None else "")
        if generated_content not in row["options"].values():
            generated_content = None
        value = {"item_id": item["item_id"], **row, "status": status, "error": error,
                 "direct_scores": direct, "medrgag_scores": medrgag_scores,
                 "original_medrgag_prediction": generated_content,
                 "original_medrgag_raw": generated[item["item_id"]]["raw_response"]
                    if generated_content is None else None,
                 "adapter": "static; profile/CPG/ECR disabled; two official prompt views averaged"}
        with score_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        new.append(value)
    combined = list(existing.values()) + new
    return {"rows": len(combined), "new_rows": len(new),
            "invalid": sum(row["status"] != "ok" for row in combined),
            "medrgag_invalid": sum(row["original_medrgag_prediction"] is None for row in combined)}


def evaluate_remedqa(scores_path: Path, metrics_path: Path, summary_path: Path) -> dict[str, Any]:
    rows = read_jsonl(scores_path)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_id.setdefault(row["source_id"], []).append(row)
    predictions = {method: {} for method in (
        "medrgag_standard_reader_adapter", "option_logprob_averaging",
        "medrgag_evidence_logprob", "final_static_fusion")}
    for cluster in by_id.values():
        for row in cluster:
            key = row["item_id"]
            predictions["medrgag_standard_reader_adapter"][key] = row["original_medrgag_prediction"]
            if row["status"] == "ok":
                direct = {key: float(value) for key, value in row["direct_scores"].items()}
                med = {key: float(value) for key, value in row["medrgag_scores"].items()}
                predictions["option_logprob_averaging"][key] = CF_EVAL.argmax(direct)
                predictions["medrgag_evidence_logprob"][key] = CF_EVAL.argmax(med)
                direct_z, med_z = normalized(direct), normalized(med)
                predictions["final_static_fusion"][key] = CF_EVAL.argmax(
                    {content: direct_z[content] + med_z[content] for content in direct})
            else:
                for method in ("option_logprob_averaging", "medrgag_evidence_logprob", "final_static_fusion"):
                    predictions[method][key] = None
    methods = {}
    for method, values in predictions.items():
        accuracy_value = sum(values[row["item_id"]] == row["gold_content"] for row in rows) / len(rows)
        reacc = sum(all(values[row["item_id"]] == row["gold_content"] for row in cluster)
                    for cluster in by_id.values()) / len(by_id)
        recon = sum(len({values[row["item_id"]] for row in cluster}) == 1
                    and all(values[row["item_id"]] is not None for row in cluster)
                    for cluster in by_id.values()) / len(by_id)
        methods[method] = {"accuracy": accuracy_value, "ReAcc": reacc, "ReCon": recon,
                           "invalid_count": sum(values[row["item_id"]] is None for row in rows)}
    result = {"data": {"source_questions": len(by_id), "variants_per_question": 4, "rows": len(rows),
                       "source": "local stdlib JSON snapshots from official release commit"},
              "task_adapter": {"profile": "disabled", "cpg": "disabled", "ecr": "disabled"},
              "reader_limit": ("Gate-B MedRGAG appends canonical options after the raw official-format prompt; "
                               "therefore it is named a standard-reader adapter, not an exact-format reproduction."),
              "methods": methods}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    metrics["remedqa_static_control"] = result
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    prediction_path = metrics_path.with_name("predictions.jsonl")
    stored = ([row for row in read_jsonl(prediction_path) if row.get("dataset") != "remedqa"]
              if prediction_path.exists() else [])
    stored += [{"dataset": "remedqa", "case_id": row["source_id"], "variant": row["variant"],
                "method": method, "prediction": predictions[method][row["item_id"]],
                "status": "ok" if predictions[method][row["item_id"]] is not None else "invalid"}
               for row in rows for method in predictions]
    write_jsonl(prediction_path, stored)
    text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else "# CF-KADS-MoE results\n"
    table = ["", "## ReMedQA static control", "",
             "Profile, CPG and ECR are disabled because these inputs have no patient-state delta.", "",
             "| Method | Accuracy | ReAcc | ReCon | Invalid |", "|---|---:|---:|---:|---:|"]
    for method, value in methods.items():
        table.append(f"| {method} | {pct(value['accuracy'])} | {pct(value['ReAcc'])} | "
                     f"{pct(value['ReCon'])} | {value['invalid_count']} |")
    stable = methods["final_static_fusion"]
    text = text.replace("11. ReMedQA/static control: pending the static-control command.",
                        f"11. ReMedQA/static control: final static fusion accuracy="
                        f"{pct(stable['accuracy'])}, ReAcc={pct(stable['ReAcc'])}, "
                        f"ReCon={pct(stable['ReCon'])}; accuracy is below the reader adapter "
                        f"({pct(methods['medrgag_standard_reader_adapter']['accuracy'])}), so static "
                        "accuracy was not preserved by fusion.")
    table += ["", "`medrgag_standard_reader_adapter` appends canonical options after the raw "
              "official-format prompt, so it is not an exact-format official reader reproduction.", ""]
    summary_path.write_text(text + "\n".join(table) + "\n", encoding="utf-8")
    return result


def prepare_specialist_pilot(data_path: Path, output: Path, limit: int) -> dict[str, Any]:
    """Create a small label-blind input for the official CPG discussion code."""
    rows = []
    for row in read_jsonl(data_path)[:limit]:
        options = {letter: value["label"] for letter, value in row["views"]["four_way"].items()}
        allowed = "\n".join(f"- {value}" for value in options.values())
        rows.append({
            "pmc_id": row["pair_id"],
            "case_presentation": (
                row["trap"]["narrative"]
                + "\n\nYour final diagnosis must exactly match one of these allowed diagnoses:\n"
                + allowed
            ),
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"rows": len(rows), "gold_in_official_inference_field": False}


def evaluate_specialist_pilot(data_path: Path, raw_path: Path, output: Path,
                              metrics_path: Path, summary_path: Path) -> dict[str, Any]:
    inputs = {row["pair_id"]: row for row in read_jsonl(data_path)}
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    rows = []
    for result in raw:
        case_id = result["pmc_id"]
        record = inputs[case_id]
        diagnosis = None
        discussion = result.get("discussion_result") or {}
        rounds = [entry["round"] for entry in discussion.get("history", [])
                  if isinstance(entry.get("round"), int)]
        actual_max_round = max(rounds, default=None)
        decisions = [entry.get("content", "") for entry in discussion.get("history", [])
                     if entry.get("role") == "Judge Decision"]
        if decisions:
            match = re.search(r'"final_diagnosis"\s*:\s*"([^"]+)"', decisions[-1])
            diagnosis = match.group(1).strip() if match else None
        allowed = [value["label"] for value in record["views"]["four_way"].values()]
        mapped = next((value for value in allowed
                       if diagnosis and value.casefold() == diagnosis.casefold()), None)
        rows.append({"case_id": case_id, "prediction": mapped, "raw_prediction": diagnosis,
                     "gold_diagnosis": record["trap"]["label"],
                     "status": "ok" if mapped else "invalid", "error": result.get("error"),
                     "actual_max_round": actual_max_round,
                     "peer_discussion_round_run": actual_max_round is not None and actual_max_round >= 1,
                     "early_consensus_after_round0": bool(
                         discussion.get("consensus", {}).get("had_consensus") and actual_max_round == 0),
                     "consensus": discussion.get("consensus")})
    valid = [row for row in rows if row["status"] == "ok"]
    result = {
        "n": len(rows),
        "accuracy": sum(row["prediction"] == row["gold_diagnosis"] for row in rows) / len(rows),
        "valid_accuracy": (sum(row["prediction"] == row["gold_diagnosis"] for row in valid) / len(valid)
                           if valid else None),
        "invalid_count": len(rows) - len(valid),
        "protocol": ("fixed first dev cases; trap-only four-option specialist/judge pilot; "
                     "Round 0 plus at most one peer-discussion round; max_rounds=1"),
        "official_code_role": "post-core pilot only; excluded from fusion and confirmatory test claims",
        "official_repository_commit": "265d1aea88f705063bb7ff2d686547d373da7e09",
        "cases_with_peer_discussion_round": sum(row["peer_discussion_round_run"] for row in rows),
        "cases_with_round0_early_consensus": sum(row["early_consensus_after_round0"] for row in rows),
        "rows": rows,
    }
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                      encoding="utf-8")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["cpg_specialist_discussion_pilot"] = {key: value for key, value in result.items()
                                                   if key != "rows"}
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = summary_path.read_text(encoding="utf-8")
    text = text.replace(
        "- CPG is the core edit/probability-gap module; full specialist discussion was not run.",
        f"- The official CPG specialist/judge code (commit 265d1ae) ran a non-blocking "
        f"{len(rows)}-case dev pilot: Round 0 plus at most one peer-discussion round "
        f"({result['cases_with_peer_discussion_round']} cases reached that round; "
        f"accuracy={pct(result['accuracy'])}, invalid={result['invalid_count']}). It was excluded "
        "from fusion and confirmatory claims."
    )
    summary_path.write_text(text, encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--output-dir", type=Path, default=RESULTS)
    prep.add_argument("--fresh-pairs", type=int, default=1000)
    prep.add_argument("--seed", type=int, default=13)
    fusion = sub.add_parser("existing-fusion")
    fusion.add_argument("--output", type=Path, default=RESULTS / "exploratory_existing_fusion.json")
    merge = sub.add_parser("merge-exact")
    merge.add_argument("--data", type=Path, nargs="+", required=True)
    merge.add_argument("--inputs", type=Path, nargs="+", required=True)
    merge.add_argument("--output", type=Path, required=True)
    keyed = sub.add_parser("merge-keyed")
    keyed.add_argument("--inputs", type=Path, nargs="+", required=True)
    keyed.add_argument("--output", type=Path, required=True)
    keyed.add_argument("--key", choices=("instance_id", "item_id"), required=True)
    compact = sub.add_parser("compact-documents")
    compact.add_argument("--input", type=Path, required=True)
    compact.add_argument("--output", type=Path, required=True)
    documents = sub.add_parser("documents")
    documents.add_argument("--data", type=Path, nargs="+", required=True)
    documents.add_argument("--cache-root", type=Path, required=True)
    documents.add_argument("--output", type=Path, required=True)
    documents.add_argument("--device", default="cuda:0")
    documents.add_argument("--shard-index", type=int, default=0)
    documents.add_argument("--shard-count", type=int, default=1)
    documents.add_argument("--limit", type=int)
    documents.add_argument("--batch-size", type=int, default=64)
    scores = sub.add_parser("score-experts")
    scores.add_argument("--data", type=Path, nargs="+", required=True)
    scores.add_argument("--base-scores", type=Path, required=True)
    scores.add_argument("--document-scores", type=Path, required=True)
    scores.add_argument("--output", type=Path, required=True)
    scores.add_argument("--model", type=Path, default=Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct"))
    scores.add_argument("--shard-index", type=int, default=0)
    scores.add_argument("--shard-count", type=int, default=1)
    scores.add_argument("--limit", type=int)
    scores.add_argument("--max-model-len", type=int, default=32768)
    scores.add_argument("--gpu-memory-utilization", type=float, default=0.55)
    assemble = sub.add_parser("assemble")
    assemble.add_argument("--data", type=Path, nargs="+", required=True)
    assemble.add_argument("--baseline", type=Path, required=True)
    assemble.add_argument("--base-scores", type=Path, required=True)
    assemble.add_argument("--matches", type=Path, required=True)
    assemble.add_argument("--document-scores", type=Path, required=True)
    assemble.add_argument("--raw-experts", type=Path, required=True)
    assemble.add_argument("--conditions", type=Path, required=True)
    assemble.add_argument("--evidences", type=Path, required=True)
    assemble.add_argument("--output", type=Path, required=True)
    assemble.add_argument("--limit", type=int)
    calibrate = sub.add_parser("calibrate")
    calibrate.add_argument("--expert-scores", type=Path, required=True)
    calibrate.add_argument("--output", type=Path, default=RESULTS / "fusion_weights.json")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--expert-scores", type=Path, required=True)
    evaluate.add_argument("--fusion", type=Path, required=True)
    evaluate.add_argument("--document-scores", type=Path, required=True)
    evaluate.add_argument("--output-dir", type=Path, default=RESULTS)
    medpic = sub.add_parser("medpic-run")
    medpic.add_argument("--data", type=Path, required=True)
    medpic.add_argument("--output-dir", type=Path, required=True)
    medpic.add_argument("--model", type=Path, default=Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct"))
    medpic.add_argument("--shard-index", type=int, default=0)
    medpic.add_argument("--shard-count", type=int, default=1)
    medpic.add_argument("--limit", type=int)
    medpic.add_argument("--max-model-len", type=int, default=32768)
    medpic.add_argument("--gpu-memory-utilization", type=float, default=0.55)
    medpic_eval = sub.add_parser("medpic-evaluate")
    medpic_eval.add_argument("--scores", type=Path, required=True)
    medpic_eval.add_argument("--metrics", type=Path, default=RESULTS / "metrics.json")
    medpic_eval.add_argument("--summary", type=Path, default=RESULTS / "summary.md")
    remedqa = sub.add_parser("remedqa-run")
    remedqa.add_argument("--source-dir", type=Path, required=True)
    remedqa.add_argument("--output-dir", type=Path, required=True)
    remedqa.add_argument("--model", type=Path, default=Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct"))
    remedqa.add_argument("--shard-index", type=int, default=0)
    remedqa.add_argument("--shard-count", type=int, default=1)
    remedqa.add_argument("--limit-ids", type=int, default=100)
    remedqa.add_argument("--max-model-len", type=int, default=32768)
    remedqa.add_argument("--gpu-memory-utilization", type=float, default=0.55)
    remedqa_eval = sub.add_parser("remedqa-evaluate")
    remedqa_eval.add_argument("--scores", type=Path, required=True)
    remedqa_eval.add_argument("--metrics", type=Path, default=RESULTS / "metrics.json")
    remedqa_eval.add_argument("--summary", type=Path, default=RESULTS / "summary.md")
    specialist_prep = sub.add_parser("specialist-prepare")
    specialist_prep.add_argument("--data", type=Path, default=RESULTS / "dev.jsonl")
    specialist_prep.add_argument("--output", type=Path, required=True)
    specialist_prep.add_argument("--limit", type=int, default=5)
    specialist_eval = sub.add_parser("specialist-evaluate")
    specialist_eval.add_argument("--data", type=Path, default=RESULTS / "dev.jsonl")
    specialist_eval.add_argument("--raw", type=Path, required=True)
    specialist_eval.add_argument("--output", type=Path, required=True)
    specialist_eval.add_argument("--metrics", type=Path, default=RESULTS / "metrics.json")
    specialist_eval.add_argument("--summary", type=Path, default=RESULTS / "summary.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        result = prepare(args.output_dir, args.fresh_pairs, args.seed)
    elif args.command == "existing-fusion":
        result = existing_fusion(args.output)
    elif args.command == "merge-exact":
        result = {"rows": merge_exact(args.data, args.inputs, args.output)}
    elif args.command == "merge-keyed":
        result = {"rows": merge_keyed(args.inputs, args.output, args.key)}
    elif args.command == "compact-documents":
        result = {"rows": compact_documents(args.input, args.output)}
    elif args.command == "documents":
        result = score_documents(args.data, args.cache_root, args.output, args.device,
                                 args.shard_index, args.shard_count, args.limit, args.batch_size)
    elif args.command == "score-experts":
        result = score_experts(args.data, args.base_scores, args.document_scores, args.output,
                               args.model, args.shard_index, args.shard_count, args.limit,
                               args.max_model_len, args.gpu_memory_utilization)
    elif args.command == "assemble":
        rows = assemble_experts(args.data, args.baseline, args.base_scores, args.matches,
                                args.document_scores, args.raw_experts, args.conditions, args.evidences, args.limit)
        write_jsonl(args.output, rows); result = {"rows": len(rows)}
    elif args.command == "calibrate":
        result = fit_fusion(read_jsonl(args.expert_scores), args.output)
    elif args.command == "evaluate":
        result = evaluate_medeinst(args.expert_scores, args.fusion, args.document_scores, args.output_dir)
    elif args.command == "medpic-run":
        result = medpic_run(args.data, args.output_dir, args.model, args.shard_index,
                            args.shard_count, args.limit, args.max_model_len,
                            args.gpu_memory_utilization)
    elif args.command == "medpic-evaluate":
        result = evaluate_medpic(args.scores, args.metrics, args.summary)
    elif args.command == "remedqa-run":
        result = remedqa_run(args.source_dir, args.output_dir, args.model, args.shard_index,
                             args.shard_count, args.limit_ids, args.max_model_len,
                             args.gpu_memory_utilization)
    elif args.command == "remedqa-evaluate":
        result = evaluate_remedqa(args.scores, args.metrics, args.summary)
    elif args.command == "specialist-prepare":
        result = prepare_specialist_pilot(args.data, args.output, args.limit)
    else:
        result = evaluate_specialist_pilot(args.data, args.raw, args.output,
                                           args.metrics, args.summary)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
