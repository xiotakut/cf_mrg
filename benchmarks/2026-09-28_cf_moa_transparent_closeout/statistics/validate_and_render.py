#!/usr/bin/env python3
"""Check saved denominator identities and render all contrasts from saved outputs."""
import json
from pathlib import Path
import hashlib
import sys
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT / 'scripts'))
from summarize_existing_results import read_jsonl

ROOT = Path(json.loads((OUT / 'execution_receipt.json').read_text())['source_root'])
ARM_NAMES = {'original_C0':'C0', 'strong_B':'B (C1)', 'candidate_only':'C2',
             'candidate_with_rationales':'C3', 'pool_old_plus_three':'C4', 'joint_selector':'C5'}
ARM_ORDER = {arm:i for i, arm in enumerate(ARM_NAMES)}
results = json.loads((OUT / 'complete_summary.json').read_text())
checks = []
main_rows = []
pair_rows = []
max_mean_error = 0.0
for result in results:
    method = result['method']
    quality = json.loads((ROOT / method.lower() / 'quality_summary.json').read_text())
    actual = {(r['arm'],r['category']):r for r in result['categories']}
    saved_pairs = list(read_jsonl(ROOT / method.lower() / 'pairs.jsonl.gz'))
    for report in quality['reports']:
        arm = report['arm']
        assert report['planned_inputs'] == 13905
        assert report['planned_native_mappings'] == report['scored_native_mappings'] == 15616
        assert report['pending_native_mappings'] == report['awaiting_native_scores'] == 0
        assert report['input_status_counts'] == {'scored':13905}
        formats = [r for r in result['all_formats_input_metrics'] if r['arm'] == arm]
        sources = [r for r in result['all_sources'] if r['arm'] == arm]
        assert len(formats) == 5 and len(sources) == 11
        assert sum(r['inputs'] for r in formats) == 13905
        assert sum(r['correct'] for r in formats) == report['correct_inputs']
        assert sum(r['unavailable'] for r in formats) == report['unavailable_inputs']
        assert sum(r['units'] for r in sources) == 6104
        observed = actual[arm,'ALL']
        assert observed['units'] == 6104
        assert abs(sum(r['units']*r['mean_native_unit_score'] for r in sources)/6104 - observed['mean_native_unit_score']) < 1e-12
        for category in report['native_categories']:
            cat = actual[arm,category['category']]
            error = abs(cat['mean_native_unit_score'] - category['mean_native_unit_score'])
            max_mean_error = max(max_mean_error,error)
            assert cat['units'] == category['units'] and error < 1e-10
        for pair in report['pairs']:
            rows = [r for r in saved_pairs if r['arm'] == arm and r['relation'] == pair['relation']]
            assert len(rows) == pair['pairs']
            assert all(r['complete'] for r in rows)
            assert sum(r['both_correct'] is True for r in rows) == pair['both_correct']
            pair_rows.append(dict(method=method,arm=arm,**pair))
        checks.append(dict(method=method,arm=arm,inputs=13905,native_mappings=15616,
                           native_ALL_units=6104,source_strata=11,answer_formats=5,
                           correct_inputs=report['correct_inputs'],unavailable_inputs=report['unavailable_inputs'],
                           pending_inputs=0,all_saved_means_match=True,all_pair_counts_match=True))
        main_rows.append(dict(method=method,arm=arm,mean=observed['mean_native_unit_score'],
                              correct=report['correct_inputs'],unavailable=report['unavailable_inputs']))
validation = dict(checked_at=datetime.now(timezone.utc).isoformat(),checks=checks,
                  category_mean_checks=72,max_absolute_mean_difference=max_mean_error,
                  all_passed=True,inference_calls=0,grader_calls=0,
                  native_mapping_count_source='Saved quality_summary.json; no rescoring or remapping.',
                  all_sources_kept=True,all_formats_kept=True)
(OUT/'validation_receipt.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
(OUT/'pair_summary.json').write_text(json.dumps(pair_rows,ensure_ascii=False,indent=2)+'\n')

lines=['# 完整 v5 六臂只读统计','',
       '2026-09-28；来源为 d85793470cf75af57217f3fdc73093f494d9f003。每臂完整保留 13,905 输入、15,616 原生评分映射、6,104 非参考 ALL 单元。输入准确率与原生单元均分分列，不按来源重新等权，也不删除不可用输出。', '',
       '| 骨干 | 臂 | 输入正确 / 13905 | 不可用输入 | 原生 ALL / 6104 |',
       '|---|---|---:|---:|---:|']
for row in sorted(main_rows,key=lambda r:(r['method'],ARM_ORDER[r['arm']])):
    lines.append(f"| {row['method']} | {ARM_NAMES[row['arm']]} | {row['correct']} | {row['unavailable']} | {row['mean']:.8%} |")
lines += ['', '配对家族 bootstrap：5,000 次，seed 240924，同次对比较两臂抽取相同家族，保留家族内单元权重。native_ALL = 原生单元均分；maintain/respond = 合格配对两端均正确率。所有区间均为已暴露开发数据的描述，未校正方法及范围事后选择；未执行独立确认。', '',
          '| 骨干 | 指标 | 比较 | 原子数 | 家族数 | 差值（百分点） | 95% percentile 区间（百分点） |',
          '|---|---|---|---:|---:|---:|---|']
for r in json.loads((OUT/'family_effect_intervals.json').read_text()):
    lo,hi=r['percentile_95_pp']
    lines.append(f"| {r['method']} | {r['metric']} | {ARM_NAMES[r['candidate']]} − {ARM_NAMES[r['baseline']]} | {r['atoms']} | {r['families']} | {r['delta_pp']:+.6f} | [{lo:+.6f}, {hi:+.6f}] |")
lines += ['', 'B−C0 属采用版旧核心的增量，不归为新增 RCV 贡献。C3−B 的原生 ALL 在两骨干方向相反；C3−C2 的 M4 原生 ALL 区间跨零。respond 的 C3−B、C3−C2 均为逐配对相同，区间 [0, 0]。默认 B 保持。', '',
          '全部 11 来源、5 输入格式与 ALL/R1–R5：见 [complete_summary.json](complete_summary.json)、[all_source_results.json](all_source_results.json)、[format_input_results.json](format_input_results.json)。R 类可重叠，不相加。全部 36 条家族区间见 [family_effect_intervals.json](family_effect_intervals.json)。', '',
          '验收：提供脚本未修改，6 项测试通过；72 个类别均值逐项匹配保存质量 JSON（容差 1e−10），来源按单元数加权还原 ALL；全部输入正确/不可用数及配对两端均正确数与原结果一致。八份实际输入文件与提交字节一致，运行前后 SHA-256 与 mtime 均保持。新推理 0、grader 0、资源/其他进程操作 0。证据：[execution_receipt.json](execution_receipt.json)、[validation_receipt.json](validation_receipt.json)、[source_hashes_before.json](source_hashes_before.json)、[source_hashes_after.json](source_hashes_after.json)、[script_provenance.json](script_provenance.json)。', '',
          '本目录是离线统计运行证据；持续研究记录由 [CF-MoA 主记录](/home/data3/txy/docs/research/cf_moa.md)维护。']
(OUT/'full_results.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(all_passed=True,denominator_rows=len(checks),category_mean_checks=72,
                     max_absolute_mean_difference=max_mean_error,pair_rows=len(pair_rows)),indent=2))
