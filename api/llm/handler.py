import typing
from fastapi import APIRouter
from api.llm.models import ChatCompletionSecureRequest, ChatCompletionSecureResponse, DemoDocumentStoreRequest, DemoRAGRequest, DemoRAGResponse

from pkgs.models import pydantic_openai as models_openai
from pkgs.modifiers.anonymity.presidio_anonymizer import PresidioAnonymizer, PresidioDeanonymizer, PII_Type, EntityResolution
import openai

from pkgs import Node
from pkgs.loaders.wiki_loader import WikiLoader
from pkgs.modifiers.stop_words.remove_stop_words import RemoveStopWords
from pkgs.modifiers.anonymity.presidio_anonymizer import PresidioAnonymizer, PresidioDeanonymizer, PII_Type, EntityResolution
from pkgs.chunkers.sentence_chunker import SentenceChunker
from pkgs.embedders.sentence_embedder import SentenceEmbedder
from pkgs.orchestrator import orchestrator

from pkgs.models.pontus.base import ChatMessage, ChatMessageRole
from pkgs.vector_dbs.pg_vector_store import PgVectorStore
from pkgs.llm.guidance import LLM, ModelProvider

from pkgs.config.setting import Settings, getSettings

from api.llm.helpers import retrieve_context

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
    role=ChatMessageRole.System, 
    content=RAGSystemPrompt, 
    name=None
)



@router.post("/chat/completions", tags=["llm"])
async def create_chat_completion(
    chat_completion: ChatCompletionSecureRequest,
    enable_rag: bool = False,
    debug: bool = False,
) -> ChatCompletionSecureResponse:
    ai_orchestrator = orchestrator.get_orchestrator()

    context_messages = [retrieve_context(ai_orchestrator, chat_completion.context_prompt, chat_completion.titles)] if enable_rag else []

    transformed_messages = [RagSystemPromptMessage] + ai_orchestrator.pre_process(
        chat_completion.messages + context_messages
    )

    chat_response = ai_orchestrator.call_llm(
        model=chat_completion.model, 
        msgs=transformed_messages,
        options=chat_completion.options,
        debug=debug,
    )


    return ChatCompletionSecureResponse(
        messages=chat_response.messages,
        deanoymized_provider_response=chat_response.deanoymized_provider_response,
        raw_provider_response=chat_response.raw_provider_response,
        raw_request=transformed_messages if debug else None,
    )
