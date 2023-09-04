from fastapi import APIRouter
import ee

router = APIRouter()
@router.get("/v1/chat/completions")
async def root():
    print("hello world")
    ee.test()
    return {"message": "Hello World"}