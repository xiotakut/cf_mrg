"""Native format adapters preserve full evidence and the original ordinary MCQ prompt."""
import json
from prepare_v5 import OUT,read,dump
from run_medrag import MEDRAG,messages,general_medrag_system,general_medrag,load_config
from transformers import AutoTokenizer

def main():
    excluded={'method_id','method','model_id','model_path','chat_template_kwargs','rope_scaling','context_extension_reason'}
    c4,c5=load_config('M4'),load_config('M5')
    assert {k:v for k,v in c4.items() if k not in excluded}=={k:v for k,v in c5.items() if k not in excluded}
    items=read(OUT/'items.jsonl');chosen={}
    for i in items:chosen.setdefault(i['answer_format'],i)
    chosen['longest']=max(items,key=lambda i:len(i['question'])+sum(map(len,i['fixed_evidence'])))
    chosen['binary']=next(i for i in items if 'yes' in i['options'])
    docs=[dict(title='Retrieval test',content='External retrieved context.')];results=[]
    for m in ['m4','m5']:
        cfg=load_config(m.upper());tok=AutoTokenizer.from_pretrained(cfg['model_path'],local_files_only=True)
        for tag,item in chosen.items():
            ms,truncated=messages(item,docs,tok,cfg)
            assert item['question'] in ms[1]['content']
            assert all(e in ms[1]['content'] for e in item['fixed_evidence'])
            assert all(v in ms[1]['content'] for v in item['options'].values())
            prompt=tok.apply_chat_template(ms,tokenize=False,add_generation_prompt=True,**cfg['chat_template_kwargs']);n=len(tok.encode(prompt,add_special_tokens=False));assert n+2048<131072
            if item['answer_format']=='single' and set(item['options'])<=set('ABCDEFGHIJKLMN'):
                assert ms[0]['content']==general_medrag_system
            results.append(dict(method=m,case=tag,item_id=item['item_id'],prompt_tokens=n,mandatory_evidence_preserved=True))
    dump(OUT/'medrag_prompt_validation.json',dict(status='passed',cases=results));print('MedRAG native prompts and full evidence: passed.')
if __name__=='__main__':main()
