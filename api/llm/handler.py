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
from pkgs.vector_dbs.pg_vector_store import PgVectorStore
from pkgs.llm.guidance import LLM, ModelProvider

from pkgs.config.setting import Settings

settings = Settings()

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

PlaceholderMessage = models_openai.ChatCompletionMessage(role=models_openai.ChatMessageRole.System, content=PlaceholderSystemPrompt, name=None)


loader = WikiLoader()
rm_stopwords = RemoveStopWords()
sentence_chunker = SentenceChunker(2, 256)
sentence_embedder = SentenceEmbedder("all-MiniLM-L6-v2")
containment_anonymizer = PresidioAnonymizer(
    settings.anonymizer_key,
    0.5,
    EntityResolution.containment,
    [PII_Type.person, PII_Type.email]
)
equality_anonymizer = PresidioAnonymizer(
    settings.anonymizer_key,
    0.5,
    EntityResolution.containment,
    [PII_Type.person, PII_Type.email]
)
deanonimyzer = PresidioDeanonymizer(settings.anonymizer_key)
vector_db = PgVectorStore(settings.postgres_cnxn_str)
llm = LLM(ModelProvider.OpenAI, "text-davinci-003", api_key = settings.open_api_key)


@router.post("/chat/completions")
async def create_chat_completion(
    chat_completion: ChatCompletionSecureRequest,
    full_response: bool = False,
) -> ChatCompletionSecureResponse:

    messages = [PlaceholderMessage] + chat_completion.messages

    containment_anonymizer.transform(messages)


    anonymized_messages = [msg.model_dump(exclude_none=True) for msg in messages]
    completion: typing.Dict = openai.ChatCompletion.create(
         model=chat_completion.model,
         messages=anonymized_messages,
     ) # type: ignore
    
    comp = models_openai.ChatCompletionResponse(
        **completion
    )

    for choice in comp.choices:
        choice.message.content = deanonimyzer._transform(choice.message.content)


    res = ChatCompletionSecureResponse.from_openai_response(
        comp,
        anoymized_queries= messages if full_response else None,
    )

    return res

@router.post("/demo/load_wiki_pages")
async def load_wiki_pages(
    request: DemoDocumentStoreRequest
):
    wiki_pages = [loader.load(page_name) for page_name in request.page_names]

    nodes = [
        node
        for metadata, page in wiki_pages
        for node in sentence_chunker.text_to_nodes(rm_stopwords.transform(page), metadata)
    ]

    sentence_embedder.embed(nodes)

    equality_anonymizer.transform(nodes)

    vector_db.save_nodes(nodes, "Node")

@router.post("/demo/rag")
async def chat_completion_with_rag(
    request: DemoRAGRequest
) -> DemoRAGResponse:
    nodes = [
        Node(request.user_prompt, {"doc": title}, None)
        for title in request.context_titles
    ]

    sentence_embedder.embed(nodes)

    similar_nodes = [
        similar_node
        for node in nodes
        for similar_node, distance in vector_db.find_similar_nodes(node, 'Node', 5)
    ]

    def format_context_nodes(node: Node):
        title = node.metadata["doc"]
        content = deanonimyzer._transform(node.content)
        return f"From the {title} wiki page, {content}"
    
    raw_context = "\n".join(map(format_context_nodes, similar_nodes))
    context = f"Below is useful context. Do not answer the question yet.\n{raw_context}\n---\n"

    json_structure = f"\n---\n```json{request.response_spec}```"

    full_guidance_prompt = RAGSystemPrompt + containment_anonymizer.transform(
        context + request.user_prompt + json_structure
    )

    response = llm.prompt(full_guidance_prompt)

    return {
        "prompt": full_guidance_prompt,
        "llm_response": response,
        "pontus_response": deanonimyzer.transform(response)
    }