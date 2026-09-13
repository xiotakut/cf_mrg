"""Offline native scoring and coverage; no model or retriever initialization."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from common import ROOT, PACK, V5, atomic, digest, read, visible, json_object

sys.path.insert(0, str(V5 / 'code'))
from analyze_v5 import score as native_score, norm


def cluster_interval(rows):
    import numpy as np
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['dependency_group']].append(row['score'])
    sums = np.array([sum(v) for v in grouped.values()])
    counts = np.array([len(v) for v in grouped.values()])
    if not len(sums):
        return dict(groups=0, ci95=None)
    rng = np.random.default_rng(20260911)
    means = []
    for _ in range(2000):
        chosen = rng.integers(0, len(sums), len(sums))
        means.append(float(sums[chosen].sum() / counts[chosen].sum()))
    return dict(groups=len(sums), ci95=np.quantile(means, [.025, .975]).tolist(),
                bootstrap='case/dependency-cluster, 2000, seed20260911', unstable=len(sums) < 30)


def dependencies(evaluations, items):
    """Cluster shared exact original stems/options across sources, then cases."""
    parent = {e['group_id']: e['group_id'] for e in evaluations}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    origins = {}
    for e in evaluations:
        if e.get('role') != 'reference':
            continue
        item = items[e['item_id']]
        signature = digest(dict(question=' '.join(item['question'].split()), options=item['options']))
        if signature in origins:
            left, right = find(e['group_id']), find(origins[signature])
            parent[max(left, right)] = min(left, right)
        origins[signature] = e['group_id']
    return {group: find(group) for group in parent}


def score_run(run_dir, inputs, evaluations, output):
    items = {i['item_id']: i for i in read(inputs)}
    records = read(run_dir / 'predictions.jsonl')
    predictions = {r['item_id']: r for r in records}
    assert len(predictions) == len(records) and not set(predictions) - set(items)
    assert set(predictions) == set(items), 'Run incomplete: every planned input must have a terminal result before scoring.'
    for iid, r in predictions.items():
        assert r['input_hash'] == digest(visible(items[iid]))
    canonical = {norm(s): s for s in json.loads((PACK / 'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    clusters = dependencies(evaluations, items)
    scored, detection = [], []
    for e in evaluations:
        item, result = items[e['item_id']], predictions[e['item_id']]
        # Failures and unaccepted TC conclusions retain the full denominator.
        raw = result['raw_response'] if result['status'] == 'ok' else ''
        obj = None
        try:
            obj = json_object(raw, 'answer')
        except ValueError:
            pass
        native_item = dict(item, answer_format='single') if item['answer_format'] == 'robustness_single' else item
        native = dict(raw_response=json.dumps({'answer': obj['answer']}) if obj else '')
        score = native_score(native, e, native_item, canonical)
        scored.append(dict(e, **score, method=result['method'], runtime_status=result['status'],
                           termination=result['termination'], dependency_group=clusters[e['group_id']]))
        if item['answer_format'] == 'robustness_single':
            errors = obj.get('errors') if obj else None
            valid = isinstance(errors, list) and all(isinstance(x, dict) and isinstance(x.get('document_id'), str) and isinstance(x.get('correction'), str) for x in errors)
            guessed = [x['document_id'] for x in errors] if valid else []
            valid = valid and len(guessed) == len(set(guessed)) and set(guessed) <= set(e['document_map'])
            excluded = set(e['incomplete_document_ids'])
            gold = set(e['error_document_ids']) - excluded
            guess = set(guessed) - excluded if valid else set()
            detection.append(dict(record_id=e['record_id'], item_id=e['item_id'], valid=valid,
                                  exact=valid and guess == gold, tp=len(guess & gold), fp=len(guess - gold), fn=len(gold - guess),
                                  correction_semantic_score=None, excluded_empty_document_ids=sorted(excluded)))
    atomic(output / 'scored.jsonl', scored, lines=True)
    atomic(output / 'document_detection.jsonl', detection, lines=True)
    source_rows = []
    groups = defaultdict(list)
    for r in scored:
        groups[r.get('resource_id', r.get('source_id')), r.get('role'), r.get('task', 'native')].append(r)
    for (source, role, task), rs in groups.items():
        source_rows.append(dict(source_id=source, role=role, task=task, N=len(rs),
                               correct=sum(r['correct'] for r in rs), accuracy=mean(r['correct'] for r in rs),
                               native_invalid=sum(r['invalid'] for r in rs),
                               multi_option_f1=mean(r['option_f1'] for r in rs) if rs[0]['option_f1'] is not None else None))
    atomic(output / 'source_task_scores.json', source_rows)
    # Retain the already-confirmed v5 unit-mean rule, with evaluation_labels only.
    buckets = defaultdict(list)
    for r in scored:
        if r.get('role') == 'reference':
            continue
        for cat in r.get('evaluation_labels', []):
            buckets[r['unit_id'], cat].append(r)
    unit_scores = [dict(unit_id=uid, category=cat, score=mean(r['correct'] for r in rs),
                        dependency_group=rs[0]['dependency_group']) for (uid, cat), rs in buckets.items()]
    atomic(output / 'unit_scores.jsonl', unit_scores, lines=True)
    categories = []
    for cat in sorted({r['category'] for r in unit_scores}):
        rs = [r for r in unit_scores if r['category'] == cat]
        categories.append(dict(category=cat, units=len(rs), unit_mean_accuracy=mean(r['score'] for r in rs), **cluster_interval(rs)))
    atomic(output / 'category_scores.json', categories)
    refs = {(r.get('unit_id'), 'robustness' if r.get('task', '').startswith('robustness_') else r.get('task')): r
            for r in scored if r.get('role') == 'reference'}
    pairs = []
    for r in scored:
        if r.get('role') == 'reference':
            continue
        ref = refs.get((r.get('unit_id'), 'robustness' if r.get('task', '').startswith('robustness_') else r.get('task')))
        if ref is None:
            continue
        expected = 'keep' if ref['semantic_gold'] == r['semantic_gold'] else 'change'
        pairs.append(dict(unit_id=r['unit_id'], dependency_group=r['dependency_group'], expected_relation=expected,
                          reference_correct=ref['correct'], variant_correct=r['correct'],
                          both_correct=ref['correct'] and r['correct'],
                          answer_invariant=not ref['invalid'] and not r['invalid'] and ref['semantic_prediction'] == r['semantic_prediction']))
    atomic(output / 'pairs.jsonl', pairs, lines=True)
    pair_summary = []
    for relation in ('keep', 'change'):
        selected = [r for r in pairs if r['expected_relation'] == relation]
        if selected:
            pair_summary.append(dict(expected_relation=relation, pairs=len(selected),
                both_correct_rate=mean(r['both_correct'] for r in selected),
                **cluster_interval([dict(score=r['both_correct'], dependency_group=r['dependency_group']) for r in selected])))
    atomic(output / 'pair_summary.json', pair_summary)
    statuses = Counter(r['status'] for r in records)
    summary = dict(N_planned=len(items), N_ok=statuses['ok'], N_invalid=statuses['invalid'], N_failed=statuses['failed'], N_pending=0,
                   terminal_coverage=1.0, valid_runtime_answer_rate=statuses['ok'] / len(items),
                   native_scored_records=len(scored), native_valid_rate=mean(not r['invalid'] for r in scored),
                   sources=source_rows, categories=categories,
                   pair_metric='Both correct, separated by expected keep/change; not answer invariance as quality.',
                   small_sample_note='Development/source counts are descriptive; small samples do not establish comparative accuracy.',
                   scoring_version='existing-v5-native-20260911+failure-denominator-v1',
                   diagnosis_metric='Existing fixed canonical exact match, not an official semantic judge.')
    atomic(output / 'summary.json', summary)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--split', choices=['dev', 'formal'], required=True)
    args = p.parse_args()
    if args.split == 'dev':
        evaluations = [dict(e, resource_id=e['source_id'], record_id=e['item_id'], unit_id=e['item_id'], task='native') for e in read(ROOT / 'data/dev_gold.jsonl')]
        inputs = ROOT / 'data/dev_inputs.jsonl'
    else:
        evaluations, inputs = read(ROOT / 'data/evaluation.jsonl'), ROOT / 'data/inputs.jsonl'
    output = args.run_dir / 'scores'
    output.mkdir(exist_ok=True)
    result = score_run(args.run_dir, inputs, evaluations, output)
    print(json.dumps({k: v for k, v in result.items() if k not in ('sources', 'categories')}, indent=2))


if __name__ == '__main__':
    main()
