"""R5 full-input candidate; pending final controls and semantic output review.

Only Python standard-library dependencies. The caller supplies original-model
callbacks; no data, source identities, pairing, or benchmark labels are loaded.
"""
from collections import Counter
from copy import deepcopy
import json
import math

SEED = 42
SEEDS = (42, 43, 44, 45, 46)
CODES = ('A', 'B')
RELATION_KEYS = ('higher', 'lower', 'no difference', 'uncertainty')
RULE = ('For the CURRENT question, positive means that the entire hypothesis is supported by '
        'its premise; negative means that it is not fully supported by that premise. '
        'Evaluate the exact entities, roles, direction, quantities and negation as written. '
        'Other questions and example labels are not the current premise or hypothesis.')



def native_keys(item):
    if item['answer_format'] == 'relation':
        return list(RELATION_KEYS)
    if item['answer_format'] not in ('single', 'robustness_single'):
        raise ValueError('Unsupported native answer format')
    keys = list(item['options'])
    if not keys:
        raise ValueError('Native choices are required')
    return keys


def request(item, messages, view='full'):
    if view != 'full':
        raise ValueError('This frozen candidate uses the full original input')
    instruction = (
        'Answer the current question using the complete input. Return one JSON '
        'object only, with every field required by the original task. Keep '
        'step_by_step_thinking concise and preserve the errors array when required. '
        'answer_choice must be exactly one of these native keys: '
        + json.dumps(native_keys(item), ensure_ascii=False) + '.')
    return [*messages, {'role': 'user', 'content': instruction}]


def constrained_schema(item, schema):
    """Keep the caller's native fields; constrain only the answer-choice enum."""
    result = deepcopy(schema)
    result['properties']['answer_choice']['enum'] = native_keys(item)
    return result


def aggregate(item, responses):
    """Vote over valid keys; return an entire original sample, never a splice.

    Parsing is deliberately exact: no prose/fence extraction or key conversion.
    Other task fields, such as document corrections, are scored independently.
    With no valid vote, draw zero remains unchanged and invalid.
    """
    if not responses:
        raise ValueError('At least one response is required')
    keys = native_keys(item)
    predictions, invalid_reasons = [], []
    for raw in responses:
        try:
            obj = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            prediction, reason = None, 'not_a_complete_json_value'
        else:
            if not isinstance(obj, dict):
                prediction, reason = None, 'not_a_json_object'
            elif obj.get('answer_choice') not in keys:
                prediction, reason = None, 'answer_choice_not_a_native_key'
            else:
                prediction, reason = obj['answer_choice'], None
        predictions.append(prediction)
        invalid_reasons.append(reason)
    counts = Counter(p for p in predictions if p is not None)
    leaders = [key for key, count in counts.items() if count == max(counts.values())]
    selected = next((i for i, key in enumerate(predictions) if key in leaders), 0)
    return dict(raw_response=responses[selected], selected_index=selected,
                answer_choice=predictions[selected], vote_counts=dict(counts),
                valid_votes=sum(counts.values()), total_votes=len(responses),
                predictions=predictions, invalid_reasons=invalid_reasons,
                tied_choices=leaders if len(leaders) > 1 else [])


def is_nli(item):
    question = item.get('question', '')
    return (item.get('answer_format') == 'single'
            and set(item.get('options') or {}) == {'positive', 'negative'}
            and isinstance(question, str)
            and question.startswith('what is the relationship between premise:')
            and ' hypothesis:' in question)



def nli_keys(item):
    keys = list(item['options'])
    assert item['answer_format'] == 'single' and set(keys) == {'positive', 'negative'}
    assert item['question'].startswith('what is the relationship between premise:')
    assert ' hypothesis:' in item['question']
    return keys


def nli_mappings(item):
    keys = nli_keys(item)
    return [keys, keys[::-1]]


def nli_target(item):
    return '<CURRENT_QUESTION>\n' + item['question'] + '\n</CURRENT_QUESTION>'


def nli_analysis_request(item, messages):
    nli_keys(item)
    instruction = (nli_target(item) + '\n\n' + RULE + '\nAnalyze only this current premise and '
        'hypothesis. Explain briefly whether the entire hypothesis is supported, preserving '
        'the statements as written. This is an intermediate analysis step.')
    return [*messages, dict(role='user', content=instruction)]


def nli_request(item, messages, names, analysis=None):
    assert names in nli_mappings(item)
    instruction = (nli_target(item) + '\n\n' + RULE + '\nUse this code mapping:\n' +
        '\n'.join(f'{code} = {name}' for code, name in zip(CODES, names)) +
        '\nSelect the code for the current relationship. Return only the JSON answer_choice '
        'field containing the case-sensitive code A or B; no explanation.')
    prior = [] if analysis is None else [dict(role='assistant', content=analysis)]
    return [*messages, *prior, dict(role='user', content=instruction)]


def catalog_aggregate(catalog, permutations, scores):
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


def aggregate_code_scores(item, scores):
    result = catalog_aggregate(nli_keys(item), nli_mappings(item), scores)
    return dict(answer_choice=result['mean_probability'], **result)



def decide_paths(item,messages,score_codes,analyze):
    """score_codes(messages,seed)->{A:raw_logp,B:raw_logp}; analyze(messages,seed)->str.

    Call order: direct score 0, direct score 1, new response, reasoned score 0,
    reasoned score 1. Returns an intermediate native choice and untouched response.
    """
    mappings=nli_mappings(item)
    direct_scores=[score_codes(nli_request(item,messages,names),SEED) for names in mappings]
    direct=aggregate_code_scores(item,direct_scores)
    analysis=analyze(nli_analysis_request(item,messages),SEED)
    assert isinstance(analysis,str)
    reasoned_scores=[score_codes(nli_request(item,messages,names,analysis),SEED) for names in mappings]
    reasoned=aggregate_code_scores(item,reasoned_scores)
    probabilities={key:(direct['mean_probabilities'][key]+reasoned['mean_probabilities'][key])/2
                   for key in nli_keys(item)}
    answer=max(nli_keys(item),key=probabilities.get)
    return dict(answer_choice=answer,mean_probabilities=probabilities,analysis=analysis,
        code_logprobs=direct_scores+reasoned_scores,direct_code_logprobs=direct_scores,
        reasoned_code_logprobs=reasoned_scores,direct=direct,reasoned=reasoned,
        selector_callbacks=4,analysis_callbacks=1,seed=SEED,weights=[.25]*4,
        output_contract='intermediate_native_key_only')


def completion_request(item, messages):
    nli_keys(item)
    instruction = (nli_target(item) + '\n\n' + RULE +
        '\nReturn the complete JSON object required by the original task. '
        'Keep step_by_step_thinking concise and grounded in the current premise '
        'and the exact current hypothesis. Give the native answer_choice first, '
        'followed by step_by_step_thinking.')
    return [*messages, {'role': 'user', 'content': instruction}]


def completion_schema(schema, choice=None):
    result = deepcopy(schema)
    result['properties']['answer_choice']['enum'] = (
        [choice] if choice is not None else ['positive', 'negative'])
    properties = result['properties']
    result['properties'] = {'answer_choice': properties['answer_choice'],
        **{key: value for key, value in properties.items() if key != 'answer_choice'}}
    return result


def optimize(item, messages, original_response, schema, score_codes, generate):
    """Return a complete raw response using only caller-visible task semantics.

    score_codes(messages, seed) -> complete finite raw logprobs {'A':..., 'B':...}.
    It must use the frozen one-token A/B protocol; missing scores require a
    same-prompt singleton fetch, whose actual request cost the caller records.
    generate(messages, schema_or_None, seed, temperature, max_tokens) -> raw str.
    None means unguided generation. No response is rewritten or spliced.
    `calls` counts public callback invocations, not internal missing-code fetches.
    """
    if item.get('answer_format') not in ('single', 'robustness_single', 'relation'):
        return dict(raw_response=original_response, calls=0, seeds=[], responses=[],
                    route='unchanged_unsupported_native_format', score_callbacks=0,
                    generation_callbacks=0)
    if is_nli(item):
        decision = decide_paths(item, messages, score_codes,
            lambda req, seed: generate(req, None, seed, 0, 2048))
        raw = generate(completion_request(item, messages),
            completion_schema(schema, decision['answer_choice']), SEED, 0, 2048)
        return dict(raw_response=raw, decision=decision, calls=6, score_callbacks=4,
            analysis_callbacks=1, completion_callbacks=1, generation_callbacks=2,
            min_model_requests=6, route='full_nli_equal_paths_native_completion')
    req = request(item, messages)
    native_schema = constrained_schema(item, schema)
    responses = []
    for seed in SEEDS:
        responses.append(generate(req, native_schema, seed, 0.7, 2048))
        result = aggregate(item, responses)
        if max(result['vote_counts'].values(), default=0) >= 3:
            break
    result.update(calls=len(responses), seeds=list(SEEDS[:len(responses)]),
                  responses=responses, max_calls=len(SEEDS),
                  stopped_early=len(responses) < len(SEEDS), score_callbacks=0,
                  generation_callbacks=len(responses),
                  route='full_native_key_maj5_absolute_majority_stop')
    return result



def check():
    messages = [{'role':'user','content':'Complete original context'}]
    item = dict(answer_format='single', options={'positive':'positive','negative':'negative'},
        question='what is the relationship between premise:P inhibits Q. hypothesis:Q inhibits P.')
    schema = {'type':'object','properties':{'step_by_step_thinking':{'type':'string'},
        'answer_choice':{'type':'string'}, 'extra_native_field':{'type':'string'}},
        'required':['step_by_step_thinking','answer_choice','extra_native_field']}
    events = []
    def scores(req,seed):
        index = sum(event == 'score' for event in events)
        events.append('score')
        assert req[:len(messages)] == messages and seed == 42
        return {'A':-4.,'B':-1.} if index % 2 == 0 else {'A':-1.,'B':-4.}
    raw = '{"answer_choice":"negative","step_by_step_thinking":"Exact raw.","extra_native_field":"kept"}'
    def generate(req,current_schema,seed,temperature,max_tokens):
        assert req[:len(messages)] == messages and (seed,temperature,max_tokens)==(42,0,2048)
        if current_schema is None:
            events.append('analysis')
            return 'Whole preceding raw response'
        events.append('completion')
        assert list(current_schema['properties'])[0]=='answer_choice'
        assert current_schema['properties']['answer_choice']['enum']==['negative']
        assert current_schema['required']==schema['required']
        return raw
    result = optimize(item,messages,'unused',schema,scores,generate)
    assert result['raw_response']==raw and result['decision']['analysis']=='Whole preceding raw response'
    assert events==['score','score','analysis','score','score','completion']
    assert 'enum' not in schema['properties']['answer_choice']
    changed = dict(item, gold='positive', source='unused', pair='unused', evaluation_labels=['R1'])
    assert is_nli(changed) and completion_request(changed,messages)==completion_request(item,messages)
    ordinary = dict(item, question='Choose the relationship', options={'A':'a','B':'b'})
    for choices,count in ((['A','A','A','B','B'],3),(['A','B','A','A','B'],4),
                          (['A','A','B','B','B'],5),([None,'B','A','A','B'],5),([None]*5,5)):
        pool = [json.dumps({'answer_choice':k,'errors':[]}) if k else 'invalid raw' for k in choices]
        calls=[]
        def vote(req,current_schema,seed,temperature,max_tokens):
            assert temperature==0.7 and max_tokens==2048 and seed==SEEDS[len(calls)]
            calls.append(seed)
            return pool[len(calls)-1]
        result = optimize(ordinary,messages,'unused',schema,None,vote)
        full = aggregate(ordinary,pool)
        assert result['calls']==count
        assert all(result[k]==full[k] for k in ('raw_response','selected_index','answer_choice'))
    for fmt in ('diagnosis','multi'):
        assert optimize(dict(item,answer_format=fmt),messages,'original',None,None,None)['raw_response']=='original'
    return {'status':'passed','new_model_calls':0,
        'checks':['semantic_routing','full_context','native_schema_fields','answer_first',
                  'fixed_equal_paths','3_4_5_call_stop','tie_invalid','original_raw','metadata_independence']}



if __name__ == '__main__':
    print(check())
