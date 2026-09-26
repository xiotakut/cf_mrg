"""One closed M5 db06 run -> disjoint GPU2 plus authorized resource shards.

No model, grader, STOP, process termination or source-SQL write. Existing
terminal outputs stay in their original run. GPU2 receives only complete
callback prefixes as zero-physical replay rows; added GPUs receive untouched inputs.
"""
import argparse
from collections import OrderedDict
from copy import deepcopy
import fcntl
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

WORK = Path('/home/data3/txy')
sys.path.insert(0, str(WORK))
from cf_moa.contracts import ModelResult, digest
from cf_moa.evaluation.journal import RunJournal, serialized

DB06 = 'db06c973db607a3073cc669cc184ccb26d629abf219f20219ed8f47f659c0a47'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def validate_gpus(gpus):
    gpus = tuple(gpus)
    if len(gpus) < 2 or len(set(gpus)) != len(gpus) or gpus[0] != 2 or not set(gpus) <= {1, 2, 3}:
        raise ValueError('Provide GPU2 first plus distinct authorized GPU1/GPU3; capacity is checked separately')
    return gpus


def partition_tasks(local_plan, terminal, touched, gpus=(2, 3)):
    """Original-order input round robin only; touched unfinished inputs stay GPU2."""
    gpus = validate_gpus(gpus)
    selected = local_plan['selected_task_ids']
    declared = {t['task_id']: t for t in local_plan['protocol']['methods']['M5']['tasks']}
    if len(selected) != len(set(selected)) or not set(terminal) <= set(selected) or not set(touched) <= set(selected):
        raise ValueError('Source task identities are not a subset of the bound selected plan')
    tasks = [declared[k] for k in selected]
    if set(local_plan['selected_input_ids']) != {t['request_id'] for t in tasks}:
        raise ValueError('Selected input and task scope differ')
    touched_inputs = {declared[k]['request_id'] for k in set(touched) | set(terminal)}
    remaining = [t for t in tasks if t['task_id'] not in terminal]
    unfinished = list(dict.fromkeys(t['request_id'] for t in remaining))
    untouched = [rid for rid in unfinished if rid not in touched_inputs]
    allocation = {rid: 2 for rid in unfinished if rid in touched_inputs}
    allocation.update({rid: gpus[i % len(gpus)] for i, rid in enumerate(untouched)})
    shards = {gpu: [t for t in remaining if allocation[t['request_id']] == gpu] for gpu in gpus}
    allocated = [t['task_id'] for tasks in shards.values() for t in tasks]
    if len(allocated) != len(set(allocated)) or set(allocated) & set(terminal) or set(allocated) | set(terminal) != set(selected):
        raise ValueError('Resource shards must be disjoint and exhaustive with old terminal outputs')
    return shards, dict(original_tasks=len(selected), old_terminal_tasks=len(terminal),
        remaining_tasks=len(remaining), touched_unfinished_inputs=sum(r in touched_inputs for r in unfinished),
        untouched_remaining_inputs=len(untouched),
        shard_task_counts={str(gpu):len(values) for gpu,values in shards.items()},
        shard_input_counts={str(gpu):len({t['request_id'] for t in values}) for gpu,values in shards.items()},
        selected_task_ids_sha256=digest(selected), terminal_task_ids_sha256=digest(sorted(terminal)),
        remaining_task_ids_sha256=digest([t['task_id'] for t in remaining]),
        disjoint=True, exhaustive=True,
        gpu_order=list(gpus), partial_prefix_gpu=2, allocation='Touched unfinished inputs GPU2; untouched input order round robin across gpu_order; no gold, score or source-label selection')


def replay_callback(row, source_ref):
    """Keep exact request and ordinal; original live usage is a source event."""
    if row['status'] != 'complete' or row['result'] is None or row['finished'] is None:
        raise ValueError('An unfinished task may inherit only complete durable callback prefixes')
    saved = json.loads(row['result'])
    physical = json.loads(row['physical']) if row['physical'] is not None else None
    result = ModelResult(saved['value'], saved['events'])
    if len(result.events) != 1 or result.events[0]['input_tokens'] != row['reserved_tokens']:
        raise ValueError('Saved callback has inconsistent event/token evidence')
    if physical is None or any('event' not in e for e in physical):
        raise ValueError('Original physical submission evidence is incomplete')
    if result.events[0]['mode'] == 'live' and (len(physical) != 1 or physical[0]['event'] != result.events[0]):
        raise ValueError('Original live event and physical event differ')
    reference = dict(source_ref, request_id=row['request_id'], ordinal=row['ordinal'],
        request_hash=digest(json.loads(row['request'])), result_hash=digest(saved),
        source_physical_hash=digest(physical), new_physical_requests=0)
    events = deepcopy(result.events)
    for event in events:
        original = deepcopy(event)
        event.update(mode='replay', elapsed_seconds=0., original_event=original,
            recovery='closed_partial_run_exact_prefix_transfer', source_reference=reference)
    now = time.time()
    return (row['request_id'], row['ordinal'], row['request'], row['reserved_tokens'],
            'cross_run_replay', 'complete', serialized(dict(value=result.value, events=events)),
            '[]', None, now, now)


def local_for_shard(old, protocol, tasks):
    """Match unmodified db06.execute's exact local-plan construction."""
    grouped = OrderedDict()
    for task in tasks:
        grouped.setdefault(task['request_id'], []).append(task)
    return dict(protocol=protocol, method='M5', mode='live_batched', role='readout',
        batch_size=old['batch_size'], max_inputs=None,
        scheduler_source=deepcopy(old['scheduler_source']), selected_input_ids=list(grouped),
        selected_task_ids=[t['task_id'] for values in grouped.values() for t in values])


def prepare(source_run, output, gpus=(2, 3)):
    gpus = validate_gpus(gpus)
    source_run, output = Path(source_run).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('New resource migration must use a new destination directory')
    status = json.loads((source_run/'status.json').read_text())
    supervisor = json.loads((source_run/'supervisor_result.json').read_text())
    if status.get('status') != 'stopped_by_request' or supervisor.get('exit_code') != 1:
        raise ValueError('Require original normal STOP closure, not success or systemic failure')
    if status.get('first_systemic_error') or status.get('cost', {}).get('unresolved_model_usage') != 0:
        raise ValueError('Cannot migrate unknown/systemically failed original work')
    source = source_run/'journal.sqlite3'
    # The original runner holds an exclusive lock until export and engine close.
    # This shared lock both proves closure and prevents an accidental old resume.
    with (source_run/'run.lock').open('rb') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        wal = Path(str(source)+'-wal')
        if wal.exists() and wal.stat().st_size:
            raise ValueError('Source must be ended and checkpointed; do not ignore WAL')
        source_ref = dict(journal=str(source), journal_sha256=sha(source),
            source_status='stopped_by_request', source_status_sha256=sha(source_run/'status.json'),
            source_supervisor_sha256=sha(source_run/'supervisor_result.json'))
        db = sqlite3.connect(source.as_uri()+'?mode=ro&immutable=1', uri=True)
        db.row_factory = sqlite3.Row
        try:
            old = json.loads(db.execute("SELECT value FROM meta WHERE key='plan'").fetchone()[0])
            if old.get('method') != 'M5' or old.get('role') != 'readout' or old.get('mode') != 'live_batched':
                raise ValueError('Only the fixed M5 readout transfer is authorized by this helper')
            if old['scheduler_source']['sha256'] != DB06 or sha(old['scheduler_source']['path']) != DB06:
                raise ValueError('Keep the actual original db06 scheduler unchanged')
            for path, expected in old['protocol']['code_sources'].items():
                if sha(path) != expected:
                    raise ValueError('Bound original model/control source changed: '+path)
            if db.execute("SELECT 1 FROM meta WHERE key='first_error'").fetchone():
                raise ValueError('Original source has first_error; do not reinterpret it as normal STOP')
            if db.execute("SELECT COUNT(*) FROM calls WHERE status='started' OR finished IS NULL").fetchone()[0]:
                raise ValueError('Original source still has unclosed calls')
            if db.execute("""SELECT COUNT(*) FROM calls c WHERE
                    (c.phase='submitted' AND c.physical IS NULL) OR EXISTS (
                    SELECT 1 FROM json_each(c.physical) p WHERE
                    json_type(p.value,'$.event') IS NULL AND
                    COALESCE(json_extract(p.value,'$.submission_state'),'')!='not_submitted')""").fetchone()[0]:
                raise ValueError('Original SQL still has an unknown physical submission')
            identities = {r[0]: json.loads(r[1]) for r in db.execute('SELECT request_id,record FROM outputs')}
            terminal = set(identities)
            if any(r.get('status') not in ('complete','completed','failed','unavailable','error') or r.get('method') != 'M5' for r in identities.values()):
                raise ValueError('Source terminal output status/backbone mismatch')
            touched = {r[0] for r in db.execute('SELECT DISTINCT request_id FROM calls')}
            shards, proof = partition_tasks(old, terminal, touched, gpus)
            selected = old['protocol']['methods']['M5']
            for field in ('inputs', 'saved_f_proposals', 'saved_bases'):
                if field in selected and sha(selected[field]) != selected[field+'_sha256']:
                    raise ValueError('Original input/cache binding changed')
            output.mkdir(parents=True)
            prepared = []
            for gpu, tasks in shards.items():
                folder=output/f'gpu{gpu}';folder.mkdir()
                ids={t['request_id'] for t in tasks}; keys={t['task_id'] for t in tasks}
                cached={}
                if selected.get('saved_f_proposals'):
                    for line in Path(selected['saved_f_proposals']).open():
                        row=json.loads(line)
                        if row['request_id'] in ids:cached[row['request_id']]=row.get('proposal',row.get('result',row))
                for record in identities.values():
                    rid=record['request_id']; proposal=(record.get('result') or {}).get('f_proposal')
                    if rid not in ids:continue
                    if proposal is not None:
                        if rid in cached and digest(cached[rid]) != digest(proposal):
                            raise ValueError('Same-input F cache differs from actual source F')
                        cached[rid]=proposal
                    elif record['status'] in ('failed','error') and rid not in cached:
                        raise ValueError('A failed shared head cannot be regenerated by a remaining arm')
                cache=folder/'saved_f_proposals.jsonl'
                cache.write_text(''.join(serialized(dict(request_id=rid,proposal=value))+'\n' for rid,value in cached.items()))
                protocol=deepcopy(old['protocol'])
                protocol['allowed_gpus']=[gpu]
                protocol['methods']['M5']['tasks']=tasks
                protocol['methods']['M5'].update(saved_f_proposals=str(cache),saved_f_proposals_sha256=sha(cache))
                protocol['parallel_resource_shard']=dict(source_ref,gpu=gpu,original_scheduler_sha256=DB06,
                    method_profile_budget_prompt_unchanged=True,partition=proof)
                write(folder/'plan.json',protocol)
                local=local_for_shard(old,protocol,tasks)
                count=0; task_counts={}
                if gpu == 2:
                    run=folder/'runs/m5';run.mkdir(parents=True)
                    journal=RunJournal(run/'journal.sqlite3',local)
                    try:
                        for task in tasks:
                            key=task['task_id']
                            rows=list(db.execute('SELECT * FROM calls WHERE request_id=? ORDER BY ordinal',(key,)))
                            if [r['ordinal'] for r in rows] != list(range(len(rows))):
                                raise ValueError('Saved unfinished callback ordinals are not a prefix')
                            for row in rows:
                                with journal.db:journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',replay_callback(row,source_ref))
                            if rows:task_counts[key]=len(rows)
                            count+=len(rows)
                        with journal.db:journal.db.execute('INSERT INTO meta VALUES (?,?)',('partial_prefix_transfer',serialized(dict(source_ref,callback_rows=count))))
                    finally:journal.db.close()
                    write(run/'plan.json',local)
                elif keys & touched:
                    raise ValueError('An added GPU cannot receive a previously touched task')
                prepared.append(dict(gpu=gpu,plan=str(folder/'plan.json'),plan_sha256=sha(folder/'plan.json'),
                    output=str(folder/'runs/m5'),tasks=len(tasks),inputs=len(ids),cached_F_inputs=len(cached),
                    inherited_callback_rows=count,inherited_task_callback_counts=task_counts,
                    new_physical_requests_from_transfer=0))
            receipt=dict(status='resource_shards_prepared_not_launched',source=source_ref,partition=proof,
                shards=prepared,new_model_calls=0,new_grader_calls=0,source_SQL_unchanged=sha(source)==source_ref['journal_sha256'],
                cost_policy='Old physical cost belongs to the old journal only. New inherited callbacks have physical=[] and replay events. db06 submission_attempts includes these rows; do not call it newly sent requests.')
            write(output/'transfer_receipt.json',receipt)
            return receipt
        finally:db.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-run',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--gpus', required=True, type=int, nargs='+', help='GPU2 first, then authorized extra GPU(s)')
    args=parser.parse_args()
    print(json.dumps(prepare(args.source_run,args.output,args.gpus),ensure_ascii=False))
