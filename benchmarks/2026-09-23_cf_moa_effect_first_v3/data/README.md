# Effect-first cycles 1–4: public metadata export

This is a frozen publication artifact. The continuing research record is `docs/research/cf_moa.md`; the version-3 report provides the narrative, prior history, decisions, and remaining work.

- `per_input_status.csv`: 2,546 saved status rows identified by cycle, panel, backbone, arm, and request ID. Reused/composite/posthoc rows remain separately identified; these are not 2,546 unique inputs or model calls.
- `quality_summary.json`: all 92 arm/backbone/panel groups, original native mapping/unit metrics where available, and 294 saved-correctness comparisons. Comparisons use each arm's entire membership only when the comparator covers it. No answer was reparsed or rescored.
- `pair_summary.json`: 488 original pair summary groups. Different coverage strata overlap. Do not sum them. Maintaining/changing a relation is different from both answers being correct.
- `cost_summary.json`: newly incurred physical costs, separate inherited/shared method attribution, and known missing attribution. The 2,203-call subtotal covers these four cycles only, not the entire project history.
- `failure_and_limitations.json`: unavailable denominator rows, retained query and native truncations, old unavailable B, and the unresolved diagnosis readout contract gap. Repeated arm/panel references are not unique physical failures.
- `source_manifest.json`: 54 original metadata sources with relative paths, byte counts, and SHA-256. Original traces remain on the experiment server.
- `validation.json`: structural, denominator, comparator, cost, export-field and source-hash checks.

`quality34` has a 35-input pooled baseline because its preliminary smoke adds one member. The two 34-input main arms use the same-scope baseline values **24/34 and 28/34**, not the pooled 25/35 and 29/35. The direct-verdict diagnostic reuses the exact cycle2 `a1_target34` baseline; its published panel has no duplicated baseline status rows.

Native answer values, gold values, patient content, original prompts/responses, retrieved quotations, free-form error text, target choices and generated reasons are not exported. Some local scored sources contain such fields; extraction selects explicit finite fields and never uses their values to create this package. This is a privacy-conscious metadata release, not independent reproduction of native scoring.

Verify a downloaded package without private files (read-only; the frozen validation record is not rewritten):

```sh
python3 scripts/verify_publication_data.py data
```

Regenerate only where the original local evidence is available:

```sh
python3 scripts/build_publication_data.py --source-root /path/to/effect_first_revision_20260923 --output data
python3 scripts/verify_publication_data.py data --source-root /path/to/effect_first_revision_20260923 --write-report
```

Both commands use only the Python standard library and make zero model/tool inference calls. The first reads already-saved development outcomes; neither invokes a native scorer or accesses independent evaluation data.
