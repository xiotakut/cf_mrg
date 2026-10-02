# Compile the LaTeX manuscript and reproduce the saved-result figures and tables

This package renders three completed stages: seven full-v5 baseline configurations; seven-system R1–R3 terminal-head development results; and the later M4/M5 six-arm CF-MoA full-v5 **development** evaluation. It does not run models, invoke native graders, create new experimental outcomes, or overwrite the September 28 closeout. The independent post-freeze confirmation and independent F-pool replica were not executed. The default remains B; C3 is an optional research extension.

## Compile and maintain the manuscript

The maintained manuscript source is [latex/main.tex](latex/main.tex), with native LaTeX chapters and tables under `latex/sections/` and `latex/tables/`, vector figures under `latex/figures/`, and [BibTeX references](latex/references.bib). Edit those files directly. Document builds compile LaTeX; they do not regenerate the source from Markdown.

Install Tectonic, or TeX Live with XeLaTeX, BibTeX, and latexmk. The recorded successful compilation used Tectonic 0.17.0. From this package directory:

```bash
cd latex
bash build.sh
```

The script prefers Tectonic and otherwise uses `latexmk -xelatex`. It writes `latex/main.pdf` and retains compilation logs and intermediates under `latex/build/`. Tectonic downloads any required TeX packages on its first build. To select a separately installed binary, run `TECTONIC_BIN=/path/to/tectonic bash build.sh` from `latex/`.

Alternatively, from the package root use the Python standard-library entry point:

```bash
python3 scripts/build_manuscript.py
```

The optional `--tectonic /path/to/tectonic` selects the compiler binary. [The LaTeX build receipt](validation/latex_build_receipt.json) and [source audit](validation/latex_source_audit.json) record the current compilation and source checks. The distributed `manuscript.pdf` is the LaTeX-compiled manuscript.

For Overleaf, upload [cf_moa_latex.zip](cf_moa_latex.zip), select the archive-root `main.tex` as the main document, and choose XeLaTeX. The archive preserves the required chapter, table, figure, and bibliography paths; [latex/README.md](latex/README.md) also documents direct TeX Live compilation.

The original [cf_moa_paper_bundle.zip](cf_moa_paper_bundle.zip) is unchanged. The root Word, HTML, and Markdown files are frozen references from the earlier delivery, and the prior exported LaTeX/Typst sources reside in `legacy_typst/`. Those earlier formats are not synchronized with the current LaTeX manuscript; historical rendering receipts describe their original build.

## Seven-system additions (2026-10-03)

`inputs/scope/input_manifest.json` binds the frozen baseline CSV, head CSV, and audit summaries to their recorded source hashes. These summaries were checked against complete saved scoring files: 42 baseline values and 21 head before/after pairs match. The three overlapping head strata contain 2,941 unique units; they are not three independent datasets. R2 facts were generated on two backbones and combined offline with seven saved system answers; diagnostic heads use each system's saved context. These files do not constitute seven new end-to-end reruns.

Validate the shipped scope inputs (Python standard library only):

```bash
python3 scripts/build_scope_figures_tables.py \
  --input-dir inputs/scope --manifest inputs/scope/input_manifest.json \
  --check-only --receipt validation/scope_check_receipt.json
```

Rebuild the three added manuscript tables and the vector/PNG comparison figure using matplotlib:

```bash
python3 scripts/build_scope_figures_tables.py \
  --input-dir inputs/scope --manifest inputs/scope/input_manifest.json \
  --output-dir latex --receipt validation/scope_build_receipt.json
```

This script reads saved aggregate evidence; it does not re-import the original native graders or access model weights. The original raw-score reaggregation was performed separately and is documented in `evidence/scope_20261003/`. The source paths and hashes identify server-side evidence; not all raw prediction files are included in this package. Rebuilding tables from frozen summaries is distinct from rerunning the systems.

## Retained six-arm figure and table inputs and dependencies

`inputs/manifest.json` records original absolute paths, byte sizes, and SHA-256 hashes of 12 exact copies of small saved JSON summaries (about 160 kB). All retained six-arm plotted values and table values are derived from those copies; the seven-system additions use the separate scope manifest above. The script checks their hashes before and after execution. The source closeout was published at commit `2d56c71`; its full-v5 underlying release was `d85793470cf75af57217f3fdc73093f494d9f003`.

The existing environment used for the actual build was `/home/data3/txy/MedRGAG/.venv/bin/python` with Python 3, matplotlib 3.10.9, numpy 1.26.4, and pandas 2.3.3. No environment changes were made. A separate environment with those packages can render the bundle elsewhere. LaTeX tables require `booktabs` and `longtable`; the plotting script itself does not require a TeX installation. PDF figure fonts are embedded as TrueType, and PNG exports use 300 dpi.

From this package directory, rebuild figures and tables using only the shipped summaries:

```bash
python3 scripts/build_figures_tables.py
```

Validate the shipped summaries without rewriting figures or tables:

```bash
python3 scripts/build_figures_tables.py --check-only
```

For an independent re-aggregation of the original saved record files, pass the local original-record directory:

```bash
python3 scripts/build_figures_tables.py \
  --check-only \
  --raw-root ../../benchmarks/2026-09-26_cf_moa_rcv_full_v5/data/full_v5
```

The example `--raw-root` assumes a checkout of this repository with the historical `benchmarks/2026-09-26_cf_moa_rcv_full_v5/data/full_v5` directory present. The optional `--raw-root` must contain `m4/` and `m5/`, each with `native_units.jsonl.gz`, `per_input_status.jsonl.gz`, and `pairs.jsonl.gz`. These larger original files are not duplicated in this small package. The raw check reads saved scores only; no scoring function is imported. It independently verifies 72 category means, 132 source means, 60 format strata, 24 paired outcomes, all 12 method/arm input totals, unique row keys, and before/after raw-file hashes. Use the same flag during a full build to save both raw validation and figure output hashes in one receipt. Original record paths are configurable; missing files cause an explicit failure.

`--input-root`, `--output-root`, and `--receipt` override the default locations. Check-only mode writes only its JSON receipt, not the experiment inputs, tables, or figures. Receipts include the exact command, script hash, dependency versions for rendering, elapsed time, zero model/grader calls, validation results, and generated artifact hashes. The actual build and raw checks are recorded in `validation/build_receipt.json` and `validation/check_receipt.json`.

## Artifacts

Five retained CF-MoA figure stems under `figures/`, each available as PDF and PNG; the added seven-system comparison is under `latex/figures/seven_system_heads.*`:

- `main_results`: all six arms on both backbones, with a zero-origin vertical axis.
- `verification_forest`: C3 minus B and C3 minus C2, for native ALL, maintain-pair correctness, and respond-pair correctness. These are saved 95% paired-family bootstrap intervals, not new resamples.
- `source_heterogeneity`: C3 minus B on every one of the 11 saved source IDs; all sources remain visible, including small and negative strata.
- `cost_quality`: native ALL against attributed head/readout requests. Historical C0/retrieval costs are unknown for every arm; C0 has no known cost coordinate and is explicitly described as unplottable on this axis. This is not an end-to-end monetary or latency frontier.
- `rule_ablations`: existing add/remove operation ablations on 123 rule inputs per backbone. It is a shared-kernel mechanism subset, not a full-v5 system ablation.

Eight table stems under `tables/`, each in CSV and LaTeX: `main_results`, `contrasts`, `sources`, `categories`, `formats`, `paired`, `costs`, and `ablations`. CSVs retain machine-readable details; LaTeX versions use compact publication layouts. CSV units are explicit in column names or the copied source field names: `mean_native_unit_score`, `input_accuracy`, and `full_both_correct_rate` are fractions; `ALL_percent`, `delta_pp`, and interval columns are percentages/percentage points. LaTeX rate tables display percentages. `unknown` denotes missing cost evidence, never zero expense.

## Interpretation constraints

Every arm/backbone retains 13,905 inputs and 15,616 native mappings. Native ALL averages the original non-reference scores within each unit and then weights the 6,104 unique units equally. It differs from input accuracy. R1--R5 categories overlap. Family intervals use the existing 5,000 paired bootstrap draws with seed 240924 and preserve unit weights within families. They describe exposed development data and do not correct method selection or multiple comparisons.

The all-source table partitions the 6,104 ALL units; the five input-format strata partition the 13,905 inputs. Maintain and respond metrics retain 6,838 and 1,780 pairs respectively. Failed/unavailable outcomes remain in all relevant denominators. Cost attribution gives each candidate the common B cost once plus its own increment; these per-method totals must not be added across arms or divided into the physical experiment bill. Complete upstream cost and 2,503 historical input times per backbone/arm remain unknown.
