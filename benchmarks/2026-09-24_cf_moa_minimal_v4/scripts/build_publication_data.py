#!/usr/bin/env python3
"""Whitelist export of saved CF-MoA v4 metadata; never invokes models or scorers.

Private source artifacts are required for rebuilding. The accompanying verifier
only requires the published files and Python's standard library.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

DEFAULT_RUN = Path('/home/data3/txy/Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923')
OLD_PAIRS = Path('/home/data3/txy/Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development/offline/pairs.jsonl')
PANELS = ('historical121', 'natural52')
INPUT_KEYS = ('request_id', 'method', 'seed', 'arm', 'family_id', 'source', 'answer_format',
              'correct', 'native_valid', 'native_mapping_count', 'method_score', 'run_status',
              'native_answer_ref', 'mixed_native_correctness', 'failure_type', 'repair_attempted',
              'trigger', 'F_supported')
INPUT_FIELDS = ('panel',) + INPUT_KEYS + ('correct_before', 'repair', 'harm', 'unavailable_recovery',
    'correct_lost_to_unavailable', 'new_physical_calls_this_revision')
CALL_FIELDS = ('panel', 'method', 'seed', 'request_id', 'logical_request_id', 'ordinal', 'physical_ordinal',
    'stage', 'status', 'phase', 'submission_state', 'engine_accepted', 'engine_core_request_id',
    'model', 'temperature', 'max_tokens', 'actual_sampling_seed', 'input_tokens', 'output_tokens',
    'elapsed_seconds', 'finish_reason', 'physical_batch_size', 'config_hash', 'physical_request_hash',
    'logical_request_sha256', 'prompt_sha256', 'raw_response_sha256', 'source_file', 'source_line')
BANNED_KEYS = {'messages', 'prompt', 'raw', 'raw_response', 'value', 'prediction', 'semantic_prediction',
    'semantic_gold', 'answer_choice', 'answer', 'native_answer', 'target', 'reason', 'patient', 'options',
    'question', 'retrieved_context', 'model_input', 'engine_prompt_token_ids', 'text', 'content'}

def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()

def digest(path):
    return sha_bytes(path.read_bytes())

def json_digest(value):
    return sha_bytes(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())

def audit(value, path='root'):
    """Fail closed on content-bearing fields; strings are limited to metadata size."""
    if isinstance(value, dict):
        for key, child in value.items():
            assert key not in BANNED_KEYS, (path, key)
            audit(child, path + '.' + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            audit(child, f'{path}[{i}]')
    elif isinstance(value, str):
        assert len(value) <= 1500, (path, len(value))

def write_json(path, value):
    audit(value)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def write_csv(path, fields, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            assert set(row) <= set(fields)
            audit(row)
            writer.writerow({key: (json.dumps(value) if isinstance(value, bool) else value)
                             for key, value in row.items()})

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-run', type=Path, default=DEFAULT_RUN)
    parser.add_argument('--historical-pairs', type=Path, default=OLD_PAIRS)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'data')
    args = parser.parse_args()
    run, out = args.source_run.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources = {}

    def source_name(path):
        try:
            return 'minimal_revision/' + str(path.relative_to(run))
        except ValueError:
            assert path == args.historical_pairs.resolve()
            return 'historical_development/offline/pairs.jsonl'

    def read(path, lines=False):
        path = path.resolve()
        sources[source_name(path)] = {'sha256': digest(path), 'bytes': path.stat().st_size}
        raw = path.read_text()
        return [json.loads(line) for line in raw.splitlines() if line] if lines else json.loads(raw)

    combined = read(run / 'analysis/combined_summary.json')
    quality = {'version': 'minimal_head_reuse_v4', 'interpretation': 'Saved exposed-development results; no native scoring or inference in publication.',
               'panels': {}, 'combined': combined}
    pair_data = {'interpretation': 'Pair metadata is offline evaluation only; never supplied to inference. Semantic relation is a saved native benchmark relation, not a clinical causal judgment.', 'panels': {}}
    unit_data = {'interpretation': 'Saved equal native-unit metrics, not a new scoring execution. R categories overlap and are offline only; they were not inference inputs.', 'panels': {}}
    costs = {'new_physical_execution_this_revision': combined['new_physical_execution'],
             'publication_new_model_calls': 0, 'publication_native_scorer_calls': 0, 'panels': {}}
    input_rows, call_rows = [], []
    for panel in PANELS:
        summary = read(run / 'analysis' / panel / 'summary.json')
        audit(summary)
        quality['panels'][panel] = summary
        pair_path = args.historical_pairs if panel == 'historical121' else run / 'natural_scope/offline/pairs.jsonl'
        pair_map = {row['pair_id']: {key: row[key] for key in ('pair_id', 'family_id', 'left', 'right', 'relation')}
                    for row in read(pair_path, True)}
        pair_data['panels'][panel] = {'definitions': list(pair_map.values()), 'methods': {}}
        for method, methods in summary['methods'].items():
            pair_data['panels'][panel]['methods'][method] = {'baseline': methods['baseline'].pop('pairs'), 'seeds': {}}
            for seed, item in methods['seeds'].items():
                pair_data['panels'][panel]['methods'][method]['seeds'][seed] = item.pop('pairs')
        costs['panels'][panel] = read(run / 'analysis' / panel / 'cost.json')
        units = read(run / 'analysis' / panel / 'native_unit_metrics.json')
        unit_data['panels'][panel] = {'reports': units['reports'], 'new_model_calls': units['new_model_calls'],
            'native_scorer_calls': units['native_scorer_calls'], 'origin': units['origin']}
        rows = read(run / 'analysis' / panel / 'per_input_status.jsonl', True)
        base = {(r['method'], r['request_id']): r for r in rows if r['arm'] == 'baseline'}
        for row in rows:
            before = base[(row['method'], row['request_id'])]
            result = {'panel': panel, **{key: row.get(key) for key in INPUT_KEYS}}
            result.update(correct_before=before['correct'],
                repair=(row['arm'] != 'baseline' and before['native_valid'] and not before['correct'] and row['correct'] is True),
                harm=(row['arm'] != 'baseline' and before['correct'] is True and row['native_valid'] and row['correct'] is False),
                unavailable_recovery=(not before['native_valid'] and row['native_valid']),
                correct_lost_to_unavailable=(before['correct'] is True and not row['native_valid']),
                new_physical_calls_this_revision=0)
            input_rows.append(result)
        new_seeds = (43, 44) if panel == 'historical121' else (42, 43, 44)
        for seed in new_seeds:
            for method in ('M4', 'M5'):
                prefix = 'seeds' if panel == 'historical121' else 'natural_runs'
                file = run / prefix / f'seed_{seed}' / method.lower() / 'model_calls.jsonl'
                calls = read(file, True)
                for line_number, logical in enumerate(calls, 1):
                    for physical_number, physical in enumerate(logical['physical']):
                        event = physical['event']
                        req = logical['request']
                        physical_req = physical['request']
                        call_rows.append({'panel': panel, 'method': method, 'seed': seed,
                            'request_id': logical['request_id'].split(':')[0], 'logical_request_id': logical['request_id'],
                            'ordinal': logical['ordinal'], 'physical_ordinal': physical_number, 'stage': 'ordinary_f_disagreement_reanswer',
                            'status': logical['status'], 'phase': logical['phase'], 'submission_state': physical['submission_state'],
                            'engine_accepted': bool(physical['engine_accepted']), 'engine_core_request_id': physical['engine_core_request_id'],
                            'model': Path(event['model']).name, 'temperature': req['temperature'], 'max_tokens': req['max_tokens'],
                            'actual_sampling_seed': physical['engine_accepted']['sampling_params']['seed'], 'input_tokens': event['input_tokens'],
                            'output_tokens': event['output_tokens'], 'elapsed_seconds': event['elapsed_seconds'],
                            'finish_reason': event['finish_reason'], 'physical_batch_size': event['physical_batch_size'],
                            'config_hash': event['config_hash'], 'physical_request_hash': physical['request_hash'],
                            'logical_request_sha256': json_digest(req), 'prompt_sha256': sha_bytes(physical_req['prompt'].encode()),
                            'raw_response_sha256': sha_bytes(physical['raw_response'].encode()),
                            'source_file': source_name(file), 'source_line': line_number})
    call_counts = {}
    for row in call_rows:
        key = (row['panel'], row['method'], row['seed'], row['request_id'])
        call_counts[key] = call_counts.get(key, 0) + 1
    for row in input_rows:
        row['new_physical_calls_this_revision'] = call_counts.get((row['panel'], row['method'], row['seed'], row['request_id']), 0)

    limitations = {
        'status': 'completed_keep_equivalent_B_increment_not_adopted',
        'default_system': 'adopted_B_five_operations_v1', 'optional_F_reanswer_default': False,
        'packaging_equivalence': {'cached_native_rows_equal': 242, 'shared_rule_replays': 18,
            'ordinary_algebra_checks': 12, 'special_cases_use_old_assemble': 6, 'observed_remove_operations': 0,
            'A4_main_panel_applicable_inputs': 0, 'A1_A2_are_operations_of_one_existing_kernel': True},
        'unavailable_kept': {'panel': 'historical121', 'method': 'M5', 'request_id': 'd00050',
            'arms': ['baseline', 'seed42', 'seed43', 'seed44'], 'method_score': 'not_scored',
            'interpretation': 'Inherited unavailable native answer. Not counted as an incorrect answer and not deleted from denominator.'},
        'runtime': {'new_physical_calls': 231, 'new_runtime_failures': 0, 'format_repair_calls': 0, 'unknown_usage': 0},
        'scope32_counterexample': {'origin': 'existing v3 cycle2 Scope32, not a new run',
            'M4': {'old_F': 31, 'ordinary_reanswer': 30, 'denominator': 32},
            'M5': {'old_F': 31, 'ordinary_reanswer': 31, 'denominator': 32}},
        'exposure': {'historical121': 'Previously exposed development panel.',
            'natural52': 'Fixed 18 complete families from an already exposed F development pool; 9 source-by-format strata, 2 families per stratum by prespecified hash order. No family/input overlap with historical121.',
            'natural52_M23_control': 'Contains 4 existing author-derived relevance-control endpoints; not newly collected natural clinical cases.',
            'independent_evaluation': False},
        'limitations': [
            'Fixed B/F trajectories; only the added reanswer seed changes. This is conditional stability, not end-to-end reseeding.',
            'All three seeds and both backbones are reported with equal weights; no best-seed selection.',
            'Historical121 has small positive changes; natural52 all six seed-by-backbone cells have fewer correct inputs and lower native-unit means than B.',
            'Family-bootstrap intervals cross zero; current evidence is weak and inconsistent, not proof of population-level benefit or harm.',
            'Historical121 has four response pairs, all unsupported by F. Natural52 has only two F-supported response pairs; 0/2 is not proof of zero population capability.',
            'Ordinary F reanswer is an existing simple control, not a new counterfactual algorithm.',
            'A1 and A2 are shared-kernel operation projections, not independently trained models or a demonstrated five-LLM discussion.',
            'Cumulative model seconds are not exclusive wall latency or energy. Historical timing missingness remains null.',
            'Public metadata cannot independently reproduce native clinical judgments without private legal inputs, complete responses, and frozen native scoring artifacts.'
        ],
        'analysis_error_and_correction': read(run / 'analysis/analysis_errors.json'),
        'cache_preparation_attempts': read(run / 'natural_scope/preparation_attempts.json'),
        'publication_new_model_calls': 0, 'publication_native_scorer_calls': 0,
    }
    # Keep provenance portable: report relative identifiers, not local archive links.
    for key in ('old_analysis_directory', 'corrected_analysis_directory'):
        limitations['analysis_error_and_correction'][key] = source_name(Path(limitations['analysis_error_and_correction'][key]))
    for attempt in limitations['cache_preparation_attempts']['attempts']:
        attempt['diagnostic'] = attempt.pop('reason')

    write_json(out / 'quality_summary.json', quality)
    write_json(out / 'pair_summary.json', pair_data)
    write_json(out / 'native_unit_metrics.json', unit_data)
    write_json(out / 'cost_summary.json', costs)
    write_json(out / 'failure_and_limitations.json', limitations)
    write_csv(out / 'per_input_status.csv', INPUT_FIELDS, input_rows)
    write_csv(out / 'new_model_call_trace.csv', CALL_FIELDS, call_rows)
    artifacts = {path.name: {'sha256': digest(path), 'bytes': path.stat().st_size}
                 for path in sorted(out.iterdir()) if path.is_file() and path.name not in ('source_manifest.json', 'verification_receipt.json')}
    write_json(out / 'source_manifest.json', {'version': 'v4_metadata_whitelist',
        'source_aliases': {'minimal_revision': 'cf_moa_minimal_revision_20260923',
                           'historical_development': 'existing CF-MoA development offline metadata'},
        'sources': sources, 'public_artifacts': artifacts,
        'builder_sha256': digest(Path(__file__)),
        'export_policy': 'Only explicit per-input and physical-call metadata fields; saved numeric summaries and offline IDs. No prompts, response bodies, native answers, gold labels, token IDs, SQL or legal input bodies.',
        'input_rows': len(input_rows), 'new_physical_call_rows': len(call_rows),
        'publication_new_model_calls': 0, 'publication_native_scorer_calls': 0})
    assert len(input_rows) == 1384 and len(call_rows) == 231
    print(json.dumps({'status': 'exported', 'inputs': len(input_rows), 'calls': len(call_rows), 'files': sorted(p.name for p in out.iterdir() if p.is_file())}))

if __name__ == '__main__':
    main()
