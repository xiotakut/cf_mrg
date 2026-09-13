# M3 performance investigation

Sources checked 2026-09-11:
- Official repository: https://github.com/NJU-RL/MA-RAG
- Paper: https://arxiv.org/html/2603.03292v1
- Serving defaults: https://github.com/NJU-RL/MA-RAG/blob/main/scripts/vllm_qwen3_8b.sh

The paper Appendix G identifies multi-round refinement as an inference-cost
limitation. Reducing rounds, candidate count, query diversity or history length
would change this baseline; these are not used as runtime optimizations.
The existing local setup already enables prefix caching, eight parallel client
shards over two single-GPU services, parallel retrieval of conflict queries,
and unanimity-based stopping. Official serving example allows 16 sequences;
this continuation retains the previously tested local capacity of 32 per GPU.

Unlike M5's former per-document whole-shard reads, this retriever uses
`cache=True` and loads `id2text.json` dictionaries. Loading roughly 57 GiB of
JSON is a substantial one-time startup cost and expands in RAM. Per-hit access
then uses dictionary lookup. M5's line-offset fix is therefore not a direct
per-question optimization here. A future offset-based loader could avoid the
large startup/RAM cost, but changing a running retriever is unnecessary.

`utils.process_response` calls SciPy entropy separately for every output token.
A synthetic 8,192 x 20 matrix benchmark measured 1.2124 s with individual calls
and 0.00785 s with vectorized `entropy(..., axis=1)`, bit-exact on this sample.
This is a microbenchmark, not an end-to-end speedup. It has not yet changed the
running implementation; real-response timing and equivalence are still needed.

Every new generation now has a `.timing.json` separating prompt/tokenization,
API request, response processing and gzip output. Retrieval JSON records wall
time including service batching. The upstream retriever batches with a 0.5 s
wait; changing that could trade batching throughput against individual latency.

Real-response validation also passed: 8 non-thinking candidates (674 tokens)
and one thinking response (256 tokens), with exact equality of all parsed
fields. Timings were 0.11096 -> 0.00503 s and 0.07074 -> 0.00245 s.
`response_processing_validation.json` records this check. The optimized parser
is now selected in source for subsequently launched/resumed workers. The eight
already-running workers retain their loaded original function and continue
without interruption; current throughput must not be attributed to this change.

Initial real benchmark stages showed 0.005–0.014 s prompt preparation after
initial tokenizer load, 0.33–1.33 s response parsing, 0.001–0.048 s cache writes,
and 2.30–3.97 s retrieval including the batching wait. GPU utilization reached
100% / 90% with all eight shards active. Generation remains the main cost.

## Final implementation clarification (2026-09-13)

The earlier investigation entries describe intermediate states. Vectorized response processing subsequently took effect as clients restarted, while shard 7 retained the old implementation through completion. See the [consolidated implementation record](<../EXPERIMENT_CHANGELOG_AND_REPRODUCIBILITY.md>) for the rollout timeline, equivalence evidence, and limits on speedup claims.
