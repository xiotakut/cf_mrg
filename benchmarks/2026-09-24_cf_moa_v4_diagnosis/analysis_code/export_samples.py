"""One-off v4 saved-trigger export; stdlib only, no model/head/scorer imports."""
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROOT=Path('/home/data3/txy')
HERE=Path(__file__).resolve().parent
V4=ROOT/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
OLD=ROOT/'Documents/Codex/2026-09-21/cf_moa'
CYCLE1=OLD/'effect_first_revision_20260923/a5_quality121'
R5=ROOT/'Documents/Codex/2026-09-18/r5_head'
DEV=OLD/'cpu_preparation/development'
SOURCES={}

@lru_cache(None)
def sha(path):
    path=Path(path)
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def source(path):
    path=Path(path)
    SOURCES[str(path)]={'sha256':sha(str(path)), 'bytes':path.stat().st_size}
    return str(path)

@lru_cache(None)
def obj(path):
    source(path)
    return json.loads(Path(path).read_text())

@lru_cache(None)
def indexed(path):
    source(path)
    result=[]
    with Path(path).open('rb') as stream:
        for i,line in enumerate(stream,1):
            if line.strip(): result.append((json.loads(line),{'path':str(path),'line':i,'line_sha256':hashlib.sha256(line).hexdigest()}))
    return result

def rows(path):return [r for r,_ in indexed(str(path))]

def chosen(path,predicate):return [{'record':r,'source':s} for r,s in indexed(str(path)) if predicate(r)]

def one(path,predicate):
    found=chosen(path,predicate)
    assert len(found)==1, (str(path),len(found))
    return found[0]

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert json.loads(path.read_text())==value, ('nonidentical existing export',str(path))
        return
    with path.open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')

def forbidden(value,path=''):
    if isinstance(value,dict):
        for key,child in value.items():
            assert key not in {'gold','semantic_gold','evaluation_labels','judgment_ids','scoring_eligible'},(path,key)
            forbidden(child,path+'/'+key)
    elif isinstance(value,list):
        for index,child in enumerate(value):forbidden(child,path+'/'+str(index))


def natural_callbacks(method,item_id,ftrace):
    events=chosen(R5/'delivery/callback_trace.jsonl',lambda r:r['method']==method and r['item_id']==item_id)
    events.sort(key=lambda x:x['record']['callback_index'])
    exported=[]; score_index=0;missing=Counter()
    for wrapped in events:
        event=wrapped['record'];kind=event['kind'];cache=Path(event['cache_file'])
        def eligible(r):return r['item_id']==item_id and r['seed']==event['cache_seed']
        if kind=='vote':
            arm='draw'+str(event['cache_seed']-42)
            criterion=lambda r:eligible(r) and r.get('arm')==arm
        elif kind=='score':
            stage='direct' if score_index<2 else 'reasoned';order=score_index%2;score_index+=1
            criterion=lambda r:eligible(r) and r.get('stage')==stage and r.get('order')==order
        elif kind=='analysis':
            criterion=lambda r:eligible(r) and r.get('stage')=='analysis'
        elif kind=='completion':
            arm='equal_path' if event['stage']=='nli_validation' else 'head'
            criterion=lambda r:eligible(r) and r.get('arm')==arm
        else:raise ValueError(kind)
        raw=chosen(cache,criterion)
        assert raw,(cache,item_id,kind)
        # Scoring can have original missing-code fetches. Preserve every matching
        # physical raw record; never sum them as independent semantic votes.
        reqpath=cache.with_name('requests.jsonl')
        requests=chosen(reqpath,criterion) if reqpath.exists() else []
        if not requests:
            # The old reasoned NLI phase appended request fields only to its raw log.
            assert all('messages' in r['record'] and 'prompt' in r['record'] for r in raw)
            requests=[{'record':{k:v for k,v in r['record'].items() if k in ('item_id','stage','order','seed','messages','prompt','prompt_tokens','schema')},
                       'source':r['source'],'request_fields_saved_in_raw_record':True} for r in raw]
        for entry in raw+requests:
            record=entry['record']
            if 'engine_prompt_token_ids' not in record:missing['engine_prompt_token_ids_not_saved']+=1
        if kind=='vote':
            assert len(raw)==1
            assert raw[0]['record']['raw_response']==ftrace['responses'][event['cache_seed']-42]
        elif kind=='analysis':assert raw[0]['record']['raw_response']==ftrace['decision']['analysis']
        elif kind=='completion':assert raw[0]['record']['raw_response']==ftrace['raw_response']
        elif kind=='score':
            actual={}
            for r in raw:actual.update(r['record']['code_logprobs'])
            assert actual==ftrace['decision']['code_logprobs'][score_index-1]
        configpath=cache.with_name('config.json')
        config={'record':obj(str(configpath)),'source_path':str(configpath)} if configpath.exists() else None
        exported.append({'callback':wrapped,'saved_requests':requests,'saved_raw_records':raw,'saved_config':config,
            'availability':{'serialized_prompt':'saved in requests, verbatim',
                'messages':'saved' if all('messages' in r['record'] for r in requests) else 'not separately saved for this old callback; original_context and actual complete serialized prompt are retained',
                'prompt_token_ids':'not saved; no reconstructed IDs presented as actual',
                'exclusive_latency':'not saved; batch_seconds and batch_size retained where recorded'}})
    assert len(events)==ftrace['calls']
    return {'mode':'existing_old_F_callback_binding_no_replay',
        'saved_output':one(R5/'delivery/outputs.jsonl',lambda r:r['method']==method and r['item_id']==item_id),
        'callbacks':exported,'logging_limitations':dict(missing)}


def main():
    oldplan=obj(str(V4/'seeds/seed_43/plan.json'))
    naturalplan=obj(str(V4/'natural_scope/plan_seed_42.json'))
    oldtriggers=obj(str(V4/'seeds/preparation_receipt.json'))['methods']
    naturalaudit=rows(V4/'natural_scope/cache_reuse_audit.jsonl')
    allmanifest=[]; call_count=Counter(); fcallback_count=Counter(); fphysical_count=Counter(); sample_bytes=0
    for panel,plan,expected in [('historical121',oldplan,{'M4':28,'M5':26}),('natural52',naturalplan,{'M4':25,'M5':16})]:
        evalpath=(DEV if panel=='historical121' else V4/'natural_scope')/'offline/evaluations.jsonl'
        itempath=(DEV if panel=='historical121' else V4/'natural_scope')/'offline/items.jsonl'
        evaluations=rows(evalpath); items=rows(itempath)
        scorepath=V4/'analysis'/panel/'native_scored.jsonl';statepath=V4/'analysis'/panel/'per_input_status.jsonl'
        for method in ('M4','M5'):
            spec=plan['methods'][method];lower=method.lower()
            ids=oldtriggers[method]['trigger_ids'] if panel=='historical121' else [r['request_id'] for r in naturalaudit if r['method']==method and r['trigger']]
            assert len(ids)==expected[method]
            for rid in ids:
                packet=one(spec['inputs'],lambda r:r['request_id']==rid)
                base=one(spec['bases'],lambda r:r['request_id']==rid)
                proposal=one(spec['proposals'],lambda r:r['proposal_key']==rid+':F')
                ftrace=proposal['record']['proposal']['trace']
                ownitems=[x for x in items if x['request_id']==rid]; assert len(ownitems)==1
                iid=ownitems[0]['item_id']
                evaluations_here=chosen(evalpath,lambda r:r['request_id']==rid)
                if panel=='historical121':
                    fpath=Path(base['record']['source_proof']['component_source']['path'])
                    fresult=one(fpath,lambda r:r['request_id']==rid)
                    assert fresult['record']['proposal']['trace']==ftrace
                    fcalls=chosen(fpath.with_name('model_calls.jsonl'),lambda r:r['request_id']==rid)
                    assert len(fcalls)==ftrace['calls'],(rid,len(fcalls),ftrace['calls'])
                    fexec={'mode':'saved_actual_20260921_F_journal_export','saved_output':fresult,'model_calls':fcalls,
                           'saved_plan':{'record':obj(str(fpath.with_name('plan.json'))),'source_path':str(fpath.with_name('plan.json'))}}
                    fphysical_count[panel,method]+=sum(len(c['record']['physical']) for c in fcalls)
                else:
                    fexec=natural_callbacks(method,iid,ftrace)
                    fphysical_count[panel,method]+=sum(e['callback']['record']['actual_cached_model_requests'] for e in fexec['callbacks'])
                fcallback_count[panel,method]+=ftrace['calls']
                reanswers={}
                for seed in (42,43,44):
                    directory=(CYCLE1/lower if seed==42 else V4/'seeds'/f'seed_{seed}'/lower) if panel=='historical121' else V4/'natural_runs'/f'seed_{seed}'/lower
                    out=one(directory/'proposals.jsonl',lambda r:r['request_id']==rid and r['arm']=='a5_reanswer')
                    calls=chosen(directory/'model_calls.jsonl',lambda r:r['request_id']==rid+':a5_reanswer')
                    assert len(calls)==1,(panel,method,rid,seed,len(calls))
                    assert calls[0]['record']['request']['seed']==seed
                    assert out['record']['status']=='complete' and out['record']['result']['native_valid']
                    reanswers[str(seed)]={'output':out,'model_calls':calls,
                        'run_profile':{'record':obj(str(directory/'plan.json')),'source_path':str(directory/'plan.json')},
                        'provenance':'historical_cycle1_seed42' if panel=='historical121' and seed==42 else 'v4_saved_run',
                        'no_new_call_during_export':True}
                    call_count[panel,method,seed]+=len(calls)
                # Offline administrative source/family/gold metadata is separate.
                # Removing source_proof from the online view does not change the
                # saved base native response; complete base row is kept offline.
                base_online=dict(base['record']);base_online.pop('source_proof',None)
                sample={'sample_id':f'{panel}:{method}:{rid}','panel':panel,'method':method,'request_id':rid,
                    'input_packet':packet,'base_result':{'record':base_online,'source':base['source']},
                    'f_proposal':proposal,'f_original_execution':fexec,'reanswers':reanswers,
                    'trigger':{'actual_triggered':True,'competitors':reanswers['42']['output']['record']['result']['trace'].get('competitors'),
                               'saved_original_trigger_trace':reanswers['42']['output']['record']['result']['trace']},
                    'boundaries':{'new_model_calls':0,'new_head_replay_callbacks':0,'new_native_scoring_calls':0,
                        'early_stopped_F_paths_not_generated':True,'gold_and_quality':'separate offline file',
                        'actual_messages_or_prompt':'copied from saved records; absent fields explicitly unavailable'}}
                # Source paths/IDs in original logs are provenance, never injected
                # into request.messages or physical.prompt by this exporter.
                forbidden(sample)
                spath=HERE/'samples'/panel/f'{method}_{rid}.json';opath=HERE/'offline'/panel/f'{method}_{rid}.json'
                write(spath,sample)
                offline={'sample_id':sample['sample_id'],'item_id':iid,'item_record':one(itempath,lambda r:r['request_id']==rid),
                    'evaluations':evaluations_here,'native_scores':chosen(scorepath,lambda r:r['method']==method and r['request_id']==rid),
                    'per_input_states':chosen(statepath,lambda r:r['method']==method and r['request_id']==rid),
                    'complete_base_source_record':base,
                    'use':'offline diagnosis only; never an inference request or online selection rule'}
                assert len(offline['per_input_states'])==4
                write(opath,offline);sample_bytes+=spath.stat().st_size+opath.stat().st_size
                allmanifest.append({'sample_id':sample['sample_id'],'panel':panel,'method':method,'request_id':rid,
                    'sample_path':str(spath.relative_to(HERE)),'sample_sha256':sha(str(spath)),'sample_bytes':spath.stat().st_size,
                    'offline_path':str(opath.relative_to(HERE)),'offline_sha256':sha(str(opath)),'offline_bytes':opath.stat().st_size,
                    'f_route':ftrace['route'],'actual_F_callbacks':ftrace['calls'],'reanswer_seeds':[42,43,44]})
    assert len(allmanifest)==95 and sum(call_count.values())==285
    manifest={'version':'v4_all95_saved_trigger_export_v1','created_at':datetime.now().astimezone().isoformat(),
       'private_local_only':True,'new_model_calls':0,'new_head_replay_callbacks':0,'new_native_scoring_calls':0,
       'complete_trigger_scope':{'historical121':{'M4':28,'M5':26},'natural52':{'M4':25,'M5':16}},
       'samples':allmanifest,'source_files':SOURCES,
       'scope_limit':'Trigger subset for cause diagnosis. Full121/52 denominators remain in original reports; not replaced by this subset.'}
    write(HERE/'sample_manifest.json',manifest)
    receipt={'status':'passed_saved_records_only','sample_count':95,'sample_json_files':95,'offline_json_files':95,
        'sample_and_offline_bytes':sample_bytes,'saved_reanswer_logical_calls':285,'old_seed42_calls':54,'v4_new_calls_reused':231,
        'counts':{':'.join(map(str,k)):v for k,v in call_count.items()},
        'old_F_callbacks':{':'.join(k):v for k,v in fcallback_count.items()},
        'old_F_physical_requests':{':'.join(k):v for k,v in fphysical_count.items()},
        'new_model_calls':0,'new_head_replay_callbacks':0,'new_native_scoring_calls':0,
        'all_triggered_have_three_seeds':True,'all_native_answers_valid':True,'gold_separated':True,
        'actual_request_response_fields_copied_not_regenerated':True,
        'preparation_error_retained':'samples/_preparation/attempt1_error.txt',
        'logging_limits':['Old natural F logs save complete serialized prompts but vote messages and engine token IDs were not separately retained. No reconstructed fields are presented as actual.',
          'Old natural F timing is shared batch time, not exclusive per-request latency.',
          'Callbacks count semantic callbacks; saved missing-code fetch physical rows retained separately where present.'],
        'manifest_sha256':sha(str(HERE/'sample_manifest.json')),'export_script_sha256':sha(str(Path(__file__)))}
    write(HERE/'export_receipt.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
def verify_export():
    """Check saved values directly. Do not import request builders/parsers/heads."""
    manifest=json.loads((HERE/'sample_manifest.json').read_text())
    counts=Counter();token_totals=Counter();limits=Counter()
    for entry in manifest['samples']:
        spath=HERE/entry['sample_path'];opath=HERE/entry['offline_path']
        assert sha(str(spath))==entry['sample_sha256'] and sha(str(opath))==entry['offline_sha256']
        x=json.loads(spath.read_text());packet=x['input_packet']['record'];f=x['f_proposal']['record']['proposal']
        base=f['native_proposal'];format_=packet['native_input']['answer_format']
        nativekeys=list(packet['native_input'].get('options') or {})
        if format_=='relation':nativekeys=['higher','lower','no difference','uncertainty']
        trace=f['trace']
        observed=(trace['decision']['direct']['per_order']+trace['decision']['reasoned']['per_order']) if 'decision' in trace else trace['predictions']
        expected_competing=[k for k in nativekeys if k in observed]
        assert len(expected_competing)>1
        counts['95_trigger_semantic_keys_equal']+=1
        for seed,wrapped in x['reanswers'].items():
            call=wrapped['model_calls'][0]['record'];request=call['request'];result=wrapped['output']['record']['result']
            prior=packet['original_context']
            if isinstance(prior,str):prior=[{'role':'user','content':prior}]
            assert request['messages'][:-1]==prior
            last=request['messages'][-1]['content']
            data=json.loads(last[last.index('\n{')+1:])
            assert data=={'current_native_input':packet['native_input'],'retrieved_context':packet['retrieved_context'],'model_input':packet['model_input']}
            assert result['trace']['competing_keys']==expected_competing
            raw=call['result']['value'];parsed=json.loads(raw)
            assert parsed['answer_choice']==result['trace']['attempts'][0]['answer_choice']==result['native_answer']['answer_choice']
            assert parsed['answer_choice'] in nativekeys
            auxiliary={k:v for k,v in base.items() if k not in ('answer_choice','step_by_step_thinking')}
            assert {k:v for k,v in result['native_answer'].items() if k not in ('answer_choice','step_by_step_thinking')}==auxiliary
            assert sorted(result['trace']['retained_auxiliary_fields'])==sorted(auxiliary)
            assert result['trace']['attempts'][0]['raw_response']==raw
            assert len(wrapped['output']['record']['model_callbacks'])==1
            for name in ['original_context_prefix_equal','current_input_context_payload_equal','native_key_mapping_equal','parsed_key_equals_final_native','auxiliary_values_retained_equal','raw_response_equals_saved_parser_input']:
                counts[name]+=1
            counts['auxiliary_present']+=bool(auxiliary)
            for event in call['result']['events']:
                assert event['mode']=='live'
                token_totals['saved_reanswer_input_tokens']+=event['input_tokens']
                token_totals['saved_reanswer_output_tokens']+=event['output_tokens']
                counts['finish_reason_'+str(event.get('finish_reason','unknown'))]+=1
            for physical in call['physical']:
                counts['reanswer_physical_prompt_token_ids_saved']+=bool(physical.get('engine_prompt_token_ids'))
            if x['panel']=='natural52':
                for callback in x['f_original_execution']['callbacks']:
                    limits['natural_F_callback_entries_once_per_seed']+=1
    assert counts['original_context_prefix_equal']==285
    path=HERE/'export_receipt.json';receipt=json.loads(path.read_text())
    receipt['direct_saved_value_verification']={'status':'passed','checks':dict(counts),'token_totals':dict(token_totals),
        'zero_request_builder_or_parser_calls':True,'source_manifest_and_sample_hashes_verified':True,
        'auxiliary_count_interpretation':'Count includes three saved seeds per qualifying question-backbone; absent auxiliary is not an error.'}
    receipt['export_script_sha256']=sha(str(Path(__file__)))
    path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt['direct_saved_value_verification'],ensure_ascii=False,indent=2))

if __name__=='__main__':
    import sys
    if sys.argv[1:]==['--verify']:verify_export()
    else:main();verify_export()

