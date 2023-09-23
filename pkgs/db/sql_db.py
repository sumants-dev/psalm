from sqlalchemy import create_engine


class SQLDB:
    def __init__(self, conn_str: str, pool_size: int = 20):
        self._engine = create_engine(conn_str, pool_size=pool_size)

    @property
    def engine(self):
        return self._engine
