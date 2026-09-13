"""Resume native M0 or the unchanged local M2 stages on v5 inputs."""
import argparse, gzip, json, os, sys, time
from pathlib import Path
from types import SimpleNamespace
from prepare_v5 import OUT, PACK, LEGACY, read, write, dump
os.environ['CF_SCREENING_OUTPUT']=str(OUT/'m2_runtime')
sys.path.insert(0,str(PACK/'scripts'))
import run_cf_baseline_screening as base
# Use the existing full native task prompt for robustness as well as ordinary QA.
source=(LEGACY/'code/run_benchmark.py').read_text()
ns={'reader_prompt':base.reader_prompt,'chat':base.chat}
exec(source[source.index('def prompt('):source.index('\ndef preflight')],ns)
task_prompt=ns['prompt']
base.reader_prompt=task_prompt

def main():
    p=argparse.ArgumentParser();p.add_argument('method',choices=['M0','M2']);p.add_argument('--gpu-memory',type=float,default=.55);p.add_argument('--limit',type=int);p.add_argument('--smoke',action='store_true');p.add_argument('--batch-size',type=int,default=16);a=p.parse_args()
    root=OUT/a.method;root.mkdir(exist_ok=True)
    items=read(OUT/f'pending_{a.method}.jsonl');done={r['item_id'] for r in read(root/'predictions.jsonl')}
    items=[i for i in items if i['item_id'] not in done]
    # Short and long budgets stay separate, preserving native per-input budgets.
    items.sort(key=lambda i:(i.get('max_tokens',64),len(i['question'])+sum(map(len,i['fixed_evidence'])),i['item_id']))
    if a.smoke:
        chosen={}
        for i in items:chosen.setdefault(i['answer_format'],i)
        if items:chosen['longest']=max(items,key=lambda i:len(i['question'])+sum(map(len,i['fixed_evidence'])))
        items=list({i['item_id']:i for i in chosen.values()}.values())
    if a.limit:items=items[:a.limit]
    if not items:return
    started=time.time();dump(root/'started.json',dict(pid=os.getpid(),time=started,pending=len(items),gpu=os.environ.get('CUDA_VISIBLE_DEVICES')))
    if a.method=='M2':
        args=SimpleNamespace(mode='run',shard_index=0,batch_size=a.batch_size,gpu_memory=a.gpu_memory)
        runner=base.Runner(args)
        raw_llm=runner.llm
        budgets={i['item_id']:i.get('max_tokens',64) for i in items}
        def llm(stage,entries):
            if stage!='M2':return raw_llm(stage,entries)
            for budget in sorted({budgets[e['item_id']] for e in entries}):
                runner.config['reader']['max_tokens']=budget
                raw_llm(stage,[e for e in entries if budgets[e['item_id']]==budget])
            runner.config['reader']['max_tokens']=64
            return runner.cached['M2']
        runner.llm=llm
        for pos in range(0,len(items),a.batch_size):
            chunk=items[pos:pos+a.batch_size];runner.run_chunk(chunk)
            rows=[runner.cached['M2'][i['item_id']] for i in chunk]
            base.base.append_rows(root/'predictions.jsonl',rows)
            dump(root/'progress.json',dict(completed_this_run=pos+len(chunk),pending_at_start=len(items),seconds=time.time()-started,updated=time.time()))
    else:
        from vllm import SamplingParams
        backend=base.base.VLLMBackend(Path(base.json.loads(base.CONFIG.read_text())['model']),98304,a.gpu_memory)
        for pos in range(0,len(items),a.batch_size):
            chunk=items[pos:pos+a.batch_size]
            prompts=[task_prompt(backend.tokenizer,i,[]) for i in chunk]
            params=[SamplingParams(temperature=0,top_p=1,max_tokens=i.get('max_tokens',64),seed=base.stable_seed(20260906,i['item_id'],'M0',0)) for i in chunk]
            for prompt,cfg in zip(prompts,params):assert len(backend.tokenizer.encode(prompt,add_special_tokens=False))+cfg.max_tokens<=98304
            t=time.time();outputs=backend.model.generate(prompts,params,use_tqdm=False);elapsed=time.time()-t
            rows=[dict(item_id=i['item_id'],method='direct_llama',stage='M0',raw_response=o.outputs[0].text,prompt_tokens=len(o.prompt_token_ids),completion_tokens=len(o.outputs[0].token_ids),finish_reason=o.outputs[0].finish_reason,sampling=dict(temperature=0,top_p=1,max_tokens=c.max_tokens,seed=c.seed),batch_wall_seconds=elapsed,batch_size=len(chunk),time=time.time()) for i,o,c in zip(chunk,outputs,params)]
            with gzip.open(root/'prompts.jsonl.gz','at') as f:
                for i,prompt in zip(chunk,prompts):f.write(json.dumps(dict(item_id=i['item_id'],method='direct_llama',prompt=prompt))+'\n')
            base.base.append_rows(root/'predictions.jsonl',rows)
            status=dict(completed_this_run=pos+len(chunk),pending_at_start=len(items),seconds=time.time()-started,updated=time.time())
            dump(root/'progress.json',status);print(json.dumps(status),flush=True)
    dump(root/('smoke_complete.json' if a.smoke or a.limit else 'complete.json'),dict(time=time.time(),seconds=time.time()-started,inputs=len(items)))
if __name__=='__main__':main()
