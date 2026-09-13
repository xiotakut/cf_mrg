"""Small shared utilities for the existing dated benchmark run-pack interface."""
import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V5 = Path('/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5')
SELECTION = Path('/home/data3/txy/Documents/Codex/2026-09-09/agent-md-medrgag-workspace-guide-md/benchmark_r1_r5_v5_20260910')
PACK = Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
MEDRAG = Path('/home/data3/txy/Documents/Codex/2026-09-10/benchmark-gzxiong-medrag-sota-baseline-medrag')
VISIBLE = ('question', 'options', 'fixed_evidence', 'answer_format')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    # Preserve dict insertion order, including native option order.
    return hashlib.sha256(encoded(value)).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    path = Path(path)
    op = gzip.open if path.suffix == '.gz' else open
    with op(path, 'rt') as f:
        return [json.loads(line) for line in f if line.strip()]


def atomic(path, value, lines=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'wb') as f:
            if lines:
                for row in value:
                    f.write(encoded(row) + b'\n')
            else:
                f.write(encoded(value) + b'\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def visible(item):
    result = {key: item[key] for key in VISIBLE}
    if not isinstance(result['question'], str) or not result['question'].strip():
        raise ValueError('empty_question')
    if not isinstance(result['options'], dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in result['options'].items()):
        raise ValueError('invalid_options')
    if not isinstance(result['fixed_evidence'], list) or not all(isinstance(v, str) for v in result['fixed_evidence']):
        raise ValueError('invalid_evidence')
    return result


def answer_contract(item):
    fmt = item['answer_format']
    return {'single': 'one native option key string',
            'multi': 'a JSON array of one or more native option keys',
            'diagnosis': 'one concise most likely diagnosis label',
            'relation': 'exactly one of "higher", "lower", "no difference", "uncertainty"',
            'robustness_single': 'one native option key string'}[fmt]


def question_text(item):
    item = visible(item)
    text = 'Here is the question:\n' + item['question']
    if item['options']:
        text += '\n\nHere are the potential choices:\n' + '\n'.join(k + '. ' + v for k, v in item['options'].items())
    if item['fixed_evidence']:
        text += '\n\nEvidence supplied with the question:\n' + '\n\n'.join(item['fixed_evidence'])
    text += '\n\nThe answer field must contain ' + answer_contract(item) + '.'
    if item['answer_format'] == 'robustness_single':
        # Exact native robustness requirement already visible to v5 M4/M5.
        text += '\nSome supplied D-numbered documents may contain factual errors. Identify them, correct their factual errors, and answer the main question. Do not assume all documents are correct. Also include an "errors" JSON array; each entry has "document_id" (D-numbered ID) and "correction" (concise corrected statement). Use [] when none are erroneous.'
    return text


def json_object(raw, key):
    """Use the v5 strict-object convention; conflicting answers are invalid."""
    decoder, found, pos = json.JSONDecoder(), [], 0
    while pos < len(raw):
        start = raw.find('{', pos)
        if start < 0:
            break
        try:
            obj, size = decoder.raw_decode(raw[start:])
            pos = start + size
            if isinstance(obj, dict) and key in obj:
                found.append(obj)
        except json.JSONDecodeError:
            pos = start + 1
    if not found or any(obj[key] != found[0][key] for obj in found[1:]):
        raise ValueError('missing_or_conflicting_' + key)
    return found[0]


def valid_answer(raw, item):
    try:
        obj = json_object(raw, 'answer')
    except ValueError as e:
        return str(e)
    value, fmt = obj['answer'], item['answer_format']
    if fmt == 'multi':
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or x not in item['options'] for x in value) or len(value) != len(set(value)):
            return 'invalid_option_set'
    elif not isinstance(value, str) or not value.strip():
        return 'invalid_answer_type'
    elif fmt in ('single', 'robustness_single') and value not in item['options']:
        return 'invalid_option_key'
    elif fmt == 'relation' and value.strip().lower() not in ('higher', 'lower', 'no difference', 'uncertainty'):
        return 'invalid_relation'
    if fmt == 'robustness_single':
        errors = obj.get('errors')
        if not isinstance(errors, list) or any(not isinstance(e, dict) or not isinstance(e.get('document_id'), str) or not isinstance(e.get('correction'), str) for e in errors):
            return 'invalid_errors'
        ids = [e['document_id'] for e in errors]
        if len(ids) != len(set(ids)) or not set(ids) <= {f'D{i}' for i in range(len(item['fixed_evidence']))}:
            return 'invalid_document_ids'
    return None
