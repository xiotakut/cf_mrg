"""Read-only environment, input, and prompt-length checks, without model calls."""
import json
import os
from collections import Counter
from pathlib import Path
from common import ROOT, MEDRAG, atomic, digest, file_hash, read, question_text


def main():
    import sys
    sys.path.insert(0, str(MEDRAG))
    from src.baselines import missing_resources
    from transformers import AutoTokenizer
    lock = json.loads((ROOT / 'configs/resources.json').read_text())
    for corpus in lock['corpus'].values():
        for name, expected in corpus['index_files'].items():
            path = Path(corpus['path']) / 'index/bm25' / name
            st = path.stat()
            assert st.st_size == expected['size'] and st.st_mtime_ns == expected['mtime_ns'], str(path)
            if expected['sha256']:
                assert file_hash(path) == expected['sha256'], str(path)
    for filename, expected in lock['reranker'].items():
        assert file_hash(filename) == expected, filename
    checks = {}
    for method in ('imedrag', 'tcrag'):
        config = json.loads((ROOT / 'configs' / (method + '.json')).read_text())
        for filename, expected in lock['models'][method]['files'].items():
            st = Path(filename).stat()
            assert st.st_size == expected['size'] and st.st_mtime_ns == expected['mtime_ns'], filename
        missing = missing_resources(config['retrieval'], config['retrieval']['corpus_path'])
        assert not missing, missing
        tok = AutoTokenizer.from_pretrained(config['model_path'], local_files_only=True)
        lengths = []
        for item in read(ROOT / 'data/inputs.jsonl'):
            text = question_text(item)
            prompt = tok.apply_chat_template([dict(role='system', content='You are a helpful medical expert.'), dict(role='user', content=text)],
                         tokenize=False, add_generation_prompt=True, **config['chat_template_kwargs'])
            n = len(tok.encode(prompt, add_special_tokens=False))
            lengths.append(dict(item_id=item['item_id'], mandatory_tokens=n, answer_format=item['answer_format']))
        assert all(r['mandatory_tokens'] + max(config['budgets'].values()) < config['max_length'] for r in lengths)
        atomic(ROOT / 'reports' / (method + '_input_lengths.jsonl'), lengths, lines=True)
        values = sorted(r['mandatory_tokens'] for r in lengths)
        checks[method] = dict(model_id=config['model_id'], model_files_unchanged=True, retrieval_missing=missing,
              index_files_unchanged=True, reranker_files_unchanged=True,
              mandatory_max_tokens=max(values), median_tokens=values[len(values) // 2],
              p95_tokens=values[int(len(values) * .95)], count=len(values),
              limitation='Checks mandatory input only; every actual stage also checks its complete prompt plus generation allowance. No native evidence is clipped.')
    atomic(ROOT / 'reports/environment_check.json', checks)
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
