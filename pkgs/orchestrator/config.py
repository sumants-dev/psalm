import enum

from pydantic import BaseModel, validator
from pkgs.models.pontus.base import ProviderType

from pkgs.modifiers.anonymity.anonymizer import EntityResolution, PII_Type
from typing import List


class VectorDBType(str, enum.Enum):
    pgvector = "pgvector"


class VectorDBConfig(BaseModel):
    type: VectorDBType
    conn_str: str
    collection_name: str = "Node"


class EmbedderType(str, enum.Enum):
    sentence = "sentence"


class EmbedderConfig(BaseModel):
    type: EmbedderType
    model: str
    max_length: int


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


class RemoveToxcityType(str, enum.Enum):
    simple = "simple"


class RemoveToxcityProccessorConfig(BaseModel):
    type: RemoveToxcityType


class ProcessorConfig(BaseModel):
    remove_toxicity: RemoveToxcityProccessorConfig | None = None


class RagConfig(BaseModel):
    vector_db: VectorDBConfig
    embedder: EmbedderConfig
    anoymizer: AnoymizerConfig | None = None
    pre_processors: ProcessorConfig | None = None
    post_processors: ProcessorConfig | None = None


class ProviderConfig(BaseModel):
    type: ProviderType
    api_key: str
    default_model: str


class CacheType(str, enum.Enum):
    small_cache = "small_cache"


class CacheConfig(BaseModel):
    type: CacheType
    vector_db: VectorDBConfig | None = None
    embedder: EmbedderConfig | None = None
    expiry_in_seconds: int = 60 * 60 * 24 * 7


class LLMConfig(BaseModel):
    provider: ProviderConfig
    anoymizer: AnoymizerConfig
    pre_processors: ProcessorConfig | None = None
    post_processors: ProcessorConfig | None = None
    cache: CacheConfig | None = None
