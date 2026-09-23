#!/usr/bin/env python3
"""Check the published metadata without needing models, raw patient files, or gold."""
import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path


def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path,nargs='?',default=Path(__file__).parent);ap.add_argument('--source-root',type=Path);ap.add_argument('--write-report',action='store_true',help='Explicitly write validation.json; default is read-only stdout.');args=ap.parse_args();d=args.directory
 def load(n):return json.loads((d/n).read_text())
 fields=['cycle','panel','method','arm','request_id','correct','native_valid','run_status','native_mapping_count','method_score','actual_adjudication','proposal_delivered','modified_answer','repair_attempted','failure_type','warnings','origin','source_file','source_line']
 with (d/'per_input_status.csv').open() as f:
  reader=csv.DictReader(f);assert reader.fieldnames==fields;rows=list(reader)
 groups=defaultdict(list);seen=set()
 for r in rows:
  key=tuple(r[k] for k in ('cycle','panel','method','arm','request_id'));assert key not in seen;seen.add(key);groups[key[:4]].append(r)
  assert r['correct'] in ('True','False','');assert r['native_valid'] in ('True','False','')
  assert r['method_score'] in ('scored','not_scored')
  if r['correct']=='':assert r['method_score']=='not_scored'
  for k in ('method','arm','request_id','run_status','method_score','failure_type','origin'):
   assert len(r[k])<160 and (not r[k] or re.fullmatch(r'[A-Za-z0-9_.:/ -]+',r[k]))
 quality=load('quality_summary.json');assert len(quality['rows'])==len(groups)
 for q in quality['rows']:
  key=tuple(q[k] for k in ('cycle','panel','method','arm'));rs=groups[key];c=Counter(r['correct'] for r in rs)
  assert q['unique_inputs']=={'denominator':len(rs),'correct':c['True'],'incorrect':c['False'],'unavailable':c['']}
  if 'same_scope_B' in q:
   baseline_panel='a1_target34' if key[1]=='a1_direct_verdict_posthoc' else key[1]
   bs=groups[(key[0],baseline_panel,key[2],'F' if key[1].startswith('synthetic') else 'baseline')];bm={r['request_id']:r for r in bs};bc=Counter(bm[r['request_id']]['correct'] for r in rs)
   assert all(q['same_scope_B'][k]==v for k,v in {'denominator':len(rs),'correct':bc['True'],'incorrect':bc['False'],'unavailable':bc['']}.items())
 for cmp in quality['comparisons']:
  key=tuple(cmp[k] for k in ('cycle','panel','method','arm'));rs=groups[key];old={r['request_id']:r for r in groups[(*key[:3],cmp['comparator'])]};counts=Counter()
  for r in rs:
   a=old[r['request_id']]['correct'];b=r['correct']
   if a=='False' and b=='True':counts['repairs']+=1
   if a=='True' and b=='False':counts['harms']+=1
   if a=='' and b!='':counts['unavailable_recoveries']+=1
   if a=='' and b=='True':counts['correct_unavailable_recoveries']+=1
   if a=='True' and b=='':counts['correct_lost_to_unavailable']+=1
   if a=='' and b=='':counts['both_unavailable']+=1
  assert cmp['denominator']==len(rs)
  assert all(counts[k]==v for k,v in cmp['counts'].items())
 pair=load('pair_summary.json')
 for r in pair['rows']:
  assert 0<=r['both_correct']<=r['pairs']
 cost=load('cost_summary.json');total=Counter()
 for c in cost['cycle_new_costs']:
  for k in cost['four_cycle_physical_subtotal']:total[k]+=c['new_physical_cost'][k]
 assert dict(total)==cost['four_cycle_physical_subtotal']
 assert total['new_model_requests']==2203
 forbidden={'native_answer','answer_choice','native_choice','prediction','semantic_prediction','gold','semantic_gold','question','options','patient','prompt','messages','raw_text','raw_response','changed_choice_rows','reason'}
 def inspect(v):
  if isinstance(v,dict):
   assert not forbidden.intersection(v),forbidden.intersection(v)
   for z in v.values():inspect(z)
  elif isinstance(v,list):
   for z in v:inspect(z)
 for name in ('quality_summary.json','pair_summary.json','cost_summary.json','failure_and_limitations.json','source_manifest.json'):inspect(load(name))
 manifest=load('source_manifest.json');checked=0
 if args.source_root:
  for s in manifest['files']:
   b=(args.source_root/s['relative_to_effect_first_root']).read_bytes();assert len(b)==s['bytes'];assert hashlib.sha256(b).hexdigest()==s['sha256'];checked+=1
 outputs={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(d.iterdir()) if p.suffix in ('.csv','.json','.py') and p.name!='validation.json'}
 result={'status':'passed','unique_public_status_rows':len(rows),'quality_groups':len(groups),'pair_summary_groups':len(pair['rows']),'comparisons':len(quality['comparisons']),'source_hashes_checked':checked,'source_hashes_available':len(manifest['files']),'sensitive_fields_in_exports':0,'new_model_calls':0,'new_native_scoring_calls':0,'artifacts':outputs}
 if args.write_report:(d/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))

if __name__=='__main__':main()
