import datetime, hashlib, json, os, pathlib, re, subprocess, sys, tempfile, traceback, zipfile
import pymupdf
run = pathlib.Path('/home/data3/txy/Documents/Codex/2026-10-03/cf_moa_full_manuscript/anti_defensive_revision')
review = run / 'review'
zip_path = run / 'cf_moa_latex.zip'
canonical = pathlib.Path('/home/data3/txy/docs/paper/latex/main.pdf')
tectonic = '/home/data3/txy/.local/opt/tectonic-0.17.0/tectonic'
receipt_path = review / 'isolated_build_receipt.json'
sha = lambda data: hashlib.sha256(data).hexdigest()
receipt = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status':'running', 'zip_path':str(zip_path), 'canonical_pdf':str(canonical), 'command':f'TECTONIC_BIN={tectonic} bash build.sh', 'python':sys.version, 'pymupdf_version':pymupdf.VersionBind, 'render_dpi':108, 'failures':[]}
def save():
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False)+'\n')
try:
    zip_original = zip_path.read_bytes()
    canonical_original = canonical.read_bytes()
    receipt['zip_sha256'] = sha(zip_original)
    receipt['canonical_pdf_sha256'] = sha(canonical_original)
    receipt['tectonic_version'] = subprocess.check_output([tectonic,'--version'],text=True).strip()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='cf_moa_anti_defensive_isolated_'))
    receipt['isolated_directory'] = str(tmp)
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert len(names)==len(set(names)), 'Duplicate ZIP member'
        assert len(names)==65, f'Expected65members,got{len(names)}'
        assert all(not pathlib.PurePosixPath(n).is_absolute() and '..' not in pathlib.PurePosixPath(n).parts for n in names), 'Unsafe ZIP path'
        assert z.testzip() is None, 'ZIP CRC failure'
        manifest = json.loads(z.read('SOURCE_MANIFEST.json'))['files']
        assert len(manifest)==64, f'Expected64manifestrows,got{len(manifest)}'
        manifest_names = [row['path'] for row in manifest]
        assert len(manifest_names)==len(set(manifest_names)), 'Duplicate manifest row'
        assert set(names)==set(manifest_names)|{'SOURCE_MANIFEST.json'}, 'ZIP/manifest mismatch'
        verified=[]
        for row in manifest:
            data=z.read(row['path'])
            assert len(data)==row['bytes'], f'Size mismatch:{row["path"]}'
            assert sha(data)==row['sha256'], f'Hash mismatch:{row["path"]}'
            verified.append({'path':row['path'], 'bytes':len(data), 'sha256':sha(data)})
        assert z.read('main.pdf')==canonical_original, 'Bundled PDF does not match canonical PDF'
        z.extractall(tmp)
    receipt['manifest_verification']={'status':'passed','member_count':len(names),'manifest_rows':len(manifest),'all64_hashes_and_sizes_validated':True,'bundled_pdf_equals_canonical':True,'files':verified}
    save()
    # Force a real build; remove the PDF bundled for readers from the isolated copy only.
    (tmp/'main.pdf').unlink()
    env=os.environ.copy(); env['TECTONIC_BIN']=tectonic
    log_path=review/'isolated_build.log'
    with log_path.open('w') as log:
        proc=subprocess.run(['bash','build.sh'],cwd=tmp,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=360)
    receipt['build']={'exit_code':proc.returncode,'log_path':str(log_path),'cwd':str(tmp),'command':'bash build.sh','environment_override':{'TECTONIC_BIN':tectonic}}
    assert proc.returncode==0, f'Build exit:{proc.returncode}'
    rebuilt=(tmp/'main.pdf').read_bytes()
    receipt['rebuilt_pdf_sha256']=sha(rebuilt)
    receipt['raw_pdf_bytes_equal']=rebuilt==canonical_original
    a=pymupdf.open(stream=canonical_original,filetype='pdf'); b=pymupdf.open(stream=rebuilt,filetype='pdf')
    assert len(a)==len(b)==19, f'Page counts:{len(a)},{len(b)}'
    page_results=[]
    for i in range(len(a)):
        ta=a[i].get_text(); tb=b[i].get_text()
        pa=a[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),colorspace=pymupdf.csRGB,alpha=False)
        pb=b[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),colorspace=pymupdf.csRGB,alpha=False)
        sizes_equal=(pa.width,pa.height,pa.n)==(pb.width,pb.height,pb.n)
        row={'page':i+1,'text_equal':ta==tb,'text_sha256':sha(ta.encode()),'pixel_geometry_equal':sizes_equal,'pixel_geometry':[pa.width,pa.height,pa.n],'pixels_equal':sizes_equal and pa.samples==pb.samples,'canonical_pixel_sha256':sha(pa.samples),'rebuilt_pixel_sha256':sha(pb.samples)}
        page_results.append(row)
    receipt['pdf_comparison']={'page_count':len(a),'all_text_equal':all(p['text_equal'] for p in page_results),'all_pixels_equal':all(p['pixels_equal'] for p in page_results),'pages':page_results}
    assert receipt['pdf_comparison']['all_text_equal'], 'PDF text mismatch'
    assert receipt['pdf_comparison']['all_pixels_equal'], 'PDF pixel mismatch'
    log=log_path.read_text(errors='replace')
    fatal_patterns={k:bool(re.search(v,log,re.I)) for k,v in {'overfull':'Overfull \\[hv]box','undefined_reference':'(?:undefined references|Reference .* undefined)','undefined_citation':'Citation .* undefined','missing_character':'Missing character'}.items()}
    receipt['log_checks']=fatal_patterns
    assert not any(fatal_patterns.values()), f'Unexpected TeX diagnostics:{fatal_patterns}'
    assert zip_path.read_bytes()==zip_original, 'Input ZIP changed during verification'
    assert canonical.read_bytes()==canonical_original, 'Canonical PDF changed during verification'
    receipt['input_files_unchanged']=True
    receipt['status']='passed'
except Exception as e:
    receipt['status']='failed'
    receipt['failures'].append({'error':str(e),'traceback':traceback.format_exc()})
finally:
    receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print(json.dumps({'status':receipt['status'],'receipt':str(receipt_path),'build':receipt.get('build'),'page_count':receipt.get('pdf_comparison',{}).get('page_count'),'text_equal':receipt.get('pdf_comparison',{}).get('all_text_equal'),'pixels_equal':receipt.get('pdf_comparison',{}).get('all_pixels_equal'),'zip_sha256':receipt.get('zip_sha256'),'canonical_pdf_sha256':receipt.get('canonical_pdf_sha256'),'failures':receipt['failures']},ensure_ascii=False,indent=2))
sys.exit(0 if receipt['status']=='passed' else 1)
