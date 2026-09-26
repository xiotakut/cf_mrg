"""Observe two fixed M4 shards, then submit existing CPU analysis at most once.

No model, GPU action, job launch, retries, or M5 observation. Invocation must
name resolved analysis config and a fresh listener directory. --wait polls 15s.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
HELPER=HERE/'analysis_plan.py'
HELPER_SHA256='5d3fd6701ed257118d6fc9dddd8ea00c8ab3fc1ad638f364f801c728f4dac665'
POLL_SECONDS=15
spec=importlib.util.spec_from_file_location('closed_M4_analysis_helper',HELPER)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)


def now():return datetime.now(timezone.utc).isoformat()


def dump(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    tmp.replace(path)


def probe_shard(entry):
    """Only read status/closure metadata; proposal/SQL hashing waits for closure."""
    run=Path(entry['run_dir']);sp=run/'status.json';cp=run/'supervisor_result.json'
    state=helper.read(sp) if sp.is_file() else None
    if state and state.get('first_systemic_error'):
        return dict(state='blocked',reason='shard_systemic_error',run_dir=str(run))
    if state and state.get('status') not in ('running','complete'):
        return dict(state='blocked',reason='shard_not_successfully_complete',run_dir=str(run),model_status=state.get('status'))
    if not cp.is_file():
        return dict(state='waiting',reason='awaiting_supervisor_closure',run_dir=str(run))
    closed=helper.read(cp)
    if closed.get('exit_code')!=0 or closed.get('method') not in (None,'M4') or not closed.get('finished_at'):
        return dict(state='blocked',reason='nonzero_or_invalid_supervisor_closure',run_dir=str(run),exit_code=closed.get('exit_code'))
    if not state or state.get('status')!='complete':
        return dict(state='blocked',reason='closed_shard_not_complete',run_dir=str(run))
    planned=len(helper.tasks(helper.read(entry['stage_plan'])))
    if (state.get('planned')!=planned or state.get('not_submitted')!=0 or
            sum(state.get(k,0) for k in ('complete','failed','unavailable'))!=planned):
        return dict(state='blocked',reason='closed_shard_denominator_incomplete',run_dir=str(run))
    cost=state.get('cost',{})
    if cost.get('model_usage_complete') is not True or cost.get('unresolved_model_usage')!=0 or cost.get('unfinished_call_wall_unknown',0)!=0:
        return dict(state='blocked',reason='unknown_submission_or_timing',run_dir=str(run))
    return dict(state='ready',run_dir=str(run),planned=planned,
                complete=state.get('complete',0),failed=state.get('failed',0),unavailable=state.get('unavailable',0))


def readiness(config):
    if config.get('schema_version')!='M4_three_source_incremental_analysis_v1' or len(config.get('new_shards',[]))!=2:
        raise ValueError('Only the two explicitly bound M4 shards are supported')
    old=config['old_stopped_source'];run=Path(old['run_dir'])
    if not (run/'supervisor_result.json').is_file() or not (run/'status.json').is_file():
        return dict(state='blocked',reason='old_STOP_source_not_closed_before_listener')
    state=helper.read(run/'status.json');closed=helper.read(run/'supervisor_result.json')
    if state.get('status')!='stopped_by_request' or state.get('first_systemic_error') or closed.get('exit_code')!=1:
        return dict(state='blocked',reason='old_source_not_normal_STOP')
    values=[probe_shard(s) for s in config['new_shards']]
    bad=next((v for v in values if v['state']=='blocked'),None)
    if bad:return dict(state='blocked',reason=bad['reason'],shards=values)
    return dict(state='ready' if all(v['state']=='ready' for v in values) else 'waiting',shards=values)


def run_once(config,folder,ready,popen=subprocess.Popen,prepare=helper.prepare,validate=helper.validate_final):
    """Atomic durable claim is kept on any interruption/error, forbidding retry."""
    attempt=folder/'analysis_once'
    try:attempt.mkdir()
    except FileExistsError:return dict(status='already_claimed_no_retry',attempt=str(attempt)),3
    result=dict(status='claimed',claimed_at=now(),automatic_retry=False,new_model_calls=0,analysis_submissions=0,readiness=ready)
    dump(attempt/'result.json',result)
    try:
        if ready.get('state')!='ready':raise ValueError('Both shards must first be ready')
        prepared=prepare(config)
        dump(attempt/'analysis_handoff.ready.json',prepared)
        output=Path(config['analysis_output']);receipt_path=output/'receipt.json'
        before=helper.read(receipt_path)
        shutil.copy2(receipt_path,attempt/'analysis_receipt.before.json')
        # A manually completed identical union needs no additional analyzer call.
        if before.get('status')=='complete':
            validation=validate(prepared,before)
            result.update(status='already_analyzed_no_new_grader',validation=validation,finished_at=now())
            dump(attempt/'result.json',result);return result,0
        command=prepared['command'];result.update(status='submitting_analysis',command=command,submitted_at=now())
        dump(attempt/'result.json',result)
        env=dict(os.environ,CUDA_VISIBLE_DEVICES='')
        with (attempt/'stdout.log').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
            child=popen(command,cwd='/home/data3/txy',env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
            result.update(status='analysis_running',analysis_submissions=1,pid=child.pid)
            dump(attempt/'result.json',result);code=child.wait()
        result.update(exit_code=code,finished_at=now())
        if receipt_path.is_file():shutil.copy2(receipt_path,attempt/'analysis_receipt.after.json')
        if code!=0:
            result['status']='blocked_analysis_failed_no_retry';dump(attempt/'result.json',result);return result,2
        result.update(status='complete',validation=validate(prepared,helper.read(receipt_path)))
        dump(attempt/'result.json',result);return result,0
    except Exception as error:
        result.update(status='blocked_no_retry',error_type=type(error).__name__,error=str(error),finished_at=now())
        dump(attempt/'result.json',result);return result,2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--wait',action='store_true')
    args=parser.parse_args()
    if helper.sha(HELPER)!=HELPER_SHA256:raise ValueError('Source-bound preparation helper changed')
    config=helper.read(args.config);digest=helper.sha(args.config)
    if any(not r.get('run_dir') or not r.get('stage_plan') for r in config['new_shards']):
        raise ValueError('Bind actual two-shard paths before starting listener')
    args.output.mkdir(parents=True,exist_ok=True)
    with (args.output/'listener.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (args.output/'analysis_once').exists():return 3
        binding_path=args.output/'binding.json'
        if binding_path.exists():
            if helper.read(binding_path)['config_sha256']!=digest:raise ValueError('Listener config changed')
        else:dump(binding_path,dict(config_path=str(args.config.resolve()),config_sha256=digest,helper_sha256=HELPER_SHA256,created_at=now(),poll_seconds=POLL_SECONDS,model_launcher=False,automatic_retry=False))
        while True:
            try:
                if helper.sha(args.config)!=digest:raise ValueError('Bound config changed during observation')
                ready=readiness(config)
            except Exception as error:ready=dict(state='blocked',reason=type(error).__name__+': '+str(error))
            dump(args.output/'status.json',dict(at=now(),**ready))
            if ready['state']=='blocked':return 2
            if ready['state']=='ready':
                result,code=run_once(config,args.output,ready)
                dump(args.output/'terminal_result.json',result);return code
            if not args.wait:return 4
            time.sleep(POLL_SECONDS)


if __name__=='__main__':sys.exit(main())
