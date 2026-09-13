"""Read-only diagnosis of frozen M4/M5 outputs; does not rescore or repair them."""
import ast
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Use the exact frozen adapter without importing inference/scoring dependencies.
tree = ast.parse((ROOT / 'code/analyze_v5.py').read_text())
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'objects')
namespace = {'json': json}
exec(compile(ast.Module(body=[node], type_ignores=[]), '<frozen objects>', 'exec'), namespace)
objects = namespace['objects']
assert objects('{"answer_choice":"A"}', 'answer_choice')['answer_choice'] == 'A'
assert objects('{"answer_choice":"A"}{"answer_choice":"B"}', 'answer_choice') is None

def read(name):
    with (ROOT / name).open() as f:
        return [json.loads(line) for line in f]

def relaxed(raw):
    decoder = json.JSONDecoder(strict=False)
    for match in re.finditer(r'\{', raw):
        try:
            obj, _ = decoder.raw_decode(raw[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and 'answer_choice' in obj:
            return True
    return False

preds = {(r['method_id'], r['item_id']): r for r in read('predictions.jsonl') if r.get('method_id') in ('M4', 'M5')}
scored = read('scored.jsonl')
items = {r['item_id']: r for r in read('items.jsonl')}
report = {'denominator': '15616 scored mappings per method, including reference records; unique input diagnostics separately use 13905', 'relaxed_decode_note': 'Diagnostic only: accepts literal control characters in JSON strings; no output repair or score changes', 'methods': {}}
for method in ('M4', 'M5'):
    rows = [r for r in scored if r['method'] == method]
    reasons = collections.Counter(r['invalid_reason'] or 'valid' for r in rows)
    detail = collections.Counter()
    examples = {}
    for r in rows:
        raw = preds[method, r['item_id']]['raw_response']
        reason = r['invalid_reason']
        if reason == 'malformed_json':
            obj = objects(raw, 'answer_choice')
            kind = ('strict_object_present' if obj is not None else
                    'control_character_tolerant_decode_finds_answer' if relaxed(raw) else
                    'no_answer_even_with_control_character_tolerance')
            detail[kind] += 1
            examples.setdefault(kind, r['item_id'])
        if reason == 'invalid_option_key':
            obj = objects(raw, 'answer_choice')
            value = obj['answer_choice'] if obj else None
            opts = items[r['item_id']]['options']
            match = re.match(r'^([A-Za-z0-9]+)[.、:)\s]', value or '')
            kind = 'valid_key_followed_by_extra_text' if match and match[1] in opts else 'other_invalid_option'
            detail[kind] += 1
            examples.setdefault(kind, {'item_id': r['item_id'], 'answer_choice': value})
    unique = [v for (m, _), v in preds.items() if m == method]
    formats = {}
    for fmt in sorted({r['answer_format'] for r in rows}):
        group = [r for r in rows if r['answer_format'] == fmt]
        formats[fmt] = {'records': len(group), 'format_valid': sum(not r['format_invalid'] for r in group), 'native_valid': sum(not r['invalid'] for r in group)}
    report['methods'][method] = {
        'records': len(rows), 'format_valid': sum(not r['format_invalid'] for r in rows),
        'format_valid_pct': 100 * sum(not r['format_invalid'] for r in rows) / len(rows),
        'native_valid': reasons['valid'], 'native_valid_pct': 100 * reasons['valid'] / len(rows),
        'invalid_reasons': dict(reasons), 'diagnostics_scored_mappings': dict(detail), 'examples': examples,
        'formats': formats, 'unique_inputs': len(unique),
        'unique_strict_answer_choice_object': sum(objects(v['raw_response'], 'answer_choice') is not None for v in unique),
        'finish_reasons': dict(collections.Counter(v['finish_reason'] for v in unique)),
    }
(ROOT / 'output_validity_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
