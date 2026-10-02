#!/usr/bin/env python3
"""Stage the authorized private-repository manuscript update, without committing."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=Path('/home/data3/txy')
REPO=WORKSPACE/'Documents/Codex/2026-10-02/cf_moa_paper_github'
PKG=REPO/'papers/2026-10-02_cf_moa'
EVIDENCE=PKG/'evidence/full_manuscript_20261003'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def manifest():
    rows=[{'path':str(p.relative_to(PKG)),'bytes':p.stat().st_size,'sha256':digest(p)}
          for p in sorted(PKG.rglob('*')) if p.is_file() and p != PKG/'DELIVERY_MANIFEST.json']
    out={'version':'2026-10-03 full native LaTeX manuscript','files':rows}
    (PKG/'DELIVERY_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    return len(rows)

def main():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    previous=EVIDENCE/'previous_publication';previous.mkdir(exist_ok=True)
    for name in ['README.md','PUBLICATION.json','DELIVERY_MANIFEST.json','cf_moa_latex.zip']:
        if not (previous/name).exists():shutil.copy2(PKG/name,previous/name)
    dossier=PKG/'cf_moa_author_dossier.zip';dossier_hash=digest(dossier)
    old_framework_hash=digest(PKG/'cf_moa_framework.zip')
    if (PKG/'latex').exists():shutil.rmtree(PKG/'latex')
    shutil.copytree(ROOT/'release/latex',PKG/'latex')
    shutil.copy2(ROOT/'release/latex/main.pdf',PKG/'manuscript.pdf')
    shutil.copy2(ROOT/'cf_moa_latex.zip',PKG/'cf_moa_latex.zip')
    for folder in ['review','skill']:
        if (EVIDENCE/folder).exists():shutil.rmtree(EVIDENCE/folder)
        shutil.copytree(ROOT/folder,EVIDENCE/folder)
    for name in ['paper_configuration.json','outline.json']:
        shutil.copy2(ROOT/name,EVIDENCE/name)
    (EVIDENCE/'scripts').mkdir(exist_ok=True)
    for name in ['verify_manuscript.py','prepare_release.py','prepare_github.py']:
        if (ROOT/'scripts'/name).exists():shutil.copy2(ROOT/'scripts'/name,EVIDENCE/'scripts'/name)
    (EVIDENCE/'records').mkdir(exist_ok=True)
    for name in ['writing_record.md','outline.md']:
        shutil.copy2(WORKSPACE/'docs/paper'/name,EVIDENCE/'records'/name)
    (PKG/'README.md').write_text('''# CF-MoA: complete English LaTeX manuscript

**2026-10-03 full rewrite:** [20-page PDF](manuscript.pdf) · [Native LaTeX](latex/main.tex) · [Overleaf/source ZIP](cf_moa_latex.zip) · [Build and figure reproduction](latex/README.md).

完整英文通用会议论文，以五类功能体系、benchmark构建、七系统诊断、五head及CF-MoA串成完整主线。正文突出采用B的两配置全量结果；附录保留六臂、全部类别、来源、格式、组件对照和成本。3张矢量图、14张表、29条参考文献。已有预测、标签和评分未修改；本轮没有新增实验。

## Read and edit

- [main.tex](latex/main.tex), [section sources](latex/sections), [tables](latex/tables), [figures](latex/figures), and [BibTeX](latex/references.bib)
- [Frozen figure/result inputs](latex/inputs) and [reproduction scripts](latex/scripts)
- [Writing, factual, bibliography, layout, and rebuild receipts](evidence/full_manuscript_20261003/review)
- [Skill workflow and evidence-to-claim map](evidence/full_manuscript_20261003/skill/workflow_record.json)

The manuscript is a complete generic conference draft, with anonymous author details. Author identities, affiliations, funding, contributions, and competing interests must be completed before submission. Edit the `.tex` sources directly. The archive contains `main.tex` at its root and all included assets; the verified build uses Tectonic/XeTeX and BibTeX.

## Coauthor research material

The [complete Chinese research dossier](author_dossier/research_dossier.md), [41-page reading PDF](author_dossier/research_dossier.pdf), and [dossier archive](cf_moa_author_dossier.zip) remain unchanged. They explain the entire experimental path and preserve the detailed positive and negative history. The new English manuscript is a scientific narrative built from that dossier, rather than a literal translation.

The [earlier paper framework](framework/README.md) and [framework ZIP](cf_moa_framework.zip) remain historical artifacts. The prior 28-page English source archive and publication metadata are preserved in [the previous-publication snapshot](evidence/full_manuscript_20261003/previous_publication). The initial Markdown/Word/HTML/Typst deliverables are also historical; they are not synchronized sources for the current manuscript.

The repository remains **private**. Source data and third-party resources retain their original licensing and access conditions. [Publication metadata](PUBLICATION.json) and [delivery manifest](DELIVERY_MANIFEST.json) identify this package.
''')
    publication={
        'version':'2026-10-03 full manuscript from author dossier',
        'title':'CF-MoA: Taxonomy-Guided Benchmarking and Agent Orchestration for Counterfactual Medical Reasoning',
        'repository':'xiotakut/cf_mrg','visibility':'private','branch':'main',
        'format':'English native LaTeX, generic two-column conference + one-column appendix',
        'pdf':'manuscript.pdf','pages':20,'figures':3,'tables':14,'references':29,
        'source_zip':'cf_moa_latex.zip','source_zip_members':65,
        'pdf_sha256':digest(PKG/'manuscript.pdf'),'source_zip_sha256':digest(PKG/'cf_moa_latex.zip'),
        'previous_remote_main':'787e63c83733af5c2f8f124077ffd1d1f96e0efd',
        'preserved_dossier_zip_sha256':dossier_hash,'preserved_framework_zip_sha256':old_framework_hash,
        'new_experiment_inference':0,'new_grading':0,
        'publication_state':'Prepared for normal authorized push; remote verification recorded separately after push.'}
    (PKG/'PUBLICATION.json').write_text(json.dumps(publication,indent=2)+'\n')
    prefix='''**2026-10-03 · 完整英文论文：[20页PDF](papers/2026-10-02_cf_moa/manuscript.pdf) · [原生LaTeX](papers/2026-10-02_cf_moa/latex/main.tex) · [Overleaf工程ZIP](papers/2026-10-02_cf_moa/cf_moa_latex.zip)。从五类体系、benchmark、七系统、五head到CF-MoA完成全文，3图/14表/29引用；[作者raw底稿](papers/2026-10-02_cf_moa/author_dossier/README.md)与历史框架保留。仓库private，本轮0新增实验。**

'''
    p=REPO/'README.md';s=p.read_text()
    if not s.startswith(prefix):p.write_text(prefix+s)
    assert digest(dossier)==dossier_hash and digest(PKG/'cf_moa_framework.zip')==old_framework_hash
    count=manifest()
    receipt={'manifest_entries':count,'package_files':count+1,'source_files':65,
             'dossier_unchanged':True,'framework_unchanged':True,'publication':publication}
    (ROOT/'review/github_preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
