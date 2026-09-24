"""C4: existing old-pool-plus-three control on a shared adopted F pool.

New draws use the unchanged cycle1 ordinary-reanswer request/format policy.
This is a separately costed sampling control, never the RCV default path.
"""
from collections import Counter
from copy import deepcopy

from cf_moa.agents import a5_candidate_verify as rcv, a5_premise

VARIANT = 'a5_old_pool_plus_three_control_v1'


def select(saved_proposal, candidates, supplementary):
    base = saved_proposal['native_proposal']
    votes = [v for v in saved_proposal['trace']['predictions'] if isinstance(v, str)]
    votes += [row['native_answer']['answer_choice'] for row in supplementary]
    counts = Counter(votes)
    top = {key for key,value in counts.items() if value == max(counts.values())}
    selected = base['answer_choice'] if base['answer_choice'] in top else next(v for v in votes if v in top)
    representatives = {c['key']: c['native_response'] for c in candidates}
    representatives[base['answer_choice']] = base
    native = representatives.get(selected)
    if native is None:
        native = next(row['native_answer'] for row in supplementary if row['native_answer']['answer_choice'] == selected)
    return deepcopy(native), dict(selected_key=selected, vote_counts=dict(counts), tied_maximum=sorted(top))


def run(packet, session, base_native_answer, saved_proposal, *, include_rationales=True, config=None):
    if config is not None and config != {'seed':42}:
        raise ValueError('C4 fixes its supplementary seeds to 42,43,44')
    rcv._bind(packet, saved_proposal)
    base=saved_proposal.get('native_proposal')
    candidates=rcv.candidate_records(packet,saved_proposal)
    if (saved_proposal.get('applicability')=='unsupported' or not isinstance(base,dict)
            or base.get('answer_choice') not in rcv.r5_module().native_keys(packet.native_input)
            or len(candidates)<2):
        result=rcv.run(packet,session,base_native_answer,saved_proposal,config={'seed':42})
        result['variant']=VARIANT
        return result
    start=session.checkpoint()
    replies=[]
    for seed in (42,43,44):
        replies.append(a5_premise.run(packet,session,base_native_answer,saved_proposal,
                                     control=True,config={'seed':seed}))
    # A failed complete supplemental answer remains an unavailable control;
    # do not silently turn a predeclared three-draw control into two draws.
    valid=all(row['native_answer'] is not None for row in replies)
    native,selection=select(saved_proposal,candidates,replies) if valid else (None,{})
    trace=dict(route='old_pool_plus_three',old_f_identity=saved_proposal['variant'],
        seeds=[42,43,44],supplementary=replies,**selection,
        supplementary_policy_source=a5_premise.CONTROL,
        selection_policy='old_pool_votes_plus_three; ties retain F; earliest old representative except F whole response',
        auxiliary_policy='existing cycle1 responses retain F auxiliary fields; unchanged historical control identity')
    return dict(variant=VARIANT,native_answer=native,native_valid=native is not None,
        status='complete' if valid else 'unavailable',trace=trace,cost=session.cost_since(start),
        warnings=[],new_answer_generation_calls=sum(len(r['raw']) for r in replies))
