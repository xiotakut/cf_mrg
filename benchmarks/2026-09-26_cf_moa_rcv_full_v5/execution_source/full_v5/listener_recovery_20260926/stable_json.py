"""Bounded metadata read retry; no raw JSON contents are emitted to diagnostics."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

RETRY_DELAYS = (0.1, 0.25, 0.5, 1.0)
AUDIT_PATH = None


class PersistentJSONReadError(ValueError):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
        super().__init__(json.dumps(diagnostic, ensure_ascii=False))


def emit(diagnostic):
    if AUDIT_PATH is not None:
        with Path(AUDIT_PATH).open('a') as stream:
            stream.write(json.dumps(diagnostic, ensure_ascii=False) + '\n')


def read_json(path, *, delays=RETRY_DELAYS, sleeper=time.sleep, audit=None):
    """Retry decode failures only; persistent corruption fails with exact path.

    Five reads and 1.85 seconds of waiting by default. File/permission errors
    are not hidden. This does not retry any child job, model call, or scorer.
    """
    path = Path(path)
    report = emit if audit is None else audit
    errors = []
    for attempt in range(len(delays) + 1):
        raw = path.read_bytes()
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            detail = dict(attempt=attempt + 1, bytes=len(raw),
                          sha256=hashlib.sha256(raw).hexdigest(),
                          error_type=type(error).__name__, error=str(error))
            if isinstance(error, json.JSONDecodeError):
                detail.update(line=error.lineno, column=error.colno, position=error.pos)
            errors.append(detail)
            if attempt < len(delays):
                sleeper(delays[attempt])
                continue
            diagnostic = dict(status='persistent_json_read_error', path=str(path.resolve()),
                              at=datetime.now(timezone.utc).isoformat(), attempts=attempt + 1,
                              total_retry_wait_seconds=sum(delays), failures=errors)
            report(diagnostic)
            raise PersistentJSONReadError(diagnostic) from error
        if errors:
            report(dict(status='transient_json_read_recovered', path=str(path.resolve()),
                        at=datetime.now(timezone.utc).isoformat(), attempts=attempt + 1,
                        total_retry_wait_seconds=sum(delays[:attempt]), failures=errors,
                        final_bytes=len(raw), final_sha256=hashlib.sha256(raw).hexdigest()))
        return value
