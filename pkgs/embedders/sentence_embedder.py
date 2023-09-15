from typing import List
from sentence_transformers import SentenceTransformer
from pkgs.embedders.embedder import Embedder

class SentenceEmbedder(Embedder):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(f"sentence-transformers/{model_name}")

    def _embed(self, chunks: List[str]) -> List[List[float]]:
        return [
            [dim.item() for dim in embed]
            for embed in self.model.encode(chunks)
        ]