# CFShift-MedRGAG validation pack

CFShift-MedRGAG tests **Counterfactual Preference-Shift Residual Reranking** on a fixed
four-option MedEinst MCQ view. The retrieval → KGCC → KADS → reader baseline is unchanged;
the side branch measures how option sequence log-likelihoods move from the control case to the
trap case. NICE, atomic rules, transition cards, the old 49-way integer scorer, and the old hard
preserve/revise gate are inactive. This is not a world model.

The actual scientific result is in [`results_cfshift/summary.md`](results_cfshift/summary.md).

## Result

On 500 fresh official test pairs, `medrgag_mcq_proxy` reaches 46.0% trap accuracy. The frozen
CFShift residual reaches 47.6%: 14 repairs, 6 harms, +1.6 percentage points net correction,
5.8% revision coverage, 2.61% conditional harm, and 97.39% original-correct preservation.
The profile always-apply method reaches 60.0%; shuffled control, delta, and profile variants reach
57.0%, 44.4%, and 35.2%, respectively. However, pure CF shift improves target-only accuracy by
only 0.2 points and its paired-bootstrap 95% interval crosses zero. The profile residual has a
larger +13.0-point net correction but 38.70% conditional harm, so it is not a conservative
operating point. A no-MedRGAG-evidence scorer reaches 64.4%, identifying selected-evidence context
interference and score separation as the main remaining bottleneck.

The frozen directional criteria are met, so this is qualified evidence for counterfactual/profile
updating and a small nontrivial residual augmentation. It is not strong evidence for pure
preference shift, and it does not support a world-model claim.

## Data and environment

- Development: 800 complete official MedEinst train/reference pairs.
- Calibration: 200 different official train/reference pairs.
- Fresh test: 500 official test pairs excluding every `source_case_id` in the inspected
  300-pair DeltaRank test.
- Options: trap diagnosis, control diagnosis, and two deterministic DDXPlus-profile hard
  negatives, identically presented to every main method.
- Model: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`.
- Runtime: the existing `/home/data3/txy/MedRGAG/.venv` and vLLM 0.8.5.
- Profiles: official `release_conditions.json` and `release_evidences.json`; MedCPT performs one
  deterministic best-evidence match per changed finding.
- `medrgag_mcq_proxy` is the local all-Llama implementation, not the paper's mixed-model setup.
  No other complete stronger local model was available, so no model-capacity comparison was run.

Private source files and `results_cfshift/cache/` are ignored by git.

## Prepare and zero-cost audit

```bash
python3 scripts/run_cfshift.py prepare \
  --train-raw private_data/deltarank_sources/medeinst_train.jsonl \
  --test-raw private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl \
  --conditions private_data/deltarank_sources/release_conditions.json \
  --old-dev results_deltarank/dev.jsonl \
  --old-test results_deltarank/test.jsonl \
  --output-dir results_cfshift \
  --dev-pairs 800 --calibration-pairs 200 --fresh-test-pairs 500 --seed 13

python3 scripts/run_cfshift.py audit \
  --candidates results_deltarank/candidate_scores.jsonl \
  --dev results_deltarank/dev.jsonl --test results_deltarank/test.jsonl \
  --mcq results_deltarank/predictions_mcq.jsonl \
  --output results_cfshift/existing_candidate_audit.json

CUDA_VISIBLE_DEVICES=0 /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_cfshift.py match \
  --data results_cfshift/dev.jsonl results_cfshift/calibration.jsonl results_cfshift/fresh_test.jsonl \
  --evidences private_data/deltarank_sources/release_evidences.json \
  --output results_cfshift/delta_evidence_matches.jsonl --device cuda:0
```

## Unchanged MedRGAG baseline

Run two independent shards. Existing DeltaRank stage caches are reused only when item IDs and
four-option views are identical.

```bash
for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_cfshift.py baseline \
    --data results_cfshift/dev.jsonl results_cfshift/calibration.jsonl results_cfshift/fresh_test.jsonl \
    --output-dir results_cfshift/cache/formal_baseline \
    --old-cache results_deltarank/cache/formal \
    --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
    --shard-index $i --shard-count 2 --gpu-memory-utilization .55 &
done
wait

python3 scripts/run_cfshift.py merge \
  --inputs results_cfshift/cache/formal_baseline/shard-*/baseline.jsonl \
  --output results_cfshift/cache/baseline.jsonl
```

## Option scoring and frozen calibration

The scorer sums the exact option-label token log-likelihood, maps two deterministic label
permutations back to diagnosis IDs, averages them, and normalizes over the four choices. Invalid
numeric scoring is reported as invalid and is never converted to the MedRGAG answer.

Run a 20-pair smoke test first, then score only development and calibration:

```bash
CUDA_VISIBLE_DEVICES=0 /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_cfshift.py baseline \
  --data results_cfshift/dev.jsonl \
  --output-dir results_cfshift/cache/smoke_baseline \
  --old-cache results_deltarank/cache/formal \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct --limit 20

CUDA_VISIBLE_DEVICES=0 /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_cfshift.py score \
  --data results_cfshift/dev.jsonl \
  --baseline results_cfshift/cache/smoke_baseline/shard-000-of-001/baseline.jsonl \
  --output-dir results_cfshift/cache/smoke_scores_final \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct --limit 20

for i in 0 1; do
  CUDA_VISIBLE_DEVICES=$i /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_cfshift.py score \
    --data results_cfshift/dev.jsonl results_cfshift/calibration.jsonl \
    --baseline results_cfshift/cache/baseline.jsonl \
    --output-dir results_cfshift/cache/formal_scores \
    --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
    --shard-index $i --shard-count 2 --gpu-memory-utilization .55 &
done
wait

python3 scripts/run_cfshift.py merge \
  --inputs results_cfshift/cache/formal_scores/shard-*/option_scores.jsonl \
  --output results_cfshift/cache/option_scores.train.jsonl

python3 scripts/evaluate_cfshift.py calibrate \
  --data results_cfshift/dev.jsonl results_cfshift/calibration.jsonl \
  --baseline results_cfshift/cache/baseline.jsonl \
  --scores results_cfshift/cache/option_scores.train.jsonl \
  --matches results_cfshift/delta_evidence_matches.jsonl \
  --conditions private_data/deltarank_sources/release_conditions.json \
  --output results_cfshift/cache/frozen_config.json
```

Only after `frozen_config.json` exists, score the fresh test with the same two shard commands,
replacing `--data` with `results_cfshift/fresh_test.jsonl`. Then merge all shard rows and evaluate:

```bash
python3 scripts/run_cfshift.py merge \
  --inputs results_cfshift/cache/formal_scores/shard-*/option_scores.jsonl \
  --output results_cfshift/option_scores.jsonl

python3 scripts/evaluate_cfshift.py evaluate \
  --data results_cfshift/dev.jsonl results_cfshift/calibration.jsonl results_cfshift/fresh_test.jsonl \
  --baseline results_cfshift/cache/baseline.jsonl \
  --scores results_cfshift/option_scores.jsonl \
  --matches results_cfshift/delta_evidence_matches.jsonl \
  --conditions private_data/deltarank_sources/release_conditions.json \
  --config results_cfshift/cache/frozen_config.json \
  --audit results_cfshift/existing_candidate_audit.json \
  --output-dir results_cfshift
```

## Methods and outputs

Main methods are `direct_mcq`, `medrgag_mcq_proxy`, `pair_prompt`,
`target_margin_ranker`, `cf_shift_ranker`, `cf_shift_profile_ranker`, the three shuffled
profile controls, `no_medrgag_evidence`, `no_cf_shift`, the always-apply aliases, and the two
single-margin residual policies. `gold_control_anchor_diagnostic` is an oracle diagnostic and is
excluded from the main interpretation.

Final outputs are under [`results_cfshift/`](results_cfshift/): `dev.jsonl`,
`calibration.jsonl`, `fresh_test.jsonl`, `existing_candidate_audit.json`,
`option_scores.jsonl`, `delta_evidence_matches.jsonl`, `predictions.jsonl`, `metrics.json`,
`metrics.csv`, `tradeoff.csv`, and `summary.md`.

DeltaRank remains a historical candidate-generation pilot in [`results_deltarank/`](results_deltarank/).
