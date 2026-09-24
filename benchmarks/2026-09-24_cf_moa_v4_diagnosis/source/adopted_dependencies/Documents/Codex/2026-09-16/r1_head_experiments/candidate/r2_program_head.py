"""Current-patient extraction, fixed guideline execution, and native-set assembly."""
import json
import re

from r2_support_interface import OPS,combine,contains,has_number,obj,option_keys
from r2_guideline_rules import RULES

NUMERIC={
 'age_years':'Patient age in YEARS; copy a stated number, do not convert months.',
 'crcl':'Creatinine clearance, CrCl, in mL/min. Never substitute eGFR or serum creatinine.',
 'egfr':'Estimated glomerular filtration rate, eGFR, in its stated usual mL/min or mL/min/1.73m2 units. Never substitute CrCl.',
 'digoxin_mg_day':'Stated total daily DIGOXIN dose in mg/day.',
 'doxepin_mg_day':'Stated daily DOXEPIN dose in mg/day.',
 'ppi_duration_weeks':'Stated scheduled proton-pump-inhibitor duration in WEEKS; do not convert other units.',
 'metoclopramide_weeks':'Stated metoclopramide duration in WEEKS; do not convert other units.',
}
BOOL={
 'heart_failure':'Heart failure is present, including asymptomatic heart failure.',
 'hf_symptomatic':'Heart failure is explicitly symptomatic; false for explicitly asymptomatic/NYHA I without symptoms. Do not infer symptoms from ejection fraction alone.',
 'hf_reduced_ef':'Heart failure is explicitly described as reduced-ejection-fraction/HFrEF. Do not invent a cutoff or classify a numeric LVEF here.',
 'syncope':'History of syncope/syncopal episodes.',
 'bradycardia_related_syncope':'The syncope is attributed to, or may be due to, bradycardia/bradyarrhythmia.',
 'orthostatic_related_syncope':'The syncope is attributed to, or may be due to, orthostatic hypotension.',
 'delirium':'Current delirium or history of delirium as stated.',
 'high_delirium_risk':'Patient explicitly described as at high/elevated risk of delirium; age alone is not such a statement.',
 'dementia':'Dementia, Alzheimer disease or cognitive impairment is present.',
 'falls_or_fractures':'History of falls or fractures, including recurrent falls.',
 'parkinson':'Parkinson disease is present.',
 'peptic_ulcer_history':'History of gastric, duodenal or peptic ulcer disease, even if H.pylori was eradicated.',
 'female':'Patient is a woman/female (false for a man/male).',
 'urinary_incontinence':'Urinary incontinence is present.',
 'bph_or_luts':'Benign prostatic hyperplasia or lower urinary tract symptoms are present.',
 'antipsychotic_accepted_indication':'The proposed antipsychotic is for schizophrenia, bipolar disorder, Parkinson disease psychosis, explicitly adjunctive MDD treatment, or explicitly short-term antiemetic use. A stated proposed purpose establishes true even before the patient takes the drug; explicitly different purpose may establish false.',
 'nonpharm_failed_or_impossible':'Nonpharmacologic management for dementia/delirium behavior has failed or is impossible.',
 'substantial_harm_risk':'Patient threatens substantial harm to self or others.',
 'chronic_or_persistent_ap':'Antipsychotic use is chronic or persistent as-needed. Not currently taking one does not specify a proposed future duration.',
 'no_safer_alternative':'It is explicitly stated that safer alternatives are unavailable. Merely listing options or not mentioning alternatives does not establish this.',
 'seizure_or_mood_disorder':'A seizure disorder or mood disorder is explicitly present.',
 'severe_acute_pain':'Pain is explicitly both severe and acute.',
 'systemic_steroid_required':'Systemic corticosteroids are explicitly required, not merely among answer options.',
 'systemic_steroid_route':'The proposed corticosteroid is explicitly oral or parenteral. False if explicitly inhaled or topical; unspecified route is null.',
 'opioid_required_balanced_pain_plan':'An opioid is explicitly required as part of a balanced/multimodal pain plan.',
 'gastroprotection':'Current PPI or misoprostol use, or explicitly confirmed ability to use one. Do not add an imaginary new prescription.',
 'alternatives_ineffective':'Other treatment alternatives have explicitly been ineffective. Unmentioned treatment history is null.',
 'chronic_nsaid_use':'The proposed/current NSAID course is explicitly chronic or long-term.',
 'scheduled_nsaid_use':'The proposed/current NSAID course is explicitly scheduled rather than occasional as needed.',
 'bleeding_risk_comedication':'Current oral/parenteral corticosteroids, anticoagulants or antiplatelet agents. False only if these are explicitly excluded.',
 'long_term_suppression':'The proposed nitrofurantoin is explicitly for long-term suppressive treatment. Recurrent infections alone do not establish duration/purpose.',
 'antihypertensive_purpose':'The proposed alpha-1 blocker is for hypertension. Explicit use for BPH/LUTS instead establishes false.',
 'first_line_af':'The proposed amiodarone is explicitly first-line atrial fibrillation therapy.',
 'lv_hypertrophy':'Substantial left ventricular hypertrophy is explicitly present.',
 'permanent_af':'Atrial fibrillation is explicitly permanent.',
 'severe_or_decompensated_hf':'Heart failure is explicitly severe or recently decompensated.',
 'digoxin_first_line_af_or_hf':'The proposed digoxin is explicitly first-line atrial fibrillation or heart failure therapy.',
 'benzodiazepine_specific_indication':'Explicit use for seizure disorder, REM sleep behavior disorder, benzodiazepine/ethanol withdrawal, severe generalized anxiety disorder, or periprocedural anesthesia.',
 'ppi_accepted_indication':'Explicit high GI risk requiring PPI (e.g. systemic steroid/chronic NSAID), erosive/Barrett esophagitis, hypersecretory condition, or demonstrated maintenance need after failed withdrawal/H2 treatment.',
 'gastroparesis':'Gastroparesis is present.',
 'severe_allergic_reaction':'Acute severe allergic reaction is explicitly present.',
 'dabigatran_dose_relevant_interaction':'The question explicitly states a dabigatran interaction requiring dose adjustment. Do not infer one from documents or an unlisted medicine.',
}


def fields(expr):
    if expr is None or isinstance(expr,bool):return set()
    if expr[0]=='test':return {expr[1]}
    return set().union(*(fields(x) for x in expr[1:]))


def relevant_rules(item):
    drugs={v.strip().casefold() for v in item['options'].values()}
    return [r for r in RULES if drugs.intersection(r['drugs'])]


def eligible(item):
    age=re.search(r'(\d+)-year-old',item['question'],re.I)
    return item['answer_format']=='multi' and bool(age and int(age[1])>=65 and relevant_rules(item))


def required_fields(item):
    return {'age_years'}|set().union(*(fields(r['when'])|fields(r['unless']) for r in relevant_rules(item)))


def build_request(item,kind='facts'):
    required=sorted(required_fields(item));definitions={k:NUMERIC.get(k,BOOL.get(k)) for k in required}
    assert all(definitions.values())
    action=obj(dict(value={'enum':['avoid','dose_reduce','other']},quote={'type':'string'}))
    visible={k:item[k] for k in ['question','options','answer_format']}
    if kind=='facts':
        schema=obj(dict(action=action,facts=obj({k:obj(dict(value={'type':['number','null'] if k in NUMERIC else ['boolean','null']},quote={'type':'string'})) for k in required})))
        instruction='''Extract ONLY facts stated about the CURRENT patient and the exact question action. You are not deciding medications. Return null for unmentioned or ambiguous facts; false requires an explicit negation or a directly stated incompatible fact/purpose. Every non-null value needs a short exact quote from the QUESTION, including the full negation. Options do not establish current medicine use. Copy numbers with their correct variable and units: CrCl and eGFR differ. Do not infer missing facts or a medical rule. action is avoid for avoidance/inappropriateness questions, dose_reduce for questions asking dose reduction/adjustment, and other otherwise; quote the question's request. For null values use an empty quote. Return only the requested JSON, concisely.'''
        content=json.dumps(dict(current_input=visible,requested_facts=definitions),ensure_ascii=False)+'\n\n'+instruction
    else:
        keys,_=option_keys(item)
        schema=obj(dict(action=action,options=obj({k:obj(dict(state={'enum':['MET','CONTRADICTED','UNKNOWN']},reason={'type':'string'})) for k in keys})))
        instruction='''Execute the supplied finite rule bank for the CURRENT patient and EXACT requested action. The bank applies only to age>=65. Match each option to its listed drugs and the requested action. test means compare the named patient fact with operator eq/lt/le/ge/gt. all means AND, any means OR. Separate rules for the same option provide independent sufficient support (OR). A known false prerequisite defeats that support; an unmentioned required fact is UNKNOWN, not false. An unless expression is an exception: suppress support only if the complete exception is established. When prerequisites are established but the exception is unconfirmed, retain the default guideline recommendation without claiming the unknown fact is false. Return MET if any matched rule supports the option, CONTRADICTED if all its matched rules are inapplicable, UNKNOWN if its rule support is unresolved or no rule covers it. A general fact about a drug cannot create a current-patient fact. Keep reasons concise. Do not use an old answer or other medical rules. Return only requested JSON.'''
        content=json.dumps(dict(current_input=visible,fact_definitions=definitions,rules=relevant_rules(item)),ensure_ascii=False)+'\n\n'+instruction
    return dict(messages=[dict(role='system',content='You process current-patient data for a medication-rule research experiment.'),dict(role='user',content=content)],schema=schema)


def clean_extraction(item,extraction):
    q=item['question'];facts={};errors=[]
    for key in required_fields(item):
        record=extraction['facts'][key];value=record['value'];quote=record['quote']
        valid=value is None or contains(quote,q)
        if value is not None and key in NUMERIC:
            valid=valid and not isinstance(value,bool) and has_number(value,quote)
            if key=='crcl':valid=valid and bool(re.search(r'\bCrCl\b|creatinine clearance',quote,re.I))
            if key=='egfr':valid=valid and bool(re.search(r'\beGFR\b|glomerular filtration',quote,re.I))
        if not valid:errors.append(dict(field=key,record=record,reason='patient_quote_or_measure_mismatch'))
        facts[key]=value if valid else None
    action=extraction['action'];kind=action['value'] if contains(action['quote'],q) else 'other'
    return kind,facts,errors


def evaluate(expr,facts):
    if isinstance(expr,bool):return 'MET' if expr else 'CONTRADICTED'
    if expr[0]=='test':
        _,field,op,value=expr;current=facts.get(field)
        return 'UNKNOWN' if current is None else ('MET' if OPS[op](current,value) else 'CONTRADICTED')
    return combine([evaluate(x,facts) for x in expr[1:]],expr[0]=='all')


def execute(item,action,facts,exception_policy='documented',rules=None):
    age=evaluate(['test','age_years','ge',65],facts);keys,_=option_keys(item);trace={}
    rules=relevant_rules(item) if rules is None else rules
    for k in keys:
        paths=[]
        for rule in rules:
            if item['options'][k].strip().casefold() not in rule['drugs'] or rule['action']!=action:continue
            when=combine([age,evaluate(rule['when'],facts)],True)
            exception=evaluate(rule['unless'],facts) if rule['unless'] is not None else 'CONTRADICTED'
            state=when
            if exception=='MET':state='CONTRADICTED'
            elif exception=='UNKNOWN' and when=='MET' and exception_policy=='strict':state='UNKNOWN'
            paths.append(dict(rule_id=rule['id'],prerequisites=when,exception=exception,state=state,
                used_default_recommendation=when=='MET' and exception=='UNKNOWN' and exception_policy=='documented'))
        trace[k]=dict(state=combine([p['state'] for p in paths],False),paths=paths)
    return trace


def assemble(item,initial_answer,trace,add_only=False):
    keys,none=option_keys(item)
    valid=isinstance(initial_answer,(list,tuple)) and bool(initial_answer) and all(k in item['options'] for k in initial_answer) and not (none in initial_answer and len(initial_answer)>1)
    if not valid and any(trace[k]['state']=='UNKNOWN' for k in keys):return None
    selected=set(initial_answer or [])-({none} if none else set()) if valid else set()
    for k in keys:
        if trace[k]['state']=='MET':selected.add(k)
        elif trace[k]['state']=='CONTRADICTED' and not add_only:selected.discard(k)
    return [k for k in keys if k in selected] or ([none] if none else None)


def check():
    assert evaluate(['test','crcl','lt',30],{'crcl':70})=='CONTRADICTED'
    assert evaluate(['test','crcl','lt',30],{'egfr':20})=='UNKNOWN'
    assert evaluate(['all',['test','a','eq',True],['test','b','eq',True]],{'a':True,'b':None})=='UNKNOWN'
    i=dict(answer_format='multi',options={'A':'Aripiprazole','B':'Quetiapine','C':'None of the above'},question='A 79-year-old woman.')
    fs={k:None for k in required_fields(i)};fs.update(age_years=79,parkinson=True,antipsychotic_accepted_indication=True)
    t=execute(i,'avoid',fs);assert t['A']['state']=='MET' and assemble(i,['C'],t)==['A']
    assert assemble(i,('C',),t)==assemble(i,['C'],t)==['A']
    assert assemble(i,('A','B'),{'A':{'state':'CONTRADICTED'},'B':{'state':'UNKNOWN'}})==['B']
    j=dict(i,options={'A':'Ibuprofen','B':'None of the above'})
    fs={k:None for k in required_fields(j)};fs.update(age_years=79,peptic_ulcer_history=True,gastroprotection=True)
    t=execute(j,'avoid',fs);p=next(x for x in t['A']['paths'] if x['rule_id']=='ulcer_nsaid')
    assert p['exception']=='UNKNOWN' and p['state']=='MET' and p['used_default_recommendation']
    fs['alternatives_ineffective']=True;p=next(x for x in execute(j,'avoid',fs)['A']['paths'] if x['rule_id']=='ulcer_nsaid');assert p['state']=='CONTRADICTED'
    print('PASS: numeric identity, unknown conjunction, PD class exception, full ulcer exception and native answer addition.')
