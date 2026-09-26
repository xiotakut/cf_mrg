"""Build an immutable public snapshot from saved outputs; no inference or grader."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import shutil
from datetime import datetime

W = Path('/home/data3/txy')
R = W/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924'
PREP = R/'public_preparation/full_v5_publication_20260926'
GIT = W/'Documents/Codex/2026-09-24/cf_moa_github_rcv_progress'
OLD = GIT/'benchmarks/2026-09-25_cf_moa_rcv_completion_in_progress'
OUT = GIT/'benchmarks/2026-09-26_cf_moa_rcv_full_v5'
F = R/'full_v5'
records = {}

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def put(rel, data):
    p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return p

def copy(src, rel):
    dst=OUT/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
    records[rel]={'source_path':str(src),'source_sha256':digest(src),'transformation':'byte-identical copy'}

def gzcopy(src, rel):
    dst=OUT/rel; dst.parent.mkdir(parents=True,exist_ok=True)
    with src.open('rb') as a,dst.open('wb') as b,gzip.GzipFile(fileobj=b,mode='wb',mtime=0) as z:
        shutil.copyfileobj(a,z)
    records[rel]={'source_path':str(src),'source_sha256':digest(src),'transformation':'lossless gzip; decompressed bytes equal source'}

if not OUT.exists(): shutil.copytree(OLD,OUT)
old_manifest=json.loads((OLD/'SOURCE_MANIFEST.json').read_text())
for e in old_manifest['files']:
    records[e['path']]={k:v for k,v in e.items() if k not in ('path','sha256','bytes')}
    records[e['path']]['inherited_from']='2026-09-25_cf_moa_rcv_completion_in_progress'

for name in ['cf_moa.md','cf_moa_experiment_report.md']:
    copy(W/'docs/research'/name,'docs/research/'+name)

# Actual method source has not changed since the previous run snapshot.
source_checks=[]
for e in old_manifest['files']:
    if e['path'].startswith('source_snapshot/') and e.get('source_path'):
        p=Path(e['source_path'])
        assert p.exists() and digest(p)==e['sha256'], ('runtime source changed', str(p))
        source_checks.append({'path':e['path'],'sha256':e['sha256'],'matches_runtime_source':True})
put('evidence/runtime_source_comparison.json',{'checks':source_checks,'model_calls':0,'grader_calls':0})

for sub in ['parallel_gpu3_preparation','parallel_m5_preparation_20260926','listener_recovery_20260926','tail_m5_preparation_20260926']:
    for src in sorted((F/sub).glob('*.py')):
        copy(src,'execution_source/full_v5/'+sub+'/'+src.name)
copy(F/'analyze_full.py','analysis_source/full_v5/analyze_full.py')
copy(Path(__file__),'publication_source/build_publication.py')

metadata_fields={
 'per_input_status.jsonl':{'method','arm','request_id','analysis_status','native_mapping_count','correct','unavailable','answer_format'},
 'paired_atoms.jsonl':{'panel','model','metric','candidate','family_id','atom_id','baseline_score','candidate_score','weight','complete'},
 'family_effects.jsonl':{'model','candidate','metric','family_id','planned_atoms','completed_atoms','complete','paired_delta'},
 'native_units.jsonl':{'method','arm','unit_id','category','source','family_id','native_records','complete','score','pending_mappings','awaiting_score_mappings','unavailable_mappings'},
 'pairs.jsonl':{'method','arm','pair_id','family_id','relation','complete','both_correct','unavailable_endpoints','valid_relation'},
}
metadata_counts={}
private=[]
for model in ['m4','m5']:
    folder=F/'analysis'/model
    for name in ['quality_summary.json','receipt.json']:
        copy(folder/name,'data/full_v5/'+model+'/'+name)
    for name,fields in metadata_fields.items():
        count=0
        with (folder/name).open() as f:
            for line in f:
                row=json.loads(line); assert set(row)<=fields,(name,set(row)-fields);count+=1
        rel='data/full_v5/'+model+'/'+name+'.gz';gzcopy(folder/name,rel);metadata_counts[rel]=count
    receipt=json.loads((folder/'receipt.json').read_text())
    for e in receipt['input_sources']:
        p=Path(e['path'])
        private.append({'kind':'complete_native_proposals_and_F_verification_trace','model':model.upper(),**e,
          'lookup':'request_id / arm (task_id where present); full response remains private'})
        journal=p.parent/'journal.sqlite3'
        if journal.exists():private.append({'kind':'complete_model_request_response_journal','model':model.upper(),
          'path':str(journal),'bytes':journal.stat().st_size,'sha256':None,
          'hash_status':'not rehashed during publication; bind via saved transfer receipts and run identity',
          'opened_by_publication':False})
    for name in ['native_scored.jsonl','native_score_cache.sqlite3']:
        p=folder/name
        private.append({'kind':'offline_native_gold_and_scoring','model':model.upper(),'path':str(p),'bytes':p.stat().st_size,
           'sha256':None,'publication':'private; scores are public through metadata tables'})

status_paths=sorted(F.glob('**/runs/*/status.json'))
jobs=[]
for src in status_paths:
    rel=src.relative_to(F).as_posix();d=json.loads(src.read_text())
    assert d['status'] in ('complete','stopped_by_request','stopped_on_systemic_error'),rel
    dst='evidence/full_v5/'+rel;copy(src,dst)
    jobs.append({'source':str(src),'public_status':dst,'status':d['status'],'cost':d.get('cost'),
                 'inputs':d.get('inputs'),'planned_tasks':d.get('planned'),'complete':d.get('complete'),
                 'unavailable':d.get('unavailable'),'failed':d.get('failed'),'not_submitted':d.get('not_submitted')})
    sup=src.parent/'supervisor_result.json'
    if sup.exists():copy(sup,'evidence/full_v5/'+sup.relative_to(F).as_posix())

evidence=[
 'listener_recovery_20260926/preparation_receipt.json',
 'listener_recovery_20260926/m4_listener/terminal_result.json',
 'readout_parallel_gpu13_20260925/transfer_receipt.json',
 'readout_parallel_gpu13_20260925/physical_cost_handoff.json',
 'readout_parallel_m5_20260926/transfer_receipt.json',
 'readout_tail_gpu123_20260926/transfer_receipt.json',
 'readout_tail_gpu123_20260926/plan_difference_receipt.json',
 'readout_tail_gpu123_20260926/handoff_result.json',
 'readout_tail_gpu123_20260926/analysis_config.resolved.json',
 'readout_tail_gpu123_20260926/analysis_listener/terminal_result.json',
 'parallel_m5_preparation_20260926/tail_preparation_receipt.json',
]
for rel in evidence: copy(F/rel,'evidence/full_v5/'+rel)
put('data/execution_status_snapshot.json',{'status':'all_model_and_native_analysis_jobs_finished','as_of':'2026-09-26T18:44:00+08:00',
 'jobs':jobs,'resource_observation':'GPU1/2/3 retain existing user-authorized holders; GPU0 free at observation',
 'process_actions_during_publication':0,'automatic_experiment_queue':'stopped'})
copy(R/'resources/progress_check_20260926_1844.json','evidence/progress_check_20260926_1844.json')

plan_sources=[F/'plan.json',F/'readout_tail_gpu123_20260926/gpu2/plan.json']
for n,src in enumerate(plan_sources):
    d=json.loads(src.read_text())
    projection={k:v for k,v in d.items() if k!='methods'}
    projection['methods']={k:{x:y for x,y in v.items() if x!='tasks'} for k,v in d['methods'].items()}
    projection['task_manifests']='Private full plans; request identifiers and scored status exported separately without inputs.'
    projection['source_plan_sha256']=digest(src)
    projection['source_plan_path']=str(src)
    put('configs/'+['full_v5.resolved.json','m5_tail_actual.resolved.json'][n],projection)
for model,src in [('M4',F/'readout_parallel_gpu13_20260925/gpu1/plan.json'),('M5',plan_sources[1])]:
    if not src.exists():
        matches=list((F/'readout_parallel_gpu13_20260925').glob('**/*plan*.json'))
        raise RuntimeError((str(src),[str(x) for x in matches]))
    d=json.loads(src.read_text());put('configs/'+model+'_actual_profiles.json',{'model':model,
      'profiles':d['profiles'][model],'source_plan':str(src),'source_plan_sha256':digest(src),
      'verification_seed':d['verification_seed'],'per_task_budget':d['per_task_budget']})

cost=PREP/'cost_inventory.json'
assert cost.exists(),'cost inventory must be produced from saved status first'
copy(cost,'data/full_v5_new_physical_cost.json')
put('data/private_artifact_index.json',{'root':str(R),'scope':'Actual completed full-v5 artifacts; not uploaded raw clinical data',
 'records':private,'additional_private_paths':{'inputs':str(F/'inference'),'offline_gold':str(F/'offline'),
 'old_panels_index':'../2026-09-25_cf_moa_rcv_completion_in_progress/data/private_artifact_index.json'},
 'public_scope':'Losslessly compressed identifiers, status, metrics, family atoms, pairs, source paths, hashes and aggregate cost. No full messages, raw model response, patient text, gold content or SQL.'})
runtime=json.loads((OUT/'runtime_identity.json').read_text());runtime['status']='full_v5_run_completed_20260926'
runtime['active_full_v5_driver']['status']='actual_executed_version_now_finished'
runtime['actual_profiles']='configs/';runtime['future_replica_not_executed']=True
put('runtime_identity.json',runtime)
put('data/public_delivery_index.json',{
 'status':'complete_full_v5_regression; overall_research_plan_incomplete',
 'at':datetime.now().astimezone().isoformat(),'main':'a5_candidate_with_rationales_v1','default_B_unchanged':True,
 'full_report':'docs/research/cf_moa_experiment_report.md#rcv-full-v5-results-20260926',
 'run_and_delivery':'RUN_AND_DELIVERY.md','source_snapshot':'source_snapshot/','execution_recovery_source':'execution_source/',
 'configuration':'configs/','resolved_spec':'method_spec.resolved.json','runtime_identity':'runtime_identity.json',
 'quality':{m:'data/full_v5/'+m+'/quality_summary.json' for m in ['m4','m5']},
 'metadata':metadata_counts,'metadata_compression':'gzip, unchanged decompressed original bytes',
 'physical_new_cost':'data/full_v5_new_physical_cost.json','earlier_completed_stage_cost':'data/completed_new_physical_cost.json',
 'cost_attribution_note':'Full-v5 17 closed physical sources do not duplicate inherited callback prefixes. Earlier stage table overlaps catalog/readout16: do not add its total. Per-method attributed full costs including inherited pools not finalized.',
 'trace_private_index':'data/private_artifact_index.json','job_snapshot':'data/execution_status_snapshot.json',
 'development_121_52_tables':'data/tables/five_tables.md','earlier_development_family_CI':'data/statistics/paired_effects.json',
 'pending':['Full-v5 family bootstrap intervals','Full per-method attributed cost and final five integrated tables',
 'Natural52 M5 original C0 missing four','Common freeze and post-freeze confirmation','Independent F generation replica','Final adoption decision'],
 'publication_model_calls':0,'publication_grader_calls':0,'publication_process_actions':0})
put('evidence/metadata_export_validation.json',{'rows':metadata_counts,'allowlisted_fields':{k:sorted(v) for k,v in metadata_fields.items()},
 'new_model_calls':0,'new_grader_calls':0,'native_scored_raw_exported':False})
(PREP/'staged_source_map.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'package':str(OUT),'metadata_rows':metadata_counts,'runtime_source_checks':len(source_checks)},ensure_ascii=False))
