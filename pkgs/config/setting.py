from pydantic import BaseModel, validator
import enum
from typing import Dict
from pkgs.models.pontus.base import ProviderType

from pkgs.modifiers.anonymity.anonymizer import EntityResolution, PII_Type
class VectorDBType(str, enum.Enum):
    pgvector = "pgvector"

class VectorDBConfig(BaseModel):
    type: VectorDBType
    conn_str: str

class EmbedderType(str, enum.Enum):
    sentence = "sentence"

class EmbedderConfig(BaseModel):
    type: EmbedderType
    model: str

class AnoymizerType(str, enum.Enum):
    presidio = "presidio"

class AnoymizerEntityResolution(str, enum.Enum):
    containment = "containment"


class AnoymizerConfig(BaseModel):
    type: AnoymizerType
    key: str
    threshold: float
    entity_resolution: EntityResolution
    pii_types: list[PII_Type] 

    @validator("entity_resolution", pre=True)
    def entity_resolution_to_enum(cls, v):
        assert isinstance(v, str)
        return v.upper()

    @validator("pii_types", pre=True)
    def pii_types_upper(cls, v):
        assert isinstance(v, list)
        return [pii_type.upper() for pii_type in v]



class ProviderConfig(BaseModel):
    type: ProviderType
    api_key: str

class Settings(BaseModel):
    app_name: str = "Pontus PSaLM"
    version: str
    provider: ProviderConfig
    vector_db: VectorDBConfig
    embedder: EmbedderConfig
    anoymizer: AnoymizerConfig



settings: Settings | None = None


def setSettings(json: Dict):
    global settings
    settings = Settings(**json)

def getSettings():
    assert settings is not None, "Settings not set"
    return settings
