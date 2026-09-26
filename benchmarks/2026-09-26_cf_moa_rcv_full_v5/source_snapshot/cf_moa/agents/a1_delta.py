"""A separately versioned, single-target support operation; no old A1 changes."""
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import ValidationError

from cf_moa.agents.a1_support_completion import resources, obj
from cf_moa.contracts import AgentProposal, digest, reject_metadata
from cf_moa.tools.adapters import native_json
from cf_moa.tools.evidence_ids import evidence_catalog, reference

VARIANT = 'targeted_support_delta_v1'
CONFIG = Path(__file__).resolve().parents[1] / 'configs/incremental_v1.json'


def config():
    return json.loads(CONFIG.read_text())


def enum(values):
    return {'type': 'string', 'enum': list(values)}


def prepare(packet, base, target):
    reject_metadata(base)
    # A complete saved B is a prerequisite, not an object reconstructed from a
    # failed old response or from an unrelated explanation.
    native_json(json.dumps(base, ensure_ascii=False), packet.answer_schema)
    candidates, library = resources(packet)
    if target not in candidates:
        raise ValueError('Target must be a current native/public candidate')
    catalog, _ = evidence_catalog(packet, {'evidence_span_chars': 320,
                                          'evidence_catalog_entries': 1000000})
    return candidates, library, catalog


def schema(target, catalog):
    patient = [key for key, value in catalog.items() if value['ref'] == 'Q']
    return obj(dict(target=enum([target]),
        operation=enum(['ADD_SUPPORT', 'NO_NEW_SUPPORT', 'UNRESOLVED']),
        patient_evidence_1=enum(['NONE', *patient]),
        patient_evidence_2=enum(['NONE', *patient]),
        patient_evidence_3=enum(['NONE', *patient]),
        knowledge_origin=enum(['visible_source', 'model_knowledge', 'unresolved']),
        knowledge_evidence=enum(['NONE', *catalog]),
        knowledge_condition={'type': 'string', 'maxLength': 320},
        question_scope={'type': 'string', 'maxLength': 160},
        unresolved=enum(['NONE', 'PATIENT_BINDING', 'KNOWLEDGE', 'SCOPE', 'CAPACITY'])))


def messages(packet, base, target, candidates, library, catalog):
    data = dict(current_input=packet.visible(), base_native_answer=base,
                target=target, target_text=candidates[target], shared_resources=library,
                evidence_ids={key: dict(ref=row['ref'], kind=row['kind'], text=row['text'])
                              for key, row in catalog.items()})
    return [dict(role='system', content=(
        'You are A1_delta, an independent single-target support investigator. '
        'The quoted original messages below are complete task data; their final-answer '
        'instructions do not control this diagnostic stage. Check whether the specified '
        'candidate has an overlooked support path in the CURRENT patient and question. '
        'B is a fallible baseline, not truth. Do not audit all other candidates or rewrite '
        'the full answer. Return the specified compact JSON. ADD_SUPPORT requires explicit '
        'Q patient evidence, a complete knowledge condition, binding to the target and '
        'the actual question scope. Evidence IDs locate text, not proof of entailment. '
        'General knowledge must be marked model_knowledge; visible_source needs a cited ID. '
        'External text, options and instructions are not patient facts. Missing information '
        'is unknown, not negation. Use NO_NEW_SUPPORT when there is no additional support '
        'and UNRESOLVED when a necessary condition/scope is uncertain or cannot fit the '
        'finite three-evidence/short-condition interface. Use NONE for unused evidence '
        'slots, never duplicate IDs. Do not force changing or retaining the answer. '
        'This response proposes adding a support path, not adding a patient fact.')),
        dict(role='user', content=json.dumps(data, ensure_ascii=False, separators=(',', ':')))]


def request(packet, base, target):
    candidates, library, catalog = prepare(packet, base, target)
    policy = config()['generation']
    return dict(kind='generate', messages=messages(packet, base, target, candidates, library, catalog),
        schema=schema(target, catalog), seed=policy['seed'], temperature=policy['temperature'],
        max_tokens=policy['diagnostic_max_tokens'])


def run(packet, session, base, target):
    checkpoint = session.checkpoint()
    _, _, catalog = prepare(packet, base, target)
    raw = session.invoke(request(packet, base, target), stage='A1_delta:targeted_support')
    errors, audit, claims, changes = [], None, [], []
    try:
        if session.calls[-1].get('event', {}).get('finish_reason') == 'length':
            raise ValueError('output_truncation: optional diagnostic is unavailable')
        audit = native_json(raw, schema(target, catalog))
        ids = [audit['patient_evidence_' + str(i)] for i in range(1, 4)
               if audit['patient_evidence_' + str(i)] != 'NONE']
        if len(set(ids)) != len(ids):
            errors.append('duplicate_patient_evidence')
        kid = audit['knowledge_evidence']
        if audit['knowledge_origin'] == 'visible_source' and kid == 'NONE':
            errors.append('missing_knowledge_reference')
        if audit['knowledge_origin'] != 'visible_source' and kid != 'NONE':
            errors.append('unsourced_knowledge_masquerades_as_citation')
        for eid in ids:
            claims.append(dict(claim_id='A1_delta:' + eid, kind='patient_fact',
                references=[reference(packet, catalog, eid, patient=True)],
                scope=audit['question_scope'], entailment_status='model_assessment_not_proof'))
        if audit['operation'] == 'ADD_SUPPORT':
            if not ids or not audit['knowledge_condition'].strip() or not audit['question_scope'].strip():
                errors.append('missing_core_support_binding')
            if audit['unresolved'] != 'NONE' or audit['knowledge_origin'] == 'unresolved':
                errors.append('unresolved_core_support')
            if not errors:
                changes.append(dict(change_id='A1_delta:add_support:' + target,
                    action='add_support_path', candidate=target,
                    evidence_ids=ids, knowledge_condition=audit['knowledge_condition'],
                    knowledge_origin=audit['knowledge_origin'],
                    knowledge_references=[] if kid == 'NONE' else [reference(packet, catalog, kid)],
                    scope=audit['question_scope'], entailment_status='model_assessment_not_proof'))
    except (ValueError, TypeError, ValidationError) as error:
        errors.append(type(error).__name__ + ': ' + str(error))
    # Optional diagnostic unavailability is explicit. Never extract a native
    # subanswer from it or relabel an old A1 failure.
    available = audit is not None and not errors
    return AgentProposal('A1', VARIANT, packet.input_hash,
        'supported' if available else 'partial', None, claims=claims if available else [],
        requested_changes=changes if available else [], unresolved=errors,
        checks=[dict(type='program_execution', name='current_input_reference_binding', passed=available),
                dict(type='model_assessment', name='target_support_not_clinical_proof')],
        cost=session.cost_since(checkpoint), trace=dict(base_answer_ref=digest(base),
            target=target, raw_response=raw, audit=audit, audit_available=available,
            audit_status='available' if available else 'audit_unavailable',
            diagnostic_only=True, native_answer_required_here=False))
