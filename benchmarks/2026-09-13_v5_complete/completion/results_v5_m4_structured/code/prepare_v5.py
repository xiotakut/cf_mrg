"""Frozen v5 paths and the original scorer's JSON I/O interface."""
import gzip
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
PACK = Path('/home/data3/txy/Documents/Codex/2026-08-23/https-github-com-xiotakut-cf-mrg/cf_medrgag_validation_pack')
SOURCE = Path('/home/data3/txy/Documents/Codex/2026-09-11/agent-md-medrgag-workspace-guide-md/results_v5_m0_m2_m4_m5')


def read(path):
    if not path.exists():
        return []
    op = gzip.open if path.suffix == '.gz' else open
    with op(path, 'rt') as f:
        return [json.loads(line) for line in f if line.strip()]


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    tmp.replace(path)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)
