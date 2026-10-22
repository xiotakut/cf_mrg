"""Offline execution audit and costs from actual stage receipts, without gold."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from common import ROOT, atomic, digest, file_hash, read, visible, question_text
from methods import history_text, messages, IMED_SYSTEM, ASK, FINAL, TC_SYSTEM, state_signal


def quantiles(values):
    if not values:
        return None
    values = sorted(values)
    def at(q):
        x = (len(values) - 1) * q
        lo = int(x)
        return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (x - lo)
    return dict(min=values[0], p50=at(.5), p90=at(.9), p95=at(.95), max=values[-1], mean=mean(values))


def trace_audit(item, result, events, requests, config):
    """Compare real prompts with permitted input + the actual active history."""
    llm = {r['spec']['stage']: r for r in requests if r['spec']['kind'] == 'llm'}
    checks = Counter()
    for r in requests:
        if r['status'] != 'ok' or r['spec']['kind'] != 'llm':
            continue
        for output in r['result']:
            assert output['model']['model_id'] == config['model_id']
            assert output['model']['weight_id'] == config['weight_id']
            assert output['model']['tokenizer_id'] == config['tokenizer_id']
            assert output['prompt_tokens'] == len(output['prompt_token_ids'])
            checks['model_and_token_identity'] += 1
    if config['method'] == 'imedrag':
        history = []
        for e in events:
            if e['kind'] == 'imedrag_queries':
                assert e['history_before'] == history
                spec = llm[f'query/{e["round"]}']['spec']
                expected = messages(IMED_SYSTEM, history_text(history) + '\n\n' + question_text(item) + '\n\n' + ASK.format(config['n_queries']))
                assert spec['messages'] == [expected]
                assert e['actual'] == len(e['queries'])
                checks['query_history_and_required_evidence'] += 1
            elif e['kind'] == 'imedrag_qa':
                stage = f'qa/{e["round"]}/{e["query_index"]}'
                retrieval = next(x for x in events if x['kind'] == 'retrieval' and x['stage'] == stage)
                context = next(x for x in events if x['kind'] == 'retrieval_context' and x['stage'] == stage)
                assert retrieval['query'] == e['query']
                prompts = llm[stage]['spec']['messages']
                assert any(context['text'] in m[-1]['content'] and m[-1]['content'].endswith(e['query']) for m in prompts)
                history.append({k: e[k] for k in ('round', 'query_index', 'query', 'answer')})
                checks['actual_retrieval_and_ordered_qa'] += 1
            elif e['kind'] == 'imedrag_round':
                assert e['history_after'] == history
                assert e['executed'] == len(history) - len(e['history_before'])
                indices = [q['query_index'] for q in history if q['round'] == e['round']]
                assert indices == sorted(indices)
                checks['round_writeback'] += 1
            elif e['kind'] == 'imedrag_final':
                assert e['history'] == history
                expected = messages(IMED_SYSTEM, history_text(history) + '\n\n' + question_text(item) + '\n\n' + FINAL)
                assert llm['final']['spec']['messages'] == [expected]
                checks['final_qa_history_and_required_evidence'] += 1
    else:
        stack = [dict(kind='question', text=question_text(item), state=100000.0)]
        for e in events:
            if e['kind'] not in ('tc_action', 'tc_parse_failed'):
                continue
            assert e['stack_before'] == stack
            record = llm[f'action/{e["step"]}']
            prompt = '\n\n'.join(x['kind'].title() + ': ' + x['text'] for x in stack)
            assert record['spec']['messages'] == [messages(TC_SYSTEM, prompt)]
            checks['active_stack_prompt_and_required_evidence'] += 1
            if e['kind'] == 'tc_parse_failed':
                continue
            if e['state_signal']:
                assert state_signal(record['result'][0]) == e['state_signal']
                checks['entropy_recalculation_from_saved_full_signal'] += 1
            if e['removed']:
                assert e['removed'] == stack[-1:]
                if e['action'] == 'backtrack':
                    assert e['stack_after'] == stack[:-1]
                else:
                    assert e['action'] == 'summary'
                    assert e['stack_after'][:-1] == stack[:-1]
                    assert e['stack_after'][-1] == dict(kind='summary', text=e['content'], state=stack[-2]['state'])
                assert e['state_after'] == stack[-2]['state']
                checks['removed_memory_and_state_restore'] += 1
            if e['action'] == 'final answer':
                assert e['accepted'] == (e['step'] >= config['topK'] and e['state_signal']['value'] < config['sigma'])
                checks['acceptance_boundary'] += 1
            stack = e['stack_after']
            assert stack[0] == e['stack_before'][0]
        if result['termination'] == 'budget_exhausted':
            assert result['status'] == 'invalid' and result['raw_response'] == stack[-1]['text']
            assert result['steps'] == config['max_loop']
            checks['budget_not_promoted_to_answer'] += 1
    return checks


def report(root, inputs):
    config = json.loads((root / 'resolved_config.json').read_text())
    assert file_hash(inputs) == config['inputs_hash']
    items = {i['item_id']: i for i in read(inputs)}
    paths = sorted((root / 'items').glob('*/result.json'))
    records = [json.loads(p.read_text()) for p in paths]
    assert len(records) == len({r['item_id'] for r in records})
    assert {r['item_id'] for r in records} <= set(items)
    source_map = {r['inference_input_id']: r['source_ids'] for r in read(ROOT / 'data/input_manifest.jsonl')}
    source_map.update({r['item_id']: [r['source_id']] for r in read(ROOT / 'data/dev_provenance.jsonl')})
    rows, requests, checks, entropy_values = [], [], Counter(), []
    attempt_states = Counter()
    engine_batches, fresh_batches = {}, {}
    provenance_path = root / 'cache_provenance.json'
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else None
    reused_keys = {(r['item_id'], r['request_key']) for r in provenance['copied_requests']} if provenance else set()
    fresh_generations, reused_generations = [], []
    retrieval_receipts, fresh_retrievals = [], []
    for result, path in zip(records, paths):
        item = items[result['item_id']]
        assert result['input_hash'] == digest(visible(item))
        assert result['config_hash'] == digest(config)
        events = [json.loads(p.read_text()) for p in sorted((path.parent / 'events').glob('*.json'))]
        receipts = [json.loads(p.read_text()) for p in (path.parent / 'requests').glob('*.json')]
        for p in (path.parent / 'attempts').glob('*/*.json'):
            attempt_states[json.loads(p.read_text())['status']] += 1
        checks.update(trace_audit(item, result, events, receipts, config))
        requests += receipts
        actions = Counter(e['action'] for e in events if e['kind'] == 'tc_action')
        queries = [e for e in events if e['kind'] == 'imedrag_queries']
        states = [e['state_signal']['value'] for e in events if e['kind'] == 'tc_action' and e['state_signal']]
        entropy_values += states
        rows.append(dict(item_id=result['item_id'], source_ids=source_map[result['item_id']],
            status=result['status'], termination=result['termination'], seconds=result['seconds'],
            costs=result['costs'], rounds=len(queries), requested_queries=sum(e['requested'] for e in queries),
            generated_queries=sum(e['actual'] for e in queries),
            completed_qa=sum(e['kind'] == 'imedrag_qa' for e in events),
            answer_syntax_repairs=sum(e['kind'] == 'answer_syntax_repair' for e in events),
            query_parse_status=dict(Counter(e['parse_status'] for e in queries)), actions=dict(actions),
            backtracks=sum(e['action'] == 'backtrack' and bool(e['removed']) for e in events if e['kind'] == 'tc_action'),
            summaries=sum(e['action'] == 'summary' and bool(e['removed']) for e in events if e['kind'] == 'tc_action'),
            steps=sum(e['kind'] in ('tc_action', 'tc_parse_failed') for e in events), entropy=quantiles(states),
            required_evidence_documents=len(item['fixed_evidence']),
            truncated_documents=sum(bool(d['truncated_tokens']) for e in events if e['kind'] == 'retrieval_context' for d in e['documents']),
            error=result.get('error'), issues=result.get('issues', [])))
        for r in receipts:
            if r['status'] != 'ok':
                continue
            if r['spec']['kind'] == 'retrieval':
                retrieval_receipts.append(r['result'])
                if (result['item_id'], digest(r['spec'])) not in reused_keys:
                    fresh_retrievals.append(r['result'])
                continue
            for v in r['result']:
                key = v.get('engine_batch_id', digest(r['spec']))
                engine_batches[key] = dict(seconds=v.get('engine_batch_seconds', v['batch_seconds']),
                                            rows=v.get('engine_batch_size', v['batch_size']))
                if (result['item_id'], digest(r['spec'])) in reused_keys:
                    reused_generations.append(v)
                else:
                    fresh_generations.append(v)
                    fresh_batches[key] = engine_batches[key]
    statuses = Counter(r['status'] for r in records)
    coverage = dict(N_planned=len(items), N_ok=statuses['ok'], N_invalid=statuses['invalid'],
                    N_failed=statuses['failed'], N_pending=len(items) - len(records), duplicates=0, unknown_ids=0)
    complete = json.loads((root / 'complete.json').read_text()) if (root / 'complete.json').exists() else None
    def summarize(rs):
        n = len(rs)
        costs = {k: sum(r['costs'][k] for r in rs) for k in rs[0]['costs']} if n else {}
        return dict(N=n, terminal_counts=dict(Counter(r['status'] for r in rs)),
            termination_counts=dict(Counter(r['termination'] for r in rs)),
            valid_rate=sum(r['status'] == 'ok' for r in rs) / n if n else None,
            invalid_rate=sum(r['status'] == 'invalid' for r in rs) / n if n else None,
            failed_rate=sum(r['status'] == 'failed' for r in rs) / n if n else None,
            output_truncation_input_rate=sum(r['costs']['generated_truncations'] > 0 for r in rs) / n if n else None,
            budget_exhausted_rate=sum(r['termination'] == 'budget_exhausted' for r in rs) / n if n else None,
            costs=costs, latency_seconds=quantiles([r['seconds'] for r in rs]),
            rounds=quantiles([r['rounds'] for r in rs]), steps=quantiles([r['steps'] for r in rs]),
            retrievals=quantiles([r['costs']['retrieval_requests'] for r in rs]),
            generated_queries=sum(r['generated_queries'] for r in rs), completed_qa=sum(r['completed_qa'] for r in rs),
            answer_syntax_repairs=sum(r['answer_syntax_repairs'] for r in rs),
            backtracks=sum(r['backtracks'] for r in rs), summaries=sum(r['summaries'] for r in rs))
    result = dict(run_id=config['run_id'], method=config['method'], coverage=coverage,
        complete=bool(complete) and coverage['N_pending'] == 0,
        overall=summarize(rows), by_source={s: summarize([r for r in rows if s in r['source_ids']]) for s in sorted({s for r in rows for s in r['source_ids']})},
        checks=dict(checks), attempt_states=dict(attempt_states), entropy_values=quantiles(entropy_values),
        physical_engine_batches=len(engine_batches), engine_active_seconds=sum(b['seconds'] for b in engine_batches.values()),
        physical_batch_rows=quantiles([b['rows'] for b in engine_batches.values()]),
        wall_seconds=complete['seconds'] if complete else None,
        throughput_inputs_per_hour=len(items) * 3600 / complete['seconds'] if complete and not provenance else None,
        replay_throughput_inputs_per_hour=len(items) * 3600 / complete['seconds'] if complete and provenance else None,
        cache_provenance=str(provenance_path.resolve()) if provenance else None,
        timing_scope='Cached unchanged stages plus interface-fix recomputation; not cold method throughput.' if provenance else 'Complete method execution.',
        fresh_compute=dict(llm_requests=len(fresh_generations),
            prompt_tokens=sum(v['prompt_tokens'] for v in fresh_generations),
            completion_tokens=sum(v['completion_tokens'] for v in fresh_generations),
            engine_active_seconds=sum(b['seconds'] for b in fresh_batches.values()),
            retrieval_requests=len(fresh_retrievals),
            retrieval_backend_calls=sum(not r['cache_hit'] for r in fresh_retrievals),
            retrieval_cache_hits=sum(r['cache_hit'] for r in fresh_retrievals)),
        reused_llm_requests=len(reused_generations),
        logical_retrieval_cache_hits=sum(r['cache_hit'] for r in retrieval_receipts),
        extra_reference_requests=2 if (root / 'backend_reference.json').exists() else 0,
        scoring_forward_calls=0, protocol=config['evidence_protocol'],
        gold_read=False, cost_scope='Terminal input receipts; interrupted/in-flight pilot costs are reported separately. Shared engine batches deduplicated by ID; wall throughput is not divided again by workers.')
    atomic(root / 'execution_rows.jsonl', rows, lines=True)
    atomic(root / 'execution_report.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--run-dir', type=Path, required=True)
    p.add_argument('--inputs', type=Path, required=True)
    args = p.parse_args()
    result = report(args.run_dir, args.inputs)
    print(json.dumps({k: result[k] for k in ('run_id', 'coverage', 'checks', 'wall_seconds', 'throughput_inputs_per_hour')}, indent=2))
