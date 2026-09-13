"""Audit completed diagnostic runs; retain every invalid and failed input."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, read
from report import report
from run import audit


def main():
    manifest = {r['item_id']: r for r in read(ROOT / 'data/pilot_manifest.jsonl')}
    summaries, details = [], []
    for name in ('pilot_m6_gpu1', 'pilot_m6_gpu2', 'pilot_m7_gpu3'):
        run = ROOT / 'runs' / name
        config = json.loads((run / 'resolved_config.json').read_text())
        inputs = Path(config['input_path'])
        assert (run / 'complete.json').exists(), name + ' is not complete'
        coverage = audit(run, read(inputs))
        assert coverage['N_pending'] == 0
        execution = report(run, inputs)
        records = read(run / 'predictions.jsonl')
        summaries.append(dict(run=name, method=config['method'], gpu=config['physical_gpu_selection'],
                              coverage=coverage, wall_seconds=execution['wall_seconds'],
                              throughput_inputs_per_hour=execution['throughput_inputs_per_hour'],
                              fresh_compute=execution['fresh_compute'], checks=execution['checks']))
        for row in records:
            details.append(dict(manifest[row['item_id']], method=row['method'], status=row['status'],
                                termination=row['termination'], seconds=row['seconds'],
                                issues=row.get('issues', []), answer_error=row.get('answer_error'),
                                error=row.get('error'), costs=row['costs']))
    for method in ('imedrag', 'tcrag'):
        rows = [r for r in details if r['method'] == method]
        assert len(rows) == 12 and {r['item_id'] for r in rows} == set(manifest)
    atomic(ROOT / 'pilot_summary.json', dict(scope='12 diagnostic inputs per method; not full benchmark accuracy',
           runs=summaries, statuses={m: dict(Counter(r['status'] for r in details if r['method'] == m))
                                    for m in ('imedrag', 'tcrag')}))
    atomic(ROOT / 'pilot_details.jsonl', details, lines=True)
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
