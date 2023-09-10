import typing
import pydantic
import enum
from pkgs.models import pydantic_openai as models_openai
from pkgs.toxicity.toxicity import check_toxicity


class Provider(str, enum.Enum):
    openai = "openai"


class PontusChatCompletionMetadata(pydantic.BaseModel):
    is_toxic: bool = False

class PontusChatCompletionMessage(models_openai.ChatCompletionMessage):
    metadata: PontusChatCompletionMetadata | None = None

    @classmethod
    def from_openai_message(
        cls, 
        message: models_openai.ChatCompletionMessage,
        metadata: PontusChatCompletionMetadata | None = None,
    ) -> "PontusChatCompletionMessage":
        return cls(
            role=message.role,
            content=message.content,
            name=message.name,
            metadata=metadata,
        )

class PontusChatCompletionChoice(models_openai.ChatCompletionChoice):
    message: PontusChatCompletionMessage

class ChatCompletionSecureRequest(pydantic.BaseModel):
    provider: Provider
    model: models_openai.GPT3Models = models_openai.GPT3Models.GPT3Dot5Turbo
    messages:  typing.List[models_openai.ChatCompletionMessage]


class ChatCompletionSecureResponse(models_openai.ChatCompletionResponse):
    anoymized_queries: typing.List[models_openai.ChatCompletionMessage] | None = None
    choices: typing.List[PontusChatCompletionChoice]

    @classmethod
    def from_openai_response(
        cls, 
        response: models_openai.ChatCompletionResponse,
        anoymized_queries: typing.List[models_openai.ChatCompletionMessage] | None = None,
    ) -> "ChatCompletionSecureResponse":

        choices = [ 
            PontusChatCompletionChoice(
                index=c.index,
                message= PontusChatCompletionMessage.from_openai_message(
                    message=c.message,
                    metadata=PontusChatCompletionMetadata(is_toxic=check_toxicity(c.message.content))
                ),
                finish_reason=c.finish_reason,
            ) for c in response.choices
        ]

        return cls(
            id = response.id,
            object = response.object,
            created = response.created,
            model = response.model,
            choices = choices,
            usage = response.usage,
            anoymized_queries=anoymized_queries,
        )