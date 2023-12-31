# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.21.0
# source: node_queries.sql
import dataclasses
from typing import Any, AsyncIterator, Iterator, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from db import models


GET_NEAREST_NODES = """-- name: get_nearest_nodes \\:many
SELECT content, embedding <-> :p1 AS distance
FROM node
ORDER BY 2
LIMIT :p2
"""


@dataclasses.dataclass()
class GetNearestNodesRow:
    content: str
    distance: Optional[Any]


GET_NEAREST_NODES_GIVEN_CONDITION = """-- name: get_nearest_nodes_given_condition \\:many
SELECT content, embedding <-> :p1 AS distance
FROM node
WHERE metadata @> :p3\\:\\:JSONB
ORDER BY 2
LIMIT :p2
"""


@dataclasses.dataclass()
class GetNearestNodesGivenConditionRow:
    content: str
    distance: Optional[Any]


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def get_nearest_nodes(
        self, *, embedding: Any, limit: int
    ) -> Iterator[GetNearestNodesRow]:
        result = self._conn.execute(
            sqlalchemy.text(GET_NEAREST_NODES), {"p1": embedding, "p2": limit}
        )
        for row in result:
            yield GetNearestNodesRow(
                content=row[0],
                distance=row[1],
            )

    def get_nearest_nodes_given_condition(
        self, *, embedding: Any, limit: int, dollar_3: Any
    ) -> Iterator[GetNearestNodesGivenConditionRow]:
        result = self._conn.execute(
            sqlalchemy.text(GET_NEAREST_NODES_GIVEN_CONDITION),
            {"p1": embedding, "p2": limit, "p3": dollar_3},
        )
        for row in result:
            yield GetNearestNodesGivenConditionRow(
                content=row[0],
                distance=row[1],
            )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def get_nearest_nodes(
        self, *, embedding: Any, limit: int
    ) -> AsyncIterator[GetNearestNodesRow]:
        result = await self._conn.stream(
            sqlalchemy.text(GET_NEAREST_NODES), {"p1": embedding, "p2": limit}
        )
        async for row in result:
            yield GetNearestNodesRow(
                content=row[0],
                distance=row[1],
            )

    async def get_nearest_nodes_given_condition(
        self, *, embedding: Any, limit: int, dollar_3: Any
    ) -> AsyncIterator[GetNearestNodesGivenConditionRow]:
        result = await self._conn.stream(
            sqlalchemy.text(GET_NEAREST_NODES_GIVEN_CONDITION),
            {"p1": embedding, "p2": limit, "p3": dollar_3},
        )
        async for row in result:
            yield GetNearestNodesGivenConditionRow(
                content=row[0],
                distance=row[1],
            )
