"""Bounded saved-score C0 table supplement. No model or scorer imports."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent.parent
SUP = RUN/'c0_missing_natural'
V4 = RUN.parents[1]/'2026-09-23/cf_moa_minimal_revision_20260923'
MISSING = {'n00000', 'n00005', 'n00019', 'n00030'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, allow_nan=False,
        separators=(',', ':')).encode()).hexdigest()


def load_supplement(original, evaluations, read):
    """Retain the old 48 source audit; append only completed fixed missing rows."""
    assert len(original) == 96 and Counter(r['method'] for r in original) == {'M4':48, 'M5':48}
    answer = deepcopy(original)
    eidx = {r['record_id']: r for r in evaluations}
    by_request = {r['request_id']: r for r in evaluations}
    info, costs, issues = {}, {}, []
    plan = read(V4/'natural_scope/plan_seed_42.json')
    auxiliary_path = SUP/'auxiliary_reuse/bindings.jsonl'
    auxiliary = {}
    if auxiliary_path.exists():
        receipt = read(auxiliary_path.parent/'receipt.json')
        assert receipt['output']['sha256'] == sha(auxiliary_path)
        assert receipt['new_model_calls'] == receipt['new_native_grader_calls'] == receipt['new_auxiliary_score_calls'] == 0
        bindings = read(auxiliary_path, True)
        assert len(bindings) == len({(r['method'], r['request_id']) for r in bindings}) == 24
        auxiliary = {(r['method'], r['request_id']):r for r in bindings}
    for method in ('M4', 'M5'):
        old = [r for r in original if r['method'] == method]
        absent = set(eidx)-{r['record_id'] for r in old}
        assert {eidx[r]['request_id'] for r in absent} == MISSING
        packets = {r['request_id']:r for r in read(plan['methods'][method]['inputs'], True)}
        assert all(packets[r].get('baseline_response') is None and packets[r].get('baseline_answer') is None for r in MISSING)
        added = []
        scored_path = SUP/f'analysis/{method.lower()}/new_native_scored.jsonl'
        if scored_path.exists():
            folder = SUP/f'{method.lower()}_live/run'
            status = read(folder/'status.json'); closed = read(folder/'supervisor_result.json')
            assert status['status'] == 'complete' and closed['exit_code'] == 0
            evidence = read(scored_path.parent/'receipt.json')
            assert evidence['new_grader_calls'] == 4 and evidence['old48_grader_calls'] == 0
            for path in (folder/'proposals.jsonl', folder/'status.json', folder/'supervisor_result.json'):
                assert evidence['sources'][str(path)] == sha(path)
            outputs = {r['request_id']:r for r in read(folder/'proposals.jsonl', True)}
            assert set(outputs) == MISSING
            added = read(scored_path, True)
            assert len(added) == 4 and {r['record_id'] for r in added} == absent
            for row in added:
                rid = row['request_id']
                assert row['method'] == method and row['arm'] == 'original'
                assert row['record_id'] == by_request[rid]['record_id']
                assert row['native_answer_ref'] == digest(outputs[rid]['result']['native_answer'])
                assert all(row.get(k) == v for k, v in by_request[rid].items())
            assert status['cost']['physical_model_requests'] == 4
            answer.extend(deepcopy(added))
            costs[method] = dict(incremental_execution=status['cost'],
                new_run_wall_seconds=status['elapsed_seconds'], source=str(folder/'status.json'),
                new_outputs=4, timing_note='Model event time is batch wall attribution; recorded_call_wall_seconds repeats lazy initialization and is not exclusive GPU time.')
        for record in sorted(absent):
            issues.append(dict(panel='natural52', model=method, record_id=record, request_id=eidx[record]['request_id'],
                original_response_absent_in_historical_packet=True,
                status='completed_original_C0_supplement' if added else 'original_response_absent_not_just_missing_score',
                original_score_available=bool(added), native_single_or_combined_head_not_substituted=True))
        info[method] = dict(denominator=52, inherited_original_inputs=48,
            supplemental_original_inputs=len(added), observed_inputs=48+len(added),
            missing_inputs=4-len(added), status='complete' if added else 'partial_original_response_absent')
        for row in answer:
            if row['method'] != method:
                continue
            binding = auxiliary.get((method, row['request_id']))
            if not binding or binding['status'] != 'exact_saved_auxiliary_reuse':
                continue
            assert binding['record_id'] == row['record_id']
            assert binding['raw_response_hash'] == digest(packets[row['request_id']]['baseline_response'])
            assert all(binding['identity_checks'].values())
            if 'document_detection' in row:
                assert row['document_detection'] == binding['document_detection']
            row['document_detection'] = binding['document_detection']
            row['auxiliary_score_origin'] = dict(kind='exact_saved_C0_auxiliary_reuse', binding_source=str(auxiliary_path))
        info[method]['auxiliary_planned'] = 12
        info[method]['auxiliary_available'] = sum('document_detection' in r for r in answer if r['method'] == method)
    assert all(all(next(r for r in answer if r['method'] == old['method'] and r['record_id'] == old['record_id'])[k] == v
                   for k, v in old.items()) for old in original)
    return answer, info, costs, issues


def cost_row(method, supplement):
    row = dict(panel='natural52', model=method, control='C0', attributed_input_tokens=None,
        attributed_output_tokens=None, attributed_model_requests=None,
        inherited_original48_cost='unknown_not_reconstructed_not_zero',
        cost_status='partial_cost_only_known_supplement; historical_original_cost_unknown',
        inference_scope='original_C0_existing_context_readout_no_new_retrieval')
    if supplement:
        row.update(supplement, physical_execution_origin='four_completed_missing_original_C0_requests')
    else:
        row.update(incremental_execution=None, new_outputs=0,
                   physical_execution_origin='four_missing_original_C0_requests_not_completed')
    return row


def supplement_tables(here, out, read, dump, write, units):
    """Reuse the existing five-table snapshot; replace natural C0 rows only."""
    stat = read(RUN/'statistics/receipt.json')
    evaluations = read(stat['source_bindings']['natural52']['evaluations'], True)
    pairs = read(stat['source_bindings']['natural52']['pairs'], True)
    pointer = read(V4/'natural_scope/offline/baseline_native_scores_reused.jsonl', True)
    assert {r['original_arm'] for r in pointer} == {'combined_head'}
    paths = {r['score_source'] for r in pointer}; assert len(paths) == 1
    records = {r['record_id']:r for r in evaluations}
    original = [dict(r,request_id=records[r['record_id']]['request_id']) for r in read(next(iter(paths)), True)
                if r['arm'] == 'original' and r['record_id'] in records]
    merged, status, costs, issues = load_supplement(original, evaluations, read)
    old_unique_path = RUN.parents[1]/'2026-09-24/cf_moa_candidate_verify_20260924/recovery_gpu23/analysis/complete_results/per_input_status.jsonl'
    baseline = {(r['method'],r['request_id']):r for r in read(old_unique_path, True)
                if r['panel'] == 'natural52' and r['arm'] == 'F'}
    names = ['table1_native_effects.json', 'table1_source_R_strata.json', 'table2_selection_mechanisms.json',
             'table3_pairs_auxiliary.json', 'table3_A4_separate_model_scope.json',
             'table4_operation_ablations.json', 'table5_quality_cost.json']
    tables = {name:read(here/name) for name in names}
    for name in ('table1_source_R_strata.json', 'table3_pairs_auxiliary.json'):
        tables[name] = [r for r in tables[name] if not (r['panel']=='natural52' and r['control']=='C0')]
    for method in ('M4','M5'):
        scores = [r for r in merged if r['method']==method]
        by = {r['record_id']:r for r in scores}; assert len(by)==len(scores)
        us = units(scores,evaluations); all_units = [u for u in us if u['category']=='ALL']
        complete = set(by)==set(records)
        row = next(r for r in tables['table1_native_effects.json'] if (r['panel'],r['model'],r['control'])==('natural52',method,'C0'))
        row.update(status=status[method]['status'], observed_inputs=len(scores), observed_native_mappings=len(scores),
            correct_inputs_observed=sum(r['correct'] is True for r in scores), unavailable_inputs=sum(r['correct'] is None for r in scores),
            not_available_original_inputs=52-len(scores), native_ALL_mean=sum(u['score'] for u in all_units)/18 if complete else None,
            repair_inputs_vs_B=sum(r['correct'] is True and baseline[method,r['request_id']]['correct'] is False for r in scores),
            harm_inputs_vs_B=sum(r['correct'] is False and baseline[method,r['request_id']]['correct'] is True for r in scores))
        assert len(all_units)==18
        for source in ['ALL',*sorted({r['resource_id'] for r in evaluations})]:
            for category in ['ALL','R1','R2','R3','R4','R5']:
                group=[r for r in us if r['category']==category and (source=='ALL' or r['source']==source)]
                if not group:continue
                have=all(r['score'] is not None for r in group)
                tables['table1_source_R_strata.json'].append(dict(panel='natural52',model=method,control='C0',source=source,category=category,
                    units=len(group),scored_units=sum(r['score'] is not None for r in group),
                    mean_native_unit_score=sum(r['score'] for r in group)/len(group) if have else None,
                    status='complete' if have else 'partial',overlapping_R_categories_not_summed=True))
        for relation in ('maintain','respond'):
            ps=[r for r in pairs if r['relation']==relation]
            known=[r for r in ps if r['left_record_id'] in by and r['right_record_id'] in by]
            correct=sum(by[r['left_record_id']]['correct'] is True and by[r['right_record_id']]['correct'] is True for r in known)
            tables['table3_pairs_auxiliary.json'].append(dict(panel='natural52',model=method,control='C0',metric=relation+'_both_correct',
                denominator=len(ps),observed_pairs=len(known),correct_observed=correct,value=correct/len(ps) if len(known)==len(ps) else None))
        aux=[r['document_detection'] for r in scores if 'document_detection' in r]
        tables['table3_pairs_auxiliary.json'].append(dict(panel='natural52',model=method,control='C0',metric='native_auxiliary_fields',
            denominator=12,observed_auxiliary_mappings=len(aux),valid=sum(r['valid'] is True for r in aux) if aux else None,
            exact=sum(r['exact'] is True for r in aux) if aux else None,
            **{k:sum(r[k] or 0 for r in aux) if aux else None for k in ('tp','fp','fn')},
            status='exact_saved_scores' if len(aux)==12 else 'partial_saved_auxiliary_unknown_not_recomputed',correction_semantic_score=None))
        target=next(r for r in tables['table5_quality_cost.json'] if (r['panel'],r['model'],r['control'])==('natural52',method,'C0'))
        target.clear();target.update(cost_row(method,costs.get(method)))
    for name, rows in tables.items():dump(name,rows)
    write('c0_missing_originals.jsonl',issues)
    write('c0_natural_merged_scored.jsonl',merged)
    # Unchanged earlier C5 interval output is copied, never bootstrapped again.
    dump('c5_paired_effects.json',read(here/'c5_paired_effects.json'))
    return status
