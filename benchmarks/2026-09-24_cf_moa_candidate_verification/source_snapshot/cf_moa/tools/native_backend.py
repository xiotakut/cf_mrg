"""Native R2 facts, R3 code scoring, and F-generation policies for M4/M5.

New A1/A5 operations use F's model/rendering engine and explicitly declared
per-call parameters. No memory, context, prompt, or seed tuning is performed.
"""
from copy import deepcopy
from dataclasses import dataclass
import json

from cf_moa.contracts import digest
from cf_moa.tools.adopted import CONFIG_ROOT, sha256
from cf_moa.tools.vllm_backend import VLLMBackend, sampling_snapshot
from cf_moa.tools.schema_compat import guidance


@dataclass
class NativeProfile:
    method: str
    role: str
    config: dict
    source: dict

    @property
    def config_hash(self):
        return digest(dict(role=self.role,config=self.config))

    def engine_kwargs(self):
        cfg=self.config
        args=dict(model=cfg['model'],seed=cfg['seed'],
            **{k:cfg[k] for k in ('dtype','gpu_memory_utilization','max_model_len','max_num_seqs','max_num_batched_tokens')},
            **cfg['model_kwargs'],enable_prefix_caching=True,enable_chunked_prefill=True)
        if self.role!='facts':
            args.update(enforce_eager=True,max_logprobs=2048)
        if self.role!='catalog':
            args['guided_decoding_backend']='xgrammar'
        return args


def profile(method,role):
    if method not in ('M4','M5') or role not in ('facts','catalog','readout'):
        raise ValueError('An explicit supported backbone and native role are required')
    manifest=json.loads((CONFIG_ROOT/'native_sources.json').read_text())
    source=manifest[role][method]
    copied=CONFIG_ROOT/source['copy']
    if sha256(copied)!=source['sha256'] or sha256(source['path'])!=source['sha256']:
        raise RuntimeError('Native selected configuration no longer matches its source')
    return NativeProfile(method,role,json.loads(copied.read_text()),deepcopy(source))


class NativeBackend(VLLMBackend):
    def prepare(self,request):
        cfg=self.adopted.config
        prompt=request.get('prompt')
        if prompt is None:
            prompt=self.tokenizer.apply_chat_template(request['messages'],tokenize=False,
                add_generation_prompt=True,**cfg.get('chat_template_kwargs',{}))
        if request['kind']=='score':
            if request['temperature']!=0 or request['max_tokens']!=1:
                raise ValueError('Native code score requires temperature0 and one token')
            ids={c:self.tokenizer.encode(c,add_special_tokens=False) for c in request['codes']}
            if not all(len(v)==1 for v in ids.values()):
                raise ValueError('An adopted native code must be exactly one token')
            prompt += '{"answer_choice": "'
            forced=len(request['allowed_codes'])<len(request['codes'])
            params=self.SamplingParams(seed=request['seed'],temperature=0,max_tokens=1,
                logprobs=0 if forced else 2048,allowed_token_ids=[ids[c][0] for c in request['allowed_codes']])
        else:
            options={k:request[k] for k in ('seed','temperature','max_tokens')}
            if self.adopted.role=='facts':
                for key in ('seed','temperature','max_tokens'):
                    if request[key]!=cfg[key]:
                        raise ValueError('A2 facts request changed adopted '+key)
                options.update(top_p=cfg['top_p'],top_k=cfg['top_k'])
            elif request['temperature']:
                options.update(top_p=cfg['top_p'],top_k=cfg['top_k'])
            if request.get('schema') is not None:
                # F explicitly guides when a schema is provided, including Qwen.
                options['guided_decoding']=guidance(request['schema'],self.Guided,
                    decoding_revision=request.get('decoding_revision'),
                    reference_max_start=request.get('reference_max_start'))
            elif request.get('decoding_revision') is not None or request.get('reference_max_start') is not None:
                raise ValueError('A decoding revision cannot be used without its output schema')
            params=self.SamplingParams(**options)
        length=len(self.tokenizer.encode(prompt))
        if length+request['max_tokens']>cfg['max_model_len']:
            raise ValueError('Complete native context exceeds selected capacity; no truncation')
        return dict(engine_kwargs=self.adopted.engine_kwargs(),prompt=prompt,
            sampling_params=sampling_snapshot(params),use_tqdm=False),params

    def interpret(self,result,request):
        if request['kind']!='score':
            return super().interpret(result,request)
        answer=result.outputs[0]
        ids={c:self.tokenizer.encode(c,add_special_tokens=False)[0] for c in request['codes']}
        if len(answer.token_ids)!=1 or answer.token_ids[0] not in [ids[c] for c in request['allowed_codes']]:
            raise ValueError('Native score generated a foreign or empty code')
        return {c:answer.logprobs[0][tid].logprob for c,tid in ids.items() if tid in answer.logprobs[0]}
