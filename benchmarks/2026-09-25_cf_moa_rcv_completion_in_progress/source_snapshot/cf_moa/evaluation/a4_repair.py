"""Separate physical request identity from historical-response execution replay."""
import argparse
import ast
from collections import Counter
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import inspect
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

from cf_moa.agents import a4_intervention_execution as a4
from cf_moa.contracts import InputPacket, ModelResult, digest
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import a4_adopted, R4_ROOT, R4_RENDER, R4_WORKER, EXTRA_SITE, sha256
from cf_moa.tools.legacy import r4_modules
from cf_moa.tools.vllm_backend import VLLMBackend, sampling_snapshot

DEV = R4_ROOT / 'v2/dev'


def read(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream]


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def append(path, value):
    with Path(path).open('a') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False)+'\n')


def packet(row, handle):
    native = dict(question=row['question'], options={'yes': 'yes', 'no': 'no'},
                  answer_format='single', fixed_evidence=[])
    return InputPacket(request_id=handle, native_input=native, question=row['question'],
        original_context=[dict(role='user', content=row['question'])],
        answer_schema={'type': 'object'}, model_input=row['native_input'], available_tools=[a4.TOOL])


def source_function(path, name, namespace):
    """Execute the exact old function, excluding unrelated dataset/scoring imports."""
    tree = ast.parse(Path(path).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


class Captured(BaseException):
    """Stop before any response parse/solver execution; not a model failure."""
    def __init__(self, value):
        self.value = deepcopy(value)


class CaptureBackend:
    def count_tokens(self, request):
        return 0  # No generation; request-only instrumentation has no token cost.

    def __call__(self, request):
        raise Captured(request)


def capture_new(p, method):
    try:
        a4.run(p, ModelSession(p, CaptureBackend()), method=method)
    except Captured as result:
        return result.value
    raise AssertionError('Eligible A4 did not issue exactly one compile request')


def capture_old(p):
    def generate(messages, schema):
        raise Captured(dict(messages=messages, schema=schema))
    with r4_modules() as (head, _):
        try:
            head.optimize(p.model_input, p.question, generate, arm='patch')
        except Captured as result:
            return result.value
    raise AssertionError('Old R4 did not issue a compile request')


def differences(left, right, path='request'):
    result = []
    if type(left) is not type(right):
        return [dict(field=path, old=left, new=right)]
    if isinstance(left, dict):
        if list(left) != list(right):
            result.append(dict(field=path+'.__key_order__', old=list(left), new=list(right)))
        for key in left.keys() | right.keys():
            if key not in left or key not in right:
                result.append(dict(field=path+'.'+key, old=left.get(key), new=right.get(key)))
            else:
                result.extend(differences(left[key], right[key], path+'.'+key))
    elif isinstance(left, list):
        if len(left) != len(right):
            result.append(dict(field=path+'.length', old=len(left), new=len(right)))
        for index, (x, y) in enumerate(zip(left, right)):
            result.extend(differences(x, y, path+f'[{index}]'))
    elif left != right:
        result.append(dict(field=path, old=left, new=right))
    return result


def old_physical_requests(method, jobs):
    """Instrument original run_model at its LLM boundary, retaining real SamplingParams."""
    import vllm
    cfg = json.loads((DEV / method.lower() / 'config.json').read_text())
    captured = []

    class EngineCapture:
        def __init__(self, **kwargs):
            self.kwargs = deepcopy(kwargs)

        def generate(self, prompts, params, **kwargs):
            for prompt, sampling in zip(prompts, params):
                captured.append(dict(engine_kwargs=deepcopy(self.kwargs), prompt=prompt,
                    sampling_params=sampling_snapshot(sampling), **kwargs))
            return [SimpleNamespace(prompt_token_ids=[], outputs=[SimpleNamespace(
                text='', token_ids=[], finish_reason='offline_boundary_capture')]) for _ in prompts]

    with tempfile.TemporaryDirectory(prefix='cf_moa_old_worker_capture_') as directory:
        out = Path(directory)
        folder = out / method.lower()
        folder.mkdir()
        dump(folder/'config.json', cfg)
        for job in jobs:
            append(folder/'capture_requests.jsonl', job)
        namespace = dict(OUT=out, read=read, dump=dump, os=os, json=json, sys=sys,
                         time=time, EXTRA_SITE=EXTRA_SITE)
        worker = source_function(R4_WORKER, 'run_model', namespace)
        with patch.object(vllm, 'LLM', EngineCapture), patch.dict(os.environ, {'CUDA_VISIBLE_DEVICES': '0'}), redirect_stdout(io.StringIO()):
            worker(method, 0, 'capture', ['patch'])
    return captured


@contextmanager
def solver_trace():
    """Observe actual old/new solver invocations, including resolved keyword defaults."""
    with r4_modules() as (_, executor):
        original = executor.execute
        signature = inspect.signature(original)
        calls = []

        def execute(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            record = dict(arguments=deepcopy(dict(bound.arguments)))
            calls.append(record)
            result = original(*args, **kwargs)
            record['result'] = deepcopy(result)
            return result

        with patch.object(executor, 'execute', execute):
            yield calls


class CachedBackend:
    def __init__(self, expected, raw, adopted, *, mode='replay'):
        self.expected, self.raw, self.adopted, self.mode = expected, raw, adopted, mode
        self.calls = 0

    def count_tokens(self, request):
        assert not differences(self.expected, request), 'Adapter request changed after the separate request check'
        return self.raw['prompt_tokens']

    def __call__(self, request):
        self.count_tokens(request)
        self.calls += 1
        assert self.calls == 1, 'No extra response retry is adopted'
        return ModelResult(self.raw['raw_response'], [dict(mode=self.mode,
            model=self.adopted.config['model'], config_hash=self.adopted.config_hash,
            input_tokens=self.raw['prompt_tokens'], output_tokens=self.raw['completion_tokens'],
            elapsed_seconds=self.raw.get('elapsed_seconds', 0),
            original_finish_reason=self.raw['finish_reason'])])


def request_audit(output, method, rows):
    output.mkdir(parents=True, exist_ok=False)
    adopted = a4_adopted(method)
    backend = VLLMBackend(adopted)
    render = source_function(R4_RENDER, 'render', {})
    historic = {r['item_id']: r for r in read(DEV/method.lower()/'matched_requests.jsonl') if r['arm']=='patch'}
    historical_runtime = {r['item_id']:r for r in read(DEV/method.lower()/'matched_raw.jsonl') if r['arm']=='patch'}
    jobs, requests, records = [], [], []
    for index, row in enumerate(rows):
        p = packet(row, f'{method}-{index}')
        old = capture_old(p)
        new = capture_new(p, method)
        diff = differences(old, {k:new[k] for k in ('messages', 'schema')}, 'callback')
        prompt = render(backend.tokenizer, adopted.config, old['messages'])
        job = dict(item_id=row['item_id'], arm='patch', prompt=prompt, schema=old['schema'])
        expected = historic[row['item_id']]
        diff.extend(differences(expected['prompt'], prompt, 'historical_prompt'))
        diff.extend(differences(expected['schema'], old['schema'], 'historical_schema'))
        prepared_tokens = len(backend.tokenizer.encode(prompt,add_special_tokens=False))
        runtime_tokens = backend.count_tokens(new)
        diff.extend(differences(expected['prompt_tokens'],prepared_tokens,'historical_prepared_prompt_tokens'))
        diff.extend(differences(historical_runtime[row['item_id']]['prompt_tokens'],runtime_tokens,'historical_actual_prompt_tokens'))
        jobs.append(job)
        requests.append(new)
        records.append(dict(request_id=p.request_id, source_item_id=row['item_id'],
            old_callback=old, new_callback=new, differences=diff,
            prepared_prompt_tokens=prepared_tokens,actual_prompt_tokens=runtime_tokens,
            tokenizer_default_special_token_delta=runtime_tokens-prepared_tokens))
    old_physical = old_physical_requests(method, jobs)
    for record, new, old in zip(records, requests, old_physical):
        actual, _ = backend.prepare(new)
        record.update(old_physical=old, new_physical=actual)
        record['differences'].extend(differences(old, actual, 'physical'))
        append(output/'requests.jsonl', record)
    failed = [dict(request_id=r['request_id'], differences=r['differences']) for r in records if r['differences']]
    receipt = dict(status='failed' if failed else 'passed', method=method, inputs=len(rows),
        checks=['old/new messages and schema', 'historical rendered prompt and token count',
                'actual historical runtime input tokens including tokenizer default special tokens',
                'original worker LLM kwargs', 'all resolved SamplingParams fields including defaults'],
        old_worker=str(R4_WORKER), old_worker_sha256=sha256(R4_WORKER),
        render_source=str(R4_RENDER), config_source=adopted.source,
        new_model_requests=0, integrations=0, differences=failed)
    dump(output/'receipt.json', receipt)
    print(json.dumps(receipt), flush=True)
    if failed:
        raise RuntimeError('Affected '+method+' A4 request check failed; see explicit field differences')
    return requests


def output_replay(output, method, rows, requests):
    output.mkdir(parents=True, exist_ok=False)
    adopted = a4_adopted(method)
    historical = {r['item_id']:r for r in read(DEV/method.lower()/'matched_raw.jsonl') if r['arm']=='patch'}
    counts = Counter()
    started = time.monotonic()
    tokens = Counter()
    for index, (row, request) in enumerate(zip(rows, requests)):
        p = packet(row, f'{method}-{index}')
        raw = historical[row['item_id']]
        with solver_trace() as old_calls, r4_modules() as (head, _):
            old = head.optimize(p.model_input, p.question, lambda *_: raw['raw_response'], arm='patch')
        backend = CachedBackend(request, raw, adopted)
        session = ModelSession(p, backend)
        with solver_trace() as new_calls:
            new = a4.run(p, session, method=method)
        diff = differences(old, new.trace, 'full_result')
        diff.extend(differences(old_calls, new_calls, 'solver_calls'))
        diff.extend(differences(old['answer'], new.native_proposal, 'native_answer'))
        record = dict(request_id=p.request_id, source_item_id=row['item_id'],
            historical_response=raw, old_result=old, new_proposal=new.to_dict(),
            old_solver_calls=old_calls, new_solver_calls=new_calls, differences=diff,
            model_callbacks=session.calls, tool_callbacks=session.tools)
        append(output/'replay.jsonl', record)
        if diff:
            dump(output/'receipt.json', dict(status='failed', method=method,
                request_id=p.request_id, differences=diff, completed=index))
            raise RuntimeError('Same cached response differs on '+method+'; affected A4 paused')
        counts[old['route']] += 1
        counts['inline_json_valid' if old.get('inline_json_valid') else 'inline_json_invalid'] += 1
        counts['solver_calls'] += len(old_calls)+len(new_calls)
        counts[old.get('tool_fields', {}).get('intervention', {}).get('kind', 'no_action')] += 1
        tokens['input_tokens'] += raw['prompt_tokens']
        tokens['output_tokens'] += raw['completion_tokens']
        if (index+1) % 12 == 0:
            print(json.dumps(dict(method=method, replayed=index+1, counts=counts)), flush=True)
    receipt = dict(status='passed', method=method, inputs=len(rows), counts=dict(counts),
        integrations=counts['solver_calls']*2, new_model_requests=0,
        historical_model_responses=len(rows), historical_tokens=dict(tokens),
        elapsed_seconds=time.monotonic()-started,
        scope='exposed development replay; identical cached response, not fresh text matching',
        checks=['complete old/new trace including parsing and intervention',
                'actual solver arguments with all defaults and complete outputs', 'native answer'])
    dump(output/'receipt.json', receipt)
    print(json.dumps(receipt), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--method', choices=['M4', 'M5', 'both'], default='both')
    parser.add_argument('--request-only',action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = read(DEV/'inputs.jsonl')
    for method in (('M4', 'M5') if args.method=='both' else (args.method,)):
        requests = request_audit(args.output/method.lower()/'requests', method, rows)
        if not args.request_only:
            output_replay(args.output/method.lower()/'replay', method, rows, requests)


if __name__ == '__main__':
    main()
