"""Same-100-input ablation of exception recovery versus the complete adaptation."""
import json
from pathlib import Path
from statistics import mean
from report import report
ROOT=Path(__file__).resolve().parent

def main():
    recovered=ROOT/'recovery100'
    report([recovered/'gpu1',recovered/'gpu3'],recovered)
    cases=[c for i in [1,3] for c in json.loads((recovered/f'gpu{i}'/'selection.json').read_text())['cases']]
    original={c['item']['item_id']:c['original'] for c in cases}
    variants={}
    for name,folder,gpus in [('recovery_only','recovery100',[1,3]),('complete_fix','typed100',[1,2,3])]:
        variants[name]={r['item_id']:r for i in gpus for p in (ROOT/folder/f'gpu{i}'/'candidate').glob('*/result.json') if (r:=json.loads(p.read_text()))}
        assert variants[name].keys()==original.keys()
    for iid,old in original.items():
        new=variants['recovery_only'][iid]
        if old['status']=='ok' or old['termination']=='budget_exhausted':
            assert all(new[k]==old[k] for k in ['raw_response','status','termination'])
            assert new['new_llm']==0
    summary={}
    for name,values in [('original',original),*variants.items()]:
        rows=list(values.values())
        summary[name]=dict(N=len(rows),protocol_valid=sum(r['status']=='ok' for r in rows),
                          llm_calls_total=sum(r['costs']['llm_requests'] for r in rows),
                          mean_llm_calls=mean(r['costs']['llm_requests'] for r in rows),
                          completion_tokens=sum(r['costs']['completion_tokens'] for r in rows),
                          retrieval_calls=sum(r['costs']['retrieval_requests'] for r in rows))
    result=dict(summary=summary,
                original_valid_61_and_original_budget_exhausted_12_unchanged_in_exception_only=True,
                exception_only_new_llm=sum(r['new_llm'] for r in variants['recovery_only'].values()),
                note='Same 100 previously used development inputs. Total logical calls count reused stages; new_llm counts this ablation computation. Complete fix also changes other feedback and adds deterministic representation normalization, so its gain is not attributed solely to recovery.')
    (recovered/'three_way_comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
