#!/usr/bin/env python3
"""Judge transition claims against their cited evidence and scan leakage."""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any


PROHIBITED = re.compile(
    r"correct answer|selected option|preferred candidate|gold answer|option\s+[A-Z]\s+is\s+correct",
    re.IGNORECASE,
)
SUPPORT = {"entailed", "contradicted", "not_supported"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def last_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    found = None
    for index, char in enumerate(text):
        if char == "{":
            try:
                value, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                found = value
    return found


def evidence_map(row: dict[str, Any]) -> dict[str, str]:
    evidence = row.get("evidence") or row.get("documents") or []
    if isinstance(evidence, dict):
        return {str(key): str(value) for key, value in evidence.items()}
    return {
        str(value.get("id", value.get("evidence_id"))): str(value.get("text", value.get("contents", "")))
        for value in evidence if isinstance(value, dict) and value.get("id", value.get("evidence_id")) is not None
    }


def claims(row: dict[str, Any]) -> list[dict[str, Any]]:
    transition = row.get("transition") or row
    explicit = transition.get("claims", transition.get("claim_grounding")) if isinstance(transition, dict) else None
    result = [
        value for value in (explicit or [])
        if isinstance(value, dict) and str(value.get("claim", "")).strip()
    ] if isinstance(explicit, list) else []
    grounded = {str(value["claim"]).strip(): value for value in result}
    if isinstance(transition, dict):
        for field in ("satisfied_preconditions", "failed_preconditions", "expected_observations", "expected_state_changes", "contraindications_or_harms", "monitoring_or_next_step", "uncertainties"):
            for value in transition.get(field) or []:
                if isinstance(value, dict):
                    claim = str(value.get("claim", value.get("text", ""))).strip()
                    fallback = {"claim": claim, "evidence_ids": value.get("evidence_ids", [])}
                else:
                    claim = str(value).strip()
                    fallback = {"claim": claim, "evidence_ids": []}
                if claim and claim not in grounded:
                    result.append(fallback)
                    grounded[claim] = fallback
    return [value for value in result if str(value.get("claim", "")).strip()]


def valid_judgment(value: Any) -> bool:
    boolean_or_null = lambda field: value.get(field) is None or isinstance(value.get(field), bool)
    return (
        isinstance(value, dict)
        and all(key in value for key in (
            "precondition_correct", "effect_correct", "temporally_consistent",
            "evidence_support", "option_leakage", "comments",
        ))
        and all(boolean_or_null(field) for field in ("precondition_correct", "effect_correct", "temporally_consistent"))
        and value["evidence_support"] in SUPPORT
        and isinstance(value["option_leakage"], bool)
        and isinstance(value["comments"], str)
    )


def prompt(row: dict[str, Any], claim: dict[str, Any], cited: list[dict[str, str]]) -> str:
    payload = {
        "patient_state": row.get("state", {}), "action": row.get("action"),
        "claim": claim.get("claim"), "cited_evidence": cited, "task_type": row.get("task_type"),
    }
    return (
        "Judge this transition claim. Compare the claim to the cited evidence text, not merely its IDs. "
        "Return JSON only with precondition_correct, effect_correct, temporally_consistent (booleans or null), "
        "evidence_support (entailed|contradicted|not_supported), option_leakage (boolean), comments (short string).\n"
        + json.dumps(payload, ensure_ascii=False)
    )


def inspect(rows: list[dict[str, Any]], precomputed: list[dict[str, Any]] | None = None, backend: Any = None, max_input: int = 8192, sample_size: int | None = None, seed: int = 13, method: str | None = "full_transition") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    supplied = {(str(row.get("id", row.get("item_id"))), int(row.get("card_index", 0)), int(row["claim_index"])): row["judgment"] for row in (precomputed or [])}
    output, pending = [], []
    if method is not None:
        rows = [row for row in rows if row.get("method") == method]
        if not rows:
            raise ValueError(f"no cards found for method={method}")
    card_rows = [(row, index, card) for row in rows for index, card in enumerate(row.get("cards") if isinstance(row.get("cards"), list) else [row.get("transition") or row])]
    if sample_size is not None and len(card_rows) > sample_size:
        card_rows = random.Random(seed).sample(card_rows, sample_size)
    for row, card_index, card in card_rows:
        identifier = str(row.get("id", row.get("item_id")))
        context = {**row, "transition": card, "action": card.get("action", row.get("action")) if isinstance(card, dict) else row.get("action")}
        docs = {**evidence_map(row), **evidence_map(card if isinstance(card, dict) else {})}
        for index, claim in enumerate(claims(context)):
            ids = [str(value) for value in claim.get("evidence_ids", [])]
            cited = [{"id": key, "text": docs[key]} for key in ids if key in docs]
            base = {"id": identifier, "method": row.get("method"), "card_index": card_index, "claim_index": index, "claim": claim["claim"], "evidence_ids": ids, "valid_evidence_ids": [value["id"] for value in cited], "prohibited_leakage": bool(PROHIBITED.search(str(claim["claim"])))}
            judgment = supplied.get((identifier, card_index, index))
            if judgment is not None:
                if not valid_judgment(judgment):
                    raise ValueError(f"invalid precomputed judgment for {identifier}:{index}")
                output.append({**base, "judgment": judgment})
            else:
                pending.append((base, prompt(context, claim, cited)))
    if pending:
        if backend is None:
            raise ValueError("claims without precomputed judgments require a local model backend")
        rendered = [backend.tokenizer.apply_chat_template([{"role": "user", "content": text}], tokenize=False, add_generation_prompt=True) for _, text in pending]
        generated = backend.generate(rendered, 384)
        parsed = [last_object(value["raw_response"]) for value in generated]
        retry = [index for index, value in enumerate(parsed) if not valid_judgment(value)]
        if retry:
            retry_outputs = backend.generate([rendered[index] + "\nRepair: return one complete JSON object only." for index in retry], 384)
            for index, value in zip(retry, retry_outputs):
                parsed[index] = last_object(value["raw_response"])
        for (base, _), value in zip(pending, parsed):
            if not valid_judgment(value):
                raise ValueError(f"judge JSON repair failed for {base['id']}:{base['claim_index']}")
            output.append({**base, "judgment": value})
    cited = [row for row in output if row["valid_evidence_ids"]]
    support = [row["judgment"]["evidence_support"] for row in output]
    cited_support = [row["judgment"]["evidence_support"] for row in cited]
    summary = {
        "method": method or "all",
        "cards_judged": len({(row["id"], row["card_index"]) for row in output}),
        "claims": len(output),
        "claim_citation_rate": len(cited) / len(output) if output else None,
        "claim_entailment_rate": cited_support.count("entailed") / len(cited) if cited else None,
        "unsupported_claim_rate": support.count("not_supported") / len(output) if output else None,
        "contradiction_rate": support.count("contradicted") / len(output) if output else None,
        "hard_prohibited_string_rate": sum(row["prohibited_leakage"] for row in output) / len(output) if output else None,
        "judge_option_leakage_rate": sum(row["judgment"]["option_leakage"] for row in output) / len(output) if output else None,
        "prohibited_leakage_rate": sum(row["prohibited_leakage"] or row["judgment"]["option_leakage"] for row in output) / len(output) if output else None,
    }
    return output, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards", type=Path, default=Path("results/cards.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("results/mechanism_judgments.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("results/mechanism_metrics.json"))
    parser.add_argument("--precomputed", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.5)
    parser.add_argument("--sample-size", type=int, default=100, help="Fixed number of cards to judge (all if fewer)")
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--method", default="full_transition", help="Card method to judge, or 'all'")
    args = parser.parse_args()
    backend = None
    if args.model:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_gate_b import VLLMBackend
        backend = VLLMBackend(args.model, 32768, args.gpu_memory_utilization)
    judged, summary = inspect(load_jsonl(args.cards), load_jsonl(args.precomputed) if args.precomputed else None, backend, sample_size=args.sample_size, seed=args.seed, method=None if args.method == "all" else args.method)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in judged), encoding="utf-8")
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
