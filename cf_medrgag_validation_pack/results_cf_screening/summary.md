# Cross-benchmark all-Llama baseline screening

Status: **complete**; unique method predictions 11322/11322.

Local baseline and exact stage contract: [baseline_contract.md](baseline_contract.md). Public source revisions and release discrepancies: [acquisition.md](acquisition.md).

## Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M0 | 665 | 57.58% | [45.00%, 70.00%] | 57.14% | 0 | 60/60 |
| cpv | M1 | 665 | 59.85% | [47.88%, 71.67%] | 59.40% | 0 | 60/60 |
| cpv | M2 | 665 | 55.30% | [45.45%, 65.31%] | 54.89% | 0 | 60/60 |
| cultural | M0 | 1500 | 62.53% | [55.67%, 69.60%] | 62.53% | 9 | 150/150 |
| cultural | M1 | 1500 | 61.53% | [54.73%, 68.60%] | 61.53% | 3 | 150/150 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M0 | 400 | 67.25% | [57.50%, 76.50%] | 67.25% | 0 | 80/80 |
| medcounterfact | M1 | 400 | 63.75% | [54.25%, 73.00%] | 63.75% | 0 | 80/80 |
| medcounterfact | M2 | 400 | 66.75% | [57.49%, 75.50%] | 66.75% | 0 | 80/80 |
| medeinst | M0 | 600 | 10.83% | [8.66%, 13.17%] | 10.83% | 323 | 300/300 |
| medeinst | M1 | 600 | 9.00% | [7.00%, 11.33%] | 9.00% | 462 | 300/300 |
| medeinst | M2 | 600 | 7.67% | [5.83%, 10.00%] | 7.67% | 435 | 300/300 |
| medpic | M0 | 467 | 35.97% | [31.69%, 40.26%] | 35.97% | 10 | 467/467 |
| medpic | M1 | 467 | 36.83% | [32.55%, 41.11%] | 36.83% | 1 | 467/467 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

## Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M0 | 605/60 | -1.00 pp | [-4.00, 1.00] pp | NA / 0 |
| cpv/native | M1 | 605/60 | 2.00 pp | [-2.33, 7.33] pp | NA / 0 |
| cpv/native | M2 | 605/60 | -2.17 pp | [-10.67, 5.83] pp | NA / 0 |
| cultural/native | M0 | 1350/150 | 2.37 pp | [-0.81, 5.41] pp | NA / 0 |
| cultural/native | M1 | 1350/150 | -0.22 pp | [-4.07, 3.78] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M0 | 320/80 | 1.88 pp | [-2.50, 6.56] pp | NA / 0 |
| medcounterfact/native | M1 | 320/80 | 1.56 pp | [-5.62, 8.76] pp | NA / 0 |
| medcounterfact/native | M2 | 320/80 | -0.62 pp | [-7.19, 5.94] pp | NA / 0 |
| medeinst/derived_four_way | M0 | 60/60 | 0.00 pp | [-20.00, 20.04] pp | 64.29% / 28 |
| medeinst/derived_four_way | M1 | 60/60 | -10.00 pp | [-30.00, 10.00] pp | 60.87% / 23 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-30.00, 10.00] pp | 43.33% / 30 |
| medeinst/native | M0 | 300/300 | 6.33 pp | [1.33, 11.67] pp | 85.71% / 42 |
| medeinst/native | M1 | 300/300 | 4.00 pp | [-0.67, 8.67] pp | 51.52% / 33 |
| medeinst/native | M2 | 300/300 | 6.67 pp | [2.67, 10.67] pp | 45.45% / 33 |

## Changes relative to Direct and retrieval-only
| Benchmark/protocol | Comparison | Source groups | Source-mean score gain | 95% CI | Introduced errors / items | Conditional harm |
|---|---|---:|---:|---|---:|---:|
| cpv/native | M1-M0 | 60 | 2.27% | [-6.36, 10.91] pp | 45/665 | 11.84% |
| cpv/native | M2-M0 | 60 | -2.27% | [-10.45, 5.61] pp | 68/665 | 17.89% |
| cpv/native | M2-M1 | 60 | -4.55% | [-14.09, 4.85] pp | 100/665 | 25.32% |
| cultural/native | M1-M0 | 150 | -1.00% | [-6.13, 3.87] pp | 135/1500 | 14.39% |
| cultural/native | M2-M0 | 150 | 3.60% | [-0.60, 7.80] pp | 118/1500 | 12.58% |
| cultural/native | M2-M1 | 150 | 4.60% | [-0.00, 9.27] pp | 140/1500 | 15.17% |
| medcounterfact/native | M1-M0 | 80 | -3.50% | [-7.00, -0.25] pp | 24/400 | 8.92% |
| medcounterfact/native | M2-M0 | 80 | -0.50% | [-3.75, 2.75] pp | 14/400 | 5.20% |
| medcounterfact/native | M2-M1 | 80 | 3.00% | [-0.75, 6.50] pp | 14/400 | 5.49% |
| medeinst/derived_four_way | M1-M0 | 60 | -3.33% | [-11.67, 4.17] pp | 13/120 | 23.21% |
| medeinst/derived_four_way | M2-M0 | 60 | 8.33% | [0.83, 15.83] pp | 7/120 | 12.50% |
| medeinst/derived_four_way | M2-M1 | 60 | 11.67% | [3.33, 21.67] pp | 9/120 | 17.31% |
| medeinst/native | M1-M0 | 300 | -1.83% | [-4.33, 0.50] pp | 34/600 | 52.31% |
| medeinst/native | M2-M0 | 300 | -3.17% | [-5.33, -1.00] pp | 31/600 | 47.69% |
| medeinst/native | M2-M1 | 300 | -1.33% | [-3.50, 0.83] pp | 27/600 | 50.00% |
| medpic/native | M1-M0 | 467 | 0.86% | [-1.71, 3.64] pp | 20/467 | 11.90% |
| medpic/native | M2-M0 | 467 | -5.14% | [-8.99, -1.50] pp | 53/467 | 31.55% |
| medpic/native | M2-M1 | 467 | -6.00% | [-10.06, -2.14] pp | 56/467 | 32.56% |

Gain intervals use source means. Introduced-error and conditional-harm columns retain their specified item-level denominators; for M2−M1, the comparator is M1. Positive paired amplification means greater reference-to-variant sensitivity than Direct; it is not a causal finding.

| Benchmark/protocol | Method | Drop amplification vs Direct | 95% CI |
|---|---|---:|---|
| cpv/native | M1 | 3.00 pp | [-2.00, 8.67] pp |
| cpv/native | M2 | -1.17 pp | [-9.17, 6.50] pp |
| cultural/native | M1 | -2.59 pp | [-6.96, 2.00] pp |
| cultural/native | M2 | -2.52 pp | [-8.37, 3.19] pp |
| medcounterfact/native | M1 | -0.31 pp | [-6.88, 5.94] pp |
| medcounterfact/native | M2 | -2.50 pp | [-8.44, 3.44] pp |
| medeinst/derived_four_way | M1 | -10.00 pp | [-23.33, 5.00] pp |
| medeinst/derived_four_way | M2 | -10.00 pp | [-26.67, 6.67] pp |
| medeinst/native | M1 | -2.33 pp | [-7.33, 3.00] pp |
| medeinst/native | M2 | 0.33 pp | [-3.67, 4.34] pp |

| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |
|---|---:|---:|---|
| M0 | 284/183 | 16.92 pp | [8.52, 25.68] pp |
| M1 | 284/183 | 17.43 pp | [9.15, 26.19] pp |
| M2 | 284/183 | 14.76 pp | [6.63, 22.90] pp |

MedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.

## Interpretation and limits
The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.

Errors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.

Native/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.

## Cost and next research decision
Recorded main-run LLM requests (including frozen sensitivity inputs): 56610; prompt tokens: 97047730; completion tokens: 11521838. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches cause evidence loss that explains M2−M1 changes within the same source question. Current empty-selection/document-count records motivate this question but do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 99197477 logical prompt tokens and 11649160 completion tokens. Exact visible-input deduplication removes 96 duplicate tasks and avoids 1440 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

## Execution and parsing details
Formal concurrent batch elapsed: 4.53 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 57140. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M0 | 0 | 0 | 0 | 0 |
| cpv | M1 | 0 | 0 | 0 | 0 |
| cpv | M2 | 0 | 0 | 0 | 0 |
| cultural | M0 | 9 | 0 | 0 | 0 |
| cultural | M1 | 3 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M0 | 0 | 0 | 0 | 0 |
| medcounterfact | M1 | 0 | 0 | 0 | 7 |
| medcounterfact | M2 | 0 | 0 | 0 | 1 |
| medeinst | M0 | 0 | 323 | 0 | 0 |
| medeinst | M1 | 0 | 462 | 0 | 0 |
| medeinst | M2 | 3 | 432 | 3 | 0 |
| medpic | M0 | 10 | 0 | 0 | 0 |
| medpic | M1 | 1 | 0 | 0 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

## Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M0 | reference | 60 | 31.67% | [20.00, 43.37] pp |
| M0 | variant | 60 | 38.33% | [25.00, 51.67] pp |
| M1 | reference | 60 | 33.33% | [21.67, 45.00] pp |
| M1 | variant | 60 | 43.33% | [28.33, 56.67] pp |
| M2 | reference | 60 | 38.33% | [25.00, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 344, 1: 5, 2: 7, 3: 10, 4: 33, 5: 3375}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](findings.md), [validation.json](validation.json).
