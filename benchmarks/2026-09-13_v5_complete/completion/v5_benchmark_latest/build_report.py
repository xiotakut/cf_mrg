"""Aggregate frozen v5 scores; produce paper-ready plots without rescoring."""
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

ROOT=Path(__file__).resolve().parent;WS=Path('/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md')
M4FIX=ROOT.parent/'results_v5_m4_structured/scores'
METHODS=['M0','M2','M3','M4','M5'];CATS=['R1','R2','R3','R4','R5']
NAMES={'R1':'新增支持','R2':'撤销支持','R3':'重新比较','R4':'推导后果','R5':'保持判断','ALL':'整体（去重）'}
FOUR=WS/'results_v5_m0_m2_m4_m5';THREE=WS/'results_v5_m3'
def csvread(p):return list(csv.DictReader(p.open()))
def table(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
a={r['category']:r for r in csvread(FOUR/'category_scores.csv')};b={r['category']:r for r in csvread(THREE/'category_scores.csv')}
fixed={r['category']:r for r in csvread(M4FIX/'category_scores.csv')}
rows=[]
for cat in CATS+['ALL']:
 r={**a[cat],**b[cat],**fixed[cat]};assert len({r[m+'_units'] for m in METHODS})==1
 values={m:float(r[m+'_pct']) for m in METHODS}
 rows.append(dict(category=cat,name=NAMES[cat],units=int(r['M0_units']),**values,method_mean=mean(values.values()),mean_without_M4=mean(v for m,v in values.items() if m!='M4')))
bycat={r['category']:r for r in rows};order=sorted(CATS,key=lambda c:bycat[c]['method_mean'])
table('category_scores_merged.csv',rows)
table('priority.csv',[dict(rank=i+1,**bycat[c]) for i,c in enumerate(order)])
# Same non-reference task -> unit -> method weighting as the original metric.
groups=defaultdict(lambda:[0,0,0,0,0])
unique=defaultdict(dict);mapped=Counter()
for path in [FOUR/'scored.jsonl',THREE/'scored.jsonl',M4FIX/'scored.jsonl']:
 for line in path.open():
  r=json.loads(line)
  if path.parent==FOUR and r['method']=='M4':continue
  m=r['method'];iid=r['item_id'];v=(bool(r['format_invalid']),bool(r['invalid']))
  assert m in METHODS
  if iid in unique[m]:assert unique[m][iid]==v
  unique[m][iid]=v;mapped[m]+=1
  if r['role']=='reference':continue
  for c in r['evaluation_labels']:
   v=groups[r['method'],c,r['unit_id']];v[0]+=1;v[1]+=bool(r['correct']);v[2]+=bool(r['format_invalid']);v[3]+=bool(r['unmapped_diagnosis']);v[4]+=not r['correct'] and not r['invalid']
assert all(len(unique[m])==13905 and mapped[m]==15616 for m in METHODS)
assert all(set(unique[m])==set(unique['M0']) for m in METHODS)
validity=[dict(method=m,unique_inputs=len(unique[m]),mapped_records=mapped[m],format_valid=sum(not a for a,b in unique[m].values()),native_valid=sum(not b for a,b in unique[m].values())) for m in METHODS]
for r in validity:
 r['format_valid_pct']=100*r['format_valid']/r['unique_inputs'];r['native_valid_pct']=100*r['native_valid']/r['unique_inputs']
table('validity.csv',validity)
loss=[];per_method=[]
for c in CATS:
 for m in METHODS:
  values=[v for (method,cat,u),v in groups.items() if method==m and cat==c]
  assert len(values)==bycat[c]['units']
  rates=[100*mean(v[i]/v[0] for v in values) for i in range(1,5)]
  assert abs(rates[0]-bycat[c][m])<1e-9 and abs(sum(rates)-100)<1e-9
  per_method.append(dict(category=c,method=m,correct=rates[0],format_invalid=rates[1],unmapped_diagnosis=rates[2],valid_but_wrong=rates[3]))
 loss.append(dict(category=c,**{k:mean(r[k] for r in per_method if r['category']==c) for k in ['correct','format_invalid','unmapped_diagnosis','valid_but_wrong']}))
table('loss_decomposition.csv',loss);table('loss_by_method.csv',per_method)
sources=defaultdict(Counter)
for r in csvread(FOUR/'unit_scores.csv'):
 if r['method']=='M0' and r['category'] in CATS:sources[r['category']][r['resource_id']]+=1
table('category_source_counts.csv',[dict(category=c,resource_id=rid,units=n,share_pct=100*n/bycat[c]['units']) for c in CATS for rid,n in sources[c].most_common()])
font=FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'font.size':11,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
# Preserve the original four-method grouped-bar colors; add purple for M3.
colors={'M0':'#1f77b4','M2':'#ff7f0e','M3':'#9467bd','M4':'#2ca02c','M5':'#d62728'}
fig,ax=plt.subplots(figsize=(15,6.5))
x=np.arange(len(rows));width=.15
for j,m in enumerate(METHODS):
 values=[r[m] for r in rows]
 bars=ax.bar(x+(j-2)*width,values,width,label='M4（修复）' if m=='M4' else m,color=colors[m],zorder=3)
 assert np.allclose([b.get_height() for b in bars],values)
 ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=8)
ax.set(xticks=x,xticklabels=[f"{r['category']} {r['name']}\nn={r['units']:,}" for r in rows],
       ylim=(0,100),ylabel='单元平均原生准确率（%）')
ax.grid(axis='y',alpha=.16,zorder=0)
ax.legend(ncol=5,frameon=False,loc='upper left')
ax.set_title('v5 benchmark：M0 / M2 / M3 / 新 M4 / M5',pad=16,fontweight='bold',fontsize=17)
fig.text(.06,.025,'各方法覆盖相同13,905个输入；M4使用修复后全量结果。R1–R5可重叠，ALL按6,104唯一单元计算；R4仅13单元。',fontsize=10,color='#475569')
fig.tight_layout(rect=[0,.065,1,1])
for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'v5_grouped_methods.{ext}',dpi=180,facecolor='white')
plt.close(fig)
fig,(ax,bars)=plt.subplots(1,2,figsize=(15.5,6.5),gridspec_kw={'width_ratios':[1.55,1]})
mat=np.array([[r[m] for m in METHODS]+[r['method_mean']] for r in rows])
im=ax.imshow(mat,cmap='YlGnBu',vmin=0,vmax=100,aspect='auto')
ax.set_xticks(range(6),['M0','M2','M3','M4（修复）','M5','五方法均值']);ax.set_yticks(range(6),[f"{r['category']} {r['name']}\nn={r['units']:,}" for r in rows]);ax.tick_params(length=0)
for y in range(6):
 for x in range(6):ax.text(x,y,f'{mat[y,x]:.2f}',ha='center',va='center',color='white' if mat[y,x]>55 else '#152232',fontsize=11,fontweight='bold' if x==5 else 'normal')
ax.axvline(4.5,color='white',lw=2);ax.axhline(4.5,color='white',lw=3)
ax.set_title('A  单元平均原生准确率（%）',loc='left',pad=13,fontweight='bold')
y=np.arange(5);averages=[bycat[c]['method_mean'] for c in order]
bars.barh(y,averages,color=['#b33e53','#cd7954','#407f9f','#71949a','#8da792'],height=.55,label='五方法等权均值')
bars.scatter([bycat[c]['mean_without_M4'] for c in order],y,marker='D',facecolors='white',edgecolors='#20374c',s=45,zorder=3,label='排除 M4 的敏感性检查')
for i,(c,value) in enumerate(zip(order,averages)):bars.text(value/2,i,f'{value:.2f}%',va='center',ha='center',fontsize=11,color='white')
bars.set_yticks(y,[f'{c} {NAMES[c]}' for c in order]);bars.invert_yaxis();bars.set_xlim(0,85);bars.set_xlabel('平均正确率（越低，当前表现越差）');bars.grid(axis='x',alpha=.18);bars.set_axisbelow(True);bars.legend(loc='upper right',fontsize=9,frameon=False)
bars.set_title('B  按分类平均表现由低到高排列',loc='left',pad=13,fontweight='bold')
fig.suptitle('v5 五方法最新全量结果（M4 已修复）',fontsize=18,fontweight='bold',y=.98)
fig.text(.02,.025,'单元内非参考任务平均 → 类别内单元等权；再对五方法等权。类别重叠，ALL 单独去重。\nM4 使用修复后13,905条全量结果；其他方法沿用既有完整结果。R4 仅13个单元；排名为描述性结果，无显著性声明。',fontsize=10,color='#48515b')
fig.subplots_adjust(left=.12,right=.98,top=.85,bottom=.20,wspace=.44)
for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'v5_category_comparison.{ext}',dpi=180,facecolor='white')
plt.close(fig)
fig,ax=plt.subplots(figsize=(12.5,5.5));left=np.zeros(5);lossmap={r['category']:r for r in loss}
for k,label,color in [('correct','原生正确','#41948b'),('valid_but_wrong','格式有效但回答错误','#e59e45'),('unmapped_diagnosis','诊断未匹配固定标签','#7a75ad'),('format_invalid','评分器格式/终态无效','#c95d70')]:
 vals=np.array([lossmap[c][k] for c in order]);ax.barh(y,vals,left=left,color=color,label=label,height=.62)
 for j,v in enumerate(vals):
  if v>=4:ax.text(left[j]+v/2,j,f'{v:.1f}',ha='center',va='center',color='white' if k in ['unmapped_diagnosis','format_invalid'] else '#162e32',fontsize=11)
 left+=vals
ax.set_yticks(y,[f'{c} {NAMES[c]} (n={bycat[c]["units"]:,})' for c in order]);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('五方法等权平均，占类别得分的百分点（每行合计100）');ax.legend(loc='upper center',bbox_to_anchor=(.46,-.18),ncol=2,frameon=False,fontsize=10)
ax.set_title('低分从哪里来：同一评分权重下的正确与错误构成',fontsize=16,pad=16,fontweight='bold')
fig.text(.025,.025,'诊断未映射可能包含错诊或名称差异，不能直接视为答对；“格式/终态无效”也包含被序列化为空答案的流程失败。',fontsize=9,color='#48515b')
fig.subplots_adjust(left=.25,right=.98,top=.84,bottom=.29)
for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'v5_category_error_decomposition.{ext}',dpi=180,facecolor='white')
plt.close(fig)
(ROOT/'validation.json').write_text(json.dumps(dict(status='passed',methods=METHODS,categories=CATS,rank_low_to_high=order,source_files=[str(FOUR/'category_scores.csv'),str(THREE/'category_scores.csv'),str(M4FIX/'category_scores.csv')],m4_variant='structured_fix_20260913',same_input_ids_all_methods=True,unique_inputs_per_method=13905,mapped_records_per_method=15616,metric='equal non-reference native tasks within unit, equal units within category, equal methods',all_25_method_category_scores_match_decomposition=True,each_loss_row_sums_to_100=True,inference_requests=0),indent=2)+'\n')
print(json.dumps({'order':order,'means':{c:bycat[c]['method_mean'] for c in order},'artifacts':str(ROOT)},ensure_ascii=False))
