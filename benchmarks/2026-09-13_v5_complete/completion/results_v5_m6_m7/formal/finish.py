"""Score only when every frozen chunk has completed and passed its trace audit."""
import fcntl
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, read
from score import score_run


def main():
    with (ROOT / 'finalize.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (ROOT / 'complete.json').exists():
            return
        plan = json.loads((ROOT / 'plan.json').read_text())
        jobs = [json.loads((ROOT / 'jobs' / (j['name'] + '.json')).read_text()) for j in plan['jobs']]
        if any(j['state'] != 'done' for j in jobs):
            print('Other chunks are still pending, active, or in error; final scoring waits.')
            return
        expected = {r['item_id'] for r in read(ROOT / 'data/inputs.jsonl')}
        evaluations = read(ROOT / 'data/evaluation.jsonl')
        assert len(expected) == 13905 and len(evaluations) == 15616
        summaries = {}
        for method in ('imedrag', 'tcrag'):
            predictions = read(ROOT / 'data' / f'reused_{method}.jsonl')
            for job in jobs:
                if job['method'] != method:
                    continue
                run = ROOT / 'runs' / job['name']
                report = json.loads((run / 'execution_report.json').read_text())
                assert report['complete'] and report['coverage']['N_planned'] == job['n']
                predictions.extend(read(run / 'predictions.jsonl'))
            assert len(predictions) == len(expected) and {r['item_id'] for r in predictions} == expected
            output = ROOT / 'results' / method
            atomic(output / 'predictions.jsonl', predictions, lines=True)
            summaries[method] = score_run(output, ROOT / 'data/inputs.jsonl', evaluations, output / 'scores')
        atomic(ROOT / 'complete.json', dict(completed_at=datetime.now().astimezone().isoformat(),
               unique_inputs_per_method=13905, missing=0, duplicates=0, methods=summaries))
        lines = ['# v5 M6/M7 全量结果', '',
                 '每方法13,905输入全部有终态，15,616条原生评分映射；缺失0，重复0。无效与运行失败保留分母。', '']
        for method, s in summaries.items():
            lines += [f"{method}: 有效{s['N_ok']}，无效{s['N_invalid']}，运行失败{s['N_failed']}。", '']
            for row in s['categories']:
                lines.append(f"- {row['category']}: 单元平均准确率 {100*row['unit_mean_accuracy']:.2f}%（{row['units']}单元）")
            lines.append('')
        lines.append('完整评分、配对结果和来源统计见 results/；逐分片执行与成本审计见 runs/*/execution_report.json。试跑复用来源与递归成本链保留在 plan.json 引用的原目录。')
        (ROOT / 'RESULTS.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
