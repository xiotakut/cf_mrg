"""The historical R1 dispatch, preserved as a control rather than named A1.

Identical task predicates, calls, and result fields to candidate/r1_head.py.
The original file stays in its historical package for reproducibility.
"""
from cf_moa.tools.legacy import r123_module


def optimize(item, original_context, original_answer, public_catalog, log_priors,
             score_codes, generate_facts):
    catalog = r123_module('r3_catalog_distribution_head')
    conditions = r123_module('r2_condition_head')
    program = r123_module('r2_program_head')
    if item['answer_format'] == 'diagnosis':
        return dict(catalog.optimize_calibrated(
            item, original_context, original_answer, public_catalog, log_priors,
            score_codes), branch='catalog_vote')
    if program.eligible(item):
        result = conditions.optimize(item, original_answer, generate_facts)
        return dict(result, branch='rule_support', used_original=not result['applied'])
    return dict(answer=original_answer, used_original=True, branch='original')
