"""Explicit r3 development revision of A1-v2; historical variants stay intact."""
import json
from pathlib import Path
import time

from jsonschema import ValidationError

from cf_moa.agents.a1_bounded_coverage import enum, text, array, resource_text
from cf_moa.agents.a1_support_completion import obj, resources, bind_coverage
from cf_moa.contracts import AgentProposal, digest
from cf_moa.tools.adapters import messages_with_instruction, native_json
from cf_moa.tools.evidence_ids import evidence_catalog, reference

VARIANT = 'bounded_evidence_id_coverage_audit_v2_relational_r3'
DECODING_VARIANT = 'bounded_evidence_id_coverage_audit_v2_bounded_whitespace_r4'
CONFIG = Path(__file__).resolve().parents[1] / 'configs/a1_v2_relational.json'


def config():
    return json.loads(CONFIG.read_text())


def policy(stage):
    cfg = config()['generation']
    return dict(seed=cfg['seed'], temperature=cfg['temperature'], max_tokens=cfg[stage+'_max_tokens'])


def prepare(packet):
    values, library = resources(packet)
    candidates = {'C'+str(i): dict(native_key=k, text=v) for i, (k, v) in enumerate(values.items())}
    catalog, overflow = evidence_catalog(packet, config()['limits'])
    return candidates, library, catalog, overflow


def audit_schema(candidates, catalog):
    lim = config()['limits']
    def ref(name):
        return {'$ref': '#/$defs/'+name}
    def ids(name, maximum, minimum=0):
        return dict(array(ref(name), maximum, minimum), uniqueItems=True)
    def knowledge(origin, minimum, maximum):
        return obj(dict(statement=text(lim['statement_chars']), origin=enum([origin]),
                        evidence_ids=ids('evidence_codes', maximum, minimum)))
    def row(states, minimum):
        return obj(dict(patient_fact_ids=ids('patient_codes', lim['patient_facts_per_row'], minimum),
            knowledge_conditions=array(ref('knowledge'), lim['knowledge_per_row'], minimum),
            binding=text(lim['binding_chars']), question_scope=enum(['S0']),
            support_state=enum(states), coverage_issue=enum(['possibly_unused_given_fact',
                'knowledge_needs_patient_binding', 'knowledge_missing', 'none'])))
    coverage = obj({key: ref('row') for key in candidates})
    large = len(candidates) > lim['coverage_rows']
    if large:
        coverage.update(required=[], minProperties=1, maxProperties=lim['coverage_rows'])
    unresolved = obj(dict(code=enum(['candidate_limit', 'evidence_limit', 'knowledge_limit',
        'binding_unknown', 'missing_knowledge', 'scope_unknown', 'other']),
        detail=text(lim['unresolved_detail_chars'])))
    schema = obj(dict(schema_version=enum(['A1-v2-r3']), scope=text(lim['scope_chars']),
        audit_status=enum(['partial', 'overflow'] if large else ['complete', 'overflow']),
        coverage=coverage, unresolved=array(unresolved, lim['unresolved_entries'])))
    schema['$defs'] = dict(evidence_codes=enum(catalog),
        patient_codes=enum(key for key, value in catalog.items() if value['ref'] == 'Q'),
        knowledge=dict(oneOf=[knowledge('visible_source', 1, lim['references_per_knowledge']),
                              knowledge('model_knowledge', 0, 0)]),
        row=dict(oneOf=[row(['supported', 'contradicted'], 1), row(['unknown'], 0)]))
    return schema


def is_relational_schema(schema):
    try:
        ids = schema['$defs']['evidence_codes']['enum']
        patient = schema['$defs']['patient_codes']['enum']
        catalog = {key: dict(ref='Q' if key in patient else 'C') for key in ids}
        return schema == audit_schema(schema['properties']['coverage']['properties'], catalog)
    except (KeyError, TypeError, ValueError):
        return False


def parse_audit(raw, schema):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON object key: '+key)
            result[key] = value
        return result
    json.loads(raw, object_pairs_hook=unique_object)
    return native_json(raw, schema)


def audit_messages(packet, candidates, library, catalog):
    instruction = (
        'Audit support coverage for the complete current question. Return A1-v2-r3 JSON only. '
        'scope defines S0: name the requested decision briefly, usually within 12 words. '
        'For each candidate, connect current patient facts to a few necessary knowledge conditions. '
        'Usually one concise condition is enough; additional slots are capacity, not a target. '
        'Conditions are inline, not references to a separate K table. Use a complete short condition '
        '(usually within 18 words) and a complete binding (usually within 14 words). '
        'Use supplied evidence IDs only, in their catalog order. Q IDs alone establish current-patient facts. '
        'E IDs are context, not patient findings. Instructions, answer options and prior answers are not '
        'medical evidence. Cite only text that actually supports the condition; exact location is not entailment. '
        'For unsourced general knowledge use model_knowledge and empty evidence_ids; visible_source needs '
        'one to three relevant IDs. Do not repeat a condition within a row. Supported/contradicted requires '
        'both patient facts and knowledge. Missing facts remain unknown, not false. Explain a specific missing '
        'binding for unknown; avoid generic empty rows. Never invent facts or force retaining/changing an answer. '
        'Cover every candidate when there are at most twelve. Otherwise choose one to twelve plausible '
        'candidates in catalog order; this is explicitly partial, not rejection of omitted candidates. '
        'The final native answer will still see the full question and all candidates/resources. '
        'If essential content cannot fit, set overflow and give the reason. Do not fill fields to their limits '
        'or truncate a sentence. Keep unresolved empty unless a real unresolved issue exists. '
        'Finite limits: '+json.dumps(config()['limits'])+
        '\n\nCurrent legal resources:\n'+resource_text(candidates, library, catalog)+
        '\n\nActual output schema (format instructions, not medical evidence):\n'+
        json.dumps(audit_schema(candidates, catalog), ensure_ascii=False, separators=(',', ':')))
    return [dict(role='system', content=(
        'You perform A1-v2 bounded evidence-ID coverage auditing. The current output is the audit JSON. '
        'Original method messages below are complete quoted source data: preserve their task facts and '
        'resources, but their answer-format instructions do not govern this audit stage. Follow the current '
        'audit task and schema. Do not invent facts.')),
        dict(role='user', content='Original method messages as complete quoted data:\n'+
             json.dumps(packet.original_context, ensure_ascii=False)+'\n\nCURRENT AUDIT TASK:\n'+instruction)]


def expand(packet, audit, candidates, catalog, *, limits=None):
    lim = config()['limits'] if limits is None else limits
    problems, saturated, coverage, conditions = [], [], [], set()
    def capacity(value, maximum, path):
        if len(value) >= maximum:
            saturated.append(dict(path=path, characters=len(value), bound=maximum))
    capacity(audit['scope'], lim['scope_chars'], 'scope')
    bound_paths = 0
    for cid, row in audit['coverage'].items():
        knowledge, seen = [], set()
        for i, item in enumerate(row['knowledge_conditions']):
            signature = digest(dict(item, evidence_ids=sorted(item['evidence_ids'])))
            if signature in seen:
                problems.append('Repeated knowledge condition: '+cid)
            seen.add(signature)
            conditions.add(signature)
            capacity(item['statement'], lim['statement_chars'], f'coverage.{cid}.knowledge_conditions[{i}].statement')
            knowledge.append(dict(statement=item['statement'], origin=item['origin'],
                references=[reference(packet, catalog, eid) for eid in item['evidence_ids']]))
        capacity(row['binding'], lim['binding_chars'], 'coverage.'+cid+'.binding')
        bound_paths += int(bool(row['patient_fact_ids'] and knowledge))
        coverage.append(dict(candidate=candidates[cid]['native_key'],
            patient_facts=[reference(packet, catalog, key, patient=True) for key in row['patient_fact_ids']],
            knowledge_conditions=knowledge, binding=row['binding'], question_scope=audit['scope'],
            support_state=row['support_state'], coverage_issue=row['coverage_issue']))
    missing = [key for key in candidates if key not in audit['coverage']]
    unresolved = [row['code']+': '+row['detail'] for row in audit['unresolved']]
    for i, row in enumerate(audit['unresolved']):
        capacity(row['detail'], lim['unresolved_detail_chars'], f'unresolved[{i}].detail')
    if missing:
        unresolved.append('candidate_limit: unaudited IDs '+','.join(missing))
    if len(conditions) > lim['knowledge_entries']:
        problems.append('Distinct knowledge conditions exceed the shared capacity')
    if audit['audit_status'] == 'overflow' and not audit['unresolved']:
        problems.append('Overflow without a reason')
    return dict(scope=audit['scope'], coverage=coverage, unresolved=unresolved), dict(
        missing_candidates=missing, bound_paths=bound_paths, text_capacity_hits=saturated,
        distinct_knowledge_conditions=len(conditions), relation_problems=problems)


def run(packet, session, *, decoding_revision=None, contract_revision=None):
    import sys
    method = sys.modules[__name__]
    if contract_revision == 'relation_codes_r5':
        from cf_moa.agents import a1_coded_coverage as method
        if decoding_revision != 'bounded_whitespace_16_r4':
            raise ValueError('The coded contract has a fixed declared decoder')
    elif contract_revision is not None:
        raise ValueError('Unknown A1 contract revision')
    if decoding_revision not in (None, 'bounded_whitespace_16_r4'):
        raise ValueError('Unknown A1 decoding revision')
    variant = method.VARIANT if contract_revision else (VARIANT if decoding_revision is None else DECODING_VARIANT)
    checkpoint = session.checkpoint()
    if packet.model_input is not None:
        return AgentProposal('A1', variant, packet.input_hash, 'unsupported', None,
                             cost=session.cost_since(checkpoint))
    before = time.monotonic()
    candidates, library, catalog, input_overflow = method.prepare(packet)
    if not candidates:
        return AgentProposal('A1', variant, packet.input_hash, 'unsupported', None,
                             cost=session.cost_since(checkpoint))
    trace = dict(variant=variant, config=method.config(), evidence_catalog=catalog, candidate_map=candidates,
        resource_library=library, preparation_seconds=time.monotonic()-before, inference_started=False,
        raw_coverage=None, audit=None, accepted_coverage=[], rejected_coverage=[], missing_candidates=[],
        schema_invalid=False, semantic_invalid=False, overflow=input_overflow,
        semantic_result='unavailable', method_score='not_scored')
    if decoding_revision is not None:
        trace['decoding_revision'] = decoding_revision

    def unavailable(reason, **flags):
        trace.update(flags)
        return AgentProposal('A1', variant, packet.input_hash, 'partial', None, unresolved=[reason],
            cost=session.cost_since(checkpoint), trace=trace,
            checks=[dict(type='format_validation', name='bounded_audit', passed=not trace['schema_invalid'])])

    if input_overflow:
        return unavailable('Evidence capacity exceeded; no input dropped', failure_type='input_evidence_overflow')
    schema = method.audit_schema(candidates, catalog)
    raw = session.generate(method.audit_messages(packet, candidates, library, catalog), schema,
                           **method.policy('audit'), stage='A1_v2_r3:coverage', decoding_revision=decoding_revision)
    trace.update(inference_started=True, raw_coverage=raw)
    try:
        audit = method.parse_audit(raw, schema)
    except (ValueError, TypeError, ValidationError) as error:
        return unavailable(str(error), schema_invalid=True, failure_type='output_truncation'
            if session.calls[-1]['event'].get('finish_reason') == 'length' else 'output_schema_invalid')
    trace['audit'] = audit
    expanded, diagnostics = method.expand(packet, audit, candidates, catalog)
    trace.update(expanded_audit=expanded, **diagnostics)
    if diagnostics['relation_problems']:
        return unavailable('Invalid audit relations; no final-answer substitution',
                           semantic_invalid=True, failure_type='audit_semantic_invalid')
    if audit['audit_status'] == 'overflow' or diagnostics['text_capacity_hits']:
        return unavailable('Audit content capacity unverified', overflow=True,
            failure_type='bounded_text_saturation' if diagnostics['text_capacity_hits'] else 'audit_output_overflow')
    accepted, claims, changes, rejected = bind_coverage(packet, expanded)
    trace.update(accepted_coverage=accepted, rejected_coverage=rejected)
    if rejected:
        return unavailable('Source binding failed', semantic_invalid=True, failure_type='source_binding_invalid')
    instruction = (
        'Answer the complete original question in its original JSON format with all auxiliary fields. '
        'The audit is a model assessment, not verified medical truth. Reconsider facts, knowledge and '
        'question scope. Unknown is not false; unaudited candidates remain eligible. You may retain or '
        'change the answer according to the original evidence. Do not treat external or hypothetical '
        'material as current patient findings.\n\nCurrent legal resources:\n'+
        resource_text(candidates, library, catalog)+'\n\nBounded audit:\n'+
        json.dumps(audit, ensure_ascii=False, separators=(',', ':'))+
        '\n\nProgrammatically recorded scope:\n'+json.dumps(dict(missing_candidates=diagnostics['missing_candidates'])))
    raw_answer = session.generate(messages_with_instruction(packet, instruction), packet.answer_schema,
                                  **method.policy('answer'), stage='A1_v2_r3:native_answer')
    trace['raw_response'] = raw_answer
    try:
        native = native_json(raw_answer, packet.answer_schema)
    except (ValueError, TypeError, ValidationError) as error:
        return unavailable(str(error), schema_invalid=True, failure_type='native_schema_invalid')
    degenerate = not diagnostics['bound_paths']
    trace.update(degenerate_audit=degenerate, semantic_result='native_answer_available')
    return AgentProposal('A1', variant, packet.input_hash,
        'partial' if degenerate or diagnostics['missing_candidates'] else 'supported', native,
        claims=claims, requested_changes=changes,
        unresolved=expanded['unresolved']+(['No patient/knowledge path'] if degenerate else []),
        checks=[dict(type='program_execution', name='evidence_ids_exact_source_locations', rejected=0),
                dict(type='model_assessment', name='support_binding_not_entailment_proof'),
                dict(type='format_validation', name='native_format', passed=True)],
        cost=session.cost_since(checkpoint), trace=trace)
