"""Matched one-call development/validation, reusing the established GPU runner."""
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

from head import ARMS, SCHEMAS, check, optimize, request
from executor import expand_schedule, project as project_trajectory

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'clinical_prior'
sys.path.insert(0, str(OUT.parents[1] / 'r4_head_binding'))
spec = importlib.util.spec_from_file_location('r4_matched_helpers', OUT.parents[1] / 'r4_head_binding/experiment.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
read, write, dump = previous.read, previous.write, previous.dump
runner = previous.runner
NUMERIC_TOLERANCE = 1.0  # mg/dL, fixed before development predictions.


def prepare(split, reused_redo=None):
    directory = OUT / split
    rows = list(read(directory / 'inputs.jsonl'))
    check()
    checks = []
    for method in ('M4', 'M5'):
        target = directory / method.lower()
        target.mkdir(exist_ok=True)
        assert not (target / 'matched_requests.jsonl').exists()
        cfg = json.loads((SOURCE / method.lower() / 'config.json').read_text())
        tok = previous.tokenizer(cfg)
        jobs = []
        for index, row in enumerate(rows):
            offset = index % len(ARMS)
            for arm in ARMS[offset:] + ARMS[:offset]:
                messages = request(row['native_input'], row['question'], arm)
                prompt = previous.render(tok, cfg, messages)
                length = len(tok.encode(prompt, add_special_tokens=False))
                assert length + cfg['max_tokens'] <= cfg['max_model_len']
                jobs.append(dict(item_id=row['item_id'], arm=arm, prompt=prompt,
                    prompt_tokens=length, schema=SCHEMAS[arm]))
        write(target / 'matched_requests.jsonl', jobs)
        dump(target / 'config.json', cfg)
        reused_count=0
        if reused_redo:
            old_requests={r['item_id']:r for r in read(reused_redo/method.lower()/'matched_requests.jsonl') if r['arm']=='redo'}
            for row in rows:
                expected=old_requests[row['item_id']]
                assert expected['schema']==SCHEMAS['redo']
                assert previous.render(tok,cfg,request(row['native_input'],row['question'],'redo'))==expected['prompt']
                reused_count+=1
        checks.append(dict(method=method, cases=len(rows), calls=len(jobs),
            reused_redo_calls=reused_count, max_prompt_tokens=max(r['prompt_tokens'] for r in jobs)))
    dump(directory / 'preparation.json', dict(status='prepared_not_run', split=split,
        at=time.strftime('%Y-%m-%d %H:%M:%S %z'), numeric_tolerance_mg_dL=NUMERIC_TOLERANCE,
        checks=checks, arms=list(ARMS), planned_new_calls=len(rows)*len(ARMS)*2,
        reused_redo_from=str(reused_redo) if reused_redo else None,
        permissions='Same full author patient code and visible state/parameters/factual schedule/question in all arms. Gold plans and numeric trajectories absent.',
        scope='Known-model virtual-patient consequences; no new independent clinical ground truth.',
        controls='One call per arm. full and patch share numerical tool. redo has same information without tool. Inline and no-do are projections with no extra generations.'))
    print(json.dumps(checks, indent=2), flush=True)


def grade(answer, expected):
    prediction = answer.get('answer_choice')
    result = dict(prediction=prediction, correct=prediction == expected['answer_choice'],
        invalid=prediction not in ('yes', 'no'))
    for field in ('counterfactual_value', 'difference'):
        value = answer.get(field)
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
        error = abs(value - expected[field]) if valid else None
        result[field + '_error'] = error
        result[field + '_valid'] = valid
        result[field + '_within_tolerance'] = valid and error <= NUMERIC_TOLERANCE
    result['joint_numeric_correct'] = all(result[f + '_within_tolerance'] for f in ('counterfactual_value', 'difference'))
    result['all_outputs_correct'] = result['correct'] and result['joint_numeric_correct']
    return result


def source_no_do(reference):
    query = reference['oracle_ir']['query']
    value = reference['factual_value'] if query['quantity']=='counterfactual' else 0.
    threshold = query['threshold']
    truth = {'ge': value>=threshold, 'le': value<=threshold, 'lt': value<threshold}[query['comparison']]
    return dict(counterfactual_value=reference['factual_value'], difference=0., answer_choice='yes' if truth else 'no')


def summarize(records):
    groups = defaultdict(list)
    for row in records:
        groups[row['method'], row['arm']].append(row)
    result = []
    for (method, arm), rows in groups.items():
        entry = dict(method=method, arm=arm, n=len(rows),
            correct=sum(r['correct'] for r in rows), invalid=sum(r['invalid'] for r in rows),
            joint_numeric_correct=sum(r['joint_numeric_correct'] for r in rows),
            all_outputs_correct=sum(r['all_outputs_correct'] for r in rows),
            routes=dict(Counter(r['route'] for r in rows)))
        for field in ('counterfactual_value', 'difference'):
            errors = [r[field+'_error'] for r in rows if r[field+'_valid']]
            entry[field] = dict(valid_n=len(errors), missing_n=len(rows)-len(errors),
                mae=sum(errors)/len(errors) if errors else None,
                rmse=math.sqrt(sum(e*e for e in errors)/len(errors)) if errors else None,
                within_tolerance=sum(r[field+'_within_tolerance'] for r in rows))
        entry['by_profile'] = {p: dict(n=sum(r['profile']==p for r in rows),
            correct=sum(r['correct'] for r in rows if r['profile']==p),
            joint_numeric_correct=sum(r['joint_numeric_correct'] for r in rows if r['profile']==p))
            for p in sorted({r['profile'] for r in rows})}
        for key in ('schedule_faithful', 'query_faithful', 'fully_faithful'):
            if any(key in r for r in rows):
                entry[key] = sum(r.get(key, False) for r in rows)
        for group in ('scenario', 'time_min', 'predicate_changes'):
            entry['by_'+group] = {str(value): dict(n=sum(r[group]==value for r in rows),
                correct=sum(r['correct'] for r in rows if r[group]==value),
                joint_numeric_correct=sum(r['joint_numeric_correct'] for r in rows if r[group]==value))
                for value in sorted({r[group] for r in rows})}
        result.append(entry)
    return result


def analyze(split, reused_redo=None):
    directory = OUT / split
    inputs = {r['item_id']:r for r in read(directory / 'inputs.jsonl')}
    evaluation = {r['item_id']:r for r in read(directory / 'evaluation.jsonl')}
    records, executions, costs = [], [], []
    replays = 0
    for method in ('M4', 'M5'):
        target = directory / method.lower()
        cfg = json.loads((target / 'config.json').read_text())
        tok = previous.tokenizer(cfg)
        requests = {(r['item_id'],r['arm']):r for r in read(target / 'matched_requests.jsonl')}
        raw = list(read(target / 'matched_raw.jsonl'))
        runtime = json.loads((target / 'matched_runtime.json').read_text())
        assert runtime['status']=='complete' and len(raw)==len(requests)==len(inputs)*len(ARMS)
        new_raw=list(raw)
        if reused_redo:
            raw.extend(dict(r,generation_origin='reused_v1_redo') for r in read(reused_redo/method.lower()/'matched_raw.jsonl') if r['arm']=='redo')
            requests.update({(r['item_id'],r['arm']):r for r in read(reused_redo/method.lower()/'matched_requests.jsonl') if r['arm']=='redo'})
            write(target/'effective_raw.jsonl',raw)
        assert len(raw)==len(requests)==len(inputs)*3
        assert len({(r['item_id'],r['arm']) for r in raw})==len(raw)
        for index, response in enumerate(raw):
            iid, arm = response['item_id'], response['arm']
            row, reference = inputs[iid], evaluation[iid]
            def cached(messages, schema):
                assert schema == requests[iid,arm]['schema']
                assert previous.render(tok, cfg, messages) == requests[iid,arm]['prompt']
                return response['raw_response']
            result = optimize(row['native_input'], row['question'], cached, arm)
            replays += result['calls']
            expected = dict(counterfactual_value=reference['counterfactual_value'],
                difference=reference['difference'], answer_choice=reference['gold'])
            base = dict(method=method, item_id=iid, profile=row['profile'],
                scenario=row['scene'], time_min=reference['oracle_ir']['query']['time_min'],
                gold=expected['answer_choice'],
                predicate_changes=source_no_do(reference)['answer_choice'] != expected['answer_choice'])
            scored = dict(**base, arm=arm, route=result['route'], **grade(result['answer'], expected))
            if 'cropped_outside_window' in result:
                scored['cropped_outside_window']=result['cropped_outside_window']
                scored['inline_json_valid']=result['inline_json_valid']
            if arm != 'redo':
                faithful_schedule = faithful_query = False
                if result['route']=='executed':
                    _, obtained = expand_schedule(row['native_input'], result['plan'])
                    _, intended = expand_schedule(row['native_input'], reference['oracle_ir'])
                    faithful_schedule = all(abs(x-y)<=1e-10 for x,y in zip(obtained,intended))
                    faithful_query = result['plan']['query'] == reference['oracle_ir']['query']
                    factual = result['execution']['factual_trajectory']
                    ablated = project_trajectory(factual, factual, result['plan']['query'])
                    ablation_route = 'executed_no_do'
                    executions.append(dict(method=method,item_id=iid,arm=arm,
                        plan=result['plan'],tool_fields=result.get('tool_fields'),
                        cropped_outside_window=result.get('cropped_outside_window',[]), **result['execution']))
                else:
                    ablated, ablation_route = result['inline'], 'inline_fallback'
                    scored['reason'] = result.get('reason')
                scored.update(schedule_faithful=faithful_schedule, query_faithful=faithful_query,
                    fully_faithful=faithful_schedule and faithful_query)
                records.append(dict(**base, arm=arm+'_inline', route='inline', **grade(result['inline'], expected)))
                records.append(dict(**base, arm=arm+'_no_do', route=ablation_route, **grade(ablated, expected)))
            records.append(scored)
            if arm=='redo':
                records.append(dict(**base, arm='source_no_do', route='source_model_control',
                    **grade(source_no_do(reference), expected)))
            if index % 24 == 0:
                print(json.dumps(dict(method=method, analyzed=index+1, total=len(raw))), flush=True)
        costs.append(dict(method=method,calls=len(new_raw),reused_calls=len(raw)-len(new_raw),
            input_tokens=sum(r['prompt_tokens'] for r in new_raw), output_tokens=sum(r['completion_tokens'] for r in new_raw),
            length_stops=sum(r['finish_reason']=='length' for r in new_raw),
            worker_seconds=runtime['elapsed_seconds'],initialization_seconds=runtime['initialization_seconds']))
    lookup = {(r['method'],r['item_id'],r['arm']):r for r in records}
    comparisons = []
    for method in ('M4','M5'):
        for left,right in [('patch','redo'),('patch','full'),('patch','patch_inline'),('full','full_inline'),('patch','patch_no_do')]:
            a,b = [[lookup[method,i,arm] for i in inputs] for arm in (left,right)]
            comparisons.append(dict(method=method, candidate=left, control=right,
                repairs=sum(x['correct'] and not y['correct'] for x,y in zip(a,b)),
                harms=sum(not x['correct'] and y['correct'] for x,y in zip(a,b)),
                numeric_repairs=sum(x['joint_numeric_correct'] and not y['joint_numeric_correct'] for x,y in zip(a,b)),
                numeric_harms=sum(not x['joint_numeric_correct'] and y['joint_numeric_correct'] for x,y in zip(a,b))))
    write(directory / 'scored.jsonl', records)
    write(directory / 'executions.jsonl', executions)
    dump(directory / 'summary.json', dict(status='complete', split=split,
        results=summarize(records), comparisons=comparisons, costs=costs,
        new_calls=sum(c['calls'] for c in costs), cached_callbacks=replays,
        numeric_tolerance_mg_dL=NUMERIC_TOLERANCE,
        label_counts=dict(Counter(e['gold'] for e in evaluation.values())),
        constant_yes_correct=sum(e['gold']=='yes' for e in evaluation.values()),
        constant_no_correct=sum(e['gold']=='no' for e in evaluation.values())))
    dump(directory / 'replay.json', dict(exact_requests=replays,cached_callbacks=replays,new_calls=0))
    print(json.dumps(dict(results=summarize(records),comparisons=comparisons),indent=2),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','run','analyze'))
    parser.add_argument('--split',choices=('dev','heldout'),required=True)
    parser.add_argument('--method',choices=('M4','M5'))
    parser.add_argument('--gpu',type=int)
    parser.add_argument('--version',choices=('v1','v2'),default='v1')
    args=parser.parse_args()
    reused_redo=None
    if args.version=='v2':
        import head_v2
        ARMS,SCHEMAS,check,optimize,request=head_v2.ARMS,head_v2.SCHEMAS,head_v2.check,head_v2.optimize,head_v2.request
        if args.split=='heldout':
            ARMS=('redo','full','patch')
        reused_redo=OUT/'dev' if args.split=='dev' else None
        OUT=OUT/'v2'
    if args.action=='prepare':
        prepare(args.split,reused_redo)
    elif args.action=='run':
        runner.OUT=OUT/args.split
        runner.run_model(args.method,args.gpu,'matched',list(ARMS))
    else:
        analyze(args.split,reused_redo)
