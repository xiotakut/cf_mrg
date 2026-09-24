"""Two candidate-selection arms on saved F pools; no gold or F generation.

The existing score backend and durable journal are reused unchanged. Smoke is
the first fixed part of the same run; successful requests are not sampled again.
"""
import argparse
from dataclasses import replace
import fcntl
import json
import os
from pathlib import Path
import sys
import time

from cf_moa.agents import a5_candidate_verify as operation
from cf_moa.contracts import Budget, InputPacket, reject_metadata
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.effect_first_runner import ResearchJournal, execute, check_baseline_binding
from cf_moa.evaluation.incremental_runner import CachedTokenBackend, close_runtime
from cf_moa.evaluation.journal import JournalBackend, JournalConflict
from cf_moa.tools.adopted import sha256
from cf_moa.tools.native_backend import profile
from cf_moa.evaluation.resources import admission

ARMS = ('a5_candidate_only', 'a5_candidate_with_rationales')


def load_plan(path, method):
    plan = json.loads(Path(path).read_text())
    for name, expected in plan['code_sources'].items():
        if sha256(name) != expected:
            raise JournalConflict('Candidate method source changed: ' + name)
    selected = profile(method, 'readout')
    if selected.config != plan['profiles'][method]:
        raise JournalConflict('Adopted readout profile changed')
    packets, bases, proposals, tasks = {}, {}, {}, []
    for source in plan['inputs'][method]:
        if sha256(source['path']) != source['sha256']:
            raise JournalConflict('Saved current-input sample changed')
        sample = json.loads(Path(source['path']).read_text())
        data = dict(sample['input_packet']['record'])
        data['budget'] = Budget(**plan['per_task_budget'])
        packet = InputPacket(**data)
        # d/n request handles are disjoint; they are never model prompt fields.
        if packet.request_id in packets:
            raise JournalConflict('Duplicate request handle')
        base = sample['base_result']['record']
        check_baseline_binding(packet, base)
        proposal = sample['f_proposal']['record']['proposal']
        reject_metadata(proposal)
        packets[packet.request_id], bases[packet.request_id] = packet, base
        proposals[packet.request_id] = proposal
        for arm in ARMS:
            tasks.append(dict(task_id=packet.request_id + ':' + arm,
                request_id=packet.request_id, arm=arm, proposal_key=packet.request_id))
    order = {rid: i for i, rid in enumerate(plan['smoke_ids'][method])}
    tasks.sort(key=lambda t: (0, order[t['request_id']], ARMS.index(t['arm']))
        if t['request_id'] in order else (1, t['request_id'], ARMS.index(t['arm'])))
    return plan, selected, packets, bases, proposals, tasks


def preflight(plan_path, method, output):
    plan, selected, packets, bases, proposals, tasks = load_plan(plan_path, method)
    backend = CachedTokenBackend(selected)
    records = []
    for task in tasks:
        packet = packets[task['request_id']]
        candidates = operation.candidate_records(packet, proposals[packet.request_id])
        if len(candidates) < 2:
            continue
        for candidate in candidates:
            for true_code in ('A', 'B'):
                messages = operation.verifier_messages(packet, candidates, candidate['key'], true_code,
                    include_rationales=task['arm'] == ARMS[1])
                request = dict(messages=messages, schema=None, codes=['A', 'B'], allowed_codes=['A', 'B'],
                    seed=42, temperature=0, max_tokens=1, kind='score')
                reject_metadata(request)
                ready = backend.preflight(request)
                physical, _ = backend.prepare(request)
                from cf_moa.contracts import digest
                records.append(dict(task_id=task['task_id'], candidate=candidate['key'], true_code=true_code,
                    input_tokens=backend.count_tokens(request), request_hash=digest(request),
                    rendered_prompt_hash=digest(physical['prompt']), preflight=ready))
    output.mkdir(parents=True, exist_ok=True)
    dump(output/(method.lower()+'_preflight.json'), dict(status='passed', method=method,
        logical_score_requests=len(records), maximum_input_tokens=max(r['input_tokens'] for r in records),
        input_tokens=sum(r['input_tokens'] for r in records), records=records,
        new_model_calls=0, actual_backend_tokenizer_and_score_ingress=True,
        no_new_structured_output_schema=True))
    backend.close()
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--method', choices=('M4','M5'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--gpu', type=int)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    if args.preflight_only:
        print(json.dumps(dict(method=args.method, preflight_requests=preflight(args.plan,args.method,args.output))))
        return
    plan, selected, packets, bases, proposals, tasks = load_plan(args.plan,args.method)
    if args.gpu not in plan['allowed_gpus'] or os.environ.get('CUDA_VISIBLE_DEVICES') != str(args.gpu):
        raise JournalConflict('GPU must be authorized by the run plan with matching CUDA binding')
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        resource = admission(selected,'readout',args.gpu)
        dump(args.output/'resource_admission.json',resource)
        if not resource['ready']:
            raise RuntimeError('Insufficient resources: no inference submitted')
        local = dict(protocol=plan, method=args.method, profile=selected.config,
            profile_source=selected.source, selected_source_sha256=sha256(args.plan))
        journal = ResearchJournal(args.output/'journal.sqlite3',local,
            resume=(args.output/'journal.sqlite3').exists())
        dump(args.output/'plan.json',local)
        backend = JournalBackend(journal,lambda:CachedTokenBackend(selected))
        try:
            smoke = [t for t in tasks if t['request_id'] in plan['smoke_ids'][args.method]]
            status = execute(packets,bases,smoke,proposals,backend,journal,args.output,args.method,plan['generation'])
            dump(args.output/'smoke_status.json',status)
            if not journal.first_error():
                dump(args.output/'smoke_ready.json', dict(method=args.method,
                    expected_tasks=len(smoke), offline_quality_review_required=True,
                    gold_is_not_loaded_by_inference=True))
                while not (args.output/'continue_full.json').exists():
                    if (args.output/'STOP').exists():
                        raise KeyboardInterrupt('Stopped while awaiting offline smoke review')
                    time.sleep(1)
                review = json.loads((args.output/'continue_full.json').read_text())
                if review.get('action') != 'continue_all_predeclared_inputs':
                    raise JournalConflict('Unexpected smoke handoff action')
                # Ordinary wrong answers or single-item failures do not select
                # the remaining sample membership or trigger any resampling.
                status = execute(packets,bases,tasks,proposals,backend,journal,args.output,args.method,plan['generation'])
            print(json.dumps(status,ensure_ascii=False),flush=True)
            if journal.first_error():
                raise SystemExit(1)
        finally:
            journal.export(args.output)
            close_runtime(backend,journal,args.output,active_error=sys.exc_info()[1])


if __name__ == '__main__':
    main()
