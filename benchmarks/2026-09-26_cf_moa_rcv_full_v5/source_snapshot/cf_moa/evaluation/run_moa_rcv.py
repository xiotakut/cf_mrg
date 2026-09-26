"""Cached/live thin RCV system runner; evaluation records are never loaded.

Plan methods bind either ``inputs`` (InputPacket JSONL), or existing ``samples``
containing input_packet/base_result/f_proposal records. Optional tasks select a
declared arm; otherwise ``arms`` are run for every input using a shared B/F pool.
Cached score_journal is opened read-only and exact requests must match.
"""
import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import replace
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

from cf_moa.contracts import Budget, InputPacket, ModelResult, digest
from cf_moa.controller import moa_rcv, strong_legacy
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.effect_first_runner import ResearchJournal
from cf_moa.evaluation.incremental_runner import CachedTokenBackend
from cf_moa.evaluation.journal import JournalBackend, JournalConflict, serialized
from cf_moa.evaluation.native_runner import load_packets
from cf_moa.evaluation.resources import admission
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import a4_adopted, sha256
from cf_moa.tools.native_backend import profile
from cf_moa.tools.vllm_backend import VLLMBackend

ARM_ALIASES = {'a5_candidate_only': 'candidate_only',
               'a5_candidate_with_rationales': 'candidate_with_rationales'}


def _check_file(path, expected=None):
    path = Path(path)
    if expected and sha256(path) != expected:
        raise JournalConflict('Bound source changed: ' + str(path))
    return path


def _rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_plan(path, method):
    plan = json.loads(Path(path).read_text())
    if plan.get('schema_version') != 'moa_rcv_run_v1':
        raise ValueError('This CLI requires schema_version moa_rcv_run_v1, not the design spec')
    if plan.get('f_disagreement_reanswer', False):
        raise ValueError('Ordinary replacement and RCV cannot be stacked')
    for source, expected in plan.get('code_sources', {}).items():
        _check_file(source, expected)
    selected = plan['methods'][method]
    packets, pools, bases = {}, {}, {}
    if 'samples' in selected:
        for source in selected['samples']:
            sample = json.loads(_check_file(source['path'], source.get('sha256')).read_text())
            value = dict(sample['input_packet']['record'])
            value['budget'] = Budget(**value.get('budget', {}))
            packet = InputPacket(**value)
            if packet.request_id in packets:
                raise ValueError('Duplicate opaque input handle')
            packets[packet.request_id] = packet
            pools[packet.request_id] = sample['f_proposal']['record']['proposal']
            bases[packet.request_id] = sample['base_result']['record']
    else:
        packets = {packet.request_id: packet for packet in load_packets(
            _check_file(selected['inputs'], selected.get('inputs_sha256')))}
    for field, target in [('saved_f_proposals', pools), ('saved_bases', bases)]:
        if field in selected:
            for row in _rows(_check_file(selected[field], selected.get(field + '_sha256'))):
                target[row['request_id']] = row.get('proposal', row.get('result', row))
    if 'per_task_budget' in plan:
        packets = {key: replace(packet, budget=Budget(**plan['per_task_budget']))
                   for key, packet in packets.items()}
    arms = selected.get('arms', plan.get('arms', ['candidate_with_rationales']))
    tasks = selected.get('tasks', [dict(task_id=key + ':' + arm, request_id=key, arm=arm)
                                 for key in packets for arm in arms])
    if len({task['task_id'] for task in tasks}) != len(tasks):
        raise ValueError('Duplicate task identity')
    for task in tasks:
        arm = ARM_ALIASES.get(task['arm'], task['arm'])
        if arm not in moa_rcv.VARIANTS or task['request_id'] not in packets:
            raise ValueError('Unknown arm or packet in task')
    return plan, selected, packets, pools, bases, tasks


class SavedScoreBackend:
    """Real historical model responses, exact request comparison, zero inference."""
    def __init__(self, path, journal):
        self.db = sqlite3.connect('file:' + str(Path(path).resolve()) + '?mode=ro', uri=True) if path else None
        self.journal = journal
        self.ordinal = 0
        self.source_task_id = None

    def begin_item(self, task_id):
        self.source_task_id, self.ordinal = task_id, 0

    def _row(self, request):
        if self.db is None:
            raise JournalConflict('Cached verification requires a saved score journal')
        row = self.db.execute('SELECT request,reserved_tokens,status,result FROM calls '
            'WHERE request_id=? AND ordinal=?', (self.source_task_id, self.ordinal)).fetchone()
        if not row or row[2] != 'complete':
            raise JournalConflict('Missing complete historical score: ' + str(self.source_task_id) + ':' + str(self.ordinal))
        if digest(json.loads(row[0])) != digest(request):
            raise JournalConflict('Cached final model request differs: ' + self.source_task_id + ':' + str(self.ordinal))
        return row

    def count_tokens(self, request):
        return self._row(request)[1]

    def __call__(self, request):
        row = self._row(request)
        value = json.loads(row[3])
        events = deepcopy(value['events'])
        for event in events:
            original = deepcopy(event)
            event.update(mode='replay', elapsed_seconds=0.0, original_event=original,
                         recovery='exact_saved_candidate_score_request')
        self.ordinal += 1
        return ModelResult(value['value'], events)

    def finish_item(self):
        count = self.db.execute('SELECT COUNT(*) FROM calls WHERE request_id=?',
            (self.source_task_id,)).fetchone()[0] if self.db else 0
        if count != self.ordinal:
            raise JournalConflict('Cached execution did not consume exactly its historical requests')

    def close(self):
        if self.db:
            self.db.close()


class AdoptedA4Backend(CachedTokenBackend):
    # Keep original A4 physical request/interpretation and common engine cleanup.
    prepare = VLLMBackend.prepare
    interpret = VLLMBackend.interpret


def selected_profile(method, role):
    return a4_adopted(method) if role == 'a4' else profile(method, role)


def _initial_native(packet):
    if packet.baseline_response is None:
        return {}
    try:
        return {'initial_native': json.loads(packet.baseline_response)}
    except (TypeError, ValueError):
        return {}


def stream_export(journal, output):
    """Bound memory to one saved row; full-v5 traces may exceed process RAM."""
    for name, query in [('proposals.jsonl', 'SELECT record FROM outputs ORDER BY rowid'),
        ('model_calls.jsonl', 'SELECT request_id,ordinal,request,status,phase,result,physical,error '
                             'FROM calls ORDER BY rowid')]:
        temp = output/(name + '.tmp')
        with temp.open('w') as stream:
            for row in journal.db.execute(query):
                if name == 'proposals.jsonl':
                    stream.write(row[0] + '\n')
                else:
                    rid, ordinal, request, status, phase, result, physical, error = row
                    stream.write(serialized(dict(request_id=rid, ordinal=ordinal,
                        request=json.loads(request), status=status, phase=phase,
                        result=json.loads(result) if result else None,
                        physical=json.loads(physical) if physical else None,
                        error=json.loads(error) if error else None)) + '\n')
        temp.replace(output/name)
    if journal.first_error():
        dump(output/'first_error.json', journal.first_error())


def stream_cost(journal):
    value = dict(physical_model_requests=0, new_model_requests=0, live_input_tokens=0,
        live_output_tokens=0, live_model_seconds=0.0, recorded_call_wall_seconds=0.0,
        unfinished_call_wall_unknown=0, unresolved_model_usage=0,
        submission_attempts=0, failed_attempts=0)
    for status, phase, physical, start, end in journal.db.execute(
            'SELECT status,phase,physical,started,finished FROM calls'):
        value['submission_attempts'] += 1
        value['failed_attempts'] += int(status == 'failed')
        value['unfinished_call_wall_unknown'] += int(end is None)
        if end is not None:
            value['recorded_call_wall_seconds'] += max(0, end-start)
        entries = json.loads(physical) if physical is not None else []
        value['physical_model_requests'] += len(entries)
        value['unresolved_model_usage'] += int(physical is None and phase == 'submitted')
        for entry in entries:
            event = entry.get('event')
            if event is None:
                value['unresolved_model_usage'] += int(entry.get('submission_state') != 'not_submitted')
            elif event['mode'] == 'live':
                value['new_model_requests'] += 1
                value['live_input_tokens'] += event['input_tokens']
                value['live_output_tokens'] += event['output_tokens']
                value['live_model_seconds'] += event['elapsed_seconds']
    value.update(model_usage_complete=value['unresolved_model_usage'] == 0,
                 cost_basis='unique durable physical records; one-row streaming accumulation')
    return value


def execute(plan, selected, packets, pools, bases, tasks, method, mode, output, gpu=None):
    local = dict(protocol=plan, method=method, mode=mode)
    journal = ResearchJournal(output/'journal.sqlite3', local,
                              resume=(output/'journal.sqlite3').exists())
    dump(output/'plan.json', local)
    backend = (SavedScoreBackend(selected.get('score_journal'), journal) if mode == 'cached'
               else JournalBackend(journal, lambda: None))
    active_role = None
    expected = {row['task_id']: row for row in _rows(selected['expected_outputs'])} if selected.get('expected_outputs') else {}
    verification_checks = []
    remaining = Counter(task['request_id'] for task in tasks)
    def release_finished_input(rid):
        remaining[rid] -= 1
        if not remaining[rid]:
            pools.pop(rid, None)
            bases.pop(rid, None)
    start = time.monotonic()
    try:
        for task in tasks:
            key, rid = task['task_id'], task['request_id']
            old_row = journal.output(key)
            if old_row is not None:
                old_result = old_row.get('result', {})
                if old_result.get('f_proposal') is not None:
                    pools[rid] = old_result['f_proposal']
                if old_row.get('status') == 'complete':
                    bases[rid] = old_result
                release_finished_input(rid)
                continue
            if journal.first_error() or (output/'STOP').exists():
                break
            packet = packets[rid]
            arm = ARM_ALIASES.get(task['arm'], task['arm'])
            component, _ = strong_legacy.select(packet)
            role = moa_rcv.profile_role(packet)
            if mode == 'cached' and component == 'F' and rid not in pools:
                journal.stop(key, JournalConflict('Cached input has no real saved F pool'), 0)
                break
            if mode == 'live' and role != active_role:
                if backend.backend is not None:
                    backend.backend.close()
                    backend.backend = None
                chosen = selected_profile(method, role)
                declared = plan.get('profiles', {}).get(method, {}).get(role)
                if declared is not None and declared != chosen.config:
                    raise JournalConflict('Actual role profile differs from frozen run plan')
                def factory(chosen=chosen, role=role):
                    resource = admission(chosen, role, gpu)
                    dump(output/('resource_admission_' + role + '.json'), resource)
                    if not resource['ready']:
                        raise MemoryError('Insufficient authorized GPU memory for unchanged ' + role + ' profile')
                    return (AdoptedA4Backend if role == 'a4' else CachedTokenBackend)(chosen)
                backend.factory, active_role = factory, role
            source_task_id = task.get('source_task_id', key)
            backend.begin_item(source_task_id if mode == 'cached' else key)
            session = ModelSession(packet, backend)
            before = time.monotonic()
            try:
                result = moa_rcv.run(packet, session, method=method, mode=arm,
                    seed=plan.get('verification_seed', 42),
                    saved_f_proposal=pools.get(rid),
                    saved_base=bases.get(rid) if component != 'F' else None,
                    **_initial_native(packet))
                backend.finish_item()
                if result['f_proposal'] is not None:
                    pools[rid] = result['f_proposal']
                if component != 'F':
                    bases[rid] = result
                record = dict(status='complete' if result['native_valid'] else 'unavailable', result=result)
                if source_task_id in expected:
                    prior = expected[source_task_id]['result']
                    same = (result['native_answer'] == prior['native_answer'] and
                            result['verification']['trace'] == prior['trace'])
                    verification_checks.append(dict(task_id=key, source_task_id=source_task_id,
                        complete_native_and_verification_trace_equal=same))
                    if not same:
                        raise JournalConflict('Cached full response or verification trace differs')
            except Exception as error:
                journal.stop(key, error, backend.ordinal)
                record = dict(status='failed', error_type=type(error).__name__, error=str(error),
                    result=dict(native_answer=None, native_valid=False, cost=session.cost_since()))
            journal.save_output(key, dict(task_id=key, request_id=rid, method=method,
                arm=arm, input_hash=packet.input_hash, elapsed_seconds=time.monotonic()-before,
                model_callbacks=session.calls, tool_callbacks=session.tools,
                cost=session.cost_since(), **record))
            release_finished_input(rid)
            dump(output/'status.json', dict(status='running', planned=len(tasks),
                completed=journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0],
                first_systemic_error=journal.first_error()))
        counts = Counter()
        for task in tasks:
            row = journal.output(task['task_id'])
            counts[row['status'] if row else 'not_submitted'] += 1
        status = dict(status=('stopped_on_systemic_error' if journal.first_error() else
                              'stopped_by_request' if (output/'STOP').exists() else 'complete'),
            planned=len(tasks), complete=counts['complete'], unavailable=counts['unavailable'],
            failed=counts['failed'], not_submitted=counts['not_submitted'],
            first_systemic_error=journal.first_error(), cost=stream_cost(journal),
            elapsed_seconds=time.monotonic()-start,
            ordinary_item_failure_stops_batch=False, mode=mode)
        dump(output/'status.json', status)
        dump(output/'cached_equality.json', dict(checks=verification_checks,
            all_equal=all(row['complete_native_and_verification_trace_equal'] for row in verification_checks),
            new_model_calls=0 if mode=='cached' else None))
        return status
    finally:
        stream_export(journal, output)
        try:
            if mode == 'cached':
                backend.close()
            elif backend.backend is not None:
                backend.backend.close()
        finally:
            journal.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--method', required=True, choices=('M4', 'M5'))
    parser.add_argument('--mode', required=True, choices=('cached', 'live'))
    parser.add_argument('--gpu', type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    plan, selected, packets, pools, bases, tasks = load_plan(args.plan, args.method)
    if args.mode == 'live':
        if args.gpu not in plan.get('allowed_gpus', []):
            raise ValueError('The requested GPU is not authorized by this plan')
        visible = os.environ.get('CUDA_VISIBLE_DEVICES')
        if visible is not None and visible != str(args.gpu):
            raise ValueError('Existing CUDA binding differs from requested authorized GPU')
        os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        status = execute(plan, selected, packets, pools, bases, tasks, args.method,
                         args.mode, args.output, args.gpu)
    print(json.dumps(status, ensure_ascii=False), flush=True)
    if status['status'] != 'complete':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
