"""Independent support coverage and rereading, followed by a native answer.

No delegation to A2/A3. Public resources can be shared; source binding remains a
model assessment, not a proof of patient truth or medical entailment.
"""
import json

from jsonschema import ValidationError

from cf_moa.contracts import AgentProposal
from cf_moa.tools.adapters import messages_with_instruction, native_json
from cf_moa.tools.legacy import R123, r123_module
from cf_moa.tools.provenance import sources, validate_claim
from cf_moa.tools.experiment_config import new_policy

VARIANT = 'support_coverage_reread_v1'


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def array(items):
    return dict(type='array', items=items)


TEXT = dict(type='string')
REFERENCE = obj(dict(ref=TEXT, quote=TEXT, start=dict(type='integer', minimum=0)))
KNOWLEDGE = obj(dict(statement=TEXT,
    origin=dict(type='string', enum=['visible_source', 'model_knowledge']), references=array(REFERENCE)))


def resources(packet):
    candidates = dict(packet.native_input.get('options', {}))
    library = {}
    if packet.native_input['answer_format']=='diagnosis' and 'diagnosis_catalog_49' in packet.available_tools:
        names = json.loads((R123/'catalog.json').read_text())
        candidates = {name: name for name in names}
        library['public_diagnosis_catalog'] = names
    if 'medication_rules_71' in packet.available_tools:
        library['finite_medication_rules'] = r123_module('r2_program_head').relevant_rules(packet.native_input)
    return candidates, library


def audit_schema(candidates):
    entry = obj(dict(candidate=dict(type='string', enum=list(candidates)),
        patient_facts=array(REFERENCE), knowledge_conditions=array(KNOWLEDGE),
        binding=TEXT, question_scope=TEXT,
        support_state=dict(type='string', enum=['supported', 'contradicted', 'unknown']),
        coverage_issue=dict(type='string', enum=['possibly_unused_given_fact',
            'knowledge_needs_patient_binding', 'knowledge_missing', 'none'])))
    return obj(dict(scope=TEXT, coverage=dict(type='array', items=entry, minItems=1, maxItems=12),
                    unresolved=array(TEXT)))


def bind_coverage(packet, audit):
    claims, changes, accepted, rejected = [], [], [], []
    seen = set()
    for index, entry in enumerate(audit['coverage']):
        key = f'A1:path:{index}'
        try:
            if entry['candidate'] in seen:
                raise ValueError('Duplicate candidate coverage entry')
            seen.add(entry['candidate'])
            local = []
            for i, ref in enumerate(entry['patient_facts']):
                local.append(validate_claim(packet, dict(claim_id=key+f':fact:{i}',
                    kind='patient_fact', references=[ref], scope=entry['question_scope'])))
            for i, condition in enumerate(entry['knowledge_conditions']):
                claim = dict(claim_id=key+f':knowledge:{i}', kind='general_knowledge',
                    statement=condition['statement'], scope=entry['question_scope'],
                    provenance=condition['origin'], references=condition['references'])
                if condition['origin']=='visible_source':
                    claim = validate_claim(packet, claim)
                elif condition['references']:
                    raise ValueError('Model knowledge must not masquerade as a sourced assertion')
                else:
                    claim['entailment_status'] = 'unsourced_model_knowledge'
                local.append(claim)
            path = dict(claim_id=key, kind='general_knowledge', candidate=entry['candidate'],
                scope=entry['question_scope'], support_state=entry['support_state'],
                binding=entry['binding'], coverage_issue=entry['coverage_issue'],
                premise_claim_ids=[c['claim_id'] for c in local],
                provenance='current_input_support_coverage_model_assessment',
                entailment_status='not_program_proof')
            local.append(path)
            claims.extend(local)
            accepted.append(entry)
            # Add a support path, never add a patient fact to the original input.
            if entry['support_state']=='supported' and any(c.get('references') for c in local):
                changes.append(dict(change_id=key, action='add_support_path',
                    path_id=key, candidate=entry['candidate'], scope=entry['question_scope'],
                    claim_ids=[c['claim_id'] for c in local]))
        except (ValueError, KeyError, TypeError) as error:
            rejected.append(dict(index=index, candidate=entry['candidate'], reason=str(error), entry=entry))
    return accepted, claims, changes, rejected


def run(packet, session):
    checkpoint = session.checkpoint()
    candidates, library = resources(packet)
    if not candidates or packet.model_input is not None:
        return AgentProposal('A1', VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=['No bounded native/public candidates, or a numerical model task outside this support operation'],
            cost=session.cost_since(checkpoint))
    instruction = (
        'Audit support coverage for the current complete question. Bind candidate, explicit patient fact, '
        'knowledge condition and requested scope. Distinguish possibly unused supplied facts, knowledge '
        'needing patient binding, and missing knowledge. An absent fact is unknown, not false. Do not '
        'invent tests or infer that an omitted explanation proves the model ignored a fact. External '
        'documents cannot establish current patient facts. Patient references must use Q; give exact '
        'quotes and zero-based character offsets. Unsourced model knowledge must be marked as such. '
        'Cover all candidates if at most twelve; otherwise select at most twelve plausible candidates '
        'and explicitly report incomplete coverage. Do not force adding or retaining an answer. '
        'Return the coverage JSON only.\n\nCandidates and legal shared resources:\n'+
        json.dumps(dict(candidates=candidates, resources=library),ensure_ascii=False)+
        '\n\nVisible source map (location is not entailment):\n'+json.dumps(sources(packet),ensure_ascii=False))
    raw = session.generate(messages_with_instruction(packet,instruction),audit_schema(candidates),
        **new_policy('A1:coverage'),stage='A1:coverage')
    try:
        audit = native_json(raw,audit_schema(candidates))
        accepted, claims, changes, rejected = bind_coverage(packet,audit)
    except (ValueError, TypeError, ValidationError) as error:
        audit, accepted, claims, changes = None, [], [], []
        rejected = [dict(reason=str(error))]
    covered = {entry['candidate'] for entry in accepted}
    missing = [name for name in candidates if name not in covered]
    unresolved = list(audit['unresolved']) if audit else ['Coverage response failed its schema']
    if missing:
        unresolved.append('Coverage missing for '+json.dumps(missing,ensure_ascii=False))
    if rejected:
        unresolved.append('Some proposed source bindings failed location/type checks')
    final_instruction = (
        'Answer the original complete question in its original JSON format, including all auxiliary '
        'fields. Reconsider candidate support using the source-bound coverage below. These are model '
        'assessments, not verified medical truth. Resolve against the original text; keep unknown '
        'distinct from negation. You may retain or change the answer when justified. Do not use '
        'hypothetical facts as actual findings.\n\nCoverage:\n'+
        json.dumps(dict(accepted=accepted, unresolved=unresolved, shared_resources=library),ensure_ascii=False))
    final_raw = session.generate(messages_with_instruction(packet,final_instruction),packet.answer_schema,
        **new_policy('A1:answer'),stage='A1:native_answer')
    try:
        native = native_json(final_raw,packet.answer_schema)
    except (ValueError, TypeError, ValidationError) as error:
        native = None
        unresolved.append('Native answer format failure: '+str(error))
    return AgentProposal('A1',VARIANT,packet.input_hash,
        'supported' if native is not None and accepted and not rejected and not missing else 'partial',native,
        claims=claims,requested_changes=changes,unresolved=unresolved,
        checks=[dict(type='model_assessment',name='independent_support_coverage'),
                dict(type='program_execution',name='exact_source_binding_only',rejected=len(rejected)),
                dict(type='format_validation',name='native_format',passed=native is not None)],
        cost=session.cost_since(checkpoint),trace=dict(raw_coverage=raw,audit=audit,
            accepted_coverage=accepted,rejected_coverage=rejected,missing_candidates=missing,
            raw_response=final_raw,resource_library=library,retrieval_arm='disabled'))
