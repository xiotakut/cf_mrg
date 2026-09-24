"""Offline quality and cost report for the fixed effect-first development tasks.

Inference never imports this module. The CLI reads only the existing 121-input
development label package, keeps failed/unsubmitted planned members, and creates
a new output directory. Target selection is a shared operation, not an answer.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

ROOT = Path('/home/data3/txy')
sys.path.insert(0, str(ROOT))
DEVELOPMENT = ROOT / 'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'

from cf_moa.contracts import digest
from cf_moa.evaluation.native_scoring import load_native_scorer, score_proposal, source_lock
from cf_moa.evaluation.score_run import unit_summaries
from cf_moa.tools.adopted import sha256


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write(path, values):
    Path(path).write_text(''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in values))


def counts(values):
    values = list(values)
    return dict(denominator=len(values), correct=sum(v['correct'] is True for v in values),
                incorrect=sum(v['correct'] is False for v in values),
                unavailable=sum(v['correct'] is None for v in values),
                not_submitted=sum(v.get('run_status') == 'not_submitted' for v in values),
                submitted_unavailable=sum(v['correct'] is None and v.get('run_status') != 'not_submitted'
                                          for v in values))


def compare(values, base):
    values = list(values)
    result = dict(repair_ids=[], harm_ids=[], unavailable_recovery_ids=[],
                  correct_unavailable_recovery_ids=[], correct_lost_to_unavailable_ids=[])
    for row in values:
        rid, new = row['request_id'], row['correct']
        old = base[rid]['correct']
        if old is False and new is True:
            result['repair_ids'].append(rid)
        if old is True and new is False:
            result['harm_ids'].append(rid)
        if old is None and new is not None:
            result['unavailable_recovery_ids'].append(rid)
        if old is None and new is True:
            result['correct_unavailable_recovery_ids'].append(rid)
        if old is True and new is None:
            result['correct_lost_to_unavailable_ids'].append(rid)
    result.update(repairs=len(result['repair_ids']), harms=len(result['harm_ids']),
        unavailable_recoveries=len(result['unavailable_recovery_ids']),
        correct_unavailable_recoveries=len(result['correct_unavailable_recovery_ids']),
        correct_lost_to_unavailable=len(result['correct_lost_to_unavailable_ids']),
        same_scope_B=counts(base[r['request_id']] for r in values),
        correct_count_delta=sum(r['correct'] is True for r in values)
                            - sum(base[r['request_id']]['correct'] is True for r in values))
    return result


def physical_cost(calls):
    events, count, unresolved = [], 0, 0
    for call in calls:
        physical = call.get('physical')
        if physical is not None:
            count += len(physical)
            events.extend(p['event'] for p in physical if p.get('event'))
            unresolved += sum(not p.get('event') and p.get('submission_state') != 'not_submitted'
                              for p in physical)
        elif call.get('phase') == 'submitted':
            unresolved += 1
    live = [event for event in events if event.get('mode') == 'live']
    return dict(physical_model_requests=count, new_model_requests=len(live),
                live_input_tokens=sum(e['input_tokens'] for e in live),
                live_output_tokens=sum(e['output_tokens'] for e in live),
                live_model_seconds=sum(e['elapsed_seconds'] for e in live),
                submission_attempts=len(calls), failed_attempts=sum(c.get('status') == 'failed' for c in calls),
                unresolved_model_usage=unresolved, model_usage_complete=unresolved == 0)


def find_runs(paths, methods):
    found = {}
    for path in paths:
        path = Path(path)
        options = [path] + [path / m.lower() for m in methods] + [path / m for m in methods]
        for candidate in options:
            source = candidate / 'plan.json'
            if not source.exists():
                continue
            method = json.loads(source.read_text()).get('method')
            if method not in methods:
                continue
            candidate = candidate.resolve()
            if method in found and found[method] != candidate:
                raise ValueError('More than one run supplied for method ' + method)
            found[method] = candidate
    return found


def score_development(plan_path, runs, output, *, development=DEVELOPMENT, scorer=None):
    plan_path, output, development = Path(plan_path), Path(output), Path(development)
    if output.exists():
        raise FileExistsError('Keep earlier scoring identities; choose a new output directory')
    plan = json.loads(plan_path.read_text())
    plan_hash = sha256(plan_path)
    sources = {str(plan_path.resolve()): plan_hash}

    def read_source(path, expected=None):
        path = Path(path)
        actual = sha256(path)
        if expected is not None and actual != expected:
            raise ValueError('Source differs from the selected plan: ' + str(path))
        sources[str(path.resolve())] = actual
        return rows(path)

    # This fixed development package is the only label source exposed by the CLI.
    items = {r['request_id']: r for r in read_source(development / 'offline/items.jsonl')}
    evaluations = read_source(development / 'offline/evaluations.jsonl')
    eval_by_id = defaultdict(list)
    for evaluation in evaluations:
        eval_by_id[evaluation['request_id']].append(evaluation)
    scorer = scorer or load_native_scorer()
    run_paths = find_runs(runs, plan['methods'])
    native, unique, unit_reports, methods = [], [], [], {}
    costs, target_states = {}, []
    for method, method_plan in plan['methods'].items():
        tasks = method_plan['tasks']
        task_by_id = {t['task_id']: t for t in tasks}
        if len(task_by_id) != len(tasks):
            raise ValueError('Duplicate planned task ID')
        bases = {r['request_id']: r for r in read_source(method_plan['bases'], method_plan.get('bases_sha256'))}
        packets = {r['request_id']: r for r in read_source(method_plan['inputs'], method_plan.get('inputs_sha256'))}
        run = run_paths.get(method)
        observed, calls = {}, []
        if run:
            run_plan = json.loads((run / 'plan.json').read_text())
            if run_plan.get('selected_source_sha256') != plan_hash:
                raise ValueError('Run was created from a different source plan: ' + str(run))
            sources[str(run / 'plan.json')] = sha256(run / 'plan.json')
            output_file = run / 'proposals.jsonl'
            if output_file.exists():
                for row in read_source(output_file):
                    key = row['task_id']
                    if key not in task_by_id or key in observed:
                        raise ValueError('Unexpected or duplicate output task: ' + key)
                    task = task_by_id[key]
                    if row['method'] != method or row['arm'] != task['arm'] or row['request_id'] != task['request_id']:
                        raise ValueError('Output task identity mismatch: ' + key)
                    if row['input_hash'] != bases[row['request_id']]['input_hash']:
                        raise ValueError('Output and baseline input identity differ: ' + key)
                    observed[key] = row
            if (run / 'model_calls.jsonl').exists():
                calls = read_source(run / 'model_calls.jsonl')
                identities = {(r['request_id'], r['ordinal']) for r in calls}
                if len(identities) != len(calls) or any(r['request_id'] not in task_by_id for r in calls):
                    raise ValueError('Duplicate or unplanned durable model call')
        groups = defaultdict(dict)
        for task in tasks:
            rid, arm = task['request_id'], task['arm']
            if rid not in items or rid not in eval_by_id or rid not in packets or rid not in bases:
                raise ValueError('Plan member is outside the current development package: ' + rid)
            row = observed.get(task['task_id'])
            if arm == 'target_select':
                result = (row or {}).get('result', {})
                target_states.append(dict(method=method, request_id=rid, task_id=task['task_id'],
                    execution_status=(row or {}).get('status', 'not_submitted'),
                    target=result.get('target'), target_available=result.get('target') is not None
                    and result.get('failure_type') is None, failure_type=result.get('failure_type'),
                    is_native_answer=False))
                continue
            if rid in groups[arm]:
                raise ValueError('Duplicate input within one arm; give repeated variants distinct arm names')
            groups[arm][rid] = row

        for cache in method_plan.get('cached_comparators', []):
            arm = cache['arm']
            if arm in groups:
                raise ValueError('Cached comparator collides with a planned live arm')
            cached = {r['request_id']: r for r in read_source(cache['path'], cache['sha256'])}
            for rid in cache['request_ids']:
                if rid not in items or rid not in bases or rid not in packets:
                    raise ValueError('Cached comparison member is outside the development plan input source')
                row = cached.get(rid)
                if row is not None and row.get('input_hash') != bases[rid]['input_hash']:
                    raise ValueError('Cached comparator input identity differs')
                groups[arm][rid] = dict(row, cached_comparator=True) if row is not None else None
        all_ids = list(dict.fromkeys(rid for group in groups.values() for rid in group))
        # A saved complete B is already available irrespective of whether its
        # optional zero-call runner task was submitted before an interruption.
        groups['baseline'] = {rid: dict(status='cached_baseline', result=bases[rid],
                                       cached_comparator=True) for rid in all_ids}

        def score_group(arm, group):
            local, local_native = [], []
            for rid, row in group.items():
                result = (row or {}).get('result', {})
                cached = bool((row or {}).get('cached_comparator'))
                saved_native = result.get('native_answer')
                valid = result.get('native_valid', False)
                if cached and 'proposal' in (row or {}):
                    proposal = row['proposal'] or {}
                    saved_native = proposal.get('native_proposal')
                    valid = saved_native is not None and row.get('status') == 'complete'
                elif cached and 'native_answer' in (row or {}):
                    saved_native = row['native_answer']
                    valid = saved_native is not None and row.get('status') == 'complete'
                valid = bool(valid and saved_native is not None)
                value = saved_native if valid else None
                proposal = dict(native_proposal=value, applicability='supported' if valid else 'failed')
                current = []
                for evaluation in eval_by_id[rid]:
                    scored = score_proposal(items[rid], evaluation, proposal, scorer=scorer)
                    entry = dict(method=method, arm=arm, request_id=rid, record_id=evaluation['record_id'],
                                 run_status=(row or {}).get('status', 'not_submitted'), **scored)
                    native.append(entry)
                    local_native.append(entry)
                    current.append(entry)
                correct = None if any(r['correct'] is None for r in current) else all(r['correct'] for r in current)
                base_native = bases[rid]['native_answer']
                modified = valid and saved_native is not None and base_native is not None and (
                    (saved_native.get('answer_choice') if isinstance(saved_native, dict) else saved_native)
                    != (base_native.get('answer_choice') if isinstance(base_native, dict) else base_native))
                state = dict(method=method, arm=arm, request_id=rid, correct=correct,
                    run_status=(row or {}).get('status', 'not_submitted'), native_valid=bool(valid),
                    native_mapping_count=len(current), native_answer_ref=digest(value) if value is not None else None,
                    method_score='scored' if correct is not None else 'not_scored',
                    mixed_native_correctness=len({r['correct'] for r in current}) > 1,
                    decision=result.get('decision'), actual_adjudication=bool(result.get('actual_adjudication')),
                    proposal_delivered=bool(result.get('actual_adjudication') and result.get('proposal') is not None),
                    modified_answer=bool(modified), repair_attempted=bool(result.get('repair_attempted')),
                    first_error=result.get('first_error'), failure_type=result.get('failure_type'),
                    warnings=len(result.get('warnings', [])), target=result.get('target'),
                    origin='saved_cache' if cached else 'current_run')
                unique.append(state)
                local.append(state)
            report = unit_summaries(local_native, evaluations)
            unit_reports.append(dict(method=method, arm=arm, **report))
            return local, dict(unique_inputs=counts(local), native_mappings=counts(local_native),
                native_unit_ALL=next(row for row in report['categories'] if row['category'] == 'ALL'),
                actual_adjudications=sum(r['actual_adjudication'] for r in local),
                proposal_delivered=sum(r['proposal_delivered'] for r in local),
                modified_answers=sum(r['modified_answer'] for r in local),
                format_repair_attempts=sum(r['repair_attempted'] for r in local),
                first_output_errors=sum(r['first_error'] is not None for r in local))

        base_rows, base_summary = score_group('baseline', groups.pop('baseline'))
        base_lookup = {r['request_id']: r for r in base_rows}
        summaries = dict(baseline=base_summary)
        for arm, group in groups.items():
            values, summary = score_group(arm, group)
            summary['relative_to_B'] = compare(values, base_lookup)
            summaries[arm] = summary
        methods[method] = dict(arms=summaries, planned_tasks=len(tasks),
                              recorded_tasks=len(observed), not_submitted_tasks=len(tasks)-len(observed))
        by_arm_calls = defaultdict(list)
        for call in calls:
            by_arm_calls[task_by_id[call['request_id']]['arm']].append(call)
        costs[method] = dict(total_new_execution=physical_cost(calls),
            shared_target_selection=physical_cost(by_arm_calls.pop('target_select', [])),
            answer_arms={arm: physical_cost(group) for arm, group in by_arm_calls.items()},
            historical_baseline_costs=sum_cost_rows(bases[rid].get('cost', {}) for rid in all_ids),
            historical_baseline_cost_not_added_to_new_execution=True,
            cost_log_available=run is not None and (run / 'model_calls.jsonl').exists())
    totals = sum_cost_rows(value['total_new_execution'] for value in costs.values())
    output.mkdir(parents=True)
    write(output / 'native_scored.jsonl', native)
    write(output / 'per_input_status.jsonl', unique)
    write(output / 'target_selection_status.jsonl', target_states)
    dump(output / 'native_unit_metrics.json', dict(reports=unit_reports,
        scope='Only units/mappings covered by each arm fixed plan. Partial units are descriptive; not independent evaluation.'))
    dump(output / 'cost_summary.json', dict(methods=costs, total_new_execution=totals,
        note='Physical durable events counted once. Shared target cost is already included in totals, not added again. '
             'Historical B costs are separate; reused expert-proposal acquisition is not included in these new-run costs. '
             'These are not complete method-attributed totals. Model wall time is not exclusive GPU latency or energy.'))
    summary = dict(status='development_scored_with_full_planned_denominators', plan_sha256=plan_hash,
        methods=methods, target_selection_count=len(target_states),
        no_independent_evaluation_claim=True, new_model_requests_during_scoring=0,
        definition='Unavailable includes not-submitted and retains the denominator; it is not an incorrect answer. '
                   'Repairs/harms compare wrong/right available answers; availability recoveries are separate.',
        source_plan=str(plan_path.resolve()))
    dump(output / 'summary.json', summary)
    dump(output / 'receipt.json', dict(source_hashes=sources, plan_sha256=plan_hash,
        script_sha256=sha256(Path(__file__)), native_scorer_sources=source_lock(),
        unit_summary_source=dict(path=str(ROOT / 'cf_moa/evaluation/score_run.py'),
                                 sha256=sha256(ROOT / 'cf_moa/evaluation/score_run.py')),
        native_score_mappings=len(native), unique_input_arm_rows=len(unique),
        read_independent_gold=False, old_results_modified=False, new_model_requests=0))
    return summary


def sum_cost_rows(values):
    total = Counter()
    for value in values:
        for key, amount in value.items():
            if isinstance(amount, (int, float)) and not isinstance(amount, bool):
                total[key] += amount
    return dict(total)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = score_development(args.plan, args.runs, args.output)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
