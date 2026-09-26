"""Incremental, offline full-v5 C0-C5 accounting. Never imports an inference engine.

Default is reuse-only. --grade-missing scores only durable terminal responses,
once per backbone / whole response / actual evaluation mapping / scorer version.
Unsubmitted rows remain pending, never silently zero-scored or dropped.
"""
import argparse
import ast
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

WORK = Path('/home/data3/txy')
sys.path.insert(0, str(WORK))
from cf_moa.contracts import digest
from cf_moa.evaluation.native_scoring import load_native_scorer, score_proposal, source_lock

HERE = Path(__file__).resolve().parent
NEW = HERE.parent
REC = NEW.parent/'cf_moa_candidate_verify_20260924/recovery_gpu23'
DEV = WORK/'Documents/Codex/2026-09-21/cf_moa/cpu_preparation/development'
NAT = WORK/'Documents/Codex/2026-09-23/cf_moa_minimal_revision_20260923/natural_scope'
SCORE_KEYS = ('correct prediction semantic_prediction semantic_gold invalid_reason invalid '
              'format_invalid unmapped_diagnosis ambiguous raw_exact uncertainty option_f1 '
              'tp fp fn predicted_set_size gold_set_size native_available method_score '
              'semantic_result document_detection').split()
ARMS = ['original_C0', 'strong_B', 'candidate_only', 'candidate_with_rationales',
        'pool_old_plus_three', 'joint_selector']
TERMINAL = {'complete', 'completed', 'unavailable', 'failed', 'error'}


def rows(path):
    with Path(path).open() as stream:
        for line, text in enumerate(stream, 1):
            if text.strip():
                try:
                    yield json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'Incomplete/malformed JSONL at {path}:{line}; analyze completed chunks only') from exc


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def write(path, values):
    path = Path(path)
    tmp = path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False)+'\n')
    tmp.replace(path)


def scientific_score(row):
    result = {key: deepcopy(row[key]) for key in SCORE_KEYS if key in row}
    if 'correct' not in result:
        raise ValueError('Not a native score')
    result.setdefault('native_available', row['correct'] is not None)
    result.setdefault('method_score', 'scored' if result['native_available'] else 'not_scored')
    result.setdefault('semantic_result', 'native_answer_available' if result['native_available'] else 'unavailable')
    return result


def evaluation_binding(evaluation):
    # request_id is a local handle; every other frozen mapping field is bound,
    # including gold, role, target, resource, unit and auxiliary document maps.
    return {key: value for key, value in evaluation.items() if key != 'request_id'}


def item_binding(item):
    return {key: item[key] for key in ('question', 'options', 'fixed_evidence', 'answer_format')}


class ScoreCache:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS scores (cache_key TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS imports (name TEXT PRIMARY KEY, signature TEXT NOT NULL)')
        self.lock = source_lock()+[dict(path=str(WORK/'cf_moa/evaluation/native_scoring.py'),
                                      sha256=sha(WORK/'cf_moa/evaluation/native_scoring.py'))]
        self.scorer_id = digest(self.lock)
        self.new_calls = 0
        self.new_auxiliary_only = 0
        self.reuse = Counter()
        self.scorer = None

    def key(self, method, item, evaluation, native_hash):
        return digest(dict(method=method, whole_native_hash=native_hash,
                           native_item=item_binding(item), evaluation=evaluation_binding(evaluation),
                           scorer_id=self.scorer_id))

    def put(self, key, score, provenance):
        score = scientific_score(score)
        previous = self.db.execute('SELECT payload FROM scores WHERE cache_key=?', (key,)).fetchone()
        if previous:
            old = json.loads(previous[0])
            if old['score'] != score:
                raise ValueError('Conflicting native scores for same method/full response/evaluation: '+key)
            return
        self.db.execute('INSERT INTO scores VALUES (?, ?)',
                        (key, json.dumps(dict(score=score, provenance=provenance), ensure_ascii=False)))

    def import_once(self, name, paths, callback):
        signature = digest({str(path): sha(path) for path in paths})
        old = self.db.execute('SELECT signature FROM imports WHERE name=?', (name,)).fetchone()
        if old:
            if old[0] != signature:
                raise ValueError('Previously imported frozen score source changed: '+name)
            return
        callback()
        self.db.execute('INSERT INTO imports VALUES (?, ?)', (name, signature))
        self.db.commit()

    def supplement_auxiliary(self, item, evaluation, native, score):
        if item['answer_format'] != 'robustness_single' or 'document_detection' in score:
            return score
        # Execute the exact existing auxiliary block only; never re-run its
        # already saved native-answer score to obtain missing document fields.
        wrapper = WORK/'cf_moa/evaluation/native_scoring.py'
        func = next(n for n in ast.parse(wrapper.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == 'score_proposal')
        node = next(n for n in func.body if isinstance(n, ast.If)
                    and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Subscript)
                    and isinstance(n.test.left.value, ast.Name) and n.test.left.value.id == 'native_item')
        ns = dict(native_item=item, evaluation=evaluation, value=native, result={}, available=native is not None)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(wrapper), 'exec'), ns)
        self.new_auxiliary_only += 1
        return dict(score, document_detection=ns['result']['document_detection'])

    def obtain(self, method, item, evaluation, native, *, grade):
        key = self.key(method, item, evaluation, digest(native))
        old = self.db.execute('SELECT payload FROM scores WHERE cache_key=?', (key,)).fetchone()
        if old:
            value = json.loads(old[0])
            self.reuse[value['provenance']['kind']] += 1
            return value['score'], dict(kind='whole_response_cache_hit', cache_key=key,
                                       original=value['provenance'])
        if not grade:
            return None, dict(kind='awaiting_native_score', cache_key=key)
        if self.scorer is None:
            self.scorer = load_native_scorer()
        value = score_proposal(item, evaluation, dict(native_proposal=native,
            applicability='supported' if native is not None else 'failed'), scorer=self.scorer)
        proof = dict(kind='new_native_mapping_score', method=method,
                     request_id=evaluation['request_id'], record_id=evaluation['record_id'])
        self.put(key, value, proof)
        self.new_calls += 1
        # Durable per genuinely new score; crash recovery never needs to regrade it.
        self.db.commit()
        return scientific_score(value), dict(proof, cache_key=key)


def seed_existing(cache, full, items, evaluations, methods):
    """Bind earlier scores to their complete outputs, not just selected keys."""
    lookup = {e['record_id']: e for e in evaluations}
    by_request = defaultdict(list)
    for evaluation in evaluations:
        by_request[evaluation['request_id']].append(evaluation)
    # A passthrough or F-selected initial response may be exactly the complete
    # original answer. Reuse that original grade, never relabel a B grade C0.
    for method in methods:
        original_path = full/'offline'/f'{method.lower()}_C0_native_scored.jsonl'
        packet_path = full/'inference'/f'{method.lower()}.jsonl'
        def originals(method=method, original_path=original_path, packet_path=packet_path):
            originals = {r['record_id']: r for r in rows(original_path)}
            for packet in rows(packet_path):
                raw = packet.get('baseline_response')
                if not isinstance(raw, str):
                    continue
                try:
                    native = json.loads(raw)
                except json.JSONDecodeError:
                    continue  # No repaired or partial original answer is synthesized.
                if not isinstance(native, dict) or 'answer_choice' not in native:
                    continue
                rid = packet['request_id']
                assert packet['native_input'] == item_binding(items[rid])
                for e in by_request[rid]:
                    old = originals[e['record_id']]
                    assert all(old.get(k) == v for k, v in evaluation_binding(e).items())
                    score = cache.supplement_auxiliary(items[rid], e, native, old)
                    cache.put(cache.key(method, items[rid], e, digest(native)), score,
                              dict(kind='saved_original_complete_response_score', path=str(original_path),
                                   record_id=e['record_id'], complete_native_source=str(packet_path)))
        cache.import_once('original_whole_responses_'+method, [original_path, packet_path], originals)
    operation = full.parent/'operation_ablations'
    paths = [operation/'native_scored.jsonl', operation/'proposals.jsonl']
    paths += [full/'cache'/f'{m.lower()}_bases.jsonl' for m in methods]
    def operations():
        native = {}
        for method in methods:
            for row in rows(full/'cache'/f'{method.lower()}_bases.jsonl'):
                native[method, 'strong_B', row['request_id']] = row['result']['native_answer']
        for row in rows(operation/'proposals.jsonl'):
            native[row['method'], row['arm'], row['request_id']] = row['native_answer']
        for line, row in enumerate(rows(operation/'native_scored.jsonl'), 1):
            if row['method'] not in methods:
                continue
            e = lookup[row['record_id']]
            value = native[row['method'], row['arm'], row['request_id']]
            key = cache.key(row['method'], items[e['request_id']], e, digest(value))
            cache.put(key, row, dict(kind='saved_operation_ablation_score', path=str(paths[0]), line=line))
    cache.import_once('operation_scores_'+','.join(methods), paths, operations)
    r1 = WORK/'Documents/Codex/2026-09-16/r1_head_experiments'
    old_base = WORK/'Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5'
    r1paths = [r1/'candidate_replay_scored.jsonl', r1/'replay_candidate.py',
               old_base/'evaluation.jsonl', old_base/'items.jsonl']
    r1paths += [full/'cache'/f'{m.lower()}_bases.jsonl' for m in methods]
    def adopted_r1():
        # This is exactly the mapping selection in replay_candidate.py: the
        # last eligible non-reference R1 mapping for each item. Do not attach
        # one old item score to all other mappings for that item.
        old_e = {e['item_id']: e for e in rows(old_base/'evaluation.jsonl')
                 if 'R1' in e['evaluation_labels'] and e['role'] != 'reference'}
        old_i = {r['item_id']: r for r in rows(old_base/'items.jsonl')}
        old_scores = {(r['method'], r['item_id']): (line, r)
                      for line, r in enumerate(rows(r1/'candidate_replay_scored.jsonl'), 1)}
        api, canonical = load_native_scorer()  # Only api.parse is called here.
        for method in methods:
            for row in rows(full/'cache'/f'{method.lower()}_bases.jsonl'):
                base = row['result']
                if base['operations']['selected_component'] != 'legacy_R1':
                    continue
                item = items[row['request_id']]
                previous = old_scores.get((method, item['item_id']))
                if previous is None:
                    continue
                line, score = previous
                native = base['native_answer']
                if native is None or score.get('used_original') or 'prediction' not in score:
                    continue  # Preserve unavailable wrappers and sparse passthrough score identity.
                if native.get('answer_choice') != score['answer']:
                    continue
                original_e = old_e[item['item_id']]
                e = lookup[original_e['record_id']]
                assert evaluation_binding(e) == evaluation_binding(original_e)
                assert item_binding(item) == item_binding(old_i[item['item_id']])
                prediction, error, raw = api.parse(json.dumps(dict(answer=native['answer_choice']),
                    ensure_ascii=False), item, canonical)
                prediction = json.loads(json.dumps(prediction))
                if (prediction != score['prediction'] or error != score['invalid_reason']
                        or (raw == e['gold']) != score['raw_exact']):
                    raise ValueError('Saved R1 parser projection differs from current native interface: '+row['request_id'])
                cache.put(cache.key(method, item, e, digest(native)), score,
                    dict(kind='saved_adopted_R1_same_native_scoring_inputs', path=str(r1/'candidate_replay_scored.jsonl'),
                        line=line, original_record_id=e['record_id'],
                        equivalence='Same frozen item and evalmap; same complete answer value; unchanged parser prediction/error/raw_exact. New deterministic summary is not a diagnosis/multi grader input.',
                        parser_only=True, grader_called=False))
    cache.import_once('adopted_R1_parser_bound_'+','.join(methods), r1paths, adopted_r1)
    panel_dirs = {'historical121': DEV/'offline', 'natural52': NAT/'offline'}
    for label, directory in [('candidate_complete', REC/'analysis/complete_results'),
                             ('joint_selector', full.parent/'c5/analysis')]:
        paths = [directory/'native_scored.jsonl', directory/'per_input_status.jsonl']
        paths += [d/'evaluations.jsonl' for d in panel_dirs.values()]
        paths += [d/'items.jsonl' for d in panel_dirs.values()]
        def prior(directory=directory):
            old_e = {p: {e['record_id']: e for e in rows(d/'evaluations.jsonl')} for p, d in panel_dirs.items()}
            old_i = {p: {i['request_id']: i for i in rows(d/'items.jsonl')} for p, d in panel_dirs.items()}
            hashes = {(r['panel'], r['method'], r['arm'], r['request_id']): r['native_answer_ref']
                      for r in rows(directory/'per_input_status.jsonl')}
            for line, row in enumerate(rows(directory/'native_scored.jsonl'), 1):
                if row['method'] not in methods or row['record_id'] not in lookup:
                    continue
                e = lookup[row['record_id']]
                original_e = old_e[row['panel']][row['record_id']]
                original_i = old_i[row['panel']][row['request_id']]
                if evaluation_binding(e) != evaluation_binding(original_e):
                    continue  # Genuinely new mapping cannot borrow the old score.
                if item_binding(items[e['request_id']]) != item_binding(original_i):
                    continue
                h = hashes[row['panel'], row['method'], row['arm'], row['request_id']]
                # Earlier unavailable results use null refs, canonical JSON null here.
                h = h if h is not None else digest(None)
                cache.put(cache.key(row['method'], items[e['request_id']], e, h), row,
                          dict(kind='saved_complete_response_score', path=str(directory/'native_scored.jsonl'), line=line))
        cache.import_once(label+'_'+','.join(methods), paths, prior)

    delivery = WORK/'Documents/Codex/2026-09-18/r5_head/delivery'
    fpaths = [delivery/'outputs.jsonl', delivery/'scored.jsonl']
    fpaths += [full/'cache'/f'{m.lower()}_f_proposals.jsonl' for m in methods]
    def adopted_f():
        actual_outputs = list(rows(delivery/'outputs.jsonl'))
        old_scores = defaultdict(list)
        for line, row in enumerate(rows(delivery/'scored.jsonl'), 1):
            if row['method'] in methods and row['arm'] == 'combined_head':
                old_scores[row['method'], row['record_id']].append((line, row))
        by_request = defaultdict(list)
        for e in evaluations:
            by_request[e['request_id']].append(e)
        for method in methods:
            for row in rows(full/'cache'/f'{method.lower()}_f_proposals.jsonl'):
                proof = row['source_proof']
                if proof.get('output_source') != str(delivery/'outputs.jsonl'):
                    continue
                source = actual_outputs[proof['output_line']-1]
                assert source['method'] == method
                assert source['item_id'] == items[row['request_id']]['item_id']
                native = row['proposal']['native_proposal']
                assert json.loads(source['raw_response']) == native
                for e in by_request[row['request_id']]:
                    for line, prior_score in old_scores[method, e['record_id']]:
                        # Runtime-only prior metadata is irrelevant, but every
                        # field of the actual evaluation mapping must match.
                        if any(prior_score.get(k) != v for k, v in evaluation_binding(e).items()):
                            continue
                        score = cache.supplement_auxiliary(items[e['request_id']], e, native, prior_score)
                        cache.put(cache.key(method, items[e['request_id']], e, digest(native)), score,
                                  dict(kind='saved_adopted_F_delivery_score', path=str(delivery/'scored.jsonl'),
                                       line=line, whole_response_source_line=proof['output_line'],
                                       auxiliary_only_backfill='document_detection' not in prior_score and 'document_detection' in score))
    cache.import_once('adopted_F_delivery_'+','.join(methods), fpaths, adopted_f)


def read_outputs(full, methods, proposals, provenance):
    by_method = {method: {} for method in methods}
    paths = [full/'cache'/f'{m.lower()}_completed_union.jsonl' for m in methods] + proposals
    source_info = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        count = 0
        for line, row in enumerate(rows(path), 1):
            method = row['method']
            if method not in methods:
                continue
            rid, arm = row['request_id'], row['arm']
            if arm not in ARMS[1:] or (method, rid) not in provenance:
                raise ValueError(f'Unknown task at {path}:{line}')
            if row['input_hash'] != provenance[method, rid]['input_hash']:
                raise ValueError(f'Input identity mismatch at {path}:{line}')
            if row.get('task_id') != rid+':'+arm:
                raise ValueError(f'Task identity mismatch at {path}:{line}')
            status = row['status']
            if status not in TERMINAL:
                # Infrastructure/not-submitted is pending, not a clinical failure.
                if status not in {'pending', 'not_submitted', 'in_flight', 'stopped_on_error', 'blocked'}:
                    raise ValueError(f'Unknown status {status} at {path}:{line}')
                continue
            result = row.get('result') or {}
            if status in {'complete', 'completed'} and 'native_answer' not in result:
                raise ValueError(f'Completed output missing native_answer field at {path}:{line}')
            native = result.get('native_answer')
            compact = dict(status=status, native=native, whole_native_hash=digest(native),
                           source=dict(path=str(path), line=line), cost=row.get('cost', result.get('cost')),
                           verification_failure=(result.get('verification') or {}).get('failure_type'))
            old = by_method[method].get((rid, arm))
            if old and (old['whole_native_hash'], old['status']) != (compact['whole_native_hash'], compact['status']):
                raise ValueError(f'Conflicting terminal outputs for {method}/{rid}/{arm}: {old["source"]} vs {compact["source"]}')
            if old is None:
                by_method[method][rid, arm] = compact
            count += 1
        source_info.append(dict(path=str(path), size=path.stat().st_size, sha256=sha(path), terminal_rows=count))
    return by_method, source_info


def summarize(method, arm, scored, evaluations, pairs, items):
    byid = defaultdict(list)
    units = defaultdict(list)
    for e in evaluations:
        row = scored[e['record_id']]
        byid[e['request_id']].append(row)
        if e['role'] != 'reference':
            for category in ['ALL', *sorted(set(e['evaluation_labels']))]:
                units[e['unit_id'], category, e['resource_id']].append((e, row))
    unique = []
    for rid in items:
        values = byid[rid]
        done = all(r['analysis_status'] == 'scored' for r in values)
        status = 'scored' if done else ('pending' if any(r['analysis_status'] == 'pending' for r in values) else 'awaiting_native_score')
        correctness = (None if any(r.get('correct') is None for r in values) else all(r['correct'] for r in values)) if done else None
        unique.append(dict(method=method, arm=arm, request_id=rid, analysis_status=status,
                           native_mapping_count=len(values), correct=correctness,
                           unavailable=done and any(r.get('correct') is None for r in values),
                           answer_format=items[rid]['answer_format']))
    unit_rows = []
    for (unit, category, source), values in sorted(units.items()):
        done = all(r['analysis_status'] == 'scored' for e, r in values)
        families = {e['group_id'] for e, r in values}
        if len(families) != 1:
            raise ValueError('One native unit spans multiple family IDs')
        unit_rows.append(dict(method=method, arm=arm, unit_id=unit, category=category, source=source,
            family_id=next(iter(families)), native_records=len(values), complete=done,
            score=sum(r.get('correct') is True for e, r in values)/len(values) if done else None,
            pending_mappings=sum(r['analysis_status'] == 'pending' for e, r in values),
            awaiting_score_mappings=sum(r['analysis_status'] == 'awaiting_native_score' for e, r in values),
            unavailable_mappings=sum(r['analysis_status'] == 'scored' and r.get('correct') is None for e, r in values)))
    categories = []
    for category in ['ALL', 'R1', 'R2', 'R3', 'R4', 'R5']:
        values = [r for r in unit_rows if r['category'] == category]
        complete = [r for r in values if r['complete']]
        categories.append(dict(category=category, units=len(values), completed_units=len(complete),
            mean_native_unit_score=sum(r['score'] for r in values)/len(values) if values and len(complete) == len(values) else None,
            completed_unit_mean_descriptive=sum(r['score'] for r in complete)/len(complete) if complete else None,
            full_primary_score_available=bool(values) and len(complete) == len(values)))
    pair_rows = []
    for pair in pairs:
        a, b = scored[pair['left_record_id']], scored[pair['right_record_id']]
        done = a['analysis_status'] == b['analysis_status'] == 'scored'
        if done and (a['semantic_gold'] == b['semantic_gold']) != (pair['relation'] == 'maintain'):
            raise ValueError('Pair relation differs from native semantic gold: '+pair['pair_id'])
        same = (a.get('semantic_prediction') == b.get('semantic_prediction') and not a.get('invalid') and not b.get('invalid')) if done else None
        pair_rows.append(dict(method=method, arm=arm, pair_id=pair['pair_id'], family_id=pair['family_id'],
            relation=pair['relation'], complete=done,
            both_correct=(a['correct'] is True and b['correct'] is True) if done else None,
            unavailable_endpoints=int(a['correct'] is None)+int(b['correct'] is None) if done else None,
            valid_relation=(same if pair['relation'] == 'maintain' else not same and not a['invalid'] and not b['invalid']) if done else None))
    pair_summary = []
    for relation in ['maintain', 'respond']:
        values = [r for r in pair_rows if r['relation'] == relation]
        n = sum(r['complete'] for r in values)
        correct = sum(r['both_correct'] is True for r in values)
        pair_summary.append(dict(relation=relation, pairs=len(values), completed_pairs=n, both_correct=correct,
            full_both_correct_rate=correct/len(values) if values and n == len(values) else None))
    auxiliary = [r for r in scored.values() if 'document_detection' in r]
    planned_aux = sum(items[e['request_id']]['answer_format'] == 'robustness_single' for e in evaluations)
    report = dict(method=method, arm=arm, planned_inputs=len(items), planned_native_mappings=len(evaluations),
        scored_native_mappings=sum(r['analysis_status'] == 'scored' for r in scored.values()),
        pending_native_mappings=sum(r['analysis_status'] == 'pending' for r in scored.values()),
        awaiting_native_scores=sum(r['analysis_status'] == 'awaiting_native_score' for r in scored.values()),
        input_status_counts=dict(Counter(r['analysis_status'] for r in unique)),
        correct_inputs=sum(r['correct'] is True for r in unique),
        incorrect_answer_inputs=sum(r['analysis_status'] == 'scored' and r['correct'] is False for r in unique),
        unavailable_inputs=sum(r['unavailable'] for r in unique), native_categories=categories,
        pairs=pair_summary, auxiliary=dict(planned_mappings=planned_aux, scored_mappings=len(auxiliary),
            valid=sum(r['document_detection']['valid'] is True for r in auxiliary),
            exact=sum(r['document_detection']['exact'] is True for r in auxiliary),
            full_exact_rate=sum(r['document_detection']['exact'] is True for r in auxiliary)/planned_aux if len(auxiliary) == planned_aux and planned_aux else None))
    report['status'] = 'complete' if all(r['analysis_status'] == 'scored' for r in unique) else 'partial'
    report['accuracy_full_denominator'] = report['correct_inputs']/len(items) if report['status'] == 'complete' else None
    return report, unique, unit_rows, pair_rows


def comparisons(all_unique, all_units, all_pairs):
    atoms, families, reports = [], [], []
    for method in sorted({r['method'] for r in all_unique}):
        baseline = {r['request_id']: r for r in all_unique if r['method'] == method and r['arm'] == 'strong_B'}
        base_units = {r['unit_id']: r for r in all_units if r['method'] == method and r['arm'] == 'strong_B' and r['category'] == 'ALL'}
        base_pairs = {r['pair_id']: r for r in all_pairs if r['method'] == method and r['arm'] == 'strong_B'}
        for arm in ARMS:
            if arm == 'strong_B':
                continue
            values = [r for r in all_unique if r['method'] == method and r['arm'] == arm]
            done = [r for r in values if r['analysis_status'] == baseline[r['request_id']]['analysis_status'] == 'scored']
            repairs = sum(baseline[r['request_id']]['correct'] is False and r['correct'] is True for r in done)
            harms = sum(baseline[r['request_id']]['correct'] is True and r['correct'] is False for r in done)
            reports.append(dict(method=method, candidate=arm, planned_inputs=len(values), jointly_scored_inputs=len(done),
                repairs=repairs, harms=harms,
                unavailable_to_correct=sum(baseline[r['request_id']]['unavailable'] and r['correct'] is True for r in done),
                correct_to_unavailable=sum(baseline[r['request_id']]['correct'] is True and r['unavailable'] for r in done),
                complete=len(done) == len(values),
                completed_subset_only=len(done) != len(values)))
            current = []
            for row in all_units:
                if row['method'] != method or row['arm'] != arm or row['category'] != 'ALL':
                    continue
                base = base_units[row['unit_id']]
                complete = row['complete'] and base['complete']
                current.append(dict(panel='full_v5', model=method, metric='native_ALL', candidate=arm,
                    family_id=row['family_id'], atom_id=row['unit_id'], baseline_score=base['score'] if complete else None,
                    candidate_score=row['score'] if complete else None, weight=1, complete=complete))
            for row in all_pairs:
                if row['method'] != method or row['arm'] != arm:
                    continue
                base = base_pairs[row['pair_id']]
                complete = row['complete'] and base['complete']
                current.append(dict(panel='full_v5', model=method, metric='pair_'+row['relation'], candidate=arm,
                    family_id=row['family_id'], atom_id=row['pair_id'], baseline_score=int(base['both_correct']) if complete else None,
                    candidate_score=int(row['both_correct']) if complete else None, weight=1, complete=complete))
            atoms.extend(current)
            grouped = defaultdict(list)
            for row in current:
                grouped[row['metric'], row['family_id']].append(row)
            for (metric, family), group in sorted(grouped.items()):
                complete = all(r['complete'] for r in group)
                families.append(dict(model=method, candidate=arm, metric=metric, family_id=family,
                    planned_atoms=len(group), completed_atoms=sum(r['complete'] for r in group), complete=complete,
                    paired_delta=sum(r['candidate_score']-r['baseline_score'] for r in group)/len(group) if complete else None))
    return reports, atoms, families


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-root', type=Path, default=HERE)
    parser.add_argument('--method', action='append', choices=['M4', 'M5'])
    parser.add_argument('--proposals', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--grade-missing', action='store_true')
    args = parser.parse_args()
    started = time.monotonic()
    executing_script_sha256 = sha(Path(__file__))
    methods = args.method or ['M4', 'M5']
    if len(set(methods)) != len(methods):
        raise ValueError('Repeated method')
    full, out = args.full_root.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    previous_receipt = out/'receipt.json'
    prior_sources = []
    if previous_receipt.exists():
        previous = json.loads(previous_receipt.read_text())
        if previous['methods'] != methods:
            raise ValueError('Keep the same method scope for an incremental output directory')
        automatic = {str(full/'cache'/f'{m.lower()}_completed_union.jsonl') for m in methods}
        prior_sources = [Path(r['path']) for r in previous['input_sources'] if r['path'] not in automatic]
    # Each completed chunk may be passed once. The next invocation retains all
    # previously registered chunk paths and verifies the entire terminal union.
    proposals = list(dict.fromkeys([p.resolve() for p in prior_sources+args.proposals]))
    items = {r['request_id']: r for r in rows(full/'offline/items.jsonl')}
    evaluations = list(rows(full/'offline/evaluations.jsonl'))
    pairs = list(rows(full/'offline/pairs.jsonl'))
    provenance = {(r['model'], r['request_id']): r for r in rows(full/'offline/provenance.jsonl')}
    assert len(items) == 13905 and len(evaluations) == 15616
    assert len({e['record_id'] for e in evaluations}) == 15616
    assert len({e['unit_id'] for e in evaluations if e['role'] != 'reference'}) == 6104
    assert len({p['pair_id'] for p in pairs}) == len(pairs)
    cache = ScoreCache(out/'native_score_cache.sqlite3')
    seed_existing(cache, full, items, evaluations, methods)
    observed, sources = read_outputs(full, methods, proposals, provenance)
    all_native, all_unique, all_units, all_pairs, reports = [], [], [], [], []
    for method in methods:
        original = {r['record_id']: r for r in rows(full/'offline'/f'{method.lower()}_C0_native_scored.jsonl')}
        assert set(original) == {e['record_id'] for e in evaluations}
        for arm in ARMS:
            scored = {}
            for e in evaluations:
                rid = e['request_id']
                row = dict(method=method, arm=arm, request_id=rid, record_id=e['record_id'])
                if arm == 'original_C0':
                    row.update(scientific_score(original[e['record_id']]), analysis_status='scored',
                        score_provenance=dict(kind='unchanged_formal_C0_score', path=str(full/'offline'/f'{method.lower()}_C0_native_scored.jsonl')))
                else:
                    result = observed[method].get((rid, arm))
                    if result is None:
                        row.update(analysis_status='pending', run_status='not_submitted_or_no_durable_terminal_result')
                    else:
                        value, proof = cache.obtain(method, items[rid], e, result['native'], grade=args.grade_missing)
                        row.update(analysis_status='scored' if value is not None else 'awaiting_native_score',
                            run_status=result['status'], native_answer_ref=result['whole_native_hash'],
                            output_source=result['source'], score_provenance=proof)
                        if value is not None:
                            row.update(value)
                scored[e['record_id']] = row
            report, unique, units, pair_rows = summarize(method, arm, scored, evaluations, pairs, items)
            all_native.extend(scored.values()); all_unique.extend(unique)
            all_units.extend(units); all_pairs.extend(pair_rows); reports.append(report)
    effects, atoms, families = comparisons(all_unique, all_units, all_pairs)
    write(out/'native_scored.jsonl', all_native)
    write(out/'per_input_status.jsonl', all_unique)
    write(out/'native_units.jsonl', all_units)
    write(out/'pairs.jsonl', all_pairs)
    write(out/'paired_atoms_with_pending.jsonl', atoms)
    write(out/'family_effects.jsonl', families)
    # Do not feed an outcome-selected complete subset to a full-panel bootstrap.
    complete = all(r['complete'] for r in atoms)
    if complete:
        write(out/'paired_atoms.jsonl', atoms)
    elif (out/'paired_atoms.jsonl').exists():
        raise ValueError('Previously complete analysis became partial; refusing stale paired_atoms publication')
    dump(out/'quality_summary.json', dict(reports=reports, comparisons=effects,
        complete=all(r['status'] == 'complete' for r in reports), independent=False,
        status='complete' if all(r['status'] == 'complete' for r in reports) else 'partial',
        denominator_policy='Pending is not failed. Native unavailable terminal output contributes zero success and stays not_scored. ALL excludes reference and never sums overlapping R categories.',
        bootstrap_ready=complete, development_selection_bias=True))
    receipt = dict(timestamp=datetime.now(timezone.utc).isoformat(), status='complete' if complete else 'partial',
        methods=methods, inference_calls=0, new_native_grader_calls=cache.new_calls,
        new_auxiliary_only_backfills=cache.new_auxiliary_only,
        reused_native_score_cache_hits=dict(cache.reuse), new_scores_enabled=args.grade_missing,
        planned_inputs_per_method=13905, planned_native_mappings_per_method=15616, planned_ALL_units=6104,
        mapping_rows_with_pending=len(all_native), input_rows_with_pending=len(all_unique),
        input_sources=sources, scorer_sources=cache.lock, script_sha256=executing_script_sha256,
        elapsed_seconds=time.monotonic()-started, cache_scope='backbone + whole native response + complete eval mapping except local request handle + full native item + unchanged scorer',
        bootstrap_policy='Only produce full paired_atoms when every planned atom is complete; no complete-case subset is presented as full-v5.')
    dump(out/'receipt.json', receipt)
    with (out/'invocations.jsonl').open('a') as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False)+'\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'new_native_grader_calls', 'reused_native_score_cache_hits', 'elapsed_seconds')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
