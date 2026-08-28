# cf_mrg

The active experiment is **CF-KADS-MoE: Counterfactual Knowledge-Aware Document Selection
with Modular Reasoning Experts and Soft Option-Score Fusion**, implemented in
[`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/).

The central result is positive on MedEinst but does not yet generalize to MedPIC. On 1,000
previously unseen official MedEinst pairs, the all-Llama MedRGAG MCQ proxy reaches 45.4%, the
true no-document profile expert reaches 77.7%, and calibration-frozen learned fusion reaches
78.5%. The fusion improvement over that strongest expert is +0.8 percentage points with a 95%
paired-bootstrap interval of [-1.6,+3.3] points, so it is not significant. CF-KADS top-3 improves
profile scoring from 58.4% with original KADS evidence to 68.5% (+10.1 points, 95% CI
[+6.3,+14.0]); no-document remains stronger.

CPG core improves the trap-only direct log-probability baseline by 5.5 points (95% CI
[+1.4,+9.5]) and beats shuffled edits by 15.0 points. Real profile/delta information also beats
both shuffle controls. These are counterfactual evidence-selection and expert-fusion results,
not a world-model result.

The confirmatory protocol keeps pair-aware and single-case settings separate. Pair-aware methods
see control, trap, the structured delta, and the same four diagnoses; single-case MedRGAG/direct
baselines see only trap plus options. This fixed four-option view is not official MedEinst
open-diagnosis SOTA. Development uses 800 train/reference pairs, calibration uses a disjoint 200,
and the fresh 1,000 were seed-shuffled without label conditioning after excluding all 800
previously observed DeltaRank/CFShift test pairs.

MedPIC uses all 467 released rows. Its release has no official linked-pair map, so only row-level
metrics are reported; the proposed modules underperform the 34.7% MedRGAG proxy and do not provide
second-dataset positive evidence. ReMedQA uses 100 source questions across four variants as a
static control with profile/CPG/ECR disabled; static fusion reaches 68.5% versus 71.0% for the
standard-reader adapter.

See the [validation-pack README](cf_medrgag_validation_pack/README.md), the exact
[commands](cf_medrgag_validation_pack/results_cfmoe/commands.sh), and the complete
[result summary](cf_medrgag_validation_pack/results_cfmoe/summary.md). Earlier CFShift,
DeltaRank, DeltaRev, and transition-card results remain historical artifacts under
`results_cfshift/`, `results_deltarank/`, and `results/`.
