import json
from collections import Counter
from common import read, digest, visible
from medgenie import context_messages, reader_messages, native_answer

def audit_run(run, items):
    checks, truncations = Counter(), Counter()
    cfg = json.loads((run/'resolved_config.json').read_text())
    for r in read(run/'predictions.jsonl'):
        item = items[r['item_id']]
        assert r['input_hash'] == digest(visible(item)) and r['config_hash'] == digest(cfg)
        checks['input_and_config_identity'] += 1
        records = [json.loads(p.read_text()) for p in (run/'items'/r['item_id']/'requests').glob('*.json')]
        if r['status']=='failed':
            checks['retained_runtime_failures'] += 1
            continue
        assert all(x['status']=='ok' for x in records)
        req = {x['spec']['stage']:x for x in records}
        prompts, views = context_messages(item)
        contexts = [x['text'].strip() for x in req['contexts']['result']]
        assert req['contexts']['spec']['messages'] == prompts and len(contexts)==5
        if 'reader' not in req:
            assert r['termination']=='incomplete_contexts' and any(not c for c in contexts)
            checks['incomplete_contexts'] += 1
            continue
        assert req['reader']['spec']['messages'] == [reader_messages(item,contexts)]
        assert r['context_views'] == views
        assert r['raw_response'] == native_answer(req['reader']['result'][0]['text'],item)
        checks['five_contexts_and_ordered_reader'] += 1
        checks['native_serializations'] += r['raw_response'] != r['model_raw_response']
        for stage,rec in req.items():
            spec=rec['spec']
            assert spec['max_tokens']==cfg['budgets'][stage]
            assert spec['sampling']==cfg['generator_sampling' if stage=='contexts' else 'reader_sampling']
            for out,msg in zip(rec['result'],spec['messages']):
                assert out['model']['model_id']==cfg['model_id']
                assert len(out['token_ids'])==out['completion_tokens']
                assert len(out['prompt_token_ids'])==out['prompt_tokens']
                assert out['completion_tokens']<=spec['max_tokens']
                assert all(m['content'] in out['prompt'] for m in msg)
                assert out['scoring_forward_calls']==0
                checks['actual_generation_prompt_model_tokens'] += 1
                truncations[stage] += out['finish_reason']=='length'
        assert r['costs']['llm_requests']==6 and r['costs']['retrieval_requests']==0
    return checks, truncations
