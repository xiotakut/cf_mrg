# Public Dataset Matrix

| Dataset | Public resource | Core capability | Compatibility with MedRGAG | World-model value | Primary limitation |
|---|---|---|---|---|---|
| MedPIC-Bench | `TIM0927/MedPIC-Bench` | rule activation/deactivation under patient changes | Very high | L1 applicability/precondition | medication safety only; weak next-state rollout |
| CLIR-Bench | `winall/CLIR-Bench` | irregular temporal evidence, intervention response, forecast, next action, causal edits | Medium; requires time-series adapter | Highest for `(s,a)->s'` | derived ICU QA; viewer currently has schema error |
| MedEinst | `zhui711/MedEinst` | diagnosis flip after minimal discriminative-evidence change | High for textual input | state-update generalization | diagnosis, not action transition |
| MedCounterFact | `KaijieMo-kj/Counterfactual-Medical-Evidence` | conflict between supplied evidence, priors and safety | High for KGCC/KADS stress test | evidence-world consistency | not a patient transition benchmark |
| ReMedQA | `disi-unibo-nlp/ReMedQA` | MCQ/open/format perturbation robustness | Very high | negative control | not causal counterfactual |
| CPV / MedEqualQA / FairMedQA | public GitHub/HF releases | demographic counterfactual invariance/bias | High | negative control | answers usually should not change |
| CLADDER | `causalNLP/cladder` | formal SCM counterfactual reasoning | Low end-to-end; high module-level | causal sanity test | non-medical synthetic text |
| CP-Env | `SPIRAL-MED/CP_ENV` | dynamic clinical pathways and tool use | Low; requires agent wrapper | optional L3 pathway test | expensive; not paired static QA |

## Recommended core suite

### Minimal publishable diagnosis suite

- MedPIC-Bench
- MedEinst
- MedCounterFact
- ReMedQA or CPV control

### Strong world-model suite

- MedPIC-Bench
- CLIR-Bench IR + forecasting + decision + official counterfactual edits
- MedEinst
- MedCounterFact
- ReMedQA/CPV controls
- CLADDER module sanity

## Adaptation principles

1. Do not flatten all datasets into identical single-choice MCQ if that destroys the official task.
2. A unified internal schema may coexist with dataset-specific output parsers.
3. Pair members are independent at inference and grouped only for metrics.
4. Distinguish answer-changing counterfactuals from answer-invariant perturbations.
5. Distinguish in-world evidence faithfulness from real-world clinical safety.
6. Distinguish observed intervention response from normative guideline recommendation.
