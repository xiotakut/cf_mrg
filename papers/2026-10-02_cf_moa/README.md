# CF-MoA LaTeX manuscript and experimental figures

The current generic English conference draft is maintained directly in LaTeX and compiled with XeTeX and BibTeX through Tectonic 0.17.0. It uses the completed full-v5 development evaluation and the existing-result figures and tables. Subsequent writing edits go directly into the `.tex` sources; Markdown is no longer the source for document builds.

GitHub delivery directory: [`papers/2026-10-02_cf_moa`](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa). This repository is private and requires authorized access.

## Read and edit the paper

- [LaTeX main document](latex/main.tex) and [source/build guide](latex/README.md)
- [English PDF compiled from LaTeX](manuscript.pdf)
- [LaTeX / Overleaf ZIP](cf_moa_latex.zip), with `main.tex` at the archive root
- [BibTeX references](latex/references.bib)
- [Chinese outline and claim map](outline.zh.md)

Edit `latex/main.tex`, `latex/sections/*.tex`, `latex/tables/*.tex`, and `latex/references.bib` directly. The continuously maintained originals are at `/home/data3/txy/docs/paper/latex/`; the Chinese outline and writing record remain at `/home/data3/txy/docs/paper/outline.md` and `/home/data3/txy/docs/paper/writing_record.md`. This directory is the dated GitHub delivery of those sources and their compilation evidence.

The [original manuscript bundle](cf_moa_paper_bundle.zip) is unchanged. The earlier [Word document](manuscript.docx), [HTML](manuscript.html), [rendered Markdown](manuscript.readable.md), and [Markdown source](manuscript.md) remain frozen references from the initial delivery and are not synchronized with the current LaTeX manuscript. The earlier exported sources are retained as [legacy LaTeX](legacy_typst/manuscript.tex) and [legacy Typst](legacy_typst/manuscript.typ); the [frozen writing record](FROZEN_WRITING_RECORD.md) describes that earlier stage.

## Figures and tables

[Reproduction instructions](REPRODUCE.md) explain the frozen inputs, denominator checks, raw-record reaggregation, and five figures. Every figure is available as vector PDF and 300 dpi PNG:

1. [Six-arm results](figures/main_results.pdf)
2. [Verification effect intervals](figures/verification_forest.pdf)
3. [All-source heterogeneity](figures/source_heterogeneity.pdf)
4. [Support-operation ablations](figures/rule_ablations.pdf)
5. [Attributed computation and quality](figures/cost_quality.pdf)

Eight CSV/LaTeX table pairs cover main results, all contrasts, sources, categories, formats, paired outcomes, costs, and rule ablations. The [input manifest](inputs/manifest.json) binds the exact 12 frozen JSON inputs to their original paths and SHA-256 hashes.

From this directory, preferably use an isolated Python environment and install the recorded dependencies to validate the frozen inputs or rebuild the figures and tables:

```bash
python3 -m pip install matplotlib==3.10.9 numpy==1.26.4 pandas==2.3.3
python3 scripts/build_figures_tables.py --check-only
python3 scripts/build_figures_tables.py
```

## Compile the LaTeX manuscript

Install Tectonic or TeX Live with XeLaTeX, BibTeX, and latexmk. From this package directory:

```bash
cd latex
bash build.sh
```

The script selects Tectonic when available and otherwise uses `latexmk -xelatex`; it writes `latex/main.pdf`. For a separately installed Tectonic binary, run `TECTONIC_BIN=/path/to/tectonic bash build.sh` from `latex/`. The Python standard-library entry point can also compile the current source from the package root:

```bash
python3 scripts/build_manuscript.py
```

Use `--tectonic /path/to/tectonic` with the Python entry point if needed. For Overleaf, upload `cf_moa_latex.zip`, select `main.tex` as the main document, and choose XeLaTeX. The layout is a generic single-column review manuscript; a specific venue template has not been selected.

See [reproduction instructions](REPRODUCE.md) for the separate figure/table workflow and [the LaTeX build receipt](validation/latex_build_receipt.json) for the actual compiler invocation and output checks.

## Verification and boundaries

- [Figure/table build receipt](validation/build_receipt.json) and [raw-record check](validation/check_receipt.json)
- [Current LaTeX build receipt](validation/latex_build_receipt.json) and [LaTeX source audit](validation/latex_source_audit.json)
- [Historical initial-render receipt](validation/manuscript_build_receipt.json)
- [Independent numerical/method audit](validation/manuscript_fact_check.json)
- [Independent draft review](evidence/peer_review.json) and [revision resolution](evidence/revision_resolution.json)
- [Reference existence/metadata audit](evidence/reference_verification.json)
- [Claim-to-evidence map](evidence/claim_evidence_map.json)
- [Skill selection and stars](evidence/skill_selection.json)

The selected skill is `academic-paper` from Imbad0202/academic-research-skills, pinned at `9201425a88d729a74aadd75c114f2f34851a93e9`. It had 50,152 repository stars at selection and 50,154 at archival recheck on 2026-10-02. This was the highest-star directly applicable candidate found in the documented search, not a proof of a global maximum. Its workflow was adapted to the authorized Codex task; Claude hooks, the upstream 12-agent orchestration, and a certified upstream pipeline verdict were not run or claimed. Source documentation and license notices are retained under `evidence/skill_source/`.

The 13,905 inputs, 6,104 native ALL units, exposed-development status, negative results, unknown upstream costs, and deferred independent confirmation remain explicit. Author identities, affiliations, funding, conflicts, and applicable institutional ethics declarations must be completed by the authors before a submission. A writing-tool review is not external peer review or a submission-readiness certification.

Historical sources: [full-v5 snapshot](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5) (`d857934`) and [transparent closeout](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-28_cf_moa_transparent_closeout) (`2d56c71`). The [frozen writing record](FROZEN_WRITING_RECORD.md) describes the state before this GitHub delivery; its historical publication statements are retained as dated evidence.
