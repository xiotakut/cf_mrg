#!/usr/bin/env python3
"""Run the revised, gold-free counterfactual/transition experiment matrix.

The runner deliberately accepts inference records only.  Gold joins belong in
``evaluate.py`` so transition generation cannot accidentally become an oracle.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import random
import re
import sys
import unicodedata
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_gate_b as legacy


METHODS = (
    "direct", "medrgag_proxy", "decomposition_only", "candidate_retrieval",
    "direct_rank", "structured_no_transition", "equal_token_reasoning", "transition_no_comparator",
    "full_transition", "parametric_transition", "effect_shuffle",
    "full_card_shuffle", "teacher_transition",
)
TRANSITION_METHODS = {
    "transition_no_comparator", "full_transition", "parametric_transition",
    "effect_shuffle", "full_card_shuffle", "teacher_transition",
}
LEAKAGE = re.compile(
    r"\b(correct answer|gold answer|selected option|preferred candidate|option [A-J] is correct)\b",
    re.I,
)
TRANSITION_KEYS = (
    "current_state_summary", "action", "satisfied_preconditions",
    "failed_preconditions", "expected_observations", "expected_state_changes",
    "contraindications_or_harms", "monitoring_or_next_step", "uncertainties",
)
TRANSITION_ARRAY_KEYS = TRANSITION_KEYS[2:]
EFFECT_KEYS = (
    "expected_observations", "expected_state_changes", "contraindications_or_harms",
    "monitoring_or_next_step",
)


class ModelContractError(ValueError):
    def __init__(self, message: str, usage: dict[str, Any]):
        super().__init__(message)
        self.usage = usage


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return legacy.read_jsonl(path)


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    legacy.append_rows(path, rows)


def last_json(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    found, found_end, found_start = None, -1, len(text)
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        absolute_end = index + end
        if isinstance(value, dict) and (absolute_end > found_end or (absolute_end == found_end and index < found_start)):
            found, found_end, found_start = value, absolute_end, index
    if found is None:
        stripped = text.strip()
        start = stripped.find("{")
        if start >= 0:
            try:
                value = json.loads(stripped[start:] + "}")
            except json.JSONDecodeError:
                value = None
            if isinstance(value, dict):
                found = value
    return found


def task_mode(item: dict[str, Any]) -> str:
    """Route from visible metadata/text only; never from labels or pair fields."""
    dataset = str(item.get("dataset", "")).lower()
    family = str(item.get("task_family", "")).lower()
    question = str(item.get("question", "")).lower()
    if dataset == "medcounterfact":
        return "evidence_world_reasoning"
    if dataset == "medeinst" or "diagnos" in family:
        return "diagnosis_state_update"
    clir_task = str(item.get("metadata", {}).get("task") or item.get("task") or family).lower()
    if dataset == "clir" and ("t7" in clir_task or "t8" in clir_task):
        return "temporal_forecasting"
    if dataset == "clir" and "t6" in clir_task:
        return "outcome_prediction"
    if dataset == "clir" and "t10" in clir_task:
        return "action_selection"
    if dataset == "clir" and any(word in family + " " + question for word in ("forecast", "next action", "threshold", "future")):
        return "temporal_forecasting"
    if any(word in family + " " + question for word in ("outcome", "response", "observation after", "following the intervention")):
        return "outcome_prediction"
    return "action_selection"


def excluded_clir_t9(item: dict[str, Any]) -> bool:
    task = str(item.get("metadata", {}).get("task") or item.get("task") or item.get("task_family", "")).lower()
    return item.get("dataset") == "clir" and ("t9" in task or task == "clinical_timeseries_summarization")


def options_for(item: dict[str, Any]) -> dict[str, str]:
    options = item.get("options")
    if isinstance(options, dict) and options:
        return {str(key): str(value) for key, value in options.items()}
    if item.get("dataset") == "clir":
        return legacy.embedded_clir_options(str(item.get("question", "")))
    if item.get("dataset") == "medcounterfact":
        return {value: value for value in ("higher", "lower", "no difference")}
    return {}


def visible_context(item: dict[str, Any]) -> str:
    values = {
        "patient_state": item.get("patient_state") or {},
        "time_series": item.get("time_series") or [],
        "fixed_evidence": item.get("fixed_evidence") or [],
    }
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def _without_future_targets(value: Any) -> Any:
    forbidden = ("gold", "answer", "label", "target", "future", "outcome", "post_observation", "next_observation")
    if isinstance(value, dict):
        return {key: _without_future_targets(child) for key, child in value.items() if not any(word in str(key).lower() for word in forbidden)}
    if isinstance(value, list):
        return [_without_future_targets(child) for child in value]
    return value


def prediction_context(item: dict[str, Any]) -> str:
    """Context available at prediction time for option-hidden temporal modes."""
    if item.get("dataset") == "clir":
        family = str(item.get("task_family", "")).lower()
        fixed = item.get("fixed_evidence") or []
        if family == "intervention_response":
            allowed = {
                "baseline_observation", "context_end_time", "intervention_event_hour",
                "intervention_items_at_event_hour", "response_variable", "response_variable_label", "source",
            }
            fixed = [{key: value for key, value in row.items() if key in allowed} for row in fixed if isinstance(row, dict)]
            values = {"patient_state": {}, "time_series": [], "fixed_evidence": fixed, "patient_evidence_available": bool(fixed)}
        elif family == "next_value_interval_forecasting":
            allowed = {
                "anchor_time", "horizon_hours", "previous_same_variable_observation",
                "recent_visible_same_variable_observations", "target_variable",
                "target_variable_label", "source",
            }
            fixed = [{key: value for key, value in row.items() if key in allowed} for row in fixed if isinstance(row, dict)]
            values = {"patient_state": {}, "time_series": [], "fixed_evidence": fixed, "patient_evidence_available": bool(fixed)}
        else:  # CLIR t7/t10 lack an official patient-evidence payload in this repository.
            values = {"patient_state": {}, "time_series": [], "fixed_evidence": [], "patient_evidence_available": False}
        return json.dumps(values, ensure_ascii=False, sort_keys=True)
    values = {
        "patient_state": _without_future_targets(item.get("patient_state") or {}),
        "time_series": _without_future_targets(item.get("time_series") or []),
        "fixed_evidence": _without_future_targets(item.get("fixed_evidence") or []),
    }
    return json.dumps(values, ensure_ascii=False, sort_keys=True)


def safe_fixed_documents(item: dict[str, Any]) -> list[dict[str, Any]]:
    safe = json.loads(prediction_context(item)).get("fixed_evidence", [])
    return legacy.fixed_documents({"fixed_evidence": safe}, 5)


def question_stem(item: dict[str, Any]) -> str:
    text = str(item.get("question", ""))
    text = re.split(r"(?im)^\s*Options\s*:", text, maxsplit=1)[0]
    text = re.split(r"(?m)^\s*A[.)]\s+", text, maxsplit=1)[0]
    return text.strip()


def inference_stem(item: dict[str, Any]) -> str:
    text = question_stem(item)
    if item.get("dataset") == "medcounterfact":
        text = re.sub(
            r"(?i)(?:higher|lower)\s*,\s*(?:higher|lower)\s*,\s*or\s*(?:the\s*)?(?:same|no difference)",
            "a different direction", text,
        )
    return text


def evidence_slots(documents: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = [
        {"id": f"D{index + 1}", "text": str(document.get("contents", ""))}
        for index, document in enumerate(documents[:5])
    ]
    return rows + [{"id": f"D{index + 1}", "text": ""} for index in range(len(rows), 5)]


def candidate_actions(item: dict[str, Any], state: dict[str, Any]) -> list[dict[str, str]]:
    mode = task_mode(item)
    if mode == "evidence_world_reasoning":
        return [{"id": "FIXED", "text": "interpret the supplied local evidence world"}]
    if mode in {"outcome_prediction", "temporal_forecasting"}:
        action = str(state.get("fixed_action") or state.get("observed_intervention") or "action described in the question")
        return [{"id": "FIXED", "text": action}]
    options = options_for(item)
    if options:
        return [{"id": key, "text": value} for key, value in options.items()]
    hypotheses = state.get("candidate_hypotheses") or []
    result = [
        {"id": f"H{index}", "text": str(value)}
        for index, value in enumerate(hypotheses[:5]) if str(value).strip()
    ]
    if item.get("dataset") == "medeinst" and len(result) != 5:
        raise ValueError(f"MedEinst requires five diagnosis hypotheses: {item['item_id']}")
    return result or [{"id": "H0", "text": "most likely conclusion"}]


def chat(tokenizer: Any, system: str, user: str, max_input_tokens: int) -> str:
    def render(value: str) -> str:
        return tokenizer.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": value}],
            tokenize=False, add_generation_prompt=True,
        )
    rendered = render(user)
    if len(tokenizer.encode(rendered, add_special_tokens=False)) <= max_input_tokens:
        return rendered
    overhead = len(tokenizer.encode(render(""), add_special_tokens=False))
    rendered = render(legacy._truncate_head_tail(tokenizer, user, max(0, max_input_tokens - overhead)))
    if len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        raise ValueError("prompt cannot fit configured input budget")
    return rendered


def generate_json(
    backend: Any, system: str, user: str, max_input_tokens: int, max_tokens: int,
    required: tuple[str, ...] = (), validator: Any | None = None, repair_rule: str = "",
    repair_preamble: str | None = None,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    """Generate JSON with at most one semantic-preserving repair retry."""
    return generate_json_batch(
        backend, system, [user], max_input_tokens, max_tokens, required, validator, repair_rule,
        repair_preamble,
    )[0]


def generate_json_batch(
    backend: Any, system: str, users: list[str], max_input_tokens: int, max_tokens: int,
    required: tuple[str, ...] = (), validator: Any | None = None, repair_rule: str = "",
    repair_preamble: str | None = None,
) -> list[tuple[dict[str, Any], str, dict[str, Any]]]:
    input_limit = max(1, max_input_tokens + 512 - max_tokens)
    prompts = [chat(backend.tokenizer, system, user, input_limit) for user in users]
    outputs = backend.generate(prompts, max_tokens)
    parsed = [last_json(output["raw_response"]) for output in outputs]
    retries = [0] * len(users)
    invalid = lambda value: not isinstance(value, dict) or any(key not in value for key in required) or (validator is not None and not validator(value))
    bad = [index for index, value in enumerate(parsed) if invalid(value)]
    if bad:
        preamble = repair_preamble or (
            "Repair the response below into one complete JSON object. Do not add facts or change its meaning."
        )
        repair_prompts = [
            chat(
                backend.tokenizer, system,
                f"{preamble} Required keys: {list(required)}. {repair_rule} Return JSON only.\n\n"
                + outputs[index]["raw_response"],
                input_limit,
            )
            for index in bad
        ]
        repaired = backend.generate(repair_prompts, max_tokens)
        for index, value in zip(bad, repaired):
            retries[index] = 1
            parsed[index] = last_json(value["raw_response"])
            outputs[index] = {
                **value,
                "prompt_tokens": outputs[index]["prompt_tokens"] + value["prompt_tokens"],
                "completion_tokens": outputs[index]["completion_tokens"] + value["completion_tokens"],
            }
    result = []
    for value, output, retry_count in zip(parsed, outputs, retries):
        usage = {
            "prompt_tokens": output["prompt_tokens"],
            "completion_tokens": output["completion_tokens"],
            "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
            "retry_count": retry_count,
        }
        if invalid(value):
            excerpt = output.get("raw_response", "")[-2000:]
            raise ModelContractError(
                f"model failed JSON contract after one retry; required={required}; response_tail={excerpt!r}",
                usage,
            )
        result.append((value, output["raw_response"], usage))
    return result


def state_prompt(item: dict[str, Any]) -> str:
    mode = task_mode(item)
    diagnosis_rule = " For MedEinst, candidate_hypotheses must be exactly five distinct concise diagnosis labels." if item.get("dataset") == "medeinst" else ""
    return (
        "Extract only facts visible at prediction time. Do not answer or rank anything. "
        "Preserve timestamps and intervention order. Return JSON with current_state_summary, fixed_action, "
        f"candidate_hypotheses, and uncertainties.{diagnosis_rule}\n\n"
        f"Task mode: {mode}\nQuestion:\n{inference_stem(item)}\nOptions: HIDDEN\n"
        f"Patient/fixed context:\n{prediction_context(item) if item.get('dataset') == 'clir' else visible_context(item)}"
    )


def build_state(item: dict[str, Any], backend: Any, max_input: int) -> tuple[dict[str, Any], dict[str, Any]]:
    if item.get("dataset") == "medcounterfact":
        return ({
            "current_state_summary": inference_stem(item),
            "fixed_action": "interpret the supplied local evidence world",
            "candidate_hypotheses": [],
            "uncertainties": [],
        }, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "retry_count": 0})
    def valid(value: dict[str, Any]) -> bool:
        if item.get("dataset") != "medeinst":
            return True
        hypotheses = value.get("candidate_hypotheses")
        return isinstance(hypotheses, list) and len(hypotheses) == 5 and len({str(row).strip().casefold() for row in hypotheses}) == 5 and all(str(row).strip() for row in hypotheses)
    medeinst = item.get("dataset") == "medeinst"
    repair_rule = ""
    repair_preamble = None
    if medeinst:
        repair_preamble = (
            "Repair the response below into one complete JSON object. Preserve current_state_summary, fixed_action, "
            "and uncertainties. For candidate_hypotheses, replace duplicates with distinct plausible differential "
            "diagnoses grounded only in the visible case; these are hypotheses, not added patient facts."
        )
        repair_rule = (
            "candidate_hypotheses must be exactly five concise diagnosis-label strings, distinct after trimming and "
            "case folding. They must be diagnoses, not actions, treatments, or tests. Visible case (options hidden): "
            f"{inference_stem(item)}\n{visible_context(item)}"
        )
    state, _, usage = generate_json(
        backend, "You extract medical benchmark state without answering. JSON only.", state_prompt(item),
        max_input, 768, ("current_state_summary", "fixed_action", "candidate_hypotheses", "uncertainties"),
        valid, repair_rule, repair_preamble,
    )
    return state, usage


def transition_prompt(
    item: dict[str, Any], state: dict[str, Any], candidate: dict[str, str],
    slots: list[dict[str, str]], teacher: bool = False,
) -> str:
    mode = task_mode(item)
    options_hidden = mode in {"outcome_prediction", "temporal_forecasting", "evidence_world_reasoning"}
    evidence = "No retrieved evidence; use parametric knowledge and cite nothing." if not slots else json.dumps(slots, ensure_ascii=False)
    strength = "Use your strongest careful medical reasoning." if teacher else "Be concise and neutral."
    mode_rule = {
        "action_selection": "Assess this one action's preconditions, applicability, effects, harms, and monitoring independently.",
        "outcome_prediction": "The action is fixed. Predict its expected observation in free text; outcome options are unavailable.",
        "temporal_forecasting": "Use only observations through prediction time. Preserve timestamps/order and forecast direction, interval, threshold, or next action in free text.",
        "diagnosis_state_update": "Represent the edited patient evidence explicitly and assess this one competing diagnosis; do not assume the original diagnosis persists.",
        "evidence_world_reasoning": "Treat supplied fixed evidence as the local evidence world; keep any real-world implausibility or safety concern separate.",
    }[mode]
    grounding_rule = (
        "Return only the neutral transition fields; citations will be judged separately. "
        if teacher else
        "Each claim_grounding row must be {claim, evidence_ids, support}, where support is entailed, "
        "contradicted, or not_supported. Use only evidence IDs whose text actually supports the claim; "
        "otherwise use [] and not_supported. "
    )
    output_shape = {
        "current_state_summary": "one short sentence",
        "action": "one short phrase",
        **{key: ["short string"] for key in TRANSITION_ARRAY_KEYS},
    }
    if not teacher:
        output_shape["claim_grounding"] = [
            {"claim": "short string", "evidence_ids": ["D1"], "support": "entailed"}
        ]
    grounding_budget = " Keep claim_grounding to at most eight rows." if not teacher else ""
    return (
        "Predict an action-conditioned observation/state, not an answer or option ranking. "
        f"Never mention a preferred/selected/correct option. {grounding_rule}"
        f"{strength} Use strings for the summary and action, and short string arrays for the other seven fields. "
        f"Across those arrays use at most eight short statements.{grounding_budget} Keep "
        f"the complete JSON under 700 tokens. {mode_rule}\n\nTask mode: {mode}\nOutcome options hidden: {str(options_hidden).lower()}\n"
        f"Current state:\n{json.dumps(state, ensure_ascii=False)}\n"
        f"Action evaluated independently (label hidden):\n{candidate['text']}\n"
        f"Evidence:\n{evidence}\n\nReturn one compact JSON object with exactly this shape: "
        f"{json.dumps(output_shape, ensure_ascii=False)} current_state_summary and action must each be one "
        "short JSON string. The other seven transition fields must be arrays containing only short JSON strings; "
        "never write a key:value expression or nested object inside an array, and use [] when empty."
    )


def valid_transition_fields(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and all(isinstance(value.get(key), str) for key in TRANSITION_KEYS[:2])
        and all(
            isinstance(value.get(key), list)
            and all(isinstance(row, str) for row in value[key])
            for key in TRANSITION_ARRAY_KEYS
        )
    )


def normalize_card(
    raw: dict[str, Any], candidate: dict[str, str], slots: list[dict[str, str]], *, grounding_assessed: bool = True,
) -> dict[str, Any]:
    if not valid_transition_fields(raw):
        raise ValueError("transition output reached normalization with an invalid nine-field shape")
    valid_ids = {row["id"] for row in slots if row["text"]}
    card = {key: raw[key] if key in TRANSITION_KEYS[:2] else list(raw[key]) for key in TRANSITION_KEYS}
    card["action"] = candidate["text"]
    card["candidate_id"] = candidate["id"]
    card["evidence_ids"] = []
    card["evidence"] = copy.deepcopy(slots)
    card["option_leakage"] = bool(LEAKAGE.search(json.dumps(card, ensure_ascii=False)))
    if not grounding_assessed:
        card["grounding_status"] = "not_assessed"
        return card
    grounding = []
    for row in raw.get("claim_grounding", []) if isinstance(raw.get("claim_grounding"), list) else []:
        if isinstance(row, str) and row.strip():
            grounding.append({"claim": row.strip(), "evidence_ids": [], "support": "not_supported"})
            continue
        if not isinstance(row, dict) or not str(row.get("claim", "")).strip():
            continue
        ids = [str(value) for value in row.get("evidence_ids", []) if str(value) in valid_ids]
        support = str(row.get("support", "not_supported"))
        if support not in {"entailed", "contradicted", "not_supported"}:
            support = "not_supported"
        if not ids:
            support = "not_supported"
        grounding.append({"claim": str(row["claim"]), "evidence_ids": ids, "support": support})
    if grounding_assessed:
        known = {" ".join(row["claim"].casefold().split()) for row in grounding}
        for field in ("satisfied_preconditions", "failed_preconditions", "expected_observations", "expected_state_changes", "contraindications_or_harms", "monitoring_or_next_step"):
            values = card.get(field, [])
            for value in values if isinstance(values, list) else [values]:
                claim = str(value).strip()
                if claim and " ".join(claim.casefold().split()) not in known:
                    grounding.append({"claim": claim, "evidence_ids": [], "support": "not_supported"})
                    known.add(" ".join(claim.casefold().split()))
    card["claim_grounding"] = grounding
    card["claims"] = grounding
    cited = sorted({value for row in grounding for value in row["evidence_ids"]})
    card["evidence_ids"] = cited
    card["grounding_status"] = "grounded" if any(row["support"] == "entailed" for row in grounding) else "unsupported"
    card["option_leakage"] = bool(LEAKAGE.search(json.dumps(card, ensure_ascii=False)))
    return card


def make_cards(
    item: dict[str, Any], state: dict[str, Any], slots_by_candidate: dict[str, list[dict[str, str]]],
    backend: Any, max_input: int, *, teacher: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cards, total = [], {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "retry_count": 0}
    candidates = candidate_actions(item, state)
    slots = [slots_by_candidate.get(candidate["id"], []) for candidate in candidates]
    def valid_transition(value: dict[str, Any]) -> bool:
        if not valid_transition_fields(value) or bool(LEAKAGE.search(json.dumps(value, ensure_ascii=False))):
            return False
        if teacher and set(value) != set(TRANSITION_KEYS):
            return False
        grounding = value.get("claim_grounding", [])
        return teacher or (
            isinstance(grounding, list)
            and all(
                isinstance(row, str) or (
                    isinstance(row, dict)
                    and all(key in row for key in ("claim", "evidence_ids", "support"))
                )
                for row in grounding
            )
        )
    repair_shape = {
        "current_state_summary": "brief summary", "action": "action",
        "satisfied_preconditions": [], "failed_preconditions": [], "expected_observations": [],
        "expected_state_changes": [], "contraindications_or_harms": [], "monitoring_or_next_step": [],
        "uncertainties": [],
    }
    if not teacher:
        repair_shape["claim_grounding"] = [
            {"claim": "short claim", "evidence_ids": ["D1"], "support": "entailed"}
        ]
    required = TRANSITION_KEYS if teacher else (*TRANSITION_KEYS, "claim_grounding")
    if teacher:
        repair_rule = (
            "Remove any correct-answer, preferred-candidate, selected-option, or answer-ranking language. "
            "current_state_summary and action must each be one short JSON string. The other seven transition fields "
            "must be arrays containing only short JSON strings, never key:value expressions or nested objects; use at "
            "most eight total statements. "
            f"Use exactly this compact shape (replace values, keep every key): {json.dumps(repair_shape)}"
        )
    else:
        repair_rule = (
            "Remove any correct-answer, preferred-candidate, selected-option, or answer-ranking language. "
            "Discard extra detail instead of copying or expanding the long response. current_state_summary and action "
            "must each be one short JSON string. Across the other seven transition arrays use at most four total short "
            "string statements. Use at most four claim_grounding rows; each must contain only one short-sentence claim, "
            "a compact evidence_ids string array, and support set to entailed, contradicted, or not_supported. Keep the "
            "complete JSON short. "
            f"Use exactly this compact shape (replace values, keep every key): {json.dumps(repair_shape)}"
        )
    generated = generate_json_batch(
        backend, "You are a neutral clinical transition predictor. JSON only.",
        [transition_prompt(item, state, candidate, evidence, teacher) for candidate, evidence in zip(candidates, slots)],
        max_input, 768, required, valid_transition,
        repair_rule,
    )
    for candidate, evidence, (raw, _, usage) in zip(candidates, slots, generated):
        card = normalize_card(raw, candidate, evidence, grounding_assessed=not teacher)
        if card["option_leakage"]:
            raise ValueError(f"prohibited transition leakage for {item['item_id']} candidate {candidate['id']}")
        cards.append(card)
        for key in total:
            total[key] += usage[key]
    return cards, total


def shuffled(cards: list[dict[str, Any]], item_id: str, full: bool) -> list[dict[str, Any]]:
    if len(cards) < 2:
        return copy.deepcopy(cards)
    shift = random.Random(f"13:{item_id}:{'full' if full else 'effect'}").randrange(1, len(cards))
    result = copy.deepcopy(cards)
    for index, target in enumerate(result):
        source = cards[(index + shift) % len(cards)]
        if full:
            preserved_id, preserved_action = target["candidate_id"], target["action"]
            target.clear(); target.update(copy.deepcopy(source))
            target["candidate_id"], target["action"] = preserved_id, preserved_action
        else:
            for key in EFFECT_KEYS:
                target[key] = copy.deepcopy(source.get(key))
            def effect_claims(card: dict[str, Any]) -> set[str]:
                return {
                    " ".join(str(value).casefold().split())
                    for key in EFFECT_KEYS for value in (card.get(key) or [])
                }
            target_effects, source_effects = effect_claims(cards[index]), effect_claims(source)
            grounding = [
                copy.deepcopy(row) for row in cards[index].get("claim_grounding", [])
                if " ".join(str(row.get("claim", "")).casefold().split()) not in target_effects
            ] + [
                copy.deepcopy(row) for row in source.get("claim_grounding", [])
                if " ".join(str(row.get("claim", "")).casefold().split()) in source_effects
            ]
            target["claim_grounding"] = target["claims"] = grounding
            target["evidence_ids"] = sorted({value for row in grounding for value in row.get("evidence_ids", [])})
            documents = {
                str(document.get("id")): copy.deepcopy(document)
                for document in [*(target.get("evidence") or []), *(source.get("evidence") or [])]
                if isinstance(document, dict) and document.get("id") is not None
            }
            target["evidence"] = [documents[value] for value in target["evidence_ids"] if value in documents]
            target["grounding_status"] = "grounded" if any(row.get("support") == "entailed" for row in grounding) else "unsupported"
        target["shuffle_source_candidate_id"] = source["candidate_id"]
    return result


def reader_contract(item: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    if item.get("dataset") == "medcounterfact":
        return (
            '{"evidence_conditioned_answer":"...","real_world_safety_flag":"none|implausible|unsafe|uncertain",'
            '"reasoning":"...","supporting_evidence_ids":[]}',
            ("evidence_conditioned_answer", "real_world_safety_flag", "reasoning", "supporting_evidence_ids"),
        )
    if item.get("dataset") == "medpic":
        return ('{"answer_choices":["A"],"reasoning":"...","supporting_evidence_ids":[]}',
                ("answer_choices", "reasoning", "supporting_evidence_ids"))
    if item.get("dataset") == "medeinst":
        return ('{"open_answer":"actual diagnosis name","reasoning":"...","supporting_evidence_ids":[]}',
                ("open_answer", "reasoning", "supporting_evidence_ids"))
    return ('{"answer_choice":"A","reasoning":"...","supporting_evidence_ids":[]}',
            ("answer_choice", "reasoning", "supporting_evidence_ids"))


def normalize_reader_output(item: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    """Normalize exact output aliases without changing the model's answer."""
    if item.get("dataset") == "medpic" and isinstance(parsed.get("answer_choices"), list):
        options = options_for(item)
        reverse: dict[str, list[str]] = {}
        for key, text in options.items():
            normalized = " ".join(unicodedata.normalize("NFKC", text).strip().casefold().split())
            reverse.setdefault(normalized, []).append(key)
        choices = []
        for value in parsed["answer_choices"]:
            value = str(value)
            if value in options:
                choices.append(value)
                continue
            normalized = " ".join(unicodedata.normalize("NFKC", value).strip().casefold().split())
            matches = reverse.get(normalized, [])
            choices.append(matches[0] if len(matches) == 1 else value)
        parsed["answer_choices"] = choices
    if item.get("dataset") == "medcounterfact":
        safety = parsed.get("real_world_safety_flag")
        if safety == "safe":
            parsed["real_world_safety_flag"] = "none"
        elif safety not in {"none", "implausible", "unsafe", "uncertain"}:
            parsed["real_world_safety_flag"] = "uncertain"
            parsed["safety_parse_failure"] = True
    return parsed


def common_input(item: dict[str, Any], slots: list[dict[str, str]], block: Any) -> str:
    temporal = task_mode(item) in {"outcome_prediction", "temporal_forecasting"}
    safe_context = prediction_context(item) if item.get("dataset") == "clir" else visible_context(item)
    sections = [f"1. Patient/question state\n{question_stem(item) if temporal else item['question']}\n{safe_context}"]
    sections += [f"{index + 2}. Evidence slot {index + 1}\n{slot['id']}: {slot['text']}" for index, slot in enumerate(slots)]
    sections.append("7. Optional method-specific structured block\n" + json.dumps(block, ensure_ascii=False, sort_keys=True))
    return "\n\n".join(sections)


def answer_with(
    item: dict[str, Any], method: str, slots: list[dict[str, str]], block: Any,
    backend: Any, max_input: int, max_new: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract, required = reader_contract(item)
    rank_instruction = {
        "direct_rank": "Directly rank the visible answer options; do not predict transitions.",
        "structured_no_transition": (
            "Score only current-state compatibility, evidence relevance, guideline applicability, and contradictions. "
            "Do not predict future observations, next states, rollouts, or action effects."
        ),
        "full_transition": "Compare the neutral cards and return only the dataset reader contract; emit no separate ranking metadata.",
        "effect_shuffle": "Compare the supplied shuffled cards and answer; do not repair the shuffle.",
        "full_card_shuffle": "Compare the supplied shuffled cards and answer; do not repair the shuffle.",
        "teacher_transition": "Compare the teacher's neutral cards and return only the dataset reader contract.",
    }.get(method, "Use the supplied information and answer.")
    prompt = (
        f"Method: {method}. {rank_instruction}\n"
        "Priority: patient/fixed in-world facts, grounded structured content, external evidence, then parametric knowledge. "
        "Never overwrite explicit patient facts with generic priors.\n"
        f"Options:\n{json.dumps(options_for(item), ensure_ascii=False)}\n"
        f"Required output: {contract}\n\n{common_input(item, slots, block)}"
    )
    mcf = item.get("dataset") == "medcounterfact"
    medeinst = item.get("dataset") == "medeinst"
    def valid_reader(value: dict[str, Any]) -> bool:
        answer = value.get("open_answer")
        return (
            isinstance(answer, str) and bool(answer.strip())
            and " ".join(answer.casefold().split()) not in {"concise diagnosis", "actual diagnosis name"}
        )
    repair_rule = (
        "Discard repeated or extra detail instead of copying the long response. Return exactly this compact JSON: "
        '{"evidence_conditioned_answer":"higher|lower|no difference",'
        '"real_world_safety_flag":"none|implausible|unsafe|uncertain",'
        '"reasoning":"at most two short sentences","supporting_evidence_ids":["D1"]}. '
        "Use one allowed enum value for each of the first two fields, keep reasoning at most 240 characters, keep "
        "supporting_evidence_ids a short string list, and output JSON only."
    ) if mcf else (
        "Return the actual concise diagnosis stated or supported by the response reasoning; never copy the schema "
        "placeholder. Return exactly open_answer, reasoning, and supporting_evidence_ids as JSON."
        if medeinst else ""
    )
    parsed, _, usage = generate_json(
        backend, "You are a provenance-aware medical benchmark reader. JSON only.",
        prompt, max_input, max_new, required, validator=valid_reader if medeinst else None,
        repair_rule=repair_rule,
    )
    return normalize_reader_output(item, parsed), usage


def prediction_value(item: dict[str, Any], parsed: dict[str, Any]) -> Any:
    if item.get("dataset") == "medcounterfact":
        return parsed.get("evidence_conditioned_answer")
    if item.get("dataset") == "medpic":
        return parsed.get("answer_choices")
    if item.get("dataset") == "medeinst":
        return parsed.get("open_answer")
    return parsed.get("answer_choice")


def validate_reader_citations(parsed: dict[str, Any], slots: list[dict[str, str]]) -> None:
    valid = {slot["id"] for slot in slots if slot.get("text")}
    values = parsed.get("supporting_evidence_ids")
    parsed["supporting_evidence_ids"] = [str(value) for value in values if str(value) in valid] if isinstance(values, list) else []


def direct_rank(
    item: dict[str, Any], state: dict[str, Any], slots: list[dict[str, str]], backend: Any, max_input: int, max_new: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    choices = options_for(item) or {row["id"]: row["text"] for row in candidate_actions(item, state)}
    safety = " Also return real_world_safety_flag as none, implausible, unsafe, or uncertain." if item.get("dataset") == "medcounterfact" else ""
    prompt = (
        "Directly rank the answer options using the question and five evidence slots. Do not extract state, "
        "predict observations, next states, effects, or rollouts. For multi-label questions selected is a JSON list; "
        f"otherwise it is one string. Return ranking, selected, reasoning, supporting_evidence_ids.{safety}\n\n"
        f"Options or open hypotheses: {json.dumps(choices, ensure_ascii=False)}\n\n{common_input(item, slots, {})}"
    )
    required = ("ranking", "selected", "reasoning", "supporting_evidence_ids")
    if item.get("dataset") == "medcounterfact":
        required += ("real_world_safety_flag",)
    candidate_ids = list(choices)
    candidate_id_set = set(candidate_ids)
    def valid(value: dict[str, Any]) -> bool:
        ranking = value.get("ranking")
        selected = value.get("selected")
        safety = value.get("real_world_safety_flag")
        return (
            isinstance(ranking, list) and bool(ranking)
            and all(isinstance(row, str) and row in candidate_id_set for row in ranking)
            and (
                isinstance(selected, list) and bool(selected)
                and all(isinstance(row, str) and row in candidate_id_set for row in selected)
                if item.get("dataset") == "medpic"
                else isinstance(selected, str) and selected in candidate_id_set
            )
            and isinstance(value.get("reasoning"), str)
            and isinstance(value.get("supporting_evidence_ids"), list)
            and (
                item.get("dataset") != "medcounterfact"
                or isinstance(safety, str) and safety in {"none", "safe", "implausible", "unsafe", "uncertain"}
            )
        )
    sample_id = candidate_ids[0] if candidate_ids else "H0"
    repair_shape = {
        "ranking": candidate_ids,
        "selected": [sample_id] if item.get("dataset") == "medpic" else sample_id,
        "reasoning": "one short sentence",
        "supporting_evidence_ids": ["D1"],
    }
    if item.get("dataset") == "medcounterfact":
        repair_shape["real_world_safety_flag"] = "none|implausible|unsafe|uncertain"
    selected_rule = "a short JSON list of candidate IDs" if item.get("dataset") == "medpic" else "one candidate-ID JSON string"
    parsed, _, usage = generate_json(
        backend, "You are a direct medical option ranker. JSON only.", prompt, max_input, max_new,
        required, valid, repair_rule=(
            "Discard malformed or repeated detail and return exactly this compact JSON shape: "
            f"{json.dumps(repair_shape, ensure_ascii=False)}. ranking must be one flat JSON list using only candidate "
            f"IDs {candidate_ids}; selected must be {selected_rule}, never diagnosis/action text or an object. reasoning "
            "must be one short JSON string and supporting_evidence_ids a short JSON string list. For MCF, use one "
            f"allowed safety enum. Candidate ID mapping: {json.dumps(choices, ensure_ascii=False)}. The values shown "
            "in the shape are placeholders; preserve the response's intended ranking and selection when mapping text "
            "to IDs."
        ),
    )
    return normalize_reader_output(item, parsed), usage


def structured_factors(
    item: dict[str, Any], state: dict[str, Any], slots: list[dict[str, str]], backend: Any, max_input: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    choices = options_for(item) or {row["id"]: row["text"] for row in candidate_actions(item, state)}
    prompt = (
        "Score each option only on current-state compatibility, evidence relevance, guideline applicability, and "
        "contradictions. Do not predict action effects, future observations, next states, or rollouts. Return JSON "
        "with candidate_factors (list) and summary.\n\n"
        f"State: {json.dumps(state, ensure_ascii=False)}\nOptions or hypotheses: {json.dumps(choices, ensure_ascii=False)}\n"
        f"Evidence: {json.dumps(slots, ensure_ascii=False)}"
    )
    factor_keys = (
        "current_state_compatibility", "evidence_relevance",
        "guideline_applicability", "contradictions",
    )
    exact_shape = {
        "candidate_factors": [
            {"candidate_id": candidate_id, **{key: "short scalar" for key in factor_keys}}
            for candidate_id in choices
        ],
        "summary": "one short sentence",
    }
    parsed, _, usage = generate_json(
        backend, "You perform structured present-state scoring without transitions. JSON only.",
        prompt, max_input, 768, ("candidate_factors", "summary"),
        repair_rule=
        "Return exactly this compact shape: " + json.dumps(exact_shape, ensure_ascii=False) +
        ". summary must be one short JSON string of at most 240 characters. candidate_factors must contain "
        "exactly one row for every shown candidate ID and no others. Factor values must be short JSON scalars, "
        "not arrays or objects. Do not add state, evidence, transition, expected, or future fields. Keep the "
        "complete JSON short.",
    )
    rows = parsed.get("candidate_factors")
    if isinstance(rows, list):
        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                normalized.append(row)
                continue
            row = dict(row)
            if "option" in row:
                row.setdefault("candidate_id", row.pop("option"))
            normalized.append(row)
        parsed["candidate_factors"] = normalized
    return parsed, usage


def comparison_factors(
    item: dict[str, Any], state: dict[str, Any], cards: list[dict[str, Any]], backend: Any, max_input: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    prompt = (
        "Compare the candidate transition cards and return neutral per-candidate factors only: candidate_id, "
        "precondition_fit, state_consistency, effect_consistency, evidence_support, harms_or_contradictions, and "
        "uncertainty. Do not select, rank, recommend, or compute a total score. Return candidate_factors and "
        "cross_candidate_observations. Return exactly one short candidate_factors row per candidate; do not make "
        "pairwise candidate combinations. Use at most three short cross-candidate observations and keep the complete "
        "JSON under 700 tokens.\n\n"
        f"Question: {item['question']}\nState: {json.dumps(state, ensure_ascii=False)}\n"
        f"Cards: {json.dumps(cards, ensure_ascii=False)}"
    )
    expected_ids = {str(card.get("candidate_id")) for card in cards}
    def valid(value: dict[str, Any]) -> bool:
        rows = value.get("candidate_factors")
        return not expected_ids or (
            isinstance(rows, list)
            and {str(row.get("candidate_id")) for row in rows if isinstance(row, dict)} == expected_ids
        )
    parsed, _, usage = generate_json(
        backend, "You compare transition information without choosing an answer. JSON only.",
        prompt, max_input, 768, ("candidate_factors", "cross_candidate_observations"), valid,
        (
            f"candidate_factors must contain exactly one short row for each ID {sorted(expected_ids)}; "
            "cross_candidate_observations must contain at most three short strings. Do not emit pairwise combinations."
        ),
    )
    allowed = {
        "candidate_id", "precondition_fit", "state_consistency", "effect_consistency",
        "evidence_support", "harms_or_contradictions", "uncertainty",
    }
    rows = parsed.get("candidate_factors")
    neutral_rows = [
        {key: value for key, value in row.items() if key in allowed}
        for row in rows if isinstance(row, dict)
    ] if isinstance(rows, list) else []
    neutral = {
        "candidate_factors": neutral_rows,
        "cross_candidate_observations": parsed.get("cross_candidate_observations", []),
    }
    return neutral, usage


def equal_token_analysis(
    item: dict[str, Any], state: dict[str, Any], per_candidate: dict[str, list[dict[str, str]]],
    backend: Any, max_input: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    rows, total = [], {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "retry_count": 0}
    candidates = candidate_actions(item, state)
    prompts = [
        chat(backend.tokenizer, "You reason about present evidence without transition prediction.", (
            "Analyze only present-state compatibility, evidence relevance, guideline applicability, and contradictions "
            "for this candidate. Do not predict effects, observations, future states, next states, or rollouts. "
            "Do not quote or copy evidence. Return one concise paragraph under 400 tokens.\n\n"
            f"State: {json.dumps(state, ensure_ascii=False)}\nCandidate: {candidate['text']}\n"
            f"Evidence: {json.dumps(per_candidate.get(candidate['id'], []), ensure_ascii=False)}"
        ), max_input)
        for candidate in candidates
    ]
    outputs = backend.generate(prompts, 512)
    for candidate, output in zip(candidates, outputs):
        usage = {
            "prompt_tokens": output["prompt_tokens"],
            "completion_tokens": output["completion_tokens"],
            "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
            "retry_count": 0,
        }
        rows.append({"candidate_id": candidate["id"], "analysis": output["raw_response"]})
        for key in total:
            total[key] += usage[key]
    synthesis, synthesis_usage = structured_factors(item, state, combined_candidate_slots(per_candidate), backend, max_input)
    for key in total:
        total[key] += synthesis_usage[key]
    return {"per_candidate_reasoning": rows, "present_state_synthesis": synthesis}, total


def outcome_match(
    item: dict[str, Any], cards: list[dict[str, Any]], backend: Any, max_input: int, max_new: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    predicted = [{key: card.get(key) for key in ("expected_observations", "expected_state_changes", "monitoring_or_next_step", "uncertainties", "claim_grounding", "evidence_ids")} for card in cards]
    prompt = (
        "Match an already-completed, option-hidden prediction to the answer options. Do not revise or regenerate "
        "the prediction. Return answer_choice, reasoning, and supporting_evidence_ids.\n\n"
        f"Predicted observation/next state: {json.dumps(predicted, ensure_ascii=False)}\n"
        f"Options: {json.dumps(options_for(item), ensure_ascii=False)}"
    )
    return generate_json(
        backend, "You are an independent outcome-to-option matcher. JSON only.", prompt, max_input, max_new,
        ("answer_choice", "reasoning", "supporting_evidence_ids"),
    )[::2]


def evidence_world_match(
    item: dict[str, Any], cards: list[dict[str, Any]], backend: Any, max_input: int, max_new: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    conclusion = [{key: card.get(key) for key in ("expected_observations", "expected_state_changes", "uncertainties", "claim_grounding", "evidence_ids")} for card in cards]
    question = inference_stem(item)
    prompt = (
        "Map the completed neutral local-evidence conclusion to exactly higher, lower, or no difference. "
        "Do not revise the conclusion. Separately assess real-world safety as none, implausible, unsafe, or uncertain. "
        "Return evidence_conditioned_answer, real_world_safety_flag, reasoning, supporting_evidence_ids.\n\n"
        f"Question: {question}\nNeutral conclusion: {json.dumps(conclusion, ensure_ascii=False)}"
    )
    required = ("evidence_conditioned_answer", "real_world_safety_flag", "reasoning", "supporting_evidence_ids")
    def valid(value: dict[str, Any]) -> bool:
        answer = value.get("evidence_conditioned_answer")
        safety = value.get("real_world_safety_flag")
        return (
            isinstance(answer, str) and answer in {"higher", "lower", "no difference", "same"}
            and isinstance(safety, str) and safety in {"none", "safe", "implausible", "unsafe", "uncertain"}
            and isinstance(value.get("reasoning"), str)
            and isinstance(value.get("supporting_evidence_ids"), list)
        )
    parsed, _, usage = generate_json(
        backend, "You are an independent evidence-world conclusion matcher. JSON only.", prompt, max_input, max_new,
        required, valid, repair_rule=(
            "Discard malformed structure and return exactly this compact JSON shape: "
            '{"evidence_conditioned_answer":"higher","real_world_safety_flag":"uncertain",'
            '"reasoning":"one short sentence","supporting_evidence_ids":[]}. '
            "The first value must be higher, lower, or no difference; the safety value must be none, implausible, "
            "unsafe, or uncertain. The shown values are placeholders. Use only the question and neutral conclusion "
            f"below. Question: {question}\nNeutral conclusion: {json.dumps(conclusion, ensure_ascii=False)}"
        ),
    )
    if parsed["evidence_conditioned_answer"] == "same":
        parsed["evidence_conditioned_answer"] = "no difference"
    return normalize_reader_output(item, parsed), usage


def candidate_retrievals(item: dict[str, Any], state: dict[str, Any], retriever: Any) -> dict[str, list[dict[str, str]]]:
    result, next_id = {}, 1
    fixed = item.get("dataset") == "medcounterfact"
    candidates = candidate_actions(item, state)
    shared = []
    if item.get("dataset") == "clir":
        document = next((row for row in safe_fixed_documents(item) if row.get("contents")), None)
        if document:
            shared = [{"id": "D1", "text": str(document["contents"])}]
            next_id = 2
    remaining = 5 - len(shared)
    for index, candidate in enumerate(candidates):
        count = remaining // len(candidates) + int(index < remaining % len(candidates))
        documents = safe_fixed_documents(item)[:count] if fixed else retriever.retrieve(
            f"{inference_stem(item)}\nAction or hypothesis: {candidate['text']}", count
        )
        result[candidate["id"]] = shared + [
            {"id": f"D{doc_index}", "text": str(document.get("contents", ""))}
            for doc_index, document in enumerate(documents, next_id)
        ]
        next_id += len(documents)
    return result


def combined_candidate_slots(values: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    chosen, seen = [], set()
    for rank in range(5):
        for slots in values.values():
            if rank < len(slots) and slots[rank]["id"] not in seen:
                chosen.append(slots[rank])
                seen.add(slots[rank]["id"])
            if len(chosen) == 5:
                break
        if len(chosen) == 5:
            break
    return chosen + evidence_slots([])[len(chosen):]


def run(
    items: list[dict[str, Any]], methods: tuple[str, ...], output_dir: Path, backend: Any,
    max_input: int, max_new: int, retriever: Any | None = None,
    medrgag_documents: dict[str, list[dict[str, Any]]] | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_path, card_path = output_dir / "predictions.jsonl", output_dir / "cards.jsonl"
    def method_uses_state(method: str, dataset: str) -> bool:
        return method not in {"direct", "medrgag_proxy"} and (
            method != "direct_rank" or dataset == "medeinst"
        )
    previous_predictions = read_jsonl(prediction_path) if prediction_path.exists() else []
    done = {(row["item_id"], row["method"]) for row in previous_predictions}
    saved_states: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for row in previous_predictions:
        method = row.get("method")
        uses_state = method_uses_state(str(method), str(row.get("dataset")))
        state = row.get("state")
        if uses_state and isinstance(state, dict) and state and row["item_id"] not in saved_states:
            state_usage = row.get("token_usage", {}).get("state") or {"total_tokens": 0}
            saved_states[row["item_id"]] = (state, state_usage)
    existing_cards = {(row["item_id"], row["method"]): row for row in read_jsonl(card_path)} if card_path.exists() else {}
    needed = [item for item in items if any((item["item_id"], method) not in done for method in methods)]
    if "medrgag_proxy" in methods and medrgag_documents is None:
        raise ValueError("medrgag_proxy requires real selected top-5 documents via --medrgag-documents")
    retrieval_methods = set(methods) - {"direct", "medrgag_proxy"}
    need_external = any(
        item.get("dataset") != "medcounterfact"
        and any((item["item_id"], method) not in done for method in retrieval_methods)
        for item in needed
    )
    owned = retriever is None and need_external
    if owned:
        retriever = legacy.LocalRetriever(device="cuda:0")
    def record_contract_failure(
        item: dict[str, Any], method: str, stage: str, error: ModelContractError,
        state: dict[str, Any], state_usage: dict[str, Any], cards: list[dict[str, Any]] | None,
        card_usage: dict[str, Any], method_usage: dict[str, Any],
    ) -> None:
        reader_usage = {"total_tokens": 0}
        if stage == "state_extraction":
            pass
        elif stage == "transition_generation":
            card_usage = error.usage
        elif stage in {"structured_factors", "equal_token_reasoning", "transition_comparison"}:
            method_usage = error.usage
        else:
            reader_usage = error.usage
        uses_state = method_uses_state(method, str(item.get("dataset")))
        method_state_usage = state_usage if uses_state else {"total_tokens": 0}
        total_tokens = sum(
            value.get("total_tokens", 0)
            for value in (method_state_usage, card_usage, method_usage, reader_usage)
        )
        reader_output = {
            "error": str(error), "error_stage": stage, "parse_failure": True,
            "supporting_evidence_ids": [],
        }
        card_key = (item["item_id"], method)
        if (
            stage in {"state_extraction", "transition_generation"}
            and method in TRANSITION_METHODS and card_key not in existing_cards
        ):
            card_row = {
                "id": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"],
                "task_type": task_mode(item), "method": method, "state": state, "cards": [],
                "parse_failure": True, "error": str(error), "error_stage": stage,
                "shuffle_applicable": (
                    method in {"effect_shuffle", "full_card_shuffle"}
                    and item.get("dataset") in {"medpic", "medeinst"}
                ),
                "token_usage": error.usage,
            }
            append_jsonl(card_path, [card_row])
            existing_cards[card_key] = card_row
        append_jsonl(prediction_path, [{
            "id": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"],
            "task_type": task_mode(item), "method": method, "prediction": None,
            "reader_output": reader_output, "parse_failure": True,
            "state": state if uses_state else {}, "transition": cards or {},
            "evidence_ids": [], "supporting_evidence_ids": [],
            "shuffle_applicable": not (
                method in {"effect_shuffle", "full_card_shuffle"} and cards is not None and len(cards) < 2
            ),
            "teacher_type": "same_model_prompt_upper_bound" if method == "teacher_transition" else None,
            "token_usage": {
                "total_tokens": total_tokens, "state": method_state_usage, "transition": card_usage,
                "method_specific": method_usage, "reader": reader_usage,
            },
        }])
    try:
        for item in needed:
            active = [method for method in methods if (item["item_id"], method) not in done]
            state_methods = [method for method in active if method_uses_state(method, str(item.get("dataset")))]
            state_needed = bool(state_methods)
            if state_needed and item["item_id"] in saved_states:
                state, state_usage = copy.deepcopy(saved_states[item["item_id"]])
            else:
                try:
                    state, state_usage = build_state(item, backend, max_input) if state_needed else ({}, {"total_tokens": 0})
                except ModelContractError as error:
                    state, state_usage = {}, error.usage
                    for method in state_methods:
                        record_contract_failure(
                            item, method, "state_extraction", error, state, state_usage,
                            None, {"total_tokens": 0}, {"total_tokens": 0},
                        )
                    active = [method for method in active if method not in state_methods]
                    if not active:
                        continue
            item_retrieval_methods = set(active) - {"direct", "medrgag_proxy"}
            if "decomposition_only" in item_retrieval_methods:
                base_docs = safe_fixed_documents(item) if item.get("dataset") == "medcounterfact" else retriever.retrieve(legacy.retrieval_query(item), 5)
                base_slots = evidence_slots(base_docs)
            else:
                base_slots = evidence_slots([])
            candidate_needed = bool(set(active) & ({"candidate_retrieval", "direct_rank", "structured_no_transition", "equal_token_reasoning"} | TRANSITION_METHODS))
            per_candidate = candidate_retrievals(item, state, retriever) if candidate_needed else {}
            candidate_slots = combined_candidate_slots(per_candidate) if per_candidate else base_slots
            grounded_cards = parametric_cards = teacher_cards = None
            grounded_usage = parametric_usage = teacher_usage = None
            for base_method in ("transition_no_comparator", "full_transition"):
                previous = existing_cards.get((item["item_id"], base_method))
                if previous and not previous.get("parse_failure"):
                    grounded_cards, grounded_usage = previous["cards"], previous.get("token_usage", {"total_tokens": 0})
                    break
            for method in active:
                slots, block = base_slots, {"state": state}
                card_usage = {"total_tokens": 0}
                method_usage = {"total_tokens": 0}
                cards = None
                if method == "direct":
                    slots, block = evidence_slots(safe_fixed_documents(item)), {}
                elif method == "medrgag_proxy":
                    assert medrgag_documents is not None
                    if item["item_id"] not in medrgag_documents:
                        raise ValueError(f"medrgag proxy documents missing item: {item['item_id']}")
                    slots = evidence_slots(medrgag_documents[item["item_id"]])
                elif method == "candidate_retrieval":
                    slots = candidate_slots
                    block = {"state": state, "candidate_actions_or_hypotheses": candidate_actions(item, state)}
                elif method == "decomposition_only":
                    block = {"state": state, "candidate_actions_or_hypotheses": candidate_actions(item, state)}
                elif method == "direct_rank":
                    slots = candidate_slots
                elif method == "structured_no_transition":
                    slots = candidate_slots
                    try:
                        factors, method_usage = structured_factors(item, state, slots, backend, max_input)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "structured_factors", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                    block = {"state": state, "present_state_factors": factors}
                elif method == "equal_token_reasoning":
                    slots = candidate_slots
                    try:
                        block, method_usage = equal_token_analysis(item, state, per_candidate, backend, max_input)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "equal_token_reasoning", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                elif method in TRANSITION_METHODS:
                    slots = candidate_slots
                    cached_card_row = existing_cards.get((item["item_id"], method))
                    if cached_card_row and cached_card_row.get("parse_failure"):
                        cached_card_row = None
                    if cached_card_row:
                        cards = cached_card_row["cards"]
                        card_usage = cached_card_row.get("token_usage", {"total_tokens": 0})
                    elif method == "parametric_transition":
                        if parametric_cards is None:
                            try:
                                parametric_cards, parametric_usage = make_cards(item, state, {}, backend, max_input)
                            except ModelContractError as error:
                                record_contract_failure(
                                    item, method, "transition_generation", error, state, state_usage,
                                    cards, card_usage, method_usage,
                                )
                                continue
                            card_usage = parametric_usage
                        cards = parametric_cards
                        card_usage = parametric_usage
                    elif method == "teacher_transition":
                        if teacher_cards is None:
                            try:
                                teacher_cards, teacher_usage = make_cards(
                                    item, state, per_candidate, backend, max_input, teacher=True,
                                )
                            except ModelContractError as error:
                                record_contract_failure(
                                    item, method, "transition_generation", error, state, state_usage,
                                    cards, card_usage, method_usage,
                                )
                                continue
                            card_usage = teacher_usage
                        cards = teacher_cards
                        card_usage = teacher_usage
                    else:
                        if grounded_cards is None:
                            try:
                                grounded_cards, grounded_usage = make_cards(
                                    item, state, per_candidate, backend, max_input,
                                )
                            except ModelContractError as error:
                                record_contract_failure(
                                    item, method, "transition_generation", error, state, state_usage,
                                    cards, card_usage, method_usage,
                                )
                                continue
                            card_usage = grounded_usage
                        cards = grounded_cards
                        card_usage = grounded_usage
                    if not cached_card_row and method == "effect_shuffle":
                        cards = shuffled(cards, item["item_id"], False)
                    elif not cached_card_row and method == "full_card_shuffle":
                        cards = shuffled(cards, item["item_id"], True)
                    reader_cards = [{key: value for key, value in card.items() if key != "evidence"} for card in cards]
                    block = {"state": state, "transition_cards": reader_cards}
                    if not cached_card_row and (item["item_id"], method) not in existing_cards:
                        row = {
                            "id": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"],
                            "task_type": task_mode(item), "method": method, "state": state, "cards": cards,
                            "shuffle_applicable": not (method in {"effect_shuffle", "full_card_shuffle"} and len(cards) < 2),
                            "token_usage": card_usage,
                        }
                        append_jsonl(card_path, [row]); existing_cards[(item["item_id"], method)] = row
                    if method in {"full_transition", "parametric_transition", "effect_shuffle", "full_card_shuffle", "teacher_transition"} and task_mode(item) not in {"outcome_prediction", "temporal_forecasting", "evidence_world_reasoning"}:
                        try:
                            factors, method_usage = comparison_factors(item, state, reader_cards, backend, max_input)
                        except ModelContractError as error:
                            record_contract_failure(
                                item, method, "transition_comparison", error, state, state_usage,
                                cards, card_usage, method_usage,
                            )
                            continue
                        block["neutral_comparison_factors"] = factors
                if method == "direct_rank":
                    try:
                        parsed, reader_usage = direct_rank(item, state, slots, backend, max_input, max_new)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "direct_rank", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                    prediction = parsed["selected"]
                    if item.get("dataset") == "medeinst":
                        mapping = {row["id"]: row["text"] for row in candidate_actions(item, state)}
                        selected = prediction[0] if isinstance(prediction, list) and prediction else prediction
                        prediction = mapping.get(str(selected), selected)
                    if item.get("dataset") == "medcounterfact":
                        parsed["evidence_conditioned_answer"] = prediction
                elif cards is not None and task_mode(item) in {"outcome_prediction", "temporal_forecasting"}:
                    try:
                        parsed, reader_usage = outcome_match(item, cards, backend, max_input, max_new)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "outcome_matcher", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                    prediction = parsed["answer_choice"]
                elif cards is not None and task_mode(item) == "evidence_world_reasoning":
                    try:
                        parsed, reader_usage = evidence_world_match(item, cards, backend, max_input, max_new)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "evidence_world_matcher", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                    prediction = parsed["evidence_conditioned_answer"]
                else:
                    try:
                        parsed, reader_usage = answer_with(item, method, slots, block, backend, max_input, max_new)
                    except ModelContractError as error:
                        record_contract_failure(
                            item, method, "final_reader", error, state, state_usage,
                            cards, card_usage, method_usage,
                        )
                        continue
                    prediction = prediction_value(item, parsed)
                citation_slots = slots if cards is None else [evidence for card in cards for evidence in card.get("evidence", [])]
                validate_reader_citations(parsed, citation_slots)
                uses_state = method_uses_state(method, str(item.get("dataset")))
                method_state_usage = state_usage if uses_state else {"total_tokens": 0}
                total_tokens = sum(value.get("total_tokens", 0) for value in (method_state_usage, card_usage, method_usage, reader_usage))
                append_jsonl(prediction_path, [{
                    "id": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"],
                    "task_type": task_mode(item), "method": method,
                    "prediction": prediction, "reader_output": parsed,
                    "state": state if uses_state else {}, "transition": cards or {},
                    "evidence_ids": parsed.get("supporting_evidence_ids", []),
                    "shuffle_applicable": not (method in {"effect_shuffle", "full_card_shuffle"} and cards is not None and len(cards) < 2),
                    "teacher_type": "same_model_prompt_upper_bound" if method == "teacher_transition" else None,
                    "token_usage": {"total_tokens": total_tokens, "state": method_state_usage, "transition": card_usage, "method_specific": method_usage, "reader": reader_usage},
                }])
    except Exception as error:
        print(f"experiment failed before cleanup: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        raise
    finally:
        if owned:
            retriever.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inference", type=Path, required=True, help="Gold-free inference JSONL")
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=METHODS)
    parser.add_argument("--model", type=Path, default=legacy.MODEL)
    parser.add_argument("--medrgag-documents", type=Path, help="M2 selected/reranked JSONL: item_id, documents")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--max-model-len", type=int, default=32768)
    parser.add_argument("--max-input-tokens", type=int, default=32256)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items = read_jsonl(args.inference)
    random.Random(args.seed).shuffle(items)
    if args.limit is not None:
        items = items[:args.limit]
    assert items, "inference JSONL is empty"
    forbidden = {"gold", "answer", "label", "selected_candidate_ids", "oracle_status"}
    assert not any(forbidden & set(item) for item in items), "inference rows contain forbidden answer/oracle fields"
    excluded = [item for item in items if excluded_clir_t9(item)]
    items = [item for item in items if item not in excluded]
    if excluded:
        print(f"excluded unsupported CLIR t9 items: {len(excluded)}", file=sys.stderr)
    assert items, "no supported inference rows remain after excluding CLIR t9"
    proxy_documents = None
    if args.medrgag_documents:
        proxy_documents = {row["item_id"]: row["documents"] for row in read_jsonl(args.medrgag_documents)}
        if any(len(documents) > 5 for documents in proxy_documents.values()):
            raise ValueError("--medrgag-documents may contain at most five selected/reranked documents per item")
    backend = legacy.VLLMBackend(args.model, args.max_model_len, args.gpu_memory_utilization)
    run(items, tuple(args.methods), args.output_dir, backend, args.max_input_tokens, args.max_new_tokens, medrgag_documents=proxy_documents)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
