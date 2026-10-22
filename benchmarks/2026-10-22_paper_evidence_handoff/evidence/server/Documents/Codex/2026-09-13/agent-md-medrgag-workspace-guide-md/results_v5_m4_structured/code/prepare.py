"""Apply the accepted M4 prompt/schema repair to all archived formal inputs."""
import gzip
import json
import random
from collections import Counter
from datetime import datetime
from prepare_v5 import OUT, SOURCE, read, dump
from m4_format_pilot import instruction
from m4_output_schema import output_schema


def main():
    assert not (OUT / 'plan.json').exists()
    items = read(OUT / 'items.jsonl')
    by_id = {i['item_id']: i for i in items}
    assert len(items) == len(by_id) == 13905
    assert len(read(OUT / 'evaluation.jsonl')) == 15616
    random.Random(20260913).shuffle(items)
    assignment, jobs, handles = {}, [], {}
    for start in range(0, len(items), 128):
        name = f'm4_{start // 128:03d}'
        chunk = items[start:start + 128]
        jobs.append(dict(name=name, state='queued', n=len(chunk)))
        handles[name] = (OUT / 'inputs' / (name + '.jsonl')).open('w')
        for item in chunk:
            assignment[item['item_id']] = name
    seen = set()
    try:
        with gzip.open(SOURCE / 'M4/prompts.jsonl.gz', 'rt') as f:
            for line in f:
                archived = json.loads(line)
                iid = archived['item_id']
                assert iid not in seen
                seen.add(iid)
                item = by_id[iid]
                assert archived['retrieval_question'] == item['question']
                messages = [dict(m) for m in archived['messages']]
                extra = instruction(item)
                messages[0]['content'] += '\n\n' + extra
                messages[-1]['content'] += '\n\n' + extra
                assert all(e in messages[-1]['content'] for e in item['fixed_evidence'])
                schema = output_schema(item)
                row = dict(item=item, messages=messages, schema=schema,
                           context_truncated_tokens=archived['context_truncated_tokens'])
                handles[assignment[iid]].write(json.dumps(row, ensure_ascii=False) + '\n')
    finally:
        for f in handles.values():
            f.close()
    assert seen == set(by_id)
    for job in jobs:
        assert len(read(OUT / 'inputs' / (job['name'] + '.jsonl'))) == job['n']
        dump(OUT / 'jobs' / (job['name'] + '.json'), job)
    base = json.loads((SOURCE / 'M4/config.json').read_text())
    config = dict(base=base, repair='explicit output contract + visible-input JSON Schema/xgrammar',
                  gpu_memory_utilization=.90, max_num_seqs=128, max_num_batched_tokens=16384,
                  batch_size=128, max_model_len=131072, enable_prefix_caching=True,
                  enable_chunked_prefill=True, guided_decoding_backend='xgrammar',
                  prompt_source=str(SOURCE / 'M4/prompts.jsonl.gz'),
                  retrieval_policy='reuse exact archived evidence; no new retrieval',
                  prediction_reuse=0, generation_budget=2048, seed=42)
    dump(OUT / 'config.json', config)
    pilot_ids = [i['item_id'] for i in read(SOURCE / 'old_m4_pilot/items.jsonl')]
    plan = dict(prepared_at=datetime.now().astimezone().isoformat(), total=13905,
                native_records=15616, unique_units=6104, selected_judgments=13000,
                fresh_inputs=13905, reused_predictions=0, gpu_ids=[1, 2, 3], jobs=jobs,
                prior_selection_pilot_ids=pilot_ids, prior_selection_pilot_size=100,
                formats=dict(Counter(i['answer_format'] for i in items)),
                source=str(SOURCE), exact_archived_input_coverage=True)
    dump(OUT / 'plan.json', plan)
    print(json.dumps({k: v for k, v in plan.items() if k not in ('jobs', 'prior_selection_pilot_ids')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
