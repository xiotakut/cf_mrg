# CF medical-RAG project: evidence handoff for ChatGPT

Snapshot date: 2026-09-05 (Asia/Shanghai)

Repository: `https://github.com/xiotakut/cf_mrg`

Canonical repository commit before this handoff: `53aaff676439066f8d0b6478404c91e7ece3528f`

This document collects what the repository and the visible conversation history can actually answer about datasets, prior use, current methods, results, hardware, runtime, and budget. It is an evidence handoff, not a new literature review or a new experiment.

Two reading rules matter:

1. Early files such as [`AGENTS.md`](../cf_medrgag_validation_pack/AGENTS.md) and the old world-model plans describe a historical project stage. They are not the current claim.
2. The current canonical result is the CF-Residual Adapter report in [`results_marag_cf/summary.md`](../cf_medrgag_validation_pack/results_marag_cf/summary.md). It supports a pair-aware four-option MedEinst result, not a general medical counterfactual, SOTA, safety, or world-model claim.

## 1. What the requested audit material can and cannot provide

| Requested information | Availability | Evidence or limitation |
|---|---|---|
| Initial “five CF test sets” | Available, but the phrase is ambiguous | The historical stack had five **roles**, while the fifth role contained more than one named control dataset. See Section 2. |
| Dataset versions, sizes, and actual usage | Available | Source revisions are in [`GATE_A_RESULTS.md`](../cf_medrgag_validation_pack/GATE_A_RESULTS.md); actual inference runs are summarized below. |
| Exact IDs used in later MedEinst splits | Available in committed JSONL files | Every relevant row contains `source_case_id`; Section 4 lists the files and overlap audit. |
| Latest result table and frozen configuration | Available | [`summary.md`](../cf_medrgag_validation_pack/results_marag_cf/summary.md), [`metrics.json`](../cf_medrgag_validation_pack/results_marag_cf/metrics.json), and [`fusion_config.json`](../cf_medrgag_validation_pack/results_marag_cf/fusion_config.json). |
| Adapter-visible fields and fairness boundary | Available | Section 5 distinguishes trap-only MA-RAG, pair-prompt MA-RAG, and the pair-aware sidecar. |
| Hardware and stage timing | Mostly available | Exact server inventory and logged stage spans are in Section 7. The reboot downtime was not separately timestamped. |
| Numeric compute or money budget | **Not specified** | The user later stopped fresh native/direct/three-seed work and requested the core adapter only, but gave no GPU-hour, wall-time, or paid-API cap. |
| Systematic literature coverage | **Not available** | [`references/SOURCES.md`](../cf_medrgag_validation_pack/references/SOURCES.md) is a project source list, not a PRISMA-style search ledger. Claims in the supplied ChatGPT literature discussion still require independent verification. |

## 2. What “the original five datasets” meant

The historical recommended stack numbered five benchmark roles:

1. MedPIC-Bench
2. CLIR-Bench
3. MedEinst
4. MedCounterFact
5. An answer-invariant control role: ReMedQA plus CPV/MedEqualQA

The fifth role was not one dataset. In the actual Gate-A preparation, ReMedQA and CPV were frozen separately, so there were **six named public sources**. MedEqualQA was discussed as an alternative but was not run in the committed experiments. CLADDER and CP-Env were optional extensions and were not part of the end-to-end result.

### 2.1 Frozen public-source inventory

These are preparation counts, not all inference counts.

| Dataset | Pinned revision | Upstream/raw size observed | Gate-A prepared subset | Unit |
|---|---|---:|---:|---|
| MedPIC | `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983` | 467 | 467 | rows; no released official linked-pair map was found |
| CLIR | `e7e1733b74819bbefa2a1b5bf653a0d1e00fbb9a` | 3,000 rows in the pinned snapshot | 500 | t6–t10, 100 rows each; only t6/t8 had safely usable observations |
| MedEinst | `354f4b527e764a8f2bebea8f71be55e0a6966402` | 10,766 | 500 pairs / 1,000 rows | paired cases; upstream total is 5,383 pairs |
| MedCounterFact | `f35b98063b51a63e677829b6d173029d98dd3b1e` | 1,012 | 200 pairs / 400 rows | four categories, 50 pairs each |
| ReMedQA | `3abb4b47a5859c7b46c0a1872a58c82e2e3029e3` | 5,036 | 300 source IDs / 1,200 rows | four variants per selected ID |
| CPV | `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5` | 12,310 | 300 case IDs / 3,010 rows | demographic variants |

Important caveats already recorded in Gate A:

- preparation stopped before the planned full inference because MedPIC lacked the expected linked-pair map and CLIR lacked planned Full-TS/edit-pair assets;
- MedCounterFact and ReMedQA redistribution/license terms still required upstream verification;
- the config calls CLIR’s broader official size 6,600, while the pinned raw snapshot used by Gate A contained 3,000 rows. This discrepancy has not been resolved here.

The raw public-source cache is deliberately ignored by Git and is not on GitHub. The committed Gate-A reports preserve revisions, counts, and hashes.

### 2.2 What was actually passed through model inference

| Stage | MedPIC | CLIR | MedEinst | MedCounterFact | ReMedQA | CPV | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| balanced60 Gate-B pilot | 10 | 10 | 20 | 16 | 2 | 2 | Single-seed 60-item pilot; NO-GO for the old world-model route |
| revised gold-free heldout | 78 | 79 | 72 | 74 | 0 | 0 | 303 items after contract-debug exclusions; world-model result negative |
| CF-KADS-MoE secondary evaluation | 467 | 0 | see Section 4 | 0 | 400 rows | 0 | MedPIC row-level result negative; ReMedQA static control |

The balanced60 result is in [`GATE_B_D_RESULTS.md`](../cf_medrgag_validation_pack/GATE_B_D_RESULTS.md). The 303-item result is preserved at commit `b714735`; its current artifacts remain under [`results/`](../cf_medrgag_validation_pack/results/). The later MedPIC and ReMedQA results are in [`results_cfmoe/summary.md`](../cf_medrgag_validation_pack/results_cfmoe/summary.md).

Consequently, the repository does **not** contain a successful five-dataset counterfactual result. It contains:

- a negative small multi-dataset world-model experiment;
- a negative full-row MedPIC transfer attempt;
- a ReMedQA static compatibility/control result;
- extensive positive evidence concentrated on a pair-aware four-option MedEinst protocol.

## 3. Project trajectory and what each stage established

| Commit | Date | Experiment | Main data | Outcome |
|---|---|---|---|---|
| `b714735` | 2026-08-25 | Revised gold-free transition/world-model experiment | 303 items across MedPIC, CLIR, MedEinst, MedCounterFact | Negative: full transition 20.8%, below local MedRGAG proxy 31.7% |
| `f2652d0` | 2026-08-27 | DeltaRev-MedRGAG | 40 dev + 160 test MedEinst pairs | No useful repair; heavy fail-closed behavior; no world-model support |
| `c5b20e2` | 2026-08-27 | DeltaRank-MedRGAG | 300 dev + 300 test pairs | Four-way MedRGAG 45.33%; residual +1.0 point with 5 repairs/2 harms; not a strong positive result |
| `9768abe` | 2026-08-28 | CFShift-MedRGAG | 800 dev + 200 cal + 500 fresh pairs | Profile signal strong; pure CF shift only +0.2 point over target margin and CI crossed zero |
| `1b95f9b` | 2026-08-29 | CF-KADS-MoE | reused 800/200 + 1,000 fresh pairs | Profile-no-document 77.7%; learned fusion 78.5%, only +0.8 point and not significant; MedPIC transfer negative |
| `212866d` | 2026-08-31 | RiskRoute-CF | reused 800/200 + a new 1,000-pair test | Risk-aware router 73.3% versus Profile 74.3%; no Pareto/safety-aware success |
| `53aaff6` | 2026-09-03 | CF-Residual Adapter on MA-RAG | reused 400/150 + 500 later test pairs | Large cross-interface gain, but no MA-RAG synergy; details in Section 6 |

The important scientific trajectory is therefore narrower than “a general CF system improved five datasets”:

> Repeated MedEinst experiments found that the control-to-trap score shift plus DDXPlus disease-profile alignment is powerful. Evidence-selection and risk-routing additions did not reliably beat the profile expert. The latest work attached that same sidecar to a second base interface, MA-RAG, where it again dominated the base but did not benefit from MA-RAG’s own scores.

## 4. Exact MedEinst split reuse and data lineage

Every modern MedEinst JSONL row represents one **pair** containing both a control and a trap narrative. “500 pairs” therefore means 500 JSONL rows and 1,000 case narratives. MA-RAG additionally converts every pair into three model records: control, trap, and pair prompt.

### 4.1 Committed split files

| Experiment | Development | Calibration | Test/fresh | Relationship |
|---|---:|---:|---:|---|
| DeltaRev | 40 | — | 160 | [`results/deltarev.gold.jsonl`](../cf_medrgag_validation_pack/results/deltarev.gold.jsonl) |
| DeltaRank | 300 | — | 300 | [`results_deltarank/dev.jsonl`](../cf_medrgag_validation_pack/results_deltarank/dev.jsonl), [`test.jsonl`](../cf_medrgag_validation_pack/results_deltarank/test.jsonl) |
| CFShift | 800 | 200 | 500 | [`results_cfshift/`](../cf_medrgag_validation_pack/results_cfshift/) |
| CF-KADS-MoE | 800 | 200 | 1,000 | Dev/cal are exactly CFShift’s sets; fresh is new |
| RiskRoute-CF | same 800 | same 200 | 1,000 | Reuses CF-MoE training/calibration features; `new_test.jsonl` is new |
| MA-RAG CF-Residual | 400 | 150 | 500 | Dev is first 400 of the reused 800; cal is first 150 of the reused 200; later test selected with seed 223 |

Development reuse is intentional and extensive:

- all 300 DeltaRank development source IDs are inside the later 800-row CFShift/CF-MoE development set;
- CFShift and CF-MoE development sets are identical (800/800), as are their calibration sets (200/200);
- MA-RAG development contains the first 400 of those 800 and MA-RAG calibration the first 150 of those 200;
- RiskRoute also learned from the same 800/200 asset family.

This is acceptable as iterative development, but these are not independent confirmations.

### 4.2 Later test sets and legacy exposure

The five later test files are pairwise disjoint by `source_case_id`:

- DeltaRank: 300
- CFShift: 500
- CF-KADS-MoE: 1,000
- RiskRoute: 1,000
- MA-RAG CF-Residual: 500
- total: 3,300 distinct later-test source IDs

However, the earlier DeltaRev 160-pair test was not included in the later exclusion code. Of those 160 old test IDs, 115 were subsequently reused:

| Later test | Overlap with old DeltaRev test |
|---|---:|
| DeltaRank 300 | 25 |
| CFShift 500 | 38 |
| CF-KADS-MoE 1,000 | 18 |
| RiskRoute 1,000 | 27 |
| MA-RAG CF-Residual 500 | 7 |

The current MA-RAG fresh set also contains one exact pair previously present in the older CFShift/CF-MoE calibration set: `case_180796`. A second matching ID, `case_36868`, occurs in an older training file with different narratives and labels; that one is an ID-namespace collision rather than the same pair. `case_36868` was nevertheless also present in the old DeltaRev asset.

This means the wording “excluded every source ID used by DeltaRank, CFShift, CF-KADS-MoE, RiskRoute, development, or calibration” in the existing latest summary is too broad. The selection code actually excludes:

- the four named later **test** files;
- the current MA-RAG 400/150 development/calibration subsets.

It does not exclude the older DeltaRev file or the unused tails of earlier development/calibration files. See `excluded_source_ids()` in [`prepare_marag_medeinst.py`](../cf_medrgag_validation_pack/scripts/prepare_marag_medeinst.py).

This newly documented issue does not numerically explain the large latest gain. A conservative offline sensitivity that removes all eight MA fresh IDs seen anywhere in old DeltaRev plus the additional prior-calibration duplicate leaves 491 pairs:

| Method | Original 500 | Conservative 491 |
|---|---:|---:|
| MA-RAG | 39.2% | 39.51% |
| MA-RAG + adapter | 80.0% | 79.84% |
| Profile-only | 79.4% | 79.02% |
| Adapter without MA-RAG | 81.8% | 81.87% |
| MedRGAG | 40.8% | 40.53% |
| MedRGAG + adapter | 82.4% | 82.48% |

On the 491-row sensitivity, paired-bootstrap accuracy differences remain large:

- MA-RAG adapter minus MA-RAG: +40.33 points, 95% CI +35.64 to +44.81;
- MedRGAG adapter minus MedRGAG: +41.96 points, 95% CI +37.27 to +46.84.

This sensitivity is an audit calculation only: no model was refit or rerun, and it has not replaced the committed primary metrics.

The full ID lists remain in their canonical JSONL files. They can be extracted without copying clinical text, for example:

```bash
jq -r '.source_case_id' cf_medrgag_validation_pack/results_marag_cf/fresh_test.jsonl
```

## 5. What the current adapter actually sees

The latest experiment mixes three distinct information conditions. They must not be described as equivalent.

| Method/input path | Sees trap case | Sees control case | Sees structured delta | Sees another model’s scores |
|---|---:|---:|---:|---:|
| `marag_int_trap` | yes | no | no | no |
| `marag_int_control` | no | yes | no | no |
| `marag_int_pair_prompt` | yes | yes | yes | no |
| `profile_only` / sidecar | yes | yes | yes | Llama option likelihoods and DDXPlus profiles |
| `marag_cf_learned` | yes | yes | yes | MA-RAG vote/entropy scores plus the Llama sidecar |
| `medrgag_cf_learned` | yes | yes | yes | MedRGAG score vector plus the same Llama sidecar |

Therefore:

- the main adapter is **pair-aware**, not an independent single-case diagnostic method;
- the trap-only MA-RAG baseline has less information;
- the pair-prompt baseline is the direct control for seeing both cases and reaches 50.2%, well below the adapter’s 80.0%;
- pair-prompt does **not** equalize the extra Llama compute. A same-model/same-budget non-CF ensemble control has not been run and is an important missing attribution experiment.

### 5.1 Four-option construction

Every pair uses:

- the trap diagnosis;
- the control diagnosis;
- two deterministic hard negatives selected by DDXPlus profile overlap;
- one frozen A–D mapping shared by all methods for that pair.

Gold labels are used to construct the MCQ and to train/evaluate the small linear model, as in ordinary supervised MCQ experiments. They are not inserted into solver, retrieval, profile-query, or native-ranking prompts. This is a **four-option MedEinst proxy**, not the upstream open-diagnosis task.

### 5.2 Sidecar scores

The strongest single expert is `profile_no_document`. Up to an option-independent constant, its score is:

```text
2 * direct_trap_score(option)
- direct_control_score(option)
+ 2 * standardized_delta_profile_score(option)
```

The profile term matches added/new findings positively and removed/old findings negatively against DDXPlus disease profiles. It does not use MA-RAG documents.

`cpg_core` borrows the counterfactual edit/probability-gap idea from `FAIRHealth/clinical-counterfactual-reasoning` at commit `265d1aea88f705063bb7ff2d686547d373da7e09`. This project uses deterministic remove/revert/negate edits of at most two ordered delta findings and exact option-sequence likelihood differences. It does **not** reproduce the full multi-agent discussion framework. The five-case official-code compatibility pilot was excluded from the fusion claim.

### 5.3 Learned fusion

For MA-RAG, the frozen per-option feature groups are:

```text
MA-RAG vote score
MA-RAG entropy-weighted vote score
Profile score
CPG score
vote x consensus
entropy vote x rounds
Profile x MA-RAG agreement
Profile x Profile margin
CPG x availability
```

Development fits the entropy temperature and linear weights. Calibration selects L2 from `{0, 0.01, 0.1, 1}`. The chosen L2 is zero. The fresh test is evaluated once without refitting. Exact weights are in [`fusion_config.json`](../cf_medrgag_validation_pack/results_marag_cf/fusion_config.json).

There is no neural router, hard preserve/revise gate, silent baseline fallback, or gold-dependent tie resolution in the latest portable main method.

## 6. Latest MA-RAG/MedRGAG results and the correct claim boundary

### 6.1 Configuration

| Component | Actual configuration |
|---|---|
| MA-RAG code | Upstream commit `423f031cc0ffca679a047c885be999b9604100a9` plus two recorded logging/retriever compatibility patches |
| MA-RAG backbone | local Qwen3-8B |
| Candidate/round budget | `N=8`, `T=4` |
| Solver | thinking disabled, default temperature 0.7, max 2,048 new tokens |
| Conflict query generator | thinking enabled, temperature 0, max 8,192 new tokens |
| Retrieval | BM25 + MedCPT-Cross-Encoder |
| Corpus | **MedCorp3**: PubMed, textbooks, Wikipedia; StatPearls was corrupt/unavailable and not silently substituted |
| Sidecar | local Llama-3.1-8B-Instruct, exact option-sequence likelihood, Profile and CPG |
| Development/calibration/test | 400 / 150 / 500 pairs |
| Fresh sampling seed | 223 |
| Bootstrap | 1,000 paired resamples |

MA-RAG’s checked-out script default is `T=8`; this experiment explicitly ran `T=4`. It is an intentional cost-effective setting from the experiment prompt, not an exact reproduction of the repository default or the paper’s full benchmark table. The available intrinsic implementation was used. The extrinsic evaluator was not run because its official checkpoint was unavailable.

The MedRGAG branch is a local all-Llama implementation/proxy. It must not be called an exact reproduction of any mixed-model paper configuration without a separate paper/code audit.

### 6.2 Fresh 500-pair result

| Method | Accuracy | Pair accuracy | BTR | Repairs | Harms | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| MA-RAG trap | 39.2% | 17.6% | 66.76% | — | — | 8 |
| MA-RAG pair prompt | 50.2% | 30.2% | 49.00% | 86 | 31 | 3 |
| Profile-only | 79.4% | 42.8% | 12.19% | 226 | 25 | 0 |
| MA-RAG + learned adapter | 80.0% | 52.6% | 13.18% | 210 | 6 | 1 |
| Adapter without MA-RAG | **81.8%** | 55.0% | 8.31% | 229 | 16 | 1 |
| MedRGAG | 40.8% | 17.6% | 60.54% | — | — | 0 |
| MedRGAG + learned adapter | **82.4%** | 47.0% | 10.88% | 220 | 12 | 0 |
| Adapter without MedRGAG | 81.8% | 46.8% | 10.88% | 217 | 12 | 0 |

Main paired-bootstrap comparisons:

- MA-RAG + adapter minus MA-RAG: +40.8 points, 95% CI +36.6 to +45.4;
- MedRGAG + adapter minus MedRGAG: +41.6 points, 95% CI +37.0 to +46.2;
- MA-RAG + adapter minus pair prompt: +29.8 points, 95% CI +25.2 to +34.6;
- MA-RAG + adapter minus Profile-only: +0.6 points, 95% CI -2.4 to +3.8;
- MA-RAG + adapter minus adapter without MA-RAG: -1.8 points, 95% CI -4.2 to +0.4.

Mechanism shuffles reduce MA adapter accuracy from 80.0% to:

- 50.0% with shuffled delta;
- 42.4% with shuffled profile;
- 73.0% with shuffled CPG edit.

All three real-minus-shuffle confidence intervals are above zero.

### 6.3 False consensus

- 459/500 MA-RAG final pools are unanimous;
- 273/500 are wrong-unanimous;
- the post-hoc adapter corrects 190/273 of those wrong-unanimous cases.

This demonstrates that the post-hoc state signal can expose errors missed by answer-to-answer agreement. It does not validate the native trigger by itself.

The native development/calibration diagnostics were weak:

- pure trigger: no repairs and no harms;
- delta-query: +3.75 points on dev and +1.33 on calibration;
- history ranking: +2.0 on dev and -0.67 on calibration;
- full native: +0.25 on dev and +1.33 on calibration.

Fresh native inference was stopped when the user narrowed the scope.

### 6.4 What may and may not be claimed

Supported, with the data-lineage caveat in Section 4:

> The same pair-aware counterfactual sidecar produces large gains over two different medical-RAG base interfaces under one four-option MedEinst protocol.

Not supported:

- genuine synergy with MA-RAG: removing MA-RAG scores is numerically better;
- broad cross-dataset transfer: MedPIC was negative and the latest positive test is MedEinst only;
- improvement on MA-RAG’s original benchmark suite;
- official open-diagnosis MedEinst SOTA;
- a clinical safety guarantee;
- a clinical world model.

The most conservative interpretation is that the Llama pair-aware Profile/CPG sidecar is strong on this constructed MedEinst MCQ, while the base MA-RAG distribution contributes no demonstrated incremental value.

## 7. Hardware, software, and runtime

### 7.1 Server inventory

Inventory queried on the same server on 2026-09-05:

| Resource | Value |
|---|---|
| GPU | 4 × NVIDIA H20, 97,871 MiB each |
| Driver | 570.133.20 |
| CPU | Intel Xeon Platinum 8469C, 48 physical cores / 96 threads |
| RAM | 491 GiB |
| Swap | none |
| OS/kernel | Linux 5.15.0-144-generic, x86_64 |
| Main inference stack | vLLM 0.8.5, PyTorch 2.6.0 |
| Base environment Transformers | 5.16.1 |
| Sidecar compatibility path | pinned Transformers 4.51.3 via `/home/data3/txy/.cache/marag_pydeps` |

Qwen services used GPUs 1 and 2 with:

```text
dtype=bfloat16
max_model_len=32768
max_num_seqs=16
gpu_memory_utilization=0.82
seed=223
prefix caching enabled
```

Four dataset shards ran concurrently, two client runners per Qwen service, each with `num_workers=8`. GPU 3 hosted the BM25/MedCPT retrieval service. During fresh evaluation GPU 0 ran the Llama sidecar with `gpu_memory_utilization=0.55`; its code default was a 32k context.

### 7.2 End-to-end visible timeline

The first smoke artifact was written at 2026-09-02 16:44:31 and the final commit at 2026-09-03 19:24:48: a visible window of about 26 h 40 m. Exact reboot downtime was not logged separately.

| Phase | Artifact span | Wall time | Work |
|---|---|---:|---|
| Environment, original MedQA check, smoke, pilot | 09-02 16:44–21:50 | about 5 h visible window | 450 official pilot item-runs plus 1,603 native/grid artifacts; some work overlapped |
| Formal MA-RAG dev/cal base | 09-02 22:08–09-03 04:45 | 6 h 37 m | 1,650 item-runs |
| Parse, fit, freeze | 04:47–04:50 | minutes | entropy temperature, linear weights, L2 selection |
| Formal native dev/cal | 04:53–13:05 | 8 h 12 m | four variants × 550 pairs = 2,200 method/item runs |
| Fresh Qwen control/trap/pair | 13:11–18:43 | 5 h 32 m | 1,500 item-runs |
| Fresh Llama sidecar | 13:12–17:51 | 4 h 38 m 52 s | ran concurrently with fresh Qwen; do not add it again to wall time |
| Evaluation, report, verification, commit | 18:46–19:24 | about 38 m | metrics, bootstrap, tests, documentation |

The earlier “5–6 hour” estimate referred only to the remaining fresh core stage. It did not describe the already elapsed pilot/formal/native work.

### 7.3 Why the base inference is expensive

One MA-RAG item is not one model answer. It generates eight solver candidates, may generate conflict queries, retrieves and reranks documents, then generates another eight candidates for each additional round.

Across only the formal and fresh **unchanged MA-RAG base** runs, excluding pilot, native variants, and sidecar:

| Quantity | Formal dev/cal | Fresh | Combined |
|---|---:|---:|---:|
| MA-RAG item-runs | 1,650 | 1,500 | 3,150 |
| Candidate answers | 24,584 | 21,288 | 45,872 |
| Retrieval queries | 5,692 | 4,640 | 10,332 |
| Retained/retrieved documents | 10,814 | 8,896 | 19,710 |
| Generated tokens | 11,259,265 | 9,272,035 | 20,531,300 |
| Sum of per-item wall time | 25.08 h | 20.91 h | 45.99 h |

Parallel shards compressed those approximately 46 summed item-hours into about 12.1 elapsed hours. The server was heavily utilized; the task was simply much larger than an interactive single-inference job.

Formal native dev/cal consumed another 8 h 12 m. Its artifacts contain 36,928 candidate slots and about 16.38 million recorded candidate-pool tokens, but the first-round pools were reused, so these figures must not be interpreted as all newly generated work.

### 7.4 Sidecar timing

For 500 fresh pairs:

| Sidecar stage | Time |
|---|---:|
| Retrieval plus MedRGAG M0/M2 baseline stages | about 1 h 43 m |
| Exact four-option likelihood scoring | about 47 m |
| Delta matching and document scoring | about 7 m |
| Raw CPG/expert option scoring | about 2 h 1 m |
| Assembly | about 22 s |
| Total | 4 h 38 m 52 s |

The generation stages recorded 3,312,304 completion tokens. Exact sequence-likelihood passes are additional and did not expose a compatible token counter. The sidecar was computed once and shared between the MA-RAG and MedRGAG comparisons; this saves experiment cost but does not make the sidecar free at deployment.

### 7.5 Avoidable versus scientifically necessary time

Necessary for the declared frozen core protocol:

- fit/select on development and calibration before opening fresh test;
- run the official-strength MA-RAG trap distribution;
- compute the pair-aware sidecar;
- retain pair-prompt if the adapter sees both cases;
- run one untouched test after freezing.

The largest avoidable delay was running the 8 h 12 m formal native block before the main fresh result. It was requested as a supplement, but it was not a prerequisite for the portable-transfer question. Native pilot grids also expanded before the main result. A better order would have delivered the core answer roughly 8–10 hours earlier:

```text
smoke/pilot -> formal portable fit -> fresh portable core -> optional native work
```

Minor overhead came from service reload after reboot, one Transformers incompatibility at Llama initialization, one upstream unbounded `</think>` formatting retry that was recorded invalid, and process resumption. Completed item caches prevented wholesale reruns; these were not the main source of the one-day runtime.

## 8. Reproducibility and asset inventory

### 8.1 Public, committed artifacts

Canonical latest files:

- exact command record: [`results_marag_cf/commands.sh`](../cf_medrgag_validation_pack/results_marag_cf/commands.sh);
- frozen splits and mapping: `dev.jsonl`, `calibration.jsonl`, `fresh_test.jsonl`, `marag_dataset_map.jsonl`;
- parsed MA-RAG rounds/scores: `marag_rounds.jsonl`, `marag_option_scores.jsonl`;
- sidecar scores and model: `cf_expert_scores.jsonl`, `fusion_config.json`;
- predictions/statistics: `predictions.jsonl`, `metrics.json`, `bootstrap.json`, `false_consensus.csv`, `efficiency.csv`;
- native dev/cal diagnostics: `native_dev_cal_metrics.json`;
- static check: `static_compatibility.json`;
- two small upstream patches: `marag_logging.patch`, `marag_retriever_compat.patch`.

The exact MA-RAG operational check was 100 MedQA items at `N=4,T=2`, with 72.0% accuracy. It verified the interface, retrieval, round logs, stopping, and vote path. It was not a full-paper reproduction.

### 8.2 Local-only expensive assets

These were intentionally not committed:

| Local asset | Approximate size | Meaning |
|---|---:|---|
| `results_marag_cf/cache/` | 92 MiB | fresh sidecar intermediates and merged fresh rounds |
| `results_cfmoe/cache/` | 865 MiB | earlier MedEinst retrieval/scoring/model caches |
| external MA-RAG base runs | 1.7 GiB | raw per-question rounds under `/home/data3/txy/MA-RAG/runs/ma-rag` |
| external MA-RAG native runs | 1.1 GiB | raw native rounds |
| local Qwen3-8B weights | about 16 GiB | not in repository |
| local Llama-3.1-8B weights | about 15 GiB | not in repository |

The official MA-RAG checkout is external at `/home/data3/txy/MA-RAG`; it remains at commit `423f031...` with the two recorded runtime patches and an untracked local corpus link. The task services were stopped after completion.

Older public result directories remain useful assets:

- [`results_deltarank/`](../cf_medrgag_validation_pack/results_deltarank/)
- [`results_cfshift/`](../cf_medrgag_validation_pack/results_cfshift/)
- [`results_cfmoe/`](../cf_medrgag_validation_pack/results_cfmoe/)
- [`results_riskroute/`](../cf_medrgag_validation_pack/results_riskroute/)
- [`results_marag_cf/`](../cf_medrgag_validation_pack/results_marag_cf/)

They should be reused for offline category/error analysis. Changing only fusion weights, thresholds, or category groupings does not require model inference. Changing retrieval, prompts, visible fields, documents, or model behavior does.

## 9. Budget facts and missing decisions

No explicit wall-time, GPU-hour, money, or paid-model budget appears in the visible conversation. The only firm operational decision was made after the user questioned the runtime:

- continue the portable core adapter;
- do not run fresh native variants;
- do not run direct-Qwen fresh baselines;
- do not run the three-seed robustness extension.

An observed preference can be stated, but it must not be mistaken for a numeric budget:

> Prioritize the shortest experiment that answers the main scientific question; disclose cumulative elapsed time and remaining ETA separately; do not start multi-hour supplements before the core result without explicit approval.

Before another large run, the user still needs to specify:

1. maximum acceptable wall time for one exploratory run;
2. maximum aggregate GPU-hours for the project;
3. whether a same-budget extra-model control is worth its cost;
4. whether small-model training or paid APIs are allowed;
5. whether the paper’s main task is independent diagnosis or explicit paired comparison.

## 10. Direct answers to the strategic questions in the supplied ChatGPT discussion

### Is the current evidence broad across counterfactual categories?

No. The successful modern evidence is concentrated on answer-changing MedEinst pairs. Earlier MedPIC/CLIR/MedCounterFact experiments are either small, negative, or incompatible with the same metric. ReMedQA is a static invariance control, not an answer-changing CF success.

### Does the repository already contain a usable category taxonomy?

Only a coarse dataset/task routing taxonomy. MedEinst stores deterministic `added_findings`, `removed_findings`, and `changed_findings`, but it does not contain a frozen, clinically audited sample-level taxonomy for negation, time, numeric change, risk factor, irrelevant attribute, and so on. Creating that taxonomy would be new work.

### Is the latest adapter an independent diagnostic method?

No. It is explicitly pair-aware. It compares control and counterfactual cases. The base trap-only scores remain useful baselines, and pair-prompt is the fairness control for access to both cases.

### Is transfer to MA-RAG established?

Only in the interface-level sense that the same sidecar can be attached to MA-RAG and beats its base under this protocol. Genuine synergy is not established: the adapter without MA-RAG is stronger than the adapter with MA-RAG.

### Could the gain be ordinary model ensembling or extra compute?

That explanation is not fully excluded. Pair-prompt rules out “merely seeing the control case” as a complete explanation, and the delta/profile/CPG shuffles support the specific sidecar signals. But there is no same-extra-Llama, similar-token, non-counterfactual ensemble control. This is a high-priority missing comparison.

### Could poor base performance be only retrieval coverage?

The current artifacts show that the no-document profile expert is much stronger than the MedRGAG/MA-RAG bases and that adding selected MedRGAG evidence previously hurt the profile expert. That is evidence against a simple “more retrieval fixes everything” account, but it is not a complete causal decomposition. The repository lacks a clinically verified sufficient-evidence oracle and document-level factuality/applicability annotations.

### Is CPG original to this project?

No. The core edit/probability-gap idea is explicitly attributed to the FAIRHealth repository/commit above. This project’s contribution is its particular deterministic edit, option-scoring, and fusion integration—not invention of the name or general idea.

### Can the current work support a world-model claim?

No. The old world-model experiment was negative, and the current method is a counterfactual residual adapter.

## 11. Recommended next non-inference deliverable

Before another full run, the repository can support a low-cost audit that:

1. builds a dataset/paper/config difference matrix from verified primary sources;
2. freezes a clinically reviewed sample-level change taxonomy;
3. uses all saved predictions to measure category-specific errors without rerunning models;
4. separates retrieval absence from evidence-use failure on a small reviewed subset;
5. defines one primary mechanism and a same-budget non-CF model-ensemble control;
6. records a hard runtime/GPU budget and makes native extensions opt-in.

What should **not** happen next is an automatic Cartesian product of every dataset, category, base system, and native variant. The existing history already shows that this delays the main answer and makes attribution harder.

## 12. Minimal verification commands

```bash
# Current revision and clean worktree
git rev-parse HEAD
git status --short

# Latest complete test sizes
wc -l \
  cf_medrgag_validation_pack/results_deltarank/test.jsonl \
  cf_medrgag_validation_pack/results_cfshift/fresh_test.jsonl \
  cf_medrgag_validation_pack/results_cfmoe/fresh_test.jsonl \
  cf_medrgag_validation_pack/results_riskroute/new_test.jsonl \
  cf_medrgag_validation_pack/results_marag_cf/fresh_test.jsonl

# Latest tests
/home/data3/txy/MedRGAG/.venv/bin/python -m unittest discover \
  -s cf_medrgag_validation_pack/tests -v

# Latest machine-readable result
jq '.methods.fresh_test // .' \
  cf_medrgag_validation_pack/results_marag_cf/metrics.json
```

No new model inference was performed to create this handoff.
