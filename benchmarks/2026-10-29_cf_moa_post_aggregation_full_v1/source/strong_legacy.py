"""Fixed adopted-head control, declared before F development quality scoring.

Preserve R1's original predicates first, then the explicitly supplied-model
executor and selected F. This is neither an oracle nor the proposed MoA router.
"""
from cf_moa.agents.a4_intervention_execution import capability
from cf_moa.tools.legacy import r123_module

VARIANT = 'adopted_R1_R4_F_capability_composite_v1'


def select(packet):
    if packet.native_input['answer_format'] == 'diagnosis':
        return 'legacy_R1', 'original_catalog_predicate'
    if r123_module('r2_program_head').eligible(packet.native_input):
        return 'legacy_R1', 'original_rule_predicate'
    if capability(packet)[0]:
        return 'A4', 'complete_supplied_model_capability'
    if (packet.native_input['answer_format'] in ('single', 'robustness_single', 'relation')
            and not isinstance(packet.original_context, str)):
        return 'F', 'adopted_F_native_capability'
    return 'legacy_R1', 'original_passthrough_predicate'
