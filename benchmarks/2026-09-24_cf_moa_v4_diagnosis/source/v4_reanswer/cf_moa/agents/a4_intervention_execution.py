"""Declared-model local interventions; no patient-model invention or HIV proxy."""
import math
import re

from cf_moa.contracts import AgentProposal, digest
from cf_moa.tools.legacy import R4, r4_modules
from cf_moa.tools.adopted import a4_adopted

VARIANT = 'frozen_physiology_v2_typed_patch'
TOOL = 'simglucose_frozen_120min_gsub'
FIELDS = {'params', 'initial_state', 'reset_auxiliary', 'horizon_min',
          'meal_announcements', 'factual_basal', 'factual_boluses'}


def capability(packet):
    if TOOL not in packet.available_tools or packet.model_input is None:
        return False, 'No explicitly supplied executable physiological model input'
    native = packet.model_input
    if set(native) != FIELDS:
        return False, 'Incomplete or undeclared physiological input fields'
    source = (R4.parent / 'physiology_probe/author/simglucose/patient/t1dpatient.py').read_text()
    parameters = set(re.findall(r'\bparams\.([A-Za-z][A-Za-z0-9_]*)', source)) - {'iloc', 'loc'}
    parameters |= {'Name', 'Vg'}
    if not parameters <= set(native['params']):
        return False, 'The supplied model parameter set is incomplete'
    for key in parameters - {'Name'}:
        value = native['params'][key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return False, 'Nonfinite or nonnumeric model parameter: ' + key
    state = native['initial_state']
    if len(state) != 13 or not all(type(x) in (int, float) and math.isfinite(x) for x in state):
        return False, 'All thirteen finite initial states must be supplied'
    aux = native['reset_auxiliary']
    if set(aux) != {'last_Qsto_mg', 'last_foodtaken_g', 'last_action', 'is_eating', 'planned_meal_g'}:
        return False, 'Complete initial auxiliary memory is required'
    if set(aux['last_action']) != {'CHO', 'insulin'} or type(aux['is_eating']) is not bool:
        return False, 'Malformed auxiliary memory'
    values = [aux['last_Qsto_mg'], aux['last_foodtaken_g'], aux['planned_meal_g'], *aux['last_action'].values()]
    if not all(type(x) in (int, float) and math.isfinite(x) for x in values):
        return False, 'Nonfinite auxiliary state'
    try:
        with r4_modules() as (head, executor):
            head.query_from_question(packet.question)
            executor.expand_schedule(native)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return False, str(error)
    return True, 'Complete explicitly supplied model within the frozen capability'


def run(packet, session, *, method=None):
    checkpoint = session.checkpoint()
    supported, reason = capability(packet)
    if not supported:
        return AgentProposal('A4', VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=[reason], cost=session.cost_since(checkpoint))
    adopted = a4_adopted(method)
    with r4_modules() as (head, _):
        def generate(messages, schema):
            return session.generate_adopted(messages, schema, adopted, stage='A4:compile_patch')
        result = session.tool(TOOL, head.optimize, packet.model_input,
                              packet.question, generate, arm='patch')
    executed = result['route'] == 'executed'
    claim = dict(claim_id='A4:execution', kind='tool_output' if executed else 'hypothetical_probe',
        scope=TOOL, supplied_model_hash=digest(packet.model_input),
        query=result.get('plan', {}).get('query'), answer=result['answer'],
        provenance='actual_selected_executor' if executed else 'model_inline_fallback',
        tool_succeeded=executed)
    return AgentProposal('A4', VARIANT, packet.input_hash,
        'supported' if executed else 'partial', result['answer'], claims=[claim],
        requested_changes=[dict(change_id='A4:readout', action='replace_with_model_conditional_readout',
            claim_ids=['A4:execution'], scope=TOOL)] if executed else [],
        unresolved=[] if executed else [result.get('reason', 'Execution did not produce a supported result')],
        checks=[dict(type='program_execution' if executed else 'model_assessment',
            name='actual_numerical_projection' if executed else 'inline_model_estimate')],
        cost=session.cost_since(checkpoint), trace=result)
