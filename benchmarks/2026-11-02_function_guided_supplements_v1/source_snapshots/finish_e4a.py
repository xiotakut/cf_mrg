"""Post-hoc diagnostics of completed E4a outputs; no inference or re-scoring."""
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT, rows, write, dump, now

out = ROOT / 'e4a/analysis'
scored = list(rows(out / 'native_scored.jsonl'))
by_key = {(r['method'], r['request_id'], r['arm']): r for r in scored}
decomposition = []
for method in ['M4', 'M5']:
    ids = sorted(rid for m, rid, arm in by_key if m == method and arm == 'program_B')
    assert len(ids) == 123
    groups = {
        'all': lambda b, l: True,
        'B_available': lambda b, l: b['native_available'],
        'B_unavailable': lambda b, l: not b['native_available'],
        'upstream_applied': lambda b, l: b['upstream_applied'],
        'upstream_not_applied': lambda b, l: not b['upstream_applied'],
        'both_available': lambda b, l: b['native_available'] and l['native_available'],
    }
    for subset, predicate in groups.items():
        pairs = [(by_key[method, rid, 'program_B'], by_key[method, rid, 'uniform_LLM']) for rid in ids]
        pairs = [(b, l) for b, l in pairs if predicate(b, l)]
        decomposition.append(dict(method=method, subset=subset, n=len(pairs),
            program_correct=sum(b['correct'] is True for b, l in pairs),
            LLM_correct=sum(l['correct'] is True for b, l in pairs),
            LLM_available=sum(l['native_available'] for b, l in pairs)))
table = pd.DataFrame(decomposition)
if (out / 'availability_decomposition.csv').exists():
    pd.testing.assert_frame_equal(table, pd.read_csv(out / 'availability_decomposition.csv'))
table.to_csv(out / 'availability_decomposition.csv', index=False)

# These were chosen after examining saved answers. They illustrate a success and a
# failure; they are not independently coded errors and do not estimate prevalence.
requests = {r['request_id']: r for r in rows(ROOT / 'e4a/inference/m4.jsonl')}
examples = []
for rid, purpose, observation in [
    ('v03572', 'supported_option_dropped_in_generated_answer',
     'Both B and E have saved MET support. The generated explanation names both medications, but its answer_choice contains only B; program_B retains both and matches the reference.'),
    ('v03569', 'faithful_state_execution_can_preserve_wrong_initial_option',
     'Initial D has UNKNOWN support and E has MET support. Program_B follows the frozen policy and retains D plus E, while the reference contains E only. The LLM omits D and matches the reference, departing from the prescribed UNKNOWN-preservation policy. This does not establish that all of its clinical explanation is correct.'),
]:
    req = requests[rid]
    visible = json.loads(req['request']['messages'][1]['content'])
    b = by_key['M4', rid, 'program_B']
    l = by_key['M4', rid, 'uniform_LLM']
    response_path = ROOT / 'e4a/runs/m4/responses' / (rid + '.json')
    raw = json.load(response_path.open())
    examples.append(dict(method='M4', request_id=rid, record_id=b['record_id'],
        selection='post-hoc illustrative example, not blinded human error coding',
        purpose=purpose, observation=observation, input=visible,
        program_B=b, uniform_LLM=l, saved_response=raw,
        request_hash=req['request_hash'], source=str(response_path)))
assert examples[0]['program_B']['correct'] and not examples[0]['uniform_LLM']['correct']
assert not examples[1]['program_B']['correct'] and examples[1]['uniform_LLM']['correct']
write(out / 'illustrative_execution_examples.jsonl', examples)

overall = pd.read_csv(out / 'overall.csv').set_index(['method', 'arm'])
paired = [json.load((out / f'{m}_paired.json').open()) for m in ['m4', 'm5']]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout='constrained')
x = np.arange(2)
for j, (arm, label, color) in enumerate([
    ('uniform_LLM', 'Uniform LLM execution', '#e39742'),
    ('program_B', 'Frozen functional execution', '#2a69a2'),
]):
    data = [overall.loc[(m, arm)] for m in ['M4', 'M5']]
    bars = axes[0].bar(x + (j - .5) * .35, [r.accuracy * 100 for r in data], .35,
                       label=label, color=color)
    axes[0].bar_label(bars, labels=[f'{int(r.correct)}/123' for r in data], padding=3)
axes[0].set_xticks(x, ['M4', 'M5'])
axes[0].set_ylim(0, 100)
axes[0].set_ylabel('Native accuracy (%)')
axes[0].set_title('Same frozen information; all 123 inputs')
axes[0].legend(frameon=False, fontsize=9)
means = np.array([r['program_minus_LLM'] * 100 for r in paired])
cis = np.array([r['ci95'] for r in paired]) * 100
axes[1].errorbar(means, x, xerr=[means-cis[:, 0], cis[:, 1]-means], fmt='o',
                 capsize=5, color='#2a69a2')
axes[1].axvline(0, color='gray', linewidth=1, linestyle='--')
axes[1].set_yticks(x, ['M4', 'M5'])
axes[1].invert_yaxis()
axes[1].set_ylim(1.65, -.55)
axes[1].set_xlabel('Functional minus LLM accuracy (percentage points)')
axes[1].set_title('95% intervals from 66 scenario-family clusters')
for i, r in enumerate(paired):
    axes[1].text(means[i], i+.19, f'{means[i]:+.2f} [{cis[i,0]:+.2f}, {cis[i,1]:+.2f}]',
                 ha='center', fontsize=9)
fig.suptitle('Terminal execution control; exposed development panel', fontsize=12)
for ext in ['png', 'pdf']:
    fig.savefig(out / f'terminal_execution_comparison.{ext}', dpi=180)
plt.close(fig)
dump(out / 'diagnostics_receipt.json', dict(time=now(), status='complete',
    new_model_calls=0, native_rescoring=0, availability_rows=len(table),
    examples=len(examples), examples_post_hoc=True,
    human_annotations=0, primary_denominator_per_method=123))
print(json.dumps(dict(status='complete', availability_rows=len(table), examples=len(examples))))
