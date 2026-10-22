#!/usr/bin/env python3
"""Only saved membership and judgment counts. No scoring."""
import os,json,collections
from pathlib import Path
os.environ['HANDOFF_ONLY']='1'
from evidence_io import open_text
P='/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v5_20260910/'
counts=collections.defaultdict(collections.Counter);ids=set();targets=set();r123=set()
with open_text(P+'units.jsonl') as f:
 for line in f:
  r=json.loads(line);ids.add(r['unit_id']);counts[r['resource_id']]['Units']+=1
  for c in r['evaluation_labels']:counts[r['resource_id']][c]+=1
  if set(r['evaluation_labels'])&{'R1','R2','R3'}:r123.add(r['unit_id'])
with open_text(P+'selected_targets.jsonl.gz') as f:
 for line in f:
  r=json.loads(line);counts[r['resource_id']]['Judgments']+=1;targets.add(r['judgment_id'])
counts['Total']=sum(counts.values(),collections.Counter())
expected=json.loads((Path(__file__).resolve().parents[1]/'audit/data/recomputed_counts.json').read_text())
result={'counts':counts,'units':len(ids),'judgments':len(targets),'R123_union':len(r123),'matches_saved_reaggregation':dict(counts)==expected['counts'],'new_scores':0,'new_model_calls':0}
print(json.dumps(result,ensure_ascii=False,indent=2));assert result['matches_saved_reaggregation']
