import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi import security
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

RAGSystemPrompt = (
    "Ensure that all placeholders, including those inside quotes, are enclosed by "
    "the greek letter alpha (α), exactly as I have done in this prompt. You MUST use the greek letter (α) to "
    "indicate placeholders. Use the context below to help answer the question and follow the desired "
    "format accurately."
)

RagSystemPromptMessage = ChatMessage(
    role=ChatMessageRole.System, content=RAGSystemPrompt, name=None
)

from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic(auto_error=False)


@router.post("/chat/completions", tags=["llm"])
async def create_chat_completion(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    chat_completion: ChatCompletionSecureRequest,
    enable_rag: bool = False,
    debug: bool = False,
) -> ChatCompletionSecureResponse:
    session_id = secrets.token_urlsafe(16)
    orch = orchestrator.get_orchestrator()

    if not orch.application.auth.authenticate(credentials=credentials):
        raise HTTPException(status_code=401, detail="Unauthorized")

    cache_hit = get_cache(orch, chat_completion.key_cache_prompt)

    if cache_hit:
        return cache_hit

    context_messages = (
        retrieve_context(
            orchestrator=orch,
            user_prompt=chat_completion.context_prompt,
            titles=chat_completion.titles,
        )
        if enable_rag
        else []
    )

    msgs = chat_completion.messages + context_messages

    anon_msgs = orch.privacy.anoymizer.transform(msgs)

    for msg in anon_msgs:
        raw_content = orch.privacy.token_mapper.set_alias_for_text(
            session_id=session_id, text=msg.content or ""
        )
        msg.content = raw_content

    msgs_to_send = [RagSystemPromptMessage] + anon_msgs
    chat_response = orch.llm.call_llm(
        model=chat_completion.model,
        msgs=msgs_to_send,
        options=chat_completion.options,
        debug=debug,
    )

    for msg in chat_response.messages:
        raw_text = orch.privacy.token_mapper.get_for_text(
            session_id=session_id, text=msg.content or ""
        )
        msg.content = raw_text

    if chat_completion.key_cache_prompt and orch.llm.cache:
        orch.llm.cache.set(
            prompt=orch.privacy.anoymizer.transform(chat_completion.key_cache_prompt),
            record=PromptCacheRecord(
                messages=chat_completion.messages,
                provider_response=chat_response.provider_response,
            ),
        )

    return ChatCompletionSecureResponse(
        messages=orch.privacy.deanoymizer.transform(chat_response.messages),
        provider_response=chat_response.provider_response,
        raw_provider_response=chat_response.raw_provider_response,
        raw_request=msgs_to_send if debug else None,
    )
