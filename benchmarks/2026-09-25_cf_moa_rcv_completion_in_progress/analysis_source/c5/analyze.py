"""Score only genuinely new complete C5 responses; reuse all existing scores."""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import csv
import importlib.util
import json

from cf_moa.contracts import digest
from cf_moa.evaluation.score_run import unit_summaries
from cf_moa.evaluation.paired_metrics import paired_metrics
from cf_moa.tools.adopted import sha256

HERE=Path(__file__).resolve().parent
WORK=Path('/home/data3/txy')
OLD=HERE.parents[1]/'cf_moa_candidate_verify_20260924'
REC=OLD/'recovery_gpu23'
V4=WORK/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
DEV=WORK/'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
spec=importlib.util.spec_from_file_location('completed_candidate_metrics',OLD/'analysis/score_candidate_experiment.py')
metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)


def rows(path):
    with Path(path).open() as stream:return [json.loads(line) for line in stream]


def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def write(path,values):path.write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in values))


def main():
    out=HERE/'analysis';out.mkdir(exist_ok=True)
    scoring=metrics.Scoring(out)
    scoring.cache.update({r['cache_key']:r for r in rows(REC/'analysis/score_cache.jsonl')})
    previous=rows(REC/'analysis/complete_results/native_scored.jsonl')
    previous_unique=rows(REC/'analysis/complete_results/per_input_status.jsonl')
    score_by={(r['panel'],r['method'],r['arm'],r['record_id']):r for r in previous}
    unique_by=defaultdict(list)
    for r in previous_unique:unique_by[r['panel'],r['method'],r['request_id']].append(r)
    trigger_meta={}
    with (metrics.BUNDLE/'analysis/per_trigger_seed.csv').open() as f:
        for r in csv.DictReader(f):trigger_meta[r['panel'],r['method'],r['request_id']]=r
    costs=json.loads((REC/'analysis/complete_results/cost.json').read_text())['costs']
    all_native=[];all_unique=[];reports=[];cost_rows=[];returned=0;source_files={}
    for method in ['M4','M5']:
        run=HERE/'runs'/method.lower()
        state=json.loads((run/'status.json').read_text())
        if state['status']!='complete':raise ValueError('C5 run incomplete; do not present final quality')
        observed={r['request_id']:r for r in rows(run/'proposals.jsonl')}
        calls=rows(run/'model_calls.jsonl')
        for panel,offline in [('historical121',DEV/'offline'),('natural52',V4/'natural_scope/offline')]:
            items={r['request_id']:r for r in rows(offline/'items.jsonl')}
            evaluations=rows(offline/'evaluations.jsonl')
            pairs=[dict(p,left=p['left_record_id'],right=p['right_record_id']) for p in rows(offline/'pairs.jsonl')]
            byid=defaultdict(list)
            for e in evaluations:byid[e['request_id']].append(e)
            native=[];unique=[]
            for rid,item in items.items():
                old_rows=unique_by[panel,method,rid]
                base=next(r for r in old_rows if r['arm']=='F')
                result=observed.get(rid)
                if result is None:
                    ref=base['native_answer_ref'];status='unchanged_outside_C5_old_trigger_scope';value=None
                    reuse_arm='F'
                else:
                    value=result.get('result',{}).get('native_answer')
                    ref=digest(value) if value is not None else None
                    status=result['status']
                    reuse_arm=next((r['arm'] for r in old_rows if r['native_answer_ref']==ref),None)
                    returned+=1
                scored=[]
                for e in byid[rid]:
                    if reuse_arm is not None:
                        score=deepcopy(score_by[panel,method,reuse_arm,e['record_id']])
                        score['score_origin']='existing_identical_full_native_response'
                    else:score=scoring.score(item,e,value)
                    row=dict(score,panel=panel,method=method,arm='joint_selector',request_id=rid,
                             record_id=e['record_id'],run_status=status)
                    scored.append(row);native.append(row)
                correct=None if any(r['correct'] is None for r in scored) else all(r['correct'] for r in scored)
                aux=[r['document_detection'] for r in scored if 'document_detection' in r]
                unique.append(dict(base,arm='joint_selector',correct=correct,native_answer_ref=ref,
                    native_valid=ref is not None,run_status=status,
                    auxiliary_exact=None if not aux or any(a['exact'] is None for a in aux) else all(a['exact'] for a in aux)))
            baseline={r['request_id']:r for r in previous_unique if r['panel']==panel and r['method']==method and r['arm']=='F'}
            selection=[]
            for row in unique:
                t=trigger_meta.get((panel,method,row['request_id']))
                if t and t['F_path']==metrics.old.old_score.__dict__.get('VOTE_ROUTE','full_native_key_maj5_absolute_majority_stop'):
                    selection.append((t['old_pool_has_joint_correct_key'] in ['True','true','1'],row['correct'] is True))
            units=unit_summaries(native,evaluations)
            report=dict(panel=panel,method=method,arm='joint_selector',
                **metrics.old.comparison(unique,baseline),native_unit_metrics=units,
                auxiliary_mapping_metrics=metrics.auxiliary_summary(native),
                pairs=paired_metrics({r['record_id']:r for r in native},pairs),
                candidate_pool=dict(non_NLI_inputs=len(selection),covered=sum(a for a,b in selection),
                    covered_selected_correct=sum(a and b for a,b in selection)),
                result_status='complete',inference_context='saved_F_pool_only_new_C5_scores_not_fresh_end_to_end')
            reports.append(report);all_native.extend(native);all_unique.extend(unique)
            inherited=next(c['inherited_B'] for c in costs if c['panel']==panel and c['method']==method and c['arm']=='F')
            selected_calls=[c for c in calls if c['request_id'].split(':')[0] in items]
            extra=metrics.summed_cost(selected_calls)
            extra['logical_score_callbacks']=sum(
                row.get('result',{}).get('verification',{}).get('trace',{}).get('logical_score_calls',0)
                for rid,row in observed.items() if rid in items)
            cost_rows.append(dict(panel=panel,method=method,arm='joint_selector',inherited_B=inherited,
                new_physical_execution=extra,attributed_model_requests=inherited['reused_head_model_requests']+extra['new_model_requests'],
                attributed_input_tokens=inherited['reused_head_input_tokens']+extra['live_input_tokens'],
                attributed_output_tokens=inherited['reused_head_output_tokens']+extra['live_output_tokens']))
        source_files[str(run/'status.json')]=sha256(run/'status.json')
    assert returned==95
    write(out/'native_scored.jsonl',all_native);write(out/'per_input_status.jsonl',all_unique)
    dump(out/'quality_summary.json',dict(reports=reports,full_denominators=True,independent=False))
    dump(out/'cost_summary.json',dict(costs=cost_rows,do_not_sum_inherited_B_as_new_calls=True))
    dump(out/'receipt.json',dict(new_model_calls_during_analysis=0,new_native_score_calls=scoring.calls,
        reused_existing_native_mapping_rows=len(all_native)-scoring.calls,
        source_status_hashes=source_files,returned_C5_outputs=returned,full_input_rows=len(all_unique)))
    print(json.dumps([dict(panel=r['panel'],method=r['method'],correct=r['counts']['correct'],
        repairs=r['repairs'],harms=r['harms'],native=next(u for u in r['native_unit_metrics']['categories'] if u['category']=='ALL')) for r in reports]))


if __name__=='__main__':main()
