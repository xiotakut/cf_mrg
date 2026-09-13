"""Disjoint M4 batches, separate artifacts, exact coverage before final merge."""
import fcntl
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from prepare_v5 import OUT, read, write, dump
from run_m4_gpu0_guard import check, stop_group

ROOT = OUT/'M4'


def split_batches(items, workers=3):
    shards = [[] for _ in range(workers)]
    for start in range(0, len(items), 16):
        shards[(start//16) % workers].extend(items[start:start+16])
    return shards


def prepare():
    assert not (ROOT/'parallel_plan.json').exists()
    items = read(OUT/'items.jsonl')
    rows = read(ROOT/'predictions.jsonl')
    done = {r['item_id'] for r in rows}
    assert len(done) == len(rows)
    with gzip.open(ROOT/'prompts.jsonl.gz', 'rt') as f:
        prompts = [json.loads(line) for line in f]
    assert {r['item_id'] for r in prompts} == done and len(prompts) == len(rows)
    pending = [i for i in items if i['item_id'] not in done]
    pending.sort(key=lambda i:(len(i['question'])+sum(map(len,i['fixed_evidence'])),i['item_id']))
    shards = split_batches(pending)
    sets = [{i['item_id'] for i in shard} for shard in shards]
    expected = {i['item_id'] for i in items}
    assert len(expected) == len(items)
    remaining=set().union(*sets)
    assert sum(map(len,sets))==len(remaining) and not done & remaining
    assert done | remaining == expected
    for n, shard in enumerate(shards):
        folder = ROOT/'parallel'/f'worker-{n}'
        folder.mkdir(parents=True)
        write(folder/'items.jsonl', shard)
        shutil.copyfile(ROOT/'retrieval.jsonl', folder/'retrieval.jsonl')
    plan = dict(total=len(items), base_completed=len(done), shards=list(map(len, shards)),
                batch_size=16, disjoint=True, exact_coverage=True)
    dump(ROOT/'parallel_plan.json', plan)
    print(json.dumps(plan), flush=True)


def merge(partial=False):
    plan=json.loads((ROOT/'parallel_plan.json').read_text())
    folders = [ROOT, *[ROOT/'parallel'/f'worker-{n}' for n in range(len(plan['shards']))]]
    rows = [row for folder in folders for row in read(folder/'predictions.jsonl')]
    expected = {i['item_id'] for i in read(OUT/'items.jsonl')}
    actual = {r['item_id'] for r in rows}
    assert actual <= expected and len(rows) == len(actual), 'unexpected/duplicate predictions'
    if not partial:assert actual == expected, 'missing predictions'
    prompt_ids = []
    for folder in folders:
        with gzip.open(folder/'prompts.jsonl.gz', 'rt') as f:
            prompt_ids.extend(json.loads(line)['item_id'] for line in f)
    assert set(prompt_ids) == actual and len(prompt_ids) == len(actual)
    retrievals = {r['question']:r for folder in folders for r in read(folder/'retrieval.jsonl')}
    backup = ROOT/f'before_parallel_{time.time_ns()}'
    backup.mkdir(exist_ok=True)
    for name in ['predictions.jsonl', 'prompts.jsonl.gz', 'retrieval.jsonl']:
        shutil.copyfile(ROOT/name, backup/name)
    write(ROOT/'predictions.merged.jsonl', rows)
    write(ROOT/'retrieval.merged.jsonl', retrievals.values())
    with (ROOT/'prompts.merged.jsonl.gz').open('wb') as out:
        for folder in folders:
            with (folder/'prompts.jsonl.gz').open('rb') as src:
                shutil.copyfileobj(src, out)
    for stem, suffix in [('predictions','jsonl'),('retrieval','jsonl'),('prompts','jsonl.gz')]:
        os.replace(ROOT/f'{stem}.merged.{suffix}', ROOT/f'{stem}.{suffix}')
    dump(ROOT/'parallel_coverage.json', dict(expected=len(expected),predictions=len(rows),
         prompts=len(prompt_ids),missing=len(expected-actual),duplicates=0,partial=partial))
    dump(ROOT/'progress.json', dict(completed_this_run=len(rows),pending_at_start=len(expected),updated=time.time()))
    if not partial:dump(ROOT/'complete.json', dict(inputs=len(rows),time=time.time(),parallel=True))


def run():
    lock = (ROOT/'run.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX)
    plan = json.loads((ROOT/'parallel_plan.json').read_text())
    children = {}
    yielded = False
    def launch(n, gpu):
        folder = ROOT/'parallel'/f'worker-{n}'
        env = os.environ | {'CUDA_VISIBLE_DEVICES':str(gpu)}
        with (folder/'run.log').open('a') as log:
            child = subprocess.Popen([sys.executable,'-u',str(OUT/'code/run_medrag.py'),'M4',
                '--gpu-memory','.50','--batch-size','16','--work-dir',str(folder),
                '--items-file',str(folder/'items.jsonl')],env=env,stdout=log,
                stderr=subprocess.STDOUT,start_new_session=True)
        children[n] = child
    reason = check()
    if reason:
        yielded = True
    else:
        launch(0, 0)
    for n in range(1,len(plan['shards'])):launch(n,n)
    try:
        while children:
            if 0 in children and not yielded:
                reason = check(children[0].pid)
                if reason:
                    stop_group(children[0].pid)
                    children[0].wait()
                    del children[0]
                    yielded = True
            for n, child in list(children.items()):
                if child.poll() is not None:
                    stop_group(child.pid)
                    assert child.returncode == 0, f'worker {n} failed: {child.returncode}'
                    del children[n]
            status = dict(status='running',pids={n:c.pid for n,c in children.items()},
                          gpu0_yielded=yielded,reason=reason,base_completed=plan['base_completed'],time=time.time())
            dump(ROOT/'parallel_status.json',status)
            if not children and yielded and not (ROOT/'parallel/worker-0/complete.json').exists():
                launch(0, 1)
            time.sleep(2)
        merge()
        dump(ROOT/'parallel_status.json',dict(status='complete',time=time.time()))
    finally:
        for child in children.values():
            stop_group(child.pid)
            child.wait()


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        for workers in [2,3]:
            for size in [0,1,16,17,32,95,1000]:
                shards=split_batches(list(range(size)),workers)
                flat=[i for s in shards for i in s]
                assert sorted(flat)==list(range(size)) and len(flat)==len(set(flat))
                assert max(map(len,shards))-min(map(len,shards))<=16
        print('disjoint batch partition checks passed')
    elif '--prepare' in sys.argv:
        prepare()
    elif '--merge-partial' in sys.argv:
        merge(partial=True)
    else:
        run()
