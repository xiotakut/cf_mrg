"""Finite public-source rule bank for older-adult medication questions.

This is a research representation of selected AGS2023 recommendations, not a
complete prescribing knowledge base. Table/class/page attribution is explicit.
No benchmark IDs, answers, target-rule metadata or patient cases occur here.
"""
AGS='https://aging.rush.edu/wp-content/uploads/2023/10/J-American-Geriatrics-Society-2023-American-Geriatrics-Society-2023-updated-AGS-Beers-Criteria-for-potentially.pdf'
LABELS={
 'sertraline':'https://www.dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=f6346a11-88b9-4425-b08d-a22f19c4ceb4&type=display',
 'venlafaxine':'https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=27656716-8525-4a3a-a110-a48f0c081c31',
 'escitalopram':'https://www.dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d31c02d0-81d9-4aa4-bde9-52135aa5a66d',
 'fluoxetine':'https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=a7ba9184-7dad-4f82-a947-bb2cc6b760ce',
 'citalopram':'https://www.dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f3a26d92-b662-4896-82eb-261948042408',
 'duloxetine':'https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=3424a326-9543-44f7-b31c-f84e12509238',
}

def names(s):return s.split('|')
NSAID=names('diclofenac|diflunisal|etodolac|flurbiprofen|ibuprofen|indomethacin|ketorolac|meloxicam|nabumetone|naproxen|oxaprozin|piroxicam|sulindac')
COX2=['celecoxib']
AP=names('chlorpromazine|fluphenazine|haloperidol|perphenazine|aripiprazole|brexpiprazole|cariprazine|clozapine|lurasidone|olanzapine|paliperidone|pimavanserin|quetiapine|risperidone|ziprasidone')
BENZO=names('alprazolam|chlordiazepoxide|clobazam|clonazepam|clorazepate|diazepam|estazolam|lorazepam|midazolam|oxazepam|temazepam|triazolam')
ZDRUG=names('eszopiclone|zaleplon|zolpidem')
H2=names('cimetidine|famotidine|nizatidine')
TCA=names('amitriptyline|amoxapine|clomipramine|desipramine|imipramine|nortriptyline')
SSRI=names('sertraline|escitalopram|fluoxetine|citalopram')
SNRI=names('venlafaxine|duloxetine')
ANTIHIST=names('brompheniramine|chlorpheniramine|cyproheptadine|dimenhydrinate|diphenhydramine|doxylamine|hydroxyzine|meclizine|promethazine|triprolidine')
ANTIMUSC=names('darifenacin|fesoterodine|flavoxate|oxybutynin|solifenacin|tolterodine|trospium')
ACH=TCA+['paroxetine','prochlorperazine','promethazine']+ANTIHIST+ANTIMUSC+names('benztropine|trihexyphenidyl|chlorpromazine|clozapine|olanzapine|perphenazine|atropine|clidinium-chlordiazepoxide|dicyclomine|homatropine|hyoscyamine|scopolamine|cyclobenzaprine|orphenadrine')
ALPHA=names('doxazosin|prazosin|terazosin')
ACHE=names('donepezil|galantamine|rivastigmine')
STEROID=names('prednisone|prednisolone|methylprednisolone|dexamethasone|hydrocortisone')
OPIOID=names('codeine|fentanyl|hydrocodone|hydromorphone|meperidine|morphine|oxycodone|tramadol|tramadol immediate-release|tramadol extended-release')
AED=names('gabapentin|pregabalin|levetiracetam|valproic acid|lamotrigine|phenytoin|topiramate|oxcarbazepine')

# Prefix expressions preserve conjunctions, alternative supports and exceptions.
def atom(field,op='eq',value=True):return ['test',field,op,value]
def both(*xs):return ['all',*xs]
def either(*xs):return ['any',*xs]

RULES=[]
def add(key,drugs,when=True,unless=None,action='avoid',pages=(14,),note=''):
    RULES.append(dict(id=key,drugs=sorted(set(drugs)),action=action,when=when,unless=unless,
                      source_url=AGS,source_pages=list(pages),note=note))

# Table2 populations and named exceptions, including rules independent of Table3.
add('first_generation_antihistamines',[d for d in ANTIHIST if d!='diphenhydramine'],pages=(6,))
add('diphenhydramine',['diphenhydramine'],pages=(6,),unless=atom('severe_allergic_reaction'))
add('nitrofurantoin_suppression',['nitrofurantoin'],atom('long_term_suppression'),pages=(6,))
add('alpha_blocker_hypertension',ALPHA,atom('antihypertensive_purpose'),pages=(7,))
add('amiodarone_first_line',['amiodarone'],atom('first_line_af'),either(atom('heart_failure'),atom('lv_hypertrophy')),pages=(7,))
add('dronedarone_severe',['dronedarone'],either(atom('permanent_af'),atom('severe_or_decompensated_hf')),pages=(7,))
add('digoxin_first_line',['digoxin'],atom('digoxin_first_line_af_or_hf'),pages=(8,))
add('digoxin_high_dose',['digoxin'],atom('digoxin_mg_day','gt',.125),pages=(8,))
add('strong_anticholinergic_antidepressants',TCA+['paroxetine'],pages=(8,))
add('doxepin_high_dose',['doxepin'],atom('doxepin_mg_day','gt',6),pages=(8,))
add('antipsychotic_general',AP,unless=atom('antipsychotic_accepted_indication'),pages=(8,9,12),note='Use-specific exception; PD disease interaction is evaluated separately.')
add('benzodiazepines_general',BENZO,unless=atom('benzodiazepine_specific_indication'),pages=(9,))
add('z_drugs',ZDRUG,pages=(9,))
add('ppi_long_use',names('dexlansoprazole|esomeprazole|lansoprazole|omeprazole|pantoprazole|rabeprazole'),atom('ppi_duration_weeks','gt',8),atom('ppi_accepted_indication'),pages=(11,))
add('metoclopramide_general',['metoclopramide'],unless=both(atom('gastroparesis'),atom('metoclopramide_weeks','le',12)),pages=(11,),note='Rare longer-use exceptions not modeled: unresolved specialist exceptions remain a scope limit.')
gastro_exception=both(atom('alternatives_ineffective'),atom('gastroprotection'))
add('nsaid_chronic',NSAID,atom('chronic_nsaid_use'),gastro_exception,pages=(11,12))
add('nsaid_scheduled_comedication',NSAID,both(atom('scheduled_nsaid_use'),atom('bleeding_risk_comedication')),gastro_exception,pages=(11,12))
add('indomethacin_ketorolac',['indomethacin','ketorolac'],pages=(12,))
add('meperidine',['meperidine'],pages=(12,))
add('musculoskeletal_relaxants',names('carisoprodol|chlorzoxazone|cyclobenzaprine|metaxalone|methocarbamol|orphenadrine'),pages=(12,))

# Table3 drug-disease interactions. Class members are materialized before inference.
add('hf_cilostazol_dmq',names('cilostazol|dextromethorphan-quinidine'),atom('heart_failure'))
add('hf_reduced_ccb',names('diltiazem|verapamil'),both(atom('heart_failure'),atom('hf_reduced_ef')))
add('hf_symptomatic',NSAID+COX2+['dronedarone','pioglitazone'],both(atom('heart_failure'),atom('hf_symptomatic')))
add('syncope_selected_ap_tca',['chlorpromazine','olanzapine','amitriptyline','clomipramine','doxepin','imipramine'],atom('syncope'))
add('syncope_ache',ACHE,both(atom('syncope'),atom('bradycardia_related_syncope')))
add('syncope_alpha',ALPHA,both(atom('syncope'),atom('orthostatic_related_syncope')))
delirium=either(atom('delirium'),atom('high_delirium_risk'))
psych_exception=either(atom('antipsychotic_accepted_indication'),both(atom('nonpharm_failed_or_impossible'),atom('substantial_harm_risk')))
add('delirium_ach_h2_z',ACH+H2+ZDRUG,delirium,pages=(15,16,23))
add('delirium_benzo',BENZO,delirium,atom('benzodiazepine_specific_indication'),pages=(15,16))
add('delirium_ap',AP,delirium,psych_exception,pages=(15,16))
add('delirium_steroid',STEROID,both(delirium,atom('systemic_steroid_route')),atom('systemic_steroid_required'),pages=(15,16))
add('delirium_opioid',OPIOID,delirium,atom('opioid_required_balanced_pain_plan'),pages=(15,16),note='The guideline asks for balanced pain management; represented exception requires explicit plan.')
add('dementia_ach_benzo_z',ACH+BENZO+ZDRUG,atom('dementia'),pages=(15,16,23))
add('dementia_ap',AP,both(atom('dementia'),atom('chronic_or_persistent_ap')),psych_exception,pages=(15,16))
add('falls_ach_antidepressant_benzo_z',ACH+TCA+SSRI+SNRI+BENZO+ZDRUG,atom('falls_or_fractures'),atom('no_safer_alternative'),pages=(15,16,23))
add('falls_ap',AP,atom('falls_or_fractures'),either(atom('no_safer_alternative'),atom('antipsychotic_accepted_indication')),pages=(15,16))
add('falls_antiepileptic',AED,atom('falls_or_fractures'),either(atom('no_safer_alternative'),atom('seizure_or_mood_disorder')),pages=(15,16))
add('falls_opioid',OPIOID,atom('falls_or_fractures'),either(atom('no_safer_alternative'),atom('severe_acute_pain')),pages=(15,16))
add('parkinson_dopamine_antagonist',[d for d in AP if d not in ['clozapine','pimavanserin','quetiapine']]+['metoclopramide','prochlorperazine','promethazine'],atom('parkinson'),pages=(16,12))
add('ulcer_nsaid',NSAID+['aspirin'],atom('peptic_ulcer_history'),gastro_exception,pages=(16,22))
add('female_incontinence_alpha',ALPHA,both(atom('female'),atom('urinary_incontinence')),pages=(16,))
add('male_bph_anticholinergic',[d for d in ACH if d not in ANTIMUSC],both(atom('female','eq',False),atom('bph_or_luts')),pages=(16,23))

# Table6: variable identity stays CrCl or eGFR; no cross-measure substitution.
for drug,threshold in [('nitrofurantoin',30),('amiloride',30),('fondaparinux',30),('spironolactone',30),('triamterene',30),('duloxetine',30),('probenecid',30)]:
    add('renal_avoid_'+drug,[drug],atom('crcl','lt',threshold),pages=(21,22))
add('renal_nsaid',NSAID+COX2,atom('crcl','lt',30),pages=(22,))
add('renal_baclofen',['baclofen'],atom('egfr','lt',60),pages=(22,))
add('renal_tmp_smx_avoid',['trimethoprim-sulfamethoxazole'],atom('crcl','lt',15),pages=(21,))
add('renal_tmp_smx_reduce',['trimethoprim-sulfamethoxazole'],both(atom('crcl','ge',15),atom('crcl','le',29)),action='dose_reduce',pages=(21,))
add('renal_dabigatran_avoid',['dabigatran'],atom('crcl','lt',30),pages=(21,))
add('renal_dabigatran_ddi_reduce',['dabigatran'],both(atom('crcl','gt',30),atom('dabigatran_dose_relevant_interaction')),action='dose_reduce',pages=(21,))
add('renal_dofetilide_avoid',['dofetilide'],atom('crcl','lt',20),pages=(21,))
add('renal_dofetilide_reduce',['dofetilide'],both(atom('crcl','ge',20),atom('crcl','le',59)),action='dose_reduce',pages=(21,))
add('renal_edoxaban_avoid',['edoxaban'],either(atom('crcl','lt',15),atom('crcl','gt',95)),pages=(21,))
add('renal_edoxaban_reduce',['edoxaban'],both(atom('crcl','ge',15),atom('crcl','le',50)),action='dose_reduce',pages=(21,))
add('renal_rivaroxaban_avoid',['rivaroxaban'],atom('crcl','lt',15),pages=(21,))
add('renal_rivaroxaban_reduce',['rivaroxaban'],both(atom('crcl','ge',15),atom('crcl','le',50)),action='dose_reduce',pages=(21,),note='Indication-specific manufacturer dosing remains necessary in clinical use.')
for drug,threshold,op in [('ciprofloxacin',30,'lt'),('enoxaparin',30,'lt'),('gabapentin',60,'lt'),('pregabalin',60,'lt'),('levetiracetam',80,'le'),('cimetidine',50,'lt'),('famotidine',50,'lt'),('nizatidine',50,'lt'),('colchicine',30,'lt')]:
    add('renal_reduce_'+drug,[drug],atom('crcl',op,threshold),action='dose_reduce',pages=(21,22))
add('renal_tramadol_ir',['tramadol immediate-release'],atom('crcl','lt',30),action='dose_reduce',pages=(22,))
add('renal_tramadol_er',['tramadol extended-release'],atom('crcl','lt',30),pages=(22,))

CLASS_SOURCES=dict(antipsychotic=dict(pages=[8,12],drugs=AP),nsaid=dict(pages=[11,12,22],drugs=NSAID+COX2),
    strong_anticholinergic=dict(pages=[8,23],drugs=sorted(set(ACH))),ssri=dict(drugs=SSRI,labels={d:LABELS[d] for d in SSRI}),snri=dict(drugs=SNRI,labels={d:LABELS[d] for d in SNRI}))
