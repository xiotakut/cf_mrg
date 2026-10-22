"""Completed-run comparison, prior-exposure strata and the established bar chart."""
from pathlib import Path
import csv
import gzip
import json
from datetime import datetime
from collections import Counter, defaultdict
from statistics import mean
from common import ROOT, V5, SELECTION, read, atomic


def main():
    assert (ROOT/'complete.json').exists()
    result=json.loads((ROOT/'reports/final_results.json').read_text())
    predictions=read(ROOT/'reports/predictions.jsonl')
    assert len(predictions)==13905 and all(r['reused_stage_requests']==0 for r in predictions)
    scored=read(ROOT/'scores/scored.jsonl')
    assert len(scored)==15616 and sum(r['role']!='reference' for r in scored)==8798
    with gzip.open(SELECTION/'selected_targets.jsonl.gz','rt') as f:
        assert sum(bool(line.strip()) for line in f)==13000
    buckets=defaultdict(list)
    for r in scored:
        if r['role']!='reference': buckets[r['unit_id']].append(r['correct'])
    assert len(buckets)==6104
    categories={r['category']:r for r in result['categories']}
    assert abs(categories['ALL']['unit_mean_accuracy']-mean(mean(v) for v in buckets.values()))<1e-12
    assert {k:v['units'] for k,v in categories.items()}==dict(ALL=6104,R1=2866,R2=79,R3=733,R4=13,R5=3600)
    pilot={r['item_id'] for r in read(ROOT.parent/'m6_medgenie_fresh/inputs/all.jsonl')}
    source=Path('/home/data3/txy/Documents/Codex/2026-09-12/benchmark-imedrag-medrag-agent-md-tc')
    repair={r['item_id'] for r in read(source/'data/medgenie_format_smoke.jsonl')}
    known=pilot|repair
    native=read(ROOT/'reports/native_validity_rows.jsonl')
    def rates(rows):
        return dict(N=len(rows),**{k:dict(count=sum(r[k] for r in rows),pct=100*mean(r[k] for r in rows)) for k in ['protocol_valid','format_valid','native_valid']})
    strata=dict(prior_formal_format_smoke=rates([r for r in native if r['item_id'] in repair]), prior_384_pilot=rates([r for r in native if r['item_id'] in pilot]), outside_recorded_prior_runs=rates([r for r in native if r['item_id'] not in known]), note='Descriptive exclusion of saved MedGENIE format-smoke/pilot IDs; not an independently constructed untouched test set; M7 full already used all v5 inputs.')
    atomic(ROOT/'reports/exposure_strata.json',strata)
    jobs=[json.loads(p.read_text()) for p in (ROOT/'jobs').glob('*.json')]
    ready=[json.loads(p.read_text()) for p in (ROOT/'logs').glob('gpu*_ready.json')]
    durations=[json.loads(p.read_text())['seconds'] for p in (ROOT/'runs').glob('*/complete.json')]
    timing=dict(inference_wall_seconds=max(j['finished_at'] for j in jobs)-min(r['started'] for r in ready), summed_chunk_gpu_seconds=sum(durations), inputs_per_gpu_hour=13905*3600/sum(durations), initialization_seconds={str(g):json.loads((ROOT/'logs'/f'gpu{g}_ready.json').read_text())['time']-json.loads((ROOT/'logs'/f'gpu{g}_ready.json').read_text())['started'] for g in [0,1,3]}, note='Wall includes initialization; sum of chunk execution times excludes engine/retriever startup and between-chunk queue overhead. GPU0 is shared with other users.')
    result['timing']=timing
    result['exposure_strata']=strata
    atomic(ROOT/'reports/final_results.json',result)
    previous=ROOT.parents[1]/'v5_benchmark_latest'
    with (previous/'category_scores_merged.csv').open() as f: rows=list(csv.DictReader(f))
    methods=['M0','M2','M3','M4','M5','M6','M7']
    m7_scores={c['category']:c for c in json.loads((ROOT.parent/'m7_typed_v5_full/scores/category_scores.json').read_text())}
    for r in rows:
        for m in methods[:5]:r[m]=float(r[m])
        r['M6']=100*categories[r['category']]['unit_mean_accuracy']
        r['M7']=100*m7_scores[r['category']]['unit_mean_accuracy']
    with (ROOT/'reports/category_comparison.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['category','name','units',*methods],extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.font_manager import FontProperties
    font=FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
    plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=dict(M0='#1f77b4',M2='#ff7f0e',M3='#9467bd',M4='#2ca02c',M5='#d62728',M6='#17becf',M7='#8c564b')
    fig,ax=plt.subplots(figsize=(16,6.5));x=np.arange(len(rows));width=.115
    for j,m in enumerate(methods):
        values=[r[m] for r in rows];bars=ax.bar(x+(j-3)*width,values,width,label=m,color=colors[m],zorder=3)
        assert np.allclose([b.get_height() for b in bars],values)
        ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=7)
    ax.set(xticks=x,xticklabels=[f"{r['category']} {r['name']}\nn={int(r['units']):,}" for r in rows],ylim=(0,100),ylabel='单元平均原生准确率（%）')
    ax.grid(axis='y',alpha=.16,zorder=0);ax.legend(ncol=7,frameon=False,loc='upper left')
    ax.set_title('v5 benchmark：M0 / M2 / M3 / 新 M4 / M5 / M6 MedGENIE / M7',pad=16,fontweight='bold',fontsize=16)
    fig.text(.06,.025,'同13,905输入；M4结构化修复；M6 MedGENIE；M7完整第二版。R1–R5可重叠，ALL按6,104唯一单元计算；R4仅13单元。',fontsize=10)
    fig.tight_layout(rect=[0,.065,1,1])
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/'reports'/f'v5_grouped_methods.{ext}',dpi=180,facecolor='white')
    plt.close(fig)
    p=ROOT/'RESULTS.md'
    p.write_text(p.read_text()+f'\n含初始化推理墙钟{timing["inference_wall_seconds"]/60:.2f}分钟；累计分片耗时{timing["summed_chunk_gpu_seconds"]/3600:.2f} GPU小时；{timing["inputs_per_gpu_hour"]:.2f}题/GPU小时。\n'+ '\n![方法分组柱状图](reports/v5_grouped_methods.png)\n\n七方法比较见 reports/category_comparison.csv；开发/试跑以外的有效率见 reports/exposure_strata.json。\n')
    atomic(ROOT/'reports/report_complete.json',dict(unique_inputs=13905,selected_units=6104,selected_judgments=13000,native_mappings=15616,category_counts_verified=True,chart_values_verified=True))
    print(json.dumps(dict(complete=True,categories=categories,exposure=strata),ensure_ascii=False))


if __name__=='__main__':main()
