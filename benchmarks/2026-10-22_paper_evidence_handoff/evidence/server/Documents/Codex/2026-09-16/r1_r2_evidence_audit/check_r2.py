"""CPU audit of frozen R2 evidence; write only beside this script, no new inference.

Detect stale scores/request drift, label dependency, fabricated fact provenance,
format-only improvements and denominator mistakes before accepting the report.
"""
from collections import Counter
from pathlib import Path
import itertools
import json
import os
import sys

ROOT = Path('/home/data3/txy/Documents/Codex/2026-09-14/new-chat')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from r2_condition_head import optimize, check
from r2_positive_facts import build_request, clean_extraction
from r2_program_head import eligible, assemble
from r2_action_scope import execute_scoped, renal_question, requested_action
from r2_support_interface import option_keys
from r2_program_all_methods import MODEL
from r2_guideline_rules import RULES
from r2_support_pilot import PACK
os.environ['CF_SCREENING_OUTPUT'] = 'results_cf_full_comparison'
sys.path.insert(0, str(PACK / 'scripts'))
from analyze_cf_baseline_screening import score


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def normalize(value):
    return list(value) if isinstance(value, tuple) else value


check()
refs = [r for r in read(ROOT / 'r2_question_scope_analysis/positive_facts_scored.jsonl') if r['policy'] == 'inherit_unknown']
bases = {(r['method'], r['item_id']): r for r in read(ROOT / 'r2_program_all_methods/scored.jsonl') if r['policy'] == 'baseline'}
items = {r['item']['item_id']: r['item'] for r in read(ROOT / 'r2_positive_facts_qwen/inputs.jsonl') if r['scope'] == 'native'}
assert len(items) == 79 and len(bases) == len(refs) == 553

# Compare to real selected v5 scores, not just the R2 excerpt/old audit receipt.
guide = json.loads((ROOT / 'r2_question_scope_analysis/guide_verification_20260915.json').read_text())
source_rows = {}
for source in guide['baseline_sources']:
    # These two original runners use native names in the saved score files.
    native_methods = {'tcrag': 'M7', 'medgenie': 'M6'}
    rows = [dict(r, method=native_methods.get(r.get('method'), r.get('method'))) for r in read(source['path'])]
    selected = [r for r in rows if r.get('method') in source['methods'] and (r['method'], r['item_id']) in bases]
    for r in selected:
        b = bases[r['method'], r['item_id']]
        assert all(r[k] == b[k] for k in ['record_id', 'prediction', 'correct', 'invalid', 'invalid_reason', 'gold'])
        assert (r['method'], r['item_id']) not in source_rows
        source_rows[r['method'], r['item_id']] = source['path']
assert len(source_rows) == 553

raws, requests, traces, physical, probes = {}, {}, {}, [], []
for model in ['llama', 'qwen']:
    old, positive = ROOT / ('r2_task_scoped_' + model), ROOT / ('r2_positive_facts_' + model)
    raw = {r['item_id']: r for r in read(old / 'raw_predictions.jsonl') if r['review'] == 'facts'}
    req = {r['item_id']: r for r in read(old / 'requests.jsonl') if r['review'] == 'facts'}
    new = read(positive / 'gpu3/predictions.jsonl')
    reused = read(positive / 'reused_predictions.jsonl')
    old_physical = {r['item_id']: r for p in old.glob('gpu*/predictions.jsonl') for r in read(p) if r['review'] == 'facts'}
    archived = {r['item_id']: r for r in read(positive / 'raw_predictions.jsonl')}
    assert len(new) == 71 and all(r == archived[r['item_id']] for r in new)
    native_new = [r for r in new if r['item_id'] in items]
    native_reuse = [r for r in reused if r['item_id'] in items]
    assert len(native_new) == 27 and len(native_reuse) == 28
    for r in native_reuse:
        assert all(r[k] == old_physical[r['item_id']][k] for k in old_physical[r['item_id']])
    raw.update(archived)
    req.update({r['item_id']: r for r in read(positive / 'requests.jsonl')})
    raws[model], requests[model] = raw, req
    current = {r['item_id']: r for r in read(positive / 'extractions.jsonl') if r['scope'] == 'native'}
    model_traces = {}
    for iid, item in items.items():
        if not eligible(item):
            continue
        minimal = {k: item[k] for k in ['question', 'options', 'answer_format']}
        polluted = dict(minimal, item_id='arbitrary', gold=['NOT_AN_OPTION'], evaluation_labels=['R5'], target_rule='unused')
        assert build_request(minimal) == build_request(polluted)
        assert build_request(minimal) == {k: req[iid][k] for k in ['messages', 'schema']}
        action, facts, errors = clean_extraction(minimal, json.loads(raw[iid]['raw_response']))
        assert facts == current[iid]['facts'] and sorted(errors,key=lambda e:e['field']) == sorted(current[iid]['evidence_errors'],key=lambda e:e['field']), (model,iid)
        model_traces[iid] = execute_scoped(minimal, action, facts)
    traces[model] = model_traces
    physical.append(dict(model=model, native_new=len(native_new), native_reused=len(native_reuse), native_fact_sets=len(model_traces), physical_parity=True))
    for scope in ['rule_probe', 'scope_probe']:
        rows = [r for r in read(positive / 'scored.jsonl') if r['scope'] == scope]
        probes.append(dict(model=model, scope=scope, n=len(rows), correct=sum(r['correct'] for r in rows), invalid=sum(r['invalid'] for r in rows)))

calls = []
receipts = []
for ref in refs:
    method, iid = ref['method'], ref['item_id']
    b, model = bases[method, iid], MODEL[method]
    item = {k: items[iid][k] for k in ['question', 'options', 'answer_format']}
    def replay(messages, schema):
        assert messages == requests[model][iid]['messages'] and schema == requests[model][iid]['schema']
        calls.append((method, iid))
        return raws[model][iid]['raw_response']
    result = optimize(item, None if b['invalid'] else b['prediction'], replay)
    scored = score({'raw_response': json.dumps({'answer': result['answer']})}, ref, item, {}) if result['applied'] else b
    assert normalize(scored['prediction']) == ref['prediction'] and all(scored[k] == ref[k] for k in ['correct', 'invalid'])
    # Independent exact-set check detects accidental semantic/fuzzy scorer gains.
    exact = (set(ref['prediction']) == set(ref['gold']) if item['answer_format'] == 'multi' else ref['prediction'] == ref['gold']) if not ref['invalid'] else False
    assert exact == ref['correct']
    keys, none = option_keys(item)
    mixed = not b['invalid'] and item['answer_format'] == 'multi' and none in b['prediction'] and len(b['prediction']) > 1
    receipts.append(dict(method=method, item_id=iid, applied=result['applied'], reason=result['reason'], baseline_invalid=b['invalid'], baseline_mixed_none=mixed, repaired=not b['correct'] and ref['correct'], harmed=b['correct'] and not ref['correct']))
assert len(calls) == len(set(calls)) == 385

summary = []
for method in MODEL:
    rr = [r for r in refs if r['method'] == method]
    rec = [r for r in receipts if r['method'] == method]
    constant = support = 0
    groups = {}
    for group in ['none', 'remaining', 'M14']:
        selected = []
        for r in rr:
            item = items[r['item_id']]
            none = item['answer_format'] == 'multi' and any(item['options'][k] == 'None of the above' for k in r['gold'])
            if {'none': none, 'remaining': item['answer_format'] == 'multi' and not none, 'M14': item['answer_format'] == 'single'}[group]:
                selected.append(r)
        groups[group] = dict(n=len(selected), baseline=sum(bases[method, r['item_id']]['correct'] for r in selected), head=sum(r['correct'] for r in selected))
    for r in rr:
        iid, item = r['item_id'], items[r['item_id']]
        b = bases[method, iid]
        if eligible(item):
            keys, none = option_keys(item)
            met = [k for k in keys if traces[MODEL[method]][iid][k]['state'] == 'MET']
            constant += score({'raw_response': json.dumps({'answer': [none]})}, r, item, {})['correct']
            support += score({'raw_response': json.dumps({'answer': met or [none]})}, r, item, {})['correct']
        else:
            constant += b['correct']
            support += b['correct']
    summary.append(dict(method=method, n=len(rr), baseline=sum(bases[method,r['item_id']]['correct'] for r in rr), head=sum(r['correct'] for r in rr), groups=groups, baseline_invalid=sum(r['baseline_invalid'] for r in rec), head_invalid=sum(r['invalid'] for r in rr), repairs=sum(r['repaired'] for r in rec), harms=sum(r['harmed'] for r in rec), repaired_from_invalid=sum(r['repaired'] and r['baseline_invalid'] for r in rec), repaired_mixed_none=sum(r['repaired'] and r['baseline_mixed_none'] for r in rec), baseline_mixed_none=sum(r['baseline_mixed_none'] for r in rec), same_coverage_none=constant, same_coverage_support_only=support))

dependencies = []
for model, ts in traces.items():
    states = Counter(x['state'] for trace in ts.values() for x in trace.values())
    full, sensitive, defaulted = [], [], []
    for iid, trace in ts.items():
        item = items[iid]
        keys, none = option_keys(item)
        if assemble(item, None, trace) is not None:
            full.append(iid)
        initials = [[none]] + [list(c) for n in range(1,len(keys)+1) for c in itertools.combinations(keys,n)]
        answers = {tuple(assemble(item, initial, trace) or []) for initial in initials}
        if len(answers) > 1:
            sensitive.append(iid)
        if any(p['used_default_recommendation'] for v in trace.values() for p in v['paths']):
            defaulted.append(iid)
    dependencies.append(dict(model=model, option_states=dict(states), covered=55, answerable_without_initial=len(full), initial_sensitive=len(sensitive), unknown_exception_default_used=len(defaulted), initial_sensitive_ids=sensitive))

controls = []
for model in ['qwen','llama']:
    rows = read(ROOT / ('r2_samefacts_reasoning_' + model) / 'scored.jsonl')
    for method in sorted({r['method'] for r in rows}):
        rr = [r for r in rows if r['method'] == method and r['scope'] == 'native']
        controls.append(dict(model=model, version='historical indexed facts before question scope/positive fields', method=method, n=len(rr), correct=sum(r['correct'] for r in rr)))

report = dict(status='passed',new_model_calls=0, baseline_source_parity=553, api_records=len(receipts), exact_actual_request_replays=len(calls), inference_item_keys=['question','options','answer_format'], metadata_invariance_requests=110, physical_fact_provenance=physical, rules=len(RULES), drug_names=len({d for r in RULES for d in r['drugs']}), covered=sum(eligible(i) for i in items.values()), actions=dict(Counter(requested_action(i) for i in items.values() if eligible(i))), renal=sum(renal_question(i) for i in items.values()), routes=dict(Counter(r['reason'] for r in receipts)), results=summary, dependencies=dependencies, probes=probes, historical_samefacts=controls, baseline_sources=guide['baseline_sources'], receipts=receipts)
(OUT / 'r2_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['receipts','baseline_sources']},ensure_ascii=False,indent=2))
