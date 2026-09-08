"""Join complete local comparisons and make the requested thousand-scale analysis subset."""
import csv,json,random
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
LABELS={'R1':'新增支持','R2':'撤销支持','R3':'重新比较','R4':'推导后果','R5':'保持判断'}
SEED=20260908
FIELDS=['unit_id','resource_id','benchmark','source_root_id','analysis_selected','status','annotation_method','labels','label_names','change','target','rationale','evidence','cannot_infer','quality_flags','source','clinical_review']
def rows(p):
 with p.open() as f:
  for l in f:
   if l.strip():yield json.loads(l)
def dumps(x):return json.dumps(x,ensure_ascii=False,allow_nan=False)
def rootid(u):
 if 'source_root_id' in u:return u['source_root_id']
 rid=u['resource_id'];sid=u['source_unit_id']
 if rid in ['M02','M16']:return None
 if rid in ['M12','M17']:return sid.rsplit(':',1)[0]
 if rid=='M22':return sid.rsplit(':DOC_',1)[0]
 if rid=='M24':return sid.rsplit(':locality_',1)[0]
 if rid=='M14':return 'source_row_'+str(u['original_records'][0]['Row Number'])
 return sid

def normalize(u,part):
 rid=u['resource_id'];u['source_root_id']=rootid(u)
 if rid=='M16':u['source_root_id']=None
 if u.get('annotation_method')=='pending':u['annotation_method']='pending_review'
 u['annotation_source_file']=str(part.relative_to(ROOT))
 u['label_names']=[LABELS[l] for l in u['labels']]
 u['collection_kind']='documentation_example' if rid=='M09' else 'multimodal_edit_metadata_images_missing' if rid=='M25' else 'text_comparison_record'
 u['quality_flags']=list(dict.fromkeys(u.get('quality_flags',[])+u.get('source_quality_flags',[])))
 if rid=='M01' and len(u['original_records'])==2 and ' '.join(u['original_records'][0]['narrative'].split())==' '.join(u['original_records'][1]['narrative'].split()):
  if 'no_visible_clinical_text_change' not in u['quality_flags']:u['quality_flags'].append('no_visible_clinical_text_change')
 u['cf_eligible']=u.get('cf_eligible',True) and u.get('counted_as_cf',True) and rid!='M09'
 if any(flag in u['quality_flags'] for flag in ['no_visible_clinical_text_change','no_visible_change','no_op_exact_text','no_op']):u['cf_eligible']=False
 u['source_root_note']='Official source question/edit root, not an independently verified patient; null indicates no verified one-root pairing.'
 p=Path(u['source']['file'])
 if not p.is_absolute():p=ROOT.parent/p
 assert p.is_file(),str(p)
 u['source']['file']=str(p)
 assert bool(u['labels'])==(u['status']=='labeled'),u['unit_id']
 assert set(u['labels'])<=set(LABELS) and u['clinical_review'] is False
 return u

def stratum(u):
 rid=u['resource_id']
 if rid=='M01':return u['original_records'][1].get('ground_truth','unknown')
 if rid=='M10':
  r=u['original_records'][0];return str(r['ethnicity'])+':'+str(r['gender_male'])+':'+str(r['gender_female'])
 if rid=='M23':return str(u.get('noise_condition',u.get('perturbation',u.get('selected_role','BioNLI'))))
 return str(u.get('subtask',u.get('split',u.get('task_type',u.get('unit_kind','default')))))

def select(meta):
 # Clinical labels and model scores do not participate in sampling.
 out=set();policy={};rng=random.Random(SEED)
 for rid,us in sorted(meta.items()):
  eligible=[u for u in us if u['cf_eligible']]
  # MedCF split is part of the native edit protocol. Preserve training/development
  # units in the complete corpus; use all official test edits in the analysis.
  if rid=='M24':
   test=[u for u in eligible if u.get('split',u.get('source_split',u.get('official_split')))=='test']
   if test:eligible=test
  n=len(eligible)
  if n<5000:chosen=eligible;mode='all_eligible_under_5000'
  else:
   # Stratified round-robin, distinct source roots first within each stratum.
   strata=defaultdict(lambda:defaultdict(list))
   for u in eligible:strata[u['sampling_stratum']][u['source_root_id'] or u['unit_id']].append(u)
   queues=[]
   for _,roots in sorted(strata.items()):
    keys=sorted(roots);rng.shuffle(keys)
    for vs in roots.values():rng.shuffle(vs)
    q=[];level=0
    while any(len(roots[k])>level for k in keys):
     q.extend(roots[k][level] for k in keys if len(roots[k])>level);level+=1
    queues.append(q)
   rng.shuffle(queues);chosen=[];level=0
   while len(chosen)<2500:
    for q in queues:
     if len(q)>level:chosen.append(q[level])
     if len(chosen)==2500:break
    level+=1
   mode='2500_from_at_least_5000_stratified_root_round_robin'
  out.update(u['unit_id'] for u in chosen)
  policy[rid]={'normalized_units':len(us),'eligible_pool':n,'analysis_units':len(chosen),'mode':mode,'sampling_strata':dict(Counter(u['sampling_stratum'] for u in chosen)),'source_roots_in_analysis':len({u['source_root_id'] for u in chosen if u['source_root_id'] is not None})}
 return out,policy

def main():
 if (ROOT/'reports/classification_review.json').exists():
  raise SystemExit('Reviewed corpus exists. Apply annotations with scripts/finalize_review.py; do not reset it with the preliminary assembler.')
 parts=sorted((ROOT/'parts').glob('*/full_units.jsonl'));assert len(parts)==4
 meta=defaultdict(list);ids=set()
 for part in parts:
  for raw in rows(part):
   u=normalize(raw,part);uid=u['unit_id'];assert uid not in ids,uid;ids.add(uid)
   m={k:u.get(k) for k in ['unit_id','resource_id','source_root_id','cf_eligible','split','source_split','official_split']};m['sampling_stratum']=stratum(u);meta[u['resource_id']].append(m)
 selected,policy=select(meta)
 counts=Counter();byrid=defaultdict(Counter);labels=Counter();selected_labels=Counter();methods=Counter();bylabel=defaultdict(set);frozen={}
 files={name:(ROOT/name).open('w') for name in ['全部比较单元.jsonl','已标注比较单元.jsonl','待定比较单元.jsonl','分析子集.jsonl','分析子集_已标注.jsonl','参照与不计CF记录.jsonl']}
 csvfiles={name:(ROOT/name).open('w',encoding='utf-8-sig',newline='') for name in ['逐题标注.csv','分析子集_逐题标注.csv']}
 writers={name:csv.DictWriter(f,fieldnames=FIELDS) for name,f in csvfiles.items()}
 for w in writers.values():w.writeheader()
 for part in parts:
  for raw in rows(part):
   u=normalize(raw,part);uid=u['unit_id'];rid=u['resource_id'];u['analysis_selected']=uid in selected
   counts['normalized_units']+=1;counts[u['collection_kind']]+=1;counts[u['status']]+=1;byrid[rid]['units']+=1;byrid[rid][u['status']]+=1;methods[u['annotation_method']]+=1
   if u['cf_eligible']:counts['eligible_units']+=1
   else:counts['non_cf_or_problem_records']+=1
   if u['analysis_selected']:counts['analysis_units']+=1;counts['analysis_'+u['status']]+=1;byrid[rid]['analysis_units']+=1;byrid[rid]['analysis_'+u['status']]+=1
   frozen[uid]=u['labels']
   for l in u['labels']:
    labels[l]+=1;byrid[rid][l]+=1;bylabel[l].add(rid)
    if u['analysis_selected']:selected_labels[l]+=1
   line=dumps(u)+'\n';files['全部比较单元.jsonl'].write(line)
   if u['status']=='labeled':files['已标注比较单元.jsonl'].write(line)
   elif u['status']=='uncertain':files['待定比较单元.jsonl'].write(line)
   if u['analysis_selected']:
    files['分析子集.jsonl'].write(line)
    if u['labels']:files['分析子集_已标注.jsonl'].write(line)
   if not u['cf_eligible']:files['参照与不计CF记录.jsonl'].write(line)
   row={k:dumps(u.get(k)) if isinstance(u.get(k),(dict,list)) else u.get(k,'') for k in FIELDS}
   writers['逐题标注.csv'].writerow(row)
   if u['analysis_selected']:writers['分析子集_逐题标注.csv'].writerow(row)
 # Every separately retained no-op/reference record remains in the package.
 for part in sorted(list((ROOT/'parts').glob('*/full_reference_only.jsonl'))+list((ROOT/'parts').glob('*/full_references.jsonl'))):
  for u in rows(part):files['参照与不计CF记录.jsonl'].write(dumps(u)+'\n');counts['separately_retained_reference_records']+=1
 for f in list(files.values())+list(csvfiles.values()):f.close()
 freeze={'scope':'Complete normalized units; labels frozen before reading saved model predictions. Rule labels are preliminary, not expert gold.','inference_calls':0,'unit_labels':frozen}
 (ROOT/'reports/annotation_freeze.json').write_text(dumps(freeze))
 sampling={'seed':SEED,'prediction_or_annotation_labels_used':False,'threshold':5000,'large_source_target':2500,'policy':'<1000全部收录；1000–4999目标子集原则全收；>=5000按作者子任务/属性和源根抽2500。MedCF保存802条test，正式分析798条有效编辑，另4条原值未变参照；其余split完整保留。缺图多模态单列。','resources':policy}
 (ROOT/'reports/analysis_selection.json').write_text(json.dumps(sampling,ensure_ascii=False,indent=2))
 stats={'resource_candidates':26,**counts,'label_counts':dict(labels),'analysis_label_counts':dict(selected_labels),'annotation_methods':dict(methods),'sources_by_label':{k:sorted(v) for k,v in bylabel.items()},'by_resource':{k:dict(v) for k,v in byrid.items()},'clinical_expert_validated':False,'all_items_individually_reviewed':False,'annotation_or_sampling_uses_predictions':False,'inference_calls':0,'pilot_records':358}
 (ROOT/'reports/collection_counts.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
 catalog=json.loads((ROOT/'pilot_358/资源目录.json').read_text())
 for r in catalog:
  rid=r['resource_id'];r['pilot_selected_units']=r.pop('selected_units',0);r.update(full_counts=dict(byrid[rid]),analysis_selection=policy.get(rid,{}))
  r.pop('labeled_units',None);r.pop('uncertain_units',None);r.pop('source_roots_in_selected',None);r.pop('label_counts',None)
  r['acquisition_note']='Acquisition fields describe the raw release and access status; historical selected/labeled counts there refer to the archived pilot. Current counts are full_counts and analysis_selection.'
 (ROOT/'资源目录.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
 with (ROOT/'资源目录.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['resource_id','benchmark','scope','full_counts','analysis_selection','primary_source']);w.writeheader()
  for r in catalog:w.writerow({k:dumps(r[k]) if isinstance(r[k],dict) else r[k] for k in w.fieldnames})
 table='|编号|资源|完整比较记录|分析子集|分析已标|分析待定|全库R1/R2/R3/R4/R5|\n|---|---|---:|---:|---:|---:|---|\n'
 for r in catalog:
  c=byrid[r['resource_id']];table+=f"|{r['resource_id']}|{r['benchmark']}|{c['units']}|{c['analysis_units']}|{c['analysis_labeled']}|{c['analysis_uncertain']}|"+'/'.join(str(c[l]) for l in LABELS)+'|\n'
 (ROOT/'reports/来源与标签计数.md').write_text('# 全量与分析子集计数\n\n'+table+'\n标签允许重叠；子任务、知识编辑根、患者对和图像元数据不换算成独立患者数。待定记录仍保留。\n')
 print(json.dumps({k:v for k,v in stats.items() if k!='by_resource'},ensure_ascii=False))
if __name__=='__main__':main()
