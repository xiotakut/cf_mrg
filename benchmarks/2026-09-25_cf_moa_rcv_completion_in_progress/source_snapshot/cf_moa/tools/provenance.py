"""Exact source locations are distinct from model-assessed entailment."""
import json
import re

from cf_moa.contracts import digest


def sources(packet):
    result = {'Q': dict(kind='current_question', text=packet.question)}
    for index, evidence in enumerate(packet.native_input.get('fixed_evidence', [])):
        text = evidence if isinstance(evidence, str) else json.dumps(evidence, ensure_ascii=False)
        result['F' + str(index)] = dict(kind='required_task_evidence', text=text)
    for index, evidence in enumerate(packet.retrieved_context):
        result['D' + str(index)] = dict(kind='retrieved_knowledge', text=evidence['text'],
            uri=evidence.get('uri'), title=evidence.get('title'))
    # Some historical methods retain the actual retrieval only in their messages.
    contexts = ([dict(content=packet.original_context)] if isinstance(packet.original_context, str)
                else packet.original_context)
    for index, message in enumerate(contexts):
        result['C' + str(index)] = dict(kind='original_method_context', text=message['content'])
    for value in result.values():
        value['sha256'] = digest(value['text'])
    return result


def spans(packet):
    result = {}
    for ref, source in sources(packet).items():
        text = source['text']
        for index, match in enumerate(re.finditer(r'[^\n]+(?:\n|$)', text)):
            start, end = match.span()
            if text[start:end].strip():
                result[f'{ref}:{index}'] = dict(ref=ref, start=start, end=end,
                    text=text[start:end], kind=source['kind'], sha256=source['sha256'])
    return result


def bind_quote(packet, ref, quote, *, start=None):
    source = sources(packet).get(ref)
    if source is None or not isinstance(quote, str) or not quote:
        raise ValueError('A nonempty quote from a visible source is required')
    text = source['text']
    if start is None:
        start = text.find(quote)
        if start >= 0 and text.find(quote, start + 1) >= 0:
            raise ValueError('Repeated quote requires an explicit source offset')
    if type(start) is not int or start < 0 or text[start:start + len(quote)] != quote:
        raise ValueError('The quoted source span does not match')
    return dict(ref=ref, start=start, end=start + len(quote), quote=quote,
        source_sha256=source['sha256'], check='exact_location_only')


def validate_claim(packet, claim):
    references = [bind_quote(packet, r['ref'], r['quote'], start=r.get('start'))
                  for r in claim.get('references', [])]
    if not references:
        raise ValueError('A supported claim needs a visible source or actual tool trace')
    if claim.get('kind') == 'patient_fact' and any(r['ref'] != 'Q' for r in references):
        raise ValueError('External material cannot establish a current-patient fact')
    return dict(claim, references=references,
        entailment_status='model_assessment_not_program_proof')
