#!/usr/bin/env python3
"""Prepare and run the minimal DeltaRev-MedRGAG MedEinst pilot."""

from __future__ import annotations

import argparse
import copy
import difflib
import importlib.util
import json
import random
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct")
UNAVAILABLE = {
    "medpic_official_linked_pairs": "unavailable: local official pair map is absent",
    "nice": "unavailable: excluded by the frozen experiment boundary",
    "without_nice": "NA: NICE is unavailable, so this is identical to the main condition",
    "gold_delta_diagnostic": "unavailable: MedEinst has no official edit metadata",
    "source_rule_upper_bound": "unavailable: MedEinst has no official decisive source span",
    "retrieval_reference_metrics": "unavailable: no official decisive evidence reference",
}
METHODS = (
    "direct", "medrgag_proxy", "decomposition_only",
    "direct_counterfactual_prompt", "direct_answer_revision",
    "standard_question_retrieval", "candidate_specific_retrieval",
    "ea_rag_style_retrieval", "delta_only_retrieval",
    "triangular_decision_change_retrieval", "always_preserve", "always_revise",
    "llm_verifier_without_evidence", "evidence_verifier_with_standard_retrieval",
    "evidence_verifier_with_ea_rag_retrieval", "full_deltarev", "without_delta",
    "without_baseline_answer_in_query", "refute_only_retrieval",
    "without_preserve_evidence", "without_alternative_support_requirement",
    "without_entailment_check", "without_patient_applicability_check",
    "without_nice", "kgcc_generated_docs_as_decisive_evidence",
    "shuffled_delta", "shuffled_rule_evidence",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def append_rows(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()


def append_once(path: Path, key: tuple[Any, ...], row: dict[str, Any], fields: tuple[str, ...]) -> None:
    if path.exists() and any(tuple(value.get(field) for field in fields) == key for value in read_jsonl(path)):
        return
    append_rows(path, [row])


def _load_script(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_answer(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("answer", value.get("open_answer", ""))
    if isinstance(value, list):
        value = value[0] if len(value) == 1 else " | ".join(map(str, value))
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.strip().casefold().split()).rstrip(" .,:;!?")


def prepare_pilot(raw_path: Path, inference_path: Path, gold_path: Path,
                  exclude_gold: Path | None = None, seed: int = 13) -> dict[str, int]:
    rows = read_jsonl(raw_path)
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        if row.get("case_type") not in {"control", "trap"}:
            continue
        grouped.setdefault(str(row["case_id"]), {})[str(row["case_type"])] = row
    complete = {key: value for key, value in grouped.items() if set(value) == {"control", "trap"}}
    excluded = set()
    if exclude_gold and exclude_gold.exists():
        excluded = {
            str(row["pair_id"])
            for row in read_jsonl(exclude_gold)
            if row.get("dataset") == "medeinst" and row.get("pair_id")
        }
    complete = {key: value for key, value in complete.items() if key not in excluded}
    families: dict[tuple[str, str], list[str]] = {}
    for case_id, pair in complete.items():
        diagnoses = tuple(sorted((normalize_answer(pair["control"]["ground_truth"]),
                                  normalize_answer(pair["trap"]["ground_truth"]))))
        families.setdefault(diagnoses, []).append(case_id)
    eligible = [family for family, case_ids in families.items() if len(case_ids) >= 2]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    if len(eligible) < 21:
        raise ValueError(f"pilot needs at least 21 two-pair families; found {len(eligible)}")
    dev_families, test_families = eligible[:20], eligible[20:]
    selected: list[tuple[tuple[str, str], str, int, str]] = []
    for family_index, family in enumerate(dev_families):
        case_ids = sorted(families[family]); rng.shuffle(case_ids)
        selected.extend((family, case_id, family_index, "dev") for case_id in case_ids[:2])
    test_pools = {family: sorted(families[family]) for family in test_families}
    for pool in test_pools.values():
        rng.shuffle(pool)
    round_index = 0
    while sum(split == "test" for _, _, _, split in selected) < 160:
        progressed = False
        for family_index, family in enumerate(test_families, start=20):
            pool = test_pools[family]
            if round_index < len(pool):
                selected.append((family, pool[round_index], family_index, "test")); progressed = True
                if sum(split == "test" for _, _, _, split in selected) == 160:
                    break
        if not progressed:
            raise ValueError("remaining test families contain fewer than 160 pairs")
        round_index += 1
    inference, gold = [], []
    within_counts: dict[tuple[str, tuple[str, str]], int] = {}
    for family, case_id, family_index, split in selected:
        within_index = within_counts.get((split, family), 0)
        within_counts[(split, family)] = within_index + 1
        pair = complete[case_id]
        opaque = f"medeinst-{split}-{family_index:03d}-{within_index}"
        def visible(member: dict[str, Any], role: str) -> dict[str, Any]:
            return {
                "member_id": f"{opaque}-{role}", "role": role,
                "age": member.get("age"), "sex": member.get("sex"),
                "text": member["narrative"],
            }
        inference.append({
            "pair_id": opaque, "dataset": "medeinst", "split": split,
            "original_case": visible(pair["control"], "control"),
            "counterfactual_case": visible(pair["trap"], "trap"),
            "target_question": pair["trap"]["narrative"], "target_options": {},
            "task_type": "diagnosis_update",
        })
        gold.append({
            "pair_id": opaque, "source_case_id": case_id, "dataset": "medeinst",
            "split": split, "family": list(family),
            "control_answer": pair["control"]["ground_truth"],
            "trap_answer": pair["trap"]["ground_truth"],
        })
    if len(inference) != 200 or len({row["source_case_id"] for row in gold}) != 200:
        raise AssertionError("DeltaRev selection must contain 200 unique source pairs")
    inference_path.parent.mkdir(parents=True, exist_ok=True)
    inference_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in inference), encoding="utf-8")
    gold_path.parent.mkdir(parents=True, exist_ok=True)
    gold_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in gold), encoding="utf-8")
    return {"pairs": len(inference), "dev_pairs": 40, "test_pairs": 160,
            "medpic_official_pairs": 0}


def member_items(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for pair in pairs:
        for name in ("original_case", "counterfactual_case"):
            case = pair[name]
            items.append({"item_id": case["member_id"], "dataset": "medeinst",
                          "question": case["text"], "options": {}, "fixed_evidence": [],
                          "time_series": [], "task_family": "diagnosis_cf"})
    return items


def run_baseline(pairs: list[dict[str, Any]], output_dir: Path, output_path: Path,
                 backend: Any, batch_size: int = 16, max_input: int = 32256,
                 max_new: int = 512, retriever: Any | None = None,
                 ranker: Any | None = None) -> int:
    """Run the unchanged Gate-B M2 implementation for both pair members."""
    gate_b = _load_script("deltarev_gate_b", ROOT / "scripts" / "run_gate_b.py")
    items = member_items(pairs)
    retrievals = gate_b.prepare_retrievals(items, output_dir / "retrieval.jsonl", retriever)
    gate_b.run_m2(items, retrievals, output_dir, backend, batch_size, max_input, max_new, ranker)
    answers = {row["item_id"]: row for row in gate_b.read_jsonl(output_dir / "M2.jsonl")}
    selected = {row["item_id"]: row["documents"] for row in gate_b.read_jsonl(output_dir / "M2.rerank.jsonl")}
    generated_rows = gate_b.read_jsonl(output_dir / "M2.generate.jsonl")
    import sys
    sys.path.insert(0, str(gate_b.MEDRGAG))
    from src.medrgag_logic import clean_generated_text
    generated: dict[str, list[dict[str, Any]]] = {}
    for row in generated_rows:
        generated.setdefault(row["item_id"], []).append({
            "id": "generated-" + row["key"].rsplit("::", 1)[-1], "source": "generated",
            "contents": clean_generated_text(row["raw_response"]),
        })
    done = {row["pair_id"] for row in read_jsonl(output_path)} if output_path.exists() else set()
    new_rows = []
    for pair in pairs:
        if pair["pair_id"] in done:
            continue
        members = {}
        for key in ("original_case", "counterfactual_case"):
            member_id = pair[key]["member_id"]
            answer = answers[member_id]["prediction"]["answer"]
            if not normalize_answer(answer):
                raise ValueError(f"M2 baseline answer contract failure: {member_id}")
            members[pair[key]["role"]] = {
                "member_id": member_id,
                "baseline_answer": copy.deepcopy(answer),
                "retrieved_documents": copy.deepcopy(retrievals[member_id]),
                "generated_documents": copy.deepcopy(generated.get(member_id, [])),
                "selected_documents": copy.deepcopy(selected[member_id]),
                "reader_record": copy.deepcopy(answers[member_id]),
            }
        new_rows.append({"pair_id": pair["pair_id"], "dataset": "medeinst",
                         "split": pair["split"], "members": members})
    append_rows(output_path, new_rows)
    return len(new_rows)


def deterministic_delta(original: str, target: str) -> dict[str, Any]:
    old_lines = [" ".join(line.split()) for line in original.splitlines() if line.strip()]
    new_lines = [" ".join(line.split()) for line in target.splitlines() if line.strip()]
    removed = list(difflib.ndiff(old_lines, new_lines))
    changes = []
    for line in removed:
        if line.startswith("- "):
            changes.append({"name": "clinical text", "old_value": line[2:], "new_value": "",
                            "change_type": "clinical_condition", "temporal_relation": "current",
                            "potentially_affected_concepts": []})
        elif line.startswith("+ "):
            changes.append({"name": "clinical text", "old_value": "", "new_value": line[2:],
                            "change_type": "clinical_condition", "temporal_relation": "current",
                            "potentially_affected_concepts": []})
    return {"changed_variables": changes, "unresolved_differences": []}


def last_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    found: list[tuple[int, int, dict[str, Any]]] = []
    for match in re.finditer(r"\{", text):
        try:
            value, used = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            found.append((match.start() + used, -match.start(), value))
    return max(found, key=lambda row: (row[0], row[1]))[2] if found else None


def one_repair(backend: Any, prompt: str, valid: Callable[[dict[str, Any]], bool],
               repair: str, max_tokens: int = 1024) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
             "retry_count": 0, "contract_failure": False}
    for attempt, value in enumerate((prompt, repair)):
        output = backend.generate([render_model_prompt(backend, value)], max_tokens)[0]
        usage["calls"] += 1
        usage["prompt_tokens"] += int(output.get("prompt_tokens", 0))
        usage["completion_tokens"] += int(output.get("completion_tokens", 0))
        parsed = last_object(str(output.get("raw_response", "")))
        if parsed is not None and valid(parsed):
            usage["retry_count"] = attempt
            return parsed, usage
    usage["retry_count"] = 1
    usage["contract_failure"] = True
    return None, usage


def render_model_prompt(backend: Any, prompt: str, max_input_tokens: int = 30000) -> str:
    tokenizer = getattr(backend, "tokenizer", None)
    if tokenizer is None:
        return prompt
    def chat(text: str) -> str:
        return tokenizer.apply_chat_template(
            [{"role": "system", "content": "You are a medical benchmark research model. Return JSON only."},
             {"role": "user", "content": text}], tokenize=False, add_generation_prompt=True)
    tokens = tokenizer.encode(prompt, add_special_tokens=False)
    empty = len(tokenizer.encode(chat(""), add_special_tokens=False))
    budget = max(0, max_input_tokens - empty - 16)
    if len(tokens) > budget:
        marker = tokenizer.encode("\n[...truncated...]\n", add_special_tokens=False)
        usable = max(0, budget - len(marker)); head = usable // 2
        tokens = tokens[:head] + marker + tokens[-(usable - head):]
        prompt = tokenizer.decode(tokens, skip_special_tokens=True)
    rendered = chat(prompt)
    if len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        raise ValueError("rendered DeltaRev prompt exceeds fixed input budget")
    return rendered


def delta_prompt(pair: dict[str, Any], mode: str, deterministic: dict[str, Any]) -> str:
    return (
        "Compare two synthetic benchmark cases. Return JSON with changed_variables and "
        "unresolved_differences. Do not diagnose or answer the case. "
        f"Mode: {mode}. Deterministic diff: {json.dumps(deterministic if mode == 'hybrid' else {}, ensure_ascii=False)}\n"
        f"Original:\n{pair['original_case']['text']}\nCounterfactual:\n{pair['counterfactual_case']['text']}"
    )


def delta_valid(value: dict[str, Any]) -> bool:
    return isinstance(value.get("changed_variables"), list) and isinstance(value.get("unresolved_differences"), list)


def hypotheses_valid(value: dict[str, Any]) -> bool:
    values = value.get("diagnoses")
    return (isinstance(values, list) and len(values) == 5
            and all(isinstance(row, str) and row.strip() for row in values)
            and len({normalize_answer(row) for row in values}) == 5)


def relevance_valid(value: dict[str, Any]) -> bool:
    return value.get("relevance") in {"relevant", "irrelevant", "uncertain"} and isinstance(value.get("reason"), str)


def rule_valid(value: dict[str, Any], allowed_targets: set[str]) -> bool:
    required = ("condition", "target", "polarity", "decision_effect", "exceptions",
                "population_scope", "evidence_id", "evidence_span", "source_type")
    return isinstance(value.get("rules"), list) and len(value["rules"]) <= 2 and all(
        isinstance(row, dict)
        and all(isinstance(row.get(key), str) for key in required if key != "exceptions")
        and isinstance(row.get("exceptions"), list)
        and row.get("polarity") in {"positive", "negative", "neutral"}
        and 0 < len(row["condition"]) <= 80
        and normalize_answer(row["target"]) in allowed_targets
        and 0 < len(row["decision_effect"]) <= 80
        and len(row["exceptions"]) <= 1
        and all(isinstance(item, str) and len(item) <= 80 for item in row["exceptions"])
        and 0 < len(row["population_scope"]) <= 40
        and 0 < len(row["source_type"]) <= 40
        and 0 < len(row["evidence_id"]) <= 40
        and 0 < len(row["evidence_span"]) <= 160
        for row in value["rules"]
    )


def verifier_valid(value: dict[str, Any]) -> bool:
    return isinstance(value.get("verifications"), list) and all(
        isinstance(row, dict) and isinstance(row.get("rule_id"), str)
        and isinstance(row.get("rule_entailed"), bool)
        and isinstance(row.get("patient_applicable"), bool)
        and row.get("relation_to_baseline") in {"refute", "support", "neutral"}
        and isinstance(row.get("supported_alternatives"), list)
        and isinstance(row.get("alternative_support_entailed"), bool)
        and row.get("conflict_status") in {"none", "resolved", "unresolved"}
        for row in value["verifications"]
    )


def build_queries(case_text: str, delta: dict[str, Any], baseline: str,
                  hypotheses: list[str]) -> dict[str, list[str]]:
    changed = " ; ".join(str(row.get("new_value", "")) for row in delta.get("changed_variables", []))
    refute = [f"{baseline} {changed} contraindication exclusion avoid not recommended inconsistent"]
    preserve = [f"{baseline} {changed} still indicated compatible permitted not contraindicated"]
    alternative = [f"{changed} {diagnosis} preferred diagnostic criterion appropriate" for diagnosis in hypotheses if normalize_answer(diagnosis) != normalize_answer(baseline)]
    return {
        "standard_question_retrieval": [case_text],
        "candidate_specific_retrieval": [f"{case_text}\nCandidate diagnosis: {candidate}" for candidate in hypotheses],
        "ea_rag_style_retrieval": [f"clinical parameters {changed}", f"evidence coverage {baseline} {changed}"] + refute + preserve,
        "delta_only_retrieval": [changed or case_text],
        "triangular_decision_change_retrieval": refute + preserve + alternative,
        "refute_only_retrieval": refute,
        "without_baseline_answer_in_query": [f"{changed} diagnostic criterion appropriate"] + alternative,
        "without_preserve_evidence": refute + alternative,
    }


def retrieve_queries(retriever: Any, queries: list[str], method: str,
                     count: int = 10) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    chosen, seen, pools, errors = [], set(), [], []
    for query_index, query in enumerate(queries):
        try:
            pools.append((query_index, retriever.retrieve(query, count)))
        except RuntimeError as error:
            errors.append({"method": method, "query_index": query_index,
                           "query": query, "error": str(error)})
    if errors:
        return [], errors
    for rank in range(count):
      for query_index, pool in pools:
        if rank >= len(pool):
            continue
        document = pool[rank]
        original_text = str(document.get("contents", document.get("text", "")))
        text = original_text[:4000]
        identity = (str(document.get("id", document.get("docid", ""))), text)
        if not text or identity in seen:
            continue
        seen.add(identity)
        chosen.append({**document, "id": f"D{len(chosen)}", "source_id": identity[0],
                       "contents": text, "query_index": query_index,
                       "truncated": len(original_text) > len(text)})
        if len(chosen) == count:
            return chosen, []
    return chosen[:count], []


def dependency_retrieval_errors(errors: list[dict[str, Any]], method: str,
                                dependency: str) -> list[dict[str, Any]]:
    return [{**row, "method": method, "error": f"{dependency}: {row['error']}"} for row in errors]


def zero_usage() -> dict[str, Any]:
    return {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
            "retry_count": 0, "contract_failure": False}


def retrieval_dependency_failures(method: str, shared_failures: list[str]) -> list[str]:
    dependencies = {
        "standard_question_retrieval": (),
        "candidate_specific_retrieval": ("hypotheses",),
        "ea_rag_style_retrieval": ("hybrid_delta",),
        "delta_only_retrieval": ("hybrid_delta",),
        "triangular_decision_change_retrieval": ("hybrid_delta", "hypotheses"),
    }[method]
    return [stage for stage in dependencies if stage in shared_failures]


def evidence_coverage_audit(delta: dict[str, Any], documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    corpus = " ".join(normalize_answer(row.get("contents", "")) for row in documents)
    audit = []
    for change in delta.get("changed_variables", []):
        name, value = str(change.get("name", "")), str(change.get("new_value", ""))
        terms = [term for term in (normalize_answer(name), normalize_answer(value)) if term]
        audit.append({"name": name, "new_value": value,
                      "covered": bool(terms) and all(term in corpus for term in terms)})
    return audit


def validate_rule_spans(rules: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = {str(row.get("id", row.get("docid", ""))): str(row.get("contents", "")) for row in documents}
    required = {"condition", "target", "polarity", "decision_effect", "exceptions",
                "population_scope", "evidence_id", "evidence_span", "source_type"}
    result = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict) or not required <= set(rule):
            continue
        evidence_id, span = str(rule["evidence_id"]), str(rule["evidence_span"]).strip()
        source = sources.get(evidence_id, "")
        start = source.casefold().find(span.casefold())
        if not span or evidence_id not in sources or start < 0:
            continue
        result.append({**rule, "evidence_span": source[start:start + len(span)],
                       "rule_id": str(rule.get("rule_id", f"R{index}"))})
    return result


def feature_score(verification: dict[str, Any]) -> float:
    features = verification.get("computed_features", {})
    score = 0.0
    score += .25 * bool(verification.get("rule_entailed"))
    score += .20 * bool(verification.get("patient_applicable"))
    score += .15 * float(features.get("source_authority", 0))
    score += .15 * max(0.0, min(1.0, float(features.get("refute_preserve_margin", 0))))
    score += .15 * bool(verification.get("supported_alternatives"))
    score += .10 * max(0.0, min(1.0, float(features.get("cross_query_agreement", 0))))
    if verification.get("conflict_status") == "unresolved":
        score -= .25
    return round(max(0.0, min(1.0, score)), 6)


def revision_allowed(relevance: str, verifications: list[dict[str, Any]], threshold: float,
                     require_entailment: bool = True, require_applicability: bool = True,
                     require_alternative: bool = True) -> tuple[bool, float, list[str]]:
    if any(row.get("conflict_status") == "unresolved"
           and row.get("computed_features", {}).get("source_authority", 0) > 0
           for row in verifications):
        return False, 0.0, []
    alternatives, refute_scores, alternative_scores = [], [], []
    for row in verifications:
        if require_entailment and not row.get("rule_entailed"):
            continue
        if require_applicability and not row.get("patient_applicable"):
            continue
        if row.get("conflict_status") == "unresolved":
            continue
        if row.get("relation_to_baseline") == "refute":
            refute_scores.append(feature_score(row))
        if (row.get("alternative_support_entailed")
                and (row.get("rule_entailed") or not require_entailment)
                and (row.get("patient_applicable") or not require_applicability)):
            supported = [str(value) for value in row.get("supported_alternatives", []) if str(value).strip()]
            if supported:
                alternatives.extend(supported)
                alternative_scores.append(feature_score(row))
    # Threshold only decisive evidence. A strong baseline-support/neutral rule cannot
    # rescue weak refutation or weak positive support.
    refute_score = max(refute_scores, default=0.0)
    score = (min(refute_score, max(alternative_scores, default=0.0))
             if require_alternative else refute_score)
    allowed = relevance == "relevant" and bool(refute_scores) and score >= threshold
    if require_alternative:
        allowed = allowed and bool(alternatives)
    return allowed, score, list(dict.fromkeys(alternatives))


def deterministic_candidate(hypotheses: list[str], baseline: Any,
                            verifications: list[dict[str, Any]],
                            require_alternative: bool = True,
                            require_entailment: bool = True,
                            require_applicability: bool = True) -> dict[str, Any]:
    allowed = {normalize_answer(value): value for value in hypotheses
               if normalize_answer(value) != normalize_answer(baseline)}
    counts = {key: 0 for key in allowed}
    rule_ids = {key: [] for key in allowed}
    refute_ids = [row["rule_id"] for row in verifications
                  if row.get("relation_to_baseline") == "refute"
                  and (row.get("rule_entailed") or not require_entailment)
                  and (row.get("patient_applicable") or not require_applicability)
                  and row.get("conflict_status") != "unresolved"]
    for row in verifications:
        if not (row.get("alternative_support_entailed")
                and (row.get("rule_entailed") or not require_entailment)
                and (row.get("patient_applicable") or not require_applicability)
                and row.get("conflict_status") != "unresolved"):
            continue
        for value in row.get("supported_alternatives", []):
            key = normalize_answer(value)
            if key in counts:
                counts[key] += 1; rule_ids[key].append(row["rule_id"])
    ranked = sorted(allowed, key=lambda key: (-counts[key], list(allowed).index(key)))
    chosen = next((key for key in ranked if counts[key] > 0), None)
    if chosen is None and not require_alternative:
        chosen = ranked[0] if ranked else None
    return {
        "candidate_answer": allowed.get(chosen) if chosen else None,
        "decisive_rule_ids": list(dict.fromkeys(refute_ids + (rule_ids.get(chosen, []) if chosen else []))),
        "reason": ("highest verified positive alternative-support count"
                   if chosen and counts[chosen] else "alternative-support requirement ablated"
                   if chosen else "no verified supported alternative"),
    }


def preserve_or_revise(baseline: Any, allowed: bool, reviser: Callable[[], Any]) -> Any:
    """The exact baseline object is returned without invoking the reviser on preserve."""
    if not allowed:
        return baseline
    revised = reviser()
    return baseline if revised is None else revised


def _model_answer(backend: Any, prompt: str) -> tuple[Any | None, dict[str, Any]]:
    placeholders = {"concise diagnosis", "specific diagnosis", "specific clinical label",
                    "diagnosis", "answer", "unknown", "n/a", "none", "unspecified"}
    valid = lambda row: (set(row) == {"answer"} and isinstance(row["answer"], str)
                         and bool(normalize_answer(row["answer"]))
                         and normalize_answer(row["answer"]) not in placeholders)
    contract = (
        'Output exactly one JSON object and no other text. The object must have exactly one top-level field '
        'named "answer" and follow this empty schema: {"answer":""}. Replace the empty value with the '
        'specific diagnosis inferred by the task; never copy an empty or generic placeholder.'
    )
    initial = f"{contract}\nTask:\n{prompt}"
    repair = f"{contract}\nThe previous response violated this JSON contract. Return the corrected object only.\nTask:\n{prompt}"
    parsed, usage = one_repair(
        backend, initial, valid, repair
    )
    return (parsed.get("answer") if parsed else None), usage


def answer_with_retrieval(backend: Any, prompt: str,
                          errors: list[dict[str, Any]]) -> tuple[Any | None, dict[str, Any]]:
    return ((None, {**zero_usage(), "skipped": "retrieval_error"}) if errors
            else _model_answer(backend, prompt))


def _extract_rules(backend: Any, case_text: str, baseline: Any, hypotheses: list[str],
                   documents: list[dict[str, Any]], allow_generated: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prompt_documents = [{"id": row.get("id"), "source": row.get("source"),
                         "contents": str(row.get("contents", ""))[:1200]} for row in documents]
    allowed_targets = {normalize_answer(value) for value in [baseline, *hypotheses]
                       if normalize_answer(value)}
    skeleton = ('{"rules":[{"condition":"","target":"","polarity":"",'
                '"decision_effect":"","exceptions":[],"population_scope":"",'
                '"evidence_id":"","evidence_span":"","source_type":""}]}')
    prompt = (
        "Return one complete compact JSON object within 384 output tokens. Extract at most two atomic rules. "
        "Condition must be a short clinical predicate grounded by the evidence, never a copy of the whole case. "
        "Target must exactly equal the baseline or one listed alternative. Evidence span must be short and verbatim. "
        "each rule requires condition,target,polarity,decision_effect,exceptions,population_scope,evidence_id,"
        "evidence_span,source_type. Limits: condition/decision_effect 80 chars; exceptions array max one; "
        "population/source 40 chars; evidence_span 160 chars. Omit explanations. Exact skeleton: " + skeleton + ". "
        + ("This negative-control condition explicitly treats generated text as decisive.\n" if allow_generated
           else "Do not use generated medical text as authoritative.\n")
        + f"Case: {case_text}\nBaseline: {baseline}\nAlternatives: {hypotheses}\nDocuments: {prompt_documents}"
    )
    parsed, usage = one_repair(
        backend, prompt, lambda value: rule_valid(value, allowed_targets),
        prompt + "\nRepair as one complete compact JSON object with at most two rules; return an empty rules array if no cited span exists.",
        max_tokens=384)
    return validate_rule_spans(parsed.get("rules", []) if parsed else [], documents), usage


def _verify_rules(backend: Any, case_text: str, baseline: Any, hypotheses: list[str],
                  rules: list[dict[str, Any]], documents: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not rules:
        return [], {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                    "retry_count": 0, "contract_failure": False}
    prompt = (
        "Return one complete compact JSON object within 384 output tokens. Verify every cited rule. "
        "Return JSON verifications with rule_id,rule_entailed,"
        "patient_applicable,relation_to_baseline(refute/support/neutral),supported_alternatives,"
        "alternative_support_entailed(boolean),conflict_status(none/resolved/unresolved). "
        "Return exactly one compact verification for every input rule_id. Do not output confidence scores or explanations.\n"
        f"Case: {case_text}\nBaseline: {baseline}\nRules: {rules}\nDocuments: {documents}"
    )
    required_ids = [row["rule_id"] for row in rules]
    def verification_rows(value: dict[str, Any]) -> list[dict[str, Any]] | None:
        rows = value.get("verifications")
        if isinstance(rows, list):
            return rows
        if set(value) != set(required_ids) or not all(isinstance(value[key], dict) for key in required_ids):
            return None
        return [{**value[key], "rule_id": value[key].get("rule_id", key)} for key in required_ids]
    def complete(value: dict[str, Any]) -> bool:
        rows = verification_rows(value)
        if rows is None or not verifier_valid({"verifications": rows}):
            return False
        observed = [row["rule_id"] for row in rows]
        return len(observed) == len(set(observed)) and sorted(observed) == sorted(required_ids)
    parsed, usage = one_repair(
        backend, prompt, complete,
        prompt + "\nRepair as one complete compact JSON object covering each listed rule_id exactly once.",
        max_tokens=384
    )
    values = verification_rows(parsed) if parsed else []
    known = {row["rule_id"]: row for row in rules}
    docs = {str(row["id"]): row for row in documents}
    allowed = {normalize_answer(value): value for value in hypotheses
               if normalize_answer(value) != normalize_answer(baseline)}
    result = []
    for row in values:
        if not isinstance(row, dict) or row.get("rule_id") not in known:
            continue
        rule = known[row["rule_id"]]
        document = docs.get(str(rule["evidence_id"]), {})
        target = normalize_answer(rule.get("target"))
        positive_target = allowed.get(target) if rule.get("polarity") == "positive" else None
        alternatives = [positive_target for value in row.get("supported_alternatives", [])
                        if positive_target and row.get("alternative_support_entailed")
                        and row.get("rule_entailed") and row.get("patient_applicable")
                        and normalize_answer(value) == target]
        result.append({**row, "alternative_support_entailed": bool(alternatives),
                       "supported_alternatives": list(dict.fromkeys(alternatives)),
                       "computed_features": {
                           "source_authority": int(document.get("source") in {"textbooks", "wikipedia", "fixed"}),
                           "query_index": document.get("query_index"),
                       }})
    refute = sum(row["relation_to_baseline"] == "refute" for row in result)
    support = sum(row["relation_to_baseline"] == "support" for row in result)
    refute_queries = {row["computed_features"].get("query_index") for row in result
                      if row["relation_to_baseline"] == "refute"}
    margin = max(0.0, (refute - support) / max(1, refute + support))
    agreement = min(1.0, len(refute_queries) / 2)
    for row in result:
        row["computed_features"].update({"refute_preserve_margin": margin,
                                         "cross_query_agreement": agreement})
    return result, usage


def rules_with_retrieval(backend: Any, case_text: str, baseline: Any, hypotheses: list[str],
                         documents: list[dict[str, Any]], errors: list[dict[str, Any]],
                         allow_generated: bool = False) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if errors:
        skipped = {**zero_usage(), "skipped": "retrieval_error"}
        return [], [], skipped, copy.deepcopy(skipped)
    rules, extraction = _extract_rules(
        backend, case_text, baseline, hypotheses, documents, allow_generated=allow_generated)
    verified, verification = _verify_rules(
        backend, case_text, baseline, hypotheses, rules, documents)
    return rules, verified, extraction, verification


def shuffle_source_map(pairs: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    by_split: dict[str, list[str]] = {}
    for pair in pairs:
        by_split.setdefault(pair["split"], []).append(pair["pair_id"])
    for split, identifiers in by_split.items():
        identifiers.sort()
        if len(identifiers) < 2:
            raise ValueError(f"shuffle needs at least two pairs in split {split}")
        for target, source in zip(identifiers, identifiers[1:] + identifiers[:1]):
            result[target] = source
    return result


def run_pairs(pairs: list[dict[str, Any]], baselines: dict[str, dict[str, Any]], output_dir: Path,
              backend: Any, retriever: Any) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    proposal_path = output_dir / "raw_proposals.jsonl"
    existing_rows = read_jsonl(proposal_path) if proposal_path.exists() else []
    done = {(row["pair_id"], row["method"]) for row in existing_rows}
    existing = {(row["pair_id"], row["method"]): row for row in existing_rows}
    delta_cache = {row["pair_id"]: row for row in read_jsonl(output_dir / "deltas.jsonl")} if (output_dir / "deltas.jsonl").exists() else {}
    retrieval_cache = {row["pair_id"]: row for row in read_jsonl(output_dir / "retrieval.jsonl")
                       if row.get("artifact_type", "base") == "base"} if (output_dir / "retrieval.jsonl").exists() else {}
    rule_cache = {(row["pair_id"], row["retrieval_method"]): row for row in read_jsonl(output_dir / "rules.jsonl")} if (output_dir / "rules.jsonl").exists() else {}
    source_map = shuffle_source_map(pairs)
    prepared: dict[str, dict[str, Any]] = {}
    for pair in pairs:
        pair_id = pair["pair_id"]
        if all((pair_id, method) in done for method in METHODS):
            continue
        baseline_row = baselines[pair_id]
        baseline = copy.deepcopy(baseline_row["members"]["trap"]["baseline_answer"])
        if not normalize_answer(baseline) or not normalize_answer(baseline_row["members"]["control"]["baseline_answer"]):
            raise ValueError(f"empty baseline answer: {pair_id}")
        det = deterministic_delta(pair["original_case"]["text"], pair["counterfactual_case"]["text"])
        llm, llm_usage = one_repair(backend, delta_prompt(pair, "llm", det), delta_valid,
                                    delta_prompt(pair, "llm", det) + "\nRepair JSON only.")
        hybrid, hybrid_usage = one_repair(backend, delta_prompt(pair, "hybrid", det), delta_valid,
                                          delta_prompt(pair, "hybrid", det) + "\nRepair JSON only.")
        llm = llm or {"changed_variables": [], "unresolved_differences": ["contract_failure"]}
        hybrid = hybrid or det
        append_once(output_dir / "deltas.jsonl", (pair_id,),
                    {"pair_id": pair_id, "split": pair["split"], "deterministic": det,
                     "llm_only": llm, "hybrid": hybrid,
                     "usage": {"llm": llm_usage, "hybrid": hybrid_usage}}, ("pair_id",))
        delta_cache[pair_id] = {"pair_id": pair_id, "hybrid": hybrid,
                                "usage": {"llm": llm_usage, "hybrid": hybrid_usage}}
        hypothesis_prompt = ("Return JSON with exactly five distinct plausible diagnosis strings under diagnoses. "
                             f"Do not answer from a paired case. Target case:\n{pair['counterfactual_case']['text']}")
        hypothesis_obj, hypothesis_usage = one_repair(backend, hypothesis_prompt, hypotheses_valid,
                                                       hypothesis_prompt + "\nRepair to exactly five diagnoses.")
        hypotheses = list(dict.fromkeys(hypothesis_obj.get("diagnoses", []) if hypothesis_obj else []))
        relevance_prompt = ("Classify whether the delta can change the baseline diagnosis. JSON relevance must be "
                            "relevant, irrelevant, or uncertain; include affected_decision_dimension and reason.\n"
                            f"Target: {pair['counterfactual_case']['text']}\nDelta: {hybrid}\nBaseline: {baseline}")
        relevance_obj, relevance_usage = one_repair(backend, relevance_prompt, relevance_valid,
                                                     relevance_prompt + "\nRepair JSON only.")
        relevance = relevance_obj or {"relevance": "uncertain", "affected_decision_dimension": [], "reason": "contract failure"}
        queries = build_queries(pair["counterfactual_case"]["text"], hybrid, str(baseline), hypotheses)
        standard_documents, standard_errors = retrieve_queries(
            retriever, queries["standard_question_retrieval"], "standard_question_retrieval")
        retrievals = {"standard_question_retrieval": standard_documents}
        retrieval_errors = {"standard_question_retrieval": standard_errors}
        coverage_audit = evidence_coverage_audit(hybrid, retrievals["standard_question_retrieval"])
        queries["ea_rag_style_retrieval"] += [
            f"{row['name']} {row['new_value']} contrasting diagnostic evidence"
            for row in coverage_audit if not row["covered"]
        ]
        for name, query_list in queries.items():
            if name not in retrievals:
                if name == "ea_rag_style_retrieval" and standard_errors:
                    retrievals[name] = []
                    retrieval_errors[name] = dependency_retrieval_errors(
                        standard_errors, name, "standard_question_retrieval")
                else:
                    retrievals[name], retrieval_errors[name] = retrieve_queries(
                        retriever, query_list, name)
        append_once(output_dir / "retrieval.jsonl", (pair_id, "base"),
                    {"pair_id": pair_id, "split": pair["split"], "artifact_type": "base",
                     "queries": queries, "results": retrievals, "errors": retrieval_errors,
                     "ea_rag_style": {"reproduction": "coverage-audit proxy, not exact reproduction",
                                      "coverage_audit": coverage_audit}},
                    ("pair_id", "artifact_type"))
        retrieval_cache[pair_id] = {"pair_id": pair_id, "artifact_type": "base",
                                    "queries": queries, "results": retrievals,
                                    "errors": retrieval_errors}
        rule_sets, verification_sets, rule_failures = {}, {}, {}
        for name, documents in retrievals.items():
            errors = retrieval_errors.get(name, [])
            rules, verified, extraction_usage, verifier_usage = rules_with_retrieval(
                backend, pair["counterfactual_case"]["text"], baseline, hypotheses, documents, errors)
            rule_sets[name], verification_sets[name] = rules, verified
            rule_failures[name] = (["retrieval"] if errors else []) + [stage for stage, usage in (("rule_extraction", extraction_usage),
                                                               ("verification", verifier_usage))
                                   if usage.get("contract_failure")]
            append_once(output_dir / "rules.jsonl", (pair_id, name),
                        {"pair_id": pair_id, "retrieval_method": name, "rules": rules,
                         "verifications": verified,
                         "usage": {"extractor": extraction_usage, "verifier": verifier_usage},
                         "retrieval_errors": errors},
                        ("pair_id", "retrieval_method"))
            rule_cache[(pair_id, name)] = {"pair_id": pair_id, "retrieval_method": name,
                                           "rules": rules, "verifications": verified,
                                           "usage": {"extractor": extraction_usage, "verifier": verifier_usage},
                                           "retrieval_errors": errors}
        prepared[pair_id] = {"pair": pair, "baseline": baseline, "hypotheses": hypotheses,
                             "relevance": relevance, "delta": hybrid, "retrievals": retrievals,
                             "retrieval_errors": retrieval_errors,
                             "rules": rule_sets, "verified": verification_sets,
                             "failures": ([stage for stage, usage in (("hybrid_delta", hybrid_usage),
                                                                       ("hypotheses", hypothesis_usage),
                                                                       ("relevance", relevance_usage))
                                           if usage.get("contract_failure")]),
                             "rule_failures": rule_failures,
                             "shared_usage": {"hypotheses": hypothesis_usage, "relevance": relevance_usage}}
    # Mapping is based on the complete shard input, so resume cannot change shuffle assignment.
    missing_shuffle_cache = [source for source in set(source_map.values())
                             if source not in delta_cache or source not in retrieval_cache
                             or (source, "triangular_decision_change_retrieval") not in rule_cache]
    if missing_shuffle_cache:
        raise ValueError(f"shuffle source cache missing after preparation: {missing_shuffle_cache[:3]}")
    written = 0
    for pair_id, value in prepared.items():
        pair, baseline, hypotheses = value["pair"], value["baseline"], value["hypotheses"]
        relevance = value["relevance"]["relevance"]
        direct, direct_usage = _model_answer(backend, f"Return JSON answer with a concise diagnosis. Case:\n{pair['counterfactual_case']['text']}")
        direct_control, control_usage = _model_answer(backend, f"Return JSON answer with a concise diagnosis. Case:\n{pair['original_case']['text']}")
        counterfactual_direct, counterfactual_usage = _model_answer(
            backend, f"Compare the original and target cases and return JSON answer for the target.\nOriginal: {pair['original_case']['text']}\nTarget: {pair['counterfactual_case']['text']}")
        revised_direct, revised_usage = _model_answer(
            backend, f"Revise only if needed and return JSON answer for the target. Target: {pair['counterfactual_case']['text']}\nBaseline: {baseline}\nDelta: {value['delta']}")
        decomposition, decomposition_usage = _model_answer(
            backend, f"Choose the best present-state diagnosis from these hypotheses and return JSON answer. Do not predict transitions.\nTarget: {pair['counterfactual_case']['text']}\nDelta: {value['delta']}\nHypotheses: {hypotheses}")
        decomposition_control, decomposition_control_usage = _model_answer(
            backend, f"Choose the best present-state diagnosis and return JSON answer. Do not predict transitions.\nCase: {pair['original_case']['text']}")
        rows = []
        def add(method: str, proposed: Any, score: float = 1.0, gate: bool = True,
                status: str = "ok", details: dict[str, Any] | None = None,
                control_prediction: Any | None = None) -> None:
            if (pair_id, method) not in done:
                rows.append({"pair_id": pair_id, "dataset": "medeinst", "split": pair["split"],
                             "method": method, "baseline_answer": copy.deepcopy(baseline),
                             "proposed_answer": copy.deepcopy(proposed), "verifier_score": score,
                             "gate_without_threshold": gate, "status": status, "details": details or {},
                             "control_prediction": copy.deepcopy(control_prediction)})
        add("direct", direct, status="ok" if direct and direct_control else "parse_failure",
            details={"usage": direct_usage, "control_usage": control_usage}, control_prediction=direct_control)
        add("direct_counterfactual_prompt", counterfactual_direct,
            status="ok" if counterfactual_direct and direct_control else "parse_failure",
            details={"usage": counterfactual_usage}, control_prediction=direct_control)
        revision_failures = (["hybrid_delta"] if "hybrid_delta" in value["failures"] else [])
        add("direct_answer_revision", revised_direct,
            status="contract_failure" if revision_failures else "ok" if revised_direct else "parse_failure",
            details={"usage": revised_usage, "stage_failures": revision_failures})
        add("medrgag_proxy", baseline)
        add("always_preserve", copy.deepcopy(baseline))
        decomposition_failures = [stage for stage in ("hybrid_delta", "hypotheses")
                                  if stage in value["failures"]] + [stage for stage, usage in (
            ("decomposition", decomposition_usage), ("decomposition_control", decomposition_control_usage))
            if usage.get("contract_failure")]
        add("decomposition_only", decomposition,
            status="contract_failure" if decomposition_failures else "ok",
            details={"usage": decomposition_usage, "control_usage": decomposition_control_usage,
                     "stage_failures": decomposition_failures}, control_prediction=decomposition_control)
        different = next((row for row in hypotheses if normalize_answer(row) != normalize_answer(baseline)), None)
        add("always_revise", different, status="ok" if different else "contract_failure")
        no_evidence, no_evidence_usage = _model_answer(
            backend, f"Without external evidence, decide whether to revise and return a diagnosis JSON answer.\nTarget: {pair['counterfactual_case']['text']}\nBaseline: {baseline}\nHypotheses: {hypotheses}")
        no_evidence_gate = bool(no_evidence) and normalize_answer(no_evidence) != normalize_answer(baseline)
        no_evidence_failures = (["hypotheses"] if value["shared_usage"]["hypotheses"].get("contract_failure") else [])
        add("llm_verifier_without_evidence", no_evidence or baseline, .5, no_evidence_gate,
            status="contract_failure" if no_evidence_failures else "ok" if no_evidence else "parse_failure",
            details={"usage": no_evidence_usage, "stage_failures": no_evidence_failures})
        # Retrieval baselines answer normally from equal-budget retrieved text; they do not use the residual gate.
        for method in ("standard_question_retrieval", "candidate_specific_retrieval", "ea_rag_style_retrieval",
                       "delta_only_retrieval", "triangular_decision_change_retrieval"):
            errors = value["retrieval_errors"].get(method, [])
            answer, usage = answer_with_retrieval(
                backend,
                f"Answer the target case using the retrieved documents. Return JSON answer.\nTarget: {pair['counterfactual_case']['text']}\nDocuments: {value['retrievals'][method]}",
                errors)
            failures = retrieval_dependency_failures(method, value["failures"])
            if errors:
                failures.append(method)
            add(method, answer,
                status="contract_failure" if failures else "ok" if answer else "parse_failure",
                details={"usage": usage, "ordinary_retrieval_reader": True,
                         "stage_failures": failures})
        # Mechanism ablations are rebuilt and reverified for the target patient.
        empty_relevance_prompt = (
            "Classify whether the target can change the baseline without an explicit delta. JSON relevance, "
            f"affected_decision_dimension, reason. Target: {pair['counterfactual_case']['text']}\nBaseline: {baseline}"
        )
        empty_relevance, empty_relevance_usage = one_repair(
            backend, empty_relevance_prompt, relevance_valid,
            empty_relevance_prompt + "\nRepair JSON only.")
        shuffled_source = source_map[pair_id]
        shuffled_value = copy.deepcopy(delta_cache[shuffled_source]["hybrid"])
        shuffled_relevance_prompt = (
            "Classify whether this shuffled delta changes the target baseline. JSON relevance, "
            f"affected_decision_dimension, reason. Target: {pair['counterfactual_case']['text']}\n"
            f"Baseline: {baseline}\nDelta: {shuffled_value}"
        )
        shuffled_relevance, shuffled_relevance_usage = one_repair(
            backend, shuffled_relevance_prompt, relevance_valid,
            shuffled_relevance_prompt + "\nRepair JSON only.")
        shuffled_queries = build_queries(pair["counterfactual_case"]["text"], shuffled_value, str(baseline), hypotheses)
        shuffled_documents, shuffled_retrieval_errors = retrieve_queries(
            retriever, shuffled_queries["triangular_decision_change_retrieval"], "shuffled_delta")
        append_once(output_dir / "retrieval.jsonl", (pair_id, "shuffled_delta"),
                    {"pair_id": pair_id, "split": pair["split"], "artifact_type": "shuffled_delta",
                     "source_pair_id": shuffled_source,
                     "queries": shuffled_queries["triangular_decision_change_retrieval"],
                     "results": shuffled_documents, "errors": shuffled_retrieval_errors},
                    ("pair_id", "artifact_type"))
        shuffled_delta_rules, shuffled_delta_verified, shuffled_extract_usage, shuffled_verify_usage = rules_with_retrieval(
            backend, pair["counterfactual_case"]["text"], baseline, hypotheses,
            shuffled_documents, shuffled_retrieval_errors)
        append_once(output_dir / "rules.jsonl", (pair_id, "shuffled_delta"),
                    {"pair_id": pair_id, "retrieval_method": "shuffled_delta",
                     "rules": shuffled_delta_rules, "verifications": shuffled_delta_verified,
                     "usage": {"extractor": shuffled_extract_usage, "verifier": shuffled_verify_usage},
                     "retrieval_errors": shuffled_retrieval_errors},
                    ("pair_id", "retrieval_method"))
        donor_retrieval_errors = retrieval_cache[shuffled_source].get("errors", {}).get(
            "triangular_decision_change_retrieval", [])
        if donor_retrieval_errors:
            mismatched_documents, mismatched_rules, shuffled_evidence_verified = [], [], []
            shuffled_evidence_usage = {**zero_usage(), "skipped": "donor_retrieval_error"}
        else:
            mismatched_documents = copy.deepcopy(
                retrieval_cache[shuffled_source]["results"]["triangular_decision_change_retrieval"])
            mismatched_rules = validate_rule_spans(
                copy.deepcopy(rule_cache[(shuffled_source, "triangular_decision_change_retrieval")]["rules"]),
                mismatched_documents)
            shuffled_evidence_verified, shuffled_evidence_usage = _verify_rules(
                backend, pair["counterfactual_case"]["text"], baseline, hypotheses,
                mismatched_rules, mismatched_documents)
        append_once(output_dir / "rules.jsonl", (pair_id, "shuffled_rule_evidence"),
                    {"pair_id": pair_id, "retrieval_method": "shuffled_rule_evidence",
                     "source_pair_id": shuffled_source, "rules": mismatched_rules,
                     "verifications": shuffled_evidence_verified,
                     "usage": {"verifier": shuffled_evidence_usage},
                     "retrieval_errors": donor_retrieval_errors}, ("pair_id", "retrieval_method"))
        conditions = {
            "evidence_verifier_with_standard_retrieval": ("standard_question_retrieval", {}),
            "evidence_verifier_with_ea_rag_retrieval": ("ea_rag_style_retrieval", {}),
            "full_deltarev": ("triangular_decision_change_retrieval", {}),
            "without_delta": ("standard_question_retrieval", {
                "relevance": (empty_relevance or {"relevance": "uncertain"})["relevance"],
                "failures": (["hypotheses"] if "hypotheses" in value["failures"] else [])
                + (["without_delta_relevance"] if empty_relevance_usage.get("contract_failure") else [])
                + [f"standard_{stage}" for stage in value["rule_failures"]["standard_question_retrieval"]]}),
            "without_baseline_answer_in_query": ("without_baseline_answer_in_query", {}),
            "refute_only_retrieval": ("refute_only_retrieval", {}),
            "without_preserve_evidence": ("without_preserve_evidence", {}),
            "without_alternative_support_requirement": ("triangular_decision_change_retrieval", {"require_alternative": False}),
            "without_entailment_check": ("triangular_decision_change_retrieval", {"require_entailment": False}),
            "without_patient_applicability_check": ("triangular_decision_change_retrieval", {"require_applicability": False}),
            "shuffled_delta": ("triangular_decision_change_retrieval", {
                "relevance": (shuffled_relevance or {"relevance": "uncertain"})["relevance"],
                "verified": shuffled_delta_verified, "rules": shuffled_delta_rules,
                "failures": (["hypotheses"] if "hypotheses" in value["failures"] else [])
                + (["donor_hybrid_delta"] if delta_cache[shuffled_source].get("usage", {}).get("hybrid", {}).get("contract_failure") else [])
                + (["shuffled_retrieval"] if shuffled_retrieval_errors else [])
                + [stage for stage, usage in (("shuffled_relevance", shuffled_relevance_usage),
                    ("shuffled_rule_extraction", shuffled_extract_usage),
                    ("shuffled_verification", shuffled_verify_usage)) if usage.get("contract_failure")]}),
            "shuffled_rule_evidence": ("triangular_decision_change_retrieval", {
                "verified": shuffled_evidence_verified, "rules": mismatched_rules,
                "failures": ([stage for stage in ("hypotheses", "relevance") if stage in value["failures"]]
                + (["donor_hybrid_delta"] if delta_cache[shuffled_source].get("usage", {}).get("hybrid", {}).get("contract_failure") else [])
                + (["donor_hypotheses"] if ((shuffled_source in prepared and "hypotheses" in prepared[shuffled_source]["failures"])
                    or "hypotheses" in existing.get((shuffled_source, "candidate_specific_retrieval"), {}).get("details", {}).get("stage_failures", [])) else [])
                + (["donor_triangular_rule_extraction"] if rule_cache[(shuffled_source, "triangular_decision_change_retrieval")]
                   .get("usage", {}).get("extractor", {}).get("contract_failure") else [])
                + (["donor_triangular_retrieval"] if donor_retrieval_errors else [])
                + (["shuffled_evidence_verification"] if shuffled_evidence_usage.get("contract_failure") else []))}),
        }
        for method, (retrieval_name, overrides) in conditions.items():
            verified = overrides.get("verified", value["verified"].get(retrieval_name, []))
            rel = overrides.get("relevance", relevance)
            allowed, score, alternatives = revision_allowed(
                rel, verified, 0.0,
                require_entailment=overrides.get("require_entailment", True),
                require_applicability=overrides.get("require_applicability", True),
                require_alternative=overrides.get("require_alternative", True),
            )
            selection = deterministic_candidate(
                hypotheses, baseline, verified,
                require_alternative=overrides.get("require_alternative", True),
                require_entailment=overrides.get("require_entailment", True),
                require_applicability=overrides.get("require_applicability", True),
            )
            proposed = selection["candidate_answer"]
            if proposed is None:
                allowed = False
            failures = (list(overrides["failures"]) if "failures" in overrides else
                        list(value["failures"]) + list(value["rule_failures"].get(retrieval_name, [])))
            add(method, proposed, score, allowed,
                status="contract_failure" if failures else "ok",
                details={"retrieval_method": retrieval_name, "relevance": rel,
                         "alternative_count": len(alternatives), "stage_failures": failures, **selection})
        generated = baselines[pair_id]["members"]["trap"].get("generated_documents", [])
        kgcc_rules, kgcc_extract_usage = _extract_rules(
            backend, pair["counterfactual_case"]["text"], baseline,
            hypotheses, generated, allow_generated=True)
        kgcc_verified, kgcc_verify_usage = _verify_rules(
            backend, pair["counterfactual_case"]["text"], baseline,
            hypotheses, kgcc_rules, generated)
        append_once(output_dir / "rules.jsonl", (pair_id, "kgcc_generated_decisive"),
                    {"pair_id": pair_id, "retrieval_method": "kgcc_generated_decisive",
                     "rules": kgcc_rules, "verifications": kgcc_verified,
                     "usage": {"extractor": kgcc_extract_usage, "verifier": kgcc_verify_usage}},
                    ("pair_id", "retrieval_method"))
        allowed, score, alternatives = revision_allowed(relevance, kgcc_verified, 0.0)
        selection = deterministic_candidate(hypotheses, baseline, kgcc_verified)
        proposed = selection["candidate_answer"]
        if proposed is None:
            allowed = False
        kgcc_failures = list(value["failures"]) + [stage for stage, usage in (
            ("kgcc_rule_extraction", kgcc_extract_usage), ("kgcc_verification", kgcc_verify_usage))
            if usage.get("contract_failure")]
        add("kgcc_generated_docs_as_decisive_evidence", proposed, score, allowed,
            status="contract_failure" if kgcc_failures else "ok",
            details={"negative_control": True,
                     "stage_failures": kgcc_failures, **selection})
        add("without_nice", baseline, 0.0, False, status="unavailable", details={"reason": UNAVAILABLE["without_nice"]})
        append_rows(proposal_path, rows)
        written += len(rows)
    return written


def normalize_artifact(row: dict[str, Any], kind: str) -> dict[str, Any]:
    row = copy.deepcopy(row)
    if kind == "retrieval" and "errors" not in row:
        row["errors"] = ({method: [] for method in row.get("results", {})}
                         if row.get("artifact_type", "base") == "base" else [])
    if kind == "rules" and "retrieval_errors" not in row:
        row["retrieval_errors"] = []
    return row


def merge_jsonl(inputs: list[Path], output: Path, key_fields: tuple[str, ...],
                kind: str = "") -> int:
    values: dict[tuple[Any, ...], dict[str, Any]] = {}
    for path in inputs:
        for raw_row in read_jsonl(path):
            row = normalize_artifact(raw_row, kind)
            key = tuple(row.get(field) for field in key_fields)
            if None in key:
                raise ValueError(f"missing merge key {key_fields}: {path}")
            if key in values and values[key] != row:
                raise ValueError(f"conflicting duplicate merge key: {key}")
            values[key] = row
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(values[key], ensure_ascii=False, sort_keys=True) + "\n"
                              for key in sorted(values)), encoding="utf-8")
    return len(values)


def _unique_index(rows: list[dict[str, Any]], fields: tuple[str, ...], label: str) -> dict[tuple[Any, ...], dict[str, Any]]:
    result = {}
    for row in rows:
        key = tuple(row.get(field) for field in fields)
        if None in key or key in result:
            raise ValueError(f"invalid or duplicate {label} key: {key}")
        result[key] = row
    return result


def corrected_proposal_rows(proposal_path: Path) -> list[dict[str, Any]]:
    """Recompute dependency-only statuses while preserving the raw shard file."""
    sibling_paths = {name: proposal_path.parent / name for name in
                     ("deltas.jsonl", "retrieval.jsonl", "rules.jsonl")}
    missing = [str(path) for path in sibling_paths.values() if not path.exists()]
    if missing:
        raise ValueError(f"proposal merge requires sibling artifacts: {missing}")
    rows = read_jsonl(proposal_path)
    proposals = _unique_index(rows, ("pair_id", "method"), "proposal")
    deltas = _unique_index(read_jsonl(sibling_paths["deltas.jsonl"]), ("pair_id",), "delta")
    retrievals = _unique_index(read_jsonl(sibling_paths["retrieval.jsonl"]),
                               ("pair_id", "artifact_type"), "retrieval")
    rules = _unique_index(read_jsonl(sibling_paths["rules.jsonl"]),
                          ("pair_id", "retrieval_method"), "rule")

    def failed(usage: dict[str, Any]) -> bool:
        return bool(usage.get("contract_failure"))
    def stages(pair_id: str, method: str) -> list[str]:
        return list(proposals[(pair_id, method)].get("details", {}).get("stage_failures", []))
    def rule_failure(pair_id: str, method: str, prefix: str,
                     extractor: bool = True, verifier: bool = True) -> list[str]:
        artifact = rules[(pair_id, method)]
        usage = artifact.get("usage", {})
        result = []
        if extractor and failed(usage.get("extractor", {})):
            result.append(f"{prefix}rule_extraction")
        if verifier and failed(usage.get("verifier", {})):
            result.append(f"{prefix}verification")
        return result
    def shared(pair_id: str) -> tuple[bool, bool, bool]:
        hybrid = failed(deltas[(pair_id,)].get("usage", {}).get("hybrid", {}))
        hypothesis = "hypotheses" in stages(pair_id, "candidate_specific_retrieval")
        relevance = "relevance" in stages(pair_id, "full_deltarev")
        return hybrid, hypothesis, relevance
    def update(pair_id: str, method: str, failures: list[str]) -> None:
        row = proposals[(pair_id, method)]
        row["details"] = {**row.get("details", {}),
                          "stage_failures": list(dict.fromkeys(failures))}
        row["status"] = "contract_failure" if failures else "ok"
    def retrieval_failed(pair_id: str, method: str) -> bool:
        artifact = retrievals[(pair_id, "base")]
        errors = artifact.get("errors", {})
        return bool(errors.get(method, []) or
                    (method == "ea_rag_style_retrieval"
                     and errors.get("standard_question_retrieval", [])))
    def add_retrieval_failure(pair_id: str, method: str, stage: str) -> None:
        row = proposals[(pair_id, method)]
        failures = [value for value in row.get("details", {}).get("stage_failures", [])
                    if value not in {"retrieval", stage}] + [stage]
        update(pair_id, method, failures)

    pair_ids = sorted({str(row["pair_id"]) for row in rows})
    for pair_id in pair_ids:
        # Assert every dependency carrier instead of silently treating absence as success.
        for key in ((pair_id, "decomposition_only"), (pair_id, "without_delta"),
                    (pair_id, "shuffled_delta"), (pair_id, "shuffled_rule_evidence"),
                    (pair_id, "kgcc_generated_docs_as_decisive_evidence"),
                    (pair_id, "candidate_specific_retrieval"), (pair_id, "full_deltarev")):
            if key not in proposals:
                raise ValueError(f"missing dependency proposal: {key}")
        hybrid, hypothesis, relevance = shared(pair_id)
        decomposition = proposals[(pair_id, "decomposition_only")].get("details", {})
        update(pair_id, "decomposition_only",
               (["hybrid_delta"] if hybrid else []) + (["hypotheses"] if hypothesis else [])
               + [name for name, usage in (("decomposition", decomposition.get("usage", {})),
                                            ("decomposition_control", decomposition.get("control_usage", {})))
                  if failed(usage)])

        without = proposals[(pair_id, "without_delta")]
        update(pair_id, "without_delta", (["hypotheses"] if hypothesis else [])
               + (["without_delta_relevance"] if "without_delta_relevance" in
                  without.get("details", {}).get("stage_failures", []) else [])
               + (["standard_retrieval"] if retrieval_failed(pair_id, "standard_question_retrieval") else [])
               + rule_failure(pair_id, "standard_question_retrieval", "standard_"))

        shuffled = retrievals[(pair_id, "shuffled_delta")]
        donor = str(shuffled.get("source_pair_id", ""))
        if not donor or (donor,) not in deltas:
            raise ValueError(f"missing shuffled donor delta: {pair_id}")
        donor_hybrid, donor_hypothesis, _ = shared(donor)
        shuffled_old = stages(pair_id, "shuffled_delta")
        update(pair_id, "shuffled_delta", (["hypotheses"] if hypothesis else [])
               + (["donor_hybrid_delta"] if donor_hybrid else [])
               + (["shuffled_retrieval"] if shuffled.get("errors", []) else [])
               + (["shuffled_relevance"] if "shuffled_relevance" in shuffled_old else [])
               + rule_failure(pair_id, "shuffled_delta", "shuffled_"))

        update(pair_id, "shuffled_rule_evidence",
               (["hypotheses"] if hypothesis else []) + (["relevance"] if relevance else [])
               + (["donor_hybrid_delta"] if donor_hybrid else [])
               + (["donor_hypotheses"] if donor_hypothesis else [])
               + (["donor_triangular_retrieval"] if retrieval_failed(
                   donor, "triangular_decision_change_retrieval") else [])
               + rule_failure(donor, "triangular_decision_change_retrieval",
                              "donor_triangular_", verifier=False)
               + rule_failure(pair_id, "shuffled_rule_evidence", "shuffled_evidence_",
                              extractor=False))

        update(pair_id, "kgcc_generated_docs_as_decisive_evidence",
               (["hybrid_delta"] if hybrid else []) + (["hypotheses"] if hypothesis else [])
               + (["relevance"] if relevance else [])
               + rule_failure(pair_id, "kgcc_generated_decisive", "kgcc_"))

        retrieval_consumers = {
            "standard_question_retrieval": ("standard_question_retrieval",
                                             "evidence_verifier_with_standard_retrieval"),
            "ea_rag_style_retrieval": ("ea_rag_style_retrieval",
                                        "evidence_verifier_with_ea_rag_retrieval"),
            "candidate_specific_retrieval": ("candidate_specific_retrieval",),
            "delta_only_retrieval": ("delta_only_retrieval",),
            "triangular_decision_change_retrieval": (
                "triangular_decision_change_retrieval", "full_deltarev",
                "without_alternative_support_requirement", "without_entailment_check",
                "without_patient_applicability_check"),
            "refute_only_retrieval": ("refute_only_retrieval",),
            "without_baseline_answer_in_query": ("without_baseline_answer_in_query",),
            "without_preserve_evidence": ("without_preserve_evidence",),
        }
        for retrieval_method, consumers in retrieval_consumers.items():
            if retrieval_failed(pair_id, retrieval_method):
                for consumer in consumers:
                    add_retrieval_failure(pair_id, consumer, retrieval_method)
    return list(proposals.values())


def merge_proposals(inputs: list[Path], output: Path) -> int:
    values: dict[tuple[Any, ...], dict[str, Any]] = {}
    for path in inputs:
        for row in corrected_proposal_rows(path):
            key = (row.get("pair_id"), row.get("method"))
            if None in key or key in values:
                raise ValueError(f"invalid or duplicate merged proposal key: {key}")
            values[key] = row
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(values[key], ensure_ascii=False, sort_keys=True) + "\n"
                              for key in sorted(values)), encoding="utf-8")
    return len(values)


def shard_paths(output_dir: Path, output: Path | None, index: int, count: int) -> tuple[Path, Path | None]:
    if count == 1:
        return output_dir, output
    shard = f"shard-{index:03d}-of-{count:03d}"
    return output_dir / shard, (output.parent / shard / output.name if output else None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--raw", type=Path, required=True)
    prepare.add_argument("--inference", type=Path, required=True)
    prepare.add_argument("--gold", type=Path, required=True)
    prepare.add_argument("--exclude-gold", type=Path)
    prepare.add_argument("--seed", type=int, default=13)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--inference", type=Path, required=True)
    baseline.add_argument("--output-dir", type=Path, required=True)
    baseline.add_argument("--output", type=Path, required=True)
    baseline.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    baseline.add_argument("--shard-index", type=int, default=0)
    baseline.add_argument("--shard-count", type=int, default=1)
    run = sub.add_parser("run")
    run.add_argument("--inference", type=Path, required=True)
    run.add_argument("--baseline", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    run.add_argument("--shard-index", type=int, default=0)
    run.add_argument("--shard-count", type=int, default=1)
    merge = sub.add_parser("merge")
    merge.add_argument("--inputs", type=Path, nargs="+", required=True)
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--kind", choices=("baseline", "proposals", "deltas", "retrieval", "rules"), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        print(json.dumps({**prepare_pilot(args.raw, args.inference, args.gold, args.exclude_gold, args.seed),
                          "availability": UNAVAILABLE}, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "merge":
        keys = {"baseline": ("pair_id",), "proposals": ("pair_id", "method"),
                "deltas": ("pair_id",), "retrieval": ("pair_id", "artifact_type"),
                "rules": ("pair_id", "retrieval_method")}[args.kind]
        count = (merge_proposals(args.inputs, args.output) if args.kind == "proposals"
                 else merge_jsonl(args.inputs, args.output, keys, args.kind))
        print(f"merged rows={count}")
        return 0
    pairs = read_jsonl(args.inference)
    gate_b = _load_script("deltarev_gate_b_cli", ROOT / "scripts" / "run_gate_b.py")
    if args.command == "baseline":
        if not 0 <= args.shard_index < args.shard_count:
            raise ValueError("invalid shard")
        pairs = [row for index, row in enumerate(pairs) if index % args.shard_count == args.shard_index]
        output_dir, output = shard_paths(args.output_dir, args.output, args.shard_index, args.shard_count)
        backend = gate_b.VLLMBackend(args.model, 32768, .5)
        print(f"baseline rows={run_baseline(pairs, output_dir, output, backend)}")
        return 0
    if not 0 <= args.shard_index < args.shard_count:
        raise ValueError("invalid shard")
    pairs = [row for index, row in enumerate(pairs) if index % args.shard_count == args.shard_index]
    output_dir, _ = shard_paths(args.output_dir, None, args.shard_index, args.shard_count)
    baselines = {row["pair_id"]: row for row in read_jsonl(args.baseline)}
    missing = [row["pair_id"] for row in pairs if row["pair_id"] not in baselines]
    if missing:
        raise ValueError(f"missing baseline pairs: {missing[:3]}")
    backend = gate_b.VLLMBackend(args.model, 32768, .5)
    retriever = gate_b.LocalRetriever()
    try:
        print(f"proposal rows={run_pairs(pairs, baselines, output_dir, backend, retriever)}")
    finally:
        retriever.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
