import json,sys,time,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'formal/code'))
from backend import HFBackend
import torch
config=json.loads((ROOT.parent/'formal/configs/imedrag_single_gpu.json').read_text())
rows=json.loads((ROOT/'bucketing_requests.json').read_text())
engine=HFBackend(config)
engine.generate([rows[0]['messages']],8,rows[0]['seed'])
buckets=collections.defaultdict(list)
for r in rows:buckets[(*r['batch_group'],(r['prompt_tokens']-1).bit_length())].append(r)
results=[]
for name,groups in [('flat',[rows]),('bucketed',list(buckets.values()))]:
    torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats();start=time.monotonic();outputs=[]
    for group in groups:
        outputs.extend(engine.generate([r['messages'] for r in group],128,42,
            sampling_groups=[(1,r['seed']) for r in group]))
    seconds=time.monotonic()-start;tokens=sum(r['completion_tokens'] for r in outputs)
    row=dict(grouping=name,requests=len(outputs),batch_sizes=[len(g) for g in groups],
        padded_prompt_tokens=sum(len(g)*max(r['prompt_tokens'] for r in g) for g in groups),
        tokens=tokens,seconds=seconds,tokens_per_second=tokens/seconds,
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30)
    results.append(row);(ROOT/'bucketing_comparison.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(row),flush=True)
