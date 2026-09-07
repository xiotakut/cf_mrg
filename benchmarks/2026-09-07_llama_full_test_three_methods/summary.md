# Cross-benchmark all-Llama baseline screening

Status: **complete**; unique method predictions 75840/75840.

Evaluation scope: entire official test/released evaluation data; no source-group sampling.

Current batch completes the previously stopped M0/M1 readers on the exact same entire test set. All 25,280 M2 predictions and their stages are inherited unchanged. Full three-method results are now compared; current batch wall time covers only the missing M0/M1 calls.

Local baseline and exact stage contract: [baseline_contract.md](baseline_contract.md). Public source revisions and release discrepancies: [acquisition.md](acquisition.md).

## Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M0 | 13512 | 61.59% | [58.86%, 64.24%] | 61.60% | 17 | 1202/1202 |
| cpv | M1 | 13512 | 63.78% | [61.08%, 66.58%] | 63.85% | 0 | 1202/1202 |
| cpv | M2 | 13512 | 67.09% | [64.89%, 69.35%] | 67.20% | 6 | 1202/1202 |
| cultural | M0 | 1500 | 62.53% | [55.67%, 69.60%] | 62.53% | 9 | 150/150 |
| cultural | M1 | 1500 | 61.53% | [54.73%, 68.60%] | 61.53% | 3 | 150/150 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M0 | 1012 | 66.31% | [60.20%, 72.22%] | 66.30% | 0 | 203/203 |
| medcounterfact | M1 | 1012 | 61.87% | [55.96%, 67.78%] | 61.86% | 0 | 203/203 |
| medcounterfact | M2 | 1012 | 66.50% | [60.59%, 72.12%] | 66.50% | 0 | 203/203 |
| medeinst | M0 | 10766 | 10.93% | [10.39%, 11.48%] | 10.93% | 6427 | 5383/5383 |
| medeinst | M1 | 10766 | 7.75% | [7.26%, 8.23%] | 7.75% | 8579 | 5383/5383 |
| medeinst | M2 | 10766 | 8.26% | [7.76%, 8.75%] | 8.26% | 7817 | 5383/5383 |
| medpic | M0 | 467 | 35.97% | [31.69%, 40.26%] | 35.97% | 10 | 467/467 |
| medpic | M1 | 467 | 36.83% | [32.55%, 41.11%] | 36.83% | 1 | 467/467 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

## Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M0 | 12310/1202 | 0.07 pp | [-0.54, 0.68] pp | NA / 0 |
| cpv/native | M1 | 12310/1202 | 0.58 pp | [-0.38, 1.56] pp | NA / 0 |
| cpv/native | M2 | 12310/1202 | 0.33 pp | [-1.34, 2.08] pp | NA / 0 |
| cultural/native | M0 | 1350/150 | 2.37 pp | [-0.81, 5.41] pp | NA / 0 |
| cultural/native | M1 | 1350/150 | -0.22 pp | [-4.07, 3.78] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M0 | 809/203 | 1.48 pp | [-1.35, 4.43] pp | NA / 0 |
| medcounterfact/native | M1 | 809/203 | 3.94 pp | [-0.25, 8.13] pp | NA / 0 |
| medcounterfact/native | M2 | 809/203 | 0.62 pp | [-3.33, 4.68] pp | NA / 0 |
| medeinst/derived_four_way | M0 | 60/60 | 0.00 pp | [-20.00, 21.67] pp | 64.29% / 28 |
| medeinst/derived_four_way | M1 | 60/60 | -10.00 pp | [-28.33, 10.00] pp | 60.87% / 23 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-28.37, 8.33] pp | 43.33% / 30 |
| medeinst/native | M0 | 5383/5383 | 5.59 pp | [4.38, 6.80] pp | 84.17% / 739 |
| medeinst/native | M1 | 5383/5383 | 1.60 pp | [0.58, 2.66] pp | 47.61% / 460 |
| medeinst/native | M2 | 5383/5383 | 1.80 pp | [0.74, 2.86] pp | 40.37% / 493 |

## Changes relative to Direct and retrieval-only
| Benchmark/protocol | Comparison | Source groups | Source-mean score gain | 95% CI | Introduced errors / items | Conditional harm |
|---|---|---:|---:|---|---:|---:|
| cpv/native | M1-M0 | 1202 | 2.19% | [0.17, 4.15] pp | 909/13512 | 10.92% |
| cpv/native | M2-M0 | 1202 | 5.50% | [3.60, 7.34] pp | 957/13512 | 11.50% |
| cpv/native | M2-M1 | 1202 | 3.31% | [1.47, 5.20] pp | 1178/13512 | 13.65% |
| cultural/native | M1-M0 | 150 | -1.00% | [-6.13, 3.87] pp | 135/1500 | 14.39% |
| cultural/native | M2-M0 | 150 | 3.60% | [-0.60, 7.80] pp | 118/1500 | 12.58% |
| cultural/native | M2-M1 | 150 | 4.60% | [-0.00, 9.27] pp | 140/1500 | 15.17% |
| medcounterfact/native | M1-M0 | 203 | -4.43% | [-7.19, -2.07] pp | 67/1012 | 9.99% |
| medcounterfact/native | M2-M0 | 203 | 0.20% | [-1.97, 2.56] pp | 36/1012 | 5.37% |
| medcounterfact/native | M2-M1 | 203 | 4.63% | [2.17, 7.19] pp | 31/1012 | 4.95% |
| medeinst/derived_four_way | M1-M0 | 60 | -3.33% | [-10.83, 4.17] pp | 13/120 | 23.21% |
| medeinst/derived_four_way | M2-M0 | 60 | 8.33% | [0.83, 15.83] pp | 7/120 | 12.50% |
| medeinst/derived_four_way | M2-M1 | 60 | 11.67% | [3.33, 20.83] pp | 9/120 | 17.31% |
| medeinst/native | M1-M0 | 5383 | -3.19% | [-3.79, -2.56] pp | 741/10766 | 62.96% |
| medeinst/native | M2-M0 | 5383 | -2.68% | [-3.21, -2.07] pp | 616/10766 | 52.34% |
| medeinst/native | M2-M1 | 5383 | 0.51% | [-0.04, 1.05] pp | 425/10766 | 50.96% |
| medpic/native | M1-M0 | 467 | 0.86% | [-1.71, 3.64] pp | 20/467 | 11.90% |
| medpic/native | M2-M0 | 467 | -5.14% | [-8.99, -1.50] pp | 53/467 | 31.55% |
| medpic/native | M2-M1 | 467 | -6.00% | [-10.06, -2.14] pp | 56/467 | 32.56% |

Gain intervals use source means. Introduced-error and conditional-harm columns retain their specified item-level denominators; for M2−M1, the comparator is M1. Positive paired amplification means greater reference-to-variant sensitivity than Direct; it is not a causal finding.

| Benchmark/protocol | Method | Drop amplification vs Direct | 95% CI |
|---|---|---:|---|
| cpv/native | M1 | 0.52 pp | [-0.61, 1.67] pp |
| cpv/native | M2 | 0.26 pp | [-1.49, 2.06] pp |
| cultural/native | M1 | -2.59 pp | [-6.96, 2.00] pp |
| cultural/native | M2 | -2.52 pp | [-8.37, 3.19] pp |
| medcounterfact/native | M1 | 2.46 pp | [-1.35, 6.04] pp |
| medcounterfact/native | M2 | -0.86 pp | [-4.43, 2.46] pp |
| medeinst/derived_four_way | M1 | -10.00 pp | [-25.00, 5.00] pp |
| medeinst/derived_four_way | M2 | -10.00 pp | [-26.67, 5.04] pp |
| medeinst/native | M1 | -3.99 pp | [-5.22, -2.79] pp |
| medeinst/native | M2 | -3.79 pp | [-4.87, -2.69] pp |

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
Recorded main-run LLM requests (including frozen sensitivity inputs): 379200; prompt tokens: 481617579; completion tokens: 77700293. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches cause evidence loss that explains M2−M1 changes within the same source question. Current empty-selection/document-count records motivate this question but do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 483767326 logical prompt tokens and 77827615 completion tokens. Exact visible-input deduplication removes 2097 duplicate tasks and avoids 31455 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

## Execution and parsing details
Formal concurrent batch elapsed: 0.75 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 379730. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M0 | 17 | 0 | 0 | 0 |
| cpv | M1 | 0 | 0 | 0 | 0 |
| cpv | M2 | 6 | 0 | 0 | 0 |
| cultural | M0 | 9 | 0 | 0 | 0 |
| cultural | M1 | 3 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M0 | 0 | 0 | 0 | 5 |
| medcounterfact | M1 | 0 | 0 | 0 | 31 |
| medcounterfact | M2 | 0 | 0 | 0 | 15 |
| medeinst | M0 | 11 | 6416 | 10 | 0 |
| medeinst | M1 | 7 | 8572 | 7 | 0 |
| medeinst | M2 | 68 | 7749 | 68 | 0 |
| medpic | M0 | 10 | 0 | 0 | 0 |
| medpic | M1 | 1 | 0 | 0 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

## Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M0 | reference | 60 | 31.67% | [20.00, 45.00] pp |
| M0 | variant | 60 | 38.33% | [25.00, 51.67] pp |
| M1 | reference | 60 | 33.33% | [21.67, 45.00] pp |
| M1 | variant | 60 | 43.33% | [30.00, 56.67] pp |
| M2 | reference | 60 | 38.33% | [26.67, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 2561, 1: 10, 2: 28, 3: 37, 4: 130, 5: 22514}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](findings.md), [validation.json](validation.json).

Full-test reader completion: 38896 newly executed requests; 33914033 prompt tokens; 339142 completion tokens. Aggregate workload above includes prior screening stages reused by exact input equality. The fixed auxiliary 20-input repeat is inherited from the earlier screening subset, not a new random sample of the enlarged test population. See cache_reuse.json and prior_run_efficiency.json for exact reuse and prior-cost provenance.
