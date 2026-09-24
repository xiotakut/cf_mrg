"""Lossless locations for bounded evidence-ID generation, using current inputs only."""
import re

from cf_moa.tools.provenance import sources, bind_quote


def text_spans(text, maximum):
    """Cover every non-whitespace character, retaining original character offsets.

    Prefer sentence/line boundaries; split a longer span at whitespace or, as a
    last resort, at the fixed character boundary. This is indexing, not selection.
    """
    start = 0
    while start < len(text):
        while start < len(text) and text[start].isspace():
            start += 1
        if start == len(text):
            break
        stop = min(start + maximum, len(text))
        chunk = text[start:stop]
        boundary = re.search(r'[.!?](?=\s)|\n', chunk)
        if boundary:
            stop = start + boundary.end()
        elif stop < len(text):
            spaces = list(re.finditer(r'\s+', chunk))
            if spaces:
                stop = start + spaces[-1].start()
        if stop <= start:
            stop = min(start + maximum, len(text))
        while stop > start and text[stop-1].isspace():
            stop -= 1
        yield start, stop
        start = stop


def evidence_catalog(packet, limits):
    catalog = {}
    counts = {'Q': 0, 'E': 0}
    for ref, source in sources(packet).items():
        prefix = 'Q' if ref == 'Q' else 'E'
        for start, end in text_spans(source['text'], limits['evidence_span_chars']):
            key = prefix + str(counts[prefix])
            counts[prefix] += 1
            catalog[key] = dict(ref=ref, start=start, end=end,
                text=source['text'][start:end], source_sha256=source['sha256'], kind=source['kind'])
    return catalog, len(catalog) > limits['evidence_catalog_entries']


def reference(packet, catalog, key, *, patient=False):
    if key not in catalog:
        raise ValueError('Unknown evidence ID: ' + key)
    entry = catalog[key]
    if patient and entry['ref'] != 'Q':
        raise ValueError('Only Q IDs may establish current-patient evidence')
    checked = bind_quote(packet, entry['ref'], entry['text'], start=entry['start'])
    if checked['end'] != entry['end'] or checked['source_sha256'] != entry['source_sha256']:
        raise ValueError('Evidence catalog no longer matches the current legal input')
    return dict(ref=entry['ref'], quote=entry['text'], start=entry['start'])
