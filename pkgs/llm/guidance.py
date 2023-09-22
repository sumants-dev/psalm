import guidance
from enum import Enum
from typing import Dict
import json


class ModelProvider(Enum):
    OpenAI = "OpenAI"
    Transformer = "Transformer"


class LLM:
    """
    Our abstraction for interacting with LLMs.
    We will use guidance syntax for issuing commands.
    See here for more details: https://github.com/guidance-ai/guidance/tree/main
    """

    def __init__(self, model_provider: ModelProvider, model_name: str, **model_kwargs):
        if model_provider == ModelProvider.OpenAI:
            guidance.llm = guidance.llms.OpenAI(model_name, **model_kwargs)
        else:
            guidance.llm = guidance.llms.Transformers(model_name, **model_kwargs)

    def prompt(self, guidance_spec: str, **kwargs) -> str:
        program = guidance(guidance_spec)
        return json.dumps(program(**kwargs).variables())
