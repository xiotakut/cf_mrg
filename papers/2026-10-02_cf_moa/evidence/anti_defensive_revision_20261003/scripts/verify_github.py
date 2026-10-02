from pathlib import Path
import subprocess,json,hashlib,base64,concurrent.futures
repo=Path('/home/data3/txy/Documents/Codex/2026-10-02/cf_moa_paper_github');ev=Path('/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript/anti_defensive_revision');pkg=repo/'papers/2026-10-02_cf_moa'
def gh(path):return json.loads(subprocess.check_output(['gh','api',path],cwd=repo))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();info=gh('repos/xiotakut/cf_mrg');ref=gh('repos/xiotakut/cf_mrg/git/ref/heads/main');assert info['private'] and ref['object']['sha']==head
tr=gh(f'repos/xiotakut/cf_mrg/git/trees/{head}?recursive=1');assert not tr['truncated'];tree={x['path']:x for x in tr['tree'] if x['type']=='blob'}
m=json.loads((pkg/'DELIVERY_MANIFEST.json').read_text());checked=[]
for row in m['files']:
 f=pkg/row['path'];data=f.read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];checked.append(f)
checked.extend([pkg/'DELIVERY_MANIFEST.json',repo/'README.md'])
for f in checked:
 data=f.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert tree[str(f.relative_to(repo))]['sha']==blob,str(f)
files=['latex/main.tex','manuscript.pdf','cf_moa_latex.zip','latex/references.bib','latex/figures/cf_moa_architecture.pdf','PUBLICATION.json']
def get(rel):
 f=pkg/rel;row=tree[str(f.relative_to(repo))];b=gh('repos/xiotakut/cf_mrg/git/blobs/'+row['sha']);data=base64.b64decode(b['content']);assert data==f.read_bytes();return {'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:downloads=list(ex.map(get,files))
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
r={'status':'passed','repository':'xiotakut/cf_mrg','private':info['private'],'remote_main':head,'package_files':len(checked)-1,'checked_git_blobs':len(checked),'manifest_entries':len(m['files']),'downloaded_byte_checks':downloads,'working_tree_clean':True,'current_main_pdf_sha256':hashlib.sha256((pkg/'manuscript.pdf').read_bytes()).hexdigest()}
(ev/'review/github_verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
