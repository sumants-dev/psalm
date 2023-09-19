
import typing


from pkgs import Node

from pkgs.models.pontus.base import ChatMessage, ChatMessageRole
from pkgs.orchestrator.orchestrator import Orchestrator


def retrieve_context(orchestrator: Orchestrator ,user_prompt: str, titles: typing.List[str]) -> ChatMessage:
    nodes = [
        Node(content=user_prompt, metadata={"doc": title}, embedding=None)
        for title in titles
    ]

    orchestrator.embed(nodes)
 
    similar_nodes = orchestrator.find_context_nodes(nodes, 5)

    def format_context_nodes(node: Node):
        # NOTE: we deanomize here and then reanoyimize in the handler
        title = node.metadata["doc"]
        content = orchestrator.deanoymize(node.content)
        return f"From the {title} wiki page, {content}"
    
    raw_context = "\n".join(map(format_context_nodes, similar_nodes))

    context = f"Below is useful context. Do not answer the question yet.\n{raw_context}\n---\n"

    return ChatMessage(role=ChatMessageRole.System, content=context)

