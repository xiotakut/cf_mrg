"""Candidate TC-RAG output adapter, applied only AFTER the original acceptance gate."""
import json


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate_field')
        obj[key] = value
    return obj


def normalize_accepted(result, item):
    raw = result['raw_response']
    if result.get('termination') != 'accepted' or result.get('status') != 'invalid':
        return raw, None
    if item['answer_format'] not in ('single', 'robustness_single'):
        return raw, None
    options = item['options']
    # A bare exact key is already an explicit answer; do not infer from prose.
    if item['answer_format'] == 'single' and raw.strip() in options:
        return json.dumps({'answer': raw.strip()}, ensure_ascii=False), 'bare_exact_key'
    try:
        obj = json.loads(raw, object_pairs_hook=unique_pairs)
    except ValueError:
        return raw, None
    if not isinstance(obj, dict) or not isinstance(obj.get('answer'), str):
        return raw, None
    value = obj['answer']
    if value in options:
        return raw, None
    matches = [(key, 'key_plus_exact_option_text') for key, text in options.items()
               if value == key + '. ' + text]
    matches += [(key, 'key_plus_period') for key in options if value == key + '.']
    if len(matches) != 1:
        return raw, None
    key, rule = matches[0]
    obj['answer'] = key
    # Preserve every other field; missing errors stay missing, IDs stay unchanged.
    return json.dumps(obj, ensure_ascii=False), rule


def test():
    item = dict(answer_format='single', options={'A': 'Alpha', 'B': 'Beta'})
    def result(raw, termination='accepted', status='invalid'):
        return dict(raw_response=raw, termination=termination, status=status)
    assert json.loads(normalize_accepted(result('{"answer":"A. Alpha"}'), item)[0])['answer'] == 'A'
    assert json.loads(normalize_accepted(result('{"answer":"A."}'), item)[0])['answer'] == 'A'
    assert json.loads(normalize_accepted(result('B'), item)[0])['answer'] == 'B'
    for raw in ['{"answer":"A. Beta"}', '{"answer":"A","answer":"B. Beta"}',
                'Probably A', '{"answer":"A. Alpha"}{"answer":"B. Beta"}']:
        assert normalize_accepted(result(raw), item) == (raw, None)
    for termination in ['budget_exhausted', 'action_parse_failed']:
        assert normalize_accepted(result('A', termination), item) == ('A', None)
    assert normalize_accepted(result('{"answer":"A"}', status='ok'), item)[1] is None
    robust = dict(item, answer_format='robustness_single')
    raw = '{"answer":"A. Alpha"}'
    assert 'errors' not in json.loads(normalize_accepted(result(raw), robust)[0])
    assert normalize_accepted(result('A'), robust) == ('A', None)


if __name__ == '__main__':
    test()
    print('Exact answer preservation, conflict rejection and acceptance gate: passed.')
