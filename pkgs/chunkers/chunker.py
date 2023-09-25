from pkgs import Node
from typing import Dict, List, Tuple


class Chunker:
    """
    Converts a large block of text into embeddable chunks
    """

    max_chunk_size: int
    min_chunk_size: int
    max_overlap: int

    def _split_text(self, text: str) -> List[str]:
        """
        Split the text into meaningful subdivisions for embedding
        """
        raise NotImplementedError("Must implement _chunk_text")

    def _add_metadata_per_chunk(self, chunk: str) -> Dict:
        """
        Add any additional metadata for a chunk here before it's converted
        to a node
        """
        return {}

    def _to_node(self, current_chunk: List[Tuple[str, int]], metadata: Dict) -> Node:
        chunk = ". ".join(subdivision[0] for subdivision in current_chunk)
        new_metadata = {**self._add_metadata_per_chunk(chunk), **metadata}
        return Node(content=chunk, metadata=new_metadata)

    def document_to_nodes(self, text: str, metadata: Dict) -> List[Node]:
        """
        Generate nodes from a moving window over the subdivisions based on
        max_chunk_size and max_overlap
        """
        nodes = []
        current_chunk_length = 0
        current_chunk = []
        for subdivision in self._split_text(text=text):
            subdivision_length = len(subdivision.split())
            current_chunk.append((subdivision, subdivision_length))
            current_chunk_length += subdivision_length
            if subdivision_length < self.min_chunk_size:
                continue

            while (
                current_chunk_length
                > min(self.max_chunk_size, self.max_overlap + subdivision_length)
                and len(current_chunk) > 1
            ):
                current_chunk_length -= current_chunk.pop(0)[1]
            if current_chunk_length > self.max_chunk_size:
                pass
                # TODO: Log here to warn about long chunks (will be truncated by embedder)
            nodes.append(self._to_node(current_chunk=current_chunk, metadata=metadata))

        return nodes
