"""Freeze the reviewed text cohort and its independent M0/M1 inputs."""
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

COLLECTION = Path('/home/data3/txy/Documents/Codex/2026-09-08/ben-c-h-ma-r-k/medical_cf_collection')
PACK = Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
OLD = PACK / 'results_cf_full_comparison'
OUT = PACK / 'results_r1_r5_m0_m1_20260908'
METHODS = {'M0': 'direct_llama', 'M1': 'retrieval_only_llama'}


def read(path):
    if not path.exists():
        return []
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write(path, rows):
    with path.open('w') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


# Detect an actual reference to an unavailable visual, not an imaging finding
# described in prose. These matches are retained in the exclusion receipt.
IMAGE = re.compile(
    r'(?:shown|displayed|depicted|illustrated|indicated|marked)\s+in (?:the |an? )?(?:image|figure|photograph|picture|diagram|exhibit)'
    r'|(?:image|figure|photograph|picture|diagram|exhibit|micrograph)\s+(?:shown|below|above|attached|provided)'
    r'|(?:following|accompanying|attached)\s+(?:image|figure|photograph|picture|diagram|exhibit|micrograph)'
    r'|(?:indicated|marked|denoted) by (?:the |an? )?arrow'
    r'|(?:image|figure)\s+[A-F1-9]\b'
    r'|(?:image|figure|photograph|picture|diagram|exhibit|micrograph|radiograph|x-ray|ECG|EKG|electrocardiogram|electroencephalogram|tracing|histology|biopsy|fundoscop\w*|rash|lesion|physical examination findings)[^.\n]{0,80}(?:shown|displayed|depicted|illustrated)\s+(?:below|above|here)'
    r'|<image>|!\[[^\]]*\]\(', re.I)


def unused_image_reason(text):
    match = IMAGE.search(text)
    return match.group() if match else None


def prepare(previous_items=None):
    assert not (OUT / 'plan.json').exists(), 'Inputs already frozen; do not rebuild a running benchmark.'
    
    units = selected_units
    assert len(units) == 6104 and all(u['review_state'] == 'reviewed' for u in units)
    old_items = prior_pool
    old_labels = {(r['dataset'], r['source_id'], r['role'], r['protocol']): r for r in read(OLD / 'evaluation_labels.jsonl')}
    m22roots = {}
    with (COLLECTION / 'parts/evidence_other/full_root_records.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['resource_id'] == 'M22':
                m22roots[row['source_root_id']] = row['original_records'][0]
    items, labels, coverage, recoveries = {}, [], [], []
    # Seed deduplication with every compatible old input before processing any
    # new source; source iteration order must not create duplicate reader calls.
    visible_ids = {json.dumps({k: r[k] for k in ['question', 'options', 'fixed_evidence', 'answer_format']}, ensure_ascii=False): iid
                   for iid, r in old_items.items()}
    next_id = 200000
    if previous_items:
        for r in previous_items:
            sig = json.dumps({k: v for k, v in r.items() if k != 'item_id'}, ensure_ascii=False)
            assert sig not in visible_ids or visible_ids[sig] == r['item_id']
            visible_ids[sig] = r['item_id']
        next_id = max(int(r['item_id'][1:]) for r in previous_items) + 1

    def add(u, role, question, options=None, evidence=None, fmt='single', gold=None,
            task='native', target=None, old=None, extra=None, max_tokens=64):
        nonlocal next_id
        item = dict(question=question, options=options or {}, fixed_evidence=evidence or [],
                    answer_format=fmt)
        if fmt in ['open', 'robustness_single', 'robustness_open']:
            item['max_tokens'] = max_tokens
        sig = json.dumps(item, ensure_ascii=False)
        if old:
            iid = old['item_id']
            assert all(item[k] == old[k] for k in ['question', 'options', 'fixed_evidence', 'answer_format'])
        elif sig in visible_ids:
            iid = visible_ids[sig]
        else:
            iid = f's{next_id:06d}'
            next_id += 1
        visible_ids.setdefault(sig, iid)
        items[iid] = dict(item_id=iid, **item)
        judgments = u['judgments']
        if target:
            judgments = [j for j in judgments if j.get('target_id') == target or j['judgment_id'].endswith(':' + target)]
        eligible = not any(j.get('scoring_eligible') is False for j in judgments)
        row = dict(record_id=f"{u['unit_id']}::{task}::{role}", unit_id=u['unit_id'],
                   resource_id=u['resource_id'], benchmark=u['benchmark'], item_id=iid,
                   group_id=f"{u['resource_id']}:{u.get('source_root_id') or u['unit_id']}",
                   source_family=u.get('source_family'), role=role, task=task, target=target,
                   labels=sorted({l for j in judgments for l in j['labels']}),
                   gold=gold, scoring_eligible=eligible and gold is not None,
                   scoring_exclusion=('reviewed_reference_ineligible' if not eligible else 'no_automatic_gold' if gold is None else None),
                   review_resolution=u['review_resolution'], split=u.get('split'),
                   source=u['source'], **(extra or {}))
        labels.append(row)
        return iid

    for n, u in enumerate(units):
        rid = u['resource_id']; originals = u['original_records']; start = len(labels)
        c = dict(unit_id=u['unit_id'], resource_id=rid, labels=u['labels'], status='included', reason=None)
        if rid == 'M25':
            c.update(status='excluded_multimodal', reason='MedMKEB requires missing images')
            coverage.append(c); continue
        if rid == 'M24':
            c.update(status='not_applicable', reason='Native post-edit task requires a knowledge editing method; M0/M1 do not edit weights')
            coverage.append(c); continue
        refs = u.get('existing_evaluation_records', u.get('existing_evaluation_links', []))
        if refs:
            selected = [old_labels[(r['dataset'], r['source_id'], r['role'], r['protocol'])] for r in refs]
            reason = next((image_reason(old_items[r['item_id']]['question']) for r in selected if image_reason(old_items[r['item_id']]['question'])), None)
            if reason:
                c.update(status='excluded_multimodal', reason=reason)
            else:
                for r in selected:
                    old = old_items[r['item_id']]
                    add(u, r['role'], old['question'], old['options'], old['fixed_evidence'], old['answer_format'], r['gold'], old=old,
                        extra={'old_evaluation_record': r})
        elif rid in ['M12', 'M14', 'M16']:
            r = originals[0]
            if rid == 'M12':
                q1 = r['original_question']; q2 = r[next(k for k in r if k.startswith('adv_question_'))]
                opts, gold = r['options'], r['answer_idx']
            elif rid == 'M14':
                q1 = r['Question']; q2 = r[next(k for k in r if k not in ['', 'Question', 'Row Number'])]
                match = recovered[q1]; opts=match['options']; gold=match['gold']
                recoveries.append(dict(unit_id=u['unit_id'], **match))
            else:
                q1, q2 = r['question_1_text'], r['question_2_text']; opts, gold = {}, None
            reason = image_reason(q1) or image_reason(q2)
            if reason:
                c.update(status='excluded_multimodal', reason=reason)
            else:
                for role, q in [('reference', q1), ('variant', q2)]:
                    add(u, role, q, opts, fmt='single' if opts else 'open', gold=gold, max_tokens=512)
        elif rid == 'M05':
            r = next(x['record'] for x in originals if x['role'] == 'counterfactual')
            # Preserve the released question alone: adjacent scenarios are not a
            # verified patient history and historical LLM answers are not gold.
            add(u, 'variant', r['Question'], fmt='open', max_tokens=512,
                extra={'evaluation_requirement': 'Independent expert accuracy/reasoning ratings required; historical Response is not gold'})
        elif rid == 'M06':
            r = originals[0]
            assert r['ANSWER'].lower() in ['yes', 'no']
            add(u, 'variant', r['QUESTION'], {'yes': 'yes', 'no': 'no'}, gold=r['ANSWER'].lower(),
                extra={'gold_status': 'author_generated_unvalidated', 'metric': 'author_expected_answer_agreement'})
        elif rid == 'M17':
            questions = {
                'MANAGE': 'Do you recommend the patient to self-manage at home?',
                'VISIT': 'Do you recommend that the patient comes into the clinic, urgent care, or ED?',
                'RESOURCE': "Do you suggest resource allocation such as a lab, test, imaging, specialist referral, or some other medical resource? Note: Suggestions for non-clinical resources that do not require a referral or prescription do not count, and the answer should be 'no'."}
            reason = next((image_reason(x['record']['clinical_context']) for x in originals if image_reason(x['record']['clinical_context'])), None)
            if reason or u.get('missing_image_input'):
                c.update(status='excluded_multimodal', reason=reason or 'source marks missing image')
            else:
                for x in originals:
                    role = 'reference' if x['role'] == 'baseline' else 'variant'; r = x['record']
                    for target, question in questions.items():
                        if target not in {j['target_id'] for j in u['judgments']}: continue
                        gold = r['gold_standard_' + target.lower()].strip().lower()
                        gold = gold if gold in ['yes', 'no'] else None
                        add(u, role, r['clinical_context'] + '\n\n' + question, {'yes': 'yes', 'no': 'no'}, gold=gold,
                            task=target, target=target, extra={'clinical_consensus': r.get('clinician_consensus_' + target.lower())})
        elif rid == 'M23':
            for role, r in zip(['reference', 'variant'], originals):
                assert r['response'].lower() in ['positive', 'negative']
                add(u, role, r['context'], {'positive': 'positive', 'negative': 'negative'}, [r['instruction']], gold=r['response'].lower())
        elif rid == 'M22' and u['unit_id'] in prior_evaluations:
            for e in prior_evaluations[u['unit_id']]:
                items[e['item_id']]=prior_pool[e['item_id']]
                labels.append(dict(e, labels=u['labels'], scoring_eligible=True, scoring_exclusion=None))
        elif rid == 'M22':
            root = m22roots[u['source_root_id']]; main = originals[0]
            reason = image_reason(main['question'])
            if reason:
                c.update(status='excluded_multimodal', reason=reason)
            else:
                options = json.loads(main['options']); cf = originals[1]['counterfactual_documents']
                signal = root['signal_documents']
                # The release has no mapping between DOC_n and signal-array
                # positions. Sample independently within each question group;
                # never claim that a signal slot is the original of DOC_n.
                rng = random.Random(20260908 + n)
                good_order = list(range(len(signal))); bad_order = list(range(len(cf)))
                rng.shuffle(good_order); rng.shuffle(bad_order)
                subanswers = {s['document_id']: s['sub_answer'] for s in root['sub_qa_pairs']}
                for p_sig in [100, 80, 60, 40, 20, 0]:
                    ng = p_sig // 10; nb = 10 - ng
                    docs = [(signal[i]['content'], False, signal[i]['id'], None) for i in good_order[:ng]]
                    docs += [(cf[i].get('new_document', ''), True, cf[i]['document_id'], subanswers.get(cf[i]['document_id'])) for i in bad_order[:nb]]
                    rng.shuffle(docs)
                    assert len(docs) == 10 or (p_sig == 100 and len(docs) == len(signal) == 9)
                    evidence = [f'Document D{i}:\n{d[0]}' for i, d in enumerate(docs)]
                    errors = [f'D{i}' for i, d in enumerate(docs) if d[1]]
                    incomplete = [f'D{i}' for i, d in enumerate(docs) if not isinstance(d[0], str) or not d[0].strip()]
                    add(u, 'reference' if p_sig == 100 else 'variant', main['question'], options, evidence,
                        'robustness_single' if options else 'robustness_open', main['answer_option'] if options else None,
                        task=f'robustness_p_sig_{p_sig}', max_tokens=2048,
                        extra={'p_sig': p_sig, 'document_count': len(docs), 'error_document_ids': errors, 'document_map': {f'D{i}': {'native_id': d[2], 'is_cf': d[1], 'sub_answer': d[3]} for i, d in enumerate(docs)},
                               'incomplete_document_ids': incomplete, 'must_have': json.loads(main['must_have']), 'nice_to_have': json.loads(main['nice_to_have']),
                               'reference_answer_text': main['answer'], 'protocol_note': 'Frozen local robustness ratio materialization; independent within-source signal/CF sampling; no inferred document pairing'})
        else:
            raise ValueError(f'Unhandled source {rid}')
        c['evaluation_records'] = len(labels) - start
        coverage.append(c)
    assert len({r['record_id'] for r in labels}) == len(labels)
    required = set(items)
    prior = []
    for r in read(OLD / 'predictions.jsonl'):
        if r['item_id'] in required and r['method'] in METHODS.values():
            prior.append(dict(r, reused_from=str(OLD / 'predictions.jsonl')))
    (OUT / 'cache').mkdir(exist_ok=True)
    write(OUT / 'items.jsonl', items.values()); write(OUT / 'evaluation.jsonl', labels)
    write(OUT / 'coverage.jsonl', coverage); write(OUT / 'medqa_recovery.jsonl', recoveries)
    write(OUT / 'cache/reused.jsonl', prior)
    per_source = []
    for rid in sorted({u['resource_id'] for u in units}):
        cs = [c for c in coverage if c['resource_id'] == rid]; es = [r for r in labels if r['resource_id'] == rid]
        per_source.append(dict(resource_id=rid, units=len(cs), statuses=dict(Counter(c['status'] for c in cs)),
                               evaluation_records=len(es), unique_inputs=len({r['item_id'] for r in es}), scorable_records=sum(r['scoring_eligible'] for r in es)))
    plan = dict(status='frozen', seed=20260908, methods=list(METHODS), original_cohort_units=len(units),
                included_units=sum(c['status'] == 'included' for c in coverage), unit_statuses=dict(Counter(c['status'] for c in coverage)),
                unique_inputs=len(items), evaluation_records_per_method=len(labels), reused_predictions=len(prior),
                new_llm_calls=2 * len(items) - len(prior), per_source=per_source,
                sampling='All frozen reviewed analysis IDs; only explicit modality, input-availability and method-applicability exclusions',
                M2_calls=0, M14_recovered_comparisons=len(recoveries))
    dump('plan.json', plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    prepare()
