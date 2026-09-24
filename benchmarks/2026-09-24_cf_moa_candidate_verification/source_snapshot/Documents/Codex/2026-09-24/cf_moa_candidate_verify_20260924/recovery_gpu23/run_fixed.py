"""One authorized fixed GPU2/3 run; no resource search or automatic retry."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('/home/data3/txy')
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
C3 = ROOT/'Documents/Codex/2026-09-21/cf_moa/effect_first_revision_20260923/cycle3'
sys.path[:0] = [str(ROOT), str(C3)]
import queue_answers_reserved as holders
from cf_moa.evaluation.candidate_verify_runner import load_plan

PY = ROOT/'MedRGAG/.venv/bin/python'
ASSIGNMENT = {'M5': 2, 'M4': 3}


def save(value):
    value['updated_at'] = holders.stamp()
    temporary = HERE/'status.tmp'
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(HERE/'status.json')


def restore(gpu, state):
    directory = HERE/'restored_holders'/('gpu'+str(gpu))
    directory.mkdir(parents=True, exist_ok=False)
    command = [str(PY), '-u', str(holders.WATCH), '--state-dir', str(directory),
        '--only-gpu', str(gpu), '--min-free-gib', '50', '--gib', '60',
        '--hold-hours', '0', '--wait-hours', '0', '--interval', '5',
        '--log-interval', '300', '--max-cards', '1', '--torch-python', str(PY)]
    with (directory/'watch.log').open('wb') as log:
        child = subprocess.Popen(command, cwd=ROOT, stdout=log,
            stderr=subprocess.STDOUT, start_new_session=True)
    identity = holders.process(child.pid)
    state.setdefault('restored_holders', {})[str(gpu)] = dict(
        identity=identity, state_dir=str(directory), command=command)
    save(state)


def analysis(arguments, logfile):
    command = [str(PY), str(RUN/'analysis/score_candidate_experiment.py'),
        '--runs-root', str(HERE/'runs'), '--plan', str(HERE/'plan.json'),
        '--output-root', str(HERE/'analysis'), *arguments]
    with (HERE/logfile).open('wb') as log:
        return subprocess.run(command, cwd=ROOT, stdout=log,
            stderr=subprocess.STDOUT).returncode


def main():
    lock = (HERE/'fixed_run.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (HERE/'status.json').exists():
        raise RuntimeError('This fixed launch was already attempted; no automatic retry')
    for method in ASSIGNMENT:
        load_plan(HERE/'plan.json', method)
    holders.HERE = HERE
    holders.STATUS = HERE/'holder_handoff.json'
    watch_state = json.loads((HERE/'holder_sources.json').read_text())
    state = dict(status='launching_fixed_gpu23', assignment=ASSIGNMENT,
        launched={}, finished={}, automatic_retry=False)
    save(state)
    children = {}
    for method, gpu in ASSIGNMENT.items():
        if not holders.same_process(watch_state['watches'][str(gpu)]):
            state['finished'][method] = dict(status='holder_identity_changed_no_launch')
            save(state)
            continue
        if not holders.stop_watch(watch_state, gpu):
            state['finished'][method] = dict(status='holder_release_incomplete_no_launch')
            save(state)
            continue
        output = HERE/'runs'/method.lower()
        command = [str(PY), '-u', str(RUN/'launch_candidate.py'),
            '--plan', str(HERE/'plan.json'), '--method', method,
            '--output', str(output), '--gpu', str(gpu)]
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), PYTHONPATH=str(ROOT),
            VLLM_USE_V1='1', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4',
            TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1')
        with (HERE/(method.lower()+'.log')).open('wb') as log:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True)
        children[method] = child
        state['launched'][method] = dict(pid=child.pid, gpu=gpu,
            identity=holders.process(child.pid), command=command, at=holders.stamp())
        save(state)
    while children:
        for method, child in list(children.items()):
            output = HERE/'runs'/method.lower()
            if ((output/'smoke_ready.json').exists()
                    and not (output/'continue_full.json').exists()
                    and not (output/'STOP').exists()):
                code = analysis(['--smoke-only', '--method', method], method.lower()+'_smoke_analysis.log')
                path = HERE/'analysis'/('smoke_'+method.lower())/'summary.json'
                report = json.loads(path.read_text()) if path.exists() else {}
                expected = json.loads((output/'smoke_ready.json').read_text())['expected_tasks']
                if (code == 0 and report.get('method') == method
                        and report.get('status') == 'smoke_review_complete'
                        and len(report.get('records', [])) == expected):
                    marker = dict(action='continue_all_predeclared_inputs',
                        conditioned_on_gold_quality=False, offline_quality_report=str(path))
                    (output/'continue_full.json').write_text(json.dumps(marker)+'\n')
                    state.setdefault('smoke_reviewed', {})[method] = str(path)
                else:
                    state.setdefault('analysis_errors', {})[method] = dict(returncode=code, report=str(path))
                    (output/'STOP').touch()
                save(state)
            code = child.poll()
            if code is None:
                continue
            lifecycle_path = output/'lifecycle.json'
            lifecycle = json.loads(lifecycle_path.read_text()) if lifecycle_path.exists() else {}
            state['finished'][method] = dict(returncode=code, lifecycle=lifecycle)
            del children[method]
            save(state)
            if lifecycle.get('status') == 'closed':
                restore(ASSIGNMENT[method], state)
        state['status'] = 'running' if children else 'inference_finished'
        save(state)
        if children:
            time.sleep(2)
    state['analysis_returncode'] = analysis(['--include-candidate'], 'full_analysis.log')
    state['status'] = 'fixed_run_finished'
    save(state)


if __name__ == '__main__':
    main()
