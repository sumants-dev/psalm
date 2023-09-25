from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi import security
from pkgs.config.setting import getSettings
from pkgs.orchestrator import orchestrator


settings = getSettings()

router = APIRouter()
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic(auto_error=False)


@router.post("/load/bulk", tags=["rag"])
def start_loader(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    ai_orchestrator = orchestrator.get_orchestrator()

    if not ai_orchestrator.application.auth.authenticate(credentials=credentials):
        raise HTTPException(status_code=401, detail="Unauthorized")

    assert ai_orchestrator.rag.population
    assert ai_orchestrator.rag.population.loader

    bulk_load = ai_orchestrator.rag.population.loader.bulk_load()

    nodes = [
        node
        for _, loader in bulk_load.items()
        for node in ai_orchestrator.rag.chunker.document_to_nodes(
            text=loader["text"],
            metadata=loader["metadata"],
        )
    ]

    ai_orchestrator.rag.embedder.embed(nodes)
    transformed_nodes = ai_orchestrator.rag.pre_process(nodes)

    ai_orchestrator.rag.vector_collection.save_nodes(
        nodes=transformed_nodes,
    )


@router.post("/load", tags=["rag"])
def load(
    resource: str,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    ai_orchestrator = orchestrator.get_orchestrator()

    if not ai_orchestrator.application.auth.authenticate(credentials=credentials):
        raise HTTPException(status_code=401, detail="Unauthorized")

    assert ai_orchestrator.rag.population
    assert ai_orchestrator.rag.population.loader

    bulk_load = [ai_orchestrator.rag.population.loader.load(resource=resource)]

    nodes = [
        node
        for loader in bulk_load
        for node in ai_orchestrator.rag.chunker.document_to_nodes(
            text=loader["text"],
            metadata=loader["metadata"],
        )
    ]

    ai_orchestrator.rag.embedder.embed(nodes)
    transformed_nodes = ai_orchestrator.rag.pre_process(nodes)

    ai_orchestrator.rag.vector_collection.save_nodes(
        nodes=transformed_nodes,
    )
