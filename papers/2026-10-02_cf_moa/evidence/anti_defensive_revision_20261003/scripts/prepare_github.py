"""Prepare the authorized manuscript revision in the existing private checkout."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

RUN = Path(__file__).resolve().parents[1]
WORKSPACE = Path('/home/data3/txy')
REPO = WORKSPACE / 'Documents/Codex/2026-10-02/cf_moa_paper_github'
PKG = REPO / 'papers/2026-10-02_cf_moa'
EV = PKG / 'evidence/anti_defensive_revision_20261003'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=REPO, text=True).strip():
        raise SystemExit('Publication checkout must be clean before preparation.')
    previous_head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    keep = {n: digest(PKG / n) for n in ['cf_moa_author_dossier.zip', 'cf_moa_framework.zip']}
    previous = EV / 'previous_publication'
    previous.mkdir(parents=True, exist_ok=True)
    for name in ['README.md', 'PUBLICATION.json', 'DELIVERY_MANIFEST.json', 'cf_moa_latex.zip']:
        assert not (previous / name).exists(), name
        shutil.copy2(PKG / name, previous / name)
    current_names = {str(p.relative_to(PKG / 'latex')) for p in (PKG / 'latex').rglob('*') if p.is_file()}
    new_names = {str(p.relative_to(RUN / 'release/latex')) for p in (RUN / 'release/latex').rglob('*') if p.is_file()}
    assert current_names == new_names and len(new_names) == 65
    shutil.copytree(RUN / 'release/latex', PKG / 'latex', dirs_exist_ok=True)
    shutil.copy2(RUN / 'release/latex/main.pdf', PKG / 'manuscript.pdf')
    shutil.copy2(RUN / 'cf_moa_latex.zip', PKG / 'cf_moa_latex.zip')
    for folder in ['skill', 'review', 'scripts']:
        shutil.copytree(RUN / folder, EV / folder)
    (EV / 'records').mkdir()
    shutil.copy2(WORKSPACE / 'docs/paper/writing_record.md', EV / 'records/writing_record.md')
    shutil.copy2(RUN / 'README.md', EV / 'RUN_README.md')
    (PKG / 'README.md').write_text('''# CF-MoA: English LaTeX manuscript

**2026-10-03 writing revision:** [19-page PDF](manuscript.pdf) · [Native LaTeX](latex/main.tex) · [Overleaf/source ZIP](cf_moa_latex.zip) · [Build and figure reproduction](latex/README.md).

按作者选定的 [Kiterlin anti-defensive-writing skill](https://github.com/Kiterlin/anti-defensive-writing) 修订全文14个章节：突出五类体系、benchmark、七系统诊断与CF-MoA贡献，精简重复辩解和过程旁白。3张图、14张表、29条引用及实验结果保持。独立内容审阅、编译与ZIP逐页重建验收通过。

## Read and edit

- [Section sources](latex/sections), [tables](latex/tables), [figures](latex/figures), and [BibTeX](latex/references.bib)
- [Frozen inputs](latex/inputs) and [figure/table reproduction scripts](latex/scripts)
- [Revision and validation record](evidence/anti_defensive_revision_20261003/records/writing_record.md#kiterlin-manuscript-revision-20261003)
- [Before/after diff](evidence/anti_defensive_revision_20261003/review/revision_diff.patch)
- [Independent content review](evidence/anti_defensive_revision_20261003/review/independent_review.json) and [isolated ZIP rebuild](evidence/anti_defensive_revision_20261003/review/isolated_build_receipt.json)
- [Invoked skill and fixed-source provenance](evidence/anti_defensive_revision_20261003/skill)

Edit the native `.tex` sources directly. The ZIP contains `main.tex` at its root and all required assets. The verified build uses Tectonic/XeTeX and BibTeX. This generic conference draft uses anonymous author details; authors must complete identities, affiliations, funding, contributions, and competing interests before submission.

## Coauthor material and earlier versions

The [Chinese research dossier](author_dossier/research_dossier.md), [41-page PDF](author_dossier/research_dossier.pdf), and [dossier ZIP](cf_moa_author_dossier.zip) explain the complete experimental path. The [paper framework](framework/README.md) and [framework ZIP](cf_moa_framework.zip) provide the earlier outline.

The previous 20-page manuscript and publication metadata are frozen in [the revision snapshot](evidence/anti_defensive_revision_20261003/previous_publication). Earlier full-writing evidence remains in [the original writing package](evidence/full_manuscript_20261003); its previous-publication snapshot contains the 28-page draft. Initial Markdown/Word/HTML/Typst artifacts retain their historical status.

The repository is **private**. Original datasets and third-party resources retain their licensing and access conditions. [Publication metadata](PUBLICATION.json) and [delivery manifest](DELIVERY_MANIFEST.json) identify this version.
''')
    publication = json.loads((previous / 'PUBLICATION.json').read_text())
    publication.update({'version': '2026-10-03 Kiterlin anti-defensive-writing revision', 'pages': 19,
                        'previous_remote_main': previous_head,
                        'pdf_sha256': digest(PKG / 'manuscript.pdf'),
                        'source_zip_sha256': digest(PKG / 'cf_moa_latex.zip'),
                        'editing_skill': json.loads((RUN / 'skill/provenance.json').read_text()),
                        'publication_state': 'Validated locally for authorized normal push; remote verification follows separately.'})
    (PKG / 'PUBLICATION.json').write_text(json.dumps(publication, indent=2) + '\n')
    intro = '**2026-10-03 · 论文表达修订完成：[19页PDF](papers/2026-10-02_cf_moa/manuscript.pdf) · [LaTeX](papers/2026-10-02_cf_moa/latex/main.tex) · [Overleaf ZIP](papers/2026-10-02_cf_moa/cf_moa_latex.zip)。使用作者指定的Kiterlin anti-defensive-writing，精简全文重复辩解，突出贡献与结果；原图表、数据和29引用保持，独立审阅与重编译通过。下方20页为前轮版本。**\n\n'
    p = REPO / 'README.md'
    p.write_text(intro + p.read_text())
    for name, sha in keep.items():
        assert digest(PKG / name) == sha
    rows = [{'path': str(p.relative_to(PKG)), 'bytes': p.stat().st_size, 'sha256': digest(p)}
            for p in sorted(PKG.rglob('*')) if p.is_file() and p.name != 'DELIVERY_MANIFEST.json']
    # Nested historical manifests are evidence and must also be in the current manifest.
    for p in sorted(PKG.rglob('DELIVERY_MANIFEST.json')):
        if p != PKG / 'DELIVERY_MANIFEST.json':
            rows.append({'path': str(p.relative_to(PKG)), 'bytes': p.stat().st_size, 'sha256': digest(p)})
    rows.sort(key=lambda x: x['path'])
    (PKG / 'DELIVERY_MANIFEST.json').write_text(json.dumps({'version': publication['version'], 'files': rows}, indent=2) + '\n')
    receipt = {'package_files': len(rows) + 1, 'previous_head': previous_head,
               'publication': publication, 'preserved_archives': keep}
    (RUN / 'review/github_preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'package_files': len(rows) + 1, 'previous_head': previous_head,
                      'pages': 19, 'preserved_archives': keep}, indent=2))


if __name__ == '__main__':
    main()
