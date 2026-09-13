"""Synthetic responses are restricted to tests; no benchmark model fallback."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from common import digest, visible, question_text, valid_answer
from methods import imedrag, tcrag, parse_queries, parse_action, state_signal, final_json
from runtime import Session
from run import run_item, audit, main, resolve


ITEM = dict(item_id='test_only', question='Choose the symbol.', options={'A': 'alpha', 'B': 'beta'}, fixed_evidence=[], answer_format='single')


class Tokenizer:
    def encode(self, text, **kwargs):
        return list(map(ord, text))

    def decode(self, tokens):
        return ''.join(map(chr, tokens))


class Replay:
    tokenizer = Tokenizer()

    def __init__(self, outputs):
        self.outputs, self.calls = list(outputs), []

    def generate(self, messages, max_tokens, seed, entropy=False, **kwargs):
        self.calls.append(messages)
        result = []
        for message in messages:
            raw = self.outputs.pop(0)
            text, values = raw if isinstance(raw, tuple) else (raw, [0.1] * 4)
            result.append(dict(text=text, prompt_tokens=10, completion_tokens=4, finish_reason='stop',
                batch_seconds=.01, tokens=['x'] * 4, useful_positions=list(range(4)), entropies=values,
                score_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32'))
        return result


class Retrieval:
    def __init__(self):
        self.queries = []

    def retrieve(self, query):
        self.queries.append(query)
        return dict(documents=[dict(id='test_doc', title='test', content='TOOL_ONLY_MATERIAL')], scores=[1.])


def config(root, method='imedrag'):
    return dict(method=method, run_id='tests_only', seed=42, transport_retries=2,
                retry_backoff_seconds=[0, 0], format_repairs=1, n_rounds=2, n_queries=2,
                max_loop=8, topK=4, sigma=1.2,
                budgets={k: 1024 for k in ('query', 'parse', 'qa', 'final', 'format', 'action')},
                retrieval={'context_length': 30000, 'version': 'test'}, retrieval_cache=str(root / 'shared'))


class MethodsTest(unittest.TestCase):
    def test_final_literal_syntax_preserves_values_without_model_calls(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            model = Replay([])
            session = Session(root / 'syntax', config(root), model, Retrieval())
            for raw, expected in [("{'answer': 'A'}", {'answer': 'A'}),
                    ('```json\n{\'answer\': "Crohn\'s disease"}\n```', {'answer': "Crohn's disease"}),
                    ("{'answer': ['A', 'B']}", {'answer': ['A', 'B']})]:
                self.assertEqual(json.loads(final_json(raw, session, 'format')), expected)
            for raw in ["{'answer':'A','answer':'B'}", "{'answer': __import__('os').getcwd()}",
                        "{'answer': ('A', 'B')}", "{'answer': 'A'", '{"answer":"a"}']:
                self.assertEqual(final_json(raw, session, 'format'), raw)
            self.assertEqual(model.calls, [])
            self.assertEqual(len(session.trace), 3)
            self.assertTrue(all(e['llm_calls'] == 0 for e in session.trace))
            session.config['format_repairs'] = 0
            self.assertEqual(final_json("{'answer': 'A'}", session, 'format'), "{'answer': 'A'}")

    def test_imedrag_dependency_batch_order_and_resume(self):
        outputs = ['## Queries\n1. q1?\n2. q2?', '{"output":["q1?","q2?"]}',
                   '## Queries\nq3?\nq4?', '{"output": ["q3?", "q4?"]}',
                   '## Answer\nA', '{"answer":"A"}']
        class QAReplay(Replay):
            def generate(self, messages, *args, **kwargs):
                text = messages[0][-1]['content']
                if text.startswith('Here are the relevant documents:'):
                    import time
                    query = text.rsplit('\n', 1)[-1]
                    time.sleep(.02 if query == 'q1?' else 0)
                    self.calls.append(messages)
                    return Replay(['a' + query[1]]).generate(messages, *args, **kwargs)
                return super().generate(messages, *args, **kwargs)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            model, retriever = QAReplay(outputs), Retrieval()
            cfg = config(root)
            s = Session(root / 'stages', cfg, model, retriever)
            first = imedrag(ITEM, s)
            self.assertEqual(first['status'], 'ok')
            self.assertEqual(retriever.queries, ['q1?', 'q2?', 'q3?', 'q4?'])
            second_round = next(m[0][-1]['content'] for m in model.calls if 'Query: q1?\nAnswer: a1' in m[0][-1]['content'])
            self.assertIn('Query: q1?\nAnswer: a1\n\nQuery: q2?\nAnswer: a2', second_round)
            final = model.calls[-2][0][-1]['content']
            self.assertIn('Answer: a4', final)
            self.assertNotIn('TOOL_ONLY_MATERIAL', final)
            self.assertEqual(model.calls[-1][0][-1]['content'], "Output the answer in JSON: {'answer': your_answer (A/B)}")
            # Lose a request index after its successful attempt receipt commits.
            next((root / 'stages/requests').glob('*.json')).unlink()
            resumed_model = Replay([])
            resumed = imedrag(ITEM, Session(root / 'stages', cfg, resumed_model, Retrieval()))
            self.assertEqual(first, resumed)
            self.assertEqual(resumed_model.calls, [])

    def test_query_extractor_output_matches_upstream_policy(self):
        self.assertEqual(parse_queries('{"output":["1. rewritten query?", ""]}', 'different source'),
                         ([dict(index=0, query='rewritten query?')], [1]))
        self.assertEqual(parse_queries('{"output":["q2?", "q1?"]}', 'q1? q2?')[0],
                         [dict(index=0, query='q2?'), dict(index=1, query='q1?')])
        for raw in ['{"output":null}', '{"output":[1]}', '{"other":[]}']:
            with self.assertRaises(ValueError):
                parse_queries(raw, 'source')

    def test_skipped_query_rounds_do_not_invalidate_final_answer(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            outputs = ['No queries.', 'No queries.', '## Answer\nA', '{"answer":"A"}']
            result = imedrag(ITEM, Session(root / 'skip', config(root), Replay(outputs), Retrieval()))
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['executed_queries'], 0)
            self.assertEqual(len(result['issues']), 2)

    def test_run_location_does_not_change_generation_seed(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            one, two = config(root), dict(config(root), run_id='different_run', input_path='different_manifest')
            a, b = Session(root / 'a', one, Replay(['x']), Retrieval()), Session(root / 'b', two, Replay(['x']), Retrieval())
            a.call('query/0', [dict(role='user', content='same input')])
            b.call('query/0', [dict(role='user', content='same input')])
            self.assertEqual(next(iter(a.receipts)), next(iter(b.receipts)))

    def test_tc_stack_summary_backtrack_and_acceptance_boundary(self):
        outputs = [('Thought: investigate\nAction: DOC_RAG\nAction Input: {"query":"q"}\nObservation: FAKE_TOOL\nFinal Answer: {"answer":"B"}', [2.] * 4),
                   'Summary: condensed evidence', 'Backtrack: summary is irrelevant',
                   'Final Answer: {"answer":"A"}', 'Final Answer: {"answer":"A"}']
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            model = Replay(outputs)
            s = Session(root / 'tc', config(root, 'tcrag'), model, Retrieval())
            r = tcrag(ITEM, s)
            self.assertEqual((r['status'], r['steps'], r['backtracks'], r['summaries']), ('ok', 5, 1, 1))
            traces = [x for x in s.trace if x['kind'] == 'tc_action']
            self.assertEqual(traces[3]['rejected'], 'minimum_steps')
            self.assertTrue(traces[4]['accepted'])
            self.assertEqual(traces[2]['state_after'], 8.)
            self.assertIn('TOOL_ONLY_MATERIAL', model.calls[1][0][-1]['content'])
            self.assertNotIn('TOOL_ONLY_MATERIAL', model.calls[2][0][-1]['content'])
            self.assertNotIn('condensed evidence', model.calls[3][0][-1]['content'])
            self.assertNotIn('FAKE_TOOL', json.dumps(model.calls))

    def test_tc_early_final_preserves_its_thought_prefix(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            model = Replay(['Thought: KEEP_EARLY_REASON\nFinal Answer: {"answer":"A"}'] +
                           ['Thought: continue'] * 3 + ['Final Answer: {"answer":"A"}'])
            s = Session(root / 'tc', config(root, 'tcrag'), model, Retrieval())
            result = tcrag(ITEM, s)
            self.assertIn('KEEP_EARLY_REASON', model.calls[1][0][-1]['content'])
            self.assertEqual((result['status'], result['steps']), ('ok', 5))
            events = [e for e in s.trace if e['kind'] == 'tc_action']
            self.assertEqual(events[0]['rejected'], 'minimum_steps')
            self.assertEqual(events[0]['state_after'], .4)

    def test_tc_high_entropy_and_budget_never_fabricate_answer(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg = config(root, 'tcrag')
            high = [('Final Answer: {"answer":"A"}', [1.] * 4)] * 8
            s = Session(root / 'tc', cfg, Replay(high), Retrieval())
            r = tcrag(ITEM, s)
            self.assertEqual((r['status'], r['termination'], r['returned_kind']), ('invalid', 'budget_exhausted', 'thought'))
            self.assertEqual([x for x in s.trace if x['kind'] == 'tc_action'][-1]['rejected'], 'entropy_threshold')
            cfg['max_loop'] = 1
            model = Replay(['Action: DOC_RAG\nAction Input: {"query":"q"}'])
            r = tcrag(ITEM, Session(root / 'tc2', cfg, model, Retrieval()))
            self.assertEqual(r['returned_kind'], 'tool_observation')
            self.assertEqual(r['status'], 'invalid')

    def test_state_restoration_isolation_and_original_immutable(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg = config(root, 'tcrag')
            cfg['max_loop'] = 3
            for i in range(2):
                s = Session(root / str(i), cfg, Replay([('Thought: T', [1.] * 4), 'Backtrack: remove T', 'Backtrack: cannot remove Q']), Retrieval())
                tcrag(ITEM, s)
                traces = [x for x in s.trace if x['kind'] == 'tc_action']
                self.assertEqual(traces[0]['state_before'], 100000.)
                self.assertEqual(traces[1]['state_after'], 100000.)
                self.assertEqual(len(traces[2]['stack_after']), 1)

    def test_gold_whitelist_evidence_and_cache_identity(self):
        one = dict(ITEM, fixed_evidence=['real evidence'], gold='GOLD_SENTINEL', rationale='PAIR_SENTINEL', evaluation_labels=['CLASS_SENTINEL'])
        two = dict(one, fixed_evidence=['intervened evidence'])
        for marker in ('GOLD_SENTINEL', 'PAIR_SENTINEL', 'CLASS_SENTINEL'):
            self.assertNotIn(marker, question_text(one))
        self.assertNotEqual(question_text(one), question_text(two))
        self.assertNotEqual(digest(visible(one)), digest(visible(two)))
        self.assertIn('real evidence', question_text(one))

    def test_entropy_selector_keeps_upstream_whitespace_and_boundaries(self):
        r = dict(tokens=['Final', ' Answer', ':', ' A', '.'], entropies=[1., 2., 3., 4., 5.], useful_positions=[0, 1, 2, 4, 5], score_convention='full_vocab_HF_post_processors_nats_eps1e-10_fp32')
        self.assertEqual(state_signal(r)['value'], 15.)
        r['tokens'][1] = 'Answer'
        self.assertEqual(state_signal(r)['selected_positions'], [4, 5])
        self.assertEqual(state_signal(r)['value'], 9.)
        r['entropies'] = [float('nan')] * 5
        with self.assertRaises(ValueError):
            state_signal(r)

    def test_failure_keeps_denominator_and_terminal_resume(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg = config(root, 'tcrag')
            a = run_item(ITEM, root, cfg, Replay(['Thought:']), Retrieval())
            self.assertEqual(a['status'], 'invalid')
            self.assertEqual(run_item(ITEM, root, cfg, Replay([]), Retrieval()), a)
            report = audit(root, [ITEM, dict(ITEM, item_id='pending')])
            self.assertEqual((report['N_planned'], report['N_invalid'], report['N_pending']), (2, 1, 1))

    def test_resume_rejects_worker_count_change_before_model_loading(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg_path, inputs, run_dir = root / 'config.json', root / 'inputs.jsonl', root / 'run'
            cfg_path.write_text(json.dumps(config(root, 'tcrag')))
            inputs.write_text(json.dumps(ITEM) + '\n')
            resolve(cfg_path, inputs, run_dir)
            (run_dir / 'batching.json').write_text(json.dumps({'workers': 4}))
            argv = ['run.py', 'tcrag', '--config', str(cfg_path), '--inputs', str(inputs),
                    '--run-dir', str(run_dir), '--workers', '2']
            with patch.object(sys, 'argv', argv), self.assertRaisesRegex(ValueError, 'run_workers_changed'):
                main()

    def test_unlabelled_final_still_requires_steps_entropy_and_valid_format(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            for name, outputs, expected in [
                ('low', ['{"answer":"A"}'] * 5, ('ok', 'accepted', 5)),
                ('high', [('{"answer":"A"}', [1.] * 4)] * 8, ('invalid', 'budget_exhausted', 8)),
                ('malformed', ['not an answer'] * 5, ('invalid', 'accepted', 5)),
            ]:
                session = Session(root / name, config(root, 'tcrag'), Replay(outputs), Retrieval())
                result = tcrag(ITEM, session)
                self.assertEqual((result['status'], result['termination'], result['steps']), expected)
                actions = [e for e in session.trace if e['kind'] == 'tc_action']
                self.assertEqual(actions[0]['rejected'], 'minimum_steps')
                self.assertEqual(len([e for e in session.trace if e['kind'] == 'tc_output_normalized']), result['steps'])
                self.assertEqual(actions[0]['state_signal']['selected_tokens'], ['x'] * 4)

    def test_resume_rejects_worker_count_change_before_model_loading(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg_path, inputs, run_dir = root / 'config.json', root / 'inputs.jsonl', root / 'run'
            cfg_path.write_text(json.dumps(config(root, 'tcrag')))
            inputs.write_text(json.dumps(ITEM) + '\n')
            resolve(cfg_path, inputs, run_dir)
            (run_dir / 'batching.json').write_text(json.dumps({'workers': 4}))
            argv = ['run.py', 'tcrag', '--config', str(cfg_path), '--inputs', str(inputs),
                    '--run-dir', str(run_dir), '--workers', '2']
            with patch.object(sys, 'argv', argv), self.assertRaisesRegex(ValueError, 'run_workers_changed'):
                main()

    def test_native_output_spaces(self):
        self.assertIsNone(valid_answer('{"answer":["A","B"]}', dict(ITEM, answer_format='multi')))
        self.assertIsNotNone(valid_answer('{"answer":"A"}', dict(ITEM, answer_format='multi')))
        self.assertIsNone(valid_answer('{"answer":"uncertainty"}', dict(ITEM, answer_format='relation', options={})))
        self.assertIsNone(valid_answer('{"answer":"new diagnosis"}', dict(ITEM, answer_format='diagnosis', options={})))
        self.assertIsNotNone(valid_answer('{"answer":"A"} {"answer":"B"}', ITEM))


if __name__ == '__main__':
    unittest.main()
