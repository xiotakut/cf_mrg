# Cross-benchmark all-Llama baseline screening

Status: **complete**; unique method predictions 25280/25280.

Evaluation scope: entire official test/released evaluation data; no source-group sampling.

Local baseline and exact stage contract: [baseline_contract.md](baseline_contract.md). Public source revisions and release discrepancies: [acquisition.md](acquisition.md).

## Native primary results
| Benchmark | Method | N | Source-mean score | 95% CI | Micro score | Invalid | Complete/planned groups |
|---|---|---:|---:|---|---:|---:|---:|
| cpv | M2 | 13512 | 67.09% | [64.89%, 69.35%] | 67.20% | 6 | 1202/1202 |
| cultural | M2 | 1500 | 66.13% | [60.60%, 71.80%] | 66.13% | 1 | 150/150 |
| medcounterfact | M2 | 1012 | 66.50% | [60.59%, 72.12%] | 66.50% | 0 | 203/203 |
| medeinst | M2 | 10766 | 8.26% | [7.76%, 8.75%] | 8.26% | 7817 | 5383/5383 |
| medpic | M2 | 467 | 30.84% | [26.77%, 34.90%] | 30.84% | 4 | 467/467 |

MedCounterFact score is evidence agreement, not clinical accuracy or safety. MedEinst score is deterministic canonical matching, not the official semantic evaluator. Extra sensitivity-only native cases are excluded from this primary table.

## Paired effects
| Benchmark/protocol | Method | Pairs / groups | Source-mean drop | 95% CI | BTR / denominator |
|---|---|---:|---:|---|---:|
| cpv/native | M2 | 12310/1202 | 0.33 pp | [-1.34, 2.08] pp | NA / 0 |
| cultural/native | M2 | 1350/150 | -0.15 pp | [-5.56, 5.11] pp | NA / 0 |
| medcounterfact/native | M2 | 809/203 | 0.62 pp | [-3.33, 4.68] pp | NA / 0 |
| medeinst/derived_four_way | M2 | 60/60 | -10.00 pp | [-28.37, 8.33] pp | 43.33% / 30 |
| medeinst/native | M2 | 5383/5383 | 1.80 pp | [0.74, 2.86] pp | 40.37% / 493 |

## Method scope
Only MedRGAG-Llama base (M2) is required after the explicit user scope correction. Previously completed Direct/retrieval-only outputs are preserved in auxiliary_predictions.jsonl and are not completed full-test comparisons. No cross-method amplification is estimated in this report.

| MedPIC method | GF / CF N | Unpaired GF−CF gap | 95% CI |
|---|---:|---:|---|
| M2 | 284/183 | 14.76 pp | [6.63, 22.90] pp |

MedPIC GF−CF is an unpaired composition gap; no pair mapping is fabricated. Cultural has no released Neutral condition; only Original comparisons are possible.

## Interpretation and limits
The three semantic domains are reported separately. The cross-source taxonomy is NOT_IDENTIFIABLE: operation tags lack independent compatible source coverage and are confounded with dataset/source/format. CPV and Cultural are both MedQA constructions. Within-Cultural Id/Context contrasts do not establish independent clinical-source replication.

Errors, correct revision/preservation, stable/changed wrong outputs and old-answer persistence are retained in transitions.csv. Invalid completed responses count wrong; missing requests remain incomplete. Neither a positive amplification nor retrieval overlap establishes a causal retrieval failure or clinical harm.

Native/derived, exposure, quality-flag and source-overlap sensitivities are in sensitivities.json; the 20-input independent-seed estimate is in seed_repeat.json. No best-seed selection, ensemble, new judge, Profile or sidecar was run.

## Cost and next research decision
Recorded LLM requests (including frozen sensitivity and preserved auxiliary readers): 340304; prompt tokens: 447703546; completion tokens: 77361151. See efficiency.csv and commands.sh for concurrency and wall-clock provenance.
One follow-up worth testing is whether original KADS output/parser format mismatches explain evidence loss associated with M2 reference/variant prediction changes. These saved stage proxies do not establish causation; no parser repair or new method is evaluated here.

A completed run establishes execution completeness, not that every benchmark degrades or that the taxonomy is validated.

All recorded workloads including superseded attempts: 449853293 logical prompt tokens and 77488473 completion tokens. Exact visible-input deduplication removes 2097 duplicate tasks and avoids 27261 LLM requests. Logical prompt tokens include cached prefixes; they are not a count of physically recomputed prefill tokens.

## Execution and parsing details
Formal concurrent batch elapsed: 15.53 h. Including seed-repeat and superseded smoke attempts, recorded LLM requests: 340834. Full stage token counts, queue times, truncation counts and worker cache hits are retained in metrics.json and efficiency.csv.
Independent-seed repeat: 20/20 executed, 20 matched completed primary inputs, semantic flips 36.84% among 19 valid comparisons; raw-output changes 50.00%. This estimate does not alter primary scores.

| Native benchmark | Method | Format invalid | Unmapped diagnosis | Ambiguous | Uncertainty |
|---|---|---:|---:|---:|---:|
| cpv | M2 | 6 | 0 | 0 | 0 |
| cultural | M2 | 1 | 0 | 0 | 0 |
| medcounterfact | M2 | 0 | 0 | 0 | 15 |
| medeinst | M2 | 68 | 7749 | 68 | 0 |
| medpic | M2 | 4 | 0 | 0 | 0 |

Unmapped diagnosis is a valid JSON diagnosis outside the frozen canonical mapping, distinct from malformed output. It counts wrong in canonical screening; no outcome-driven medical aliases were added. Ambiguous answers are included in format-invalid counts. Uncertainty is a legal MedCounterFact answer and is reported separately.

## Frozen MedEinst format sensitivity
| Method | Role | Matched inputs | Four-way minus native score | 95% CI |
|---|---|---:|---:|---|
| M2 | reference | 60 | 38.33% | [26.67, 51.67] pp |
| M2 | variant | 60 | 56.67% | [45.00, 68.33] pp |

Original KADS/parser selected-document distribution: {0: 2561, 1: 10, 2: 28, 3: 37, 4: 130, 5: 22514}. Empty selections are retained local-baseline stage failures; all KGCC/generation/select requests and final readers still ran. No outcome-driven parser repair or document fallback was applied.

Interpretation, execution audit and limitations: [findings.md](findings.md), [validation.json](validation.json).

Full-test expansion: 283694 newly executed requests; 350655816 prompt tokens; 65839313 completion tokens. Aggregate workload above includes prior screening stages reused by exact input equality. The fixed auxiliary 20-input repeat is inherited from the earlier screening subset, not a new random sample of the enlarged test population. See cache_reuse.json for context-capacity provenance.
