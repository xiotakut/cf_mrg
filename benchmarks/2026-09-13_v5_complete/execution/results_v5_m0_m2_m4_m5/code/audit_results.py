"""Audit complete coverage, per-stage sampling, raw prompts, and actual token costs."""
from collections import Counter
import gzip,json
from prepare_v5 import OUT,read,dump

def main():
    items={r['item_id']:r for r in read(OUT/'items.jsonl')}
    pending={r['item_id'] for r in read(OUT/'pending_M2.jsonl')}
    costs={};stage_counts={};max_prompt={}
    root=OUT/'m2_runtime/cache/main/worker-0'
    stages=['summary','explore','generate','select','M2']
    cfg=json.loads((OUT/'m2_runtime/config.json').read_text())
    for stage in ['retrieval',*stages,'rerank']:
        rs=read(root/(stage+'.jsonl'));keys=[r['key'] for r in rs]
        wanted={f'{iid}::{slot}' for iid in pending for slot in range(5)} if stage in ['summary','generate'] else pending
        assert len(keys)==len(set(keys)) and set(keys)==wanted,(stage,len(keys),len(wanted))
        stage_counts[stage]=len(rs)
        if stage in stages:
            for r in rs:
                iid=r['item_id'];slot=int(r['key'].split('::')[1]) if '::' in r['key'] else 0
                index=['summary','explore','generate','select','M0','M1','M2'].index(stage)
                seed=(cfg['seed']+int(iid[1:])*101+index*11+slot)%(2**31-1)
                expected=dict(cfg['reader' if stage=='M2' else stage],seed=seed)
                if stage=='M2':expected['max_tokens']=items[iid].get('max_tokens',64)
                assert r['sampling']==expected
                assert r['prompt_tokens']+expected['max_tokens']<=98304
            costs[stage]=dict(calls=len(rs),prompt_tokens=sum(r['prompt_tokens'] for r in rs),completion_tokens=sum(r['completion_tokens'] for r in rs))
            max_prompt[stage]=max(r['prompt_tokens'] for r in rs)
    found=[]
    with gzip.open(root/'prompts.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);found.append((r['key'],r['stage']))
    expected={(r['key'],s) for s in stages for r in read(root/(s+'.jsonl'))}
    assert len(found)==len(set(found)) and set(found)==expected
    for method in ['M0','M2','M4','M5']:
        rs=read(OUT/method/'predictions.jsonl');assert (OUT/method/'complete.json').exists()
        costs[method+'_final']=dict(calls=len(rs),prompt_tokens=sum(r['prompt_tokens'] for r in rs),completion_tokens=sum(r['completion_tokens'] for r in rs))
        keys=[r['item_id'] for r in rs];assert len(keys)==len(set(keys))
        assert all(r['completion_tokens']<=r['sampling']['max_tokens'] for r in rs)
        if method in ['M4','M5']:
            assert set(keys)==set(items)
            config=json.loads((OUT/method/'config.json').read_text());assert config['seed']==42
        if method!='M2':
            with gzip.open(OUT/method/'prompts.jsonl.gz','rt') as f:prompt_keys=[json.loads(l)['item_id'] for l in f]
            assert len(prompt_keys)==len(set(prompt_keys)) and set(prompt_keys)==set(keys)
    excluded={'method_id','method','model_id','model_path','chat_template_kwargs','rope_scaling','context_extension_reason'}
    c4=json.loads((OUT/'M4/config.json').read_text());c5=json.loads((OUT/'M5/config.json').read_text())
    assert {k:v for k,v in c4.items() if k not in excluded}=={k:v for k,v in c5.items() if k not in excluded}
    assert c4['retriever_name']=='BM25+MedCPT' and c4['corpus_name']=='MedCorp' and c4['k']==8
    validation=json.loads((OUT/'validation.json').read_text());assert validation['status']=='complete'
    dump(OUT/'artifact_audit.json',dict(status='passed',m2_stage_counts=stage_counts,costs=costs,m2_max_prompt_tokens=max_prompt,duplicate_stage_keys=0,missing_prompt_records=0,old_results_preserved=True))
    print('Complete coverage, stage seeds/budgets and raw prompts: passed.')
if __name__=='__main__':main()
