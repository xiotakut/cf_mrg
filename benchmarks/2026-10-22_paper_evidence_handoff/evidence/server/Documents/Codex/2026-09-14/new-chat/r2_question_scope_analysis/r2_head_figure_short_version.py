"""Export the seven-method development comparison; subgroup denominators stay explicit."""
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from r2_support_pilot import HERE


def run():
    target=HERE/'r2_question_scope_analysis'
    old=json.loads((HERE/'r2_program_all_methods/summary.json').read_text())['results']
    new=json.loads((target/'summary.json').read_text())['results']
    methods=['M0','M2','M3','M4','M5','M6','M7'];rows=[]
    for method in methods:
        for group in ['all','none','remaining']:
            a=next(r for r in old if r['method']==method and r['policy']=='baseline' and r['group']==group)
            b=next(r for r in new if r['method']==method and r['group']==group)
            rows.append(dict(method=method,group=group,n=a['n'],original_correct=a['correct'],head_correct=b['correct']))
    with (target/'figure_data.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
    fig,axes=plt.subplots(1,3,figsize=(10.8,3.7),sharey=True)
    for ax,group,title in zip(axes,['all','none','remaining'],['All R2 (n=79)','None answers (n=66)','Retained answers (n=9)']):
        rs=[r for r in rows if r['group']==group]
        a=[100*r['original_correct']/r['n'] for r in rs];b=[100*r['head_correct']/r['n'] for r in rs]
        for x,y,z in zip(range(7),a,b):ax.plot([x,x],[y,z],color='#9aa4af',lw=1.6,zorder=1)
        ax.scatter(range(7),a,marker='o',s=35,color='#c17d32',label='Original',zorder=2)
        ax.scatter(range(7),b,marker='D',s=31,color='#236b8e',label='+ condition head',zorder=3)
        ax.set_xticks(range(7),methods);ax.set_ylim(-3,103);ax.set_title(title);ax.grid(axis='y',alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    axes[0].set_ylabel('Agreement with benchmark answer (%)');axes[0].legend(frameon=False,loc='upper left')
    fig.suptitle('R2 condition head: seven-method development comparison',fontsize=12,y=.99)
    fig.text(.5,.035,'Same-backbone frozen fact reuse; 55 covered inputs + 24 original-output fallbacks. Exposed development set.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.085,1,.94])
    for suffix in ['pdf','svg','png']:fig.savefig(target/('r2_condition_head.'+suffix),dpi=220)
    plt.close(fig);print('Exported PDF, SVG, PNG and figure_data.csv.')


if __name__=='__main__':run()
