"""Explicit adopted policies. Generic callback defaults cannot merge into them."""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from cf_moa.contracts import digest

CONFIG_ROOT = Path(__file__).resolve().parents[1] / 'configs'
R4_ROOT = Path('/home/data3/txy/Documents/Codex/2026-09-17/r4_structural_head/physiology_head')
R4_WORKER = Path('/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/relations/experiment.py')
R4_RENDER = Path('/home/data3/txy/Documents/Codex/2026-09-17/r4_head_binding/experiment.py')
EXTRA_SITE = '/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class AdoptedGeneration:
    method: str
    config: dict
    source: dict

    def request(self, messages, schema):
        cfg = self.config
        return deepcopy(dict(kind='generate', messages=messages, schema=schema,
            **{k: cfg[k] for k in ('seed', 'temperature', 'top_p', 'top_k', 'max_tokens')},
            model_config=cfg, config_source=self.source))

    def engine_kwargs(self):
        cfg = self.config
        return deepcopy(dict(model=cfg['model'], seed=cfg['seed'],
            **{k: cfg[k] for k in ('dtype', 'gpu_memory_utilization', 'max_model_len',
                                  'max_num_seqs', 'max_num_batched_tokens')},
            **cfg['model_kwargs'], enable_prefix_caching=True,
            enable_chunked_prefill=True, enforce_eager=True, guided_decoding_backend='xgrammar'))

    @property
    def config_hash(self):
        return digest(self.config)


def a4_adopted(method):
    """Pin each model's complete adopted configuration, with no common defaults."""
    if method not in ('M4', 'M5'):
        raise ValueError('A4 requires an explicit adopted backbone: M4 or M5')
    manifest = json.loads((CONFIG_ROOT / 'a4_sources.json').read_text())
    source = manifest['methods'][method]
    copied = CONFIG_ROOT / source['copy']
    if sha256(copied) != source['sha256'] or sha256(source['path']) != source['sha256']:
        raise RuntimeError('Adopted A4 configuration no longer matches its locked source: ' + method)
    for record in manifest['implementation_sources']:
        if sha256(record['path']) != record['sha256']:
            raise RuntimeError('Adopted A4 implementation changed: ' + record['path'])
    return AdoptedGeneration(method, json.loads(copied.read_text()), deepcopy(source))
