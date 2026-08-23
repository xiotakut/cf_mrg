#!/usr/bin/env python3
"""Run the balanced60 Gate-D M3--M11 ablations without gold access."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import run_gate_b as gb


PROMPTS = SCRIPT_DIR.parent / "prompts"
METHODS = tuple(f"M{number}" for number in range(3, 12))
QUERY_KINDS = (
    "applicability and indications",
    "immediate effects and observations",
    "time course thresholds and follow-up",
    "contraindications harms and conflicting evidence",
)


def load_items(inference_path: Path, reference_path: Path, reference_sha256: str) -> list[dict[str, Any]]:
    if gb.sha256_file(reference_path) != reference_sha256:
        raise ValueError("balanced60 reference SHA-256 mismatch")
    ids = json.loads(reference_path.read_text(encoding="utf-8"))
    if not isinstance(ids, list) or len(ids) != 60 or len(set(ids)) != 60:
        raise ValueError("balanced60 reference must contain 60 unique item IDs")
    inference = {row["item_id"]: row for row in gb.read_jsonl(inference_path)}
    missing = set(ids) - set(inference)
    if missing:
        raise ValueError(f"balanced60 IDs missing from inference: {sorted(missing)[:3]}")
    return [inference[item_id] for item_id in ids]


def require_rows(path: Path, items: list[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"{label} artifact is required: {path}")
    rows = gb.read_jsonl(path)
    by_id = {row["item_id"]: row for row in rows}
    expected = {item["item_id"] for item in items}
    missing, extra = expected - set(by_id), set(by_id) - expected
    if len(rows) != len(items) or missing or extra:
        raise ValueError(
            f"{label} must cover balanced60 exactly once; "
            f"rows={len(rows)}, unique={len(by_id)}, missing={sorted(missing)[:3]}, extra={sorted(extra)[:3]}"
        )
    return [by_id[item["item_id"]] for item in items]


def last_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    found, found_end, found_start = None, -1, len(text)
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        absolute_end = index + end
        if isinstance(value, dict) and (absolute_end > found_end or (absolute_end == found_end and index < found_start)):
            found, found_end, found_start = value, absolute_end, index
    return found


def empty_state() -> dict[str, Any]:
    return {
        "demographics": [], "conditions": [], "symptoms": [], "measurements": [],
        "temporal_facts": [], "completed_interventions": [], "medications": [],
        "contraindications_or_risks": [], "explicit_unknowns": [],
    }


def candidates_for(item: dict[str, Any], parsed: dict[str, Any]) -> list[dict[str, str]]:
    task = str(item.get("task_family") or "")
    fallback_type = (
        "diagnosis" if item["dataset"] == "medeinst" or "diagnosis" in task
        else "outcome" if item["dataset"] == "medcounterfact" or "forecast" in task or "response" in task
        else "action" if "intervention" in task or "medication" in task
        else "rule_judgment" if item["dataset"] in {"cpv", "remedqa"} or "invariance" in task
        else "action"
    )
    options = item.get("options")
    if item["dataset"] == "clir" and not options:
        options = gb.embedded_clir_options(item["question"])
    if isinstance(options, dict) and options:
        return [{"id": str(key), "text": str(value), "type": fallback_type} for key, value in list(options.items())[:5]]
    if item["dataset"] == "medcounterfact":
        return [{"id": key, "text": key, "type": "outcome"} for key in ("higher", "lower", "no difference")]
    raw = parsed.get("candidate_actions_or_hypotheses") or []
    result = []
    for index, candidate in enumerate(raw):
        if not isinstance(candidate, dict) or not str(candidate.get("text", "")).strip():
            continue
        text = str(candidate["text"]).strip()
        if item["dataset"] == "medeinst" and (
            str(candidate.get("type", "")).lower() != "diagnosis"
            or text == "..." or "|" in text
            or re.search(r"\b(order|investigate|investigation|test|workup|treat|treatment|management|action)\b", text, re.I)
        ):
            continue
        if text.casefold() in {row["text"].casefold() for row in result}:
            continue
        candidate_id = f"H{len(result)}" if item["dataset"] == "medeinst" else str(candidate.get("id") or f"H{index}")
        if candidate_id in {row["id"] for row in result}:
            continue
        result.append({"id": candidate_id, "text": text, "type": str(candidate.get("type") or fallback_type)})
        if len(result) == 5:
            break
    if item["dataset"] == "medeinst" and len(result) != 5:
        raise ValueError(f"MedEInst requires exactly 5 diagnosis candidates: {item.get('item_id', '<unknown>')} got {len(result)}")
    return result or [{"id": "H0", "text": "most likely diagnosis", "type": fallback_type}]


def prompt_text(name: str, replacements: dict[str, str]) -> str:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace("{" + key + "}", value)
    return text


def usage(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt_tokens": output["prompt_tokens"],
        "completion_tokens": output["completion_tokens"],
        "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
        "finish_reason": output["finish_reason"],
    }


def stage_input_limit(reader_input_limit: int, output_tokens: int) -> int:
    return max(1, reader_input_limit + 512 - output_tokens)


def run_state(items: list[dict[str, Any]], output_path: Path, backend: Any, batch_size: int, max_input: int) -> int:
    cached = {row["item_id"] for row in gb.read_jsonl(output_path)} if output_path.exists() else set()
    pending = [item for item in items if item["item_id"] not in cached]
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        prompts = []
        for item in batch:
            options = item.get("options")
            value = prompt_text("02_state_change_action_extractor.md", {
                "question": str(item["question"]),
                "options_or_null": json.dumps(options, ensure_ascii=False) if options else "null",
                "context_or_null": gb._evidence_text(item) or "null",
            })
            if item["dataset"] == "medeinst":
                value += (
                    "\n\nThis benchmark asks for the most likely diagnosis. "
                    "candidate_actions_or_hypotheses must contain exactly 5 distinct concise plausible diagnosis labels, "
                    "with IDs H0 through H4 and type diagnosis. Do not rank or select them. "
                    "Do not output actions, investigations, treatments, schema placeholders, or ellipses. "
                    "Keep every state list concise and complete the entire JSON response in under 900 tokens."
                )
            prompts.append(gb._stage_chat(backend.tokenizer, value, stage_input_limit(max_input, 1024)))
        outputs = backend.generate(prompts, 1024)
        rows = []
        for item, output in zip(batch, outputs):
            parsed = last_json_object(output["raw_response"]) or {}
            rows.append({
                "item_id": item["item_id"], "dataset": item["dataset"],
                "state": parsed.get("current_state") if isinstance(parsed.get("current_state"), dict) else empty_state(),
                "decision_goal": str(parsed.get("decision_goal") or item["question"]),
                "requested_transition_target": str(parsed.get("requested_transition_target") or "evidence_conclusion"),
                "candidates": candidates_for(item, parsed),
                "raw_response": output["raw_response"], "usage": usage(output),
            })
        gb.append_rows(output_path, rows)
    return len(pending)


def action_queries(item: dict[str, Any], candidate: dict[str, str]) -> list[str]:
    base = f"{item['question']}\nCandidate: {candidate['text']}"
    return [f"{base}\nEvidence focus: {kind}" for kind in QUERY_KINDS]


def round_robin_context(candidate_rows: list[dict[str, Any]], count: int = 5) -> list[dict[str, Any]]:
    streams = []
    for candidate in candidate_rows:
        query_docs = [query["documents"] for query in candidate["queries"]]
        streams.append([doc for rank in range(max(map(len, query_docs), default=0)) for docs in query_docs if rank < len(docs) for doc in [docs[rank]]])
    chosen, seen, positions = [], set(), [0] * len(streams)
    while len(chosen) < count:
        progressed = False
        for index, stream in enumerate(streams):
            while positions[index] < len(stream):
                document = stream[positions[index]]
                positions[index] += 1
                key = str(document.get("id") or document.get("contents"))
                if key in seen:
                    continue
                seen.add(key)
                chosen.append(document)
                progressed = True
                break
            if len(chosen) == count:
                break
        if not progressed:
            break
    return chosen


def run_retrieval(items: list[dict[str, Any]], output_dir: Path, retriever: Any | None = None) -> int:
    states = {row["item_id"]: row for row in require_rows(output_dir / "state_action.jsonl", items, "state_action")}
    path = output_dir / "action_retrieval.jsonl"
    cached = {row["item_id"]: row for row in gb.read_jsonl(path)} if path.exists() else {}
    pending = [item for item in items if item["item_id"] not in cached]
    owned = retriever is None and any(item["dataset"] != "medcounterfact" for item in pending)
    if owned:
        retriever = gb.LocalRetriever()
    try:
        for item in pending:
            candidate_rows = []
            for candidate in states[item["item_id"]]["candidates"]:
                queries = action_queries(item, candidate)
                if item["dataset"] == "medcounterfact":
                    documents = gb.fixed_documents(item, 5)
                    query_rows = [{"kind": kind, "query": query, "documents": documents} for kind, query in zip(QUERY_KINDS, queries)]
                else:
                    query_rows = [{"kind": kind, "query": query, "documents": retriever.retrieve(query, 5)} for kind, query in zip(QUERY_KINDS, queries)]
                candidate_rows.append({"candidate_id": candidate["id"], "queries": query_rows})
            row = {"item_id": item["item_id"], "dataset": item["dataset"], "policy": "fixed_only" if item["dataset"] == "medcounterfact" else "external", "candidates": candidate_rows}
            gb.append_rows(path, [row]); cached[item["item_id"]] = row
    finally:
        if owned:
            retriever.close()
    context_path = output_dir / "action_context.jsonl"
    contexts = {row["item_id"]: row for row in gb.read_jsonl(context_path)} if context_path.exists() else {}
    for item in items:
        if item["item_id"] in contexts:
            continue
        documents = round_robin_context(cached[item["item_id"]]["candidates"])
        if len(documents) != 5:
            raise ValueError(f"action context requires 5 documents: {item['item_id']}")
        gb.append_rows(context_path, [{"item_id": item["item_id"], "dataset": item["dataset"], "documents": documents}])
    return len(pending)


CARD_FIELDS = (
    "applicability", "triggering_conditions", "failed_or_absent_conditions", "exceptions",
    "immediate_observations", "next_state_changes", "future_threshold_or_interval", "benefits",
    "harms_or_constraints", "monitoring_or_next_action", "evidence_ids", "contradictions",
    "uncertainty_reasons", "unsupported_claims", "rollout_valid",
)


def fallback_card(candidate: dict[str, str], evidence_ids: list[str]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["id"], "action": candidate["text"], "applicability": "unknown",
        "triggering_conditions": [], "failed_or_absent_conditions": [], "exceptions": [],
        "immediate_observations": [], "next_state_changes": [], "future_threshold_or_interval": "not_required",
        "benefits": [], "harms_or_constraints": [], "monitoring_or_next_action": [],
        "evidence_ids": evidence_ids, "contradictions": [], "uncertainty_reasons": ["model output unavailable"],
        "unsupported_claims": [], "rollout_valid": False,
    }


def parsed_card(raw: str, candidate: dict[str, str], evidence_ids: list[str]) -> dict[str, Any]:
    fallback = fallback_card(candidate, evidence_ids)
    parsed = last_json_object(raw) or {}
    for field in CARD_FIELDS:
        if field in parsed:
            fallback[field] = parsed[field]
    fallback["candidate_id"] = candidate["id"]
    valid_ids = [value for value in fallback.get("evidence_ids", []) if value in evidence_ids]
    fallback["evidence_ids"] = valid_ids or evidence_ids
    return fallback


def complete_card_response(raw: str) -> bool:
    parsed = last_json_object(raw)
    return isinstance(parsed, dict) and "candidate_id" in parsed and all(field in parsed for field in CARD_FIELDS)


def card_usage(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "prompt_tokens": sum(output["prompt_tokens"] for output in outputs),
        "completion_tokens": sum(output["completion_tokens"] for output in outputs),
        "total_tokens": sum(output["prompt_tokens"] + output["completion_tokens"] for output in outputs),
        "finish_reasons": [output["finish_reason"] for output in outputs],
    }


def finalize_cards(
    raw_responses: list[str],
    candidates: list[dict[str, str]],
    evidence_ids: list[list[str]],
    initial_usage: dict[str, Any],
    backend: Any,
    max_input: int,
) -> tuple[list[dict[str, Any]], list[str], list[int], dict[str, Any]]:
    invalid = [index for index, raw in enumerate(raw_responses) if not complete_card_response(raw)]
    retry_outputs = []
    if invalid:
        prompts = []
        for index in invalid:
            schema = fallback_card(candidates[index], evidence_ids[index])
            prompts.append(gb._stage_chat(backend.tokenizer, (
                "Repair the response into one complete JSON object matching the supplied schema exactly. "
                "Do not add unsupported facts; use unknown, empty lists, false, or not_required for missing values. "
                "Return JSON only.\n\n"
                f"Required schema and allowed evidence IDs:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
                f"Response to repair:\n{raw_responses[index]}"
            ), stage_input_limit(max_input, 2048)))
        retry_outputs = backend.generate(prompts, 2048)
        for index, output in zip(invalid, retry_outputs):
            raw_responses[index] = output["raw_response"]
    still_invalid = [index for index, raw in enumerate(raw_responses) if not complete_card_response(raw)]
    if still_invalid:
        raise ValueError(f"card JSON repair failed for candidate indexes: {still_invalid}")
    retry_counts = [int(index in invalid) for index in range(len(raw_responses))]
    cards = []
    for raw, candidate, ids, retry_count in zip(raw_responses, candidates, evidence_ids, retry_counts):
        card = parsed_card(raw, candidate, ids)
        card["retry_count"] = retry_count
        cards.append(card)
    retry_usage = card_usage(retry_outputs)
    combined = {
        "prompt_tokens": initial_usage["prompt_tokens"] + retry_usage["prompt_tokens"],
        "completion_tokens": initial_usage["completion_tokens"] + retry_usage["completion_tokens"],
        "total_tokens": initial_usage["total_tokens"] + retry_usage["total_tokens"],
        "finish_reasons": [*initial_usage["finish_reasons"], *retry_usage["finish_reasons"]],
    }
    return cards, raw_responses, retry_counts, combined


def evidence_with_ids(documents: list[dict[str, Any]]) -> tuple[str, list[str]]:
    ids = [f"D{index}" for index in range(len(documents))]
    return "\n\n".join(f"{key}: {document['contents']}" for key, document in zip(ids, documents)), ids


def run_cards(items: list[dict[str, Any]], output_dir: Path, backend: Any, max_input: int) -> int:
    states = {row["item_id"]: row for row in require_rows(output_dir / "state_action.jsonl", items, "state_action")}
    retrievals = {row["item_id"]: row for row in require_rows(output_dir / "action_retrieval.jsonl", items, "action_retrieval")}
    path = output_dir / "grounded_cards.jsonl"
    previous_path = output_dir / "grounded_cards.pre-schema-retry.jsonl"
    previous = {row["item_id"]: row for row in gb.read_jsonl(previous_path)} if previous_path.exists() else {}
    done = {row["item_id"] for row in gb.read_jsonl(path)} if path.exists() else set()
    pending = [item for item in items if item["item_id"] not in done]
    for item in pending:
        state = states[item["item_id"]]
        by_candidate = {row["candidate_id"]: row for row in retrievals[item["item_id"]]["candidates"]}
        evidence_sets = [
            evidence_with_ids(round_robin_context([by_candidate[candidate["id"]]]))
            for candidate in state["candidates"]
        ]
        prompts = [gb._stage_chat(backend.tokenizer, prompt_text("04_rule_transition_model.md", {
            "state_json": json.dumps(state["state"], ensure_ascii=False),
            "candidate_json": json.dumps(candidate, ensure_ascii=False),
            "evidence_with_ids": evidence,
            "task_family": str(item.get("task_family") or item["dataset"]),
        }), stage_input_limit(max_input, 1024)) for candidate, (evidence, _) in zip(state["candidates"], evidence_sets)]
        if item["item_id"] in previous:
            old = previous[item["item_id"]]
            raw_responses = list(old["raw_responses"])
            initial_usage = old["usage"]
        else:
            outputs = backend.generate(prompts, 1024)
            raw_responses = [output["raw_response"] for output in outputs]
            initial_usage = card_usage(outputs)
        cards, raw_responses, retry_counts, final_usage = finalize_cards(
            raw_responses, state["candidates"], [ids for _, ids in evidence_sets], initial_usage, backend, max_input
        )
        gb.append_rows(path, [{"item_id": item["item_id"], "dataset": item["dataset"], "cards": cards,
            "raw_responses": raw_responses, "retry_counts": retry_counts, "usage": final_usage}])
    return len(pending)


def run_parametric_cards(items: list[dict[str, Any]], states: dict[str, dict[str, Any]], output_dir: Path, backend: Any, max_input: int) -> int:
    path = output_dir / "parametric_cards.jsonl"
    done = {row["item_id"] for row in gb.read_jsonl(path)} if path.exists() else set()
    pending = [item for item in items if item["item_id"] not in done]
    template = (PROMPTS / "04_rule_transition_model.md").read_text(encoding="utf-8").replace(
        "1. Cite evidence IDs for every nontrivial claim.",
        "1. PARAMETRIC ABLATION: use model prior knowledge only; no retrieved or fixed evidence is supplied. Always return evidence_ids as [].",
    )
    for item in pending:
        state = states[item["item_id"]]
        prompts = []
        for candidate in state["candidates"]:
            value = template
            for key, replacement in {
                "state_json": json.dumps(state["state"], ensure_ascii=False),
                "candidate_json": json.dumps(candidate, ensure_ascii=False),
                "evidence_with_ids": "No retrieved or fixed evidence is supplied.",
                "task_family": str(item.get("task_family") or item["dataset"]),
            }.items():
                value = value.replace("{" + key + "}", replacement)
            prompts.append(gb._stage_chat(backend.tokenizer, value, stage_input_limit(max_input, 1024)))
        outputs = backend.generate(prompts, 1024)
        cards, raw_responses, retry_counts, final_usage = finalize_cards(
            [output["raw_response"] for output in outputs], state["candidates"], [[] for _ in outputs], card_usage(outputs), backend, max_input
        )
        gb.append_rows(path, [{"item_id": item["item_id"], "dataset": item["dataset"], "cards": cards,
            "raw_responses": raw_responses, "retry_counts": retry_counts, "usage": final_usage}])
    return len(pending)


SCORE_FIELDS = (
    "candidate_id", "precondition_fit", "state_consistency", "effect_consistency",
    "evidence_support", "harm_or_contradiction_penalty", "uncertainty_penalty", "total",
)


def complete_comparator_response(raw: str, candidates: list[dict[str, str]]) -> bool:
    parsed = last_json_object(raw)
    if not isinstance(parsed, dict) or not all(key in parsed for key in ("candidate_scores", "selected_candidate_ids", "causal_determinants", "comparison_valid")):
        return False
    valid = {candidate["id"] for candidate in candidates}
    scores = parsed["candidate_scores"]
    selected = parsed["selected_candidate_ids"]
    return (
        isinstance(scores, list) and len(scores) == len(valid)
        and all(isinstance(row, dict) and all(field in row for field in SCORE_FIELDS) for row in scores)
        and {str(row["candidate_id"]) for row in scores} == valid
        and isinstance(selected, list) and bool(selected)
        and {str(value) for value in selected}.issubset(valid)
        and isinstance(parsed["causal_determinants"], list)
        and isinstance(parsed["comparison_valid"], bool)
    )


def normalize_comparator(raw: str, candidates: list[dict[str, str]]) -> dict[str, Any]:
    if not complete_comparator_response(raw, candidates):
        raise ValueError("incomplete comparator response")
    parsed = last_json_object(raw)
    return {key: parsed[key] for key in ("candidate_scores", "selected_candidate_ids", "causal_determinants", "comparison_valid")}


def comparator_prompt(item: dict[str, Any], state: dict[str, Any], cards: list[dict[str, Any]]) -> str:
    return prompt_text("05_counterfactual_comparator.md", {
        "question": str(item["question"]),
        "options_or_null": json.dumps(item.get("options"), ensure_ascii=False),
        "state_json": json.dumps(state, ensure_ascii=False),
        "transition_cards": json.dumps(cards, ensure_ascii=False),
    })


def run_comparators(items: list[dict[str, Any]], states: dict[str, dict[str, Any]], cards: dict[str, list[dict[str, Any]]], path: Path, backend: Any, batch_size: int, max_input: int) -> int:
    done = {row["item_id"] for row in gb.read_jsonl(path)} if path.exists() else set()
    previous_path = path.with_name(path.stem + ".pre-schema-retry.jsonl")
    previous = {row["item_id"]: row for row in gb.read_jsonl(previous_path)} if previous_path.exists() else {}
    pending = [item for item in items if item["item_id"] not in done]
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        fresh = [item for item in batch if item["item_id"] not in previous]
        outputs = backend.generate([gb._stage_chat(backend.tokenizer, comparator_prompt(item, states[item["item_id"]]["state"], cards[item["item_id"]]), stage_input_limit(max_input, 1024)) for item in fresh], 1024) if fresh else []
        generated = {item["item_id"]: output for item, output in zip(fresh, outputs)}
        raw = {item["item_id"]: previous[item["item_id"]]["raw_response"] if item["item_id"] in previous else generated[item["item_id"]]["raw_response"] for item in batch}
        initial_usage = {item["item_id"]: previous[item["item_id"]]["usage"] if item["item_id"] in previous else usage(generated[item["item_id"]]) for item in batch}
        retry_items = [item for item in batch if not complete_comparator_response(raw[item["item_id"]], states[item["item_id"]]["candidates"])]
        retry_outputs = backend.generate([gb._stage_chat(backend.tokenizer, (
            comparator_prompt(item, states[item["item_id"]]["state"], cards[item["item_id"]])
            + "\n\nRetry instruction: Re-run the complete comparison from the state and cards above. Return compact JSON only. "
            "candidate_scores must contain exactly one full score row for every required candidate ID; "
            "selected_candidate_ids is required, nonempty, and contains only required IDs; causal_determinants must be a list "
            "and comparison_valid a boolean. Do not use option position or a first-candidate fallback.\n"
            f"Required candidate IDs: {[candidate['id'] for candidate in states[item['item_id']]['candidates']]}"
        ), stage_input_limit(max_input, 2048)) for item in retry_items], 2048) if retry_items else []
        retry_by_id = {item["item_id"]: output for item, output in zip(retry_items, retry_outputs)}
        for item in retry_items:
            raw[item["item_id"]] = retry_by_id[item["item_id"]]["raw_response"]
        second_retry_items = [item for item in retry_items if not complete_comparator_response(raw[item["item_id"]], states[item["item_id"]]["candidates"])]
        second_retry_outputs = backend.generate([gb._stage_chat(backend.tokenizer, (
            comparator_prompt(item, states[item["item_id"]]["state"], cards[item["item_id"]])
            + "\n\nFinal retry instruction: Re-run the complete comparison. Return one compact JSON object only. "
            "candidate_scores must contain exactly one full score row for every required candidate ID; "
            "selected_candidate_ids is required, nonempty, and contains only required IDs; set causal_determinants to []; "
            "comparison_valid must be a boolean. Do not include prose.\n"
            f"Required candidate IDs: {[candidate['id'] for candidate in states[item['item_id']]['candidates']]}"
        ), stage_input_limit(max_input, 3072)) for item in second_retry_items], 3072) if second_retry_items else []
        second_retry_by_id = {item["item_id"]: output for item, output in zip(second_retry_items, second_retry_outputs)}
        for item in second_retry_items:
            raw[item["item_id"]] = second_retry_by_id[item["item_id"]]["raw_response"]
        failed = [item["item_id"] for item in batch if not complete_comparator_response(raw[item["item_id"]], states[item["item_id"]]["candidates"])]
        if failed:
            raise ValueError(f"comparator JSON repair failed: {failed}")
        rows = []
        for item in batch:
            item_id = item["item_id"]
            retry_output = second_retry_by_id.get(item_id) or retry_by_id.get(item_id)
            row_usage = dict(initial_usage[item_id])
            for extra_output in (retry_by_id.get(item_id), second_retry_by_id.get(item_id)):
                if not extra_output:
                    continue
                extra = usage(extra_output)
                for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                    row_usage[key] += extra[key]
                row_usage["finish_reason"] = extra["finish_reason"]
            rows.append({"item_id": item_id, "dataset": item["dataset"], "comparator": normalize_comparator(raw[item_id], states[item_id]["candidates"]), "raw_response": raw[item_id], "retry_count": int(item_id in retry_by_id) + int(item_id in second_retry_by_id), "usage": row_usage})
        gb.append_rows(path, rows)
    return len(pending)


def project_cards(cards: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "applicability":
        fields = ("candidate_id", "action", "applicability", "triggering_conditions", "failed_or_absent_conditions", "exceptions", "contradictions", "evidence_ids")
    elif mode == "effect":
        fields = ("candidate_id", "action", "immediate_observations", "next_state_changes", "future_threshold_or_interval", "benefits", "harms_or_constraints", "monitoring_or_next_action", "evidence_ids", "rollout_valid")
    else:
        return cards
    return [{key: card.get(key) for key in fields} for card in cards]


def shuffled_cards(item_id: str, cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(cards) < 2:
        return [dict(card) for card in cards]
    shift = random.Random(int(hashlib.sha256(f"13:{item_id}".encode()).hexdigest(), 16)).randrange(1, len(cards))
    order = [(index + shift) % len(cards) for index in range(len(cards))]
    bundle = ("immediate_observations", "next_state_changes", "future_threshold_or_interval", "benefits", "harms_or_constraints", "monitoring_or_next_action", "evidence_ids")
    result = []
    for target, source in enumerate(order):
        row = dict(cards[target])
        for field in bundle:
            row[field] = cards[source].get(field)
        row["shuffle_source_candidate_id"] = cards[source]["candidate_id"]
        result.append(row)
    return result


def artifact_document(label: str, value: Any) -> dict[str, str]:
    return {"contents": f"{label}:\n{json.dumps(value, ensure_ascii=False, sort_keys=True)}"}


def state_action_document(row: dict[str, Any]) -> dict[str, str]:
    return artifact_document("Extracted state and actions", {
        "state": row["state"],
        "decision_goal": row["decision_goal"],
        "requested_transition_target": row["requested_transition_target"],
        "candidates": row["candidates"],
    })


def run_m4_reasoning(items: list[dict[str, Any]], states: dict[str, dict[str, Any]], grounded: dict[str, dict[str, Any]], m9: dict[str, dict[str, Any]], base: dict[str, list[dict[str, Any]]], output_dir: Path, backend: Any, batch_size: int, max_input: int) -> int:
    path = output_dir / "M4.reasoning.jsonl"
    done = {row["item_id"] for row in gb.read_jsonl(path)} if path.exists() else set()
    pending = [item for item in items if item["item_id"] not in done]
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        targets, prompts = [], []
        for item in batch:
            key = item["item_id"]
            target = states[key]["usage"]["completion_tokens"] + grounded[key]["usage"]["completion_tokens"] + m9[key]["usage"]["completion_tokens"]
            targets.append(max(1, target))
            prompts.append(gb._stage_chat(backend.tokenizer, (
                "Generate a computation-matched reasoning control for the following medical question. "
                "Do not construct a transition card, use guideline text, predict the answer from option position, or provide a final answer. "
                "Spend the configured output budget on concise question analysis only.\n\n"
                f"Question:\n{item['question']}\n\nOptions:\n{json.dumps(item.get('options'), ensure_ascii=False)}\n\n"
                f"Base evidence:\n" + "\n\n".join(document.get("contents", "") for document in base[key]) + "\n\n"
                f"Configured output-token budget: {target}"
            ), stage_input_limit(max_input, target)))
        outputs = backend.generate(prompts, targets, ignore_eos=True)
        rows = []
        for item, target, output in zip(batch, targets, outputs):
            if output["completion_tokens"] != target:
                raise ValueError(f"M4 reasoning token mismatch for {item['item_id']}: {output['completion_tokens']} != {target}")
            rows.append({"item_id": item["item_id"], "dataset": item["dataset"], "target_completion_tokens": target, "raw_response": output["raw_response"], "usage": usage(output)})
        gb.append_rows(path, rows)
    return len(pending)


def prepare_run_artifacts(items: list[dict[str, Any]], output_dir: Path, backend: Any, batch_size: int, max_input: int) -> tuple[dict[str, Any], ...]:
    states = {row["item_id"]: row for row in require_rows(output_dir / "state_action.jsonl", items, "state_action")}
    contexts = {row["item_id"]: row["documents"] for row in require_rows(output_dir / "action_context.jsonl", items, "action_context")}
    base = {row["item_id"]: row["documents"] for row in require_rows(output_dir / "M2.rerank.jsonl", items, "M2.rerank")}
    run_cards(items, output_dir, backend, max_input)
    grounded_rows = {row["item_id"]: row for row in require_rows(output_dir / "grounded_cards.jsonl", items, "grounded_cards")}
    grounded = {key: row["cards"] for key, row in grounded_rows.items()}
    run_comparators(items, states, grounded, output_dir / "M9.comparator.jsonl", backend, batch_size, max_input)
    m9 = {row["item_id"]: row for row in require_rows(output_dir / "M9.comparator.jsonl", items, "M9 comparator")}
    run_m4_reasoning(items, states, grounded_rows, m9, base, output_dir, backend, batch_size, max_input)
    m4 = {row["item_id"]: row for row in require_rows(output_dir / "M4.reasoning.jsonl", items, "M4 reasoning")}
    run_parametric_cards(items, states, output_dir, backend, max_input)
    parametric_rows = {row["item_id"]: row for row in require_rows(output_dir / "parametric_cards.jsonl", items, "parametric_cards")}
    parametric = {key: row["cards"] for key, row in parametric_rows.items()}
    run_comparators(items, states, parametric, output_dir / "M10.comparator.jsonl", backend, batch_size, max_input)
    m10 = {row["item_id"]: row for row in require_rows(output_dir / "M10.comparator.jsonl", items, "M10 comparator")}
    shuffle_path = output_dir / "M11.shuffle.jsonl"
    shuffled_rows = {row["item_id"]: row for row in gb.read_jsonl(shuffle_path)} if shuffle_path.exists() else {}
    for item in items:
        if item["item_id"] not in shuffled_rows:
            row = {"item_id": item["item_id"], "dataset": item["dataset"], "cards": shuffled_cards(item["item_id"], grounded[item["item_id"]])}
            gb.append_rows(shuffle_path, [row]); shuffled_rows[item["item_id"]] = row
    shuffled = {key: row["cards"] for key, row in shuffled_rows.items()}
    run_comparators(items, states, shuffled, output_dir / "M11.comparator.jsonl", backend, batch_size, max_input)
    m11 = {row["item_id"]: row for row in require_rows(output_dir / "M11.comparator.jsonl", items, "M11 comparator")}
    return states, contexts, base, grounded, m4, m9, parametric, m10, shuffled, m11


def run_methods(items: list[dict[str, Any]], output_dir: Path, backend: Any, methods: tuple[str, ...], batch_size: int, max_input: int, max_new: int) -> dict[str, int]:
    states, contexts, base, grounded, m4, m9, parametric, m10, shuffled, m11 = prepare_run_artifacts(items, output_dir, backend, batch_size, max_input)
    documents: dict[str, dict[str, list[dict[str, Any]]]] = {method: {} for method in methods}
    for item in items:
        key = item["item_id"]
        padded_base = [*base[key], *({"contents": ""} for _ in range(max(0, 5 - len(base[key]))))]
        if "M3" in documents:
            documents["M3"][key] = [*padded_base, state_action_document(states[key])]
        if "M4" in documents:
            documents["M4"][key] = [*padded_base, {"contents": "Computation-matched extra reasoning:\n" + m4[key]["raw_response"]}]
        if "M5" in documents: documents["M5"][key] = contexts[key]
        state_doc = state_action_document(states[key])
        if "M6" in documents: documents["M6"][key] = [*contexts[key], state_doc, artifact_document("Applicability cards", project_cards(grounded[key], "applicability"))]
        if "M7" in documents: documents["M7"][key] = [*contexts[key], state_doc, artifact_document("Effect cards", project_cards(grounded[key], "effect"))]
        if "M8" in documents: documents["M8"][key] = [*contexts[key], state_doc, artifact_document("Transition cards", grounded[key])]
        if "M9" in documents: documents["M9"][key] = [*contexts[key], state_doc, artifact_document("Transition cards", grounded[key]), artifact_document("Comparator", m9[key]["comparator"])]
        if "M10" in documents: documents["M10"][key] = [*contexts[key], state_doc, artifact_document("Parametric cards", parametric[key]), artifact_document("Comparator", m10[key]["comparator"])]
        if "M11" in documents: documents["M11"][key] = [*contexts[key], state_doc, artifact_document("Shuffled transition cards", shuffled[key]), artifact_document("Comparator", m11[key]["comparator"])]
    return {method: gb.run_reader_method(method, items, documents[method], output_dir / f"{method}.jsonl", backend, batch_size, max_input, max_new) for method in methods}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--pilot-reference", type=Path, default=gb.REFERENCE)
    parser.add_argument("--reference-sha256", default=gb.REFERENCE_SHA256)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--phase", choices=("state", "retrieval", "run"), required=True)
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=METHODS)
    parser.add_argument("--model", type=Path, default=gb.MODEL)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=32768)
    parser.add_argument("--max-input-tokens", type=int, default=32256)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args(); items = load_items(args.inference, args.pilot_reference, args.reference_sha256)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    expected = json.dumps(gb.selection_payload(items, args.reference_sha256), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    selection_path = args.output_dir / "selection.json"
    if selection_path.exists() and selection_path.read_text(encoding="utf-8") != expected:
        raise SystemExit(f"selection already differs: {selection_path}")
    selection_path.write_text(expected, encoding="utf-8")
    require_rows(args.output_dir / "M2.rerank.jsonl", items, "M2.rerank")
    if args.phase == "state":
        backend = gb.VLLMBackend(args.model, args.max_model_len, args.gpu_memory_utilization)
        print(f"state generated={run_state(items, args.output_dir / 'state_action.jsonl', backend, args.batch_size, args.max_input_tokens)}", flush=True)
        require_rows(args.output_dir / "state_action.jsonl", items, "state_action")
    if args.phase == "retrieval":
        print(f"retrieval generated={run_retrieval(items, args.output_dir)}", flush=True)
        require_rows(args.output_dir / "action_retrieval.jsonl", items, "action_retrieval")
        require_rows(args.output_dir / "action_context.jsonl", items, "action_context")
    if args.phase == "run":
        require_rows(args.output_dir / "state_action.jsonl", items, "state_action")
        require_rows(args.output_dir / "action_retrieval.jsonl", items, "action_retrieval")
        require_rows(args.output_dir / "action_context.jsonl", items, "action_context")
        backend = gb.VLLMBackend(args.model, args.max_model_len, args.gpu_memory_utilization)
        for method, count in run_methods(items, args.output_dir, backend, tuple(args.methods), args.batch_size, args.max_input_tokens, args.max_new_tokens).items():
            print(f"{method} complete: generated={count}, total={len(items)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
