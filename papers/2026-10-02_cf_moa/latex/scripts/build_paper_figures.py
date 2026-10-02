#!/usr/bin/env python3
"""Rebuild three publication figures and two evidence tables from frozen summaries.

No model, grader, training, simulation, network or raw-score execution occurs.
Run from any cwd using an existing matplotlib environment.  --check-only validates
input hashes, all derived integers and generated assets without rebuilding them.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil

PACKAGE = Path(__file__).resolve().parents[1]
WORKSPACE = Path('/home/data3/txy')
SOURCE_MAP = {
    'framework.json': WORKSPACE/'Documents/Codex/2026-10-03/paper_story_alignment/five_agent_framework_audit.json',
    'heads.json': WORKSPACE/'Documents/Codex/2026-10-03/paper_scope_audit/head_research_audit.json',
    'benchmark.json': WORKSPACE/'Documents/Codex/2026-10-03/paper_story_alignment/benchmark_contribution_audit.json',
}
METHODS = ('M0','M2','M3','M4','M5','M6','M7')
NAMES = {'M0':'Direct','M2':'MedRGAG','M3':'MA-RAG','M4':'MedRAG',
         'M5':'MedRAG','M6':'MedGENIE','M7':'TC-RAG'}
BACKBONES = {m: ('Qwen' if m in ('M3','M5','M7') else 'Llama') for m in METHODS}
CATEGORIES = ('ALL','R1','R2','R3','R4','R5')
COLOR = {'ink':'#243443','muted':'#61717E','line':'#CBD4DA',
         'original':'#8094A5','head':'#087F83','light':'#EAF5F4',
         'blue':'#EDF3F8','paper':'#F6F8FA','amber':'#B98431','amberlight':'#FCF6E9'}
FIGURE_INFO = {
    'cf_moa_architecture': {
        'label':'fig:architecture','size_inches':[6.8,4.8],
        'caption':'From functional benchmarking to sparse CF-MoA execution. The five relations organize the benchmark and seven-system diagnosis (top). The adopted system selects the first applicable branch using the visible input (bottom). A1 and A2 share a support kernel. A4 requires an explicitly supplied model and state and is evaluated separately from clinical v5, where it has no activations. The terminal output retains the native task contract.',
        'semantics':['Offline R labels do not enter the online router.',
                     'The priority is diagnosis, rule support, supplied model, supported F task, then passthrough.',
                     'Arrows denote alternative routes; they do not denote simultaneous five-agent debate.',
                     'A4 is conditional and had zero activation in the clinical v5 run.'],
    },
    'seven_system_head_gains': {
        'label':'fig:seven-head-gains','size_inches':[6.8,3.45],
        'caption':'Terminal-head transfer across seven system configurations. Each segment links the selected original system to its R1, R2, or R3 head result on the same category. All 21 comparisons improve. L and Q denote the Llama and Qwen backbones. Category memberships overlap: the three panels cover 2,941 unique units, with R3 contained in R1. These are the recorded head-development comparisons, distinct from the complete CF-MoA evaluation.',
        'semantics':['All seven configurations and all three reported head categories are included.',
                     'Common 0–70 percent axes preserve the scale of every before/after difference.',
                     'Original endpoints match the selected formal baselines.',
                     'Rule facts were generated for two backbones and combined offline with the seven original answer sets.'],
    },
    'paired_behavior': {
        'label':'fig:paired-behavior','size_inches':[6.8,3.05],
        'caption':'Correct behavior on paired inputs before and after CF-MoA. Both endpoints must be correct: 6,838 pairs require maintaining the judgment and 1,780 require responding to change. Endpoints are inferred separately, and pair relations are used only for evaluation. Labels show the exact numerator and denominator; the two panels use the same percentage axis.',
        'semantics':['Correctness of both endpoints, rather than answer consistency alone.',
                     'C0 and adopted B are compared; no backbone-specific winner selection.',
                     'Pairs may share source roots or endpoints.'],
    },
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def freeze(input_dir):
    input_dir.mkdir(parents=True, exist_ok=True)
    entries=[]
    for name, source in SOURCE_MAP.items():
        target=input_dir/name
        shutil.copyfile(source,target)
        entries.append({'file':name,'sha256':digest(target),'bytes':target.stat().st_size,
                        'source_path':str(source),'source_sha256':digest(source)})
    dossier=WORKSPACE/'docs/paper/research_dossier.md'
    context={'path':str(dossier),'sha256':digest(dossier),'bytes':dossier.stat().st_size,
             'lines':len(dossier.read_text().splitlines()),
             'reading_coverage':'Source metadata captured at input freeze; reading coverage is recorded separately in the author audit.',
             'use':'Design/context only; quantitative output derives solely from the three frozen JSON inputs.'}
    dump(input_dir/'manifest.json',{'schema_version':2,'files':entries,'context_document':context,
         'use':'Frozen audited summaries; original source score paths and hashes remain within the audits.',
         'historical_note':'The framework audit contains an older 40-case narrative subsequently corrected in the dossier. No 40-case fields are used in these figures or tables.'})


def load(input_dir):
    manifest=json.loads((input_dir/'manifest.json').read_text())
    assert manifest['schema_version']==2, 'Expected portable input manifest version 2'
    context=manifest['context_document']
    assert len(context['sha256'])==64 and context['lines']>0
    assert {r['file'] for r in manifest['files']} == set(SOURCE_MAP)
    for r in manifest['files']:
        p=input_dir/r['file']
        assert p.stat().st_size==r['bytes'] and digest(p)==r['sha256'], f'Changed input: {p}'
    return [json.loads((input_dir/name).read_text()) for name in ('framework.json','heads.json','benchmark.json')],manifest


def derive(framework, heads, benchmark):
    systems=[]
    for r in framework['primary_main_table']['rows']:
        original=r['kind']=='formal_baseline'
        m=r['system'].split()[0] if original else r['system'].split('(')[1].rstrip(')')
        systems.append({'configuration':m if original else 'CF-MoA-B-'+m,
                        'system':NAMES[m] if original else 'CF-MoA (B)',
                        'backbone':BACKBONES[m],
                        **{c:float(r['percent'][c]) for c in CATEGORIES}})
    hs=[]
    for c,n in [('R1',2866),('R2',79),('R3',733)]:
        rows=heads['verified_results'][c]
        assert [r['method'] for r in rows]==list(METHODS)
        for r in rows:
            assert r['n']==n and r['head_correct']>r['baseline_correct']
            base=100*r['baseline_correct']/n; final=100*r['head_correct']/n
            formal=next(x for x in systems if x['configuration']==r['method'])
            assert abs(formal[c]-base)<1e-9
            hs.append({'category':c,'method':r['method'],'n':n,
                       'original_correct':r['baseline_correct'],'head_correct':r['head_correct'],
                       'original_percent':base,'head_percent':final,'delta_pp':final-base})
    pairs=[]
    for r in framework['strong_system_evidence']['paired_counts']:
        for arm in ('C0','B'):
            for mode in ('maintain','respond'):
                n=r[mode+'_n']; correct=r[mode+'_'+arm]
                assert n=={'maintain':6838,'respond':1780}[mode]
                pairs.append({'method':r['method'],'backbone':BACKBONES[r['method']],
                              'arm':arm,'behavior':mode,'correct':correct,'n':n,'percent':100*correct/n})
    support=[]
    ar=framework['operation_evidence']['A1_A2']; assert ar['n']==123
    for r in ar['rows']:
        for policy,key in [('Full support kernel','B_correct'),('Without add','disable_add'),('Without remove','disable_remove')]:
            support.append({'method':r['method'],'backbone':BACKBONES[r['method']],
                            'policy':policy,'correct':r[key],'n':123,
                            'delta_correct':r[key]-r['B_correct'], 'percent':100*r[key]/123})
    sources=benchmark['tables']['v5_sources']
    units=sum(int(r['adopted_units']) for r in sources)
    targets=sum(int(r['adopted_targets']) for r in sources)
    assert len(sources)==11 and units==6104 and targets==13000
    assert len(systems)==9 and len(hs)==21 and len(pairs)==8 and len(support)==6
    return {'systems':systems,'heads':hs,'pairs':pairs,'support':support,
            'architecture_counts':{'source_count':11,'comparison_units':units,'target_judgments':targets,
                                   'baseline_configurations':7,'method_families':6,'backbones':2},
            'head_unique_units':2941,
            'category_denominators':framework['primary_main_table']['denominators']}


def csv_string(rows):
    f=io.StringIO(newline=''); w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
    w.writeheader();w.writerows(rows);return f.getvalue()


def tables(data):
    maxvals={c:max(r[c] for r in data['systems']) for c in CATEGORIES}
    lines=[r'% Generated from frozen audited summaries by build_paper_figures.py.',
           r'\begin{table*}[t]',r'\centering',r'\small',r'\setlength{\tabcolsep}{5.5pt}',
           r'\caption{Complete v5 results for seven baseline configurations and two CF-MoA instantiations. Scores are percentages of native-unit means; bold denotes the highest value in each column.}',
           r'\label{tab:main-system-results}',r'\begin{tabular}{llrrrrrr}',r'\toprule',
           r'System & Backbone & ALL & R1 & R2 & R3 & R4 & R5 \\',
           r'\multicolumn{2}{l}{\emph{Comparison units}} & 6,104 & 2,866 & 79 & 733 & 13 & 3,600 \\',r'\midrule']
    for i,r in enumerate(data['systems']):
        if i==7:lines.append(r'\midrule')
        vals=[(r'\textbf{'+f'{r[c]:.2f}'+'}') if abs(r[c]-maxvals[c])<1e-10 else f'{r[c]:.2f}' for c in CATEGORIES]
        name=r'\textbf{CF-MoA (B)}' if i>=7 else r['system']
        lines.append(' & '.join([name,r['backbone'],*vals])+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}',r'\par\smallskip',
              r'\begin{minipage}{0.97\textwidth}\footnotesize Each configuration covers 13,905 unique inputs. ALL averages non-reference task scores within units and then across units; R labels may overlap. Llama denotes Llama-3.1-8B-Instruct and Qwen denotes Qwen3-8B. The selected MedRAG-Llama baseline includes its output repair.\end{minipage}',r'\end{table*}','']
    support=[r'% Generated from frozen audited summaries by build_paper_figures.py.',
             r'\begin{table}[t]',r'\centering',r'\small',r'\setlength{\tabcolsep}{6pt}',
             r'\caption{Support-operation ablation on all 123 rule inputs, reusing the same extracted facts and execution states. Parentheses give the change in correct outputs relative to the complete kernel.}',
             r'\label{tab:support-ablation}',r'\begin{tabular}{lrr}',r'\toprule',
             r'Policy & Llama & Qwen \\',r'\midrule']
    for pol in ('Full support kernel','Without add','Without remove'):
        rows=[next(r for r in data['support'] if r['method']==m and r['policy']==pol) for m in ('M4','M5')]
        vals=[f"{r['correct']}/123"+(f" ({r['delta_correct']:+d})" if pol!='Full support kernel' else '') for r in rows]
        support.append(' & '.join([pol,*vals])+r' \\')
    support += [r'\bottomrule',r'\end{tabular}',r'\par\smallskip',
                r'\begin{minipage}{\linewidth}\footnotesize A1 and A2 share one rule kernel. Unavailable outputs remain in the denominator.\end{minipage}',r'\end{table}','']
    return {'main_system_results.tex':'\n'.join(lines),'support_operation_ablation.tex':'\n'.join(support),
            'main_system_results.csv':csv_string(data['systems']),
            'support_operation_ablation.csv':csv_string(data['support']),
            'seven_system_head_gains.csv':csv_string(data['heads']),
            'paired_behavior.csv':csv_string(data['pairs'])}


def plotting():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False,
                         'text.color':COLOR['ink'],'axes.labelcolor':COLOR['ink'],
                         'xtick.color':COLOR['muted'],'ytick.color':COLOR['ink'],
                         'axes.edgecolor':COLOR['line'],'axes.linewidth':.6,
                         'savefig.facecolor':'white'})
    return plt


def save(fig,stem):
    from matplotlib.text import Text
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    w,h=fig.canvas.get_width_height();outside=[];fonts=[]
    for t in fig.findobj(match=Text):
        if not t.get_visible() or not t.get_text():continue
        bb=t.get_window_extent(renderer=renderer);fonts.append(t.get_fontsize())
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > w+1 or bb.y1 > h+1:
            outside.append({'text':t.get_text(),'bbox':[bb.x0,bb.y0,bb.x1,bb.y1]})
    assert not outside, f'Text outside figure {stem.name}: {outside}'
    fig.savefig(stem.with_suffix('.pdf'),metadata={'Creator':'build_paper_figures.py','CreationDate':None,'ModDate':None})
    fig.savefig(stem.with_suffix('.png'),dpi=300,metadata={'Software':'build_paper_figures.py'})
    return {'size_inches':list(fig.get_size_inches()),'minimum_text_points':min(fonts),'maximum_text_points':max(fonts),'out_of_canvas_text':outside}


def architecture(out):
    plt=plotting()
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fig=plt.figure(figsize=(6.8,4.8));ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,6.8),ylim=(0,4.8));ax.axis('off')
    def box(x,y,w,h,fc=COLOR['paper'],ec=COLOR['line'],dash=False):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.025,rounding_size=0.07',
                                   facecolor=fc,edgecolor=ec,linewidth=.8,linestyle=(0,(3,2)) if dash else '-'))
    def txt(x,y,text,sz=8,weight='normal',ha='center',color=None,**kw):
        return ax.text(x,y,text,fontsize=sz,fontweight=weight,ha=ha,va='center',color=color or COLOR['ink'],**kw)
    def arrow(x1,y1,x2,y2,color=COLOR['muted'],ls='-',lw=.8):
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=7,
                                    linewidth=lw,color=color,linestyle=ls,shrinkA=0,shrinkB=0))
    txt(.19,4.59,'a  Functional benchmarking',10,'bold',ha='left')
    box(.20,3.39,2.06,1.02,fc=COLOR['light'],ec='#A5CCC8')
    txt(.34,4.23,'Five functional relations',8.7,'bold',ha='left')
    for i,t in enumerate(['R1  Add support','R2  Withdraw support','R3  Recompare candidates','R4  Infer consequences','R5  Maintain judgment']):
        txt(.35,4.05-.137*i,t,7.9,ha='left')
    box(2.60,3.39,1.71,1.02,fc=COLOR['blue'])
    txt(3.455,4.19,'Benchmark v5',9,'bold')
    txt(3.455,3.84,'11 sources\n6,104 comparison units\n13,000 target judgments',8.1,linespacing=1.45)
    box(4.66,3.39,1.93,1.02)
    txt(5.625,4.19,'System diagnosis',9,'bold')
    txt(5.625,3.84,'7 configurations · 6 families\n2 backbones\nR1–R3 head transfer',7.8,linespacing=1.45)
    arrow(2.32,3.91,2.54,3.91);arrow(4.37,3.91,4.60,3.91)
    txt(3.40,3.13,'Functional diagnosis motivates operation specialization',7.8,color=COLOR['muted'])
    ax.plot([.20,6.59],[2.98,2.98],color=COLOR['line'],lw=.55)
    txt(.19,2.79,'b  CF-MoA: select the first applicable operation',9.6,'bold',ha='left')
    box(.20,1.18,1.07,.77,fc=COLOR['paper'])
    txt(.735,1.565,'Current question\nAllowed evidence\nInitial answer',7.7,linespacing=1.45)
    box(1.55,1.18,1.01,.77,fc=COLOR['light'],ec=COLOR['head'])
    txt(2.055,1.64,'Capability\nrouter',9.1,'bold',linespacing=1.2)
    txt(2.055,1.31,'first match',7.1,color=COLOR['muted'])
    arrow(1.33,1.565,1.49,1.565)
    cards=[('A3  Candidate comparison','diagnosis format',2.22,COLOR['blue'],False),
           ('A1 + A2  Support kernel','rules apply: add + remove',1.75,COLOR['light'],False),
           ('A4  Consequence execution','supplied model + state',1.28,COLOR['amberlight'],True),
           ('A5  Stable task readout (F)','supported native task',.81,COLOR['light'],False),
           ('Preserve initial output','otherwise',.34,COLOR['paper'],False)]
    busx=2.78;endy=1.565
    ax.plot([2.56,busx],[endy,endy],color=COLOR['muted'],lw=.75)
    ax.plot([busx,busx],[.53,2.41],color=COLOR['line'],lw=.75)
    ax.plot([5.38,5.38],[.53,2.41],color=COLOR['line'],lw=.75)
    for i,(title,condition,y,fc,dash) in enumerate(cards):
        box(3.03,y,2.10,.38,fc=fc,ec=COLOR['amber'] if dash else COLOR['line'],dash=dash)
        arrow(busx,y+.19,2.98,y+.19,color=COLOR['muted'],ls=(0,(2,2)))
        txt(3.13,y+.253,title,7.65,'bold',ha='left')
        txt(3.13,y+.097,condition,7.1,ha='left',color=COLOR['muted'])
        ax.plot([5.16,5.38],[y+.19,y+.19],color=COLOR['line'],lw=.75)
    box(5.74,1.18,.85,.77,fc=COLOR['blue'])
    txt(6.165,1.565,'Native\noutput',9.1,'bold',linespacing=1.3)
    arrow(5.38,endy,5.68,endy)
    txt(3.40,.13,'Sparse execution: one applicable branch per input',7.6,color=COLOR['muted'])
    quality=save(fig,out/'cf_moa_architecture');plt.close(fig);return quality


def head_plot(data,out):
    plt=plotting()
    from matplotlib.lines import Line2D
    fig,axs=plt.subplots(1,3,figsize=(6.8,3.45),sharey=True)
    fig.subplots_adjust(left=.183,right=.985,bottom=.145,top=.815,wspace=.19)
    titles=['R1 · Add support','R2 · Withdraw support','R3 · Recomparison']
    for ax,c,title in zip(axs,('R1','R2','R3'),titles):
        rows=[r for r in data['heads'] if r['category']==c]
        for i,r in enumerate(rows):
            if i%2==0:ax.axhspan(i-.45,i+.45,color=COLOR['paper'],zorder=0)
            x0,x1=r['original_percent'],r['head_percent']
            ax.plot([x0,x1],[i,i],color=COLOR['head'],lw=1.5,alpha=.75,zorder=2)
            ax.scatter([x0],[i],s=23,facecolor='white',edgecolor=COLOR['original'],linewidth=1.2,zorder=3)
            ax.scatter([x1],[i],s=25,facecolor=COLOR['head'],edgecolor='white',linewidth=.45,zorder=4)
            ax.text(x0,i+.18,f'{x0:.1f}',ha='center',va='top',fontsize=7.1,color=COLOR['muted'])
            ax.text(x1,i-.17,f'{x1:.1f}',ha='center',va='bottom',fontsize=7.1,color=COLOR['head'])
        ax.set_xlim(0,70);ax.set_xticks([0,20,40,60]);ax.set_ylim(6.55,-.65)
        ax.set_title(title,fontsize=8.5,fontweight='bold',pad=17)
        ax.text(.5,1.025,f"n = {rows[0]['n']:,}",transform=ax.transAxes,ha='center',fontsize=7.5,color=COLOR['muted'])
        ax.grid(axis='x',color=COLOR['line'],lw=.45,alpha=.5,zorder=0)
        ax.tick_params(axis='both',length=0,labelsize=7.5,pad=4)
        ax.spines['left'].set_visible(False);ax.spines['bottom'].set_visible(False)
        ax.set_xlabel('Native accuracy (%)',fontsize=7.6,labelpad=5)
    labels=[f"{NAMES[m]} ({'L' if BACKBONES[m]=='Llama' else 'Q'})" for m in METHODS]
    axs[0].set_yticks(range(7),labels,fontsize=8.1)
    handles=[Line2D([],[],marker='o',markerfacecolor='white',markeredgecolor=COLOR['original'],linestyle='None',markersize=4,label='Original system'),
             Line2D([],[],marker='o',markerfacecolor=COLOR['head'],markeredgecolor=COLOR['head'],linestyle='None',markersize=4,label='With terminal head')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.57,.993),ncol=2,frameon=False,fontsize=8,handletextpad=.35,columnspacing=1.8)
    quality=save(fig,out/'seven_system_head_gains');plt.close(fig);return quality


def pair_plot(data,out):
    plt=plotting()
    from matplotlib.patches import Patch
    fig,axs=plt.subplots(1,2,figsize=(6.8,3.05),sharey=True)
    fig.subplots_adjust(left=.092,right=.983,bottom=.175,top=.775,wspace=.28)
    for ax,mode,title in zip(axs,('maintain','respond'),('Maintain judgment','Respond to change')):
        for group,m in enumerate(('M4','M5')):
            yc=group*1.45
            for arm,offset,color in [('C0',-.245,COLOR['original']),('B',.245,COLOR['head'])]:
                r=next(r for r in data['pairs'] if r['method']==m and r['arm']==arm and r['behavior']==mode)
                y=yc+offset
                ax.barh(y,r['percent'],height=.34,color=color,zorder=3)
                ax.text(r['percent']+1.9,y,f"{r['percent']:.2f}%\n{r['correct']:,}/{r['n']:,}",
                        fontsize=7.15,ha='left',va='center',color=COLOR['head'] if arm=='B' else COLOR['muted'],linespacing=1.1)
        n=6838 if mode=='maintain' else 1780
        ax.set_title(title,loc='left',fontsize=9.5,fontweight='bold',pad=19)
        ax.text(0,1.055,f'Both endpoints correct · {n:,} pairs',transform=ax.transAxes,fontsize=7.6,color=COLOR['muted'])
        ax.set_xlim(0,104);ax.set_xticks([0,25,50,75,100]);ax.set_ylim(2.00,-.63)
        ax.set_yticks([0,1.45],['Llama','Qwen'],fontsize=8.3)
        ax.grid(axis='x',color=COLOR['line'],lw=.5,alpha=.6,zorder=0)
        ax.tick_params(axis='both',length=0,labelsize=7.5,pad=4)
        ax.spines['left'].set_visible(False);ax.spines['bottom'].set_visible(False)
        ax.set_xlabel('Pair accuracy (%)',fontsize=8,labelpad=5)
    handles=[Patch(facecolor=COLOR['original'],label='MedRAG (C0)'),Patch(facecolor=COLOR['head'],label='CF-MoA (B)')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,.998),ncol=2,frameon=False,fontsize=8,handlelength=1.25,columnspacing=2)
    quality=save(fig,out/'paired_behavior');plt.close(fig);return quality


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,default=PACKAGE/'inputs/figures')
    ap.add_argument('--output-dir',type=Path,default=PACKAGE/'draft')
    ap.add_argument('--review-dir',type=Path,default=PACKAGE/'review')
    ap.add_argument('--freeze-inputs',action='store_true')
    ap.add_argument('--check-only',action='store_true')
    args=ap.parse_args()
    if args.freeze_inputs:
        if args.check_only:ap.error('--freeze-inputs and --check-only cannot be combined')
        freeze(args.input_dir)
    inputs,manifest=load(args.input_dir);data=derive(*inputs);assets=tables(data)
    figs=args.output_dir/'figures';tabs=args.output_dir/'tables';audit_path=args.review_dir/'figure_audit.json'
    if args.check_only:
        audit=json.loads(audit_path.read_text())
        assert audit['script_sha256']==digest(__file__), 'Script changed since build'
        assert audit['derived_values']==data
        assert audit['input_manifest']==manifest
        for name,text in assets.items():assert (tabs/name).read_text()==text, f'Table changed: {name}'
        for row in audit['outputs']:
            assert digest(args.output_dir/row['file'])==row['sha256'], f"Changed asset: {row['file']}"
        print('PASS: frozen inputs, 54 main-table values, 21 head comparisons, 8 pair counts, 6 ablation counts, generated files and hashes.')
        return
    figs.mkdir(parents=True,exist_ok=True);tabs.mkdir(parents=True,exist_ok=True);args.review_dir.mkdir(parents=True,exist_ok=True)
    for name,text in assets.items():(tabs/name).write_text(text)
    quality={'cf_moa_architecture':architecture(figs),'seven_system_head_gains':head_plot(data,figs),'paired_behavior':pair_plot(data,figs)}
    outputs=[]
    paths=[tabs/n for n in assets]+[figs/(n+ext) for n in FIGURE_INFO for ext in ('.pdf','.png')]
    for p in paths:outputs.append({'file':str(p.relative_to(args.output_dir)),'sha256':digest(p),'bytes':p.stat().st_size})
    context=manifest['context_document']
    dump(audit_path,{'schema_version':1,'script_sha256':digest(__file__),'input_manifest':manifest,
         'context_document':context,'execution':{'new_model_calls':0,'new_grading_calls':0,'new_training':0,'new_simulation':0},
         'derived_values':data,'figures':{k:{**v,'render_checks':quality[k]} for k,v in FIGURE_INFO.items()},
         'tables':{'main_system_results.tex':{'label':'tab:main-system-results','rows':9,'score_cells':54},
                   'support_operation_ablation.tex':{'label':'tab:support-ablation','policies':3,'backbones':2,'n_per_backbone':123}},
         'outputs':outputs,'visual_review':'Pending image inspection; update after review without changing quantitative sources.',
         'reproduction':'Use the existing MedRGAG/.venv/bin/python; matplotlib only. Frozen inputs are portable; --freeze-inputs intentionally refreshes from this workspace. --check-only works from any cwd.'})
    print(json.dumps({'figures':list(FIGURE_INFO),'tables':['main_system_results.tex','support_operation_ablation.tex'],'audit':str(audit_path)},ensure_ascii=False))

if __name__=='__main__':main()
