"""Single-round upstream MedRAG retrieval/prompts with native v5 answer formats."""
import argparse,gzip,json,os,sys,time
from pathlib import Path
from prepare_v5 import OUT,read,write,dump
MEDRAG=Path('/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag')
# Use the installed MedRAG dependency versions; vLLM comes from the shared runner environment.
sys.path.insert(0,str(MEDRAG/'.venv/lib/python3.10/site-packages'))
sys.path.insert(0,str(MEDRAG))
from src.baselines import make_retriever
from src.template import general_medrag_system,general_medrag

def messages(item,docs,tok,config):
    context='\n'.join(f"Document [{j}] (Title: {d['title']}) {d['content']}" for j,d in enumerate(docs))
    tokens=tok.encode(context,add_special_tokens=False)
    context=tok.decode(tokens[:config['context_length']])
    question=item['question']
    if item['fixed_evidence']:question+='\n\nEvidence supplied with the question:\n'+'\n\n'.join(item['fixed_evidence'])
    fmt=item['answer_format'];system=general_medrag_system
    if fmt!='single' or set(item['options'])-set('ABCDEFGHIJKLMN'):
        contract={'single':'one native option key string', 'multi':'a JSON array of one or more native option keys', 'diagnosis':'one concise most likely diagnosis label', 'relation':'exactly one of "higher", "lower", "no difference", "uncertainty"', 'robustness_single':'one native option key string'}[fmt]
        system=system.replace('multi-choice medical question','medical benchmark question').replace('then choose the answer from the provided options','then give the answer in the required native format').replace('Str{A/B/C/...}',contract)
        question+='\n\nThe answer_choice field must contain '+contract+'.'
    if fmt=='robustness_single':
        question+='\nSome supplied D-numbered documents may contain factual errors. Identify them, correct their factual errors, and answer the main question. Do not assume all documents are correct. Also include an "errors" JSON array; each entry has "document_id" (D-numbered ID) and "correction" (concise corrected statement). Use [] when none are erroneous.'
    user=general_medrag.render(context=context,question=question,options='\n'.join(k+'. '+item['options'][k] for k in sorted(item['options'])))
    return [{'role':'system','content':system},{'role':'user','content':user}],max(0,len(tokens)-config['context_length'])

def load_config(method):
    config=json.loads((OUT/'configs'/f'{method.lower()}.json').read_text())
    config['model_path']=str((MEDRAG/config['model_path']).resolve())
    config['engine']='vllm'
    config['engine_note']='Batched execution; decoding settings retained. Tokens are not claimed equal to Transformers smoke.'
    config['native_task_adapter']='code/run_medrag.py::messages'
    config['max_length']=131072
    if method=='M5':
        config['rope_scaling']={'rope_type':'yarn','factor':4.0,'original_max_position_embeddings':32768}
        config['context_extension_reason']='Preserve complete mandatory v5 evidence; same extension as completed local M3.'
    return config

def main():
    p=argparse.ArgumentParser();p.add_argument('method',choices=['M4','M5']);p.add_argument('--gpu-memory',type=float,default=.65);p.add_argument('--batch-size',type=int,default=16);p.add_argument('--limit',type=int);p.add_argument('--smoke',action='store_true');p.add_argument('--work-dir',type=Path);p.add_argument('--items-file',type=Path);a=p.parse_args()
    root=a.work_dir or OUT/a.method;root.mkdir(parents=True,exist_ok=True)
    if a.method=='M4':
        import fcntl
        run_lock=(root/'run.lock').open('a')
        fcntl.flock(run_lock,fcntl.LOCK_EX)
        if (root/'complete.json').exists() or (a.smoke and (root/'smoke_complete.json').exists()):return
    config=load_config(a.method)
    if (root/'config.json').exists():assert json.loads((root/'config.json').read_text())==config
    else:dump(root/'config.json',config)
    done={r['item_id'] for r in read(root/'predictions.jsonl')}
    items=[i for i in read(a.items_file or OUT/'items.jsonl') if i['item_id'] not in done]
    if a.smoke:
        chosen={};
        for i in items:chosen.setdefault(i['answer_format'],i)
        longest=max(items,key=lambda i:len(i['question'])+sum(map(len,i['fixed_evidence'])))
        chosen['longest']=longest;items=list({i['item_id']:i for i in chosen.values()}.values())
    items.sort(key=lambda i:(len(i['question'])+sum(map(len,i['fixed_evidence'])),i['item_id']))
    if a.limit:items=items[:a.limit]
    if not items:return
    started=time.time();dump(root/'started.json',dict(time=started,pid=os.getpid(),pending=len(items),gpu=os.environ.get('CUDA_VISIBLE_DEVICES')))
    retrievals={r['question']:r for r in read(root/'retrieval.jsonl')}
    retriever=make_retriever(config,MEDRAG/'corpus',MEDRAG/'models/MedCPT-Cross-Encoder')
    from vllm import LLM,SamplingParams
    kwargs={}
    if 'rope_scaling' in config:kwargs['rope_scaling']=config['rope_scaling']
    model=LLM(model=config['model_path'],dtype='bfloat16',max_model_len=config['max_length'],gpu_memory_utilization=a.gpu_memory,max_num_seqs=16,enable_prefix_caching=True,seed=config['seed'],**kwargs)
    tok=model.get_tokenizer()
    for pos in range(0,len(items),a.batch_size):
        chunk=items[pos:pos+a.batch_size];prompts=[];metadata=[]
        for item in chunk:
            q=item['question']
            if q not in retrievals:
                t=time.time();docs,scores=retriever.retrieve(q,k=config['k'],rrf_k=config['rrf_k'])
                r=dict(question=q,documents=docs,scores=scores,seconds=time.time()-t);retrievals[q]=r
                with (root/'retrieval.jsonl').open('a') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
            r=retrievals[q];ms,truncated=messages(item,r['documents'],tok,config)
            prompt=tok.apply_chat_template(ms,tokenize=False,add_generation_prompt=True,**config['chat_template_kwargs'])
            n=len(tok.encode(prompt,add_special_tokens=False));assert n+2048<=config['max_length'],(item['item_id'],n)
            prompts.append(prompt);metadata.append(dict(messages=ms,retrieval_question=q,context_truncated_tokens=truncated))
        gen=config['generation_kwargs'];params=SamplingParams(temperature=gen['temperature'],top_p=gen['top_p'],top_k=-1,max_tokens=gen['max_new_tokens'],seed=config['seed'])
        t=time.time();outputs=model.generate(prompts,params,use_tqdm=False);elapsed=time.time()-t
        with gzip.open(root/'prompts.jsonl.gz','at') as f:
            for i,prompt,meta in zip(chunk,prompts,metadata):f.write(json.dumps(dict(item_id=i['item_id'],prompt=prompt,**meta),ensure_ascii=False)+'\n')
        with (root/'predictions.jsonl').open('a') as f:
            for i,o,meta in zip(chunk,outputs,metadata):
                answer=o.outputs[0]
                r=dict(item_id=i['item_id'],method=config['method'],method_id=a.method,raw_response=answer.text,prompt_tokens=len(o.prompt_token_ids),completion_tokens=len(answer.token_ids),finish_reason=answer.finish_reason,sampling=dict(temperature=gen['temperature'],top_p=gen['top_p'],top_k=-1,max_tokens=2048,seed=config['seed']),batch_wall_seconds=elapsed,batch_size=len(chunk),context_truncated_tokens=meta['context_truncated_tokens'],time=time.time())
                f.write(json.dumps(r,ensure_ascii=False)+'\n')
        status=dict(completed_this_run=pos+len(chunk),pending_at_start=len(items),seconds=time.time()-started,updated=time.time());dump(root/'progress.json',status);print(json.dumps(status),flush=True)
    dump(root/('smoke_complete.json' if a.smoke or a.limit else 'complete.json'),dict(inputs=len(items),seconds=time.time()-started,time=time.time()))
if __name__=='__main__':main()
