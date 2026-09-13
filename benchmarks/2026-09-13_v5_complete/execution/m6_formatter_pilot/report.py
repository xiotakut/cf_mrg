import collections,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
from common import valid_answer,json_object
sys.path.insert(0,str(ROOT.parent/'results_v5_m0_m2_m4_m5/code'))
from analyze_v5 import score,norm,PACK
inputs=[json.loads(l) for l in (ROOT/'inputs.jsonl').open()];items={r['item']['item_id']:r for r in inputs}
canonical={norm(s):s for s in json.loads((PACK/'results_cf_full_test/canonical_labels.json').read_text())['labels']}
labels={}
for l in (ROOT.parent/'results_v5_m0_m2_m4_m5/evaluation.jsonl').open():
 r=json.loads(l)
 if r['item_id'] in items:labels[r['item_id']]=r
summary={};details=[]
for arm in ('original','prompt','structured','literal'):
 rows=[dict(item_id=r['item']['item_id'],raw=r['original']['raw_response'],runtime_valid=r['original']['status']=='ok',error=r['original'].get('answer_error')) for r in inputs] if arm=='original' else [dict(item_id=r['item_id'],raw=r['result']['text'],runtime_valid=r['error'] is None,error=r['error']) for l in (ROOT/(arm+'.jsonl')).open() if (r:=json.loads(l))] if (ROOT/(arm+'.jsonl')).exists() else []
 stats=collections.Counter();changed=[]
 for r in rows:
  iid=r['item_id'];item=items[iid]['item'];obj=None
  try:obj=json_object(r['raw'],'answer');stats['json_object_valid']+=1
  except ValueError:pass
  native={'raw_response':json.dumps({'answer':obj['answer']}) if obj and r['runtime_valid'] else ''}
  result=score(native,labels[iid],dict(item,answer_format='single') if item['answer_format']=='robustness_single' else item,canonical)
  stats['N']+=1;stats['runtime_valid']+=r['runtime_valid'];stats['native_valid']+=not result['invalid'];stats['correct']+=result['correct'];stats['reason_'+str(r['error'])]+=1
  if arm!='original' and items[iid]['original']['status']=='ok' and obj:
   old=json_object(items[iid]['original']['raw_response'],'answer')['answer']
   if old!=obj['answer']:changed.append(dict(item_id=iid,answer_format=item['answer_format'],old=old,new=obj['answer']))
  details.append(dict(arm=arm,item_id=iid,answer_format=item['answer_format'],runtime_valid=r['runtime_valid'],error=r['error'],**result))
 summary[arm]=dict(stats,changed_answer_values_among_original_ok=changed)
report=dict(N_frozen=len(items),formats=dict(collections.Counter(r['item']['answer_format'] for r in inputs)),summary=summary,limitations='Frozen early formal completions; 4 formats, no multi-choice-set inputs. Historical baseline; changed prompt and batching. Runtime validity includes errors validation. Answer value comparison is not full semantic equivalence.')
(ROOT/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'scored.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in details))
print(json.dumps(report,ensure_ascii=False,indent=2))
