import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,'/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced/code')
from normalize import candidates,literal,test
from common import valid_answer

test()
inputs={r['item']['item_id']:r for l in (ROOT/'inputs.jsonl').open() if (r:=json.loads(l))}
outputs=[json.loads(l) for l in (ROOT/'literal.jsonl').open()]
assert len(outputs)==len({r['item_id'] for r in outputs})==len(inputs)==40
receipts=[]
for row in outputs:
 old=inputs[row['item_id']];source=candidates(old['original']['raw_response']);assert source
 new=json.loads(row['result']['text']);answer=source[0]['answer'];unwrapped=False
 if old['item']['answer_format']=='diagnosis':
  try:wrapped=literal(answer) if isinstance(answer,str) else answer
  except (ValueError,SyntaxError,TypeError):wrapped=None
  if isinstance(wrapped,dict) and set(wrapped)=={'diagnosis'}:
   answer=wrapped['diagnosis'];unwrapped=True
 assert answer==new['answer'],row['item_id']
 if 'errors' in source[0]:assert source[0]['errors']==new['errors']
 assert valid_answer(row['result']['text'],old['item']) is None
 receipts.append(dict(item_id=row['item_id'],answer_value_preserved=True,diagnosis_wrapper_removed=unwrapped,errors_moved_from_explicit_section='errors' in new and 'errors' not in source[0]))
(ROOT/'literal_validation.json').write_text(json.dumps(dict(status='passed',N=40,protocol_valid=40,answer_values_preserved_after_explicit_wrapper_removal=40,receipts=receipts),indent=2)+'\n')
print('40/40 values preserved after explicit wrapper removal; original errors fields unchanged; protocol valid.')
