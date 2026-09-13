import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from common import atomic, digest, visible
from score import score_run, dependencies, cluster_interval


class ScoringTest(unittest.TestCase):
    def test_failure_denominator_no_gold_rescue_and_no_llm(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            items = [dict(item_id=str(i), question='case' + str(i), options={'A': 'a', 'B': 'b'}, fixed_evidence=[], answer_format='single') for i in range(3)]
            labels = [dict(item_id=i['item_id'], gold='A', unit_id='unit' + i['item_id'], group_id='case', resource_id='test_only', record_id=i['item_id'], role='variant', evaluation_labels=['R1']) for i in items]
            preds = [dict(item_id=i['item_id'], input_hash=digest(visible(i)), method='tcrag', status=status, raw_response='{"answer":"A"}', termination=term) for i, status, term in zip(items, ['ok', 'invalid', 'failed'], ['accepted', 'budget_exhausted', 'request_failed'])]
            atomic(root / 'inputs.jsonl', items, lines=True)
            atomic(root / 'predictions.jsonl', preds, lines=True)
            result = score_run(root, root / 'inputs.jsonl', labels, root / 'scores')
            self.assertEqual(result['N_planned'], 3)
            self.assertEqual(result['N_failed'], 1)
            self.assertEqual(result['N_invalid'], 1)
            self.assertAlmostEqual(result['sources'][0]['accuracy'], 1 / 3)
            self.assertEqual(result['categories'][0]['groups'], 1)
            # No model inference takes place during scoring; even a syntactically
            # correct answer on a failed attempt receives zero correctness.
            scored = [json.loads(x) for x in (root / 'scores/scored.jsonl').read_text().splitlines()]
            self.assertEqual([r['correct'] for r in scored], [True, False, False])

    def test_shared_source_roots_are_one_bootstrap_cluster(self):
        items = {'a': dict(question='shared original', options={'A': 'a'}), 'b': dict(question='shared  original', options={'A': 'a'})}
        labels = [dict(item_id='a', role='reference', group_id='source1:case'), dict(item_id='b', role='reference', group_id='source2:case')]
        cluster = dependencies(labels, items)
        self.assertEqual(len(set(cluster.values())), 1)
        ci = cluster_interval([dict(score=0, dependency_group='same'), dict(score=1, dependency_group='same')])
        self.assertEqual(ci['ci95'], [.5, .5])
        self.assertTrue(ci['unstable'])


if __name__ == '__main__':
    unittest.main()
