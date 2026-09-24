"""Load the selected, unmodified R1/R2/R3 kernels from their verified package."""
import importlib
import importlib.util
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
import sys

R123 = Path('/home/data3/txy/Documents/Codex/2026-09-16/r1_head_experiments/candidate')
R4 = Path('/home/data3/txy/Documents/Codex/2026-09-17/r4_structural_head/physiology_head/frozen_method/physiology_head')
R5 = Path('/home/data3/txy/Documents/Codex/2026-09-18/r5_head/delivery')


def r123_module(name):
    if not name.startswith(('r1_', 'r2_', 'r3_')) or not (R123 / (name + '.py')).is_file():
        raise ValueError('Not a selected historical module: ' + name)
    for loaded_name, module in tuple(sys.modules.items()):
        if loaded_name.startswith(('r1_', 'r2_', 'r3_')) and (R123 / (loaded_name + '.py')).is_file():
            actual = Path(getattr(module, '__file__', '')).resolve()
            if actual != R123 / (loaded_name + '.py'):
                raise RuntimeError('Historical module collision: ' + str(actual))
    sys.path.insert(0, str(R123))
    try:
        module = importlib.import_module(name)
    finally:
        sys.path.remove(str(R123))
    if Path(module.__file__).resolve() != R123 / (name + '.py'):
        raise RuntimeError('Unexpected historical module: ' + str(module.__file__))
    return module


@lru_cache(maxsize=1)
def r5_module():
    spec = importlib.util.spec_from_file_location('_cf_moa_selected_r5', R5 / 'r5_head.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def r4_modules():
    """The historical solver imports generic names lazily; bind exact paths."""
    before = list(sys.path)
    for name in ('head', 'head_v2', 'executor'):
        existing = sys.modules.get(name)
        if existing is not None and Path(existing.__file__).resolve() != R4 / (name + '.py'):
            raise RuntimeError('Historical R4 module collision: ' + name)
    sys.path[:0] = [str(R4), str(R4.parent)]
    try:
        head = importlib.import_module('head_v2')
        executor = importlib.import_module('executor')
        yield head, executor
    finally:
        sys.path[:] = before
