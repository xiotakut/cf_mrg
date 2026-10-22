"""One-call support audit for native choice tasks, independent of model/backend.

build_request(item, documents, initial_response) -> {messages, schema}
resolve(item, documents, audit) -> {answer, options, ...}
optimize(item, documents, initial_response, generate) performs both steps.
generate(messages, schema) must return a JSON string using the caller's model.
"""
import argparse
from itertools import permutations
import json
import operator
from pathlib import Path
import re

OPS = {'lt': operator.lt, 'le': operator.le, 'gt': operator.gt,
       'ge': operator.ge, 'eq': operator.eq, 'ne': operator.ne}
STATES = ['MET', 'CONTRADICTED', 'UNKNOWN']


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def option_keys(item):
    if item['answer_format'] not in ('single', 'multi'):
        raise ValueError('This interface currently supports single and multi choice tasks.')
    none = [k for k, v in item['options'].items() if v.strip().casefold() == 'none of the above']
    return [k for k in item['options'] if k not in none], next(iter(none), None)


def audit_schema(item, documents, review='support'):
    text = {'type': 'string'}
    props = {'recommend': {'type': 'boolean'}, 'reason': text}
    if review == 'support':
        value = {'anyOf': [{'type': 'number'}, {'type': 'boolean'}, {'type': 'null'}]}
        condition = obj(dict(premise=text, patient_quote=text, observed=value, required=value,
                            operator={'enum': list(OPS)}, patient_unit=text, rule_unit=text,
                            model_state={'enum': STATES}))
        rule = obj(dict(statement=text, source={'enum': ['model_knowledge', *[f'D{i}' for i in range(len(documents))]]},
                        source_quote=text, conditions={'type': 'array', 'items': condition}))
        # Installed xgrammar rejects minItems/maxItems; enforce bounds in resolve.
        props['rules'] = {'type': 'array', 'items': rule}
    options, _ = option_keys(item)
    result = {'options': obj({k: obj(props) for k in options})}
    if item['answer_format'] == 'single':
        result['ranking'] = {'enum': [list(p) for p in permutations(item['options'])]}
    return obj(result)


COMMON = '''Reconsider the ORIGINAL question using its exact wording and scope. The previous answer is a fallible draft, not evidence. Evaluate EVERY substantive option, including independently applicable reasons omitted from the draft. A general medical fact does not by itself establish that its patient-specific prerequisites hold. Only the QUESTION supplies current-patient facts; documents can supply medical knowledge but can describe other people. Explicitly absent and unmentioned patient facts differ. Do not assume any condition or answer changed merely because you are reviewing. For each option, recommend=true means that option belongs in the answer to the exact question asked, not that the treatment is beneficial or harmful in general. Do not evaluate None of the above as a substantive option: the caller derives it only when no substantive option is selected. For a single-choice task also rank all visible keys from most to least appropriate. Return only the requested JSON object. Keep reasons and quotes short.'''
SUPPORT = '''For each substantive option, give up to three distinct SUPPORT PATHS for selecting it, covering independent remaining reasons. Each path states a sufficient rule and ALL its prerequisites (one to four conditions per path); an exception is represented by the prerequisite that the exception is absent. Conditions within a path are AND; independent paths are OR. Include paths whose prerequisites are contradicted, so withdrawal is explicit. Losing one path does not remove another valid path. Do not call an option unsupported merely because one familiar contraindication is absent.
For a rule from a document, source is its D-number and source_quote is a short EXACT excerpt; use model_knowledge only for an explicitly stated rule recalled from model knowledge. It is not verified external evidence. For EACH condition: premise names the proposition tested; patient_quote is an EXACT short excerpt from the QUESTION about this patient, or an empty string if unmentioned. observed is the patient's numeric value, or a Boolean truth value for the stated proposition; required is the rule threshold or required Boolean value. Use null for unobserved information. State operator lt/le/gt/ge/eq/ne and model_state MET/CONTRADICTED/UNKNOWN. Express an interval as two conditions. Use numeric values in matching patient_unit and rule_unit; do not confuse CrCl, serum creatinine, and eGFR or convert units silently. Boolean conditions use eq/ne and empty units. For a pregnancy prerequisite, for example, the proposition is patient is pregnant, required=true; explicitly not pregnant means observed=false; unmentioned means observed=null. Numeric patient values must occur in patient_quote and numeric rule thresholds in source_quote (or statement for model_knowledge). Quote the full negation rather than a misleading fragment.
Finally give your provisional recommend decision for each option. The caller will independently execute the comparisons, combine support paths, and assemble the answer. If no support path can be identified, return an empty rules list and explain your provisional decision. Do not invent a rule or patient condition just to fill a list.'''


def build_request(item, documents, initial_response, review='support'):
    schema = audit_schema(item, documents, review)
    # Only these visible fields cross the inference boundary. No labels or gold.
    visible = {k: item[k] for k in ['question', 'options', 'answer_format', 'fixed_evidence']}
    payload = dict(question=visible, documents={f'D{i}': d for i, d in enumerate(documents)},
                   previous_answer=initial_response)
    instruction = COMMON + ('\n\n' + SUPPORT if review == 'support' else '\nJudge each option carefully for factual accuracy, applicability and completeness.')
    return dict(messages=[dict(role='system', content='You are auditing a medical benchmark answer for research. Follow the requested internal audit format.'),
                          dict(role='user', content=json.dumps(payload, ensure_ascii=False)+'\n\n'+instruction)], schema=schema)


def contains(quote, text):
    return bool(quote.strip()) and ' '.join(quote.split()) in ' '.join(text.split())


def has_number(value, text):
    return any(float(n) == value for n in re.findall(r'(?<![\d.])[-+]?\d+(?:\.\d+)?', text))


def condition_state(condition, rule, item, documents, execution):
    c = condition
    if not contains(c['patient_quote'], item['question']):
        return 'UNKNOWN', 'missing_patient_quote'
    if rule['source'] != 'model_knowledge':
        source = documents[int(rule['source'][1:])]
        if not contains(rule['source_quote'], source):
            return 'UNKNOWN', 'missing_rule_quote'
    observed, required = c['observed'], c['required']
    if observed is None or required is None:
        return 'UNKNOWN', 'unobserved_value'
    if isinstance(observed, bool) or isinstance(required, bool):
        if not (isinstance(observed, bool) and isinstance(required, bool) and c['operator'] in ('eq', 'ne')):
            return 'UNKNOWN', 'incompatible_boolean_comparison'
    else:
        if ''.join(c['patient_unit'].lower().split()) != ''.join(c['rule_unit'].lower().split()):
            return 'UNKNOWN', 'unit_mismatch'
        source_text = rule['statement'] if rule['source'] == 'model_knowledge' else rule['source_quote']
        if not has_number(observed, c['patient_quote']) or not has_number(required, source_text):
            return 'UNKNOWN', 'number_not_in_quote'
    if execution == 'model':
        return c['model_state'], 'model_comparison'
    result = OPS[c['operator']](observed, required)
    return ('MET' if result else 'CONTRADICTED'), 'executed_comparison'


def combine(states, conjunction):
    if conjunction:
        return 'CONTRADICTED' if 'CONTRADICTED' in states else ('MET' if states and all(s == 'MET' for s in states) else 'UNKNOWN')
    return 'MET' if 'MET' in states else ('CONTRADICTED' if states and all(s == 'CONTRADICTED' for s in states) else 'UNKNOWN')


def resolve(item, documents, audit, execution='execute'):
    """execution='model' ablates comparisons; 'recommend' reads audit decisions."""
    keys, none = option_keys(item)
    if set(audit['options']) != set(keys):
        raise ValueError('Every substantive option must be audited exactly once.')
    trace, selected = {}, []
    for key in keys:
        proposal = audit['options'][key]
        if 'rules' in proposal and (len(proposal['rules']) > 3 or any(not 1 <= len(p['conditions']) <= 4 for p in proposal['rules'])):
            raise ValueError('Support audit requires at most 3 paths, each with 1 to 4 conditions.')
        paths = []
        if execution != 'recommend':
            for rule in proposal['rules']:
                checks = [dict(condition=c, state=s, basis=b) for c in rule['conditions']
                          for s, b in [condition_state(c, rule, item, documents, execution)]]
                paths.append(dict(rule=rule, checks=checks, state=combine([c['state'] for c in checks], True)))
        state = combine([p['state'] for p in paths], False)
        # Unknown is not evidence of absence. Use the auditor's provisional
        # decision, not a blanket freeze of the original method's answer.
        choose = state == 'MET' if state != 'UNKNOWN' else proposal['recommend']
        if choose:
            selected.append(key)
        trace[key] = dict(state=state, selected=choose, provisional=proposal['recommend'],
                          used_provisional=state == 'UNKNOWN', paths=paths)
    if item['answer_format'] == 'multi':
        answer = selected or ([none] if none else None)
    else:
        ranking = audit['ranking']
        if set(ranking) != set(item['options']) or len(ranking) != len(item['options']):
            raise ValueError('Single-choice ranking must cover every visible option.')
        answer = next((k for k in ranking if k in selected), none if not selected else None)
    return dict(answer=answer, options=trace, execution=execution,
                status='answered' if answer is not None else 'no_supported_choice')


def optimize(item, documents, initial_response, generate):
    request = build_request(item, documents, initial_response)
    raw = generate(request['messages'], request['schema'])
    audit = json.loads(raw)
    return dict(resolve(item, documents, audit), audit=audit, raw_audit=raw)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['request', 'resolve'])
    parser.add_argument('input', type=Path, help='JSON with item, documents, initial_response; resolve also requires audit')
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    if args.action == 'request':
        result = build_request(data['item'], data['documents'], data['initial_response'])
    else:
        result = resolve(data['item'], data['documents'], data['audit'])
    print(json.dumps(result, ensure_ascii=False, indent=2))
