"""Original formal M4/M5 readout on complete saved contexts.

This is C0, separate from the adopted F generator and from RCV. The historical
formal worker's engine and sampling policies are bound here without defaults
from the F profile. Importing this module does not load a model or a grader.
"""
import ast
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path

from cf_moa.contracts import digest
from cf_moa.tools.adopted import sha256

ROOT = Path('/home/data3/txy/Documents/Codex')
BASE = ROOT / '2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5'
M4 = ROOT / '2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m4_structured'
VARIANTS = {'M4': 'formal_M4_structured_fix_20260913',
            'M5': 'formal_M5_medrag_qwen3_v5'}


@lru_cache(maxsize=None)
def _function(path, name):
    """Load only the unchanged pure function, excluding historical run state."""
    path = Path(path)
    nodes = [node for node in ast.parse(path.read_text()).body
             if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(nodes) != 1:
        raise RuntimeError('Original C0 function unavailable: ' + name)
    namespace = dict(json=json, combinations=combinations)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


@dataclass(frozen=True)
class C0NativeProfile:
    method: str
    config: dict
    source: dict
    engine: dict

    @property
    def config_hash(self):
        return digest(dict(method=self.method, config=self.config, engine=self.engine))

    def engine_kwargs(self):
        return deepcopy(self.engine)

    def request(self, messages, schema):
        if not self.config['guided_json'] and schema is not None:
            raise ValueError('Formal M5 C0 is unguided; F schema is not its policy')
        if self.config['guided_json'] and schema is None:
            raise ValueError('Formal M4 C0 requires its original visible-input schema')
        return deepcopy(dict(kind='generate', messages=messages, schema=schema,
            **{key:self.config[key] for key in
               ('seed', 'temperature', 'top_p', 'top_k', 'max_tokens')},
            model_config=self.config, config_source=self.source))


def profile(method):
    """The actual formal worker policy, including original resource settings."""
    if method not in VARIANTS:
        raise ValueError('C0 requires M4 or M5')
    if method == 'M4':
        path = M4 / 'config.json'
        formal = json.loads(path.read_text())
        native = formal['base']
        engine = dict(model=native['model_path'], dtype='bfloat16',
            max_model_len=formal['max_model_len'], seed=formal['seed'],
            **{key:formal[key] for key in ('gpu_memory_utilization', 'max_num_seqs',
                'max_num_batched_tokens', 'enable_prefix_caching',
                'enable_chunked_prefill', 'guided_decoding_backend')})
        runtime_sources = [path, M4/'code/worker.py', M4/'code/m4_output_schema.py',
            M4/'code/m4_format_pilot.py', M4/'code/analyze_v5.py']
        batch_size = formal['batch_size']
    else:
        path = BASE / 'M5/config.json'
        native = json.loads(path.read_text())
        # run_m0_then_m5.sh invokes the formal M5 full run with these values.
        # Retain the worker's unspecified vLLM defaults; do not add F overrides.
        engine = dict(model=native['model_path'], dtype='bfloat16',
            max_model_len=native['max_length'], gpu_memory_utilization=.55,
            max_num_seqs=16, enable_prefix_caching=True, seed=native['seed'],
            rope_scaling=deepcopy(native['rope_scaling']))
        runtime_sources = [path, BASE/'code/run_medrag.py',
            BASE/'code/run_m0_then_m5.sh', BASE/'code/analyze_v5.py']
        batch_size = 16
    gen = native['generation_kwargs']
    config = dict(model=native['model_path'], dtype='bfloat16', seed=native['seed'],
        temperature=gen['temperature'], top_p=gen['top_p'], top_k=-1,
        max_tokens=gen['max_new_tokens'], max_model_len=native['max_length'],
        guided_json=method == 'M4', batch_size=batch_size,
        chat_template_kwargs=deepcopy(native['chat_template_kwargs']))
    return C0NativeProfile(method, config,
        dict(variant=VARIANTS[method], original_native_config=deepcopy(native),
             files=[dict(path=str(p), sha256=sha256(p)) for p in runtime_sources]), engine)


def request(packet, method):
    """Use the existing complete original messages; do not add an F instruction."""
    adopted = profile(method)
    if isinstance(packet.original_context, str):
        raise ValueError('C0 requires the original complete message sequence')
    schema = None
    if method == 'M4':
        schema = _function(M4/'code/m4_output_schema.py', 'output_schema')(packet.native_input)
        if schema != packet.answer_schema:
            raise ValueError('M4 C0 schema differs from the original formal worker')
        extra = '\n\n' + _function(M4/'code/m4_format_pilot.py', 'instruction')(packet.native_input)
        if not (packet.original_context[0]['content'].endswith(extra) and
                packet.original_context[-1]['content'].endswith(extra)):
            raise ValueError('M4 C0 lacks the formal system/user output instructions')
    return adopted.request(packet.original_context, schema)


def parse_native(raw_response, method):
    """Exactly the formal objects(raw, 'answer_choice') parser, full object kept.

    No jsonschema gate is added after generation. The native scorer remains
    responsible for native option validity and auxiliary errors, as in v5.
    """
    if method not in VARIANTS or not isinstance(raw_response, str):
        raise ValueError('A completed raw string and explicit M4/M5 are required')
    source = M4 if method == 'M4' else BASE
    return _function(source/'code/analyze_v5.py', 'objects')(raw_response, 'answer_choice')


def whole_result(packet, method, raw_response, *, cost):
    native = parse_native(raw_response, method)
    return dict(request_id=packet.request_id, input_hash=packet.input_hash,
        variant=VARIANTS[method], method_id='C0', backbone=method,
        native_answer=native, raw_response=raw_response,
        native_available=native is not None,
        failure_type=None if native is not None else 'native_parse_unavailable',
        native_validity_status='defer_to_unchanged_native_scorer',
        cost=deepcopy(cost), trace=dict(original_parser='objects(raw, answer_choice)',
            complete_original_object_retained=True, schema_validation_added=False,
            retries=0, fallback_used=False, F_pool_generated=False))


def run(packet, session, method):
    """One actual C0 generation; caller records per-input failures and resumes."""
    before = session.checkpoint()
    raw = session.invoke(request(packet, method), stage='C0:formal_native_readout')
    return whole_result(packet, method, raw, cost=session.cost_since(before))
