# Five source-unit checks per benchmark

Full prepared-set audit: normalization preserves internal punctuation and numeric operators; zero within-item option-text collisions and zero collisions among the 46 canonical diagnosis labels were found. All six recorded CPV/Cultural source-overlap pairs also match with punctuation retained (NFKC, case and whitespace only). The historical question-suffix matcher was made tolerant of the already-trimmed terminal question mark: rescanning the same 163 frozen files still finds 3,550 previously exposed official test cases, with zero changes to this run's exposure labels or sample IDs.
Inference receives only item_id, question, options, fixed_evidence, answer_format. No gold/group/role/taxonomy enters solver.
Full prepared inputs stay local and are not redistributed.

## medeinst:case_17052
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000000: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1379/0.
- s000001: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=1387/0.

## medeinst:case_123636
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000002: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1193/0.
- s000003: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=1293/0.

## medeinst:case_56300
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000004: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1196/0.
- s000005: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=890/0.

## medeinst:case_24586
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000006: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=859/0.
- s000007: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=912/0.

## medeinst:case_45856
Revision: 354f4b527e764a8f2bebea8f71be55e0a6966402; records=2; mapping=official.
- s000008: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=reference; input lengths=1240/0.
- s000009: format=diagnosis; option keys=[]; evidence articles=0; gold type=str; role=variant; input lengths=980/0.

## medpic:SS-HF-HFREF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000838: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=348/0.

## medpic:SS-HF-HFPEF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000839: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=330/0.

## medpic:SS-HF-NOHF-001
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000840: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=388/0.

## medpic:SS-HF-HFREF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000841: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=402/0.

## medpic:SS-HF-HFPEF-002
Revision: 9ef6db4f13865b14fc2e6be3f94dcfaf3a0cf983; records=1; mapping=unavailable.
- s000842: format=multi; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=list; role=guideline_following; input lengths=353/0.

## cpv:medqa_00813
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001305: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=675/0.
- s001306: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=685/0.

## cpv:medqa_01076
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001316: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=780/0.
- s001317: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=790/0.

## cpv:medqa_00448
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001327: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=1582/0.
- s001328: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=1592/0.

## cpv:medqa_00585
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001338: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=727/0.
- s001339: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=737/0.

## cpv:medqa_01242
Revision: ba7e59489f4c8e2a32d977a099e95bc3bc2587b5; records=11; mapping=official.
- s001349: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=reference; input lengths=514/0.
- s001350: format=single; option keys=['A', 'B', 'C', 'D']; evidence articles=0; gold type=str; role=variant_00; input lengths=524/0.

## medcounterfact:131
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003374: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=167/45462.
- s003375: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=142/45897.

## medcounterfact:37
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003379: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=216/1397.
- s003380: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=174/1327.

## medcounterfact:152
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003384: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=111/4843.
- s003385: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=93/4661.

## medcounterfact:108
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003389: format=relation; option keys=[]; evidence articles=2; gold type=str; role=reference; input lengths=121/37104.
- s003390: format=relation; option keys=[]; evidence articles=2; gold type=str; role=variant_1; input lengths=106/36700.

## medcounterfact:119
Revision: f35b98063b51a63e677829b6d173029d98dd3b1e; records=5; mapping=official.
- s003394: format=relation; option keys=[]; evidence articles=1; gold type=str; role=reference; input lengths=133/60800.
- s003395: format=relation; option keys=[]; evidence articles=1; gold type=str; role=variant_1; input lengths=130/60369.

## cultural:0
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001875: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=947/0.
- s001876: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=984/0.

## cultural:1
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001885: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=773/0.
- s001886: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=820/0.

## cultural:2
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001895: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=738/0.
- s001896: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=796/0.

## cultural:3
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001905: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=477/0.
- s001906: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=515/0.

## cultural:4
Revision: 5ded0d24cd3cb09e26ce3128a3fe7fa9f0a4631f; records=10; mapping=official.
- s001915: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=reference; input lengths=404/0.
- s001916: format=single; option keys=['A', 'B', 'C', 'D', 'E']; evidence articles=0; gold type=str; role=t1_i; input lengths=448/0.

Potential ambiguities: MedPIC has no official pair map; MedEinst multi-edit taxonomy remains unresolved; CPV no-op and sex-specific clinical text are flagged; Cultural Neutral absent and options can exceed four; MedCounterFact original metadata text never fills replacement input.
Raw source checks and complete prompts are retained locally; do not paste license-unclear text into Git.
