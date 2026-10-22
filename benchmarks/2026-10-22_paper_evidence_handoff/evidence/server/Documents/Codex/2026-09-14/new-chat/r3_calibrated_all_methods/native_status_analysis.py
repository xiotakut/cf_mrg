"""Separate native TC acceptance failures from diagnosis errors; zero model calls."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from r3_audit import HERE, OUT as DATA, read, write, dump
from r3_calibrated_expansion import scoring

out=HERE/'r3_calibrated_all_methods'
objects,score,canonical=scoring()
base={r['item_id']:r for r in read(DATA/'baseline_scores.jsonl') if r['method']=='M7'}
evaluation={r['item_id']:r for r in read(DATA/'evaluation.jsonl')}
rows=[]
for r in read(HERE/'r3_calibrated_expansion/all_method_contexts/inputs.jsonl'):
    if r['method']!='M7':continue
    iid=r['item']['item_id'];native=json.loads(Path(r['provenance']['result']).read_text())
    parsed=objects(r['original_response'],'answer')
    answer=parsed['answer'] if parsed else None
    metric=score(dict(raw_response=json.dumps(dict(answer=answer)) if parsed else ''),evaluation[iid],r['item'],canonical)
    rows.append(dict(item_id=iid,status=native['status'],termination=native['termination'],
        returned_kind=native.get('returned_kind'),native_correct=base[iid]['correct'],native_invalid=base[iid]['invalid'],
        raw_answer=answer,permissive_parse_correct=metric['correct'],permissive_parse_invalid=metric['invalid']))
write(out/'native_m7_status.jsonl',rows)
summary=[]
for status in sorted({r['status'] for r in rows}):
    rs=[r for r in rows if r['status']==status]
    summary.append(dict(status=status,n=len(rs),native_correct=sum(r['native_correct'] for r in rs),
        native_invalid=sum(r['native_invalid'] for r in rs),raw_answer_parsed=sum(r['raw_answer'] is not None for r in rs),
        permissive_parse_correct=sum(r['permissive_parse_correct'] for r in rs),
        terminations=dict(Counter(r['termination'] for r in rs))))
dump(out/'native_m7_status_summary.json',dict(results=summary,new_calls=0,
     interpretation='Permissive raw parsing is a descriptive acceptance control, not a correction to the frozen TC baseline.'))
print(summary)
