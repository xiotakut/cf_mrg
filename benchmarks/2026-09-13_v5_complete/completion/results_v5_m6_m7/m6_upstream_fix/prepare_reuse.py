"""Reuse requests only before the first changed extractor result per input."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, read
from methods import parse_queries


def main(source, destination):
    assert json.loads((source / 'complete.json').read_text())['N_pending'] == 0
    assert not destination.exists(), 'Prepare a fresh directory only'
    copied, cutoffs = [], {}
    for item in sorted((source / 'items').iterdir()):
        requests = [(p, json.loads(p.read_text())) for p in item.glob('requests/*.json')]
        by_stage = {r['spec']['stage']: r for _, r in requests if r['spec']['kind'] == 'llm'}
        cutoff = None
        for event_path in sorted(item.glob('events/*.json')):
            event = json.loads(event_path.read_text())
            if event['kind'] != 'imedrag_queries':
                continue
            rnd = event['round']
            stages = sorted(s for s in by_stage if s == f'parse/{rnd}' or s.startswith(f'parse/{rnd}/'))
            if not stages:
                continue
            record = by_stage[stages[-1]]
            if record['status'] != 'ok':
                continue
            try:
                queries, _ = parse_queries(record['result'][0]['text'], '')
            except ValueError:
                queries = []
            if queries != event['queries']:
                cutoff = rnd
                break
        cutoffs[item.name] = cutoff
        for path, record in requests:
            stage = record['spec']['stage'].split('/')
            if cutoff is not None:
                if stage[0] not in ('query', 'parse', 'qa'):
                    continue
                rnd = int(stage[1])
                if rnd > cutoff or (rnd == cutoff and stage[0] == 'qa'):
                    continue
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            assert json.loads(target.read_text()) == record
            copied.append(dict(item_id=item.name, request_key=path.stem, source_path=str(path)))
    atomic(destination / 'cache_provenance.json', dict(source_run=str(source),
           copied_requests=copied, recompute_from_round=cutoffs,
           selection='Every planned diagnostic input; compare extractor outputs, not correctness.',
           change='Upstream extractor-list acceptance and nonfatal skipped query rounds.',
           fresh_compute='Recompute QA and all dependent later stages from first changed query list.'))
    print(json.dumps(dict(copied_requests=len(copied), recompute_from_round=cutoffs)))


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
