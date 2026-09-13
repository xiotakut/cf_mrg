import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
items={r['item_id']:r for f in (SOURCE/'data').glob('chunk_*.jsonl') for l in f.open() if (r:=json.loads(l))}
rows=[]
for f in sorted((SOURCE/'runs').glob('imedrag_*/items/*/result.json')):
 result=json.loads(f.read_text())
 receipts=[json.loads(p.read_text()) for p in Path(result['requests_path']).glob('*.json')]
 formats=[r for r in receipts if r['spec'].get('stage')=='format' and r['status']=='ok']
 assert len(formats)==1, result['item_id']
 spec=formats[0]['spec']
 rows.append(dict(item=items[result['item_id']],original=result,spec=spec,format_raw=formats[0]['result'][0]['text']))
assert len({r['item']['item_id'] for r in rows})==len(rows)
p=ROOT/'inputs.jsonl'
assert not p.exists()
p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
print(len(rows),Counter(r['original']['status'] for r in rows),Counter(r['item']['answer_format'] for r in rows))
