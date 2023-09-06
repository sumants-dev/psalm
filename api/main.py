
from fastapi import FastAPI 

from api.openai.handler import router as openapi_router
app = FastAPI()

app.include_router(openapi_router, prefix="/openapi")
