# cf_mrg

The active experiment is **CFShift-MedRGAG: Counterfactual Preference-Shift Residual
Reranking**, implemented in [`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/).

```text
unchanged four-option MedRGAG MCQ answer
+ option log-likelihood shift from control to trap
+ deterministic DDXPlus profile shift
→ always-apply capability analysis
→ one-margin residual policy
```

Every main method receives exactly the same four diagnoses. The experiment therefore isolates
counterfactual updating from the previous 49-way candidate-generation bottleneck. It does not
use NICE, atomic rules, transition cards, or a hard conjunctive gate, and it makes no world-model
claim.

The frozen study uses 800 official MedEinst train/reference pairs for development, 200 different
train/reference pairs for calibration, and 500 fresh official test pairs. The fresh set excludes
all 300 test cases inspected in the preceding DeltaRank pilot. The local model is
Llama-3.1-8B-Instruct through vLLM; `medrgag_mcq_proxy` is an all-Llama proxy rather than an exact
reproduction of the paper's mixed-model setup.

On the 500-pair fresh test, generated MedRGAG MCQ accuracy is 46.0%. The calibration-frozen
CFShift residual reaches 47.6% by repairing 14 errors and harming 6 correct answers
(+1.6 percentage points net correction, 5.8% answer-change coverage, 97.39% original-correct
preservation). The profile always-apply scorer reaches 60.0% and drops to 44.4% with shuffled
delta and 35.2% with shuffled profiles, but pure CF shift improves target-only scoring by only
0.2 points with a bootstrap interval crossing zero. The result is qualified positive evidence
for a local profile/shift mechanism and a small residual gain, not conclusive evidence for the
pure preference-shift hypothesis and not a world-model result.

See the [validation-pack README](cf_medrgag_validation_pack/README.md) for the full run commands
and [`results_cfshift/summary.md`](cf_medrgag_validation_pack/results_cfshift/summary.md) for the
actual result.

DeltaRank, DeltaRev, and transition-card experiments remain historical results under
[`results_deltarank/`](cf_medrgag_validation_pack/results_deltarank/) and
[`results/`](cf_medrgag_validation_pack/results/).
