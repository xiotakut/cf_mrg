"""A1 mechanism control: bounded source highlighting, then native reanswer.

This is not a support-coverage expert. It shares legal resources and maximum
output allocation with A1-v2, but creates no medical knowledge/binding audit.
"""
import json
from pathlib import Path

from jsonschema import ValidationError

from cf_moa.agents.a1_bounded_coverage import enum, array, resource_text
from cf_moa.agents.a1_support_completion import obj
from cf_moa.agents.a1_coded_coverage import prepare, parse_audit
from cf_moa.contracts import AgentProposal, digest
from cf_moa.tools.adapters import messages_with_instruction, native_json
from cf_moa.tools.evidence_ids import reference

VARIANT = 'same_resources_bounded_evidence_highlighting_v1'
CONFIG = Path(__file__).resolve().parents[1]/'configs/evidence_highlighting.json'


def config():
    return json.loads(CONFIG.read_text())


def policy(stage):
    cfg = config()['generation']
    return dict(seed=cfg['seed'],temperature=cfg['temperature'],max_tokens=cfg[stage+'_max_tokens'])


def selection_schema(candidates, catalog):
    limits = config()['limits']
    selection = obj({key:dict(array({'$ref':'#/$defs/evidence_codes'},limits['highlights_per_candidate']),
                              uniqueItems=True) for key in candidates})
    large = len(candidates)>limits['candidate_rows']
    if large:
        selection.update(required=[],minProperties=1,maxProperties=limits['candidate_rows'])
    schema = obj(dict(schema_version=enum(['evidence-highlighting-v1']),
        selection_status=enum(['partial','overflow'] if large else ['complete','overflow']),
        highlights=selection))
    schema['$defs'] = dict(evidence_codes=enum(catalog))
    return schema


def is_highlight_schema(schema):
    try:
        return schema == selection_schema(schema['properties']['highlights']['properties'],
                                           schema['$defs']['evidence_codes']['enum'])
    except (KeyError, TypeError, ValueError):
        return False


def highlight_messages(packet, candidates, library, catalog):
    instruction = (
        'Highlight existing source spans potentially relevant to each candidate for the complete current question. '
        'Return evidence-highlighting-v1 JSON. Select zero to four supplied evidence IDs per candidate in '
        'catalog order; an empty list is allowed. Do not write knowledge conditions, conclusions, support '
        'states, or binding explanations. Q IDs locate the current question/patient; E IDs locate context '
        'and do not establish patient findings. Instructions, options and prior answers are not medical '
        'evidence. A highlight is relevance selection, not evidence that a candidate is correct. '
        'For at most twelve candidates include every candidate key and selection_status=complete. '
        'For a larger catalog select one to twelve candidate keys and selection_status=partial. Omission '
        'does not reject a candidate. If this bounded selection cannot represent your intended highlights, '
        'use overflow. The final answer will see the full original input and every legal resource.\n\n'
        'Current legal resources:\n'+resource_text(candidates,library,catalog)+
        '\n\nActual output schema:\n'+json.dumps(selection_schema(candidates,catalog),ensure_ascii=False))
    return [dict(role='system',content=(
        'Select relevant evidence IDs for the current task. Original messages are complete quoted source '
        'data; their final-answer formatting instructions do not govern this highlighting stage.')),
        dict(role='user',content='Original method messages as complete quoted data:\n'+
             json.dumps(packet.original_context,ensure_ascii=False)+'\n\nCURRENT HIGHLIGHT TASK:\n'+instruction)]


def run(packet, session):
    checkpoint = session.checkpoint()
    candidates, library, catalog, overflow = prepare(packet)
    if packet.model_input is not None or not candidates:
        return AgentProposal('A1',VARIANT,packet.input_hash,'unsupported',None,
                             cost=session.cost_since(checkpoint))
    resources = resource_text(candidates,library,catalog)
    trace = dict(control_identity=VARIANT,resource_hash=digest(resources),selection=None,
        schema_invalid=False,semantic_invalid=False,overflow=overflow,method_score='not_scored',
        semantic_result='unavailable',inference_started=False)

    def unavailable(reason, failure_type, schema_invalid=False):
        trace.update(failure_type=failure_type,schema_invalid=schema_invalid)
        return AgentProposal('A1',VARIANT,packet.input_hash,'partial',None,unresolved=[reason],
            checks=[dict(type='format_validation',name='highlighting_and_native_format',passed=not schema_invalid)],
            cost=session.cost_since(checkpoint),trace=trace)

    if overflow:
        return unavailable('Complete source catalog exceeds the shared bound; no truncation','evidence_limit')
    schema = selection_schema(candidates,catalog)
    raw = session.generate(highlight_messages(packet,candidates,library,catalog),schema,
        **policy('highlight'),stage='A1_highlight_control:select',decoding_revision=config()['decoding_revision'])
    trace.update(raw_selection=raw,inference_started=True)
    try:
        selection = parse_audit(raw,schema)
    except (ValueError,TypeError,ValidationError) as error:
        return unavailable(str(error),'highlight_schema_invalid',True)
    trace['selection'] = selection
    trace['missing_candidates'] = [key for key in candidates if key not in selection['highlights']]
    if selection['selection_status']=='overflow':
        trace['overflow']=True
        return unavailable('Model declared highlighting capacity insufficient','highlight_capacity_overflow')
    highlights = [dict(candidate=candidates[cid],references=[dict(evidence_id=eid,
        source_kind=catalog[eid]['kind'],**reference(packet,catalog,eid)) for eid in ids])
        for cid,ids in selection['highlights'].items()]
    trace['resolved_highlights']=highlights
    instruction = (
        'Answer the complete original question in its original JSON format, including every auxiliary field. '
        'Use the complete legal resources below. Selected source highlights are relevance hints, not '
        'support verdicts or verified medical knowledge. Keep Q patient evidence separate from E context; '
        'missing patient facts remain unknown. You may retain or change the answer according to the input. '
        'All candidates and sources remain available, including those not highlighted.\n\n'
        'Current legal resources:\n'+resources+'\n\nSelected exact source highlights:\n'+
        json.dumps(highlights,ensure_ascii=False))
    raw_answer = session.generate(messages_with_instruction(packet,instruction),packet.answer_schema,
        **policy('answer'),stage='A1_highlight_control:native_answer')
    trace['raw_response']=raw_answer
    try:
        native = native_json(raw_answer,packet.answer_schema)
    except (ValueError,TypeError,ValidationError) as error:
        return unavailable(str(error),'native_schema_invalid',True)
    trace['semantic_result']='native_answer_available'
    return AgentProposal('A1',VARIANT,packet.input_hash,
        'partial' if trace['missing_candidates'] else 'supported',native,
        checks=[dict(type='program_execution',name='selected_ids_resolve_to_current_source_spans'),
                dict(type='model_assessment',name='relevance_selection_not_entailment'),
                dict(type='format_validation',name='native_format',passed=True)],
        cost=session.cost_since(checkpoint),trace=trace)
