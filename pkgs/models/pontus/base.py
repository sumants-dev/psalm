from pydantic import BaseModel
from typing import Dict, List
from typing_extensions import NotRequired, TypedDict
from enum import Enum
from pkgs.models.pydantic_openai.src.chat import (
    ChatCompletionResponse,
    ChatCompletionMessage,
)

from pkgs.models import pydantic_openai


class Provider(str, Enum):
    openai = "openai"


class ChatMessageRole(str, Enum):
    User = "user"
    System = "system"
    Assistant = "assistant"
    Function = "function"

    @staticmethod
    def from_open_ai_role(role: pydantic_openai.ChatMessageRole) -> "ChatMessageRole":
        match role:
            case pydantic_openai.ChatMessageRole.User:
                return ChatMessageRole.User
            case pydantic_openai.ChatMessageRole.System:
                return ChatMessageRole.System
            case pydantic_openai.ChatMessageRole.Assistant:
                return ChatMessageRole.Assistant
            case pydantic_openai.ChatMessageRole.Function:
                return ChatMessageRole.Function
            case _:
                raise ValueError(f"Unknown role: {role}")


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, str]


class ChatMessage(BaseModel):
    role: ChatMessageRole
    content: str | None = None
    name: str | None = None
    function: FunctionCall | None = None

    @classmethod
    def from_openai_message(
        cls, message: pydantic_openai.ChatCompletionMessage
    ) -> "ChatMessage":
        return cls(
            role=ChatMessageRole.from_open_ai_role(message.role),
            content=message.content,
            name=message.name,
        )


class OpenAIOptions(TypedDict):
    temperature: NotRequired[float]
    top_p: NotRequired[float]
    frequency_penalty: NotRequired[float]
    max_tokens: NotRequired[int]
    frequency_penalty: NotRequired[float]


class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    deanoymized_provider_response: ChatCompletionResponse
    raw_provider_response: ChatCompletionResponse | None = None


class ProviderType(str, Enum):
    openai = "openai"
