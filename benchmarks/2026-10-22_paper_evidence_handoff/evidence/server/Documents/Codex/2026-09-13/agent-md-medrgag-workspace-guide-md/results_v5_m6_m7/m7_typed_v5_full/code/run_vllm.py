import sys

# The existing vLLM environment supplies the engine; the pinned MedRAG site
# supplies compatible Transformers and Pyserini, as in the completed M4 run.
sys.path.insert(0, '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')

if __name__ == '__main__':
    from run import main
    main()
