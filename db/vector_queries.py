# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.21.0
# source: vector_queries.sql
import dataclasses
from typing import Any, AsyncIterator, Iterator, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from db import models


CREATE_VECTOR = """-- name: create_vector \\:one
INSERT INTO vector_store (
  content, metadata, embedding
) VALUES (
  :p1, :p2, :p3
)
RETURNING id
"""


DELETE_VECTOR = """-- name: delete_vector \\:exec
DELETE FROM vector_store
WHERE id = :p1
"""


GET_NEAREST_VECTORS = """-- name: get_nearest_vectors \\:many
SELECT content, embedding <-> :p1 AS distance
FROM vector_store
ORDER BY 2
LIMIT :p2
"""


@dataclasses.dataclass()
class GetNearestVectorsRow:
    content: Optional[str]
    distance: Optional[Any]


GET_NEAREST_VECTORS_GIVEN_CONDITION = """-- name: get_nearest_vectors_given_condition \\:many
SELECT content, embedding <-> :p1 AS distance
FROM vector_store
WHERE metadata @> :p3\\:\\:JSONB
ORDER BY 2
LIMIT :p2
"""


@dataclasses.dataclass()
class GetNearestVectorsGivenConditionRow:
    content: Optional[str]
    distance: Optional[Any]


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def create_vector(self, *, content: Optional[str], metadata: Optional[Any], embedding: Optional[Any]) -> Optional[int]:
        row = self._conn.execute(sqlalchemy.text(CREATE_VECTOR), {"p1": content, "p2": metadata, "p3": embedding}).first()
        if row is None:
            return None
        return row[0]

    def delete_vector(self, *, id: int) -> None:
        self._conn.execute(sqlalchemy.text(DELETE_VECTOR), {"p1": id})

    def get_nearest_vectors(self, *, embedding: Optional[Any], limit: int) -> Iterator[GetNearestVectorsRow]:
        result = self._conn.execute(sqlalchemy.text(GET_NEAREST_VECTORS), {"p1": embedding, "p2": limit})
        for row in result:
            yield GetNearestVectorsRow(
                content=row[0],
                distance=row[1],
            )

    def get_nearest_vectors_given_condition(self, *, embedding: Optional[Any], limit: int, dollar_3: Any) -> Iterator[GetNearestVectorsGivenConditionRow]:
        result = self._conn.execute(sqlalchemy.text(GET_NEAREST_VECTORS_GIVEN_CONDITION), {"p1": embedding, "p2": limit, "p3": dollar_3})
        for row in result:
            yield GetNearestVectorsGivenConditionRow(
                content=row[0],
                distance=row[1],
            )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def create_vector(self, *, content: Optional[str], metadata: Optional[Any], embedding: Optional[Any]) -> Optional[int]:
        row = (await self._conn.execute(sqlalchemy.text(CREATE_VECTOR), {"p1": content, "p2": metadata, "p3": embedding})).first()
        if row is None:
            return None
        return row[0]

    async def delete_vector(self, *, id: int) -> None:
        await self._conn.execute(sqlalchemy.text(DELETE_VECTOR), {"p1": id})

    async def get_nearest_vectors(self, *, embedding: Optional[Any], limit: int) -> AsyncIterator[GetNearestVectorsRow]:
        result = await self._conn.stream(sqlalchemy.text(GET_NEAREST_VECTORS), {"p1": embedding, "p2": limit})
        async for row in result:
            yield GetNearestVectorsRow(
                content=row[0],
                distance=row[1],
            )

    async def get_nearest_vectors_given_condition(self, *, embedding: Optional[Any], limit: int, dollar_3: Any) -> AsyncIterator[GetNearestVectorsGivenConditionRow]:
        result = await self._conn.stream(sqlalchemy.text(GET_NEAREST_VECTORS_GIVEN_CONDITION), {"p1": embedding, "p2": limit, "p3": dollar_3})
        async for row in result:
            yield GetNearestVectorsGivenConditionRow(
                content=row[0],
                distance=row[1],
            )
