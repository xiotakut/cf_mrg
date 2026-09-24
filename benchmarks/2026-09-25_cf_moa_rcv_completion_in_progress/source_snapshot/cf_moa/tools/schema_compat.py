"""Exact compatibility guidance and separately registered bounded guidance.

The V1 logical schema stays unchanged. V2 is an explicitly new method contract.
"""
from functools import lru_cache
import json


class SchemaCompatibilityError(RuntimeError):
    category = 'schema'


class OutputSchemaError(RuntimeError):
    category = 'schema'
    source = 'output_contract'


def is_a1_coverage(schema):
    from cf_moa.agents.a1_support_completion import audit_schema
    try:
        candidates = schema['properties']['coverage']['items']['properties']['candidate']['enum']
        return schema == audit_schema(dict.fromkeys(candidates))
    except (KeyError, TypeError):
        return False


@lru_cache(maxsize=128)
def bounded_a1_grammar(serialized_schema):
    import xgrammar as xgr
    schema = json.loads(serialized_schema)
    if not is_a1_coverage(schema):
        raise SchemaCompatibilityError('Only the unchanged A1 coverage contract has this compatibility rewrite')
    # The installed converter preserves the remaining contract, but drops array
    # lengths. Replace exactly the coverage rule with 1 item + at most 11 more.
    lines = str(xgr.Grammar.from_json_schema(schema)).splitlines()
    index = list(schema['properties']).index('coverage')
    rule = 'root_prop_' + str(index)
    item = rule + '_items'
    matching = [i for i, line in enumerate(lines) if line.startswith(rule + ' ::=')]
    if len(matching) != 1 or not any(line.startswith(item + ' ::=') for line in lines):
        raise SchemaCompatibilityError('Installed xgrammar rule layout changed; refuse an unverified rewrite')
    lines[matching[0]] = rule + r' ::= ("[" [ \n\t]* ' + item + r' moa_a1_extra_1 [ \n\t]* "]")'
    for number in range(1, 12):
        following = ' moa_a1_extra_' + str(number + 1) if number < 11 else ''
        lines.append('moa_a1_extra_' + str(number) + r' ::= ("" | ([ \n\t]* "," [ \n\t]* ' + item + following + '))')
    return '\n'.join(lines) + '\n'


def guidance(schema, guided_class, *, decoding_revision=None, reference_max_start=None):
    from cf_moa.tools.single_agent_tools import ARGUMENT_DECODER, argument_grammar
    if decoding_revision == ARGUMENT_DECODER:
        if reference_max_start is not None:
            raise SchemaCompatibilityError('Tool argument decoding does not use reference offsets')
        return guided_class(grammar=argument_grammar(schema),backend='xgrammar')
    from cf_moa.tools.a5_structural_grammar import REVISION as a5_revision, grammar as a5_grammar
    if decoding_revision == a5_revision:
        return guided_class(grammar=a5_grammar(schema,reference_max_start),backend='xgrammar')
    if reference_max_start is not None:
        raise SchemaCompatibilityError('A source-offset bound requires the registered A5 decoder')
    from cf_moa.controller.evidence_highlighting import is_highlight_schema
    if is_highlight_schema(schema):
        if decoding_revision != 'bounded_highlight_whitespace_v1':
            raise SchemaCompatibilityError('Highlighting requires its explicitly registered decoder')
        from cf_moa.tools.relational_json import grammar
        return guided_class(grammar=grammar(schema, bounded_whitespace=True), backend='xgrammar')
    from cf_moa.agents.a1_relational_coverage import is_relational_schema
    from cf_moa.agents.a1_coded_coverage import is_coded_schema
    if decoding_revision is not None:
        if decoding_revision != 'bounded_whitespace_16_r4' or not (is_relational_schema(schema) or is_coded_schema(schema)):
            raise SchemaCompatibilityError('Decoding revision requires its exact registered A1 contract')
        from cf_moa.tools.relational_json import grammar
        return guided_class(grammar=grammar(schema, bounded_whitespace=True), backend='xgrammar')
    if is_coded_schema(schema):
        raise SchemaCompatibilityError('The coded contract requires its declared decoder')
    if is_relational_schema(schema):
        from cf_moa.tools.relational_json import grammar
        return guided_class(grammar=grammar(schema), backend='xgrammar')
    from cf_moa.agents.a1_bounded_coverage import is_v2_schema
    if is_v2_schema(schema):
        from cf_moa.tools.bounded_json import grammar
        return guided_class(grammar=grammar(schema), backend='xgrammar')
    if is_a1_coverage(schema):
        return guided_class(grammar=bounded_a1_grammar(json.dumps(schema, ensure_ascii=False)),
                            backend='xgrammar')
    from cf_moa.tools.a3_edit_grammar import is_editor_schema, grammar as editor_grammar
    if is_editor_schema(schema):
        return guided_class(grammar=editor_grammar(schema), backend='xgrammar')
    return guided_class(json=schema, backend='xgrammar')
