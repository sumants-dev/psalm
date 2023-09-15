from typing import List, Tuple
from pkgs import Node
from pkgs.vector_dbs.vector_db import VectorDB
from sqlalchemy import create_engine, sql
from json import dumps
from math import exp

class PgVectorStore(VectorDB):
    """
    TODO: Table Creation / Destruction
    """
    save_nodes_query = " (content, metadata, embedding) VALUES (:content, :metadata, :embedding)"

    find_nodes_select = "SELECT content, metadata, embedding <-> :embedding AS distance FROM "

    find_nodes_where = " WHERE metadata @> :metadata :: JSONB"

    find_nodes_order = " ORDER BY 3 LIMIT :max_nodes;"

    def __init__(self, cnxn_string: str, pool_size: int = 20):
        self.engine = create_engine(cnxn_string, pool_size=pool_size)

    def _sanitize_collection(self, collection: str) -> str:
        """
        Enforce strict constraints on collection to avoid SQL injection
        """
        return "".join(c for c in collection if c == '.' or c.isalnum())

    def save_nodes(self, nodes: List[Node], collection: str):
        collection = self._sanitize_collection(collection)

        serialized_nodes = [
            {
                "content": node.content, 
                "metadata": dumps(node.metadata), 
                "embedding": dumps(node.embedding)
            }
            for node in nodes
        ]

        query = sql.text("INSERT INTO " + collection + self.save_nodes_query)
        with self.engine.connect() as conn:
            conn.execute(query, serialized_nodes)
            conn.commit()

    def find_similar_nodes(self, node: Node, collection: str, max_nodes: int = 5) -> List[Tuple[Node, float]]:
        collection = self._sanitize_collection(collection)
        if node.metadata:
            query = sql.text(self.find_nodes_select + collection + self.find_nodes_where + self.find_nodes_order)
            params = dict(embedding = dumps(node.embedding), metadata = dumps(node.metadata), max_nodes = max_nodes)
        else:
            query = sql.text(self.find_nodes_select + collection + self.find_nodes_order)
            params = dict(embedding = dumps(node.embedding), max_nodes = max_nodes)
        
        with self.engine.connect() as conn:
            return [
                (Node(node.content, node.metadata, None), 1 - exp(node.distance))
                for node in conn.execute(query, params)
            ]
            