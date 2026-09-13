"""Checks for typed feedback and bounded output correction in candidate v2."""
import test_control
from test_control import Fake, ITEM
from candidate_typed import tcrag


def main():
    test_control.tcrag = tcrag
    test_control.main()
    f = Fake(['Thought: check'] * 6 + ['Final Answer: {"answer":"Example diagnosis"}'])
    result = tcrag(dict(ITEM, options={}, answer_format='diagnosis'), f)
    notice = f.calls[-1][-1]['content'].split('Protocol feedback: ')[-1]
    assert 'one concise most likely diagnosis label' in notice
    assert 'only the native option key' not in notice
    assert result['status'] == 'ok'
    f = Fake(['Thought: check'] * 4 + ['Final Answer: {"answer":"A"}', 'Final Answer: {"answer":"A","errors":[]}'])
    result = tcrag(dict(ITEM, answer_format='robustness_single'), f)
    assert result['status'] == 'ok' and result['steps'] == 6
    assert any(e['kind'] == 'tc_invalid_output_continued' for e in f.events)
    f = Fake(['Thought: check'] * 7 + ['Final Answer: {"answer":"A"}'])
    result = tcrag(dict(ITEM, answer_format='robustness_single'), f)
    assert result['status'] == 'invalid' and len(f.calls) == 8
    print('Typed diagnosis and bounded output correction: passed.')


if __name__ == '__main__':
    main()
