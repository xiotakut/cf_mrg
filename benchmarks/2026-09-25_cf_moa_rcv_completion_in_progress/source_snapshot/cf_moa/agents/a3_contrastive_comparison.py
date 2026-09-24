"""Public-catalog control; optional editing is a separately named experiment."""
import json

from cf_moa.contracts import AgentProposal, digest
from cf_moa.tools.adapters import native_json, messages_with_instruction
from cf_moa.tools.bounded_edits import editable_spans, apply_edit
from cf_moa.tools.experiment_config import new_policy
from jsonschema import ValidationError
from cf_moa.tools.legacy import R123, r123_module

VARIANT = 'legacy_catalog_six_orders_calibrated_majority'
EDIT_VARIANT = 'fixed_catalog_bounded_evidence_delta_v1'
IMPLEMENTATION_REVISION = 'bounded_edit_readiness_repair_20260922'


def resources(method):
    if method not in ('M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'):
        raise ValueError('No selected historical prior for this method')
    return (json.loads((R123 / 'catalog.json').read_text()),
            json.loads((R123 / (method.lower() + '_log_priors.json')).read_text()))


def applicable(packet):
    return (packet.native_input['answer_format'] == 'diagnosis'
            and 'diagnosis_catalog_49' in packet.available_tools)


def run(packet, session, *, method, arm='legacy'):
    if arm == 'bounded_edit':
        return run_bounded_edit(packet, session, method=method)
    if arm != 'legacy':
        raise ValueError('Unknown A3 arm; legacy is the default and bounded_edit is opt-in')
    checkpoint = session.checkpoint()
    if not applicable(packet):
        return AgentProposal('A3', VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=['Outside the fixed public diagnosis catalog capability'],
            cost=session.cost_since(checkpoint))
    catalog, priors = resources(method)
    kernel = r123_module('r3_catalog_distribution_head')
    codes = list(r123_module('r3_ontology_head').CODES[:len(catalog)])
    raw_scores = []

    def score_codes(**request):
        scores = session.score(**request, codes=codes, seed=42, stage='A3:catalog')
        raw_scores.append(scores)
        return scores

    result = kernel.optimize_calibrated(packet.native_input, packet.original_context,
        packet.baseline_answer, catalog, priors, score_codes)
    return AgentProposal('A3', VARIANT, packet.input_hash,
        'partial' if result['used_original'] else 'supported', result['answer'],
        claims=[dict(claim_id='A3:catalog_preference', kind='general_knowledge',
            candidate=result['answer'], provenance='public_catalog_and_current_context_model_scores',
            scope='supplied_49_disease_catalog', score_contract='same_model_same_codes_six_fixed_orders',
            clinical_causal_effect=False)],
        requested_changes=[dict(change_id='A3:select', action='candidate_preference',
            candidate=result['answer'], claim_ids=['A3:catalog_preference'])],
        unresolved=[result['error']] if result.get('error') else [],
        checks=[dict(type='model_assessment', name='catalog_candidate_scoring'),
                dict(type='program_execution', name='semantic_mapping_prior_and_vote')],
        cost=session.cost_since(checkpoint), trace=dict(legacy_result=result,
            catalog=catalog, raw_scores=raw_scores, native_canonical_mapping_unchanged=True))


def _invalid_output(packet, session, checkpoint, legacy, pair, margin, *,
                    stage, raw, editor_raw, probes, rejected, error):
    """Keep the failing response and its cost; never turn it into a legacy success."""
    event = session.calls[-1].get('event', {})
    return AgentProposal('A3', EDIT_VARIANT, packet.input_hash, 'partial', None,
        unresolved=[str(error)],
        checks=[dict(type='format_validation', name=stage, passed=False)],
        cost=session.cost_since(checkpoint),
        trace=dict(implementation_revision=IMPLEMENTATION_REVISION,
            legacy_result=legacy.trace, editor_raw=editor_raw, probes=probes,
            rejected_edits=rejected, raw_response=raw,
            original_pair=pair, original_margin=margin, default_enabled=False,
            schema_invalid=True, semantic_invalid=bool(rejected),
            inference_started=True, semantic_result='unavailable', method_score='not_scored',
            failure_type='output_truncation' if event.get('finish_reason') == 'length' else 'output_schema',
            failure_stage=stage, failure_call_ordinal=len(session.calls)-1,
            error_type=type(error).__name__, error=str(error)))


def _parse_output(raw, schema, session):
    if session.calls[-1].get('event', {}).get('finish_reason') == 'length':
        raise ValueError('Generation ended at its fixed output token limit')
    return native_json(raw, schema)


def run_bounded_edit(packet,session,*,method):
    checkpoint = session.checkpoint()
    legacy = run(packet,session,method=method,arm='legacy')
    if legacy.applicability=='unsupported' or legacy.trace['legacy_result']['used_original']:
        legacy.trace['requested_arm'] = EDIT_VARIANT
        return legacy
    catalog,_ = resources(method)
    spans = editable_spans(packet)
    if not spans:
        legacy.trace.update(requested_arm=EDIT_VARIANT,edit_unavailable='No bounded evidence spans')
        return legacy
    kernel = r123_module('r3_catalog_distribution_head')
    codes = list(r123_module('r3_ontology_head').CODES[:len(catalog)])
    probabilities = legacy.trace['legacy_result']['details']['mean_probabilities']
    pair = sorted(catalog,key=lambda name:probabilities[name],reverse=True)[:2]
    original_scores = legacy.trace['raw_scores'][0]
    a_code,b_code = (codes[catalog.index(name)] for name in pair)
    margin = original_scores[a_code]-original_scores[b_code]
    schema = dict(type='object',properties=dict(edits=dict(type='array',maxItems=2,items=dict(
        type='object',properties=dict(span_id=dict(type='string',enum=list(spans)),
            operation=dict(type='string',enum=['delete','explicit_negation']),replacement=dict(type='string')),
        required=['span_id','operation','replacement'],additionalProperties=False))),required=['edits'],additionalProperties=False)
    instruction = (
        'Propose at most two independent local evidence probes to distinguish the two fixed candidates. '
        'Use only the supplied span IDs. Deletion means absence of that statement; it is distinct from '
        'explicit negation. For deletion use an empty replacement. For explicit negation preserve all '
        'other characters: insert "not ", "no ", or "without ", change positive to negative, or prepend '
        '"It is not the case that " to the exact original span. Do not rewrite the target question. '
        'These probes do not establish clinical feasibility and must not become original patient facts. '
        'Return the edits JSON; an empty list is allowed.\nFixed candidates:\n'+json.dumps(pair)+
        '\nAllowed original spans:\n'+json.dumps(spans,ensure_ascii=False))
    raw = session.generate(messages_with_instruction(packet,instruction),schema,
        **new_policy('A3:editor'),stage='A3:edit_proposal')
    rejected,probes = [],[]
    try:
        edits = _parse_output(raw,schema,session)['edits']
    except (ValueError,TypeError,ValidationError) as error:
        return _invalid_output(packet,session,checkpoint,legacy,pair,margin,
            stage='A3:edit_proposal',raw=raw,editor_raw=raw,probes=probes,
            rejected=rejected,error=error)
    seen=set()
    for edit in edits:
        try:
            if edit['span_id'] in seen:
                raise ValueError('Only one probe per original span')
            seen.add(edit['span_id'])
            probe,record = apply_edit(packet,edit)
        except ValueError as error:
            rejected.append(dict(edit=edit,reason=str(error)))
            continue
        request = kernel.request(probe.native_input,probe.original_context,catalog)
        scores = session.score(**request,codes=codes,seed=42,stage='A3:fixed_catalog_probe')
        probe_margin = scores[a_code]-scores[b_code]
        probes.append(dict(**record,probe_question=probe.question,candidates=pair,
            code_mapping={a_code:pair[0],b_code:pair[1]},original_margin=margin,probe_margin=probe_margin,
            delta=margin-probe_margin,score_contract='raw log probabilities; same original catalog order and complete code set',
            raw_scores=scores,request_hash=digest(request)))
    native = legacy.native_proposal
    final_raw = None
    if probes:
        instruction = (
            'Answer the complete ORIGINAL patient question in its original JSON format. The following '
            'independent hypothetical probes used the same candidate identities and scoring contract. '
            'Their signed deltas measure model evidence sensitivity, not clinical causal effects, and '
            'are not proof of either diagnosis. Do not treat an edited finding as an original fact. '
            'Use the actual original evidence and public candidates; retain or change the answer '
            'only if supported, without a forced-flip rule.\nPublic catalog:\n'+json.dumps(catalog)+
            '\nProbe records:\n'+json.dumps(probes,ensure_ascii=False))
        final_raw = session.generate(messages_with_instruction(packet,instruction),packet.answer_schema,
            **new_policy('A3:answer'),stage='A3:original_native_answer')
        try:
            native = _parse_output(final_raw,packet.answer_schema,session)
        except (ValueError,TypeError,ValidationError) as error:
            return _invalid_output(packet,session,checkpoint,legacy,pair,margin,
                stage='A3:original_native_answer',raw=final_raw,editor_raw=raw,
                probes=probes,rejected=rejected,error=error)
    claims = [dict(claim_id=f'A3:probe:{i}',kind='hypothetical_probe',scope='current fixed catalog pair',
        candidates=pair,delta=probe['delta'],provenance=probe,clinical_causal_effect=False) for i,probe in enumerate(probes)]
    return AgentProposal('A3',EDIT_VARIANT,packet.input_hash,
        'supported' if native is not None and probes and not rejected else 'partial',native,
        claims=claims,requested_changes=[dict(change_id='A3:redecision',action='candidate_preference',
            claim_ids=[claim['claim_id'] for claim in claims],scope='original complete question')],
        unresolved=[r['reason'] for r in rejected]+([] if probes else ['No qualified probe; retained strong catalog result']),
        checks=[dict(type='program_execution',name='local_patch_and_identical_candidate_mapping'),
            dict(type='model_assessment',name='original_answer_informed_by_bounded_sensitivity')],
        cost=session.cost_since(checkpoint),trace=dict(legacy_result=legacy.trace,editor_raw=raw,
            probes=probes,rejected_edits=rejected,raw_response=final_raw,
            original_pair=pair,original_margin=margin,default_enabled=False,
            implementation_revision=IMPLEMENTATION_REVISION,
            schema_invalid=False,semantic_invalid=bool(rejected),
            inference_started=True,semantic_result='available',method_score='not_scored',
            failure_type='edit_binding_rejection' if rejected else None))
