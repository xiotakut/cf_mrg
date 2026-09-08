"""Account for all 25,280 original inputs and reuse their frozen native predictions offline."""
import csv,json,os,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
CF=Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
OLD=CF/'results_cf_full_comparison'
os.environ['CF_SCREENING_OUTPUT']='results_cf_full_comparison'
sys.path.insert(0,str(CF/'scripts'))
from analyze_cf_baseline_screening import score,METHODS

def rows(p):
 with p.open() as f:
  for l in f:
   if l.strip():yield json.loads(l)
def key(r):return (r['dataset'],r['source_id'],r['role'],r['protocol'])
def table(path,data):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def main():
 freeze=json.loads((ROOT/'reports/annotation_freeze.json').read_text())['unit_labels']
 lablist=list(rows(OLD/'evaluation_labels.jsonl'));labs={key(r):r for r in lablist};items={r['item_id']:r for r in rows(OLD/'screening_items.jsonl')}
 assert len(items)==25280 and len(lablist)==27377 and len(labs)==len(lablist)
 links=defaultdict(list);unitmeta={};required=set();reference_only_keys=set()
 for u in rows(ROOT/'全部比较单元.jsonl'):
  assert freeze[u['unit_id']]==u['labels']
  refs=u.get('existing_evaluation_records',u.get('existing_evaluation_links',[]))
  if not refs:continue
  uid=u['unit_id'];unitmeta[uid]={k:u.get(k) for k in ['unit_id','resource_id','source_root_id','labels','status','annotation_method','analysis_selected','cf_eligible','review_state','review_resolution','review_coverage']}
  for ref in refs:
   k=key(ref);e=labs[k];assert ref['item_id']==e['item_id'] and ref['gold']==e['gold']
   txt=u.get('reference_text' if ref['role']=='reference' else 'variant_text')
   if txt is not None:assert txt==items[e['item_id']]['question'],uid
   links[k].append(uid);required.add(e['item_id'])
 for u in rows(ROOT/'参照与不计CF记录.jsonl'):
  for ref in u.get('existing_evaluation_records',u.get('existing_evaluation_links',[])):reference_only_keys.add(key(ref))
 assert set(unitmeta)=={uid for uid in freeze if uid.split(':')[0] in ['M01','M02','M10','M11','M20']}
 # Freeze is checked before any saved model answer is opened.
 preds={(r['item_id'],r['method']):r for r in rows(OLD/'predictions.jsonl')}
 assert len(preds)==75840 and all((iid,m) in preds for iid in items for m in METHODS.values())
 canonical=json.loads((OLD/'canonical_labels.json').read_text());scores={};summary=defaultdict(list);lineage=defaultdict(list);inputlabs=defaultdict(list);coverage=Counter()
 for e in lablist:inputlabs[e['item_id']].append(e)
 with (ROOT/'reports/旧库全部输入索引.jsonl').open('w') as out:
  for i,(iid,item) in enumerate(items.items(),1):
   es=inputlabs[iid];matched=sorted({uid for e in es for uid in links[key(e)]});retained=bool(matched)
   reasons=[]
   if any(e['dataset']=='medpic' and e['protocol']=='native' and not links[key(e)] for e in es):reasons.append('MedPIC_GF_reference')
   if any(e['protocol']!='native' for e in es):reasons.append('historical_sensitivity_protocol')
   if any(key(e) in reference_only_keys for e in es):reasons.append('no_op_or_flagged_source_record')
   if not retained and not reasons:reasons.append('reference_for_source_roots_without_changed_variant')
   coverage['with_cf_comparison_link' if retained else 'retained_reference_or_control_input']+=1
   out.write(json.dumps({'item_id':iid,'source_file':str(OLD/'screening_items.jsonl'),'source_line_1based':i,'answer_format':item['answer_format'],'original_input':item,'comparison_unit_ids':matched,'native_evaluation_keys':[{'dataset':e['dataset'],'source_id':e['source_id'],'role':e['role'],'protocol':e['protocol']} for e in es],'reference_or_control_roles':reasons,'saved_prediction_methods':list(METHODS)},ensure_ascii=False)+'\n')
 with (ROOT/'reports/已有预测_逐题重分类.jsonl').open('w') as out:
  for e in lablist:
   k=key(e);item=items[e['item_id']];uids=links[k]
   for code,method in METHODS.items():
    pr=preds[(e['item_id'],method)];s=score(pr,e,item,canonical);scores[(k,code)]=s
    row={'item_id':e['item_id'],'dataset':e['dataset'],'source_id':e['source_id'],'role':e['role'],'protocol':e['protocol'],'method':code,'original_gold':e['gold'],'original_raw_response':pr['raw_response'],'linked_units':[unitmeta[uid] for uid in uids],**s}
    out.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
    if e['protocol']=='native' and e['role']!='reference':
     for uid in uids:
      u=unitmeta[uid]
      if not u['cf_eligible'] or not u['labels']:continue
      for scope in ['complete']+(['analysis_subset'] if u['analysis_selected'] else []):
       for label in u['labels']:summary[(scope,u['resource_id'],label,code,item['answer_format'])].append((u,s))
 data=[];metrics={'diagnosis':'canonical diagnosis match','multi':'exact set accuracy','single':'option accuracy','relation':'evidence agreement'}
 for (scope,rid,label,code,fmt),rs in sorted(summary.items()):
  roots=defaultdict(list)
  for u,s in rs:roots[u['source_root_id'] or u['unit_id']].append(int(s['correct']))
  data.append({'scope':scope,'annotation_scope':'reviewed_frozen_cohort' if scope=='analysis_subset' else 'mixed_reviewed_and_previous_preliminary','resource_id':rid,'label':label,'method':code,'native_metric':metrics[fmt],'target_records':len(rs),'source_roots_or_unpaired_rows':len(roots),'correct':sum(s['correct'] for _,s in rs),'score':sum(s['correct'] for _,s in rs)/len(rs),'source_macro_score':sum(sum(v)/len(v) for v in roots.values())/len(roots),'invalid':sum(s['invalid'] for _,s in rs),'unmapped_diagnosis':sum(s['unmapped_diagnosis'] for _,s in rs)})
 table(ROOT/'reports/已有预测_来源标签统计.csv',data)
 views=defaultdict(dict)
 for k,uids in links.items():
  for uid in uids:views[uid][k[2]]=k
 pairs=[]
 for uid,rs in views.items():
  if 'reference' not in rs:continue
  for role,k in rs.items():
   if role=='reference':continue
   for code in METHODS:
    ref=scores[(rs['reference'],code)];var=scores[(k,code)];u=unitmeta[uid]
    pairs.append({'unit_id':uid,'resource_id':u['resource_id'],'labels':' '.join(u['labels']),'annotation_method':u['annotation_method'],'analysis_selected':u['analysis_selected'],'method':code,'reference_correct':ref['correct'],'variant_correct':var['correct'],'both_correct':ref['correct'] and var['correct'],'correct_to_wrong':ref['correct'] and not var['correct'],'wrong_to_correct':not ref['correct'] and var['correct'],'both_wrong':not ref['correct'] and not var['correct']})
 table(ROOT/'reports/已有预测_配对正确性.csv',pairs)
 report={'old_unique_inputs':len(items),'old_evaluation_records_per_method':len(lablist),'old_unique_predictions_all_methods':len(preds),'all_original_inputs_accounted_for':sum(coverage.values())==len(items),'input_coverage':dict(coverage),'source_input_file':str(OLD/'screening_items.jsonl'),'source_prediction_file':str(OLD/'predictions.jsonl'),'source_parser':str(CF/'scripts/analyze_cf_baseline_screening.py')+':score','comparison_units_with_existing_predictions':len(unitmeta),'analysis_units_with_existing_predictions':sum(u['analysis_selected'] for u in unitmeta.values()),'labeled_comparison_units_with_existing_predictions':sum(bool(u['labels']) for u in unitmeta.values()),'reclassified_evaluation_rows_all_methods':len(scores),'comparison_required_unique_inputs':len(required),'source_label_metric_rows':len(data),'new_model_calls':0,'changed_inputs':0,'all_original_gold_and_native_scoring_preserved':True,'pooled_cross_task_accuracy_computed':False,'functional_reasoning_error_rate_established':False,'label_freeze_matched':True,'complete_scope_includes_unreviewed_annotations':True,'analysis_scope_reviewed':True}
 (ROOT/'reports/prediction_reuse.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
