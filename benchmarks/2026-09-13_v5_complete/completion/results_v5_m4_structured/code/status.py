"""Read-only progress and unchanged native validity scoring for completed inputs."""
import json
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
from prepare_v5 import OUT, PACK, read
from analyze_v5 import objects, score, norm
from m4_output_schema import output_schema


@lru_cache(maxsize=1)
def data():
    items = {i['item_id']: i for i in read(OUT / 'items.jsonl')}
    labels = {}
    for e in read(OUT / 'evaluation.jsonl'):
        # Validity is output-derived and independent of gold; the full scorer
        # retains every mapping, including shared inputs with different labels.
        labels[e['item_id']] = e
    canonical = {norm(s): s for s in json.loads((PACK / 'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    pilot = set(json.loads((OUT / 'plan.json').read_text())['prior_selection_pilot_ids'])
    return items, labels, canonical, pilot


@lru_cache(maxsize=None)
def validator(schema):
    from jsonschema import Draft202012Validator
    return Draft202012Validator(json.loads(schema))


def summarize(rows):
    n = len(rows)
    counts = {key: sum(r[key] for r in rows) for key in
              ('json_valid', 'schema_valid', 'format_valid', 'native_valid', 'truncated')}
    return dict(N=n, **counts, **{k + '_pct': round(100 * v / n, 3) if n else None
                for k, v in counts.items()}, invalid_reasons=dict(Counter(r['invalid_reason'] or 'valid' for r in rows)))


def status():
    items, labels, canonical, pilot = data()
    jobs = [json.loads(p.read_text()) for p in sorted((OUT / 'jobs').glob('*.json'))]
    predictions = [r for p in sorted((OUT / 'runs').glob('*/predictions.jsonl')) for r in read(p)]
    ids = {p['item_id'] for p in predictions}
    assert len(ids) == len(predictions) and ids <= set(items)
    rows = []
    for prediction in predictions:
        iid = prediction['item_id']; item = items[iid]
        obj = objects(prediction['raw_response'], 'answer_choice')
        adapted = dict(prediction, raw_response=json.dumps({'answer': obj['answer_choice']}) if obj else '')
        native_item = dict(item, answer_format='single') if item['answer_format'] == 'robustness_single' else item
        scored = score(adapted, labels[iid], native_item, canonical)
        strict, schema_ok = False, False
        try:
            value = json.loads(prediction['raw_response'])
            strict = isinstance(value, dict)
            schema_ok = validator(json.dumps(output_schema(item), sort_keys=True)).is_valid(value)
        except json.JSONDecodeError:
            pass
        rows.append(dict(item_id=iid, answer_format=item['answer_format'],
                    resource_id=labels[iid]['resource_id'], json_valid=strict,
                    schema_valid=schema_ok, format_valid=not scored['format_invalid'],
                    native_valid=not scored['invalid'], invalid_reason=scored['invalid_reason'],
                    truncated=prediction['finish_reason'] == 'length'))
    groups = defaultdict(list)
    for row in rows:
        groups[row['answer_format']].append(row)
    return dict(observed_at=datetime.now().astimezone().isoformat(), planned=13905,
                completed=len(rows), new_completed=len(rows), remaining=13905-len(rows),
                reused_predictions=0, jobs=dict(Counter(j['state'] for j in jobs)),
                active=[{k: j.get(k) for k in ('name', 'state', 'gpu', 'worker_pid', 'error')}
                        for j in jobs if j['state'] in ('running', 'error')],
                validity=summarize(rows), by_format={k: summarize(v) for k, v in groups.items()},
                outside_selection_pilot_inputs=summarize([r for r in rows if r['item_id'] not in pilot]),
                denominator='completed unique inputs, all outputs retained; native validity includes frozen diagnosis mapping')


if __name__ == '__main__':
    print(json.dumps(status(), ensure_ascii=False, indent=2))
