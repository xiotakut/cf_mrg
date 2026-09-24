"""Offline mechanism views of the SAME adopted rule execution.

These views change assembly policy for a control only, never the recorded
facts/support states. A1/A2 are two projections of one shared engine.
"""
from copy import deepcopy

from cf_moa.controller.minimal_operations import rule_operations
from cf_moa.tools.legacy import r123_module


def run(item, initial, result, *, disabled):
    if disabled not in ('add', 'remove'):
        raise ValueError('Disable exactly one declared operation')
    operations = rule_operations(item, initial, result)
    record = dict(variant='shared_rule_disable_' + disabled + '_v1',
        disabled=disabled, shared_execution=True, original_result=deepcopy(result),
        original_operations=operations, new_model_calls=0,
        applicable=False, answer=deepcopy(result['answer']))
    keys, none = r123_module('r2_support_interface').option_keys(item)
    valid = (isinstance(initial, (list, tuple)) and bool(initial)
             and all(k in item['options'] for k in initial)
             and not (none in initial and len(initial) > 1))
    if result.get('options') is None or not valid:
        record['reason'] = 'no_executed_partition_or_invalid_initial; original_policy_retained'
        return record
    view = deepcopy(result['options'])
    selected = set(initial) - ({none} if none else set())
    changed = []
    for key in keys:
        suppress = ((disabled == 'add' and view[key]['state'] == 'MET' and key not in selected)
                    or (disabled == 'remove' and view[key]['state'] == 'CONTRADICTED' and key in selected))
        if suppress:
            view[key]['state'] = 'UNKNOWN'
            changed.append(key)
    assembled = r123_module('r2_program_head').assemble(item, initial, view)
    record.update(applicable=True, assembly_view=view, policy_changed_keys=changed,
                  answer=deepcopy(initial if assembled is None else assembled),
                  reason='original_assembler_on_separate_UNKNOWN_inheritance_view')
    return record
