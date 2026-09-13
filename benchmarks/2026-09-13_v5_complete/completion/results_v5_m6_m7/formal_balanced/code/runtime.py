"""Atomic stage receipts, bounded transport retries, and local step replay."""
import json
import time
from pathlib import Path
from common import atomic, digest


class RequestFailure(RuntimeError):
    pass


class Session:
    def __init__(self, root, config, model, retriever, batch_group=None):
        self.root, self.config = Path(root), config
        self.model, self.retriever = model, retriever
        self.batch_group = batch_group
        self.trace, self.receipts, self.reused = [], {}, 0

    def event(self, kind, **values):
        row = dict(index=len(self.trace), kind=kind, **values)
        atomic(self.root / 'events' / f'{len(self.trace):04d}.json', row)
        self.trace.append(row)

    def request(self, spec, operation):
        key = digest(spec)
        path = self.root / 'requests' / f'{key}.json'
        if path.exists():
            record = json.loads(path.read_text())
            if record['spec'] != spec:
                raise ValueError('request_cache_mismatch')
            self.receipts[key] = record
            self.reused += 1
            if record['status'] == 'ok':
                return record['result']
            raise RequestFailure(record['error'])
        # Attempts persist before sending. A lost response consumes an attempt;
        # it is never relabelled as a successful cached stage.
        attempt_dir = self.root / 'attempts' / key
        attempts = sorted(attempt_dir.glob('*.json')) if attempt_dir.exists() else []
        for ap in attempts:
            receipt = json.loads(ap.read_text())
            if receipt['status'] == 'ok':
                record = dict(spec=spec, status='ok', result=receipt['result'], attempts=receipt['attempt'] + 1)
                atomic(path, record)
                self.receipts[key] = record
                self.reused += 1
                return receipt['result']
        max_attempts = self.config['transport_retries'] + 1
        for attempt in range(len(attempts), max_attempts):
            receipt = dict(spec=spec, attempt=attempt, started=time.time(), status='in_flight')
            ap = attempt_dir / f'{attempt:02d}.json'
            atomic(ap, receipt)
            try:
                result = operation()
            except Exception as e:
                error = f'{type(e).__name__}: {e}'
                receipt.update(status='failed', error=error, seconds=time.time() - receipt['started'])
                atomic(ap, receipt)
                # Model/parse/OOM/config failures are not transport retries.
                transport = isinstance(e, (ConnectionError, TimeoutError))
                if not transport or attempt + 1 == max_attempts:
                    record = dict(spec=spec, status='failed', error=error, attempts=attempt + 1)
                    atomic(path, record)
                    self.receipts[key] = record
                    raise RequestFailure(error) from e
                time.sleep(self.config['retry_backoff_seconds'][attempt])
            else:
                receipt.update(status='ok', seconds=time.time() - receipt['started'], result=result)
                atomic(ap, receipt)
                record = dict(spec=spec, status='ok', result=result, attempts=attempt + 1)
                atomic(path, record)
                self.receipts[key] = record
                return result
        # The last attempt may have committed its receipt before interruption.
        if attempts:
            last = json.loads(attempts[-1].read_text())
            if last['status'] == 'ok':
                record = dict(spec=spec, status='ok', result=last['result'], attempts=len(attempts))
                atomic(path, record)
                self.receipts[key] = record
                return last['result']
        record = dict(spec=spec, status='failed', error='interrupted_attempt_budget_exhausted', attempts=len(attempts))
        atomic(path, record)
        self.receipts[key] = record
        raise RequestFailure(record['error'])

    def call_many(self, stage, messages, entropy=False):
        limit = self.config['budgets'][stage.split('/')[0]]
        # Run location, manifest membership and code receipts are provenance,
        # not sampling inputs. A new run ID must not silently change its seed.
        semantic_config = {k: v for k, v in self.config.items() if k not in
            ('run_id', 'code_hashes', 'inputs_hash', 'input_path', 'physical_gpu_selection')}
        spec = dict(kind='llm', stage=stage, messages=messages, max_tokens=limit,
                    entropy=entropy, config_hash=digest(semantic_config), config=semantic_config)
        seed = (self.config['seed'] + int(digest(spec)[:8], 16)) % (2 ** 31)
        spec['seed'] = seed
        return self.request(spec, lambda: self.model.generate(messages, limit, seed, entropy=entropy,
                            batch_group=(self.batch_group, stage.split('/')[0])))

    def call(self, stage, messages, entropy=False):
        return self.call_many(stage, [messages], entropy)[0]

    def retrieve(self, stage, query):
        spec = dict(kind='retrieval', stage=stage, query=query, retrieval=self.config['retrieval'])
        # Shared retrieval cache has its own content-addressed key; stages can
        # reuse the same exact query without sharing final answers or histories.
        shared = Path(self.config['retrieval_cache']) / (digest(dict(query=query, retrieval=self.config['retrieval'])) + '.json')

        def perform():
            if shared.exists():
                value = json.loads(shared.read_text())
                value['cache_hit'] = True
                return value
            started = time.time()
            result = self.retriever.retrieve(query)
            if len(result['documents']) != len(result['scores']):
                raise ValueError('retrieval_document_score_mismatch')
            docs = [dict(d, rank=i + 1, score=float(s), content_hash=digest(d))
                    for i, (d, s) in enumerate(zip(result['documents'], result['scores']))]
            value = dict(query=query, documents=docs, seconds=time.time() - started,
                         status='hits' if docs else 'no_hits', cache_hit=False,
                         retrieval=self.config['retrieval'])
            atomic(shared, value)
            return value
        value = self.request(spec, perform)
        self.event('retrieval', stage=stage, **value)
        return value['documents']

    def context(self, documents, stage):
        # Keep native problem/evidence intact; only extra retrieved context clips.
        tok, budget = self.model.tokenizer, self.config['retrieval']['context_length']
        remaining, used, truncation = budget, [], []
        for d in documents:
            rendered = f'Document [{d["rank"]}] (Title: {d["title"]}) {d["content"]}'
            ids = tok.encode(rendered, add_special_tokens=False)
            take = max(0, min(remaining, len(ids)))
            fragment = rendered if take == len(ids) else tok.decode(ids[:take])
            if fragment:
                used.append(fragment)
            truncation.append(dict(document_id=d.get('id'), content_hash=d['content_hash'],
                                   input_tokens=len(ids), consumed_tokens=take,
                                   truncated_tokens=len(ids) - take, consumed_text=fragment))
            remaining -= take
        text = '\n'.join(used)
        self.event('retrieval_context', stage=stage, documents=truncation, text=text)
        return text

    def costs(self):
        llm, retrievals = [], []
        for record in self.receipts.values():
            if record['status'] != 'ok':
                continue
            (llm if record['spec']['kind'] == 'llm' else retrievals).append(record)
        generations = [v for r in llm for v in r['result']]
        return dict(llm_requests=len(generations), backend_generate_calls=len(llm),
                    prompt_tokens=sum(r['prompt_tokens'] for r in generations),
                    completion_tokens=sum(r['completion_tokens'] for r in generations),
                    retrieval_requests=len(retrievals),
                    retrieval_no_hits=sum(r['result']['status'] == 'no_hits' for r in retrievals),
                    generated_truncations=sum(r['finish_reason'] == 'length' for r in generations),
                    scoring_forward_calls=sum(r.get('scoring_forward_calls', 0) for r in generations),
                    backend_seconds=sum(v['batch_seconds'] for r in llm for v in r['result']),
                    attempt_count=sum(r['attempts'] for r in self.receipts.values()),
                    failed_requests=sum(r['status'] != 'ok' for r in self.receipts.values()),
                    retry_count=sum(r['attempts'] - 1 for r in self.receipts.values()))
