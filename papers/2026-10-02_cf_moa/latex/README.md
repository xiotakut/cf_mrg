# CF-MoA — complete English LaTeX manuscript

This is the 2026-10-03 full manuscript based on the completed coauthor research dossier.
Its main thread is the five-relation taxonomy, benchmark construction, seven configured
systems, specialized heads, and the adopted five-role CF-MoA controller. The appendix
contains the complete six-arm and component comparisons. This generic conference layout
uses anonymous author information; the author declarations must be completed before submission.

## Compile

Open `main.tex` in Overleaf and select XeLaTeX, or run:

```bash
bash build.sh
```

The script uses Tectonic when installed, otherwise `latexmk -xelatex`, and writes
`build/main.pdf` and `main.pdf`. A standalone Tectonic binary can be supplied with
`TECTONIC_BIN=/path/to/tectonic bash build.sh`. References use BibTeX and natbib.
The verified build used Tectonic 0.17.0. Install the TeX packages once before an offline build.

## Edit

Edit `main.tex`, `sections/*.tex`, `tables/*.tex`, and `references.bib` directly.
The three scientific figures are vector PDFs; PNG previews are also included.
`SOURCE_MANIFEST.json` records the delivered file hashes. This package is separate from
the Chinese author dossier and the earlier framework, which remain available in the repository.

## Rebuild figures and tables from saved results

The supplied JSON inputs are frozen summaries of already completed experiments.
The following commands regenerate artifacts without running inference or a grader:

```bash
python scripts/build_paper_figures.py --input-dir inputs/figures --output-dir . --review-dir audit
python scripts/build_appendix_tables.py --inputs inputs/full_results --output tables
python scripts/build_paper_figures.py --input-dir inputs/figures --output-dir . --review-dir audit --check-only
```

Figure generation requires Python 3.10+ and Matplotlib (verified with 3.10.9);
appendix table generation uses the Python standard library. Do not use `--freeze-inputs`
when reproducing the released results: that optional maintenance flag intentionally
reads the original workspace. Ordinary builds use only the included frozen input files.
The result JSON files include the original identities and denominators; `audit/` contains
the figure and table receipts. Native generation/scoring and dataset acquisition have
additional model, retrieval, and source-access dependencies documented in the companion
research records. Rebuilding a plot from saved scores is distinct from rerunning an experiment.

The repository is private. Original datasets, guidelines, models, and simulator resources
remain subject to their own distribution terms. This source package adds no new rights
to those resources.
