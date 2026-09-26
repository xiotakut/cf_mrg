"""One original formal C0 readout per input, with durable batched transport.

This runner has no F pool, verification, retries, answer repair, or new schema
gate. It uses c0_native's exact historical profile, request and raw parser.
"""
import argparse
from collections import Counter, deque
from dataclasses import replace
import fcntl
import json
import math
import os
from pathlib import Path
import time

from cf_moa.contracts import Budget, digest
from cf_moa.evaluation import c0_native, resources
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.effect_first_runner import ResearchJournal
from cf_moa.evaluation.journal import JournalConflict
from cf_moa.evaluation.native_runner import load_packets
from cf_moa.evaluation.run_moa_rcv import stream_cost, stream_export
from cf_moa.evaluation.run_moa_rcv_batched import FrontierBackend, NeedCallback, submit_batch
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import CONFIG_ROOT, sha256
from cf_moa.tools.vllm_backend import VLLMBackend


class C0Backend(VLLMBackend):
    """Retain VLLMBackend.prepare, not NativeBackend's F sampling adapter."""
    def __init__(self, selected):
        super().__init__(selected)
        self._token_counts = {}

    def count_tokens(self, request):
        key = digest(request)
        if key not in self._token_counts:
            self._token_counts[key] = super().count_tokens(request)
        return self._token_counts[key]

    def preflight(self, request):
        if self.count_tokens(request) + request['max_tokens'] > self.adopted.engine['max_model_len']:
            raise ValueError('Complete formal C0 request exceeds its original context capacity; no truncation')
        return super().preflight(request)

    def close(self):
        if self.llm is not None:
            try:
                self.llm.llm_engine.engine_core.shutdown()
            finally:
                self.llm = None
        self._token_counts.clear()


def resource_admission(selected, gpu):
    """Estimate the installed V1 memory equation using original engine values.

    This version subtracts profiled peak (including external allocations) from
    total * utilization. It has no free >= total * utilization startup rule.
    Thus free must cover weights, full-context KV, the utilization reserve and
    an explicitly estimated profiling margin. No F-role memory floor applies.
    """
    engine = selected.engine_kwargs()
    card = next(row for row in resources.memory() if row['gpu'] == gpu)
    fraction = engine['gpu_memory_utilization']
    model = Path(engine['model'])
    architecture = json.loads((model/'config.json').read_text())
    architecture = architecture.get('text_config', architecture)
    weights = json.loads((model/'model.safetensors.index.json').read_text())['metadata']['total_size']
    policy = json.loads((CONFIG_ROOT/'resource_admission.json').read_text())
    if engine['dtype'] != 'bfloat16' or engine.get('num_gpu_blocks_override') is not None:
        raise ValueError('C0 resource estimate expects its original BF16 profile without fixed KV override')
    head_dim = architecture.get('head_dim') or architecture['hidden_size']//architecture['num_attention_heads']
    kv_bytes = (2 * policy['model_dtype_bytes'] * architecture['num_hidden_layers'] *
        architecture['num_key_value_heads'] * head_dim * engine['max_model_len'])
    reserve = card['total_mib'] * 2**20 * (1-fraction)
    margin = policy['profile_and_runtime_margin_gib'] * 2**30
    minimum_free_mib = math.ceil((weights + kv_bytes + reserve + margin)/2**20)
    worker = Path('/home/data3/txy/MedRGAG/.venv/lib/python3.10/site-packages/vllm/v1/worker/gpu_worker.py')
    return dict(card=card, ready=card['free_mib'] >= minimum_free_mib,
        requirement=dict(minimum_free_mib=minimum_free_mib,
            gpu_memory_utilization=fraction, engine_kwargs=engine,
            config_hash=selected.config_hash,
            weights_gib=weights/2**30, max_context_kv_gib=kv_bytes/2**30,
            utilization_reserve_gib=reserve/2**30,
            unmeasured_profile_runtime_margin_gib=policy['profile_and_runtime_margin_gib'],
            installed_worker=dict(path=str(worker), sha256=sha256(worker)),
            status='cpu_estimate_not_gpu_measurement',
            basis='weights + full_context_KV + total_memory*(1-utilization) + estimated_profile_margin',
            limitation='Installed worker profiles external allocations in peak. Margin is an estimate; actual initialization may still fail. No F memory floor or parameter override.'))


def load_plan(path, method):
    plan = json.loads(Path(path).read_text())
    if plan.get('schema_version') != 'formal_C0_run_v1':
        raise ValueError('C0 draft/spec is not runnable; require formal_C0_run_v1 after the declared freeze')
    if 'draft' in plan.get('status', '').lower() or plan.get('status', '').startswith('not_'):
        raise ValueError('A draft C0 plan cannot launch a model')
    for source, expected in plan.get('code_sources', {}).items():
        if sha256(source) != expected:
            raise JournalConflict('Bound C0 runtime source changed: ' + source)
    chosen = c0_native.profile(method)
    selected = plan['methods'][method]
    for key, actual in [('original_C0_profile', chosen.source),
                        ('engine_kwargs', chosen.engine_kwargs()), ('sampling', chosen.config)]:
        if selected.get(key) != actual:
            raise JournalConflict('Frozen C0 ' + key + ' differs from its original formal profile')
    packets = {}
    for source in [selected, *selected.get('additional_inputs', [])]:
        if sha256(source['inputs']) != source['inputs_sha256']:
            raise JournalConflict('Bound C0 legal inputs changed: ' + source['inputs'])
        for packet in load_packets(source['inputs']):
            if packet.request_id in packets:
                raise ValueError('Duplicate C0 input would repeat a formal readout: ' + packet.request_id)
            packets[packet.request_id] = packet
    if not packets:
        raise ValueError('C0 requires an explicit nonempty input manifest')
    return plan, packets


def execute(plan, packets, method, output, gpu, *, runtime_factory=None):
    chosen = c0_native.profile(method)
    batch_size = chosen.config['batch_size']
    if batch_size > chosen.engine['max_num_seqs']:
        raise JournalConflict('Original C0 batch/engine binding is inconsistent')
    budget = Budget(max_model_requests=1, max_input_tokens=chosen.engine['max_model_len'],
                    max_output_tokens=chosen.config['max_tokens'], max_tool_calls=0)
    tasks = [dict(task_id=rid + ':C0', request_id=rid) for rid in packets]
    local = dict(protocol=plan, method=method, mode='formal_C0_live_batched',
        profile=chosen.config, profile_source=chosen.source, engine_kwargs=chosen.engine_kwargs(),
        input_hashes={rid: packet.input_hash for rid, packet in packets.items()},
        budget=budget.__dict__, scheduler_source=dict(path=str(Path(__file__).resolve()), sha256=sha256(__file__)))
    journal = ResearchJournal(output/'journal.sqlite3', local, resume=(output/'journal.sqlite3').exists())
    dump(output/'plan.json', local)
    engine = None

    def runtime():
        nonlocal engine
        if engine is None:
            try:
                if runtime_factory is None:
                    admission = resource_admission(chosen, gpu)
                    dump(output/'resource_admission.json', admission)
                    if not admission['ready']:
                        raise MemoryError('Original C0 engine allocation exceeds free memory')
                engine = runtime_factory(chosen) if runtime_factory else C0Backend(chosen)
            except Exception as error:
                raise JournalConflict('Shared C0 backend initialization failed before submission: '
                                      + type(error).__name__ + ': ' + str(error)) from error
        return engine

    backend = FrontierBackend(journal, runtime)
    waiting = deque(task for task in tasks if journal.output(task['task_id']) is None)
    started = time.monotonic()
    batches = 0

    def advance(task, allow_suspend):
        packet = replace(packets[task['request_id']], budget=budget)
        key = task['task_id']
        backend.begin_item(key)
        session = ModelSession(packet, backend)
        before = time.monotonic()
        try:
            result = c0_native.run(packet, session, method)
            backend.finish_item()
            record = dict(status='complete' if result['native_available'] else 'unavailable', result=result)
        except NeedCallback as need:
            if allow_suspend and need.ordinal == 0:
                return need
            error = JournalConflict('C0 attempted an unexpected additional or repeated physical request')
            journal.stop(key, error, need.ordinal)
            record = dict(status='failed', error_type=type(error).__name__, error=str(error))
        except Exception as error:
            journal.stop(key, error, backend.ordinal)
            record = dict(status='failed', error_type=type(error).__name__, error=str(error))
        if 'result' not in record:
            record['result'] = dict(native_answer=None, native_available=False,
                                   failure_type=record['error_type'], raw_response=None)
        # SQL, rather than continuation wall time, is the actual physical cost.
        cost = journal.cost(key)
        record['result']['cost'] = cost
        journal.save_output(key, dict(task_id=key, request_id=packet.request_id,
            method=method, arm='C0', input_hash=packet.input_hash,
            elapsed_seconds=time.monotonic()-before, cost=cost,
            model_callbacks=session.calls, tool_callbacks=[],
            scheduling='one_formal_readout_SQL_transport_recovery', **record))
        return None

    try:
        while waiting and not journal.first_error() and not (output/'STOP').exists():
            chunk = [waiting.popleft() for _ in range(min(batch_size, len(waiting)))]
            pending, suspended = [], []
            for task in chunk:
                if journal.first_error():
                    break
                need = advance(task, True)
                if need is not None:
                    pending.append(need)
                    suspended.append(task)
            if pending and not journal.first_error():
                submit_batch(pending, runtime(), journal)
                batches += 1
                for task in suspended:
                    if journal.first_error():
                        break
                    advance(task, False)
            dump(output/'status.json', dict(status='running', planned=len(tasks),
                completed=journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0],
                batches=batches, first_systemic_error=journal.first_error()))
        counts = Counter(json.loads(row[0])['status'] for row in journal.db.execute('SELECT record FROM outputs'))
        unfinished_submitted = 0
        for task in tasks:
            if journal.output(task['task_id']) is not None:
                continue
            call = journal.lookup(task['task_id'], 0)
            if call is None:
                continue
            physical = json.loads(call['physical']) if call['physical'] is not None else []
            sent = any('event' in row or row.get('submission_state') in ('accepted', 'attempted_unknown')
                       for row in physical) or (call['phase'] == 'submitted' and not physical)
            unfinished_submitted += int(sent)
        unfinished_outputs = len(tasks)-sum(counts.values())
        status = dict(status='stopped_on_systemic_error' if journal.first_error() else
            'stopped_by_request' if (output/'STOP').exists() else 'complete',
            method=method, mode='formal_C0_live_batched', planned=len(tasks),
            complete=counts['complete'], failed=counts['failed'], unavailable=counts['unavailable'],
            not_submitted=unfinished_outputs-unfinished_submitted,
            unfinished_outputs=unfinished_outputs, unfinished_submitted=unfinished_submitted,
            request_counts=journal.request_counts(), batches=batches, batch_size=batch_size,
            first_systemic_error=journal.first_error(), cost=stream_cost(journal),
            elapsed_seconds=time.monotonic()-started, ordinary_item_failure_stops_batch=False,
            one_original_readout_per_input=True, retry_count=0,
            native_validity='Unchanged native scorer decides; raw original parser has no added schema gate.')
        dump(output/'status.json', status)
        return status
    finally:
        stream_export(journal, output)
        try:
            if engine is not None:
                engine.close()
        finally:
            journal.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--method', required=True, choices=('M4', 'M5'))
    parser.add_argument('--gpu', required=True, type=int)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    plan, packets = load_plan(args.plan, args.method)
    if args.gpu not in plan.get('allowed_gpu_ids', []):
        raise ValueError('GPU is not authorized by the C0 plan')
    visible = os.environ.get('CUDA_VISIBLE_DEVICES')
    if visible is not None and visible != str(args.gpu):
        raise ValueError('C0 CUDA binding differs from the authorized GPU')
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        status = execute(plan, packets, args.method, args.output, args.gpu)
    print(json.dumps(status, ensure_ascii=False), flush=True)
    if status['status'] != 'complete':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
