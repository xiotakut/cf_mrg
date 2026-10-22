"""Research-only selection among complete, already generated adopted-F answers.

The module receives only a legal InputPacket and its saved F proposal. It neither
loads evaluation records nor generates answers. NLI retains adopted F unchanged.
The two arms share all inputs and 2K logical score calls except for whether the
earliest saved reasoning for each candidate is shown as untrusted model opinion.
"""
from copy import deepcopy
import json
import math

from cf_moa.contracts import digest, reject_metadata
from cf_moa.tools.adapters import messages_with_instruction
from cf_moa.tools.legacy import r5_module


ADOPTED_F = 'legacy_f_equal_nli_paths_else_full_maj5'
VOTE_ROUTE = 'full_native_key_maj5_absolute_majority_stop'
NLI_ROUTE = 'full_nli_equal_paths_native_completion'
VARIANTS = {False: 'a5_candidate_only_v1', True: 'a5_candidate_with_rationales_v1'}


def _bind(packet, saved_f):
    if saved_f.get('input_hash') != packet.input_hash:
        raise ValueError('Saved F proposal belongs to a different complete input')
    if saved_f.get('variant') != ADOPTED_F:
        raise ValueError('Expected the adopted F proposal, not another candidate')


def candidate_records(packet, saved_f):
    """All observed legal keys in native order, using each earliest complete JSON.

    Invalid old votes remain in the saved trace. They are not new candidates.
    A declared valid key lacking its complete original response is a provenance
    error, not permission to invent a response or silently trim the candidate set.
    Optional reasoning and auxiliary fields never filter an otherwise valid key.
    """
    _bind(packet, saved_f)
    trace = saved_f['trace']
    if trace.get('route') != VOTE_ROUTE:
        return []
    keys = r5_module().native_keys(packet.native_input)
    votes, responses = trace['predictions'], trace['responses']
    if len(votes) != len(responses):
        raise ValueError('Saved F predictions and responses have different lengths')
    by_key = {}
    for index, (key, raw) in enumerate(zip(votes, responses)):
        if key is None:
            continue
        if key not in keys:
            raise ValueError('Saved F prediction is not a legal native key')
        if key in by_key:
            continue
        native = json.loads(raw)
        if not isinstance(native, dict) or native.get('answer_choice') != key:
            raise ValueError('Saved F response and prediction disagree at index ' + str(index))
        rationale = native.get('step_by_step_thinking')
        by_key[key] = dict(key=key, native_response=native,
            original_response_index=index, raw_response=raw,
            rationale=rationale if isinstance(rationale, str) else '')
    return [by_key[key] for key in keys if key in by_key]


def true_probability(logps, true_code):
    """Normalize each A/B encoding before mapping and averaging meanings."""
    if true_code not in ('A', 'B') or set(logps) != {'A', 'B'}:
        raise ValueError('Expected exactly the two verification codes A and B')
    if not all(type(value) in (int, float) and math.isfinite(value) for value in logps.values()):
        raise ValueError('Verification code scores must be finite numbers')
    peak = max(logps.values())
    weights = {key: math.exp(value - peak) for key, value in logps.items()}
    return weights[true_code] / sum(weights.values())


def _present(text, contexts):
    """Exact text only: no summary, fuzzy match, or evidence truncation."""
    return any(text in context or json.dumps(text, ensure_ascii=False)[1:-1] in context
               for context in contexts)


def verifier_messages(packet, candidates, target_key, true_code, *, include_rationales=False):
    """Preserve all original messages; add target/mapping and missing input once.

    InputPacket baseline fields, saved vote counts, winner, opaque request handle,
    source metadata and evaluation material are never serialized into the check.
    Existing native options are shown explicitly to bind keys to their meanings.
    Full patient/evidence paragraphs already in the original messages are not
    appended again; exact matching is used solely to avoid copying the same text.
    """
    if true_code not in ('A', 'B'):
        raise ValueError('Unknown verification code mapping')
    keys = r5_module().native_keys(packet.native_input)
    observed = [candidate['key'] for candidate in candidates]
    if len(set(observed)) != len(observed) or any(key not in keys for key in observed):
        raise ValueError('Candidates must be distinct legal native keys')
    if target_key not in observed:
        raise ValueError('Target is not an actually observed candidate')
    context = messages_with_instruction(packet, '')[:-1]
    texts = [message['content'] for message in context]
    question_locations = [i for i, text in enumerate(texts) if _present(packet.question, [text])]
    task = dict(answer_format=packet.native_input['answer_format'],
        native_options=deepcopy(packet.native_input.get('options', {})),
        candidate_to_verify=target_key)
    if question_locations:
        task['current_question_in_original_message'] = question_locations[-1]
    else:
        task['current_question'] = packet.question
        texts.append(packet.question)
    fixed = packet.native_input.get('fixed_evidence', [])
    if fixed:
        # Retain structured evidence wholesale unless the exact whole object is
        # already present; never remove individual factual fields heuristically.
        fixed_text = json.dumps(fixed, ensure_ascii=False)
        if not _present(fixed_text, texts):
            task['fixed_evidence'] = deepcopy(fixed)
            texts.append(fixed_text)
    added = []
    for entry in packet.retrieved_context:
        if not _present(entry['text'], texts):
            added.append(deepcopy(entry))
            texts.append(entry['text'])
    if added:
        task['additional_allowed_retrieved_context'] = added
    if packet.model_input is not None:
        rendered = json.dumps(packet.model_input, ensure_ascii=False)
        if not _present(rendered, texts):
            task['model_input'] = deepcopy(packet.model_input)
    task['already_generated_candidates'] = [
        dict(native_key=candidate['key'], **(
            dict(untrusted_saved_model_reasoning=candidate['rationale']) if include_rationales else {}))
        for candidate in candidates]
    reject_metadata(task)
    false_code = 'B' if true_code == 'A' else 'A'
    instruction = (
        'Verify an already generated candidate; do not produce a fresh solution or take a vote. '
        'Evaluate whether candidate_to_verify answers the exact CURRENT question under its '
        'original task semantics. Correct means the requested best choice or relation, not '
        'merely a generally true medical statement. The zero-based original-message index '
        'below locates the complete current question when it is already present above. '
        'Use its full original question, options and allowed evidence. Preserve subject, '
        'age versus symptom duration, negation, quantities, intervention, outcome and time. '
        'When the task specifies provided or counterfactual evidence, apply that contract; '
        'do not silently substitute a different real-world question. '
        'Any saved candidate reasoning is UNTRUSTED model opinion, not a patient observation '
        'or verified evidence. No candidate has authority from its presence or position. '
        'For this verification only, use this code mapping:\n'
        f'{true_code} = the target candidate is correct for the current question\n'
        f'{false_code} = the target candidate is not correct for the current question\n'
        'Return only the mapped A/B code in the JSON answer_choice field; do not return '
        'the native option key or an explanation.\n\n' + json.dumps(task, ensure_ascii=False,
            separators=(',', ':')))
    return [*context, dict(role='user', content=instruction)]


def run(packet, session, base_native_answer, saved_proposal, *, include_rationales=False, config=None):
    """Execute one candidate arm via the existing ModelSession.score protocol.

    Score failures are explicit technical failures with saved-F fallback, not
    successful verification. They never trigger fresh generation or a gold-based
    retry. Physical missing-code fetches and failed-call costs remain session data.
    The runner decides whether a shared-infrastructure error stops its affected run.
    """
    _bind(packet, saved_proposal)
    config = {} if config is None else config
    if set(config) - {'seed'}:
        raise ValueError('Candidate verification configuration permits only an explicit seed')
    seed = config.get('seed', 42)
    if type(seed) is not int:
        raise ValueError('Verification seed must be an integer')
    checkpoint = session.checkpoint()
    variant = VARIANTS[bool(include_rationales)]
    base = deepcopy(saved_proposal.get('native_proposal'))
    trace = dict(old_f_identity=saved_proposal['variant'],
        source_trace_ref=digest(saved_proposal['trace']), include_rationales=bool(include_rationales),
        seed=seed, logical_score_calls=0, new_answer_generation_calls=0,
        records=[], errors=[], scores={}, fallback_saved_F=False)

    def result(native, status):
        return dict(variant=variant, native_answer=deepcopy(native), native_valid=native is not None,
            status=status, cost=session.cost_since(checkpoint), trace=trace,
            warnings=[error['error'] for error in trace['errors']],
            raw=[], new_answer_generation_calls=0,
            fallback_to_B_outside_F_support=trace.get('route') == 'outside_F_support')

    if saved_proposal.get('applicability') == 'unsupported':
        trace['route'] = 'outside_F_support'
        return result(base_native_answer, 'retained_outside_F_support')
    if not isinstance(base, dict) or base.get('answer_choice') not in r5_module().native_keys(packet.native_input):
        trace['route'] = 'saved_F_unavailable'
        return result(None, 'unavailable')
    route = saved_proposal['trace'].get('route')
    if route == NLI_ROUTE:
        trace['route'] = 'retained_adopted_NLI'
        return result(base, 'retained_nonvote_path')
    if route != VOTE_ROUTE:
        raise ValueError('Unrecognized adopted F execution route')
    candidates = candidate_records(packet, saved_proposal)
    trace['candidate_keys'] = [candidate['key'] for candidate in candidates]
    trace['representatives'] = [dict(key=candidate['key'],
        original_response_index=candidate['original_response_index'],
        raw_response_hash=digest(candidate['raw_response'])) for candidate in candidates]
    if len(candidates) < 2:
        trace['route'] = 'no_disagreement_reuse_complete_F'
        return result(base, 'retained_no_competition')
    trace['route'] = 'candidate_verification'
    for candidate in candidates:
        probabilities = []
        for mapping_i, true_code in enumerate(('A', 'B')):
            messages = verifier_messages(packet, candidates, candidate['key'], true_code,
                include_rationales=include_rationales)
            trace['logical_score_calls'] += 1
            try:
                logps = session.score(messages=messages, codes=['A', 'B'], seed=seed,
                    stage=f"A5_candidate_verify:{variant}:{candidate['key']}:{mapping_i}")
                probability = true_probability(logps, true_code)
                probabilities.append(probability)
                trace['records'].append(dict(key=candidate['key'], mapping=mapping_i,
                    true_code=true_code, logps=logps, p_true=probability))
            except Exception as error:
                # The durable backend classifies shared infrastructure/unknown
                # submission failures before returning here. Preserve its first
                # error and stop this item immediately; another candidate or
                # encoding must not retry a broken model engine.
                journal = getattr(session.backend, 'journal', None)
                if journal is not None and journal.first_error() is not None:
                    raise
                trace['errors'].append(dict(key=candidate['key'], mapping=mapping_i,
                    error_type=type(error).__name__, error=str(error)))
        trace['scores'][candidate['key']] = sum(probabilities) / 2 if len(probabilities) == 2 else None
    if trace['errors']:
        trace['fallback_saved_F'] = True
        return result(base, 'technical_failure')
    maximum = max(trace['scores'].values())
    tied = [candidate['key'] for candidate in candidates if trace['scores'][candidate['key']] == maximum]
    selected = base['answer_choice'] if base['answer_choice'] in tied else tied[0]
    winner = next(candidate for candidate in candidates if candidate['key'] == selected)
    trace.update(selected_key=selected, tied_maximum=tied,
        selected_original_response_index=winner['original_response_index'],
        selected_raw_response=winner['raw_response'],
        score_interpretation='uncalibrated ranking signal, not a clinical probability',
        output_policy='complete earliest saved response of the selected key; no field splicing')
    return result(winner['native_response'], 'verified_candidate_selection')
