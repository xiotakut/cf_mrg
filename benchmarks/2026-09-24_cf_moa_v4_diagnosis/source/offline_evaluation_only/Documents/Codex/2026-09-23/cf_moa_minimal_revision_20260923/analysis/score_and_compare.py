"""Offline trigger-only scoring; reuse B, seed42 and every unchanged score.

Model execution never imports this module. All fixed members, including failed
answers, remain in the native and unique-input denominators.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import random
from statistics import mean
import sys

ROOT = Path('/home/data3/txy')
sys.path.insert(0, str(ROOT))
from cf_moa.contracts import digest
from cf_moa.evaluation.native_scoring import load_native_scorer, score_proposal, source_lock
from cf_moa.evaluation.paired_metrics import paired_metrics
from cf_moa.evaluation.score_run import unit_summaries
from cf_moa.tools.adopted import sha256

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
OLD = ROOT / 'Documents/Codex/2026-09-21/cf_moa/effect_first_revision_20260923'
DEV = ROOT / 'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
METHODS = ('M4', 'M5')
SEEDS = (42, 43, 44)
spec = importlib.util.spec_from_file_location('old_effect_first_score', OLD / 'score_development.py')
old_score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old_score)


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


class Sources:
    def __init__(self):
        self.hashes = {}

    def read(self, path, expected=None, *, lines=False):
        path = Path(path)
        value = sha256(path)
        if expected is not None and value != expected:
            raise ValueError('Changed plan-bound source: ' + str(path))
        self.hashes[str(path)] = value
        text = path.read_text()
        return [json.loads(line) for line in text.splitlines() if line.strip()] if lines else json.loads(text)

    def check(self):
        if any(sha256(path) != value for path, value in self.hashes.items()):
            raise ValueError('Source changed while scoring')


def unique_rows(native, bases, observed=None):
    grouped = defaultdict(list)
    for row in native:
        grouped[row['request_id']].append(row)
    result = []
    for rid, records in grouped.items():
        row = (observed or {}).get(rid)
        answer = (row or {}).get('result', {}).get('native_answer') if observed is not None else bases[rid]['native_answer']
        correct = None if any(r['correct'] is None for r in records) else all(r['correct'] for r in records)
        native_valid = all(r['native_available'] for r in records)
        result.append(dict(request_id=rid, correct=correct, native_valid=native_valid,
            native_mapping_count=len(records), method_score='not_scored' if correct is None else 'scored',
            run_status=(row or {}).get('status', 'cached_baseline'),
            native_answer_ref=digest(answer) if answer is not None else None,
            mixed_native_correctness=len({r['correct'] for r in records}) > 1,
            first_error=(row or {}).get('result', {}).get('first_error'),
            failure_type=(row or {}).get('result', {}).get('failure_type'),
            repair_attempted=bool((row or {}).get('result', {}).get('repair_attempted'))))
    return result


def comparison(rows, baseline):
    value = old_score.compare(rows, baseline)
    value['counts'] = old_score.counts(rows)
    value['accuracy_full_denominator'] = value['counts']['correct'] / value['counts']['denominator']
    assert value['correct_count_delta'] == (value['repairs'] - value['harms']
        + value['correct_unavailable_recoveries'] - value['correct_lost_to_unavailable'])
    return value


def metadata(items, evaluations):
    grouped = defaultdict(list)
    for row in evaluations:
        grouped[row['request_id']].append(row)
    result = {}
    for rid, group in grouped.items():
        # source_family is a source taxonomy (e.g. MedQA), not patient family.
        # The existing selected-family and paired ledgers both use group_id.
        family = {e['group_id'] for e in group}
        source = {e['resource_id'] for e in group}
        if len(family) != 1 or len(source) != 1:
            raise ValueError('An input spans incompatible family/source clusters')
        result[rid] = dict(family_id=next(iter(family)), source=next(iter(source)),
                          answer_format=items[rid]['answer_format'])
    return result


def stratify(rows, baseline, meta):
    result = {}
    for field in ('family_id', 'source', 'answer_format'):
        grouped = defaultdict(list)
        for row in rows:
            grouped[meta[row['request_id']][field]].append(row)
        result[field] = {name: comparison(group, baseline) for name, group in sorted(grouped.items())}
    return result


def bootstrap_difference(by_method_seed, baseline, meta, *, resamples=2000, seed=20260923):
    """Cluster whole families; within-draw input weighting and equal seeds/bones."""
    ids = list(meta)
    groups = defaultdict(list)
    for rid in ids:
        groups[meta[rid]['family_id']].append(rid)
    names = sorted(groups)
    values = {}
    for method in METHODS:
        values[method] = {rid: mean(int(by_method_seed[method][s][rid]['correct'] is True)
            - int(baseline[method][rid]['correct'] is True) for s in SEEDS) for rid in ids}
    values['equal_backbone_mean'] = {rid: mean(values[m][rid] for m in METHODS) for rid in ids}
    result = {}
    for method, diffs in values.items():
        rng = random.Random(seed)
        estimates = []
        for _ in range(resamples):
            selected = [rid for fam in rng.choices(names, k=len(names)) for rid in groups[fam]]
            estimates.append(mean(diffs[rid] for rid in selected))
        estimates.sort()
        def quantile(p):
            position = (len(estimates) - 1) * p
            lower = int(position)
            return estimates[lower] + (estimates[min(lower + 1, len(estimates)-1)] - estimates[lower]) * (position-lower)
        result[method] = dict(mean_accuracy_difference=mean(diffs.values()),
            mean_correct_count_difference=sum(diffs.values()), ci95=[quantile(.025), quantile(.975)],
            families=len(groups), inputs=len(ids), resamples=resamples, bootstrap_seed=seed,
            seed_policy='equal average of all fixed 42/43/44; B/F held fixed',
            cluster='family', weighting='input weighted within cluster draw; equal backbone weights')
    return result


def inherited_cost(bases):
    keys = ('reused_head_model_requests', 'reused_head_input_tokens', 'reused_head_output_tokens', 'reused_head_model_seconds')
    result = {}
    for key in keys:
        known = [row['cost'].get(key) for row in bases.values() if row['cost'].get(key) is not None]
        missing = len(bases) - len(known)
        result[key] = sum(known) if not missing else None
        result[key + '_known_subtotal'] = sum(known)
        result[key + '_unknown_inputs'] = missing
    result['interpretation'] = 'Frozen B/F acquisition attributed once per deployed method; reused across all seed experiments. Common historical initial answers excluded where prior accounting excludes them. Unknown timing is not zero.'
    return result


def pair_report(native, pairs, support, *, seed, resamples):
    predictions = {r['record_id']: r for r in native}
    records = []
    summaries = {}
    for scope in ('all', 'F_supported', 'F_unsupported', 'F_mixed'):
        mapped = []
        for p in pairs:
            left, right = support[p['left']], support[p['right']]
            coverage = 'F_supported' if left and right else 'F_unsupported' if not left and not right else 'F_mixed'
            if scope not in ('all', coverage):
                continue
            mapped.append(dict(p, left=p['left_record_id'], right=p['right_record_id']))
        metric = paired_metrics(predictions, mapped, seed=seed, resamples=resamples)
        summaries[scope] = metric['summaries']
        if scope == 'all':
            records = metric['records']
    return dict(summaries=summaries, records=records)


def run_closed(sources, plan_path, run_path, method):
    plan = sources.read(plan_path)
    status = sources.read(run_path / 'status.json')
    if status.get('status') not in ('complete', 'complete_with_item_failures'):
        raise RuntimeError('Run is not closed: ' + str(run_path) + ' ' + str(status.get('status')))
    actual_plan = sources.read(run_path / 'plan.json')
    if actual_plan.get('selected_source_sha256') != sha256(plan_path) or actual_plan['method'] != method:
        raise ValueError('Run identity differs from the frozen source plan')
    observed = sources.read(run_path / 'proposals.jsonl', lines=True)
    tasks = {t['task_id']: t for t in plan['methods'][method]['tasks']}
    lookup = {r['request_id']: r for r in observed}
    if len(lookup) != len(observed) or set(lookup) != set(plan['panel_ids']):
        raise ValueError('Closed run has an incomplete or duplicate full denominator')
    for row in observed:
        task = tasks[row['task_id']]
        if row['arm'] != 'a5_reanswer' or row['request_id'] != task['request_id'] or row['method'] != method:
            raise ValueError('Output identity mismatch')
    calls = sources.read(run_path / 'model_calls.jsonl', lines=True)
    if len({(c['request_id'], c['ordinal']) for c in calls}) != len(calls):
        raise ValueError('Duplicate durable physical call')
    if any(c['request_id'] not in tasks for c in calls):
        raise ValueError('Unplanned durable model call')
    return plan, lookup, calls


def score_panel(panel, reuse_scored=None):
    output = HERE / panel
    if output.exists():
        raise FileExistsError('Preserve earlier score identity: ' + str(output))
    sources = Sources()
    cached_native = None
    if reuse_scored is not None:
        previous_receipt = sources.read(reuse_scored / 'receipt.json')
        for path, value in previous_receipt['source_hashes'].items():
            if sha256(path) != value:
                raise ValueError('Prior score source changed before metadata-only reanalysis: ' + path)
        cached_native = {(r['method'], r['seed'], r['record_id']): r for r in
                         sources.read(reuse_scored / 'native_scored.jsonl', lines=True)}
    protocol = sources.read(RUN / 'analysis_plan.json')
    natural = panel == 'natural52'
    development = RUN / 'natural_scope' if natural else DEV
    items = {r['request_id']: r for r in sources.read(development / 'offline/items.jsonl', lines=True)}
    evaluations = sources.read(development / 'offline/evaluations.jsonl', lines=True)
    pairs = sources.read(development / 'offline/pairs.jsonl', lines=True)
    meta = metadata(items, evaluations)
    eval_by_id = defaultdict(list)
    for evaluation in evaluations:
        eval_by_id[evaluation['request_id']].append(evaluation)
    expected_count = 52 if natural else 121
    assert len(meta) == expected_count
    new_runs = {}
    for method in METHODS:
        for seed in (SEEDS if natural else (43, 44)):
            plan = RUN / 'natural_scope' / f'plan_seed_{seed}.json' if natural else RUN / 'seeds' / f'seed_{seed}' / 'plan.json'
            run = RUN / 'natural_runs' / f'seed_{seed}' / method.lower() if natural else RUN / 'seeds' / f'seed_{seed}' / method.lower()
            new_runs[method, seed] = run_closed(sources, plan, run, method)
    # No native scoring begins until every requested run in this panel is closed.
    old_native = sources.read((development / 'offline/baseline_native_scores_reused.jsonl') if natural
        else OLD / 'a5_quality121/results/native_scored.jsonl', lines=True)
    score_fields = set(next(row for row in old_native if row['method'] == 'M4')) if not natural else None
    if natural:
        # Reuse original score fields, excluding its embedded full evaluation payload.
        historical_sample = sources.read(OLD / 'a5_quality121/results/native_scored.jsonl', lines=True)[0]
        score_fields = set(historical_sample)
    bases_by_method, baseline, new_unique, all_native, all_unique = {}, {}, defaultdict(dict), [], []
    summaries, cost, new_score_calls, actual_scorer_calls = {}, {}, 0, 0
    scoring = load_native_scorer()
    bootstrap = protocol['uncertainty']
    for method in METHODS:
        plan = new_runs[method, 43][0]
        method_plan = plan['methods'][method]
        bases = {r['request_id']: r for r in sources.read(method_plan['bases'], method_plan['bases_sha256'], lines=True)}
        if set(bases) != set(meta):
            raise ValueError('Baseline and evaluation scope differ')
        bases_by_method[method] = bases
        sources.read(method_plan['proposals'], method_plan['proposals_sha256'], lines=True)
        if natural:
            saved = {r['request_id']: r for r in sources.read(development / 'cache_reuse_audit.jsonl', lines=True)
                     if r['method'] == method}
            membership = {r['request_id']: r for r in sources.read(development / 'manifest.json')['selected']}
            support = {rid: membership[rid]['route'] == 'F' for rid in meta}
            if not all(support.values()):
                raise ValueError('Natural panel must retain its preselected F-only route scope')
        else:
            saved = {r['request_id']: r for r in sources.read(OLD / 'a5_preparation' / (method.lower() + '_saved_f.jsonl'), lines=True)}
            support = {rid: saved[rid]['supported'] for rid in meta}
        triggers = {rid: saved[rid]['trigger'] for rid in meta}
        base_native = []
        for row in old_native:
            if row['method'] != method or row['arm'] != 'baseline':
                continue
            copied = {k: deepcopy(v) for k, v in row.items() if k in score_fields}
            copied.update(method=method, arm='baseline', native_available=bases[row['request_id']]['native_valid'],
                method_score='scored' if bases[row['request_id']]['native_valid'] else 'not_scored',
                semantic_result='native_answer_available' if bases[row['request_id']]['native_valid'] else 'unavailable',
                score_origin='reused_existing_B_native_score', run_status='cached_baseline')
            base_native.append(copied)
        assert len(base_native) == len(evaluations)
        baseline[method] = {r['request_id']: r for r in unique_rows(base_native, bases)}
        base_by_record = {r['record_id']: r for r in base_native}
        if set(base_by_record) != {e['record_id'] for e in evaluations}:
            raise ValueError('Existing B score mappings do not match evaluation records')
        all_native.extend(dict(row, seed=None) for row in base_native)
        all_unique.extend(dict(row, method=method, seed=None, arm='baseline', **meta[row['request_id']]) for row in baseline[method].values())
        base_units = unit_summaries(base_native, evaluations)
        base_all = next(r for r in base_units['categories'] if r['category'] == 'ALL')
        summaries[method] = dict(baseline=dict(counts=old_score.counts(baseline[method].values()),
            native_unit_ALL=base_all, pairs=pair_report(base_native, pairs, support,
                seed=bootstrap['seed'], resamples=bootstrap['resamples'])), seeds={})
        cost[method] = dict(inherited_B=inherited_cost(bases), seeds={})
        for seed in SEEDS:
            reused_mapping_count, scored_mapping_count = 0, 0
            if seed == 42 and not natural:
                native = [dict(row, score_origin='reused_historical_seed42_native_score') for row in old_native
                          if row['method'] == method and row['arm'] == 'a5_reanswer']
                prior_unique = sources.read(OLD / 'a5_quality121/results/per_input_status.jsonl', lines=True)
                unique = [deepcopy(r) for r in prior_unique if r['method'] == method and r['arm'] == 'a5_reanswer']
                old_calls = sources.read(OLD / 'a5_quality121' / method.lower() / 'model_calls.jsonl', lines=True)
                calls = [c for c in old_calls if c['request_id'].endswith(':a5_reanswer')]
                execution_cost = old_score.physical_cost(calls)
                cost_origin = 'historical_already_in_cycle1_cost_not_new_this_revision'
                reused_mapping_count = len(native)
            else:
                _, observed, calls = new_runs[method, seed]
                native = []
                calls_by_id = Counter(c['request_id'].split(':')[0] for c in calls)
                for rid in meta:
                    row = observed[rid]
                    if row['input_hash'] != bases[rid]['input_hash']:
                        raise ValueError('New output and frozen B input differ')
                    value = row.get('result', {}).get('native_answer')
                    valid = bool(row.get('result', {}).get('native_valid') and value is not None)
                    native_value = value if valid else None
                    if not triggers[rid]:
                        if calls_by_id[rid] or digest(native_value) != digest(bases[rid]['native_answer']):
                            raise ValueError('Nontrigger consumed model calls or changed the frozen B answer')
                        current = [dict(base_by_record[e['record_id']], arm='a5_reanswer',
                            run_status=row['status'], score_origin='reused_unchanged_B_native_score') for e in eval_by_id[rid]]
                        reused_mapping_count += len(current)
                    else:
                        current = []
                        for evaluation in eval_by_id[rid]:
                            if cached_native is not None:
                                scored = deepcopy(cached_native[method, seed, evaluation['record_id']])
                                if scored['request_id'] != rid or scored['native_available'] != valid:
                                    raise ValueError('Prior triggered native score identity differs')
                                scored.pop('seed', None)
                                current.append(scored)
                            else:
                                scored = score_proposal(items[rid], evaluation,
                                    dict(native_proposal=native_value, applicability='supported' if valid else 'failed'), scorer=scoring)
                                current.append(dict(method=method, arm='a5_reanswer', request_id=rid,
                                    record_id=evaluation['record_id'], run_status=row['status'],
                                    score_origin='new_trigger_native_score', **scored))
                                actual_scorer_calls += 1
                            new_score_calls += 1
                            scored_mapping_count += 1
                    native.extend(current)
                unique = unique_rows(native, bases, observed)
                execution_cost = old_score.physical_cost(calls)
                cost_origin = 'new_physical_execution_this_revision'
            assert len(unique) == expected_count and len(native) == len(evaluations)
            new_unique[method][seed] = {r['request_id']: r for r in unique}
            report = unit_summaries(native, evaluations)
            unit_all = next(r for r in report['categories'] if r['category'] == 'ALL')
            summary = comparison(unique, baseline[method])
            summary.update(native_unit_ALL=unit_all,
                native_unit_mean_difference=unit_all['mean_native_unit_score'] - base_all['mean_native_unit_score'],
                strata=stratify(unique, baseline[method], meta),
                pairs=pair_report(native, pairs, support, seed=bootstrap['seed'], resamples=bootstrap['resamples']),
                predeclared_triggers=sum(triggers.values()), F_supported=sum(support.values()),
                new_native_score_mappings=scored_mapping_count, reused_native_score_mappings=reused_mapping_count,
                all_planned_inputs_retained=True)
            summaries[method]['seeds'][str(seed)] = summary
            cost[method]['seeds'][str(seed)] = dict(origin=cost_origin, extra_execution=execution_cost,
                attributed_input_tokens=cost[method]['inherited_B']['reused_head_input_tokens'] + execution_cost['live_input_tokens'],
                attributed_output_tokens=cost[method]['inherited_B']['reused_head_output_tokens'] + execution_cost['live_output_tokens'],
                attributed_model_requests=cost[method]['inherited_B']['reused_head_model_requests'] + execution_cost['new_model_requests'])
            all_native.extend(dict(row, seed=seed) for row in native)
            all_unique.extend(dict(row, method=method, seed=seed, arm='a5_reanswer', trigger=triggers[row['request_id']],
                                  F_supported=support[row['request_id']], **meta[row['request_id']]) for row in unique)
        summaries[method]['equal_seed_mean'] = dict(
            correct_count=mean(summaries[method]['seeds'][str(s)]['counts']['correct'] for s in SEEDS),
            net_correct_count=mean(summaries[method]['seeds'][str(s)]['correct_count_delta'] for s in SEEDS),
            native_unit_mean_difference=mean(summaries[method]['seeds'][str(s)]['native_unit_mean_difference'] for s in SEEDS),
            native_unit_score=mean(summaries[method]['seeds'][str(s)]['native_unit_ALL']['mean_native_unit_score'] for s in SEEDS),
            seeds=list(SEEDS), best_seed_selection=False)
    uncertainty = bootstrap_difference(new_unique, baseline, meta,
        resamples=bootstrap['resamples'], seed=bootstrap['seed'])
    totals = old_score.sum_cost_rows(v['extra_execution'] for m in cost.values() for v in m['seeds'].values()
        if v['origin'] == 'new_physical_execution_this_revision')
    summary = dict(panel=panel, status='complete_offline_comparison', denominator_per_backbone=expected_count,
        families=len({v['family_id'] for v in meta.values()}), native_mappings_per_arm=len(evaluations),
        methods=summaries, uncertainty=uncertainty, new_physical_execution=totals,
        new_native_score_mappings=new_score_calls, independent_evaluation=False,
        actual_native_scorer_calls_this_command=actual_scorer_calls,
        exposed_development=True, fixed_B_conditional_stability_only=True,
        old_B_and_seed42_rescored=False, full_denominators=True,
        note='All seeds reported; input correctness and non-reference equal-unit native metrics have different weights. '
             'Unavailable is not an incorrect answer and remains in every denominator. '
             'Natural52 retains M23_control as an explicitly separate source; not all inputs are unperturbed clinical cases.')
    sources.check()
    output.mkdir()
    write(output / 'native_scored.jsonl', all_native)
    write(output / 'per_input_status.jsonl', all_unique)
    dump(output / 'summary.json', summary)
    dump(output / 'cost.json', dict(methods=cost, new_physical_execution=totals,
        definition='Never sum inherited B over seeds to claim new physical cost. Seed42 history on121 is excluded from this revision physical total. Model seconds are cumulative event times, not exclusive GPU latency.'))
    dump(output / 'receipt.json', dict(created_at=dt.datetime.now().astimezone().isoformat(), source_hashes=sources.hashes,
        source_bytes_unchanged=True, native_scorer_sources=source_lock(), script_sha256=sha256(Path(__file__)),
        new_native_score_mappings=new_score_calls, old_B_and_seed42_rescored=False, new_model_calls=0,
        actual_native_scorer_calls_this_command=actual_scorer_calls,
        previous_same_revision_scores_reused=str(reuse_scored) if reuse_scored is not None else None,
        reused_functions=['native_scoring.score_proposal', 'score_run.unit_summaries', 'paired_metrics.paired_metrics'],
        analysis_plan_sha256=sha256(RUN / 'analysis_plan.json')))
    return summary


def combined():
    panels = {name: json.loads((HERE / name / 'summary.json').read_text()) for name in ('historical121', 'natural52')}
    result = dict(status='complete_both_fixed_panels', panels={}, no_best_seed_selection=True,
        new_physical_execution=old_score.sum_cost_rows(p['new_physical_execution'] for p in panels.values()),
        new_native_score_mappings=sum(p['new_native_score_mappings'] for p in panels.values()),
        new_model_calls_during_analysis=0, independent_evaluation=False)
    for name, panel in panels.items():
        result['panels'][name] = dict(
            equal_backbone_seed_mean_net_count=mean(panel['methods'][m]['equal_seed_mean']['net_correct_count'] for m in METHODS),
            equal_backbone_seed_mean_native_delta=mean(panel['methods'][m]['equal_seed_mean']['native_unit_mean_difference'] for m in METHODS),
            uncertainty=panel['uncertainty'], per_backbone={m: panel['methods'][m]['equal_seed_mean'] for m in METHODS})
    consistent = all(p['equal_backbone_seed_mean_net_count'] > 0 and p['equal_backbone_seed_mean_native_delta'] > 0
                     for p in result['panels'].values())
    result['recommendation'] = ('review_small_development_signal_with_family_format_regressions_before_optional_adoption'
        if consistent else 'keep_equivalent_B_default_F_reanswer_optional_not_adopted_as_stable_increment')
    result['recommendation_is_offline_research_judgment_not_online_gate'] = True
    dump(HERE / 'combined_summary.json', result)
    lines = ['# Fixed-head minimal revision: completed comparison', '',
        'This is fixed B/F conditional stability on exposed development inputs, not end-to-end seed stability or independent evaluation.', '',
        '| Panel | Backbone | B correct | Seed 42 | Seed 43 | Seed 44 | Mean net count | Mean native-unit delta |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for name, panel in panels.items():
        for method in METHODS:
            m = panel['methods'][method]
            line = f'| {name} | {method} | {m["baseline"]["counts"]["correct"]}/{panel["denominator_per_backbone"]} | '
            line += ' | '.join(str(m['seeds'][str(s)]['counts']['correct']) for s in SEEDS)
            line += f' | {m["equal_seed_mean"]["net_correct_count"]:+.3f} | {100*m["equal_seed_mean"]["native_unit_mean_difference"]:+.3f} pp |'
            lines.append(line)
    lines += ['', 'Recommendation: `' + result['recommendation'] + '`.', '',
        'Per-seed repair/harm/unavailability, source/format/family changes, paired both-correct results and family bootstrap intervals are in each panel summary. '
        'The natural panel includes separately identified M23_control author-derived premise controls. '
        'The historical Scope32 M4 regression (31→30; M5 31→31) remains an external negative development counterexample.', '',
        'Costs: ' + json.dumps(result['new_physical_execution'], ensure_ascii=False) + '.', '',
        'Old B and historical seed42 scores were reused. Only new triggered outputs were passed to the unchanged native scorer. '
        'Nontrigger outputs were checked for exact native equality before score reuse. No old score file was modified. '
        'Inherited B/F costs are listed separately; unknown historical per-input model timing remains null.']
    (HERE / 'report.md').write_text('\n'.join(lines) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--panel', choices=('historical121', 'natural52', 'all'), default='all')
    parser.add_argument('--reuse-native-scored', type=Path,
        help='Reuse same-revision native scores for a recorded metadata-only analysis fix')
    args = parser.parse_args()
    selected = ('historical121', 'natural52') if args.panel == 'all' else (args.panel,)
    for name in selected:
        if (HERE / name / 'receipt.json').exists():
            print(json.dumps(dict(panel=name, status='reuse_already_completed_analysis_no_rescoring')))
        else:
            result = score_panel(name, reuse_scored=args.reuse_native_scored)
            print(json.dumps(dict(panel=name, status=result['status'], new_native_score_mappings=result['new_native_score_mappings'])))
    if all((HERE / n / 'summary.json').exists() for n in ('historical121', 'natural52')):
        print(json.dumps(combined()))


if __name__ == '__main__':
    main()
