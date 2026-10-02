# Seven-system medical QA study — LaTeX manuscript

Edit `main.tex`, `sections/*.tex`, `tables/*.tex`, and `references.bib` directly. This is the maintained manuscript source. The initial prose was migrated once from the frozen Markdown draft; subsequent document builds compile LaTeX directly.

The study presents seven full-v5 baseline configurations, seven-system R1–R3 terminal-head development results, and the later M4/M5 six-arm CF-MoA comparison as distinct experimental stages. M4 and M5 are two MedRAG configurations; the seven rows span six method families.

The project contains the complete English manuscript, eleven manuscript tables, six vector figures, and twenty-four bibliography entries. The layout is a generic single-column review manuscript, not a specific conference template. Author names and affiliations remain to be supplied by the authors.

## Build

Install [Tectonic](https://github.com/tectonic-typesetting/tectonic) (the recorded build uses 0.17.0), or a TeX Live installation with XeLaTeX, BibTeX, and latexmk. From this directory:

```bash
bash build.sh
```

The script prefers Tectonic when available; otherwise it runs `latexmk -xelatex`. It resolves citations with BibTeX and writes `main.pdf`, retaining compilation logs and intermediates under `build/`. The first Tectonic build downloads required TeX packages. To use a separately installed binary:

```bash
TECTONIC_BIN=/path/to/tectonic bash build.sh
```

To build manually with TeX Live:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

For Overleaf, upload the files with their directory structure intact, choose `main.tex` as the main document, and select XeLaTeX. The published `cf_moa_latex.zip` includes this project and its compiled PDF.

## Contents

- `main.tex`: document class, preamble, chapter order, and bibliography configuration.
- `sections/`: abstract, main sections, declarations, and appendices.
- `tables/`: eleven native LaTeX manuscript tables with labels and cross-references.
- `figures/`: six vector PDFs derived from saved results.
- `references.bib`: twenty-four primary-source-checked bibliography records, used through natbib and BibTeX.
- `build.sh`: direct LaTeX compilation; no Markdown, Pandoc, or Typst dependency.

The broader delivery directory contains the frozen numerical inputs, CSV/LaTeX data tables, and figure reproduction script. Compiling this manuscript does not execute model inference or native grading. The exposed-development status, negative results, default B, and unexecuted independent confirmation remain part of the paper.
