import secrets
from pkgs.token_mapping.token_mapping import TokenMapper, TokenMap
from typing import Dict, DefaultDict
from collections import defaultdict


TokenMapDictType = DefaultDict[str, Dict[str, str]]


class InMemoryTokenMapper(TokenMapper):
    def __init__(self) -> None:
        self.master_map: TokenMapDictType = defaultdict(dict)

    def set(self, session_id: str, token: str, alias: str) -> TokenMap:
        self.master_map[session_id][alias] = token
        return TokenMap(session_id=session_id, alias=alias, token=token)

    def get(self, session_id: str, alias: str) -> TokenMap:
        token = self.master_map[session_id][alias]
        return TokenMap(session_id=session_id, alias=alias, token=token)

    def delete_by_session(self, session_id: str) -> bool:
        try:
            self.master_map.pop(session_id)
            return True
        except KeyError as e:
            return False

    def set_alias_for_text(self, session_id: str, text: str, prefix: str = "α"):
        """ """
        cursor = 0
        raw_text = ""
        while True:
            next_token_start = text.find(f"{prefix}", cursor)
            if next_token_start == -1:
                break
            next_token_end = text.find(f"{prefix}", next_token_start + 1)
            assert next_token_end != -1, "malformed PSaLM output"

            long_token = text[next_token_start + 1 : next_token_end]
            tokenmap = self.set(
                session_id=session_id,
                token=long_token,
                alias=f"{prefix}{secrets.token_urlsafe(5)}{prefix}",
            )

            raw_text += text[cursor:next_token_start] + tokenmap["alias"]
            cursor = next_token_end + 1
        return raw_text + text[cursor:]

    def get_for_text(self, session_id: str, text: str, prefix: str = "α"):
        """ """
        cursor = 0
        raw_text = ""
        while True:
            next_token_start = text.find(prefix, cursor)
            if next_token_start == -1:
                break
            next_token_end = text.find(prefix, next_token_start + 1)
            assert next_token_end != -1, "malformed PSaLM output"

            alias = text[next_token_start + 1 : next_token_end]
            tokenmap = self.get(session_id=session_id, alias=f"α{alias}α")

            raw_text += (
                text[cursor:next_token_start] + f"{prefix}{tokenmap['token']}{prefix}"
            )
            cursor = next_token_end + 1
        return raw_text + text[cursor:]
