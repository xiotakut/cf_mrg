"""Isolated real continuation, exact request-cache reuse and unchanged TC thresholds."""
import json
import sys
import time
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
from common import atomic,digest
from runtime import Session
from backend import HFBackend,BatchingBackend,Retriever
from methods import tcrag as original_method
from candidate_methods import tcrag as candidate_method

class Continuation(Session):
    def __init__(self,*args,source,**kwargs):
        super().__init__(*args,**kwargs)
        self.source=source;self.new_llm=0;self.new_retrieval=0;self.inherited=0
    def request(self,spec,operation):
        key=digest(spec);dest=self.root/'requests'/f'{key}.json'
        src=self.source/f'{key}.json'
        if not dest.exists() and src.exists():
            record=json.loads(src.read_text());assert record['spec']==spec and record['status']=='ok'
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
            self.inherited+=1
        def counted():
            if spec['kind']=='llm':self.new_llm+=1
            else:self.new_retrieval+=1
            return operation()
        return super().request(spec,counted)

class CacheOnly:
    def __init__(self,tokenizer):self.tokenizer=tokenizer
    def generate(self,*a,**kw):raise AssertionError('Original replay cache miss')
    def retrieve(self,*a,**kw):raise AssertionError('Original replay retrieval cache miss')

def main():
    selection=json.loads((ROOT/'selection.json').read_text())
    cases=selection['cases']
    config=json.loads((SOURCE/'configs/tcrag_single_gpu.json').read_text())
    start=time.time();model=HFBackend(config)
    atomic(ROOT/'backend.json',dict(identity=model.identity,physical_gpu=1,model_config=config,
           variant='parse_feedback_rejection_feedback_last_two_turns_contract_v1',workers=8,max_batch_tokens=64000))
    for case in cases:
        src=Path(case['original']['requests_path'])
        configs=[r['spec']['config'] for p in src.glob('*.json') if (r:=json.loads(p.read_text()))['spec']['kind']=='llm']
        assert configs and all(c==configs[0] for c in configs)
        case['config']=configs[0]
        iid=case['item']['item_id']
        cache=CacheOnly(model.tokenizer)
        replay=Continuation(ROOT/'baseline'/iid,case['config'],cache,cache,source=src,batch_group=case['item']['answer_format'])
        result=original_method(case['item'],replay)
        for key in ['raw_response','status','termination']:
            assert result[key]==case['original'][key],(iid,key)
        assert replay.new_llm==replay.new_retrieval==0
    atomic(ROOT/'baseline_replay.json',dict(N=len(cases),raw_and_status_identical=True,new_requests=0))
    print('Baseline exact-cache replay passed for all 20 cases.',flush=True)
    retriever=Retriever(config['retrieval']);backend=BatchingBackend(model,64000)
    def run(case):
        item=case['item'];iid=item['item_id'];dest=ROOT/'candidate'/iid
        if (dest/'result.json').exists():return json.loads((dest/'result.json').read_text())
        session=Continuation(dest,case['config'],backend,retriever,source=Path(case['original']['requests_path']),batch_group=item['answer_format'])
        result=candidate_method(item,session)
        result.update(item_id=iid,stratum=case['stratum'],original_status=case['original']['status'],
                      original_termination=case['original']['termination'],new_llm=session.new_llm,
                      new_retrieval=session.new_retrieval,inherited_receipts=session.inherited,costs=session.costs())
        atomic(dest/'result.json',result)
        return result
    results=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(run,c) for c in cases]
        for future in as_completed(futures):
            result=future.result();results.append(result)
            progress=dict(N=len(cases),done=len(results),status=dict(Counter(r['status'] for r in results)),
                          seconds=time.time()-start,new_llm=sum(r['new_llm'] for r in results))
            atomic(ROOT/'progress.json',progress)
            print(json.dumps(dict(item_id=result['item_id'],stratum=result['stratum'],result=result['status'],**progress)),flush=True)
    atomic(ROOT/'predictions.jsonl',results,lines=True)
    strata={s:dict(N=sum(r['stratum']==s for r in results),ok=sum(r['stratum']==s and r['status']=='ok' for r in results)) for s in selection['strata']}
    atomic(ROOT/'complete.json',dict(**progress,strata=strata,limits_unchanged=True,sigma=1.2,topK=4,max_loop=8,
                                   sampling='Failure-stratified development pilot, not overall validity estimate.'))
if __name__=='__main__':main()
