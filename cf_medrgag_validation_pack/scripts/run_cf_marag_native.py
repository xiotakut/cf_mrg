#!/usr/bin/env python3
"""Run the small state-residual extensions without modifying official MA-RAG."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
from liquid import Template


ROOT = Path(__file__).resolve().parents[1]


def load_moe() -> Any:
    path = ROOT / "scripts/run_cfmoe.py"
    spec = importlib.util.spec_from_file_location("native_cfmoe", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


MOE = load_moe()

SYSTEM = """You are a medical assistant, please answer my medical questions. Give your final choice (capital option) closed in tag `<answer>X</answer>` after your analysis.
Your response should be as detailed as possible, but please do not use any subheadings."""
QUESTION = Template("""Below is a multiple-choice question.
### Question
{{question}}

### Options
{{options}}

Please analyze the question and give your answer. Give your analysis and final choice.""")
ROUND = Template("""Below is a multiple-choice question.
### Question
{{question}}

### Options
{{options}}

### Documents
{{documents}}

---

I will provide several assistant's previous answers, which may be incorrect.
The previous answers are sorted by their confidence, but the quality metric can be imperfect.
Please analyze the previous answers and then re-answer.

{{answers}}

Give your analysis and final answer.""")
QUERY_SYSTEM = """You are a medical expert. Identify contradictions and core dispute points among candidate answers, then generate precise BM25 retrieval queries. Output only [Query 1] ... through [Query 4] ... ."""
QUERY = Template("""Question:
{{question}}

Options:
{{options}}

Candidate answers:
{{answers}}

Generate up to four retrieval queries.""")
DELTA_QUERY = Template("""Generate at most two concise BM25 diagnostic queries that resolve a patient-state conflict.

Changed findings:
{{delta}}

Current leading answer: {{leader}}
Profile-supported alternative: {{challenger}}

Output only:
[Query 1] ...
[Query 2] ...""")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def score(row: dict[str, Any], name: str) -> dict[int, float]:
    return {int(key): float(value) for key, value in row["option_scores"].get(name, {}).items()}


def normalize(values: dict[int, float]) -> dict[int, float]:
    array = np.asarray(list(values.values()), dtype=float)
    return {key: (value - float(array.mean())) / (float(array.std()) + 1e-6)
            for key, value in values.items()}


def changed(pair: dict[str, Any]) -> str:
    delta = pair["delta"]
    values = ["added: " + value for value in delta["added_findings"]]
    values += ["removed: " + value for value in delta["removed_findings"]]
    values += ["changed: " + value["old"] + " -> " + value["new"]
               for value in delta["changed_findings"]]
    return "\n".join(values) if values else "no extracted finding change"


def queries(text: str) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in re.findall(r"\[Query .*?\](.*?)$", text,
                                                                     re.MULTILINE) if value.strip()))


def should_append_trigger(rounds: list[list[dict[str, Any]]], option_to_label: dict[str, int],
                          profile_top: int, profile_margin: float, threshold: float,
                          max_rounds: int) -> bool:
    """Whether an official completed baseline has an unresolved final consensus."""
    predictions = [row.get("prediction") for row in rounds[-1]]
    unanimous = (len(set(predictions)) == 1 and isinstance(predictions[0], str)
                 and predictions[0] in option_to_label)
    return (len(rounds) < max_rounds and unanimous
            and option_to_label[predictions[0]] != profile_top
            and profile_margin >= threshold)


def run(args: argparse.Namespace) -> dict[str, Any]:
    sys.path.insert(0, str(args.marag_repo))
    from microservice import CustomLanguageModel
    from utils import RetrievalService, combine_docs, get_query, inference, judger

    datasets = json.loads(args.dataset_path.read_text(encoding="utf-8"))
    mappings = {row["trap_marag_id"]: row for row in read_jsonl(args.mapping)
                if row["split"] == args.split}
    pairs = {row["pair_id"]: row for row in read_jsonl(args.pairs)}
    experts = {row["case_id"]: row for row in read_jsonl(args.experts)}
    model = CustomLanguageModel(args.model_name, __import__("logging").getLogger(__name__),
                                base_url=args.base_url)
    retriever = RetrievalService()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    trigger_enabled = args.variant in ("cf_trigger_only", "full_cf_marag_native")
    delta_query_enabled = args.variant in ("delta_query_only", "full_cf_marag_native")
    ranking_enabled = args.variant in ("cf_history_ranking", "full_cf_marag_native")
    completed = 0
    for dataset in datasets:
        if not args.start_id <= dataset["id"] <= args.end_id:
            continue
        mapping = mappings[dataset["id"]]; pair_id = mapping["pair_id"]
        pair, expert = pairs[pair_id], experts[pair_id]
        profile = score(expert, "profile_no_document")
        cpg = score(expert, "cpg_core")
        if not cpg and expert.get("cpg_structurally_not_applicable"):
            cpg = {label: 0.0 for label in profile}
        if set(profile) != set(mapping["option_to_label_id"].values()) or not cpg:
            raise ValueError(f"invalid sidecar for {pair_id}")
        zp, zc = normalize(profile), normalize(cpg)
        profile_top = min(profile, key=lambda label: (-profile[label], label))
        profile_margin = sorted(profile.values(), reverse=True)[0] - sorted(profile.values(), reverse=True)[1]
        label_to_letter = {label: letter for letter, label in mapping["option_to_label_id"].items()}
        option_str = get_query(dataset)["option_str"]
        previous_answers: list[str] = []
        documents = "null"
        retrieval_queries = retrieved_documents = total_tokens = query_tokens = 0
        started = time.time(); triggered = False
        question_dir = args.output_dir / "evaluations" / f"question_{dataset['id']}"
        question_dir.mkdir(parents=True, exist_ok=True)
        if (question_dir / "metadata.json").exists():
            completed += 1
            continue
        baseline_question = (args.baseline_run / "evaluations" / f"question_{dataset['id']}") \
            if args.baseline_run else None
        if args.variant == "cf_trigger_only" and baseline_question:
            baseline_metadata = baseline_question / "metadata.json"
            round_paths = sorted(baseline_question.glob("round_*.jsonl"),
                                 key=lambda path: int(path.stem.split("_")[-1]))
            baseline_rounds = [read_jsonl(path) for path in round_paths]
            if (not baseline_metadata.exists() or not baseline_rounds
                    or [int(path.stem.split("_")[-1]) for path in round_paths]
                    != list(range(1, len(round_paths) + 1))
                    or any(len(rows) != args.num_workers for rows in baseline_rounds)):
                raise ValueError(f"incomplete reused baseline: {baseline_question}")
            for source in round_paths:
                shutil.copy2(source, question_dir / source.name)
            residual = should_append_trigger(
                baseline_rounds, mapping["option_to_label_id"], profile_top, profile_margin,
                args.profile_threshold, args.num_round)
            metadata = json.loads(baseline_metadata.read_text(encoding="utf-8"))
            metadata.update({"pair_id": pair_id, "variant": args.variant,
                             "counterfactual_triggered": residual,
                             "initial_candidate_pool_reused": True,
                             "baseline_rounds_reused": len(baseline_rounds),
                             "profile_threshold": args.profile_threshold,
                             "beta_profile": args.beta_profile, "beta_cpg": args.beta_cpg})
            if residual:
                final_rows = baseline_rounds[-1]
                contents = [row["response"] for row in final_rows]
                _, query_text, query_output = inference(
                    QUERY_SYSTEM, QUERY.render(question=dataset["question"], options=option_str,
                                               answers="\n\n".join(contents)),
                    model, enable_thinking=True, temperature=0.0)[0]
                ordinary = queries(query_text)[:4]
                docs, doc_ids = [], set()
                if ordinary:
                    retrieve = partial(retriever.retrieve, total_k=32, top_k=2,
                                       combine_docs=False, use_reranker=True)
                    with ThreadPoolExecutor(max_workers=len(ordinary)) as pool:
                        for found, _ in pool.map(retrieve, ordinary):
                            for document in found:
                                if document["id"] not in doc_ids and len(docs) < 8:
                                    docs.append(document); doc_ids.add(document["id"])
                entropies = [float(np.mean(row["token_entropies"])) for row in final_rows]
                order = np.argsort(entropies)[::-1]
                previous = [f"{rank}. Previous answer (Entropy {entropies[index]:.2f}):\n{contents[index]}"
                            for rank, index in enumerate(order, 1)]
                prompt = ROUND.render(question=dataset["question"], options=option_str,
                                      answers="\n\n".join(previous),
                                      documents=combine_docs(docs, combine_sep="\n") if docs else "null")
                appended = []
                for answer_id, output in enumerate(inference(SYSTEM, prompt, model,
                                                             n=args.num_workers), 1):
                    prediction, _ = judger(output[1], "", single_answer=True)
                    appended.append({"round": len(baseline_rounds) + 1,
                                     "answer_id": answer_id, "prediction": prediction,
                                     "response": output[1], "reasoning": output[0],
                                     "logprobs": output[2]["logprobs"],
                                     "token_entropies": output[2]["token_entropies"]})
                with (question_dir / f"round_{len(baseline_rounds) + 1}.jsonl").open(
                        "w", encoding="utf-8") as stream:
                    for row in appended:
                        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                metadata["wall_clock_seconds"] = metadata.get("wall_clock_seconds", 0.0) + time.time() - started
                metadata["retrieval_queries"] = metadata.get("retrieval_queries", 0) + len(ordinary)
                metadata["retrieved_documents"] = metadata.get("retrieved_documents", 0) + len(docs)
                metadata["generated_tokens"] = metadata.get("generated_tokens", 0) + sum(
                    len(row["logprobs"]) for row in appended)
                metadata["query_generated_tokens"] = metadata.get("query_generated_tokens", 0) + len(
                    query_output["logprobs"])
            (question_dir / "metadata.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            completed += 1
            continue
        for round_id in range(1, args.num_round + 1):
            prompt = (QUESTION.render(question=dataset["question"], options=option_str) if round_id == 1
                      else ROUND.render(question=dataset["question"], options=option_str,
                                        answers="\n\n".join(previous_answers), documents=documents))
            baseline_round = (args.baseline_run / "evaluations" / f"question_{dataset['id']}"
                              / "round_1.jsonl") if args.baseline_run and round_id == 1 else None
            round_rows = []
            baseline_metadata = baseline_round.parent / "metadata.json" if baseline_round else None
            if baseline_round and (not baseline_round.exists() or not baseline_metadata.exists()):
                raise ValueError(f"missing reused first round: {baseline_round}")
            if baseline_round:
                baseline_rows = read_jsonl(baseline_round)
                if len(baseline_rows) != args.num_workers:
                    raise ValueError(f"incomplete reused first round: {baseline_round}")
                for value in baseline_rows:
                    round_rows.append({key: value[key] for key in
                                       ("round", "answer_id", "prediction", "response", "reasoning",
                                        "logprobs", "token_entropies")})
                    total_tokens += len(value["logprobs"])
            else:
                outputs = inference(SYSTEM, prompt, model, n=args.num_workers)
                for answer_id, output in enumerate(outputs, 1):
                    prediction, _ = judger(output[1], "", single_answer=True)
                    total_tokens += len(output[2]["logprobs"])
                    round_rows.append({"round": round_id, "answer_id": answer_id,
                                       "prediction": prediction, "response": output[1],
                                       "reasoning": output[0], "logprobs": output[2]["logprobs"],
                                       "token_entropies": output[2]["token_entropies"]})
            with (question_dir / f"round_{round_id}.jsonl").open("w", encoding="utf-8") as stream:
                for row in round_rows:
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            predictions = [row["prediction"] for row in round_rows]
            unanimous = len(set(predictions)) == 1 and predictions[0] in mapping["option_to_label_id"]
            leader_letter = max("ABCD", key=lambda letter: (predictions.count(letter), -ord(letter)))
            leader_label = mapping["option_to_label_id"][leader_letter]
            residual = unanimous and profile_top != leader_label and profile_margin >= args.profile_threshold
            should_trigger = trigger_enabled and residual and not triggered
            if round_id == args.num_round or (unanimous and not should_trigger):
                break
            triggered = triggered or should_trigger
            contents = [row["response"] for row in round_rows]
            ordinary: list[str] = []
            if not unanimous or should_trigger:
                _, query_text, query_output = inference(
                    QUERY_SYSTEM, QUERY.render(question=dataset["question"], options=option_str,
                                               answers="\n\n".join(contents)),
                    model, enable_thinking=True, temperature=0.0)[0]
                query_tokens += len(query_output["logprobs"])
                ordinary = queries(query_text)
            extra: list[str] = []
            if delta_query_enabled:
                _, query_text, query_output = inference(
                    QUERY_SYSTEM, DELTA_QUERY.render(delta=changed(pair),
                                                     leader=dataset["option"][leader_letter],
                                                     challenger=dataset["option"][label_to_letter[profile_top]]),
                    model, enable_thinking=True, temperature=0.0)[0]
                query_tokens += len(query_output["logprobs"])
                extra = queries(query_text)[:2]
            selected_queries = ((ordinary[:2] + extra[:2]) if extra else ordinary[:4])[:4]
            retrieval_queries += len(selected_queries)
            docs, doc_ids = [], set()
            if selected_queries:
                retrieve = partial(retriever.retrieve, total_k=32, top_k=2,
                                   combine_docs=False, use_reranker=True)
                with ThreadPoolExecutor(max_workers=len(selected_queries)) as pool:
                    for found, _ in pool.map(retrieve, selected_queries):
                        for document in found:
                            if document["id"] not in doc_ids and len(docs) < 8:
                                docs.append(document); doc_ids.add(document["id"])
            retrieved_documents += len(docs)
            documents = combine_docs(docs, combine_sep="\n") if docs else "null"
            entropies = [float(np.mean(row["token_entropies"])) for row in round_rows]
            if ranking_enabled:
                quality = []
                for index, row in enumerate(round_rows):
                    label = mapping["option_to_label_id"].get(row["prediction"])
                    bonus = (args.beta_profile * zp.get(label, 0.0)
                             + args.beta_cpg * zc.get(label, 0.0))
                    quality.append(-entropies[index] + bonus)
                order = np.argsort(quality)[::-1]
                previous_answers = [f"{rank}. Previous answer (CF quality {quality[index]:.3f}):\n{contents[index]}"
                                    for rank, index in enumerate(order, 1)]
            else:
                order = np.argsort(entropies)[::-1]
                previous_answers = [f"{rank}. Previous answer (Entropy {entropies[index]:.2f}):\n{contents[index]}"
                                    for rank, index in enumerate(order, 1)]
        (question_dir / "metadata.json").write_text(json.dumps({
            "pair_id": pair_id, "variant": args.variant,
            "wall_clock_seconds": time.time() - started,
            "retrieval_queries": retrieval_queries, "retrieved_documents": retrieved_documents,
            "generated_tokens": total_tokens, "query_generated_tokens": query_tokens,
            "counterfactual_triggered": triggered,
            "initial_candidate_pool_reused": bool(args.baseline_run),
            "profile_threshold": args.profile_threshold,
            "beta_profile": args.beta_profile, "beta_cpg": args.beta_cpg,
        }, indent=2) + "\n", encoding="utf-8")
        completed += 1
    return {"completed": completed, "variant": args.variant}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--marag-repo", type=Path, default=Path("/home/data3/txy/MA-RAG"))
    parser.add_argument("--dataset-path", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--experts", type=Path, required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--variant", choices=("cf_trigger_only", "delta_query_only",
                                               "cf_history_ranking", "full_cf_marag_native"), required=True)
    parser.add_argument("--model-name", default="qwen3-8b")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--num-round", type=int, default=4)
    parser.add_argument("--profile-threshold", type=float, default=0.5)
    parser.add_argument("--beta-profile", type=float, default=0.5)
    parser.add_argument("--beta-cpg", type=float, default=0.5)
    parser.add_argument("--start-id", type=int, default=0)
    parser.add_argument("--end-id", type=int, default=10**9)
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(run(parse_args()), sort_keys=True))
