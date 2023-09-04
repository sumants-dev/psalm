
from fastapi import FastAPI 

from api.openapi.handler import router as openapi_router
app = FastAPI()

app.include_router(openapi_router, prefix="/openapi")
