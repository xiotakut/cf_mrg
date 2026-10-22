"""Locate patient facts by sentence ID, keeping the first fixed rule bank unchanged."""
import json
import re

from r2_program_head import NUMERIC,BOOL,required_fields,build_request as original_request
from r2_support_interface import obj,has_number


def sentences(item):
    parts=re.split(r'(?<=[.!?])\s+(?=[A-Z])|\n+',item['question'])
    return {f'S{i}':part.strip() for i,part in enumerate(parts) if part.strip()}


def build_request(item,kind='facts'):
    if kind!='facts':return original_request(item,kind)
    source=sentences(item);required=sorted(required_fields(item))
    evidence={'type':'array','items':{'enum':list(source)}}
    schema=obj(dict(action=obj(dict(value={'enum':['avoid','dose_reduce','other']},evidence_ids=evidence)),
        facts=obj({k:obj(dict(value={'type':['number','null'] if k in NUMERIC else ['boolean','null']},evidence_ids=evidence)) for k in required})))
    content=json.dumps(dict(current_patient_sentences=source,options=item['options'],answer_format=item['answer_format'],
                           requested_facts={k:NUMERIC.get(k,BOOL.get(k)) for k in required}),ensure_ascii=False)
    content+='''

Extract facts about THIS patient only. You do not decide medications or execute medical rules. Cite the sentence IDs that establish the value; do not generate quotes. Use null and [] when the patient text does not establish the fact. False requires explicit negation or a directly stated incompatible fact, not merely absence of information. A sentence ID is evidence only when its content actually establishes that fact. An option is not a current prescription. A statement about current medication absence does not specify future treatment duration or indication. Preserve variable identity: eGFR is not CrCl. A number must occur with the correct measure in the cited sentence. Do not infer symptomatic heart failure from ejection fraction alone. "No dementia" does not establish no delirium, no falls, or available alternatives. "Not currently taking nitrofurantoin" does not establish absence of a proposed long-term suppressive course. If alternatives are not discussed, no_safer_alternative and alternatives_ineffective are null. Extract action avoid for questions asking avoidance/inappropriateness, dose_reduce for dose reduction/adjustment, other otherwise. Cite the actual request sentence. Return only concise JSON matching the schema.'''
    return dict(messages=[dict(role='system',content='You extract explicitly supported current-patient facts for a medication-rule research experiment.'),dict(role='user',content=content)],schema=schema)


def clean_facts(item,records,required):
    source=sentences(item);facts={};errors=[]
    for key in required:
        record=records[key];value=record['value'];ids=record['evidence_ids']
        valid=value is None or (bool(ids) and all(i in source for i in ids))
        quote=' '.join(source[i] for i in ids if i in source)
        if value is not None and key in NUMERIC:
            valid=valid and not isinstance(value,bool) and has_number(value,quote)
            if key=='crcl':valid=valid and bool(re.search(r'\bCrCl\b|creatinine clearance',quote,re.I))
            if key=='egfr':valid=valid and bool(re.search(r'\beGFR\b|glomerular filtration',quote,re.I))
        if not valid:errors.append(dict(field=key,record=record,reason='missing_patient_sentence_or_measure_mismatch'))
        facts[key]=value if valid else None
    return facts,errors


def clean_extraction(item,extraction):
    source=sentences(item);facts,errors=clean_facts(item,extraction['facts'],required_fields(item))
    a=extraction['action'];ids=a['evidence_ids'];action=a['value'] if ids and all(i in source for i in ids) else 'other'
    return action,facts,errors


def check():
    i=dict(question='A 77-year-old woman has eGFR 25 mL/min. Which medicine requires dose reduction?',answer_format='multi',options={'A':'Gabapentin','B':'None of the above'})
    source=sentences(i);assert list(source)==['S0','S1']
    x=dict(action=dict(value='dose_reduce',evidence_ids=['S1']),facts={k:dict(value=None,evidence_ids=[]) for k in required_fields(i)})
    x['facts']['crcl']=dict(value=25,evidence_ids=['S0'])
    a,f,e=clean_extraction(i,x);assert a=='dose_reduce' and f['crcl'] is None and e
    x['facts']['age_years']=dict(value=77,evidence_ids=[])
    assert clean_extraction(i,x)[1]['age_years'] is None
    x['facts']['age_years']['evidence_ids']=['S0'];assert clean_extraction(i,x)[1]['age_years']==77
    print('PASS: canonical sentence lookup, missing evidence rejection and CrCl/eGFR distinction.')
