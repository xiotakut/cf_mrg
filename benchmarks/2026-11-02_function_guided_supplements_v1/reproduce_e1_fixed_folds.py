"""CPU-only E1 reproduction from saved scores and frozen family folds.

Writes nothing unless --output is supplied; never imports a benchmark model runner.
"""
import argparse, collections, gzip, json, platform, time
from pathlib import Path
import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    started=time.monotonic()
    with gzip.open(ROOT/'e1_corrected/out_of_fold.jsonl.gz','rt') as f:data=[json.loads(l) for l in f]
    folds=json.loads((ROOT/'e1_corrected/frozen_family_folds.json').read_text())['folds']
    expected=json.loads((ROOT/'e1_corrected/summary.json').read_text())
    assert len(data)==61586 and len(folds)==4216
    count=collections.Counter((r['method'],r['unit_id']) for r in data)
    weights=np.array([1/count[r['method'],r['unit_id']] for r in data])
    assigned=np.array([folds[r['family']] for r in data])
    assert all(assigned[i]==r['fold'] for i,r in enumerate(data))
    y=np.array([1-r['correct'] for r in data])
    base=[];functional=[]
    for r in data:
        b={k:r[k] for k in ['method','source','format','task']}
        b.update(method_source=r['method']+':'+r['source'],method_format=r['method']+':'+r['format'],source_format=r['source']+':'+r['format'])
        full=dict(b)
        for c in ['R1','R2','R3','R4','R5']:
            if c in r['labels']:full['function_'+c]=1.;full['method_function_'+r['method']+'_'+c]=1.
        base.append(b);functional.append(full)
    result={}
    for name,features in [('base',base),('functional',functional)]:
        prediction=np.full(len(data),np.nan)
        for fold in range(5):
            train=np.flatnonzero(assigned!=fold);test=np.flatnonzero(assigned==fold)
            assert not {data[i]['family'] for i in train}&{data[i]['family'] for i in test}
            vec=DictVectorizer()
            xtrain=vec.fit_transform([features[i] for i in train]);xtest=vec.transform([features[i] for i in test])
            model=LogisticRegression(C=1.,solver='lbfgs',max_iter=1000,random_state=20261102)
            model.fit(xtrain,y[train],sample_weight=weights[train]/weights[train].mean())
            prediction[test]=model.predict_proba(xtest)[:,1]
        saved=np.array([r[name+'_probability'] for r in data])
        maximum=float(np.max(np.abs(prediction-saved)))
        metrics=dict(brier=float(np.average((prediction-y)**2,weights=weights)),
                     log_loss=float(log_loss(y,prediction,sample_weight=weights)),
                     roc_auc=float(roc_auc_score(y,prediction,sample_weight=weights)))
        assert maximum<2e-6,(name,maximum)
        assert abs(metrics['brier']-expected['metrics'][name]['brier'])<1e-8
        result[name]=dict(max_prediction_abs_error=maximum,metrics=metrics)
    output=dict(status='passed',scope='Ten CPU logistic models refitted using the published fixed folds; no LLM inference.',
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,scikit_learn=sklearn.__version__),
        environment_identity='Current verification environment, not a recovered contemporaneous lock of the November 2 run.',
        rows=len(data),families=len(folds),folds=5,refits=10,results=result,elapsed_seconds=time.monotonic()-started)
    text=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text,end='')

if __name__=='__main__':main()
