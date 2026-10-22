"""Content-free calibration of frozen full-catalog scores; fixed formula, no label fitting."""
import argparse
import json
import math
import shutil
import sys

from r3_audit import HERE, read, write, dump
from r3_catalog_distribution_head import request
from r3_catalog_distribution_pilot import EXTRA_SITE, run, score_results

CONTENTS = ['N/A', '[MASK]', '']


def log_prior(vectors):
    probabilities = []
    for vector in vectors:
        peak = max(vector.values())
        weights = {c:math.exp(v-peak) for c,v in vector.items()}
        total = sum(weights.values())
        probabilities.append({c:v/total for c,v in weights.items()})
    return {c:math.log(sum(p[c] for p in probabilities)/len(probabilities)) for c in vectors[0]}


def prepare(method):
    source = HERE / f'r3_catalog_distribution_{method.lower()}'
    out = HERE / f'r3_catalog_calibration_{method.lower()}'
    assert not out.exists()
    rows = list(read(source/'inputs.jsonl'))
    first = rows[0]['messages']
    assert [m['role'] for m in first] == ['system','user']
    assert all([m['role'] for m in r['messages']] == ['system','user'] and r['messages'][0] == first[0] for r in rows)
    cfg = json.loads((source/'config.json').read_text())
    permutations = json.loads((source/'orders.json').read_text())
    sys.path.insert(0, EXTRA_SITE)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(cfg['model'], local_files_only=True)
    jobs, priors = [], []
    for k, text in enumerate(CONTENTS):
        item = dict(answer_format='diagnosis', question=text)
        context = [first[0], dict(role='user', content=text)]
        priors.append(dict(item_id=f'content_free_{k}', item=item, messages=context))
        for index, names in enumerate(permutations):
            req = request(item, context, names)
            prompt = tok.apply_chat_template(req['messages'], tokenize=False, add_generation_prompt=True,
                                             **cfg.get('chat_template_kwargs',{})) + '{"answer_choice": "'
            jobs.append(dict(item_id=f'content_free_{k}', order=index, prompt=prompt))
    out.mkdir()
    for name in ('inputs.jsonl','config.json','catalog.json','orders.json','token_ids.json','evaluation.jsonl','baseline_scored.jsonl','v1_scored.jsonl'):
        shutil.copyfile(source/name, out/name)
    for name in ('r3_catalog_calibration.py','r3_catalog_distribution_pilot.py','r3_catalog_distribution_head.py','r3_ontology_head.py'):
        shutil.copyfile(HERE/name, out/name)
    write(out/'prior_inputs.jsonl', priors); write(out/'requests.jsonl', jobs)
    dump(out/'plan.json', dict(status='prepared', method=method, new_distributions=18,
        reuse=str(source/'distributions.jsonl'), reused_distributions=240,
        source='https://proceedings.mlr.press/v139/zhao21c/zhao21c.pdf',
        contents=CONTENTS, rule='For each order, average the three content-free conditional49 distributions; subtract log of this prior from full raw logprobs, normalize, then apply the same frozen six-order aggregation.',
        context='Original system and user-role layout preserved; all variable patient and retrieved content replaced by the content-free string, including repeated patient. No patient-specific calibration or gold.',
        primary='Calibrated six-order mean versus frozen uncalibrated six-order mean, across both backbones; no coefficient tuning or best-order selection.',
        scope='Exposed development40. Known contextual-calibration adaptation; not a demonstrated medical causal counterfactual mechanism.'))
    print('Prepared',out, len(jobs),'content-free distributions')


def score_calibrated(method):
    source = HERE / f'r3_catalog_distribution_{method.lower()}'
    out = HERE / f'r3_catalog_calibration_{method.lower()}'
    raw = list(read(out/'distributions.jsonl'))
    assert len(raw) == len({(r['item_id'],r['order']) for r in raw}) == 18
    priors = {k:log_prior([r['code_logprobs'] for r in raw if r['order']==k]) for k in range(6)}
    corrected = [dict(r, code_logprobs={c:v-priors[r['order']][c] for c,v in r['code_logprobs'].items()})
                 for r in read(source/'distributions.jsonl')]
    write(out/'calibrated_distributions.jsonl', corrected)
    dump(out/'log_priors.json', priors)
    score_results(method, out, 'calibrated_distributions.jsonl')
    summary = json.loads((out/'summary.json').read_text())
    control = {(r['item_id'],r['variant']):r for r in read(source/'scored.jsonl')}
    for result in summary['results']:
        rows = [r for r in read(out/'scored.jsonl') if r['variant']==result['variant']]
        result['vs_uncalibrated_same_variant'] = dict(
            repairs=sum(r['correct'] and not control[r['item_id'],r['variant']]['correct'] for r in rows),
            harms=sum(not r['correct'] and control[r['item_id'],r['variant']]['correct'] for r in rows))
    summary['reused_full_distributions'] = len(corrected)
    summary['control_summary'] = str(source/'summary.json')
    dump(out/'summary.json', summary)


if __name__ == '__main__':
    # Known 3:1 content-free prior turns a 3:1 full vector into a tie; no fitted coefficient.
    prior = log_prior([dict(A=math.log(.75), B=math.log(.25))]*3)
    assert abs(prior['A']-math.log(.75)) < 1e-12 and abs(prior['B']-math.log(.25)) < 1e-12
    assert abs((math.log(.75)-prior['A'])-(math.log(.25)-prior['B'])) < 1e-12
    p = argparse.ArgumentParser(); p.add_argument('action', choices=('prepare','run','score'))
    p.add_argument('--method', choices=('M4','M5'), required=True); p.add_argument('--gpu',type=int)
    args = p.parse_args()
    if args.action == 'prepare': prepare(args.method)
    elif args.action == 'run': run(args.method, args.gpu, HERE/f'r3_catalog_calibration_{args.method.lower()}')
    else: score_calibrated(args.method)
