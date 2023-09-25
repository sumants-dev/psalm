from typing import List
from sentence_transformers import SentenceTransformer
from pkgs.embedders.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: str) -> None:
        if model_name[:22] == "sentence_transformers/":
            self.model = SentenceTransformer(model_name)
        else:
            self.model = SentenceTransformer(f"sentence-transformers/{model_name}")
        self.max_length = self.model.get_max_seq_length()
        self.output_dim = self.model.get_sentence_embedding_dimension()

    def _embed(self, chunks: List[str]) -> List[List[float]]:
        return [[dim.item() for dim in embed] for embed in self.model.encode(chunks)]
