# Experiment chronology

This is the operational history of the run, including attempts that were superseded. Exact visible agent messages are retained in `handoff/transcripts/`.

## 1. Repository and plan setup

- Cloned `https://github.com/xiotakut/cf_mrg` into the current workspace.
- The repository initially contained only `cf_medrgag_validation_pack.zip`.
- Inspected and extracted the archive into `cf_medrgag_validation_pack/`.
- The requested `/home/data3/txy/agent.md` did not exist. The applicable files found and read were `/home/data3/txy/AGENTS.md` and this pack's `AGENTS.md`.
- Used Ponytail Full: reused the existing MedRGAG checkout, environment, retrievers, prompt builders, and vLLM model rather than creating a parallel framework.

## 2. Initial SubAgent split

The work was split among result/source auditing, provenance/Gate-A audit, implementation/tests, runner mapping, and compute probing. Six completed SubAgent transcripts are stored under `handoff/transcripts/`:

- `result_audit`: initial plan/result audit;
- `code_test_audit`: Gate-A preparation implementation and tests;
- `provenance_audit`: Gate-A fail-closed audit implementation and tests;
- `source_hunt`: public source verification, scorer, balanced60 reference, independent result recomputation;
- `runner_map`: MedRGAG reuse map, Gate-D design, semantic audits, final artifact audit;
- `compute_probe`: GPU/model smoke tests, Gate-B/Gate-C/Gate-D implementation and real runs.

After the user explicitly said to focus on experimental results, further defensive-gap investigation stopped.

## 3. Public source findings and Gate A

- MedPIC-Bench: 467 public questions. The public files do not contain the paper's official 89-pair mapping, so official MedPIC PairAcc cannot be reconstructed.
- CLIR-Bench: 11 tasks × 600 rows. The public repository supplies QA/evidence records but not Full-TS trajectories or official counterfactual edit pairs.
- MedEinst: 5,383 valid test control/trap pairs. The raw train files contain 10,609 pairs, differing from the README count.
- MedCounterFact: 203 originals plus 809 replacements. The valid repository path is `KaijieMo-kj/Counterfactual-Medical-Evidence`.
- ReMedQA and CPV were usable. MEDEQUALQA's repository contained no dataset. FairMedQA was available from Zenodo rather than the assumed Hugging Face location.
- Missing official MedPIC/CLIR units were not fabricated. The pilot uses only materializable public tasks.

Gate-A v3 contains 6,577 rows:

| Dataset | Rows |
|---|---:|
| MedPIC | 467 |
| CLIR | 500 |
| MedEinst | 1,000 |
| MedCounterFact | 400 |
| ReMedQA | 1,200 |
| CPV | 3,010 |

The preparation/audit tests cover source revisions, artifact hashes, row counts, identity, pair blindness, gold separation, evidence availability, and control construction. Gate-A tests passed.

## 4. balanced60 and compute probe

The frozen seed-13 sample contains:

- MedPIC 10;
- CLIR 10: two each from t6–t10;
- MedEinst 20: ten complete two-member pairs;
- MedCounterFact 16: eight complete pairs, two per counterfactual category;
- ReMedQA 2 and CPV 2: row-level controls, not complete pairs.

The exact item list is `configs/balanced60_seed13.json`.

GPU/model probing established:

- GPUs 0–2 were free H20 devices; GPU 3 was occupied by another process and never used;
- local Llama-3.1-8B-Instruct loaded successfully through vLLM 0.8.5;
- 32k context worked at `gpu_memory_utilization=0.5` with eager execution;
- the final policy used 32,768 model length, 32,256 reader input tokens, and 512 reader output tokens;
- overlength MedCounterFact input used deterministic head/tail evidence truncation.

## 5. Gate B: M0, M1, M2

- Implemented a single batched vLLM runner with resume-safe JSONL stages.
- M0 is direct response.
- M1 uses external retrieval; CLIR keeps patient observations visible and MedCounterFact is fixed-evidence-only.
- M2 uses the released-code-intent all-Llama chain: five summaries, exploration, five generations, selection, MedCPT rerank, shared reader.
- Reader answers are parsed with dataset-specific output contracts. MedPIC uses exact sets; CLIR uses one A–D key even when options are embedded in the question; MedCounterFact uses the fixed three-value enum.

Important superseded attempt:

- The first M2 selector parser recognized mostly bracketed selections and treated many valid `Final Selection:` lines as empty. The pre-fix artifacts are retained with `pre-selector-fallback` in their names.
- A minimal final-line parser restored valid unbracketed selections. The corrected M2 accuracy changed from 21/60 to 17/60. PairAcc remained 4/18.

Final Gate-B results: M0 21/60 and 6/18; M1 21/60 and 6/18; M2 17/60 and 4/18.

## 6. Gate C: M12 oracle

- M12 reads only the current item's gold answer/evidence to build rule-based oracle cards. It never receives pair ID, counterpart row, change direction, or counterpart label.
- It reuses M2 reranked documents and the shared reader; card construction and planning require no extra LLM calls.
- M12 produced 60/60 predictions and scored 30/60, PairAcc 5/18.
- The +21.67 pp row gain over M2 passed the frozen 2 pp oracle gate, allowing Gate D.

## 7. Gate-D implementation audits before the real run

The first Gate-D implementation passed fake tests but a semantic audit found four substantive mismatches:

1. M10 merely removed `evidence_ids` from already grounded cards;
2. M11 moved action and effect together instead of breaking the mapping;
3. M4 inserted filler text rather than matching actual auxiliary generation tokens;
4. a combined `all` phase could keep vLLM alive while loading MedCPT.

The fixes were:

- regenerate M10 parametric cards independently with evidence omitted;
- keep each target action fixed and derange only effect/timestamp/evidence bundles;
- generate M4 auxiliary reasoning with the exact per-item M9 completion-token budget and `ignore_eos`;
- keep `state`, `retrieval`, and `run` as three separate process phases.

Additional corrections made before the real run:

- use candidate-specific evidence for transition cards;
- include the complete state/goal/target/candidate document in applicable methods;
- remove `rollout_valid` from the M6 projection;
- enforce auxiliary prompt + output length within 32k;
- preserve extractor candidate types and use dataset-aware fallbacks.

## 8. Gate-D real state and retrieval stages

The first state run yielded only one MedEinst candidate per item, total C=174. This was rejected because the diagnosis ablation requires five distinct hypotheses.

- The old file is retained as `state_action.pre-medeinst-candidate-fix.jsonl`.
- A first strict rerun failed because one long response had no complete JSON.
- The state prompt was made concise and required complete JSON below 900 tokens.
- The fresh state run completed with C=254: every MedEinst item has H0–H4, five distinct diagnosis candidates.

Retrieval completed in about 11m38s:

- 60 items, 254 candidates, four query types per candidate, 1,016 query records;
- 824 external retrieval calls;
- MedCounterFact made zero external calls and used fixed evidence only;
- action context is five slots per item: 250 nonempty and 50 expected MedCounterFact padding slots.

## 9. Gate-D run interruptions and repairs

### Grounded cards

The first grounded-card pass produced 17 incomplete cards out of 254: 13 length-truncated and four non-JSON responses. The run was stopped before M9 comparator output existed.

- Original file retained as `grounded_cards.pre-schema-retry.jsonl`.
- Added strict required-field validation and one 2,048-token JSON repair.
- Rebuilt 60 unique rows; all 254 cards passed schema.

### M9 comparator

The first M9 comparator batch was invalid at scale: 44 of the first 48 ended by length and 43 had empty candidate scores, silently selecting the first candidate. The run stopped at 48 rows.

- Original file retained as `M9.comparator.pre-schema-retry.jsonl`.
- Added complete candidate-score coverage, nonempty legal selection, and `comparison_valid=true` checks.
- Added a compact 2,048-token full-prompt retry. Final M9 comparator: 60/60 valid, 59 retries.

### M4 equal compute

The initial exact-token implementation generated one item at a time and was too slow. vLLM was extended minimally to accept a per-prompt `max_tokens` list.

- M4 then ran in variable batches of 16.
- All 60 rows satisfy target tokens = actual tokens.
- Total completion tokens: 258,356; per-item range 2,513–7,186.

### Parametric cards and M10

- Parametric cards completed 254/254; two cards required repair; every `evidence_ids` list is empty.
- M10 comparator completed 60/60; 52 rows required the compact retry.

### M11

- All 254 shuffled cards retained the target action and took the effect/timestamp/evidence bundle from a different candidate.
- One early M11 comparator attempt still failed after the 2,048-token retry, so a final 3,072-token retry path was added with hard failure after that.
- The resumed canonical run needed 58 first retries and no second retry; all 60 rows were valid.

### Readers and scoring

- M3–M11 each produced exactly 60 unique predictions.
- All 540 reader generations ended with `finish=stop`; null and empty answers were zero.
- Scoring was independently recomputed by the main agent and two SubAgents. Stored summaries and the canonical comparison matched exactly.

## 10. Final decision

The full result table is in `GATE_B_D_RESULTS.md`. Gate E was rejected because only one of four frozen continuation checks passed. This is the completed experimental outcome, not an unfinished run.
