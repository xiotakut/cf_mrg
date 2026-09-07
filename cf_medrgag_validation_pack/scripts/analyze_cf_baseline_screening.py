#!/usr/bin/env python3
"""Offline native-task metrics; no model imports or judge calls."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import difflib
import json
import gzip
import shutil
from pathlib import Path
import re
import time

import numpy as np
from scipy.stats import binomtest
from prepare_cf_baseline_screening import OUT, ROOT, read, write, norm

METHODS={'M0':'direct_llama','M1':'retrieval_only_llama','M2':'medrgag_llama_base'}
if (OUT/'method_scope.json').exists():
    METHODS={m:METHODS[m] for m in json.loads((OUT/'method_scope.json').read_text())['methods']}

def ratio(a,b):return a/b if b else None

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def table(name,rows):
    if not rows:
        (OUT/name).write_text('status\nunavailable\n');return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})

def parse(raw,item,canonical):
    values=[]
    for s in re.findall(r'\{[^{}]*\}',raw,re.S):
        try:
            v=json.loads(s)
            if isinstance(v,dict) and 'answer' in v:values.append(v['answer'])
        except json.JSONDecodeError:pass
    if not values:
        refusal=bool(re.search(r"cannot (provide|answer)|can't (provide|answer)|unable to (provide|answer)",raw,re.I))
        return None,'refusal' if refusal else 'malformed_json',None
    if any(v!=values[0] for v in values[1:]):return None,'ambiguous_multiple_answers',None
    v=values[0];fmt=item['answer_format'];options=item['options']
    if fmt=='multi':
        if not isinstance(v,list) or not v or any(not isinstance(x,str) or x not in options for x in v) or len(v)!=len(set(v)):
            return None,'invalid_option_set',v
        return tuple(sorted(v)),None,v
    if not isinstance(v,str):return None,'invalid_answer_type',v
    if re.search(r"cannot (provide|answer)|can't (provide|answer)|unable to (provide|answer)",v,re.I):return None,'refusal',v
    if fmt=='single':return (v,None,v) if v in options else (None,'invalid_option_key',v)
    if fmt=='relation':
        s=norm(v)
        return (s,None,v) if s in {'higher','lower','no difference','uncertainty'} else (None,'invalid_relation',v)
    s=norm(v)
    if s in canonical:return canonical[s],None,v
    ambiguous=bool(re.search(r'\bor\b|\band\b|;|\n',v))
    return None,'ambiguous_diagnosis' if ambiguous else 'unmapped_diagnosis',v

def score(record,label,item,canonical):
    pred,error,raw_value=parse(record['raw_response'],item,canonical)
    gold=tuple(sorted(label['gold'])) if isinstance(label['gold'],list) else label['gold']
    if item['answer_format']=='relation':gold=norm(gold)
    correct=pred==gold if error is None else False
    opts=item['options']
    def semantic(x):
        if isinstance(x,tuple):return tuple(sorted(norm(opts[k]) for k in x))
        return norm(opts.get(x,x)) if x is not None else None
    f1=None;tp=fp=fn=0
    if item['answer_format']=='multi':
        pp=set(pred or ());gg=set(gold);tp=len(pp&gg);fp=len(pp-gg);fn=len(gg-pp);f1=2*tp/(2*tp+fp+fn)
    return {'correct':bool(correct),'prediction':pred,'semantic_prediction':semantic(pred),'semantic_gold':semantic(gold),'invalid_reason':error,'invalid':error is not None,'format_invalid':error is not None and error!='unmapped_diagnosis','unmapped_diagnosis':error=='unmapped_diagnosis','ambiguous':bool(error and error.startswith('ambiguous')),'raw_exact':raw_value==label['gold'],'uncertainty':pred=='uncertainty','option_f1':f1,'tp':tp,'fp':fp,'fn':fn,'predicted_set_size':len(pred or ()) if item['answer_format']=='multi' else None,'gold_set_size':len(gold) if item['answer_format']=='multi' else None}

def bootstrap(values,seed=20260906):
    a=np.asarray(values,dtype=float)
    if not len(a):return [None,None]
    rng=np.random.default_rng(seed)
    means=a[rng.integers(0,len(a),size=(2000,len(a)))].mean(axis=1)
    return np.quantile(means,[.025,.975]).tolist()

def four_grid(pairs):
    counts=Counter((bool(p['ref']['correct']),bool(p['var']['correct'])) for p in pairs)
    n11,n10,n01,n00=[counts[k] for k in [(True,True),(True,False),(False,True),(False,False)]]
    n=sum(counts.values());grouped=defaultdict(list)
    for p in pairs:grouped[p['group']].append(int(p['ref']['correct'])-int(p['var']['correct']))
    groupdrops=[np.mean(v) for v in grouped.values()]
    changed=[p for p in pairs if p['relation']=='change' and p['ref']['correct']]
    persistence=sum(p['var']['semantic_prediction']==p['ref']['semantic_gold'] for p in changed)
    d=n10+n01
    source_values=defaultdict(list)
    for p in pairs:source_values[p['group']].append([int(p['ref']['correct']),int(p['var']['correct']),int(p['ref']['correct'] and p['var']['correct'])])
    macro=np.mean([np.mean(v,axis=0) for v in source_values.values()],axis=0).tolist() if source_values else [None]*3
    return {'N':n,'source_groups':len(grouped),'n11':n11,'n10':n10,'n01':n01,'n00':n00,'A_ref':ratio(n11+n10,n),'A_var':ratio(n11+n01,n),'A_ref_source_macro':macro[0],'A_var_source_macro':macro[1],'pair_accuracy_source_macro':macro[2],'drop_micro':ratio(n10-n01,n),'drop_source_macro':float(np.mean(groupdrops)) if groupdrops else None,'drop_ci':bootstrap(groupdrops),'pair_accuracy':ratio(n11,n),'conditional_success':ratio(n11,n11+n10),'conditional_failure':ratio(n10,n11+n10),'old_answer_persistence':persistence,'BTR_denominator':len(changed),'BTR':ratio(persistence,len(changed)),'mcnemar_p':(float(binomtest(n10,d,.5).pvalue) if d else 1.0) if n and len(grouped)==n else None}

def method_comparison(a,b):
    n=len(a);r=sum(not x and y for x,y in zip(a,b));h=sum(x and not y for x,y in zip(a,b));base=sum(a)
    return {'N':n,'repairs':r,'harms':h,'introduced_error_rate':ratio(h,n),'conditional_harm_rate':ratio(h,base),'OCP':1-h/base if base else None,'net_gain':ratio(r-h,n)}

def aggregate(rows):
    n=len(rows);groups=defaultdict(list)
    for r in rows:groups[r['label']['group_id']].append(int(r['correct']))
    tp=sum(r['tp'] for r in rows);fp=sum(r['fp'] for r in rows);fn=sum(r['fn'] for r in rows)
    sizes=[r for r in rows if r['option_f1'] is not None]
    return {'N':n,'source_groups':len(groups),'correct':sum(r['correct'] for r in rows),'invalid':sum(r['invalid'] for r in rows),'format_invalid':sum(r['format_invalid'] for r in rows),'unmapped_diagnosis':sum(r['unmapped_diagnosis'] for r in rows),'ambiguous':sum(r['ambiguous'] for r in rows),'accuracy':ratio(sum(r['correct'] for r in rows),n),'source_macro_score':float(np.mean([np.mean(v) for v in groups.values()])) if groups else None,'score_ci':bootstrap([np.mean(v) for v in groups.values()]),'raw_exact':ratio(sum(r['raw_exact'] for r in rows),n),'uncertainty':sum(r['uncertainty'] for r in rows),'invalid_reasons':dict(Counter(r['invalid_reason'] for r in rows if r['invalid'])),'output_distribution':dict(Counter(str(r['prediction']) for r in rows)) if rows and rows[0]['label']['dataset']=='medcounterfact' else None,'option_f1_micro':ratio(2*tp,2*tp+fp+fn) if sizes else None,'option_f1_macro':float(np.mean([r['option_f1'] for r in sizes])) if sizes else None,'predicted_set_size':float(np.mean([r['predicted_set_size'] for r in sizes])) if sizes else None,'gold_set_size':float(np.mean([r['gold_set_size'] for r in sizes])) if sizes else None}

def analyze(partial=False):
    plan=json.loads((OUT/'sample_plan.json').read_text())
    if not plan['tier_frozen']:raise SystemExit('Do not inspect formal accuracy before tier freeze.')
    labels=read(OUT/'evaluation_labels.jsonl');items={r['item_id']:r for r in read(OUT/'screening_items.jsonl')};taxonomy=read(OUT/'taxonomy.jsonl')
    canon={norm(s):s for s in json.loads((OUT/'canonical_labels.json').read_text())['labels']}
    preds={};auxiliary={};stages=[];runtimes=[]
    for worker in sorted((OUT/'cache/main').glob('worker-*')):
        if (worker/'runtime.json').exists():runtimes.append(json.loads((worker/'runtime.json').read_text()))
        for stage in ['M0','M1','M2','summary','explore','generate','select','retrieval','rerank']:
            file=worker/(stage+'.jsonl')
            if not file.exists():continue
            for r in read(file):
                if stage in METHODS:
                    key=(r['item_id'],stage)
                    if key in preds:assert preds[key]['raw_response']==r['raw_response'],'conflicting shard answers'
                    preds[key]=r
                elif stage in ['M0','M1','M2']:
                    auxiliary[(r['item_id'],stage)]=r
                compact={k:v for k,v in r.items() if k not in {'documents','raw_response'}}
                compact['stage']=stage;compact['artifact']=str(file.relative_to(OUT))
                if stage=='explore':
                    compact['missing_knowledge_slots']=[j for j in range(1,4) if not re.search(rf'Knowledge\s+{j}\s*:\s*\S',r['raw_response'],re.I)]
                if stage=='rerank':compact['selected_document_count']=len(r['documents'])
                if 'documents' in r:compact['source_ids']=[{'id':d.get('id',d.get('docid')),'source':d['source']} for d in r['documents']]
                stages.append(compact)
    expected=len(METHODS)*len(items)
    if len(preds)<expected and not partial:raise SystemExit(f'Only {len(preds)}/{expected} predictions; use --partial for an explicitly partial report.')
    exported=[]
    for (item_id,method),record in preds.items():
        answer,error,raw_value=parse(record['raw_response'],items[item_id],canon)
        exported.append(record|{'answer':answer,'raw_answer_value':raw_value,'invalid_reason':error,'format_invalid':error is not None and error!='unmapped_diagnosis','unmapped_diagnosis':error=='unmapped_diagnosis'})
    write(OUT/'predictions.jsonl',exported);write(OUT/'stages.jsonl',stages)
    if auxiliary:write(OUT/'auxiliary_predictions.jsonl',list(auxiliary.values()))
    if plan.get('candidate_tier')=='full-test':
        with (OUT/'stages.jsonl').open('rb') as source,gzip.open(OUT/'stages.jsonl.gz','wb') as target:
            shutil.copyfileobj(source,target)
    scored={};rows=[]
    tax_index={(r['item_id'],r['group_id'],r['protocol'],r['role']):r for r in taxonomy}
    for lab in labels:
        for method in METHODS:
            record=preds.get((lab['item_id'],method))
            if record is None:continue
            s=score(record,lab,items[lab['item_id']],canon);s.update(label=lab,method=method)
            scored[(lab['group_id'],lab['protocol'],lab['role'],method)]=s;rows.append(s)
    # Primary MedEinst native excludes added sensitivity-only source groups.
    primary=[r for r in rows if not r['label'].get('additional_native',False)]
    metric_rows=[];category=[];comparisons=[];pair_rows=[];transitions=[];statistics=[]
    benchmark_keys=sorted({(l['dataset'],l['protocol']) for l in labels})
    allpairs={}
    for ds,protocol in benchmark_keys:
        labs=[l for l in labels if (l['dataset'],l['protocol'])==(ds,protocol) and not l.get('additional_native',False)]
        groups=defaultdict(list)
        for l in labs:groups[l['group_id']].append(l)
        # All declared variants AND three methods must finish for primary pair effects.
        complete={g for g,ll in groups.items() if all((l['item_id'],m) in preds for l in ll for m in METHODS)}
        for method in METHODS:
            rr=[r for r in primary if (r['label']['dataset'],r['label']['protocol'],r['method'])==(ds,protocol,method)]
            for role in ['all']+sorted({r['label']['role'] for r in rr if r['label']['role'] in ['reference','guideline_following','counterfactual']})+(['variant'] if ds not in ['medpic'] else []):
                def wanted(l):return role=='all' or (l['role']!='reference' if role=='variant' else l['role']==role)
                values=[r for r in rr if wanted(r['label'])];planned=[l for l in labs if wanted(l)];planned_groups={l['group_id'] for l in planned}
                metric_rows.append({'benchmark':ds,'protocol':protocol,'method':method,'role':role,'score_name':'evidence_agreement' if ds=='medcounterfact' else 'exact_set' if ds=='medpic' else 'canonical_match' if ds=='medeinst' and protocol=='native' else 'accuracy','planned_input_records':len(planned),'planned_source_groups':len(planned_groups),'complete_source_groups_all_methods':len(complete&planned_groups),**aggregate(values)})
            fields={'medpic':['official_operation','patient_info_type'],'cpv':['gender','ethnicity','no_op','patient_attribute_pattern','potential_clinical_conflict'],'cultural':['condition','culture'],'medcounterfact':['main_category'],'medeinst':['previously_exposed']}[ds]
            for field in fields:
                for value in sorted({str(r['label'].get(field)) for r in rr}):
                    vv=[r for r in rr if str(r['label'].get(field))==value]
                    category.append({'benchmark':ds,'protocol':protocol,'method':method,'slice_field':field,'slice':value,**aggregate(vv)})
            operations=sorted({o for r in rr for o in tax_index[(r['label']['item_id'],r['label']['group_id'],protocol,r['label']['role'])]['operation_tags']})
            for op in operations:
                vv=[r for r in rr if op in tax_index[(r['label']['item_id'],r['label']['group_id'],protocol,r['label']['role'])]['operation_tags']]
                category.append({'benchmark':ds,'protocol':protocol,'method':method,'slice_field':'operation_tag','slice':op,**aggregate(vv)})
            pairs=[]
            for r in rr:
                l=r['label'];g=l['group_id']
                if g not in complete or l['role']=='reference':continue
                ref=scored.get((g,protocol,'reference',method))
                if ref is None:continue
                condition=l.get('condition',l.get('main_category',l.get('gender','all')))
                if ds=='cpv':condition=f"{l['gender']}:{l['ethnicity']}"
                if ds=='cultural':condition=f"{l['culture']}:{l['condition']}"
                relation=l.get('expected_answer_relation','unknown')
                pair={'ref':ref,'var':r,'group':g,'relation':relation,'condition':condition}
                pairs.append(pair)
                valid=not ref['invalid'] and not r['invalid'];flip=valid and ref['semantic_prediction']!=r['semantic_prediction']
                transitions.append({'benchmark':ds,'protocol':protocol,'method':method,'group_id':g,'condition':condition,'reference_item_id':ref['label']['item_id'],'variant_item_id':l['item_id'],'relation':relation,'reference_correct':ref['correct'],'variant_correct':r['correct'],'semantic_flip':bool(flip) if valid else None,'changed_but_wrong':bool(flip and not r['correct']) if valid else None,'stable_but_wrong':bool(not flip and not r['correct']) if valid else None,'correct_revision':bool(ref['correct'] and r['correct']) if relation=='change' else None,'correct_preservation':bool(ref['correct'] and r['correct']) if relation=='invariant' else None,'harmful_flip':bool(ref['correct'] and flip and not r['correct']) if relation=='invariant' and valid else None,'invalid_variant':r['invalid']})
            allpairs[(ds,protocol,method)]=pairs
            if pairs:
                for condition in ['all']+sorted({p['condition'] for p in pairs} - {'all'}):
                    pp=pairs if condition=='all' else [p for p in pairs if p['condition']==condition]
                    result=four_grid(pp);row={'benchmark':ds,'protocol':protocol,'method':method,'condition':condition,**result};pair_rows.append(row)
                    if result['mcnemar_p'] is not None:statistics.append({'comparison':'reference_vs_variant','benchmark':ds,'protocol':protocol,'method':method,'condition':condition,'p':result['mcnemar_p'],'N':result['N']})
                if ds=='cultural':
                    for operation in ['Id','Context','Id+Context']:
                        pp=[p for p in pairs if p['var']['label']['condition']==operation]
                        if pp:pair_rows.append({'benchmark':ds,'protocol':protocol,'method':method,'condition':'across_cultures:'+operation,**four_grid(pp)})
        for base_method,m in [('M0','M1'),('M0','M2'),('M1','M2')]:
            if base_method not in METHODS or m not in METHODS:continue
            usable=[l for l in labs if l['group_id'] in complete and (l['item_id'],base_method) in preds and (l['item_id'],m) in preds]
            aa=[scored[(l['group_id'],protocol,l['role'],base_method)]['correct'] for l in usable];bb=[scored[(l['group_id'],protocol,l['role'],m)]['correct'] for l in usable]
            gd=defaultdict(list)
            for l,a,b in zip(usable,aa,bb):gd[l['group_id']].append(int(b)-int(a))
            means=[np.mean(v) for v in gd.values()]
            comparisons.append({'benchmark':ds,'protocol':protocol,'comparison':m+'-'+base_method,**method_comparison(aa,bb),'source_groups':len(gd),'net_gain_source_macro':float(np.mean(means)) if means else None,'net_gain_source_ci':bootstrap(means)})
    # Holm family is fixed to all native reference–variant independent-source condition tests.
    primary_stats=[r for r in statistics if r['protocol']=='native']
    prev=0.;ordered=sorted(primary_stats,key=lambda r:r['p'])
    for i,r in enumerate(ordered):prev=max(prev,min(1.,r['p']*(len(ordered)-i)));r['p_holm']=prev
    amps=[]
    for ds,protocol in benchmark_keys:
        for method in ['M1','M2']:
            a=allpairs.get((ds,protocol,'M0'),[]);b=allpairs.get((ds,protocol,method),[])
            if not a or not b:continue
            by=defaultdict(list)
            index={(p['group'],p['var']['label']['role']):p for p in a}
            for p in b:
                q=index[(p['group'],p['var']['label']['role'])]
                by[p['group']].append(int(p['ref']['correct'])-int(p['var']['correct'])-int(q['ref']['correct'])+int(q['var']['correct']))
            values=[np.mean(v) for v in by.values()]
            amps.append({'benchmark':ds,'protocol':protocol,'method':method,'source_groups':len(by),'amplification':float(np.mean(values)),'ci':bootstrap(values)})
    gaps=[]
    for method in METHODS:
        gf=[r for r in primary if r['label']['dataset']=='medpic' and r['method']==method and r['label']['role']=='guideline_following'];cf=[r for r in primary if r['label']['dataset']=='medpic' and r['method']==method and r['label']['role']!='guideline_following']
        if gf and cf:
            a=np.array([r['correct'] for r in gf]);b=np.array([r['correct'] for r in cf]);rng=np.random.default_rng(20260906)
            diffs=a[rng.integers(0,len(a),(2000,len(a)))].mean(1)-b[rng.integers(0,len(b),(2000,len(b)))].mean(1)
            gaps.append({'method':method,'status':'unpaired_composition_gap','N_GF':len(a),'N_CF':len(b),'gap':float(a.mean()-b.mean()),'ci':np.quantile(diffs,[.025,.975]).tolist()})
    table('benchmark_metrics.csv',metric_rows);table('category_metrics.csv',category);table('paired_effects.csv',pair_rows);table('transitions.csv',transitions);table('method_comparisons.csv',comparisons);table('amplification.csv',amps)
    if (OUT/'taxonomy_corrections.json').exists():
        old={r['item_id']:r['old_tags'] for r in json.loads((OUT/'taxonomy_corrections.json').read_text())['affected']};sensitivity=[]
        for method in METHODS:
            rr=[r for r in primary if r['label']['dataset']=='medpic' and r['method']==method]
            for op in ['presence_polarity','measurement_threshold','mixed_or_unresolved']:
                for version in ['before','after']:
                    vv=[]
                    for r in rr:
                        l=r['label'];current=tax_index[(l['item_id'],l['group_id'],l['protocol'],l['role'])]['operation_tags']
                        tags=old.get(l['item_id'],current) if version=='before' else current
                        if op in tags:vv.append(r)
                    sensitivity.append({'method':method,'operation':op,'annotation_version':version,**aggregate(vv)})
        table('taxonomy_correction_sensitivity.csv',sensitivity)
    dump('statistics.json',{'bootstrap':'2000 source-group cluster resamples, source means primary; micro supplemental','mcnemar_holm_family':'native independent-source condition-level reference-vs-variant tests for required methods '+','.join(METHODS)+'; multi-variant aggregate has no McNemar p','tests':statistics,'MedPIC':gaps,'equivalence_margin':.05,'equivalence_status':'independent cross-source matching operation comparisons unavailable; within-source exploratory intervals only'})
    ident=identifiability(taxonomy)
    explanatory_models(allpairs,items,taxonomy)
    efficiency=efficiency_report(stages,runtimes,len(items),len(preds))
    repeat=repeat_report(items,labels,canon,preds)
    if repeat['executed']!=20 and not partial:raise SystemExit('The 20-input disjoint-stream repeat is incomplete; run the fixed repeat before final analysis.')
    sensitivities=sensitivity_report(rows,scored)
    proxies=mechanism_proxies(labels)
    metrics={'planned_unique_inputs':len(items),'completed_unique_method_predictions':len(preds),'planned_method_predictions':expected,'completion_rate':len(preds)/expected,'status':'complete' if len(preds)==expected and repeat['executed']==20 else 'partial','benchmarks':metric_rows,'method_comparisons':comparisons,'amplification':amps,'neutral':'unavailable in released inputs','taxonomy':ident,'efficiency':efficiency,'repeat':repeat,'sensitivities':sensitivities,'mechanism_proxies':proxies}
    metrics['evaluation_scope']=plan.get('scope','sampled screening tier; not the entire test set')
    metrics['required_methods']=list(METHODS)
    metrics['preserved_auxiliary_predictions']=dict(Counter(m for _,m in auxiliary))
    dump('metrics.json',metrics);figures(pair_rows,amps,category,stages,gaps)
    report(metrics,pair_rows,gaps)
    print(json.dumps({'status':metrics['status'],'predictions':len(preds),'planned':expected,'report':str(OUT/'summary.md')}))

def identifiability(taxonomy):
    counts=Counter((r['dataset'],','.join(r['operation_tags']) or 'reference_or_static',r['expected_answer_relation'],r['original_source_family'],r['answer_format']) for r in taxonomy)
    table('taxonomy_coverage.csv',[dict(zip(['benchmark','operation','answer_relation','source_family','format','N'],[*k,v])) for k,v in sorted(counts.items())])
    result={}
    for domain in ['clinical_update','answer_invariance','hypothetical_evidence_world']:
        rr=[r for r in taxonomy if r['task_contract']==domain and r['role']!='reference'];ops=sorted({o for r in rr for o in r['operation_tags']})
        datasets=sorted({r['dataset'] for r in rr});formats=sorted({r['answer_format'] for r in rr})
        base=np.array([[1]+[float(r['dataset']==d) for d in datasets[1:]]+[float(r['answer_format']==f) for f in formats[1:]]+[r.get('reference_length',0)/1000,r.get('edit_length',0)/1000] for r in rr])
        tags=np.array([[float(o in r['operation_tags']) for o in ops] for r in rr])
        design=np.column_stack([base,tags]);rank=int(np.linalg.matrix_rank(design));baserank=int(np.linalg.matrix_rank(base))
        cover={o:{'benchmarks':sorted({r['dataset'] for r in rr if o in r['operation_tags']}),'source_families':sorted({r['original_source_family'] for r in rr if o in r['operation_tags']})} for o in ops}
        reason='operation is confounded with benchmark/source/format' if rank<design.shape[1] else 'design is full rank within MedQA constructions, but independent cross-source taxonomy generalization is unavailable (only one source family)'
        result[domain]={'status':'NOT_IDENTIFIABLE','scope':'independent cross-source taxonomy','reason':reason,'within_domain_design_status':'full_rank' if rank==design.shape[1] else 'rank_deficient','N':len(rr),'base_rank':baserank,'augmented_rank':rank,'augmented_columns':design.shape[1],'operation_coverage':cover,'leave_one_source':'unavailable','within_Cultural_operation_contrasts':'available as same-MedQA-source construction analysis' if domain=='answer_invariance' else None}
    dump('taxonomy_identifiability.json',result);return result

def explanatory_models(allpairs,items,taxonomy):
    """Within-MedQA source comparisons; never estimate confounded clinical tags."""
    tags={(t['item_id'],t['group_id']):t['operation_tags'] for t in taxonomy}
    alias={g:min(r['groups']) for r in json.loads((OUT/'source_overlap.json').read_text()) for g in r['groups']}
    results={}
    for method in METHODS:
        pp=allpairs.get(('cpv','native',method),[])+allpairs.get(('cultural','native',method),[])
        if not pp:continue
        names=['intercept','Cultural_dataset','reference_length_kchars','net_length_change_kchars','identity_attribute','contextual_addition']
        x=[];y=[];groups=[]
        for p in pp:
            lab=p['var']['label'];ref=items[p['ref']['label']['item_id']]['question'];var=items[lab['item_id']]['question'];ops=tags[(lab['item_id'],lab['group_id'])]
            x.append([1,int(lab['dataset']=='cultural'),len(ref)/1000,(len(var)-len(ref))/1000,int('identity_attribute' in ops),int('contextual_addition' in ops)])
            y.append(int(p['var']['correct'])-int(p['ref']['correct']));groups.append(alias.get(p['group'],p['group']))
        x=np.array(x,float);y=np.array(y,float);rank=int(np.linalg.matrix_rank(x));base=x[:,:4]
        if rank<x.shape[1]:
            results[method]={'status':'NOT_IDENTIFIABLE','reason':'rank deficient available paired subset','rank':rank,'columns':x.shape[1]};continue
        # Equal source weights; all declared variants stay together in bootstrap.
        counts=Counter(groups);weights=np.array([1/counts[g] for g in groups]);root=np.sqrt(weights)
        def fit(a,b,w):return np.linalg.lstsq(a*w[:,None],b*w,rcond=None)[0]
        b0=fit(base,y,root);b1=fit(x,y,root)
        gidx=[np.flatnonzero(np.array(groups)==g) for g in sorted(set(groups))]
        rng=np.random.default_rng(20260906);boots=[]
        for _ in range(2000):
            ix=np.concatenate([gidx[i] for i in rng.integers(0,len(gidx),len(gidx))])
            if np.linalg.matrix_rank(x[ix])==x.shape[1]:boots.append(fit(x[ix],y[ix],root[ix]))
        intervals=np.quantile(np.array(boots),[.025,.975],axis=0).T.tolist() if boots else [[None,None]]*len(names)
        results[method]={'status':'exploratory_same_MedQA_source_constructions_only','outcome':'variant_correct minus reference_correct; source-paired outcome, not reference correctness as difficulty covariate','source_groups':len(gidx),'N_pairs':len(pp),'base_rank':int(np.linalg.matrix_rank(base)),'augmented_rank':rank,'base_weighted_MSE':float(np.average((y-base@b0)**2,weights=weights)),'augmented_weighted_MSE':float(np.average((y-x@b1)**2,weights=weights)),'coefficients':{k:{'estimate':float(v),'source_cluster_95_CI':ci} for k,v,ci in zip(names,b1,intervals)},'bootstrap_full_rank_resamples':len(boots),'limits':'native answer format and original source family are constant in this domain; no independent cross-source generalization; linear descriptive association, not causal attribution; edit-length covariate is signed character-length change, not clinical edit magnitude; no leave-one-source validation available'}
    dump('explanatory_models.json',results)

def efficiency_report(stages,runtimes,n,completed):
    rows=[]
    for stage in sorted({r['stage'] for r in stages}):
        rr=[r for r in stages if r['stage']==stage];pt=sum(r.get('prompt_tokens',0) for r in rr);ct=sum(r.get('completion_tokens',0) for r in rr)
        wall=sum(r.get('batch_wall_seconds',0)/r.get('batch_size',1) if 'batch_wall_seconds' in r else r.get('wall_seconds',0) for r in rr)
        queues=[r.get('request_metrics',{}).get('time_in_queue') for r in rr];queues=[q for q in queues if q is not None]
        rows.append({'stage':stage,'requests_or_records':len(rr),'prompt_tokens':pt,'completion_tokens':ct,'stage_batch_wall_seconds_sum':wall,'completion_tokens_per_stage_second':ratio(ct,wall),'truncations':sum(r.get('finish_reason')=='length' for r in rr),'explore_missing_slots':sum(bool(r.get('missing_knowledge_slots')) for r in rr),'selected_below_five':sum(r.get('selected_document_count',5)<5 for r in rr),'mean_queue_seconds':float(np.mean(queues)) if queues else None,'batch_sizes':dict(Counter(r.get('batch_size') for r in rr))})
    table('efficiency.csv',rows)
    times=[r['time'] for r in stages if 'time' in r]
    extra=[]
    for scope,files in [('seed_repeat',(OUT/'cache/repeat_independent').glob('worker-*/*.jsonl')),('superseded_seed_repeat',(OUT/'cache/repeat').glob('worker-*/*.jsonl')),('superseded_smoke',(OUT/'cache/smoke_pre_evidence_dedup').glob('*.jsonl'))]:
        rr=[r for f in files if f.stem in ['M0','M1','M2','summary','explore','generate','select'] for r in read(f)]
        extra.append({'scope':scope,'requests':len(rr),'prompt_tokens':sum(r['prompt_tokens'] for r in rr),'completion_tokens':sum(r['completion_tokens'] for r in rr)})
    wall=OUT/'cache/batch_wall_times.txt';wall_lines=wall.read_text().splitlines() if wall.exists() else []
    from datetime import datetime
    batch_elapsed=(datetime.fromisoformat(wall_lines[-1])-datetime.fromisoformat(wall_lines[0])).total_seconds() if len(wall_lines)>=2 else time.time()-datetime.fromisoformat(wall_lines[0]).timestamp() if wall_lines else None
    result={'unique_inputs_planned':n,'completed_method_predictions':completed,'LLM_requests':sum(r['requests_or_records'] for r in rows if r['stage'] not in ['retrieval','rerank']),'prompt_tokens':sum(r['prompt_tokens'] for r in rows),'completion_tokens':sum(r['completion_tokens'] for r in rows),'completion_timestamp_span_seconds':max(times)-min(times) if times else None,'formal_batch_elapsed_seconds':batch_elapsed,'formal_batch_wall_timestamps':wall_lines,'worker_runtime_records':runtimes,'pipeline_makespan_note':'formal wall timestamps include concurrent workers, not sum of stage times; separate cold smoke/compatibility work is in performance_test.json','cache_hits':dict(sum((Counter(r['cache_hits']) for r in runtimes),Counter())),'network_retries':0,'format_repairs':0,'extra_workload':extra,'cold_vs_reused':'new frozen-input run; exact duplicate input tasks collapsed before inference; smoke stage caches reused after review; historical answer caches not reused'}
    result['total_recorded_LLM_requests_including_extra']=result['LLM_requests']+sum(r['requests'] for r in extra)
    result['total_recorded_prompt_tokens_including_extra']=result['prompt_tokens']+sum(r['prompt_tokens'] for r in extra)
    result['total_recorded_completion_tokens_including_extra']=result['completion_tokens']+sum(r['completion_tokens'] for r in extra)
    records=len(read(OUT/'evaluation_labels.jsonl'))
    result.update(prepared_input_records=records,exact_duplicate_input_records=records-n,LLM_requests_avoided_by_exact_input_deduplication=(13 if list(METHODS)==['M2'] else 15)*(records-n),historical_answer_cache_hits=0)
    if list(METHODS)==['M2']:
        result['required_M2_pipeline_LLM_requests']=sum(r['requests_or_records'] for r in rows if r['stage'] in ['M2','summary','explore','generate','select'])
        result['preserved_auxiliary_reader_requests']=sum(r['requests_or_records'] for r in rows if r['stage'] in ['M0','M1'])
        result['method_scope']=json.loads((OUT/'method_scope.json').read_text())
        result['method_scope_cost']=json.loads((OUT/'method_scope_cost.json').read_text())
        if (OUT/'method_scope_restart.json').exists():result['method_scope_restart']=json.loads((OUT/'method_scope_restart.json').read_text())
    prefetch=OUT/'retrieval_prefetch_completion.json'
    if prefetch.exists():result['retrieval_prefetch']=json.loads(prefetch.read_text())
    reuse=OUT/'cache_reuse.json'
    if reuse.exists():
        result['prior_screening_reuse']=json.loads(reuse.read_text())
        result['historical_answer_cache_hits']=result['prior_screening_reuse']['prior_predictions']
        result['unrelated_historical_method_answer_cache_hits']=0
        result['cold_vs_reused']='full-test extension: exact prior screening inputs and all their stages reused; remaining inputs newly executed; no unrelated historical method answers reused'
        start=datetime.fromisoformat(wall_lines[0]).timestamp() if wall_lines else float('inf')
        fresh=[r for r in stages if r.get('time',0)>=start and 'prompt_tokens' in r]
        result['incremental_expansion_workload']={'LLM_requests':len(fresh),'prompt_tokens':sum(r['prompt_tokens'] for r in fresh),'completion_tokens':sum(r['completion_tokens'] for r in fresh),'meaning':'new requests since the full-test expansion started; earlier exact cached stages remain in total workload'}
        result['recovered_engine_startup_failures']=len(list((OUT/'cache/runtime_failures').glob('*_initial_capacity.json')))
        restart=OUT/'capacity_restart.json'
        if restart.exists():
            result['controlled_capacity_restart']=json.loads(restart.read_text())
            result['recorded_token_cost_limit']='Unreturned tokens from at most one interrupted batch per engine during the documented capacity restart are unavailable; recorded token totals exclude them. Full batch wall time includes the interruption and reinitialization.'
        restart=OUT/'throughput_restart.json'
        if restart.exists():
            result['controlled_throughput_restart']=json.loads(restart.read_text())
            result['recorded_token_cost_limit']='Two documented scheduling/capacity restarts: at most one unreturned batch per engine per restart (four batches total); their tokens are unavailable and excluded from recorded-token totals. Full wall time includes all work and restart intervals.'
            result['pipeline_makespan_note']+=' Intermediate wall timestamps mark restarted scheduler phases; first-to-last is the complete expansion makespan.'
        restart=OUT/'unexpected_exit_restart.json'
        if restart.exists():
            result['unexpected_exit_restart']=json.loads(restart.read_text())
            result['recorded_token_cost_limit']+=' An additional unexpected worker exit may have lost up to one in-flight batch per engine (64 requests each); those unreturned tokens are also unknown and excluded.'
            result['pipeline_makespan_note']+=' The unexpected-exit downtime and subsequent recovery are included.'
        restart=OUT/'tail_rebalance.json'
        if restart.exists():
            result['tail_rebalance']=json.loads(restart.read_text())
        result['cache_hits_scope']='Latest durable runtime record per worker; counters restart with each process. Exact historical input reuse and input deduplication are reported separately.'
    completion=OUT/'reader_completion.json'
    if completion.exists():
        result['reader_completion']=json.loads(completion.read_text())
        result['new_requests_by_stage']=dict(Counter(r['stage'] for r in fresh))
        assert set(result['new_requests_by_stage']) <= {'M0','M1'}, 'Reader completion recomputed a non-reader stage'
        result['incremental_expansion_workload']['meaning']='Only missing M0/M1 reader requests in this completion batch; all M2 and initial retrieval artifacts reused unchanged'
        result['pipeline_makespan_note']='First-to-last wall timestamps measure this M0/M1 completion batch only. Prior M2/screening runtime and interruption limits are retained in prior_run_efficiency.json; aggregate stage times and logical tokens include reused history.'
        result['prior_run_efficiency_file']='prior_run_efficiency.json'
    return result

def repeat_report(items,labels,canonical,preds,scope='repeat_independent'):
    rr=[];lookup={l['item_id']:l for l in labels};plan=json.loads((OUT/'sample_plan.json').read_text());executed=0
    for f in (OUT/'cache'/scope).glob('worker-*/M2.jsonl'):
        for r in read(f):
            executed+=1
            original=preds.get((r['item_id'],'M2'))
            if original:
                a=score(original,lookup[r['item_id']],items[r['item_id']],canonical);b=score(r,lookup[r['item_id']],items[r['item_id']],canonical)
                valid=not a['invalid'] and not b['invalid']
                rr.append({'item_id':r['item_id'],'semantic_flip':a['semantic_prediction']!=b['semantic_prediction'] if valid else None,'raw_output_changed':norm(original['raw_response'])!=norm(r['raw_response']),'primary_invalid':a['invalid'],'repeat_invalid':b['invalid'],'primary_correct':a['correct'],'repeat_correct':b['correct']})
    valid=[r for r in rr if r['semantic_flip'] is not None]
    result={'planned':20,'executed':executed,'matched_primary_completed':len(rr),'valid_semantic_comparisons':len(valid),'seed':plan['repeat_seed'],'stream_offset':1_000_000_000 if scope=='repeat_independent' else 0,'flip_rate':ratio(sum(r['semantic_flip'] for r in valid),len(valid)),'raw_output_change_rate':ratio(sum(r['raw_output_changed'] for r in rr),len(rr)),'rows':rr,'interpretation':'noise estimate only; no ensemble or correction; unmapped/invalid pairs excluded from semantic flip denominator and retained in raw-output change'}
    if scope=='repeat_independent':
        result['superseded_cross_slot_seed_overlap']=repeat_report(items,labels,canonical,preds,scope='repeat')
        dump('seed_repeat.json',result)
    return result

def sensitivity_report(rows,scored):
    result={};overlaps=json.loads((OUT/'source_overlap.json').read_text());overlap_groups={g for r in overlaps for g in r['groups']}
    expected=defaultdict(list)
    for l in read(OUT/'evaluation_labels.jsonl'):expected[(l['group_id'],l['protocol'])].append(l)
    complete={k for k,ll in expected.items() if all((l['group_id'],l['protocol'],l['role'],m) in scored for l in ll for m in METHODS)}
    paired_sensitivity=[]
    selectors={'no_suspected_source_overlap':lambda r:r['label']['group_id'] not in overlap_groups,'cpv_quality_flag_negative':lambda r:r['label']['dataset']=='cpv' and not r['label'].get('no_op',False) and not r['label'].get('potential_clinical_conflict',False),'medeinst_unexposed':lambda r:r['label']['dataset']=='medeinst' and not r['label'].get('previously_exposed',True),'medeinst_exposed':lambda r:r['label']['dataset']=='medeinst' and r['label'].get('previously_exposed',False)}
    if (OUT/'duplicate_gold_conflicts.json').exists():
        selectors['medeinst_without_identical_input_gold_conflict']=lambda r:r['label']['dataset']=='medeinst' and not r['label'].get('identical_input_conflicting_gold',False)
    for name,predicate in selectors.items():
        values=[r for r in rows if predicate(r) and not r['label'].get('additional_native',False)]
        result[name]=[{'benchmark':ds,'protocol':protocol,'method':m,**aggregate([r for r in values if (r['label']['dataset'],r['label']['protocol'],r['method'])==(ds,protocol,m)])} for ds,protocol,m in sorted({(r['label']['dataset'],r['label']['protocol'],r['method']) for r in values})]
        for ds,protocol,method in sorted({(r['label']['dataset'],r['label']['protocol'],r['method']) for r in values}):
            pp=[]
            for r in values:
                l=r['label']
                if (l['dataset'],l['protocol'],r['method'])!=(ds,protocol,method) or l['role']=='reference' or (l['group_id'],protocol) not in complete:continue
                ref=scored.get((l['group_id'],protocol,'reference',method))
                if ref:pp.append({'ref':ref,'var':r,'group':l['group_id'],'relation':l.get('expected_answer_relation','unknown')})
            if pp:paired_sensitivity.append({'sensitivity':name,'benchmark':ds,'protocol':protocol,'method':method,**four_grid(pp)})
    comparisons=[]
    for r in rows:
        l=r['label']
        if l['dataset']=='medeinst' and l['protocol']=='derived_four_way':
            n=scored.get((l['group_id'],'native',l['role'],r['method']))
            if n:comparisons.append({'group':l['group_id'],'method':r['method'],'role':l['role'],'native_correct':n['correct'],'derived_correct':r['correct']})
    table('native_derived_comparison.csv',comparisons);result['native_derived_matched_records']=len(comparisons)
    result['native_derived_effects']=[]
    for method in METHODS:
        for role in ['reference','variant']:
            rr=[r for r in comparisons if r['method']==method and r['role']==role]
            if not rr:continue
            a=[r['native_correct'] for r in rr];b=[r['derived_correct'] for r in rr];d=sum(x!=y for x,y in zip(a,b));h=sum(x and not y for x,y in zip(a,b))
            result['native_derived_effects'].append({'method':method,'role':role,**method_comparison(a,b),'ci':bootstrap([int(y)-int(x) for x,y in zip(a,b)]),'mcnemar_p_exploratory':float(binomtest(h,d,.5).pvalue) if d else 1.})
    result['paired_effects']=paired_sensitivity
    dump('sensitivities.json',result);return result

def mechanism_proxies(labels):
    retrieval={};selected={}
    items={r['item_id']:r for r in read(OUT/'screening_items.jsonl')}
    for worker in (OUT/'cache/main').glob('worker-*'):
        for name,target in [('retrieval',retrieval),('rerank',selected)]:
            if (worker/(name+'.jsonl')).exists():target.update({r['item_id']:r for r in read(worker/(name+'.jsonl'))})
    rr=[]
    for l in labels:
        ref=l.get('reference_item_id');key=l['item_id']
        if l['role']=='reference' or ref not in retrieval or key not in retrieval:continue
        def ids(k):return {(d['source'],d.get('id',d.get('docid'))) for d in retrieval[k]['documents']}
        a,b=ids(ref),ids(key);docs=selected.get(key,{}).get('documents',[])
        old=re.findall(r'\b\w+\b',items[ref]['question'].lower());new=re.findall(r'\b\w+\b',items[key]['question'].lower());added=set()
        for tag,_,_,j,k in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
            if tag in ['insert','replace']:added.update(t for t in new[j:k] if len(t)>3)
        words=set(re.findall(r'\b\w+\b',' '.join(d['contents'] for d in docs).lower()))
        rr.append({'benchmark':l['dataset'],'group_id':l['group_id'],'item_id':key,'retrieval_jaccard':ratio(len(a&b),len(a|b)),'selected_retrieved':sum(d['source']!='generated' for d in docs),'selected_generated':sum(d['source']=='generated' for d in docs),'edited_question_tokens':len(added),'edited_token_coverage_proxy':ratio(len(added&words),len(added))})
    table('mechanism_proxies.csv',rr);return {'records':len(rr),'interpretation':'retrieval overlap and document-source count associations; not evidence correctness, entailment, or causal failure'}

def figures(pairs,amps,categories,stages,gaps):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
    def save(fig,name):
        fig.tight_layout();fig.savefig(figdir/(name+'.svg'));fig.savefig(figdir/(name+'.png'),dpi=180);plt.close(fig)
        svg=figdir/(name+'.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    for world,name in [(False,'paired_drop'),(True,'evidence_world_drop')]:
        rr=[r for r in pairs if r['condition']=='all' and r['protocol']=='native' and (r['benchmark']=='medcounterfact')==world]
        if not rr:continue
        fig,ax=plt.subplots(figsize=(9,max(3,len(rr)*.38)))
        for i,r in enumerate(rr):
            m=r['drop_source_macro'];lo,hi=r['drop_ci'];ax.errorbar(m*100,i,xerr=[[max(0,m-lo)*100],[max(0,hi-m)*100]],fmt='o')
        ax.set_yticks(range(len(rr)),[f"{r['benchmark']} {r['method']} (groups={r['source_groups']})" for r in rr]);ax.axvline(0,color='grey',lw=.8);ax.set_xlabel('Reference − variant, source mean (pp), cluster 95% CI');save(fig,name)
    rr=[r for r in pairs if r['benchmark']=='cultural' and r['method']=='M2' and r['condition']!='all']
    if rr:
        fig,ax=plt.subplots(figsize=(9,4));ax.bar(range(len(rr)),[r['drop_source_macro']*100 for r in rr]);ax.set_xticks(range(len(rr)),[r['condition'] for r in rr],rotation=35,ha='right');ax.set_ylabel('M2 Original − variant (pp)');ax.set_title('Neutral unavailable in released inputs');save(fig,'cultural_original_comparison')
    for world,name in [(False,'pair_four_cells'),(True,'evidence_world_four_cells')]:
        rr=[r for r in pairs if r['condition']=='all' and r['protocol']=='native' and (r['benchmark']=='medcounterfact')==world]
        if not rr:continue
        fig,ax=plt.subplots(figsize=(9,4));bottom=np.zeros(len(rr))
        for key in ['n11','n10','n01','n00']:
            values=np.array([r[key]/r['N'] for r in rr]);ax.bar(range(len(rr)),values,bottom=bottom,label=key);bottom+=values
        ax.set_xticks(range(len(rr)),[r['benchmark']+' '+r['method']+f" N={r['N']}" for r in rr],rotation=65,ha='right');ax.legend();save(fig,name)
    if gaps:
        fig,ax=plt.subplots(figsize=(6,3))
        for i,r in enumerate(gaps):
            m=r['gap'];lo,hi=r['ci'];ax.errorbar(i,100*m,yerr=[[100*max(0,m-lo)],[100*max(0,hi-m)]],fmt='o')
        ax.set_xticks(range(len(gaps)),[r['method'] for r in gaps]);ax.axhline(0,color='grey',lw=.8);ax.set_ylabel('GF − CF exact-set score (pp)');ax.set_title('MedPIC: unpaired composition gap, 95% CI');save(fig,'medpic_unpaired_gap')
    if amps:
        fig,ax=plt.subplots(figsize=(9,4))
        for i,r in enumerate(amps):
            m=r['amplification'];lo,hi=r['ci'];ax.errorbar(i,100*m,yerr=[[100*max(0,m-lo)],[100*max(0,hi-m)]],fmt='o')
        ax.axhline(0,color='grey',lw=.8);ax.set_xticks(range(len(amps)),[r['benchmark']+' '+r['protocol']+' '+r['method'] for r in amps],rotation=45,ha='right');ax.set_ylabel('Drop method − drop Direct (pp), 95% CI');save(fig,'sensitivity_amplification')
    rr=[r for r in categories if r['slice_field']=='operation_tag' and r['protocol']=='native']
    if rr:
        keys=sorted({(r['benchmark'],r['slice']) for r in rr});index={(r['benchmark'],r['slice'],r['method']):r for r in rr}
        values=np.array([[100*(1-index[(ds,op,m)]['accuracy']) if (ds,op,m) in index else np.nan for m in METHODS] for ds,op in keys])
        fig,ax=plt.subplots(figsize=(9,max(3,len(keys)*.45)));im=ax.imshow(values,vmin=0,vmax=100,aspect='auto',cmap='Oranges');fig.colorbar(im,ax=ax,label='Row-specific native metric error (%)')
        ax.set_xticks(range(len(METHODS)),list(METHODS));ax.set_yticks(range(len(keys)),[ds+': '+op for ds,op in keys])
        for i,(ds,op) in enumerate(keys):
            for j,m in enumerate(METHODS):
                r=index.get((ds,op,m));ax.text(j,i,f"{values[i,j]:.1f}% (N={r['N']})" if r else 'NA',ha='center',va='center',fontsize=8)
        ax.set_title('Within-benchmark operation slices; MedCounterFact uses EA error');save(fig,'operation_error_spectrum')
    taxonomy=read(OUT/'taxonomy.jsonl');datasets=sorted({r['dataset'] for r in taxonomy});ops=sorted({o for r in taxonomy for o in r['operation_tags']})
    count=Counter((r['dataset'],o) for r in taxonomy for o in r['operation_tags']);values=np.array([[count[(d,o)] or np.nan for o in ops] for d in datasets])
    fig,ax=plt.subplots(figsize=(10,4));ax.imshow(np.log1p(values),aspect='auto',cmap='Blues');ax.set_xticks(range(len(ops)),ops,rotation=35,ha='right');ax.set_yticks(range(len(datasets)),datasets)
    for i,d in enumerate(datasets):
        for j,o in enumerate(ops):ax.text(j,i,str(count[(d,o)]) if count[(d,o)] else 'NA',ha='center',va='center',fontsize=8)
    ax.set_title('Frozen operation coverage (label records)');save(fig,'taxonomy_coverage')
    ts=[r for r in stages if 'time' in r]
    if ts:
        ts.sort(key=lambda r:r['time']);fig,ax=plt.subplots(figsize=(8,3));ax.plot([(r['time']-ts[0]['time'])/3600 for r in ts],np.cumsum([r.get('completion_tokens',0) for r in ts]));ax.set_xlabel('Elapsed completion span (h)');ax.set_ylabel('Completion tokens');save(fig,'token_progress')

def report(metrics,pairs,gaps):
    def pct(v):return 'NA' if v is None else f'{100*v:.2f}%'
    def ci(v):return 'NA' if v[0] is None else f'[{100*v[0]:.2f}, {100*v[1]:.2f}] pp'
    lines=['# Cross-benchmark all-Llama baseline screening',f"\nStatus: **{metrics['status']}**; unique method predictions {metrics['completed_unique_method_predictions']}/{metrics['planned_method_predictions']}.",'\nLocal baseline and exact stage contract: [baseline_contract.md](baseline_contract.md). Public source revisions and release discrepancies: [acquisition.md](acquisition.md).','\n## Native primary results','| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |','|---|---|---:|---:|---|---:|---:|---:|']
    for r in metrics['benchmarks']:
        if r['role']=='all' and r['protocol']=='native':lines.append(f"| {r['benchmark']} | {r['method']} | {r['N']} | {pct(r['source_macro_score'])} | [{pct(r['score_ci'][0])}, {pct(r['score_ci'][1])}] | {pct(r['accuracy'])} | {r['invalid']} | {r['complete_source_groups_all_methods']}/{r['planned_source_groups']} |")
    lines+=['\nMedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.','\n## Paired effects','| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |','|---|---|---:|---:|---|---:|']
    for r in pairs:
        if r['condition']=='all':lines.append(f"| {r['benchmark']}/{r['protocol']} | {r['method']} | {r['N']}/{r['source_groups']} | {100*r['drop_source_macro']:.2f} pp | {ci(r['drop_ci'])} | {pct(r['BTR'])} / {r['BTR_denominator']} |")
    lines+=['\n## Changes relative to Direct and retrieval-only','| Benchmark/protocol | Comparison | Source groups | Source-mean score gain | 95% CI | Introduced errors / items | Conditional harm |','|---|---|---:|---:|---|---:|---:|']
    for r in metrics['method_comparisons']:
        lines.append(f"| {r['benchmark']}/{r['protocol']} | {r['comparison']} | {r['source_groups']} | {pct(r['net_gain_source_macro'])} | {ci(r['net_gain_source_ci'])} | {r['harms']}/{r['N']} | {pct(r['conditional_harm_rate'])} |")
    lines+=['\nGain intervals use source means. Introduced-error and conditional-harm columns retain their specified item-level denominators; for M2−M1, the comparator is M1. Positive paired amplification means greater reference-to-variant sensitivity than Direct; it is not a causal finding.','\n| Benchmark/protocol | Method | Drop amplification vs Direct | 95% CI |','|---|---|---:|---|']
    for r in metrics['amplification']:
        lines.append(f"| {r['benchmark']}/{r['protocol']} | {r['method']} | {100*r['amplification']:.2f} pp | {ci(r['ci'])} |")
    lines+=['\n| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |','|---|---:|---:|---|']
    for r in gaps:lines.append(f"| {r['method']} | {r['N_GF']}/{r['N_CF']} | {100*r['gap']:.2f} pp | {ci(r['ci'])} |")
    lines+=['\nMedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.','\n## Interpretation and limits','The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.','\nErrors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.','\nNative/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.','\n## Cost and next research decision',f"Recorded main-run LLM requests (including frozen sensitivity inputs): {metrics['efficiency']['LLM_requests']}; prompt tokens: {metrics['efficiency']['prompt_tokens']}; completion tokens: {metrics['efficiency']['completion_tokens']}. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.",'One follow-up worth testing is whether original KADS output/parser format mismatches cause evidence loss that explains M2−M1 changes within the same source question. Current empty-selection/document-count records motivate this question but do not establish causation; no parser repair or new method is evaluated here.','\nA completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.']
    cost=metrics['efficiency'];repeat=metrics['repeat']
    lines+=[f"\nAll recorded workloads including superseded attempts: {cost['total_recorded_prompt_tokens_including_extra']} logical prompt tokens and {cost['total_recorded_completion_tokens_including_extra']} completion tokens. Exact visible-input deduplication removes {cost['exact_duplicate_input_records']} duplicate tasks and avoids {cost['LLM_requests_avoided_by_exact_input_deduplication']} LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens."]
    lines+=['\n## Execution and parsing details',f"Formal concurrent batch elapsed: {cost['formal_batch_elapsed_seconds']/3600:.2f} h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: {cost['total_recorded_LLM_requests_including_extra']}. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.",f"Independent-seed repeat: {repeat['executed']}/20 executed, {repeat['matched_primary_completed']} matched completed primary inputs, semantic flips {pct(repeat['flip_rate'])} among {repeat['valid_semantic_comparisons']} valid comparisons; raw-output changes {pct(repeat['raw_output_change_rate'])}. This estimate does not alter primary scores.",'\n| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |','|---|---|---:|---:|---:|---:|']
    for r in metrics['benchmarks']:
        if r['role']=='all' and r['protocol']=='native':lines.append(f"| {r['benchmark']} | {r['method']} | {r['format_invalid']} | {r['unmapped_diagnosis']} | {r['ambiguous']} | {r['uncertainty']} |")
    lines+=['\nUnmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.','\n## Frozen MedEinst format sensitivity','| Method | Role | Matched inputs | Four-way minus native score | 95% CI |','|---|---|---:|---:|---|']
    for r in metrics['sensitivities']['native_derived_effects']:lines.append(f"| {r['method']} | {r['role']} | {r['N']} | {pct(r['net_gain'])} | {ci(r['ci'])} |")
    reranks=[r for r in read(OUT/'stages.jsonl') if r['stage']=='rerank']
    if metrics['required_methods']==['M2']:
        start=lines.index('\n## Changes relative to Direct and retrieval-only')
        end=lines.index('\n| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |')
        lines[start:end]=['\n## Method scope','Only MedRGAG-Llama base (M2) is required after the explicit user scope correction. Previously completed Direct/retrieval-only outputs are preserved in auxiliary_predictions.jsonl and are not completed full-test comparisons. No cross-method amplification is estimated in this report.']
        lines=[s.replace('Recorded main-run LLM requests (including frozen sensitivity inputs):','Recorded LLM requests (including frozen sensitivity and preserved auxiliary readers):') for s in lines]
        lines=[('One follow-up worth testing is whether original KADS output/parser format mismatches explain evidence loss associated with M2 reference/variant prediction changes. These saved stage proxies do not establish causation; no parser repair or new method is evaluated here.' if s.startswith('One follow-up worth testing') else s) for s in lines]
    lines.insert(2,'\nEvaluation scope: '+metrics['evaluation_scope']+'.')
    counts=Counter(r['selected_document_count'] for r in reranks)
    lines += [f"\nOriginal KADS/parser selected-document distribution: {dict(sorted(counts.items()))}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.", '\nInterpretation, execution audit and limitations: [findings.md](findings.md), [validation.json](validation.json).']
    if 'incremental_expansion_workload' in cost:
        extra=cost['incremental_expansion_workload']
        lines += [f"\nFull-test expansion: {extra['LLM_requests']} newly executed requests; {extra['prompt_tokens']} prompt tokens; {extra['completion_tokens']} completion tokens. Aggregate workload above includes prior screening stages reused by exact input equality. The fixed auxiliary 20-input repeat is inherited from the earlier screening subset, not a new random sample of the enlarged test population. See cache_reuse.json for context-capacity provenance."]
    if 'reader_completion' in cost:
        lines.insert(3,'\nCurrent batch completes the previously stopped M0/M1 readers on the exact same entire test set. All 25,280 M2 predictions and their stages are inherited unchanged. Full three-method results are now compared; current batch wall time covers only the missing M0/M1 calls.')
        lines=[s.replace('Full-test expansion:', 'Full-test reader completion:').replace('See cache_reuse.json for context-capacity provenance.', 'See cache_reuse.json and prior_run_efficiency.json for exact reuse and prior-cost provenance.') for s in lines]
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');a=p.parse_args();analyze(a.partial)
