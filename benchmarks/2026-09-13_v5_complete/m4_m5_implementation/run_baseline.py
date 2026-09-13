"""Run a configured MedRAG reader on JSONL question/options records."""

import argparse
from itertools import islice
import json
from pathlib import Path
import time

from transformers import set_seed

from src.baselines import make_retriever, missing_resources
from src.medrag import MedRAG
from src.utils import corpus_names


ROOT = Path(__file__).resolve().parent
VARIANTS = {"m4": "m4", "m5": "m5", "llama31": "m4", "qwen3": "m5"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, type=str.lower, choices=tuple(VARIANTS), help="M4: MedRAG-Llama-3.1-8B; M5: MedRAG-Qwen3-8B")
    parser.add_argument("--input", type=Path, help="JSONL: id, question, options; optional pre-retrieved snippets")
    parser.add_argument("--output", type=Path, help="New JSONL output; existing files are never overwritten")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--model", help="Override the local model path")
    parser.add_argument("--corpus", choices=tuple(corpus_names), help="Explicit corpus override, recorded in outputs")
    parser.add_argument("--db-dir", type=Path, default=ROOT / "corpus")
    parser.add_argument("--check", action="store_true", help="Report local resource readiness without loading models")
    args = parser.parse_args()
    config = json.loads((ROOT / "configs" / f"{VARIANTS[args.variant]}.json").read_text())
    if args.corpus:
        config["corpus_name"] = args.corpus
    model_path = Path(args.model) if args.model else ROOT / config["model_path"]
    config["model_path"] = str(model_path.resolve())
    config["db_dir"] = str(args.db_dir.resolve())
    reranker_path = ROOT / config.get("reranker_path", "models/MedCPT-Cross-Encoder")
    if args.check:
        missing = missing_resources(config, args.db_dir)
        for path in [model_path] + ([reranker_path] if config["retriever_name"] == "BM25+MedCPT" else []):
            if not (path / "config.json").is_file() or not (list(path.glob("*.safetensors")) or list(path.glob("pytorch_model*.bin"))):
                missing.append(str(path))
        print(json.dumps({"config": config, "retrieval_ready": not missing, "missing": missing}, indent=2))
        raise SystemExit(bool(missing))
    if args.input is None or args.output is None:
        parser.error("--input and --output are required unless --check is used")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    with args.input.open() as stream:
        records = [json.loads(line) for line in islice(stream, args.limit)]
    if not records:
        parser.error("input contains no records")
    for record in records:
        if record.get("fixed_evidence"):
            parser.error("R1–R5 fixed_evidence requires a task adapter; this original MCQ runner cannot discard mandatory evidence")
        if not isinstance(record.get("question"), str) or not record["question"].strip():
            parser.error("each record requires a nonempty question")
        if not isinstance(record.get("options"), dict) or not record["options"]:
            parser.error("this runner expects multiple-choice options as a nonempty object")
    if args.output.exists():
        parser.error(f"output already exists: {args.output}")
    retriever = None
    if any(record.get("snippets") is None for record in records):
        retriever = make_retriever(config, args.db_dir, reranker_path)
    medrag = MedRAG(
        llm_name=str(model_path), rag=True, follow_up=False,
        retriever_name=config["retriever_name"], corpus_name=config["corpus_name"],
        db_dir=str(args.db_dir), retrieval_system=retriever,
        generation_kwargs=config["generation_kwargs"], chat_template_kwargs=config["chat_template_kwargs"],
        max_length=config["max_length"], context_length=config["context_length"],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        for index, record in enumerate(records):
            set_seed(config["seed"])
            started = time.monotonic()
            answer, snippets, scores = medrag.answer(
                question=record["question"], options=record["options"],
                snippets=record.get("snippets"), k=config["k"], rrf_k=config["rrf_k"],
            )
            result = {
                "id": record.get("id", record.get("item_id", index)),
                "method_id": config["method_id"], "method": config["method"], "config": config,
                "retrieval_mode": "provided_snippets" if record.get("snippets") is not None else "live",
                "response": answer, "snippets": snippets, "scores": scores,
                "generation": medrag.last_generation, "seconds": time.monotonic() - started,
            }
            stream.write(json.dumps(result, ensure_ascii=False) + "\n")
            stream.flush()
            print(f"{index + 1}/{len(records)} {result['id']}: {answer}", flush=True)


if __name__ == "__main__":
    main()
