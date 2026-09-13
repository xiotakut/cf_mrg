import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
sys.path.insert(0,str(ROOT.parent/'results_v5_m0_m2_m4_m5/code'))
from common import valid_answer,json_object
from normalize import normalize,candidates,literal
from analyze_v5 import score,norm,PACK
items={r['item_id']:r for l in (ROOT.parent/'results_v5_m0_m2_m4_m5/items.jsonl').open() if (r:=json.loads(l))}
rows=[json.loads(l) for l in (SOURCE/'data/reused_imedrag.jsonl').open()]
dev={json.loads(l)['item']['item_id'] for l in (ROOT/'inputs.jsonl').open()}
assert len(rows)==12 and not dev & {r['item_id'] for r in rows}
canonical={norm(s):s for s in json.loads((PACK/'results_cf_full_test/canonical_labels.json').read_text())['labels']}
labels={r['item_id']:r for l in (ROOT.parent/'results_v5_m0_m2_m4_m5/evaluation.jsonl').open() if (r:=json.loads(l))}
out=[]
for r in rows:
 item=items[r['item_id']]
 try:raw=normalize(r['raw_response'],item);error=valid_answer(raw,item)
 except (ValueError,SyntaxError) as e:raw=r['raw_response'];error=str(e)
 original=candidates(r['raw_response'])[0]['answer']
 if item['answer_format']=='diagnosis':
  try:wrapped=literal(original) if isinstance(original,str) else original
  except (ValueError,SyntaxError,TypeError):wrapped=None
  if isinstance(wrapped,dict) and set(wrapped)=={'diagnosis'}:original=wrapped['diagnosis']
 obj=json_object(raw,'answer')
 assert obj['answer']==original
 original_obj=None
 try:original_obj=json_object(r['raw_response'],'answer')
 except ValueError:pass
 scores={}
 for arm,value,valid in [('original',original_obj,r['status']=='ok'),('literal',obj,error is None)]:
  scores[arm]=score({'raw_response':json.dumps({'answer':value['answer']}) if value and valid else ''},labels[r['item_id']],dict(item,answer_format='single') if item['answer_format']=='robustness_single' else item,canonical)
 out.append(dict(item_id=r['item_id'],answer_format=item['answer_format'],original=r,normalized=raw,error=error,answer_value_preserved=True,scores=scores))
summary=dict(N=12,disjoint_from_development=True,original_protocol_valid=sum(r['original']['status']=='ok' for r in out),literal_protocol_valid=sum(r['error'] is None for r in out),original_native_valid=sum(not r['scores']['original']['invalid'] for r in out),literal_native_valid=sum(not r['scores']['literal']['invalid'] for r in out),answer_values_preserved=12,formats=sorted({r['answer_format'] for r in out}))
(ROOT/'holdout_validation.json').write_text(json.dumps(summary,indent=2)+'\n')
(ROOT/'holdout.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in out))
print(json.dumps(summary))
