"""Frozen R2 transfer to all 96 native R1 MedPIC tasks; no model or rule edits."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
OLD = OUT.parents[2] / '2026-09-14/new-chat'
sys.path.insert(0, str(OLD))
sys.path.insert(0, str(OUT / 'head'))
from audit_existing_results import BASE, M4, ROOT, SOURCES
from r2_condition_head import optimize, resolve, build_request
from r2_program_head import eligible, relevant_rules, assemble
from r2_action_scope import renal_question, requested_action
from r2_program_all_methods import MODEL
from r2_samefacts_control import request as samefacts_request


def read(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream]


def write(path, rows):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def spec(row):
    return {key: row[key] for key in ('messages', 'schema')}


def cached(model, stage, requests):
    """Compare actual saved messages/schema and generation config; no label lookup."""
    sources = [OLD / 'r3_rule_transfer' / model / stage]
    if stage == 'facts':
        sources += [OLD / ('r2_positive_facts_' + model), OLD / ('r2_task_scoped_' + model)]
    cfg = json.loads((OUT / model / 'config.json').read_text())
    lookup = {}
    for root in sources:
        source_cfg = json.loads((root / 'config.json').read_text())
        keys = ('model', 'seed', 'temperature', 'top_p', 'top_k', 'max_tokens')
        assert all(cfg[k] == source_cfg[k] for k in keys), str(root)
        assert cfg.get('chat_template_kwargs', {}) == source_cfg.get('chat_template_kwargs', {})
        specs = {(r['item_id'], r['review']): spec(r) for r in read(root / 'requests.jsonl')}
        files = list(root.glob('gpu*/predictions.jsonl')) if root.parent.name == model else [root / 'raw_predictions.jsonl']
        for path in files:
            for row in read(path):
                key = row['item_id'], row['review']
                if key not in specs:
                    continue
                wanted = requests.get(row['item_id'])
                if wanted and spec(wanted) == specs[key] and row['item_id'] not in lookup:
                    lookup[row['item_id']] = dict(row, cached_from=str(path), cached_review=row['review'],
                        review=stage, request_identity='messages/schema and model/generation parameters equal')
    return lookup


def jobs(model, stage, items, requests):
    root = OUT / model / stage
    root.mkdir()
    reused = cached(model, stage, {r['item_id']: r for r in requests})
    fresh = [r for r in requests if r['item_id'] not in reused]
    write(root / 'inputs.jsonl', [dict(item=item) for item in items])
    write(root / 'requests.jsonl', fresh)
    write(root / 'all_requests.jsonl', requests)
    write(root / 'reused_predictions.jsonl', reused.values())
    cfg = json.loads((OUT / model / 'config.json').read_text())
    dump(root / 'config.json', cfg)
    result = dict(total_requests=len(requests), new_calls=len(fresh), reused=len(reused),
                  reused_ids=sorted(reused), reused_sources=dict(Counter(r['cached_from'] for r in reused.values())))
    dump(root / 'preparation.json', result)
    return result


def error_kind(row):
    if row['invalid']:
        return 'invalid'
    if row['correct']:
        return 'correct'
    return 'extra_and_missing' if row['fp'] and row['fn'] else 'extra_only' if row['fp'] else 'missing_only'


def prepare():
    assert not (OUT / 'plan.json').exists()
    evaluation = [r for r in read(BASE / 'evaluation.jsonl') if r['resource_id'] == 'M02'
                  and 'R1' in r['evaluation_labels'] and r['role'] != 'reference']
    assert len(evaluation) == len({r['unit_id'] for r in evaluation}) == 96
    wanted = {r['item_id'] for r in evaluation}
    items = [r for r in read(BASE / 'items.jsonl') if r['item_id'] in wanted]
    assert len(items) == 96 and all(r['answer_format'] == 'multi' and not r['fixed_evidence'] for r in items)
    itemmap = {r['item_id']: r for r in items}
    sources = [*SOURCES, (ROOT / '2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/m6_medgenie_v5_full/scores/scored.jsonl', {'medgenie': 'M6'})]
    baseline = []
    for path, mapping in sources:
        baseline += [dict(r, method=mapping[r['method']], score_source=str(path)) for r in read(path)
                     if r['method'] in mapping and r['item_id'] in wanted and r['record_id'] in {e['record_id'] for e in evaluation}]
    assert len(baseline) == len({(r['method'], r['item_id']) for r in baseline}) == 672
    predictions = []
    for method, path in [('M4', M4 / 'M4/predictions.jsonl'), ('M5', BASE / 'M5/predictions.jsonl')]:
        predictions += [dict(r, method=method, prediction_source=str(path)) for r in read(path) if r['item_id'] in wanted]
    assert len(predictions) == 192
    bmap = {(r['method'], r['item_id']): r for r in baseline}
    pmap = {(r['method'], r['item_id']): r for r in predictions}
    strata = []
    for e in sorted(evaluation, key=lambda r: r['item_id']):
        item = itemmap[e['item_id']]
        strata.append(dict(item_id=e['item_id'], unit_id=e['unit_id'], eligible=eligible(item),
            r3_overlap='R3' in e['evaluation_labels'], r2_overlap='R2' in e['evaluation_labels'],
            action=requested_action(item), scope='renal' if renal_question(item) else 'general',
            operation=e['old_evaluation_record']['official_operation'],
            patient_info=e['old_evaluation_record']['patient_info_type'],
            rules=[r['id'] for r in relevant_rules(item)],
            gold=e['gold'], errors={m: error_kind(bmap[m, e['item_id']]) for m in ('M4', 'M5')}))
    for name, rows in [('items', items), ('evaluation', evaluation), ('baseline_scored', baseline),
                       ('baseline_raw', predictions), ('strata', strata)]:
        write(OUT / (name + '.jsonl'), rows)
    blocks = []
    for i, s in enumerate(strata):
        item = itemmap[s['item_id']]
        blocks += [f"\n[{i+1}] {s['item_id']} {s['unit_id']} eligible={s['eligible']} R3={s['r3_overlap']} {s['operation']} {s['patient_info']} action={s['action']} scope={s['scope']}",
                   item['question'], json.dumps(item['options'], ensure_ascii=False),
                   'GOLD ' + str(s['gold']) + ' | ' + ' | '.join(f"{m} {bmap[m,s['item_id']]['prediction']} {s['errors'][m]}" for m in ('M4', 'M5'))]
    (OUT / 'all96_readable.txt').write_text('\n'.join(blocks) + '\n')
    sample = []
    for m in ('M4', 'M5'):
        for category in sorted({(s['eligible'], s['patient_info'], s['errors'][m]) for s in strata if s['errors'][m] != 'correct'}):
            s = next(s for s in strata if (s['eligible'], s['patient_info'], s['errors'][m]) == category)
            sample.append(dict(stratum=s, item=itemmap[s['item_id']], method=m, baseline=bmap[m,s['item_id']], raw=pmap[m,s['item_id']]['raw_response']))
    write(OUT / 'stratified_raw_errors.jsonl', sample)
    checks = {}
    for model in ('llama', 'qwen'):
        (OUT / model).mkdir()
        cfg = json.loads((OLD / 'r3_rule_transfer' / model / 'facts/config.json').read_text())
        cfg['gpu_memory_utilization'] = 0.30
        dump(OUT / model / 'config.json', cfg)
        applicable = [r for r in items if eligible(r)]
        requests = [dict(item_id=r['item_id'], review='facts', **build_request(r)) for r in applicable]
        checks[model] = jobs(model, 'facts', applicable, requests)
    report = dict(scope=96, covered=sum(s['eligible'] for s in strata), uncovered=sum(not s['eligible'] for s in strata),
        r3_overlap=sum(s['r3_overlap'] for s in strata), errors={m:dict(Counter(s['errors'][m] for s in strata)) for m in ('M4','M5')},
        operations=dict(Counter(s['operation'] for s in strata)), patient_info=dict(Counter(s['patient_info'] for s in strata)),
        actions=dict(Counter(s['action'] for s in strata)), samefacts='same scope, rules, extracted facts, default exception policy; explanation budget 2048',
        facts=checks, new_inference=0, policy='Frozen MET union (original selection intersect UNKNOWN); outside coverage original pass-through',
        original_methods=MODEL, raw_error_strata=len(sample), status='prepared_pending_manual_error_review')
    dump(OUT / 'plan.json', report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def outputs(model, stage):
    root = OUT / model / stage
    rows = read(root / 'reused_predictions.jsonl')
    for path in root.glob('gpu*/predictions.jsonl'):
        rows += read(path)
    lookup = {r['item_id']: r for r in rows}
    assert len(rows) == len(lookup) == len(read(root / 'all_requests.jsonl'))
    return lookup


def prepare_execution(model):
    items = read(OUT / 'items.jsonl')
    raw = outputs(model, 'facts')
    requests, extractions = [], []
    for item in items:
        iid = item['item_id']
        if iid not in raw:
            continue
        result = optimize(item, None, lambda *_: raw[iid]['raw_response'])
        extractions.append(dict(item_id=iid, **result))
        if 'facts' not in result:
            continue
        req = samefacts_request(item, result, 'readable')
        # Old R3 transfer contained general questions only. Keep the new renal control's
        # supplied rule bank identical to the actual frozen program's scoped paths.
        content = req['messages'][-1]['content']
        obj, end = json.JSONDecoder().raw_decode(content)
        for key, lines in obj['rules_by_option'].items():
            allowed = {r['rule_id'] for r in result['options'][key]['paths']}
            obj['rules_by_option'][key] = [line for line in lines if line.split(':', 1)[0] in allowed]
        content = json.dumps(obj, ensure_ascii=False) + content[end:]
        old = 'Return only the requested JSON option states; no explanation, no action, no answer selection.'
        assert old in content
        req['messages'][-1]['content'] = content.replace(old,
            'Work through each rule prerequisite and complete exception, then combine its independent paths. '
            'Return a JSON object with reasoning (at most 300 words) followed by options, containing every supplied option state. '
            'Reason only from these frozen facts and rules, without adding patient facts or external medical rules.')
        req['schema'] = dict(type='object', properties={'reasoning': {'type':'string'}, 'options':req['schema']},
                             required=['reasoning','options'], additionalProperties=False)
        requests.append(dict(item_id=iid, review='execute', **req))
    write(OUT / model / 'fact_extractions.jsonl', extractions)
    print(model, 'execute', jobs(model, 'execute', [r for r in items if r['item_id'] in raw], requests), flush=True)


def summarize():
    from r3_delayed_options_pilot import scoring_tools
    _, score = scoring_tools()
    items = {r['item_id']: r for r in read(OUT / 'items.jsonl')}
    evaluation = {r['item_id']: r for r in read(OUT / 'evaluation.jsonl')}
    strata = {r['item_id']: r for r in read(OUT / 'strata.jsonl')}
    facts = {m: outputs(m, 'facts') for m in ('llama','qwen')}
    specs = {m:{r['item_id']:spec(r) for r in read(OUT/m/'facts/all_requests.jsonl')} for m in facts}
    executions = {m:outputs(m, 'execute') for m in facts}
    scored, traces = [], []
    replayed = 0
    for b in read(OUT / 'baseline_scored.jsonl'):
        iid, method = b['item_id'], b['method']
        item, e, model = items[iid], evaluation[iid], MODEL[method]
        initial = None if b['invalid'] else tuple(b['prediction'])
        if initial is not None:
            old = score(dict(raw_response=json.dumps(dict(answer=initial))), e, item, {})
            assert all(old[k] == b[k] for k in ('correct','invalid','invalid_reason'))
        for policy in ('baseline','program','model_execute'):
            result, answer, details = b, initial, None
            if policy == 'program':
                def callback(messages, schema):
                    nonlocal replayed
                    assert dict(messages=messages, schema=schema) == specs[model][iid]
                    replayed += 1
                    return facts[model][iid]['raw_response']
                details = optimize(item, initial, callback)
                answer = details['answer']
            elif policy == 'model_execute' and iid in executions[model]:
                try:
                    states = json.loads(executions[model][iid]['raw_response'])['options']
                    from r2_support_interface import option_keys
                    assert set(states) == set(option_keys(item)[0])
                    assert all(v in ('MET','CONTRADICTED','UNKNOWN') for v in states.values())
                    details = {k:dict(state=v) for k,v in states.items()}
                    selected = assemble(item, initial, details)
                    answer = initial if selected is None else selected
                except (ValueError, KeyError, TypeError, AssertionError) as exc:
                    details = dict(error=f'{type(exc).__name__}: {exc}')
            original_non_ok = method in ('M6', 'M7') and b.get('runtime_status') != 'ok'
            candidate_metric = None
            if policy != 'baseline' and answer is not None:
                candidate_metric = score(dict(raw_response=json.dumps(dict(answer=answer))), e, item, {})
                result = candidate_metric
            row = {**b, **result, 'policy':policy, 'fact_model':model,
                   'repaired':result['correct'] and not b['correct'], 'harmed':b['correct'] and not result['correct'],
                   'covered':strata[iid]['eligible'], 'r3_overlap':strata[iid]['r3_overlap'],
                   'original_non_ok_terminal':original_non_ok,
                   'original_runtime_status':b.get('runtime_status'),
                   'original_termination':b.get('termination')}
            scored.append(row)
            if policy != 'baseline':
                traces.append(dict(item_id=iid, method=method, policy=policy, initial=initial, answer=answer, details=details,
                                   original_non_ok_terminal=original_non_ok))
    summaries = []
    for method in MODEL:
        for policy in ('baseline','program','model_execute'):
            for group in ('all96','covered72','uncovered24','old_r3_10','new_covered62','r1_without_r3_86'):
                rs = [r for r in scored if r['method']==method and r['policy']==policy and
                      {'all96':True,'covered72':r['covered'],'uncovered24':not r['covered'],
                       'old_r3_10':r['r3_overlap'],'new_covered62':r['covered'] and not r['r3_overlap'],
                       'r1_without_r3_86':not r['r3_overlap']}[group]]
                summaries.append(dict(method=method, policy=policy, group=group, n=len(rs),
                    correct=sum(r['correct'] for r in rs), invalid=sum(r['invalid'] for r in rs),
                    repairs=sum(r['repaired'] for r in rs), harms=sum(r['harmed'] for r in rs)))
    costs = []
    for model in facts:
        for stage in ('facts','execute'):
            rows = list(outputs(model,stage).values())
            for status in ('new','reused'):
                rs = [r for r in rows if ('cached_from' in r)==(status=='reused')]
                costs.append(dict(model=model,stage=stage,status=status,calls=len(rs),
                    input_tokens=sum(r['prompt_tokens'] for r in rs), output_tokens=sum(r['completion_tokens'] for r in rs),
                    length_stops=sum(r['finish_reason']=='length' for r in rs)))
    write(OUT/'scored.jsonl',scored);write(OUT/'traces.jsonl',traces)
    dump(OUT/'summary.json',dict(status='complete_development',results=summaries,costs=costs,
        interface_replayed_callbacks=replayed, no_new_full_method_runs=True,
        native_terminal_policy='Original M6/M7 non-ok answers remain None; newly generated head answers are scored separately and do not change original runtime status. Strict-state retention is a separate sensitivity control.',
        note='Two original backbones, seven original-answer offline attachments; all exposed v5 development.'))
    print(json.dumps([r for r in summaries if r['group']=='all96'],indent=2),flush=True)


def run(gpu):
    started = time.time()
    for model in ('llama','qwen'):
        for stage in ('facts','execute'):
            if stage=='execute':
                prepare_execution(model)
            root=OUT/model/stage
            if not read(root/'requests.jsonl'):
                continue
            log=root/f'gpu{gpu}.log'
            assert not log.exists()
            dump(OUT/'runtime.json',dict(status='running',pid=os.getpid(),model=model,stage=stage,gpu=gpu))
            with log.open('w') as stream:
                child=subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'worker','--model',model,'--stage',stage,'--gpu',str(gpu)],stdout=stream,stderr=subprocess.STDOUT,cwd=OUT)
            if child.returncode:
                dump(OUT/'runtime.json',dict(status='failed',model=model,stage=stage,returncode=child.returncode,log=str(log)))
                raise RuntimeError(str(log))
    summarize()
    dump(OUT/'runtime.json',dict(status='complete',gpu=gpu,elapsed_seconds=time.time()-started))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['prepare','run','worker','summarize'])
    parser.add_argument('--gpu',type=int,default=3)
    parser.add_argument('--model',choices=['llama','qwen'])
    parser.add_argument('--stage',choices=['facts','execute'])
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='run':run(args.gpu)
    elif args.action=='summarize':summarize()
    else:
        from r2_interface_pilot import run as worker
        worker(args.gpu,OUT/args.model/args.stage)
