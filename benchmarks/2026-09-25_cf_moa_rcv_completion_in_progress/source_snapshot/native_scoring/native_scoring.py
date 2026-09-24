"""Offline native scoring only. Never import this module into model inference."""
import ast
import json
from pathlib import Path
import re
from types import SimpleNamespace

from cf_moa.tools.adopted import sha256

PACK=Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
SCORER=PACK/'scripts/analyze_cf_baseline_screening.py'
CANONICAL=PACK/'results_cf_full_test/canonical_labels.json'
NORMALIZER=PACK/'scripts/prepare_cf_baseline_screening.py'


def load_native_scorer():
    # Execute the unchanged functions without importing historical run-directory
    # state or writers. Exact sources are recorded by source_lock().
    namespace=dict(json=json,re=re)
    for path,names in [(NORMALIZER,{'norm'}),(SCORER,{'parse','score'})]:
        nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
        if {n.name for n in nodes}!=names:
            raise RuntimeError('Frozen native scoring functions are missing')
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
    module=SimpleNamespace(**{k:namespace[k] for k in ('norm','parse','score')})
    canonical={module.norm(s):s for s in json.loads(CANONICAL.read_text())['labels']}
    return module,canonical


def score_proposal(native_item,evaluation,proposal,*,scorer=None):
    scorer,canonical=scorer or load_native_scorer()
    value=proposal['native_proposal'] if proposal else None
    answer=value.get('answer_choice') if isinstance(value,dict) else value
    item=dict(native_item)
    if item['answer_format']=='robustness_single':
        item['answer_format']='single'
    record=dict(raw_response=json.dumps(dict(answer=answer),ensure_ascii=False) if value is not None else '')
    result=scorer.score(record,evaluation,item,canonical)
    result['applicability']=proposal['applicability'] if proposal else 'failed'
    # Keep the unchanged scorer for available native answers and for offline
    # task-label normalization. Absence is not a predicted wrong answer.
    available=value is not None
    result.update(native_available=available,method_score='scored' if available else 'not_scored',
        semantic_result='native_answer_available' if available else 'unavailable')
    if not available:
        result.update(correct=None,semantic_prediction=None,invalid=True)
        if 'unmapped_diagnosis' in result:result['unmapped_diagnosis']=False
    if native_item['answer_format']=='robustness_single':
        errors=value.get('errors') if isinstance(value,dict) else None
        valid=isinstance(errors,list) and all(isinstance(x,dict) and
            isinstance(x.get('document_id'),str) and isinstance(x.get('correction'),str) for x in errors)
        guessed=[x['document_id'] for x in errors] if valid else []
        valid=valid and len(guessed)==len(set(guessed)) and set(guessed)<=set(evaluation['document_map'])
        excluded=set(evaluation['incomplete_document_ids'])
        gold=set(evaluation['error_document_ids'])-excluded
        guess=set(guessed)-excluded if valid else set()
        result['document_detection']=dict(valid=valid,exact=(valid and guess==gold) if available else None,
            tp=len(guess&gold) if available else None,fp=len(guess-gold) if available else None,
            fn=len(gold-guess) if available else None,method_score='scored' if available else 'not_scored',
            correction_semantic_score=None)
    return result


def source_lock():
    return [dict(path=str(p),sha256=sha256(p)) for p in (SCORER,NORMALIZER,CANONICAL)]
