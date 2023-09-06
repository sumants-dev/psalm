import pydantic

from pkgs.models import pydantic_openai as models_openai


class ChatCompletionSecureRequest(models_openai.ChatCompletionRequest):
    pass

class ChatCompletionSecureResponse(models_openai.ChatCompletionResponse):
    pass