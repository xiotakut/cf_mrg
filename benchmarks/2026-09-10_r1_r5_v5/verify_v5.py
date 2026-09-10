"""Independently reproduce selection and verify every target against v4."""
import csv,gzip,itertools,json,random
from pathlib import Path
from collections import defaultdict,Counter
P=Path(__file__).resolve().parent
protocol=json.loads((P/'sampling_protocol.json').read_text());parent=Path(protocol['parent_directory'])
with (P/'r5_sampling_frame.csv').open() as f:frame=list(csv.DictReader(f))
pools=defaultdict(list)
for r in frame:pools[r['resource_id']].append(r['unit_id'])
assert len(frame)==len({r['unit_id'] for r in frame})==35872
expected=set()
for src,pool in pools.items():
    draw=set(random.Random(protocol['master_seed_hex']+':'+src).sample(sorted(pool),450));expected.update(draw)
    recorded={r['unit_id'] for r in frame if r['resource_id']==src and r['selected_R5']=='True'}
    assert draw==recorded
saved=json.loads((P/'selected_r5_unit_ids.json').read_text())
assert expected=={u for group in saved.values() for u in group} and len(expected)==3600
with (parent/'exports/archive_unit_coverage.csv').open() as f:old_units={r['unit_id']:r for r in csv.DictReader(f)}
with (P/'units.jsonl').open() as f:units={r['unit_id']:r for r in map(json.loads,f)}
for uid,r in units.items():assert set(r['labels'])==set(filter(None,old_units[uid]['semantic_labels'].split('|')))
allpool=set();alltargetids=set();selectedtargetids=set();categoryunits=defaultdict(set);categorytargets=Counter();selectedunits=set();original_r14={l:set() for l in ('R1','R2','R3','R4')};new_r14={l:set() for l in original_r14}
with gzip.open(parent/'exports/all_reviewed_target_annotations.jsonl.gz','rt') as oldf,gzip.open(P/'target_annotations.jsonl.gz','rt') as newf:
    for left,right in itertools.zip_longest(oldf,newf):
        assert left is not None and right is not None
        a=json.loads(left);b=json.loads(right);uid=a['unit_id'];jid=a['judgment_id'];assert jid not in alltargetids;alltargetids.add(jid)
        for k in a:
            if k!='evaluation_eligible':assert a[k]==b[k],(jid,k)
        assert b['v4_evaluation_eligible']==a['evaluation_eligible']
        wanted=[l for l in a['labels'] if a['evaluation_eligible'] and (l!='R5' or uid in expected)]
        assert b['evaluation_labels']==wanted and b['evaluation_eligible']==bool(wanted)
        if a['evaluation_eligible'] and 'R5' in a['labels']:allpool.add(uid)
        for l in original_r14:
            if a['evaluation_eligible'] and l in a['labels']:original_r14[l].add(jid)
            if l in wanted:new_r14[l].add(jid)
        if wanted:
            assert not b['image_required'];selectedtargetids.add(jid);selectedunits.add(uid)
            for l in wanted:categoryunits[l].add(uid);categorytargets[l]+=1
assert allpool=={r['unit_id'] for r in frame}
assert original_r14==new_r14
assert selectedunits==set(units)
with gzip.open(P/'selected_targets.jsonl.gz','rt') as f:
    ids=[]
    for line in f:
        r=json.loads(line);assert r['evaluation_eligible'] and r['evaluation_labels'];ids.append(r['judgment_id'])
assert len(ids)==len(set(ids)) and set(ids)==selectedtargetids
m=json.loads((P/'manifest.json').read_text());assert len(selectedunits)==m['adopted_units'] and len(ids)==m['adopted_targets']
for row in m['categories']:
    assert row['adopted_units']==len(categoryunits[row['category']]) and row['adopted_targets']==categorytargets[row['category']]
report=dict(passed=True,method='reproduce seeded random.sample from complete published frame; compare all v5 target records field-by-field to v4',seed_reproduced=True,pool_membership_exact=True,per_source_samples={s:len(v) for s,v in saved.items()},r5_selected_units=3600,all_v4_target_records_preserved=len(alltargetids),original_semantic_fields_preserved=True,all_eligible_r1_r4_judgments_preserved={l:len(v) for l,v in original_r14.items()},adopted_units=len(selectedunits),adopted_targets=len(ids),no_ineligible_target_selected=True,note='Correct random procedure and exact replay, not a claim that a random sample must look balanced by every clinical feature.')
(P/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
