import random
import time

import backoff
from openai import OpenAI
import os
import numpy as np

api_list = [
'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
]
api_nums = len(api_list)


class GPTAgent():
    def __init__(self, model):
        """
        :param model: The model to use for completion.
        """
        self.model = model


    @backoff.on_exception(
        backoff.fibo,
        # https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        (
            # openai.APIError,
            # openai.Timeout,
            # openai.RateLimitError,
            # openai.APITimeoutError,
            # openai.APIConnectionError,
            KeyError,
        ),
    )
    def __call__(self, message, max_tokens, temperature, stop_words):
        """
        :param user_prompt: The user requirments.
        :param max_tokens: The maximum number of tokens to generate.
        :param temperature: The sampling temperature.
        :param stop: The stop sequence or a list of stop sequences.
        :return: Return the response and the usage of the model.
        """
        sleep_time = random.uniform(0.1, 0.2)
        time.sleep(sleep_time)
        s = ("sdfgh\n```python\ndef solution(stdin: str) -> str:\n    my_list = [1, 2, 3]\n    value = my_list[4]\n"
             "    return \"1\"\n```\nsss\n")
        #return s, 0, 0
        api_key = api_list[np.random.randint(0, api_nums)]
        # openai.api_key = api_key
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=message,
            max_tokens=max_tokens,
            temperature=temperature,
            # stop=stop_words,
        )
        return response.choices[0].message.content, response.usage.completion_tokens, response.usage.prompt_tokens


