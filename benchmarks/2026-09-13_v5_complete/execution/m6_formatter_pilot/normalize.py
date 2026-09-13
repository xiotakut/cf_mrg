"""Offline formatter compatibility: preserve explicit values; never infer answers."""
import ast
import json
import re


def literal(text):
    def pairs(values):
        out={}
        for k,v in values:
            if k in out:raise ValueError('duplicate_key')
            out[k]=v
        return out
    try:
        return json.loads(text,strict=False,object_pairs_hook=pairs)
    except json.JSONDecodeError:
        tree=ast.parse(text,mode='eval')
        for node in ast.walk(tree):
            if isinstance(node,ast.Dict):
                keys=[ast.literal_eval(k) for k in node.keys]
                if len(keys)!=len(set(keys)):raise ValueError('duplicate_key')
        return ast.literal_eval(tree)


def candidates(raw):
    values=[];pos=0
    while True:
        start=raw.find('{',pos)
        if start<0:break
        parsed=False
        for match in re.finditer('}',raw[start:]):
            end=start+match.end()
            try:value=literal(raw[start:end])
            except (SyntaxError,ValueError,TypeError):continue
            if isinstance(value,dict):
                if 'answer' in value:values.append(value)
                pos=end;parsed=True;break
        if not parsed:pos=start+1
    return values


def normalize(raw,item):
    values=candidates(raw)
    if not values:raise ValueError('no_explicit_answer_object')
    for value in values:
        if item['answer_format']=='diagnosis':
            answer=value['answer']
            if isinstance(answer,str):
                try:wrapped=literal(answer)
                except (SyntaxError,ValueError,TypeError):wrapped=None
                if isinstance(wrapped,dict):answer=wrapped
            if isinstance(answer,dict) and set(answer)=={'diagnosis'} and isinstance(answer['diagnosis'],str):
                value['answer']=answer['diagnosis']
    if any(v!=values[0] for v in values[1:]):raise ValueError('conflicting_objects')
    result=values[0]
    if item['answer_format']=='robustness_single' and 'errors' not in result:
        sections=re.findall(r'^## Errors\s*\n(.*?)(?=^## |\Z)',raw,re.M|re.S)
        if len(sections)!=1:raise ValueError('missing_or_multiple_errors_sections')
        text=sections[0].strip()
        if text.startswith('```'):
            text=re.sub(r'^```(?:json|python)?\s*\n|\n```$', '',text)
        errors=literal(text)
        if not isinstance(errors,list):raise ValueError('errors_not_array')
        result['errors']=errors
    return json.dumps(result,ensure_ascii=False,allow_nan=False)


def test():
    assert json.loads(normalize("## Answer\n{'answer':'C'}",{'answer_format':'single'}))=={'answer':'C'}
    assert json.loads(normalize('{"answer":{"diagnosis":"X"}}',{'answer_format':'diagnosis'}))=={'answer':'X'}
    for text in ['{"answer":"A"}{"answer":"B"}', '{"answer":"A","answer":"B"}', 'The answer is probably A.']:
        try:normalize(text,{'answer_format':'single'})
        except ValueError:pass
        else:raise AssertionError(text)
    assert json.loads(normalize("## Errors\n[]\n## Answer\n{'answer':'A'}",{'answer_format':'robustness_single'}))=={'answer':'A','errors':[]}

if __name__=='__main__':test();print('Literal conversion, value preservation, conflict rejection: passed.')
