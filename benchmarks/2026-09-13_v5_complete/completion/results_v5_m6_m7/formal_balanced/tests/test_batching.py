import sys
import unittest
from concurrent.futures import Future
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from backend import BatchingBackend


class Tokenizer:
    def encode(self, text, **kwargs):
        return list(range(len(text)))

    def decode(self, tokens, **kwargs):
        return str(tokens)


class Engine:
    tokenizer = Tokenizer()
    identity = {'test_only': True}

    def __init__(self):
        self.batches = []

    def prompts(self, messages):
        return messages

    def generate(self, messages, max_tokens, seed, entropy=False, sampling_groups=None):
        self.batches.append(messages)
        return [dict(text=message, seed=group[1], batch_seconds=.001, batch_size=len(messages))
                for message, group in zip(messages, sampling_groups)]


class BatchingTest(unittest.TestCase):
    def test_length_phase_format_and_per_request_seed(self):
        engine = Engine()
        backend = BatchingBackend(engine, 1000)
        requests = [('a'*10, ('single', 'query')), ('b'*14, ('single', 'query')),
                    ('c'*50, ('single', 'query')), ('d'*12, ('single', 'parse')),
                    ('e'*11, ('diagnosis', 'query'))]
        futures = []
        for seed, (message, group) in enumerate(requests):
            future = Future()
            backend.queue.put(dict(messages=[message], max_tokens=8, seed=seed, entropy=False,
                                   batch_group=group, future=future))
            futures.append(future)
        outputs = [f.result(timeout=5)[0] for f in futures]
        self.assertEqual([r['text'] for r in outputs], [r[0] for r in requests])
        self.assertEqual([r['seed'] for r in outputs], list(range(5)))
        self.assertIn(['a'*10, 'b'*14], engine.batches)
        self.assertEqual(sorted(map(len, engine.batches)), [1, 1, 1, 2])


if __name__ == '__main__':
    unittest.main()
