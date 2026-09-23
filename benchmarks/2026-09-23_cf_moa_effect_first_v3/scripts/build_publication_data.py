#!/usr/bin/env python3
"""Export allowlisted saved metadata only. No inference or native scoring; gold values are never used."""
import argparse, csv, hashlib, json, re
from pathlib import Path
from collections import Counter, defaultdict

FIELDS = ['cycle','panel','method','arm','request_id','correct','native_valid','run_status','native_mapping_count','method_score','actual_adjudication','proposal_delivered','modified_answer','repair_attempted','failure_type','warnings','origin','source_file','source_line']
COUNT_KEYS = ('denominator','correct','incorrect','unavailable','not_submitted','submitted_unavailable')
NATIVE_KEYS = ('category','units','mean_native_unit_score','unavailable_native_records','incorrect_native_answers')
PAIR_KEYS = ('method','arm','coverage','relation','pairs','families','both_correct','both_native_scored','unavailable_endpoints','valid_relation','pair_weighted_both_correct_ci95','bootstrap_seed','available_fixed_pairs','outside_arm_scope','both_correct_rate','relation_compliance','applicable_to_A5_mechanism','acceptance_claim','unavailable_pairs','relation_satisfied')
COST_KEYS = set('physical_model_requests new_model_requests live_input_tokens live_output_tokens live_model_seconds unresolved_model_usage submission_attempts failed_attempts model_usage_complete reused_head_model_requests reused_head_input_tokens reused_head_output_tokens reused_head_model_seconds reused_historical_initial_answers physical_requests input_tokens output_tokens model_seconds physical_retrieval_calls logical_retrieval_calls failed_physical_queries reranker_forward_passes reranker_completed_forward_passes reranker_input_nonpadding_tokens reranker_padded_positions retrieval_seconds generated_model_calls recorded_encoder_nonpadding_tokens recorded_encoder_padded_positions additional_forward_passes_with_unrecorded_token_usage total_encoder_token_usage_complete query_seconds import_seconds init_seconds total_seconds attributed_to_any_method total_attributed_autoregressive_requests total_attributed_autoregressive_input_tokens total_attributed_autoregressive_output_tokens total_attributed_model_seconds retrieval_in_method_attribution attributed_total_input_tokens attributed_total_output_tokens attributed_total_model_requests'.split())
COST_CONTAINERS = set('total_new_execution shared_target_selection historical_baseline_costs new_extension_physical previous_quality34_free_reused shared_query_autoregressive own_answer_autoregressive added_autoregressive historical_B attributed_retrieval_tool_cost own_new_physical_cost shared_scoped_proposal_cost_attributed_once cycle4_method_cost inherited_query_cost inherited_retrieval_cost inherited_B_cost attributed_non_B_autoregressive_cost'.split())

SPECS = [
('cycle1','cached_smoke_review','cached_review/control_scores','per_input_status.jsonl',None),
('cycle1','quality34','quality34/results','per_input_status.jsonl',None),
('cycle1','a5_quality121','a5_quality121/results','per_input_status.jsonl',None),
('cycle1','readout_multi9_extension','readout_multi9_r2/results','per_input_status.jsonl',None),
('cycle1','readout_multi9_composite','readout_multi9_r2/composite_results','per_input_status.jsonl',None),
('cycle2','a1_target34','cycle2/a1_target34/results','per_input_status.jsonl',None),
('cycle2','a1_direct_verdict_posthoc','cycle2/a1_target34/direct_verdict_readout/results','per_input_status.jsonl',None),
('cycle2','a3_original8','cycle2/a3_original8/results','per_input_status.jsonl',None),
('cycle3','answer34','cycle3/answer34/results','per_input_status.jsonl',None),
('cycle4','answer34','cycle4/answer34/results','per_input_status.jsonl',None),
] + [(c,p,f'{d}/{m.lower()}/results','per_input_scored.jsonl',m) for c,p,d in [('cycle1','synthetic8','synthetic_live'),('cycle2','synthetic32','cycle2/a5_scope32')] for m in ('M4','M5')]
PAIR_SPECS = [('cycle1','quality34','quality34/results/pairs/pair_summary.json'),('cycle1','a5_quality121','a5_quality121/results/pairs/pair_summary.json'),('cycle1','readout_multi9_composite','readout_multi9_r2/composite_results/pairs/pair_summary.json'),('cycle2','a1_target34','cycle2/a1_target34/paired_results/pair_summary.json'),('cycle2','a3_original8','cycle2/a3_original8/paired_results/pair_summary.json'),('cycle3','answer34','cycle3/answer34/paired_results/pair_summary.json'),('cycle4','answer34','cycle4/answer34/paired_results/pair_summary.json')]


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,required=True);ap.add_argument('--output',type=Path,default=Path(__file__).parent);args=ap.parse_args();root=args.source_root;out=args.output;out.mkdir(parents=True,exist_ok=True)
 sources={}
 def source(rel):
  p=root/rel;b=p.read_bytes();sources[rel]={'relative_to_effect_first_root':rel,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return b
 def load(rel):return json.loads(source(rel))
 def rows(rel):return [json.loads(s) for s in source(rel).decode().splitlines() if s.strip()]
 def write(name,v): (out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 def pick(d,keys):return {k:d[k] for k in keys if k in d}
 def cselect(d):
  return {k:(cselect(v) if isinstance(v,dict) else v) for k,v in d.items() if (k in COST_KEYS and (v is None or isinstance(v,(int,float,bool)))) or (k in COST_CONTAINERS and isinstance(v,dict))}
 public=[];quality=[];pairs=[];panel_costs=[];groups={}
 for cycle,panel,directory,filename,method_fixed in SPECS:
  rel=f'{directory}/{filename}'; raw=rows(rel); summ=load(f'{directory}/summary.json'); bygroup=defaultdict(list)
  for i,r in enumerate(raw,1):
   method=method_fixed or r['method'];arm=r['arm']; native=r.get('native_valid',r.get('native_available'));correct=r.get('correct')
   assert isinstance(correct,(bool,type(None))), (rel,i)
   if native is False: assert correct is None or filename=='per_input_scored.jsonl', (rel,i)
   if native is False:correct=None
   row={'cycle':cycle,'panel':panel,'method':method,'arm':arm,'request_id':r['request_id'],'correct':correct,'native_valid':native,'run_status':r.get('run_status',r.get('status')),'native_mapping_count':r.get('native_mapping_count'),'method_score':r.get('method_score','scored' if native else 'not_scored'),'actual_adjudication':r.get('actual_adjudication'),'proposal_delivered':r.get('proposal_delivered'),'modified_answer':r.get('modified_answer'),'repair_attempted':r.get('repair_attempted'),'failure_type':r.get('failure_type'),'warnings':r.get('warnings'),'origin':r.get('origin'),'source_file':rel,'source_line':i}
   for k in ['method','arm','request_id','run_status','method_score','failure_type','origin']:
    val=row.get(k)
    assert val is None or (isinstance(val,str) and len(val)<160 and re.fullmatch(r'[A-Za-z0-9_.:/ -]+',val)),(k,val)
   public.append(row);bygroup[(method,arm)].append(row)
  for (method,arm),rs in bygroup.items():
   key=(cycle,panel,method,arm);assert key not in groups;groups[key]=rs
   if method_fixed: sv=summ['methods'][arm]; expected={'denominator':sv['planned_inputs'],'correct':sv['correct'],'unavailable':sv['unavailable']}
   else:
    ms=summ['methods']; ms=next(x for x in ms if x['method']==method) if isinstance(ms,list) else ms[method]
    if panel=='a1_direct_verdict_posthoc':sv=ms;expected=ms['new_identity']
    else:sv=ms.get('arms',ms)[arm];expected=sv.get('unique_inputs',sv)
   counts={'denominator':len(rs),'correct':sum(x['correct'] is True for x in rs),'incorrect':sum(x['correct'] is False for x in rs),'unavailable':sum(x['correct'] is None for x in rs)}
   for k in counts:
    if k in expected:assert expected[k]==counts[k],(cycle,panel,method,arm,k,expected[k],counts[k])
   q={'cycle':cycle,'panel':panel,'method':method,'arm':arm,'unique_inputs':counts,'native_mappings':pick(sv.get('native_mappings',{}),COUNT_KEYS),'native_unit_ALL':pick(sv.get('native_unit_ALL',{}),NATIVE_KEYS),'source_summary':f'{directory}/summary.json'}
   for k in ('actual_adjudications','proposal_delivered','modified_answers','format_repair_attempts','first_output_errors'):
    if k in sv:q[k]=sv[k]
   if sv.get('relative_to_B',{}).get('same_scope_B'):q['same_scope_B']=pick(sv['relative_to_B']['same_scope_B'],COUNT_KEYS)
   quality.append(q)
   if method_fixed:
    for relation in ('maintain','respond'):
     if relation in sv:pairs.append({'cycle':cycle,'panel':panel,'method':method,'arm':arm,'coverage':'synthetic_supported','relation':relation,**pick(sv[relation],PAIR_KEYS)})
  cpath=f'{directory}/cost_summary.json'
  if (root/cpath).exists():
   cs=load(cpath);methodcost={}
   for method,mv in cs.get('methods',{}).items():
    methodcost[method]=cselect(mv)
    for armcontainer in ('answer_arms','readout_acquisition_by_arm'):
     if armcontainer in mv:methodcost[method][armcontainer]={a:cselect(v) for a,v in mv[armcontainer].items()}
   panel_costs.append({'cycle':cycle,'panel':panel,'source':cpath,'total_new_execution':cselect(cs.get('total_new_execution',{})),'methods':methodcost})
  if method_fixed:panel_costs.append({'cycle':cycle,'panel':panel,'method':method_fixed,'source':f'{directory}/summary.json','physical_experiment_cost':cselect(summ['physical_experiment_cost']),'method_costs':{a:cselect(v) for a,v in summ['method_costs'].items()},'extra_model_stage_costs':{a:cselect(v) for a,v in summ['extra_model_stage_costs'].items()}})
 # Only recount saved correctness booleans. No answer parsing or native scoring.
 comparisons=[]
 for (cycle,panel,method,arm),rs in groups.items():
  base_arm='F' if panel.startswith('synthetic') else 'baseline';baseline=groups.get((cycle,panel,method,base_arm))
  if not baseline:continue
  br={r['request_id']:r for r in baseline};assert all(r['request_id'] in br for r in rs)
  base_counts=Counter('correct' if br[r['request_id']]['correct'] is True else 'incorrect' if br[r['request_id']]['correct'] is False else 'unavailable' for r in rs)
  for q in quality:
   if (q['cycle'],q['panel'],q['method'],q['arm'])==(cycle,panel,method,arm):q['same_scope_B']={'denominator':len(rs),**{k:base_counts[k] for k in ('correct','incorrect','unavailable')}}
  for comparator in sorted({base_arm}|{k[3] for k in groups if k[:3]==(cycle,panel,method) and k[3]!=arm}):
   rr=groups.get((cycle,panel,method,comparator));rc={r['request_id']:r for r in rr};ids=[r['request_id'] for r in rs]
   if not all(i in rc for i in ids):continue
   counts=Counter();events=defaultdict(list)
   for row in rs:
    i=row['request_id'];old=rc[i]['correct'];new=row['correct'];tag=None
    if old is False and new is True:tag='repairs'
    elif old is True and new is False:tag='harms'
    elif old is None and new is not None:tag='unavailable_recoveries'
    elif old is True and new is None:tag='correct_lost_to_unavailable'
    elif old is None and new is None:tag='both_unavailable'
    if tag:counts[tag]+=1;events[tag].append(i)
    if old is None and new is True:counts['correct_unavailable_recoveries']+=1;events['correct_unavailable_recoveries'].append(i)
   comparisons.append({'cycle':cycle,'panel':panel,'method':method,'arm':arm,'comparator':comparator,'denominator':len(rs),'counts':{k:counts[k] for k in ('repairs','harms','unavailable_recoveries','correct_unavailable_recoveries','correct_lost_to_unavailable','both_unavailable')},'request_ids':dict(events),'scope':'arm membership; comparator covers every member; no result-based selection'})
 for c,p,f in PAIR_SPECS:
  pairs.extend({'cycle':c,'panel':p,**pick(v,PAIR_KEYS)} for v in load(f)['summaries'])
 with (out/'per_input_status.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n");w.writeheader();w.writerows(public)
 write('quality_summary.json',{'status':'saved_metadata_export_verified','scope':'Exposed development only; panels, arms, and cycles overlap. Never sum their denominators as distinct patients. Historical121 remains unchanged.','note':'quality34 baseline pool has35 inputs because the3-input smoke adds a member; its main34 same-scopeB is24/28. Native-unit, native-mapping, unique-input and pair weights are different.','rows':quality,'comparisons':comparisons,'new_model_calls':0,'new_native_scoring_calls':0,'independent_evaluation':False})
 write('pair_summary.json',{'scope':'Saved pair summaries only. Small/degenerate bootstrap intervals do not establish population ability. Unsupported pairs cannot qualify A5.','rows':pairs,'new_native_scoring_calls':0,'new_model_calls':0})
 costs=[];tot=Counter()
 for cycle,rel,key in [('cycle1','cost_so_far.json','new_physical_cost'),('cycle2','cycle2/cost.json','actual_new_physical_cost'),('cycle3','cycle3/cost.json','actual_new_autoregressive_physical_cost'),('cycle4','cycle4/analysis/cost.json','actual_new_autoregressive_physical_cost')]:
  v=load(rel);new=cselect(v[key]);cc={'cycle':cycle,'source':rel,'new_physical_cost':new,'method_attribution':{m:{a:cselect(av) for a,av in mv.items()} for m,mv in v.get('method_attribution',{}).items()}}
  if cycle=='cycle3':
   for k in ('actual_new_retrieval_tool_cost','engineering_tool_probe_cost','all_occurred_tool_operations_including_engineering'):cc[k]=cselect(v[k])
  if cycle=='cycle4':
   for k in ('actual_new_retrieval_calls','actual_new_B_calls','actual_new_query_calls'):cc[k]=v[k]
  costs.append(cc)
  for k in ('new_model_requests','live_input_tokens','live_output_tokens','live_model_seconds'):tot[k]+=new[k]
 historical_target=load('cycle2/a1_target34/historical_target_and_base_costs.json')
 write('cost_summary.json',{'scope':'Only the four effect-first cycles. NOT an all-history project total. Physical cost counts each source run once. Shared/inherited method attribution must not be summed again. Existing historical initial answers excluded by source accounting.','cycle_new_costs':costs,'four_cycle_physical_subtotal':dict(tot),'panel_costs_non_additive':panel_costs,'cycle2_reused_target_selection':{m:cselect(v['target_selection_shared_once_per_input']) for m,v in historical_target['methods'].items()},'limitations':['Cycle1/2 per-panel new cost is not complete all-tools method attribution; B and reused expert material remain separate.','Same caps do not imply equal realized tokens or cost.','Model seconds are cumulative reported wall seconds, not exclusive GPU time, energy, or measured end-to-end latency.','The cycle3 engineering probe has1 forward pass with unknown encoder token use, not zero.','Composite/posthoc/cached exports create no new model cost.']})
 # Explicitly sanitized failure metadata from saved rows and decisions.
 fails=Counter((r['cycle'],r['panel'],r['method'],r['arm'],r['failure_type'] or 'unavailable_unspecified') for r in public if r['correct'] is None)
 decision=load('cycle4/decision.json');load('cycle4/native_diagnosis_contract_diagnosis.json');load('cycle3/decision.json');load('cycle2/decision.json');load('non_adoption_decision.json')
 write('failure_and_limitations.json',{'status':'all_four_cycles_not_adopted','unavailable_rows':[{'cycle':c,'panel':p,'method':m,'arm':a,'failure_type':t,'count':n} for (c,p,m,a,t),n in sorted(fails.items())],'cycle3_query_failures':{'method':'M4','request_ids':['d00018','d00054','d00062','d00077'],'type':'output_truncation','inference_started':True,'optional_query_not_native_answer':'preserved; answers independently continued under frozen optional-search contract'},'cycle4_new_failures':decision['new_native_failures'],'cycle4_retained_prior_failure':decision['retained_prior_failure'],'diagnosis_readout_gap':{k:decision['implementation_gap'][k] for k in ('kind','claim_correction','affected_future_path','remediation','remediation_status')},'scope_notes':['C3/C4 valid JSON is not evidence of finite catalog-key decoding; diagnosis free-string path not qualified for further expansion.','No failed prefix was salvaged into an old successful method.','Failures remain in denominators; unavailable means not_scored, not an incorrect answer.','Unavailable rows may recur in multiple panels and arms; the counts here are NOT unique physical failures.','Clinical semantic cause is unknown when evidence is insufficient.','Independent evaluation has not begun; all old adopted A2/A3/A4/F and native scoring remain unchanged.']})
 write('source_manifest.json',{'source_root_label':'effect_first_revision_20260923','files':list(sources.values()),'export_policy':'Finite allowlists. No prompts, schemas containing patient data, native answers, predictions, gold, hidden pair contents, raw errors, raw reasons or document quotations copied. Source filenames, hashes, development request IDs, numeric performance and cost/status metadata retained.','new_model_calls':0,'native_scoring_calls':0,'gold_fields_consulted':0})
 print(json.dumps({'rows':len(public),'quality_groups':len(quality),'pair_groups':len(pairs),'sources':len(sources),'four_cycle_physical_subtotal':dict(tot)}))

if __name__=='__main__':main()
