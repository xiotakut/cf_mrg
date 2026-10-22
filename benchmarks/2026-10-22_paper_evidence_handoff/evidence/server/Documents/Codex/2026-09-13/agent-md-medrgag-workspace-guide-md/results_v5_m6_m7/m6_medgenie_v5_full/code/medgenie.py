"""MedGENIE 3+2 generate-then-read, adapted to the existing v5 input contract."""
import json
import re
from common import ROOT, digest, json_object, question_text, valid_answer, visible

UPSTREAM = ROOT / 'upstream/medgenie'


def context_messages(item):
    item = visible(item)
    question = item['question']
    if item['fixed_evidence']:
        question += '\n\nEvidence supplied with the question:\n' + '\n\n'.join(item['fixed_evidence'])
    result, views = [], []
    # No options exist for open diagnosis/relation inputs. Generate five free
    # contexts instead of inventing answer candidates (explicit v5 adaptation).
    for focused, count in ((True, 3), (False, 2)) if item['options'] else ((False, 5),):
        suffix = '' if focused else '-no-options'
        template = (UPSTREAM / f'context_generation/prompt/pmc-llama-13b-awq-template{suffix}.txt').read_text().strip()
        examples = re.findall(r'### Question:\s*(.*?)\s*### Context:\s*(.*?)(?=\s*### Question:|$)', template, re.S)
        assert len(examples) == 2
        messages = [dict(role='system', content='Generate a medical background context for the final question, following the two examples. Return only the background context.')]
        for stem, context in examples:
            messages.extend([dict(role='user', content='### Question:\n' + stem),
                             dict(role='assistant', content=context)])
        prompt = '### Question:\n' + question
        if focused:
            prompt += '\n' + '\n'.join('- ' + value for value in item['options'].values())
        prompt += '\n\n### Context:'
        messages.append(dict(role='user', content=prompt))
        result.extend([messages] * count)
        views.extend(['option_focused' if focused else 'option_free'] * count)
    return result, views


def reader_messages(item, contexts):
    # Preserve the official Llama-3 one-shot question and all its context.
    template = (UPSTREAM / 'icl_reader/templates/templates_llama3/Meta-Llama-3-8B-Instruct/medqa/medqa4opt.txt').read_text()
    parts = re.findall(r'<\|start_header_id\|>(\w+)<\|end_header_id\|>\s*(.*?)(?:<\|eot_id\|>|$)', template, re.S)
    example = parts[1][1].strip()
    example = example.replace("Select only one option. Don't explain your choice.", 'Return a JSON object with the selected option key in "answer".')
    return [
        dict(role='system', content='You are a medical expert. Answer the medical task based on the provided context. Return one JSON object following the requested answer format.'),
        dict(role='user', content=example),
        dict(role='assistant', content='{"answer":"A"}'),
        dict(role='user', content='Context:\n' + '\n'.join(contexts) + '\n\n' + question_text(item) + '\nReturn only the requested JSON object.'),
    ]


def generate(session, stage, messages, sampling):
    limit = session.config['budgets'][stage]
    spec = dict(kind='llm', stage=stage, messages=messages, max_tokens=limit,
                sampling=sampling, model=session.config['model_id'],
                method_version=session.config['method_version'])
    spec['seed'] = (session.config['seed'] + int(digest(spec)[:8], 16)) % (2**31)
    return session.request(spec, lambda: session.model.generate(
        messages, limit, spec['seed'], sampling=sampling))


def native_answer(raw, item):
    """A single chosen native key is a singleton set for multi-answer tasks."""
    if item['answer_format'] == 'multi':
        try:
            obj = json_object(raw, 'answer')
        except ValueError:
            return raw
        if isinstance(obj['answer'], str) and obj['answer'] in item['options']:
            obj['answer'] = [obj['answer']]
            return json.dumps(obj, ensure_ascii=False)
    return raw


def medgenie(item, session):
    prompts, views = context_messages(item)
    responses = generate(session, 'contexts', prompts, session.config['generator_sampling'])
    contexts = [r['text'].strip() for r in responses]
    session.event('generated_contexts', views=views, contexts=contexts,
                  finish_reasons=[r['finish_reason'] for r in responses])
    if len(contexts) != 5 or any(not text for text in contexts):
        return dict(status='invalid', termination='incomplete_contexts', raw_response='')
    response = generate(session, 'reader', [reader_messages(item, contexts)], session.config['reader_sampling'])[0]
    raw = native_answer(response['text'], item)
    error = valid_answer(raw, item)
    session.event('reader', raw_response=response['text'], native_response=raw,
                  serialization='native_multi_singleton_v1', validation_error=error)
    return dict(status='invalid' if error else 'ok', termination='invalid_answer' if error else 'answered',
                raw_response=raw, model_raw_response=response['text'], validation_error=error, context_views=views)
