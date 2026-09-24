"""Selected F control. A new qualified-view candidate is separately versioned."""
from cf_moa.contracts import AgentProposal
from cf_moa.tools.adapters import native_json
from cf_moa.tools.legacy import r5_module
from jsonschema import ValidationError
from copy import deepcopy
import json

from cf_moa.tools.adapters import messages_with_instruction
from cf_moa.tools.provenance import validate_claim
from cf_moa.tools.validated_views import views, align_answer
from cf_moa.tools.experiment_config import new_policy

LEGACY_VARIANT = 'legacy_f_equal_nli_paths_else_full_maj5'
VIEW_VARIANT = 'qualified_code_views_original_adjudication_v1'


def run_legacy(packet, session):
    checkpoint = session.checkpoint()
    if packet.native_input['answer_format'] not in ('single', 'robustness_single', 'relation'):
        return AgentProposal('A5', LEGACY_VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=['Outside the selected F native formats'], cost=session.cost_since(checkpoint))
    if isinstance(packet.original_context, str):
        return AgentProposal('A5', LEGACY_VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=['Selected F requires the original messages, not a reserialized prompt'],
            cost=session.cost_since(checkpoint))

    def score(messages, seed):
        return session.score(messages=messages, codes=['A', 'B'], seed=seed, stage='A5:F_score')

    def generate(messages, schema, seed, temperature, max_tokens):
        return session.generate(messages, schema, seed, temperature, max_tokens, stage='A5:F_generate')

    result = r5_module().optimize(packet.native_input, packet.original_context,
        packet.baseline_response, packet.answer_schema, score, generate)
    try:
        native = native_json(result['raw_response'], packet.answer_schema)
        valid, error = True, None
    except (ValueError, TypeError, ValidationError) as exc:
        native, valid, error = None, False, str(exc)
    return AgentProposal('A5', LEGACY_VARIANT, packet.input_hash,
        'supported' if valid else 'partial', native,
        claims=[dict(claim_id='A5:F_decision', kind='general_knowledge',
            scope='current_native_task', provenance='full_input_model_decisions',
            stability_is_not_correctness=True)],
        unresolved=[] if valid else [error],
        checks=[dict(type='model_assessment', name=result['route']),
                dict(type='format_validation', passed=valid)],
        cost=session.cost_since(checkpoint), trace=result)


def run_views(packet,session):
    """One candidate only: intact anchor + two code views + at most one adjudication."""
    checkpoint = session.checkpoint()
    qualified,reason = views(packet)
    if not qualified:
        legacy = run_legacy(packet,session)
        legacy.trace = dict(fallback_reason=reason,requested_candidate=VIEW_VARIANT,
            qualified_views=[],result=legacy.trace)
        return legacy  # Retain F's real identity, not a fictitious successful new view.
    observed = []
    for view in [dict(view_id='complete_anchor',messages=packet.original_context,
                       schema=packet.answer_schema,mapping=None),*qualified]:
        raw = session.generate(view['messages'],view['schema'],**new_policy('A5:view'),stage='A5:'+view['view_id'])
        try:
            value = native_json(raw,view['schema'])
            aligned = align_answer(value,view['mapping']) if view['mapping'] else deepcopy(value)
            # Mapping back must satisfy the full original schema, including Errors.
            native_json(json.dumps(aligned,ensure_ascii=False),packet.answer_schema)
            error = None
        except (ValueError,TypeError,ValidationError) as exc:
            value,aligned,error = None,None,str(exc)
        observed.append(dict(view_id=view['view_id'],raw_response=raw,native_response=value,
            aligned_response=aligned,mapping=view['mapping'],error=error,
            qualification=view.get('checks',dict(complete_original_anchor=True))))
        if error:
            # The new candidate obeys the experiment's first-error policy even
            # inside one expert invocation. Preserve the failed view; do not
            # launch more views or an adjudication after a schema failure.
            return AgentProposal('A5',VIEW_VARIANT,packet.input_hash,'partial',None,
                unresolved=[view['view_id']+': '+error],
                checks=[dict(type='format_validation',name='view_native_schema',passed=False)],
                cost=session.cost_since(checkpoint),trace=dict(route='stopped_on_invalid_view',
                    qualification_reason=reason,views=observed,adjudication=None,
                    inference_started=True,failure_type='view_schema_invalid',
                    semantic_result='unavailable',method_score='not_scored',
                    stability_is_not_correctness=True,external_retrieval=False))
    choices = [r['aligned_response'].get('answer_choice') if r['aligned_response'] else None for r in observed]
    semantic = [{k:v for k,v in r['aligned_response'].items() if k!='step_by_step_thinking'}
                if r['aligned_response'] is not None else None for r in observed]
    agreement = all(value is not None for value in semantic) and all(value==semantic[0] for value in semantic[1:])
    unresolved = [r['view_id']+': '+r['error'] for r in observed if r['error']]
    claims = [dict(claim_id='A5:views',kind='hypothetical_probe',scope='output_code_presentation_only',
        provenance='qualified_bijective_readouts_of_unchanged_input',semantic_answers=choices,
        agreement=agreement,stability_is_not_correctness=True)]
    adjudication = None
    if agreement:
        native = observed[0]['aligned_response']
        route = 'agreement_use_full_anchor'
    else:
        from cf_moa.agents.a1_support_completion import obj, array, TEXT, REFERENCE
        schema = obj(dict(native_answer=packet.answer_schema,disagreement_basis=array(REFERENCE),reason=TEXT))
        instruction = (
            'Resolve the following readout disagreement against the complete original text above. '
            'Each response came from the same input with a different output code table; aligned_response '
            'is already in the original semantic codes. They are fallible model outputs, not new patient '
            'facts. Locate the decisive original patient fact, document statement or mapping error with '
            'an exact source ref, quote and character offset. Preserve all original facts and all required '
            'auxiliary fields in native_answer. Do not choose by majority, stability, or a rule to keep '
            'or flip the old answer. This is the only adjudication.\n\nReadouts:\n'+
            json.dumps(observed,ensure_ascii=False))
        from cf_moa.tools.provenance import sources
        instruction += '\n\nOriginal visible source map:\n'+json.dumps(sources(packet),ensure_ascii=False)
        raw = session.generate(messages_with_instruction(packet,instruction),schema,
            **new_policy('A5:adjudication'),stage='A5:original_adjudication')
        try:
            adjudication = native_json(raw,schema)
            native = adjudication['native_answer']
            for index,ref in enumerate(adjudication['disagreement_basis']):
                try:
                    claims.append(validate_claim(packet,dict(claim_id=f'A5:basis:{index}',
                        kind='patient_fact' if ref['ref']=='Q' else 'general_knowledge',
                        references=[ref],scope='current_original_question')))
                except ValueError as error:
                    unresolved.append('Adjudication source binding: '+str(error))
            if not adjudication['disagreement_basis']:
                unresolved.append('Adjudication provided no located source basis')
        except (ValueError,TypeError,ValidationError) as error:
            native = None
            unresolved.append('Adjudication format failed: '+str(error))
        adjudication = dict(raw_response=raw,parsed=adjudication)
        route = 'one_original_text_adjudication'
    return AgentProposal('A5',VIEW_VARIANT,packet.input_hash,
        'supported' if native is not None and not unresolved else 'partial',native,
        claims=claims,requested_changes=[dict(change_id='A5:readout',action='native_readout_proposal',
            claim_ids=[c['claim_id'] for c in claims],scope='current_original_question')],
        unresolved=unresolved,checks=[dict(type='program_execution',name='view_bijection_and_original_preservation'),
            dict(type='model_assessment',name='agreement_or_single_adjudication',agreement=agreement),
            dict(type='format_validation',passed=native is not None)],cost=session.cost_since(checkpoint),
        trace=dict(route=route,qualification_reason=reason,views=observed,adjudication=adjudication,
            stability_is_not_correctness=True,external_retrieval=False))
