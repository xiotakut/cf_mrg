#!/usr/bin/env python3
"""Independently check the published metadata using only the Python standard library.

No local models, datasets, SQL, native scorer or network are accessed. This verifies
saved accounting consistency, not clinical correctness or an independent rerun.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path

def read_json(path):
    return json.loads(path.read_text())

def csv_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))

def flag(row, key):
    assert row[key] in ('', 'true', 'false'), (key, row[key])
    return None if row[key] == '' else row[key] == 'true'

def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (a, b)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_content_keys(obj):
    forbidden = {'messages', 'prompt', 'raw_response', 'prediction', 'semantic_prediction', 'semantic_gold',
                 'answer_choice', 'native_answer', 'question', 'patient', 'options', 'engine_prompt_token_ids',
                 'retrieved_context', 'model_input', 'content'}
    if isinstance(obj, dict):
        assert not (set(obj) & forbidden), set(obj) & forbidden
        for value in obj.values():
            check_content_keys(value)
    elif isinstance(obj, list):
        for value in obj:
            check_content_keys(value)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_dir', type=Path, nargs='?')
    parser.add_argument('--data-dir', type=Path, dest='data_dir_flag')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    root = args.data_dir_flag or args.data_dir or Path(__file__).parent / 'data'
    manifest = read_json(root / 'source_manifest.json')
    checks = collections.Counter()
    for file, item in manifest['public_artifacts'].items():
        path = root / file
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], file
        checks['artifact_hashes'] += 1
    documents = {name: read_json(root / name) for name in manifest['public_artifacts'] if name.endswith('.json')}
    for document in documents.values():
        check_content_keys(document)
    rows = csv_rows(root / 'per_input_status.csv')
    calls = csv_rows(root / 'new_model_call_trace.csv')
    assert len(rows) == manifest['input_rows'] == 1384
    assert len(calls) == manifest['new_physical_call_rows'] == 231
    quality, costs = documents['quality_summary.json'], documents['cost_summary.json']
    pairs, units = documents['pair_summary.json'], documents['native_unit_metrics.json']
    groups = collections.defaultdict(list)
    for row in rows:
        groups[(row['panel'], row['method'], row['seed'])].append(row)
    assert len(groups) == 16
    expected = {
        ('historical121', 'M4'): [87, 89, 88, 88], ('historical121', 'M5'): [82, 83, 84, 84],
        ('natural52', 'M4'): [35, 34, 31, 32], ('natural52', 'M5'): [26, 25, 23, 24],
    }
    keyed = {(r['panel'], r['method'], r['seed'], r['request_id']): r for r in rows}
    assert len(keyed) == len(rows)
    for (panel, method, seed), group in groups.items():
        qpanel = quality['panels'][panel]
        summary = qpanel['methods'][method]['seeds'][seed] if seed else qpanel['methods'][method]['baseline']
        counts = {'denominator': len(group), 'correct': sum(flag(r, 'correct') is True for r in group),
                  'incorrect': sum(flag(r, 'native_valid') is True and flag(r, 'correct') is False for r in group),
                  'unavailable': sum(flag(r, 'native_valid') is False for r in group)}
        for key, value in counts.items():
            assert summary['counts'][key] == value, (panel, method, seed, key)
        assert sum(counts[k] for k in ('correct', 'incorrect', 'unavailable')) == counts['denominator']
        assert len(group) == qpanel['denominator_per_backbone']
        assert len({r['family_id'] for r in group}) == qpanel['families'] == (40 if panel == 'historical121' else 18)
        assert counts['correct'] == expected[(panel, method)][['', '42', '43', '44'].index(seed)]
        for row in group:
            before = keyed[(panel, method, '', row['request_id'])]
            assert flag(row, 'correct_before') == flag(before, 'correct')
            assert flag(row, 'repair') == (bool(seed) and flag(before, 'native_valid') and not flag(before, 'correct') and flag(row, 'correct') is True)
            assert flag(row, 'harm') == (bool(seed) and flag(before, 'correct') is True and flag(row, 'native_valid') and flag(row, 'correct') is False)
            if flag(row, 'native_valid') is False:
                assert row['method_score'] == 'not_scored'
            checks['input_rows'] += 1
        if seed:
            assert sum(flag(r, 'repair') for r in group) == summary['repairs']
            assert sum(flag(r, 'harm') for r in group) == summary['harms']
            assert sorted(r['request_id'] for r in group if flag(r, 'repair')) == sorted(summary['repair_ids'])
            assert sorted(r['request_id'] for r in group if flag(r, 'harm')) == sorted(summary['harm_ids'])
            assert sum(flag(r, 'unavailable_recovery') for r in group) == summary['unavailable_recoveries']
            assert sum(flag(r, 'correct_lost_to_unavailable') for r in group) == summary['correct_lost_to_unavailable']
            assert sum(flag(r, 'trigger') is True for r in group) == summary['predeclared_triggers']
        checks['quality_groups'] += 1
    unavailable = [r for r in rows if flag(r, 'native_valid') is False]
    assert len(unavailable) == 4
    assert {(r['panel'], r['method'], r['request_id']) for r in unavailable} == {('historical121', 'M5', 'd00050')}
    call_groups = collections.defaultdict(list)
    call_counts = collections.Counter()
    for call in calls:
        panel, method, seed = call['panel'], call['method'], call['seed']
        assert seed == call['actual_sampling_seed']
        assert float(call['temperature']) == 0.7 and int(call['max_tokens']) == 512
        assert call['status'] == 'complete' and call['finish_reason'] == 'stop'
        assert flag(call, 'engine_accepted') is True
        assert flag(keyed[(panel, method, seed, call['request_id'])], 'trigger') is True
        assert not (panel == 'historical121' and seed == '42')
        for key in ('config_hash', 'physical_request_hash', 'logical_request_sha256', 'prompt_sha256', 'raw_response_sha256'):
            assert len(call[key]) == 64 and all(c in '0123456789abcdef' for c in call[key])
        call_groups[(panel, method, seed)].append(call)
        call_counts[(panel, method, seed, call['request_id'])] += 1
    assert len(call_groups) == 10
    assert set(call_counts.values()) == {1}  # no format-repair physical calls this revision
    for row in rows:
        key = (row['panel'], row['method'], row['seed'], row['request_id'])
        assert int(row['new_physical_calls_this_revision']) == call_counts[key]
        if not flag(row, 'trigger'):
            assert call_counts[key] == 0
    for (panel, method, seed), group in call_groups.items():
        cost = costs['panels'][panel]['methods'][method]['seeds'][seed]
        extra = cost['extra_execution']
        assert cost['origin'] == 'new_physical_execution_this_revision'
        assert len(group) == extra['physical_model_requests']
        assert sum(int(c['input_tokens']) for c in group) == extra['live_input_tokens']
        assert sum(int(c['output_tokens']) for c in group) == extra['live_output_tokens']
        close(sum(float(c['elapsed_seconds']) for c in group), extra['live_model_seconds'])
        checks['new_run_cost_groups'] += 1
    total = costs['new_physical_execution_this_revision']
    assert sum(int(c['input_tokens']) for c in calls) == total['live_input_tokens'] == 1444680
    assert sum(int(c['output_tokens']) for c in calls) == total['live_output_tokens'] == 31047
    assert len(calls) == total['physical_model_requests'] == 231
    close(sum(float(c['elapsed_seconds']) for c in calls), total['live_model_seconds'])
    for panel, cost in costs['panels'].items():
        for method, entry in cost['methods'].items():
            inherited = entry['inherited_B']
            for seed, item in entry['seeds'].items():
                assert item['attributed_input_tokens'] == inherited['reused_head_input_tokens'] + item['extra_execution']['live_input_tokens']
                assert item['attributed_output_tokens'] == inherited['reused_head_output_tokens'] + item['extra_execution']['live_output_tokens']
                assert item['attributed_model_requests'] == inherited['reused_head_model_requests'] + item['extra_execution']['physical_model_requests']
            if panel == 'natural52':
                assert inherited['reused_head_model_seconds'] is None
                assert inherited['reused_head_model_seconds_unknown_inputs'] == 52
            else:
                assert entry['seeds']['42']['origin'] == 'historical_already_in_cycle1_cost_not_new_this_revision'
    for panel, table in units['panels'].items():
        assert table['new_model_calls'] == table['native_scorer_calls'] == 0
        for report in table['reports']:
            method, seed = report['method'], report['seed']
            group = quality['panels'][panel]['methods'][method]
            q = group['baseline'] if seed is None else group['seeds'][str(seed)]
            all_units = [u for u in report['units'] if u['category'] == 'ALL']
            assert len(all_units) == q['native_unit_ALL']['units']
            close(sum(u['score'] for u in all_units) / len(all_units), q['native_unit_ALL']['mean_native_unit_score'])
            checks['native_unit_groups'] += 1
    for panel, table in pairs['panels'].items():
        definitions = {d['pair_id']: d for d in table['definitions']}
        for method, methods in table['methods'].items():
            for seed, pair_group in [('', methods['baseline'])] + list(methods['seeds'].items()):
                records = pair_group['records']
                assert set(definitions) == {p['pair_id'] for p in records}
                for relation_summary in pair_group['summaries']['all']:
                    same = [p for p in records if p['relation'] == relation_summary['relation']]
                    assert len(same) == relation_summary['pairs']
                    assert len({p['family_id'] for p in same}) == relation_summary['families']
                    for key in ('both_correct', 'both_native_scored', 'unavailable_endpoints', 'valid_relation'):
                        assert sum(p[key] for p in same) == relation_summary[key]
                for pair in records:
                    definition = definitions[pair['pair_id']]
                    assert definition['family_id'] == pair['family_id'] and definition['relation'] == pair['relation']
                    for side in ('left', 'right'):
                        assert (panel, method, seed, definition[side]) in keyed
                checks['pair_groups'] += 1
    combined = quality['combined']
    assert combined['new_native_score_mappings'] == sum(p['new_native_score_mappings'] for p in quality['panels'].values()) == 247
    assert combined['independent_evaluation'] is False
    limitations = documents['failure_and_limitations.json']
    assert limitations['optional_F_reanswer_default'] is False
    assert limitations['analysis_error_and_correction']['scorer_calls_metadata_fix'] == 0
    assert limitations['scope32_counterexample']['M4']['old_F'] == 31
    assert limitations['scope32_counterexample']['M4']['ordinary_reanswer'] == 30
    for method in ('M4', 'M5'):
        m = quality['panels']['natural52']['methods'][method]
        assert all(s['counts']['correct'] < m['baseline']['counts']['correct'] and s['native_unit_mean_difference'] < 0 for s in m['seeds'].values())
    receipt = {'status': 'passed', 'checks': dict(checks), 'input_rows': len(rows), 'new_physical_call_rows': len(calls),
        'new_input_tokens': total['live_input_tokens'], 'new_output_tokens': total['live_output_tokens'],
        'native_score_mappings_previously_executed': 247,
        'models_called_by_this_verifier': 0, 'native_scorer_calls_by_this_verifier': 0,
        'verifier_sha256': sha(Path(__file__)), 'source_manifest_sha256': sha(root / 'source_manifest.json'),
        'interpretation': 'Offline consistency audit of published saved metadata, not independent native rescoring or clinical validation.'}
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
