#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p framework_build
if [[ -n "${TECTONIC_BIN:-}" ]]; then
  "$TECTONIC_BIN" --keep-logs --outdir framework_build framework.tex
elif command -v tectonic >/dev/null 2>&1; then
  tectonic --keep-logs --outdir framework_build framework.tex
else
  latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=framework_build framework.tex
fi
cp framework_build/framework.pdf framework.pdf
