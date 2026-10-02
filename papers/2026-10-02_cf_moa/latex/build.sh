#!/usr/bin/env bash
# Compile the maintained LaTeX source directly; no Markdown/Typst conversion.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p build

if command -v "${TECTONIC_BIN:-tectonic}" >/dev/null 2>&1; then
    "${TECTONIC_BIN:-tectonic}" --keep-logs --keep-intermediates \
        --synctex --outdir build main.tex
elif command -v latexmk >/dev/null 2>&1; then
    latexmk -xelatex -interaction=nonstopmode -halt-on-error \
        -file-line-error -outdir=build main.tex
else
    echo "Install Tectonic or TeX Live with latexmk and XeLaTeX, then rerun bash build.sh." >&2
    echo "For an existing Tectonic binary: TECTONIC_BIN=/path/to/tectonic bash build.sh" >&2
    exit 127
fi

cp build/main.pdf main.pdf
printf 'Compiled LaTeX PDF: %s/main.pdf\n' "$PWD"
