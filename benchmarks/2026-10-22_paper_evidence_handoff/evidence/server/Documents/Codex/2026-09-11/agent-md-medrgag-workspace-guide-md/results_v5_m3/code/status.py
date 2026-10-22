import json,subprocess,time
from collections import Counter
from pathlib import Path
from prepare import OUT
plan=json.loads((OUT/'plan.json').read_text())
results=[json.loads(p.read_text()) for p in (OUT/'cache/items').glob('*/result.json')]
progress=[json.loads(p.read_text()) for p in sorted(OUT.glob('run_*_progress.json'))]
value=dict(time=time.strftime('%Y-%m-%d %H:%M:%S'),reused=plan['reused_M3_predictions'],new_complete=len(results),total_complete=plan['reused_M3_predictions']+len(results),expected=plan['unique_inputs'],remaining=plan['pending']-len(results),statuses=dict(Counter(r['status'] for r in results)),progress=progress,failures=[json.loads(p.read_text()) for p in OUT.glob('*_failure.json')],gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,memory.free,utilization.gpu','--format=csv,noheader'],text=True).strip())
print(json.dumps(dict(value,progress=[dict(shard=r['shard'],processed=r['processed'],planned=r['planned'],seconds_since_update=round(time.time()-r['updated'])) for r in progress]),ensure_ascii=False,indent=2))
with (OUT/'supervision.jsonl').open('a') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')
