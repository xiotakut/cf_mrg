"""Finite JSON serialization for the registered A1-v2 relational contract.

Objects and ID sets use catalog order. Subsets remain freely selectable, but
duplicate keys/IDs and dangling separators cannot be generated. This compiler
does not silently widen unknown schema features.
"""
import json


def grammar(schema, *, bounded_whitespace=False):
    rules, cache = [], {}

    def lit(value):
        return json.dumps(value, ensure_ascii=False)

    ws = ' rel_ws' if bounded_whitespace else ''

    def punct(value):
        return lit(value) + ws

    def add(body):
        name = 'rel_' + str(len(rules))
        rules.append(name + ' ::= (' + body + ')')
        return name

    def resolve(node):
        if '$ref' in node:
            if set(node) != {'$ref'} or not node['$ref'].startswith('#/$defs/'):
                raise ValueError('Only exact local definition references are registered')
            return schema['$defs'][node['$ref'][8:]]
        return node

    def subset(items, upper, lower):
        if lower not in (0, 1) or not 0 <= lower <= upper <= len(items):
            raise ValueError('Unregistered subset bounds')
        memo = {}

        def nonempty(index, remaining):
            key = index, min(remaining, len(items)-index)
            if key in memo:
                return memo[key]
            branches = [items[index]]
            if key[1] > 1:
                branches[0] += ' (' + punct(',') + ' ' + nonempty(index+1, key[1]-1) + ')?'
            if index+1 < len(items):
                branches.append(nonempty(index+1, key[1]))
            memo[key] = add(' | '.join(branches))
            return memo[key]

        if not upper:
            return lit('')
        result = nonempty(0, upper)
        return '(' + result + ')?' if lower == 0 else result

    def emit(node):
        node = resolve(node)
        signature = json.dumps(node, ensure_ascii=False)
        if signature in cache:
            return cache[signature]
        if 'oneOf' in node:
            if set(node) != {'oneOf'}:
                raise ValueError('Unregistered union annotations')
            body = ' | '.join(emit(child) for child in node['oneOf'])
        elif 'enum' in node:
            if not node['enum']:
                raise ValueError('Empty enum')
            body = ' | '.join(lit(json.dumps(v, ensure_ascii=False, separators=(',', ':')))
                              for v in node['enum'])
        elif node['type'] == 'object':
            props = node['properties']
            if node.get('additionalProperties') is not False:
                raise ValueError('Open objects are not registered')
            items = [punct(json.dumps(key)+':') + ' ' + emit(child) for key, child in props.items()]
            if node.get('required') == list(props):
                middle = (' '+punct(',')+' ').join(items)
            elif node.get('required') == []:
                middle = subset(items, node['maxProperties'], node['minProperties'])
            else:
                raise ValueError('Mixed optional/required objects are not registered')
            body = punct('{') + ' ' + middle + ' ' + lit('}')
        elif node['type'] == 'array':
            lower, upper = node.get('minItems', 0), node['maxItems']
            if not 0 <= lower <= upper <= 512:
                raise ValueError('Invalid finite array bounds')
            if upper == 0:
                body = (punct('[') + ' ' + lit(']')) if bounded_whitespace else lit('[]')
            elif node.get('uniqueItems'):
                values = resolve(node['items'])['enum']
                items = [lit(json.dumps(v, ensure_ascii=False)) + ws for v in values]
                middle = subset(items, min(upper, len(items)), lower)
                body = punct('[') + ' ' + middle + ' ' + lit(']')
            else:
                item = emit(node['items'])
                sequence = item + ' ('+punct(',')+' '+item+'){'+str(max(0, lower-1))+','+str(upper-1)+'}'
                body = punct('[')+' ('+sequence+')'+('?' if lower == 0 else '')+' '+lit(']')
        elif node['type'] == 'string':
            lower, upper = node.get('minLength', 0), node['maxLength']
            if not 0 <= lower <= upper <= 320:
                raise ValueError('Unregistered string bound')
            body = lit('"')+' rel_char{'+str(lower)+','+str(upper)+'} '+lit('"')
        else:
            raise ValueError('Unregistered bounded schema')
        if bounded_whitespace and 'oneOf' not in node:
            body = '(' + body + ')' + ws
        cache[signature] = add(body)
        return cache[signature]

    root = emit(schema)
    char = r'rel_char ::= ([^"\\\x00-\x1f] | ("\\" ["\\/bfnrt]))'
    layout = [r'rel_ws ::= [ \t\n\r]{0,16}'] if bounded_whitespace else []
    return '\n'.join(['root ::= '+('rel_ws ' if bounded_whitespace else '')+root, char, *layout, *rules])+'\n'
