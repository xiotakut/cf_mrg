"""Thin evidence adapter for the selected complete R2 support recomputation."""
import json

from cf_moa.contracts import AgentProposal
from cf_moa.tools.legacy import r123_module
from cf_moa.tools.provenance import bind_quote

VARIANT = 'legacy_positive_facts_scoped_inherit_unknown'


def applicable(packet):
    return ('medication_rules_71' in packet.available_tools
            and r123_module('r2_program_head').eligible(packet.native_input))


def run(packet, session):
    checkpoint = session.checkpoint()
    if not applicable(packet):
        return AgentProposal('A2', VARIANT, packet.input_hash, 'unsupported', None,
            unresolved=['Outside the selected finite medication-rule capability'],
            cost=session.cost_since(checkpoint))
    kernel = r123_module('r2_condition_head')
    program = r123_module('r2_program_head')
    indexed = r123_module('r2_indexed_head')
    raw_values = []

    def generate(messages, schema):
        raw = session.generate(messages, schema, seed=42, temperature=0.0,
                               max_tokens=2048, stage='A2:positive_facts')
        raw_values.append(raw)
        return raw

    result = session.tool('medication_rules_71', kernel.optimize,
                          packet.native_input, packet.baseline_answer, generate)
    facts = result.get('facts', {})
    extracted = json.loads(raw_values[0]).get('facts', {}) if facts else {}
    aliases = r123_module('r2_positive_facts').ALIASES
    sentences = indexed.sentences(packet.native_input)
    claims = []
    for field, value in facts.items():
        if value is None:
            continue
        source_field = aliases.get(field, (field,))[0]
        record = extracted.get(source_field, extracted.get(field, {}))
        refs = []
        for evidence_id in record.get('evidence_ids', []):
            text = sentences[evidence_id]
            refs.append(bind_quote(packet, 'Q', text, start=packet.question.find(text)))
        claims.append(dict(claim_id='A2:fact:' + field, kind='patient_fact',
            field=field, value=value, references=refs, scope=result.get('scope'),
            entailment_status='model_extracted_with_location_and_numeric_checks'))
    rules = {r['id']: r for r in program.RULES}
    changes = []
    for candidate, option in result.get('options', {}).items():
        for path in option['paths']:
            rule = rules[path['rule_id']]
            key = 'A2:path:' + candidate + ':' + path['rule_id']
            claims.append(dict(claim_id=key, kind='general_knowledge',
                candidate=candidate, rule=rule, path_state=path['state'],
                prerequisites=path['prerequisites'], exception=path['exception'],
                scope=result.get('scope'), provenance='selected_finite_rule_bank',
                conditional_on_model_facts=True))
            changes.append(dict(change_id=key, candidate=candidate,
                path_id=path['rule_id'], action='recompute_path', state=path['state'],
                claim_ids=[key], scope=result.get('scope')))
    return AgentProposal('A2', VARIANT, packet.input_hash,
        'supported' if result.get('applied') else 'partial', result['answer'],
        claims=claims, requested_changes=changes,
        unresolved=[result['reason']] if not result.get('applied') else [],
        checks=[dict(type='program_execution', name='three_valued_scoped_support',
                     conditional_on_extracted_facts=True),
                dict(type='model_assessment', name='patient_fact_extraction')],
        cost=session.cost_since(checkpoint), trace=dict(legacy_result=result, raw_facts=raw_values,
            unknown_policy='inherit_current_initial_answer', not_a_delete_only_head=True))
