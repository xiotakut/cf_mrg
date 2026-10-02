-- Pandoc AST presentation filter; Markdown parsing stays with Pandoc.
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
