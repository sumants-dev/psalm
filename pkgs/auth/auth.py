from fastapi.security import HTTPBasic, HTTPBasicCredentials


class Auth:
    def authenticate(
        self, credentials: HTTPBasicCredentials | None, role: str | None = None
    ) -> bool:
        raise NotImplementedError("Must implement authenticate")

    def add_user(
        self,
        admin_credentials: HTTPBasicCredentials | None,
        new_username: str,
        new_password: str,
    ) -> bool:
        raise NotImplementedError("Must implement add_user")

    def remove_user(
        self, admin_credentials: HTTPBasicCredentials | None, username: str
    ) -> bool:
        raise NotImplementedError("Must implement revoke_user")
