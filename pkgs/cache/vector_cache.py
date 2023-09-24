from datetime import datetime, timedelta
import json
from pkgs import Node
from pkgs.cache.caching import PromptCache, PromptCacheRecord
from pkgs.embedders.embedder import Embedder
from pkgs.modifiers.anonymity.anonymizer import Anonymizer, Deanonymizer
from pkgs.modifiers.modifier import Modifier
from pkgs.vector_dbs.vector_collection import VectorCollection

from typing import List, TypeVar


T = TypeVar("T", str, list, dict, Node)


class SmallPromptCache(PromptCache):
    pre_proccesors: List[Modifier] = []
    post_processors: List[Modifier] = []

    def __init__(
        self,
        vector_collection: VectorCollection,
        embedder: Embedder,
        anoymizer: Anonymizer | None = None,
        deanonimyzer: Deanonymizer | None = None,
        threshold: float = 0.1,
        expiry_in_seconds: int = 60 * 60 * 24 * 7,
    ) -> None:
        self.vector_collection = vector_collection
        self.embedder = embedder

        self.anoymizer = anoymizer
        self.deanonimyzer = deanonimyzer

        self.expiry_in_seconds = expiry_in_seconds

        self.threshold = threshold

        if anoymizer is not None:
            self.pre_proccesors.append(anoymizer)

        if deanonimyzer is not None:
            self.post_processors.append(deanonimyzer)

    def destroy(self) -> None:
        self.vector_collection.delete_collection()

    def _pre_process(self, data: T) -> T:
        for pre_processor in self.pre_proccesors:
            data = pre_processor.transform(data)
        return data

    def _post_process(self, data: T) -> T:
        for post_processor in self.post_processors:
            data = post_processor.transform(data)
        return data

    def set(self, prompt: str, record: PromptCacheRecord) -> bool:
        if len(prompt) > self.embedder.max_length:
            return False

        nodes = [
            Node(
                content=prompt,
                metadata={"cache": record.model_dump_json(exclude=None)},
                embedding=None,
            )
        ]
        self.embedder.embed(nodes)
        self._pre_process(nodes)
        self.vector_collection.save_nodes(nodes=nodes, collection=self.collection)
        return True

    def get(self, prompt: str) -> PromptCacheRecord | None:
        t_prompt = self._pre_process(prompt)

        node = [Node(content=t_prompt, metadata={}, embedding=None)]
        self.embedder.embed(node)

        cache_lookup = self.vector_collection.find_similar_nodes(
            collection=self.collection,
            node=node[0],
            max_nodes=1,
        )

        if len(cache_lookup) == 0:
            return None

        cache_hit, dist = cache_lookup[0]

        if dist >= self.threshold:
            return None

        if (
            cache_hit.created_at
            and cache_hit.created_at + timedelta(seconds=self.expiry_in_seconds)
            < datetime.now()
        ):
            self.vector_collection.delete_node(cache_hit, collection=self.collection)
            return None

        deanomymized_cache = self._post_process(cache_hit)
        d = json.loads(deanomymized_cache.metadata["cache"])
        return PromptCacheRecord(**d)
