"""Offline native metrics; cached controls first, candidate arms only by explicit flag.
No model callbacks, old-head execution, canonical diagnosis table, or method edits.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
import csv
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace

ROOT = Path('/home/data3/txy'); sys.path.insert(0, str(ROOT))
from cf_moa.contracts import digest
from cf_moa.evaluation.native_scoring import SCORER, NORMALIZER, score_proposal
from cf_moa.evaluation.score_run import unit_summaries
from cf_moa.evaluation.paired_metrics import paired_metrics
from cf_moa.tools.adopted import sha256
HERE=Path(__file__).resolve().parent; RUN=HERE.parent
V4=ROOT/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
BUNDLE=ROOT/'Documents/Codex/2026-09-24/cf_moa_v4_trigger_diagnosis_20260924'
DEV=ROOT/'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
spec=importlib.util.spec_from_file_location('v4_saved_metrics',V4/'analysis/score_and_compare.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
BASE_ARMS=['F', 'replace_42','replace_43','replace_44','append_one_42','append_one_43','append_one_44','pool_old_plus_three']
CANDIDATE_ARMS=['candidate_only','candidate_with_rationales']
SOURCES={}

def read(path, lines=False):
    path=Path(path);SOURCES[str(path)]=sha256(path)
    text=path.read_text()
    return [json.loads(line) for line in text.splitlines() if line.strip()] if lines else json.loads(text)

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def write(path,rows):path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))

def narrow_scorer():
    ns={'json':json,'re':re}
    for path,names in [(NORMALIZER,{'norm'}),(SCORER,{'parse','score'})]:
        SOURCES[str(path)]=sha256(path)
        nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
        assert {n.name for n in nodes}==names
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
    return SimpleNamespace(**{k:ns[k] for k in ('norm','parse','score')}),{}

# Execute only the unmodified auxiliary block, without re-running old main scores.
wrapper=Path(sys.modules[score_proposal.__module__].__file__)
func=next(n for n in ast.parse(wrapper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='score_proposal')
aux_node=next(n for n in func.body if isinstance(n,ast.If) and isinstance(n.test,ast.Compare)
    and isinstance(n.test.left,ast.Subscript) and isinstance(n.test.left.value,ast.Name)
    and n.test.left.value.id=='native_item')
AUX_CODE=compile(ast.Module(body=[aux_node],type_ignores=[]),str(wrapper),'exec')

def aux_only(item,evaluation,value):
    ns=dict(native_item=item,evaluation=evaluation,value=value,result={},available=value is not None)
    exec(AUX_CODE,ns)
    return ns['result'].get('document_detection')

class Scoring:
    def __init__(self, output_root=None):
        self.path=Path(output_root or HERE)/'score_cache.jsonl';self.cache={};self.calls=0;self.aux_calls=0
        self.scorer=narrow_scorer()
        # Reuse immutable prior scores, but isolate newly scored responses from
        # the preserved original analysis when a recovery output root is set.
        prior=HERE/'score_cache.jsonl'
        if prior!=self.path and prior.exists():
            self.cache={r['cache_key']:r for r in read(prior,True)}
        if self.path.exists():
            self.cache.update({r['cache_key']:r for r in read(self.path,True)})
    def score(self,item,evaluation,native,existing=None):
        if existing is not None:
            result=deepcopy(existing)
            if item['answer_format']=='robustness_single' and 'document_detection' not in result:
                result['document_detection']=aux_only(item,evaluation,native)
                result['auxiliary_score_origin']='supplemented_this_analysis_from_unchanged_native_auxiliary_block'
                self.aux_calls+=1
            else:result['auxiliary_score_origin']='reused_existing_auxiliary_score'
            result['score_origin']='reused_existing_complete_response_score'
            return result
        assert item['answer_format'] in ('single','robustness_single','relation'), 'No diagnosis or wider native rescoring permitted'
        key=digest(dict(item=item,evaluation=evaluation,native=native,scorer=sha256(SCORER),normalizer=sha256(NORMALIZER),wrapper=sha256(wrapper)))
        if key not in self.cache:
            result=score_proposal(item,evaluation,dict(native_proposal=native,
                applicability='supported' if native is not None else 'failed'),scorer=self.scorer)
            self.cache[key]=dict(cache_key=key,result=result)
            with self.path.open('a') as stream:stream.write(json.dumps(self.cache[key],ensure_ascii=False)+'\n')
            self.calls+=1
        return dict(self.cache[key]['result'],score_origin='new_response_native_score_cached_by_full_response_and_evaluation')

def summed_cost(calls):
    result=old.old_score.physical_cost(calls)
    result['logical_score_callbacks']=0
    result['score_request_attempts']=sum(c.get('request',{}).get('kind')=='score' for c in calls)
    result['physical_score_requests']=sum(len(c.get('physical') or []) for c in calls if c.get('request',{}).get('kind')=='score')
    result['generation_requests']=sum(c.get('request',{}).get('kind')=='generate' for c in calls)
    result['missing_code_fetch_requests']=sum(len(c.get('request',{}).get('allowed_codes') or [])==1 and c.get('request',{}).get('kind')=='score' for c in calls)
    return result

def compact_call(call):
    return {k:v for k,v in call.items() if k in ('physical','phase','status')} | {'request':{k:call.get('request',{}).get(k) for k in ('kind','allowed_codes')}}

def auxiliary_summary(rows):
    values=[r['document_detection'] for r in rows if 'document_detection' in r]
    return dict(native_mapping_denominator=len(values),valid=sum(v['valid'] for v in values),
        exact=sum(v['exact'] is True for v in values),unavailable=sum(v['exact'] is None for v in values),
        exact_full_denominator=sum(v['exact'] is True for v in values)/len(values) if values else None,
        tp=sum(v['tp'] or 0 for v in values),fp=sum(v['fp'] or 0 for v in values),fn=sum(v['fn'] or 0 for v in values),
        correction_semantic_score=None,weighting='native mappings; unique-input auxiliary also reported separately')

def comparison_or_empty(rows, baseline):
    """An absent analysis stratum has no rate, not an invented zero accuracy."""
    if rows:
        return old.comparison(rows, baseline)
    return dict(old.old_score.compare([], baseline),
        counts=old.old_score.counts([]), accuracy_full_denominator=None)

def main(include_candidate=False, runs_root=None, plan_path=None, output_root=None):
    root=Path(output_root or HERE);root.mkdir(parents=True,exist_ok=True)
    out=root/('complete_results' if include_candidate else 'cached_results');out.mkdir(exist_ok=True)
    runs_root=Path(runs_root or RUN/'runs')
    active_plan=read(plan_path) if plan_path else None
    scoring=Scoring(root); cached=read(RUN/'cached_controls/cached_policy_predictions.jsonl',True)
    cached_by={(r['panel'],r['method'],r['request_id']):r for r in cached}
    trigger_meta={}
    with (BUNDLE/'analysis/per_trigger_seed.csv').open() as stream:
        for row in csv.DictReader(stream):trigger_meta[row['panel'],row['method'],row['request_id']]=row
    samples={}
    for entry in read(BUNDLE/'sample_manifest.json')['samples']:
        sample=read(BUNDLE/entry['sample_path']); identity=(sample['panel'],sample['method'],sample['request_id'])
        samples[identity]=dict(base=sample['base_result']['record']['native_answer'],
            reanswers={seed:dict(native=s['output']['record']['result']['native_answer'],
                calls=[compact_call(c['record']) for c in s['model_calls']]) for seed,s in sample['reanswers'].items()})
    observed={};candidate_calls={};run_status={}
    if include_candidate:
        for method in ('M4','M5'):
            path=runs_root/method.lower();statuspath=path/'status.json'
            run_status[method]=read(statuspath) if statuspath.exists() else {'status':'not_started'}
            if (path/'proposals.jsonl').exists():
                for row in read(path/'proposals.jsonl',True):
                    ident=(method,row['request_id'],row['arm'].removeprefix('a5_'))
                    if ident in observed:raise ValueError('Duplicate candidate output identity')
                    observed[ident]=row
            candidate_calls[method]=read(path/'model_calls.jsonl',True) if (path/'model_calls.jsonl').exists() else []
    all_native=[];all_unique=[];reports=[];costs=[]
    for panel in ('historical121','natural52'):
        natural=panel=='natural52';source=V4/'analysis'/panel;offline=(V4/'natural_scope' if natural else DEV)/'offline'
        evaluations=read(offline/'evaluations.jsonl',True);items={r['request_id']:r for r in read(offline/'items.jsonl',True)}
        pairs=[dict(p,left=p['left_record_id'],right=p['right_record_id']) for p in read(offline/'pairs.jsonl',True)]
        meta=old.metadata(items,evaluations);by_id=defaultdict(list)
        for e in evaluations:by_id[e['request_id']].append(e)
        previous=read(source/'native_scored.jsonl',True);prior={(r['method'],r['seed'],r['record_id']):r for r in previous}
        prior_unique=read(source/'per_input_status.jsonl',True)
        prior_cost=read(source/'cost.json');old_summary=read(source/'summary.json')
        plan=read(V4/'natural_scope/plan_seed_42.json' if natural else V4/'seeds/seed_43/plan.json')
        for method in ('M4','M5'):
            bases={r['request_id']:r for r in read(plan['methods'][method]['bases'],True)}
            base_unique={r['request_id']:r for r in prior_unique if r['method']==method and r['seed'] is None}
            supported={r['request_id'] for r in prior_unique if r['method']==method and r.get('F_supported')}
            triggered={rid for p,m,rid in samples if p==panel and m==method}
            for arm in BASE_ARMS+(CANDIDATE_ARMS if include_candidate else []):
                native=[];unique=[];calls=[];logical=0;failure_count=0;missing=0;fallbacks=0
                for rid in items:
                    ident=(panel,method,rid);sample=samples.get(ident);value=bases[rid]['native_answer'];status='cached_B';origin_seed=None
                    if arm.startswith('replace_'):origin_seed=int(arm.split('_')[-1])
                    if rid in triggered and arm!='F':
                        if arm in CANDIDATE_ARMS:
                            row=observed.get((method,rid,arm))
                            if row is None:value=None;status='not_submitted';missing+=1
                            else:
                                if row['input_hash']!=bases[rid]['input_hash']:raise ValueError('Candidate input hash mismatch')
                                value=row.get('result',{}).get('native_answer');status=row.get('result',{}).get('status',row['status'])
                                tr=row.get('result',{}).get('trace',{});logical+=tr.get('logical_score_calls',0)
                                failure_count+=status in ('technical_failure','failed','unavailable')
                                fallbacks+=bool(tr.get('fallback_saved_F'))
                        else:
                            row=next(r for r in cached_by[ident]['rows'] if r['arm']==arm)
                            value=row['native_response'];status='saved_cached_control'
                            for seed in row['supplementary_seeds_used']:calls.extend(sample['reanswers'][seed]['calls'])
                    records=[]
                    for evaluation in by_id[rid]:
                        record_id=evaluation['record_id'];existing=None
                        # Scores are reusable only for the very same complete native response.
                        if value==bases[rid]['native_answer']:existing=prior[method,None,record_id]
                        elif sample:
                            for seed,data in sample['reanswers'].items():
                                if value==data['native']:
                                    existing=prior[method,int(seed),record_id];break
                        if arm.startswith('replace_') and rid not in triggered:
                            existing=prior[method,origin_seed,record_id]
                        score=scoring.score(items[rid],evaluation,value,existing)
                        scored=dict(score,panel=panel,method=method,arm=arm,request_id=rid,record_id=record_id,run_status=status)
                        records.append(scored);native.append(scored)
                    correct=None if any(r['correct'] is None for r in records) else all(r['correct'] for r in records)
                    auxiliary=[r['document_detection'] for r in records if 'document_detection' in r]
                    unique.append(dict(panel=panel,method=method,arm=arm,request_id=rid,correct=correct,
                        native_valid=value is not None,run_status=status,triggered=rid in triggered,
                        native_answer_ref=digest(value) if value is not None else None,
                        auxiliary_exact=(None if not auxiliary or any(a['exact'] is None for a in auxiliary) else all(a['exact'] for a in auxiliary)),
                        has_auxiliary=bool(auxiliary),**meta[rid]))
                if arm in CANDIDATE_ARMS:
                    calls=[c for c in candidate_calls[method] if c['request_id'].endswith(':a5_'+arm) and c['request_id'].split(':')[0] in triggered]
                comparison=old.comparison(unique,base_unique);units=unit_summaries(native,evaluations)
                selection=[]
                for row in unique:
                    tm=trigger_meta.get((panel,method,row['request_id']))
                    if tm and tm['F_path']!='full_nli_equal_paths_native_completion':
                        covered=tm['old_pool_has_joint_correct_key'] in ('True','true','1')
                        selection.append((covered,row['correct'] is True))
                pool_covered=sum(a for a,b in selection);pool_correct=sum(a and b for a,b in selection)
                report=dict(panel=panel,method=method,arm=arm,**comparison,
                    result_status='pending_incomplete_do_not_claim_final_quality' if missing or (arm in CANDIDATE_ARMS and run_status[method].get('status') not in ('complete','complete_with_item_failures')) else 'complete',
                    missing_candidate_inputs=missing,technical_failures=failure_count,explicit_saved_F_fallbacks=fallbacks,
                    native_unit_metrics=units,auxiliary_mapping_metrics=auxiliary_summary(native),
                    auxiliary_unique_metrics=dict(denominator=sum(r['has_auxiliary'] for r in unique),exact=sum(r['auxiliary_exact'] is True for r in unique),unavailable=sum(r['has_auxiliary'] and r['auxiliary_exact'] is None for r in unique)),
                    trigger_comparison=old.comparison([r for r in unique if r['triggered']],base_unique),
                    F_supported_comparison=old.comparison([r for r in unique if r['request_id'] in supported],base_unique),
                    full_panel_base_identity='fixed strong B; F only in the pre-existing supported branch',
                    candidate_pool=dict(non_NLI_inputs=len(selection),covered=pool_covered,covered_selected_correct=pool_correct,
                        selection_rate_given_covered=pool_correct/pool_covered if pool_covered else None,
                        no_correct_candidate=len(selection)-pool_covered,no_correct_candidate_scored_correct=sum(not a and b for a,b in selection)),
                    strata=old.stratify(unique,base_unique,meta),
                    trigger_path_strata={path:comparison_or_empty([r for r in unique if r['triggered'] and trigger_meta[panel,method,r['request_id']]['F_path']==path],base_unique) for path in ('full_nli_equal_paths_native_completion','full_native_key_maj5_absolute_majority_stop')},
                    pairs=paired_metrics({r['record_id']:r for r in native},pairs,resamples=2000))
                inherited=prior_cost['methods'][method]['inherited_B']; extra=summed_cost(calls);extra['logical_score_callbacks']=logical
                cost=dict(panel=panel,method=method,arm=arm,inherited_B=inherited,extra_execution=extra,
                    extra_origin='new_candidate_score_requests' if arm in CANDIDATE_ARMS else 'previously_paid_cached_calls_not_new_this_analysis',
                    attributed_input_tokens=inherited['reused_head_input_tokens']+extra['live_input_tokens'],
                    attributed_output_tokens=inherited['reused_head_output_tokens']+extra['live_output_tokens'],
                    attributed_model_requests=inherited['reused_head_model_requests']+extra['new_model_requests'],
                    model_seconds_interpretation='cumulative model event time; inherited timing may be unknown; not exclusive end-to-end latency')
                reports.append(report);costs.append(cost);all_native.extend(native);all_unique.extend(unique)
    write(out/'native_scored.jsonl',all_native);write(out/'per_input_status.jsonl',all_unique)
    dump(out/'summary.json',dict(include_candidate=include_candidate,independent_evaluation=False,
        complete_denominators_retained=True,new_model_calls_during_analysis=0,reports=reports))
    dump(out/'cost.json',dict(costs=costs,do_not_sum_inherited_B_across_arms_as_new_physical_cost=True))
    lines=['# Saved controls and candidate verification: exposed development results','',
        'Full original denominators; main and auxiliary metrics use unchanged native functions. NLI is not converted to votes. Candidate results are omitted until explicitly requested; pending output is never final quality.','',
        '| Panel | Backbone | Arm | Correct / full denominator | Repairs | Harms | Native unit mean | Status |',
        '|---|---|---|---:|---:|---:|---:|---|']
    for r in reports:
        metric=next(x for x in r['native_unit_metrics']['categories'] if x['category']=='ALL')['mean_native_unit_score']
        lines.append(f"| {r['panel']} | {r['method']} | {r['arm']} | {r['counts']['correct']}/{r['counts']['denominator']} | {r['repairs']} | {r['harms']} | {metric:.6f} | {r['result_status']} |")
    lines+=['','Source/family/format strata, trigger-only results, pair both-correct metrics, candidate-pool selection and auxiliary-field scores are in summary.json.','',
        'Natural B document_detection was absent historically: this analysis supplements only the unchanged auxiliary block and labels its origin; it does not replace historical main scores. Correction semantic quality remains unscored.',
        'Saved-control calls were already paid; three cached reanswers represent three extra calls at deployment. Candidate scoring costs include missing-code physical fetches. Model seconds are cumulative event times, not exclusive GPU latency.']
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    # A cache is deliberately append-only during this invocation, so exclude its
    # old checksum from source invariance; all actual source inputs remain exact.
    SOURCES.pop(str(scoring.path),None)
    if any(sha256(path)!=value for path,value in SOURCES.items()):raise RuntimeError('Scoring input changed')
    dump(out/'receipt.json',dict(actual_new_native_score_calls=scoring.calls,
        auxiliary_only_backfills=scoring.aux_calls,canonical_table_read=False,new_model_calls=0,
        source_hashes=SOURCES,script_sha256=sha256(__file__),score_cache_sha256=sha256(scoring.path) if scoring.path.exists() else None,
        reused_functions=['native_scoring.score_proposal','score_run.unit_summaries','paired_metrics.paired_metrics'],
        candidate_run_status=run_status,candidate_runs_root=str(runs_root),
        active_plan_path=str(plan_path) if active_plan is not None else None))
    print(json.dumps(dict(output=str(out),actual_new_native_score_calls=scoring.calls,auxiliary_only_backfills=scoring.aux_calls,groups=len(reports))))

def smoke(method, runs_root=None, plan_path=None, output_root=None):
    """Fixed smoke quality review, never an accuracy-dependent launch decision."""
    import math
    import sqlite3
    plan_path=Path(plan_path or RUN/'plan.json');plan=read(plan_path);ids=plan['smoke_ids'][method]
    root=Path(output_root or HERE);root.mkdir(parents=True,exist_ok=True)
    out=root/('smoke_'+method.lower());out.mkdir(exist_ok=True)
    run=Path(runs_root or RUN/'runs')/method.lower();status=read(run/'smoke_status.json') if (run/'smoke_status.json').exists() else {'status':'not_started'}
    if (run/'proposals.jsonl').exists(): outputs=read(run/'proposals.jsonl',True)
    elif (run/'journal.sqlite3').exists():
        with sqlite3.connect('file:'+str(run/'journal.sqlite3')+'?mode=ro',uri=True) as db:
            outputs=[json.loads(r[0]) for r in db.execute('SELECT record FROM outputs')]
    else:outputs=[]
    index={(r['request_id'],r['arm'].removeprefix('a5_')):r for r in outputs if r['request_id'] in ids}
    selected={r['request_id']:r for r in plan['inputs'][method] if r['request_id'] in ids}
    scoring=Scoring(root);records=[]
    for rid in ids:
        sample=read(selected[rid]['path']);panel=sample['panel'];packet=sample['input_packet']['record'];f=sample['f_proposal']['record']['proposal']
        offline=V4/'natural_scope/offline' if panel=='natural52' else DEV/'offline'
        item=next(r for r in read(offline/'items.jsonl',True) if r['request_id']==rid)
        evaluations=[r for r in read(offline/'evaluations.jsonl',True) if r['request_id']==rid]
        previous=read(V4/'analysis'/panel/'native_scored.jsonl',True)
        base_scores={r['record_id']:r for r in previous if r['method']==method and r['seed'] is None and r['request_id']==rid}
        with (BUNDLE/'analysis/per_trigger_seed.csv').open() as stream:
            saved=next(r for r in csv.DictReader(stream) if r['panel']==panel and r['method']==method and r['request_id']==rid)
        golds=json.loads(saved['gold_keys']);baseline_correct=all(r['correct'] is True for r in base_scores.values())
        old_candidates={key for key in f['trace'].get('predictions',[]) if key is not None}
        for arm in CANDIDATE_ARMS:
            row=index.get((rid,arm));result=(row or {}).get('result',{});native=result.get('native_answer');tr=result.get('trace',{})
            scores=tr.get('scores',{});finite=bool(scores) and all(type(v) in (int,float) and math.isfinite(v) for v in scores.values())
            original_index=tr.get('selected_original_response_index');whole=False
            if type(original_index) is int and 0<=original_index<len(f['trace'].get('responses',[])):
                whole=native==json.loads(f['trace']['responses'][original_index])
            if f['trace'].get('route')=='full_nli_equal_paths_native_completion':whole=native==f['native_proposal'];finite=tr.get('logical_score_calls')==0
            complete_native=False
            if native is not None:
                import jsonschema
                try:jsonschema.validate(native,packet['answer_schema']);complete_native=True
                except jsonschema.ValidationError:pass
            score_rows=[]
            if row is not None:
                for evaluation in evaluations:
                    existing=base_scores[evaluation['record_id']] if native==sample['base_result']['record']['native_answer'] else None
                    score_rows.append(dict(scoring.score(item,evaluation,native,existing),record_id=evaluation['record_id']))
            correct=None if not score_rows or any(r['correct'] is None for r in score_rows) else all(r['correct'] for r in score_rows)
            ranks={key:1+sum(value>scores[key] for value in scores.values()) for key in golds if key in scores} if finite and scores else {}
            records.append(dict(panel=panel,method=method,request_id=rid,arm=arm,
                run_status=result.get('status',(row or {}).get('status','not_submitted')),baseline_correct=baseline_correct,
                correct=correct,repair=correct is True and not baseline_correct,harm=correct is False and baseline_correct,
                candidate_scores=scores,gold_keys=golds,gold_candidate_ranks=ranks,correct_candidate_in_pool=all(g in old_candidates for g in golds),
                score_finite=finite,all_old_candidates_retained=set(scores)==old_candidates,
                complete_existing_native_response_returned=whole,original_native_schema_valid=complete_native,
                selected_key=(native or {}).get('answer_choice'),logical_score_calls=tr.get('logical_score_calls',0),
                fallback_saved_F=bool(tr.get('fallback_saved_F')),
                physical_model_requests=row.get('cost',{}).get('physical_model_requests') if row else 0,
                native_scores=score_rows,offline_gold_used_only_here=True))
    strata=[]
    for arm in CANDIDATE_ARMS:
        for base_correct in (False,True):
            group=[r for r in records if r['arm']==arm and r['baseline_correct']==base_correct]
            strata.append(dict(arm=arm,baseline_correct=base_correct,inputs=len(group),correct=sum(r['correct'] is True for r in group),
                repairs=sum(r['repair'] for r in group),harms=sum(r['harm'] for r in group),unavailable=sum(r['correct'] is None for r in group)))
    # Runtime integrity is distinct from effectiveness. Bad accuracy never fails
    # this flag and never changes the fixed remaining membership or sampling.
    passed=len(index)==2*len(ids) and all(r['score_finite'] and r['all_old_candidates_retained'] and r['complete_existing_native_response_returned']
        and r['original_native_schema_valid'] and r['run_status']=='verified_candidate_selection' for r in records)
    summary=dict(method=method,scope='fixed_four_input_smoke_only_not_full_panel',inputs=len(ids),arms=CANDIDATE_ARMS,
        status='smoke_review_complete' if len(index)==2*len(ids) else 'smoke_outputs_incomplete',
        execution_contract_passed=passed,accuracy_is_not_continuation_gate=True,
        verified_candidate_selections=sum(r['run_status']=='verified_candidate_selection' for r in records),
        technical_failures=sum(r['run_status']=='technical_failure' for r in records),
        explicit_saved_F_fallbacks=sum(r['fallback_saved_F'] for r in records),
        run_status=status,records=records,strata=strata,new_model_calls_during_review=0,
        actual_new_native_score_calls=scoring.calls,canonical_table_read=False)
    dump(out/'summary.json',summary)
    dump(out/'receipt.json',dict(source_hashes=SOURCES,script_sha256=sha256(__file__),new_model_calls=0,
        actual_new_native_score_calls=scoring.calls,canonical_table_read=False,
        candidate_runs_root=str(run.parent),active_plan_path=str(plan_path)))
    print(json.dumps(dict(output=str(out),execution_contract_passed=passed,status=summary['status'],strata=strata)))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--include-candidate',action='store_true')
    parser.add_argument('--smoke-only',action='store_true')
    parser.add_argument('--method',choices=['M4','M5'])
    parser.add_argument('--runs-root',type=Path,help='Directory containing m4/ and m5/; defaults to the preserved original runs')
    parser.add_argument('--plan',type=Path,help='Fixed plan associated with these runs')
    parser.add_argument('--output-root',type=Path,help='Isolated parent for smoke/complete results and newly scored response cache')
    args=parser.parse_args()
    if args.smoke_only:
        if not args.method:parser.error('--smoke-only requires --method')
        smoke(args.method,args.runs_root,args.plan,args.output_root)
    else:main(args.include_candidate,args.runs_root,args.plan,args.output_root)
