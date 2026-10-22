"""Completed-run comparison, prior-exposure strata and the established bar chart."""
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
    assert all(r['steps']<=8 and r['costs']['llm_requests']==r['steps'] for r in predictions if r['status']!='failed')
    details=dict(N=len(predictions),protocol_invalid=dict(Counter(r.get('answer_error') or r['termination'] for r in predictions if r['status']=='invalid')),steps=dict(Counter(r['steps'] for r in predictions)),budget_checks='all inputs stay within 8 steps; LLM calls equal steps; old stage reuse = 0')
    atomic(ROOT/'reports/protocol_invalid_reasons.json',details)
    result['protocol_details']=details
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
    known=set()
    manifest=json.loads((V5.parent/'m7_validity_audit/control_pilot/selection_manifest.json').read_text())
    for group in manifest.values(): known.update(r['item_id'] for r in group['items'])
    repair=set(known)
    known.update(r['item_id'] for r in read(ROOT.parent/'formal_balanced/checkpoints/m7_paused_20260913_1345/predictions.jsonl'))
    for p in (ROOT.parent/'optimization_vllm/inputs').glob('*.jsonl'):
        known.update(r['item_id'] for r in read(p))
    pilot={r['item_id'] for r in read(ROOT.parent/'m7_repaired_fresh/inputs/all_384.jsonl')}
    known.update(pilot)
    native=read(ROOT/'reports/native_validity_rows.jsonl')
    def rates(rows):
        return dict(N=len(rows),**{k:dict(count=sum(r[k] for r in rows),pct=100*mean(r[k] for r in rows)) for k in ['protocol_valid','format_valid','native_valid']})
    strata=dict(repair_development=rates([r for r in native if r['item_id'] in repair]), prior_384_pilot=rates([r for r in native if r['item_id'] in pilot]), outside_recorded_prior_runs=rates([r for r in native if r['item_id'] not in known]), note='Descriptive exclusion of saved repair/old-terminal/optimization/pilot IDs; not a claim of an independently constructed untouched test set.')
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
    methods=['M0','M2','M3','M4','M5','M7']
    for r in rows:
        for m in methods[:-1]:r[m]=float(r[m])
        r['M7']=100*categories[r['category']]['unit_mean_accuracy']
    with (ROOT/'reports/category_comparison.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['category','name','units',*methods],extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.font_manager import FontProperties
    font=FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
    plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=dict(M0='#1f77b4',M2='#ff7f0e',M3='#9467bd',M4='#2ca02c',M5='#d62728',M7='#8c564b')
    fig,ax=plt.subplots(figsize=(16,6.5));x=np.arange(len(rows));width=.13
    for j,m in enumerate(methods):
        values=[r[m] for r in rows];bars=ax.bar(x+(j-2.5)*width,values,width,label=m,color=colors[m],zorder=3)
        assert np.allclose([b.get_height() for b in bars],values)
        ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=7)
    ax.set(xticks=x,xticklabels=[f"{r['category']} {r['name']}\nn={int(r['units']):,}" for r in rows],ylim=(0,100),ylabel='单元平均原生准确率（%）')
    ax.grid(axis='y',alpha=.16,zorder=0);ax.legend(ncol=6,frameon=False,loc='upper left')
    ax.set_title('v5 benchmark：M0 / M2 / M3 / 新 M4 / M5 / M7 完整第二版',pad=16,fontweight='bold',fontsize=16)
    fig.text(.06,.025,'同13,905输入；M4为结构化修复版，M7为完整第二版。R1–R5可重叠，ALL按6,104唯一单元计算；R4仅13单元。',fontsize=10)
    fig.tight_layout(rect=[0,.065,1,1])
    for ext in ['png','pdf','svg']:fig.savefig(ROOT/'reports'/f'v5_grouped_methods.{ext}',dpi=180,facecolor='white')
    plt.close(fig)
    p=ROOT/'RESULTS.md'
    p.write_text(p.read_text()+'\n![方法分组柱状图](reports/v5_grouped_methods.png)\n\n六方法比较见 reports/category_comparison.csv；开发/试跑以外的有效率见 reports/exposure_strata.json。\n')
    atomic(ROOT/'reports/report_complete.json',dict(unique_inputs=13905,selected_units=6104,selected_judgments=13000,native_mappings=15616,category_counts_verified=True,chart_values_verified=True))
    main_record=V5.parent/'EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md'
    stamp=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')
    summary=f"{stamp}：M7完整第二版全量13,905/13,905完成，协议{result['overall']['protocol_valid']['pct']:.2f}%、格式{result['overall']['format_valid']['pct']:.2f}%、原生{result['overall']['native_valid']['pct']:.2f}%，运行失败{result['failed']}；原生15,616映射、6,104唯一单元、13,000选中判定及全部轨迹审计通过。"
    text=main_record.read_text()
    text=text.replace(text.split('\n')[0], '**'+summary+'详见[第24节](#m7-typed-v5-full)。**',1)
    text+='\n\n### 24.1 全量完成与最终结果\n\n'+summary+f"全部预测来自本次推理，旧预测复用0；运行内阶段复用{result['reused_stage_requests']}。推理总墙钟{timing['inference_wall_seconds']/60:.2f}分钟，分片执行归一化吞吐{timing['inputs_per_gpu_hour']:.2f}题/GPU小时。GPU0共享条件及初始化开销见机器可读timing。\n\n| 类别 | 单元数 | 原生准确率 |\n|---|---:|---:|\n"
    for cat in ['R1','R2','R3','R4','R5','ALL']:
        c=categories[cat];text+=f"| {cat} | {c['units']} | {100*c['unit_mean_accuracy']:.2f}% |\n"
    unseen=strata['outside_recorded_prior_runs']
    text+=f"\n记录中的旧终态、修复开发、优化及384试跑之外，{unseen['N']}题格式有效{unseen['format_valid']['pct']:.2f}%、原生有效{unseen['native_valid']['pct']:.2f}%；仅为已有记录的排除分层。全部无效/失败保留分母。最终结果及六方法图表：[RESULTS.md]({ROOT}/RESULTS.md)，完整成本/轨迹检查：[final_results.json]({ROOT}/reports/final_results.json)，逐条、来源、R1–R5/ALL及配对评分：[scores]({ROOT}/scores)，分层：[exposure_strata.json]({ROOT}/reports/exposure_strata.json)。旧试验、M6暂停状态及其他用户任务保留。\n"
    main_record.write_text(text)
    print(json.dumps(dict(complete=True,categories=categories,exposure=strata),ensure_ascii=False))


if __name__=='__main__':main()
