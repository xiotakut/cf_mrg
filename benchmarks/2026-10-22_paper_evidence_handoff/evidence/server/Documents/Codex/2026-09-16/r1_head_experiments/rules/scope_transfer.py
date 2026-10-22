"""Offline test: single-drug PIM rules abstain on current-regimen additions."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def asks_regimen_addition(item):
    """Use the current question only, never its source, labels or answer."""
    questions = re.findall(r'\b(?:which|what)\b[^?]*\?', item['question'], re.I)
    question = questions[-1] if questions else ''
    return bool(re.search(r'\badd\s+to\b[^?]*\bcurrent\s+regimen\b', question, re.I))


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


def main():
    assert json.loads((ROOT / 'runtime.json').read_text())['status'] == 'complete'
    items = read(ROOT / 'items.jsonl')
    triggered = {item['item_id'] for item in items if asks_regimen_addition(item)}
    strata = {r['item_id']: r for r in read(ROOT / 'strata.jsonl')}
    scores = read(ROOT / 'scored.jsonl')
    original = {(r['method'], r['item_id']): r for r in scores if r['policy'] == 'baseline'}
    adjusted = []
    for row in scores:
        if row['policy'] != 'program':
            continue
        base = original[row['method'], row['item_id']]
        gated = row['item_id'] in triggered
        result = dict(base if gated else row, policy='program_scoped', ddi_scope_triggered=gated)
        result['repaired'] = result['correct'] and not base['correct']
        result['harmed'] = base['correct'] and not result['correct']
        adjusted.append(result)
    write(ROOT / 'scope_scored.jsonl', adjusted)
    write(ROOT / 'scope_triggered_items.jsonl', [dict(item=item, prior_eligible=strata[item['item_id']]['eligible'])
        for item in items if item['item_id'] in triggered])
    rows = [r for r in scores if r['policy'] in ('baseline', 'program')] + adjusted
    summaries = []
    for method in ('M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'):
        for policy in ('baseline', 'program', 'program_scoped'):
            for group in ('all96', 'old_covered72', 'new_covered62', 'triggered9', 'triggered_eligible8'):
                selected = [r for r in rows if r['method'] == method and r['policy'] == policy and
                    {'all96': True, 'old_covered72': r['covered'],
                     'new_covered62': r['covered'] and not r['r3_overlap'],
                     'triggered9': r['item_id'] in triggered,
                     'triggered_eligible8': r['item_id'] in triggered and r['covered']}[group]]
                summaries.append(dict(method=method, policy=policy, group=group, n=len(selected),
                    correct=sum(r['correct'] for r in selected), invalid=sum(r['invalid'] for r in selected),
                    repairs=sum(r['repaired'] for r in selected), harms=sum(r['harmed'] for r in selected)))
    (ROOT / 'scope_summary.json').write_text(json.dumps(dict(status='offline_complete_development',
        trigger='last current question contains add to ... current regimen', scanned=len(items),
        triggered=len(triggered), newly_passthrough=sum(strata[i]['eligible'] for i in triggered),
        new_model_calls=0, rules_unchanged=True, results=summaries), indent=2) + '\n')
    print(json.dumps([r for r in summaries if r['group'] in ('all96', 'triggered9')], indent=2))


if __name__ == '__main__':
    main()
