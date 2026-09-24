"""Finite compact JSON grammar for the explicitly registered A1-v2 contract.

Arrays, free strings and whitespace are bounded. Unique IDs and cross-table
relations are checked by the method after parsing. This is a new output format,
not a claim that every serialization accepted by JSON Schema is generated.
"""
import json


def grammar(schema):
    rules = []
    counter = 0

    def literal(value):
        return json.dumps(value, ensure_ascii=False)

    def emit(node):
        nonlocal counter
        name = 'v2_' + str(counter)
        counter += 1
        if 'enum' in node:
            if not node['enum']:
                raise ValueError('Empty enum in a bounded output contract')
            body = ' | '.join(literal(json.dumps(value, ensure_ascii=False, separators=(',', ':')))
                              for value in node['enum'])
        elif node['type'] == 'object':
            props = node['properties']
            if node.get('required') != list(props) or node.get('additionalProperties') is not False:
                raise ValueError('Bounded objects require all declared fields in order')
            parts = [literal('{')]
            for index, (key, child) in enumerate(props.items()):
                if index:
                    parts.append(literal(','))
                parts.extend([literal(json.dumps(key) + ':'), emit(child)])
            parts.append(literal('}'))
            body = ' '.join(parts)
        elif node['type'] == 'array':
            lower, upper = node.get('minItems', 0), node['maxItems']
            if not 0 <= lower <= upper <= 512:
                raise ValueError('Invalid finite array bound')
            if not upper:
                body = literal('[]')
            else:
                item = emit(node['items'])
                extra = max(0, lower-1)
                sequence = item + ' (' + literal(',') + ' ' + item + '){' + str(extra) + ',' + str(upper-1) + '}'
                body = literal('[') + ' (' + sequence + ')' + ('?' if lower == 0 else '') + ' ' + literal(']')
        elif node['type'] == 'string':
            lower, upper = node.get('minLength', 0), node['maxLength']
            body = literal('"') + ' v2_char{' + str(lower) + ',' + str(upper) + '} ' + literal('"')
        else:
            raise ValueError('Unregistered bounded output type: ' + str(node.get('type')))
        rules.append(name + ' ::= (' + body + ')')
        return name

    root = emit(schema)
    # No unbounded JSON whitespace and no Unicode escape spelling ambiguity.
    # Literal non-control Unicode is allowed; short escapes represent one char.
    char = r'v2_char ::= ([^"\\\x00-\x1f] | ("\\" ["\\/bfnrt]))'
    return '\n'.join(['root ::= ' + root, char, *rules]) + '\n'
