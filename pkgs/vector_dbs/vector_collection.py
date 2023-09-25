from pkgs import Node
from typing import List, Tuple
from enum import Enum


class SimilarityMetric(Enum):
    L2 = "-"
    INNER = "#"


class VectorCollection:
    """
    Abstracts the interaction with vector collections
    """

    def save_nodes(self, nodes: List[Node]):
        """
        Assumes all nodes have embeddings associated with them.
        """
        return NotImplementedError("save_nodes must be implemented")

    def find_similar_nodes(
        self,
        node: Node,
        max_nodes: int = 5,
        metric: SimilarityMetric = SimilarityMetric.L2,
    ) -> List[Tuple[Node, float]]:
        """
        Returns nodes similar to the inputted node,
        and their distance from the node given the metric
        """

        raise NotImplementedError("find_similar_nodes must be implemented")

    def delete_collection(self):
        raise NotImplementedError("delete_collection must be implemented")

    def delete_node(self, node: Node):
        raise NotImplementedError("delete_node must be implemented")
