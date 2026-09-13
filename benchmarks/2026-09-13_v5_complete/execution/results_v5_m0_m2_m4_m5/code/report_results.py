"""Write the final reviewable result report after full native/stage validation."""
import csv,json
from pathlib import Path
from prepare_v5 import OUT

def main():
    validation=json.loads((OUT/'validation.json').read_text());audit=json.loads((OUT/'artifact_audit.json').read_text())
    assert validation['status']=='complete' and audit['status']=='passed'
    rows=list(csv.DictReader((OUT/'category_scores.csv').open()))
    lines=['# V5 R1–R5：M0 / M2 / M4 / M5 完整结果','',
           '四方法已完成全部13,905个独立输入，共55,620条预测、62,464条原生评分记录，覆盖6,104个比较单元和13,000个选中判断。输入/目标映射、原生评分接口和新M2阶段审计通过。','',
           '| 类别 | 单元 | M0 | M2 | M4 | M5 |','|---|---:|---:|---:|---:|---:|']
    for r in rows:lines.append('| '+r['category']+' | '+r['M0_units']+' | '+' | '.join(f"{float(r[m+'_pct']):.2f}%" for m in ['M0','M2','M4','M5'])+' |')
    lines+=['','主表为每单元的原生任务平均正确率；类别可重叠，ALL去重。R4为作者预期答案一致率。','',
            'M0复用8,877条、补跑5,028条；M2复用6,687条、补跑7,218条。M4/M5各生成13,905条。冒烟均从正式清单取样并直接复用。','',
            '- [分类结果及来源等权/全部任务通过率](category_scores.csv)',
            '- [来源结果](source_scores.csv)与[原生任务明细](source_task_scores.csv)',
            '- [配对方法差异与来源原题聚类bootstrap区间](paired_method_comparisons.csv)',
            '- [R5答案一致性与两端同时正确](r5_pair_summary.csv)',
            '- [完整覆盖验证](validation.json)与[阶段/令牌审计](artifact_audit.json)',
            '- [四方法图](v5_four_methods.png)、[PDF](v5_four_methods.pdf)',
            '- [完整方法、评分和数据协议](README.md)','',
            '## 限制','',
            'M4/M5采用vLLM批量推理，与安装时的Transformers冒烟不保证逐token一致；M5为完整长证据使用YaRN factor4扩展到128K。M4与M5使用相同四库BM25/MedCPT检索、top8、temperature0.7及2048输出预算，仅模型及其必要模板/上下文适配不同。它们与M0/M2的语料及调用预算不同，不能把全部分数差异归因于方法算法。','',
            '开放诊断沿用归一化精确匹配，不补做医学同义表达判分。MedRGB为保留的六档本地污染比例协议；28个单元的77个上下文含原始空槽位，缺失文档不进入检测评分。文档纠正文本未做语义判分。分类目标决定成员与类别，原生任务准确率不等同于逐条分类理由的语义验证。']
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    p=OUT/'README.md';p.write_text(p.read_text().replace('2026-09-11 启动，运行中。','2026-09-11 启动，四方法完整评测及审计已完成。结果见 [RESULTS.md](RESULTS.md)。'))
if __name__=='__main__':main()
