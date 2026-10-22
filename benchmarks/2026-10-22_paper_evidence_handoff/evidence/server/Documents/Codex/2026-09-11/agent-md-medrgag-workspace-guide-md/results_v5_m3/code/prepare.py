"""Reuse exact visible M3 inputs and freeze a disjoint v5 continuation."""
import json,shutil,sys
from pathlib import Path
from collections import Counter
from datetime import datetime
OUT=Path(__file__).resolve().parents[1]
V5=OUT.parent/'results_v5_m0_m2_m4_m5'
OLD=Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack/results_r1_r5_v3_m3_20260909')
def read(p):return [json.loads(x) for x in p.open() if x.strip()]
def write(p,rows):
    with p.open('w') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def key(r):return json.dumps([r['question'],list(r['options'].items()),r['fixed_evidence'],r['answer_format'],r.get('max_tokens',64)],ensure_ascii=False)
def main():
    assert not (OUT/'plan.json').exists()
    from run_m3 import task_prompts,self_check
    from transformers import AutoTokenizer
    self_check()
    for name in ['items.jsonl','evaluation.jsonl','units.jsonl']:shutil.copy2(V5/name,OUT/name)
    items=read(OUT/'items.jsonl');olditems={r['item_id']:r for r in read(OLD/'items.jsonl')}
    oldpreds={r['item_id']:r for r in read(OLD/'m3_predictions.jsonl')}
    reusable={key(r):oldpreds[iid] for iid,r in olditems.items() if iid in oldpreds}
    reused=[];pending=[]
    for item in items:
        pred=reusable.get(key(item))
        if pred is None:pending.append(item);continue
        assert (OLD/pred['raw_candidates']/'result.json').exists()
        reused.append(dict(pred,item_id=item['item_id'],original_item_id=pred['item_id'],reused_from=str(OLD/'m3_predictions.jsonl')))
    write(OUT/'cache/reused.jsonl',reused);write(OUT/'pending_M3.jsonl',pending)
    tokenizer=AutoTokenizer.from_pretrained('/home/data3/txy/models/Qwen3-8B',local_files_only=True)
    lengths=[]
    for item in items:
        system,templates,question,options=task_prompts(item)
        prompt=templates['user_prompt'].render(question=question,options=options)
        rendered=tokenizer.apply_chat_template([dict(role='system',content=system),dict(role='user',content=prompt)],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        lengths.append(dict(item_id=item['item_id'],prompt_tokens=len(tokenizer.encode(rendered,add_special_tokens=False))))
    assert max(r['prompt_tokens'] for r in lengths)+2048<=131072
    write(OUT/'input_lengths.jsonl',lengths)
    lengthmap={r['item_id']:r['prompt_tokens'] for r in lengths}
    ordered=sorted(pending,key=lambda r:(lengthmap[r['item_id']],r['item_id']))
    shardids=[[r['item_id'] for r in ordered[i::8]] for i in range(8)]
    assert len(set(sum(shardids,[])))==len(pending)
    smoke={next(r['item_id'] for r in ordered if r['answer_format']==fmt) for fmt in {r['answer_format'] for r in ordered}}
    smoke.add(max(ordered,key=lambda r:lengthmap[r['item_id']])['item_id'])
    plan=dict(status='frozen',frozen_at=datetime.now().astimezone().isoformat(),unique_inputs=len(items),reused_M3_predictions=len(reused),pending=len(pending),shards=shardids,gpus=[1,2],smoke_item_ids=sorted(smoke),answer_formats=dict(Counter(r['answer_format'] for r in pending)),reuse_rule='exact question, ordered options, fixed evidence, answer format and output budget; completed invalid outputs retained',robustness_io='native answer tag voting; errors from first final candidate with winning answer; no correction voting or gold access')
    (OUT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in plan.items() if k!='shards'},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
