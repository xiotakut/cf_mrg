"""Compare raw pilot outputs with frozen baseline using the unchanged scorer."""
import argparse
import collections
import json
from pathlib import Path
from analyze_v5 import objects, score, norm, PACK

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--structured', action='store_true')
args = parser.parse_args()
OUT = ROOT / ('m4_format_structured_pilot' if args.structured else 'm4_format_pilot')
ARM = 'structured_fix' if args.structured else 'prompt_fix'

def read(path):
    with path.open() as f:
        return [json.loads(line) for line in f]

items = {r['item']['item_id']: r['item'] for r in read(OUT / 'inputs.jsonl')}
new = {r['item_id']: r for r in read(OUT / 'predictions.jsonl')}
old = {r['item_id']: r for r in read(ROOT / 'M4/predictions.jsonl') if r['item_id'] in items}
canonical = {norm(s): s for s in json.loads((PACK / 'results_cf_full_test/canonical_labels.json').read_text())['labels']}
labels = {}
for row in read(ROOT / 'evaluation.jsonl'):
    if row['item_id'] in items:
        if row['item_id'] in labels:
            assert labels[row['item_id']]['gold'] == row['gold']
        labels[row['item_id']] = row
rows = []
for iid in sorted(new):
    for arm, prediction in [('original', old[iid]), (ARM, new[iid])]:
        item = items[iid]
        obj = objects(prediction['raw_response'], 'answer_choice')
        native = dict(prediction, raw_response=json.dumps({'answer': obj['answer_choice']}) if obj else '')
        adapted = dict(item, answer_format='single') if item['answer_format']=='robustness_single' else item
        result = score(native, labels[iid], adapted, canonical)
        rows.append(dict(item_id=iid, arm=arm, answer_format=item['answer_format'], json_object_valid=obj is not None, **result))
summary = {}
for arm in ('original', ARM):
    selected = [r for r in rows if r['arm']==arm]
    summary[arm] = dict(N=len(selected), json_object_valid=sum(r['json_object_valid'] for r in selected), format_valid=sum(not r['format_invalid'] for r in selected),
                        native_valid=sum(not r['invalid'] for r in selected), correct=sum(r['correct'] for r in selected),
                        invalid_reasons=dict(collections.Counter(r['invalid_reason'] or 'valid' for r in selected)),
                        by_format={fmt:dict(N=len(group),format_valid=sum(not r['format_invalid'] for r in group),native_valid=sum(not r['invalid'] for r in group),correct=sum(r['correct'] for r in group)) for fmt in sorted({r['answer_format'] for r in selected}) if (group:=[r for r in selected if r['answer_format']==fmt])})
report = dict(status='complete' if len(new)==100 else 'partial', denominator='unique inputs; stratified 20 per format; historical baseline not rerun with matched batch schedule', summary=summary)
(OUT / 'comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
(OUT / 'scored.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
print(json.dumps(report,ensure_ascii=False,indent=2))
