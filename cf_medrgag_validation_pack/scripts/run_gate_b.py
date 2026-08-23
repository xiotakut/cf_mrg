#!/usr/bin/env python3
"""Run the balanced Gate-B M0/M1/M2 pilot with one local vLLM model."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable
import unicodedata


MODEL = Path("/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct")
MEDRGAG = Path("/home/data3/txy/MedRGAG")
MEDCPT = Path("/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder")
JAVA_HOME = Path("/home/data3/txy/.local/medrgag-jdk-21")
REFERENCE = Path(__file__).resolve().parents[1] / "configs" / "balanced60_seed13.json"
REFERENCE_SHA256 = "c16f7828466ca5dc1165e255f2a9d42fc2b3b8cf211503595a35490bb7f0a0f9"
SYSTEM = (
    "Answer the medical benchmark item using only the presented item and evidence. "
    "Always choose the best available option; never abstain. "
    "Return JSON only, with exactly one field named answer."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_balanced_pilot(
    inference_path: Path,
    gold_path: Path,
    reference_path: Path,
    expected_reference_sha256: str = REFERENCE_SHA256,
) -> list[dict[str, Any]]:
    if sha256_file(reference_path) != expected_reference_sha256:
        raise ValueError("balanced60 reference SHA-256 mismatch")
    ids = json.loads(reference_path.read_text(encoding="utf-8"))
    if not isinstance(ids, list) or len(ids) != 60 or len(set(ids)) != 60:
        raise ValueError("balanced60 reference must contain 60 unique item IDs")
    inference = {row["item_id"]: row for row in read_jsonl(inference_path)}
    gold_ids = {row["item_id"] for row in read_jsonl(gold_path)}
    missing = [item_id for item_id in ids if item_id not in inference or item_id not in gold_ids]
    if missing:
        raise ValueError(f"balanced60 IDs missing from inference/gold: {missing[:3]}")
    return [inference[item_id] for item_id in ids]


def _evidence_text(item: dict[str, Any]) -> str:
    evidence = item.get("fixed_evidence") or []
    time_series = item.get("time_series") or []
    values = []
    if evidence:
        values.append(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    if time_series:
        values.append(json.dumps(time_series, ensure_ascii=False, sort_keys=True))
    return "\n".join(values)


def _question_text(item: dict[str, Any]) -> str:
    options = item.get("options")
    if isinstance(options, dict) and options:
        rendered = "\n".join(f"{key}: {value}" for key, value in options.items())
        if item["dataset"] == "medpic":
            answer_format = 'The answer must be a JSON array of one or more option keys, e.g. {"answer":["A","B"]}.'
        else:
            answer_format = 'The answer must be exactly one option key string, e.g. {"answer":"A"}.'
        return f"Question:\n{item['question']}\n\nOptions:\n{rendered}\n\n{answer_format}"
    if item["dataset"] == "clir":
        answer_format = 'The answer must be exactly one A/B/C/D option key string, e.g. {"answer":"A"}.'
    elif item["dataset"] == "medcounterfact":
        answer_format = 'The answer must be exactly "higher", "lower", or "no difference", e.g. {"answer":"higher"}.'
    elif item["dataset"] == "medeinst":
        answer_format = 'The answer must be only a concise diagnosis label, never a sentence or explanation, e.g. {"answer":"Pneumonia"}.'
    else:
        answer_format = 'Return a concise answer string, e.g. {"answer":"diagnosis"}.'
    return (
        f"Question:\n{item['question']}\n\n"
        + answer_format
    )


def _truncate_head_tail(tokenizer: Any, text: str, budget: int) -> str:
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) <= budget:
        return text
    marker = "\n[...evidence truncated...]\n"
    marker_size = len(tokenizer.encode(marker, add_special_tokens=False))
    if budget <= marker_size:
        return ""
    usable = budget - marker_size
    head = usable // 2
    tail = usable - head
    return (
        tokenizer.decode(tokens[:head], skip_special_tokens=True)
        + marker
        + tokenizer.decode(tokens[-tail:] if tail else [], skip_special_tokens=True)
    )


def build_reader_chat(
    tokenizer: Any,
    item: dict[str, Any],
    evidence: str,
    max_input_tokens: int,
) -> str:
    question = _question_text(item)

    def chat(value: str) -> str:
        user = question if not value else f"{question}\n\nEvidence:\n{value}"
        return tokenizer.apply_chat_template(
            [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            tokenize=False,
            add_generation_prompt=True,
        )

    empty = chat("")
    overhead = len(tokenizer.encode(empty, add_special_tokens=False))
    original_evidence = evidence
    budget = max(0, max_input_tokens - overhead)
    evidence = _truncate_head_tail(tokenizer, original_evidence, budget)
    rendered = chat(evidence)
    while evidence and len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        overflow = len(tokenizer.encode(rendered, add_special_tokens=False)) - max_input_tokens
        budget = max(0, budget - overflow - 4)
        evidence = _truncate_head_tail(tokenizer, original_evidence, budget)
        rendered = chat(evidence)
    if len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        raise ValueError(f"question exceeds input budget: {item['item_id']}")
    return rendered


def parse_answer(raw: str) -> Any:
    for candidate in reversed(re.findall(r"\{[^{}]*\}", raw, flags=re.DOTALL)):
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "answer" in value:
            return value["answer"]
    return None


def selection_ids(text: str) -> list[int]:
    sys.path.insert(0, str(MEDRGAG))
    from src.medrgag_logic import parse_selection

    parsed = parse_selection(text, "released-code-intent")["selected_ids"]
    if parsed:
        return parsed
    lines = re.findall(r"(?im)^\s*-?\s*Final Selection\s*:\s*(.*?)\s*$", text)
    if not lines:
        return []
    result = []
    for value in re.findall(r"\b([0-9])\b", lines[-1]):
        number = int(value)
        if number not in result:
            result.append(number)
        if len(result) == 5:
            break
    return result


def _option_text(value: Any) -> str:
    text = " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())
    return re.sub(r"^(?:[a-j]|[ivxlcdm]+|\d+)\s*[.)]\s*", "", text)


def oracle_option_keys(options: dict[str, str], answers: list[Any]) -> list[str]:
    keys = {str(key).casefold(): str(key) for key in options}
    values = {_option_text(value): str(key) for key, value in options.items()}
    selected = []
    for answer in answers:
        key = keys.get(str(answer).strip().casefold()) or values.get(_option_text(answer))
        if key is None:
            raise ValueError(f"oracle answer does not map to an option: {answer!r}")
        if key not in selected:
            selected.append(key)
    return selected


def embedded_clir_options(question: str) -> dict[str, str]:
    return {
        match.group(1): " ".join(match.group(2).split())
        for match in re.finditer(r"(?ms)^([A-D])\.\s*(.*?)(?=\n[A-D]\.\s|\Z)", question)
    }


def oracle_cards(item: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    answers = gold["answer"] if isinstance(gold["answer"], list) else [gold["answer"]]
    options = item.get("options")
    if item["dataset"] == "clir" and not options:
        options = embedded_clir_options(item["question"])
    if isinstance(options, dict) and options:
        selected = oracle_option_keys(options, answers)
        candidates = [(str(key), str(value), str(key) in selected) for key, value in options.items()]
    else:
        selected = ["H0"]
        candidates = [("H0", str(answers[0]), True)]
    evidence = gold.get("evidence") if item["dataset"] == "clir" else None
    cards = []
    for candidate_id, action, is_selected in candidates:
        cards.append(
            {
                "candidate_id": candidate_id,
                "action": action,
                "oracle_status": "selected" if is_selected else "not_selected",
                "applicability": "supported" if is_selected else "inactive",
                "triggering_conditions": [],
                "failed_or_absent_conditions": [],
                "exceptions": [],
                "immediate_observations": [evidence] if is_selected and evidence is not None else [],
                "next_state_changes": [],
                "future_threshold_or_interval": "not_required",
                "benefits": [],
                "harms_or_constraints": [],
                "monitoring_or_next_action": [],
                "evidence_ids": ["same_item_gold.evidence"] if is_selected and evidence is not None else [],
                "contradictions": [] if is_selected else ["not selected by same-item oracle answer"],
                "uncertainty_reasons": [],
                "unsupported_claims": [],
                "rollout_valid": is_selected,
            }
        )
    return {
        "cards": cards,
        "planner": {
            "selected_candidate_ids": selected,
            "candidate_scores": [
                {"candidate_id": candidate_id, "total": 1.0 if is_selected else 0.0}
                for candidate_id, _, is_selected in candidates
            ],
            "causal_determinants": [],
            "comparison_valid": True,
        },
    }


def completed_ids(path: Path, method: str) -> set[str]:
    if not path.exists():
        return set()
    return {
        row["item_id"]
        for row in read_jsonl(path)
        if row.get("method") == method
    }


def append_rows(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def selection_payload(items: list[dict[str, Any]], reference_sha256: str) -> dict[str, Any]:
    return {
        "profile": "balanced60",
        "m2_profile": "released-code-intent-all-llama",
        "reference_sha256": reference_sha256,
        "item_ids": [item["item_id"] for item in items],
    }


class VLLMBackend:
    def __init__(
        self,
        model: Path,
        max_model_len: int,
        gpu_memory_utilization: float,
    ) -> None:
        from transformers import AutoTokenizer
        from vllm import LLM

        self.tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
        self.model = LLM(
            model=str(model),
            tokenizer=str(model),
            tensor_parallel_size=1,
            dtype="bfloat16",
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_memory_utilization,
            enforce_eager=True,
            trust_remote_code=True,
        )

    def generate(
        self,
        prompts: list[str],
        max_tokens: int | list[int],
        *,
        temperature: float = 0,
        seed: int | None = 42,
        top_p: float = 1.0,
        top_k: int = -1,
        presence_penalty: float = 0.0,
        ignore_eos: bool = False,
    ) -> list[dict[str, Any]]:
        from vllm import SamplingParams

        limits = [max_tokens] * len(prompts) if isinstance(max_tokens, int) else max_tokens
        if len(limits) != len(prompts):
            raise ValueError("max_tokens list must match prompts")
        params = [SamplingParams(
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                top_k=top_k,
                presence_penalty=presence_penalty,
                ignore_eos=ignore_eos,
                max_tokens=limit,
            ) for limit in limits]
        outputs = self.model.generate(
            prompts,
            params[0] if isinstance(max_tokens, int) else params,
            use_tqdm=True,
        )
        return [
            {
                "raw_response": output.outputs[0].text,
                "prompt_tokens": len(output.prompt_token_ids),
                "completion_tokens": len(output.outputs[0].token_ids),
                "finish_reason": output.outputs[0].finish_reason,
            }
            for output in outputs
        ]


def run_m0(
    items: list[dict[str, Any]],
    output_path: Path,
    backend: Any,
    batch_size: int,
    max_input_tokens: int,
    max_new_tokens: int,
) -> int:
    done = completed_ids(output_path, "M0")
    pending = [item for item in items if item["item_id"] not in done]
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        prompts = [
            build_reader_chat(backend.tokenizer, item, _evidence_text(item), max_input_tokens)
            for item in batch
        ]
        outputs = backend.generate(prompts, max_new_tokens)
        rows = []
        for item, output in zip(batch, outputs):
            usage = {
                "prompt_tokens": output["prompt_tokens"],
                "completion_tokens": output["completion_tokens"],
                "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
                "finish_reason": output["finish_reason"],
            }
            rows.append(
                {
                    "item_id": item["item_id"],
                    "dataset": item["dataset"],
                    "method": "M0",
                    "raw_response": output["raw_response"],
                    "prediction": {"answer": parse_answer(output["raw_response"])},
                    "usage": usage,
                }
            )
        append_rows(output_path, rows)
    return len(pending)


def retrieval_query(item: dict[str, Any]) -> str:
    options = item.get("options")
    suffix = ""
    if isinstance(options, dict):
        suffix = "\n" + "\n".join(f"{key}. {value}" for key, value in options.items())
    return str(item["question"]) + suffix


def fixed_documents(item: dict[str, Any], count: int) -> list[dict[str, Any]]:
    values = item.get("fixed_evidence") or []
    if len(values) > count:
        values = [
            "\n\n".join(
                value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
                for value in values[index * len(values) // count : (index + 1) * len(values) // count]
            )
            for index in range(count)
        ]
    documents = [
        {
            "id": f"fixed-{index}",
            "source": "fixed",
            "contents": value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True),
        }
        for index, value in enumerate(values[:count])
    ]
    while len(documents) < count:
        documents.append({"id": f"fixed-{len(documents)}", "source": "fixed", "contents": ""})
    return documents


class LocalRetriever:
    def __init__(self) -> None:
        os.environ.setdefault("JAVA_HOME", str(JAVA_HOME))
        sys.path.insert(0, str(MEDRGAG))
        from src.medrgag_retrieval import DualBM25Retriever, MedCPTRanker

        self.sparse = DualBM25Retriever(
            MEDRGAG / "corpus/textbooks/index/bm25",
            MEDRGAG / "corpus/wikipedia/index/bm25",
            MEDRGAG / "corpus/textbooks",
            MEDRGAG / "corpus/wikipedia",
        )
        self.ranker = MedCPTRanker(MEDCPT, device="cuda:0")

    def retrieve(self, query: str, count: int) -> list[dict[str, Any]]:
        ranked = self.ranker.rank(query, self.sparse.retrieve(query, 32))[:count]
        return [
            {
                "id": row["docid"],
                "source": row["source"],
                "contents": row["contents"],
                "bm25_score": row["bm25_score"],
                "medcpt_score": row["medcpt_score"],
            }
            for row in ranked
        ]

    def close(self) -> None:
        self.ranker.close()


class LocalReranker:
    def __init__(self) -> None:
        sys.path.insert(0, str(MEDRGAG))
        from src.medrgag_retrieval import MedCPTRanker

        self.ranker = MedCPTRanker(MEDCPT, device="cuda:0")

    def rank(self, query: str, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.ranker.rank(query, documents)

    def close(self) -> None:
        self.ranker.close()


def prepare_retrievals(
    items: list[dict[str, Any]],
    output_path: Path,
    retriever: Any | None = None,
) -> dict[str, list[dict[str, Any]]]:
    cached = {row["item_id"]: row["documents"] for row in read_jsonl(output_path)} if output_path.exists() else {}
    pending = [item for item in items if item["item_id"] not in cached]
    owned = retriever is None and any(item["dataset"] != "medcounterfact" for item in pending)
    if owned:
        retriever = LocalRetriever()
    try:
        for item in pending:
            if item["dataset"] == "medcounterfact":
                documents = fixed_documents(item, 5)
                policy = "fixed_only"
            elif item["dataset"] == "clir":
                documents = retriever.retrieve(retrieval_query(item), 5)
                policy = "patient_observations_plus_external"
            else:
                documents = retriever.retrieve(retrieval_query(item), 5)
                policy = "external"
            append_rows(
                output_path,
                [{"item_id": item["item_id"], "dataset": item["dataset"], "policy": policy, "documents": documents}],
            )
            cached[item["item_id"]] = documents
    finally:
        if owned:
            retriever.close()
    return cached


def _stage_chat(tokenizer: Any, prompt: str, max_input_tokens: int) -> str:
    def render(value: str) -> str:
        return tokenizer.apply_chat_template(
            [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": value}],
            tokenize=False,
            add_generation_prompt=True,
        )

    rendered = render(prompt)
    tokens = tokenizer.encode(rendered, add_special_tokens=False)
    if len(tokens) <= max_input_tokens:
        return rendered
    empty_size = len(tokenizer.encode(render(""), add_special_tokens=False))
    original = prompt
    budget = max_input_tokens - empty_size
    prompt = _truncate_head_tail(tokenizer, original, budget)
    rendered = render(prompt)
    while prompt and len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        overflow = len(tokenizer.encode(rendered, add_special_tokens=False)) - max_input_tokens
        budget = max(0, budget - overflow - 4)
        prompt = _truncate_head_tail(tokenizer, original, budget)
        rendered = render(prompt)
    if len(tokenizer.encode(rendered, add_special_tokens=False)) > max_input_tokens:
        raise ValueError("MedRGAG stage prompt exceeds input budget")
    return rendered


def run_prompt_stage(
    entries: list[dict[str, Any]],
    output_path: Path,
    backend: Any,
    batch_size: int,
    max_tokens: int,
    *,
    temperature: float = 0,
    seed: int | None = 42,
    top_p: float = 1.0,
    top_k: int = -1,
    presence_penalty: float = 0.0,
) -> dict[str, dict[str, Any]]:
    cached = {row["key"]: row for row in read_jsonl(output_path)} if output_path.exists() else {}
    pending = [entry for entry in entries if entry["key"] not in cached]
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        outputs = backend.generate(
            [entry["prompt"] for entry in batch],
            max_tokens,
            temperature=temperature,
            seed=seed,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty,
        )
        rows = []
        for entry, output in zip(batch, outputs):
            row = {
                "key": entry["key"],
                "item_id": entry["item_id"],
                "dataset": entry["dataset"],
                "raw_response": output["raw_response"],
                "usage": {
                    "prompt_tokens": output["prompt_tokens"],
                    "completion_tokens": output["completion_tokens"],
                    "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
                    "finish_reason": output["finish_reason"],
                },
            }
            rows.append(row)
            cached[row["key"]] = row
        append_rows(output_path, rows)
    return cached


def run_reader_method(
    method: str,
    items: list[dict[str, Any]],
    documents: dict[str, list[dict[str, Any]]],
    output_path: Path,
    backend: Any,
    batch_size: int,
    max_input_tokens: int,
    max_new_tokens: int,
) -> int:
    done = completed_ids(output_path, method)
    pending = [item for item in items if item["item_id"] not in done]
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        evidence = {}
        for item in batch:
            rendered = "\n".join(
                f"Document [{index}]: {document['contents']}"
                for index, document in enumerate(documents[item["item_id"]])
            )
            if item["dataset"] == "clir":
                rendered = f"Patient observations:\n{_evidence_text(item)}\n\n{rendered}"
            evidence[item["item_id"]] = rendered
        prompts = [
            build_reader_chat(
                backend.tokenizer,
                item,
                evidence[item["item_id"]],
                max_input_tokens,
            )
            for item in batch
        ]
        outputs = backend.generate(prompts, max_new_tokens)
        append_rows(
            output_path,
            [
                {
                    "item_id": item["item_id"],
                    "dataset": item["dataset"],
                    "method": method,
                    "raw_response": output["raw_response"],
                    "prediction": {"answer": parse_answer(output["raw_response"])},
                    "usage": {
                        "prompt_tokens": output["prompt_tokens"],
                        "completion_tokens": output["completion_tokens"],
                        "total_tokens": output["prompt_tokens"] + output["completion_tokens"],
                        "finish_reason": output["finish_reason"],
                    },
                }
                for item, output in zip(batch, outputs)
            ],
        )
    return len(pending)


def load_oracle_gold(path: Path, item_ids: set[str]) -> dict[str, dict[str, Any]]:
    result = {}
    for row in read_jsonl(path):
        item_id = row.get("item_id")
        if item_id in item_ids:
            result[item_id] = {"answer": row.get("answer"), "evidence": row.get("evidence")}
    missing = item_ids - set(result)
    if missing:
        raise ValueError(f"M12 gold rows missing: {sorted(missing)[:3]}")
    return result


def prepare_m12_cards(
    items: list[dict[str, Any]],
    gold: dict[str, dict[str, Any]],
    output_path: Path,
) -> dict[str, dict[str, Any]]:
    cached = {row["item_id"]: row for row in read_jsonl(output_path)} if output_path.exists() else {}
    for item in items:
        if item["item_id"] in cached:
            continue
        payload = {"item_id": item["item_id"], "dataset": item["dataset"], **oracle_cards(item, gold[item["item_id"]])}
        append_rows(output_path, [payload])
        cached[item["item_id"]] = payload
    return cached


def load_m2_rerank(items: list[dict[str, Any]], path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.is_file():
        raise FileNotFoundError(f"M12 requires completed M2 rerank artifact: {path}")
    documents = {row["item_id"]: row["documents"] for row in read_jsonl(path)}
    missing = {item["item_id"] for item in items} - set(documents)
    if missing:
        raise ValueError(f"M12 requires complete M2 rerank coverage; missing: {sorted(missing)[:3]}")
    return documents


def run_m12(
    items: list[dict[str, Any]],
    gold_path: Path,
    output_dir: Path,
    backend: Any,
    batch_size: int,
    max_input_tokens: int,
    max_new_tokens: int,
) -> int:
    ids = {item["item_id"] for item in items}
    gold = load_oracle_gold(gold_path, ids)
    cards = prepare_m12_cards(items, gold, output_dir / "M12.cards.jsonl")
    documents = load_m2_rerank(items, output_dir / "M2.rerank.jsonl")
    with_oracle = {}
    for item in items:
        item_id = item["item_id"]
        oracle_document = {
            "contents": "Oracle transition cards and planner:\n"
            + json.dumps(
                {"transition_cards": cards[item_id]["cards"], "planner": cards[item_id]["planner"]},
                ensure_ascii=False,
                sort_keys=True,
            )
        }
        with_oracle[item_id] = [*documents[item_id], oracle_document]
    return run_reader_method(
        "M12",
        items,
        with_oracle,
        output_dir / "M12.jsonl",
        backend,
        batch_size,
        max_input_tokens,
        max_new_tokens,
    )


def rerank_m2(
    items: list[dict[str, Any]],
    selected: dict[str, list[dict[str, Any]]],
    output_path: Path,
    ranker: Any | None = None,
) -> dict[str, list[dict[str, Any]]]:
    cached = {row["item_id"]: row["documents"] for row in read_jsonl(output_path)} if output_path.exists() else {}
    pending = [item for item in items if item["item_id"] not in cached]
    owned = ranker is None and any(selected[item["item_id"]] for item in pending)
    if owned:
        ranker = LocalReranker()
    try:
        for item in pending:
            documents = selected[item["item_id"]]
            ranked = ranker.rank(retrieval_query(item), documents) if documents else []
            append_rows(output_path, [{"item_id": item["item_id"], "dataset": item["dataset"], "documents": ranked[:5]}])
            cached[item["item_id"]] = ranked[:5]
    finally:
        if owned:
            ranker.close()
    return cached


def run_m2(
    items: list[dict[str, Any]],
    retrievals: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    backend: Any,
    batch_size: int,
    max_input_tokens: int,
    max_new_tokens: int,
    ranker: Any | None = None,
) -> int:
    sys.path.insert(0, str(MEDRGAG))
    from src.medrgag_logic import (
        build_explore_prompt,
        build_generation_slots,
        build_selection_prompt,
        build_summary_prompt,
        clean_generated_text,
        parse_knowledge_points,
    )
    from src.medrgag_prompts import get_prompt_profile

    profile = get_prompt_profile("released-code-intent")
    context_limit = max_input_tokens + max_new_tokens
    adapted = {item["item_id"]: {**item, "options": item.get("options") or {}} for item in items}
    summary_entries = []
    for item in items:
        value = adapted[item["item_id"]]
        for index, document in enumerate(retrievals[item["item_id"]]):
            prompt = build_summary_prompt(profile, value, document["contents"])
            summary_entries.append(
                {"key": f"{item['item_id']}::{index}", "item_id": item["item_id"], "dataset": item["dataset"], "prompt": _stage_chat(backend.tokenizer, prompt, context_limit - 64)}
            )
    summaries = run_prompt_stage(summary_entries, output_dir / "M2.summary.jsonl", backend, batch_size, 64)

    explore_entries = []
    for item in items:
        item_summaries = [summaries[f"{item['item_id']}::{index}"]["raw_response"] for index in range(len(retrievals[item["item_id"]]))]
        prompt, _ = build_explore_prompt(profile, adapted[item["item_id"]], item_summaries, 3)
        explore_entries.append({"key": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"], "prompt": _stage_chat(backend.tokenizer, prompt, context_limit - 1024)})
    explores = run_prompt_stage(explore_entries, output_dir / "M2.explore.jsonl", backend, batch_size, 1024)

    generation_entries = []
    for item in items:
        points, _ = parse_knowledge_points(explores[item["item_id"]]["raw_response"], 3)
        points += ["None"] * (3 - len(points))
        for slot in build_generation_slots(profile, adapted[item["item_id"]], points):
            generation_entries.append(
                {"key": f"{item['item_id']}::{slot['slot']}", "item_id": item["item_id"], "dataset": item["dataset"], "prompt": _stage_chat(backend.tokenizer, slot["prompt"], context_limit - 256)}
            )
    generated = run_prompt_stage(
        generation_entries,
        output_dir / "M2.generate.jsonl",
        backend,
        batch_size,
        256,
        temperature=1.2,
        seed=None,
        top_p=0.9,
        top_k=50,
        presence_penalty=1.0,
    )

    candidates: dict[str, list[dict[str, Any]]] = {}
    select_entries = []
    for item in items:
        retrieved = list(retrievals[item["item_id"]])
        while len(retrieved) < 5:
            retrieved.append({"id": f"empty-{len(retrieved)}", "source": "fixed", "contents": ""})
        gen_docs = [
            {"id": f"generated-{index}", "source": "generated", "contents": clean_generated_text(generated[f"{item['item_id']}::{index}"]["raw_response"])}
            for index in range(5)
        ]
        candidates[item["item_id"]] = retrieved[:5] + gen_docs
        prompt, _ = build_selection_prompt(profile, adapted[item["item_id"]], candidates[item["item_id"]])
        select_entries.append({"key": item["item_id"], "item_id": item["item_id"], "dataset": item["dataset"], "prompt": _stage_chat(backend.tokenizer, prompt, context_limit - 2048)})
    selections = run_prompt_stage(select_entries, output_dir / "M2.select.jsonl", backend, batch_size, 2048)

    selected: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        ids = selection_ids(selections[item["item_id"]]["raw_response"])
        selected[item["item_id"]] = [candidates[item["item_id"]][index] for index in ids if index < 10][:5]
    selected = rerank_m2(items, selected, output_dir / "M2.rerank.jsonl", ranker)
    return run_reader_method(
        "M2", items, selected, output_dir / "M2.jsonl", backend, batch_size, max_input_tokens, max_new_tokens
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--pilot-reference", type=Path, default=REFERENCE)
    parser.add_argument("--reference-sha256", default=REFERENCE_SHA256)
    parser.add_argument("--methods", nargs="+", choices=("M0", "M1", "M2", "M12"), default=("M0",))
    parser.add_argument("--model", type=Path, default=MODEL)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=32768)
    parser.add_argument("--max-input-tokens", type=int, default=32256)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    items = load_balanced_pilot(
        args.inference, args.gold, args.pilot_reference, args.reference_sha256
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    selection = selection_payload(items, args.reference_sha256)
    selection_path = args.output_dir / "selection.json"
    selection_text = json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if selection_path.exists() and selection_path.read_text(encoding="utf-8") != selection_text:
        raise SystemExit(f"selection already differs: {selection_path}")
    selection_path.write_text(selection_text, encoding="utf-8")
    retrievals = None
    if set(args.methods) & {"M1", "M2"}:
        retrievals = prepare_retrievals(items, args.output_dir / "retrieval.jsonl")
    if "M12" in args.methods:
        load_m2_rerank(items, args.output_dir / "M2.rerank.jsonl")
    backend = VLLMBackend(args.model, args.max_model_len, args.gpu_memory_utilization)
    if "M0" in args.methods:
        count = run_m0(
            items,
            args.output_dir / "M0.jsonl",
            backend,
            args.batch_size,
            args.max_input_tokens,
            args.max_new_tokens,
        )
        print(f"M0 complete: generated={count}, total={len(items)}", flush=True)
    if "M1" in args.methods:
        count = run_reader_method(
            "M1",
            items,
            retrievals,
            args.output_dir / "M1.jsonl",
            backend,
            args.batch_size,
            args.max_input_tokens,
            args.max_new_tokens,
        )
        print(f"M1 complete: generated={count}, total={len(items)}", flush=True)
    if "M2" in args.methods:
        count = run_m2(
            items,
            retrievals,
            args.output_dir,
            backend,
            args.batch_size,
            args.max_input_tokens,
            args.max_new_tokens,
        )
        print(f"M2 complete: generated={count}, total={len(items)}", flush=True)
    if "M12" in args.methods:
        count = run_m12(
            items,
            args.gold,
            args.output_dir,
            backend,
            args.batch_size,
            args.max_input_tokens,
            args.max_new_tokens,
        )
        print(f"M12 complete: generated={count}, total={len(items)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
