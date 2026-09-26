"""Copy existing C0 auxiliary scores only after exact input/whole-answer binding.

No scorer or inference modules are imported. Existing native scores and summaries
are never changed. Missing or nonidentical evidence stays unknown in 24 rows.
"""
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW = HERE.parent.parent
NAT = NEW.parents[1]/'2026-09-23/cf_moa_minimal_revision_20260923/natural_scope'
FULL = NEW/'full_v5'
SOURCES = {}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, allow_nan=False,
        separators=(',', ':')).encode()).hexdigest()


def source(path):
    path = Path(path)
    key = str(path)
    if key not in SOURCES:
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                h.update(chunk)
        SOURCES[key] = h.hexdigest()
    return dict(path=key, sha256=SOURCES[key])


def rows(path):
    source(path)
    with Path(path).open() as stream:
        for line, text in enumerate(stream, 1):
            if text.strip():
                yield line, json.loads(text)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    index_path = HERE.parent/'existing48_reuse_index.jsonl'
    items_path, evaluation_path = NAT/'offline/items.jsonl', NAT/'offline/evaluations.jsonl'
    items = {r['request_id']: r for _, r in rows(items_path)}
    evaluation = {r['request_id']: r for _, r in rows(evaluation_path)}
    wanted = {rid for rid, item in items.items() if item['answer_format'] == 'robustness_single'}
    check(len(wanted) == 12, 'Changed natural52 robustness denominator')
    index = {(r['method'], r['request_id']): (line, r) for line, r in rows(index_path)}
    auxiliary_receipt_path = NEW/'scope/offline_score_pair_reuse_receipt.json'
    source(auxiliary_receipt_path)
    auxiliary_sources = {r['method']: r['auxiliary_path']
                         for r in json.loads(auxiliary_receipt_path.read_text())['sources']}
    provenance_path = FULL/'offline/provenance.jsonl'
    full_keys = {(method, index[method, rid][1]['full_v5_request_id'])
                 for method in ('M4', 'M5') for rid in wanted}
    provenance = {(r['model'], r['request_id']): (line, r) for line, r in rows(provenance_path)
                  if (r['model'], r['request_id']) in full_keys}
    bound = []
    for method in ('M4', 'M5'):
        lower = method.lower()
        natural_path, full_path = NAT/f'inference/{lower}_inputs.jsonl', FULL/f'inference/{lower}.jsonl'
        score_path = FULL/f'offline/{lower}_C0_native_scored.jsonl'
        full_ids = {index[method, rid][1]['full_v5_request_id'] for rid in wanted}
        natural = {r['request_id']: (line, r) for line, r in rows(natural_path) if r['request_id'] in wanted}
        packets = {r['request_id']: (line, r) for line, r in rows(full_path) if r['request_id'] in full_ids}
        scores = {(r['request_id'], r['record_id']): (line, r) for line, r in rows(score_path) if r['request_id'] in full_ids}
        record_ids = {evaluation[rid]['record_id'] for rid in wanted}
        auxiliary_path = auxiliary_sources[method]
        auxiliary = {r['record_id']: (line, r) for line, r in rows(auxiliary_path)
                     if r['method'] == method and r['record_id'] in record_ids}
        # Original prediction/score locations come from the existing provenance,
        # never a guessed path or a search by gold/correctness.
        requested = defaultdict(set)
        for full_id in full_ids:
            _, p = provenance[method, full_id]
            requested[p['original_prediction_path']].add(p['original_prediction_line'])
            requested[p['original_native_score_path']].update(p['original_native_score_lines'])
        originals = {path: {line: r for line, r in rows(path) if line in lines}
                     for path, lines in requested.items()}
        for rid in sorted(wanted):
            row = dict(panel='natural52', method=method, control='C0', request_id=rid,
                       status='unknown', document_detection=None, new_model_calls=0,
                       new_native_grader_calls=0, new_auxiliary_score_calls=0)
            try:
                index_line, prior = index[method, rid]
                full_id = prior['full_v5_request_id']
                natural_line, packet = natural[rid]
                full_line, full_packet = packets[full_id]
                provenance_line, p = provenance[method, full_id]
                score_line, score = scores[full_id, evaluation[rid]['record_id']]
                check(prior['original_response_source']['sha256'] == source(natural_path)['sha256'], 'Changed natural source')
                check(prior['existing_C0_score_source']['sha256'] == source(score_path)['sha256'], 'Changed saved C0 score source')
                check(packet['native_input'] == full_packet['native_input'], 'Native input mismatch')
                check(packet['original_context'] == full_packet['original_context'], 'Allowed context mismatch')
                check(packet['answer_schema'] == full_packet['answer_schema'], 'Native schema mismatch')
                raw = packet['baseline_response']
                prediction = originals[p['original_prediction_path']][p['original_prediction_line']]
                check(isinstance(raw, str) and raw == full_packet['baseline_response'] == prediction['raw_response'], 'Whole original response mismatch')
                check(digest(raw) == prior['raw_response_hash'] == p['original_response_hash'], 'Raw response hash mismatch')
                native = json.loads(raw)
                check(isinstance(native, dict) and 'answer_choice' in native, 'Original response is not a complete native object')
                # The natural52 selector added a cohort/exposure label; it is
                # not an input to the auxiliary scorer. All actual evaluation
                # fields, including every document map and gold field, match.
                check(all(score.get(k) == value for k, value in evaluation[rid].items()
                          if k not in {'request_id', 'cohort'}), 'Evaluation/document-map mismatch')
                saved = [(line, originals[p['original_native_score_path']][line]) for line in p['original_native_score_lines']]
                saved = [(line, r) for line, r in saved if r['record_id'] == score['record_id'] and r['method'] == method]
                check(len(saved) == 1, 'Original auxiliary score identity is not unique')
                original_line, original_score = saved[0]
                auxiliary_line, auxiliary_row = auxiliary[score['record_id']]
                original_auxiliary = {k: auxiliary_row[k] for k in
                    ('valid', 'exact', 'tp', 'fp', 'fn', 'correction_semantic_score')}
                check('document_detection' in score and score['document_detection'] == original_auxiliary, 'Saved auxiliary field absent or changed')
                row.update(status='exact_saved_auxiliary_reuse', full_v5_request_id=full_id,
                    record_id=score['record_id'], native_input_hash=digest(packet['native_input']),
                    natural_packet_hash=digest(packet), full_v5_packet_hash=digest(full_packet),
                    full_v5_frozen_input_hash=p['input_hash'],
                    original_context_hash=digest(packet['original_context']), native_schema_hash=digest(packet['answer_schema']),
                    raw_response_hash=digest(raw), native_whole_hash=digest(native),
                    document_detection=score['document_detection'],
                    non_scoring_metadata=dict(cohort_natural=evaluation[rid].get('cohort'),
                        cohort_original=score.get('cohort'), ignored_for_score_identity=['request_id', 'cohort']),
                    identity_checks=dict(native_input_equal=True, original_context_equal=True, native_schema_equal=True,
                        raw_response_equal=True, full_native_object_parsed=True, evaluation_scoring_fields_equal=True, original_auxiliary_equal=True),
                    sources=dict(reuse_index=dict(**source(index_path), line=index_line),
                        natural_packet=dict(**source(natural_path), line=natural_line),
                        full_packet=dict(**source(full_path), line=full_line),
                        saved_C0_score=dict(**source(score_path), line=score_line),
                        original_prediction=dict(**source(p['original_prediction_path']), line=p['original_prediction_line']),
                        original_native_score=dict(**source(p['original_native_score_path']), line=original_line),
                        original_auxiliary_score=dict(**source(auxiliary_path), line=auxiliary_line),
                        auxiliary_source_index=source(auxiliary_receipt_path),
                        provenance=dict(**source(provenance_path), line=provenance_line)))
            except (KeyError, ValueError, TypeError) as exc:
                row['unknown_reason'] = f'{type(exc).__name__}: {exc}'
            bound.append(row)
    output = HERE/'bindings.jsonl'
    output.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in bound))
    receipt = dict(at=datetime.now().astimezone().isoformat(),
        purpose='Exact reuse of saved C0 document_detection; no main or auxiliary scoring',
        expected_rows=24, actual_rows=len(bound),
        per_method={method: dict(denominator=12,
            statuses=dict(Counter(r['status'] for r in bound if r['method'] == method))) for method in ('M4','M5')},
        new_model_calls=0, new_native_grader_calls=0, new_auxiliary_score_calls=0,
        sources=SOURCES, script=source(Path(__file__)), output=source(output),
        unknown_policy='Keep every planned row; missing or nonidentical evidence is null, never zero or rescored.',
        scope='Exposed natural52 only. Original48 main scores, summaries, full-v5 results and confirmation materials are unchanged.')
    (HERE/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(receipt['per_method'], ensure_ascii=False))


if __name__ == '__main__':
    main()
