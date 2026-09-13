"""Read pilot progress and real request receipts without initializing models."""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def status():
    rows = []
    directories = [ROOT / 'runs', ROOT / 'm6_upstream_fix/runs', ROOT / 'tc_upstream_fix/runs']
    for run in sorted(p for directory in directories for p in directory.glob('pilot_*')):
        config = json.loads((run / 'resolved_config.json').read_text())
        inputs = [json.loads(line) for line in Path(config['input_path']).read_text().splitlines()]
        results = [json.loads(p.read_text()) for p in run.glob('items/*/result.json')]
        counts = Counter(r['status'] for r in results)
        completed = {r['item_id'] for r in results}
        stages, requests, tokens = [], 0, 0
        for item in inputs:
            directory = run / 'items' / item['item_id']
            receipts = [json.loads(p.read_text()) for p in directory.glob('requests/*.json')]
            for receipt in receipts:
                if receipt['status'] == 'ok' and receipt['spec']['kind'] == 'llm':
                    requests += len(receipt['result'])
                    tokens += sum(r['completion_tokens'] for r in receipt['result'])
            if item['item_id'] not in completed:
                events = sorted(directory.glob('events/*.json'))
                latest = json.loads(events[-1].read_text()) if events else {}
                stages.append(dict(item_id=item['item_id'], receipts=len(receipts),
                                   event=latest.get('kind'), stage=latest.get('stage'),
                                   round=latest.get('round'), step=latest.get('step')))
        exit_file = run.parent.parent / 'logs' / (run.name + '.exit')
        rows.append(dict(run=run.name, gpu=config['physical_gpu_selection'], planned=len(inputs),
                         completed=len(results), statuses=dict(counts), pending=len(inputs)-len(results),
                         successful_llm_requests=requests, completion_tokens=tokens,
                         exit_code=int(exit_file.read_text()) if exit_file.exists() else None,
                         pending_stages=stages))
    return dict(observed_at=datetime.now().astimezone().isoformat(), runs=rows)


if __name__ == '__main__':
    print(json.dumps(status(), ensure_ascii=False, indent=2))
