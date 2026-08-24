# Prompt 06 — Provenance-Aware Final Reader

## System

Answer the benchmark item using the supplied evidence and transition analysis. Keep these information channels separate:

- patient-specific observations;
- externally retrieved medical evidence;
- generated background context;
- counterfactual in-world fixed evidence;
- unsupported parametric knowledge.

Do not let unsupported parametric knowledge override patient-specific observations or fixed in-world evidence. For MedCounterFact, provide both the evidence-conditioned conclusion and a separate real-world safety flag. Return valid JSON only.

## Input

Task route: {task_route}

Question: {question}

Options: {options_or_null}

Selected evidence: {selected_evidence}

State and transition analysis: {analysis}

## Output schema

```json
{
  "reasoning_summary": "brief, provenance-aware explanation",
  "answer_choice": ["A"],
  "open_answer": "string|null",
  "evidence_conclusion": "string|null",
  "real_world_safety_flag": "none|uncertain|implausible|unsafe|not_applicable",
  "supporting_evidence_ids": [],
  "confidence": 0.0,
  "insufficient_evidence": false
}
```
