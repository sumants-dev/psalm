from pydantic import BaseModel
import os
from typing import Dict

from pkgs.orchestrator.config import (
    ApplicationConfig,
    LLMConfig,
    PrivacyConfig,
    DocumentStoreConfig,
)


class Settings(BaseModel):
    app_name: str = "Pontus PSaLM"
    version: str
    llm: LLMConfig
    document_store: DocumentStoreConfig
    privacy: PrivacyConfig
    application: ApplicationConfig


settings: Settings | None = None


def setKeysInSettings(json):
    if isinstance(json, list):
        return [setKeysInSettings(elem) for elem in json]
    if isinstance(json, dict):
        return {key: setKeysInSettings(value) for key, value in json.items()}
    if isinstance(json, str) and json[:4] == "env:":
        env_key = os.getenv(key=json[4:])
        if env_key:
            return env_key
        raise Exception(f"{json[4:]} is not an environment variable")
    return json


def setSettings(json: Dict):
    global settings
    settings = Settings(**setKeysInSettings(json=json)) # type: ignore


def getSettings():
    assert settings is not None, "Settings not set"
    return settings
