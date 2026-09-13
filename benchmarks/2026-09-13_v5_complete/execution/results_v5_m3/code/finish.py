"""Audit exact coverage, release only this run's services, then score v5."""
import json,os,signal,subprocess,sys
from pathlib import Path
from prepare import OUT,read,write
items=read(OUT/'items.jsonl');pending=read(OUT/'pending_M3.jsonl');reused=read(OUT/'cache/reused.jsonl')
rows=[]
for item in pending:
    root=OUT/'cache/items'/item['item_id'];r=json.loads((root/'result.json').read_text())
    assert r['item_id']==item['item_id']
    for p in root.glob('*.prompt.json'):
        q=json.loads(p.read_text());assert q['prompt_tokens']+(8192 if q['thinking'] else 2048)<=131072
    rows.append(r)
ids=[r['item_id'] for r in reused+rows]
assert len(ids)==len(set(ids))==len(items) and set(ids)=={r['item_id'] for r in items}
write(OUT/'M3/predictions.jsonl',rows)
write(OUT/'m3_predictions.jsonl',reused+rows)
(OUT/'artifact_audit.json').write_text(json.dumps(dict(status='passed',expected=len(items),reused=len(reused),new=len(rows),missing=0,duplicates=0))+'\n')
for name,port in [('qwen_1',8011),('qwen_2',8012),('qwen_3',8013),('retriever',8993)]:
    if not (OUT/f'services/{name}.pid').exists():continue
    pid=int((OUT/f'services/{name}.pid').read_text())
    proc=Path(f'/proc/{pid}')
    if not proc.exists():continue
    args=(proc/'cmdline').read_bytes().decode().split('\0')
    assert proc.stat().st_uid==os.getuid() and str(port) in args and any('api_server' in a or 'run_marag_retriever.py' in a for a in args)
    os.kill(pid,signal.SIGTERM)
subprocess.run([sys.executable,str(OUT/'code/analyze_v5.py')],check=True)
(OUT/'analysis_finished_at.txt').write_text(__import__('datetime').datetime.now().astimezone().isoformat()+'\n')
