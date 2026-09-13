"""The two paper-specific single-round retrieval configurations."""

from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .utils import Retriever, RetrievalSystem, corpus_names, retriever_names


class BM25MedCPT:
    """MA-RAG Appendix D.2: 32 hits per corpus, then MedCPT top-8."""

    def __init__(self, db_dir, corpus_name, reranker_path):
        self.retrievers = [Retriever("bm25", name, db_dir) for name in corpus_names[corpus_name]]
        for retriever in self.retrievers:
            retriever.index.set_bm25(k1=0.9, b=0.4)
        self.tokenizer = AutoTokenizer.from_pretrained(reranker_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(reranker_path)
        self.model.to("cuda:0" if torch.cuda.is_available() else "cpu").eval()

    @torch.inference_mode()
    def retrieve(self, question, k=8, rrf_k=100):
        documents, bm25_scores = [], []
        for retriever in self.retrievers:
            docs, scores = retriever.get_relevant_documents(question, k=32)
            documents.extend(docs)
            bm25_scores.extend(scores)
        # Match MA-RAG's BM25 merge order before MedCPT reranking.
        documents = [documents[i] for i in np.argsort(bm25_scores)[::-1]]
        if not documents:
            return [], []
        pairs = [[question, doc["content"]] for doc in documents]
        inputs = self.tokenizer(pairs, truncation=True, padding=True, max_length=512, return_tensors="pt").to(self.model.device)
        scores = self.model(**inputs).logits.squeeze(1).float().cpu().numpy()
        order = np.argsort(scores)[::-1][:k]
        return [documents[i] for i in order], [float(scores[i]) for i in order]


def missing_resources(config, db_dir):
    """Check the configured corpus without triggering downloads or indexing."""
    missing = []
    names = ["bm25"] if config["retriever_name"] == "BM25+MedCPT" else retriever_names[config["retriever_name"]]
    for corpus in corpus_names[config["corpus_name"]]:
        root = Path(db_dir) / corpus
        if not (root / "chunk").is_dir() or not any((root / "chunk").glob("*.jsonl")):
            missing.append(str(root / "chunk"))
        for name in names:
            index = root / "index" / name.replace("Query-Encoder", "Article-Encoder")
            if name == "bm25":
                if not any(index.glob("segments_*")):
                    missing.append(str(index))
            else:
                for filename in ("faiss.index", "metadatas.jsonl"):
                    if not (index / filename).is_file():
                        missing.append(str(index / filename))
    return missing


def make_retriever(config, db_dir, reranker_path):
    missing = missing_resources(config, db_dir)
    if missing:
        raise FileNotFoundError("Required retrieval resources are missing:\n" + "\n".join(missing))
    if config["retriever_name"] == "BM25+MedCPT":
        return BM25MedCPT(db_dir, config["corpus_name"], reranker_path)
    return RetrievalSystem(config["retriever_name"], config["corpus_name"], db_dir, HNSW=False, cache=False)
