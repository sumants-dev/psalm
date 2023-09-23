from typing import List
from sentence_transformers import SentenceTransformer
from pkgs.embedders.embedder import Embedder
import enum


class SentenceEmbedder(Embedder):
    def __init__(self, model_name: str, max_length: int) -> None:
        self.model = SentenceTransformer(f"sentence-transformers/{model_name}")
        self.max_length = max_length

    def _embed(self, chunks: List[str]) -> List[List[float]]:
        return [[dim.item() for dim in embed] for embed in self.model.encode(chunks)]
