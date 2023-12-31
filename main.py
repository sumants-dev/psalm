from fastapi import FastAPI
from pkgs.config import setting
from pkgs.orchestrator.orchestrator import build_orchestrator, get_orchestrator
import yaml


app = FastAPI(title="Pontus", version="0.1.0", redoc_url="/")

try:
    with open("pontus.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except Exception as e:
    raise Exception("pontus.yaml not found")

setting.setSettings(config)
build_orchestrator()

from api.llm.handler import router as openapi_router
from api.auth.handler import router as auth_router
from api.document_store.handler import router as rag_router

app.include_router(openapi_router, prefix="/llm")
app.include_router(rag_router, prefix="/rag")
app.include_router(auth_router, prefix="/auth")
