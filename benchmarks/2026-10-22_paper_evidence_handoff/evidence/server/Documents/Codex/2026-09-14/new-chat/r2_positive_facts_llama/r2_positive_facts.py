"""Test positive Boolean extraction names; keep the original rule vocabulary."""
import json
from r2_task_scoped_head import build_request as previous_request,clean_extraction as previous_clean

ALIASES={
 'no_safer_alternative':('safer_alternative_available','A safer treatment alternative is explicitly available. False only when safer alternatives are explicitly unavailable; unmentioned availability is null.'),
 'alternatives_ineffective':('alternatives_effective','Other treatment alternatives have explicitly been effective. False when the stated alternatives have been ineffective; unmentioned treatment outcomes are null.'),
}


def build_request(item):
    request=previous_request(item);text=request['messages'][-1]['content']
    content,end=json.JSONDecoder().raw_decode(text);tail=text[end:]
    fields=content['requested_facts'];props=request['schema']['properties']['facts']['properties']
    changed=set(fields)&ALIASES.keys()
    if not changed:return request
    content['requested_facts']={ALIASES[k][0] if k in ALIASES else k:ALIASES[k][1] if k in ALIASES else v for k,v in fields.items()}
    schema=request['schema']['properties']['facts']
    schema['properties']={ALIASES[k][0] if k in ALIASES else k:v for k,v in props.items()}
    schema['required']=[ALIASES[k][0] if k in ALIASES else k for k in schema['required']]
    for k in changed:tail=tail.replace(k,ALIASES[k][0])
    request['messages'][-1]['content']=json.dumps(content,ensure_ascii=False)+tail
    return request


def clean_extraction(item,extraction):
    facts=dict(extraction['facts'])
    for old,(new,_) in ALIASES.items():
        if new in facts:
            record=facts.pop(new);value=record['value']
            facts[old]=dict(record,value=None if value is None else not value)
    return previous_clean(item,dict(facts=facts))


def check():
    item=dict(question='A 78-year-old woman has recurrent falls. A safer alternative is available. Which drugs should be avoided?',answer_format='multi',options={'A':'Duloxetine','B':'None of the above'})
    r=build_request(item);assert 'safer_alternative_available' in r['schema']['properties']['facts']['properties']
    keys=r['schema']['properties']['facts']['properties'];records={k:dict(value=None,evidence_ids=[]) for k in keys}
    for value,expected in [(True,False),(False,True),(None,None)]:
        records['safer_alternative_available']=dict(value=value,evidence_ids=['S1'] if value is not None else [])
        assert clean_extraction(item,dict(facts=records))[1]['no_safer_alternative'] is expected
    plain=dict(item,options={'A':'Gabapentin','B':'None of the above'},question='A 78-year-old woman has CrCl 55 mL/min. Which drugs require dose reduction?')
    assert build_request(plain)==previous_request(plain)
    print('PASS: positive field request, True/False/null normalization, exact unchanged request without aliases.')


if __name__=='__main__':check()
