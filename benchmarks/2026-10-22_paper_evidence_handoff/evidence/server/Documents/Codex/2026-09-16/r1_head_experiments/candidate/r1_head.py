"""R1 development interface: frozen diagnosis voting and eligible medication support.

The caller supplies its original model callbacks and matching public catalog/priors.
Only current native task fields choose the branch; no R labels or answer keys are used.
"""
from r3_catalog_distribution_head import optimize_calibrated
from r2_condition_head import optimize as optimize_conditions
from r2_program_head import eligible


def optimize(item, original_context, original_answer, public_catalog, log_priors,
             score_codes, generate_facts):
    if item['answer_format']=='diagnosis':
        return dict(optimize_calibrated(item,original_context,original_answer,
                    public_catalog,log_priors,score_codes),branch='catalog_vote')
    if eligible(item):
        result=optimize_conditions(item,original_answer,generate_facts)
        return dict(result,branch='rule_support',used_original=not result['applied'])
    return dict(answer=original_answer,used_original=True,branch='original')
