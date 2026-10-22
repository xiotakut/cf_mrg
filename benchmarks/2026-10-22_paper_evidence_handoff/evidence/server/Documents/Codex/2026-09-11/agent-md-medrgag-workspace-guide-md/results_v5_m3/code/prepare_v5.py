from prepare import OUT, read, write
from pathlib import Path
import json
PACK=Path("/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack")
def dump(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
