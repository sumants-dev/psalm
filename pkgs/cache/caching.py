from pkgs.models.pontus.base import ChatMessage
from pkgs.models.pydantic_openai.src.chat import ChatCompletionResponse
from pydantic import BaseModel
import typing


class PromptCacheRecord(BaseModel):
    messages: typing.List[ChatMessage] = []
    provider_response: ChatCompletionResponse


class PromptCache:
    def cache(self, prompt: str):
        raise NotImplementedError()

    def set(self, prompt: str, record: PromptCacheRecord) -> bool:
        raise NotImplementedError()

    def get(self, prompt: str) -> PromptCacheRecord:
        raise NotImplementedError()

    def create(self) -> None:
        raise NotImplementedError()

    def destroy(self) -> None:
        raise NotImplementedError()
