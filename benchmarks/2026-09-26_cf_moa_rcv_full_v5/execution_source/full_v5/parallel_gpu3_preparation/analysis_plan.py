"""Prepare/validate one M4 incremental analysis after a closed three-way handoff.

No model, grader, SQL mutation, monitoring, process control, or source edits.
Commands are emitted for root, never executed. Synthetic tests use tiny files.
"""
import argparse
import hashlib
import json
from pathlib import Path

ANALYZER_SHA256='ce2603986f53ce08ee6bba90a5352c648e9a8b40360e4f87f54798f10b61b03b'
TERMINAL={'complete','completed','unavailable','failed','error'}
DENOMINATORS={'planned_inputs_per_method':13905,'planned_native_mappings_per_method':15616,'planned_ALL_units':6104}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def ref(path):
    p=Path(path).resolve()
    return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)


def tasks(plan):
    ids=[r['task_id'] for r in plan['methods']['M4']['tasks']]
    if len(ids)!=len(set(ids)):
        raise ValueError('Repeated planned task identity')
    return set(ids)


def source(spec, expected, old=False):
    run=Path(spec['run_dir']).resolve()
    state=read(run/'status.json');closed=read(run/'supervisor_result.json')
    wanted='stopped_by_request' if old else 'complete'
    if state.get('status')!=wanted or closed.get('exit_code')!=(1 if old else 0):
        raise ValueError('Source is not the declared closed STOP/complete job')
    if closed.get('method') not in (None,'M4') or state.get('first_systemic_error'):
        raise ValueError('Wrong method or systemic error')
    if not closed.get('finished_at'):
        raise ValueError('Missing durable supervisor closure')
    cost=state.get('cost',{})
    if (cost.get('model_usage_complete') is not True or cost.get('unresolved_model_usage')!=0
            or cost.get('unfinished_call_wall_unknown',0)!=0):
        raise ValueError('Unresolved physical submission/time cannot be ignored')
    planned=tasks(read(spec['stage_plan']))
    if state['planned']!=len(planned) or not planned<=expected:
        raise ValueError('Source stage task scope differs')
    if old and planned!=expected:
        raise ValueError('Old STOP job must retain its original whole task plan')
    seen=set()
    with (run/'proposals.jsonl').open() as stream:
        for line in stream:
            if not line.strip():continue
            r=json.loads(line);task=r.get('task_id')
            if (r.get('method')!='M4' or task!=r.get('request_id','')+':'+r.get('arm','')
                    or task not in planned or task in seen or r.get('status') not in TERMINAL
                    or not r.get('input_hash')):
                raise ValueError('Unexpected/duplicate/nonterminal proposal identity')
            if r['status'] in ('complete','completed') and 'native_answer' not in (r.get('result') or {}):
                raise ValueError('Completed proposal lacks whole native result')
            seen.add(task)
    if len(seen)!=sum(state.get(k,0) for k in ('complete','unavailable','failed')):
        raise ValueError('Terminal proposal count differs from saved status')
    if state['not_submitted']!=len(planned)-len(seen):
        raise ValueError('Unfinished task denominator differs')
    if not old and seen!=planned:
        raise ValueError('New shard is not fully terminal')
    db=run/'journal.sqlite3';wal=Path(str(db)+'-wal')
    if not db.is_file() or (wal.exists() and wal.stat().st_size):
        raise ValueError('Cost sources must be ended/checkpointed journals')
    return dict(run_dir=str(run),proposals=ref(run/'proposals.jsonl'),journal=ref(db),
        job_status=ref(run/'status.json'),supervisor=ref(run/'supervisor_result.json'),
        task_count=len(planned),terminal_rows=len(seen),not_submitted=state['not_submitted'],
        status=state['status'],saved_cost=cost),seen,planned


def prepare(config):
    if config.get('schema_version')!='M4_three_source_incremental_analysis_v1':
        raise ValueError('Wrong plan identity')
    if len(config['new_shards'])!=2:
        raise ValueError('Bind exactly the two newly completed M4 shards')
    expected=tasks(read(config['original_stage_plan']))
    old,old_ids,_=source(config['old_stopped_source'],expected,True)
    sources=[old];union=set(old_ids);new_scopes=set()
    for shard in config['new_shards']:
        value,ids,planned=source(shard,expected)
        if union&ids or new_scopes&planned:
            raise ValueError('Old/new terminal scopes overlap; do not duplicate results')
        new_scopes.update(planned);union.update(ids);sources.append(value)
    if union!=expected or new_scopes!=(expected-old_ids):
        raise ValueError('Three-source union omits or adds original task rows')
    analyzer=Path(config['analyzer']).resolve()
    if sha(analyzer)!=ANALYZER_SHA256:
        raise ValueError('Keep the existing incremental analyzer unchanged')
    out=Path(config['analysis_output']).resolve();before=read(out/'receipt.json')
    if before.get('methods')!=['M4'] or before.get('script_sha256')!=ANALYZER_SHA256:
        raise ValueError('Existing analysis/cache identity differs')
    if any(before.get(k)!=v for k,v in DENOMINATORS.items()):
        raise ValueError('Existing complete-panel denominators differ')
    if not (out/'native_score_cache.sqlite3').is_file():
        raise ValueError('Reuse existing durable score cache; do not create a replacement')
    prior=[]
    for row in before['input_sources']:
        if sha(row['path'])!=row['sha256']:
            raise ValueError('Previously registered closed source changed')
        prior.append(row)
    db_paths=[Path(s['journal']['path']) for s in sources]
    identities={(p.stat().st_dev,p.stat().st_ino) for p in db_paths}
    if len(identities)!=3 or len({s['journal']['sha256'] for s in sources})!=3:
        raise ValueError('Bind three original journals, not aliases or copied snapshots')
    command=[config['python'],str(analyzer),'--method','M4','--output',str(out)]
    for value in sources:command+=['--proposals',value['proposals']['path']]
    command+=['--grade-missing']
    return dict(status='ready_for_one_explicit_incremental_analysis_not_executed',method='M4',
        expected_task_rows=len(expected),terminal_union_rows=len(union),sources=sources,
        prior_analysis_receipt=ref(out/'receipt.json'),prior_registered_sources=prior,
        score_cache_path=str(out/'native_score_cache.sqlite3'),command=command,
        environment={'CUDA_VISIBLE_DEVICES':''},
        physical_journal_additions=[dict(path=s['journal']['path'],method='M4',scope='current') for s in sources],
        denominators=DENOMINATORS,
        instructions=['Use the same analysis/m4 directory and existing native score cache.',
          'Do not run the old single-job watcher as the completion gate for this union.',
          'Append these three original SQLs once to the FINAL cost source list; never copied or merged SQL.',
          'Callback prefixes copied as replay/physical=[] remain inherited cost; submission_attempts is not fresh call count.',
          'After one successful incremental analysis validate the final receipt with --validate-final.',
          'Full-v5 stopped journals are not confirmation first-pool exact-callback sources.'],
        new_model_calls=0,new_grader_calls=0,SQL_opened=False)


def validate_final(prepared, receipt):
    if receipt.get('status')!='complete' or receipt.get('methods')!=['M4']:
        raise ValueError('Full M4 analysis is not complete')
    if receipt.get('script_sha256')!=ANALYZER_SHA256 or receipt.get('inference_calls')!=0:
        raise ValueError('Unexpected analyzer/inference identity')
    if any(receipt.get(k)!=v for k,v in DENOMINATORS.items()):
        raise ValueError('Full denominator changed')
    actual={r['path']:r for r in receipt['input_sources']}
    if len(actual)!=len(receipt['input_sources']):
        raise ValueError('Duplicated source metadata')
    for row in prepared['prior_registered_sources']:
        if row['path'] not in actual or actual[row['path']]['sha256']!=row['sha256']:
            raise ValueError('Previously analyzed source was omitted or changed')
    for source in prepared['sources']:
        row=actual.get(source['proposals']['path'])
        if not row or row['sha256']!=source['proposals']['sha256'] or row['terminal_rows']!=source['terminal_rows']:
            raise ValueError('Three-source terminal union was not fully bound')
    return dict(status='full_M4_incremental_analysis_receipt_bound',new_grader_calls=receipt['new_native_grader_calls'],
                denominators=DENOMINATORS,validation_model_calls=0,validation_grader_calls=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--validate-final',type=Path,help='Previously prepared handoff JSON')
    parser.add_argument('--receipt',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Use a new output; preserve previous handoff evidence')
    if args.validate_final:
        if not args.receipt:parser.error('--receipt is required for final validation')
        result=validate_final(read(args.validate_final),read(args.receipt))
    else:
        if not args.config:parser.error('--config is required for preparation')
        result=prepare(read(args.config))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','expected_task_rows','terminal_union_rows','new_model_calls','new_grader_calls')},ensure_ascii=False))


if __name__=='__main__':main()
