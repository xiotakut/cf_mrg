# Prompt 08 — Pair-Level Evaluator Specification

Pair-level metrics should be deterministic code whenever gold labels are available. Do not use an LLM judge for answer flips.

For each pair, compute:

```json
{
  "base_correct": true,
  "counterfactual_correct": true,
  "pair_correct": true,
  "prediction_changed": true,
  "gold_changed": true,
  "correct_change": true,
  "correct_invariance": null,
  "persisted_base_label_in_cf": false,
  "direction": "activate|deactivate|diagnosis_flip|causal_flip|invariant"
}
```

Dataset-specific aggregates:

- MedPIC: exact-set pair accuracy, activation, deactivation, warning persistence.
- MedEinst: paired correct, Bias Trap Rate, control-label persistence.
- CLIR: causal flip rate, irrelevant-edit invariance, evidence reliance.
- MedCounterFact: factual/CF conclusion consistency, normalization, safety/evidence decomposition.
