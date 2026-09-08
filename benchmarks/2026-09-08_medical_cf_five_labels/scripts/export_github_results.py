"""Export annotations and audit results; original benchmark bodies stay on server."""
import argparse
import gzip
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def annotations(row):
    return without_originals({k: v for k, v in row.items() if k not in {
        'original_records', 'original_raw_response', 'reviewed_original_records',
        'pre_review_annotation', 'initial_labels', 'existing_evaluation_records',
    }})


def without_originals(value):
    if isinstance(value, dict):
        return {k: without_originals(v) for k, v in value.items()
                if k not in {'original_records', 'original_raw_response', 'reviewed_original_records'}}
    if isinstance(value, list):
        return [without_originals(v) for v in value]
    return value


def export(destination):
    destination.mkdir(parents=True, exist_ok=True)
    counts = {}

    def jsonl(source, target, transform=annotations):
        output = destination / target
        output.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with gzip.open(output, 'wt', encoding='utf-8', compresslevel=6) as stream:
            for row in rows(ROOT / source):
                stream.write(json.dumps(transform(row), ensure_ascii=False) + '\n')
                count += 1
        counts[target] = count

    for source, target in [
        ('全部比较单元.jsonl', 'data/complete_annotations.jsonl.gz'),
        ('分析子集.jsonl', 'data/analysis_annotations.jsonl.gz'),
        ('参照与不计CF记录.jsonl', 'data/reference_annotations.jsonl.gz'),
        ('parts/evidence_other/full_root_records.jsonl', 'sources/shared_root_index.jsonl.gz'),
        ('reports/已有预测_逐题重分类.jsonl', 'predictions/reclassified_evaluations.jsonl.gz'),
    ]:
        jsonl(source, target)
    jsonl('parts/clinical_existing/raw/medpic_gf_references.jsonl',
          'sources/medpic_gf_index.jsonl.gz', lambda row: {
              'resource_id': 'M02', 'instance_id': row['instance_id'],
              'source': 'https://huggingface.co/datasets/TIM0927/MedPIC-Bench',
              'role': 'guideline_following_reference', 'counted_as_cf': False})
    for source, target in [
        ('分析子集_逐题标注.csv', 'data/analysis_units.csv.gz'),
        ('分析子集_具体判断.csv', 'data/analysis_judgments.csv.gz'),
        ('分析子集_未能定类.csv', 'data/analysis_unclassified.csv.gz'),
    ]:
        with (ROOT / source).open('rb') as src, gzip.open(destination / target, 'wb') as dst:
            shutil.copyfileobj(src, dst)

    report_names = [
        'classification_review.json', 'collection_counts.json', 'analysis_selection.json',
        'prediction_reuse.json', 'validation.json', '来源与标签计数.md',
        '已有预测_来源标签统计.csv', '统计口径与R5分布.md', 'r5_composition.json',
        '发布范围与原始来源.md', 'source_release_notes.json',
    ]
    copy_paths = [ROOT / 'reports' / name for name in report_names]
    copy_paths += [ROOT / '分类与抽样说明.md', ROOT / '医学CF资源清单.md']
    for subdir in ['provenance', 'classification', 'corrections']:
        copy_paths += [p for p in (ROOT / 'audit_20260908' / subdir).iterdir()
                       if p.suffix in {'.json', '.jsonl', '.csv', '.md'}
                       and not p.name.endswith('_before.jsonl')]
    copy_paths += [ROOT / 'audit_20260908' / name for name in
                   ['README.md', 'audit_status.json', '来源审核表.csv', 'checker_validation.json']]
    copy_paths += [ROOT / 'scripts' / name for name in
                   ['audit_collection.py', 'assemble_full.py', 'finalize_review.py', 'reclassify_full_predictions.py',
                    'verify_full_collection.py', 'export_github_results.py']]
    copy_paths += [ROOT / 'scripts/verify_github_results.py']
    copy_paths += [ROOT / 'audit_20260908/check_classification.py']
    copy_paths += [ROOT / 'parts/evidence_other/build_full.py']
    for src in copy_paths:
        dst = destination / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == '.jsonl':
            with dst.open('w', encoding='utf-8') as stream:
                for row in rows(src):
                    stream.write(json.dumps(without_originals(row), ensure_ascii=False) + '\n')
        elif src.suffix == '.json':
            dst.write_text(json.dumps(without_originals(json.loads(src.read_text())),
                                      ensure_ascii=False, indent=2) + '\n')
        elif src.suffix == '.md':
            content = src.read_text()
            content = content.replace('reports/分类审阅报告.md', 'reports/来源与标签计数.md')
            content = re.sub(r'\[取得记录\]\(parts/[^)]+/acquisition.json\)',
                             '[发布来源核查](reports/source_release_notes.json)', content)
            content = content.replace('../../分析子集_逐题标注.csv', '../../data/analysis_units.csv.gz')
            content = content.replace('../../分析子集_具体判断.csv', '../../data/analysis_judgments.csv.gz')
            dst.write_text(content)
        else:
            shutil.copyfile(src, dst)

    source_dir = destination / 'sources'
    files = [r for group in ['origin_a', 'origin_b']
             for r in rows(ROOT / f'audit_20260908/{group}/files.jsonl')]
    (source_dir / 'official_downloads.json').write_text(
        json.dumps(files, ensure_ascii=False, indent=2) + '\n')
    catalog = json.loads((ROOT / '资源目录.json').read_text())
    keys = ['resource_id', 'benchmark', 'scope', 'primary_source', 'full_counts',
            'analysis_selection', 'review_counts', 'review_status']
    (source_dir / 'resources.json').write_text(json.dumps(
        [{k: r[k] for k in keys if k in r} for r in catalog], ensure_ascii=False, indent=2) + '\n')
    manifest = {'date': '2026-09-08', 'scope': 'annotation_and_audit_results',
                'original_benchmark_bodies_included': False, 'new_model_calls': 0,
                'reviewed_cohort': 28243, 'jsonl_record_counts': counts,
                'omitted_fields': ['original_records', 'original_raw_response',
                    'reviewed_original_records', 'pre_review_annotation',
                    'initial_labels', 'existing_evaluation_records'],
                'historical_local_paths': 'Provenance locators in server workspace; not archive-relative paths.',
                'raw_data_restore': 'Official downloads plus shared_root_index and medpic_gf_index; source adapters and original workspace are required.'}
    (destination / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    export(parser.parse_args().destination)
