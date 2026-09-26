"""Score only the four newly completed original C0 answers; reuse old 48."""
import argparse
from collections import defaultdict
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys

WORK = Path('/home/data3/txy')
HERE = Path(__file__).resolve().parent
NEW = HERE.parent
NAT = WORK/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923/natural_scope'
sys.path.insert(0, str(WORK))
spec = importlib.util.spec_from_file_location('full_analysis', NEW/'full_v5/analyze_full.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows, sha, dump, write = module.rows, module.sha, module.dump, module.write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', choices=['M4', 'M5'], required=True)
    args = parser.parse_args()
    method = args.method
    run = HERE/(method.lower()+'_live')/'run'
    state = json.loads((run/'status.json').read_text())
    closed = json.loads((run/'supervisor_result.json').read_text())
    assert state['status'] == 'complete' and closed['exit_code'] == 0
    outputs = {r['request_id']: r for r in rows(run/'proposals.jsonl')}
    assert set(outputs) == {'n00000', 'n00005', 'n00019', 'n00030'}
    evaluations = list(rows(NAT/'offline/evaluations.jsonl'))
    items = {r['request_id']: r for r in rows(NAT/'offline/items.jsonl')}
    sources = {r['score_source'] for r in rows(NAT/'offline/baseline_native_scores_reused.jsonl')}
    assert len(sources) == 1
    source = Path(next(iter(sources)))
    eidx = {r['record_id']: r for r in evaluations}
    existing = [dict(r, request_id=eidx[r['record_id']]['request_id']) for r in rows(source)
                if r['method'] == method and r['arm'] == 'original' and r['record_id'] in eidx]
    assert len(existing) == 48
    assert {r['request_id'] for r in existing}.isdisjoint(outputs)
    dest = HERE/'analysis'/method.lower()
    dest.mkdir(parents=True, exist_ok=True)
    cache = module.ScoreCache(dest/'new_score_cache.sqlite3')
    new = []
    for evaluation in evaluations:
        rid = evaluation['request_id']
        if rid not in outputs:
            continue
        value = outputs[rid]['result']['native_answer']
        score, proof = cache.obtain(method, items[rid], evaluation, value, grade=True)
        new.append(dict(evaluation, **score, method=method, arm='original', panel='natural52',
                        score_origin=proof, native_answer_ref=module.digest(value)))
    assert len(new) == 4
    all_scores = [dict(r, panel='natural52') for r in existing]+new
    by_id = {r['record_id']: r for r in all_scores}
    assert len(by_id) == len(all_scores) == 52 and set(by_id) == set(eidx)
    units = defaultdict(list)
    for evaluation in evaluations:
        if evaluation['role'] != 'reference':
            units[evaluation['unit_id'], evaluation['resource_id']].append(evaluation['record_id'])
    unit_rows = [dict(unit_id=k[0], resource_id=k[1], records=ids,
                      score=sum(by_id[r]['correct'] is True for r in ids)/len(ids))
                 for k, ids in sorted(units.items())]
    assert len(unit_rows) == 18
    pairs = []
    for pair in rows(NAT/'offline/pairs.jsonl'):
        a, b = by_id[pair['left_record_id']], by_id[pair['right_record_id']]
        pairs.append(dict(pair, both_correct=int(a['correct'] is True and b['correct'] is True)))
    write(dest/'native_scored.jsonl', all_scores)
    write(dest/'new_native_scored.jsonl', new)
    write(dest/'native_units.jsonl', unit_rows)
    write(dest/'pairs.jsonl', pairs)
    cost = dict(state['cost'])
    # recorded_call_wall_seconds repeats shared backend initialization per row.
    # It is retained raw but never claimed as elapsed run or exclusive GPU time.
    summary = dict(status='complete', panel='natural52', method=method, control='C0',
        denominator=52, reused_inputs=48, newly_generated_inputs=4,
        correct_inputs=sum(r['correct'] is True for r in all_scores),
        unavailable_inputs=sum(r['correct'] is None for r in all_scores),
        native_ALL_units=len(unit_rows), native_ALL_mean=sum(r['score'] for r in unit_rows)/len(unit_rows),
        pairs=[dict(relation=relation, denominator=sum(p['relation']==relation for p in pairs),
                    both_correct=sum(p['both_correct'] for p in pairs if p['relation']==relation))
               for relation in ['maintain', 'respond']],
        new_physical_cost=cost, new_run_wall_seconds=state['elapsed_seconds'],
        inherited_original48_cost='not reconstructed here; retain original delivery cost',
        timing_note='event elapsed seconds allocates shared model batch wall; not exclusive GPU time. Raw recorded_call_wall_seconds includes repeated lazy initialization.',
        auxiliary='Saved fields retained. Missing historic auxiliary fields are unknown, not zero and not regraded.',
        exposure='already exposed natural52 development; not confirmation')
    dump(dest/'summary.json', summary)
    paths = [source, run/'proposals.jsonl', run/'status.json', run/'supervisor_result.json',
             NAT/'offline/items.jsonl', NAT/'offline/evaluations.jsonl', NAT/'offline/pairs.jsonl',
             Path(__file__).resolve(), NEW/'full_v5/analyze_full.py']
    receipt = dict(at=datetime.now().astimezone().isoformat(), method=method,
        new_grader_calls=cache.new_calls, exact_new_score_cache_hits=dict(cache.reuse),
        old48_grader_calls=0, new_model_calls=0, scorer_sources=cache.lock,
        sources={str(p):sha(p) for p in paths}, final_cache_rows=cache.db.execute('SELECT COUNT(*) FROM scores').fetchone()[0])
    cache.db.close()
    name = 'receipt.json' if not (dest/'receipt.json').exists() else 'receipt_reuse.json'
    dump(dest/name, receipt)
    print(json.dumps(dict(summary=summary, grading=receipt['new_grader_calls']), ensure_ascii=False))


if __name__ == '__main__':
    main()
