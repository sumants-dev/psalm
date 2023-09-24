import enum
import typing

from pydantic import BaseModel, validator
from pkgs.models.pontus.base import ProviderType

from pkgs.modifiers.anonymity.anonymizer import EntityResolution, PII_Type
from typing import List


class VectorDBType(str, enum.Enum):
    pgvector = "pgvector"

class VectorDBConfig(BaseModel):
    type: VectorDBType
    conn_str: str
    pool_size: int = 20

class VectorCollectionConfig(VectorDBConfig):
    collection_name: str
    vector_dimension: int

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


class LoaderType(str, enum.Enum):
    demo = "demo"
    api_loader = "api_loader"


class RagLoaderAuth(BaseModel):
    username: str
    password: str


class RagLoaderConfig(BaseModel):
    type: LoaderType
    auth: RagLoaderAuth | None = None
    endpoint: str | None = None
    bulk_endpoint: str | None = None
    queries: typing.Dict[str, str] | None = None


class RagDataPopulationConfig(BaseModel):
    loader: RagLoaderConfig


class RagConfig(BaseModel):
    vector_collection: VectorCollectionConfig
    population: RagDataPopulationConfig | None = None
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
    vector_collection: VectorCollectionConfig | None = None
    embedder: EmbedderConfig | None = None
    expiry_in_seconds: int = 60 * 60 * 24 * 7


class LLMConfig(BaseModel):
    provider: ProviderConfig
    anoymizer: AnoymizerConfig
    pre_processors: ProcessorConfig | None = None
    post_processors: ProcessorConfig | None = None
    cache: CacheConfig | None = None


class DatabaseType(str, enum.Enum):
    postgres = "postgres"


class DatabaseConfig(BaseModel):
    type: DatabaseType = DatabaseType.postgres
    conn_str: str
    pool_size: int = 20


class AuthType(str, enum.Enum):
    api_key = "api_key"
    no_auth = "no_auth"


class AuthConfig(BaseModel):
    type: AuthType = AuthType.no_auth
    default_admin_username: str | None = None
    default_admin_api_key: str | None = None


class ApplicationConfig(BaseModel):
    database: DatabaseConfig | None = None
    authentication: AuthConfig | None = None
