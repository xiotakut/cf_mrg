"""Independent, one-call R2 condition head using the caller's original model.

optimize(item, initial_answer, generate) -> answer plus executed support trace.
generate(messages, schema) returns a JSON string. initial_answer is a parsed
native answer to THIS SAME current question, or None for an invalid initial.
No gold, R label, previous patient, model path or evaluation loader is used.
"""
import json
from r2_positive_facts import build_request,clean_extraction
from r2_program_head import eligible,assemble
from r2_action_scope import execute_scoped,renal_question


def resolve(item,initial_answer,extraction):
    if not eligible(item):return dict(answer=initial_answer,applied=False,reason='outside_rule_coverage')
    action,facts,errors=clean_extraction(item,extraction)
    trace=execute_scoped(item,action,facts)
    answer=assemble(item,initial_answer,trace)
    return dict(answer=answer if answer is not None else initial_answer,applied=answer is not None,
                reason='support_recomputed' if answer is not None else 'unresolved_support_without_valid_initial_answer',
                action=action,scope='renal' if renal_question(item) else 'general',facts=facts,options=trace,evidence_errors=errors)


def optimize(item,initial_answer,generate):
    if not eligible(item):return dict(answer=initial_answer,applied=False,reason='outside_rule_coverage')
    request=build_request(item)
    raw=generate(request['messages'],request['schema'])
    try:return resolve(item,initial_answer,json.loads(raw))
    except (ValueError,KeyError,TypeError) as exc:
        return dict(answer=initial_answer,applied=False,reason='invalid_fact_extraction',error=f'{type(exc).__name__}: {exc}')


def check():
    item=dict(question='A 78-year-old woman has creatinine clearance (CrCl) 55 mL/min. Which medicines require dose reduction given her renal function?',
              answer_format='multi',options={'A':'Gabapentin','B':'Famotidine','C':'None of the above'})
    extraction=dict(facts=dict(age_years=dict(value=78,evidence_ids=['S0']),crcl=dict(value=55,evidence_ids=['S0'])))
    calls=[]
    def generate(messages,schema):calls.append(messages);return json.dumps(extraction)
    result=optimize(item,('B',),generate)
    assert len(calls)==1 and result['answer']==['A'] and result['applied']
    assert result['options']['A']['state']=='MET' and result['options']['B']['state']=='CONTRADICTED'
    assert optimize(item,['C'],lambda *_:'unfinished')['answer']==['C']
    outside=dict(item,question='A 48-year-old woman asks about medication.')
    assert optimize(outside,['B'],lambda *_:(_ for _ in ()).throw(AssertionError('must not call model')))['answer']==['B']
    print('PASS: one original-model callback, threshold removal/retention, invalid extraction and uncovered passthrough.')


if __name__=='__main__':check()
