"""Split the original GPU2 tail across GPU2/1/3; preserve exact CPU prefixes.

Preparation only: no models, graders, process actions or source-SQL mutations.
All 4,791 GPU2 task rows remain; 12 known cache-only outputs are reconstructed
from the identical saved F pools and original 36 callback prefixes, not rerun.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from partial_prefix_transfer import DB06, RunJournal, digest, local_for_shard, replay_callback, serialized, sha, write
from prepare_gpu2_recovery import read_db, validate_failure

GPUS=(2,1,3)
TERMINAL={'complete','completed','unavailable','failed','error'}


def split_tasks(tasks):
    ids=list(dict.fromkeys(t['request_id'] for t in tasks))
    allocation={rid:GPUS[i%len(GPUS)] for i,rid in enumerate(ids)}
    shards={gpu:[t for t in tasks if allocation[t['request_id']]==gpu] for gpu in GPUS}
    keys=[t['task_id'] for t in tasks]
    copied=[t['task_id'] for values in shards.values() for t in values]
    if len(keys)!=len(set(keys)) or len(copied)!=len(set(copied)) or set(copied)!=set(keys):
        raise ValueError('Tail shards must be disjoint and exhaustive')
    return shards,dict(original_tasks=len(tasks),old_terminal_tasks=0,remaining_tasks=len(tasks),
        original_inputs=len(ids),gpu_order=list(GPUS),disjoint=True,exhaustive=True,
        shard_task_counts={str(g):len(v) for g,v in shards.items()},
        shard_input_counts={str(g):len({t['request_id'] for t in v}) for g,v in shards.items()},
        allocation='All original GPU2 input groups round robin in original order across GPU2/1/3; exact prefixes follow their input; no gold/score/source/length selection')


def cached_subset(path, ids):
    result={}
    with Path(path).open() as stream:
        for line in stream:
            row=json.loads(line)
            if row['request_id'] in ids:
                value=row.get('proposal',row.get('result',row))
                if row['request_id'] in result and digest(result[row['request_id']])!=digest(value):
                    raise ValueError('Conflicting same-input saved F cache')
                result[row['request_id']]=value
    return result


def prepare(transfer_path,recovery_run,output):
    transfer_path=Path(transfer_path).resolve();recovery_run=Path(recovery_run).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Tail preparation requires a fresh destination')
    transfer=json.loads(transfer_path.read_text());gpu2=next(s for s in transfer['shards'] if s['gpu']==2)
    source_ref=deepcopy(transfer['source']);original=Path(source_ref['journal']).parent
    plan_path=Path(gpu2['plan'])
    if sha(plan_path)!=gpu2['plan_sha256']:raise ValueError('Original GPU2 plan changed')
    plan=json.loads(plan_path.read_text());selected=plan['methods']['M5'];tasks=selected['tasks']
    for field in ('inputs','saved_f_proposals','saved_bases'):
        if field in selected and sha(selected[field])!=selected[field+'_sha256']:
            raise ValueError('Original GPU2 input/cache binding changed')
    for path,expected in plan['code_sources'].items():
        if sha(path)!=expected:raise ValueError('Original scientific code binding changed: '+path)
    for name,key in [('status.json','source_status_sha256'),('supervisor_result.json','source_supervisor_sha256')]:
        if sha(original/name)!=source_ref[key]:raise ValueError('Original STOP evidence changed')
    status=json.loads((recovery_run/'status.json').read_text())
    supervisor=json.loads((recovery_run/'supervisor_result.json').read_text())
    if supervisor.get('plan_sha256')!=gpu2['plan_sha256']:raise ValueError('Recovery plan identity drift')
    with ExitStack() as stack:
        olddb=read_db(stack,original);failed=read_db(stack,recovery_run)
        if sha(original/'journal.sqlite3')!=source_ref['journal_sha256']:
            raise ValueError('Original prefix source differs from its frozen hash')
        old=json.loads(olddb.execute("SELECT value FROM meta WHERE key='plan'").fetchone()[0])
        local=json.loads(failed.execute("SELECT value FROM meta WHERE key='plan'").fetchone()[0])
        if digest(local)!=digest(local_for_shard(old,plan,tasks)) or sha(local['scheduler_source']['path'])!=DB06:
            raise ValueError('Keep actual db06 scheduler and local construction unchanged')
        inherited=validate_failure(status,supervisor,list(failed.execute('SELECT * FROM calls')),gpu2['inherited_task_callback_counts'])
        known={r[0]:json.loads(r[1]) for r in failed.execute('SELECT request_id,record FROM outputs')}
        if len(known)!=status['complete'] or any(r['status']!='complete' for r in known.values()):
            raise ValueError('Unexpected status among known cache-only outputs')
        tail_keys={t['task_id'] for t in tasks}
        if not set(known)<=tail_keys:raise ValueError('Known cache output lies outside original tail')
        # Verify the complete parent union without materializing complete responses.
        closed_ids={r[0] for r in olddb.execute('SELECT request_id FROM outputs')}
        closed_sources=[dict(run=str(original),status='stopped_by_request',tasks=len(closed_ids))]
        for gpu in (1,3):
            shard=next(s for s in transfer['shards'] if s['gpu']==gpu);run=Path(shard['output'])
            s=json.loads((run/'status.json').read_text());sup=json.loads((run/'supervisor_result.json').read_text())
            if s.get('status')!='complete' or sup.get('exit_code')!=0 or s.get('cost',{}).get('unresolved_model_usage')!=0:
                raise ValueError('Both prior GPU1/GPU3 shards must have closed complete')
            db=read_db(stack,run)
            expected={t['task_id'] for t in json.loads(Path(shard['plan']).read_text())['methods']['M5']['tasks']}
            rows=list(db.execute("SELECT request_id,json_extract(record,'$.status') FROM outputs"))
            ids={r[0] for r in rows}
            if ids!=expected or len(ids)!=shard['tasks'] or any(r[1] not in TERMINAL for r in rows) or ids&closed_ids:
                raise ValueError('Closed parent shard identity is not exact/disjoint')
            closed_ids|=ids
            closed_sources.append(dict(run=str(run),status='complete',tasks=len(ids),
                status_sha256=sha(run/'status.json'),supervisor_sha256=sha(run/'supervisor_result.json')))
        all_keys=set(old['selected_task_ids'])
        if closed_ids&tail_keys or closed_ids|tail_keys!=all_keys:
            raise ValueError('Old STOP + completed GPU1/GPU3 + original GPU2 tail must exactly cover parent tasks')
        original_rows={}
        for (key,ordinal),saved in inherited.items():
            row=olddb.execute('SELECT * FROM calls WHERE request_id=? AND ordinal=?',(key,ordinal)).fetchone()
            if row is None or row['request']!=saved['request'] or row['reserved_tokens']!=saved['reserved_tokens']:
                raise ValueError('Original callback request identity differs')
            a=json.loads(row['result']);b=json.loads(saved['result'])
            if digest(a['value'])!=digest(b['value']) or [e.get('original_event') for e in b['events']]!=a['events']:
                raise ValueError('Original callback value/event differs')
            original_rows[(key,ordinal)]=row
        if len(original_rows)!=gpu2['inherited_callback_rows']:raise ValueError('Original prefix count changed')
        shards,proof=split_tasks(tasks)
        proof.update(known_cache_only_terminal_tasks=len(known),actual_unfinished_tasks=len(tasks)-len(known),
            parent_selected_tasks=len(all_keys),parent_closed_tasks=len(closed_ids),parent_disjoint=True,parent_exhaustive=True)
        output.mkdir(parents=True);prepared=[]
        for gpu,part in shards.items():
            folder=output/f'gpu{gpu}';folder.mkdir();ids={t['request_id'] for t in part};keys={t['task_id'] for t in part}
            cached=cached_subset(selected['saved_f_proposals'],ids)
            cache=folder/'saved_f_proposals.jsonl'
            cache.write_text(''.join(serialized(dict(request_id=rid,proposal=value))+'\n' for rid,value in cached.items()))
            protocol=deepcopy(plan);protocol['allowed_gpus']=[gpu];protocol['methods']['M5']['tasks']=part
            protocol['methods']['M5'].update(saved_f_proposals=str(cache),saved_f_proposals_sha256=sha(cache))
            protocol['parallel_resource_shard']=dict(source_ref,gpu=gpu,original_scheduler_sha256=DB06,
                method_profile_budget_prompt_unchanged=True,partition=proof,tail_of_original_gpu2=True)
            write(folder/'plan.json',protocol);new_local=local_for_shard(old,protocol,part)
            run=folder/'runs/m5';run.mkdir(parents=True);journal=RunJournal(run/'journal.sqlite3',new_local)
            counts={}
            try:
                with journal.db:
                    for task in part:
                        key=task['task_id'];rows=[original_rows[(key,i)] for i in range(gpu2['inherited_task_callback_counts'].get(key,0))]
                        for row in rows:journal.db.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?,?)',replay_callback(row,source_ref))
                        if rows:counts[key]=len(rows)
                    journal.db.execute('INSERT INTO meta VALUES (?,?)',('partial_prefix_transfer',serialized(dict(source_ref,callback_rows=sum(counts.values())))))
            finally:journal.db.close()
            write(run/'plan.json',new_local)
            prepared.append(dict(gpu=gpu,plan=str(folder/'plan.json'),plan_sha256=sha(folder/'plan.json'),output=str(run),
                tasks=len(part),inputs=len(ids),cached_F_inputs=len(cached),inherited_callback_rows=sum(counts.values()),
                inherited_task_callback_counts=counts,new_physical_requests_from_transfer=0,
                known_cache_only_task_ids=sorted(keys&set(known))))
        receipt=dict(status='resource_shards_prepared_not_launched',source=source_ref,partition=proof,shards=prepared,
            new_model_calls=0,new_grader_calls=0,source_SQL_unchanged=True,
            parent_transfer=dict(path=str(transfer_path),sha256=sha(transfer_path)),closed_sources=closed_sources,
            preserved_failed_runs=[str(Path(gpu2['output'])),str(recovery_run)],
            cache_only_evidence=dict(source_run=str(recovery_run),source_journal_sha256=sha(recovery_run/'journal.sqlite3'),
                count=len(known),native_answer_hashes={k:digest(v['result']['native_answer']) for k,v in known.items()},
                interpretation='Reconstructed by identical saved F and exact prefixes; zero new model submissions; not a separate quality source'),
            cost_policy='Unique physical cost sources: original STOP SQL, old complete GPU1/GPU3 SQL, new three tail SQL. Prefix rows physical=[]; failed initializations keep separate wall/failure audit. No failed SQL or first_error copied.')
        write(output/'transfer_receipt.json',receipt)
        return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transfer',required=True,type=Path)
    parser.add_argument('--recovery-run',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(prepare(args.transfer,args.recovery_run,args.output),ensure_ascii=False))
