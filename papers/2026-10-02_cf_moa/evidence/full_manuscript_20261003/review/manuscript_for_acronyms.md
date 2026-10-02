# Abstract

Medical question answering must respond selectively to changing evidence: a new finding can justify an additional treatment, invalidate an earlier recommendation, reorder competing diagnoses, or leave the relevant conclusion unchanged. Existing evaluations distribute these behaviors across datasets with different tasks and output formats, making their shared failure modes difficult to identify. We introduce a five-relation functional taxonomy and construct a benchmark of 6,104 units and 13,000 target judgments from 11 sources, retaining native task interfaces with frozen source-specific scoring. An evaluation of seven medical question-answering configurations reveals a consistent gap between overall accuracy and evidence-sensitive updating. Guided by this diagnosis, we develop a counterfactual mixture of agents (CF-MoA), with five functional roles for support addition, support removal, candidate comparison, model-based consequence calculation, and stable readout. A sparse controller connects these operations to existing systems. Across seven configurations, the corresponding heads improve all 21 comparisons on the three support-update and candidate-comparison categories. In the full benchmark evaluation, CF-MoA raises the aggregate score of two MedRAG configurations from 48.20 to 58.29 and from 47.35 to 59.36, while increasing correctness on both answer-changing and answer-preserving pairs. Component controls identify explicit support execution and catalog-based re-decision as useful mechanisms. Together, these results establish a functional framework for diagnosing and improving counterfactual medical reasoning across heterogeneous tasks.

# Introduction {#sec:introduction}

A medical answer is useful only in relation to the evidence that supports it. When a patient's condition changes, a system may need to add a newly indicated treatment, withdraw an option whose prerequisites no longer hold, or reconsider the leading diagnosis. Other changes should leave the answer intact. These behaviors require more than producing a plausible response to each question in isolation: the system must track how the changed information bears on the particular judgment being requested.

Consider a treatment supported by two independent indications. Removing one indication does not necessarily justify withdrawing the treatment; conversely, preserving an answer after its only supporting condition disappears is an error. A diagnostic update presents a related but different problem. New evidence can strengthen a candidate without making it the most likely diagnosis. Grouping examples only by whether their final answer changes loses these distinctions. The underlying operation---adding support, removing support, or comparing alternatives---is a more informative basis for analysis.

Retrieval-augmented generation (RAG) gives medical language models access to external knowledge, and agent-based systems add iterative retrieval, multiple answers, or explicit control of reasoning [@xiong2024medrag; @li2026medrgag; @wu2026marag; @jiang2025tcrag]. Yet an expanded evidence context does not by itself specify how support should be updated. Existing counterfactual, perturbation, and robustness resources provide complementary tests of this ability, but differ in their units, answer spaces, and evaluation rules. A common behavioral vocabulary is needed to connect their observations without replacing their original tasks.

We address this problem through a taxonomy that describes the functional relation between a change and a target judgment. Its five categories cover support addition, support removal, candidate comparison, consequence calculation, and target preservation. The categories can overlap: the same change may add evidence for a candidate and require a new comparison among alternatives. We use this taxonomy to organize an inventory of 26 candidate resources and construct a benchmark spanning 11 sources. Its 6,104 evaluation units retain the native questions, options, target definitions, and source-specific scoring definitions.

The resulting evaluation reveals structure that an overall score obscures. Seven configurations from six system families achieve aggregate scores between 47.35 and 51.61, but their scores on support removal range from 7.59 to 41.77. The strongest aggregate baseline is not the strongest system on every functional category. This motivates an operation-centered approach: use the observed failure mode to identify the missing computation, then attach a component that performs that computation through the existing interface.

We organize these components as a counterfactual mixture of agents (CF-MoA), with five functional roles. Its support agents execute three-valued rules, its comparison agent makes an explicit decision over a diagnosis catalog, its consequence agent applies local interventions to a supplied executable model, and its preservation agent stabilizes native answers through structured readout. A sparse controller selects the applicable operation from the visible input and available capabilities. This design gives each agent a concrete responsibility and allows compatible operations to share an implementation.

Our contributions are threefold. First, we introduce a functional taxonomy and a provenance-preserving benchmark that connect diverse medical counterfactual and robustness tasks. Second, we provide a seven-configuration diagnostic evaluation, together with head-level comparisons that improve all 21 system--category combinations on support addition, support removal, and candidate comparison. Third, we develop CF-MoA and evaluate the complete adopted controller on two MedRAG configurations, obtaining aggregate gains of 10.09 and 12.01 percentage points and improved correctness on both changing and preserving pairs. The accompanying controls explain which operations account for these improvements and when further aggregation adds little value.

# Related Work {#sec:related-work}

#### Behavioral evaluation and counterfactual tests.

Behavioral testing organizes evaluation around capabilities and expected responses to controlled changes. CheckList combines linguistic capabilities with minimum functionality, invariance, and directional tests [@ribeiro2020checklist]. Contrast sets probe local decision boundaries through small, meaningful edits that typically change the reference label [@gardner2020contrastsets]. Dynabench develops this diagnostic perspective through human-and-model-in-the-loop data collection [@kiela2021dynabench]. These approaches motivate evaluating the relationship between an input change and its required response. Our five-category taxonomy applies that perspective to medical tasks: it records the changed condition, the requested decision, and the evidence needed to justify revision or preservation. Categories can overlap when one case requires several operations. This gives a shared interpretation to tests drawn from sources with different task formats.

#### Medical counterfactual and robustness benchmarks.

Medical datasets expose several distinct consequences of perturbing an input. MedEinst changes discriminative evidence to test differential diagnosis [@chen2026medeinst], while MedPIC-Bench provides patient-specific medication questions with counterfactual task families [@medpicbench]. HIV treatment scenarios examine causal consistency across interventions, interactions, and side effects [@prosperi2026hiv]. Counterfactual Patient Variations and DiversityMedQA examine demographic sensitivity in clinical decisions [@benkirane2025bias; @rawat2024diversitymedqa]; cultural-cue perturbations and AMQA extend this line to cultural context and adversarial medical questions [@rezaei2026cultural; @xiao2025amqa]. MedPerturb varies gender cues, language style, and presentation format [@gourabathina2025medperturb]. MedCounterFact studies how models follow supplied medical evidence when its content conflicts with plausibility or safety [@mo2026faithfulness]. MedRGB and BioRAB assess retrieval conditions, including misleading or counterfactual evidence [@ngo2024medrgb; @li2025biorab]. We bring eligible instances from these eleven sources into one benchmark while preserving their native questions, answer spaces, and reference relations. The resulting functional labels connect heterogeneous perturbations to the reasoning operation that each instance actually tests.

#### Medical RAG.

Retrieval-augmented generation combines a language model with external information [@lewis2020rag]. MIRAGE and the MedRAG toolkit examine how corpora, retrievers, and language models affect medical question answering [@xiong2024medrag]. MedRGAG connects retrieved and parametric knowledge [@li2026medrgag]; MA-RAG uses multiple rounds of agentic retrieval and reasoning [@wu2026marag]. MedGENIE supplies generated contexts for medical questions [@frisoni2024medgenie], and TC-RAG maintains a memory stack to control iterative retrieval [@jiang2025tcrag]. These methods provide complementary ways to acquire and organize knowledge. Our seven evaluated configurations use them to diagnose which functional requirements remain difficult, then test operation-specific heads on the resulting outputs and admissible evidence. This connects system-level evaluation to targeted repairs such as recalculating support and comparing diagnostic candidates.

#### Agent aggregation.

Self-consistency aggregates answers across sampled reasoning paths [@wang2023selfconsistency], while Mixture-of-Agents passes multiple agents' outputs between successive layers [@wang2025moa]. Contextual calibration addresses prompt-dependent answer preferences [@zhao2021calibrate]. These ideas motivate distinct controls for additional sampling, candidate comparison, and aggregation. MedGuideX transforms executable guideline logic into factual and counterfactual supervision for post-training medical models [@shen2026medguidex]. Our support agents execute guideline logic during inference to recompute a current answer. CF-MoA gives its five agents explicit functional responsibilities and combines their outputs through a shared input contract and routing interface. Our evaluation follows both the gains from integrating these specialized operations and the incremental effects of candidate verification, tying each system change to the behavior it is intended to improve.

# A Functional Benchmark for Medical Counterfactual Reasoning {#sec:benchmark}

We organize medical counterfactual tasks around the relationship between a change and a specified judgment. A *comparison unit* links a source-provided variant to its reference or identifies an explicit within-question hypothetical. A *target judgment* identifies what is being assessed within that unit. This distinction lets a single clinical narrative support several functional annotations while retaining the source's original question and answer contract. The resulting taxonomy covers condition changes, hypothetical evidence, and perturbations whose effects are evaluated through native task performance.

## Five overlapping functional relations

**R1: adding support.** A change introduces identifiable evidence for a target judgment. For example, newly reported wheezing can support a bronchitis candidate without establishing it as the unique diagnosis. **R2: withdrawing support.** An identifiable basis for a judgment becomes invalid; the annotation states which basis is lost and preserves any independent support. **R3: comparing alternatives.** A change requires reassessing the relative support for at least two identifiable candidates. Replacing a history of spontaneous pneumothorax with deep-vein thrombosis illustrates a change relevant to the comparison between pneumothorax and pulmonary embolism in MedEinst [@chen2026medeinst]. **R4: deriving consequences.** A changed premise requires propagating an established relationship to an outcome not directly supplied. **R5: preserving a judgment.** A real change leaves the evidence relevant to a specified target intact; the annotation gives a reason for that invariance.

These relations overlap because they describe functions at the target level. The same observation may add support to one diagnosis and alter its comparison with another. Annotation therefore records the change, target, applicable relations, supporting text, and conclusions that cannot be inferred, then takes the union of target labels for the parent unit. Omission of a symptom does not establish its explicit absence, and an unchanged answer alone does not establish invariance. Native comparison axes are preserved: an internal hypothetical and an externally edited patient attribute receive separate treatment when they address different judgments.

## Collection, qualification, and sampling

We registered 26 candidate sources and obtained 15, comprising 14 text resources and one multimodal metadata release lacking required images. Their normalized archive contains 55,991 units. Source acquisition, semantic classification, and scoring eligibility are recorded separately. Qualification requires the source materials needed to answer the native task and an established scoring interface. This process yielded an eligible pool of 38,123 units and 77,781 target judgments from 11 sources. The included resources cover diagnostic and prescribing edits [@chen2026medeinst; @medpicbench], treatment hypotheticals [@prosperi2026hiv], demographic and cultural perturbations [@benkirane2025bias; @rezaei2026cultural; @xiao2025amqa; @rawat2024diversitymedqa], clinical-service judgments [@gourabathina2025medperturb], hypothetical research evidence [@mo2026faithfulness], and evidence robustness [@ngo2024medrgb; @li2025biorab].

Language-model agents performed structured semantic annotation and review, supported by cross-checks and targeted audits. The construction pipeline preserves provenance and explicit correction history. Review distinguishes whether a functional relation holds from whether its reference answer supports scoring. For example, a valid invariance annotation can remain while an unreliable reference is excluded from scoring. Targeted review corrected 172 judgments across 130 units; these corrections are retained alongside their earlier versions. Unit identifiers, source locations, eligibility decisions, and target-to-input mappings make the final evaluation traceable to the acquired materials.

The frozen v5 evaluation retains all eligible R1--R4 targets and samples 450 R5 units without replacement from each of eight sources. Sampling uses sorted source-specific identifiers and a fixed seeded procedure, without consulting model predictions. Original semantic labels remain available, while a separate evaluation-label field specifies membership in this evaluation. This yields 6,104 unique comparison units, with category counts of 2,866/79/733/13/3,600 for R1--R5. Category memberships overlap; in particular, all 733 R3 units also belong to R1. Equal R5 allocations preserve source coverage while reducing the much larger invariance pool.

## Native inputs and scoring

The selected units contain 13,000 target judgments and materialize into 13,905 distinct model inputs, including reference endpoints. Each method has 15,616 native scoring mappings: one input may support multiple targets, and shared references can serve several units. Models receive the current question, native options, required evidence, and output contract. Reference and variant endpoints are answered independently; gold answers, functional labels, annotation rationales, and the opposite endpoint's answer remain outside inference.

Native interfaces preserve the distinctions between sources. MedEinst requires open diagnosis, MedPIC uses multiple-answer selection, and MedPerturb expands eligible visit, management, and resource judgments separately. Hypothetical research evidence remains attached to its relation question. MedRGB retains the locally frozen six evidence conditions, with the fully relevant condition serving as the reference endpoint. Under our evaluation protocol, systems may additionally retrieve external evidence according to their configured permissions; this combines fixed perturbed evidence with dynamic retrieval.

For unit $u$, let $\mathcal{J}_u$ contain its eligible non-reference native scoring mappings and let $c_j\in\{0,1\}$ denote primary correctness. We report $$\begin{equation}
 s_u=\frac{1}{|\mathcal{J}_u|}\sum_{j\in\mathcal{J}_u}c_j,
 \qquad
 \mathrm{ALL}=\frac{1}{|\mathcal{U}|}\sum_{u\in\mathcal{U}}s_u,
 \label{eq:native-score}
\end{equation}$$ where $|\mathcal{U}|=6{,}104$. Category scores apply the same aggregation to their eligible members and mappings. Tables report these scores as percentages. Thus, ALL weights comparison units equally, rather than averaging category percentages or pooling all model inputs.

Scoring retains native choice keys, multi-answer sets, relation labels, and frozen diagnosis normalization. Invalid outputs and unresolved protocol failures stay in the denominator. We additionally distinguish variant correctness, answer agreement, and both-endpoints-correct performance. The last measure requires successful answers on both sides, making it useful for evaluating whether systems respond to relevant changes while preserving correct judgments under irrelevant ones. These functional strata provide the diagnostic basis for the specialized operations introduced next.

# CF-MoA: Sparse Orchestration of Five Functional Roles {#sec:method}

CF-MoA turns the benchmark's functional perspective into five executable agent roles: adding support (A1), withdrawing support (A2), comparing candidates (A3), deriving consequences (A4), and preserving task-relevant judgments (A5). The roles correspond to R1--R5 as design objectives; online execution depends on the current input's capabilities. Agents can share model weights and deterministic components. The adopted configuration, denoted B, selects an applicable operation and returns a native answer, as shown in Figure [1](#fig:architecture){reference-type="ref" reference="fig:architecture"}. Its organizing principle is sparse specialization, with the base system supplying the current answer and its actual inference context.

## Capability routing and native readout

Routing follows a fixed priority: diagnosis-format inputs enter A3; eligible rule tasks enter the shared A1/A2 kernel; inputs providing a complete executable model enter A4; supported single-choice, robustness, or relation tasks with saved original messages enter A5. Other inputs retain the base response. The router uses task format, visible options, question structure, and available computational resources. Source identifiers, benchmark relation labels, gold answers, and paired endpoints are excluded. Thus a component developed on one functional subset can also operate on compatible inputs elsewhere in the benchmark.

This interface gives each role a concrete applicability domain: finite prescribing rules for A1/A2, a fixed diagnosis catalog for A3, a supplied executable mechanism and state for A4, and supported native decision formats for A5. In the complete v5 evaluation, each backbone routes 3,560 inputs to A3, 123 to A1/A2, 10,178 to A5, and 44 to passthrough. A4 has no qualifying clinical v5 input; its supplied-model evaluation is reported separately. The controller records the selected route, requests, operation traces, and complete returned response.

## A1/A2: scoped support recomputation

A1 and A2 share a kernel containing 71 manually encoded rules drawn from selected recommendations in the 2023 American Geriatrics Society Beers Criteria [@ags2023beers]. Eligibility checks require a supported multiple-choice format, an age of at least 65 in the implemented question pattern, and a recognized medication option. The kernel extracts the requested action and scope, such as avoidance or renal dose adjustment. One call to the original backbone extracts only the required patient facts from the numbered current question, with evidence sentence identifiers. It does not receive the base answer or retrieved documents during this extraction. Missing or rejected evidence produces an unknown value.

The executor evaluates conditions, exceptions, and independent support paths using [met]{.smallcaps}, [contradicted]{.smallcaps}, and [unknown]{.smallcaps}. Conjunction combines requirements within a path; disjunction preserves independent paths. Consequently, invalidating one risk does not remove an option supported by another satisfied risk. Let $S_0$ be the initial valid option set and let $M,C,U$ partition options by their aggregate status. A1 adds $M\setminus S_0$; A2 removes $C\cap S_0$. For ordinary valid sets, the result is $$\begin{equation}
 S^{\star}=M\cup(S_0\cap U).
 \label{eq:support-update}
\end{equation}$$ The native assembler additionally handles exclusive "None" options, invalid initial answers, and empty outputs. Both roles therefore use one fact extraction and one execution, while retaining separate addition and withdrawal traces.

## A3: catalog-based candidate comparison

A3 uses all 49 disease names in the public DDXPlus catalog [@ddxplus]. The same backbone reads the current patient and the base system's actual context, with diagnoses bound to scoreable codes under six fixed catalog orders. For each order, it subtracts a content-free log-score prior from the patient-conditioned code score, following the general calibration principle of separating contextual evidence from answer preferences [@zhao2021calibrate]. The prior is the logarithm of the mean of three content-free candidate distributions, computed separately for each order; its subtraction coefficient is fixed at one. A3 selects the highest corrected score per order and votes across orders, breaking vote ties using average corrected probabilities. The selected catalog entry is mapped back to the native diagnosis. The catalog and scorer's frozen normalization are separate resources; this decision stage changes candidate selection without expanding the scoring dictionary.

## A4: executing a local intervention

A4 compiles an intervention into a typed local patch when the input supplies the executable model, parameters, complete initial state, and factual action schedule. Unmodified actions remain intact. The numerical executor runs factual and patched trajectories from the same starting state and projects their consequences onto the requested time and outcome. Our implementation uses the public glucose--insulin simulator [@simglucose]. Local patches reduce the need to regenerate a complete action plan, allowing intervention fidelity to be evaluated against a same-tool full-plan control. The returned consequence is computed from the supplied mechanism and executed actions.

## A5: task-adapted robust readout

A5 retains the adopted component F. For ordinary supported tasks, F preserves the complete original messages and samples up to five native responses at temperature $0.7$, seeds 42--46, and a 2,048-token output limit. It votes over valid answer keys, stops once one key receives three votes, and returns the earliest complete response carrying a winning key. Final vote ties use earliest occurrence; if no vote is valid, the first response remains invalid. This is a native-output adaptation of sampling and answer aggregation [@wang2023selfconsistency].

For explicit premise--hypothesis tasks with two polarity options, F uses a natural language inference (NLI) branch. It scores both A/B label mappings directly, generates one current-question analysis, and scores both mappings again conditioned on that analysis. Each two-label distribution is normalized before the four semantic distributions are averaged. The highest mean determines the answer; exact ties follow native option order. A final model call generates the complete native response with its answer field constrained to that decision. This path uses four one-token score callbacks and two complete generations at temperature zero, preserving the original evidence and required auxiliary fields. Missing code scores require a matching score request and remain visible in the cost ledger.

<figure id="fig:architecture" data-latex-placement="t">
<embed src="cf_moa_architecture.pdf" />
<figcaption>From functional diagnosis to agent orchestration. The benchmark describes five relations between a change and a target judgment. CF-MoA implements the corresponding operations through a sparse controller: support addition and removal share a rule executor, candidate comparison uses a diagnosis catalog, consequence calculation requires an executable model, and stable readout handles the remaining eligible interfaces. Routing uses the current input and available capabilities; A4 is evaluated separately on supplied-model tasks.</figcaption>
</figure>

# Experimental Setup {#sec:setup}

#### Seven system configurations.

We evaluate direct answering with Llama-3.1-8B-Instruct [@dubey2024llama]; an all-Llama implementation of MedRGAG; intrinsic MA-RAG with Qwen3-8B [@yang2025qwen3]; MedRAG with each of these two backbones; MedGENIE with Llama; and TC-RAG with Qwen. These are seven configurations from six system families. We refer to the two MedRAG configurations as MedRAG-Llama and MedRAG-Qwen. Their selected versions include structured output handling for MedRAG-Llama, the second local prompt version of MedGENIE, and typed control for TC-RAG. MA-RAG uses eight solvers per round, up to four rounds, with early agreement stopping. Its available retrieval collection contains PubMed, textbooks, and Wikipedia; the other retrieval configurations have their own corpus and retrieval settings. Appendix [11](#app:implementation){reference-type="ref" reference="app:implementation"} records the implementation identities and reuse accounting. The comparison measures the complete configured systems; it does not equalize all retrieval and inference budgets.

#### Head and system evaluations.

We separate two experimental scopes. The head evaluation attaches the support-update and comparison operations to the saved contexts and original answers of all seven configurations. It covers all 2,866 support-addition units, 79 support-removal units, and 733 candidate-comparison units. The clinical categories overlap, as specified in Section [3](#sec:benchmark){reference-type="ref" reference="sec:benchmark"}. Diagnosis heads use the corresponding system contexts; the rule branches reuse two backbone-specific sets of extracted facts and combine them offline with each system's original answer. The subsequent full-system evaluation executes the adopted CF-MoA controller, denoted B, on MedRAG-Llama and MedRAG-Qwen. Each configuration covers the same 13,905 unique inputs and 15,616 native scoring mappings. The earlier head outputs and the later full-system outputs are reported separately.

#### Mechanism controls.

We compare catalog-based diagnosis with its original answer, one catalog decision, six uncalibrated decisions, and calibrated decisions on the 680-unit diagnostic subset. A 123-input control removes the addition or removal operation while retaining the same extracted facts and rule statuses. Model-based consequence execution is evaluated separately on 24 virtual profiles with 12 questions each. For the full system, we also evaluate three candidate-selection variants and an expanded sampling pool; their six-arm design and complete results appear in Appendix [10](#app:full){reference-type="ref" reference="app:full"}. These controls distinguish a useful component from a benefit attributable to extra sampling alone.

#### Metrics and uncertainty.

The primary metric is the native unit-macro score defined in Section [3](#sec:benchmark){reference-type="ref" reference="sec:benchmark"}. Category scores use their respective member units. We additionally measure paired correctness: both the reference and changed input must be correct. We report this separately when the target answer should be maintained and when it should change, using 6,838 and 1,780 scored pairs, respectively. For paired system contrasts, we draw 5,000 bootstrap replicates using seed 240924, keeping related units together. The aggregate, preserving-pair, and changing-pair analyses contain 4,766, 2,806, and 1,780 parent families, respectively. The resulting 95% intervals describe variability within the evaluated benchmark. This benchmark was also used during method development; the implications for generalization are discussed in the limitations.

#### Computation.

The adopted components use the same 8B backbones as their host configurations. The full-system ordinary-answer sampler uses temperature 0.7, top-$p=1$, and a 2,048-token output budget. Component-specific scoring and execution settings are recorded with the released configurations. We report measured requests and tokens separately from unavailable original retrieval costs, and preserve invalid outputs in every denominator.

# Results {#sec:results}

## Functional evaluation exposes different weaknesses {#sec:baseline_results}

:::: table*
+:---------------+:----------+----------:+----------:+----------:+----------:+----------:+----------:+
| System         | Backbone  | ALL       | R1        | R2        | R3        | R4        | R5        |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| *Comparison units*         | 6,104     | 2,866     | 79        | 733       | 13        | 3,600     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| Direct         | Llama     | 48.10     | 30.04     | 8.86      | 17.87     | 38.46     | 65.70     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| MedRGAG        | Llama     | 48.81     | 31.33     | 7.59      | 24.69     | 53.85     | 65.88     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| MA-RAG         | Qwen      | 51.61     | 26.73     | 34.18     | 8.59      | 38.46     | **73.37** |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| MedRAG         | Llama     | 48.20     | 27.84     | 29.11     | 30.42     | 53.85     | 65.28     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| MedRAG         | Qwen      | 47.35     | 28.58     | 41.77     | 25.24     | 53.85     | 63.42     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| MedGENIE       | Llama     | 48.02     | 29.94     | 18.99     | 21.42     | **61.54** | 65.15     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| TC-RAG         | Qwen      | 49.43     | 31.44     | 29.11     | 28.92     | 30.77     | 66.17     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| **CF-MoA (B)** | Llama     | 58.29     | 44.63     | 48.10     | 53.21     | 53.85     | 68.84     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
| **CF-MoA (B)** | Qwen      | **59.36** | **46.62** | **58.23** | **60.03** | 23.08     | 68.79     |
+----------------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+

::: minipage
Each configuration covers 13,905 unique inputs. ALL averages non-reference task scores within units and then across units; R labels may overlap. Llama denotes Llama-3.1-8B-Instruct and Qwen denotes Qwen3-8B. The selected MedRAG-Llama baseline includes its output repair.
:::
::::

The seven baselines occupy a narrow range on the aggregate metric but exhibit substantially different functional profiles (Table [\[tab:main-system-results\]](#tab:main-system-results){reference-type="ref" reference="tab:main-system-results"}). MA-RAG has the highest baseline aggregate score, 51.61, and the highest preservation score, 73.37, yet scores 8.59 on candidate comparison. MedRAG-Qwen leads the baselines on support removal at 41.77, while MedRAG-Llama leads on candidate comparison at 30.42. Direct answering reaches 48.10 overall but only 8.86 on support removal. Thus, a system can answer many ordinary or preservation-oriented items correctly while struggling to revise the support for a specific decision.

The taxonomy makes these differences actionable. Support removal calls for checking whether an answer's prerequisites still hold; diagnosis calls for comparing viable candidates under the changed evidence. Neither need is fully described by the number of retrieved passages or generated answers. This distinction motivates the specialized operations evaluated next.

## Specialized heads transfer across seven configurations {#sec:head_results}

<figure id="fig:seven-head-gains" data-latex-placement="t">
<embed src="seven_system_head_gains.pdf" />
<figcaption>Original and head-augmented performance across all seven configurations. Each panel uses the complete corresponding category: support addition (<span class="math inline"><em>n</em> = 2, 866</span>), support removal (<span class="math inline"><em>n</em> = 79</span>), and candidate comparison (<span class="math inline"><em>n</em> = 733</span>). All 21 comparisons improve. Category memberships overlap; exact correct counts and branch coverage are in Appendix <a href="#app:heads" data-reference-type="ref" data-reference="app:heads">9</a>.</figcaption>
</figure>

Figure [2](#fig:seven-head-gains){reference-type="ref" reference="fig:seven-head-gains"} shows improvements in all 21 system--category comparisons. Support addition rises from an original range of 26.73--31.44% to 42.74--47.70%; support removal rises from 7.59--41.77% to 29.11--58.23%; and candidate comparison rises from 8.59--30.42% to 32.47--60.44%. The gains occur across direct answering, retrieval-based systems, and systems with their own agent or control loops. They show that a functional head can repair failures left by different upstream workflows.

The head construction reflects the overlap between categories. On support addition, the adopted wrapper routes 1,780 units to diagnosis, 72 to rule execution, and retains the original result on 1,014 units. On candidate comparison, 680 units use diagnosis, ten use rules, and 43 retain their original result. These shared operations connect the category analysis to an implementable system, while avoiding a separate learned model for every label.

#### Candidate presentation accounts for much of the diagnosis gain.

On the 680-unit diagnostic subset, averaging across the seven systems, the original score is 20.97%, a single catalog decision reaches 45.44%, six uncalibrated decisions reach 46.47%, and calibrated decisions reach 46.13%. The largest common improvement therefore comes from asking the model to make an explicit decision over the available diagnoses. Additional voting and calibration have smaller, configuration-dependent effects. For MedRAG-Llama, the correct count changes from 203 to 339 with one catalog decision and to 359 with either six-decision variant. For MedRAG-Qwen, the corresponding counts are 160, 382, 402, and 410. Appendix [9](#app:heads){reference-type="ref" reference="app:heads"} gives every configuration and additional source checks.

#### Both support operations contribute.

::: {#tab:support-ablation}
  Policy                         Llama           Qwen
  --------------------- -------------- --------------
  Full support kernel           69/123         71/123
  Without add             43/123 (-26)   48/123 (-23)
  Without remove          53/123 (-16)   60/123 (-11)

  : Support-operation ablation on all 123 rule inputs, reusing the same extracted facts and execution states. Parentheses give the change in correct outputs relative to the complete kernel.
:::

::: minipage
A1 and A2 share one rule kernel. Unavailable outputs remain in the denominator.
:::

The shared support executor uses the extracted facts to add newly justified options and remove contradicted ones. On the 123-input control in Table [1](#tab:support-ablation){reference-type="ref" reference="tab:support-ablation"}, disabling addition reduces correct answers from 69 to 43 for Llama and from 71 to 48 for Qwen. Disabling removal reduces them to 53 and 60. Both operations contribute under the same fact extraction and rule statuses.

The small support-removal category also exposes a dataset prior: a coverage-matched constant "None" control obtains more correct answers than the head in each of the seven configurations. The head's value is therefore better assessed together with the operation ablation and the nine covered prescribing examples with remaining support, where the constant control scores zero. On these nine examples, five configurations improve, one is unchanged, and one declines. This result favors explicit support execution as a useful operation while showing why the raw category average alone is an incomplete diagnosis.

## The complete controller improves overall and paired correctness {#sec:full_results}

On the complete benchmark, the aggregate score rises from 48.20 to 58.29 for MedRAG-Llama and from 47.35 to 59.36 for MedRAG-Qwen (Table [\[tab:main-system-results\]](#tab:main-system-results){reference-type="ref" reference="tab:main-system-results"}). The gains are 10.09 percentage points (95% family bootstrap interval: 8.96--11.23) and 12.01 points (10.92--13.15). Both configurations improve on support addition, support removal, candidate comparison, and preservation. Their final scores also exceed the highest aggregate baseline, although the within-configuration contrasts provide the direct measure of the controller's effect.

On the 13 clinical consequence units, MedRAG-Llama remains at 53.85 while MedRAG-Qwen decreases from 53.85 to 23.08 under the readout branch. This localized regression is retained in the main table alongside the larger-category gains.

<figure id="fig:paired-behavior" data-latex-placement="t">
<embed src="paired_behavior.pdf" />
<figcaption>Correctness on both members of a pair. On answer-preserving pairs, correct counts increase from 4,005 to 4,440 for Llama and from 3,528 to 4,460 for Qwen (<span class="math inline"><em>n</em> = 6, 838</span>). On answer-changing pairs, they increase from 13 to 347 and from 27 to 360 (<span class="math inline"><em>n</em> = 1, 780</span>). Agreement alone does not satisfy either measure.</figcaption>
</figure>

Paired evaluation tests the behavior that motivates the benchmark (Figure [3](#fig:paired-behavior){reference-type="ref" reference="fig:paired-behavior"}). On answer-preserving pairs, both-side correctness rises from 58.57 to 64.93% for Llama and from 51.59 to 65.22% for Qwen. On answer-changing pairs, it rises from 0.73 to 19.49% and from 1.52 to 20.22%, respectively. All four paired differences have positive family-bootstrap intervals. The controller thus improves selective response to a change as well as correctness under a change that should leave the answer intact. The lower absolute scores on changing pairs identify evidence-sensitive updating as a continuing challenge.

## Conditional execution and stable readout {#sec:conditional}

The consequence agent addresses tasks with an explicit executable model. On 24 virtual physiological profiles with 12 questions each, typed local intervention produces correct binary and numerical outputs on all 288 questions for both backbones. A same-tools alternative that asks the model to generate a complete plan obtains 270 and 222 correct numerical outputs. Removing the intervention from the patch procedure reduces numerical correctness to 67 for both backbones. These controls support the value of a constrained local edit followed by execution in the supplied model (Appendix [9.4](#app:model){reference-type="ref" reference="app:model"}).

Stable readout is evaluated on a separate 208-group component panel combining answer sampling and NLI interfaces. Its group-weighted paired score improves from 60.19 to 65.90% for Llama and from 59.17 to 66.47% for Qwen. In the final 16-group extension, both-side correctness improves from 11 to 12 groups and from 12 to 13 groups relative to the matched single-answer control. These observations motivated its use as the broad readout branch of the adopted controller.

## More aggregation is not uniformly better {#sec:extensions}

We evaluated further aggregation on the same full input set. A rationale-conditioned verifier scores the distinct candidates already present in the saved readout pool and returns an existing complete answer. Relative to B, it changes the aggregate score by $-1.81$ points for Llama and $+0.93$ points for Qwen. Its candidate-only and joint-selection counterparts likewise do not provide a consistent improvement over B; three additional sampled answers yield 58.32 and 59.67, with more unavailable outputs. The complete six-arm comparison is retained in Appendix [10](#app:full){reference-type="ref" reference="app:full"}. Earlier generated-answer aggregation also underperformed the adopted controller on its development panel. These results support sparse execution of useful operations as the default CF-MoA design.

The controller adds measurable computation. Attributed component requests total 59,800 for Llama and 58,301 for Qwen, before the original answering and retrieval costs. Rationale-conditioned verification adds 13,308 and 9,820 requests. This cost and its mixed gains make it a less attractive default than the adopted controller; Appendix [10.4](#app:cost){reference-type="ref" reference="app:cost"} gives the physical request and token accounting.

# Discussion and Conclusion {#sec:discussion}

The experiments connect three levels of analysis: a functional taxonomy, operations that address its failure modes, and a controller that composes those operations through existing medical question-answering interfaces. The taxonomy reveals weaknesses hidden by the aggregate ranking. The head evaluation shows that several of these weaknesses recur across different upstream systems. The full controller then turns the specialized operations into a usable inference procedure, improving both aggregate accuracy and correctness across related inputs.

The component controls suggest a practical design principle: make the required decision explicit before increasing the amount of generated reasoning. A catalog makes competing diagnoses available for direct comparison. A support executor turns uncertain narrative revision into option-level checks with a defined treatment of unknown facts. An executable model turns an intervention specification into a verifiable calculation. These mechanisms differ, but each narrows the gap between the behavior requested by the task and the action performed by the system.

The results also clarify the role of a mixture of agents. In CF-MoA, the agents are defined by the operations they perform, with shared weights and shared execution where appropriate. The useful combination is selective: a rule question benefits from support execution, while a diagnostic question benefits from candidate comparison. The mixed results from additional verification and generation show that assigning more agents to every input is not sufficient to improve the system.

Overall, this work provides a benchmark and an operational framework for studying how medical language systems should respond to changed conditions. The 11-source benchmark, seven-configuration diagnosis, 21 head comparisons, and two full-system evaluations form a connected empirical account. Further progress can be measured at both levels: whether each operation generalizes to new cases, and whether their controller improves correct change and correct preservation together.

# Limitations {#limitations .unnumbered}

The benchmark and component panels were used during development. The bootstrap intervals quantify uncertainty within these evaluated families; a separate family-disjoint evaluation after final controller selection is needed to estimate performance on unseen case families. The final controller was evaluated on two MedRAG configurations, while transfer to seven systems was established for the earlier support and comparison heads.

Source coverage and category balance also matter. Support removal contains 79 units and consequence calculation contains 13; category labels overlap, and a substantial part of the preservation subset comes from perturbation and retrieval-robustness tasks. The taxonomy was applied through structured review and source-specific checks, but independent clinician agreement on its assignments has not been measured. Source labels and rubrics inherit the strengths and limitations of their original datasets.

Several components have explicit resource assumptions. The rule executor depends on its 71-rule bank and extracted facts, and diagnosis uses a finite public catalog. Consequently, part of the observed gain concerns candidate coverage and readable output, rather than an isolated improvement in latent clinical reasoning. The consequence agent was validated on a supplied physiological model and virtual profiles. Baselines have different retrieval, formatting, and inference budgets, and a complete resource-matched comparison remains open.

# Ethical Considerations {#ethical-considerations .unnumbered}

The study evaluates existing research datasets and simulated profiles. It does not establish clinical effectiveness or authorize patient-care use. Dataset provenance and original access conditions must accompany any redistribution. Evaluation artifacts retain source task contracts, including failures and invalid outputs, so that downstream users can inspect the system's behavior rather than relying only on aggregate scores. Author and data-availability declarations appear in Appendix [12](#app:declarations){reference-type="ref" reference="app:declarations"}.

# Benchmark Composition and Annotation {#app:benchmark}

## Source inventory and qualification

Table [\[tab:story-benchmark\]](#tab:story-benchmark){reference-type="ref" reference="tab:story-benchmark"} gives the exact composition of the frozen evaluation. Source citations and acquisition records accompany the source manifest. The original inventory contained 26 candidates, of which 15 were acquired. Four acquired resources did not contribute eligible v5 targets: the clinical laboratory and EquityMedQA resources required additional answer or rubric adjudication; MedCF required an editing operation outside the implemented answering protocol; and MedMKEB lacked the required images. For the other 11 candidates, the specified fixed cases, counterfactual edits, or required restricted context had not been obtained at collection time. These acquisition statuses describe the archived study materials.

The 55,991 archived units comprise 53,494 text units and 2,497 metadata units with missing images. An initial review frame contained 28,243 units and 80,910 judgments. Its review ledger records 603 individual semantic reviews, 13,464 grouped semantic reviews, and 14,176 structural checks. Subsequent completion and eligibility review covered all archived units, producing 109,599 reviewed judgments, of which 77,781 were eligible in 38,123 units. The evaluation sample is drawn from this completed pool rather than from the initial capped frame.

::: minipage
The benchmark contains 6,104 unique units and 13,000 target judgments. Category memberships overlap and must not be summed as independent units. Target judgments are distinct from the 13,905 inference inputs and 15,616 native scoring mappings per system. The separate supplied-model A4 panel is not added to this table.
:::

## Annotation examples and overlap

An annotation identifies the source comparison axis before assigning a relation. In a MedEinst case, the addition of wheezing supports a bronchitis candidate (R1), while the associated diagnostic question can require comparison with acute laryngitis (R3). A DiversityMedQA sex-attribute change removes one demographic basis for a Lesch--Nyhan candidate (R2), while other findings remain available. In CPV-MedQA, changing an ethnicity description leaves the chemotherapy and ototoxicity evidence relevant to a pharmacological question intact (R5). These examples illustrate functional labels on specified targets, rather than rules for assigning a diagnosis from a single feature.

Labels are assigned to targets and then combined at the unit level. In v5, R3 is contained in R1; R1 and R5 share 450 units, R1 and R2 share four, and R2 and R3 share three. R1--R3 contain 2,941 distinct units. The sum of category memberships is 7,291, whereas the union used for ALL contains 6,104 units. The 13,000 selected target judgments, 13,905 distinct inputs, and 15,616 scoring mappings refer to different representations of these same tasks. Of the scoring mappings, 6,818 address reference endpoints and 8,798 address non-reference endpoints.

## Sampling and version lineage

The earlier v2 evaluation contained 3,105 units and eight sources. A v3 display assigned overlapping units to a single category for presentation, without changing their answers. The completed v4 pool restored multi-label evaluation and expanded eligibility review. The v5 evaluation used in this paper retains all eligible R1--R4 targets and samples 450 R5 units from each of eight sources. These source samples are drawn without replacement from sorted identifiers using a source-specific seeded procedure. The original semantic labels and the selected evaluation labels are stored separately. Neither prior predictions nor final method scores determine sample membership.

The 450-unit allocation balances source representation within R5; it does not assert equal numbers of independent patients or equal sampling probabilities across sources. Related variants remain linked to their parent families for paired analysis and bootstrap resampling. The source manifest, membership files, and scoring mappings are the authoritative definition of the evaluated sample.

# Component Evidence and Controls {#app:heads}

## Complete head comparisons

Table [2](#tab:seven-heads){reference-type="ref" reference="tab:seven-heads"} reports correct counts for every configuration in the head comparison. The R1 wrapper uses diagnosis on 1,780 units, support rules on 72, and the saved original answer on 1,014. R2 uses rules on 55 units and preserves 24 original answers. R3 uses diagnosis on 680 units, rules on ten, and preserves 43 original answers. These are unit-level coverage counts for the head experiment; the full controller's input-level coverage additionally includes reference endpoints and other compatible tasks.

::: {#tab:seven-heads}
  System                  R1 ($n=2{,}866$)           R2 ($n=79$)            R3 ($n=733$)
  -------------- ------------------------- --------------------- -----------------------
  M0 Direct        $861 \rightarrow 1,329$    $7 \rightarrow 29$   $131 \rightarrow 338$
  M2 MedRGAG       $898 \rightarrow 1,323$    $6 \rightarrow 23$   $181 \rightarrow 340$
  M3 MA-RAG        $766 \rightarrow 1,260$   $27 \rightarrow 43$    $63 \rightarrow 238$
  M4 MedRAG--L     $798 \rightarrow 1,225$   $23 \rightarrow 39$   $223 \rightarrow 386$
  M5 MedRAG--Q     $819 \rightarrow 1,367$   $33 \rightarrow 46$   $185 \rightarrow 443$
  M6 MedGENIE      $858 \rightarrow 1,317$   $15 \rightarrow 38$   $157 \rightarrow 305$
  M7 TC-RAG        $901 \rightarrow 1,331$   $23 \rightarrow 37$   $212 \rightarrow 349$

  : Correct counts before and after the specialized heads. Category memberships overlap; R1--R3 contain 2,941 distinct units. Section [5](#sec:setup){reference-type="ref" reference="sec:setup"} specifies context reuse and rule-fact sharing.
:::

**(a) R3: correct out of 680**

::: {#tab:head-controls}
  System           Original   Order 0   Majority   Calibrated
  -------------- ---------- --------- ---------- ------------
  M0 Direct             116       299        314          314
  M2 MedRGAG            163       320        325          315
  M3 MA-RAG              33       215        200          204
  M4 MedRAG--L          203       339        359          359
  M5 MedRAG--Q          160       382        402          410
  M6 MedGENIE           137       296        288          276
  M7 TC-RAG             186       312        324          318

  : Diagnosis and support-removal controls. (a) Original answers, single catalog selection, six-order voting, and calibrated voting on 680 diagnostic units. (b) Head and coverage-matched constant "None" results on R2, with the nine covered cases retaining support shown separately.
:::

**(b) R2: aggregate and remaining-support subset**

::: {#tab:head-controls}
  System           Head /79   None /79   Head /9   None /9
  -------------- ---------- ---------- --------- ---------
  M0 Direct              29         48         6         0
  M2 MedRGAG             23         47         4         0
  M3 MA-RAG              43         58         3         0
  M4 MedRAG--L           39         58         4         0
  M5 MedRAG--Q           46         56         6         0
  M6 MedGENIE            38         52         5         0
  M7 TC-RAG              37         54         2         0

  : Diagnosis and support-removal controls. (a) Original answers, single catalog selection, six-order voting, and calibrated voting on 680 diagnostic units. (b) Head and coverage-matched constant "None" results on R2, with the nine covered cases retaining support shown separately.
:::

## Diagnosis: catalog, calibration, and source checks

The public catalog contains 49 diagnoses, while the frozen task scorer recognizes 46 normalized diagnosis keys. The catalog is supplied to the decision component as a fixed resource; it is not constructed from the current item's gold answer. On 680 diagnostic units, Table [4](#tab:head-controls){reference-type="ref" reference="tab:head-controls"}(a) separates the single-catalog improvement from repeated selection and calibration. Across repaired R3 outcomes, 1,186 of 1,272 previously failed outputs were unmapped diagnoses, 23 were otherwise invalid, and 63 were valid wrong answers. This breakdown indicates that output grounding accounts for a large part of the measured improvement; unmapped outputs are not retrospectively counted as clinically correct.

Additional controls explored alternative name/code presentations on 40 diagnostic inputs. Direct code selection with a 384-token budget obtained 18/21 correct for Llama/Qwen; direct name selection at a 128-token budget obtained 15/18. Reasoning with names at 384 tokens obtained 18/19, while reasoning with codes at that budget obtained 21/22. Because the direct-name and direct-code controls used different budgets, their difference does not isolate the effect of codes. The complete run identities and budgets are retained in the evidence ledger.

Two additional source checks assessed catalog compatibility. On 47 ASCENT records, the calibrated head obtained 38/39 correct for Llama/Qwen, compared with 39/39 for uncalibrated voting and 38/39 for a single catalog decision. These records included 42 source-training and five source-test examples and subsequently informed development. Across three CUPCase batches totaling 18 records, the calibrated head obtained 15/16, uncalibrated voting 16/17, single selection 15/18, and character-length-normalized candidate likelihood 15/14. The checks support useful catalog-based selection on additional records, while providing no consistent incremental advantage for calibration.

## Support removal and remaining support

The constant "None" control in Table [4](#tab:head-controls){reference-type="ref" reference="tab:head-controls"}(b) uses the same 55-input rule coverage and retains the same 24 original answers outside coverage. Forty-six covered targets have "None" as their answer; the other nine retain support for at least one option. On those nine, original correct counts for Direct, MedRGAG, MA-RAG, MedRAG-Llama, MedRAG-Qwen, MedGENIE, and TC-RAG are 5/4/1/3/0/2/3, and head counts are 6/4/3/4/6/5/2. This subset measures the ability to retain independent support after another basis is removed.

The 123-input add/remove ablation in the main text holds the extracted facts and statuses fixed. It evaluates the shared executor on the complete rule-input panel used by the controller, rather than on the 79-unit R2 category alone. The full executor leaves one Llama input and 14 Qwen inputs unavailable; these remain included in the 123-input denominator. The contrast therefore tests the effect of the specified operations under the same upstream extraction.

## Supplied-model consequence execution {#app:model}

The separate model panel uses 24 virtual parameter and initial-state profiles, each with 12 questions. A question supplies the physiological mechanism, factual schedule, requested local intervention, and output projection. The typed-patch procedure edits the named action and executes the resulting trajectory. The full-plan control has the same tool access but regenerates a complete plan; the no-intervention control retains patch structure while omitting the actual intervention. Table [5](#tab:historical_model){reference-type="ref" reference="tab:historical_model"} reports binary, numerical, and full-output correctness. The 288 questions represent structured model queries, not 288 independent patients.

::: {#tab:historical_model}
  --------- -------------------------------------- ----- ----- -----
  Config.   Procedure
  /288
  /288
  /288
  M4        Ordinary reanswer                        118     0     0
  M4        Full execution                           286   270   270
  M4        Patch without intervention execution     234    67    67
  M4        Typed patch and execution                288   288   288
  M5        Ordinary reanswer                        187     0     0
  M5        Full execution                           265   222   222
  M5        Patch without intervention execution     234    67    67
  M5        Typed patch and execution                288   288   288
  --------- -------------------------------------- ----- ----- -----

  : Supplied-model consequence execution. Each configuration contains 288 questions from 24 virtual parameter/initial-state profiles. Counts report correct outputs within the supplied model contract.
:::

## Stable readout and generated aggregation

The F component panel comprises an initial 64 groups, an additional 128 groups, and a final frozen extension of 16 groups. Group-weighted paired scores for the complete 208-group panel are reported in Section [6.4](#sec:conditional){reference-type="ref" reference="sec:conditional"}. The ordinary branch aggregates valid native answer keys; the NLI branch combines direct and analysis-conditioned semantic probabilities across both label mappings. The component's exact stopping, tie-breaking, and invalid-output policies are specified in Section [4](#sec:method){reference-type="ref" reference="sec:method"} and the accompanying implementation.

The development study also tested generated aggregation over the available expert outputs on 121 inputs. The adopted controller obtained 87/82 correct for Llama/Qwen, a three-draw alternative 84/74, and the default generated aggregator 75/73. Adding a newly developed support-addition proposal to the candidate pool produced 72/57 under top-one selection and 79/74 under generated aggregation. These experiments led to the shared support kernel and sparse adopted controller. The 121-input panel is a development control and is not added to the full-v5 evaluation sample.

# Complete System Results and Aggregation Variants {#app:full}

## Six-arm comparison

The full evaluation uses the same input and scoring-mapping sets for all six arms. Table [6](#tab:arms){reference-type="ref" reference="tab:arms"} defines the arms, and Table [7](#tab:main_results){reference-type="ref" reference="tab:main_results"} reports aggregate scores, correct-input counts, and unavailable outputs. Correct-input counts use input-level scoring and are therefore distinct from the unit-macro ALL score. Table [8](#tab:full-categories){reference-type="ref" reference="tab:full-categories"} retains all five functional categories for every arm; Table [9](#tab:source-breakdown){reference-type="ref" reference="tab:source-breakdown"} gives source-specific C0/B results, and Table [10](#tab:format-breakdown){reference-type="ref" reference="tab:format-breakdown"} gives their native input-format results.

::: {#tab:arms}
  Arm      Decision rule                                                    Role in the comparison
  -------- ---------------------------------------------------------------- -------------------------------------------------
  C0       Original MedRAG configuration                                    Original-system reference
  C1 / B   Adopted operation core                                           Adopted CF-MoA controller
  C2       B plus candidate-only binary verification                        Same-pool verification without saved rationales
  C3       B plus rationale-conditioned binary verification                 Same-pool verification with saved rationales
  C4       B with old F votes plus three additional answers                 Expanded-pool sampling control
  C5       B plus joint selection over the same candidates and rationales   Alternative same-pool selection control

  : Six evaluation arms. C1 and B denote the same adopted operation core.
:::

::: {#tab:main_results}
  ---------- ----- --------- ------- -----
  Config.    Arm     ALL (%)
  inputs
  inputs
  M4 Llama   C0      48.1990   7,441     0
  M4 Llama   B       58.2924   8,924    51
  M4 Llama   C2      55.9939   8,554    51
  M4 Llama   C3      56.4815   8,649    51
  M4 Llama   C4      58.3219   8,951   157
  M4 Llama   C5      56.7295   8,660    51
  M5 Qwen    C0      47.3487   6,913     0
  M5 Qwen    B       59.3616   8,971    22
  M5 Qwen    C2      59.3562   8,843    22
  M5 Qwen    C3      60.2889   9,060    22
  M5 Qwen    C4      59.6723   8,878    86
  M5 Qwen    C5      58.9690   8,739    22
  ---------- ----- --------- ------- -----

  : Full-v5 results. Each row contains 13,905 inputs, 15,616 scoring mappings, and 6,104 non-reference native units. ALL is the mean of native-unit scores. Unavailable inputs remain in the denominators.
:::

::: {#tab:full-categories}
  Backbone   Arm       ALL      R1      R2      R3      R4      R5
  ---------- ----- ------- ------- ------- ------- ------- -------
  Llama      C0      48.20   27.84   29.11   30.42   53.85   65.28
  Llama      B       58.29   44.63   48.10   53.21   53.85   68.84
  Llama      C2      55.99   43.79   48.10   52.11   46.15   65.61
  Llama      C3      56.48   44.87   48.10   52.80   30.77   66.05
  Llama      C4      58.32   44.87   48.10   52.52   38.46   69.11
  Llama      C5      56.73   44.80   48.10   52.39   38.46   66.49
  Qwen       C0      47.35   28.58   41.77   25.24   53.85   63.42
  Qwen       B       59.36   46.62   58.23   60.03   23.08   68.79
  Qwen       C2      59.36   48.43   58.23   60.03   30.77   68.39
  Qwen       C3      60.29   49.02   59.49   60.30   30.77   69.70
  Qwen       C4      59.67   48.15   58.23   60.30   38.46   68.93
  Qwen       C5      58.97   47.87   58.23   59.89   30.77   67.99

  : Full six-arm category scores (percent). ALL and category scores use native unit means; categories overlap.
:::

::: {#tab:source-breakdown}
  Source             Units   Llama C0   Llama B   Qwen C0   Qwen B
  ---------------- ------- ---------- --------- --------- --------
  MedEinst           1,780      13.26     35.62     10.90    40.34
  MedPIC-Bench         167      28.74     53.89     38.32    58.08
  HIV scenarios         13      53.85     53.85     53.85    23.08
  CPV-MedQA            451      68.74     69.62     65.85    65.85
  Cultural Cues        517      67.31     70.02     68.67    70.60
  FairMedQA/AMQA       584      61.47     66.78     64.04    63.01
  DiversityMedQA       454      72.25     72.91     67.40    69.82
  MedPerturb           450      87.48     91.15     76.26    81.52
  MedCounterFact       788      51.02     55.33     56.22    53.05
  MedRGB               450      69.20     72.00     52.89    74.13
  BioRAB               450      44.22     57.78     59.78    75.56

  : Source-specific native unit means (percent) for the original system and adopted controller. Source sizes are comparison units.
:::

::: {#tab:format-breakdown}
  Format                Inputs   Llama C0   Llama B   Qwen C0   Qwen B
  ------------------- -------- ---------- --------- --------- --------
  diagnosis              3,560       9.47     38.01      9.49    42.67
  multi                    167      28.74     53.89     38.32    58.08
  relation                 989      52.78     55.21     59.45    55.61
  robustness_single      2,700      69.56     71.96     53.00    74.44
  single                 6,489      71.75     76.93     69.22    73.89

  : Native input-format accuracy (percent), including reference inputs. This input-level metric differs from ALL.
:::

## Paired outcomes and uncertainty

Table [11](#tab:paired){reference-type="ref" reference="tab:paired"} reports the complete both-endpoints-correct counts. All 1,780 answer-changing pairs come from MedEinst; the preserving-pair set spans multiple sources. The candidate-selection extensions operate on ordinary readout disagreements, so the diagnostic response-pair results remain identical across B and the four extensions in this evaluation. The family bootstrap resamples parent families as clusters and recomputes paired differences, preserving all units from a sampled family. Table [12](#tab:contrasts){reference-type="ref" reference="tab:contrasts"} reports the principal aggregate contrasts, and the machine-readable result package contains all 36 recorded contrast intervals across aggregate and paired metrics.

::: {#tab:paired}
  Arm     M4 maintain   M5 maintain   M4 respond   M5 respond
  ----- ------------- ------------- ------------ ------------
  C0            4,005         3,528           13           27
  B             4,440         4,460          347          360
  C2            4,139         4,381          347          360
  C3            4,144         4,486          347          360
  C4            4,509         4,412          347          360
  C5            4,150         4,246          347          360

  : Both-endpoints-correct counts for all six arms. Maintain uses 6,838 pairs and respond uses 1,780 pairs.
:::

::: {#tab:contrasts}
  Config.   Contrast                          Effect 95% interval
  --------- ----------- ---------------------------- ------------------------------------------------------------
  M4        B $-$ C0                        +10.0934 \[+8.9580, +11.2340\]
  M4        C3 $-$ B      $-$`<!-- -->`{=html}1.8108 \[$-$`<!-- -->`{=html}2.5287, $-$`<!-- -->`{=html}1.0819\]
  M4        C3 $-$ C2                        +0.4877 \[$-$`<!-- -->`{=html}0.1275, +1.0907\]
  M5        B $-$ C0                        +12.0129 \[+10.9177, +13.1510\]
  M5        C3 $-$ B                         +0.9273 \[+0.3039, +1.5562\]
  M5        C3 $-$ C2                        +0.9327 \[+0.4641, +1.4010\]

  : Paired contrasts in the ALL mean. Effects and 95% family bootstrap intervals are in percentage points. These are descriptive intervals on exposed development data.
:::

## Candidate verification and alternative selection

For an ordinary F input with at least two distinct valid answer keys, we retain the earliest complete saved response representing each key. C2 scores whether each candidate is correct under two opposite A/B label assignments. C3 uses the same procedure and includes the saved candidate rationale as model-generated reasoning to be checked. For candidate $k$, the verifier averages its normalized probability of correctness under the two assignments: $$\begin{equation}
 v(k)=\frac{1}{2}\left[p_{AB}(\mathrm{correct}\mid x,k,r_k)+p_{BA}(\mathrm{correct}\mid x,k,r_k)\right].
\end{equation}$$ The rationale $r_k$ is omitted in C2. The highest-scoring candidate is selected; exact ties favor the saved F answer, then native order. The complete existing representative is returned, preserving its required auxiliary fields. Non-ordinary F inputs, single-candidate pools, and unavailable B outputs retain B. Technical verification failure also falls back to B and is recorded.

The full ledger identifies 2,964 Llama and 2,295 Qwen ordinary disagreement inputs. Two Llama B outputs are unavailable, leaving 2,962 actually verified Llama inputs. C3 records one Llama and eight Qwen technical verifier failures with fallback. C5 instead scores a joint finite choice over the same candidates and rationales. C4 adds three predetermined native-answer draws to the old F pool and votes over the expanded pool; its unavailable-output policy is reported separately, rather than replaced with the verifier fallback.

## Computation and attribution {#app:cost}

Table [13](#tab:costs){reference-type="ref" reference="tab:costs"} reports the adopted component cost and the additional C3 cost. B uses 241,675,469 input and 9,686,224 output tokens for Llama, and 220,580,598 input and 7,645,205 output tokens for Qwen. Across the shared full-evaluation execution of all arms, the physical ledger contains 162,979 requests, 957,810,324 input tokens, and 18,291,906 output tokens. Method-attributed costs include the shared component once for each method being evaluated; summing those attributed totals across arms would double-count reused requests.

::: {#tab:costs}
  ---------- -------- -------- -------- ------------- -----------
  Config.
  requests
  requests
  requests
  tokens
  tokens
  M4           59,800   13,308   73,108   358,643,985   9,699,532
  M5           58,301    9,820   68,121   294,927,306   7,655,025
  ---------- -------- -------- -------- ------------- -----------

  : Attributed request costs for B and C3. The table includes the shared core once per method and excludes unknown common C0/retrieval costs. Tokens are the total attributed C3 tokens, not only verifier tokens.
:::

Original C0 answering and retrieval costs are incompletely recorded and are left unknown. Timing records cover 11,402 of 13,905 component input rows per configuration, leaving 2,503 without complete timing. Recorded event durations do not establish a complete end-to-end runtime. The physical request totals cover the later full-system experiment, not the entire research project.

# Implementation and Reproducibility {#app:implementation}

## Configuration identities

The selected seven-system comparison uses the following implementation identities: M0, direct Llama-3.1-8B-Instruct; M2, local all-Llama MedRGAG; M3, intrinsic MA-RAG with Qwen3-8B; M4, MedRAG-Llama with the selected structured-output repair; M5, MedRAG-Qwen; M6, MedGENIE v2 with Llama; and M7, TC-RAG with Qwen and typed control v2. The paper uses system names, while manifests retain these identifiers. The earlier i-MedRAG experiment was stopped and is preserved under its own identity; it is not an eighth configuration in the current table.

Selected outputs cover all 13,905 native inputs per configuration. Exact reuse is recorded for M0 (8,877 reused and 5,028 newly inferred), M2 (6,687 and 7,218), and M3 (3,690 and 10,215). M4--M7 each have 13,905 newly inferred outputs in their selected runs. Reuse requires the same input, method configuration, and output contract. Structured-output handling is part of the selected method identity; earlier unrestricted and repaired runs are not pooled as independent methods.

## Rebuilding paper artifacts

The paper package separates native LaTeX source, frozen numeric inputs, plotting scripts, and audit receipts. The main manuscript is maintained in , with section files, tables, vector figures, and . Running compiles it using Tectonic or a local LaTeX toolchain.

The reproduction scripts read frozen summaries and regenerate the main tables, source and format breakdowns, and vector figures. They retain source hashes and assert denominators and selected values before exporting results. The source package includes all assets required to compile the paper offline once the TeX dependencies are installed. Its companion evidence package identifies the original configuration, prediction, score, and trace artifacts for each experiment. Dataset licenses and large model/retrieval assets remain governed by their original distribution conditions.

The deterministic artifact rebuild reproduces the displayed results from saved experiment outcomes. Re-running inference additionally requires the exact backbone checkpoints, component prompts, rules and catalogs, native-input manifests, retrieval assets, and component-specific runtime settings. These dependencies are indexed separately so that an artifact rebuild is not confused with a fresh experimental replication.

## Evidence organization

The data construction record defines eligibility and version lineage; the evaluation protocol defines native scoring and input permissions; the selected-system record defines the seven baseline versions. Head-specific records contain their implemented rules, control experiments, and transfer results. The full-system closeout binds the six arms to source/category/format results, paired intervals, and request costs. A separate coauthor dossier connects these records chronologically. The manuscript draws its claims from this evidence map while retaining the original run identities and unsuccessful variants in the companion archive.

# Author and Availability Declarations {#app:declarations}

#### Data and code availability.

The manuscript source, figure-generation scripts, frozen result summaries, and experiment evidence indexes are maintained in the authors' private repository. A public release has not yet been made. Redistribution of source datasets must follow each original provider's terms; where redistribution is restricted, the release can provide identifiers, acquisition instructions, and derived membership or scoring metadata.

#### Author information.

This generic conference draft uses anonymous author information. Author names, affiliations, contribution statements, funding information, and competing-interest disclosures remain to be completed by the authors before submission.

#### AI assistance.

An artificial intelligence assistant was used to organize existing experiment records, draft and edit text, prepare LaTeX, generate plotting code, and check consistency against saved artifacts. The writing process did not generate new model-evaluation results or alter the recorded labels and predictions. The authors remain responsible for verifying the manuscript, disclosures, citations, and source-data permissions.
