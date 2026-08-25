# CF-WM-MedRGAG Validation Pack

A reproducible evaluation plan for testing whether a world-model-style layer adds **counterfactual state/action reasoning** beyond MedRGAG's retrieval–generation–selection pipeline.

## Current result

The revised gold-free experiment is complete on 303 fresh, gold-unseen analysis items: MedPIC 78, CLIR 79, MedEinst 72 (36 official pairs), and MedCounterFact 74 (37 official pairs). `full_transition` scored 20.8%, below `medrgag_proxy` (31.7%), `direct_rank` (30.7%), and `structured_no_transition` (27.1%). Both transition shuffles were more accurate than the unshuffled method. The current implementation therefore does **not** establish a distinct world-model effect. Parser contracts were debugged on an initial 320-item draw before gold scoring, so this is not described as a pristine untouched held-out benchmark. See [`results/summary.md`](results/summary.md) for the result, confidence intervals, mechanism inspection, sensitivity analysis, and limitations.

The earlier balanced60 pilot and full work history remain in `GATE_B_D_RESULTS.md` and `handoff/`. Its M12 result is historical only: M12 read the answer label and is excluded from every revised comparison.

## Revised experiment

The revised runner is gold-free at inference time and uses the local Meta-Llama-3.1-8B-Instruct checkpoint through vLLM. It assumes Python 3 with the MedRGAG environment, a CUDA GPU, the local MedRGAG corpora/BM25 indexes, the local MedCPT checkpoint, and a real M2 selected/reranked-document JSONL with complete item coverage (zero to five documents per item). The local all-Llama baseline is reported as `medrgag_proxy`, not as an exact reproduction of the published MedRGAG configuration.

Run all 13 conditions with one command:

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/run_experiments.py \
  --inference results/heldout.inference.jsonl \
  --medrgag-documents results/medrgag_documents.jsonl \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --output-dir results
```

Evaluate the gold-free predictions by joining gold offline:

```bash
python3 scripts/evaluate.py \
  --predictions results/predictions.jsonl \
  --gold results/heldout.gold.jsonl \
  --mechanism-metrics results/mechanism_metrics.json \
  --metrics-csv results/metrics.csv \
  --metrics-json results/metrics.json \
  --summary results/summary.md \
  --seed 13 --bootstrap-samples 1000
```

Run the fixed 100-card automated mechanism inspection before evaluation when regenerating all outputs:

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/inspect_mechanism.py \
  --cards results/cards.jsonl \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --sample-size 100 --seed 13 \
  --output results/mechanism_judgments.jsonl \
  --summary results/mechanism_metrics.json
```

The methods are:

- `direct`: question and task-required patient/fixed evidence only.
- `medrgag_proxy`: the current local all-Llama MedRGAG-style selected evidence and reader.
- `decomposition_only`: state/action decomposition without transition prediction.
- `candidate_retrieval`: candidate-specific retrieval without transition cards.
- `direct_rank`: direct option or diagnosis-hypothesis ranking.
- `structured_no_transition`: structured present-state scoring without effects or next states.
- `equal_token_reasoning`: approximately matched auxiliary reasoning without transition prediction.
- `transition_no_comparator`: neutral transition cards passed directly to the reader.
- `full_transition`: grounded transition cards plus neutral comparison factors.
- `parametric_transition`: transition cards generated without retrieved evidence.
- `effect_shuffle`: candidate effects and related claims shuffled while preconditions remain fixed.
- `full_card_shuffle`: complete cards assigned to different candidates.
- `teacher_transition`: same-model, gold-free transition upper bound; not a label oracle.

The runner writes `results/predictions.jsonl` and `results/cards.jsonl`. Mechanism inspection writes `results/mechanism_judgments.jsonl` and `results/mechanism_metrics.json`. Evaluation writes `results/metrics.csv`, `results/metrics.json`, and `results/summary.md`. The fixed analysis inference/gold split and proxy documents needed for reproduction are also committed under `results/`.

## Recommended benchmark stack

1. **MedPIC-Bench** — primary static-text benchmark for patient-specific rule activation/deactivation and action applicability.
2. **CLIR-Bench** — strongest public benchmark for temporal state, intervention response, forecasting, decision making, and counterfactual evidence edits.
3. **MedEinst** — cross-domain test of diagnosis revision after minimal changes to discriminative patient evidence.
4. **MedCounterFact** — RAG/GAG-specific stress test for evidence–parametric-knowledge conflicts and unsafe/implausible counterfactual evidence.
5. **ReMedQA + CPV/MedEqualQA** — invariant/format controls; not evidence for a world-model claim by themselves.
6. **CLADDER** — optional formal causal sanity check for the standalone counterfactual module.
7. **CP-Env** — optional high-cost dynamic clinical-pathway validation after static/temporal pilots succeed.

## Main claim boundary

The public suite can test four distinct capabilities:

- conditional rule applicability;
- patient-state revision;
- intervention/temporal response reasoning;
- evidence-conflict handling.

No single public dataset proves a general clinical world model. Use the term **guideline-grounded textual clinical world-model layer** only if the full model beats decomposition, extra-retrieval, and equal-compute baselines and passes causal-edit/shuffle tests.

## Package contents

- `PROJECT_PLAN.md`: complete Chinese research plan.
- `GATE_A_RESULTS.md`: real public-source Gate-A run, audit result, and stop decision.
- `GATE_B_D_RESULTS.md`: real balanced60 Gate B–D results and final NO-GO decision.
- `handoff/`: current state, experiment chronology, upload inventory, hashes, and visible agent transcripts.
- `AGENTS.md`: coding-agent constraints and project invariants.
- `datasets/DATASET_MATRIX.md`: selection rationale and adaptation rules.
- `prompts/`: executable prompt templates.
- `configs/`: dataset, experiment, and go/no-go manifests.
- `schemas/unified_item.schema.json`: common record format.
- `scripts/validate_manifest.py`: basic leakage/schema checks.
- `scripts/run_experiments.py`: revised gold-free experiment runner.
- `scripts/evaluate.py`: offline gold join, metrics, bootstrap comparisons, and summary writer.
- `scripts/inspect_mechanism.py`: automated transition-grounding and leakage inspection.
- `references/SOURCES.md`: official paper/dataset locations.
