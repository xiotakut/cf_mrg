"""Five-minute durable progress and complete native v5 scoring."""
import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from common import ROOT, V5, PACK, read, atomic, json_object
sys.path.insert(0, str(V5 / 'code'))
from analyze_v5 import score, norm


def snapshot():
    items = {r['item_id']: r for r in read(ROOT / 'inputs/all.jsonl')}
    labels = {r['item_id']: r for r in read(V5 / 'evaluation.jsonl')}
    canonical = {norm(x): x for x in json.loads((PACK / 'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    jobs = [json.loads(p.read_text()) for p in sorted((ROOT / 'jobs').glob('*.json'))]
    rows = [json.loads(p.read_text()) for p in ROOT.glob('runs/*/items/*/result.json')]
    assert len(rows) == len({r['item_id'] for r in rows}) and {r['item_id'] for r in rows} <= set(items)
    native = []
    for r in rows:
        item = items[r['item_id']]
        raw = r['raw_response'] if r['status'] == 'ok' else ''
        try:
            raw = json.dumps({'answer': json_object(raw, 'answer')['answer']})
        except ValueError:
            raw = ''
        ni = dict(item, answer_format='single') if item['answer_format'] == 'robustness_single' else item
        s = score(dict(raw_response=raw), labels[r['item_id']], ni, canonical)
        native.append(dict(item_id=r['item_id'], answer_format=item['answer_format'], protocol_valid=r['status']=='ok', format_valid=not s['format_invalid'], native_valid=not s['invalid'], invalid_reason=s['invalid_reason'], termination=r['termination'], answer_error=r.get('validation_error')))
    def rates(rs):
        return dict(N=len(rs), **{k: dict(count=sum(r[k] for r in rs), pct=100*sum(r[k] for r in rs)/len(rs) if rs else None) for k in ['protocol_valid', 'format_valid', 'native_valid']})
    result = dict(observed_at=datetime.now().astimezone().isoformat(), timestamp=time.time(), planned=len(items), completed=len(rows), fresh_completed=len(rows), reused_predictions=0, remaining=len(items)-len(rows), overall=rates(native), failed=sum(r['status']=='failed' for r in rows), reused_stage_requests=sum(r['reused_stage_requests'] for r in rows), chunks=dict(Counter(j['state'] for j in jobs)), active_chunks=[j for j in jobs if j['state'] in ('running','error')], by_format={f:rates([r for r in native if r['answer_format']==f]) for f in sorted({r['answer_format'] for r in native})}, terminations=dict(Counter(r['termination'] for r in rows)), native_invalid_reasons=dict(Counter(r['invalid_reason'] or 'valid' for r in native)), costs={k:sum(r['costs'][k] for r in rows) for k in rows[0]['costs']} if rows else {}, gpus=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu','--format=csv,noheader'], text=True))
    previous = ROOT / 'reports/status.json'
    if previous.exists():
        old = json.loads(previous.read_text())
        delta = result['completed'] - old['completed']
        elapsed = result['timestamp'] - old['timestamp']
        result.update(interval_seconds=elapsed, interval_new=delta, interval_inputs_per_hour=delta*3600/elapsed, eta_hours=result['remaining']*elapsed/delta/3600 if delta>0 else None)
    atomic(previous, result)
    with (ROOT / 'reports/supervision.jsonl').open('a') as f:
        f.write(json.dumps(result,ensure_ascii=False)+'\n')
    return result, rows, native


if __name__ == '__main__':
    watch='--watch' in sys.argv
    while True:
        result,_,_=snapshot()
        print(json.dumps(result,ensure_ascii=False),flush=True)
        if not watch or (result['completed']==13905 and result['chunks']=={'done':109}):break
        time.sleep(300)
