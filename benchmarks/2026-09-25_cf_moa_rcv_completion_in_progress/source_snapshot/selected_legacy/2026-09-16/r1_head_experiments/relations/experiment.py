"""Same-model, same-context relation redecision with two targeted prompt controls."""
import argparse
import gzip
import json
import os
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
OLD = OUT.parents[2] / '2026-09-14/new-chat'
sys.path.insert(0, str(OLD))
from r3_audit import BASE, M4, PACK, read, write, dump
from r3_catalog_distribution_pilot import EXTRA_SITE

ARMS = ('redo', 'evidence_scope', 'target_scope')
CONTEXT_ARMS = ('no_draft', 'supplied_only')
COMMON = ('Answer the question again using the material above. Give a brief explanation and '
          'return the original JSON format with step_by_step_thinking and answer_choice. '
          'answer_choice must be higher, lower, no difference, or uncertainty.')
EVIDENCE = ('For this hypothetical evidence-comparison task, use the section labeled '
            '"Evidence supplied with the question" as the supplied study evidence for the '
            'named comparison. Other retrieved documents may clarify terminology, but do not '
            'replace the named intervention, population, or study findings with unrelated '
            'real-world treatments. An unfamiliar intervention name is not by itself missing '
            'evidence. Read all supplied studies relevant to the question.')
TARGET = ('Identify the first intervention A, comparator B, requested outcome, population and '
          'time point. Judge A relative to B, not B relative to A. Bind each quoted number and '
          'effect estimate to that exact outcome and group; do not substitute another outcome, '
          'a composite endpoint, another follow-up time, or an unrequested subgroup. Explain '
          'the overall comparison supported by the relevant studies, distinguishing no '
          'difference from insufficient or conflicting evidence. Ensure the final direction '
          'matches the comparison described in your explanation.')


def request(messages, question, original, arm):
    extra = COMMON
    if arm in ('evidence_scope', 'target_scope'):
        extra += '\n\n'+EVIDENCE
    if arm == 'target_scope':
        extra += '\n\n'+TARGET
    return [*messages, {'role':'assistant', 'content':original},
            {'role':'user', 'content':extra+'\n\nQuestion: '+question}]


def scoring():
    sys.path.insert(0, str(M4/'code'))
    from analyze_v5 import objects
    sys.path.insert(0, str(PACK/'scripts'))
    from analyze_cf_baseline_screening import score
    return objects, score


def prepare():
    assert not (OUT/'plan.json').exists()
    items = {r['item_id']:r for r in read(BASE/'items.jsonl')}
    evaluation = {r['item_id']:r for r in read(BASE/'evaluation.jsonl')
                  if r['resource_id']=='M20' and 'R1' in r['evaluation_labels'] and r['role']!='reference'}
    groups = defaultdict(list)
    for iid, e in evaluation.items():
        groups[e['group_id']].append(iid)
    # Same prospective pilot for all arms and both models; no selection by new predictions.
    rng = random.Random(20260916)
    by_gold = defaultdict(list)
    for gid, ids in sorted(groups.items()):
        assert len({evaluation[i]['gold'] for i in ids}) == 1
        by_gold[evaluation[ids[0]]['gold']].append(gid)
    pilot = set()
    for label, count in [('higher',21), ('lower',21), ('no difference',22)]:
        for gid in rng.sample(by_gold[label],count):
            pilot.add(rng.choice(sorted(groups[gid])))
    assert len(pilot)==64
    audit_groups = {r['evaluation']['group_id'] for r in read(OUT/'audit_cases.jsonl')}
    write(OUT/'split.jsonl', [dict(item_id=i, group_id=e['group_id'],
         split='pilot' if i in pilot else 'remaining', audit_group=e['group_id'] in audit_groups,
         pilot_group=e['group_id'] in {evaluation[x]['group_id'] for x in pilot}) for i,e in sorted(evaluation.items())])
    write(OUT/'evaluation.jsonl',evaluation.values())
    m4_context = {}
    for path in sorted((M4/'inputs').glob('*.jsonl')):
        m4_context.update({r['item']['item_id']:r for r in read(path) if r['item']['item_id'] in evaluation})
    with gzip.open(BASE/'M5/prompts.jsonl.gz','rt') as stream:
        m5_context = {r['item_id']:r for line in stream if (r:=json.loads(line))['item_id'] in evaluation}
    objects, score = scoring()
    sys.path.insert(0,EXTRA_SITE)
    from transformers import AutoTokenizer
    summary = []
    for method in ('M4','M5'):
        directory = OUT/method.lower();directory.mkdir(exist_ok=True)
        scorefile = M4/'scores/scored.jsonl' if method=='M4' else BASE/'scored.jsonl'
        predfile = M4/'M4/predictions.jsonl' if method=='M4' else BASE/'M5/predictions.jsonl'
        baseline = {r['item_id']:r for r in read(scorefile) if r['item_id'] in evaluation and r['method']==method and r['role']!='reference'}
        predictions = {r['item_id']:r for r in read(predfile) if r['item_id'] in evaluation}
        contexts = m4_context if method=='M4' else m5_context
        assert contexts.keys()==predictions.keys()==baseline.keys()==evaluation.keys()
        cfg = json.loads((OLD/'r3_knowledge_utility'/method.lower()/'config.json').read_text())
        cfg.update(temperature=.7,max_tokens=2048,guided_json=method=='M4',max_model_len=131072,
                   gpu_memory_utilization=.95,max_num_seqs=4,max_num_batched_tokens=4096,batch_size=4)
        cfg['model_kwargs']['num_gpu_blocks_override']=8192
        cfg.pop('max_logprobs',None)
        tok=AutoTokenizer.from_pretrained(cfg['model'],local_files_only=True)
        inputs=[];jobs=[];lengths=[]
        for iid in sorted(evaluation):
            item=items[iid];original=predictions[iid]['raw_response'];obj=objects(original,'answer_choice')
            native=json.dumps({'answer':obj['answer_choice']}) if obj else ''
            result=score({'raw_response':native},evaluation[iid],item,{})
            assert all(result[k]==baseline[iid][k] for k in ('correct','invalid','invalid_reason')),(method,iid)
            messages=contexts[iid]['messages']
            assert item['question'] in messages[-1]['content']
            assert all(e in messages[-1]['content'] for e in item['fixed_evidence'])
            inputs.append(dict(item=item,messages=messages,original_response=original))
            for arm in ARMS:
                req=request(messages,item['question'],original,arm)
                assert req[:len(messages)]==messages
                prompt=tok.apply_chat_template(req,tokenize=False,add_generation_prompt=True,**cfg.get('chat_template_kwargs',{}))
                length=len(tok.encode(prompt,add_special_tokens=False));lengths.append(length)
                jobs.append(dict(item_id=iid,arm=arm,prompt=prompt,
                                 schema=m4_context[iid]['schema'],prompt_tokens=length))
        assert max(lengths)+cfg['max_tokens']<=cfg['max_model_len']
        write(directory/'inputs.jsonl',inputs);write(directory/'baseline_scored.jsonl',baseline.values())
        write(directory/'pilot_requests.jsonl',[r for r in jobs if r['item_id'] in pilot])
        write(directory/'remaining_requests.jsonl',[r for r in jobs if r['item_id'] not in pilot])
        dump(directory/'config.json',cfg)
        summary.append(dict(method=method,baseline_parity=len(inputs),max_prompt_tokens=max(lengths),
                            baseline_correct=sum(r['correct'] for r in baseline.values()),
                            original_truncated=sum(r.get('context_truncated_tokens',0)>0 for r in predictions.values()),
                            pilot_calls=64*len(ARMS)))
    dump(OUT/'plan.json',dict(status='prepared',seed=20260916,scope='788 exposed v5 relation tasks; 201 source groups',
         arms=list(ARMS),pilot=64,pilot_source_groups=64,checks=summary,
         interpretation='Pilot is gold-stratified; all v5 is development. Remaining items include variants from pilot/audit groups and are not independent validation.',
         hypotheses='Retrieved/supplied evidence role confusion; target/outcome/group orientation confusion. Same complete original context, original answer and native decoding in all arms.',
         inputs='No gold, paired reference, replacement metadata or source labels in generated requests.',
         errors='All invalid/length-stop outputs count as errors under frozen native scoring; no silent fallback or label removal.'))
    print(json.dumps(summary),flush=True)


def run_model(method,gpu,stage,arms):
    assert os.environ['CUDA_VISIBLE_DEVICES']==str(gpu)
    directory=OUT/method.lower();cfg=json.loads((directory/'config.json').read_text())
    target=directory/(stage+'_raw.jsonl')
    jobs=[r for r in read(directory/(stage+'_requests.jsonl')) if r['arm'] in arms]
    saved=list(read(target)) if target.exists() else []
    assert [(r['item_id'],r['arm']) for r in saved]==[(r['item_id'],r['arm']) for r in jobs[:len(saved)]]
    assert len(saved)<len(jobs) and len(saved)%cfg['batch_size']==0
    previous=json.loads((directory/(stage+'_runtime.json')).read_text()) if saved else {}
    previous_seconds=previous.get('elapsed_seconds',0)
    sys.path.insert(0,EXTRA_SITE)
    from vllm import LLM,SamplingParams
    from vllm.sampling_params import GuidedDecodingParams
    start=time.time();status=dict(status='loading',pid=os.getpid(),gpu=gpu,method=method,stage=stage,arms=arms,completed=len(saved),planned=len(jobs),
        resumed_prefix_calls=len(saved),previous_logged_elapsed_seconds=previous_seconds,
        previous_initialization_seconds=previous.get('initialization_seconds',0))
    dump(directory/(stage+'_runtime.json'),status)
    llm=LLM(model=cfg['model'],seed=cfg['seed'],**{k:cfg[k] for k in ('dtype','gpu_memory_utilization','max_model_len','max_num_seqs','max_num_batched_tokens')},
            **cfg['model_kwargs'],enable_prefix_caching=True,enable_chunked_prefill=True,enforce_eager=True,guided_decoding_backend='xgrammar')
    status['initialization_seconds']=time.time()-start
    for pos in range(len(saved),len(jobs),cfg['batch_size']):
        batch=jobs[pos:pos+cfg['batch_size']]
        params=[SamplingParams(**{k:cfg[k] for k in ('seed','temperature','top_p','top_k','max_tokens')},
                 guided_decoding=GuidedDecodingParams(json=r['schema'],backend='xgrammar') if cfg['guided_json'] else None) for r in batch]
        before=time.time();outputs=llm.generate([r['prompt'] for r in batch],params,use_tqdm=False);elapsed=time.time()-before
        with target.open('a') as f:
            for job,result in zip(batch,outputs):
                answer=result.outputs[0]
                f.write(json.dumps(dict(item_id=job['item_id'],arm=job['arm'],raw_response=answer.text,
                    prompt_tokens=len(result.prompt_token_ids),completion_tokens=len(answer.token_ids),
                    finish_reason=answer.finish_reason,batch_seconds=elapsed,batch_size=len(batch)),ensure_ascii=False)+'\n')
        status.update(status='running',completed=pos+len(batch),elapsed_seconds=previous_seconds+time.time()-start,
                      attempt_elapsed_seconds=time.time()-start,new_durable_calls=pos+len(batch)-len(saved))
        dump(directory/(stage+'_runtime.json'),status);print(json.dumps(status),flush=True)
    status.update(status='complete',elapsed_seconds=previous_seconds+time.time()-start,
                  attempt_elapsed_seconds=time.time()-start);dump(directory/(stage+'_runtime.json'),status)


def prepare_group_extension():
    """One variant per remaining source group, fixed before pilot arm selection."""
    path = OUT / 'group_extension_plan.json'
    assert not path.exists()
    split = list(read(OUT / 'split.jsonl'))
    groups = defaultdict(list)
    for row in split:
        if not row['pilot_group']:
            groups[row['group_id']].append(row['item_id'])
    rng = random.Random(20260917)
    selected = {rng.choice(sorted(ids)) for _, ids in sorted(groups.items())}
    assert len(selected) == len(groups) == 137
    for method in ('M4', 'M5'):
        directory = OUT / method.lower()
        jobs = [r for r in read(directory / 'remaining_requests.jsonl') if r['item_id'] in selected]
        assert len(jobs) == 137 * len(ARMS)
        write(directory / 'extension_requests.jsonl', jobs)
    dump(path, dict(status='prepared_before_pilot_arm_selection', seed=20260917,
        item_ids=sorted(selected), source_groups=len(groups), prepared_arms=list(ARMS),
        actual_arms='Choose one common candidate plus redo after both-model pilot; record before running.',
        interpretation='One case from each of 137 source groups outside the 64-group pilot; all v5 already exposed development, not independent generalization. No full788 replacement score from this sample.',
        reason='Test transfer beyond pilot groups without repeatedly evaluating multiple name variants from the same study.'))


def prepare_context(stage):
    assert stage in ('context', 'context_extension')
    path = OUT / (stage + '_plan.json')
    assert not path.exists()
    selected_ids = ({r['item_id'] for r in read(OUT / 'split.jsonl') if r['split'] == 'pilot'}
                    if stage == 'context' else set(json.loads((OUT / 'group_extension_plan.json').read_text())['item_ids']))
    sys.path.insert(0, EXTRA_SITE)
    from transformers import AutoTokenizer
    checks = []
    for method in ('M4', 'M5'):
        directory = OUT / method.lower()
        cfg = json.loads((directory / 'config.json').read_text())
        tok = AutoTokenizer.from_pretrained(cfg['model'], local_files_only=True)
        schemas = {r['item_id']: r['schema'] for split in ('pilot', 'remaining')
                   for r in read(directory / (split + '_requests.jsonl'))}
        jobs = []
        for row in read(directory / 'inputs.jsonl'):
            item = row['item']; iid = item['item_id']
            if iid not in selected_ids:
                continue
            messages = row['messages']
            assert [m['role'] for m in messages] == ['system', 'user']
            content = messages[-1]['content']
            assert content.count('Here is the question:') == 1
            task = content[content.index('Here is the question:'):]
            assert item['question'] in task and all(e in task for e in item['fixed_evidence'])
            extra = COMMON + '\n\n' + EVIDENCE + '\n\n' + TARGET + '\n\nQuestion: ' + item['question']
            for arm in CONTEXT_ARMS:
                selected = messages if arm == 'no_draft' else [messages[0], dict(role='user', content=task)]
                req = [*selected, dict(role='user', content=extra)]
                prompt = tok.apply_chat_template(req, tokenize=False, add_generation_prompt=True,
                                                **cfg.get('chat_template_kwargs', {}))
                length = len(tok.encode(prompt, add_special_tokens=False))
                jobs.append(dict(item_id=iid, arm=arm, prompt=prompt,
                                 schema=schemas[iid], prompt_tokens=length))
        assert len(jobs) == len(selected_ids) * 2 and max(r['prompt_tokens'] for r in jobs) + cfg['max_tokens'] <= cfg['max_model_len']
        write(directory / (stage + '_requests.jsonl'), jobs)
        checks.append(dict(method=method, calls=len(jobs), max_prompt_tokens=max(r['prompt_tokens'] for r in jobs)))
    dump(path, dict(status='prepared_not_run', sample=('same64 exposed pilot cases' if stage == 'context' else 'one fixed variant from each137 source groups outside pilot'), arms=list(CONTEXT_ARMS),
        checks=checks, planned_calls=len(selected_ids) * 4, item_ids=sorted(selected_ids),
        motivation='First three-arm pilot did not improve both backbones. Qwen redo/evidence_scope repaired0, target_scope repaired2/harmed4; distinguish anchoring on appended draft from retrieved/supplied evidence role confusion.',
        controls='Same target_scope instructions, original system instructions, decoding and strict native scoring. no_draft keeps all original context; supplied_only retains the exact original question-to-end block, including every fixed_evidence passage and original output instructions. Neither adds the original answer.',
        literature='Given-evidence input organization from the MedCounterFact source study; this is a local original-backbone adaptation, not released author inference code.',
        permissions='Only actual original context and current native task fields; no reference case, replacement metadata, source label, gold or edited medical evidence.',
        selection='Same two context arms on both backbones; no per-method or per-item choice of the best output. Previous draft-prompt version is not selected. Context extension follows the preselected seed20260917 source-group list and is exposed development, not independent generalization.'))


def analyze(stage):
    objects,score=scoring();evaluation={r['item_id']:r for r in read(OUT/'evaluation.jsonl')};summaries=[]
    for method in ('M4','M5'):
        directory=OUT/method.lower();items={r['item']['item_id']:r['item'] for r in read(directory/'inputs.jsonl')}
        base={r['item_id']:r for r in read(directory/'baseline_scored.jsonl')}
        raw=list(read(directory/(stage+'_raw.jsonl')))
        status=json.loads((directory/(stage+'_runtime.json')).read_text())
        assert status['status']=='complete' and len(raw)==status['planned']
        assert len(raw)==len({(r['item_id'],r['arm']) for r in raw})
        scored=[]
        for r in raw:
            obj=objects(r['raw_response'],'answer_choice');answer=obj['answer_choice'] if obj else None
            native=json.dumps({'answer':answer}) if obj else ''
            scored.append(dict(item_id=r['item_id'],arm=r['arm'],answer=answer,
                          **score({'raw_response':native},evaluation[r['item_id']],items[r['item_id']],{})))
        lookup={(r['item_id'],r['arm']):r for r in scored};results=[]
        control_arm = 'redo' if 'redo' in status['arms'] else 'no_draft'
        for arm in status['arms']:
            rows=[r for r in scored if r['arm']==arm]
            results.append(dict(arm=arm,n=len(rows),correct=sum(r['correct'] for r in rows),invalid=sum(r['invalid'] for r in rows),
                baseline_correct=sum(base[r['item_id']]['correct'] for r in rows),
                predictions=dict(Counter(str(r['prediction']) for r in rows)),
                repairs=sum(r['correct'] and not base[r['item_id']]['correct'] for r in rows),
                harms=sum(not r['correct'] and base[r['item_id']]['correct'] for r in rows),
                **{f'vs_{control_arm}':dict(repairs=sum(r['correct'] and not lookup[r['item_id'],control_arm]['correct'] for r in rows),
                             harms=sum(not r['correct'] and lookup[r['item_id'],control_arm]['correct'] for r in rows))},
                classes={g:dict(n=sum(evaluation[r['item_id']]['gold']==g for r in rows),correct=sum(r['correct'] and evaluation[r['item_id']]['gold']==g for r in rows)) for g in ('higher','lower','no difference')}))
        write(directory/(stage+'_scored.jsonl'),scored)
        summaries.append(dict(method=method,results=results,calls=len(raw),input_tokens=sum(r['prompt_tokens'] for r in raw),
             output_tokens=sum(r['completion_tokens'] for r in raw),length_stops=sum(r['finish_reason']=='length' for r in raw),runtime=status))
    dump(OUT/(stage+'_summary.json'),summaries);print(json.dumps(summaries,ensure_ascii=False,indent=2))


def run_queue(gpu,stage,arms):
    for method in ('M4','M5'):
        log=OUT/method.lower()/(stage+'_gpu.log')
        assert not log.exists()
        with log.open('w') as stream:
            subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'run_model',
                '--method',method,'--gpu',str(gpu),'--stage',stage,'--arms',*arms],
                stdout=stream,stderr=subprocess.STDOUT,check=True)
    analyze(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','prepare_extension','prepare_context','run','run_model','analyze'))
    p.add_argument('--method',choices=('M4','M5'));p.add_argument('--gpu',type=int,default=0)
    p.add_argument('--stage',choices=('pilot','remaining','extension','context','context_extension'),default='pilot');p.add_argument('--arms',nargs='+',choices=ARMS+CONTEXT_ARMS,default=list(ARMS))
    args=p.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='prepare_extension':prepare_group_extension()
    elif args.action=='prepare_context':prepare_context(args.stage)
    elif args.action=='run':run_queue(args.gpu,args.stage,args.arms)
    elif args.action=='run_model':run_model(args.method,args.gpu,args.stage,args.arms)
    else:analyze(args.stage)
