# Full-test reader completion contract

Current comparison: M0 direct_llama, M1 retrieval_only_llama, M2 medrgag_llama_base. Only missing M0/M1 calls execute in this batch; M2 remains an exact cached result. The authoritative inherited M2 pipeline is documented in [the original contract](../../cf_medrgag_validation_pack/results_cf_full_test/baseline_contract.md).

| Method/stage | Actual function | Model | Configuration | Input/output |
|---|---|---|---|---|
| M0 | run_cf_baseline_screening.Runner.run_chunk, mode=readers; reader_prompt; Runner.llm | local Llama-3.1-8B-Instruct | BF16, original chat template, T=0, top_p=1, max_tokens=64, same per-item/stage seed | frozen independent task, all native options, mandatory evidence; JSON answer |
| M1 | same reader path, with Runner.retrieve exact cache | same Llama | same decoding; initial external reader documents=5 | same task plus unchanged first BM25/MedCPT top5; JSON answer |
| M2 | exact copied stage/answer cache from completed full run | same Llama | original complete KGCC/generation/KADS/reader configuration | no newly executed M2 calls |

Checkpoint and tokenizer: /home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct. Context capacity 98304; no quantization or decoder change. Initial retrieval is the same source-balanced BM25 32/source, MedCPT top 5 used by M2, already cached for every item. No new retrieval/reranking, KGCC, complementary generation, KADS, sidecar or judge is required.

Full input and evaluation labels, native answer formats, canonical mapping, parser, invalid policy, seed 20260906 and frozen taxonomy are identical to the original full run. Mode=readers returns immediately after M0/M1 and preserves all model parameters. No sample reduction or option truncation. MedCounterFact mandatory article evidence remains in both readers.

A new independent cache copy preserves the original completed M2 result directory and GitHub archive. Previously completed 5832 predictions per reader are retained; 19448 missing predictions per method are planned (38896 new LLM calls). The same full 25280 unique inputs are compared across all 3 methods. The fixed 20-input M2 seed repeat is inherited, not repeated or ensembled. See reader_completion.json, config.json and cache_reuse.json.
