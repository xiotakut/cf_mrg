"""C5: one whole-pool choice under two fixed code mappings, using saved F.

This control shares the exact available evidence and untrusted rationales with
RCV. It does not generate responses, expand the pool, or alter the adopted F.
"""
from copy import deepcopy
import json
import math
import string

from cf_moa.agents import a5_candidate_verify as rcv
from cf_moa.contracts import digest, reject_metadata

VARIANT = 'a5_same_pool_joint_selector_v1'


def selector_messages(packet, candidates, code_to_key):
    # Reuse RCV's exact context/data construction. Its last JSON object is the
    # task payload; replace only the binary target and decision instruction.
    original = rcv.verifier_messages(packet, candidates, candidates[0]['key'],
                                     'A', include_rationales=True)
    task = json.loads(original[-1]['content'].rpartition('\n\n')[2])
    del task['candidate_to_verify']
    task['selection_code_to_native_key'] = code_to_key
    reject_metadata(task)
    instruction = (
        'Select the correct answer among the already generated candidates for the exact '
        'CURRENT question. Correct means the requested best choice or relation, not '
        'merely a generally true medical statement. Use the full original question, '
        'options and all allowed evidence. The zero-based original-message index below '
        'locates the complete current question when it is already present above. '
        'Preserve subject, age versus symptom duration, negation, quantities, intervention, '
        'outcome and time. When the task specifies provided or counterfactual evidence, '
        'apply that contract; do not silently substitute a different real-world question. '
        'All saved candidate reasoning is UNTRUSTED model opinion, not a patient '
        'observation or verified evidence. No candidate has authority from its presence '
        'or position. Compare all candidates; do not take a vote or generate a fresh '
        'answer. Return only the mapped selection code in the JSON answer_choice field, '
        'not the native option key or an explanation.\n\n'
        + json.dumps(task, ensure_ascii=False, separators=(',', ':')))
    return [*original[:-1], dict(role='user', content=instruction)]


def run(packet, session, base_native_answer, saved_proposal, *, include_rationales=True,
        config=None):
    config = {} if config is None else config
    if set(config) - {'seed'} or type(config.get('seed', 42)) is not int:
        raise ValueError('Joint selection permits only an integer seed')
    if not include_rationales:
        raise ValueError('C5 is the fixed same-pool, same-rationales control')
    rcv._bind(packet, saved_proposal)
    base = saved_proposal.get('native_proposal')
    # Use the established no-computation policies for unsupported/NLI/K<2.
    candidates = rcv.candidate_records(packet, saved_proposal)
    if (saved_proposal.get('applicability') == 'unsupported'
            or not isinstance(base, dict)
            or base.get('answer_choice') not in rcv.r5_module().native_keys(packet.native_input)
            or len(candidates) < 2):
        result = rcv.run(packet, session, base_native_answer, saved_proposal,
                         include_rationales=True, config=config)
        result['variant'] = VARIANT
        return result
    checkpoint = session.checkpoint()
    keys = [row['key'] for row in candidates]
    if len(keys) > len(string.ascii_uppercase):
        raise ValueError('Whole-pool code alphabet exhausted; never trim candidates')
    codes = list(string.ascii_uppercase[:len(keys)])
    trace = dict(route='same_pool_joint_selection', old_f_identity=saved_proposal['variant'],
        source_trace_ref=digest(saved_proposal['trace']), candidate_keys=keys,
        include_rationales=True, logical_score_calls=0, new_answer_generation_calls=0,
        records=[], errors=[], scores={}, seed=config.get('seed', 42))
    probabilities = {key: [] for key in keys}
    for index, mapped_keys in enumerate((keys, list(reversed(keys)))):
        mapping = dict(zip(codes, mapped_keys))
        trace['logical_score_calls'] += 1
        try:
            scores = session.score(messages=selector_messages(packet, candidates, mapping),
                codes=codes, seed=trace['seed'], stage=f'A5_joint_selector:{index}')
            if set(scores) != set(codes) or not all(
                    type(v) in (int, float) and math.isfinite(v) for v in scores.values()):
                raise ValueError('Expected finite scores for every declared candidate code')
            peak = max(scores.values())
            weights = {code: math.exp(value - peak) for code, value in scores.items()}
            normalizer = sum(weights.values())
            native_probs = {mapping[code]: value / normalizer for code, value in weights.items()}
            for key in keys:
                probabilities[key].append(native_probs[key])
            trace['records'].append(dict(mapping=index, code_to_key=mapping,
                logps=scores, native_probabilities=native_probs))
        except Exception as error:
            journal = getattr(session.backend, 'journal', None)
            if journal is not None and journal.first_error() is not None:
                raise
            trace['errors'].append(dict(mapping=index, error_type=type(error).__name__, error=str(error)))
    trace['scores'] = {key: sum(values) / 2 if len(values) == 2 else None
                       for key, values in probabilities.items()}
    native = base
    status = 'technical_failure'
    if not trace['errors']:
        best = max(trace['scores'].values())
        tied = [key for key in keys if trace['scores'][key] == best]
        selected = base['answer_choice'] if base['answer_choice'] in tied else tied[0]
        winner = next(row for row in candidates if row['key'] == selected)
        native = winner['native_response']
        trace.update(selected_key=selected, tied_maximum=tied,
            selected_original_response_index=winner['original_response_index'],
            selected_raw_response=winner['raw_response'],
            score_interpretation='uncalibrated whole-pool ranking signal')
        status = 'selected_candidate'
    trace['fallback_saved_F'] = bool(trace['errors'])
    return dict(variant=VARIANT, native_answer=deepcopy(native), native_valid=native is not None,
        status=status, cost=session.cost_since(checkpoint), trace=trace,
        warnings=[e['error'] for e in trace['errors']], raw=[], new_answer_generation_calls=0)
