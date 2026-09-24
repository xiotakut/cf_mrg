"""Experiment-scoped ordinary F seed tables; adopted module stays immutable."""
from copy import deepcopy

from cf_moa.tools.adapters import ModelSession


ORIGINAL_SEEDS = (42, 43, 44, 45, 46)


class PoolReplicaSession(ModelSession):
    def __init__(self, packet, backend, *, f_generation_seeds):
        super().__init__(packet, backend)
        seeds = tuple(f_generation_seeds)
        if len(seeds) != 5 or len(set(seeds)) != 5 or any(type(s) is not int for s in seeds):
            raise ValueError('A replica needs five distinct integer F generation seeds')
        self.f_seed_map = dict(zip(ORIGINAL_SEEDS, seeds))

    def invoke(self, request, *, stage):
        original_seed = request.get('seed')
        mapped = (stage == 'A5:F_generate' and request.get('kind') == 'generate'
                  and request.get('temperature') == 0.7)
        if mapped:
            if original_seed not in self.f_seed_map:
                raise ValueError('Ordinary F requested a seed outside the bound original table')
            request = deepcopy(request)
            request['seed'] = self.f_seed_map[original_seed]
        before = len(self.calls)
        try:
            return super().invoke(request, stage=stage)
        finally:
            if mapped and len(self.calls) > before:
                self.calls[-1]['f_pool_replica'] = dict(
                    original_requested_seed=original_seed,
                    actual_submitted_seed=request['seed'],
                    scope='ordinary_F_generation_only')


def session_for_plan(packet, backend, plan):
    seeds = plan.get('f_generation_seeds')
    return (ModelSession(packet, backend) if seeds is None else
            PoolReplicaSession(packet, backend, f_generation_seeds=seeds))
