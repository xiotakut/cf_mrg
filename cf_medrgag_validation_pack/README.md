# CF-KADS-MoE validation pack

CF-KADS-MoE tests whether static MedRGAG knowledge-completion evidence interferes with
counterfactual state updating, whether delta-aware document selection can repair that
interference, and whether simple option-score fusion benefits from complementary reasoning
experts. It does not use NICE, atomic rules, transition cards, a hard preserve/revise gate, or a
world-model claim.

The implementation stays in one script, [`scripts/run_cfmoe.py`](scripts/run_cfmoe.py), and reuses
the existing CFShift/MedRGAG caches and installed models. Full commands are preserved in
[`results_cfmoe/commands.sh`](results_cfmoe/commands.sh); the actual scientific report is
[`results_cfmoe/summary.md`](results_cfmoe/summary.md).

## Confirmatory MedEinst result

The 1,000-pair fresh test was scored once after prompts, document rules, CPG edits, expert set,
features, and fusion weights were frozen on development/calibration. The old observed 500-pair
test was used only for the explicitly named exploratory zero-cost fusion audit.

| Method | Accuracy | Pair/robust | BTR | Repairs | Harms |
|---|---:|---:|---:|---:|---:|
| MedRGAG MCQ proxy | 45.4% | 17.2% | 59.1% | 0 | 0 |
| Direct option log-probability | 49.4% | 18.2% | 61.9% | 140 | 100 |
| Historical `no_medrgag_evidence` | 57.1% | 26.6% | 44.9% | 204 | 87 |
| True profile, no document | 77.7% | 41.5% | 12.4% | 368 | 45 |
| Profile + original KADS | 58.4% | 31.9% | 25.0% | 200 | 70 |
| Profile + CF-KADS top-3 | 68.5% | 19.3% | 37.1% | 333 | 102 |
| CPG core | 54.9% | 34.3% | 22.9% | 289 | 194 |
| ECR-lite | 58.0% | 34.3% | 23.6% | 302 | 176 |
| Uniform fusion | 69.9% | 37.1% | 26.9% | 288 | 43 |
| Learned fusion | 78.5% | 44.6% | 7.5% | 394 | 63 |
| Oracle expert selector | 96.3% | 65.0% | 1.9% | 514 | 5 |

Key paired-bootstrap differences (1,000 resamples) are:

- true no-document profile minus MedRGAG: +32.3 points, 95% CI [+28.8,+36.2];
- CF-KADS top-3 minus original KADS: +10.1 points, 95% CI [+6.3,+14.0];
- CPG core minus direct: +5.5 points, 95% CI [+1.4,+9.5];
- learned fusion minus strongest single expert: +0.8 points, 95% CI [-1.6,+3.3].

The previous profile-with-KADS signal approximately replicates (+13.0 points versus the earlier
+14); the historical no-evidence signal remains positive at +11.7 points but is smaller than the
earlier +18.4. The old 64.4% method is correctly named `no_medrgag_evidence`: it is a direct
pair-relative expert, not the separately defined profile/no-document method.

## Protocol and implementation

- Data: 800 official MedEinst train/reference pairs for development, 200 disjoint pairs for
  calibration, and 1,000 official test pairs selected by a fixed seed shuffle over source-ID
  sorted eligible pairs without looking at labels.
- Isolation: fresh IDs have zero overlap with DeltaRank 300, CFShift fresh 500, development, or
  calibration source IDs.
- Options: trap diagnosis, control diagnosis, and two deterministic profile hard negatives. The
  same four diagnoses are shown to every comparable method.
- Model: `/home/data3/txy/models/LLM-Research-Meta-Llama-3.1-8B-Instruct`, vLLM 0.8.5.
- Pair-aware methods see control, trap, and structured delta. `medrgag_mcq_proxy`, the MedRGAG
  option-score expert, and direct log-probability are separate trap-only baselines.
- Invalid model/numeric output is recorded as invalid and never replaced with a MedRGAG answer.
  The 27 CPG not-applicable rows have no valid semantic edit; only fusion treats that structural
  state as neutral.

Each document candidate is one of the five retrieved or five generated pre-KADS documents.
CF-KADS uses fixed equal weights:

```text
delta coverage + option contrast - shared-state redundancy
```

It evaluates top-1/top-3/top-5, no-document, retrieved-only, generated-only, and top-3 plus up to
two contrastively retrieved documents. Supplementary queries contain changed findings, the four
diagnosis names, and diagnostic significance—never gold labels or option roles. Rows without a
changed finding do not run supplementary retrieval.

CPG edits at most two changed findings with only applicable remove/revert/negate operations and
saves every edit plus all option log-scores. The shuffled control uses a donor pair's actual edit
text with the current options. ECR-lite uses fixed profile evidence-balance weights. All experts
are standardized within the four options before uniform or learned fusion. A single linear model
is trained on development; calibration selects L2 regularization 0.01; test never selects weights.

## Evidence interference

Original KADS profile scoring is 58.4%, compared with 77.7% without documents. Adding selected
evidence repairs 68 rows but harms 261. Retrieved-only reaches 70.8%, generated-only 64.8%, and
CF-KADS/contrastive reach 68.5%/68.9%. CF-KADS therefore repairs static KADS selection but does not
beat no-document. Coverage, generated ratio, document count, and option contrast have near-zero
correlation with the per-row accuracy change; score scale also does not cleanly separate repairs
from harms. Document-level factuality labels are absent, so content error cannot be distinguished
from reader distraction or score interaction without inventing an LLM judge.

## Other datasets and official-code pilot

All 467 MedPIC rows were run. The release contains only item-level fields and no official
counterpart/edit/pair mapping, so no pair metric was fabricated. MedRGAG reaches 34.7% exact-set
and 20.8% CF accuracy. The best non-baseline module reaches only 10.1% exact-set and 6.6% CF;
there is no second-dataset positive result. Contrastive retrieval adds documents on 221 rows but
matched GF/CF retrieval stagnation is not estimable. Deactivation exact accuracy is 0% for the
MedRGAG proxy versus 40.8% for activation.

The ReMedQA static control uses 100 fixed source IDs and four official variants (400 rows).
Profile, CPG, and ECR are disabled. The standard-reader adapter reaches 71.0% accuracy, 53.0%
ReAcc, and 60.0% ReCon; static fusion reaches 68.5%, 52.0%, and 61.0%, respectively. The adapter
appends canonical options after the official-format prompt and is not an exact official reader
reproduction.

After a positive 100-case CPG-core pilot, the official FAIRHealth code at commit
`265d1aea88f705063bb7ff2d686547d373da7e09` was run on five fixed dev cases. A saved one-line
compatibility patch makes its hard-coded confidence token budget respect `MAX_NEW_TOKENS`.
This is a Round-0 specialist/judge pilot configured for at most one peer-discussion round, not a
completed peer-discussion experiment: all five cases reached early consensus at Round 0, so no
peer round ran.
It scores 40.0% with zero format invalids and is excluded from fusion and confirmatory claims.

## Running and outputs

After the local private releases, MedRGAG corpus, model, and historical CFShift caches are in the
documented paths, the captured end-to-end command is:

```bash
cd cf_medrgag_validation_pack
bash results_cfmoe/commands.sh
```

The command file shows the 20-case smoke boundary, two-GPU development/calibration stages, frozen
fresh-test boundary, exact-ID merges, MedPIC/ReMedQA runs, and official-code pilot. GPU stages use
only independent CUDA devices 0 and 1.

Final public artifacts under [`results_cfmoe/`](results_cfmoe/) include `dev.jsonl`,
`calibration.jsonl`, `fresh_test.jsonl`, `expert_scores.jsonl`, `document_scores.jsonl`,
`predictions.jsonl`, `fusion_weights.json`, `metrics.json`, `metrics.csv`, `bootstrap.json`,
`summary.md`, the commands, smoke artifacts, and the official-code compatibility patch. Expensive
raw prompts/documents remain in the ignored `results_cfmoe/cache/` directory.

Historical CFShift and DeltaRank experiments remain under `results_cfshift/` and
`results_deltarank/`.
