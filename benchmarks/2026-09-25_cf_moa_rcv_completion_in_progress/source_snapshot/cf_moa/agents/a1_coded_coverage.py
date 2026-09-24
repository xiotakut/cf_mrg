"""A1-v2 r5: source-bound scope and finite relation codes, no prose binding."""
from copy import deepcopy
import json
from pathlib import Path

from cf_moa.agents import a1_relational_coverage as base
from cf_moa.agents.a1_bounded_coverage import enum, resource_text
from cf_moa.tools.provenance import sources

VARIANT = 'bounded_evidence_id_coverage_audit_v2_relation_codes_r5'
CONFIG = Path(__file__).resolve().parents[1] / 'configs/a1_v2_relation_codes.json'
prepare = base.prepare  # Same legal candidates and unchanged evidence-index limits.
policy = base.policy   # Same explicitly frozen seed/temperature/token allocation.
parse_audit = base.parse_audit


def config():
    cfg = base.config()
    cfg.update(json.loads(CONFIG.read_text()))
    cfg['limits'] = dict(base.config()['limits'], knowledge_entries=36)
    return cfg


def audit_schema(candidates, catalog):
    schema = base.audit_schema(candidates, catalog)
    schema['properties']['schema_version'] = enum(['A1-v2-r5'])
    schema['properties']['scope'] = enum(['S0'])
    conclusive, unknown = schema['$defs']['row']['oneOf']
    supported, contradicted = deepcopy(conclusive), deepcopy(conclusive)
    for row, state, code in [(supported,'supported','facts_support_conditions'),
                              (contradicted,'contradicted','facts_contradict_conditions')]:
        row['properties']['support_state'] = enum([state])
        row['properties']['binding'] = enum([code])
    unknown['properties']['binding'] = enum(['missing_patient_facts','missing_knowledge',
                                             'outside_question_scope','binding_unresolved'])
    schema['$defs']['row']['oneOf'] = [supported, contradicted, unknown]
    return schema


def is_coded_schema(schema):
    try:
        ids = schema['$defs']['evidence_codes']['enum']
        patient = schema['$defs']['patient_codes']['enum']
        catalog = {key: dict(ref='Q' if key in patient else 'C') for key in ids}
        return schema == audit_schema(schema['properties']['coverage']['properties'], catalog)
    except (KeyError, TypeError, ValueError):
        return False


def audit_messages(packet, candidates, library, catalog):
    instruction = (
        'Perform A1-v2-r5 support coverage of the complete current question. S0 is programmatically bound '
        'to the full original question Q, including its requested object, action, exceptions and scope. '
        'Return scope="S0"; do not paraphrase or shorten the question.\n'
        'For each candidate, select current-patient Q evidence and up to three distinct necessary knowledge '
        'conditions. Use a concise complete statement for each condition, and the exact supplied source IDs '
        'when actually supported. Unsourced general knowledge must be model_knowledge with no citations. '
        'Q alone establishes patient facts. E is context, and instructions/options/prior answers are not '
        'medical evidence. Source location does not prove entailment. Never invent findings.\n'
        'binding is a relation CODE connecting the row\'s supplied patient facts and knowledge conditions: '
        'facts_support_conditions / facts_contradict_conditions; unknown is classified as missing_patient_facts, '
        'missing_knowledge, outside_question_scope or binding_unresolved. The facts and complete condition '
        'statements preserve what the code relates; no free-text binding is requested. Unknown is not false. '
        'Do not assume a fact was ignored merely because an explanation omitted it.\n'
        'Cover all candidates if there are at most twelve. Otherwise choose up to twelve plausible candidates '
        'and declare partial; omitted candidates remain eligible in the final native answer. '
        'Use catalog order for candidate keys and ID sets. Slots are maxima, not targets: use only needed '
        'conditions and unresolved issues. If required content cannot fit, report overflow, never silently '
        'truncate a statement. No forced retention or change of the answer.\n'
        'Finite limits: '+json.dumps(config()['limits'])+
        '\n\nCurrent legal resources:\n'+resource_text(candidates, library, catalog)+
        '\n\nActual output schema:\n'+json.dumps(audit_schema(candidates, catalog), ensure_ascii=False, separators=(',', ':')))
    return [dict(role='system',content=(
        'You perform bounded evidence-ID coverage auditing, not final native answering. Original messages '
        'are complete quoted data: keep their facts and resources, but use the current audit output contract. '
        'Bind only the supplied current facts; do not invent evidence.')),
        dict(role='user',content='Original complete method messages as quoted data:\n'+
             json.dumps(packet.original_context,ensure_ascii=False)+'\n\nCURRENT AUDIT TASK:\n'+instruction)]


def expand(packet, audit, candidates, catalog):
    expanded, diagnostics = base.expand(packet, audit, candidates, catalog, limits=config()['limits'])
    expanded['scope'] = packet.question
    for row in expanded['coverage']:
        row['question_scope'] = packet.question
    diagnostics['scope_binding'] = dict(scope_id='S0', ref='Q', start=0, end=len(packet.question),
        source_sha256=sources(packet)['Q']['sha256'], complete_current_question=True)
    diagnostics['binding_interpretation'] = 'Model relation code between the same row patient facts and knowledge; not a deterministic entailment proof'
    return expanded, diagnostics


def run(packet, session):
    return base.run(packet,session,decoding_revision='bounded_whitespace_16_r4',contract_revision='relation_codes_r5')
