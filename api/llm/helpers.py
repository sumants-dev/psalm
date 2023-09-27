import logging
import typing
from api.llm.models import ChatCompletionSecureResponse


from pkgs import Node

from pkgs.models.pontus.base import ChatMessage, ChatMessageRole
from pkgs.orchestrator.orchestrator import Orchestrator


def retrieve_context(
    orchestrator: Orchestrator, user_prompt: str, titles: typing.List[str]
) -> typing.List[ChatMessage]:
    nodes = [
        Node(content=user_prompt, metadata={"doc": title}, embedding=None)
        for title in titles
    ]

    orchestrator.doc_store.embedder.embed(nodes)

    similar_nodes = orchestrator.doc_store.find_context_nodes(
        nodes=nodes,
        # TODO: go back to 5 from 1
        max_nodes=3,
    )

    def format_context_nodes(node: Node):
        # NOTE: we deanomize here and then reanoyimize in the handler
        nd = orchestrator.privacy.deanoymizer.transform(node)
        title = nd.metadata["doc"]
        content = nd.content
        return f"From the document with the title {title}, {content}"

    raw_context = "\n".join(map(format_context_nodes, similar_nodes))
    context = f"Below is useful context. Do not answer the question yet.\n{raw_context}\n---\n"

    return [ChatMessage(role=ChatMessageRole.System, content=context)]


def get_cache(
    ai_orchestrator: Orchestrator, key_cache_prompt: str | None
) -> ChatCompletionSecureResponse | None:
    if not ai_orchestrator.llm.cache or not key_cache_prompt:
        print("Cache is not set or key prompt is not found")
        return None

    cache_record = ai_orchestrator.llm.cache.get(
        key_cache_prompt
    )


    if cache_record:
        return ChatCompletionSecureResponse(
            messages=cache_record.messages,
            provider_response=cache_record.provider_response,
            raw_provider_response=None,
            raw_request=None,
        )
