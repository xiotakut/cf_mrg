#!/usr/bin/env bash
set -euo pipefail
MEDRAG_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export JAVA_HOME="${JAVA_HOME:-/home/data3/txy/.cache/jdk/temurin21}"
export PATH="$JAVA_HOME/bin:$MEDRAG_ROOT/.venv/bin:$PATH"
export TMPDIR="$MEDRAG_ROOT/.cache/tmp"
export HF_HOME="${HF_HOME:-$MEDRAG_ROOT/.cache/huggingface}"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
exec "$MEDRAG_ROOT/.venv/bin/python" "$MEDRAG_ROOT/run_baseline.py" "$@"
