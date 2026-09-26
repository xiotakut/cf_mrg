"""Shared capabilities for the all-tools single-agent control, not expert votes."""
import json
from copy import deepcopy

import jsonschema

from cf_moa.agents.a1_coded_coverage import prepare as evidence_resources
from cf_moa.agents.a2_support_revision import applicable as medication_applicable
from cf_moa.agents.a3_contrastive_comparison import applicable as catalog_applicable, resources as catalog_resources
from cf_moa.agents.a4_intervention_execution import capability as physiology_capability, TOOL as PHYSIOLOGY
from cf_moa.contracts import reject_metadata
from cf_moa.tools.adapters import native_json
from cf_moa.tools.legacy import r123_module, r4_modules
from cf_moa.tools.validated_views import views, align_answer
from cf_moa.tools.schema_compat import OutputSchemaError

EMPTY = dict(type='object',properties={},required=[],additionalProperties=False)
ARGUMENT_DECODER = 'bounded_single_agent_tool_whitespace_16_r2'


def argument_grammar(schema):
    """Bound only structural whitespace in this control's argument requests."""
    if set(schema.get('properties', {})) not in ({'facts'}, {'intervention'}):
        raise ValueError('Tool argument decoder requires a facts or intervention contract')
    import xgrammar as xgr
    original = str(xgr.Grammar.from_json_schema(schema))
    whitespace = r'[ \n\t]*'
    if whitespace not in original:
        raise ValueError('Installed xgrammar structural whitespace layout changed')
    return original.replace(whitespace, r'[ \n\t]{0,16}')


def stable_rule_result(result):
    """The original rule kernel may insert fact keys from a Python set."""
    result = deepcopy(result)
    result['facts'] = {key: result['facts'][key] for key in sorted(result['facts'])}
    return result


class ToolSemanticError(ValueError):
    """A valid argument object cannot designate the requested current action."""


def resources(packet, method):
    candidates, library, evidence, overflow = evidence_resources(packet)
    finite_candidate_audit = bool(candidates) and packet.model_input is None
    result = dict(candidates=candidates, knowledge=library,
        evidence_ids=evidence if finite_candidate_audit else {},
        evidence_index_scope=('same complete finite-candidate evidence-ID table' if finite_candidate_audit
            else 'finite-candidate audit not applicable; all original sources remain in the unchanged native messages'),
        current_initial_response=dict(native_answer=packet.baseline_answer,raw_response=packet.baseline_response,
            provenance='current-input model response, not patient evidence'),
        evidence_index_exceeds_A1_bound=overflow,
        resource_scope='Complete current legal sources; index overflow never deletes source content')
    if catalog_applicable(packet):
        _, priors = catalog_resources(method)
        result['catalog_log_priors'] = priors
    if physiology_capability(packet)[0]:
        with r4_modules() as (head, _):
            result['declared_physiology'] = dict(model_input=packet.model_input,
                original_author_model_context=head.request(packet.model_input,packet.question,'patch'))
    return result


def capabilities(packet):
    result = {}
    if medication_applicable(packet):
        result['medication_rules_71'] = 'Evaluate the adopted finite medication rules from source-indexed patient facts; preserve unknown and independent support paths.'
    if catalog_applicable(packet):
        result['diagnosis_catalog_49'] = 'Obtain original-backbone candidate log probabilities in six fixed orders and their original prior calibration.'
    if physiology_capability(packet)[0]:
        result[PHYSIOLOGY] = 'Execute a typed local action on the complete explicitly supplied physiological model, initial state and schedule.'
    qualified, _ = views(packet)
    for view in qualified:
        result[view['view_id']] = 'Reanswer the same complete native task under this qualified bijective output-code mapping; map the full answer back afterward.'
    return result


def argument_contract(packet, name):
    if name not in capabilities(packet):
        raise ValueError('Tool not available for the complete current input: '+name)
    if name=='medication_rules_71':
        request=r123_module('r2_positive_facts').build_request(packet.native_input)
        return request['schema'], request['messages']
    if name==PHYSIOLOGY:
        with r4_modules() as (head, _):
            schema=dict(type='object',properties=dict(intervention=head.ACTION),
                required=['intervention'],additionalProperties=False)
            return schema, head.request(packet.model_input,packet.question,'patch')
    return EMPTY, []


def execute_tool(packet, method, name, arguments, session, *, view_policy):
    """Use original kernels; no A1/A2/A3/A4/A5 proposal entry is delegated to."""
    reject_metadata(arguments)
    schema,_=argument_contract(packet,name)
    jsonschema.validate(arguments,schema)
    if name=='medication_rules_71':
        result=session.tool(name,r123_module('r2_condition_head').resolve,
                            packet.native_input,packet.baseline_answer,arguments)
        return dict(kind='program_execution_conditional_on_model_facts',scope=name,result=stable_rule_result(result))
    if name=='diagnosis_catalog_49':
        catalog,priors=catalog_resources(method)
        kernel=r123_module('r3_catalog_distribution_head')
        codes=list(r123_module('r3_ontology_head').CODES[:len(catalog)])
        def score():
            orders=kernel.orders(catalog)
            raw=[session.score(**kernel.request(packet.native_input,packet.original_context,order),
                codes=codes,seed=42,stage='single_agent:catalog_scores') for order in orders]
            calibrated=kernel.calibrate(raw,priors)
            return dict(catalog=catalog,orders=orders,raw_scores=raw,log_priors=priors,
                calibrated_scores=calibrated,aggregate=kernel.aggregate(catalog,orders,calibrated))
        return dict(kind='model_scoring_and_program_mapping',scope=name,result=session.tool(name,score))
    if name==PHYSIOLOGY:
        with r4_modules() as (head, _):
            query=head.query_from_question(packet.question)
            try:
                plan=head.compile_edit(packet.model_input,arguments['intervention'],query)
            except (ValueError,KeyError,TypeError) as error:
                raise ToolSemanticError(str(error)) from error
            result=session.tool(name,head.v1.project,packet.model_input,plan,'patch')
        if result.get('route')=='inline_fallback':
            raise ToolSemanticError(result.get('reason','Supplied action did not execute'))
        return dict(kind='program_execution',scope=name,compiled_plan=plan,result=result)
    view=next(view for view in views(packet)[0] if view['view_id']==name)
    raw=session.generate(view['messages'],view['schema'],**view_policy,stage='single_agent:'+name)
    try:
        native=native_json(raw,view['schema'])
    except (ValueError,TypeError,jsonschema.ValidationError) as error:
        raise OutputSchemaError(str(error)) from error
    return dict(kind='model_readout_not_invariance_proof',scope=name,
        mapping=view['mapping'],checks=view['checks'],original_input_hash=view['original_input_hash'],
        raw_response=raw,aligned_native_answer=align_answer(native,view['mapping']))
