"""Opt-in A5 serialization repair; logical fields and original parser stay intact."""
import json

REVISION='bounded_a5_whitespace_reference_offset_r1'


def nonnegative_range(maximum):
    """Decimal spellings of 0..maximum, without enumerating source characters."""
    if type(maximum) is not int or maximum < 0:
        raise ValueError('A measured nonnegative source length is required')
    digits=str(maximum)
    alternatives=['"0"']
    for width in range(1,len(digits)):
        alternatives.append('[1-9]'+(' [0-9]{'+str(width-1)+'}' if width>1 else ''))
    for index,char in enumerate(digits):
        low=1 if index==0 else 0
        high=int(char)-1
        if high<low:continue
        prefix=json.dumps(digits[:index])+' ' if index else ''
        choice=json.dumps(str(low)) if low==high else '['+str(low)+'-'+str(high)+']'
        remaining=len(digits)-index-1
        alternatives.append(prefix+choice+(' [0-9]{'+str(remaining)+'}' if remaining else ''))
    if maximum:alternatives.append(json.dumps(digits))
    return ' | '.join(alternatives)


def grammar(schema,maximum_start):
    from cf_moa.agents.a1_support_completion import obj,array,TEXT,REFERENCE
    from copy import deepcopy
    expected=obj(dict(native_answer=deepcopy(schema.get('properties',{}).get('native_answer')),
        disagreement_basis=array(REFERENCE),reason=TEXT))
    if schema!=expected or list(schema['properties'])!=['native_answer','disagreement_basis','reason']:
        raise ValueError('The structural repair is restricted to the exact A5 adjudication contract')
    if type(maximum_start) is not int or maximum_start<0:
        raise ValueError('Reference bound must come from complete current visible sources')
    import xgrammar as xgr
    original=str(xgr.Grammar.from_json_schema(schema))
    whitespace=r'[ \n\t]*'
    if whitespace not in original:
        raise ValueError('Installed xgrammar whitespace layout changed')
    repaired=original.replace(whitespace,r'[ \n\t]{0,16}')
    lines=repaired.splitlines()
    name='root_prop_1_items_prop_2'
    matched=[i for i,line in enumerate(lines) if line.startswith(name+' ::=')]
    if len(matched)!=1 or '[0-9]*' not in lines[matched[0]]:
        raise ValueError('Installed xgrammar reference-offset rule changed')
    # Only the reference start rule changes. Native numeric/auxiliary fields and
    # every string/array remain unchanged. Every valid source offset <= max(len(source)).
    lines[matched[0]]=name+' ::= ('+nonnegative_range(maximum_start)+')'
    return '\n'.join(lines)+'\n'
