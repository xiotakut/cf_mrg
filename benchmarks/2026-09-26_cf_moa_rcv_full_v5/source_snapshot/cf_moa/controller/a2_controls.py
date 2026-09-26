"""Separate A2 mechanism controls on cached current-input facts.

The adopted expert is unchanged. No evaluation labels, paired patient or gold
are loaded here; controls retain their identities and do not become experts.
"""
import ast
import builtins
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema

from cf_moa.agents.a2_support_revision import applicable, VARIANT as A2_VARIANT
from cf_moa.contracts import AgentProposal, reject_metadata
from cf_moa.tools.adopted import AdoptedGeneration, CONFIG_ROOT, sha256
from cf_moa.tools.legacy import r123_module
from cf_moa.tools.schema_compat import OutputSchemaError

CONFIG = CONFIG_ROOT / 'a2_controls.json'
EXECUTOR_VARIANT = 'same_facts_scoped_reasoned_executor_8192_v1'
NATIVE_EXECUTOR_VARIANT = 'same_facts_scoped_reasoned_executor_8192_native_parser_v2'
STRICT_PARSER = 'strict_v1'
NATIVE_PARSER = 'historical_native_v2'
PARSER_POLICIES = (STRICT_PARSER, NATIVE_PARSER)


def execution_policy(parser_policy=STRICT_PARSER):
    if parser_policy not in PARSER_POLICIES:
        raise ValueError('Unknown explicit A2 parser policy')
    original = config()
    if parser_policy == STRICT_PARSER:
        return original
    revised = json.loads((CONFIG_ROOT / 'a2_controls_native_parser_v2.json').read_text())
    if (revised['parent_config_sha256'] != sha256(CONFIG)
            or revised['parser_policy'] != NATIVE_PARSER
            or revised['variant'] != NATIVE_EXECUTOR_VARIANT):
        raise RuntimeError('Native-parser control revision differs from its parent identity')
    return dict(original=original, revision=revised)


def executor_variant(parser_policy):
    execution_policy(parser_policy)
    return NATIVE_EXECUTOR_VARIANT if parser_policy == NATIVE_PARSER else EXECUTOR_VARIANT


def historical_parse_execution(raw, method):
    """Run the hash-bound original function with only its parser dependency.

    Its local import is resolved without importing the legacy scoring driver,
    touching global sys.modules, or loading any evaluation data.
    """
    cfg = config()
    if method not in ('M4', 'M5'):
        raise ValueError('An explicit backbone is required')
    analyzer = next(p for p in cfg['legacy_sources'] if p.endswith('/analyze_v5.py'))
    reasoning = next(p for p in cfg['legacy_sources'] if p.endswith('/r2_samefacts_reasoning.py'))
    objects = source_function(analyzer, ('objects',), dict(json=json))['objects']

    def parser_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name != 'analyze_v5' or tuple(fromlist) != ('objects',) or level:
            raise ImportError('Unexpected historical parser dependency: ' + name)
        return SimpleNamespace(objects=objects)

    namespace = dict(__builtins__={**vars(builtins), '__import__': parser_import})
    original = source_function(reasoning, ('parse_states',), namespace)['parse_states']
    return original(raw, {'M4': 'llama', 'M5': 'qwen'}[method])


def config():
    value = json.loads(CONFIG.read_text())
    for path, expected in value['legacy_sources'].items():
        if sha256(path) != expected:
            raise RuntimeError('Historical A2 control source changed: ' + path)
    return value


def source_function(path, names, namespace):
    """Bind only named functions; never import a legacy scoring/data driver."""
    nodes = [node for node in ast.parse(Path(path).read_text()).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != set(names):
        raise RuntimeError('Historical control function is missing')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


@dataclass(frozen=True)
class StrongExecutorProfile(AdoptedGeneration):
    """Original sufficient-reasoning worker settings, independent of A2 facts."""
    def engine_kwargs(self):
        cfg = self.config
        return deepcopy(dict(model=cfg['model'], seed=cfg['seed'],
            **{key: cfg[key] for key in ('dtype', 'gpu_memory_utilization', 'max_model_len',
                                       'max_num_seqs', 'max_num_batched_tokens')},
            **cfg.get('model_kwargs', {}), enable_prefix_caching=True,
            enable_chunked_prefill=True, guided_decoding_backend='xgrammar'))


def execution_profile(method):
    source = config()['models'][method]
    copied = CONFIG_ROOT / source['copy']
    if sha256(copied) != source['sha256'] or sha256(source['path']) != source['sha256']:
        raise RuntimeError('The complete original execution profile changed')
    return StrongExecutorProfile(method, json.loads(copied.read_text()), deepcopy(source))


def replay_saved_result(packet, row):
    """Recompute with the same cached fact response, not a new extraction."""
    proposal = row['proposal']
    if row['input_hash'] != packet.input_hash or proposal['variant'] != A2_VARIANT:
        raise ValueError('Facts must come from adopted A2 on this exact legal input')
    if row['status'] != 'complete':
        raise ValueError('Stopped or failed A2 output cannot be silently reused')
    if not applicable(packet):
        if proposal['applicability'] != 'unsupported' or proposal['native_proposal'] is not None:
            raise ValueError('A2 applicability differs from the current visible capability')
        return None
    raw = proposal['trace']['raw_facts']
    if len(raw) != 1:
        raise ValueError('Exactly one original cached facts response is required')
    extraction = json.loads(raw[0])
    reject_metadata(extraction)
    result = r123_module('r2_condition_head').resolve(packet.native_input, packet.baseline_answer, extraction)
    saved = proposal['trace']['legacy_result']
    # clean_facts iterates a set of required fields. Only diagnostic ordering
    # can vary by process; preserve duplicates and compare everything else
    # exactly, including path order, support states and the native answer.
    def comparable(value):
        value = deepcopy(value)
        value['evidence_errors'] = sorted(value['evidence_errors'],
                                          key=lambda error: json.dumps(error, sort_keys=True))
        return value
    if comparable(result) != comparable(saved) or result['answer'] != proposal['native_proposal']:
        raise ValueError('Same-response A2 native result or support trace differs')
    return result


def choose(item, initial, trace, policy):
    """Declared CPU controls; they never replace the adopted selection policy."""
    interface = r123_module('r2_support_interface')
    keys, none = interface.option_keys(item)
    if policy == 'constant_none':
        return dict(answer=[none] if none else None, deleted=[], applied=none is not None,
                    reason='constant_coverage_control_not_a_support_claim')
    if set(trace) != set(keys):
        raise ValueError('Every substantive option must retain its support trace')
    if policy == 'complete_support':
        answer = r123_module('r2_program_head').assemble(item, initial, trace)
        return dict(answer=answer if answer is not None else deepcopy(initial),
                    applied=answer is not None, reason='original_complete_support_policy')
    if policy not in ('path_delete', 'delete_after_recompute'):
        raise ValueError('Unknown A2 control policy')
    # Match the adopted assembler's initial-set validity, including tuples.
    valid = isinstance(initial, (list, tuple)) and bool(initial) and all(k in item['options'] for k in initial)
    valid = valid and not (none in initial and len(initial) > 1)
    if not valid:
        return dict(answer=deepcopy(initial), deleted=[], applied=False,
                    reason='invalid_initial_retained_without_repair')
    selected = set(initial) - ({none} if none else set())
    deleted = []
    for key in keys:
        if key not in selected:
            continue
        failed_paths = [path['rule_id'] for path in trace[key]['paths'] if path['state'] == 'CONTRADICTED']
        remove = bool(failed_paths) if policy == 'path_delete' else trace[key]['state'] == 'CONTRADICTED'
        if remove:
            selected.remove(key)
            deleted.append(dict(option=key, contradicted_paths=failed_paths))
    answer = [key for key in keys if key in selected] or ([none] if none else None)
    return dict(answer=answer, deleted=deleted, applied=True, reason=policy,
        initial_support_path_attribution='not_observed_or_inferred',
        remaining_paths_recombined=policy == 'delete_after_recompute', additions_allowed=False)


def execution_request(packet, result):
    """Same cleaned facts and scoped rules; no program states or old answer."""
    if not applicable(packet):
        raise ValueError('No finite-rule capability for the current input')
    cfg = config()
    source = next(path for path in cfg['legacy_sources'] if path.endswith('/r2_samefacts_control.py'))
    reasoning = next(path for path in cfg['legacy_sources'] if path.endswith('/r2_samefacts_reasoning.py'))
    program = r123_module('r2_program_head')
    scope = r123_module('r2_action_scope')
    rules = program.relevant_rules(packet.native_input)
    if scope.renal_question(packet.native_input):
        rules = [rule for rule in rules if (program.fields(rule['when']) | program.fields(rule['unless'])) & {'crcl', 'egfr'}]
    namespace = source_function(source, ('expression', 'request'), dict(json=json,
        option_keys=r123_module('r2_support_interface').option_keys,
        obj=r123_module('r2_support_interface').obj,
        relevant_rules=lambda _: rules))
    # The adopted program strips surrounding option whitespace when matching.
    # Retain the exact original option text in the final model payload below.
    item = deepcopy(packet.native_input)
    item['options'] = {key: text.strip() for key, text in item['options'].items()}
    facts = {key: result['facts'][key] for key in sorted(result['facts'])}
    request = namespace['request'](item, dict(action=result['action'], facts=facts), 'readable')
    content = request['messages'][-1]['content']
    payload, end = json.JSONDecoder().raw_decode(content)
    payload['options'] = {key: packet.native_input['options'][key] for key in payload['options']}
    for key, lines in payload['rules_by_option'].items():
        expected = [rule['id'] for rule in rules
                    if item['options'][key].casefold() in rule['drugs'] and rule['action'] == result['action']]
        if [line.split(':', 1)[0] for line in lines] != expected:
            raise ValueError('Model rule payload differs from the adopted scoped program')
        if 'options' in result and expected != [path['rule_id'] for path in result['options'][key]['paths']]:
            raise ValueError('Prepared path identifiers differ from the saved A2 trace')
    prepare = next(node for node in ast.parse(Path(reasoning).read_text()).body
                   if isinstance(node, ast.FunctionDef) and node.name == 'prepare')
    replacements = [node for node in ast.walk(prepare) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and node.func.attr == 'replace'
                    and len(node.args) == 2 and all(isinstance(arg, ast.Constant) for arg in node.args)]
    if len(replacements) != 1:
        raise RuntimeError('Original strong-control instruction replacement changed')
    old, new = (arg.value for arg in replacements[0].args)
    tail = content[end:]
    if tail.count(old) != 1:
        raise RuntimeError('Original execution instruction missing')
    request['messages'][-1]['content'] = json.dumps(payload, ensure_ascii=False) + tail.replace(old, new)
    reject_metadata(payload)
    return request


def parse_execution(raw, method, options_schema, *, parser_policy=STRICT_PARSER):
    """Original final-object extraction, plus explicit finite option validation."""
    execution_policy(parser_policy)
    if parser_policy == NATIVE_PARSER:
        try:
            return historical_parse_execution(raw, method)
        except (ValueError, KeyError, TypeError) as error:
            raise OutputSchemaError(str(error)) from error
    cfg = config()
    source = next(path for path in cfg['legacy_sources'] if path.endswith('/analyze_v5.py'))
    if method not in ('M4', 'M5'):
        raise ValueError('An explicit backbone is required')
    if method == 'M5' and '</think>' not in raw:
        raise OutputSchemaError('Qwen thinking did not close')
    final = raw.split('</think>', 1)[-1] if method == 'M5' else raw
    objects = source_function(source, ('objects',), dict(json=json))['objects']
    parsed = objects(final, 'options')
    if parsed is None:
        raise OutputSchemaError('No unambiguous final options JSON after reasoning')
    try:
        jsonschema.validate(parsed['options'], options_schema)
    except jsonschema.ValidationError as error:
        raise OutputSchemaError(str(error)) from error
    return parsed['options']


def executor_proposal(packet, bundle, raw, event, method, schema, *, parser_policy=STRICT_PARSER):
    """Original state parser/assembler, with truncation retained as unavailable."""
    variant = executor_variant(parser_policy)
    trace = dict(action=bundle['action'], scope=bundle['scope'], facts=bundle['facts'],
        fact_source=bundle['source'], raw_execution=raw, states=None,
        inference_started=True, method_score='not_scored', semantic_invalid=False)
    if parser_policy == NATIVE_PARSER:
        trace.update(parser_policy=parser_policy,
            model_result=dict(complete=event.get('finish_reason') != 'length',
                              finish_reason=event.get('finish_reason')),
            parser_result=dict(status='not_run'), assembler_result=dict(status='not_run'),
            system_fallback=dict(applied=False, reason=None))
    try:
        if event.get('finish_reason') == 'length':
            raise OutputSchemaError('Executor output reached its unchanged token limit')
        states = parse_execution(raw, method, schema, parser_policy=parser_policy)
    except OutputSchemaError as error:
        trace.update(schema_invalid=True, semantic_result='unavailable', error=str(error),
            failure_type='output_truncation' if event.get('finish_reason') == 'length' else 'output_schema')
        if parser_policy == NATIVE_PARSER:
            trace['parser_result'] = dict(status='not_run_truncation' if event.get('finish_reason') == 'length'
                                         else 'error', error=str(error))
        return AgentProposal('A2', variant, packet.input_hash, 'partial', None,
            unresolved=[str(error)], checks=[dict(type='format_validation', name='original_final_option_states',
            passed=False)], trace=trace)
    if parser_policy == NATIVE_PARSER:
        trace['parser_result'] = dict(status='parsed', value=deepcopy(states))
        # Keep strict-v1 compatibility as a diagnostic, never as a native-v2 gate.
        trace['strict_v1_schema_diagnostic'] = dict(valid=jsonschema.Draft7Validator(schema).is_valid(states))
    try:
        options = {key: dict(state=value) for key, value in states.items()}
        answer = r123_module('r2_program_head').assemble(packet.native_input, packet.baseline_answer, options)
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        if parser_policy != NATIVE_PARSER:
            raise
        # A successfully extracted object is not automatically a native answer.
        # Preserve the existing first-error contract; no new failure fallback.
        trace.update(states=states, schema_invalid=True, semantic_result='unavailable',
            failure_type='output_schema', error=str(error),
            assembler_result=dict(status='error', error_type=type(error).__name__, error=str(error)))
        return AgentProposal('A2', variant, packet.input_hash, 'partial', None,
            unresolved=[str(error)], checks=[dict(type='format_validation',
                name='original_state_assembly', passed=False)], trace=trace)
    applied = answer is not None
    native = answer if applied else deepcopy(packet.baseline_answer)
    if parser_policy == NATIVE_PARSER:
        trace['assembler_result'] = dict(status='assembled' if applied else 'no_proposal', answer=answer)
        trace['system_fallback'] = dict(applied=not applied,
            reason=None if applied else 'original_assembler_no_proposal_retains_current_initial')
        actual_keys, _ = r123_module('r2_support_interface').option_keys(packet.native_input)
        trace['ignored_option_keys'] = sorted(set(states) - set(actual_keys))
    trace.update(states=states, schema_invalid=False, applied=applied,
        semantic_result='available' if native is not None else 'unavailable',
        reason='model_support_recomputed' if applied else 'unresolved_support_without_valid_initial_answer')
    claims = [dict(claim_id='cached_A2_fact:' + key, kind='patient_fact', field=key, value=value,
                   scope=bundle['scope'], source=bundle['source'],
                   entailment_status='reused_same_input_model_extraction_not_new_ground_truth')
              for key, value in bundle['facts'].items() if value is not None]
    return AgentProposal('A2', variant, packet.input_hash,
        'supported' if applied else 'partial', native, claims=claims,
        requested_changes=[dict(candidate=key, action='recompute_option_by_model', state=state,
                                conditional_on_cached_facts=True) for key, state in states.items()
                           if parser_policy == STRICT_PARSER or key in actual_keys],
        unresolved=[] if applied else [trace['reason']],
        checks=[dict(type='format_validation', name='original_final_option_states', passed=True),
                dict(type='model_assessment', name='finite_rule_execution', conditional_on_cached_facts=True)],
        trace=trace)


def run_executor(packet, session, method, bundle, *, parser_policy=STRICT_PARSER):
    variant = executor_variant(parser_policy)
    if not applicable(packet):
        if bundle is not None:
            raise ValueError('An unsupported input must not read another input fact cache')
        return AgentProposal('A2', variant, packet.input_hash, 'unsupported', None,
            unresolved=['Outside the retained A2 finite-rule capability'], cost=session.cost_since())
    if bundle is None or bundle['input_hash'] != packet.input_hash:
        raise ValueError('A same-input fact bundle is required')
    reject_metadata({key: bundle[key] for key in ('facts', 'action', 'scope')})
    session.attach_fact_resources(bundle['source']['original_fact_resources'])
    request = execution_request(packet, bundle)
    raw = session.generate_adopted(request['messages'], request['schema'], execution_profile(method),
                                   stage='A2_control:execute_cached_facts')
    proposal = executor_proposal(packet, bundle, raw, session.calls[-1]['event'], method, request['schema'],
                                 parser_policy=parser_policy)
    proposal.cost.update(session.cost_since())
    return proposal
