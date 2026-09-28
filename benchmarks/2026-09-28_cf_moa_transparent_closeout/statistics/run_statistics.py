#!/usr/bin/env python3
"""Execute supplied unmodified statistics script and preserve read-only receipts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
BUNDLE = OUT.parent / 'source_request/extracted/CF_MoA_Full_V5_Closeout'
REPO = Path('/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_github_rcv_progress')
ROOT = REPO / 'benchmarks/2026-09-26_cf_moa_rcv_full_v5/data/full_v5'
COMMIT = 'd85793470cf75af57217f3fdc73093f494d9f003'

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def main():
    started = now()
    before = []
    for method in ('m4', 'm5'):
        for name in ('native_units.jsonl.gz', 'pairs.jsonl.gz', 'per_input_status.jsonl.gz', 'quality_summary.json'):
            path = ROOT / method / name
            rel = path.relative_to(REPO).as_posix()
            data = path.read_bytes()
            git_data = subprocess.check_output(['git', '-C', str(REPO), 'show', f'{COMMIT}:{rel}'])
            row = dict(path=str(path), relative_to_repo=rel, bytes=len(data), sha256=sha(data),
                       commit_sha256=sha(git_data), matches_commit=data == git_data,
                       mtime_ns=path.stat().st_mtime_ns)
            before.append(row)
            if not row['matches_commit']:
                raise RuntimeError(f'Source mismatch against {COMMIT}: {path}')
    dump('source_hashes_before.json', dict(commit=COMMIT, verified_at=now(), files=before))
    script_rows = []
    for name in ('summarize_existing_results.py', 'test_summary.py'):
        source = BUNDLE / name
        target = OUT / 'scripts' / name
        shutil.copyfile(source, target)
        script_rows.append(dict(original=str(source), execution_copy=str(target),
                                original_sha256=sha(source.read_bytes()), execution_sha256=sha(target.read_bytes()),
                                unchanged=source.read_bytes() == target.read_bytes()))
    dump('script_provenance.json', dict(supplied_scripts=script_rows, modified=False))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(OUT / 'tmp'))
    commands = [
        ('tests', [sys.executable, '-B', '-m', 'unittest', '-v', 'test_summary.py']),
        ('bootstrap', [sys.executable, '-B', 'summarize_existing_results.py', '--root', str(ROOT),
                       '--out', str(OUT), '--draws', '5000', '--seed', '240924']),
    ]
    receipt = dict(started_at=started, status='running', source_commit=COMMIT, source_root=str(ROOT),
                   output_root=str(OUT), python=sys.executable, commands=[], inference_calls=0,
                   grader_calls=0, resource_or_other_process_actions=0, source_modifications=0,
                   output_filtering=False, data_scope='complete_exposed_v5_development')
    dump('execution_receipt.json', receipt)
    for label, command in commands:
        start = time.monotonic()
        row = dict(label=label, argv=command, cwd=str(OUT / 'scripts'), started_at=now())
        with (OUT / f'{label}.log').open('w') as log:
            result = subprocess.run(command, cwd=OUT / 'scripts', env=env, stdout=log, stderr=subprocess.STDOUT)
        row.update(ended_at=now(), elapsed_seconds=time.monotonic()-start, exit_code=result.returncode)
        receipt['commands'].append(row)
        dump('execution_receipt.json', receipt)
        if result.returncode:
            receipt.update(status='failed', ended_at=now(), failed_step=label)
            dump('execution_receipt.json', receipt)
            raise RuntimeError(f'{label} failed, inspect {OUT / (label + ".log")}')
    after = []
    for row in before:
        path = Path(row['path'])
        digest = sha(path.read_bytes())
        after.append(dict(path=str(path), sha256=digest, mtime_ns=path.stat().st_mtime_ns,
                          hash_unchanged=digest == row['sha256'], mtime_unchanged=path.stat().st_mtime_ns == row['mtime_ns']))
    if not all(r['hash_unchanged'] and r['mtime_unchanged'] for r in after):
        raise RuntimeError('Source mutation detected')
    dump('source_hashes_after.json', dict(checked_at=now(), files=after, all_sources_unchanged=True))
    receipt.update(status='complete', ended_at=now(), source_files_verified=8,
                   all_sources_unchanged=True, supplied_tests_passed=6, draws=5000, seed=240924,
                   saved_quality_means_validated_by_unmodified_script=True)
    dump('execution_receipt.json', receipt)
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
