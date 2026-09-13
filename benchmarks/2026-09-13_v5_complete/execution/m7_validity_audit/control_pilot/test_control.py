import sys
from pathlib import Path
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
from candidate_methods import tcrag
ITEM=dict(question='Choose a symbol.', options={'A':'alpha','B':'beta'}, fixed_evidence=[], answer_format='single')
class Fake:
    config=dict(max_loop=8,topK=4,sigma=1.2,format_repairs=1)
    def __init__(self, texts, high=False): self.texts=iter(texts);self.events=[];self.calls=[];self.high=high
    def event(self,kind,**kw):self.events.append(dict(kind=kind,**kw))
    def call(self,stage,messages,entropy):
        self.calls.append(messages)
        return dict(text=next(self.texts),tokens=['x']*4,entropies=[1.0 if self.high else .1]*4,
                    useful_positions=list(range(4)),score_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32')
    def retrieve(self,*args):raise AssertionError('Missing action must not execute a tool')

def main():
    f=Fake(['Action Input: {"query":"alpha"}']+['Thought: verify']*3+['Final Answer: {"answer":"A. alpha"}'])
    r=tcrag(ITEM,f)
    assert r['status']=='ok' and r['steps']==5 and r['raw_response']=='{"answer": "A"}'
    assert any(e['kind']=='tc_parse_failed' for e in f.events)
    assert 'No tool was executed' in f.calls[1][-1]['content']
    f=Fake(['Final Answer: {"answer":"A"}']*8,high=True)
    r=tcrag(ITEM,f)
    assert r['status']=='invalid' and r['termination']=='budget_exhausted' and len(f.calls)==8
    assert all(not e['accepted'] for e in f.events if e['kind']=='tc_action')
    assert 'too early' in f.calls[1][-1]['content']
    assert 'did not pass' in f.calls[5][-1]['content']
    f=Fake(['Action Input: {"query":"alpha"}']*8)
    r=tcrag(ITEM,f)
    assert r['status']=='invalid' and len(f.calls)==8
    assert len(r['issues'])==8
    print('Recovery, no fabricated tool, minimum steps, entropy rejection, budget bound: passed.')
if __name__=='__main__':main()
