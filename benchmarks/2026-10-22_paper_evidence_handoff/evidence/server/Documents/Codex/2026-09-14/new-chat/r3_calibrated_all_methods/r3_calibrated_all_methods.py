"""Frozen catalog-head transfer to the other five native methods on all680 diagnoses."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from r3_audit import HERE, OUT as DATA, read, write, dump
from r3_calibrated_expansion import scoring
from r3_catalog_distribution_head import orders, request, aggregate, calibrate, optimize_calibrated
from r3_catalog_distribution_pilot import EXTRA_SITE, render_request, run as run_scores
from r3_catalog_calibration import content_free_context

OUT=HERE/'r3_calibrated_all_methods'
METHODS=('M0','M2','M3','M6','M7')
ALL_METHODS=('M0','M2','M3','M4','M5','M6','M7')
VARIANTS=('original','order0','uncalibrated_majority','calibrated_majority')


def prepare():
    if OUT.exists():
        assert json.loads((OUT/'plan.json').read_text())['status']=='preparing'
        assert not list(OUT.glob('*/raw_calls.jsonl'))
    rows=list(read(HERE/'r3_calibrated_expansion/all_method_contexts/inputs.jsonl'))
    evaluation={r['item_id']:r for r in read(DATA/'evaluation.jsonl')}
    baseline={(r['method'],r['item_id']):r for r in read(DATA/'baseline_scores.jsonl')}
    objects,score,canonical=scoring()
    OUT.mkdir(exist_ok=True)
    dump(OUT/'plan.json',dict(status='preparing',methods=METHODS,cases_per_method=640,
         requested_score_vectors=19200,scope='Same680 exposed v5 diagnoses; original40 per new method reused.',
         head='Frozen catalog, six orders, content-free priors, coefficient1 and majority/tie rules. No per-method policy selection.',
         controls=VARIANTS,prior_new_calls=0,
         reuse='Existing M4/M5 all680; other methods initial40;90 content-free prior calls. Exact M2/M0 same-case prompts reuse M0 raw scores when model/config match.',
         inference='Original model and exact native final context. No new retrieval, training labels, test gold or reference case in GPU requests.',
         cost='Each deployed head requests six score vectors. Cross-method evaluation cache is reported separately from this per-invocation cost.'))
    sys.path.insert(0,EXTRA_SITE)
    from transformers import AutoTokenizer
    original_m0_jobs={};original_m0_cfg=None;preflights=[]
    for method in METHODS:
        path=OUT/method.lower();path.mkdir(exist_ok=True)
        # The first preparation stopped at M7 native-status parity; reuse completed CPU preparation.
        if (path/'preflight.json').exists():
            info=json.loads((path/'preflight.json').read_text());preflights.append(info)
            if method=='M0':
                original_m0_cfg=json.loads((path/'config.json').read_text())
                original_m0_jobs={(r['item_id'],r['order']):r for r in read(path/'requests.jsonl')}
            print('Reused completed preparation',method,flush=True)
            continue
        old=HERE/f'r3_catalog_distribution_{method.lower()}'
        prior=HERE/f'r3_catalog_calibration_{method.lower()}'
        old_rows=list(read(old/'inputs.jsonl'));old_ids={r['item']['item_id'] for r in old_rows}
        selected=[r for r in rows if r['method']==method and r['item']['item_id'] not in old_ids]
        assert len(selected)==len({r['item']['item_id'] for r in selected})==640
        cfg=json.loads((old/'config.json').read_text())
        cfg.setdefault('model_kwargs',{})['num_gpu_blocks_override']=2048
        catalog=json.loads((old/'catalog.json').read_text());permutations=orders(catalog)
        assert permutations==json.loads((old/'orders.json').read_text())
        assert (HERE/'r3_catalog_distribution_head.py').read_text()==(old/'r3_catalog_distribution_head.py').read_text()
        log_priors=json.loads((prior/'log_priors.json').read_text())
        log_priors=[log_priors[str(k)] for k in range(6)]
        tokens=json.loads((old/'token_ids.json').read_text())
        tok=AutoTokenizer.from_pretrained(cfg['model'],local_files_only=True)
        assert all(tok.encode(c,add_special_tokens=False)==[v] for c,v in tokens.items())
        template=content_free_context(old_rows[0].get('original_prompt') or old_rows[0]['messages'],'N/A')
        jobs,prepared,lengths=[],[],[]
        mismatches=[]
        for row in sorted(selected,key=lambda r:r['item']['item_id']):
            item=row['item'];iid=item['item_id'];context=row.get('original_prompt') or row['messages']
            assert content_free_context(context,'N/A')==template
            raw=row['original_response'];native_status=None
            if method in ('M6','M7'):
                native_status=json.loads(Path(row['provenance']['result']).read_text())['status']
                if native_status!='ok':raw=''
            parsed=objects(raw,'answer');answer=parsed['answer'] if parsed else None
            metric=score(dict(raw_response=json.dumps(dict(answer=answer)) if parsed else ''),evaluation[iid],item,canonical)
            if any(metric[k]!=baseline[method,iid][k] for k in ('correct','invalid','invalid_reason')):
                mismatches.append(dict(item_id=iid,parsed_answer=answer,current=metric,baseline=baseline[method,iid],original_response=row['original_response']))
            prepared.append(dict(row,original_answer=answer,native_status=native_status))
            for k,names in enumerate(permutations):
                req=request(item,context,names)
                prompt=render_request(req,tok,cfg)
                jobs.append(dict(item_id=iid,order=k,prompt=prompt))
                lengths.append(len(tok.encode(prompt,add_special_tokens=False)))
        write(path/'baseline_parity_mismatches.jsonl',mismatches)
        assert not mismatches,(method,'original-score parity failures',len(mismatches))
        assert max(lengths)+1<=cfg['max_model_len'],(method,max(lengths),cfg['max_model_len'])
        reused=[]
        if method=='M0':
            original_m0_jobs={(r['item_id'],r['order']):r for r in jobs};original_m0_cfg=cfg
        if method=='M2':
            assert cfg==original_m0_cfg
            reused=[dict(j,source_method='M0') for j in jobs if original_m0_jobs[j['item_id'],j['order']]['prompt']==j['prompt']]
            keys={(r['item_id'],r['order']) for r in reused}
            jobs=[j for j in jobs if (j['item_id'],j['order']) not in keys]
        write(path/'inputs.jsonl',prepared);write(path/'requests.jsonl',jobs);write(path/'reused_requests.jsonl',reused)
        ids={r['item']['item_id'] for r in prepared}
        write(path/'evaluation.jsonl',[evaluation[i] for i in sorted(ids)])
        write(path/'baseline_scored.jsonl',[baseline[method,i] for i in sorted(ids)])
        for name,value in [('config',cfg),('catalog',catalog),('orders',permutations),('token_ids',tokens),('log_priors',log_priors)]:dump(path/f'{name}.json',value)
        info=dict(method=method,cases=len(prepared),new_primary_requests=len(jobs),reused_score_requests=len(reused),
                  baseline_parity=640,max_prompt_tokens=max(lengths),prior_template_matches=True,
                  config_change='2048 KV blocks; all inference/template settings otherwise unchanged')
        dump(path/'preflight.json',info);preflights.append(info);print(info,flush=True)
    for name in ('r3_calibrated_all_methods.py','r3_catalog_distribution_head.py','r3_catalog_distribution_pilot.py','r3_catalog_calibration.py','r3_ontology_head.py'):
        shutil.copyfile(HERE/name,OUT/name)
    plan=json.loads((OUT/'plan.json').read_text());plan.update(status='prepared',preflight=preflights,
         new_primary_requests=sum(r['new_primary_requests'] for r in preflights),
         reused_m0_m2_requests=sum(r['reused_score_requests'] for r in preflights));dump(OUT/'plan.json',plan)
    (OUT/'README.md').write_text('# Frozen R3 seven-method expansion\n\n'
        'Main record: [R3 all-method expansion](/home/data3/txy/docs/research/r3_candidate_comparison.md#r3-calibrated-all-methods).\n\n'
        'From the parent directory use the existing MedRGAG venv: `r3_calibrated_all_methods.py prepare`; '
        'then run GPU1 with `run --gpu 1 --methods M0 M2 M3` and GPU3 with `run --gpu 3 --methods M6 M7`, '
        'setting CUDA_VISIBLE_DEVICES to the corresponding GPU. Finally use `analyze`.\n'
        'GPU workers read requests/config/token IDs only. Priors, original40 and all M4/M5 outputs are reused. '
        'M0 precedes M2 for the exact-request cache. Run logs, status and costs are separate per worker/queue.\n')


def run(gpu,methods):
    assert os.environ['CUDA_VISIBLE_DEVICES']==str(gpu)
    start=time.time();status=dict(status='running',pid=os.getpid(),gpu=gpu,methods=methods,started_at=start,finished=[])
    for method in methods:
        path=OUT/method.lower()
        if method=='M2':assert json.loads((OUT/'m0/runtime.json').read_text())['status']=='complete'
        status.update(method=method,elapsed_seconds=time.time()-start);dump(OUT/f'runtime_gpu{gpu}.json',status)
        with (path/f'gpu{gpu}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,'-u',str(HERE/'r3_calibrated_all_methods.py'),'worker',
                                    '--gpu',str(gpu),'--method',method],cwd=HERE,stdout=log,stderr=subprocess.STDOUT)
            status['child_pid']=child.pid;dump(OUT/f'runtime_gpu{gpu}.json',status);code=child.wait()
        if code:
            status.update(status='failed',returncode=code);dump(OUT/f'runtime_gpu{gpu}.json',status)
            raise RuntimeError(f'{method} failed; see {path}')
        status['finished'].append(method)
    status.update(status='complete',elapsed_seconds=time.time()-start);dump(OUT/f'runtime_gpu{gpu}.json',status)


def analyze():
    objects,score,canonical=scoring()
    evaluation={r['item_id']:r for r in read(DATA/'evaluation.jsonl')}
    splits={r['item_id']:r['split'] for r in read(DATA/'split.jsonl')}
    all_rows=[dict(r,split=splits[r['item_id']]) for r in read(HERE/'r3_calibrated_expansion/scored.jsonl')]
    costs,replay,predictions=[],[],[]
    sys.path.insert(0,EXTRA_SITE)
    from transformers import AutoTokenizer
    for method in METHODS:
        path=OUT/method.lower();old=HERE/f'r3_catalog_distribution_{method.lower()}'
        cfg=json.loads((path/'config.json').read_text());tok=AutoTokenizer.from_pretrained(cfg['model'],local_files_only=True)
        catalog=json.loads((path/'catalog.json').read_text());permutations=orders(catalog)
        priors=json.loads((path/'log_priors.json').read_text());matched=0
        for source,is_new in [(old,False),(path,True)]:
            inputs={r['item']['item_id']:r for r in read(source/'inputs.jsonl')}
            baseline={r['item_id']:r for r in read(source/'baseline_scored.jsonl')}
            raw=list(read(source/'distributions.jsonl'))
            lookup={(r['item_id'],r['order']):r['code_logprobs'] for r in raw}
            assert len(raw)==len(lookup)
            jobs={(r['item_id'],r['order']):r for r in read(source/'requests.jsonl')}
            if is_new:
                reused=list(read(path/'reused_requests.jsonl'))
                if reused:
                    origin={(r['item_id'],r['order']):r['code_logprobs'] for r in read(OUT/'m0/distributions.jsonl')}
                    for j in reused:
                        key=(j['item_id'],j['order']);assert key not in lookup
                        lookup[key]=origin[key];jobs[key]=j
            assert len(lookup)==len(jobs)==len(inputs)*6
            old_scores={}
            if not is_new:
                for family,mapping in [('distribution',{'order0':'order0','majority_vote':'uncalibrated_majority'}),
                                       ('calibration',{'majority_vote':'calibrated_majority'})]:
                    for r in read(HERE/f'r3_catalog_{family}_{method.lower()}'/'scored.jsonl'):
                        if r['variant'] in mapping:old_scores[r['item_id'],mapping[r['variant']]]=r
            for iid,row in inputs.items():
                values=[lookup[iid,k] for k in range(6)]
                plain=aggregate(catalog,permutations,values);cal=aggregate(catalog,permutations,calibrate(values,priors))
                if is_new:
                    calls=[]
                    def callback(**req):
                        k=len(calls);assert render_request(req,tok,cfg)==jobs[iid,k]['prompt'];calls.append(k)
                        return lookup[iid,k]
                    result=optimize_calibrated(row['item'],row.get('original_prompt') or row['messages'],row['original_answer'],catalog,priors,callback)
                    assert result['answer']==cal['majority_vote'] and not result['used_original'] and len(calls)==6
                variants=dict(order0=plain['per_order'][0],uncalibrated_majority=plain['majority_vote'],calibrated_majority=cal['majority_vote'])
                predictions.append(dict(method=method,item_id=iid,uncalibrated=plain,calibrated=cal))
                for variant,answer in variants.items():
                    metric=score(dict(raw_response=json.dumps(dict(answer=answer))),evaluation[iid],row['item'],canonical)
                    if not is_new:
                        before=old_scores[iid,variant]
                        assert answer==before['answer'] and all(metric[k]==before[k] for k in ['correct','invalid']);matched+=1
                    all_rows.append(dict(method=method,item_id=iid,group_id=evaluation[iid]['group_id'],split=splits[iid],
                                         gold=evaluation[iid]['gold'],variant=variant,answer=answer,**metric))
                b=baseline[iid]
                all_rows.append(dict(method=method,item_id=iid,group_id=evaluation[iid]['group_id'],split=splits[iid],
                     gold=evaluation[iid]['gold'],variant='original',answer=b['prediction'],
                     **{k:b[k] for k in ('correct','invalid','invalid_reason','format_invalid','unmapped_diagnosis')}))
        assert matched==120
        replay.append(dict(method=method,new_cases=640,matching_callbacks=3840,reused_initial40_predictions=matched,new_model_calls=0))
        raw=list(read(path/'raw_calls.jsonl'))
        costs.append(dict(method=method,new_calls=len(raw),input_tokens=sum(r['prompt_tokens'] for r in raw),
             output_tokens=sum(r['completion_tokens'] for r in raw),reused_m0_scores=len(list(read(path/'reused_requests.jsonl'))),
             runtime=json.loads((path/'runtime.json').read_text())))
    results=[]
    for method in ALL_METHODS:
        for scope in ['all680','development','confirmation']:
            rows=[r for r in all_rows if r['method']==method and (scope=='all680' or r['split']==scope)]
            controls={v:{r['item_id']:r for r in rows if r['variant']==v} for v in VARIANTS[:3]}
            for variant in VARIANTS:
                rs=[r for r in rows if r['variant']==variant];assert len(rs)==len({r['item_id'] for r in rs})==len(controls['original'])
                assert len(rs)==dict(all680=680,development=128,confirmation=552)[scope]
                classes={}
                for r in rs:
                    c=classes.setdefault(str(r['gold']),dict(n=0,correct=0));c['n']+=1;c['correct']+=int(r['correct'])
                results.append(dict(method=method,scope=scope,variant=variant,n=len(rs),correct=sum(r['correct'] for r in rs),
                    invalid=sum(r['invalid'] for r in rs),macro_recall=sum(c['correct']/c['n'] for c in classes.values())/len(classes),class_results=classes,
                    comparisons={v:dict(repairs=sum(r['correct'] and not control[r['item_id']]['correct'] for r in rs),
                                        harms=sum(not r['correct'] and control[r['item_id']]['correct'] for r in rs)) for v,control in controls.items()}))
    assert len(all_rows)==680*7*4
    write(OUT/'scored.jsonl',all_rows);write(OUT/'predictions_new_methods.jsonl',predictions);dump(OUT/'interface_replay.json',replay)
    dump(OUT/'summary.json',dict(status='complete_exposed_seven_method_expansion',results=results,costs=costs,
         new_calls=sum(c['new_calls'] for c in costs),reused_m0_scores=sum(c['reused_m0_scores'] for c in costs),
         reused_other_methods_initial40_calls=1200,reused_m4_m5_patient_calls=8160,reused_prior_calls=126,
         scope='680 exposed v5 diagnoses and native final contexts for each of seven methods. New calls are terminal head scores only; no independent generalization.',
         runtime=[json.loads(p.read_text()) for p in sorted(OUT.glob('runtime_gpu*.json'))]))
    for method in ALL_METHODS:
        print(method,[(r['variant'],r['correct'],round(r['macro_recall'],4),r['comparisons']['uncalibrated_majority']) for r in results if r['method']==method and r['scope']=='all680'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','run','worker','analyze'))
    p.add_argument('--gpu',type=int);p.add_argument('--method',choices=METHODS);p.add_argument('--methods',nargs='+',choices=METHODS);a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='run':run(a.gpu,a.methods)
    elif a.action=='worker':run_scores(a.method,a.gpu,OUT/a.method.lower())
    else:analyze()
