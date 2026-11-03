from pathlib import Path
import pandas as pd,numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT
p=ROOT/'e3'
support=pd.read_csv(p/'support_operation_controls.csv')
candidate=pd.read_csv(p/'candidate_controls_680.csv')
consequence=pd.read_csv(p/'consequence_controls_288.csv')
invariance=pd.read_csv(p/'invariance_matched_controls.csv')
fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
def grouped(ax,frame,arms,label,den):
 x=np.arange(len(arms));width=.35
 for j,m in enumerate(['M4','M5']):
  a=frame[frame.method==m].set_index('arm');ys=[a.loc[c,'correct']/den*100 for c in arms]
  ax.bar(x+(j-.5)*width,ys,width,label=m,color=['#2a69a2','#e39742'][j])
 ax.set_xticks(x,label);ax.set_ylim(0,105);ax.set_ylabel('Native accuracy (%)');ax.legend(frameon=False)
grouped(axs[0,0],support,['strong_B','disable_add','disable_remove'],['Full','No activation','No retraction'],123)
axs[0,0].set_title('Shared support kernel: 123 inputs')
arms=['original','order0','uncalibrated_majority','calibrated_majority']
avail=list(candidate.variant.unique());arms=[a for a in arms if a in avail]
# Preserve actual saved variant identity if the calibrated arm has a versioned name.
if len(arms)<4:
 extras=[a for a in avail if a not in arms]
 print('candidate extra saved arms',extras)
 if len(extras)==1:arms+=extras
means=candidate.groupby('variant').correct.mean()/680*100
axs[0,1].bar(range(len(arms)),[means[a] for a in arms],color='#2a69a2')
axs[0,1].set_xticks(range(len(arms)),['Original','Single catalog','Voting','Calibrated'][:len(arms)],rotation=12)
axs[0,1].set_ylabel('Seven-configuration mean (%)');axs[0,1].set_title('Candidate decision: 680 units / configuration')
c=consequence[consequence.arm.isin(['full','patch'])].copy();c['correct']=c.joint_numeric_correct
grouped(axs[1,0],c,['full','patch'],['Full plan','Local patch'],288);axs[1,0].set_ylabel('Joint numeric correctness (%)');axs[1,0].set_title('Given-model panel: 24 profiles / 288 tasks')
x=np.arange(2);w=.35
a=invariance[(invariance.stage=='all')&(invariance.control=='maj5')].set_index('method')
for j,m in enumerate(['M4','M5']):axs[1,1].bar(x+(j-.5)*w,[a.loc[m,'control_both_pct'],a.loc[m,'head_both_pct']],w,label=m,color=['#2a69a2','#e39742'][j])
axs[1,1].set_xticks(x,['Ordinary Maj5','Task-adapted F']);axs[1,1].set_ylim(0,100);axs[1,1].set_ylabel('Both endpoints correct (%)');axs[1,1].set_title('Invariance panel: same 192 groups');axs[1,1].legend(frameon=False)
for ax in axs.flat:
 for container in ax.containers:ax.bar_label(container,fmt='%.2f',padding=3,fontsize=8)
for ext in ['png','pdf']:fig.savefig(p/f'operation_controls.{ext}',dpi=180)
plt.close(fig)
d=pd.read_csv(p/'role_coverage_by_function_nonreference.csv')
d=d[(d.method=='M4')&(d.role.isin(['A2','A3','A4','A5']))]
den=d.groupby(['category','role']).inputs.sum();num=d[d.tool_applicable].groupby(['category','role']).inputs.sum()
mat=(num.reindex(den.index,fill_value=0)/den*100).unstack('role').reindex(index=['R1','R2','R3','R4','R5'],columns=['A2','A3','A4','A5'])
mat.to_csv(p/'applicability_matrix.csv')
fig,ax=plt.subplots(figsize=(8,4),layout='constrained');im=ax.imshow(mat.values,cmap='Blues',vmin=0,vmax=100,aspect='auto')
ax.set_xticks(range(4),['Shared support\nA1/A2','Catalog\nA3','Given model\nA4','Native decisions\nA5']);ax.set_yticks(range(5),mat.index)
for i in range(5):
 for j in range(4):ax.text(j,i,f'{mat.iloc[i,j]:.1f}%',ha='center',va='center',color='white' if mat.iloc[i,j]>60 else 'black')
ax.set_title('Applicable cached roles within functional members\nBoth backbones share this applicability map; not independent generations')
for ext in ['png','pdf']:fig.savefig(p/f'functional_coverage.{ext}',dpi=180)
plt.close(fig)
p=ROOT/'aggregation'
if (p/'system_main_table_long.csv').exists():
 d=pd.read_csv(p/'system_main_table_long.csv');wide=d.pivot(index=['method','arm'],columns='category',values='accuracy');wide['Avg_R']=wide[['R1','R2','R3','R4','R5']].mean(1);(wide*100).to_csv(p/'system_main_table_pct.csv')
print('figures complete')
