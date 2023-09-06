import typing
import pydantic
import enum
from pkgs.models import pydantic_openai as models_openai


class Provider(str, enum.Enum):
    openai = "openai"

class ChatCompletionSecureRequest(pydantic.BaseModel):
    provider: Provider
    model: models_openai.GPT3Models = models_openai.GPT3Models.GPT3Dot5Turbo
    messages:  typing.List[models_openai.ChatCompletionMessage]


class ChatCompletionSecureResponse(models_openai.ChatCompletionResponse):
    anoymized_queries: typing.List[models_openai.ChatCompletionMessage] | None = None
