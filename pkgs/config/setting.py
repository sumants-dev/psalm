from pydantic import BaseModel, validator
import enum
from typing import Dict
from pkgs.models.pontus.base import ProviderType

from pkgs.modifiers.anonymity.anonymizer import EntityResolution, PII_Type
from pkgs.orchestrator.config import AnoymizerConfig, EmbedderConfig, LLMConfig, ProviderConfig, RagConfig, VectorDBConfig
class Settings(BaseModel):
    app_name: str = "Pontus PSaLM"
    version: str
    llm: LLMConfig
    rag: RagConfig



settings: Settings | None = None


def setSettings(json: Dict):
    global settings
    settings = Settings(**json)

def getSettings():
    assert settings is not None, "Settings not set"
    return settings
