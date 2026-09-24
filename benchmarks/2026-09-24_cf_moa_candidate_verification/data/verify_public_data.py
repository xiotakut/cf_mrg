"""Verify published metadata with Python stdlib; no private files/model/grader."""
import hashlib
import json
import math
import argparse
from collections import Counter, defaultdict
from pathlib import Path


def read(root, name):
    text = (root / name).read_text()
    return [json.loads(line) for line in text.splitlines()] if name.endswith('.jsonl') else json.loads(text)


def verify(root, check_manifest=True):
    root = Path(root)
    summary = read(root, 'quality_summary.json')
    costs = read(root, 'cost_summary.json')['costs']
    statuses = read(root, 'per_input_status.jsonl')
    native = read(root, 'native_scoring_metadata.jsonl')
    calls = read(root, 'model_call_metadata.jsonl')
    selections = read(root, 'candidate_selection_metadata.jsonl')
    failed = read(root, 'prior_initialization_failures.jsonl')
    reviews = read(root, 'prior_semantic_review_metadata.jsonl')
    examples = read(root, 'fixed_smoke_counterexample_metadata.jsonl')
    assert len(summary['reports']) == len(costs) == 40
    assert len(statuses) == 3460 and len(native) == 4180
    assert len(calls) == 780 and len(selections) == 190
    assert len(failed) == 32 and len(reviews) == 31 and len(examples) == 4
    key = lambda x: (x['panel'], x['method'], x['arm'])
    grouped = defaultdict(list)
    native_grouped = defaultdict(list)
    for row in statuses:
        grouped[key(row)].append(row)
    for row in native:
        native_grouped[key(row)].append(row)
    assert len(grouped) == len(native_grouped) == 40
    assert len({key(x) for x in costs}) == 40
    for row in summary['reports']:
        group = grouped[key(row)]
        n = 121 if row['panel'] == 'historical121' else 52
        assert len(group) == n == row['counts']['denominator']
        assert len({x['request_id'] for x in group}) == n
        assert sum(bool(x['correct']) for x in group) == row['counts']['correct']
        assert len(native_grouped[key(row)]) == (157 if n == 121 else 52)
        assert math.isclose(row['accuracy_full_denominator'], row['counts']['correct'] / n)
        base = {x['request_id']: x for x in grouped[(row['panel'], row['method'], 'F')]}
        assert row['repairs'] == sum(bool(not base[x['request_id']]['correct'] and x['correct']) for x in group)
        assert row['harms'] == sum(bool(base[x['request_id']]['correct'] and not x['correct']) for x in group)
        for category in row['native_unit_metrics']['categories']:
            units = [x for x in row['native_unit_metrics']['units'] if x['category'] == category['category']]
            assert len(units) == category['units']
            if units:
                assert math.isclose(sum(x['score'] for x in units) / len(units), category['mean_native_unit_score'])
            else:
                assert category['mean_native_unit_score'] is None
        for pair in row['pairs']['summaries']:
            records = [x for x in row['pairs']['records'] if x['relation'] == pair['relation']]
            assert len(records) == pair['pairs']
            assert sum(x['both_correct'] for x in records) == pair['both_correct']
    assert Counter(x['method'] for x in calls) == {'M4': 420, 'M5': 360}
    assert all(x['status'] == 'complete' and x['error_type'] is None for x in calls)
    assert all(x['decoding_parameters_match_constructed_request'] for x in calls)
    assert all(x['engine_interface_normalization'] == {'output_kind': {'constructed': 0, 'engine_accepted': 2}} for x in calls)
    for row in calls:
        p = row['actual_sampling_parameters']
        assert p['temperature'] == 0 and p['max_tokens'] == 1 and p['seed'] == 42
        assert row['actual_engine_parameters']['max_model_len'] == 131072
        assert row['event']['output_tokens'] == 1 and row['event']['mode'] == 'live'
        assert set(row['code_logprobs']) == {'A', 'B'}
    input_tokens = sum(x['event']['input_tokens'] for x in calls)
    output_tokens = sum(x['event']['output_tokens'] for x in calls)
    seconds = sum(x['event']['elapsed_seconds'] for x in calls)
    assert (input_tokens, output_tokens) == (5504408, 780)
    assert math.isclose(seconds, 858.7597930309421)
    for cost in costs:
        if cost['arm'] not in {'candidate_only', 'candidate_with_rationales'}:
            continue
        matching = [x for x in calls if x['panel'] == cost['panel'] and
                    x['method'] == cost['method'] and x['arm'] == 'a5_' + cost['arm']]
        extra = cost['extra_execution']
        assert len(matching) == extra['physical_model_requests'] == extra['logical_score_callbacks']
        assert sum(x['event']['input_tokens'] for x in matching) == extra['live_input_tokens']
        assert sum(x['event']['output_tokens'] for x in matching) == extra['live_output_tokens']
        assert math.isclose(sum(x['event']['elapsed_seconds'] for x in matching), extra['live_model_seconds'])
        assert extra['generation_requests'] == extra['missing_code_fetch_requests'] == extra['failed_attempts'] == 0
    assert len({(x['method'], x['task_id'], x['ordinal']) for x in calls}) == 780
    assert Counter(x['method'] for x in selections) == {'M4': 106, 'M5': 84}
    verified = [x for x in selections if x['verification_status'] == 'verified_candidate_selection']
    assert len(verified) == 176
    assert all(x['status'] == 'complete' and not x['verification_failed'] for x in selections)
    assert all(not x['verification_fallback_saved_F'] for x in selections)
    assert sum(x['cost']['physical_model_requests'] for x in selections) == 780
    for row in verified:
        trace = row['trace_metadata']
        assert len(trace['records']) == len(trace['candidate_keys']) * 2
        assert trace['selected_key'] in trace['candidate_keys']
        assert Counter(x['key'] for x in trace['records']) == {x: 2 for x in trace['candidate_keys']}
        representative = next(x for x in trace['representatives'] if x['key'] == trace['selected_key'])
        assert representative['original_response_index'] == trace['selected_original_response_index']
    assert all(x['phase'] == 'initializing' and x['valid_model_requests'] == 0 for x in failed)
    seeds = [x for row in reviews for x in row['seed_outcomes']]
    assert len(seeds) == 93 and sum(x['repair'] for x in seeds) == 35 and sum(x['harm'] for x in seeds) == 40
    assert sum(x['quote_locations_checked_in_private_trace'] for x in examples) == 26
    # Exact forbidden data keys; do not filter public source-code prompts or
    # legitimate scalar metric names such as raw_exact and request hashes.
    forbidden = {'messages', 'prompt', 'question', 'native_input', 'native_options',
                 'raw_response', 'selected_raw_response', 'native_answer',
                 'semantic_gold', 'gold', 'gold_keys_offline', 'gold_keys_offline_only',
                 'engine_prompt_token_ids', 'prompt_token_ids', 'input_ids',
                 'allowed_token_ids', 'stop_token_ids', 'quote', 'content'}
    def check(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value), forbidden.intersection(value)
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)
    for name in ('quality_summary.json', 'cost_summary.json', 'per_input_status.jsonl',
                 'native_scoring_metadata.jsonl', 'model_call_metadata.jsonl',
                 'candidate_selection_metadata.jsonl', 'prior_initialization_failures.jsonl',
                 'prior_semantic_review_metadata.jsonl', 'fixed_smoke_counterexample_metadata.jsonl'):
        check(read(root, name))
    if check_manifest:
        manifest = read(root, 'source_manifest.json')
        for record in manifest['public_files']:
            data = (root / record['path']).read_bytes()
            assert len(data) == record['bytes']
            assert hashlib.sha256(data).hexdigest() == record['sha256'], record['path']
    return {'status': 'passed', 'quality_groups': 40, 'per_input_rows': 3460,
            'native_scoring_mapping_rows': 4180, 'model_call_rows': 780,
            'input_tokens': input_tokens, 'output_tokens': output_tokens,
            'live_model_seconds': seconds, 'execution_output_rows': 190,
            'verified_non_NLI_outputs': 176, 'retained_NLI_outputs': 14,
            'prior_initialization_failures': 32, 'reviewed_old_change_groups': 31,
            'old_review_seed_rows': 93, 'old_review_repairs': 35, 'old_review_harms': 40,
            'fixed_smoke_counterexamples': 4, 'private_quote_locations_checked': 26,
            'full_historical_denominator': 121, 'full_natural_denominator': 52,
            'forbidden_raw_data_keys_found': 0,
            'verification_scope': 'Public consistency only; no private medical semantic regrading.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(verify(args.data_dir), ensure_ascii=False, indent=2))
