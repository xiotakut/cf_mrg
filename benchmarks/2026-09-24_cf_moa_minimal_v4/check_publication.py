"""Read-only public-package consistency check; no models, private inputs or graders."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = read(HERE / 'PACKAGE_MANIFEST.json')['files']
    for row in files:
        path = HERE / row['path']
        assert path.is_file(), path
        assert path.stat().st_size == row['bytes'], path
        assert sha(path) == row['sha256'], path
    expected = {r['path'] for r in files} | {'PACKAGE_MANIFEST.json'}
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}
    assert actual == expected, (actual - expected, expected - actual)
    for row in read(HERE / 'SOURCE_MANIFEST.json'):
        assert sha(HERE / row['published_path']) == row['published_sha256']
    original = read(HERE / 'data/delivery_index.json')
    public = read(HERE / 'data/public_delivery_index.json')
    assert sha(HERE / 'data/delivery_index.json') == public['original_index_sha256']
    assert original['fixed_run_count'] == 10 and len(original['artifacts']) == 99
    assert len(public['artifacts']) == 99
    assert sum(r['cost']['new_model_requests'] for r in original['runs']) == 231
    assert sum(r['cost']['live_input_tokens'] for r in original['runs']) == 1444680
    assert sum(r['cost']['live_output_tokens'] for r in original['runs']) == 31047
    for old, row in zip(original['artifacts'], public['artifacts']):
        assert all(row[k] == v for k, v in old.items())
        if row['public_path']:
            target = HERE / row['public_path']
            assert target.exists() and sha(target) == row['public_sha256']
            if row['publication_status'] == 'byte_identical':
                assert sha(target) == row['sha256']
        else:
            assert row['publication_status'] == 'local_only'
    config = read(HERE / 'source_snapshot/cf_moa/configs/minimal_system.json')
    assert config['f_disagreement_reanswer'] is False
    assert config['global_generation_aggregator'] is False
    assert config['method_source_sha256'] == sha(HERE / 'source_snapshot/cf_moa/controller/minimal_operations.py')
    plan = read(HERE / 'source_snapshot/cf_moa/configs/execution_plan.json')
    assert plan['core_plan']['sha256'] == sha(HERE / 'source_snapshot/cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md')
    assert read(HERE / 'data/decision.json')['optional_control_adopted_as_default'] is False
    count = 0
    for doc in HERE.rglob('*.md'):
        for match in re.finditer(r'\]\((<[^>]+>|[^)\n]+)\)', doc.read_text()):
            link = match.group(1).strip('<>')
            parsed = urlsplit(link)
            if parsed.scheme or link.startswith('//') or not parsed.path:
                continue
            assert not parsed.path.startswith('/'), (doc, link)
            path = (doc.parent / unquote(parsed.path)).resolve()
            assert path.exists(), (doc, link)
            count += 1
    result = subprocess.run([sys.executable, str(HERE / 'scripts/verify_publication_data.py'),
        '--data-dir', str(HERE / 'data')], check=True, capture_output=True, text=True)
    data_check = json.loads(result.stdout)
    print(json.dumps(dict(status='passed', package_files=len(expected), original_artifacts=99,
        relative_links=count, public_data_check=data_check, new_model_calls=0,
        native_scoring_calls=0, private_source_access=False,
        interpretation='Document/hash/saved arithmetic check; not independent scientific replication'), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
