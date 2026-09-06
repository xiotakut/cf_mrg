#!/usr/bin/env python3
"""Three independent all-Llama baselines; one resident model, bounded stages."""
from __future__ import annotations
import argparse
from collections import defaultdict, Counter
from dataclasses import replace
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from prepare_cf_baseline_screening import ROOT, OUT, read, write
sys.path.insert(0,str(OUT/'runtime'))
import run_gate_b as base

sys.path.insert(0,str(base.MEDRGAG))
from src.medrgag_logic import (build_summary_prompt, build_explore_prompt,
    build_generation_slots, build_selection_prompt, clean_generated_text, parse_knowledge_points)
from src.medrgag_prompts import get_prompt_profile

CONFIG=ROOT/'configs/cf_baseline_screening.json'
METHODS={'M0':'direct_llama','M1':'retrieval_only_llama','M2':'medrgag_llama_base'}
VISIBLE={'item_id','question','options','fixed_evidence','answer_format'}

def solver_input(row):
    return {k:row[k] for k in VISIBLE}

def task_question(item):
    q=item['question']
    if item['fixed_evidence']:
        q+='\n\nEvidence supplied with the question:\n'+'\n\n'.join(item['fixed_evidence'])
    return q

def task_profile(item):
    profile=get_prompt_profile('released-code-intent')
    if item['options']:return profile
    def adapt(text):
        return text.replace('multiple-choice question','medical question').replace('evaluating any of the answer options','evaluating possible answers').replace('guesses about which option is correct','guesses about the correct answer').replace('phrases like “the answer is A”','phrases that directly state the answer')
    return replace(profile,summary_prompt=adapt(profile.summary_prompt),generation_prompt=adapt(profile.generation_prompt),question_only_generation_prompt=adapt(profile.question_only_generation_prompt))

def chat(tokenizer,user,system='You are a helpful assistant.'):
    return tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)

def reader_prompt(tokenizer,item,documents):
    fmt=item['answer_format'];q='Question:\n'+task_question(item)
    if item['options']:
        q+='\n\nOptions:\n'+'\n'.join(f'{k}: {v}' for k,v in item['options'].items())
    contract={'single':'The answer must be exactly one option key string, e.g. {"answer":"A"}.',
              'multi':'The answer must be a JSON array of one or more option keys, e.g. {"answer":["A","B"]}.',
              'diagnosis':'Give exactly one most likely diagnosis for this patient. The answer must be only a concise diagnosis label, never a sentence or explanation, e.g. {"answer":"Pneumonia"}.',
              'relation':'The answer must be exactly "higher", "lower", "no difference", or "uncertainty", e.g. {"answer":"higher"}.'}[fmt]
    q+='\n\n'+contract
    if documents:
        q+='\n\nEvidence:\n'+'\n'.join(f"Document [{i}]: {d['contents']}" for i,d in enumerate(documents))
    system=base.SYSTEM if item['options'] else 'Answer the medical benchmark item using only the presented item and evidence. Return JSON only, with exactly one field named answer.'
    return chat(tokenizer,q,system)

def stable_seed(seed,item_id,stage,slot,*,repeat_stream=False):
    # Opaque sequential IDs allocated before inference, independent of role or batching.
    stages=['summary','explore','generate','select','M0','M1','M2']
    return (seed+int(item_id[1:])*101+stages.index(stage)*11+slot+(1_000_000_000 if repeat_stream else 0)) % (2**31-1)

class Runner:
    def __init__(self,args):
        self.args=args;self.config=json.loads(CONFIG.read_text());self.started=time.time()
        self.root=OUT/'cache'/('repeat_independent' if args.mode=='repeat' else 'main')/f'worker-{args.shard_index}'
        self.root.mkdir(parents=True,exist_ok=True)
        frozen=self.root/'config.json'
        if frozen.exists():assert json.loads(frozen.read_text())==self.config,'incompatible resume configuration'
        else:frozen.write_text(json.dumps(self.config,indent=2))
        # One digest guards reuse of expensive inference, not a row-level registry.
        digest=hashlib.sha256((OUT/'screening_items.jsonl').read_bytes()).hexdigest()
        stamp=self.root/'inputs.sha256'
        if stamp.exists():assert stamp.read_text()==digest,'prepared inputs changed; cannot reuse answers'
        else:stamp.write_text(digest)
        self.cached={};self.hits=Counter()
        for worker in sorted(self.root.parent.glob('worker-*')):
            if (worker/'config.json').exists():assert json.loads((worker/'config.json').read_text())==self.config
            for f in worker.glob('*.jsonl'):
                self.cached.setdefault(f.stem,{}).update({r['key']:r for r in read(f)})
        self.backend=None;self.retriever=None

    def append(self,stage,rows):
        base.append_rows(self.root/(stage+'.jsonl'),rows)
        self.cached.setdefault(stage,{}).update({r['key']:r for r in rows})

    def llm(self,stage,entries):
        cache=self.cached.setdefault(stage,{})
        pending=[e for e in entries if e['key'] not in cache]
        self.hits[stage]+=len(entries)-len(pending)
        if not pending:return cache
        if self.backend is None:
            self.backend=base.VLLMBackend(Path(self.config['model']),self.config['max_model_len'],self.args.gpu_memory)
            (self.root/'chat_template.txt').write_text(self.backend.tokenizer.chat_template)
        from vllm import SamplingParams
        cfg=self.config['reader' if stage in METHODS else stage]
        for start in range(0,len(pending),self.args.batch_size):
            batch=pending[start:start+self.args.batch_size]
            prompts=[e['prompt'] for e in batch]
            for e in batch:
                n=len(self.backend.tokenizer.encode(e['prompt'],add_special_tokens=False))
                if n+cfg['max_tokens']>self.config['max_model_len']:
                    raise ValueError(f"overflow: {stage} {e['key']} {n} + {cfg['max_tokens']}")
            params=[SamplingParams(**cfg,seed=stable_seed(self.config['seed']+(1 if self.args.mode=='repeat' else 0),e['item_id'],stage,e.get('slot',0),repeat_stream=self.args.mode=='repeat')) for e in batch]
            t=time.time();outputs=self.backend.model.generate(prompts,params,use_tqdm=False);elapsed=time.time()-t
            rows=[]
            for e,p,o in zip(batch,params,outputs):
                result=o.outputs[0];metrics=o.metrics
                row={'key':e['key'],'item_id':e['item_id'],'stage':stage,'raw_response':result.text,'prompt_tokens':len(o.prompt_token_ids),'completion_tokens':len(result.token_ids),'finish_reason':result.finish_reason,'sampling':cfg|{'seed':p.seed},'batch_size':len(batch),'batch_wall_seconds':elapsed,'request_metrics':{k:getattr(metrics,k,None) for k in ['arrival_time','first_scheduled_time','first_token_time','finished_time','time_in_queue']} if metrics else {},'prompt_ref':str((self.root/'prompts.jsonl.gz').relative_to(OUT))+':'+e['key']+':'+stage,'time':time.time()}
                if stage in METHODS:row.update(method=METHODS[stage],answer=base.parse_answer(result.text))
                rows.append(row)
            with gzip.open(self.root/'prompts.jsonl.gz','at') as f:
                for e in batch:f.write(json.dumps({'key':e['key'],'stage':stage,'prompt':e['prompt']},ensure_ascii=False)+'\n')
            self.append(stage,rows)
            print(json.dumps({'stage':stage,'batch':len(batch),'seconds':round(elapsed,2),'completion_tokens':sum(r['completion_tokens'] for r in rows),'completed_stage':len(cache)}),flush=True)
        return cache

    def retrieve(self,items):
        cache=self.cached.setdefault('retrieval',{})
        # Consume completed retrieval from the concurrent small MedCPT worker.
        for f in self.root.parent.glob('worker-*/retrieval.jsonl'):
            if f.parent==self.root:continue
            with f.open() as stream:
                for line in stream:
                    try:r=json.loads(line)
                    except json.JSONDecodeError:break  # concurrent writer's unfinished last line
                    cache[r['key']]=r
        for item in items:
            key=item['item_id']
            if key in cache:self.hits['retrieval']+=1;continue
            if self.retriever is None:self.retriever=base.LocalRetriever()
            t=time.time()
            # Standard query stays question+all native options, as in the local base.
            docs=self.retriever.retrieve(base.retrieval_query(item),5)
            self.append('retrieval',[{'key':key,'item_id':key,'documents':docs,'wall_seconds':time.time()-t,'policy':'source_balanced_external'}])
        return {i['item_id']:cache[i['item_id']]['documents'] for i in items}

    def run_chunk(self,items):
        required=['M2'] if self.args.mode=='repeat' else ['M0','M1','M2']
        if all(i['item_id'] in self.cached.get(m,{}) for i in items for m in required):
            self.hits['complete_input_tasks']+=len(items)
            return
        if self.backend is None:
            # Retrieve before reserving vLLM memory and retain the small ranker.
            retrieval=self.retrieve(items)
            self.backend=base.VLLMBackend(Path(self.config['model']),self.config['max_model_len'],self.args.gpu_memory)
            (self.root/'chat_template.txt').write_text(self.backend.tokenizer.chat_template)
        else:retrieval=self.retrieve(items)
        tok=self.backend.tokenizer
        adapted={i['item_id']:{'question':task_question(i),'options':i['options']} for i in items}
        def entry(i,p,slot=None):
            return {'key':i['item_id']+(f'::{slot}' if slot is not None else ''),'item_id':i['item_id'],'slot':slot or 0,'prompt':p}
        for method in ([] if self.args.mode=='repeat' else ['M0','M1']):
            self.llm(method,[entry(i,reader_prompt(tok,i,[] if method=='M0' else retrieval[i['item_id']])) for i in items])
        summaries=self.llm('summary',[entry(i,chat(tok,build_summary_prompt(task_profile(i),adapted[i['item_id']],d['contents'])),j) for i in items for j,d in enumerate(retrieval[i['item_id']])])
        es=[]
        for i in items:
            ss=[summaries[f"{i['item_id']}::{j}"]['raw_response'] for j in range(5)]
            prompt,_=build_explore_prompt(task_profile(i),adapted[i['item_id']],ss,3)
            es.append(entry(i,chat(tok,prompt)))
        explores=self.llm('explore',es);gs=[]
        for i in items:
            points,warnings=parse_knowledge_points(explores[i['item_id']]['raw_response'],3)
            points+=['None']*(3-len(points))
            for slot in build_generation_slots(task_profile(i),adapted[i['item_id']],points):gs.append(entry(i,chat(tok,slot['prompt']),slot['slot']))
        generated=self.llm('generate',gs);candidates={};ss=[]
        for i in items:
            docs=retrieval[i['item_id']]+[{'id':f"{i['item_id']}:generated-{j}",'source':'generated','contents':clean_generated_text(generated[f"{i['item_id']}::{j}"]['raw_response'])} for j in range(5)]
            candidates[i['item_id']]=docs
            prompt,_=build_selection_prompt(task_profile(i),adapted[i['item_id']],docs)
            # Original KADS repeats the question twice. Task evidence needs one full
            # copy, otherwise long published articles alone exceed the context.
            if i['fixed_evidence']:
                prompt=prompt.replace(task_question(i),i['question'],1)
            ss.append(entry(i,chat(tok,prompt)))
        selected=self.llm('select',ss);reranked=self.cached.setdefault('rerank',{})
        for i in items:
            key=i['item_id']
            if key in reranked:self.hits['rerank']+=1;continue
            ids=base.selection_ids(selected[key]['raw_response'])
            docs=[candidates[key][j] for j in ids if 0<=j<10][:5]
            if self.retriever is None:self.retriever=base.LocalRetriever()
            t=time.time();ranked=self.retriever.ranker.rank(base.retrieval_query(i),docs)[:5]
            self.append('rerank',[{'key':key,'item_id':key,'selected_ids':ids,'documents':ranked,'wall_seconds':time.time()-t,'selection_invalid':len(ids)!=5}])
        self.llm('M2',[entry(i,reader_prompt(tok,i,reranked[i['item_id']]['documents'])) for i in items])
        (self.root/'runtime.json').write_text(json.dumps({'started':self.started,'updated':time.time(),'elapsed_seconds':time.time()-self.started,'cache_hits':dict(self.hits),'batch_size':self.args.batch_size,'gpu_memory_utilization':self.args.gpu_memory,'cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'completed_available_in_cache':len(self.cached.get('M2',{}))},indent=2))

def preflight():
    from transformers import AutoTokenizer
    cfg=json.loads(CONFIG.read_text());tok=AutoTokenizer.from_pretrained(cfg['model'],local_files_only=True)
    items=read(OUT/'screening_items.jsonl');rows=[]
    for item in items:
        p=reader_prompt(tok,solver_input(item),[]);n=len(tok.encode(p,add_special_tokens=False))
        rows.append({'item_id':item['item_id'],'reader_task_tokens':n,'overflow':n+64>cfg['max_model_len']})
    write(OUT/'input_lengths.jsonl',rows)
    print(json.dumps({'items':len(rows),'max_mandatory_reader_tokens':max(r['reader_task_tokens'] for r in rows),'overflows':sum(r['overflow'] for r in rows)}))
    assert not any(r['overflow'] for r in rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['preflight','smoke','run','repeat','retrieval']);p.add_argument('--batch-size',type=int,default=32);p.add_argument('--chunk-size',type=int,default=32);p.add_argument('--gpu-memory',type=float,default=.45);p.add_argument('--shard-index',type=int,default=0);p.add_argument('--shard-count',type=int,default=1);p.add_argument('--limit',type=int);a=p.parse_args()
    if a.mode=='preflight':preflight();return
    plan=json.loads((OUT/'sample_plan.json').read_text())
    if a.mode=='run' and not plan['tier_frozen']:raise SystemExit('Freeze tier using measured smoke throughput before formal run.')
    items=[solver_input(x) for x in read(OUT/'screening_items.jsonl')]
    if a.mode in ['smoke','repeat']:
        ids=plan['smoke_item_ids' if a.mode=='smoke' else 'repeat_item_ids'];im={i['item_id']:i for i in items};items=[im[k] for k in ids]
    if a.mode in ['run','retrieval']:
        # Interleave whole source groups across datasets; retain the frozen group order.
        labels=read(OUT/'evaluation_labels.jsonl');by_ds=defaultdict(dict)
        for r in labels:by_ds[r['dataset']].setdefault(r['group_id'],[]).append(r['item_id'])
        queues=[list(groups.values()) for groups in by_ds.values()];ordered=[];seen=set()
        for j in range(max(map(len,queues))):
            for q in queues:
                if j<len(q):
                    for key in q[j]:
                        if key not in seen:ordered.append(key);seen.add(key)
        im={i['item_id']:i for i in items};items=[im[k] for k in ordered]
    if a.mode!='retrieval':items=items[a.shard_index::a.shard_count]
    if a.limit:items=items[:a.limit]
    runner=Runner(a)
    try:
        for start in range(0,len(items),a.chunk_size):
            if a.mode=='retrieval':
                runner.retrieve(items[start:start+a.chunk_size]);print(json.dumps({'retrieval_available':len(runner.cached['retrieval']),'elapsed':time.time()-runner.started}),flush=True)
            else:runner.run_chunk(items[start:start+a.chunk_size])
    except Exception as e:
        (runner.root/'failure.json').write_text(json.dumps({'type':type(e).__name__,'message':str(e),'time':time.time()}));raise
    print(json.dumps({'mode':a.mode,'tasks':len(items),'makespan_seconds':time.time()-runner.started,'status':'complete'}),flush=True)

if __name__=='__main__':main()
