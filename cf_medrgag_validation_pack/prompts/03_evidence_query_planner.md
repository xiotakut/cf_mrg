# Prompt 03 — Balanced Evidence Query Planner

## System

Create balanced retrieval queries for each candidate action or hypothesis. Do not favor an answer option. Use the same number of query categories per candidate. For `fixed_evidence_only`, output no external queries and instead identify which supplied evidence spans must be interpreted.

Return valid JSON only.

## Input

Task route: {task_route_json}

State/action representation: {state_action_json}

Available evidence policy: {retrieval_policy}

## Output schema

```json
{
  "per_candidate": [
    {
      "candidate_id": "A",
      "queries": {
        "precondition_or_indication": ["..."],
        "exception_or_deactivation": ["..."],
        "effect_or_next_observation": ["..."],
        "harm_or_monitoring": ["..."]
      },
      "fixed_evidence_targets": []
    }
  ],
  "balance_check": {
    "same_query_count_per_candidate": true,
    "option_label_words_removed": true
  }
}
```
