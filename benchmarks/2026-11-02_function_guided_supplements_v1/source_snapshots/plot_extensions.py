"""Publication-ready plots from saved supplementary tables only."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT,dump,now
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
out=ROOT/'e4b/analysis'
q=pd.read_csv(out/'by_operation.csv').set_index(['method','arm','operation'])
fig,axes=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
ops=['support','candidate','current_decision'];x=np.arange(3)
for ax,m in zip(axes,['M4','M5']):
 for j,(arm,label,color) in enumerate([('uniform','Uniform prompt','#d98735'),('conditioned','Capability-conditioned','#286797')]):
  r=[q.loc[m,arm,op] for op in ops];bars=ax.bar(x+(j-.5)*.36,[z.accuracy*100 for z in r],.36,label=label,color=color)
  ax.bar_label(bars,labels=[f'{int(z.correct)}/{int(z.n)}' for z in r],padding=3,fontsize=9)
 ax.set_xticks(x,['Support\nexecution','Candidate\ncomparison','Current\ndecision']);ax.set_ylim(0,100);ax.set_title(m);ax.set_ylabel('Native accuracy (%)')
axes[0].legend(frameon=False,fontsize=9)
fig.suptitle('Same resources and one-call budget; exposed 80-family panel')
for ext in ['png','pdf']:fig.savefig(out/('instruction_comparison.'+ext),dpi=180)
plt.close(fig)
out=ROOT/'e5/analysis'
if (out/'receipt.json').exists():
 import json
 if json.load((out/'receipt.json').open())['status']=='complete':
  primary=pd.read_csv(out/'primary_unit_mean.csv').set_index(['method','arm'])
  pairs=pd.read_csv(out/'pair_summary.csv').set_index(['method','arm'])
  fig,axes=plt.subplots(1,2,figsize=(10,4.6),layout='constrained');x=np.arange(2)
  arms=[('C0','#9c9c9c'),('B','#3f6f9e'),('Gen','#d98735'),('RulePrompt','#31876a')]
  for j,(arm,color) in enumerate(arms):
   vals=[primary.loc[m,arm].accuracy*100 for m in ['M4','M5']]
   b=axes[0].bar(x+(j-1.5)*.18,vals,.18,label=arm,color=color);axes[0].bar_label(b,fmt='%.1f',fontsize=8,padding=2)
   r=[pairs.loc[m,arm] for m in ['M4','M5']]
   b=axes[1].bar(x+(j-1.5)*.18,[z.both_correct/z.pairs*100 for z in r],.18,label=arm,color=color)
   axes[1].bar_label(b,labels=[f'{int(z.both_correct)}/64' for z in r],fontsize=8,padding=2)
  for ax in axes:ax.set_xticks(x,['M4','M5']);ax.set_ylim(0,100);ax.set_ylabel('Accuracy (%)')
  axes[0].set_title('32 unit means, equal weight');axes[0].legend(frameon=False,ncol=2,fontsize=9)
  axes[1].set_title('Both endpoints correct, 64 keep-answer pairs')
  fig.suptitle('Frozen new-family confirmation: R5 scope only')
  for ext in ['png','pdf']:fig.savefig(out/('r5_confirmation.'+ext),dpi=180)
  plt.close(fig)
dump(ROOT/'extension_plot_receipt.json',dict(time=now(),e4b='complete',e5='complete' if (out/'r5_confirmation.pdf').exists() else 'pending',new_model_calls=0,new_scoring=0))
