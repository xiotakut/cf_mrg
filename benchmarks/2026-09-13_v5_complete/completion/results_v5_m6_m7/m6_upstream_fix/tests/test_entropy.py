import math
import sys
import threading
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from backend import entropy_from_scores, HFBackend


class EntropyTest(unittest.TestCase):
    def test_reference_formula(self):
        import torch
        p = torch.tensor([[.1, .2, .7], [.5, .5, 0]], dtype=torch.float32)
        got = entropy_from_scores(torch.log(p))
        expected = torch.tensor([-sum(float(x) * math.log(float(x) + 1e-10) for x in row if x > 0) for row in p])
        self.assertLess(float((got - expected).abs().max()), 1e-5)
        self.assertNotAlmostEqual(float(got.sum()), float(got.mean()))

    def test_same_backend_scores_after_sampling_processors(self):
        import torch
        from tokenizers import Tokenizer
        from tokenizers.models import WordLevel
        from tokenizers.pre_tokenizers import Whitespace
        from transformers import PreTrainedTokenizerFast, LlamaConfig, LlamaForCausalLM
        vocab = {'[UNK]': 0, '[EOS]': 1, 'alpha': 2, 'beta': 3, 'gamma': 4, 'delta': 5, 'epsilon': 6, 'zeta': 7}
        tok = Tokenizer(WordLevel(vocab, unk_token='[UNK]'))
        tok.pre_tokenizer = Whitespace()
        fast = PreTrainedTokenizerFast(tokenizer_object=tok, unk_token='[UNK]', eos_token='[EOS]', pad_token='[EOS]', padding_side='left')
        fast.chat_template = '{% for message in messages %}{{ message["content"] }} {% endfor %}'
        torch.manual_seed(1)
        model = LlamaForCausalLM(LlamaConfig(vocab_size=8, hidden_size=16, intermediate_size=32, num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=2, eos_token_id=1, pad_token_id=1)).eval()
        engine = HFBackend.__new__(HFBackend)
        engine.config = dict(chat_template_kwargs={}, max_length=128, temperature=.7, top_p=.8, top_k=4)
        engine.model, engine.tokenizer, engine.lock = model, fast, threading.Lock()
        engine.identity = {'test_only': True}
        requests = [[dict(role='user', content='alpha beta')], [dict(role='user', content='gamma')]]
        both = engine.generate(requests, 8, 123, entropy=True, reference=True)
        plain = engine.generate(requests, 8, 123, entropy=False)
        for a, b in zip(both, plain):
            self.assertEqual(a['token_ids'], b['token_ids'])
            self.assertEqual(a['prompt_token_ids'], b['prompt_token_ids'])
            self.assertTrue(all(abs(x - y) <= 1e-5 for x, y in zip(a['entropies'], a['reference_entropies'])))
            self.assertTrue(all(a['token_ids'][i] not in fast.all_special_ids for i in a['useful_positions']))
            self.assertEqual(len(a['tokens']), len(a['entropies']))
        # Changing the co-batched request must not consume this request's RNG.
        joint = engine.generate(requests, 8, 0, entropy=True, sampling_groups=[(1, 81), (1, 92)])
        for request, result, seed in zip(requests, joint, [81, 92]):
            solo = engine.generate([request], 8, seed, entropy=True)[0]
            self.assertEqual(result['token_ids'], solo['token_ids'])


if __name__ == '__main__':
    unittest.main()
