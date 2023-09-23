from pkgs import Node
from typing import List, Tuple


class VectorDB:
    """
    Abstracts the interaction with the DB
    """

    def save_nodes(self, nodes: List[Node], collection: str):
        """
        Assumes all nodes have embeddings associated with them.
        """
        return NotImplementedError("save_nodes must be implemented")

    def find_similar_nodes(
        self, node: Node, collection: str, max_nodes: int = 5
    ) -> List[Tuple[Node, float]]:
        raise NotImplementedError("find_similar_nodes must be implemented")

    def delete_node(self, node: Node, collection: str):
        raise NotImplementedError("delete_node must be implemented")

    def create_collection(self, collection: str):
        raise NotImplementedError("create_collection must be implemented")

    def drop_collection(self, collection: str):
        raise NotImplementedError("drop_collection must be implemented")

    def execute(self, cmd: str):
        raise NotImplementedError("execute must be implemented")
