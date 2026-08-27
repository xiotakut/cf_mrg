# cf_mrg

The active experiment is **DeltaRank-MedRGAG**, implemented in
[`cf_medrgag_validation_pack/`](cf_medrgag_validation_pack/).

```text
fixed 49-label ontology
→ two-way / four-way MedRGAG MCQ
→ structured control-to-trap delta
→ DDXPlus profile reranking
→ optional score-margin residual policy
```

NICE, medication-oriented atomic rules, and the old hard preserve/revise gate are not active.
The method is a counterfactual diagnostic reranker, not a world model.

The frozen pilot used 300 complete official MedEinst train/reference pairs for development and
300 official test pairs. The result did **not** meet the predefined positive-signal or residual-
augmentation criteria: the best development point had negative net correction, despite an
exploratory +1.0 percentage-point test result at that frozen threshold.

See the [validation-pack README](cf_medrgag_validation_pack/README.md) for commands and the
[final report](cf_medrgag_validation_pack/results_deltarank/summary.md) for results.

Previous DeltaRev and transition-card experiments remain historical results under
[`cf_medrgag_validation_pack/results/`](cf_medrgag_validation_pack/results/).
