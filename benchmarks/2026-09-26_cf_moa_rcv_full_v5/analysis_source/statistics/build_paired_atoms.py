#!/usr/bin/env python3
"""Join already scored native units and qualified pairs; no scorer/model imports."""
import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ARMS = ('candidate_only', 'candidate_with_rationales', 'pool_old_plus_three')
CONTROL = dict(zip(ARMS, ('C2', 'C3', 'C4')))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write(path, data):
    Path(path).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in data))


def mean_success(records):
    # Preserve the existing native ALL end-to-end denominator. None remains a
    # separately counted unavailable response, never an asserted wrong answer.
    return Fraction(sum(r['correct'] is True for r in records), len(records))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--delivery-index', type=Path, required=True)
    p.add_argument('--published-data', type=Path, required=True)
    p.add_argument('--plan-bundle', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    used = {str(args.delivery_index.resolve()): sha(args.delivery_index)}
    index = json.loads(args.delivery_index.read_text())
    indexed = {e['path']: e['sha256'] for e in index['files']}

    def verified_read(path, expected=None, jsonl=False):
        path = Path(path)
        checksum = sha(path)
        if expected is not None and expected != checksum:
            raise ValueError(f'Changed input: {path}')
        used[str(path.resolve())] = checksum
        return rows(path) if jsonl else json.loads(path.read_text())

    def find(suffix):
        matches = [Path(path) for path in indexed if path.endswith(suffix)]
        if len(matches) != 1:
            raise ValueError(f'Expected unique indexed source: {suffix}: {matches}')
        return matches[0]

    def indexed_read(suffix, jsonl=False):
        path = find(suffix)
        return verified_read(path, indexed[str(path)], jsonl)

    receipt = indexed_read('/recovery_gpu23/analysis/complete_results/receipt.json')
    native = indexed_read('/recovery_gpu23/analysis/complete_results/native_scored.jsonl', True)
    unique = indexed_read('/recovery_gpu23/analysis/complete_results/per_input_status.jsonl', True)
    summary = indexed_read('/recovery_gpu23/analysis/complete_results/summary.json')
    public_summary = verified_read(args.published_data / 'quality_summary.json')
    public_native = verified_read(args.published_data / 'native_scoring_metadata.jsonl', jsonl=True)
    identity = lambda r: (r['panel'], r['method'], r['arm'], r['record_id'])
    native_by = {identity(r): r for r in native}
    assert len(native_by) == len(native) == len(public_native)
    for r in public_native:
        old = native_by[identity(r)]
        for key in ('request_id', 'correct', 'native_available', 'method_score', 'invalid'):
            assert r.get(key) == old.get(key), (identity(r), key)
    reports = {(r['panel'], r['method'], r['arm']): r for r in summary['reports']}
    pub_reports = {(r['panel'], r['method'], r['arm']): r for r in public_summary['reports']}
    for key, report in reports.items():
        assert report['native_unit_metrics'] == pub_reports[key]['native_unit_metrics']
        assert report['pairs'] == pub_reports[key]['pairs']

    uid = {(r['panel'], r['method'], r['arm'], r['request_id']): r for r in unique}
    assert len(uid) == len(unique)
    panels = sorted({r['panel'] for r in unique})
    eval_sources = [(path, checksum) for path, checksum in receipt['source_hashes'].items()
                    if path.endswith('/evaluations.jsonl')]
    pair_sources = [(path, checksum) for path, checksum in receipt['source_hashes'].items()
                    if path.endswith('/pairs.jsonl')]
    eval_sets = [(path, verified_read(path, checksum, True)) for path, checksum in eval_sources]
    pair_sets = [(path, verified_read(path, checksum, True)) for path, checksum in pair_sources]
    atoms, provenance, checks, source_bindings = [], [], [], {}
    exact_scores = {}
    for panel in panels:
        expected_ids = {r['request_id'] for r in unique if r['panel'] == panel}
        matches = [(path, rs) for path, rs in eval_sets if {r['request_id'] for r in rs} == expected_ids]
        assert len(matches) == 1, (panel, 'evaluation source matching membership')
        eval_path, evaluations = matches[0]
        matches = [(path, rs) for path, rs in pair_sets
                   if {r[side] for r in rs for side in ('left', 'right')} <= expected_ids]
        assert len(matches) == 1, (panel, 'pair source matching membership')
        pair_path, pairs = matches[0]
        source_bindings[panel] = dict(evaluations=eval_path, pairs=pair_path,
                                     unique_inputs=len(expected_ids), native_mappings=len(evaluations))
        eval_by = {e['record_id']: e for e in evaluations}
        assert len(eval_by) == len(evaluations)
        unit_members = defaultdict(list)
        for e in evaluations:
            if e['role'] != 'reference':
                unit_members[e['unit_id'], e['resource_id']].append(e['record_id'])
        # Unit IDs are unambiguous here; category is NOT part of an ALL atom ID.
        assert len({u for u, s in unit_members}) == len(unit_members)
        for model in ('M4', 'M5'):
            unit_scores, pair_scores = {}, {}
            for arm in ('F', *ARMS):
                mapped = {r['record_id']: r for r in native
                          if (r['panel'], r['method'], r['arm']) == (panel, model, arm)}
                assert set(mapped) == set(eval_by), (panel, model, arm, 'missing mapping')
                assert {r['request_id'] for r in unique if
                        (r['panel'], r['method'], r['arm']) == (panel, model, arm)} == expected_ids
                family_map = {rid: uid[panel, model, arm, rid]['family_id'] for rid in expected_ids}
                for e in evaluations:
                    assert family_map[e['request_id']] == e['group_id']
                saved_units = {(r['unit_id'], r['source']): r for r in
                               reports[panel, model, arm]['native_unit_metrics']['units']
                               if r['category'] == 'ALL'}
                assert set(saved_units) == set(unit_members)
                unit_scores[arm] = {}
                for key, members in sorted(unit_members.items()):
                    families = {family_map[eval_by[r]['request_id']] for r in members}
                    assert len(families) == 1, (key, families)
                    records = [mapped[r] for r in members]
                    score = mean_success(records)
                    saved = saved_units[key]
                    assert abs(float(score) - saved['score']) < 1e-12
                    assert len(members) == saved['native_records']
                    assert sum(r['correct'] is None for r in records) == saved['unavailable']
                    unit_scores[arm][key] = dict(score=score, family_id=next(iter(families)),
                        unavailable=sum(r['correct'] is None for r in records),
                        incorrect=sum(r['correct'] is False for r in records))
                pair_scores[arm] = {}
                saved_pairs = {r['pair_id']: r for r in reports[panel, model, arm]['pairs']['records']}
                assert {r['pair_id'] for r in pairs} == set(saved_pairs)
                for pair in pairs:
                    left, right = (mapped[pair[side + '_record_id']] for side in ('left', 'right'))
                    assert family_map[pair['left']] == family_map[pair['right']] == pair['family_id']
                    score = int(left['correct'] is True and right['correct'] is True)
                    saved = saved_pairs[pair['pair_id']]
                    assert score == int(saved['both_correct'])
                    assert pair['relation'] == saved['relation']
                    assert pair['family_id'] == saved['family_id']
                    pair_scores[arm][pair['pair_id']] = dict(score=score,
                        unavailable=int(left['correct'] is None) + int(right['correct'] is None))
                exact = sum(v['score'] for v in unit_scores[arm].values()) / len(unit_members)
                exact_scores[panel, model, arm] = exact
                saved_mean = next(r['mean_native_unit_score'] for r in
                                 reports[panel, model, arm]['native_unit_metrics']['categories']
                                 if r['category'] == 'ALL')
                assert abs(float(exact) - saved_mean) < 1e-12
            for arm in ARMS:
                for (unit_id, source), members in sorted(unit_members.items()):
                    b, c = (unit_scores[a][unit_id, source] for a in ('F', arm))
                    atoms.append(dict(panel=panel, model=model, metric='native_ALL',
                        candidate=arm, family_id=b['family_id'], atom_id=unit_id,
                        baseline_score=float(b['score']), candidate_score=float(c['score']), weight=1,
                        baseline_unavailable_native_records=b['unavailable'],
                        candidate_unavailable_native_records=c['unavailable'], native_records=len(members)))
                    provenance.append(dict(panel=panel, model=model, candidate=arm, atom_id=unit_id,
                        metric='native_ALL', family_id=b['family_id'], source=source,
                        baseline_exact=str(b['score']), candidate_exact=str(c['score']),
                        record_ids=members, request_ids=sorted({eval_by[r]['request_id'] for r in members})))
                for pair in pairs:
                    b, c = (pair_scores[a][pair['pair_id']] for a in ('F', arm))
                    atoms.append(dict(panel=panel, model=model, metric=pair['relation'] + '_both_correct',
                        candidate=arm, family_id=pair['family_id'], atom_id=pair['pair_id'],
                        baseline_score=b['score'], candidate_score=c['score'], weight=1,
                        baseline_unavailable_endpoints=b['unavailable'], candidate_unavailable_endpoints=c['unavailable']))
                    provenance.append(dict(panel=panel, model=model, candidate=arm,
                        atom_id=pair['pair_id'], metric=pair['relation'] + '_both_correct',
                        family_id=pair['family_id'], record_ids=[pair['left_record_id'], pair['right_record_id']],
                        request_ids=[pair['left'], pair['right']]))
                delta = exact_scores[panel, model, arm] - exact_scores[panel, model, 'F']
                checks.append(dict(panel=panel, model=model, candidate=arm,
                    baseline_exact=str(exact_scores[panel, model, 'F']), candidate_exact=str(exact_scores[panel, model, arm]),
                    exact_delta=str(delta), delta_percentage_points=float(100 * delta),
                    native_units=len(unit_members), families=len({v['family_id'] for v in unit_scores['F'].values()}),
                    unique_input_repairs=reports[panel, model, arm]['repairs'],
                    unique_input_harms=reports[panel, model, arm]['harms'],
                    complete_input_denominator=len(expected_ids)))
    assert exact_scores['natural52', 'M5', 'candidate_with_rationales'] - exact_scores['natural52', 'M5', 'F'] == Fraction(-1, 90)
    atoms.sort(key=lambda r: tuple(str(r[k]) for k in ('panel', 'model', 'metric', 'candidate', 'family_id', 'atom_id')))
    write(args.output / 'paired_atoms.jsonl', atoms)
    write(args.output / 'atom_provenance.jsonl', provenance)
    dump(args.output / 'point_estimate_crosscheck.json', checks)

    script = args.plan_bundle / 'paired_cluster_effects.py'
    used[str(script.resolve())] = sha(script)
    command = [sys.executable, str(script), '--input', str(args.output / 'paired_atoms.jsonl'),
               '--output', str(args.output / 'paired_effects.json'), '--resamples', '5000', '--seed', '240924']
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    (args.output / 'bootstrap.stdout').write_text(result.stdout)
    effects = json.loads((args.output / 'paired_effects.json').read_text())
    effect_by = {tuple(r[k] for k in ('panel', 'model', 'metric', 'candidate')): r for r in effects['reports']}
    groups = defaultdict(list)
    for row in atoms:
        groups[tuple(row[k] for k in ('panel', 'model', 'metric', 'candidate'))].append(row)
    family_rows = []
    for key, group in sorted(groups.items()):
        total_weight = sum(r['weight'] for r in group)
        sb = sum(r['baseline_score'] * r['weight'] for r in group)
        sc = sum(r['candidate_score'] * r['weight'] for r in group)
        delta = (sc - sb) / total_weight
        by_family = defaultdict(list)
        for row in group:
            by_family[row['family_id']].append(row)
        for family, members in sorted(by_family.items()):
            weight = sum(r['weight'] for r in members)
            b = sum(r['baseline_score'] * r['weight'] for r in members)
            c = sum(r['candidate_score'] * r['weight'] for r in members)
            remaining = total_weight - weight
            leave_out = ((sc - c) - (sb - b)) / remaining if remaining else None
            family_rows.append(dict(zip(('panel', 'model', 'metric', 'candidate'), key)) | dict(
                family_id=family, atoms=len(members), total_weight=weight,
                baseline_mean=b/weight, candidate_mean=c/weight, family_delta_percentage_points=100*(c-b)/weight,
                contribution_to_full_delta_percentage_points=100*(c-b)/total_weight,
                improved_atoms=sum(r['candidate_score'] > r['baseline_score'] for r in members),
                harmed_atoms=sum(r['candidate_score'] < r['baseline_score'] for r in members),
                unchanged_atoms=sum(r['candidate_score'] == r['baseline_score'] for r in members),
                leave_one_family_out_delta_percentage_points=None if leave_out is None else 100*leave_out,
                leave_one_family_out_shift_percentage_points=None if leave_out is None else 100*(leave_out-delta)))
        assert abs(delta-effect_by[key]['point_delta']) < 1e-12
    write(args.output / 'family_effects.jsonl', family_rows)
    with (args.output / 'family_effects.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(family_rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(family_rows)
    tests = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_paired_cluster_effects'],
                           cwd=args.plan_bundle, text=True, capture_output=True)
    (args.output / 'bundled_tests.stdout').write_text(tests.stdout + tests.stderr)
    assert tests.returncode == 0
    for path, checksum in used.items():
        assert sha(path) == checksum, ('input_changed_during_analysis', path)
    dump(args.output / 'receipt.json', dict(at=datetime.now(timezone.utc).isoformat(),
        status='complete_existing_scored_results_paired_family_effects', new_model_calls=0, new_grader_calls=0,
        independent_evaluation=False, development_selection_bias=True,
        interpretations=['Descriptive paired uncertainty conditional on previously selected methods and exposed panels.',
          'The intervals do not establish unseen generalization or remove researcher selection bias.',
          'Intervals crossing zero are not an integration or evaluation stop condition.',
          'Unavailable native answers retain their original not_scored identity and full-denominator zero success contribution.',
          'ALL uses original non-reference equal native-unit weights, not input or equal-family weights.'],
        source_hashes=used, source_bindings=source_bindings, identity_map=CONTROL,
        script_sha256=sha(__file__), bootstrap_command=command,
        bootstrap_resamples=5000, bootstrap_seed=240924, atoms=len(atoms), strata=len(effects['reports']),
        family_effect_rows=len(family_rows), bundled_tests_passed=10,
        existing_native_rows_crosschecked=len(native), existing_public_metadata_rows_crosschecked=len(public_native),
        existing_summary_groups_crosschecked=len(reports), input_denominator_policy='all existing panel members retained',
        reference_policy='reference excluded from native_ALL; original qualified pairs may contain reference endpoints',
        category_policy='one atom per original ALL unit; overlapping R mappings never become duplicate atoms'))
    print(json.dumps(dict(output=str(args.output), atoms=len(atoms), strata=len(effects['reports']),
                         new_model_calls=0, new_grader_calls=0)))


if __name__ == '__main__':
    main()
