# AGENTS.md — CF-WM-MedRGAG

## Objective

Implement a reproducible evaluation of whether an explicit state–action–transition layer improves counterfactual medical reasoning beyond MedRGAG's retrieval, context generation, and document selection.

## Non-negotiable invariants

1. **No pair leakage.** Never expose the paired item, `pair_id`, counterpart label, change direction, or gold answer at inference time.
2. **No outcome-based selection.** Never select items because MedRGAG answered them incorrectly.
3. **Preserve official tasks.** MedPIC remains exact-set multi-select; MedEinst remains open diagnosis; CLIR remains its official MCQ/time-series format; MedCounterFact uses its supplied evidence.
4. **Fixed evidence for MedCounterFact.** External retrieval is disabled in the primary setting. The supplied RCT summaries define the in-world evidence. Real-world plausibility is scored separately.
5. **Patient data outranks priors.** In CLIR, observed timestamps and interventions are authoritative for the specific trajectory; medical documents provide priors but cannot overwrite observations.
6. **Equal-compute comparisons.** Hold reader, context limit, retrieval calls, document count, and output-token budget constant across M2–M11 whenever the comparison claims mechanism-level improvement.
7. **No option leakage into transition generation.** Default transition cards are generated without answer options. Options are visible only to the comparator/reader.
8. **No test prompt tuning.** Tune only on declared development samples. Freeze prompts and hashes before running official test sets.
9. **Version pinning.** Record dataset commit/hash, code commit, model revision, tokenizer revision, prompts, environment, and random seeds.
10. **Cache every stage.** Store retrieval results, summaries, missing-knowledge items, generated documents, selected documents, state cards, transition cards, and final predictions.
11. **Structured outputs only.** Validate every LLM output against JSON Schema; retry at most twice; then mark invalid rather than silently repairing semantics.
12. **Claim discipline.** Do not call the method a world model unless `configs/no_go.yaml` passes.

## Dataset routing

- `medpic`: conditional medication rule and action applicability.
- `clir`: temporal state, intervention response, forecasting, decision, and evidence-edit counterfactuals.
- `medeinst`: diagnosis revision under minimally changed discriminative evidence.
- `medcounterfact`: evidence–parametric conflict and safety boundary.
- `remedqa/cpv/medequalqa`: answer-invariant controls.
- `cladder`: formal causal sanity test only.

## Required experiment order

1. Validate adapters and leakage checks.
2. Run M0/M1/M2.
3. Run oracle M12 on a preregistered pilot.
4. If oracle passes, run M3/M4/M5 controls.
5. Only then run M6–M11.
6. Freeze results before any qualitative error selection.

## Logging fields

Every prediction must log:

- run ID, item ID, dataset and task family;
- method ID and seed;
- input hash and visible fields;
- retrieval queries and document IDs;
- generated and selected contexts with provenance;
- state/action/transition JSON;
- model revisions and generation parameters;
- raw response, parsed response, parse status;
- latency, prompt tokens, completion tokens, and call count.

## Evaluation safety

- Never present benchmark outputs as clinical advice.
- Do not infer real patient treatment from de-identified or synthetic benchmark cases.
- For toxic/non-medical MedCounterFact items, report both evidence-conditioned conclusion and real-world safety warning as separate fields.
