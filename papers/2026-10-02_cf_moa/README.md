# CF-MoA conference manuscript and experimental figures

This package accompanies the generic English conference draft based on the completed full-v5 development evaluation. It contains existing-result figures, tables, document sources, and reproducible rendering scripts. It does not add model experiments, change labels, or replace the adopted B system.

GitHub delivery directory: [`papers/2026-10-02_cf_moa`](https://github.com/xiotakut/cf_mrg/tree/main/papers/2026-10-02_cf_moa). [Download the original manuscript bundle](cf_moa_paper_bundle.zip) for the unchanged, pre-publication delivery snapshot. The files displayed in this directory have GitHub navigation and portable command examples; the original archive preserves the initial delivery and its manifest.

## Read the paper

- [English PDF](manuscript.pdf)
- [Editable Word document](manuscript.docx)
- [Self-contained HTML](manuscript.html)
- [Rendered Markdown with references](manuscript.readable.md)
- [LaTeX source](manuscript.tex), [Typst source used for the PDF](manuscript.typ), and [BibTeX](references.bib)
- [Chinese outline and claim map](outline.zh.md)

The continuously maintained originals remain in the local workspace at `/home/data3/txy/docs/paper/manuscript.md`, `/home/data3/txy/docs/paper/outline.md`, and `/home/data3/txy/docs/paper/writing_record.md`. This package provides dated snapshots of [the manuscript](manuscript.md), [the outline](outline.zh.md), and [the writing record](FROZEN_WRITING_RECORD.md), together with reproduction evidence.

## Figures and tables

[Reproduction instructions](REPRODUCE.md) explain the frozen inputs, denominator checks, raw-record reaggregation, and five figures. Every figure is available as vector PDF and 300 dpi PNG:

1. [Six-arm results](figures/main_results.pdf)
2. [Verification effect intervals](figures/verification_forest.pdf)
3. [All-source heterogeneity](figures/source_heterogeneity.pdf)
4. [Attributed computation and quality](figures/cost_quality.pdf)
5. [Support-operation ablations](figures/rule_ablations.pdf)

Eight CSV/LaTeX table pairs cover main results, all contrasts, sources, categories, formats, paired outcomes, costs, and rule ablations. The [input manifest](inputs/manifest.json) binds the exact 12 frozen JSON inputs to their original paths and SHA-256 hashes.

From this directory, preferably use an isolated Python environment and install the recorded dependencies to validate the frozen inputs or rebuild the figures and tables:

```bash
python3 -m pip install -r requirements-build.txt
python3 scripts/build_figures_tables.py --check-only
python3 scripts/build_figures_tables.py
```

## Document reproduction

The recorded document renderer uses Python 3.10, Pandoc 3.9 through `pypandoc_binary==1.17`, `typst==0.15.0`, and `pymupdf==1.28.2`. These optional build dependencies were installed only into this package's `.build_deps` directory, not the experiment environment. That directory is excluded from the portable archive. To recreate it using an existing Python/pip installation:

```bash
python3 -m pip install --target .build_deps pypandoc_binary==1.17 typst==0.15.0 pymupdf==1.28.2
python3 scripts/build_manuscript.py --source manuscript.md --preview
```

Always pass `--source manuscript.md` when building this GitHub copy. The script's default source refers to `docs/paper/manuscript.md` in the original workspace; the recorded original interpreter was `/home/data3/txy/MedRGAG/.venv/bin/python`.

PDF output uses a generic single-column conference-review layout, compiled by Typst. It is not a specific venue's template. LaTeX is exported as an editable, standalone source; it was not compiled because no TeX engine is installed. The build applies one documented Pandoc 3.9 to Typst 0.15 math-alias compatibility replacement (`sect` to `inter` for set intersection); the original LaTeX equation is unchanged.

## Verification and boundaries

- [Figure/table build receipt](validation/build_receipt.json) and [raw-record check](validation/check_receipt.json)
- [Manuscript render receipt](validation/manuscript_build_receipt.json)
- [Independent numerical/method audit](validation/manuscript_fact_check.json)
- [Independent draft review](evidence/peer_review.json) and [revision resolution](evidence/revision_resolution.json)
- [Reference existence/metadata audit](evidence/reference_verification.json)
- [Claim-to-evidence map](evidence/claim_evidence_map.json)
- [Skill selection and stars](evidence/skill_selection.json)

The selected skill is `academic-paper` from Imbad0202/academic-research-skills, pinned at `9201425a88d729a74aadd75c114f2f34851a93e9`. It had 50,152 repository stars at selection and 50,154 at archival recheck on 2026-10-02. This was the highest-star directly applicable candidate found in the documented search, not a proof of a global maximum. Its workflow was adapted to the authorized Codex task; Claude hooks, the upstream 12-agent orchestration, and a certified upstream pipeline verdict were not run or claimed. Source documentation and license notices are retained under `evidence/skill_source/`.

The 13,905 inputs, 6,104 native ALL units, exposed-development status, negative results, unknown upstream costs, and deferred independent confirmation remain explicit. Author identities, affiliations, funding, conflicts, and applicable institutional ethics declarations must be completed by the authors before a submission. A writing-tool review is not external peer review or a submission-readiness certification.

Historical sources: [full-v5 snapshot](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-26_cf_moa_rcv_full_v5) (`d857934`) and [transparent closeout](https://github.com/xiotakut/cf_mrg/tree/main/benchmarks/2026-09-28_cf_moa_transparent_closeout) (`2d56c71`). The [frozen writing record](FROZEN_WRITING_RECORD.md) describes the state before this GitHub delivery; its historical publication statements are retained as dated evidence.
