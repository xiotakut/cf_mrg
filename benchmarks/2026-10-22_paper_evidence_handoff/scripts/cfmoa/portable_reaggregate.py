#!/usr/bin/env python3
"""Recompute paper aggregates from delivered saved scores (zero scoring).
Run with Python + numpy. All original paths resolve through FILE_MANIFEST.csv via
scripts/evidence_io.py; the original server and model environment are not needed.
"""
import argparse,collections,hashlib,importlib.util,json,math,sys
from pathlib import Path
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--handoff',type=Path,default=Path(__file__).resolve().parents[2]);P.add_argument('--out',type=Path,required=True);a=P.parse_args();sys.path.insert(0,str(a.handoff/'scripts'))
from evidence_io import open_text
spec=importlib.util.spec_from_file_location('saved_aggregate',Path(__file__).with_name('summarize_existing_results.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
base='/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924'
def rows(p):
 with open_text(p) as f:return [json.loads(l) for l in f if l.strip()]
def load(p):
 with open_text(p) as f:return json.load(f)
a.out.mkdir(parents=True,exist_ok=True);checks=[];summary=[];intervals=[]
for model in ['m4','m5']:
 r=f'{base}/full_v5/analysis/{model}';units=rows(r+'/native_units.jsonl');pairs=rows(r+'/pairs.jsonl');inputs=rows(r+'/per_input_status.jsonl');old=load(r+'/quality_summary.json');categories=mod.aggregate_units(units,('method','arm','category'))
 lookup={(x['arm'],x['category']):x for x in categories}
 for x in old['reports']:
  for z in x['native_categories']:
   y=lookup[x['arm'],z['category']];checks.append({'model':model,'arm':x['arm'],'metric':z['category'],'matches':y['units']==z['units'] and abs(y['mean_native_unit_score']-z['mean_native_unit_score'])<1e-10})
  for z in x['pairs']:
   ys=[y for y in pairs if y['arm']==x['arm'] and y['relation']==z['relation']];checks.append({'model':model,'arm':x['arm'],'metric':z['relation'],'matches':len(ys)==z['pairs'] and sum(y['both_correct'] is True for y in ys)==z['both_correct']})
 for metric,data in [('native_ALL',units),('maintain',pairs),('respond',pairs)]:
  intervals.extend(dict(method=model.upper(),metric=metric,**x) for x in mod.paired_family_bootstrap(mod.build_atoms(data,metric),5000,240924))
 summary.append({'model':model,'categories':categories,'sources':mod.aggregate_units([x for x in units if x['category']=='ALL'],('method','arm','source')),'input_counts':dict(collections.Counter(x['arm'] for x in inputs))})
old=load(base+'/closeout_20260928/family_effect_intervals.json')
for x,y in zip(old,intervals):
 keys=['method','metric','candidate','baseline'];assert all(x[k]==y[k] for k in keys)
 checks.append({'model':x['method'],'arm':x['candidate'],'metric':x['metric']+'/interval','matches':abs(x['delta_pp']-y['delta_pp'])<1e-10 and max(abs(u-v) for u,v in zip(x['percentile_95_pp'],y['percentile_95_pp']))<1e-10})
op=rows(base+'/operation_ablations/per_input_status.jsonl');opout=[]
for x in load(base+'/closeout_20260928/operation_ablations_reused.json'):
 ys=[z for z in op if z['method']==x['method'] and z['arm']==x['arm']];correct=sum(z['correct'] is True for z in ys);unavailable=sum(not z['native_available'] for z in ys)
 checks.append({'model':x['method'],'arm':x['arm'],'metric':'operation123','matches':len(ys)==123 and correct==x['correct'] and unavailable==x['unavailable']});opout.append({'method':x['method'],'arm':x['arm'],'correct':correct,'unavailable':unavailable,'n':len(ys)})
cost=collections.defaultdict(list)
for x in rows(base+'/closeout_20260928/costs/per_input_cost_coverage.jsonl.gz'):cost[x['method'],x['arm']].append(x)
for x in load(base+'/closeout_20260928/costs/per_method_costs.json')['rows']:
 for field,old in x['cost']['method_attributed_cost'].items():
  vals=[y.get('method_attributed_cost',{}).get(field) for y in cost[x['method'],x['arm']]];known=[v for v in vals if v is not None];value=math.fsum(known)
  checks.append({'model':x['method'],'arm':x['arm'],'metric':'cost/'+field,'matches':len(vals)-len(known)==old['unknown_rows'] and abs(value-old['known_subtotal'])<max(1e-6,abs(value)*1e-12)})
for name,value in [('summary.json',summary),('intervals.json',intervals),('operation123.json',opout),('validation.json',{'checks':checks,'all_passed':all(x['matches'] for x in checks),'new_model_calls':0,'new_scores':0,'bootstrap_draws':5000,'seed':240924})]:
 (a.out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print('checks',len(checks),'all_passed',all(x['matches'] for x in checks),'new_model_calls=0 new_scores=0')
