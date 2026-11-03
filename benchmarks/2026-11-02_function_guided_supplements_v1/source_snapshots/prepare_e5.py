"""Identity-only exposure update, fixed family selection, and legal input packets."""
import sys,json,re,hashlib,collections,os
from pathlib import Path
from dataclasses import asdict
from common import ROOT,WORK,rows,dump,write,sha,now
sys.path.insert(0,str(WORK))
from cf_moa.contracts import InputPacket,Budget,NATIVE_FIELDS
from cf_moa.evaluation import c0_native
from cf_moa.tools.legacy import r5_module
from cf_moa.controller.strong_legacy import select

D=WORK/'Documents/Codex/2026-09-18/r5_head/mechanism_research/data'
OUT=ROOT/'e5';OUT.mkdir(exist_ok=True)
assert not (OUT/'preparation.json').exists(),'Keep the original frozen family selection.'
members=list(rows(D/'selected_candidates.jsonl'));native=list(rows(D/'items.jsonl'))
norm=lambda t:hashlib.sha256(' '.join(t.casefold().split()).encode()).hexdigest()
def premise(q):
 m=re.search(r'premise:(.*?)\s+hypothesis:',q,re.I|re.S)
 return norm(m.group(1)) if m else None
candidate_units={r['unit_id']:r for r in members}
item_units={i['item_id']:i['unit_id'] for i in native if i.get('unit_id') in candidate_units}
if not item_units:
 # Existing materialization uses evaluation only for identity joins; no values are printed.
 item_units={e['item_id']:e['unit_id'] for e in rows(D/'evaluation.jsonl') if e['unit_id'] in candidate_units}
q_units=collections.defaultdict(set);p_units=collections.defaultdict(set)
for item in native:
 if item['item_id'] not in item_units:continue
 uid=item_units[item['item_id']];q_units[norm(item['question'])].add(uid)
 if premise(item['question']):p_units[premise(item['question'])].add(uid)

# Bounded, explicit inventory of post-18 September working input manifests. Read
# identity/text fields only; neither answer values nor correctness select families.
roots=[p for p in (WORK/'Documents/Codex').iterdir() if p.is_dir() and re.match(r'^2026-\d\d-\d\d$',p.name) and p.name>='2026-09-18']
roots += [p for p in Path('/home/data4/txy/codex_runs').iterdir() if p.is_dir() and re.match(r'^2026-',p.name)]
files=[]
for root in roots:
 for directory,dirs,names in os.walk(root):
  dirs[:]=[x for x in dirs if x not in ('.git','.venv','node_modules','__pycache__','responses','submitted','raw','runtime_cache','source_snapshot','before','models')]
  path=Path(directory)
  if path==ROOT or path==D or path.name.startswith('before_legacy_exposure'):
   dirs[:]=[];continue
  for name in names:
   if name in ('items.jsonl','inputs.jsonl','input_manifest.jsonl') or (path.name=='inference' and name in ('m4.jsonl','m5.jsonl','m4.json','m5.json')):
    files.append(path/name)
audit=[];excluded=set()
for path in sorted(set(files)):
 seen=0;matches=set()
 data=json.load(path.open()) if path.suffix=='.json' else rows(path)
 if isinstance(data,dict):
  audit.append(dict(path=str(path),sha256=sha(path),status='unsupported_json_container'));continue
 for row in data:
  if not isinstance(row,dict):continue
  item=row.get('item',row.get('native_input',row.get('packet',{}).get('native_input',row)))
  if not isinstance(item,dict) or not isinstance(item.get('question'),str):continue
  seen+=1;matches.update(q_units.get(norm(item['question']),set()))
  pr=premise(item['question'])
  if pr:matches.update(p_units.get(pr,set()))
 prior_unexecuted=WORK/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/confirmation/preparation'
 preparation_only=path.is_relative_to(prior_unexecuted)
 if preparation_only:assert (OUT/'prior_preparation_identity.json').exists()
 else:excluded.update(matches)
 audit.append(dict(path=str(path),sha256=sha(path),input_rows=seen,overlap_units=sorted(matches),exposure_kind='same128_prepared_not_executed' if preparation_only else 'other_working_input_exclusion'))
write(OUT/'exposure_scan.jsonl',audit)
allocation={'M10':8,'M14':8,'M17':8,'M22':4,'M23':4}
selected=[]
for source,n in allocation.items():
 eligible=[r for r in members if r['resource_id']==source and r['unit_id'] not in excluded]
 eligible.sort(key=lambda r:hashlib.sha256(('e5-20261102:'+r['group_id']).encode()).hexdigest())
 assert len(eligible)>=n,(source,len(eligible),n)
 selected+=eligible[:n]
assert len({r['group_id'] for r in selected})==32
units={r['unit_id'] for r in selected};ids=sorted(iid for iid,uid in item_units.items() if uid in units)
assert len(ids)==112,len(ids)
handles={iid:f'n{i:04d}' for i,iid in enumerate(ids)}
write(OUT/'offline/families.jsonl',[{k:r[k] for k in ('unit_id','group_id','resource_id')} for r in selected])
write(OUT/'offline/input_mapping.jsonl',[dict(request_id=handles[iid],item_id=iid,unit_id=item_units[iid]) for iid in ids])
source_paths=[D/'selected_candidates.jsonl',D/'items.jsonl',D/'evaluation.jsonl',D/'frozen_manifest.json',D/'retrieval.jsonl']
method_paths=[WORK/'cf_moa/agents/a5_robust_readout.py',WORK/'cf_moa/agents/post_proposers.py',WORK/'cf_moa/controller/post_selective.py',WORK/'cf_moa/controller/strong_legacy.py',WORK/'cf_moa/prompts/rule_guided_aggregator.txt',WORK/'cf_moa/evaluation/c0_native.py',Path(r5_module().__file__)]
for method in ['M4','M5']:
 path=D/method.lower()/'inputs.jsonl';source_paths += [path,D/method.lower()/'native_config.json']
 inputs=[];nli=0;lengths=[]
 for row in rows(path):
  iid=row['item']['item_id']
  if iid not in handles:continue
  assert row['original_response'] is None
  item={k:row['item'][k] for k in NATIVE_FIELDS}
  packet=InputPacket(request_id=handles[iid],native_input=item,question=item['question'],original_context=row['messages'],answer_schema=row['schema'],available_tools=['native_readout'],budget=Budget(max_model_requests=24,max_input_tokens=3000000,max_output_tokens=65536,max_tool_calls=4))
  assert select(packet)[0]=='F'
  req=c0_native.request(packet,method)
  inputs.append(dict(packet=asdict(packet),c0_request=req))
  nli+=r5_module().is_nli(item);lengths.append(row['prompt_tokens'])
 assert len(inputs)==112 and nli==8,(method,len(inputs),nli)
 inputs.sort(key=lambda r:r['packet']['request_id'])
 write(OUT/'inference'/f'{method.lower()}.jsonl',inputs)
 source_paths += [Path(r['path']) for r in c0_native.profile(method).source['files']]
# Evaluator data are physically separate and never imported by the live runner.
evaluation=[]
for e in rows(D/'evaluation.jsonl'):
 if e['item_id'] in handles:evaluation.append(dict(e,request_id=handles[e['item_id']]))
write(OUT/'offline/evaluations.jsonl',evaluation)
rt=dict(context=131072,gpu_memory_utilization=.48,blocks=8192,batch_size=4,max_num_seqs=4,max_num_batched_tokens=4096,gpu=3)
dump(OUT/'runtime.json',rt)
dump(OUT/'exposure_review_20261102.json',dict(status='bounded_identity_update_complete',time=now(),candidate_families=128,scanned_files=len(audit),excluded_family_count=len(excluded),excluded_units=sorted(excluded),selected_families=32,selected_overlap=0,limits=['Scan covers enumerated working input manifests, not all human memory or pretraining.','Existing source collection/classification/qualification exposure retained.','Separately exposed eight target-change controls excluded.','BioNLI article-level independence remains unresolved; prior audit is reused.']))
dump(OUT/'preparation.json',dict(status='method_and_panel_frozen_before_outputs',time=now(),families=32,inputs_per_method=112,allocation=allocation,nli_inputs_per_method=8,planned_calls_range=[1392,1808],new_retrieval_calls=0,retrieval_identity='Reuse complete 2026-09-18 saved native MedRAG contexts and retrieval documents.',
 sources={str(p):sha(p) for p in sorted(set(source_paths+method_paths))},inference_hashes={m:sha(OUT/'inference'/f'{m.lower()}.jsonl') for m in ['M4','M5']},runtime_sha256=sha(OUT/'runtime.json'),
 methodology=dict(C0='Exact original messages, sampling and guidance/parser; smaller runtime batch and fixed KV allocation only.',B='Adopted F with original seeds42–46, absolute-three early stop or six NLI callbacks; five-role capability records; other roles explicit C0 fallback.',Gen='Existing post_selective gen, max2048.',RulePrompt='Existing rule_prompt, max256; complete selected native response copied.',selection='Seeded hash by family, fixed source quotas, no outcome filtering.',failure='Keep invalid answers and capacity failures; do not retry semantic failures.'),
 limits=['R5 scope only; cannot confirm A1–A4 or cross-functional generalization.','Previously collected and qualified source families, not new clinical patients or all-blind material.','One frozen run per backbone; no prompt search or performance-driven sample replacement.']))
print(json.dumps(dict(status='prepared',files_scanned=len(audit),excluded=len(excluded),families=32,inputs_per_method=112,evaluations=len(evaluation))))
