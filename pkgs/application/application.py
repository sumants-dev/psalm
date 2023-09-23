from pkgs.auth.auth import Auth
from pkgs.db.sql_db import SQLDB


class Application:
    auth: Auth
    sql_db: SQLDB | None

    def __init__(self, auth: Auth, sql_db: SQLDB | None = None) -> None:
        self.auth = auth
        self.sql_db = sql_db
