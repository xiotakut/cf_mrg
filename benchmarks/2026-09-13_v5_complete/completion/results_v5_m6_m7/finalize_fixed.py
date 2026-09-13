"""Collect the two upstream compatibility fixes after all pilot shards finish."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from common import atomic, read
from score import score_run


def main():
    inputs = ROOT / 'data/pilot_inputs.jsonl'
    ids = {r['item_id'] for r in read(inputs)}
    evaluations = [r for r in read(ROOT / 'data/evaluation.jsonl') if r['item_id'] in ids]
    method_runs = {
        'M6': [ROOT / 'm6_upstream_fix/runs' / f'pilot_m6_fixed_gpu{gpu}' for gpu in (1, 2)],
        'M7': [ROOT / 'tc_upstream_fix/runs/pilot_m7_fixed'],
    }
    summaries = {}
    for method, runs in method_runs.items():
        predictions, executions = [], []
        for run in runs:
            complete = json.loads((run / 'complete.json').read_text())
            assert complete['N_pending'] == 0
            executions.append(json.loads((run / 'execution_report.json').read_text()))
            predictions.extend(read(run / 'predictions.jsonl'))
        assert len(predictions) == 12 and {r['item_id'] for r in predictions} == ids
        output = ROOT / 'diagnostics' / method
        atomic(output / 'predictions.jsonl', predictions, lines=True)
        scoring = score_run(output, inputs, evaluations, output / 'scores')
        summaries[method] = dict(statuses=dict(Counter(r['status'] for r in predictions)),
            input_count=12, native_scored_records=scoring['native_scored_records'],
            source_scores=scoring['sources'],
            new_llm_requests=sum(e['fresh_compute']['llm_requests'] for e in executions),
            reused_llm_requests=sum(e['reused_llm_requests'] for e in executions),
            new_completion_tokens=sum(e['fresh_compute']['completion_tokens'] for e in executions),
            incremental_run_wall_seconds=[e['wall_seconds'] for e in executions],
            audits=[dict(run=e['run_id'], checks=e['checks']) for e in executions])
    atomic(ROOT / 'fixed_pilot_summary.json', dict(
        scope='Same 12 diagnostic inputs per method; source medians plus longest. Not full v5 accuracy.',
        timing='Fix runs reuse old requests; their elapsed time is incremental, not cold inference throughput.',
        methods=summaries))
    lines = ['# v5 M6/M7 小批量结果', '',
             '每方法12条诊断输入（11来源中位长度输入＋全库最长输入）。不是全量R1–R5结果；全量队列尚未启动。', '',
             '| 方法 | 有效 | 无效 | 运行失败 | 修复新增LLM请求 | 复用LLM请求 |',
             '|---|---:|---:|---:|---:|---:|']
    for method, summary in summaries.items():
        c = summary['statuses']
        lines.append(f"| {method} | {c.get('ok', 0)} | {c.get('invalid', 0)} | {c.get('failed', 0)} | {summary['new_llm_requests']} | {summary['reused_llm_requests']} |")
    lines += ['', '“有效”是运行协议有效，不等于答对。原生评分见 `diagnostics/M6/scores/` 和 `diagnostics/M7/scores/`；小样本的分类聚合不用于全库比较，部分病例也未覆盖其全部变体。开放诊断沿用既有canonical精确匹配。', '',
              'M7补回上游无动作关键词输出作为Final Answer提议的处理，仍执行原步数和熵阈值。M6恢复直接使用抽取模型的查询列表，取消逐字匹配门槛，并允许解析失败的轮次跳过后返回有效最终答案。两处修复均保留原始试跑与源码，未添加CF/WM/adapter模块。', '',
              '模型权重、提示、轮数、阈值和检索预算未改变。修复运行复用未受影响请求；其运行时间只代表追加计算，不能当作冷启动吞吐。完整覆盖、请求成本和轨迹审计在 `fixed_pilot_summary.json` 及各run的 `execution_report.json`。']
    (ROOT / 'RESULTS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
