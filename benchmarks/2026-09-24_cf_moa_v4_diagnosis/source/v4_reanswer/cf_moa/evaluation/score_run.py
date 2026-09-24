"""Score saved independent outputs in a separate offline process."""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from statistics import mean

from cf_moa.evaluation.native_scoring import load_native_scorer,score_proposal,source_lock
from cf_moa.evaluation.paired_metrics import paired_metrics
from cf_moa.evaluation.prepare_development import rows,write,dump
from cf_moa.tools.adopted import sha256


def unit_summaries(scored,evaluations):
    buckets=defaultdict(list)
    lookup={e['record_id']:e for e in evaluations}
    for row in scored:
        e=lookup[row['record_id']]
        if e['role']=='reference':continue
        for category in ['ALL',*e['evaluation_labels']]:
            buckets[e['unit_id'],category,e['resource_id']].append(row)
    units=[dict(unit_id=u,category=c,source=s,native_records=len(rs),
        score=mean(int(r['correct'] is True) for r in rs),all_tasks_pass=all(r['correct'] is True for r in rs),
        native_scored=sum(r['correct'] is not None for r in rs),
        unavailable=sum(r['correct'] is None for r in rs),
        incorrect_answers=sum(r['correct'] is False for r in rs))
        for (u,c,s),rs in sorted(buckets.items())]
    categories=[]
    for category in ['ALL','R1','R2','R3','R4','R5']:
        group=[r for r in units if r['category']==category]
        categories.append(dict(category=category,units=len(group),
            mean_native_unit_score=mean(r['score'] for r in group) if group else None,
            unavailable_native_records=sum(r['unavailable'] for r in group),
            incorrect_native_answers=sum(r['incorrect_answers'] for r in group)))
    return dict(units=units,categories=categories,
        interpretation='Original non-reference equal-unit weighting; legacy score fields measure end-to-end native success over the complete denominator. Unavailable remains not_scored, not an incorrect answer; availability and wrong answers are separate. Overlapping R categories are not summed.')


def score_run(development,run,output):
    plan=json.loads((run/'plan.json').read_text())
    status_path=run/'status.json'
    if status_path.exists() and json.loads(status_path.read_text()).get('status')=='stopped_on_error':
        raise ValueError('Stopped runs cannot produce main results by dropping unsubmitted/failed inputs')
    output.mkdir(parents=True,exist_ok=False)
    method=plan['method'];expert=plan['expert']
    packet_file=development/'inference'/(method.lower()+'.jsonl')
    if sha256(packet_file)!=plan['input_file_sha256']:
        raise ValueError('The run used a different inference packet file')
    items={r['request_id']:r for r in rows(development/'offline/items.jsonl')}
    evaluations=list(rows(development/'offline/evaluations.jsonl'))
    proposals=list(rows(run/'proposals.jsonl'))
    by_id={r['request_id']:r for r in proposals}
    if len(by_id)!=len(proposals) or set(by_id)!=set(items):
        raise ValueError('Require every independent input exactly once, including failed/unsupported')
    for rid,row in by_id.items():
        if row['input_hash']!=plan['input_hashes'][rid]:raise ValueError('Run output input-hash mismatch')
    scorer=load_native_scorer();scored=[]
    for e in evaluations:
        row=by_id[e['request_id']]
        proposal=row.get('proposal')
        value=score_proposal(items[e['request_id']],e,proposal,scorer=scorer)
        scored.append(dict(request_id=e['request_id'],record_id=e['record_id'],expert=expert,method=method,
            run_status=row['status'],variant=proposal['variant'] if proposal else None,**value))
    unique=[]
    for rid,row in by_id.items():
        judgments=[r for r in scored if r['request_id']==rid]
        unique.append(dict(request_id=rid,expert=expert,method=method,
            variant=(row.get('proposal') or {}).get('variant'),applicability=judgments[0]['applicability'],
            correct=None if any(j['correct'] is None for j in judgments) else all(j['correct'] for j in judgments),
            method_score='not_scored' if any(j['correct'] is None for j in judgments) else 'scored',
            native_mapping_count=len(judgments),
            mixed_native_correctness=len({j['correct'] for j in judgments})>1,cost=row['cost']))
    lookup={r['record_id']:r for r in scored}
    pairs=[dict(p,left=p['left_record_id'],right=p['right_record_id'])
           for p in rows(development/'offline/pairs.jsonl')]
    write(output/'native_scored.jsonl',scored)
    write(output/'complementarity_inputs.jsonl',unique)
    dump(output/'paired_metrics.json',paired_metrics(lookup,pairs))
    dump(output/'native_unit_metrics.json',unit_summaries(scored,evaluations))
    dump(output/'receipt.json',dict(status='scored_historical_baseline_reuse' if plan.get('origin')=='historical_reuse'
        else 'scored_saved_independent_development_outputs',expert=expert,
        method=method,inputs=len(unique),native_mappings=len(scored),
        variants=dict(Counter(str(r['variant']) for r in unique)),
        applicability=dict(Counter(r['applicability'] for r in unique)),
        unavailable_inputs=sum(r['correct'] is None for r in unique),
        incorrect_answer_inputs=sum(r['correct'] is False for r in unique),
        proposal_file_sha256=sha256(run/'proposals.jsonl'),scorer_sources=source_lock(),
        evaluation_wrapper_sources=[dict(path=str(Path(__file__).with_name(name)),
            sha256=sha256(Path(__file__).with_name(name))) for name in
            ('score_run.py','native_scoring.py','paired_metrics.py')],
        mixed_mapping_inputs=sum(r['mixed_native_correctness'] for r in unique),
        unique_correctness_definition='all available native mappings must be correct; an unavailable answer is None/not_scored, remains in success/coverage/failure denominators, and is not labelled an incorrect answer; costs counted once per input',
        no_independent_evaluation_claim=True,new_model_requests=0))


def main():
    parser=argparse.ArgumentParser()
    for key in ('development','run','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();score_run(args.development,args.run,args.output)


if __name__=='__main__':main()
