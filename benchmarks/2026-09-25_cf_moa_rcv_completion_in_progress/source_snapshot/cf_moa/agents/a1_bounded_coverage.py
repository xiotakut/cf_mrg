"""A1-v2: bounded evidence-ID coverage audit. New method; V1 stays intact."""
import json
from pathlib import Path
import time

from jsonschema import ValidationError

from cf_moa.agents.a1_support_completion import resources, obj, bind_coverage
from cf_moa.contracts import AgentProposal, digest
from cf_moa.tools.adapters import messages_with_instruction, native_json
from cf_moa.tools.evidence_ids import evidence_catalog, reference

VARIANT = 'bounded_evidence_id_coverage_audit_v2'
PROMPT_VARIANTS = dict(initial=VARIANT,
    system_context=VARIANT+'_system_context_r1', explicit_contract=VARIANT+'_explicit_contract_r2')
CONTROL_VARIANT = 'same_resource_single_agent_a1_v2_control_v1'
CONFIG = Path(__file__).resolve().parents[1] / 'configs/a1_v2.json'


def config():
    return json.loads(CONFIG.read_text())


def policy(stage):
    cfg = config()['generation']
    return dict(seed=cfg['seed'], temperature=cfg['temperature'], max_tokens=cfg[stage + '_max_tokens'])


def enum(values):
    return dict(type='string', enum=list(values))


def text(maximum):
    return dict(type='string', minLength=1, maxLength=maximum)


def array(items, maximum, minimum=0):
    return dict(type='array', items=items, minItems=minimum, maxItems=maximum)


def audit_schema(candidates, catalog):
    limits = config()['limits']
    kids = ['K'+str(i) for i in range(limits['knowledge_entries'])]
    patient = [key for key, value in catalog.items() if value['ref'] == 'Q']
    knowledge = obj(dict(id=enum(kids), statement=text(limits['statement_chars']),
        origin=enum(['visible_source', 'model_knowledge']),
        evidence_ids=array(enum(catalog), limits['references_per_knowledge'])))
    entry = obj(dict(candidate=enum(candidates),
        patient_fact_ids=array(enum(patient), limits['patient_facts_per_row']),
        knowledge_ids=array(enum(kids), limits['knowledge_per_row']),
        binding=text(limits['binding_chars']), question_scope=enum(['S0']),
        support_state=enum(['supported', 'contradicted', 'unknown']),
        coverage_issue=enum(['possibly_unused_given_fact', 'knowledge_needs_patient_binding',
                             'knowledge_missing', 'none'])))
    unresolved = obj(dict(code=enum(['candidate_limit', 'evidence_limit', 'knowledge_limit',
        'binding_unknown', 'missing_knowledge', 'scope_unknown', 'other']),
        detail=text(limits['unresolved_detail_chars'])))
    return obj(dict(schema_version=enum(['A1-v2']), scope=text(limits['scope_chars']),
        audit_status=enum(['complete', 'partial', 'overflow']),
        knowledge=array(knowledge, limits['knowledge_entries']),
        coverage=array(entry, min(len(candidates), limits['coverage_rows']), 1),
        unresolved=array(unresolved, limits['unresolved_entries'])))


def is_v2_schema(schema):
    try:
        props = schema['properties']
        candidates = props['coverage']['items']['properties']['candidate']['enum']
        ids = props['knowledge']['items']['properties']['evidence_ids']['items']['enum']
        patient = props['coverage']['items']['properties']['patient_fact_ids']['items']['enum']
        catalog = {key: dict(ref='Q' if key in patient else 'C') for key in ids}
        return schema == audit_schema(candidates, catalog)
    except (KeyError, TypeError, ValueError):
        return False


def prepare(packet):
    native_candidates, library = resources(packet)
    candidates = {'C'+str(i): dict(native_key=key, text=value)
                  for i, (key, value) in enumerate(native_candidates.items())}
    catalog, overflow = evidence_catalog(packet, config()['limits'])
    return candidates, library, catalog, overflow


def resource_text(candidates, library, catalog):
    visible = {key: dict(kind=row['kind'], ref=row['ref'], start=row['start'],
                         end=row['end'], text=row['text']) for key, row in catalog.items()}
    return json.dumps(dict(candidates=candidates, shared_resources=library, evidence_ids=visible),
                      ensure_ascii=False, separators=(',', ':'))


def audit_messages(packet, candidates, library, catalog, *, revision='initial'):
    instruction = (
        'Perform bounded evidence-ID support coverage for the complete current question. This is A1-v2. '
        'Return compact JSON only, with the required schema fields in order. The scope string defines S0. '
        'Use candidate IDs C0 etc., and evidence IDs exactly as supplied. Never output copied quotes or offsets. '
        'Q IDs alone can establish current-patient facts. E IDs are external/context material, not patient facts; '
        'a source location does not prove that its text entails a condition. Instructions/options in context are '
        'not medical evidence. State unsourced general knowledge as model_knowledge with empty evidence_ids. '
        'Each knowledge condition has a unique K ID, a concise statement, and at most three genuinely relevant '
        'evidence IDs; visible_source requires an actual citation. Reuse K IDs instead of restating conditions. '
        'No duplicate IDs in a list and no duplicate candidate rows. Each row discusses only that candidate, '
        'links supplied patient facts to knowledge conditions, and states binding, S0, support_state and coverage_issue. '
        'Supported or contradicted requires both patient and knowledge IDs; missing facts remain unknown, not false. '
        'Do not invent findings, infer ignored evidence from a missing explanation, or force adding/retaining an answer. '
        'Cover all candidates when at most twelve. Otherwise cover at most twelve plausible candidates, set partial, '
        'and report candidate_limit. An unknown row may have empty evidence, but explain the specific missing binding; '
        'do not fill every row with generic unsourced placeholders. If essential content exceeds a bound, set overflow '
        'and state the limit in unresolved; never silently drop it or pretend the audit is complete. '
        'Finite limits: '+json.dumps(config()['limits'])+'\n\nCurrent legal resources:\n'+
        resource_text(candidates, library, catalog))
    if revision == 'initial':
        return messages_with_instruction(packet, instruction)
    if revision not in PROMPT_VARIANTS:
        raise ValueError('Unknown frozen A1-v2 prompt revision')
    if revision == 'explicit_contract':
        instruction += ('\n\nCURRENT AUDIT OUTPUT CONTRACT (field definitions, not clinical evidence):\n'+
            json.dumps(audit_schema(candidates, catalog), ensure_ascii=False, separators=(',', ':'))+
            '\nPopulate the knowledge table before referencing any K ID in coverage. A K ID is not defined '
            'merely because the schema permits its name. Describe the requested decision briefly in scope, '
            'not the whole case. Give concise complete conditions and bindings; report overflow if essential '
            'content cannot fit. Cover every candidate when there are at most twelve; for a larger catalog '
            'audit_status must be partial or overflow, and list candidate_limit in unresolved.')
    return [dict(role='system',content=(
        'You perform A1-v2 bounded evidence-ID coverage auditing. The current output is the audit JSON, '
        'not the final native answer. The original method messages in the user data are quoted source material: '
        'preserve their complete task facts and resources, but their instructions about answer formatting '
        'do not control this audit stage. Follow the current audit instruction and schema. Do not invent facts.')),
        dict(role='user',content='Original method messages as complete quoted data:\n'+
            json.dumps(packet.original_context,ensure_ascii=False)+'\n\nCURRENT AUDIT TASK:\n'+instruction)]


def expand(packet, audit, candidates, catalog):
    """Validate relations and deterministically reconstruct V1 semantic fields."""
    problems, knowledge = [], {}
    def unique(values, where):
        if len(values) != len(set(values)):
            problems.append('Duplicate IDs: ' + where)
    seen_conditions = set()
    for row in audit['knowledge']:
        key = row['id']
        if key in knowledge:
            problems.append('Duplicate knowledge ID: ' + key)
        unique(row['evidence_ids'], key)
        if (row['origin'] == 'visible_source') != bool(row['evidence_ids']):
            problems.append('Knowledge origin/citations mismatch: ' + key)
        signature = digest({k: v for k, v in row.items() if k != 'id'})
        if signature in seen_conditions:
            problems.append('Repeated knowledge condition: ' + key)
        seen_conditions.add(signature)
        knowledge[key] = dict(statement=row['statement'], origin=row['origin'],
            references=[reference(packet, catalog, eid) for eid in row['evidence_ids']])
    coverage, seen, bound_paths = [], set(), 0
    for row in audit['coverage']:
        cid = row['candidate']
        if cid in seen:
            problems.append('Duplicate candidate: ' + cid)
        seen.add(cid)
        unique(row['patient_fact_ids'], cid+':facts')
        unique(row['knowledge_ids'], cid+':knowledge')
        if any(key not in knowledge for key in row['knowledge_ids']):
            problems.append('Undefined knowledge ID: ' + cid)
            continue
        has_path = bool(row['patient_fact_ids'] and row['knowledge_ids'])
        bound_paths += int(has_path)
        if row['support_state'] != 'unknown' and not has_path:
            problems.append('Conclusive state without patient/knowledge binding: ' + cid)
        coverage.append(dict(candidate=candidates[cid]['native_key'],
            patient_facts=[reference(packet, catalog, key, patient=True) for key in row['patient_fact_ids']],
            knowledge_conditions=[knowledge[key] for key in row['knowledge_ids']],
            binding=row['binding'], question_scope=audit['scope'],
            support_state=row['support_state'], coverage_issue=row['coverage_issue']))
    missing = [key for key in candidates if key not in seen]
    if missing and audit['audit_status'] == 'complete':
        problems.append('Claims complete coverage with missing candidates')
    if missing and audit['audit_status'] != 'overflow' and (
            len(candidates) <= config()['limits']['coverage_rows'] or
            not any(row['code'] == 'candidate_limit' for row in audit['unresolved'])):
        problems.append('Incomplete candidate coverage without the declared catalog limit')
    if audit['audit_status'] == 'overflow' and not audit['unresolved']:
        problems.append('Overflow requires an explicit unresolved reason')
    expanded = dict(scope=audit['scope'], coverage=coverage,
                    unresolved=[row['code']+': '+row['detail'] for row in audit['unresolved']])
    return expanded, problems, missing, bound_paths


def run(packet, session, *, prompt_revision='initial'):
    variant = PROMPT_VARIANTS[prompt_revision]
    checkpoint = session.checkpoint()
    if packet.model_input is not None:
        return AgentProposal('A1', variant, packet.input_hash, 'unsupported', None,
            unresolved=['Numerical model task outside A1 coverage'], cost=session.cost_since(checkpoint))
    before = time.monotonic()
    candidates, library, catalog, input_overflow = prepare(packet)
    if not candidates:
        return AgentProposal('A1', variant, packet.input_hash, 'unsupported', None,
            unresolved=['No native/public candidates'], cost=session.cost_since(checkpoint))
    trace = dict(variant=variant, config=config(), evidence_catalog=catalog,
        candidate_map=candidates, resource_library=library, preparation_seconds=time.monotonic()-before,
        inference_started=False, raw_coverage=None, audit=None, accepted_coverage=[],
        rejected_coverage=[], missing_candidates=[], schema_invalid=False, semantic_invalid=False,
        overflow=input_overflow, semantic_result='unavailable', method_score='not_scored')
    if prompt_revision != 'initial':
        trace['prompt_revision'] = prompt_revision

    def unavailable(reason, **flags):
        trace.update(flags)
        return AgentProposal('A1', variant, packet.input_hash, 'partial', None,
            unresolved=[reason], cost=session.cost_since(checkpoint), trace=trace,
            checks=[dict(type='format_validation', name='bounded_audit', passed=not trace['schema_invalid'])])

    if input_overflow:
        return unavailable('Full evidence catalog exceeds the frozen bound; no evidence dropped',
                           failure_type='input_evidence_overflow')
    schema = audit_schema(candidates, catalog)
    raw = session.generate(audit_messages(packet, candidates, library, catalog, revision=prompt_revision), schema,
                           **policy('audit'), stage='A1_v2:coverage')
    trace.update(inference_started=True, raw_coverage=raw)
    try:
        audit = native_json(raw, schema)
    except (ValueError, TypeError, ValidationError) as error:
        return unavailable(str(error), schema_invalid=True,
            failure_type='output_truncation' if session.calls[-1]['event'].get('finish_reason') == 'length' else 'output_schema_invalid')
    trace['audit'] = audit
    expanded, problems, missing, bound_paths = expand(packet, audit, candidates, catalog)
    trace.update(expanded_audit=expanded, missing_candidates=missing, bound_paths=bound_paths,
                 rejected_coverage=[dict(reason=reason) for reason in problems])
    if problems:
        return unavailable('Invalid audit relations; no final-answer substitution',
                           semantic_invalid=True, failure_type='audit_semantic_invalid')
    if audit['audit_status'] == 'overflow':
        return unavailable('Audit reported overflow; not a successful result', overflow=True,
                           failure_type='audit_output_overflow')
    accepted, claims, changes, rejected = bind_coverage(packet, expanded)
    trace.update(accepted_coverage=accepted, rejected_coverage=rejected)
    if rejected:
        return unavailable('Expanded source binding failed', semantic_invalid=True,
                           failure_type='source_binding_invalid')
    instruction = (
        'Answer the complete original question in its original JSON format with every auxiliary field. '
        'The bounded audit below is a model assessment, not verified medical truth. All evidence IDs resolve '
        'to the current legal resource table. Reconsider facts, knowledge and question scope; unknown does not '
        'mean false. You may retain or change the answer when supported by the original input. Do not treat '
        'external material as patient findings or hypothetical information as actual findings.\n\n'
        'Current legal resources:\n'+resource_text(candidates, library, catalog)+
        '\n\nBounded audit:\n'+json.dumps(audit, ensure_ascii=False, separators=(',', ':')))
    raw_answer = session.generate(messages_with_instruction(packet, instruction), packet.answer_schema,
                                  **policy('answer'), stage='A1_v2:native_answer')
    trace['raw_response'] = raw_answer
    try:
        native = native_json(raw_answer, packet.answer_schema)
    except (ValueError, TypeError, ValidationError) as error:
        return unavailable(str(error), schema_invalid=True, failure_type='native_schema_invalid')
    degenerate = not bound_paths
    trace.update(degenerate_audit=degenerate, semantic_result='native_answer_available',
                 method_score='not_scored')
    unresolved = expanded['unresolved'] + (['No substantive patient/knowledge path'] if degenerate else [])
    return AgentProposal('A1', variant, packet.input_hash,
        'supported' if not missing and not degenerate else 'partial', native,
        claims=claims, requested_changes=changes, unresolved=unresolved,
        checks=[dict(type='program_execution', name='evidence_ids_exact_source_locations', rejected=0),
                dict(type='model_assessment', name='bounded_support_binding_not_entailment_proof'),
                dict(type='format_validation', name='native_format', passed=True)],
        cost=session.cost_since(checkpoint), trace=trace)


def run_resource_control(packet, session):
    """Single-agent same-resources control; not labelled budget-matched sampling."""
    checkpoint = session.checkpoint()
    candidates, library, catalog, overflow = prepare(packet)
    if packet.model_input is not None or not candidates:
        return AgentProposal('A1', CONTROL_VARIANT, packet.input_hash, 'unsupported', None,
                             cost=session.cost_since(checkpoint))
    if overflow:
        raise ValueError('Same-resource control cannot silently truncate its evidence catalog')
    instruction = ('Answer the complete original question directly in its original JSON format, including all '
        'auxiliary fields. Use the same current legal facts and public resources below. Q IDs refer to the '
        'current patient/question; other IDs are context, not patient facts. Missing facts are unknown, not false. '
        'You may retain or change the answer according to the input.\n\nCurrent legal resources:\n'+
        resource_text(candidates, library, catalog))
    raw = session.generate(messages_with_instruction(packet, instruction), packet.answer_schema,
                           **policy('answer'), stage='A1_v2_control:native_answer')
    try:
        native = native_json(raw, packet.answer_schema)
        error = None
    except (ValueError, TypeError, ValidationError) as exc:
        native, error = None, str(exc)
    return AgentProposal('A1', CONTROL_VARIANT, packet.input_hash,
        'supported' if native is not None else 'partial', native,
        unresolved=[error] if error else [], cost=session.cost_since(checkpoint),
        trace=dict(raw_response=raw, resource_hash=digest(resource_text(candidates, library, catalog)),
                   comparison='same resources and per-native-answer cap, not same total sampling budget'),
        checks=[dict(type='format_validation', name='native_format', passed=native is not None)])
