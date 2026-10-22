import json
from prepare import OUT,read
from run_m3 import task_prompts
plan=json.loads((OUT/'plan.json').read_text());items={r['item_id']:r for r in read(OUT/'items.jsonl')}
for iid in plan['smoke_item_ids']:
    root=OUT/'cache/items'/iid
    result=json.loads((root/'result.json').read_text())
    system,templates,q,o=task_prompts(items[iid])
    prompt=json.loads((root/'round_1.prompt.json').read_text())
    assert prompt['messages']==[dict(role='system',content=system),dict(role='user',content=templates['user_prompt'].render(question=q,options=o))]
    assert result['rounds_used'] in range(1,5)
    for p in root.glob('*.prompt.json'):
        r=json.loads(p.read_text());assert r['prompt_tokens']+(8192 if r['thinking'] else 2048)<=131072
    if items[iid]['answer_format']=='robustness_single':
        assert 'errors' in json.loads(result['raw_response'])
        assert 'D-numbered' in q
(OUT/'smoke_audit.json').write_text(json.dumps(dict(status='passed',items=len(plan['smoke_item_ids'])))+'\n')
print('Smoke protocol audit passed')
