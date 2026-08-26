# DeltaRev-MedRGAG validation pack

The current experiment is **DeltaRev-MedRGAG: Selective Counterfactual Decision Revision**. It keeps the existing MedRGAG proxy unchanged and applies a conservative, evidence-constrained residual update: preserve the exact baseline answer unless verified evidence both refutes it and supports an alternative.

This is not a world-model experiment or claim. The earlier transition-card/world-model work is historical; see [`GATE_B_D_RESULTS.md`](GATE_B_D_RESULTS.md) and [`handoff/`](handoff/).

## Data and availability

- Main pilot: 200 complete MedEinst control/trap pairs, with control as the original case and trap as the target.
- Split: 40 development and 160 test pairs, grouped by unordered diagnosis family so no family crosses splits. Pairs used by the earlier 303-item analysis are excluded.
- MedPIC: 0 locally available official linked pairs, so it is unavailable for this paired pilot.
- NICE: unavailable and not replaced by KGCC-generated text. `without_nice` is NA.
- Official edit metadata, decisive source spans, and retrieval relevance references are unavailable for MedEinst. Gold-delta accuracy, source-rule upper bounds, Recall@5/10, MRR, and evidence-coverage accuracy are therefore NA.
- The local all-Llama `medrgag_proxy` reuses the repository's M2 retrieval/KGCC/KADS/reader path; it is not an exact reproduction of the published MedRGAG model configuration.

Inference reads only the answer-free pilot file. Gold is joined offline by the evaluator and is never passed to delta detection, retrieval, rule extraction, verification, gating, or revision.

## Current result

On the frozen 160-pair test split, the local `medrgag_proxy` achieved 9.38% strict normalized exact-match trap accuracy, 10.00% control accuracy, 0.63% both-correct pair accuracy, 21.25% old-answer persistence, and 56.25% Bias Trap Rate among 16 control-correct pairs. Both development harm budgets selected the inclusive threshold `score >= 1.0`. `full_deltarev` revised 1/160 answers, repaired 0 baseline errors, harmed 0 baseline-correct answers, and obtained zero net correction.

The run also diagnosed implementation bottlenecks: LLM-only delta extraction produced 0/200 usable outputs, and atomic-rule extraction failed its contract on 72.74% of applicable rows. The result is therefore **not support** for the current selective-revision hypothesis, but it is not a structural falsification of the architecture. No MedCounterFact/MediEval extension or world-model claim was made. Accuracy uses NFKC/casefold/whitespace/terminal-punctuation normalized exact match; no post-hoc clinical-equivalence rescoring was applied. Full details are in [`results/summary.md`](results/summary.md).

## Environment

Assumptions: Python 3 in the existing MedRGAG environment, CUDA and vLLM, the local Meta-Llama-3.1-8B-Instruct checkpoint, local Textbooks/Wikipedia BM25 indexes, and the local MedCPT checkpoint.

Run commands below from this directory. The raw MedEinst path matches the checked local snapshot.

## Prepare

```bash
python3 scripts/run_deltarev.py prepare \
  --raw private_data/gate-a-public-20260823-seed13-v3/raw/medeinst/354f4b527e764a8f2bebea8f71be55e0a6966402/00-test.jsonl \
  --exclude-gold results/heldout.gold.jsonl \
  --inference results/deltarev.inference.jsonl \
  --gold results/deltarev.gold.jsonl \
  --seed 13
```

## Single-GPU baseline and run

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/run_deltarev.py baseline \
  --inference results/deltarev.inference.jsonl \
  --output-dir results/baseline_work \
  --output results/baseline.jsonl \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct

CUDA_VISIBLE_DEVICES=0 python3 scripts/run_deltarev.py run \
  --inference results/deltarev.inference.jsonl \
  --baseline results/baseline.jsonl \
  --output-dir results \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct
```

## Three-GPU sharded baseline, run, and merge

Each shard writes a separate directory; concurrent processes never append to the same JSONL.

```bash
for shard in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$shard python3 scripts/run_deltarev.py baseline \
    --inference results/deltarev.inference.jsonl \
    --output-dir results/baseline_work \
    --output results/baseline_shards/baseline.jsonl \
    --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
    --shard-index $shard --shard-count 3 &
done
wait

python3 scripts/run_deltarev.py merge --kind baseline \
  --inputs results/baseline_shards/shard-000-of-003/baseline.jsonl \
           results/baseline_shards/shard-001-of-003/baseline.jsonl \
           results/baseline_shards/shard-002-of-003/baseline.jsonl \
  --output results/baseline.jsonl

for shard in 0 1 2; do
  CUDA_VISIBLE_DEVICES=$shard python3 scripts/run_deltarev.py run \
    --inference results/deltarev.inference.jsonl \
    --baseline results/baseline.jsonl \
    --output-dir results/run_shards \
    --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
    --shard-index $shard --shard-count 3 &
done
wait

for kind in proposals deltas retrieval rules; do
  name=$kind
  [ "$kind" = proposals ] && name=raw_proposals
  python3 scripts/run_deltarev.py merge --kind "$kind" \
    --inputs results/run_shards/shard-000-of-003/$name.jsonl \
             results/run_shards/shard-001-of-003/$name.jsonl \
             results/run_shards/shard-002-of-003/$name.jsonl \
    --output results/$name.jsonl
done
```

The proposals merge also normalizes dependency failures from the sibling delta, retrieval, and rule artifacts. Missing dependencies fail closed.

## Evaluate

```bash
python3 scripts/evaluate_deltarev.py \
  --gold results/deltarev.gold.jsonl \
  --baseline results/baseline.jsonl \
  --proposals results/raw_proposals.jsonl \
  --deltas results/deltas.jsonl \
  --retrieval results/retrieval.jsonl \
  --rules results/rules.jsonl \
  --output-dir results \
  --bootstrap-samples 1000
```

The commands above regenerate `results/raw_proposals.jsonl`. In this completed checkout, the frozen intermediate proposal cache used for the reported evaluation is `results/cache/raw_proposals.jsonl`; substitute that path to rerun only the evaluator without rerunning inference.

Thresholds are selected on development only. Test gold is used only for final offline reporting and the separately labeled oracle-gate diagnostic.

## Methods

- Base and simple baselines: `direct`, `medrgag_proxy`, `decomposition_only`, `direct_counterfactual_prompt`, `direct_answer_revision`, `always_preserve`, `always_revise`, `llm_verifier_without_evidence`.
- Retrieval readers: `standard_question_retrieval`, `candidate_specific_retrieval`, `ea_rag_style_retrieval`, `delta_only_retrieval`, `triangular_decision_change_retrieval`. EA-RAG-style is a coverage-audit proxy, not an exact reproduction.
- Evidence-constrained residual methods: `evidence_verifier_with_standard_retrieval`, `evidence_verifier_with_ea_rag_retrieval`, `full_deltarev`.
- Ablations and mechanism controls: `without_delta`, `without_baseline_answer_in_query`, `refute_only_retrieval`, `without_preserve_evidence`, `without_alternative_support_requirement`, `without_entailment_check`, `without_patient_applicability_check`, `shuffled_delta`, `shuffled_rule_evidence`, and `kgcc_generated_docs_as_decisive_evidence` (negative control only).
- `without_nice` is unavailable/NA because NICE is unavailable.

## Outputs

Final outputs:

- `results/predictions.jsonl`
- `results/deltas.jsonl`
- `results/retrieval.jsonl`
- `results/rules.jsonl`
- `results/metrics.csv`
- `results/metrics.json`
- `results/tradeoff.csv`
- `results/summary.md`

Intermediate caches are `results/deltarev.inference.jsonl`, `results/deltarev.gold.jsonl` (offline evaluation only), `results/baseline.jsonl`, `results/raw_proposals.jsonl`, and the optional shard work directories. Artifact coverage and contract diagnostics do not substitute for unavailable official delta accuracy or retrieval Recall/MRR.

## Historical work

The balanced60 and 303-item transition-card experiments, including their negative world-model result, remain documented in [`GATE_B_D_RESULTS.md`](GATE_B_D_RESULTS.md) and [`handoff/`](handoff/). They are debugging/comparison history, not a new untouched test set and not the current pipeline.
