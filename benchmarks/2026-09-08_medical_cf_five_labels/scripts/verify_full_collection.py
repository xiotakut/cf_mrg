"""Check full coverage, thousand-scale sampling, source links and unchanged prediction reuse."""
import csv,json
from itertools import chain, zip_longest
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
def rows(p):
 with p.open() as f:
  for l in f:
   if l.strip():yield json.loads(l)
def main():
 csv.field_size_limit(20_000_000)
 stats=json.loads((ROOT/'reports/collection_counts.json').read_text());policy=json.loads((ROOT/'reports/analysis_selection.json').read_text());freeze=json.loads((ROOT/'reports/annotation_freeze.json').read_text())['unit_labels']
 assert len(json.loads((ROOT/'资源目录.json').read_text()))==26
 sources=set();partlabels={};partcounts=Counter()
 for p in (ROOT/'parts').glob('*/full_units.jsonl'):
  for u in rows(p):partlabels[u['unit_id']]=u['labels'];partcounts[u['resource_id']]+=1
 units={};counts=Counter();actual=Counter();chosen=[];methods=Counter();rootrefs=set();judgments=Counter()
 for u in rows(ROOT/'全部比较单元.jsonl'):
  uid=u['unit_id'];assert uid not in units;units[uid]={k:u.get(k) for k in ['resource_id','labels','status','analysis_selected','cf_eligible','reviewed_target_count']}
  assert freeze[uid]==u['labels']
  if u['analysis_selected']:
   assert u.get('review_state')=='reviewed' and u.get('review_resolution') in ['classified','insufficient_evidence','invalid_source','outside_five_labels'],uid
   assert bool(u['labels'])==(u['review_resolution']=='classified')
   assert set(u['labels'])=={l for j in u['judgments'] for l in j['labels']},uid
   assert u['reviewed_target_count']==len(u['judgments']) and 'target_annotations' not in u,uid
   assert all(j.get('review_state')=='reviewed' and j.get('target') and j.get('rationale') and j.get('evidence') for j in u['judgments']),uid
  else:
   assert partlabels[uid]==u['labels'] and u.get('review_state')=='outside_frozen_review_cohort',uid
  assert bool(u['labels'])==(u['status']=='labeled') and u['clinical_review'] is False
  if u['labels']:assert u['target'] and u['rationale'] and u['evidence']
  methods[u['annotation_method']]+=1;counts[u['status']]+=1;actual[u['resource_id']]+=1;sources.add(u['source']['file'])
  if u.get('root_record_ref'):rootrefs.add(json.dumps(u['root_record_ref'],sort_keys=True))
  if u['analysis_selected']:chosen.append(uid);assert u['cf_eligible']
  for j in u.get('judgments',[]):
   if 'status'in j:assert bool(j.get('labels'))==(j['status']=='labeled'),j
   method=j.get('annotation_method',u['annotation_method'])
   judgments['pending_review' if method=='pending' else method]+=1
 assert len(units)==stats['normalized_units']==len(partlabels) and actual==partcounts
 assert counts['labeled']==stats['labeled'] and counts['uncertain']==stats['uncertain']
 assert methods==stats['annotation_methods'] and len(chosen)==stats['analysis_units']
 assert chosen==[r['unit_id'] for r in rows(ROOT/'review_20260908/input_manifest.jsonl')]
 # Compare retained native payloads independently with the original adapters.
 payload_fields=['original_records','original_task','native_task','source_unit_id','source_root_id','root_record_ref','reference_text','variant_text','existing_evaluation_records','existing_evaluation_links']
 source_rows=chain.from_iterable(rows(p) for p in sorted((ROOT/'parts').glob('*/full_units.jsonl')))
 for a,b in zip_longest(source_rows,rows(ROOT/'全部比较单元.jsonl')):
  assert a and b and a['unit_id']==b['unit_id']
  for k in payload_fields:
   if k=='source_root_id' and a['resource_id']=='M16':
    assert b[k] is None  # Existing normalization: a pair is not a verified single root.
    continue
   if k in a:assert a[k]==b[k],(a['unit_id'],k)
 assert all(Path(p).is_file() for p in sources)
 for name,condition in [('已标注比较单元.jsonl',lambda u:u['status']=='labeled'),('待定比较单元.jsonl',lambda u:u['status']=='uncertain'),('分析子集.jsonl',lambda u:u['analysis_selected']),('分析子集_已标注.jsonl',lambda u:u['analysis_selected'] and u['labels'])]:
  expected={uid for uid,u in units.items() if condition(u)};got={u['unit_id'] for u in rows(ROOT/name)};assert got==expected,name
 for name,wanted in [('逐题标注.csv',set(units)),('分析子集_逐题标注.csv',set(chosen))]:
  with (ROOT/name).open(encoding='utf-8-sig') as f:assert {r['unit_id'] for r in csv.DictReader(f)}==wanted,name
 with (ROOT/'分析子集_未能定类.csv').open(encoding='utf-8-sig') as f:
  unresolved=[r['unit_id'] for r in csv.DictReader(f)]
 assert len(unresolved)==len(set(unresolved)) and set(unresolved)=={uid for uid in chosen if not units[uid]['labels']}
 child_counts=Counter();child_ids=set();child_labels=defaultdict(set)
 with (ROOT/'分析子集_具体判断.csv').open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   uid=r['unit_id'];jid=r['judgment_id'];assert uid in units and units[uid]['analysis_selected'] and jid not in child_ids
   child_ids.add(jid);child_counts[uid]+=1;child_labels[uid].update(json.loads(r['labels']))
 assert child_counts=={uid:units[uid]['reviewed_target_count'] for uid in chosen}
 assert all(child_labels[uid]==set(units[uid]['labels']) for uid in chosen)
 for rid,r in policy['resources'].items():
  assert r['analysis_units']==(r['eligible_pool'] if r['eligible_pool']<5000 else 2500),rid
 assert policy['prediction_or_annotation_labels_used'] is False
 reuse=json.loads((ROOT/'reports/prediction_reuse.json').read_text())
 index=list(rows(ROOT/'reports/旧库全部输入索引.jsonl'))
 assert len(index)==len({u['item_id'] for u in index})==reuse['old_unique_inputs']==25280
 assert all(r['original_input']['item_id']==r['item_id'] and r['saved_prediction_methods']==['M0','M1','M2'] for r in index)
 unit_ids=set(units)
 assert all(set(r['comparison_unit_ids'])<=unit_ids for r in index)
 scored=0;predkeys=set()
 for r in rows(ROOT/'reports/已有预测_逐题重分类.jsonl'):
  scored+=1;predkeys.add((r['item_id'],r['method']))
  for u in r['linked_units']:
   assert u['labels']==freeze[u['unit_id']]
   assert u['analysis_selected']==units[u['unit_id']]['analysis_selected']
 assert scored==reuse['reclassified_evaluation_rows_all_methods']==27377*3
 assert len(predkeys)==reuse['old_unique_predictions_all_methods']==25280*3
 assert reuse['all_original_inputs_accounted_for'] and reuse['new_model_calls']==0 and reuse['changed_inputs']==0
 # Cross-file root references must resolve; the source text is retained once.
 evidence_roots=set()
 for r in rows(ROOT/'parts/evidence_other/full_root_records.jsonl'):
  evidence_roots.add((r['resource_id'],r['source_root_id']))
 for ref in rootrefs:
  r=json.loads(ref);assert Path(r['file']).is_file() and (r['resource_id'],r['source_root_id']) in evidence_roots
 audits=['parts/clinical_existing/full_rule_review.json','parts/clinical_existing/cross_rule_review.json','parts/evidence_other/full_rule_audit.json','parts/new_clinical/full_validation.json']
 result={'status':'passed','complete_comparison_records':len(units),'analysis_comparison_records':len(chosen),'resource_entries':26,'source_files_exist':len(sources),'root_references_resolved':len(rootrefs),'previous_inputs_accounted':25280,'saved_unique_predictions_accounted':len(predkeys),'native_and_sensitivity_evaluation_rows_reused':scored,'complete_and_analysis_export_ids_consistent':True,'frozen_labels_preserved':True,'sampling_uses_predictions_or_labels':False,'new_model_calls':0,'clinical_expert_validation':False,'per_target_annotation_methods_scope':'complete_corpus_including_nonselected','per_target_annotation_methods':dict(judgments),'review_target_export_rows':len(child_ids),'unclassified_parent_export_rows':len(unresolved),'source_rule_audits':[p for p in audits if (ROOT/p).is_file()],'reviewed_analysis_units':len(chosen),'analysis_ids_and_order_unchanged':True,'native_source_payloads_unchanged':True,'all_reviewed_parent_labels_equal_child_union':True,'note':'Structural/source coverage validation. Semantic item review, semantic group review and structural verification remain distinct; source gold is not promoted to clinical expert validation.'}
 (ROOT/'reports/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
