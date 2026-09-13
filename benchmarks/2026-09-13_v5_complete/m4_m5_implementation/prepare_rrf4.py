"""Build missing RRF-4 dense indexes locally when upstream embedding URLs return 403."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from src.utils import construct_index, embed


ROOT = Path(__file__).resolve().parent
ENCODERS = {"contriever": "facebook/contriever", "specter": "allenai/specter", "medcpt": "ncbi/MedCPT-Article-Encoder"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoder", required=True, choices=ENCODERS)
    parser.add_argument("--corpora", nargs="+", choices=("textbooks", "wikipedia"), default=("textbooks", "wikipedia"))
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()
    model = ENCODERS[args.encoder]
    for corpus in args.corpora:
        chunk_dir = ROOT / "corpus" / corpus / "chunk"
        index_dir = ROOT / "corpus" / corpus / "index" / model
        if (index_dir / "faiss.index").is_file():
            print(f"Already indexed: {corpus} / {model}", flush=True)
            continue
        if not chunk_dir.is_dir():
            raise FileNotFoundError(chunk_dir)
        started = time.monotonic()
        print(f"{datetime.now(timezone.utc).isoformat()} Embedding {corpus} / {model}", flush=True)
        dimension = embed(str(chunk_dir), str(index_dir), model, batch_size=args.batch_size, show_progress_bar=False)
        index = construct_index(str(index_dir), model, h_dim=dimension, HNSW=False)
        status = {"corpus": corpus, "encoder": model, "vectors": index.ntotal, "dimension": dimension,
                  "dtype": "float32", "HNSW": False, "seconds": time.monotonic() - started,
                  "completed_at": datetime.now(timezone.utc).isoformat()}
        (index_dir / "build.json").write_text(json.dumps(status, indent=2) + "\n")
        print(json.dumps(status), flush=True)
        del index


if __name__ == "__main__":
    main()
