"""Isolated prompt-only M4 experiment using frozen per-item retrieved evidence."""
import argparse
import gzip
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'm4_format_pilot'


def instruction(item):
    fmt = item['answer_format']
    example = {'step_by_step_thinking': 'Brief step-by-step explanation.', 'answer_choice': 'A'}
    if fmt in ('single', 'robustness_single'):
        example['answer_choice'] = next(iter(item['options']))
        contract = 'answer_choice must be exactly one of these option key strings: ' + json.dumps(list(item['options'])) + '. Do not append option text, punctuation, or explanation to the key.'
    elif fmt == 'multi':
        example['answer_choice'] = [next(iter(item['options']))]
        contract = 'answer_choice must be a nonempty JSON array of distinct option key strings from ' + json.dumps(list(item['options'])) + '. Use an actual array, not a string containing an array; do not include option text.'
    elif fmt == 'relation':
        example['answer_choice'] = 'uncertainty'
        contract = 'answer_choice must be exactly one of these strings: "higher", "lower", "no difference", "uncertainty".'
    else:
        example['answer_choice'] = '<diagnosis label>'
        contract = 'answer_choice must be a string containing one concise most likely diagnosis label, not a nested object, list, sentence, or explanation.'
    if fmt == 'robustness_single':
        example['errors'] = []
        contract += ' Also include the required errors array with document_id and correction strings; [] is only for when you identify no erroneous documents.'
    return ('Output contract (mandatory): Return exactly one valid JSON object, with no Markdown fences, headings, or text outside it. '
            'Keep your step-by-step reasoning inside the step_by_step_thinking string. Use double quotes for all JSON keys and strings. '
            'Inside strings, encode line breaks as \\n and escape any double quotes as \\"; never insert literal line breaks inside a quoted string. '
            + contract + ' The following is a syntax example only, NOT a suggested answer: ' + json.dumps(example))


def read(path):
    with path.open() as f:
        return [json.loads(line) for line in f]


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--structured', action='store_true')
    args = parser.parse_args()
    if args.structured:
        OUT = ROOT / 'm4_format_structured_pilot'
    OUT.mkdir(exist_ok=True)
    items = read(ROOT / 'old_m4_pilot/items.jsonl')
    wanted = {i['item_id'] for i in items}
    archived = {}
    with gzip.open(ROOT / 'M4/prompts.jsonl.gz', 'rt') as f:
        for line in f:
            row = json.loads(line)
            if row['item_id'] in wanted:
                assert row['item_id'] not in archived
                archived[row['item_id']] = row
    assert set(archived) == wanted and len(wanted) == 100
    inputs = []
    for item in items:
        original = archived[item['item_id']]['messages']
        messages = [dict(m) for m in original]
        extra = instruction(item)
        messages[0]['content'] += '\n\n' + extra
        messages[-1]['content'] += '\n\n' + extra
        assert messages[-1]['content'].startswith(original[-1]['content'])
        assert all(e in messages[-1]['content'] for e in item['fixed_evidence'])
        inputs.append(dict(item=item, messages=messages))
    if not (OUT / 'inputs.jsonl').exists():
        (OUT / 'inputs.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in inputs))
    else:
        assert read(OUT / 'inputs.jsonl') == inputs
    if args.prepare_only:
        print('100 paired inputs prepared; original messages and mandatory evidence preserved.')
        return
    # Match the original runner's Transformers dependency precedence.
    sys.path.insert(0, "/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages")
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams
    from m4_output_schema import output_schema
    config = json.loads((ROOT / 'M4/config.json').read_text())
    model = LLM(model=config['model_path'], dtype='bfloat16', max_model_len=131072,
                gpu_memory_utilization=.50, max_num_seqs=16, enable_prefix_caching=True, seed=42,
                guided_decoding_backend='xgrammar' if args.structured else 'auto')
    tok = model.get_tokenizer()
    completed = {r['item_id'] for r in read(OUT / 'predictions.jsonl')} if (OUT / 'predictions.jsonl').exists() else set()
    pending = [r for r in inputs if r['item']['item_id'] not in completed]
    params = SamplingParams(temperature=.7, top_p=1., top_k=-1, max_tokens=2048, seed=42)
    (OUT / 'config.json').write_text(json.dumps(dict(base=config, change='append explicit JSON/type contract to archived messages', gpu_memory=.50, max_num_seqs=16, constrained_decoding=args.structured), indent=2))
    for pos in range(0, len(pending), 16):
        chunk = pending[pos:pos+16]
        prompts = [tok.apply_chat_template(r['messages'], tokenize=False, add_generation_prompt=True) for r in chunk]
        assert all(len(tok.encode(p, add_special_tokens=False)) + 2048 <= 131072 for p in prompts)
        start = time.time()
        batch_params = [SamplingParams(temperature=.7, top_p=1., top_k=-1, max_tokens=2048, seed=42, guided_decoding=GuidedDecodingParams(json=output_schema(r['item']), backend='xgrammar')) for r in chunk] if args.structured else params
        outputs = model.generate(prompts, batch_params, use_tqdm=False)
        with (OUT / 'predictions.jsonl').open('a') as f:
            for row, output in zip(chunk, outputs):
                answer = output.outputs[0]
                result = dict(item_id=row['item']['item_id'], raw_response=answer.text,
                              completion_tokens=len(answer.token_ids), prompt_tokens=len(output.prompt_token_ids),
                              finish_reason=answer.finish_reason, time=time.time())
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
        print(json.dumps(dict(completed=len(completed)+pos+len(chunk), total=100, batch_seconds=time.time()-start)), flush=True)
    (OUT / 'complete.json').write_text(json.dumps(dict(completed=100, time=time.time())))


if __name__ == '__main__':
    main()
