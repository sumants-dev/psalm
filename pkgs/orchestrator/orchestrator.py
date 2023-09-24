from fastapi.security import HTTPBasicCredentials
from pkgs import Node
from pkgs.application.application import Application
from pkgs.auth.api_key_auth import ApiKeyAuth
from pkgs.auth.auth import Auth
from pkgs.auth.no_auth import NoAuth
from pkgs.cache.caching import PromptCache
from pkgs.cache.vector_cache import SmallPromptCache
from pkgs.chunkers.chunker import Chunker
from pkgs.chunkers.sentence_chunker import SentenceChunker
from pkgs.db.sql_db import SQLDB
from pkgs.embedders.embedder import Embedder
from pkgs.loaders.api_loader import ApiLoader
from pkgs.loaders.demo_loader import DemoLoader
from pkgs.embedders.sentence_transformer_embedder import SentenceTransformerEmbedder
from pkgs.modifiers.anonymity.anonymizer import Anonymizer, Deanonymizer
from pkgs.modifiers.anonymity.presidio_anonymizer import (
    PresidioAnonymizer,
    PresidioDeanonymizer,
)
from pkgs.modifiers.modifier import Modifier

from pkgs.models import pydantic_openai
from pkgs.models.pontus.base import (
    ChatMessage,
    ChatResponse,
    OpenAIOptions,
    ProviderType,
)

from requests.auth import HTTPBasicAuth

from copy import deepcopy
from sqlalchemy import create_engine
from typing import TypeVar, List, Dict, Any


import openai
from pkgs.orchestrator.config import AnoymizerConfig, AnoymizerType, ApplicationConfig, AuthConfig, AuthType, CacheConfig, CacheType, DatabaseConfig, DatabaseType, EmbedderConfig, EmbedderType, LoaderType, ProcessorConfig, ProviderConfig, RagConfig, RagDataPopulationConfig, VectorDBConfig, VectorDBType, VectorCollectionConfig
from pkgs.population.population import Population
from pkgs.vector_dbs.pg_vector_collection import PgVectorCollection
from pkgs.vector_dbs.vector_collection import VectorCollection
from pkgs.config.setting import (
    getSettings,
)


T = TypeVar("T")


class Rag:
    config: RagConfig

    def __init__(
        self,
        config: RagConfig,
        vector_collection: VectorCollection,
        embedder: Embedder,
        anoymizer: Anonymizer | None,
        deanoymizer: Deanonymizer | None,
        population: Population | None = None,
        chunker: Chunker = SentenceChunker(min_chunk_length=2, max_chunk_length=256), # TODO: make this configurable
        pre_processors: List[Modifier] = [],
        post_processors: List[Modifier] = [],
    ) -> None:
        self.config = config
        self._vector_collection = vector_collection
        self._embedder = embedder
        self.pre_processors = pre_processors
        self.post_processors = post_processors
        self.population = population
        self._anoymizer = anoymizer
        self._deanoymize = deanoymizer
        self.chunker = chunker

        if anoymizer:
            self.pre_processors.append(anoymizer)
        
        if deanoymizer:
            self.post_processors.append(deanoymizer)


    def pre_process(self, data: T) -> T:
        t_data = data
        for modifier in self.pre_processors:
            modifier.transform(data=t_data)
        return t_data

    def post_process(self, data: T) -> T:
        t_data = data
        for modifier in self.post_processors:
            modifier.transform(data=t_data)
        return t_data
    
    @property
    def anoymizer(self) -> Anonymizer | None:
        return self._anoymizer

    @property
    def vector_collection(self) -> VectorCollection:
        return self._vector_collection

    @property
    def embedder(self) -> Embedder:
        return self._embedder

    def find_context_nodes(self, nodes: List[Node], max_nodes: int = 5) -> List[Node]:
        similar_nodes = []
        if self.vector_collection:
            similar_nodes = [
                similar_node
                for node in nodes
                for similar_node, distance in self.vector_collection.find_similar_nodes(
                    node=node, max_nodes=max_nodes
                )
            ]
        return similar_nodes

class LLM:
    anoymizer: Anonymizer | None
    provider: ProviderConfig
    pre_processors: List[Modifier] = []
    post_processors: List[Modifier] = []

    def __init__(
        self,
        provider: ProviderConfig,
        anonymizer: Anonymizer | None = None,
        deanoymizer: Deanonymizer | None = None,
        cache: PromptCache | None = None,
        pre_processors: List[Modifier] = [],
        post_processors: List[Modifier] = [],
    ) -> None:
        self.openai = openai
        self.provider = provider
        self._anoymizer = anonymizer

        self.cache = cache

        self.pre_processors = pre_processors
        self.post_processors = post_processors


        if anonymizer:
            self.pre_processors.append(anonymizer)

        if deanoymizer:
            self.post_processors.append(deanoymizer)


    def call_llm(
        self,
        msgs: List[ChatMessage],
        model: str | None = None,
        options: OpenAIOptions | None = None,
        debug: bool = False,
    ) -> ChatResponse:
        match (self.provider.type):
            case ProviderType.openai:
                return self._call_openai(
                    model=model or self.provider.default_model,
                    msgs=msgs,
                    opts=options,
                    debug=debug
                )
            case _:
                raise Exception("Provider not supported")

    def pre_process(self, data: T) -> T:
        t_data = data
        for modifier in self.pre_processors:
            t_data = modifier.transform(data=data)
        return t_data

    def post_process(self, data: T) -> T:
        t_data = data
        for modifier in self.post_processors:
            t_data = modifier.transform(data=data)
        return t_data

    def _call_openai(
        self,
        model: str,
        msgs: List[ChatMessage],
        opts: OpenAIOptions | None = None,
        debug: bool = False,
    ) -> ChatResponse:
        self.openai.api_key = self.provider.api_key
        opts = opts or {}
        transformed_msgs = self.pre_process(data=msgs)

        res: Dict[str, Any] = self.openai.ChatCompletion.create(
            model=model,
            messages=[m.model_dump(exclude_none=True) for m in transformed_msgs],
            **opts,
        )  # type: ignore

        open_ai_res = pydantic_openai.ChatCompletionResponse(**res)

        processed_msgs = [
            ChatMessage.from_openai_message(message=res.message) for res in open_ai_res.choices
        ]

        post_processed_msgs = self.post_process(data=processed_msgs)

        orginal_open_ai_res = deepcopy(x=open_ai_res) if debug else None

        open_ai_res.choices = self.post_process(data=open_ai_res.choices)

        return ChatResponse(
            raw_provider_response=orginal_open_ai_res,
            provider_response=open_ai_res,
            messages=post_processed_msgs,
        )


class Orchestrator:
    llm: LLM
    rag: Rag
    application: Application

    def set_llm(self, llm: LLM) -> None:
        self.llm = llm
    
    def set_rag(self, rag: Rag) -> None:
        self.rag = rag
    
    def set_application(self, application: Application) -> None:
        self.application = application

orchestrator = Orchestrator()


def build_orchestrator():
    settings = getSettings()

    sql_db = _build_db(settings.application.database) if settings.application.database else None
    auth = _build_auth(settings.application.authentication, sql_db=sql_db) 
    app = Application(
        auth=auth,
        sql_db=sql_db, 
    )
    rag_anoymizer = _build_anoymizer(settings.rag.anoymizer) if settings.rag.anoymizer else None
    rag_deanoymizer = _build_deanoymizer(settings.rag.anoymizer) if settings.rag.anoymizer else None
    llm = LLM(
        provider=settings.llm.provider,
        cache=_build_cache(
            settings.llm.cache,
            anoymizer=rag_anoymizer,
            deanonimyzer=rag_deanoymizer
        ) if settings.llm.cache else None,
        anonymizer=rag_anoymizer,
        deanoymizer=rag_deanoymizer,
        pre_processors=_build_processors(settings.rag.pre_processors) if settings.rag.pre_processors else [],
        post_processors=_build_processors(settings.rag.post_processors) if settings.rag.post_processors else [],
    )

    rag = Rag(
        config=settings.rag,
        population=_build_population(settings.rag.population) if settings.rag.population else None,
        vector_collection=_build_vector_collection(settings.rag.vector_collection) ,
        embedder=_build_embedder(settings.rag.embedder),
        anoymizer=_build_anoymizer(settings.rag.anoymizer) if settings.rag.anoymizer else None,
        deanoymizer=_build_deanoymizer(settings.rag.anoymizer) if settings.rag.anoymizer else None,
        pre_processors=_build_processors(settings.rag.pre_processors) if settings.rag.pre_processors else [],
        post_processors=_build_processors(settings.rag.post_processors) if settings.rag.post_processors else [],
    )

    orchestrator.set_llm(llm)
    orchestrator.set_rag(rag)
    orchestrator.set_application(app)

def _build_population(config: RagDataPopulationConfig) -> Population:
    match (config.loader.type):
        case LoaderType.demo:
            return Population(loader=DemoLoader(),)
        case LoaderType.api_loader:
            assert config.loader.endpoint is not None, "endpoint must be set for api loader"
            assert config.loader.auth is not None, "auth must be set for api loader"
            assert config.loader.bulk_endpoint is not None, "bulk_endpoint must be set for api loader"
            return Population(
                loader=ApiLoader(
                    endpoint=config.loader.endpoint,
                    bulk_endpoint=config.loader.bulk_endpoint,
                    auth=HTTPBasicAuth(
                        username=config.loader.auth.username,
                        password=config.loader.auth.password
                    )
                )
            )
        case _:
            return Population(loader=DemoLoader())



def _build_cache(config: CacheConfig, anoymizer: Anonymizer | None = None, deanonimyzer: Deanonymizer | None = None) -> PromptCache | None:
    match (config.type):
        case CacheType.small_cache:
            assert config.vector_collection is not None
            assert config.embedder is not None
            return SmallPromptCache(
                vector_collection=_build_vector_collection(config.vector_collection, include_metadata=True),
                embedder=_build_embedder(config.embedder),
                anoymizer=anoymizer,
                deanonimyzer=deanonimyzer,
                expiry_in_seconds=config.expiry_in_seconds,
            )
        case _:
            return None

def _build_processors(config: ProcessorConfig) -> List[Modifier]:
    processors: List[Modifier] = []

    if config.remove_toxicity:
        # TODO: add toxicity processor
        return processors

    return processors

def _build_embedder(config: EmbedderConfig) -> Embedder:
    match (config.type):
        case EmbedderType.sentence:
            return SentenceTransformerEmbedder(
                model_name=config.model,
                max_length=config.max_length,
            )
        case _:
            raise Exception("Embedder not supported")
    

def _build_vector_db(config: VectorDBConfig) -> Any:
    match (config.type):
        case VectorDBType.pgvector:
            return create_engine(url = config.conn_str, pool_size = config.pool_size)
        case _:
            raise Exception("Vector DB not supported")
        

def _build_vector_collection(config: VectorCollectionConfig, include_metadata: bool = True) -> VectorCollection:
    db_engine = _build_vector_db(config)
    match(config.type):
        case VectorDBType.pgvector:
            return PgVectorCollection(db_engine, config.collection_name, config.vector_dimension, include_metadata)
        case _:
            raise Exception("Vector DB not supported")


def _build_anoymizer(config: AnoymizerConfig) -> Anonymizer:
    match (config.type):
        case AnoymizerType.presidio:
            return PresidioAnonymizer(
                key=config.key,
                threshold=config.threshold,
                entity_resolution=config.entity_resolution,
                pii_types=config.pii_types,
            )
        case _:
            raise Exception("Anonymizer not supported")

def _build_deanoymizer(config: AnoymizerConfig) -> Deanonymizer:
    match (config.type):
        case AnoymizerType.presidio:
            return PresidioDeanonymizer(
                key=config.key,
            )
        case _:
            raise Exception("Anonymizer not supported")

def _build_db(config: DatabaseConfig):
    match (config.type):
        case DatabaseType.postgres:
            return SQLDB(
                conn_str=config.conn_str, pool_size=config.pool_size
            )
        case _:
            raise Exception("DB not supported")



def _build_auth(config: AuthConfig | None = None, sql_db: SQLDB | None  = None) -> Auth:
    if config is None:
        return NoAuth()
    
    match (config.type):
        case AuthType.api_key:
            assert sql_db is not None, "SQL DB must be set for api key auth"
            default_credentials = HTTPBasicCredentials(
                username=config.default_admin_username or "admin",
                password=config.default_admin_api_key or "admin",
            )
            return ApiKeyAuth(
                sql_db=sql_db,
                default_admin_credentials=default_credentials,
            )
        case _:
            return NoAuth()

def get_orchestrator():
    return orchestrator
