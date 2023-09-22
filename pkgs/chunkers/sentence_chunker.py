from typing import Dict, List
from pkgs.chunkers.chunker import Chunker
from pkgs import Node


class SentenceChunker(Chunker):
    """
    Runs on the assumption that the text is a long paragraph.
    """

    def __init__(
        self,
        min_chunk_length: int,
        max_chunk_length: int,
        word_sep: str = " ",
        sentence_sep: str = ".",
    ):
        self.min_cl = min_chunk_length
        self.max_cl = max_chunk_length
        self.ws = word_sep
        self.ss = sentence_sep

    def text_to_nodes(self, text: str, metadata: Dict) -> List[Node]:
        nodes = []
        for sentence in text.split(self.ss):
            words = [word for word in sentence.split(self.ws) if word]
            if len(words) < self.min_cl:
                continue
            new_sentence = " ".join(words[: self.max_cl])
            nodes.append(Node(new_sentence, metadata, None))
        return nodes
