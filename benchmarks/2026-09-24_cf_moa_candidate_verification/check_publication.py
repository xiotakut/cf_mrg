"""Read-only check of published saved artifacts, not inference or native scoring."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    manifest = read(ROOT / 'PACKAGE_MANIFEST.json')
    for row in manifest['files']:
        path = ROOT / row['path']
        assert path.is_file(), row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
    index = read(ROOT / 'data/public_delivery_index.json')
    original = ROOT / 'data/original_delivery_index.json'
    assert sha(original) == index['original_index_sha256']
    original_rows = read(original)['files']
    assert index['original_artifacts'] == len(original_rows) == len(index['artifacts']) == 116
    for raw, projected in zip(original_rows, index['artifacts']):
        assert all(projected[k] == raw[k] for k in ('path', 'sha256', 'bytes'))
        if projected['public_path']:
            path = ROOT / projected['public_path']
            assert path.is_file() and sha(path) == projected['public_sha256'], path
    relative = 0
    for path in ROOT.rglob('*.md'):
        # Source snapshots retain original server references, explicitly documented.
        if 'source_snapshot' in path.parts: continue
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for match in re.finditer(r'\]\((<[^>]+>|[^)\n]+)\)', text):
            raw = match[1].strip('<>')
            url = urlsplit(raw)
            if url.scheme or raw.startswith('//') or not url.path: continue
            target = (path.parent / unquote(url.path)).resolve()
            assert target.exists(), (str(path.relative_to(ROOT)), raw)
            relative += 1
    reports = read(ROOT / 'data/quality_summary.json')
    if isinstance(reports, dict): reports = reports['reports']
    assert len(reports) == 40
    expected = {
        ('historical121', 'M4', 'F'): 87, ('historical121', 'M5', 'F'): 82,
        ('natural52', 'M4', 'F'): 35, ('natural52', 'M5', 'F'): 26,
        ('historical121', 'M4', 'candidate_only'): 87, ('historical121', 'M5', 'candidate_only'): 83,
        ('natural52', 'M4', 'candidate_only'): 33, ('natural52', 'M5', 'candidate_only'): 27,
        ('historical121', 'M4', 'candidate_with_rationales'): 88, ('historical121', 'M5', 'candidate_with_rationales'): 87,
        ('natural52', 'M4', 'candidate_with_rationales'): 35, ('natural52', 'M5', 'candidate_with_rationales'): 28,
    }
    for r in reports:
        assert r['counts']['denominator'] == (121 if r['panel'] == 'historical121' else 52)
        key = (r['panel'], r['method'], r['arm'])
        if key in expected: assert r['counts']['correct'] == expected[key], key
    costs = read(ROOT / 'data/cost_summary.json')
    if isinstance(costs, dict): costs = costs['costs']
    added = [r['extra_execution'] for r in costs if r['arm'] in ('candidate_only', 'candidate_with_rationales')]
    totals = {k: sum(r[k] for r in added) for k in ('physical_model_requests', 'live_input_tokens', 'live_output_tokens')}
    assert totals == dict(physical_model_requests=780, live_input_tokens=5504408, live_output_tokens=780)
    data_check = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'data/verify_public_data.py')], text=True))
    print(json.dumps(dict(public_data_check=data_check, status='passed', package_files=len(manifest['files']) + 1,
                         original_artifacts=116, relative_links=relative, quality_groups=40,
                         saved_new_call_totals=totals, new_model_calls=0, new_native_scores=0,
                         private_source_access=False,
                         interpretation='Published byte and saved-result consistency only; not independent clinical replication'), ensure_ascii=False))


if __name__ == '__main__': main()
