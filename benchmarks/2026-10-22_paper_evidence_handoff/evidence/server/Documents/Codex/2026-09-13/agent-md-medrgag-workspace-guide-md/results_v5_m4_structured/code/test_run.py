import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import worker
import status
from prepare_v5 import OUT, SOURCE, read, write, dump


class RunTest(unittest.TestCase):
    def test_disjoint_claims_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(worker, 'OUT', Path(directory)):
            for n in range(4):
                dump(worker.OUT / 'jobs' / f'{n}.json', dict(name=str(n), state='queued', n=128))
            jobs = [worker.claim(g) for g in ('1', '2', '3')]
            self.assertEqual(len({j['name'] for j in jobs}), 3)
            self.assertEqual(worker.claim('2')['name'], jobs[1]['name'])
            dump(worker.OUT / 'jobs' / (jobs[0]['name'] + '.json'), dict(jobs[0], state='done'))
            self.assertNotIn(worker.claim('1')['name'], {j['name'] for j in jobs})

    def test_validity_monitor_matches_the_frozen_pilot(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(status, 'OUT', Path(directory)):
            root = status.OUT
            for name in ('items.jsonl', 'evaluation.jsonl', 'plan.json'):
                (root / name).symlink_to(OUT / name)
            rows = read(SOURCE / 'm4_format_structured_pilot/predictions.jsonl')
            write(root / 'runs/test/predictions.jsonl', rows)
            dump(root / 'jobs/test.json', dict(name='test', state='done'))
            status.data.cache_clear()
            result = status.status()
            self.assertEqual(result['completed'], 100)
            self.assertEqual(result['validity']['format_valid'], 98)
            self.assertEqual(result['validity']['native_valid'], 84)
            self.assertEqual(result['validity']['schema_valid'], 99)
            self.assertEqual(result['validity']['truncated'], 1)
            self.assertEqual(result['outside_selection_pilot_inputs']['N'], 0)
            status.data.cache_clear()


if __name__ == '__main__':
    unittest.main()
