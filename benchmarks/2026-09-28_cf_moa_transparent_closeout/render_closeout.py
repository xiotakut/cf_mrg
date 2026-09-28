"""Render saved all-data statistics, attribution and scope; no models/graders."""
from pathlib import Path
import json,shutil,re

HERE=Path(__file__).resolve().parent
RUN=HERE.parent
FROZEN=Path('/home/data3/txy/Documents/Codex/2026-09-24/cf_moa_github_rcv_progress/benchmarks/2026-09-26_cf_moa_rcv_full_v5')
ARMS=['original_C0','strong_B','candidate_only','candidate_with_rationales','pool_old_plus_three','joint_selector']
LABELS=dict(zip(ARMS,['C0 原系统','C1/B 采用核心','C2 无理由验证','C3 带理由验证','C4 旧池＋三回答','C5 整体选择']))
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def table(headers,rows):
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])+'\n'
def pct(x):return f'{x*100:.4f}%'
def pp(x):return f'{x:+.4f}'
def ci(x):return '['+', '.join(pp(v) for v in x['percentile_95_pp'])+']'

stats=load(HERE/'statistics/complete_summary.json')
intervals=load(HERE/'statistics/family_effect_intervals.json')
quality={m:load(FROZEN/'data/full_v5'/m.lower()/'quality_summary.json') for m in ['M4','M5']}
index={m:{v['arm']:v for v in x['reports']} for m,x in quality.items()}
for name in ['all_source_results.json','format_input_results.json','family_effect_intervals.json']:
 shutil.copyfile(HERE/'statistics'/name,HERE/name)
dump(HERE/'all_category_results.json',[v for s in stats for v in s['categories']])

def main_score(r):return next(x['mean_native_unit_score'] for x in r['native_categories'] if x['category']=='ALL')
rows=[]
for m in ['M4','M5']:
 for a in ARMS:
  r=index[m][a]
  assert r['planned_inputs']==13905 and r['scored_native_mappings']==15616
  assert r['pending_native_mappings']==0
  rows.append([m,LABELS[a],f"{r['correct_inputs']}/13905",r['unavailable_inputs'],'15616','6104',pct(main_score(r))])
t1='# 表1：六臂完整v5主结果\n\n'+table(['骨干','方法','正确输入','不可用输入','评分映射','ALL非参考单位','原生单元均分'],rows)
t1+='\n每个原生单元内分数保持原样，6104单位等权；reference不进入ALL。不可用保留分母，不按来源重新加权。正确输入数与原生均分不是同一指标。\n\n'
contrasts=[v for v in intervals if v['metric']=='native_ALL' and (v['candidate'],v['baseline']) in [('strong_B','original_C0'),('candidate_with_rationales','strong_B'),('candidate_with_rationales','candidate_only')]]
t1+=table(['骨干','对比','点差pp','95%家族区间pp'],[[v['method'],LABELS[v['candidate']]+' − '+LABELS[v['baseline']],pp(v['delta_pp']),ci(v)] for v in contrasts])
t1+='\nB−C0属于已有采用head和计算的整体作用，不是新增RCV贡献。C3−C2是同池理由增量；相对C2有正点差，不代表相对B有一致收益。区间为已暴露开发数据的描述，未校正事后选择及多重比较。\n'
t1+='\n相对B的完整输入级变化（正负及不可用恢复全部保留）：\n\n'
t1+=table(['骨干','候选','修复','误伤','不可用→正确','正确→不可用'],[[m,LABELS[v['candidate']],v['repairs'],v['harms'],v['unavailable_to_correct'],v['correct_to_unavailable']] for m in ['M4','M5'] for v in quality[m]['comparisons']])
t1+='\n修复−误伤需再加不可用→正确、减正确→不可用，才是净正确输入差；不能把不可用另行删掉。\n\n'
t1+=table(['骨干','方法','辅助映射','辅助valid','辅助exact'],[[m,LABELS[a],index[m][a]['auxiliary']['planned_mappings'],index[m][a]['auxiliary']['valid'],index[m][a]['auxiliary']['exact']] for m in ['M4','M5'] for a in ARMS])
t1+='\n辅助字段按原独立合同保留，主答案正确不自动使辅助字段正确；全部数值直接复用质量JSON，0重评分。\n'

t2='# 表2：全部来源、R类别和输入格式\n\n所有来源按ID排列，所有类别和格式完整保留；来源均值不再宏平均替代ALL。类别重叠不相加，输入格式分层另用输入分母。\n'
source_rows=load(HERE/'all_source_results.json');format_rows=load(HERE/'format_input_results.json')
for m in ['M4','M5']:
 t2+=f'\n## {m}：全部11来源（原生ALL单位）\n\n'
 rows=[]
 for source in sorted({r['source'] for r in source_rows}):
  lookup={r['arm']:r for r in source_rows if r['method']==m and r['source']==source}
  assert set(lookup)==set(ARMS)
  v={a:lookup[a]['mean_native_unit_score'] for a in ARMS}
  rows.append([source,lookup['strong_B']['units']]+[pct(v[a]) for a in ARMS]+[pp(100*(v['strong_B']-v['original_C0'])),pp(100*(v['candidate_with_rationales']-v['strong_B'])),pp(100*(v['candidate_with_rationales']-v['candidate_only']))])
 t2+=table(['来源','单位','C0','B','C2','C3','C4','C5','B−C0 pp','C3−B pp','C3−C2 pp'],rows)
 t2+=f'\n## {m}：全部R类别（可重叠）\n\n'
 categories=next(s for s in stats if s['method']==m)['categories'];rows=[]
 for cat in ['ALL','R1','R2','R3','R4','R5']:
  lookup={r['arm']:r for r in categories if r['category']==cat}
  v={a:lookup[a]['mean_native_unit_score'] for a in ARMS}
  rows.append([cat,lookup['strong_B']['units']]+[pct(v[a]) for a in ARMS]+[pp(100*(v['strong_B']-v['original_C0'])),pp(100*(v['candidate_with_rationales']-v['strong_B'])),pp(100*(v['candidate_with_rationales']-v['candidate_only']))])
 t2+=table(['类别','单位','C0','B','C2','C3','C4','C5','B−C0 pp','C3−B pp','C3−C2 pp'],rows)
 t2+=f'\n## {m}：全部5种answer_format（输入级）\n\n';rows=[]
 for fmt in sorted({r['answer_format'] for r in format_rows}):
  lookup={r['arm']:r for r in format_rows if r['method']==m and r['answer_format']==fmt}
  rows.append([fmt,lookup['strong_B']['inputs']]+[f"{pct(lookup[a]['input_accuracy'])} ({lookup[a]['unavailable']}不可用)" for a in ARMS])
 t2+=table(['格式','输入数','C0','B','C2','C3','C4','C5'],rows)
t2+='\n来源JSON保留单位/家族/native_records/不可用映射；格式JSON保留输入/正确/不可用数及输入准确率。无删题名单或按成绩筛选的来源视图。\n'

t3='# 表3：理由增量与旧共享规则操作消融\n\n'
t3+=table(['骨干','C3−C2原生ALL点差pp','95%家族区间pp'],[[v['method'],pp(v['delta_pp']),ci(v)] for v in intervals if v['metric']=='native_ALL' and v['baseline']=='candidate_only'])
t3+='\n下表复用已有完整123规则输入/123 ALL单位的机制实验，与13905全量表分开；不是旧121/52面板。保留UNKNOWN/None与原assembler，禁add/remove仅为独立组装视图，不重算事实或原评分。\n\n'
ablation=load(FROZEN/'data/tables/table4_operation_ablations.json')
dump(HERE/'operation_ablations_reused.json',ablation)
t3+=table(['骨干','操作臂','正确/123','不可用','原生ALL','修复','误伤'],[[r['method'],r['arm'],f"{r['correct']}/123",r['unavailable'],pct(r['native_ALL_mean']),r['repair'],r['harm']] for r in ablation])
t3+='\nA1/A2是同一已采用执行核的正负操作分解，不是两个独立训练模型。禁add/remove带来的下降支持这两种既有操作的作用，不证明新增多模型协作。\n\nA4在临床v5实际覆盖0，仍保留全部13个R4标签单位。旧完整模型24-profile机制验证属于条件化工具验证；结果与临床准确率不合并，也不视为本轮新患者或独立确认。\n'
a4=load(HERE/'review/operation_ablation_binding.json')['A4_separate_panel']
t3+='\n旧A4模型内条件面板（24个参数/初态profile ×12题／骨干，全部旧结果，本轮0模型/积分）：\n\n'
t3+=table(['骨干','旧实验臂','二值正确/288','数值联合正确/288','全输出正确/288'],[[v['model'],v['arm'],v['binary_correct'],v['joint_numeric_correct'],v['all_outputs_correct']] for v in a4['rows']])
t3+='\n该面板限制在同一公开simglucose模型、四种固定动作及三类问句；旧held-out参数profile不等于本轮未见临床患者、跨模型或开放语言因果验证。\n'

t4='# 表4：保持／应变及完整配对家族区间\n\n'
pairrows=[]
# Stable projection from the saved pair metadata, not source answers/gold.
import gzip
from collections import Counter
for m in ['M4','M5']:
 counts=Counter();correct=Counter()
 with gzip.open(FROZEN/'data/full_v5'/m.lower()/'pairs.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);assert r['complete'];key=(r['arm'],r['relation']);counts[key]+=1;correct[key]+=r['both_correct'] is True
 for a in ARMS:
  pairrows.append([m,LABELS[a],f"{correct[a,'maintain']}/{counts[a,'maintain']}",f"{correct[a,'respond']}/{counts[a,'respond']}"])
t4+=table(['骨干','方法','保持两端均正确','应变两端均正确'],pairrows)
t4+='\n5000次家族有放回抽样，seed=240924；同次抽样的全部arm共享家族抽样序列。按被抽家族内单位的分数和/单位数计算，未改成家族均值等权。ALL、maintain、respond分别计算，分别为6104/6838/1780 atoms。\n\n'
t4+=table(['骨干','metric','对比','atoms','家族','点差pp','95%区间pp'],[[v['method'],v['metric'],LABELS[v['candidate']]+' − '+LABELS[v['baseline']],v['atoms'],v['families'],pp(v['delta_pp']),ci(v)] for v in intervals])
t4+='\n应变某些差值及区间均为0表示当前固定候选输出在此配对范围未改变得分，不证明所有未来模型、任务或反事实能力恒为0。所有区间仅描述已暴露开发样本；不消除事后方法/范围选择，不是独立泛化证据。\n'

# Produced by the separate, bounded read-only SQL attribution task.
cost_report=HERE/'costs/attributed_costs.md'
assert cost_report.exists(),'cost attribution must actually finish before final tables'
cost_text=re.sub(r'\]\(([^)#]+\.json(?:l\.gz)?)\)',r'](costs/\1)',cost_report.read_text())
cost_text=cost_text.replace('`projection/`','`costs/projection/`')
t5='# 表5：各方法成本、共享归属与机制覆盖\n\n'+cost_text.split('\n',1)[1].lstrip()
for name,text in [('table1_full_results.md',t1),('table2_all_strata.md',t2),('table3_rationales_and_operations.md',t3),('table4_pairs_and_intervals.md',t4),('table5_cost_and_coverage.md',t5)]:
 (HERE/name).write_text(text)
intro='''# CF-MoA完整v5透明收尾：五张表

2026-09-28。基于用户指定d857934完整结果；本轮0新增模型、0原生重评分、0删题。全部六臂、两骨干、13905输入/15616评分映射/6104非参考ALL单位保持。默认采用B，C3仅研究扩展；B−C0不作为RCV新增贡献。冻结后确认与独立F复本未执行，延后列为限制。

'''
(HERE/'five_tables.md').write_text(intro+'\n\n---\n\n'.join([t1,t2,t3,t4,t5]))
(HERE/'full_results.md').write_text(intro+t1+'\n\n所有来源、类别、格式、操作消融、保持/应变和费用见[完整五表](five_tables.md)。[范围与限制](scope_and_limitations.md)及[最终状态](final_status.json)明确区分本轮已完成与未执行部分。\n')
(HERE/'attributed_costs.md').write_text(cost_text)
print('Rendered five unfiltered tables and requested root artifacts; no inference/grading.')
