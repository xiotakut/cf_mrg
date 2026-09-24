"""One-off allowlisted publication projection. No inference, parsing or native grading."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('/home/data3/txy/Documents/Codex/2026-09-24')
RUN = BASE / 'cf_moa_candidate_verify_20260924'
REC = RUN / 'recovery_gpu23'
OUT = BASE / 'cf_moa_candidate_publication/data_staging'
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = {}
PROJECTIONS = {}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    SOURCES[str(path)] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    if path.suffix == '.jsonl':
        with path.open() as stream:
            return [json.loads(line) for line in stream if line.strip()]
    return json.loads(path.read_text())


def pick(row, fields):
    return {key: row[key] for key in fields.split() if key in row}


def write(name, rows, sources, fields):
    path = OUT / name
    if name.endswith('.jsonl'):
        path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    else:
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    PROJECTIONS[name] = {'source_files': [str(x) for x in sources], 'projection': fields}


summary_path = REC / 'analysis/complete_results/summary.json'
cost_path = REC / 'analysis/complete_results/cost.json'
summary, costs = read(summary_path), read(cost_path)
# These reviewed aggregate objects contain only IDs, existing scalar metrics and
# methodological notes, including every mother-family/source/format and pair.
assert len(summary['reports']) == len(costs['costs']) == 40
REPORT_FIELDS = set('panel method arm repair_ids harm_ids unavailable_recovery_ids correct_unavailable_recovery_ids correct_lost_to_unavailable_ids repairs harms unavailable_recoveries correct_unavailable_recoveries correct_lost_to_unavailable same_scope_B correct_count_delta counts accuracy_full_denominator result_status missing_candidate_inputs technical_failures explicit_saved_F_fallbacks native_unit_metrics auxiliary_mapping_metrics auxiliary_unique_metrics trigger_comparison F_supported_comparison full_panel_base_identity candidate_pool strata trigger_path_strata pairs'.split())
assert all(set(report) == REPORT_FIELDS for report in summary['reports'])
write('quality_summary.json', summary, [summary_path], 'Reviewed full aggregate object; all 40 groups and existing native/auxiliary/pool/strata/pair metrics; no answer text or gold.')
write('cost_summary.json', costs, [cost_path], 'Reviewed full scalar cost object; inherited B/F attributed once per method, kept separate from new physical experiment cost.')

status_path = REC / 'analysis/complete_results/per_input_status.jsonl'
status_fields = 'panel method arm request_id correct native_valid run_status triggered native_answer_ref auxiliary_exact has_auxiliary family_id source answer_format'
statuses = [pick(row, status_fields) for row in read(status_path)]
assert len(statuses) == 3460
write('per_input_status.jsonl', statuses, [status_path], status_fields.split())
with (OUT / 'per_input_status.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=status_fields.split(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(statuses)
PROJECTIONS['per_input_status.csv'] = PROJECTIONS['per_input_status.jsonl']

native_path = REC / 'analysis/complete_results/native_scored.jsonl'
native_fields = 'panel method arm request_id record_id run_status correct invalid format_invalid unmapped_diagnosis ambiguous raw_exact uncertainty option_f1 tp fp fn predicted_set_size applicability native_available method_score semantic_result score_origin seed auxiliary_score_origin document_detection'
native = [pick(row, native_fields) for row in read(native_path)]
for row in native:
    if 'document_detection' in row and row['document_detection'] is not None:
        row['document_detection'] = pick(row['document_detection'], 'valid exact tp fp fn method_score correction_semantic_score')
assert len(native) == 4180
write('native_scoring_metadata.jsonl', native, [native_path], native_fields.split())

status_lookup = {(x['method'], x['request_id']): x for x in statuses if x['arm'] == 'F'}
calls, selected = [], []
ENGINE_FIELDS = 'model seed dtype gpu_memory_utilization max_model_len max_num_seqs max_num_batched_tokens num_gpu_blocks_override enable_prefix_caching enable_chunked_prefill enforce_eager max_logprobs guided_decoding_backend'
SAMPLING_FIELDS = 'n best_of _real_n presence_penalty frequency_penalty repetition_penalty temperature top_p top_k min_p seed ignore_eos max_tokens min_tokens logprobs prompt_logprobs detokenize skip_special_tokens spaces_between_special_tokens include_stop_str_in_output truncate_prompt_tokens output_kind output_text_buffer_length guided_decoding extra_args'
EVENT_FIELDS = 'mode model config_hash input_tokens output_tokens elapsed_seconds elapsed_attribution batch_seconds finish_reason physical_batch_size'
SELECT_FIELDS = 'method request_id task_id arm input_hash base_answer_ref elapsed_seconds cost status verification_status verification_failed verification_fallback_saved_F'
TRACE_FIELDS = 'old_f_identity include_rationales seed logical_score_calls new_answer_generation_calls records scores fallback_saved_F candidate_keys representatives route selected_key tied_maximum selected_original_response_index score_interpretation output_policy'
call_sources, selection_sources = [], []
for method in ('M4', 'M5'):
    call_path = REC / f'runs/{method.lower()}/model_calls.jsonl'
    selection_path = REC / f'runs/{method.lower()}/proposals.jsonl'
    call_sources.append(call_path)
    selection_sources.append(selection_path)
    proposals = read(selection_path)
    by_task = {x['task_id']: x for x in proposals}
    for source in read(call_path):
        assert len(source['physical']) == 1
        physical = source['physical'][0]
        request = physical['request']
        accepted = physical['engine_accepted']
        actual_sampling = accepted['sampling_params']
        constructed_sampling = request['sampling_params']
        sampling_differences = {k: {'constructed': constructed_sampling.get(k), 'engine_accepted': actual_sampling.get(k)}
                               for k in set(actual_sampling) | set(constructed_sampling)
                               if actual_sampling.get(k) != constructed_sampling.get(k)}
        assert sampling_differences == {'output_kind': {'constructed': 0, 'engine_accepted': 2}}
        task = source['request_id']
        callback = by_task[task]['model_callbacks'][source['ordinal']]
        row = {
            'method': method, 'gpu': 3 if method == 'M4' else 2,
            'panel': status_lookup[(method, by_task[task]['request_id'])]['panel'],
            'request_id': by_task[task]['request_id'], 'task_id': task,
            'arm': by_task[task]['arm'], 'ordinal': source['ordinal'],
            'stage': callback['stage'], 'status': source['status'],
            'phase': source['phase'], 'physical_status': physical['status'],
            'submission_state': physical['submission_state'],
            'logical_request_hash': callback['request_hash'],
            'physical_request_hash': physical['request_hash'],
            'engine_request_id': accepted['engine_request_id'],
            'engine_core_request_id': physical['engine_core_request_id'],
            'actual_engine_parameters': pick(request['engine_kwargs'], ENGINE_FIELDS),
            'actual_sampling_parameters': pick(accepted['sampling_params'], SAMPLING_FIELDS),
            'omitted_sampling_token_id_fields_sha256': digest({k: v for k, v in accepted['sampling_params'].items() if 'token_ids' in k}),
            'decoding_parameters_match_constructed_request': True,
            'engine_interface_normalization': sampling_differences,
            'event': pick(physical['event'], EVENT_FIELDS),
            'code_logprobs': source['result']['value'],
            'callback_seconds': callback['callback_seconds'],
            'reserved_input_tokens': callback['reserved_input_tokens'],
            'reserved_output_tokens': callback['reserved_output_tokens'],
            'error_type': None if source['error'] is None else source['error']['type'],
            'error_category': None if source['error'] is None else source['error']['category'],
            'projection_is_full_request': False,
        }
        assert set(row['code_logprobs']) == {'A', 'B'}
        calls.append(row)
    for source in proposals:
        row = pick(source, SELECT_FIELDS)
        row['panel'] = status_lookup[(method, source['request_id'])]['panel']
        row['native_valid'] = source['result']['native_valid']
        row['native_answer_object_canonical_sha256'] = digest(source['result']['native_answer'])
        row['trace_metadata'] = pick(source['result']['trace'], TRACE_FIELDS)
        row['omitted'] = ['complete native response', 'selected raw response', 'actual messages and retrieved case context']
        selected.append(row)
assert len(calls) == 780 and len(selected) == 190
write('model_call_metadata.jsonl', calls, call_sources, {'engine_fields': ENGINE_FIELDS.split(), 'sampling_fields': SAMPLING_FIELDS.split(), 'event_fields': EVENT_FIELDS.split(), 'other_fields': list(calls[0]), 'messages_prompts_and_token_sequences_omitted': True})
write('candidate_selection_metadata.jsonl', selected, selection_sources, {'outer_fields': SELECT_FIELDS.split(), 'trace_fields': TRACE_FIELDS.split(), 'complete_native_response_omitted_referenced_by_hash': True})

old_call_path = RUN / 'runs/m4/model_calls.jsonl'
failed = []
for source in read(old_call_path):
    failed.append({
        'method': 'M4', 'gpu': 0, 'run_identity': 'initial_failed_attempt_preserved',
        'task_id': source['request_id'], 'ordinal': source['ordinal'],
        'status': source['status'], 'phase': source['phase'],
        'error': pick(source['error'], 'type category message'),
        'physical_records': len(source['physical']), 'valid_model_requests': 0,
        'input_tokens': 0, 'output_tokens': 0,
        'logical_request_canonical_sha256': digest(source['request']),
        'not_counted_as_successful_candidate_verification': True,
    })
assert len(failed) == 32 and all(x['phase'] == 'initializing' for x in failed)
write('prior_initialization_failures.jsonl', failed, [old_call_path], list(failed[0]))

# Original case quotations and prose observations remain in the private files.
# This is only their reviewed category/selection-outcome projection.
old_review, review_sources = [], []
for method in ('M4', 'M5'):
    path = RUN / f'semantic_review/{method.lower()}.jsonl'
    review_sources.append(path)
    for source in read(path):
        row = pick(source, 'review_version panel method request_id answer_format F_path sample_sha256')
        row['review_unit'] = 'one_unique_input_backbone_all_three_saved_seeds'
        row['categories'] = source.get('categories') or sorted({f['category'] for f in source['findings']})
        row['baseline_correct'] = source.get('baseline_saved_correct', source.get('baseline_correct_saved'))
        row['seed_outcomes'] = []
        for seed in source['seed_outcomes']:
            if method == 'M4':
                value = {'seed': seed['seed'], 'correct': seed['saved_native_correct'], 'repair': seed['change'] == 'repair', 'harm': seed['change'] == 'harm'}
            else:
                value = {'seed': seed['seed'], 'correct': seed['new_correct_saved'], 'repair': seed['repair_saved'], 'harm': seed['harm_saved']}
            row['seed_outcomes'].append(value)
        row['private_original_text_review_completed'] = True
        row['medical_truth_independently_regraded'] = False
        row['code_mapping_issue_confirmed'] = source.get('code_mapping_issue_confirmed', source.get('output_mapping_only_supported', False))
        row['interpretation'] = 'Observed text and saved selection outcomes; categories are nonexclusive, not proof of model-internal causes.'
        row['new_model_calls'] = row['new_native_score_calls'] = 0
        old_review.append(row)
assert len(old_review) == 31
write('prior_semantic_review_metadata.jsonl', old_review, review_sources, list(old_review[0]))

example_path = REC / 'counterexamples/smoke_four.jsonl'
example_notes = {
    ('M4', 'd00014'): 'A task-scope/generalizability mismatch is visible in one existing rationale. The rationale-free verifier selected that response; this does not show causal influence from text it never received. Adding rationales changes selection back to the saved correct candidate.',
    ('M4', 'n00009'): 'Rationale-free selection repairs the main answer; adding untrusted rationales selects a different wrong candidate. Auxiliary detection remains incomplete despite the main-answer repair.',
    ('M5', 'd00015'): 'The correct old candidate wins without rationales and loses with rationales. Swapped arbitrary encodings have visibly different semantic probabilities; no unique semantic cause is established.',
    ('M5', 'n00014'): 'Both arms select a wrong old candidate with a very high normalized verification score. Existing rationale explicitly attends to the question polarity, so missed negation is not established. These scores are not calibrated correctness probabilities.',
}
examples = []
for source in read(example_path):
    row = pick(source, 'method request_id panel scope task_format rationales_change_rank_order rationales_change_selected_key candidate_ability_failure')
    row['mechanism_summary_without_case_text'] = example_notes[(source['method'], source['request_id'])]
    row['quote_locations_checked_in_private_trace'] = len(source['quotes'])
    row['candidate_count'] = len(source['candidate_keys'])
    row['arms'] = {}
    for arm, value in source['arms'].items():
        row['arms'][arm] = pick(value, 'mean_scores rank_order selected_key correct_from_existing_smoke_score baseline_correct_from_existing_smoke_score repair harm selected_original_response_index returned_complete_existing_response_verified run_status new_model_cost_already_in_main_experiment failure_stages')
    row['new_model_calls_for_review'] = row['new_native_score_calls_for_review'] = 0
    row['causality_limit'] = 'Verifier emits one code without a new reasoning trace. Existing selected rationale is not a causal explanation of verifier selection.'
    examples.append(row)
assert len(examples) == 4 and sum(x['quote_locations_checked_in_private_trace'] for x in examples) == 26
write('fixed_smoke_counterexample_metadata.jsonl', examples, [example_path], {'fields': list(examples[0]), 'case_text_and_original_quotes_omitted': True, 'mechanism_notes': 'Short manually written nonclinical summaries from already completed private reviews; no new inference or medical grading.'})

decision_path = REC / 'decision.json'
decision = read(decision_path)
decision_fields = 'at experiment execution_status quality_identity independent_evaluation default_system f_disagreement_reanswer candidate_only_adopted candidate_with_rationales_adopted candidate_only_conclusion candidate_with_rationales_conclusion policy reviewed_existing_change_groups existing_trigger_groups existing_supplemental_rows non_NLI_groups distinct_existing_candidates verification_outputs NLI_passthrough_outputs real_cost_this_recovery native_scoring_this_recovery prior_cached_control_native_scores old_failed_run no_more_automatic_experiments'
public_decision = pick(decision, decision_fields)
write('decision.json', public_decision, [decision_path], decision_fields.split())

analysis_receipt_path = REC / 'analysis/complete_results/receipt.json'
analysis_receipt = read(analysis_receipt_path)
receipt_fields = 'actual_new_native_score_calls auxiliary_only_backfills canonical_table_read new_model_calls script_sha256 score_cache_sha256 reused_functions candidate_run_status'
write('analysis_receipt_metadata.json', pick(analysis_receipt, receipt_fields), [analysis_receipt_path], receipt_fields.split())

vllm_llm = Path('/home/data3/txy/MedRGAG/.venv/lib/python3.10/site-packages/vllm/entrypoints/llm.py')
vllm_params = vllm_llm.parent.parent / 'sampling_params.py'
for path in (vllm_llm, vllm_params):
    SOURCES[str(path)] = {'sha256': sha(path), 'bytes': path.stat().st_size}
assert 'sp.output_kind = RequestOutputKind.FINAL_ONLY' in vllm_llm.read_text()
assert 'CUMULATIVE = 0' in vllm_params.read_text() and 'FINAL_ONLY = 2' in vllm_params.read_text()
normalization = {
    'observed_calls': 780, 'field': 'sampling_params.output_kind',
    'constructed_value': 0, 'constructed_name': 'CUMULATIVE',
    'engine_accepted_value': 2, 'engine_accepted_name': 'FINAL_ONLY',
    'other_sampling_fields_equal': True,
    'evidence': [{'file': str(vllm_llm), 'line': 1350, 'sha256': sha(vllm_llm)},
                 {'file': str(vllm_params), 'line': 113, 'sha256': sha(vllm_params)}],
    'interpretation': 'Installed vLLM LLM entrypoint always sets SamplingParams.output_kind to FINAL_ONLY before engine submission; this selects final-only response delivery rather than intermediate cumulative responses, not a change to decoding probabilities or max_tokens.',
    'historical_receipts_unchanged': True,
    'new_models_or_scores': 0,
}
write('engine_interface_normalization.json', normalization, [*call_sources, vllm_llm, vllm_params], list(normalization))

# The standalone checker only reads these public scalar projections.
import runpy
verifier = runpy.run_path(str(OUT / 'verify_public_data.py'))
checks = verifier['verify'](OUT, check_manifest=False)
assert checks['status'] == 'passed'
assert all(sha(Path(path)) == value['sha256'] for path, value in SOURCES.items())
write('verification_receipt.json', {
    **checks, 'new_model_calls_this_export': 0, 'new_native_score_calls_this_export': 0,
    'old_head_replays_this_export': 0, 'private_source_bytes_unchanged': True,
    'source_projection_only': True, 'full_private_trace_published': False,
}, [], 'Derived consistency checks over saved public projections only; no native rescoring.')

(OUT / 'README.md').write_text('''# 候选验证效果实验：公开数据与trace元数据

这是2026-09-24已完成实验的发布投影，不是新增模型实验。本次导出0模型调用、0原生评分、0旧head回放。全部40个面板×骨干×实验臂结果保留历史121／自然52完整分母。

- `quality_summary.json`：40组完整结果，含原生ALL/类别单元、辅助检测、候选池覆盖与选择率、修复/误伤、母题/来源/格式分层及逐配对/区间。旧普通重答三seed全部保留。
- `cost_summary.json`：每个方法继承一次已付B/F成本，另列追加计算；不能跨臂累加继承成本来声称本轮物理花费。
- `per_input_status.jsonl` / `.csv`：3460行完整逐输入状态；`native_scoring_metadata.jsonl`：4180条原生评分映射。只保留现成评分与状态，不包含答案正文或gold。
- `model_call_metadata.jsonl`：780次真实score调用的请求哈希、实际engine/sampling参数、完成状态、A/B logprobs、token与耗时。实际消息、检索原文、渲染prompt、原始返回与token序列不公开；哈希不等于这些原内容已发布。采样token-ID列表仅保留哈希。
- `candidate_selection_metadata.jsonl`：190条执行输出（176候选选择、14 NLI原F直返），全候选键、两次交换编码分数、选中索引、原响应哈希与成本。选中完整原生对象保存在服务器私有trace，不在此文件中。
- `prior_initialization_failures.jsonl`：原GPU0批32次初始化失败，0成功计算/0token；473.925秒初始化墙时见`decision.json`。8条旧smoke回退没有改名成新验证成功。
- `prior_semantic_review_metadata.jsonl`：31个旧修复/误伤独立组、93个三seed结果与非互斥原因类别；原文引文留私有记录，不是医学独立复判。
- `fixed_smoke_counterexample_metadata.jsonl`：4个事先固定smoke反例的短机制摘要与分数；26条原文位置已在私有trace核验。其成本属于本次780调用，不额外累加；反例不代替完整面板估计。
- `decision.json`：两臂暂不默认采用的结论；`analysis_receipt_metadata.json`：已完成评分的来源、数量和完整终态。
- `engine_interface_normalization.json`：发布核对发现780条请求的包装`output_kind=0`在实际vLLM入口统一变为`2`。本地`vllm/entrypoints/llm.py:1350`明确在engine提交前设置`FINAL_ONLY`，`sampling_params.py:113`定义0为CUMULATIVE、2为FINAL_ONLY；这是仅返回最终结果的接口模式，其余实际采样字段逐项一致。没有将整个sampling对象声称为逐字段完全一致，原历史验收收据不改写。
- `source_manifest.json`：准确来源文件SHA/字节数、投影字段、公开制品SHA；`verification_receipt.json`：导出一致性收据。

**public metadata != full trace。** 当前题面、选项文本、模型真实messages、检索上下文、理由、原始输出、完整原生响应、gold及SQLite仍在服务器。公开文件足以复核计数、费用、状态与已保存指标，不足以独立重做医学语义评分。固定公共提示源码由上层`source_snapshot/`提供，不因数据隐藏病例全文而删掉公共提示。

两臂新增780次真实取分，5,504,408输入token、780输出token；未重跑旧F或补造早停票。旧初始化失败与新成功批次分列。默认旧B不变；带理由臂开发有增益，但自然M5原生单元均分及自然保持配对仍有退步，不能称稳定泛化。

从本数据目录运行独立公开一致性验证：`python3 verify_public_data.py`；或从发布包根目录运行`python3 data/verify_public_data.py --data-dir data`。只需Python标准库，不读取私有目录、不运行模型或grader。
''')
PROJECTIONS['README.md'] = {'source_files': [], 'projection': 'Publication data navigation and privacy/scope boundary; all quantities verified from saved metadata.'}
PROJECTIONS['verify_public_data.py'] = {'source_files': [], 'projection': 'Standalone standard-library consistency checker; public metadata only.'}
files = [{'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'source_manifest.json']
(OUT / 'source_manifest.json').write_text(json.dumps({
    'version': 'candidate_verification_public_data_v1', 'date': '2026-09-24',
    'operation': 'Allowlisted projection of existing results; no model inference, grading or head replay.',
    'source_files': SOURCES, 'projections': PROJECTIONS, 'public_files': files,
    'full_private_trace_published': False, 'export_script_sha256': sha(Path(__file__)),
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(verifier['verify'](OUT), ensure_ascii=False, indent=2))
