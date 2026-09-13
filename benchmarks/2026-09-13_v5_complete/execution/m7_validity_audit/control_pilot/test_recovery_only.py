from test_control import Fake,ITEM
from candidate_recovery_only import tcrag

def main():
    f=Fake(['Final Answer: {"answer":"A"}']*8,high=True)
    r=tcrag(ITEM,f)
    assert r['termination']=='budget_exhausted' and len(f.calls)==8
    assert not any(e['kind']=='tc_exception_feedback' for e in f.events)
    f=Fake(['Action Input: {"query":"alpha"}']+['Thought: check']*3+['Final Answer: {"answer":"A"}'])
    r=tcrag(ITEM,f)
    assert r['status']=='ok' and r['steps']==5
    assert 'No tool was executed' in f.calls[1][-1]['content']
    f=Fake(['Thought: check']*4+['Final Answer: {"answer":"A. alpha"}', 'Final Answer: {"answer":"A"}'])
    r=tcrag(ITEM,f)
    assert r['status']=='ok' and r['steps']==6
    f=Fake(['Thought: check']*7+['Final Answer: {"answer":"A. alpha"}'])
    r=tcrag(ITEM,f)
    assert r['status']=='invalid' and len(f.calls)==8
    print('Exception-only recovery, unchanged rejection prompts, bounded retries: passed.')
if __name__=='__main__':main()
