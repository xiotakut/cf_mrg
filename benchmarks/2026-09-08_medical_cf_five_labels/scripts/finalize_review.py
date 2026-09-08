"""Apply reviewed annotations to the already frozen cohort; never select new rows."""
import csv
import json
from collections import Counter, defaultdict
from contextlib import ExitStack
from pathlib import Path

from assemble_full import ROOT, LABELS, FIELDS, rows, dumps

REVIEW = ROOT / 'review_20260908'
OVERLAYS = [
    'parts/clinical_existing/classification_review.jsonl',
    'parts/evidence_other/classification_review.jsonl',
    'parts/new_clinical/classification_review.jsonl',
    'parts/new_clinical/cpv_review.jsonl',
    'parts/evidence_other/equity_review.jsonl',
    'review_20260908/protocol_review.jsonl',
    'review_20260908/cultural_review.jsonl',
    'review_20260908/multimodal_review.jsonl',
]
PATCH_FILE = 'parts/evidence_other/amqa_feasibility_patch.jsonl'
AUDIT_PATCH_FILES = ['audit_20260908/corrections/' + name + '.jsonl'
                     for name in ['clinical', 'amqa', 'gold']]
METHODS = {'semantic_item_review', 'semantic_group_review', 'structural_verification'}
RESOLUTIONS = {'classified', 'insufficient_evidence', 'invalid_source', 'outside_five_labels'}
ANNOTATION_FIELDS = {'change', 'target', 'labels', 'rationale', 'evidence', 'cannot_infer',
    'judgments', 'review_state', 'review_method', 'review_resolution', 'clinical_review'}
REVIEW_FIELDS = ['review_state', 'review_method', 'review_resolution', 'review_coverage',
    'reviewed_target_count', 'classified_target_count', 'unclassified_target_count']
HISTORY_FIELDS = ['labels', 'status', 'annotation_method', 'rationale', 'adjudication',
    'rule_ids', 'rule_id', 'rule_matches', 'target_annotations', 'grounding_reviewed_unit_id',
    'preserved_review_source', 'inherited_adjudication_file']


def normalize_review(r):
    assert r['review_state'] == 'reviewed' and r['clinical_review'] is False, r['unit_id']
    assert r['review_method'] in METHODS and r['review_resolution'] in RESOLUTIONS
    assert bool(r['labels']) == (r['review_resolution'] == 'classified'), r['unit_id']
    for key in ['change', 'target', 'rationale', 'evidence', 'cannot_infer']:
        assert r.get(key), (r['unit_id'], key)
    # Some sources have one actual target; retain an explicit adjudication even
    # when that target cannot receive an R label.
    if not r.get('judgments'):
        r['judgments'] = [{k: r[k] for k in ['target', 'labels', 'rationale', 'evidence', 'cannot_infer', 'review_resolution']}]
    for i, j in enumerate(r['judgments']):
        j['labels'] = sorted(set(j.get('labels', [j['label']] if j.get('label') else [])))
        j.pop('label', None)  # Active labels have one canonical representation.
        assert set(j['labels']) <= set(LABELS)
        j.setdefault('judgment_id', r['unit_id'] + ':review_target_' + str(i))
        j.setdefault('review_resolution', 'classified' if j['labels'] else r['review_resolution'])
        if not j['labels'] and j['review_resolution'] == 'classified':
            j['review_resolution'] = 'insufficient_evidence'
        for k in ['rationale', 'evidence', 'cannot_infer']:
            j.setdefault(k, r[k])
        assert j.get('target') and j['rationale'] and j['evidence']
        assert bool(j['labels']) == (j['review_resolution'] == 'classified')
        assert j['review_resolution'] in RESOLUTIONS
        j['review_state'] = 'reviewed'
        j.setdefault('review_method', r['review_method'])
        j['clinical_review'] = False
        j['status'] = 'labeled' if j['labels'] else 'uncertain'
        j['annotation_method'] = j['review_method']
    assert set(r['labels']) == {l for j in r['judgments'] for l in j['labels']}, r['unit_id']
    return r


def apply_audit_corrections(decisions):
    """Apply reviewed child edits; never modify native records or source gold."""
    changes = []
    seen = set()
    byunit = defaultdict(list)
    compare = ['labels', 'target', 'rationale', 'evidence']
    for name in AUDIT_PATCH_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        for patch in rows(path):
            uid, jid = patch['unit_id'], patch['judgment_id']
            assert jid not in seen and uid in decisions, (uid, jid)
            seen.add(jid)
            unit = decisions[uid]
            child = next(j for j in unit['judgments'] if j['judgment_id'] == jid)
            assert all(child.get(k) == patch['before'].get(k) for k in compare), (uid, jid, 'stale correction')
            assert patch['after']['judgment_id'] == jid
            child.clear()
            child.update(patch['after'])
            child.pop('label', None)
            unit['review_source_file'] = name
            byunit[uid].append(jid)
            changes.append(dict(patch, correction_file=name))
    for uid, changed in byunit.items():
        unit = decisions[uid]
        unit['labels'] = sorted({l for j in unit['judgments'] for l in j['labels']})
        resolutions = {j['review_resolution'] for j in unit['judgments']}
        unit['review_resolution'] = ('classified' if unit['labels'] else
                                    'invalid_source' if resolutions == {'invalid_source'} else
                                    'outside_five_labels' if resolutions == {'outside_five_labels'} else 'insufficient_evidence')
        unit['rationale'] = '已按来源审核发现复核并修正具体判断；各目标的依据、未定类或原参考质量问题见 judgments。父标签仅为现有子判断标签的并集，不把一个目标成立扩大到整份回答。'
        unit['audit_correction_judgment_ids'] = changed
        normalize_review(unit)
    return changes


def main():
    manifest = list(rows(REVIEW / 'input_manifest.jsonl'))
    expected_order = [r['unit_id'] for r in manifest]
    expected = set(expected_order)
    assert len(expected) == len(manifest) == 28243
    assert [r['unit_id'] for r in rows(ROOT / '分析子集.jsonl')] == expected_order
    decisions = {}
    for name in OVERLAYS:
        for r in rows(ROOT / name):
            assert r['unit_id'] not in decisions, r['unit_id']
            r['review_source_file'] = name
            decisions[r['unit_id']] = normalize_review(r)
    patches = list(rows(ROOT / PATCH_FILE))
    assert len(patches) == len({r['unit_id'] for r in patches}) == 704
    for r in patches:
        assert r['unit_id'] in decisions and r['unit_id'].startswith('M12:')
        r['review_source_file'] = PATCH_FILE
        decisions[r['unit_id']] = normalize_review(r)
    assert set(decisions) == expected, (len(expected - set(decisions)), len(set(decisions) - expected))
    audit_changes = apply_audit_corrections(decisions)
    stats = json.loads((ROOT / 'reports/collection_counts.json').read_text())
    before = {k: stats[k] for k in ['normalized_units', 'analysis_units', 'labeled', 'uncertain']}
    counts, methods, labels, selected_labels = Counter(), Counter(), Counter(), Counter()
    byrid, review_counts, target_counts = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    bylabel = defaultdict(set)
    frozen, chosen = {}, []
    json_names = ['全部比较单元.jsonl', '已标注比较单元.jsonl', '待定比较单元.jsonl',
                  '分析子集.jsonl', '分析子集_已标注.jsonl']
    csv_fields = FIELDS + REVIEW_FIELDS + ['review_source_file']
    csv_names = ['逐题标注.csv', '分析子集_逐题标注.csv', '分析子集_未能定类.csv']
    child_fields = ['unit_id', 'resource_id', 'collection_kind', 'judgment_id', 'target', 'labels',
                    'rationale', 'evidence', 'cannot_infer', 'comparison_axis', 'review_resolution', 'review_method', 'clinical_review',
                    'scoring_eligible', 'gold_review_status', 'scoring_exclusion_reason']
    with ExitStack() as stack:
        files = {n: stack.enter_context((ROOT / (n + '.review_tmp')).open('w')) for n in json_names}
        writers = {}
        for name in csv_names + ['分析子集_具体判断.csv']:
            f = stack.enter_context((ROOT / (name + '.review_tmp')).open('w', encoding='utf-8-sig', newline=''))
            w = csv.DictWriter(f, fieldnames=child_fields if name == '分析子集_具体判断.csv' else csv_fields)
            w.writeheader()
            writers[name] = w
        for u in rows(ROOT / '全部比较单元.jsonl'):
            uid, rid = u['unit_id'], u['resource_id']
            assert u['analysis_selected'] == (uid in expected)
            if uid in decisions:
                r = decisions[uid]
                assert r.get('resource_id', rid) == rid
                u.setdefault('pre_review_annotation', {k: u.get(k) for k in HISTORY_FIELDS if k in u})
                # This allowlist prevents review files from changing source text,
                # native answers, pairing, sampling, or saved evaluation links.
                u.update({k: r[k] for k in ANNOTATION_FIELDS})
                u['review_source_file'] = r['review_source_file']
                u['review_details'] = {k: v for k, v in r.items() if k not in ANNOTATION_FIELDS | {'unit_id', 'resource_id', 'status', 'review_source_file'}}
                u['annotation_method'] = r['review_method']
                u['annotation_basis'] = '依据具体原文、原任务要求和逐项/分组语义审阅或字段验证；未使用模型结果，非临床专家验收。'
                for k in HISTORY_FIELDS[4:]:
                    u.pop(k, None)
                u['status'] = 'labeled' if u['labels'] else 'uncertain'
                u['reviewed_target_count'] = len(u['judgments'])
                u['classified_target_count'] = sum(bool(j['labels']) for j in u['judgments'])
                u['unclassified_target_count'] = u['reviewed_target_count'] - u['classified_target_count']
                u['review_coverage'] = ('all_targets_classified' if not u['unclassified_target_count'] else
                    'some_targets_classified' if u['classified_target_count'] else 'no_targets_classified')
                group = 'multimodal_metadata' if rid == 'M25' else 'text'
                for key in [rid, group, 'all']:
                    review_counts[key]['reviewed'] += 1
                    review_counts[key][u['review_resolution']] += 1
                    review_counts[key][u['review_coverage']] += 1
                    review_counts[key][u['review_method']] += 1
                    for l in u['labels']: review_counts[key][l] += 1
                for j in u['judgments']:
                    for key in [rid, group, 'all']:
                        target_counts[key][j['review_resolution']] += 1
                        target_counts[key]['reviewed_targets'] += 1
                    child = {**{k: u.get(k) for k in ['unit_id', 'resource_id', 'collection_kind']}, **j}
                    writers['分析子集_具体判断.csv'].writerow({k: dumps(child.get(k)) if isinstance(child.get(k), (list, dict)) else child.get(k, '') for k in child_fields})
                chosen.append(uid)
            else:
                u['review_state'] = 'outside_frozen_review_cohort'
            u['label_names'] = [LABELS[l] for l in u['labels']]
            frozen[uid] = u['labels']
            counts['normalized_units'] += 1
            counts[u['status']] += 1
            methods[u['annotation_method']] += 1
            byrid[rid]['units'] += 1
            byrid[rid][u['status']] += 1
            for l in u['labels']:
                labels[l] += 1; byrid[rid][l] += 1; bylabel[l].add(rid)
            if u['analysis_selected']:
                counts['analysis_units'] += 1
                counts['analysis_' + u['status']] += 1
                byrid[rid]['analysis_units'] += 1
                byrid[rid]['analysis_' + u['status']] += 1
                selected_labels.update(u['labels'])
            line = dumps(u) + '\n'
            files['全部比较单元.jsonl'].write(line)
            files['已标注比较单元.jsonl' if u['labels'] else '待定比较单元.jsonl'].write(line)
            if u['analysis_selected']:
                files['分析子集.jsonl'].write(line)
                if u['labels']: files['分析子集_已标注.jsonl'].write(line)
            row = {k: dumps(u.get(k)) if isinstance(u.get(k), (dict, list)) else u.get(k, '') for k in csv_fields}
            writers['逐题标注.csv'].writerow(row)
            if u['analysis_selected']:
                writers['分析子集_逐题标注.csv'].writerow(row)
                if not u['labels']: writers['分析子集_未能定类.csv'].writerow(row)
    assert chosen == expected_order and counts['normalized_units'] == before['normalized_units'] == 55991
    for name in json_names + csv_names + ['分析子集_具体判断.csv']:
        (ROOT / (name + '.review_tmp')).replace(ROOT / name)
    stats.update(counts)
    stats.update(label_counts=dict(labels), analysis_label_counts=dict(selected_labels),
                 annotation_methods=dict(methods), by_resource={k: dict(v) for k, v in byrid.items()},
                 sources_by_label={k: sorted(v) for k, v in bylabel.items()},
                 analysis_cohort_review_completed=True, all_items_individually_reviewed=False,
                 reviewed_analysis_units=28243, unreviewed_full_corpus_units=55991 - 28243)
    (ROOT / 'reports/collection_counts.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    freeze = dict(scope='Fixed 28,243 analysis units reviewed; nonselected full-corpus labels retain previous preliminary status.',
                  inference_calls=0, source='scripts/finalize_review.py', unit_labels=frozen,
                  review_cohort_size=28243, review_before_saved_prediction_reclassification=True)
    (ROOT / 'reports/annotation_freeze.json').write_text(dumps(freeze))
    report = dict(review_date='2026-09-08', full_corpus_records=55991, frozen_analysis_records=28243,
                  selection_ids_and_order_unchanged=True, all_selected_units_have_review_decision=True,
                  unit_counts={k: dict(v) for k, v in review_counts.items()},
                  target_counts={k: dict(v) for k, v in target_counts.items()},
                  overlay_files=OVERLAYS, correction_overlay=PATCH_FILE, corrected_units=len(patches), before_counts=before, new_model_calls=0, clinical_expert_validation=False,
                  audit_correction_files=[p for p in AUDIT_PATCH_FILES if (ROOT/p).exists()],
                  audit_corrected_judgments=len(audit_changes), audit_corrected_units=len({p['unit_id'] for p in audit_changes}),
                  note='审阅完成不等于全部可定类；父标签为子判断并集；分组语义/结构验证不等于逐病例临床重诊。')
    (ROOT / 'reports/classification_review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    catalog = json.loads((ROOT / '资源目录.json').read_text())
    for r in catalog:
        rid = r['resource_id']; r['full_counts'] = dict(byrid[rid]); r['analysis_review'] = dict(review_counts[rid])
    (ROOT / '资源目录.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2))
    with (ROOT / '资源目录.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['resource_id','benchmark','scope','full_counts','analysis_selection','analysis_review','primary_source'])
        w.writeheader()
        for r in catalog:w.writerow({k:dumps(r.get(k)) if isinstance(r.get(k),(list,dict)) else r.get(k,'') for k in w.fieldnames})
    table = '|来源|分析单元|有标签|证据不足|源问题|五类不适用|R1|R2|R3|R4|R5|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in catalog:
        c = review_counts[r['resource_id']]
        table += '|' + r['resource_id'] + ' ' + r['benchmark'] + '|' + '|'.join(str(c[k]) for k in ['reviewed','classified','insufficient_evidence','invalid_source','outside_five_labels',*LABELS]) + '|\n'
    (ROOT / 'reports/来源与标签计数.md').write_text('# 冻结分析子集的审阅计数\n\n' + table + '\n同一单元允许多标签；有标签表示至少一个具体目标已定类。M25仅为缺图元数据，单列，不计入文本题量。完整库未入选27,748条保留原初标，不与本轮审阅混称。\n')
    print(json.dumps({k:report[k] for k in ['full_corpus_records','frozen_analysis_records','unit_counts','target_counts']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
