# Agent handoff

## Current state

The requested public-data pilot is complete. Gate C passed, Gate D failed the frozen mechanism gates, and the run stopped before Gate E by design.

- Final decision: `NO-GO_AFTER_GATE_D`
- Branch at handoff: `main`
- Repository: `xiotakut/cf_mrg`
- Canonical pilot: balanced60, seed 13
- Model: local Meta-Llama-3.1-8B-Instruct
- Final implementation tests: 27/27 passed
- Gate-D LLM tokens: 4,108,920
- GPU state after the run: GPUs 0–2 released; GPU 3 belongs to an unrelated Qwen process

Do not start the full three-seed Gate E run unless the user explicitly changes the frozen decision or supplies the missing benchmark units.

## Read in this order

1. `AGENTS.md`
2. `PROJECT_PLAN.md`
3. `GATE_A_RESULTS.md`
4. `GATE_B_D_RESULTS.md`
5. `handoff/EXPERIMENT_CHRONOLOGY.md`
6. `configs/experiments.yaml` and `configs/no_go.yaml`
7. `results/gate-b-real-20260824-seed13-v4/canonical-comparison-M0-M12.json`

Visible main-agent and SubAgent transcripts are in `handoff/transcripts/`. They intentionally contain task/user messages and visible commentary/final messages only; hidden reasoning, system/developer instructions, tool-internal payloads, and credentials are not exported.

## Implementation map

| File | Purpose |
|---|---|
| `scripts/prepare_gate_a.py` | Download pinned public sources and build the public Gate-A pack |
| `scripts/audit_gate_a.py` | Fail-closed manifest/count/pair/gold/evidence checks |
| `scripts/run_gate_b.py` | balanced60 selection and M0/M1/M2/M12 execution |
| `scripts/score_gate_b.py` | Dataset-aware row and complete-pair scoring |
| `scripts/run_gate_d.py` | Three-phase Gate-D runner for M3–M11 |
| `scripts/summarize_gate_results.py` | Canonical overall, dataset, pair, and slice aggregation |
| `tests/` | 27 unit/integration tests for Gate A, runners, scoring, and aggregation |

Gate-D execution is deliberately split into separate `state`, `retrieval`, and `run` processes. This avoids loading vLLM and MedCPT in the same GPU lifecycle.

## Canonical artifacts

- `results/balanced60-seed13/`: the exact 60 inference/gold rows needed to inspect and rescore this pilot.
- `results/gate-a-public-20260823-seed13-v3/`: final Gate-A manifest and report. Raw downloaded datasets are rebuilt through `prepare_gate_a.py`.
- `results/gate-b-real-20260824-seed13-v4/`: all current predictions, scores, summaries, cards, retrieval caches, comparator caches, shuffle output, and pre-fix attempt backups.
- `handoff/LOCAL_PRIVATE_DATA.sha256`: hashes for every local-only file that existed under `private_data/` at handoff time.
- `handoff/UPLOAD_MANIFEST.sha256`: hashes for the committed validation-pack handoff files.
- `configs/balanced60_seed13.json`: frozen ordered item IDs.

Important hashes:

| Artifact | SHA-256 |
|---|---|
| balanced60 IDs | `c16f7828466ca5dc1165e255f2a9d42fc2b3b8cf211503595a35490bb7f0a0f9` |
| Gate-B runner at execution | `2c28d2715a2eb748148236a620dfd9a6da1c9aeb4f28002e4afcd2f17d7043d9` |
| Gate-B runner in this handoff | `dc0df989aae2537b0858f26d40a78f33e7d4e923d9b5b04ba239eeefb1284ab8` |
| Gate-D runner | `f49e91f22cbc67940912bc01dd3058495fd53df4e4af7db4e385f4efad9921d8` |
| canonical comparison | `3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e` |
| Gate-D state/action | `aa1a9653fb255944d7029e63c583a7e4f4dc31865eef45dc7d1bbfc3c832c378` |
| action retrieval | `9c25b973eb57e9b7584df0a0dff43bb338e547f14c792c8d38d883e8988fe5af` |
| action context | `0534d2237d96f77964054190bcff48a2528d2ec6f8af242b050b311b77f9f4ed` |

The only Gate-B runner change after execution was replacing its `/tmp` default balanced60 reference with the byte-identical repository file in `configs/`; method logic and the reference SHA are unchanged.

## Final result

| Method | Accuracy | Complete PairAcc |
|---|---:|---:|
| M0 | 21/60 | 6/18 |
| M1 | 21/60 | 6/18 |
| M2 | 17/60 | 4/18 |
| M3 | 17/60 | 3/18 |
| M4 | 15/60 | 4/18 |
| M5 | 20/60 | 6/18 |
| M6 | 21/60 | 6/18 |
| M7 | 22/60 | 6/18 |
| M8 | 22/60 | 6/18 |
| M9 | 21/60 | 5/18 |
| M10 | 23/60 | 7/18 |
| M11 | 22/60 | 6/18 |
| M12 | 30/60 | 5/18 |

Gate C passed because M12 improved over M2 by 13/60 rows (+21.67 pp). Gate D passed only the condition that M9 strictly beat M3 and M5. It failed all three mechanism/continuation checks:

- shuffle did not hurt: M11 improved over M9 by 1 row and 1 complete pair;
- MedEinst trap stayed 1/10 while control fell from 1/10 to 0/10;
- CLIR t6+t7+t8+t10 was 3/8 for both M9 and the best equal-budget baseline M8.

M10, which removes the grounding/provenance gate, was the best non-oracle method. The pilot therefore does not support a textual clinical world-model claim.

## Local dependencies not stored in Git

These paths existed on the execution host:

- MedRGAG checkout and Python environment: `/home/data3/txy/MedRGAG`, `/home/data3/txy/MedRGAG/.venv`
- Llama model: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`
- MedCPT cross encoder: `/home/data3/txy/models/ncbi-MedCPT-Cross-Encoder`
- Java used by Pyserini: `/home/data3/txy/.local/medrgag-jdk-21`
- BM25 indexes and local Wikipedia/textbook corpora: under the existing MedRGAG workspace
- Raw public downloads and full 6,577-row Gate-A v3 pack: local `private_data/`, reproducible from the pinned source manifest

## Verification

From `cf_medrgag_validation_pack/`:

```bash
python3 -m unittest discover -v tests
python3 -m py_compile scripts/*.py tests/*.py
python3 scripts/summarize_gate_results.py \
  --inference results/balanced60-seed13/pilot.inference.jsonl \
  --gold results/balanced60-seed13/pilot.gold.jsonl \
  --run-dir results/gate-b-real-20260824-seed13-v4 \
  --methods M0 M1 M2 M3 M4 M5 M6 M7 M8 M9 M10 M11 M12 \
  --output /tmp/cf_mrg-comparison-check.json
sha256sum /tmp/cf_mrg-comparison-check.json
```

The last hash must be `3141c60ff63efc9065cf277249babcd27a5410c2d9966bd10c9fb82f89c15f1e`.
