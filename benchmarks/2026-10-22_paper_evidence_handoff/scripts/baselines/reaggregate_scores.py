#!/usr/bin/env python3
"""Recompute the 42 saved-score category means using only delivered artifacts.
HANDOFF_ONLY=1 forbids original server reads. Does not import or run a scorer.
"""
import csv,json,sys,os
from pathlib import Path
from collections import defaultdict
from statistics import mean
H=Path(__file__).resolve().parents[2];sys.path.insert(0,str(H/'scripts'));from evidence_io import open_text
entries=json.loads((H/'audit/baselines/tables.json').read_text());result=[];cache={}
for e in entries:
 path=e['score_paths'][0]
 if path not in cache:
  with open_text(path) as f:cache[path]=[json.loads(l) for l in f if l.strip()]
 m=e['row_or_cell'].split()[0];method={'M6':'medgenie','M7':'tcrag'}.get(m,m);cat=e['sample_scope'];b=defaultdict(list)
 for r in cache[path]:
  if r['method']!=method or r['role']=='reference':continue
  if cat!='ALL' and cat not in r['evaluation_labels']:continue
  b[r['unit_id']].append(int(r['correct']))
 value=100*mean(mean(x) for x in b.values());old=e['value_full_precision_existing'];ok=len(b)==e['denominator'] and abs(value-old)<1e-10
 result.append({'method':m,'category':cat,'units':len(b),'saved_table_pct':old,'recomputed_pct':value,'match':ok})
assert all(r['match'] for r in result),result
out=Path(sys.argv[1]) if len(sys.argv)>1 else H/'audit/baselines/portable_reaggregation.json'
out.write_text(json.dumps({'HANDOFF_ONLY':os.environ.get('HANDOFF_ONLY','0'),'cells':len(result),'all_match':True,'rule':'saved correct; exclude reference; average within unit then equal weight over units; overlapping evaluation_labels; no scorer','rows':result},ensure_ascii=False,indent=2)+'\n')
print('Verified',len(result),'saved-score cells; all match; output',out)
