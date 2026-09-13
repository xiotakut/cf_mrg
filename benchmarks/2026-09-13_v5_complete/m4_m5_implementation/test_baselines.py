"""Small regression check for the real Llama/Qwen chat and generation interface."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import struct

from transformers import AutoTokenizer

from src.medrag import MedRAG
from src.utils import Retriever, RetrievalSystem


ROOT = Path(__file__).resolve().parent


def main():
    for name in ("m4", "m5"):
        config = json.loads((ROOT / "configs" / f"{name}.json").read_text())
        tokenizer = AutoTokenizer.from_pretrained(ROOT / config["model_path"], local_files_only=True)
        pipeline = SimpleNamespace(model=SimpleNamespace(generation_config=SimpleNamespace(eos_token_id=[tokenizer.eos_token_id])))
        with patch("src.medrag.transformers.pipeline", return_value=pipeline), patch("src.medrag.RetrievalSystem", side_effect=AssertionError("unexpected retrieval initialization")):
            model = MedRAG(str(ROOT / config["model_path"]), generation_kwargs=config["generation_kwargs"], chat_template_kwargs=config["chat_template_kwargs"])
        with patch.object(model, "model") as generate:
            generate.model.generation_config.eos_token_id = [tokenizer.eos_token_id]
            generate.return_value = [{"generated_text": '{"answer_choice":"A"}'}]
            answer, snippets, scores = model.answer("Test?", {"A": "One", "B": "Two"}, snippets=[])
            assert answer == '{"answer_choice":"A"}' and snippets == scores == []
            prompt = generate.call_args.args[0]
            kwargs = generate.call_args.kwargs
            assert kwargs["add_special_tokens"] is False and kwargs["return_full_text"] is False
            assert kwargs["max_new_tokens"] == 2048 and "max_length" not in kwargs
            if name == "m4":
                assert prompt.count("<|begin_of_text|>") == 1
            else:
                assert prompt.endswith("<think>\n\n</think>\n\n")
                assert model.context_length > 1024
            model.context_length = 2
            model.answer("Test?", {"A": "One"}, snippets=[{"id": "long", "title": "T", "content": "test " * 20}])
            assert model.last_generation["context_truncated_tokens"] > 0
            model.max_length = 1
            try:
                model.generate([{"role": "user", "content": "overflow"}])
            except ValueError:
                pass
            else:
                raise AssertionError("context overflow was silently accepted")

    # RRF must retain contributions from all four retrievers.
    retrieval = object.__new__(RetrievalSystem)
    retrieval.retriever_name = "RRF-4"
    retrieval.corpus_name = "Textbooks"
    texts = [[[{'id': 'a'}, {'id': 'b'}]]] + [[[{'id': 'b'}, {'id': 'a'}]]] * 3
    docs, scores = retrieval.merge(texts, [[[2., 1.]], [[2., 1.]], [[1., 2.]], [[2., 1.]]], k=2)
    assert docs[0]["id"] == "b" and scores[0] > scores[1]

    # A source filename can contain underscores; byte offsets must select its exact line.
    with TemporaryDirectory() as directory:
        root = Path(directory) / "textbooks"
        (root / "chunk").mkdir(parents=True)
        (root / "line_offsets").mkdir()
        rows = [json.dumps({"id": f"source_part_{i}", "content": str(i)}) + "\n" for i in range(2)]
        (root / "chunk/source_part.jsonl").write_text("".join(rows))
        (root / "line_offsets/source_part.u64le").write_bytes(struct.pack("<QQ", 0, len(rows[0].encode())))
        retriever = object.__new__(Retriever)
        retriever.db_dir, retriever.corpus_name, retriever.chunk_dir = directory, "textbooks", str(root / "chunk")
        assert retriever.idx2txt([{"source": "source_part", "index": 1}])[0]["content"] == "1"
    print("PASS: both real chat templates, generation budgets, RRF fusion, and corpus offset lookup")


if __name__ == "__main__":
    main()
