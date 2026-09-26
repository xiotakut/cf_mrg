"""One explicit target, one support proposal, one local native adjudication.

No request-ID policy or quality lookup exists in this inference module.
"""
from copy import deepcopy
import json

from cf_moa.agents import a1_delta
from cf_moa.contracts import digest
from cf_moa.tools.adapters import native_json
from cf_moa.tools.schema_compat import OutputSchemaError

VARIANT = 'baseline_targeted_delta_adjudication_v1'


class NativeTruncation(OutputSchemaError):
    failure_type = 'output_truncation'


def target_for_smoke(packet, base):
    """Stable interface exercise, not evidence that this is an effective router."""
    answer = base['answer_choice']
    chosen = answer if isinstance(answer, list) else [answer]
    return next((key for key, value in packet.native_input.get('options', {}).items()
                 if key not in chosen and str(value).strip().casefold().rstrip('.') != 'none of the above'), None)


def final_request(packet, base, target, proposal=None, *, control=False, draft=None):
    cfg = a1_delta.config()['generation']
    data = dict(current_input=packet.visible(), base_native_answer=base, target=target)
    candidates, library = a1_delta.resources(packet)
    data.update(candidates=candidates, shared_resources=library)
    if proposal is not None:
        data['support_proposal'] = dict(audit=proposal.trace['audit'], claims=proposal.claims,
                                       requested_changes=proposal.requested_changes)
    if draft is not None:
        data['same_agent_draft'] = draft
    instruction = (
        'Answer the complete original question using its full native JSON schema. '
        'Keep all native auxiliary fields. B is a fallible baseline, never gold. '
        'Only revise the specified candidate when the complete current evidence and '
        'question scope justify it. Model assertions and citations are not proof. '
        'Check negation, units, time, exceptions and independent support paths. '
        'A removed support path cannot erase a separate valid path. '
        'For multi-select, add the target only if supported; retain other selections '
        'except an explicit None-of-the-above choice that becomes incompatible. '
        'For single-select, either keep B or select the challenged target. '
        'Do not alter unrelated auxiliary corrections; preserve B auxiliary fields '
        'other than the answer and its explanation. You may reject the proposal. '
        'Give a concise complete explanation; no per-claim audit table is requested.'
    )
    if control:
        instruction = (
            'Answer the complete original question in its full native JSON schema, '
            'including every auxiliary field. Independently reconsider the specified '
            'target with the same current data and available shared resources. '
            'The baseline and draft are fallible; change or retain the answer according '
            'to evidence. Return a concise complete native answer, not an audit table.'
        )
    return dict(kind='generate', messages=[dict(role='system', content=instruction),
        dict(role='user', content=json.dumps(data, ensure_ascii=False, separators=(',', ':')))],
        schema=packet.answer_schema, seed=cfg['seed'], temperature=cfg['temperature'],
        max_tokens=cfg['answer_max_tokens'])


def local_change(packet, base, final, target):
    old, new = base['answer_choice'], final['answer_choice']
    for key in set(base) | set(final):
        if key not in ('answer_choice', 'step_by_step_thinking') and (
                key not in base or key not in final or final[key] != base[key]):
            return False, 'unrelated_auxiliary_change'
    if new == old:
        return True, 'retained_baseline_answer'
    if isinstance(old, list):
        none_keys = {k for k, v in packet.native_input.get('options', {}).items()
                     if str(v).strip().casefold().rstrip('.') == 'none of the above'}
        expected = (set(old) | {target}) - (none_keys if target not in none_keys else set())
        if target in none_keys:
            return False, 'absence_of_all_support_is_not_an_add_support_path'
        ok = isinstance(new, list) and set(new) == expected
    else:
        ok = new == target
    return ok, 'local_target_change' if ok else 'nonlocal_answer_change'


def run(packet, session, base, target, arm='delta_adjudication'):
    before = session.checkpoint()
    native_json(json.dumps(base, ensure_ascii=False), packet.answer_schema)
    if arm not in a1_delta.config()['arms']:
        raise ValueError('Unknown preregistered incremental arm')
    result = dict(variant=VARIANT, arm=arm, input_hash=packet.input_hash,
        base_answer_ref=digest(base), challenged_target=target, proposal=None,
        native_answer=deepcopy(base), audit_status='not_requested',
        decision='baseline_reuse', failure_type=None, native_valid=True)
    if arm == 'baseline' or target is None:
        result['cost'] = session.cost_since(before)
        return result
    a1_delta.prepare(packet, base, target)
    if arm == 'delta_adjudication':
        proposal = a1_delta.run(packet, session, base, target)
        result.update(proposal=proposal.to_dict(), audit_status=proposal.trace['audit_status'])
        if not proposal.trace['audit_available'] or not proposal.requested_changes:
            result.update(decision='audit_unavailable_reuse_B' if not proposal.trace['audit_available']
                          else 'no_qualified_new_support_reuse_B', cost=session.cost_since(before))
            return result
        request = final_request(packet, base, target, proposal)
    else:
        # Same 1024-token optional preparation and 2048-token native answer caps
        # as the main arm. Actual tokens/time are measured, not assumed equal.
        control_target = target if arm == 'targeted_reanswer' else None
        first = final_request(packet, base, control_target, control=True)
        first['messages'][0]['content'] = (
            'Prepare one concise draft for answering the complete current question. '
            'Reconsider the specified target if present; otherwise reconsider the question. '
            'Use the complete current data and legal shared resources. The baseline is '
            'fallible. Return a short note in JSON field draft; no final native answer yet.')
        first['schema'] = a1_delta.obj(dict(draft={'type': 'string'}))
        first['max_tokens'] = a1_delta.config()['generation']['diagnostic_max_tokens']
        raw = session.invoke(first, stage=arm + ':draft')
        try:
            if session.calls[-1].get('event', {}).get('finish_reason') == 'length':
                raise ValueError('output_truncation: optional draft unavailable')
            draft = native_json(raw, first['schema'])
        except (ValueError, TypeError, a1_delta.ValidationError):
            result.update(audit_status='audit_unavailable', decision='audit_unavailable_reuse_B',
                          raw_draft=raw, cost=session.cost_since(before))
            return result
        request = final_request(packet, base, control_target, control=True, draft=draft)
    raw = session.invoke(request, stage=arm + ':native_answer')
    if session.calls[-1].get('event', {}).get('finish_reason') == 'length':
        raise NativeTruncation('Final native answer hit its output limit; not scored')
    try:
        final = native_json(raw, packet.answer_schema)
    except Exception as error:
        raise OutputSchemaError('Final native answer invalid: ' + str(error)) from error
    result['raw_final_response'] = raw
    if arm == 'delta_adjudication':
        accepted, reason = local_change(packet, base, final, target)
        result.update(decision=reason, proposed_native_answer=final)
        if accepted:
            result['native_answer'] = final
    else:
        result.update(native_answer=final, decision='control_reanswer')
    result['cost'] = session.cost_since(before)
    return result
