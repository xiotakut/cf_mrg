"""Explicit research entry: adopted five operations plus F-local selection.

A1/A2 share the adopted rule engine. No global model rewrites a rule,
catalogue, solver or passthrough answer. Old defaults are not changed.
"""
from copy import deepcopy

from jsonschema import ValidationError, validate

from cf_moa.agents import a5_candidate_verify, a5_robust_readout
from cf_moa.contracts import digest, reject_metadata
from cf_moa.controller import baseline_native, minimal_operations, strong_legacy

VARIANTS = {
    'strong_B': minimal_operations.VARIANT,
    'candidate_only': 'cf_moa_rcv_candidate_only_v1',
    'candidate_with_rationales': 'cf_moa_rcv_rationales_v1',
    'joint_selector': 'cf_moa_rcv_joint_selector_control_v1',
    'pool_old_plus_three': 'cf_moa_rcv_old_pool_plus_three_control_v1',
}
_MISSING = object()


def profile_role(packet):
    component, predicate = strong_legacy.select(packet)
    return {'original_catalog_predicate': 'catalog',
            'original_rule_predicate': 'facts',
            'complete_supplied_model_capability': 'a4'}.get(predicate, 'readout')


def _complete_old_interface(packet, native, trace, component):
    """Use the already adopted deterministic rule/catalogue native interface."""
    if native is None:
        return None, None
    candidate = deepcopy(native)
    if component == 'legacy_R1' and not isinstance(native, dict):
        result = trace.get('legacy_result', {})
        if result.get('used_original'):
            # The old passthrough must already carry a complete initial response.
            raise ValueError('Passthrough requires its complete original native response')
        candidate = dict(step_by_step_thinking=baseline_native._execution_summary(result),
                         answer_choice=deepcopy(native))
    try:
        validate(candidate, packet.answer_schema)
    except ValidationError as error:
        return None, dict(failure_type='baseline_native_schema_invalid', message=error.message,
                         candidate_native_answer=candidate)
    return candidate, None


def run(packet, session, *, method, mode='candidate_with_rationales', seed=42,
        initial_native=_MISSING, saved_f_proposal=None, saved_base=None):
    """Run/reuse B once, then select only inside the adopted F branch.

    ``saved_base`` is an already accepted complete B interface, never a stand-in
    for F's candidate pool. Session costs are measured once outside both phases;
    saved costs are separately labelled and never added to physical new usage.
    """
    if mode not in VARIANTS or type(seed) is not int:
        raise ValueError('Unknown research mode or noninteger verification seed')
    outer = session.checkpoint()
    component, predicate = strong_legacy.select(packet)
    verification = None
    inherited = None
    interface_failure = None
    f_proposal = None
    if component == 'F':
        if saved_f_proposal is None:
            f_proposal = a5_robust_readout.run_legacy(packet, session).to_dict()
        else:
            reject_metadata(saved_f_proposal)
            a5_candidate_verify._bind(packet, saved_f_proposal)
            f_proposal = deepcopy(saved_f_proposal)
            inherited = deepcopy(f_proposal.get('cost', {}))
        native = deepcopy(f_proposal['native_proposal'])
        base_native = deepcopy(native)
        trace = deepcopy(f_proposal['trace'])
        operations = minimal_operations.operation_record(packet, component, predicate)
        original_variant = f_proposal['variant']
    elif saved_base is not None:
        if saved_base.get('input_hash') != packet.input_hash:
            raise ValueError('Saved non-F B belongs to a different complete input')
        if saved_base.get('request_id') != packet.request_id:
            raise ValueError('Saved non-F B has a different request handle')
        bound = saved_base.get('base_answer_ref')
        if bound is not None and digest(saved_base['native_answer']) != bound:
            raise ValueError('Saved non-F B native response changed')
        operations = deepcopy(saved_base.get('operations'))
        if operations is None:
            raise ValueError('Saved non-F B needs its original operation/route record')
        if (operations['selected_component'], operations['capability_predicate']) != (component, predicate):
            raise ValueError('Saved non-F B route differs from unchanged capability routing')
        native = deepcopy(saved_base['native_answer'])
        base_native = deepcopy(native)
        trace = deepcopy(saved_base.get('trace', {}))
        original_variant = saved_base.get('original_component_variant', saved_base['variant'])
        inherited = deepcopy(saved_base.get('cost', {}))
    else:
        kwargs = {} if initial_native is _MISSING else dict(initial_native=initial_native)
        old = minimal_operations.run(packet, session, method=method,
                                     f_disagreement_reanswer=False, **kwargs)
        native, interface_failure = _complete_old_interface(
            packet, old['native_proposal'], old['trace'], component)
        base_native = deepcopy(native)
        trace, operations = deepcopy(old['trace']), deepcopy(old['operations'])
        original_variant = old['original_component_variant']
    base_cost = session.cost_since(outer)
    verification_start = session.checkpoint()
    if component == 'F' and mode != 'strong_B':
        operation = a5_candidate_verify
        if mode == 'joint_selector':
            from cf_moa.agents import a5_joint_selector as operation
        elif mode == 'pool_old_plus_three':
            from cf_moa.agents import a5_pool_expansion_control as operation
        verification = operation.run(packet, session,
            base_native_answer=base_native, saved_proposal=f_proposal,
            include_rationales=mode != 'candidate_only', config={'seed': seed})
        native = deepcopy(verification['native_answer'])
    cost = session.cost_since(outer)
    return dict(request_id=packet.request_id, input_hash=packet.input_hash,
        variant=VARIANTS[mode], research_mode=mode, native_answer=deepcopy(native),
        native_proposal=deepcopy(native), native_valid=native is not None,
        base_native_answer=base_native, base_answer_ref=digest(base_native) if base_native is not None else None,
        original_component_variant=original_variant, operations=operations,
        trace=trace, f_proposal=f_proposal, verification=verification,
        interface_failure=interface_failure, cost=cost,
        stage_costs=dict(adopted_B=base_cost, verification=session.cost_since(verification_start)),
        reused_B_cost=inherited, reused_B_cost_is_new_physical_usage=False,
        f_disagreement_reanswer=False, global_generation_aggregator=False)
