"""One offline decomposition of existing choices; no model/head/scorer execution.

Only the frozen native parser and norm functions are imported. Saved native
scores remain authoritative and are checked against exact parsed native keys.
"""
import collections
import csv
import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path('/home/data3/txy')
sys.path.insert(0, str(ROOT))
from cf_moa.evaluation.native_scoring import load_native_scorer, source_lock

RUN = ROOT/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
OLD = ROOT/'Documents/Codex/2026-09-21/cf_moa/effect_first_revision_20260923'
DEV = ROOT/'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
OUT = Path(__file__).parent
sources = {}
parser, canonical = load_native_scorer()

def read(path, lines=False, expected=None):
    path = Path(path); raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
    if expected: assert digest == expected, str(path)
    sources[str(path)] = digest
    return [json.loads(l) for l in raw.splitlines() if l.strip()] if lines else json.loads(raw)

def dump(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def table(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w') as f:
        writer = csv.DictWriter(f, fields); writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})

def native_key(value, item):
    item = dict(item)
    if item['answer_format'] == 'robustness_single': item['answer_format'] = 'single'
    pred, error, _ = parser.parse(json.dumps({'answer':value}), item, canonical)
    return pred if error is None else None

def gold_key(value, item):
    return parser.norm(value) if item['answer_format'] == 'relation' else value

def category(trace):
    if trace.get('route') == 'full_nli_equal_paths_native_completion':
        d = trace['decision']; a,b=d['direct'],d['reasoned']
        parts=[]
        if len(set(a['per_order'])) > 1 or len(set(b['per_order'])) > 1: parts.append('mapping_top1_disagreement')
        if a['answer_choice'] != b['answer_choice']: parts.append('direct_reasoned_mean_disagreement')
        return '+'.join(parts) or 'subpath_top1_disagreement'
    return 'tied_vote_leaders' if trace.get('tied_choices') else 'majority_with_minority_votes'

def candidates(trace):
    if trace.get('route') == 'full_nli_equal_paths_native_completion':
        d=trace['decision']
        return list(d['direct']['per_order'])+list(d['reasoned']['per_order'])
    return trace.get('predictions', [])

def summary(rows):
    n=len(rows)
    sums = ['baseline_correct','old_pool_has_joint_correct_key','old_F_correct','old_pool_has_correct_but_F_wrong',
            'old_pool_lacks_correct_key','new_correct','repair','harm','retained_correct','retained_wrong',
            'new_correct_first_in_pool','harm_to_old_pool_wrong_key','harm_to_new_wrong_key',
            'union_old_plus_this_seed_has_correct','new_key_in_old_pool','new_model_requests','input_tokens','output_tokens',
            'auxiliary_values_identical','baseline_document_detection_if_scored_exact','new_document_detection_exact','baseline_document_detection_recorded',
            'has_document_detection','native_mapping_count']
    result={'trigger_combinations':n}
    for key in sums: result[key]=sum(int(row[key]) for row in rows)
    result['net_correct_count']=result['repair']-result['harm']
    result['old_pool_key_coverage']=result['old_pool_has_joint_correct_key']/n if n else None
    result['F_accuracy_on_trigger']=result['baseline_correct']/n if n else None
    result['reanswer_accuracy_on_trigger']=result['new_correct']/n if n else None
    result['repair_rate_given_old_wrong']=result['repair']/(n-result['baseline_correct']) if n!=result['baseline_correct'] else None
    result['harm_rate_given_old_correct']=result['harm']/result['baseline_correct'] if result['baseline_correct'] else None
    return result

rows=[]; pools=[]; full=[]; propensity=[]; aux=[]; nli_rows=[]
for panel in ('historical121','natural52'):
    natural=panel=='natural52'
    plan=read(RUN/'natural_scope/plan_seed_42.json' if natural else RUN/'seeds/seed_43/plan.json')
    offline=(RUN/'natural_scope' if natural else DEV)/'offline'
    evaluations=read(offline/'evaluations.jsonl',True)
    eval_by=collections.defaultdict(list)
    for e in evaluations:eval_by[e['request_id']].append(e)
    statuses=read(RUN/'analysis'/panel/'per_input_status.jsonl',True)
    status_index={(r['method'],r['seed'],r['request_id']):r for r in statuses}
    scored=read(RUN/'analysis'/panel/'native_scored.jsonl',True)
    score_index={(r['method'],r['seed'],r['record_id']):r for r in scored}
    panel_summary=read(RUN/'analysis'/panel/'summary.json')
    for method in ('M4','M5'):
        spec=plan['methods'][method]
        inputs={r['request_id']:r for r in read(spec['inputs'],True,spec['inputs_sha256'])}
        bases={r['request_id']:r for r in read(spec['bases'],True,spec['bases_sha256'])}
        props={r['proposal_key'].split(':')[0]:r['proposal'] for r in read(spec['proposals'],True,spec['proposals_sha256'])}
        outputs={}
        for seed in (42,43,44):
            path=RUN/'natural_runs'/f'seed_{seed}'/method.lower()/'proposals.jsonl' if natural else (
                OLD/'a5_quality121'/method.lower()/'proposals.jsonl' if seed==42 else RUN/'seeds'/f'seed_{seed}'/method.lower()/'proposals.jsonl')
            outputs[seed]={r['request_id']:r for r in read(path,True) if r['arm']=='a5_reanswer'}
            ss=panel_summary['methods'][method]['seeds'][str(seed)]
            full.append({'panel':panel,'method':method,'seed':seed,'full_inputs':len(inputs),
                         'B_correct':panel_summary['methods'][method]['baseline']['counts']['correct'],
                         'new_correct':ss['counts']['correct'],'repairs':ss['repairs'],'harms':ss['harms'],
                         'native_unit_delta':ss['native_unit_mean_difference'], 'scoring_source':'existing_v4_native_scores_not_rescored'})
        for rid,packet in inputs.items():
            proposal=props[rid];trace=proposal['trace'];observed=candidates(trace)
            pool=[native_key(v,packet['native_input']) for v in observed]
            distinct=list(dict.fromkeys(v for v in pool if v is not None))
            trigger=len(distinct)>=2
            supported=proposal['applicability']!='unsupported'
            base_status=status_index[method,None,rid]
            propensity.append(dict(panel=panel,method=method,request_id=rid,F_supported=supported,trigger=trigger,
                                   baseline_correct=base_status['correct'],baseline_valid=base_status['native_valid']))
            if not trigger:continue
            item=packet['native_input'];ev=eval_by[rid]
            golds=[gold_key(e['gold'],item) for e in ev]
            joint=lambda k: k is not None and all(k==g for g in golds)
            covered=any(joint(k) for k in distinct)
            base=bases[rid]['native_answer'];f_native=proposal['native_proposal']
            assert base==f_native,(panel,method,rid,'baseline F differs')
            basekey=native_key(base['answer_choice'],item)
            for e,g in zip(ev,golds):
                saved=score_index[method,None,e['record_id']]
                assert saved['correct']==(basekey==g),(panel,method,rid,'stored baseline score differs')
            assert base_status['correct']==joint(basekey)
            if trace['route']=='full_native_key_maj5_absolute_majority_stop':
                assert len(observed)==len(trace['responses'])
                decoded=[]
                for raw in trace['responses']:
                    try: obj=json.loads(raw)
                    except (ValueError,TypeError): obj=None
                    value=obj.get('answer_choice') if isinstance(obj,dict) else None
                    decoded.append(value if value in item.get('options',{}) or (item['answer_format']=='relation' and value in ('higher','lower','no difference','uncertainty')) else None)
                assert decoded==observed
                assert trace['responses'][trace['selected_index']]==trace['raw_response']
            else:
                d=trace['decision']; mappings=[list(item['options']),list(item['options'])[::-1]]
                path_means=[d['direct']['answer_choice'],d['reasoned']['answer_choice']]
                assert d['answer_choice']==basekey==max(list(item['options']),key=d['mean_probabilities'].get)
                nli_rows.append(dict(panel=panel,method=method,request_id=rid,gold=golds,
                    mapping_order=mappings,per_mapping_top1=observed,path_mean_winners=path_means,
                    mean_probabilities=d['mean_probabilities'],code_logprobs=d['code_logprobs'],
                    old_pool_has_correct=covered,F_correct=joint(basekey),
                    any_nonzero_mass_keys=[k for k,v in d['mean_probabilities'].items() if v>0],
                    note='Binary triggered top1 disagreement necessarily includes both keys. Nonzero mass is not a generated candidate.'))
            seedkeys=[]
            for seed in (42,43,44):
                output=outputs[seed][rid];res=output['result'];assert res['trace']['route']=='ordinary_reanswer'
                assert set(res['trace']['competing_keys'])==set(distinct)
                native=res['native_answer'];key=native_key(native['answer_choice'],item)
                seedkeys.append(key)
                sc=[score_index[method,seed,e['record_id']] for e in ev]
                for e,g,s in zip(ev,golds,sc):assert s['correct']==(key==g),(panel,method,rid,seed,'stored reanswer score differs')
                assert status_index[method,seed,rid]['correct']==joint(key)
                bsc=[score_index[method,None,e['record_id']] for e in ev]
                auxfields=[k for k in base if k not in ('answer_choice','step_by_step_thinking')]
                auxsame={k:base[k] for k in auxfields}=={k:native[k] for k in auxfields}
                assert auxsame
                detection=[s.get('document_detection') for s in sc]
                bdet=[s.get('document_detection') for s in bsc]
                assert all(old is None or old==new for old,new in zip(bdet,detection)),(panel,method,rid,seed,bdet,detection)
                derived_bdet=[old if old is not None else new for old,new in zip(bdet,detection)]
                bcorrect=joint(basekey);correct=joint(key);cost=res['cost']
                row=dict(panel=panel,method=method,seed=seed,request_id=rid,family_id=base_status['family_id'],
                    source=base_status['source'],answer_format=item['answer_format'],F_path=trace['route'],
                    output_disagreement_type=category(trace),clinical_evidence_conflict_type='unknown_not_assessed',
                    native_mapping_count=len(ev),gold_keys=golds,gold_mapping_conflict=len(set(golds))>1,
                    old_candidate_keys=distinct,old_candidate_observations=len(observed),old_invalid_observations=pool.count(None),
                    baseline_key=basekey,new_key=key,baseline_correct=bcorrect,old_F_correct=bcorrect,
                    old_pool_has_joint_correct_key=covered,old_pool_has_correct_but_F_wrong=covered and not bcorrect,
                    old_pool_lacks_correct_key=not covered,new_correct=correct,
                    repair=not bcorrect and correct,harm=bcorrect and not correct,retained_correct=bcorrect and correct,
                    retained_wrong=not bcorrect and not correct,new_correct_first_in_pool=correct and not covered,
                    harm_to_old_pool_wrong_key=bcorrect and not correct and key in distinct,
                    harm_to_new_wrong_key=bcorrect and not correct and key not in distinct,
                    union_old_plus_this_seed_has_correct=covered or correct,new_key_in_old_pool=key in distinct,
                    auxiliary_values_identical=auxsame,auxiliary_fields=auxfields,has_document_detection=any(d is not None for d in detection),
                    baseline_document_detection_if_scored_exact=all(d and d['exact'] for d in derived_bdet),
                    baseline_document_detection_recorded=all(d is not None for d in bdet),
                    new_document_detection_exact=all(d and d['exact'] for d in detection),
                    new_model_requests=cost['new_model_requests'],input_tokens=cost['live_input_tokens'],output_tokens=cost['live_output_tokens'])
                rows.append(row)
                if any(d is not None for d in detection):
                    aux.append(dict(panel=panel,method=method,seed=seed,request_id=rid,
                                    keys=dict(baseline=basekey,reanswer=key),auxiliary_values_identical=auxsame,
                                    record_ids=[e['record_id'] for e in ev],baseline_document_detection_recorded=bdet,reanswer_document_detection=detection,
                                    baseline_document_detection_by_identical_auxiliary_and_same_gold=derived_bdet,
                                    missing_B_metric_inferred_from_identical_auxiliary_not_rescored=any(d is None for d in bdet),
                                    answer_main_metric_and_document_auxiliary_are_separate=True))
            pools.append(dict(panel=panel,method=method,request_id=rid,F_path=trace['route'],old_pool=distinct,
                              reanswers_by_seed=dict(zip((42,43,44),seedkeys)),old_pool_has_correct=covered,
                              three_seed_new_pool_has_correct=any(joint(k) for k in seedkeys),
                              old_plus_three_seed_pool_has_correct=covered or any(joint(k) for k in seedkeys),
                              first_correct_from_three_seed_pool=not covered and any(joint(k) for k in seedkeys),
                              supplementary_calls_used=3,deployable_method=False,
                              note='Offline gold-selecting oracle over 3 supplementary calls, not one-call performance.'))
assert len(rows)==285 and len(pools)==95
assert sum(r['new_model_requests'] for r in rows)==285
expected={('historical121','M4'):28,('historical121','M5'):26,('natural52','M4'):25,('natural52','M5'):16}
for k,n in expected.items():assert sum((r['panel'],r['method'])==k for r in pools)==n
summary_rows=[]
for panel,method in expected:
    for seed in (42,43,44):
        subset=[r for r in rows if (r['panel'],r['method'],r['seed'])==(panel,method,seed)]
        row=dict(panel=panel,method=method,seed=seed,**summary(subset));summary_rows.append(row)
        reference=next(r for r in full if (r['panel'],r['method'],r['seed'])==(panel,method,seed))
        assert (row['repair'],row['harm'])==(reference['repairs'],reference['harms'])
strata=[]
for fields in [('answer_format',),('F_path',),('output_disagreement_type',),('answer_format','F_path')]:
    grouped=collections.defaultdict(list)
    for row in rows:grouped[tuple(row[k] for k in ('panel','method','seed')+fields)].append(row)
    for key,subset in grouped.items():
        strata.append(dict(zip(('panel','method','seed')+fields,key),stratification='+'.join(fields),**summary(subset)))
trigger_comparison=[]
for panel,method in expected:
    for scope in ('F_trigger','F_nontrigger','outside_F'):
        selected=[r for r in propensity if (r['panel'],r['method'])==(panel,method) and (
            (r['F_supported'] and r['trigger']) if scope=='F_trigger' else
            (r['F_supported'] and not r['trigger']) if scope=='F_nontrigger' else not r['F_supported'])]
        trigger_comparison.append(dict(panel=panel,method=method,scope=scope,inputs=len(selected),
            baseline_correct=sum(r['baseline_correct'] is True for r in selected),
            baseline_unavailable=sum(not r['baseline_valid'] for r in selected)))
for path,value in sources.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==value,path
for entry in source_lock():sources[entry['path']]=entry['sha256']
table('selection_decomposition.csv',[{k:r[k] for k in ('panel','method','seed','trigger_combinations','baseline_correct','old_pool_has_joint_correct_key','old_pool_has_correct_but_F_wrong','old_pool_lacks_correct_key','new_correct','repair','harm','net_correct_count','new_correct_first_in_pool','harm_to_old_pool_wrong_key','harm_to_new_wrong_key','new_model_requests')} for r in summary_rows])
table('per_trigger_seed.csv',rows)
table('stratified_decomposition.csv',strata)
table('full_panel_existing_results.csv',full)
table('trigger_baseline_comparison.csv',trigger_comparison)
for name,value in [('per_trigger_seed.jsonl',rows),('three_seed_oracle.jsonl',pools),('nli_candidate_details.jsonl',nli_rows),('auxiliary_field_comparison.jsonl',aux)]:
    (OUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in value))
dump('summary.json',dict(status='completed_saved_choices_only',combinations=95,seed_combinations=285,
    native_candidate_definition='NLI: four existing mapped top1s, not nonzero probability mass; other formats: only actual generated vote keys before early stop',
    seed_comparisons=summary_rows,three_seed_oracle={f'{p}/{m}':dict(combinations=len(rr),
        old_pool_has_correct=sum(r['old_pool_has_correct'] for r in rr),
        new_three_seed_pool_has_correct=sum(r['three_seed_new_pool_has_correct'] for r in rr),
        union_has_correct=sum(r['old_plus_three_seed_pool_has_correct'] for r in rr),
        first_correct_from_new_pool=sum(r['first_correct_from_three_seed_pool'] for r in rr),
        supplementary_calls_used=3*len(rr)) for (p,m) in expected for rr in [[r for r in pools if(r['panel'],r['method'])==(p,m)]]},
    trigger_baseline_comparison=trigger_comparison,full_panel_existing_results=full,
    nli_trigger_count=len(nli_rows),gold_mapping_conflicts=sum(r['gold_mapping_conflict'] for r in rows)//3,
    known_limitations=['Triggered-only selection; not an unbiased whole-panel oracle','Clinical evidence conflict unassessed and marked unknown','Native correct scores assess answer key; document detection is a separate auxiliary metric','Gold only offline; no deployed selection or new aggregation','Three seed pool spends three supplementary calls and is not an online method','Nontrigger reanswer counterfactuals do not exist: this cannot identify predictive calibration or causal effect of disagreement versus nontrigger','Natural52 baseline document_detection is absent; unchanged auxiliary plus same gold establishes same auxiliary judgment, explicitly marked inferred rather than stored score'],
    supplementary_cost_including_prior_seed42=dict(calls=sum(r['new_model_requests'] for r in rows),input_tokens=sum(r['input_tokens'] for r in rows),output_tokens=sum(r['output_tokens'] for r in rows)),
    current_analysis_new_model_calls=0,current_analysis_native_score_calls=0,current_analysis_head_replays=0))
dump('receipt.json',dict(created_at=datetime.datetime.now().astimezone().isoformat(),
    source_hashes=sources,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    source_bytes_unchanged=True,new_model_calls=0,new_native_scorer_calls=0,old_head_replays=0,
    reused_native_parser=True,all_existing_scores_verified_on_trigger_keys=True,
    all_seed_scores_reused=True,online_gold_access=False,
    outputs=['selection_decomposition.csv','per_trigger_seed.csv','stratified_decomposition.csv','full_panel_existing_results.csv','trigger_baseline_comparison.csv','per_trigger_seed.jsonl','three_seed_oracle.jsonl','nli_candidate_details.jsonl','auxiliary_field_comparison.jsonl','summary.json']))
print(json.dumps(summary_rows,ensure_ascii=False,indent=2))
