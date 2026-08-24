# Prompt 05 — Candidate Rollout Comparator

## System

Compare candidate rule/transition cards against the current patient state and decision goal. Do not reward verbosity. Penalize unsupported claims and evidence contradictions. Select all correct options for multi-select tasks.

Return valid JSON only.

## Input

Question: {question}

Options: {options_or_null}

Current state: {state_json}

Transition cards: {transition_cards}

## Output schema

```json
{
  "candidate_scores": [
    {
      "candidate_id": "A",
      "precondition_fit": 0.0,
      "state_consistency": 0.0,
      "effect_consistency": 0.0,
      "evidence_support": 0.0,
      "harm_or_contradiction_penalty": 0.0,
      "uncertainty_penalty": 0.0,
      "total": 0.0
    }
  ],
  "selected_candidate_ids": ["A"],
  "causal_determinants": [
    {"state_variable": "...", "why_it_changes_or_preserves_the_decision": "...", "evidence_ids": []}
  ],
  "comparison_valid": true
}
```
