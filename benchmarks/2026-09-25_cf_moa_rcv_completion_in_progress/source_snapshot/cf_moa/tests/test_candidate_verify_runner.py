"""Candidate-arm dispatch, explicit failure, and durable smoke reuse.

These exercise the real runner, verifier, ModelSession and SQLite journal with
synthetic one-token transport results. They are not model-quality evidence.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cf_moa.agents import a5_candidate_verify as verifier
from cf_moa.contracts import digest
from cf_moa.evaluation.effect_first_runner import ResearchJournal, execute
from cf_moa.evaluation.journal import JournalBackend
from cf_moa.tests.test_a5_candidate_verify import fixture, scores_for
from cf_moa.tests.test_incremental_runner import FixtureModel


ARMS = ('a5_candidate_only', 'a5_candidate_with_rationales')


class ScoreTransport(FixtureModel):
    """Only replace transport; keep production score/session/journal behavior."""

    def __init__(self, responses, *, fail_first_preflight=False):
        super().__init__(responses)
        self.fail_first_preflight = fail_first_preflight
        self.preflight_count = 0

    def preflight(self, request):
        self.preflight_count += 1
        if self.fail_first_preflight and self.preflight_count == 1:
            raise ValueError('Deterministic fixture score rejected before submission')

    def __call__(self, request):
        if request['kind'] != 'score' or request['max_tokens'] != 1:
            raise AssertionError('Candidate runner must only request one-token scores')
        result = super().__call__(request)
        # FixtureModel models a five-token generation; this transport emits one
        # score token. The same event object is retained in physical_calls.
        result.events[0]['output_tokens'] = 1
        return result


class CandidateVerifyRunnerTests(unittest.TestCase):
    def scope(self, count=1, arms=ARMS):
        packets, bases, proposals, tasks = {}, {}, {}, []
        for index in range(count):
            packet, saved = fixture()
            packet.request_id = 'runner_fixture_' + str(index)
            saved['input_hash'] = packet.input_hash
            proposal_key = packet.request_id + ':F'
            packets[packet.request_id] = packet
            native = deepcopy(saved['native_proposal'])
            bases[packet.request_id] = dict(native_answer=native, native_valid=True,
                base_answer_ref=digest(native), input_hash=packet.input_hash)
            proposals[proposal_key] = saved
            for arm in arms:
                tasks.append(dict(task_id=packet.request_id + ':' + arm,
                    request_id=packet.request_id, arm=arm, proposal_key=proposal_key))
        return packets, bases, proposals, tasks

    def test_both_arms_dispatch_to_real_candidate_module_and_return_whole_response(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            packets, bases, proposals, tasks = self.scope()
            transport = ScoreTransport(scores_for([.2, .9, .3]) * 2)
            journal = ResearchJournal(output / 'journal.sqlite', {'synthetic_test': True})
            try:
                backend = JournalBackend(journal, lambda: transport)
                with patch.object(verifier, 'run', wraps=verifier.run) as operation, \
                     patch('cf_moa.agents.a5_premise.run',
                           side_effect=AssertionError('Old ordinary reanswer must not run')) as old:
                    status = execute(packets, bases, tasks, proposals, backend, journal,
                                     output, 'M5', {'seed': 42})
                old.assert_not_called()
                self.assertEqual([call.kwargs['include_rationales']
                                  for call in operation.call_args_list], [False, True])
                self.assertEqual(status['status'], 'complete')
                self.assertEqual(status['complete'], 2)
                self.assertEqual(status['verification_failed'], 0)
                self.assertEqual(status['verification_fallback_saved_F'], 0)
                self.assertEqual(len(transport.sent), 12)
                expected = json.loads(next(iter(proposals.values()))['trace']['responses'][0])
                for task in tasks:
                    saved = journal.output(task['task_id'])
                    self.assertEqual(saved['verification_status'], 'verified_candidate_selection')
                    self.assertEqual(saved['result']['native_answer'], expected)
                    self.assertEqual(saved['result']['native_answer']['errors'][0]['correction'],
                                     'FULL_AUX_B_0')
                    self.assertEqual(saved['result']['new_answer_generation_calls'], 0)
                    self.assertEqual(len(saved['model_callbacks']), 6)
                self.assertNotIn('UNTRUSTED_B_0', json.dumps(transport.sent[:6]))
                self.assertIn('UNTRUSTED_B_0', json.dumps(transport.sent[6:]))
                self.assertEqual(status['request_counts']['submitted'], 12)
            finally:
                journal.db.close()

    def test_local_score_failure_keeps_saved_F_and_failure_count_then_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            packets, bases, proposals, tasks = self.scope(2, arms=(ARMS[0],))
            transport = ScoreTransport(
                scores_for([.2, .9, .3])[1:] + scores_for([.2, .9, .3]),
                fail_first_preflight=True)
            journal = ResearchJournal(output / 'journal.sqlite', {'synthetic_test': True})
            try:
                backend = JournalBackend(journal, lambda: transport)
                with patch('cf_moa.agents.a5_premise.run',
                           side_effect=AssertionError('No ordinary reanswer fallback')):
                    status = execute(packets, bases, tasks, proposals, backend, journal,
                                     output, 'M4', {'seed': 42})
                first, second = [journal.output(task['task_id']) for task in tasks]
                self.assertEqual(status['status'], 'complete')
                self.assertEqual((status['planned'], status['complete'], status['not_submitted']),
                                 (2, 2, 0))
                self.assertTrue(status['complete_means_execution_finished_not_verification_success'])
                self.assertEqual(status['verification_failed'], 1)
                self.assertEqual(status['verification_fallback_saved_F'], 1)
                self.assertIsNone(status['first_systemic_error'])
                self.assertEqual(first['verification_status'], 'technical_failure')
                self.assertTrue(first['verification_failed'])
                self.assertTrue(first['verification_fallback_saved_F'])
                self.assertEqual(first['result']['native_answer'],
                                 proposals[tasks[0]['proposal_key']]['native_proposal'])
                self.assertEqual(first['model_callbacks'][0]['status'], 'failed')
                self.assertEqual(first['result']['trace']['errors'][0]['error_type'], 'ValueError')
                self.assertEqual(second['verification_status'], 'verified_candidate_selection')
                self.assertFalse(second['verification_failed'])
                self.assertEqual(second['result']['native_answer']['answer_choice'], 'B')
                self.assertEqual(status['cost']['failed_attempts'], 1)
                self.assertEqual(status['request_counts']['attempted'], 12)
                self.assertEqual(status['request_counts']['submitted'], 11)
                self.assertEqual(status['request_counts']['in_flight_state_unknown'], 0)
            finally:
                journal.db.close()

    def test_engine_initialization_failure_stops_after_one_attempt_and_preserves_first_error(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            packets, bases, proposals, tasks = self.scope(2)
            transport = ScoreTransport([])
            journal = ResearchJournal(output / 'journal.sqlite', {'synthetic_test': True})
            message = 'Engine core initialization failed. See root cause above.'
            try:
                backend = JournalBackend(journal, lambda: transport)
                with patch.object(transport, 'start', side_effect=RuntimeError(message)) as start, \
                     patch.object(verifier, 'verifier_messages', wraps=verifier.verifier_messages) as messages:
                    status = execute(packets, bases, tasks, proposals, backend, journal,
                                     output, 'M4', {'seed': 42})
                self.assertEqual(start.call_count, 1)
                self.assertEqual(messages.call_count, 1)
                self.assertEqual(transport.sent, [])
                self.assertEqual(status['status'], 'stopped_on_systemic_error')
                self.assertEqual((status['planned'], status['complete'], status['failed'],
                                  status['not_submitted']), (4, 0, 1, 3))
                first = status['first_systemic_error']
                self.assertEqual((first['request_id'], first['ordinal']), (tasks[0]['task_id'], 0))
                self.assertEqual(first['error_type'], 'RuntimeError')
                self.assertEqual(first['message'], message)
                self.assertEqual(first['error_category'], 'infrastructure')
                self.assertEqual(first['counts']['attempted'], 1)
                self.assertEqual(first['counts']['submitted'], 0)
                self.assertEqual(first['counts']['completed'], 0)
                self.assertEqual(first['counts']['in_flight'], 0)
                self.assertEqual(status['cost']['failed_attempts'], 1)
                self.assertEqual(status['cost']['new_model_requests'], 0)
                self.assertEqual(status['cost']['unresolved_model_usage'], 0)
                self.assertEqual(status['cost']['live_input_tokens'], 0)
                self.assertEqual(status['cost']['live_output_tokens'], 0)
                call = journal.lookup(tasks[0]['task_id'], 0)
                self.assertEqual((call['status'], call['phase']), ('failed', 'initializing'))
                self.assertEqual(json.loads(call['physical']), [])
                saved = journal.output(tasks[0]['task_id'])
                self.assertEqual((saved['status'], saved['error_type'], saved['error']),
                                 ('failed', 'RuntimeError', message))
                self.assertIsNone(saved['result']['native_answer'])
                self.assertEqual(len(saved['model_callbacks']), 1)
                self.assertTrue(all(journal.output(task['task_id']) is None for task in tasks[1:]))
                self.assertEqual(json.loads((output / 'first_error.json').read_text()), first)
            finally:
                journal.db.close()

    def test_full_execute_reuses_saved_smoke_and_resumed_terminal_outputs_without_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            packets, bases, proposals, tasks = self.scope(2)
            transport = ScoreTransport(scores_for([.2, .9, .3]) * 4)
            plan = {'synthetic_test': True, 'tasks': tasks}
            path = output / 'journal.sqlite'
            journal = ResearchJournal(path, plan)
            try:
                backend = JournalBackend(journal, lambda: transport)
                execute(packets, bases, tasks[:2], proposals, backend, journal,
                        output, 'M5', {'seed': 42})
                smoke = [journal.output(task['task_id']) for task in tasks[:2]]
                self.assertEqual(len(transport.sent), 12)
                with patch.object(verifier, 'run', wraps=verifier.run) as operation:
                    status = execute(packets, bases, tasks, proposals, backend, journal,
                                     output, 'M5', {'seed': 42})
                self.assertEqual(operation.call_count, 2)
                self.assertTrue(all(call.args[0].request_id == 'runner_fixture_1'
                                    for call in operation.call_args_list))
                self.assertEqual(len(transport.sent), 24)
                self.assertEqual(status['complete'], 4)
                self.assertEqual([journal.output(task['task_id']) for task in tasks[:2]], smoke)
                all_outputs = [journal.output(task['task_id']) for task in tasks]
                persisted_cost = journal.cost()
            finally:
                journal.db.close()

            journal = ResearchJournal(path, plan, resume=True)
            try:
                backend = JournalBackend(journal,
                    lambda: self.fail('Completed results must not initialize transport'))
                with patch.object(verifier, 'run',
                                  side_effect=AssertionError('Saved smoke/result must not rerun')) as operation:
                    status = execute(packets, bases, tasks, proposals, backend, journal,
                                     output, 'M5', {'seed': 42})
                operation.assert_not_called()
                self.assertIsNone(backend.backend)
                self.assertEqual(status['complete'], 4)
                self.assertEqual(status['cost'], persisted_cost)
                self.assertEqual(status['request_counts']['submitted'], 24)
                self.assertEqual([journal.output(task['task_id']) for task in tasks], all_outputs)
            finally:
                journal.db.close()


if __name__ == '__main__':
    unittest.main()
