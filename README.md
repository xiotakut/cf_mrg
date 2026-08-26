# cf_mrg

The current experiment is **DeltaRev-MedRGAG: Selective Counterfactual Decision Revision**, implemented in [`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/). It conservatively preserves the unchanged local `medrgag_proxy` answer unless verified source evidence refutes it and supports an alternative. This is not a world-model claim.

The pilot contains 200 complete MedEinst control/trap pairs: 40 development and 160 test, split by diagnosis family without overlap and excluding pairs from the earlier 303-item analysis. Locally available MedPIC official linked pairs are 0. NICE, official MedEinst edit metadata, decisive source spans, and retrieval relevance references are unavailable; KGCC text does not replace them. The local all-Llama `medrgag_proxy` is not an exact reproduction of the published MedRGAG configuration.

## Current result

On the 160-pair test split, `medrgag_proxy` scored 9.38% strict normalized exact-match on trap cases and 10.00% on controls; old-answer persistence was 21.25%. The development-selected threshold was 1.0 for both harm budgets. `full_deltarev` changed 1/160 answers, repaired 0 errors, harmed 0 correct answers, and achieved zero net correction. LLM-only delta extraction produced 0/200 usable outputs, and atomic-rule extraction failed its output contract on 72.74% of applicable rows. The current implementation therefore does **not** support the selective-revision hypothesis, was not extended to MedCounterFact/MediEval, and makes no world-model claim. See the [full scientific summary](cf_medrgag_validation_pack/results/summary.md).

See the [validation-pack README](cf_medrgag_validation_pack/README.md) for environment assumptions, all methods, output definitions, and the complete single-GPU and three-shard workflow.

From the repository root, the minimal single-GPU workflow is:

```bash
cd cf_medrgag_validation_pack

python3 scripts/run_deltarev.py prepare \
  --raw private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl \
  --exclude-gold results/heldout.gold.jsonl \
  --inference results/deltarev.inference.jsonl --gold results/deltarev.gold.jsonl

CUDA_VISIBLE_DEVICES=0 python3 scripts/run_deltarev.py baseline \
  --inference results/deltarev.inference.jsonl --output-dir results/baseline_work \
  --output results/baseline.jsonl

CUDA_VISIBLE_DEVICES=0 python3 scripts/run_deltarev.py run \
  --inference results/deltarev.inference.jsonl --baseline results/baseline.jsonl \
  --output-dir results

python3 scripts/evaluate_deltarev.py \
  --gold results/deltarev.gold.jsonl --baseline results/baseline.jsonl \
  --proposals results/raw_proposals.jsonl --deltas results/deltas.jsonl \
  --retrieval results/retrieval.jsonl --rules results/rules.jsonl \
  --output-dir results --bootstrap-samples 1000
```

Final outputs are `predictions.jsonl`, `deltas.jsonl`, `retrieval.jsonl`, `rules.jsonl`, `metrics.csv`, `metrics.json`, `tradeoff.csv`, and `summary.md` under `cf_medrgag_validation_pack/results/`. Intermediate caches are the inference/gold split, baseline, raw proposals, and optional shard directories.

The previous transition-card/world-model experiments are historical. Their results remain in [`GATE_B_D_RESULTS.md`](cf_medrgag_validation_pack/GATE_B_D_RESULTS.md) and [`handoff/`](cf_medrgag_validation_pack/handoff/).
