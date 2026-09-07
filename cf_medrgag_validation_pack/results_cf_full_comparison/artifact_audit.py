"""Run after completion: python results_cf_full_comparison/artifact_audit.py."""
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def main():
    config = json.loads((OUT / 'config.json').read_text())
    items = {r['item_id']: r for r in rows(OUT / 'screening_items.jsonl')}
    ids = set(items)
    scope = json.loads((OUT / 'method_scope.json').read_text())
    assert scope['methods'] == ['M0', 'M1', 'M2'] and len(ids) == 25280
    stages = ['summary', 'explore', 'generate', 'select', 'M0', 'M1', 'M2']
    keys = defaultdict(set)
    item_counts = defaultdict(Counter)
    expected_prompts = defaultdict(set)
    counts = Counter()
    max_prompt_tokens = Counter()
    document_keys = defaultdict(dict)
    for worker in sorted((OUT / 'cache/main').glob('worker-*')):
        assert json.loads((worker / 'config.json').read_text()) == config
        assert not (worker / 'failure.json').exists()
        for stage in stages + ['retrieval', 'rerank']:
            file = worker / (stage + '.jsonl')
            if not file.exists():
                continue
            for r in rows(file):
                assert r['item_id'] in ids
                counts[stage] += 1
                if stage not in stages:
                    assert len(r['documents']) == 5 if stage == 'retrieval' else len(r['documents']) <= 5
                    documents = tuple((d['source'], d.get('id', d.get('docid')), d['contents']) for d in r['documents'])
                    previous = document_keys[stage].setdefault(r['key'], documents)
                    assert previous == documents, ('conflicting document cache', stage, r['key'])
                    continue
                assert r['key'] not in keys[stage], (stage, r['key'])
                keys[stage].add(r['key'])
                item_counts[stage][r['item_id']] += 1
                slot = int(r['key'].split('::')[1]) if '::' in r['key'] else 0
                seed = (config['seed'] + int(r['item_id'][1:]) * 101 + stages.index(stage) * 11 + slot) % (2**31 - 1)
                cfg = config['reader' if stage.startswith('M') else stage]
                assert r['sampling'] == cfg | {'seed': seed}
                assert r['prompt_tokens'] + cfg['max_tokens'] <= config['max_model_len']
                assert r['completion_tokens'] <= cfg['max_tokens']
                max_prompt_tokens[stage] = max(max_prompt_tokens[stage], r['prompt_tokens'])
                prompt_path, suffix = r['prompt_ref'].split(':', 1)
                assert suffix == r['key'] + ':' + stage
                expected_prompts[prompt_path].add((r['key'], stage))
    for stage in ['summary', 'explore', 'generate', 'select', 'M0', 'M1', 'M2']:
        slots = 5 if stage in ['summary', 'generate'] else 1
        assert item_counts[stage] == Counter({k: slots for k in ids}), stage
    assert counts['M0'] == counts['M1'] == 25280
    assert set(item_counts['M2']) == ids
    assert all(set(document_keys[s]) == ids for s in ['retrieval', 'rerank'])
    source = Path(json.loads((OUT / 'reader_completion.json').read_text())['source'])
    unchanged_files = []
    for file in (source / 'cache/main').glob('worker-*/*.jsonl'):
        current = OUT / file.relative_to(source)
        if file.stem in ['M0', 'M1']:
            assert current.read_bytes().startswith(file.read_bytes()), ('old reader output changed', file)
        else:
            assert current.read_bytes() == file.read_bytes(), ('non-reader stage changed', file)
            unchanged_files.append(str(file.relative_to(source)))
    for name in ['screening_items.jsonl', 'evaluation_labels.jsonl', 'taxonomy.jsonl', 'config.json']:
        assert (OUT / name).read_bytes() == (source / name).read_bytes(), name
    prompt_counts = {}
    for path, expected in expected_prompts.items():
        found = set()
        with gzip.open(OUT / path, 'rt') as stream:
            for line in stream:
                r = json.loads(line)
                found.add((r['key'], r['stage']))
        assert expected <= found, path
        prompt_counts[path] = {'referenced': len(expected), 'missing': len(expected - found)}
    report = {'status': 'pass', 'checked_at': datetime.now().astimezone().isoformat(),
              'unique_inputs': len(ids), 'stage_record_counts': dict(counts), 'unchanged_source_stage_files': unchanged_files,
              'max_prompt_tokens': dict(max_prompt_tokens), 'durable_prompt_references': prompt_counts,
              'checks': ['complete M2 stage slots', 'no duplicate LLM stage keys', 'complete M0/M1 counts and unchanged prior reader prefixes',
                         'frozen decoding and input/stage seeds', 'context/completion budgets',
                         'same worker configs and source inputs', 'no M2/retrieval/KGCC/KADS recomputation', 'consistent complete document caches',
                         'readable durable gzip prompt references']}
    (OUT / 'artifact_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
