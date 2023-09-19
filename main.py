from fastapi import FastAPI 
from pkgs.config import setting
from pkgs.orchestrator.orchestrator import build_orchestrator
import yaml


app = FastAPI()

try:
    with open('pontus.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except Exception as e:
    raise Exception("pontus.yaml not found")

setting.setSettings(config)
build_orchestrator()

from api.llm.handler import router as openapi_router
from api.demo.handler import router as demo_router


app.include_router(openapi_router, prefix="/llm")
app.include_router(demo_router, prefix="/demo")
