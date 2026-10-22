"""Frozen R3 development40 distribution probe; no gold is read by the GPU runner."""
import argparse
import json
import math
import os
import shutil
import sys
import time

from r3_audit import HERE, PACK, read, write, dump
from r3_catalog_distribution_head import CODES, orders, request, aggregate, check

EXTRA_SITE = '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages'
BACKBONES = {'M0':'llama','M2':'llama','M3':'qwen','M4':'llama','M5':'qwen','M6':'llama','M7':'qwen'}


def render_request(req, tok, cfg):
    prompt = req['prompt'] if 'prompt' in req else tok.apply_chat_template(
        req['messages'], tokenize=False, add_generation_prompt=True, **cfg.get('chat_template_kwargs', {}))
    return prompt + '{"answer_choice": "'


def prepare(method, remaining=False):
    check()
    backbone = BACKBONES[method]
    assert not remaining or method in ('M4','M5')
    source = HERE / (f'r3_patient_selection_{method.lower()}_remaining' if remaining else f'r3_patient_focus_{backbone}')
    out = HERE / (f'r3_catalog_distribution_{method.lower()}' + ('_remaining' if remaining else ''))
    assert not out.exists()
    rows = [r for r in read(source/'inputs.jsonl') if r.get('method', method) == method]
    n = 88 if remaining else 40
    assert len(rows) == len({r['item']['item_id'] for r in rows}) == n
    if remaining:
        prior_rows = list(read(HERE/f'r3_catalog_distribution_{method.lower()}/inputs.jsonl'))
        assert not {r['item']['item_id'] for r in rows} & {r['item']['item_id'] for r in prior_rows}
        assert all([m['role'] for m in r['messages']] == ['system','user'] and r['messages'][0] == prior_rows[0]['messages'][0] for r in rows)
    catalog = json.loads((source/'catalog.json').read_text())
    assert len(catalog) == 49
    permutations = orders(catalog)
    cfg = json.loads((source/'config.json').read_text())
    cfg.update(max_tokens=1, max_logprobs=2048, guided_json=False)
    sys.path.insert(0, EXTRA_SITE)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(cfg['model'], local_files_only=True)
    token_ids = {c: tok.encode(c, add_special_tokens=False) for c in CODES[:len(catalog)]}
    assert all(len(v) == 1 for v in token_ids.values())
    token_ids = {c: v[0] for c, v in token_ids.items()}
    assert len(set(token_ids.values())) == 49
    jobs = []
    for row in rows:
        context = row.get('original_prompt') or row['messages']
        for index, names in enumerate(permutations):
            req = request(row['item'], context, names)
            if isinstance(context,str):
                tail = '<|start_header_id|>assistant<|end_header_id|>\n\n'
                assert req['prompt'].startswith(context[:-len(tail)])
            else:
                assert req['messages'][:-1] == context
            prompt = render_request(req, tok, cfg)
            jobs.append(dict(item_id=row['item']['item_id'], order=index, prompt=prompt))
    lengths = [len(tok.encode(r['prompt'], add_special_tokens=False)) for r in jobs]
    assert max(lengths)+1 <= cfg['max_model_len']
    out.mkdir()
    write(out/'inputs.jsonl', rows); write(out/'requests.jsonl', jobs)
    dump(out/'catalog.json', catalog); dump(out/'orders.json', permutations)
    dump(out/'config.json', cfg); dump(out/'token_ids.json', token_ids)
    ids = {r['item']['item_id'] for r in rows}
    write(out/'evaluation.jsonl', [r for r in read(source/'evaluation.jsonl') if r['item_id'] in ids])
    write(out/'baseline_scored.jsonl', [r for r in read(source/'baseline_scored.jsonl') if r.get('method',method) == method])
    write(out/'v1_scored.jsonl', [r for r in read(source/'scored.jsonl') if r.get('method',method) == method and r['variant'] == 'repeat_patient'])
    for name in ('r3_catalog_distribution_head.py', 'r3_catalog_distribution_pilot.py', 'r3_ontology_head.py'):
        shutil.copyfile(HERE/name, out/name)
    dump(out/'plan.json', dict(status='prepared', method=method, cases=n, distributions=len(jobs),
         scope=f'Exposed R3 diagnosis development{n}; not independent validation.',
         model=cfg['model'], max_prompt_tokens=max(lengths),
         variants=['order0', 'mean_probability', 'majority_vote'],
         permutations='Public sorted order + 5 global shuffles from Random(20260916), shared across methods; never selected using gold.',
         inference='Original native context plus exact current-patient repetition; direct code prompt, JSON answer prefix, one-token raw logprobs.',
         coverage='Top2048 raw token logprobs, then force any missing catalog codes in identical prompts. No probability floor or omitted candidate.',
         aggregation='Normalize each complete49 vector; equally average six distributions; majority tie-break by mean probability then original catalog order.',
         controls='Same order0 scoring is the matched single-call control. Existing v1/name/code results are separate controls with differing output/reasoning protocols.',
         criterion=('Frozen calibrated six-order majority transfer to another original method; same40 exposed cases, compare with uncalibrated majority and old v1, no method-specific policy selection.' if method not in ('M4','M5') else 'Fixed calibrated six-order majority selected on first40; compare with uncalibrated majority and v1 on other88. Reuse frozen18 content-free distributions per model; no coefficient, permutation or prompt changes.' if remaining else 'Require cross-backbone gain over matched order0 and credible behavior versus frozen v1 before expansion; no best-order selection.'),
         resources='Public49 disease names only. No new retrieval, training patients, or label input. No model weight changes.'))
    print('Prepared', out, len(jobs), 'distributions, max tokens', max(lengths))


def run(method, gpu, out=None):
    assert os.environ['CUDA_VISIBLE_DEVICES'] == str(gpu)
    out = out or HERE / f'r3_catalog_distribution_{method.lower()}'
    assert not (out/'raw_calls.jsonl').exists()
    cfg = json.loads((out/'config.json').read_text())
    jobs = list(read(out/'requests.jsonl'))
    token_ids = json.loads((out/'token_ids.json').read_text())
    sys.path.insert(0, EXTRA_SITE)
    from vllm import LLM, SamplingParams
    start = time.time()
    status = dict(status='loading', method=method, gpu=gpu, pid=os.getpid(), started_at=start, completed_calls=0)
    dump(out/'runtime.json', status)
    llm = LLM(model=cfg['model'], seed=cfg['seed'],
              **{k: cfg[k] for k in ('dtype','gpu_memory_utilization','max_model_len','max_num_seqs','max_num_batched_tokens','max_logprobs')},
              **cfg.get('model_kwargs', {}), enable_prefix_caching=True, enable_chunked_prefill=True, enforce_eager=True)
    status['initialization_seconds'] = time.time()-start
    def generate(batch, forced=False):
        params = [SamplingParams(temperature=0, seed=cfg['seed'], max_tokens=1,
                  logprobs=0 if forced else cfg['max_logprobs'],
                  allowed_token_ids=[token_ids[j['code']]] if forced else [token_ids[c] for c in j.get('codes', token_ids)]) for j in batch]
        before = time.time()
        outputs = llm.generate([j['prompt'] for j in batch], params, use_tqdm=False)
        elapsed = time.time()-before
        records = []
        for job, output in zip(batch, outputs):
            answer = output.outputs[0]
            assert len(answer.token_ids) == 1 and answer.token_ids[0] in [token_ids[c] for c in job.get('codes', token_ids)]
            if forced:
                assert answer.token_ids == [token_ids[job['code']]]
            available = answer.logprobs[0]
            scores = {c: available[token_ids[c]].logprob for c in job.get('codes', token_ids) if token_ids[c] in available}
            assert scores and all(math.isfinite(v) for v in scores.values())
            records.append(dict(item_id=job['item_id'], order=job['order'], forced_code=job.get('code'),
                    raw_response=answer.text, code_logprobs=scores, prompt_tokens=len(output.prompt_token_ids),
                    completion_tokens=1, finish_reason=answer.finish_reason, batch_seconds=elapsed))
        with (out/'raw_calls.jsonl').open('a') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False)+'\n')
        status.update(status='running', completed_calls=status['completed_calls']+len(batch), elapsed_seconds=time.time()-start)
        dump(out/'runtime.json', status)
        print(json.dumps(status), flush=True)
        return records
    distributions, missing_jobs = [], []
    for pos in range(0, len(jobs), cfg['batch_size']):
        batch = jobs[pos:pos+cfg['batch_size']]
        for job, record in zip(batch, generate(batch)):
            distributions.append(record)
            missing_jobs.extend(dict(job, code=c) for c in job.get('codes', token_ids) if c not in record['code_logprobs'])
    lookup = {(r['item_id'],r['order']):r['code_logprobs'] for r in distributions}
    write(out/'missing_code_requests.jsonl', missing_jobs)
    for pos in range(0, len(missing_jobs), cfg['batch_size']):
        for record in generate(missing_jobs[pos:pos+cfg['batch_size']], True):
            c = record['forced_code']
            lookup[record['item_id'],record['order']][c] = record['code_logprobs'][c]
    assert all(set(r['code_logprobs']) == set(j.get('codes', token_ids)) for j,r in zip(jobs, distributions))
    assert min(v for r in distributions for v in r['code_logprobs'].values()) < -.01
    write(out/'distributions.jsonl', distributions)
    status.update(status='complete', distributions=len(distributions), missing_code_calls=len(missing_jobs), elapsed_seconds=time.time()-start)
    dump(out/'runtime.json', status)


def score_results(method, out=None, distributions='distributions.jsonl'):
    out = out or HERE / f'r3_catalog_distribution_{method.lower()}'
    sys.path.insert(0, str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score, norm
    catalog = json.loads((out/'catalog.json').read_text())
    permutations = json.loads((out/'orders.json').read_text())
    inputs = {r['item']['item_id']: r['item'] for r in read(out/'inputs.jsonl')}
    evaluation = {r['item_id']: r for r in read(out/'evaluation.jsonl')}
    base = {r['item_id']: r for r in read(out/'baseline_scored.jsonl')}
    v1 = {r['item_id']: r for r in read(out/'v1_scored.jsonl')}
    canonical = {norm(x):x for x in json.loads((PACK/'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    raw = list(read(out/distributions))
    lookup = {(r['item_id'],r['order']):r['code_logprobs'] for r in raw}
    assert len(raw) == len(lookup) == len(inputs)*6
    scored, predictions = [], []
    for iid, item in inputs.items():
        result = aggregate(catalog, permutations, [lookup[iid,k] for k in range(6)])
        predictions.append(dict(item_id=iid, **result))
        variants = {f'order{k}':a for k,a in enumerate(result['per_order'])}
        variants.update({k:result[k] for k in ('mean_probability','majority_vote')})
        for variant, answer in variants.items():
            metric = score(dict(raw_response=json.dumps(dict(answer=answer))), evaluation[iid], item, canonical)
            scored.append(dict(item_id=iid, method=method, variant=variant, answer=answer, **metric))
    control = {r['item_id']:r for r in scored if r['variant'] == 'order0'}
    summary = []
    for variant in variants:
        rs = [r for r in scored if r['variant'] == variant]
        classes = sorted({str(evaluation[r['item_id']]['gold']) for r in rs})
        by_class = {c:[r for r in rs if str(evaluation[r['item_id']]['gold']) == c] for c in classes}
        summary.append(dict(variant=variant, n=len(rs), correct=sum(r['correct'] for r in rs),
            macro_recall=sum(sum(r['correct'] for r in group)/len(group) for group in by_class.values())/len(classes),
            class_results={c:dict(n=len(group), correct=sum(r['correct'] for r in group)) for c,group in by_class.items()},
            vs_order0=dict(repairs=sum(r['correct'] and not control[r['item_id']]['correct'] for r in rs),
                           harms=sum(not r['correct'] and control[r['item_id']]['correct'] for r in rs)),
            vs_v1=dict(repairs=sum(r['correct'] and not v1[r['item_id']]['correct'] for r in rs),
                       harms=sum(not r['correct'] and v1[r['item_id']]['correct'] for r in rs))))
    calls = list(read(out/'raw_calls.jsonl'))
    cost = dict(calls=len(calls), input_tokens=sum(r['prompt_tokens'] for r in calls), output_tokens=len(calls))
    write(out/'scored.jsonl', scored); write(out/'predictions.jsonl', predictions)
    result = dict(status='complete_development', method=method, results=summary, costs=cost,
         original_correct=sum(r['correct'] for r in base.values()), v1_correct=sum(r['correct'] for r in v1.values()),
         changed_by_permutation=sum(len(set(r['per_order'])) > 1 for r in predictions),
         runtime=json.loads((out/'runtime.json').read_text()))
    dump(out/'summary.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'results'}, indent=2))
    print([(r['variant'],r['correct'],r['macro_recall']) for r in summary])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare','run','score','check'))
    p.add_argument('--method', choices=BACKBONES); p.add_argument('--gpu', type=int)
    p.add_argument('--remaining', action='store_true')
    args = p.parse_args()
    out = HERE / (f'r3_catalog_distribution_{args.method.lower()}' + ('_remaining' if args.remaining else '')) if args.method else None
    if args.action == 'prepare': prepare(args.method, args.remaining)
    elif args.action == 'run': run(args.method, args.gpu, out)
    elif args.action == 'score': score_results(args.method, out)
    else: check()
