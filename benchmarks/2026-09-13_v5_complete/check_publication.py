"""Offline checks for the published v5 tables and documentation. No model calls."""
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
LATEST = BASE / 'completion/v5_benchmark_latest'
METHODS = ['M0', 'M2', 'M3', 'M4', 'M5']


def rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def check():
    manifest = rows(BASE / 'SOURCE_MANIFEST.csv')
    for row in manifest:
        assert (REPO / row['published_path']).is_file(), row['published_path']
    scores = {r['category']: r for r in rows(LATEST / 'category_scores_merged.csv')}
    assert set(scores) == {'R1', 'R2', 'R3', 'R4', 'R5', 'ALL'}
    inputs = {
        'original': BASE / 'execution/results_v5_m0_m2_m4_m5/unit_scores.csv',
        'M3': BASE / 'execution/results_v5_m3/unit_scores.csv',
        'M4': BASE / 'completion/results_v5_m4_structured/scores/unit_scores.csv',
    }
    groups = defaultdict(list)
    ids = defaultdict(set)
    for version, path in inputs.items():
        for row in rows(path):
            method = row['method']
            if version == 'original' and method == 'M4':
                continue
            key = (row['category'], method)
            assert row['unit_id'] not in ids[key], (key, row['unit_id'])
            ids[key].add(row['unit_id'])
            groups[key].append(float(row['score']))
    for category, row in scores.items():
        for method in METHODS:
            values = groups[category, method]
            assert len(values) == int(row['units']), (category, method, len(values))
            assert math.isclose(sum(values) / len(values) * 100, float(row[method]), abs_tol=1e-8)
        assert math.isclose(sum(float(row[m]) for m in METHODS) / 5, float(row['method_mean']), abs_tol=1e-8)
    losses = rows(LATEST / 'loss_by_method.csv')
    assert len(losses) == 25
    for row in losses:
        assert math.isclose(sum(float(row[k]) for k in ['correct', 'format_invalid', 'unmapped_diagnosis', 'valid_but_wrong']), 100, abs_tol=1e-8)
        assert math.isclose(float(row['correct']), float(scores[row['category']][row['method']]), abs_tol=1e-8)
    validity = rows(LATEST / 'validity.csv')
    assert {r['method'] for r in validity} == set(METHODS)
    for row in validity:
        assert int(row['unique_inputs']) == 13905 and int(row['mapped_records']) == 15616
        for field in ['format_valid', 'native_valid']:
            assert math.isclose(int(row[field]) / 13905 * 100, float(row[field + '_pct']), abs_tol=1e-8)
    m4 = json.loads((BASE / 'completion/results_v5_m4_structured/complete.json').read_text())
    assert (m4['unique_inputs'], m4['native_records'], m4['missing'], m4['duplicates']) == (13905, 15616, 0, 0)
    m4row = next(r for r in validity if r['method'] == 'M4')
    for field in ['format_valid', 'native_valid']:
        assert m4['validity'][field] == int(m4row[field])
    # Inspect this publication's Markdown paths, not external sites or historic source code.
    docs = list(BASE.rglob('*.md')) + [REPO / 'README.md', REPO / 'benchmarks/README.md', REPO / 'README_HISTORY.md']
    links = 0
    broken = []
    for path in docs:
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text):
            target = target.strip('<>')
            if target.startswith(('http:', 'https:', 'mailto:', '#', 'data:')):
                continue
            target = unquote(target.split('#')[0])
            if not target:
                continue
            links += 1
            resolved = path.parent / target
            if target.startswith('/') or (not resolved.exists() and resolved.resolve() != BASE / 'publication_validation.json'):
                broken.append((str(path.relative_to(REPO)), target))
    assert not broken, broken
    return {
        'status': 'passed', 'source_files': len(manifest),
        'source_documents': sum(r['published_path'].endswith('.md') for r in manifest),
        'markdown_documents_checked': len(docs), 'local_links_checked': links,
        'method_category_scores_recomputed_from_unit_csv': 30,
        'loss_decomposition_rows_checked': len(losses),
        'validity_denominators_checked': len(validity),
        'm4_complete_receipt_matches': True, 'inference_requests': 0,
        'scope': 'Published tables, archived completion evidence and local Markdown targets; raw prediction caches are not included or re-audited by this check.',
    }


if __name__ == '__main__':
    result = check()
    (BASE / 'publication_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
