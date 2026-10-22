"""R2 fact head: explicit question action selects only the facts that its rules require."""
import json
from r2_action_scope import requested_action
from r2_program_head import NUMERIC,BOOL,relevant_rules,fields
from r2_indexed_head import sentences,clean_facts
from r2_support_interface import obj


def required_fields(item):
    action=requested_action(item)
    rules=[r for r in relevant_rules(item) if r['action']==action]
    return {'age_years'}|set().union(*(fields(r['when'])|fields(r['unless']) for r in rules))


def build_request(item):
    source=sentences(item);required=sorted(required_fields(item));evidence={'type':'array','items':{'enum':list(source)}}
    schema=obj(dict(facts=obj({k:obj(dict(value={'type':['number','null'] if k in NUMERIC else ['boolean','null']},evidence_ids=evidence)) for k in required})))
    content=json.dumps(dict(current_patient_sentences=source,options=item['options'],
                           requested_facts={k:NUMERIC.get(k,BOOL.get(k)) for k in required}),ensure_ascii=False)
    content+='''

Extract only these requested facts about the current patient. You do not decide medications or supply medical rules. Return each value with the IDs of sentences that establish it. Use null and [] for unmentioned or ambiguous facts. False requires an explicit negation or directly stated incompatible fact, not absence of discussion. A listed option is not a current prescription, and not taking a drug does not specify the duration of a proposed course. Preserve the numeric variable and units: CrCl is not eGFR. A number must be present with the correct measure in the cited sentence. No dementia does not establish no delirium or no falls. If alternatives are unmentioned, no_safer_alternative and alternatives_ineffective are null. Return concise JSON with facts only.'''
    return dict(messages=[dict(role='system',content='You extract explicitly supported current-patient facts for a medication-rule research experiment.'),dict(role='user',content=content)],schema=schema)


def clean_extraction(item,extraction):
    facts,errors=clean_facts(item,extraction['facts'],required_fields(item))
    return requested_action(item),facts,errors


def check():
    item=dict(question='A 78-year-old woman has creatinine clearance (CrCl) 55 mL/min. Which drugs require dose reduction?',answer_format='multi',options={'A':'Gabapentin','B':'Famotidine','C':'None of the above'})
    assert required_fields(item)=={'age_years','crcl'}
    x=dict(facts=dict(age_years=dict(value=78,evidence_ids=['S0']),crcl=dict(value=55,evidence_ids=['S0'])))
    a,f,e=clean_extraction(item,x);assert a=='dose_reduce' and f=={'age_years':78,'crcl':55} and not e
    from r2_program_head import execute,assemble
    assert assemble(item,None,execute(item,a,f))==['A']
    print('PASS: action-scoped fields, canonical evidence, exact threshold and removal/retention without an initial answer.')


if __name__=='__main__':check()
