"""New incremental experiment entry; durable SQL, one terminal full export.

An optional shared first-error file coordinates independently scheduled GPUs.
The file is checked before every new request; in-flight requests may finish.
"""
import argparse
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import sys
import time
import tempfile
import weakref

from cf_moa.controller import incremental
from cf_moa.agents import a1_delta
from cf_moa.contracts import digest
from cf_moa.evaluation.native_runner import load_packets
from cf_moa.evaluation.journal import RunJournal, JournalBackend, StoppedOnError
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.resources import admission
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import sha256
from cf_moa.tools.native_backend import NativeBackend, profile


class CachedTokenBackend(NativeBackend):
    def __init__(self, selected, stop_path=None):
        super().__init__(selected)
        self._input_counts = {}
        self.stop_path = Path(stop_path) if stop_path else None

    def start(self):
        if getattr(self, '_closed', False):
            raise RuntimeError('Cannot initialize a closed incremental backend')
        super().start()
        # The peer can fail while this engine is loading. Check again at the
        # actual engine-core transport, after preflight and initialization.
        core = self.llm.llm_engine.engine_core
        self._core_original_add_request = core.add_request
        self._core_had_instance_add_request = 'add_request' in vars(core)
        self._core_previous_instance_add_request = vars(core).get('add_request')
        owner = weakref.ref(self)
        def guarded(request, *args, **kwargs):
            backend = owner()
            if backend is None:
                raise RuntimeError('Incremental backend no longer owns this engine')
            if backend.stop_path and backend.stop_path.exists():
                for record in reversed(backend.physical_calls):
                    if record.get('engine_core_request_id') == request.request_id:
                        record['submission_state'] = 'not_submitted'
                        break
                raise StoppedOnError('Shared error before engine-core submission')
            return backend._core_original_add_request(request, *args, **kwargs)
        self._core_guard = guarded
        core.add_request = guarded

    def close(self):
        """Explicit V1 engine cleanup, never a model request or an output rewrite."""
        if getattr(self, '_close_error', None):
            raise RuntimeError('Previous incremental engine shutdown failed: ' + self._close_error)
        if getattr(self, '_closed', False):
            return 'already_closed'
        llm = self.llm
        self._closed = True
        if llm is None:
            return 'not_initialized'
        core = llm.llm_engine.engine_core
        try:
            guard = getattr(self, '_core_guard', None)
            if guard is not None and vars(core).get('add_request') is guard:
                if self._core_had_instance_add_request:
                    core.add_request = self._core_previous_instance_add_request
                else:
                    del core.add_request
            # The installed vLLM V1 MPClient implements shutdown via its
            # idempotent weakref finalizer, which closes workers and IPC.
            core.shutdown()
        except Exception as error:
            self._close_error = type(error).__name__ + ': ' + str(error)
            raise
        finally:
            self.llm = None
            self._core_original_add_request = None
            self._core_previous_instance_add_request = None
            self._core_guard = None
        return 'engine_shutdown'

    def count_tokens(self, request):
        key = digest(request)
        if key not in self._input_counts:
            self._input_counts[key] = super().count_tokens(request)
        return self._input_counts[key]


class SharedStopBackend(JournalBackend):
    def __init__(self, journal, factory, stop_path=None):
        super().__init__(journal, factory)
        self.stop_path = Path(stop_path) if stop_path else None

    def check_peer(self):
        if self.stop_path and self.stop_path.exists():
            raise StoppedOnError('Shared first-error latch: ' + self.stop_path.read_text())

    def count_tokens(self, request):
        self.check_peer()
        return super().count_tokens(request)

    def __call__(self, request):
        self.check_peer()
        return super().__call__(request)


def close_runtime(backend, journal, output, *, active_error=None):
    """Release owned resources on success and failure, preserving inference status."""
    started = time.monotonic()
    errors = []
    engine_status = 'not_constructed'
    try:
        if backend.backend is not None:
            engine_status = backend.backend.close()
    except Exception as error:
        engine_status = 'shutdown_failed'
        errors.append(dict(resource='engine', error_type=type(error).__name__, error=str(error)))
    try:
        journal.db.close()
        journal_status = 'closed'
    except Exception as error:
        journal_status = 'close_failed'
        errors.append(dict(resource='journal', error_type=type(error).__name__, error=str(error)))
    result = dict(status='cleanup_failed' if errors else 'closed', engine=engine_status,
        journal=journal_status, errors=errors, elapsed_seconds=time.monotonic()-started,
        original_exception=None if active_error is None else
            dict(type=type(active_error).__name__, message=str(active_error)),
        inference_results_rewritten=False, new_model_calls=0)
    dump(Path(output)/'lifecycle.json', result)
    if errors and active_error is None:
        raise RuntimeError('Incremental resource cleanup failed; see lifecycle.json')
    return result


def latch(path, value):
    if path is None:
        return
    path = Path(path)
    fd, name = tempfile.mkstemp(prefix='.first-error-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(name, path)  # Publish a complete inode without overwriting a winner.
        except FileExistsError:
            pass
    finally:
        os.unlink(name)


def execute(packets, bases, arms, backend, journal, output, *, method, shared_stop=None):
    started = time.monotonic()
    planned = [(p, arm) for p in packets for arm in arms]
    try:
        for packet, arm in planned:
            key = packet.request_id + ':' + arm
            if journal.output(key) is not None:
                continue
            if journal.first_error() or (shared_stop and Path(shared_stop).exists()):
                break
            backend.begin_item(key)
            session = ModelSession(packet, backend)
            base_row = bases[packet.request_id]
            try:
                base = base_row['native_answer']
                target = incremental.target_for_smoke(packet, base)
                result = incremental.run(packet, session, base, target, arm)
                backend.finish_item()
                record = dict(status='complete', result=result)
            except Exception as error:
                first = journal.stop(key, error, backend.ordinal)
                latch(shared_stop, dict(method=method, **first))
                record = dict(status='failed', error_type=type(error).__name__, error=str(error),
                              native_answer=None, failure_type=getattr(error,'failure_type',None))
            journal.save_output(key, dict(request_id=packet.request_id, journal_key=key,
                arm=arm, input_hash=packet.input_hash, base_answer_ref=base_row['base_answer_ref'],
                baseline_source=base_row.get('source_proof'),
                historical_baseline_cost=base_row.get('cost'),
                cost=journal.cost(key), model_callbacks=session.calls, **record))
            # SQL is authoritative and fsynced. This small status replaces the
            # previous per-input cumulative JSONL export; one full export below.
            done = journal.db.execute('SELECT COUNT(*) FROM outputs').fetchone()[0]
            dump(output / 'status.json', dict(status='stopped_on_error' if journal.first_error() else 'running',
                completed_outputs=done, planned=len(planned), first_error=journal.first_error()))
            if journal.first_error():
                break
    finally:
        journal.export(output)
    records = [journal.output(p.request_id + ':' + a) for p, a in planned]
    peer = json.loads(Path(shared_stop).read_text()) if shared_stop and Path(shared_stop).exists() else None
    status = dict(status='stopped_on_error' if journal.first_error() or peer else 'complete',
        planned=len(planned), complete=sum(bool(r and r['status']=='complete') for r in records),
        failed=sum(bool(r and r['status']=='failed') for r in records),
        not_submitted=sum(r is None for r in records), first_error=journal.first_error(),
        shared_first_error=peer, cost=journal.cost(), request_counts=journal.request_counts(),
        elapsed_seconds=time.monotonic()-started, full_exports=1,
        actual_quality_scoring=False, qualification='technical smoke only, not adoption')
    dump(output/'status.json', status)
    return status


def source_lock():
    root = Path(__file__).resolve().parents[1]
    files = ['agents/a1_delta.py','controller/incremental.py','configs/incremental_v1.json',
             'evaluation/prepare_incremental.py',
             'evaluation/incremental_runner.py','evaluation/journal.py','tools/adapters.py',
             'tools/native_backend.py','tools/vllm_backend.py','tools/evidence_ids.py','contracts.py',
             'agents/a1_support_completion.py','tools/provenance.py','tools/schema_compat.py',
             'tools/legacy.py','tools/adopted.py','configs/native_sources.json',
             'configs/readout_m4.json','configs/readout_m5.json',
             'CF_MED_MoA_Router_Five_Agents_Execution_Plan.md']
    from cf_moa.tools.legacy import R123
    paths = [root / path for path in files]
    paths.extend(p for p in R123.iterdir() if p.suffix in ('.py','.json'))
    return {str(path): sha256(path) for path in paths}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--method', choices=['M4','M5'], required=True)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--bases', type=Path, required=True)
    p.add_argument('--protocol', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--gpu', type=int, required=True)
    p.add_argument('--shared-stop', type=Path)
    args = p.parse_args()
    assert os.environ['CUDA_VISIBLE_DEVICES'] == str(args.gpu)
    protocol = json.loads(args.protocol.read_text())
    assert protocol['status'] == 'fixed_for_technical_smoke'
    assert protocol['method_files'][args.method] == dict(
        inputs=str(args.inputs.resolve()), bases=str(args.bases.resolve()))
    assert protocol['source_hashes'][str(args.inputs)] == sha256(args.inputs)
    assert protocol['source_hashes'][str(args.bases)] == sha256(args.bases)
    assert protocol['code_lock'] == source_lock()
    packets_by_id = {p.request_id:p for p in load_packets(args.inputs)}
    packets = [packets_by_id[rid] for rid in protocol['smoke_ids']]
    bases = {r['request_id']:r for r in map(json.loads,args.bases.read_text().splitlines())}
    for packet in packets:
        row = bases[packet.request_id]
        assert row['input_hash'] == packet.input_hash and row['status'] == 'complete'
        assert digest(row['native_answer']) == row['base_answer_ref']
    selected = profile(args.method,'readout')
    args.output.mkdir(parents=True,exist_ok=False)
    lock=(args.output/'run.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    resource = admission(selected,'readout',args.gpu);dump(args.output/'resource_admission.json',resource)
    if not resource['ready']:
        dump(args.output/'status.json',dict(status='waiting_for_resources',new_model_requests=0))
        raise SystemExit(75)
    plan=dict(variant=incremental.VARIANT,method=args.method,profile=selected.config,
              profile_source=selected.source,protocol=protocol,protocol_sha256=sha256(args.protocol))
    dump(args.output/'plan.json',plan)
    journal=RunJournal(args.output/'journal.sqlite3',plan)
    backend=SharedStopBackend(journal,lambda:CachedTokenBackend(selected,args.shared_stop),args.shared_stop)
    try:
        status=execute(packets,bases,protocol['arms'],backend,journal,args.output,
                       method=args.method,shared_stop=args.shared_stop)
        if status['status']!='complete':raise SystemExit(1)
    finally:
        try:
            close_runtime(backend,journal,args.output,active_error=sys.exc_info()[1])
        finally:
            lock.close()


if __name__=='__main__':main()
