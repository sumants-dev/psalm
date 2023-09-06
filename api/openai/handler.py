from fastapi import APIRouter
from api.openai.models import ChatCompletionSecureRequest, ChatCompletionSecureResponse
from pkgs.models import pydantic_openai as models_openai

router = APIRouter()

@router.get("v1/chat/completions")
async def create_chat_completion(chat_completion: ChatCompletionSecureRequest) -> ChatCompletionSecureResponse:
    # TODO: Implement
    return ChatCompletionSecureResponse(
        id="id",
        model="model",
        object="object",
        created=0,
        choices=[],
        usage= models_openai.Usage(prompt_tokens=10, completion_tokens=10, total_tokens=10)
    )