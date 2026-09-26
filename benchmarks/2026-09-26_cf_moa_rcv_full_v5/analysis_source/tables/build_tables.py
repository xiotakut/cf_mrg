"""Saved-result table assembly and independent C5 arithmetic audit; no grader."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path('/home/data3/txy')
HERE = Path(__file__).resolve().parent
OUT = HERE
RUN = HERE.parent
REC = ROOT/'Documents/Codex/2026-09-24/cf_moa_candidate_verify_20260924/recovery_gpu23'
OLD = REC/'analysis/complete_results'
V4 = ROOT/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
DEV = ROOT/'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
ARMS = {'C0':'original', 'C1':'F', 'C2':'candidate_only', 'C3':'candidate_with_rationales',
        'C4':'pool_old_plus_three', 'C5':'joint_selector'}
SOURCES = {}


def read(path, lines=False):
    path = Path(path); SOURCES[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if lines else json.loads(path.read_text())


def dump(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


def write(name, rows):
    (OUT/name).write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))


def units(scored, evaluations):
    by = {r['record_id']:r for r in scored}; grouped = defaultdict(list)
    for e in evaluations:
        if e['role'] == 'reference': continue
        for category in ('ALL', *e['evaluation_labels']):
            grouped[e['unit_id'], e['resource_id'], category].append(e['record_id'])
    result=[]
    for (unit, source, category), ids in sorted(grouped.items()):
        missing=[rid for rid in ids if rid not in by]
        result.append(dict(unit_id=unit, source=source, category=category, native_records=len(ids),
            missing_mapping_ids=missing,
            score=None if missing else sum(by[r]['correct'] is True for r in ids)/len(ids),
            unavailable=sum(by[r]['correct'] is None for r in ids if r in by)))
    return result


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=HERE)
    parser.add_argument('--c0-only',action='store_true',help='Reuse existing tables and update only saved natural C0 results.')
    args=parser.parse_args();OUT=args.output.resolve()
    if args.c0_only and OUT==HERE:
        parser.error('--c0-only requires an explicit separate --output directory')
    OUT.mkdir(parents=True,exist_ok=True)
    from c0_supplement import load_supplement, cost_row, supplement_tables
    if args.c0_only:
        status=supplement_tables(HERE,OUT,read,dump,write,units)
        dump('receipt.json',dict(at=datetime.now(timezone.utc).isoformat(),
            status='saved_C0_supplement_only_full_v5_and_confirmation_pending',
            sources=SOURCES,C0_natural_status=status,new_model_calls=0,new_grader_calls=0,new_auxiliary_score_calls=0,
            C5_reaudited=False,C5_bootstrap_repeated=False,original_snapshot=str(HERE)))
        print(json.dumps(status));return
    old_native=read(OLD/'native_scored.jsonl', True); old_unique=read(OLD/'per_input_status.jsonl', True)
    old_reports=read(OLD/'summary.json')['reports']; old_cost=read(OLD/'cost.json')['costs']
    c5_native=read(RUN/'c5/analysis/native_scored.jsonl',True)
    c5_unique=read(RUN/'c5/analysis/per_input_status.jsonl',True)
    c5_reports=read(RUN/'c5/analysis/quality_summary.json')['reports']
    c5_cost=read(RUN/'c5/analysis/cost_summary.json')['costs']
    c5_receipt=read(RUN/'c5/analysis/receipt.json')
    assert len(c5_native)==418 and len(c5_unique)==346
    assert Counter(r['score_origin'] for r in c5_native)=={
        'existing_identical_full_native_response':405,
        'new_response_native_score_cached_by_full_response_and_evaluation':13}
    assert len(read(RUN/'c5/analysis/score_cache.jsonl',True))==c5_receipt['new_native_score_calls']==13
    stat_receipt=read(RUN/'statistics/receipt.json')
    evaluations={panel:read(bind['evaluations'],True) for panel,bind in stat_receipt['source_bindings'].items()}
    pairs={panel:read(bind['pairs'],True) for panel,bind in stat_receipt['source_bindings'].items()}
    family={(r['panel'],r['method'],r['request_id']):r['family_id'] for r in old_unique}
    c0_hist=read(DEV/'offline/baseline_native_scores.jsonl',True)
    mislabeled=read(V4/'natural_scope/offline/baseline_native_scores_reused.jsonl',True)
    original_source={r['score_source'] for r in mislabeled}; assert len(original_source)==1
    assert {r['original_arm'] for r in mislabeled}=={'combined_head'}
    actual_original=read(next(iter(original_source)),True)
    natural_evals={r['record_id']:r for r in evaluations['natural52']}
    c0_nat=[dict(r,request_id=natural_evals[r['record_id']]['request_id']) for r in actual_original
            if r['arm']=='original' and r['record_id'] in natural_evals]
    assert len(c0_hist)==314 and len(c0_nat)==96
    c0_nat,c0_status,c0_cost,c0_issue=load_supplement(c0_nat,evaluations['natural52'],read)
    write('c0_missing_originals.jsonl',c0_issue)

    # Independently check C5 whole-response selection, score normalization and usage.
    runtime=[];count_outputs=count_calls=count_selected=count_nli=0
    old_u={(r['panel'],r['method'],r['arm'],r['request_id']):r for r in old_unique}
    old_s={(r['panel'],r['method'],r['arm'],r['record_id']):r for r in old_native}
    model_cost={}
    for model in ('M4','M5'):
        folder=RUN/'c5/runs'/model.lower();state=read(folder/'status.json')
        assert state['status']=='complete'
        outputs=read(folder/'proposals.jsonl',True);calls=read(folder/'model_calls.jsonl',True)
        assert len({r['request_id'] for r in outputs})==len(outputs)
        call_by=defaultdict(list)
        for call in calls:
            assert call['request']['kind']=='score'
            assert call['request']['temperature']==0 and call['request']['max_tokens']==1
            assert len(call['physical'])==1
            physical=call['physical'][0];assert physical['status']=='complete'
            assert physical['submission_state']=='accepted' and physical['engine_accepted']
            call_by[call['request_id'].split(':')[0]].append(call)
        for output in outputs:
            result=output['result']; verify=result['verification'];trace=verify['trace']
            assert result['native_answer']==verify['native_answer']
            assert result['f_proposal']['trace']==result['trace']
            assert result['f_disagreement_reanswer'] is False and result['global_generation_aggregator'] is False
            if trace['route']=='same_pool_joint_selection':
                assert len(trace['records'])==2 and trace['logical_score_calls']==2
                assert len(call_by[output['request_id']])==2
                candidates=trace['candidate_keys'];avg=defaultdict(list)
                for record,call in zip(trace['records'],call_by[output['request_id']]):
                    assert call['result']['value']==record['logps']
                    peak=max(record['logps'].values())
                    weights={k:math.exp(v-peak) for k,v in record['logps'].items()};z=sum(weights.values())
                    for code,w in weights.items():
                        key=record['code_to_key'][code];prob=w/z
                        assert abs(prob-record['native_probabilities'][key])<1e-14
                        avg[key].append(prob)
                assert set(avg)==set(candidates)
                final={k:sum(v)/2 for k,v in avg.items()};assert final==trace['scores']
                best=max(final.values());ties=[k for k in candidates if final[k]==best]
                base=result['base_native_answer']['answer_choice'];expected=base if base in ties else ties[0]
                assert trace['selected_key']==expected==result['native_answer']['answer_choice']
                idx=trace['selected_original_response_index']
                assert json.loads(result['trace']['responses'][idx])==result['native_answer']
                assert json.loads(trace['selected_raw_response'])==result['native_answer']
                count_selected+=1
            else:
                assert trace['route']=='retained_adopted_NLI'
                assert not call_by[output['request_id']] and result['native_answer']==result['base_native_answer']
                count_nli+=1
        for panel in evaluations:
            member_ids={r['request_id'] for r in evaluations[panel]}
            pcalls=[c for c in calls if c['request_id'].split(':')[0] in member_ids]
            physical=[p for c in pcalls for p in c['physical']]
            values=dict(physical_model_requests=len(physical),new_model_requests=len(physical),
                live_input_tokens=sum(p['event']['input_tokens'] for p in physical),
                live_output_tokens=sum(p['event']['output_tokens'] for p in physical),
                live_model_seconds=sum(p['event']['elapsed_seconds'] for p in physical),
                logical_score_callbacks=sum(o['result']['verification']['trace']['logical_score_calls']
                                            for o in outputs if o['request_id'] in member_ids))
            cost=next(c for c in c5_cost if c['panel']==panel and c['method']==model)
            for key,value in values.items(): assert abs(cost['new_physical_execution'][key]-value)<1e-8,(panel,model,key)
            for suffix in ('model_requests','input_tokens','output_tokens'):
                assert cost['attributed_'+suffix]==cost['inherited_B']['reused_head_'+suffix]+values[
                    'new_model_requests' if suffix=='model_requests' else 'live_'+suffix]
            runtime.append(dict(panel=panel,model=model,**values))
        count_outputs+=len(outputs);count_calls+=len(calls)
    assert (count_outputs,count_calls,count_selected,count_nli)==(95,176,88,7)
    for row in c5_native:
        if row['score_origin']!='existing_identical_full_native_response':continue
        u=next(r for r in c5_unique if (r['panel'],r['method'],r['request_id'])==(row['panel'],row['method'],row['request_id']))
        matches=[old_s[row['panel'],row['method'],arm,row['record_id']] for arm in set(r['arm'] for r in old_unique)
                 if old_u[row['panel'],row['method'],arm,row['request_id']]['native_answer_ref']==u['native_answer_ref']]
        assert matches
        for saved in matches:
            for k in ('correct','invalid','prediction','semantic_prediction','semantic_gold','document_detection'):
                assert row.get(k)==saved.get(k),(row['request_id'],k)

    native_all=[]
    for panel,c0 in [('historical121',c0_hist),('natural52',c0_nat)]:
        native_all.extend(dict(r,panel=panel,arm='original') for r in c0)
    native_all += [r for r in old_native if r['arm'] in ARMS.values()]
    native_all += c5_native
    reports={(r['panel'],r['method'],r['arm']):r for r in old_reports+c5_reports}
    table1=[];table2=[];table3=[];strata=[];lookup_units={}
    for panel in ('historical121','natural52'):
        e= evaluations[panel];eidx={r['record_id']:r for r in e};ids={r['request_id'] for r in e}
        for model in ('M4','M5'):
            baseline={r['request_id']:r for r in old_unique if (r['panel'],r['method'],r['arm'])==(panel,model,'F')}
            for control,arm in ARMS.items():
                n=[r for r in native_all if (r['panel'],r['method'],r['arm'])==(panel,model,arm)]
                by={r['record_id']:r for r in n};assert len(by)==len(n)
                complete=set(by)==set(eidx)
                us=units(n,e);lookup_units[panel,model,arm]={r['unit_id']:r for r in us if r['category']=='ALL'}
                input_group=defaultdict(list)
                for r in n: input_group[r['request_id']].append(r)
                valid_inputs={rid: None if any(r['correct'] is None for r in rs) else all(r['correct'] for r in rs)
                              for rid,rs in input_group.items()}
                correct=sum(v is True for v in valid_inputs.values())
                unavailable=sum(v is None for v in valid_inputs.values())
                all_units=[r for r in us if r['category']=='ALL']
                native_mean=None if not complete else sum(r['score'] for r in all_units)/len(all_units)
                repairs=sum(v is True and baseline[rid]['correct'] is False for rid,v in valid_inputs.items())
                harms=sum(v is False and baseline[rid]['correct'] is True for rid,v in valid_inputs.items())
                report=reports.get((panel,model,arm))
                if report:
                    assert correct==report['counts']['correct'] and unavailable==report['counts']['unavailable']
                    assert (repairs,harms)==(report['repairs'],report['harms'])
                    saved=next(r for r in report['native_unit_metrics']['categories'] if r['category']=='ALL')
                    assert abs(native_mean-saved['mean_native_unit_score'])<1e-12
                    saved_units={(r['unit_id'],r['source'],r['category']):r for r in report['native_unit_metrics']['units']}
                    for unit in us:
                        assert abs(unit['score']-saved_units[unit['unit_id'],unit['source'],unit['category']]['score'])<1e-12
                table1.append(dict(panel=panel,model=model,control=control,arm=arm,status='complete' if complete else 'partial_original_response_absent',
                    unique_input_denominator=len(ids),observed_inputs=len(valid_inputs),correct_inputs_observed=correct,
                    unavailable_inputs=unavailable,not_available_original_inputs=len(ids)-len(valid_inputs),
                    native_mapping_denominator=len(e),observed_native_mappings=len(n),native_ALL_units=len(all_units),
                    native_ALL_mean=native_mean,repair_inputs_vs_B=repairs,harm_inputs_vs_B=harms))
                for source in ['ALL',*sorted({r['resource_id'] for r in e})]:
                    for category in ['ALL','R1','R2','R3','R4','R5']:
                        group=[r for r in us if r['category']==category and (source=='ALL' or r['source']==source)]
                        if not group:continue
                        have=all(r['score'] is not None for r in group)
                        strata.append(dict(panel=panel,model=model,control=control,source=source,category=category,
                            units=len(group),scored_units=sum(r['score'] is not None for r in group),
                            mean_native_unit_score=sum(r['score'] for r in group)/len(group) if have else None,
                            status='complete' if have else 'partial',overlapping_R_categories_not_summed=True))
                if control!='C0':
                    pool=report['candidate_pool'];table2.append(dict(panel=panel,model=model,control=control,
                        pool_identity='old_F_plus_three_cached_reanswers' if control=='C4' else 'same_fixed_F_pool',
                        non_NLI_disagreement_inputs=pool['non_NLI_inputs'],pool_contains_correct_key=pool['covered'],
                        selected_correct_given_pool=pool['covered_selected_correct'],
                        conditional_selection_rate=pool['covered_selected_correct']/pool['covered'],
                        repairs=repairs,harms=harms,correct_input_delta=correct-sum(r['correct'] is True for r in baseline.values())))
                pair_data=[]
                for pair in pairs[panel]:
                    a=by.get(pair['left_record_id']);b=by.get(pair['right_record_id'])
                    pair_data.append(dict(pair_id=pair['pair_id'],family_id=pair['family_id'],relation=pair['relation'],
                        both_correct=None if a is None or b is None else int(a['correct'] is True and b['correct'] is True)))
                aux=[r['document_detection'] for r in n if 'document_detection' in r]
                for relation in ('maintain','respond'):
                    ps=[r for r in pair_data if r['relation']==relation];known=[r for r in ps if r['both_correct'] is not None]
                    total=sum(r['both_correct'] for r in known)
                    if report:assert total==next(r for r in report['pairs']['summaries'] if r['relation']==relation)['both_correct']
                    table3.append(dict(panel=panel,model=model,control=control,metric=relation+'_both_correct',
                        denominator=len(ps),observed_pairs=len(known),correct_observed=total,
                        value=total/len(ps) if len(known)==len(ps) else None))
                table3.append(dict(panel=panel,model=model,control=control,metric='native_auxiliary_fields',
                    denominator=len(aux) if aux else None,valid=sum(r['valid'] is True for r in aux) if aux else None,
                    exact=sum(r['exact'] is True for r in aux) if aux else None,
                    tp=sum(r['tp'] or 0 for r in aux) if aux else None,fp=sum(r['fp'] or 0 for r in aux) if aux else None,
                    fn=sum(r['fn'] or 0 for r in aux) if aux else None,
                    status='saved_scores' if aux else 'no_existing_auxiliary_score_not_recomputed',correction_semantic_score=None))

    # Add C5 paired atoms independently, preserving the earlier task2 files.
    template=read(RUN/'statistics/paired_atoms.jsonl',True);atoms=[]
    c5_rep={(r['panel'],r['method']):r for r in c5_reports}
    for atom in template:
        if atom['candidate']!='candidate_only':continue
        out=dict(atom,candidate='joint_selector');panel=out['panel'];model=out['model']
        if atom['metric']=='native_ALL':
            unit=lookup_units[panel,model,'joint_selector'][atom['atom_id']]
            out['candidate_score']=unit['score'];out['candidate_unavailable_native_records']=unit['unavailable']
        else:
            pair=next(r for r in c5_rep[panel,model]['pairs']['records'] if r['pair_id']==out['atom_id'])
            out['candidate_score']=int(pair['both_correct']);out['candidate_unavailable_endpoints']=pair['unavailable_endpoints']
        atoms.append(out)
    assert len(atoms)==398;write('c5_paired_atoms.jsonl',atoms)
    stats=RUN/'source_request/extracted/CF_MoA_Completion_Plan/paired_cluster_effects.py'
    proc=subprocess.run([sys.executable,str(stats),'--input',str(OUT/'c5_paired_atoms.jsonl'),
        '--output',str(OUT/'c5_paired_effects.json'),'--resamples','5000','--seed','240924'],capture_output=True,text=True,check=True)
    (OUT/'c5_bootstrap.stdout').write_text(proc.stdout)

    costs=[]
    for row in table1:
        panel,model,control=row['panel'],row['model'],row['control']
        if control=='C0':
            if panel=='natural52':
                costs.append(cost_row(model,c0_cost.get(model)));continue
            costs.append(dict(panel=panel,model=model,control=control,attributed_input_tokens=None,
                attributed_output_tokens=None,attributed_model_requests=None,
                cost_status='common_original_historical_initial_cost_not_reconstructed; not zero',inference_scope='historical_initial_answer'))
            continue
        source=next(c for c in (c5_cost if control=='C5' else old_cost)
                    if c['panel']==panel and c['method']==model and c['arm']==ARMS[control])
        extra=source.get('new_physical_execution',source.get('extra_execution'))
        costs.append(dict(panel=panel,model=model,control=control,inherited_B=source['inherited_B'],
            incremental_execution=extra,attributed_input_tokens=source['attributed_input_tokens'],
            attributed_output_tokens=source['attributed_output_tokens'],attributed_model_requests=source['attributed_model_requests'],
            physical_execution_origin='new_C5_score_batch' if control=='C5' else
                'previous_780_score_batch' if control in ('C2','C3') else
                'previous_three_reanswers_paid_not_free' if control=='C4' else 'cached_B',
            inference_scope='shared_saved_F_pool_not_independent_F_replication',
            common_historical_initial_answer_cost_excluded=True))
    r4=read(ROOT/'Documents/Codex/2026-09-17/r4_structural_head/physiology_head/v2/heldout/summary.json')
    r4table=[dict(model=r['method'],arm=r['arm'],profiles=24,inputs=r['n'],binary_correct=r['correct'],
        joint_numeric_correct=r['joint_numeric_correct'],all_outputs_correct=r['all_outputs_correct'],
        scope='old_frozen_supplied_model_profiles_not_new_clinical_patients_or_current_main_panel',
        new_model_calls_this_table=0) for r in r4['results'] if r['arm'] in ('redo','full','patch','patch_no_do')]
    scope=read(RUN/'scope/cache_coverage_summary.json')
    ablations=read(RUN/'operation_ablations/summary.json')
    ablation_receipt=read(RUN/'operation_ablations/receipt.json')
    ablation_rows=read(RUN/'operation_ablations/native_scored.jsonl',True)
    assert len(ablation_rows)==738 and len(ablations)==6
    table4=[]
    for r in ablations:
        category=next(c for c in r['native_units']['categories'] if c['category']=='ALL')
        assert r['inputs']==category['units']==123
        assert abs(r['correct']/123-category['mean_native_unit_score'])<1e-12
        table4.append({k:v for k,v in r.items() if k!='native_units'} | dict(
            native_ALL_mean=category['mean_native_unit_score'],
            scope='complete_123_rule_capability_subset_not_full_v5_system',
            operation_engine='shared_adopted_rule_kernel',
            score_execution_origin='existing_operation_ablations_receipt_53_new_grades_not_new_this_table'))
    outputs={'table1_native_effects.json':table1,'table1_source_R_strata.json':strata,
             'table2_selection_mechanisms.json':table2,'table3_pairs_auxiliary.json':table3,
             'table3_A4_separate_model_scope.json':r4table,'table4_operation_ablations.json':table4,
             'table5_quality_cost.json':costs}
    for name,value in outputs.items():dump(name,value)
    dump('c5_independent_verification.json',dict(status='passed_with_logical_cost_metadata_bug_corrected',
        outputs=count_outputs,verified_selections=count_selected,NLI_passthrough=count_nli,
        score_calls=count_calls,native_mapping_rows=418,full_input_rows=346,existing_score_reuses=405,
        original_new_score_calls=13,new_model_calls_this_audit=0,new_grader_calls_this_audit=0,
        observed_physical_usage=runtime,all_native_and_pair_points_match_saved_summary=True,
        whole_response_and_normalization_checks=True,c0_natural_initially_missing_original_rows=8,
        c0_natural_still_missing_original_rows=sum(r['missing_inputs'] for r in c0_status.values()),
        cost_fix='c5_cost_metadata_fix/receipt.json'))
    dump('receipt.json',dict(at=datetime.now(timezone.utc).isoformat(),status='completed_121_52_tables_full_v5_and_confirmation_pending',
        sources=SOURCES,new_model_calls=0,new_grader_calls=0,table_groups=len(table1),native_strata=len(strata),
        C0_natural_status=c0_status,
        limitations=['Exposed development; old F pools fixed.','Full v5 and post-freeze independent family results pending.',
                     'Common initial answer cost excluded, not claimed zero.','A4 old model-profile evidence separate from clinical panels.']))
    print(json.dumps(dict(table_groups=len(table1),native_strata=len(strata),c5_calls=count_calls,new_grader_calls=0)))


if __name__=='__main__': main()
