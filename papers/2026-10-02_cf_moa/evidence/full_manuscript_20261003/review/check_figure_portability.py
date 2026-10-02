from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile
root=Path('/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript')
script=root/'scripts/build_paper_figures.py'
python='/home/data3/txy/MedRGAG/.venv/bin/python'
old=json.loads((root/'review/figure_portability_before.json').read_text())
tmp=Path(tempfile.mkdtemp(prefix='cf_moa_portability_'))
inputs=tmp/'frozen-inputs'
shutil.copytree(root/'inputs/figures',inputs)
missing=tmp/'workspace-does-not-exist'
assert not missing.exists()
clone=tmp/'copy/scripts/build_paper_figures.py';clone.parent.mkdir(parents=True)
code=script.read_text()
assert code.count("WORKSPACE = Path('/home/data3/txy')")==1
clone.write_text(code.replace("WORKSPACE = Path('/home/data3/txy')",f'WORKSPACE = Path({str(missing)!r})'))
runner=tmp/'guarded_build.py'
runner.write_text('''from pathlib import Path
import json,os,runpy,sys
script,inputdir,outdir,reviewdir,missing,logfile=sys.argv[1:]
blocked=[];source_reads=[]
def guard(event,args):
    if event!='open' or not isinstance(args[0],(str,bytes,os.PathLike)):return
    path=os.fsdecode(os.fspath(args[0]))
    absolute=str(Path(path).absolute())
    forbidden=(absolute.startswith('/home/data3/txy/') and not absolute.startswith('/home/data3/txy/MedRGAG/.venv/')) or absolute.startswith(missing)
    if forbidden:
        blocked.append(absolute)
        raise RuntimeError('External workspace access forbidden: '+absolute)
    if absolute.startswith(inputdir):source_reads.append(absolute)
sys.addaudithook(guard)
for check in (False,True):
    sys.argv=[script,'--input-dir',inputdir,'--output-dir',outdir,'--review-dir',reviewdir]+(['--check-only'] if check else [])
    runpy.run_path(script,run_name='__main__')
Path(logfile).write_text(json.dumps({'blocked_workspace_accesses':blocked,'frozen_input_read_paths':sorted(set(source_reads))},indent=2)+'\\n')
''')
env=dict(os.environ,MPLCONFIGDIR=str(tmp/'mpl-cache'))
portable=subprocess.run([python,str(runner),str(clone),str(inputs),str(tmp/'portable-output'),str(tmp/'portable-review'),str(missing),str(tmp/'access_log.json')],cwd='/tmp',env=env,text=True,capture_output=True)
assert portable.returncode==0,portable.stderr
actual=subprocess.run([python,str(script),'--input-dir',str(inputs),'--output-dir',str(tmp/'actual-output'),'--review-dir',str(tmp/'actual-review')],cwd='/tmp',env=env,text=True,capture_output=True)
assert actual.returncode==0,actual.stderr
check=subprocess.run([python,str(script),'--input-dir',str(inputs),'--output-dir',str(tmp/'actual-output'),'--review-dir',str(tmp/'actual-review'),'--check-only'],cwd='/tmp',env=env,text=True,capture_output=True)
assert check.returncode==0,check.stderr
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for row in old['outputs']:
    expected=row['sha256'];rel=row['file']
    assert h(root/'draft'/rel)==expected,(rel,'canonical changed')
    assert h(tmp/'portable-output'/rel)==expected,(rel,'portable differs')
    assert h(tmp/'actual-output'/rel)==expected,(rel,'actual differs')
    checks.append({'file':rel,'sha256':expected,'original_unchanged':True,'portable_build_identical':True,'actual_script_build_identical':True})
a=json.loads((tmp/'actual-review/figure_audit.json').read_text())
a['visual_review']=old['visual_review']
a['visual_review']['portability_patch']='Prior visual review remains valid: all 12 rendered/table artifacts are byte-identical after the metadata-only portability repair.'
(root/'review/figure_audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
canonical_check=subprocess.run([python,str(script),'--check-only'],cwd='/tmp',env=env,text=True,capture_output=True)
assert canonical_check.returncode==0,canonical_check.stderr
access=json.loads((tmp/'access_log.json').read_text())
receipt={'passed':True,'workdir':'/tmp','temporary_package':str(tmp),'original_script_sha256':old['script_sha256'],'updated_script_sha256':h(script),'test_copy_script_sha256':h(clone),'test_copy_only_change':'WORKSPACE assigned to an absent path','absent_workspace':str(missing),'absent_workspace_exists':missing.exists(),'manifest_sha256':h(root/'inputs/figures/manifest.json'),'guard':'Python open audit hook rejects original workspace access except interpreter runtime under MedRGAG/.venv, and rejects all accesses to the absent test workspace. Matplotlib cache placed in temporary directory.','access_check':access,'checks':checks,'check_only_results':{'copied_script':portable.stdout.strip(),'actual_script_custom_paths':check.stdout.strip(),'actual_script_defaults_from_tmp':canonical_check.stdout.strip()},'new_model_calls':0,'new_grading_calls':0}
(root/'review/figure_portability_check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'tmp':str(tmp),'byte_identical_outputs':len(checks),'blocked_workspace_access_attempts':len(access['blocked_workspace_accesses']),'updated_script_sha256':h(script)},indent=2))
