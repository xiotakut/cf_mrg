from copy import deepcopy
import itertools
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cf_moa.controller import minimal_operations as minimal
from cf_moa.tests.test_contracts import packet, FixtureBackend
from cf_moa.tests.test_support_and_views import current_packet
from cf_moa.tools.adapters import ModelSession
from cf_moa.tools.legacy import r123_module
from cf_moa.contracts import AgentProposal
from cf_moa.tests.test_a5_premise import fixture as f_fixture


def resolved(item, initial, states):
    options = {k: dict(state=v, paths=[dict(rule_id=k, state=v)]) for k, v in states.items()}
    answer = r123_module('r2_program_head').assemble(item, initial, options)
    return dict(answer=initial if answer is None else answer, applied=answer is not None,
        scope='general', action='avoid', facts={}, options=options, reason='fixture')


class MinimalOperationsTests(unittest.TestCase):
    def test_all_ordinary_partitions_and_initial_sets_match_old_assembly(self):
        item = packet().native_input
        cases = 0
        for states in itertools.product(('MET', 'CONTRADICTED', 'UNKNOWN'), repeat=2):
            for selected in (['A'], ['B'], ['A', 'B'], ('B',)):
                with self.subTest(states=states, selected=selected):
                    result = resolved(item, selected, dict(zip(('A', 'B'), states)))
                    record = minimal.rule_operations(item, selected, result)
                    self.assertTrue(record['formula_checked'])
                    self.assertEqual(record['old_answer'], result['answer'])
                    cases += 1
        self.assertEqual(cases, 36)

    def test_none_initial_and_invalid_initial_use_original_policy(self):
        item = packet().native_input
        for initial in (['C'], ['C', 'A'], ['foreign'], [], None, 'A'):
            result = resolved(item, initial, dict(A='MET', B='UNKNOWN'))
            record = minimal.rule_operations(item, initial, result)
            self.assertFalse(record['formula_checked'])
            self.assertEqual(record['old_answer'], result['answer'])
        self.assertEqual(minimal.rule_operations(item, ['C'],
            resolved(item, ['C'], dict(A='MET', B='UNKNOWN')))['A1']['add'], ['A'])

    def test_no_none_and_empty_entity_result_keeps_old_no_proposal(self):
        item = deepcopy(packet().native_input)
        del item['options']['C']
        result = resolved(item, ['A'], dict(A='CONTRADICTED', B='CONTRADICTED'))
        record = minimal.rule_operations(item, ['A'], result)
        self.assertFalse(record['formula_checked'])
        self.assertFalse(result['applied'])
        self.assertEqual(record['old_answer'], ['A'])
        self.assertNotIn('formula_entities', record)

    def test_a_failed_path_does_not_remove_independent_supported_option(self):
        item = packet().native_input
        result = resolved(item, ['A', 'B'], dict(A='MET', B='CONTRADICTED'))
        result['options']['A']['paths'].append(dict(rule_id='independent_failed', state='CONTRADICTED'))
        record = minimal.rule_operations(item, ['A', 'B'], result)
        self.assertEqual(record['A2']['remove'], ['B'])
        self.assertEqual(len(record['A2']['invalid_paths']['A']), 1)
        self.assertEqual(record['old_answer'], ['A'])

    def test_scoped_documented_exception_execution_is_not_reinterpreted(self):
        item = packet().native_input
        result = resolved(item, ['B'], dict(A='MET', B='UNKNOWN'))
        result['scope'] = 'renal'
        result['options']['A']['paths'][0].update(exception='UNKNOWN', used_default_recommendation=True)
        before = deepcopy(result)
        record = minimal.rule_operations(item, ['B'], result)
        self.assertEqual(record['A1']['add'], ['A'])
        self.assertEqual(record['A2']['inherited_unknown'], ['B'])
        self.assertEqual(result, before)
        self.assertTrue(record['A1']['established_support']['A']['paths'][0]['used_default_recommendation'])

    def test_invalid_facts_do_not_gain_a_fabricated_state_partition(self):
        result = dict(answer=['B'], applied=False, reason='invalid_fact_extraction')
        record = minimal.rule_operations(packet().native_input, ['B'], result)
        self.assertIsNone(record['A1']['add'])
        self.assertNotIn('states', record)
        self.assertFalse(record['formula_checked'])

    def test_saved_result_drift_is_rejected(self):
        p = packet()
        result = resolved(p.native_input, ['B'], dict(A='MET', B='CONTRADICTED'))
        result['answer'] = ['B']
        with self.assertRaisesRegex(ValueError, 'adopted assembler'):
            minimal.rule_operations(p.native_input, ['B'], result)

    def test_actual_rule_entry_extracts_once_and_never_runs_aggregator(self):
        p = packet()
        raw = json.dumps(dict(facts=dict(age_years=dict(value=78, evidence_ids=['S0']),
                                       crcl=dict(value=55, evidence_ids=['S0']))))
        backend = FixtureBackend([raw])
        session = ModelSession(p, backend)
        row = minimal.run(p, session, method='M4')
        self.assertEqual(row['native_proposal'], ['A'])
        self.assertEqual(row['operations']['roles'], ['A1', 'A2'])
        self.assertEqual(row['operations']['shared_rule_operations']['A1']['add'], ['A'])
        self.assertEqual(row['operations']['shared_rule_operations']['A2']['remove'], ['B'])
        self.assertEqual(len(backend.requests), 1)
        self.assertEqual(backend.requests[0]['temperature'], 0.0)
        self.assertEqual(backend.requests[0]['max_tokens'], 2048)
        self.assertFalse(row['operations']['global_generation_aggregator'])

    def test_f_entry_returns_complete_old_native_object_without_rewrite(self):
        p = current_packet()
        session = ModelSession(p, FixtureBackend([]))
        native = dict(answer_choice='A', step_by_step_thinking='verbatim', errors=['keep'])
        proposal = SimpleNamespace(native_proposal=native, trace={'paths': ['unchanged']}, variant='original_F')
        with patch.object(minimal.old_f, 'run_legacy', return_value=proposal) as old:
            row = minimal.run(p, session, method='M5')
        old.assert_called_once_with(p, session)
        self.assertEqual(row['native_proposal'], native)
        self.assertEqual(row['operations']['roles'], ['A5'])
        self.assertEqual(row['original_component_variant'], 'original_F')

    def test_f_switch_reuses_exact_ordinary_request_and_preserves_auxiliary_fields(self):
        p, saved = f_fixture()
        proposal = AgentProposal('A5', saved['variant'], p.input_hash, 'supported',
            saved['native_proposal'], trace=saved['trace'])
        backend = FixtureBackend(['{"answer_choice":"B","reason":"short"}'])
        session = ModelSession(p, backend)
        with patch.object(minimal.old_f, 'run_legacy', return_value=proposal):
            row = minimal.run(p, session, method='M4',
                f_disagreement_reanswer=True, f_reanswer_seed=43)
        self.assertEqual(row['variant'], minimal.F_REANSWER_VARIANT)
        self.assertEqual(row['native_proposal']['answer_choice'], 'B')
        self.assertEqual(row['native_proposal']['errors'], saved['native_proposal']['errors'])
        self.assertEqual(row['trace'], saved['trace'])
        self.assertEqual(len(backend.requests), 1)
        self.assertEqual(backend.requests[0], minimal.f_reanswer.request(p, ['A', 'B'],
            control=True, config={'seed': 43}))
        self.assertEqual(row['cost']['physical_model_requests'], 1)

    def test_f_switch_no_disagreement_is_zero_call_complete_passthrough(self):
        p, saved = f_fixture()
        saved['trace']['predictions'] = ['A', 'A']
        proposal = AgentProposal('A5', saved['variant'], p.input_hash, 'supported',
            saved['native_proposal'], trace=saved['trace'])
        session = ModelSession(p, FixtureBackend([]))
        with patch.object(minimal.old_f, 'run_legacy', return_value=proposal):
            row = minimal.run(p, session, method='M5', f_disagreement_reanswer=True)
        self.assertEqual(row['native_proposal'], saved['native_proposal'])
        self.assertEqual(session.calls, [])

    def test_failed_f_reanswer_remains_unavailable_after_single_original_repair(self):
        p, saved = f_fixture()
        proposal = AgentProposal('A5', saved['variant'], p.input_hash, 'supported',
            saved['native_proposal'], trace=saved['trace'])
        session = ModelSession(p, FixtureBackend(['unreadable', 'still unreadable']))
        with patch.object(minimal.old_f, 'run_legacy', return_value=proposal):
            row = minimal.run(p, session, method='M4', f_disagreement_reanswer=True)
        self.assertIsNone(row['native_proposal'])
        self.assertEqual(len(session.calls), 2)
        self.assertTrue(all(call['request']['max_tokens'] == 512 for call in session.calls))
        self.assertEqual(row['cost']['physical_model_requests'], 2)

    def test_catalog_entry_preserves_adopted_mapped_label(self):
        p = packet()
        p.native_input['answer_format'] = 'diagnosis'
        native = 'Exact adopted catalogue label'
        result = dict(answer=native, used_original=False, branch='catalog_vote')
        session = ModelSession(p, FixtureBackend([]))
        with patch.object(minimal.legacy_router, 'optimize', return_value=result) as old:
            row = minimal.run(p, session, method='M4')
        self.assertEqual(old.call_count, 1)
        self.assertEqual(row['native_proposal'], native)
        self.assertEqual(row['operations']['roles'], ['A3'])
        self.assertEqual(session.calls, [])

    def test_a4_passes_original_executor_output_without_new_readout(self):
        p = packet()
        session = ModelSession(p, FixtureBackend([]))
        native = dict(answer=19.625, unit='mg/dL', original_detail=['preserve'])
        proposal = SimpleNamespace(native_proposal=native, trace={'route': 'executed'}, variant='frozen_physiology_v2_typed_patch')
        with patch.object(minimal.strong_legacy, 'select', return_value=('A4', 'complete_supplied_model_capability')):
            with patch.object(minimal.a4, 'run', return_value=proposal) as old:
                row = minimal.run(p, session, method='M4')
        old.assert_called_once_with(p, session, method='M4')
        self.assertEqual(row['native_proposal'], native)
        self.assertEqual(row['trace'], proposal.trace)
        self.assertEqual(row['operations']['roles'], ['A4'])

    def test_f_switch_never_calls_reanswer_on_a4_branch(self):
        p = packet()
        session = ModelSession(p, FixtureBackend([]))
        native = dict(answer=19.625, unit='mg/dL')
        proposal = SimpleNamespace(native_proposal=native, trace={}, variant='adopted_a4')
        with patch.object(minimal.strong_legacy, 'select', return_value=('A4', 'complete_supplied_model_capability')):
            with patch.object(minimal.a4, 'run', return_value=proposal):
                with patch.object(minimal.f_reanswer, 'run') as reanswer:
                    row = minimal.run(p, session, method='M4', f_disagreement_reanswer=True)
        reanswer.assert_not_called()
        self.assertEqual(row['native_proposal'], native)
        self.assertFalse(row['f_ordinary_reanswer']['eligible_branch'])
        self.assertEqual(session.calls, [])

    def test_passthrough_requires_bound_complete_original_not_fabricated_explanation(self):
        p = packet()
        p.native_input['question'] = 'A 48-year-old adult asks about medicine.'
        p.question = p.native_input['question']
        session = ModelSession(p, FixtureBackend([]))
        with self.assertRaisesRegex(ValueError, 'complete saved initial'):
            minimal.run(p, session, method='M4')
        with self.assertRaisesRegex(ValueError, 'baseline value'):
            minimal.run(p, session, method='M4', initial_native={'answer_choice': ['A']})
        self.assertEqual(session.calls, [])

    def test_passthrough_retains_original_invalid_answer_without_new_generation(self):
        p = packet()
        p.native_input['answer_format'] = 'multi'
        p.native_input['question'] = 'A 48-year-old adult asks about medicine.'
        p.question = p.native_input['question']
        p.baseline_answer = ['invalid']
        original = {'answer_choice': ['invalid'], 'step_by_step_thinking': 'keep'}
        session = ModelSession(p, FixtureBackend([]))
        row = minimal.run(p, session, method='M4', initial_native=original)
        self.assertEqual(row['native_proposal'], original)
        self.assertEqual(row['operations']['roles'], [])
        self.assertEqual(session.calls, [])


if __name__ == '__main__':
    unittest.main()
