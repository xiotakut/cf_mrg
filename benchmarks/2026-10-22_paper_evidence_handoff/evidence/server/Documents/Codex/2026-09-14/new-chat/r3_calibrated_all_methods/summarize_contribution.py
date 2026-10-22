"""Separate workflow increments and describe the seven-method gap; no inference."""
import json
from pathlib import Path

out = Path(__file__).resolve().parent
summary = json.loads((out/'summary.json').read_text())
rows = [json.loads(line) for line in (out/'scored.jsonl').open()]
lookup = {(r['method'], r['item_id'], r['variant']): r for r in rows}
methods = ('M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7')
variants = ('original', 'order0', 'uncalibrated_majority', 'calibrated_majority')
all680 = {(r['method'], r['variant']): r for r in summary['results'] if r['scope'] == 'all680'}
increments = []
for method in methods:
    ids = [r['item_id'] for r in rows if r['method'] == method and r['variant'] == 'original']
    assert len(ids) == 680
    for previous, current in zip(variants, variants[1:]):
        repairs = sum(lookup[method, i, current]['correct'] and not lookup[method, i, previous]['correct'] for i in ids)
        harms = sum(not lookup[method, i, current]['correct'] and lookup[method, i, previous]['correct'] for i in ids)
        increments.append(dict(method=method, previous=previous, current=current, n=680,
                               repairs=repairs, harms=harms, net=repairs-harms))
gaps = []
for variant in variants:
    counts = {m: all680[m, variant]['correct'] for m in methods}
    gap = max(counts.values())-min(counts.values())
    gaps.append(dict(variant=variant, correct=counts, gap_cases=gap, gap_percentage_points=100*gap/680))
shared = sorted({json.loads(line)['item_id'] for line in (out/'m2/reused_requests.jsonl').open()})
assert len(shared) == 81
same = sum(lookup['M0', i, 'calibrated_majority']['answer'] == lookup['M2', i, 'calibrated_majority']['answer'] for i in shared)
assert same == len(shared)
matched = dict(n=81, identical_calibrated_answers=same,
    original_correct={m: sum(lookup[m, i, 'original']['correct'] for i in shared) for m in ('M0', 'M2')},
    calibrated_correct={m: sum(lookup[m, i, 'calibrated_majority']['correct'] for i in shared) for m in ('M0', 'M2')})
result = dict(increments=increments, seven_method_gaps=gaps, identical_request_m0_m2=matched,
    new_calls=summary['new_calls'], new_input_tokens=sum(r['input_tokens'] for r in summary['costs']),
    new_output_tokens=sum(r['output_tokens'] for r in summary['costs']), new_model_calls_for_analysis=0,
    scope='Descriptive680-case development comparison. Order0 combines public catalog, patient repetition and a new terminal score; its gain is not solely CF reasoning.')
(out/'contribution_summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
for method in methods:
    print(method, [all680[method, v]['correct'] for v in variants],
          'cal_macro', round(100*all680[method, 'calibrated_majority']['macro_recall'], 3),
          'cal_invalid', all680[method, 'calibrated_majority']['invalid'])
print('gaps', [(r['variant'], r['gap_cases'], round(r['gap_percentage_points'], 3)) for r in gaps])
print('shared', matched)
print('cost', result['new_calls'], result['new_input_tokens'], result['new_output_tokens'])
