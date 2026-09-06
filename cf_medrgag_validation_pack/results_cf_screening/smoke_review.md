# Smoke acceptance

25 independent inputs, five per dataset, all three methods; 375 current LLM requests. Reviewed all 75 raw reader responses and sampled complete saved prompts. No gold, paired-case body, dataset operation or reference/trap role is available to solver_input. All options retained (MedPIC multi-select arrays; Cultural five-option example); open diagnosis returns actual diseases rather than a placeholder. Mandatory evidence is retained in M0/M1/M2 and external retrieval/KGCC/KADS executed.

MedEinst outputs include diagnoses outside the canonical list; these remain unmapped in conservative screening, not repaired with gold or post-hoc medical aliases. This is scoring coverage, not a JSON placeholder failure.

One native CPV source group and one Cultural source group are included only partially in the five-input smoke; full groups are scheduled for formal completion. The five MedCounterFact inputs cover a complete original+four-variant source group with about 11K mandatory tokens each. Separate 20-input second-seed M2 run uses frozen random IDs; its raw answers have not been used for sample or tier selection.

Tests: tests/test_cf_baseline_screening.py, two tests pass (visible-field filtering, mandatory evidence, full options, task parsing, contradictory answers, stable independent seeds, metric identities). Input preflight: 3774 items; max mandatory reader 48747 tokens; 0 overflows at 65536 capacity. Full KADS includes only one copy of mandatory evidence to prevent duplication overflow.

Runtime compatibility failures and replaced smoke select/reader artifacts are retained locally under cache. No transport error is treated as a model wrong answer.
