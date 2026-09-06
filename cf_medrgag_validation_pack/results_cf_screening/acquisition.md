# Acquisition

Exact-input reuse: CPV has 665 released/reference records but 570 unique visible tasks. Cultural has 1,500 records but 1,499 unique visible tasks: source group `cultural:90`, `t3_i`, is an exact visible-input no-op relative to its Original. That author-labeled Id condition remains in the declared main analysis and shares the exact-input prediction; it is not removed or relabeled using model outcomes.

- medeinst: [zhui711/MedEinst](https://huggingface.co/datasets/zhui711/MedEinst), revision `354f4b527e764a8f2bebea8f71be55e0a6966402`; source files in acquisition.json.
- medpic: [TIM0927/MedPIC-Bench](https://huggingface.co/datasets/TIM0927/MedPIC-Bench), revision `9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983`; source files in acquisition.json.
- cpv: [kenza-ily/medqa-cpv](https://huggingface.co/datasets/kenza-ily/medqa-cpv), revision `ba7e59489f4c8e2a32d977a099e95bc3bc2587b5`; source files in acquisition.json.
- medcounterfact: [KaijieMo-kj/Counterfactual-Medical-Evidence](https://github.com/KaijieMo-kj/Counterfactual-Medical-Evidence), revision `f35b98063b51a63e677829b6d173029d98dd3b1e`; source files in acquisition.json.
- cultural: [HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs](https://github.com/HIVE-UofT/Evaluating-Cultural-Cues-Medical-LLMs), revision `5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f`; source files in acquisition.json.

Released rows: MedEinst 10766; MedPIC 467; CPV 12310 in 1202 groups; Cultural 150 groups × 10 = 1500 inputs; MedCounterFact 203 original + 809 replaced. Cultural Neutral is absent. Four existing caches match current remote revisions checked 2026-09-06.

CPV authentic question field is verified against author create.py (case_text and question both initialized from original MedQA question). Variants use case_text alone. Cultural originals all match author test.jsonl by complete normalized question, exact options and gold. No published model answers downloaded.

MedPIC official pair map unavailable: GF–CF is unpaired_composition_gap. MedCounterFact aligns only metadata.id; original metadata.question and treatment fields never enter model inputs. Public author releases without repository license remain local; only download code, IDs and derived aggregate outputs are committed.

Cultural slots follow the paper’s C1/C2/C3 order: t1 Indigenous Canadian, t2 Middle-Eastern Muslim, t3 Southeast Asian. Id, Context, and Id+Context retain the author operations. See https://arxiv.org/html/2601.20102v1 . The source file contains no Neutral field despite its presence in paper tables.
