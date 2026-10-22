"""Full native scoring and the already-tested MedGENIE request audit."""
import json
from collections import Counter
from common import ROOT, V5, read, atomic
from monitor import snapshot
from score import score_run
from audit_medgenie import audit_run

status, rows, native = snapshot()
assert status['completed']==13905 and status['chunks']=={'done':109}
items={r['item_id']:r for r in read(ROOT/'inputs/all.jsonl')}
assert not status['reused_stage_requests']
atomic(ROOT/'reports/predictions.jsonl',rows,lines=True)
atomic(ROOT/'reports/native_validity_rows.jsonl',native,lines=True)
evals=read(V5/'evaluation.jsonl')
assert len(evals)==15616
scoring=score_run(ROOT/'reports',ROOT/'inputs/all.jsonl',evals,ROOT/'scores')
checks,truncations=Counter(),Counter()
for run in sorted((ROOT/'runs').glob('chunk_*')):
    c,t=audit_run(run,items);checks.update(c);truncations.update(t)
    print(json.dumps(dict(audited=run.name,checks=dict(c))),flush=True)
assert checks['input_and_config_identity']==13905
assert status['costs']['retrieval_requests']==0
status.update(complete=True,protocol_invalid_reasons=dict(Counter(r.get('validation_error') or r['termination'] for r in rows if r['status']!='ok')),audit_checks=dict(checks),truncations_by_stage=dict(truncations),native_scoring_mappings=15616,categories=scoring['categories'])
atomic(ROOT/'reports/final_results.json',status)
atomic(ROOT/'complete.json',dict(inputs=13905,fresh=13905,reused=0,failed=status['failed'],native_mappings=15616,audit_passed=True))
lines=['# M6 MedGENIE v2：v5全量结果','','全部13,905输入新生成，旧预测和阶段复用0；完整保留15,616条原生评分映射。Llama-3.1-8B-Instruct、5份背景＋1次greedy reader；本轮沿用试跑版方法和预算。','','| 有效率（分母13,905） | 数量 | 比例 |','|---|---:|---:|']
for k,label in [('protocol_valid','协议有效'),('format_valid','格式有效'),('native_valid','原生有效')]:
    v=status['overall'][k];lines.append(f'| {label} | {v["count"]} | {v["pct"]:.2f}% |')
lines+=['','有效率不是准确率。格式有效率沿用既有v5解析口径；原生有效率还要求诊断等映射成功。协议拒绝结果在native入口置空，原生malformed_json计数不能当作原始输出JSON语法错误数。','','| 类别 | 单元数 | 单元平均原生准确率 |','|---|---:|---:|']
for c in scoring['categories']:lines.append(f'| {c["category"]} | {c["units"]} | {100*c["unit_mean_accuracy"]:.2f}% |')
lines+=['',f'运行失败{status["failed"]}，请求重试{status["costs"]["retry_count"]}；背景截断{truncations["contexts"]}次，reader截断{truncations["reader"]}次。全部无效/失败保留分母。','', 'MedGENIE的模型和v5开放题接口为本地适配，原论文/MedRGAG差异见主记录；不声称复现作者原模型的表格分数。R1–R5可重叠，ALL按6104唯一单元计算，R4仅13单元。','','[详细成本、题型有效率和审计](reports/final_results.json) · [原生逐题评分](scores/scored.jsonl) · [监督历史](reports/supervision.jsonl)','']
(ROOT/'RESULTS.md').write_text('\n'.join(lines))
print(json.dumps(dict(complete=True,overall=status['overall'],audit_checks=dict(checks)),ensure_ascii=False),flush=True)
