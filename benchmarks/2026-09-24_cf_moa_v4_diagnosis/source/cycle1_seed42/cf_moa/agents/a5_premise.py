"""Research A5: one premise-focused reconsideration of saved F disagreement.

The old F implementation/results are untouched. Candidate and ordinary-reanswer
control use the same trigger and one-call budget, plus one format-only repair
when the answer key itself is unavailable. Optional reasons never gate a key.
"""
from copy import deepcopy
import json
import re

from jsonschema import ValidationError

from cf_moa.contracts import AgentProposal, digest, reject_metadata
from cf_moa.tools.adapters import native_json, messages_with_instruction
from cf_moa.tools.legacy import r5_module

VARIANT = 'f_disagreement_key_premise_v1'
CONTROL = 'f_disagreement_ordinary_reanswer_v1'
POLICY = dict(seed=42, temperature=0.7, max_tokens=512)


def competition(packet, saved_f):
    """Map saved F outputs to distinct native keys, without scores or vote counts.

    Ordering is the current native key order, not frequency or winning path.
    The source proposal is bound to the complete current input before any use.
    """
    if saved_f.get('input_hash') != packet.input_hash:
        raise ValueError('F source does not belong to the current complete input')
    if saved_f.get('variant') != 'legacy_f_equal_nli_paths_else_full_maj5':
        raise ValueError('Expected the saved adopted F identity')
    if saved_f.get('applicability') == 'unsupported':
        return []
    keys = r5_module().native_keys(packet.native_input)
    trace = saved_f['trace']
    if trace.get('route') == 'full_nli_equal_paths_native_completion':
        decision = trace['decision']
        observed = decision['direct']['per_order'] + decision['reasoned']['per_order']
    elif trace.get('route') == 'full_native_key_maj5_absolute_majority_stop':
        observed = trace['predictions']
    else:
        return []
    return [key for key in keys if key in observed]


def schema(packet):
    return dict(type='object', properties=dict(
        answer_choice=dict(type='string', enum=r5_module().native_keys(packet.native_input)),
        reason=dict(type='string')), required=['answer_choice'], additionalProperties=False)


def request(packet, competitors, *, control=False, repair_raw=None, config=None):
    keys = r5_module().native_keys(packet.native_input)
    if any(key not in keys for key in competitors):
        raise ValueError('Competition contains a foreign native answer key')
    data = dict(current_native_input=packet.native_input,
                retrieved_context=packet.retrieved_context, model_input=packet.model_input)
    if not control:
        data['competing_answers'] = [dict(key=key, meaning=packet.native_input.get('options', {}).get(key, key))
                                     for key in keys if key in competitors]
    reject_metadata(data)
    if control:
        instruction = ('Answer the current complete original question independently. '
                       'Use the supplied text and the current native options. ')
    else:
        instruction = ('Reconsider the current complete original question. The competing '
            'answers below are distinct fallible outputs with no authority or vote ranking. '
            'Identify which exact premise relation decides the current answer: entities, '
            'roles, direction, negation, quantities and time must stay as written. '
            'Do not invent patient facts. You may keep or change the previous choice; '
            'neither agreement nor disagreement is itself evidence. ')
    instruction += ('Return answer_choice FIRST as one exact current native key, then an '
                    'optional short reason. Select from the full native key space, not '
                    'only the competing subset. No long audit or source-offset table.\n' +
                    json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    if repair_raw is not None:
        instruction += ('\nThe prior response did not contain a readable complete native '
                        'answer key. This is the single allowed format repair; return '
                        'only answer_choice in JSON. Prior response:\n' + repair_raw)
    result_schema = schema(packet)
    if repair_raw is not None:
        result_schema['properties'].pop('reason')
    policy = {key: (config or {}).get(key, value) for key, value in POLICY.items()}
    return dict(kind='generate', messages=messages_with_instruction(packet, instruction),
                schema=result_schema, **policy)


def parse_key(raw, keys):
    """A complete answer-first scalar can survive only trailing reason truncation.

    Never guess or close an unfinished answer key. This is a new postprocessing
    contract, not a reinterpretation of earlier failed A5/A1 results.
    """
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        match = re.match(r'^\s*\{\s*"answer_choice"\s*:\s*', raw or '')
        if match:
            try:
                choice, end = json.JSONDecoder().raw_decode(raw[match.end():])
            except ValueError:
                pass
            else:
                remainder = raw[match.end() + end:]
                if choice in keys and re.match(r'^\s*,\s*"reason"\s*:', remainder):
                    return choice, None, ['optional_reason_incomplete_or_invalid']
        return None, None, ['native_answer_unavailable']
    if not isinstance(value, dict) or value.get('answer_choice') not in keys:
        return None, None, ['native_answer_unavailable']
    reason = value.get('reason')
    return value['answer_choice'], reason if isinstance(reason, str) else None, (
        [] if reason is None or isinstance(reason, str) else ['optional_reason_invalid'])


def run_proposal(packet, session, saved_f, *, control=False, config=None):
    checkpoint = session.checkpoint()
    variant = CONTROL if control else VARIANT
    competitors = competition(packet, saved_f)
    if saved_f.get('applicability') == 'unsupported':
        return AgentProposal('A5', variant, packet.input_hash, 'unsupported', None,
            unresolved=['Outside saved F supported formats'], cost=session.cost_since(checkpoint),
            trace=dict(route='unsupported', old_f_identity=saved_f['variant']))
    base = deepcopy(saved_f['native_proposal'])
    try:
        native_json(json.dumps(base, ensure_ascii=False), packet.answer_schema)
    except (ValueError, TypeError, ValidationError) as error:
        return AgentProposal('A5', variant, packet.input_hash, 'partial', None,
            unresolved=['saved_F_native_unavailable: ' + str(error)], cost=session.cost_since(checkpoint),
            trace=dict(route='saved_F_unavailable', old_f_identity=saved_f['variant']))
    if len(competitors) < 2:
        return AgentProposal('A5', variant, packet.input_hash, 'supported', base,
            cost=session.cost_since(checkpoint), trace=dict(route='no_disagreement_reuse_complete_F',
                source_trace_ref=digest(saved_f['trace']), old_f_identity=saved_f['variant'],
                new_premise_inference=False))
    raw = session.invoke(request(packet, competitors, control=control, config=config), stage='A5_premise:reanswer' if control else 'A5_premise:premise')
    keys = r5_module().native_keys(packet.native_input)
    choice, reason, warnings = parse_key(raw, keys)
    attempts = [dict(raw_response=raw, answer_choice=choice, warnings=warnings)]
    if choice is None:
        raw = session.invoke(request(packet, competitors, control=control, repair_raw=raw, config=config), stage='A5_premise:format_repair')
        choice, reason, warnings = parse_key(raw, keys)
        attempts.append(dict(raw_response=raw, answer_choice=choice, warnings=warnings))
    native = None
    if choice is not None:
        native = deepcopy(base)
        native['answer_choice'] = choice
        native['step_by_step_thinking'] = (reason if reason is not None else
            'Program readout of the model-selected native key; optional explanation unavailable.')
        native_json(json.dumps(native, ensure_ascii=False), packet.answer_schema)
    return AgentProposal('A5', variant, packet.input_hash,
        'supported' if native is not None else 'partial', native,
        claims=[dict(claim_id='A5_premise:assessment', kind='general_knowledge',
                     scope='current_original_question', provenance='unverified_model_judgment')],
        requested_changes=[] if native is None else [dict(change_id='A5_premise:key',
            action='native_key_proposal', scope='current_original_question', answer_choice=choice)],
        unresolved=warnings, checks=[dict(type='format_validation', passed=native is not None)],
        cost=session.cost_since(checkpoint), trace=dict(route='ordinary_reanswer' if control else 'key_premise_reconsideration',
            competing_keys=competitors, attempts=attempts, source_trace_ref=digest(saved_f['trace']),
            base_answer_ref=digest(base), old_f_identity=saved_f['variant'],
            retained_auxiliary_fields=[key for key in base if key not in ('answer_choice', 'step_by_step_thinking')],
            auxiliary_policy='retain complete saved F auxiliary values; this operation changes only the answer key',
            optional_explanation_is_not_patient_fact=True, new_premise_inference=True))


def run(packet, session, base_native_answer, saved_proposal, *, control=False, config=None):
    """Small runner interface; unsupported F keeps the separately supplied B.

    This fallback is declared before the experiment. A supported-but-invalid old
    F or a failed new answer remains unavailable, rather than extracting parts.
    """
    proposal = run_proposal(packet, session, saved_proposal, control=control, config=config)
    native = proposal.native_proposal
    if proposal.applicability == 'unsupported':
        native = deepcopy(base_native_answer)
        if native is not None:
            native_json(json.dumps(native, ensure_ascii=False), packet.answer_schema)
    attempts = proposal.trace.get('attempts', [])
    return dict(variant=proposal.variant, native_answer=native, native_valid=native is not None,
        raw=[row['raw_response'] for row in attempts], warnings=proposal.unresolved,
        cost=proposal.cost, trace=proposal.trace, proposal=proposal.to_dict(),
        status='complete' if native is not None else 'unavailable',
        fallback_to_B_outside_F_support=proposal.applicability == 'unsupported')
