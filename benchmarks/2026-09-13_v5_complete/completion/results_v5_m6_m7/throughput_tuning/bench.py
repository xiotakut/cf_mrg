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
    try:
        outputs = engine.generate([r['messages'] for r in rows[:batch_size]], 128, 42,
                                  entropy=method == 'tcrag',
                                  sampling_groups=[(1, r['seed']) for r in rows[:batch_size]])
        tokens = sum(r['completion_tokens'] for r in outputs)
        seconds = time.monotonic() - started
        result = dict(batch_size=batch_size, seconds=seconds, completion_tokens=tokens,
                      tokens_per_second=tokens/seconds,
                      padded_prompt_tokens=batch_size*max(r['prompt_tokens'] for r in outputs),
                      peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                      peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30, status='ok')
        del outputs
    except torch.OutOfMemoryError as error:
        result = dict(batch_size=batch_size, status='oom', error=str(error))
        torch.cuda.empty_cache()
    results.append(result)
    (ROOT / f'{method}_benchmark.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(result), flush=True)
