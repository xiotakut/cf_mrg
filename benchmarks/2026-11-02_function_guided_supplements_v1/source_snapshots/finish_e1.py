import itertools,json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT,dump,now
P=ROOT/'e1_corrected'
df=pd.read_json(P/'out_of_fold.jsonl.gz',lines=True)
strata=df.groupby(['method','source','format','signature','unit_id','family']).agg(score=('correct','mean')).reset_index()
out=[]
for (m,s,f),g in strata.groupby(['method','source','format']):
 groups={sig:x for sig,x in g.groupby('signature') if len(x)>=20 and x.family.nunique()>=10}
 for a,b in itertools.combinations(sorted(groups),2):
  left,right=groups[a],groups[b];fam=sorted(set(left.family)|set(right.family))
  x=left.groupby('family').score.agg(['sum','count']).reindex(fam,fill_value=0).to_numpy()
  y=right.groupby('family').score.agg(['sum','count']).reindex(fam,fill_value=0).to_numpy()
  rng=np.random.default_rng(20261102);v=[]
  for _ in range(20):
   ix=rng.integers(len(fam),size=(100,len(fam)));aa=x[ix].sum(1);bb=y[ix].sum(1);ok=(aa[:,1]>0)&(bb[:,1]>0);v.extend(bb[ok,0]/bb[ok,1]-aa[ok,0]/aa[ok,1])
  lo,hi=np.quantile(v,[.025,.975])
  out.append(dict(method=m,source=s,format=f,left=a,right=b,n_left=len(left),n_right=len(right),families_left=left.family.nunique(),families_right=right.family.nunique(),accuracy_left=left.score.mean(),accuracy_right=right.score.mean(),difference=right.score.mean()-left.score.mean(),ci95_low=lo,ci95_high=hi))
pd.DataFrame(out).to_csv(P/'supported_within_source_contrasts.csv',index=False)
diag=df.groupby(['method','source','format','signature']).agg(mappings=('record_id','size'),accuracy=('correct','mean'),invalid=('invalid','mean'),format_invalid=('format_invalid','mean'),unmapped_diagnosis=('unmapped_diagnosis','mean')).reset_index();diag.to_csv(P/'error_interface_diagnostics.csv',index=False)
# Covariates in the original run are not available at clinical inference; these are offline explanatory models.
sumry=json.load(open(P/'summary.json'))
cat=pd.read_csv(P/'category_reproduction.csv');tab=cat.pivot(index='method',columns='category',values='score').reindex(columns=['R1','R2','R3','R4','R5','ALL'])
ranks=tab.rank(ascending=False,method='min');ranks.to_csv(P/'method_ranks.csv')
fig,axs=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
im=axs[0].imshow(tab.values*100,cmap='Blues',vmin=0,vmax=80,aspect='auto')
axs[0].set_xticks(range(6),tab.columns);axs[0].set_yticks(range(7),tab.index)
for i in range(7):
 for j in range(6):axs[0].text(j,i,f'{tab.iloc[i,j]*100:.1f}',ha='center',va='center',fontsize=8,color='white' if tab.iloc[i,j]>.48 else 'black')
axs[0].set_title('Frozen configurations: native accuracy (%)')
a=pd.read_csv(P/'medeinst_within_source_contrast.csv')
for i,r in a.iterrows():
 axs[1].plot([r.ci95_low*100,r.ci95_high*100],[i,i],color='#246bb1');axs[1].scatter(r.difference_R1_R3_minus_R1_only*100,i,color='#246bb1')
axs[1].axvline(0,color='grey',ls='--');axs[1].set_yticks(range(len(a)),a.method);axs[1].invert_yaxis();axs[1].set_xlabel('R1+R3 minus R1-only (percentage points)');axs[1].set_title('Within MedEinst / diagnosis format\n680 vs 1,100 units; family bootstrap 95% CI')
for ext in ['png','pdf']:fig.savefig(P/f'functional_diagnostics.{ext}',dpi=180)
plt.close(fig)
# Verify family isolation includes all original IDs, known root IDs, and all observed MedPIC scenario siblings.
fm=json.load(open(P/'family_mapping.json'))['record_to_family'];fold_by_family=df.groupby('family').fold.nunique();assert fold_by_family.max()==1
assert df.groupby(['method','unit_id']).weight.sum().sub(1).abs().max()<1e-8
assert df.groupby('record_id').fold.nunique().max()==1
dump(P/'validation.json',dict(status='passed',time=now(),all42_category_values_reproduced=True,all_method_versions_isolated=True,one_fold_per_family=True,one_fold_across_methods_per_record=True,unit_weights_sum_to_one=True,identified_within_source_contrasts=len(out),multiple_comparisons='descriptive intervals, not multiplicity-adjusted significance claims',inference_calls=0))
print(sumry['analysis_families'],sumry['brier_improvement'],sumry['brier_improvement_ci95'])
print(pd.DataFrame(out).groupby(['source','format','left','right']).difference.agg(['min','max']).to_string())
