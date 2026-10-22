"""Post-hoc reuse of existing arithmetic means; no new model calls or head changes."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from r3_audit import HERE, OUT as DATA, read, write, dump
from r3_calibrated_expansion import scoring

out = Path(__file__).resolve().parent
objects, score, canonical = scoring()
items = {r['item_id']: r for r in read(DATA/'items.jsonl')}
evaluation = {r['item_id']: r for r in read(DATA/'evaluation.jsonl')}
controls = {(r['method'], r['item_id'], r['variant']): r for r in read(out/'scored.jsonl')}
predictions = list(read(out/'predictions_new_methods.jsonl')) + list(read(HERE/'r3_calibrated_expansion/predictions.jsonl'))
assert len(predictions) == len({(r['method'], r['item_id']) for r in predictions}) == 680*7
rows = []
for r in predictions:
    method = r['method']; iid = r['item_id']
    for family in ('uncalibrated', 'calibrated'):
        assert r[family]['majority_vote'] == controls[method, iid, family+'_majority']['answer']
        answer = r[family]['mean_probability']
        metric = score(dict(raw_response=json.dumps(dict(answer=answer))), evaluation[iid], items[iid], canonical)
        comparisons = {}
        for control in ('order0', family+'_majority', 'calibrated_majority'):
            before = controls[method, iid, control]
            comparisons[control] = dict(repaired=metric['correct'] and not before['correct'],
                                        harmed=not metric['correct'] and before['correct'])
        rows.append(dict(method=method, item_id=iid, variant=family+'_mean', gold=evaluation[iid]['gold'],
                         answer=answer, comparisons=comparisons, **metric))
results = []
for method in ('M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'):
    for variant in ('uncalibrated_mean', 'calibrated_mean'):
        rs = [r for r in rows if r['method'] == method and r['variant'] == variant]
        classes = {r['gold'] for r in rs}
        macro = sum(sum(r['correct'] for r in rs if r['gold'] == c)/sum(r['gold'] == c for r in rs) for c in classes)/len(classes)
        results.append(dict(method=method, variant=variant, n=len(rs), correct=sum(r['correct'] for r in rs),
            invalid=sum(r['invalid'] for r in rs), macro_recall=macro,
            comparisons={c: dict(repairs=sum(r['comparisons'][c]['repaired'] for r in rs),
                                 harms=sum(r['comparisons'][c]['harmed'] for r in rs)) for c in rs[0]['comparisons']}))
write(out/'mean_probability_scored.jsonl', rows)
dump(out/'mean_probability_summary.json', dict(status='complete_posthoc_development_control', results=results,
    new_model_calls=0, reused_patient_distributions=28560,
    scope='All680 exposed cases per method. Arithmetic means already computed from original six-order scores; this analysis follows the all-method results. Frozen primary unchanged.'))
for r in results:
    print(r['method'], r['variant'], r['correct'], round(100*r['macro_recall'], 3), r['comparisons'])
