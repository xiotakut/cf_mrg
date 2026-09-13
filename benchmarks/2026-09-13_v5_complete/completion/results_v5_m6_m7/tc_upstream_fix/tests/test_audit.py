"""The offline audit must reject an altered active-context receipt."""
import copy
import tempfile
import unittest
from pathlib import Path
from test_methods import ITEM, Replay, Retrieval, config
from methods import tcrag
from runtime import Session
from report import trace_audit
from common import atomic, digest
from cost import pilot_cost


class AuditTest(unittest.TestCase):
    def test_reused_prefix_is_not_charged_twice(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            copied = []
            for stage in ('query/0', 'format'):
                spec = dict(kind='llm', stage=stage)
                key = digest(spec)
                response = dict(prompt_tokens=10, completion_tokens=4, batch_seconds=2.,
                                engine_batch_id=stage, engine_batch_seconds=2.)
                atomic(root / 'items/test/requests' / (key + '.json'),
                       dict(spec=spec, status='ok', result=[response]))
                atomic(root / 'items/test/attempts' / key / '00.json',
                       dict(status='ok'))
                if stage != 'format':
                    copied.append(dict(item_id='test', request_key=key))
            atomic(root / 'cache_provenance.json', dict(copied_requests=copied))
            result = pilot_cost(root)
            self.assertEqual(result['llm_requests_with_saved_output'], 1)
            self.assertEqual(result['prompt_tokens'], 10)
            self.assertEqual(result['known_engine_seconds'], 2.)
            self.assertEqual(result['attempt_statuses'], {'ok': 1})
            self.assertEqual(result['reused_stage_requests_excluded'], 1)

    def test_real_receipt_shape_and_tampered_prompt(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            cfg = dict(config(root, 'tcrag'), model_id='synthetic_test', weight_id='test', tokenizer_id='test')
            replay = Replay(['Thought: continue'] * 4 + ['Final Answer: {"answer":"A"}'])
            session = Session(root, cfg, replay, Retrieval())
            result = tcrag(ITEM, session)
            receipts = list(session.receipts.values())
            for receipt in receipts:
                for response in receipt['result']:
                    response.update(model={k: cfg[k] for k in ('model_id', 'weight_id', 'tokenizer_id')},
                                    prompt_token_ids=[0] * response['prompt_tokens'])
            checks = trace_audit(ITEM, result, session.trace, receipts, cfg)
            self.assertEqual(checks['active_stack_prompt_and_required_evidence'], 5)
            self.assertEqual(checks['acceptance_boundary'], 1)
            altered = copy.deepcopy(receipts)
            altered[-1]['spec']['messages'][0][-1]['content'] += '\nUNPERMITTED_PAIR_SENTINEL'
            with self.assertRaises(AssertionError):
                trace_audit(ITEM, result, session.trace, altered, cfg)


if __name__ == '__main__':
    unittest.main()
