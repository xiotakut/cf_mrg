"""Explicit native interface for complete, saved strong-old answers.

No generation, scoring or answer repair occurs here. Existing objects retain
every value. A list/string answer can gain only an execution-record summary;
missing semantic auxiliary fields cannot be invented to satisfy a schema.
"""
from copy import deepcopy
import json

from jsonschema import ValidationError, validate

from cf_moa.contracts import digest, reject_metadata

VARIANT = 'strong_old_native_interface_v2'


def answer_value(native):
    return native.get('answer_choice') if isinstance(native, dict) else native


def _execution_summary(result):
    """Describe stored program outputs, never reconstruct private reasoning."""
    prefix = 'Deterministic summary of the saved execution record; not a model reasoning transcript. '
    if result.get('branch') == 'rule_support':
        required = ('action', 'scope', 'applied', 'reason', 'options')
        if any(key not in result for key in required) or not isinstance(result['options'], dict):
            raise ValueError('Stored rule execution lacks fields required for a factual summary')
        states = {}
        for candidate, option in result['options'].items():
            if not isinstance(option, dict) or 'state' not in option or not isinstance(option.get('paths'), list):
                raise ValueError('Stored rule option has no complete state/path record')
            paths = []
            for path in option['paths']:
                if not isinstance(path, dict) or not {'rule_id', 'state'} <= set(path):
                    raise ValueError('Stored support path lacks identity or state')
                paths.append(dict(rule_id=path['rule_id'], state=path['state']))
            states[candidate] = dict(state=option['state'], paths=paths)
        record = {key: result[key] for key in ('action', 'scope', 'applied', 'reason')}
        record['recorded_option_states'] = states
        return (prefix + 'The stored rule execution was conditional on model-extracted patient facts. '
                + json.dumps(record, ensure_ascii=False, separators=(',', ':'))
                + '. The stored answer is carried unchanged; this summary adds no medical evidence.')
    if result.get('branch') == 'catalog_vote':
        details = result.get('details')
        if not isinstance(details, dict) or not isinstance(details.get('per_order'), list):
            raise ValueError('Stored catalogue execution has no recorded per-order results')
        if not details['per_order'] or 'majority_vote' not in details or 'mean_probability' not in details:
            raise ValueError('Stored catalogue execution lacks its selection record')
        record = dict(recorded_orders=len(details['per_order']),
                      recorded_order_winners=details['per_order'],
                      recorded_majority_vote=details['majority_vote'],
                      recorded_mean_probability_winner=details['mean_probability'])
        return (prefix + 'The stored catalogue result came from calibrated candidate scoring and program aggregation. '
                + json.dumps(record, ensure_ascii=False, separators=(',', ':'))
                + '. These are model preferences, not independent patient facts. The stored answer is carried unchanged.')
    raise ValueError('No supported rule/catalogue execution record for deterministic wrapping')


def wrap(packet, strong_row, component_row, source_proof):
    """Return one new-interface row; source_proof binds already-verified files.

    Hash/file reading is the caller's responsibility. Row-level binding is
    checked here, including the strong control's original component pointer.
    Invalid native objects remain in candidate_native_answer for auditing but
    are never exposed as a usable native_answer.
    """
    for row in (strong_row, component_row):
        if (row.get('request_id') != packet.request_id or row.get('input_hash') != packet.input_hash
                or row.get('status') != 'complete'):
            raise ValueError('Saved B source is not a complete result for this exact legal input')
    trace = strong_row['proposal']['trace']
    component_proof = source_proof['component_source']
    if (trace.get('source_output') != component_proof['path']
            or trace.get('source_output_sha256') != component_proof['file_sha256']
            or trace.get('source_request_id') != packet.request_id
            or trace.get('source_input_hash') != packet.input_hash):
        raise ValueError('Strong B component source pointer does not match its bound source')
    for key, row in [('strong_source', strong_row), ('component_source', component_row)]:
        if source_proof[key]['row_digest'] != digest(row):
            raise ValueError('Saved B source row changed after binding')
    original = strong_row['proposal']['native_proposal']
    if digest(original) != digest(component_row['proposal']['native_proposal']):
        raise ValueError('Strong B and selected component answers disagree')
    reject_metadata(original)
    candidate = deepcopy(original)
    failure = None
    detail = None
    action = 'unchanged_existing_native_object'
    if not isinstance(original, dict):
        action = 'deterministic_execution_summary_wrapper'
        result = component_row['proposal'].get('trace', {}).get('legacy_result')
        try:
            if not isinstance(original, (list, str)) or not isinstance(result, dict):
                raise ValueError('Only a complete stored list/string with an execution record can be wrapped')
            if 'answer' not in result or digest(result['answer']) != digest(original):
                raise ValueError('Stored execution answer differs from the original answer value')
            reject_metadata(result)
            candidate = dict(step_by_step_thinking=_execution_summary(result), answer_choice=deepcopy(original))
        except ValueError as error:
            failure, detail = 'baseline_execution_summary_unavailable', str(error)
    if failure is None:
        try:
            validate(candidate, packet.answer_schema)
        except ValidationError as error:
            failure = 'baseline_native_schema_invalid'
            detail = dict(validator=error.validator, path=list(error.absolute_path),
                          schema_path=list(error.absolute_schema_path), message=error.message)
    preserved = digest(answer_value(candidate)) == digest(answer_value(original))
    if not preserved:
        raise AssertionError('The native interface must never change the stored answer value')
    valid = failure is None
    return dict(request_id=packet.request_id, input_hash=packet.input_hash, variant=VARIANT,
        status='complete' if valid else 'unavailable', native_answer=deepcopy(candidate) if valid else None,
        base_answer_ref=digest(candidate) if valid else None, source_proof=deepcopy(source_proof),
        cost=deepcopy(strong_row['cost']), original_native_proposal=deepcopy(original),
        candidate_native_answer=candidate, native_valid=valid, failure_type=failure,
        failure_detail=detail, method_score='not_scored', interface_action=action,
        semantic_result='native_answer_available' if valid else 'unavailable',
        answer_value_preserved=preserved, original_source_status=strong_row['status'],
        historical_score_recomputed=False, new_model_requests=0,
        explanation_provenance=('existing_complete_native_object_unchanged' if isinstance(original, dict)
                                else 'deterministic_saved_program_execution_summary_not_model_reasoning'))
