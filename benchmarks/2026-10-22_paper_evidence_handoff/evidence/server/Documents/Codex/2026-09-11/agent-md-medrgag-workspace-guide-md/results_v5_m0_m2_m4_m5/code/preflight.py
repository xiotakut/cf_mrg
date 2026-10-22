import sys
from prepare_v5 import OUT,read,write,dump
from transformers import AutoTokenizer
from run_llama import task_prompt
items=read(OUT/'items.jsonl');rows=[]
for model in ['/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct','/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/models/Qwen3-8B']:
 tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
 lengths=[dict(item_id=i['item_id'],tokens=len(tok.encode(task_prompt(tok,i,[]),add_special_tokens=False))) for i in items]
 name='llama' if 'Llama' in model else 'qwen'
 write(OUT/f'lengths_{name}.jsonl',lengths)
 report=dict(model=model,max_tokens=max(r['tokens'] for r in lengths),above_30k=sum(r['tokens']>30000 for r in lengths),above_90k=sum(r['tokens']>90000 for r in lengths));rows.append(report);print(report,flush=True)
 assert report['max_tokens']+2048<98304
 dump(OUT/'preflight.json',rows)
