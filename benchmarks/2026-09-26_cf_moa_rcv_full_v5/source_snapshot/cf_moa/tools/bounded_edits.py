"""Local evidence edits with exact current-question binding.

Eligibility recognizes a limited English clinical form, not arbitrary natural
language instructions. Unknown forms, task clauses and layout are ineligible;
this does not establish clinical feasibility or require an answer to stay/flip.
"""
from copy import deepcopy
from dataclasses import asdict, replace
import re

from cf_moa.contracts import digest


# Keep segmentation and original indices stable; qualification never renumbers Q:N.
_SEGMENTS = r'.+?(?:[.!?](?=\s+[A-Z]|\s*$)|\n|$)'
_DIRECTIVE = re.compile(
    r'\b(?:please|which|what|would|could|should|choose|select|answer|give|identify|'
    r'determine|diagnose|name|state|provide|indicate|return|respond|list|explain|'
    r'infer|decide|recommend|summarize|classify|report|output|tell|write|'
    r'formulate|asking|requesting)\b|'
    r'\bmost likely (?:diagnosis|cause|condition|explanation)\b', re.I)
_DECLARATION = re.compile(
    r'^(?:(?:the patient|patient|he|she|i)\s+'
    r'(?:(?:currently|also)\s+)?(?:has|have|had|is|am|was|reports|reported|'
    r'feels?|takes?|smokes?|drinks?|undergo(?:es)?|presents?)\b|'
    r'my\s+(?:BMI|temperature|blood pressure|pulse)\b|'
    r'the\s+(?:pain(?: locations)?|rash|swelling|lesions|affected regions|symptoms|temperature|pulse)\s+'
    r'(?:is|are|was|were|has|have|do|does|radiates|appeared|started)\b|'
    r'on a scale of\s+\d+\s*-\s*\d+\s*,?\s+the\s+'
    r'(?:pain|itching|swelling|intensity|speed of pain onset)\b|'
    r'at\s+\d{1,2}:\d{2}\s+(?:glucose|temperature|blood pressure|pulse)\b)', re.I)
_CLINICAL_FIELD = re.compile(
    r'^(?:sex|age|geographical region|temperature|blood pressure|pulse|'
    r'heart rate|respiratory rate|oxygen saturation|glucose)\s*:\s*\S', re.I)
_ATTRIBUTE_HEADER = re.compile(
    r'^the (?:pain(?: locations)?|rash|swelling|affected regions) '
    r'(?:is(?: located (?:on|at))?|are|radiates to these locations)\s*:\s*$', re.I)
_ATTRIBUTE_VALUE = re.compile(
    r'(?:sensitive|exhausting|tedious|heavy|crushing|sharp|dull|burning|'
    r'red|pink|nowhere|(?:back|side|top|front) of (?:the )?(?:head|neck|chest)|'
    r'(?:dorsal aspect|palmar face) of the wrist|'
    r'ankle|wrist|shoulder|forehead|cheek|nose|head|neck|chest|back|arm|leg|'
    r'calf|breast|biceps|jaw|tibia)'
    r'(?:\([LR]\))?\.?', re.I)


def _clinical_segment(text, attribute_header):
    """Positive, deliberately finite eligibility; no generic prose/bullet fallback."""
    if not text or len(text)>320 or '?' in text or _DIRECTIVE.search(text):
        return False
    content = re.sub(r'^-\s+', '', text.strip())
    if content.startswith('* '):
        return bool(attribute_header and _ATTRIBUTE_VALUE.fullmatch(content[2:].strip()))
    # Reject mixed evidence/task segments, including lowercase post-period clauses.
    clauses = [re.sub(r'^-\s+', '', clause.strip()) for clause in
               re.split(r';\s*|(?<=[.!])\s+|\s+-\s+', content) if clause.strip()]
    return bool(clauses) and all(_DECLARATION.match(clause) or _CLINICAL_FIELD.match(clause)
                                 for clause in clauses)


def editable_spans(packet):
    result = {}
    attribute_header = False
    for index,match in enumerate(re.finditer(_SEGMENTS,packet.question,re.S)):
        text = match.group()
        start = match.start()+len(text)-len(text.lstrip())
        text = text.lstrip()
        eligible = _clinical_segment(text,attribute_header)
        if eligible:
            result[f'Q:{index}'] = dict(ref='Q',start=start,end=match.end(),text=text)
        content = re.sub(r'^-\s+', '', text.strip())
        if content:
            if content.startswith('* '):
                attribute_header = attribute_header and eligible
            else:
                attribute_header = bool(_ATTRIBUTE_HEADER.fullmatch(content))
    return result


def _occurrences(text, question):
    # Include overlapping occurrences: an ambiguous binding must never be guessed.
    return [match.start() for match in re.finditer('(?='+re.escape(question)+')',text)]


def bind_question(packet):
    """Bind one exact string occurrence or one exact occurrence in user messages.

    Other roles may quote the question but are never editable. Multiple user
    occurrences (including quoted documents) are ambiguous and explicitly fail.
    No role/quotation or semantic-currentness inference is attempted for strings.
    """
    if isinstance(packet.original_context,str):
        matches = [(None,start) for start in _occurrences(packet.original_context,packet.question)]
        kind = 'string'
    else:
        matches = [(index,start) for index,message in enumerate(packet.original_context)
                   if message['role']=='user'
                   for start in _occurrences(message['content'],packet.question)]
        kind = 'user_message'
    if len(matches)!=1:
        raise ValueError('Exact current-question binding requires one '+kind+
                         ' occurrence; found '+str(len(matches)))
    index,start = matches[0]
    return dict(kind=kind,message_index=index,question_start=start,
                question_end=start+len(packet.question))


def is_explicit_negation(original,replacement):
    # Accept only a negation insertion or an exact positive/negative word swap;
    # other characters, numbers, units, subject and chronology stay verbatim.
    if replacement == 'It is not the case that '+original:
        return True
    for match in re.finditer(r'\b(?:not |no |without )',replacement,re.I):
        if replacement[:match.start()]+replacement[match.end():] == original:
            return True
    for match in re.finditer(r'\bpositive\b',original,re.I):
        if original[:match.start()]+'negative'+original[match.end():] == replacement:
            return True
    return False


def apply_edit(packet,edit):
    spans = editable_spans(packet)
    if (not isinstance(edit,dict) or set(edit) != {'span_id','operation','replacement'}
            or not all(isinstance(value,str) for value in edit.values())
            or edit['span_id'] not in spans):
        raise ValueError('Edit must refer to one declared visible question span')
    span = spans[edit['span_id']]
    operation,replacement = edit['operation'],edit['replacement']
    if operation=='delete':
        if replacement!='':
            raise ValueError('Deletion must use the empty replacement; it is not explicit negation')
    elif operation=='explicit_negation':
        if not is_explicit_negation(span['text'],replacement):
            raise ValueError('Negation must preserve all text outside a recognized local negation change')
    else:
        raise ValueError('Only deletion and explicit_negation are supported')
    before = asdict(packet)
    binding = bind_question(packet)
    question = packet.question[:span['start']]+replacement+packet.question[span['end']:]
    context = deepcopy(packet.original_context)
    index = binding['message_index']
    source = context if index is None else context[index]['content']
    start,end = binding['question_start']+span['start'],binding['question_start']+span['end']
    if source[start:end] != span['text']:
        raise ValueError('Bound context span differs from declared evidence')
    patched = source[:start]+replacement+source[end:]
    if index is None:
        context = patched
    else:
        context[index]['content'] = patched
    native = deepcopy(packet.native_input)
    native['question'] = question
    probe = replace(packet,native_input=native,question=question,original_context=context)
    # Build the expected full packet independently from the original snapshot.
    # Never copy the changed native/context objects into this reference.
    expected = deepcopy(before)
    expected_question = before['question'][:span['start']]+replacement+before['question'][span['end']:]
    expected['question'] = expected_question
    expected['native_input']['question'] = expected_question
    if index is None:
        original_text = before['original_context']
        expected['original_context'] = original_text[:start]+replacement+original_text[end:]
        unbound_unchanged = True  # There are no other messages in a string input.
    else:
        original_text = before['original_context'][index]['content']
        expected['original_context'][index]['content'] = original_text[:start]+replacement+original_text[end:]
        unbound_unchanged = (len(probe.original_context)==len(before['original_context']) and
            all(message==probe.original_context[i] for i,message in enumerate(before['original_context']) if i!=index))
    native_other_unchanged = ({k:v for k,v in before['native_input'].items() if k!='question'}==
                              {k:v for k,v in probe.native_input.items() if k!='question'})
    prefix_unchanged = patched[:start]==source[:start]
    suffix_unchanged = patched[start+len(replacement):]==source[end:]
    if (asdict(packet)!=before or asdict(probe)!=expected or not unbound_unchanged or
            not native_other_unchanged or not prefix_unchanged or not suffix_unchanged):
        raise ValueError('Edit changed data outside its authorized question/context patch')
    record = dict(edit=deepcopy(edit),original_span=span,original_input_hash=packet.input_hash,
        probe_input_hash=probe.input_hash,original_question_hash=digest(packet.question),
        probe_question_hash=digest(question),unchanged_prefix=prefix_unchanged,
        unchanged_suffix=suffix_unchanged,binding=dict(binding,edit_start=start,edit_end=end),
        complete_packet_diff_verified=True,native_other_fields_unchanged=native_other_unchanged,
        unbound_messages_unchanged=unbound_unchanged,
        semantic_feasibility='not established; bounded model-sensitivity probe only',
        deletion_is_negation=False)
    return probe,record
