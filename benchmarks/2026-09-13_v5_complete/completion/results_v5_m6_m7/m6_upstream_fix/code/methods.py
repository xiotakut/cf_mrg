"""Paper-aligned i-MedRAG and TC-RAG control flow; no benchmark gold imports."""
import ast
import json
import math
import re
from concurrent.futures import ThreadPoolExecutor
from common import question_text, json_object, valid_answer, visible
from runtime import RequestFailure

IMED_SYSTEM = 'You are a helpful medical assistant, and your task is to answer the given question following the instructions given by the user. '
ASK = 'Please first analyze all the information in a section named Analysis (## Analysis). Then, use key terms from previous answers to form specific and direct questions. Generate {} concise, context-specific queries to search for additional information in an external knowledge base, in a section named Queries (## Queries). Each query should be simple and focused, directly relating to the key terms used in the answers. Wait for responses from the user before proceeding.'
FINAL = 'Please first think step-by-step to analyze all the information in a section named Analysis (## Analysis). Then, please provide your answer in a section named Answer (## Answer).'
RAG_SYSTEM = 'You are a helpful medical expert, and your task is to answer a medical question using the relevant documents.'


def messages(system, text):
    return [dict(role='system', content=system), dict(role='user', content=text)]


def history_text(history):
    return '\n\n'.join(f'Query: {q["query"]}\nAnswer: {q["answer"]}' for q in history)


def final_json(raw, session, stage):
    """Convert the upstream single-quoted literal example to JSON, without inference."""
    try:
        json_object(raw, 'answer')
        return raw
    except ValueError:
        if not session.config['format_repairs']:
            return raw
    text = raw.strip()
    fence = re.fullmatch(r'```(?:json|python)?\s*\n(.*?)\n```', text, re.S | re.I)
    if fence:
        text = fence[1]
    try:
        tree = ast.parse(text, mode='eval')
        if not isinstance(tree.body, ast.Dict):
            return raw
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = [ast.literal_eval(key) for key in node.keys]
                if any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
                    return raw
        value = ast.literal_eval(tree)
        if 'answer' not in value:
            return raw
        repaired = json.dumps(value, ensure_ascii=False, allow_nan=False)
        if json.loads(repaired) != value:
            return raw
    except (SyntaxError, ValueError, TypeError, RecursionError):
        return raw
    session.event('answer_syntax_repair', stage=stage, raw_response=raw,
                  repaired_response=repaired, algorithm='literal_dict_to_json_v1',
                  repairs=1, llm_calls=0)
    return repaired


def parse_queries(raw, original):
    values = json_object(raw, 'output')['output']
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise ValueError('output_must_be_string_list')
    # Upstream consumes the extractor's list without a verbatim-source gate.
    # Keep JSON/type validation; strip only upstream's numbered-list prefix.
    queries, empty = [], []
    for index, value in enumerate(values):
        query = re.sub(r'^\d+\.\s*', '', value.strip())
        if query.strip():
            queries.append(dict(index=index, query=query))
        else:
            empty.append(index)
    return queries, empty


def imedrag(item, session):
    item, config = visible(item), session.config
    history, issues = [], []
    question = question_text(item)
    for rnd in range(config['n_rounds']):
        before = list(history)
        asked = session.call(f'query/{rnd}', messages(IMED_SYSTEM, history_text(history) + '\n\n' + question + '\n\n' + ASK.format(config['n_queries'])))
        queries, empty, parse_status = [], [], 'missing_queries_section'
        if '## Queries' in asked['text']:
            parse_prompt = f'Parse the following passage and extract the queries as a list: {asked["text"]}.\n\nPresent the queries as they are. DO NOT merge or break down queries. Output the list of queries in JSON format: {{"output": ["query 1", ..., "query N"]}}'
            parsed = session.call(f'parse/{rnd}', [dict(role='user', content=parse_prompt)])
            for repair in range(config['format_repairs'] + 1):
                try:
                    queries, empty = parse_queries(parsed['text'], asked['text'])
                    parse_status = 'ok' if queries else 'empty_queries'
                    break
                except ValueError as e:
                    parse_status = str(e)
                    if repair == config['format_repairs'] or parse_status in ('query_not_verbatim_or_out_of_order', 'query_fragment_or_merge'):
                        break
                    parsed = session.call(f'parse/{rnd}/format_repair/{repair}',
                        [dict(role='user', content='Repair only JSON syntax in the following text. Preserve every query string and its order; do not solve or add a question. Return {"output": [...]} with ASCII JSON delimiters.\n' + parsed['text'])])
        if parse_status != 'ok':
            issues.append(dict(round=rnd, status=parse_status))
        session.event('imedrag_queries', round=rnd, history_before=before,
                      requested=config['n_queries'], actual=len(queries), empty_indices=empty,
                      parse_status=parse_status, queries=queries)
        qa_prompts, valid_queries = [], []
        for entry in queries:
            stage = f'qa/{rnd}/{entry["index"]}'
            try:
                docs = session.retrieve(stage, entry['query'])
                context = session.context(docs, stage)
                qa_prompts.append(messages(RAG_SYSTEM, f'Here are the relevant documents:\n{context}\nHere is the question:\n{entry["query"]}'))
                valid_queries.append(entry)
            except RequestFailure as e:
                issues.append(dict(round=rnd, query_index=entry['index'], status='retrieval_failed', error=str(e)))
        if qa_prompts:
            # Each completed QA has its own durable receipt. The backend may
            # batch their tensors, while writeback waits in original query order.
            with ThreadPoolExecutor(max_workers=len(qa_prompts)) as pool:
                futures = [pool.submit(session.call, f'qa/{rnd}/{entry["index"]}', prompt)
                           for entry, prompt in zip(valid_queries, qa_prompts)]
                for entry, future in zip(valid_queries, futures):
                    try:
                        answer = future.result()
                    except RequestFailure as e:
                        issues.append(dict(round=rnd, query_index=entry['index'], status='qa_failed', error=str(e)))
                        continue
                    if not answer['text'].strip():
                        issues.append(dict(round=rnd, query_index=entry['index'], status='empty_qa_answer'))
                        continue
                    history.append(dict(round=rnd, query_index=entry['index'], query=entry['query'], answer=answer['text']))
                    session.event('imedrag_qa', **history[-1], finish_reason=answer['finish_reason'])
        session.event('imedrag_round', round=rnd, history_before=before,
                      history_after=list(history), executed=len(history) - len(before))
    final_messages = messages(IMED_SYSTEM, history_text(history) + '\n\n' + question + '\n\n' + FINAL)
    final = session.call('final', final_messages)
    session.event('imedrag_final', history=list(history), response=final['text'])
    if '## Answer' not in final['text'] and 'answer is' not in final['text'].lower():
        return dict(raw_response=final['text'], status='invalid', termination='missing_final_answer', issues=issues)
    # Pinned i-MedRAG formatter, adapting only the native answer space.
    hint = ' (' + '/'.join(item['options']) + ')' if item['options'] else ''
    if item['answer_format'] == 'multi':
        hint = ' (a JSON array of option key strings from ' + '/'.join(item['options']) + ')'
    elif item['answer_format'] == 'relation':
        hint = ' (higher/lower/no difference/uncertainty)'
    format_request = "Output the answer in JSON: {'answer': your_answer" + hint + "}"
    if item['answer_format'] == 'diagnosis':
        format_request += ' The answer value must be a JSON string containing the diagnosis already given.'
    if item['answer_format'] == 'robustness_single':
        format_request += ' Also preserve the existing "errors" array as a top-level field.'
    final_messages = final_messages + [dict(role='assistant', content=final['text']), dict(role='user', content=format_request)]
    formatted = session.call('format', final_messages)
    answer = final_json(formatted['text'], session, 'format')
    error = valid_answer(answer, item)
    # Upstream skips failed query parsing rounds and still returns its final answer.
    status = 'invalid' if error else 'ok'
    if any(x['status'] in ('qa_failed', 'retrieval_failed') for x in issues):
        status = 'failed'
    return dict(raw_response=answer, status=status, termination='final_formatted',
                answer_error=error, issues=issues, rounds=config['n_rounds'], executed_queries=len(history))


TC_SYSTEM = '''Use the available tools to help answer the question. Your knowledge may be incomplete.
Tool: DOC_RAG. Search the frozen medical document collection. Action Input must be a JSON object {"query": "a focused search query"}.
Use these explicit action labels:
Thought: reasoning about the question and active memory.
Plan: a plan for subsequent actions.
Action: DOC_RAG
Action Input: {"query": "..."}
Observation: supplied by the tool, never generated by you.
Backtrack: explain why the top memory entry is unhelpful; the program will remove it and restore its preceding state.
Summary: a concise replacement for the TOP memory entry; the program will replace the old entry with this summary.
Final Answer: the answer to the original question, as JSON with an "answer" field in its required native format (and "errors" when required).
Produce one action per turn, optionally preceded by Thought. After Action Input stop and wait for the real tool result. You may inspect all active memory but Backtrack and Summary operate only on its top. The original question cannot be removed. Use retrieval when you need information. A proposed final answer may be reclassified as Thought by the state monitor; then continue reasoning or using tools.
'''


def state_signal(response):
    tokens, entropies = response['tokens'], response['entropies']
    if response.get('score_convention') != 'full_vocab_HF_post_processors_nats_eps1e-10_fp32':
        raise ValueError('unverified_entropy_convention')
    if not entropies or len(entropies) != len(tokens) or any(not math.isfinite(v) or v < -1e-5 for v in entropies):
        raise ValueError('invalid_distribution_entropy')
    start, match = 0, 'no_exact_header_match'
    # Deliberately preserve the pinned upstream selector including whitespace and
    # range boundaries. It selects a suffix, not just the semantic answer body.
    for i in range(len(tokens) - 3):
        if tokens[i] == 'Thought':
            start, match = i + 2, 'Thought'
            break
        if tokens[i] == 'Final':
            match = 'Final_without_exact_Answer'
            if tokens[i + 1] == 'Answer':
                start, match = i + 3, 'Final_Answer'
            break
    if start >= len(tokens) - 1:
        start, match = 0, 'upstream_boundary_fallback'
    positions = response['useful_positions'][start:]
    return dict(value=sum(entropies[start:]), start=start, match=match,
                selected_positions=positions, selected_tokens=tokens[start:],
                selected_entropies=entropies[start:], aggregation='sum', log_base='e',
                convention=response['score_convention'])


def parse_action(raw):
    # Discard invented observations and EVERYTHING following them before action
    # dispatch. The unmodified output stays in the model request receipt.
    clean = re.split(r'(?im)^\s*Observation\s*:', raw, maxsplit=1)[0]
    marks = list(re.finditer(r'(?im)^\s*(Thought|Plan|Action Input|Action|Backtrack|Summary|Final Answer)\s*:', clean))
    parts = [(m.group(1).lower(), clean[m.end():marks[i + 1].start() if i + 1 < len(marks) else len(clean)].strip()) for i, m in enumerate(marks)]
    if not parts:
        raise ValueError('missing_action_label')
    # Upstream prioritizes Backtrack over simultaneous tool actions.
    for key in ('backtrack', 'summary'):
        found = next((v for k, v in parts if k == key), None)
        if found is not None:
            if not found:
                raise ValueError('empty_' + key)
            return key, found, None
    actions = [(k, v) for k, v in parts if k not in ('thought', 'action input')]
    if len(actions) > 1:
        # Use the first actual action; never execute model-invented later tools.
        actions = actions[:1]
    thought = '\n'.join(v for k, v in parts if k == 'thought')
    if not actions:
        if not thought:
            raise ValueError('empty_thought')
        return 'thought', thought, None
    kind, value = actions[0]
    if kind == 'action':
        if value != 'DOC_RAG':
            raise ValueError('unknown_tool:' + value)
        args = next((v for k, v in parts if k == 'action input'), '')
        obj = json_object(args, 'query')
        if set(obj) != {'query'} or not isinstance(obj['query'], str) or not obj['query'].strip():
            raise ValueError('invalid_tool_query')
        return 'tool', obj['query'], thought
    if not value:
        raise ValueError('empty_action')
    return kind, value, thought


def tcrag(item, session):
    item, config = visible(item), session.config
    # State lives only inside this invocation. Every stack entry has a snapshot.
    stack = [dict(kind='question', text=question_text(item), state=100000.0)]
    state, issues = 100000.0, []
    backtracks = summaries = retrievals = 0
    for step in range(config['max_loop']):
        before, prior_state = list(stack), state
        prompt = '\n\n'.join(e['kind'].title() + ': ' + e['text'] for e in stack)
        response = session.call(f'action/{step}', messages(TC_SYSTEM, prompt), entropy=True)
        try:
            kind, value, thought = parse_action(response['text'])
        except ValueError as e:
            session.event('tc_parse_failed', step=step, error=str(e), stack_before=before)
            return dict(raw_response=response['text'], status='invalid', termination='action_parse_failed', issues=[str(e)], steps=step + 1)
        signal = state_signal(response) if kind in ('thought', 'final answer') or thought else None
        removed, accepted, rejected = [], False, None
        if kind in ('backtrack', 'summary'):
            if len(stack) == 1:
                issues.append(dict(step=step, status='immutable_question'))
            else:
                removed = [stack.pop()]
                state = stack[-1]['state']
                if kind == 'summary':
                    # Replacing a Thought also removes its entropy contribution.
                    # Summary is not a monitored action in the paper.
                    stack.append(dict(kind='summary', text=value, state=state))
                    summaries += 1
                else:
                    backtracks += 1
        elif kind == 'final answer':
            state = signal['value']
            accepted = step >= config['topK'] and state < config['sigma']
            rejected = None if accepted else 'minimum_steps' if step < config['topK'] else 'entropy_threshold'
            # Before topK the pinned executor retains the original Thought
            # prefix while reclassifying the premature conclusion as Thought.
            memory = thought + '\n\n' + value if thought and step < config['topK'] else value
            stack.append(dict(kind='final answer' if accepted else 'thought', text=memory, state=state))
        else:
            if kind == 'thought' or thought:
                state = signal['value']
                stack.append(dict(kind='thought', text=value if kind == 'thought' else thought, state=state))
            if kind == 'tool':
                docs = session.retrieve(f'action/{step}', value)
                context = session.context(docs, f'action/{step}')
                stack.append(dict(kind='tool_observation', text=f'Action: DOC_RAG\nAction Input: {{"query": {__import__("json").dumps(value)}}}\nObservation: {context}', state=state))
                retrievals += 1
            elif kind == 'plan':
                stack.append(dict(kind='plan', text=value, state=state))
        session.event('tc_action', step=step, action=kind, content=value, stack_before=before,
                      stack_after=list(stack), removed=removed, state_before=prior_state,
                      state_after=state, state_signal=signal, sigma=config['sigma'],
                      accepted=accepted, rejected=rejected)
        if accepted:
            answer = final_json(value, session, f'action/{step}')
            error = valid_answer(answer, item)
            return dict(raw_response=answer, status='invalid' if error else 'ok', termination='accepted',
                        answer_error=error, issues=issues, steps=step + 1,
                        backtracks=backtracks, summaries=summaries, retrievals=retrievals)
    # Keep the actual returned stack top, but never score an Observation or a
    # rejected Thought as an accepted final answer. No post-budget generation.
    return dict(raw_response=stack[-1]['text'], status='invalid', termination='budget_exhausted',
                returned_kind=stack[-1]['kind'], steps=config['max_loop'], issues=issues,
                backtracks=backtracks, summaries=summaries, retrievals=retrievals)


METHODS = {'imedrag': imedrag, 'tcrag': tcrag}
