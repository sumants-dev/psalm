from fastapi import APIRouter
from api.llm.models import (
    ChatCompletionSecureRequest,
    ChatCompletionSecureResponse,
)
from pkgs.cache.caching import PromptCacheRecord


from pkgs.orchestrator import orchestrator

from pkgs.models.pontus.base import ChatMessage, ChatMessageRole

from pkgs.config.setting import getSettings

from api.llm.helpers import get_cache, retrieve_context

settings = getSettings()

router = APIRouter()

PlaceholderSystemPrompt = (
    "Ensure that all placeholders, including those inside quotes, are enclosed by the greek letter alpha (α), "
    "exactly as I have done in this prompt. You MUST use the greek letter (α) to indicate placeholders."
    "Do not include any additional text or explanations. Simply follow this format accurately."
)
RAGSystemPrompt = (
    "Ensure that all placeholders, including those inside quotes, are enclosed by"
    "the greek letter alpha (α), exactly as I have done in this prompt. You MUST use the greek letter (α) to "
    "indicate placeholders. Use the context below to help answer the question and follow the desired "
    "format accurately."
)

RagSystemPromptMessage = ChatMessage(
    role=ChatMessageRole.System, content=RAGSystemPrompt, name=None
)


@router.post("/chat/completions", tags=["llm"])
async def create_chat_completion(
    chat_completion: ChatCompletionSecureRequest,
    enable_rag: bool = False,
    debug: bool = False,
) -> ChatCompletionSecureResponse:
    ai_orchestrator = orchestrator.get_orchestrator()

    cache_hit = get_cache(ai_orchestrator, chat_completion.key_cache_prompt)

    if cache_hit:
        return cache_hit

    context_messages = (
        retrieve_context(
            ai_orchestrator,
            chat_completion.context_prompt,
            chat_completion.titles,
        )
        if enable_rag
        else []
    )

    msgs = [RagSystemPromptMessage] + chat_completion.messages + context_messages

    chat_response = ai_orchestrator.llm.call_llm(
        model=chat_completion.model,
        msgs=msgs,
        options=chat_completion.options,
        debug=debug,
    )

    if chat_completion.key_cache_prompt and ai_orchestrator.llm.cache:
        ai_orchestrator.llm.cache.set(
            prompt=chat_completion.key_cache_prompt,
            record=PromptCacheRecord(
                messages=chat_response.messages,
                provider_response=chat_response.provider_response,
            ),
        )

    return ChatCompletionSecureResponse(
        messages=chat_response.messages,
        provider_response=chat_response.provider_response,
        raw_provider_response=chat_response.raw_provider_response,
        raw_request=msgs if debug else None,
    )
