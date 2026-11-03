import hashlib, json, os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = Path('/home/data3/txy')
FULL = WORK / 'Documents/Codex/2026-09-24/cf_moa_rcv_completion_20260924/full_v5'
PYTHON = WORK / 'MedRGAG/.venv/bin/python'
DEP = Path('/home/data4/txy/codex_runs/2026-10-23/cf_moa_publication_gpu/environment/dependencies')

def now(): return datetime.now().astimezone().isoformat()
def rows(p):
    import gzip
    p=Path(p)
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:
        for l in f:
            if l.strip(): yield json.loads(l)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''): h.update(b)
    return h.hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n');t.replace(p)
def write(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp')
    with t.open('w') as f:
        for r in x:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
    t.replace(p)
def environment(gpu='3'):
    e=dict(os.environ); cache=ROOT/'runtime_cache';tmp=Path('/home/data4/txy/fgsup-tmp')
    tmp.mkdir(exist_ok=True,mode=0o700)
    e.update(CUDA_VISIBLE_DEVICES=str(gpu),VLLM_USE_V1='1',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONPATH=str(WORK)+':'+str(DEP),XDG_CACHE_HOME=str(cache),HF_HOME=str(cache/'hf'),VLLM_CACHE_ROOT=str(cache/'vllm'),TORCHINDUCTOR_CACHE_DIR=str(cache/'torchinductor'),TRITON_CACHE_DIR=str(cache/'triton'),CUDA_CACHE_PATH=str(cache/'cuda'),TMPDIR=str(tmp),VLLM_WORKER_MULTIPROC_METHOD='spawn')
    return e
