"""M4 + independent support audit: only the 79 frozen R2 target inputs."""
import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import time

from r2_support_pilot import HERE, M4, PACK, read, write, dump
from r2_support_interface import build_request, resolve

OUT = HERE / 'r2_interface_pilot'
METHODS = ['option_review', 'audit_recommend', 'audit_model', 'audit_execute']


def prepare():
    assert not OUT.exists(), 'Preserve previous experiment packages.'
    original = HERE / 'r2_support_pilot'
    evaluations = [r for r in read(original / 'evaluation.jsonl') if r['role'] != 'reference' and 'R2' in r['evaluation_labels']]
    wanted = {r['item_id'] for r in evaluations}
    base = {r['item_id']: r for r in read(original / 'baseline.jsonl') if r['item_id'] in wanted}
    inputs, requests = [], []
    for row in read(original / 'inputs.jsonl'):
        item = row['item']
        if item['item_id'] not in wanted:
            continue
        assert not item['fixed_evidence']
        block = row['messages'][-1]['content'].split('\n\nHere is the question:\n')[0]
        docs = re.findall(r'Document \[\d+\] (.*?)(?=\nDocument \[\d+\] |\Z)', block, re.S)
        assert len(docs) == 8 and item['question'] not in block
        data = dict(item=item, documents=docs, initial_response=base[item['item_id']]['raw_response'])
        inputs.append(data)
        for review in ['option', 'support']:
            requests.append(dict(item_id=item['item_id'], review=review, **build_request(**data, review=review)))
    assert len(wanted) == len(evaluations) == len(inputs) == len(base) == 79
    OUT.mkdir()
    write(OUT / 'inputs.jsonl', inputs)
    write(OUT / 'requests.jsonl', requests)
    write(OUT / 'evaluation.jsonl', evaluations)
    write(OUT / 'baseline.jsonl', list(base.values()))
    write(OUT / 'baseline_scored.jsonl', [r for r in read(original / 'baseline_scored.jsonl') if r['record_id'] in {e['record_id'] for e in evaluations}])
    dump(OUT / 'config.json', dict(model='/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct', dtype='bfloat16',
         seed=42, temperature=.7, top_p=1., top_k=-1, max_tokens=4096, gpu_memory_utilization=.60,
         max_model_len=131072, max_num_seqs=16, max_num_batched_tokens=8192, batch_size=16))
    dump(OUT / 'plan.json', dict(status='prepared', prepared_at=datetime.now().astimezone().isoformat(),
         original_method='M4 structured full v5', target_inputs=79, medpic_inputs=75, m14_inputs=4,
         new_calls=158, calls_per_candidate_per_input=1, methods=['baseline', *METHODS],
         labels_and_gold_used_only_in_preparation_and_scoring=True,
         note='audit_recommend, audit_model and audit_execute reuse the SAME support generation.'))
    for name in ['r2_support_interface.py', 'r2_interface_pilot.py', 'check_r2_support_interface.py']:
        (OUT / name).write_text((HERE / name).read_text())
    dump(OUT / 'example_request_input.json', inputs[0])
    print(f'Prepared {len(inputs)} R2 inputs, {len(requests)} fresh calls.')


def run(gpu, output_dir=OUT):
    assert os.environ['CUDA_VISIBLE_DEVICES'] == str(gpu)
    cfg = json.loads((output_dir / 'config.json').read_text())
    inputs = read(output_dir / 'inputs.jsonl')
    ids = {r['item']['item_id'] for i, r in enumerate(inputs) if i % cfg.get('num_shards',4) == (0 if cfg.get('num_shards',4)==1 else gpu)}
    jobs = [r for r in read(output_dir / 'requests.jsonl') if r['item_id'] in ids]
    folder = output_dir / f'gpu{gpu}'
    folder.mkdir()
    sys.path.insert(0, '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams
    started = time.time()
    status = dict(status='loading', gpu=gpu, pid=os.getpid(), started_at=started, total=len(jobs))
    dump(folder / 'runtime.json', status)
    model = LLM(model=cfg['model'], seed=cfg['seed'],
                **{k: cfg[k] for k in ['dtype', 'gpu_memory_utilization', 'max_model_len', 'max_num_seqs', 'max_num_batched_tokens']},
                **cfg.get('model_kwargs', {}),
                enable_prefix_caching=True, enable_chunked_prefill=True, guided_decoding_backend='xgrammar')
    tok = model.get_tokenizer()
    status['initialization_seconds'] = time.time()-started
    for pos in range(0, len(jobs), cfg['batch_size']):
        chunk = jobs[pos:pos+cfg['batch_size']]
        prompts = [tok.apply_chat_template(r['messages'], tokenize=False, add_generation_prompt=True,
                   **cfg.get('chat_template_kwargs', {})) for r in chunk]
        lengths = [len(tok.encode(p, add_special_tokens=False)) for p in prompts]
        assert max(lengths) + cfg['max_tokens'] <= cfg['max_model_len']
        params = [SamplingParams(**{k: cfg[k] for k in ['seed', 'temperature', 'top_p', 'top_k', 'max_tokens']},
                  guided_decoding=GuidedDecodingParams(json=r['schema'], backend='xgrammar') if cfg.get('guided_json', True) else None) for r in chunk]
        before = time.time()
        outputs = model.generate(prompts, params, use_tqdm=False)
        elapsed = time.time()-before
        with (folder / 'predictions.jsonl').open('a') as stream:
            for row, result in zip(chunk, outputs):
                answer = result.outputs[0]
                stream.write(json.dumps(dict(item_id=row['item_id'], review=row['review'], raw_response=answer.text,
                    prompt_tokens=len(result.prompt_token_ids), completion_tokens=len(answer.token_ids),
                    finish_reason=answer.finish_reason, batch_seconds=elapsed, batch_size=len(chunk), time=time.time()))+'\n')
        status.update(status='running', completed=pos+len(chunk), elapsed_seconds=time.time()-started, last_batch_seconds=elapsed)
        dump(folder / 'runtime.json', status)
        print(json.dumps(status), flush=True)
    status.update(status='complete', completed_at=time.time())
    dump(folder / 'runtime.json', status)


def score_results():
    os.environ['CF_SCREENING_OUTPUT'] = 'results_cf_full_comparison'
    sys.path.insert(0, str(PACK / 'scripts'))
    from analyze_cf_baseline_screening import score
    from analyze_v5 import objects
    inputs = {r['item']['item_id']: r for r in read(OUT / 'inputs.jsonl')}
    evaluations = read(OUT / 'evaluation.jsonl')
    raw = [r for gpu in range(4) for r in read(OUT / f'gpu{gpu}/predictions.jsonl')]
    lookup = {(r['item_id'], r['review']): r for r in raw}
    assert len(raw) == len(lookup) == 158
    assert set(lookup) == {(iid, review) for iid in inputs for review in ['option', 'support']}
    write(OUT / 'raw_predictions.jsonl', raw)
    baseline = {r['record_id']: r for r in read(OUT / 'baseline_scored.jsonl')}
    base_predictions = {r['item_id']: r for r in read(OUT / 'baseline.jsonl')}
    scored, resolved = [], []
    for e in evaluations:
        data = inputs[e['item_id']]
        item = data['item']
        obj = objects(base_predictions[e['item_id']]['raw_response'], 'answer_choice')
        old = score(dict(raw_response=json.dumps({'answer': obj['answer_choice']}) if obj else ''), e, item, {})
        assert all(old[k] == baseline[e['record_id']][k] for k in ['correct', 'invalid', 'invalid_reason'])
        scored.append(dict(baseline[e['record_id']], method='baseline'))
        for method in METHODS:
            r = lookup[e['item_id'], 'option' if method == 'option_review' else 'support']
            execution = 'recommend' if method in ['option_review', 'audit_recommend'] else method.split('_')[1]
            try:
                audit = json.loads(r['raw_response'])
                answer = resolve(item, data['documents'], audit, execution)
                native = json.dumps({'answer': answer['answer']})
                error = None
            except (ValueError, KeyError, TypeError, IndexError) as exc:
                answer, native, error = None, '', f'{type(exc).__name__}: {exc}'
            resolved.append(dict(item_id=e['item_id'], method=method, result=answer, error=error))
            result = score(dict(raw_response=native), e, item, {})
            scored.append(dict(e, method=method, **result))
    write(OUT / 'resolved.jsonl', resolved)
    write(OUT / 'scored.jsonl', scored)
    summaries = []
    for method in ['baseline', *METHODS]:
        for scope in ['R2_all', 'R2_none', 'R2_remaining', 'M14']:
            rs = []
            for r in scored:
                mp = r['resource_id'] == 'M02'
                none = mp and any(inputs[r['item_id']]['item']['options'][k].lower() == 'none of the above' for k in r['gold'])
                if r['method'] == method and {'R2_all': True, 'R2_none': none, 'R2_remaining': mp and not none, 'M14': not mp}[scope]:
                    rs.append(r)
            summaries.append(dict(method=method, scope=scope, n=len(rs), correct=sum(r['correct'] for r in rs),
                 accuracy_pct=100*sum(r['correct'] for r in rs)/len(rs), invalid=sum(r['invalid'] for r in rs),
                 repairs=sum(r['correct'] and not baseline[r['record_id']]['correct'] for r in rs),
                 harms=sum(not r['correct'] and baseline[r['record_id']]['correct'] for r in rs)))
    costs = [dict(review=review, calls=len(rs), input_tokens=sum(r['prompt_tokens'] for r in rs),
             output_tokens=sum(r['completion_tokens'] for r in rs), length_stops=sum(r['finish_reason']=='length' for r in rs))
             for review in ['option', 'support'] for rs in [[r for r in raw if r['review'] == review]]]
    mechanisms = []
    model_results = {r['item_id']: r for r in resolved if r['method'] == 'audit_model'}
    for r in resolved:
        if r['method'] != 'audit_execute' or r['result'] is None:
            continue
        result = r['result']
        checks = [c for o in result['options'].values() for p in o['paths'] for c in p['checks']]
        changed = [c for c in checks if c['basis'] == 'executed_comparison' and c['state'] != c['condition']['model_state']]
        model_result = model_results[r['item_id']]['result']
        mechanisms.append(dict(item_id=r['item_id'], conditions=len(checks), bases=dict(Counter(c['basis'] for c in checks)),
            comparison_disagreements=changed, answer_changed_from_model=bool(model_result and model_result['answer'] != result['answer']),
            provisional_options=[k for k, v in result['options'].items() if v['used_provisional']]))
    write(OUT / 'mechanism_cases.jsonl', mechanisms)
    dump(OUT / 'summary.json', dict(status='complete', results=summaries, costs=costs, baseline_parity=79,
        runtime=[json.loads((OUT / f'gpu{i}/runtime.json').read_text()) for i in range(4)],
        mechanism=dict(successful_audits=len(mechanisms), conditions=sum(r['conditions'] for r in mechanisms),
                       comparison_disagreements=sum(len(r['comparison_disagreements']) for r in mechanisms),
                       answers_changed_by_execution=sum(r['answer_changed_from_model'] for r in mechanisms))))
    lines = ['# M4 + R2 independent support audit', '', 'Only 79 frozen R2 targets. One seed (42). Existing baseline, 158 fresh calls.', '',
             '| Scope | Condition | Correct / n | Accuracy | Repairs / harms | Invalid |', '|---|---|---:|---:|---:|---:|']
    lines += [f"| {r['scope']} | {r['method']} | {r['correct']}/{r['n']} | {r['accuracy_pct']:.2f}% | {r['repairs']}/{r['harms']} | {r['invalid']} |" for r in summaries]
    (OUT / 'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'score'])
    parser.add_argument('--gpu', type=int, choices=range(4))
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'run':
        run(args.gpu)
    else:
        score_results()
