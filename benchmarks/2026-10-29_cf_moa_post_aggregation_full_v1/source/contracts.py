"""Current-input and proposal contracts; no evaluation data belongs here."""
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Any, Literal

NATIVE_FIELDS = frozenset(('question', 'options', 'fixed_evidence', 'answer_format'))
FORBIDDEN_FIELDS = frozenset(('gold', 'gold_answer', 'target_answer', 'evaluation_labels',
    'labels', 'classification_reason', 'classification_rationale', 'reference_answer',
    'reference_input', 'paired_input', 'paired_answer', 'pair_id', 'unit_id', 'group_id',
    'resource_id', 'source_id', 'item_id', 'author_explanation', 'author_answer'))


def reject_metadata(value, path='input'):
    """Reject metadata keys, without censoring ordinary text containing these words."""
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError('All object keys must be strings: ' + path)
            if key.casefold() in FORBIDDEN_FIELDS:
                raise ValueError('Evaluation metadata is not an inference input: ' + path + '.' + key)
            reject_metadata(child, path + '.' + key)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            reject_metadata(child, path + '[' + str(index) + ']')


def digest(value):
    # Preserve insertion order: option and schema order can affect model requests.
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, allow_nan=False,
        separators=(',', ':')).encode()).hexdigest()


@dataclass(frozen=True)
class Budget:
    max_model_requests: int = 16
    max_input_tokens: int = 400000
    max_output_tokens: int = 32768
    max_tool_calls: int = 4

    def __post_init__(self):
        if any(type(x) is not int or x < 0 for x in asdict(self).values()):
            raise ValueError('Budget limits must be nonnegative integers')


@dataclass
class InputPacket:
    request_id: str
    native_input: dict[str, Any]
    question: str
    original_context: list[dict[str, str]] | str
    answer_schema: dict[str, Any]
    baseline_answer: Any = None
    baseline_response: str | None = None
    retrieved_context: list[dict[str, str]] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    budget: Budget = field(default_factory=Budget)
    model_input: dict[str, Any] | None = None

    def __post_init__(self):
        unknown = set(self.native_input) - NATIVE_FIELDS
        if unknown:
            raise ValueError('Native input has non-whitelisted fields: ' + repr(sorted(unknown)))
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError('A complete current question is required')
        if self.native_input.get('question') != self.question:
            raise ValueError('The current question and native input disagree')
        if not isinstance(self.native_input.get('answer_format'), str):
            raise ValueError('Native answer_format is required')
        if not isinstance(self.native_input.get('options', {}), dict):
            raise ValueError('Native options must preserve their original key order')
        if not isinstance(self.request_id, str) or not self.request_id:
            raise ValueError('An opaque request handle is required')
        if not isinstance(self.original_context, str):
            for message in self.original_context:
                if set(message) != {'role', 'content'} or message['role'] not in (
                        'system', 'user', 'assistant', 'tool') or not isinstance(message['content'], str):
                    raise ValueError('Original messages require only role and complete text content')
        for entry in self.retrieved_context:
            if set(entry) - {'ref', 'text', 'uri', 'title'} or not all(
                    isinstance(value, str) for value in entry.values()) or 'text' not in entry:
                raise ValueError('Retrieved evidence must have text and only declared source fields')
        for value in (self.native_input, self.original_context, self.retrieved_context,
                      self.answer_schema, self.model_input, self.baseline_answer):
            reject_metadata(value)
        # Make caller mutation unable to change a packet after its provenance is bound.
        self.native_input = deepcopy(self.native_input)
        self.original_context = deepcopy(self.original_context)
        self.answer_schema = deepcopy(self.answer_schema)
        self.retrieved_context = deepcopy(self.retrieved_context)
        self.model_input = deepcopy(self.model_input)
        self.baseline_answer = deepcopy(self.baseline_answer)

    @property
    def input_hash(self):
        return digest(self.visible())

    def visible(self):
        """Only these fields may enter an expert or controller model request."""
        return dict(native_input=self.native_input, original_context=self.original_context,
            retrieved_context=self.retrieved_context, answer_schema=self.answer_schema,
            baseline_answer=self.baseline_answer, baseline_response=self.baseline_response,
            available_tools=self.available_tools, model_input=self.model_input)


@dataclass
class AgentProposal:
    agent_id: Literal['A1', 'A2', 'A3', 'A4', 'A5']
    variant: str
    input_hash: str
    applicability: Literal['supported', 'partial', 'unsupported']
    native_proposal: Any | None
    claims: list[dict[str, Any]] = field(default_factory=list)
    requested_changes: list[dict[str, Any]] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    cost: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.agent_id not in ('A1', 'A2', 'A3', 'A4', 'A5'):
            raise ValueError('Unknown expert')
        if self.applicability not in ('supported', 'partial', 'unsupported'):
            raise ValueError('Unknown applicability')
        if self.applicability == 'unsupported' and self.native_proposal is not None:
            raise ValueError('An unsupported operation must not claim a new answer')
        for check in self.checks:
            if check.get('type') not in ('program_execution', 'model_assessment', 'format_validation'):
                raise ValueError('Every check must state its actual evidence type')
        for claim in self.claims:
            if claim.get('kind') not in ('patient_fact', 'general_knowledge', 'hypothetical_probe', 'tool_output'):
                raise ValueError('Every claim must state its provenance kind')

    def to_dict(self):
        return asdict(self)


@dataclass
class ModelResult:
    value: Any
    events: list[dict[str, Any]]

    def __post_init__(self):
        if not self.events:
            raise ValueError('Actual generation, scoring, or replay events are required')
        for event in self.events:
            if event.get('mode') not in ('live', 'replay'):
                raise ValueError('Declare whether each model event is new or replayed')
            for key in ('input_tokens', 'output_tokens'):
                if type(event.get(key)) is not int or event[key] < 0:
                    raise ValueError('Model token costs must be measured: ' + key)
            latency = event.get('elapsed_seconds')
            if isinstance(latency, bool) or not isinstance(latency, (int, float)) or not math.isfinite(latency) or latency < 0:
                raise ValueError('Event latency must be measured and finite')
            if not event.get('model') or not event.get('config_hash'):
                raise ValueError('Every event must identify its actual model and configuration')
