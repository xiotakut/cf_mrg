# Prompt 07 — Transition and Provenance Judge

## System

Judge a model trace against the item and gold evidence. You may see the gold answer because this is offline evaluation, never inference. Score only what is supported. Return valid JSON only.

## Input

Item: {item_without_hidden_pair_counterpart}

Gold answer/evidence: {gold}

Model trace: {trace}

## Output schema

```json
{
  "state_extraction_correct": 0,
  "decision_variable_identified": 0,
  "precondition_correct": 0,
  "effect_or_next_state_correct": 0,
  "temporal_order_correct": 0,
  "evidence_entailment": 0,
  "provenance_correct": 0,
  "option_leakage_detected": false,
  "counterfactual_normalization_detected": false,
  "unsupported_medical_claim_detected": false,
  "final_answer_consistent_with_trace": 0,
  "error_tags": [],
  "justification": "concise"
}
```

Use integer scores 0 or 1 unless a field is not applicable, in which case use `null`.
