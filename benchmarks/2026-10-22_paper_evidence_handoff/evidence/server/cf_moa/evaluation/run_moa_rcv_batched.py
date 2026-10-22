"""Batch only ready callbacks from the unchanged per-input RCV computation.

Each input has one frontier. Its existing Python operation is resumed by exact
SQL response replay until the next missing callback. That callback suspends via
BaseException, which cannot be mistaken for an ordinary model failure. No later
F draw is requested unless the original early-stop code actually reaches it.
"""
import argparse
from collections import Counter, OrderedDict, deque
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import time

from cf_moa.contracts import ModelResult, digest
from cf_moa.controller import moa_rcv, strong_legacy
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.effect_first_runner import ResearchJournal
from cf_moa.evaluation.incremental_runner import CachedTokenBackend
from cf_moa.evaluation.journal import JournalConflict, UnresolvedCall, serialized
from cf_moa.evaluation.resources import admission
from cf_moa.evaluation.run_moa_rcv import (ARM_ALIASES, _initial_native, load_plan,
    selected_profile, stream_cost, stream_export)
from cf_moa.tools.adopted import sha256
from cf_moa.tools.f_pool_replica import session_for_plan


class NeedCallback(BaseException):
    def __init__(self, task_id, ordinal, request, tokens):
        self.task_id, self.ordinal = task_id, ordinal
        self.request, self.tokens = deepcopy(request), tokens


class SavedItemFailure(RuntimeError):
    """A known failed callback is never submitted again during planning."""


class FrontierBackend:
    def __init__(self, journal, runtime):
        self.journal, self.runtime = journal, runtime
        self.request_id, self.ordinal = None, 0

    def begin_item(self, task_id):
        self.request_id, self.ordinal = task_id, 0

    def row(self, request):
        self.journal.ensure_running()
        row = self.journal.lookup(self.request_id, self.ordinal)
        if row and digest(json.loads(row['request'])) != digest(request):
            raise JournalConflict('Scheduled replay request changed at ' + self.request_id + ':' + str(self.ordinal))
        if row and row['status'] == 'started':
            raise UnresolvedCall('Unknown earlier batch submission; automatic resampling prohibited')
        return row

    def count_tokens(self, request):
        row = self.row(request)
        return row['reserved_tokens'] if row else self.runtime().count_tokens(request)

    def __call__(self, request):
        row = self.row(request)
        if row is None:
            raise NeedCallback(self.request_id, self.ordinal, request, self.count_tokens(request))
        self.ordinal += 1
        if row['status'] == 'failed':
            raise SavedItemFailure(row['error'])
        saved = json.loads(row['result'])
        events = deepcopy(saved['events'])
        # These are THIS run's real physical events, counted once in SQL.
        # Rewalking Python does not add an event or another model request.
        for event in events:
            event['scheduled_response_reuse'] = True
        return ModelResult(saved['value'], events)

    def finish_item(self):
        if self.ordinal != self.journal.count(self.request_id):
            raise JournalConflict('Operation ended before consuming its saved physical callbacks')


def submit_batch(pending, runtime, journal):
    """Persist reservations before transport and every observed physical result."""
    ready = []
    for need in pending:
        now = time.time()
        with journal.db:
            journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (need.task_id, need.ordinal, serialized(need.request), need.tokens,
                 'validating', 'started', None, None, None, now, None))
        try:
            runtime.preflight(need.request)
        except Exception as error:
            detail = dict(type=type(error).__name__, message=str(error))
            with journal.db:
                journal.db.execute("UPDATE calls SET status='failed',physical=?,error=?,finished=? "
                    'WHERE request_id=? AND ordinal=?',
                    (serialized([dict(submission_state='not_submitted', error=detail)]),
                     serialized(detail), time.time(), need.task_id, need.ordinal))
            journal.stop(need.task_id, error, need.ordinal)
        else:
            ready.append(need)
    if not ready or journal.first_error():
        return
    try:
        with journal.db:
            for need in ready:
                journal.db.execute("UPDATE calls SET phase='initializing' WHERE request_id=? AND ordinal=?",
                                   (need.task_id, need.ordinal))
        if runtime.llm is None:
            runtime.start()
    except Exception as error:
        with journal.db:
            for need in ready:
                journal.db.execute("UPDATE calls SET status='failed',physical='[]',error=?,finished=? "
                    'WHERE request_id=? AND ordinal=?',
                    (serialized(dict(type=type(error).__name__,message=str(error))),time.time(),need.task_id,need.ordinal))
        # Initialization belongs to the shared engine even if a provider uses
        # an unfamiliar exception name. Do not try it once per waiting input.
        journal.stop(ready[0].task_id, JournalConflict('Shared engine initialization failed: ' + str(error)), ready[0].ordinal)
        return
    with journal.db:
        for need in ready:
            journal.db.execute("UPDATE calls SET phase='submitted' WHERE request_id=? AND ordinal=?",
                               (need.task_id, need.ordinal))
    before = len(runtime.physical_calls)
    try:
        results = runtime.generate_batch([need.request for need in ready])
        physical = runtime.physical_calls[before:]
        if len(results) != len(ready) or len(physical) != len(ready):
            raise JournalConflict('Batch response/physical count mismatch')
        with journal.db:
            for need, result, actual in zip(ready, results, physical):
                if not isinstance(result, ModelResult) or len(result.events) != 1:
                    raise JournalConflict('Expected one actual physical result per ready callback')
                event = result.events[0]
                if event['input_tokens'] != need.tokens or event['output_tokens'] > need.request['max_tokens']:
                    raise JournalConflict('Batch token usage differs from the per-input reservation')
                journal.db.execute("UPDATE calls SET status='complete',result=?,physical=?,finished=? "
                    'WHERE request_id=? AND ordinal=?',
                    (serialized(dict(value=result.value,events=result.events)),serialized([actual]),
                     time.time(),need.task_id,need.ordinal))
    except Exception as error:
        physical = runtime.physical_calls[before:]
        with journal.db:
            for i, need in enumerate(ready):
                actual = [physical[i]] if i < len(physical) else None
                journal.db.execute("UPDATE calls SET status='failed',physical=?,error=?,finished=? "
                    'WHERE request_id=? AND ordinal=?',
                    (serialized(actual) if actual is not None else None,
                     serialized(dict(type=type(error).__name__, message=str(error))),
                     time.time(),need.task_id,need.ordinal))
        journal.stop(ready[0].task_id, JournalConflict('Failed or unknown batch submission; no automatic retry: ' + str(error)), ready[0].ordinal)
    finally:
        # Records are durable in SQLite. Do not retain the entire full-v5
        # history of token IDs/prompts in the live backend's Python list.
        del runtime.physical_calls[before:]


def execute(plan, selected, packets, pools, bases, tasks, method, role, output, gpu,
            *, runtime_factory=None, max_inputs=None, operation=moa_rcv.run):
    chosen = selected_profile(method, role)
    if role not in ('catalog', 'readout'):
        raise ValueError('This batch entry handles only the catalog/readout role')
    declared = plan.get('profiles', {}).get(method, {}).get(role)
    if declared is not None and declared != chosen.config:
        raise JournalConflict('Frozen role profile differs from actual adopted profile')
    batch_size = min(chosen.config['batch_size'], chosen.config['max_num_seqs'])
    grouped = OrderedDict()
    for task in tasks:
        if moa_rcv.profile_role(packets[task['request_id']]) == role:
            grouped.setdefault(task['request_id'], deque()).append(task)
    if max_inputs is not None:
        grouped = OrderedDict(list(grouped.items())[:max_inputs])
    selected_tasks = [task for local in grouped.values() for task in local]
    local_plan = dict(protocol=plan, method=method, mode='live_batched', role=role,
        batch_size=batch_size, max_inputs=max_inputs,
        scheduler_source=dict(path=str(Path(__file__).resolve()),sha256=sha256(__file__)),
        selected_input_ids=list(grouped), selected_task_ids=[t['task_id'] for t in selected_tasks])
    journal = ResearchJournal(output/'journal.sqlite3', local_plan,
                              resume=(output/'journal.sqlite3').exists())
    dump(output/'plan.json', local_plan)
    engine = None
    def runtime():
        nonlocal engine
        if engine is None:
            try:
                if runtime_factory is None:
                    resources = admission(chosen, role, gpu)
                    dump(output/'resource_admission.json', resources)
                    if not resources['ready']:
                        raise MemoryError('Insufficient authorized GPU for unchanged role profile')
                engine = runtime_factory(chosen) if runtime_factory else CachedTokenBackend(chosen)
            except Exception as error:
                raise JournalConflict('Shared backend initialization failed before submission: '
                    + type(error).__name__ + ': ' + str(error)) from error
        return engine
    backend = FrontierBackend(journal, runtime)
    waiting, active = deque(grouped), OrderedDict()
    failed_shared_sources = set()
    started = time.monotonic()
    batches = 0
    try:
        while (waiting or active) and not journal.first_error() and not (output/'STOP').exists():
            pending = []
            while waiting and len(active) < batch_size:
                rid = waiting.popleft()
                active[rid] = grouped[rid]
            for rid in list(active):
                remaining = active[rid]
                packet = packets[rid]
                while remaining and not journal.first_error():
                    task = remaining[0]
                    key = task['task_id']
                    old = journal.output(key)
                    if old is not None:
                        result = old.get('result', {})
                        if result.get('f_proposal') is not None:
                            pools[rid] = result['f_proposal']
                        if old['status'] == 'complete' and strong_legacy.select(packet)[0] != 'F':
                            bases[rid] = result
                        component = strong_legacy.select(packet)[0]
                        source_available = rid in pools if component == 'F' else rid in bases
                        if old['status'] == 'failed' and not source_available:
                            failed_shared_sources.add(rid)
                        remaining.popleft()
                        continue
                    backend.begin_item(key)
                    session = session_for_plan(packet, backend, plan)
                    before = time.monotonic()
                    try:
                        component, _ = strong_legacy.select(packet)
                        arm = ARM_ALIASES.get(task['arm'], task['arm'])
                        if rid in failed_shared_sources:
                            raise SavedItemFailure('Shared adopted head source failed; another arm must not execute that head again')
                        result = operation(packet, session, method=method, mode=arm,
                            seed=plan.get('verification_seed', 42),
                            saved_f_proposal=pools.get(rid),
                            saved_base=bases.get(rid) if component != 'F' else None,
                            **_initial_native(packet))
                        backend.finish_item()
                        if result['f_proposal'] is not None:
                            pools[rid] = result['f_proposal']
                        if component != 'F':
                            bases[rid] = result
                        record = dict(status='complete' if result['native_valid'] else 'unavailable', result=result)
                    except NeedCallback as need:
                        pending.append(need)
                        break
                    except Exception as error:
                        journal.stop(key, error, backend.ordinal)
                        component = strong_legacy.select(packet)[0]
                        source_available = rid in pools if component == 'F' else rid in bases
                        if not source_available:
                            failed_shared_sources.add(rid)
                        record = dict(status='failed', error_type=type(error).__name__, error=str(error),
                            result=dict(native_answer=None,native_valid=False,cost=session.cost_since()))
                    journal.save_output(key,dict(task_id=key,request_id=rid,method=method,
                        arm=ARM_ALIASES.get(task['arm'],task['arm']),input_hash=packet.input_hash,
                        elapsed_seconds=time.monotonic()-before,cost=session.cost_since(),
                        model_callbacks=session.calls,tool_callbacks=session.tools,
                        scheduling='exact_same_run_SQL_callback_continuations',**record))
                    remaining.popleft()
                if not remaining:
                    del active[rid]
                    pools.pop(rid,None)
                    bases.pop(rid,None)
            if pending and not journal.first_error():
                submit_batch(pending,runtime(),journal)
                batches += 1
            dump(output/'status.json',dict(status='running',role=role,planned=len(selected_tasks),
                completed=journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0],
                batches=batches,active_inputs=len(active),waiting_inputs=len(waiting),
                first_systemic_error=journal.first_error()))
        counts=Counter()
        for task in selected_tasks:
            row=journal.output(task['task_id'])
            counts[row['status'] if row else 'not_submitted']+=1
        status=dict(status='stopped_on_systemic_error' if journal.first_error() else
                    'stopped_by_request' if (output/'STOP').exists() else 'complete',
            mode='live_batched',role=role,planned=len(selected_tasks),inputs=len(grouped),
            complete=counts['complete'],unavailable=counts['unavailable'],failed=counts['failed'],
            not_submitted=counts['not_submitted'],batches=batches,batch_size=batch_size,
            first_systemic_error=journal.first_error(),cost=stream_cost(journal),
            elapsed_seconds=time.monotonic()-started,
            scope='declared role/input prefix of the frozen plan; not automatically complete full-v5',
            no_speculative_F_draws=True,ordinary_item_failure_stops_batch=False)
        dump(output/'status.json',status)
        return status
    finally:
        stream_export(journal,output)
        try:
            if engine is not None:
                engine.close()
        finally:
            journal.db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',required=True,type=Path)
    parser.add_argument('--method',required=True,choices=('M4','M5'))
    parser.add_argument('--role',required=True,choices=('catalog','readout'))
    parser.add_argument('--gpu',required=True,type=int)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--max-inputs',type=int)
    args=parser.parse_args()
    plan,selected,packets,pools,bases,tasks=load_plan(args.plan,args.method)
    if args.gpu not in plan.get('allowed_gpus',[]):
        raise ValueError('GPU is not authorized by the plan')
    visible=os.environ.get('CUDA_VISIBLE_DEVICES')
    if visible is not None and visible!=str(args.gpu):
        raise ValueError('CUDA binding differs from authorized GPU')
    if args.max_inputs is not None and args.max_inputs<=0:
        raise ValueError('A prefix must include at least one input')
    os.environ['CUDA_VISIBLE_DEVICES']=str(args.gpu)
    args.output.mkdir(parents=True,exist_ok=True)
    with (args.output/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        status=execute(plan,selected,packets,pools,bases,tasks,args.method,args.role,args.output,args.gpu,max_inputs=args.max_inputs)
    print(json.dumps(status,ensure_ascii=False),flush=True)
    if status['status']!='complete':
        raise SystemExit(1)


if __name__=='__main__':
    main()
