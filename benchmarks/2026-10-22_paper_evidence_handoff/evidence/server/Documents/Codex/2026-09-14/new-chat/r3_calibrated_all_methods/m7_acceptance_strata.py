"""Describe frozen-head gains by original TC acceptance status; no model calls."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from r3_audit import HERE, OUT as DATA, read, dump
from r3_calibrated_expansion import scoring
from r3_catalog_distribution_head import aggregate, calibrate, orders

out = Path(__file__).resolve().parent
objects, score, canonical = scoring()
evaluation = {r['item_id']: r for r in read(DATA/'evaluation.jsonl')}
native = {r['item_id']: r for r in read(out/'native_m7_status.jsonl')}
path = out/'m7'
catalog = json.loads((path/'catalog.json').read_text())
priors = json.loads((path/'log_priors.json').read_text())
lookup = {(r['item_id'], r['order']): r['code_logprobs'] for r in read(path/'distributions.jsonl')}
head = {r['item_id']: r for r in read(HERE/'r3_catalog_calibration_m7/scored.jsonl') if r['variant'] == 'majority_vote'}
for r in read(path/'inputs.jsonl'):
    item = r['item']; iid = item['item_id']
    answer = aggregate(catalog, orders(catalog), calibrate([lookup[iid, k] for k in range(6)], priors))['majority_vote']
    head[iid] = score(dict(raw_response=json.dumps(dict(answer=answer))), evaluation[iid], item, canonical)
assert set(head) == set(native) and len(head) == 680
results = []
for status in ('ok', 'invalid'):
    ids = [iid for iid, r in native.items() if r['status'] == status]
    results.append(dict(status=status, n=len(ids), original_correct=sum(native[i]['native_correct'] for i in ids),
        head_correct=sum(head[i]['correct'] for i in ids), head_invalid=sum(head[i]['invalid'] for i in ids),
        repairs=sum(head[i]['correct'] and not native[i]['native_correct'] for i in ids),
        harms=sum(not head[i]['correct'] and native[i]['native_correct'] for i in ids)))
dump(out/'m7_acceptance_strata.json', dict(results=results, new_model_calls=0,
    scope='Same680 exposed cases. Original status retained; descriptive strata, not a modified TC baseline.'))
print(results)
