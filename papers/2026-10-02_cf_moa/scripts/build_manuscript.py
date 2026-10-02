#!/usr/bin/env python3
"""Compile the maintained LaTeX project; no document conversion or model calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tectonic', help='Optional path to a Tectonic binary')
    args = parser.parse_args()
    project = ROOT / 'latex'
    validation = ROOT / 'validation'
    validation.mkdir(exist_ok=True)
    env = os.environ.copy()
    if args.tectonic:
        env['TECTONIC_BIN'] = args.tectonic
    sources = sorted(p for p in project.rglob('*')
                     if p.is_file() and 'build' not in p.relative_to(project).parts
                     and p.name != 'main.pdf')
    hashes = {str(p.relative_to(project)): sha(p) for p in sources}
    started = time.monotonic()
    command = ['bash', str(project / 'build.sh')]
    result = subprocess.run(command, cwd=project, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (validation / 'latex_rebuild_console.log').write_text(result.stdout)
    print(result.stdout, end='')
    if result.returncode:
        raise SystemExit(result.returncode)
    for name, expected in hashes.items():
        if sha(project / name) != expected:
            raise RuntimeError(f'Source changed during build: {name}')
    log = (project / 'build/main.log').read_text()
    bbl = (project / 'build/main.bbl').read_text()
    if re.search(r'undefined|Missing character|^!', log, re.MULTILINE):
        raise RuntimeError('Unresolved references, missing glyphs, or TeX errors; inspect latex/build/main.log')
    shutil.copy2(project / 'main.pdf', ROOT / 'manuscript.pdf')
    receipt = {
        'status': 'passed',
        'finished_at': datetime.now(timezone.utc).isoformat(),
        'seconds': time.monotonic() - started,
        'command': command,
        'source_sha256': hashes,
        'pdf_sha256': sha(ROOT / 'manuscript.pdf'),
        'bibliography_items': len(re.findall(r'\\bibitem', bbl)),
        'warnings': re.findall(r'^.*(?:Overfull|Underfull|Warning).*$', log, re.MULTILINE),
        'requires_markdown_pandoc_typst': False,
        'model_calls': 0,
        'grader_calls': 0,
    }
    path = validation / 'latex_rebuild_receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'LaTeX build receipt: {path}')


if __name__ == '__main__':
    main()
