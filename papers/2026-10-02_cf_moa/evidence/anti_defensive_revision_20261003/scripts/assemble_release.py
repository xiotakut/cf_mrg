"""Refresh the previously verified 65-file LaTeX package from the canonical source."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

RUN = Path(__file__).resolve().parents[1]
SRC = Path('/home/data3/txy/docs/paper/latex')
OUT = RUN / 'release/latex'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(RUN / 'before_cf_moa_latex.zip') as previous:
        names = sorted(n for n in previous.namelist() if not n.endswith('/'))
    for name in names:
        if name == 'SOURCE_MANIFEST.json':
            continue
        source, target = SRC / name, OUT / name
        assert source.is_file(), source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    rows = [{'path': n, 'bytes': (OUT / n).stat().st_size, 'sha256': digest(OUT / n)}
            for n in names if n != 'SOURCE_MANIFEST.json']
    provenance = json.loads((RUN / 'skill/provenance.json').read_text())
    manifest = {'title': 'CF-MoA: Taxonomy-Guided Benchmarking and Agent Orchestration for Counterfactual Medical Reasoning',
                'version': '2026-10-03 Kiterlin anti-defensive-writing revision',
                'source': 'native LaTeX', 'files': rows,
                'editing_skill': provenance, 'new_model_calls': 0, 'new_grader_calls': 0}
    (OUT / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    shutil.copy2(OUT / 'SOURCE_MANIFEST.json', SRC / 'SOURCE_MANIFEST.json')
    archive = RUN / 'cf_moa_latex.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in names:
            z.write(OUT / name, name)
    receipt = {'files_in_zip': len(names), 'zip_sha256': digest(archive),
               'pdf_sha256': digest(OUT / 'main.pdf'), 'release_dir': str(OUT),
               'archive': str(archive), 'package_members_unchanged': True}
    (RUN / 'review/release_assembly.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
