"""Frozen 2x2 patient/outcome binding experiment using the established runner."""
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import sys
import time

from r4_binding_head import ARMS, check, eligible, optimize, request

OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / 'r4_head_experiment'
spec = importlib.util.spec_from_file_location('first_r4_experiment', PREVIOUS / 'experiment.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
read, write, dump = previous.read, previous.write, previous.dump
runner = previous.runner
runner.OUT = OUT


def tokenizer(cfg):
    sys.path.insert(0, previous.EXTRA_SITE)
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(cfg['model'], local_files_only=True)


def render(tok, cfg, messages):
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                   **cfg.get('chat_template_kwargs', {}))


def prepare():
    assert not (OUT / 'plan.json').exists(), 'Preserve the frozen experiment.'
    check()
    diagnostics = list(read(OUT / 'diagnostic.jsonl'))
    assert len(diagnostics) == 24 and Counter(d['gold'] for d in diagnostics) == {'yes': 12, 'no': 12}
    cohort = list(read(PREVIOUS / 'cohort.jsonl'))
    evaluation = list(read(PREVIOUS / 'evaluation.jsonl'))
    for d in diagnostics:
        item = dict(item_id=d['item_id'], question=d['question'], options={'yes': 'yes', 'no': 'no'},
                    fixed_evidence=[d['evidence']], answer_format='single')
        cohort.append(dict(item_id=d['item_id'], original_id=d['intervention_world'], form='diagnostic', item=item))
        evaluation.append(dict(item_id=d['item_id'], gold=d['gold'], metric='deterministic_rule_diagnostic'))
    assert len(cohort) == len({r['item_id'] for r in cohort}) == 50
    assert all(eligible(r['item']) for r in cohort)
    write(OUT / 'cohort.jsonl', cohort)
    write(OUT / 'evaluation.jsonl', evaluation)
    checks = []
    for method in ('M4', 'M5'):
        directory = OUT / method.lower()
        directory.mkdir(exist_ok=True)
        cfg = json.loads((PREVIOUS / method.lower() / 'config.json').read_text())
        tok = tokenizer(cfg)
        inputs = list(read(PREVIOUS / method.lower() / 'inputs.jsonl'))
        template = inputs[0]
        # Keep each method's native system and formatting; replace only the task/data block for new simulations.
        tail = template['messages'][1]['content'].split(template['item']['question'], 1)[1]
        for row in cohort[26:]:
            item = row['item']
            messages = [dict(template['messages'][0]), dict(role='user', content=
                '\nHere are the relevant documents:\n' + item['fixed_evidence'][0]
                + '\n\nHere is the question:\n' + item['question'] + tail)]
            inputs.append(dict(item=item, messages=messages, original_id=row['original_id'],
                               form='diagnostic', original_response=''))
        schema = next(read(PREVIOUS / method.lower() / 'paired_requests.jsonl'))['schema']
        jobs = []
        for index, row in enumerate(inputs):
            rotation = index % len(ARMS)
            for arm in ARMS[rotation:] + ARMS[:rotation]:
                req = request(row['item'], row['messages'], arm)
                assert req[:-1] == row['messages'] and all(m['role'] != 'assistant' for m in req)
                assert row['item']['question'] in req[1]['content']
                prompt = render(tok, cfg, req)
                length = len(tok.encode(prompt, add_special_tokens=False))
                assert length + cfg['max_tokens'] <= cfg['max_model_len']
                jobs.append(dict(item_id=row['item']['item_id'], arm=arm, prompt=prompt,
                                 prompt_tokens=length, schema=schema))
        assert len(jobs) == 200
        write(directory / 'inputs.jsonl', inputs)
        write(directory / 'paired_requests.jsonl', jobs)
        write(directory / 'baseline_scored.jsonl', read(PREVIOUS / method.lower() / 'baseline_scored.jsonl'))
        dump(directory / 'config.json', cfg)
        checks.append(dict(method=method, calls=len(jobs), max_prompt_tokens=max(r['prompt_tokens'] for r in jobs)))
    dump(OUT / 'plan.json', dict(status='prepared_not_run', at=time.strftime('%Y-%m-%d %H:%M:%S %z'),
        arms=list(ARMS), planned_new_calls=400, methods=['M4', 'M5'], checks=checks,
        hypothesis='Separate patient/source binding and outcome/proposition binding with a 2x2 one-call experiment.',
        scope='13 exposed clinical originals, their 13 modal opposite-outcome probes, and 24 deterministic simulations from3 base worlds/6 intervention worlds.',
        controls='Four fresh calls per input, each original model, actual full context, original schema/decoding, seed42, max2048. Rotate four arms within each batch4 by input index. No old answer appended.',
        inference='Original/native question, documents and choices only. Diagnostics expose their fictional rules. No gold, grouping metadata, expected_event or rationale enters any request.',
        interpretation='Clinical author agreement is not clinical truth; clinical question opposition is diagnostic only. Synthetic rules give exact labels but no clinical generalization. No mechanical answer inversion.',
        decision='One fixed prompt per factor shared across both models. Review original-baseline and fresh-redo repairs/harms and component effects; do not select different arms by item/model or tune on diagnostics.',
        previous_artifacts=str(PREVIOUS), runner=str(previous.RUNNER)))
    print(json.dumps(checks, indent=2))


def compare(rows, lookup, arm):
    return dict(repairs=sum(r['correct'] and not lookup[r['item_id'], arm]['correct'] for r in rows),
                harms=sum(not r['correct'] and lookup[r['item_id'], arm]['correct'] for r in rows))


def analyze():
    objects, score = runner.scoring()
    evaluation = {r['item_id']: r for r in read(OUT / 'evaluation.jsonl')}
    cohort = {r['item_id']: r for r in read(OUT / 'cohort.jsonl')}
    diagnostics = {r['item_id']: r for r in read(OUT / 'diagnostic.jsonl')}
    records, summaries, costs = [], [], []
    replay_count = 0
    for method in ('M4', 'M5'):
        directory = OUT / method.lower()
        raw = list(read(directory / 'paired_raw.jsonl'))
        runtime = json.loads((directory / 'paired_runtime.json').read_text())
        assert runtime['status'] == 'complete' and len(raw) == len({(r['item_id'], r['arm']) for r in raw}) == 200
        baseline = {r['item_id']: r for r in read(directory / 'baseline_scored.jsonl')}
        lookup = {}
        for r in raw:
            row = cohort[r['item_id']]
            obj = objects(r['raw_response'], 'answer_choice')
            native = json.dumps({'answer': obj['answer_choice']}) if obj else ''
            result = score({'raw_response': native}, evaluation[r['item_id']], row['item'], {})
            rec = dict(method=method, item_id=r['item_id'], original_id=row['original_id'], form=row['form'],
                       arm=r['arm'], gold=evaluation[r['item_id']]['gold'], **result)
            records.append(rec)
            lookup[r['item_id'], r['arm']] = rec
        results = []
        for arm in ARMS:
            original = [lookup[i, arm] for i in baseline]
            reversed_rows = [lookup[i + '_reversed', arm] for i in baseline]
            diagnostic_rows = [lookup[i, arm] for i in diagnostics]
            pairs = defaultdict(dict)
            contexts = defaultdict(dict)
            for iid, d in diagnostics.items():
                pairs[d['intervention_world'], d['context_variant']][d['polarity']] = lookup[iid, arm]
                contexts[d['intervention_world'], d['polarity']][d['context_variant']] = lookup[iid, arm]
            results.append(dict(arm=arm, original_n=13, baseline_correct=sum(r['correct'] for r in baseline.values()),
                author_agreement=sum(r['correct'] for r in original), invalid=sum(r['invalid'] for r in original),
                original_repairs=sum(r['correct'] and not baseline[r['item_id']]['correct'] for r in original),
                original_harms=sum(not r['correct'] and baseline[r['item_id']]['correct'] for r in original),
                vs_redo=compare(original, lookup, 'redo'),
                predictions=dict(Counter(str(r['prediction']) for r in original)),
                reversed_formal_agreement=sum(r['correct'] for r in reversed_rows),
                reversed_invalid=sum(r['invalid'] for r in reversed_rows),
                polarity_opposed_pairs=sum(not a['invalid'] and not b['invalid'] and a['prediction'] != b['prediction']
                                          for a, b in zip(original, reversed_rows)),
                both_formal_correct=sum(a['correct'] and b['correct'] for a, b in zip(original, reversed_rows)),
                diagnostic_n=24, diagnostic_correct=sum(r['correct'] for r in diagnostic_rows),
                diagnostic_invalid=sum(r['invalid'] for r in diagnostic_rows),
                diagnostic_vs_redo=compare(diagnostic_rows, lookup, 'redo'),
                diagnostic_by_context={c:sum(lookup[i, arm]['correct'] for i,d in diagnostics.items() if d['context_variant']==c)
                                       for c in ('clean', 'distractor')},
                diagnostic_both_polarities_correct=sum(all(r['correct'] for r in pair.values()) for pair in pairs.values()),
                diagnostic_context_invariant=sum(not p['clean']['invalid'] and not p['distractor']['invalid']
                    and p['clean']['prediction']==p['distractor']['prediction'] for p in contexts.values())))
        effects = {}
        for metric in ('author_agreement', 'diagnostic_correct', 'polarity_opposed_pairs'):
            a,b,c,d = [r[metric] for r in results]
            effects[metric] = dict(scope_without_outcome=b-a, scope_with_outcome=d-c,
                                   outcome_without_scope=c-a, outcome_with_scope=d-b, interaction=d-c-b+a)
        summaries.append(dict(method=method, results=results, factorial_differences=effects))
        costs.append(dict(method=method, calls=len(raw), input_tokens=sum(r['prompt_tokens'] for r in raw),
            output_tokens=sum(r['completion_tokens'] for r in raw), length_stops=sum(r['finish_reason']=='length' for r in raw),
            worker_seconds=runtime['elapsed_seconds'], initialization_seconds=runtime['initialization_seconds']))
        cfg = json.loads((directory / 'config.json').read_text())
        tok = tokenizer(cfg)
        executed = {(r['item_id'], r['arm']):r['prompt'] for r in read(directory / 'paired_requests.jsonl')}
        saved = {(r['item_id'], r['arm']):r['raw_response'] for r in raw}
        for row in read(directory / 'inputs.jsonl'):
            for arm in ARMS:
                key = row['item']['item_id'], arm
                def cached(messages):
                    assert render(tok, cfg, messages) == executed[key]
                    return saved[key]
                result = optimize(row['item'], row['messages'], row['original_response'], cached, arm)
                assert result == dict(raw_response=saved[key], applied=True, calls=1)
                replay_count += 1
    write(OUT / 'scored.jsonl', records)
    dump(OUT / 'summary.json', dict(status='complete', results=summaries, costs=costs, new_calls=400))
    dump(OUT / 'replay.json', dict(exact_requests=replay_count, cached_callbacks=replay_count, new_calls=0))
    plan = json.loads((OUT / 'plan.json').read_text())
    plan.update(status='complete', finished_at=time.strftime('%Y-%m-%d %H:%M:%S %z'), completed_new_calls=400)
    dump(OUT / 'plan.json', plan)
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'run', 'analyze'))
    parser.add_argument('--method', choices=('M4', 'M5'))
    parser.add_argument('--gpu', type=int)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'run':
        runner.run_model(args.method, args.gpu, 'paired', list(ARMS))
    else:
        analyze()
