"""Only temporary files/fake sleeps; no model, real child process, or grader."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bounded_reader_under_test', Path(__file__).with_name('stable_json.py'))
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class StableJSONTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'status.json'

    def test_truncated_then_valid_recovers_same_metadata_and_records_path(self):
        self.path.write_text('{"status":')
        sleeps = []
        audit = []
        expected = {'status': 'complete', 'complete': 17}
        def finish_write(delay):
            sleeps.append(delay)
            self.path.write_text(json.dumps(expected))
        self.assertEqual(reader.read_json(self.path, sleeper=finish_write, audit=audit.append), expected)
        self.assertEqual(sleeps, [0.1])
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]['status'], 'transient_json_read_recovered')
        self.assertEqual(audit[0]['path'], str(self.path.resolve()))
        self.assertEqual(audit[0]['attempts'], 2)

    def test_permanent_malformed_has_bounded_attempts_and_no_raw_contents(self):
        self.path.write_text('{sensitive_case_content')
        sleeps = []
        audit = []
        with self.assertRaises(reader.PersistentJSONReadError) as caught:
            reader.read_json(self.path, sleeper=sleeps.append, audit=audit.append)
        self.assertEqual(sleeps, list(reader.RETRY_DELAYS))
        self.assertEqual(caught.exception.diagnostic['attempts'], 5)
        self.assertEqual(caught.exception.diagnostic['path'], str(self.path.resolve()))
        self.assertNotIn('sensitive_case_content', str(caught.exception))
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]['status'], 'persistent_json_read_error')

    def test_valid_never_sleeps_or_audits(self):
        self.path.write_text('{"complete": 19}')
        fail = lambda *args: self.fail('No retry or diagnostic needed')
        self.assertEqual(reader.read_json(self.path, sleeper=fail, audit=fail), {'complete': 19})

    def test_missing_file_is_not_hidden(self):
        with self.assertRaises(FileNotFoundError):
            reader.read_json(self.path, sleeper=lambda *args: self.fail('No decode retry'))

    def test_incomplete_utf8_then_valid_is_retried(self):
        self.path.write_bytes(b'{"s":"\xe4\xb8')
        def finish_write(delay): self.path.write_text('{"s":"完整"}')
        self.assertEqual(reader.read_json(self.path, sleeper=finish_write, audit=lambda row: None), {'s': '完整'})


if __name__ == '__main__':
    unittest.main()
