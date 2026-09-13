"""Read queue progress without touching active inference artifacts."""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def status():
    jobs = [json.loads(p.read_text()) for p in (ROOT / 'jobs').glob('*.json')]
    methods = {}
    for method in ('imedrag', 'tcrag'):
        selected = [j for j in jobs if j['method'] == method]
        counts = Counter(r['status'] for r in map(json.loads, (ROOT / 'data' / f'reused_{method}.jsonl').open()))
        active = []
        for job in selected:
            progress = ROOT / 'runs' / job['name'] / 'progress.json'
            if progress.exists():
                p = json.loads(progress.read_text())
                counts.update(ok=p['N_ok'], invalid=p['N_invalid'], failed=p['N_failed'])
            if job['state'] in ('running', 'error'):
                active.append(dict(job=job['name'], state=job['state'], gpu=job['gpu']))
        completed = sum(counts.values())
        methods[method] = dict(planned=13905, reused=12, completed=completed,
                               new_completed=completed-12, remaining=13905-completed,
                               terminal_statuses=dict(counts), jobs=dict(Counter(j['state'] for j in selected)),
                               active=active)
    return dict(observed_at=datetime.now().astimezone().isoformat(), methods=methods)


if __name__ == '__main__':
    print(json.dumps(status(), ensure_ascii=False, indent=2))
