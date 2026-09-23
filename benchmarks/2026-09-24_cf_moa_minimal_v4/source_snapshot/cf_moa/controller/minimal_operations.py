"""Five operation labels over the adopted B computation; no global reanswer.

A1 and A2 are projections of one existing rule execution, not independent
models. Their operation sets are explanatory/ablatable records. The original
assembler remains authoritative even where the ordinary-set identity holds.
"""
from copy import deepcopy

from cf_moa.agents import a3_contrastive_comparison as a3
from cf_moa.agents import a4_intervention_execution as a4
from cf_moa.agents import a5_robust_readout as old_f
from cf_moa.agents import a5_premise as f_reanswer
from cf_moa.contracts import digest
from cf_moa.controller import baseline_native, legacy_router, strong_legacy
from cf_moa.tools.legacy import r123_module

VARIANT = 'adopted_B_five_operations_v1'
F_REANSWER_VARIANT = 'adopted_B_five_operations_f_ordinary_reanswer_v1'
RULE_DECOMPOSITION = 'shared_adopted_rule_add_remove_v1'
_MISSING = object()


def rule_operations(item, initial, result):
    """Project an already executed old result and check, never replace, assembly.

    Ineligible or failed extraction results have no invented state partition.
    None exclusivity, invalid initial answers, out-of-bank options, scoped
    rules, documented exceptions and UNKNOWN inheritance stay with old code.
    """
    options = result.get('options')
    record = dict(variant=RULE_DECOMPOSITION, shared_execution=True,
        additional_fact_extractions=0, additional_rule_executions=0,
        output_authority='adopted_r2_program_head.assemble',
        old_answer=deepcopy(result['answer']),
        formula_checked=False, formula_applicable=False,
        A1=dict(established_support={}, add=None),
        A2=dict(invalid_paths={}, remove=None, inherited_unknown=None))
    if options is None:
        record['special_policy'] = result.get('reason', 'no_executed_support_partition')
        return record
    program = r123_module('r2_program_head')
    keys, none = r123_module('r2_support_interface').option_keys(item)
    if set(options) != set(keys) or any(options[k].get('state') not in
            ('MET', 'CONTRADICTED', 'UNKNOWN') for k in keys):
        raise ValueError('Executed support states do not partition the current entity options')
    assembled = program.assemble(item, initial, options)
    expected = initial if assembled is None else assembled
    if expected != result['answer'] or bool(assembled is not None) != result['applied']:
        raise ValueError('Saved support result differs from the adopted assembler')
    states = {state: [k for k in keys if options[k]['state'] == state]
              for state in ('MET', 'CONTRADICTED', 'UNKNOWN')}
    valid = (isinstance(initial, (list, tuple)) and bool(initial)
             and all(k in item['options'] for k in initial)
             and not (none in initial and len(initial) > 1))
    record['states'] = states
    record['scope'] = result.get('scope')
    record['action'] = result.get('action')
    record['facts'] = deepcopy(result.get('facts', {}))
    record['A1']['established_support'] = {
        k: deepcopy(options[k]) for k in states['MET']}
    record['A2']['invalid_paths'] = {
        k: [deepcopy(path) for path in options[k].get('paths', [])
            if path.get('state') == 'CONTRADICTED'] for k in keys}
    if valid:
        selected = set(initial) - ({none} if none else set())
        add = [k for k in states['MET'] if k not in selected]
        remove = [k for k in states['CONTRADICTED'] if k in selected]
        record['A1']['add'] = add
        record['A2']['remove'] = remove
        record['A2']['inherited_unknown'] = [k for k in states['UNKNOWN'] if k in selected]
        record['formula_applicable'] = none not in initial and assembled is not None
        if record['formula_applicable']:
            operated = (selected - set(remove)) | set(add)
            recomputed = set(states['MET']) | (selected & set(states['UNKNOWN']))
            # Empty entities may become the native None option or no proposal.
            native_entities = set(assembled or []) - ({none} if none else set())
            if operated != recomputed or operated != native_entities:
                raise AssertionError('Ordinary entity-set decomposition changed old assembly')
            record.update(formula_checked=True, formula_entities=[k for k in keys if k in operated])
    record['special_policy'] = ('old_assembler_for_all_cases_including_native_none' if valid
                                else 'old_invalid_initial_and_unknown_policy')
    return record


def operation_record(packet, component, predicate, legacy_result=None):
    roles = {'original_catalog_predicate': ['A3'], 'original_rule_predicate': ['A1', 'A2'],
        'complete_supplied_model_capability': ['A4'], 'adopted_F_native_capability': ['A5'],
        'original_passthrough_predicate': []}[predicate]
    result = dict(selected_component=component, capability_predicate=predicate, roles=roles,
        router_variant=strong_legacy.VARIANT, global_generation_aggregator=False,
        adopted_head_identity_preserved=True, new_independent_algorithms=0)
    if roles == ['A1', 'A2']:
        if legacy_result is None:
            raise ValueError('Rule decomposition needs its same-execution support result')
        result['shared_rule_operations'] = rule_operations(
            packet.native_input, packet.baseline_answer, legacy_result)
    return result


def wrap_cached(packet, strong_row, component_row, source_proof):
    """Retain the accepted B native interface and append only outer operation data."""
    component, predicate = strong_legacy.select(packet)
    old_trace = strong_row['proposal']['trace']
    if (old_trace.get('selected_component') != component
            or old_trace.get('capability_predicate') != predicate):
        raise ValueError('Saved B route differs from the unchanged visible capability policy')
    base = baseline_native.wrap(packet, strong_row, component_row, source_proof)
    operations = operation_record(packet, component, predicate,
        component_row['proposal'].get('trace', {}).get('legacy_result'))
    return dict(base, variant=VARIANT, baseline_interface_variant=base['variant'],
        baseline_interface_digest=digest(base), operations=operations)


def run(packet, session, *, method, initial_native=_MISSING,
        f_disagreement_reanswer=False, f_reanswer_seed=42):
    """Run the adopted entry once and pass its native proposal through unchanged.

    The result deliberately retains the adopted head's native value type. Saved
    complete outputs use wrap_cached for the already accepted B object interface.
    The optional F-only switch reuses the exact cycle1 ordinary control. It
    never gives a new model final authority over another adopted head.
    """
    checkpoint = session.checkpoint()
    if f_disagreement_reanswer and f_reanswer_seed not in (42, 43, 44):
        raise ValueError('F ordinary reanswer requires a preregistered seed: 42, 43 or 44')
    component, predicate = strong_legacy.select(packet)
    optional_reanswer = None
    if component == 'legacy_R1':
        catalog, priors = a3.resources(method) if predicate == 'original_catalog_predicate' else (None, None)
        codes = list(r123_module('r3_ontology_head').CODES[:len(catalog)]) if catalog else None

        def score_codes(**request):
            return session.score(**request, codes=codes, seed=42, stage='A3:catalog')

        def generate_facts(messages, schema):
            return session.generate(messages, schema, seed=42, temperature=0.0,
                                    max_tokens=2048, stage='A2:positive_facts')

        result = legacy_router.optimize(packet.native_input, packet.original_context,
            packet.baseline_answer, catalog, priors, score_codes, generate_facts)
        native = result['answer']
        if result['used_original']:
            if initial_native is _MISSING:
                raise ValueError('Old passthrough needs its complete saved initial native response')
            if baseline_native.answer_value(initial_native) != packet.baseline_answer:
                raise ValueError('Complete initial response differs from the current baseline value')
            native = initial_native
        trace = dict(legacy_result=result)
        adopted_variant = 'adopted_R1_dispatch'
    else:
        proposal = (a4.run(packet, session, method=method) if component == 'A4'
                    else old_f.run_legacy(packet, session))
        native, trace, adopted_variant = proposal.native_proposal, proposal.trace, proposal.variant
        if component == 'F' and f_disagreement_reanswer:
            optional_reanswer = f_reanswer.run(packet, session, native, proposal.to_dict(),
                control=True, config=dict(seed=f_reanswer_seed))
            native = optional_reanswer['native_answer']
        result = None
    record = dict(request_id=packet.request_id, input_hash=packet.input_hash,
        variant=F_REANSWER_VARIANT if f_disagreement_reanswer else VARIANT,
        native_proposal=deepcopy(native), original_component_variant=adopted_variant,
        operations=operation_record(packet, component, predicate, result),
        trace=deepcopy(trace), cost=session.cost_since(checkpoint))
    if f_disagreement_reanswer:
        record['f_ordinary_reanswer'] = dict(enabled=True, seed=f_reanswer_seed,
            eligible_branch=component == 'F', result=optional_reanswer,
            policy_source=f_reanswer.CONTROL,
            global_generation_aggregator=False)
    return record
