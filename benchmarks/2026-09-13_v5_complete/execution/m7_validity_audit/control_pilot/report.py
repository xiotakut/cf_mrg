"""Report real pilot results, retained TC gates and native scores without new inference."""
import json,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parent
SOURCE=Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0,str(SOURCE/'code'))
from common import json_object
sys.path.insert(0,str(ROOT.parents[1]/'results_v5_m0_m2_m4_m5/code'))
from analyze_v5 import score,norm,PACK

def report(roots,dest):
    cases=[];results={}
    for root in roots:
        cases+=json.loads((root/'selection.json').read_text())['cases']
        for p in (root/'candidate').glob('*/result.json'):
            r=json.loads(p.read_text());assert r['item_id'] not in results;results[r['item_id']]=r
    assert len(cases)==len(results)
    canonical={norm(s):s for s in json.loads((PACK/'results_cf_full_test/canonical_labels.json').read_text())['labels']}
    evaluations=defaultdict(list)
    for line in (SOURCE/'data/evaluation.jsonl').open():
        e=json.loads(line)
        if e['item_id'] in results:evaluations[e['item_id']].append(e)
    stats={arm:Counter() for arm in ['original','candidate']};strata={};changed=[];gate_checks=0
    for case in cases:
        iid=case['item']['item_id'];old=case['original'];new=results[iid];item=case['item']
        group=strata.setdefault(case['stratum'],dict(N=0,original_ok=0,candidate_ok=0))
        group['N']+=1;group['original_ok']+=old['status']=='ok';group['candidate_ok']+=new['status']=='ok'
        for arm,r in [('original',old),('candidate',new)]:
            stats[arm]['protocol_ok']+=r['status']=='ok'
            obj=json_object(r['raw_response'],'answer') if r['status']=='ok' else None
            native=dict(raw_response=json.dumps({'answer':obj['answer']}) if obj else '')
            native_item=dict(item,answer_format='single') if item['answer_format']=='robustness_single' else item
            for e in evaluations[iid]:
                scored=score(native,e,native_item,canonical)
                stats[arm]['mapped_records']+=1
                stats[arm]['native_valid']+=not scored['invalid']
                stats[arm]['native_correct']+=bool(scored['correct'])
                if old['status']=='ok':
                    stats[arm]['original_ok_mapped_records']+=1
                    stats[arm]['original_ok_native_correct']+=bool(scored['correct'])
                    stats[arm]['original_ok_native_valid']+=not scored['invalid']
        if old['status']=='ok':
            old_value=json_object(old['raw_response'],'answer')['answer']
            new_value=json_object(new['raw_response'],'answer')['answer'] if new['status']=='ok' else None
            if old_value!=new_value:changed.append(dict(item_id=iid,old=old_value,new=new_value))
        for root in roots:
            for p in (root/'candidate'/iid/'events').glob('*.json'):
                e=json.loads(p.read_text())
                if e['kind']=='tc_action' and e['action']=='final answer':
                    expected=e['step']>=4 and e['state_after']<1.2
                    assert e['accepted']==expected
                    assert abs(e['state_after']-sum(e['state_signal']['selected_entropies']))<1e-8
                    gate_checks+=1
    value=dict(N=len(cases),summary={k:dict(v) for k,v in stats.items()},strata=strata,
               original_valid_answer_changes=changed,gate_checks=gate_checks,
               raw_entropy_and_gate_consistent=True,new_llm=sum(r['new_llm'] for r in results.values()),
               inherited_receipts=sum(r['inherited_receipts'] for r in results.values()),
               invalid_reasons=dict(Counter(r.get('answer_error') or r['termination'] for r in results.values() if r['status']!='ok')),
               note='Native scoring uses all mappings, including references; not v5 category/unit accuracy. Correctness labels are read only after generation. Prompt changes can change answers and are not token-equivalent.')
    (dest/'comparison.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(value,ensure_ascii=False,indent=2))
if __name__=='__main__':
    if len(sys.argv)>1:
        root=ROOT/('typed100' if sys.argv[1]=='typed' else 'validation100');report([root/f'gpu{i}' for i in [1,2,3]],root)
    else:report([ROOT],ROOT)
