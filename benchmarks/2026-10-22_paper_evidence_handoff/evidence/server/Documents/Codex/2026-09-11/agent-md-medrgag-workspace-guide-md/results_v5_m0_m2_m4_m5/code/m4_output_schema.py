"""Output syntax and visible answer-space constraints; no gold labels."""
from itertools import combinations


def output_schema(item):
    fmt = item['answer_format']
    keys = list(item['options'])
    if fmt in ('single', 'robustness_single'):
        answer = {'type': 'string', 'enum': keys}
    elif fmt == 'multi':
        # Native scoring treats order as irrelevant. Enumerate nonempty subsets
        # in the visible option order to enforce distinct legal keys.
        answer = {'enum': [list(c) for n in range(1, len(keys)+1) for c in combinations(keys, n)]}
    elif fmt == 'relation':
        answer = {'type': 'string', 'enum': ['higher', 'lower', 'no difference', 'uncertainty']}
    else:
        answer = {'type': 'string'}
    props = {'step_by_step_thinking': {'type': 'string'}, 'answer_choice': answer}
    if fmt == 'robustness_single':
        props['errors'] = {'type': 'array', 'items': {'type': 'object', 'properties': {
            'document_id': {'type': 'string', 'enum': [f'D{i}' for i in range(len(item['fixed_evidence']))]},
            'correction': {'type': 'string'}}, 'required': ['document_id', 'correction'], 'additionalProperties': False}}
    return {'type': 'object', 'properties': props, 'required': list(props), 'additionalProperties': False}
