"""Project formal costs from measured execution and frozen input lengths."""
import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from common import ROOT, atomic, read, question_text
from report import quantiles


def pilot_cost(root):
    generations, attempts, engine = [], [], {}
    retrievals = 0
    provenance_path = root / 'cache_provenance.json'
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else None
    reused = {(r['item_id'], r['request_key']) for r in provenance['copied_requests']} if provenance else set()
    for p in (root / 'items').glob('*/requests/*.json'):
        if (p.parent.parent.name, p.stem) in reused:
            continue
        r = json.loads(p.read_text())
        if r['status'] != 'ok':
            continue
        if r['spec']['kind'] == 'llm':
            generations.extend(r['result'])
            first = r['result'][0]
            engine[first.get('engine_batch_id', str(p))] = first.get('engine_batch_seconds', first['batch_seconds'])
        else:
            retrievals += 1
    for p in (root / 'items').glob('*/attempts/*/*.json'):
        if (p.parent.parent.parent.name, p.parent.name) in reused:
            continue
        attempts.append(json.loads(p.read_text()))
    proof = json.loads((root / 'backend_reference.json').read_text()) if (root / 'backend_reference.json').exists() else None
    return dict(run_id=root.name, llm_requests_with_saved_output=len(generations),
        prompt_tokens=sum(g['prompt_tokens'] for g in generations),
        completion_tokens=sum(g['completion_tokens'] for g in generations),
        retrievals_with_receipts=retrievals, known_engine_seconds=sum(engine.values()),
        attempt_statuses=dict(Counter(a['status'] for a in attempts)),
        reference_requests=2 if proof else 0,
        reference_prompt_tokens=sum(proof[k]['prompt_tokens'] for k in ('reference', 'ordinary')) if proof else 0,
        reference_completion_tokens=sum(proof[k]['completion_tokens'] for k in ('reference', 'ordinary')) if proof else 0,
        reused_stage_requests_excluded=len(reused),
        limitation='Fresh compute only when prefix provenance exists. Lower bound: interrupted generations without a response have unknown token usage; failed/in-flight attempts remain saved.')


def estimate(roots):
    from transformers import AutoTokenizer
    by_method = {}
    for method in ('imedrag', 'tcrag'):
        selected = []
        for root in roots:
            cfg = json.loads((root / 'resolved_config.json').read_text())
            if cfg['method'] == method:
                selected.append((root, cfg))
        if not selected:
            continue
        tokenizer = AutoTokenizer.from_pretrained(selected[0][1]['model_path'], local_files_only=True)
        samples, total_wall, total_engine, timing_sources = [], 0., 0., []
        for root, cfg in selected:
            rep = json.loads((root / 'execution_report.json').read_text())
            assert rep['complete'], 'Incomplete acceptance runs cannot define final throughput.'
            timing = rep
            timing_root = root
            seen = set()
            while timing.get('cache_provenance'):
                assert timing_root.resolve() not in seen, 'Cyclic cache provenance.'
                seen.add(timing_root.resolve())
                provenance = json.loads(Path(timing['cache_provenance']).read_text())
                timing_root = Path(provenance['source_run'])
                timing = json.loads((timing_root / 'execution_report.json').read_text())
                assert timing['complete']
            timing_sources.append(str(timing_root))
            total_wall += timing['wall_seconds']
            total_engine += timing['engine_active_seconds']
            items = {i['item_id']: i for i in read(cfg['input_path'])}
            for row in read(root / 'execution_rows.jsonl'):
                prompt = tokenizer.apply_chat_template([dict(role='system', content='You are a helpful medical expert.'),
                    dict(role='user', content=question_text(items[row['item_id']]))],
                    tokenize=False, add_generation_prompt=True, **cfg['chat_template_kwargs'])
                row['mandatory_tokens'] = len(tokenizer.encode(prompt, add_special_tokens=False))
                row['run_id'] = root.name
                samples.append(row)
        formal = read(ROOT / 'reports' / (method + '_input_lengths.jsonl'))
        wall_factor = total_wall / total_engine
        strata = []
        for low, high in ((0, 1024), (1024, 8192), (8192, 131072)):
            planned = [i for i in formal if low < i['mandatory_tokens'] <= high]
            observed = [r for r in samples if low < r['mandatory_tokens'] <= high]
            seconds = [r['costs']['backend_seconds'] for r in observed]
            per_input = mean(seconds) * wall_factor if seconds else None
            strata.append(dict(mandatory_token_range=[low, high], planned=len(planned), observed=len(observed),
                failed_observations=sum(r['status'] == 'failed' for r in observed),
                measured_backend_seconds_per_input=quantiles(seconds),
                projected_attempt_wall_hours=len(planned) * per_input / 3600 if per_input is not None else None,
                projected_attempt_llm_requests=len(planned) * mean(r['costs']['llm_requests'] for r in observed) if observed else None,
                projected_attempt_prompt_tokens=len(planned) * mean(r['costs']['prompt_tokens'] for r in observed) if observed else None,
                projected_attempt_completion_tokens=len(planned) * mean(r['costs']['completion_tokens'] for r in observed) if observed else None,
                projected_attempt_retrievals=len(planned) * mean(r['costs']['retrieval_requests'] for r in observed) if observed else None))
        hours = [s['projected_attempt_wall_hours'] for s in strata if s['planned']]
        by_method[method] = dict(N_planned=len(formal), acceptance_runs=[str(r) for r, _ in selected],
            observed_inputs=len(samples), measured_wall_seconds=total_wall, measured_engine_seconds=total_engine,
            cold_timing_sources=timing_sources,
            measured_inputs_per_hour=len(samples) * 3600 / total_wall,
            wall_to_engine_factor=wall_factor, input_lengths=quantiles([r['mandatory_tokens'] for r in formal]),
            strata=strata, projected_attempt_wall_hours=sum(hours) if None not in hours else None,
            standard_full_call_scenario=dict(llm_requests=22 * len(formal), retrievals=12 * len(formal),
                assumption='Exactly 3 executed queries in each of 4 rounds, parser and formatter calls, no retry; not a hard maximum.') if method == 'imedrag'
                else dict(max_action_requests=8 * len(formal), min_accepted_action_requests=5 * len(formal),
                    assumption='8-step maximum, earliest acceptance on generation 5; transport retries extra.'),
            extra_scoring_forward_calls=0, physical_gpus=selected[0][1]['physical_gpu_selection'],
            forecast_interpretation='Observed attempts including failures, not guaranteed valid outputs. For interface-fix prefix replay, use cold source-run wall/engine ratio with the final version logical request costs; never use replay throughput as full-method throughput. No second division by concurrency. Unmeasured long/source inputs limit the estimate.')
    prefix_roots = set()
    for root in roots:
        while (root / 'cache_provenance.json').exists():
            source = Path(json.loads((root / 'cache_provenance.json').read_text())['source_run'])
            if source.resolve() in prefix_roots:
                break
            prefix_roots.add(source.resolve())
            root = source
    result = dict(methods=by_method,
        superseded_pilots=[pilot_cost(p) for p in sorted((ROOT / 'runs').glob('*')) if any(p.glob('superseded*.json'))],
        acceptance_fresh_compute=[pilot_cost(p) for p in roots],
        prefix_source_compute=[pilot_cost(p) for p in sorted(prefix_roots)],
        verification=[{k: v for k, v in pilot_cost(p).items() if k == 'run_id' or k.startswith('reference_')} for p in roots],
        formal_scope='Confirmed v5: 6104 units, 13000 selected judgments, 13905 unique inputs per method; all are still planned.',
        price='Local shared GPUs; no external API charge or invented currency price. Hours exclude model/index startup; all reference and pilot requests are listed separately.',
        formal_started=False)
    atomic(ROOT / 'reports/formal_cost_estimate.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--run-dirs', nargs='+', type=Path, required=True)
    args = p.parse_args()
    estimate(args.run_dirs)
