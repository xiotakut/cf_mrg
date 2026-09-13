"""Replay all 1,646 frozen terminals; do not load a model or change original outputs."""
import collections
import json
import sys
from pathlib import Path
from normalize_accepted import normalize_accepted, test

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/home/data3/txy/Documents/Codex/2026-09-13/agent-md-medrgag-workspace-guide-md/results_v5_m6_m7/formal_balanced')
sys.path.insert(0, str(SOURCE / 'code'))
from common import valid_answer, visible


def main():
    test()
    original = [json.loads(line) for line in (ROOT / 'snapshot.jsonl').open()]
    assert len(original) == len({r['item_id'] for r in original}) == 1646
    wanted = {r['item_id'] for r in original}
    items = {r['item_id']: visible(r) for line in (SOURCE / 'data/inputs.jsonl').open()
             if (r := json.loads(line))['item_id'] in wanted}
    assert set(items) == wanted
    counts, rules, remaining, detail = collections.Counter(), collections.Counter(), collections.Counter(), []
    for result in original:
        item = items[result['item_id']]
        raw, rule = normalize_accepted(result, item)
        accepted = result['termination'] == 'accepted'
        old_valid = result['status'] == 'ok'
        error = valid_answer(raw, item) if accepted else result['termination']
        new_valid = error is None
        if old_valid or not accepted:
            assert raw == result['raw_response'] and new_valid == old_valid
        if rule:
            assert accepted and not old_valid
            rules[rule] += 1
            # Only answer representation changes; all explicit other fields remain.
            if rule != 'bare_exact_key':
                before = json.loads(result['raw_response'])
                after = json.loads(raw)
                assert {k: v for k, v in before.items() if k != 'answer'} == {k: v for k, v in after.items() if k != 'answer'}
                key = after['answer']
                assert before['answer'] == (key + '. ' + item['options'][key] if rule == 'key_plus_exact_option_text' else key + '.')
            else:
                assert json.loads(raw)['answer'] == result['raw_response'].strip()
        counts['original_valid'] += old_valid
        counts['repaired_valid'] += new_valid
        counts['newly_valid'] += new_valid and not old_valid
        if not new_valid:
            remaining[error] += 1
        detail.append(dict(item_id=result['item_id'], old_status=result['status'],
                           termination=result['termination'], raw_response=raw,
                           status='ok' if new_valid else 'invalid', error=error, rule=rule))
    report = dict(N=len(original), counts=dict(counts), rules=dict(rules), remaining=dict(remaining),
                  original_valid_pct=counts['original_valid']/len(original)*100,
                  repaired_valid_pct=counts['repaired_valid']/len(original)*100,
                  all_original_valid_unchanged=True, all_unaccepted_unchanged=True,
                  choice_identity_and_other_fields_preserved=True, llm_requests=0,
                  scope='Offline candidate on the existing paused sample; protocol validity, not accuracy or full-v5 generalization. No live code or original terminals modified.')
    (ROOT / 'repair_comparison.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (ROOT / 'repaired_candidate.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in detail))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
