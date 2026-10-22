"""Offline subgroup and execution diagnostics for the frozen transfer."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))


strata = {r['item_id']: r for r in read(ROOT / 'strata.jsonl')}
scores = read(ROOT / 'scored.jsonl')
traces = {(r['method'], r['policy'], r['item_id']): r for r in read(ROOT / 'traces.jsonl')}
groups = []
for method in sorted({r['method'] for r in scores}):
    for policy in ('baseline', 'program', 'model_execute'):
        for dimension in ('patient_info', 'action', 'scope'):
            for value in sorted({r[dimension] for r in strata.values()}):
                rows = [r for r in scores if r['method'] == method and r['policy'] == policy
                        and strata[r['item_id']][dimension] == value]
                groups.append(dict(method=method, policy=policy, dimension=dimension, value=value,
                    n=len(rows), covered=sum(r['covered'] for r in rows), correct=sum(r['correct'] for r in rows),
                    invalid=sum(r['invalid'] for r in rows), repairs=sum(r['repaired'] for r in rows),
                    harms=sum(r['harmed'] for r in rows)))
write(ROOT / 'subgroups.jsonl', groups)

changes = []
for row in scores:
    if row['method'] not in ('M4', 'M5') or row['policy'] != 'program':
        continue
    trace = traces[row['method'], row['policy'], row['item_id']]
    if trace['initial'] == trace['answer']:
        continue
    changes.append(dict(item_id=row['item_id'], method=row['method'], gold=row['gold'],
        initial=trace['initial'], answer=trace['answer'], correct=row['correct'], repaired=row['repaired'],
        harmed=row['harmed'], patient_info=strata[row['item_id']]['patient_info'], details=trace['details']))
write(ROOT / 'm4_m5_program_changes.jsonl', changes)

diagnostics = []
for model in ('llama', 'qwen'):
    facts = read(ROOT / model / 'fact_extractions.jsonl')
    rows = [*read(ROOT / model / 'execute/reused_predictions.jsonl'),
            *read(ROOT / model / 'execute/gpu3/predictions.jsonl')]
    executions, invalid_executions = {}, []
    for row in rows:
        try:
            executions[row['item_id']] = json.loads(row['raw_response'])['options']
        except (ValueError, KeyError, TypeError) as exc:
            invalid_executions.append(dict(item_id=row['item_id'], error=f'{type(exc).__name__}: {exc}'))
    state_pairs = Counter()
    disagreement = []
    for fact in facts:
        if 'options' not in fact:
            continue
        states = executions.get(fact['item_id'], {})
        differing = []
        for key, detail in fact['options'].items():
            state_pairs[detail['state'], states.get(key)] += 1
            if detail['state'] != states.get(key):
                differing.append(dict(option=key, program=detail['state'], model=states.get(key)))
        if differing:
            disagreement.append(dict(item_id=fact['item_id'], differences=differing))
    diagnostics.append(dict(model=model, facts=len(facts), invalid_executions=invalid_executions,
        invalid_facts=sum(r['reason'] == 'invalid_fact_extraction' for r in facts),
        evidence_error_items=sum(bool(r.get('evidence_errors')) for r in facts),
        evidence_error_fields=sum(len(r.get('evidence_errors', [])) for r in facts),
        clean_reasons=dict(Counter(e['reason'] for r in facts for e in r.get('evidence_errors', []))),
        program_model_state_pairs=[dict(program=k[0], model=k[1], n=v) for k, v in state_pairs.items()],
        disagreeing_items=disagreement))
(ROOT / 'execution_diagnostics.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n')
summary = json.loads((ROOT / 'summary.json').read_text())
lookup = {(r['method'], r['policy'], r['group']): r for r in summary['results']}
lines = ['# Frozen R2 transfer: native R1 MedPIC', '',
         'All data are exposed v5 development. Two backbone fact/execution runs attach offline to seven existing method answers. The 24 uncovered tasks retain their original outputs.', '']
for group in ('all96', 'covered72', 'new_covered62', 'old_r3_10', 'uncovered24'):
    lines += ['## ' + group, '', '| Original method | Original correct | Program correct | Program repair/harm | Same-facts model correct | Model repair/harm |',
              '|---|---:|---:|---:|---:|---:|']
    for method in ('M0', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'):
        base, prog, model = [lookup[method, policy, group] for policy in ('baseline', 'program', 'model_execute')]
        lines.append(f"| {method} | {base['correct']}/{base['n']} | {prog['correct']}/{prog['n']} | {prog['repairs']}/{prog['harms']} | {model['correct']}/{model['n']} | {model['repairs']}/{model['harms']} |")
    lines.append('')
lines += ['## Actual generation and reuse', '', '| Backbone | Phase | Status | Calls | Input tokens | Output tokens | Length stops |',
          '|---|---|---|---:|---:|---:|---:|']
for row in summary['costs']:
    lines.append(f"| {row['model']} | {row['stage']} | {row['status']} | {row['calls']} | {row['input_tokens']} | {row['output_tokens']} | {row['length_stops']} |")
lines += ['', 'Requests, source cache paths, native scores, rule traces and model raw outputs are retained in this package. `subgroups.jsonl` covers action, question scope and patient-info type; `m4_m5_program_changes.jsonl` records every M4/M5 program change; `execution_diagnostics.json` compares option states on the identical frozen facts. See README for pre-inference error findings and rule-bank limits.', '']
(ROOT / 'RESULTS.md').write_text('\n'.join(lines))
print('Saved subgroup, M4/M5 change and frozen-fact execution diagnostics.')
