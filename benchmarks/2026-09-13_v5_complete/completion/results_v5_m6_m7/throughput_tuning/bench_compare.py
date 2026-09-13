"""Bounded throughput probe using saved formal prompts; never scored."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'formal/code'))
from backend import HFBackend
import torch

method = sys.argv[1]
config = json.loads((ROOT.parent / 'formal/configs' / f'{method}_single_gpu.json').read_text())
rows = json.loads((ROOT / f'{method}_requests.json').read_text())
engine = HFBackend(config)
engine.generate([rows[0]['messages']], 8, rows[0]['seed'], entropy=method == 'tcrag')
results = []
for batch_size in (4, 16, 32):
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    outputs = []
    for offset in range(0, len(rows), batch_size):
        group = rows[offset:offset+batch_size]
        outputs.extend(engine.generate([r['messages'] for r in group], 128, 42,
            entropy=method == 'tcrag', sampling_groups=[(1, r['seed']) for r in group]))
    seconds = time.monotonic()-started
    tokens = sum(r['completion_tokens'] for r in outputs)
    result = dict(batch_size=batch_size, total_requests=len(outputs), seconds=seconds,
        completion_tokens=tokens, tokens_per_second=tokens/seconds,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30)
    results.append(result)
    (ROOT/f'{method}_comparison.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    del outputs
with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) as prof:
    engine.generate([r['messages'] for r in rows], 16, 42, entropy=method == 'tcrag',
        sampling_groups=[(1,r['seed']) for r in rows])
(ROOT/f'{method}_profile.txt').write_text(prof.key_averages().table(sort_by='self_cpu_time_total',row_limit=25)+'\n'+prof.key_averages().table(sort_by='self_cuda_time_total',row_limit=25))
