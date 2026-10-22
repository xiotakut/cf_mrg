"""Replay the independent composite interface on all733 R3 targets; no new inference."""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
candidate=Path(__file__).resolve().parent/'candidate'
sys.path.insert(0,str(candidate))
from r3_audit import HERE, OUT as DATA, read, write, dump
from r3_calibrated_expansion import scoring
from r3_catalog_distribution_pilot import EXTRA_SITE, render_request, BACKBONES
from r3_optimization_head import optimize

out=HERE/'r3_calibrated_all_methods'
methods=('M0','M2','M3','M4','M5','M6','M7')
items={r['item_id']:r for r in read(DATA/'items.jsonl')}
evaluation={r['item_id']:r for r in read(DATA/'evaluation.jsonl')}
baseline={(r['method'],r['item_id']):r for r in read(DATA/'baseline_scores.jsonl')}
diagnoses={(r['method'],r['item_id']):r for r in read(out/'scored.jsonl') if r['variant']=='calibrated_majority'}
medications={(r['method'],r['item_id']):r for r in read(HERE/'r3_rule_transfer/scored.jsonl') if r['policy']=='program'}
objects,score,canonical=scoring()
sys.path.insert(0,EXTRA_SITE)
from transformers import AutoTokenizer

scored,replay=[],[]
for method in methods:
    if method in ('M4','M5'):
        cfg_path=HERE/'r3_calibrated_expansion'/method.lower()
        sources=[cfg_path,HERE/f'r3_catalog_distribution_{method.lower()}',HERE/f'r3_catalog_distribution_{method.lower()}_remaining']
    else:
        cfg_path=out/method.lower()
        sources=[cfg_path,HERE/f'r3_catalog_distribution_{method.lower()}']
    cfg=json.loads((cfg_path/'config.json').read_text())
    tok=AutoTokenizer.from_pretrained(cfg['model'],local_files_only=True)
    catalog=json.loads((cfg_path/'catalog.json').read_text())
    priors=json.loads((cfg_path/'log_priors.json').read_text())
    native={};vectors={};jobs={}
    for source in sources:
        native.update({r['item']['item_id']:r for r in read(source/'inputs.jsonl')})
        vectors.update({(r['item_id'],r['order']):r['code_logprobs'] for r in read(source/'distributions.jsonl')})
        jobs.update({(r['item_id'],r['order']):r for r in read(source/'requests.jsonl')})
    if method=='M2':
        origin={(r['item_id'],r['order']):r['code_logprobs'] for r in read(out/'m0/distributions.jsonl')}
        for r in read(cfg_path/'reused_requests.jsonl'):
            key=(r['item_id'],r['order']);assert key not in vectors
            vectors[key]=origin[key];jobs[key]=r
    assert len(native)==680 and len(vectors)==len(jobs)==4080
    facts_path=HERE/'r3_rule_transfer'/BACKBONES[method]/'facts'
    facts={r['item_id']:r for r in read(facts_path/'gpu3/predictions.jsonl')}
    specs={r['item_id']:{k:r[k] for k in ('messages','schema')} for r in read(facts_path/'requests.jsonl')}
    branch_counts=Counter();score_count=fact_count=0
    for iid,item in items.items():
        b=baseline[method,iid]
        # The original native prediction is a current-case model output, never the gold field.
        initial=None if b['invalid'] else b['prediction']
        row=native.get(iid,{})
        context=row.get('original_prompt') or row.get('messages',[])
        calls=[]
        def score_codes(**req):
            k=len(calls)
            assert render_request(req,tok,cfg)==jobs[iid,k]['prompt']
            calls.append(('score',k));return vectors[iid,k]
        def generate_facts(messages,schema):
            assert dict(messages=messages,schema=schema)==specs[iid]
            calls.append(('facts',0));return facts[iid]['raw_response']
        result=optimize(item,context,initial,catalog,priors,score_codes,generate_facts)
        branch_counts[result['branch']]+=1
        score_count+=sum(c[0]=='score' for c in calls);fact_count+=sum(c[0]=='facts' for c in calls)
        if result['used_original']:
            metric={k:b[k] for k in ('correct','invalid','invalid_reason','format_invalid','unmapped_diagnosis')}
            assert result['answer']==initial
        else:
            metric=score(dict(raw_response=json.dumps(dict(answer=result['answer']))),evaluation[iid],item,canonical)
        if result['branch']=='catalog_vote':
            expected=diagnoses[method,iid];assert len(calls)==6
        elif result['branch']=='rule_support':
            expected=medications[method,iid];assert len(calls)==1
        else:
            expected=b;assert not calls and result['used_original']
        assert all(metric[k]==expected[k] for k in ('correct','invalid','invalid_reason'))
        if result['branch']!='original':assert result['answer']==expected['answer']
        scored.append(dict(method=method,item_id=iid,group_id=evaluation[iid]['group_id'],
            answer_format=item['answer_format'],branch=result['branch'],answer=result['answer'],used_original=result['used_original'],
            original_correct=b['correct'],repaired=metric['correct'] and not b['correct'],harmed=not metric['correct'] and b['correct'],**metric))
    assert branch_counts==dict(catalog_vote=680,rule_support=10,original=43)
    assert score_count==4080 and fact_count==10
    replay.append(dict(method=method,inputs=733,branches=dict(branch_counts),score_callbacks=score_count,
                       fact_callbacks=fact_count,zero_call_passthrough=43,new_model_calls=0))
summary=[]
for method in methods:
    for scope in ('all','diagnosis','multi','single'):
        rs=[r for r in scored if r['method']==method and (scope=='all' or r['answer_format']==scope)]
        summary.append(dict(method=method,scope=scope,n=len(rs),original_correct=sum(r['original_correct'] for r in rs),
            correct=sum(r['correct'] for r in rs),repairs=sum(r['repaired'] for r in rs),harms=sum(r['harmed'] for r in rs),
            invalid=sum(r['invalid'] for r in rs)))
assert len(scored)==733*7
write(out/'complete_head_scored.jsonl',scored)
dump(out/'complete_head_replay.json',replay)
modules=json.loads((candidate/'candidate.json').read_text())['modules']
locations={name:str(Path(sys.modules[name].__file__)) for name in modules}
assert all(Path(path).parent==candidate for path in locations.values())
dump(out/'package_replay_imports.json',dict(status='passed',locations=locations))
dump(out/'complete_head_summary.json',dict(status='complete_cached_replay',results=summary,new_model_calls=0,
    unique_inputs=733,groups=len({r['group_id'] for r in evaluation.values()}),
    resources='Public49 diagnosis names and frozen71 medication rules; original models. No training-case answer retrieval.',
    scope='Exposed v5 R3 only. Diagnosis calls use seven actual native contexts; medication calls reuse two original-backbone fact sets across actual seven initial answers. Single-choice43 pass through unchanged. Not independent generalization.'))
shutil.copyfile(HERE/'r3_optimization_head.py',out/'r3_optimization_head.py')
for r in summary:
    if r['scope']=='all':print(r)
print('callbacks',sum(r['score_callbacks']+r['fact_callbacks'] for r in replay))
