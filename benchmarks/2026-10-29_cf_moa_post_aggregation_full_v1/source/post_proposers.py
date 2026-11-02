"""Frozen-component proposers for the first post-aggregation migration pilot.

This entry reuses complete native results. It does not claim new expert inference.
Each role checks only its own capability; the global selector is never called.
"""
from copy import deepcopy

from cf_moa.agents.a4_intervention_execution import capability
from cf_moa.contracts import digest, reject_metadata
from cf_moa.controller.minimal_operations import rule_operations
from cf_moa.tools.legacy import r123_module

ROLES = ('A1', 'A2', 'A3', 'A4', 'A5')
VARIANT = 'frozen_functional_proposals_v1'


def collect_cached(packet, *, method, c0_native, components):
    """Complete all five role records using explicitly bound component snapshots."""
    events, proposals, shared = [], {}, {}
    c0 = deepcopy(c0_native)
    reject_metadata(c0)
    c0_ref = digest(c0)
    capabilities = {}

    def saved(role):
        record = components[role]
        if (record['input_hash'] != packet.input_hash or record['method'] != method
                or record['role'] != role or record['request_id'] != packet.request_id):
            raise ValueError('Frozen component identity mismatch: ' + role)
        if record['native_hash'] != digest(record['native_answer']):
            raise ValueError('Frozen complete native response changed: ' + role)
        reject_metadata(record['native_answer'])
        return deepcopy(record)

    def rule():
        if 'rule' not in shared:
            supported = r123_module('r2_program_head').eligible(packet.native_input)
            capabilities['rule_eligible'] = supported
            record = saved('A2') if supported else None
            operations = None
            if record is not None:
                result = record['trace']['legacy_result']
                operations = rule_operations(packet.native_input, packet.baseline_answer, result)
                native = record['native_answer']
                value = native.get('answer_choice') if isinstance(native, dict) else native
                if value is not None and digest(value) != digest(result['answer']):
                    raise ValueError('Rule native response differs from its executed result')
            shared['rule'] = (supported, record, operations)
        return shared['rule']

    for role in ROLES:
        events.append(dict(event='proposer_started', role=role))
        evidence, record = {}, None
        if role in ('A1', 'A2'):
            supported, record, operations = rule()
            if supported:
                evidence = dict(shared_rule_execution=True, operation=operations[role],
                    special_policy=operations.get('special_policy'),
                    assembly_authority=operations['output_authority'])
        elif role == 'A3':
            supported = packet.native_input['answer_format'] == 'diagnosis'
            capabilities['diagnosis'] = supported
            if supported:
                record = saved(role)
                result = record.get('trace', {}).get('legacy_result', {})
                details = result.get('details', {})
                evidence = {k: deepcopy(details[k]) for k in ('per_order', 'majority_vote', 'mean_probability') if k in details}
        elif role == 'A4':
            supported, reason = capability(packet)
            capabilities['complete_model_capability'] = supported
            evidence = dict(capability_reason=reason)
            if supported:
                record = saved(role)
        else:
            supported = (packet.native_input['answer_format'] in ('single', 'robustness_single', 'relation')
                         and not isinstance(packet.original_context, str))
            capabilities['F_eligible'] = supported
            if supported:
                record = saved(role)
                trace = record.get('trace', {})
                evidence = {k: deepcopy(trace[k]) for k in ('route', 'calls', 'seeds', 'vote_counts', 'selected_index') if k in trace}
        native = deepcopy(record['native_answer']) if supported else deepcopy(c0)
        proposal = dict(role=role, input_hash=packet.input_hash, tool_applicable=supported,
            execution_mode='cached_native' if supported else 'C0_fallback_no_tool_execution',
            execution_status=record['status'] if supported else 'unsupported',
            native_answer=native, native_hash=digest(native), evidence=evidence,
            shared_origin='A1_A2_shared_rule' if supported and role in ('A1', 'A2') else (role if supported else 'C0'),
            source_ref=record['source_ref'] if supported else dict(kind='current_C0', native_hash=c0_ref))
        proposals[role] = proposal
        events.append(dict(event='proposer_finished', role=role))
    body = dict(variant=VARIANT, method=method, request_id=packet.request_id,
        input_hash=packet.input_hash, proposals=proposals, capabilities=capabilities,
        c0_native=c0, c0_hash=c0_ref, events=events,
        new_expert_model_calls=0, shared_rule_snapshot_loads=int(capabilities['rule_eligible']))
    return dict(body, pool_hash=digest(body))


def validate_pool(packet, pool):
    if pool['input_hash'] != packet.input_hash or pool['request_id'] != packet.request_id:
        raise ValueError('Pool belongs to a different input')
    if tuple(pool['proposals']) != ROLES:
        raise ValueError('All five ordered proposal records must be present')
    finished = [e['role'] for e in pool['events'] if e['event'] == 'proposer_finished']
    if finished != list(ROLES):
        raise ValueError('Five proposers must finish before aggregation')
    if digest({k: v for k, v in pool.items() if k != 'pool_hash'}) != pool['pool_hash']:
        raise ValueError('Frozen pool changed')
    for proposal in pool['proposals'].values():
        if digest(proposal['native_answer']) != proposal['native_hash']:
            raise ValueError('Native candidate changed')


def visible_pool(pool):
    """No source paths, old selection, scores, or evaluation metadata enter prompts."""
    natives, roles = {}, []
    for proposal in pool['proposals'].values():
        ref = proposal['native_hash']
        natives.setdefault(ref, deepcopy(proposal['native_answer']))
        roles.append({k: deepcopy(proposal[k]) for k in
            ('role', 'tool_applicable', 'execution_mode', 'execution_status', 'native_hash', 'shared_origin', 'evidence')})
    natives.setdefault(pool['c0_hash'], deepcopy(pool['c0_native']))
    view = dict(roles=roles, complete_native_responses=natives, C0_native_ref=pool['c0_hash'],
        capabilities=deepcopy(pool['capabilities']),
        duplicates='Equal native_hash values share a response. C0 fallbacks and A1/A2 are not independent votes.')
    reject_metadata(view)
    return view
