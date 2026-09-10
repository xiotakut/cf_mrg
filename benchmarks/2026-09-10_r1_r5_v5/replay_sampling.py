"""Replay the published draw using only the protocol, candidate IDs and selected IDs."""
import csv,gzip,json,random
from collections import defaultdict
from pathlib import Path
p=Path(__file__).resolve().parent
protocol=json.loads((p/'sampling_protocol.json').read_text())
file=p/'r5_sampling_frame.csv'
if file.exists():handle=file.open()
else:handle=gzip.open(p/'r5_sampling_frame.csv.gz','rt')
with handle:rows=list(csv.DictReader(handle))
pools=defaultdict(list)
for r in rows:pools[r['resource_id']].append(r['unit_id'])
assert len(rows)==len({r['unit_id'] for r in rows})==35872
recorded=json.loads((p/'selected_r5_unit_ids.json').read_text())
assert set(recorded)==set(pools)==set(protocol['sources'])
for src,pool in pools.items():
    draw=sorted(random.Random(protocol['master_seed_hex']+':'+src).sample(sorted(pool),protocol['per_source']))
    assert draw==recorded[src]
    assert set(draw)=={r['unit_id'] for r in rows if r['resource_id']==src and r['selected_R5']=='True'}
    assert len(draw)==len(set(draw))==450
print('PASS: exact replay for all 8 sources, 450 per source, 3600 unique R5 units; no files changed.')
