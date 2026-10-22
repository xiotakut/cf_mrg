#!/usr/bin/env python3
"""Replay handoff table sums using persisted flags only, via FILE_MANIFEST; stdlib only.
Run from any directory: python3 /path/to/handoff/scripts/heads/reaggregate_packaged.py
No source-server files, model packages, GPUs, parsers, or graders are accessed.
"""
from pathlib import Path
import sys,json,functools,os
HANDOFF=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HANDOFF/'scripts'))
os.environ['HANDOFF_ONLY']='1'
from evidence_io import open_text
@functools.lru_cache(maxsize=None)
def read(original):
 with open_text(original) as stream:return [json.loads(line) for line in stream if line.strip()]
tables=json.loads((HANDOFF/'audit/heads/tables.json').read_text());out=[]
for t in tables:
 if t['value_recomputed'] is None:
  out.append({'cell':t['row_or_cell'],'status':'summary_only_not_rescored'});continue
 rs=[r for p in t['score_paths'] for r in read(p)]
 m=t['system'];table=t['table_claim_id'];metric=t['metric']
 if table=='tab:seven-heads':
  _,category,mode=t['row_or_cell'].split('/')
  if category=='R2':
   rs=read(t['score_paths'][0] if mode=='head' else t['score_paths'][1]);rs=[r for r in rs if r['method']==m and r['policy']==('inherit_unknown' if mode=='head' else 'baseline')];metric='correct'
  else:rs=[r for r in rs if r['method']==m]
 elif table=='tab:head-controls(a)':rs=[r for r in rs if r['method']==m and r['variant']==t['arm']]
 elif table=='tab:head-controls(b)':
  rs=[r for r in rs if r['method']==m and r['policy']==t['arm']]
  if t['row_or_cell'].endswith('/remaining'):rs=[r for r in rs if r['resource_id']=='M02' and r['semantic_gold']!=['none of the above']]
 elif table=='tab:historical_model':rs=[r for r in rs if r['method']==m and r['arm']==t['arm']]
 elif table=='appendix:source-checks':
  if t['dataset']=='ASCENT47':rs=[r for r in rs if r['method']==m and r['variant']==t['arm']]
  else:rs=[r for r in rs if ('llama' if m=='M4' else 'qwen') in r['model'].lower() and r['variant']==t['arm']]
 else:raise ValueError(table)
 val=sum(int(r[metric]) for r in rs);passed=val==t['value_recomputed'] and len(rs)==int(t['denominator'])
 out.append({'table':table,'cell':t['row_or_cell'],'n':len(rs),'value':val,'expected':t['value_recomputed'],'status':'pass' if passed else 'FAIL'})
report={'saved_score_cells_checked':sum(r['status']=='pass' for r in out),'summary_only':sum(r['status']=='summary_only_not_rescored' for r in out),'failures':[r for r in out if r['status']=='FAIL'],'rows':out,'new_model_calls':0,'new_scores':0}
print(json.dumps(report,ensure_ascii=False,indent=2))
if report['failures']:sys.exit(1)
