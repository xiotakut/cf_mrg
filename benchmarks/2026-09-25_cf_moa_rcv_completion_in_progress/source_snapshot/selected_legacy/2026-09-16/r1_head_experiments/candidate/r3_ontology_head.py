"""Diagnosis selection over a caller-supplied public ontology, using the original model."""
import json
import string

CODES=string.ascii_uppercase+string.ascii_lowercase


def build_request(item, original_messages, vocabulary, encoding='name', reasoned=False):
    assert item['answer_format']=='diagnosis' and encoding in ['name','code']
    assert len(vocabulary)<=len(CODES)
    mapping={CODES[i]:name for i,name in enumerate(vocabulary)}
    choices=list(mapping) if encoding=='code' else vocabulary
    shown=mapping if encoding=='code' else vocabulary
    instruction='Select the most likely diagnosis for the current patient from this public disease vocabulary: '+json.dumps(shown)+'. '
    instruction+=('The answer_choice must be the case-sensitive single-letter identifier, which will be decoded to its disease name. ' if encoding=='code' else 'The answer_choice must be exactly one disease name. ')
    instruction+=('First explain the decisive patient evidence in at most 80 words in step_by_step_thinking, then give answer_choice.' if reasoned else 'Return only the JSON answer_choice field; no explanation.')
    if encoding=='name' and not reasoned:
        instruction='Select the most likely diagnosis for the current patient. Use exactly one name from this public disease vocabulary: '+json.dumps(vocabulary)+'. Return only the JSON answer_choice field; no explanation.'
    props={}
    if reasoned:props['step_by_step_thinking']={'type':'string'}
    props['answer_choice']=dict(type='string',enum=choices)
    schema=dict(type='object',properties=props,required=list(props),additionalProperties=False)
    if isinstance(original_messages,str):
        # M0/M2 archives contain serialized Llama prompts; preserve their original prefix.
        tail='<|start_header_id|>assistant<|end_header_id|>\n\n'
        assert original_messages.endswith(tail)
        prompt=original_messages[:-len(tail)]+'<|start_header_id|>user<|end_header_id|>\n\n'+instruction+'<|eot_id|>'+tail
        return dict(prompt=prompt,schema=schema)
    return dict(messages=[*original_messages,dict(role='user',content=instruction)],schema=schema)


def resolve(raw_response,vocabulary,encoding='name'):
    value=json.loads(raw_response)['answer_choice']
    if encoding=='code':return {CODES[i]:name for i,name in enumerate(vocabulary)}[value]
    if value not in vocabulary:raise ValueError('Diagnosis is outside the supplied vocabulary')
    return value


def optimize(item,original_messages,original_answer,vocabulary,generate,encoding='code',reasoned=False):
    raw=generate(**build_request(item,original_messages,vocabulary,encoding,reasoned))
    try:answer=resolve(raw,vocabulary,encoding);error=None
    except (ValueError,KeyError,TypeError) as exc:answer=original_answer;error=str(exc)
    return dict(answer=answer,raw_response=raw,used_original=error is not None,error=error)


def check():
    item=dict(answer_format='diagnosis');messages=[dict(role='user',content='Current patient')];v=['Disease A','Disease B']
    r=build_request(item,messages,v,'code',True)
    assert r['schema']['properties']['answer_choice']['enum']==['A','B']
    assert resolve('{"answer_choice":"B"}',v,'code')=='Disease B'
    assert messages==[dict(role='user',content='Current patient')]
    assert r['messages'][0]==messages[0]
    fallback=optimize(item,messages,'Disease A',v,lambda **_: '{"unfinished":')
    assert fallback['answer']=='Disease A' and fallback['used_original']
    tail='<|start_header_id|>assistant<|end_header_id|>\n\n';prefix='Original serialized patient context<|eot_id|>'
    raw=build_request(item,prefix+tail,v,'code')['prompt']
    assert raw.startswith(prefix) and raw.endswith(tail) and raw.count(prefix)==1
    print('PASS: vocabulary round-trip, original message/raw context, and actual fallback answer.')


if __name__=='__main__':check()
