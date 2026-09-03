#!/usr/bin/env python3
"""Launch MA-RAG retrieval once, avoiding its script-mode double initialization."""

import argparse
import importlib
import jnius_config
import sys
from pathlib import Path

import uvicorn


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--marag-repo", type=Path, default=Path("/home/data3/txy/MA-RAG"))
known, remaining = parser.parse_known_args()
original = jnius_config.add_options
jnius_config.add_options = lambda *values: original(
    *(value for value in values if "jdk.incubator.vector" not in value))
sys.argv = [str(known.marag_repo / "microservice/RetrievalSystem.py"), *remaining]
sys.path.insert(0, str(known.marag_repo))
retrieval_module = importlib.import_module("microservice.RetrievalSystem")

args = retrieval_module.init_retriever()
uvicorn.run(retrieval_module.app, host="0.0.0.0", port=args.port,
            log_level="info", loop="uvloop")
