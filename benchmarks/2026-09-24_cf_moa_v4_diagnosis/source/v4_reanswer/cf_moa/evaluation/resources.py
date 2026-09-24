"""CPU-only admission estimates for the immutable selected engine profiles."""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess

from cf_moa.tools.adopted import CONFIG_ROOT, a4_adopted, sha256
from cf_moa.tools.native_backend import profile


def memory():
    result = subprocess.check_output(['nvidia-smi',
        '--query-gpu=index,name,uuid,memory.total,memory.free',
        '--format=csv,noheader,nounits'], text=True)
    return [dict(gpu=int(a), name=b.strip(), uuid=c.strip(), total_mib=int(d), free_mib=int(e))
            for a,b,c,d,e in csv.reader(result.splitlines())]


def requirement(selected, role, total_mib):
    policy = json.loads((CONFIG_ROOT/'resource_admission.json').read_text())
    cfg = selected.config
    model = Path(cfg['model'])
    architecture = json.loads((model/'config.json').read_text())
    weights = json.loads((model/'model.safetensors.index.json').read_text())['metadata']['total_size']
    if cfg['dtype'] != 'bfloat16':
        raise ValueError('The estimate is specific to the adopted BF16 engines')
    head_dim = architecture.get('head_dim') or architecture['hidden_size']//architecture['num_attention_heads']
    bytes_per_token = (2 * policy['model_dtype_bytes'] * architecture['num_hidden_layers'] *
                       architecture['num_key_value_heads'] * head_dim)
    blocks = cfg.get('model_kwargs', {}).get('num_gpu_blocks_override')
    cache = bytes_per_token * blocks * policy['block_size_tokens'] if blocks is not None else 0
    minimum_context_cache = bytes_per_token * cfg['max_model_len']
    reserve = total_mib * 2**20 * (1-cfg['gpu_memory_utilization'])
    # V1 checks the profiled capacity for max_model_len BEFORE applying the
    # block override. Account for both that check and the actual fixed cache.
    margin = policy['profile_and_runtime_margin_gib'] * 2**30
    estimated_bytes = weights + max(cache, minimum_context_cache + reserve) + margin
    free_mib = max(policy['minimum_free_gib'][role]*1024, math.ceil(estimated_bytes/2**30)*1024)
    return dict(role=role, method=selected.method, minimum_free_mib=free_mib,
        weights_gib=weights/2**30, fixed_kv_gib=cache/2**30 if blocks is not None else None,
        max_context_kv_gib=minimum_context_cache/2**30, utilization_reserve_gib=reserve/2**30,
        unmeasured_profile_runtime_margin_gib=policy['profile_and_runtime_margin_gib'],
        config_hash=selected.config_hash, model_config_sha256=sha256(model/'config.json'),
        weights_index_sha256=sha256(model/'model.safetensors.index.json'),
        status='cpu_estimate_not_gpu_measurement', interpretation=policy['interpretation'])


def admission(selected, role, gpu):
    card = next(row for row in memory() if row['gpu']==gpu)
    needed = requirement(selected, role, card['total_mib'])
    return dict(card=card, requirement=needed, ready=card['free_mib']>=needed['minimum_free_mib'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--role',choices=['a4','readout','facts','catalog','all'],default='all')
    args=parser.parse_args()
    roles=['a4','readout','facts','catalog'] if args.role=='all' else [args.role]
    checks=[admission(a4_adopted(m) if r=='a4' else profile(m,r),r,args.gpu)
            for r in roles for m in ('M4','M5')]
    print(json.dumps(dict(checks=checks, ready=all(c['ready'] for c in checks),
        no_cuda_allocation=True, no_polling_or_reservation=True),ensure_ascii=False,indent=2))
    if not all(c['ready'] for c in checks):
        raise SystemExit(75)


if __name__=='__main__':
    main()
