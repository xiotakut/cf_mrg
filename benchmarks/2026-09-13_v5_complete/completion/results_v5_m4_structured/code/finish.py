"""Merge the complete new M4 run and invoke the frozen full native v5 scorer."""
import csv
import fcntl
import json
import subprocess
import sys
import time
from prepare_v5 import OUT, read, write, dump


def main():
    with (OUT / 'finalize.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (OUT / 'complete.json').exists():
            return
        jobs = [json.loads(p.read_text()) for p in sorted((OUT / 'jobs').glob('*.json'))]
        if any(j['state'] != 'done' for j in jobs):
            return
        expected = {i['item_id'] for i in read(OUT / 'items.jsonl')}
        predictions = []
        for job in jobs:
            rows = read(OUT / 'runs' / job['name'] / 'predictions.jsonl')
            assert len(rows) == job['n']
            predictions.extend(rows)
        assert len(predictions) == len(expected) == 13905
        assert {r['item_id'] for r in predictions} == expected
        write(OUT / 'M4/predictions.jsonl', predictions)
        dump(OUT / 'M4/config.json', json.loads((OUT / 'config.json').read_text()))
        subprocess.run([sys.executable, str(OUT / 'code/analyze_v5.py'), '--methods', 'M4',
                        '--output-dir', str(OUT / 'scores')], check=True)
        from status import status
        snapshot = status()
        dump(OUT / 'validity.json', snapshot)
        validation = json.loads((OUT / 'scores/validation.json').read_text())
        assert validation['status'] == 'complete'
        dump(OUT / 'complete.json', dict(time=time.time(), unique_inputs=13905,
             native_records=15616, missing=0, duplicates=0, validity=snapshot['validity']))
        v = snapshot['validity']
        lines = ['# 新 M4 v5 全量结果', '', '13,905个独立输入全部完成；原M4输出独立保留。', '',
                 f"格式有效率 {v['format_valid_pct']:.2f}%；原生评分有效率 {v['native_valid_pct']:.2f}%；严格Schema有效率 {v['schema_valid_pct']:.2f}%。", '',
                 '| 类别 | 单元数 | 单元平均准确率 |', '|---|---:|---:|']
        with (OUT / 'scores/category_scores.csv').open() as f:
            for r in csv.DictReader(f):
                lines.append(f"| {r['category']} | {r['M4_units']} | {float(r['M4_pct']):.2f}% |")
        lines += ['', '修复为明确输出契约＋xgrammar JSON Schema；权重、温度、输出预算及历史检索证据固定。',
                  '约束解码改变允许采样的token，不声称与原输出等价。全部无效结果保留分母。',
                  '100条既有方案选择样本包含在全库内，试跑以外输入的有效率单列于validity.json。',
                  '完整原生评分、来源与R5配对统计见scores/，运行与成本记录见runs/和logs/。', '']
        (OUT / 'RESULTS.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
