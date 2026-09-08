"""Expand every acquired target subset. No model calls, no new CF generation.

Uses only existing source files. Full root evidence is stored once; the balanced
analysis sample is selected by the parent collection, never by this script.
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

P = Path(__file__).resolve().parent
RAW = P / 'raw'
COLLECTION = P.parents[1]
NAMES = {'M12': 'FairMedQA/AMQA', 'M14': 'DiversityMedQA', 'M16': 'EquityMedQA',
         'M22': 'MedRGB', 'M23': 'BioRAB', 'M24': 'MedCF', 'M25': 'MedMKEB'}
COUNTS = defaultdict(Counter)
METHODS = defaultdict(Counter)
LABELS = defaultdict(Counter)
ROOT_IDS = defaultdict(set)
PROMPTS = defaultdict(set)
SEEN_IDS = set()
ROOT_SEEN = set()
REVIEWED = {}
for line in (P / 'frozen_item_reviews.jsonl').open():
    row = json.loads(line)
    if row['resource_id'] in NAMES:
        REVIEWED[row['unit_id']] = row


def load(name):
    return json.loads((RAW / name).read_text())


def jsonlines(name):
    with (RAW / name).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def sheet(n):
    rows = load(f'M16/sheet_{n}.json')['rows']
    headers = {re.sub(r'\d', '', k): v for k, v in rows[0].items()}
    return [{headers[re.sub(r'\d', '', k)]: v for k, v in r.items()} for r in rows[1:]]


def source(rid, path, locator, url=None, revision=None):
    if url is None:
        metadata = load(rid + '_github.json')
        revision = metadata['tree']['sha']
        url = f"https://github.com/{metadata['repo']}/blob/{revision}/{path.split('/', 1)[1]}"
    return {'url': url, 'file': str(RAW / path), 'revision': revision, 'locator': locator}


def ev(quote, where):
    return {'quote': quote, 'source_locator': where}


def root(rid, rootid, src, records, projection=None):
    key = rid + ':' + rootid
    if key not in ROOT_SEEN:
        ROOT_SEEN.add(key)
        record = dict(source_root_id=rootid, resource_id=rid, source=src, original_records=records)
        if projection:
            record['projection'] = projection
        ROOT_OUT.write(json.dumps(record, ensure_ascii=False) + '\n')
    return {'file': str(P / 'full_root_records.jsonl'), 'resource_id': rid, 'source_root_id': rootid}


def reviewed_judgment(uid):
    old = REVIEWED.get(uid)
    if old is None:
        return None
    return dict(judgment_id=uid, target=old['target'], labels=old['labels'],
                rationale=old['rationale'], evidence=old['evidence'],
                cannot_infer=old['cannot_infer'], status=old['status'],
                annotation_method='item_reviewed', rule_id='PRESERVED_ITEM_REVIEW_20260908',
                clinical_review=False)


def unit(rid, sid, src, rootid, records, kind, change, target, labels, rationale,
         evidence, cannot, task, rule, **extra):
    uid = rid + ':' + sid
    item = dict(unit_id=uid, resource_id=rid, benchmark=NAMES[rid], source_unit_id=sid,
                source_root_id=rootid, source=src, original_records=records, unit_kind=kind,
                change=change, target=target, labels=labels, rationale=rationale,
                evidence=evidence, cannot_infer=cannot, original_task=task,
                status='labeled' if labels else 'uncertain', clinical_review=False,
                annotation_method='rule_grounded' if labels else 'pending', rule_id=rule,
                evaluation_role='evaluation', runnable_text=True, **extra)
    if uid in REVIEWED:
        old = REVIEWED[uid]
        for k in ['target', 'labels', 'rationale', 'evidence', 'cannot_infer', 'status']:
            item[k] = old[k]
        for k in ['judgments', 'quality_flags', 'other_judgments', 'missing_inputs', 'runnable_text']:
            if k in old:
                item[k] = old[k]
        item['annotation_method'] = 'item_reviewed'
        item['rule_id'] = 'PRESERVED_ITEM_REVIEW_20260908'
        item['preserved_review_source'] = str(P / 'frozen_item_reviews.jsonl')
    return item


def emit(item):
    uid = item['unit_id']; rid = item['resource_id']
    assert uid not in SEEN_IDS, uid
    assert Path(item['source']['file']).is_file()
    assert not item['labels'] or (item['rationale'] and item['evidence'])
    SEEN_IDS.add(uid)
    ROOT_IDS[rid].add(item['source_root_id'])
    COUNTS[rid]['comparison_units'] += 1
    COUNTS[rid][item['status']] += 1
    COUNTS[rid]['split:' + item.get('split', 'unspecified')] += 1
    METHODS[rid][item['annotation_method']] += 1
    LABELS[rid].update(item['labels'])
    OUT.write(json.dumps(item, ensure_ascii=False) + '\n')


def reference(rid, sid, reason, src, records):
    COUNTS[rid]['excluded_reference_rows'] += 1
    REF_OUT.write(json.dumps(dict(resource_id=rid, source_unit_id=sid, source=src,
                                 reason=reason, original_records=records), ensure_ascii=False) + '\n')


def question_target(text):
    parts = re.findall(r'[^.!?]*\?', text)
    return parts[-1].strip() if parts else text[-450:]


def normalize_gender(text):
    replacements = {'man': 'person', 'woman': 'person', 'men': 'people', 'women': 'people',
                    'male': 'person_sex', 'female': 'person_sex', 'boy': 'child', 'girl': 'child',
                    'he': 'they', 'she': 'they', 'his': 'their', 'her': 'their', 'him': 'them',
                    'wife': 'spouse', 'husband': 'spouse', 'father': 'parent', 'mother': 'parent'}
    return re.sub(r'\b(' + '|'.join(replacements) + r')\b', lambda m: replacements[m[0]], text.lower()).rstrip(' ?.')


def normalize_race(text):
    return re.sub(r'\b(black|white|african|asian|caucasian|hispanic|latino|latina)\b',
                  'racial_identifier', text.lower())


RISK_TERMS = re.compile(r'pregnan|gestation|breastf|breast.fed|breast milk|uter|ovari|prostat|testic|penis|vagina|menstr|sex.link|x.link|y.chrom|hemophil|muscular dystrophy|prevalen|incidence|risk factor', re.I)
MECHANISM_TARGET = re.compile(r'\b(mechanism|embryolog|structure|enzyme|mediator|innervat|nerve|pathophysiolog|receptor|molecular|derived|origin|produces|sequela|function)\w*', re.I)


with (P / 'full_units.jsonl').open('w') as OUT, (P / 'full_root_records.jsonl').open('w') as ROOT_OUT, (P / 'full_references.jsonl').open('w') as REF_OUT:
    # Every fixed AMQA adversarial variant; no rule treats all attacks as R5.
    for i, r in enumerate(jsonlines('M12/AMQA_Dataset/AMQA_Dataset.jsonl')):
        rid = 'M12'; rootid = str(r['question_id'])
        src = source(rid, 'M12/AMQA_Dataset/AMQA_Dataset.jsonl', f'JSONL line {i+1}')
        ref = root(rid, rootid, src, [r])
        COUNTS[rid]['declared_source_rows'] += 1
        for variant in ['white', 'black', 'high_income', 'low_income', 'male', 'female']:
            key = 'adv_question_' + variant; sid = rootid + ':' + variant
            srcv = dict(src, locator=f'JSONL line {i+1}; original_question / {key}')
            records = [{k: r[k] for k in ['question_id', 'original_question', 'desensitized_question', 'options', 'answer', 'answer_idx', 'adv_description_'+variant, key]}]
            COUNTS[rid]['declared_variant_rows'] += 1
            if r['original_question'] == r[key]:
                reference(rid, sid, 'no textual condition change', srcv, records)
                continue
            PROMPTS[rid].update([r['original_question'], r[key]])
            item = unit(rid, sid, srcv, rootid, records, 'official_pair',
                        f'原题 → 官方{variant}固定攻击变体；新增叙述：{r["adv_description_"+variant]}',
                        question_target(r['original_question']), [],
                        '已逐行定位作者固定原题/变体与变化叙述；该构造常同时加入临床线索，未逐项审定新增内容对当前医学判断的作用，不由作者统一答案或攻击结果自动赋R5。',
                        [ev(r['adv_description_'+variant], srcv['locator'])],
                        '未写条件不等于明确不存在；原有模型预测、attack_result和统一答案不用于定类。',
                        '原生MedQA选择题与固定对抗背景；保留原答案及公平性指标，不运行攻击。',
                        'AMQA_FIXED_ATTACK_PENDING_RELATION', root_record_ref=ref, split='released_evaluation', input_record_count=2)
            emit(item)

    # Every official Diversity variant; exact no-op rows are references.
    dhf = load('M14_official_hf.json'); diversity_roots = {}
    for filename in ['GenderDataset.csv', 'EthnicityDataset.csv']:
        with (RAW/'M14/official'/filename).open() as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                rid = 'M14'; q = r['Question']; is_gender = filename.startswith('Gender')
                rootid = diversity_roots.setdefault(q, f'exact_source_text:{len(diversity_roots)}')
                src = source(rid, 'M14/official/'+filename, f'CSV data row {i+1}',
                             f"https://huggingface.co/datasets/{dhf['id']}/blob/{dhf['sha']}/{filename}", dhf['sha'])
                ref = root(rid, rootid, src, [r])
                COUNTS[rid]['declared_source_rows'] += 1
                keys = [k for k in r if k not in ['', 'Question', 'Row Number']]
                for j, key in enumerate(keys):
                    oldsid = f'{filename}:row{i+1}:source{r["Row Number"]}'
                    sid = oldsid if j == 0 else oldsid + ':' + ['african', 'caucasian', 'asian', 'hispanic', 'native_american'][j]
                    srcv = dict(src, locator=src['locator']+'; Question / '+key)
                    pair = [{k: r[k] for k in ['', 'Question', 'Row Number', key]}]
                    COUNTS[rid]['declared_variant_rows'] += 1
                    if q == r[key]:
                        reference(rid, sid, '两端逐字相同，不是CF变化', srcv, pair)
                        continue
                    exact_control = normalize_gender(q) == normalize_gender(r[key]) if is_gender else r[key] == key.removesuffix(' Question') + ' ' + q
                    target = question_target(q)
                    labelable = bool(exact_control and not RISK_TERMS.search(q) and MECHANISM_TARGET.search(target) and not re.search(r'image|shown|figure|photograph|x-ray', q, re.I))
                    labels = ['R5'] if labelable else []
                    PROMPTS[rid].update([q, r[key]])
                    item = unit(rid, sid, srcv, rootid, pair, 'official_pair',
                                '原Question → '+key+'；仅在文本规则满足时初标机制/结构问题的保持。', target, labels,
                                ('该行满足原作者不影响诊断筛选、原题与变体临床文字严格一致（仅受控身份词/前缀不同）、目标明确问机制/结构且未命中性别相关或缺图条件，因此初标当前机制目标保持；这不是临床专家逐题验收。' if labels else
                                 '完整原题及该官方属性变体已收；临床目标可能涉及诊断/处置、性别关联、图像或超出严格文字替换，当前证据不足以自动判定其功能。'),
                                [ev('impact factor of 1 (no change)', 'M14/official/README.md'), ev(target, srcv['locator']), ev(r[key], srcv['locator'])],
                                '未提供原生选项/金标；不能把所有人口属性都视为无关，也不按模型答案保持与否定类。',
                                '原作者MedQA人口属性公平性任务；原生选项/金标缺失，不能直接计准确率。',
                                'DIVERSITY_EXACT_ATTRIBUTE_MECHANISM_SCOPE' if labels else 'DIVERSITY_PENDING_CLINICAL_RELATION',
                                root_record_ref=ref, split='author_test' if i < 500 else 'author_train', input_record_count=2)
                    item['runnable_text'] = False
                    item['evaluation_role'] = 'evaluation' if i < 500 else 'research_training_split'
                    emit(item)

    # All 323 official Equity pairs, retaining ideal-answer assessor disagreement.
    ideal = defaultdict(list)
    for r in sheet(4):
        ideal[r['question_1_id'], r['question_2_id']].append({k: r[k] for k in ['rater_id', 'rater_type', 'ideal_answers_diff']})
    for sn, split in [(11, 'CC-Manual'), (12, 'CC-LLM')]:
        for i, r in enumerate(sheet(sn)):
            rid = 'M16'; ids = [r['question_1_id'], r['question_2_id']]; sid = ':'.join(ids)
            src = source(rid, f'M16/sheet_{sn}.json', f'{split}!row{i+2}',
                         'https://arxiv.org/src/2403.12025v2/anc/equitymedqa_ratings.xlsx', 'arXiv:2403.12025v2')
            COUNTS[rid]['declared_pairs'] += 1
            if r['question_1_text'] == r['question_2_text']:
                reference(rid, sid, 'no textual condition change', src, [r]); continue
            rr = ideal[tuple(ids)]; votes = Counter(v['ideal_answers_diff'] for v in rr)
            q1, q2 = r['question_1_text'], r['question_2_text']
            race_only = q1 != q2 and normalize_race(q1) == normalize_race(q2)
            same_target_scope = re.search(r'eGFR|lung capacity', q1)
            labels = ['R5'] if rr and set(votes) == {'ideal_answers_same'} and race_only and same_target_scope else []
            rootid = split+':'+sid
            PROMPTS[rid].update([q1, q2])
            item = unit(rid, sid, src, rootid, [r], 'official_pair', q1+' → '+q2,
                        '这两个具体医学问题的理想回答内容', labels,
                        ('所有已发表评定均为ideal_answers_same，且此条严格仅种族词替换，当前对象限定为eGFR/肺容量计算；不依据模型回答相似性。' if labels else
                         '完整官方对与ideal评定已保留。评定为应不同、存在分歧/未评定，或变化超出严格种族计算问题；暂不推断新增/撤销哪条支持。'),
                        [ev(json.dumps(dict(votes)), 'equitymedqa_ratings.xlsx:Counterfactual Paired ratings; exact IDs '+sid), ev(q2, src['locator'])],
                        '应不同不是R1/R2/R3的充分依据；身份背景不自动R5；删除共病/妊娠提及不是明确取消。',
                        '开放医学问答与原反事实公平性rubric，保留原研究ideal-answer评定而不据模型表现定类。',
                        'EQUITY_UNANIMOUS_IDEAL_RACE_CALCULATION' if labels else 'EQUITY_PENDING_RELATION',
                        source_question_ids=ids, original_ideal_answer_assessments=rr, split=split, input_record_count=2)
            emit(item)

    # MedRGB: one official source-question CF group, all ten document slots.
    mhf = load('M22_hf.json')
    for path in sorted((RAW/'M22/data').glob('*.parquet')):
        rownum = 0
        for batch in pq.ParquetFile(path).iter_batches(batch_size=32):
            for r in batch.to_pylist():
                rid = 'M22'; rootid = r['question_id']; cf = json.loads(r['counterfactual_documents']); subqa = json.loads(r['sub_qa_pairs'])
                src = source(rid, 'M22/data/'+path.name, f'parquet row {rownum}; question_id={rootid}',
                             f"https://huggingface.co/datasets/{mhf['id']}/blob/{mhf['sha']}/data/{path.name}", mhf['sha'])
                rownum += 1; COUNTS[rid]['declared_source_rows'] += 1
                main = {k: r[k] for k in ['question_id', 'question', 'options', 'answer', 'answer_option', 'must_have', 'nice_to_have']}
                roots = dict(main, signal_documents=json.loads(r['signal_documents']), sub_qa_pairs=subqa)
                ref = root(rid, rootid, src, [roots], '原生Robustness所需主问/金标/清洁文档/子问；非CF的noise_documents留在原parquet，未改写。DOC_n不擅自映射signal_documents数组位置。')
                valid_cf = []; judgments = []; flags = []
                smap = {x['document_id']: x for x in subqa}
                for edited in cf:
                    docid = edited.get('document_id', '')
                    COUNTS[rid]['raw_counterfactual_field_entries'] += 1
                    if docid == 'options':
                        reference(rid, rootid+':options', '转换产生的options元数据占位，不是CF文档', src, [edited]); continue
                    valid_cf.append(edited)
                    COUNTS[rid]['cf_document_slots'] += 1
                    clean = smap.get(docid)
                    complete = bool(edited.get('new_document') and edited.get('new_answer') and edited.get('question'))
                    labels = ['R5'] if complete and clean and clean.get('sub_question') == edited['question'] and clean.get('sub_answer') != edited['new_answer'] else []
                    COUNTS[rid]['complete_cf_documents' if complete else 'incomplete_cf_documents'] += 1
                    juid = rid+':'+rootid+':'+docid
                    judgment = reviewed_judgment(juid) or dict(judgment_id=juid, target=r['question'], labels=labels,
                        status='labeled' if labels else 'uncertain', annotation_method='rule_grounded' if labels else 'pending',
                        rule_id='MEDRGB_MATCHED_WRONG_EVIDENCE_PRESERVES_MAIN' if labels else 'MEDRGB_PENDING_INCOMPLETE_OR_ALIGNMENT',
                        rationale=('同一DOC标识的子问严格匹配、错误子答案实际替换且错误文档非空；作者Robustness要求纠正错误证据，因此当前主问原生正确标准保持。' if labels else
                                   'CF字段缺失、子问不匹配或新旧子答案相同；未把这一文档自动标保持，完整记录仍保留。'),
                        evidence=[ev(edited.get('new_answer', ''), src['locator']+':'+docid), ev('detect which documents are factually incorrect and provide corrected answers', 'M22/README.md:Robustness')],
                        clinical_review=False)
                    judgments.append(judgment)
                    if not complete: flags.append(docid+':incomplete_cf_fields')
                group_labels = sorted({label for j in judgments for label in j['labels']})
                PROMPTS[rid].add(r['question'])
                item = unit(rid, rootid+':cf_group', src, rootid, [main, {'counterfactual_documents': valid_cf}],
                            'official_cf_document_group', '同一原问的官方错误证据集合；逐DOC保留原始改写，不生成污染比例或新的混合提示。',
                            r['question'], group_labels,
                            '组内标签为具体DOC判断的并集；清洁证据由root_record_ref恢复，全部官方DOC保留。存在坏条目时对子判断暂缓，不宣称整组每个编辑均验收。',
                            [ev('Robustness', 'M22/README.md'), ev(rootid, src['locator'])],
                            '不能把错误文档当假设金标；3680组不等于36800独立医学源题；未发布具体污染mask时不编造完整实验提示对。',
                            '原生主问/长答rubric、错误证据检测与纠正；保留官方证据集合和文档级子判断。',
                            'MEDRGB_OFFICIAL_ROOT_CF_GROUP', root_record_ref=ref, judgments=judgments, quality_flags=flags,
                            split=path.stem.split('-')[0], cf_document_count=len(valid_cf), input_record_count=None,
                            native_input_count_note='一组原问及官方CF文档集合；未物化各污染比例提示，不能等同独立模型输入数。')
                emit(item)

    # Every provided BioNLI corruption input, paired by exact target context and
    # native reference label; repeated targets are retained with explicit counts.
    clean = list(jsonlines('M23/BioNELL_test_instruction_medcpt.json'))
    contexts = {}; occurrence = defaultdict(int)
    for i, a in enumerate(clean):
        rootid = contexts.setdefault(a['context'], f'BioNLI:exact_context:{len(contexts)}')
        root('M23', rootid, source('M23', 'M23/BioNELL_test_instruction_medcpt.json', f'JSONL row {i+1}',
             'https://drive.google.com/file/d/11sFEdlmtOvXDYFr5a3wZGXabcsc76qXH/view', 'public Drive; retrieved 2026-09-08'),
             [{'context': a['context'], 'response': a['response'], 'category': a['category']}])
    for strength, fileid in [('20', '1KyuTpMbibMa9C5ngtf1KwwFgFxqv1N16'), ('100', '1RBxo33TXaHqOdOyemLU8Clc-4QnwDUqE')]:
        data = list(jsonlines(f'M23/BioNELL_test_instruction_medcpt_noise_{strength}.json'))
        assert len(clean) == len(data) == 6308
        for i, (a, b) in enumerate(zip(clean, data)):
            assert a['context'] == b['context'] and a['response'] == b['response'], (strength, i)
            rid = 'M23'; sid = f'BioNLI:noise{strength}:row{i}'; rootid = contexts[a['context']]
            src = source(rid, f'M23/BioNELL_test_instruction_medcpt_noise_{strength}.json', f'JSONL row {i+1}; matched exact target to clean row {i+1}',
                         'https://drive.google.com/file/d/'+fileid+'/view', 'public Drive; retrieved 2026-09-08')
            COUNTS[rid]['declared_corruption_pairs'] += 1
            if a['instruction'] == b['instruction']:
                reference(rid, sid, '目标与检索演示全文都相同，没有实际CF输入变化', src, [a, b]); continue
            occurrence[rootid] += 1
            PROMPTS[rid].add(a['context'])
            item = unit(rid, sid, src, rootid, [a, b], 'official_wrong_label_demonstration_pair',
                        f'官方clean检索演示 → noise{strength}错误标签语料下的固定检索演示；目标文本严格保持。',
                        a['context'], ['R5'],
                        '逐行检查固定两端target context/reference一致而instruction实际改变；作者错误标签构造与CR任务要求目标判断抵抗演示污染。标签基于任务作用对象，不基于模型输出。',
                        [ev('n["response"]=wrong_type', 'M23/data_progress.py'), ev(a['response'], 'BioNELL_test_instruction_medcpt.json:row'+str(i+1)), ev(b['instruction'][-350:], src['locator'])],
                        '污染比例属于语料构造；noise20单条检索到的示例不保证一定是被翻转的那条，不声称每个变体都有100%错误示例。重复目标不当独立病例。',
                        'BioNLI positive/negative及原生指标，clean/污染语料固定对照；不是患者干预。',
                        'BIORAB_TARGET_UNCHANGED_UNDER_OFFICIAL_CORRUPTION',
                        split='BioNLI_test_noise'+strength, input_record_count=2, target_occurrence=occurrence[rootid])
            emit(item)
        COUNTS['M23']['declared_rows:noise'+strength] = len(data)
    COUNTS['M23']['clean_rows'] = len(clean)
    COUNTS['M23']['unique_clean_contexts'] = len(contexts)
    COUNTS['M23']['duplicate_target_rows_per_strength'] = len(clean)-len(contexts)

    # All MedCF splits in the archive, while only test is an evaluation split.
    for split in ['train', 'valid', 'test']:
        for i, r in enumerate(load(f'M24/MedCF/{split}.json')):
            rid = 'M24'; sid = f'{split}:{i}'; src = source(rid, f'M24/MedCF/{split}.json', f'array[{i}]')
            COUNTS[rid]['declared_edit_roots'] += 1
            if r['target_new'] == r['ground_truth']:
                reference(rid, sid, '编辑目标与原值相同，没有事实替换', src, [r]); continue
            judgments = []; flags = []
            for loc in ['target', 'mapping', 'struc', 'tokenSem']:
                pk, ak = f'locality_{loc}_prompt', f'locality_{loc}_ground_truth'
                valid = bool(r.get(pk) and r.get(ak) and r[pk] not in [r['prompt'], r['rephrase_prompt']])
                juid = rid+':'+sid+':locality_'+loc
                j = reviewed_judgment(juid) or dict(judgment_id=juid, target=r.get(pk), labels=['R5'] if valid else [],
                    rationale='作者locality构造明确要求无关知识保持，且本行目标问题非空、与主编辑/重述不同，原locality参考保留。' if valid else 'locality缺字段或与主编辑问题完全相同，不自动赋保持。',
                    evidence=[ev(str(r.get(pk, '')), src['locator']+':'+pk), ev(str(r.get(ak, '')), src['locator']+':'+ak)],
                    status='labeled' if valid else 'uncertain', annotation_method='rule_grounded' if valid else 'pending',
                    rule_id='MEDCF_DISTINCT_LOCALITY_TARGET' if valid else 'MEDCF_AMBIGUOUS_LOCALITY', clinical_review=False)
                judgments.append(j)
                if not valid: flags.append('ambiguous_locality_'+loc)
            for field in ['prompt', 'rephrase_prompt']:
                judgments.append(dict(judgment_id=rid+':'+sid+':'+field, target=r[field], labels=[], status='uncertain',
                    annotation_method='pending', rule_id='KNOWLEDGE_RESTATEMENT_NOT_AUTOMATIC_R4',
                    rationale='原生主编辑/重述保留，不因为知识编辑自动匹配五类或推导后果。', evidence=[ev(r[field], src['locator']+':'+field)], clinical_review=False))
            labs = sorted({x for j in judgments for x in j['labels']})
            item = unit(rid, sid, src, sid, [r], 'knowledge_edit_root',
                        r['prompt']+'：'+r['ground_truth']+' → '+r['target_new'],
                        '编辑根及其原生重述、四类locality子任务', labs,
                        '一个编辑根只计一次；标签由有依据的独立locality判断合并，主编辑与重述另保留未定类。',
                        [ev('assess the impact of model editing on unrelated knowledge', 'https://arxiv.org/html/2402.18099v3:Locality Data Construction'), ev(r['prompt'], src['locator'])],
                        '训练/valid记录用于资源归档与标注研究，不能冒充测试规模；缺少具体医学关系时不补R1–R4。',
                        '执行单项知识编辑后分别测Efficacy/Generality/Locality token matching；不能直接视为文本RAG问题。',
                        'MEDCF_EDIT_ROOT_WITH_LOCALITY_JUDGMENTS', split=split, judgments=judgments, quality_flags=flags, input_record_count=None)
            item['runnable_text'] = False
            item['evaluation_role'] = 'evaluation' if split == 'test' else 'research_training_split'
            PROMPTS[rid].add(r['prompt'])
            emit(item)

    # All MedMKEB evaluation edit roots. Train/attack arrays remain raw archives.
    for i, r in enumerate(load('M25/data/eval_data_threehop_final.json')):
        rid = 'M25'; sid = f'eval:{r["id"]}'; src = source(rid, 'M25/data/eval_data_threehop_final.json', f'array[{i}] id={r["id"]}')
        COUNTS[rid]['declared_eval_edit_roots'] += 1
        if r['pred'] == r['alt']:
            reference(rid, sid, 'pred与alt相同，没有事实替换', src, [r]); continue
        judgments = []; labels = set()
        if r.get('loc') and r.get('loc_ans') and r['loc'] not in [r['src'], r['rephrase']]:
            labels.add('R5')
            judgments.append(dict(judgment_id=rid+':'+sid+':text_locality', target=r['loc'], labels=['R5'],
                status='labeled', annotation_method='rule_grounded', rule_id='MEDMKEB_DISTINCT_TEXT_LOCALITY',
                rationale='该文字locality为编辑对象之外的不同问题；按作者locality协议保持。',
                evidence=[ev(r['loc'], src['locator']+':loc'), ev(r['loc_ans'], src['locator']+':loc_ans')], clinical_review=False))
        for pi, port in enumerate(r.get('port_new', [])):
            q = port.get('Q&A', {}); triple = port.get('triple2', {})
            direct = (port.get('port_type') == '1-hop' and triple.get('entity1') == r['alt']
                      and triple.get('relation') in ['Complication', 'Side effect']
                      and q.get('Answer') == triple.get('entity2')
                      and re.search(r'complication|side effect|consequence|outcome', q.get('Question', ''), re.I)
                      and q.get('Answer', '').lower() not in r['alt'].lower())
            # Inspection found e.g. "spiculated masses -> malignant breast
            # cancer" called Complication: a source field alone can encode a
            # diagnostic association, so retain new R4 candidates for review.
            pl = []
            labels.update(pl)
            judgments.append(dict(judgment_id=rid+':'+sid+':port'+str(pi), target=q.get('Question'), labels=pl,
                status='labeled' if pl else 'uncertain', annotation_method='rule_grounded' if pl else 'pending',
                rule_id='MEDMKEB_DIRECT_COMPLICATION_CANDIDATE' if direct else 'MEDMKEB_OTHER_PORTABILITY_PENDING',
                candidate_labels=['R4'] if direct else [],
                rationale='作者记录满足直接Complication/Side effect形式，但抽查发现同名关系可实际表示诊断线索；保留R4候选，需核对这条真实医学关系。' if direct else '保留原生portability，位置/名称重述或未审定多跳链不自动归R4。',
                evidence=[ev(json.dumps(port, ensure_ascii=False), src['locator']+':port_new['+str(pi)+']')], clinical_review=False))
        item = unit(rid, sid, src, sid, [r], 'multimodal_edit_metadata',
                    r['pred']+' → '+r['alt'], '该编辑根的独立locality与具体portability子判断', sorted(labels),
                    '逐行依原生独立文字locality及严格直接并发关系初标；未取得图像，不声称完成影像病例验收。',
                    [ev(r['loc'], src['locator']+':loc'), ev(r['alt'], src['locator']+':alt')],
                    '图片缺失，不能运行纯文本替代版；2497 eval外的train4490/attack721不充作额外独立测试根。',
                    '原生多模态知识编辑与reliability/generality/locality/portability评分；保留图像路径和全部子任务。',
                    'MEDMKEB_EVAL_ROOT_JUDGMENTS', split='eval', judgments=judgments,
                    missing_inputs=[r['image'], r['image_rephrase'], r['m_loc']], input_record_count=None)
        item['runnable_text'] = False
        item['collection_kind'] = 'multimodal_edit_metadata_images_missing'
        PROMPTS[rid].add(r['src'])
        emit(item)

summary = {'schema_version': 'medical-cf-full-20260908', 'comparison_units': len(SEEN_IDS),
           'by_resource': {}, 'annotation_note': 'item_reviewed为保留的逐题代理复核，非临床专家验收；rule_grounded为文本与官方规则逐行初标；pending未强行定类。',
           'pilot_review_source': str(P/'frozen_item_reviews.jsonl'),
           'root_records_file': str(P/'full_root_records.jsonl'), 'references_file': str(P/'full_references.jsonl'),
           'counting_note': 'MedRGB按3680原问CF组计数；组内实际DOC单列。MedCF完整归档split，测试仅test。变体/重复target不等于独立病例。'}
for rid in NAMES:
    summary['by_resource'][rid] = dict(COUNTS[rid], source_roots=len(ROOT_IDS[rid]),
                                      unique_target_or_view_texts=len(PROMPTS[rid]),
                                      annotation_methods=dict(METHODS[rid]), labels=dict(LABELS[rid]))
summary['by_resource']['M16'].update(source_roots=None, official_pair_index_entries=323,
    unique_question_ids=145, manual_question_ids=45, llm_question_ids=100,
    seed_templates={'CC-Manual': 8, 'CC-LLM': 20, 'llm_includes_manual_templates': True},
    root_count_note='开放问答没有独立患者根；source_root_id用于定位官方比较对，不能当323独立病例。')
summary['by_resource']['M22'].update(root_count_note='3680官方question IDs，3595不同问句；相同问句的证据集合可不同，不擅自合并。')
summary['by_resource']['M23'].update(unique_visible_pairs=11125, duplicate_visible_pair_records=1490,
    unique_visible_input_records=16688, conflicting_gold_for_identical_contexts=0,
    unique_pairs_by_strength={'noise20': 5562, 'noise100': 5563},
    root_count_note='5563不同目标上下文；保留作者重复发布行，但重复行不能当独立医学来源。')
summary['by_resource']['M24'].update(declared_split_rows={'train': 2408, 'valid': 818, 'test': 802},
    noop_edits_by_split={'train': 9, 'valid': 2, 'test': 4},
    identical_edit_overlap_across_splits=0,
    root_count_note='4013真实替换根+15无变化参照=4028原记录；主评测仅test的798真实CF根。')
summary['by_resource']['M25'].update(unique_original_images=2497,
    root_count_note='2497原图/编辑根，140种问题文本模板；没有因共享模板合并不同图像。新Complication字段只列R4候选，保留此前3个逐项复核R4。')
(P/'full_counts.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps(summary, ensure_ascii=False, indent=2))
