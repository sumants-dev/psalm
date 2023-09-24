# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.21.0
# source: user.sql
from typing import Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from db import models


CREATE_API_KEY = """-- name: create_api_key \\:one
INSERT INTO pontus_api_keys (username, password)
VALUES (:p1, :p2)
RETURNING id, username, password, role, enabled, created_at, updated_at
"""


CREATE_API_KEY_WITH_ROLE = """-- name: create_api_key_with_role \\:one
INSERT INTO pontus_api_keys (username, password, role)
VALUES (:p1, :p2, :p3)
RETURNING id, username, password, role, enabled, created_at, updated_at
"""


DELETE_API_KEY_BY_USERNAME = """-- name: delete_api_key_by_username \\:one
DELETE FROM pontus_api_keys WHERE username = :p1 RETURNING id, username, password, role, enabled, created_at, updated_at
"""


GET_API_KEY_BY_USERNAME = """-- name: get_api_key_by_username \\:one
SELECT id, username, password, role, enabled, created_at, updated_at FROM pontus_api_keys WHERE username = :p1
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def create_api_key(
        self, *, username: str, password: str
    ) -> Optional[models.PontusApiKey]:
        row = self._conn.execute(
            sqlalchemy.text(CREATE_API_KEY), {"p1": username, "p2": password}
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def create_api_key_with_role(
        self, *, username: str, password: str, role: models.Roletype
    ) -> Optional[models.PontusApiKey]:
        row = self._conn.execute(
            sqlalchemy.text(CREATE_API_KEY_WITH_ROLE),
            {"p1": username, "p2": password, "p3": role},
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def delete_api_key_by_username(
        self, *, username: str
    ) -> Optional[models.PontusApiKey]:
        row = self._conn.execute(
            sqlalchemy.text(DELETE_API_KEY_BY_USERNAME), {"p1": username}
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    def get_api_key_by_username(
        self, *, username: str
    ) -> Optional[models.PontusApiKey]:
        row = self._conn.execute(
            sqlalchemy.text(GET_API_KEY_BY_USERNAME), {"p1": username}
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def create_api_key(
        self, *, username: str, password: str
    ) -> Optional[models.PontusApiKey]:
        row = (
            await self._conn.execute(
                sqlalchemy.text(CREATE_API_KEY), {"p1": username, "p2": password}
            )
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    async def create_api_key_with_role(
        self, *, username: str, password: str, role: models.Roletype
    ) -> Optional[models.PontusApiKey]:
        row = (
            await self._conn.execute(
                sqlalchemy.text(CREATE_API_KEY_WITH_ROLE),
                {"p1": username, "p2": password, "p3": role},
            )
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    async def delete_api_key_by_username(
        self, *, username: str
    ) -> Optional[models.PontusApiKey]:
        row = (
            await self._conn.execute(
                sqlalchemy.text(DELETE_API_KEY_BY_USERNAME), {"p1": username}
            )
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    async def get_api_key_by_username(
        self, *, username: str
    ) -> Optional[models.PontusApiKey]:
        row = (
            await self._conn.execute(
                sqlalchemy.text(GET_API_KEY_BY_USERNAME), {"p1": username}
            )
        ).first()
        if row is None:
            return None
        return models.PontusApiKey(
            id=row[0],
            username=row[1],
            password=row[2],
            role=row[3],
            enabled=row[4],
            created_at=row[5],
            updated_at=row[6],
        )