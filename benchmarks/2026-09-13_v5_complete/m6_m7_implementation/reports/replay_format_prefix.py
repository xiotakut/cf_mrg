"""Uniform reuse of unchanged real stages for the syntax/interface fixes."""
import json
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, digest, file_hash, read
from methods import parse_queries

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=Path, default=ROOT / 'runs/imedrag_dev_v4')
p.add_argument('--target', type=Path, default=ROOT / 'runs/imedrag_dev')
p.add_argument('--reuse-format', action='store_true', help='For a deterministic output syntax change with unchanged model prompts.')
args = p.parse_args()
source, target = args.source.resolve(), args.target.resolve()
config = json.loads((source / 'resolved_config.json').read_text())
assert config['method'] == 'imedrag'
complete = json.loads((source / 'complete.json').read_text())
assert complete['N_pending'] == 0 and complete['N_planned'] == 24
assert file_hash(ROOT / 'data/dev_inputs.jsonl') == config['inputs_hash']
assert not target.exists(), 'Never overwrite an existing run.'
for name, value in config['code_hashes'].items():
    # The runner change only rejects changed worker counts before loading.
    # Request construction, sampling, tokenizer and retrieval stay unchanged.
    if name not in ('methods.py', 'run.py'):
        assert file_hash(ROOT / 'code' / name) == value
copied, changed_rounds = [], {}
for item in read(ROOT / 'data/dev_inputs.jsonl'):
    folder = source / 'items' / item['item_id']
    records = [json.loads(p.read_text()) for p in (folder / 'requests').glob('*.json')]
    llm = {r['spec']['stage']: r for r in records if r['spec']['kind'] == 'llm' and r['status'] == 'ok'}
    restart_round = None
    for path in sorted((folder / 'events').glob('*.json')):
        event = json.loads(path.read_text())
        if event['kind'] != 'imedrag_queries':
            continue
        rnd = event['round']
        parser_stages = sorted(s for s in llm if s == f'parse/{rnd}' or s.startswith(f'parse/{rnd}/'))
        if not parser_stages:
            continue
        try:
            queries, _ = parse_queries(llm[parser_stages[-1]]['result'][0]['text'],
                                       llm[f'query/{rnd}']['result'][0]['text'])
        except ValueError:
            continue
        if queries != event['queries']:
            restart_round = rnd
            changed_rounds[item['item_id']] = rnd
            break
    for request in sorted((folder / 'requests').glob('*.json')):
        record = json.loads(request.read_text())
        assert request.stem == digest(record['spec'])
        parts = record['spec']['stage'].split('/')
        if parts[0] == 'format' and not args.reuse_format:
            continue
        # A syntax fix can recover a previously rejected genuine query. Its
        # QA and every subsequent history-dependent request must be recomputed.
        if restart_round is not None:
            assert not args.reuse_format, 'Full receipt replay requires unchanged queries.'
            if parts[0] == 'final':
                continue
            rnd = int(parts[1])
            if rnd > restart_round or (rnd == restart_round and parts[0] == 'qa'):
                continue
        files = [request] + sorted((folder / 'attempts' / request.stem).glob('*.json'))
        for old in files:
            new = target / old.relative_to(source)
            new.parent.mkdir(parents=True, exist_ok=True)
            os.link(old, new)
        copied.append(dict(item_id=item['item_id'], request_key=request.stem,
                           source_path=str(request), sha256=file_hash(request)))
os.link(source / 'batching.json', target / 'batching.json')
atomic(target / 'cache_provenance.json', dict(source_run=str(source),
    source_config_hash=digest(config), inputs_hash=config['inputs_hash'],
    copied_requests=copied, excluded_stage=None if args.reuse_format else 'format',
    recompute_from_round=changed_rounds,
    selection='Every fixed development input; no correctness filtering.',
    fresh_compute='None expected: deterministic answer syntax only.' if args.reuse_format else 'Existing final formatter, plus QA/history requests affected by syntactically recovered queries. Prior final predictions remain in the source run.'))
print(json.dumps(dict(source_run=str(source), target_run=str(target), copied_requests=len(copied))))
