"""Check this public saved-artifact release, without opening original sources."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote,urlsplit

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())

def anchors(path):
    content=path.read_text();found=set(re.findall(r'<a\s+id=["\']([^"\']+)',content,re.I));counts=Counter()
    for h in re.findall(r'^#{1,6}\s+(.+)$',content,re.M):
        slug=re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-')
        found.add(slug+('-'+str(counts[slug]) if counts[slug] else ''));counts[slug]+=1
    return found

def validate(root):
    root=Path(root).resolve();manifest=read(root/'SOURCE_MANIFEST.json');seen=set()
    for row in manifest:
        rel=row['published_path'];p=(root/rel).resolve()
        assert p.is_relative_to(root) and rel not in seen;seen.add(rel)
        assert sha(p)==row['published_sha256'],rel
        assert re.fullmatch('[0-9a-f]{64}',row['source_sha256']),rel
    links=0;cache={}
    for doc in root.rglob('*.md'):
        for raw in re.findall(r'!?\[[^\]\n]+\]\((<[^>]+>|[^)\n]+)\)',doc.read_text()):
            raw=raw.strip().strip('<>');p=urlsplit(raw)
            if p.scheme or raw.startswith('//'):continue
            assert not raw.startswith('/'),(doc,raw)
            dest=(doc.parent/unquote(p.path)).resolve() if p.path else doc
            assert dest.is_relative_to(root.parent) and dest.is_file(),(doc,raw)
            if p.fragment and dest.suffix=='.md':
                if dest not in cache:cache[dest]=anchors(dest)
                assert unquote(p.fragment) in cache[dest],(doc,raw,'missing anchor')
            links+=1
    # The public data verifier has no GPU/scorer/source-path access.
    result=subprocess.run([sys.executable,str(root/'scripts/verify_publication_data.py'),
                           str(root/'data')],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    gpu=read(root/'data/gpu_release_summary.json')
    assert gpu['released_gpus']==[0,1] and gpu['retained_gpus']==[2,3]
    return dict(status='passed',manifest_entries=len(manifest),relative_markdown_links=links,
        public_data_verifier=json.loads(result.stdout),gpu_release_metadata_checked=True,
        new_model_calls=0,native_rescoring_calls=0,local_original_sources_opened=False,
        interpretation='Published-file hashes, saved counts/costs and links only; not independent scientific replication.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    a=parser.parse_args();print(json.dumps(validate(a.root),ensure_ascii=False,indent=2))
