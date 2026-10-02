#!/usr/bin/env python3
"""Render the evidence-backed manuscript; no models, graders, or experiment writes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / '.build_deps').exists():
    sys.path.insert(0, str(ROOT / '.build_deps'))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path,
                        default=ROOT.parents[3] / 'docs/paper/manuscript.md')
    parser.add_argument('--output-root', type=Path, default=ROOT)
    parser.add_argument('--preview', action='store_true', help='Render small PDF page previews')
    args = parser.parse_args()
    start = time.monotonic()
    import pypandoc
    import typst
    import pymupdf

    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=True)
    validation = out / 'validation'
    validation.mkdir(exist_ok=True)
    source = args.source.resolve()
    source_hash = sha(source)
    text = source.read_text()
    # The workspace canonical source links to the same package's figures.
    text = text.replace('../../Documents/Codex/2026-10-02/cf_moa_paper/figures/', 'figures/')
    bib = ROOT / 'references.bib'
    cite_keys = set(re.findall(r'(?<![\w.])@([A-Za-z][A-Za-z0-9_:-]*)', text))
    bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib.read_text()))
    missing, uncited = cite_keys - bib_keys, bib_keys - cite_keys
    if missing or uncited:
        raise ValueError(f'Citation mismatch: missing={sorted(missing)}, uncited={sorted(uncited)}')
    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text):
        if not (ROOT / target).is_file():
            raise FileNotFoundError(target)
    if source != (out / 'manuscript.md').resolve():
        (out / 'manuscript.md').write_text(text)
    pandoc = pypandoc.get_pandoc_path()
    common = [pandoc, str(out / 'manuscript.md'), '--from=markdown',
              '--standalone', '--citeproc', '--bibliography', str(bib),
              '--resource-path', str(ROOT), '--number-sections']
    logs = []

    def convert(suffix: str, fmt: str, extra: list[str]) -> None:
        command = common + ['--to', fmt, '-o', str(out / f'manuscript.{suffix}')] + extra
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        logs.append(dict(command=command, returncode=result.returncode, stdout=result.stdout,
                         stderr=result.stderr))
        (validation / 'document_build_commands.json').write_text(json.dumps(logs, indent=2))
        if result.returncode:
            raise RuntimeError(result.stderr)

    # Generic readable review layout. No claim of a particular conference's template.
    convert('typ', 'typst', ['-V', 'fontsize=10.5pt', '-V', 'papersize=a4',
                            '-V', 'page-numbering=1', '-V', 'section-numbering=1.1',
                            '-V', 'columns=1'])
    typ_path = out / 'manuscript.typ'
    typ_source = typ_path.read_text()
    # Preserve the standard Pandoc template while making wide quantitative tables legible.
    typ_source = typ_source.replace('#set table(\n  inset: 6pt,', '#set table(\n  inset: 4pt,')
    # Pandoc 3.9 emits the older `sect` math alias for LaTeX \\cap;
    # Typst 0.15 uses `inter`. The LaTeX source retains the original \\cap.
    typ_source = typ_source.replace(' sect ', ' inter ')
    typ_source = typ_source.replace('#set table(\n',
        '#show table.cell: set par(justify: false)\n#show table: set text(size: 9.5pt)\n\n#set table(\n', 1)
    typ_source += '\n'
    typ_path.write_text(typ_source)
    typst.compile(str(typ_path), output=str(out / 'manuscript.pdf'), root=str(ROOT))
    convert('tex', 'latex', ['-V', 'documentclass=article', '-V', 'fontsize=11pt',
                            '-V', 'geometry:margin=0.9in', '-V', 'colorlinks=true'])
    tex_path = out / 'manuscript.tex'
    tex = tex_path.read_text()
    for stem in ['main_results', 'verification_forest', 'source_heterogeneity',
                 'rule_ablations', 'cost_quality']:
        tex = tex.replace(f'figures/{stem}.png', f'figures/{stem}.pdf')
    tex_path.write_text(tex)
    convert('docx', 'docx', [])
    convert('html', 'html5', ['--embed-resources', '--metadata', 'pagetitle=CF-MoA conference draft'])
    convert('readable.md', 'gfm', [])

    document = pymupdf.open(out / 'manuscript.pdf')
    page_texts = [page.get_text() for page in document]
    full_text = '\n'.join(page_texts)
    required = ['13,905', '6,104', '58.2924', '60.2889', '162,979',
                'Limitations', 'References', 'independent', 'unexecuted']
    absent = [s for s in required if s not in full_text]
    if absent:
        raise ValueError(f'PDF text validation missing: {absent}')
    previews = []
    if args.preview:
        preview_dir = validation / 'pdf_preview'
        preview_dir.mkdir(exist_ok=True)
        for index, page in enumerate(document):
            path = preview_dir / f'page_{index + 1:02d}.png'
            page.get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(path)
            previews.append(str(path.relative_to(out)))
    artifacts = [out / f'manuscript.{ext}' for ext in
                 ['md', 'typ', 'pdf', 'tex', 'docx', 'html', 'readable.md']]
    assert sha(source) == source_hash, 'Canonical source changed during render'
    receipt = dict(status='passed', timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   seconds=time.monotonic() - start, source=str(source), source_sha256=source_hash,
                   bibliography_sha256=sha(bib), citation_keys=sorted(cite_keys),
                   references=len(bib_keys), zero_missing_and_uncited=True,
                   pdf_pages=len(document), pdf_text_characters=len(full_text),
                   pdf_required_strings=required, layout='Generic single-column review manuscript',
                   pdf_engine='Typst via Pandoc; LaTeX source exported but not compiled',
                   model_calls=0, grader_calls=0, experiment_files_modified=0,
                   versions={k: importlib.metadata.version(k) for k in
                             ['pypandoc_binary', 'typst', 'pymupdf']},
                   pandoc_version=str(pypandoc.get_pandoc_version()),
                   artifacts=[dict(path=str(p.relative_to(out)), bytes=p.stat().st_size,
                                   sha256=sha(p)) for p in artifacts], previews=previews)
    (validation / 'manuscript_build_receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: receipt[k] for k in ['status', 'seconds', 'references', 'pdf_pages',
                                             'pdf_text_characters', 'pdf_engine']}, indent=2))


if __name__ == '__main__':
    main()
