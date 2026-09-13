"""Render the fully covered M0/M2/M5 comparison from the native scorer outputs."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]/'completed_m0_m2_m5'
METHODS = ['M0','M2','M5']
COLORS = ['#64748b','#087f8c','#8b5cf6']


def main():
    validation = json.loads((ROOT/'validation.json').read_text())
    assert validation['status']=='complete' and not any(validation['missing_predictions'].values())
    with (ROOT/'category_scores.csv').open() as f: rows=list(csv.DictReader(f))
    with (ROOT/'paired_method_comparisons.csv').open() as f: contrasts=list(csv.DictReader(f))
    counts=[2866,79,733,13,3600,6104]
    for row,n in zip(rows,counts):
        assert all(int(row[m+'_units'])==n for m in METHODS)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                         'axes.spines.right':False,'savefig.facecolor':'white'})
    x=np.arange(6);width=.24
    fig,ax=plt.subplots(figsize=(12,5.8))
    for j,(method,color) in enumerate(zip(METHODS,COLORS)):
        bars=ax.bar(x+(j-1)*width,[float(r[method+'_pct']) for r in rows],width,
                    label=method,color=color,zorder=3)
        ax.bar_label(bars,fmt='%.1f',padding=4,fontsize=9)
    ax.set(xticks=x,xticklabels=[f"{r['category']}\nn = {n:,}" for r,n in zip(rows,counts)],
           ylim=(0,100),ylabel='Unit-mean native accuracy (%)')
    ax.grid(axis='y',alpha=.16,zorder=0);ax.legend(ncol=3,frameon=False,loc='upper left')
    ax.set_title('V5 completed methods | M0, M2, M5',loc='left',fontweight='bold',pad=18)
    fig.text(.08,.025,'6,104 unique units. R1-R5 overlap; ALL counts each unit once. R4: expected-answer agreement (n=13).',fontsize=9,color='#475569')
    fig.tight_layout(rect=[0,.065,1,1])
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'v5_m0_m2_m5.{ext}',dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,5.8))
    for j,(method,color) in enumerate(zip(METHODS[1:],COLORS[1:])):
        rs=[next(c for c in contrasts if c['category']==r['category'] and c['baseline']=='M0' and c['method']==method) for r in rows]
        values=np.array([float(r['difference_pp']) for r in rs])
        low=np.array([float(r['ci_low_pp']) for r in rs]);high=np.array([float(r['ci_high_pp']) for r in rs])
        ax.errorbar(values,x+(j-.5)*.24,xerr=[values-low,high-values],fmt='o',capsize=4,
                    color=color,label=f'{method} - M0',markersize=6)
    ax.axvline(0,color='#94a3b8',linewidth=1);ax.set(yticks=x,yticklabels=[r['category'] for r in rows],
        xlabel='Difference from M0 (percentage points)',xlim=(-22,52))
    ax.invert_yaxis();ax.grid(axis='x',alpha=.15);ax.legend(frameon=False)
    ax.set_title('Paired differences | 95% cluster-bootstrap intervals',loc='left',fontweight='bold',pad=18)
    fig.text(.08,.025,'2,000 resamples of source-root groups; seed 20260911. Intervals are not adjusted for multiple comparisons.',fontsize=9,color='#475569')
    fig.tight_layout(rect=[0,.065,1,1])
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/f'v5_differences.{ext}',dpi=180)
    plt.close(fig)
    lines=['# V5 已完成方法：M0 / M2 / M5','',
        '三个方法均覆盖全部 13,905 个独立输入，合计 41,715 条预测、46,848 条评分记录，无缺失或重复。M4 仍在运行，本报告不纳入其未完成结果。','',
        '主表为单元等权的原生任务平均正确率：单元内先平均非参考任务，再对单元取均值；无效回答计错。类别可重叠，ALL 对 6,104 个单元去重。','',
        '| 类别 | 单元数 | M0 | M2 | M5 | M2−M0 | M5−M0 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r,n in zip(rows,counts):
        vals=[float(r[m+'_pct']) for m in METHODS]
        lines.append(f"| {r['category']} | {n:,} | {vals[0]:.2f}% | {vals[1]:.2f}% | {vals[2]:.2f}% | {vals[1]-vals[0]:+.2f} pp | {vals[2]-vals[0]:+.2f} pp |")
    lines+=['','![分类对比](v5_m0_m2_m5.png)','','![配对差值](v5_differences.png)','',
        'M2 的 ALL 点估计最高（48.81%），比 M0 高 0.71 个百分点；M5 为 47.35%。M5 在 R2 提升突出，但 R2 只有 79 个单元；M2/M5 在 R3 均高于 M0。R4 仅 13 个单元，分数为作者预期答案一致率，不宜据此作稳定排名。','',
        'ALL 配对差值的 95% 区间：','',
        '| 比较 | 差值（百分点） | 95% 区间 |','|---|---:|---:|']
    for c in contrasts:
        if c['category']=='ALL':lines.append(f"| {c['method']} − {c['baseline']} | {float(c['difference_pp']):+.2f} | [{float(c['ci_low_pp']):+.2f}, {float(c['ci_high_pp']):+.2f}] |")
    lines+=['','区间沿用既定来源原题分组 bootstrap（2,000 次，seed 20260911），未作多重比较校正。','',
        '来源等权 ALL：M0 54.58%，M2 56.05%，M5 55.83%。该口径与主表的单元等权不同，详见 CSV。','',
        'M0 为直接 Llama，M2 为全 Llama MedRGAG，M5 为 MedRAG-Qwen。三者的模型、检索语料及调用预算并不全部相同，分数差不能单独归因于算法。开放诊断沿用归一化精确匹配，未增加医学同义表达判分。','',
        '- [分类数据 CSV](category_scores.csv) / [来源数据 CSV](source_scores.csv)',
        '- [原生任务明细](source_task_scores.csv) / [R5 配对结果](r5_pair_summary.csv)',
        '- [配对差值及区间](paired_method_comparisons.csv) / [完整覆盖验证](validation.json)',
        '- [主图 PDF](v5_m0_m2_m5.pdf) / [主图 SVG](v5_m0_m2_m5.svg)',
        '- [差值图 PDF](v5_differences.pdf) / [差值图 SVG](v5_differences.svg)','']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines))
    print(ROOT/'RESULTS.md')


if __name__=='__main__':main()
