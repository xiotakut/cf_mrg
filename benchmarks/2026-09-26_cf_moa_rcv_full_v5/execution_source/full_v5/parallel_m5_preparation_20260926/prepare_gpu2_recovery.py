"""Prepare one separate GPU2 runtime recovery after zero-submission initialization failure.

No process/GPU/model actions. Original failure and all source SQL stay unchanged.
The original plan is copied byte-for-byte into a new directory solely so the
unchanged launcher can restore its holder in a fresh directory after this run.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
import fcntl
import json
from pathlib import Path
import sqlite3
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from partial_prefix_transfer import DB06, RunJournal, digest, local_for_shard, replay_callback, serialized, sha, write


def read_db(stack, run):
    lock=stack.enter_context((run/'run.lock').open('rb'))
    fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
    path=run/'journal.sqlite3'
    wal=Path(str(path)+'-wal')
    if wal.exists() and wal.stat().st_size:
        raise ValueError('Recovery sources must be closed/checkpointed, never a live WAL')
    db=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True)
    db.row_factory=sqlite3.Row
    stack.callback(db.close)
    return db


def validate_failure(status, supervisor, rows, expected_counts):
    if status.get('status')!='stopped_on_systemic_error' or supervisor.get('exit_code')!=1:
        raise ValueError('Only closed shared-engine initialization failure can use this recovery')
    first=status.get('first_systemic_error') or {}
    if first.get('error_category')!='infrastructure' or 'initialization failed' not in first.get('message',''):
        raise ValueError('This is not the bounded zero-submission initialization failure')
    cost=status['cost']
    if any(cost.get(k)!=0 for k in ('new_model_requests','physical_model_requests','unresolved_model_usage')):
        raise ValueError('A run with live or unknown model submissions cannot use this recovery')
    expected={(key,i) for key,count in expected_counts.items() for i in range(count)}
    prefixes={}
    for row in rows:
        if row['physical'] is None or json.loads(row['physical'])!=[] or row['finished'] is None:
            raise ValueError('Failed run must contain only finished zero-physical callback attempts')
        if row['status']=='complete':
            result=json.loads(row['result'])
            if row['phase']!='cross_run_replay' or any(e['mode']!='replay' for e in result['events']):
                raise ValueError('A completed callback was not an inherited prefix')
            prefixes[(row['request_id'],row['ordinal'])]=row
        elif row['status']!='failed' or row['phase']!='initializing':
            raise ValueError('Only preserved initialization failure attempts may be left behind')
    if set(prefixes)!=expected:
        raise ValueError('Inherited callback identities differ from original transfer receipt')
    return prefixes


def prepare(transfer_path, destination):
    transfer_path=Path(transfer_path).resolve();destination=Path(destination).resolve()
    transfer=json.loads(transfer_path.read_text())
    shard=next(x for x in transfer['shards'] if x['gpu']==2)
    plan_path=Path(shard['plan']);failed=Path(shard['output'])
    if destination.exists() or destination.name!='gpu2_recovery1' or destination.parent!=plan_path.parent.parent:
        raise ValueError('One fresh sibling gpu2_recovery1 directory is required; do not replace or loop retries')
    if sha(plan_path)!=shard['plan_sha256']:
        raise ValueError('Original GPU2 plan changed')
    status=json.loads((failed/'status.json').read_text())
    supervisor=json.loads((failed/'supervisor_result.json').read_text())
    if supervisor.get('plan_sha256')!=shard['plan_sha256']:
        raise ValueError('Failed run was not bound to the same unchanged plan')
    source_ref=deepcopy(transfer['source']);source=Path(source_ref['journal']).parent
    source_status=json.loads((source/'status.json').read_text())
    if source_status.get('status')!='stopped_by_request' or source_status.get('first_systemic_error'):
        raise ValueError('Original source must remain the original normal closed partial run')
    if sha(source/'status.json')!=source_ref['source_status_sha256'] or sha(source/'supervisor_result.json')!=source_ref['source_supervisor_sha256']:
        raise ValueError('Original STOP evidence changed')
    with ExitStack() as stack:
        olddb=read_db(stack,source);faildb=read_db(stack,failed)
        if sha(source/'journal.sqlite3')!=source_ref['journal_sha256']:
            raise ValueError('Original complete callback source no longer matches transfer hash')
        failed_sha=sha(failed/'journal.sqlite3')
        rows=list(faildb.execute('SELECT * FROM calls ORDER BY request_id,ordinal'))
        inherited=validate_failure(status,supervisor,rows,shard['inherited_task_callback_counts'])
        old=json.loads(olddb.execute("SELECT value FROM meta WHERE key='plan'").fetchone()[0])
        local=json.loads(faildb.execute("SELECT value FROM meta WHERE key='plan'").fetchone()[0])
        plan=json.loads(plan_path.read_text());tasks=plan['methods']['M5']['tasks']
        if digest(local)!=digest(local_for_shard(old,plan,tasks)) or local['scheduler_source']['sha256']!=DB06:
            raise ValueError('Failed local plan does not exactly match unchanged original db06 construction')
        if sha(local['scheduler_source']['path'])!=DB06:
            raise ValueError('Original scheduler changed')
        selected=set(local['selected_task_ids']);prefix_rows=[]
        for (key,ordinal),failed_row in inherited.items():
            if key not in selected:
                raise ValueError('Inherited prefix is outside unchanged GPU2 task scope')
            original=olddb.execute('SELECT * FROM calls WHERE request_id=? AND ordinal=?',(key,ordinal)).fetchone()
            if original is None or original['request']!=failed_row['request'] or original['reserved_tokens']!=failed_row['reserved_tokens']:
                raise ValueError('Failed run prefix request is not exact original source callback')
            a=json.loads(original['result']);b=json.loads(failed_row['result'])
            if digest(a['value'])!=digest(b['value']) or [e.get('original_event') for e in b['events']]!=a['events']:
                raise ValueError('Failed run prefix response/event differs from original source')
            prefix_rows.append(replay_callback(original,source_ref))
        if len(prefix_rows)!=shard['inherited_callback_rows']:
            raise ValueError('Original transferred callback count differs')
        old_outputs=list(faildb.execute('SELECT record FROM outputs'))
        if len(old_outputs)!=status['complete'] or any(json.loads(r[0])['status']!='complete' for r in old_outputs):
            raise ValueError('Failed run had unexpected output statuses')
        destination.mkdir();new_plan=destination/'plan.json';new_plan.write_bytes(plan_path.read_bytes())
        run=destination/'runs/m5';run.mkdir(parents=True)
        journal=RunJournal(run/'journal.sqlite3',local)
        provenance=dict(failed_run=str(failed),failed_journal_sha256=failed_sha,
            failed_status_sha256=sha(failed/'status.json'),failed_supervisor_sha256=sha(failed/'supervisor_result.json'),
            original_transfer=str(transfer_path),original_transfer_sha256=sha(transfer_path),
            original_plan=str(plan_path),plan_byte_identical=True,failed_attempts_preserved=status['cost']['failed_attempts'],
            cached_outputs_recomputed_without_copy=len(old_outputs),recovery_attempt=1,
            reason='One separate runtime initialization recovery; no new scientific setting, seed or sampling')
        try:
            with journal.db:
                journal.db.executemany('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',prefix_rows)
                journal.db.execute('INSERT INTO meta VALUES (?,?)',('partial_prefix_transfer',serialized(dict(source_ref,callback_rows=len(prefix_rows)))))
                journal.db.execute('INSERT INTO meta VALUES (?,?)',('runtime_recovery',serialized(provenance)))
        finally:journal.db.close()
        write(run/'plan.json',local)
        new_shard=deepcopy(shard);new_shard.update(plan=str(new_plan),output=str(run))
        receipt=deepcopy(transfer);receipt.update(shards=[new_shard],recovery=provenance,
            failed_source_SQL_unchanged=sha(failed/'journal.sqlite3')==failed_sha,
            no_outputs_copied=True,new_model_calls=0,new_grader_calls=0)
        write(destination/'transfer_receipt.json',receipt)
        return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transfer',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(prepare(args.transfer,args.output),ensure_ascii=False))
