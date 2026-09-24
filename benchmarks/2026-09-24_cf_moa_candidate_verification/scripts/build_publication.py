"""Publish saved candidate-verification artifacts; no model or native grading calls."""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path('/home/data3/txy')
HERE = ROOT / 'Documents/Codex/2026-09-24/cf_moa_candidate_publication'
RUN = ROOT / 'Documents/Codex/2026-09-24/cf_moa_candidate_verify_20260924'
REC = RUN / 'recovery_gpu23'
REPO = ROOT / 'Documents/Codex/2026-09-24/cf_moa_github_candidate_verify'
PACKAGE = REPO / 'benchmarks/2026-09-24_cf_moa_candidate_verification'
LINK = re.compile(r'(!?)\[([^\]\n]+)\]\((<[^>]+>|[^)\n]+)\)')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    old = read(HERE / 'old_publication_hashes.json')
    assert all(sha(REPO / p) == h for p, h in old.items())
    PACKAGE.mkdir(parents=True, exist_ok=True)
    manifest, refs, mapping = [], [], {}
    for folder in sorted((REPO / 'benchmarks').glob('*cf_moa*')):
        source_manifest = folder / 'SOURCE_MANIFEST.json'
        if source_manifest.exists() and folder != PACKAGE:
            for row in read(source_manifest):
                mapping[Path(row['source_path']).resolve()] = folder / row['published_path']

    def copy(source, relative, transformation='Byte-identical frozen source; server paths retained'):
        source = Path(source)
        target = PACKAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        mapping[source.resolve()] = target
        manifest.append(dict(published_path=relative, source_path=str(source), source_sha256=sha(source),
                             published_sha256=sha(target), transformation=transformation))
        return target

    for p in sorted((HERE / 'data_staging').iterdir()):
        if p.is_file():
            copy(p, 'data/' + p.name,
                 'Allowlisted projection of saved metadata; no new inference or native scoring')
    copy(HERE / 'export_public_data.py', 'scripts/export_public_data.py')
    for p in sorted((REC / 'code_snapshot').rglob('*')):
        if p.is_file():
            relative = p.relative_to(REC / 'code_snapshot')
            target = copy(p, 'source_snapshot/' + str(relative))
            mapping[(ROOT / relative).resolve()] = target
    frozen = read(REC / 'plan.json')
    for source, expected in frozen['protected_sources'].items():
        p = Path(source)
        assert sha(p) == expected
        copy(p, 'source_snapshot/' + str(p.relative_to(ROOT)))
    for p in sorted((REC / 'runtime_source').rglob('test_*.py')):
        copy(p, 'source_snapshot/' + str(p.relative_to(REC / 'runtime_source')))
    # Source actually used for final offline analysis differs from the launch snapshot.
    copy(RUN / 'analysis/score_candidate_experiment.py', 'analysis_code/score_candidate_experiment.py')
    for p in sorted((REC / 'analysis_fix_empty_nli').iterdir()):
        if p.is_file(): copy(p, 'evidence/analysis_fix_empty_nli/' + p.name)
    for name in ['runtime_recovery.diff', 'runtime_test_receipt.json', 'analysis_revision_receipt.json',
                 'analysis_test/regression_receipt.json', 'prelaunch_receipt.json', 'inference_spotcheck.json',
                 'final_runtime_receipt.json', 'final_analysis_review.json', 'counterexamples/receipt.json',
                 'delivery_validation.json']:
        copy(REC / name, 'evidence/' + name)
    for name in ['launch.json', 'status.json', 'runs/m4/status.json', 'runs/m5/status.json',
                 'runs/m4/lifecycle.json', 'runs/m5/lifecycle.json']:
        copy(REC / name, 'evidence/execution/' + name)
    copy(REC / 'plan.json', 'plan/runtime_plan.json')
    copy(RUN / 'source_request/download_receipt.json', 'plan/download_receipt.json')
    copy(RUN / 'source_request/CF_MoA_V4_Source_Diagnosis_and_Coding_Instructions.md',
         'plan/CF_MoA_V4_Source_Diagnosis_and_Coding_Instructions.md')
    copy(REC / 'final_delivery_index.json', 'data/original_delivery_index.json')
    copy(HERE / 'original_delivery_verified.json', 'evidence/original_delivery_verified.json')
    copy(HERE / 'source_document_archive.json', 'evidence/source_document_archive.json')
    copy(ROOT / 'cf_moa/configs/execution_plan.json', 'plan/current_execution_state.json')
    copy(HERE / 'preparation_notes.json', 'evidence/publication_preparation_notes.json')
    for name in ('document_review.json', 'publication_data_review.json'):
        if (HERE / name).exists(): copy(HERE / name, 'evidence/' + name)
    for name in ['README.md', 'RUN_AND_DELIVERY.md', 'SOURCE_ENTRY.md', 'check_publication.py']:
        copy(HERE / name, name)
    copy(Path(__file__), 'scripts/build_publication.py')

    aliases = {
        REC / 'analysis/complete_results/summary.json': 'data/quality_summary.json',
        REC / 'analysis/complete_results/cost.json': 'data/cost_summary.json',
        REC / 'analysis/complete_results/per_input_status.jsonl': 'data/per_input_status.jsonl',
        REC / 'analysis/complete_results/native_scored.jsonl': 'data/native_scoring_metadata.jsonl',
        REC / 'decision.json': 'data/decision.json',
        REC / 'analysis/complete_results/README.md': 'RUN_AND_DELIVERY.md',
        REC / 'analysis/complete_results/receipt.json': 'data/analysis_receipt_metadata.json',
        REC / 'code_snapshot': 'source_snapshot',
        RUN / 'semantic_review/m4.jsonl': 'data/prior_semantic_review_metadata.jsonl',
        RUN / 'semantic_review/m5.jsonl': 'data/prior_semantic_review_metadata.jsonl',
        RUN / 'runs/m4/model_calls.jsonl': 'data/prior_initialization_failures.jsonl',
        REC / 'counterexamples/smoke_four.jsonl': 'data/fixed_smoke_counterexample_metadata.jsonl',
        REC / 'README.md': 'RUN_AND_DELIVERY.md',
        RUN / 'README.md': 'README.md',
        RUN / 'delivery_index.json': 'data/public_delivery_index.json',
        REC / 'final_delivery_index.json': 'data/public_delivery_index.json',
    }
    # Data exporter may also provide its exact original -> public file map.
    extra = HERE / 'data_staging/publication_path_map.json'
    if extra.exists():
        for source, target in read(extra).items(): aliases[Path(source)] = 'data/' + target
    mapping.update({p.resolve(): PACKAGE / target for p, target in aliases.items()})
    report = ROOT / 'docs/research/cf_moa_experiment_report.md'
    record = ROOT / 'docs/research/cf_moa.md'
    core = ROOT / 'cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md'
    mapping[report] = PACKAGE / 'docs/research/cf_moa_experiment_report.md'
    mapping[record] = PACKAGE / 'docs/research/cf_moa.md'
    mapping[core] = PACKAGE / 'plan/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md'
    for bone in ('m4', 'm5'):
        mapping[REC / f'runs/{bone}/model_calls.jsonl'] = PACKAGE / 'data/model_call_metadata.jsonl'
        mapping[REC / f'runs/{bone}/proposals.jsonl'] = PACKAGE / 'data/candidate_selection_metadata.jsonl'

    def publish(source, target, notice):
        def replace(m):
            image, label, raw = m.groups()
            raw = raw.strip().strip('<>')
            parsed = urlsplit(raw)
            if parsed.scheme or raw.startswith('//') or not parsed.path: return m[0]
            path = unquote(parsed.path)
            resolved = (source.parent / re.sub(r':\d+$', '', path)).resolve()
            dest = mapping.get(resolved)
            if resolved == REC / 'counterexamples/smoke_four.jsonl':
                return label + '（完整内容未公开；服务器制品：`' + str(resolved) + '`；[仅公开元数据](' + os.path.relpath(dest, target.parent) + ')）'
            if dest and (dest.exists() or dest in (mapping[report], mapping[record], mapping[core], PACKAGE / 'data/public_delivery_index.json')):
                fragment = '#' + parsed.fragment if parsed.fragment else ''
                return image + '[' + label + '](' + os.path.relpath(dest, target.parent) + fragment + ')'
            display = str(resolved) + ('#' + parsed.fragment if parsed.fragment else '')
            refs.append(dict(published_document=str(target.relative_to(PACKAGE)), source_document=str(source),
                             label=label, original_target=raw, resolved_local_target=display))
            return label + '（本地制品：`' + display + '`）'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(notice + LINK.sub(replace, source.read_text()))
        manifest.append(dict(published_path=str(target.relative_to(PACKAGE)), source_path=str(source),
                             source_sha256=sha(source), published_sha256=sha(target),
                             transformation='Frozen research text with publication notice and resolved public/local links'))

    publish(report, mapping[report], '> 2026-09-24候选验证公开快照；[第15章](#candidate-verification-execution)为本轮新计划真实运行结果，[运行与交付导航](../../RUN_AND_DELIVERY.md)提供代码、配置、逐题元数据与成本。前14章保留历史身份。此发布0新模型/评分；完整SQL、病例、请求和响应正文留服务器。\n\n')
    publish(record, mapping[record], '> 2026-09-24固定主记录快照；[本轮最终结果](#candidate-verify-results-20260924)与[公开交付导航](../../RUN_AND_DELIVERY.md)。历史段落的等待/未运行按原时间理解。\n\n')
    publish(core, mapping[core], '> 本轮采用计划与执行边界；真实结果见[完整报告第15章](../docs/research/cf_moa_experiment_report.md#candidate-verification-execution)。计划不是成绩。\n\n')
    with (PACKAGE / 'LOCAL_ARTIFACT_REFERENCES.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['published_document', 'source_document', 'label', 'original_target', 'resolved_local_target'], lineterminator='\n')
        w.writeheader(); w.writerows(refs)

    indexed = []
    for row in read(REC / 'final_delivery_index.json')['files']:
        source = Path(row['path']).resolve()
        target = mapping.get(source)
        if not target or not target.is_file(): target = None
        identical = bool(target and sha(target) == row['sha256'])
        indexed.append(dict(row, publication_status='byte_identical' if identical else 'metadata_or_document_projection' if target else 'local_only',
                            public_path=os.path.relpath(target, PACKAGE) if target else None,
                            public_sha256=sha(target) if target else None))
    write_json(PACKAGE / 'data/public_delivery_index.json', dict(
        original_index='original_delivery_index.json', original_index_sha256=sha(REC / 'final_delivery_index.json'),
        original_artifacts=len(indexed), artifacts=indexed,
        note='Public metadata is not the full private trace. SQL, model text, input text and gold remain server-side. Historical hashes are retained; mutable docs have archival bytes saved.'))
    write_json(PACKAGE / 'SOURCE_MANIFEST.json', manifest)
    write_json(PACKAGE / 'PACKAGE_MANIFEST.json', dict(files=[dict(path=str(p.relative_to(PACKAGE)), bytes=p.stat().st_size, sha256=sha(p))
        for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name != 'PACKAGE_MANIFEST.json' and '__pycache__' not in p.parts]))
    assert all(sha(REPO / p) == h for p, h in old.items())
    receipt = dict(status='built_not_pushed', package=str(PACKAGE), files=sum(p.is_file() for p in PACKAGE.rglob('*')),
                   source_entries=len(manifest), original_artifacts=len(indexed), prior_files_unchanged=len(old),
                   local_link_occurrences=len(refs), new_model_calls=0, native_scoring_calls=0)
    write_json(HERE / 'build_receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__': main()
