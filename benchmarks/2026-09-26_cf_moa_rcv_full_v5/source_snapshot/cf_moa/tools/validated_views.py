"""Qualified code views retain every original character and all auxiliary fields."""
from copy import deepcopy
import json
import re

from cf_moa.contracts import digest


def qualify(packet):
    if isinstance(packet.original_context,str):
        return False,'An intact original message sequence is required'
    if packet.model_input is not None:
        return False,'This code-view candidate does not cover model-conditioned numerical outputs'
    if packet.native_input['answer_format'] not in ('single','robustness_single','relation'):
        return False,'Native format outside this single-answer code-view capability'
    options = packet.native_input.get('options',{})
    if not 2 <= len(options) <= 12 or not all(isinstance(x,str) for x in options.values()):
        return False,'Two to twelve complete textual native options are required'
    if len(set(options.values())) != len(options):
        return False,'Duplicate option meanings lack a unique semantic mapping'
    if 'answer_choice' not in packet.answer_schema.get('properties',{}):
        return False,'No declared native answer_choice field'
    relative = r'\b(?:all|none|both|either|neither)\b.{0,24}\b(?:above|below|former|latter)\b|\b(?:first|last|previous|next) option\b'
    if any(re.search(relative,text,re.I) for text in [packet.question,*options.values()]):
        return False,'Relative option references are not qualified for code remapping'
    for code in options:
        pointer = r'\b(?:option|choice|answer)\s*["\x27(]?'+re.escape(code)+r'\b'
        if any(re.search(pointer,text,re.I) for text in [packet.question,*options.values()]):
            return False,'Task text refers to an original option code'
    return True,'Complete original anchor plus explicit bijective readout code tables'


def views(packet):
    ok,reason = qualify(packet)
    if not ok:
        return [],reason
    originals = list(packet.native_input['options'])
    result = []
    for index,(prefix,order) in enumerate([('V',originals[1:]+originals[:1]),('W',list(reversed(originals)))]):
        mapping = {prefix+str(i+1):code for i,code in enumerate(order)}
        table = [{'output_code':code,'unchanged_option_text':packet.native_input['options'][original]}
                 for code,original in mapping.items()]
        instruction = (
            'Answer the same complete question above. All original patient facts, quantities, units, '
            'negation, time relations, subjects, supplied edits, documents and required auxiliary fields '
            'remain in force. Only the output code table changes for this readout. Use one output_code '
            'below in answer_choice; it refers to the unchanged option text, not the old option code. '
            'Do not summarize or omit the original input. Preserve all other required JSON fields.\n\n'+
            json.dumps(table,ensure_ascii=False))
        schema = deepcopy(packet.answer_schema)
        schema['properties']['answer_choice'] = dict(type='string',enum=list(mapping))
        messages = [*deepcopy(packet.original_context),dict(role='user',content=instruction)]
        assert messages[:-1] == packet.original_context
        assert set(mapping.values()) == set(originals) and len(mapping)==len(originals)
        result.append(dict(view_id=f'code_view_{index+1}',messages=messages,schema=schema,
            mapping=mapping,original_input_hash=packet.input_hash,
            original_context_hash=digest(packet.original_context),
            checks=dict(original_context_exact=True,original_question_exact=True,
                options_text_exact=True,bijection=True,patient_edits=0,external_reordering=0)))
    return result,reason


def align_answer(value, mapping):
    result = deepcopy(value)
    if result.get('answer_choice') not in mapping:
        raise ValueError('Output code is outside the view bijection')
    result['answer_choice'] = mapping[result['answer_choice']]
    return result
