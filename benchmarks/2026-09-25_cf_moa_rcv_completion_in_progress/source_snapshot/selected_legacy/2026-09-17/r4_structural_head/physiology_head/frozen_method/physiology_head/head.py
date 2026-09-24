"""One-call intervention binding over an explicitly supplied physiological model."""
import copy
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ('redo', 'full', 'patch')


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def array(properties):
    return dict(type='array', items=obj(properties))


NUMBER = dict(type='number')
INTEGER = dict(type='integer')
QUERY = obj(dict(time_min=INTEGER, readout=dict(type='string', enum=['gsub']),
    quantity=dict(type='string', enum=['counterfactual', 'difference']),
    comparison=dict(type='string', enum=['ge', 'le', 'lt']), threshold=NUMBER))
ANSWER = dict(step_by_step_thinking=dict(type='string'),
    counterfactual_value=NUMBER, difference=NUMBER,
    answer_choice=dict(type='string', enum=['yes', 'no']))
SCHEMAS = {'redo': obj(ANSWER),
    'full': obj(dict(**ANSWER, query=QUERY,
        basal=array(dict(start_min=INTEGER, end_min=INTEGER, multiplier=NUMBER)),
        boluses=array(dict(time_min=INTEGER, units=NUMBER)))),
    'patch': obj(dict(**ANSWER, query=QUERY,
        basal_changes=array(dict(start_min=INTEGER, end_min=INTEGER, multiplier=NUMBER)),
        bolus_changes=array(dict(from_time_min=INTEGER, to_time_min=INTEGER, units=NUMBER))))}

COMMON = '''Evaluate a counterfactual in the explicitly supplied virtual-patient model.
Use the supplied equations, parameters, complete initial state, and initial auxiliary memory.
The question is conditional on this model, not a claim about a real patient's treatment.
Keep the patient, initial state, meal announcements, and all unmodified insulin events fixed.
Time t is the state after exactly t minutes. Inputs at minute t apply over [t,t+1).
A meal is announced once at its listed minute; the author's step handles its 5 g/min queue.
Each bolus is a one-minute pulse: units U are added to that minute's basal rate in U/min.
Basal multipliers in tool plans are relative to the supplied factual basal rate, not total insulin.
The author's dopri5 solver uses rtol=1e-6, atol=1e-12 with one-minute patient steps.
Gsub is the noiseless subcutaneous glucose state[12]/Vg in mg/dL; it is not plasma glucose.
Counterfactual value and difference always refer to Gsub at the requested time, before rounding.
Difference means counterfactual minus factual, using the same patient and meal in both worlds.
Answer the exact inequality in the question; equality is included only for >= or <=.
Return JSON with a brief explanation, your own numeric estimates counterfactual_value and difference,
and answer_choice exactly yes or no. These estimates are your inline answer, separate from the tool plan.'''
INSTRUCTIONS = {
    'redo': 'Reason directly from the supplied model and data to answer. Return only the four answer fields.',
    'full': '''Also compile a complete counterfactual insulin schedule for the supplied simulator.
basal lists nonoverlapping segments covering the whole [0,horizon_min), each with start_min,
end_min, multiplier relative to factual basal. Include every unchanged basal segment as well.
boluses lists every counterfactual bolus with time_min and units, including unchanged boluses.
Omitted boluses do not occur. The tool will evaluate this complete schedule.
query records time_min, readout="gsub", quantity="counterfactual" or "difference",
comparison="ge" for >=, "le" for <=, or "lt" for <, and threshold in mg/dL.''',
    'patch': '''Also compile only the intervention edits for the supplied simulator.
basal_changes lists only changed intervals, with start_min, end_min, multiplier relative to factual basal.
Outside those intervals the tool preserves factual basal automatically. Use [] if basal is unchanged.
bolus_changes lists only modified factual events: from_time_min identifies the original event;
to_time_min and units give its replacement. For deletion use units=0 and keep its original time.
All unmentioned factual boluses remain unchanged. Use [] if no bolus changes.
Do not put meals or initial-state changes in an insulin intervention.
query records time_min, readout="gsub", quantity="counterfactual" or "difference",
comparison="ge" for >=, "le" for <=, or "lt" for <, and threshold in mg/dL.'''}


def request(native_input, question, arm='patch'):
    source = (HERE.parent / 'physiology_probe/author/simglucose/patient/t1dpatient.py').read_text()
    return [dict(role='system', content=COMMON + '\n\n' + INSTRUCTIONS[arm]),
        dict(role='user', content='Supplied author patient model (Python):\n' + source +
            '\n\nComplete visible input (JSON):\n' + json.dumps(native_input, ensure_ascii=False) +
            '\n\nCounterfactual question:\n' + question + '\n\nOutput schema:\n' + json.dumps(SCHEMAS[arm]))]


def parse(raw):
    decoder = json.JSONDecoder()
    for i, ch in enumerate(raw):
        if ch == '{':
            try:
                value, _ = decoder.raw_decode(raw[i:])
            except ValueError:
                continue
            if isinstance(value, dict) and 'answer_choice' in value:
                return value
    return {}


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Nonfinite or nonnumeric tool value')
    return value


def minute(value, horizon, endpoint=False):
    upper = horizon if endpoint else horizon - 1
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or int(value) != value or not 0 <= value <= upper:
        raise ValueError('Minute outside simulation horizon')
    return int(value)


def patch_plan(native_input, parsed):
    """Apply only explicitly compiled changes; preserve the factual background."""
    horizon = native_input['horizon_min']
    multipliers = [1.] * horizon
    touched = set()
    for change in parsed['basal_changes']:
        start = minute(change['start_min'], horizon)
        end = minute(change['end_min'], horizon, endpoint=True)
        factor = finite(change['multiplier'])
        if end <= start or factor < 0 or touched.intersection(range(start, end)):
            raise ValueError('Invalid or overlapping basal change')
        touched.update(range(start, end))
        multipliers[start:end] = [factor] * (end - start)
    segments = []
    for t, factor in enumerate(multipliers):
        if segments and segments[-1]['multiplier'] == factor:
            segments[-1]['end_min'] = t + 1
        else:
            segments.append(dict(start_min=t, end_min=t+1, multiplier=factor))
    boluses = copy.deepcopy(native_input['factual_boluses'])
    modified = set()
    for change in parsed['bolus_changes']:
        origin = minute(change['from_time_min'], horizon)
        destination = minute(change['to_time_min'], horizon)
        units = finite(change['units'])
        matches = [i for i, event in enumerate(native_input['factual_boluses']) if event['time_min'] == origin]
        if len(matches) != 1 or origin in modified or units < 0:
            raise ValueError('Ambiguous, repeated or invalid bolus change')
        modified.add(origin)
        boluses[matches[0]] = dict(time_min=destination, units=units)
    return dict(basal=segments, boluses=[b for b in boluses if b['units'] != 0], query=parsed['query'])


def project(native_input, parsed, arm='patch', no_do=False):
    if arm == 'redo':
        return dict(route='inline', answer=parsed)
    from executor import execute
    try:
        plan = patch_plan(native_input, parsed) if arm == 'patch' else {
            key: parsed[key] for key in ('basal', 'boluses', 'query')}
        outcome = execute(native_input, plan, no_do=no_do)
        return dict(route='executed', answer={key: outcome[key] for key in
            ('counterfactual_value', 'difference', 'answer_choice')}, plan=plan, execution=outcome)
    except (ValueError, KeyError, TypeError, IndexError, RuntimeError) as error:
        return dict(route='inline_fallback', reason=str(error), answer=parsed)


def optimize(native_input, question, generate, arm='patch'):
    raw = generate(request(native_input, question, arm), SCHEMAS[arm])
    parsed = parse(raw)
    result = project(native_input, parsed, arm)
    return dict(raw_response=raw, inline=parsed, calls=1, **result)


def check():
    native = dict(horizon_min=120, factual_boluses=[dict(time_min=0, units=2),dict(time_min=90, units=1)])
    parsed = dict(basal_changes=[dict(start_min=0,end_min=60,multiplier=.5)],
        bolus_changes=[dict(from_time_min=0,to_time_min=30,units=2)],query={})
    result = patch_plan(native, parsed)
    assert result['basal'] == [dict(start_min=0,end_min=60,multiplier=.5),dict(start_min=60,end_min=120,multiplier=1.)]
    assert result['boluses'] == [dict(time_min=30,units=2),dict(time_min=90,units=1)]
    assert native['factual_boluses'][0]['time_min'] == 0
    parsed['bolus_changes'][0]['units'] = 0
    assert patch_plan(native, parsed)['boluses'] == [dict(time_min=90,units=1)]
    parsed['basal_changes'].append(dict(start_min=30,end_min=60,multiplier=2))
    try:
        patch_plan(native, parsed)
    except ValueError:
        pass
    else:
        raise AssertionError('Overlapping changes silently accepted')
    assert parse('```json\n{"answer_choice":"no"}\n```')['answer_choice'] == 'no'
    print('PASS: background preservation, interval end, moved/deleted bolus, overlap rejection and JSON parsing')


if __name__ == '__main__':
    check()
