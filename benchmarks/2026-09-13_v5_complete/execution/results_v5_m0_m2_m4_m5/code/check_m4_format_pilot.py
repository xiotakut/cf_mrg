"""Validate real structured outputs and reject the observed malformed shapes."""
import json
from pathlib import Path
import jsonschema
from m4_output_schema import output_schema

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'm4_format_structured_pilot'
items = {r['item']['item_id']: r['item'] for line in (OUT / 'inputs.jsonl').open() if (r := json.loads(line))}
rows = [json.loads(line) for line in (OUT / 'predictions.jsonl').open()]
assert len(rows) == len({r['item_id'] for r in rows}) == 100
assert {r['item_id'] for r in rows} == set(items)
failures = []
for row in rows:
    try:
        obj = json.loads(row['raw_response'])
        jsonschema.validate(obj, output_schema(items[row['item_id']]))
    except (json.JSONDecodeError, jsonschema.ValidationError) as error:
        failures.append(dict(item_id=row['item_id'], finish_reason=row['finish_reason'], error=str(error)[:300]))
        # The grammar must hold for normally completed outputs. Truncation is
        # retained as an experimental failure, never silently repaired.
        assert row['finish_reason'] == 'length', failures[-1]
# Real failure shapes: option text instead of key, nested diagnosis, duplicate
# multi-answer keys. These must remain rejected, without permissive rescoring.
for fmt in ('single', 'diagnosis', 'multi'):
    item = next(i for i in items.values() if i['answer_format']==fmt)
    key = next(iter(item['options']), 'A')
    bad = {'step_by_step_thinking': 'Explanation', 'answer_choice':
           key + '. extra option text' if fmt=='single' else {'diagnosis': 'label'} if fmt=='diagnosis' else [key,key]}
    assert not jsonschema.Draft202012Validator(output_schema(item)).is_valid(bad)
receipt = dict(status='checks_passed_with_recorded_truncation' if failures else 'passed',unique_inputs=100,schema_valid=100-len(failures),failures=failures,negative_shapes_rejected=3,finish_reasons={reason:sum(r['finish_reason']==reason for r in rows) for reason in {r['finish_reason'] for r in rows}})
(OUT / 'schema_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
