"""One-off source export only; does not import project code or run inference/scoring."""
import ast
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path('/home/data3/txy')
OUT=ROOT/'Documents/Codex/2026-09-24/cf_moa_v4_trigger_diagnosis_20260924'
V4=ROOT/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923'
OLD=ROOT/'Documents/Codex/2026-09-21/cf_moa'
EFFECT=OLD/'effect_first_revision_20260923'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
rows=[]
proofs={}

def add_proof(path,value,evidence,field):
    proofs.setdefault(str(path),[]).append(dict(sha256=value,evidence_path=str(evidence),evidence_sha256=sha(evidence),field=field))

# These are real executed-run locks, not a claim that the whole tree was frozen.
for p in [V4/'seeds/seed_43/m4/plan.json',V4/'seeds/seed_44/m5/plan.json',V4/'natural_runs/seed_42/m4/plan.json',V4/'natural_runs/seed_44/m5/plan.json']:
    for path,value in read(p).get('code_sources',{}).items():add_proof(path,value,p,'code_sources')
for path,value in read(OLD/'incremental_revision_20260923/baseline_contract/v2/receipt.json')['implementation'].items():
    add_proof(path,value,OLD/'incremental_revision_20260923/baseline_contract/v2/receipt.json','implementation')
p=OLD/'a5_f_preparation/strong_legacy_complete/m4/plan.json';q=read(p)['policy_source'];add_proof(q['path'],q['sha256'],p,'policy_source')
p=OLD/'a5_f_preparation/f_complete/m4/plan.json'
for rel,value in read(p)['code_lock'].items():add_proof(ROOT/'cf_moa'/rel,value,p,'code_lock')
for p in [V4/'analysis/historical121/receipt.json',V4/'analysis/natural52/receipt.json']:
    for x in read(p)['native_scorer_sources']:add_proof(x['path'],x['sha256'],p,'native_scorer_sources')
for p in [V4/'operations/f_toggle_receipt.json']:
    for key,val in read(p).items():
        if isinstance(val,dict):
            for path,h in val.items():
                if isinstance(path,str) and path.startswith(str(ROOT)) and isinstance(h,str) and len(h)==64:add_proof(path,h,p,key)
# Post-run delivery receipts bind the final wrapper and analysis without claiming
# those files generated the historical cached F.
p=V4/'operations/f_toggle_receipt.json'
for r in read(p)['sources']:add_proof(r['path'],r['sha256'],p,'sources')
p=V4/'analysis/natural52/receipt.json'
add_proof(V4/'analysis/score_and_compare.py',read(p)['script_sha256'],p,'script_sha256')
p=V4/'delivery_index.json'
for r in read(p)['artifacts']:
    if isinstance(r,dict) and 'path' in r and 'sha256' in r:add_proof(r['path'],r['sha256'],p,'artifacts')

# Config copy/source hashes are verified by the actual profile loader and run plan.
for role,methods in read(ROOT/'cf_moa/configs/native_sources.json').items():
    for method,value in methods.items():
        for p in [ROOT/'cf_moa/configs'/value['copy'],Path(value['path'])]:add_proof(p,value['sha256'],ROOT/'cf_moa/configs/native_sources.json',role+'/'+method)

files=subprocess.check_output(['rg','--files',str(OLD),str(V4)],text=True).splitlines()
byname={}
for p in files:
    if Path(p).suffix in ('.py','.json'):
        byname.setdefault(Path(p).name,[]).append(Path(p))

def snapshot(path,wanted):
    candidates=[]
    if str(path).startswith(str(ROOT/'cf_moa')):
        rel=path.relative_to(ROOT)
        candidates += [V4/'seeds/code_snapshot'/rel,V4/'final_source_snapshot'/rel,
                       OLD/'a5_f_preparation/frozen_code'/rel]
    candidates+=byname.get(path.name,[])
    for p in candidates:
        if p.exists() and sha(p)==wanted:return p
    if path.exists() and sha(path)==wanted:return path
    raise RuntimeError('No saved source with required runtime hash: '+str(path)+' '+wanted)

def export(path,*,group='v4_reanswer',wanted=None,evidence=None,role='active_runtime',dest=None):
    path=Path(path)
    current=sha(path) if path.exists() else None
    candidates=proofs.get(str(path),[])
    if wanted is None:
        # Prefer current if it matches a known run lock; otherwise label the gap.
        known=[r for r in candidates if r['sha256']==current]
        wanted=current
    else:known=[r for r in candidates if r['sha256']==wanted]
    selected=snapshot(path,wanted)
    if dest is None:dest=OUT/'source'/group/path.relative_to(ROOT)
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(selected.read_bytes())
    diff=None
    if current!=wanted and current is not None:
        diff=OUT/'source/diffs'/group/(str(path.relative_to(ROOT))+'.diff')
        diff.parent.mkdir(parents=True,exist_ok=True)
        diff.write_text(''.join(difflib.unified_diff(selected.read_text().splitlines(True),path.read_text().splitlines(True),fromfile='runtime/'+str(path.relative_to(ROOT)),tofile='current/'+str(path.relative_to(ROOT)))))
    rec=dict(exported_path=str(dest.relative_to(OUT)),logical_source_path=str(path),copied_from=str(selected),sha256=wanted,size_bytes=dest.stat().st_size,
             current_sha256=current,current_equal_runtime=current==wanted,role=role,
             provenance='run_hash_bound' if known or evidence else 'current_dependency_no_complete_run_hash_lock',
             run_hash_evidence=known+([evidence] if evidence else []),diff_path=str(diff.relative_to(OUT)) if diff else None)
    rows.append(rec);return rec

# Full files on the active F call path. Other branch imports are listed only.
starts=['agents/a5_premise.py','agents/a5_robust_readout.py','controller/strong_legacy.py','controller/baseline_native.py',
        'controller/minimal_operations.py','evaluation/minimal_f_runner.py','evaluation/effect_first_runner.py',
        'evaluation/native_scoring.py','evaluation/score_run.py','tools/native_backend.py','tools/adopted.py']
active=set('cf_moa/'+p for p in starts)|set('cf_moa/'+p for p in ['contracts.py','tools/adapters.py','tools/legacy.py','tools/vllm_backend.py','tools/schema_compat.py','evaluation/journal.py','evaluation/incremental_runner.py','evaluation/native_runner.py','evaluation/a4_repair.py','evaluation/paired_metrics.py'])
seen=set();todo=list(active);edges=[]
while todo:
    rel=todo.pop()
    if rel in seen or not (ROOT/rel).exists():continue
    seen.add(rel)
    for n in ast.walk(ast.parse((ROOT/rel).read_text())):
        mods=[n.module]+[n.module+'.'+a.name for a in n.names] if isinstance(n,ast.ImportFrom) and n.module else [a.name for a in n.names] if isinstance(n,ast.Import) else []
        for m in mods:
            target=m.replace('.','/')+'.py'
            if m.startswith('cf_moa') and (ROOT/target).exists():
                edges.append(dict(source=rel,target=target,lineno=n.lineno));todo.append(target)
for rel in sorted(active | {'cf_moa/agents/a4_intervention_execution.py','cf_moa/evaluation/resources.py'}):export(ROOT/rel,role='F_call_or_evaluation_chain')
for p in [ROOT/'cf_moa/__init__.py',ROOT/'cf_moa/agents/__init__.py',ROOT/'cf_moa/controller/__init__.py',ROOT/'cf_moa/tools/__init__.py',ROOT/'cf_moa/evaluation/__init__.py']:
    export(p,role='package_import')
for name in ['native_sources','readout_m4','readout_m5','minimal_system']:
    export(ROOT/f'cf_moa/configs/{name}.json',role='actual_profile_or_default_configuration')
export(ROOT/'Documents/Codex/2026-09-18/r5_head/delivery/r5_head.py',role='adopted_F_kernel_standard_library_only')
# Physical F acquisition used an older adapter/backend; preserve those byte-locked versions separately.
fplan=OLD/'a5_f_preparation/f_complete/m4/plan.json';flock=read(fplan)['code_lock']
for rel in ['agents/a5_robust_readout.py','evaluation/native_runner.py','tools/adapters.py','tools/native_backend.py','tools/schema_compat.py','tools/vllm_backend.py','contracts.py','tools/legacy.py','tools/adopted.py']:
    export(ROOT/'cf_moa'/rel,group='historical_F_acquisition',wanted=flock[rel],role='original_121_F_acquisition_runtime')
# Reused seed42 really ran an earlier effect_first_runner, with the same A5 module.
cplan=EFFECT/'a5_quality121/m4/plan.json'
for path,value in read(cplan)['code_sources'].items():
    export(Path(path),group='cycle1_seed42',wanted=value,evidence=dict(evidence_path=str(cplan),evidence_sha256=sha(cplan),field='code_sources',sha256=value),role='original_121_seed42_runtime')
# Actual scorer and old scoring entry; no AST execution occurs during export.
for x in read(V4/'analysis/natural52/receipt.json')['native_scorer_sources']:
    if Path(x['path']).suffix=='.py':export(Path(x['path']),group='offline_evaluation_only',wanted=x['sha256'],role='native_gold_scoring_dependency_not_inference')
for p in [V4/'analysis/score_and_compare.py',EFFECT/'score_development.py']:
    export(p,group='offline_evaluation_only',role='actual_analysis_entry')
# Legacy capability predicate and directly imported support-rule helpers.
legacy=ROOT/'Documents/Codex/2026-09-16/r1_head_experiments/candidate'
q=['r2_program_head.py'];oldseen=set()
while q:
    n=q.pop()
    if n in oldseen or not(legacy/n).exists():continue
    oldseen.add(n);export(legacy/n,group='adopted_dependencies',role='old_rule_eligibility_and_assembly')
    for node in ast.walk(ast.parse((legacy/n).read_text())):
        names=[node.module] if isinstance(node,ast.ImportFrom) and node.module else [a.name for a in node.names] if isinstance(node,ast.Import) else []
        q += [name+'.py' for name in names if (legacy/(name+'.py')).exists()]
# Current template bytes are supplied, with an explicit provenance limitation.
# Historical physical prompts remain the authoritative rendering evidence.
for method in ['m4','m5']:
    cfg=read(ROOT/f'cf_moa/configs/readout_{method}.json')
    for name in ['tokenizer_config.json','special_tokens_map.json','chat_template.jinja','config.json']:
        p=Path(cfg['model'])/name
        if p.exists():export(p,group='template_metadata',role='current_template_metadata_historical_exact_template_file_hash_not_logged')
# Minimal provenance inputs, not outputs/gold caches.
for i,p in enumerate([V4/'seeds/seed_43/plan.json',V4/'seeds/seed_43/m4/plan.json',V4/'seeds/seed_43/m5/plan.json',
                     V4/'natural_scope/plan_seed_42.json',EFFECT/'a5_quality121/m4/plan.json',EFFECT/'a5_quality121/m5/plan.json',
                     fplan,OLD/'a5_f_preparation/strong_legacy_complete/m4/plan.json',
                     OLD/'incremental_revision_20260923/baseline_contract/v2/receipt.json']):
    export(p,group='provenance',role='existing_run_provenance')
# Include all generated diffs in the manifest so they are reviewable artifacts.
for p in sorted((OUT/'source/diffs').rglob('*.diff')):
    rows.append(dict(exported_path=str(p.relative_to(OUT)),logical_source_path=None,copied_from=None,
        sha256=sha(p),size_bytes=p.stat().st_size,role='runtime_to_current_source_diff',provenance='derived_readonly_diff'))

# The export script is an audit utility written now, never a runtime method.
script=Path(__file__)
rows.append(dict(exported_path=str(script.relative_to(OUT)),logical_source_path=str(script),copied_from=str(script),sha256=sha(script),size_bytes=script.stat().st_size,role='one_off_export_utility_new_no_inference',provenance='created_for_this_export'))
manifest=dict(created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),scope='v4 F trigger source review, no new method',
    new_model_calls=0,replay_calls=0,native_scoring_calls=0,current_method_modified=False,files=rows,
    counts=dict(files=len(rows),bytes=sum(r['size_bytes'] for r in rows),provenance=dict(Counter(r['provenance'] for r in rows))),
    inactive_import_files_not_packaged=sorted(seen-active-{'cf_moa/agents/a4_intervention_execution.py','cf_moa/evaluation/resources.py'}),excluded_unneeded_canonical_labels=dict(path=read(V4/'analysis/natural52/receipt.json')['native_scorer_sources'][-1]['path'],sha256=read(V4/'analysis/natural52/receipt.json')['native_scorer_sources'][-1]['sha256'],reason='All selected triggers use F-supported formats; diagnosis canonical branch is irrelevant and not executed. A preparation copy was removed without using it for sample analysis or inference.'),template_provenance='Model template metadata files are current byte snapshots, not falsely labeled pre-run frozen. Actual physical prompts are preserved in sample records.',
    limitations=['Historical locks are partial; each file without a matching runtime lock is explicitly marked.',
                'Only the actual F branch and needed base helpers are packaged. Inactive import names are listed without copying their full module chains.',
                'Model weights, tokenizer vocabulary files, retrieval indexes, credentials, unrelated data and caches are excluded.',
                'No standalone installation or medical correctness certification is claimed.'])
(OUT/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest['counts'],ensure_ascii=False))
