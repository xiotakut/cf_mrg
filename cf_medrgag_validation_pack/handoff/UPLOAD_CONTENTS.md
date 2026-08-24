# GitHub upload contents

## Included

- Entire validation-pack implementation, prompts, configs, schemas, tests, and reports.
- Exact balanced60 inference/gold rows and ordered ID list.
- Final Gate-A manifest/report.
- All 65 files from the canonical Gate-B/C/D run directory, including:
  - M0–M12 predictions, scored rows, and summaries;
  - retrieval, state, card, comparator, M4 reasoning, and shuffle caches;
  - canonical comparison;
  - superseded M2 selector, state, grounded-card, and M9 comparator attempts.
- Visible-message transcripts for the main Agent and six SubAgents.
- Detailed handoff and experiment chronology.
- SHA-256 inventory for all local `private_data/` files.
- SHA-256 inventory for the committed validation-pack files.

## Not included

- Three duplicated copies of downloaded raw public datasets under `private_data/` (about 265 MB total). Their pinned sources and hashes are retained, and Gate A rebuilds them.
- Local model weights, BM25 indexes, Wikipedia/textbook corpora, Python environment, and Java runtime.
- Raw Codex session JSONL files. Those include hidden reasoning, system/developer instructions, and tool-internal payloads; the visible/task messages are exported instead.
- GitHub credentials or any local authentication files.

No Git LFS dependency is needed: the largest committed artifact is about 8.1 MB.
