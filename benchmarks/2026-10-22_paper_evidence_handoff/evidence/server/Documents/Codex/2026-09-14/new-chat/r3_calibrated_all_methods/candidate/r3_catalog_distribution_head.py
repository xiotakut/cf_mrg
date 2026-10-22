"""Original-model scores over a public catalog, aligned across fixed permutations."""
from collections import Counter
import math
import random

from r3_ontology_head import CODES, build_request


def orders(catalog):
    result = [list(catalog)]
    rng = random.Random(20260916)
    for _ in range(5):
        other = list(catalog)
        rng.shuffle(other)
        result.append(other)
    return result


def request(item, context, catalog):
    result = build_request(item, context, catalog, 'code', False)
    prefix = 'Current patient case:\n' + item['question'] + '\n\n'
    if 'messages' in result:
        result['messages'][-1] = dict(result['messages'][-1], content=prefix + result['messages'][-1]['content'])
    else:
        instruction = build_request(item, [], catalog, 'code', False)['messages'][-1]['content']
        suffix = instruction + '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
        assert result['prompt'].endswith(suffix)
        result['prompt'] = result['prompt'][:-len(suffix)] + prefix + suffix
    return result


def aggregate(catalog, permutations, scores):
    assert len(permutations) == len(scores) and len(set(catalog)) == len(catalog)
    probabilities, winners = [], []
    for names, values in zip(permutations, scores):
        assert set(names) == set(catalog)
        if set(values) != set(CODES[:len(names)]):
            raise ValueError('Incomplete model code scores')
        if not all(math.isfinite(v) for v in values.values()):
            raise ValueError('Non-finite model score')
        peak = max(values.values())
        weights = [math.exp(values[CODES[i]] - peak) for i in range(len(names))]
        total = sum(weights)
        probabilities.append({name: weight / total for name, weight in zip(names, weights)})
        # Public catalog order is the fixed tie-break, independent of the displayed permutation.
        winners.append(max(catalog, key=probabilities[-1].get))
    mean = {name: sum(p[name] for p in probabilities) / len(probabilities) for name in catalog}
    votes = Counter(winners)
    return dict(per_order=winners, mean_probabilities=mean,
                mean_probability=max(catalog, key=mean.get),
                majority_vote=max(catalog, key=lambda name: (votes[name], mean[name])))


def optimize(item, original_context, original_answer, public_catalog, score_codes):
    if item['answer_format'] != 'diagnosis':
        return dict(answer=original_answer, used_original=True)
    permutations = orders(public_catalog)
    scores = [score_codes(**request(item, original_context, names)) for names in permutations]
    try:
        result = aggregate(public_catalog, permutations, scores)
    except (ValueError, KeyError, TypeError) as exc:
        return dict(answer=original_answer, used_original=True, error=str(exc))
    return dict(answer=result['mean_probability'], used_original=False, details=result)


def calibrate(scores, log_priors):
    return [{c:v-log_priors[k][c] for c,v in values.items()} for k,values in enumerate(scores)]


def optimize_calibrated(item, original_context, original_answer, public_catalog, log_priors, score_codes):
    """Six-order calibrated majority; priors come from fixed content-free original-model calls."""
    if item['answer_format'] != 'diagnosis':
        return dict(answer=original_answer, used_original=True)
    permutations = orders(public_catalog)
    scores = [score_codes(**request(item, original_context, names)) for names in permutations]
    try:
        result = aggregate(public_catalog, permutations, calibrate(scores, log_priors))
    except (ValueError, KeyError, TypeError) as exc:
        return dict(answer=original_answer, used_original=True, error=str(exc))
    return dict(answer=result['majority_vote'], used_original=False, details=result)


def check():
    catalog = ['Disease A', 'Disease B', 'Disease C']
    permutations = orders(catalog)
    values = [{CODES[i]: (-1.0 if name == 'Disease B' else -4.0) for i, name in enumerate(names)}
              for names in permutations]
    result = aggregate(catalog, permutations, values)
    assert result['per_order'] == ['Disease B'] * 6
    assert result['mean_probability'] == result['majority_vote'] == 'Disease B'
    item = dict(answer_format='diagnosis', question='Patient observation.')
    context = [dict(role='user', content='Native patient and evidence')]
    calls = []
    def callback(**kwargs):
        assert kwargs['messages'][:-1] == context
        assert kwargs['messages'][-1]['content'].startswith('Current patient case:\nPatient observation.')
        calls.append(kwargs)
        return values[len(calls)-1]
    assert optimize(item, context, 'Old diagnosis', catalog, callback)['answer'] == 'Disease B'
    assert len(calls) == 6 and len(context) == 1
    assert optimize(dict(answer_format='single_choice'), context, 'A', [], None)['answer'] == 'A'
    failed = optimize(item, context, 'Old diagnosis', catalog, lambda **_: dict(A=float('nan'), B=-1, C=-2))
    assert failed['used_original'] and failed['answer'] == 'Old diagnosis'
    # A 3:1 score preference is reversed by a stronger 9:1 content-free preference.
    raw = [dict(A=math.log(.75), B=math.log(.25))]
    prior = [dict(A=math.log(.9), B=math.log(.1))]
    assert calibrate(raw,prior)[0]['B'] > calibrate(raw,prior)[0]['A']
    missing = optimize_calibrated(item, context, 'Old diagnosis', catalog,
                  [dict(A=-1, B=-1, C=-1)]*6, lambda **_: dict(A=-1, B=-2))
    assert missing['used_original'] and missing['answer'] == 'Old diagnosis'
    print('PASS: disease-aligned aggregation, six original-model callbacks, native context, and true fallback.')


if __name__ == '__main__':
    check()
