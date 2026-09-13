import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worker


class QueueTest(unittest.TestCase):
    def test_paused_m6_is_not_claimed_by_any_gpu(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(worker, 'ROOT', Path(directory)):
            (worker.ROOT / 'jobs').mkdir()
            for i, method in enumerate(['imedrag', 'tcrag', 'tcrag', 'tcrag']):
                (worker.ROOT / 'jobs' / f'{i}.json').write_text(json.dumps(
                    dict(name=str(i), method=method, state='paused' if i == 0 else 'queued')))
            claimed = [worker.claim(gpu) for gpu in ('1', '2', '3')]
            self.assertEqual(len({j['name'] for j in claimed}), 3)
            self.assertTrue(all(j['method'] == 'tcrag' for j in claimed))

    def test_disjoint_claims_recovery_and_helping(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(worker, 'ROOT', Path(directory)):
            (worker.ROOT / 'jobs').mkdir()
            for i, method in enumerate(['imedrag', 'imedrag', 'tcrag', 'tcrag']):
                (worker.ROOT / 'jobs' / f'{i}.json').write_text(json.dumps(
                    dict(name=str(i), method=method, state='queued')))
            claimed = [worker.claim(gpu) for gpu in ('1', '2', '3')]
            self.assertEqual(len({j['name'] for j in claimed}), 3)
            self.assertEqual([j['method'] for j in claimed], ['imedrag', 'imedrag', 'tcrag'])
            self.assertEqual(worker.claim('1')['name'], claimed[0]['name'])
            first = dict(claimed[0], state='done')
            (worker.ROOT / 'jobs' / (first['name'] + '.json')).write_text(json.dumps(first))
            self.assertEqual(worker.claim('1')['method'], 'tcrag')


if __name__ == '__main__':
    unittest.main()
