import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import finish


class FinishTest(unittest.TestCase):
    def test_completed_m7_scores_while_m6_paused_and_does_not_rescore(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(finish, 'ROOT', Path(directory)):
            root = finish.ROOT
            jobs = [dict(name=m, method=m, state=s, n=13893)
                    for m, s in [('imedrag', 'paused'), ('tcrag', 'done')]]
            finish.atomic(root / 'plan.json', dict(jobs=jobs))
            for job in jobs:
                finish.atomic(root / 'jobs' / (job['name'] + '.json'), job)
                finish.atomic(root / 'runs' / job['name'] / 'execution_report.json',
                              dict(complete=True, coverage=dict(N_planned=13893)))
            inputs = [dict(item_id=str(i)) for i in range(13905)]

            def read(path):
                if path.name == 'inputs.jsonl':
                    return inputs
                if path.name == 'evaluation.jsonl':
                    return [{}] * 15616
                return inputs[:12] if path.name.startswith('reused_') else inputs[12:]

            summary = dict(N_ok=13905, N_invalid=0, N_failed=0, categories=[])
            with patch.object(finish, 'read', side_effect=read), patch.object(
                    finish, 'score_run', return_value=summary) as score:
                finish.main()
                self.assertTrue((root / 'results/tcrag/complete.json').exists())
                self.assertFalse((root / 'complete.json').exists())
                self.assertIn('paused', (root / 'RESULTS.md').read_text())
                finish.main()
                self.assertEqual(score.call_count, 1)
                jobs[0]['state'] = 'done'
                finish.atomic(root / 'jobs/imedrag.json', jobs[0])
                finish.main()
                self.assertEqual(score.call_count, 2)
                self.assertEqual(set(json.loads((root / 'complete.json').read_text())['methods']),
                                 {'imedrag', 'tcrag'})


if __name__ == '__main__':
    unittest.main()
