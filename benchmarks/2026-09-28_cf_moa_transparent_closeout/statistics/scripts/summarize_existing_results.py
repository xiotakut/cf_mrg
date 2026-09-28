#!/usr/bin/env python3
"""Read-only, all-data summary and paired family bootstrap for published CF-MoA files.

Uses saved scores, not model requests or native graders. Does not select samples
by performance, build an exclusion mask, or change any source files.
Expected schema: analysis_source/full_v5/analyze_full.py at the supplied release.
"""
from __future__ import annotations
import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable
import numpy as np

CONTRASTS = (
    ('strong_B', 'original_C0'),
    ('candidate_with_rationales', 'strong_B'),
    ('candidate_with_rationales', 'candidate_only'),
    ('candidate_only', 'strong_B'),
    ('pool_old_plus_three', 'strong_B'),
    ('joint_selector', 'strong_B'),
)

def read_jsonl(path: Path) -> Iterable[dict]:
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        # Iterate physical lines. str.splitlines() can split U+2029 in a value.
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'{path}:{number}: invalid JSON') from exc


def find_file(directory: Path, stem: str) -> Path:
    for name in (stem + '.jsonl.gz', stem + '.jsonl'):
        path = directory / name
        if path.is_file():
            return path
    raise FileNotFoundError(f'Missing {directory}/{stem}.jsonl[.gz]')


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def aggregate_units(rows: list[dict], dimensions: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        if not row['complete'] or row['score'] is None:
            raise ValueError('Incomplete results: do not silently create a complete-case subset.')
        groups[tuple(row[d] for d in dimensions)].append(row)
    result = []
    for key, values in sorted(groups.items()):
        item = dict(zip(dimensions, key))
        item.update(units=len(values), families=len({r['family_id'] for r in values}),
                    mean_native_unit_score=float(np.mean([r['score'] for r in values])),
                    native_records=sum(r['native_records'] for r in values),
                    unavailable_mappings=sum(r['unavailable_mappings'] for r in values))
        result.append(item)
    return result


def paired_family_bootstrap(atoms_by_arm: dict[str, dict[str, tuple[str, float]]],
                            draws: int = 5000, seed: int = 240924) -> list[dict]:
    """Cluster-resample families; ratio of score sums to units, not family means.

    All contrasts use the same family draws. Each atom is a native unit or a
    qualified pair. Unavailable results already contribute 0 to saved scores.
    """
    arms = sorted({a for pair in CONTRASTS for a in pair})
    missing = set(arms) - set(atoms_by_arm)
    if missing:
        raise ValueError(f'Missing arms, not excluded: {sorted(missing)}')
    ids = sorted(atoms_by_arm['strong_B'])
    if not ids:
        raise ValueError('No atoms')
    for arm in arms:
        if set(atoms_by_arm[arm]) != set(ids):
            raise ValueError(f'Unmatched atoms for {arm}; preserve the planned denominator.')
    families = sorted({atoms_by_arm['strong_B'][k][0] for k in ids})
    fi = {f: i for i, f in enumerate(families)}
    counts = np.zeros(len(families), dtype=np.float64)
    deltas = np.zeros((len(families), len(CONTRASTS)), dtype=np.float64)
    for atom_id in ids:
        family = atoms_by_arm['strong_B'][atom_id][0]
        j = fi[family]
        counts[j] += 1
        for k, (candidate, baseline) in enumerate(CONTRASTS):
            cf, cs = atoms_by_arm[candidate][atom_id]
            bf, bs = atoms_by_arm[baseline][atom_id]
            if cf != family or bf != family:
                raise ValueError(f'Family mismatch for {atom_id}')
            deltas[j, k] += cs - bs
    observed = deltas.sum(axis=0) / counts.sum()
    rng = np.random.default_rng(seed)
    boot = np.empty((draws, len(CONTRASTS)), dtype=np.float64)
    for start in range(0, draws, 64):
        n = min(64, draws - start)
        pick = rng.integers(0, len(families), size=(n, len(families)))
        boot[start:start+n] = deltas[pick].sum(axis=1) / counts[pick].sum(axis=1)[:, None]
    limits = np.quantile(boot, [.025, .975], axis=0)
    return [dict(candidate=c, baseline=b, atoms=len(ids), families=len(families),
                 delta_pp=float(observed[k]*100),
                 percentile_95_pp=[float(limits[0,k]*100),float(limits[1,k]*100)],
                 resamples=draws, seed=seed, paired=True,
                 interpretation='descriptive_exposed_development_not_selection_adjusted')
            for k,(c,b) in enumerate(CONTRASTS)]


def build_atoms(rows: list[dict], metric: str) -> dict[str, dict[str, tuple[str, float]]]:
    arms: dict[str, dict[str, tuple[str,float]]] = defaultdict(dict)
    for r in rows:
        if metric == 'native_ALL' and r['category'] != 'ALL':
            continue
        if metric != 'native_ALL' and r['relation'] != metric:
            continue
        if not r['complete']:
            raise ValueError(f'Incomplete atom for {metric}')
        key = r['unit_id'] if metric == 'native_ALL' else r['pair_id']
        score = r['score'] if metric == 'native_ALL' else float(r['both_correct'] is True)
        if score is None:
            raise ValueError(f'Missing saved score: {key}')
        if key in arms[r['arm']]:
            raise ValueError(f'Duplicate atom: {r["arm"]}/{key}')
        arms[r['arm']][key] = (r['family_id'], float(score))
    return dict(arms)


def summarize_method(directory: Path, draws: int, seed: int) -> dict:
    units = list(read_jsonl(find_file(directory, 'native_units')))
    pairs = list(read_jsonl(find_file(directory, 'pairs')))
    inputs = list(read_jsonl(find_file(directory, 'per_input_status')))
    methods = {r['method'] for r in units}
    if len(methods) != 1:
        raise ValueError(f'Expected one backbone per folder, found {methods}')
    method = next(iter(methods))
    by_category = aggregate_units(units, ('method','arm','category'))
    by_source = aggregate_units([r for r in units if r['category']=='ALL'], ('method','arm','source'))
    format_groups: dict[tuple,list[dict]] = defaultdict(list)
    for r in inputs:
        if r['analysis_status'] != 'scored':
            raise ValueError('Pending input present; no silent exclusion permitted.')
        format_groups[(r['method'],r['arm'],r['answer_format'])].append(r)
    by_format=[]
    for (m,a,f),v in sorted(format_groups.items()):
        by_format.append(dict(method=m,arm=a,answer_format=f,inputs=len(v),
            correct=sum(r['correct'] is True for r in v),
            unavailable=sum(bool(r['unavailable']) for r in v),
            input_accuracy=sum(r['correct'] is True for r in v)/len(v),
            metric='input_accuracy_not_native_unit_mean'))
    intervals=[]
    for metric,records in [('native_ALL',units),('maintain',pairs),('respond',pairs)]:
        intervals.extend(dict(method=method,metric=metric,**x)
                         for x in paired_family_bootstrap(build_atoms(records,metric),draws,seed))
    # Check rather than regenerate saved native scores.
    quality=directory/'quality_summary.json'
    if quality.exists():
        q=json.loads(quality.read_text(encoding='utf-8'))
        observed={(r['arm'],r['category']):r for r in by_category}
        for rep in q['reports']:
            for cat in rep['native_categories']:
                actual=observed[rep['arm'],cat['category']]
                expected=cat['mean_native_unit_score']
                if actual['units']!=cat['units'] or abs(actual['mean_native_unit_score']-expected)>1e-10:
                    raise ValueError(f'Mean mismatch: {method}/{rep["arm"]}/{cat["category"]}')
    return dict(method=method,categories=by_category,all_sources=by_source,
                all_formats_input_metrics=by_format,paired_family_effects=intervals,
                no_outcome_filter=True,inference_calls=0,grader_calls=0,
                independent=False,development_selection_bias=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True,help='Existing data/full_v5 folder containing m4 and m5')
    parser.add_argument('--out',type=Path,required=True,help='New output folder; source files are never changed')
    parser.add_argument('--draws',type=int,default=5000)
    parser.add_argument('--seed',type=int,default=240924)
    args=parser.parse_args()
    if args.draws<100: raise ValueError('Use at least 100 bootstrap draws; released specification uses 5000.')
    args.out.mkdir(parents=True,exist_ok=True)
    results=[summarize_method(args.root/m,args.draws,args.seed) for m in ('m4','m5')]
    dump(args.out/'complete_summary.json',results)
    dump(args.out/'all_source_results.json',[r for x in results for r in x['all_sources']])
    dump(args.out/'format_input_results.json',[r for x in results for r in x['all_formats_input_metrics']])
    dump(args.out/'family_effect_intervals.json',[r for x in results for r in x['paired_family_effects']])
    lines=['# Complete, unfiltered native results','',
           '| Backbone | Arm | Native ALL units | Native ALL mean |',
           '|---|---|---:|---:|']
    for result in results:
        for r in result['categories']:
            if r['category']=='ALL':
                lines.append(f'| {r["method"]} | {r["arm"]} | {r["units"]} | {r["mean_native_unit_score"]:.8%} |')
    lines += ['', 'All sources and failures remain included. Family intervals are descriptive for exposed development data; they do not correct post-hoc method or scope selection. No inference or grading was performed.']
    (args.out/'full_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Wrote unfiltered summaries to {args.out}; 0 model calls, 0 grader calls.')

if __name__=='__main__':
    main()
