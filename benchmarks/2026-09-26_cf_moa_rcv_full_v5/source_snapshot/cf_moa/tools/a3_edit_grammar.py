"""Exact A3 editor array-bound compatibility for the installed xgrammar.

The logical schema and all converter rules except the edit-array continuation
remain unchanged. This adds no whitespace, string-length or sampling policy.
"""
from functools import lru_cache
import json

from cf_moa.tools.schema_compat import SchemaCompatibilityError


def is_editor_schema(schema):
    try:
        spans = schema['properties']['edits']['items']['properties']['span_id']['enum']
        if not isinstance(spans, list) or not spans or not all(isinstance(s, str) for s in spans):
            return False
        expected = dict(type='object', properties=dict(edits=dict(type='array', maxItems=2, items=dict(
            type='object', properties=dict(span_id=dict(type='string', enum=spans),
                operation=dict(type='string', enum=['delete', 'explicit_negation']), replacement=dict(type='string')),
            required=['span_id', 'operation', 'replacement'], additionalProperties=False))),
            required=['edits'], additionalProperties=False)
        return schema == expected
    except (KeyError, TypeError):
        return False


@lru_cache(maxsize=128)
def bounded_editor_grammar(serialized_schema):
    schema = json.loads(serialized_schema)
    if not is_editor_schema(schema):
        raise SchemaCompatibilityError('Only the unchanged A3 editor contract has this compatibility rewrite')
    import xgrammar as xgr
    original = str(xgr.Grammar.from_json_schema(schema))
    # The converter supports the empty array and all item fields, but ignores
    # maxItems. Remove recursion from its optional continuation: one initial
    # item plus at most one more. Preserve every other byte of the converter's
    # grammar, including its unbounded whitespace and JSON-string conventions.
    lines = original.splitlines()
    continuation = 'root_prop_0_1'
    item = 'root_prop_0_items'
    expected = continuation + r' ::= ("" | ([ \n\t]* "," [ \n\t]* ' + item + ' ' + continuation + r')) (=([ \n\t]* "]"))'
    matches = [i for i, line in enumerate(lines) if line.startswith(continuation + ' ::=')]
    if (len(matches) != 1 or lines[matches[0]] != expected
            or not any(line.startswith('root_prop_0 ::=') and '"["' in line and item + ' ' + continuation in line for line in lines)):
        raise SchemaCompatibilityError('Installed A3 array grammar layout changed; refuse an unverified rewrite')
    lines[matches[0]] = expected.replace(item + ' ' + continuation, item)
    return '\n'.join(lines) + '\n'


def grammar(schema):
    return bounded_editor_grammar(json.dumps(schema, ensure_ascii=False))
