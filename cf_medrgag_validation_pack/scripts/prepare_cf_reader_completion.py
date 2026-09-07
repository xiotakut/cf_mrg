#!/usr/bin/env python3
"""Copy the frozen full test and exact caches for the requested M0/M1 completion."""
from datetime import datetime
from pathlib import Path
import csv
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results_cf_full_test'
OUT = ROOT / 'results_cf_full_comparison'


def prepare():
    if (OUT / 'reader_completion.json').exists():
        print('Already prepared; resume with cf_baseline_screening.sh readers.')
        return
    metrics = json.loads((SOURCE / 'metrics.json').read_text())
    assert metrics['status'] == 'complete' and metrics['required_methods'] == ['M2']
    OUT.mkdir(exist_ok=True)
    names = ['screening_items.jsonl', 'evaluation_labels.jsonl', 'taxonomy.jsonl',
             'config.json', 'sample_plan.json', 'canonical_labels.json', 'source_overlap.json',
             'input_lengths.jsonl', 'acquisition.json', 'acquisition.md', 'data_checks.md',
             'exposure_audit.json', 'duplicate_gold_conflicts.json', 'environment.json',
             'performance_test.json', 'RESEARCH_PLAN.md', 'taxonomy_corrections.json',
             'rng_repeat_correction.json', 'smoke_review.md']
    for name in names:
        shutil.copy2(SOURCE / name, OUT / name)
    (OUT / 'runtime').symlink_to((SOURCE / 'runtime').resolve(), target_is_directory=True)
    for name in ['main', 'repeat_independent', 'repeat', 'smoke_pre_evidence_dedup']:
        shutil.copytree(SOURCE / 'cache' / name, OUT / 'cache' / name)
    counts = {m: sum(sum(1 for _ in f.open()) for f in (OUT / 'cache/main').glob('worker-*/' + m + '.jsonl'))
              for m in ['M0', 'M1', 'M2']}
    assert counts == {'M0': 5832, 'M1': 5832, 'M2': 25280}, counts
    for name in ['screening_items.jsonl', 'evaluation_labels.jsonl', 'taxonomy.jsonl', 'config.json']:
        assert (SOURCE / name).read_bytes() == (OUT / name).read_bytes()
    record = {'prepared_at': datetime.now().astimezone().isoformat(),
              'authorization': 'User requests completing previously stopped M0 and M1 on the same entire test set, with unchanged requirements and configuration.',
              'source': str(SOURCE), 'source_result_commit': '638f1e3ad116ffdad609e74bb5a9f019a196911e',
              'methods_executed_now': ['M0', 'M1'], 'methods_compared': ['M0', 'M1', 'M2'],
              'planned_unique_inputs': 25280, 'prior_predictions_by_method': counts,
              'new_predictions_per_method': {'M0': 19448, 'M1': 19448},
              'new_LLM_requests_planned': 38896,
              'reuse': 'Independent byte-for-byte copies; all M2 stages and M1 initial retrieval stay fixed. No input, prompt, checkpoint, precision, decoding, parsing or seed changes.'}
    (OUT / 'reader_completion.json').write_text(json.dumps(record, indent=2) + '\n')
    (OUT / 'method_scope.json').write_text(json.dumps({'methods': ['M0', 'M1', 'M2'],
        'methods_executed_now': ['M0', 'M1'], 'authorization': record['authorization'],
        'planned_method_predictions': 75840}, indent=2) + '\n')
    (OUT / 'cache_reuse.json').write_text(json.dumps({'source': str(SOURCE),
        'prior_unique_inputs': 25280, 'prior_predictions': sum(counts.values()),
        'prior_predictions_by_method': counts, 'prior_LLM_requests': metrics['efficiency']['LLM_requests'],
        'prior_batch_wall_seconds': metrics['efficiency']['formal_batch_elapsed_seconds'],
        'reuse_basis': record['reuse']}, indent=2) + '\n')
    (OUT / 'prior_run_efficiency.json').write_text(json.dumps(metrics['efficiency'], indent=2) + '\n')
    shutil.copy2(SOURCE / 'artifact_audit.json', OUT / 'prior_M2_artifact_audit.json')
    with (SOURCE / 'benchmark_summary.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row['planned_method_predictions'] = 3 * int(row['unique_inputs'])
    with (OUT / 'benchmark_summary.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps(record))


if __name__ == '__main__':
    prepare()
