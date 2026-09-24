"""Fixed development-candidate generation policy; separate from adopted heads."""
from copy import deepcopy
from functools import lru_cache
import json

from cf_moa.tools.adopted import CONFIG_ROOT


@lru_cache(maxsize=1)
def prototype():
    return json.loads((CONFIG_ROOT/'prototype.json').read_text())


def new_policy(operation):
    limits={'A1:coverage':'a1_audit_max_tokens','A1:answer':'answer_max_tokens',
            'A3:editor':'a3_editor_max_tokens','A3:answer':'answer_max_tokens',
            'A5:view':'answer_max_tokens','A5:adjudication':'answer_max_tokens'}
    if operation not in limits:
        raise ValueError('Unregistered new experimental generation operation')
    cfg=prototype()['new_generation']
    return deepcopy(dict(seed=cfg['seed'],temperature=cfg['temperature'],max_tokens=cfg[limits[operation]]))
