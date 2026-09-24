"""Bind supported quantitative propositions directly; compile a typed insulin edit."""
import json
import re

import head as v1

ARMS = ('full', 'patch')
NUMBER, INTEGER = v1.NUMBER, v1.INTEGER


def action_schema(kind, fields):
    return v1.obj(dict(kind=dict(type='string', enum=[kind]), **fields))


ACTION = dict(anyOf=[
    action_schema('scale_basal', dict(start_min=INTEGER,end_min=INTEGER,multiplier=NUMBER)),
    action_schema('remove_bolus', dict(time_min=INTEGER)),
    action_schema('move_bolus', dict(from_time_min=INTEGER,to_time_min=INTEGER)),
    action_schema('set_bolus', dict(time_min=INTEGER,units=NUMBER))])
SCHEMAS = dict(redo=v1.SCHEMAS['redo'],
    full=v1.obj(dict(basal=v1.SCHEMAS['full']['properties']['basal'],
        boluses=v1.SCHEMAS['full']['properties']['boluses'], **v1.ANSWER)),
    patch=v1.obj(dict(intervention=ACTION, **v1.ANSWER)))

INSTRUCTIONS = {
    'full': v1.INSTRUCTIONS['full'].split('\nquery records')[0] + '''
Compile basal and boluses first, then give your own inline estimates and answer.
The program reads the requested time and inequality directly from the original question.
Do not rewrite the query or add segments outside [0,horizon_min).''',
    'patch': '''First compile the single requested change as an intervention object:
scale_basal: start_min, end_min, multiplier, applied only over [start_min,end_min).
remove_bolus: time_min identifies the original bolus to remove.
move_bolus: from_time_min identifies the original bolus and to_time_min its new start; its units are preserved.
set_bolus: time_min identifies the original bolus and units is its new dose; its start is preserved.
Use exactly the kind and fields for that change. The program preserves all unmodified events,
the meal and full initial state. A one-minute bolus starting at minute 0 has time_min=0, not 1.
After compiling intervention, give your own inline estimates and answer.
The program reads the requested time and inequality directly from the original question;
do not rewrite query fields or try to encode your inline answer into the intervention.'''}


def query_from_question(question):
    """A declared three-form grammar, with arbitrary visible magnitudes and times."""
    question = ' '.join(question.split())
    match = re.search(r'\bWould (.+?) if ', question, re.IGNORECASE)
    if not match:
        raise ValueError('No supported final counterfactual proposition')
    number = r'([0-9]+(?:\.[0-9]+)?)'
    prefix = r'counterfactual subcutaneous glucose \(Gsub\) be '
    suffix = r' at minute ([0-9]+)'
    forms = [
        (prefix+r'at least '+number+r' mg/dL lower than factual Gsub'+suffix, 'difference','le',-1),
        (prefix+r'at least '+number+r' mg/dL'+suffix, 'counterfactual','ge',1),
        (prefix+r'below '+number+r' mg/dL'+suffix, 'counterfactual','lt',1)]
    for pattern,quantity,comparison,sign in forms:
        found = re.fullmatch(pattern, match[1], re.IGNORECASE)
        if found:
            return dict(time_min=int(found[2]),readout='gsub',quantity=quantity,
                comparison=comparison,threshold=sign*float(found[1]))
    raise ValueError('Proposition outside the declared quantitative grammar')


def request(native_input, question, arm='patch'):
    if arm=='redo':
        return v1.request(native_input,question,arm)
    import json
    source=(v1.HERE.parent/'physiology_probe/author/simglucose/patient/t1dpatient.py').read_text()
    return [dict(role='system',content=v1.COMMON+'\n\n'+INSTRUCTIONS[arm]),
        dict(role='user',content='Supplied author patient model (Python):\n'+source+
            '\n\nComplete visible input (JSON):\n'+json.dumps(native_input,ensure_ascii=False)+
            '\n\nCounterfactual question:\n'+question+'\n\nOutput schema:\n'+json.dumps(SCHEMAS[arm]))]


def compile_edit(native_input, action, query):
    kind=action['kind']
    result=dict(basal_changes=[],bolus_changes=[],query=query)
    if kind=='scale_basal':
        result['basal_changes']=[{k:action[k] for k in ('start_min','end_min','multiplier')}]
    elif kind in ('remove_bolus','move_bolus','set_bolus'):
        origin=action['from_time_min'] if kind=='move_bolus' else action['time_min']
        matches=[b for b in native_input['factual_boluses'] if b['time_min']==origin]
        if len(matches)!=1:
            raise ValueError('Requested source bolus is not unique')
        units=0 if kind=='remove_bolus' else action['units'] if kind=='set_bolus' else matches[0]['units']
        destination=action['to_time_min'] if kind=='move_bolus' else origin
        result['bolus_changes']=[dict(from_time_min=origin,to_time_min=destination,units=units)]
    else:
        raise ValueError('Unsupported intervention kind')
    return result


def tool_fields(raw, parsed, arm):
    """Read complete JSON tool values independently of malformed inline prose."""
    keys=('intervention',) if arm=='patch' else ('basal','boluses')
    result={}
    for key in keys:
        if key in parsed:
            result[key]=parsed[key]
            continue
        for match in re.finditer(r'"'+key+r'"\s*:',raw):
            try:
                value,_=json.JSONDecoder().raw_decode(raw[match.end():].lstrip())
            except ValueError:
                continue
            result[key]=value
            break
        if key not in result:
            raise ValueError('Missing complete JSON tool field: '+key)
    return result


def restrict_horizon(native_input, fields):
    """A stronger full-plan control: ignore actions after the modeled window."""
    horizon=native_input['horizon_min']
    basal,boluses,cropped=[],[],[]
    for segment in fields['basal']:
        start,end=v1.finite(segment['start_min']),v1.finite(segment['end_min'])
        if int(start)!=start or int(end)!=end:
            raise ValueError('Basal boundary is not an integer minute')
        if start>=horizon:
            cropped.append(dict(kind='outside_basal',original=segment))
            continue
        if end>horizon:
            cropped.append(dict(kind='clipped_basal_end',original=segment))
        basal.append(dict(segment,end_min=min(end,horizon)))
    for bolus in fields['boluses']:
        t=v1.finite(bolus['time_min'])
        if int(t)!=t:
            raise ValueError('Bolus start is not an integer minute')
        if t>=horizon:
            cropped.append(dict(kind='outside_bolus',original=bolus))
        else:
            boluses.append(bolus)
    return dict(basal=basal,boluses=boluses),cropped


def optimize(native_input, question, generate, arm='patch'):
    raw=generate(request(native_input,question,arm),SCHEMAS[arm])
    parsed=v1.parse(raw)
    if arm=='redo':
        result=dict(route='inline',answer=parsed)
    else:
        try:
            query=query_from_question(question)
            fields=tool_fields(raw,parsed,arm)
            cropped=[]
            if arm=='patch':
                compiled=compile_edit(native_input,fields['intervention'],query)
            else:
                fields,cropped=restrict_horizon(native_input,fields)
                compiled=dict(fields,query=query)
            result=v1.project(native_input,compiled,arm)
            result['tool_fields']=fields
            result['cropped_outside_window']=cropped
            result['inline_json_valid']=bool(parsed)
            if result['route']=='inline_fallback':
                result['answer']=parsed
        except (ValueError,KeyError,TypeError,IndexError) as error:
            result=dict(route='inline_fallback',reason=str(error),answer=parsed)
    return dict(raw_response=raw,inline=parsed,calls=1,**result)


def check():
    q='Would counterfactual subcutaneous glucose (Gsub) be at least 3.5 mg/dL lower than factual Gsub at minute 80 if the bolus changed?'
    assert query_from_question(q)==dict(time_min=80,readout='gsub',quantity='difference',comparison='le',threshold=-3.5)
    q=q.replace('at least 3.5 mg/dL lower than factual Gsub','below 111 mg/dL')
    assert query_from_question(q)['threshold']==111 and query_from_question(q)['comparison']=='lt'
    native=dict(horizon_min=120,factual_boluses=[dict(time_min=0,units=2),dict(time_min=90,units=1)])
    changed=compile_edit(native,dict(kind='move_bolus',from_time_min=0,to_time_min=30),{})
    assert v1.patch_plan(native,changed)['boluses']==[dict(time_min=30,units=2),dict(time_min=90,units=1)]
    changed=compile_edit(native,dict(kind='remove_bolus',time_min=0),{})
    assert v1.patch_plan(native,changed)['boluses']==[dict(time_min=90,units=1)]
    malformed='{"intervention":{"kind":"remove_bolus","time_min":0},"step_by_step_thinking":"ok",},"answer_choice":"no"}'
    assert not v1.parse(malformed)
    assert tool_fields(malformed,{},'patch')['intervention']==dict(kind='remove_bolus',time_min=0)
    full=dict(basal=[dict(start_min=0,end_min=180,multiplier=1),dict(start_min=180,end_min=240,multiplier=1)],
        boluses=[dict(time_min=0,units=2),dict(time_min=120,units=1)])
    bounded,cropped=restrict_horizon(native,full)
    assert bounded==dict(basal=[dict(start_min=0,end_min=120,multiplier=1)],boluses=[dict(time_min=0,units=2)])
    assert len(cropped)==3
    print('PASS: visible arbitrary-magnitude query projection and typed edit background preservation')


if __name__=='__main__':
    check()
