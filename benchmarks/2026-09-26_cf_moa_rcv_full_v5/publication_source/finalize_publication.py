from pathlib import Path
import ast,gzip,hashlib,json,os,re,shutil
from datetime import datetime

W=Path('/home/data3/txy')
R=W/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924'
P=R/'public_preparation/full_v5_publication_20260926'
G=W/'Documents/Codex/2026-09-24/cf_moa_github_rcv_progress'
O=G/'benchmarks/2026-09-26_cf_moa_rcv_full_v5'
records=json.loads((P/'staged_source_map.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def copy(src,rel):
 dst=O/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 records[rel]={'source_path':str(src),'source_sha256':sha(src),'transformation':'byte-identical copy'}
for rel in ['full_v5/readout_parallel_m5_20260926/gpu2_initialization_failure.json',
 'full_v5/readout_parallel_m5_20260926/gpu2_recovery1/failure_summary.json',
 'full_v5/readout_parallel_gpu13_20260925/analysis_listener/status.json',
 'c0_missing_natural/m5_live/run/status.json','c0_missing_natural/m5_live/run/supervisor_result.json']:
 copy(R/rel,'evidence/'+rel)
for name in ['write_delivery.py','finalize_publication.py']:
 copy(P/name,'publication_source/'+name)
copy(W/'docs/research/cf_moa_experiment_report.md','docs/research/cf_moa_experiment_report.md')

# The ongoing private master is not an audited public trace export.
master=O/'docs/research/cf_moa.md'
master.write_text('''# CF-MoA持续记录：公开导航

本页是冻结发布包的导航，不是服务器持续主记录的全文副本。

完整公开研究历史、失败/负结果及2026-09-26全量结果见[完整报告](cf_moa_experiment_report.md#rcv-full-v5-results-20260926)。

本轮运行过程与代码、配置、逐题trace及成本索引见[RUN_AND_DELIVERY](../../RUN_AND_DELIVERY.md)。完整患者输入、模型请求响应及离线gold保留服务器，见[私有制品索引](../../data/private_artifact_index.json)。

全量开发已完成，冻结后验证仍未完成；旧默认B保持。此前公开版本及本地完整过程记录不覆盖。
''')
records['docs/research/cf_moa.md']={'transformation':'public navigation only; not private master copy'}

# Resolve public artifacts inside the report; unmapped absolute paths are explicitly private.
mapping={v['source_path']:k for k,v in records.items() if v.get('source_path')}
mapping[str(R/'full_v5/analysis/m4')]='data/full_v5/m4'
mapping[str(R/'full_v5/analysis/m5')]='data/full_v5/m5'
mapping[str(R/'table_supplement/five_tables.md')]='data/tables/five_tables.md'
report=O/'docs/research/cf_moa_experiment_report.md'
body=report.read_text(); count=[0]
def subst(m):
 target=m.group(2); base,sep,anchor=target.partition('#')
 if base not in mapping:return m.group(0)
 dest=os.path.relpath(O/mapping[base],report.parent)
 count[0]+=1
 return '['+m.group(1)+']('+dest+(sep+anchor if sep else '')+')'
body=re.sub(r'\[([^\]]+)\]\((/home/data3/txy/[^)]+)\)',subst,body)
body=body.replace('## 阅读导航','公开阅读说明：指向`/home/data3/txy/`的未转换链接是服务器私有证据位置；本包可直接阅读的源码、结果和费用见[公开交付索引](../../RUN_AND_DELIVERY.md)。\n\n## 阅读导航',1)
report.write_text(body)
records['docs/research/cf_moa_experiment_report.md']['transformation']='research text preserved; public artifact links resolved, publication scope note added'

# Keep earlier files as dated snapshots, and link the new result above prior navigation.
for name,prefix in [('README.md','benchmarks/'),('benchmarks/README.md','')]:
 file=G/name;body=file.read_text()
 title='**2026-09-26 · RCV完整v5回归已完成：'
 if not body.startswith(title):
  link=prefix+'2026-09-26_cf_moa_rcv_full_v5/'
  intro=title+f'[完整报告第16章]({link}docs/research/cf_moa_experiment_report.md#rcv-full-v5-results-20260926) · [运行结果、源码/配置/逐题trace与成本索引]({link}RUN_AND_DELIVERY.md)。M4/M5各13,905输入、六臂原生评分齐全；主C3相对B原生ALL为−1.8108/+0.9273个百分点，旧默认B保持。全量新增162,979物理调用；冻结后确认、全量区间及最终方法费用仍待完成，不能称整个研究计划完成。**\n\n'
  file.write_text(intro+body)

checks={'python_ast_files':0,'json_files':0,'jsonl_rows':0,'gzip_rows':0,'byte_copies':0,'gzip_byte_checks':0,'report_public_links_resolved':count[0]}
for f in sorted(O.rglob('*')):
 if not f.is_file() or f.name=='SOURCE_MANIFEST.json':continue
 rel=f.relative_to(O).as_posix()
 if f.suffix=='.py':ast.parse(f.read_text());checks['python_ast_files']+=1
 if f.suffix=='.json':json.loads(f.read_text());checks['json_files']+=1
 if f.suffix=='.jsonl':
  with f.open() as z:
   for line in z:json.loads(line);checks['jsonl_rows']+=1
 if f.name.endswith('.jsonl.gz'):
  with gzip.open(f,'rt') as z:
   for line in z:json.loads(line);checks['gzip_rows']+=1
 e=records.get(rel,{})
 if e.get('transformation')=='byte-identical copy':
  assert sha(f)==e['source_sha256'],rel;checks['byte_copies']+=1
 if (e.get('transformation') or '').startswith('lossless gzip'):
  with gzip.open(f,'rb') as z:d=hashlib.sha256(z.read()).hexdigest()
  assert d==e['source_sha256'],rel;checks['gzip_byte_checks']+=1
assert checks['gzip_rows']==671756,checks
# Human entry links must all resolve inside the repository.
broken=[]
for name in ['README.md','RUN_AND_DELIVERY.md','PRIVATE_ARTIFACTS.md']:
 file=O/name
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if target.startswith(('http','#')):continue
  target=target.split('#')[0]
  if not (file.parent/target).exists():broken.append((name,target))
assert not broken,broken
checks['human_entry_links']='all local targets exist'
checks['frozen_source_whitespace']='Four copied scheduler test files retain an existing final blank line to preserve source bytes; no other git whitespace issues.'
checks['model_calls']=checks['grader_calls']=checks['process_actions']=0
(O/'evidence/publication_validation.json').write_text(json.dumps(checks,indent=2)+'\n')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file() or f.name=='SOURCE_MANIFEST.json':continue
 rel=f.relative_to(O).as_posix()
 files.append({'path':rel,'sha256':sha(f),'bytes':f.stat().st_size,**records.get(rel,{'transformation':'publication metadata or authored summary from indexed saved sources'})})
manifest={'status':'frozen_publication_snapshot','at':datetime.now().astimezone().isoformat(),
 'excludes_self':True,'scope':'complete full-v5 regression; research confirmation pending','file_count_excluding_manifest':len(files),'files':files}
(O/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(P/'package_validation.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({'files':len(files)+1,'bytes':sum(x['bytes'] for x in files),'checks':checks},ensure_ascii=False))
