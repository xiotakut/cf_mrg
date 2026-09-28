"""Bounded full-v5 C1-C5 mechanism/cost projection; no model or grader imports.

All inputs are declared in --sources. Original native parse/norm/semantic mapping
are AST-loaded without loading or executing score(). Outputs contain no prompts.
"""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ARMS = ('strong_B', 'candidate_only', 'candidate_with_rationales',
        'pool_old_plus_three', 'joint_selector')
VOTE = 'full_native_key_maj5_absolute_majority_stop'
NLI = 'full_nli_equal_paths_native_completion'
TERMINAL = {'complete', 'completed', 'unavailable', 'failed', 'error'}
COST_FIELDS = ('model_requests', 'input_tokens', 'output_tokens', 'model_seconds')
ZERO = dict.fromkeys(COST_FIELDS, 0)


def rows(path):
    with Path(path).open() as stream:
        for line, text in enumerate(stream, 1):
            if text.strip():
                yield line, json.loads(text)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


class NativeSemantics:
    """Execute ONLY original parse, norm and nested semantic mapping, never score."""
    def __init__(self, parser_source, normalizer_source, canonical_source):
        namespace = dict(json=json, re=re)
        self.sources = []
        for path, name in ((normalizer_source, 'norm'), (parser_source, 'parse')):
            text = Path(path).read_text()
            nodes = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name]
            if len(nodes) != 1:
                raise ValueError('Missing original native function: '+name)
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
            self.sources.append(dict(path=str(Path(path).resolve()), sha256=hashlib.sha256(text.encode()).hexdigest()))
        tree = ast.parse(Path(parser_source).read_text())
        score = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'score')
        self.semantic_node = next(n for n in score.body if isinstance(n, ast.FunctionDef) and n.name == 'semantic')
        self.semantic_code = compile(ast.Module(body=[self.semantic_node], type_ignores=[]), '<original native semantic>', 'exec')
        self.parse, self.norm = namespace['parse'], namespace['norm']
        labels = json.loads(Path(canonical_source).read_text())['labels']
        self.canonical = {self.norm(s): s for s in labels}
        self.sources.append(dict(path=str(Path(canonical_source).resolve()), sha256=hashlib.sha256(Path(canonical_source).read_bytes()).hexdigest()))

    def value(self, item, native):
        if native is None:
            return None, 'unavailable'
        answer = native.get('answer_choice') if isinstance(native, dict) else native
        current = dict(item)
        if current['answer_format'] == 'robustness_single':
            current['answer_format'] = 'single'
        prediction, error, _ = self.parse(json.dumps({'answer': answer}, ensure_ascii=False), current, self.canonical)
        if error:
            return None, error
        ns = dict(norm=self.norm, opts=current['options'])
        exec(self.semantic_code, ns)
        return ns['semantic'](prediction), None


def known_sum(values):
    return sum(values) if all(isinstance(v, (int, float)) for v in values) else None


def cost_value(raw):
    """Normalize recorded usage; unknown timing/usage remains null, never free."""
    if raw is None:
        return dict.fromkeys(COST_FIELDS)
    if 'reused_head_model_requests' in raw:
        names = ('reused_head_model_requests', 'reused_head_input_tokens', 'reused_head_output_tokens', 'reused_head_model_seconds')
        return dict(zip(COST_FIELDS, (raw.get(k) for k in names)))
    if 'reused_generation_calls' in raw:
        names = ('reused_generation_calls', 'reused_input_tokens', 'reused_output_tokens', 'reused_model_seconds')
        return dict(zip(COST_FIELDS, (raw.get(k) for k in names)))
    result = dict(model_requests=known_sum([raw.get('new_model_requests'), raw.get('replayed_model_requests', 0)]),
        input_tokens=known_sum([raw.get('live_input_tokens'), raw.get('replayed_original_input_tokens', 0)]),
        output_tokens=known_sum([raw.get('live_output_tokens'), raw.get('replayed_original_output_tokens', 0)]),
        model_seconds=raw.get('live_model_seconds'))
    if result['model_requests'] == 0 and result['input_tokens'] == 0 and result['output_tokens'] == 0:
        result['model_seconds'] = 0
    if raw.get('replayed_model_requests', 0):
        result['model_seconds'] = known_sum([result['model_seconds'], raw.get('replayed_original_model_seconds')])
    if raw.get('missing_usage', 0) or raw.get('unresolved_model_usage', 0) or raw.get('model_usage_complete') is False:
        # Keep partial known sums separately in the raw cost; don't call them totals.
        result['input_tokens'] = result['output_tokens'] = result['model_seconds'] = None
    return result


def original_elapsed(event):
    """A cross-run replay's zero destination elapsed is not its attributed cost."""
    while event.get('mode') == 'replay':
        event = event.get('original_event')
        if not isinstance(event, dict):
            return None
    return event.get('elapsed_seconds')


def with_event_seconds(raw, callbacks):
    if raw is None or callbacks is None:
        return raw
    expected = raw.get('physical_model_requests', known_sum([
        raw.get('new_model_requests'), raw.get('replayed_model_requests', 0)]))
    if expected != len(callbacks):
        return raw  # No invented association between partial callbacks and a total.
    events = [c.get('event') for c in callbacks]
    live = [e for e in events if isinstance(e, dict) and e.get('mode') == 'live']
    replay = [e for e in events if isinstance(e, dict) and e.get('mode') == 'replay']
    result = dict(raw)
    if len(live)+len(replay) != len(events):
        result['live_model_seconds'] = result['replayed_original_model_seconds'] = None
    else:
        result['live_model_seconds'] = known_sum([e.get('elapsed_seconds') for e in live])
        result['replayed_original_model_seconds'] = known_sum([original_elapsed(e) for e in replay])
    return result


def add_cost(a, b):
    return {key: known_sum([a[key], b[key]]) for key in COST_FIELDS}


def execution_cost_parts(raw):
    if raw is None:
        return dict.fromkeys(COST_FIELDS), dict.fromkeys(COST_FIELDS)
    fresh = dict(raw, replayed_model_requests=0, replayed_original_input_tokens=0,
                 replayed_original_output_tokens=0)
    fresh = cost_value(fresh)
    replay = dict(model_requests=raw.get('replayed_model_requests', 0),
        input_tokens=raw.get('replayed_original_input_tokens', 0),
        output_tokens=raw.get('replayed_original_output_tokens', 0),
        model_seconds=raw.get('replayed_original_model_seconds'))
    if replay['model_requests'] == 0:
        replay['model_seconds'] = 0
    return fresh, replay


def inherited_remainder(total, fresh, replay):
    result = {}
    for key in COST_FIELDS:
        numbers = [total[key], fresh[key], replay[key]]
        value = numbers[0]-numbers[1]-numbers[2] if all(isinstance(v, (int, float)) for v in numbers) else None
        if value is not None and value < -1e-7:
            raise ValueError('Method cost smaller than its actual new/replay usage: '+key)
        result[key] = max(0, value) if value is not None else None
    return result


def pool_record(item, proposal, semantics):
    trace = proposal.get('trace') or {}
    route = trace.get('route')
    out = dict(route=route, trace_hash=digest(trace), cost=cost_value(proposal.get('cost')),
        original_cost=proposal.get('cost'), K=None, candidate_semantics=[], invalid_vote_count=0,
        actual_votes=None, stopped_early=trace.get('stopped_early'), source_complete=True)
    if route == NLI:
        out['stratum'] = 'NLI'
        return out
    if route != VOTE:
        out.update(stratum='pool_unknown', source_complete=False, unknown_reason='unrecognized_F_trace_route')
        return out
    predictions, responses = trace.get('predictions'), trace.get('responses')
    if not isinstance(predictions, list) or not isinstance(responses, list) or len(predictions) != len(responses):
        out.update(stratum='pool_unknown', source_complete=False, unknown_reason='missing_or_misaligned_actual_F_responses')
        return out
    keys, semantic = set(), []
    for key, raw in zip(predictions, responses):
        if key is None:
            out['invalid_vote_count'] += 1
            continue
        if key in keys:
            continue
        try:
            native = json.loads(raw)
            if not isinstance(native, dict) or native.get('answer_choice') != key:
                raise ValueError('response/prediction mismatch')
            value, error = semantics.value(item, native)
            if error:
                raise ValueError(error)
        except (TypeError, ValueError) as exc:
            out.update(stratum='pool_unknown', source_complete=False, unknown_reason=str(exc))
            return out
        keys.add(key)
        semantic.append(dict(key=key, semantic=value))
    out.update(K=len(keys), candidate_semantics=semantic, actual_votes=len(predictions),
        stratum='K=1' if len(keys) == 1 else ('K>=2' if len(keys) >= 2 else 'K=0'))
    return out


def audit_state(result, row, pool, arm, terminal):
    if not terminal:
        return 'pending', False
    verification = result.get('verification') or {}
    trace = verification.get('trace') or {}
    status = verification.get('status')
    activated = trace.get('route') in ('candidate_verification', 'same_pool_joint_selection', 'old_pool_plus_three')
    activated = activated or (row.get('reuse_origin') in ('same_saved_verification_requests', 'same_saved_C5_requests', 'same_saved_three_paid_reanswers'))
    if status == 'technical_failure' or trace.get('errors') or trace.get('fallback_saved_F'):
        return 'audit_unavailable_saved_F_fallback' if result.get('native_answer') is not None else 'audit_and_native_unavailable', activated
    if result.get('native_answer') is None:
        return 'whole_native_unavailable', activated
    if arm == 'strong_B':
        return 'baseline_no_verifier', False
    if verification and (status in ('selected_candidate', 'verified_candidate_selection') or (status == 'complete' and activated)):
        return 'completed_selection', activated
    if row.get('reuse_origin') == 'same_saved_three_paid_reanswers':
        return 'completed_sampling_control', True
    if activated:
        return 'selection_status_unknown', True
    if pool and pool.get('stratum') == 'NLI':
        return 'retained_NLI', False
    if pool and pool.get('K') is not None and pool['K'] < 2:
        return 'retained_K_below_2', False
    if result.get('operations', {}).get('selected_component') not in (None, 'F') or row.get('reuse_origin') == 'non_F_identical_adopted_B':
        return 'non_F_no_verifier', False
    if status and status.startswith('retained_'):
        return status, False
    return 'audit_status_unknown', False


def extra_cost(row, result, arm, pool):
    if arm == 'strong_B':
        return dict(ZERO), 'none'
    origin = row.get('reuse_origin')
    if origin in ('same_saved_verification_requests', 'same_saved_C5_requests', 'same_saved_three_paid_reanswers'):
        return cost_value(result.get('reused_method_cost')), 'historical_extra_only'
    if origin in ('non_F_identical_adopted_B', 'fixed_zero_call_F_policy'):
        return dict(ZERO), 'none'
    if 'stage_costs' in result:
        return cost_value(result['stage_costs'].get('verification')), 'current_stage_including_exact_replay'
    verification = result.get('verification')
    if verification and 'cost' in verification:
        return cost_value(verification['cost']), 'verification_record'
    return dict.fromkeys(COST_FIELDS), 'missing_extra_cost'


def supplementary_semantics(item, verification, semantics):
    """Only the three actual complete C4 returns, never inferred from vote counts."""
    replies = ((verification or {}).get('trace') or {}).get('supplementary')
    if not isinstance(replies, list) or len(replies) != 3:
        return dict(complete=False, reason='three_saved_supplementary_responses_unavailable')
    candidates = []
    for reply in replies:
        native = reply.get('native_answer') if isinstance(reply, dict) else None
        value, error = semantics.value(item, native)
        if error or not isinstance(native, dict):
            return dict(complete=False, reason='supplementary_native_semantics_unavailable')
        candidates.append(dict(key=native['answer_choice'], semantic=value))
    return dict(complete=True, candidates=candidates)


def c4_expanded_pool(pool, supplementary, selected_key, gold, gold_known, activated):
    result = dict(expanded_pool_contains_gold=None, expanded_first_correct_candidate=None,
        selected_old_or_new=None, expanded_K=None,
        expanded_unknown_reason='C4_not_activated' if not activated else 'old_F_pool_unavailable')
    if not activated or not pool or not pool.get('source_complete') or pool.get('route') != VOTE:
        return result
    old = pool['candidate_semantics']
    old_keys = {r['key'] for r in old}
    if selected_key in old_keys:
        result['selected_old_or_new'] = 'old'
    if not supplementary or not supplementary.get('complete'):
        result['expanded_unknown_reason'] = (supplementary or {}).get('reason', 'three_saved_supplementary_responses_unavailable')
        return result
    added = supplementary['candidates']
    all_keys = old_keys | {r['key'] for r in added}
    result['expanded_K'] = len(all_keys)
    if selected_key in all_keys and selected_key not in old_keys:
        result['selected_old_or_new'] = 'new'
    if not gold_known:
        result['expanded_unknown_reason'] = 'saved_semantic_gold_unknown'
        return result
    contained = any(digest(r['semantic']) == digest(gold) for r in old)
    expanded = contained or any(digest(r['semantic']) == digest(gold) for r in added)
    result.update(expanded_pool_contains_gold=expanded,
        expanded_first_correct_candidate=expanded and not contained,
        expanded_unknown_reason=None)
    return result


def compact_output(row, item, semantics):
    result = row.get('result') or {}
    native = result.get('native_answer')
    selected, parse_error = semantics.value(item, native)
    # Retain only the fields needed for this projection, never repeated messages.
    compact = {k: result.get(k) for k in ('cost', 'stage_costs', 'reused_B_cost', 'reused_method_cost', 'operations') if k in result}
    callbacks = row.get('model_callbacks')
    if callbacks is not None and result.get('stage_costs'):
        stages = result['stage_costs']
        count = (stages.get('adopted_B') or {}).get('physical_model_requests')
        if isinstance(count, int):
            compact['stage_costs'] = dict(adopted_B=with_event_seconds(stages.get('adopted_B'), callbacks[:count]),
                verification=with_event_seconds(stages.get('verification'), callbacks[count:]))
    verification = result.get('verification')
    if verification:
        tr = verification.get('trace') or {}
        compact['verification'] = dict(status=verification.get('status'), cost=verification.get('cost'), trace={k: tr[k] for k in ('route', 'errors', 'fallback_saved_F', 'selected_key', 'seeds', 'logical_score_calls') if k in tr})
    compact['native_answer'] = None if native is None else {'present': True}
    return dict(status=row.get('status'), result=compact, reuse_origin=row.get('reuse_origin'),
        native_hash=digest(native), selected_semantic=selected, native_parse_error=parse_error,
        selected_key=native.get('answer_choice') if isinstance(native, dict) else None,
        c4_supplementary=(supplementary_semantics(item, verification, semantics)
            if row.get('arm') == 'pool_old_plus_three' else None),
        execution_cost_parts=execution_cost_parts(with_event_seconds(row.get('cost', result.get('cost')), callbacks)),
        input_hash=row.get('input_hash'))


def physical_costs(sources):
    """Count unique durable physical events, not output copies or callback walks."""
    buckets = defaultdict(lambda: dict(callbacks=0, physical_records=0, live_requests=0,
        input_tokens=0, output_tokens=0, model_seconds=0., unknown_usage=0,
        cross_run_replay_events=0, replayed_original_input_tokens=0, replayed_original_output_tokens=0,
        replayed_original_unknown_usage=0, non_live_physical_events=0, failed_callbacks=0))
    seen, refs, journals = set(), [], []
    for source in sources:
        path = Path(source['path']).resolve()
        identity = (path.stat().st_dev, path.stat().st_ino)
        if identity in seen:
            continue
        seen.add(identity)
        method, scope = source['method'], source.get('scope', 'current')
        bucket = buckets[method, scope]
        db = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)
        db.execute('PRAGMA query_only=ON')
        count = 0
        for task, ordinal, status, phase, events_text, physical_len in db.execute(
                "SELECT request_id,ordinal,status,phase,json_extract(result,'$.events'),json_array_length(physical) FROM calls ORDER BY rowid"):
            count += 1
            bucket['callbacks'] += 1
            bucket['failed_callbacks'] += status == 'failed'
            if not physical_len and phase == 'submitted':
                bucket['unknown_usage'] += 1
            for index, event in enumerate(json.loads(events_text) if events_text else []):
                if event.get('mode') != 'replay':
                    continue
                bucket['cross_run_replay_events'] += 1
                old = event
                while isinstance(old.get('original_event'), dict):
                    old = old['original_event']
                if all(isinstance(old.get(k), (int, float)) for k in ('input_tokens', 'output_tokens')):
                    bucket['replayed_original_input_tokens'] += old['input_tokens']
                    bucket['replayed_original_output_tokens'] += old['output_tokens']
                else:
                    bucket['replayed_original_unknown_usage'] += 1
                refs.append(dict(method=method, destination_journal=str(path), task_id=task,
                    ordinal=ordinal, event_index=index, source=event.get('source_reference'),
                    new_physical_requests=0))
        # JSON SQL projection avoids materializing raw prompts, token ID arrays and answers.
        query = """SELECT c.request_id,c.ordinal,p.key,json_extract(p.value,'$.event'),
            json_extract(p.value,'$.submission_state') FROM calls c,json_each(c.physical) p"""
        for task, ordinal, index, event_text, state in db.execute(query):
            bucket['physical_records'] += 1
            if not event_text:
                bucket['unknown_usage'] += state != 'not_submitted'
                continue
            event = json.loads(event_text)
            if event.get('mode') != 'live':
                bucket['non_live_physical_events'] += 1
                continue
            bucket['live_requests'] += 1
            if not all(isinstance(event.get(k), (int, float)) for k in ('input_tokens', 'output_tokens', 'elapsed_seconds')):
                bucket['unknown_usage'] += 1
            for key, target in [('input_tokens', 'input_tokens'), ('output_tokens', 'output_tokens'), ('elapsed_seconds', 'model_seconds')]:
                value = event.get(key)
                if isinstance(value, (int, float)):
                    bucket[target] += value
        db.close()
        journals.append(dict(path=str(path), method=method, scope=scope, callbacks=count))
    return dict(by_model_scope=[dict(method=m, scope=s, **b) for (m, s), b in sorted(buckets.items())],
        journals=journals, replay_source_references=refs,
        identity='resolved journal inode + call(request_id,ordinal) + physical entry index; repeated file declarations deduplicated',
        unknown_usage_policy='Known subtotals exclude unknown usage; unknown is not zero. Replay original usage never adds a new physical event.',
        elapsed_policy='Recorded event elapsed attribution, not exclusive GPU runtime or energy.')


def summarize(records):
    groups = defaultdict(list)
    for row in records:
        for dimension, values in [('all', ['ALL']), ('format', [row['answer_format']]),
                ('pool', [row['pool_stratum']]), ('family', row['family_ids'] or ['unknown'])]:
            for value in values:
                groups[row['method'], row['arm'], dimension, value].append(row)
    result = []
    for (method, arm, dimension, value), values in sorted(groups.items()):
        terminal = [r for r in values if r['execution_status'] == 'terminal']
        covered = [r for r in terminal if r['pool_contains_gold'] is True]
        selected = [r for r in covered if r['selected_correct_by_saved_semantics'] is True]
        known = [r for r in terminal if r['pool_contains_gold'] is not None]
        expanded_known = [r for r in terminal if r['expanded_pool_contains_gold'] is not None]
        expanded_covered = [r for r in expanded_known if r['expanded_pool_contains_gold']]
        cost = {}
        for category in ('method_attributed_cost', 'new_execution_cost', 'exact_replay_attributed_cost', 'inherited_other_cost'):
            cost[category] = {}
            for field in COST_FIELDS:
                have = [r[category][field] for r in terminal if r[category][field] is not None]
                cost[category][field] = dict(known_subtotal=sum(have), known_rows=len(have), unknown_rows=len(terminal)-len(have))

        result.append(dict(method=method, arm=arm, dimension=dimension, value=value,
            planned=len(values), terminal=len(terminal), pending=len(values)-len(terminal),
            status='complete' if len(values)==len(terminal) else 'partial',
            native_unavailable=sum(r['native_unavailable'] for r in terminal),
            activation_attempted=sum(r['activation_attempted'] for r in terminal),
            audit_status_counts=dict(Counter(r['audit_status'] for r in values)),
            pool_known=len(known), pool_contains_gold=len(covered),
            candidate_coverage_pool='old_F_only; C4 expanded pool is separate below',
            saved_semantic_gold_unknown=sum(not r['saved_semantic_gold_known'] for r in terminal),
            selected_semantic_unavailable_when_covered=sum(r['selected_correct_by_saved_semantics'] is None for r in covered),
            candidate_coverage=len(covered)/len(known) if known else None,
            selected_correct_given_pool_contains_gold=len(selected)/len(covered) if covered else None,
            selection_denominator=len(covered), selection_numerator=len(selected),
            C4_expanded_pool_known=len(expanded_known),
            C4_expanded_pool_contains_gold=len(expanded_covered),
            C4_expanded_candidate_coverage=len(expanded_covered)/len(expanded_known) if expanded_known else None,
            C4_first_correct_candidate_appeared=sum(r['expanded_first_correct_candidate'] is True for r in terminal),
            C4_selected_correct_given_expanded_pool_contains_gold=(sum(r['selected_correct_by_saved_semantics'] is True for r in expanded_covered)/len(expanded_covered) if expanded_covered else None),
            C4_selected_old_or_new=dict(Counter(r['selected_old_or_new'] or 'unknown' for r in terminal
                if r['arm'] == 'pool_old_plus_three' and r['activation_attempted'])),
            C4_expanded_unknown_reasons=dict(Counter(r['expanded_unknown_reason'] for r in terminal
                if r['arm'] == 'pool_old_plus_three' and r['activation_attempted'] and r['expanded_unknown_reason'])),
            saved_native_score_status=dict(Counter(r['saved_native_score_status'] for r in values)),
            cost=cost))
    return result


def run(spec, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    semantics = NativeSemantics(**spec['native_semantics'])
    summary, provenance = [], []
    total_rows = 0
    with (out/'per_input_mechanism_cost.jsonl').open('w') as destination:
        for method, config in spec['methods'].items():
            items = {r['request_id']: r for _, r in rows(config['items'])}
            families, eval_ids = defaultdict(set), defaultdict(set)
            for _, e in rows(config['evaluations']):
                rid = e['request_id']
                if rid in items:
                    families[rid].add(e.get('family_id', e.get('group_id', 'unknown')))
                    eval_ids[rid].add(e['record_id'])
            gold_by_record, score_by_task = {}, defaultdict(dict)
            for path in config['native_scores']:
                for _, row in rows(path):
                    if row.get('method', method) != method or row['request_id'] not in items:
                        continue
                    rid, record = row['request_id'], row['record_id']
                    if record not in eval_ids[rid]:
                        raise ValueError('Score mapping absent from declared evaluations: '+record)
                    if 'semantic_gold' in row:
                        old = gold_by_record.get((rid, record))
                        if old is not None and digest(old) != digest(row['semantic_gold']):
                            raise ValueError('Saved semantic gold conflict: '+record)
                        gold_by_record[rid, record] = row['semantic_gold']
                    arm = row.get('arm')
                    if arm in ARMS and (row.get('analysis_status') in (None, 'scored')) and 'correct' in row:
                        score_by_task[rid, arm][record] = dict(correct=row['correct'], native_answer_ref=row.get('native_answer_ref'))
            pools, base_costs, components, output = {}, {}, {}, {}
            declared_historical_costs = {}
            for path in config.get('cost_source_outputs', []):
                for line, row in rows(path):
                    if row.get('method') == method:
                        raw = row.get('cost', (row.get('result') or {}).get('cost'))
                        declared_historical_costs[str(Path(path).resolve()), line] = cost_value(
                            with_event_seconds(raw, row.get('model_callbacks')))
                provenance.append(dict(method=method, kind='declared_historical_cost_source', path=str(path)))
            for path in config.get('f_proposals', []):
                for line, row in rows(path):
                    rid = row['request_id']
                    if rid not in items:
                        continue
                    pool = pool_record(items[rid], row['proposal'], semantics)
                    pools[rid] = pool
                    provenance.append(dict(method=method, kind='saved_F', path=str(path), line=line, request_id=rid))
            for path in config.get('bases', []):
                for _, row in rows(path):
                    if row['request_id'] in items:
                        base_costs[row['request_id']] = cost_value(row['result'].get('cost'))
                        components[row['request_id']] = row['result'].get('operations', {}).get('selected_component')
            for path in config['outputs']:
                count = 0
                for line, row in rows(path):
                    if row.get('method') != method:
                        continue
                    rid, arm = row['request_id'], row['arm']
                    if rid not in items or arm not in ARMS:
                        raise ValueError('Output outside declared panel/arm: '+str((rid, arm)))
                    key = rid, arm
                    compact = compact_output(row, items[rid], semantics)
                    reference = row.get('source_ref') or {}
                    declared = declared_historical_costs.get((str(Path(reference.get('path', '.')).resolve()), reference.get('line')))
                    if declared is not None and row.get('reuse_origin') in ('same_saved_verification_requests', 'same_saved_C5_requests'):
                        compact['declared_historical_extra_cost'] = declared
                    old = output.get(key)
                    if old and (old['native_hash'], old['status']) != (compact['native_hash'], compact['status']):
                        raise ValueError('Conflicting output identities: '+str(key))
                    if old is None:
                        compact['source'] = dict(path=str(path), line=line)
                        output[key] = compact
                    result = row.get('result') or {}
                    component = (result.get('operations') or {}).get('selected_component')
                    if component is not None:
                        components[rid] = component
                    proposal = result.get('f_proposal')
                    if proposal:
                        pool = pool_record(items[rid], proposal, semantics)
                        if rid in pools and pools[rid]['trace_hash'] != pool['trace_hash']:
                            raise ValueError('C1-C5 do not share the same F pool: '+rid)
                        base_calls = ((result.get('stage_costs') or {}).get('adopted_B') or {}).get('physical_model_requests', 0)
                        if base_calls and row.get('model_callbacks') is not None:
                            pool['cost'] = cost_value(with_event_seconds(proposal.get('cost'), row['model_callbacks'][:base_calls]))
                        if rid in pools and pool['cost']['model_seconds'] is None:
                            pool['cost']['model_seconds'] = pools[rid]['cost']['model_seconds']
                        pools[rid] = pool
                    if arm == 'strong_B' and 'stage_costs' in result:
                        base_costs[rid] = add_cost(cost_value(compact['result']['stage_costs'].get('adopted_B')),
                            cost_value(result.get('reused_B_cost')) if result.get('reused_B_cost') is not None else dict(ZERO))
                    count += 1
                provenance.append(dict(method=method, kind='outputs', path=str(path), rows=count))
            records = []
            for rid, item in items.items():
                pool = pools.get(rid)
                values = [gold_by_record.get((rid, record)) for record in eval_ids[rid]]
                gold_known = bool(values) and all(v is not None for v in values) and len({digest(v) for v in values}) == 1
                gold = values[0] if gold_known else None
                covered = (any(digest(v['semantic']) == digest(gold) for v in pool['candidate_semantics'])
                    if pool and pool['source_complete'] and pool['route'] == VOTE and gold_known else None)
                for arm in ARMS:
                    row = output.get((rid, arm), {})
                    result = row.get('result') or {}
                    terminal = row.get('status') in TERMINAL
                    audit, active = audit_state(result, row, pool, arm, terminal)
                    base = pool['cost'] if pool else base_costs.get(rid, dict.fromkeys(COST_FIELDS))
                    extra, extra_origin = extra_cost(row, result, arm, pool) if terminal else (dict.fromkeys(COST_FIELDS), 'pending')
                    if terminal and row.get('declared_historical_extra_cost') is not None:
                        extra = row['declared_historical_extra_cost']
                        extra_origin = 'historical_extra_with_original_events'
                    attributed = add_cost(base, extra) if terminal else dict.fromkeys(COST_FIELDS)
                    fresh, replay = row.get('execution_cost_parts', (dict.fromkeys(COST_FIELDS), dict.fromkeys(COST_FIELDS)))
                    inherited = inherited_remainder(attributed, fresh, replay) if terminal else dict.fromkeys(COST_FIELDS)
                    scores = score_by_task[rid, arm]
                    scored = (terminal and bool(eval_ids[rid]) and set(scores) == eval_ids[rid]
                        and all(v['native_answer_ref'] == row['native_hash'] for v in scores.values()))
                    selected_correct = (digest(row.get('selected_semantic')) == digest(gold)
                        if terminal and gold_known and row.get('native_parse_error') is None else None)
                    expanded = c4_expanded_pool(pool, row.get('c4_supplementary'), row.get('selected_key'),
                        gold, gold_known, terminal and active and arm == 'pool_old_plus_three')
                    r = dict(method=method, arm=arm, request_id=rid, family_ids=sorted(families[rid]),
                        answer_format=item['answer_format'], execution_status='terminal' if terminal else 'pending',
                        actual_output_status=row.get('status'), source=row.get('source'),
                        native_unavailable=terminal and result.get('native_answer') is None,
                        audit_status=audit, activation_attempted=active,
                        pool_stratum=pool['stratum'] if pool else ('non_F' if components.get(rid) not in (None, 'F') else 'pool_pending_or_unknown'),
                        K=pool['K'] if pool else None, actual_F_votes=pool['actual_votes'] if pool else None,
                        invalid_F_votes=pool['invalid_vote_count'] if pool else None,
                        stopped_early=pool['stopped_early'] if pool else None,
                        pool_unknown_reason=pool.get('unknown_reason') if pool else 'no_declared_complete_F_trace',
                        saved_semantic_gold_known=gold_known, pool_contains_gold=covered,
                        selection_pool_identity=('old_F_plus_three_actual_draws' if arm == 'pool_old_plus_three' and active
                            else ('old_F' if pool else 'non_F_or_unknown')),
                        **expanded,
                        selected_correct_by_saved_semantics=selected_correct,
                        saved_native_score_status='scored' if scored else ('awaiting_score' if terminal else 'pending'),
                        saved_native_correct=(all(v['correct'] is True for v in scores.values()) if scored and all(v['correct'] is not None for v in scores.values()) else None),
                        base_cost_once=base if terminal else dict.fromkeys(COST_FIELDS), extra_cost=extra,
                        extra_cost_origin=extra_origin, method_attributed_cost=attributed,
                        new_execution_cost=fresh, exact_replay_attributed_cost=replay, inherited_other_cost=inherited,
                        elapsed_policy='model_seconds unknown unless recorded; callback wall time not substituted')
                    records.append(r)
                    destination.write(json.dumps(r, ensure_ascii=False, allow_nan=False)+'\n')
            summary.extend(summarize(records))
            total_rows += len(records)
    write_json(out/'mechanism_cost_summary.json', summary)
    physical = physical_costs(spec.get('journals', []))
    physical['declared_physical_scope_complete'] = spec.get('physical_scope_complete', False)
    physical['scope_limit'] = spec.get('physical_scope_description', 'Only explicitly supplied journals; not all project history unless separately declared complete.')
    write_json(out/'physical_cost_summary.json', physical)
    receipt = dict(status='offline_prepared_projection', per_input_rows=total_rows,
        no_model_calls=True, no_grader_calls=True, parser_sources=semantics.sources,
        sources=spec, output_sources=provenance,
        interpretation='Candidate coverage uses unchanged native semantic mapping and saved semantic_gold; not a deployable gold selector. Not a new native score. Pending rows stay in planned denominator.',
        limitations=['Family groups can share an input; per-family counts are not additive.',
            'Unknown old usage stays unknown; attributed costs are not global physical sums.',
            'NLI distributions are not converted to ordinary votes or candidate oracle.',
            'A valid saved-F fallback after technical verification failure is not verifier success.',
            'Timing is recorded event attribution, not exclusive GPU latency or energy.'])
    write_json(out/'receipt.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', required=True, help='Explicit JSON paths; see README')
    parser.add_argument('--output', required=True, help='New directory, never overwrites existing analysis')
    args = parser.parse_args()
    receipt = run(json.loads(Path(args.sources).read_text()), args.output)
    print(json.dumps({k: receipt[k] for k in ('status', 'per_input_rows', 'no_model_calls', 'no_grader_calls')}))


if __name__ == '__main__':
    main()
