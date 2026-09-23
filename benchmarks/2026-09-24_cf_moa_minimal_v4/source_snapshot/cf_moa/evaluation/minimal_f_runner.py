"""Fixed-B/F conditional seed replication of the saved ordinary reanswer control.

The method, prompt, trigger, parser and optional format repair are the unchanged
cycle1 implementation. This entry adds only source binding and seed-run identity;
the existing research runner keeps ordinary item failures in the denominator.
"""
import argparse
from copy import deepcopy
from dataclasses import replace
import fcntl
import json
import os
from pathlib import Path
import sys

from cf_moa.agents import a5_premise
from cf_moa.contracts import Budget, digest, reject_metadata
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.effect_first_runner import ResearchJournal, check_baseline_binding, execute
from cf_moa.evaluation.incremental_runner import CachedTokenBackend
from cf_moa.evaluation.journal import JournalBackend, JournalConflict, UnresolvedCall
from cf_moa.evaluation.native_runner import load_packets
from cf_moa.evaluation.resources import admission
from cf_moa.tools.adopted import sha256
from cf_moa.tools.native_backend import profile


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_plan(path, method):
    plan = json.loads(Path(path).read_text())
    if plan['generation'] != dict(seed=plan['seed'], temperature=0.7, max_tokens=512):
        raise JournalConflict('Only the preregistered seed may differ from cycle1 generation')
    for source, expected in plan['code_sources'].items():
        if sha256(source) != expected:
            raise JournalConflict('Bound method source changed: ' + source)
    selected = profile(method, 'readout')
    if selected.config != plan['methods'][method]['profile']:
        raise JournalConflict('Selected readout profile differs from cycle1')
    local = plan['methods'][method]
    for key in ('inputs', 'bases', 'proposals'):
        if sha256(local[key]) != local[key+'_sha256']:
            raise JournalConflict('Bound current-input source changed: ' + key)
    packets = {p.request_id: replace(p, budget=Budget(**plan['per_task_budget']))
               for p in load_packets(local['inputs'])}
    bases = {row['request_id']: row for row in rows(local['bases'])}
    proposals = {row['proposal_key']: row['proposal'] for row in rows(local['proposals'])}
    reject_metadata(proposals)
    tasks = local['tasks']
    if len({t['task_id'] for t in tasks}) != len(tasks):
        raise JournalConflict('Duplicate task identity')
    if [t['request_id'] for t in tasks] != plan['panel_ids']:
        raise JournalConflict('Every fixed panel member must appear exactly once')
    for task in tasks:
        if task['arm'] != 'a5_reanswer':
            raise JournalConflict('This runner permits only the saved ordinary control')
        check_baseline_binding(packets[task['request_id']], bases[task['request_id']])
    references = {}
    if local.get('reference_calls'):
        if sha256(local['reference_calls']) != local['reference_calls_sha256']:
            raise JournalConflict('Saved real request source changed')
        references = {row['request_id']: row for row in rows(local['reference_calls'])
                      if row['request_id'].endswith(':a5_reanswer') and row['ordinal'] == 0}
    return plan, selected, packets, bases, proposals, tasks, references


class BoundJournalBackend(JournalBackend):
    """Before submission, compare the new first request with the actual old one."""
    def __init__(self, journal, factory, references, seed):
        super().__init__(journal, factory)
        self.references, self.seed = references, seed

    def count_tokens(self, request):
        if request.get('seed') != self.seed:
            raise JournalConflict('Request seed is not the preregistered run seed')
        if self.references and self.ordinal == 0:
            old = self.references.get(self.request_id)
            comparable = deepcopy(request)
            comparable['seed'] = 42
            if old is None or comparable != old['request']:
                raise JournalConflict('Request differs from saved cycle1 beyond its seed')
        count = super().count_tokens(request)
        if self.references and self.ordinal == 0 and self.backend is not None:
            physical, _ = self.backend.prepare(request)
            physical['sampling_params']['seed'] = 42
            if physical != self.references[self.request_id]['physical'][0]['request']:
                raise JournalConflict('Physical request differs from cycle1 beyond its seed')
        return count


class MinimalJournal(ResearchJournal):
    def stop(self, request_id, error, ordinal=None):
        saved = self.lookup(request_id, ordinal) if ordinal is not None else None
        if saved and saved['phase'] == 'submitted':
            physical = json.loads(saved['physical']) if saved['physical'] else []
            if not physical or any(not row.get('event') and
                    row.get('submission_state') != 'not_submitted' for row in physical):
                error = UnresolvedCall('Uncertain physical completion; preserve without resampling: '
                                       + type(error).__name__ + ': ' + str(error))
        if saved and saved['phase'] == 'validating' and getattr(error, 'category', '') == 'schema':
            error = JournalConflict('Bound input grammar failed before submission: ' + str(error))
        return super().stop(request_id, error, ordinal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plans', nargs='+', required=True, type=Path)
    parser.add_argument('--method', required=True, choices=['M4', 'M5'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--gpu', required=True, type=int)
    args = parser.parse_args()
    if os.environ.get('CUDA_VISIBLE_DEVICES') != str(args.gpu):
        raise JournalConflict('GPU binding mismatch')
    prepared = [(path, load_plan(path, args.method)) for path in args.plans]
    if len({data[0]['seed'] for _, data in prepared}) != len(prepared):
        raise JournalConflict('Duplicate requested seed')
    selected = prepared[0][1][1]
    if any(data[1].config != selected.config for _, data in prepared):
        raise JournalConflict('Cannot share an engine across different profiles')
    shared = None
    journals = []
    def factory():
        nonlocal shared
        if shared is None:
            shared = CachedTokenBackend(selected)
        return shared
    try:
        resource = admission(selected, 'readout', args.gpu)
        if not resource['ready']:
            raise RuntimeError('Insufficient resources; no model request submitted')
        for path, data in prepared:
            plan, _, packets, bases, proposals, tasks, references = data
            output = args.output / ('seed_' + str(plan['seed'])) / args.method.lower()
            output.mkdir(parents=True, exist_ok=True)
            with (output/'run.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                local_plan = dict(protocol=plan, method=args.method, profile=selected.config,
                    profile_source=selected.source, selected_source_sha256=sha256(path),
                    code_sources=plan['code_sources'])
                journal = MinimalJournal(output/'journal.sqlite3', local_plan,
                    resume=(output/'journal.sqlite3').exists())
                journals.append((journal, output))
                dump(output/'plan.json', local_plan)
                dump(output/'resource_admission.json', resource)
                backend = BoundJournalBackend(journal, factory, references, plan['seed'])
                status = execute(packets, bases, tasks, proposals, backend, journal,
                    output, args.method, plan['generation'])
                print(json.dumps(dict(seed=plan['seed'], method=args.method, **status)), flush=True)
                if journal.first_error():
                    raise SystemExit(1)
    finally:
        active_error = sys.exc_info()[1]
        engine = shared.close() if shared is not None else 'not_initialized'
        for journal, output in journals:
            journal.export(output)
            journal.db.close()
            dump(output/'lifecycle.json', dict(status='closed', engine=engine, journal='closed',
                shared_engine_across_fixed_seeds=True, inference_results_rewritten=False,
                new_model_calls=0, original_exception=None if active_error is None else
                dict(type=type(active_error).__name__, message=str(active_error))))


if __name__ == '__main__':
    main()
