"""Resolve explicit medication question actions without interpreting patient facts."""
import re
from r2_program_head import execute, fields, relevant_rules


def requested_action(item):
    requests=re.findall(r'\b(?:which|what)\b[^?]*\?',item['question'],re.I)
    request=requests[-1] if requests else item['question'].split('\n\n')[-1]
    reduce=bool(re.search(r'\b(?:dose|dosage)\s+(?:reduction|adjustment)|\b(?:dose|dosage)s?\s+(?:be\s+)?(?:reduced|adjusted)\b',request,re.I))
    avoid=bool(re.search(r'\bavoid(?:ed|ance)?\b|\binappropriate\b|\bshould not be prescribed\b',request,re.I))
    return ('dose_reduce' if reduce else 'avoid') if reduce!=avoid else 'other'


def renal_question(item):
    questions=re.findall(r'\b(?:which|what)\b[^?\n]*\?',item['question'],re.I)
    q=questions[-1] if questions else ''
    return bool(re.search(r'\bgiven\b[^?]*\b(?:renal|kidney)\s+function\s*\?',q,re.I))


def execute_scoped(item,action,facts,policy='documented'):
    rules=relevant_rules(item)
    if renal_question(item):
        rules=[r for r in rules if (fields(r['when'])|fields(r['unless'])) & {'crcl','egfr'}]
    return execute(item,action,facts,policy,rules=rules)


def check():
    assert requested_action({'question':'CrCl is 85 mL/min. Which medicine requires dose reduction?'})=='dose_reduce'
    assert requested_action({'question':'A prior dose adjustment is mentioned. Which medicine should be avoided?'})=='avoid'
    assert requested_action({'question':'Which medicine requires dose reduction or avoidance?'})=='other'
    assert requested_action({'question':'Which medicine is potentially inappropriate?'})=='avoid'
    assert requested_action({'question':'Which medicine is most effective?'})=='other'
    print('PASS: explicit dose/avoid actions, patient-text separation, ambiguous combined action left unresolved.')


if __name__=='__main__':check()
