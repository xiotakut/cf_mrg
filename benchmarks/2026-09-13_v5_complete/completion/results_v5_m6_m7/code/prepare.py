"""Freeze references to the confirmed v5 pack; never resample its targets."""
import argparse
import importlib.metadata
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from common import ROOT, V5, SELECTION, PACK, MEDRAG, VISIBLE, atomic, digest, file_hash, read, visible


def freeze(path, value, lines=False):
    if Path(path).exists():
        previous = read(path) if lines else json.loads(Path(path).read_text())
        if previous != value:
            raise ValueError('frozen_file_changed:' + str(path))
    else:
        atomic(path, value, lines=lines)


def prepare():
    items, evaluations = read(V5 / 'items.jsonl'), read(V5 / 'evaluation.jsonl')
    units = {r['unit_id']: r for r in read(V5 / 'source_units.jsonl')}
    targets = {r['judgment_id']: r for r in read(SELECTION / 'selected_targets.jsonl.gz')}
    byid = {i['item_id']: i for i in items}
    assert len(items) == len(byid) == 13905
    assert len(units) == 6104 and len(targets) == 13000
    assert len(evaluations) == len({e['record_id'] for e in evaluations}) == 15616
    assert {j for e in evaluations for j in e['judgment_ids']} == set(targets)
    assert {e['unit_id'] for e in evaluations} == set(units)
    assert {e['item_id'] for e in evaluations} == set(byid)
    hashes = {iid: digest(visible(i)) for iid, i in byid.items()}
    assert len(set(hashes.values())) == len(items)
    mapping, manifest, sources = [], [], defaultdict(list)
    for e in evaluations:
        u = units[e['unit_id']]
        ts = [targets[j] for j in e['judgment_ids']]
        assert e['evaluation_labels'] == sorted({l for t in ts for l in t['evaluation_labels']})
        assert all(t['unit_id'] == e['unit_id'] and t['evaluation_eligible'] for t in ts)
        assert set(byid[e['item_id']]) <= set(VISIBLE) | {'item_id', 'max_tokens'}
        if e['resource_id'] == 'M17':
            def task(t):
                return 'MANAGE' if '在家' in t else 'VISIT' if '到诊所' in t else 'RESOURCE'
            assert all(task(t['target']) == e['task'] for t in ts)
        if e['resource_id'] == 'M22':
            assert len(byid[e['item_id']]['fixed_evidence']) == len(e['document_map'])
        for target in ts:
            mapping.append(dict(source_id=e['resource_id'], original_record_id=u.get('source_unit_id', u['unit_id']),
                                original_records=[dict(index=j, content_hash=digest(r)) for j, r in enumerate(u['original_records'])],
                                source=u['source'], unit_id=u['unit_id'], target_id=target['judgment_id'],
                                inference_input_id=e['item_id'], input_hash=hashes[e['item_id']],
                                evaluation_record_id=e['record_id'], evaluation_labels=target['evaluation_labels'],
                                group_id=e['group_id'], role=e['role'], task=e['task']))
        sources[e['item_id']].append(e['resource_id'])
    for i in items:
        manifest.append(dict(inference_input_id=i['item_id'], input_hash=hashes[i['item_id']],
                             source_ids=sorted(set(sources[i['item_id']])), input_path=str(V5 / 'items.jsonl'),
                             answer_format=i['answer_format'], fixed_evidence_hash=digest(i['fixed_evidence'])))
    freeze(ROOT / 'data/input_manifest.jsonl', manifest, lines=True)
    freeze(ROOT / 'data/source_target_input_mapping.jsonl', mapping, lines=True)
    freeze(ROOT / 'data/inputs.jsonl', [dict(item_id=i['item_id'], **visible(i)) for i in items], lines=True)
    # Scoring remains a separate input file that inference never opens.
    freeze(ROOT / 'data/evaluation.jsonl', evaluations, lines=True)
    files = [V5 / 'items.jsonl', V5 / 'evaluation.jsonl', V5 / 'source_units.jsonl',
             SELECTION / 'selected_targets.jsonl.gz', SELECTION / 'sampling_protocol.json',
             SELECTION / 'v3_v4_v5_membership.csv', PACK / 'results_cf_full_test/canonical_labels.json']
    freeze(ROOT / 'data/input_lock.json', dict(files={str(p): file_hash(p) for p in files},
           source_units=len(units), selected_targets=len(targets), unique_inputs=len(items),
           evaluation_records=len(evaluations), expanded_target_input_mappings=len(mapping),
           formats=dict(Counter(i['answer_format'] for i in items)),
           sampling='Reuse confirmed v5; no new sample/seed/qualification decision.'))
    # Check original builder's own selected-target/scoring contracts, redirecting
    # its receipt so no historical preparation_validation.json is overwritten.
    sys.path.insert(0, str(V5 / 'code'))
    import check_v5
    check_v5.dump = lambda path, value: atomic(ROOT / 'reports/v5_existing_contract_audit.json', value)
    check_v5.main()
    prepare_dev(items, evaluations)
    print(json.dumps(dict(inputs=len(items), units=len(units), targets=len(targets), mappings=len(mapping))))


def prepare_dev(formal_items, evaluations):
    formal_hashes = {digest(visible(i)) for i in formal_items}
    dev, labels, provenance, skipped = [], [], [], []
    formal_cases = {e['unit_id'].split(':', 1)[-1] for e in evaluations if e['resource_id'] == 'M01'}

    def add(iid, item, gold, source, raw, locator, role='dev'):
        item = visible(item)
        assert digest(item) not in formal_hashes
        dev.append(dict(item_id=iid, **item))
        labels.append(dict(item_id=iid, source_id=source, gold=gold, role=role, group_id=iid))
        provenance.append(dict(item_id=iid, source_id=source, locator=locator, original_hash=digest(raw), input_hash=digest(item), exposure='official_training_or_development'))

    # Reuse the already-downloaded official validation parquet, with an explicit
    # deterministic option-list -> ordered-dict conversion.
    import pyarrow.parquet as pq
    source_root = PACK / 'results_r1_r5_m0_m1_20260908/sources'
    acquisition = next(x for x in json.loads((source_root / 'acquisition.json').read_text()) if x['split'] == 'validation')
    original = pq.read_table(acquisition['file']).to_pylist()
    converted = [dict(r, options={x['key']: x['value'] for x in r['options']}) for r in original]
    source = ROOT / 'data/medqa_dev_source.jsonl'
    freeze(source, converted, lines=True)
    # The older provenance's url slot holds the local parquet locator. This
    # receipt preserves it while adding the actual pinned acquisition URL.
    freeze(ROOT / 'data/dev_source_acquisition.json', dict(**acquisition,
           file_hash=file_hash(acquisition['file']), records=len(original),
           conversion='options key/value list to insertion-ordered dict; all other fields unchanged',
           selected_original_records=[dict(index=i, original_hash=digest(r), materialized_hash=digest(converted[i])) for i, r in enumerate(original[:12])]))
    for idx, r in enumerate(read(source)[:12]):
        add(f'dev_medqa_{idx:03d}', dict(question=r['question'], options=r['options'], fixed_evidence=[], answer_format='single'),
            r['answer_idx'], 'MedQA_dev', r, dict(path=str(source), line=idx + 1, url=(ROOT / 'data/medqa_source_url.txt').read_text().strip()))
    source = PACK / 'private_data/deltarank_sources/medeinst_train.jsonl'
    with source.open() as f:
        for idx, line in enumerate(f):
            r = json.loads(line)
            item = dict(question=r['narrative'], options={}, fixed_evidence=[], answer_format='diagnosis')
            if r['case_id'] in formal_cases or digest(item) in formal_hashes:
                skipped.append(dict(line=idx + 1, case_id=r['case_id'], reason='formal_group_or_input_overlap'))
                continue
            if len(dev) >= 24:
                break
            add(f'dev_medeinst_{idx:03d}', item,
                r['ground_truth'], 'MedEinst_train', r, dict(path=str(source), line=idx + 1, case_id=r['case_id']))
    assert len(dev) == 24
    freeze(ROOT / 'data/dev_overlap_audit.json', dict(skipped=skipped, formal_inputs_removed=0, dev_inputs=24,
           rule='First 12 MedQA validation + first 12 MedEinst training records outside every formal group/input; no score-based selection.'))
    freeze(ROOT / 'data/dev_inputs.jsonl', dev, lines=True)
    freeze(ROOT / 'data/dev_gold.jsonl', labels, lines=True)
    freeze(ROOT / 'data/dev_provenance.jsonl', provenance, lines=True)


def lock_resources():
    model_names = dict(imedrag=('meta-llama/Llama-3.1-8B-Instruct', '/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct'),
                       tcrag=('Qwen/Qwen3-8B', '/home/data3/txy/models/Qwen3-8B'))
    resource_lock = ROOT / 'configs/resources.json'
    if resource_lock.exists():
        resources = json.loads(resource_lock.read_text())
    else:
        resources = {'models': {}, 'corpus': {}}
        for method, (model_id, path) in model_names.items():
            root = Path(path)
            names = sorted([*root.glob('*.safetensors'), *root.glob('*config.json'), root / 'tokenizer.json'])
            files = {str(p): dict(size=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns, sha256=file_hash(p)) for p in names}
            resources['models'][method] = dict(id=model_id, path=path, files=files,
                 weight_id=digest({p: x['sha256'] for p, x in files.items() if p.endswith('.safetensors')}),
                 tokenizer_id=digest({p: x['sha256'] for p, x in files.items() if 'tokenizer' in p}))
        for corpus in ('textbooks', 'statpearls', 'pubmed', 'wikipedia'):
            root = MEDRAG / 'corpus' / corpus
            paths = sorted((root / 'index/bm25').glob('*'))
            assert paths and any(p.name.startswith('segments_') for p in paths)
            resources['corpus'][corpus] = dict(path=str(root.resolve()),
                index_files={p.name: dict(size=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns,
                             sha256=file_hash(p) if p.name.startswith('segments_') else None) for p in paths if p.is_file()},
                chunk_count=len(list((root / 'chunk').glob('*.jsonl'))))
        reranker = Path('/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder')
        resources['reranker'] = {str(p): file_hash(p) for p in sorted(reranker.glob('*')) if p.is_file() and p.suffix in ('.json', '.bin', '.safetensors', '.txt')}
        atomic(resource_lock, resources)
    packages = {p: importlib.metadata.version(p) for p in ('torch', 'transformers', 'accelerate', 'pyserini', 'numpy', 'scipy', 'python-liquid', 'safetensors')}
    freeze(ROOT / 'configs/environment.json', dict(python=sys.version, executable=sys.executable, packages=packages))
    retrieval = dict(retriever_name='BM25+MedCPT', corpus_name='MedCorp',
                     corpus_path=str(MEDRAG / 'corpus'), reranker_path='/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder',
                     k=8, per_corpus_k=32, rrf_k=100, bm25_k1=.9, bm25_b=.4, context_length=30000,
                     corpus_version=digest(resources['corpus']), reranker_version=digest(resources['reranker']),
                     protocol='v5_full_medcorp_plus_required_evidence_20260911')
    for method, model in resources['models'].items():
        layers = json.loads((Path(model['path']) / 'config.json').read_text())['num_hidden_layers']
        device_map = {'model.embed_tokens': 0, **{f'model.layers.{i}': int(i >= layers // 2) for i in range(layers)}, 'model.norm': 1, 'lm_head': 1}
        config = dict(method=method, method_version='iterative-v1', model_id=model['id'], model_path=model['path'],
                      weight_id=model['weight_id'], tokenizer_id=model['tokenizer_id'], dtype='bfloat16',
                      engine='transformers', environment=packages, device_map=device_map,
                      seed=42, temperature=.7, top_p=1.0, top_k=0, max_length=131072,
                      chat_template_kwargs={'enable_thinking': False} if method == 'tcrag' else {},
                      transport_retries=2, retry_backoff_seconds=[1, 2], format_repairs=1,
                      budgets=dict(query=1024, parse=1024, qa=1024, action=2048, final=2048, format=2048),
                      retrieval=retrieval, retrieval_cache=str(ROOT / 'runs/retrieval_cache'),
                      n_rounds=4, n_queries=3, max_loop=8, topK=4, sigma=1.2,
                      entropy_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32',
                      entropy_span='pinned_upstream_exact_token_suffix',
                      evidence_protocol='v5_full_medcorp_plus_required_evidence_20260911')
        if method == 'tcrag':
            config['rope_scaling'] = dict(rope_type='yarn', factor=4.0, original_max_position_embeddings=32768)
        freeze(ROOT / 'configs' / (method + '.json'), config)
    print('Resource identities and two configurations frozen.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--resources', action='store_true')
    args = p.parse_args()
    lock_resources() if args.resources else prepare()
