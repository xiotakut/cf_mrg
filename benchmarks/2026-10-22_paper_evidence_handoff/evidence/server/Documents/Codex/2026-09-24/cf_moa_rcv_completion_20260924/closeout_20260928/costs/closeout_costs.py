"""Offline closeout wrapper; all writes confined to this new costs directory."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
ARMS = ['original_C0', 'strong_B', 'candidate_only', 'candidate_with_rationales', 'pool_old_plus_three', 'joint_selector']
FIELDS = ['model_requests', 'input_tokens', 'output_tokens', 'model_seconds']
N = 13905


def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def rows(p):
    with Path(p).open() as f:
        for line, text in enumerate(f, 1):
            if text.strip():
                yield line, json.loads(text)


def source_bindings():
    spec = json.loads((OUT/'sources.json').read_text())
    evidence, routes = [], {}
    for method, cfg in spec['methods'].items():
        for p in cfg['bases']:
            for line, row in rows(p):
                routes[method, row['request_id']] = dict(row['result'].get('operations', {}))
        expected = {s['path']: s for s in cfg['expected_output_sources']}
        for p in cfg['outputs']:
            path = Path(p)
            h = hashlib.sha256()
            count = 0
            with path.open('rb') as f:
                for line, raw in enumerate(f, 1):
                    h.update(raw)
                    if not raw.strip():
                        continue
                    row = json.loads(raw)
                    count += 1
                    if row['arm'] == 'strong_B':
                        ops = row.get('result', {}).get('operations')
                        if ops:
                            routes[method, row['request_id']] = dict(ops)
            old = expected[p]
            check = dict(path=p, sha256=h.hexdigest(), bytes=path.stat().st_size,
                         rows=count, expected_sha256=old['sha256'],
                         matches_completed_receipt=h.hexdigest() == old['sha256'] and path.stat().st_size == old['size'])
            assert check['matches_completed_receipt'], check
            evidence.append(check)
    write('source_binding_verification.json', dict(snapshot='d857934', sources=evidence, all_match=True))
    with (OUT/'per_input_routes.jsonl').open('w') as f:
        for (method, rid), op in sorted(routes.items()):
            f.write(json.dumps(dict(method=method, request_id=rid, **op))+'\n')
    print('source bindings verified', len(evidence), 'route rows', len(routes), flush=True)


def aggregate(values, field):
    known = [v[field] for v in values if v[field] is not None]
    return dict(known_subtotal=sum(known), known_rows=len(known), unknown_rows=len(values)-len(known),
                total=sum(known) if len(known) == len(values) else None)


def finalize():
    spec = json.loads((OUT/'sources.json').read_text())
    projection = OUT/'projection/per_input_mechanism_cost.jsonl'
    route = {(x['method'], x['request_id']): x for _, x in rows(OUT/'per_input_routes.jsonl')}
    buckets = collections.defaultdict(list)
    unknown_c4 = []
    for _, x in rows(projection):
        assert x['execution_status'] == 'terminal'
        if x['method'] == 'M5' and x['arm'] == 'pool_old_plus_three' and x['extra_cost']['model_requests'] is None:
            unknown_c4.append(x)
        buckets[x['method'], x['arm']].append(x)
    assert len(unknown_c4) == 8
    fixes = []
    for x in unknown_c4:
        sql = Path(x['source']['path']).with_name('journal.sqlite3')
        con = sqlite3.connect(sql.as_uri()+'?mode=ro', uri=True)
        con.execute('PRAGMA query_only=ON')
        task = x['request_id']+':'+x['arm']
        count = con.execute('SELECT COUNT(*) FROM calls WHERE request_id=?', (task,)).fetchone()[0]
        raw_text = con.execute('SELECT record FROM outputs WHERE request_id=?', (task,)).fetchone()[0]
        raw = json.loads(raw_text)
        con.close()
        assert count == 0 and raw['status'] == 'failed'
        assert raw['error'] == 'Complete native context exceeds selected capacity; no truncation'
        assert not raw.get('model_callbacks') and raw['cost']['physical_model_requests'] == 0
        assert all(raw['cost'][k] == 0 for k in ['new_model_requests', 'replayed_model_requests', 'live_input_tokens', 'live_output_tokens'])
        before = {k:x[k] for k in ['extra_cost','method_attributed_cost','inherited_other_cost','extra_cost_origin']}
        x['extra_cost'] = dict.fromkeys(FIELDS, 0)
        x['method_attributed_cost'] = dict(x['base_cost_once'])
        x['inherited_other_cost'] = dict(x['base_cost_once'])
        x['extra_cost_origin'] = 'closed_SQL_no_callback_pre_submission_capacity_failure'
        fixes.append(dict(method=x['method'], arm=x['arm'], request_id=x['request_id'], source=x['source'],
                          journal=str(sql), SQL_task_id=task, SQL_callback_rows=count, original_error=raw['error'],
                          original_status=raw['status'], SQL_output_record_sha256=hashlib.sha256(raw_text.encode()).hexdigest(),
                          before=before, after={k:x[k] for k in before},
                          score_or_denominator_changed=False))
    write('cost_correction_receipt.json', dict(corrections=fixes, model_calls=0, grader_calls=0,
          original_projection_preserved=True, reason='Eight closed task records prove pre-submission failure and zero additional callbacks; inherited B remains paid.'))
    output, coverage = [], []
    categories = ['base_cost_once','extra_cost','method_attributed_cost','new_execution_cost','exact_replay_attributed_cost','inherited_other_cost']
    keep = ['method','arm','request_id','answer_format','execution_status','actual_output_status','native_unavailable',
            'audit_status','activation_attempted','pool_stratum','K','actual_F_votes','invalid_F_votes','stopped_early',
            'pool_unknown_reason','extra_cost_origin']+categories
    with gzip.open(OUT/'per_input_cost_coverage.jsonl.gz', 'wt', encoding='utf-8') as f:
        for method in ['M4','M5']:
            base = buckets[method,'strong_B']
            assert len(base) == N and len({x['request_id'] for x in base}) == N
            for x in base:
                z = dict(method=method, arm='original_C0', request_id=x['request_id'], answer_format=x['answer_format'],
                         planned=True, original_C0_upstream_cost=dict.fromkeys(FIELDS),
                         cost_status='historical_common_upstream_unavailable; not zero')
                f.write(json.dumps(z,separators=(',',':'))+'\n')
            output.append(dict(method=method,arm='original_C0',inputs=N,terminal=N,
                               cost_status='unknown_common_upstream',cost={k:{field:dict(total=None, known_subtotal=0,
                               known_rows=0,unknown_rows=N) for field in FIELDS} for k in ['method_attributed_cost']},
                               end_to_end_total=None, common_original_C0_upstream_cost='unknown'))
            pool = collections.Counter(x['pool_stratum'] for x in base)
            ops = collections.Counter(route.get((method,x['request_id']),{}).get('selected_component','unknown') for x in base)
            predicates = collections.Counter(route.get((method,x['request_id']),{}).get('capability_predicate','unknown') for x in base)
            ordinary = sum(pool[k] for k in ['K=0','K=1','K>=2'])
            eligible = pool['K>=2']
            coverage.append(dict(method=method,planned_inputs=N,terminal_inputs=N,
              rule='saved ordinary-F route with >=2 distinct actually legal native keys; no gold/outcome/arm-success filter',
              eligible_inputs=eligible,full_input_denominator=N,coverage_of_all_inputs=eligible/N,
              ordinary_F_trace_inputs=ordinary,coverage_of_known_ordinary_F=eligible/ordinary,
              pool_strata=dict(pool),selected_component=dict(ops),capability_predicate=dict(predicates),
              A4_selected_inputs=ops.get('legacy_R4',0),A4_denominator=N,by_arm=[]))
            for arm in ARMS[1:]:
                values = buckets[method,arm]
                assert len(values)==N and len({x['request_id'] for x in values})==N
                costs = {category:{field:aggregate([x[category] for x in values],field) for field in FIELDS} for category in categories}
                output.append(dict(method=method,arm=arm,inputs=N,terminal=N,cost_status='complete_accounting_with_explicit_unknown_history',
                  cost=costs,end_to_end_total=None,common_original_C0_upstream_cost='unknown; excluded from known head/readout subtotal'))
                eligible_values = [x for x in values if x['pool_stratum']=='K>=2']
                assert len(eligible_values)==eligible
                coverage[-1]['by_arm'].append(dict(arm=arm,all_inputs=N,eligible_inputs=eligible,
                  eligible_native_unavailable=sum(x['native_unavailable'] for x in eligible_values),
                  all_native_unavailable=sum(x['native_unavailable'] for x in values),
                  eligible_activation_attempted=sum(x['activation_attempted'] for x in eligible_values),
                  eligible_audit_status=dict(collections.Counter(x['audit_status'] for x in eligible_values)),
                  all_audit_status=dict(collections.Counter(x['audit_status'] for x in values)),
                  eligible_invalid_F_votes=sum(x['invalid_F_votes'] or 0 for x in eligible_values)))
                for x in values:
                    z = {k:x[k] for k in keep}
                    op = route.get((method,x['request_id']),{})
                    z.update(selected_component=op.get('selected_component'), capability_predicate=op.get('capability_predicate'),
                             common_C0_upstream_cost='unknown',RCV_eligible=x['pool_stratum']=='K>=2')
                    f.write(json.dumps(z,separators=(',',':'))+'\n')
    write('per_method_costs.json', dict(snapshot='d857934',inputs_per_method_arm=N,rows=output,
      accounting='Each method receives one shared B/F/legacy-head cost plus its own extra cost. Never divide multi-arm physical requests by six or sum attributed costs as physical spend.',
      historical_common_C0_upstream='unknown for all six arms; no end-to-end monetary, energy or latency claim',
      timing='recorded event elapsed attribution, not exclusive GPU time or wall latency',correction_count=8))
    write('mechanism_coverage.json', dict(snapshot='d857934',rows=coverage,no_gold_or_outcome_conditions=True,
      denominator_policy='All 13905 per backbone retained; invalid votes, unavailable outputs and verifier failures remain explicit.',
      five_roles='Five roles are not five independent models; A1/A2 share a kernel; clinical v5 A4 coverage is zero.'))
    physical_path = OUT/'projection/physical_cost_summary.json'
    if not physical_path.exists():
        print('compact method and coverage outputs ready; physical scan pending', flush=True)
        return
    physical = json.loads(physical_path.read_text())
    inventory = json.loads(Path(spec['source_inventory']).read_text())
    reconciled = []
    for p in physical['by_model_scope']:
        assert p['scope']=='current'
        m = p['method']; expected = inventory['by_model'][m]
        checks = {a:p[a]==expected[b] for a,b in [('live_requests','new_model_requests'),('input_tokens','live_input_tokens'),('output_tokens','live_output_tokens')]}
        checks['model_seconds'] = abs(p['model_seconds']-expected['live_model_seconds'])<0.01
        assert all(checks.values()), (p,expected)
        attributed_new = {field:sum(x['cost']['new_execution_cost'][field]['known_subtotal'] for x in output if x['method']==m and x['arm']!='original_C0') for field in FIELDS}
        reconciled.append(dict(method=m,physical=p,inventory_checks=checks,per_arm_new_execution_sum=attributed_new,
          physical_minus_final_rows=dict(model_requests=p['live_requests']-attributed_new['model_requests'],
             input_tokens=p['input_tokens']-attributed_new['input_tokens'],output_tokens=p['output_tokens']-attributed_new['output_tokens'],
             model_seconds=p['model_seconds']-attributed_new['model_seconds'])))
    write('physical_reconciliation.json',dict(snapshot='d857934',methods=reconciled,
       overall=dict(model_requests=sum(p['physical']['live_requests'] for p in reconciled),
          input_tokens=sum(p['physical']['input_tokens'] for p in reconciled),output_tokens=sum(p['physical']['output_tokens'] for p in reconciled),
          model_seconds=sum(p['physical']['model_seconds'] for p in reconciled)),
       published_inventory=spec['source_inventory'],current_closeout_model_calls=0,current_closeout_grader_calls=0))
    print('all compact outputs and SQL reconciliation ready', flush=True)


def report():
    costs = json.loads((OUT/'per_method_costs.json').read_text())
    coverage = json.loads((OUT/'mechanism_coverage.json').read_text())
    physical = json.loads((OUT/'physical_reconciliation.json').read_text())
    raw_physical = json.loads((OUT/'projection/physical_cost_summary.json').read_text())
    distinct = {}
    for reference in raw_physical['replay_source_references']:
        ref = reference['source']
        key = ref['journal'], ref['request_id'], ref['ordinal']
        distinct[key] = reference['method']
    original = collections.defaultdict(list)
    handles = {}
    for (journal, task, ordinal), method in distinct.items():
        if journal not in handles:
            handles[journal] = sqlite3.connect(Path(journal).as_uri()+'?mode=ro', uri=True)
            handles[journal].execute('PRAGMA query_only=ON')
        values = handles[journal].execute("SELECT json_extract(p.value,'$.event') FROM calls c,json_each(c.physical) p WHERE c.request_id=? AND c.ordinal=?", (task, ordinal)).fetchall()
        for (text,) in values:
            e = json.loads(text)
            assert e['mode']=='live'
            original[method].append(dict(journal=journal,task_id=task,ordinal=ordinal,
               model_requests=1,input_tokens=e['input_tokens'],output_tokens=e['output_tokens'],model_seconds=e['elapsed_seconds']))
    for c in handles.values():
        c.close()
    transfer = []
    for p in physical['methods']:
        m=p['method']; total={field:sum(x[field] for x in original[m]) for field in FIELDS}
        assert all(abs(total[f]-p['physical_minus_final_rows'][f])<0.001 for f in FIELDS)
        transfer.append(dict(method=m,unique_paid_origin_callbacks=len(original[m]),cost=total,
          final_row_new_execution_plus_unique_paid_prefix_equals_physical=True,events=original[m]))
    write('transfer_cost_reconciliation.json',dict(methods=transfer,all_replay_rows=147,unique_paid_origin_callbacks=len(distinct),
        interpretation='147 replay rows represent only 75 distinct already-paid callbacks. Failed M5 initialization copies do not duplicate cost. The same-run paid-prefix costs occur in original SQL but final outputs attribute them to replay.'))
    components = collections.defaultdict(list)
    base_by_input = {}
    metadata_rows=0
    with gzip.open(OUT/'per_input_cost_coverage.jsonl.gz','rt') as f:
        for line in f:
            x=json.loads(line);metadata_rows+=1
            assert not any(k in x for k in ['correct','gold','pool_contains_gold','selected_correct_by_saved_semantics'])
            if x['arm']=='original_C0':
                continue
            key=x['method'],x['request_id']
            if x['arm']=='strong_B':
                base_by_input[key]=x['base_cost_once']
                components[x['method'],x['selected_component']].append(x['base_cost_once'])
            else:
                assert x['base_cost_once']==base_by_input[key]
    assert metadata_rows==2*6*N
    costs['shared_base_by_component']=[dict(method=m,component=c,inputs=len(v),cost={field:aggregate(v,field) for field in FIELDS}) for (m,c),v in sorted(components.items())]
    costs['timing_known_subtotal_definition']='method_attributed_cost.model_seconds.known_subtotal includes only inputs whose complete attributed elapsed is known (11402/13905); base and extra component subtotals are separately available.'
    write('per_method_costs.json',costs)
    label=dict(zip(ARMS,['C0 原方法','C1 / B','C2 无理由验证','C3 带理由验证','C4 旧池＋三答','C5 联合选择']))
    lines=['# 全量 v5 方法归属成本与机制覆盖（2026-09-28）','',
      '本页绑定已完成的 `d857934` 范围：M4/M5 每骨干每臂 13,905 输入。分析只读现存输出与 SQL，0 新模型调用、0 grader、0 缓存修改。默认仍为 `adopted_B_five_operations_v1`。','',
      '每个方法归属一次共同 B（F 或旧 head）费用，再加该臂实际追加费用。共同历史 C0 上游费用没有完整逐输入账，六臂均保留 unknown；下表为该上游之外的 head/readout 成本，不是端到端总成本。C0 的 unknown 不是免费。','',
      '| 骨干 | 臂 | 共同 B 请求 | 追加请求 | 归属请求小计 | 输入 token | 输出 token | 已知完整输入行模型秒小计 | 时间未知输入 |',
      '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for x in costs['rows']:
        if x['arm']=='original_C0':
            lines.append(f"| {x['method']} | {label[x['arm']]} | unknown | unknown | unknown | unknown | unknown | unknown | 13,905 |")
            continue
        c=x['cost']; total=c['method_attributed_cost']
        vals=[f"{c['base_cost_once']['model_requests']['total']:,}",f"{c['extra_cost']['model_requests']['total']:,}",f"{total['model_requests']['total']:,}",f"{total['input_tokens']['total']:,}",f"{total['output_tokens']['total']:,}",f"{total['model_seconds']['known_subtotal']:,.3f}",f"{total['model_seconds']['unknown_rows']:,}"]
        lines.append('| '+x['method']+' | '+label[x['arm']]+' | '+' | '.join(vals)+' |')
    lines += ['', '上述时间仅统计完整归属秒数已知的 11,402/13,905 输入；每臂另有 2,503 输入的历史时间 unknown。模型秒是事件归属和，不是独占 GPU 时间、端到端延迟、能耗或货币费用。共享成本逐方法重复用于比较，不能跨臂相加当作物理实验账。','',
      'M4 C2 比 C3 多 6 次追加请求全部来自 `v10426`：C2 实际完成 6 个取分 callback；C3 的 6 个逻辑请求均在完整上下文容量检查时失败，SQL callback 为 0，按原逻辑保留已存 F。它解释实际调用差异，不能据此称带理由版本天然更省。详见 [该输入的 stage/SQL 证据](c2_c3_call_difference.json)。','',
      '| 骨干 | 共享组件 | 输入数 | 请求 | 输入 token | 输出 token |', '|---|---|---:|---:|---:|---:|']
    for x in costs['shared_base_by_component']:
        c=x['cost'];lines.append(f"| {x['method']} | {x['component']} | {x['inputs']:,} | {c['model_requests']['total']:,} | {c['input_tokens']['total']:,} | {c['output_tokens']['total']:,} |")
    lines += ['', '只读 SQL 去重核对：19 个已列来源（17 个非零、2 个初始化失败）合 **162,979** 新物理请求、**957,810,324** 输入及 **18,291,906** 输出 token，与已发布 inventory 一致。M4 为 87,429，M5 为 75,550；记录事件秒合 331,241.294，usage unknown 为 0。这个物理总数不能除以六。','',
      '最终输出行的 new_execution 小计比物理 SQL 少 M4 39 / M5 36 请求：这些是迁移前已付且在最终行归为 replay 的前缀。147 条跨运行 replay 只对应 75 个唯一原 callback；按原 SQL 每个只计一次，差额的请求、token 和事件秒逐字段相等。两次 M5 初始化失败有 28 个失败 callback、0 新物理调用，初始化墙时仍非零。','',
      '原准备脚本对 M5 C4 八条调用前上下文超容量失败没有 stage_costs，先输出 unknown。限定 SQL 核对证明八条各有 0 callback、0 新 token；本次仅将追加费用明确为 0、归属已付 B。八条全部继续为 failed/不可用，不改评分或分母；原始投影与补正前后保留。','',
      '| 骨干 | 全输入 | F 路由 | 普通 F | NLI | 普通 F 且 K≥2 | 占全输入 | K=0 | A4 覆盖 |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for x in coverage['rows']:
        s=x['pool_strata']; lines.append(f"| {x['method']} | 13,905 | 10,178 | {x['ordinary_F_trace_inputs']:,} | {s['NLI']:,} | {x['eligible_inputs']:,} | {100*x['coverage_of_all_inputs']:.4f}% | {s.get('K=0',0)} | 0/13,905 |")
    lines += ['', '覆盖只使用旧路由及实际合法键数，不使用 gold、正确性、改进符号或某臂成功来选范围。K≥2 分母保留 M4 的 2 条 B 不可用输入；普通 F 的有效票失败也保留（K≥2 范围 M4 533 / M5 186 个无效旧 F draw）。此覆盖表是机制描述，不重新定义全 v5。','',
      '| 骨干 | 臂 | K≥2分母 | 有记录的激活尝试 | 范围内原生不可用 | 技术失败后回退已存F |', '|---|---|---:|---:|---:|---:|']
    for x in coverage['rows']:
        for a in x['by_arm']:
            lines.append(f"| {x['method']} | {label[a['arm']]} | {a['eligible_inputs']:,} | {a['eligible_activation_attempted']:,} | {a['eligible_native_unavailable']} | {a['eligible_audit_status'].get('audit_unavailable_saved_F_fallback',0)} |")
    lines += ['', 'M5 C4 的八条调用前失败没有激活 trace，因此“有记录的激活尝试”比 K≥2 范围少八条，范围和失败分母均未删除。五角色不是五个独立模型；A1/A2 共享核，临床 v5 的 A4 实际覆盖为零，旧显式模型验证属于其他范围。','',
      '机器文件：[方法成本](per_method_costs.json)、[机制覆盖](mechanism_coverage.json)、[物理对账](physical_reconciliation.json)、[迁移前缀对账](transfer_cost_reconciliation.json)、[八条费用补正](cost_correction_receipt.json)、[19输出源哈希](source_binding_verification.json)、[无 gold 逐输入元数据](per_input_cost_coverage.jsonl.gz)。私有原始投影保留在 `projection/`，不作为公开全量原文导出。','',
      '本次费用与覆盖收尾完成；历史未知仍明列，冻结后确认与独立 F 复本未执行，不能由本页替代。研究主记录由上级任务续写 `/home/data3/txy/docs/research/cf_moa.md`。','']
    (OUT/'attributed_costs.md').write_text('\n'.join(lines))
    write('completion_receipt.json',dict(status='complete',model_calls=0,grader_calls=0,cache_writes=0,
      per_input_metadata_rows=metadata_rows,source_output_hashes_verified=19,full_denominator_each_arm=N,
      current_physical_calls_reconciled=162979,shared_B_once_per_arm_verified=True,corrections=8,
      original_projection_unchanged=True,private_projection_contains_saved_gold_derived_diagnostics=True,
      public_metadata_contains_gold_or_correctness=False,unknown_history_preserved=True))
    print('cost report and all reconciliations complete', flush=True)


if __name__=='__main__':
    {'bind':source_bindings,'finalize':finalize,'report':report}[sys.argv[1]]()
