import typing
import pydantic
import enum
from pkgs.models import pydantic_openai as models_openai
from pkgs.models.pontus.base import ChatMessage, ChatResponse, OpenAIOptions


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
    provider: Provider | None = None
    model: models_openai.GPT3Models = models_openai.GPT3Models.GPT3Dot5Turbo
    messages: typing.List[ChatMessage]
    titles: typing.List[str] = []
    context_prompt: str = ""
    key_cache_prompt: str | None = None
    options: OpenAIOptions | None = None


class ChatCompletionSecureResponse(ChatResponse):
    raw_request: typing.List[ChatMessage] | None = None


class DemoDocumentStoreRequest(pydantic.BaseModel):
    page_names: typing.List[str]


class DemoRAGRequest(pydantic.BaseModel):
    user_prompt: str
    context_titles: typing.List[str]
    response_spec: str


class DemoRAGResponse(pydantic.BaseModel):
    prompt: str
    llm_response: str
    pontus_response: str
