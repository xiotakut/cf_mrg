"""Continue the frozen intrinsic MA-RAG loop on native v5 task formats."""
import argparse
import ast
from collections import Counter
import gzip
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import numpy as np
from liquid import Template

OUT = Path(__file__).resolve().parents[1]
MARAG = Path('/home/data3/txy/MA-RAG')
sys.path.insert(0, str(MARAG))
from microservice import CustomLanguageModel
from utils import combine_docs, RetrievalService, judger
from response_processing import process_response

# Read the official prompt literals without executing its CLI or loading gold.
PROMPTS = {}
TOKENIZER = None
for node in ast.parse((MARAG / 'ma_rag_entropy.py').read_text()).body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name in ['system_prompt', 'user_prompt', 'user_prompt_round', 'system_prompt_query', 'user_prompt_query']:
            value = node.value.args[0] if isinstance(node.value, ast.Call) else node.value
            PROMPTS[name] = ast.literal_eval(value)


def read(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def dump(path, value):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False) + '\n')
    temp.replace(path)


def norm(text):
    return ' '.join(text.casefold().split()).strip(' .,:;!?"')


def task_prompts(item):
    fmt = item['answer_format']
    system = PROMPTS['system_prompt']
    capital = bool(item['options']) and all(re.fullmatch('[A-Z]', k) for k in item['options'])
    if fmt == 'single' and not capital:
        system = system.replace('capital option', 'exact option key as written in the options')
    elif fmt == 'multi':
        system = system.replace('final choice (capital option)', 'final choices (all and only the correct option keys, separated by commas)')
        system = system.replace('<answer>X</answer>', '<answer>A,B</answer>')
    elif fmt == 'diagnosis':
        system = system.replace('final choice (capital option)', 'single most likely diagnosis (a concise diagnosis label, without alternatives or explanation inside the answer tag)')
    elif fmt == 'relation':
        system = system.replace('final choice (capital option)', 'final answer (exactly higher, lower, no difference, or uncertainty)')
    templates = {}
    for name in ['user_prompt', 'user_prompt_round', 'user_prompt_query']:
        text = PROMPTS[name]
        if fmt in ['diagnosis', 'relation']:
            text = text.replace('multiple-choice question', 'medical question').replace('### Options\n{{options}}\n\n', '')
        elif fmt == 'multi':
            text = text.replace('multiple-choice question', 'multiple-select question (select all correct options)')
        templates[name] = Template(text)
    question = item['question']
    if fmt == 'robustness_single':
        question += '\nSome supplied D-numbered documents may contain factual errors. Identify them, correct their factual errors, and answer the main question. Do not assume all documents are correct. After your answer tag, also include a JSON object with an "errors" array; each entry has "document_id" (D-numbered ID) and "correction" (concise corrected statement). Use [] when none are erroneous.'
    if item['fixed_evidence']:
        question += '\n\nEvidence supplied with the question:\n' + '\n\n'.join(item['fixed_evidence'])
    options = '\n'.join(f'{k}. {v}' for k, v in item['options'].items())
    return system, templates, question, options


def prediction(text, item):
    fmt = item['answer_format']
    if fmt == 'robustness_single':
        return prediction(text, dict(item, answer_format='single'))
    if fmt == 'single' and all(re.fullmatch('[A-Z]', k) for k in item['options']):
        answer, _ = judger(text, '', single_answer=True)
        return answer if answer in item['options'] else None
    if fmt == 'multi':
        answer, _ = judger(text, '', single_answer=False)
        return list(answer) if answer and len(answer) == len(set(answer)) and all(k in item['options'] for k in answer) else None
    tags = re.findall(r'<answer>(.*?)</answer>', text, re.S)
    if not tags:
        return None
    answer = tags[-1].strip()
    if fmt == 'single':
        return answer if answer in item['options'] else None
    if fmt == 'relation':
        answer = norm(answer)
        return answer if answer in ['higher', 'lower', 'no difference', 'uncertainty'] else None
    return answer or None


def vote_key(answer, item):
    if isinstance(answer, str) and item['answer_format'] == 'diagnosis':
        answer = norm(answer)
    return json.dumps(answer, ensure_ascii=False)


class QueryFormatError(RuntimeError):
    pass


def generate(model, path, system, prompt, *, thinking=False, n=1):
    global TOKENIZER
    if path.exists():
        with gzip.open(path, 'rt') as stream:
            return json.load(stream)
    preparing = time.time()
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]
    if TOKENIZER is None:
        from transformers import AutoTokenizer
        TOKENIZER = AutoTokenizer.from_pretrained('/home/data3/txy/models/Qwen3-8B', local_files_only=True)
    rendered = TOKENIZER.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=thinking)
    prompt_tokens = len(TOKENIZER.encode(rendered, add_special_tokens=False))
    maximum = 8192 if thinking else 2048
    if prompt_tokens + maximum > 131072:
        raise ValueError(f'Full stage context overflow: {path.name}: {prompt_tokens} + {maximum}')
    dump(path.with_suffix('').with_suffix('.prompt.json'), dict(messages=messages, thinking=thinking, prompt_tokens=prompt_tokens))
    started = time.time()
    response = model.generate(messages, temperature=0.0 if thinking else 0.7,
        max_new_tokens=8192 if thinking else 2048, enable_thinking=thinking, top_logprobs=20, n=n)
    received = time.time()
    rows = process_response(response)
    processed = time.time()
    assert len(rows) == n
    value = dict(responses=rows, usage=response.usage.model_dump(), seconds=time.time() - started,
        time=time.time(), candidates=n, thinking=thinking,
        finish_reasons=[c.finish_reason for c in response.choices])
    temp = path.with_name(path.name + '.tmp')
    with gzip.open(temp, 'wt') as stream:
        json.dump(value, stream, ensure_ascii=False)
    temp.replace(path)
    dump(path.with_suffix('').with_suffix('.timing.json'), dict(
        preparation_seconds=started-preparing, request_seconds=received-started,
        response_processing_seconds=processed-received, cache_write_seconds=time.time()-processed))
    return value


def solve(item, model, retriever, config):
    root = OUT / 'cache/items' / item['item_id']
    root.mkdir(parents=True, exist_ok=True)
    if (root / 'result.json').exists():
        return json.loads((root / 'result.json').read_text())
    started = time.time()
    system, templates, question, options = task_prompts(item)
    documents = 'null'
    previous_answers = []
    total_queries = total_documents = 0
    status = 'complete'
    error = None
    try:
        for round_id in range(1, config['max_rounds'] + 1):
            prompt = templates['user_prompt' if round_id == 1 else 'user_prompt_round'].render(
                question=question, options=options, answers='\n\n'.join(previous_answers), documents=documents)
            result = generate(model, root / f'round_{round_id}.json.gz', system, prompt, n=config['candidates'])
            outputs = result['responses']
            responses = [r['text'].strip() for r in outputs]
            predictions = [prediction(r, item) for r in responses]
            keys = [vote_key(r, item) for r in predictions]
            entropies = [float(np.mean(r['token_entropies'])) for r in outputs]
            assert all(math.isfinite(e) for e in entropies), 'Nonfinite or missing intrinsic entropy'
            dump(root / f'round_{round_id}.summary.json', dict(predictions=predictions, vote_keys=keys,
                mean_token_entropies=entropies))
            previous_answers = [f"{i}. The assistant's previous answer is:\n" + answer
                                for i, answer in enumerate(responses, 1)]
            if len(set(keys)) == 1 or round_id == config['max_rounds']:
                break
            query = generate(model, root / f'query_{round_id}.json.gz', PROMPTS['system_prompt_query'],
                templates['user_prompt_query'].render(question=question, options=options,
                    answers='\n\n'.join(previous_answers)), thinking=True)
            text = query['responses'][0]['text']
            if '</think>' not in text:
                raise QueryFormatError('Query generation reached its frozen output budget without </think>')
            query_content = text.rsplit('</think>', 1)[1].strip()
            queries = list(set(x.strip() for x in re.findall(r'\[Query .*?\](.*?)$', query_content, re.MULTILINE)))
            total_queries += len(queries)
            retrieval_path = root / f'retrieval_{round_id}.json'
            retrieval_started = time.time()
            if retrieval_path.exists():
                record = json.loads(retrieval_path.read_text())
                assert record['queries'] == queries
                docs = record['documents']
            else:
                docs, seen = [], set()
                if queries:
                    fetch = partial(retriever.retrieve, total_k=32, top_k=2, combine_docs=False, use_reranker=True)
                    with ThreadPoolExecutor(max_workers=len(queries)) as pool:
                        for found, _ in pool.map(fetch, queries):
                            fresh = [doc for doc in found if doc['id'] not in seen]
                            docs.extend(fresh)
                            seen.update(doc['id'] for doc in fresh)
                dump(retrieval_path, dict(queries=queries, documents=docs, seconds=time.time()-retrieval_started))
            total_documents += len(docs)
            documents = combine_docs(docs, combine_sep='\n') if queries else 'null'
            order = np.argsort(entropies)[::-1]
            contents = [responses[i] for i in order]
            previous_answers = [f"{i}. The assistant's previous answer is (Entropy {entropy:.2f}):\n" + answer
                for i, (answer, entropy) in enumerate(zip(contents, sorted(entropies, reverse=True)), 1)]
    except QueryFormatError as exc:
        status, error = 'runtime_invalid', str(exc)
    leaders = Counter(keys).most_common()
    unique = len(leaders) == 1 or leaders[0][1] > leaders[1][1]
    answer = predictions[keys.index(leaders[0][0])] if unique and status == 'complete' else None
    if status == 'complete' and not unique:
        status, error = 'vote_tie', 'Equal highest final vote counts'
    elif status == 'complete' and answer is None:
        status, error = 'invalid_answer', 'The highest-vote candidate has no valid native answer'
    record = dict(item_id=item['item_id'], method='marag_intrinsic_qwen3_8b', stage='M3',
        answer=answer, raw_response=json.dumps({'answer': answer}, ensure_ascii=False),
        output_kind='native_scorer_serialization_of_final_vote', status=status, error=error,
        rounds_used=round_id, final_vote_counts=dict(leaders), unanimous=len(leaders) == 1,
        retrieval_queries=total_queries, retrieved_documents=total_documents,
        elapsed_seconds=time.time() - started, finished_at=time.time(), source_run=str(OUT),
        raw_candidates=str(root.relative_to(OUT)))
    if item['answer_format'] == 'robustness_single':
        # Answer voting is unchanged. Preserve one real winning candidate's
        # document corrections; never synthesize corrections from gold labels.
        selected = keys.index(leaders[0][0]) if answer is not None else None
        errors = None
        if selected is not None:
            decoder = json.JSONDecoder()
            for match in re.finditer(r'\{', responses[selected]):
                try:
                    obj, _ = decoder.raw_decode(responses[selected][match.start():])
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and 'errors' in obj:
                    errors = obj['errors']
                    break
        record['selected_candidate_index'] = selected
        record['raw_response'] = json.dumps(dict(answer=answer, errors=errors), ensure_ascii=False)
    dump(root / 'result.json', record)
    return record


def self_check():
    item = dict(question='Question text', options={'A': 'Alpha', 'B': 'Beta'}, fixed_evidence=[], answer_format='single')
    system, templates, q, opts = task_prompts(item)
    assert system == PROMPTS['system_prompt']
    assert templates['user_prompt'].render(question=q, options=opts) == Template(PROMPTS['user_prompt']).render(question=q, options=opts)
    assert prediction('<answer>B</answer>', item) == 'B'
    assert prediction('<answer>A,B</answer>', dict(item, answer_format='multi')) == ['A', 'B']
    assert prediction('<answer>A,A</answer>', dict(item, answer_format='multi')) is None
    assert prediction('<answer>yes</answer>', dict(item, options={'yes': 'yes', 'no': 'no'})) == 'yes'
    diagnostic = dict(item, answer_format='diagnosis', options={})
    assert prediction('<answer>Pneumonia</answer>', diagnostic) == 'Pneumonia'
    assert vote_key('Pneumonia', diagnostic) == vote_key('pneumonia', diagnostic)
    assert prediction('<answer>No difference</answer>', dict(item, answer_format='relation', options={})) == 'no difference'
    evidence = 'Keep this exact supplied evidence.'
    assert task_prompts(dict(item, fixed_evidence=[evidence]))[2].endswith(evidence)
    print('Native format, unchanged single-choice prompt, diagnosis voting and full-evidence checks passed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=4)
    parser.add_argument('--endpoint')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    config = json.loads((OUT / 'config.json').read_text())
    plan = json.loads((OUT / 'plan.json').read_text())
    assert plan['status'] == 'frozen' and config['method'] == 'M3'
    items = read(OUT / 'pending_M3.jsonl')
    lengths = {r['item_id']: r['prompt_tokens'] for r in read(OUT / 'input_lengths.jsonl')}
    items.sort(key=lambda r: (lengths[r['item_id']], r['item_id']))
    if args.smoke:
        chosen = set(plan['smoke_item_ids'])
        items = [r for r in items if r['item_id'] in chosen]
    items = items[args.shard::args.shards]
    logging.basicConfig(level=logging.WARNING)
    endpoint = args.endpoint or config['endpoints'][args.shard % len(config['endpoints'])]
    model = CustomLanguageModel('qwen3-8b', logging.getLogger(__name__), base_url=endpoint)
    retriever = RetrievalService()
    started = time.time()
    label = 'smoke' if args.smoke else 'run'
    for index, item in enumerate(items):
        try:
            result = solve(item, model, retriever, config)
        except Exception as exc:
            dump(OUT / f'{label}_{args.shard}_failure.json', dict(item_id=item['item_id'],
                type=type(exc).__name__, message=str(exc), time=time.time()))
            raise
        status = dict(shard=args.shard, item_id=item['item_id'], status=result['status'],
            rounds=result['rounds_used'], processed=index + 1, planned=len(items),
            elapsed_seconds=time.time() - started, updated=time.time())
        dump(OUT / f'{label}_{args.shard}_progress.json', status)
        print(json.dumps(status), flush=True)
    dump(OUT / f'{label}_{args.shard}_complete.json', dict(status='complete', tasks=len(items), time=time.time()))


if __name__ == '__main__':
    main()
