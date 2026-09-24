"""Run one independent expert; inference never loads an evaluation ledger."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import time

from cf_moa.agents import (a1_support_completion as a1,a2_support_revision as a2,
    a3_contrastive_comparison as a3,a4_intervention_execution as a4,a5_robust_readout as a5)
from cf_moa.agents import a1_bounded_coverage as a1_v2
from cf_moa.agents import a1_relational_coverage as a1_r3
from cf_moa.agents import a1_coded_coverage as a1_r5
from cf_moa.controller import native_sampling, evidence_highlighting, single_agent_tools
from cf_moa.contracts import Budget,InputPacket
from cf_moa.evaluation.a4_repair import dump
from cf_moa.evaluation.journal import RunJournal,JournalBackend,JournalConflict,UnresolvedCall
from cf_moa.evaluation.resources import admission
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.adopted import a4_adopted,sha256
from cf_moa.tools.experiment_config import prototype
from cf_moa.tools.native_backend import profile,NativeBackend
from cf_moa.tools.vllm_backend import VLLMBackend
from cf_moa.tools.schema_compat import OutputSchemaError


def execute(expert,packet,session,method):
    if expert=='A1':return a1.run(packet,session)
    if expert=='A1_v2':return a1_v2.run(packet,session)
    if expert=='A1_v2_system':return a1_v2.run(packet,session,prompt_revision='system_context')
    if expert=='A1_v2_explicit':return a1_v2.run(packet,session,prompt_revision='explicit_contract')
    if expert=='A1_v2_relational':return a1_r3.run(packet,session)
    if expert=='A1_v2_whitespace':return a1_r3.run(packet,session,decoding_revision='bounded_whitespace_16_r4')
    if expert=='A1_v2_codes':return a1_r5.run(packet,session)
    if expert=='native_sampling':return native_sampling.run(packet,session)
    if expert=='A1_resource_control':return a1_v2.run_resource_control(packet,session)
    if expert=='A1_highlight_control':return evidence_highlighting.run(packet,session)
    if expert=='same_tools_single_agent':return single_agent_tools.run(packet,session,method=method)
    if expert=='A2':return a2.run(packet,session)
    if expert=='A3':return a3.run(packet,session,method=method)
    if expert=='A3_edit':return a3.run(packet,session,method=method,arm='bounded_edit')
    if expert=='A4':return a4.run(packet,session,method=method)
    if expert=='A5':return a5.run_views(packet,session)
    if expert=='F':return a5.run_legacy(packet,session)
    raise ValueError('Unknown independent expert')


def code_lock():
    root=Path(__file__).resolve().parents[1]
    return {str(p.relative_to(root)):sha256(p) for p in sorted(root.rglob('*'))
            if p.suffix in ('.py','.json') and 'tests' not in p.parts}


def load_packets(path):
    packets=[]
    with Path(path).open() as stream:
        for line in stream:
            row=json.loads(line)
            row['budget']=Budget(**row.get('budget',{}))
            packets.append(InputPacket(**row))
    if len({p.request_id for p in packets})!=len(packets):
        raise ValueError('Duplicate opaque input handle')
    return packets


def output_flags(proposal):
    """Contract/binding outcomes, without consulting gold or changing the head."""
    if proposal.applicability=='unsupported':
        return dict(output_schema_invalid=False,semantic_invalid=False,coverage_incomplete=False)
    if proposal.variant==single_agent_tools.VARIANT:
        trace=proposal.trace
        return dict(output_schema_invalid=trace['schema_invalid'],semantic_invalid=trace['semantic_invalid'],
            coverage_incomplete=False,budget_exhausted=trace['budget_exhausted'],
            semantic_result=trace['semantic_result'],method_score='not_scored')
    if proposal.variant in (*a1_v2.PROMPT_VARIANTS.values(), a1_r3.VARIANT, a1_r3.DECODING_VARIANT, a1_r5.VARIANT, evidence_highlighting.VARIANT):
        trace=proposal.trace
        return dict(output_schema_invalid=trace.get('schema_invalid',False),
            semantic_invalid=trace.get('semantic_invalid',False),
            coverage_incomplete=bool(trace.get('missing_candidates')),
            audit_overflow=trace.get('overflow',False),
            degenerate_audit=trace.get('degenerate_audit',False),
            semantic_result=trace.get('semantic_result','unavailable'),
            method_score='not_scored')
    schema_invalid=proposal.native_proposal is None or any(
        c['type']=='format_validation' and c.get('passed') is False for c in proposal.checks)
    trace=proposal.trace
    if proposal.agent_id=='A1' and 'raw_coverage' in trace:
        schema_invalid=schema_invalid or trace.get('audit') is None
    return dict(output_schema_invalid=schema_invalid,
        semantic_invalid=bool(trace.get('rejected_coverage')) and trace.get('audit') is not None,
        coverage_incomplete=bool(trace.get('missing_candidates')))


def run_packets(expert,method,packets,backend,journal,output):
    """Single in-flight callback; latch first runtime error before another item."""
    started=time.monotonic()
    for p in packets:
        if journal.output(p.request_id) is not None:
            continue
        if journal.first_error():
            break
        had_calls=journal.count(p.request_id)>0
        backend.begin_item(p.request_id)
        session=ModelSession(p,backend);before=time.monotonic()
        try:
            proposal=execute(expert,p,session,method)
            if backend.unresolved:raise backend.unresolved
            backend.finish_item()
            proposal.cost.update(journal.cost(p.request_id))
            proposal.cost['prior_interrupted_tool_cost_unknown']=had_calls
            record=dict(status='complete',proposal=proposal.to_dict(),**output_flags(proposal))
            if record['output_schema_invalid']:
                # The unchanged native head has returned its full result. Keep
                # that result, but do not send another experiment input.
                coverage_failed=expert in ('A1','A1_v2','A1_v2_system','A1_v2_explicit','A1_v2_relational','A1_v2_whitespace','A1_v2_codes') and proposal.trace.get('audit') is None
                error=OutputSchemaError('Coverage response failed original A1 schema' if coverage_failed
                    else 'Native result failed its original output schema')
                journal.stop(p.request_id,error,0 if coverage_failed else max(0,backend.ordinal-1))
                record.update(status='invalid_output',error_type=type(error).__name__,error=str(error))
        except Exception as error:
            journal.stop(p.request_id,error,backend.ordinal)
            record=dict(status='blocked_unresolved_call' if isinstance(error,UnresolvedCall) else 'failed',
                error_type=type(error).__name__,error=str(error),proposal=None)
        journal.save_output(p.request_id,dict(request_id=p.request_id,input_hash=p.input_hash,
            elapsed_seconds=time.monotonic()-before,**record,
            cost=dict(session.cost_since(),**journal.cost(p.request_id)),
            reused_same_run_responses=backend.reused,prior_interrupted_tool_cost_unknown=had_calls,
            model_callbacks=session.calls,tool_callbacks=session.tools))
        journal.export(output)
        dump(output/'status.json',dict(status='stopped_on_error' if journal.first_error() else 'running',
            first_error=journal.first_error(),cost=journal.cost()))
        if journal.first_error():
            break
    journal.export(output)
    results=[journal.output(p.request_id) for p in packets]
    first=journal.first_error()
    counts=dict(infrastructure=0,schema=0,semantic_invalid=0,audit_overflow=0,degenerate_audit=0)
    if first and first.get('source')!='output_contract':counts[first['error_category']]+=1
    for row in results:
        if row:
            counts['schema']+=int(row.get('output_schema_invalid',False))
            counts['semantic_invalid']+=int(row.get('semantic_invalid',False))
            counts['audit_overflow']+=int(row.get('audit_overflow',False))
            counts['degenerate_audit']+=int(row.get('degenerate_audit',False))
    status=dict(status='stopped_on_error' if first else 'complete',first_error=first,
        complete=sum(r is not None and r['status']=='complete' for r in results),
        failed=sum(r is not None and r['status'] in ('failed','invalid_output') for r in results),
        blocked=sum(r is not None and r['status']=='blocked_unresolved_call' for r in results),
        not_submitted=sum(r is None for r in results),failure_counts=counts,
        invocation_elapsed_seconds=time.monotonic()-started,cost=journal.cost(),
        request_counts=journal.request_counts(),
        current_initialization_seconds=backend.backend.initialization_seconds if backend.backend else 0,
        interpretation='Runtime errors and returned schema-invalid outputs stop submissions. Original native-head internal handling and all responses are preserved; semantic binding negatives are counted without using gold or changing the method.')
    with (output/'input_status.jsonl').open('w') as stream:
        for p,row in zip(packets,results):
            stream.write(json.dumps(dict(request_id=p.request_id,input_hash=p.input_hash,
                status=row['status'] if row else 'not_submitted_after_error'),ensure_ascii=False)+'\n')
    dump(output/'status.json',status)
    return status


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--expert',choices=['A1','A1_v2','A1_v2_system','A1_v2_explicit','A1_v2_relational','A1_v2_whitespace','A1_v2_codes','native_sampling','A1_resource_control','A1_highlight_control','same_tools_single_agent','A2','A3','A3_edit','A4','A5','F'],required=True)
    parser.add_argument('--method',choices=['M4','M5'],required=True)
    parser.add_argument('--inputs',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--gpu',type=int,required=True)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--origin-manifest',type=Path)
    args=parser.parse_args()
    assert os.environ['CUDA_VISIBLE_DEVICES']==str(args.gpu)
    args.output.mkdir(parents=True,exist_ok=args.resume)
    lock=(args.output/'run.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    packets=load_packets(args.inputs)
    role={'A1':'readout','A1_v2':'readout','A1_v2_system':'readout','A1_v2_explicit':'readout','A1_resource_control':'readout',
          'A1_v2_relational':'readout','A1_v2_whitespace':'readout','A1_v2_codes':'readout','native_sampling':'readout','A1_highlight_control':'readout','same_tools_single_agent':'readout',
          'A2':'facts','A3':'catalog','A3_edit':'readout','A5':'readout','F':'readout'}.get(args.expert,'a4')
    selected=a4_adopted(args.method) if role=='a4' else profile(args.method,role)
    plan=dict(expert=args.expert,method=args.method,input_file_sha256=sha256(args.inputs),
        input_hashes={p.request_id:p.input_hash for p in packets},config=selected.config,
        config_source=selected.source,code_lock=code_lock(),
        origin_manifest=dict(path=str(args.origin_manifest),sha256=sha256(args.origin_manifest)) if args.origin_manifest else None,
        experimental_policy=prototype() if args.expert in ('A1','A3_edit','A5') else None,
        a1_v2_policy=a1_v2.config() if args.expert in ('A1_v2','A1_v2_system','A1_v2_explicit','A1_resource_control') else None,
        relational_policy=a1_r3.config() if args.expert in ('A1_v2_relational','A1_v2_whitespace') else None,
        coded_policy=a1_r5.config() if args.expert=='A1_v2_codes' else None,
        decoding_revision='bounded_whitespace_16_r4' if args.expert in ('A1_v2_whitespace','A1_v2_codes') else None,
        sampling_policy=native_sampling.config() if args.expert=='native_sampling' else None,
        highlight_policy=evidence_highlighting.config() if args.expert=='A1_highlight_control' else None,
        single_agent_policy=single_agent_tools.config() if args.expert=='same_tools_single_agent' else None,
        inference_scope='current packets only; no gold, labels, paired endpoint or evaluation file')
    journal=RunJournal(args.output/'journal.sqlite3',plan,resume=args.resume)
    if not args.resume:dump(args.output/'plan.json',plan)
    remaining=[p for p in packets if journal.output(p.request_id) is None]
    if remaining and not journal.first_error():
        resources=admission(selected,role,args.gpu)
        dump(args.output/'resource_admission.json',resources)
        if not resources['ready']:
            dump(args.output/'status.json',dict(status='waiting_for_resources',resources=resources,cost=journal.cost()))
            raise SystemExit(75)
    backend=JournalBackend(journal,lambda:(VLLMBackend if role=='a4' else NativeBackend)(selected))
    status=run_packets(args.expert,args.method,packets,backend,journal,args.output)
    if status['status']=='stopped_on_error':
        raise SystemExit(1)


if __name__=='__main__':main()
