# CF-MoA: taxonomy, benchmark and five-agent framework

This is the 2026-10-03 framework revision, prepared before rewriting the full paper. Read the [Chinese logic chain and evidence selection](outline.zh.md), [native LaTeX framework](framework.tex), and [10-page English PDF](framework.pdf). The prior [28-page manuscript](../manuscript.pdf) remains unchanged.

The story follows resource collection → five functional categories → benchmark construction → seven-system diagnosis → specialized heads → five-role CF-MoA → complete system and mechanism evaluation. The main comparison contains all seven baselines and the two adopted B instantiations, with every R1–R5 category retained. No predictions, labels, scores, or evaluation membership were changed.

## Contents

- `framework.tex`, `framework.pdf`, `references.bib`, `tables/`, `figures/`: native LaTeX framework, three generated data tables plus two structural tables, two vector figures, eight cited references.
- `inputs/manifest.json`: two frozen audit inputs with SHA-256 hashes.
- `scripts/build_story_assets.py` and `generated/`: portable offline reproduction of all three CSV/LaTeX tables and PDF/PNG figures.
- `evidence/`: data, agent-framework, full research-path audits and independent text review.
- `records/`: dated snapshots of relevant master records and both continuous process reports; ongoing records remain in workspace `docs/`. Historical record links preserve their original workspace provenance and are not all portable.
- `validation/`: compilation and numerical checks, acronym review, and build log. Three harmless underfull table warnings remain; there are no unresolved references or overfull boxes.

## Reproduce existing results

```bash
python3 scripts/build_story_assets.py --check-only
python3 scripts/build_story_assets.py
bash build_framework.sh
```

Only regeneration of the figures needs Matplotlib (recorded 3.10.9); input/table checks use the standard library. The script resolves defaults relative to itself and supports `--input-dir` and `--output-dir`. It does not run models, grading, or simulations. Generated data tables map to the LaTeX includes as follows: `system_comparison.tex` → `tables/story_main_results.tex`; `paired_behavior.tex` → `tables/story_pairs.tex`; `benchmark_composition.tex` → `tables/story_sources.tex`. Figures map from `story_map.pdf` and `system_results.pdf` to `figures/story_map.pdf` and `figures/story_system_results.pdf`. Refresh these copies after deliberately changing frozen inputs; no refresh is required for the delivered sources.

Install Tectonic or TeX Live with XeLaTeX/BibTeX/latexmk. `TECTONIC_BIN=/path/to/tectonic bash build_framework.sh` selects an explicit compiler. For Overleaf upload the sibling `cf_moa_framework.zip`, select `framework.tex` as the main document, and use XeLaTeX. The ZIP contains the compact source project and compiled PDF; the full audit and reconstruction evidence stays in this directory.

## Scope

Five agents are functional roles. A1/A2 share a rule kernel; A4 is conditional on a supplied executable model and has no clinical-v5 activation. The adopted system uses sparse capability routing. Actual generative aggregation trials and all later six-arm results remain in the records and previous delivery. Complete-v5 improvements are 10.09/12.01 percentage points versus the corresponding MedRAG baseline. These are exposed-development comparisons with differing resources, not a claim of independently confirmed five-agent synergy.

The installed academic-paper skill guided the outline/evidence-map workflow; this is not a certified upstream multi-agent pipeline verdict. The repository remains private.
