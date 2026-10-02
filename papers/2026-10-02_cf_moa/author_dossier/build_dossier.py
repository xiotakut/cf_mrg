#!/usr/bin/env python3
"""Export the collaborative Chinese Markdown dossier through Pandoc to LaTeX/PDF.

This is a reading edition, not the native LaTeX English conference manuscript.
Requires Python 3, Pandoc, Tectonic, and installed Unicode/CJK fonts. Example:
  python3 build_dossier.py --input docs/paper/research_dossier.md \
      --output docs/paper/latex/research_dossier.tex
The .tex, .pdf, Pandoc filter/header, logs, and build receipt share the output stem.
Tool/font locations can be overridden; no third-party Python packages are needed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit

HEADER = r"""% Author research dossier; generated reading edition from Markdown.
\usepackage{etoolbox}
\usepackage{xurl}
\usepackage{fvextra}
\usepackage{fancyhdr}
\usepackage{needspace}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}
\setlength{\tabcolsep}{3.5pt}
\renewcommand{\arraystretch}{1.2}
\AtBeginEnvironment{longtable}{\footnotesize\sloppy}
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{breaklines=true,breakanywhere=true,fontsize=\small}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\},breaklines=true,breakanywhere=true,fontsize=\small}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small CF-MoA / 作者研究底稿}
\fancyhead[R]{\small Markdown 阅读版}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}
\renewcommand{\headrulewidth}{0.3pt}
\pretocmd{\section}{\Needspace{5\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{4\baselineskip}}{}{}
\AtBeginDocument{\let\originaltableofcontents\tableofcontents
  \renewcommand{\tableofcontents}{\clearpage\originaltableofcontents\clearpage}}
"""
FILTER = r"""-- Pandoc AST presentation filter; Markdown parsing stays with Pandoc.
local function rooted_url_path(path)
  local parts={}
  for part in path:gmatch('[^/]+') do
    if part == '..' then
      if #parts > 0 then table.remove(parts) end
    elseif part ~= '.' then table.insert(parts,part) end
  end
  return '/'..table.concat(parts,'/')
end
function Pandoc(doc)
  if #doc.blocks > 0 and doc.blocks[1].t == 'Header' and doc.blocks[1].level == 1 then
    if not doc.meta.title then doc.meta.title = pandoc.MetaInlines(doc.blocks[1].content) end
    doc.blocks:remove(1)
    doc = doc:walk({Header=function(h) h.level=math.max(1,h.level-1); return h end})
  end
  local basedir=pandoc.utils.stringify(doc.meta['dossier-source-dir'] or '')
  local baseurl=pandoc.utils.stringify(doc.meta['dossier-link-base-url'] or '')
  if basedir ~= '' then
    doc=doc:walk({Link=function(link)
      if not link.target:match('^[/#]') and not link.target:match('^[%a][%w+%.%-]*:') then
        local path,fragment=link.target:match('^([^#]+)(#.*)$')
        path=path or link.target; fragment=fragment or ''
        if baseurl ~= '' then
          local origin,basepath=baseurl:match('^(https?://[^/]+)(/.*)$')
          if not origin then origin=baseurl; basepath='/' end
          local file,line=path:match('^(.*):(%d+)$')
          if file and fragment == '' then path=file; fragment='#L'..line end
          link.target=origin..rooted_url_path(pandoc.path.join({basepath,path}))..fragment
        else
          link.target=pandoc.path.normalize(pandoc.path.join({basedir,path}))..fragment
        end
      end
      return link
    end})
  end
  return doc
end
function RawBlock(el)
  if FORMAT:match('latex') and el.format:match('html') then
    local id=el.text:match('^%s*<a%s+id="([%w_%-]+)"%s*>%s*</a>%s*$')
    if id then return pandoc.RawBlock('latex','\\phantomsection\\label{'..id..'}') end
  end
end
function RawInline(el)
  if FORMAT:match('latex') and el.format:match('html') then
    local id=el.text:match('^%s*<a%s+id="([%w_%-]+)"%s*>%s*$')
    if id then return pandoc.RawInline('latex','\\phantomsection\\label{'..id..'}') end
  end
end
local function breakable_text(text)
  local escaped = pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(text)})}), 'latex'):gsub('%s+$','')
  escaped=escaped:gsub('(\\_)','%1\\allowbreak{}')
  escaped=escaped:gsub('([/%.:%-])','%1\\allowbreak{}')
  return escaped
end
function Code(el)
  if FORMAT:match('latex') then
    -- Break long identifiers at their existing separators without changing text.
    return pandoc.RawInline('latex','\\texttt{'..breakable_text(el.text)..'}')
  end
end
function Str(el)
  if FORMAT:match('latex') and #el.text > 12 and el.text:match('^[%w_/%.-]+$') and el.text:match('[_/]') then
    return pandoc.RawInline('latex',breakable_text(el.text))
  end
end
function Table(t)
  -- Pandoc retains all cells; only allocate widths for wide quantitative tables.
  -- Longest numeric value controls its column, while prose labels can wrap.
  local n=#t.colspecs
  if n < 8 then return t end
  local numeric,maxlen={},{}
  for col=1,n do numeric[col]=true; maxlen[col]=1 end
  for _,body in ipairs(t.bodies) do
    for _,row in ipairs(body.body) do
      for col,cell in ipairs(row.cells) do
        local s=pandoc.utils.stringify(cell.contents)
        maxlen[col]=math.max(maxlen[col],#s)
        if not s:match('^[%d%.,%+%-%s%%]+$') and s ~= 'unknown' and s ~= '—' then numeric[col]=false end
      end
    end
  end
  local numeric_count=0
  for col=1,n do if numeric[col] then numeric_count=numeric_count+1 end end
  if numeric_count < n-2 then return t end
  local weights,total={},0
  for col=1,n do
    weights[col]=numeric[col] and math.max(9,maxlen[col]+1) or math.min(12,math.max(6,maxlen[col]))
    total=total+weights[col]
  end
  for col=1,n do t.colspecs[col][2]=weights[col]/total end
  return t
end
"""

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def find_tool(explicit: str | None, name: str, candidates: list[Path]) -> str:
    if explicit:
        selected = shutil.which(explicit) or str(Path(explicit).expanduser().resolve())
        if not Path(selected).is_file():
            raise FileNotFoundError(f'{name} not found: {selected}')
        return selected
    installed = shutil.which(name)
    if installed:
        return installed
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())
    raise FileNotFoundError(f'{name} not found; provide --{name} /path/to/{name}')

def run(command: list[str], log: Path, cwd: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, errors='replace')
    log.write_text(result.stdout, encoding='utf-8')
    status = {'command':command, 'returncode':result.returncode,
              'seconds':round(time.monotonic()-started,3), 'log':str(log)}
    if result.returncode:
        print(result.stdout[-6000:], file=sys.stderr)
        raise RuntimeError(f'Command failed ({result.returncode}); see {log}')
    return status

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input', type=Path, default=Path('docs/paper/research_dossier.md'))
    parser.add_argument('--output', type=Path, help='Target .tex path; PDF uses the same stem.')
    parser.add_argument('--pandoc', help='Pandoc executable (otherwise PATH/local known installation).')
    parser.add_argument('--tectonic', help='Tectonic executable (otherwise PATH/local known installation).')
    parser.add_argument('--font', default='WenQuanYi Zen Hei', help='Installed CJK font family or font file.')
    parser.add_argument('--main-font', default='DejaVu Serif', help='Latin body font family.')
    parser.add_argument('--mono-font', default='DejaVu Sans Mono', help='Latin monospace font family.')
    parser.add_argument('--title', help='Override the Markdown document title.')
    parser.add_argument('--date', default='', help='Printed date, empty by default for stable output.')
    parser.add_argument('--link-base-url', help='GitHub/HTTP directory URL used for relative file links; internal #anchors and absolute links stay unchanged.')
    parser.add_argument('--only-cached', action='store_true', help='Forbid Tectonic package downloads.')
    parser.add_argument('--tex-only', action='store_true', help='Export LaTeX without compiling PDF.')
    args=parser.parse_args()
    if args.link_base_url:
        uri=urlsplit(args.link_base_url)
        if uri.scheme not in ('http','https') or not uri.netloc or uri.query or uri.fragment:
            parser.error('--link-base-url must be an HTTP(S) directory URL without a query or fragment')
    source=args.input.expanduser().resolve()
    if not source.is_file(): parser.error(f'Markdown input does not exist: {source}')
    target=(args.output or source.parent/'latex'/f'{source.stem}.tex').expanduser().resolve()
    if target.suffix.lower() != '.tex': parser.error('--output must name a .tex file')
    if source == target: parser.error('Input and output must differ')
    target.parent.mkdir(parents=True,exist_ok=True)
    # Fallbacks are conveniences for this workspace; explicit arguments/PATH are portable.
    home=Path.home()
    pandoc=find_tool(args.pandoc,'pandoc',[home/'Documents/Codex/2026-10-02/cf_moa_paper/.build_deps/pypandoc/files/pandoc'])
    tectonic=None if args.tex_only else find_tool(args.tectonic,'tectonic',[home/'.local/opt/tectonic-0.17.0/tectonic'])
    header=target.with_suffix('.header.tex');lua=target.with_suffix('.filter.lua')
    header.write_text(HEADER,encoding='utf-8');lua.write_text(FILTER,encoding='utf-8')
    command=[pandoc,str(source),'--from=markdown-blank_before_header','--to=latex','--standalone',
             '--pdf-engine=tectonic','--table-of-contents','--toc-depth=2',
             '--resource-path='+str(source.parent),'--lua-filter='+str(lua),
             '--include-in-header='+str(header),'--output='+str(target),
             '-V','documentclass=article','-V','papersize=a4','-V','fontsize=11pt',
             '-V','geometry=margin=20mm,headsep=8mm,footskip=12mm',
             '-V','mainfont='+args.main_font,'-V','sansfont=DejaVu Sans',
             '-V','monofont='+args.mono_font,'-V','CJKmainfont='+args.font,
             '-V','CJKoptions=AutoFakeBold=1.5','-V','linestretch=1.15',
             '-V','colorlinks=true','-V','linkcolor=blue','-V','urlcolor=blue',
             '-M','toc-title=目录','-M','subtitle=共同作者阅读版 · 由 Markdown 导出',
             '-M','dossier-source-dir='+str(source.parent),
             '-M','date='+args.date]
    if args.title: command.extend(['-M','title='+args.title])
    if args.link_base_url:command.extend(['-M','dossier-link-base-url='+args.link_base_url.rstrip('/')+'/'])
    receipt={'kind':'author_research_dossier_markdown_export',
             'description':'Reading edition exported from collaborative Markdown; not the native LaTeX English conference paper.',
             'input':{'path':str(source),'sha256':sha256(source)},
             'builder':{'path':str(Path(__file__).resolve()),'sha256':sha256(Path(__file__))},
             'fonts':{'cjk':args.font,'main':args.main_font,'mono':args.mono_font},'stages':[]}
    receipt['link_base_url']=args.link_base_url
    receipt_path=target.with_suffix('.build.json')
    try:
        print(f'Exporting {source.name} -> {target.name}',flush=True)
        receipt['stages'].append(run(command,target.with_suffix('.pandoc.log'),source.parent))
        if tectonic:
            print(f'Compiling {target.with_suffix(".pdf").name}',flush=True)
            compilation=[tectonic,'--keep-logs','--keep-intermediates','--print','--outdir',str(target.parent)]
            if args.only_cached:compilation.append('--only-cached')
            compilation.append(str(target))
            receipt['stages'].append(run(compilation,target.with_suffix('.tectonic.stdout.log'),source.parent))
            log=target.with_suffix('.log').read_text(encoding='utf-8',errors='replace')
            receipt['missing_character_lines']=[line for line in log.splitlines() if 'Missing character:' in line]
            receipt['overfull_box_lines']=[line for line in log.splitlines() if 'Overfull ' in line]
            if receipt['missing_character_lines']:
                raise RuntimeError('Missing font glyphs in PDF; see build receipt and TeX log.')
            if receipt['overfull_box_lines']:
                print(f'Layout warning: {len(receipt["overfull_box_lines"])} overfull boxes; review the build receipt/PDF.',flush=True)
            if not target.with_suffix('.pdf').is_file():raise RuntimeError('Tectonic returned without a PDF.')
        receipt['status']='complete'
    except Exception as error:
        receipt['status']='failed';receipt['error']=str(error)
        raise
    finally:
        receipt['outputs']=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha256(p)}
                            for p in [target,target.with_suffix('.pdf'),header,lua] if p.is_file()]
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Done; receipt: {receipt_path}',flush=True)
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,RuntimeError) as error:
        print(f'build_dossier: {error}',file=sys.stderr);raise SystemExit(1)
