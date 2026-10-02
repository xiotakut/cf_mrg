#!/usr/bin/env python3
"""Assemble the manuscript's source closure and its frozen figure inputs."""
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'draft'
OUT = ROOT / 'release' / 'latex'

README = r'''# CF-MoA — complete English LaTeX manuscript

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
'''

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    seen = set()
    def copy(relative):
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / relative, target)
    def visit(relative):
        if relative in seen:
            return
        seen.add(relative)
        copy(relative)
        text = re.sub(r'(?m)(?<!\\)%.*$', '', (SRC / relative).read_text())
        for child in re.findall(r'\\input\{([^}]+)\}', text):
            visit(child if child.endswith('.tex') else child + '.tex')
        for fig in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', text):
            f = Path(fig)
            if not f.suffix:
                f = f.with_suffix('.pdf')
            if not (SRC / f).exists():
                f = Path('figures') / f
            copy(str(f))
            if (SRC / f.with_suffix('.png')).exists():
                copy(str(f.with_suffix('.png')))
    visit('main.tex')
    for f in ['references.bib', 'build.sh', 'main.pdf']:
        copy(f)
    for f in (SRC/'tables').glob('*.csv'):
        copy(str(f.relative_to(SRC)))
    for folder in ['scripts', 'audit']:
        (OUT/folder).mkdir()
    for name in ['build_paper_figures.py', 'build_appendix_tables.py']:
        shutil.copy2(ROOT/'scripts'/name, OUT/'scripts'/name)
    shutil.copytree(ROOT/'inputs', OUT/'inputs')
    for name in ['figure_audit.json', 'figure_rebuild_check.json', 'figure_portability_check.json']:
        shutil.copy2(ROOT/'review'/name, OUT/'audit'/name)
    shutil.copy2(SRC/'tables/appendix_table_audit.json', OUT/'audit/appendix_table_audit.json')
    (OUT/'README.md').write_text(README)
    (OUT/'Makefile').write_text('all:\n\tbash build.sh\n\nclean:\n\trm -rf build\n')
    (OUT/'requirements-figures.txt').write_text('matplotlib==3.10.9\n')
    files = [{'path':str(p.relative_to(OUT)), 'bytes':p.stat().st_size, 'sha256':digest(p)}
             for p in sorted(OUT.rglob('*')) if p.is_file()]
    manifest = {'title':'CF-MoA: Taxonomy-Guided Benchmarking and Agent Orchestration for Counterfactual Medical Reasoning',
                'version':'2026-10-03 full manuscript', 'source':'native LaTeX',
                'files':files, 'new_model_calls':0, 'new_grader_calls':0}
    (OUT/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive = ROOT/'cf_moa_latex.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, str(p.relative_to(OUT)))
    receipt = {'files_in_zip':len(files)+1, 'zip_bytes':archive.stat().st_size,
               'zip_sha256':digest(archive), 'pdf_sha256':digest(OUT/'main.pdf'),
               'source_closure':sorted(seen)}
    (ROOT/'review/release_assembly.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
