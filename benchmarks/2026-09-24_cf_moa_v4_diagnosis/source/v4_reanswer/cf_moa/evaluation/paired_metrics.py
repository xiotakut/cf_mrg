"""Explicit offline pair relations and family-cluster uncertainty; no model input."""
from collections import defaultdict
import random
from statistics import mean


def paired_metrics(predictions,pairs,*,seed=20260921,resamples=2000):
    # Each pair must come from a qualified evaluation ledger, not inferred from R.
    records=[]
    seen=set()
    for pair in pairs:
        if pair['pair_id'] in seen or pair['relation'] not in ('maintain','respond'):
            raise ValueError('Pairs require unique IDs and an explicit qualified relation')
        seen.add(pair['pair_id'])
        a,b=predictions[pair['left']],predictions[pair['right']]
        gold_same=a['semantic_gold']==b['semantic_gold']
        if gold_same!=(pair['relation']=='maintain'):
            raise ValueError('Declared relation disagrees with native semantic gold; do not force a flip')
        same=a['semantic_prediction']==b['semantic_prediction'] and not a['invalid'] and not b['invalid']
        records.append(dict(pair_id=pair['pair_id'],family_id=pair['family_id'],relation=pair['relation'],
            both_correct=a['correct'] is True and b['correct'] is True,semantic_same=same,
            both_native_scored=a['correct'] is not None and b['correct'] is not None,
            unavailable_endpoints=int(a['correct'] is None)+int(b['correct'] is None),
            valid_relation=(same if pair['relation']=='maintain' else
                not same and not a['invalid'] and not b['invalid'])))
    summaries=[]
    for relation in ('maintain','respond'):
        group=[r for r in records if r['relation']==relation]
        families=defaultdict(list)
        for row in group:
            families[row['family_id']].append(int(row['both_correct']))
        names=sorted(families)
        interval=None
        if names:
            rng=random.Random(seed)
            estimates=[]
            for _ in range(resamples):
                values=[v for name in rng.choices(names,k=len(names)) for v in families[name]]
                estimates.append(mean(values))
            estimates.sort()
            def quantile(p):
                position=(len(estimates)-1)*p
                lower=int(position)
                return estimates[lower]+(estimates[min(lower+1,len(estimates)-1)]-estimates[lower])*(position-lower)
            interval=[quantile(.025),quantile(.975)]
        summaries.append(dict(relation=relation,pairs=len(group),families=len(names),
            both_correct=sum(r['both_correct'] for r in group),
            both_native_scored=sum(r['both_native_scored'] for r in group),
            unavailable_endpoints=sum(r['unavailable_endpoints'] for r in group),
            valid_relation=sum(r['valid_relation'] for r in group),
            pair_weighted_both_correct_ci95=interval,cluster='family_id',bootstrap_seed=seed))
    return dict(records=records,summaries=summaries,
        interpretation='Stability and change are reported separately from both-correct; native failures retained')
