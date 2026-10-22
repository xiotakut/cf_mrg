"""Upstream response parsing, with the same SciPy entropy batched by token."""
from typing import List,Dict,Any
from openai.types.chat.chat_completion import ChatCompletion
import numpy as np
from scipy.stats import entropy

def process_response(response: ChatCompletion) -> List[Dict[str, Any]]:
    responses = []
    for choice in response.choices:
        tokens = [cont.token for cont in choice.logprobs.content]
        if 'token_id:' in tokens[0]:
            try:
                think_rindex = len(tokens) - tokens[::-1].index('token_id:151668')  # </think> token
            except ValueError:
                think_rindex = 0
        else:
            try:
                think_rindex = len(tokens) - tokens[::-1].index('</think>')  # </think> token
            except ValueError:
                think_rindex = 0
        text = choice.message.content
        top = [[entry.logprob for entry in cont.top_logprobs] for cont in choice.logprobs.content[think_rindex:]]
        token_entropies = entropy(np.exp(top), axis=1).tolist() if top and len({len(row) for row in top}) == 1 else [entropy(np.exp(row)) for row in top]
        logprobs = [cont.logprob for cont in choice.logprobs.content[think_rindex:]]
        # entropies = [-cont.logprob * math.exp(cont.logprob) for cont in choice.logprobs.content]
        # top_logprobs = [[top_logprobs.logprob for top_logprobs in cont.top_logprobs] for cont in choice.logprobs.content]
        responses.append({
            'text': text,
            # 'entropies': entropies,
            'token_entropies': token_entropies,
            'logprobs': logprobs,
            # 'top_logprobs': top_logprobs,
            # 'tokens': tokens,
        })

    return responses
