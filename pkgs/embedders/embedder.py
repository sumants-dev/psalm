from typing import List
from pkgs import Node


class Embedder:
    def _embed(self, chunks: List[str]) -> List[List[float]]:
        """
        Produce a vector embedding for every chunk
        """
        return NotImplementedError("Must implement _embed")
    
    def embed(self, nodes: List[Node]):
        """
        Attach embeddings to nodes
        """
        embeddings = self._embed([node.content for node in nodes])
        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding