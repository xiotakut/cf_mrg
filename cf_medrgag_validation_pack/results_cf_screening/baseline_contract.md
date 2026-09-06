# medrgag_llama_base: local reproduction contract

Starting repository HEAD: `1e01b3a33c378041c64a76cce70ed381e4280d35`, current branch main. Existing uncommitted documentation edits and archived AGENTS changes are retained separately. Research authority: `/home/data3/txy/RESEARCH_PLAN.md`, copied alongside this report. The current conversation defines scope.

The latest reusable baseline is `run_cfshift.py::run_baseline` → `run_gate_b.py::run_m2`; no sidecar function is needed. This is the actual recent CF baseline, distinct from the older v15 guided sentence-label summary experiment. The new runner reuses its prompt builders, parsers, Llama backend, sparse retrieval and MedCPT ranking; only task I/O, scheduling, provenance and resume are adapted.

| Stage | Actual file/function | Model | Decoding / configuration | Input → output |
|---|---|---|---|---|
| Initial retrieval | `run_gate_b.LocalRetriever`, `src/medrgag_retrieval.DualBM25Retriever.retrieve` | BM25 | 32 hits independently per source | question + native options → 64 candidates |
| Initial reranking | `src/medrgag_retrieval.MedCPTRanker.rank` | ncbi MedCPT Cross Encoder | FP32, pair max_length 512, descending logits, stable ties | 64 candidates → 5 external documents |
| KGCC summary | `src/medrgag_logic.build_summary_prompt`, screening `Runner.llm` | Llama | T=0, top_p=1, max=64; 5 calls | current independent task + each document → useful information |
| KGCC exploration | `build_explore_prompt`, `parse_knowledge_points` | Llama | T=0, max=1024; 1 call | task + summaries → 3 missing knowledge points |
| Complementary generation | `build_generation_slots`, `clean_generated_text` | Llama | T=1.2, top_p=.9, top_k=50, presence_penalty=1, max=256; 5 calls | 3 knowledge-conditioned + 2 question-only slots → 5 documents |
| Original KADS | `build_selection_prompt`, `run_gate_b.selection_ids` | Llama | T=0, max=2048; 1 call | 5 retrieved + 5 generated passages → up to 5 selected IDs |
| Final reranking | `MedCPTRanker.rank` | same MedCPT | same tokenization/scoring/order | selected documents → up to 5 reader documents |
| Reader M0/M1/M2 | screening `reader_prompt`, original JSON answer reader contract and `parse_answer` | same Llama | T=0, top_p=1, max=64; one independent request per method | same native task + 0 / 5 initial / up to 5 selected external documents → raw JSON answer |

Llama checkpoint and tokenizer: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`; BF16, tensor parallel=1, eager vLLM 0.8.5. No quantization, likelihood scoring, voting or permutation ensemble. The local checkpoint has no separately verifiable remote revision; configuration files and local checkpoint location are recorded, rather than inventing a revision. The installed tokenizer chat template is archived in each worker cache. MedCPT: `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder`.

Corpus/index: `/home/data3/txy/MedRGAG/corpus/{textbooks,wikipedia}/index/bm25`; existing corpus resolvers use those source directories. Neither PubMed nor historical MA-RAG MedCorp3 is substituted. BM25's configured source balance is before cross-encoder reranking; the final top five are not forced source-balanced.

Task changes are frozen before formal predictions: native diagnoses request exactly one actual diagnosis; multi-select keeps all option keys and exact-set scoring; evidence comparison adds explicit uncertainty. Mandatory MedCounterFact article_summaries are retained in every task-aware stage and every reader, outside KADS's external-document candidates. External retrieval is enabled for that dataset, correcting the old fixed-only pilot path. No metadata.question, metadata treatment labels, gold, pair text, edit label or previous answer enters the solver. For open tasks only, MCQ-specific auxiliary wording is replaced with medical-question wording; actual complete prompts are stored in compressed local archives.

Preflight found 11 mandatory tasks beyond the old 32768 context window, maximum approximately 48747 tokens. Capacity is therefore 65536 for all methods; completion budgets stay unchanged. Complete prompts are checked; overflow is recorded as a technical failure, never silently truncated. This preserves task content and is an explicit capacity adaptation, not the old 32K experiment.

The historical generator seed was unset. This run uses preassigned, role-independent seeds from opaque input ID, stage and slot, plus master seed 20260906. Repeated-input noise experiment uses master seed+1; no best-seed selection. Temperatures and output budgets remain the recent baseline's values. Exact source text/options/evidence/format deduplication shares predictions only for identical visible tasks. Resume requires equal frozen config and unchanged prepared input list.

Differences from published mixed-model MedRGAG: all auxiliary roles use Llama instead of hosted GPT; local prompt/JSON parser adaptations and short reader budget follow the recent local CF baseline; this does not use the earlier v15 constrained summary labels. Official code was checked as provenance, not used to overwrite local decoding. Official references: https://github.com/ll0ruc/MedRGAG and https://raw.githubusercontent.com/ll0ruc/MedRGAG/master/main.py.

Excluded call paths: Profile/DDXPlus scoring, CFShift, CPG, CF-KADS, ECR, RiskRoute, residual fusion, MA-RAG, Qwen, NICE/WM, teacher/judge. Only `run_gate_b` is imported from historical runners; `run_cfmoe.py` and `run_cfshift.py` are not imported or run. A completed independent input requires 15 LLM requests: M0+M1+5 summaries+1 explorer+5 generators+1 selector+M2. Logs permit checking that count and include source IDs, tokens, raw responses and full prompts. No format repair (zero extra attempts). Network acquisition has at most 3 attempts; model/backend failures exit with a durable error and resume from completed stages.

Runtime drift discovered at smoke: shared Transformers was 5.16.1, incompatible with vLLM 0.8.5 (`all_special_tokens_extended`). This task uses a local PYTHONPATH overlay pinned to project-recorded Transformers 4.53.2, tokenizers 0.21.4, huggingface-hub 0.30.2; shared model packages are not downgraded. Auxiliary pyarrow and matplotlib were added for native Parquet reading and requested figures.

KADS task-format clarification before formal inference: its original template repeats question text twice. Mandatory article_summaries appear fully in the second question instance only; the first retains the complete top-level question. This avoids duplicating up to 48K tokens of evidence without discarding any article or changing candidate budgets. Five affected smoke select/reader results were recomputed; old attempts remain in cache/smoke_pre_evidence_dedup.

Exposure correction retained the frozen 300-pair primary sample: 299 have no narrative match in the 163 scanned historical assets, one (`case_13504`) was previously used but has a malformed official heading (`Sym.`), initially missed by a heading-dependent scanner. The corrected full-text scanner labels it exposed; there is no pristine-test claim and no outcome-based resampling.
