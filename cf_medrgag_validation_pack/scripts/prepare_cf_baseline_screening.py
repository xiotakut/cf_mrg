#!/usr/bin/env python3
"""Pinned public-source acquisition and output-blind baseline screening sample."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import json
import os
from pathlib import Path
import random
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / os.environ.get('CF_SCREENING_OUTPUT', 'results_cf_screening')
RAW = ROOT / 'private_data/cf_screening_sources'
SEED = 20260906
CULT_REV = '5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f'
CULT_REPO = 'HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs'

def read(path):
    with Path(path).open() as stream:
        return [json.loads(s) for s in stream if s.strip()]

def write(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))

def norm(text):
    return ' '.join(str(text).casefold().split()).strip(' .,:;!?"')

def download(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        for attempt in range(3):
            try:
                data = urllib.request.urlopen(url, timeout=90).read()
                path.write_bytes(data)
                break
            except Exception:
                if attempt == 2:
                    raise
    return path

def acquire():
    entries = json.loads((ROOT/'configs/gate_a_sources.json').read_text())['datasets']
    paths, provenance = {}, {}
    for ds in ['medeinst', 'medpic', 'cpv', 'medcounterfact']:
        e = entries[ds]
        paths[ds] = []
        for i, name in enumerate(e.get('files', [e.get('file')])):
            prefix = f"https://raw.githubusercontent.com/{e['repo_id']}/{e['revision']}/" if e['source']=='github' else f"https://huggingface.co/datasets/{e['repo_id']}/resolve/{e['revision']}/"
            cached = ROOT/'private_data/gate-a-public-20260823-seed13-v3/raw'/ds/e['revision']/f'{i:02d}-{Path(name).name}'
            path = cached if cached.exists() else RAW/ds/e['revision']/Path(name).name
            paths[ds].append(download(prefix+name, path))
        provenance[ds] = {k:e[k] for k in ['repo_id','revision','license','url']}
        provenance[ds]['paths'] = list(map(str,paths[ds]))
    paths['cultural'] = [download(f'https://raw.githubusercontent.com/{CULT_REPO}/{CULT_REV}/{name}', RAW/('cultural_'+Path(name).name)) for name in ['Data/final_augment_test_questions.json','Data/test.jsonl']]
    provenance['cultural'] = {'repo_id':CULT_REPO,'revision':CULT_REV,'license':{'declared':None,'status':'no repository license; public author research release; no text redistribution'},'url':f'https://github.com/{CULT_REPO}','paths':list(map(str,paths['cultural']))}
    (OUT/'acquisition.json').write_text(json.dumps(provenance,indent=2))
    return paths, provenance

def exposure(test):
    """Exact complete narrative matching; bare case IDs never establish exposure."""
    lookup = defaultdict(set)
    for r in test:
        lookup[norm(r['narrative'])].add(r['case_id'])
    found, files = defaultdict(set), []
    # Historical inputs, test/dev/calibration tails, and early DeltaRev are all scanned.
    # Raw full releases and retrieval/generation caches are assets, not exposure.
    for path in sorted(ROOT.rglob('*.jsonl')):
        rel = path.relative_to(ROOT)
        if any(x in rel.parts for x in ['raw','cache','cf_screening_sources','results_cf_screening','results_cf_full_test','deltarank_sources','clir-full-e7e1733']):
            continue
        files.append(str(rel))
        def walk(v):
            if isinstance(v, dict):
                for x in v.values(): yield from walk(x)
            elif isinstance(v,list):
                for x in v: yield from walk(x)
            elif isinstance(v,str) and len(v)>100:
                yield v
        for row in read(path):
            for text in walk(row):
                s = norm(text)
                # Known old task suffix; do not compare short clinical fragments.
                s = s.split(' which diagnosis best fits this patient')[0].rstrip(' .')
                for case in lookup.get(s,[]): found[case].add(str(rel))
    return found, files

def prepare(tier):
    OUT.mkdir(exist_ok=True)
    if (OUT/'screening_items.jsonl').exists():
        raise SystemExit('Prepared sample already exists. Reuse it; do not silently resample.')
    paths, provenance = acquire()
    frozen_plan=json.loads((OUT/'sample_plan.json').read_text()) if (OUT/'sample_plan.json').exists() else None
    import pyarrow.parquet as pq
    test = read(paths['medeinst'][0])
    medpic = json.loads(paths['medpic'][0].read_text())
    cpv = pq.read_table(paths['cpv'][0]).to_pylist()
    original, replaced = map(read, paths['medcounterfact'])
    cultural = json.loads(paths['cultural'][0].read_text())
    culture_sources = {norm(r['question']):r for r in read(paths['cultural'][1])}
    exposed, scanned = exposure(test)
    (OUT/'exposure_audit.json').write_text(json.dumps({'matching':'normalized complete narrative; case_id only after text verification','scanned_files':scanned,'exposed_test_case_count':len(exposed)},indent=2))
    previous=ROOT/'results_cf_screening'
    prior_items=read(previous/'screening_items.jsonl') if tier=='full-test' else []
    prior_plan=json.loads((previous/'sample_plan.json').read_text()) if prior_items else None
    if prior_items:
        used={norm(r['question']) for r in prior_items if r['answer_format']=='diagnosis'}
        for r in test:
            if norm(r['narrative']) in used:exposed[r['case_id']].add('results_cf_screening/screening_items.jsonl')
        (OUT/'exposure_audit.json').write_text(json.dumps({'matching':'normalized complete narrative, including completed prior screening inputs','scanned_files':scanned+['results_cf_screening/screening_items.jsonl'],'exposed_test_case_count':len(exposed)},indent=2))
    nmed,ncpv,nmcf = (len(test),len(cpv),len(original)) if tier=='full-test' else (300,60,80) if tier=='full' else (200,40,60)
    rng = random.Random(SEED)
    pairs=defaultdict(dict)
    for r in test:
        assert r['case_type'] not in pairs[r['case_id']]
        pairs[r['case_id']][r['case_type']]=r
    valid = sorted(k for k,v in pairs.items() if set(v)=={'control','trap'})
    fresh=[k for k in valid if k not in exposed]; old=[k for k in valid if k in exposed]
    rng.shuffle(fresh);rng.shuffle(old)
    selected=(fresh+old)[:nmed]
    if frozen_plan:selected=frozen_plan['primary_medeinst_groups']
    # Frozen options are accepted only with exact matching narratives for BOTH members.
    frozen={}
    for f in sorted(ROOT.glob('results_*/*.jsonl')):
        if f.name not in {'dev.jsonl','test.jsonl','fresh_test.jsonl','calibration.jsonl'}:continue
        for r in read(f):
            case=r.get('source_case_id')
            if case in pairs and 'four_way' in r.get('views',{}) and all(norm(r.get(m,{}).get('narrative',''))==norm(pairs[case][m]['narrative']) for m in ['control','trap']):
                frozen.setdefault(case, ({k:v['label'] for k,v in r['views']['four_way'].items()},str(f.relative_to(ROOT))))
    auxiliary=[k for k in selected if k in frozen]
    extra=sorted(set(frozen)-set(selected));rng.shuffle(extra)
    auxiliary=(auxiliary+extra)[:60]
    if frozen_plan:auxiliary=frozen_plan['auxiliary_medeinst_groups']
    elif prior_plan:auxiliary=prior_plan['auxiliary_medeinst_groups']
    inputs=list(prior_items);labels=[];tax=[]
    dedup={json.dumps({k:v for k,v in r.items() if k!='item_id'},sort_keys=True,ensure_ascii=False):r['item_id'] for r in inputs}
    def add(ds, source, role, question, options, gold, fmt, *, protocol='native', evidence=None, operation=None, **extra):
        item={'question':question,'options':options,'fixed_evidence':evidence or [],'answer_format':fmt}
        key=json.dumps(item,sort_keys=True,ensure_ascii=False)
        if key not in dedup:
            dedup[key]=f's{len(inputs):06d}'
            inputs.append({'item_id':dedup[key],**item})
        item_id=dedup[key]; group=f'{ds}:{source}'
        row={'item_id':item_id,'dataset':ds,'source_id':str(source),'group_id':group,'role':role,'gold':gold,'protocol':protocol,'answer_format':fmt,'revision':provenance[ds]['revision'],**extra}
        labels.append(row)
        task='clinical_update' if ds in ['medeinst','medpic'] else 'hypothetical_evidence_world' if ds=='medcounterfact' else 'answer_invariance'
        family={'medeinst':'DDXPlus','medpic':'clinical_guidelines','cpv':'MedQA','cultural':'MedQA','medcounterfact':'MedEvidence'}[ds]
        tax.append({k:row[k] for k in ['item_id','dataset','group_id','role','protocol']} | {'task_contract':task,'operation_tags':operation or [],'clinical_target':{'medeinst':'diagnosis','medpic':'medication_eligibility_safety','cpv':'medical_QA','cultural':'medical_QA','medcounterfact':'evidence_comparison'}[ds],'expected_answer_relation':'unknown','edit_scope':'unresolved','answer_format':fmt,'original_source_family':family,'construction_family':ds,'native_or_derived':protocol,'pair_mapping_status':'unavailable' if ds=='medpic' else 'official','annotation_source':'official metadata and frozen deterministic rules','annotation_confidence':'low' if ds=='medeinst' else 'medium'})
        return row
    for case in selected+[k for k in auxiliary if k not in selected]:
        for member in ['control','trap']:
            r=pairs[case][member]
            add('medeinst',case,'reference' if member=='control' else 'variant',r['narrative'],{},r['ground_truth'],'diagnosis',operation=[] if member=='control' else ['mixed_or_unresolved'],previously_exposed=case in exposed,exposure_files=sorted(exposed.get(case,())),additional_native=case not in selected,official_split='test')
        if case in auxiliary:
            options,asset=frozen[case]
            for member in ['control','trap']:
                r=pairs[case][member];gold=next(k for k,v in options.items() if v==r['ground_truth'])
                add('medeinst',case,'reference' if member=='control' else 'variant',r['narrative']+'\n\nWhich diagnosis best fits this patient?',options,gold,'single',protocol='derived_four_way',operation=[] if member=='control' else ['mixed_or_unresolved'],previously_exposed=case in exposed,option_asset=asset,official_split='test')
    for r in medpic:
        info=r['taxonomy_patient_info_type'];op='measurement_threshold' if 'threshold' in info else 'presence_polarity' if info in ['disease presence','pregnancy status'] else 'mixed_or_unresolved'
        add('medpic',r['instance_id'],r['benchmark_task_family'],r['patient_vignette']+'\n\n'+r['question'],r['options'],sorted(r['answer']),'multi',operation=[] if r['benchmark_task_family']=='guideline_following' else [op],official_operation=r['taxonomy_reasoning_operation'],patient_info_type=info,department=r['taxonomy_clinical_department'])
    cg=defaultdict(list)
    for r in cpv:cg[r['case_id']].append(r)
    ids=sorted(cg);rng.shuffle(ids)
    if frozen_plan:ids=frozen_plan['cpv_groups']
    for case in ids[:ncpv]:
        rows=cg[case];r=rows[0];options={k:r['option_'+k.lower()] for k in 'ABCD'}
        assert all(x['question']==r['question'] and x['answer_idx']==r['answer_idx'] and all(x['option_'+k.lower()]==options[k] for k in options) for x in rows)
        add('cpv',case,'reference',r['question'],options,r['answer_idx'],'single',reference_status='authentic_official_original_question')
        for i,x in enumerate(rows):
            gender=next(k for k in ['male','female','none'] if x['gender_'+k])
            # Pre-output flags are conservative proxies, not clinical adjudication.
            noop=norm(x['case_text'])==norm(x['question'])
            conflict=bool(re.search(r'\b(pregnan\w*|gravida|prostate|testicular|ovarian|ovary|uterus)\b',x['case_text'],re.I))
            eligible=bool(re.search(r'\b\d+-year-old\b',x['question']))
            add('cpv',case,f'variant_{i:02}',x['case_text'],options,x['answer_idx'],'single',operation=['identity_attribute'],gender=gender,ethnicity=x['ethnicity'],no_op=noop,patient_attribute_pattern=eligible,potential_clinical_conflict=conflict,reference_status='authentic_official_original_question')
    for i,r in enumerate(cultural):
        source=culture_sources[norm(r['original_question'])]
        assert source['options']==r['options'] and source['answer_idx']==r['answer_idx']
        add('cultural',i,'reference',r['original_question'],r['options'],r['answer_idx'],'single',condition='Original',culture=None,reference_mapping='normalized full original question AND exact options/gold in author test.jsonl')
        for culture in ['t1','t2','t3']:
            for k,condition in [('i','Id'),('c','Context'),('ic','Id+Context')]:
                add('cultural',i,culture+'_'+k,r[culture+'_question'][k],r['options'],r['answer_idx'],'single',condition=condition,culture=culture,operation=({'i':['identity_attribute'],'c':['contextual_addition'],'ic':['identity_attribute','contextual_addition']})[k])
    mg=defaultdict(list)
    for r in replaced:mg[str(r['metadata']['id'])].append(r)
    originals={str(r['metadata']['id']):r for r in original}
    mids=sorted(originals);rng.shuffle(mids)
    mids=mids[:nmcf]
    if frozen_plan:mids=frozen_plan['medcounterfact_groups']
    for case in mids:
        rows=[originals[case]]+mg[case]
        for i,r in enumerate(rows):
            m=r['metadata']
            add('medcounterfact',case,'reference' if i==0 else f'variant_{i}',r['question'],{},m['answer'],'relation',evidence=r['article_summaries'],operation=[] if i==0 else ['hypothetical_entity_replacement'],main_category=m.get('MainCategory','Original'),sub_category=m.get('SubCategory'),replacement=m.get('item'),original_review=m.get('original_review'),missing_categories=sorted({'OOD','ID','Nonsense tokens','Poison'}-{x['metadata'].get('MainCategory') for x in mg[case]}))
    # Semantics and cross-resource mappings belong only to evaluation.
    itemmap={r['item_id']:r for r in inputs}
    if tier=='full-test':
        by_input=defaultdict(list)
        for r in labels:by_input[r['item_id']].append(r)
        conflicts=[]
        for key,rows in by_input.items():
            if len({json.dumps(r['gold'],sort_keys=True) for r in rows})>1:
                conflicts.append({'item_id':key,'groups':[r['group_id'] for r in rows],'gold_values':[r['gold'] for r in rows]})
                for r in rows:r['identical_input_conflicting_gold']=True
        (OUT/'duplicate_gold_conflicts.json').write_text(json.dumps(conflicts,indent=2)+'\n')
    refs={(r['group_id'],r['protocol']):r for r in labels if r['role']=='reference'}
    def semantic(r):
        opts=itemmap[r['item_id']]['options']; g=r['gold']
        return sorted(norm(opts[x]) for x in g) if isinstance(g,list) else norm(opts.get(g,g))
    cross=defaultdict(list)
    for r,t in zip(labels,tax):
        ref=refs.get((r['group_id'],r['protocol']))
        r['reference_item_id']=ref['item_id'] if ref else None
        if ref:
            t['expected_answer_relation']='relation_transport' if r['dataset']=='medcounterfact' else 'invariant' if semantic(ref)==semantic(r) else 'change'
            r['expected_answer_relation']=t['expected_answer_relation']
            t['reference_length']=len(itemmap[ref['item_id']]['question'])
            t['edit_length']=len(itemmap[r['item_id']]['question'])-t['reference_length']
        if r['role']=='reference' and r['dataset'] in ['cpv','cultural']:
            q=norm(itemmap[r['item_id']]['question'])
            cross[q].append(r)
    overlaps=[]
    for values in cross.values():
        if len({r['dataset'] for r in values})<2:continue
        for r in values:
            for s in values:
                if r['dataset']>=s['dataset']:continue
                a=set(map(norm,itemmap[r['item_id']]['options'].values()));b=set(map(norm,itemmap[s['item_id']]['options'].values()))
                overlaps.append({'groups':[r['group_id'],s['group_id']],'status':'exact_question_options' if a==b else 'exact_question_different_native_options','source_family':'MedQA'})
    # Fixed five input smoke per dataset; independent 20-task seed repeat chosen now.
    smoke=[]
    for ds in provenance:
        candidates=list(dict.fromkeys(r['item_id'] for r in labels if r['dataset']==ds and r['protocol']=='native'))
        smoke+=candidates[:5]
    repeat=random.Random(SEED+1).sample([x['item_id'] for x in inputs],20)
    if prior_plan:repeat=prior_plan['repeat_item_ids'];smoke=prior_plan['smoke_item_ids']
    assert {r['item_id'] for r in labels}==set(itemmap), 'every retained inference input must belong to the prepared release'
    write(OUT/'screening_items.jsonl',inputs);write(OUT/'evaluation_labels.jsonl',labels);write(OUT/'taxonomy.jsonl',tax)
    (OUT/'source_overlap.json').write_text(json.dumps(overlaps,indent=2))
    plan={'seed':SEED,'candidate_tier':tier,'tier_frozen':False,'smoke_item_ids':smoke,'repeat_item_ids':repeat,'repeat_seed':SEED+1,'primary_medeinst_groups':selected,'auxiliary_medeinst_groups':auxiliary,'cpv_groups':ids[:ncpv],'medcounterfact_groups':mids,'cultural_groups':len(cultural),'neutral_available':False,'unique_inputs':len(inputs),'label_records':len(labels),'no_prediction_inspected':True}
    if frozen_plan:
        assert len(inputs)==frozen_plan['unique_inputs']
        plan=frozen_plan
    if tier=='full-test':
        plan.update(tier_frozen=True,scope='entire official test/released evaluation data; no source-group sampling',no_prediction_inspected=False,scope_decision='user expanded to all released test units after prior sampled results; no output-dependent inclusion',prior_unique_inputs=len(prior_items),repeat_scope='unchanged 20-input auxiliary repeat from prior screening; not a fresh random full-population sample')
        config=json.loads((ROOT/'configs/cf_baseline_screening.json').read_text());config['max_model_len']=98304
        (OUT/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (OUT/'sample_plan.json').write_text(json.dumps(plan,indent=2))
    canonical=sorted({r['ground_truth'] for r in test})
    train=ROOT/'private_data/deltarank_sources/medeinst_train.jsonl'
    if train.exists():canonical=sorted(set(canonical)|{r['ground_truth'] for r in read(train)})
    (OUT/'canonical_labels.json').write_text(json.dumps({'labels':canonical,'aliases':{},'source':'official MedEinst train/test ground_truth; no test-derived medical aliases','evaluator':'normalized exact screening, not official semantic evaluator'},indent=2))
    counts=[]
    def sample_role(r):
        return 'additional_native_sensitivity' if r.get('additional_native') else 'derived_sensitivity' if r['protocol']=='derived_four_way' else 'primary'
    for ds in provenance:
        for protocol in sorted({r['protocol'] for r in labels if r['dataset']==ds}):
            for role in sorted({sample_role(r) for r in labels if r['dataset']==ds and r['protocol']==protocol}):
                rr=[r for r in labels if r['dataset']==ds and r['protocol']==protocol and sample_role(r)==role]
                counts.append({'benchmark':ds,'protocol':protocol,'sample_role':role,'source_groups':len({r['group_id'] for r in rr}),'input_records':len(rr),'unique_inputs':len({r['item_id'] for r in rr}),'planned_method_predictions':3*len({r['item_id'] for r in rr})})
    with (OUT/'benchmark_summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(counts[0]),lineterminator='\n');w.writeheader();w.writerows(counts)
    checks=['# Five source-unit checks per benchmark','Inference receives only item_id, question, options, fixed_evidence, answer_format. No gold/group/role/taxonomy enters solver.','Full prepared inputs stay local and are not redistributed.']
    for ds in provenance:
        groups=list(dict.fromkeys(r['group_id'] for r in labels if r['dataset']==ds))[:5]
        for group in groups:
            rr=[r for r in labels if r['group_id']==group and r['protocol']=='native']
            checks += [f'\n## {group}',f'Revision: {provenance[ds]["revision"]}; records={len(rr)}; mapping={tax[labels.index(rr[0])]["pair_mapping_status"]}.']
            for r in rr[:2]:
                it=itemmap[r['item_id']]; checks += [f'- {r["item_id"]}: format={it["answer_format"]}; option keys={list(it["options"])}; evidence articles={len(it["fixed_evidence"])}; gold type={type(r["gold"]).__name__}; role={r["role"]}; input lengths={len(it["question"])}/{sum(map(len,it["fixed_evidence"]))}.']
    checks+=['\nPotential ambiguities: MedPIC has no official pair map; MedEinst multi-edit taxonomy remains unresolved; CPV no-op and sex-specific clinical text are flagged; Cultural Neutral absent and options can exceed four; MedCounterFact original metadata text never fills replacement input.','Raw source checks and complete prompts are retained locally; do not paste license-unclear text into Git.']
    (OUT/'data_checks.md').write_text('\n'.join(checks)+'\n')
    (OUT/'acquisition.md').write_text('# Acquisition\n\n'+ '\n'.join(f'- {ds}: [{v["repo_id"]}]({v["url"]}), revision `{v["revision"]}`; source files in acquisition.json.' for ds,v in provenance.items())+'\n\nReleased rows: MedEinst '+str(len(test))+f'; MedPIC {len(medpic)}; CPV {len(cpv)} in {len(cg)} groups; Cultural {len(cultural)} groups × 10 = {len(cultural)*10} inputs; MedCounterFact {len(original)} original + {len(replaced)} replaced. Cultural Neutral is absent. Four existing caches match current remote revisions checked 2026-09-06.\n\nCPV authentic question field is verified against author create.py (case_text and question both initialized from original MedQA question). Variants use case_text alone. Cultural originals all match author test.jsonl by complete normalized question, exact options and gold. No published model answers downloaded.\n\nMedPIC official pair map unavailable: GF–CF is unpaired_composition_gap. MedCounterFact aligns only metadata.id; original metadata.question and treatment fields never enter model inputs. Public author releases without repository license remain local; only download code, IDs and derived aggregate outputs are committed.\n')
    if prior_items:
        import hashlib
        import shutil
        assert OUT!=previous
        assert inputs[:len(prior_items)]==prior_items
        for name in ['main','repeat','repeat_independent','smoke_pre_evidence_dedup']:
            shutil.copytree(previous/'cache'/name,OUT/'cache'/name)
        digest=hashlib.sha256((OUT/'screening_items.jsonl').read_bytes()).hexdigest()
        for stamp in (OUT/'cache').glob('*/worker-*/inputs.sha256'):stamp.write_text(digest)
        for stamp in (OUT/'cache').glob('*/worker-*/config.json'):
            inherited=json.loads(stamp.read_text());assert inherited|{'max_model_len':98304}==config
            stamp.write_text(json.dumps(config,indent=2)+'\n')
        (OUT/'runtime').symlink_to(previous/'runtime',target_is_directory=True)
        for name in ['baseline_contract.md','environment.json','performance_test.json','rng_repeat_correction.json','flow.mmd','smoke_review.md','taxonomy_corrections.json','RESEARCH_PLAN.md']:
            shutil.copy2(previous/name,OUT/name)
        (OUT/'cache_reuse.json').write_text(json.dumps({'source':str(previous),'prior_unique_inputs':len(prior_items),'prior_predictions':3*len(prior_items),'reuse_basis':'exact visible-input equality; item IDs, seeds, model, templates, evidence, decoding and copied stage outputs unchanged','input_digest_update':'only after verifying the complete old input list is an identical prefix; independent cache copy preserves prior artifacts','context_capacity':{'prior':65536,'new':98304,'reason':'full released mandatory evidence plus unchanged KADS/documents exceeds previous capacity; no token budget or prompt change'},'prior_batch_wall_seconds':16316},indent=2))
    print(json.dumps({'counts':counts,'unique_inputs':len(inputs),'medeinst_unexposed_pool':len(fresh),'auxiliary_pairs':len(auxiliary),'source_overlaps':len(overlaps)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tier',choices=['full','compact','full-test'],default='full');a=p.parse_args();prepare(a.tier)
