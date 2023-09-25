from typing_extensions import TypedDict
from typing import Dict
from abc import ABC, abstractmethod


class TokenMap(TypedDict):
    session_id: str
    token: str
    alias: str


class TokenMapper(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def set(self, session_id: str, token: str, alias: str) -> TokenMap:
        raise NotImplementedError()

    @abstractmethod
    def get(self, session_id: str, alias: str) -> TokenMap:
        raise NotImplementedError()

    @abstractmethod
    def delete_by_session(self, session_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def set_alias_for_text(self, session_id: str, text: str, prefix: str = "α"):
        pass

    @abstractmethod
    def get_for_text(self, session_id: str, text: str, prefix: str = "α"):
        pass
