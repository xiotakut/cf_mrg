"""Additive documentary release of completed v4; no inference or native grading."""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path('/home/data3/txy')
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
REPO = ROOT / 'Documents/Codex/2026-09-24/cf_moa_github_publish_v4'
PREFIX = 'benchmarks/2026-09-24_cf_moa_minimal_v4'
PACKAGE = REPO / PREFIX
REPORT = ROOT / 'docs/research/cf_moa_experiment_report.md'
MAIN = ROOT / 'docs/research/cf_moa.md'
PLAN = ROOT / 'cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md'
LINK = re.compile(r'(!?)\[([^\]\n]+)\]\((<[^>]+>|[^)\n]+)\)')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def inline_refs(text):
    pattern = re.compile(r'^\[([^\]\n]+)\]:\s*(\S+)\s*$', re.M)
    refs = {m.group(1).lower(): m.group(2) for m in pattern.finditer(text)}
    text = re.sub(r'\[([^\]\n]+)\]\[([^\]\n]+)\]', lambda m:
        '[' + m[1] + '](' + refs[m[2].lower()] + ')' if m[2].lower() in refs else m[0], text)
    return pattern.sub('', text)


def main():
    old = read(HERE / 'old_publication_hashes.json')
    assert all(sha(REPO / p) == h for p, h in old.items())
    PACKAGE.mkdir(parents=True, exist_ok=True)
    manifest, refs, mapping = [], [], {}
    for directory in sorted((REPO / 'benchmarks').glob('*cf_moa*')):
        source_manifest = directory / 'SOURCE_MANIFEST.json'
        if source_manifest.exists() and directory != PACKAGE:
            for row in read(source_manifest):
                mapping[Path(row['source_path']).resolve()] = directory / row['published_path']

    def copy(source, relative, transformation='Byte-identical source snapshot; original local paths retained'):
        source = Path(source)
        target = PACKAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        mapping[source.resolve()] = target
        manifest.append(dict(published_path=relative, source_path=str(source), source_sha256=sha(source),
            published_sha256=sha(target), transformation=transformation))
        return target

    prepared = HERE / 'data_preparation'
    for source in sorted((prepared / 'data').iterdir()):
        if source.suffix in ('.json', '.csv', '.md'):
            copy(source, 'data/' + source.name, 'Allowlisted saved metadata; no new model or native scoring')
    for source in sorted(prepared.glob('*.py')):
        copy(source, 'scripts/' + source.name)

    snapshot = RUN / 'final_source_snapshot'
    for source in sorted(snapshot.rglob('*')):
        if source.is_file():
            target = copy(source, 'source_snapshot/' + str(source.relative_to(snapshot)))
            mapping[(ROOT / source.relative_to(snapshot)).resolve()] = target
    copy(RUN / 'delivery_index.json', 'data/delivery_index.json')
    copy(RUN / 'decision.json', 'data/decision.json')
    copy(RUN / 'analysis_plan.json', 'plan/analysis_plan.json')
    copy(HERE / 'document_review.json', 'evidence/document_review.json')
    copy(HERE / 'publication_data_review.json', 'evidence/publication_data_review.json')
    copy(HERE / 'original_delivery_verified.json', 'evidence/original_delivery_verified.json')
    receipt_names = [
        'operations/replay/receipt.json', 'operations/unit_test_receipt.json',
        'operations/f_toggle_receipt.json', 'seeds/preparation_receipt.json',
        'seeds/live_receipt.json', 'natural_scope/preparation_receipt.json',
        'natural_scope/preparation_attempts.json', 'natural_scope/seed_amendment_receipt.json',
        'natural_scope/live_receipt.json', 'analysis/analysis_errors.json',
        'analysis/independent_review.json', 'gpu_final_receipt.json',
    ]
    for relative in receipt_names:
        copy(RUN / relative, 'evidence/' + relative)
    for name in ('historical121', 'natural52'):
        mapping[(RUN / 'analysis' / name / 'summary.json').resolve()] = PACKAGE / 'data/quality_summary.json'
        mapping[(RUN / 'analysis' / name / 'per_input_status.jsonl').resolve()] = PACKAGE / 'data/per_input_status.csv'
        mapping[(RUN / 'analysis' / name / 'cost.json').resolve()] = PACKAGE / 'data/cost_summary.json'
    mapping[(RUN / 'analysis/combined_summary.json').resolve()] = PACKAGE / 'data/quality_summary.json'
    mapping[(RUN / 'README.md').resolve()] = PACKAGE / 'README.md'
    mapping[RUN.resolve()] = PACKAGE / 'README.md'
    mapping[REPORT] = PACKAGE / 'docs/research/cf_moa_experiment_report.md'
    mapping[MAIN] = PACKAGE / 'docs/research/cf_moa.md'
    mapping[PLAN] = PACKAGE / 'plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md'

    def publish(source, target, notice=''):
        def replace(match):
            image, label, raw = match.groups()
            raw = raw.strip().strip('<>')
            parsed = urlsplit(raw)
            if parsed.scheme or raw.startswith('//') or not parsed.path:
                return match[0]
            path = unquote(parsed.path)
            line = ''
            found = re.match(r'^(.*):(\d+)$', path)
            if found:
                path, line = found.groups()
            resolved = (source.parent / path).resolve()
            dest = mapping.get(resolved)
            if dest:
                fragment = '#' + parsed.fragment if parsed.fragment else ''
                return image + '[' + label + '](' + os.path.relpath(dest, target.parent) + fragment + ')'
            display = str(resolved) + (':' + line if line else '') + ('#' + parsed.fragment if parsed.fragment else '')
            refs.append(dict(published_document=str(target.relative_to(PACKAGE)), source_document=str(source),
                label=label, original_target=raw, resolved_local_target=display))
            return label + '（本地制品：`' + display + '`）'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(notice + LINK.sub(replace, inline_refs(source.read_text())))
        manifest.append(dict(published_path=str(target.relative_to(PACKAGE)), source_path=str(source),
            source_sha256=sha(source), published_sha256=sha(target),
            transformation='Research text retained; added dated publication notice and mapped links. Unexported artifacts marked local.'))

    publish(REPORT, mapping[REPORT], '> 2026-09-24版本4公开快照，实验截至2026-09-23完成。正文“本地续写/尚未上传”保留撰写时身份；本次发布导航见[运行与交付说明](../../RUN_AND_DELIVERY.md)。原始SQL和请求正文未公开，本次0新推理/评分。\n\n')
    publish(MAIN, mapping[MAIN], '> 2026-09-24版本4固定主记录快照。历史状态按原时点理解；[本轮完整报告](cf_moa_experiment_report.md#minimal-head-reuse-v4)与[公开交付导航](../../RUN_AND_DELIVERY.md)优先。\n\n')
    publish(PLAN, mapping[PLAN], '> 用户采用的最简复用计划；[已完成结果](../docs/research/cf_moa_experiment_report.md#minimal-head-reuse-v4)。计划内未来时态不代表未执行。\n\n')
    with (PACKAGE / 'LOCAL_ARTIFACT_REFERENCES.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['published_document', 'source_document', 'label', 'original_target', 'resolved_local_target'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(refs)

    original = read(RUN / 'delivery_index.json')
    indexed = []
    for row in original['artifacts']:
        source = Path(row['path']).resolve()
        target = mapping.get(source)
        if not target and source.name in ('model_calls.jsonl', 'proposals.jsonl'):
            target = PACKAGE / 'data' / ('new_model_call_trace.csv' if source.name == 'model_calls.jsonl' else 'per_input_status.csv')
        published = str(target.relative_to(PACKAGE)) if target and target.is_relative_to(PACKAGE) else None
        identical = bool(target and target.is_file() and sha(target) == row['sha256'])
        indexed.append(dict(row, publication_status='byte_identical' if identical else 'metadata_projection' if target else 'local_only',
            public_path=published, public_sha256=sha(target) if target and target.is_file() else None))
    write_json(PACKAGE / 'data/public_delivery_index.json', dict(
        original_index='delivery_index.json', original_index_sha256=sha(RUN / 'delivery_index.json'),
        original_artifact_count=len(indexed), original_run_count=10, new_model_calls=231,
        new_native_score_mappings=247, artifacts=indexed,
        note='Original paths/hashes retained. metadata_projection is not a full trace. local_only files are not in this GitHub package.'))
    for name in ('README.md', 'RUN_AND_DELIVERY.md', 'check_publication.py'):
        copy(HERE / name, name)
    copy(Path(__file__), 'scripts/build_publication.py')
    write_json(PACKAGE / 'SOURCE_MANIFEST.json', manifest)
    # Package-wide hashes also cover generated navigation and original/public indices.
    write_json(PACKAGE / 'PACKAGE_MANIFEST.json', dict(files=[dict(path=str(p.relative_to(PACKAGE)),
        bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name != 'PACKAGE_MANIFEST.json']))
    assert all(sha(REPO / p) == h for p, h in old.items())
    receipt = dict(status='built_not_pushed', package=str(PACKAGE), files=sum(p.is_file() for p in PACKAGE.rglob('*')),
        source_entries=len(manifest), original_artifacts=len(indexed), prior_package_files_unchanged=len(old),
        unexported_link_occurrences=len(refs), new_model_calls=0, native_scoring_calls=0)
    write_json(HERE / 'build_receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
