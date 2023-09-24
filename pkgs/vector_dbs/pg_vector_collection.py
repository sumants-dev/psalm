from typing import List, Tuple, Dict
from pkgs import Node
from pkgs.vector_dbs.vector_collection import VectorCollection, SimilarityMetric
from sqlalchemy.sql import text
from sqlalchemy.engine import Engine as SQLAlchemyEngine
from json import dumps
from math import exp


class PgVectorCollection(VectorCollection):
    save_nodes_query = (
        " (content, metadata, embedding) VALUES (:content, :metadata, :embedding)"
    )

    find_nodes_where = " WHERE metadata @> :metadata :: JSONB"

    find_nodes_order = " ORDER BY 3 LIMIT :max_nodes;"

    def __init__(self, engine: SQLAlchemyEngine, collection: str, vector_dimension: int, include_metadata: bool = True):
        self.engine = engine
        self.collection = self._sanitize_collection(collection)
        self.include_metadata = include_metadata
        assert vector_dimension > 0, "Vectors must have non-negative dimension"
        self.dim = vector_dimension

        if self.include_metadata:
            COLLECTION_SQL = f"""
                CREATE TABLE IF NOT EXISTS Pontus.{self.collection} (
                    id bigserial primary key,
                    content text not null,
                    metadata JSONB not null,
                    embedding vector({self.dim}) not null,
                    created_at timestamp default current_timestamp
                );
            """

            INDEX_SQL = f"""
                CREATE INDEX ix_{self.collection} ON Pontus.{self.collection} USING gin (metadata jsonb_path_ops);
            """
        else:
            COLLECTION_SQL = f"""
                CREATE TABLE IF NOT EXISTS Pontus.{self.collection} (
                    id bigserial primary key,
                    content text not null,
                    embedding vector({self.dim}) not null,
                    created_at timestamp default current_timestamp
                );
            """

            INDEX_SQL = f"""
                CREATE INDEX ix_{self.collection} ON Pontus.{self.collection} USING hash (content);
            """

        try:
            self.execute("CREATE SCHEMA IF NOT EXISTS Pontus")
            self.execute(COLLECTION_SQL)
            self.execute(INDEX_SQL)
        except:
            raise Exception(f"Failed to initialize PgVectorCollection {self.collection}")
        
        self.is_queryable = True

    def _sanitize_collection(self, collection: str) -> str:
        """
        Enforce strict constraints on collection to avoid SQL injection
        """
        return "".join(c for c in collection if c.isalnum())  

    def delete_collection(self):
        self.execute(f"DROP INDEX IF EXISTS ix_{self.collection};")
        self.execute(f"DROP TABLE IF EXISTS Pontus.{self.collection};")
        self.is_queryable = False

    def execute(self, cmd: str, parameters: Dict | List[Dict] | None = None):
        if not self.is_queryable:
            raise Exception("Can only query queryable collections")

        with self.engine.connect() as conn:
            if parameters:
                conn.exec_driver_sql(cmd, parameters=parameters)
            else:
                conn.exec_driver_sql(cmd)

            conn.commit()

    def save_nodes(self, nodes: List[Node]):
        def serialize_node(node: Node) -> Dict:
            serialized_node = {
                "content": node.content,
                "embedding": dumps(node.embedding)
            }
            if self.include_metadata:
                serialized_node["metadata"] = dumps(node.metadata)

        serialized_nodes = [
            serialize_node(node)
            for node in nodes
        ]

        query = text("INSERT INTO " + self.collection + self.save_nodes_query)
        with self.engine.connect() as conn:
            conn.execute(query, serialized_nodes)
            conn.commit()

    def find_similar_nodes(
        self, node: Node, max_nodes: int = 5, metric: SimilarityMetric = SimilarityMetric.L2
    ) -> List[Tuple[Node, float]]:
        find_nodes_select = f"SELECT content, {'metadata, ' if self.include_metadata else ''}embedding <{metric.value}> :embedding AS distance, created_at FROM "

        if node.metadata and self.include_metadata:
            query = text(
                find_nodes_select
                + self.collection
                + self.find_nodes_where
                + self.find_nodes_order
            )
            params = dict(
                embedding=dumps(node.embedding),
                metadata=dumps(node.metadata),
                max_nodes=max_nodes,
            )
        else:
            query = text(
                find_nodes_select + self.collection + self.find_nodes_order
            )
            params = dict(embedding=dumps(node.embedding), max_nodes=max_nodes)

        with self.engine.connect() as conn:
            data = [
                (
                    Node(node.content, node.metadata if self.include_metadata else {}, None, created_at=node.created_at),
                    1 - exp(-abs(node.distance)),
                )
                for node in conn.execute(query, params)
            ]
            return data

    def delete_node(self, node: Node):
        query = text("DELETE FROM " + self.collection + " WHERE content = :content")
        with self.engine.connect() as conn:
            conn.execute(query, {"content": node.content})
            conn.commit()