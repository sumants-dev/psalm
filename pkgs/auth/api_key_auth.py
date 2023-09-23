from fastapi.security import HTTPBasicCredentials
from db.user import Querier, models
from pkgs.auth.auth import Auth
from passlib.hash import bcrypt

from pkgs.db.sql_db import SQLDB


class ApiKeyAuth(Auth):
    def __init__(
        self, sql_db: SQLDB, default_admin_credentials: HTTPBasicCredentials | None
    ) -> None:
        self.sql_db = sql_db

        if default_admin_credentials is not None:
            with self.sql_db.engine.connect() as conn:
                q = Querier(conn)
                api_key = q.get_api_key_by_username(
                    username=default_admin_credentials.username
                )

                if api_key is None:
                    hash_pass = bcrypt.hash(default_admin_credentials.password)
                    q.create_api_key_with_role(
                        username=default_admin_credentials.username,
                        password=hash_pass,
                        role=models.Roletype.ADMIN,
                    )
                conn.commit()

    def authenticate(
        self, credentials: HTTPBasicCredentials | None, role: str | None = None
    ) -> bool:
        if credentials is None:
            return False

        with self.sql_db.engine.connect() as conn:
            q = Querier(conn)
            api_key = q.get_api_key_by_username(username=credentials.username)

            if api_key is not None and bcrypt.verify(
                credentials.password, api_key.password
            ):
                if role is None:
                    return True
                return api_key.role == role

            return False

    def add_user(
        self,
        admin_credentials: HTTPBasicCredentials | None,
        new_username: str,
        new_password: str,
    ) -> bool:
        if admin_credentials is None:
            return False

        admin_auth = self.authenticate(credentials=admin_credentials, role="admin")

        if not admin_auth:
            return False

        with self.sql_db.engine.connect() as conn:
            q = Querier(conn)
            try:
                hash_pass = bcrypt.hash(new_password)
                api_key = q.create_api_key(username=new_username, password=hash_pass)
                conn.commit()
                return api_key is not None
            except Exception:
                conn.rollback()
                return False

    def remove_user(
        self, admin_credentials: HTTPBasicCredentials, username: str
    ) -> bool:
        admin_auth = self.authenticate(credentials=admin_credentials, role="admin")

        with self.sql_db.engine.connect() as conn:
            q = Querier(conn)
            if not admin_auth:
                return False

            try:
                api_key = q.delete_api_key_by_username(username=username)
                conn.commit()
                return api_key is not None
            except Exception:
                conn.rollback()
                return False
