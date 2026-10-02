## Contract Paraphrase

This is a prospective, field-general review plan for an English empirical AI conference paper, **CF-MoA: Taxonomy-Guided Benchmarking and Agent Orchestration for Counterfactual Medical Reasoning**. The target is a generic conference, approximately 5,500 main-text words, native LaTeX with supplementary evidence. No named venue, track, rubric binding, or calibrated target profile has been supplied. `criteria_binding_unavailable`; `calibration_status: NOT_CALIBRATED`. The installed academic-paper evaluator guidance and the frozen source contract `academic_paper/evaluator_full/v1` supply the five dimensions. This artifact adapts their precommitment structure; it does not certify completion of the upstream paper-blind pipeline.

**Exposure and role disclosure.** I am `/root/seven_methods_audit`. I wrote this draft's 458-word related-work section and revised its bibliography, and I have read their complete contents. I have also previously audited seven-system results and data construction, written the data chapter of the Chinese research dossier, reviewed its links, and inspected selected pages while building its reading PDF. I have seen prior manuscript artifacts, the source dossier, project records, frozen result audits, citation verification records, and the current paper-configuration metadata. I am therefore neither paper-blind nor an external author-independent reviewer; the later report will be an explicitly non-blind internal logic/readability review, including scrutiny of my own related-work text. Since receiving the present assignment I have not opened any new draft body section, assembled full draft, or new PDF. I will wait for the parent's exact assembled-manuscript handoff before judging it. No other reviewer's verdict or expected answer key has been supplied.

For **D1 Originality**, I will examine whether the manuscript identifies a concrete contribution in the collection, functional organization, evaluation, and method development actually performed, and differentiates that contribution from nearby behavioral-testing, medical-counterfactual, retrieval, and agent-aggregation research. New empirical organization or a well-supported boundary result can be a contribution; a claim of being first is not required. Scope-limited literature positioning must remain separate from a systematic novelty certification.

For **D2 Methodological Rigor**, I will ask whether the design and reporting support the stated inferences. This includes the data lineage and selection, overlapping functional labels, native inputs and scoring units, baseline identities, head-to-agent adaptation, controls, and development/confirmation distinction. I will assess replicability from the methods and linked artifacts without running inference, scoring, training, or simulation.

For **D3 Evidence Sufficiency**, I will trace material claims to appropriately scoped data or primary literature and check whether the breadth of a statement matches the coverage of its evidence. Favorable complete-scope results should be presented directly, while relevant negative controls and opposite effects must remain visible where they change the inference. A single valid caveat can delimit a claim; it need not be repeated after every favorable result.

For **D4 Argument Coherence**, I will test the chain from the medical counterfactual problem through the five-category organization and benchmark, seven-system diagnosis, specialized operations, CF-MoA integration, and conclusions. The paper should make the reason for each experimental comparison understandable and distinguish the contribution from the chronology of exploratory failures. Abstract, introduction, results, and conclusion must describe the same study.

For **D5 Writing Quality**, I will judge whether a reader unfamiliar with the workspace can understand the definitions, algorithms, figures, and quantitative conclusions without interpreting internal run identifiers. I will favor direct, supported statements and concise explanations, keeping essential inference limits close to their evidence and consolidating broader limitations. I will distinguish copyediting from substantive inferential weaknesses and avoid imposing an unconfirmed venue's style.

The subsequent review will use the categorical judgments `EXCEEDS`, `MEETS`, `PARTLY_MEETS`, `DOES_NOT_MEET`, or `NOT_ASSESSED`, with manuscript anchors, rationale, uncertainty, and decision impact. No numerical scores, weights, aggregate ranking, simulated venue acceptance probability, or calibration claim will be produced. Conditional block/warn triggers below guide findings; they are not judgments already made about an unseen assembled manuscript. For each material issue I will give the smallest honest repair and its likely effort/trade-off. I will not prescribe invented results or treat unperformed new research as a completed remedy. Revisions remain the parent's responsibility.

## Scoring Plan

### D1: Originality

- `dimension_id`: D1
- `what_to_look_for`: An explicit claim about the collected and curated benchmark, five functional categories, systematic seven-configuration evaluation, and operation-based agent construction, grounded in the actually delivered evidence. The relationship to CheckList/contrast sets, existing medical perturbation benchmarks, RAG methods, and layered MoA should be specific enough to identify what this work adds. Distinguish seven implemented configurations from six methodological families where relevant.
- `what_triggers_block`: The principal contribution is absent or depends on an unsupported first/exclusive claim; an existing external taxonomy or method is represented as wholly original; the paper's main contribution is materially different from the evidence produced. These require a concrete anchored instance, not an assumption that all integration work lacks originality.
- `what_triggers_warn`: A defensible contribution is present but the nearest-work distinction is vague, source collection is described as if it generated every original dataset, or novelty language exceeds the bounded literature review. Minimum remedy is usually a precise contribution statement or local attribution, not a new exhaustive review.

### D2: Methodological Rigor

- `dimension_id`: D2
- `what_to_look_for`: Reconstructable data selection and lineage; a clear definition of source units, judgments, model inputs, and metric aggregation; explicit overlapping R1–R5 membership; baseline configuration identities and admissible evidence; executable descriptions of heads and routed agents; correct reuse/new-call distinction; controls appropriate to claims about sampling, calibration, verification, and compute. Check that the separate physiological-model panel and clinical benchmark answer different questions. Check development exposure and independent-confirmation status without turning them into generic disclaimers.
- `what_triggers_block`: An inference requires independence, matched resources, equal backbone/output protocols, or a clinical outcome evaluation that the described design lacks; pooled denominators or label overlap invalidate a principal result; source or scoring leakage is concealed; the main method cannot be reconstructed from the text/artifact pointers. A core reporting omission that prevents assessing validity is also blocking until repaired.
- `what_triggers_warn`: The design is interpretable but a necessary operational detail, control definition, selection rule, scorer aggregation step, or resource scope is missing or difficult to locate. Remedy should first expose existing information rather than demand an unrequested new experiment.

### D3: Evidence Sufficiency

- `dimension_id`: D3
- `what_to_look_for`: Main quantitative claims tied to frozen complete-scope tables and actual denominators; baseline/head/agent effects kept separate; paired changes and intervals explained where used; source and format heterogeneity visible when it affects interpretation. Confirm that small R4 coverage, limited R5 research status, and mixed later-verifier effects bound the claims they actually affect. Citations should support the associated statement, and the source table should cover all eleven retained datasets. Cost claims should identify their accounting scope and missing historical measurements.
- `what_triggers_block`: Fabricated or materially wrong numbers, omitted counter-evidence that reverses a main conclusion, a subset gain described as a complete-scope gain, a development observation presented as independent confirmation, or a local benchmark result presented as established clinical benefit. A main causal/method-component claim without a relevant comparison is blocking for that claim, not grounds to erase otherwise valid descriptive results.
- `what_triggers_warn`: Core evidence is sound but secondary statements lack a source, a denominator/cost boundary is distant, uncertainty wording is imprecise, or a figure emphasizes favorable slices without directing the reader to the full relevant comparison. Minimum repair is a local qualifier, citation, complete row/panel, or corrected evidence pointer.

### D4: Argument Coherence

- `dimension_id`: D4
- `what_to_look_for`: Each section answers a recognizable part of the research question; taxonomy definitions lead to annotation/evaluation and motivate the five operations; seven-system diagnosis leads coherently into the two backbone-specific CF-MoA evaluations. Baseline comparison, head transfer, integrated operation gains, and incremental verification answer distinct questions. Main conclusions preserve that hierarchy.
- `what_triggers_block`: The abstract/title promise a study not performed; the five categories are conflated with five learned classifiers or the five agents with an unimplemented generic ensemble; conclusions contradict main tables; a major unexplained logical jump makes the central claim unsupported. The evidence must establish the contradiction in the assembled draft.
- `what_triggers_warn`: The study is consistent but key transitions or terminology are unclear, contribution priorities drift toward only the final verifier experiment, or exploratory chronology obscures the final method. Remedy is targeted reorganization and clearer rationale, preserving useful negative evidence.

### D5: Writing Quality

- `dimension_id`: D5
- `what_to_look_for`: Accessible first definitions, consistent terms and symbols, readable native-LaTeX structure, self-contained captions, figures/tables introduced in the argument, and stable references. Direct presentation of supported gains, one well-placed explanation of each substantive limit, and concise treatment of unsuccessful branches. Treat the approximate 5,500-word target as configuration guidance rather than an invented venue page ceiling.
- `what_triggers_block`: Widespread ambiguity or missing definitions prevents determining what was evaluated or what a principal result means; persistent unreadable tables/figures or unresolved core references prevent verification; the assembled article remains visibly incomplete. Cosmetic imperfections alone do not meet this threshold.
- `what_triggers_warn`: Readable text contains redundant defensive caveats, unexplained workspace jargon, dense process lists, overlong captions, avoidable cross-reference burden, inconsistent terminology, or several local grammar/formatting issues. Remedy is a specified local edit or consolidation; no vague demand to make the paper sound stronger.

`criteria_binding_unavailable`: no ReviewTargetContext, binding manifest, ordered venue-criterion pointers, or target digest was supplied. No such identifiers are inferred or fabricated. Scientific validity, venue alignment, and submission readiness will be reported separately; venue alignment is not assessed.

`review_state`: PRECOMMITTED_AWAITING_ASSEMBLED_DRAFT. No dimension judgment, strength/weakness finding, or verdict has been issued. The later review will cite the exact input paths/hashes and this precommitment, disclose the unchanged exposure status, and record any newly received information. Criteria will not be changed retrospectively to fit a preferred conclusion.

Provenance (SHA-256; read scope as described above):

- `/home/data3/txy/.codex/skills/academic-paper/agents/peer_reviewer_agent.md` — `ed37055a86a8d95bbbd0c3148936d690a98440f96417a3a066222c4a7b1aa415`
- `/home/data3/txy/.codex/skills/academic-paper/SKILL.md` — `cef2ec11fe5921a480ab93294706c26515e4ce2e0a26f7c33308db2b3fdb6c2d`
- `/home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper/evidence/skill_source/shared/contracts/evaluator/full.json` — `ce3b3e19f1da68985ebeb2dd2d7904d7343724d0847fff4e08704d79f083158a`
- `/home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper/evidence/skill_source/shared/references/review_criteria_consumer_protocol.md` — `575cc8c4d286c07fbd56f035c1dad3a65ff34a5b581bedca602dd286df54e1c7`
- `/home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper/evidence/skill_source/shared/ground_truth_isolation_pattern.md` — `737b1da4769e65a9a691f951c5b12dfabf1c3e5cdfb4073b6f29bf46e428cd88`
- `/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript/paper_configuration.json` — `d833a974a25a2ee6ab9451837e3fdfe3726a696ebaec745a6da9030994be4e59`
- `/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript/draft/sections/related_work.tex` — `967760906a43cb249f7abe0a223eb4e2f97426863ae6c3ce599e15e2c0a6cd58`
- `/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript/draft/references.bib` — `94cdecc00e8eb7f4a28276bae989e4457c7ff56a77da369338c28328a612fd9e`

Created 2026-10-02T18:55:59.739708+00:00.

[PRE-COMMITMENT-ACKNOWLEDGED]
