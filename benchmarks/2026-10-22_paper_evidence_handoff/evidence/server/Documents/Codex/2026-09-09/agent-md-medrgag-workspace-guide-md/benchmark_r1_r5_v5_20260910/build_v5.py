"""Create v5 evaluation selection without changing v4 semantics or source records."""
import csv,gzip,json,random,sys
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROTOCOL=json.loads((HERE/'sampling_protocol.json').read_text())
V4=Path(PROTOCOL['parent_directory'])
LABELS=('R1','R2','R3','R4','R5')


def read_targets(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        for line in f:yield json.loads(line)


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    with (V4/'exports/archive_unit_coverage.csv').open() as f:archive={r['unit_id']:r for r in csv.DictReader(f)}
    with (V4/'source_scope_inventory.csv').open() as f:names={r['resource_id']:r['benchmark'] for r in csv.DictReader(f)}
    source=V4/'exports/all_reviewed_target_annotations.jsonl.gz'
    pools=defaultdict(set)
    for r in read_targets(source):
        if r['evaluation_eligible'] and 'R5' in r['labels']:pools[r['resource_id']].add(r['unit_id'])
    assert set(pools)==set(PROTOCOL['sources'])
    assert sum(map(len,pools.values()))==35872
    chosen=set();draw={}
    for src in sorted(pools):
        pool=sorted(pools[src]);assert len(pool)>=PROTOCOL['per_source']
        draw[src]=sorted(random.Random(PROTOCOL['master_seed_hex']+':'+src).sample(pool,PROTOCOL['per_source']))
        assert len(set(draw[src]))==450;chosen.update(draw[src])
    assert len(chosen)==3600
    selected_path=HERE/'selected_r5_unit_ids.json'
    if selected_path.exists():assert json.loads(selected_path.read_text())==draw,'Existing draw must never be replaced with a different sample'
    else:selected_path.write_text(json.dumps(draw,ensure_ascii=False,indent=2)+'\n')
    poolrows=[]
    for src in sorted(pools):
        for uid in sorted(pools[src]):
            poolrows.append(dict(resource_id=src,benchmark=names[src],unit_id=uid,source_root_id=archive[uid]['source_root_id'],in_frozen_v3=archive[uid]['in_frozen_v3'],selected_R5=uid in chosen,pool_size=len(pools[src]),sample_size=450,inclusion_probability=450/len(pools[src]),design_weight=len(pools[src])/450))
    write_csv(HERE/'r5_sampling_frame.csv',poolrows)
    write_csv(HERE/'selected_r5_units.csv',[r for r in poolrows if r['selected_R5']])
    category_ids=defaultdict(set);category_targets=Counter();unit_labels=defaultdict(set);semantic_labels=defaultdict(set);unit_targets=Counter();src_targets=Counter();selected_target_count=0
    before_r14={l:set() for l in LABELS[:-1]};after_r14={l:set() for l in LABELS[:-1]}
    with gzip.open(HERE/'target_annotations.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as allout,gzip.open(HERE/'selected_targets.jsonl.gz','wt',encoding='utf-8',compresslevel=3) as out:
        for old in read_targets(source):
            uid=old['unit_id'];src=old['resource_id'];labels=old['labels'];old_eligible=old['evaluation_eligible']
            evaluation_labels=[l for l in labels if old_eligible and (l!='R5' or uid in chosen)]
            r=dict(old,benchmark=names[src],v4_evaluation_eligible=old_eligible,evaluation_labels=evaluation_labels,evaluation_eligible=bool(evaluation_labels),v5_selection_reason=('retained_non_R5_and_or_randomly_selected_R5' if evaluation_labels else 'R5_budget_not_selected' if old_eligible else 'v4_ineligible'),in_frozen_v3=archive[uid]['in_frozen_v3']=='True',r5_sample_selected=uid in chosen)
            allout.write(json.dumps(r,ensure_ascii=False)+'\n')
            for l in LABELS[:-1]:
                if old_eligible and l in labels:before_r14[l].add(old['judgment_id'])
                if l in evaluation_labels:after_r14[l].add(old['judgment_id'])
            if not evaluation_labels:continue
            out.write(json.dumps(r,ensure_ascii=False)+'\n');selected_target_count+=1;src_targets[src]+=1;unit_targets[uid]+=1
            unit_labels[uid].update(evaluation_labels);semantic_labels[uid].update(labels)
            for l in evaluation_labels:category_ids[l].add(uid);category_targets[l]+=1
    assert before_r14==after_r14,'All eligible non-R5 judgment memberships must be retained'
    assert category_ids['R5']==chosen
    units=[]
    for uid in sorted(unit_labels):
        a=archive[uid];src=a['resource_id']
        units.append(dict(unit_id=uid,resource_id=src,benchmark=names[src],source_root_id=a['source_root_id'],labels=sorted(filter(None,a['semantic_labels'].split('|'))),evaluation_labels=sorted(unit_labels[uid]),eligible_target_count=unit_targets[uid],in_frozen_v3=a['in_frozen_v3']=='True',r5_sample_selected=uid in chosen,source_archive=str(V4/'exports/archive_unit_coverage.csv')))
    with (HERE/'units.jsonl').open('w') as f:
        for r in units:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    crosswalk=[]
    for uid,a in archive.items():
        if a['evaluation_eligible']!='True':continue
        crosswalk.append(dict(unit_id=uid,resource_id=a['resource_id'],benchmark=names[a['resource_id']],in_frozen_v3=a['in_frozen_v3'],in_v5=uid in unit_labels,v5_evaluation_labels='|'.join(sorted(unit_labels.get(uid,()))),selected_R5=uid in chosen,status='retained_v3_member' if uid in unit_labels and a['in_frozen_v3']=='True' else 'outside_v3_selected' if uid in unit_labels else 'v4_eligible_R5_not_selected'))
    write_csv(HERE/'v3_v4_v5_membership.csv',crosswalk)
    cats=[dict(category=l,adopted_units=len(category_ids[l]),adopted_targets=category_targets[l],benchmark_count=len({archive[u]['resource_id'] for u in category_ids[l]})) for l in LABELS]
    write_csv(HERE/'category_summary.csv',cats)
    sources=[]
    for src in sorted({u['resource_id'] for u in units}):
        group=[u for u in units if u['resource_id']==src]
        sources.append(dict(resource_id=src,benchmark=names[src],adopted_units=len(group),adopted_targets=src_targets[src],in_frozen_v3=sum(u['in_frozen_v3'] for u in group),**{l:sum(l in u['evaluation_labels'] for u in group) for l in LABELS}))
    write_csv(HERE/'source_summary.csv',sources)
    r5_summary=[]
    for src in sorted(pools):
        rows=[r for r in poolrows if r['resource_id']==src and r['selected_R5']]
        rootcounts=Counter(r['source_root_id'] for r in rows if r['source_root_id'])
        r5_summary.append(dict(resource_id=src,benchmark=names[src],pool_units=len(pools[src]),selected_units=len(rows),sample_fraction=450/len(pools[src]),pool_root_ids=len({archive[u]['source_root_id'] for u in pools[src] if archive[u]['source_root_id']}),selected_root_ids=len(rootcounts),max_variants_per_selected_root=max(rootcounts.values(),default=0),in_frozen_v3=sum(r['in_frozen_v3']=='True' for r in rows)))
    write_csv(HERE/'r5_sampling_summary.csv',r5_summary)
    manifest=dict(version='v5',parent_version='v4',selection_status='complete',runtime_compatibility='not_verified',adopted_units=len(units),adopted_targets=selected_target_count,adopted_sources=len(sources),r5_sources=8,r5_units=3600,per_source_r5=450,categories=cats,v3_member_units=sum(u['in_frozen_v3'] for u in units),outside_v3_units=sum(not u['in_frozen_v3'] for u in units),semantic_label_field='labels',evaluation_label_field='evaluation_labels',selected_targets='selected_targets.jsonl.gz',all_target_annotations='target_annotations.jsonl.gz',sampling_protocol='sampling_protocol.json',parent_directory=str(V4),preserved_v3=True,preserved_v4=True)
    (HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
