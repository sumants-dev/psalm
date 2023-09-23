from fastapi.security import HTTPBasicCredentials
from pkgs.auth.auth import Auth


class NoAuth(Auth):
    def authenticate(
        self, credentials: HTTPBasicCredentials, role: str | None = None
    ) -> bool:
        return True

    def add_user(
        self,
        admin_credentials: HTTPBasicCredentials,
        new_username: str,
        new_password: str,
    ) -> bool:
        return True

    def remove_user(
        self, admin_credentials: HTTPBasicCredentials, username: str
    ) -> bool:
        return True
