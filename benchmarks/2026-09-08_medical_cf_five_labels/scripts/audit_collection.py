"""Audit published-source fidelity independently of collection/build outputs.

Run with the existing MedRGAG Python (pyarrow is needed for published Parquet).
The dated evidence directory holds independently fetched originals and reviewed
paper-to-author links. A cached run rechecks content, not today's website state.
"""
import argparse
import csv
import json
import math
import re
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'audit_20260908'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def jl(path):
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def absolute(path):
    p = Path(path)
    return p.resolve() if p.is_absolute() else (ROOT.parent / p).resolve()


def normalized(value):
    # The published MedCounterFact JSON contains NaN; the collection uses null.
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def bytes_equal(a, b):
    if a.stat().st_size != b.stat().st_size:
        return False
    with a.open('rb') as af, b.open('rb') as bf:
        while True:
            x, y = af.read(1024 * 1024), bf.read(1024 * 1024)
            if x != y:
                return False
            if not x:
                return True


@lru_cache(maxsize=4)
def xlsx_cells(path, sheet):
    """Decode populated native XLSX cells, preserving strings and numeric text."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(t.itertext()) for t in
                      ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        rows = []
        for row in ET.fromstring(z.read(f'xl/worksheets/sheet{sheet}.xml')).findall('.//s:row', NS):
            cells = {}
            for c in row.findall('s:c', NS):
                v = c.find('s:v', NS)
                if c.get('t') == 'inlineStr':
                    value = ''.join(c.find('s:is', NS).itertext())
                elif v is None:
                    continue
                elif c.get('t') == 's':
                    value = shared[int(v.text)]
                else:
                    value = v.text or ''
                cells[c.get('r')] = value
            rows.append((int(row.get('r')), cells))
        return rows


@lru_cache(maxsize=4)
def xlsx_rows(path, sheet, lab=False):
    cells = xlsx_cells(path, sheet)
    headers = {re.sub(r'\d', '', k): v for k, v in cells[0][1].items()}
    if lab:
        headers['A'] = 'source_index'
    return {n: {headers[re.sub(r'\d', '', k)]: v for k, v in r.items()}
            for n, r in cells[1:]}


def url_identity(url):
    u = urlsplit(url)
    if u.hostname in {'drive.google.com', 'drive.usercontent.google.com'}:
        m = re.search(r'/file/d/([^/]+)', u.path)
        return ('drive', m[1] if m else parse_qs(u.query).get('id', [''])[0])
    if u.hostname == 'raw.githubusercontent.com':
        bits = u.path.strip('/').split('/')
        return ('github', '/'.join(bits[:2]), '/'.join(bits[2:]))
    if u.hostname == 'github.com':
        bits = u.path.strip('/').split('/')
        return ('github', '/'.join(bits[:2]), '/'.join(bits[3:]) if len(bits) > 2 else '')
    if u.hostname == 'huggingface.co':
        bits = u.path.strip('/').split('/')
        return ('hf', '/'.join(bits[:3]), '/'.join(bits[4:]) if len(bits) > 3 else '')
    return ('url', url.rstrip('/'))


def url_matches(source, entry):
    a = url_identity(source)
    for url in [entry['remote_url']] + entry.get('equivalent_source_urls', []):
        b = url_identity(url)
        if a == b or (len(a) == len(b) == 3 and a[:2] == b[:2] and a[2] == ''):
            return True
    return False


class Originals:
    def __init__(self):
        self.entries = [r for group in ('origin_a', 'origin_b')
                        for r in jl(AUDIT / group / 'files.jsonl')]
        self.files = {str(absolute(r['cached_file'])): r for r in self.entries
                      if r.get('cached_file') and r.get('fetched')}
        self.used = set()
        self.root_links = {}
        for r in jl(ROOT / 'parts/evidence_other/full_root_records.jsonl'):
            v = r['original_records'][0]
            self.root_links[(r['resource_id'], r['source_root_id'])] = {
                k: v[k] for k in ('question_id', 'Question') if k in v}

    def entry(self, source):
        key = str(absolute(source['file']))
        if re.search(r'/M16/sheet_\d+\.json$', key):
            key = str(Path(key).with_name('equitymedqa_ratings.xlsx'))
        self.used.add(key)
        return self.files[key]

    def find(self, rid, suffix):
        candidates = [v for k, v in self.files.items()
                      if v['resource_id'] == rid and k.endswith(suffix)]
        if len(candidates) != 1:
            raise ValueError(f'Expected one official {rid}/{suffix}, found {len(candidates)}')
        self.used.add(str(absolute(candidates[0]['cached_file'])))
        return candidates[0]

    @lru_cache(maxsize=12)
    def read(self, path):
        path = Path(path)
        if path.suffix == '.parquet':
            import pyarrow.parquet as pq
            return normalized(pq.read_table(path).to_pylist())
        if path.suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as f:
                return list(csv.DictReader(f))
        if path.suffix == '.jsonl' or path.name.startswith('BioNELL_'):
            return normalized(list(jl(path)))
        return normalized(json.loads(path.read_text()))

    def data(self, entry):
        return self.read(str(absolute(entry['downloaded_file'])))

    def expected(self, unit, role='unit'):
        rid, src = unit['resource_id'], unit['source']
        entry = self.entry(src)
        if entry['resource_id'] != rid:
            raise ValueError('Official file belongs to a different benchmark: ' + entry['resource_id'])
        path, loc = absolute(entry['downloaded_file']), src['locator']
        additional = {}
        method = 'exact_record_values'
        if rid == 'M06':
            # Independently transcribed/reviewed against the publisher PDF.
            rows = {r['record']['N']: r for r in jl(AUDIT / 'origin_a/transcription_audit.jsonl')}
            n = int(re.search(r'N=(\d+)', loc)[1])
            check = rows[n]
            if check['verdict'] != 'verified':
                raise ValueError(f'PDF transcription {n} not verified')
            expected = [check['record']]
            method = 'publisher_pdf_transcription_checked'
        elif rid == 'M05':
            rows = xlsx_rows(str(path), 1, lab=True)
            n = int(re.search(r'Sheet1 row (\d+)', loc)[1])
            expected = [dict(worksheet='Sheet1', row_number=i, record=rows[i],
                             role='counterfactual' if i == n else 'original_sequence_reference')
                        for i in range(n - 2, n + 1)]
            if rows[n]['Causal Type'] != 'Counterfactual':
                raise ValueError('Source row is not Counterfactual')
            method = 'xlsx_cells_redecoded'
        elif rid == 'M16':
            sheet = int(re.search(r'sheet_(\d+)', src['file'])[1])
            n = int(re.search(r'row(\d+)', loc)[1])
            row = xlsx_rows(str(path), sheet)[n]
            expected = [row]
            ratings = xlsx_rows(str(path), 4)
            additional['original_ideal_answer_assessments'] = [
                {k: r[k] for k in ('rater_id', 'rater_type', 'ideal_answers_diff')}
                for r in ratings.values() if r['question_1_id'] == row['question_1_id']
                and r['question_2_id'] == row['question_2_id']]
            method = 'xlsx_cells_redecoded'
        else:
            rows = self.data(entry)
            if rid == 'M01':
                a, b = map(int, re.search(r'lines (\d+),(\d+)', loc).groups())
                expected = [rows[a - 1], rows[b - 1]]
                if expected[0]['case_id'] != expected[1]['case_id'] or [r['case_type'] for r in expected] != ['control', 'trap']:
                    raise ValueError('Not an official control/trap pair')
            elif rid in ('M02', 'M11', 'M24', 'M25'):
                n = int(re.search(r'\[(\d+)\]', loc)[1])
                expected = [rows[n]]
                if rid == 'M11' and role != 'root':
                    kind, part = re.search(r'\.(t\d_question)\.(\w+)', loc).groups()
                    additional = dict(reference_text=rows[n]['original_question'], variant_text=rows[n][kind][part])
                if rid == 'M02' and rows[n]['benchmark_task_family'] != 'counterfactual':
                    raise ValueError('Collected MedPIC row is not official CF')
            elif rid in ('M10', 'M22'):
                n = int(re.search(r'parquet row (\d+)', loc)[1])
                row = rows[n]
                if rid == 'M10':
                    expected = [row]
                    additional = dict(reference_text=row['question'], variant_text=row['case_text'])
                else:
                    main = {k: row[k] for k in ('question_id', 'question', 'options', 'answer', 'answer_option', 'must_have', 'nice_to_have')}
                    docs = json.loads(row['counterfactual_documents'])
                    if role == 'root':
                        expected = [dict(main, signal_documents=json.loads(row['signal_documents']), sub_qa_pairs=json.loads(row['sub_qa_pairs']))]
                    elif role == 'reference':
                        expected = [d for d in docs if d['document_id'] == 'options']
                    else:
                        expected = [main, {'counterfactual_documents': [d for d in docs if d['document_id'] != 'options']}]
                    method = 'documented_field_projection_and_json_decode'
            elif rid == 'M12':
                n = int(re.search(r'JSONL line (\d+)', loc)[1]) - 1
                row = rows[n]
                if role == 'root':
                    expected = [row]
                else:
                    variant = unit['source_unit_id'].split(':', 1)[1]
                    fields = ['question_id', 'original_question', 'desensitized_question', 'options', 'answer', 'answer_idx', 'adv_description_' + variant, 'adv_question_' + variant]
                    expected = [{k: row[k] for k in fields}]
                    method = 'documented_field_projection'
            elif rid == 'M14':
                n = int(re.search(r'CSV data row (\d+)', loc)[1]) - 1
                row = rows[n]
                if role == 'root':
                    expected = [row]
                else:
                    variant = loc.split('Question / ', 1)[1]
                    expected = [{k: row[k] for k in ('', 'Question', 'Row Number', variant)}]
                    method = 'documented_field_projection'
            elif rid == 'M17':
                v, b = map(int, re.search(r'CSV-record (\d+).*baseline record=(\d+)', loc).groups())
                expected = [dict(role=rows[n - 2]['perturbation'], source_csv_record=n, record=rows[n - 2]) for n in (b, v)]
                if rows[b - 2]['context_id'] != rows[v - 2]['context_id'] or rows[b - 2]['perturbation'] != 'baseline':
                    raise ValueError('Baseline and variant do not share official context_id')
            elif rid == 'M20':
                n = int(re.search(r'JSONL row (\d+)', loc)[1])
                row = rows[n]
                original = self.data(self.find('M20', '00-MedCounterFact_original_data.jsonl'))
                matches = [r for r in original if r['metadata']['id'] == row['metadata']['id']]
                if len(matches) != 1:
                    raise ValueError('MedCounterFact reference is not unique by official metadata.id')
                expected = [matches[0], row]
                additional = dict(reference_text=matches[0]['question'], variant_text=row['question'])
                method = 'exact_record_values_nan_to_null'
            elif rid == 'M23':
                n = int(re.search(r'JSONL row (\d+)', loc)[1]) - 1
                row = rows[n]
                if role == 'root':
                    expected = [{k: row[k] for k in ('context', 'response', 'category')}]
                else:
                    clean = self.data(self.find('M23', '/BioNELL_test_instruction_medcpt.json'))[n]
                    if clean['context'] != row['context'] or clean['response'] != row['response']:
                        raise ValueError('BioRAB clean/noise target mismatch')
                    expected = [clean, row]
            else:
                raise ValueError(f'No original-record adapter for {rid}')
        if role != 'root':
            source_id = None
            if rid == 'M01':
                source_id = expected[0]['case_id']
            elif rid == 'M02':
                source_id = expected[0]['instance_id']
            elif rid == 'M10':
                source_id = expected[0]['case_id']
            elif rid == 'M11':
                source_id = str(n)
            elif rid == 'M12':
                source_id = str(expected[0]['question_id']) + ':' + variant
            elif rid == 'M20':
                source_id = str(expected[1]['metadata']['id'])
            elif rid == 'M24':
                source_id = path.stem + ':' + str(n)
            elif rid == 'M25':
                source_id = 'eval:' + str(expected[0]['id'])
            if source_id is not None:
                additional['source_unit_id'] = source_id
        return expected, additional, method, entry


def mismatch_paths(expected, actual, path='original_records'):
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            return [path + ':keys']
        return [p for k in expected for p in mismatch_paths(expected[k], actual[k], path + '.' + str(k))]
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [path + ':length']
        return [p for i, (a, b) in enumerate(zip(expected, actual)) for p in mismatch_paths(a, b, f'{path}[{i}]')]
    return [] if expected == actual else [path]


def check_unit(bank, unit, role):
    result = dict(resource_id=unit['resource_id'], unit_id=unit.get('unit_id', unit.get('source_unit_id', unit.get('source_root_id'))), role=role)
    try:
        expected, extra, method, entry = bank.expected(unit, role)
        actual = unit['original_records']
        if unit['resource_id'] == 'M06':
            def pdf_normalize(records):
                return [{k: re.sub(r'\s+', '', v.replace('\u2019', "'")) if isinstance(v, str) else v
                         for k, v in r.items()} for r in records]
            errors = mismatch_paths(pdf_normalize(expected), pdf_normalize(actual))
        else:
            errors = mismatch_paths(expected, actual)
        for k, value in extra.items():
            errors.extend(mismatch_paths(value, unit.get(k), k))
        ref = unit.get('root_record_ref')
        if ref:
            if absolute(ref['file']) != (ROOT / 'parts/evidence_other/full_root_records.jsonl').resolve():
                errors.append('root_record_ref.file:not_audited')
            link = bank.root_links[(ref['resource_id'], ref['source_root_id'])]
            if ref['resource_id'] != unit['resource_id']:
                errors.append('root_record_ref.resource_id')
            for k, v in link.items():
                if unit['original_records'][0].get(k) != v:
                    errors.append('root_record_ref.' + k)
        result.update(status='mismatch' if errors else 'verified', method=method,
                      differences=errors, official_file=entry['downloaded_file'],
                      source_url_status='verified' if url_matches(unit['source']['url'], entry) else 'needs_url_review')
    except (KeyError, ValueError, IndexError, FileNotFoundError, AttributeError) as e:
        result.update(status='unverified', reason=str(e))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        # Corrupted question/gold, removed field and a wrong owner's URL must not pass.
        original = [{'question': 'original', 'answer': ['A'], 'context': 'C'}]
        assert not mismatch_paths(original, original)
        for damaged in [[{'question': 'invented', 'answer': ['A'], 'context': 'C'}],
                        [{'question': 'original', 'answer': ['B'], 'context': 'C'}],
                        [{'question': 'original', 'answer': ['A']}]]:
            assert mismatch_paths(original, damaged)
        entry = {'remote_url': 'https://raw.githubusercontent.com/author/data/rev/test.json'}
        assert url_matches('https://github.com/author/data/blob/rev/test.json', entry)
        assert not url_matches('https://github.com/impostor/data/blob/rev/test.json', entry)
        bank = Originals()
        real = next(jl(ROOT / '全部比较单元.jsonl'))
        assert check_unit(bank, real, 'unit')['status'] == 'verified'
        corrupt = json.loads(json.dumps(real))
        corrupt['original_records'][0]['narrative'] += ' invented clinical condition'
        assert check_unit(bank, corrupt, 'unit')['status'] == 'mismatch'
        corrupt = dict(real, source=dict(real['source'], file='/missing-original.jsonl'))
        assert check_unit(bank, corrupt, 'unit')['status'] == 'unverified'
        print('corruption detection self-test passed')
        return
    out = AUDIT / 'provenance'
    out.mkdir(exist_ok=True)
    bank = Originals()
    counts = defaultdict(Counter)
    frozen_ids = {r['unit_id'] for r in jl(ROOT / 'review_20260908/input_manifest.jsonl')}
    issues = []
    for fn, role in [('全部比较单元.jsonl', 'unit'), ('分析子集.jsonl', 'frozen'), ('parts/evidence_other/full_root_records.jsonl', 'root'), ('参照与不计CF记录.jsonl', 'reference')]:
        with (out / (role + 's.jsonl')).open('w') as f:
            for unit in jl(ROOT / fn):
                result = check_unit(bank, unit, role)
                counts[role][result['status']] += 1
                counts[role + ':' + unit['resource_id']][result['status']] += 1
                if role == 'unit' and unit['unit_id'] in frozen_ids:
                    counts['frozen_from_full'][result['status']] += 1
                if result.get('source_url_status') == 'needs_url_review':
                    counts['source_url_review:' + role][unit['resource_id']] += 1
                if result['status'] != 'verified':
                    issues.append(result)
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        print(role, dict(counts[role]), flush=True)
    file_checks = []
    for key in sorted(bank.files):
        entry = bank.files[key]
        local, remote = Path(key), absolute(entry['downloaded_file'])
        equal = local.exists() and remote.exists() and bytes_equal(local, remote)
        file_checks.append(dict(resource_id=entry['resource_id'], cached_file=key,
                                official_file=str(remote), remote_url=entry['remote_url'],
                                used_in_collected_records=key in bank.used,
                                status='verified' if equal else 'mismatch_or_missing'))
    # MedPIC's additional GF reference copy must also reproduce the full release.
    gf = ROOT / 'parts/clinical_existing/raw/medpic_questions_all467.json'
    official = bank.data(bank.find('M02', '/00-questions.json'))
    gf_errors = mismatch_paths(official, json.loads(gf.read_text()), 'MedPIC_reference_copy')
    reference_check = dict(file=str(gf), total_rows=len(official),
                           gf_rows=sum(r['benchmark_task_family'] == 'guideline_following' for r in official),
                           status='mismatch' if gf_errors else 'verified', differences=gf_errors)
    resources = [r for group in ('origin_a', 'origin_b') for r in jl(AUDIT / group / 'resources.jsonl')]
    controls = list(jl(AUDIT / 'origin_a/control_resources.jsonl'))
    registry_ids = {r['resource_id'] for r in json.loads((ROOT / '资源目录.json').read_text())}
    reviewed_ids = {r['resource_id'] for r in resources}
    source_verdicts = dict(Counter(r['verdict'] for r in resources))
    summary = dict(audit_date='2026-09-08', network_mode='independently_downloaded_dated_snapshots',
                   source_catalog_review_count=len(resources), missing_catalog_reviews=sorted(registry_ids - reviewed_ids),
                   source_catalog_verdicts=source_verdicts,
                   control_source_review_count=len(controls),
                   control_source_verdicts=dict(Counter(r['verdict'] for r in controls)),
                   counts={k: dict(v) for k, v in counts.items()}, used_raw_files=len(bank.used),
                   cached_file_comparisons=len(file_checks),
                   independently_downloaded_files_compared=len({r['official_file'] for r in file_checks}),
                   raw_file_results=dict(Counter(r['status'] for r in file_checks)),
                   medpic_reference_check=reference_check, record_issue_count=len(issues),
                   boundaries=['Verified means fidelity to the published data, not medical correctness of author-generated data.',
                               'Paper-to-author links and PDF transcription need reviewed evidence; HTTP 200 alone never verifies authenticity.',
                               'Original source-owned response columns are compared as data only; no model outcome determines functional labels.',
                               'Missing multimodal images are not audited as present; text metadata fidelity does not certify image input completeness.'])
    dump(out / 'summary.json', summary)
    for fn, rows in [('files.jsonl', file_checks), ('resources.jsonl', resources), ('controls.jsonl', controls), ('findings.jsonl', issues)]:
        with (out / fn).open('w') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with (AUDIT / '来源审核表.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['编号', '名称', '目录角色', '来源结论', '实际论文题名', '第一手链接', 'CF任务依据', '完整库记录', '分析子集记录', '数据取得状态', '限制'])
        for r in resources + controls:
            rid = r['resource_id']
            writer.writerow([rid, r.get('benchmark'), r.get('catalog_role', '医学CF候选'), r['verdict'],
                             r['actual_title'], '\n'.join(r['primary_urls']), r['cf_scope_verdict'],
                             sum(counts.get('unit:' + rid, {}).values()), sum(counts.get('frozen:' + rid, {}).values()),
                             r.get('data_provenance_verdict', r.get('local_data_status')), '\n'.join(r.get('limitations', []))])
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    unresolved = (issues or summary['missing_catalog_reviews'] or gf_errors
                  or source_verdicts != {'verified': len(registry_ids)}
                  or {r['resource_id'] for r in controls} != {'C01', 'C02'}
                  or any(r['verdict'] != 'verified' for r in controls)
                  or any(k.startswith('source_url_review:') for k in counts)
                  or any(r['status'] != 'verified' for r in file_checks))
    classification = subprocess.run([sys.executable, str(AUDIT / 'check_classification.py')], check=False)
    annotation_report = json.loads((ROOT / 'reports/classification_review.json').read_text())
    classification_report = json.loads((AUDIT / 'classification/summary.json').read_text())
    current_review = classification_report.get('correction_review', {})
    dump(AUDIT / 'audit_status.json', dict(
        source_status='needs_review' if unresolved else 'verified',
        source_summary='provenance/summary.json',
        classification_status='passed_within_review_scope' if classification.returncode == 0 else 'needs_review',
        classification_exit_code=classification.returncode,
        classification_summary='classification/summary.json',
        audit_run_modifies_data_or_labels=False,
        annotation_corrections_applied_before_audit=annotation_report.get('audit_corrected_judgments', 0),
        remaining_label_problems=current_review.get('remaining_label_problems'),
        original_references_excluded_from_scoring=current_review.get('gold_scoring_exclusions')))
    raise SystemExit(1 if unresolved or classification.returncode else 0)


if __name__ == '__main__':
    main()
