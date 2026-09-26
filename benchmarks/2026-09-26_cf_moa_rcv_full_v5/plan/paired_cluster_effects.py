#!/usr/bin/env python3
"""Paired FAMILY-cluster bootstrap of existing native/pair-level scores.

No model, grader, network or candidate selection is invoked.
Input JSONL: one row per original scoring atom (native unit OR eligible pair).
Required: panel, model, metric, family_id, atom_id, baseline_score, candidate_score.
Optional: candidate (default RCV_rationales_v1), weight (default 1).

The caller constructs native-unit scores with the UNCHANGED existing scorer.
Do not feed endpoint rows as if they were native units, or silently omit failed
outputs. Atoms belonging to a family are resampled together; the estimate keeps
the original atom weights, NOT an unrequested equal-family average.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random
from typing import Any


def quantile(sorted_values: list[float], q: float) -> float:
    pos = (len(sorted_values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def summarize(rows: list[dict[str, Any]], resamples: int = 5000,
              seed: int = 240924) -> dict[str, Any]:
    if not rows:
        return {"status": "empty_stratum", "atoms": 0, "families": 0,
                "point_delta": None, "paired_cluster_ci95": None}
    if resamples < 1:
        raise ValueError("resamples must be positive")
    groups: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    seen: set[str] = set()
    improved = harmed = unchanged = 0
    for row in rows:
        atom, family = str(row['atom_id']), str(row['family_id'])
        if atom in seen:
            raise ValueError(f"Duplicate scoring atom within one stratum: {atom}")
        seen.add(atom)
        vals = [row['baseline_score'], row['candidate_score'], row.get('weight', 1)]
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) for v in vals):
            raise ValueError("Scores/weight must be finite numbers; apply the original missing-output policy upstream")
        b, c, w = map(float, vals)
        if not (0 <= b <= 1 and 0 <= c <= 1 and w > 0):
            raise ValueError("Scores must be in [0,1]; original atom weight must be positive")
        groups[family][0] += w * b
        groups[family][1] += w * c
        groups[family][2] += w
        improved += c > b
        harmed += c < b
        unchanged += c == b
    values = list(groups.values())
    sb, sc, sw = (sum(v[j] for v in values) for j in range(3))
    result = dict(status='complete', atoms=len(rows), families=len(values),
                  total_weight=sw, baseline_mean=sb/sw, candidate_mean=sc/sw,
                  point_delta=(sc-sb)/sw, point_delta_percentage_points=100*(sc-sb)/sw,
                  improved_atoms=improved, harmed_atoms=harmed, unchanged_atoms=unchanged,
                  interpretation='paired descriptive uncertainty conditional on the fixed method and dataset; not proof against developer selection bias')
    if len(values) < 2:
        result.update(status='point_only_one_family', paired_cluster_ci95=None)
        return result
    rng = random.Random(seed)
    boot = []
    for _ in range(resamples):
        bsum = csum = wsum = 0.0
        for _ in values:
            b, c, w = values[rng.randrange(len(values))]
            bsum += b; csum += c; wsum += w
        boot.append((csum-bsum)/wsum)
    boot.sort()
    ci = [quantile(boot, .025), quantile(boot, .975)]
    result.update(paired_cluster_ci95=ci, paired_cluster_ci95_percentage_points=[100*v for v in ci],
                  resamples=resamples, seed=seed,
                  resampling_unit='family; both methods use the SAME resampled clusters')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--resamples', type=int, default=5000)
    parser.add_argument('--seed', type=int, default=240924)
    args = parser.parse_args()
    strata: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    with args.input.open(encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            for field in ('panel', 'model', 'metric', 'family_id', 'atom_id',
                          'baseline_score', 'candidate_score'):
                if field not in row:
                    raise ValueError(f"Line {line_number}: missing {field}")
            key = (str(row['panel']), str(row['model']), str(row['metric']),
                   str(row.get('candidate', 'RCV_rationales_v1')))
            strata[key].append(row)
    output = []
    for key in sorted(strata):
        output.append(dict(zip(('panel', 'model', 'metric', 'candidate'), key)) |
                      summarize(strata[key], args.resamples, args.seed))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'new_model_calls': 0, 'new_grader_calls': 0,
        'reports': output}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'strata': len(output), 'output': str(args.output), 'new_model_calls': 0}))


if __name__ == '__main__':
    main()
