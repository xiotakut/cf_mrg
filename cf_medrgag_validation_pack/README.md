# CF-WM-MedRGAG Validation Pack

A reproducible evaluation plan for testing whether a world-model-style layer adds **counterfactual state/action reasoning** beyond MedRGAG's retrieval–generation–selection pipeline.

## Agent handoff

The real balanced60 run is complete and stopped after a Gate-D NO-GO. A new agent should start with `handoff/AGENT_HANDOFF.md`; the full attempt history is in `handoff/EXPERIMENT_CHRONOLOGY.md`, and committed artifacts are under `results/gate-b-real-20260824-seed13-v4/`.

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
- `references/SOURCES.md`: official paper/dataset locations.
