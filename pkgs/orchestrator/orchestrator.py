from pkgs import Node
from pkgs.chunkers.chunker import Chunker
from pkgs.embedders.embedder import Embedder
from pkgs.embedders.sentence_embedder import SentenceEmbedder
from pkgs.modifiers.anonymity.anonymizer import Anonymizer, Deanonymizer
from pkgs.modifiers.anonymity.presidio_anonymizer import EntityResolution, PII_Type, PresidioAnonymizer, PresidioDeanonymizer
from pkgs.modifiers.modifier import Modifier

from pkgs.models import pydantic_openai
from pkgs.models.pontus.base import ChatMessage, ChatResponse, OpenAIOptions, ProviderType

from copy import deepcopy

from typing import TypeVar, List, Dict, Any


import openai
from pkgs.vector_dbs.pg_vector_store import PgVectorStore

from pkgs.vector_dbs.vector_db import VectorDB
from pkgs.config.setting import AnoymizerType, EmbedderType, Settings, VectorDBType, getSettings


T = TypeVar("T")


class Orchestrator:
    def __init__(self) -> None:
        self.embedder: Embedder | None = None
        self.vector_db: VectorDB | None = None
        self.provider: ProviderType | None = None
        self.pre_processing: List[Modifier]  = []
        self.post_processing: List[Modifier] = []

        self.anoymizer: Anonymizer | None = None
        self.deanoymizer: Deanonymizer | None = None

        self.chunker: Chunker | None = None

        self.openai = openai

    def set_provider_type(self, provider: ProviderType):
        self.provider = provider

    def set_anonymizer(self, anonymizer: Anonymizer):
        self.anoymizer = anonymizer
    
    def anoymize(self, data: T) -> T:
        if self.anoymizer:
            return self.anoymizer.transform(data)
        return data

    def set_deanonymizer(self, deanonymizer: Deanonymizer):
        self.deanoymizer = deanonymizer

    def deanoymize(self, data: str) -> str:
        if self.deanoymizer:
            return self.deanoymizer.transform(data)
        return data

    def add_pre_processor(self, modifier: Modifier):
        self.pre_processing.append(modifier)
    
    def add_post_processor(self, modifier: Modifier):
        self.post_processing.append(modifier)
    
    def set_embedder(self, embedder: Embedder):
        self.embedder = embedder
    
    def set_vector_db(self, vector_db: VectorDB):
        self.vector_db = vector_db

    def pre_process(self, data: T) -> T:
        t_data = data
        for modifier in self.pre_processing:
            t_data = modifier.transform(t_data)
        return t_data 
    
    def post_process(self, data: T) -> T:
        t_data = data
        for modifier in self.post_processing:
            t_data = modifier.transform(t_data)
        return t_data

    def embed(self, nodes: List[Node]):
        if self.embedder:
            self.embedder.embed(nodes)
        
    def find_context_nodes(self, nodes: List[Node], max_nodes: int= 5) -> List[Node]:
        similar_nodes = []
        if self.vector_db:
            similar_nodes = [
                similar_node
                for node in nodes
                for similar_node, distance in 
                self.vector_db.find_similar_nodes(node, 'Node', max_nodes=max_nodes)
            ]
        return similar_nodes

    def _call_openai(
            self, 
            model: str,
            msgs: List[ChatMessage], 
            opts: OpenAIOptions | None = None,
            debug: bool = False
        ) -> ChatResponse:

            settings = getSettings()
            self.openai.api_key = settings.provider.api_key
            opts = opts or {}

            res: Dict[str, Any] = self.openai.ChatCompletion.create(
                model=model,
                messages=[m.model_dump(exclude_none=True) for m in msgs],
                **opts,
            ) # type: ignore

            open_ai_res = pydantic_openai.ChatCompletionResponse(**res)

            processed_msgs = [
                ChatMessage.from_openai_message(res.message)
                for res in open_ai_res.choices
            ]

            post_processed_msgs = self.post_process(processed_msgs)

            orginal_open_ai_res = deepcopy(open_ai_res) if debug else None        


            open_ai_res.choices = self.post_process(open_ai_res.choices)

            return ChatResponse(
                raw_provider_response=orginal_open_ai_res,
                deanoymized_provider_response=open_ai_res,
                messages=post_processed_msgs,
            )

    def call_llm(self, model: str ,msgs: List[ChatMessage], options: OpenAIOptions | None = None, debug: bool = False) -> ChatResponse:
        match (self.provider):
            case ProviderType.openai:
                return self._call_openai(model=model, msgs=msgs, opts=options, debug=debug)
            case _:
                raise Exception("Provider not supported")    

orchestrator = Orchestrator()

def build_orchestrator():
    settings = getSettings()

    orchestrator.set_provider_type(settings.provider.type)
    _build_anoymizer(settings)
    _build_sentence_embedder(settings)
    _build_vector_db(settings)

def _build_vector_db(settings: Settings):
    if settings.vector_db.type == VectorDBType.pgvector:
        orchestrator.set_vector_db(PgVectorStore(settings.vector_db.conn_str))

def _build_sentence_embedder(settings: Settings):
    if settings.embedder.type == EmbedderType.sentence:
        orchestrator.set_embedder(SentenceEmbedder(settings.embedder.model))

def _build_anoymizer(settings: Settings):
    if settings.anoymizer.type == AnoymizerType.presidio:
        anoymizer = PresidioAnonymizer(
            settings.anoymizer.key,
            settings.anoymizer.threshold,
            settings.anoymizer.entity_resolution,
            settings.anoymizer.pii_types
        ) 
        orchestrator.set_anonymizer(anoymizer)
        orchestrator.add_pre_processor(anoymizer)

        deanoymizer = PresidioDeanonymizer(settings.anoymizer.key) 
        orchestrator.set_deanonymizer(deanoymizer)
        orchestrator.add_post_processor(deanoymizer)
    else:
        raise Exception("Anonymizer not supported")

def get_orchestrator():
    return orchestrator