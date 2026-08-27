# DeltaRank-MedRGAG validation pack

DeltaRank-MedRGAG tests **Structured Counterfactual Delta + Closed-Set Diagnostic Ranking**.
It evaluates ranking capability before applying an optional residual margin policy. NICE, the
old atomic-rule extractor, and the old hard conjunctive gate are not used. No world-model claim
is made.

## Result

The frozen pilot used 300 official MedEinst train/reference pairs for development and 300
official test pairs. Key test results:

| Method | Accuracy | R@5 | R@10 | Repairs | Harms | Conditional harm | Net |
|---|---:|---:|---:|---:|---:|---:|---:|
| legacy open MedRGAG | 10.33% | — | — | 6 | 111 | 81.62% | -35.00% |
| MedRGAG MCQ, 2-way | 59.00% | — | — | 62 | 21 | 15.44% | +13.67% |
| MedRGAG MCQ, 4-way baseline | 45.33% | — | — | 0 | 0 | 0.00% | 0.00% |
| target-only ranker | 13.33% | 45.67% | 55.33% | 21 | 117 | 86.03% | -32.00% |
| delta-profile ranker | 27.67% | 49.00% | 61.00% | 25 | 78 | 57.35% | -17.67% |
| residual, dev-selected threshold 4 | 46.33% | — | — | 5 | 2 | 1.47% | +1.00% |

The residual threshold was **not** a useful development operating point: dev had 3 repairs,
4 harms, and -0.33% net correction, and no development threshold had positive net correction.
Therefore the pilot does not support the residual-augmentation hypothesis. Real delta/profile
reranking beat both shuffles, but candidate R@10 reached only 61%, below the predefined
capability target. See [`results_deltarank/summary.md`](results_deltarank/summary.md).

## Data and environment

- Development: 300 complete official MedEinst train/reference pairs.
- Test: 300 complete official MedEinst test pairs, used only after prompts and scoring froze.
- Ontology: all 49 official DDXPlus conditions; 46 occur in the downloaded train/test files.
- Profiles: deterministic `release_conditions.json` and `release_evidences.json` data.
- Model: local `Meta-Llama-3.1-8B-Instruct` through the existing MedRGAG vLLM environment.
- `medrgag_mcq_proxy` reuses retrieval → KGCC → KADS → reader with real answer options. It is
  a local all-Llama proxy, not the published mixed-model configuration.

Private source data and expensive caches are ignored by git.

## Prepare

```bash
python3 scripts/run_deltarank.py prepare \
  --train-raw private_data/deltarank_sources/medeinst_train.jsonl \
  --test-raw private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl \
  --conditions private_data/deltarank_sources/release_conditions.json \
  --evidences private_data/deltarank_sources/release_evidences.json \
  --output-dir results_deltarank --dev-pairs 300 --test-pairs 300 --seed 13
```

## Run

Run a 20-pair smoke test first:

```bash
CUDA_VISIBLE_DEVICES=0 /home/data3/txy/MedRGAG/.venv/bin/python scripts/run_deltarank.py run \
  --data results_deltarank/dev.jsonl \
  --labels results_deltarank/labels.json \
  --profiles results_deltarank/cache/profiles.json \
  --deltas results_deltarank/deltas.jsonl \
  --output-dir results_deltarank/cache/smoke \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --limit 20
```

For the formal run, launch three independent shards with `--shard-index 0|1|2` and
`--shard-count 3`, then merge:

```bash
python3 scripts/run_deltarank.py merge --kind mcq \
  --inputs results_deltarank/cache/formal/shard-*/mcq_predictions.jsonl \
  --output results_deltarank/predictions_mcq.jsonl

python3 scripts/run_deltarank.py merge --kind candidates \
  --inputs results_deltarank/cache/formal/shard-*/candidate_scores.jsonl \
  --output results_deltarank/candidate_scores.jsonl
```

## Evaluate

```bash
python3 scripts/evaluate_deltarank.py \
  --dev results_deltarank/dev.jsonl \
  --test results_deltarank/test.jsonl \
  --labels results_deltarank/labels.json \
  --deltas results_deltarank/deltas.jsonl \
  --mcq results_deltarank/predictions_mcq.jsonl \
  --candidates results_deltarank/candidate_scores.jsonl \
  --output-dir results_deltarank
```

Thresholds are selected on development data only. Invalid final outputs count as wrong and are
never converted to PRESERVE.

## Methods and outputs

Methods: `legacy_open_medrgag`, `direct_mcq`, `medrgag_mcq_proxy`,
`target_only_ranker`, `medrgag_evidence_ranker`, `full_pair_ranker`,
`pair_aware_ranker`, `delta_profile_ranker`, `delta_always_apply`, `delta_residual`,
`shuffled_delta`, and `shuffled_profile`. Oracle top-5/top-10 selectors are diagnostics only.

Final outputs are under [`results_deltarank/`](results_deltarank/): `labels.json`, `dev.jsonl`,
`test.jsonl`, `deltas.jsonl`, `candidate_scores.jsonl`, `predictions.jsonl`, `metrics.json`,
`metrics.csv`, `tradeoff.csv`, and `summary.md`.
