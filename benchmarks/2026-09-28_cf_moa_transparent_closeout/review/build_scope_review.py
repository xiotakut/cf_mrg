"""Read saved results/metadata; write closeout review evidence only. No inference/grading."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json

ROOT = Path('/home/data3/txy')
RUN = ROOT / 'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924'
PUB = ROOT / 'Documents/Codex/2026-09-24/cf_moa_github_rcv_progress/benchmarks/2026-09-26_cf_moa_rcv_full_v5'
OUT = RUN / 'closeout_20260928/review'
OLD_A4 = ROOT / 'Documents/Codex/2026-09-17/r4_structural_head/physiology_head/v2/heldout/summary.json'
NLI_REVIEW = ROOT / 'Documents/Codex/2026-09-18/r5_head/mechanism_research/data/nli_semantic_cross_review.json'


def read(path):
    return json.loads(path.read_text())


def lines(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def binding(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


ablation_source = PUB / 'data/operation_ablations/summary.json'
table_source = PUB / 'data/tables/table4_operation_ablations.json'
receipt_source = PUB / 'data/operation_ablations/receipt.json'
receipt = read(receipt_source)
summary = read(ablation_source)
table = read(table_source)
coverage_source = RUN / 'scope/cache_coverage.jsonl'
coverage = list(lines(coverage_source))
statuses_source = PUB / 'data/operation_ablations/per_input_status.jsonl'
statuses = list(lines(statuses_source))
assert len(summary) == len(table) == 6
assert len(statuses) == 738
models = {}
all_unit_memberships = {}
for model in ('M4', 'M5'):
    rows = [r for r in coverage if r['model'] == model]
    assert len(rows) == 13905
    rule_requests = {r['request_id'] for r in rows if r['capability_predicate'] == 'original_rule_predicate'}
    assert len(rule_requests) == 123
    groups = []
    base_units = None
    for group in [g for g in summary if g['method'] == model]:
        cats = group['native_units']['categories']
        native_all = next(c for c in cats if c['category'] == 'ALL')
        units = {u['unit_id']: u['score'] for u in group['native_units']['units'] if u['category'] == 'ALL'}
        assert len(units) == native_all['units'] == group['inputs'] == 123
        assert abs(sum(units.values()) / 123 - native_all['mean_native_unit_score']) < 1e-12
        assert abs(group['correct'] / 123 - native_all['mean_native_unit_score']) < 1e-12
        group_status = [r for r in statuses if r['method'] == model and r['arm'] == group['arm']]
        assert {r['request_id'] for r in group_status} == rule_requests
        assert len(group_status) == 123
        t = next(t for t in table if t['method'] == model and t['arm'] == group['arm'])
        for key, value in group.items():
            if key != 'native_units':
                assert t[key] == value
        assert t['native_ALL_mean'] == native_all['mean_native_unit_score']
        groups.append({**t, 'category_denominators': {c['category']: c['units'] for c in cats}})
        if group['arm'] == 'strong_B':
            base_units = units
    full_units_source = PUB / f'data/full_v5/{model.lower()}/native_units.jsonl.gz'
    full_units = list(lines(full_units_source))
    full_b = {r['unit_id']: r['score'] for r in full_units if r['arm'] == 'strong_B' and r['category'] == 'ALL'}
    assert len(full_b) == 6104
    assert all(full_b[k] == v for k, v in base_units.items())
    all_unit_memberships[model] = {r['unit_id'] for r in full_units}
    r4_units = {r['unit_id'] for r in full_units if r['arm'] == 'strong_B' and r['category'] == 'R4'}
    assert len(r4_units) == 13
    full_status_source = PUB / f'data/full_v5/{model.lower()}/per_input_status.jsonl.gz'
    full_status = {r['request_id']: r for r in lines(full_status_source) if r['arm'] == 'strong_B'}
    ablation_status = [r for r in statuses if r['method'] == model and r['arm'] == 'strong_B']
    assert all(r['correct'] == full_status[r['request_id']]['correct'] for r in ablation_status)
    routes = dict(Counter(r['capability_predicate'] for r in rows))
    assert sum(routes.values()) == 13905
    assert routes == {'original_catalog_predicate': 3560, 'original_rule_predicate': 123,
                      'original_passthrough_predicate': 44, 'adopted_F_native_capability': 10178}
    models[model] = {
        'rows': groups, 'exact_rule_request_ids': sorted(rule_requests),
        'exact_rule_ALL_unit_ids': sorted(base_units),
        'full_v5_B_unit_scores_and_input_correctness_match': True,
        'capability_counts': routes,
        'clinical_A4_capability_inputs': 0, 'clinical_R4_native_units': 13,
        'full_native_units_source': binding(full_units_source),
        'full_input_status_source': binding(full_status_source),
    }

a4_table_source = PUB / 'data/tables/table3_A4_separate_model_scope.json'
a4_table = read(a4_table_source)
old_a4 = read(OLD_A4)
for row in a4_table:
    src = next(s for s in old_a4['results'] if s['method'] == row['model'] and s['arm'] == row['arm'])
    assert row['profiles'] == 24 and row['inputs'] == src['n'] == 288
    assert row['binary_correct'] == src['correct']
    assert row['joint_numeric_correct'] == src['joint_numeric_correct']
    assert row['all_outputs_correct'] == src['all_outputs_correct']

dump('operation_ablation_binding.json', {
    'status': 'verified_saved_123_rule_subset_and_separate_A4_panel',
    'date': '2026-09-28',
    'public_commit': 'd85793470cf75af57217f3fdc73093f494d9f003',
    'public_package': str(PUB),
    'scope': 'All 123 previously frozen rule-capability inputs and 123 nonreference ALL units per backbone; not historical121, natural52, or a new full-v5 system ablation.',
    'mechanism': 'A1/add and A2/remove are projections of one shared adopted support/rule execution kernel, not independent trained models.',
    'sources': [binding(p) for p in [ablation_source, table_source, receipt_source, statuses_source,
                                    coverage_source, PUB / 'method_spec.resolved.json',
                                    PUB / 'analysis_source/tables/build_tables.py']],
    'historical_ablation_execution': {
        k: receipt[k] for k in ['status', 'inputs_per_method', 'complete_native_nonreference_units_per_method',
                                'operation_views', 'new_model_calls', 'new_fact_extractions',
                                'new_old_head_executions', 'new_native_grader_calls', 'reused_scores']},
    'closeout_new_model_calls': 0, 'closeout_new_grader_calls': 0,
    'models': models,
    'interpretation_limits': [
        'All nonapplicable/unavailable cases remain in each 123-input denominator.',
        '119/106 applicable projections do not replace the 123-input denominator.',
        'R1 72, R2 55, R3 10 overlap; these counts must not be summed.',
        'These saved operation projections do not establish independent-agent or full-system causal contributions.',
        'The receipt records 53 original analysis grades; this closeout only reads saved results.'
    ],
    'A4_separate_panel': {
        'sources': [binding(OLD_A4), binding(a4_table_source), binding(ROOT / 'docs/research/r4_consequence_head.md')],
        'identity': '2026-09-17 physiology_head/v2/heldout, frozen typed-patch validation on the same public simglucose supplied model',
        'profiles_per_backbone': 24, 'questions_per_profile': 12, 'inputs_per_backbone_per_arm': 288,
        'not_clinical_patients': True, 'not_current_full_v5': True,
        'original_backbones_with_original_guided_unguided_decoding_not_end_to_end_RAG_rerun': True,
        'fixed_language_and_interventions': 'four fixed action types, three limited query forms, complete supplied model/parameters/13 states and auxiliary quantities',
        'independence_limit': 'held-out parameter/initial-state profiles within one model and action/language family; no cross-model, open-language, or clinical individual causal-effect validation',
        'rows': a4_table,
        'closeout_new_model_calls': 0, 'closeout_new_integrations': 0,
    }
})

exposure_source = RUN / 'scope/exposure_review.json'
exposure = read(exposure_source)
nli = read(NLI_REVIEW)
confirmed_nli = [r for r in nli['comparisons'] if r['independent_final_category'] == 'clear_text_label_conflict']
assert len(confirmed_nli) == 1
nli_unit = confirmed_nli[0]['unit_id']
nli_membership = {m: nli_unit in ids for m, ids in all_unit_memberships.items()}
assert not any(nli_membership.values())
v5_overlap = next(r for r in exposure['overlaps'] if r['scope'] == 'formal_v5')
assert v5_overlap['group_overlap'] == v5_overlap['unit_overlap'] == v5_overlap['endpoint_id_overlap'] == 0
m20_membership = {m: sorted(u for u in ids if u.startswith('M20:255:')) for m, ids in all_unit_memberships.items()}
dump('data_issue_evidence_review.json', {
    'status': 'no_established_objective_issue_in_current_full_v5_from_reviewed_existing_evidence',
    'date': '2026-09-28',
    'review_scope': 'Targeted existing-record and frozen-membership cross-check only; not an exhaustive data audit or new case adjudication.',
    'exhaustive_audit': False, 'new_case_semantic_audit': False,
    'confirmed_objective_issues_current_full_v5': [],
    'data_issues_file': str(OUT / 'data_issues.jsonl'),
    'data_issues_rows': 0,
    'searched_record_sources': [binding(ROOT / 'docs/data/construction.md'), binding(ROOT / 'docs/evaluation/v5.md'), binding(ROOT / 'docs/research/cf_moa.md')],
    'existing_evidence_checked': [
        {
            'kind': 'previously_confirmed_NLI_text_label_conflict',
            'unit_id': nli_unit, 'original_review_date': nli['completed_at'],
            'source': binding(NLI_REVIEW),
            'current_frozen_membership_by_backbone': nli_membership,
            'formal_v5_overlap_evidence': {'source': binding(exposure_source), 'row': v5_overlap},
            'decision': 'Outside current full-v5 scope; do not represent a pending confirmation-set issue as a full-v5 data defect.',
            'model_outcomes_read_during_original_review': False,
            'original_source_label_or_member_changed': False,
        },
        {
            'kind': 'unresolved_reference_reliability_concern',
            'family_id': 'M20:255', 'reviewed_original_input_ids': ['s024962', 's024963'],
            'source': str(ROOT / 'docs/data/construction.md') + '#r5-mechanism-m20-reference-question',
            'existing_evidence_path': str(ROOT / 'Documents/Codex/2026-09-18/r5_head/mechanism_research/data/m20_reference_question_audit.json'),
            'current_family_ALL_units_by_backbone': m20_membership,
            'original_record_status': '待正式裁定; original gold and formal v5 unchanged',
            'decision': 'Retain as an existing unresolved concern; no formal label erratum or objective exclusion is established by the record. Do not extrapolate the two reviewed endpoints to all family variants.',
            'current_closeout_model_outcomes_known': True,
            'new_case_audit_or_adjudication': False,
        },
        {
            'kind': 'CUPCase_historical_source_label_issues',
            'source': str(ROOT / 'docs/data/construction.md'),
            'decision': 'Separate R3 new-source qualification history; not evidence that current frozen full-v5 contains these records. No issue imported into current data_issues.',
        },
        {
            'kind': 'implementation_and_report_corrections',
            'examples': ['invalid native-answer cache interface', 'historical paired diagnosis-versus-multi description', 'legal U+2029 JSONL reader behavior', 'GPU initialization failures'],
            'decision': 'Model/output-interface, documentation, parser, or runtime issues; not independent evidence of corrupt benchmark inputs or incorrect labels.',
        },
    ],
    'actions': {'data_modified': False, 'labels_modified': False, 'members_removed': 0,
                'new_model_calls': 0, 'new_grader_calls': 0, 'new_sensitivity_dataset': False},
    'limitations': [
        'An empty issue list means no qualifying objective full-v5 defect was established in this bounded evidence review; it does not certify all data as error-free.',
        'Outcome losses, invalid/unavailable predictions, pool_has_gold failure, and low source scores are not dataset exclusion grounds.',
        'Prior review annotations, including existing label references, were read; no new confirmation inputs or gold files were opened, and no blind-review claim is made.'
    ]
})
(OUT / 'data_issues.jsonl').write_text('')
print(json.dumps({'status': 'complete', 'operation_groups': 6, 'inputs_per_group': 123,
                  'A4_saved_rows': len(a4_table), 'confirmed_current_full_v5_data_issues': 0,
                  'new_model_calls': 0, 'new_grader_calls': 0}, ensure_ascii=False))
