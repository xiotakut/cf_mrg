"""Validate a self-contained GitHub result package without raw benchmark files."""
import argparse
import csv
import gzip
import json
from pathlib import Path

LABELS = {'R1', 'R2', 'R3', 'R4', 'R5'}
FORBIDDEN = {'original_records', 'reviewed_original_records', 'original_raw_response'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_omissions(value, location):
    if isinstance(value, dict):
        require(not (FORBIDDEN & value.keys()), f'Raw record field in {location}: {FORBIDDEN & value.keys()}')
        for key, item in value.items():
            check_omissions(item, location + '.' + key)
    elif isinstance(value, list):
        for item in value:
            check_omissions(item, location)


def jsonl(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def csv_value_matches(value, expected):
    if isinstance(expected, (dict, list)):
        return json.loads(value) == expected
    if expected is None:
        return value == ''
    if isinstance(expected, bool):
        return value.lower() == str(expected).lower()
    return value == str(expected)


def verify(package):
    manifest = json.loads((package / 'manifest.json').read_text(encoding='utf-8'))
    require(manifest['original_benchmark_bodies_included'] is False, 'Manifest claims raw benchmark bodies')
    full_path = 'data/complete_annotations.jsonl.gz'
    analysis_path = 'data/analysis_annotations.jsonl.gz'
    csv_paths = ['data/analysis_units.csv.gz', 'data/analysis_judgments.csv.gz',
                 'data/analysis_unclassified.csv.gz']
    for name in [full_path, analysis_path, *csv_paths]:
        require((package / name).is_file(), 'Missing required file: ' + name)

    full_ids, selected, analysis = set(), {}, []
    jsonl_counts, checked_gzip = {}, set()
    # Consume every gzip to EOF. JSONL files also get recursive raw-field checks.
    for path in sorted(package.rglob('*.gz')):
        name = path.relative_to(package).as_posix()
        if name.endswith('.jsonl.gz'):
            count = 0
            for row in jsonl(path):
                count += 1
                check_omissions(row, f'{name}:{count}')
                if name == full_path:
                    uid = row['unit_id']
                    require(uid not in full_ids, 'Duplicate complete unit: ' + uid)
                    full_ids.add(uid)
                    require(isinstance(row.get('analysis_selected'), bool), 'Missing selection flag: ' + uid)
                    if row['analysis_selected']:
                        selected[uid] = row
                    else:
                        require(row.get('review_state') == 'outside_frozen_review_cohort',
                                'Unselected unit claims reviewed state: ' + uid)
                elif name == analysis_path:
                    analysis.append(row)
            jsonl_counts[name] = count
        else:
            with gzip.open(path, 'rb') as stream:
                while stream.read(1024 * 1024):
                    pass
        checked_gzip.add(name)
    for name, expected in manifest['jsonl_record_counts'].items():
        require(jsonl_counts.get(name) == expected, 'JSONL manifest count mismatch: ' + name)
    require(len(full_ids) == 55991, f'Complete unit count: {len(full_ids)}')
    require(len(selected) == len(analysis) == 28243, 'Selected/analysis count is not 28243')
    units, targets, excluded = {}, {}, set()
    for row in analysis:
        uid = row['unit_id']
        require(uid not in units, 'Duplicate analysis unit: ' + uid)
        require(row == selected.get(uid), 'Analysis fields differ from selected complete record: ' + uid)
        require(row.get('review_state') == 'reviewed', 'Analysis unit is not reviewed: ' + uid)
        union = set()
        for child in row['judgments']:
            jid = child['judgment_id']
            labs = child['labels']
            require(isinstance(labs, list) and set(labs) <= LABELS and len(labs) == len(set(labs)),
                    'Invalid child labels: ' + jid)
            require(jid not in targets, 'Duplicate judgment ID: ' + jid)
            union.update(labs)
            targets[jid] = {**{k: row.get(k) for k in ['unit_id', 'resource_id', 'collection_kind']}, **child}
            if child.get('scoring_eligible') is False:
                require(child.get('gold_review_status') and child.get('scoring_exclusion_reason'),
                        'Incomplete scoring exclusion: ' + jid)
                excluded.add(jid)
        require(set(row['labels']) == union and len(row['labels']) == len(union),
                'Parent/child label union mismatch: ' + uid)
        units[uid] = row
    require(list(units) == list(selected), 'Analysis IDs/order differ from selected complete IDs')
    require(len(targets) == 80910, f'Judgment count: {len(targets)}')
    require(len(excluded) == 11, f'Scoring exclusions: {len(excluded)}')
    no_labels = [r['unit_id'] for r in analysis if not r['labels']]
    require(len(no_labels) == 4051, f'Unclassified units: {len(no_labels)}')
    text = [r for r in analysis if r['collection_kind'] == 'text_comparison_record']
    r5_count = sum('R5' in r['labels'] for r in text)
    require(len(text) == 25746 and r5_count == 20318, 'Text/R5 count mismatch')

    csv_counts = {}
    for name in csv_paths:
        is_child = name.endswith('analysis_judgments.csv.gz')
        expected = targets if is_child else units
        id_field = 'judgment_id' if is_child else 'unit_id'
        seen = []
        with gzip.open(package / name, 'rt', encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            require({id_field, 'unit_id', 'resource_id', 'labels'} <= set(reader.fieldnames or []),
                    'Missing CSV identity/label fields: ' + name)
            for row in reader:
                key = row[id_field]
                require(key in expected, 'Unknown CSV ID: ' + key)
                require(all(csv_value_matches(value, expected[key].get(field)) for field, value in row.items()),
                        'CSV field mismatch: ' + name + ':' + key)
                seen.append(key)
        wanted = list(targets) if is_child else no_labels if name.endswith('analysis_unclassified.csv.gz') else list(units)
        require(seen == wanted, 'CSV IDs/order/count differ from JSONL: ' + name)
        csv_counts[name] = len(seen)

    # Audit exports can contain nested review snapshots too; check uncompressed
    # structured files, not just the primary data files.
    for path in sorted(package.rglob('*')):
        if path.suffix == '.jsonl':
            for line, row in enumerate(jsonl(path), 1):
                check_omissions(row, f'{path.relative_to(package)}:{line}')
        elif path.suffix == '.json' and path.name != 'github_package_validation.json':
            check_omissions(json.loads(path.read_text(encoding='utf-8')), str(path.relative_to(package)))
    return dict(status='passed', gzip_files_checked=len(checked_gzip),
                gzip_files=sorted(checked_gzip), jsonl_counts=jsonl_counts,
                complete_units=len(full_ids), analysis_units=len(units), judgments=len(targets),
                csv_counts=csv_counts, unclassified_units=len(no_labels),
                scoring_exclusions=len(excluded), scoring_exclusion_ids=sorted(excluded),
                text_units=len(text), text_R5_units=r5_count,
                analysis_matches_complete_selected_fields=True,
                analysis_parent_labels_equal_child_union=True,
                csv_fields_and_ids_match_jsonl=True, original_record_fields_absent=True,
                unselected_units_marked_outside_frozen_review_cohort=len(full_ids)-len(selected),
                raw_data_required=False, semantic_validity_proved=False,
                limitation='Package consistency only; does not repeat source downloads or medical semantic review.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.package)
    except (OSError, ValueError, KeyError, TypeError, EOFError) as error:
        result = dict(status='failed', error=str(error), raw_data_required=False)
    report = args.package / 'reports/github_package_validation.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'passed' else 1)
