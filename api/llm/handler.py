import typing
from fastapi import APIRouter
from api.llm.models import ChatCompletionSecureRequest, ChatCompletionSecureResponse

from pkgs.models import pydantic_openai as models_openai
from pkgs.privacy.anonymizer import DefaultAnonymizer, PII_Type
import openai

from pkgs.config.setting import Settings

settings = Settings()

router = APIRouter()

PlaceholderSystemPrompt = (
    "Ensure that all placeholders, including those inside quotes, are enclosed by the greek letter alpha (α), "
    "exactly as I have done in this prompt. You MUST use the greek lette (α) to indicate placeholders."
    "Do not include any additional text or explanations. Simply follow this format accurately."
)

PlaceholderMessage = models_openai.ChatCompletionMessage(role=models_openai.ChatMessageRole.System, content=PlaceholderSystemPrompt, name=None)

@router.post("/chat/completions")
async def create_chat_completion(
    chat_completion: ChatCompletionSecureRequest,
    full_response: bool = False,
) -> ChatCompletionSecureResponse:

    anonymizer = DefaultAnonymizer(
        key=settings.anonymizer_key, 
        pii_types=[PII_Type.phone, PII_Type.email, PII_Type.person, PII_Type.place]
    )

    messages = [PlaceholderMessage] + chat_completion.messages

    for message in messages:
        message.content = anonymizer.anonymize(message.content)


    anonymized_messages = [msg.model_dump(exclude_none=True) for msg in messages]
    completion: typing.Dict = openai.ChatCompletion.create(
         model=chat_completion.model,
         messages=anonymized_messages,
     ) # type: ignore
    
    comp = models_openai.ChatCompletionResponse(
        **completion
    )

    for choice in comp.choices:
        choice.message.content = anonymizer.deanonymize(choice.message.content)


    res = ChatCompletionSecureResponse(
        **comp.model_dump(exclude_none=True),
    )
    if full_response:
        res.anoymized_queries = messages


    return res