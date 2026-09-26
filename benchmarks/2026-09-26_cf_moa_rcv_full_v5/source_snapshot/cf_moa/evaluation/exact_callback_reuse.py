"""Read-only, source-bound reuse of complete inference callbacks.

This helper never imports a model, reads evaluation files, selects an answer,
or writes a destination journal. A caller must still rerun the current-pool
parser/normalization/tie/whole-response assembly after receiving a replay.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3

from cf_moa.contracts import ModelResult, digest
from cf_moa.evaluation.journal import JournalConflict, UnresolvedCall


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def _stat(path):
    value = Path(path).stat()
    # Some workspace mounts expose coarse/cached timestamps. A same-size SQL
    # transaction may therefore leave stat metadata apparently unchanged; the
    # SQLite header contains its file-change counter and schema/version fields.
    with Path(path).open('rb') as stream:
        header = stream.read(100)
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns, header


def _request_digest(request):
    # Unlike a sorted-key content hash, keep nested schema/property insertion
    # order as well as message/code order. No normalization drops request fields.
    text = json.dumps(request, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class CompletedJournal:
    path: str
    sha256: str
    method: str
    backend_protocol_hash: str
    # Optional when selected_task_ids or protocol.methods[method].tasks/samples
    # are already in the inference SQL plan. Never guess input IDs from paths.
    expected_task_ids: tuple[str, ...] | None = None


@dataclass
class CallbackReplay:
    result: ModelResult
    reserved_tokens: int
    source_ref: dict
    # The destination must persist this empty list, NOT original live physical
    # records. Original token costs remain in the replay event/source reference.
    phase: str = 'cross_run_replay'

    def journal_payload(self):
        return dict(phase=self.phase, status='complete', reserved_tokens=self.reserved_tokens,
                    result=dict(value=deepcopy(self.result.value), events=deepcopy(self.result.events)),
                    physical=[], reused_source=deepcopy(self.source_ref))


def _planned_tasks(plan, method):
    if 'selected_task_ids' in plan:
        return plan['selected_task_ids']
    protocol = plan.get('protocol', plan)
    selected = protocol.get('methods', {}).get(method, {})
    if 'tasks' in selected:
        return [row['task_id'] for row in selected['tasks']]
    if 'samples' in selected and all('request_id' in s for s in selected['samples']):
        arms = selected.get('arms', protocol.get('arms', []))
        if arms:
            return [s['request_id']+':'+arm for s in selected['samples'] for arm in arms]
    return None


class ExactCallbackReuse:
    """Index declared completed journals in source order, then earliest SQL row.

    backend_protocol_hash is a frozen source-descriptor attestation, preferably
    also stored in protocol.exact_callback_backend_protocol_hash in source SQL.
    It must cover renderer/tokenizer/chat-template/guidance/interpreter identity,
    not a hash of the current file guessed for an older run. The destination
    supplies its own hash on lookup; a different protocol is a normal miss.
    """
    def __init__(self, sources):
        self.sources = []
        self.index = {}
        self.stats = dict(complete_callbacks_indexed=0, duplicate_exact_callbacks=0,
                          failed_callbacks_skipped=0, hits=0, misses=0)
        try:
            for binding in sources:
                self._add(binding)
        except BaseException:
            self.close()
            raise

    def _check(self, source):
        path, binding = source['path'], source['binding']
        wal = Path(str(path)+'-wal')
        if wal.exists() and wal.stat().st_size:
            raise JournalConflict('Reuse requires an ended, checkpointed source journal: '+str(path))
        current = _stat(path)
        if current[-1] != source['stat'][-1]:
            raise JournalConflict('Bound reuse source changed (SQLite header): '+str(path))
        if current != source['stat']:
            if _sha(path) != binding.sha256:
                raise JournalConflict('Bound reuse source changed: '+str(path))
            source['stat'] = current

    def _add(self, binding):
        if not isinstance(binding, CompletedJournal):
            raise TypeError('Use an explicit CompletedJournal source binding')
        if binding.method not in ('M4', 'M5') or not binding.backend_protocol_hash:
            raise JournalConflict('Source backbone and frozen backend protocol must be declared')
        path = Path(binding.path).resolve()
        wal = Path(str(path)+'-wal')
        if wal.exists() and wal.stat().st_size:
            raise JournalConflict('Source WAL is not empty; finish/checkpoint source first: '+str(path))
        if _sha(path) != binding.sha256:
            raise JournalConflict('Bound reuse source hash differs: '+str(path))
        # immutable avoids creating/updating source -shm state. Nonempty WAL is
        # rejected above rather than silently omitting its durable contents.
        db = sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1', uri=True)
        db.execute('PRAGMA query_only=ON')
        source = dict(path=path, binding=binding, db=db, stat=_stat(path))
        self.sources.append(source)
        stored = db.execute("SELECT value FROM meta WHERE key='plan'").fetchone()
        if stored is None:
            raise JournalConflict('Source inference plan missing')
        plan = json.loads(stored[0])
        if plan.get('method') != binding.method:
            raise JournalConflict('Source SQL backbone differs from binding')
        declared = plan.get('protocol', plan).get('exact_callback_backend_protocol_hash')
        if declared is not None and declared != binding.backend_protocol_hash:
            raise JournalConflict('Source SQL backend protocol differs from binding')
        planned = binding.expected_task_ids or _planned_tasks(plan, binding.method)
        if not planned or len(planned) != len(set(planned)):
            raise JournalConflict('Bind the complete source task list; cannot establish completed scope')
        # Read ONLY output identity/status columns through SQLite JSON projection.
        # Never load a final native answer or an old candidate pool from outputs.
        identities = {}
        for task, method, input_hash, status in db.execute(
                "SELECT request_id,json_extract(record,'$.method'),"
                "json_extract(record,'$.input_hash'),json_extract(record,'$.status') FROM outputs"):
            if method != binding.method or not input_hash:
                raise JournalConflict('Source output lacks a bound input/backbone identity')
            if status not in ('complete', 'completed', 'unavailable', 'failed', 'error'):
                raise JournalConflict('Source contains nonterminal input output')
            identities[task] = input_hash
        if set(identities) != set(planned):
            raise JournalConflict('Source task scope is not fully ended')
        query = 'SELECT rowid,request_id,ordinal,request,reserved_tokens,status,result,physical,phase,finished FROM calls ORDER BY rowid'
        for rowid, task, ordinal, raw, tokens, status, result, physical, phase, finished in db.execute(query):
            if task not in identities:
                raise JournalConflict('Callback has no terminal source input identity')
            entries = json.loads(physical) if physical is not None else None
            uncertain = (entries is None and phase == 'submitted') or any(
                'event' not in entry and entry.get('submission_state') != 'not_submitted'
                for entry in entries or [])
            if status == 'started' or uncertain:
                raise UnresolvedCall('Source has an uncertain submission; it is not a cache miss: '+task)
            if status != 'complete':
                self.stats['failed_callbacks_skipped'] += 1
                continue
            if result is None or finished is None:
                raise JournalConflict('Complete callback lacks a durable result/finish record')
            request, saved = json.loads(raw), json.loads(result)
            checked = ModelResult(saved['value'], saved['events'])
            if len(checked.events) != 1 or checked.events[0]['input_tokens'] != tokens:
                raise JournalConflict('Source callback usage/reservation is inconsistent')
            event = checked.events[0]
            key = (binding.method, event['config_hash'], identities[task], _request_digest(request),
                   binding.backend_protocol_hash)
            pointer = dict(source=len(self.sources)-1, rowid=rowid, request_id=task, ordinal=ordinal,
                           input_hash=identities[task], request_hash=_request_digest(request),
                           result_hash=digest(saved), physical_hash=digest(entries),
                           config_hash=event['config_hash'], model=event['model'])
            if key in self.index:
                self.stats['duplicate_exact_callbacks'] += 1
            else:
                self.index[key] = pointer
            self.stats['complete_callbacks_indexed'] += 1
        self._check(source)

    def lookup(self, *, method, config_hash, input_hash, request, backend_protocol_hash,
               physical_request=None):
        """Return one exact callback replay or None; never choose a native answer.

        physical_request optionally checks the destination's already-rendered
        ingress against the stored physical request. Even when omitted, the
        physical ingress hash and complete source event are bound in the receipt.
        """
        for source in self.sources:
            self._check(source)
        key = (method, config_hash, input_hash, _request_digest(request), backend_protocol_hash)
        pointer = self.index.get(key)
        if pointer is None:
            self.stats['misses'] += 1
            return None
        source = self.sources[pointer['source']]
        row = source['db'].execute(
            'SELECT request,reserved_tokens,status,result,physical FROM calls WHERE rowid=?',
            (pointer['rowid'],)).fetchone()
        saved_request = json.loads(row[0])
        saved = json.loads(row[3])
        entries = json.loads(row[4]) if row[4] is not None else None
        # Digest lookup is followed by a full field/value comparison. List and
        # message order, schema, seed and singleton allowed_codes are untouched.
        if row[2] != 'complete' or saved_request != request or _request_digest(saved_request) != pointer['request_hash']:
            raise JournalConflict('Complete source request changed after indexing')
        if digest(saved) != pointer['result_hash'] or digest(entries) != pointer['physical_hash']:
            raise JournalConflict('Complete source callback changed after indexing')
        if physical_request is not None:
            actual = [entry.get('request') for entry in entries or [] if 'request' in entry]
            if len(actual) != 1 or actual[0] != physical_request or _request_digest(actual[0]) != _request_digest(physical_request):
                raise JournalConflict('Rendered physical ingress differs from saved source')
        reference = dict(journal=str(source['path']), journal_sha256=source['binding'].sha256,
            method=method, config_hash=config_hash, input_hash=input_hash,
            backend_protocol_hash=backend_protocol_hash, request_id=pointer['request_id'],
            ordinal=pointer['ordinal'], rowid=pointer['rowid'], request_hash=pointer['request_hash'],
            result_hash=pointer['result_hash'], source_physical_hash=pointer['physical_hash'],
            selection='declared source order then earliest SQL row', new_physical_requests=0)
        events = deepcopy(saved['events'])
        for event in events:
            original = deepcopy(event)
            event.update(mode='replay', elapsed_seconds=0.0, original_event=original,
                         recovery='exact_cross_run_complete_callback', source_reference=deepcopy(reference))
        self.stats['hits'] += 1
        return CallbackReplay(ModelResult(deepcopy(saved['value']), events), row[1], reference)

    def close(self):
        for source in self.sources:
            source['db'].close()
        self.sources = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
