"""Verify selection, input deduplication, native mappings, parser and prompt contracts."""
from collections import Counter,defaultdict
import json,sys
from prepare_v5 import OUT,V5,read,dump,task
from analyze_v5 import objects,score,norm

def main():
    items=read(OUT/'items.jsonl');ev=read(OUT/'evaluation.jsonl');targets=read(V5/'selected_targets.jsonl.gz');units=read(V5/'units.jsonl')
    byid={i['item_id']:i for i in items};ts={t['judgment_id']:t for t in targets}
    assert len(items)==len(byid)==13905
    assert len(ev)==len({e['record_id'] for e in ev})==15616
    assert {e['unit_id'] for e in ev}=={u['unit_id'] for u in units}
    assert {j for e in ev for j in e['judgment_ids']}==set(ts)
    for e in ev:
        selected=[ts[j] for j in e['judgment_ids']]
        assert e['evaluation_labels']==sorted({l for t in selected for l in t['evaluation_labels']})
        assert all(t['unit_id']==e['unit_id'] and t['evaluation_eligible'] for t in selected)
        if e['resource_id']=='M17':assert all(task(t['target'])==e['task'] for t in selected)
        item=byid[e['item_id']]
        assert set(item)<= {'item_id','question','options','fixed_evidence','answer_format','max_tokens'}
        assert e['gold'] is not None and e['scoring_eligible']
        if item['answer_format']=='robustness_single':
            assert len(item['fixed_evidence'])==len(e['document_map'])
            selected_native={t['judgment_id'].rsplit(':',1)[-1] for t in selected}
            assert all(e['document_map'][d]['native_id'] not in selected_native for d in e['incomplete_document_ids'])
    # Equal visible inputs (including native budget and option order) must share inference.
    seen={}
    for i in items:
        sig=json.dumps({k:i.get(k,64) if k=='max_tokens' else i[k] for k in ['question','options','fixed_evidence','answer_format','max_tokens']},ensure_ascii=False)
        assert sig not in seen,(i['item_id'],seen.get(sig));seen[sig]=i['item_id']
    for m in ['M0','M2']:
        pending={r['item_id'] for r in read(OUT/f'pending_{m}.jsonl')};name={'M0':'direct_llama','M2':'medrgag_llama_base'}[m]
        reused={r['item_id'] for r in read(OUT/'cache/reused.jsonl') if r['method']==name}
        assert not pending&reused and pending|reused==set(byid)
    # Strict native key/set handling; rationale cannot supply an alternative answer.
    assert objects('{"answer_choice":"A","errors":[{"document_id":"D0","correction":"x"}]}','answer_choice')['answer_choice']=='A'
    assert objects('{"answer_choice":"A"} {"answer_choice":"B"}','answer_choice') is None
    assert score({'raw_response':'{"answer":["A","B"]}'},{'gold':['B','A']},{'answer_format':'multi','options':{'A':'a','B':'b'}},{})['correct']
    assert not score({'raw_response':'{"answer":"A"}'},{'gold':['A']},{'answer_format':'multi','options':{'A':'a'}},{})['correct']
    report=dict(status='passed',units=len(units),inputs=len(items),selected_judgments=len(targets),evaluation_records=len(ev),selection_and_target_membership=True,visible_input_duplicates=0,pending_reuse_disjoint=True,native_parser_contract=True)
    dump(OUT/'preparation_validation.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
