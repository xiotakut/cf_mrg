"""The adopted R4 worker's physical request and engine settings, explicitly bound.

This backend never changes a model policy to fit available GPU memory. In-process
LLM.generate is the original serving boundary (there was no HTTP server).
"""
import sys
import time
import json
from pathlib import Path
from copy import deepcopy
from itertools import count
from types import SimpleNamespace, MethodType
from unittest.mock import patch

from cf_moa.contracts import ModelResult, digest
from cf_moa.tools.adopted import EXTRA_SITE
from cf_moa.tools.schema_compat import SchemaCompatibilityError


def dependencies():
    if EXTRA_SITE not in sys.path:
        sys.path.insert(0, EXTRA_SITE)
    import msgspec
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams
    return msgspec, AutoTokenizer, LLM, SamplingParams, GuidedDecodingParams


def sampling_snapshot(params):
    # SamplingParams is an omit-defaults msgspec Struct; include defaults too.
    import msgspec
    return msgspec.to_builtins({key: getattr(params, key) for key in params.__struct_fields__})


def engine_request_snapshot(prompt, params, llm_class):
    """Run the installed synchronous ingress on a copy, without an engine.

    LLM.generate sets output_kind=FINAL_ONLY before add_request, including in
    the original adopted worker. Compare at the same boundary, preserving the
    caller's request and checking every resolved field rather than ignoring one.
    """
    accepted=[]
    def observe(request_id, prompt, params, **extra):
        accepted.append(dict(prompt=prompt,sampling_params=sampling_snapshot(params),extra=extra))
    observer=SimpleNamespace(request_counter=count(),llm_engine=SimpleNamespace(add_request=observe))
    observer._add_guided_params=MethodType(llm_class._add_guided_params,observer)
    observer._add_request=MethodType(llm_class._add_request,observer)
    llm_class._validate_and_add_requests(observer,[deepcopy(prompt)],[deepcopy(params)],
        lora_request=None,prompt_adapter_request=None)
    if len(accepted)!=1:raise RuntimeError('Unexpected synchronous request ingress count')
    return accepted[0]


class VLLMBackend:
    def __init__(self, adopted, *, load_model=False):
        self.adopted = adopted
        self.msgspec, AutoTokenizer, self.LLM, self.SamplingParams, self.Guided = dependencies()
        self.tokenizer = AutoTokenizer.from_pretrained(adopted.config['model'], local_files_only=True)
        self.physical_calls = []
        self.llm = None
        self.initialization_seconds = 0.0
        self._grammar_compiler = None
        self._preflight_cache = {}
        if load_model:
            self.start()

    def start(self):
        if self.llm is not None:
            raise RuntimeError('Model already initialized')
        before = time.monotonic()
        self.llm = self.LLM(**self.adopted.engine_kwargs())
        self.initialization_seconds = time.monotonic() - before

    def prepare(self, request):
        if request != self.adopted.request(request['messages'], request['schema']):
            raise ValueError('Physical request differs from its complete adopted policy')
        cfg = self.adopted.config
        prompt = self.tokenizer.apply_chat_template(request['messages'], tokenize=False,
            add_generation_prompt=True, **cfg.get('chat_template_kwargs', {}))
        params = self.SamplingParams(
            **{k: request[k] for k in ('seed', 'temperature', 'top_p', 'top_k', 'max_tokens')},
            guided_decoding=self.Guided(json=request['schema'], backend='xgrammar') if cfg['guided_json'] else None)
        physical = dict(engine_kwargs=self.adopted.engine_kwargs(), prompt=prompt,
            sampling_params=sampling_snapshot(params), use_tqdm=False)
        return physical, params

    def count_tokens(self, request):
        physical, _ = self.prepare(request)
        # vLLM InputPreprocessor uses the tokenizer's default special-token
        # policy for these models. Llama adds a BOS; Qwen does not.
        return len(self.tokenizer.encode(physical['prompt']))

    def preflight(self, request):
        """Compile with the installed V1/xgrammar and the actual model tokenizer.

        This CPU gate is complemented by live smoke through generate_batch and
        the unchanged expert/parser. It is not called a real model request.
        """
        from vllm.v1.structured_output.backend_xgrammar import validate_xgrammar_grammar
        physical, params = self.prepare(request)
        key = digest(physical['sampling_params'].get('guided_decoding'))
        if key in self._preflight_cache:
            return self._preflight_cache[key]
        before = time.monotonic()
        try:
            validate_xgrammar_grammar(deepcopy(params))
            guided = params.guided_decoding
            if guided is not None:
                import xgrammar as xgr
                if self._grammar_compiler is None:
                    cfg = json.loads((Path(self.adopted.config['model'])/'config.json').read_text())
                    vocab_size = cfg.get('text_config', cfg)['vocab_size']
                    info = xgr.TokenizerInfo.from_huggingface(self.tokenizer, vocab_size=vocab_size)
                    self._grammar_compiler = xgr.GrammarCompiler(info, max_threads=8, cache_enabled=True)
                if guided.grammar is not None:
                    self._grammar_compiler.compile_grammar(guided.grammar)
                elif guided.json is not None:
                    self._grammar_compiler.compile_json_schema(guided.json)
                else:
                    raise SchemaCompatibilityError('Unexpected guidance type for this native backend')
        except Exception as error:
            if isinstance(error, SchemaCompatibilityError):
                raise
            raise SchemaCompatibilityError(str(error)) from error
        value = dict(status='compiled', model=self.adopted.config['model'],
            config_hash=self.adopted.config_hash, guidance_hash=key,
            elapsed_seconds=time.monotonic()-before, new_model_requests=0)
        self._preflight_cache[key] = value
        return value

    def __call__(self, request):
        return self.generate_batch([request])[0]

    def interpret(self, result, request):
        return result.outputs[0].text

    def generate_batch(self, requests):
        if self.llm is None:
            raise RuntimeError('Model is not loaded; offline capture is not a live result')
        if not 0 < len(requests) <= self.adopted.config['batch_size']:
            raise ValueError('Batch must respect the adopted worker batch_size')
        prepared = [self.prepare(request) for request in requests]
        before = time.monotonic()
        records = [dict(request=physical, request_hash=digest(physical), status='started',
                       submission_state='not_submitted',
                       expected_engine_request=engine_request_snapshot(physical['prompt'],params,self.LLM))
                   for physical, params in prepared]
        self.physical_calls.extend(records)
        accepted = []
        original = self.llm.llm_engine.add_request
        core = self.llm.llm_engine.engine_core
        original_core_add = core.add_request

        def observe(request_id, prompt, params, **kwargs):
            entry = dict(engine_request_id=request_id, prompt=prompt,
                sampling_params=sampling_snapshot(params), extra=kwargs)
            records[len(accepted)]['engine_accepted'] = entry
            accepted.append(entry)
            return original(request_id, prompt, params, **kwargs)

        def observe_core(request, *args, **kwargs):
            record = next(r for r in records if
                r.get('engine_accepted', {}).get('engine_request_id') == request.request_id)
            record.update(submission_state='attempted_unknown', engine_core_request_id=request.request_id)
            value = original_core_add(request, *args, **kwargs)
            record['submission_state'] = 'accepted'
            return value

        try:
            with patch.object(self.llm.llm_engine, 'add_request', observe), \
                 patch.object(core, 'add_request', observe_core):
                outputs = self.llm.generate([physical['prompt'] for physical, _ in prepared],
                    [params for _, params in prepared], use_tqdm=False)
            elapsed = time.monotonic()-before
            if len(outputs) != len(requests) or len(accepted) != len(requests):
                raise RuntimeError('Engine accepted/output request count differs from the submitted batch')
            results = []
            for result, record, engine, request in zip(outputs, records, accepted, requests):
                answer = result.outputs[0]
                event = dict(mode='live', model=self.adopted.config['model'],
                    config_hash=self.adopted.config_hash, input_tokens=len(result.prompt_token_ids),
                    output_tokens=len(answer.token_ids), elapsed_seconds=elapsed/len(requests),
                    elapsed_attribution='equal share of measured batch wall time', batch_seconds=elapsed,
                    finish_reason=answer.finish_reason, physical_batch_size=len(requests))
                record.update(status='complete', raw_response=answer.text, event=event, engine_accepted=engine)
                record['engine_prompt_token_ids'] = list(result.prompt_token_ids)
                if record['engine_prompt_token_ids'] != self.tokenizer.encode(record['request']['prompt']):
                    raise RuntimeError('Actual engine tokenization differs from measured input reservation')
                value = self.interpret(result,request)
                record['value'] = value
                results.append(ModelResult(value, [event]))
            return results
        except Exception as error:
            for record in records:
                record.update(status='failed', error_type=type(error).__name__, error=str(error))
            raise
