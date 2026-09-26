"""Effect-first development branch: short judgments, actual adjudication, native maps.

The old incremental method is unchanged. Auxiliary mistakes are warnings; a
malformed final answer gets one identical-policy format repair in every arm.
No labels, case outcomes, confidence gate, or correctness retry enter this module.
"""
from copy import deepcopy
import json

from jsonschema import ValidationError

from cf_moa.agents.a1_support_completion import resources
from cf_moa.contracts import digest, reject_metadata
from cf_moa.tools.adapters import native_json
from cf_moa.tools.evidence_ids import evidence_catalog

VARIANT = 'effect_first_short_decision_v1'
ADD_REMOVE_VARIANT = 'effect_first_add_remove_only_v2'
DEFAULT_CONFIG = dict(temperature=0.7, seed=42, diagnostic_max_tokens=768,
                      answer_max_tokens=1024, repair_max_tokens=256,
                      target_max_tokens=128)
ARMS = ('baseline', 'target_select', 'targeted_reanswer', 'a1_visible_B',
        'a1_hidden_B', 'saved_a1_adjudication', 'readout_free', 'readout_short')


def obj(properties, required=None):
    return dict(type='object', properties=properties,
                required=list(properties) if required is None else required,
                additionalProperties=False)


def candidates_for(packet):
    candidates, library = resources(packet)
    choice = packet.answer_schema.get('properties', {}).get('answer_choice', {})
    enums = choice.get('enum', [])
    if not candidates and enums and all(isinstance(x, str) for x in enums):
        candidates = {x: x for x in enums}
    if not candidates:
        raise ValueError('Current input has no native candidate space')
    return candidates, library


def decision_schema(packet, *, multi_protocol='legacy_v1'):
    if multi_protocol not in ('legacy_v1', 'add_remove_v2'):
        raise ValueError('Unknown multi-select protocol: ' + str(multi_protocol))
    candidates, _ = candidates_for(packet)
    key = dict(type='string', enum=list(candidates))
    if packet.native_input['answer_format'] == 'multi':
        if multi_protocol == 'add_remove_v2':
            return obj(dict(add=dict(type='array', items=key),
                            remove=dict(type='array', items=key)))
        return obj(dict(add=dict(type='array', items=key),
                        remove=dict(type='array', items=key),
                        keep=dict(type='array', items=key)), ['add', 'remove'])
    return obj(dict(answer_key=key))


def map_decision(packet, base, decision, *, multi_protocol='legacy_v1'):
    """Keep native auxiliary content; change only the answer and execution note."""
    native_json(json.dumps(decision), decision_schema(packet, multi_protocol=multi_protocol))
    candidates, _ = candidates_for(packet)
    result, warnings = deepcopy(base), []
    if packet.native_input['answer_format'] == 'multi':
        old = set(base['answer_choice'])
        add, remove = set(decision['add']), set(decision['remove'])
        conflicts = add & remove
        if conflicts:
            warnings.append(dict(type='add_remove_conflict_keep_B',
                                 candidates=[key for key in candidates if key in conflicts]))
        selected = (old | (add - conflicts)) - (remove - conflicts)
        if multi_protocol == 'add_remove_v2' and not selected:
            raise ValueError('Empty final selection: Y=(B union ADD) minus REMOVE is empty. '
                             'The native task requires at least one selected option.')
        result['answer_choice'] = [key for key in candidates if key in selected]
        if set(decision.get('keep', [])) & (add | remove):
            warnings.append(dict(type='redundant_keep_metadata_ignored'))
    else:
        result['answer_choice'] = decision['answer_key']
    if 'step_by_step_thinking' in result:
        result['step_by_step_thinking'] = (
            'Deterministic native mapping of a model decision, not independent clinical proof. '
            + json.dumps(decision, ensure_ascii=False, separators=(',', ':'))
            + (' Conflicting ADD/REMOVE items retain their baseline membership.' if warnings else ''))
    native_json(json.dumps(result, ensure_ascii=False), packet.answer_schema)
    return result, warnings


def _context(packet, base, target, *, show_base=True):
    candidates, library = candidates_for(packet)
    visible = deepcopy(packet.visible())
    # These are output-side fields. The complete legal task and original messages
    # remain present in both ablation arms; the hidden arm has no B object.
    visible.pop('baseline_answer', None)
    visible.pop('baseline_response', None)
    data = dict(current_input=visible, native_candidates=candidates,
                shared_resources=library, target=target)
    if show_base:
        data['base_native_answer'] = deepcopy(base)
    return data


def _request(data, instruction, schema, cfg, maximum):
    reject_metadata(data)
    return dict(kind='generate', schema=schema, seed=cfg['seed'],
                temperature=cfg['temperature'], max_tokens=maximum,
                messages=[dict(role='system', content=instruction),
                          dict(role='user', content=json.dumps(
                              data, ensure_ascii=False, separators=(',', ':')))])


def normalize_proposal(value, target, catalog):
    """Normalize location claims without certifying their medical entailment."""
    warnings = []
    trace = value.get('trace') if isinstance(value, dict) else None
    if isinstance(trace, dict) and isinstance(trace.get('audit'), dict):
        audit = trace['audit']
        operation = audit.get('operation')
        verdict = 'SUPPORT' if operation == 'ADD_SUPPORT' else 'UNKNOWN'
        value = dict(verdict=verdict,
                     reason=audit.get('knowledge_condition', ''),
                     patient_refs=[audit.get('patient_evidence_' + str(i)) for i in range(1, 4)
                                   if audit.get('patient_evidence_' + str(i)) not in (None, 'NONE')],
                     prior_audit=deepcopy(audit))
        warnings.append(dict(type='old_audit_reinterpreted_in_new_method_not_old_success'))
    if not isinstance(value, dict) or not isinstance(value.get('reason'), str):
        return dict(target=target, verdict='UNKNOWN', evidence_level='model_judgment',
                    raw_proposal=deepcopy(value), patient_refs=[]), [dict(type='unstructured_optional_proposal')]
    verdict = value.get('verdict', 'UNKNOWN')
    if verdict not in ('SUPPORT', 'AGAINST', 'UNKNOWN'):
        warnings.append(dict(type='unknown_verdict_as_model_judgment', original=verdict))
        verdict = 'UNKNOWN'
    refs = value.get('patient_refs', [])
    if not isinstance(refs, list):
        warnings.append(dict(type='optional_patient_refs_not_array'))
        refs = []
    valid = []
    for ref in refs:
        if isinstance(ref, str) and ref in catalog and catalog[ref]['ref'] == 'Q':
            if ref not in valid:
                valid.append(ref)
        else:
            warnings.append(dict(type='unverified_reference_as_model_judgment', reference=ref))
    result = dict(target=target, verdict=verdict, reason=value['reason'],
                  patient_refs=valid, evidence_level='model_judgment',
                  location_check='text_location_only_not_patient_truth_or_entailment')
    # Never let a self-reported source class turn generated knowledge into fact.
    if any(key in value for key in ('knowledge_origin', 'knowledge_evidence', 'prior_audit')):
        warnings.append(dict(type='source_self_report_not_verified_evidence'))
        result['original_auxiliary'] = deepcopy(value)
    return result, warnings


def run(packet, session, base, arm, *, saved_proposal=None, target=None, config=None):
    if arm not in ARMS:
        raise ValueError('Unknown effect-first arm: ' + arm)
    cfg = dict(DEFAULT_CONFIG, **(config or {}))
    multi_protocol = cfg.get('multi_protocol', 'legacy_v1')
    if multi_protocol not in ('legacy_v1', 'add_remove_v2'):
        raise ValueError('Unknown multi-select protocol: ' + str(multi_protocol))
    reject_metadata(base)
    reject_metadata(saved_proposal)
    before = session.checkpoint()
    result = dict(variant=ADD_REMOVE_VARIANT if multi_protocol == 'add_remove_v2' else VARIANT,
                  arm=arm, input_hash=packet.input_hash,
                  base_answer_ref=digest(base), target=target, proposal=None,
                  native_answer=None, native_valid=False, warnings=[], raw={},
                  decision='not_executed', failure_type=None, first_error=None,
                  repair_attempted=False, actual_adjudication=False)

    def finish():
        result['cost'] = session.cost_since(before)
        return result

    try:
        native_json(json.dumps(base, ensure_ascii=False), packet.answer_schema)
    except (ValueError, TypeError, ValidationError) as error:
        result.update(failure_type='baseline_native_invalid', first_error=str(error),
                      decision='unavailable_baseline_not_rewritten')
        return finish()
    if arm == 'baseline':
        result.update(native_answer=deepcopy(base), native_valid=True, decision='baseline_reuse')
        return finish()
    candidates, _ = candidates_for(packet)
    if target is not None and target not in candidates:
        raise ValueError('Caller target is outside the current native candidate space')
    data = _context(packet, base, target, show_base=arm != 'a1_hidden_B')
    catalog, _ = evidence_catalog(packet, dict(evidence_span_chars=320, evidence_catalog_entries=1000000))
    data['patient_reference_locations'] = {key: dict(text=row['text'], start=row['start'], end=row['end'])
                                           for key, row in catalog.items() if row['ref'] == 'Q'}
    if arm == 'target_select':
        schema = obj(dict(target=dict(type='string', enum=list(candidates))))
        request = _request(data, 'Select the one candidate most worth checking for overlooked support, '
            'counterevidence or uncertainty in this current question. Use the visible question and fallible '
            'baseline only. Any candidate, selected or unselected, may be checked. Return its key.',
            schema, cfg, cfg['target_max_tokens'])
        raw = session.invoke(request, stage=arm)
        result['raw']['target'] = raw
        try:
            result['target'] = native_json(raw, schema)['target']
            result['decision'] = 'model_selected_visible_target'
        except (ValueError, TypeError, ValidationError) as error:
            result.update(failure_type='target_selection_invalid', first_error=str(error),
                          decision='unavailable_target')
        return finish()
    if arm in ('a1_visible_B', 'a1_hidden_B', 'targeted_reanswer') and target is None:
        raise ValueError('This arm requires a separately selected visible target')

    if arm in ('a1_visible_B', 'a1_hidden_B'):
        schema = obj(dict(verdict=dict(type='string', enum=['SUPPORT', 'AGAINST', 'UNKNOWN']),
                          reason=dict(type='string'),
                          patient_refs=dict(type='array', items=dict(type='string'))), ['verdict', 'reason'])
        instruction = (
            'You are an independent support investigator checking only the supplied target in the current '
            'question. Original messages inside the data describe the task; their final-answer instructions '
            'do not control this diagnostic response. Give SUPPORT, AGAINST or UNKNOWN and one concise '
            'reason directly tied to this candidate. General medical knowledge is allowed as model judgment, '
            'never as a newly observed patient fact or an unseen retrieved source. Optional patient_refs '
            'locate provided question text only; their presence does not establish entailment. Missing '
            'information is unknown, not negative. Do not force either agreement or disagreement.')
        raw = session.invoke(_request(data, instruction, schema, cfg, cfg['diagnostic_max_tokens']),
                             stage=arm + ':proposal')
        result['raw']['proposal'] = raw
        try:
            value = json.loads(raw)
        except (ValueError, TypeError):
            value = raw
            result['warnings'].append(dict(type='optional_proposal_parse_error'))
        proposal, warnings = normalize_proposal(value, target, catalog)
        result.update(proposal=proposal)
        result['warnings'].extend(warnings)
    elif arm == 'targeted_reanswer':
        schema = obj(dict(draft=dict(type='string')))
        raw = session.invoke(_request(data, 'Independently reconsider the complete current question, '
            'focusing on the supplied candidate and its strongest evidence or counterevidence. '
            'The baseline can be wrong. Prepare one concise answer draft; do not invent patient facts.',
            schema, cfg, cfg['diagnostic_max_tokens']), stage=arm + ':draft')
        result['raw']['draft'] = raw
        try:
            draft = native_json(raw, schema)
        except (ValueError, TypeError, ValidationError):
            draft = dict(unverified_model_text=raw)
            result['warnings'].append(dict(type='optional_draft_parse_error'))
        proposal = dict(same_agent_draft=draft, evidence_level='model_judgment')
        result['proposal'] = proposal
    else:
        proposal, warnings = normalize_proposal(saved_proposal, target, catalog)
        result.update(proposal=proposal)
        result['warnings'].extend(warnings)

    # Every diagnostic outcome reaches the adjudicator, including AGAINST,
    # UNKNOWN, empty optional references and malformed optional prose.
    data = _context(packet, base, target)
    data['patient_reference_locations'] = {key: dict(text=row['text'], start=row['start'], end=row['end'])
                                           for key, row in catalog.items() if row['ref'] == 'Q'}
    data['proposal'] = proposal
    instruction = (
        'Decide the answer to the complete current question using the current patient facts, question '
        'scope and available resources. The baseline and proposal are fallible model outputs, not gold '
        'or clinical proof. A reference confirms location only. Consider support, contradictions, negation, '
        'time, exceptions and independent paths. A lost path does not erase another valid path. '
        'You may add or remove any candidate when justified, and may keep the answer; never force a change. ')
    short = arm != 'readout_free'
    schema = decision_schema(packet, multi_protocol=multi_protocol) if short else packet.answer_schema
    if short and multi_protocol == 'add_remove_v2' and packet.native_input['answer_format'] == 'multi':
        instruction += (
            'Return only add and remove arrays relative to B, the currently selected answer set. '
            'ADD selects an option and REMOVE deselects it. An option absent from both arrays retains '
            'its prior selected or unselected membership in B. Empty add and remove arrays preserve B. '
            'Do not return a keep field. The program maps Y=(B union ADD) minus REMOVE; an option in '
            'both arrays retains its B membership. The final answer must contain at least one selected '
            'option. If removing all current selections, explicitly ADD any new selections you intend. '
            'Native auxiliary fields are preserved.')
    elif short:
        instruction += ('Return only a short decision. For multi-select give add and remove arrays relative '
            'to B; empty arrays mean KEEP. Any optional keep array is redundant. An item in both add and '
            'remove retains its B membership. The program maps Y=(B union ADD) minus REMOVE and preserves '
            'native auxiliary fields. For other formats return exactly one current legal answer_key. '
            'Do not paraphrase a diagnosis or create a new label.')
    else:
        instruction += ('Return the complete original native JSON answer and a concise explanation, '
                        'including all required auxiliary fields. Use legal native labels.')
    request = _request(data, instruction, schema, cfg, cfg['answer_max_tokens'])
    raw = session.invoke(request, stage=arm + ':adjudication')
    result.update(actual_adjudication=True)
    result['raw']['final'] = raw

    def parse_final(text, *, repair=False):
        value = native_json(text, decision_schema(packet, multi_protocol=multi_protocol)
                            if repair or short else packet.answer_schema)
        if repair or short:
            native, warnings = map_decision(packet, base, value, multi_protocol=multi_protocol)
            result['warnings'].extend(warnings)
            result['mapped_decision'] = value
            return native
        return value

    try:
        final = parse_final(raw)
    except (ValueError, TypeError, ValidationError) as error:
        result.update(first_error=dict(type='native_output_invalid', message=str(error)), repair_attempted=True)
        repair_data = dict(data, previous_output=raw, format_problem=str(error))
        repair_instruction = ('Repair this invalid answer format once. Return only the short '
            'native decision schema. Use current legal keys; do not rewrite labels, invent facts or add an '
            'explanation. Preserve the intended answer where it is unambiguous; otherwise decide from '
            'the complete current question. Multi-select add/remove apply relative to B. '
            'This is the same one-repair policy used for every experimental and control arm.')
        if multi_protocol == 'add_remove_v2' and packet.native_input['answer_format'] == 'multi':
            repair_instruction += (
                ' Return only add and remove, never keep. Options absent from both retain their prior '
                'selected or unselected membership in B. The mapped final answer must be nonempty; '
                'if Y is empty, express a legal nonempty selection with add/remove. Do not infer '
                'additions from a previous keep field. Decide from the complete current question '
                'when the previous intended selection is ambiguous.')
        repair = _request(repair_data, repair_instruction,
            decision_schema(packet, multi_protocol=multi_protocol), cfg, cfg['repair_max_tokens'])
        fixed = session.invoke(repair, stage=arm + ':format_repair')
        result['raw']['repair'] = fixed
        try:
            final = parse_final(fixed, repair=True)
        except (ValueError, TypeError, ValidationError) as second:
            result.update(failure_type='native_output_invalid_after_one_repair',
                          final_error=str(second), decision='unavailable')
            return finish()
    result.update(native_answer=final, native_valid=True,
                  decision='changed' if final['answer_choice'] != base['answer_choice'] else 'retained')
    return finish()
