# Bibliography and claim map

27 BibTeX entries; original 24 keys preserved. Related work is 458 words (excluding headings and citation commands) and cites all 11 final data sources. Three added behavioral-testing references were verified against official ACL metadata. Existing primary-source verification is reused explicitly; this is not a systematic novelty or retraction review.

| Key | Claim / role | Source |
|---|---|---|
| `lewis2020rag` | Retrieval-augmented generation combines parametric generation with retrieved non-parametric evidence; foundational RAG context. | [primary](https://proceedings.neurips.cc/paper/2020/hash/6b493230-Abstract.html) |
| `xiong2024medrag` | MIRAGE and MedRAG provide a medical RAG benchmark and modular toolkit; supports the medical RAG baseline provenance, not our measured effects. | [primary](https://aclanthology.org/2024.findings-acl.372/) |
| `wang2025moa` | Layered Mixture-of-Agents aggregates outputs from multiple LLM agents; comparison background. Our five operations are not a replication of that architecture. | [primary](https://openreview.net/pdf?id=h0ZfDIrj7T) |
| `wang2023selfconsistency` | Self-consistency samples reasoning paths and aggregates answers; motivation for an explicit sampling/aggregation control. | [primary](https://openreview.net/pdf?id=1PL1NIMMrw) |
| `zhao2021calibrate` | Content-free contextual calibration addresses answer-prior and prompt sensitivity. Does not establish that our order-swapped verifier is calibrated or causally superior. | [primary](https://proceedings.mlr.press/v139/zhao21c.html) |
| `dubey2024llama` | The Llama 3 model family and its training/evaluation context; model-family provenance only. | [primary](https://arxiv.org/abs/2407.21783v1) |
| `yang2025qwen3` | Qwen3 dense/MoE model family and thinking/non-thinking modes; model-family provenance, not proof of our exact runtime settings. | [primary](https://arxiv.org/abs/2505.09388) |
| `chen2026medeinst` | M01; MedEinst introduces counterfactual differential-diagnosis pairs with discriminative evidence changes; original source for M01. | [primary](https://aclanthology.org/2026.acl-long.1847/) |
| `medpicbench` | M02; MedPIC-Bench supplies patient-specific medication-safety questions with guideline-following and counterfactual task families; original M02 data-card provenance. | [primary](https://huggingface.co/datasets/TIM0927/MedPIC-Bench) |
| `prosperi2026hiv` | M06; Original HIV antiretroviral-treatment, interaction, and adverse-effect causal-scenario study; provenance for M06. Does not establish correctness of every source reference answer. | [primary](https://www.nature.com/articles/s41746-026-02771-7) |
| `benkirane2025bias` | M10; Counterfactual Patient Variations evaluate demographic bias in clinical decision making. M10 specifically uses the authors' MedQA extension, not the paper's JAMA cohort. | [primary](https://aclanthology.org/2025.naacl-long.114/) |
| `rezaei2026cultural` | M11; Counterfactual cultural identifiers and contextual cues in medical QA; source provenance for M11. | [primary](https://arxiv.org/abs/2601.20102) |
| `xiao2025amqa` | M12; AMQA introduces adversarial medical questions involving race, gender, and socioeconomic attributes. Version 1 matches the AMQA identity used here; later FairMedQA is not a separate independent source. | [primary](https://arxiv.org/abs/2505.19562v1) |
| `rawat2024diversitymedqa` | M14; DiversityMedQA evaluates demographic biases in medical diagnosis; original M14 source. Native-option restoration and our eligibility decisions require the local construction record. | [primary](https://aclanthology.org/2024.nlp4pi-1.29/) |
| `gourabathina2025medperturb` | M17; MedPerturb studies gender, style, and format perturbations in clinical vignettes and treatment decisions; original M17 source. | [primary](https://arxiv.org/abs/2506.17163) |
| `mo2026faithfulness` | M20; Evaluates medical LLM behavior under counterfactual evidence and the tension between following supplied evidence and medical safety; source provenance for MedCounterFact. | [primary](https://aclanthology.org/2026.findings-acl.1847/) |
| `ngo2024medrgb` | M22; MedRGB studies medical RAG behavior under varied retrieval/evidence conditions; original M22 source. | [primary](https://arxiv.org/abs/2411.09213) |
| `li2025biorab` | M23; Biomedical RAG robustness evaluation includes counterfactual evidence and biomedical NLP tasks such as NLI; original BioRAB source. | [primary](https://arxiv.org/abs/2405.08151v3) |
| `simglucose` | Software provenance of the adopted A4 model execution, including 30 released virtual patient parameter profiles. Appendix C uses a 24-profile historical subset of this model. | [primary](https://github.com/jxx123/simglucose/tree/a6f6777586c860457a2a1e6cce6d0bd3fd33d1cc) |
| `ddxplus` | DDXPlus is a synthetic medical diagnosis dataset containing differential diagnoses, pathologies, symptoms, and antecedents; provides upstream dataset attribution. | [primary](https://proceedings.neurips.cc/paper_files/paper/2022/hash/cae73a974390c0edd95ae7aeae09139c-Abstract.html) |
| `li2026medrgag` | MedRGAG combines retrieval with generated parametric knowledge through context completion and document selection. | [primary](https://arxiv.org/abs/2510.18297) |
| `wu2026marag` | MA-RAG iterates reasoning and retrieval, deriving queries from candidate disagreement. | [primary](https://arxiv.org/abs/2603.03292) |
| `frisoni2024medgenie` | MedGENIE uses generated contexts for medical question answering. | [primary](https://aclanthology.org/2024.acl-long.533/) |
| `jiang2025tcrag` | TC-RAG uses a memory stack and state variables to control iterative retrieval. | [primary](https://aclanthology.org/2025.acl-long.558/) |
| `ribeiro2020checklist` | CheckList organizes behavioral tests by capability and minimum-functionality, invariance, and directional expectations. | [primary](https://aclanthology.org/2020.acl-main.442/) |
| `gardner2020contrastsets` | Contrast sets use small meaningful edits to probe local decision boundaries, typically changing the label. | [primary](https://aclanthology.org/2020.findings-emnlp.117/) |
| `kiela2021dynabench` | Dynabench supports human-and-model-in-the-loop dynamic dataset creation. | [primary](https://aclanthology.org/2021.naacl-main.324/) |

The full author fields for the four shortened entries are preserved in citation_audit.json, with BibTeX `and others` used in the readable bibliography. The original full 24-entry bibliography remains in ../archive/references.bib.

Publication-specific boundaries: MedPIC-Bench is an undated dataset card; CPV source M10 is the authors’ MedQA extension; AMQA is pinned to v1; BioRAB is pinned to v3; the MedRGAG DOI is printed in the previously verified publisher PDF but its registry resolution is not certified. Sources support their own methods/data, while this project’s counts, labels and scores require local benchmark evidence.

Additional keys intended for methods/setup/appendix rather than repeated in related work: `dubey2024llama`, `yang2025qwen3`, `ddxplus`, `simglucose`. Parent integration owns the final whole-manuscript citation-key check.

Round-1 attribution additions (29 entries total):

| Key | Supported use | Primary source |
|---|---|---|
| `ags2023beers` | Source of selected public prescribing recommendations. The local 71-rule count is supported by the project rule file and record, not claimed by the external paper. | [primary](https://agsjournals.onlinelibrary.wiley.com/doi/abs/10.1111/jgs.18372) |
| `shen2026medguidex` | Executable clinical-guideline logic produces factual/counterfactual supervision for medical LLM post-training. Our inference-time use is a local method distinction. | [primary](https://arxiv.org/abs/2605.26567v1) |
