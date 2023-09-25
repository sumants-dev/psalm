from typing import List
from pkgs.chunkers.chunker import Chunker
from nltk.tokenize import sent_tokenize


class NLTKChunker(Chunker):
    """
    Splits documents using nltk's NLP tokenizer
    """

    def __init__(
        self, min_chunk_length: int, max_chunk_length: int, max_overlap: int = 10
    ):
        self.min_chunk_size = min_chunk_length
        self.max_chunk_size = max_chunk_length
        self.max_overlap = max_overlap

    def _split_text(self, text: str) -> List[str]:
        return sent_tokenize(text=text)
