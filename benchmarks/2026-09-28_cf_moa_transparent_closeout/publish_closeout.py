"""Stage only completed closeout artifacts, leaving private raw projections local."""
from pathlib import Path
import ast,gzip,hashlib,json,os,re,shutil
from datetime import datetime

W=Path('/home/data3/txy')
R=W/'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924'
S=R/'closeout_20260928'
G=W/'Documents/Codex/2026-09-24/cf_moa_github_rcv_progress'
O=G/'benchmarks/2026-09-28_cf_moa_transparent_closeout'
O.mkdir(parents=True,exist_ok=True)
records={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy(src,rel):
 dst=O/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 records[rel]={'source_path':str(src),'source_sha256':sha(src),'transformation':'byte-identical'}
def write(rel,data):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

# Refresh the local delivery hashes only after final text corrections.
index=json.loads((S/'delivery_index.json').read_text())
for e in index['artifacts']:
 p=S/e['path'];e.update(bytes=p.stat().st_size,sha256=sha(p))
(S/'delivery_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
root_files=['final_status.json','full_results.md','all_source_results.json','all_category_results.json','format_input_results.json',
 'family_effect_intervals.json','attributed_costs.md','scope_and_limitations.md','data_issues.jsonl','five_tables.md',
 'method_identity.final.json','delivery_index.json','table1_full_results.md','table2_all_strata.md','table3_rationales_and_operations.md',
 'table4_pairs_and_intervals.md','table5_cost_and_coverage.md','operation_ablations_reused.json','render_closeout.py','publish_closeout.py']
for rel in root_files:copy(S/rel,rel)
for sub in ['statistics','review']:
 for p in sorted((S/sub).rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or 'tmp' in p.relative_to(S/sub).parts:continue
  if p.suffix in ('.json','.jsonl','.md','.py','.log'):copy(p,p.relative_to(S).as_posix())
for name in ['attributed_costs.md','closeout_costs.py','sources.json','completion_receipt.json','per_method_costs.json','mechanism_coverage.json',
 'physical_reconciliation.json','transfer_cost_reconciliation.json','cost_correction_receipt.json','source_binding_verification.json',
 'per_input_cost_coverage.jsonl.gz']:
 copy(S/'costs'/name,'costs/'+name)
copy(R/'full_v5/analysis_preparation/summarize_mechanism_cost.py','analysis_source/summarize_mechanism_cost.py')
diff=json.loads((S/'costs/c2_c3_call_difference.json').read_text());redacted=0
for record in diff['records']:
 for e in record.get('trace',{}).get('errors',[]):
  if 'key' in e:
   e['key_sha256']=hashlib.sha256(json.dumps(e.pop('key'),ensure_ascii=False,sort_keys=True).encode()).hexdigest();redacted+=1
assert redacted==6
write('costs/c2_c3_call_difference.json',diff)
records['costs/c2_c3_call_difference.json']={'source_path':str(S/'costs/c2_c3_call_difference.json'),'source_sha256':sha(S/'costs/c2_c3_call_difference.json'),'transformation':'six private candidate keys replaced by hashes; request counts and errors unchanged'}
for name in ['README.md','01_Closeout_Without_Outcome_Filtering.md','02_CODING_AGENT_CLOSEOUT.md','03_Verified_Aggregate_Contrasts.md','verified_summary_excerpt.json']:
 copy(S/'source_request/extracted/CF_MoA_Full_V5_Closeout'/name,'plan/'+name)
copy(S/'source_request/download_receipt.json','plan/download_receipt.json')
copy(W/'cf_moa/CF_MED_MoA_Router_Five_Agents_Execution_Plan.md','plan/active_workspace_plan.md')
copy(W/'cf_moa/configs/execution_plan.json','plan/execution_plan_metadata.json')
copy(W/'docs/research/cf_moa_experiment_report.md','docs/research/cf_moa_experiment_report.md')

old='https://github.com/xiotakut/cf_mrg/blob/d85793470cf75af57217f3fdc73093f494d9f003/benchmarks/2026-09-26_cf_moa_rcv_full_v5/'
nav=O/'docs/research/cf_moa.md';nav.write_text('# 持续主记录公开导航\n\n'+
 '完整本阶段结果见[透明收尾报告](cf_moa_experiment_report.md#transparent-closeout-20260928)和[五表](../../five_tables.md)。服务器持续研究记录保留本地，完整私有病例/SQL不在公开包内。\n')
report=O/'docs/research/cf_moa_experiment_report.md';s=report.read_text()
for e in root_files:
 s=s.replace(']('+str(S/e)+')','](../../'+e+')')
s=s.replace('## 阅读导航','公开阅读说明：未转换的`/home/data3/txy/`链接是服务器私有证据位置；本轮公开交付见[README](../../README.md)，原d857934代码与输入元数据见[冻结包]('+old+'README.md)。\n\n## 阅读导航',1)
report.write_text(s);records['docs/research/cf_moa_experiment_report.md']['transformation']='original report with public closeout links and scope note'
notes=O/'review/scope_notes.md';s=notes.read_text();s=re.sub(r'\]\(\.\./\.\./\.\./cf_moa_github_rcv_progress/[^)]+/method_spec.resolved.json\)',']('+old+'method_spec.resolved.json)',s);notes.write_text(s);records['review/scope_notes.md']['transformation']='same review with frozen public method link'
(O/'README.md').write_text('''# CF-MoA完整v5透明收尾（2026-09-28）

**本阶段零新增推理收尾已完成；冻结后新家族确认与独立F复本未执行并延后。** 默认采用B保持，C3为显式研究扩展。原d857934结果、全部六臂与完整分母不覆盖、不按输赢筛选。

- [完整结果与三组主要对比](full_results.md)
- [五张完整表：全量、全部来源/类别/格式、理由与旧核消融、配对区间、成本/覆盖](five_tables.md)
- [完整过程报告第16.13节](docs/research/cf_moa_experiment_report.md#transparent-closeout-20260928)
- [阶段状态](final_status.json) · [归属成本](attributed_costs.md) · [范围与限制](scope_and_limitations.md) · [交付索引](public_delivery_index.json)

两骨干每臂13905输入、15616评分映射、6104非参考ALL单位保持。11来源、5格式、全部R类及36个5000次/seed240924家族区间齐全；区间仅描述已暴露开发数据，未校正选择偏差。

原生ALL C3−B：M4 −1.8108pp [−2.5287,−1.0819]；M5 +0.9273pp [0.3039,1.5562]。B−C0的收益来自已有采用组件，不是RCV新增贡献。C3相对无理由版本的正点差不等于稳定超过B。

每方法费用按共同B/旧head/F一次＋自身增量归属，未将162979多臂物理请求除以六。历史上游与部分旧模型秒保持unknown。空data_issues.jsonl表示本次有限既有证据未确立当前可更正缺陷，不意味着全数据无误。

所有本轮模型/原生grader/缓存写入/GPU进程操作为0。完整患者文本、原始模型请求响应、SQL及costs/projection内gold派生诊断留私有；公开逐输入费用/覆盖166860行无gold/原文，来源索引保留。

'''+f'代码与实际配置仍为[原d857934冻结快照]({old}README.md)、[解析规格]({old}method_spec.resolved.json)，不是新的算法版本。本包仅增加离线统计/费用收尾代码与产物。\n\n'+'''复现纯统计（在合法本地结果目录运行，OUT使用新目录）：

```bash
python statistics/scripts/summarize_existing_results.py --root EXISTING_DATA_FULL_V5 --out NEW_OUT --draws 5000 --seed 240924
```

成本脚本使用已有私有SQL和本地来源路径，见costs/sources.json与原始目录索引；公开包不包含SQL，不能仅凭公共元数据重建所有真实messages。主方法与原生分数没有重新生成。
''')
write('public_delivery_index.json',{'status':'complete_zero_new_inference_phase_closeout','base_commit':'d85793470cf75af57217f3fdc73093f494d9f003',
 'method_and_full_result_source':old+'README.md','completed':['full_results.md','all_source_results.json','all_category_results.json','format_input_results.json','family_effect_intervals.json','attributed_costs.md','scope_and_limitations.md','data_issues.jsonl','five_tables.md'],
 'final_status':'final_status.json','method_identity':'method_identity.final.json','statistics_receipt':'statistics/execution_receipt.json','statistics_validation':'statistics/validation_receipt.json','cost_receipt':'costs/completion_receipt.json','per_method_costs':'costs/per_method_costs.json','per_input_costs_and_coverage':'costs/per_input_cost_coverage.jsonl.gz','coverage':'costs/mechanism_coverage.json','raw_full_trace_index':old+'data/private_artifact_index.json','private_current_cost_projection':str(S/'costs/projection'),'source_manifest':'SOURCE_MANIFEST.json','deferred_not_executed':['postfreeze_confirmation','independent_F_replica','natural52_M5_C0_missing4'],'default_B_unchanged':True,'no_outcome_filtering':True,'new_model_calls':0,'new_grader_calls':0,'process_actions':0})

checks={'json':0,'python_AST':0,'gzip_rows':0,'new_model_calls':0,'new_grader_calls':0,'source_data_mutations':0,'candidate_keys_hashed':redacted}
for f in O.rglob('*'):
 if not f.is_file() or f.name=='SOURCE_MANIFEST.json':continue
 if f.suffix=='.json':json.loads(f.read_text());checks['json']+=1
 if f.suffix=='.py':ast.parse(f.read_text());checks['python_AST']+=1
 if f.name.endswith('.jsonl.gz'):
  with gzip.open(f,'rt') as z:
   for line in z:
    row=json.loads(line);checks['gzip_rows']+=1
    assert not any(k in row for k in ['gold','native_answer','question','messages','semantic_gold','correct'])
assert checks['gzip_rows']==166860
assert (O/'data_issues.jsonl').stat().st_size==0
for name in ['README.md','full_results.md','five_tables.md','scope_and_limitations.md','attributed_costs.md']:
 f=O/name
 for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if link.startswith(('http','#')):continue
  assert (f.parent/link.split('#')[0]).exists(),(name,link)
write('publication_validation.json',checks)
files=[]
for f in sorted(O.rglob('*')):
 if f.is_file() and f.name!='SOURCE_MANIFEST.json':
  rel=f.relative_to(O).as_posix();e=records.get(rel,{})
  if e.get('transformation')=='byte-identical':assert sha(f)==e['source_sha256'],rel
  files.append({'path':rel,'bytes':f.stat().st_size,'sha256':sha(f),**e})
write('SOURCE_MANIFEST.json',{'at':datetime.now().astimezone().isoformat(),'excludes_self':True,'files':files,'file_count_excluding_manifest':len(files),'base_snapshot_preserved':'d857934','scope':'zero new inference closeout, not new independent evaluation'})
for name,prefix in [('README.md','benchmarks/'),('benchmarks/README.md','')]:
 p=G/name;s=p.read_text();marker='**2026-09-28 · 完整v5透明收尾已完成：'
 if not s.startswith(marker):
  rel=prefix+'2026-09-28_cf_moa_transparent_closeout/'
  s=marker+f'[完整结果与区间]({rel}full_results.md) · [五张表]({rel}five_tables.md) · [费用/范围/交付索引]({rel}README.md)。零新增推理，六臂/11来源/5格式全保留；默认B保持，C3研究扩展。统计与费用已实际收尾，冻结后确认及独立F复本未执行/延后，未按输赢筛选。**\n\n'+s;p.write_text(s)
print(json.dumps({'output':str(O),'files':len(files)+1,'bytes_without_manifest':sum(e['bytes'] for e in files),'checks':checks},ensure_ascii=False))
