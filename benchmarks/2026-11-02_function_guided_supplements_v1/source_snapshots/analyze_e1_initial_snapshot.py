"""Offline, family-isolated functional analysis of the frozen seven configurations."""
import json, csv, gzip, time, sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.metrics import log_loss,roc_auc_score
from common import ROOT,WORK,FULL,rows,dump,write,sha,now

OUT=ROOT/'e1';OUT.mkdir(exist_ok=True)
BASE=WORK/'Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md'
LATER=WORK/'Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md'
SOURCES=[(BASE/'results_v5_m0_m2_m4_m5/scored.jsonl',None),(BASE/'results_v5_m3/scored.jsonl',None),(LATER/'results_v5_m4_structured/scores/scored.jsonl','M4'),(LATER/'results_v5_m6_m7/m6_medgenie_v5_full/scores/scored.jsonl','M6'),(LATER/'results_v5_m6_m7/m7_typed_v5_full/scores/scored.jsonl','M7')]
METHODS=['M0','M2','M3','M4','M5','M6','M7'];CATS=['R1','R2','R3','R4','R5']
started=time.monotonic()
evaluations=list(rows(FULL/'offline/evaluations.jsonl'));meta={e['record_id']:e for e in evaluations}
items={r['request_id']:r for r in rows(FULL/'offline/items.jsonl')}
byitem={r['item_id']:r for r in items.values()}
parent={e['group_id']:e['group_id'] for e in evaluations}
def find(x):
    if parent[x]!=x:parent[x]=find(parent[x])
    return parent[x]
def union(a,b):
    a,b=find(a),find(b)
    if a!=b:parent[max(a,b)]=min(a,b)
seen={}
for e in evaluations:
    item=byitem[e['item_id']]
    key=json.dumps({k:item[k] for k in ['question','options','fixed_evidence','answer_format']},sort_keys=True,ensure_ascii=False)
    if key in seen:union(e['group_id'],seen[key])
    else:seen[key]=e['group_id']
families={e['record_id']:find(e['group_id']) for e in evaluations}
sources={str(p):sha(p) for p,_ in SOURCES}
sources.update({str(FULL/'offline'/p):sha(FULL/'offline'/p) for p in ['evaluations.jsonl','items.jsonl']})
data=[];references={};versions=Counter();all_mappings=defaultdict(set)
for path,override in SOURCES:
    for r in rows(path):
        m=override or r['method']
        if path==SOURCES[0][0] and m=='M4':continue
        assert r['record_id'] in meta
        e=meta[r['record_id']]
        for k in ['unit_id','item_id','role','evaluation_labels']:
            assert r[k]==e[k],(m,k,r['record_id'])
        assert r['record_id'] not in all_mappings[m];all_mappings[m].add(r['record_id'])
        if m=='M0' and e['role']=='reference':references[e['unit_id'],e['task'],str(e['target'])]=r.get('semantic_gold',r['gold'])
        if e['role']=='reference':continue
        labels=sorted(set(e['evaluation_labels']))
        data.append(dict(method=m,record_id=r['record_id'],unit_id=e['unit_id'],item_id=e['item_id'],request_id=e['request_id'],source=e['resource_id'],task=e['task'],format=byitem[e['item_id']]['answer_format'],family=families[e['record_id']],signature='+'.join(labels),labels=labels,correct=int(r['correct'] is True),invalid=bool(r['invalid']),format_invalid=bool(r['format_invalid']),unmapped_diagnosis=bool(r['unmapped_diagnosis']),semantic_gold=r.get('semantic_gold',r['gold'])))
        versions[m]+=1
assert set(all_mappings)==set(METHODS) and all(len(x)==15616 for x in all_mappings.values())
df=pd.DataFrame(data);assert len(df)==8798*7
df['weight']=1/df.groupby(['method','unit_id'])['record_id'].transform('count')
assert all(df.groupby('method')['unit_id'].nunique()==6104)
unitrecords=[]
for c in ['ALL']+CATS:
    part=df if c=='ALL' else df[df['labels'].map(lambda x:c in x)]
    g=part.groupby(['method','unit_id','source','family'])['correct'].mean().reset_index(name='score');g['category']=c
    unitrecords.extend(g.to_dict('records'))
units=pd.DataFrame(unitrecords);units.to_csv(OUT/'unit_scores.csv.gz',index=False)
category=units.groupby(['category','method']).agg(units=('unit_id','size'),score=('score','mean')).reset_index()
official=pd.read_csv(LATER/'results_v5_m6_m7/m6_medgenie_v5_full/reports/category_comparison.csv').set_index('category')
for r in category.to_dict('records'):
    assert r['units']==int(official.loc[r['category'],'units'])
    assert abs(r['score']*100-official.loc[r['category'],r['method']])<1e-8
category.to_csv(OUT/'category_reproduction.csv',index=False)
strata=df.groupby(['method','source','format','signature','unit_id','family'])['correct'].mean().reset_index(name='score')
table=strata.groupby(['method','source','format','signature']).agg(units=('unit_id','size'),families=('family','nunique'),accuracy=('score','mean')).reset_index()
table['rank']=table.groupby(['source','format','signature'])['accuracy'].rank(ascending=False,method='min')
table.to_csv(OUT/'source_format_function_scores.csv',index=False)
support=table[table.method=='M0'].drop(columns=['method','accuracy','rank']);support['signatures_in_source_format']=support.groupby(['source','format'])['signature'].transform('count');support.to_csv(OUT/'common_support.csv',index=False)

def interval(frame,value,weight,draws=2000):
    g=frame.groupby('family').agg(numerator=(value,'sum'),denominator=(weight,'sum'))
    a=g.to_numpy();rng=np.random.default_rng(20261102);v=[]
    for _ in range(draws//100):
        idx=rng.integers(len(a),size=(100,len(a)));s=a[idx].sum(axis=1);v.extend((s[:,0]/s[:,1]).tolist())
    return [float(x) for x in np.quantile(v,[.025,.975])]

# Matched source and format, but different functional members: observational contrast.
contrasts=[]
for m in METHODS:
    a=strata[(strata.method==m)&(strata.source=='M01')&(strata['format']=='diagnosis')&(strata.signature=='R1')]
    b=strata[(strata.method==m)&(strata.source=='M01')&(strata['format']=='diagnosis')&(strata.signature=='R1+R3')]
    assert len(a)>0 and len(b)>0
    allg=sorted(set(a.family)|set(b.family));ag=a.groupby('family').score.agg(['sum','count']).reindex(allg,fill_value=0).to_numpy();bg=b.groupby('family').score.agg(['sum','count']).reindex(allg,fill_value=0).to_numpy()
    rng=np.random.default_rng(20261102);vals=[]
    for _ in range(20):
        ix=rng.integers(len(allg),size=(100,len(allg)));sa=ag[ix].sum(1);sb=bg[ix].sum(1);valid=(sa[:,1]>0)&(sb[:,1]>0);vals.extend((sb[valid,0]/sb[valid,1]-sa[valid,0]/sa[valid,1]).tolist())
    lo,hi=np.quantile(vals,[.025,.975])
    contrasts.append(dict(method=m,source='M01',format='diagnosis',R1_only_units=len(a),R1_R3_units=len(b),R1_only_accuracy=float(a.score.mean()),R1_R3_accuracy=float(b.score.mean()),difference_R1_R3_minus_R1_only=float(b.score.mean()-a.score.mean()),ci95_low=float(lo),ci95_high=float(hi)))
pd.DataFrame(contrasts).to_csv(OUT/'medeinst_within_source_contrast.csv',index=False)

# Fixed regularization; fit feature vocabularies on training folds only.
feature_sets={name:[] for name in ['base','functional']}
for r in df.to_dict('records'):
    base={k:r[k] for k in ['method','source','format','task']}
    base.update(method_source=r['method']+':'+r['source'],method_format=r['method']+':'+r['format'],source_format=r['source']+':'+r['format'])
    full=dict(base)
    for c in CATS:
        if c in r['labels']:full['function_'+c]=1.;full['method_function_'+r['method']+'_'+c]=1.
    feature_sets['base'].append(base);feature_sets['functional'].append(full)
y=1-df.correct.to_numpy();w=df.weight.to_numpy();splits=list(GroupKFold(n_splits=5).split(df,y,df.family));preds={};folds=[]
for name,features in feature_sets.items():
    pred=np.full(len(df),np.nan)
    for fold,(train,test) in enumerate(splits):
        assert not (set(df.iloc[train].family)&set(df.iloc[test].family))
        vec=DictVectorizer();xtr=vec.fit_transform([features[i] for i in train]);xte=vec.transform([features[i] for i in test])
        model=LogisticRegression(C=1.0,solver='lbfgs',max_iter=1000,random_state=20261102)
        model.fit(xtr,y[train],sample_weight=w[train]/w[train].mean());pred[test]=model.predict_proba(xte)[:,1]
        folds.append(dict(model=name,fold=fold,train_families=int(df.iloc[train].family.nunique()),test_families=int(df.iloc[test].family.nunique()),features=xtr.shape[1],iterations=int(model.n_iter_[0])))
        print(name,'fold',fold,'complete',flush=True)
    assert np.isfinite(pred).all();preds[name]=pred
metrics={name:dict(brier=float(np.average((p-y)**2,weights=w)),log_loss=float(log_loss(y,p,sample_weight=w)),roc_auc=float(roc_auc_score(y,p,sample_weight=w))) for name,p in preds.items()}
df['base_probability']=preds['base'];df['functional_probability']=preds['functional'];df['brier_improvement_weighted']=w*((preds['base']-y)**2-(preds['functional']-y)**2)
ci=interval(df,'brier_improvement_weighted','weight')
for fold,(_,test) in enumerate(splits):df.loc[test,'fold']=fold
df.drop(columns=['semantic_gold']).to_json(OUT/'out_of_fold.jsonl.gz',orient='records',lines=True,compression='gzip',force_ascii=False)
dump(OUT/'family_mapping.json',dict(record_to_family=families,rule='union original group IDs through exact shared native inputs, including reference endpoints; no outcomes used'))
dump(OUT/'folds.json',folds)
dump(OUT/'summary.json',dict(status='complete',time=now(),methods=METHODS,native_mappings_per_method=15616,nonreference_rows_per_method=8798,units_per_method=6104,analysis_families=int(df.family.nunique()),source_hashes=sources,metrics=metrics,brier_improvement=metrics['base']['brier']-metrics['functional']['brier'],brier_improvement_ci95=ci,folds=5,bootstrap_draws=2000,seed=20261102,regularization_C=1,hyperparameter_search=False,new_model_inference=0,new_native_scores=0,independent_confirmation=False,elapsed_seconds=time.monotonic()-started,limits=['Already exposed v5; OOF analysis does not undo historical method selection.','Associational predictive information, not causal functional difficulty.','Rare/completely confounded categories not separately identifiable.','Intervals condition on fitted OOF models; no nested model-selection bootstrap.','Alternative edit/flip representations not yet fitted.']))
print(json.dumps(metrics),flush=True)
