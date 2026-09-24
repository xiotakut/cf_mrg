"""New development A3: compare two saved candidates on the complete original case.

No edited input or new catalogue scoring is constructed. The pair is a focus,
not a restriction on the final native diagnosis. The old A3 remains unchanged.
"""
from copy import deepcopy
import json
import math
import re

from cf_moa.contracts import digest, reject_metadata
from cf_moa.tools.adapters import messages_with_instruction, native_json

VARIANT = 'a3_original_case_pair_comparison_v1'
CONTROL = 'a3_original_case_ordinary_reanswer_v1'
POLICY = dict(seed=42, temperature=0.7, answer_max_tokens=512, repair_max_tokens=128)


def select_focus(packet, base, saved_row, catalog):
    """Use the adopted six-order calibrated probabilities already in the trace."""
    reject_metadata(base)
    if packet.native_input['answer_format'] != 'diagnosis':
        raise ValueError('Original-case comparison supports diagnosis inputs')
    if saved_row['request_id'] != packet.request_id or saved_row['input_hash'] != packet.input_hash:
        raise ValueError('Saved catalogue scores refer to a different current input')
    proposal = saved_row['proposal']
    if proposal['variant'] != 'adopted_R1_dispatch_saved_callbacks_v1':
        raise ValueError('Expected the adopted dispatcher catalogue result')
    result = proposal['trace']['legacy_result']
    if result.get('branch') != 'catalog_vote' or result.get('used_original'):
        raise ValueError('Saved source did not execute the adopted catalogue head')
    old = base['answer_choice']
    scores = result['details']['mean_probabilities']
    if old not in catalog or result['answer'] != old:
        raise ValueError('Complete B differs from its adopted catalogue source')
    if (set(scores) != set(catalog) or len(result['details']['per_order']) != 6
            or not all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in scores.values())):
        raise ValueError('Complete finite six-order candidate probabilities unavailable; do not guess a competitor')
    competitor = max((key for key in catalog if key != old), key=scores.get)
    return dict(input_hash=packet.input_hash, base_answer_ref=digest(base),
        baseline_candidate=old, competitor=competitor, catalog=deepcopy(catalog),
        focus_candidates=[key for key in catalog if key in (old, competitor)],
        candidate_score_source=dict(
            field='proposal.trace.legacy_result.details.mean_probabilities',
            meaning='Mean probabilities across six fixed orders after adopted content-free log-prior correction',
            selection='Highest saved probability excluding B; ties follow the frozen catalogue order',
            saved_row_digest=digest(saved_row), saved_input_hash=saved_row['input_hash'],
            base_probability=scores[old], competitor_probability=scores[competitor],
            catalogue_candidates=len(catalog), new_catalogue_calls=0, fallback_used=False))


def schema(catalog, *, repair=False):
    properties = dict(answer_choice=dict(type='string', enum=list(catalog)))
    if not repair:
        properties['reason'] = dict(type='string')
    return dict(type='object', properties=properties, required=['answer_choice'], additionalProperties=False)


def parse_key(raw, catalog):
    """Only a complete native key may survive a truncated optional reason."""
    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        prefix = re.match(r'^\s*\{\s*"answer_choice"\s*:\s*', raw or '')
        if prefix:
            try:
                choice, end = json.JSONDecoder().raw_decode(raw[prefix.end():])
            except ValueError:
                pass
            else:
                if choice in catalog and re.match(r'^\s*,\s*"reason"\s*:', raw[prefix.end()+end:]):
                    return choice, None, ['optional_reason_incomplete_or_invalid']
        return None, None, ['native_key_unavailable']
    if not isinstance(value, dict) or value.get('answer_choice') not in catalog:
        return None, None, ['native_key_unavailable']
    reason = value.get('reason')
    return value['answer_choice'], reason if isinstance(reason, str) else None, (
        [] if reason is None or isinstance(reason, str) else ['optional_reason_invalid'])


def request(packet, base, focus, *, control=False, config=None, repair_raw=None):
    cfg = dict(POLICY, **(config or {}))
    data = dict(current_native_input=packet.native_input, retrieved_context=packet.retrieved_context,
                model_input=packet.model_input, base_native_answer=base,
                public_diagnosis_catalog=focus['catalog'])
    if not control:
        data['focus_candidates'] = focus['focus_candidates']
    reject_metadata(data)
    instruction = (
        'Independently answer the complete original patient question using the entire public diagnosis catalogue. '
        if control else
        'On the complete ORIGINAL patient case, compare the strongest case-specific support and counterevidence '
        'for the two focus candidates. Identify which actual observation or missing necessary condition '
        'best distinguishes them. The focus pair comes from saved model preferences; it is not clinical proof. ')
    instruction += (
        'Use the full current case, including negation, timing, subject and supplied documents. Do not edit '
        'the case, invent patient facts, or interpret absent information as a negative finding. The baseline '
        'is fallible. You may retain or change it, and may select ANY label in the entire catalogue, including '
        'labels outside the focus pair. No change or agreement is required. Return answer_choice FIRST as '
        'one exact catalogue label, then an optional concise reason. Do not paraphrase the label.\n' +
        json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    if repair_raw is not None:
        instruction += ('\nThis is the one allowed native-key format repair, shared by both arms. '
            'Return only answer_choice as one exact catalogue label; no reason. '
            'Previous response:\n' + repair_raw)
    return dict(kind='generate', messages=messages_with_instruction(packet, instruction),
        schema=schema(focus['catalog'], repair=repair_raw is not None), seed=cfg['seed'],
        temperature=cfg['temperature'],
        max_tokens=cfg['repair_max_tokens'] if repair_raw is not None else cfg['answer_max_tokens'])


def run(packet, session, base, *, control=False, target=None, saved_proposal=None, config=None):
    checkpoint = session.checkpoint()
    focus = saved_proposal
    reject_metadata(focus)
    if (not isinstance(focus, dict) or packet.native_input['answer_format'] != 'diagnosis'
            or focus.get('input_hash') != packet.input_hash or focus.get('base_answer_ref') != digest(base)):
        raise ValueError('Original-case comparison requires its current-input saved candidate selection')
    native_json(json.dumps(base, ensure_ascii=False), packet.answer_schema)
    catalog = focus['catalog']
    if (focus['baseline_candidate'] != base['answer_choice'] or focus['competitor'] not in catalog
            or focus['baseline_candidate'] not in catalog or focus['competitor'] == focus['baseline_candidate']
            or set(focus['focus_candidates']) != {focus['baseline_candidate'], focus['competitor']}):
        raise ValueError('Saved focus pair is not B plus one legal different candidate')
    attempts, previous = [], None
    for ordinal in range(2):
        raw = session.invoke(request(packet, base, focus, control=control, config=config,
                                     repair_raw=previous),
            stage=('A3_original:reanswer' if control else 'A3_original:compare')
                  + (':format_repair' if ordinal else ':native_answer'))
        choice, reason, warnings = parse_key(raw, catalog)
        attempts.append(dict(raw_response=raw, answer_choice=choice, warnings=warnings))
        if choice is not None:
            break
        previous = raw
    native = None
    if choice is not None:
        native = deepcopy(base)
        native['answer_choice'] = choice
        native['step_by_step_thinking'] = (reason if reason is not None else
            'Program mapping of the generated catalogue key; optional model explanation unavailable.')
        native_json(json.dumps(native, ensure_ascii=False), packet.answer_schema)
    return dict(variant=CONTROL if control else VARIANT, native_answer=native,
        native_valid=native is not None, raw=[attempt['raw_response'] for attempt in attempts],
        warnings=warnings, cost=session.cost_since(checkpoint),
        decision='unavailable' if native is None else ('retained' if choice == base['answer_choice'] else 'changed'),
        first_error=None if attempts[0]['answer_choice'] is not None else 'native_key_unavailable',
        failure_type=None if native is not None else 'native_key_unavailable_after_one_repair',
        repair_attempted=len(attempts) == 2, actual_adjudication=True,
        trace=dict(route='ordinary_original_reanswer' if control else 'full_original_pair_comparison',
            input_hash=packet.input_hash, base_answer_ref=digest(base),
            pair=focus['focus_candidates'], competitor=focus['competitor'],
            candidate_score_source=focus['candidate_score_source'],
            final_choice_restricted_to_pair=False, full_catalogue_supplied=True,
            patient_edit_performed=False, attempts=attempts, new_catalogue_calls=0,
            explanation_provenance='unverified_model_judgment', target_argument_unused=target))
