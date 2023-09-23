import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi import security
from api.auth.models import ApiCreationReq, ApiCreationRes, ApiDeletionReq, BasicRes
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

http_basic_security = security.HTTPBasic(auto_error=False)


@router.post("/api_key", tags=["auth"])
async def create_api_key(
    credentials: Annotated[security.HTTPBasicCredentials, Depends(http_basic_security)],
    req: ApiCreationReq,
) -> ApiCreationRes:
    ai_orchestrator = orchestrator.get_orchestrator()

    api_key = secrets.token_urlsafe(32)
    if not ai_orchestrator.application.auth.authenticate(
        credentials=credentials, role="admin"
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    is_user_added = ai_orchestrator.application.auth.add_user(
        admin_credentials=credentials,
        new_username=req.username,
        new_password=api_key,
    )

    return ApiCreationRes(username=req.username, api_key=api_key, success=is_user_added)


@router.delete("/api_key", tags=["auth"])
async def delete_api_key(
    credentials: Annotated[security.HTTPBasicCredentials, Depends(http_basic_security)],
    req: ApiDeletionReq,
) -> BasicRes:
    ai_orchestrator = orchestrator.get_orchestrator()

    ok = ai_orchestrator.application.auth.remove_user(
        admin_credentials=credentials, username=req.username
    )

    return BasicRes(success=ok)
