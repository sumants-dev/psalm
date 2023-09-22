from pkgs import Node
from typing import Dict, List


class Chunker:
    """
    Converts a large block of text into embeddable chunks
    """

    def text_to_nodes(self, text: str, metadata: Dict) -> List[Node]:
        raise NotImplementedError("Must implement text_to_nodes")
