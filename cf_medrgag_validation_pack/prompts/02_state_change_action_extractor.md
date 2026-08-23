# Prompt 02 — State, Decision Variable, and Action Extractor

## System

Extract a faithful structured representation from one medical item. Do not answer the item. Do not use information from an unseen paired item. Do not add medical facts that are not explicitly present. Represent missing values as `unknown`.

Return valid JSON only.

## Input

Question: {question}

Options: {options_or_null}

Patient trajectory or fixed evidence: {context_or_null}

## Output schema

```json
{
  "current_state": {
    "demographics": [],
    "conditions": [],
    "symptoms": [],
    "measurements": [],
    "temporal_facts": [],
    "completed_interventions": [],
    "medications": [],
    "contraindications_or_risks": [],
    "explicit_unknowns": []
  },
  "decision_goal": "...",
  "decision_determining_variables": [
    {"name": "...", "value": "...", "evidence_span": "..."}
  ],
  "candidate_actions_or_hypotheses": [
    {"id": "A", "text": "...", "type": "action|diagnosis|outcome|rule_judgment"}
  ],
  "observed_intervention": "string|null",
  "requested_transition_target": "applicability|immediate_observation|next_state|future_threshold|next_action|diagnosis_update|evidence_conclusion",
  "unsupported_inferences": []
}
```
