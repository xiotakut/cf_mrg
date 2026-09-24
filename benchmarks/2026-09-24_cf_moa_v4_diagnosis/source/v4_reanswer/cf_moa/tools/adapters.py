"""Measured model callbacks and a hard per-input request/token budget."""
from copy import deepcopy
import json
import math
import time

from cf_moa.contracts import ModelResult, digest, reject_metadata


class BudgetExceeded(RuntimeError):
    pass


class ModelSession:
    """backend(request) -> ModelResult; backend.count_tokens(request) -> int.

    Every call to the backend is one physical model request. Missing score codes
    use additional identical-prompt requests within the same budget. Failures are
    recorded and propagated; invalid model answers are not silently retried.
    """
    def __init__(self, packet, backend):
        self.packet, self.backend = packet, backend
        self.calls, self.tools = [], []
        self.reserved_input = self.reserved_output = 0

    def invoke(self, request, *, stage):
        request = deepcopy(request)
        reject_metadata(request)
        budget = self.packet.budget
        if len(self.calls) >= budget.max_model_requests:
            raise BudgetExceeded('Physical model request budget exhausted')
        input_tokens = self.backend.count_tokens(request)
        maximum = request['max_tokens']
        if self.reserved_input + input_tokens > budget.max_input_tokens:
            raise BudgetExceeded('Input token budget exhausted')
        if self.reserved_output + maximum > budget.max_output_tokens:
            raise BudgetExceeded('Insufficient output budget for this complete request')
        self.reserved_input += input_tokens
        self.reserved_output += maximum
        record = dict(stage=stage, request=request, request_hash=digest(request),
                      status='started', reserved_input_tokens=input_tokens,
                      reserved_output_tokens=maximum)
        self.calls.append(record)
        started = time.monotonic()
        try:
            result = self.backend(request)
            if not isinstance(result, ModelResult) or len(result.events) != 1:
                raise ValueError('Backend must report exactly one physical request')
            event = result.events[0]
            if event['input_tokens'] != input_tokens or event['output_tokens'] > maximum:
                raise ValueError('Backend token count disagrees with the reserved request')
            self.reserved_output -= maximum - event['output_tokens']
            record.update(status='complete', value=result.value, event=event)
            return result.value
        except Exception as error:
            record.update(status='failed', error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record['callback_seconds'] = time.monotonic() - started

    def generate(self, messages, schema, seed=42, temperature=0, max_tokens=2048, *, stage='generate', decoding_revision=None, reference_max_start=None):
        request = dict(messages=messages, schema=schema, seed=seed,
            temperature=temperature, max_tokens=max_tokens, kind='generate')
        if decoding_revision is not None:
            request['decoding_revision'] = decoding_revision
        if reference_max_start is not None:
            request['reference_max_start'] = reference_max_start
        return self.invoke(request, stage=stage)

    def generate_adopted(self, messages, schema, adopted, *, stage):
        # Deliberately bypass generate() and all its generic defaults. The bound
        # policy includes model, rendering, sampling, and guidance for one backbone.
        return self.invoke(adopted.request(messages, schema), stage=stage)

    def score(self, *, messages=None, prompt=None, schema=None, codes, seed=42, stage='score'):
        if (messages is None) == (prompt is None):
            raise ValueError('Supply exactly one complete prompt or message sequence')
        request = dict(schema=schema, codes=list(codes), allowed_codes=list(codes),
            seed=seed, temperature=0, max_tokens=1, kind='score')
        request.update(messages=messages) if messages is not None else request.update(prompt=prompt)
        scores = dict(self.invoke(request, stage=stage))
        if set(scores) - set(codes):
            raise ValueError('Backend returned a foreign score code')
        for code in codes:
            if code not in scores:
                extra = self.invoke(dict(request, allowed_codes=[code]), stage=stage + ':missing_code')
                scores[code] = extra[code]
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in scores.values()):
            raise ValueError('All candidate scores must be finite')
        return scores

    def tool(self, name, function, *args, **kwargs):
        if name not in self.packet.available_tools:
            raise ValueError('The requested tool is not declared available: ' + name)
        if len(self.tools) >= self.packet.budget.max_tool_calls:
            raise BudgetExceeded('Tool invocation budget exhausted')
        record = dict(name=name, status='started')
        self.tools.append(record)
        started = time.monotonic()
        model_start = len(self.calls)
        try:
            value = function(*args, **kwargs)
            record.update(status='complete', result_hash=digest(value))
            return value
        except Exception as error:
            record.update(status='failed', error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record['elapsed_seconds'] = time.monotonic() - started
            record['nested_model_seconds'] = sum(c['callback_seconds'] for c in self.calls[model_start:])
            record['exclusive_seconds'] = max(0, record['elapsed_seconds'] - record['nested_model_seconds'])

    def checkpoint(self):
        return len(self.calls), len(self.tools)

    def cost_since(self, checkpoint=(0, 0)):
        calls, tools = self.calls[checkpoint[0]:], self.tools[checkpoint[1]:]
        events = [call['event'] for call in calls if 'event' in call]
        live, replay = ([e for e in events if e['mode'] == mode] for mode in ('live', 'replay'))
        return dict(physical_model_requests=len(calls), new_model_requests=len(live),
            replayed_model_requests=len(replay), failed_model_requests=sum(c['status'] == 'failed' for c in calls),
            live_input_tokens=sum(e['input_tokens'] for e in live),
            live_output_tokens=sum(e['output_tokens'] for e in live),
            replayed_original_input_tokens=sum(e['input_tokens'] for e in replay),
            replayed_original_output_tokens=sum(e['output_tokens'] for e in replay),
            model_callback_seconds=sum(c['callback_seconds'] for c in calls),
            tool_calls=len(tools), tool_seconds=sum(t['exclusive_seconds'] for t in tools),
            tool_inclusive_seconds=sum(t['elapsed_seconds'] for t in tools),
            missing_usage=sum('event' not in c for c in calls),
            retrieval_calls=0)


def native_json(raw, schema):
    """Output validation only; it never scores correctness or rewrites an answer."""
    import jsonschema
    value = json.loads(raw)
    jsonschema.validate(value, schema)
    return value


def messages_with_instruction(packet, instruction):
    if isinstance(packet.original_context, str):
        # Preserve the complete serialized original as data for this new variant.
        # Legacy score callbacks use their exact original serialized prompt instead.
        context = [dict(role='user', content=packet.original_context)]
    else:
        context = deepcopy(packet.original_context)
    return [*context, dict(role='user', content=instruction)]
