"""Single central agent with shared tools; CPU preparation, no live adoption."""
from dataclasses import asdict,dataclass,field
import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError

from cf_moa.tools import single_agent_tools as toolbox
from cf_moa.tools.adapters import BudgetExceeded,messages_with_instruction,native_json
from cf_moa.tools.schema_compat import OutputSchemaError

CONFIG=Path(__file__).resolve().parents[1]/'configs/single_agent_tools.json'
VARIANT='same_tools_single_agent_v1'


@dataclass
class ControlResult:
    """Controls are not a sixth medical expert or a renamed A1 proposal."""
    input_hash: str
    native_proposal: Any | None
    applicability: str
    cost: dict
    trace: dict
    checks: list[dict]=field(default_factory=list)
    variant: str=VARIANT
    control_id: str='same_tools_single_agent'

    @property
    def agent_id(self):
        return None

    def to_dict(self):
        return asdict(self)


def config():
    return json.loads(CONFIG.read_text())


def policy(stage):
    cfg=config()['generation']
    return dict(seed=cfg['seed'],temperature=cfg['temperature'],max_tokens=cfg[stage+'_max_tokens'])


def choose_schema(names):
    return dict(type='object',properties=dict(tool=dict(type='string',enum=['answer',*names])),
                required=['tool'],additionalProperties=False)


def parse(raw,schema):
    try:
        return native_json(raw,schema)
    except (ValueError,TypeError,ValidationError) as error:
        raise OutputSchemaError(str(error)) from error


def context(packet, resource_data, observations, instruction):
    return messages_with_instruction(packet,
        'You are one agent answering the complete original native task. Use the same legal resources '
        'and tools below. Current-patient facts must come from the current question, not from documents, '
        'options, prior answers, or transformed views. Unknown is not false. Program outputs are '
        'conditional on their stated input and scope; model scores and views are not medical proof. '
        'You may retain or change the answer according to evidence; never force stability or a flip.\n\n'
        'Complete legal resources:\n'+json.dumps(resource_data,ensure_ascii=False)+
        '\n\nYour tool observations for this same input:\n'+json.dumps(observations,ensure_ascii=False)+
        '\n\nCURRENT ACTION:\n'+instruction)


def argument_messages(packet,resource_data,observations,choice,schema,instructions):
    return context(packet,resource_data,observations,
        'Supply only the arguments for the selected tool '+choice+'. The following original '
        'tool instructions define the facts/action semantics. Return the CURRENT argument '
        'schema, not any inline answer fields in the original instructions.\n'+
        json.dumps(instructions,ensure_ascii=False)+'\nCURRENT ARGUMENT SCHEMA:\n'+json.dumps(schema))


def answer_messages(packet,resource_data,observations):
    return context(packet,resource_data,observations,
        'Now answer the complete ORIGINAL task in its native JSON format, preserving every '
        'required auxiliary field. Use all original information and any in-scope tool observations. '
        'Explain uncertainty where appropriate; tool suggestions are not an instruction to keep or change an answer.')


def run(packet,session,*,method):
    checkpoint=session.checkpoint()
    resource_data=toolbox.resources(packet,method)
    available=toolbox.capabilities(packet)
    observations=[]
    trace=dict(capabilities=dict(available),decisions=[],observations=observations,schema_invalid=False,
        semantic_invalid=False,semantic_result='unavailable',method_score='not_scored',
        budget_exhausted=False,tool_profile_scope=config()['readout_engine'])

    def unavailable(error,kind,*,schema=False):
        trace.update(failure_type=kind,failure_detail=str(error),schema_invalid=schema,
            inference_started=any('event' in call for call in session.calls[checkpoint[0]:]))
        return ControlResult(packet.input_hash,None,'partial',session.cost_since(checkpoint),trace,
            [dict(type='format_validation',name='single_agent_native_contract',passed=not schema)])

    try:
        for _ in range(min(config()['maximum_tool_actions'],packet.budget.max_tool_calls)):
            if not available:break
            raw=session.generate(context(packet,resource_data,observations,
                'Choose one available tool worth using next, or answer if ready. Prefer the finite '
                'rules or supplied-model executor when applicable. A tool can be used once; all '
                'calls share the original budget. Return only the choice JSON.\n'+json.dumps(available)),
                choose_schema(available),**policy('choose'),stage='single_agent:choose')
            choice=parse(raw,choose_schema(available))['tool']
            trace['decisions'].append(dict(raw_response=raw,choice=choice))
            if choice=='answer':break
            schema,instructions=toolbox.argument_contract(packet,choice)
            arguments={}
            if schema['properties']:
                raw=session.generate(argument_messages(packet,resource_data,observations,choice,schema,instructions),
                    schema,**policy('arguments'),stage='single_agent:arguments:'+choice,
                    decoding_revision=config()['tool_argument_decoding_revision'])
                arguments=parse(raw,schema)
                trace['decisions'][-1]['raw_arguments']=raw
            observation=toolbox.execute_tool(packet,method,choice,arguments,session,view_policy=policy('view'))
            observations.append(dict(tool=choice,arguments=arguments,observation=observation))
            del available[choice]
        raw=session.generate(answer_messages(packet,resource_data,observations),
            packet.answer_schema,**policy('answer'),stage='single_agent:native_answer')
        trace['raw_response']=raw
        native=parse(raw,packet.answer_schema)
    except BudgetExceeded as error:
        trace['budget_exhausted']=True
        return unavailable(error,'budget_capacity_unavailable')
    except toolbox.ToolSemanticError as error:
        trace['semantic_invalid']=True
        return unavailable(error,'tool_semantic_invalid')
    except OutputSchemaError as error:
        # No format-repair call, alternate parser, or baseline substitution.
        return unavailable(error,'single_agent_contract_invalid',schema=True)
    trace.update(semantic_result='native_answer_available',inference_started=True)
    return ControlResult(packet.input_hash,native,'supported',session.cost_since(checkpoint),trace,
        [dict(type='format_validation',name='native_format',passed=True),
         dict(type='model_assessment',name='single_agent_final_decision_with_scoped_tools')])
