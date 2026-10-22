"""Resolve archived server paths through FILE_MANIFEST without a server checkout.
Set HANDOFF_ONLY=1 to forbid any reads from the original server paths.
This module performs file reads only; no model or scoring imports.
"""
import csv,gzip,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
_manifest=None
def _index():
 global _manifest
 if _manifest is None:
  with (ROOT/'FILE_MANIFEST.csv').open(newline='') as f:
   _manifest={r['original_path']:r for r in csv.DictReader(f) if r['original_path']}
 return _manifest

def resolve(original_path):
 p=Path(original_path)
 if os.environ.get('HANDOFF_ONLY')!='1' and p.is_file():return p
 if not p.is_absolute() and (ROOT/p).is_file():return ROOT/p
 r=_index().get(str(p))
 if not r or not r.get('package_path'):raise FileNotFoundError(f'Not delivered in handoff: {p}')
 if r.get('encoding') not in ['identity','gzip','deduplicated_identity','deduplicated_gzip']:
  raise ValueError(f'Export needs its dedicated decoder: {p}; {r.get("package_path")}')
 return ROOT/r['package_path']

def open_text(original_path,encoding='utf-8'):
 p=resolve(original_path)
 return gzip.open(p,'rt',encoding=encoding) if p.suffix=='.gz' else p.open('r',encoding=encoding)

def open_binary(original_path):
 p=resolve(original_path)
 original_gzip=str(original_path).endswith('.gz')
 return gzip.open(p,'rb') if p.suffix=='.gz' and not original_gzip else p.open('rb')
