"""Launch one explicitly prepared M4 resource shard once, then restore reservation."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

WORK = Path('/home/data3/txy')
PY = WORK/'MedRGAG/.venv/bin/python'
sys.path.insert(0, str(WORK))
from cf_moa.evaluation.resources import admission
from cf_moa.evaluation.run_moa_rcv import load_plan, selected_profile

DB06 = 'db06c973db607a3073cc669cc184ccb26d629abf219f20219ed8f47f659c0a47'
WATCH_SHA = 'a6ef2550000a72d3fa558b48f0e665d4861a29204d0a8898ef97ef1105913ec0'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transfer', type=Path, required=True)
    parser.add_argument('--gpu', type=int, choices=(1,3), required=True)
    args = parser.parse_args()
    receipt = json.loads(args.transfer.read_text())
    shard = next(row for row in receipt['shards'] if row['gpu']==args.gpu)
    plan_path = Path(shard['plan'])
    output = Path(shard['output'])
    if (receipt['status']!='resource_shards_prepared_not_launched' or not receipt['source_SQL_unchanged']
            or sha(plan_path)!=shard['plan_sha256']):
        raise ValueError('Resource transfer identity differs')
    if sha(WORK/'cf_moa/evaluation/run_moa_rcv_batched.py')!=DB06:
        raise ValueError('Keep original running scheduler unchanged')
    watch = WORK/'.local/bin/gpu_watch.py'
    if sha(watch)!=WATCH_SHA:
        raise ValueError('Original reservation script changed')
    plan, selected, packets, pools, bases, tasks = load_plan(plan_path, 'M4')
    if plan['allowed_gpus']!=[args.gpu] or len(tasks)!=shard['tasks']:
        raise ValueError('Bound shard GPU/task identity differs')
    profile = selected_profile('M4','readout')
    resource = admission(profile,'readout',args.gpu)
    if not resource['ready']:
        print(json.dumps(dict(status='capacity_not_ready_no_model_initialization',resources=resource)))
        raise SystemExit(75)
    output.mkdir(parents=True,exist_ok=True)
    launch_path = output/'launch.json'
    # Exclusive create prevents duplicate launch of even a prefilled prefix journal.
    record = dict(at=datetime.now().astimezone().isoformat(),method='M4',gpu=args.gpu,
        supervisor_pid=os.getpid(),plan=str(plan_path),plan_sha256=sha(plan_path),
        transfer_receipt=str(args.transfer.resolve()),transfer_sha256=sha(args.transfer),
        scheduler_sha256=DB06,launcher_sha256=sha(__file__),resources=resource,
        general_autoqueue_enabled=False,automatic_retry=False)
    with launch_path.open('x') as stream:
        json.dump(record,stream,ensure_ascii=False,indent=2)
    command = [str(PY),'-m','cf_moa.evaluation.run_moa_rcv_batched','--plan',str(plan_path),
        '--method','M4','--role','readout','--gpu',str(args.gpu),'--output',str(output)]
    code = None
    try:
        with (output/'stdout.log').open('a') as log:
            process = subprocess.Popen(command,cwd=WORK,
                env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(args.gpu),PYTHONPATH=str(WORK)),
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            record.update(pid=process.pid,command=command)
            dump(launch_path,record)
            code = process.wait()
    finally:
        state = plan_path.parent/'restored_holders'/f'gpu{args.gpu}'
        state.mkdir(parents=True,exist_ok=False)
        holder_command = [str(PY),'-u',str(watch),'--state-dir',str(state),'--only-gpu',str(args.gpu),
            '--min-free-gib','50','--gib','60','--hold-hours','0','--wait-hours','0',
            '--interval','5','--log-interval','300','--max-cards','1','--torch-python',str(PY)]
        with (state/'watch.log').open('a') as log:
            holder = subprocess.Popen(holder_command,cwd=WORK,stdin=subprocess.DEVNULL,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        dump(output/'supervisor_result.json',dict(**record,exit_code=code,
            finished_at=datetime.now().astimezone().isoformat(),restored_watch_pid=holder.pid,
            restored_state=str(state)))
    raise SystemExit(code)


if __name__=='__main__':
    main()
