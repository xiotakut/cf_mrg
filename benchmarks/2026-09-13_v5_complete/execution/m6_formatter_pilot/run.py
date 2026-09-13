"""Two isolated formatter-only variants; frozen final reasoning is reused."""
import json
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
sys.path.insert(0,'/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag/.venv/lib/python3.10/site-packages')
sys.path.insert(0,str(ROOT.parent/'results_v5_m0_m2_m4_m5/code'))
from backend import HFBackend
from common import valid_answer
from m4_output_schema import output_schema


def schema(item):
    s=output_schema(item)
    s['properties'].pop('step_by_step_thinking')
    s['properties']['answer']=s['properties'].pop('answer_choice')
    s['required']=list(s['properties'])
    return s


def messages(row):
    ms=[dict(m) for m in row['spec']['messages'][0]]
    ms[-1]['content']=('Format ONLY the answer already stated in your preceding response. Do not solve the question again, change the chosen option, add a new diagnosis, or add reasoning. '
        'Return exactly one valid JSON object with double-quoted keys and strings, no headings, code fences, or surrounding prose. '
        'For option answers output only the native option key, not option text. For diagnosis copy the already stated diagnosis into a string, not a nested object. '
        'Escape line breaks and embedded quotes inside strings. Preserve existing document corrections, if required. '
        'Follow this JSON Schema (it specifies the legal output shape, NOT the correct answer): '+json.dumps(schema(row['item'])))
    assert ms[:-1]==row['spec']['messages'][0][:-1]
    assert ms[-2]['role']=='assistant'
    return ms


def main():
    rows=[json.loads(l) for l in (ROOT/'inputs.jsonl').open()]
    config=dict(rows[0]['spec']['config']);config['device_map']={'':0}
    model=HFBackend(config)
    import xgrammar as xgr
    from xgrammar.contrib.hf import LogitsProcessor
    info=xgr.TokenizerInfo.from_huggingface(model.tokenizer,vocab_size=model.model.config.vocab_size,stop_token_ids=model.model.generation_config.eos_token_id)
    compiler=xgr.GrammarCompiler(info)
    compiled={r['item']['item_id']:compiler.compile_json_schema(json.dumps(schema(r['item']))) for r in rows}
    (ROOT/'config.json').write_text(json.dumps(dict(config=config,identity=model.identity,format_budget=2048,arms=['prompt','structured'],note='Only last user formatting instruction replaced; original per-request seed retained; batching differs from historical runs.'),indent=2))
    rows.sort(key=lambda r:len(model.tokenizer.encode(model.prompts([messages(r)])[0],add_special_tokens=False)))
    for arm in ('prompt','structured'):
        target=ROOT/(arm+'.jsonl')
        done={r['item_id'] for l in target.open() if (r:=json.loads(l))} if target.exists() else set()
        pending=[r for r in rows if r['item']['item_id'] not in done]
        for start in range(0,len(pending),8):
            chunk=pending[start:start+8]
            original=model.model._get_logits_processor
            if arm=='structured':
                processor=LogitsProcessor([compiled[r['item']['item_id']] for r in chunk])
                def get_processors(*args,**kwargs):
                    result=original(*args,**kwargs);result.append(processor);return result
                model.model._get_logits_processor=get_processors
            try:
                outputs=model.generate([messages(r) for r in chunk],2048,chunk[0]['spec']['seed'],sampling_groups=[(1,r['spec']['seed']) for r in chunk])
            finally:
                model.model._get_logits_processor=original
            with target.open('a') as f:
                for row,result in zip(chunk,outputs):
                    error=valid_answer(result['text'],row['item'])
                    f.write(json.dumps(dict(item_id=row['item']['item_id'],arm=arm,error=error,result=result),ensure_ascii=False)+'\n')
            print(json.dumps(dict(arm=arm,completed=len(done)+start+len(chunk),total=len(rows))),flush=True)
    (ROOT/'complete.json').write_text(json.dumps(dict(N=len(rows),arms=2)))

if __name__=='__main__':main()
