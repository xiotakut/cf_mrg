# Revised counterfactual / transition experiment

## Result

The result is **negative for the world-model hypothesis**. On the 303-item fresh, gold-unseen analysis, `full_transition` reached 63/303 (20.8%), below `medrgag_proxy` at 96/303 (31.7%), `direct_rank` at 93/303 (30.7%), and `structured_no_transition` at 82/303 (27.1%). Candidate-effect and full-card shuffling did not reduce accuracy: on the 150 items where within-item shuffling was defined, both shuffled conditions were more accurate than `full_transition`.

This is not an exact reproduction of the published MedRGAG system. `medrgag_proxy` is the repository's local all-Llama retrieval/generation/selection proxy. The result supports neither a distinct transition-model benefit nor a general clinical world-model claim.

## Data and freeze policy

The initial fresh sample contained 320 items with zero overlap with `balanced60` or prior repository result artifacts. Seventeen items used while repairing parser contracts, plus complete-pair counterparts where applicable, were excluded before gold accuracy was inspected. The final fixed analysis contains 303 items:

| Dataset / task | Items | Official complete pairs |
|---|---:|---:|
| MedPIC action selection | 78 | unavailable |
| CLIR prospective intervention response | 40 | unavailable |
| CLIR next-value interval forecasting | 39 | unavailable |
| MedEinst diagnosis state update | 72 | 36 |
| MedCounterFact evidence-world reasoning | 74 | 37 |
| **Total** | **303** | **73** |

Because parser/prompt contracts were repaired after inspecting outputs from the initial 320, this is a fresh gold-unseen analysis after pre-accuracy contract debugging, not a pristine untouched held-out benchmark. Triggering items were excluded without consulting correctness, and no item was removed after the final freeze.

CLIR t7 and t10 were not used because the available public inference records contain no pre-anchor patient observations after target fields are removed. No pair mapping, temporal evidence, activation label, or safety label was guessed.

## Implementation note

- The historical M12 path read the answer/correct candidate and was a label oracle. Its active functions and CLI method were removed from `scripts/run_gate_b.py`; historical artifacts remain explicitly labeled invalid for revised analysis.
- `teacher_transition` is gold-free and emits only nine neutral transition fields. It is a same-Llama prompt upper bound, not a gold oracle and not a stronger external-model upper bound.
- A task router separates action selection, option-hidden outcome prediction, prospective temporal forecasting, diagnosis state update, and fixed-evidence-world reasoning.
- Action cards are generated independently without labels or competing option text. Fixed-action outcome options are hidden until a separate matcher runs. MedCounterFact keeps the local evidence conclusion separate from the real-world safety flag.
- Missing or invalid evidence citations remain empty and unsupported. Claim/evidence entailment is judged from the cited text rather than from ID presence.
- Final readers use dataset-specific provenance-aware schemas. Reader citations are filtered to actual input evidence IDs.
- The controls are direct, local MedRGAG proxy, decomposition only, candidate retrieval, direct rank, structured no-transition, and approximately equal-token reasoning. The transition variants include no-comparator, full, parametric, effect shuffle, full-card shuffle, and gold-free teacher.
- The runner permits one JSON repair. A second contract failure is persisted as `prediction=null` and counted wrong; it is never silently replaced.

## Main results

Token totals are observed per-condition attribution from runner records; shared state/card calls can be attributed to more than one condition and therefore must not be summed as a wall-clock execution total.

| Method | Correct / 303 | Accuracy | Parse failures | Attributed tokens |
|---|---:|---:|---:|---:|
| `direct` | 94 | 31.0% | 1 | 1.09M |
| `medrgag_proxy` | 96 | 31.7% | 10 | 1.23M |
| `decomposition_only` | 98 | **32.3%** | 6 | 1.47M |
| `candidate_retrieval` | 89 | 29.4% | 32 | 1.46M |
| `direct_rank` | 93 | 30.7% | 2 | 1.49M |
| `structured_no_transition` | 82 | 27.1% | 25 | 2.57M |
| `equal_token_reasoning` | 81 | 26.7% | 12 | 3.75M |
| `transition_no_comparator` | 70 | 23.1% | 49 | 2.84M |
| `full_transition` | 63 | 20.8% | 64 | 3.83M |
| `parametric_transition` | 55 | 18.2% | 23 | 3.18M |
| `effect_shuffle` | 67 | 22.1% | 43 | 3.85M |
| `full_card_shuffle` | 69 | 22.8% | 22 | 3.86M |
| `teacher_transition` | 59 | 19.5% | 72 | 2.32M |

The approximately token-matched non-transition control averaged 12,373 attributed tokens/item, versus 12,650 for `full_transition`, and was 5.9 percentage points more accurate.

## Paired comparisons

Confidence intervals use 1,000 paired bootstrap resamples. Shuffle comparisons include only the 150 MedPIC/MedEinst items where within-item shuffling is meaningful; fixed-action CLIR/MedCounterFact rows are marked not applicable.

| Difference | n | Delta | 95% CI |
|---|---:|---:|---:|
| full − `medrgag_proxy` | 303 | −10.9 pp | [−15.5, −5.9] |
| full − `direct_rank` | 303 | −9.9 pp | [−15.8, −4.0] |
| full − `structured_no_transition` | 303 | −6.3 pp | [−11.6, −1.3] |
| full − `equal_token_reasoning` | 303 | −5.9 pp | [−10.9, −1.3] |
| full − `transition_no_comparator` | 303 | −2.3 pp | [−4.6, −0.3] |
| full − `effect_shuffle` | 150 | −2.7 pp | [−6.0, 0.0] |
| full − `full_card_shuffle` | 150 | −4.0 pp | [−8.0, −0.7] |
| full − `parametric_transition` | 303 | +2.6 pp | [−2.0, +7.3] |

## Dataset results

| Method | MedPIC (78) | CLIR (79) | MedEinst (72) | MedCounterFact (74) |
|---|---:|---:|---:|---:|
| `medrgag_proxy` | 21.8% | 27.8% | 8.3% | 68.9% |
| `direct_rank` | 29.5% | 27.8% | 4.2% | 60.8% |
| `structured_no_transition` | 17.9% | 21.5% | 1.4% | 67.6% |
| `equal_token_reasoning` | 16.7% | 25.3% | 1.4% | 63.5% |
| `transition_no_comparator` | 24.4% | 16.5% | 1.4% | 50.0% |
| `full_transition` | 14.1% | 17.7% | 1.4% | 50.0% |
| `parametric_transition` | 24.4% | 22.8% | 1.4% | 23.0% |
| `effect_shuffle` | 19.2% | 17.7% | 1.4% | 50.0% |
| `full_card_shuffle` | 20.5% | 17.7% | 2.8% | 50.0% |

`full_transition` did not beat both ranking and structured controls on either MedPIC or CLIR. Its CLIR intervention-response / interval-forecast accuracies were 15.0% / 20.5%, versus 22.5% / 33.3% for the proxy and 32.5% / 23.1% for direct rank. Grounded cards only clearly exceeded parametric cards on MedCounterFact; they were worse on MedPIC and CLIR.

For the 37 official MedCounterFact pairs, both-correct accuracy was 16/37 (43.2%) for full transition, 22/37 (59.5%) for the proxy, 18/37 (48.6%) for direct rank, and 20/37 (54.1%) for structured no-transition. MedCounterFact safety labels are null in the available gold, so safety-flag accuracy is unavailable.

## Mechanism inspection

A fixed seed-13 sample of 100 `full_transition` cards (39 MedPIC, 36 MedEinst, 16 MedCounterFact, 9 CLIR) produced 1,567 claims for the automated evidence judge.

| Metric | Result |
|---|---:|
| Claims with a valid citation | 598/1,567 (38.2%) |
| Entailed among cited claims | 400/598 (66.9%) |
| Unsupported claims | 953/1,567 (60.8%) |
| Contradicted claims | 150/1,567 (9.6%) |
| Hard prohibited-string matches | 0/1,567 (0.0%) |
| Judge-flagged option leakage | 34/1,567 (2.2%) |

The hard scan found no `correct answer`, `gold answer`, or equivalent prohibited strings. The 2.2% judge flag is reported separately because automated comments indicate some flags may reflect incorrect/unsupported claims rather than confirmed answer leakage.

## Failure accounting and sensitivity

The online run recorded 35 one-repair contract failures. Post-run schema inspection found another 326 MedEinst method-rows whose reader copied the literal schema example `concise diagnosis`; these were uniformly changed to explicit parse failures and counted wrong, without consulting gold or changing the sample. The future runner now rejects that placeholder. Because this affects methods unevenly, MedEinst is not used as evidence for or against the transition mechanism in the scientific interpretation.

The negative result is not caused by this correction:

| Sensitivity analysis | full | proxy | direct rank | structured | effect shuffle | full-card shuffle |
|---|---:|---:|---:|---:|---:|---:|
| Exclude MedEinst (n=231) | 26.8% | 39.0% | 39.0% | 35.1% | 28.6% | 29.0% |
| Exclude every item with any parse failure (n=226) | 27.0% | 39.4% | 39.8% | 35.0% | 28.3% | 28.8% |

On pairwise complete cases, full remained below proxy by 11.7 pp, direct rank by 11.7 pp, and structured scoring by 7.6 pp. These are diagnostic sensitivities; the primary table conservatively counts every failure as wrong.

## Answers to the research questions

1. **Versus MedRGAG proxy:** no; −10.9 pp.
2. **Versus direct ranking:** no; −9.9 pp.
3. **Versus structured scoring:** no; −6.3 pp.
4. **Effect shuffle:** no degradation; the shuffle was +2.7 pp relative to full.
5. **Full-card shuffle:** no degradation; the shuffle was +4.0 pp relative to full.
6. **Grounding versus parametric cards:** mixed by dataset and only +2.6 pp overall with a CI crossing zero; grounding quality was weak.
7. **Benefiting datasets/tasks:** none established against both required controls; MedCounterFact was the only clear grounded-over-parametric slice.
8. **Claim support:** insufficient—only 38.2% cited and 60.8% unsupported.
9. **Scientific conclusion:** negative. This implementation does not establish a distinct world-model effect.

## Metric availability and limitations

- MedPIC activation/deactivation and guideline labels were unavailable, so only exact-set accuracy is reported.
- CLIR t7/t10, official pairs, and supporting-timestamp labels were unavailable; only prospective t6 and t8 metrics are reported.
- MedCounterFact safety labels and generated-context contamination labels were unavailable; those metrics are omitted.
- MedEinst's open-diagnosis reader contract failed systematically. Its primary rows remain for transparency, but conclusions rely on the non-MedEinst sensitivity.
- The teacher uses the same local Llama model, not a stronger external teacher. It is gold-free but not a true capability upper bound.
- This is one model and one fresh gold-unseen sample after contract debugging. Bootstrap intervals quantify item sampling uncertainty, not model/seed variation.
- The proxy's precomputed KGCC/KADS token cost is outside runner token logs. Batched transition failures can also omit discarded sibling-generation tokens.

Detailed overall, dataset, task, pair, token, sensitivity, and bootstrap results are in `metrics.json`; per-item outputs are in `predictions.jsonl`, transition cards in `cards.jsonl`, and automated judgments in `mechanism_judgments.jsonl`.

## Commands used

```bash
CUDA_VISIBLE_DEVICES=0 python3 scripts/run_experiments.py \
  --inference results/heldout.inference.jsonl \
  --medrgag-documents results/medrgag_documents.jsonl \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct \
  --output-dir results

CUDA_VISIBLE_DEVICES=0 python3 scripts/inspect_mechanism.py \
  --cards results/cards.jsonl --sample-size 100 --seed 13 \
  --model /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct

python3 scripts/evaluate.py \
  --predictions results/predictions.jsonl \
  --gold results/heldout.gold.jsonl \
  --mechanism-metrics results/mechanism_metrics.json \
  --metrics-csv results/metrics.csv \
  --metrics-json results/metrics.json \
  --summary results/summary.md \
  --seed 13 --bootstrap-samples 1000
```
