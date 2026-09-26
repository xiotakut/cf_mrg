"""Fixed-budget original-input sampling control, separate from F and experts."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import ValidationError
from cf_moa.contracts import AgentProposal
from cf_moa.tools.adapters import native_json

VARIANT = 'same_budget_native_sampling_3x2048_v1'
CONFIG = Path(__file__).resolve().parents[1] / 'configs/native_sampling.json'


def config():
    return json.loads(CONFIG.read_text())


def vote_key(packet, native):
    value = native['answer_choice']
    if packet.native_input['answer_format'] == 'multi':
        value = sorted(set(value))
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def run(packet, session):
    checkpoint, cfg = session.checkpoint(), config()
    if packet.model_input is not None or 'answer_choice' not in packet.answer_schema.get('properties', {}):
        return AgentProposal('A1', VARIANT, packet.input_hash, 'unsupported', None,
                             cost=session.cost_since(checkpoint))
    draws, error = [], None
    for seed in cfg['seeds']:
        request = dict(schema=packet.answer_schema, seed=seed, temperature=cfg['temperature'],
                       max_tokens=cfg['max_tokens_per_draw'], kind='generate')
        request['prompt' if isinstance(packet.original_context, str) else 'messages'] = packet.original_context
        raw = session.invoke(request, stage='native_sampling:seed_'+str(seed))
        try:
            native = native_json(raw, packet.answer_schema)
            key = vote_key(packet, native)
        except (ValueError, TypeError, KeyError, ValidationError) as exc:
            native, key, error = None, None, str(exc)
        draws.append(dict(seed=seed, raw_response=raw, native_response=native, vote_key=key, error=error))
        if error:
            break  # No later draw or later experiment item after a schema error.
    winner, index, counts = None, None, Counter(row['vote_key'] for row in draws if row['vote_key'] is not None)
    if error is None:
        index = next(i for i, row in enumerate(draws) if counts[row['vote_key']] == max(counts.values()))
        winner = deepcopy(draws[index]['native_response'])
    return AgentProposal('A1', VARIANT, packet.input_hash, 'supported' if winner is not None else 'partial',
        winner, unresolved=[error] if error else [], cost=session.cost_since(checkpoint),
        checks=[dict(type='format_validation', name='all_fixed_draws_native_format', passed=error is None)],
        trace=dict(control_only=True, config=cfg, draws=draws, winner_index=index, vote_counts=dict(counts),
            inference_started=bool(draws), semantic_result='unavailable' if error else 'native_answer_available',
            method_score='not_scored', schema_invalid=bool(error),
            comparison='Same 6144 maximum output allocation as A1 audit+answer; actual compute and input differ'))
