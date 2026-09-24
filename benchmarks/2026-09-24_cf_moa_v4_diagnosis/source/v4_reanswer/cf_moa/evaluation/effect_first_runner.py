"""Effect-first research runner: durable results, ordinary item failures continue.

Inference loads legal packets and saved proposals only; evaluation is separate.
Reuses the existing backend, SQL journal and explicit engine shutdown.
"""
import argparse
from dataclasses import replace
import fcntl
import json
import os
from pathlib import Path
import sys
import time

from cf_moa.contracts import Budget, digest, reject_metadata
from cf_moa.controller import effect_first
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.incremental_runner import CachedTokenBackend, close_runtime
from cf_moa.evaluation.journal import RunJournal, JournalBackend, JournalConflict, UnresolvedCall, serialized
from cf_moa.evaluation.native_runner import load_packets
from cf_moa.evaluation.resources import admission
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import sha256
from cf_moa.tools.native_backend import profile


def systemic(error):
    if isinstance(error, (JournalConflict, UnresolvedCall, MemoryError)):
        return True
    text = (type(error).__name__ + ': ' + str(error)).lower()
    return any(term in text for term in (
        'enginedead', 'engine core failed', 'enginecore encountered', 'cuda error',
        'out of memory', 'connection refused', 'broken pipe', 'connection reset',
        'token count disagrees', 'evaluation metadata is not an inference input'))


class ResearchJournal(RunJournal):
    """Preserve every error; only broken execution integrity stops this run."""
    def stop(self, request_id, error, ordinal=None):
        if systemic(error):
            return super().stop(request_id, error, ordinal)
        value = dict(request_id=request_id, ordinal=ordinal, error_type=type(error).__name__,
                     message=str(error), at=time.time(), action='record_item_error_continue')
        key = 'item_error:' + request_id + ':' + str(ordinal)
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, serialized(value)))
        return value


def check_baseline_binding(packet, base):
    # A documented unavailable B has no answer reference. Keep that original
    # failure in the fixed denominator; it is not a mismatched saved answer.
    unavailable = (base.get('native_valid') is False and base.get('native_answer') is None
                   and base.get('base_answer_ref') is None)
    if packet.input_hash != base['input_hash'] or (
            not unavailable and digest(base['native_answer']) != base['base_answer_ref']):
        raise ValueError('Wrong input/baseline binding')


def method_sources(tasks):
    paths = [Path(__file__), Path(effect_first.__file__)]
    if any(task['arm'].startswith('a1_binding_') for task in tasks):
        from cf_moa.agents import a1_scoped_binding, a1_retrieved_evidence, a1_support_completion
        from cf_moa import contracts
        from cf_moa.tools import adapters
        paths.extend(Path(module.__file__) for module in (
            a1_scoped_binding, a1_retrieved_evidence, a1_support_completion, contracts, adapters))
    if any(task['arm'].startswith('a5_') for task in tasks):
        from cf_moa.agents import a5_premise
        paths.append(Path(a5_premise.__file__))
    if any(task['arm'].startswith('a1_target_') for task in tasks):
        from cf_moa.agents import a1_target_evidence
        paths.append(Path(a1_target_evidence.__file__))
    if any(task['arm'].startswith('a3_original_') for task in tasks):
        from cf_moa.agents import a3_original_compare
        paths.append(Path(a3_original_compare.__file__))
    if any(task['arm'].startswith('a1_search_') for task in tasks):
        from cf_moa.agents import a1_retrieved_evidence
        paths.append(Path(a1_retrieved_evidence.__file__))
        if any(task['arm'] != 'a1_search_query' and task['arm'].startswith('a1_search_') for task in tasks):
            from cf_moa.agents import a1_retrieved_evidence_answers
            paths.append(Path(a1_retrieved_evidence_answers.__file__))
    return {str(path): sha256(path) for path in paths}


def execute(packets, bases, tasks, proposals, backend, journal, output, method, config):
    started = time.monotonic()
    for task in tasks:
        key = task['task_id']
        if journal.output(key) is not None:
            continue
        if journal.first_error():
            break
        packet = packets[task['request_id']]
        base = bases[packet.request_id]
        backend.begin_item(key)
        session = ModelSession(packet, backend)
        before = time.monotonic()
        try:
            target = task.get('target')
            if task.get('target_task'):
                selected = journal.output(task['target_task'])
                target = selected.get('result', {}).get('target') if selected else None
                if target is None:
                    raise ValueError('Shared target selection unavailable; this arm remains unavailable')
            proposal = proposals.get(task.get('proposal_key'))
            if task['arm'] == 'baseline':
                result = dict(native_answer=base['native_answer'], native_valid=base['native_valid'],
                              warnings=[], decision='saved_B', cost=session.cost_since())
            elif task['arm'].startswith('a1_binding_'):
                from cf_moa.agents import a1_scoped_binding
                support = None
                if task['arm'] == 'a1_binding_verdict_only':
                    source_key = task.get('support_source_task')
                    source = journal.output(source_key) if source_key else None
                    if (not source or source.get('arm') != 'a1_binding_scoped'
                            or source.get('method') != method
                            or source.get('request_id') != packet.request_id
                            or source.get('input_hash') != packet.input_hash
                            or source.get('base_answer_ref') != base['base_answer_ref']):
                        raise JournalConflict('Missing or mismatched prior scoped proposal task: '+str(source_key))
                    support = source.get('result')
                try:
                    result = a1_scoped_binding.run(packet, session, base['native_answer'],
                        arm=task['arm'], target=target, saved_proposal=proposal,
                        support_result=support, config=config)
                except a1_scoped_binding.SupportBindingError as error:
                    raise JournalConflict(str(error)) from error
                if task['arm'] == 'a1_binding_verdict_only':
                    result['trace']['support_source_task'] = task['support_source_task']
            elif task['arm'].startswith('a1_search_'):
                from cf_moa.agents import a1_retrieved_evidence
                if task['arm'] == 'a1_search_query':
                    result = a1_retrieved_evidence.run_query(packet, session, base['native_answer'], config=config)
                else:
                    from cf_moa.agents import a1_retrieved_evidence_answers
                    result = a1_retrieved_evidence_answers.run(packet, session, base['native_answer'],
                        arm=task['arm'], target=target, saved_proposal=proposal, config=config)
            elif task['arm'].startswith('a5_'):
                from cf_moa.agents import a5_premise
                result = a5_premise.run(packet, session, base['native_answer'],
                                       proposal, control=task['arm'] == 'a5_reanswer', config=config)
            elif task['arm'].startswith(('a1_target_', 'a3_original_')):
                if task['arm'].startswith('a1_target_'):
                    from cf_moa.agents import a1_target_evidence as operation
                else:
                    from cf_moa.agents import a3_original_compare as operation
                result = operation.run(packet, session, base['native_answer'],
                    control=task['arm'].endswith('_reanswer'), target=target,
                    saved_proposal=proposal, config=config)
            else:
                result = effect_first.run(packet, session, base['native_answer'], task['arm'],
                    saved_proposal=proposal, target=target, config=config)
            backend.finish_item()
            available = bool(result.get('target')) if task['arm'] in ('target_select', 'a1_search_query') else result.get('native_valid', True)
            record = dict(status='complete' if available else 'unavailable', result=result)
        except Exception as error:
            journal.stop(key, error, backend.ordinal)
            record = dict(status='failed', error_type=type(error).__name__, error=str(error),
                          result=dict(native_answer=None, native_valid=False,
                                      failure_type=getattr(error, 'failure_type', type(error).__name__)))
        journal.save_output(key, dict(method=method, request_id=packet.request_id, task_id=key,
            arm=task['arm'], input_hash=packet.input_hash, base_answer_ref=base['base_answer_ref'],
            target=task.get('target'), target_task=task.get('target_task'),
            proposal_key=task.get('proposal_key'), elapsed_seconds=time.monotonic()-before,
            cost=journal.cost(key), model_callbacks=session.calls, **record))
        done = journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0]
        dump(output/'status.json', dict(status='running', completed=done, planned=len(tasks),
                                       first_systemic_error=journal.first_error()))
    journal.export(output)
    rows = [journal.output(t['task_id']) for t in tasks]
    status = dict(status='stopped_on_systemic_error' if journal.first_error() else 'complete',
        planned=len(tasks), complete=sum(bool(r and r['status']=='complete') for r in rows),
        failed=sum(bool(r and r['status']=='failed') for r in rows),
        unavailable=sum(bool(r and r['status']=='unavailable') for r in rows),
        not_submitted=sum(r is None for r in rows), first_systemic_error=journal.first_error(),
        cost=journal.cost(), request_counts=journal.request_counts(),
        elapsed_seconds=time.monotonic()-started, ordinary_item_failure_stops_batch=False)
    dump(output/'status.json', status)
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--method', required=True, choices=['M4', 'M5'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--gpu', required=True, type=int)
    args = parser.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES') != str(args.gpu):
        raise ValueError('GPU binding mismatch')
    plan = json.loads(args.plan.read_text())
    method_plan = plan['methods'][args.method]
    for key in ('inputs', 'bases', 'proposals'):
        path = Path(method_plan[key])
        if sha256(path) != method_plan[key+'_sha256']:
            raise ValueError('Input/source changed: ' + key)
    packets = {p.request_id: replace(p, budget=Budget(**plan['per_task_budget']))
               for p in load_packets(method_plan['inputs'])}
    with Path(method_plan['bases']).open() as stream:
        bases = {row['request_id']: row for row in map(json.loads, stream)}
    with Path(method_plan['proposals']).open() as stream:
        proposals = {row['proposal_key']: row['proposal'] for row in map(json.loads, stream)}
    reject_metadata(proposals)
    tasks = method_plan['tasks']
    if len({t['task_id'] for t in tasks}) != len(tasks):
        raise ValueError('Duplicate task identity')
    for task in tasks:
        packet, base = packets[task['request_id']], bases[task['request_id']]
        check_baseline_binding(packet, base)
    selected = profile(args.method, 'readout')
    args.output.mkdir(parents=True, exist_ok=True)
    lock = (args.output/'run.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    resource = admission(selected, 'readout', args.gpu)
    dump(args.output/'resource_admission.json', resource)
    if not resource['ready']:
        raise RuntimeError('Insufficient resources; no model requests submitted')
    local_plan = dict(protocol=plan, method=args.method, profile=selected.config,
                      profile_source=selected.source, selected_source_sha256=sha256(args.plan),
                      code_sources=method_sources(tasks))
    journal = ResearchJournal(args.output/'journal.sqlite3', local_plan,
                              resume=(args.output/'journal.sqlite3').exists())
    dump(args.output/'plan.json', local_plan)
    backend = JournalBackend(journal, lambda: CachedTokenBackend(selected))
    try:
        status = execute(packets, bases, tasks, proposals, backend, journal, args.output,
                         args.method, plan['generation'])
        print(json.dumps(status, ensure_ascii=False), flush=True)
        if journal.first_error():
            raise SystemExit(1)
    finally:
        journal.export(args.output)
        close_runtime(backend, journal, args.output, active_error=sys.exc_info()[1])


if __name__ == '__main__':
    main()
